// Unwanted grinds: ollies that are NOT aimed at the bar must not get pulled onto it.
const puppeteer=require('puppeteer-core');
(async()=>{ const b=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--mute-audio']});
const pg=await b.newPage(); await pg.goto('http://localhost:8765/sunset-yard-3d.html?shot',{waitUntil:'domcontentloaded',timeout:0}); await pg.waitForFunction('window.__booted===true',{timeout:180000});
await pg.evaluate(()=>window.__startGame());
const r=await pg.evaluate(()=>{ const D=window.__dbg,H=D.held,E=D.edges; const res={parallel2m:[0,0],hopOver:[0,0],snapMax:0};
 D.rails.forEach((rl)=>{ if(rl.y>1) return; const px=-rl.dir.z,pz=rl.dir.x;
  for(const side of [-1,1]) for(const sp of [4,7]){
   // A) riding parallel 2.0m beside the bar, plain ollie
   for(const k in H)H[k]=false; E.clear(); D.state().phase='playing'; const m={x:rl.a.x+rl.dir.x*rl.len*0.3,z:rl.a.z+rl.dir.z*rl.len*0.3};
   let sx=m.x+side*px*2.0, sz=m.z+side*pz*2.0; if(D.surfH(sx,sz)<0.15){ D.place(sx,sz,Math.atan2(rl.dir.x,rl.dir.z),sp); D.sk().railCoolT=0; E.add('ollie'); let g=false; for(let i=0;i<120;i++){ D.step(1); if(D.sk().state==='grind'){g=true;break;} } res.parallel2m[0]++; if(g)res.parallel2m[1]++; }
   // B) hopping OVER the bar square-on
   for(const k in H)H[k]=false; E.clear(); const m2={x:rl.a.x+rl.dir.x*rl.len*0.5,z:rl.a.z+rl.dir.z*rl.len*0.5};
   sx=m2.x+side*px*1.6; sz=m2.z+side*pz*1.6; if(D.surfH(sx,sz)<0.15){ D.place(sx,sz,Math.atan2(-side*px,-side*pz),sp); D.sk().railCoolT=0; H.ollie=true; D.step(24); H.ollie=false; let g=false; for(let i=0;i<120;i++){ D.step(1); if(D.sk().state==='grind'){g=true;break;} } res.hopOver[0]++; if(g)res.hopOver[1]++; }
  } });
 // C) snap distance at grind entry (visual position jump)
 D.rails.forEach((rl)=>{ if(rl.y>1) return; const px=-rl.dir.z,pz=rl.dir.x; for(const off of [0.6,1.2]){ for(const k in H)H[k]=false; E.clear();
   const m={x:rl.a.x+rl.dir.x*rl.len*0.4,z:rl.a.z+rl.dir.z*rl.len*0.4}, a=0.4, hx=rl.dir.x*Math.cos(a)-px*Math.sin(a), hz=rl.dir.z*Math.cos(a)-pz*Math.sin(a);
   const sx=m.x+px*off-hx*4, sz=m.z+pz*off-hz*4; if(D.surfH(sx,sz)>0.15) continue; D.place(sx,sz,Math.atan2(hx,hz),6); D.sk().railCoolT=0;
   let pressed=false, prev=null; const sk=D.skater();
   for(let i=0;i<240;i++){ if(!pressed && document.getElementById('manBtn').textContent==='GRIND'){ E.add('ollie'); pressed=true; }
     const wasAir=D.sk().state; D.step(1); const p=sk.position.clone(); if(prev && wasAir==='air' && D.sk().state==='grind'){ res.snapMax=Math.max(res.snapMax, Math.hypot(p.x-prev.x,p.z-prev.z)); } prev=p; if(D.sk().state==='grind') break; } } });
 return res; });
console.log('unwanted grind riding parallel 2m away:', r.parallel2m[1]+'/'+r.parallel2m[0]);
console.log('unwanted grind hopping over square-on :', r.hopOver[1]+'/'+r.hopOver[0]);
console.log('max visual jump on grind entry (m)    :', r.snapMax.toFixed(3));
await b.close(); })();
