#!/usr/bin/env python3
"""
Regenerate the full favicon + social-card asset set for narendranathe.github.io.

Why this exists
---------------
Photo at 16-32px is unreadable. Senior-tier portfolios (Stripe, Linear, Vercel,
Anthropic) split: monogram for tab favicon, photo for Apple touch icon and OG
share card. This script implements that split deterministically so the assets
can be regenerated from a fresh source photo without archaeology.

Inputs
------
A single source headshot at scripts/_in/headshot-portrait.jpg (head-and-shoulders
shot; landscape or square, face visible, neutral background OK).

Outputs (relative to repo root)
-------------------------------
- static/favicon.ico              — 16+32+48 multi-res, monogram "N"
- static/favicon-16.png           — monogram "N", 16x16
- static/favicon-32.png           — monogram "N", 32x32
- static/favicon-48.png           — monogram "N", 48x48
- static/apple-touch-icon.png     — photo, 180x180, full RGBA, tight face crop
- static/favicon-512-maskable.png — photo on safe area for Android adaptive
- static/og-image.jpg             — photo, 1200x630, social share card
- static/originals/<filename>.jpg — source masters downscaled to 1200px long edge

Usage
-----
    pip install -r scripts/requirements.txt
    # place fresh source photo at scripts/_in/headshot-portrait.jpg
    python scripts/snap-favicon.py
"""
from __future__ import annotations

from pathlib import Path

import cv2
from PIL import Image, ImageDraw, ImageFont

# ------- Constants -------
REPO_ROOT = Path(__file__).resolve().parent.parent
STATIC = REPO_ROOT / "static"
ORIGINALS = STATIC / "originals"
INPUT_DIR = REPO_ROOT / "scripts" / "_in"

ORANGE = "#E8743C"  # color pulled from photo's spotlight; site brand color
WHITE = "#FFFFFF"

# Crop policy — face fills ~85% of canvas. Pull tight, like Stripe/Linear.
FACE_PADDING_RATIO = 1.18  # multiplied by detected face bbox

# Output sizes
TAB_SIZES = (16, 32, 48)
APPLE_TOUCH_SIZE = 180
MASKABLE_SIZE = 512
OG_SIZE = (1200, 630)
ORIGINAL_LONG_EDGE = 1200


# ------- Helpers -------
def detect_face_bbox(img_path: Path) -> tuple[int, int, int, int]:
    """Detect single face. Return (x, y, w, h)."""
    img = cv2.imread(str(img_path))
    if img is None:
        raise FileNotFoundError(f"could not read {img_path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
    if len(faces) == 0:
        raise RuntimeError(f"no face found in {img_path}")
    # Pick the largest face (filter out cuff buttons, microphones, etc.)
    faces = sorted(faces, key=lambda b: b[2] * b[3], reverse=True)
    return tuple(int(v) for v in faces[0])


def tight_face_crop(img: Image.Image, face: tuple[int, int, int, int]) -> Image.Image:
    """Crop a square centered on the face with FACE_PADDING_RATIO padding."""
    x, y, w, h = face
    cx, cy = x + w // 2, y + h // 2
    side = int(max(w, h) * FACE_PADDING_RATIO)
    half = side // 2
    left = max(0, cx - half)
    top = max(0, cy - half)
    right = min(img.width, cx + half)
    bottom = min(img.height, cy + half)
    # Force square (clamp to smaller dimension if image edge clipped)
    actual_side = min(right - left, bottom - top)
    return img.crop((left, top, left + actual_side, top + actual_side))


def render_monogram(text: str, size: int, font_size_ratio: float = 0.78) -> Image.Image:
    """Render solid orange square with white letterform, centered."""
    img = Image.new("RGB", (size, size), ORANGE)
    d = ImageDraw.Draw(img)

    # Try Inter Black, fall back to Arial Bold (Windows) or DejaVu Sans Bold (Linux)
    candidates = [
        REPO_ROOT / "scripts" / "_fonts" / "Inter-Black.ttf",
        Path(r"C:\Windows\Fonts\arialbd.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/Library/Fonts/Arial Bold.ttf"),
    ]
    font_path = next((str(p) for p in candidates if p.exists()), None)
    if font_path is None:
        raise RuntimeError("no bold font found; place Inter-Black.ttf in scripts/_fonts/")

    fs = int(size * font_size_ratio)
    font = ImageFont.truetype(font_path, fs)
    # Optical centering: nudge up slightly because most fonts have descender bias
    d.text((size / 2, size / 2 - size * 0.04), text, font=font, fill=WHITE, anchor="mm")
    return img


def maskable_photo(face_crop: Image.Image, size: int) -> Image.Image:
    """Place tight-cropped face on a safe-area-padded canvas for Android adaptive icons.

    Android crops adaptive icons into circles/rounded squares. To survive that
    crop, the meaningful content must sit within the inner 80% of the canvas.
    """
    canvas = Image.new("RGB", (size, size), "#1A1A1A")
    inner = int(size * 0.80)
    inset = (size - inner) // 2
    photo_inner = face_crop.resize((inner, inner), Image.LANCZOS)
    canvas.paste(photo_inner, (inset, inset))
    return canvas


def make_og_card(face_crop: Image.Image, full_src: Image.Image) -> Image.Image:
    """1200x630 OG card — photo composited onto the brand orange backdrop.

    Layout: face anchored on the right, brand-color block on the left for
    future text overlay. Falls back to a simple letterboxed photo if full_src
    is absent.
    """
    w, h = OG_SIZE
    canvas = Image.new("RGB", (w, h), ORANGE)
    # Resize face_crop to height h, centered horizontally on right 60% of canvas
    fc_h = h
    fc_w = fc_h
    fc = face_crop.resize((fc_w, fc_h), Image.LANCZOS)
    canvas.paste(fc, (w - fc_w, 0))
    return canvas


def downscale_long_edge(img: Image.Image, long_edge: int) -> Image.Image:
    if max(img.size) <= long_edge:
        return img
    if img.width >= img.height:
        scale = long_edge / img.width
    else:
        scale = long_edge / img.height
    new_size = (int(img.width * scale), int(img.height * scale))
    return img.resize(new_size, Image.LANCZOS)


# ------- Main pipeline -------
def main() -> None:
    STATIC.mkdir(parents=True, exist_ok=True)
    ORIGINALS.mkdir(parents=True, exist_ok=True)

    portrait_src = INPUT_DIR / "headshot-portrait.jpg"
    fullbody_src = INPUT_DIR / "headshot-fullbody.jpg"

    if not portrait_src.exists():
        raise FileNotFoundError(
            f"missing source photo: {portrait_src}\n"
            f"place a head-and-shoulders shot at that path and rerun."
        )

    # 1. Face detection + tight crop
    bbox = detect_face_bbox(portrait_src)
    print(f"face bbox in portrait: {bbox}")
    portrait = Image.open(portrait_src).convert("RGB")
    face_crop_master = tight_face_crop(portrait, bbox)
    # Resize to 1024 for crisp downstream
    face_crop_1024 = face_crop_master.resize((1024, 1024), Image.LANCZOS)

    # 2. Monogram favicons (tab) — 16, 32, 48 PNG
    for px in TAB_SIZES:
        # Render at 8x then downscale for cleaner antialiasing
        master_size = px * 8
        m = render_monogram("N", master_size, font_size_ratio=0.85)
        m.resize((px, px), Image.LANCZOS).save(STATIC / f"favicon-{px}.png", "PNG", optimize=True)
        print(f"  static/favicon-{px}.png")

    # 3. .ico — multi-res 16+32+48 from monogram
    mono_512 = render_monogram("N", 512, font_size_ratio=0.85)
    mono_512.save(STATIC / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
    print("  static/favicon.ico (16+32+48)")

    # 4. Apple touch icon — photo, 180x180, full RGBA, no quantization
    apple = face_crop_1024.resize((APPLE_TOUCH_SIZE, APPLE_TOUCH_SIZE), Image.LANCZOS)
    apple.save(STATIC / "apple-touch-icon.png", "PNG", optimize=True)
    print("  static/apple-touch-icon.png (180x180, full RGBA)")

    # 5. Maskable icon — photo on safe-area-padded canvas for Android
    masked = maskable_photo(face_crop_1024, MASKABLE_SIZE)
    masked.save(STATIC / "favicon-512-maskable.png", "PNG", optimize=True)
    print("  static/favicon-512-maskable.png (Android adaptive)")

    # 6. OG share card — 1200x630 photo composite
    full_img = Image.open(fullbody_src).convert("RGB") if fullbody_src.exists() else None
    og = make_og_card(face_crop_1024, full_img or portrait)
    og.save(STATIC / "og-image.jpg", "JPEG", quality=85, optimize=True, progressive=True)
    print("  static/og-image.jpg (1200x630)")

    # 7. Originals — downscaled to 1200px long edge to keep repo light
    for src_path, out_name in [
        (portrait_src, "headshot-portrait.jpg"),
        (fullbody_src, "headshot-fullbody.jpg"),
    ]:
        if not src_path.exists():
            continue
        img = Image.open(src_path).convert("RGB")
        small = downscale_long_edge(img, ORIGINAL_LONG_EDGE)
        out = ORIGINALS / out_name
        small.save(out, "JPEG", quality=82, optimize=True, progressive=True)
        print(f"  static/originals/{out_name} ({small.size}, {out.stat().st_size} B)")

    # 8. Print final byte budget
    print()
    favicon_files = [
        "favicon-16.png", "favicon-32.png", "favicon-48.png",
        "favicon.ico", "apple-touch-icon.png",
        "favicon-512-maskable.png", "og-image.jpg",
    ]
    total = sum((STATIC / n).stat().st_size for n in favicon_files if (STATIC / n).exists())
    print(f"total favicon + OG byte budget: {total} B = {total/1024:.1f} KB")


if __name__ == "__main__":
    main()
