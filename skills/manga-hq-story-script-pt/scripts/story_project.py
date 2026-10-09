#!/usr/bin/env python3
"""Inventory image pages and validate an evidence-linked, human-reviewed script.

Python standard library is sufficient for JPG/PNG/GIF/BMP dimensions. Pillow,
then ffprobe, are optional fallbacks for other image formats. This program does
not read panels, infer a plot, classify advertisements, or generate narration.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import struct
import subprocess
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import quote

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tif", ".tiff"}
STATUSES = {"narrative", "cover", "advertisement", "editorial"}
DIRECTIONS = {"left-to-right", "right-to-left"}
AD_SECTION_KINDS = {"advertisement", "ad", "sponsor", "sponsorship", "commercial", "promotion"}


class ProjectError(ValueError):
    """An input or project contract could not be verified."""


def natural_key(value: str):
    # Tagged components avoid comparing ints with strings for mixed names.
    return [(1, int(part)) if part.isdigit() else (0, part.casefold())
            for part in re.split(r"(\d+)", value)]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def image_size(path: Path):
    """Read actual image headers, not dimensions guessed from a filename."""
    with path.open("rb") as stream:
        header = stream.read(32)
        if len(header) >= 24 and header.startswith(b"\x89PNG\r\n\x1a\n") and header[12:16] == b"IHDR":
            return struct.unpack(">II", header[16:24])
        if len(header) >= 10 and header[:6] in {b"GIF87a", b"GIF89a"}:
            return struct.unpack("<HH", header[6:10])
        if header[:2] == b"BM" and len(header) >= 26:
            dib_size = struct.unpack("<I", header[14:18])[0]
            if dib_size == 12:
                return struct.unpack("<HH", header[18:22])
            if dib_size >= 40:
                width, height = struct.unpack("<ii", header[18:26])
                return abs(width), abs(height)
        if header[:2] == b"\xff\xd8":
            stream.seek(2)
            sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                   0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
            while True:
                marker_start = stream.read(1)
                if not marker_start:
                    break
                if marker_start != b"\xff":
                    continue
                marker = stream.read(1)
                while marker == b"\xff":
                    marker = stream.read(1)
                if not marker:
                    break
                code = marker[0]
                if code in {0xD9, 0xDA}:
                    break
                if code in {0x00, 0x01} or 0xD0 <= code <= 0xD8:
                    continue
                raw_length = stream.read(2)
                if len(raw_length) != 2:
                    break
                length = struct.unpack(">H", raw_length)[0]
                if length < 2:
                    break
                if code in sof:
                    data = stream.read(5)
                    if len(data) == 5:
                        height, width = struct.unpack(">HH", data[1:5])
                        return width, height
                    break
                stream.seek(length - 2, 1)
    try:
        from PIL import Image
        with Image.open(path) as image:
            return image.size
    except (ImportError, OSError, ValueError):
        pass
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
             "stream=width,height", "-of", "json", str(path)],
            check=True, capture_output=True, text=True, timeout=20)
        stream = json.loads(result.stdout)["streams"][0]
        return int(stream["width"]), int(stream["height"])
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, IndexError):
        return None


def portable_file(value: str) -> bool:
    if not isinstance(value, str) or not value.strip() or "\\" in value:
        return False
    path = PurePosixPath(value)
    return bool(path.name) and value not in {".", "./"} and not path.is_absolute() and ".." not in path.parts and not re.match(r"^[A-Za-z]:", value)


def inventory(folder: Path, reading_direction: str, classifications=None, recursive=False):
    folder = Path(folder).resolve()
    if not folder.is_dir():
        raise ProjectError(f"Pasta de imagens inexistente: {folder}")
    if reading_direction not in DIRECTIONS:
        raise ProjectError("Defina a direção de leitura a partir da fonte.")
    classifications = classifications or {}
    paths = folder.rglob("*") if recursive else folder.iterdir()
    files = [p for p in paths if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]
    files.sort(key=lambda p: (natural_key(p.relative_to(folder).as_posix()), p.name))
    if not files:
        raise ProjectError("A pasta não contém imagens suportadas.")
    known = {p.relative_to(folder).as_posix() for p in files}
    unknown = set(classifications) - known
    if unknown:
        raise ProjectError("Classificação para arquivo inexistente: " + ", ".join(sorted(unknown)))
    if any(status not in STATUSES for status in classifications.values()):
        raise ProjectError("Status deve ser narrative, cover, advertisement ou editorial.")
    pages, warnings = [], []
    for i, file in enumerate(files, 1):
        relative = file.relative_to(folder).as_posix()
        if not file.resolve().is_relative_to(folder):
            raise ProjectError(f"Imagem aponta para fora da pasta: {relative}")
        dimensions = image_size(file)
        if not dimensions or min(dimensions) <= 0:
            warnings.append(f"Dimensões não verificadas: {relative}; revisar formato/arquivo.")
            dimensions = None
        page = {"id": f"P{i:03d}", "file": relative,
                "status": classifications.get(relative, "narrative"),
                "reviewed": relative in classifications,
                "sha256": sha256(file), "bytes": file.stat().st_size,
                "width": dimensions[0] if dimensions else None,
                "height": dimensions[1] if dimensions else None,
                "panels": []}
        pages.append(page)
    return {"schema_version": 1, "reading_direction": reading_direction,
            "classification_policy": "manual; narrative is provisional until reviewed=true",
            "pages": pages, "warnings": warnings}


def valid_bbox(box):
    if not isinstance(box, list) or len(box) != 4:
        return False
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) for x in box):
        return False
    x1, y1, x2, y2 = box
    # Chained comparisons also reject nan and infinities.
    return 0 <= x1 < x2 <= 1 and 0 <= y1 < y2 <= 1


def clean_narration(value: str):
    if not isinstance(value, str) or not value.strip():
        return False
    patterns = [
        r"\[[^\]]*\]", r"```", r"(?m)^\s*#", r"<[^>]+>",
        r"\b\d{1,2}:\d{2}(?::\d{2})?(?:[,.]\d+)?\b",
        r"\bP\d{2,}(?:[-_]Q\d{1,})?\b",
        r"(?im)^\s*(?:cena|beat|shot|painel|página|page|narrador|locução|narração|sfx|vfx|zoom|corte|trilha|imagem)\s*\d*\s*[:=]",
        r"(?i)\((?:zoom|corte|sfx|vfx|trilha|imagem|pausa|mostrar|fade|pan)\b[^)]*\)",
    ]
    return not any(re.search(pattern, value) for pattern in patterns)


def validate_descriptive_fields(obj, label):
    """Validate optional reviewed descriptions without inventing image facts."""
    errors = []
    for field in ("description", "observed_summary_pt", "summary", "summary_pt"):
        if field in obj and not isinstance(obj[field], str):
            errors.append(f"{label}: {field} deve ser texto.")
    for field in ("characters", "visual_tags"):
        if field in obj and (not isinstance(obj[field], list)
                             or any(not isinstance(item, str) for item in obj[field])):
            errors.append(f"{label}: {field} deve ser lista de textos.")
    if "editorial_notes" in obj and not (
            isinstance(obj["editorial_notes"], str)
            or isinstance(obj["editorial_notes"], list)
            and all(isinstance(item, str) for item in obj["editorial_notes"])):
        errors.append(f"{label}: editorial_notes deve ser texto ou lista de textos.")
    return errors


def validate_production_structure(script):
    """Check optional section links without ordering or generating any beats."""
    errors = []
    beats = script.get("beats", [])
    beats = beats if isinstance(beats, list) else []
    beat_map = {beat["id"]: beat for beat in beats
                if isinstance(beat, dict) and isinstance(beat.get("id"), str)}
    structure = script.get("production_structure")
    if "production_structure" not in script:
        if any(isinstance(beat, dict) and "section_id" in beat for beat in beats):
            errors.append("section_id exige production_structure com sections.")
        return errors
    if not isinstance(structure, dict) or not isinstance(structure.get("sections"), list):
        return ["production_structure deve ser objeto com sections como lista."]
    section_map, memberships = {}, {}
    for section in structure["sections"]:
        if not isinstance(section, dict):
            errors.append("production_structure: seção deve ser objeto.")
            continue
        sid = section.get("id")
        if not isinstance(sid, str) or not sid.strip():
            errors.append("production_structure: seção sem id válido.")
            continue
        if sid in section_map:
            errors.append(f"production_structure: ID de seção duplicado: {sid}.")
        section_map[sid] = section
        kind = section.get("kind")
        if not isinstance(kind, str) or not kind.strip():
            errors.append(f"{sid}: kind deve ser texto não vazio.")
        elif kind.strip().casefold() in AD_SECTION_KINDS:
            errors.append(f"{sid}: seção de publicidade não permitida nesta produção sem anúncios.")
        if "goal" in section and not isinstance(section["goal"], str):
            errors.append(f"{sid}: goal deve ser texto.")
        if "beats" in section:
            refs = section["beats"]
            if not isinstance(refs, list):
                errors.append(f"{sid}: beats deve ser lista de IDs.")
                continue
            for bid in refs:
                if not isinstance(bid, str) or bid not in beat_map:
                    errors.append(f"{sid}: beats referencia ID inexistente.")
                elif bid in memberships:
                    errors.append(f"{sid}: beat associado a mais de uma seção ou duplicado: {bid}.")
                else:
                    memberships[bid] = sid
    for bid, beat in beat_map.items():
        if "section_id" not in beat:
            continue
        sid = beat["section_id"]
        if not isinstance(sid, str) or sid not in section_map:
            errors.append(f"{bid}: section_id deve referenciar uma seção existente.")
            continue
        section = section_map[sid]
        if ((bid in memberships and memberships[bid] != sid)
                or (isinstance(section.get("beats"), list) and bid not in section["beats"])):
            errors.append(f"{bid}: section_id diverge dos beats declarados na seção.")
    return errors


def validate(manifest, script):
    errors = []
    if not isinstance(manifest, dict) or not isinstance(script, dict):
        return ["Manifesto e roteiro devem ser objetos JSON."]
    for label, obj in (("manifesto", manifest), ("roteiro", script)):
        if obj.get("schema_version") != 1 or isinstance(obj.get("schema_version"), bool):
            errors.append(f"{label}: schema_version deve ser 1.")
        if not isinstance(obj.get("reading_direction"), str) or obj["reading_direction"] not in DIRECTIONS:
            errors.append(f"{label}: reading_direction inválido.")
    if manifest.get("reading_direction") != script.get("reading_direction"):
        errors.append("A direção de leitura do roteiro diverge do manifesto.")
    if "narrative_order" in script and script["narrative_order"] not in ("source-order", "editorial"):
        errors.append("narrative_order deve ser source-order ou editorial.")
    errors.extend(validate_production_structure(script))
    pages = manifest.get("pages")
    if not isinstance(pages, list) or not pages:
        return errors + ["Manifesto sem lista de páginas."]
    page_map, panel_map = {}, {}
    for p in pages:
        if not isinstance(p, dict) or not isinstance(p.get("id"), str) or not p["id"].strip():
            errors.append("Página sem id válido.")
            continue
        pid = p["id"]
        errors.extend(validate_descriptive_fields(p, pid))
        if pid in page_map:
            errors.append(f"ID de página duplicado: {pid}.")
        page_map[pid] = p
        if not portable_file(p.get("file")):
            errors.append(f"{pid}: file deve ser caminho relativo portátil.")
        if not isinstance(p.get("status"), str) or p["status"] not in STATUSES:
            errors.append(f"{pid}: status inválido.")
        if not isinstance(p.get("reviewed"), bool):
            errors.append(f"{pid}: reviewed deve ser true ou false.")
        panels = p.get("panels")
        if not isinstance(panels, list):
            errors.append(f"{pid}: panels deve ser lista.")
            continue
        for panel in panels:
            if not isinstance(panel, dict) or not isinstance(panel.get("id"), str) or not panel["id"].strip():
                errors.append(f"{pid}: painel sem id válido.")
                continue
            key = (pid, panel["id"])
            errors.extend(validate_descriptive_fields(panel, f"{pid}/{panel['id']}"))
            if key in panel_map:
                errors.append(f"{pid}: ID de painel duplicado: {panel['id']}.")
            panel_map[key] = panel
            if not valid_bbox(panel.get("bbox")):
                errors.append(f"{pid}/{panel['id']}: bbox deve ser [x1,y1,x2,y2] normalizada.")
    beats = script.get("beats")
    if not isinstance(beats, list) or not beats:
        return errors + ["Roteiro sem beats."]
    seen = set()
    page_positions = {page_id: i for i, page_id in enumerate(page_map)}
    last_position = -1
    for beat in beats:
        if not isinstance(beat, dict):
            errors.append("Beat deve ser objeto.")
            continue
        bid = beat.get("id")
        errors.extend(validate_descriptive_fields(beat, str(bid)))
        if not isinstance(bid, str) or not bid.strip() or bid in seen:
            errors.append("Beat sem ID único válido.")
        if isinstance(bid, str):
            seen.add(bid)
        if not clean_narration(beat.get("narration")):
            errors.append(f"{bid}: narration vazia ou contém instruções/editorial/IDs/timecodes.")
        if not isinstance(beat.get("purpose"), str) or not beat["purpose"].strip():
            errors.append(f"{bid}: purpose é obrigatório fora da narração.")
        pid, qid = beat.get("page_id"), beat.get("panel_id")
        if not isinstance(pid, str) or pid not in page_map:
            errors.append(f"{bid}: page_id inexistente.")
            continue
        page = page_map[pid]
        if script.get("narrative_order") == "source-order":
            position = page_positions[pid]
            if position < last_position:
                errors.append(f"{bid}: roteiro declara source-order mas retrocede na ordem do manifesto.")
            last_position = position
        if page.get("status") != "narrative":
            errors.append(f"{bid}: página excluída do enredo ({page.get('status')}).")
        if page.get("reviewed") is not True:
            errors.append(f"{bid}: página ainda não revisada visualmente/classificada.")
        if not isinstance(qid, str) or (pid, qid) not in panel_map:
            errors.append(f"{bid}: panel_id inexistente nessa página.")
            continue
        panel = panel_map[(pid, qid)]
        if "bbox" in beat:
            box = beat["bbox"]
            if not valid_bbox(box):
                errors.append(f"{bid}: bbox inválida.")
            elif valid_bbox(panel.get("bbox")) and any(abs(a-b) > 1e-6 for a,b in zip(box, panel["bbox"])):
                errors.append(f"{bid}: bbox diverge do painel; corrija o manifesto primeiro.")
        if "evidence_refs" in beat:
            refs = beat["evidence_refs"]
            if not isinstance(refs, list) or not refs:
                errors.append(f"{bid}: evidence_refs deve ser lista não vazia.")
            else:
                for ref in refs:
                    if not isinstance(ref, dict) or not isinstance(ref.get("page_id"), str) or not isinstance(ref.get("panel_id"), str):
                        errors.append(f"{bid}: evidence_refs contém referência inválida.")
                        continue
                    rid, rpanel = ref["page_id"], ref["panel_id"]
                    if rid not in page_map or (rid, rpanel) not in panel_map:
                        errors.append(f"{bid}: evidence_refs referencia página/painel inexistente.")
                    elif page_map[rid].get("status") != "narrative" or page_map[rid].get("reviewed") is not True:
                        errors.append(f"{bid}: evidence_refs referencia página excluída ou sem revisão.")
    expected = "\n\n".join(b["narration"].strip() for b in beats
                              if isinstance(b, dict) and isinstance(b.get("narration"), str))
    if "narration" in script and script["narration"] != expected:
        errors.append("narration do roteiro diverge da concatenação dos beats.")
    return errors


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise ProjectError(f"JSON não pode ser lido: {path}: {exc}") from exc


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def canonical_sha256(obj):
    """Fingerprint source JSON independently of indentation or key ordering."""
    canonical = json.dumps(obj, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def reviewed_text(obj, *fields):
    for field in fields:
        value = obj.get(field)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def analysis_image_root(image_root, output_dir):
    if image_root is None:
        return None
    root = Path(image_root).resolve()
    try:
        return Path(os.path.relpath(root, Path(output_dir).resolve())).as_posix()
    except ValueError:
        # Different drive letters on Windows cannot have a relative path.
        return root.as_posix()


def editing_analysis(manifest, script, output_dir, image_root=None):
    """Export reviewed page/panel facts and an exact beat-to-image lookup.

    This is a mapping export, not image recognition or audio alignment. Keep
    the full source objects and fingerprints so editors can verify the handoff.
    """
    errors = validate(manifest, script)
    if errors:
        raise ProjectError("\n".join(errors))
    catalog, warnings = [], []
    page_map, panel_map = {}, {}
    for page in manifest["pages"]:
        pid = page["id"]
        entry = {"page_id": pid, "file": page["file"], "status": page["status"],
                 "reviewed": page["reviewed"],
                 "summary": reviewed_text(page, "summary", "summary_pt", "description"),
                 "panels": []}
        for panel in page["panels"]:
            item = {"id": panel["id"], "bbox": copy.deepcopy(panel["bbox"]),
                    "description": reviewed_text(panel, "description", "observed_summary_pt"),
                    "characters": copy.deepcopy(panel.get("characters", [])),
                    "visual_tags": copy.deepcopy(panel.get("visual_tags", []))}
            if not item["description"]:
                warnings.append(f"{pid}/{panel['id']}: descrição visual ausente; não foi inferida.")
            entry["panels"].append(item)
            panel_map[(pid, panel["id"])] = item
        page_map[pid] = entry
        catalog.append(entry)
    shots = []
    for beat in script["beats"]:
        pid, qid = beat["page_id"], beat["panel_id"]
        page, panel = page_map[pid], panel_map[(pid, qid)]
        shot = {"beat_id": beat["id"], "narration": beat["narration"],
                "purpose": beat["purpose"], "page_id": pid, "panel_id": qid,
                "file": page["file"], "bbox": copy.deepcopy(panel["bbox"]),
                "description": panel["description"] or reviewed_text(beat, "description", "observed_summary_pt"),
                "characters": copy.deepcopy(beat.get("characters", panel["characters"])),
                "visual_tags": copy.deepcopy(beat.get("visual_tags", panel["visual_tags"])),
                "evidence_refs": copy.deepcopy(beat.get("evidence_refs", [{"page_id": pid, "panel_id": qid}])),
                "editorial_notes": copy.deepcopy(beat.get("editorial_notes", ""))}
        if "motion" in beat:
            shot["motion"] = copy.deepcopy(beat["motion"])
        if "section_id" in beat:
            shot["section_id"] = beat["section_id"]
        if not shot["description"]:
            warnings.append(f"{beat['id']}: descrição visual ausente; consultar a imagem indicada.")
        shots.append(shot)
    root_hint = analysis_image_root(image_root, output_dir)
    if root_hint is None:
        warnings.append("Raiz das imagens não informada; a edição precisa de --image-root.")
    analysis = {"schema_version": 1, "kind": "manga-hq-editing-analysis",
            "manifest": copy.deepcopy(manifest), "script": copy.deepcopy(script),
            "source_fingerprints": {"manifest_sha256": canonical_sha256(manifest),
                                    "script_sha256": canonical_sha256(script)},
            "image_root": root_hint, "image_catalog": catalog, "shots": shots,
            "notes": "timestamps require supplied audio alignment",
            "warnings": warnings}
    if "production_structure" in script:
        analysis["production_structure"] = copy.deepcopy(script["production_structure"])
    return analysis


def markdown_text(value):
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def markdown_image_link(analysis, file):
    root = analysis["image_root"]
    label = markdown_text(file).replace("[", "\\[").replace("]", "\\]")
    if root is None:
        return f"`{file}` (raiz pendente)"
    target = (Path(root) / Path(file)).as_posix()
    return f"[{label}](<{quote(target, safe='/:')}>)"


def analysis_markdown(analysis):
    """Readable lookup: ordered shots, excluded pages and searchable panel index."""
    root = analysis["image_root"]
    if root is None:
        root_description = "Raiz das imagens não informada; fornecer `--image-root` na edição."
    elif Path(root).is_absolute():
        root_description = f"Raiz das imagens: `{root}` (caminho absoluto; ajustar se o projeto mudar de computador)."
    else:
        root_description = f"Raiz das imagens: `{root}` (relativa à pasta desta análise)."
    lines = ["# Análise de imagens para edição", "",
             "Este arquivo relaciona o roteiro às páginas e aos painéis já revisados. "
             "As descrições vêm das fontes fornecidas; o exportador não interpreta imagens.", "",
             "Os tempos devem vir do alinhamento com o áudio de narração fornecido.", "",
             root_description, ""]
    if "production_structure" in analysis:
        structure = analysis["production_structure"]
        lines.extend(["## Estrutura completa da produção", "",
                      "Este plano preserva gancho, intro/vinheta, desenvolvimento e encerramento. "
                      "As seções são orientações de montagem; este arquivo não confirma que esses módulos "
                      "foram renderizados nem fornece tempos finais de áudio.", ""])
        extras = {key: value for key, value in structure.items() if key != "sections"}
        if extras:
            lines.extend(["Plano geral:", "", "```json", json.dumps(extras, ensure_ascii=False, indent=2), "```", ""])
        for section in structure["sections"]:
            sid = section["id"]
            refs = section.get("beats", [shot["beat_id"] for shot in analysis["shots"]
                                         if shot.get("section_id") == sid])
            lines.extend([f"### {markdown_text(sid)} — {markdown_text(section['kind'])}", ""])
            if section.get("goal"):
                lines.extend([markdown_text(section["goal"]), ""])
            lines.append("- Beats: " + (", ".join(f"`{markdown_text(bid)}`" for bid in refs)
                                          if refs else "nenhum; elemento de produção sem beat narrado."))
            details = {key: value for key, value in section.items() if key not in {"id", "kind", "goal", "beats"}}
            if details:
                lines.extend(["", "Orientações fornecidas (durações estimadas não são marcas confirmadas):", "",
                              "```json", json.dumps(details, ensure_ascii=False, indent=2), "```"])
            lines.append("")
    lines.extend(["## Roteiro e imagens por beat", ""])
    for shot in analysis["shots"]:
        lines.extend([f"### {markdown_text(shot['beat_id'])} — {markdown_text(shot['purpose'])}", "",
                      shot["narration"], "",
                      f"- Imagem: {markdown_image_link(analysis, shot['file'])}",
                      f"- Página/painel: `{shot['page_id']}` / `{shot['panel_id']}`; "
                      f"bbox normalizada: `{json.dumps(shot['bbox'])}`.",
                      f"- Descrição: {markdown_text(shot['description']) or 'Não fornecida; conferir a imagem.'}",
                      f"- Personagens: {markdown_text(', '.join(shot['characters'])) or 'Não informados.'}",
                      f"- Palavras-chave visuais: {markdown_text(', '.join(shot['visual_tags'])) or 'Não informadas.'}"])
        if "section_id" in shot:
            lines.append(f"- Seção de produção: `{markdown_text(shot['section_id'])}`.")
        refs = ", ".join(f"{ref['page_id']}/{ref['panel_id']}" for ref in shot["evidence_refs"])
        lines.append(f"- Evidências de apoio: {markdown_text(refs)}.")
        notes = shot["editorial_notes"]
        if notes:
            lines.append(f"- Orientação editorial: {markdown_text('; '.join(notes) if isinstance(notes, list) else notes)}")
        if "motion" in shot:
            lines.append(f"- Movimento proposto: `{json.dumps(shot['motion'], ensure_ascii=False)}`.")
        lines.append("")
    lines.extend(["## Páginas excluídas do enredo", ""])
    excluded = [page for page in analysis["image_catalog"] if page["status"] != "narrative"]
    if not excluded:
        lines.extend(["Nenhuma página classificada para exclusão.", ""])
    for page in excluded:
        lines.append(f"- `{page['page_id']}` — {page['status']}: {markdown_image_link(analysis, page['file'])}"
                     + (f" — {markdown_text(page['summary'])}" if page["summary"] else ""))
    lines.extend(["", "## Índice de todas as imagens e painéis", "",
                  "Use a busca por descrição, personagem, palavra-chave, ID ou nome do arquivo. "
                  "Páginas excluídas continuam no catálogo, mas não são planos narrativos.", ""])
    for page in analysis["image_catalog"]:
        lines.extend([f"### {page['page_id']} — {page['status']}", "",
                      f"Imagem: {markdown_image_link(analysis, page['file'])}. "
                      f"Revisada: {'sim' if page['reviewed'] else 'não'}.", ""])
        if page["summary"]:
            lines.extend([markdown_text(page["summary"]), ""])
        for panel in page["panels"]:
            lines.append(f"- `{panel['id']}`; bbox `{json.dumps(panel['bbox'])}`; "
                         f"{markdown_text(panel['description']) or 'Descrição não fornecida.'} "
                         f"Personagens: {markdown_text(', '.join(panel['characters'])) or 'não informados'}. "
                         f"Palavras-chave: {markdown_text(', '.join(panel['visual_tags'])) or 'não informadas'}.")
        lines.append("")
    if analysis["warnings"]:
        lines.extend(["## Pendências", ""])
        lines.extend(f"- {markdown_text(warning)}" for warning in analysis["warnings"])
        lines.append("")
    return "\n".join(lines)


def build(manifest, script, output_dir, *, image_root=None):
    errors = validate(manifest, script)
    if errors:
        raise ProjectError("\n".join(errors))
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    analysis = editing_analysis(manifest, script, out, image_root)
    narration = "\n\n".join(b["narration"].strip() for b in script["beats"]) + "\n"
    (out / "narration.txt").write_text(narration, encoding="utf-8")
    write_json(out / "validated-script.json", script)
    write_json(out / "editing-analysis.json", analysis)
    (out / "editing-analysis.md").write_text(analysis_markdown(analysis), encoding="utf-8")
    return out / "narration.txt"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inv = commands.add_parser("inventory", help="Inventariar imagens; classificação exige revisão humana.")
    inv.add_argument("folder", type=Path)
    inv.add_argument("--output", type=Path, required=True)
    inv.add_argument("--reading-direction", choices=sorted(DIRECTIONS), required=True)
    inv.add_argument("--recursive", action="store_true")
    inv.add_argument("--classify", action="append", default=[], metavar="FILE=STATUS")
    for name in ("validate", "build"):
        cmd = commands.add_parser(name)
        cmd.add_argument("--manifest", required=True, type=Path)
        cmd.add_argument("--script", required=True, type=Path)
        if name == "build":
            cmd.add_argument("--output-dir", required=True, type=Path)
            cmd.add_argument("--image-root", type=Path,
                             help="Pasta base das imagens; padrão: pasta do manifesto.")
    args = parser.parse_args(argv)
    try:
        if args.command == "inventory":
            classifications = {}
            for item in args.classify:
                if "=" not in item:
                    raise ProjectError("Use --classify FILE=STATUS após examinar a página.")
                file, status = item.rsplit("=", 1)
                classifications[file] = status
            obj = inventory(args.folder, args.reading_direction, classifications, args.recursive)
            write_json(args.output, obj)
            print(f"{len(obj['pages'])} imagens inventariadas; nenhuma história foi inferida.")
        else:
            manifest, script = load_json(args.manifest), load_json(args.script)
            if args.command == "validate":
                errors = validate(manifest, script)
                if errors:
                    raise ProjectError("\n".join(errors))
                print(f"Roteiro válido: {len(script['beats'])} beats com referências existentes.")
                print("A validação estrutural não substitui conferência factual das imagens.")
            else:
                root = args.image_root if args.image_root is not None else args.manifest.resolve().parent
                print(f"Narração limpa criada: {build(manifest, script, args.output_dir, image_root=root)}")
                print(f"Análise para edição criada: {args.output_dir / 'editing-analysis.json'}")
                print(f"Índice visual legível criado: {args.output_dir / 'editing-analysis.md'}")
    except (ProjectError, OSError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
