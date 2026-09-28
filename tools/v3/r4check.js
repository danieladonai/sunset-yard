const puppeteer=require('puppeteer-core');
(async()=>{ const b=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--mute-audio']});
const pg=await b.newPage(); pg.on('console',m=>{ const t=m.text(); if(/rider|error|warn|fail/i.test(t)) console.log('CONSOLE',t.slice(0,300)); }); pg.on('pageerror',e=>console.log('PAGEERR',e.message));
pg.on('response',r=>{ if(r.status()>=400) console.log('HTTP',r.status(),r.url()); });
await pg.goto('http://localhost:8765/sunset-yard-3d.html?shot',{waitUntil:'domcontentloaded',timeout:0}); await pg.waitForFunction('window.__booted===true',{timeout:180000});
await pg.evaluate(()=>window.__startGame()); await new Promise(r=>setTimeout(r,8000));
console.log(await pg.evaluate(()=>{ const r=window.__dbg.r4(); return r? {ok:true, acts:Object.keys(r.A), legs:Object.keys(r.legs).map(k=>!!r.legs[k].thigh)} : {ok:false, cm:!!window.__dbg.cm()}; }));
await b.close(); })();
