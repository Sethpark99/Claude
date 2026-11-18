# Clean a rembg cut-out: kill faint alpha haze, firm up half-transparent edges (paper, skewer picks),
# erase hand-picked polygons (e.g. table wood showing through lettuce), optional gentle grade, trim.
# Usage: python clean_cutout.py <in.png> <out.png> [--erase "x1,y1 x2,y2 x3,y3 ..."]... [--lo 20] [--hi 160] [--grade]
import sys, argparse, numpy as np
from PIL import Image, ImageDraw, ImageFilter
ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('out')
ap.add_argument('--erase', action='append', default=[], help='polygon in source px, space-separated x,y pairs')
ap.add_argument('--lo', type=float, default=20); ap.add_argument('--hi', type=float, default=160)
ap.add_argument('--grade', action='store_true', help='mild contrast/saturation lift for a flat sips develop')
a = ap.parse_args()
im = Image.open(a.src).convert('RGBA'); rgb = np.asarray(im)[..., :3].astype(np.float32); al = np.asarray(im)[..., 3].astype(np.float32)
al = np.clip((al - a.lo) / (a.hi - a.lo), 0, 1) * 255          # below lo -> 0, above hi -> solid
m = Image.fromarray(al.astype(np.uint8))
if a.erase:
    d = ImageDraw.Draw(m)
    for poly in a.erase: d.polygon([tuple(map(float, p.split(','))) for p in poly.split()], fill=0)
m = m.filter(ImageFilter.GaussianBlur(1.2))                        # soften the hard cut a touch
if a.grade:
    x = rgb / 255; x = x + 0.12 * (x - 0.5) * (1 - abs(2 * x - 1))   # gentle S-curve
    g = x.mean(-1, keepdims=True); x = g + (x - g) * 1.10           # +10% saturation
    rgb = np.clip(x * 255, 0, 255)
out = Image.fromarray(np.dstack([rgb, np.asarray(m)]).astype(np.uint8), 'RGBA')
out = out.crop(m.point(lambda v: 255 if v > 8 else 0).getbbox()); out.save(a.out); print(a.out, out.size)
