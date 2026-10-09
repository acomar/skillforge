#!/usr/bin/env python3
"""Local video evidence, resumable chapter analysis and technical validation.

Python 3.11+, standard library, FFmpeg and FFprobe. No media is downloaded,
modified or loaded into memory in full. Still timestamps are requested seek
positions, not a claim of frame-accurate annotations. Scene times are relative
to playback zero (the container start_time is removed by FFmpeg).
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Iterator

VERSION = "1.0.0"
SCHEMA = 1
MAX_STILLS_PER_CHAPTER = 1000


class WorkbenchError(Exception):
    """An actionable failure; never silently turn failed extraction into evidence."""


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def write_json(path: Path, value: Any, *, replace: bool = False) -> None:
    """Replace only owned work files; public reports never overwrite existing files."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".json-", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(json_bytes(value))
            handle.flush()
            os.fsync(handle.fileno())
        if replace:
            os.replace(temporary, path)
            temporary = None
        elif os.name == "nt":
            # Windows rename fails if the destination exists; avoids hard-link
            # privileges unavailable in some restricted Windows environments.
            os.rename(temporary, path)
            temporary = None
        else:
            # Hard linking publishes a complete file atomically without clobbering.
            os.link(temporary, path)
    except FileExistsError as exc:
        raise WorkbenchError(f"Report already exists; choose a new path: {path}") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def local_source(value: str | Path) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise WorkbenchError(f"Local input file does not exist: {path}")
    return path


def public_report(value: str, source: Path) -> Path:
    path = Path(value).expanduser().resolve()
    if path == source:
        raise WorkbenchError("The report path must differ from the input file")
    if path.exists():
        raise WorkbenchError(f"Report already exists; choose a new path: {path}")
    return path


def owned_path(root: Path, relative: str | Path) -> Path:
    candidate = root / relative
    resolved = candidate.resolve()
    if not resolved.is_relative_to(root) or resolved == root:
        raise WorkbenchError(f"Artifact path escapes the work directory: {relative}")
    if candidate.is_symlink():
        raise WorkbenchError(f"Refusing a symbolic link at artifact path: {candidate}")
    return resolved


def tool_paths() -> dict[str, str]:
    paths = {name: shutil.which(name) for name in ("ffmpeg", "ffprobe")}
    missing = [name for name, path in paths.items() if not path]
    if missing:
        raise WorkbenchError("Install required executables on PATH: " + ", ".join(missing))
    return {name: str(path) for name, path in paths.items()}


def execute(command: list[str], timeout: float, *, log: Path | None = None) -> str:
    """Run without a shell, stream FFmpeg diagnostics to disk, enforce timeout."""
    try:
        if log is None:
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8",
                                    errors="replace", timeout=timeout, check=False)
            if result.returncode:
                raise WorkbenchError(f"{Path(command[0]).name} failed ({result.returncode}): "
                                     + result.stderr[-2000:].strip())
            return result.stdout
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("wb") as handle:
            result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=handle,
                                    timeout=timeout, check=False)
        if result.returncode:
            with log.open("rb") as handle:
                handle.seek(max(0, log.stat().st_size - 2000))
                tail = handle.read().decode("utf-8", errors="replace").strip()
            raise WorkbenchError(f"{Path(command[0]).name} failed ({result.returncode}); "
                                 f"see {log}: {tail}")
        return ""
    except subprocess.TimeoutExpired as exc:
        raise WorkbenchError(f"{Path(command[0]).name} exceeded {timeout:g} seconds"
                             + (f"; partial log: {log}" if log else "")) from exc
    except OSError as exc:
        raise WorkbenchError(f"Cannot run {Path(command[0]).name}: {exc}") from exc


def versions(paths: dict[str, str], timeout: float) -> dict[str, Any]:
    result: dict[str, Any] = {"workbench": VERSION, "python": sys.version.split()[0]}
    for name, executable in paths.items():
        output = execute([executable, "-version"], timeout)
        result[name] = {"executable": executable, "version": output.splitlines()[0],
                        "build_sha256": hashlib.sha256(output.encode()).hexdigest()}
    return result


def finite_positive(value: Any) -> float | None:
    try:
        number = float(value)
        return number if math.isfinite(number) and number > 0 else None
    except (ValueError, TypeError):
        return None


def facts(payload: dict[str, Any]) -> dict[str, Any]:
    stream_list = payload.get("streams", [])
    duration = finite_positive(payload.get("format", {}).get("duration"))
    if duration is None:
        durations = [finite_positive(stream.get("duration")) for stream in stream_list]
        duration = max((value for value in durations if value is not None), default=None)
    video = []
    audio = []
    for stream in stream_list:
        if stream.get("codec_type") == "video" and not stream.get("disposition", {}).get("attached_pic"):
            rotation = next((item.get("rotation") for item in stream.get("side_data_list", [])
                             if "rotation" in item), stream.get("tags", {}).get("rotate"))
            video.append({"index": stream["index"], "codec": stream.get("codec_name"),
                          "width": stream.get("width"), "height": stream.get("height"),
                          "pixel_format": stream.get("pix_fmt"), "rotation_degrees": rotation,
                          "sample_aspect_ratio": stream.get("sample_aspect_ratio"),
                          "display_aspect_ratio": stream.get("display_aspect_ratio"),
                          "average_frame_rate": stream.get("avg_frame_rate"),
                          "real_frame_rate": stream.get("r_frame_rate"),
                          "color_space": stream.get("color_space"),
                          "color_range": stream.get("color_range")})
        elif stream.get("codec_type") == "audio":
            audio.append({"index": stream["index"], "codec": stream.get("codec_name"),
                          "sample_rate": stream.get("sample_rate"), "channels": stream.get("channels"),
                          "channel_layout": stream.get("channel_layout")})
    return {"duration_seconds": duration, "start_time": payload.get("format", {}).get("start_time"),
            "format": payload.get("format", {}).get("format_name"),
            "video_streams": video, "audio_streams": audio}


def probe(source: Path, paths: dict[str, str], timeout: float, *, source_hash: str | None = None) -> dict[str, Any]:
    signature = source_signature(source)
    output = execute([paths["ffprobe"], "-v", "error", "-protocol_whitelist", "file,pipe",
                      "-show_format", "-show_streams", "-show_chapters", "-of", "json", str(source)], timeout)
    try:
        payload = json.loads(output)
    except ValueError as exc:
        raise WorkbenchError("FFprobe did not return valid JSON") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("streams"), list):
        raise WorkbenchError("FFprobe returned an unexpected metadata shape")
    checksum = source_hash or digest(source)
    unchanged(source, signature)
    return {"schema_version": SCHEMA, "source": str(source), "source_sha256": checksum,
            "source_size_bytes": signature[0], "facts": facts(payload), "ffprobe": payload}


def source_signature(source: Path) -> tuple[int, int]:
    stat = source.stat()
    return stat.st_size, stat.st_mtime_ns


def unchanged(source: Path, signature: tuple[int, int]) -> None:
    if source_signature(source) != signature:
        raise WorkbenchError("Input changed during analysis; restart with the unchanged source")


def chapters(duration: float, chunk: float, overlap: float) -> list[dict[str, Any]]:
    result = []
    for index in range(math.ceil(duration / chunk)):
        start = index * chunk
        end = min(duration, (index + 1) * chunk)
        result.append({"id": index + 1, "start_seconds": start, "end_seconds": end,
                       "window_start_seconds": max(0.0, start - overlap),
                       "window_end_seconds": min(duration, end + overlap)})
    return result


def sample_times(chapter: dict[str, Any], sample: float) -> list[float]:
    duration = chapter["end_seconds"] - chapter["start_seconds"]
    count = math.ceil(duration / sample)
    if count > MAX_STILLS_PER_CHAPTER:
        raise WorkbenchError(f"Chapter requests {count} stills; limit is {MAX_STILLS_PER_CHAPTER}. "
                             "Increase --sample-seconds or reduce --chunk-seconds")
    # Midpoints sample the final partial interval too; never seek past media end.
    return [chapter["start_seconds"] + (i * sample + min((i + 1) * sample, duration)) / 2
            for i in range(count)]


def artifact(root: Path, path: Path) -> dict[str, Any]:
    return {"path": path.relative_to(root).as_posix(), "size_bytes": path.stat().st_size,
            "sha256": digest(path)}


def artifact_valid(root: Path, item: Any) -> bool:
    if not isinstance(item, dict):
        return False
    try:
        path = owned_path(root, item["path"])
        return path.is_file() and path.stat().st_size == item["size_bytes"] and digest(path) == item["sha256"]
    except (KeyError, OSError, TypeError, ValueError, WorkbenchError):
        return False


def valid_checkpoint(root: Path, path: Path, key: str, chapter: dict[str, Any],
                     times: list[float]) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if (payload["schema_version"] != SCHEMA or payload["cache_key"] != key
                or payload["status"] != "complete" or payload["chapter"] != chapter
                or payload["scene_detection"]["status"] != "complete"):
            return None
        stills = payload["stills"]
        if [item["requested_time_seconds"] for item in stills] != times:
            return None
        if not all(artifact_valid(root, item) for item in stills):
            return None
        if not artifact_valid(root, payload["scene_detection"]["log"]):
            return None
        scenes = payload["scene_detection"]["candidates"]
        if not isinstance(scenes, list) or any(not chapter["start_seconds"] <= item["time_seconds"]
                                             < chapter["end_seconds"] for item in scenes):
            return None
        return payload
    except (OSError, ValueError, KeyError, TypeError, WorkbenchError):
        return None


def scene_candidates(log: Path, chapter: dict[str, Any]) -> list[dict[str, float]]:
    timestamp = None
    candidates = []
    with log.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            time_match = re.search(r"\bpts_time:([-+\d.eE]+)", line)
            if time_match:
                timestamp = float(time_match.group(1))
            score_match = re.search(r"lavfi\.scene_score=([-+\d.eE]+)", line)
            if score_match and timestamp is not None:
                global_time = chapter["window_start_seconds"] + timestamp
                score = float(score_match.group(1))
                if (math.isfinite(global_time) and math.isfinite(score)
                        and chapter["start_seconds"] <= global_time < chapter["end_seconds"]):
                    candidates.append({"time_seconds": round(global_time, 6), "score": score})
                timestamp = None
    return candidates


def analyze_chapter(source: Path, paths: dict[str, str], root: Path, directory: Path,
                    key: str, chapter: dict[str, Any], times: list[float], options: dict[str, Any],
                    stream_index: int, signature: tuple[int, int]) -> dict[str, Any]:
    directory.mkdir(parents=True, exist_ok=True)
    checkpoint = owned_path(root, directory.relative_to(root) / "checkpoint.json")
    payload: dict[str, Any] = {"schema_version": SCHEMA, "cache_key": key,
                               "chapter": chapter, "status": "running", "stills": []}
    write_json(checkpoint, payload, replace=True)
    stage = "scene_detection"
    try:
        unchanged(source, signature)
        scene_log = owned_path(root, directory.relative_to(root) / "scenes.log")
        window_start = chapter["window_start_seconds"]
        window_duration = chapter["window_end_seconds"] - window_start
        execute([paths["ffmpeg"], "-hide_banner", "-nostdin", "-nostats", "-loglevel", "info",
                 "-xerror", "-protocol_whitelist", "file,pipe", "-ss", f"{window_start:.9f}",
                 "-t", f"{window_duration:.9f}", "-i", str(source), "-map", f"0:{stream_index}",
                 "-vf", f"select=gt(scene\\,{options['scene_threshold']}),metadata=mode=print",
                 "-an", "-sn", "-dn", "-f", "null", "-"], options["timeout_seconds"], log=scene_log)
        payload["scene_detection"] = {"status": "complete", "log": artifact(root, scene_log),
                                       "candidates": scene_candidates(scene_log, chapter)}
        stage = "stills"
        for index, requested_time in enumerate(times):
            unchanged(source, signature)
            output = owned_path(root, directory.relative_to(root) / f"still-{index + 1:04d}.jpg")
            temporary = owned_path(root, directory.relative_to(root) / f".still-{index + 1:04d}.tmp.jpg")
            log = owned_path(root, directory.relative_to(root) / "stills.log")
            try:
                execute([paths["ffmpeg"], "-hide_banner", "-nostdin", "-loglevel", "error",
                         "-xerror", "-protocol_whitelist", "file,pipe", "-ss", f"{requested_time:.9f}",
                         "-i", str(source), "-map", f"0:{stream_index}", "-frames:v", "1", "-an", "-sn", "-dn",
                         "-vf", "scale=320:-2", "-q:v", "3", "-y", str(temporary)],
                        options["timeout_seconds"], log=log)
                if not temporary.is_file() or temporary.stat().st_size == 0:
                    raise WorkbenchError(f"No video frame at requested time {requested_time:g}")
                os.replace(temporary, output)
            finally:
                temporary.unlink(missing_ok=True)
            payload["stills"].append({**artifact(root, output), "requested_time_seconds": requested_time})
        unchanged(source, signature)
        payload["status"] = "complete"
        write_json(checkpoint, payload, replace=True)
        return payload
    except (WorkbenchError, OSError) as exc:
        payload.update(status="failed", failure_stage=stage, error=str(exc))
        write_json(checkpoint, payload, replace=True)
        raise


@contextmanager
def workspace_lock(root: Path) -> Iterator[None]:
    lock = owned_path(root, ".video-workbench.lock")
    try:
        descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise WorkbenchError(f"Work directory is locked: {lock}. If the previous process stopped, "
                             "remove only this lock file before resuming") from exc
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(f"pid={os.getpid()}\n")
        yield
    finally:
        lock.unlink(missing_ok=True)


def analyze(args: argparse.Namespace, paths: dict[str, str]) -> dict[str, Any]:
    source = local_source(args.input)
    signature = source_signature(source)
    source_hash = digest(source)
    unchanged(source, signature)
    metadata = probe(source, paths, args.timeout_seconds, source_hash=source_hash)
    duration = metadata["facts"]["duration_seconds"]
    video = metadata["facts"]["video_streams"]
    if duration is None or not video:
        raise WorkbenchError("Analysis requires a video stream and a finite positive duration")
    options = {"chunk_seconds": args.chunk_seconds, "sample_seconds": args.sample_seconds,
               "overlap_seconds": args.overlap_seconds, "scene_threshold": args.scene_threshold,
               "timeout_seconds": args.timeout_seconds, "still_width": 320}
    plan = chapters(duration, args.chunk_seconds, args.overlap_seconds)
    time_lists = [sample_times(chapter, args.sample_seconds) for chapter in plan]
    tool_versions = versions(paths, args.timeout_seconds)
    identity = {"source_sha256": source_hash, "source_size_bytes": signature[0],
                "options": options, "versions": tool_versions, "schema_version": SCHEMA}
    key = hashlib.sha256(json_bytes(identity)).hexdigest()
    root = Path(args.workdir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    if source == owned_path(root, "analysis.json"):
        raise WorkbenchError("Input cannot occupy a managed analysis path")
    manifest_path = owned_path(root, "analysis.json")
    cache = owned_path(root, Path("cache") / key)
    manifest: dict[str, Any] = {"schema_version": SCHEMA, "status": "running", "cache_key": key,
                                "source": str(source), "identity": identity, "facts": metadata["facts"],
                                "chapter_count": len(plan), "chapters": [], "reused_chapters": 0,
                                "processed_chapters": 0,
                                "limitations": ["Stills are sparse samples at requested seek positions.",
                                                "Scene scores propose visual changes, not editorial boundaries.",
                                                "Audio, subtitles and narrative meaning were not analyzed."]}
    with workspace_lock(root):
        try:
            cache.mkdir(parents=True, exist_ok=True)
            write_json(owned_path(root, cache.relative_to(root) / "probe.json"), metadata, replace=True)
            write_json(manifest_path, manifest, replace=True)
            for chapter, times in zip(plan, time_lists, strict=True):
                unchanged(source, signature)
                directory = owned_path(root, cache.relative_to(root) / f"chapter-{chapter['id']:05d}")
                checkpoint = owned_path(root, directory.relative_to(root) / "checkpoint.json")
                cached = valid_checkpoint(root, checkpoint, key, chapter, times) if args.resume else None
                if cached:
                    payload = cached
                    manifest["reused_chapters"] += 1
                else:
                    payload = analyze_chapter(source, paths, root, directory, key, chapter, times,
                                              options, video[0]["index"], signature)
                    manifest["processed_chapters"] += 1
                manifest["chapters"].append({**chapter, "checkpoint": checkpoint.relative_to(root).as_posix(),
                                              "stills": payload["stills"],
                                              "scene_candidates": payload["scene_detection"]["candidates"]})
                write_json(manifest_path, manifest, replace=True)
            unchanged(source, signature)
            manifest["status"] = "complete"
            write_json(manifest_path, manifest, replace=True)
        except (WorkbenchError, OSError) as exc:
            manifest.update(status="failed", error=str(exc), completed_chapters=len(manifest["chapters"]))
            write_json(manifest_path, manifest, replace=True)
            raise
    return {"status": "complete", "analysis": str(manifest_path), "cache_key": key,
            "chapter_count": len(plan), "reused_chapters": manifest["reused_chapters"],
            "processed_chapters": manifest["processed_chapters"]}


def validate(args: argparse.Namespace, paths: dict[str, str]) -> tuple[dict[str, Any], bool]:
    source = Path(args.output).expanduser().resolve()
    report_path = public_report(args.report, source)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {"schema_version": SCHEMA, "source": str(source), "status": "failed",
                              "expected_duration_seconds": args.expected_duration,
                              "tolerance_seconds": args.tolerance, "checks": {},
                              "editorial_audio": "not_evaluated",
                              "limitations": ["No assessment of sound mix, intelligibility, sync, captions or editorial intent.",
                                               "Geometry is reported; no target resolution or aspect ratio was supplied."]}
    try:
        source = local_source(source)
        signature = source_signature(source)
        metadata = probe(source, paths, args.timeout_seconds)
        report["facts"] = metadata["facts"]
        report["source_sha256"] = metadata["source_sha256"]
        report["source_size_bytes"] = metadata["source_size_bytes"]
        actual = metadata["facts"]["duration_seconds"]
        video = metadata["facts"]["video_streams"]
        report["checks"]["video_stream_present"] = bool(video)
        report["checks"]["geometry_valid"] = bool(video) and all(
            finite_positive(item["width"]) is not None and finite_positive(item["height"]) is not None
            for item in video)
        report["checks"]["duration_matches"] = actual is not None and abs(actual - args.expected_duration) <= args.tolerance
        report["duration_difference_seconds"] = None if actual is None else actual - args.expected_duration
        with tempfile.TemporaryDirectory(prefix="video-validation-", dir=report_path.parent) as temporary:
            directory = Path(temporary)
            decode_log = directory / "decode.log"
            progress = directory / "progress.txt"
            try:
                execute([paths["ffmpeg"], "-hide_banner", "-nostdin", "-nostats", "-loglevel", "error",
                         "-xerror", "-err_detect", "explode", "-protocol_whitelist", "file,pipe", "-i", str(source),
                         "-map", "0:v?", "-map", "0:a?", "-sn", "-dn", "-progress", str(progress),
                         "-f", "null", "-"], args.timeout_seconds, log=decode_log)
            except WorkbenchError:
                if decode_log.exists():
                    with decode_log.open("rb") as handle:
                        handle.seek(max(0, decode_log.stat().st_size - 4000))
                        report["decode_log_tail"] = handle.read().decode("utf-8", errors="replace")
                raise
            progress_text = progress.read_text(encoding="utf-8", errors="replace") if progress.exists() else ""
            frames = re.findall(r"^frame=(\d+)\s*$", progress_text, flags=re.MULTILINE)
            decoded_frames = int(frames[-1]) if frames else 0
            report["decoded_video_frames"] = decoded_frames
            report["checks"]["full_decode"] = "progress=end" in progress_text and decoded_frames > 0
            report["decode_scope"] = "All video and audio streams were decoded from start to EOF with FFmpeg -xerror."
        unchanged(source, signature)
        passed = all(report["checks"].values())
        report["status"] = "passed" if passed else "failed"
    except (WorkbenchError, OSError) as exc:
        report["checks"]["full_decode"] = False
        report["error"] = str(exc)
        passed = False
    write_json(report_path, report)
    return {"status": report["status"], "report": str(report_path), "checks": report["checks"]}, passed


def positive(value: str) -> float:
    number = finite_positive(value)
    if number is None:
        raise argparse.ArgumentTypeError("must be a finite positive number")
    return number


def nonnegative(value: str) -> float:
    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a finite nonnegative number") from exc
    if not math.isfinite(number) or number < 0:
        raise argparse.ArgumentTypeError("must be a finite nonnegative number")
    return number


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--version", action="version", version=VERSION)
    commands = result.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser("probe", help="Report technical metadata without modifying the source")
    inspect.add_argument("input")
    inspect.add_argument("--output", required=True, help="New JSON file; existing files are refused")
    inspect.add_argument("--timeout-seconds", type=positive, default=3600.0)
    analysis = commands.add_parser("analyze", help="Analyze every chapter; evidence stays inside workdir")
    analysis.add_argument("input")
    analysis.add_argument("--workdir", required=True)
    analysis.add_argument("--chunk-seconds", type=positive, default=300.0)
    analysis.add_argument("--sample-seconds", type=positive, default=30.0)
    analysis.add_argument("--overlap-seconds", type=nonnegative, default=2.0)
    analysis.add_argument("--scene-threshold", type=nonnegative, default=0.3)
    analysis.add_argument("--timeout-seconds", type=positive, default=3600.0,
                          help="Timeout per subprocess, not the total job duration")
    analysis.add_argument("--resume", action="store_true", help="Reuse only complete, hash-verified chapters")
    validation = commands.add_parser("validate", help="Probe and fully decode an output video")
    validation.add_argument("output")
    validation.add_argument("--expected-duration", required=True, type=positive)
    validation.add_argument("--tolerance", type=nonnegative, default=0.5, help="Duration tolerance in seconds")
    validation.add_argument("--report", required=True, help="New JSON file, also written on validation failure")
    validation.add_argument("--timeout-seconds", type=positive, default=3600.0)
    return result


def main(argv: list[str] | None = None) -> int:
    # Machine-readable stdout remains UTF-8 even under Windows legacy locales.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    arguments = parser().parse_args(argv)
    try:
        if arguments.command == "analyze" and arguments.scene_threshold > 1:
            raise WorkbenchError("--scene-threshold must be between 0 and 1")
        paths = tool_paths()
        passed = True
        if arguments.command == "probe":
            source = local_source(arguments.input)
            report_path = public_report(arguments.output, source)
            write_json(report_path, probe(source, paths, arguments.timeout_seconds))
            summary = {"status": "complete", "output": str(report_path)}
        elif arguments.command == "analyze":
            summary = analyze(arguments, paths)
        else:
            summary, passed = validate(arguments, paths)
        print(json.dumps(summary, ensure_ascii=False))
        return 0 if passed else 1
    except (WorkbenchError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
