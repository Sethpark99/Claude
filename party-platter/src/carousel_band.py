# IG 4:5 close-up carousel, "awards poster" style: full-bleed photo, translucent Oxblood band rising from the
# bottom, left-aligned stacked dish name (Cinzel) + ingredients (Cormorant Garamond italic) + small brand line.
# Fonts/colours from the MODU Bistro brand guidelines (Cinzel + Cormorant; Oxblood / Silk Cream / Brass Gold).
# Usage: python carousel_band.py <spec.json> <outdir>
# spec.json: [{"src": "x.jpg", "name": "Chicken Katsu Sandos", "lines": ["CHICKEN", "KATSU", "SANDOS"] (optional),
#              "ingredients": "Crumbed chicken · cabbage · milk bread", "cx": 0.5, "cy": 0.4, "zoom": 1.0}, ...]
import sys, os, json
from PIL import Image, ImageOps
import build as B
W, H = 1080, 1350
OX, CREAM, BRASS = '#570E0D', '#FDF0D9', '#C49E60'
ML = 84                                                     # left margin
spec, out = json.load(open(sys.argv[1])), sys.argv[2]; os.makedirs(out, exist_ok=True)
B.FONTS['CormI'] = 'cormorant-garamond-latin-500-italic.woff2'

def crop45(path, cx, cy, zoom):
    im = ImageOps.exif_transpose(Image.open(path)).convert('RGB'); w, h = im.size
    cw = min(w, h * 4 / 5) / zoom; ch = cw * 5 / 4
    x0 = min(max(cx * w - cw / 2, 0), w - cw); y0 = min(max(cy * h - ch / 2, 0), h - ch)
    return im.crop((round(x0), round(y0), round(x0 + cw), round(y0 + ch))).resize((W * 2, H * 2), Image.LANCZOS)

def ff(f, fam, wt, st='normal'):
    return f"@font-face{{font-family:'{fam}';font-weight:{wt};font-style:{st};src:url(data:font/woff2;base64,{B.b64(os.path.join(B.HERE, B.FONTS[f]))}) format('woff2');}}"
style = ff('Cinzel', 'Cinzel', 400) + ff('CormI', 'Cormorant Garamond', 500, 'italic')

def split_name(name):
    words = name.upper().replace('&', '&').split(); lines, cur = [], ''
    for wd in words:                                        # greedy, ~11 chars per line, '&' sticks to the next word
        if cur and (len(cur) + 1 + len(wd) > 11) and cur not in ('&',): lines.append(cur); cur = wd
        else: cur = (cur + ' ' + wd).strip()
    lines.append(cur); return lines

def ltext(id_, txt, x, y, fam, size, fill, ls=0, extra=''):
    return (f'<text id="{id_}" x="{x:.1f}" y="{y:.1f}" {B.FAM[fam] if fam in B.FAM else fam} font-size="{size:.2f}" '
            f'fill="{fill}" letter-spacing="{ls:.2f}" {extra}>{B.esc(txt)}</text>')

FAMI = 'font-family="Cormorant Garamond" font-weight="500" font-style="italic"'
for i, s in enumerate(spec, 1):
    ph = crop45(s['src'], s.get('cx', .5), s.get('cy', .45), s.get('zoom', 1.0))
    lines = s.get('lines') or split_name(s['name'])
    # name size: fit the longest line into ~62% of the width, capped
    longest = max(lines, key=lambda t: B.tlen(t, 'Cinzel', 100))
    size = min(96, 0.62 * W / (B.tlen(longest, 'Cinzel', 100) / 100 + 0.02 * (len(longest) - 1)))
    lh = size * 0.98
    y_brand = H - 64; y_ing = y_brand - 62; y_last = y_ing - 58
    ys = [y_last - (len(lines) - 1 - k) * lh for k in range(len(lines))]
    band_top = (ys[0] - size * 1.6) / H                    # band starts fading in above the name block
    L = [f'<g id="01_photo"><image width="{W}" height="{H}" href="data:image/jpeg;base64,{B.b64(im=ph)}"/></g>',
         f'<g id="02_band"><rect width="{W}" height="{H}" fill="url(#band)"/></g>',
         '<g id="03_name">' + ''.join(ltext(f'name_line{k+1}', t, ML, ys[k], 'Cinzel', size, CREAM, size * 0.02) for k, t in enumerate(lines)) + '</g>',
         '<g id="04_ingredients">' + ltext('ingredients', s.get('ingredients', ''), ML + 2, y_ing, FAMI, 33, CREAM, 0.3, 'fill-opacity="0.92"') + '</g>',
         f'<g id="05_brand"><line x1="{ML+2}" y1="{y_brand-9}" x2="{ML+42}" y2="{y_brand-9}" stroke="{BRASS}" stroke-width="1.5"/>'
         + ltext('brand', 'MODU BISTRO · PARTY PLATTER', ML + 56, y_brand, 'Cinzel', 19, BRASS, 3.2) + '</g>']
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}px" height="{H}px" viewBox="0 0 {W} {H}">
<defs><style>{style}</style>
<linearGradient id="band" x1="0" y1="0" x2="0" y2="1">
<stop offset="{max(0.2, band_top - 0.10):.3f}" stop-color="{OX}" stop-opacity="0"/>
<stop offset="{band_top + 0.06:.3f}" stop-color="{OX}" stop-opacity="0.55"/>
<stop offset="{min(0.95, band_top + 0.22):.3f}" stop-color="{OX}" stop-opacity="0.82"/>
<stop offset="1" stop-color="{OX}" stop-opacity="0.90"/></linearGradient>
</defs>
{chr(10).join(L)}
</svg>'''
    p = os.path.join(out, f'MODU-Bistro_party-platter_carousel-band_{i:02d}.svg'); open(p, 'w').write(svg); print(p)
