// A: standalone scene; B: actual Studio DOM; C: actual Studio integration. No video export.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import http from 'node:http';
import {spawnSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const require = createRequire(path.join(repo, '.studio/remotion/package.json'));
const {build} = require('esbuild');
const {chromium} = require('playwright-core');
const {HF_PACKAGE, CHROME_PATH, GSAP_FILE, FONT_FILE} = process.env;
assert(HF_PACKAGE && CHROME_PATH && GSAP_FILE && FONT_FILE, 'Set local pinned HF_PACKAGE, CHROME_PATH, GSAP_FILE, FONT_FILE');
const output = await fs.mkdtemp(path.join(os.tmpdir(), 'hf-remotion-init-'));
const evidence = {platform: process.platform, hostVersion: JSON.parse(await fs.readFile(path.join(HF_PACKAGE, 'package.json'))).version,
  nativeWindows: process.platform === 'win32', audioVerified: false, videoExported: false, output, layers: {}};
assert.equal(evidence.hostVersion, JSON.parse(await fs.readFile(path.join(repo, 'windows-runtime.lock.json'))).versions.hyperframes);
const cli = path.join(HF_PACKAGE, 'dist/cli.js');
const env = {...process.env, DO_NOT_TRACK: '1', HYPERFRAMES_NO_TELEMETRY: '1', XDG_STATE_HOME: path.join(output, 'state')};
const servers = [];
let browser, context, server;

const probe = `window.domProbe=()=>{const el=document.querySelector('#stage');return {
  connected:el.isConnected,document:el.ownerDocument===document,view:el.ownerDocument.defaultView===window,
  currentRealm:el instanceof HTMLElement,ownerRealm:el instanceof el.ownerDocument.defaultView.HTMLElement,
  parentRealm:el instanceof parent.HTMLElement,newRealm:document.createElement('div') instanceof HTMLElement};};`;
const entry = `import React from 'react';
import {useCurrentFrame} from 'remotion';
import {mountRemotion} from './preview.jsx';
function Shot(){const f=useCurrentFrame();return <div style={{width:640,height:360,background:'#f3f4f5',fontFamily:'FixtureFont'}}>
<div id="moving" style={{width:90,height:90,background:'#168c62',transform:'translateX('+f*2+'px)'}}/>
<img src="pixel.png" width="40" height="40"/><output id="frame">{f}</output></div>;}
function Broken(){throw new Error('fixture component failure');}
window.mountFixture=(options={})=>{window.fixtureBinding?.dispose();window.releaseAssets=null;
 const image=new Image();image.src='pixel.png';
 const font=new FontFace('FixtureFont','url(font.ttf)');document.fonts.add(font);
 window.assetsReady=Promise.all([image.decode(),font.load()]);
 const ready=Promise.all([window.assetsReady,new Promise(r=>window.releaseAssets=r)]);
 window.fixtureBinding=mountRemotion({container:document.querySelector('#stage'),component:Shot,
  fps:30,durationInFrames:180,width:640,height:360,ready,...options});
 window.fixtureReady=window.fixtureBinding.ready;window.fixtureReady.catch(()=>{});
 return true;};
window.Broken=Broken;
const boot=()=>{try{window.mountFixture(window.initialFailure?{component:null}:{});}catch(error){window.bootFailure=error.message;}};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});
else boot();`;

async function fixture(layer) {
  const dir = path.join(output, layer);
  await fs.mkdir(dir);
  await fs.copyFile(GSAP_FILE, path.join(dir, 'gsap.min.js'));
  await fs.copyFile(path.join(path.dirname(GSAP_FILE), 'MotionPathPlugin.min.js'), path.join(dir, 'MotionPathPlugin.min.js'));
  await fs.copyFile(path.join(repo, '.studio/runtime/scene-binding.js'), path.join(dir, 'scene-binding.js'));
  if (layer !== 'B') {
    await fs.copyFile(FONT_FILE, path.join(dir, 'font.ttf'));
    await fs.writeFile(path.join(dir, 'pixel.png'), Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aN1sAAAAASUVORK5CYII=', 'base64'));
    await build({stdin: {contents: entry, resolveDir: path.join(repo, '.studio/remotion'), loader: 'jsx'},
      outfile: path.join(dir, 'preview.js'), bundle: true, format: 'iife', define: {'process.env.NODE_ENV': '"production"'}});
  }
  if (layer === 'A') await fs.copyFile(path.join(HF_PACKAGE, 'dist/hyperframe.runtime.iife.js'), path.join(dir, 'runtime.js'));
  await fs.writeFile(path.join(dir, 'index.html'), `<!doctype html><html><head><meta charset="utf-8">
<style>body{margin:0}#stage{width:640px;height:360px}</style>
<script src="gsap.min.js"></script><script src="MotionPathPlugin.min.js"></script><script src="scene-binding.js"></script>
${layer === 'A' ? '<script src="runtime.js"></script>' : ''}</head><body>
<main data-hf-id="fixture-root" data-composition-id="init-fixture" data-start="0" data-duration="6" data-width="640" data-height="360">
<div data-hf-id="fixture-stage" id="stage" data-start="0" data-duration="6" data-track-index="0"></div></main>
<script>${probe}window.__timelines={'init-fixture':gsap.timeline({paused:true}).to({},{duration:6})};</script>
${layer === 'B' ? '' : '<script src="preview.js"></script>'}</body></html>`);
  return dir;
}

function run(dir, args) {
  const result = spawnSync(process.execPath, [cli, 'preview', dir, ...args], {cwd: dir, env, encoding: 'utf8', timeout: 90000});
  assert.equal(result.status, 0, result.stderr || result.stdout);
  return JSON.parse(result.stdout).result;
}
async function open(layer) {
  const dir = await fixture(layer);
  let url;
  if (layer === 'A') {
    server = http.createServer(async (req, res) => {
      try {
        const file = path.resolve(dir, '.' + new URL(req.url, 'http://localhost').pathname.replace(/\/$/, '/index.html'));
        if (!file.startsWith(dir + path.sep)) return res.writeHead(403).end();
        res.setHeader('Content-Type', file.endsWith('.js') ? 'text/javascript' : file.endsWith('.html') ? 'text/html' : 'application/octet-stream');
        res.end(await fs.readFile(file));
      } catch { res.writeHead(404).end(); }
    });
    await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
    url = `http://127.0.0.1:${server.address().port}/`;
  } else {
    const record = run(dir, ['--background', '--json', '--no-open']);
    servers.push({dir, port: record.port});
    assert.equal(path.resolve(record.projectDir), dir);
    url = record.studioUrl;
  }
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.stack));
  evidence.layers[layer] = {passed: false, errors};
  await page.goto(url);
  const frame = layer === 'A' ? page.mainFrame() : await studioFrame(page);
  return {page, frame, url};
}
async function studioFrame(page) {
  const iframe = page.locator('hyperframes-player').locator('iframe');
  await iframe.waitFor();
  return (await iframe.elementHandle()).contentFrame();
}
async function ready(frame) {
  await frame.waitForFunction(() => window.fixtureBinding && window.__player);
  await frame.evaluate(async () => {await window.assetsReady; window.releaseAssets(); await window.fixtureReady;});
}
async function visiblePixels(page, layer) {
  const shot = await page.screenshot({path: path.join(output, `${layer}.png`)});
  const green = await page.evaluate(async base64 => {
    const img = new Image(); img.src = 'data:image/png;base64,' + base64; await img.decode();
    const canvas = document.createElement('canvas'); canvas.width = img.width; canvas.height = img.height;
    const ctx = canvas.getContext('2d'); ctx.drawImage(img, 0, 0);
    const pixels = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
    let count = 0;
    for (let i = 0; i < pixels.length; i += 4) if (pixels[i] < 50 && pixels[i + 1] > 110 && pixels[i + 2] > 70 && pixels[i + 1] > pixels[i + 2]) count++;
    return count;
  }, shot.toString('base64'));
  assert(green > 100, `${layer}: visible scene pixels`);
  return green;
}
async function seek(page, frame, layer, time) {
  if (layer === 'A') await frame.evaluate(t => window.__player.renderSeek(t), time);
  else await page.locator('hyperframes-player').evaluate((p, t) => p.seek(t), time);
  const expected = Math.min(179, Math.floor(time * 30 + 1e-7));
  await frame.waitForFunction(f => document.querySelector('#frame')?.textContent === String(f), expected);
  return frame.locator('#moving').getAttribute('style');
}
async function failures(page, frame) {
  await page.waitForFunction(() => document.querySelector('hyperframes-player').ready);
  const invalid = await frame.evaluate(() => {
    const foreign = parent.document.createElement('div'); parent.document.body.appendChild(foreign);
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); document.body.appendChild(svg);
    const inputs = [null, {}, {nodeType: 1, namespaceURI: 'http://www.w3.org/1999/xhtml', ownerDocument: document},
      document.createElement('div'), foreign, svg];
    const results = inputs.map(container => {try {window.mountFixture({container}); return 'accepted';} catch (e) {return e.message;}});
    foreign.remove(); svg.remove();
    for (const options of [{component: null}, {width: 0}, {height: 1.5}, {durationInFrames: -1}, {fps: NaN}, {fps: Number.MIN_VALUE}, {start: -1}]) {
      try {window.mountFixture(options); results.push('accepted');} catch (e) {results.push(e.message);}
    }
    return results;
  });
  assert(invalid.slice(0, 6).every(message => message.includes('container')));
  assert(invalid[6].includes('component'));
  assert(invalid.slice(7).every(message => message.includes('dimensions')));
  const overlay = page.getByTestId('composition-preview-error');
  await overlay.waitFor();
  assert((await overlay.textContent()).includes('dimensions'));

  // Explicit parent-created/adopted HTML reproduces the same valid cross-realm input deterministically.
  await page.reload(); frame = await studioFrame(page); await ready(frame);
  const realm = await frame.evaluate(() => {
    const node = parent.document.createElement('div'); node.id = 'stage';
    window.fixtureBinding.dispose(); document.querySelector('#stage').replaceWith(node);
    window.mountFixture(); return {current: node instanceof HTMLElement, parent: node instanceof parent.HTMLElement};
  });
  assert.deepEqual(realm, {current: false, parent: true});
  await ready(frame); await seek(page, frame, 'C', 2);
  await page.locator('hyperframes-player').evaluate(p => {
    p.oldStage = p.iframeElement.contentDocument.querySelector('#stage');
    const url = new URL(p.getAttribute('src'), location.href); url.searchParams.set('rc1_reload', '1');
    p.setAttribute('src', url.href);
  });
  await frame.waitForURL(/rc1_reload=1/);
  await ready(frame); await seek(page, frame, 'C', 1);
  assert.equal(await page.locator('hyperframes-player').evaluate(p => {
    const children = p.oldStage.childElementCount; delete p.oldStage; return children;
  }), 0, 'Same-host navigation must unmount the old React root');

  const rejected = [];
  for (const kind of ['image', 'component']) {
    await page.reload(); frame = await studioFrame(page); await ready(frame);
    rejected.push(await frame.evaluate(async kind => {
      const options = kind === 'component' ? {component: window.Broken} : {ready: (async () => {
        const image = new Image(); image.src = 'missing-image.png';
        try {await image.decode();} catch {throw new Error('fixture missing image');}
      })()};
      try {window.mountFixture(options); await window.fixtureReady; return 'accepted';} catch (e) {return e.message;}
    }, kind));
    await overlay.waitFor();
    assert((await overlay.textContent()).includes(kind === 'image' ? 'fixture missing image' : 'fixture component failure'));
    await frame.evaluate(() => window.mountFixture());
    await ready(frame); await seek(page, frame, 'C', 2);
    await overlay.waitFor({state: 'hidden'});
  }
  assert(rejected.every(message => message.startsWith('fixture ')));

  await page.reload(); frame = await studioFrame(page); await ready(frame);
  await frame.evaluate(async () => {
    try {window.mountFixture({component: null});} catch {}
    const other = document.createElement('div'); document.body.appendChild(other);
    window.mountFixture({container: other});
    window.releaseAssets(); await window.fixtureReady;
  });
  await overlay.waitFor();
  assert((await overlay.textContent()).includes('component'), 'Another instance cannot clear a failed target');
  await frame.evaluate(() => window.mountFixture());
  await ready(frame); await seek(page, frame, 'C', 1);
  await overlay.waitFor({state: 'hidden'});

  await page.reload(); frame = await studioFrame(page); await ready(frame);
  await frame.evaluate(async () => {
    let reject;
    window.mountFixture({ready: new Promise((_, r) => {reject = r;})});
    const old = window.fixtureBinding;
    window.mountFixture();
    reject(new Error('disposed resource failure'));
    await old.ready.catch(() => {});
    window.releaseAssets(); await window.fixtureReady;
  });
  await seek(page, frame, 'C', 2);
  assert.equal(await overlay.count(), 0, 'Disposed instance must not report errors into the new mount');

  // Fail before host readiness: later load/ready must not erase the specific error.
  await page.addInitScript(() => {window.initialFailure = true;});
  await page.reload(); frame = await studioFrame(page);
  await page.waitForFunction(() => document.querySelector('hyperframes-player').ready);
  await frame.waitForFunction(() => window.bootFailure);
  await overlay.waitFor();
  assert((await overlay.textContent()).includes('Remotion component must be a function'));
  return {invalid, realm, rejected, instanceErrorsIsolated: true, disposedRejectionIgnored: true, initializationErrorVisible: true};
}
try {
  browser = await chromium.launch({executablePath: CHROME_PATH, headless: true, args: process.platform === 'linux' ? ['--no-sandbox'] : []});
  context = await browser.newContext();
  // Block accidental external media/telemetry; fixtures are self-contained.
  await context.route('**/*', route => {
    const u = new URL(route.request().url());
    return /^https?:$/.test(u.protocol) && !['127.0.0.1', 'localhost', '[::1]'].includes(u.hostname) ? route.abort() : route.continue();
  });
  const b = await open('B');
  const probes = [];
  for (let i = 0; i < 3; i++) {
    const frame = await studioFrame(b.page);
    await frame.waitForFunction(() => window.domProbe && window.__player);
    const value = await frame.evaluate(() => window.domProbe());
    assert(value.connected && value.document && value.view && value.newRealm);
    probes.push(value);
    if (i < 2) await b.page.reload();
  }
  evidence.layers.B = {...evidence.layers.B, passed: true, probes};
  await b.page.close();
  for (const layer of ['A', 'C']) {
    const {page, frame} = await open(layer);
    await frame.waitForFunction(() => window.releaseAssets && window.__player);
    assert.equal(await frame.locator('#stage').getAttribute('data-remotion-frame'), null);
    await ready(frame);
    assert.equal(await frame.evaluate(() => document.fonts.check('16px FixtureFont') && document.querySelector('#stage img').naturalWidth > 0), true);
    const states = [];
    for (const time of [3, 0, 1.5, 3, 6]) states.push(await seek(page, frame, layer, time));
    assert.equal(states[0], states[3]);
    await seek(page, frame, layer, 0);
    if (layer === 'C') await page.getByRole('button', {name: 'Play', exact: true}).click();
    else await frame.evaluate(() => window.__player.play());
    await frame.waitForFunction(() => Number(document.querySelector('#frame').textContent) > 5);
    if (layer === 'C') await page.getByRole('button', {name: 'Pause', exact: true}).click();
    else await frame.evaluate(() => window.__player.pause());
    const paused = await frame.locator('#frame').textContent();
    await page.waitForTimeout(150);
    assert.equal(await frame.locator('#frame').textContent(), paused);
    const greenPixels = await visiblePixels(page, layer);
    await frame.evaluate(() => {window.fixtureBinding.dispose(); window.fixtureBinding.dispose();});
    assert.equal(await frame.locator('#frame').count(), 0);
    await frame.evaluate(() => window.mountFixture());
    await ready(frame);
    await seek(page, frame, layer, 3);
    assert.deepEqual(evidence.layers[layer].errors, []);
    evidence.layers[layer] = {...evidence.layers[layer], states, greenPixels, remounted: true};
    if (layer === 'C') evidence.layers.C.failures = await failures(page, frame);
    evidence.layers[layer].passed = true;
    await page.close();
  }
} catch (error) {
  evidence.failure = error.stack;
  evidence.frames = await Promise.all(context.pages().flatMap(p => p.frames()).map(async f => ({url: f.url(),
    state: await f.evaluate(() => ({body: !!document.body, html: document.documentElement?.outerHTML.slice(-2500),
      ready: document.readyState, probe: window.domProbe?.(), binding: !!window.fixtureBinding})).catch(e => e.message)})));
  throw error;
} finally {
  await browser?.close();
  if (server) await new Promise(resolve => server.close(resolve));
  for (const {dir, port} of servers) run(dir, ['--stop', '--json', '--port', String(port)]);
  await fs.writeFile(path.join(output, 'evidence.json'), JSON.stringify(evidence, null, 2));
  console.log(output);
}
