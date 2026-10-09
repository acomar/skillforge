import base64
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import wave

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


if __name__ == "__main__":
    unittest.main()
