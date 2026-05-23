"""Verify every link on the portfolio resolves.

Three modes (via --mode):
  local (default) checks relative paths exist on disk + fragment IDs
  resolve to elements in the target file. Fast, deterministic, CI-safe.

  live ALSO hits external https:// URLs with a HEAD request and
  reports 4xx/5xx. Slow + flaky (depends on third-party uptime); only
  use when you actually want to audit external links.

  live-strict extends live with cross-origin asset URLs (the media
  repo's Pages site and GitHub Release downloads) and additionally
  asserts the response Content-Type header matches the file suffix.
  Used by the M5 forkable-skeleton verifier to catch silent
  mis-uploads on the assets repo.

Outputs a single report. Exits 1 on any failure so CI can gate.

Stdlib-only. No new runtime deps.

Usage
-----
    python scripts/verify-links.py                        # local-only
    python scripts/verify-links.py --mode live            # local + external
    python scripts/verify-links.py --mode live-strict     # + assets-repo
    python scripts/verify-links.py --live                 # DEPRECATED alias for --mode live
    python scripts/verify-links.py --json                 # machine-readable
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
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
# - LinkedIn: 999 (their bot guard), 403/405 on auth-walled HEAD.
#   404 is DELIBERATELY NOT lenient: LinkedIn returns 404 for both
#   bot-walled-but-valid profiles AND genuinely wrong/typo'd URLs,
#   indistinguishable from outside. Hiding 404 would silently pass
#   typos like /in/naren-edaraXXX. Specific URLs verified by hand
#   from a real browser go in HOST_ALLOWLIST instead.
# - GitHub raw + plain github: 403 on HEAD/some IPs
# - doi.org: redirects to publisher pages that frequently 403 bots
LENIENT_HOSTS: dict[str, frozenset[int]] = {
    "linkedin.com": frozenset({403, 405, 999}),
    "www.linkedin.com": frozenset({403, 405, 999}),
    "github.com": frozenset({403, 405, 999}),
    "raw.githubusercontent.com": frozenset({403, 405}),
    "doi.org": frozenset({403, 405}),
}

# Specific URLs the maintainer has verified by hand from a real
# browser and that bot-wall the verifier on a 404. Adding here
# acknowledges "this URL was confirmed working manually; the
# verifier just can't reach it from a stdlib bot." Exact-URL match.
HOST_ALLOWLIST: frozenset[str] = frozenset({
    "https://www.linkedin.com/in/narendranathe/",
    "https://linkedin.com/in/narendranathe/",
    # Testimonial-author profiles - manually verified from a real
    # browser. LinkedIn 404s these to unauthenticated bots.
    "https://www.linkedin.com/in/pranav-s-47356a58/",
})

# ---------- live-strict mode constants ----------
# The forkable-portfolio skeleton (M5) splits heavy media into a
# sibling assets repo and publishes large binaries (resume PDF, etc.)
# via GitHub Releases. live-strict mode crawls those URLs too.
MEDIA_REPO_URL = "https://narendranathe.github.io/resume2"
RELEASE_URL_BASE = "https://github.com/narendranathe/resume2/releases/download"

# Expected Content-Type per file suffix. Servers occasionally serve
# the right body with the wrong type (cached uploads, mis-configured
# CDNs); the strict mode catches this. NO application/pdf entry on
# purpose - per M5 scope-lock decision 2, the resume PDF stays at
# /static/resume.pdf and is covered by the existing live mode.
EXPECTED_CONTENT_TYPES: dict[str, tuple[str, ...]] = {
    ".jpg":  ("image/jpeg",),
    ".jpeg": ("image/jpeg",),
    ".png":  ("image/png",),
    ".avif": ("image/avif",),
    ".webp": ("image/webp",),
    ".json": ("application/json",),
    ".svg":  ("image/svg+xml",),
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
    if href in HOST_ALLOWLIST:
        return None  # manually verified URL; bot can't reach but human did
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


# ---------- live-strict: seeded URLs + Content-Type assertion ----------
# Synthetic file/line for seeded LinkRefs - they're not parsed out of
# any HTML on disk, but the LinkRef dataclass needs a Path/line. Using
# the verifier script itself keeps the failure reporter sensible.
_SEEDED_FILE = Path(__file__).resolve()


def seed_assets_urls(media_repo_url: str) -> list[LinkRef]:
    """Synthesize LinkRefs for the canonical assets-repo asset paths.

    These are the files the M1 milestone uploads to the media repo's
    Pages site. Hardcoded for now - if the layout drifts, this list
    needs an update. Mirrors the asset layout in narendranathe/resume2.
    """
    base = media_repo_url.rstrip("/")
    paths = (
        "/headshot.jpg",
        "/headshot.webp",
        "/headshot.avif",
        "/og-image.png",
        "/previews/index-preview.png",
        "/previews/resume-preview.png",
        "/manifest.json",
    )
    return [
        LinkRef(file=_SEEDED_FILE, tag="seeded", href=f"{base}{p}", line=0)
        for p in paths
    ]


def seed_release_urls() -> list[LinkRef]:
    """Synthesize LinkRefs for the rolling `resume` tag + most-recent
    dated release.

    Hardcoded for now - could later call the GitHub API to discover
    the actual latest dated tag. The rolling `resume` tag is what
    public consumers fetch; the dated tag is the immutable backup.
    """
    # The dated tag is a snapshot; pinning a known-good value keeps the
    # check deterministic. Bump when M1 cuts a fresh release.
    dated_tag = "resume-2025-01-01"
    paths = (
        f"/resume/resume.pdf",
        f"/{dated_tag}/resume.pdf",
    )
    return [
        LinkRef(file=_SEEDED_FILE, tag="seeded", href=f"{RELEASE_URL_BASE}{p}", line=0)
        for p in paths
    ]


def _request_with_headers(href: str, method: str = "HEAD", timeout: float = 10.0) -> tuple[int | str, dict[str, str]]:
    """Variant of _request that also returns response headers.

    Returns (status_or_error, headers_dict). Headers dict uses
    lowercased keys for case-insensitive lookup. On error the headers
    dict is empty.
    """
    req = urllib.request.Request(href, method=method, headers={"User-Agent": EXTERNAL_USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            headers = {k.lower(): v for k, v in resp.headers.items()}
            return resp.status, headers
    except urllib.error.HTTPError as exc:
        # HTTPError still carries response headers - useful for debugging
        # but we don't need them on the failure path.
        return exc.code, {}
    except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
        return f"network error: {exc}", {}


def check_external_strict(ref: LinkRef) -> str | None:
    """Status check (delegates to check_external) PLUS Content-Type
    assertion against EXPECTED_CONTENT_TYPES[suffix].

    Returns an error string on Content-Type mismatch; None on pass. If
    the URL's suffix isn't in EXPECTED_CONTENT_TYPES, no Content-Type
    check runs (status-only - same behaviour as check_external).
    """
    # Status check first - reuse existing logic, including HEAD->GET
    # fallback, lenient hosts, and host allowlist.
    status_err = check_external(ref)
    if status_err:
        return status_err

    parsed = urllib.parse.urlparse(ref.href)
    suffix = Path(parsed.path).suffix.lower()
    expected = EXPECTED_CONTENT_TYPES.get(suffix)
    if not expected:
        return None  # status-only check for unknown suffixes

    # Need the Content-Type header. HEAD usually carries it; fall back
    # to GET if a host stripped it (CDNs sometimes do).
    status, headers = _request_with_headers(ref.href, "HEAD")
    if isinstance(status, str) or status in (403, 405) or status >= 500:
        status, headers = _request_with_headers(ref.href, "GET")
        if isinstance(status, str):
            return status

    content_type = headers.get("content-type", "")
    # Content-Type may include charset suffix (e.g. "application/json; charset=utf-8");
    # split on ';' and compare the bare media type.
    media_type = content_type.split(";", 1)[0].strip().lower()
    if not media_type:
        return f"missing Content-Type header (expected one of {expected})"
    if media_type not in expected:
        return f"Content-Type {media_type!r} not in expected {expected}"
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
def _is_strict_url(href: str) -> bool:
    """True if href targets the assets-repo Pages site or the GitHub
    Releases download base. These URLs get the Content-Type-asserting
    strict check; everything else stays on the existing status check.
    """
    return href.startswith(MEDIA_REPO_URL) or href.startswith(RELEASE_URL_BASE)


def main() -> int:
    p = argparse.ArgumentParser(description="Verify every link on the portfolio resolves.")
    p.add_argument(
        "--mode",
        choices=("local", "live", "live-strict"),
        default="local",
        help="local (default): on-disk + fragment checks only. "
             "live: also crawl external URLs. "
             "live-strict: live + seeded assets-repo + Release URLs with Content-Type assertion.",
    )
    p.add_argument("--live", action="store_true",
                   help="DEPRECATED: alias for --mode live. Will be removed in a future release.")
    p.add_argument("--json", action="store_true", help="Machine-readable JSON output")
    p.add_argument("--max-workers", type=int, default=8,
                   help="Parallelism for external (--mode live/live-strict) checks. Default 8; raise carefully - high values can trip bot guards on hostile hosts.")
    args = p.parse_args()

    # Reconcile --live (deprecated) with --mode. If --live is set, force
    # mode to "live" unless the user explicitly passed --mode (in which
    # case --mode wins and --live is a no-op).
    mode = args.mode
    if args.live:
        print(
            "warning: --live is deprecated; use --mode live (or --mode live-strict) instead",
            file=sys.stderr,
        )
        if mode == "local":
            mode = "live"

    do_external = mode in ("live", "live-strict")
    do_strict = mode == "live-strict"

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
    externals_to_check: list[LinkRef] = []
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
            if do_external:
                externals_to_check.append(ref)
            continue
        report.checked_local += 1
        err = check_local(ref, ids_by_file)
        if err:
            report.failures.append((ref, err))

    # live-strict also seeds canonical assets-repo + Release URLs that
    # don't appear in any HTML on disk yet (M5 adds them; full HTML
    # cutover lands in a later milestone).
    if do_strict:
        seeded = seed_assets_urls(MEDIA_REPO_URL) + seed_release_urls()
        externals_to_check.extend(seeded)
        report.checked_external += len(seeded)

    # External checks fan out via ThreadPoolExecutor. Sequential at
    # 72 URLs * 10s timeout each was up to 12 min worst-case; 8 workers
    # collapses that to ~90 seconds without tripping bot guards.
    if externals_to_check:
        def _dispatch(ref: LinkRef) -> str | None:
            if do_strict and _is_strict_url(ref.href):
                return check_external_strict(ref)
            return check_external(ref)

        with ThreadPoolExecutor(max_workers=args.max_workers) as ex:
            futures = {ex.submit(_dispatch, ref): ref for ref in externals_to_check}
            for fut in as_completed(futures):
                ref = futures[fut]
                err = fut.result()
                if err:
                    report.failures.append((ref, err))

    out = report_json(report) if args.json else report_text(report)
    print(out)
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
