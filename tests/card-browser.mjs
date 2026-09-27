// HF_RUNTIME=<locked 0.8.27 iife> GSAP_FILE=<local gsap> CHROME_PATH=<chromium> node tests/card-browser.mjs
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import http from 'node:http';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const { chromium } = createRequire(path.join(repo, '.studio/remotion/package.json'))('playwright-core');
const { HF_RUNTIME, GSAP_FILE, CHROME_PATH } = process.env;
assert(HF_RUNTIME && GSAP_FILE && CHROME_PATH, 'Set local runtime, GSAP and Chromium paths');
assert.equal(JSON.parse(await fs.readFile(path.resolve(HF_RUNTIME, '../../package.json'), 'utf8')).version, '0.8.27');
const output = await fs.mkdtemp(path.join(os.tmpdir(), 'hf-card-'));
await fs.cp(path.join(repo, '.studio/runtime'), path.join(output, 'runtime'), { recursive: true });
for (const ratio of ['16x9', '9x16']) await fs.cp(path.join(repo, '.studio/components/cover-title-core', ratio, 'v2'), path.join(output, ratio), { recursive: true });
await fs.copyFile(HF_RUNTIME, path.join(output, 'hf-runtime.js'));
await fs.copyFile(GSAP_FILE, path.join(output, 'gsap.js'));
const assets = [];
for (const [kind, payload, dependencies] of [
  ['theme', {tokens:{colors:{text:'#17272c'},surface:{color:'#ffffff'},typography:{body:'sans-serif'}}}, []],
  ['background', {renderer:'module',entry:'module.js',parameters:{moods:[{cue:'E',tint:'#dcebf7'}]}}, ['module.js']],
]) {
  await fs.mkdir(path.join(output, kind));
  await fs.writeFile(path.join(output, kind, 'asset.json'), JSON.stringify({schema_version:2,id:kind,version:1,kind,contract_version:1,entry:'entry.json',dependencies}));
  await fs.writeFile(path.join(output, kind, 'entry.json'), JSON.stringify(payload));
  assets.push({ref:kind+'@v1',kind,vendor_path:kind,package_sha256:'fixture'});
}
await fs.copyFile(path.join(repo, 'tests/fixtures/explainer-background.js'), path.join(output, 'background/module.js'));
await fs.writeFile(path.join(output, 'appearance-lock.json'), JSON.stringify({schema_version:2,contract_version:2,resolver_version:1,assets,mode:'card',selection:{captions:false,theme:assets[0],background:assets[1],motion:{}},parameters:{theme:{},background:{},motion:{}}}));
await fs.mkdir(path.join(output,'explainer'));
for(const kind of ['theme','background'])await fs.cp(path.join(output,kind),path.join(output,'explainer',kind),{recursive:true});
const explainerLock=JSON.parse(await fs.readFile(path.join(output,'appearance-lock.json'),'utf8'));
explainerLock.mode='explainer';
explainerLock.selection.captions=true;
await fs.writeFile(path.join(output,'explainer','appearance-lock.json'),JSON.stringify(explainerLock));
await fs.writeFile(path.join(output, 'index.html'), `<!doctype html><meta charset="utf-8"><style>
:root{--hf-color-canvas:#f3f5f6;--hf-color-surface:#fff;--hf-color-text-primary:#12342d;--hf-color-text-secondary:#416563;--hf-color-accent-primary:#be4625;--hf-font-body:sans-serif}
body{margin:0;background:#f3f5f6}main{position:relative;width:100vw;height:100vh;overflow:hidden}[data-hf-layer]{position:absolute;inset:0}#background{z-index:0}#stage{z-index:1}#overlay{z-index:2}#text{z-index:3}#captions{z-index:4}iframe{border:0;width:100%;height:100%;position:absolute;inset:0}.group{position:absolute;inset:0}.media{position:absolute;inset:20%;background:#29796f;border:6px solid #dca340}.words{padding:10%;font:30px sans-serif;color:#12342d}.words p{margin:10px 0}.btitle{position:absolute;top:8%;left:10%;font:32px sans-serif}#caption{position:absolute;bottom:8%;width:100%;text-align:center;font:22px sans-serif;color:#172b3a}
</style><script src="gsap.js"></script><script src="hf-runtime.js"></script>
${['cues', 'captions', 'appearance', 'rolls', 'card-component', 'scene-binding'].map(n => '<script src="runtime/' + n + '.js"></script>').join('')}
<main data-composition-id="fixture" data-start="0" data-duration="22">
<div id="background" data-hf-layer="background"></div><div id="stage" data-hf-layer="stage"><div id="decor" class="group"></div><div id="continued-decor" class="group"></div><div id="b1" class="media"></div><div id="b2" class="media"></div><div id="b3" class="media"></div></div>
<div id="overlay" data-hf-layer="overlay"></div><div id="text" data-hf-layer="text"><div id="card" class="group"></div><div id="continued-card" class="group"></div><div id="a2" class="group words"><p id="old">Earlier conclusion</p><p id="new">Next conclusion</p></div><div id="a3" class="group words"><p id="read">Earlier conclusion</p><p id="later">Final conclusion</p></div><div id="bt1" class="btitle">Evidence 1</div><div id="bt2" class="btitle">Evidence 2</div><div id="bt3" class="btitle">Evidence 3</div></div>
<div id="captions" data-hf-layer="captions"></div></main>
<script>
const el=id=>document.getElementById(id);
window.__timelines={fixture:gsap.timeline({paused:true}).to({},{duration:22})};
window.ready=(async()=>{
 const mode=new URLSearchParams(location.search).get('mode');
 const characters=Array.from('ABCDEFGHIJKLMNOPQRSTUVW',(char,i)=>({char,start:i,end:i+.9,aligned:true}));
 window.cues=HarnessCues.from({schema_version:1,text:characters.map(c=>c.char).join(''),characters});
 window.appearance=await HarnessAppearance.load(mode==='explainer'?'explainer/':'./');HarnessAppearance.apply(document.querySelector('main'),appearance);
 if(appearance.lock.mode!==mode)throw new Error('Fixture must load the actual selected mode');
 const enabled=appearance.lock.selection.captions;if(!enabled)el('captions').remove();
 const captions=HarnessCaptions.mount(el('captions'),cues,{ratio:innerWidth<innerHeight?'9:16':'16:9',enabled});
 const background=await HarnessAppearance.mountBackground(el('background'),appearance,cues);
 for(const [id,scene] of [['card','S1'],['decor','S1'],['continued-card','S4'],['continued-decor','S4']])el(id).dataset.sceneId=scene;
 el('card').dataset.infoId='I01';el('continued-card').dataset.infoId='I04';
 window.component=await HarnessCardComponent.mount({source:(innerWidth<innerHeight?'9x16':'16x9')+'/component.html',stage:el('decor'),text:el('card'),items:[{id:'context',selector:'#ct-context',cue:'A'}]});
 window.continued=await HarnessCardComponent.mount({source:(innerWidth<innerHeight?'9x16':'16x9')+'/component.html',stage:el('continued-decor'),text:el('continued-card'),items:[{id:'context',selector:'#ct-context'}]});
 const componentRender=component.renderAt;window.activeTime=0;
 window.scenes=[
 {id:'S1',startCue:'A',endCue:'I',a:{...component,renderAt:async t=>{activeTime=t;await componentRender(t)}},b:[{startCue:'C',endCue:'E',retreat:'hide',media:el('b1'),text:el('bt1')},{startCue:'F',endCue:'G',retreat:'blur',media:el('b2'),text:el('bt2')}]},
 {id:'S2',startCue:'I',endCue:'M',a:{text:el('a2'),items:[{id:'old',element:el('old'),cue:'I'},{id:'new',element:el('new'),cue:'J'}]},b:[{startCue:'K',endCue:'M',retreat:'hide',media:el('b3'),text:el('bt3')}]},
 {id:'S3',startCue:'M',endCue:'S',continuation:{from:'S2',readItems:['old']},a:{text:el('a3'),items:[{id:'old',element:el('read')},{id:'later',element:el('later'),cue:'O'}]}},
 {id:'S4',startCue:'S',endCue:'W',continuation:{from:'S1',readItems:['context']},a:continued}
 ];
 window.rolls=HarnessRolls.mount({cues,scenes});
 window.binding=HarnessScene.bindExplainer({duration:22,background,captions,renderAt:t=>rolls.renderAt(t)});await binding.seek(0);
})();
window.frameState=f=>{const body=f.contentDocument.body.cloneNode(true);body.querySelector('#ct-context').style.removeProperty('visibility');return body.innerHTML};
window.snapshot=()=>({activeTime,groups:[component.text,component.decorations,...['a2','a3','old','new','read','later','b1','b2','b3','bt1','bt2','bt3'].map(el)].map(e=>({visibility:getComputedStyle(e).visibility,filter:getComputedStyle(e).filter})),frames:[component.text,component.decorations].map(frameState)});
</script>`);
const server = http.createServer(async (request, response) => {
  try {
    const file = path.resolve(output, decodeURIComponent(new URL(request.url, 'http://localhost').pathname).slice(1) || 'index.html');
    assert(file.startsWith(output + path.sep));
    response.setHeader('Content-Type', ({ '.js': 'application/javascript', '.json': 'application/json', '.png': 'image/png', '.svg': 'image/svg+xml', '.woff2': 'font/woff2' })[path.extname(file)] || 'text/html');
    response.end(await fs.readFile(file));
  } catch { response.writeHead(404).end(); }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
let browser;
const evidence = { scope: 'Isolated WSL Chromium, not Windows native or production acceptance', output, cases: [], errors: [] };
try {
  browser = await chromium.launch({ executablePath: CHROME_PATH, headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  page.on('pageerror', e => evidence.errors.push(e.message));
  await page.route('**/*', route => new URL(route.request().url()).hostname === '127.0.0.1' ? route.continue() : route.abort());
  for (const viewport of [{ width: 1280, height: 720 }, { width: 450, height: 800 }]) for (const mode of ['card', 'explainer']) {
    await page.setViewportSize(viewport);
    const visit = async () => { await page.goto('http://127.0.0.1:' + server.address().port + '/?mode=' + mode); await page.evaluate(() => ready); };
    const seek = t => page.evaluate(async t => {
      await __player.renderSeek(t); await window.__hfWaitForSeekCompletion?.();
      // DOM seek completion precedes painting the scaled, filtered iframe layers.
      await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
      return snapshot();
    }, t);
    await visit();
    assert.equal(await page.locator('[data-hf-layer="captions"]').count(), mode==='explainer'?1:0);
    const states = {};
    for (const t of [1.9, 2, 3, 4, 5, 5.5, 6, 8, 9, 11, 12, 14, 18]) states[t] = await seek(t);
    assert.deepEqual(await page.evaluate(() => [continued.text,continued.decorations].map(frameState)), states[8].frames, 'Actual component continuation starts at source A exit, not time zero');
    assert.equal(await page.evaluate(() => getComputedStyle(continued.items[0].element).visibility), 'visible');
    const hero = await page.screenshot({path:path.join(output,viewport.width+'-'+mode+'-continued.png')});
    const pixels = await page.evaluate(async base64 => {
      const img=new Image();img.src='data:image/png;base64,'+base64;await img.decode();
      const canvas=document.createElement('canvas');canvas.width=img.width;canvas.height=img.height;
      const ctx=canvas.getContext('2d');ctx.drawImage(img,0,0);const data=ctx.getImageData(0,0,img.width,img.height).data;
      let dark=0;for(let i=0;i<data.length;i+=4)if(data[i]<150&&data[i+1]<150&&data[i+2]<150)dark++;
      const background=el('background').querySelector('canvas').getContext('2d').getImageData(0,0,1,1).data;
      return {dark,background:Array.from(background)};
    },hero.toString('base64'));
    assert(pixels.dark>1000,'Real component and labels must paint nonblank pixels');
    assert.deepEqual(pixels.background,[220,235,247,255],'Card module background executes its cue mood');
    assert.equal(states[3].activeTime, 2, 'A timeline freezes during B');
    assert.equal(states[4].activeTime, 2, 'A resumes at its exact prior time');
    assert.equal(states[5.5].activeTime, 3);
    assert.equal(states[6].activeTime, 3);
    assert.equal(states[3].groups[0].visibility, 'hidden');
    assert.equal(states[3].groups[1].visibility, 'hidden', 'Actual component decoration retreats with A');
    assert.equal(states[5.5].groups[0].filter, 'blur(8px)');
    assert.equal(states[5.5].groups[1].filter, 'blur(8px)');
    assert.equal(states[6].groups[0].filter, 'none');
    assert.equal(states[6].groups[1].filter, 'none');
    assert.equal(states[11].groups[2].visibility, 'hidden', 'A to B without return');
    assert.equal(states[12].groups[6].visibility, 'visible', 'Read continuation item is present on entry');
    assert.equal(states[12].groups[7].visibility, 'hidden');
    assert.equal(states[14].groups[7].visibility, 'visible');
    await seek(5.5);
    const beforeRepeat = await page.evaluate(() => snapshot());
    const shot = await page.screenshot({ path: path.join(output, viewport.width + '-' + mode + '-blur.png') });
    await seek(0); await seek(5.5);
    const repeated = await page.screenshot({path:path.join(output,viewport.width+'-'+mode+'-blur-repeat.png')});
    assert.deepEqual(await page.evaluate(() => snapshot()),beforeRepeat,'Repeat seek restores identical DOM state');
    assert(shot.equals(repeated), 'Repeat seek produces identical pixels');
    await seek(1.9);
    await page.screenshot({ path: path.join(output, viewport.width + '-' + mode + '-card.png') });
    const dimensions = await page.evaluate(() => [component.text, component.decorations].map(frame => {
      const r = frame.getBoundingClientRect(), doc = frame.contentDocument;
      return { fits: r.left >= 0 && r.top >= 0 && r.right <= innerWidth + 1 && r.bottom <= innerHeight + 1,
        content: doc.body.textContent.trim().length, images: [...doc.images].every(i => i.complete && i.naturalWidth > 0) };
    }));
    assert(dimensions.every(d => d.fits && d.content > 20 && d.images));
    await visit();
    for (let t = 0; t <= 18; t += .25) {
      const actual = await seek(t);
      if (states[t]) assert.deepEqual(actual, states[t], 'Sequential and direct seek match at ' + t);
    }
    const validation = await page.evaluate(() => {
      const fails = change => { try { HarnessRolls.mount({cues,scenes:change(scenes)}); return false; } catch { return true; } };
      return [fails(s => [{...s[1],a:{...s[1].a,items:[{id:'bad',element:el('old'),cue:'L'}]}}]),
        fails(s => [{...s[2],continuation:{from:'missing',readItems:['old']}}]),
        fails(s => [{...s[0],b:[{...s[0].b[0],endCue:'B'}]}]),
        fails(s => [{...s[0],b:[s[0].b[0],{...s[0].b[1],startCue:'D'}]}])];
    });
    assert(validation.every(Boolean));
    await seek(1.95);
    await page.evaluate(() => __player.play());
    await page.waitForTimeout(220);
    await page.evaluate(() => __player.pause());
    const playback = await page.evaluate(() => ({time:activeTime,hidden:getComputedStyle(component.text).visibility}));
    assert.deepEqual(playback,{time:2,hidden:'hidden'},'Real playback crosses into B without an A reveal');
    evidence.cases.push({viewport,mode,dimensions,pixels,validation,checkedTimes:Object.keys(states)});
  }
  assert.deepEqual(evidence.errors, []);
  evidence.passed = true;
} finally {
  await browser?.close(); await new Promise(resolve => server.close(resolve));
  await fs.writeFile(path.join(output, 'evidence.json'), JSON.stringify(evidence, null, 2));
  console.log(output);
}
