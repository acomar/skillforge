#!/usr/bin/env python3
"""ShortForm Manga Motion renderer: image/video beats + continuous narration + discreet CTA.

Requires Python >=3.11, ffmpeg with libx264, drawtext, zoompan; ffprobe.
Plans are a transparent editorial contract. This engine does not use AI to choose scenes.
"""
import argparse
import hashlib
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

VERSION = "1.0.2"
IMAGE_EXTENSIONS = {".png", ".jpeg", ".jpg", ".webp", ".bmp"}

class PlanError(Exception):
    pass


def check(condition, message):
    if not condition:
        raise PlanError(message)


def src(root, rel):
    check(isinstance(rel, str) and bool(rel.strip()), "Caminho da fonte obrigatório")
    result = (root / rel).resolve()
    check(result.is_file(), f"Fonte não encontrada: {result}")
    return result


def ffprobe(path):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate",
                             "-of", "json", str(path)], text=True, capture_output=True)
    check(result.returncode == 0, f"ffprobe falhou para {path}: {result.stderr}")
    return json.loads(result.stdout)


def numeric(v):
    return type(v) in (float, int) and math.isfinite(v)


def validate(path):
    check(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg/FFprobe ausentes")
    p = json.loads(path.read_text(encoding="utf-8"))
    check(p.get("schema_version") == 1, "schema_version deve ser 1")
    c = p.get("canvas", {})
    w, h, fps = c.get("width"), c.get("height"), c.get("fps")
    check(all(type(v) is int for v in [w, h, fps]) and
          120 <= w <= 4096 and 120 <= h <= 4096 and 15 <= fps <= 60 and
          w % 2 == 0 and h % 2 == 0 and h > w,
          "Canvas vertical inválido: width/height pares, fps 15..60")
    root = path.parent
    audio = src(root, p.get("audio"))
    aud = ffprobe(audio)
    check(any(s.get("codec_type") == "audio" for s in aud.get("streams", [])),
          "Narração sem stream de áudio")
    audio_dur = float(aud.get("format", {}).get("duration") or 0)
    check(audio_dur > 0, "Narração com duração zero")
    if p.get("music"):
        m = ffprobe(src(root, p["music"]))
        check(any(s.get("codec_type") == "audio" for s in m.get("streams", [])),
              "Música sem faixa de áudio")
    gain = p.get("music_gain", 0.12)
    check(numeric(gain) and 0 <= gain <= 0.35, "music_gain fora de 0..0.35")
    beats = p.get("segments")
    check(isinstance(beats, list) and beats, "segments precisa conter pelo menos um plano")
    end_previous, seen, protected = 0., set(), []
    for i, b in enumerate(beats):
        ident = b.get("id")
        check(isinstance(ident, str) and ident and ident not in seen,
              f"Beat {i}: id único requerido")
        seen.add(ident)
        start, end = b.get("start"), b.get("end")
        check(numeric(start) and numeric(end) and end > start,
              f"{ident}: marcas inválidas")
        check(abs(start - end_previous) <= 0.51 / fps,
              f"{ident}: lacuna/sobreposição de beats")
        check(abs(start*fps-round(start*fps)) < 0.08 and
              abs(end*fps-round(end*fps)) < 0.08,
              f"{ident}: marque tempos em frames inteiros")
        end_previous = end
        image, video = b.get("image"), b.get("video")
        check(bool(image) != bool(video), f"{ident}: precisa image OU video")
        if image:
            check(src(root, image).suffix.lower() in IMAGE_EXTENSIONS,
                  f"{ident}: imagem em formato não aceito")
        else:
            media = ffprobe(src(root, video))
            check(any(s.get("codec_type") == "video" for s in media.get("streams", [])),
                  f"{ident}: sem faixa de vídeo")
            offset = b.get("source_start", 0)
            check(numeric(offset) and offset >= 0, f"{ident}: source_start inválido")
            mlen = float(media.get("format", {}).get("duration") or 0)
            check(mlen + 0.1 >= offset + end-start,
                  f"{ident}: trecho ultrapassa duração do vídeo original")
        focus = b.get("focus", [0.5, 0.5])
        zoom = b.get("zoom", [1.0, 1.12])
        check(isinstance(focus, list) and len(focus) == 2 and
              all(numeric(v) and 0 <= v <= 1 for v in focus),
              f"{ident}: focus deve ser [0..1,0..1]")
        check(isinstance(zoom, list) and len(zoom) == 2 and
              all(numeric(v) and 1 <= v <= 2 for v in zoom),
              f"{ident}: zoom deve ser [1..2,1..2]")
        check(b.get("reviewed") is True, f"{ident}: recorte não revisado")
        check(isinstance(b.get("why"), str) and b["why"].strip(),
              f"{ident}: razão narrativa ausente")
        if b.get("protected"):
            protected.append((start, end))
    total = end_previous
    check(2 <= total <= 180, "Duração fora de 2 a 180s")
    check(abs(total-audio_dur) <= max(0.25, 2/fps),
          f"Narração ({audio_dur:.3f}s) e vídeo ({total:.3f}s) divergentes")
    for interval in p.get("protected_intervals", []):
        start, end = interval.get("start"), interval.get("end")
        check(numeric(start) and numeric(end) and 0 <= start < end <= total,
              "protected_intervals inválido")
        protected.append((start, end))
    ctas = p.get("cta", [])
    check(isinstance(ctas, list) and len(ctas) <= (2 if total >= 75 else 1),
          "CTAs demais. Máximo 1, ou 2 se >=75s")
    for item in ctas:
        action, text = item.get("action"), item.get("text")
        start, duration = item.get("start"), item.get("duration")
        check(action in {"comment", "follow", "like"}, "CTA inválido")
        check(isinstance(text, str) and 1 <= len(text.strip()) <= 56 and
              "\n" not in text and "\r" not in text,
              "CTA precisa de frase de até 56 caracteres em uma linha")
        check(numeric(start) and numeric(duration) and start >= 3 and
              1 <= duration <= 2.5 and start + duration <= total+0.001,
              "CTA fora da janela temporal")
        check(isinstance(item.get("why_now"), str) and item["why_now"].strip(),
              "Falta justificativa de timing do CTA")
        check(not any(start < b-1e-4 and start+duration > a+1e-4
                      for a, b in protected),
              "CTA atravessa clímax ou intervalo protegido")
    return p, {"duration": total, "audio_duration": audio_dur,
               "segment_count": len(beats), "cta_count": len(ctas),
               "protected": protected}


def shell(command, logfile):
    with logfile.open("a", encoding="utf-8") as output:
        output.write("COMMAND " + json.dumps(command,ensure_ascii=False) + "\n")
        result = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT)
    check(result.returncode == 0, f"FFmpeg falhou ({result.returncode}); veja {logfile}")


def motion_filter(width, height, fps, frames, beat):
    fx, fy = beat.get("focus", [0.5, 0.5])
    z0, z1 = beat.get("zoom", [1.0, 1.12])
    t = f"(on/{max(1,frames-1)})"
    smooth = f"({t}*{t}*(3-2*{t}))"
    z = f"{z0:.6f}+({z1-z0:.6f})*{smooth}"
    return (f"scale={width}:{height}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={width}:{height}:x='(in_w-out_w)*{fx:.6f}':"
            f"y='(in_h-out_h)*{fy:.6f}',"
            f"zoompan=z='{z}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':"
            f"d=1:s={width}x{height}:fps={fps},format=yuv420p")


def overlay_filters(ctas, temp, w):
    filters = []
    for i, item in enumerate(ctas):
        t0, t1 = float(item["start"]), float(item["start"]+item["duration"])
        text_path = temp / f"cta_{i:02d}.txt"
        text_path.write_text(item["text"], encoding="utf-8")
        active = f"between(t\\,{t0:.3f}\\,{t1:.3f})"
        fadein = f"min(1\\,max(0\\,(t-{t0:.3f})/0.22))"
        fadeout = f"min(1\\,max(0\\,({t1:.3f}-t)/0.22))"
        x = f"(w-text_w)/2-20*max(0\\,1-(t-{t0:.3f})/0.25)"
        filters.append("drawbox=x=iw*0.10:y=ih*0.67:w=iw*0.80:h=ih*0.073:"
                       f"color=black@0.28:t=fill:enable='{active}'")
        filters.append("drawtext=font='DejaVu Sans':"
                       f"textfile='{text_path}':fontsize={max(15,int(w*.033))}:"
                       "fontcolor=white:shadowcolor=black@0.6:shadowx=1:shadowy=1:"
                       f"x='{x}':y='h*0.687':alpha='{fadein}*{fadeout}':"
                       f"enable='{active}'")
    return filters


def sha256(file):
    h = hashlib.sha256()
    with file.open("rb") as f:
        for part in iter(lambda:f.read(1024*1024),b""):
            h.update(part)
    return h.hexdigest()


def render(plan_path, dest, workdir, scale):
    plan, info = validate(plan_path)
    check(not dest.exists(), "Destino existente: não sobrescrever entregas")
    c = plan["canvas"]
    w, h = round(c["width"]*scale/2)*2, round(c["height"]*scale/2)*2
    fps = c["fps"]
    check(w >= 120 and h >= 120, "preview-scale pequeno")
    workdir.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix="shortform_",dir=workdir))
    log = temp / "render.log"
    clips = []
    for i, b in enumerate(plan["segments"]):
        part = temp / f"beat_{i:03d}.mp4"
        frames = round((b["end"]-b["start"])*fps)
        check(frames > 0, "Beat sem frames")
        path = src(plan_path.parent, b.get("image") or b.get("video"))
        cmd = ["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y"]
        if b.get("image"):
            cmd += ["-loop","1","-framerate",str(fps),"-i",str(path)]
        else:
            cmd += ["-ss",str(b.get("source_start",0)),"-i",str(path)]
        cmd += ["-an","-vf",motion_filter(w,h,fps,frames,b),"-frames:v",str(frames),
                "-r",str(fps),"-c:v","libx264","-preset","veryfast",
                "-crf","20","-pix_fmt","yuv420p",str(part)]
        shell(cmd, log)
        check(part.stat().st_size > 0, "Beat não renderizado")
        clips.append(part)
    playlist = temp / "concat.txt"
    playlist.write_text("".join("file '"+str(p).replace("'","'\\''")+"'\n" for p in clips))
    joined = temp / "video.mp4"
    shell(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
           "-f","concat","-safe","0","-i",str(playlist),"-c","copy","-an",str(joined)],log)
    dest.parent.mkdir(parents=True,exist_ok=True)
    command = ["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
               "-i",str(joined),"-i",str(src(plan_path.parent, plan["audio"]))]
    if plan.get("music"):
        command += ["-i",str(src(plan_path.parent,plan["music"]))]
    video_filters = overlay_filters(plan.get("cta",[]),temp,w)
    graph = ""
    vmap = "0:v:0"
    amap = "1:a:0"
    if video_filters:
        graph = "[0:v]"+",".join(video_filters)+"[v]"
        vmap = "[v]"
    if plan.get("music"):
        audio_graph = ("[1:a:0]aresample=48000,asetpts=PTS-STARTPTS[a0];"
                       f"[2:a:0]aresample=48000,volume={float(plan.get('music_gain',0.12)):.4f},"
                       f"atrim=0:{info['duration']:.3f},asetpts=PTS-STARTPTS[a1];"
                       "[a0][a1]amix=inputs=2:duration=first:dropout_transition=0[aout]")
        graph = graph + (";" if graph else "") + audio_graph
        amap = "[aout]"
    if graph:
        command += ["-filter_complex",graph]
    command += ["-map",vmap,"-map",amap,"-t",str(info["duration"]),
                "-c:v","libx264","-preset","medium","-crf","20",
                "-pix_fmt","yuv420p","-c:a","aac","-ar","48000","-b:a","192k",
                "-movflags","+faststart",str(dest)]
    shell(command,log)
    check(dest.exists() and dest.stat().st_size > 0, "Saída não gerada")
    shell(["ffmpeg","-nostdin","-v","error","-i",str(dest),"-f","null","-"],log)
    probe = ffprobe(dest)
    streams = probe.get("streams",[])
    video = [x for x in streams if x.get("codec_type")=="video"]
    audio = [x for x in streams if x.get("codec_type")=="audio"]
    check(len(video)==1 and len(audio)==1, "Saída sem vídeo+áudio únicos")
    check(video[0].get("width")==w and video[0].get("height")==h,
          "Dimensões finais diferentes do plano")
    duration = float(probe.get("format",{}).get("duration") or 0)
    check(abs(duration-info["duration"]) <= .2, "Duração final incorreta")
    report = {"status":"technically_validated","render_version":VERSION,
              "output":str(dest),"sha256":sha256(dest),"duration_s":duration,
              "canvas":{"width":w,"height":h,"fps":fps},
              "segments":len(clips),"cta":len(plan.get("cta",[])),"log":str(log),
              "human_review_required":["recorte em movimento", "sincronismo e mix",
                                      "legibilidade móvel do CTA", "ápice e desfecho",
                                      "originalidade e direitos das fontes"]}
    dest.with_suffix(".edit-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest="command",required=True)
    sub.add_parser("validate").add_argument("plan",type=Path)
    rr=sub.add_parser("render")
    rr.add_argument("plan",type=Path)
    rr.add_argument("--output",type=Path,required=True)
    rr.add_argument("--workdir",type=Path,default=Path(".shortform-work"))
    rr.add_argument("--preview-scale",type=float,default=1.)
    args=p.parse_args()
    try:
        plan=args.plan.resolve()
        if args.command=="validate":
            _,r=validate(plan)
            print(json.dumps({"status":"valid",**r},ensure_ascii=False,indent=2))
        else:
            check(numeric(args.preview_scale) and .25<=args.preview_scale<=1.,
                  "preview-scale precisa estar em .25..1")
            print(json.dumps(render(plan,args.output.resolve(),args.workdir.resolve(),
                                    args.preview_scale),ensure_ascii=False,indent=2))
    except (PlanError,ValueError,OSError,KeyError,json.JSONDecodeError) as e:
        print(f"ERROR: {e}",file=sys.stderr)
        return 2
    return 0

if __name__=="__main__":
    raise SystemExit(main())
