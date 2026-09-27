// First-timer grind: press Space/K on the prompt, then NO balance input. How does it end?
const puppeteer=require('puppeteer-core');
(async()=>{ const b=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--mute-audio']});
const pg=await b.newPage(); const errs=[]; pg.on('pageerror',e=>errs.push(e.message));
await pg.goto('http://localhost:8765/sunset-yard-3d.html?shot',{waitUntil:'domcontentloaded',timeout:0}); await pg.waitForFunction('window.__booted===true',{timeout:180000});
await pg.evaluate(()=>window.__startGame());
const r=await pg.evaluate(()=>{ const D=window.__dbg,H=D.held,E=D.edges; const res={grinds:0, endBail:0, endHop:0, endRailEnd:0, durs:[], kManual:0, kTries:0, fakiePush:null};
 D.rails.forEach((rl,ri)=>{ if(rl.y>0.7) return; for(const key of ['ollie','manual']) for(const side of [-1,1]){
   for(const k in H)H[k]=false; E.clear(); D.state().phase='playing'; D.state().time=120;
   const px=-rl.dir.z,pz=rl.dir.x, m={x:rl.a.x+rl.dir.x*rl.len*0.25,z:rl.a.z+rl.dir.z*rl.len*0.25}, a=0.35;
   const hx=rl.dir.x*Math.cos(a)-side*px*Math.sin(a), hz=rl.dir.z*Math.cos(a)-side*pz*Math.sin(a);
   const sx=m.x+side*px*1.3-hx*4, sz=m.z+side*pz*1.3-hz*4; if(D.surfH(sx,sz)>0.15) return;
   D.place(sx,sz,Math.atan2(hx,hz),6); D.sk().railCoolT=0; let pressed=false, t0=0, inG=false;
   if(key==='manual') res.kTries++;
   for(let i=0;i<120*6;i++){ const s=D.sk(); const lbl=document.getElementById('manBtn').textContent;
     if(!pressed && s.state==='roll' && lbl==='GRIND'){ E.add(key); pressed=true; }
     D.step(1); const st=D.sk().state;
     if(key==='manual' && pressed && st==='manual'){ res.kManual++; break; }
     if(!inG && st==='grind'){ inG=true; t0=i; res.grinds++; }
     if(inG && st!=='grind'){ res.durs.push(+((i-t0)/120).toFixed(2)); if(st==='bail') res.endBail++; else { const s2=D.sk(); if(s2.lastRail && Math.min(s2.railT, s2.lastRail.len-s2.railT)<0.3) res.endRailEnd++; else res.endHop++; } break; } } } });
 // fakie push: ride backwards, press push -> should turn round, not push backwards
 for(const k in H)H[k]=false; D.place(0,-5,0,3); const s=D.sk(); s.fakie=true; H.push=true; const ev=[]; for(let i=0;i<120;i++){ D.step(1); if(i%20===0) ev.push((D.sk().fakie?'F':'-')+(D.sk().stroke&&D.sk().stroke.ph)); } H.push=false; res.fakiePush=ev.join(' ');
 return res; });
console.log(JSON.stringify(r)); console.log('ERR',errs); await b.close(); })();
