// Grind reliability: for every rail, approach at several angles/offsets, press K once when in range.
const puppeteer=require('puppeteer-core');
(async()=>{ const b=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--mute-audio']});
const pg=await b.newPage(); await pg.goto('http://localhost:8765/sunset-yard-3d.html?shot',{waitUntil:'domcontentloaded',timeout:0}); await pg.waitForFunction('window.__booted===true',{timeout:180000});
await pg.evaluate(()=>window.__startGame());
const r=await pg.evaluate(()=>{ const D=window.__dbg,H=D.held,E=D.edges; const out=[];
 D.rails.forEach((rl,ri)=>{ for(const ang of [0,0.44,0.87]) for(const side of [-1,1]) for(const off of [0.6,1.1,1.6]){
   for(const k in H)H[k]=false; E.clear(); D.state().phase='playing'; D.state().time=120;
   const px=-rl.dir.z, pz=rl.dir.x;                       // perpendicular
   const mid={x:rl.a.x+rl.dir.x*rl.len*0.45, z:rl.a.z+rl.dir.z*rl.len*0.45};
   // start 5m back along a line that converges on the rail at angle ang, ending 'off' to the side
   const hx=rl.dir.x*Math.cos(ang)-side*px*Math.sin(ang), hz=rl.dir.z*Math.cos(ang)-side*pz*Math.sin(ang);
   const sx=mid.x+side*px*off-hx*5, sz=mid.z+side*pz*off-hz*5;
   if(D.surfH(sx,sz)>0.2) continue;
   D.place(sx,sz,Math.atan2(hx,hz),6); const S=D.sk(); S.railCoolT=0; S.fakie=false;
   let pressed=false, got=false;
   for(let i=0;i<240;i++){ const s=D.sk();
     if(!pressed && s.state==='roll'){ const nr0=window.__dbg.rails.length; const lbl=document.getElementById('manBtn').textContent; if(lbl==='GRIND'){ E.add('manual'); pressed=true; } }
     D.step(1); if(D.sk().state==='grind'){ got=true; break; } }
   out.push({ri,ang:+ang.toFixed(2),side,off,pressed,got});
 } }); return out; });
const tot=r.length, pressed=r.filter(x=>x.pressed).length, got=r.filter(x=>x.got).length;
console.log(`attempts ${tot}  GRIND prompt shown ${pressed}  locked on ${got}  (${Math.round(100*got/Math.max(1,pressed))}% of prompted)`);
const byRail={}; r.forEach(x=>{ const k='rail'+x.ri; byRail[k]=byRail[k]||[0,0,0]; byRail[k][0]++; if(x.pressed)byRail[k][1]++; if(x.got)byRail[k][2]++; });
console.log(JSON.stringify(byRail)); console.log('misses:',JSON.stringify(r.filter(x=>x.pressed&&!x.got).slice(0,12)));
await b.close(); })();
