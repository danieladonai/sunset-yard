// Sunset Yard v3 test harness — drives the real game headless through window.__dbg.
// Serve the repo first:  python3 -m http.server 8765   (from the repo root)
//   node harness.js phys                 physics scenarios: every ramp, spins, bails, bowl
//   node harness.js poses <outDir> [names] [camDist] [camFwd]   freeze + shoot the rider per state
//   node harness.js sheet <dir> [cols]   contact sheet of the PNGs in <dir>
//   node harness.js cards                re-render roster cards from the in-game models
//   node harness.js smoke                boot, 20s scripted run, report page errors + fps
const puppeteer = require('puppeteer-core');
const fs = require('fs'), path = require('path');
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const URL = process.env.SY_URL || 'http://localhost:8765/sunset-yard-3d.html';
const [cmd, ...args] = process.argv.slice(2);

async function boot(opts = {}) {
  const b = await puppeteer.launch({ executablePath: CHROME, headless: 'new',
    args: opts.gpu ? ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist', '--mute-audio']
                   : ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--mute-audio'] });
  const pg = await b.newPage(); await pg.setViewport(opts.vp || { width: 960, height: 600 });
  const errs = [];
  pg.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
  pg.on('response', r => { if (r.status() >= 400 && !/favicon/.test(r.url())) errs.push('HTTP ' + r.status() + ' ' + r.url()); });
  await pg.goto(URL + (opts.qs || '?shot'), { waitUntil: 'domcontentloaded', timeout: 0 });
  await pg.waitForFunction('window.__booted===true', { timeout: 180000 });
  if (opts.fresh) await pg.evaluate(() => localStorage.removeItem('sy3_save'));
  await pg.evaluate(() => window.__startGame());
  return { b, pg, errs };
}

const PHYS = [
  ['vert wall', 12, -15.2, -Math.PI / 2, 0, { runup: true, }],
  ['vert wall + ollie at lip', 12, -15.2, -Math.PI / 2, 0, { runup: true,  ollieHold: true }],
  ['vert wall + 180', 12, -15.2, -Math.PI / 2, 0, { runup: true,  spin: 0.49 }],
  ['vert wall + 90 (must bail)', 12, -15.2, -Math.PI / 2, 0, { runup: true,  spin: 0.25 }],
  ['spine', 10, 14, Math.PI / 2, 8.5, {}],
  ['spine transfer (loaded ollie)', 10, 14, Math.PI / 2, 8.5, { ollieTill: 1.62 }],
  ['spine side-on (bonk, no launch)', 22, 2, 0, 8.5, {}],
  ['3.2 quarter off dock', -16, 20, 0, 8.5, {}],
  ['bowl drop', 30, 14, 0, 8.5, {}],
  ['four stair (ollie off the pad)', -7.5, -9.2, Math.PI, 8.5, { ollieAt: 0.04, ollieHold: false }],
  ['rail 50-50 (press grind)', 'rail2', 0, 0, 7, { railOllie: true, grind: true }],
  ['rail, no press (must NOT grind)', 'rail2', 0, 0, 7, { railOllie: true }],
  ['kicker ride-up launch', -21, -34, Math.PI, 7, {}],
  ['idle: no input (must coast to a stop)', 0, -5, 0, 6, { idle: true }],
];

async function phys() {
  const { b, pg, errs } = await boot({ fresh: true });
  for (const [name, x, z, yaw, sp, o] of PHYS) {
    const r = await pg.evaluate((x, z, yaw, sp, o, process_trace) => {
      const D = window.__dbg, H = D.held, E = D.edges;
      for (const k in H) H[k] = false; E.clear(); D.state().phase = 'playing'; D.state().time = 120;
      if (x === 'rail2') { const r = D.rails[2]; D.place(r.a.x + r.dir.x * 6, r.a.z + r.dir.z * 6, Math.atan2(r.dir.x, r.dir.z), sp); E.add('ollie'); }
      else D.place(x, z, yaw, sp);
      const S = D.sk(); S.chargeT = 0; S.fakie = false; S.ollieWas = false; S.to = null; S.lastRail = null; S.railCoolT = 0;
      if (o.ollieHold && !o.runup) H.ollie = true;
      const ev = []; let last = S.state, peak = -9, spinT = 0;
      for (let i = 0; i < 120 * (o.runup ? 9 : 5); i++) {
        const t = i / 120, s = D.sk();
        if (o.ollieTill != null) H.ollie = s.state !== 'air' && t < o.ollieTill;
        if (o.spin && s.state === 'air' && s.airFrom === 'lip') { if (spinT < o.spin) { H.left = true; spinT += 1 / 120; } else H.left = false; }
        if (o.runup) { const onT = s.pos.x < -14.6; H.push = !onT; if (o.ollieHold) H.ollie = onT && s.state === 'roll'; }
        if (o.ollieAt != null && Math.abs(t - o.ollieAt) < 0.004) E.add('ollie');
        if (o.grind && s.state === 'air' && t > 0.15) H.manual = true;
        if (s.state === 'grind') { H.manual = false; H.left = s.balance > 0.2; H.right = s.balance < -0.2; } else if (!o.spin) { H.left = H.right = false; }
        D.step(1);
        if (s.state !== last) { ev.push(`${t.toFixed(2)}s ${last}->${s.state} y=${s.pos.y.toFixed(2)} spd=${s.speed.toFixed(1)} ${s.airFrom || ''}`); last = s.state; }
        if (s.state === 'air') peak = Math.max(peak, s.pos.y);
        if (!isFinite(s.pos.x + s.pos.y + s.pos.z + s.yaw)) { ev.push('NaN!'); break; }
        if (process_trace && i % 120 === 0) ev.push('  t'+t.toFixed(0)+' '+s.state+' '+s.pos.x.toFixed(1)+','+s.pos.y.toFixed(2)+','+s.pos.z.toFixed(1)+' v'+s.speed.toFixed(1)+' ph'+D.state().phase);
      }
      const lc = D.state().lastCombo; const S2 = D.sk(); ev.push('end: '+S2.state+' spd='+S2.speed.toFixed(2)+' pos='+S2.pos.x.toFixed(1)+','+S2.pos.z.toFixed(1)); return { ev: process_trace ? ev : ev.slice(0, 8).concat(ev.slice(-1)), peak: +peak.toFixed(2), last: lc && lc.tricks, gaps: Object.keys(D.state().stats.gaps) };
    }, x, z, yaw, sp, o, !!process.env.TRACE);
    console.log(`\n## ${name}  peak=${r.peak}  last=${JSON.stringify(r.last)}  gaps=${r.gaps}`);
    r.ev.forEach(e => console.log('   ' + e));
  }
  console.log('\nERRORS:', errs.length ? errs : 'none'); await b.close();
}

const POSES = [
  ['push', `D.place(0,-5,0.6,3); H.push=true; D.step(50);`],
  ['crouch', `D.place(0,-5,0.6,15); H.ollie=true; D.step(60);`],
  ['air-kickflip', `D.place(0,-5,0.6,15); E.add('ollie'); D.step(20); E.add('trick'); D.step(8);`],
  ['air-grab', `D.place(0,-5,0.6,15); E.add('ollie'); D.step(14); E.add('manual'); H.manual=true; D.step(22);`],
  ['grind-5050', `const r=D.rails[2]; D.place(r.a.x+r.dir.x*6, r.a.z+r.dir.z*6, Math.atan2(r.dir.x,r.dir.z),15); E.add('ollie'); D.step(80);`],
  ['manual', `D.place(0,-5,0.6,15); D.step(10); E.add('manual'); H.manual=true; D.step(50);`],
  ['ollie-a', `D.place(0,-5,0.6,7); H.ollie=true; D.step(30); H.ollie=false; D.step(8);`],
  ['ollie-b', `D.place(0,-5,0.6,7); H.ollie=true; D.step(30); H.ollie=false; D.step(16);`],
  ['ollie-c', `D.place(0,-5,0.6,7); H.ollie=true; D.step(30); H.ollie=false; D.step(30);`],
  ['ollie-d', `D.place(0,-5,0.6,7); H.ollie=true; D.step(30); H.ollie=false; D.step(48);`],
  ['bail-a', `D.place(0,-5,0.6,7); D.step(5); D.bail(); D.step(12);`],
  ['bail-b', `D.place(0,-5,0.6,7); D.step(5); D.bail(); D.step(45);`],
  ['bail-c', `D.place(0,-5,0.6,7); D.step(5); D.bail(); D.step(100);`],
  ['push-0', `D.place(0,-5,0.6,5); H.push=true; D.step(75);`],
  ['push-1', `D.place(0,-5,0.6,5); H.push=true; D.step(84);`],
  ['push-2', `D.place(0,-5,0.6,5); H.push=true; D.step(94);`],
  ['push-3', `D.place(0,-5,0.6,5); H.push=true; D.step(103);`],
  ['push-4', `D.place(0,-5,0.6,5); H.push=true; D.step(112);`],
  ['push-5', `D.place(0,-5,0.6,5); H.push=true; D.step(122);`],
  ['push-6', `D.place(0,-5,0.6,5); H.push=true; D.step(131);`],
  ['push-7', `D.place(0,-5,0.6,5); H.push=true; D.step(140);`],
  ['pushlow', `D.place(0,-5,0.6,3); H.push=true; D.step(50);`],
  ['vert-air', `D.place(-4,-15.2,-Math.PI/2,16); D.step(170);`],
];
async function poses(out, only, camd = 2.3, camf = 1.2) {
  fs.mkdirSync(out, { recursive: true });
  const { b, pg, errs } = await boot({ gpu: true, qs: '?q=high', vp: { width: 640, height: 640 } });
  await new Promise(r => setTimeout(r, 2500));
  for (const [n, code] of POSES.filter(p => !only || only.split(',').includes(p[0]))) {
    await pg.evaluate((code, camd, camf) => {
      const D = window.__dbg, H = D.held, E = D.edges; for (const k in H) H[k] = false; E.clear();
      D.state().phase = 'playing'; D.state().time = 120; eval(code); D.state().phase = 'paused';
      const s = D.sk(), yv = s.yaw, rx = -Math.cos(yv), rz = Math.sin(yv), fx = Math.sin(yv), fz = Math.cos(yv);
      window.__setFrame([s.pos.x + rx * camd + fx * camf, s.pos.y + 1.15, s.pos.z + rz * camd + fz * camf], [s.pos.x, s.pos.y + 0.8, s.pos.z]);
    }, code, +camd, +camf);
    await new Promise(r => setTimeout(r, 500));
    await pg.screenshot({ path: path.join(out, n + '.png') });
    await pg.evaluate(() => { window.__freezeCam = false; });
  }
  console.log('errors', errs); await b.close();
}

async function sheet(dir, cols = 3) {
  const files = fs.readdirSync(dir).filter(f => f.endsWith('.png') && !f.startsWith('sheet')).sort();
  const html = `<body style="margin:0;background:#111;display:grid;grid-template-columns:repeat(${cols},320px);gap:2px;font:12px sans-serif;color:#fff">` +
    files.map(f => `<div style="position:relative"><img src="file://${path.resolve(dir, f)}" style="width:320px;height:320px;object-fit:cover;display:block"><span style="position:absolute;left:4px;top:4px;background:#000a;padding:1px 4px">${f.slice(0, -4)}</span></div>`).join('') + '</body>';
  fs.writeFileSync(path.join(dir, '_s.html'), html);
  const b = await puppeteer.launch({ executablePath: CHROME, headless: 'new', args: ['--allow-file-access-from-files'] });
  const pg = await b.newPage(); await pg.setViewport({ width: cols * 322, height: Math.ceil(files.length / cols) * 322 });
  await pg.goto('file://' + path.resolve(dir, '_s.html')); await pg.screenshot({ path: path.join(dir, 'sheet.png') });
  await b.close(); console.log(path.join(dir, 'sheet.png'));
}

async function cards() {
  const { b, pg, errs } = await boot({ gpu: true, qs: '?q=high', vp: { width: 300, height: 400 } });
  for (const [i, id] of [[0, 'lowpoly-woman'], [1, 'lowpoly-man']]) {
    await pg.evaluate(i => window.__dbg.pick(i), i);
    await pg.waitForFunction('window.__dbg.charReady()', { timeout: 60000 }); await new Promise(r => setTimeout(r, 600));
    await pg.evaluate(() => { const D = window.__dbg; for (const k in D.held) D.held[k] = false; D.edges.clear();
      D.state().phase = 'playing'; D.place(0, -5, 0.6, 4); D.step(90); D.state().phase = 'paused';
      const s = D.sk(), yv = s.yaw, rx = -Math.cos(yv), rz = Math.sin(yv), fx = Math.sin(yv), fz = Math.cos(yv);
      window.__setFrame([s.pos.x + rx * 2.6 + fx * 1.1, s.pos.y + 1.15, s.pos.z + rz * 2.6 + fz * 1.1], [s.pos.x, s.pos.y + 0.75, s.pos.z]);
      for (const id of ['hud', 'touch', 'start', 'over']) { const e = document.getElementById(id); if (e) e.style.visibility = 'hidden'; } });
    await new Promise(r => setTimeout(r, 700));
    await pg.screenshot({ path: path.resolve(__dirname, '../../sunset-yard-assets/card-' + id + '.png') });
    await pg.evaluate(() => { window.__freezeCam = false; });
  }
  console.log('cards written', errs); await b.close();
}
async function smoke() {
  const { b, pg, errs } = await boot({ gpu: true, qs: '', fresh: true });
  const r = await pg.evaluate(async () => {
    const D = window.__dbg, H = D.held, E = D.edges; let frames = 0, t0 = performance.now();
    const raf = () => { frames++; if (performance.now() - t0 < 20000) requestAnimationFrame(raf); }; requestAnimationFrame(raf);
    // scripted "player": ollie every ~1.2s, flip in the air, steer in waves
    const iv = setInterval(() => { const s = D.sk(); const t = performance.now() - t0;
      H.left = Math.sin(t / 900) > 0.6; H.right = Math.sin(t / 900) < -0.6;
      if (s.state === 'roll' && Math.random() < 0.08) E.add('ollie');
      if (s.state === 'air' && Math.random() < 0.05) E.add('trick'); }, 100);
    await new Promise(r => setTimeout(r, 20000)); clearInterval(iv);
    return { fps: +(frames / ((performance.now() - t0) / 1000)).toFixed(1), score: D.state().score, stats: D.state().stats, rinfo: window.__rinfo() };
  });
  console.log(JSON.stringify(r)); console.log('ERRORS:', errs.length ? errs : 'none'); await b.close();
}

({ phys, cards, poses: () => poses(...args), sheet: () => sheet(...args), smoke })[cmd || 'phys']().catch(e => { console.error(e); process.exit(1); });
