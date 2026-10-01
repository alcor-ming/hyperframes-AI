import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import http from 'node:http';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
export async function run(id) {
 const root=path.dirname(fileURLToPath(import.meta.url));
 const require=createRequire(process.env.PLAYWRIGHT_PACKAGE?path.join(process.env.PLAYWRIGHT_PACKAGE,'package.json'):import.meta.url);
 const {chromium}=require('playwright');
 const mime={'.html':'text/html','.js':'text/javascript','.json':'application/json','.ttf':'font/ttf','.otf':'font/otf','.woff2':'font/woff2'};
 const server=http.createServer(async(req,res)=>{try{const target=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://local').pathname));if(!target.startsWith(root+path.sep))throw Error('outside');const bytes=await fs.readFile(target);res.writeHead(200,{'Content-Type':mime[path.extname(target)]||'application/octet-stream'});res.end(bytes);}catch{res.writeHead(404);res.end();}});
 await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',resolve);});
 let browser;const results=[];const digest=bytes=>createHash('sha256').update(bytes).digest('hex');
 try {
 browser=await chromium.launch({headless:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});
 const page=await browser.newPage({viewport:{width:1200,height:1200},deviceScaleFactor:1});
 const failures=[];page.on('pageerror',e=>failures.push(e.message));
 const url=`http://127.0.0.1:${server.address().port}/${id}/fixture/index.html`;
 await page.goto(url);await page.evaluate(()=>readyPromise);
 const graph=id==='graph-grow',variants=graph?['star','chain','layers','mesh']:['fill','overflow','generate'],durations=graph?[4,6,10]:[5,7,12];
 for(const ratio of ['16:9','9:16'])for(const theme of ['light','dark'])for(const variant of variants)for(const reduced of [false,true])for(const duration of durations){
  const config={ratio,theme,variant,reduced,duration};const moments=await page.evaluate(c=>configure(c),config);
  const times=[2,...moments.key_moments,2+duration,2+duration*.371].filter((t,i,a)=>a.indexOf(t)===i).sort((a,b)=>a-b);
  assert.ok(times.every((t,i)=>!i||t-times[i-1]<=2+1e-8),'effective moments gap >2 seconds');
  const capture=async t=>{await page.evaluate(t=>seek(t),t);return page.locator('#frame').screenshot({animations:'disabled'});};
  for(const t of times){
   await page.evaluate(t=>{for(let u=2;u<t;u+=1/30)seek(u);seek(t);},t);
   const forward=await capture(t),expected=digest(forward);
   await page.evaluate(()=>seek(0));assert.equal(digest(await capture(t)),expected,'direct seek '+JSON.stringify(config)+' '+t);
   await page.evaluate(t=>seek(t),2+duration);assert.equal(digest(await capture(t)),expected,'back seek');
   assert.equal(digest(await capture(t)),expected,'repeat seek');
  const bounds=await page.evaluate(()=>{const host=document.getElementById('frame').getBoundingClientRect();return [...document.querySelectorAll('[data-calm-label]')].filter(x=>getComputedStyle(x).opacity!=='0').map(x=>{const r=x.getBoundingClientRect();return {name:x.dataset.calmLabel,ok:r.left>=host.left&&r.right<=host.right+1&&r.top>=host.top&&r.bottom<=host.top+host.height*.84+1};});});
  assert.ok(bounds.every(x=>x.ok),JSON.stringify(bounds));
   if(variant===(graph?'star':'overflow')&&duration===(graph?6:7)&&!reduced&&moments.key_moments.includes(t)){
    await fs.writeFile(path.join(root,id,'qa',`${ratio.replace(':','x')}-${theme}-${(t-2).toFixed(3)}.png`),forward);
   }
  }
  results.push({...config,pixelSeek:true,captionSafe:true});
 }
 // Resources and rhythm registration must return to the pre-mount state.
 await page.evaluate(()=>disposeShot());
 assert.deepEqual(await page.evaluate(()=>({children:document.querySelector('#stage').children.length+document.querySelector('#text').children.length,rhythm:window.__hfRhythmSources?.size??0})),{children:0,rhythm:0});
 assert.deepEqual(failures,[]);await fs.writeFile(path.join(root,id,'qa/results.json'),JSON.stringify({passed:true,checks:results},null,2));
 console.log(`${id}: ${results.length} configuration combinations passed pixel seek, caption bounds and cleanup`);
 }finally{await browser?.close();await new Promise(resolve=>server.close(resolve));}
}
