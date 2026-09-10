// Real player + lifecycle integration. This temporary Work is a technical fixture, not user approval.
// HF_PACKAGE, PLAYWRIGHT_PACKAGE, CHROME_PATH, MIXED_FIXTURE point to existing local dependencies.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {createRequire} from 'node:module';
import {spawn, spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {HF_PACKAGE,PLAYWRIGHT_PACKAGE,CHROME_PATH,MIXED_FIXTURE}=process.env;
assert(HF_PACKAGE&&PLAYWRIGHT_PACKAGE&&CHROME_PATH&&MIXED_FIXTURE);
const require=createRequire(path.join(PLAYWRIGHT_PACKAGE,'package.json'));
const {chromium}=require(PLAYWRIGHT_PACKAGE);
const root=await fs.mkdtemp(path.join(os.tmpdir(),'hf-visual-plan-'));
await fs.cp(path.join(repo,'.studio/templates'),path.join(root,'.studio/templates'),{recursive:true});
const env={...process.env,HYPERFRAMES_AI_ROOT:root,DO_NOT_TRACK:'1',PUPPETEER_EXECUTABLE_PATH:CHROME_PATH};
function work(...args){const result=spawnSync('python',[path.join(repo,'.studio/work.py'),...args],{env,encoding:'utf8',timeout:240000});assert.equal(result.status,0,result.stderr+'\n'+result.stdout);return result.stdout.trim()}
const id=work('new','Technical Visual Plan integration','--workflow','hyperframes_video');
const variant=path.join(root,'works/active',id,'variants/main'),project=path.join(variant,'project');
async function ready(file){let text=await fs.readFile(path.join(variant,file),'utf8');text=text.replace('"pending"','"ready"');await fs.writeFile(path.join(variant,file),text)}
await ready('RESEARCH.md');
for(const file of ['gsap.min.js','three.min.js','texture.png','scene-binding.js']){
  await fs.mkdir(path.join(project,'assets'),{recursive:true});await fs.copyFile(path.join(MIXED_FIXTURE,file),path.join(project,'assets',file));
}
let html=await fs.readFile(path.join(MIXED_FIXTURE,'index.html'),'utf8');
assert.equal(spawnSync('ffmpeg',['-v','error','-f','lavfi','-i','sine=frequency=440:sample_rate=16000:duration=4',path.join(project,'assets/voice.wav')]).status,0);
html=html.replaceAll('src="gsap.min.js"','src="assets/gsap.min.js"').replaceAll('src="three.min.js"','src="assets/three.min.js"').replaceAll('src="scene-binding.js"','src="assets/scene-binding.js"').replace("'texture.png'","'assets/texture.png'")
 .replace('id="first"','id="first" data-scene-id="S01" data-start="0" data-duration="2.25" data-reading-time="1.5"')
 .replace('id="second"','id="second" data-scene-id="S02" data-start="2" data-duration="2" data-reading-time="1"')
 .replace('<h1>','<audio id="voice" src="assets/voice.wav" data-start="0" data-duration="4" data-track-index="0"></audio><h1>');
await fs.writeFile(path.join(project,'index.html'),html);
await fs.mkdir(path.join(project,'compositions'),{recursive:true});
await fs.writeFile(path.join(project,'DESIGN.md'),'Technical test: independent text bindings and layer separation.');
await fs.writeFile(path.join(project,'project-config.json'),'{}');
await fs.appendFile(path.join(variant,'ANIMATION_PLAN.md'),'\n| S02 | P001 | 2-4s | Technical fixture | Compare the second binding | Stable text | index.html | Reading 3s | Work-local | No production claim |\n');
assert.equal(work('preview','register','--purpose','plan'),'plan-v001');
const server=spawn('python',[path.join(repo,'.studio/work.py'),'preview','open','plan-v001','--hyperframes-dist',path.join(HF_PACKAGE,'dist')],{env});
let serverErrors='';server.stderr.on('data',data=>serverErrors+=data);
const url=await new Promise((resolve,reject)=>{server.stdout.on('data',data=>{const match=String(data).match(/http:\/\/127\.0\.0\.1:\d+\//);if(match)resolve(match[0])});server.once('exit',code=>reject(Error(serverErrors+code)));setTimeout(()=>reject(Error('viewer timeout '+serverErrors)),15000).unref()});
const browser=await chromium.launch({executablePath:CHROME_PATH,headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader','--use-angle=swiftshader']});
const errors=[],network=[];
try{
 const page=await browser.newPage({viewport:{width:1440,height:900}});
 page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>network.push(r.url()));
 await page.goto(url);await page.waitForFunction(()=>document.querySelector('#player').duration===4,{timeout:20000});
 const range=await page.request.get(url+'source-snapshot/assets/voice.wav',{headers:{Range:'bytes=8-15'}});
 assert.equal(range.status(),206);assert.equal((await range.body()).length,8);
 const invalid=await page.request.get(url+'source-snapshot/assets/voice.wav',{headers:{Range:'bytes=999999-'}});assert.equal(invalid.status(),416);
 await page.locator('#scenes').selectOption('S02');
 await page.locator('#reading').click();
 assert.equal(await page.locator('#locator').inputValue(),'plan-v001 S02 3.00s');
 await page.locator('#in').click();await page.locator('#out').click();
 assert.equal(await page.locator('#locator').inputValue(),'plan-v001 S02 3.00-3.00s');
 const states=[];
 for(const time of [2.5,0,.5,2.5]) states.push(await page.evaluate(async time=>{const p=document.querySelector('#player');p.seek(time);const w=p.iframeElement.contentWindow;await w.__hfWaitForSeekCompletion();return w.records.map(r=>({local:r.time,progress:r.state.progress,pixels:r.renderer.domElement.toDataURL()}))},time));
 assert.deepEqual(states[0],states[3]);assert.notEqual(states[0][0].pixels,states[1][0].pixels);
 await page.locator('hyperframes-player').getByRole('button',{name:'Play',exact:true}).click();
 await page.waitForFunction(()=>document.querySelector('#player').currentTime>2.6,undefined,{timeout:10000});
 assert(await page.evaluate(()=>{const p=document.querySelector('#player');p.pause();return p.iframeElement.contentDocument.querySelector('#voice').currentTime>2.5}));
 await page.screenshot({path:path.join(root,'desktop.png'),fullPage:true});
 await page.locator('#size').click();assert.equal(await page.locator('#size').getAttribute('aria-pressed'),'true');
 await page.locator('#size').click();await page.setViewportSize({width:390,height:844});
 await page.screenshot({path:path.join(root,'mobile.png'),fullPage:true});
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'mobile must not overflow');
 assert.deepEqual(errors,[]);assert.deepEqual(network,[]);
}finally{await browser.close();server.kill('SIGINT');await new Promise(resolve=>server.once('exit',resolve))}
work('preview','accept','plan-v001');
const state=JSON.parse(await fs.readFile(path.join(variant,'variant.yaml'),'utf8'));assert.equal(state.accepted_preview,null);
const renderArgs=['--hyperframes-cli',path.join(HF_PACKAGE,'dist/cli.js'),'--software-gl','--fps','12'];
work('preview','render','plan-v001',...renderArgs,'--output',path.join(root,'draft.mp4'));
assert.equal(work('preview','register',path.join(root,'draft.mp4')),'draft-v001');
work('preview','accept','draft-v001');
work('preview','render','draft-v001','--final',...renderArgs,'--output',path.join(root,'final.mp4'));
const final=work('finalize',path.join(root,'final.mp4'),'--qa-passed');
const manifest=JSON.parse(await fs.readFile(path.join(path.dirname(final),'manifest.json'),'utf8'));
assert.equal(manifest.render.source_preview,'draft-v001');assert.equal(manifest.render.purpose,'final');
await fs.writeFile(path.join(root,'verification.json'),JSON.stringify({technicalFixture:true,errors,network,final,render:manifest.render},null,2));
console.log(root);
