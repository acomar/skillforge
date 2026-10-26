"""Comportamento do helper de legendas e integridade dos recursos publicados."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1] / "skills" / "meu-bebe-popup"
spec = importlib.util.spec_from_file_location("popup_tools", ROOT / "scripts" / "popup_tools.py")
popup_tools = importlib.util.module_from_spec(spec)
spec.loader.exec_module(popup_tools)


class CaptionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.source = self.folder / "words.json"
        self.words = [
            {"text": "Seu", "start": 0, "end": 0.2},
            {"text": "bebê", "start": 0.2, "end": 0.55},
            {"text": "sorriu.", "start": 0.55, "end": 1},
            {"text": "Agora", "start": 3, "end": 3.5},
            {"text": "é", "start": 3.5, "end": 3.7},
            {"text": "sua", "start": 3.7, "end": 4.1},
            {"text": "vez!", "start": 4.1, "end": 4.5},
        ]
        self.source.write_text(json.dumps(self.words, ensure_ascii=False), encoding="utf-8")

    def invoke(self, *extra):
        with contextlib.redirect_stdout(io.StringIO()):
            return popup_tools.main([
                "captions", str(self.source), "--lead", "1.25", "--duration", "7",
                "--srt", str(self.folder / "captions.srt"),
                "--cues", str(self.folder / "cues.json"), *extra,
            ])

    def test_exports_preserve_words_and_real_times_with_one_lead(self):
        self.assertEqual(self.invoke(), 0)
        payload = json.loads((self.folder / "cues.json").read_text(encoding="utf-8"))
        cues = payload["cues"]
        exported = [word for cue in cues for word in cue["words"]]
        self.assertEqual([w["text"] for w in exported], [w["text"] for w in self.words])
        for original, result in zip(self.words, exported):
            self.assertAlmostEqual(result["start"] - original["start"], 1.25)
            self.assertAlmostEqual(result["end"] - original["end"], 1.25)
        self.assertTrue(all(1 <= len(cue["words"]) <= 2 for cue in cues))
        self.assertEqual(cues[1]["text"], "sorriu.")
        self.assertLess(cues[1]["end"], cues[2]["start"])
        srt = (self.folder / "captions.srt").read_text(encoding="utf-8")
        self.assertIn("00:00:01,250 --> 00:00:01,800\nSeu bebê", srt)

    def test_invalid_alignment_does_not_create_outputs(self):
        invalid = [
            [],
            [{"text": "bebê", "start": -0.1, "end": 1}],
            [{"text": "bebê", "start": 1, "end": 1}],
            [{"text": "duas palavras", "start": 0, "end": 1}],
            [{"text": "bebê", "start": True, "end": 1}],
            [{"text": "bebê", "start": 0, "end": float("nan")}],
            [{"text": "A", "start": 0, "end": 1}, {"text": "B", "start": 0.5, "end": 2}],
            [{"text": "bebê", "start": 0, "end": 8}],
        ]
        for words in invalid:
            with self.subTest(words=words):
                self.source.write_text(json.dumps(words), encoding="utf-8")
                self.assertEqual(self.invoke(), 2)
                self.assertFalse((self.folder / "captions.srt").exists())
                self.assertFalse((self.folder / "cues.json").exists())

    def test_existing_output_requires_explicit_overwrite(self):
        self.assertEqual(self.invoke(), 0)
        output = self.folder / "captions.srt"
        output.write_text("PRESERVAR", encoding="utf-8")
        source_before = self.source.read_bytes()
        self.assertEqual(self.invoke(), 2)
        self.assertEqual(output.read_text(encoding="utf-8"), "PRESERVAR")
        self.assertEqual(self.invoke("--force"), 0)
        self.assertEqual(self.source.read_bytes(), source_before)


class PackageTests(unittest.TestCase):
    def test_local_markdown_links_resolve(self):
        for file in ROOT.rglob("*.md"):
            for link in re.findall(r"\]\(([^)]+)\)", file.read_text(encoding="utf-8")):
                if not re.match(r"\w+://", link) and not link.startswith("#"):
                    self.assertTrue((file.parent / link.split("#")[0]).exists(), f"{file}: {link}")

    def test_bundled_board_matches_brand_manifest(self):
        tokens = json.loads((ROOT / "assets" / "brand-tokens.json").read_text(encoding="utf-8"))
        board = ROOT / "assets" / tokens["reference_board"]["file"]
        self.assertEqual(hashlib.sha256(board.read_bytes()).hexdigest(), tokens["reference_board"]["sha256"])
        self.assertEqual(tokens["video"]["width"] * 16, tokens["video"]["height"] * 9)


if __name__ == "__main__":
    unittest.main()
