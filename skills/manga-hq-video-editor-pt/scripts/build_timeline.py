#!/usr/bin/env python3
"""Build a checked, frame-contiguous timeline from reviewed comic evidence.

Python 3.11+ and FFprobe. This helper does not transcribe or force-align audio.
Confirmed beat timestamps create a renderable plan. Word-count estimates create
only a draft, explicitly rejected for final rendering by the companion renderer.
Paths in manifests resolve against --image-root or the manifest directory; media
paths in the generated plan resolve against that plan's directory. --analysis
accepts the reviewed handoff from the story skill, including embedded evidence
and a portable image_root; it requires no duplicate manifest/script files.
"""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys

AD_SECTION_KINDS = {"advertisement", "ad", "sponsor", "sponsorship", "commercial", "promotion"}


class TimelineError(ValueError):
    """The media, evidence, review or synchronization contract is incomplete."""


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise TimelineError(f"JSON não pode ser lido: {path}: {exc}") from exc


def finite(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise TimelineError(f"{label}: número finito obrigatório.")
    return float(value)


def valid_id(value, label):
    if not isinstance(value, str) or not value.strip():
        raise TimelineError(f"{label}: ID não vazio obrigatório.")
    return value


def checked_production_structure(script):
    """Validate optional production metadata without creating timed segments."""
    beats = script.get("beats", [])
    beats = beats if isinstance(beats, list) else []
    beat_map = {beat["id"]: beat for beat in beats
                if isinstance(beat, dict) and isinstance(beat.get("id"), str)}
    if "production_structure" not in script:
        if any(isinstance(beat, dict) and "section_id" in beat for beat in beats):
            raise TimelineError("section_id exige production_structure com sections.")
        return
    structure = script["production_structure"]
    if not isinstance(structure, dict) or not isinstance(structure.get("sections"), list):
        raise TimelineError("production_structure deve ser objeto com sections como lista.")
    section_map, memberships = {}, {}
    for section in structure["sections"]:
        if not isinstance(section, dict):
            raise TimelineError("production_structure: seção deve ser objeto.")
        sid = valid_id(section.get("id"), "production_structure seção")
        if sid in section_map:
            raise TimelineError(f"production_structure: ID de seção duplicado: {sid}.")
        section_map[sid] = section
        kind = section.get("kind")
        if not isinstance(kind, str) or not kind.strip():
            raise TimelineError(f"{sid}: kind deve ser texto não vazio.")
        if kind.strip().casefold() in AD_SECTION_KINDS:
            raise TimelineError(f"{sid}: seção de publicidade não permitida nesta produção sem anúncios.")
        if "goal" in section and not isinstance(section["goal"], str):
            raise TimelineError(f"{sid}: goal deve ser texto.")
        if "beats" in section:
            refs = section["beats"]
            if not isinstance(refs, list):
                raise TimelineError(f"{sid}: beats deve ser lista de IDs.")
            for bid in refs:
                if not isinstance(bid, str) or bid not in beat_map:
                    raise TimelineError(f"{sid}: beats referencia ID inexistente.")
                if bid in memberships:
                    raise TimelineError(f"{sid}: beat associado a mais de uma seção ou duplicado: {bid}.")
                memberships[bid] = sid
    for bid, beat in beat_map.items():
        if "section_id" not in beat:
            continue
        sid = beat["section_id"]
        if not isinstance(sid, str) or sid not in section_map:
            raise TimelineError(f"{bid}: section_id deve referenciar uma seção existente.")
        section = section_map[sid]
        if ((bid in memberships and memberships[bid] != sid)
                or (isinstance(section.get("beats"), list) and bid not in section["beats"])):
            raise TimelineError(f"{bid}: section_id diverge dos beats declarados na seção.")


def bbox(box, label):
    if not isinstance(box, list) or len(box) != 4:
        raise TimelineError(f"{label}: bbox deve ser [x1,y1,x2,y2] normalizada.")
    x1, y1, x2, y2 = [finite(v, label) for v in box]
    if not (0 <= x1 < x2 <= 1 and 0 <= y1 < y2 <= 1):
        raise TimelineError(f"{label}: bbox deve satisfazer 0≤x1<x2≤1 e 0≤y1<y2≤1.")
    return [x1, y1, x2, y2]


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def semantic_sha256(value):
    """Hash embedded source objects independently of JSON file formatting."""
    try:
        data = json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise TimelineError(f"Objeto não possui representação JSON canônica: {exc}") from exc
    return hashlib.sha256(data).hexdigest()


def fps_value(value):
    if isinstance(value, bool):
        raise TimelineError("FPS inválido.")
    try:
        fps = Fraction(str(value))
    except (ValueError, ZeroDivisionError):
        raise TimelineError("FPS deve ser número ou fração, como 30000/1001.")
    if not 1 <= fps <= 120:
        raise TimelineError("FPS deve estar entre 1 e 120.")
    return fps


def relative_media(path, plan_dir):
    # Windows cannot express a relative path between two volumes.
    try:
        return Path(os.path.relpath(path, plan_dir)).as_posix()
    except ValueError:
        return str(Path(path).resolve())


def probe_audio(path, stream_index=None):
    path = Path(path).resolve()
    if not path.is_file():
        raise TimelineError(f"Áudio inexistente: {path}")
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
            check=True, capture_output=True, text=True, encoding="utf-8", timeout=60)
        data = json.loads(result.stdout)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        raise TimelineError(f"FFprobe não verificou o áudio: {exc}") from exc
    streams = [s for s in data.get("streams", []) if s.get("codec_type") == "audio"]
    if not streams:
        raise TimelineError("Arquivo não possui faixa de áudio.")
    if stream_index is None:
        if len(streams) != 1:
            raise TimelineError("Há várias faixas; use --audio-stream com o índice absoluto da faixa correta.")
        stream = streams[0]
    else:
        if isinstance(stream_index, bool) or not isinstance(stream_index, int) or stream_index < 0:
            raise TimelineError("audio_stream deve ser índice absoluto inteiro não negativo.")
        stream = next((s for s in streams if s.get("index") == stream_index), None)
        if stream is None:
            raise TimelineError("Índice selecionado não corresponde a uma faixa de áudio.")
    raw_duration = stream.get("duration", data.get("format", {}).get("duration"))
    try:
        duration = float(raw_duration)
    except (TypeError, ValueError):
        raise TimelineError("Duração da faixa de áudio indisponível; forneça um áudio com duração verificável.")
    if not math.isfinite(duration) or duration <= 0:
        raise TimelineError("Duração da faixa de áudio inválida.")
    try:
        start_time = float(stream.get("start_time", 0))
    except (TypeError, ValueError):
        start_time = 0
    if not math.isfinite(start_time) or abs(start_time) > 0.1:
        raise TimelineError("Faixa tem timestamp inicial deslocado; normalize uma cópia local antes de alinhar.")
    return {"stream_index": stream["index"], "duration_seconds": duration,
            "sample_rate": stream.get("sample_rate"), "channels": stream.get("channels"),
            "sha256": sha256(path)}


def checked_evidence(manifest, script, image_root):
    for label, value in (("manifesto", manifest), ("roteiro", script)):
        if not isinstance(value, dict) or value.get("schema_version") != 1 or isinstance(value.get("schema_version"), bool):
            raise TimelineError(f"{label}: schema_version deve ser 1.")
    if manifest.get("reading_direction") != script.get("reading_direction"):
        raise TimelineError("Direções de leitura divergem entre manifesto e roteiro.")
    pages = manifest.get("pages")
    beats = script.get("beats")
    if not isinstance(pages, list) or not pages or not isinstance(beats, list) or not beats:
        raise TimelineError("Manifesto deve conter pages e roteiro deve conter beats não vazios.")
    checked_production_structure(script)
    page_map, panel_map = {}, {}
    for page in pages:
        if not isinstance(page, dict):
            raise TimelineError("Página deve ser objeto.")
        pid = valid_id(page.get("id"), "Página")
        if pid in page_map:
            raise TimelineError(f"ID de página duplicado: {pid}.")
        page_map[pid] = page
        panels = page.get("panels")
        if not isinstance(panels, list):
            raise TimelineError(f"{pid}: panels deve ser lista.")
        for panel in panels:
            if not isinstance(panel, dict):
                raise TimelineError(f"{pid}: painel deve ser objeto.")
            qid = valid_id(panel.get("id"), f"{pid} painel")
            key = (pid, qid)
            if key in panel_map:
                raise TimelineError(f"ID de painel duplicado: {pid}/{qid}.")
            bbox(panel.get("bbox"), f"{pid}/{qid}")
            panel_map[key] = panel
    result, seen, verified_files = [], set(), {}
    for beat in beats:
        if not isinstance(beat, dict):
            raise TimelineError("Beat deve ser objeto.")
        bid = valid_id(beat.get("id"), "Beat")
        if bid in seen:
            raise TimelineError(f"ID de beat duplicado: {bid}.")
        seen.add(bid)
        if not isinstance(beat.get("narration"), str) or not beat["narration"].strip():
            raise TimelineError(f"{bid}: narration não vazia obrigatória.")
        pid, qid = beat.get("page_id"), beat.get("panel_id")
        if not isinstance(pid, str) or pid not in page_map:
            raise TimelineError(f"{bid}: page_id inexistente.")
        page = page_map[pid]
        if page.get("status") != "narrative" or page.get("reviewed") is not True:
            raise TimelineError(f"{bid}: página deve ser narrative e reviewed=true; não narre anúncios/capas sem classificação.")
        if not isinstance(qid, str) or (pid, qid) not in panel_map:
            raise TimelineError(f"{bid}: panel_id inexistente nessa página.")
        panel = panel_map[(pid, qid)]
        box = bbox(panel["bbox"], bid)
        if "bbox" in beat and bbox(beat["bbox"], bid) != box:
            raise TimelineError(f"{bid}: bbox do beat diverge do manifesto.")
        if beat.get("legibility_reviewed") is not True and panel.get("legibility_reviewed") is not True:
            raise TimelineError(f"{bid}: reveja o recorte e o movimento e marque legibility_reviewed=true.")
        value = page.get("file")
        if not isinstance(value, str) or not value.strip():
            raise TimelineError(f"{pid}: caminho de imagem obrigatório.")
        path = (image_root / value).resolve()
        if not path.is_relative_to(image_root):
            raise TimelineError(f"{pid}: imagem sai do image_root; use caminho relativo ao diretório informado.")
        if not path.is_file():
            raise TimelineError(f"{pid}: imagem inexistente: {path}")
        if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}:
            raise TimelineError(f"{pid}: formato de imagem não suportado.")
        if path not in verified_files:
            verified_files[path] = sha256(path)
        if page.get("sha256") and page["sha256"] != verified_files[path]:
            raise TimelineError(f"{pid}: imagem mudou desde o manifesto (checksum diferente).")
        result.append({"beat": beat, "image": path, "image_sha256": verified_files[path], "bbox": box})
    return result


def alignment_frames(alignment, beat_ids, duration, fps, confirm=False):
    """Validate measured/manual beat marks; no transcription inference occurs."""
    total_frames = max(1, math.ceil(duration * float(fps) - 1e-9))
    if isinstance(alignment, dict):
        if alignment.get("schema_version") != 1 or isinstance(alignment.get("schema_version"), bool):
            raise TimelineError("Alinhamento deve usar schema_version=1.")
        if alignment.get("method") not in {"manual", "reviewed-asr"}:
            raise TimelineError("method deve ser manual ou reviewed-asr; ASR precisa revisão dos limites por beat.")
        rows = alignment.get("beats")
        confirmed = alignment.get("confirmed") is True or confirm
        method = alignment["method"]
    elif isinstance(alignment, list):
        rows, confirmed, method = alignment, confirm, "manual"
    else:
        raise TimelineError("Alinhamento deve ser objeto com beats ou lista de marcas.")
    if not confirmed:
        raise TimelineError("Alinhamento não confirmado. Revise marcas e use confirmed=true ou --confirm-alignment; estimativas só permitem --draft.")
    if not isinstance(rows, list) or len(rows) != len(beat_ids):
        raise TimelineError("Alinhamento deve conter exatamente uma marca para cada beat.")
    boundaries, previous_raw_end = [], None
    rate, frame_seconds = float(fps), 1 / float(fps)
    for i, (row, bid) in enumerate(zip(rows, beat_ids)):
        if not isinstance(row, dict) or row.get("id") != bid:
            raise TimelineError("IDs/ordem de marcas divergem dos beats do roteiro.")
        start = finite(row.get("start"), f"{bid} start")
        end = finite(row.get("end"), f"{bid} end")
        if start < 0 or end <= start:
            raise TimelineError(f"{bid}: intervalo deve ser positivo e começar em tempo não negativo.")
        sf, ef = round(start * rate), round(end * rate)
        if i == 0 and sf != 0:
            raise TimelineError("Alinhamento deve começar no frame 0, incluindo eventual silêncio inicial.")
        if previous_raw_end is not None and (sf != boundaries[-1][1] or abs(start-previous_raw_end) > frame_seconds + 1e-8):
            raise TimelineError(f"{bid}: alinhamento contém lacuna ou sobreposição entre beats.")
        if i == len(rows)-1:
            if abs(end-duration) > frame_seconds + 1e-8:
                raise TimelineError("Última marca deve alcançar a duração real do áudio, incluindo silêncio final, com tolerância de um frame.")
            ef = total_frames
        if ef <= sf:
            raise TimelineError(f"{bid}: beat ficou sem frames após quantização.")
        if sf >= total_frames or ef > total_frames:
            raise TimelineError(f"{bid}: marca fora da duração do áudio.")
        boundaries.append((sf, ef))
        previous_raw_end = end
    return boundaries, total_frames, method


def draft_frames(beats, duration, fps):
    """Word-count weights are rough estimates; never claim synchronization."""
    total = max(1, math.ceil(duration*float(fps)-1e-9))
    if total < len(beats):
        raise TimelineError("Áudio possui menos frames que beats.")
    weights = [max(1, len(re.findall(r"\w+", b["narration"]))) for b in beats]
    remaining = total-len(beats)
    allocations = [1+(remaining*w)//sum(weights) for w in weights]
    for i in range(total-sum(allocations)):
        allocations[i % len(allocations)] += 1
    cursor, rows = 0, []
    for frames in allocations:
        rows.append((cursor, cursor+frames))
        cursor += frames
    return rows, total


def _build_plan(manifest, script, audio_path, output_path, *, images, sources,
                source_paths=(), alignment_path=None, confirm_alignment=False,
                draft=False, audio_stream=None, fps="30000/1001", width=1920,
                height=1080):
    audio_path, output_path = [Path(p).resolve() for p in (audio_path, output_path)]
    protected = {audio_path, *(Path(p).resolve() for p in source_paths)}
    if alignment_path is not None:
        protected.add(Path(alignment_path).resolve())
    if output_path in protected or output_path.exists():
        raise TimelineError("Saída já existe ou coincide com uma fonte; escolha arquivo novo.")
    rate = fps_value(fps)
    for label, value in (("width", width), ("height", height)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 2 or value % 2:
            raise TimelineError(f"{label}: dimensão deve ser inteiro positivo par.")
    images = Path(images).resolve()
    if not images.is_dir():
        raise TimelineError("image_root inexistente.")
    evidence = checked_evidence(manifest, script, images)
    if any(output_path == item["image"] for item in evidence):
        raise TimelineError("Saída coincide com imagem de origem.")
    audio = probe_audio(audio_path, audio_stream)
    if alignment_path is not None:
        boundaries, frames, method = alignment_frames(load_json(alignment_path), [b["beat"]["id"] for b in evidence], audio["duration_seconds"], rate, confirm_alignment)
    elif draft:
        boundaries, frames = draft_frames([b["beat"] for b in evidence], audio["duration_seconds"], rate)
        method = "estimated-word-count"
    else:
        raise TimelineError("Forneça --alignment confirmado ou --draft para estimativa não renderizável.")
    # Even a supplied alignment does not promote an explicitly requested draft.
    ready = not draft and method != "estimated-word-count"
    planned = []
    for i, (item, (sf, ef)) in enumerate(zip(evidence, boundaries)):
        beat = item["beat"]
        duration = (ef-sf)/float(rate)
        motion = beat.get("motion", {"from_scale": 1 if i%2 == 0 else 1.8, "to_scale": 1.8 if i%2 == 0 else 1})
        if not isinstance(motion, dict):
            raise TimelineError(f"{beat['id']}: motion deve ser objeto.")
        motion = {key: finite(motion.get(key), f"{beat['id']} {key}") for key in ("from_scale", "to_scale")}
        if any(not 1 <= value <= 2.5 for value in motion.values()):
            raise TimelineError(f"{beat['id']}: escalas devem estar entre 1 e 2.5, sobre contain-fit.")
        transition = finite(beat.get("transition_seconds", min(.4, duration/4)), f"{beat['id']} transition_seconds")
        if not 0 <= transition <= min(1, duration/2):
            raise TimelineError(f"{beat['id']}: fade deve estar entre 0 e min(1s,duração/2).")
        color = beat.get("color_mode", "manga_cyan")
        if color not in {"manga_cyan", "original"}:
            raise TimelineError(f"{beat['id']}: color_mode inválido.")
        row = {"id": beat["id"], "start": sf/float(rate), "end": ef/float(rate),
               "start_frame": sf, "end_frame": ef,
               "image": relative_media(item["image"], output_path.parent),
               "image_sha256": item["image_sha256"], "page_id": beat["page_id"], "panel_id": beat["panel_id"],
               "bbox": item["bbox"], "motion": motion, "transition_seconds": transition,
               "color_mode": color, "legibility_reviewed": True}
        if "section_id" in beat:
            row["section_id"] = beat["section_id"]
        if "focal_point" in beat:
            focal = beat["focal_point"]
            if not isinstance(focal, list) or len(focal) != 2 or any(not 0 <= finite(v, "focal_point") <= 1 for v in focal):
                raise TimelineError(f"{beat['id']}: focal_point deve ser [x,y] normalizado ao recorte.")
            row["focal_point"] = focal
        planned.append(row)
    plan = {"schema_version": 1, "readiness": "ready" if ready else "draft", "renderable": ready,
            "canvas": {"width": width, "height": height, "fps": str(rate)},
            "profile": "manga-blue-longform-v1", "duration_seconds": frames/float(rate), "total_frames": frames,
            "audio": {"file": relative_media(audio_path, output_path.parent), **audio},
            "alignment": {"method": method, "confirmed": method != "estimated-word-count", "frame_quantized": True,
                          "precision_claim": "reviewed beat intervals; no forced alignment performed by this helper"},
            "sources": sources,
            "beats": planned,
            "limitations": (["Tempos por peso de palavras são estimativas; revise contra o áudio e crie alignment confirmado antes de master."] if not ready else ["Revisão declarada das marcas/recortes não substitui conferir o preview, sincronismo perceptivo e conteúdo."])}
    if "production_structure" in script:
        plan["production_structure"] = copy.deepcopy(script["production_structure"])
        plan["limitations"].append("production_structure preserva o plano de gancho/intro/desenvolvimento/encerramento; módulos sem beats exigem composição posterior e não foram renderizados por este helper.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation preserves source data and previous deliverables.
    with output_path.open("x", encoding="utf-8") as handle:
        json.dump(plan, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return plan


def build_plan(manifest_path, script_path, audio_path, output_path, *, alignment_path=None,
               confirm_alignment=False, draft=False, image_root=None, audio_stream=None,
               fps="30000/1001", width=1920, height=1080):
    """Original manifest/script API retained for existing projects."""
    manifest_path, script_path = [Path(p).resolve() for p in (manifest_path, script_path)]
    return _build_plan(load_json(manifest_path), load_json(script_path), audio_path,
                       output_path, images=Path(image_root).resolve() if image_root else manifest_path.parent,
                       sources={"manifest_sha256": sha256(manifest_path),
                                "script_sha256": sha256(script_path)},
                       source_paths=(manifest_path, script_path), alignment_path=alignment_path,
                       confirm_alignment=confirm_alignment, draft=draft,
                       audio_stream=audio_stream, fps=fps, width=width, height=height)


def checked_analysis(analysis):
    """Verify that the handoff index still describes its embedded evidence."""
    if (not isinstance(analysis, dict) or analysis.get("schema_version") != 1
            or isinstance(analysis.get("schema_version"), bool)
            or analysis.get("kind") != "manga-hq-editing-analysis"):
        raise TimelineError("Análise deve usar schema_version=1 e kind=manga-hq-editing-analysis.")
    manifest, script = analysis.get("manifest"), analysis.get("script")
    if not isinstance(manifest, dict) or not isinstance(script, dict):
        raise TimelineError("Análise deve conter manifesto e roteiro embutidos como objetos.")
    fingerprints = analysis.get("source_fingerprints")
    if not isinstance(fingerprints, dict):
        raise TimelineError("Análise deve conter source_fingerprints.")
    hashes = {}
    for name, value in (("manifest", manifest), ("script", script)):
        expected = fingerprints.get(f"{name}_sha256")
        actual = semantic_sha256(value)
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected) or expected != actual:
            raise TimelineError(f"Análise desatualizada: fingerprint do {name} diverge do objeto embutido.")
        hashes[f"{name}_semantic_sha256"] = actual
    checked_production_structure(script)
    if ("production_structure" in script or "production_structure" in analysis):
        if analysis.get("production_structure") != script.get("production_structure"):
            raise TimelineError("production_structure da análise diverge do roteiro embutido.")
    pages, beats = manifest.get("pages"), script.get("beats")
    if not isinstance(pages, list) or not isinstance(beats, list) or not pages or not beats:
        raise TimelineError("Análise deve conter pages e beats não vazios.")
    page_map, panel_map, beat_map = {}, {}, {}
    for page in pages:
        if not isinstance(page, dict):
            raise TimelineError("Página embutida deve ser objeto.")
        pid = valid_id(page.get("id"), "Página")
        if pid in page_map:
            raise TimelineError(f"ID de página duplicado: {pid}.")
        page_map[pid] = page
        panels = page.get("panels")
        if not isinstance(panels, list):
            raise TimelineError(f"{pid}: panels deve ser lista.")
        for panel in panels:
            if not isinstance(panel, dict):
                raise TimelineError(f"{pid}: painel deve ser objeto.")
            qid = valid_id(panel.get("id"), f"{pid} painel")
            if (pid, qid) in panel_map:
                raise TimelineError(f"ID de painel duplicado: {pid}/{qid}.")
            panel_map[(pid, qid)] = panel
    for beat in beats:
        if not isinstance(beat, dict):
            raise TimelineError("Beat embutido deve ser objeto.")
        bid = valid_id(beat.get("id"), "Beat")
        if bid in beat_map:
            raise TimelineError(f"ID de beat duplicado: {bid}.")
        beat_map[bid] = beat
    catalog, shots = analysis.get("image_catalog"), analysis.get("shots")
    if not isinstance(catalog, list):
        raise TimelineError("Análise deve conter image_catalog como lista.")
    if not isinstance(shots, list) or len(shots) != len(beats):
        raise TimelineError("Análise deve conter exatamente um shot por beat do roteiro.")
    seen = set()
    for shot in shots:
        if not isinstance(shot, dict):
            raise TimelineError("Shot da análise deve ser objeto.")
        bid = valid_id(shot.get("beat_id"), "Shot beat_id")
        if bid in seen:
            raise TimelineError(f"Shot duplicado para beat: {bid}.")
        seen.add(bid)
        if bid not in beat_map:
            raise TimelineError(f"Shot referencia beat inexistente: {bid}.")
        beat = beat_map[bid]
        pid, qid = beat.get("page_id"), beat.get("panel_id")
        if not isinstance(pid, str) or pid not in page_map or not isinstance(qid, str) or (pid, qid) not in panel_map:
            raise TimelineError(f"{bid}: referência de página/painel inexistente.")
        expected = {"page_id": pid, "panel_id": qid, "narration": beat.get("narration"),
                    "file": page_map[pid].get("file"), "bbox": bbox(panel_map[(pid, qid)].get("bbox"), bid)}
        if "section_id" in beat or "section_id" in shot:
            expected["section_id"] = beat.get("section_id")
        for field, value in expected.items():
            candidate = bbox(shot.get(field), bid) if field == "bbox" else shot.get(field)
            if candidate != value:
                raise TimelineError(f"{bid}: shot {field} diverge do manifesto/roteiro embutido.")
    # Search descriptions/tags are advisory. Rendering follows confirmed IDs and
    # embedded evidence, never a semantic guess from the catalog.
    return manifest, script, hashes


def build_from_analysis(analysis_path, audio_path, output_path, *, alignment_path=None,
                        confirm_alignment=False, draft=False, image_root=None,
                        audio_stream=None, fps="30000/1001", width=1920, height=1080,
                        confirm_legibility=False):
    analysis_path = Path(analysis_path).resolve()
    analysis = load_json(analysis_path)
    manifest, script, hashes = checked_analysis(analysis)
    sources = {"analysis_sha256": sha256(analysis_path), **hashes}
    if confirm_legibility:
        # This declares an actual editorial review of crops and planned motion;
        # it does not change the source or imply confirmed audio timestamps.
        script = copy.deepcopy(script)
        for beat in script["beats"]:
            beat["legibility_reviewed"] = True
        sources["legibility_confirmation"] = "declared-after-editorial-review"
        sources["effective_script_semantic_sha256"] = semantic_sha256(script)
    if image_root is not None:
        images = Path(image_root).resolve()
    else:
        root_hint = analysis.get("image_root")
        if not isinstance(root_hint, str) or not root_hint.strip():
            raise TimelineError("Análise sem image_root; informe --image-root com a pasta de imagens.")
        images = (analysis_path.parent / root_hint).resolve()
    return _build_plan(manifest, script, audio_path, output_path, images=images,
                       sources=sources,
                       source_paths=(analysis_path,), alignment_path=alignment_path,
                       confirm_alignment=confirm_alignment, draft=draft,
                       audio_stream=audio_stream, fps=fps, width=width, height=height)


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--manifest", type=Path)
    source.add_argument("--analysis", type=Path)
    parser.add_argument("--script", type=Path)
    parser.add_argument("--audio", type=Path, required=True)
    parser.add_argument("--alignment", type=Path)
    parser.add_argument("--confirm-alignment", action="store_true")
    parser.add_argument("--confirm-legibility", action="store_true",
                        help="Com --analysis, declara revisão real dos recortes e movimentos; não confirma sincronismo.")
    parser.add_argument("--draft", action="store_true")
    parser.add_argument("--image-root", type=Path)
    parser.add_argument("--audio-stream", type=int)
    parser.add_argument("--fps", default="30000/1001")
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.analysis is not None and args.script is not None:
        parser.error("--analysis substitui --manifest e --script; não combine essas entradas.")
    if args.manifest is not None and args.script is None:
        parser.error("--manifest exige --script.")
    if args.confirm_legibility and args.analysis is None:
        parser.error("--confirm-legibility exige --analysis.")
    try:
        options = {"alignment_path": args.alignment, "confirm_alignment": args.confirm_alignment,
                   "draft": args.draft, "image_root": args.image_root,
                   "audio_stream": args.audio_stream, "fps": args.fps,
                   "width": args.width, "height": args.height}
        if args.analysis is not None:
            plan = build_from_analysis(args.analysis, args.audio, args.output,
                                       confirm_legibility=args.confirm_legibility, **options)
        else:
            plan = build_plan(args.manifest, args.script, args.audio, args.output, **options)
    except (TimelineError, OSError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"status": plan["readiness"], "renderable": plan["renderable"],
                      "beats": len(plan["beats"]), "frames": plan["total_frames"], "output": str(args.output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
