"""Fetch the latest posts from a Substack publication's RSS feed and
write a same-origin JSON snapshot the hover-preview popup can consume.

Why a snapshot, not a live fetch:
- Substack's /feed endpoint does NOT return Access-Control-Allow-Origin,
  so client-side fetch from narendranathe.github.io is blocked by CORS.
- A periodic GitHub Action runs this script on a cron, writes the JSON
  to static/substack-latest.json, and commits only if the content has
  changed. Same-origin fetch from the popup, no CORS, no third-party
  tracking, no client-side parsing cost.

Output shape (stable contract — see hover-preview-pattern.md):
    {
      "publication": "Naren's Substack",
      "url": "https://narendranathe.substack.com/",
      "fetched_at": "2026-05-01T18:00:00Z",
      "posts": [
        {
          "title": "...",
          "url": "https://...",
          "published_at": "2026-04-28T15:30:00Z",
          "excerpt": "..."
        },
        ...
      ]
    }

Usage
-----
    python scripts/snap-substack-feed.py
    python scripts/snap-substack-feed.py --feed https://example.substack.com/feed
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FEED = "https://narendranathe.substack.com/feed"
TARGET = REPO_ROOT / "static" / "substack-latest.json"
TIMEOUT_S = 15
USER_AGENT = "Mozilla/5.0 (compatible; PortfolioSubstackSnap/1.0)"
MAX_POSTS = 3
EXCERPT_MAX_CHARS = 220
# Substack uses <content:encoded> in the content namespace; we read
# <description> instead (always present, plain HTML, shorter for excerpts).
NS = {"content": "http://purl.org/rss/1.0/modules/content/"}

# Strip ALL HTML tags (Substack descriptions are HTML); collapse whitespace.
_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def fetch_feed(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
        return resp.read().decode("utf-8")


def parse_rfc822(date_str: str) -> str:
    """RSS 2.0 uses RFC 822 dates ("Mon, 28 Apr 2026 15:30:00 GMT").
    Convert to ISO-8601 UTC for the JSON output. Returns the input
    unchanged if parsing fails (better than dropping the field)."""
    try:
        # email.utils handles RFC 822 robustly
        from email.utils import parsedate_to_datetime
        d = parsedate_to_datetime(date_str)
        if d is None:
            return date_str
        if d.tzinfo is None:
            d = d.replace(tzinfo=dt.timezone.utc)
        return d.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    except Exception:  # noqa: BLE001
        return date_str


def html_to_excerpt(s: str, max_chars: int = EXCERPT_MAX_CHARS) -> str:
    if not s:
        return ""
    # Strip tags, decode HTML entities, collapse whitespace
    plain = _TAG_RE.sub(" ", s)
    plain = html.unescape(plain)
    plain = _WS_RE.sub(" ", plain).strip()
    if len(plain) <= max_chars:
        return plain
    cut = plain[:max_chars].rsplit(" ", 1)[0]
    return cut + "..."


def parse_feed(xml_text: str) -> dict:
    root = ET.fromstring(xml_text)
    channel = root.find("channel")
    if channel is None:
        raise ValueError("RSS feed has no <channel>")

    publication = (channel.findtext("title") or "Substack").strip()
    site_url = (channel.findtext("link") or "").strip()

    posts: list[dict] = []
    for item in channel.findall("item")[:MAX_POSTS]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date = parse_rfc822((item.findtext("pubDate") or "").strip())
        excerpt = html_to_excerpt(item.findtext("description") or "")
        if title and link:
            posts.append({
                "title": title,
                "url": link,
                "published_at": pub_date,
                "excerpt": excerpt,
            })

    return {
        "publication": publication,
        "url": site_url,
        "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "posts": posts,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--feed", default=DEFAULT_FEED, help="Substack RSS feed URL")
    p.add_argument("--out", default=str(TARGET), help="Output JSON path")
    args = p.parse_args()

    try:
        xml_text = fetch_feed(args.feed)
    except urllib.error.URLError as exc:
        print(f"fetch failed: {exc}", file=sys.stderr)
        return 1
    except TimeoutError as exc:
        print(f"fetch timeout: {exc}", file=sys.stderr)
        return 1

    try:
        snapshot = parse_feed(xml_text)
    except (ET.ParseError, ValueError) as exc:
        print(f"parse failed: {exc}", file=sys.stderr)
        return 1

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"wrote {len(snapshot['posts'])} posts to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
