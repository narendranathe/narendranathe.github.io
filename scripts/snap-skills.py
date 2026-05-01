"""Generate the skill-grid monogram SVGs (issue #71).

Each SVG is a 48x48 viewBox with a centered monogram in JetBrains Mono,
fill=currentColor so the dark/light mode + warm-token palette flows in.

Reproducibility: re-run after editing SKILLS to regenerate the static
asset set. Output is byte-stable: same source produces identical bytes.

Why monograms (not branded logos): see docs/skills-grid-pattern.md.
Tradeoff is documented; short version: ~half the spec list (Anthropic
Claude, OpenAI, AWS, Azure, MS Fabric*, MCP) carries trademark or
brand-use risk that monochrome currentColor rendering does not
mitigate. Monograms are 100% original IP, dark-mode safe, ~250 bytes
each, and read as elegant when a wall of color logos would not.

(*Microsoft Fabric was scrapped from this portfolio entirely - that
project's outcomes are no longer cited.)
"""

from __future__ import annotations

from pathlib import Path

# (slug, monogram, font_size_px) - slug is filename + aria-label key.
SKILLS: list[tuple[str, str, int]] = [
    # AI & LLM Stack
    ("claude", "C*", 18),
    ("gpt-4o", "4o", 18),
    ("langchain", "LC", 18),
    ("mcp", "MCP", 14),
    ("faiss", "Fai", 14),
    # Languages & Frameworks
    ("python", "Py", 18),
    ("typescript", "TS", 18),
    ("sql", "SQL", 14),
    ("fastapi", "Fas", 14),
    ("pydantic", "Pyd", 14),
    ("streamlit", "St", 18),
    # Data & Storage
    ("postgresql", "Pg", 18),
    ("pgvector", "pgv", 14),
    ("redis", "Rd", 18),
    ("kafka", "Kf", 18),
    ("spark", "Sp", 18),
    ("delta-lake", "DL", 18),
    # Cloud & Deployment
    ("aws", "AWS", 13),
    ("azure", "Az", 18),
    ("docker", "Dk", 18),
    ("kubernetes", "K8s", 13),
    ("fly", "Fly", 14),
    # Observability & Ops
    ("prometheus", "Pr", 18),
    ("grafana", "Gr", 18),
    ("sentry", "Sn", 18),
    ("mlflow", "ML", 18),
    ("github-actions", "GH", 18),
]

SVG_TEMPLATE = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" '
    'fill="currentColor" aria-hidden="true">'
    '<rect x="2" y="2" width="44" height="44" rx="9" '
    'fill="none" stroke="currentColor" stroke-width="1.4" opacity="0.42"/>'
    '<text x="24" y="{y}" text-anchor="middle" '
    'font-family="\'JetBrains Mono\',ui-monospace,monospace" '
    'font-size="{fs}" font-weight="600" letter-spacing="0.5" '
    'fill="currentColor">{m}</text>'
    "</svg>"
)


def main() -> int:
    out_dir = Path(__file__).resolve().parent.parent / "static" / "skills"
    out_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for slug, monogram, fs in SKILLS:
        # Vertical centering: cap-height of JetBrains Mono ~0.7 of font-size,
        # baseline sits at y. Center cap-mass on y=24 (frame center).
        y = 24 + fs * 0.34
        svg = SVG_TEMPLATE.format(m=monogram, fs=fs, y=f"{y:.1f}")
        target = out_dir / f"{slug}.svg"
        target.write_text(svg, encoding="utf-8")
        written += 1
    print(f"wrote {written} skill SVGs to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
