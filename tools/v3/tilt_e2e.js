// END-TO-END tilt QA on an emulated iPhone: real touch taps on the real checkbox + Drop In, an
// iOS-faithful permission stub (rejects unless called inside a user gesture, remembers a denial),
// and the motion sensor driven through Chrome's DeviceOrientation override (the same event path
// a phone uses). Each scenario checks the box state, the on-screen note, and that the rider moves.
const puppeteer=require('puppeteer-core');
const URL=process.env.SY_URL||'http://localhost:8765/sunset-yard-3d.html';
const IOS_STUB=(mode)=>`(()=>{ const mode=${JSON.stringify(mode)}; let state=null;
  const rp=function(){ window.__permCalls=(window.__permCalls||0)+1;
    if(!(navigator.userActivation && navigator.userActivation.isActive)) return Promise.reject(new DOMException('Requires a user gesture','NotAllowedError'));
    if(state===null) state = mode==='deny' ? 'denied' : 'granted';
    return Promise.resolve(state); };
  window.DeviceOrientationEvent && (window.DeviceOrientationEvent.requestPermission=rp);
  window.DeviceMotionEvent && (window.DeviceMotionEvent.requestPermission=rp); })()`;
async function run(name, {mode='grant', untickFirst=false, tickAfterUntick=false, sensor=true, checkLoadRace=false, hudRecenter=false, retickAfterDeny=false, expect={}}={}){
  const b=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--use-angle=metal','--enable-gpu','--ignore-gpu-blocklist','--mute-audio']});
  const pg=await b.newPage(); const errs=[]; pg.on('pageerror',e=>errs.push(e.message));
  await pg.emulate({viewport:{width:390,height:844,deviceScaleFactor:2,isMobile:true,hasTouch:true},
    userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 26_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1'});
  await pg.evaluateOnNewDocument(IOS_STUB(mode));
  const cdp=await pg.target().createCDPSession();
  let jit=0; const setTilt=async(beta,gamma)=>{ if(sensor) await cdp.send('DeviceOrientation.setDeviceOrientationOverride',{alpha:0,beta:beta+(process.env.JITTER?((jit++%2)?0.05:-0.05):0),gamma}); };
  await setTilt(45,0);
  await pg.goto(URL+'?shot',{waitUntil:'domcontentloaded',timeout:0});
  if(checkLoadRace){ /* tap the box OFF as early as possible, before load finishes */
    await pg.waitForSelector('#tiltChk',{visible:true}); let bx=null; for(let k=0;k<100&&!bx;k++){ bx=await (await pg.$('#tiltChk')).boundingBox(); if(!bx) await new Promise(r=>setTimeout(r,50)); } await pg.touchscreen.tap(bx.x+bx.width/2,bx.y+bx.height/2); }
  await pg.waitForFunction('window.__booted===true',{timeout:180000});
  const R={name};
  const chk=async()=>pg.evaluate(()=>({checked:document.getElementById('tiltChk').checked, note:document.getElementById('tiltNote').textContent}));
  const tapSel=async(sel)=>{ const el=await pg.$(sel); await el.evaluate(e=>e.scrollIntoView({block:'center'})); const bx=await el.boundingBox(); await pg.touchscreen.tap(bx.x+bx.width/2,bx.y+bx.height/2); await new Promise(r=>setTimeout(r,300)); };
  R.atLoad=await chk();
  if(untickFirst){ await tapSel('#tiltChk'); R.afterUntick=await chk(); }
  if(tickAfterUntick){ await tapSel('#tiltChk'); R.afterRetick=await chk(); }
  if(retickAfterDeny){ await tapSel("#tiltChk"); await new Promise(r=>setTimeout(r,300)); R.afterDeny=await chk(); await tapSel("#tiltChk"); await new Promise(r=>setTimeout(r,300)); R.afterRetry=await chk(); }
  R.help=await pg.evaluate(()=>{ const h=document.getElementById("tiltHelp"); return h && getComputedStyle(h).display!=="none" ? h.textContent.slice(0,60) : ""; });
  R.rowStable=await pg.evaluate(()=>{ const a=document.getElementById("freeChk").getBoundingClientRect(); return Math.round(a.top); });
  await tapSel('#startBtn'); await new Promise(r=>setTimeout(r,800));
  R.afterDropIn=await chk();
  /* hold the phone at 45deg for a moment (calibration), then lean forward, then tilt right */
  await pg.evaluate(()=>{ window.__dbg.state().free=true; });
  for(let i=0;i<10;i++){ await setTilt(45,0); await new Promise(r=>setTimeout(r,50)); }
  const p0=await pg.evaluate(()=>{ const s=window.__dbg.sk(); return {x:s.pos.x,z:s.pos.z,yaw:s.yaw}; });
  for(let i=0;i<40;i++){ await setTilt(20,0); await new Promise(r=>setTimeout(r,50)); }
  const p1=await pg.evaluate(()=>{ const s=window.__dbg.sk(); return {x:s.pos.x,z:s.pos.z,yaw:s.yaw,speed:s.speed}; });
  for(let i=0;i<30;i++){ await setTilt(20,18); await new Promise(r=>setTimeout(r,50)); }
  const p2=await pg.evaluate(()=>{ const s=window.__dbg.sk(); return {yaw:s.yaw}; });
  R.tilt=await pg.evaluate(()=>window.__tilt&&window.__tilt()); R.held=await pg.evaluate(()=>({push:window.__dbg.held.push, phase:window.__dbg.state().phase, cruise:window.__dbg.sk().cruise, st:window.__dbg.sk().state, orient:(screen.orientation&&screen.orientation.angle)}));
  R.moved=+Math.hypot(p1.x-p0.x,p1.z-p0.z).toFixed(2); R.speed=+p1.speed.toFixed(2); R.steered=+(p2.yaw-p1.yaw).toFixed(2);
  R.permCalls=await pg.evaluate(()=>window.__permCalls||0);
  R.hud=await pg.evaluate(()=>{ const h=document.getElementById("tiltHud"); return {shown:getComputedStyle(h).display!=="none", label:h.querySelector(".lbl").textContent}; });
  if(hudRecenter){ const d0=await pg.evaluate(()=>window.__tilt().drive); const h=await pg.$("#tiltHud"); const bx=await h.boundingBox(); await pg.touchscreen.tap(bx.x+bx.width/2,bx.y+bx.height/2); await new Promise(r=>setTimeout(r,200)); R.recenter={before:+d0.toFixed(2), after:+(await pg.evaluate(()=>window.__tilt().drive)).toFixed(2)}; }
  const F=[]; if(expect.moves && !(R.moved>2)) F.push("rider did not roll when leaning"); if(expect.moves && !(Math.abs(R.steered)>0.4)) F.push("did not steer when tilting");
  if(expect.still && (R.moved>0.3)) F.push("moved with tilt OFF"); R.final=await chk(); if(expect.note && !R.final.note.includes(expect.note)) F.push("note should say "+expect.note+", says "+R.final.note);
  if(expect.hud!==undefined && R.hud.shown!==expect.hud) F.push("tilt HUD shown="+R.hud.shown); if(expect.hudLabel && R.hud.label!==expect.hudLabel) F.push("HUD label "+R.hud.label);
  if(expect.helpShown && !R.help) F.push("no help text after a denial"); if(retickAfterDeny && (R.afterRetry.checked)) F.push("box stuck ON after denied retry");
  if(hudRecenter && !(R.recenter.before>0.5 && Math.abs(R.recenter.after)<0.1)) F.push("HUD tap did not recentre");
  R.result = F.length ? "FAIL: "+F.join("; ") : "PASS";
  R.fps=await pg.evaluate(()=>new Promise(r=>{ let n=0; const t=performance.now(); const f=()=>{ n++; if(performance.now()-t<1000) requestAnimationFrame(f); else r(n); }; requestAnimationFrame(f); }));
  R.final=await chk(); R.errs=errs;
  await b.close(); return R;
}
(async()=>{
  const rows=[];
  rows.push(await run("default: box ticked, tap Drop In",{expect:{moves:true,hud:true,hudLabel:"TILT"}}));
  rows.push(await run("untick box, Drop In (tilt must stay OFF)",{untickFirst:true,expect:{still:true,hud:false}}));
  rows.push(await run("untick then re-tick, Drop In",{untickFirst:true,tickAfterUntick:true,expect:{moves:true,hud:true}}));
  rows.push(await run("denied, then tick the box again (iOS remembers)",{mode:"deny",retickAfterDeny:true,expect:{still:true,note:"denied",helpShown:true}}));
  rows.push(await run("permission denied",{mode:"deny",expect:{still:true,note:"denied",hud:true,hudLabel:"TILT BLOCKED"}}));
  rows.push(await run("no sensor data (desktop/locked)",{sensor:false,expect:{still:true,note:"no motion data",hud:true,hudLabel:"NO TILT SENSOR"}}));
  rows.push(await run("untick during load (race)",{checkLoadRace:true,expect:{still:true}}));
  rows.push(await run("tap TILT pill recentres",{hudRecenter:true,expect:{moves:true}}));
  for(const r of rows) console.log((r.result==="PASS"?"PASS ":"FAIL ")+r.name+(r.result==="PASS"?"":"  -> "+r.result)+"  [moved "+r.moved+"m steer "+r.steered+" note "+JSON.stringify(r.final.note)+" hud "+JSON.stringify(r.hud)+(r.recenter?" recentre "+JSON.stringify(r.recenter):"")+"]");
  const nf=rows.filter(r=>r.result!=="PASS").length; console.log(nf? nf+" FAILED":"ALL TILT E2E PASS"); process.exit(nf?1:0);
})();
