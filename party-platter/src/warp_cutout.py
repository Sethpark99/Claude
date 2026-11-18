# Reshape a steamer cut-out toward the reference look (shallow tray seen from higher up).
# Usage: python warp_cutout.py <in.png> <out.png> [--wall PX] [--squash F] [--vstretch S] [--keystone K]
#   --wall PX     height in source px of the steamer's front side wall (front rim top edge -> bottom edge, centre column)
#   --squash F    keep F of the wall height (0.4 = wall becomes 40% as tall); the food above is untouched
#   --vstretch S  stretch the whole cut-out vertically (1.15 = rim ellipse 15% rounder, reads more top-down)
#   --keystone K  top edge width relative to bottom (1.06 = back widened 6%, flattens the perspective)
#   The wall is located from an ellipse fitted to the steamer's base (not per-column matte edges), so paper or
#   lettuce hanging over the sides can't drag the squash out of shape; --debug draws the fit for checking.
# Then place with build.py (CROP_BOTTOM/FADE still work on top of this).
import argparse, numpy as np
from PIL import Image
ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('out')
ap.add_argument('--wall', type=float, default=0); ap.add_argument('--squash', type=float, default=1)
ap.add_argument('--vstretch', type=float, default=1); ap.add_argument('--keystone', type=float, default=1)
ap.add_argument('--debug', help='save a JPG with the fitted rim-arc (cyan) and new base (magenta) drawn on')
a = ap.parse_args()
im = Image.open(a.src).convert('RGBA'); im = im.crop(im.split()[3].point(lambda v: 255 if v > 8 else 0).getbbox())
def fit_base(al):
    """Fit the steamer's base outline (lower arc of an ellipse) from the matte's bottom edge.
    Central columns only (side overhangs of paper/lettuce would skew it); robust grid search on cx, a."""
    H, W = al.shape; solid = al > 128
    yb = np.where(solid.any(0), H - 1 - np.argmax(solid[::-1], 0), -1).astype(np.float64)
    cols = np.where(solid.any(0))[0]; x0, x1 = cols[0], cols[-1]; w = x1 - x0
    xs = np.arange(int(x0 + 0.18 * w), int(x1 - 0.18 * w)); ys = yb[xs]
    best = None
    for cx in np.linspace(x0 + 0.42 * w, x0 + 0.58 * w, 33):
        for ah in np.linspace(0.40 * w, 0.56 * w, 33):
            sv = np.sqrt(np.clip(1 - ((xs - cx) / ah) ** 2, 0, None))
            A = np.stack([np.ones_like(sv), sv], 1)
            for _ in range(3):                                    # reweighted LSQ, drops lettuce spikes
                coef, *_ = np.linalg.lstsq(A, ys, rcond=None); r = ys - A @ coef
                keep = np.abs(r) < max(4, 2.5 * np.median(np.abs(r)))
                if keep.all(): break
                coef, *_ = np.linalg.lstsq(A[keep], ys[keep], rcond=None); r = ys - A @ coef
            err = np.median(np.abs(r))
            if best is None or err < best[0]: best = (err, cx, ah, coef[0], coef[1])
    return best

if a.wall > 0 and a.squash < 1:
    arr = np.asarray(im).astype(np.float32); H, W = arr.shape[:2]; al = arr[..., 3]
    err, cx, ah, cy, b = fit_base(al)
    print(f'base ellipse fit: cx={cx:.0f} a={ah:.0f} cy={cy:.0f} b={b:.0f} (median err {err:.1f}px)')
    x = np.arange(W); sv = np.sqrt(np.clip(1 - ((x - cx) / ah) ** 2, 0, None))
    base = cy + b * sv                                   # base outline per column (continuous, also past the ends)
    y0 = base - a.wall                                   # rim lower arc = top of the visible front/side wall
    nb = y0 + a.wall * a.squash                          # new base outline
    newH = int(np.ceil(max(H - a.wall * (1 - a.squash), nb.max() + 2)))
    yy = np.arange(newH, dtype=np.float32)[:, None]
    src_y = np.where(yy <= y0[None, :], yy, y0[None, :] + (yy - y0[None, :]) / a.squash)
    src_y = np.clip(src_y, 0, H - 1); i0 = np.floor(src_y).astype(int); i1 = np.minimum(i0 + 1, H - 1); t = (src_y - i0)[..., None]
    cols = np.arange(W)[None, :]
    out = arr[i0, cols] * (1 - t) + arr[i1, cols] * t
    # clean, anti-aliased base edge from the model inside the steamer's width (no stair-stepping at the sides)
    inside = np.clip((ah - np.abs(x - cx)) + 0.5, 0, 1)[None, :]
    cover = np.clip(nb[None, :] - yy + 0.5, 0, 1)
    out[..., 3] *= (1 - inside) + inside * cover
    im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGBA')
    if a.debug:
        from PIL import ImageDraw
        dbg = im.convert('RGB'); d = ImageDraw.Draw(dbg)
        d.line([(i, float(y0[i])) for i in range(W)], fill=(0, 255, 255), width=3)
        d.line([(i, float(nb[i])) for i in range(W)], fill=(255, 0, 255), width=3)
        dbg.save(a.debug)
if a.vstretch != 1:
    im = im.resize((im.size[0], round(im.size[1] * a.vstretch)), Image.LANCZOS)
if a.keystone != 1:
    W, H = im.size; kk = a.keystone; nw = round(W * max(kk, 1)); off = (nw - W) / 2
    # output quad: top edge width W*kk, bottom edge width W, centred
    dst = [((nw - W * kk) / 2, 0), ((nw + W * kk) / 2, 0), (off + W, H), (off, H)]
    src = [(0, 0), (W, 0), (W, H), (0, H)]
    A = []; B = []
    for (x, y), (u, v) in zip(dst, src):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]; B += [u, v]
    c = np.linalg.solve(np.array(A, float), np.array(B, float))
    im = im.transform((nw, H), Image.PERSPECTIVE, tuple(c), Image.BICUBIC)
im = im.crop(im.split()[3].point(lambda v: 255 if v > 8 else 0).getbbox()); im.save(a.out); print(a.out, im.size)
