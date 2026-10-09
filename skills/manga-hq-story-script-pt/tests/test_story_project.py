import copy
import contextlib
import hashlib
import importlib.util
import io
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

    def test_analysis_catalog_keeps_excluded_pages_but_shots_only_use_script(self):
        panel = self.manifest["pages"][0]["panels"][0]
        panel.update(description="Detetive em uma rua chuvosa.",
                     characters=["Detetive"], visual_tags=["chuva", "rua"])
        self.manifest["pages"][0]["summary"] = "Uma pista aparece."
        self.manifest["pages"][0]["panels"].append({"id": "P01-Q02", "bbox": [0, 0, 0.1, 0.1],
                                                    "description": "Uma carta ainda fechada."})
        self.manifest["pages"][1]["summary_pt"] = "Publicidade fora do enredo."
        self.script["beats"][0].update(editorial_notes=["Manter a pista visível."],
                                        motion={"from_scale": 1, "to_scale": 1.8})
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            output = story.build(self.manifest, self.script, directory)
            analysis = json.loads((output.parent / "editing-analysis.json").read_text(encoding="utf-8"))
            self.assertEqual(analysis["kind"], "manga-hq-editing-analysis")
            self.assertEqual([page["page_id"] for page in analysis["image_catalog"]], ["P01", "P02"])
            self.assertEqual(analysis["image_catalog"][1]["status"], "advertisement")
            self.assertEqual(len(analysis["shots"]), 1)
            shot = analysis["shots"][0]
            self.assertEqual((shot["beat_id"], shot["page_id"], shot["panel_id"], shot["file"]),
                             ("B01", "P01", "P01-Q01", "1.png"))
            self.assertEqual(shot["description"], panel["description"])
            self.assertEqual(shot["bbox"], panel["bbox"])
            self.assertEqual(shot["characters"], ["Detetive"])
            self.assertEqual(shot["visual_tags"], ["chuva", "rua"])
            self.assertEqual(shot["evidence_refs"], [{"page_id": "P01", "panel_id": "P01-Q01"}])
            self.assertEqual(shot["motion"], self.script["beats"][0]["motion"])
            self.assertNotIn("start", shot)
            self.assertNotIn("end", shot)
            human = (output.parent / "editing-analysis.md").read_text(encoding="utf-8")
            self.assertIn(self.script["beats"][0]["narration"], human)
            self.assertIn("Páginas excluídas do enredo", human)
            self.assertIn("P01-Q02", human)
            self.assertIn("Uma carta ainda fechada", human)
            self.assertIn("chuva", human)

    def test_analysis_canonical_fingerprints_and_sources_are_independent_copies(self):
        original_manifest, original_script = copy.deepcopy(self.manifest), copy.deepcopy(self.script)
        analysis = story.editing_analysis(self.manifest, self.script, Path("unused"))
        self.assertEqual(self.manifest, original_manifest)
        self.assertEqual(self.script, original_script)
        for name, source in (("manifest", self.manifest), ("script", self.script)):
            expected = hashlib.sha256(json.dumps(source, ensure_ascii=False, sort_keys=True,
                                                  separators=(",", ":")).encode("utf-8")).hexdigest()
            self.assertEqual(analysis["source_fingerprints"][name + "_sha256"], expected)
            self.assertEqual(story.canonical_sha256(dict(reversed(list(source.items())))), expected)
        analysis["manifest"]["pages"][0]["file"] = "alterado.png"
        analysis["script"]["beats"][0]["narration"] = "Alterado."
        analysis["shots"][0]["bbox"][0] = 0
        analysis["image_catalog"][0]["panels"][0]["bbox"][0] = 0
        self.assertEqual(self.manifest, original_manifest)
        self.assertEqual(self.script, original_script)

    def test_missing_visual_descriptions_are_empty_with_honest_warnings(self):
        analysis = story.editing_analysis(self.manifest, self.script, Path("unused"))
        self.assertIsNone(analysis["image_root"])
        shot = analysis["shots"][0]
        self.assertEqual(shot["description"], "")
        self.assertEqual(shot["characters"], [])
        self.assertEqual(shot["visual_tags"], [])
        self.assertTrue(any("descrição visual ausente" in warning for warning in analysis["warnings"]))
        self.assertTrue(any("--image-root" in warning for warning in analysis["warnings"]))
        self.assertEqual(analysis["notes"], "timestamps require supplied audio alignment")
        self.assertNotIn("motion", shot)

    def test_analysis_image_paths_are_relative_portable_and_markdown_escaped(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            base = Path(directory).resolve()
            project = base / "projeto original"
            images = project / "imagens da HQ"
            images.mkdir(parents=True)
            filename = "1 cena [chuva]#.png"
            png(images / filename)
            self.manifest["pages"][0]["file"] = filename
            out = project / "export" / "roteiro"
            story.build(self.manifest, self.script, out, image_root=images)
            analysis = story.load_json(out / "editing-analysis.json")
            self.assertEqual(analysis["image_root"], "../../imagens da HQ")
            self.assertEqual((out / analysis["image_root"] / filename).resolve(), (images / filename).resolve())
            human = (out / "editing-analysis.md").read_text(encoding="utf-8")
            self.assertIn("../../imagens%20da%20HQ/1%20cena%20%5Bchuva%5D%23.png", human)
            self.assertIn(r"1 cena \[chuva\]#.png", human)
            moved = base / "projeto movido"
            self.assertTrue(project.resolve().is_relative_to(base))
            self.assertTrue(moved.resolve().is_relative_to(base))
            project.rename(moved)
            moved_out = moved / "export" / "roteiro"
            self.assertTrue((moved_out / analysis["image_root"] / filename).is_file())

    def test_cli_build_default_root_is_manifest_parent_and_explicit_root_wins(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            base = Path(directory).resolve()
            source = base / "source"
            source.mkdir()
            manifest_path, script_path = source / "manifest.json", base / "script.json"
            story.write_json(manifest_path, self.manifest)
            story.write_json(script_path, self.script)
            for explicit in (False, True):
                output = base / ("explicit" if explicit else "default")
                argv = ["build", "--manifest", str(manifest_path), "--script", str(script_path),
                        "--output-dir", str(output)]
                expected = source
                if explicit:
                    expected = base / "another image folder"
                    expected.mkdir()
                    argv.extend(["--image-root", str(expected)])
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(story.main(argv), 0)
                analysis = story.load_json(output / "editing-analysis.json")
                self.assertEqual((output / analysis["image_root"]).resolve(), expected)

    def test_descriptive_metadata_requires_text_and_lists_of_text(self):
        for key, value in [("description", ["palavra"]), ("summary", {}),
                           ("characters", "Detetive"), ("visual_tags", [1]),
                           ("editorial_notes", {"instruction": "zoom"})]:
            with self.subTest(key=key):
                manifest = copy.deepcopy(self.manifest)
                manifest["pages"][0]["panels"][0][key] = value
                self.assertTrue(any(key in error for error in story.validate(manifest, self.script)))
                with self.assertRaises(story.ProjectError):
                    story.editing_analysis(manifest, self.script, Path("unused"))

    def test_reviewed_alias_and_beat_metadata_are_preserved_without_guessing(self):
        panel = self.manifest["pages"][0]["panels"][0]
        panel["observed_summary_pt"] = "Objeto na mão do personagem."
        beat = self.script["beats"][0]
        beat.update(characters=["Nome informado"], visual_tags=["objeto"],
                    description="Descrição editorial fornecida.", editorial_notes="Mostrar o objeto.")
        analysis = story.editing_analysis(self.manifest, self.script, Path("unused"))
        shot = analysis["shots"][0]
        self.assertEqual(shot["description"], panel["observed_summary_pt"])
        self.assertEqual(shot["characters"], beat["characters"])
        self.assertEqual(shot["visual_tags"], beat["visual_tags"])
        del panel["observed_summary_pt"]
        self.assertEqual(story.editing_analysis(self.manifest, self.script, Path("unused"))["shots"][0]["description"],
                         beat["description"])

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
