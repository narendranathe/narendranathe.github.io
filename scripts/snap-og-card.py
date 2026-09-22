#!/usr/bin/env python3
"""
Regenerate static/og-image.jpg - the link preview card LinkedIn, Slack and
iMessage render when the portfolio URL is shared.

Why this exists
---------------
The previous card was a flat #E8743C block with a very tight face crop pasted
beside it. Two problems: the orange predates the current palette (the site is
warm off-white with a deep green accent - there is no orange on it anywhere
except the stale favicons), and the crop cut the forehead and chin, which is
what a crop looks like when it is driven by a face-detection box rather than by
a layout.

This script builds the card as a layout instead: a deep green type block
carrying the same hierarchy the hero section uses (mono eyebrow in the accent,
Playfair tagline) and a full-bleed photo panel on the right. The subject is
matted off the blue-grey studio backdrop and set on the site's cream, rather
than a photo's own rectangle butted against the green.

Inputs
------
- The current headshot: scripts/_in/headshot-2026.* if present, otherwise the
  committed master under static/originals/. A studio shot, head and shoulders,
  on a plain backdrop that differs from the subject in hue - see
  portrait_matte for what the matte can and cannot separate.
- scripts/_fonts/{PlayfairDisplay,JetBrainsMono,Inter-SemiBold,Inter-Regular}.ttf

  scripts/_in/ and scripts/_fonts/ are both gitignored. The headshot still
  survives a fresh clone because this script commits it to static/originals/
  and reads it back from there; the fonts do not, so fetch them with:

    cd scripts/_fonts
    curl -LO "https://raw.githubusercontent.com/google/fonts/main/ofl/playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf"
    curl -LO "https://raw.githubusercontent.com/google/fonts/main/ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf"
    # Inter statics: https://github.com/rsms/inter/releases -> extras/ttf/

Outputs
-------
- static/og-image.jpg                      1200x630, the share card
- static/originals/headshot-2026.*         the committed master: a verbatim
  copy of the source, or a reduction if the source exceeds the long-edge budget

Usage
-----
    pip install -r scripts/requirements.txt
    python scripts/snap-og-card.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Same directory as this script, so a plain import resolves when it is run
# as `python scripts/snap-og-card.py`.
from portrait_matte import (
    background_alpha,
    find_headshot,
    reconstruct_crown,
    subject_geometry,
    write_master,
)

# ------- Paths -------
REPO_ROOT = Path(__file__).resolve().parent.parent
STATIC = REPO_ROOT / "static"
ORIGINALS = STATIC / "originals"
FONTS = REPO_ROOT / "scripts" / "_fonts"

# ------- Palette -------
# Lifted from styles.css .section-dark, the inverted band the career history
# already uses. Reusing it means the card and the site agree; the old orange
# agreed with nothing.
INK = (31, 61, 43)  # #1F3D2B  dark block
CREAM = (243, 238, 229)  # #F3EEE5  primary ink on dark
CREAM_SOFT = (201, 194, 180)  # #C9C2B4  secondary
# The site's --fg-muted (#9A9384) measures 3.91:1 on this ground, which is
# below AA and well below what survives a feed thumbnail. Stepped up until it
# passed; report_contrast() is the check, not the eye.
MUTED = (176, 169, 151)  # #B0A997  tertiary
ACCENT = (99, 185, 149)  # #63B995  accent green
WARM = (217, 160, 91)  # #D9A05B  warm accent
# Flat, not a gradient. A gradient behind a cut-out subject reads as two
# separate pictures; one field reads as a panel the portrait sits on.
PANEL = (243, 240, 233)

# ------- Geometry -------
CARD = (1200, 630)
PANEL_X = 736  # photo panel starts here; 61/39 split
PAD_L = 76
PAD_T = 58
PAD_B = 54
TEXT_W = PANEL_X - PAD_L - 72

# Portrait placement, scaled off the head rather than off the frame. The
# frame is whatever the photographer left round the subject and changes with
# every new photo; the head is the thing the composition is actually about,
# so sizing on it survives a swap. The subject runs off the bottom edge - a
# portrait that stops mid-chest in open space looks like a mistake - and off
# both sides at shoulder height, while keeping air around the head.
HEAD_H = 268  # crown to shoulder line, in panel pixels
CROWN_TOP = 74  # where the crown sits below the panel's top edge

# ------- Copy -------
EYEBROW = "NARENDRANATH EDARA  /  DATA ENGINEER"
TAGLINE = "Data platforms that give teams time back."
STATS = [
    ("14 days", "release cycle, from three months"),
    ("67%", "less compute, CDC pipeline"),
]
FOOTER = "narendranathe.github.io"
FOOTER_META = "Dallas, TX"


# ------- Color checks -------
def _lin(c: float) -> float:
    c /= 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = (_lin(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float:
    a, b = luminance(fg), luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def report_contrast() -> None:
    """Every ink color on the dark block, measured rather than assumed.

    The card is read at roughly 46% scale in a LinkedIn feed, so anything that
    only just clears 4.5:1 at full size is effectively unreadable in situ. The
    floor here is the WCAG AA number; the copy is sized so nothing important
    depends on the colors closest to it.
    """
    print("contrast on the dark block (#1F3D2B):")
    for name, col, floor in [
        ("cream / tagline", CREAM, 4.5),
        ("cream-soft", CREAM_SOFT, 4.5),
        ("muted / footer", MUTED, 4.5),
        ("accent / eyebrow", ACCENT, 4.5),
        ("warm / rule", WARM, 3.0),
    ]:
        ratio = contrast(col, INK)
        flag = "ok  " if ratio >= floor else "FAIL"
        print(f"  {flag} {name:<18} {ratio:5.2f}:1  (floor {floor})")


# ------- Type -------
def font(name: str, size: int, weight: int | None = None) -> ImageFont.FreeTypeFont:
    path = FONTS / name
    if not path.exists():
        raise FileNotFoundError(f"missing font: {path}\nsee the module docstring for fetch commands")
    f = ImageFont.truetype(str(path), size)
    if weight is not None:
        f.set_variation_by_axes([weight])
    return f


def draw_tracked(
    d: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    f: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    tracking: float = 0.0,
) -> float:
    """Draw text with letter spacing. PIL has no tracking, so step per glyph."""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + tracking
    return x - xy[0] - tracking


def wrap(d: ImageDraw.ImageDraw, text: str, f: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if d.textlength(trial, font=f) <= width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


# ------- Panels -------
def photo_panel(src: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Matted portrait on a flat panel, sized and placed off the head."""
    pw, ph = size
    panel = Image.new("RGB", (pw, ph), PANEL)

    alpha = background_alpha(src)
    rgb, alpha = reconstruct_crown(src.convert("RGB"), alpha)
    crown, shoulder = subject_geometry(alpha)
    scale = HEAD_H / max(1, shoulder - crown)

    tw, th = (max(1, int(round(v * scale))) for v in (rgb.width, rgb.height))
    rgb = rgb.resize((tw, th), Image.LANCZOS)
    alpha = alpha.resize((tw, th), Image.LANCZOS)

    x = (pw - tw) // 2
    y = CROWN_TOP - int(round(crown * scale))
    panel.paste(rgb, (x, y), alpha)
    print(f"  portrait: head {shoulder - crown}px -> {HEAD_H}px, {tw}x{th} at ({x},{y})")
    return panel


def build_card(src: Image.Image) -> Image.Image:
    w, h = CARD
    card = Image.new("RGB", (w, h), INK)
    card.paste(photo_panel(src, (w - PANEL_X, h)), (PANEL_X, 0))
    d = ImageDraw.Draw(card)

    f_eyebrow = font("JetBrainsMono.ttf", 19, weight=500)
    f_stat = font("Inter-SemiBold.ttf", 38)
    f_label = font("Inter-Regular.ttf", 18)
    f_foot = font("Inter-Medium.ttf", 19)

    # Set the tagline as large as it goes while still breaking in two lines.
    # Three lines shrinks every glyph for no gain and leaves an orphan; hard
    # coding a size means the next copy edit silently reflows the card.
    f_tag, tag_lines = None, None
    for size in range(66, 39, -1):
        candidate = font("PlayfairDisplay.ttf", size, weight=500)
        lines = wrap(d, TAGLINE, candidate, TEXT_W)
        if len(lines) <= 2:
            f_tag, tag_lines = candidate, lines
            break
    if f_tag is None:
        f_tag = font("PlayfairDisplay.ttf", 40, weight=500)
        tag_lines = wrap(d, TAGLINE, f_tag, TEXT_W)
    tag_size = f_tag.size
    print(f"  tagline: {tag_size}px, {len(tag_lines)} lines")

    # Measure the block, then sit it optically above centre in the space above
    # the footer. Stacking from a fixed top padding leaves whatever is left
    # over as a hole above the footer, which is what it did.
    leading = int(tag_size * 1.13)
    label_lines = max(len(wrap(d, lbl, f_label, (TEXT_W + 24) // 2 - 24)) for _, lbl in STATS)
    block_h = (19 + 44) + (len(tag_lines) * leading + 26) + (2 + 40) + (50 + label_lines * 24)
    footer_top = h - PAD_B - 19
    avail = footer_top - 28 - PAD_T
    y = PAD_T + max(0, int((avail - block_h) * 0.40))

    # Eyebrow - mono, tracked, accent green. Same treatment as .hero-role.
    draw_tracked(d, (PAD_L, y), EYEBROW, f_eyebrow, ACCENT, tracking=2.4)
    y += 19 + 44

    # Tagline - Playfair, the one display element, as on the live hero.
    for line in tag_lines:
        d.text((PAD_L, y), line, font=f_tag, fill=CREAM)
        y += leading
    y += 26

    # Rule
    d.rectangle([PAD_L, y, PAD_L + 72, y + 2], fill=WARM)
    y += 2 + 40

    # Stat tiles - value in sans (never the serif face used for the tagline),
    # label in muted sentence case. Two of them, not four: the card is read at
    # roughly 46% scale in a feed, and a fourth tile is a fourth thing nobody
    # can read.
    col_w = (TEXT_W + 24) // 2
    for i, (value, label) in enumerate(STATS):
        x = PAD_L + i * col_w
        d.text((x, y), value, font=f_stat, fill=CREAM)
        ly = y + 50
        for line in wrap(d, label, f_label, col_w - 24):
            d.text((x, ly), line, font=f_label, fill=MUTED)
            ly += 24

    # Footer
    fy = h - PAD_B - 19
    adv = d.textlength(FOOTER, font=f_foot)
    d.text((PAD_L, fy), FOOTER, font=f_foot, fill=CREAM_SOFT)
    d.text((PAD_L + adv + 14, fy), "·", font=f_foot, fill=MUTED)
    d.text((PAD_L + adv + 28, fy), FOOTER_META, font=f_foot, fill=MUTED)

    return card


def main() -> None:
    STATIC.mkdir(parents=True, exist_ok=True)

    src_path = find_headshot(REPO_ROOT)
    print(f"source: {src_path.relative_to(REPO_ROOT)}")
    report_contrast()
    print()

    src = Image.open(src_path).convert("RGB")
    card = build_card(src)

    out = STATIC / "og-image.jpg"
    card.save(out, "JPEG", quality=88, optimize=True, progressive=True, subsampling=0)
    print(f"  static/og-image.jpg  {card.size}  {out.stat().st_size/1024:.1f} KB")

    master = write_master(src_path, ORIGINALS)
    print(f"  {master.relative_to(REPO_ROOT)}  {master.stat().st_size/1024:.1f} KB")


if __name__ == "__main__":
    main()
