# Render SVGs with Playwright (Python). Usage: python render.py <svg> <out.jpg|out.pdf> [px_width]
# A2 PDF = 420x594mm page, full bleed. JPG = screenshot at px_width (default 1400); aspect read from the SVG name.
# A temp HTML is written next to the SVG and opened via file:// (Chromium blocks file:// images on about:blank).
import sys, os, pathlib
from playwright.sync_api import sync_playwright
svg, out = sys.argv[1], sys.argv[2]; pw = int(sys.argv[3]) if len(sys.argv) > 3 else 1400
sp = pathlib.Path(svg).resolve(); tmp = sp.parent / '_render_tmp.html'
ar = 1350 / 1080 if ('IG' in sp.name or 'carousel' in sp.name) else 594 / 420
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    if out.endswith('.pdf'):
        tmp.write_text(f'<html><head><style>@page{{size:420mm 594mm;margin:0}}html,body{{margin:0}}</style></head>'
                       f'<body><img src="{sp.name}" style="width:420mm;height:594mm;display:block"></body></html>')
        pg.goto(tmp.as_uri()); pg.wait_for_timeout(2500); pg.pdf(path=out, width='420mm', height='594mm', print_background=True)
    else:
        h = round(pw * ar); pg.set_viewport_size({'width': pw, 'height': h})
        tmp.write_text(f'<html><body style="margin:0"><img src="{sp.name}" style="width:{pw}px;height:{h}px;display:block"></body></html>')
        pg.goto(tmp.as_uri()); pg.wait_for_timeout(2500); pg.screenshot(path=out, type='jpeg', quality=95)
    b.close()
tmp.unlink(missing_ok=True); print(out)
