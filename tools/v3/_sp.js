const puppeteer=require('puppeteer-core');
(async()=>{ const b=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--mute-audio']});
const pg=await b.newPage(); await pg.goto('http://localhost:8765/sunset-yard-3d.html?shot',{waitUntil:'domcontentloaded',timeout:0}); await pg.waitForFunction('window.__booted===true',{timeout:180000});
await pg.evaluate(()=>window.__startGame());
console.log(await pg.evaluate(()=>{ const D=window.__dbg,H=D.held,out=[]; for(const k in H)H[k]=false; D.state().phase='playing'; D.place(30,6,0,9); H.left=true;
 let last=null; for(let i=0;i<600;i++){ D.step(1); const s=D.sk(); if(i%4==0){ const row=[i,s.state,s.airFrom,s.yaw.toFixed(2),s.yawVis.toFixed(2),(s.spinNet||0).toFixed(2),s.fakie?'F':'',s.pos.y.toFixed(2)].join(' '); if(s.state==='air'||last==='air') out.push(row); last=s.state; } if(s.state==='bail'){ out.push('BAIL '+i); break; } } return out.slice(0,60).join('\n'); }));
await b.close(); })();
