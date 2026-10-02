// Isolated real-browser checks; screenshots only, no video export.
import assert from 'node:assert/strict';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {inspectCarry, layerPixels} from '../.studio/visual_probe.mjs';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const {chromium} = createRequire(path.join(root, '.studio/remotion/package.json'))('playwright-core');
const browser = await chromium.launch({executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome', headless: true, args: ['--no-sandbox']});
try {
  const page = await browser.newPage({viewport: {width: 640, height: 360}});
  await page.setContent(`<style>body{margin:0}main{position:relative;width:640px;height:360px}[data-hf-layer]{position:absolute;inset:0}#a,#b,#bt{position:absolute;left:80px;top:80px;width:160px;height:100px;background:#456}#b{background:#fa0}#ip{width:20px;height:20px;background:red}#carry{width:40px;height:40px;background:black}</style><main data-width="640" data-height="360"><div data-hf-layer="background" id="bg"></div><div data-hf-layer="stage"><div id="b"></div><div id="ip" data-hf-motion="idle"></div><div id="carry" data-hf-carry="node"></div></div><div data-hf-layer="text"><div id="a"><p id="item">A text</p></div><div id="bt">B text</div></div><div data-hf-layer="captions" id="captions">字幕</div></main>`);
  await page.addScriptTag({path: path.join(root, '.studio/runtime/rolls.js')});
  const result = await page.evaluate(async () => {
    const el = id => document.getElementById(id), cues = {find: value => value};
    let activeTime;
    const make = (ranges, options = {}) => HarnessRolls.mount({cues, ...options, scenes: [{id: 'S01', startCue: 0, endCue: 6,
      a: {text: el('a'), items: [{id: 'first', cue: 0, element: el('item')}], renderAt: t => {activeTime = t;}},
      b: ranges.map(range => ({startCue: 2, endCue: 4, retreat: 'hide', media: el('b'), text: el('bt'), ...range}))}]});
    const state = () => ['a', 'b', 'bt'].map(id => {const s = getComputedStyle(el(id)); return {alpha: +s.opacity, visibility: s.visibility, filter: s.filter};});
    const rolls = make([{}]);
    await rolls.renderAt(2); const enter = state(), pause1 = activeTime;
    await rolls.renderAt(3.5); const middle = state(), pause2 = activeTime;
    await rolls.renderAt(4); const back = state();
    await rolls.renderAt(4.4); const end = state();
    await rolls.renderAt(2.1); const direct = state();
    for (let t = 0; t <= 2.1; t += .05) await rolls.renderAt(t);
    await rolls.renderAt(2.1); const forward = state();
    await rolls.renderAt(5); await rolls.renderAt(2.1); const reverse = state();
    const events = [...__hfRhythmSources].flatMap(read => read()).filter(e => ['a', 'b', 'bt'].includes(e.target.id)).map(e => ({target: e.target.id, time: e.time, kind: e.kind}));
    rolls.dispose();
    const cut = make([{handoff: 'cut'}]); await cut.renderAt(2); const hard = state(); cut.dispose();
    const reduced = make([{}], {reducedMotion: true}); await reduced.renderAt(2); const less = state(); reduced.dispose();
    el('a').style.filter = 'none';
    const blur = make([{retreat: 'blur'}]); await blur.renderAt(3); const blurred = state()[0].filter;
    blur.dispose(); const restoredFilter = el('a').style.filter;
    const short = make([{startCue: .01, endCue: .09}]);
    await short.renderAt(.01); const edge = state();
    const shortEvents = [...__hfRhythmSources].flatMap(read => read()).map(e => e.time); short.dispose();
    const animation = el('b').animate([{opacity: 0}, {opacity: 1}], {duration: 1000});
    let conflict = false; try { make([{}]); } catch (error) { conflict = error.message.includes('ownership'); } animation.cancel();
    return {enter, middle, back, end, pause1, pause2, direct, forward, reverse, events, hard, less, blurred, restoredFilter, edge, shortEvents, conflict, ownersCleared: !__hfRollOwners.has(el('a'))};
  });
  assert.equal(result.enter[1].alpha, 1); assert.equal(result.enter[0].alpha, 1); assert.equal(result.enter[2].alpha, 0);
  assert.equal(result.middle[0].visibility, 'hidden'); assert.equal(result.middle[2].alpha, 1);
  assert.equal(result.back[0].alpha, 1); assert.equal(result.back[2].alpha, 0); assert.equal(result.back[1].alpha, 1);
  assert.equal(result.end[1].visibility, 'hidden'); assert.equal(result.pause1, result.pause2);
  assert.deepEqual(result.direct, result.forward); assert.deepEqual(result.direct, result.reverse);
  assert.equal(result.blurred, 'blur(8px)'); assert.equal(result.restoredFilter, 'none');
  assert.equal(new Set(result.events.filter(e => e.time < 3).map(e => e.time)).size, 3);
  assert.deepEqual(result.hard, result.less); assert.equal(result.hard[0].visibility, 'hidden'); assert.equal(result.hard[2].alpha, 1);
  assert.equal(result.edge[1].alpha, 1); assert(result.shortEvents.every(t => t >= 0 && t <= .09)); assert(result.conflict && result.ownersCleared);
  const screenshot = () => page.screenshot({type: 'png'});
  const before = await layerPixels(page, page.mainFrame(), screenshot);
  await page.evaluate(() => {
    document.getElementById('bg').style.background = 'red';
    document.getElementById('captions').textContent = '不断推进的字幕';
    document.getElementById('ip').style.transform = 'translate(140px,80px)';
  });
  assert.deepEqual(await layerPixels(page, page.mainFrame(), screenshot), before, 'ambient/IP/background/captions cannot hide a frozen stage');
  assert.equal(await page.evaluate(() => getComputedStyle(document.getElementById('ip')).visibility), 'visible', 'mask restored');
  const first = await page.evaluate(inspectCarry);
  await page.evaluate(() => {document.getElementById('carry').style.transform = 'translateX(40px)';});
  const second = await page.evaluate(inspectCarry);
  assert.equal(second[0].box[0] - first[0].box[0], 40);
  assert.notDeepEqual(await layerPixels(page, page.mainFrame(), screenshot), before, 'real subject movement changes pixels');
  console.log('v3.7 browser: stagger, cut/reduced, seek, pause, ownership, layer pixels, carry passed');
} finally {await browser.close();}
