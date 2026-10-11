#!/usr/bin/env python3
"""Discover YouTube video outliers with transparent, same-format channel baselines.

Python 3.10+, standard library only. No authenticated channel access required.
Offline --snapshot mode is designed for repeatable tests and audited imports.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import statistics
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

BASE = "https://www.googleapis.com/youtube/v3"
QUOTA_COST = {"search": 1, "channels": 1, "playlistItems": 1, "videos": 1}


class ResearchError(Exception):
    """Actionable input, quota, or API failure."""


def chunks(items, size=50):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def duration_seconds(iso):
    match = re.fullmatch(r"P(?:(\d+)D)?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not match:
        return 0
    d, h, m, s = (int(n or 0) for n in match.groups())
    return d * 86400 + h * 3600 + m * 60 + s


def timestamp(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return (parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)
    except (ValueError, AttributeError, TypeError):
        return None


def kind(video, threshold):
    seconds = video.get("duration_seconds", 0)
    if not isinstance(seconds, (int, float)) or seconds <= 0:
        return None
    return "shorts_proxy" if seconds <= threshold else "longs"


def score_snapshot(snapshot, args, now=None):
    """Pure scoring, with candidate excluded from its own channel baseline."""
    now = now or datetime.now(timezone.utc)
    videos = [v for v in snapshot.get("videos", []) if isinstance(v, dict)]
    by_id = {v.get("id"): v for v in videos if v.get("id")}
    channels = {c.get("id"): c for c in snapshot.get("channels", []) if c.get("id")}
    candidates = snapshot.get("candidate_ids")
    if candidates is None:
        candidates = list(by_id)
    ids = list(dict.fromkeys(candidates))
    by_channel_format = defaultdict(list)
    for v in videos:
        fmt = kind(v, args.max_duration_seconds)
        if fmt and v.get("channel_id"):
            by_channel_format[(v["channel_id"], fmt)].append(v)
    for group in by_channel_format.values():
        group.sort(key=lambda v: timestamp(v.get("published_at")) or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    start = timestamp(args.published_after) if args.published_after else now - timedelta(days=args.days)
    end = timestamp(args.published_before) if args.published_before else now
    if not start or not end or start > end:
        raise ResearchError("Invalid publication dates: use ISO 8601 and start <= end.")
    results = []
    reasons = defaultdict(int)
    for vid in ids:
        v = by_id.get(vid)
        if not v:
            reasons["candidate_missing"] += 1
            continue
        ch = channels.get(v.get("channel_id"))
        if not ch:
            reasons["channel_missing"] += 1
            continue
        subs = ch.get("subscriber_count")
        if args.max_subscribers is not None and (subs is None or subs > args.max_subscribers):
            reasons["subscriber_filter"] += 1
            continue
        fmt = kind(v, args.max_duration_seconds)
        if not fmt or (args.video_format != "all" and args.video_format != "shorts" and fmt != "longs") or (args.video_format == "shorts" and fmt != "shorts_proxy"):
            reasons["format_filter"] += 1
            continue
        published = timestamp(v.get("published_at"))
        if not published or not (start <= published <= end):
            reasons["date_filter"] += 1
            continue
        age_hours = (now - published).total_seconds() / 3600
        if age_hours < args.min_age_hours or age_hours < 0:
            reasons["too_new"] += 1
            continue
        views = v.get("views")
        if not isinstance(views, (int, float)) or views < args.min_views:
            reasons["view_filter"] += 1
            continue
        peers = [p for p in by_channel_format[(v["channel_id"], fmt)]
                 if p.get("id") != vid and p.get("views") is not None
                 and isinstance(p.get("views"), (int, float)) and p["views"] >= 0
                 and timestamp(p.get("published_at")) is not None
                 and (now - timestamp(p["published_at"])).total_seconds() / 3600 >= args.min_age_hours]
        peers = peers[:args.baseline_size]
        if len(peers) < args.min_baseline:
            reasons["insufficient_baseline"] += 1
            continue
        baseline = statistics.median(p["views"] for p in peers)
        if baseline <= 0:
            reasons["zero_baseline"] += 1
            continue
        multiple = views / baseline
        if multiple < args.min_outlier_score:
            reasons["below_score"] += 1
            continue
        velocity = views / max(age_hours / 24, 1)
        results.append({
            "video_id": vid, "video_url": f"https://www.youtube.com/watch?v={vid}",
            "title": v.get("title", ""), "published_at": v["published_at"],
            "channel_id": ch["id"], "channel_name": ch.get("title", ""),
            "channel_url": f"https://www.youtube.com/channel/{ch['id']}",
            "subscribers": subs, "views": int(views), "duration_seconds": int(v["duration_seconds"]),
            "format": fmt, "format_verified": False if fmt == "shorts_proxy" else None,
            "baseline_median_views": float(baseline), "baseline_sample_size": len(peers),
            "outlier_score": round(multiple, 3), "views_per_day": round(velocity, 1),
            "views_per_subscriber": round(views / subs, 2) if isinstance(subs, int) and subs > 0 else None,
            "confidence": "higher" if len(peers) >= 15 else "limited",
            "caveat": "Public lifetime views; uploads of different ages are not normalized by age."
        })
    sort_key = {"outlier": lambda v: v["outlier_score"], "views": lambda v: v["views"],
                "velocity": lambda v: v["views_per_day"]}[args.sort_by]
    results.sort(key=lambda v: (sort_key(v), v["views"]), reverse=True)
    return results[:args.max_results], dict(reasons)


class YouTubeClient:
    def __init__(self, key, quota_budget, search_call_budget=100):
        self.key = key
        self.budget = quota_budget
        self.search_call_budget = search_call_budget
        self.used = 0
        self.search_calls = 0
        self.calls = defaultdict(int)

    def request(self, endpoint, **params):
        cost = QUOTA_COST[endpoint]
        if endpoint == "search" and self.search_calls >= self.search_call_budget:
            raise ResearchError(f"Local search call limit hit: {self.search_calls}/{self.search_call_budget}. Reduce search terms or change --search-call-budget.")
        if self.used + cost > self.budget:
            raise ResearchError(f"Quota budget exceeded before {endpoint}: {self.used}/{self.budget} estimated units. Narrow terms/channels or raise --quota-budget.")
        self.used += cost
        self.calls[endpoint] += 1
        if endpoint == "search":
            self.search_calls += 1
        # Never include API key or generated URL in logs/errors.
        url = f"{BASE}/{endpoint}?" + urlencode({"part": params.pop("part"), **params, "key": self.key})
        for attempt in range(3):
            try:
                with urlopen(url, timeout=25) as response:
                    return json.load(response)
            except HTTPError as exc:
                reason = ""
                try:
                    payload = json.loads(exc.read().decode("utf-8"))
                    errors = payload.get("error", {}).get("errors", [])
                    reason = errors[0].get("reason", "") if errors else ""
                except (ValueError, AttributeError, UnicodeError):
                    pass
                if reason in {"quotaExceeded", "dailyLimitExceeded"}:
                    raise ResearchError("YouTube Data API daily quota exhausted. Results may be incomplete.") from None
                if exc.code in (429, 500, 502, 503, 504) and attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                raise ResearchError(f"YouTube API {endpoint}: HTTP {exc.code}, reason={reason or 'unknown'}. Check key, permissions and parameters.") from None
            except (URLError, TimeoutError) as exc:
                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                raise ResearchError(f"Network error calling YouTube {endpoint}: {type(exc).__name__}") from None
        raise ResearchError(f"YouTube {endpoint}: retries exhausted")


def collect_live(args, client):
    found = []
    channel_ids = dict.fromkeys(args.channel_ids or [])
    for term in args.terms or []:
        response = client.request("search", part="snippet", q=term, type="video",
                                  order=args.search_order, maxResults=min(args.search_results, 50),
                                  publishedAfter=(args.published_after or (datetime.now(timezone.utc)-timedelta(days=args.days)).isoformat().replace('+00:00', 'Z')),
                                  **({"publishedBefore": args.published_before} if args.published_before else {}),
                                  **({"relevanceLanguage": args.relevance_language} if args.relevance_language else {}),
                                  **({"regionCode": args.region_code} if args.region_code else {}))
        for item in response.get("items", []):
            video_id = item.get("id", {}).get("videoId")
            channel_id = item.get("snippet", {}).get("channelId")
            if video_id and channel_id:
                found.append(video_id)
                channel_ids[channel_id] = None
    if not channel_ids:
        return {"candidate_ids": [], "videos": [], "channels": []}
    channel_ids = list(channel_ids)[:args.max_channels]
    channels = []
    for batch in chunks(channel_ids):
        response = client.request("channels", part="snippet,statistics,contentDetails", id=','.join(batch))
        for item in response.get("items", []):
            stats = item.get("statistics", {})
            count = stats.get("subscriberCount")
            if stats.get("hiddenSubscriberCount") is True:
                count = None
            channels.append({"id": item["id"], "title": item.get("snippet", {}).get("title", ""),
                             "subscriber_count": int(count) if count is not None else None,
                             "uploads_playlist_id": item.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")})
    videos = {}
    for ch in channels:
        if args.max_subscribers is not None and (ch["subscriber_count"] is None or ch["subscriber_count"] > args.max_subscribers):
            continue
        playlist = ch.get("uploads_playlist_id")
        if not playlist:
            continue
        ids = []
        page_token = None
        max_scanned = min(250, max(50, args.baseline_size * 4))
        while len(ids) < max_scanned:
            params = {"playlistId": playlist, "maxResults": min(50, max_scanned - len(ids))}
            if page_token:
                params["pageToken"] = page_token
            response = client.request("playlistItems", part="contentDetails", **params)
            for item in response.get("items", []):
                ident = item.get("contentDetails", {}).get("videoId")
                if ident:
                    ids.append(ident)
            page_token = response.get("nextPageToken")
            if not page_token or not response.get("items"):
                break
        for batch in chunks(list(dict.fromkeys(ids))):
            response = client.request("videos", part="snippet,statistics,contentDetails", id=','.join(batch))
            for item in response.get("items", []):
                snippet = item.get("snippet", {})
                if snippet.get("liveBroadcastContent") in ("live", "upcoming"):
                    continue
                d = duration_seconds(item.get("contentDetails", {}).get("duration", ""))
                count = item.get("statistics", {}).get("viewCount")
                if not d or count is None:
                    continue
                videos[item["id"]] = {"id": item["id"], "title": snippet.get("title", ""),
                                      "channel_id": ch["id"], "views": int(count),
                                      "duration_seconds": d, "published_at": snippet.get("publishedAt", "")}
    active_ids = set(videos)
    if args.channel_ids and not args.terms:
        found = list(active_ids)
    # videos returned by search may not be among the sampled uploads; fetch them once.
    missing = [v for v in dict.fromkeys(found) if v not in active_ids]
    if missing:
        for batch in chunks(missing):
            response = client.request("videos", part="snippet,statistics,contentDetails", id=','.join(batch))
            for item in response.get("items", []):
                snip = item.get("snippet", {})
                count = item.get("statistics", {}).get("viewCount")
                if count is None or snip.get("channelId") not in {c["id"] for c in channels}:
                    continue
                videos[item["id"]] = {"id": item["id"], "title": snip.get("title", ""),
                                      "channel_id": snip["channelId"], "views": int(count),
                                      "duration_seconds": duration_seconds(item.get("contentDetails", {}).get("duration", "")),
                                      "published_at": snip.get("publishedAt", "")}
    return {"channels": channels, "videos": list(videos.values()), "candidate_ids": list(dict.fromkeys(found))}


def build_parser():
    p = argparse.ArgumentParser(description="Find relative YouTube outliers; API or offline JSON snapshot.")
    p.add_argument("--terms", nargs="+", help="Niche/topic search terms")
    p.add_argument("--channel-ids", nargs="+", default=[], help="YouTube UC... channel IDs (not @handles)")
    p.add_argument("--snapshot", help="Offline snapshot JSON; no API key or network needed")
    p.add_argument("--save-snapshot", help="Save normalized public API input for repeatable analysis")
    p.add_argument("--published-after", help="ISO 8601/RFC3339, inclusive")
    p.add_argument("--published-before", help="ISO 8601/RFC3339, inclusive")
    p.add_argument("--days", type=int, default=30)
    p.add_argument("--max-subscribers", type=int, default=50000)
    p.add_argument("--min-views", type=int, default=10000)
    p.add_argument("--min-outlier-score", type=float, default=3)
    p.add_argument("--video-format", choices=["shorts", "longs", "all"], default="all")
    p.add_argument("--max-duration-seconds", type=int, default=180)
    p.add_argument("--baseline-size", type=int, default=30)
    p.add_argument("--min-baseline", type=int, default=5)
    p.add_argument("--min-age-hours", type=float, default=24)
    p.add_argument("--search-results", type=int, default=25)
    p.add_argument("--max-channels", type=int, default=40)
    p.add_argument("--sort-by", choices=["outlier", "views", "velocity"], default="outlier")
    p.add_argument("--search-order", choices=["date", "viewCount", "relevance"], default="date")
    p.add_argument("--region-code", help="Optional YouTube region hint (BR, MX, US)")
    p.add_argument("--relevance-language", help="Optional search relevance language hint (pt, es, en)")
    p.add_argument("--quota-budget", type=int, default=1000, help="Hard local estimated total-request unit budget")
    p.add_argument("--search-call-budget", type=int, default=100, help="Hard local search.list call limit (separate API bucket)")
    p.add_argument("--max-results", type=int, default=15)
    p.add_argument("--output", default="outliers.json", help="JSON result path; CSV saved alongside")
    p.add_argument("--dry-run", action="store_true", help="No API calls, show approximate quota budget")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.days < 1 or args.baseline_size < 1 or args.min_baseline < 1 or args.min_baseline > args.baseline_size or args.search_results < 1 or args.max_channels < 1 or args.max_duration_seconds < 1 or args.quota_budget < 1 or args.search_call_budget < 1 or args.max_results < 1 or args.min_views < 0 or args.min_outlier_score <= 0 or args.min_age_hours < 0:
        raise ResearchError("Invalid thresholds: use positive sizes/budget and min-baseline <= baseline-size.")
    if not args.snapshot and not args.terms and not args.channel_ids:
        raise ResearchError("Provide --terms, --channel-ids or --snapshot.")
    if args.dry_run:
        print(json.dumps({"planned_search_calls": len(args.terms or []),
                          "search_call_budget": args.search_call_budget,
                          "other_calls": "channels.list, playlistItems.list, videos.list cost 1 unit per call",
                          "request_budget": args.quota_budget,
                          "max_channels": args.max_channels}, indent=2))
        return 0
    client = None
    if args.snapshot:
        snapshot = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
    else:
        key = os.environ.get("YOUTUBE_API_KEY")
        if not key:
            raise ResearchError("YOUTUBE_API_KEY missing. Export it in the environment; never put it in CLI arguments.")
        client = YouTubeClient(key, args.quota_budget, args.search_call_budget)
        snapshot = collect_live(args, client)
    if args.save_snapshot:
        dst = Path(args.save_snapshot)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    items, reasons = score_snapshot(snapshot, args)
    out = {"generated_at": datetime.now(timezone.utc).isoformat(),
           "search_terms": args.terms or [], "method": "video_views / median(same-channel, same-duration-class peers; candidate excluded)",
           "format_caveat": "Shorts are duration proxies; YouTube API does not confirm Shorts membership.",
           "age_caveat": "Views are lifetime counts, not normalized for upload age.",
           "sampled_channels": len(snapshot.get("channels", [])),
           "sampled_videos": len(snapshot.get("videos", [])),
           "candidate_count": len(snapshot.get("candidate_ids", [])),
           "estimated_quota_used": client.used if client else 0,
           "search_calls_used": client.search_calls if client else 0,
           "quota_calls": dict(client.calls) if client else {},
           "rejection_counts": reasons, "results": items}
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    csv_path = target.with_suffix(".csv")
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        if items:
            writer = csv.DictWriter(f, fieldnames=list(items[0]))
            writer.writeheader()
            writer.writerows(items)
    print(json.dumps({"found": len(items), "json": str(target), "csv": str(csv_path),
                      "quota_estimated": out["estimated_quota_used"], "rejections": reasons}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ResearchError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)