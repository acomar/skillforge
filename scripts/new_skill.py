#!/usr/bin/env python3
"""Cria uma nova skill experimental a partir do modelo do SkillForge."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = (
    "architecture", "engineering", "leadership", "automation", "content",
    "marketing", "product", "data", "operations", "research",
)
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def scaffold(name: str, description: str, category: str, root: Path = ROOT) -> Path:
    if not NAME_PATTERN.fullmatch(name) or len(name) > 64:
        raise ValueError("O nome deve ter até 64 caracteres em kebab-case.")
    if not description.strip() or len(description) > 1024:
        raise ValueError("A descrição deve ter entre 1 e 1024 caracteres.")
    if category not in CATEGORIES:
        raise ValueError("Categoria inválida: " + category)

    destination = root / "skills" / name
    if destination.exists():
        raise FileExistsError(f"A skill já existe: {destination}")

    template = (root / "templates" / "SKILL.template.md").read_text(encoding="utf-8")
    replacements = {
        "{{NAME}}": name,
        "{{DESCRIPTION}}": json.dumps(description.strip(), ensure_ascii=False),
        "{{CATEGORY}}": category,
        "{{STATUS}}": "experimental",
    }
    for original, replacement in replacements.items():
        template = template.replace(original, replacement)

    destination.mkdir(parents=True)
    (destination / "SKILL.md").write_text(template, encoding="utf-8")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="Nome em kebab-case, como eventstorming-facilitator")
    parser.add_argument("--category", required=True, choices=CATEGORIES)
    parser.add_argument("--description", required=True)
    args = parser.parse_args()

    try:
        path = scaffold(args.name, args.description, args.category)
    except (ValueError, FileExistsError) as error:
        parser.error(str(error))
    print(f"Skill experimental criada: {path}")
    print("Edite o SKILL.md, substitua as instruções genéricas e valide antes de usar.")


if __name__ == "__main__":
    main()
