// Diagnostic frames: forces canonical camera framings + poses so the park can be
// inspected directly rather than through whatever the sim happened to be doing.
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');
const htmlPath = process.argv[2] || '/root/Code/sunset-yard/sunset-yard-3d.html';
const outDir = process.argv[3] || '/root/Code/sunset-yard/tools/diag';
fs.mkdirSync(outDir, { recursive: true });

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--enable-webgl', '--ignore-gpu-blocklist',
           '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
  });
  const errors = [];
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 720, deviceScaleFactor: 1 });
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', e => errors.push('PAGEERROR ' + e.message));
  await page.goto('file://' + path.resolve(htmlPath), { waitUntil: 'load', timeout: 30000 });
  await new Promise(r => setTimeout(r, 1500));
  await page.evaluate(() => { const b = document.getElementById('startBtn'); if (b) b.click(); });
  await new Promise(r => setTimeout(r, 600));

  const shots = [
    ['wall',   () => { window.__freezeCam = true; }, { cam: [-2, 6, -26], look: [-18, 2.5, -8] }],
    ['spine',  null, { cam: [8, 5.5, 6], look: [22, 1.6, 14] }],
    ['qp',     null, { cam: [-4, 6, 18], look: [-16, 2.0, 34] }],
    ['bowl',   null, { cam: [16, 7.5, 14], look: [30, -1.2, 30] }],
    ['rails',  null, { cam: [4, 2.2, -14], look: [-7, 1.4, 2] }],
    ['wide',   null, { cam: [-30, 16, -44], look: [4, 1, 6] }],
    ['grindP', async () => { window.__pose('grind'); }, { cam: [-9.5, 3.0, -3.5], look: [-7, 1.5, 2] }],
    ['airP',   async () => { window.__pose('air'); },   { cam: [3.5, 3.4, -4.5], look: [0, 3.2, 0] }],
  ];
  const info = {};
  for (const [name, pre, fr] of shots) {
    if (pre) { await page.evaluate(pre); await new Promise(r=>setTimeout(r,300)); }
    await page.evaluate((fr) => {
      window.__freezeCam = true;
      const c = window.__scene ? null : null;
      const cam = window.__cameraRef;
      void cam;
      window.__setFrame(fr.cam, fr.look);
    }, fr);
    await new Promise(r => setTimeout(r, 500));
    await page.screenshot({ path: path.join(outDir, name + '.png') });
    info[name] = await page.evaluate(() => window.__dbgCam());
  }
  await page.close();
  await browser.close();
  console.log(JSON.stringify({ errors, info }, null, 2));
})().catch(e => { console.error('DIAG FAIL:', e.message); process.exit(1); });
