const puppeteer=require('puppeteer-core');
(async()=>{ const b=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--mute-audio']});
const pg=await b.newPage(); await pg.goto('http://localhost:8765/sunset-yard-3d.html?shot',{waitUntil:'domcontentloaded',timeout:0}); await pg.waitForFunction('window.__booted===true',{timeout:180000});
await pg.evaluate(()=>{ window.__dbg.pick(1); window.__startGame(); }); await pg.waitForFunction('window.__dbg.charReady()',{timeout:60000});
const r=await pg.evaluate(()=>{ window.__recHold=true; const D=window.__dbg; for(const k in D.held)D.held[k]=false; D.edges.clear(); D.state().phase='playing'; D.state().free=true;
  const rl=D.rails.filter(q=>q.y<=1)[0]; const px=-rl.dir.z, pz=rl.dir.x; D.place(rl.a.x+px*1.0-rl.dir.x*5, rl.a.z+pz*1.0-rl.dir.z*5, Math.atan2(rl.dir.x,rl.dir.z), 6.5); D.sk().railCoolT=0;
  window.__advance(30); const out=[]; let pr=0;
  for(let f=0; f<120; f++){ if(!pr && document.getElementById('manBtn').textContent==='GRIND'){ D.edges.add('manual'); pr=1; }
    window.__advance(2); if(f>=55 && f<=95 && f%3==0){ const s=D.sk(), c=D.cam(); out.push([f, s.state, s.pos.y.toFixed(2), D.surfH(s.pos.x,s.pos.z).toFixed(2), 'cam', c.y.toFixed(2), 'd', Math.hypot(c.x-s.pos.x,c.z-s.pos.z).toFixed(2), 'occ', c.occ.toFixed(2), c.occY.toFixed(2)].join(' ')); } }
  return out; });
console.log(r.join('\n')); await b.close(); })();
