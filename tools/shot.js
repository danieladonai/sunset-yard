// Screenshot harness for the visual-critic loop.
// Loads the game file headlessly, clicks Drop In, lets the 3D scene run, and
// captures PNGs (desktop + mobile) plus any console errors.
// Usage: NODE_PATH=$(npm root -g) node shot.js <htmlPath> <outDir>
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const htmlPath = process.argv[2] || '/root/Code/sunset-yard/sunset-yard-3d.html';
const outDir = process.argv[3] || '/root/Code/sunset-yard/tools/shots';
fs.mkdirSync(outDir, { recursive: true });

const VIEWS = [
  { name: 'desktop', w: 1280, h: 720, mobile: false },
  { name: 'mobile',  w: 390,  h: 844, mobile: true  },
];

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--enable-webgl', '--ignore-gpu-blocklist',
           '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
  });
  const report = { errors: [], shots: [] };
  for (const v of VIEWS) {
    const page = await browser.newPage();
    await page.setViewport({ width: v.w, height: v.h, isMobile: v.mobile, hasTouch: v.mobile, deviceScaleFactor: 1 });
    page.on('console', m => { if (m.type() === 'error') report.errors.push(`[${v.name}] ${m.text()}`); });
    page.on('pageerror', e => report.errors.push(`[${v.name}] PAGEERROR ${e.message}`));
    await page.goto('file://' + path.resolve(htmlPath), { waitUntil: 'load', timeout: 30000 });
    // start the game
    await new Promise(r => setTimeout(r, 1200));
    await page.evaluate(() => { const b = document.getElementById('startBtn'); if (b) b.click(); });
    await new Promise(r => setTimeout(r, 800));
    // drive it a moment so we see motion/tricks, then grab a few frames
    for (let i = 0; i < 3; i++) {
      await page.evaluate(() => { const e=(a)=>document.querySelector(`[data-act="${a}"]`); }); // noop hook
      await new Promise(r => setTimeout(r, 900));
      const f = path.join(outDir, `${v.name}-${i}.png`);
      await page.screenshot({ path: f });
      report.shots.push(f);
    }
    await page.close();
  }
  await browser.close();
  fs.writeFileSync(path.join(outDir, 'report.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report, null, 2));
})().catch(e => { console.error('HARNESS FAIL:', e.message); process.exit(1); });
