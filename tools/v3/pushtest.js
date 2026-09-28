// Planted-foot drift: while the stroke is in PLANT, the pushing foot must stay put on the ground.
const puppeteer=require('puppeteer-core');
(async()=>{ const b=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--mute-audio']});
const pg=await b.newPage(); const errs=[]; pg.on('pageerror',e=>errs.push(e.message));
await pg.goto('http://localhost:8765/sunset-yard-3d.html?shot',{waitUntil:'domcontentloaded',timeout:0}); await pg.waitForFunction('window.__booted===true',{timeout:180000});
await pg.evaluate(()=>window.__startGame()); await pg.waitForFunction('window.__dbg.charReady()',{timeout:60000});
const r=await pg.evaluate(()=>{ const D=window.__dbg,H=D.held,out={}; const R4=D.r4(); const B=R4?{RightFoot:R4.root.getObjectByName('ball_r')}:D.cm().ik.B; const V=B.RightFoot.position.constructor; const ROOT=R4?R4.root:D.cm().root;
 for(const v0 of [0.5,3,6,8.5]){ for(const k in H)H[k]=false; D.state().phase='playing'; D.place(0,-5,0.6,v0); D.sk().stroke=null; H.push=true;
  let plantStart=null, drifts=[], jumps=0, last=null;
  for(let i=0;i<240;i++){ D.step(1); D.skater().updateMatrixWorld(true); const p=B.RightFoot.getWorldPosition(new V()); const S=D.sk().stroke;
    if(last){ const j=p.distanceTo(last); if(j>0.12) jumps++; } last=p.clone();
    if(S && S.ph==='plant'){ if(!plantStart) plantStart=p.clone(); else drifts.push(Math.hypot(p.x-plantStart.x,p.z-plantStart.z)); } else plantStart=null; }
  H.push=false; out['v'+v0]={maxDriftCm:+(100*Math.max(0,...drifts)).toFixed(1), frameJumps:jumps, endSpeed:+D.sk().speed.toFixed(2)}; }
 // interrupt: push then pop mid-stroke
 for(const k in H)H[k]=false; D.place(0,-5,0.6,5); D.sk().stroke=null; H.push=true; let last=null, maxJ=0;
 for(let i=0;i<150;i++){ if(i===40){ D.edges.add('ollie'); } if(i===70) H.push=false; D.step(1); D.skater().updateMatrixWorld(true); const p=B.RightFoot.getWorldPosition(new V()); if(last){ const s=D.sk(); const rel=p.clone().sub(last); /* subtract body motion */ maxJ=Math.max(maxJ, Math.hypot(rel.x-s.vel.x/120, rel.y-(s.vy||0)/120, rel.z-s.vel.z/120)); } last=p.clone(); }
 out.interruptMaxFootJumpCm=+(maxJ*100).toFixed(1); return out; });
console.log(JSON.stringify(r,null,1)); console.log('ERR',errs); await b.close(); })();
