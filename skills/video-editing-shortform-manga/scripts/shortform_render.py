#!/usr/bin/env python3
"""ShortForm Manga Motion: strict plan validation and a real FFmpeg editor.

Python 3.11+, ffmpeg and ffprobe. No ASR, TTS, scene classification, or network calls.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

VERSION = "1.0.0"
ACTIONS = {"follow", "like", "comment"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
EPS = 1e-4


class PlanError(ValueError):
    pass


def require(ok: bool, message: str) -> None:
    if not ok:
        raise PlanError(message)


def source_path(root: Path, name: str) -> Path:
    require(isinstance(name, str) and bool(name.strip()), "caminho da fonte vazio")
    p = (root / name).resolve()
    require(p.is_file(), f"fonte não encontrada: {p}")
    return p


def probe(path: Path) -> dict:
    cp = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration:stream=codec_type,width,height,avg_frame_rate",
         "-of", "json", str(path)], capture_output=True, text=True
    )
    require(cp.returncode == 0, f"ffprobe falhou: {path}: {cp.stderr.strip()}")
    return json.loads(cp.stdout)


def validate(path: Path) -> tuple[dict, dict]:
    require(shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None,
            "FFmpeg e FFprobe precisam estar no PATH")
    plan = json.loads(path.read_text(encoding="utf-8"))
    require(plan.get("schema_version") == 1, "schema_version deve ser 1")
    root = path.parent
    canvas = plan.get("canvas", {})
    w, h, fps = canvas.get("width"), canvas.get("height"), canvas.get("fps")
    require(all(type(v) is int for v in (w, h, fps)), "canvas requer inteiros")
    require(120 <= w <= 4096 and 120 <= h <= 4096 and w % 2 == 0 and h % 2 == 0,
            "canvas inválido ou dimensões ímpares")
    require(15 <= fps <= 60, "fps fora da faixa [15,60]")
    require(h > w, "perfil shortform requer vídeo vertical")
    voice = source_path(root, plan.get("audio"))
    voice_probe = probe(voice)
    require(any(s.get("codec_type") == "audio" for s in voice_probe.get("streams", [])),
            "fonte de narração não contém áudio")
    voice_duration = float(voice_probe.get("format", {}).get("duration") or 0)
    require(voice_duration > 0, "duração de áudio inválida")
    music = plan.get("music")
    if music:
        mpath = source_path(root, music)
        require(any(s.get("codec_type") == "audio" for s in probe(mpath).get("streams", [])),
                "música não contém áudio")
    gain = plan.get("music_gain", 0.12)
    require(isinstance(gain, (float, int)) and 0 <= gain <= 0.35,
            "music_gain deve estar entre 0 e 0.35")
    beats = plan.get("segments")
    require(isinstance(beats, list) and beats, "segments requer ao menos um plano")
    last = 0.0
    protected = []
    seen = set()
    for index, seg in enumerate(beats):
        name = seg.get("id")
        require(isinstance(name, str) and name and name not in seen,
                f"segmento {index}: id obrigatório e único")
        seen.add(name)
        start, end = seg.get("start"), seg.get("end")
        require(all(isinstance(t, (int, float)) and math.isfinite(t) for t in (start, end)),
                f"{name}: tempos inválidos")
        require(abs(start-last) <= 0.5 / fps + EPS and end > start + 0.5 / fps,
                f"{name}: sobreposição, lacuna ou duração não positiva")
        require(abs(start*fps-round(start*fps)) <= 0.08 and
                abs(end*fps-round(end*fps)) <= 0.08,
                f"{name}: marcas precisam estar alinhadas aos frames")
        last = float(end)
        image = seg.get("image")
        video = seg.get("video")
        require(bool(image) != bool(video), f"{name}: escolha image OU video")
        if image:
            require(source_path(root, image).suffix.lower() in IMAGE_EXT,
                    f"{name}: formato de imagem não aceito")
        else:
            vp = source_path(root, video)
            require(any(s.get("codec_type") == "video" for s in probe(vp).get("streams", [])),
                    f"{name}: não há stream de vídeo")
            src_start = seg.get("source_start", 0)
            require(isinstance(src_start, (int, float)) and src_start >= 0,
                    f"{name}: source_start inválido")
        focus = seg.get("focus", [0.5, 0.5])
        zoom = seg.get("zoom", [1, 1.12])
        require(isinstance(focus, list) and len(focus) == 2 and all(
            isinstance(v, (int, float)) and 0 <= v <= 1 for v in focus),
            f"{name}: focus deve conter dois valores 0..1")
        require(isinstance(zoom, list) and len(zoom) == 2 and all(
            isinstance(v, (int, float)) and 1 <= v <= 2 for v in zoom),
            f"{name}: zoom deve conter dois valores 1..2")
        require(seg.get("reviewed") is True, f"{name}: recorte precisa de reviewed=true")
        require(isinstance(seg.get("why"), str) and seg["why"].strip(),
                f"{name}: justificativa narrativa ausente")
        if seg.get("protected", False):
            protected.append((float(start), float(end), name))
    total = last
    require(2 <= total <= 180, "duração deve estar entre 2 e 180 segundos")
    require(abs(total-voice_duration) <= max(0.25, 2 / fps),
            f"áudio ({voice_duration:.3f}s) e vídeo ({total:.3f}s) divergentes")
    for interval in plan.get("protected_intervals", []):
        st, en = interval["start"], interval["end"]
        require(0 <= st < en <= total, "protected_intervals inválido")
        protected.append((float(st), float(en), "intervalo protegido"))
    ctas = plan.get("cta", [])
    require(isinstance(ctas, list), "cta precisa ser lista")
    require(len(ctas) <= (2 if total >= 75 else 1),
            "CTA excessivo: regra de 1 por vídeo, 2 apenas se >=75s")
    for cta in ctas:
        act, text = cta.get("action"), cta.get("text")
        st, duration = cta.get("start"), cta.get("duration")
        require(act in ACTIONS, "cta.action inválido")
        require(isinstance(text, str) and 1 <= len(text.strip()) <= 56 and
                "\n" not in text and "\r" not in text,
                "CTA deve usar frase curta de uma linha")
        require(isinstance(cta.get("why_now"), str) and cta["why_now"].strip(),
                "CTA deve justificar oportunidade narrativa")
        require(all(isinstance(x, (int, float)) for x in (st, duration)) and
                st >= 3 and 1 <= duration <= 2.5 and st+duration <= total+EPS,
                "CTA fora da área temporal permitida")
        require(not any(st < pe-EPS and (st+duration) > ps+EPS
                        for ps, pe, _ in protected),
                "CTA invade clímax/intervalo protegido")
    return plan, {"duration": total, "audio_duration": voice_duration,
                  "protected": protected, "segment_count": len(beats),
                  "cta_count": len(ctas)}


def run(cmd: list[str], log: Path) -> None:
    with log.open("a", encoding="utf-8") as f:
        f.write("COMMAND " + json.dumps(cmd, ensure_ascii=False) + "\n")
        cp = subprocess.run(cmd, text=True, stdout=f, stderr=subprocess.STDOUT)
    require(cp.returncode == 0, f"FFmpeg falhou ({cp.returncode}); log: {log}")


def clip_filter(width: int, height: int, fps: int, n: int, seg: dict) -> str:
    fx, fy = seg.get("focus", [0.5, 0.5])
    za, zb = seg.get("zoom", [1, 1.12])
    # Zoompan's 'on' counts output frames, with smoothstep interpolation.
    fraction = f"(on/{max(1,n-1)})"
    eased = f"({fraction}*{fraction}*(3-2*{fraction}))"
    z = f"{za:.6f}+({zb-za:.6f})*{eased}"
    return (
        f"scale={width}:{height}:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop={width}:{height}:x='(in_w-out_w)*{fx:.5f}':"
        f"y='(in_h-out_h)*{fy:.5f}',"
        f"zoompan=z='{z}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':"
        f"d=1:s={width}x{height}:fps={fps},format=yuv420p"
    )


def cta_filters(plan: dict, output_width: int, output_height: int, temp: Path) -> list[str]:
    filters = []
    for ix, cta in enumerate(plan.get("cta", [])):
        start = float(cta["start"])
        end = start + float(cta["duration"])
        textfile = temp / f"cta_{ix:02d}.txt"
        textfile.write_text(cta["text"], encoding="utf-8")
        active = f"between(t\\,{start:.3f}\\,{end:.3f})"
        fadein = f"min(1\\,max(0\\,(t-{start:.3f})/0.22))"
        fadeout = f"min(1\\,max(0\\,({end:.3f}-t)/0.22))"
        alpha = f"{fadein}*{fadeout}"
        x = f"(w-text_w)/2-24*max(0\\,1-(t-{start:.3f})/0.25)"
        filters.append(
            "drawbox=x=iw*0.09:y=ih*0.67:w=iw*0.82:h=ih*0.075:"
            f"color=black@0.34:t=fill:enable='{active}'"
        )
        font = plan.get("font_file")
        font_argument = (
            f"fontfile='{source_path(temp.parent.parent, font)}'"
            if font else "font='DejaVu Sans'"
        )
        filters.append(
            f"drawtext={font_argument}:textfile='{textfile}':"
            f"fontsize={max(15, round(output_width*0.038))}:fontcolor=white:"
            "shadowcolor=black@0.55:shadowx=1:shadowy=1:"
            f"x='{x}':y='h*0.687':alpha='{alpha}':enable='{active}'"
        )
    return filters


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()


def render(plan_path: Path, output: Path, workdir: Path, preview_scale: float) -> dict:
    plan, info = validate(plan_path)
    require(not output.exists(), f"saída já existe, não sobrescrever: {output}")
    width = round(plan["canvas"]["width"]*preview_scale/2)*2
    height = round(plan["canvas"]["height"]*preview_scale/2)*2
    fps = plan["canvas"]["fps"]
    require(width >= 120 and height >= 120, "preview muito pequeno")
    workdir.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix="shortform_", dir=workdir))
    log = temp / "ffmpeg.log"
    parts = []
    for idx, seg in enumerate(plan["segments"]):
        frames = round((seg["end"]-seg["start"])*fps)
        require(frames > 0, "segmento sem frames")
        clip = temp / f"part_{idx:03d}.mp4"
        src = source_path(plan_path.parent, seg.get("image") or seg.get("video"))
        cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y"]
        if seg.get("image"):
            cmd += ["-loop", "1", "-framerate", str(fps), "-i", str(src)]
        else:
            cmd += ["-ss", str(seg.get("source_start", 0)), "-i", str(src)]
        cmd += ["-an", "-vf", clip_filter(width,height,fps,frames,seg),
                "-frames:v", str(frames), "-r", str(fps), "-c:v", "libx264",
                "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
                str(clip)]
        run(cmd, log)
        require(clip.exists() and clip.stat().st_size > 0, "clipe não gerado")
        parts.append(clip)
    playlist = temp / "concat.txt"
    playlist.write_text("".join(
        "file '" + str(part).replace("'", "'\\''") + "'\n" for part in parts
    ), encoding="utf-8")
    joined = temp / "joined.mp4"
    run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
         "-f", "concat", "-safe", "0", "-i", str(playlist), "-c", "copy",
         "-an", str(joined)], log)
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
           "-i", str(joined), "-i", str(source_path(plan_path.parent,plan["audio"]))]
    filters = cta_filters(plan, width, height, temp)
    if filters:
        cmd += ["-filter_complex", "[0:v]" + ",".join(filters) + "[v]"]
        vmap = "[v]"
    else:
        vmap = "0:v:0"
    music = plan.get("music")
    if music:
        cmd += ["-i", str(source_path(plan_path.parent,music))]
        audio_graph = (
            "[1:a:0]aresample=48000,asetpts=PTS-STARTPTS[a0];"
            f"[2:a:0]aresample=48000,volume={plan.get('music_gain',0.12):.4f},"
            f"atrim=0:{info['duration']:.3f},asetpts=PTS-STARTPTS[a1];"
            "[a0][a1]amix=inputs=2:duration=first:dropout_transition=0[aout]"
        )
        if filters:
            # Merge audio chains with video overlay into one filtergraph.
            at = cmd.index("-filter_complex") + 1
            cmd[at] += ";" + audio_graph
        else:
            cmd += ["-filter_complex", audio_graph]
        amap = "[aout]"
    else:
        amap = "1:a:0"
    cmd += ["-map", vmap, "-map", amap, "-t", str(info["duration"]),
            "-c:v", "libx264", "-preset", "medium", "-crf", "19",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
            "-ar", "48000", "-movflags", "+faststart", str(output)]
    run(cmd, log)
    require(output.is_file() and output.stat().st_size > 0, "master não gerado")
    run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(output),
         "-f", "null", "-"], log)
    meta = probe(output)
    streams = meta.get("streams", [])
    videos = [s for s in streams if s.get("codec_type") == "video"]
    audios = [s for s in streams if s.get("codec_type") == "audio"]
    require(len(videos) == 1 and len(audios) == 1, "master requer um vídeo e um áudio")
    require(videos[0].get("width") == width and videos[0].get("height") == height,
            "dimensões finais incorretas")
    actual_duration = float(meta.get("format", {}).get("duration", 0))
    require(abs(actual_duration-info["duration"]) <= 0.20,
            "duração final diverge do plano")
    result = {
        "status": "technically_validated", "version": VERSION,
        "source_plan": str(plan_path), "output": str(output),
        "duration_expected": info["duration"], "duration_measured": actual_duration,
        "canvas": {"width":width,"height":height,"fps":fps},
        "sha256": digest(output), "segments": info["segment_count"],
        "cta": info["cta_count"], "preview": preview_scale < 1,
        "ffmpeg_log": str(log),
        "human_review_pending": [
            "sincronismo da voz", "inteligibilidade e loudness do mix",
            "revisão de recortes em movimento", "CTA em celular",
            "clímax, desfecho e direitos das fontes"
        ],
    }
    report = output.with_suffix(".edit-report.json")
    report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    s = p.add_subparsers(dest="cmd", required=True)
    v = s.add_parser("validate")
    v.add_argument("plan", type=Path)
    r = s.add_parser("render")
    r.add_argument("plan", type=Path)
    r.add_argument("--output", type=Path, required=True)
    r.add_argument("--workdir", type=Path, default=Path(".shortform-work"))
    r.add_argument("--preview-scale",type=float,default=1.0)
    args = p.parse_args()
    try:
        plan = args.plan.resolve()
        if args.cmd == "validate":
            _, details = validate(plan)
            print(json.dumps({"status":"valid",**details},ensure_ascii=False,indent=2))
        else:
            require(0.25 <= args.preview_scale <= 1.0, "preview-scale deve ser 0.25..1")
            result = render(plan,args.output.resolve(),args.workdir.resolve(),
                            args.preview_scale)
            print(json.dumps(result,ensure_ascii=False,indent=2))
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERRO: {exc}",file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
