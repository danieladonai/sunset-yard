// Record a scripted run through the REAL game to a PNG sequence (30fps) with the game's own camera.
//   node record.js <outDir> [script] [char 0|1] [w h]
// Scripts drive held/edges per video frame. Compose to mp4 with tools/blender/compose.py (or seq2mp4.py).
const puppeteer=require('puppeteer-core'); const fs=require('fs');
const [out, script='tour', ch='0', W='960', H='540', CAMMODE='chase']=process.argv.slice(2); fs.mkdirSync(out,{recursive:true});
const SCRIPTS={
  // spawn lane: push up to speed, carve, ollie, kickflip, grab off the kicker-free flat, manual, bail
  tour: [
    {place:[-2,-44,0,0]},
    {t:0.2,  hold:['push']}, {t:2.6, rel:['push']},
    {t:2.8,  hold:['left']}, {t:3.5, rel:['left']}, {t:3.6, hold:['right']}, {t:4.3, rel:['right']},
    {t:4.6,  hold:['ollie']}, {t:4.85, rel:['ollie']},
    {t:5.8,  hold:['push']}, {t:6.8, rel:['push']},
    {t:7.0,  hold:['ollie']}, {t:7.25, rel:['ollie']}, {t:7.36, tap:['trick']},
    {t:8.6,  hold:['ollie']}, {t:8.85, rel:['ollie']}, {t:9.0, hold:['manual']}, {t:9.6, rel:['manual']},
    {t:10.4, tap:['manual']},
    {t:12.0, end:true}],
  carve: [ {place:[-2,-44,0,0]}, {t:0.1, hold:['push']}, {t:2.4, rel:['push']}, {t:2.5, hold:['left']}, {t:3.6, rel:['left']}, {t:3.8, hold:['right']}, {t:4.9, rel:['right']}, {t:5.4, end:true} ],
  grab: [ {place:[-21,-31,Math.PI,8.8]}, {t:1.0, hold:['manual']}, {t:1.9, rel:['manual']}, {t:3.2, js:"window.__dbg.bail('test')"}, {t:5.0, end:true} ],
  brake: [ {place:[-2,-44,0,0]}, {t:0.1, hold:['push']}, {t:2.2, rel:['push']}, {t:2.5, hold:['brake']}, {t:4.2, rel:['brake']}, {t:4.5, end:true} ],
  quarter: [ {place:[-16,20,0,8.8]}, {t:0.05, hold:['push']}, {t:0.6, rel:['push']}, {t:4.5, end:true} ],
  vert: [ {place:[5,-15.2,-Math.PI/2,10]}, {t:0.1, hold:["push"]}, {t:1.2, rel:["push"]}, {t:5.0, end:true} ],
  quarter2: [ {place:[-16,14,0,9.5]}, {t:4.5, end:true} ],
  grind: [ {rail:0, off:1.0, speed:6.5}, {t:0.05, hold:['push']}, {t:0.5, rel:['push']}, {prompt:'manual'}, {t:4.5, end:true} ],
};
(async()=>{ const b=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--use-angle=metal','--enable-gpu','--ignore-gpu-blocklist','--mute-audio']});
const pg=await b.newPage(); await pg.setViewport({width:+W,height:+H}); const errs=[]; pg.on('pageerror',e=>errs.push(e.message));
await pg.goto('http://localhost:8765/sunset-yard-3d.html?shot&q=high',{waitUntil:'domcontentloaded',timeout:0}); await pg.waitForFunction('window.__booted===true',{timeout:180000});
await pg.evaluate((c)=>{ window.__dbg.pick(+c); window.__startGame(); },ch); await pg.waitForFunction('window.__dbg.charReady()',{timeout:60000});
await new Promise(r=>setTimeout(r,1500));
const S=SCRIPTS[script];
await pg.evaluate((m)=>{ window.__camMode=m; },CAMMODE);
await pg.evaluate((S)=>{ window.__recHold=true; const D=window.__dbg; for(const k in D.held)D.held[k]=false; D.edges.clear(); D.state().phase='playing'; D.state().time=120; D.state().free=true;
  const p=S.find(e=>e.place); if(p) D.place(...p.place);
  const r=S.find(e=>e.rail!==undefined); if(r){ const rl=D.rails.filter(q=>q.y<=1)[r.rail]; const px=-rl.dir.z, pz=rl.dir.x;
    const sx=rl.a.x+px*r.off-rl.dir.x*5, sz=rl.a.z+pz*r.off-rl.dir.z*5; D.place(sx,sz,Math.atan2(rl.dir.x,rl.dir.z),r.speed); D.sk().railCoolT=0; }
  window.__advance(30); },S);
const END=S.find(e=>e.end).t; let n=0;
for(let fr=0; fr/30<END; fr++){
  const t=fr/30;
  await pg.evaluate((S,t)=>{ const D=window.__dbg,H=D.held,E=D.edges;
    for(const e of S){ if(e.t===undefined||e.t>t||e.t<=t-1/30) continue;
      (e.hold||[]).forEach(k=>{ if(!H[k]) E.add(k); H[k]=true; }); (e.rel||[]).forEach(k=>H[k]=false); (e.tap||[]).forEach(k=>E.add(k)); if(e.js) eval(e.js); }
    const pr=S.find(e=>e.prompt); if(pr && !window.__pr && document.getElementById('manBtn').textContent==='GRIND'){ E.add(pr.prompt); window.__pr=1; }
    if(window.__camMode==='side'){ const s=D.sk(), yv=s.yaw, rx=-Math.cos(yv), rz=Math.sin(yv), v=s.speed/30; const fx=Math.sin(yv)*v, fz=Math.cos(yv)*v;
      window.__setFrame([s.pos.x+fx+rx*3.4, s.pos.y+1.0, s.pos.z+fz+rz*3.4],[s.pos.x+fx, s.pos.y+0.75, s.pos.z+fz]); }
    window.__advance(2); },S,t);
  await pg.screenshot({path:`${out}/f${String(n++).padStart(4,'0')}.png`});
}
console.log('frames',n,'errors',errs); await b.close(); })();
