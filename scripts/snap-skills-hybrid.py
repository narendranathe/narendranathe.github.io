"""Fetch CC0 simple-icons silhouettes for the OFL/CC0-permissive subset
of static/skills/, render them in their official brand colors at our
48x48 viewBox, frameless (silhouette alone has enough visual mass).

Why brand colors (v3): user-requested override of the earlier monochrome
decision. Trade is real - "wall of color logos" risk vs. "instant
recognition for recruiters scanning at 3s." User priority is the latter.

License note: simple-icons publishes path data under CC0 1.0. Brand
trademarks remain with their respective owners; rendering in each
brand's official color is universally accepted practice for personal
portfolios. The official-color choice (vs. recoloring) actually
satisfies AWS / Microsoft brand guidelines that forbid recoloring.

Idempotent: re-running with the same simple-icons version produces
byte-stable output (modulo any upstream simple-icons update).
"""

from __future__ import annotations

import re
import sys
import urllib.request
from pathlib import Path

# (filename slug, simple-icons slug, brand hex color)
HYBRID_TARGETS: list[tuple[str, str, str]] = [
    # AI, LLM & RAG
    ("anthropic", "anthropic", "#D97757"),
    ("huggingface", "huggingface", "#FFD21E"),
    ("langchain", "langchain", "#1C3C3C"),
    # Languages & Frameworks
    ("python", "python", "#3776AB"),
    ("typescript", "typescript", "#3178C6"),
    ("fastapi", "fastapi", "#009688"),
    ("pydantic", "pydantic", "#E92063"),
    ("streamlit", "streamlit", "#FF4B4B"),
    # Data & Storage
    ("postgresql", "postgresql", "#4169E1"),
    ("redis", "redis", "#DC382D"),
    ("kafka", "apachekafka", "#231F20"),
    ("spark", "apachespark", "#E25A1C"),
    ("databricks", "databricks", "#FF3621"),
    # Cloud & Deployment
    ("supabase", "supabase", "#3FCF8E"),
    ("docker", "docker", "#2496ED"),
    ("kubernetes", "kubernetes", "#326CE5"),
    ("fly", "flydotio", "#7B3FE4"),
    # Observability & Ops
    ("prometheus", "prometheus", "#E6522C"),
    ("grafana", "grafana", "#F46800"),
    ("sentry", "sentry", "#362D59"),
    ("mlflow", "mlflow", "#0194E2"),
    ("airflow", "apacheairflow", "#017CEE"),
    ("github-actions", "githubactions", "#2088FF"),
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


def render(path_d: str, brand_color: str) -> str:
    """Wrap the simple-icons 24x24 path in our 48x48 viewBox in brand
    color, on a brand-tinted rounded-rect background. The 0.13-opacity
    tint matches snap-skills.py monograms so silhouettes and monograms
    read as the same tile family across the grid."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" '
        'aria-hidden="true">'
        '<rect x="2" y="2" width="44" height="44" rx="9" '
        f'fill="{brand_color}" opacity="0.13"/>'
        '<g transform="translate(8 8) scale(1.333)">'
        f'<path d="{path_d}" fill="{brand_color}"/>'
        '</g>'
        '</svg>'
    )


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = 0
    failed: list[tuple[str, str]] = []
    for filename, simple_slug, brand_color in HYBRID_TARGETS:
        try:
            svg = fetch(simple_slug)
            d = extract_path_d(svg)
            out = render(d, brand_color)
            target = OUT_DIR / f"{filename}.svg"
            target.write_text(out, encoding="utf-8")
            size = target.stat().st_size
            print(f"  {filename:20s} <- simple-icons:{simple_slug:20s} {brand_color}  ({size}B)")
            written += 1
        except Exception as e:  # noqa: BLE001 - per-icon network failures are expected
            failed.append((filename, str(e)))
            print(f"  {filename:20s} FAILED: {e}", file=sys.stderr)
    print(f"\nwrote {written}/{len(HYBRID_TARGETS)} silhouettes")
    if failed:
        print(f"failed: {[f for f, _ in failed]}", file=sys.stderr)
    return 0 if written > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
