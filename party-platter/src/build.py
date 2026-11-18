# MODU Bistro "Party Platter" poster, layout matched 1:1 to Seth's reference (photo left empty).
# All positions are in reference-image px (880 x 1209) and scaled by height, so A2 and IG 4:5 share one layout.
# Usage: python3 build.py <outdir> <version> [guides|clean|phone|photo] [cutout.png]
import os, sys, base64, io
import numpy as np
from PIL import Image, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT, VER = sys.argv[1], sys.argv[2]
MODE = sys.argv[3] if len(sys.argv) > 3 else 'guides'   # guides | clean | phone | photo
CUT = sys.argv[4] if len(sys.argv) > 4 else os.path.join(HERE, 'steamer_cutout.png')
PW = float(os.environ.get('PLATTER_W', 845))       # platter width in ref px (cut-out bbox width)
PB = float(os.environ.get('PLATTER_BOTTOM', 995))  # cut-out bottom edge in ref px
GUIDES = MODE == 'guides'

RW, RH = 880, 1209                                  # reference size
GOLD = ('#C48A5A', '#EDC79C', '#C48A5A')            # rose-gold title gradient (sampled)
LINE = '#D6A07C'                                    # corner + footer rule colour
CREAM = '#F6E6D8'
BG = (90, 2, 2)                                     # sampled background red
PANEL_LT, PANEL_DK = '#620B03', '#480001'

FONTS = {'Cinzel': 'cinzel-latin-400-normal.woff2', 'Bodoni': 'bodoni-moda-latin-400-italic.woff2',
         'Corm': 'cormorant-garamond-latin-500-normal.woff2'}
FAM = {'Cinzel': 'font-family="Cinzel" font-weight="400"',
       'Bodoni': 'font-family="Bodoni Moda" font-weight="400" font-style="italic"',
       'Corm': 'font-family="Cormorant Garamond" font-weight="500"'}
ITEMS = [['Vegetable Spring Rolls', 'Fried Dumplings', 'Deep-Fried Prawn Skewers'],
         ['Sweet & Spicy Chicken Skewers', 'Chicken Katsu Sandos', 'Bulgogi Sliders'],
         ['Vegetarian Kimbap', 'Salt & Pepper Squid', 'Mini Chocolate Cake Bites']]

def b64(path=None, im=None, fmt='JPEG'):
    if im is not None:
        buf = io.BytesIO(); im.save(buf, fmt, quality=90); return base64.b64encode(buf.getvalue()).decode()
    return base64.b64encode(open(path, 'rb').read()).decode()

def tlen(txt, font, size, ls=0):
    return ImageFont.truetype(os.path.join(HERE, FONTS[font]), 1000).getlength(txt) * size / 1000 + ls * (len(txt) - 1)

def fit(txt, font, width, ls_em):
    s = width / (tlen(txt, font, 1000) / 1000 + ls_em * (len(txt) - 1)); return s, s * ls_em

def esc(t): return t.replace('&', '&amp;')

def text(id_, txt, x, y, font, size, fill, ls=0, extra=''):
    # letter-spacing adds space after the last glyph too; shift x so the visible text stays centred
    return (f'<text id="{id_}" x="{x + ls / 2:.1f}" y="{y:.1f}" {FAM[font]} font-size="{size:.2f}" fill="{fill}" '
            f'text-anchor="middle" letter-spacing="{ls:.2f}" {extra}>{esc(txt)}</text>')

def texture(w, h, seed=5):
    """Deep red mottled velvet/paper, like the reference."""
    rng = np.random.default_rng(seed)
    def noise(scale):
        n = rng.standard_normal((h // scale + 2, w // scale + 2)).astype(np.float32)
        return np.asarray(Image.fromarray(n).resize((w, h), Image.BICUBIC))
    lum = 0.55 * noise(max(w // 4, 8)) + 0.30 * noise(max(w // 14, 4)) + 0.15 * noise(max(w // 60, 2)) + 0.06 * rng.standard_normal((h, w))
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    streak = np.sin((xx + yy * 0.9) / (w / 7.0) + 1.5 * noise(max(w // 6, 8))) * 0.5 + 0.5   # faint diagonal sheen
    img = np.array(BG, np.float32)[None, None, :] * (1 + 0.16 * lum[..., None] + 0.10 * (streak[..., None] - 0.5))
    img[..., 1:] += 2.0 * np.clip(lum, 0, None)[..., None]       # keep it a touch warm in the highlights
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    img *= (1 - 0.06 * np.clip(r - 0.8, 0, 1))[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))

# official Store 2 logo paths; emblem moved to the left of MODU (horizontal lockup, as in the reference)
LOGO = [l for l in open(os.path.join(HERE, 'logo_paths.txt')).read().split('\n') if l and not l.startswith('logo')]
WORD, EMB = LOGO[:12], LOGO[12:]
ES = 163 / 132
EX, EY = 54 - 55 - 124 * ES, 552.5 - 66 * ES
LB = (EX, 471, 946, 726)
def logo(cx, top, width):
    sc = width / (LB[2] - LB[0])
    t = f'translate({cx - (LB[0] + (LB[2]-LB[0])/2) * sc:.1f} {top - LB[1] * sc:.1f}) scale({sc:.5f})'
    emb = f'<g id="emblem" transform="translate({EX:.2f} {EY:.2f}) scale({ES:.4f}) translate(-438 -275)">' + ''.join(f'<path d="{d}"/>' for d in EMB) + '</g>'
    word = '<g id="wordmark">' + ''.join(f'<path d="{d}"/>' for d in WORD) + '</g>'
    return f'<g id="03_logo_modu-bistro" fill="{CREAM}" transform="{t}">' + emb + word + '</g>'

def build(W, H, unit_w, unit_h, name, tex_px):
    k = H / RH; cx = W / 2
    X = lambda x: cx + (x - RW / 2) * k          # centred elements
    XR = lambda x: W - (RW - x) * k              # anchored to right edge
    YB = lambda y: H - (RH - y) * k              # anchored to bottom edge
    Y = lambda y: y * k
    lw = 1.4 * k
    L = []
    tex = texture(tex_px, round(tex_px * H / W))
    L.append(f'<g id="01_background"><image width="{W}" height="{H}" preserveAspectRatio="none" href="data:image/jpeg;base64,{b64(im=tex)}"/></g>')

    # corner geometry traced from the reference
    c = ['<g id="02_corner-panels">',
         f'<rect id="tr_panel_light" x="{XR(826):.1f}" y="0" width="{W - XR(826):.1f}" height="{Y(75):.1f}" fill="{PANEL_LT}"/>',
         f'<rect id="tr_panel_dark" x="{XR(843):.1f}" y="{Y(75):.1f}" width="{W - XR(843):.1f}" height="{Y(103):.1f}" fill="{PANEL_DK}"/>',
         f'<polygon id="bl_panel_light" points="0,{YB(1100):.1f} {37*k:.1f},{YB(1143):.1f} {37*k:.1f},{YB(1180):.1f} 0,{YB(1180):.1f}" fill="#5A0603"/>',
         f'<rect id="bl_panel_bright" x="0" y="{YB(1180):.1f}" width="{37*k:.1f}" height="{H - YB(1180):.1f}" fill="#6E0F07"/>',
         '</g>',
         f'<g id="02_corner-lines" fill="none" stroke="{LINE}" stroke-width="{lw:.2f}">',
         f'<line x1="{XR(729):.1f}" y1="{Y(43):.1f}" x2="{XR(826):.1f}" y2="{Y(43):.1f}"/>',
         f'<line x1="{XR(802):.1f}" y1="0" x2="{XR(802):.1f}" y2="{Y(43):.1f}"/>',
         f'<line x1="{XR(826):.1f}" y1="0" x2="{XR(826):.1f}" y2="{Y(111):.1f}"/>',
         f'<line x1="{XR(826):.1f}" y1="{Y(75):.1f}" x2="{W}" y2="{Y(75):.1f}"/>',
         f'<polyline points="{XR(843):.1f},{Y(75):.1f} {XR(843):.1f},{Y(178):.1f} {W},{Y(178):.1f}"/>',
         f'<line x1="{37*k:.1f}" y1="{YB(1143):.1f}" x2="{37*k:.1f}" y2="{H}"/>',
         f'<line x1="0" y1="{YB(1180):.1f}" x2="{37*k:.1f}" y2="{YB(1180):.1f}"/>',
         f'<line x1="0" y1="{YB(1100):.1f}" x2="{37*k:.1f}" y2="{YB(1143):.1f}" stroke-opacity="0.35"/>',
         '</g>']
    L.append(''.join(c))

    L.append(logo(X(440), Y(45), 230 * k))

    # title + subtitle
    s, ls = fit('PARTY PLATTER', 'Cinzel', 570 * k, 0.03)
    s2, ls2 = fit('Serves 5 people', 'Bodoni', 280 * k, 0.24)
    L.append('<g id="04_title">' + text('title_party-platter', 'PARTY PLATTER', X(445), Y(172), 'Cinzel', s, 'url(#gold)', ls)
             + text('subtitle_serves-5', 'Serves 5 people', X(420), Y(203), 'Bodoni', s2, CREAM, ls2) + '</g>')

    # photo slot (empty): guides traced from the reference platter footprint; hide/delete before print
    if GUIDES:
        g = [f'<g id="05_PHOTO-SLOT_guides" fill="none" stroke="{CREAM}" stroke-opacity="0.45" stroke-width="{lw:.2f}">',
             f'<rect id="food-top-limit_zone" x="{X(15):.1f}" y="{Y(209):.1f}" width="{845*k:.1f}" height="{786*k:.1f}" stroke-dasharray="{6*k:.1f} {5*k:.1f}"/>',
             f'<ellipse id="steamer-rim_ref" cx="{X(437):.1f}" cy="{Y(707):.1f}" rx="{422*k:.1f}" ry="{288*k:.1f}" stroke="{LINE}" stroke-opacity="0.8" stroke-dasharray="{10*k:.1f} {6*k:.1f}"/>',
             '</g>']
        g.append(f'<g id="05_PHOTO-SLOT_label" fill="{CREAM}" fill-opacity="0.6">'
                 + text('slot_label', 'PLATTER PHOTO HERE', X(437), Y(700), 'Cinzel', 15 * k, CREAM, 3 * k)
                 + text('slot_note', 'Cut-out PNG on this layer. Food may rise to the dashed line.', X(437), Y(728), 'Corm', 14 * k, CREAM) + '</g>')
        L.append(''.join(g))
    if MODE in ('phone', 'photo'):
        # cut-out PNG: trimmed to its alpha bbox, centred, bottom edge on the reference rim line
        im = Image.open(CUT).convert('RGBA'); im = im.crop(im.split()[3].point(lambda a: 255 if a > 8 else 0).getbbox())
        ar = im.size[1] / im.size[0]
        pw = PW * k; phh = pw * ar; px = X(437) - pw / 2; py = Y(PB) - phh
        tw = min(im.size[0], 3600) if W > 2000 else 1200
        im = im.resize((tw, round(tw * ar)), Image.LANCZOS)
        L.append('<g id="05_PHOTO_platter">'
                 f'<ellipse id="photo_shadow" cx="{X(437):.1f}" cy="{Y(PB - 12):.1f}" rx="{pw*0.50:.1f}" ry="{38*k:.1f}" fill="url(#shadow)"/>'
                 f'<image id="photo_platter_cutout" x="{px:.1f}" y="{py:.1f}" width="{pw:.1f}" height="{phh:.1f}" href="data:image/png;base64,{b64(im=im, fmt="PNG")}"/></g>')
    else:
        L.append('<g id="05_PHOTO_platter"></g>')

    # item list
    sep = '\u2002\u00b7\u2002'   # en spaces (SVG collapses plain double spaces)
    lines = [sep.join(r) for r in ITEMS]
    s3, ls3 = fit(lines[1], 'Corm', 737 * k, 0.05)
    L.append('<g id="06_item-list">' + ''.join(text(f'items_line{i+1}', t, X(441), Y(1019 + i * 31.5), 'Corm', s3, CREAM, ls3)
                                               for i, t in enumerate(lines)) + '</g>')

    # footer
    ft = 'BURWOOD HOTEL\u2002\u00d7\u2002MODU BISTRO'
    s4, ls4 = fit(ft, 'Cinzel', 411 * k, 0.20)
    L.append('<g id="07_footer">' + text('footer_text', ft, X(440), Y(1135), 'Cinzel', s4, CREAM, ls4)
             + f'<line id="rule_left" x1="{X(115):.1f}" y1="{Y(1130):.1f}" x2="{X(205):.1f}" y2="{Y(1130):.1f}" stroke="{LINE}" stroke-width="{lw:.2f}"/>'
             + f'<line id="rule_right" x1="{X(677):.1f}" y1="{Y(1130):.1f}" x2="{X(767):.1f}" y2="{Y(1130):.1f}" stroke="{LINE}" stroke-width="{lw:.2f}"/></g>')

    def ff(f, fam, wt, st='normal'):
        return f"@font-face{{font-family:'{fam}';font-weight:{wt};font-style:{st};src:url(data:font/woff2;base64,{b64(os.path.join(HERE, FONTS[f]))}) format('woff2');}}"
    style = ff('Cinzel', 'Cinzel', 400) + ff('Bodoni', 'Bodoni Moda', 400, 'italic') + ff('Corm', 'Cormorant Garamond', 500)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{unit_w}" height="{unit_h}" viewBox="0 0 {W} {H}">
<defs><style>{style}</style>
<linearGradient id="gold" gradientUnits="userSpaceOnUse" x1="{X(160):.0f}" y1="0" x2="{X(730):.0f}" y2="0"><stop offset="0" stop-color="{GOLD[0]}"/><stop offset="0.5" stop-color="{GOLD[1]}"/><stop offset="1" stop-color="{GOLD[2]}"/></linearGradient>
<radialGradient id="shadow"><stop offset="0" stop-color="#000" stop-opacity="0.6"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
</defs>
{chr(10).join(L)}
</svg>'''
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f'MODU-Bistro_party-platter_{name}_{VER}.svg'); open(p, 'w').write(svg); print(p)

build(4200, 5940, '420mm', '594mm', 'A2', 2400)    # 1 unit = 0.1 mm
build(1080, 1350, '1080px', '1350px', 'IG-4x5', 1080)
