"""One-off: upgrade ~half of static/skills/*.svg from monogram tiles
to monochrome brand silhouettes sourced from simple-icons (CC0 1.0).

Why hybrid not all-silhouettes:
- Trademark-restricted brands (Claude, OpenAI/GPT-4o, AWS, Azure) keep
  their monograms regardless of license — recoloring a trademarked
  mark is the source of risk, not the SVG license.
- Niche tools without simple-icons coverage (MCP Protocol, FAISS,
  pgvector, Delta Lake, SQL) stay as monograms.
- Everything else (15 tools) gets a simple-icons silhouette.

simple-icons license note: SVG path data is CC0; brand trademarks are
still owned by their respective companies. Personal portfolio use is
universally accepted practice in the dev community. We render in
currentColor (no brand colors) to avoid any "you used the wrong
shade of orange" brand-guide pedantry.

Idempotent: re-running with the same simple-icons version produces
byte-stable output.
"""

from __future__ import annotations

import re
import sys
import urllib.request
from pathlib import Path

# (filename slug, simple-icons slug)
# simple-icons slugs: lowercase, no spaces, sometimes prefixed for
# Apache projects ("apachespark") or Microsoft brands.
HYBRID_TARGETS: list[tuple[str, str]] = [
    ("python", "python"),
    ("typescript", "typescript"),
    ("postgresql", "postgresql"),
    ("redis", "redis"),
    ("kafka", "apachekafka"),
    ("spark", "apachespark"),
    ("fastapi", "fastapi"),
    ("pydantic", "pydantic"),
    ("streamlit", "streamlit"),
    ("docker", "docker"),
    ("kubernetes", "kubernetes"),
    ("fly", "flydotio"),
    ("prometheus", "prometheus"),
    ("grafana", "grafana"),
    ("sentry", "sentry"),
    ("mlflow", "mlflow"),
    ("github-actions", "githubactions"),
    ("langchain", "langchain"),
]

SIMPLE_ICONS_URL = (
    "https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/{slug}.svg"
)

OUT_DIR = Path(__file__).resolve().parent.parent / "static" / "skills"


def fetch(slug: str) -> str:
    url = SIMPLE_ICONS_URL.format(slug=slug)
    req = urllib.request.Request(url, headers={"User-Agent": "snap-skills-hybrid"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8")


def extract_path_d(svg_text: str) -> str:
    """Pull the d="..." attribute from the first <path> in a simple-icons
    SVG. simple-icons format always has a single <path> at viewBox 0 0 24 24."""
    m = re.search(r'<path\b[^>]*\bd="([^"]+)"', svg_text)
    if not m:
        raise ValueError(f"no <path d=...> found in svg: {svg_text[:200]}")
    return m.group(1)


def render(filename: str, path_d: str) -> str:
    """Wrap the simple-icons 24x24 path in our 48x48 viewBox with the
    standard frame + scaled silhouette."""
    # simple-icons paths are at viewBox 0 0 24. Our frame is 48x48, with
    # the inner content area 8-40 (32x32). Scale 24->32 = scale(1.333..)
    # offset (8, 8) to center the silhouette inside the frame.
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" '
        'fill="currentColor" aria-hidden="true">'
        '<rect x="2" y="2" width="44" height="44" rx="9" '
        'fill="none" stroke="currentColor" stroke-width="1.4" opacity="0.42"/>'
        '<g transform="translate(8 8) scale(1.333)">'
        f'<path d="{path_d}"/>'
        '</g>'
        '</svg>'
    )


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = 0
    failed: list[tuple[str, str]] = []
    for filename, simple_slug in HYBRID_TARGETS:
        try:
            svg = fetch(simple_slug)
            d = extract_path_d(svg)
            out = render(filename, d)
            target = OUT_DIR / f"{filename}.svg"
            target.write_text(out, encoding="utf-8")
            size = target.stat().st_size
            print(f"  {filename:20s} <- simple-icons:{simple_slug:20s} ({size}B)")
            written += 1
        except Exception as e:  # noqa: BLE001 - network failures are expected per-icon
            failed.append((filename, str(e)))
            print(f"  {filename:20s} FAILED: {e}", file=sys.stderr)
    print(f"\nwrote {written}/{len(HYBRID_TARGETS)} silhouettes")
    if failed:
        print(f"failed: {[f for f, _ in failed]}", file=sys.stderr)
    return 0 if written > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
