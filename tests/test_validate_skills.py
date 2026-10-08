"""Testes locais do scaffold e das validações do SkillForge."""
import tempfile
import unittest
from pathlib import Path

from scripts.new_skill import scaffold
from scripts.validate_skills import validate_collection


class SkillforgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "skills").mkdir()
        (self.root / "templates").mkdir()
        source = Path(__file__).resolve().parents[1] / "templates" / "SKILL.template.md"
        (self.root / "templates" / "SKILL.template.md").write_text(
            source.read_text(encoding="utf-8"), encoding="utf-8"
        )

    def test_scaffold_produces_valid_skill(self) -> None:
        path = scaffold("example-skill", "Use para exemplificar um fluxo.", "research", self.root)
        self.assertTrue((path / "SKILL.md").exists())
        count, errors = validate_collection(self.root)
        self.assertEqual(count, 1)
        self.assertEqual(errors, [])

    def test_bad_name_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            scaffold("Invalid Name", "Descrição", "research", self.root)

    def test_duplicate_is_rejected(self) -> None:
        scaffold("example-skill", "Descrição", "research", self.root)
        with self.assertRaises(FileExistsError):
            scaffold("example-skill", "Descrição", "research", self.root)

    def test_missing_skill_md_is_rejected(self) -> None:
        (self.root / "skills" / "broken-skill").mkdir()
        _, errors = validate_collection(self.root)
        self.assertTrue(any("SKILL.md" in error for error in errors))

    def test_invalid_category_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            scaffold("example-skill", "Descrição", "other", self.root)


if __name__ == "__main__":
    unittest.main()
