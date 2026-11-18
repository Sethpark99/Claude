# Render the poster SVGs with Playwright (Python). Usage: python render.py <svg> <out.jpg|out.pdf> [px_width]
# A2 PDF = 420x594mm page, full bleed. JPG = screenshot at px_width (default 1400).
import sys, os, pathlib
from playwright.sync_api import sync_playwright
svg, out = sys.argv[1], sys.argv[2]; pw = int(sys.argv[3]) if len(sys.argv) > 3 else 1400
url = pathlib.Path(svg).resolve().as_uri()
is_ig = 'IG-4x5' in os.path.basename(svg)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    if out.endswith('.pdf'):
        pg.set_content(f'<html><head><style>@page{{size:420mm 594mm;margin:0}}html,body{{margin:0}}</style></head>'
                       f'<body><img src="{url}" style="width:420mm;height:594mm;display:block"></body></html>')
        pg.wait_for_timeout(2500); pg.pdf(path=out, width='420mm', height='594mm', print_background=True)
    else:
        h = round(pw * (1350 / 1080 if is_ig else 594 / 420))
        pg.set_viewport_size({'width': pw, 'height': h})
        pg.set_content(f'<html><body style="margin:0"><img src="{url}" style="width:{pw}px;height:{h}px;display:block"></body></html>')
        pg.wait_for_timeout(2500); pg.screenshot(path=out, type='jpeg', quality=95)
    b.close()
print(out)
