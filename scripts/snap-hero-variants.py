"""Generate the mobile hero variant from the 1200x798 source (#79).

The full hero `static/originals/headshot-fullbody.jpg` is 1200x798
(66 KB) and gets served to every viewport. On a 320-780 px mobile
viewport the image renders at ~280 px wide, so we're downloading
~3.5x more pixels than displayed.

This script generates a single 800x533 variant (~25-40 KB at JPEG
quality 82, mozjpeg-style) used as the `<source media="(max-width:
780px)">` srcset in the hero `<picture>` element. Desktop falls
through to the original 1200x798.

Idempotent + byte-stable: same input + same Pillow version produces
identical output bytes. Re-run after editing the source if the
photographer ever delivers a new master.

Usage
-----
    python scripts/snap-hero-variants.py
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("error: Pillow not installed. pip install Pillow>=10", file=sys.stderr)
    raise SystemExit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE = REPO_ROOT / "static" / "originals" / "headshot-fullbody.jpg"
TARGET = REPO_ROOT / "static" / "originals" / "headshot-fullbody-800.jpg"
TARGET_W = 800
TARGET_H = 533  # 800 * (798/1200) = 532.0; round up to 533 to match aspect within rounding
JPEG_QUALITY = 82  # quality 82 keeps perceptual fidelity at ~30 KB for this content


def main() -> int:
    if not SOURCE.exists():
        print(f"source missing: {SOURCE}", file=sys.stderr)
        return 1

    with Image.open(SOURCE) as img:
        # Match the source aspect by computing height from width
        src_w, src_h = img.size
        new_h = round(src_h * TARGET_W / src_w)
        resized = img.convert("RGB").resize((TARGET_W, new_h), Image.LANCZOS)
        # Strip EXIF + ICC profile (no metadata leaks; smaller bytes)
        resized.save(
            TARGET,
            "JPEG",
            quality=JPEG_QUALITY,
            optimize=True,
            progressive=True,
            exif=b"",
            icc_profile=None,
        )

    src_kb = SOURCE.stat().st_size / 1024
    tgt_kb = TARGET.stat().st_size / 1024
    saving = (1 - tgt_kb / src_kb) * 100
    print(f"source {src_w}x{src_h} {src_kb:.1f} KB -> {TARGET_W}x{new_h} {tgt_kb:.1f} KB (-{saving:.0f}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
