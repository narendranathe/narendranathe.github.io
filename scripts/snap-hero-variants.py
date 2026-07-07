"""Generate hero variants in JPEG + WebP + AVIF at desktop (1200) and
mobile (800) sizes (#79 + #83).

Input: static/originals/headshot-fullbody.jpg (the photographer's master,
1200x1500).

Output (six files in static/originals/):
  Desktop variants (1200x1500):
    headshot-fullbody.jpg   -- input (NOT overwritten)
    headshot-fullbody.webp  -- new (~50% smaller than JPEG)
    headshot-fullbody.avif  -- new (~70% smaller than JPEG)
  Mobile variants (800x1000):
    headshot-fullbody-800.jpg
    headshot-fullbody-800.webp
    headshot-fullbody-800.avif

The hero <picture> serves AVIF first (best browsers + smallest bytes),
falls through to WebP (universal modern browsers), then JPEG (fallback
that works everywhere). The JPEG also stays the preload `href` so
preload-scanner cold-start works on all browsers.

Idempotent + byte-stable for the same Pillow version. Re-run after
editing the source.

Dependencies (install once):
    pip install "Pillow>=10" pillow-avif-plugin

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

# pillow-avif-plugin registers the AVIF codec on import. AVIF write is
# not built into Pillow itself.
try:
    import pillow_avif  # noqa: F401  (registers AVIF format on import)
    _HAS_AVIF = True
except ImportError:
    _HAS_AVIF = False
    print(
        "warning: pillow-avif-plugin not installed; AVIF variants will be skipped.\n"
        "  pip install pillow-avif-plugin",
        file=sys.stderr,
    )

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE = REPO_ROOT / "static" / "originals" / "headshot-fullbody.jpg"
OUT_DIR = REPO_ROOT / "static" / "originals"

DESKTOP_W = 1200
MOBILE_W = 800

# Per-format quality. AVIF is more efficient than JPEG/WebP at a given
# perceptual fidelity, so its quality number is lower.
JPEG_QUALITY = 82
WEBP_QUALITY = 80
AVIF_QUALITY = 60  # AVIF q60 ≈ JPEG q82 perceptually, ~50% fewer bytes


def emit(img: Image.Image, target: Path, fmt: str) -> int:
    """Write img to target in fmt and return file size in bytes. fmt is
    one of 'JPEG' / 'WEBP' / 'AVIF'."""
    save_kwargs: dict = {"optimize": True}
    if fmt == "JPEG":
        save_kwargs.update({
            "quality": JPEG_QUALITY,
            "progressive": True,
            "exif": b"",
            "icc_profile": None,
        })
    elif fmt == "WEBP":
        save_kwargs.update({
            "quality": WEBP_QUALITY,
            "method": 6,  # 6 = max compression effort, slowest
            "exif": b"",
            "icc_profile": None,
        })
    elif fmt == "AVIF":
        save_kwargs.update({
            "quality": AVIF_QUALITY,
            "speed": 4,  # 0..10; 4 is the libavif default. Lower = better compression, slower.
        })
    else:
        raise ValueError(f"unknown format: {fmt}")

    img.save(target, fmt, **save_kwargs)
    return target.stat().st_size


def main() -> int:
    if not SOURCE.exists():
        print(f"source missing: {SOURCE}", file=sys.stderr)
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with Image.open(SOURCE) as img:
        src_w, src_h = img.size
        rgb = img.convert("RGB")

        # Desktop (1200) — re-use source aspect; if source is already
        # 1200 wide we still re-encode for WEBP/AVIF, but skip writing
        # the JPEG (don't overwrite the master).
        desktop_w = min(DESKTOP_W, src_w)
        if desktop_w != src_w:
            desktop = rgb.resize((desktop_w, round(src_h * desktop_w / src_w)), Image.LANCZOS)
        else:
            desktop = rgb

        # Mobile (800)
        mobile_h = round(src_h * MOBILE_W / src_w)
        mobile = rgb.resize((MOBILE_W, mobile_h), Image.LANCZOS)

    src_kb = SOURCE.stat().st_size / 1024
    print(f"source: {src_w}x{src_h}  {src_kb:.1f} KB (preserved)")

    targets = [
        ("desktop", desktop, "headshot-fullbody"),
        ("mobile",  mobile,  "headshot-fullbody-800"),
    ]
    formats = [("JPEG", "jpg"), ("WEBP", "webp")]
    if _HAS_AVIF:
        formats.append(("AVIF", "avif"))

    for label, img, stem in targets:
        for fmt, ext in formats:
            target = OUT_DIR / f"{stem}.{ext}"
            # Don't overwrite the desktop JPEG master — that's the photographer's deliverable
            if label == "desktop" and ext == "jpg":
                kb = target.stat().st_size / 1024 if target.exists() else 0
                print(f"  {target.name:36s}  {img.size[0]}x{img.size[1]}  {kb:5.1f} KB  (kept)")
                continue
            bytes_ = emit(img, target, fmt)
            saving = (1 - bytes_ / SOURCE.stat().st_size) * 100
            print(f"  {target.name:36s}  {img.size[0]}x{img.size[1]}  {bytes_/1024:5.1f} KB  (-{saving:.0f}% vs source JPEG)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
