// ride at the pipe from every side: must never end up inside a wall, mounds must be ridden over
const puppeteer=require('puppeteer-core');
(async()=>{ const b=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--mute-audio']});
const pg=await b.newPage(); const errs=[]; pg.on('pageerror',e=>errs.push(e.message)); await pg.goto('http://localhost:8765/sunset-yard-3d.html?shot',{waitUntil:'domcontentloaded',timeout:0}); await pg.waitForFunction('window.__booted===true',{timeout:180000});
await pg.evaluate(()=>window.__startGame());
const r=await pg.evaluate(()=>{ const D=window.__dbg,H=D.held; const cx=9.5,cz=-31, rot=0.34; const ax=Math.cos(rot), az=-Math.sin(rot);
  let inside=0, through=0, bumps=0, bails=0, maxH=0, n=0;
  for(let a=0;a<360;a+=15) for(const sp of [3,6,9]){ for(const k in H)H[k]=false; D.state().phase='playing'; D.state().time=120;
    const t=a*Math.PI/180, sx=cx+Math.sin(t)*11, sz=cz+Math.cos(t)*11; D.place(sx,sz,Math.atan2(cx-sx,cz-sz),sp); n++;
    for(let i=0;i<500;i++){ D.step(1); const s=D.sk(); const dx=s.pos.x-cx, dz=s.pos.z-cz; const along=dx*ax+dz*az, lat=Math.abs(-dx*az+dz*ax);
      if(Math.abs(along)<3.1 && lat>2.12 && lat<2.55 && s.state!=='air') { inside++; break; }
      maxH=Math.max(maxH,s.pos.y); if(s.state==='bail'){ bails++; break; } }
  } return {n, inside, bails, maxH:+maxH.toFixed(2)}; });
console.log(JSON.stringify(r), errs); await b.close(); })();
