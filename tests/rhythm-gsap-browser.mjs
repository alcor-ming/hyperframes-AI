// Local browser and GSAP only; no WorkStore, Studio server or video export.
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {inspectFrame, inspectRhythmFrame} from '../.studio/visual_probe.mjs';

const {HF_PACKAGE, CHROME_PATH, GSAP_FILE} = process.env;
assert(HF_PACKAGE && CHROME_PATH && GSAP_FILE, 'Set HF_PACKAGE, CHROME_PATH, GSAP_FILE');
const {launch} = createRequire(path.join(HF_PACKAGE, 'package.json'))('puppeteer-core');
const browser = await launch({executablePath: CHROME_PATH, headless: true, args: ['--no-sandbox'],
  timeout: 10000, protocolTimeout: 10000});
try {
  const page = await browser.newPage();
  page.setDefaultTimeout(10000);
  await page.setContent(`<style>body{margin:0}.box{width:40px;height:40px;background:red;position:absolute}
    #good{top:0}#set{top:60px}#hidden{top:120px;display:none}#off{left:2000px}
    #ambient{top:180px}#idle{top:240px}#camera{top:300px}#noop{top:360px}
    #background{top:420px}#captions{top:480px}</style>
    <main data-composition-id="main" data-scene-id="S01"><div data-hf-layer="stage">
    <div data-info-id="I01"><div id="good" class="box"></div></div><div id="set" class="box"></div>
    <div id="hidden" class="box"></div><div id="off" class="box"></div>
    <div id="ambient" class="box" data-hf-ambient></div><div id="idle" class="box" data-hf-motion="idle"></div>
    <div id="yoyo" class="box" data-hf-camera style="left:400px;top:100px"></div>
    <div id="infinite" class="box" data-hf-camera style="left:400px;top:200px"></div>
    <svg width="150" height="140" style="position:absolute;left:500px;top:300px">
      <path id="draw" d="M5 10 L105 10" fill="none" stroke="black" stroke-width="4" stroke-dasharray="100" stroke-dashoffset="100"/>
      <path id="reshape" d="M5 40 L105 40 L105 100 Z" fill="red"/>
      <path id="invisible-svg" d="M5 110 L105 110 L105 130 Z" fill="none" stroke="none" pointer-events="all"/>
    </svg>
    <div id="camera" class="box" data-hf-camera></div><div id="noop" class="box"></div></div>
    <div data-hf-layer="background"><div id="background" class="box"></div></div>
    <div data-hf-layer="captions"><div id="captions" class="box"></div></div></main>`);
  await page.addScriptTag({path: GSAP_FILE});
  await page.evaluate(() => {
    const host = gsap.timeline({paused: true});
    window.__timelines = {main: host};
    const nested = gsap.timeline().to('#good', {x: 50, duration: .2}, .2);
    nested.timeScale(2);
    host.add(nested, .9); // Local .2 at scale 2 => host 1.0.
    host.set('#set', {backgroundColor: 'blue'}, 2);
    host.to('#hidden,#off,#ambient,#idle,#background,#captions', {x: 50, duration: .2}, 1);
    host.to('#noop', {x: 0, duration: .2}, 1);
    host.to({}, {duration: .2}, 1);
    host.to('#camera', {x: 100, duration: 2, ease: 'none'}, 0);
    host.to('#camera', {x: 200, duration: 2, ease: 'none'}, 2);
    host.to('#camera', {x: 100, duration: 2, ease: 'none'}, 4);
    host.to('#yoyo', {x: 100, duration: 2, ease: 'none', repeat: 1, yoyo: true}, 0);
    host.to('#infinite', {x: 100, duration: 2, repeat: -1, yoyo: true}, 0);
    host.to('#draw', {strokeDashoffset: 0, duration: .4}, 1);
    host.to('#reshape', {attr: {d: 'M5 40 L5 100 L105 100 Z'}, duration: .4}, 2);
    host.to('#invisible-svg', {attr: {d: 'M5 110 L5 130 L105 130 Z'}, duration: .4}, 2);
    window.__hfRhythmSources = [() => [{target: document.querySelector('#set'), time: 2, duration: 0, kind: 'state'}]];
  });
  const inspect = async time => {
    await page.evaluate(time => { __timelines.main.seek(time); }, time);
    return {time, ready: true, texts: [], rhythm_candidates: await page.evaluate(inspectRhythmFrame)};
  };
  let candidates = (await inspect(0)).rhythm_candidates;
  assert(candidates.some(item => item.targets.includes('I01') && Math.abs(item.time - 1) < 1e-6));
  assert(!candidates.some(item => item.targets.some(id => ['ambient', 'idle', 'background', 'captions'].includes(id))));
  assert.equal(candidates.filter(item => item.targets.includes('set')).length, 1, 'helper/GSAP deduplicated');
  // Remove the helper so the set's actual CSS paint change is independently checked.
  await page.evaluate(() => {window.__hfRhythmSources = [];});
  candidates = (await inspect(0)).rhythm_candidates;
  const times = new Set([0, 6]);
  for (const event of candidates) {
    times.add(event.before ?? Math.max(0, event.time - .001));
    times.add(event.after ?? event.time + (event.duration / 2 || .001));
  }
  const samples = [];
  for (const time of [...times].sort((a, b) => a - b)) samples.push(await inspect(time));
  const python = spawnSync('python3', ['-c', `import json,sys
sys.path.insert(0,'.studio')
from visual_diagnostics import rhythm_diagnostics
print(json.dumps(rhythm_diagnostics(json.load(sys.stdin),[dict(id='S01',start=0,duration=6)])))`],
  {input: JSON.stringify(samples), encoding: 'utf8', timeout: 10000});
  assert.equal(python.status, 0, python.stderr);
  const report = JSON.parse(python.stdout);
  assert(report.events.some(event => event.kind === 'tween' && event.targets.includes('good')));
  assert(report.events.some(event => event.kind === 'set' && event.targets.includes('set')));
  assert(!report.events.some(event => event.targets?.some(id => ['hidden', 'off', 'noop'].includes(id))));
  const camera = report.events.filter(event => event.targets?.includes('camera'));
  assert(!camera.some(event => event.time === 2), 'continuous same-direction camera has no intermediate event');
  assert(camera.some(event => event.time === 4), 'camera reversal is an event');
  assert(camera.some(event => event.time === 6), 'camera endpoint is observed');
  assert(report.events.some(event => event.targets?.includes('yoyo') && event.kind === 'camera_turn'));
  assert(!report.events.some(event => event.targets?.includes('infinite')));
  assert(report.unverified.some(item => item.reason === 'unbounded_repeated_motion'));
  assert(report.events.some(event => event.targets?.includes('draw')), 'individual SVG stroked path draw is visible');
  assert(report.events.some(event => event.targets?.includes('reshape')), 'same-bounds SVG d mutation is visible');
  assert(!report.events.some(event => event.targets?.includes('invisible-svg')), 'unpainted SVG is not a visible event');
  await page.evaluate(() => {
    for (let i = 0; i < 2; i++) {
      const frame = document.createElement('iframe');
      frame.srcdoc = '<div data-hf-layer="stage"><div id="same" style="width:20px;height:20px;background:red"></div></div>';
      document.body.appendChild(frame);
    }
  });
  const frameCandidates = [];
  for (const frame of page.mainFrame().childFrames()) {
    await frame.waitForSelector('#same');
    await frame.evaluate(() => {
      window.__hfRhythmSources = [() => [{target: document.querySelector('#same'), time: 1, duration: .2, kind: 'point'}]];
    });
    frameCandidates.push((await frame.evaluate(inspectRhythmFrame))[0]);
  }
  assert.equal(frameCandidates.length, 2);
  assert.notEqual(frameCandidates[0].id, frameCandidates[1].id, 'identical srcdoc instances retain separate events');
  assert.notEqual(frameCandidates[0].target_node, frameCandidates[1].target_node, 'camera identity is frame-scoped');
  await page.setRequestInterception(true);
  page.on('request', request => {
    const svg = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" data-icon="fake:line@1.0.0"><path d="M0 0L24 24"/></svg>';
    void request.respond({status: 200, contentType: request.url().endsWith('.svg') ? 'image/svg+xml' : 'text/html',
      body: request.url().endsWith('.svg') ? svg : `<div data-hf-layer="stage"><canvas width="24" height="24"></canvas>
        <img id="icon-file" src="/icon.svg"><span data-hf-schematic>${svg}</span>
        <span data-card-svg-slot>${svg}</span><span style="opacity:0">${svg}</span></div>`});
  });
  await page.goto('http://localhost/isolated-fixture', {waitUntil: 'load'});
  const frame = await page.evaluate(inspectFrame, [], 0);
  assert.equal(frame.icons.length, 3, 'external SVG, schematic and slot observed; transparent SVG excluded');
  assert(frame.icons.some(icon => icon.target === '#icon-file' && icon.svg.includes('data-icon')));
  assert(frame.icons.some(icon => icon.schematic));
  assert(frame.icons.some(icon => icon.card_slot));
  assert.equal(frame.motion_unverified[0].reason, 'media_canvas_motion_unverified');
  console.log(JSON.stringify({checks: ['nested-scaled-timeline', 'set-paint', 'target-ancestry', 'helper-dedupe',
    'hidden-offscreen-noop', 'ambient-role-layer-exclusion', 'camera-continuation-and-reversal',
    'svg-file-provenance', 'schematic-and-slot-markers', 'canvas-unverified', 'svg-draw-and-geometry',
    'same-source-frame-identity'], events: report.events.length}));
} finally { await browser.close(); }
