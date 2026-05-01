"""Generate the colored-monogram skill SVGs for the trademark-restricted
or simple-icons-uncovered subset of static/skills/ (issue #71).

Tools fetched as silhouettes by snap-skills-hybrid.py do NOT appear in
this list - that script overwrites their SVG files. This script only
covers tiles that:
  - Have brand-mark trademark restrictions where recoloring monochrome
    is more risky than just not using the mark (AWS, Azure)
  - Lack simple-icons coverage as of 2026 (MCP, pgvector, SQL)
  - Are best represented by a typographic mark, not a silhouette
    (Claude / GPT-4o which OpenAI / Anthropic both publish wordmark-
    forward brand identities)

Each tile is a 48x48 viewBox with a centered monogram in JetBrains Mono,
fill set to the brand's official color (so AWS reads as orange and
Azure as blue without us recoloring a trademark-protected silhouette).

Reproducibility: re-run after editing SKILLS to regenerate the static
asset set. Output is byte-stable: same source produces identical bytes.
"""

from __future__ import annotations

from pathlib import Path

# (slug, monogram, font_size_px, brand_color_hex)
SKILLS: list[tuple[str, str, int, str]] = [
    # AI & LLM Stack
    ("claude", "C*", 18, "#D97757"),       # Anthropic warm
    ("gpt-4o", "4o", 18, "#10A37F"),       # OpenAI green
    ("mcp", "MCP", 14, "#6B5B9C"),          # purple - matches modelcontextprotocol.io
    # Languages
    ("sql", "SQL", 14, "#336791"),          # postgres-flavor blue
    # Data
    ("pgvector", "pgv", 14, "#4169E1"),    # PostgreSQL royal blue
    ("sql-server", "MSS", 13, "#CC2927"),  # MS SQL Server red (brand-restricted, monogram-safer than silhouette)
    ("delta-lake", "DL", 18, "#00ADD4"),   # Delta Lake teal
    # Cloud
    ("aws", "AWS", 13, "#FF9900"),         # AWS orange (official brand)
    ("azure", "Az", 18, "#0078D4"),        # Azure blue (official brand)
    # ETL / Lakehouse-adjacent
    ("ssis", "SSIS", 12, "#BC8D2C"),       # ETL gold; complements SQL Server red without competing
]

SVG_TEMPLATE = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" '
    'aria-hidden="true">'
    # Brand-tinted rounded-rect background gives the monogram visual
    # mass to match neighboring silhouette tiles. 0.13 opacity is the
    # sweet spot - readable on both light and dark site backgrounds.
    '<rect x="2" y="2" width="44" height="44" rx="9" '
    'fill="{color}" opacity="0.13"/>'
    '<text x="24" y="{y}" text-anchor="middle" '
    'font-family="\'JetBrains Mono\',ui-monospace,monospace" '
    'font-size="{fs}" font-weight="700" letter-spacing="0.5" '
    'fill="{color}">{m}</text>'
    "</svg>"
)


def main() -> int:
    out_dir = Path(__file__).resolve().parent.parent / "static" / "skills"
    out_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for slug, monogram, fs, color in SKILLS:
        # Vertical centering: cap-mass of JetBrains Mono ~0.7 of font-size,
        # baseline sits at y. Center cap-mass on y=24 (frame center).
        y = 24 + fs * 0.34
        svg = SVG_TEMPLATE.format(m=monogram, fs=fs, y=f"{y:.1f}", color=color)
        target = out_dir / f"{slug}.svg"
        target.write_text(svg, encoding="utf-8")
        written += 1
    print(f"wrote {written} colored-monogram skill SVGs to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
