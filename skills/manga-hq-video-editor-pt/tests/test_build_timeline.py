import base64
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import wave
import zlib

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/build_timeline.py"
SPEC = importlib.util.spec_from_file_location("build_timeline", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TimelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.image = self.root / "page 1.png"
        self.image.write_bytes(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aP1sAAAAASUVORK5CYII="))
        self.audio = self.root / "audio.wav"
        with wave.open(str(self.audio), "wb") as handle:
            handle.setnchannels(1)
            handle.setsampwidth(2)
            handle.setframerate(16000)
            handle.writeframes(b"\x00\x00" * 37920)
        self.manifest = {"schema_version": 1, "reading_direction": "left-to-right", "pages": [
            {"id": "P001", "file": self.image.name, "status": "narrative", "reviewed": True,
             "sha256": MODULE.sha256(self.image), "panels": [
                 {"id": "Q01", "bbox": [0, 0, .5, 1], "legibility_reviewed": True},
                 {"id": "Q02", "bbox": [.5, 0, 1, 1], "legibility_reviewed": True}]}]}
        self.script = {"schema_version": 1, "reading_direction": "left-to-right", "beats": [
            {"id": "B1", "narration": "Ele atravessa o portão.", "page_id": "P001", "panel_id": "Q01"},
            {"id": "B2", "narration": "Então para.", "page_id": "P001", "panel_id": "Q02"}]}
        self.alignment = {"schema_version": 1, "method": "manual", "confirmed": True, "beats": [
            {"id": "B1", "start": 0, "end": 1}, {"id": "B2", "start": 1, "end": 2.37}]}
        self.manifest_path = self.root / "manifest.json"
        self.script_path = self.root / "script.json"
        self.align_path = self.root / "alignment.json"
        self.out = self.root / "plans/timeline.json"

    def inputs(self):
        for path, value in ((self.manifest_path, self.manifest), (self.script_path, self.script), (self.align_path, self.alignment)):
            path.write_text(json.dumps(value), encoding="utf-8")

    def build(self, **kwargs):
        self.inputs()
        if "alignment_path" not in kwargs and not kwargs.get("draft"):
            kwargs["alignment_path"] = self.align_path
        return MODULE.build_plan(self.manifest_path, self.script_path, self.audio, self.out, **kwargs)

    def analysis_inputs(self, *, root_hint="."):
        self.inputs()
        panels = {p["id"]: p for p in self.manifest["pages"][0]["panels"]}
        self.analysis = {"schema_version": 1, "kind": "manga-hq-editing-analysis",
                         "manifest": copy.deepcopy(self.manifest), "script": copy.deepcopy(self.script),
                         "source_fingerprints": {"manifest_sha256": MODULE.semantic_sha256(self.manifest),
                                                 "script_sha256": MODULE.semantic_sha256(self.script)},
                         "image_root": root_hint, "image_catalog": [],
                         "shots": [{"beat_id": beat["id"], "narration": beat["narration"],
                                    "page_id": beat["page_id"], "panel_id": beat["panel_id"],
                                    "file": self.image.name, "bbox": panels[beat["panel_id"]]["bbox"]}
                                   for beat in self.script["beats"]]}
        self.analysis_path = self.root / "editing-analysis.json"
        if "production_structure" in self.script:
            self.analysis["production_structure"] = copy.deepcopy(self.script["production_structure"])
        for key in ("visual_identity", "story_coverage"):
            if key in self.script:
                self.analysis[key] = copy.deepcopy(self.script[key])
        for shot, beat in zip(self.analysis["shots"], self.script["beats"]):
            if "section_id" in beat:
                shot["section_id"] = beat["section_id"]
        self.save_analysis()

    def save_analysis(self):
        self.analysis_path.write_text(json.dumps(self.analysis, ensure_ascii=False, indent=2), encoding="utf-8")

    def build_analysis(self, **kwargs):
        kwargs.setdefault("alignment_path", self.align_path)
        return MODULE.build_from_analysis(self.analysis_path, self.audio, self.out, **kwargs)

    def test_analysis_cli_real_audio_relative_media_and_no_duplicate_sources(self):
        self.analysis_inputs()
        # The handoff embeds all evidence; external manifest/script are optional.
        self.manifest_path.unlink()
        self.script_path.unlink()
        original = self.analysis_path.read_bytes()
        result = subprocess.run([sys.executable, str(SCRIPT), "--analysis", str(self.analysis_path),
                                 "--audio", str(self.audio), "--alignment", str(self.align_path),
                                 "--output", str(self.out)], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = json.loads(self.out.read_text(encoding="utf-8"))
        self.assertTrue(plan["renderable"])
        self.assertEqual(plan["total_frames"], 72)
        self.assertEqual(plan["sources"], {"analysis_sha256": MODULE.sha256(self.analysis_path),
                                         "manifest_semantic_sha256": MODULE.semantic_sha256(self.manifest),
                                         "script_semantic_sha256": MODULE.semantic_sha256(self.script)})
        self.assertEqual((self.out.parent/plan["beats"][0]["image"]).resolve(), self.image.resolve())
        self.assertEqual(self.analysis_path.read_bytes(), original)
        self.assertFalse(self.manifest_path.exists())
        self.assertFalse(self.script_path.exists())

    def test_legacy_cli_still_accepts_manifest_and_script(self):
        self.inputs()
        result = subprocess.run([sys.executable, str(SCRIPT), "--manifest", str(self.manifest_path),
                                 "--script", str(self.script_path), "--audio", str(self.audio),
                                 "--alignment", str(self.align_path), "--output", str(self.out)],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(self.out.read_text(encoding="utf-8"))["sources"],
                         {"manifest_sha256": MODULE.sha256(self.manifest_path),
                          "script_sha256": MODULE.sha256(self.script_path)})

    def test_analysis_rejects_changed_embedded_sources_and_missing_hash(self):
        self.analysis_inputs()
        original = copy.deepcopy(self.analysis)
        for source, field in (("manifest", "reading_direction"), ("script", "reading_direction")):
            with self.subTest(source=source):
                self.analysis = copy.deepcopy(original)
                self.analysis[source][field] = "right-to-left"
                self.save_analysis()
                with self.assertRaisesRegex(MODULE.TimelineError, "fingerprint"):
                    self.build_analysis()
        self.analysis = original
        self.analysis["source_fingerprints"].pop("script_sha256")
        self.save_analysis()
        with self.assertRaisesRegex(MODULE.TimelineError, "fingerprint"):
            self.build_analysis()

    def test_analysis_rejects_tampered_or_duplicate_shot_links(self):
        self.analysis_inputs()
        original = copy.deepcopy(self.analysis)
        for field, value in (("file", "other.png"), ("page_id", "P002"), ("panel_id", "Q02"),
                             ("narration", "Outra narração."), ("bbox", [0, 0, 1, 1])):
            with self.subTest(field=field):
                self.analysis = copy.deepcopy(original)
                self.analysis["shots"][0][field] = value
                self.save_analysis()
                with self.assertRaisesRegex(MODULE.TimelineError, f"shot {field}"):
                    self.build_analysis()
        self.analysis = copy.deepcopy(original)
        self.analysis["shots"][1]["beat_id"] = "B1"
        self.save_analysis()
        with self.assertRaisesRegex(MODULE.TimelineError, "Shot duplicado"):
            self.build_analysis()
        self.analysis["shots"].pop()
        self.save_analysis()
        with self.assertRaisesRegex(MODULE.TimelineError, "exatamente um shot"):
            self.build_analysis()

    def test_analysis_portable_after_project_folder_is_moved(self):
        self.analysis_inputs(root_hint="../images")
        handoff = self.root / "handoff"
        handoff.mkdir()
        images = self.root / "images"
        images.mkdir()
        self.image.rename(images/self.image.name)
        self.analysis_path.rename(handoff/self.analysis_path.name)
        moved = self.root / "moved-project"
        moved.mkdir()
        shutil.move(str(handoff), str(moved/handoff.name))
        shutil.move(str(images), str(moved/images.name))
        self.analysis_path = moved / "handoff/editing-analysis.json"
        plan = self.build_analysis()
        self.assertEqual((self.out.parent/plan["beats"][0]["image"]).resolve(),
                         (moved/images.name/self.image.name).resolve())

    def test_analysis_explicit_image_root_relocation_verifies_checksums(self):
        self.analysis_inputs(root_hint="missing-folder")
        relocated = self.root / "relocated-images"
        relocated.mkdir()
        shutil.copyfile(self.image, relocated/self.image.name)
        (relocated/self.image.name).write_bytes(b"a different image")
        with self.assertRaisesRegex(MODULE.TimelineError, "checksum"):
            self.build_analysis(image_root=relocated)
        shutil.copyfile(self.image, relocated/self.image.name)
        plan = self.build_analysis(image_root=relocated)
        self.assertEqual((self.out.parent/plan["beats"][0]["image"]).resolve(),
                         (relocated/self.image.name).resolve())

    def test_analysis_null_root_requires_explicit_override(self):
        self.analysis_inputs(root_hint=None)
        with self.assertRaisesRegex(MODULE.TimelineError, "informe --image-root"):
            self.build_analysis()
        self.assertTrue(self.build_analysis(image_root=self.root)["renderable"])

    def test_analysis_catalog_search_hints_do_not_change_confirmed_selection(self):
        self.analysis_inputs()
        self.analysis["image_catalog"] = [{"page_id": "P002", "file": "missing.png",
                                          "description": "Perfect semantic match"}]
        self.analysis["shots"].reverse()
        self.analysis["shots"][0]["motion"] = {"from_scale": 9, "to_scale": 9}
        self.save_analysis()
        plan = self.build_analysis()
        self.assertEqual([beat["id"] for beat in plan["beats"]], ["B1", "B2"])
        self.assertEqual(plan["beats"][0]["panel_id"], "Q01")
        self.assertEqual(plan["beats"][0]["motion"], {"from_scale": 1, "to_scale": 1.8})

    def test_analysis_reuses_evidence_legibility_and_alignment_checks(self):
        self.analysis_inputs()
        self.analysis["manifest"]["pages"][0]["reviewed"] = False
        self.analysis["source_fingerprints"]["manifest_sha256"] = MODULE.semantic_sha256(self.analysis["manifest"])
        self.save_analysis()
        with self.assertRaisesRegex(MODULE.TimelineError, "reviewed=true"):
            self.build_analysis()
        self.analysis["manifest"]["pages"][0]["reviewed"] = True
        self.analysis["source_fingerprints"]["manifest_sha256"] = MODULE.semantic_sha256(self.analysis["manifest"])
        self.save_analysis()
        self.alignment["confirmed"] = False
        self.align_path.write_text(json.dumps(self.alignment), encoding="utf-8")
        with self.assertRaisesRegex(MODULE.TimelineError, "não confirmado"):
            self.build_analysis()

    def test_analysis_declared_legibility_preserves_source_and_records_effective_hash(self):
        self.analysis_inputs()
        for panel in self.analysis["manifest"]["pages"][0]["panels"]:
            panel.pop("legibility_reviewed")
        self.analysis["source_fingerprints"]["manifest_sha256"] = MODULE.semantic_sha256(self.analysis["manifest"])
        self.save_analysis()
        original = self.analysis_path.read_bytes()
        with self.assertRaisesRegex(MODULE.TimelineError, "legibility_reviewed"):
            self.build_analysis()
        plan = self.build_analysis(confirm_legibility=True)
        effective = copy.deepcopy(self.script)
        for beat in effective["beats"]:
            beat["legibility_reviewed"] = True
        self.assertTrue(plan["renderable"])
        self.assertEqual(plan["sources"]["legibility_confirmation"], "declared-after-editorial-review")
        self.assertEqual(plan["sources"]["script_semantic_sha256"], MODULE.semantic_sha256(self.script))
        self.assertEqual(plan["sources"]["effective_script_semantic_sha256"], MODULE.semantic_sha256(effective))
        self.assertEqual(self.analysis_path.read_bytes(), original)

    def test_legibility_confirmation_never_confirms_audio_alignment(self):
        self.analysis_inputs()
        self.alignment["confirmed"] = False
        self.align_path.write_text(json.dumps(self.alignment), encoding="utf-8")
        with self.assertRaisesRegex(MODULE.TimelineError, "não confirmado"):
            self.build_analysis(confirm_legibility=True)
        with self.assertRaisesRegex(MODULE.TimelineError, "Forneça --alignment"):
            self.build_analysis(confirm_legibility=True, alignment_path=None)
        result = subprocess.run([sys.executable, str(SCRIPT), "--manifest", str(self.manifest_path),
                                 "--script", str(self.script_path), "--audio", str(self.audio),
                                 "--output", str(self.out), "--confirm-legibility"],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--confirm-legibility exige --analysis", result.stderr)

    def test_analysis_rejects_schema_mismatch_and_cli_source_mix(self):
        self.analysis_inputs()
        self.analysis["schema_version"] = True
        self.save_analysis()
        with self.assertRaisesRegex(MODULE.TimelineError, "schema_version"):
            self.build_analysis()
        result = subprocess.run([sys.executable, str(SCRIPT), "--analysis", str(self.analysis_path),
                                 "--script", str(self.script_path), "--audio", str(self.audio),
                                 "--output", str(self.out)], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 2)
        self.assertIn("não combine", result.stderr)

    def production_script(self):
        self.script["production_structure"] = {
            "advertisements": False, "sections": [
                {"id": "gancho", "kind": "hook", "goal": "Abrir com uma pergunta.", "beats": ["B1"]},
                {"id": "vinheta", "kind": "intro", "goal": "Vinheta do canal.", "beats": [],
                 "narrated": False, "estimated_duration_seconds": 3},
                {"id": "cta", "kind": "cta", "goal": "Convidar comentário.", "beats": ["B2"]},
                {"id": "outro", "kind": "outro", "beats": [], "narrated": False}]}
        self.script["beats"][0]["section_id"] = "gancho"
        self.script["beats"][1]["section_id"] = "cta"

    def test_analysis_structure_preserved_without_creating_module_timestamps_or_images(self):
        self.production_script()
        self.analysis_inputs()
        original = self.analysis_path.read_bytes()
        plan = self.build_analysis()
        self.assertEqual(plan["production_structure"], self.script["production_structure"])
        self.assertEqual([beat["section_id"] for beat in plan["beats"]], ["gancho", "cta"])
        self.assertEqual([beat["id"] for beat in plan["beats"]], ["B1", "B2"])
        self.assertEqual([beat["panel_id"] for beat in plan["beats"]], ["Q01", "Q02"])
        self.assertEqual(plan["total_frames"], 72)
        self.assertEqual(plan["beats"][0]["end_frame"], 30)
        self.assertEqual(plan["beats"][1]["start_frame"], 30)
        self.assertEqual(plan["beats"][1]["end_frame"], 72)
        self.assertTrue(all("start" not in section and "end" not in section
                            for section in plan["production_structure"]["sections"]))
        self.assertTrue(any("composição posterior" in limitation for limitation in plan["limitations"]))
        self.assertEqual(self.analysis_path.read_bytes(), original)
        plan["production_structure"]["sections"][1]["goal"] = "Mudou."
        self.assertEqual(self.script["production_structure"]["sections"][1]["goal"], "Vinheta do canal.")

    def test_legacy_path_optional_structure_and_old_projects_remain_compatible(self):
        self.production_script()
        plan = self.build()
        self.assertEqual(plan["production_structure"], self.script["production_structure"])
        self.assertEqual(plan["beats"][0]["section_id"], "gancho")
        self.out = self.root / "plans/legacy.json"
        self.script.pop("production_structure")
        for beat in self.script["beats"]:
            beat.pop("section_id")
        legacy = self.build()
        self.assertNotIn("production_structure", legacy)
        self.assertTrue(all("section_id" not in beat for beat in legacy["beats"]))

    def test_analysis_rejects_structure_or_section_link_divergence(self):
        self.production_script()
        self.analysis_inputs()
        original = copy.deepcopy(self.analysis)
        for edit in ("missing-structure", "changed-structure", "missing-section", "changed-section"):
            with self.subTest(edit=edit):
                self.analysis = copy.deepcopy(original)
                if edit == "missing-structure":
                    self.analysis.pop("production_structure")
                elif edit == "changed-structure":
                    self.analysis["production_structure"]["sections"][1]["goal"] = "Outra vinheta."
                elif edit == "missing-section":
                    self.analysis["shots"][0].pop("section_id")
                else:
                    self.analysis["shots"][0]["section_id"] = "cta"
                self.save_analysis()
                with self.assertRaisesRegex(MODULE.TimelineError, "production_structure|shot section_id"):
                    self.build_analysis()

    def test_bad_production_sections_and_conflicting_links_rejected_before_media_planning(self):
        self.production_script()
        original = copy.deepcopy(self.script)
        for value in (None, [], {}, {"sections": [None]},
                      {"sections": [{"id": "gancho", "kind": ""}]},
                      {"sections": [{"id": "gancho", "kind": "hook", "beats": ["missing"]}]},
                      {"sections": [{"id": "gancho", "kind": "hook", "beats": []}]}):
            with self.subTest(value=value):
                self.script = copy.deepcopy(original)
                self.script["production_structure"] = value
                with self.assertRaises(MODULE.TimelineError):
                    self.build()
        self.script = copy.deepcopy(original)
        self.script["production_structure"]["sections"][1]["beats"] = ["B1"]
        with self.assertRaisesRegex(MODULE.TimelineError, "mais de uma"):
            self.build()
        self.script = copy.deepcopy(original)
        self.script["beats"][0]["section_id"] = "missing"
        with self.assertRaisesRegex(MODULE.TimelineError, "section_id"):
            self.build()
        self.script.pop("production_structure")
        with self.assertRaisesRegex(MODULE.TimelineError, "section_id exige"):
            self.build()

    def test_ad_sections_rejected_but_channel_cta_does_not_change_alignment_confirmation(self):
        self.production_script()
        original = copy.deepcopy(self.script)
        for kind in ("ad", "advertisement", "sponsor", "sponsorship", "commercial", "promotion"):
            with self.subTest(kind=kind):
                self.script = copy.deepcopy(original)
                self.script["production_structure"]["sections"][1]["kind"] = kind
                with self.assertRaisesRegex(MODULE.TimelineError, "publicidade"):
                    self.build()
        self.script = original
        self.alignment["confirmed"] = False
        with self.assertRaisesRegex(MODULE.TimelineError, "não confirmado"):
            self.build()
        draft = self.build(draft=True)
        self.assertFalse(draft["renderable"])
        self.assertEqual(draft["production_structure"], self.script["production_structure"])

    def test_real_wav_frame_contiguous_plan_and_relative_paths(self):
        plan = self.build()
        self.assertEqual(plan["readiness"], "ready")
        self.assertTrue(plan["renderable"])
        self.assertEqual(plan["canvas"]["fps"], "30000/1001")
        self.assertEqual(plan["total_frames"], 72)
        self.assertGreaterEqual(plan["duration_seconds"], 2.37)
        self.assertLess(plan["duration_seconds"]-2.37, 1001/30000)
        first, last = plan["beats"]
        self.assertEqual(first["start_frame"], 0)
        self.assertEqual(first["end_frame"], last["start_frame"])
        self.assertEqual(last["end_frame"], 72)
        self.assertEqual(first["motion"], {"from_scale": 1, "to_scale": 1.8})
        self.assertEqual(last["motion"], {"from_scale": 1.8, "to_scale": 1})
        self.assertEqual((self.out.parent/first["image"]).resolve(), self.image.resolve())
        self.assertEqual((self.out.parent/plan["audio"]["file"]).resolve(), self.audio.resolve())
        self.assertEqual(plan["audio"]["stream_index"], 0)

    def test_motion_outside_renderer_range_rejected(self):
        self.script["beats"][0]["motion"] = {"from_scale": 1, "to_scale": 3}
        with self.assertRaisesRegex(MODULE.TimelineError, "2.5"):
            self.build()

    def test_unconfirmed_alignment_rejected(self):
        self.alignment["confirmed"] = False
        with self.assertRaisesRegex(MODULE.TimelineError, "não confirmado"):
            self.build()

    def test_alignment_list_needs_explicit_confirmation(self):
        self.alignment = self.alignment["beats"]
        with self.assertRaisesRegex(MODULE.TimelineError, "não confirmado"):
            self.build()
        self.assertTrue(self.build(confirm_alignment=True)["renderable"])

    def test_gap_rejected(self):
        self.alignment["beats"][1]["start"] = 1.1
        with self.assertRaisesRegex(MODULE.TimelineError, "lacuna"):
            self.build()

    def test_overlap_rejected(self):
        self.alignment["beats"][1]["start"] = .9
        with self.assertRaisesRegex(MODULE.TimelineError, "sobreposição"):
            self.build()

    def test_tail_audio_not_covered_rejected(self):
        self.alignment["beats"][1]["end"] = 2
        with self.assertRaisesRegex(MODULE.TimelineError, "Última marca"):
            self.build()

    def test_leading_audio_not_covered_rejected(self):
        self.alignment["beats"][0]["start"] = .2
        with self.assertRaisesRegex(MODULE.TimelineError, "frame 0"):
            self.build()

    def test_alignment_wrong_order_rejected(self):
        self.alignment["beats"].reverse()
        with self.assertRaisesRegex(MODULE.TimelineError, "IDs/ordem"):
            self.build()

    def test_nonfinite_alignment_rejected(self):
        self.alignment["beats"][0]["end"] = float("nan")
        with self.assertRaisesRegex(MODULE.TimelineError, "finito"):
            self.build()

    def test_draft_estimates_are_explicitly_nonrenderable(self):
        plan = self.build(draft=True)
        self.assertEqual(plan["readiness"], "draft")
        self.assertFalse(plan["renderable"])
        self.assertEqual(plan["alignment"]["method"], "estimated-word-count")
        self.assertFalse(plan["alignment"]["confirmed"])
        self.assertEqual(plan["beats"][0]["end_frame"], plan["beats"][1]["start_frame"])
        self.assertEqual(plan["beats"][-1]["end_frame"], plan["total_frames"])

    def test_no_alignment_no_draft_rejected(self):
        with self.assertRaisesRegex(MODULE.TimelineError, "Forneça --alignment"):
            self.build(alignment_path=None)

    def test_missing_page_panel_image_audio_rejected(self):
        for field, value, pattern in (("page_id", "missing", "page_id"), ("panel_id", "missing", "panel_id")):
            with self.subTest(field=field):
                original = self.script["beats"][0][field]
                self.script["beats"][0][field] = value
                with self.assertRaisesRegex(MODULE.TimelineError, pattern):
                    self.build()
                self.script["beats"][0][field] = original
        self.image.unlink()
        with self.assertRaisesRegex(MODULE.TimelineError, "imagem inexistente"):
            self.build()
        self.image.write_bytes(b"image")
        self.manifest["pages"][0].pop("sha256")
        self.audio.unlink()
        with self.assertRaisesRegex(MODULE.TimelineError, "Áudio inexistente"):
            self.build()

    def test_advertisement_and_unreviewed_page_rejected(self):
        self.manifest["pages"][0]["status"] = "advertisement"
        with self.assertRaisesRegex(MODULE.TimelineError, "narrative"):
            self.build()
        self.manifest["pages"][0]["status"] = "narrative"
        self.manifest["pages"][0]["reviewed"] = False
        with self.assertRaisesRegex(MODULE.TimelineError, "reviewed=true"):
            self.build()

    def test_strong_motion_needs_crop_legibility_review(self):
        self.manifest["pages"][0]["panels"][0].pop("legibility_reviewed")
        with self.assertRaisesRegex(MODULE.TimelineError, "legibility_reviewed"):
            self.build()
        self.script["beats"][0]["legibility_reviewed"] = True
        self.assertTrue(self.build()["renderable"])

    def test_bbox_and_changed_source_rejected(self):
        self.manifest["pages"][0]["panels"][0]["bbox"] = [.6, 0, .5, 1]
        with self.assertRaisesRegex(MODULE.TimelineError, "bbox"):
            self.build()
        self.manifest["pages"][0]["panels"][0]["bbox"] = [0, 0, .5, 1]
        self.image.write_bytes(b"changed source")
        with self.assertRaisesRegex(MODULE.TimelineError, "checksum"):
            self.build()

    def test_duplicate_beats_and_boolean_schema_rejected(self):
        self.script["beats"][1]["id"] = "B1"
        with self.assertRaisesRegex(MODULE.TimelineError, "duplicado"):
            self.build()
        self.script["beats"][1]["id"] = "B2"
        self.script["schema_version"] = True
        with self.assertRaisesRegex(MODULE.TimelineError, "schema_version"):
            self.build()

    def test_output_not_overwritten(self):
        self.build()
        original = self.out.read_bytes()
        with self.assertRaisesRegex(MODULE.TimelineError, "já existe"):
            self.build()
        self.assertEqual(self.out.read_bytes(), original)

    def test_path_escape_rejected(self):
        self.manifest["pages"][0]["file"] = "../outside.png"
        with self.assertRaisesRegex(MODULE.TimelineError, "sai do image_root"):
            self.build()

    def test_multi_audio_requires_absolute_audio_index(self):
        probe = {"streams": [{"index": 0, "codec_type": "video"},
                             {"index": 1, "codec_type": "audio", "duration": "2.37"},
                             {"index": 2, "codec_type": "audio", "duration": "2.37"}]}
        completed = subprocess.CompletedProcess([], 0, json.dumps(probe), "")
        with patch.object(MODULE.subprocess, "run", return_value=completed):
            with self.assertRaisesRegex(MODULE.TimelineError, "várias faixas"):
                MODULE.probe_audio(self.audio)
            with self.assertRaisesRegex(MODULE.TimelineError, "não corresponde"):
                MODULE.probe_audio(self.audio, 0)
            self.assertEqual(MODULE.probe_audio(self.audio, 2)["stream_index"], 2)

    def test_explicit_color_and_motion_preserved(self):
        self.script["beats"][0].update(color_mode="original", motion={"from_scale": 1, "to_scale": 1.2}, focal_point=[.25, .5])
        plan = self.build()
        self.assertEqual(plan["beats"][0]["color_mode"], "original")
        self.assertEqual(plan["beats"][0]["motion"]["to_scale"], 1.2)
        self.assertEqual(plan["beats"][0]["focal_point"], [.25, .5])

    def visual_script(self, *, file=None):
        self.script["visual_identity"] = {
            "work_title": "Gotham: identidade editorial", "genre": "noir psicológico",
            "palette": ["#161A22", "#D4B782"], "background": {
                "mode": "image", "file": file or self.image.name,
                "sha256": MODULE.sha256(self.image), "darkness": .2,
                "zoom_from": 1, "zoom_to": 1.04}}

    def test_original_art_default_and_explicit_cyan_override(self):
        self.script["beats"][1]["color_mode"] = "manga_cyan"
        plan = self.build()
        self.assertEqual(plan["profile"], "comic-identity-longform-v1")
        self.assertEqual(plan["beats"][0]["color_mode"], "original")
        self.assertEqual(plan["beats"][1]["color_mode"], "manga_cyan")
        self.assertNotIn("visual_identity", plan)

    def test_legacy_identity_asset_resolves_against_script_directory_not_manifest(self):
        scripts = self.root / "editorial"
        scripts.mkdir()
        self.script_path = scripts / "script.json"
        self.visual_script(file="../page 1.png")
        original = copy.deepcopy(self.script)
        plan = self.build()
        identity = plan["visual_identity"]
        self.assertEqual((self.out.parent/identity["background"]["file"]).resolve(), self.image.resolve())
        self.assertEqual(identity["background"]["sha256"], MODULE.sha256(self.image))
        self.assertEqual(identity["genre"], "noir psicológico")
        self.assertEqual(self.script, original)
        self.assertEqual(json.loads(self.script_path.read_text(encoding="utf-8")), original)

    def test_analysis_identity_asset_and_root_remain_portable_after_folder_move(self):
        self.visual_script()
        self.analysis_inputs(root_hint="../images")
        self.analysis["visual_identity_root"] = "../images"
        self.save_analysis()
        handoff, images = self.root/"handoff", self.root/"images"
        handoff.mkdir()
        images.mkdir()
        self.image.rename(images/self.image.name)
        self.analysis_path.rename(handoff/self.analysis_path.name)
        moved = self.root/"moved-project"
        moved.mkdir()
        shutil.move(str(handoff), str(moved/handoff.name))
        shutil.move(str(images), str(moved/images.name))
        self.analysis_path = moved/"handoff/editing-analysis.json"
        original = self.analysis_path.read_bytes()
        plan = self.build_analysis()
        actual = (self.out.parent/plan["visual_identity"]["background"]["file"]).resolve()
        self.assertEqual(actual, (moved/"images"/self.image.name).resolve())
        self.assertEqual(plan["sources"]["script_semantic_sha256"], MODULE.semantic_sha256(self.script))
        self.assertEqual(self.analysis_path.read_bytes(), original)

    def test_analysis_null_identity_root_requires_explicit_relocation(self):
        self.visual_script()
        self.analysis_inputs()
        self.analysis["visual_identity_root"] = None
        self.save_analysis()
        with self.assertRaisesRegex(MODULE.TimelineError, "--visual-identity-root"):
            self.build_analysis()
        relocated = self.root/"new assets"
        relocated.mkdir()
        shutil.copyfile(self.image, relocated/self.image.name)
        plan = self.build_analysis(visual_identity_root=relocated)
        self.assertEqual((self.out.parent/plan["visual_identity"]["background"]["file"]).resolve(),
                         (relocated/self.image.name).resolve())

    def test_missing_identity_root_field_resolves_next_to_legacy_analysis(self):
        self.visual_script()
        self.analysis_inputs()
        plan = self.build_analysis()
        self.assertEqual((self.out.parent/plan["visual_identity"]["background"]["file"]).resolve(),
                         self.image.resolve())

    def test_absolute_identity_asset_does_not_require_root_guess(self):
        self.visual_script(file=str(self.image.resolve()))
        self.analysis_inputs()
        self.analysis["visual_identity_root"] = None
        self.save_analysis()
        self.assertTrue(self.build_analysis()["renderable"])

    def test_background_override_cli_records_provenance_without_mutating_source(self):
        self.visual_script(file="missing-original.png")
        self.analysis_inputs()
        self.analysis["visual_identity_root"] = None
        self.save_analysis()
        original = self.analysis_path.read_bytes()
        result = subprocess.run([sys.executable, str(SCRIPT), "--analysis", str(self.analysis_path),
                                 "--audio", str(self.audio), "--alignment", str(self.align_path),
                                 "--background-image", str(self.image), "--output", str(self.out)],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = json.loads(self.out.read_text(encoding="utf-8"))
        self.assertTrue(plan["renderable"])
        self.assertEqual(plan["sources"]["background_override"]["sha256"], MODULE.sha256(self.image))
        self.assertEqual(plan["sources"]["effective_visual_identity_sha256"],
                         MODULE.semantic_sha256(plan["visual_identity"]))
        self.assertEqual(plan["sources"]["script_semantic_sha256"], MODULE.semantic_sha256(self.script))
        self.assertEqual(self.analysis_path.read_bytes(), original)
        self.assertEqual(plan["visual_identity"]["work_title"], self.script["visual_identity"]["work_title"])

    def replacement_background(self):
        def chunk(name, data):
            return struct.pack(">I", len(data)) + name + data + struct.pack(">I", zlib.crc32(name+data))
        asset = self.root/"new background.png"
        data = b"\x89PNG\r\n\x1a\n"
        data += chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 2, 0, 0, 0))
        data += chunk(b"IDAT", zlib.compress((b"\0"+b"\x18\x20\x28"*2)*2))
        data += chunk(b"IEND", b"")
        asset.write_bytes(data)
        return asset

    def test_background_override_keeps_reviewed_image_controls_and_replaces_checksum(self):
        replacement = self.replacement_background()
        self.visual_script()
        self.script["visual_identity"]["background"].update(darkness=.05, zoom_from=1, zoom_to=1.02)
        self.analysis_inputs()
        original = self.analysis_path.read_bytes()
        plan = self.build_analysis(background_image=replacement)
        background = plan["visual_identity"]["background"]
        self.assertEqual(background["darkness"], .05)
        self.assertEqual(background["zoom_from"], 1)
        self.assertEqual(background["zoom_to"], 1.02)
        self.assertEqual((self.out.parent/background["file"]).resolve(), replacement.resolve())
        self.assertEqual(background["sha256"], MODULE.sha256(replacement))
        self.assertNotEqual(background["sha256"], MODULE.sha256(self.image))
        self.assertEqual(plan["sources"]["background_override"]["sha256"], background["sha256"])
        self.assertEqual(plan["sources"]["script_semantic_sha256"], MODULE.semantic_sha256(self.script))
        self.assertEqual(self.analysis_path.read_bytes(), original)

    def test_ambient_override_keeps_shared_darkness_and_external_identity_metadata(self):
        replacement = self.replacement_background()
        self.script["visual_identity"] = {"genre": "noir", "palette": ["#161A22", "#D4B782"],
                                         "background": {"mode": "ambient", "darkness": .05,
                                                        "palette": ["#161A22", "#242A34"]}}
        self.analysis_inputs()
        original = self.analysis_path.read_bytes()
        plan = self.build_analysis(background_image=replacement)
        identity = plan["visual_identity"]
        self.assertEqual(identity["background"]["darkness"], .05)
        self.assertEqual(identity["palette"], self.script["visual_identity"]["palette"])
        self.assertEqual(identity["genre"], "noir")
        self.assertNotIn("palette", identity["background"])
        self.assertNotIn("zoom_from", identity["background"])
        self.assertNotIn("zoom_to", identity["background"])
        self.assertEqual(self.analysis_path.read_bytes(), original)
        # With no prior image controls, the renderer's image defaults apply.
        self.script.pop("visual_identity")
        self.out = self.root/"plans/default-background.json"
        defaults = self.build(background_image=replacement)["visual_identity"]["background"]
        self.assertEqual(set(defaults), {"mode", "file", "sha256"})

    def test_background_override_cannot_hide_invalid_original_image_controls(self):
        replacement = self.replacement_background()
        for key, value in (("darkness", .9), ("zoom_to", 2), ("sha256", "invalid")):
            with self.subTest(key=key):
                self.visual_script()
                self.script["visual_identity"]["background"][key] = value
                with self.assertRaisesRegex(MODULE.TimelineError, key):
                    self.build(background_image=replacement)

    def test_changed_identity_checksum_and_missing_background_rejected(self):
        self.visual_script()
        self.script["visual_identity"]["background"]["sha256"] = "0"*64
        with self.assertRaisesRegex(MODULE.TimelineError, "checksum diferente"):
            self.build()
        self.script["visual_identity"]["background"].update(file="missing.png", sha256=MODULE.sha256(self.image))
        with self.assertRaisesRegex(MODULE.TimelineError, "Fundo de identidade inexistente"):
            self.build()

    def test_identity_background_output_collision_and_unsupported_format_rejected(self):
        asset = self.root/"future.json"
        asset.write_bytes(self.image.read_bytes())
        self.visual_script(file=asset.name)
        with self.assertRaisesRegex(MODULE.TimelineError, "formato suportado"):
            self.build()
        self.visual_script()
        self.out = self.image
        with self.assertRaisesRegex(MODULE.TimelineError, "coincide com uma fonte"):
            self.build()

    def test_identity_metadata_mismatch_and_invalid_controls_rejected(self):
        self.visual_script()
        self.analysis_inputs()
        self.analysis["visual_identity"]["genre"] = "Outra obra"
        self.save_analysis()
        with self.assertRaisesRegex(MODULE.TimelineError, "visual_identity da análise"):
            self.build_analysis()
        for value in (None, [], {"background": None}, {"background": {}},
                      {"background": {"mode": "blue-shapes"}},
                      {"background": {"mode": "image", "file": ""}},
                      {"background": {"mode": "image", "file": self.image.name, "sha256": "invalid"}},
                      {"background": {"mode": "image", "file": self.image.name, "zoom_to": 2}},
                      {"background": {"mode": "ambient", "darkness": float("nan")}},
                      {"background": {"mode": "ambient", "palette": ["#fff", "#000"]}}):
            with self.subTest(value=value):
                self.script["visual_identity"] = value
                with self.assertRaises(MODULE.TimelineError):
                    self.build()

    def test_ambient_identity_preserves_work_palette_and_editorial_metadata(self):
        self.script["visual_identity"] = {"genre": "aventura", "reference_panels": ["P001/Q01"],
                                         "background": {"mode": "ambient", "palette": ["#161A22", "#D4B782"],
                                                        "darkness": .1}}
        plan = self.build()
        self.assertEqual(plan["visual_identity"], self.script["visual_identity"])
        plan["visual_identity"]["reference_panels"].append("P002/Q01")
        self.assertEqual(self.script["visual_identity"]["reference_panels"], ["P001/Q01"])

    def test_planning_duration_and_complete_story_metadata_never_replace_real_audio(self):
        self.script["story_coverage"] = {"scope": "complete", "reviewed": True, "included_pages": ["P001"]}
        self.analysis_inputs()
        estimate = {"kind": "planning-estimate", "timestamps_confirmed": False,
                    "target_minutes": [10, 30], "estimated_narration_seconds": 1200,
                    "word_count": 2960, "assumed_words_per_minute": 148}
        self.analysis["duration_estimate"] = estimate
        self.save_analysis()
        plan = self.build_analysis()
        self.assertEqual(plan["duration_estimate"], estimate)
        self.assertEqual(plan["story_coverage"], self.script["story_coverage"])
        self.assertEqual(plan["total_frames"], 72)
        self.assertLess(plan["duration_seconds"], 2.41)
        self.assertEqual(plan["alignment"]["method"], "manual")
        self.assertTrue(any("áudio real" in line for line in plan["limitations"]))

    def test_planning_metadata_mismatch_or_timestamp_claim_rejected(self):
        self.script["story_coverage"] = {"scope": "complete", "included_pages": ["P001"]}
        self.analysis_inputs()
        self.analysis["story_coverage"]["included_pages"] = []
        self.save_analysis()
        with self.assertRaisesRegex(MODULE.TimelineError, "story_coverage"):
            self.build_analysis()
        self.analysis["story_coverage"] = copy.deepcopy(self.script["story_coverage"])
        self.analysis["duration_estimate"] = {"kind": "planning-estimate", "timestamps_confirmed": True}
        self.save_analysis()
        with self.assertRaisesRegex(MODULE.TimelineError, "timestamps_confirmed=false"):
            self.build_analysis()


if __name__ == "__main__":
    unittest.main()
