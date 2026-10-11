"""Offline contract tests for the YouTube outlier research skill."""
import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "youtube_outliers.py"
spec = importlib.util.spec_from_file_location("youtube_outliers", MODULE)
outliers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(outliers)
NOW = datetime(2026, 10, 11, 12, 0, tzinfo=timezone.utc)


def fixture(shorts=True):
    videos = []
    for i in range(6):
        videos.append({"id": f"peer{i}", "channel_id": "UCexample", "title": f"Reference {i}",
                       "views": 1000 + i * 100, "duration_seconds": 60 if shorts else 600,
                       "published_at": (NOW-timedelta(days=10+i)).isoformat()})
    videos.append({"id": "winner", "channel_id": "UCexample", "title": "Winner",
                   "views": 50000, "duration_seconds": 60, "published_at": (NOW-timedelta(days=2)).isoformat()})
    return {"channels": [{"id": "UCexample", "title": "Example", "subscriber_count": 5000}],
            "videos": videos, "candidate_ids": ["winner"]}


class TestOutlierScoring(unittest.TestCase):
    def args(self, *extra):
        return outliers.build_parser().parse_args(["--snapshot", "unused", *extra])

    def test_strong_outlier_excludes_self_from_median(self):
        rows, reasons = outliers.score_snapshot(fixture(), self.args(), NOW)
        self.assertEqual(reasons, {})
        self.assertEqual(len(rows), 1)
        self.assertAlmostEqual(rows[0]["baseline_median_views"], 1250)
        self.assertEqual(rows[0]["outlier_score"], 40)
        self.assertEqual(rows[0]["format"], "shorts_proxy")
        self.assertIs(rows[0]["format_verified"], False)

    def test_separate_format_baseline(self):
        _, reasons = outliers.score_snapshot(fixture(shorts=False), self.args(), NOW)
        self.assertEqual(reasons["insufficient_baseline"], 1)

    def test_too_few_peers_is_not_claimed_as_outlier(self):
        data = fixture()
        data["videos"] = data["videos"][-3:]
        _, reasons = outliers.score_snapshot(data, self.args(), NOW)
        self.assertEqual(reasons["insufficient_baseline"], 1)

    def test_hidden_subscribers_not_silently_accepted_under_cap(self):
        data = fixture()
        data["channels"][0]["subscriber_count"] = None
        _, reasons = outliers.score_snapshot(data, self.args(), NOW)
        self.assertEqual(reasons["subscriber_filter"], 1)

    def test_date_window_and_long_only(self):
        data = fixture()
        _, reasons = outliers.score_snapshot(data, self.args("--video-format", "longs"), NOW)
        self.assertEqual(reasons["format_filter"], 1)
        _, reasons = outliers.score_snapshot(data, self.args("--published-after", "2026-10-10T00:00:00Z"), NOW)
        self.assertEqual(reasons["date_filter"], 1)

    def test_duration_parser_and_age(self):
        self.assertEqual(outliers.duration_seconds("PT2M59S"), 179)
        self.assertEqual(outliers.duration_seconds("PT1H2M"), 3720)
        self.assertEqual(outliers.duration_seconds("garbage"), 0)
        data = fixture()
        data["videos"][-1]["published_at"] = (NOW-timedelta(hours=2)).isoformat()
        _, reasons = outliers.score_snapshot(data, self.args(), NOW)
        self.assertEqual(reasons["too_new"], 1)

    def test_offline_cli_and_no_network(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            snapshot = path / "snapshot.json"
            snapshot.write_text(json.dumps(fixture()), encoding="utf-8")
            output = path / "report.json"
            rc = outliers.main(["--snapshot", str(snapshot), "--min-age-hours", "0", "--output", str(output)])
            self.assertEqual(rc, 0)
            self.assertTrue(output.exists())
            self.assertTrue(output.with_suffix(".csv").exists())
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(len(report["results"]), 1)
            self.assertEqual(report["estimated_quota_used"], 0)

    def test_quota_guard_before_network(self):
        api = outliers.YouTubeClient("secret", quota_budget=1)
        with self.assertRaises(outliers.ResearchError):
            api.request("search", part="snippet", q="manga")
        self.assertEqual(api.used, 0)

    def test_invalid_thresholds(self):
        with self.assertRaises(outliers.ResearchError):
            outliers.main(["--snapshot", "irrelevant", "--baseline-size", "2", "--min-baseline", "5"])


if __name__ == "__main__":
    unittest.main()