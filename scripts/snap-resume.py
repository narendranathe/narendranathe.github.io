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
- static/resume.pdf                — canonical PDF, metadata-stripped
- static/resume-page1-preview.png  — 240x320 portrait PNG of page 1 (#67)
- static/resume.schema.json        — JSON Schema draft 2020-12
- .well-known/resume.json          — discovery sidecar
- index.html                       — auto-rewritten in place: ?v=<new-hash>

Usage
-----
    pip install -r scripts/requirements.txt
    python scripts/snap-resume.py
    python scripts/snap-resume.py --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import shutil
import struct
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
PREVIEW_PUBLIC_PATH = "/static/resume-page1-preview.png"
SPEC_VERSION = "0.1.0-experimental"

# Hover-preview thumbnail target dimensions. Portrait matches US-letter
# resume aspect (8.5x11 ≈ 0.773); 240x320 = 0.75 → minor pillar/letterbox
# absorbed into a centered white canvas.
PREVIEW_WIDTH = 240
PREVIEW_HEIGHT = 320
PREVIEW_BYTE_BUDGET = 30 * 1024  # 30 KB hard ceiling per #67 AC

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
        "preview_path": {
            "type": "string",
            "pattern": r"^/[^\s\"'<>]+\.png$",
            "description": "Repo-rooted public path of the page-1 preview PNG (#67). Optional — present only if rendering toolchain succeeded.",
        },
        "preview_hash": {
            "type": "string",
            "pattern": r"^[a-f0-9]{8}$",
            "description": "Short hash of the preview PNG bytes. Decoupled from version_hash so metadata-only PDF updates don't bust preview cache.",
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
    preview_path: Path | None = None,
    preview_public_path: str = PREVIEW_PUBLIC_PATH,
) -> dict:
    """Build a sidecar JSON object from a resume PDF.
    Pure: same input bytes → same output (modulo wall-clock date).

    If `preview_path` is provided and exists, also embeds `preview_path` +
    `preview_hash` (hash of the PNG bytes — decoupled from version_hash so a
    metadata-only PDF rebuild that produces a byte-identical PNG does NOT
    bust the hover-preview cache).
    """
    pdf_bytes = pdf_path.read_bytes()
    sha = hashlib.sha256(pdf_bytes).hexdigest()
    sidecar: dict = {
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
    if preview_path is not None and preview_path.exists():
        png_bytes = preview_path.read_bytes()
        sidecar["preview_path"] = preview_public_path
        sidecar["preview_hash"] = hashlib.sha256(png_bytes).hexdigest()[:8]
    return sidecar


def read_png_dimensions(png_bytes: bytes) -> tuple[int, int]:
    """Parse PNG IHDR width + height with stdlib only. No Pillow required.
    Used by the self-test path so CI (which doesn't install pymupdf/Pillow)
    can still verify the committed preview's geometry.
    """
    if png_bytes[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG (bad magic)")
    # IHDR is the first chunk; its data starts at byte 16 (8 magic + 4 length + 4 type).
    width, height = struct.unpack(">II", png_bytes[16:24])
    return width, height


def render_page1_preview(
    pdf_path: Path,
    output_path: Path,
    *,
    width: int = PREVIEW_WIDTH,
    height: int = PREVIEW_HEIGHT,
) -> int:
    """Render page 1 of `pdf_path` to a portrait PNG thumbnail at `output_path`.

    Returns the output file size in bytes.

    Encoding choices (deterministic given a pinned pymupdf + Pillow + zlib):
      - Render at 2× target dims, downsample with LANCZOS for crisp text AA.
      - White background composite (no alpha) — resumes are white paper, and
        a transparent PNG would leak the dark-mode card colour through.
      - 1-px subtle inset border baked in (#e6e6e6) — anchors the thumb on
        light-mode cards which are also white. Shadow stays in CSS so it
        adapts to theme.
      - PNG `optimize=True, compress_level=9`, empty PngInfo (no tIME, no
        text chunks) → no toolchain or wall-clock leakage in image metadata.

    Cross-platform byte-stability is best-effort: pinning pymupdf + Pillow
    versions in scripts/requirements.txt gets you reproducible output on the
    same arch. The committed PNG is the canonical artefact; CI verifies the
    committed file's geometry + size budget rather than re-rendering.
    """
    import pymupdf  # type: ignore[import-untyped]
    from PIL import Image, ImageDraw
    from PIL.PngImagePlugin import PngInfo

    doc = pymupdf.open(pdf_path)
    try:
        if doc.page_count < 1:
            raise ValueError(f"PDF {pdf_path} has no pages")
        page = doc[0]
        page_w = float(page.rect.width)
        page_h = float(page.rect.height)
        # Render at 2× target for cleaner LANCZOS downsample.
        scale = min(width / page_w, height / page_h) * 2.0
        mat = pymupdf.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mat, colorspace=pymupdf.csRGB, alpha=False)
        png_buf = pix.tobytes("png")
    finally:
        doc.close()

    rendered = Image.open(io.BytesIO(png_buf)).convert("RGB")
    rendered.thumbnail((width, height), Image.LANCZOS)

    canvas = Image.new("RGB", (width, height), "white")
    rx = (width - rendered.width) // 2
    ry = (height - rendered.height) // 2
    canvas.paste(rendered, (rx, ry))

    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, 0, width - 1, height - 1], outline=(230, 230, 230), width=1)

    # Quantize to a 256-colour adaptive palette → PNG-8. For a downscaled
    # mostly-white-plus-black-text thumbnail this is visually indistinguishable
    # from the RGB original but cuts the file size by ~4× (LANCZOS produces
    # lots of subtle grays during text AA which inflate RGB PNG payloads).
    paletted = canvas.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Empty PngInfo strips text/tIME chunks → no PDF-rendering-toolchain leak.
    paletted.save(
        output_path,
        format="PNG",
        optimize=True,
        compress_level=9,
        pnginfo=PngInfo(),
    )
    return output_path.stat().st_size


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

    # 3. Render page-1 hover-preview PNG (#67). Must run AFTER metadata
    # strip so the rendered pixels can't leak the source toolchain.
    preview_path = STATIC / "resume-page1-preview.png"
    try:
        preview_size = render_page1_preview(dest_pdf, preview_path)
        if preview_size > PREVIEW_BYTE_BUDGET:
            print(
                f"warning: preview {preview_size} B exceeds {PREVIEW_BYTE_BUDGET} B "
                "budget — consider reducing dims or using PNG-8 quantization.",
                file=sys.stderr,
            )
        print(f"  static/resume-page1-preview.png ({preview_size} B, {PREVIEW_WIDTH}x{PREVIEW_HEIGHT})")
    except ImportError:
        print(
            "warning: pymupdf not installed — preview NOT rendered. "
            "Run `pip install -r scripts/requirements.txt` then rerun. "
            "Existing committed preview (if any) is left untouched.",
            file=sys.stderr,
        )

    # 4. Build sidecar + schema (sidecar embeds preview_hash if PNG exists)
    sidecar = build_sidecar(dest_pdf, preview_path=preview_path)
    write_json(WELL_KNOWN / "resume.json", sidecar)
    write_json(STATIC / "resume.schema.json", JSON_SCHEMA)

    print(f"  static/resume.pdf ({size} B)")
    print(f"  static/resume.schema.json (draft 2020-12)")
    print(
        f"  .well-known/resume.json (version_hash={sidecar['version_hash']}"
        + (f", preview_hash={sidecar['preview_hash']}" if "preview_hash" in sidecar else "")
        + ")"
    )

    # 5. Auto-rewrite index.html cache-bust (PDF only — preview markup
    # is owned by issue #70's hover-preview UI, not this script).
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

    # 12. read_png_dimensions parses IHDR correctly on a synthetic PNG.
    # Build a minimal 2x3 PNG entirely from stdlib (zlib + struct + crc).
    import zlib
    from binascii import crc32

    def _make_png(w: int, h: int) -> bytes:
        def chunk(tag: bytes, data: bytes) -> bytes:
            return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc32(tag + data) & 0xFFFFFFFF)

        ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)  # 8-bit RGB
        raw = b"".join(b"\x00" + b"\xff\xff\xff" * w for _ in range(h))  # filter byte + white pixels
        idat = zlib.compress(raw, 9)
        return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")

    fake_png = _make_png(7, 11)
    assert read_png_dimensions(fake_png) == (7, 11)
    try:
        read_png_dimensions(b"not a png at all")
    except ValueError:
        pass
    else:
        raise AssertionError("read_png_dimensions should reject non-PNG input")

    # 13-15. If the committed preview PNG exists in the repo (it should, per
    # #67 AC), validate its geometry + size budget WITHOUT requiring pymupdf
    # or Pillow at test time. CI runs --self-test on Ubuntu with no extra
    # deps, so all the assertions below are stdlib-only.
    repo_preview = STATIC / "resume-page1-preview.png"
    if repo_preview.exists():
        png_bytes = repo_preview.read_bytes()
        assert png_bytes[:8] == b"\x89PNG\r\n\x1a\n", "preview is not a valid PNG"
        w, h = read_png_dimensions(png_bytes)
        assert (w, h) == (PREVIEW_WIDTH, PREVIEW_HEIGHT), (
            f"preview dims {w}x{h} != expected {PREVIEW_WIDTH}x{PREVIEW_HEIGHT}"
        )
        assert len(png_bytes) <= PREVIEW_BYTE_BUDGET, (
            f"preview size {len(png_bytes)} B exceeds budget {PREVIEW_BYTE_BUDGET} B"
        )
        # Sidecar should embed a matching preview_hash if the artefact is committed.
        sidecar_path = WELL_KNOWN / "resume.json"
        if sidecar_path.exists():
            live_sc = json.loads(sidecar_path.read_text(encoding="utf-8"))
            if "preview_hash" in live_sc:
                expected = hashlib.sha256(png_bytes).hexdigest()[:8]
                assert live_sc["preview_hash"] == expected, (
                    f"sidecar preview_hash {live_sc['preview_hash']} drift from PNG bytes ({expected})"
                )
        print(f"  preview: {len(png_bytes)} B, {w}x{h} OK")
        n_assertions = 15
    else:
        print("  preview: not committed yet (skipping geometry/size assertions)")
        n_assertions = 12

    print(f"  all {n_assertions} assertions passed")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        _smoke_tests()
        sys.exit(0)
    sys.exit(main())
