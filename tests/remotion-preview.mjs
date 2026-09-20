// Synthetic HF/Remotion integration. Never invokes a video renderer.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import http from 'node:http';
import {spawnSync} from 'node:child_process';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const require = createRequire(path.join(repo, '.studio/remotion/package.json'));
const {build} = require('esbuild');
const {chromium} = require('playwright-core');

export async function verifyRemotion({studio = false} = {}) {
  if (studio) assert.equal(process.platform, 'win32', 'Native Windows Studio evidence requires Windows; WSL is not a substitute');
  const {HF_RUNTIME, HF_PACKAGE, GSAP_FILE, CHROME_PATH} = process.env;
  assert(CHROME_PATH && GSAP_FILE, 'Set CHROME_PATH and GSAP_FILE to local pinned tools');
  assert(studio ? HF_PACKAGE : HF_RUNTIME, 'Set HF_PACKAGE for Studio, HF_RUNTIME for runtime-only evidence');
  const output = await fs.mkdtemp(path.join(os.tmpdir(), 'hf-remotion-'));
  const project = path.join(output, 'project');
  await fs.mkdir(project);
  await fs.copyFile(path.join(repo, '.studio/runtime/scene-binding.js'), path.join(project, 'scene-binding.js'));
  await fs.copyFile(GSAP_FILE, path.join(project, 'gsap.min.js'));
  await fs.copyFile(path.join(path.dirname(GSAP_FILE), 'MotionPathPlugin.min.js'), path.join(project, 'MotionPathPlugin.min.js'));
  if (!studio) await fs.copyFile(HF_RUNTIME, path.join(project, 'hf-runtime.js'));
  const entry = `import React from 'react';
import {useCurrentFrame} from 'remotion';
import {mountRemotion} from './preview.jsx';
function Shot() { const frame=useCurrentFrame(); return <div style={{width:960,height:540,background:'#f0f4f2',fontFamily:'Arial',padding:40,boxSizing:'border-box'}}>
<h1 style={{fontSize:38}}>Semantic timing</h1><div id="moving" style={{width:100,height:100,background:'#188b72',transform:'translateX('+frame*2+'px)'}}/>
<p id="first" style={{fontSize:26,visibility:frame>=30?'visible':'hidden'}}>First complete idea</p>
<p id="second" style={{fontSize:26,visibility:frame>=90?'visible':'hidden'}}>Next idea, not before its cue</p>
<output id="actual-frame" style={{fontSize:24}}>{frame}</output></div>; }
window.releaseAssets=null;
window.fixtureBinding=mountRemotion({container:document.getElementById('remotion'),component:Shot,start:1,fps:30,durationInFrames:180,width:960,height:540,
ready:new Promise(resolve=>{window.releaseAssets=resolve})});
window.fixtureReady=window.fixtureBinding.ready;
window.__timelines={'remotion-fixture':gsap.timeline({paused:true}).to({},{duration:8})};`;
  await build({stdin:{contents:entry,resolveDir:path.join(repo,'.studio/remotion'),loader:'jsx'},
    outfile:path.join(project,'preview.js'),bundle:true,format:'iife',define:{'process.env.NODE_ENV':'"production"'}});
  const rate = 24000, wav = Buffer.alloc(44 + rate * 8 * 2);
  wav.write('RIFF'); wav.writeUInt32LE(wav.length - 8, 4); wav.write('WAVEfmt ', 8);
  wav.writeUInt32LE(16,16); wav.writeUInt16LE(1,20); wav.writeUInt16LE(1,22);
  wav.writeUInt32LE(rate,24); wav.writeUInt32LE(rate*2,28); wav.writeUInt16LE(2,32); wav.writeUInt16LE(16,34);
  wav.write('data',36); wav.writeUInt32LE(wav.length-44,40);
  for(let i=0;i<rate*8;i++) wav.writeInt16LE(Math.round(4000*Math.sin(2*Math.PI*440*i/rate)),44+i*2);
  await fs.writeFile(path.join(project,'tone.wav'),wav);
  await fs.writeFile(path.join(project,'index.html'),`<!doctype html><html><head><meta charset="utf-8">
<title>HF Remotion integration</title><style>body{margin:0}#remotion{width:min(960px,100vw);aspect-ratio:16/9}</style>
<script src="gsap.min.js"></script><script src="MotionPathPlugin.min.js"></script><script src="scene-binding.js"></script>
${studio?'':'<script src="hf-runtime.js"></script>'}</head><body>
<main data-composition-id="remotion-fixture" data-start="0" data-duration="8" data-width="960" data-height="540">
<section id="S01" data-start="0" data-duration="8" data-track-index="0"><div id="remotion"></div></section>
<audio id="fixture-audio" class="clip" src="tone.wav" data-start="0" data-duration="8" data-track-index="1"></audio></main>
<script src="preview.js"></script></body></html>`);
  let server, browser, cli, port;
  const evidence = {platform:process.platform,studio,scope:studio?'native-studio-with-audio':'visual-only',
    audioAcceptance:studio?'required':'deferred-to-windows',videoExported:false,passed:false,errors:[],output};
  const run = args => spawnSync(process.execPath,[cli,'preview',project,...args],{cwd:project,encoding:'utf8',timeout:90000,
    env:{...process.env,DO_NOT_TRACK:'1',HYPERFRAMES_NO_TELEMETRY:'1',XDG_STATE_HOME:path.join(output,'state')}});
  try {
    let url;
    if(studio) {
      cli=path.join(HF_PACKAGE,'dist/cli.js');
      const result=run(['--background','--json','--no-open']);
      assert.equal(result.status,0,result.stderr||result.stdout);
      const record=JSON.parse(result.stdout).result;
      port=record.port; url=record.studioUrl;
      assert.equal(path.resolve(record.projectDir),path.resolve(project));
      evidence.studioUrl=url;
    } else {
      server=http.createServer(async(req,res)=>{
        try { const name=decodeURIComponent(new URL(req.url,'http://localhost').pathname).slice(1)||'index.html';
          const file=path.resolve(project,name);
          if(!file.startsWith(project+path.sep)) {res.writeHead(403).end();return;}
          res.setHeader('Content-Type',file.endsWith('.js')?'application/javascript':file.endsWith('.wav')?'audio/wav':'text/html');
          res.end(await fs.readFile(file));
        } catch {res.writeHead(404).end();}
      });
      await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',resolve);});
      url=`http://127.0.0.1:${server.address().port}`;
    }
    const profile=path.join(output,'browser');
    await fs.mkdir(path.join(profile,'Default'),{recursive:true});
    await fs.writeFile(path.join(profile,'Default/Preferences'),JSON.stringify({enable_do_not_track:true}));
    browser=await chromium.launchPersistentContext(profile,{executablePath:CHROME_PATH,headless:true,
      viewport:{width:1280,height:900},args:process.platform==='linux'?['--no-sandbox']:[]});
    const page=await browser.newPage();
    page.on('pageerror',e=>evidence.errors.push(e.message));
    await page.route('**/*',route=>{
      const u=new URL(route.request().url());
      return /^https?:$/.test(u.protocol)&&!['127.0.0.1','localhost','[::1]'].includes(u.hostname)?route.abort():route.continue();
    });
    await page.goto(url);
    let frame=page.mainFrame();
    if(studio) {const iframe=page.locator('iframe').first();await iframe.waitFor();frame=await(await iframe.elementHandle()).contentFrame();}
    await frame.waitForFunction(()=>typeof window.releaseAssets==='function'&&window.__player);
    assert.equal(await frame.evaluate(()=>document.getElementById('remotion').dataset.remotionFrame),undefined);
    await frame.evaluate(async()=>{window.releaseAssets();await window.fixtureReady;});
    const seek=async time=>{
      if(studio) await page.locator('hyperframes-player').evaluate((p,t)=>p.seek(t),time);
      else await frame.evaluate(t=>window.__player.renderSeek(t),time);
      await frame.evaluate(()=>window.__hfWaitForSeekCompletion?.());
      const expected=Math.min(179,Math.max(0,Math.floor((time-1)*30+1e-7)));
      await frame.waitForFunction(f=>document.querySelector('#actual-frame')?.textContent===String(f),expected);
      return frame.evaluate(()=>({frame:document.querySelector('#actual-frame').textContent,
        x:document.querySelector('#moving').style.transform,
        first:getComputedStyle(document.querySelector('#first')).visibility,
        second:getComputedStyle(document.querySelector('#second')).visibility}));
    };
    const states=[];
    for(const t of [4.5,0,2.5,4.5,8]) states.push(await seek(t));
    assert.deepEqual(states[0],states[3]); assert.equal(states[1].first,'hidden');
    assert.equal(states[2].first,'visible');assert.equal(states[2].second,'hidden');
    assert.equal(states[3].second,'visible');
    await seek(0);
    if(studio) await page.getByRole('button',{name:'Play',exact:true}).click();
    else await frame.evaluate(()=>window.__player.play());
    await page.waitForTimeout(1600);
    if(studio) await page.getByRole('button',{name:'Pause',exact:true}).click();
    else await frame.evaluate(()=>window.__player.pause());
    const advanced=await frame.locator('#actual-frame').textContent();assert(Number(advanced)>0);
    await page.waitForTimeout(200);assert.equal(await frame.locator('#actual-frame').textContent(),advanced,'No second clock while HF is paused');
    const audioState=await frame.evaluate(()=>{const audio=document.querySelector('audio');return {
      time:audio.currentTime,paused:audio.paused,readyState:audio.readyState,error:audio.error?.message||null};});
    evidence.audioState=audioState;evidence.playbackFrame=Number(advanced);
    // Keep the observed probe in WSL evidence, but acceptance belongs to Windows.
    // Native failures must be diagnosed against HF's actual audio owner, not waived.
    if(studio) {
      assert.equal(audioState.error,null);assert.equal(audioState.paused,true);
      assert(audioState.readyState>=2,'HF audio must be loaded');
      assert(Math.abs(audioState.time-(Number(advanced)/30+1))<0.2,`HF audio and derived Remotion frame must share time: ${JSON.stringify(audioState)} frame=${advanced}`);
    }
    const shot=await page.screenshot({path:path.join(output,'desktop.png')});
    const green=await page.evaluate(async base64=>{
      const image=new Image();image.src='data:image/png;base64,'+base64;await image.decode();
      const c=document.createElement('canvas');c.width=image.width;c.height=image.height;
      const context=c.getContext('2d');context.drawImage(image,0,0);
      const pixels=context.getImageData(0,0,c.width,c.height).data;let n=0;
      for(let i=0;i<pixels.length;i+=4)if(pixels[i]<60&&pixels[i+1]>100&&pixels[i+2]>70&&pixels[i+1]>pixels[i+2])n++;
      return n;
    },shot.toString('base64'));assert(green>100,'Actual screenshot must contain the animated object');
    await page.setViewportSize({width:390,height:844});
    await seek(4.5);
    await page.screenshot({path:path.join(output,'mobile.png')});
    await frame.evaluate(()=>window.fixtureBinding.dispose());
    assert.equal(await frame.locator('#actual-frame').count(),0);
    assert.deepEqual(evidence.errors,[]);
    evidence.states=states;evidence.greenPixels=green;evidence.playbackFrame=Number(advanced);evidence.audioState=audioState;
    evidence.audio='Synthetic tone is HF-owned; physical sound and native audible alignment are not verified by this check';
    evidence.passed=true;
  } catch(error) {evidence.failure=error.stack;throw error;}
  finally {
    await browser?.close();
    if(server)await new Promise(resolve=>server.close(resolve));
    if(cli&&port){const stopped=run(['--stop','--json','--port',String(port)]);if(stopped.status!==0){evidence.passed=false;throw new Error(stopped.stderr||'Studio stop failed');}}
    await fs.writeFile(path.join(output,'verification.json'),JSON.stringify(evidence,null,2));
    console.log(output);
  }
  return evidence;
}

if(process.argv[1]&&pathToFileURL(path.resolve(process.argv[1])).href===import.meta.url)await verifyRemotion();
