#!/usr/bin/env python3
"""Add subtle, narrative-safe CTA motion to a pre-rendered vertical manga master.

Preserves the original audio stream; the video is re-encoded once for overlays.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from shortform_render import (
    ACTIONS, PlanError, cta_filters, digest, probe, require, run
)


def overlay(master: Path, spec: Path, output: Path, workdir: Path) -> dict:
    require(master.is_file(), f"master ausente: {master}")
    require(spec.is_file(), f"plano CTA ausente: {spec}")
    require(not output.exists(), f"não sobrescrever saída existente: {output}")
    media = probe(master)
    v = [s for s in media.get("streams", []) if s.get("codec_type") == "video"]
    a = [s for s in media.get("streams", []) if s.get("codec_type") == "audio"]
    require(len(v)==1 and len(a)==1, "master requer 1 vídeo e 1 áudio")
    width, height = v[0]["width"], v[0]["height"]
    require(height > width, "esperado master vertical já revisado")
    duration = float(media.get("format", {}).get("duration") or 0)
    require(duration > 0, "duração inválida")
    plan = json.loads(spec.read_text(encoding="utf-8"))
    ctas = plan.get("cta",[])
    require(isinstance(ctas,list), "cta deve ser lista")
    require(len(ctas) <= (2 if duration >= 75 else 1),
            "CTA excessivo para duração")
    protected = []
    for interval in plan.get("protected_intervals",[]):
        start,end = interval["start"],interval["end"]
        require(0 <= start < end <= duration, "intervalo protegido inválido")
        protected.append((start,end))
    for ev in ctas:
        start, leng = ev.get("start"), ev.get("duration")
        require(ev.get("action") in ACTIONS,"action inválida")
        require(isinstance(start,(int,float)) and
                isinstance(leng,(int,float)) and start >= 3 and
                1 <= leng <= 2.5 and start+leng <= duration+0.01,
                "CTA fora de tempo")
        require(isinstance(ev.get("text"),str) and
                1 <= len(ev["text"].strip()) <= 56 and
                "\\n" not in ev["text"],"texto CTA inválido")
        require(bool(ev.get("why_now","").strip()),"why_now obrigatório")
        require(not any(start < end_protect and start+leng > st_protect
                        for st_protect,end_protect in protected),
                "CTA invade o clímax/tempo protegido")
    workdir.mkdir(parents=True,exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix="cta_",dir=workdir))
    log = temp/"ffmpeg.log"
    # cta_filters is shared with the standalone renderer.
    ff = cta_filters(plan,width,height,temp,spec.parent)
    require(ff, "sem CTA, preserve o master original sem reencode")
    output.parent.mkdir(parents=True,exist_ok=True)
    cmd = ["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
           "-i",str(master),"-map","0:v:0","-map","0:a:0",
           "-vf",",".join(ff),"-c:v","libx264","-preset","medium",
           "-crf","18","-pix_fmt","yuv420p","-c:a","copy",
           "-movflags","+faststart",str(output)]
    run(cmd,log)
    run(["ffmpeg","-nostdin","-v","error","-i",str(output),
         "-f","null","-"],log)
    actual=probe(output)
    require(any(s.get("codec_type")=="audio" for s in actual["streams"]),
            "áudio desapareceu")
    total=float(actual["format"].get("duration") or 0)
    require(abs(total-duration)<=0.25,"duração divergente")
    result={
        "status":"technically_validated","mode":"cta-over-existing-master",
        "input":str(master),"output":str(output),
        "duration_before_s":duration,"duration_after_s":total,
        "cta_count":len(ctas),"audio_codec_preserved":True,
        "sha256":digest(output),"log":str(log),
        "human_review_pending":["composição visual do CTA","clímax e pausa emocional",
                                "direitos e monetização das fontes"]
    }
    report=output.with_suffix(".motion-report.json")
    report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("master",type=Path)
    p.add_argument("cta_plan",type=Path)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--workdir",type=Path,default=Path(".motion-work"))
    args=p.parse_args()
    try:
        result=overlay(args.master.resolve(),args.cta_plan.resolve(),
                       args.output.resolve(),args.workdir.resolve())
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except (PlanError,ValueError,KeyError,OSError) as exc:
        print(f"ERRO: {exc}",file=__import__("sys").stderr)
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
