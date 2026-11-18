# Reshape a steamer cut-out toward the reference look (shallow tray seen from higher up).
# Usage: python warp_cutout.py <in.png> <out.png> [--wall PX] [--squash F] [--vstretch S] [--keystone K]
#   --wall PX     height in source px of the steamer's front side wall (front rim top edge -> bottom edge, centre column)
#   --squash F    keep F of the wall height (0.4 = wall becomes 40% as tall); the food above is untouched
#   --vstretch S  stretch the whole cut-out vertically (1.15 = rim ellipse 15% rounder, reads more top-down)
#   --keystone K  top edge width relative to bottom (1.06 = back widened 6%, flattens the perspective)
# Then place with build.py (CROP_BOTTOM/FADE still work on top of this).
import argparse, numpy as np
from PIL import Image
ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('out')
ap.add_argument('--wall', type=float, default=0); ap.add_argument('--squash', type=float, default=1)
ap.add_argument('--vstretch', type=float, default=1); ap.add_argument('--keystone', type=float, default=1)
a = ap.parse_args()
im = Image.open(a.src).convert('RGBA'); im = im.crop(im.split()[3].point(lambda v: 255 if v > 8 else 0).getbbox())
if a.wall > 0 and a.squash < 1:
    arr = np.asarray(im).astype(np.float32); H, W = arr.shape[:2]; al = arr[..., 3]
    solid = al > 128
    yb = np.where(solid.any(0), H - 1 - np.argmax(solid[::-1], 0), 0).astype(np.float32)   # bottom edge per column
    k = max(3, W // 60) | 1; pad = np.pad(yb, k // 2, mode='edge')
    yb = np.array([np.median(pad[i:i + k]) for i in range(W)])                              # smooth lettuce spikes
    y0 = yb - a.wall                                                                         # wall top per column
    newH = int(np.ceil(H - a.wall * (1 - a.squash))) + 2
    yy = np.arange(newH, dtype=np.float32)[:, None]
    src_y = np.where(yy <= y0[None, :], yy, y0[None, :] + (yy - y0[None, :]) / a.squash)    # inverse map
    src_y = np.clip(src_y, 0, H - 1); i0 = np.floor(src_y).astype(int); i1 = np.minimum(i0 + 1, H - 1); t = (src_y - i0)[..., None]
    cols = np.arange(W)[None, :]
    out = arr[i0, cols] * (1 - t) + arr[i1, cols] * t
    im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGBA')
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
