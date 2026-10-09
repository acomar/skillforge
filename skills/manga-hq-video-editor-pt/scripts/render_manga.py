#!/usr/bin/env python3
"""Render a reviewed comic timeline locally with FFmpeg; Python stdlib only.

Coordinates are normalized XYXY. All source paths are relative to the plan
unless absolute. One explicit audio stream is muxed globally after video-only
segments, so encoding audio does not introduce priming at every panel.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any

VERSION = "1.2.0"
PROFILE = "comic-identity-longform-v1"
SUPPORTED_PROFILES = {PROFILE, "manga-blue-longform-v1"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
MOTION_EASING = {"smoothstep", "linear"}
MOTION_MAX_INTERMEDIATE_PIXELS = 3840 * 2160
MOTION_MAX_INTERMEDIATE_AXIS = 3840


class RenderError(Exception):
    pass


def number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise RenderError(f"{label} must be a finite number")
    return float(value)


def integer(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise RenderError(f"{label} must be an integer")
    return value


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def expected_hash(actual: str, expected: Any, label: str) -> None:
    if expected is None:
        return
    if not isinstance(expected, str) or re.fullmatch(r"[0-9a-fA-F]{64}", expected) is None:
        raise RenderError(f"{label} expected SHA256 must contain 64 hexadecimal characters")
    if actual != expected.lower():
        raise RenderError(f"{label} does not match the reviewed plan; regenerate and review the plan before rendering")


def json_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as target:
        json.dump(value, target, ensure_ascii=False, indent=2, allow_nan=False)
        target.write("\n")
    os.replace(temporary, path)


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (ValueError, OSError) as error:
        raise RenderError(f"Cannot read JSON {path}: {error}") from error


def run(command: list[str], timeout: float, log: Path | None = None) -> str:
    try:
        result = subprocess.run(command, capture_output=True, encoding="utf-8", errors="replace",
                                check=False, timeout=timeout, shell=False)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise RenderError(f"Cannot finish {Path(command[0]).name}: {error}") from error
    if log is not None:
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(result.stderr, encoding="utf-8")
    if result.returncode:
        raise RenderError(f"{Path(command[0]).name} exited {result.returncode}: "
                          + result.stderr[-1600:].strip() + (f"; log {log}" if log else ""))
    return result.stdout


def tool_paths() -> dict[str, str]:
    result = {name: shutil.which(name) for name in ("ffmpeg", "ffprobe")}
    if any(value is None for value in result.values()):
        raise RenderError("FFmpeg and FFprobe are required on PATH")
    return {key: str(value) for key, value in result.items()}


def probe(path: Path, tools: dict[str, str], timeout: float) -> dict[str, Any]:
    return json.loads(run([tools["ffprobe"], "-v", "error", "-show_streams", "-show_format",
                           "-of", "json", str(path)], timeout))


def source_path(value: Any, base: Path, label: str) -> Path:
    if not isinstance(value, str) or not value or "\x00" in value:
        raise RenderError(f"{label} must be a local file path")
    path = Path(value).expanduser()
    path = (base / path).resolve() if not path.is_absolute() else path.resolve()
    if not path.is_file():
        raise RenderError(f"{label} does not exist: {path}")
    return path


def frame_rate(value: Any) -> Fraction:
    if isinstance(value, bool):
        raise RenderError("canvas.fps must be a number or rational string")
    try:
        rate = Fraction(str(value))
    except (ValueError, ZeroDivisionError) as error:
        raise RenderError("canvas.fps must be a number or rational string") from error
    if rate < 1 or rate > 120:
        raise RenderError("canvas.fps must be between 1 and 120")
    return rate


def validate_background(identity: Any, base: Path, tools: dict[str, str],
                        timeout: float) -> dict[str, Any]:
    """Resolve a quiet ambient fallback or a supplied, reviewed art-direction asset."""
    if identity is None:
        identity = {}
    if not isinstance(identity, dict):
        raise RenderError("visual_identity must be an object")
    supplied = identity.get("background", {})
    if not isinstance(supplied, dict):
        raise RenderError("visual_identity.background must be an object")
    mode = supplied.get("mode", "ambient")
    if mode not in {"image", "ambient"}:
        raise RenderError("visual_identity.background.mode must be image or ambient")
    darkness = number(supplied.get("darkness", .18 if mode == "image" else 0),
                      "visual_identity.background.darkness")
    if not 0 <= darkness <= .65:
        raise RenderError("visual_identity.background.darkness must be within 0..0.65")
    background = {"mode": mode, "darkness": darkness}
    if mode == "ambient":
        palette = supplied.get("palette", ["#161A22", "#242A34"])
        if (not isinstance(palette, list) or len(palette) != 2
                or any(not isinstance(color, str) or re.fullmatch(r"#[0-9a-fA-F]{6}", color) is None
                       for color in palette)):
            raise RenderError("visual_identity.background.palette needs two #RRGGBB colors")
        background["palette"] = [color.upper() for color in palette]
        return background
    image = source_path(supplied.get("file"), base, "visual_identity.background.file")
    if image.suffix.lower() not in IMAGE_EXTENSIONS:
        raise RenderError("visual_identity.background.file must be a supported still image")
    metadata = probe(image, tools, timeout)
    streams = [stream for stream in metadata.get("streams", []) if stream.get("codec_type") == "video"]
    if len(streams) != 1:
        raise RenderError("visual_identity.background.file must decode to one video stream")
    width, height = int(streams[0].get("width", 0)), int(streams[0].get("height", 0))
    if not (2 <= width <= 30000 and 2 <= height <= 30000):
        raise RenderError("Invalid dimensions in visual_identity.background.file")
    digest = file_hash(image)
    expected_hash(digest, supplied.get("sha256"), "visual_identity.background.file")
    start = number(supplied.get("zoom_from", 1), "visual_identity.background.zoom_from")
    end = number(supplied.get("zoom_to", 1.035), "visual_identity.background.zoom_to")
    if not (1 <= start <= 1.12 and 1 <= end <= 1.12):
        raise RenderError("Background zoom scales must be between 1 and 1.12")
    background.update(file=str(image), sha256=digest, width=width, height=height,
                      zoom_from=start, zoom_to=end)
    return background


def validate_plan(plan_path: Path, tools: dict[str, str], timeout: float = 900,
                  preview: tuple[int, int] | None = None) -> dict[str, Any]:
    plan_path = plan_path.resolve()
    data = read_json(plan_path)
    if not isinstance(data, dict) or isinstance(data.get("schema_version"), bool) or data.get("schema_version") != 1:
        raise RenderError("Plan must use schema_version 1")
    if preview is None and (data.get("readiness") != "ready" or data.get("renderable") is not True):
        raise RenderError("Draft/unconfirmed plan cannot produce a master; require readiness=ready and renderable=true or use --preview")
    canvas = data.get("canvas", {})
    if not isinstance(canvas, dict):
        raise RenderError("canvas must be an object")
    width = integer(canvas.get("width", 1920), "canvas.width")
    height = integer(canvas.get("height", 1080), "canvas.height")
    if preview is not None:
        width, height = preview
    if width < 160 or height < 90 or width > 7680 or height > 7680 or width % 2 or height % 2:
        raise RenderError("Canvas dimensions must be even, at least 160×90 and at most 7680")
    rate = frame_rate(canvas.get("fps", "30000/1001"))
    frame_seconds = 1 / float(rate)
    profile = data.get("profile", PROFILE)
    if profile not in SUPPORTED_PROFILES:
        raise RenderError(f"Unsupported profile: {profile}; expected {PROFILE}")
    visual_identity = data.get("visual_identity", {})
    background = validate_background(visual_identity, plan_path.parent, tools, timeout)
    audio = data.get("audio")
    if not isinstance(audio, dict) or "stream_index" not in audio:
        raise RenderError("audio.file and an explicit absolute audio.stream_index are required")
    audio_file = source_path(audio.get("file"), plan_path.parent, "audio.file")
    audio_hash = file_hash(audio_file)
    expected_hash(audio_hash, audio.get("sha256"), "audio.file")
    audio_index = integer(audio["stream_index"], "audio.stream_index")
    audio_metadata = probe(audio_file, tools, timeout)
    matching = [stream for stream in audio_metadata.get("streams", [])
                if stream.get("index") == audio_index and stream.get("codec_type") == "audio"]
    if len(matching) != 1:
        raise RenderError(f"Stream {audio_index} is not an audio stream in {audio_file}")
    stream = matching[0]
    duration_value = stream.get("duration", audio_metadata.get("format", {}).get("duration"))
    try:
        audio_duration = float(duration_value)
    except (ValueError, TypeError) as error:
        raise RenderError("Selected audio stream needs a finite duration") from error
    if not math.isfinite(audio_duration) or audio_duration <= 0:
        raise RenderError("Selected audio stream needs a positive finite duration")
    target_frames = math.ceil(audio_duration * float(rate) - 1e-8)
    if target_frames < 1:
        raise RenderError("Audio is shorter than one video frame")
    entries = data.get("beats")
    if not isinstance(entries, list) or not entries or len(entries) > 10000:
        raise RenderError("beats must contain between 1 and 10000 entries")
    beats = []
    image_cache: dict[Path, dict[str, Any]] = {}
    ids = set()
    previous_raw_end = 0.0
    previous_frame = 0
    adjustments = []
    for index, item in enumerate(entries):
        if not isinstance(item, dict):
            raise RenderError(f"Beat {index} must be an object")
        identifier = item.get("id")
        if not isinstance(identifier, str) or not identifier.strip() or identifier in ids:
            raise RenderError("Each beat needs a unique nonempty id")
        ids.add(identifier)
        start = number(item.get("start"), f"{identifier}.start")
        end = number(item.get("end"), f"{identifier}.end")
        if start < 0 or end <= start or end - start > 300:
            raise RenderError(f"{identifier} duration must be positive and at most 300 seconds")
        if abs(start - previous_raw_end) > frame_seconds + 1e-7:
            raise RenderError(f"Timeline gap/overlap before {identifier} exceeds one frame")
        if index == 0 and abs(start) > frame_seconds / 2 + 1e-7:
            raise RenderError("Timeline must start at 0")
        end_frame = round(end * float(rate))
        if index == len(entries) - 1:
            if abs(end - audio_duration) > frame_seconds + 1e-7:
                raise RenderError("Timeline end differs from selected audio duration by more than one frame")
            end_frame = target_frames
        if end_frame <= previous_frame:
            raise RenderError(f"{identifier} is shorter than one frame after timing alignment")
        if abs(start - previous_frame * frame_seconds) > frame_seconds + 1e-7:
            raise RenderError(f"{identifier} cannot be aligned without moving its start by more than one frame")
        image_file = source_path(item.get("image"), plan_path.parent, f"{identifier}.image")
        if image_file.suffix.lower() not in IMAGE_EXTENSIONS:
            raise RenderError(f"{identifier} must use a supported still image: {sorted(IMAGE_EXTENSIONS)}")
        if image_file not in image_cache:
            metadata = probe(image_file, tools, timeout)
            videos = [s for s in metadata.get("streams", []) if s.get("codec_type") == "video"]
            if len(videos) != 1:
                raise RenderError(f"{identifier} image must decode to one video stream")
            source_width = int(videos[0].get("width", 0))
            source_height = int(videos[0].get("height", 0))
            if not (2 <= source_width <= 30000 and 2 <= source_height <= 30000):
                raise RenderError(f"Invalid image dimensions for {identifier}")
            rotation = next((s.get("rotation", 0) for s in videos[0].get("side_data_list", [])
                             if "rotation" in s), 0)
            if abs(int(rotation)) % 180 == 90:
                source_width, source_height = source_height, source_width
            image_cache[image_file] = {"file": str(image_file), "width": source_width,
                                       "height": source_height, "sha256": file_hash(image_file)}
        facts = image_cache[image_file]
        expected_hash(facts["sha256"], item.get("image_sha256"), f"{identifier}.image")
        box = item.get("bbox", [0, 0, 1, 1])
        if not isinstance(box, list) or len(box) != 4:
            raise RenderError(f"{identifier}.bbox must be normalized [x1,y1,x2,y2]")
        x1, y1, x2, y2 = [number(v, f"{identifier}.bbox") for v in box]
        if not (0 <= x1 < x2 <= 1 and 0 <= y1 < y2 <= 1):
            raise RenderError(f"{identifier}.bbox must be ordered normalized XYXY coordinates")
        crop_x = math.floor(x1 * facts["width"])
        crop_y = math.floor(y1 * facts["height"])
        crop_width = min(facts["width"], math.ceil(x2 * facts["width"])) - crop_x
        crop_height = min(facts["height"], math.ceil(y2 * facts["height"])) - crop_y
        if min(crop_width, crop_height) < 2:
            raise RenderError(f"{identifier}.bbox produces an empty or too-small crop")
        beat_seconds = (end_frame - previous_frame) * frame_seconds
        # Match the builder for previously unplanned shots. Explicit and
        # partially specified legacy motion objects keep their old defaults.
        default_scale = 1 + min(.5, max(.25, beat_seconds * .06))
        motion = item.get("motion", {"from_scale": 1 if index % 2 == 0 else default_scale,
                                   "to_scale": default_scale if index % 2 == 0 else 1})
        if not isinstance(motion, dict):
            raise RenderError(f"{identifier}.motion must be an object")
        from_scale = number(motion.get("from_scale", 1), f"{identifier}.motion.from_scale")
        to_scale = number(motion.get("to_scale", 1.8), f"{identifier}.motion.to_scale")
        if not (1 <= from_scale <= 2.5 and 1 <= to_scale <= 2.5):
            raise RenderError(f"{identifier} motion scales must be between 1 and 2.5")
        easing = motion.get("easing", "smoothstep")
        if not isinstance(easing, str) or easing not in MOTION_EASING:
            raise RenderError(f"{identifier}.motion.easing must be smoothstep or linear")
        focal = item.get("focal_point", [.5, .5])
        if not isinstance(focal, list) or len(focal) != 2:
            raise RenderError(f"{identifier}.focal_point must be normalized [x,y]")
        focal = [number(v, f"{identifier}.focal_point") for v in focal]
        if any(v < 0 or v > 1 for v in focal):
            raise RenderError(f"{identifier}.focal_point must be within 0..1")
        transition = number(item.get("transition_seconds", min(.25, beat_seconds / 4)),
                            f"{identifier}.transition_seconds")
        if not (0 <= transition <= 1 and transition * 2 <= beat_seconds + 1e-7):
            raise RenderError(f"{identifier} fade must be at most 1 second and half the beat duration")
        mode = item.get("color_mode", "original")
        if mode not in {"manga_cyan", "original"}:
            raise RenderError(f"{identifier}.color_mode must be manga_cyan or original")
        if preview is None and item.get("legibility_reviewed") is not True:
            raise RenderError(f"{identifier} requires legibility_reviewed=true before master render")
        snapped_start = previous_frame * frame_seconds
        snapped_end = end_frame * frame_seconds
        if abs(snapped_start-start) > 1e-7 or abs(snapped_end-end) > 1e-7:
            adjustments.append({"id": identifier, "input": [start, end],
                                "rendered": [snapped_start, snapped_end]})
        beats.append({"id": identifier, "start": snapped_start, "end": snapped_end,
                      "frames": end_frame-previous_frame, "image": str(image_file),
                      "image_sha256": facts["sha256"], "crop": [crop_x, crop_y, crop_width, crop_height],
                      "motion": {"from_scale": from_scale, "to_scale": to_scale, "easing": easing},
                      "focal_point": focal, "transition_seconds": transition, "color_mode": mode,
                      "legibility_reviewed": item.get("legibility_reviewed") is True})
        previous_raw_end, previous_frame = end, end_frame
    if previous_frame != target_frames:
        raise RenderError("Frame-aligned timeline does not cover audio")
    return {"schema_version": 1, "renderer_version": VERSION, "profile": profile,
            "plan": str(plan_path), "plan_sha256": file_hash(plan_path),
            "canvas": {"width": width, "height": height, "fps": f"{rate.numerator}/{rate.denominator}"},
            "audio": {"file": str(audio_file), "stream_index": audio_index,
                      "duration": audio_duration, "duration_source": "stream" if "duration" in stream else "container",
                      "start_time": stream.get("start_time"), "sha256": audio_hash},
            "frames": target_frames, "duration": target_frames * frame_seconds,
            "beats": beats, "background": background,
            "motion_rendering": {"strategy": "supersampled-gbrap-zoompan",
                                 "input_supersampling": motion_supersampling(width, height),
                                 "max_intermediate_pixels": MOTION_MAX_INTERMEDIATE_PIXELS,
                                 "max_intermediate_axis": MOTION_MAX_INTERMEDIATE_AXIS,
                                 "default_easing": "smoothstep"},
            "visual_identity": visual_identity,
            "timing_adjustments": adjustments, "preview": preview is not None,
            "limitations": ["Image legibility and focal point are human/editorial review decisions.",
                            "Background assets and palette require editorial review; the quiet ambient fallback is not a complete identity design.",
                            "Panel easing and continuous background drift are original motion; source keyframes are not recovered.",
                            "Supersampling reduces integer crop stepping, not source-image resolution limits; UHD and larger outputs use factor 1 under the intermediate-canvas memory cap.",
                            "Fades occur inside each beat; adjacent beats do not overlap.",
                            "Only the selected supplied audio stream is used. No music or speech is generated."]}


def background_filter(width: int, height: int, fps: str, duration: float, offset: float,
                      background: dict[str, Any] | None = None) -> str:
    """Low-contrast textured ambient fallback; no symbols, particles or geometry."""
    background = background or {"palette": ["#161A22", "#242A34"], "darkness": 0}
    bg_width = 320
    bg_height = max(90, round(320 * height / width / 2) * 2)
    clock = f"(T+{offset:.9f})"
    colors = [[int(color[i:i+2], 16) for i in (1, 3, 5)] for color in background["palette"]]
    gradient = f"(0.25+0.55*X/W+0.15*Y/H+0.025*sin({clock}*0.08))"
    grain = f"(0.55*sin(X*19+Y*37)*cos(X*13-Y*17+{clock}*0.04))"
    vignette = "(1-0.18*((X/W-0.5)*(X/W-0.5)+(Y/H-0.5)*(Y/H-0.5)))"
    factor = 1-background["darkness"]
    channels = [f"clip(({start}+({end-start})*{gradient}+{grain})*{vignette}*{factor:.9f},0,255)"
                for start, end in zip(*colors)]
    return (f"nullsrc=s={bg_width}x{bg_height}:r={fps}:d={duration:.9f},format=gbrp,"
            f"geq=r='{channels[0]}':g='{channels[1]}':b='{channels[2]}'")


def motion_supersampling(width: int, height: int) -> int:
    """Reduce zoompan's integer crop quantization with a bounded input canvas.

    The usual 960x540 preview gets 4x and 1920x1080 gets 2x. UHD uses 1x;
    already-large canvases are not enlarged further. This is an interpolation
    working grid, not a claim that the source contains additional detail.
    """
    for factor in range(4, 1, -1):
        if (width * height * factor * factor <= MOTION_MAX_INTERMEDIATE_PIXELS
                and max(width, height) * factor <= MOTION_MAX_INTERMEDIATE_AXIS):
            return factor
    return 1


def motion_progress(frames: int, easing: str) -> str:
    """An absolute frame expression reaches both endpoints without accumulation."""
    progress = f"(on/{max(1, frames-1)})"
    if easing == "smoothstep":
        return f"({progress}*{progress}*(3-2*{progress}))"
    return progress


def image_background_filter(background: dict[str, Any], canvas: dict[str, Any],
                            beat: dict[str, Any], total_frames: int) -> str:
    """Cover the canvas with a dimmed image and keep its zoom continuous across cuts."""
    width, height = canvas["width"], canvas["height"]
    factor = motion_supersampling(width, height)
    intermediate_width, intermediate_height = width * factor, height * factor
    start, end = background["zoom_from"], background["zoom_to"]
    frame_offset = round(beat["start"] * float(Fraction(canvas["fps"])))
    progress = f"(on+{frame_offset})/{max(1,total_frames-1)}"
    zoom = f"{start:.9f}+({end-start:.9f})*{progress}"
    return (f"format=gbrap,scale={intermediate_width}:{intermediate_height}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={intermediate_width}:{intermediate_height}:exact=1,setsar=1,format=gbrap,"
            f"zoompan=z='{zoom}':x='iw/2-iw/(2*zoom)':y='ih/2-ih/(2*zoom)':"
            f"d={beat['frames']}:s={width}x{height}:fps={canvas['fps']},"
            f"eq=brightness=-{background['darkness']:.9f}:saturation=0.85,"
            "vignette=PI/5:mode=forward:dither=0,format=rgba,setsar=1,setpts=PTS-STARTPTS")


def panel_filter(beat: dict[str, Any], canvas: dict[str, Any]) -> str:
    width, height = canvas["width"], canvas["height"]
    factor = motion_supersampling(width, height)
    intermediate_width, intermediate_height = width * factor, height * factor
    crop_x, crop_y, crop_width, crop_height = beat["crop"]
    fitting = min(width * .90 / crop_width, height * .90 / crop_height)
    fitted_width = max(2, min(width, round(crop_width * fitting / 2) * 2))
    fitted_height = max(2, min(height, round(crop_height * fitting / 2) * 2))
    frames = beat["frames"]
    from_scale, to_scale = beat["motion"]["from_scale"], beat["motion"]["to_scale"]
    zoom = (f"{from_scale:.9f}+({to_scale-from_scale:.9f})*"
            + motion_progress(frames, beat["motion"].get("easing", "smoothstep")))
    focal_x = ((width-fitted_width)/2 + fitted_width*beat["focal_point"][0]) * factor
    focal_y = ((height-fitted_height)/2 + fitted_height*beat["focal_point"][1]) * factor
    x = f"max(0,min(iw-iw/zoom,{focal_x:.9f}-iw/(2*zoom)))"
    y = f"max(0,min(ih-ih/zoom,{focal_y:.9f}-ih/(2*zoom)))"
    filters = ["format=rgba", f"crop={crop_width}:{crop_height}:{crop_x}:{crop_y}:exact=1"]
    if beat["color_mode"] == "manga_cyan":
        gray = ("colorchannelmixer=rr=.2126:rg=.7152:rb=.0722:gr=.2126:gg=.7152:gb=.0722:"
                "br=.2126:bg=.7152:bb=.0722")
        filters.extend([gray, "lutrgb=r=val*80/255:g=val*174/255:b=val"])
    filters.extend([f"scale={fitted_width * factor}:{fitted_height * factor}:flags=lanczos",
                    f"pad={intermediate_width}:{intermediate_height}:(ow-iw)/2:(oh-ih)/2:color=0x00000000",
                    "format=gbrap",
                    f"zoompan=z='{zoom}':x='{x}':y='{y}':d={frames}:s={width}x{height}:fps={canvas['fps']}",
                    "format=rgba", "setsar=1", "setpts=PTS-STARTPTS"])
    fade = beat["transition_seconds"]
    if fade > 0:
        filters.extend([f"fade=t=in:st=0:d={fade:.9f}:alpha=1",
                        f"fade=t=out:st={max(0,beat['end']-beat['start']-fade):.9f}:d={fade:.9f}:alpha=1"])
    return ",".join(filters)


def validate_video(path: Path, tools: dict[str, str], frames: int, width: int, height: int,
                   fps: str, timeout: float, log: Path, audio_required: bool = False) -> dict[str, Any]:
    data = probe(path, tools, timeout)
    videos = [s for s in data.get("streams", []) if s.get("codec_type") == "video"]
    audios = [s for s in data.get("streams", []) if s.get("codec_type") == "audio"]
    if len(videos) != 1 or len(audios) != int(audio_required):
        raise RenderError(f"Unexpected stream count in {path}")
    video = videos[0]
    if (video.get("width"), video.get("height")) != (width, height):
        raise RenderError(f"Unexpected rendered dimensions in {path}")
    if int(video.get("nb_frames", -1)) != frames:
        raise RenderError(f"Frame count mismatch in {path}: expected {frames}, got {video.get('nb_frames')}")
    for field in ("avg_frame_rate", "r_frame_rate"):
        try:
            actual_fps = Fraction(video.get(field, "0/1"))
        except (ValueError, ZeroDivisionError) as error:
            raise RenderError(f"Invalid rendered frame rate in {path}") from error
        if actual_fps != Fraction(fps):
            raise RenderError(f"Rendered {field} differs from expected {fps} in {path}")
    expected_duration = frames / float(Fraction(fps))
    actual_duration = float(video.get("duration", data["format"]["duration"]))
    if abs(actual_duration-expected_duration) > 1/float(Fraction(fps)) + 1e-5:
        raise RenderError(f"Rendered video duration mismatch in {path}")
    audio_duration = None
    if audio_required:
        audio_duration = float(audios[0].get("duration", data["format"]["duration"]))
        codec_padding = 1024 / int(audios[0].get("sample_rate", 48000)) if audios[0].get("codec_name") == "aac" else 0
        if abs(audio_duration-expected_duration) > 1/float(Fraction(fps)) + codec_padding + 1e-5:
            raise RenderError(f"Delivered audio duration differs by more than one frame plus one AAC packet in {path}")
    run([tools["ffmpeg"], "-hide_banner", "-nostdin", "-v", "error", "-xerror", "-threads", "2",
         "-i", str(path), "-map", "0:v:0"] + (["-map", "0:a:0"] if audio_required else [])
        + ["-f", "null", "-"], timeout, log)
    return {"status": "passed", "video_frames": frames, "video_duration": actual_duration,
            "container_duration": float(data["format"]["duration"]),
            "width": width, "height": height, "audio_streams": len(audios), "decoded": True,
            "audio_duration": audio_duration, "frame_rate": fps, "sha256": file_hash(path)}


@contextmanager
def workspace_lock(directory: Path):
    lock = directory / ".render.lock"
    try:
        descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as error:
        raise RenderError(f"Render work directory is locked: {lock}") from error
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as target:
            target.write(f"pid={os.getpid()}\n")
        yield
    finally:
        lock.unlink(missing_ok=True)


def loudnorm_json(log: Path) -> dict[str, Any]:
    text = log.read_text(encoding="utf-8")
    match = re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", text, re.DOTALL)
    if not match:
        raise RenderError(f"No loudness report found: {log}")
    return json.loads(match[-1])


def audio_filter(plan: dict[str, Any], tools: dict[str, str], timeout: float, directory: Path,
                 normalize: bool) -> tuple[str, dict[str, Any]]:
    base = f"asetpts=PTS-STARTPTS,atrim=duration={plan['duration']:.9f}"
    if not normalize:
        return base + f",apad=whole_dur={plan['duration']:.9f}", {"enabled": False}
    log = directory / "audio-loudness-analysis.log"
    run([tools["ffmpeg"], "-hide_banner", "-nostdin", "-threads", "2", "-i", plan["audio"]["file"],
         "-map", f"0:{plan['audio']['stream_index']}", "-vn", "-af",
         base + ",loudnorm=I=-17:LRA=11:TP=-1:print_format=json", "-f", "null", "-"], timeout, log)
    stats = loudnorm_json(log)
    if not all(math.isfinite(float(stats[key])) for key in ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset")):
        return base + f",apad=whole_dur={plan['duration']:.9f}", {"enabled": False, "reason": "silent_or_ungated_input", "measurement": stats}
    normalization = ("loudnorm=I=-17:LRA=11:TP=-1:"
                     f"measured_I={stats['input_i']}:measured_LRA={stats['input_lra']}:"
                     f"measured_TP={stats['input_tp']}:measured_thresh={stats['input_thresh']}:"
                     f"offset={stats['target_offset']}:linear=true:print_format=json")
    return base + "," + normalization + f",apad=whole_dur={plan['duration']:.9f}", {
        "enabled": True, "target_integrated_lufs": -17, "target_true_peak_dbtp": -1,
        "target_lra": 11, "measurement": stats,
        "limitation": "Targets apply before AAC encoding; delivery true peak must be audited separately."}


def audit_loudness(path: Path, tools: dict[str, str], timeout: float, log: Path) -> dict[str, Any]:
    run([tools["ffmpeg"], "-hide_banner", "-nostdin", "-threads", "2", "-i", str(path),
         "-map", "0:a:0", "-vn", "-af", "loudnorm=I=-17:LRA=11:TP=-1:print_format=json",
         "-f", "null", "-"], timeout, log)
    stats = loudnorm_json(log)
    return {"method": "FFmpeg loudnorm measurement of delivered AAC stream",
            "integrated_lufs": stats["input_i"], "true_peak_dbtp": stats["input_tp"],
            "lra_lu": stats["input_lra"], "target_integrated_lufs": -17, "target_true_peak_dbtp": -1,
            "finite_measurement": all(math.isfinite(float(stats[key])) for key in ("input_i", "input_tp"))}


def render(plan_path: Path, output: Path, workdir: Path, preview: tuple[int, int] | None,
           threads: int, timeout: float, resume: bool, normalize: bool = True) -> dict[str, Any]:
    tools = tool_paths()
    plan = validate_plan(plan_path, tools, timeout, preview)
    output, workdir = output.resolve(), workdir.resolve()
    source_paths = {Path(plan["audio"]["file"]), Path(plan["plan"])} | {Path(b["image"]) for b in plan["beats"]}
    if plan["background"]["mode"] == "image":
        source_paths.add(Path(plan["background"]["file"]))
    if output in source_paths or output.exists():
        raise RenderError("Output must be a new path and must not overwrite a source")
    if output.suffix.lower() != ".mp4":
        raise RenderError("Output must end in .mp4")
    if not 1 <= threads <= 8:
        raise RenderError("threads must be between 1 and 8")
    version = run([tools["ffmpeg"], "-version"], timeout).splitlines()[0]
    identity = {"plan": plan, "ffmpeg_version": version, "threads": threads, "normalize_audio": normalize,
                "encoder": {"name": "libx264", "preset": "veryfast", "crf": 18}}
    key = hashlib.sha256(json.dumps(identity, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    workdir.mkdir(parents=True, exist_ok=True)
    cache = workdir / "cache" / key
    cache.mkdir(parents=True, exist_ok=True)
    checkpoint = cache / "checkpoint.json"
    state = {"schema_version": 1, "status": "running", "cache_key": key, "identity": identity,
             "segments": [], "reused_segments": 0, "rendered_segments": 0, "commands": []}
    with workspace_lock(workdir):
        json_write(checkpoint, state)
        try:
            canvas = plan["canvas"]
            for index, beat in enumerate(plan["beats"]):
                segment = cache / f"segment-{index+1:05d}.mp4"
                segment_identity = {"beat": beat, "canvas": canvas, "background": plan["background"],
                                    "background_timeline_frames": plan["frames"], "renderer_version": VERSION,
                                    "ffmpeg_version": version, "threads": threads,
                                    "encoder": identity["encoder"]}
                segment_key = hashlib.sha256(json.dumps(segment_identity, sort_keys=True).encode()).hexdigest()
                shared = workdir / "segments" / segment_key
                shared_file = shared / "segment.mp4"
                shared_report = shared / "validation.json"
                existing = read_json(shared_report) if resume and shared_report.is_file() else None
                reused = False
                if existing and shared_file.is_file() and file_hash(shared_file) == existing.get("sha256"):
                    validation = validate_video(shared_file, tools, beat["frames"], canvas["width"], canvas["height"],
                                                canvas["fps"], timeout, cache/f"decode-reuse-{index+1:05d}.log")
                    shutil.copyfile(shared_file, segment)
                    reused = True
                if not reused:
                    duration = beat["end"]-beat["start"]
                    background = plan["background"]
                    if background["mode"] == "image":
                        inputs = ["-i", background["file"], "-i", beat["image"]]
                        bg_filter = image_background_filter(background, canvas, beat, plan["frames"])
                    else:
                        bg = background_filter(canvas["width"], canvas["height"], canvas["fps"], duration+.1,
                                               beat["start"], background)
                        inputs = ["-f", "lavfi", "-i", bg, "-i", beat["image"]]
                        bg_filter = f"scale={canvas['width']}:{canvas['height']}:flags=bilinear,setsar=1"
                    graph = (f"[0:v]{bg_filter}[bg];"
                             f"[1:v]{panel_filter(beat,canvas)}[panel];"
                             "[bg][panel]overlay=x=0:y=0:format=auto:shortest=1,format=yuv420p[v]")
                    command = [tools["ffmpeg"], "-hide_banner", "-nostdin", "-y", "-threads", str(threads),
                               "-filter_complex_threads", "1"] + inputs + [
                               "-filter_complex", graph, "-map", "[v]", "-an", "-frames:v", str(beat["frames"]),
                               "-r", canvas["fps"], "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                               "-pix_fmt", "yuv420p", "-threads", str(threads), str(segment)]
                    state["commands"].append(list(command))
                    run(command, timeout, cache/f"render-{index+1:05d}.log")
                    validation = validate_video(segment, tools, beat["frames"], canvas["width"], canvas["height"],
                                                canvas["fps"], timeout, cache/f"decode-{index+1:05d}.log")
                    shared.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(segment, shared_file)
                    json_write(shared_report, validation)
                state["segments"].append({"index": index, "id": beat["id"], "path": str(segment),
                                          "segment_cache_key": segment_key, "reused": reused, "validation": validation})
                state["reused_segments" if reused else "rendered_segments"] += 1
                json_write(checkpoint, state)
                print(json.dumps({"segment": index+1, "total": len(plan["beats"]), "reused": reused}), flush=True)
            concat = cache / "segments.ffconcat"
            concat.write_text("ffconcat version 1.0\n"
                              + "".join(f"file 'segment-{i+1:05d}.mp4'\n" for i in range(len(plan["beats"]))), encoding="utf-8")
            af, loudness = audio_filter(plan, tools, timeout, cache, normalize)
            candidate = cache / "candidate.mp4"
            command = [tools["ffmpeg"], "-hide_banner", "-nostdin", "-y", "-threads", str(threads),
                       "-f", "concat", "-safe", "1", "-i", str(concat), "-i", plan["audio"]["file"],
                       "-map", "0:v:0", "-map", f"1:{plan['audio']['stream_index']}", "-c:v", "copy",
                       "-af", af, "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                       "-t", f"{plan['duration']:.9f}", "-movflags", "+faststart", str(candidate)]
            state["commands"].append(list(command))
            run(command, timeout, cache/"mux.log")
            validation = validate_video(candidate, tools, plan["frames"], canvas["width"], canvas["height"],
                                        canvas["fps"], timeout, cache/"decode-master.log", audio_required=True)
            delivered_loudness = audit_loudness(candidate, tools, timeout, cache/"delivery-loudness.log")
            if normalize and delivered_loudness["finite_measurement"] and float(delivered_loudness["true_peak_dbtp"]) > -1:
                # AAC can add an intersample peak. One deterministic global
                # attenuation keeps the delivered peak below the target; no
                # per-beat audio is encoded and speech timing stays intact.
                correction = -1.15-float(delivered_loudness["true_peak_dbtp"])
                af += f",volume={correction:.3f}dB"
                command[command.index("-af")+1] = af
                state["commands"].append(list(command))
                run(command, timeout, cache/"mux-peak-correction.log")
                validation = validate_video(candidate, tools, plan["frames"], canvas["width"], canvas["height"],
                                            canvas["fps"], timeout, cache/"decode-master-corrected.log", audio_required=True)
                delivered_loudness = audit_loudness(candidate, tools, timeout, cache/"delivery-loudness-corrected.log")
                delivered_loudness["global_attenuation_db"] = correction
            if normalize and delivered_loudness["finite_measurement"] and float(delivered_loudness["true_peak_dbtp"]) > -.95:
                raise RenderError("Delivered true peak exceeds -1 dBTP target after correction; inspect audio before delivery")
            loudness["delivery_measurement"] = delivered_loudness
            loudness["limitation"] = "Normalization preserves timing and measures AAC delivery. It does not repair clipped recordings or certify perceptual mix/voice clarity."
            expected_assets = {Path(plan['plan']): plan['plan_sha256'],
                               Path(plan['audio']['file']): plan['audio']['sha256']}
            expected_assets.update({Path(b['image']): b['image_sha256'] for b in plan['beats']})
            if plan["background"]["mode"] == "image":
                expected_assets[Path(plan["background"]["file"])] = plan["background"]["sha256"]
            for asset, expected_hash in expected_assets.items():
                if file_hash(asset) != expected_hash:
                    raise RenderError(f"Source changed during render: {asset}")
            output.parent.mkdir(parents=True, exist_ok=True)
            if output.exists():
                raise RenderError("Output appeared during rendering; refusing to replace it")
            with candidate.open("rb") as source, output.open("xb") as target:
                shutil.copyfileobj(source, target, length=1024*1024)
            if file_hash(output) != validation["sha256"]:
                raise RenderError("Delivered file hash does not match validated candidate")
            state.update(status="complete", output=str(output), validation=validation, loudness=loudness)
            report = output.with_suffix(".render-report.json")
            if report.exists():
                report = workdir / f"delivery-{key}.json"
            json_write(checkpoint, state)
            json_write(report, state)
            return {"status": "complete", "output": str(output), "report": str(report),
                    "cache_key": key, "rendered_segments": state["rendered_segments"],
                    "reused_segments": state["reused_segments"], "validation": validation}
        except (RenderError, OSError, ValueError) as error:
            state.update(status="failed", error=str(error))
            json_write(checkpoint, state)
            raise


def preview_dimensions(value: str) -> tuple[int, int]:
    try:
        width, height = (int(part) for part in value.lower().split("x"))
    except ValueError as error:
        raise argparse.ArgumentTypeError("Use WIDTHxHEIGHT, e.g. 640x360") from error
    return width, height


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--workdir", type=Path)
    parser.add_argument("--preview", type=preview_dimensions)
    parser.add_argument("--threads", type=int, default=2)
    parser.add_argument("--timeout-seconds", type=float, default=900)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--no-loudnorm", action="store_true", help="Keep supplied audio level; report normalization disabled")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    try:
        if not math.isfinite(args.timeout_seconds) or args.timeout_seconds <= 0:
            raise RenderError("timeout must be positive and finite")
        if args.validate_only:
            result = validate_plan(args.plan, tool_paths(), args.timeout_seconds, args.preview)
            print(json.dumps({"status": "valid", "plan": result}, ensure_ascii=False))
            return 0
        if args.output is None:
            raise RenderError("--output is required unless --validate-only is used")
        workdir = args.workdir or args.plan.resolve().parent / "render-work" / args.output.stem
        print(json.dumps(render(args.plan, args.output, workdir, args.preview, args.threads,
                                args.timeout_seconds, args.resume, not args.no_loudnorm), ensure_ascii=False))
        return 0
    except (RenderError, OSError, ValueError) as error:
        print(f"Render error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
