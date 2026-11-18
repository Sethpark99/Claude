// node render.js <svg> <out.jpg|out.pdf> [pxWidth]
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => {
  const [svg, out, pw] = process.argv.slice(2); const b = await chromium.launch(); const p = await b.newPage();
  const url = 'file://' + path.resolve(svg);
  if (out.endsWith('.pdf')) {
    const tmp=path.join(path.dirname(path.resolve(svg)),'_r.html'); fs.writeFileSync(tmp,`<html><head><style>@page{size:841mm 1189mm;margin:0}html,body{margin:0}</style></head><body><img src="${url}" style="width:841mm;height:1189mm;display:block"></body></html>`); await p.goto('file://'+tmp);
    await p.waitForTimeout(1500); await p.pdf({ path: out, width: '841mm', height: '1189mm', printBackground: true });
  } else {
    const w = +(pw || 1400), h = Math.round(w * 1189 / 841);
    await p.setViewportSize({ width: w, height: h });
    const tmp=path.join(path.dirname(path.resolve(svg)),'_r.html'); fs.writeFileSync(tmp,`<html><body style="margin:0"><img src="${url}" style="width:${w}px;height:${h}px;display:block"></body></html>`); await p.goto('file://'+tmp);
    await p.waitForTimeout(1500); await p.screenshot({ path: out, type: 'jpeg', quality: 90 });
  }
  fs.unlinkSync(path.join(path.dirname(path.resolve(svg)),'_r.html')); await b.close();
})();
