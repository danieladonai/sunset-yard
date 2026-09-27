// After a wall bail near stairs / ledge ends: do you get up clear, and can you push away?
const puppeteer=require('puppeteer-core');
(async()=>{ const b=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--mute-audio']});
const pg=await b.newPage(); const errs=[]; pg.on('pageerror',e=>errs.push(e.message));
await pg.goto('http://localhost:8765/sunset-yard-3d.html?shot',{waitUntil:'domcontentloaded',timeout:0}); await pg.waitForFunction('window.__booted===true',{timeout:180000});
await pg.evaluate(()=>window.__startGame());
const r=await pg.evaluate(()=>{ const D=window.__dbg,H=D.held,out=[];
 const spots=[[-10,-11.4],[-10.9,-25.3],[-7.5,-13.2],[-5,-13],[6.2,-19.5],[-8,-26],[-14,6],[22,9],[-21,-38]];
 for(const [x,z] of spots) for(const yaw of [0,1.57,3.14,-1.57]){ for(const k in H)H[k]=false; D.state().phase='playing';
   D.place(x-Math.sin(yaw)*3, z-Math.cos(yaw)*3, yaw, 7); let bailed=false; for(let i=0;i<120*3;i++){ D.step(1); if(D.sk().state==='bail'){ bailed=true; break; } }
   if(!bailed) continue; for(let i=0;i<150 && D.sk().state==='bail';i++) D.step(1);
   const p0=D.sk().pos.clone(); H.push=true; for(let i=0;i<180;i++) D.step(1); H.push=false; const s=D.sk();
   out.push({spot:[x,z],yaw, moved:+Math.hypot(s.pos.x-p0.x,s.pos.z-p0.z).toFixed(2), speed:+s.speed.toFixed(1), state:s.state}); }
 return out; });
const stuck=r.filter(o=>o.moved<1.0); console.log('wall bails tested',r.length,' stuck after get-up (moved<1m in 1.5s of pushing):',stuck.length); if(stuck.length) console.log(JSON.stringify(stuck));
console.log('ERR',errs); await b.close(); })();
