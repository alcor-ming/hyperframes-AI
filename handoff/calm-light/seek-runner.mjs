import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import http from 'node:http';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';

const graphCases = [
  {name:'star4-chinese',ratio:'16:9',variant:'star',slots:{hub:'调度',n1:'输入',n2:'工具',n3:'记忆',n4:'输出'}},
  {name:'chain8-chinese',ratio:'16:9',variant:'chain',slots:{hub:'中枢调度系统',...Object.fromEntries(Array.from({length:7},(_,i)=>['n'+(i+1),'中文六个字符']))}},
  {name:'mesh9-portrait',ratio:'9:16',variant:'mesh',slots:{hub:'中枢调度系统',...Object.fromEntries(Array.from({length:8},(_,i)=>['n'+(i+1),'中文六个字符']))}}
];

export async function run(id, {reviewOnly=false}={}) {
  const root=path.dirname(fileURLToPath(import.meta.url));
  const require=createRequire(process.env.PLAYWRIGHT_PACKAGE?path.join(process.env.PLAYWRIGHT_PACKAGE,'package.json'):import.meta.url);
  const {chromium}=require('playwright');
  const mime={'.html':'text/html','.js':'text/javascript','.json':'application/json','.ttf':'font/ttf','.otf':'font/otf','.woff2':'font/woff2'};
  const server=http.createServer(async(req,res)=>{
    try{
      const target=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://local').pathname));
      if(!target.startsWith(root+path.sep))throw Error('outside');
      const bytes=await fs.readFile(target);res.writeHead(200,{'Content-Type':mime[path.extname(target)]||'application/octet-stream'});res.end(bytes);
    }catch{res.writeHead(404);res.end();}
  });
  await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',resolve);});
  let browser;const results=[],digest=bytes=>createHash('sha256').update(bytes).digest('hex');
  try{
    browser=await chromium.launch({headless:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});
    const page=await browser.newPage({viewport:{width:1400,height:1400},deviceScaleFactor:1});
    const failures=[];page.on('pageerror',e=>failures.push(e.message));
    await page.goto(`http://127.0.0.1:${server.address().port}/${id}/fixture/index.html`);
    await page.evaluate(()=>readyPromise);
    const graph=id==='graph-grow',variants=graph?['star','chain','layers','mesh']:['fill','overflow','generate'];
    const durations=graph?[4,6,10]:[5,7,12],configs=[];
    if(!reviewOnly)for(const ratio of ['16:9','9:16'])for(const theme of ['light','dark'])for(const variant of variants)for(const reduced of [false,true])for(const duration of durations)configs.push({ratio,theme,variant,reduced,duration});
    if(graph)for(const target of graphCases)for(const theme of ['light','dark'])for(const reduced of [false,true])configs.push({...target,theme,reduced,duration:6,extra:{path:'n1/hub/n4'}});
    else for(const ratio of ['16:9','9:16'])for(const variant of variants)for(const capacity_ratio of [.5,1.5]){
      if(variant==='overflow'&&capacity_ratio<=1)continue;
      configs.push({name:'capacity-extreme',ratio,theme:'light',variant,reduced:false,duration:7,extra:{token_count:80,capacity_ratio}});
    }
    async function layout() {
      return page.evaluate(()=>{
        const host=document.getElementById('frame').getBoundingClientRect();
        const labels=[...document.querySelectorAll('[data-calm-label]')].filter(e=>getComputedStyle(e).opacity!=='0'&&
          !e.parentElement.closest('[data-calm-label]')).map(e=>({name:e.dataset.calmLabel,...Object.fromEntries(['left','right','top','bottom'].map(k=>[k,e.getBoundingClientRect()[k]]))}));
        const collisions=[];
        for(let i=0;i<labels.length;i++)for(let j=i+1;j<labels.length;j++){
          const a=labels[i],b=labels[j];if(a.left<b.right-.5&&a.right>b.left+.5&&a.top<b.bottom-.5&&a.bottom>b.top+.5)collisions.push([a.name,b.name]);
        }
        return {collisions,bounds:labels.map(r=>({name:r.name,ok:r.left>=host.left-.5&&r.right<=host.right+.5&&r.top>=host.top-.5&&r.bottom<=host.top+host.height*.84+.5}))};
      });
    }
    const capture=async t=>{await page.evaluate(t=>seek(t),t);return page.locator('#frame').screenshot({animations:'disabled'});};
    for(const config of configs){
      // Reset overrides between every case, rather than inheriting the prior stress case.
      const moments=await page.evaluate(c=>configure(c),{...config,extra:config.extra||{}});
      const times=config.name&&graph?[3.5,5.2,6.8,8]:[2,...moments.key_moments,2+config.duration,2+config.duration*.371].filter((t,i,a)=>a.indexOf(t)===i).sort((a,b)=>a-b);
      const events=[...moments.key_moments,2+config.duration];assert.ok(events.every((t,i)=>!i||t-events[i-1]<=2+1e-8));
      for(const t of times){
        await page.evaluate(t=>{for(let u=2;u<t;u+=1/30)seek(u);seek(t);},t);
        const forward=await capture(t),expected=digest(forward);
        await page.evaluate(()=>seek(0));assert.equal(digest(await capture(t)),expected,'direct seek '+JSON.stringify(config)+' '+t);
        await page.evaluate(t=>seek(t),2+config.duration);assert.equal(digest(await capture(t)),expected,'back seek');
        assert.equal(digest(await capture(t)),expected,'repeat seek');
        const inspected=await layout();assert.ok(inspected.bounds.every(r=>r.ok),JSON.stringify({config,t,...inspected}));
        assert.deepEqual(inspected.collisions,[],JSON.stringify({config,t,...inspected}));
        if(!config.reduced&&((config.name&&graph)||(!config.name&&config.variant===(graph?'star':'overflow')&&config.duration===(graph?6:7)&&moments.key_moments.includes(t)))){
          const prefix=`${config.name||config.ratio.replace(':','x')}-${config.theme}-${(t-2).toFixed(3)}`;
          await fs.writeFile(path.join(root,id,'qa',prefix+'.png'),forward);
          if(config.name&&t===8){
            await page.locator('#frame').evaluate(e=>e.style.filter='grayscale(1)');
            await fs.writeFile(path.join(root,id,'qa',prefix+'-gray.png'),await page.locator('#frame').screenshot());
            await page.locator('#frame').evaluate(e=>e.style.filter='');
            for(const scale of [.5,.25]){
              await page.locator('#frame').evaluate((e,s)=>{e.style.transform=`scale(${s})`;e.style.transformOrigin='top left';},scale);
              await fs.writeFile(path.join(root,id,'qa',prefix+`-${scale*100}pct.png`),await page.locator('#frame').screenshot());
            }
            await page.locator('#frame').evaluate(e=>e.style.transform='');
          }
        }
      }
      // Resize-and-return must not change label padding, geometry or frame identity.
      const t=2+config.duration,before=digest(await capture(t));
      await page.evaluate(()=>{const e=document.getElementById('frame');window.__oldSize=[e.style.width,e.style.height];e.style.width=(e.clientWidth*.8)+'px';e.style.height=(e.clientHeight*.8)+'px';});
      await capture(t);
      await page.evaluate(()=>{const e=document.getElementById('frame');[e.style.width,e.style.height]=window.__oldSize;});
      assert.equal(digest(await capture(t)),before,'resize-and-return');
      results.push({...config,pixelSeek:true,captionSafe:true,labelCollisionFree:true});
    }
    await page.evaluate(()=>disposeShot());
    assert.deepEqual(await page.evaluate(()=>({children:document.querySelector('#stage').children.length+document.querySelector('#text').children.length,rhythm:window.__hfRhythmSources?.size??0})),{children:0,rhythm:0});
    assert.deepEqual(failures,[]);
    await fs.writeFile(path.join(root,id,'qa',reviewOnly?'review-results.json':'results.json'),JSON.stringify({passed:true,checks:results},null,2));
    console.log(`${id}: ${results.length} configurations passed pixel seek, caption/label bounds, resize and cleanup`);
  }finally{await browser?.close();await new Promise(resolve=>server.close(resolve));}
}
