// Real browser visibility and helper semantics, isolated from Work/AssetStore.
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {inspectRhythmFrame} from '../.studio/visual_probe.mjs';

const {HF_PACKAGE, CHROME_PATH} = process.env;
assert(HF_PACKAGE && CHROME_PATH, 'Set HF_PACKAGE and CHROME_PATH');
const require = createRequire(path.join(HF_PACKAGE, 'package.json'));
const {launch} = require('puppeteer-core');
const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const browser = await launch({executablePath: CHROME_PATH, headless: true,
  args: process.platform === 'linux' ? ['--no-sandbox', '--disable-dev-shm-usage'] : []});
try {
  const page = await browser.newPage();
  await page.setContent(`<style>body{margin:0}.thing{position:absolute;width:100px;height:100px;background:red}
    #a{left:0;top:0}#b{left:120px;top:0}#idle{left:240px;top:0}#noOp{left:360px;top:0}
    #aText{position:absolute;top:150px}#bText{position:absolute;top:200px}</style>
    <main data-scene-id="S01"><div data-hf-layer="stage"><div id="a" class="thing"></div>
    <div id="b" class="thing"></div><div id="idle" class="thing"></div><div id="noOp" class="thing"></div></div>
    <div data-hf-layer="text"><div id="aText"><p id="item">A reveal</p></div><p id="bText">B words</p></div></main>`);
  await page.addScriptTag({path: path.join(repo, '.studio/runtime/figures.js')});
  await page.addScriptTag({path: path.join(repo, '.studio/runtime/rolls.js')});
  await page.evaluate(async () => {
    const el = id => document.getElementById(id), cues = {find: value => value};
    window.figures = await HarnessFigures.load({assets: []}, {projectURL: 'about:blank', cues});
    figures.image(el('a')).point(.123, {duration: .04}).bounce(.3, {duration: .1, cycles: 4}).pan(1, {duration: 2, x: 40});
    figures.image(el('idle')).idle(0, {duration: 6}).talk([[0, 6]]);
    figures.image(el('noOp')).pan(1, {duration: 2, x: 0}).zoom(1, {duration: 2, scale: 1});
    window.rolls = HarnessRolls.mount({cues, scenes: [{id: 'S01', startCue: 0, endCue: 6,
      a: {text: el('aText'), items: [{id: 'I01', element: el('item'), cue: .2}]},
      b: [{startCue: 2, endCue: 4, retreat: 'hide', media: el('b'), text: el('bText')}]}]});
    window.seek = async time => {await figures.renderAt(time); await rolls.renderAt(time);};
  });
  const inspect = async time => {await page.evaluate(time => seek(time), time); return page.evaluate(inspectRhythmFrame);};
  const before = await inspect(.122), during = await inspect(.143);
  const point = values => values.find(event => event.kind === 'point');
  assert(point(during).visible);
  assert.notEqual(point(before).signature, point(during).signature, 'sub-grid point produces real state change');
  assert(!during.some(event => ['idle', 'talk'].includes(event.kind)));
  const cyclic = during.find(event => event.kind === 'bounce');
  assert.equal(cyclic.after, .3125, 'cyclic action probes a peak, not its unchanged midpoint');
  const revealed = await inspect(.201);
  assert(revealed.find(event => event.kind === 'text_reveal').visible);
  const middle = await inspect(2.001);
  assert(!middle.find(event => event.kind === 'text_reveal').visible, 'A is genuinely hidden during B');
  assert(middle.filter(event => event.kind === 'b_enter').every(event => event.visible));
  const cameraStart = await inspect(.999), cameraMiddle = await inspect(2);
  const moving = values => values.filter(event => event.kind === 'pan_start');
  assert.notEqual(moving(cameraStart)[0].signature, moving(cameraMiddle)[0].signature);
  assert.equal(moving(cameraStart).length, 1, 'zero amplitude is not an event');
  const end = (await inspect(3.001)).find(event => event.kind === 'pan_end');
  assert.equal(end.before, 2, 'camera endpoint compares its actual final approach, not a middle-process tick');
  assert.notEqual(end.signature, (await inspect(end.before)).find(event => event.kind === 'pan_end').signature);
  assert.deepEqual(await inspect(.143), during, 'backward seek preserves projected event identity and visible state');
  await page.evaluate(() => {figures.dispose(); rolls.dispose();});
  assert.deepEqual(await page.evaluate(inspectRhythmFrame), [], 'dispose removes read-only sources');
  console.log(JSON.stringify({platform: process.platform, checks: ['short-event', 'real-visibility', 'rolls',
    'idle-talk-exclusion', 'camera-boundaries', 'zero-amplitude', 'repeat-seek', 'dispose']}));
} finally {
  await browser.close();
}
