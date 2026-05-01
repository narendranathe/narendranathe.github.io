"""Verify every link on the portfolio resolves.

Two modes:
  --local (default) checks relative paths exist on disk + fragment IDs
  resolve to elements in the target file. Fast, deterministic, CI-safe.

  --live ALSO hits external https:// URLs with a HEAD request and
  reports 4xx/5xx. Slow + flaky (depends on third-party uptime); only
  use when you actually want to audit external links.

Outputs a single report. Exits 1 on any failure so CI can gate.

Stdlib-only. No new runtime deps.

Usage
-----
    python scripts/verify-links.py              # local-only
    python scripts/verify-links.py --live       # local + external
    python scripts/verify-links.py --json       # machine-readable
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

HTML_GLOBS: tuple[str, ...] = ("*.html", "content/posts/*.html")
LINK_TAGS: dict[str, str] = {
    "a": "href",
    "link": "href",
    "img": "src",
    "script": "src",
}
SKIP_SCHEMES: tuple[str, ...] = ("mailto:", "tel:", "javascript:", "sms:", "data:")
EXTERNAL_TIMEOUT_S = 10
EXTERNAL_USER_AGENT = "Mozilla/5.0 (compatible; PortfolioLinkVerifier/1.0)"
# Hosts known to be hostile to verifiers (block bots, throttle HEAD,
# wall behind login). Map host -> set of status codes to treat as
# "lenient pass" since we can't reliably verify reachability without
# a real browser. The URL is assumed well-formed if we got that far.
#
# - LinkedIn: 999 (their bot guard), and 404 + 403 when unauthenticated
# - GitHub raw + plain github: 403 on HEAD/some IPs
# - doi.org: redirects to publisher pages that frequently 403 bots
LENIENT_HOSTS: dict[str, frozenset[int]] = {
    "linkedin.com": frozenset({403, 404, 405, 999}),
    "www.linkedin.com": frozenset({403, 404, 405, 999}),
    "github.com": frozenset({403, 405, 999}),
    "raw.githubusercontent.com": frozenset({403, 405}),
    "doi.org": frozenset({403, 405}),
}


@dataclass
class LinkRef:
    file: Path
    tag: str
    href: str
    line: int
    rel: str | None = None  # only set for <link rel="...">; used to skip preconnect/dns-prefetch hints


@dataclass
class Report:
    checked_local: int = 0
    checked_external: int = 0
    skipped: int = 0
    failures: list[tuple[LinkRef, str]] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failures


# ---------- HTML parsing ----------
class LinkCollector(HTMLParser):
    def __init__(self, file: Path) -> None:
        super().__init__()
        self.file = file
        self.refs: list[LinkRef] = []
        self.id_attrs: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        adict = dict(attrs)
        # Track id="..." for same-page fragment validation
        id_val = adict.get("id")
        if id_val:
            self.id_attrs.add(id_val)
        attr = LINK_TAGS.get(tag)
        if not attr:
            return
        href = adict.get(attr)
        if not href:
            return
        line, _ = self.getpos()
        rel = adict.get("rel") if tag == "link" else None
        self.refs.append(LinkRef(file=self.file, tag=tag, href=href, line=line, rel=rel))


def collect_html_files() -> list[Path]:
    found: list[Path] = []
    for pattern in HTML_GLOBS:
        found.extend(REPO_ROOT.glob(pattern))
    return sorted(set(found))


def parse_file(path: Path) -> tuple[list[LinkRef], set[str]]:
    parser = LinkCollector(path)
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.refs, parser.id_attrs


# ---------- local resolution ----------
def is_external(href: str) -> bool:
    return href.startswith(("http://", "https://"))


def is_skip(href: str) -> bool:
    return href.startswith(SKIP_SCHEMES) or not href.strip()


def resolve_local(href: str, file: Path) -> tuple[Path, str | None]:
    """Resolve a local href to (target_path, fragment).

    Fragment is the part after '#' if present, else None.
    Target_path is the on-disk file the href points to (which may be
    the same file as the source if href is purely a fragment).
    """
    parsed = urllib.parse.urlparse(href)
    fragment = parsed.fragment or None
    path_part = parsed.path

    # Pure fragment (#section) -> same file
    if not path_part and fragment:
        return file, fragment

    # Absolute path (/static/foo.pdf) -> repo root
    if path_part.startswith("/"):
        target = REPO_ROOT / path_part.lstrip("/")
    else:
        # Relative path -> sibling of the HTML file
        target = (file.parent / path_part).resolve()

    return target, fragment


def check_local(ref: LinkRef, ids_by_file: dict[Path, set[str]]) -> str | None:
    """Return None if OK, else an error string."""
    href = ref.href
    target, fragment = resolve_local(href, ref.file)

    # Strip query string from target path
    target_str = str(target)
    if "?" in target_str:
        target = Path(target_str.split("?", 1)[0])

    if not target.exists():
        # Allow special files served by GitHub Pages config but absent
        # from the source tree (e.g. CNAME redirects). None expected for
        # this repo, but leaving the hook open.
        return f"file not found on disk: {target}"

    if fragment:
        # Fragment must resolve to an id="..." in the target file
        if target.suffix.lower() == ".html":
            target_ids = ids_by_file.get(target)
            if target_ids is None:
                _, target_ids = parse_file(target)
                ids_by_file[target] = target_ids
            if fragment not in target_ids:
                return f"fragment #{fragment} not found in {target.name}"
    return None


# ---------- external resolution ----------
def _request(href: str, method: str) -> int | str:
    """Return HTTP status int, or an error string."""
    req = urllib.request.Request(href, method=method, headers={"User-Agent": EXTERNAL_USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=EXTERNAL_TIMEOUT_S) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
        return f"network error: {exc}"


def check_external(ref: LinkRef) -> str | None:
    href = ref.href
    parsed = urllib.parse.urlparse(href)
    host = parsed.hostname or ""

    # Try HEAD first (cheap). If the server rejects HEAD with 403/405
    # or returns 5xx, retry with GET — many origins accept GET but
    # block HEAD (e.g. fly.dev /health, doi.org, some publisher CDNs).
    status = _request(href, "HEAD")
    if isinstance(status, str):
        return status
    if status in (403, 405) or status >= 500:
        status = _request(href, "GET")
        if isinstance(status, str):
            return status

    if status >= 400:
        lenient_codes = LENIENT_HOSTS.get(host)
        if lenient_codes and status in lenient_codes:
            # Host known to wall verifiers; URL is well-formed, assume
            # reachable from a real browser. See LENIENT_HOSTS comment.
            return None
        return f"HTTP {status}"
    return None


# ---------- reporting ----------
def report_text(report: Report) -> str:
    lines: list[str] = []
    lines.append(f"checked {report.checked_local} local + {report.checked_external} external; skipped {report.skipped}")
    if report.ok:
        lines.append("")
        lines.append("all links OK")
        return "\n".join(lines)
    lines.append(f"\n{len(report.failures)} failure(s):")
    for ref, err in report.failures:
        rel = ref.file.relative_to(REPO_ROOT)
        lines.append(f"  {rel}:{ref.line}  <{ref.tag} {ref.href!r}>  -> {err}")
    return "\n".join(lines)


def report_json(report: Report) -> str:
    return json.dumps(
        {
            "ok": report.ok,
            "checked_local": report.checked_local,
            "checked_external": report.checked_external,
            "skipped": report.skipped,
            "failures": [
                {
                    "file": str(ref.file.relative_to(REPO_ROOT)),
                    "line": ref.line,
                    "tag": ref.tag,
                    "href": ref.href,
                    "error": err,
                }
                for ref, err in report.failures
            ],
        },
        indent=2,
    )


# ---------- main ----------
def main() -> int:
    p = argparse.ArgumentParser(description="Verify every link on the portfolio resolves.")
    p.add_argument("--live", action="store_true", help="Also check external URLs (slow, network-dependent)")
    p.add_argument("--json", action="store_true", help="Machine-readable JSON output")
    args = p.parse_args()

    files = collect_html_files()
    if not files:
        print("no HTML files found", file=sys.stderr)
        return 1

    # Pre-scan for IDs in every HTML file so cross-page fragments
    # resolve without re-parsing.
    ids_by_file: dict[Path, set[str]] = {}
    all_refs: list[LinkRef] = []
    for f in files:
        refs, ids = parse_file(f)
        ids_by_file[f] = ids
        all_refs.extend(refs)

    report = Report()
    for ref in all_refs:
        if is_skip(ref.href):
            report.skipped += 1
            continue
        # <link rel="preconnect"> / <link rel="dns-prefetch"> are
        # connection hints, not destinations. The browser warms the
        # TLS+TCP handshake to the origin; the bare-origin URL itself
        # often returns 404/405 on a real request. Skip these.
        if ref.rel and any(r in ref.rel.split() for r in ("preconnect", "dns-prefetch", "modulepreload")):
            report.skipped += 1
            continue
        if is_external(ref.href):
            report.checked_external += 1
            if args.live:
                err = check_external(ref)
                if err:
                    report.failures.append((ref, err))
            continue
        report.checked_local += 1
        err = check_local(ref, ids_by_file)
        if err:
            report.failures.append((ref, err))

    out = report_json(report) if args.json else report_text(report)
    print(out)
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
