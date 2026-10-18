"""Smoke tests for the shortform editor with generated, non-copyright media."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "skills/video-editing-shortform-manga/scripts/shortform_render.py"
HAS_MEDIA = shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


@unittest.skipUnless(HAS_MEDIA, "FFmpeg and FFprobe are required")
class ShortFormSmoke(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name, color in (("a.jpg", "red"), ("b.jpg", "blue")):
            subprocess.run(
                ["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "lavfi",
                 "-i", f"color=c={color}:s=240x320:r=1", "-frames:v", "1",
                 "-update", "1", str(self.root / name)],
                check=True, capture_output=True
            )
        subprocess.run(
            ["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "lavfi",
             "-i", "anullsrc=r=44100:cl=mono", "-t", "4", "-c:a", "pcm_s16le",
             str(self.root / "voice.wav")],
            check=True, capture_output=True
        )
        self.plan = {
            "schema_version": 1, "language": "es",
            "canvas": {"width": 180, "height": 320, "fps": 15},
            "audio": "voice.wav",
            "segments": [
                {"id": "B01", "image": "a.jpg", "start": 0, "end": 2,
                 "focus": [0.5, 0.5], "zoom": [1.0, 1.15],
                 "protected": True, "why": "apice", "reviewed": True},
                {"id": "B02", "image": "b.jpg", "start": 2, "end": 4,
                 "focus": [0.6, 0.4], "zoom": [1.14, 1.00],
                 "protected": False, "why": "resolucao", "reviewed": True}
            ],
            "cta": [{"action":"comment", "start":3, "duration":1,
                     "text":"Que opinas?", "why_now":"depois da resolucao"}]
        }
        self.plan_path = self.root / "plan.json"

    def invoke(self, *args):
        self.plan_path.write_text(json.dumps(self.plan),encoding="utf-8")
        return subprocess.run([sys.executable,str(SCRIPT),*args],
                              text=True,capture_output=True)

    def test_protects_climax(self):
        self.plan["cta"][0]["start"] = 1
        cp = self.invoke("validate",str(self.plan_path))
        self.assertNotEqual(cp.returncode,0)

    def test_render_and_full_decode(self):
        cp = self.invoke("validate",str(self.plan_path))
        self.assertEqual(cp.returncode,0,cp.stderr)
        target = self.root/"master.mp4"
        cp = self.invoke("render",str(self.plan_path),"--output",str(target),
                         "--workdir",str(self.root/"work"))
        self.assertEqual(cp.returncode,0,cp.stderr)
        self.assertTrue(target.exists())
        report = json.loads((self.root/"master.edit-report.json").read_text())
        self.assertEqual(report["status"],"technically_validated")
        self.assertEqual(report["cta"],1)
        self.assertEqual(report["canvas"]["width"],180)
        # Rendered video from the advanced manga editor can receive a CTA as a
        # separate post-processing step, preserving its original audio codec.
        overlay = SCRIPT.parent / "motion_cta_overlay.py"
        overlay_target = self.root / "overlay.mp4"
        cp = subprocess.run(
            [sys.executable, str(overlay), str(target), str(self.plan_path),
             "--output", str(overlay_target),
             "--workdir", str(self.root / "cta-work")],
            text=True, capture_output=True
        )
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertTrue(overlay_target.is_file())
        motion_report = json.loads(
            (self.root / "overlay.motion-report.json").read_text())
        self.assertEqual(motion_report["status"], "technically_validated")
        self.assertTrue(motion_report["audio_codec_preserved"])


if __name__ == "__main__":
    unittest.main()
