#!/usr/bin/env python3
"""Validação estrutural de skills compatíveis com Agent Skills."""
import argparse
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {
    "architecture", "engineering", "leadership", "automation", "content",
    "marketing", "product", "data", "operations", "research",
}
STATUSES = {"experimental", "stable", "deprecated"}
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate_skill(directory: Path) -> list[str]:
    errors: list[str] = []
    filepath = directory / "SKILL.md"
    if not filepath.is_file():
        return [f"{directory}: SKILL.md obrigatório ausente."]

    raw = filepath.read_text(encoding="utf-8-sig")
    lines = raw.splitlines()
    if not lines or lines[0] != "---":
        return [f"{filepath}: frontmatter YAML deve começar com ---."]

    try:
        end = lines.index("---", 1)
    except ValueError:
        return [f"{filepath}: frontmatter YAML não foi fechado com ---."]

    try:
        fields = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError as error:
        return [f"{filepath}: YAML inválido: {error}"]

    if not isinstance(fields, dict):
        return [f"{filepath}: frontmatter deve conter um mapa YAML."]

    name = fields.get("name")
    if not isinstance(name, str) or not NAME_PATTERN.fullmatch(name) or len(name) > 64:
        errors.append(f"{filepath}: name deve ter 1 a 64 caracteres em kebab-case.")
    elif name != directory.name:
        errors.append(f"{filepath}: name deve coincidir com o nome da pasta.")

    description = fields.get("description")
    if not isinstance(description, str) or not 1 <= len(description.strip()) <= 1024:
        errors.append(f"{filepath}: description deve ter entre 1 e 1024 caracteres.")

    meta = fields.get("metadata")
    if not isinstance(meta, dict):
        errors.append(f"{filepath}: metadata é obrigatório e deve ser um mapa.")
    else:
        if meta.get("category") not in CATEGORIES:
            errors.append(f"{filepath}: metadata.category inválida.")
        if meta.get("status") not in STATUSES:
            errors.append(f"{filepath}: metadata.status inválido.")
        if not isinstance(meta.get("version"), str) or not meta["version"].strip():
            errors.append(f"{filepath}: metadata.version deve ser texto não vazio.")

    if not "\n".join(lines[end + 1:]).strip():
        errors.append(f"{filepath}: corpo Markdown não pode estar vazio.")

    return errors


def validate_collection(root: Path = ROOT) -> tuple[int, list[str]]:
    skills = root / "skills"
    if not skills.is_dir():
        return 0, [f"{skills}: diretório skills/ não encontrado."]
    directories = sorted(
        item for item in skills.iterdir() if item.is_dir() and not item.name.startswith(".")
    )
    errors: list[str] = []
    if not directories:
        errors.append("Nenhuma skill cadastrada em skills/.")

    for directory in directories:
        if directory.is_symlink():
            errors.append(f"{directory}: symlinks não são permitidos em skills/.")
        else:
            errors.extend(validate_skill(directory))
    return len(directories), errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    count, errors = validate_collection(args.root)

    if errors:
        for error in errors:
            print("ERRO:", error)
        raise SystemExit(1)
    print(f"OK: {count} skill(s) válida(s).")


if __name__ == "__main__":
    main()
