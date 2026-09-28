const puppeteer=require('puppeteer-core');
(async()=>{ const b=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--mute-audio']});
const pg=await b.newPage(); await pg.goto('http://localhost:8765/sunset-yard-3d.html?shot',{waitUntil:'domcontentloaded',timeout:0}); await pg.waitForFunction('window.__booted===true',{timeout:180000});
await pg.evaluate(()=>window.__startGame());
console.log(await pg.evaluate(()=>{ const D=window.__dbg,H=D.held,out=[];
 for(const deg of [10,20,35,55,80]) for(const sp of [4,8]){ for(const k in H)H[k]=false; D.state().phase='playing';
  const a=deg*Math.PI/180, yaw=Math.atan2(Math.sin(a),Math.cos(a)); // toward +x, fence at x=12.48, z -27..
  D.place(12.48-Math.sin(a)*2.0, -13-Math.cos(a)*2.0, yaw, sp); let res='pass';
  for(let i=0;i<180;i++){ D.step(1); const s=D.sk(); if(s.state==='bail'){ res='BAIL'; break; } }
  const s=D.sk(); out.push(deg+'deg '+sp+'m/s -> '+res+' x='+s.pos.x.toFixed(2)+' v='+s.speed.toFixed(1)); } return out.join('\n'); }));
await b.close(); })();
