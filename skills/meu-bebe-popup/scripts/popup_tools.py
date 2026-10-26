#!/usr/bin/env python3
"""Diagnóstico local e legendas de até duas palavras a partir de alinhamento real."""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import sys


SKILL_ROOT = Path(__file__).resolve().parents[1]


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label}: esperado número em segundos")
    if not math.isfinite(value):
        raise ValueError(f"{label}: número não finito")
    return float(value)


def load_words(path):
    data = read_json(path)
    if not isinstance(data, list) or not data:
        raise ValueError("Alinhamento deve ser uma lista não vazia de palavras")
    result = []
    previous_end = 0.0
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"Palavra {index}: esperado objeto com text, start, end")
        word = item.get("text")
        if not isinstance(word, str) or not word.strip():
            raise ValueError(f"Palavra {index}: texto ausente")
        word = word.strip()
        if re.search(r"\s", word):
            raise ValueError(f"Palavra {index}: cada item deve conter uma só palavra")
        start = number(item.get("start"), f"Palavra {index}.start")
        end = number(item.get("end"), f"Palavra {index}.end")
        if start < 0 or end <= start:
            raise ValueError(f"Palavra {index}: esperado 0 <= start < end")
        if start < previous_end - 1e-6:
            raise ValueError(f"Palavra {index}: sobreposição; revise o alinhamento real")
        result.append({"index": index, "text": word, "start": start, "end": end})
        previous_end = end
    return result


def group_words(words, lead, gap):
    groups = []
    current = []

    def append_group():
        if current:
            groups.append({
                "id": f"caption-{len(groups) + 1:04d}",
                "text": " ".join(w["text"] for w in current),
                "start": current[0]["start"] + lead,
                "end": current[-1]["end"] + lead,
                "words": [{"index": w["index"], "text": w["text"],
                           "start": w["start"] + lead, "end": w["end"] + lead}
                          for w in current],
            })
            current.clear()

    for word in words:
        if current and word["start"] - current[-1]["end"] > gap:
            append_group()
        current.append(word)
        if len(current) == 2 or re.search(r"[.!?…;:][\"'”’)]*$", word["text"]):
            append_group()
    append_group()
    return groups


def milliseconds(value):
    return int(math.floor(value * 1000 + 0.5))


def srt_time(value):
    total = milliseconds(value)
    hours, remain = divmod(total, 3600000)
    minutes, remain = divmod(remain, 60000)
    seconds, millis = divmod(remain, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def make_srt(groups):
    blocks = []
    previous_end = 0
    for index, cue in enumerate(groups, 1):
        start = milliseconds(cue["start"])
        end = milliseconds(cue["end"])
        if end <= start:
            raise ValueError(f"Legenda {index}: intervalo menor que a precisão do SRT")
        if start < previous_end:
            raise ValueError(f"Legenda {index}: sobreposição após converter para milissegundos")
        blocks.append(f"{index}\n{srt_time(cue['start'])} --> {srt_time(cue['end'])}\n{cue['text']}\n")
        previous_end = end
    return "\n".join(blocks)


def captions(args):
    lead = number(args.lead, "lead")
    gap = number(args.gap, "gap")
    if lead < 0 or gap < 0:
        raise ValueError("lead e gap devem ser não negativos")
    words = load_words(args.words)
    duration = None if args.duration is None else number(args.duration, "duration")
    if duration is not None and (duration <= 0 or words[-1]["end"] + lead > duration + 1e-6):
        raise ValueError("As palavras e o lead ultrapassam a duração do filme")
    groups = group_words(words, lead, gap)
    srt = make_srt(groups)
    source = Path(args.words).resolve()
    targets = [Path(args.srt).resolve(), Path(args.cues).resolve()]
    if targets[0] == targets[1] or source in targets:
        raise ValueError("Entrada, SRT e cues devem usar caminhos diferentes")
    for target in targets:
        if target.exists() and not args.force:
            raise ValueError(f"Saída já existe: {target}. Use --force para substituí-la")
    for target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "timebase": "film_seconds",
        "lead_seconds": lead,
        "duration_seconds": duration,
        "source_word_count": len(words),
        "max_words_per_cue": 2,
        "cues": groups,
    }
    targets[0].write_text(srt, encoding="utf-8")
    targets[1].write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    emit({"word_count": len(words), "cue_count": len(groups), "srt": str(targets[0]),
          "cues": str(targets[1]), "timebase": "film_seconds", "lead_applied_once": True})
    return 0


def resolve_library(explicit):
    if explicit:
        return Path(explicit).expanduser().resolve()
    candidates = []
    if os.environ.get("LEMO_OPUSCAR_HOME"):
        candidates.append(Path(os.environ["LEMO_OPUSCAR_HOME"]).expanduser())
    candidates.extend([
        SKILL_ROOT.parent / "lemo-opuscar" / "library",
        Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "skills" / "lemo-opuscar" / "library",
        Path.home() / "lemo-opuscar",
    ])
    for candidate in candidates:
        if (candidate / "core" / "render" / "video.mjs").is_file():
            return candidate.resolve()
    return None


def doctor(args):
    tools = {name: shutil.which(name) for name in ("node", "ffmpeg", "ffprobe")}
    tokens = read_json(SKILL_ROOT / "assets" / "brand-tokens.json")
    board = SKILL_ROOT / "assets" / tokens["reference_board"]["file"]
    board_ok = (board.is_file() and hashlib.sha256(board.read_bytes()).hexdigest()
                == tokens["reference_board"]["sha256"])
    library = resolve_library(args.library)
    markers = ["core/render/video.mjs", "core/render/still.mjs", "core/render/events.mjs",
               "styles/paper-popup/STYLE.md", "node_modules/three/package.json",
               "node_modules/playwright-core/package.json"]
    files = {marker: bool(library and (library / marker).is_file()) for marker in markers}
    missing = [f"ferramenta:{name}" for name, path in tools.items() if not path]
    missing += [f"biblioteca:{marker}" for marker, exists in files.items() if not exists]
    if not board_ok:
        missing.append("prancha:ausente_ou_hash_divergente")
    emit({
        "python": sys.executable,
        "tools": tools,
        "library": str(library) if library else None,
        "library_files": files,
        "family_board_sha256_ok": board_ok,
        "demo_source_present": bool(library and (library / "styles/paper-popup/demo").is_dir()),
        "missing": missing,
        "render_readiness": "not_exercised",
        "note": "Não instala dependências nem comprova navegador, WebGL, fontes, voz ou SFX. Teste um quadro real antes do render.",
    })
    return 1 if missing else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    doc = commands.add_parser("doctor", help="Inspeciona ferramentas, biblioteca e prancha, sem instalar")
    doc.add_argument("--library", help="Caminho explícito da biblioteca Lemo-Opuscar")
    doc.set_defaults(handler=doctor)
    cap = commands.add_parser("captions", help="Agrupa alinhamento real em legendas de uma ou duas palavras")
    cap.add_argument("words", help="JSON [{text,start,end}] em segundos relativos à voz")
    cap.add_argument("--lead", type=float, default=1.0, help="Offset da voz no filme; padrão 1 s")
    cap.add_argument("--gap", type=float, default=0.3, help="Pausa máxima dentro de um grupo; padrão 0,3 s")
    cap.add_argument("--duration", type=float, help="Duração total real do filme para validar limites")
    cap.add_argument("--srt", required=True, help="Caminho de saída .srt")
    cap.add_argument("--cues", required=True, help="Caminho JSON para o HUD; tempos já incluem lead")
    cap.add_argument("--force", action="store_true", help="Substitui arquivos de saída existentes")
    cap.set_defaults(handler=captions)
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        emit({"error": str(exc)})
        return 2


if __name__ == "__main__":
    sys.exit(main())
