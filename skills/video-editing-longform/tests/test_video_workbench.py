"""Real FFmpeg integration checks; skipped explicitly when tools are unavailable."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "video_workbench.py"
SPEC = importlib.util.spec_from_file_location("longform_workbench", SCRIPT)
assert SPEC and SPEC.loader
workbench = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(workbench)
TOOLS_AVAILABLE = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))
TEST_TEMP = Path(os.environ.get("VIDEO_WORKBENCH_TEST_TMP", str(Path.cwd()))).resolve()


@unittest.skipUnless(TOOLS_AVAILABLE, "FFmpeg and FFprobe are required for integration tests")
class VideoWorkbenchIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        TEST_TEMP.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(prefix="video tests ação ", dir=TEST_TEMP)
        cls.root = Path(cls.temporary.name)
        cls.source = cls.root / "origem com espaços ação.mp4"
        cls.generate(cls.source)
        cls.source_digest = hashlib.sha256(cls.source.read_bytes()).hexdigest()

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    @staticmethod
    def generate(target, first_color="red"):
        command = [shutil.which("ffmpeg"), "-hide_banner", "-loglevel", "error", "-nostdin",
                   "-f", "lavfi", "-i", f"color=c={first_color}:s=160x90:r=25:d=2",
                   "-f", "lavfi", "-i", "color=c=blue:s=160x90:r=25:d=2",
                   "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=4",
                   "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v]",
                   "-map", "[v]", "-map", "2:a", "-c:v", "mpeg4", "-q:v", "3", "-c:a", "aac",
                   "-y", str(target)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        if result.returncode:
            raise RuntimeError(result.stderr)

    def setUp(self):
        self.case = self.root / self._testMethodName
        self.case.mkdir()

    def cli(self, *args, expected=0):
        result = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def analysis_args(self, source=None):
        return ["analyze", source or self.source, "--workdir", self.case / "analysis",
                "--chunk-seconds", "1.5", "--overlap-seconds", "0.5", "--sample-seconds", "1"]

    def manifest(self):
        return json.loads((self.case / "analysis" / "analysis.json").read_text(encoding="utf-8"))

    def test_probe_unicode_and_input_preserved(self):
        target = self.case / "metadados.json"
        self.cli("probe", self.source, "--output", target)
        metadata = json.loads(target.read_text(encoding="utf-8"))
        self.assertAlmostEqual(metadata["facts"]["duration_seconds"], 4, places=2)
        self.assertEqual(metadata["facts"]["video_streams"][0]["width"], 160)
        self.assertEqual(len(metadata["facts"]["audio_streams"]), 1)
        self.assertEqual(hashlib.sha256(self.source.read_bytes()).hexdigest(), self.source_digest)

    def test_coverage_and_global_scene_timestamp(self):
        self.cli(*self.analysis_args())
        result = self.manifest()
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["chapter_count"], 3)
        chapters = result["chapters"]
        self.assertEqual(chapters[0]["start_seconds"], 0)
        self.assertAlmostEqual(chapters[-1]["end_seconds"], 4, places=2)
        self.assertEqual([chapter["end_seconds"] for chapter in chapters[:-1]],
                         [chapter["start_seconds"] for chapter in chapters[1:]])
        scenes = [scene for chapter in chapters for scene in chapter["scene_candidates"]]
        self.assertTrue(any(abs(scene["time_seconds"] - 2) < 0.05 for scene in scenes), scenes)
        self.assertEqual(sum(abs(scene["time_seconds"] - 2) < 0.05 for scene in scenes), 1)
        for chapter in chapters:
            self.assertTrue(chapter["stills"])
            for still in chapter["stills"]:
                self.assertGreater((self.case / "analysis" / still["path"]).stat().st_size, 0)
                self.assertGreaterEqual(still["requested_time_seconds"], chapter["start_seconds"])
                self.assertLess(still["requested_time_seconds"], chapter["end_seconds"])

    def test_resume_reuses_complete_hash_verified_chapters(self):
        self.cli(*self.analysis_args())
        original = self.manifest()
        root = self.case / "analysis"
        paths = [root / chapter["checkpoint"] for chapter in original["chapters"]]
        previous_mtimes = [path.stat().st_mtime_ns for path in paths]
        self.cli(*self.analysis_args(), "--resume")
        resumed = self.manifest()
        self.assertEqual(resumed["reused_chapters"], 3)
        self.assertEqual(resumed["processed_chapters"], 0)
        self.assertEqual([path.stat().st_mtime_ns for path in paths], previous_mtimes)

    def test_scene_on_chapter_boundary_is_assigned_once(self):
        self.cli(*self.analysis_args(), "--chunk-seconds", "2")
        chapters = self.manifest()["chapters"]
        self.assertEqual(len(chapters), 2)
        self.assertFalse(chapters[0]["scene_candidates"])
        candidates = chapters[1]["scene_candidates"]
        self.assertEqual(len(candidates), 1)
        self.assertAlmostEqual(candidates[0]["time_seconds"], 2, places=2)

    def test_changed_tool_version_invalidates_cache(self):
        self.cli(*self.analysis_args())
        first_key = self.manifest()["cache_key"]
        paths = workbench.tool_paths()
        changed = workbench.versions(paths, 10)
        changed["ffmpeg"]["version"] += " changed-test-build"
        args = workbench.parser().parse_args(list(map(str, self.analysis_args())) + ["--resume"])
        with mock.patch.object(workbench, "versions", return_value=changed):
            result = workbench.analyze(args, paths)
        self.assertNotEqual(first_key, result["cache_key"])
        self.assertEqual(result["reused_chapters"], 0)
        self.assertEqual(result["processed_chapters"], 3)

    def test_corrupt_artifact_reprocesses_only_its_chapter(self):
        self.cli(*self.analysis_args())
        original = self.manifest()
        root = self.case / "analysis"
        target = root / original["chapters"][1]["stills"][0]["path"]
        target.write_bytes(b"broken evidence")
        self.cli(*self.analysis_args(), "--resume")
        resumed = self.manifest()
        self.assertEqual(resumed["reused_chapters"], 2)
        self.assertEqual(resumed["processed_chapters"], 1)
        self.assertNotEqual(target.read_bytes(), b"broken evidence")

    def test_cache_invalidated_by_options_and_source_content(self):
        alternative = self.case / "mutable video.mp4"
        shutil.copyfile(self.source, alternative)
        self.cli(*self.analysis_args(alternative))
        first = self.manifest()["cache_key"]
        self.cli(*self.analysis_args(alternative), "--scene-threshold", "0.4", "--resume")
        second = self.manifest()["cache_key"]
        self.assertNotEqual(first, second)
        self.assertEqual(self.manifest()["reused_chapters"], 0)
        self.generate(alternative, first_color="green")
        self.cli(*self.analysis_args(alternative), "--scene-threshold", "0.4", "--resume")
        self.assertNotEqual(second, self.manifest()["cache_key"])
        self.assertEqual(self.manifest()["reused_chapters"], 0)

    def test_validation_fully_decodes_audio_video_and_checks_duration(self):
        report = self.case / "validacao.json"
        self.cli("validate", self.source, "--expected-duration", "4", "--tolerance", "0.05", "--report", report)
        payload = json.loads(report.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "passed")
        self.assertTrue(payload["checks"]["full_decode"])
        self.assertGreaterEqual(payload["decoded_video_frames"], 100)
        self.assertEqual(payload["editorial_audio"], "not_evaluated")
        mismatch = self.case / "duracao-errada.json"
        self.cli("validate", self.source, "--expected-duration", "9", "--report", mismatch, expected=1)
        failed = json.loads(mismatch.read_text(encoding="utf-8"))
        self.assertFalse(failed["checks"]["duration_matches"])
        self.assertTrue(failed["checks"]["full_decode"])

    def test_invalid_media_has_explicit_failure_report(self):
        invalid = self.case / "invalid.mp4"
        invalid.write_bytes(b"this is not a video")
        self.cli("probe", invalid, "--output", self.case / "probe.json", expected=1)
        self.assertFalse((self.case / "probe.json").exists())
        report = self.case / "failure.json"
        self.cli("validate", invalid, "--expected-duration", "4", "--report", report, expected=1)
        payload = json.loads(report.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "failed")
        self.assertFalse(payload["checks"]["full_decode"])
        self.assertIn("error", payload)

    def test_timeout_is_reported_without_false_validation(self):
        report = self.case / "timeout.json"
        self.cli("validate", self.source, "--expected-duration", "4", "--report", report,
                 "--timeout-seconds", "0.000001", expected=1)
        payload = json.loads(report.read_text(encoding="utf-8"))
        self.assertIn("exceeded", payload["error"])
        self.assertFalse(payload["checks"]["full_decode"])

    def test_reports_never_overwrite_input_or_existing_deliverables(self):
        self.cli("probe", self.source, "--output", self.source, expected=1)
        target = self.case / "existing.json"
        target.write_text("retain this", encoding="utf-8")
        self.cli("probe", self.source, "--output", target, expected=1)
        self.assertEqual(target.read_text(encoding="utf-8"), "retain this")
        self.assertEqual(hashlib.sha256(self.source.read_bytes()).hexdigest(), self.source_digest)

    def test_scene_failure_checkpoint_is_failed_and_resume_retries(self):
        arguments = workbench.parser().parse_args(list(map(str, self.analysis_args())))
        real_execute = workbench.execute

        def fail_scene(command, timeout, **kwargs):
            if "-vf" in command and "select=gt(scene" in command[command.index("-vf") + 1]:
                raise workbench.WorkbenchError("simulated FFmpeg scene failure")
            return real_execute(command, timeout, **kwargs)

        with mock.patch.object(workbench, "execute", side_effect=fail_scene):
            with self.assertRaisesRegex(workbench.WorkbenchError, "scene failure"):
                workbench.analyze(arguments, workbench.tool_paths())
        failed = self.manifest()
        self.assertEqual(failed["status"], "failed")
        checkpoints = list((self.case / "analysis" / "cache").rglob("checkpoint.json"))
        self.assertEqual(len(checkpoints), 1)
        checkpoint = json.loads(checkpoints[0].read_text(encoding="utf-8"))
        self.assertEqual(checkpoint["status"], "failed")
        self.assertEqual(checkpoint["failure_stage"], "scene_detection")
        self.cli(*self.analysis_args(), "--resume")
        self.assertEqual(self.manifest()["processed_chapters"], 3)
        self.assertEqual(self.manifest()["reused_chapters"], 0)


class BoundaryChecks(unittest.TestCase):
    def test_missing_tools_fail_explicitly(self):
        with mock.patch.object(workbench.shutil, "which", return_value=None):
            with self.assertRaisesRegex(workbench.WorkbenchError, "ffmpeg, ffprobe"):
                workbench.tool_paths()

    def test_plan_covers_partial_last_chapter(self):
        plan = workbench.chapters(601, 300, 2)
        self.assertEqual([(chapter["start_seconds"], chapter["end_seconds"]) for chapter in plan],
                         [(0, 300), (300, 600), (600, 601)])
        self.assertEqual(plan[-1]["window_end_seconds"], 601)

    def test_nonfinite_or_invalid_options_refused(self):
        for bad in ("nan", "inf", "-1", "0"):
            with self.assertRaises(Exception):
                workbench.positive(bad)

    def test_artifacts_cannot_escape_work_directory(self):
        with tempfile.TemporaryDirectory(dir=TEST_TEMP) as temporary:
            with self.assertRaises(workbench.WorkbenchError):
                workbench.owned_path(Path(temporary).resolve(), "../outside.json")

    def test_sample_cap_prevents_unbounded_frame_work(self):
        chapter = workbench.chapters(300, 300, 2)[0]
        with self.assertRaisesRegex(workbench.WorkbenchError, "limit"):
            workbench.sample_times(chapter, 0.01)


if __name__ == "__main__":
    unittest.main()
