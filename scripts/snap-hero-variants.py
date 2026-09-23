#!/usr/bin/env python3
"""
Generate the hero portrait's responsive variants: JPEG + WebP + AVIF, at a
desktop and a mobile width.

Input
-----
The current headshot, resolved exactly as snap-og-card.py and snap-favicon.py
resolve it: scripts/_in/headshot-2026.* if present, otherwise the committed
master under static/originals/. One photo drives the hero, the share card and
the icons, so they cannot drift apart.

Output (in static/originals/)
-----------------------------
  headshot-hero.{jpg,webp,avif}       native width, for desktop
  headshot-hero-800.{jpg,webp,avif}   800px wide, for phones

The hero <picture> serves AVIF first (smallest bytes), falls through to WebP
(universal modern), then JPEG. The JPEG stays the preload `href` so the
preload scanner works on a cold start in every browser.

These are all derived files. The master is never rewritten - see
portrait_matte.write_master for why that matters.

Never upscales. A variant wider than the master would be interpolation sold
as detail, and the hero renders at 368 CSS px at its largest, so the master's
own width already covers a 3x display with room to spare.

Usage
-----
    pip install -r scripts/requirements.txt
    python scripts/snap-hero-variants.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, features

# Same directory as this script, so a plain import resolves when it is run
# as `python scripts/snap-hero-variants.py`.
from portrait_matte import find_headshot

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "static" / "originals"

STEM = "headshot-hero"
MOBILE_W = 800

# Per-format quality. AVIF is more efficient than JPEG/WebP at a given
# perceptual fidelity, so its number is lower for the same result.
JPEG_QUALITY = 84
# The mobile JPEG is the fallback for browsers with neither AVIF nor WebP,
# so it is tuned down: a phone that reaches it is already on a slow, old
# stack and the bytes matter more there than the last few percent of
# fidelity. Every current browser takes the AVIF.
MOBILE_JPEG_QUALITY = 76
WEBP_QUALITY = 82
AVIF_QUALITY = 60


def emit(img: Image.Image, target: Path, fmt: str, mobile: bool = False) -> int:
    """Write img to target in fmt; return the file size in bytes."""
    kwargs: dict = {"optimize": True}
    if fmt == "JPEG":
        quality = MOBILE_JPEG_QUALITY if mobile else JPEG_QUALITY
        kwargs.update(quality=quality, progressive=True, exif=b"", icc_profile=None)
    elif fmt == "WEBP":
        kwargs.update(quality=WEBP_QUALITY, method=6, exif=b"", icc_profile=None)
    elif fmt == "AVIF":
        kwargs.update(quality=AVIF_QUALITY, speed=4)
    else:
        raise ValueError(f"unknown format: {fmt}")
    img.save(target, fmt, **kwargs)
    return target.stat().st_size


def main() -> int:
    src_path = find_headshot(REPO_ROOT)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with Image.open(src_path) as im:
        rgb = im.convert("RGB")
        src_w, src_h = rgb.size
        desktop = rgb.copy()
        mobile_w = min(MOBILE_W, src_w)
        mobile = rgb.resize((mobile_w, round(src_h * mobile_w / src_w)), Image.LANCZOS)

    print(f"source: {src_path.relative_to(REPO_ROOT)}  {src_w}x{src_h}")

    formats = [("JPEG", "jpg"), ("WEBP", "webp")]
    if features.check("avif"):
        formats.append(("AVIF", "avif"))
    else:
        print("warning: no AVIF codec in this Pillow; skipping AVIF variants", file=sys.stderr)

    for img, stem, is_mobile in ((desktop, STEM, False), (mobile, f"{STEM}-{mobile_w}", True)):
        for fmt, ext in formats:
            target = OUT_DIR / f"{stem}.{ext}"
            size = emit(img, target, fmt, mobile=is_mobile)
            print(f"  {target.name:28s} {img.size[0]:5d}x{img.size[1]:<5d} {size/1024:6.1f} KB")

    print()
    print(f"  hero <img> should declare width={src_w} height={src_h}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
