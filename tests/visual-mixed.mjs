// Run with HF_PACKAGE, GSAP_FILE, THREE_FILE, CHROME_PATH pointing at local installations.
// Evidence stays in /tmp; this is a synthetic runtime check, not production reuse acceptance.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import http from 'node:http';
import { createRequire } from 'node:module';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const { HF_PACKAGE, GSAP_FILE, THREE_FILE, CHROME_PATH } = process.env;
const gpuMode=process.env.HF_BROWSER_MODE||'software';
assert(['software','hardware'].includes(gpuMode));
assert(HF_PACKAGE && GSAP_FILE && THREE_FILE && CHROME_PATH, 'Set HF_PACKAGE, GSAP_FILE, THREE_FILE, CHROME_PATH');
const require = createRequire(path.join(HF_PACKAGE, 'package.json'));
const puppeteer = require('puppeteer-core');
const output = await fs.mkdtemp(path.join(os.tmpdir(), 'hf-mixed-'));
for (const [source, target] of [
  [path.join(repo,'tests/visual-mixed.html'),'index.html'],
  [path.join(repo,'.studio/runtime/scene-binding.js'),'scene-binding.js'],
  [path.join(HF_PACKAGE,'dist/hyperframe.runtime.iife.js'),'runtime.js'],
  [GSAP_FILE,'gsap.min.js'], [THREE_FILE,'three.min.js'],
]) await fs.copyFile(source,path.join(output,target));
// Frozen, local test texture. No network provider or private Work content.
assert.equal(spawnSync('ffmpeg',['-v','error','-f','lavfi','-i','color=c=white:s=8x8','-frames:v','1',path.join(output,'texture.png')]).status,0);
const server=http.createServer(async(req,res)=>{
  try { const name=decodeURIComponent(req.url.split('?')[0]).replace(/^\//,'')||'index.html';
    assert(!name.includes('..'));let data=await fs.readFile(path.join(output,name));
    if(name==='index.html') data=data.toString().replace('<head>','<head><script src="runtime.js"></script>');
    res.setHeader('Content-Type',name.endsWith('.js')?'application/javascript':name.endsWith('.png')?'image/png':'text/html');
    if(name==='texture.png') await new Promise(resolve=>setTimeout(resolve,150));
    res.end(data);
  } catch { res.writeHead(404);res.end(); }
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const browser=await puppeteer.launch({executablePath:CHROME_PATH,headless:true,args:['--disable-dev-shm-usage',...(process.platform==='linux'?['--no-sandbox']:[]),...(gpuMode==='software'?['--enable-unsafe-swiftshader','--use-angle=swiftshader']:[])]});
const errors=[];
const interactiveBackends=[];
try {
  const page=await browser.newPage();await page.setViewport({width:960,height:540});
  page.on('pageerror',error=>errors.push(error.message));
  page.on('console',message=>{const text=message.text();if(text.startsWith('HF_WEBGL_BACKEND '))interactiveBackends.push(JSON.parse(text.slice(17)))});
  await page.goto(`http://127.0.0.1:${server.address().port}`,{waitUntil:'load'});
  await page.evaluate(()=>fixtureReady);
  await page.waitForFunction(()=>typeof window.__player?.renderSeek==='function');
  await page.evaluate(async()=>{
    let release,draws=0;
    const binding=HarnessScene.bindScene({duration:1,ready:new Promise(resolve=>{release=resolve}),renderAt(){draws++}});
    window.__player.renderSeek(.5);
    const pending=window.__hfWaitForSeekCompletion();await Promise.resolve();
    if(draws!==0)throw Error('render ran before resources were ready');
    release();await pending;if(draws!==1)throw Error('ready did not unblock render');binding.dispose();
    const rejected=HarnessScene.bindScene({duration:1,ready:Promise.reject(new Error('missing asset')),renderAt(){throw Error('must not render')}});
    try{await rejected.seek(0);throw Error('missing asset accepted')}catch(error){if(error.message!=='missing asset')throw error}finally{rejected.dispose()}
  });
  const samples=[];
  for(const time of [2.5,0,.5,2.5]) {
    samples.push(await page.evaluate(async(time)=>{
      window.__player.renderSeek(time);await window.__hfWaitForSeekCompletion?.();
      return {time,textureLoaded,records:records.map(r=>{
        const gl=r.renderer.getContext(), pixels=new Uint8Array(480*280*4);gl.readPixels(0,0,480,280,gl.RGBA,gl.UNSIGNED_BYTE,pixels);
        return {local:r.time,progress:r.state.progress,domProgress:gsap.getProperty(document.querySelector(`#${r.id} .progress`),'scaleX'),lit:pixels.filter((v,i)=>i%4!==3&&v>40).length,png:r.renderer.domElement.toDataURL()};
      })};
    },time));
  }
  assert.deepEqual(samples[0],samples[3],'random seek must reconstruct identical pixels/state');
  for(const sample of samples) for(const [i,record] of sample.records.entries()) {
    assert.equal(record.local,Math.max(0,Math.min(2,sample.time-i)));
    assert.equal(record.progress,record.local/2);assert.equal(record.domProgress,record.progress);assert(record.lit>1000,'WebGL must be nonblank');
  }
  assert.notEqual(samples[0].records[0].png,samples[1].records[0].png,'spatial state must move');
  await page.screenshot({path:path.join(output,'mixed.png')});
  await page.evaluate(()=>{window.__player.seek(0);window.__player.play()});
  await new Promise(resolve=>setTimeout(resolve,250));
  assert(await page.evaluate(()=>{window.__player.pause();return records[0].time>0}),'upstream playback must advance the same binding');
  await page.evaluate(async()=>{
    const r=records[0], draws=r.draws;r.binding.dispose();r.binding.dispose();
    window.__player.renderSeek(1);await window.__hfWaitForSeekCompletion?.();
    if(r.draws!==draws||r.disposed!==1)throw Error('dispose did not detach/release exactly once');
  });
  assert.deepEqual(errors,[]);
  await fs.writeFile(path.join(output,'browser-evidence.json'),JSON.stringify({platform:process.platform,requestedGpuMode:gpuMode,interactiveBackends,samples:samples.map(s=>({...s,records:s.records.map(({png,...r})=>r)})),versions:await page.evaluate(()=>({gsap:gsap.version,three:THREE.REVISION})),errors},null,2));
} finally {await browser.close();await new Promise(resolve=>server.close(resolve));}
const renderEnv={...process.env,DO_NOT_TRACK:'1',PRODUCER_BROWSER_GPU_MODE:gpuMode,HYPERFRAMES_BROWSER_PATH:CHROME_PATH};
const check=spawnSync(process.execPath,[path.join(HF_PACKAGE,'dist/cli.js'),'check',output,'--json'],{encoding:'utf8',env:renderEnv,timeout:90000});
await fs.writeFile(path.join(output,'check.json'),check.stdout);
await fs.writeFile(path.join(output,'check.log'),check.stderr);
assert.equal(check.status,0,`HyperFrames check failed; see ${output}/check.json`);
const result=spawnSync(process.execPath,[path.join(HF_PACKAGE,'dist/cli.js'),'render',output,'--output',path.join(output,'mixed.mp4'),'--fps','12','--quality','draft','--workers','1',...(gpuMode==='software'?['--no-browser-gpu']:['--browser-gpu']),'--experimental-fast-capture=false'],{encoding:'utf8',env:renderEnv,timeout:180000});
await fs.writeFile(path.join(output,'render.log'),result.stdout+result.stderr);
assert.equal(result.status,0,`HyperFrames render failed; see ${output}/render.log`);
assert(!/Browser:PAGEERROR|sub_timeline_readiness_timeout/.test(result.stdout+result.stderr),'render must not silently succeed with broken WebGL or missing timelines');
assert((await fs.stat(path.join(output,'mixed.mp4'))).size>1000);
const probe=spawnSync('ffprobe',['-v','error','-show_entries','stream=width,height,duration,nb_frames,codec_name:stream_tags=encoder:format_tags=encoder','-of','json',path.join(output,'mixed.mp4')],{encoding:'utf8'});
assert.equal(probe.status,0);await fs.writeFile(path.join(output,'ffprobe.json'),probe.stdout);
await fs.writeFile(path.join(output,'backend-evidence.json'),JSON.stringify({platform:process.platform,requestedGpuMode:gpuMode,interactiveBackends,captureBackends:(result.stdout+result.stderr).split('\n').filter(line=>line.includes('HF_WEBGL_BACKEND ')||line.includes('[BrowserManager] Browser launched')),encoding:JSON.parse(probe.stdout),hardwareAcceptance:'Inspect actual renderer and encoder evidence; requested mode alone is not proof'},null,2));
const frames=spawnSync('ffmpeg',['-v','error','-i',path.join(output,'mixed.mp4'),'-vf','fps=1','-f','framemd5','-'],{encoding:'utf8'});
assert.equal(frames.status,0);const hashes=frames.stdout.split('\n').filter(line=>line&&!line.startsWith('#')).map(line=>line.split(',').at(-1).trim());
assert(new Set(hashes).size>=3,'rendered motion must change, not hold a static/blank frame');
await fs.writeFile(path.join(output,'frames.md5'),frames.stdout);
assert.equal(spawnSync('ffmpeg',['-v','error','-ss','2.5','-i',path.join(output,'mixed.mp4'),'-frames:v','1',path.join(output,'rendered.png')]).status,0);
console.log(output);
