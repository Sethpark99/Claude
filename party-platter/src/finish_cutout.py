# Final polish for the platter cut-out so it sits in the deep-red poster: grade, defringe, choke, light wrap.
# Usage: python finish_cutout.py <in.png> <out.png> [--ev -0.15] [--warm 0.5] [--contrast 0.25] [--vib 0.2]
#        [--split 0.35] [--choke 1] [--defringe 6] [--wrap 0.35] [--wrap-px 18] [--bg 90,2,2]
import argparse, numpy as np
from PIL import Image, ImageFilter
ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('out')
ap.add_argument('--ev', type=float, default=-0.15, help='exposure in stops')
ap.add_argument('--warm', type=float, default=0.5, help='white balance push toward warm (0-1)')
ap.add_argument('--contrast', type=float, default=0.25, help='S-curve strength (0-1)')
ap.add_argument('--vib', type=float, default=0.2, help='vibrance: lifts muted colours more than saturated ones')
ap.add_argument('--split', type=float, default=0.35, help='split tone: shadows -> red-brown, highlights -> warm cream')
ap.add_argument('--choke', type=int, default=1, help='shrink the matte by N px (kills bright halos)')
ap.add_argument('--defringe', type=int, default=6, help='radius (px) used to pull edge colours from the interior')
ap.add_argument('--wrap', type=float, default=0.35, help='background light wrap strength on the edges')
ap.add_argument('--wrap-px', type=int, default=18); ap.add_argument('--bg', default='90,2,2')
a = ap.parse_args()
im = Image.open(a.src).convert('RGBA'); rgb = np.asarray(im)[..., :3].astype(np.float32) / 255
al_img = im.split()[3]
for _ in range(a.choke): al_img = al_img.filter(ImageFilter.MinFilter(3))
al = np.asarray(al_img).astype(np.float32) / 255

def blur(arr, r):
    # float box blur x3 (~gaussian), numpy only
    r = max(1, int(r)); out = arr.astype(np.float32)
    for _ in range(3):
        for ax in (0, 1):
            c = np.cumsum(np.pad(out, [(r + 1, r) if i == ax else (0, 0) for i in range(2)], mode='edge'), axis=ax)
            hi = np.take(c, np.arange(2 * r + 1, c.shape[ax]), axis=ax); lo = np.take(c, np.arange(0, c.shape[ax] - 2 * r - 1), axis=ax)
            out = (hi - lo) / (2 * r + 1)
    return out

# --- grade ---
x = rgb * 2 ** a.ev
x = x * np.array([1 + 0.06 * a.warm, 1 + 0.01 * a.warm, 1 - 0.09 * a.warm])
s = np.clip(x, 0, 1); x = s + a.contrast * (s * s * (3 - 2 * s) - s)                  # smoothstep S-curve
lum = (x * [0.2126, 0.7152, 0.0722]).sum(-1, keepdims=True)
sat = x.max(-1, keepdims=True) - x.min(-1, keepdims=True)
x = lum + (x - lum) * (1 + a.vib * (1 - np.clip(sat * 1.6, 0, 1)))                    # vibrance
sh, hi = np.array([0.30, 0.06, 0.03]), np.array([0.98, 0.90, 0.80])
w_sh = np.clip(1 - lum / 0.45, 0, 1) ** 2; w_hi = np.clip((lum - 0.6) / 0.4, 0, 1) ** 2
x = x + a.split * 0.25 * (w_sh * (sh - x) + w_hi * (hi - x))                          # split tone
x = np.clip(x, 0, 1)

# --- defringe: edge pixels take colour from the solid interior nearby (premultiplied blur) ---
if a.defringe:
    solid = (al > 0.97).astype(np.float32)
    w = blur(solid, a.defringe) + 1e-6
    inner = np.dstack([blur(x[..., c] * solid, a.defringe) / w for c in range(3)])
    edge = np.clip((0.97 - al) / 0.6, 0, 1)[..., None] * (w[..., None] > 0.02)
    x = x * (1 - edge) + np.clip(inner, 0, 1) * edge

# --- light wrap: background red bleeds onto the outer few px of the subject ---
if a.wrap:
    bg = np.array([float(v) for v in a.bg.split(',')]) / 255
    outside = blur(1 - al, a.wrap_px / 2)
    k = (a.wrap * outside * al)[..., None]
    x = x * (1 - k) + (x * 0.5 + bg * 0.5 * 2.2) * k                                   # screen-ish tint, not a flat fill

out = np.dstack([np.clip(x, 0, 1) * 255, al * 255]).astype(np.uint8)
Image.fromarray(out, 'RGBA').save(a.out); print(a.out, im.size)
