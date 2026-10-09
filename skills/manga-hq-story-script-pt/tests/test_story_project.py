import copy
import importlib.util
import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("story_project", Path(__file__).parents[1] / "scripts" / "story_project.py")
story = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(story)


def png(path, width=8, height=12):
    def chunk(name, data):
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", zlib.crc32(name + data))
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    data += chunk(b"IDAT", zlib.compress((b"\0" + b"\xff\xff\xff" * width) * height))
    data += chunk(b"IEND", b"")
    path.write_bytes(data)


class StoryProjectTests(unittest.TestCase):
    def setUp(self):
        self.manifest = {"schema_version": 1, "reading_direction": "left-to-right", "pages": [
            {"id": "P01", "file": "1.png", "status": "narrative", "reviewed": True,
             "panels": [{"id": "P01-Q01", "bbox": [0.1, 0.2, 0.9, 0.8]}]},
            {"id": "P02", "file": "2.png", "status": "advertisement", "reviewed": True,
             "panels": [{"id": "P02-Q01", "bbox": [0, 0, 1, 1]}]}]}
        self.script = {"schema_version": 1, "reading_direction": "left-to-right", "beats": [
            {"id": "B01", "narration": "Ele encontrou uma pista e decidiu investigar.",
             "page_id": "P01", "panel_id": "P01-Q01", "purpose": "gancho"}]}

    def test_inventory_real_images_natural_order_and_nonimage_filter(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            root = Path(directory)
            for name in ["10.png", "2.png", "1.png"]:
                png(root / name)
            (root / "roteiro.txt").write_text("texto", encoding="utf-8")
            result = story.inventory(root, "right-to-left")
            self.assertEqual([p["file"] for p in result["pages"]], ["1.png", "2.png", "10.png"])
            self.assertEqual([p["id"] for p in result["pages"]], ["P001", "P002", "P003"])
            self.assertEqual((result["pages"][0]["width"], result["pages"][0]["height"]), (8, 12))
            self.assertEqual(len(result["pages"][0]["sha256"]), 64)
            self.assertFalse(result["pages"][0]["reviewed"])

    def test_manual_exclusion_is_recorded_not_guessed(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            root = Path(directory)
            png(root / "capa.png")
            result = story.inventory(root, "left-to-right", {"capa.png": "cover"})
            self.assertEqual(result["pages"][0]["status"], "cover")
            self.assertTrue(result["pages"][0]["reviewed"])
            with self.assertRaises(story.ProjectError):
                story.inventory(root, "left-to-right", {"ausente.png": "editorial"})

    def test_valid_script(self):
        self.assertEqual(story.validate(self.manifest, self.script), [])

    def test_unknown_page_and_panel(self):
        for field, value in [("page_id", "P99"), ("panel_id", "P02-Q01")]:
            with self.subTest(field=field):
                script = copy.deepcopy(self.script)
                script["beats"][0][field] = value
                self.assertTrue(story.validate(self.manifest, script))

    def test_all_editorial_page_types_are_excluded(self):
        for status in ["cover", "advertisement", "editorial"]:
            with self.subTest(status=status):
                self.manifest["pages"][0]["status"] = status
                self.assertTrue(any("excluída" in e for e in story.validate(self.manifest, self.script)))

    def test_unreviewed_used_page_is_rejected(self):
        self.manifest["pages"][0]["reviewed"] = False
        self.assertTrue(any("revisada" in e for e in story.validate(self.manifest, self.script)))

    def test_mismatched_and_invalid_bbox_are_rejected(self):
        for bbox in [[0, 0, 1, 1], [0.9, 0.2, 0.1, 0.8], [0, 0, 2, 1], [0, 0, True, 1]]:
            with self.subTest(bbox=bbox):
                self.script["beats"][0]["bbox"] = bbox
                self.assertTrue(any("bbox" in e for e in story.validate(self.manifest, self.script)))
        self.script["beats"][0]["bbox"] = [0.1, 0.2, 0.9, 0.8]
        self.assertEqual(story.validate(self.manifest, self.script), [])

    def test_empty_narration_and_editorial_cues_are_rejected(self):
        for narration in ["", "   ", "[zoom no rosto] Ele correu.", "P01-Q01: Ele correu.",
                          "Cena 1: Ele correu.", "00:04 Ele correu.", "Ele correu. (SFX explosão)"]:
            with self.subTest(narration=narration):
                self.script["beats"][0]["narration"] = narration
                self.assertTrue(any("narration" in e for e in story.validate(self.manifest, self.script)))

    def test_build_only_exports_validated_clean_narration(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            output = story.build(self.manifest, self.script, directory)
            self.assertEqual(output.read_text(encoding="utf-8"), self.script["beats"][0]["narration"] + "\n")
            saved = json.loads((Path(directory) / "validated-script.json").read_text(encoding="utf-8"))
            self.assertEqual(saved, self.script)
            self.script["beats"][0]["narration"] = "[Corte]"
            with self.assertRaises(story.ProjectError):
                story.build(self.manifest, self.script, directory)
            self.assertEqual(output.read_text(encoding="utf-8"), "Ele encontrou uma pista e decidiu investigar.\n")

    def test_divergent_aggregate_narration_and_reading_direction(self):
        self.script["narration"] = "Texto que não é o dos beats."
        self.script["reading_direction"] = "right-to-left"
        errors = story.validate(self.manifest, self.script)
        self.assertTrue(any("concatenação" in e for e in errors))
        self.assertTrue(any("direção" in e for e in errors))

    def test_manifest_path_portability_and_duplicate_ids(self):
        self.manifest["pages"][0]["file"] = "../fora.png"
        self.manifest["pages"].append(copy.deepcopy(self.manifest["pages"][0]))
        errors = story.validate(self.manifest, self.script)
        self.assertTrue(any("portátil" in e for e in errors))
        self.assertTrue(any("duplicado" in e for e in errors))

    def test_malformed_input_returns_errors_without_crash(self):
        self.assertTrue(story.validate([], self.script))
        self.manifest["reading_direction"] = []
        self.manifest["pages"][0]["status"] = []
        self.assertTrue(story.validate(self.manifest, self.script))
        self.script["beats"] = [None]
        self.assertTrue(story.validate(self.manifest, self.script))

    def test_declared_source_order_cannot_reverse_pages(self):
        self.manifest["pages"][1]["status"] = "narrative"
        self.script["narrative_order"] = "source-order"
        earlier = copy.deepcopy(self.script["beats"][0])
        later = copy.deepcopy(earlier)
        later.update(id="B02", page_id="P02", panel_id="P02-Q01")
        self.script["beats"] = [later, earlier]
        self.assertTrue(any("source-order" in e for e in story.validate(self.manifest, self.script)))

    def test_unknown_narrative_order_and_directory_as_file_rejected(self):
        self.script["narrative_order"] = "soruce-order"
        self.manifest["pages"][0]["file"] = "."
        errors = story.validate(self.manifest, self.script)
        self.assertTrue(any("narrative_order" in e for e in errors))
        self.assertTrue(any("portátil" in e for e in errors))

    def test_supporting_evidence_cannot_reference_ads_or_unknown_panels(self):
        for refs in [[{"page_id": "P02", "panel_id": "P02-Q01"}],
                     [{"page_id": "P01", "panel_id": "P99-Q01"}], [None]]:
            with self.subTest(refs=refs):
                self.script["beats"][0]["evidence_refs"] = refs
                self.assertTrue(any("evidence_refs" in e for e in story.validate(self.manifest, self.script)))


if __name__ == "__main__":
    unittest.main()
