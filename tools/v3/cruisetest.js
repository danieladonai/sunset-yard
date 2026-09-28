// hold PUSH for 15s on the long straight: expect kick sets, then cruising, not endless kicking
const puppeteer=require('puppeteer-core');
(async()=>{ const b=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--mute-audio']});
const pg=await b.newPage(); await pg.goto('http://localhost:8765/sunset-yard-3d.html?shot',{waitUntil:'domcontentloaded',timeout:0}); await pg.waitForFunction('window.__booted===true',{timeout:180000});
await pg.evaluate(()=>window.__startGame());
console.log(await pg.evaluate(()=>{ const D=window.__dbg,H=D.held; for(const k in H)H[k]=false; D.state().phase='playing'; D.state().free=true; D.place(0,-60,0,0); H.push=true;
 const ev=[]; let last=null, kicks=0, cruiseT=0;
 for(let i=0;i<120*15;i++){ D.step(1); const s=D.sk(); const mode=s.cruise?'CRUISE':(s.pushOn?'push':'idle'); if(s.stroke&&s.stroke.ph==='plant'&&s._lp!=='plant') kicks++; s._lp=s.stroke&&s.stroke.ph; if(s.cruise) cruiseT+=1/120;
   if(mode!==last){ ev.push((i/120).toFixed(1)+'s '+mode+' v='+s.speed.toFixed(1)); last=mode; } if(Math.abs(s.pos.z)>70) { D.sk().pos.z=-60; } }
 return ev.slice(0,24).join('\n')+'\nkicks '+kicks+' cruising '+cruiseT.toFixed(1)+'s of 15'; }));
await b.close(); })();
