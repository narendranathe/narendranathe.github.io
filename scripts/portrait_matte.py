#!/usr/bin/env python3
"""
Find the current headshot, and lift its subject off the studio background so
it can be placed on a chosen ground instead of on a white rectangle.

Shared by scripts/snap-og-card.py (share card) and scripts/snap-favicon.py
(home-screen and Android adaptive icons). It lives here rather than in either
of them because both read the same photo and put it on a colored ground, and
a matte that drifts between the two shows up as two slightly different faces
across a person's own assets.

Assumes a plain studio backdrop that differs from the subject in hue, not
merely in brightness, and that reaches the left, right and top borders of the
frame. That is what the current master gives: a cool blue-grey wall behind a
warm jacket. It is not a general-purpose matter and will not cope with a busy
backdrop, nor with a white wall behind a white shirt - there the two are the
same colour and no threshold separates them.
"""
from __future__ import annotations

import math
import shutil
from collections import deque
from pathlib import Path
from statistics import median

from PIL import Image, ImageFilter

HEADSHOT_STEM = "headshot-2026"
# Masters are committed in whatever format they arrived in, so no generation
# of JPEG loss is introduced just to normalise a file extension.
HEADSHOT_EXTS = (".webp", ".jpg", ".jpeg", ".png")
MASTER_LONG_EDGE = 2000


def find_headshot(repo_root: Path) -> Path:
    """Locate the current headshot, preferring a freshly dropped-in file.

    scripts/_in/ is gitignored, so on a fresh clone it is empty and the only
    copy of the photo is the committed master under static/originals/. Falling
    back to that means the asset scripts run against a clean checkout with no
    files fetched from anywhere; without the fallback the repo carries a
    headshot its own scripts cannot see.
    """
    for directory in (repo_root / "scripts" / "_in", repo_root / "static" / "originals"):
        for ext in HEADSHOT_EXTS:
            candidate = directory / f"{HEADSHOT_STEM}{ext}"
            if candidate.exists():
                return candidate
    exts = "|".join(e.lstrip(".") for e in HEADSHOT_EXTS)
    raise FileNotFoundError(
        f"no headshot found. Put one at scripts/_in/{HEADSHOT_STEM}.({exts}), or "
        f"restore the committed master under static/originals/."
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
    master = originals / f"{HEADSHOT_STEM}{src_path.suffix.lower()}"
    if src_path.resolve() == master.resolve():
        return master  # running off the fallback; nothing to refresh
    with Image.open(src_path) as probe:
        oversized = max(probe.size) > MASTER_LONG_EDGE
    if oversized:
        with Image.open(src_path) as img:
            img = img.convert("RGB")
            scale = MASTER_LONG_EDGE / max(img.size)
            small = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
            small.save(master, quality=90, method=6) if master.suffix == ".webp" else small.save(
                master, "JPEG", quality=88, optimize=True, progressive=True
            )
    else:
        shutil.copyfile(src_path, master)
    return master


def _opponent(c: tuple[int, int, int]) -> tuple[float, float]:
    """Colour as two opponent axes, independent of how bright it is.

    Brightness is the axis a studio backdrop shares with everything lit by the
    same lamps; hue is the one it does not. Separating on these two is what
    makes a mid-grey-blue wall trivially distinguishable from a warm jacket
    that happens to sit at the same luminance.
    """
    r, g, b = c
    return (b - r, g - (r + b) / 2)


def backdrop_signature(im: Image.Image, margin_frac: float = 0.02) -> tuple[int, int, int]:
    """The backdrop's colour, read from the border it is guaranteed to own."""
    w, h = im.size
    px = im.convert("RGB").load()
    m = max(3, int(min(w, h) * margin_frac))
    # Top edge and the upper half of both sides. Not the bottom: shoulders
    # reach that border in any head-and-shoulders frame.
    samples = [px[x, y] for y in range(m) for x in range(0, w, 4)]
    for y in range(m, h // 2, 4):
        samples += [px[x, y] for x in range(m)] + [px[w - 1 - x, y] for x in range(m)]
    return tuple(int(median([s[i] for s in samples])) for i in range(3))


def background_alpha(
    im: Image.Image,
    hue_tol: float = 16.0,
    lum_span: float = 62.0,
    clear_tol: float = 11.0,
    feather: float = 1.0,
    erode: float = 0.6,
) -> Image.Image:
    """Alpha for the subject, matted off a plain studio backdrop.

    Classifies on distance from the backdrop's own colour in the opponent
    axes above, then floods that classification in from the left, right and
    top borders. The bottom border is excluded deliberately: shoulders reach
    it, so seeding there walks straight into the jacket.

`clear_tol` then removes any remaining pixel that matches the backdrop
    closely, connected or not. Backdrop gets trapped between an arm and the
    frame where the flood cannot reach it. It is tighter than `hue_tol`
    because nothing vouches for those pixels but their own colour.

    The backdrop has to differ from the subject in hue, not merely in
    brightness. A white wall behind a white shirt does not, which is why this
    does not attempt one.
    """
    w, h = im.size
    px = im.convert("RGB").load()
    sig = backdrop_signature(im)
    s_op = _opponent(sig)
    s_lum = 0.299 * sig[0] + 0.587 * sig[1] + 0.114 * sig[2]

    def score(c: tuple[int, int, int]) -> tuple[float, float]:
        op = _opponent(c)
        hue = math.hypot(op[0] - s_op[0], op[1] - s_op[1])
        bright = abs((0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) - s_lum)
        return hue, bright

    def is_bg(x: int, y: int, tol: float) -> bool:
        hue, bright = score(px[x, y])
        return hue <= tol and bright <= lum_span

    seen = [[False] * w for _ in range(h)]
    q: deque[tuple[int, int]] = deque()

    def seed(x: int, y: int) -> None:
        if not seen[y][x] and is_bg(x, y, hue_tol):
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
            # Reached by the flood, or unmistakably the backdrop wherever it
            # sits. The second test uses a tighter tolerance than the flood,
            # because it answers for pixels with no connection to vouch for
            # them: only a near-exact colour match clears one.
            if seen[y][x] or is_bg(x, y, clear_tol):
                ap[x, y] = 0

    # close pinholes the threshold punches in lit fabric, then pull the edge
    # in a fraction of a pixel so no backdrop survives in the fringe
    alpha = alpha.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
    alpha = Image.blend(alpha.filter(ImageFilter.MinFilter(3)), alpha, 1 - erode)
    return alpha.filter(ImageFilter.GaussianBlur(feather))


def subject_geometry(alpha: Image.Image, head_band: float = 0.40) -> tuple[int, int]:
    """Return (crown row, shoulder row) from a matte.

    The shoulder line is where the outline stops being a head: scanning down,
    the width holds roughly steady through the skull and jaw, necks in, then
    jumps as the shoulders arrive. Taking the widest row in the upper part of
    the subject as the head's own width and calling the first row a quarter
    wider than that the shoulder line finds the transition without needing a
    second detector.

    Composition sized off these two numbers survives a change of photo;
    composition sized off the frame does not, because the frame is only
    whatever the photographer left around the subject.
    """
    ap = alpha.load()
    w, h = alpha.size
    step = max(1, w // 400)
    spans = []
    for y in range(h):
        xs = [x for x in range(0, w, step) if ap[x, y] > 128]
        spans.append((xs[0], xs[-1]) if xs else None)

    crown = next((y for y, sp in enumerate(spans) if sp), 0)
    band_end = crown + int((h - crown) * head_band)
    head_w = max((sp[1] - sp[0]) for sp in spans[crown:band_end] if sp)
    shoulder = next(
        (
            y
            for y in range(band_end, h)
            if spans[y] and (spans[y][1] - spans[y][0]) > head_w * 1.25
        ),
        band_end,
    )
    return crown, shoulder


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

    # Nothing is clipped unless the subject reaches the frame's top edge. The
    # ellipse fit is only meaningful when it does, and a photo with headroom
    # must not have a cap invented on top of it.
    if not any(ap[x, 0] > 128 for x in range(0, w, 3)):
        return im, alpha

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
