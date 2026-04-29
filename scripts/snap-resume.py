#!/usr/bin/env python3
"""
Stable canonical resume URL — drop-in for any developer's portfolio.

Why this exists
---------------
Recruiter clicks 6-month-old resume URL → 404 (file renamed). LinkedIn /
Cal.com / cold-outreach links rot every update. CDNs cache aggressively;
content updates take weeks to propagate. No version visibility; can't tell
if a resume is 2 weeks or 11 months old.

The protocol shipped here:

    1. The PDF lives at exactly ONE canonical URL — `/static/resume.pdf`.
       The filename never changes. Inbound links never break.
    2. A discovery sidecar lives at `/.well-known/resume.json` (RFC 8615).
       Any tool / extension / aggregator can probe it and read version +
       page count + last_updated metadata without parsing PDF bytes.
    3. A JSON Schema (draft 2020-12) is published at
       `/static/resume.schema.json` so adopters can validate sidecars.
    4. Cache-bust uses content-derived `version_hash` (?v=<hash>) — stable
       URL, immediate invalidation on content change.
    5. PDF metadata (Producer, CreationDate, /ID) is stripped before
       publishing to avoid toolchain fingerprinting and timing leaks.

Status: v0.1.0-experimental. The well-known path `/.well-known/resume.json`
is unregistered with IANA; for hardened deployment, vendor-prefix it (e.g.
`/.well-known/resume+<vendor>.json`) until a future registration lands.

Inputs
------
A source PDF at scripts/_in/resume.pdf (gitignored).

Outputs (relative to repo root)
-------------------------------
- static/resume.pdf            — canonical PDF, metadata-stripped
- static/resume.schema.json    — JSON Schema draft 2020-12
- .well-known/resume.json      — discovery sidecar
- index.html                   — auto-rewritten in place: ?v=<new-hash>

Usage
-----
    pip install -r scripts/requirements.txt
    python scripts/snap-resume.py
    python scripts/snap-resume.py --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

# ------- Constants -------
REPO_ROOT = Path(__file__).resolve().parent.parent
STATIC = REPO_ROOT / "static"
WELL_KNOWN = REPO_ROOT / ".well-known"
INPUT_DIR = REPO_ROOT / "scripts" / "_in"
INDEX_HTML = REPO_ROOT / "index.html"

DEFAULT_SOURCE = INPUT_DIR / "resume.pdf"
SCHEMA_URL = "https://narendranathe.github.io/static/resume.schema.json"
PORTFOLIO_HOST = "https://narendranathe.github.io"
PUBLIC_PATH = "/static/resume.pdf"
SPEC_VERSION = "0.1.0-experimental"

JSON_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": SCHEMA_URL,
    "title": "Resume Discovery Sidecar",
    "description": (
        "Stable resume URL pattern with version metadata. Place the canonical "
        "instance at /.well-known/resume.json (RFC 8615). Any tool can probe "
        "<host>/.well-known/resume.json for a portfolio's resume contract."
    ),
    "type": "object",
    "additionalProperties": False,
    "required": [
        "spec_version",
        "url",
        "byte_size",
        "page_count",
        "version_hash",
        "last_updated",
    ],
    "properties": {
        "$schema": {"type": "string", "format": "uri"},
        "spec_version": {
            "type": "string",
            "pattern": r"^\d+\.\d+\.\d+(-[a-z0-9-]+)?$",
            "description": "SemVer version of this sidecar's schema contract.",
        },
        "url": {
            "type": "string",
            "format": "uri",
            "pattern": r"^https://[^\s\"'<>]+\.pdf(\?[^\s]*)?$",
            "maxLength": 2048,
            "description": "Absolute https URL of the canonical resume PDF.",
        },
        "byte_size": {"type": "integer", "minimum": 1, "maximum": 10485760},
        "page_count": {"type": "integer", "minimum": 1, "maximum": 20},
        "sha256": {
            "type": "string",
            "pattern": r"^[a-f0-9]{64}$",
            "description": "Full SHA-256 of resume.pdf for content addressing.",
        },
        "version_hash": {
            "type": "string",
            "pattern": r"^[a-f0-9]{8}$",
            "description": "Short version hash (first 8 chars of sha256). Use as ?v=<hash> cache-bust.",
        },
        "last_updated": {
            "type": "string",
            "format": "date",
            "pattern": r"^\d{4}-\d{2}-\d{2}$",
            "description": "Date-only (YYYY-MM-DD UTC) of latest regeneration. Date-only by design — full timestamps leak job-search activity.",
        },
    },
}


# ------- Helpers -------
def count_pdf_pages(pdf_bytes: bytes) -> int:
    """Count pages by regex over PDF object catalog. No external deps.
    Robust enough for hand-authored resumes (1-3 pages); falls back to 1
    on encrypted/compressed PDFs where the page tree is hidden.
    """
    matches = re.findall(rb"/Type\s*/Page(?![s/])", pdf_bytes)
    return max(1, len(matches))


def strip_pdf_metadata(pdf_path: Path) -> None:
    """Remove identifying metadata: /Producer, /Creator, /Author,
    /CreationDate, /ModDate, XMP packet, and the trailer /ID array.
    Mitigates toolchain fingerprinting + timing-signal leaks per security
    review. In place; deterministic.
    """
    import pikepdf

    with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
        # Remove document info dictionary entirely (Producer, Creator, Author,
        # CreationDate, ModDate, etc.). Working on the trailer entry directly
        # is cross-version stable; pikepdf's docinfo accessor lacks .clear()
        # in 10.x and quirks differ across releases.
        if "/Info" in pdf.trailer:
            del pdf.trailer["/Info"]
        # Strip XMP metadata packet (separate from /Info dict).
        if "/Metadata" in pdf.Root:
            del pdf.Root["/Metadata"]
        # Replace deterministic /ID array with zeros to break cross-document
        # fingerprint correlation.
        pdf.trailer["/ID"] = pikepdf.Array(
            [pikepdf.String(b"\x00" * 16), pikepdf.String(b"\x00" * 16)]
        )
        pdf.save(pdf_path, deterministic_id=True)


def build_sidecar(
    pdf_path: Path,
    *,
    portfolio_host: str = PORTFOLIO_HOST,
    public_path: str = PUBLIC_PATH,
) -> dict:
    """Build a sidecar JSON object from a resume PDF.
    Pure: same input bytes → same output (modulo wall-clock date).
    """
    pdf_bytes = pdf_path.read_bytes()
    sha = hashlib.sha256(pdf_bytes).hexdigest()
    return {
        "$schema": SCHEMA_URL,
        "spec_version": SPEC_VERSION,
        "url": f"{portfolio_host}{public_path}",
        "byte_size": len(pdf_bytes),
        "page_count": count_pdf_pages(pdf_bytes),
        "sha256": sha,
        "version_hash": sha[:8],
        # Date-only — full ISO timestamps leak job-search activity to anyone
        # probing /.well-known/resume.json (e.g. current employer, recruiter ATS).
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }


def write_canonical_pdf(source: Path, dest: Path) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    return dest.stat().st_size


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rewrite_index_html_cache_bust(index_path: Path, new_hash: str) -> int:
    """Replace every `/static/resume.pdf?v=<old>` occurrence in index.html
    with the new hash. Returns the number of replacements made.
    """
    text = index_path.read_text(encoding="utf-8")
    pattern = re.compile(r"(/static/resume\.pdf\?v=)[a-f0-9]{8}")
    new_text, n = pattern.subn(rf"\g<1>{new_hash}", text)
    if n > 0 and new_text != text:
        index_path.write_text(new_text, encoding="utf-8")
    return n


# ------- Main pipeline -------
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Stable canonical resume URL + .well-known sidecar generator"
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help=f"path to source PDF (default: {DEFAULT_SOURCE.relative_to(REPO_ROOT)})",
    )
    parser.add_argument(
        "--no-strip-metadata",
        action="store_true",
        help="skip the PDF metadata sanitization step (NOT recommended).",
    )
    parser.add_argument(
        "--no-rewrite-html",
        action="store_true",
        help="skip rewriting index.html ?v= cache-bust.",
    )
    args = parser.parse_args(argv)

    if not args.source.exists():
        print(f"error: missing source PDF: {args.source}", file=sys.stderr)
        print("Drop your latest resume at scripts/_in/resume.pdf and rerun.", file=sys.stderr)
        return 1

    # 1. Copy PDF to canonical path
    dest_pdf = STATIC / "resume.pdf"
    size = write_canonical_pdf(args.source, dest_pdf)

    # 2. Strip identifying metadata (must happen before hashing)
    if not args.no_strip_metadata:
        try:
            strip_pdf_metadata(dest_pdf)
            size = dest_pdf.stat().st_size  # may shrink slightly
            print(f"  metadata stripped from static/resume.pdf")
        except ImportError:
            print(
                "warning: pikepdf not installed — PDF metadata NOT stripped. "
                "Run `pip install pikepdf` then rerun.",
                file=sys.stderr,
            )

    # 3. Build sidecar + schema
    sidecar = build_sidecar(dest_pdf)
    write_json(WELL_KNOWN / "resume.json", sidecar)
    write_json(STATIC / "resume.schema.json", JSON_SCHEMA)

    print(f"  static/resume.pdf ({size} B)")
    print(f"  static/resume.schema.json (draft 2020-12)")
    print(f"  .well-known/resume.json (version_hash={sidecar['version_hash']})")

    # 4. Auto-rewrite index.html cache-bust
    if not args.no_rewrite_html and INDEX_HTML.exists():
        n = rewrite_index_html_cache_bust(INDEX_HTML, sidecar["version_hash"])
        print(f"  index.html ({n} cache-bust occurrences updated)")

    return 0


# ------- Smoke tests (no pytest required; runs via __main__) -------
def _smoke_tests() -> None:
    """python scripts/snap-resume.py --self-test"""
    import tempfile

    print("snap-resume self-test...")

    pdf_bytes = (
        b"%PDF-1.4\n"
        b"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
        b"2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
        b"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]>> endobj\n"
        b"trailer <</Root 1 0 R>>\n%%EOF\n"
    )
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "fake.pdf"
        src.write_bytes(pdf_bytes)
        # 1. page count regex correctly distinguishes /Page from /Pages
        n = count_pdf_pages(pdf_bytes)
        assert n == 1, f"expected 1 page, got {n}"
        # 2. sidecar has all required fields
        sc = build_sidecar(src, portfolio_host="https://example.test")
        for k in [
            "$schema",
            "spec_version",
            "url",
            "byte_size",
            "page_count",
            "sha256",
            "version_hash",
            "last_updated",
        ]:
            assert k in sc, f"missing {k}"
        # 3. version_hash deterministic on identical bytes
        sc2 = build_sidecar(src, portfolio_host="https://example.test")
        assert sc["version_hash"] == sc2["version_hash"]
        # 4. version_hash changes on content change
        src.write_bytes(pdf_bytes + b" % comment\n")
        sc3 = build_sidecar(src, portfolio_host="https://example.test")
        assert sc["version_hash"] != sc3["version_hash"]
        # 5. byte_size matches actual file
        assert sc["byte_size"] == len(pdf_bytes)
        # 6. last_updated is date-only (YYYY-MM-DD)
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", sc["last_updated"])
        # 7. version_hash is 8 lowercase hex chars
        assert re.fullmatch(r"[a-f0-9]{8}", sc["version_hash"])
        # 8. url uses provided host + canonical path
        assert sc["url"] == "https://example.test/static/resume.pdf"
        # 9. spec_version is set
        assert sc["spec_version"] == SPEC_VERSION
        # 10. cache-bust rewrite is idempotent on input without occurrences
        empty_html = Path(td) / "empty.html"
        empty_html.write_text("<html><body>no resume link</body></html>", encoding="utf-8")
        assert rewrite_index_html_cache_bust(empty_html, "deadbeef") == 0
        # 11. cache-bust rewrite replaces all occurrences
        with_html = Path(td) / "with.html"
        with_html.write_text(
            'a <a href="/static/resume.pdf?v=11111111">x</a>'
            ' b <a href="/static/resume.pdf?v=22222222">y</a>',
            encoding="utf-8",
        )
        n = rewrite_index_html_cache_bust(with_html, "deadbeef")
        assert n == 2
        new = with_html.read_text(encoding="utf-8")
        assert new.count("?v=deadbeef") == 2
        assert "?v=11111111" not in new and "?v=22222222" not in new

    print("  all 11 assertions passed")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        _smoke_tests()
        sys.exit(0)
    sys.exit(main())
