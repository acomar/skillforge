#!/usr/bin/env python3
"""Apply quiet CTA motion to an existing vertical master, retaining audio codec.

This is the bridge to the installed manga-hq-video-editor-pt advanced render.
Requires only Python>=3.11 and FFmpeg; no TTS, ASR, automatic CTA placement.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import tempfile
from pathlib import Path

from shortform_render import PlanError, check, ffprobe, numeric, overlay_filters, sha256, shell


def overlay(master:Path, specification:Path, output:Path, workdir:Path):
    check(master.is_file(), f"Master não encontrado: {master}")
    check(specification.is_file(), f"Plano não encontrado: {specification}")
    check(not output.exists(), f"Saída existente, não sobrescrever: {output}")
    meta=ffprobe(master)
    videos=[s for s in meta.get('streams',[]) if s.get('codec_type')=='video']
    audios=[s for s in meta.get('streams',[]) if s.get('codec_type')=='audio']
    check(len(videos)==1 and len(audios)==1,'Master precisa ter 1 faixa de vídeo e 1 de áudio')
    width,height=videos[0]['width'],videos[0]['height']
    check(height>width,'Master precisa ser vertical; reenquadre com o editor primeiro')
    total=float(meta.get('format',{}).get('duration') or 0)
    check(total>0,'Duração do master inválida')
    p=json.loads(specification.read_text(encoding='utf-8'))
    ctas=p.get('cta',[])
    check(isinstance(ctas,list) and ctas,'Nenhum CTA: melhor usar o master sem re-encoding')
    check(len(ctas)<= (2 if total>=75 else 1),'CTA demais para o vídeo')
    protected=[]
    for beat in p.get('segments',[]):
        if beat.get('protected'):
            a,b=beat.get('start'),beat.get('end')
            check(numeric(a) and numeric(b) and 0<=a<b<=total+0.02,
                  'Beat protegido com tempos inválidos')
            protected.append((a,b))
    for interval in p.get('protected_intervals',[]):
        a,b=interval.get('start'),interval.get('end')
        check(numeric(a) and numeric(b) and 0<=a<b<=total+0.02,
              'Intervalo protegido inválido')
        protected.append((a,b))
    for event in ctas:
        a,d=event.get('start'),event.get('duration')
        check(event.get('action') in {'follow','like','comment'},'Ação de CTA inválida')
        text=event.get('text')
        check(isinstance(text,str) and 1<=len(text.strip())<=56 and
              '\n' not in text and '\r' not in text,'Texto de CTA inválido')
        check(isinstance(event.get('why_now'),str) and event['why_now'].strip(),
              'CTA sem justificativa narrativa')
        check(numeric(a) and numeric(d) and a>=3 and 1<=d<=2.5 and a+d<=total+0.01,
              'CTA fora da janela temporal')
        check(not any(a<b-0.0001 and a+d>x+0.0001 for x,b in protected),
              'CTA sobrepõe intervalo emocional protegido')
    workdir.mkdir(parents=True,exist_ok=True)
    temp=Path(tempfile.mkdtemp(prefix='motion_',dir=workdir))
    logfile=temp/'ffmpeg.log'
    filters=overlay_filters(ctas,temp,width)
    output.parent.mkdir(parents=True,exist_ok=True)
    cmd=['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y',
         '-i',str(master),'-map','0:v:0','-map','0:a:0',
         '-vf',','.join(filters),'-c:v','libx264','-preset','medium',
         '-crf','19','-pix_fmt','yuv420p','-c:a','copy',
         '-movflags','+faststart',str(output)]
    shell(cmd,logfile)
    shell(['ffmpeg','-nostdin','-v','error','-i',str(output),'-f','null','-'],logfile)
    actual=ffprobe(output)
    audios_after=[s for s in actual.get('streams',[]) if s.get('codec_type')=='audio']
    video_after=[s for s in actual.get('streams',[]) if s.get('codec_type')=='video']
    check(len(audios_after)==1 and len(video_after)==1,'Faixa desapareceu na saída')
    actual_total=float(actual['format'].get('duration') or 0)
    check(abs(actual_total-total)<=0.25,'Duração divergente após CTA')
    check(video_after[0]['width']==width and video_after[0]['height']==height,
          'Tamanho alterado após overlay')
    check(audios_after[0].get('codec_name')==audios[0].get('codec_name'),
          'Codec de áudio foi alterado')
    result={'status':'technically_validated','mode':'cta-over-existing-master',
            'input':str(master),'output':str(output),
            'duration_before_s':total,'duration_after_s':actual_total,
            'cta_count':len(ctas),'audio_codec_preserved':True,
            'sha256':sha256(output),'log':str(logfile),
            'human_review_required':['legibilidade do CTA','percepção do clímax',
                                     'originalidade e direitos','revisão no celular']}
    output.with_suffix('.motion-report.json').write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('master',type=Path)
    cli.add_argument('cta_plan',type=Path)
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--workdir',type=Path,default=Path('.motion-work'))
    args=cli.parse_args()
    try:
        result=overlay(args.master.resolve(),args.cta_plan.resolve(),
                       args.output.resolve(),args.workdir.resolve())
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except (PlanError,ValueError,KeyError,OSError,json.JSONDecodeError) as e:
        print(f'ERROR: {e}',file=sys.stderr)
        return 2
    return 0

if __name__=='__main__':
    raise SystemExit(main())
