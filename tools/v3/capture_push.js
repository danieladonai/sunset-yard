// Capture the CURRENT game's push as a 30fps image sequence from a fixed side camera.
const puppeteer=require('puppeteer-core'); const fs=require('fs'); const out=process.argv[2]; fs.mkdirSync(out,{recursive:true});
(async()=>{ const b=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--use-angle=metal','--enable-gpu','--ignore-gpu-blocklist','--mute-audio']});
const pg=await b.newPage(); await pg.setViewport({width:640,height:640});
await pg.goto('http://localhost:8765/sunset-yard-3d.html?shot&q=high',{waitUntil:'domcontentloaded',timeout:0}); await pg.waitForFunction('window.__booted===true',{timeout:180000});
await pg.evaluate(()=>window.__startGame()); await pg.waitForFunction('window.__dbg.charReady()',{timeout:60000}); await new Promise(r=>setTimeout(r,2500));
await pg.evaluate(()=>{ const D=window.__dbg,H=D.held; for(const k in H)H[k]=false; D.state().phase='playing'; D.state().time=120; D.place(0,-5,0.6,1.5); D.sk().stroke=null; H.push=true;
  for(let i=0;i<240;i++) D.step(1); });   // settle into the stroke cycle
for(let f=0; f<96; f++){
  await pg.evaluate(()=>{ const D=window.__dbg; D.state().phase='playing'; for(let i=0;i<4;i++) D.step(1); D.state().phase='paused';
    const s=D.sk(), yv=s.yaw, rx=-Math.cos(yv), rz=Math.sin(yv);
    window.__setFrame([s.pos.x+rx*3.6, s.pos.y+0.85, s.pos.z+rz*3.6],[s.pos.x, s.pos.y+0.62, s.pos.z]); });
  await new Promise(r=>setTimeout(r,60));
  await pg.screenshot({path:`${out}/f${String(f).padStart(3,'0')}.png`});
}
console.log('done'); await b.close(); })();
