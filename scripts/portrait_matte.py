#!/usr/bin/env python3
"""
Find the current headshot, and lift its subject off the studio background so
it can be placed on a chosen ground instead of on a white rectangle.

Shared by scripts/snap-og-card.py (share card) and scripts/snap-favicon.py
(home-screen and Android adaptive icons). It lives here rather than in either
of them because both read the same photo and put it on a colored ground, and
a matte that drifts between the two shows up as two slightly different faces
across a person's own assets.

The matte assumes what a studio headshot gives you: a near-white, near-neutral
background reaching the left, right and top borders of the frame. It is not a
general-purpose matter and will not cope with a busy or dark backdrop.
"""
from __future__ import annotations

import shutil
from collections import deque
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter

HEADSHOT = "headshot-2026.jpg"
MASTER_LONG_EDGE = 1200


def find_headshot(repo_root: Path) -> Path:
    """Locate the current headshot, preferring a freshly dropped-in file.

    scripts/_in/ is gitignored, so on a fresh clone it is empty and the only
    copy of the photo is the committed master under static/originals/. Falling
    back to that means the asset scripts run against a clean checkout with no
    files fetched from anywhere; without the fallback the repo carries a
    headshot its own scripts cannot see.
    """
    for candidate in (
        repo_root / "scripts" / "_in" / HEADSHOT,
        repo_root / "static" / "originals" / HEADSHOT,
    ):
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"no headshot found. Put one at scripts/_in/{HEADSHOT}, or restore the "
        f"committed master at static/originals/{HEADSHOT}."
    )


def write_master(src_path: Path, originals: Path) -> Path:
    """Refresh the committed master from `src_path`, without re-encoding it.

    The master doubles as the fallback input above, so a lossy rewrite on every
    run would feed its own losses back in and compound. Copying the bytes when
    the photo is already inside the size budget keeps the committed copy
    identical to what came out of the camera; a 43 KB master re-encoded at
    quality 86 measured 42.7 dB PSNR against its source, with single channels
    off by as much as 16.
    """
    originals.mkdir(parents=True, exist_ok=True)
    master = originals / HEADSHOT
    if src_path.resolve() == master.resolve():
        return master  # running off the fallback; nothing to refresh
    with Image.open(src_path) as probe:
        oversized = max(probe.size) > MASTER_LONG_EDGE
    if oversized:
        with Image.open(src_path) as img:
            img = img.convert("RGB")
            scale = MASTER_LONG_EDGE / max(img.size)
            img.resize(
                (int(img.width * scale), int(img.height * scale)), Image.LANCZOS
            ).save(master, "JPEG", quality=86, optimize=True, progressive=True)
    else:
        shutil.copyfile(src_path, master)
    return master


def background_alpha(im: Image.Image) -> Image.Image:
    """Alpha for the subject, matted off a near-white studio background.

    Flood-fills white from the left, right and top borders only. The bottom
    border is excluded deliberately: at the bottom of the frame the shirt spans
    the full width, so there is no background there to find, and seeding from
    it would leak into the shirt - which is itself near-white.
    """
    w, h = im.size
    px = im.convert("RGB").load()

    WHITE_MIN, NEUTRAL_TOL = 243, 8
    white = [
        [
            min(px[x, y]) >= WHITE_MIN and (max(px[x, y]) - min(px[x, y])) <= NEUTRAL_TOL
            for x in range(w)
        ]
        for y in range(h)
    ]

    seen = [[False] * w for _ in range(h)]
    q: deque[tuple[int, int]] = deque()

    def seed(x: int, y: int) -> None:
        if white[y][x] and not seen[y][x]:
            seen[y][x] = True
            q.append((x, y))

    for y in range(h):
        seed(0, y)
        seed(w - 1, y)
    for x in range(w):
        seed(x, 0)
    while q:
        x, y = q.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h:
                seed(nx, ny)

    alpha = Image.new("L", (w, h), 255)
    ap = alpha.load()
    for y in range(h):
        for x in range(w):
            if seen[y][x]:
                ap[x, y] = 0

    # Closing bridges the notches the threshold bites out of lit fabric. The
    # shoulders take a wide kernel because a shirt edge is smooth; the hair
    # takes a narrow one because its edge is the detail worth keeping.
    def closed(img: Image.Image, k: int) -> Image.Image:
        return img.filter(ImageFilter.MaxFilter(k)).filter(ImageFilter.MinFilter(k))

    hair_split = int(h * 0.42)
    gentle, strong = closed(alpha, 3), closed(alpha, 9)
    merged = gentle.copy()
    merged.paste(strong.crop((0, hair_split, w, h)), (0, hair_split))
    band = 24
    for i in range(band):
        y = hair_split - band + i
        merged.paste(
            Image.blend(gentle.crop((0, y, w, y + 1)), strong.crop((0, y, w, y + 1)), i / band),
            (0, y),
        )

    # Erode by about two thirds of a pixel to bite off the white rim the
    # threshold leaves behind, then feather.
    eroded = merged.filter(ImageFilter.MinFilter(3))
    return Image.blend(eroded, merged, 0.35).filter(ImageFilter.GaussianBlur(0.7))


def decontaminate(im: Image.Image, alpha: Image.Image) -> Image.Image:
    """Pull edge pixels toward local subject color so no white rim survives."""
    interior = im.filter(ImageFilter.GaussianBlur(3))
    edge = ImageChops.difference(alpha, alpha.filter(ImageFilter.MinFilter(5)))
    edge = edge.filter(ImageFilter.GaussianBlur(1.0)).point(lambda v: min(255, int(v * 1.6)))
    return Image.composite(interior, im, edge)


def reconstruct_crown(
    im: Image.Image, alpha: Image.Image, pad: int = 16
) -> tuple[Image.Image, Image.Image]:
    """Paint back the few pixels of crown the source frame cuts off.

    The master is framed with the top of the head flush against the top edge,
    so the matte comes out with a flat-topped skull. That is invisible while
    the portrait bleeds off the top of the card and glaring the moment it does
    not - which is what was forcing the subject to fill the panel edge to edge.

    An ellipse is fitted to the head outline (widest row gives the centre and
    semi-major axis; the rows where the outline is still curving hard give the
    semi-minor), extrapolated above row 0, and filled with the hair color
    directly below, shaded down slightly because a crown sits away from the
    key light. The gap here measures about four pixels on a 480px master, so
    this is a repair, not an invention.
    """
    import math

    w, h = im.size
    ap = alpha.load()

    # Only the skull. Read far enough down and the widest row is the jaw or a
    # shoulder, which fits an ellipse half again too wide and builds a dome.
    scan = min(90, h)
    widths = []
    for y in range(scan):
        xs = [x for x in range(w) if ap[x, y] > 128]
        widths.append((xs[0], xs[-1]) if xs else None)

    spans = [(y, l, r) for y, lr in enumerate(widths) if lr for l, r in [lr]]
    if not spans:
        return im, alpha
    y_wide, l_wide, r_wide = max(spans, key=lambda s: s[2] - s[1])
    a = (r_wide - l_wide) / 2.0
    cx = (r_wide + l_wide) / 2.0

    # Solve the semi-minor axis on every row still clearly on the curve, and
    # take the median. Rows nearest the cut are the least trustworthy.
    b_estimates = []
    for y, l, r in spans:
        if y >= y_wide:
            continue
        hw = (r - l) / 2.0
        if not (0.35 * a <= hw <= 0.80 * a):
            continue
        denom = math.sqrt(max(1e-6, 1.0 - (hw / a) ** 2))
        b_estimates.append((y_wide - y) / denom)
    if not b_estimates:
        return im, alpha
    b_estimates.sort()
    b = b_estimates[len(b_estimates) // 2]

    missing = min(b - y_wide, pad)  # rows of crown above the frame
    if missing <= 0.5:
        return im, alpha
    print(f"  crown: ellipse a={a:.1f} b={b:.1f}, {missing:.1f}px clipped, rebuilding")

    new_im = Image.new("RGB", (w, h + pad), (255, 255, 255))
    new_im.paste(im, (0, pad))
    new_alpha = Image.new("L", (w, h + pad), 0)
    new_alpha.paste(alpha, (0, pad))

    src_px = im.convert("RGB").load()
    out_px = new_im.load()
    out_ap = new_alpha.load()
    row0_l, row0_r = widths[0] if widths[0] else (int(cx), int(cx))
    row0_hw = (row0_r - row0_l) / 2.0

    # The cap has to leave row 0 at exactly the width row 0 already is and
    # only narrow from there. Without that the ellipse can step out wider than
    # the hair it is growing from, and the result is a dome sitting on a head.
    prev_hw = row0_hw
    # Sample color a few pixels inside the hair. The boundary pixels are part
    # matte, so reading them paints the cap in grey.
    inset = 3
    sample_y = min(2, im.height - 1)

    for step in range(pad):
        y = -1 - step  # rows above the original frame
        dy = y_wide - y
        if dy >= b:
            break
        hw = min(prev_hw, a * math.sqrt(max(0.0, 1.0 - (dy / b) ** 2)))
        if hw <= 1.0:
            break
        prev_hw = hw
        yy = pad + y
        shade = 1.0 - 0.07 * min(1.0, (step + 1) / max(1.0, missing))
        left, right = cx - hw, cx + hw
        for x in range(max(0, int(left) - 1), min(w, int(right) + 2)):
            # antialias the two boundary pixels rather than stepping hard
            cov = min(1.0, max(0.0, min(x + 1 - left, right - x, 1.0)))
            if cov <= 0:
                continue
            sx = min(max(x, row0_l + inset), row0_r - inset)
            r, g, bl = src_px[sx, sample_y]
            out_px[x, yy] = (int(r * shade), int(g * shade), int(bl * shade))
            out_ap[x, yy] = max(out_ap[x, yy], int(255 * cov))

    # Soften the join so the rebuilt cap and the real hair read as one surface.
    seam = new_im.crop((0, 0, w, pad + 6)).filter(ImageFilter.GaussianBlur(1.1))
    new_im.paste(seam, (0, 0))
    new_alpha = new_alpha.filter(ImageFilter.GaussianBlur(0.6))
    return new_im, new_alpha
