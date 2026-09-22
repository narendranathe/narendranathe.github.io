#!/usr/bin/env python3
"""
Regenerate the favicon / home-screen icon set for narendranathe.github.io.

Why this exists
---------------
Photo at 16-32px is unreadable. Senior-tier portfolios (Stripe, Linear, Vercel,
Anthropic) split: monogram for the tab favicon, photo for the iOS home screen
and the Android adaptive icon. This script implements that split
deterministically so the assets can be regenerated without archaeology.

The OpenGraph share card used to be produced here too and no longer is; see
scripts/snap-og-card.py for why.

Inputs
------
A single source headshot at scripts/_in/headshot-2026.jpg (head-and-shoulders
shot; landscape or square, face visible, neutral background OK). This is the
same master scripts/snap-og-card.py reads.

Outputs (relative to repo root)
-------------------------------
- static/favicon.ico              - 16+32+48 multi-res, monogram "N"
- static/favicon-16.png           - monogram "N", 16x16
- static/favicon-32.png           - monogram "N", 32x32
- static/favicon-48.png           - monogram "N", 48x48
- static/apple-touch-icon.png     - photo on the brand ground, 180x180, head-framed crop
- static/favicon-512-maskable.png - photo on the brand ground, Android safe area
  (static/og-image.jpg is NOT written here - scripts/snap-og-card.py owns it)
- static/originals/headshot-fullbody.jpg - hero master, 1200px long edge

Usage
-----
    pip install -r scripts/requirements.txt
    # place fresh source photo at scripts/_in/headshot-2026.jpg
    python scripts/snap-favicon.py
"""
from __future__ import annotations

from pathlib import Path

import cv2
from PIL import Image, ImageDraw, ImageFont

# Same directory as this script, so a plain import resolves when it is run
# as `python scripts/snap-favicon.py`.
from portrait_matte import background_alpha, decontaminate, reconstruct_crown

# ------- Constants -------
REPO_ROOT = Path(__file__).resolve().parent.parent
STATIC = REPO_ROOT / "static"
ORIGINALS = STATIC / "originals"
INPUT_DIR = REPO_ROOT / "scripts" / "_in"

# The tab mark's ground. This was #E8743C for a long time, pulled from a
# spotlight in a photo that is no longer on the site; nothing on the page has
# been orange for several redesigns. It is now the accent the stylesheets
# actually resolve to (recruiter.css :root wins, loading last).
#
# The change also buys legibility rather than spending it: white on the orange
# measured 3.0:1, under AA, which is a poor place to put a letterform that has
# to survive 16px. White on this green measures 7.1:1.
BRAND = "#176447"  # --accent, recruiter.css
WHITE = "#FFFFFF"
# Ground behind the photo on the Android adaptive icon. The site's inverted
# band, not the generic near-black it used to be.
MASKABLE_GROUND = "#1F3D2B"  # .section-dark background, styles.css

# Crop policy. A Haar box bounds the face - brow to chin - not the head, so
# padding it by a small factor lands the top edge partway up the hair and
# chops it flat. These two numbers frame the head instead: how far above the
# box the crown sits, and how wide a square to take around it.
HEAD_ABOVE_FACE = 0.30  # crown height as a fraction of face-box height
HEAD_CROP_RATIO = 1.46  # square side as a multiple of face-box height

# Output sizes
TAB_SIZES = (16, 32, 48)
APPLE_TOUCH_SIZE = 180
MASKABLE_SIZE = 512
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


def head_crop_box(
    size: tuple[int, int], face: tuple[int, int, int, int], top_pad: int = 0
) -> tuple[int, int, int, int]:
    """Square crop box holding the whole head, not just the face box.

    Anchored to the estimated crown rather than centred on the face box: a
    centred square of any size that reaches the chin also reaches above the
    crown, and a square small enough to avoid that cuts the hair off flat.
    Anchoring at the top and letting the square run down into the collar puts
    the slack where slack looks deliberate.

    Returns a box rather than an image so the photo and its alpha can be cut
    with exactly the same numbers.
    """
    iw, ih = size
    x, y, w, h = face
    cx = x + w // 2
    side = int(h * HEAD_CROP_RATIO)
    # top_pad is the crown the matte rebuilt above the original frame.
    top = max(0, int(y + top_pad - h * HEAD_ABOVE_FACE))
    left = min(max(0, cx - side // 2), max(0, iw - side))
    # If the source cannot give a square that big, take the largest it can.
    side = min(side, iw - left, ih - top)
    return (left, top, left + side, top + side)


def render_monogram(text: str, size: int, font_size_ratio: float = 0.78) -> Image.Image:
    """Render a solid brand-colored square with a white letterform, centered."""
    img = Image.new("RGB", (size, size), BRAND)
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


def on_ground(rgb: Image.Image, alpha: Image.Image, size: int, ground: str) -> Image.Image:
    """Composite the matted subject onto a flat brand ground at `size` square."""
    canvas = Image.new("RGB", (size, size), ground)
    canvas.paste(
        rgb.resize((size, size), Image.LANCZOS),
        (0, 0),
        alpha.resize((size, size), Image.LANCZOS),
    )
    return canvas


def maskable_photo(rgb: Image.Image, alpha: Image.Image, size: int) -> Image.Image:
    """Matted subject on a safe-area-padded canvas for Android adaptive icons.

    Android crops adaptive icons into circles and rounded squares, so the
    meaningful content - the face - has to sit inside the inner 80% of the
    canvas. Two consequences:

    - The subject is matted rather than pasted as a square. A white photo tile
      on a green field turns into a white blob with green cardinal edges once
      the launcher applies its circle, which is not a design anyone chose.
    - It takes the tall crop, not the square one, so the shoulders run off the
      bottom edge. Stopping them at the safe-area line instead leaves a collar
      hovering in mid-air with ground visible underneath it.
    """
    canvas = Image.new("RGB", (size, size), MASKABLE_GROUND)
    inner = int(size * 0.80)
    inset = (size - inner) // 2
    scale = inner / rgb.width
    wh = (inner, int(round(rgb.height * scale)))
    canvas.paste(rgb.resize(wh, Image.LANCZOS), (inset, inset), alpha.resize(wh, Image.LANCZOS))
    return canvas


def _ico_frame_sizes(path: Path) -> list[tuple[int, int]]:
    """Read the frame table out of an .ico, to check what was actually written.

    Pillow reports only the frame it loaded, so `Image.open(...).info["sizes"]`
    will happily look right for a one-frame file. This reads the directory.
    """
    import struct

    data = path.read_bytes()
    _, _, count = struct.unpack("<HHH", data[:6])
    out = []
    for i in range(count):
        w, h = data[6 + i * 16], data[7 + i * 16]
        out.append((w or 256, h or 256))
    return sorted(out)


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

    # One current headshot, two consumers: this script and snap-og-card.py
    # read the same master so the tab mark, the home-screen icon and the
    # share card cannot drift onto different photos.
    portrait_src = INPUT_DIR / "headshot-2026.jpg"
    fullbody_src = INPUT_DIR / "headshot-fullbody.jpg"

    if not portrait_src.exists():
        raise FileNotFoundError(
            f"missing source photo: {portrait_src}\n"
            f"place a head-and-shoulders shot at that path and rerun."
        )

    # 1. Face detection, matte, then a head-framed square crop.
    #    Matting before cropping rather than after: the flood fill needs the
    #    background to reach the frame border, which a crop through the hair
    #    takes away.
    bbox = detect_face_bbox(portrait_src)
    portrait = Image.open(portrait_src).convert("RGB")
    alpha = background_alpha(portrait)
    padded, alpha = reconstruct_crown(portrait, alpha)
    top_pad = padded.height - portrait.height
    clean = decontaminate(padded, alpha)

    box = head_crop_box(padded.size, bbox, top_pad=top_pad)
    print(f"face box {bbox} -> head crop {box} (crown pad {top_pad}px)")
    face_crop_1024 = clean.crop(box).resize((1024, 1024), Image.LANCZOS)
    face_alpha_1024 = alpha.crop(box).resize((1024, 1024), Image.LANCZOS)

    # Same columns, run to the bottom of the frame: the maskable icon needs
    # shoulders it can bleed off the canvas edge.
    tall = (box[0], box[1], box[2], padded.height)
    tall_rgb, tall_alpha = clean.crop(tall), alpha.crop(tall)

    # 2. Monogram favicons (tab) - 16, 32, 48 PNG
    #
    #    Rendered at the target size, not supersampled and reduced. An 8:1
    #    LANCZOS reduction is a blur: it lands the stems between pixels and a
    #    16px "N" comes out grey and mushy. Rasterising at 16px instead lets
    #    the hinter put the stems on the pixel grid. The difference is large at
    #    16px, small at 48px, and 16px is the one in the tab.
    monos = {}
    for px in TAB_SIZES:
        m = render_monogram("N", px, font_size_ratio=0.85)
        m.save(STATIC / f"favicon-{px}.png", "PNG", optimize=True)
        monos[px] = m
        print(f"  static/favicon-{px}.png")

    # 3. .ico - multi-res 16+32+48, each frame the natively rendered one above
    #    rather than three reductions of a single large master.
    #    `sizes` has to name every frame wanted; `append_images` then supplies
    #    the exact image for each size it matches, and Pillow reduces the base
    #    image for any it does not. Naming only one size writes one frame.
    monos[48].save(
        STATIC / "favicon.ico",
        format="ICO",
        sizes=[(px, px) for px in TAB_SIZES],
        append_images=[monos[px] for px in TAB_SIZES],
    )
    ico_frames = _ico_frame_sizes(STATIC / "favicon.ico")
    assert ico_frames == sorted((px, px) for px in TAB_SIZES), f"ico wrote {ico_frames}"
    print(f"  static/favicon.ico {ico_frames}")

    # 4. Apple touch icon - photo on the brand ground, 180x180, full RGBA.
    #    iOS masks this into a squircle and puts it on whatever wallpaper the
    #    owner has, so a studio-white ground would read as a cut-out sticker.
    apple = on_ground(face_crop_1024, face_alpha_1024, APPLE_TOUCH_SIZE, BRAND)
    apple.save(STATIC / "apple-touch-icon.png", "PNG", optimize=True)
    print("  static/apple-touch-icon.png (180x180, full RGBA)")

    # 5. Maskable icon - photo on safe-area-padded canvas for Android
    masked = maskable_photo(tall_rgb, tall_alpha, MASKABLE_SIZE)
    masked.save(STATIC / "favicon-512-maskable.png", "PNG", optimize=True)
    print("  static/favicon-512-maskable.png (Android adaptive)")

    # 6. OG share card — deliberately NOT written here.
    #    The card is a layout (type block + matted portrait), not a crop, so it
    #    lives in scripts/snap-og-card.py. This script used to emit a flat
    #    orange block with a face pasted beside it; running it must not quietly
    #    restore that.

    # 7. Originals — downscaled to 1200px long edge to keep repo light
    # The portrait master is written by snap-og-card.py; writing it from both
    # scripts at different JPEG qualities would make the file flip-flop with
    # whichever ran last.
    for src_path, out_name in [
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
        "favicon-512-maskable.png",
    ]
    total = sum((STATIC / n).stat().st_size for n in favicon_files if (STATIC / n).exists())
    print(f"total favicon byte budget: {total} B = {total/1024:.1f} KB")


if __name__ == "__main__":
    main()
