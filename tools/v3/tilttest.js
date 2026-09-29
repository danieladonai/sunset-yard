// Tilt-to-ride: lean forward from the start angle -> rolls; sideways -> steers; back -> brakes.
const puppeteer=require('puppeteer-core');
(async()=>{ const b=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--mute-audio']});
const pg=await b.newPage(); const errs=[]; pg.on('pageerror',e=>errs.push(e.message));
await pg.goto('http://localhost:8765/sunset-yard-3d.html?shot',{waitUntil:'domcontentloaded',timeout:0}); await pg.waitForFunction('window.__booted===true',{timeout:180000});
await pg.evaluate(()=>{ const c=document.getElementById('tiltChk'); c.checked=true; window.__startGame(); });
await pg.waitForFunction('window.__dbg.charReady()',{timeout:60000});
const r=await pg.evaluate(async ()=>{ const D=window.__dbg,H=D.held,out={};
 const tilt=(beta,gamma)=>window.dispatchEvent(new DeviceOrientationEvent('deviceorientation',{alpha:0,beta,gamma}));
 const run=(beta,gamma,n)=>{ for(let i=0;i<n;i++){ tilt(beta,gamma); D.step(1); } };
 for(const k in H)H[k]=false; D.state().phase='playing'; D.place(0,-5,0.6,0); D.sk().stroke=null;
 run(45,0,60); await new Promise(r=>setTimeout(r,450)); run(45,0,5);  out.neutral={speed:+D.sk().speed.toFixed(2), push:H.push};                 // calibrate at 45deg: stays still
 run(35,0,240); out.lightLean={speed:+D.sk().speed.toFixed(2), push:H.push};
 run(22,0,360); out.fullLean={speed:+D.sk().speed.toFixed(2)};
 const y0=D.sk().yaw; run(22,-20,120); out.tiltLeftYaw=+(D.sk().yaw-y0).toFixed(2);   // left edge down
 const y1=D.sk().yaw; run(22,20,120); out.tiltRightYaw=+(D.sk().yaw-y1).toFixed(2);
 const s0=D.sk().speed; run(62,0,120); out.brake={from:+s0.toFixed(2), to:+D.sk().speed.toFixed(2), brake:H.brake};
 run(45,0,5); out.backToNeutral={push:H.push, brake:H.brake};
 out.note=document.getElementById('tiltNote').textContent; return out; });
console.log(JSON.stringify(r,null,1)); console.log('ERR',errs); await b.close(); })();
