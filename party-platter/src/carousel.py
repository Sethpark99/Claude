# IG 4:5 carousel slides (1080x1350) from close-up photos, in the poster's style.
# Usage: python carousel.py <spec.json> <outdir>
# spec.json: [{"src": "DSC04417_dev.jpg", "label": "Chicken Katsu Sandos", "cx": 0.5, "cy": 0.5, "zoom": 1.0}, ...]
#   cx/cy = crop centre as a fraction of the photo, zoom >= 1 crops tighter than the largest 4:5 window.
# Each slide -> layered SVG (photo / shade / logo / label as separate groups, live text). Render JPGs with render.py.
import sys, os, json
from PIL import Image, ImageOps
import build as B
W, H = 1080, 1350
spec, out = json.load(open(sys.argv[1])), sys.argv[2]; os.makedirs(out, exist_ok=True)
DARK = '#3A0101'

def crop45(path, cx, cy, zoom):
    im = ImageOps.exif_transpose(Image.open(path)).convert('RGB'); w, h = im.size
    cw = min(w, h * 4 / 5) / zoom; ch = cw * 5 / 4
    x0 = min(max(cx * w - cw / 2, 0), w - cw); y0 = min(max(cy * h - ch / 2, 0), h - ch)
    return im.crop((round(x0), round(y0), round(x0 + cw), round(y0 + ch))).resize((W * 2, H * 2), Image.LANCZOS)

def ff(f, fam, wt, st='normal'):
    return f"@font-face{{font-family:'{fam}';font-weight:{wt};font-style:{st};src:url(data:font/woff2;base64,{B.b64(os.path.join(B.HERE, B.FONTS[f]))}) format('woff2');}}"
style = ff('Cinzel', 'Cinzel', 400) + ff('Bodoni', 'Bodoni Moda', 400, 'italic')

for i, s in enumerate(spec, 1):
    ph = crop45(s['src'], s.get('cx', .5), s.get('cy', .5), s.get('zoom', 1.0))
    lab = s['label'].upper()
    size, ls = B.fit(lab, 'Cinzel', 760, 0.12)
    size = min(size, 52); ls = size * 0.12                      # cap so short names don't get huge
    L = [f'<g id="01_photo"><image width="{W}" height="{H}" href="data:image/jpeg;base64,{B.b64(im=ph)}"/></g>',
         f'<g id="02_shade"><rect width="{W}" height="{H}" fill="url(#bottom)"/><rect width="{W}" height="300" fill="url(#top)"/></g>',
         B.logo(W / 2, 58, 210).replace('id="03_logo_modu-bistro"', 'id="03_logo"'),
         '<g id="04_label">'
         + B.text('item_name', lab, W / 2, H - 150, 'Cinzel', size, 'url(#gold)', ls)
         + f'<line id="rule" x1="{W/2-120}" y1="{H-112}" x2="{W/2+120}" y2="{H-112}" stroke="{B.LINE}" stroke-width="1.5"/>'
         + B.text('subline', 'Party Platter · Serves 5 people', W / 2, H - 62, 'Bodoni', 27, B.CREAM, 1)
         + '</g>']
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}px" height="{H}px" viewBox="0 0 {W} {H}">
<defs><style>{style}</style>
<linearGradient id="gold" gradientUnits="userSpaceOnUse" x1="{W/2-380}" y1="0" x2="{W/2+380}" y2="0"><stop offset="0" stop-color="{B.GOLD[0]}"/><stop offset="0.5" stop-color="{B.GOLD[1]}"/><stop offset="1" stop-color="{B.GOLD[2]}"/></linearGradient>
<linearGradient id="bottom" x1="0" y1="0" x2="0" y2="1"><stop offset="0.58" stop-color="{DARK}" stop-opacity="0"/><stop offset="0.86" stop-color="{DARK}" stop-opacity="0.82"/><stop offset="1" stop-color="{DARK}" stop-opacity="0.95"/></linearGradient>
<linearGradient id="top" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{DARK}" stop-opacity="0.55"/><stop offset="1" stop-color="{DARK}" stop-opacity="0"/></linearGradient>
</defs>
{chr(10).join(L)}
</svg>'''
    p = os.path.join(out, f'MODU-Bistro_party-platter_carousel_{i:02d}.svg'); open(p, 'w').write(svg); print(p)
