// Isolated technical fixture. Existing local Playwright and Chrome only; no HF runtime.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {createRequire} from 'node:module';
import {spawn, spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {PLAYWRIGHT_PACKAGE,CHROME_PATH}=process.env;
assert(PLAYWRIGHT_PACKAGE&&CHROME_PATH);
const {chromium}=createRequire(path.join(PLAYWRIGHT_PACKAGE,'package.json'))(PLAYWRIGHT_PACKAGE);
const root=await fs.mkdtemp(path.join(os.tmpdir(),'hf-visual-layout-'));
await fs.cp(path.join(repo,'.studio/templates'),path.join(root,'.studio/templates'),{recursive:true});
const env={...process.env,HYPERFRAMES_AI_ROOT:root};
delete env.HYPERFRAMES_DIST;
function work(...args){const r=spawnSync('python',[path.join(repo,'.studio/work.py'),...args],{env,encoding:'utf8',timeout:30000});assert.equal(r.status,0,r.stderr+'\n'+r.stdout);return r.stdout.trim()}
const id=work('new','Technical layout fixture','--workflow','hyperframes_video');
const variant=path.join(root,'works/active',id,'variants/main'),sample=path.join(variant,'layout');
await fs.mkdir(sample);
const research=path.join(variant,'RESEARCH.md');
await fs.writeFile(research,(await fs.readFile(research,'utf8')).replace('"pending"','"ready"'));
await fs.copyFile('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',path.join(sample,'font.ttf'));
await fs.writeFile(path.join(sample,'style.css'),`@font-face{font-family:Fixture;src:url(font.ttf)}
*{box-sizing:border-box}body{margin:0;font:18px Fixture,sans-serif;color:#202020;background:#f3f4f5;letter-spacing:0}
main{width:min(960px,100%);aspect-ratio:16/9;padding:24px;background:#fff;border-top:8px solid #238364}
h1{font-size:28px;margin:0 0 16px}p{margin:12px 0}.placeholder{background:#e4eaed;padding:16px}
button{font:inherit;padding:8px;border:1px solid #555;background:white}button:focus-visible{outline:3px solid #238364}`);
await fs.writeFile(path.join(sample,'index.html'),`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="style.css"><title>Layout fixture</title>
<main data-width="960" data-height="540" data-scene-id="S01"><h1>Layout before motion</h1><p>One real sample establishes the reading hierarchy.</p><div class="placeholder">Media: presenter portrait, 16:9, centered crop.</div><p id="state">Start: statement</p><button id="next" type="button">Next state</button></main><script>document.querySelector('#next').onclick=()=>document.querySelector('#state').textContent='End: supporting evidence';</script></html>`);
assert.equal(work('preview','register','--purpose','plan','--kind','layout','--sample-dir','layout','--scene','S01'),'plan-v001');
let browser,server;
const errors=[],requests=[],failures=[];
try{
 server=spawn('python',[path.join(repo,'.studio/work.py'),'preview','open','plan-v001'],{env});
 let stderr='';server.stderr.on('data',data=>stderr+=data);
 const url=await new Promise((resolve,reject)=>{server.stdout.on('data',data=>{const m=String(data).match(/http:\/\/127\.0\.0\.1:\d+\//);if(m)resolve(m[0])});server.once('exit',code=>reject(Error(stderr+code)));setTimeout(()=>reject(Error('viewer timeout '+stderr)),15000).unref()});
 browser=await chromium.launch({executablePath:CHROME_PATH,headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1440,height:900}});
 page.on('pageerror',error=>errors.push(error.message));page.on('request',request=>requests.push(request.url()));page.on('requestfailed',request=>failures.push(request.url()));
 await page.goto(url);
 const frame=page.frames().find(f=>f.url().endsWith('/source-snapshot/index.html'));assert(frame);
 await frame.evaluate(()=>document.fonts.ready);
 assert(await frame.evaluate(()=>document.fonts.check('18px Fixture')));
 assert.equal(await frame.locator('main').evaluate(el=>el.getBoundingClientRect().width),960);
 assert.equal(await frame.locator('main').evaluate(el=>el.getBoundingClientRect().height),540);
 await frame.locator('#next').click();assert.equal(await frame.locator('#state').textContent(),'End: supporting evidence');
 await page.screenshot({path:path.join(root,'desktop.png'),fullPage:true});
 await page.setViewportSize({width:390,height:844});
 await page.screenshot({path:path.join(root,'mobile.png'),fullPage:true});
 for(const f of page.frames())assert(await f.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'horizontal overflow');
 assert.equal(await frame.locator('audio,video,canvas,hyperframes-player').count(),0);
 assert(requests.some(url=>url.endsWith('/font.ttf')));
 assert(!requests.some(url=>/hyperframe|gsap|three|\.(mp3|mp4|wav)/i.test(new URL(url).pathname)));
 assert.deepEqual(errors,[]);assert.deepEqual(failures,[]);
 await fs.writeFile(path.join(root,'verification.json'),JSON.stringify({technicalFixture:true,errors,failures,requests},null,2));
 // Viewer field compatibility only; the player is a stub, not a runtime check.
 const viewer=await browser.newPage();
 const viewerErrors=[];viewer.on('pageerror',error=>viewerErrors.push(error.message));
 const responses={
  '/viewer-fields':await fs.readFile(path.join(repo,'.studio/visual_plan.html'),'utf8'),
  '/session.json':JSON.stringify({version:'technical-fixture'}),
  '/visual-plan.json':JSON.stringify({id:'plan-v001',scenes:[{id:'S01',start:0,reading:1,intent:{'内容 / 素材引用':'Research S01 / process'}},{id:'S02',start:2,reading:3,intent:{'上屏信息引用':'Legacy Anchor P002'}}]}),
  '/source-snapshot/index.html':'<main data-width="960" data-height="540"></main>',
  '/hf/hyperframes-player.global.js':'customElements.define("hyperframes-player",class extends HTMLElement{seek(time){this.currentTime=time}});',
 };
 await viewer.route('**/*',route=>{const name=new URL(route.request().url()).pathname;assert(Object.hasOwn(responses,name),name);return route.fulfill({body:responses[name],contentType:name.endsWith('.js')?'text/javascript':name.endsWith('.json')?'application/json':'text/html'})});
 await viewer.goto(url+'viewer-fields');
 await viewer.locator('#intent dd').filter({hasText:'Research S01 / process'}).waitFor();
 await viewer.selectOption('#scenes','S02');
 assert((await viewer.locator('#intent').textContent()).includes('Legacy Anchor P002'));
 assert.deepEqual(viewerErrors,[]);assert.equal(await viewer.locator('#error').textContent(),'');
 await viewer.close();
}finally{
 if(browser)await browser.close();
 if(server&&server.exitCode===null){server.kill('SIGINT');await new Promise(resolve=>server.once('exit',resolve))}
}
console.log(root);
