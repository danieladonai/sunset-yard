// How grindable is it for a real player? Three input styles, every ground rail, many approaches.
const puppeteer=require('puppeteer-core');
(async()=>{ const b=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--mute-audio']});
const pg=await b.newPage(); await pg.goto('http://localhost:8765/sunset-yard-3d.html?shot',{waitUntil:'domcontentloaded',timeout:0}); await pg.waitForFunction('window.__booted===true',{timeout:180000});
await pg.evaluate(()=>window.__startGame());
for(const style of ['K on prompt','SPACE on prompt','naive ollie ~1m out']){
 const r=await pg.evaluate((style)=>{ const D=window.__dbg,H=D.held,E=D.edges; let tries=0, got=0, prompted=0;
  D.rails.forEach((rl,ri)=>{ if(rl.y>1) return; for(const ang of [0,0.3,0.6,0.9]) for(const side of [-1,1]) for(const off of [0.5,1.0,1.6,2.2]) for(const sp of [3,6,8.5]){
    for(const k in H)H[k]=false; E.clear(); D.state().phase='playing'; D.state().time=120;
    const px=-rl.dir.z, pz=rl.dir.x, mid={x:rl.a.x+rl.dir.x*rl.len*0.45, z:rl.a.z+rl.dir.z*rl.len*0.45};
    const hx=rl.dir.x*Math.cos(ang)-side*px*Math.sin(ang), hz=rl.dir.z*Math.cos(ang)-side*pz*Math.sin(ang);
    const sx=mid.x+side*px*off-hx*6, sz=mid.z+side*pz*off-hz*6; if(D.surfH(sx,sz)>0.15) continue;
    D.place(sx,sz,Math.atan2(hx,hz),sp); const S=D.sk(); S.railCoolT=0; S.fakie=false; tries++;
    let pressed=false, ok=false;
    for(let i=0;i<300;i++){ const s=D.sk();
      if(!pressed && s.state==='roll'){
        const lbl=document.getElementById('manBtn').textContent;
        if(style==='K on prompt' && lbl==='GRIND'){ E.add('manual'); pressed=true; prompted++; }
        else if(style==='SPACE on prompt' && lbl==='GRIND'){ E.add('ollie'); pressed=true; prompted++; }
        else if(style==='naive ollie ~1m out'){ // lateral distance to the bar line
          const lat=Math.abs((s.pos.x-rl.a.x)*px+(s.pos.z-rl.a.z)*pz); if(lat<1.0){ E.add('ollie'); pressed=true; prompted++; } }
      }
      D.step(1); if(D.sk().state==='grind'){ ok=true; break; } if(D.sk().state==='bail') break; }
    if(ok) got++;
  } }); return {tries,prompted,got}; },style);
 console.log(style.padEnd(22), `tries ${r.tries}  acted ${r.prompted}  grinded ${r.got}  = ${Math.round(100*r.got/Math.max(1,r.prompted))}% of attempts`);
}
await b.close(); })();
