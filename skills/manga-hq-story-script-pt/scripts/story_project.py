#!/usr/bin/env python3
"""Inventory image pages and validate an evidence-linked, human-reviewed script.

Python standard library is sufficient for JPG/PNG/GIF/BMP dimensions. Pillow,
then ffprobe, are optional fallbacks for other image formats. This program does
not read panels, infer a plot, classify advertisements, or generate narration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import subprocess
import sys
from pathlib import Path, PurePosixPath

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tif", ".tiff"}
STATUSES = {"narrative", "cover", "advertisement", "editorial"}
DIRECTIONS = {"left-to-right", "right-to-left"}


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
    pages = manifest.get("pages")
    if not isinstance(pages, list) or not pages:
        return errors + ["Manifesto sem lista de páginas."]
    page_map, panel_map = {}, {}
    for p in pages:
        if not isinstance(p, dict) or not isinstance(p.get("id"), str) or not p["id"].strip():
            errors.append("Página sem id válido.")
            continue
        pid = p["id"]
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


def build(manifest, script, output_dir):
    errors = validate(manifest, script)
    if errors:
        raise ProjectError("\n".join(errors))
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    narration = "\n\n".join(b["narration"].strip() for b in script["beats"]) + "\n"
    (out / "narration.txt").write_text(narration, encoding="utf-8")
    write_json(out / "validated-script.json", script)
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
                print(f"Narração limpa criada: {build(manifest, script, args.output_dir)}")
    except (ProjectError, OSError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
