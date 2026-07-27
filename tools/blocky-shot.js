// Verification harness for the blocky-skater rebuild.
// Loads the LIVE url, selects a character, drops in, screenshots the skater,
// then triggers ollie+trick and screenshots mid-air. Reports console errors.
// Usage: NODE_PATH=$(npm root -g) node blocky-shot.js
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const URL = 'https://cy.someantics.xyz/sunset-yard-3d.html';
const outDir = '/root/Code/sunset-yard/tools/shots';
fs.mkdirSync(outDir, { recursive: true });

const CHARS = [
  { ix: 0, name: 'nova' },
  { ix: 1, name: 'rio' },
];

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--enable-webgl', '--ignore-gpu-blocklist',
           '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
  });
  const report = { errors: [], shots: [] };

  for (const c of CHARS) {
    const page = await browser.newPage();
    await page.setViewport({ width: 390, height: 844, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
    page.on('console', m => { if (m.type() === 'error') report.errors.push(`[${c.name}] ${m.text()}`); });
    page.on('pageerror', e => report.errors.push(`[${c.name}] PAGEERROR ${e.message}`));
    await page.goto(URL, { waitUntil: 'load', timeout: 60000 });

    // wait for #start to lose .hide
    await page.waitForFunction(() => {
      const el = document.getElementById('start');
      return el && !el.classList.contains('hide');
    }, { timeout: 60000 });

    // select character
    await page.evaluate((ix) => {
      const cards = document.querySelectorAll('.char-card');
      if (cards[ix]) cards[ix].click();
    }, c.ix);
    await new Promise(r => setTimeout(r, 300));

    // Drop In
    await page.evaluate(() => { const b = document.getElementById('startBtn'); if (b) b.click(); });
    await new Promise(r => setTimeout(r, 2600));

    const restFile = path.join(outDir, `blocky-${c.name}.png`);
    await page.screenshot({ path: restFile });
    report.shots.push(restFile);

    // animation check: ollie (Space) then trick (KeyJ)
    await page.keyboard.press('Space');
    await new Promise(r => setTimeout(r, 120));
    await page.keyboard.down('KeyJ');
    await new Promise(r => setTimeout(r, 260));
    await page.keyboard.up('KeyJ');
    const airFile = path.join(outDir, `blocky-${c.name}-air.png`);
    await page.screenshot({ path: airFile });
    report.shots.push(airFile);

    await page.close();
  }

  await browser.close();
  fs.writeFileSync(path.join(outDir, 'blocky-report.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report, null, 2));
})().catch(e => { console.error('HARNESS FAIL:', e.message); process.exit(1); });
