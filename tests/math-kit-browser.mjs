// CHROME_PATH=/usr/bin/google-chrome node tests/math-kit-browser.mjs
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {inspectRhythmFrame} from '../.studio/visual_probe.mjs';
const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const {chromium} = createRequire(path.join(repo, '.studio/remotion/package.json'))('playwright-core');
const font = await fs.readFile('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf');
const output = await fs.mkdtemp(path.join(os.tmpdir(), 'hf-math-kit-'));
const browser = await chromium.launch({executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome', headless: true, args: ['--no-sandbox']});
const fixture = {
  font: {path: 'font.ttf', sha256: '0'.repeat(64), characters: '1234567890x=+ABCtotalparts'},
  items: [
    {id: 'f', kind: 'formula', box: [60, 60, 900, 60], slots: ['x', '+', '', '=', '6']},
    {id: 'u', kind: 'unknown', box: [60, 160, 140, 140], label: 'x'},
    {id: 'b', kind: 'units', box: [260, 160, 600, 140], count: 3, value: '2', label: '3 parts'},
    {id: 's', kind: 'segment', box: [60, 350, 600, 120], count: 3, value: '2', label: 'total 6'},
    {id: 'a', kind: 'area', box: [760, 340, 180, 220], value: '9', label: 'A'},
    {id: 'n', kind: 'number-line', box: [60, 600, 700, 100], min: 0, max: 3, step: 1, labels: ['0', '1', '2', '3']},
    {id: 's1', kind: 'strike', box: [60, 750, 160, 60], label: 'ABC', negate: false},
    {id: 's2', kind: 'strike', box: [300, 750, 160, 60], label: 'ABC', negate: true},
    {id: 'e', kind: 'edge', box: [60, 850, 600, 150], from: [60, 900], to: [450, 960], length: 150, label: '3', duration: 1},
    {id: 'eq', kind: 'equals', box: [850, 750, 70, 60], to: [750, 850], duration: 1},
  ],
};
const intent = {units: fixture.items.map(({id}) => ({id})), symbols: [], invariants: [], zero_basics: [], cues: [
  {cue: 1, reveal: fixture.items.map(item => item.id), keep: [], remove: []},
  {cue: 3, reveal: [], keep: ['f'], remove: ['s1']},
  {cue: 4, reveal: ['s1'], keep: [], remove: []},
]};
async function setup(page, html) {
  await page.route('**/*', route => route.request().url() === 'http://math.invalid/font.ttf'
    ? route.fulfill({status: 200, contentType: 'font/ttf', body: font}) : route.abort());
  await page.setContent('<base href="http://math.invalid/"><style>body{margin:0;background:#eef2f0}main{position:relative;width:1920px;height:1080px;transform:scale(.6666667);transform-origin:0 0}#stage,#text,#S2{position:absolute;inset:0}</style>' + html);
  await page.addStyleTag({path: path.join(repo, '.studio/runtime/math-kit.css')});
  for (const script of ['math-kit', 'cues', 'rolls', 'scene-binding']) await page.addScriptTag({path: path.join(repo, '.studio/runtime', script + '.js')});
}
try {
  const page = await browser.newPage({viewport: {width: 1280, height: 720}});
  await setup(page, '<main><div id="stage" data-hf-layer="stage"></div><div id="text" data-hf-layer="text"></div></main>');
  await page.evaluate(({math, intent}) => {
    window.math = math; window.intent = intent;
    window.mount = (extra = {}) => HarnessMathKit.mount({stage: document.querySelector('#stage'), text: document.querySelector('#text'), math, intent,
      cues: {find: Number}, ratio: '16:9', start: 0, end: 6, fontURL: 'http://math.invalid/font.ttf', ...extra});
    window.snapshot = () => document.querySelector('main').innerHTML;
  }, {math: fixture, intent});
  for (const ratio of ['16:9', '9:16']) {
    await page.setViewportSize(ratio === '16:9' ? {width: 1280, height: 720} : {width: 450, height: 800});
    const result = await page.evaluate(async ratio => {
      Object.assign(document.querySelector('main').style, ratio === '16:9' ? {width: '1920px', height: '1080px', transform: 'scale(.6666667)'} : {width: '1080px', height: '1920px', transform: 'scale(.4166667)'});
      window.instance = await mount({ratio});
      instance.renderAt(2.5); const direct = snapshot();
      for (let t = 0; t < 2.5; t += .05) instance.renderAt(t);
      instance.renderAt(2.5); const sequential = snapshot();
      instance.renderAt(5); instance.renderAt(2.5); const backward = snapshot();
      const states = [];
      for (const t of [.5, 1.125, 2, 3.5, 4.5, 6]) { instance.renderAt(t); states.push(instance.getState()); }
      instance.renderAt(2.5);
      return {equal: direct === sequential && direct === backward, states, layers: !instance.decorations.textContent.trim() && instance.items.every(item => instance.text.contains(item.element)), events: instance.rhythm().map(({time, kind}) => ({time, kind}))};
    }, ratio);
    assert(result.equal && result.layers);
    assert.equal(result.states[0].items[0].opacity, 0);
    assert.equal(result.states[1].items[0].opacity, .5);
    assert.equal(result.states[2].items[0].opacity, 1);
    assert.equal(result.states[3].items.find(item => item.id === 's1').opacity, 0);
    assert.equal(result.states[4].items.find(item => item.id === 's1').opacity, 1);
    assert.equal(result.states[5].items[0].opacity, 0);
    assert.equal(result.events.length, 22);
    const candidates = await page.evaluate(inspectRhythmFrame);
    for (const item of fixture.items) {
      const layers = candidates.filter(candidate => candidate.targets.includes(item.id) && candidate.time === 1).map(candidate => candidate.layer).sort();
      assert.deepEqual(layers, ['formula', 'equals'].includes(item.kind) ? ['text'] : ['stage', 'text'], item.id);
    }
    assert.deepEqual(candidates.filter(candidate => candidate.kind === 'math_remove').map(candidate => candidate.layer).sort(), ['stage', 'text']);
    const cdp = await page.context().newCDPSession(page);
    await cdp.send('DOM.enable'); await cdp.send('CSS.enable');
    const {root} = await cdp.send('DOM.getDocument');
    const {nodeIds} = await cdp.send('DOM.querySelectorAll', {nodeId: root.nodeId, selector: '[data-hf-math-label],[data-hf-math-glyphs]'});
    let glyphs = 0;
    for (const nodeId of nodeIds) {
      const {fonts} = await cdp.send('CSS.getPlatformFontsForNode', {nodeId});
      assert(fonts.every(font => font.isCustomFont), JSON.stringify(fonts));
      glyphs += fonts.reduce((sum, font) => sum + font.glyphCount, 0);
    }
    assert(glyphs > 30); await cdp.detach();
    await page.screenshot({path: path.join(output, ratio.replace(':', 'x') + '.png')});
    await page.evaluate(() => instance.dispose());
  }
  const errors = await page.evaluate(async () => {
    const fail = async extra => { try { const a = await mount(extra); a.dispose(); return ''; } catch (e) { return e.message; } };
    const long = structuredClone(math); long.items[0].slots[0] = 'x'.repeat(100);
    const before = document.fonts.size;
    const badFont = await fail({fontURL: 'http://math.invalid/missing.ttf'});
    const remoteFont = await fail({fontURL: 'https://external.invalid/font.ttf'});
    const overflow = await fail({math: long});
    const shortArea = structuredClone(math); shortArea.items.find(item => item.kind === 'area').box[3] = 20;
    const invalidArea = await fail({math: shortArea});
    const narrowUnits = structuredClone(math); narrowUnits.items.find(item => item.kind === 'units').count = 100;
    const invalidUnits = await fail({math: narrowUnits});
    const a = await mount();
    a.retime(cue => Number(cue) + .2); a.renderAt(1.25);
    const shifted = a.getState().items[0].opacity;
    const raw = a.rhythm()[0].time; a.dispose();
    return {badFont, remoteFont, overflow, invalidArea, invalidUnits, shifted, raw, cleanup: document.querySelectorAll('.hf-math-kit').length, sources: __hfRhythmSources.size, fonts: document.fonts.size - before};
  });
  assert(errors.badFont); assert.match(errors.overflow, /math_label_overflow/);
  assert.equal(errors.remoteFont, 'math_font_requires_local_source');
  assert.match(errors.invalidArea, /invalid_math_geometry/); assert.match(errors.invalidUnits, /invalid_math_geometry/);
  assert(Math.abs(errors.shifted - .2) < .00001); assert.equal(errors.raw, 1);
  assert.equal(errors.cleanup, 0); assert.equal(errors.sources, 0); assert.equal(errors.fonts, 0);
  const geometry = await page.evaluate(async () => {
    const a = await mount();
    const group = (id, graphics = false) => (graphics ? a.decorations : a.text).querySelector(`[data-hf-math-id="${id}"]`);
    const formula = [...group('f').children].map(el => [el.textContent, el.style.left, el.style.width]);
    const unknown = group('u', true).firstElementChild;
    const area = group('a', true).firstElementChild;
    const units = group('b', true).children.length, segments = group('s', true).children.length;
    const ticks = group('n', true).querySelectorAll('.hf-math-tick').length;
    a.renderAt(1.5);
    const edgeMid = group('e', true).lastElementChild.style.transform;
    const equalsMid = group('eq').firstElementChild.style.transform;
    a.renderAt(2.5);
    const edgeEnd = group('e', true).lastElementChild.style.transform;
    const equalsEnd = group('eq').firstElementChild.style.transform;
    for (const root of [a.text, a.decorations]) root.style.setProperty('--appearance-colors-text', '#e9f0ee');
    const token = getComputedStyle(group('f').firstElementChild).color;
    const result = {formula, negateLines: group('s2', true).children.length, squares: unknown.style.width === unknown.style.height && area.style.width === area.style.height,
      units, segments, ticks, edgeMid, edgeEnd, equalsMid, equalsEnd, token};
    a.dispose(); return result;
  });
  assert.deepEqual(geometry.formula, [['x', '0px', '180px'], ['+', '180px', '180px'], ['=', '540px', '180px'], ['6', '720px', '180px']]);
  assert(geometry.squares); assert.equal(geometry.units, 3); assert.equal(geometry.segments, 3); assert.equal(geometry.ticks, 4);
  assert.equal(geometry.negateLines, 2);
  assert.equal(geometry.edgeMid, 'translate(195px, 30px)'); assert.equal(geometry.edgeEnd, 'translate(390px, 60px)');
  assert.equal(geometry.equalsMid, 'translate(-50px, 50px)'); assert.equal(geometry.equalsEnd, 'translate(-100px, 100px)');
  assert.equal(geometry.token, 'rgb(233, 240, 238)');
  for (const inline of [false, true]) {
    const host = await browser.newPage();
    await setup(host, '<main data-composition-id="fixture">' + (inline ? '<div id="S2" data-scene-id="S2"></div><div id="S3" data-scene-id="S3"></div>' : '') + '</main>');
    await host.evaluate(({inline, math}) => {
      window.HarnessAppearance = {load: async () => ({dispose() {}}), apply() {}};
      const item = math.items[0]; math.items = [item];
      const plan = {ratio: '16:9', projectBase: './', cues: {schema_version: 1, text: 'ABCDEFGHIJKLMNOPQRSTU', characters: Array.from('ABCDEFGHIJKLMNOPQRSTU', (char, start) => ({char, start, end: start + .9, aligned: true}))},
        scenes: [{id: 'S2', inline, start: 10, duration: 10, math, intent: {cues: [{cue: {token: 'M'}, reveal: [item.id], keep: [], remove: []}]}}]};
      if (inline) plan.scenes.push({id: 'S3', inline, start: 0, duration: 10, math, intent: {cues: [{cue: {token: 'C'}, reveal: [item.id], keep: [], remove: []}]}});
      const data = document.createElement('script'); data.type = 'application/json'; data.dataset.hfMathPlan = ''; data.textContent = JSON.stringify(plan); document.body.append(data);
      window.seek = async time => { const jobs = []; dispatchEvent(new CustomEvent('hf-seek', {detail: {time, waitUntil: p => jobs.push(p)}})); await Promise.all(jobs); };
    }, {inline, math: fixture});
    await host.addScriptTag({path: path.join(repo, '.studio/runtime/math-project.js')});
    const result = await host.evaluate(async inline => {
      await __hfMathBuildReady;
      const a = await HarnessMathProject.scene('S2'), offset = inline ? 0 : 10;
      const opacity = () => Number(a.items[0].element.style.opacity);
      await seek(11.9 - offset); const before = opacity();
      await seek(12.125 - offset); const middle = opacity();
      await seek(12.5 - offset); const after = opacity();
      const snapshot = a.text.innerHTML; await HarnessMathProject.renderAt(12.5); const api = snapshot === a.text.innerHTML;
      const b = document.createElement('div'); b.dataset.hfLayer = 'stage'; document.querySelector('main').append(b);
      await HarnessMathProject.setRolls([{id: 'S2', startCue: 'K', endCue: 'U', b: [{startCue: 'N', endCue: 'P', retreat: 'hide', media: b}]}]);
      let otherScene = true;
      if (inline) {
        await HarnessMathProject.renderAt(2.5);
        const other = await HarnessMathProject.scene('S3');
        otherScene = Number(other.items[0].element.style.opacity) === 1;
      }
      await seek(13.1 - offset); const freeze = a.text.innerHTML;
      await seek(14.8 - offset); const paused = freeze === a.text.innerHTML;
      await seek(16.5 - offset); const direct = a.text.innerHTML;
      await seek(19 - offset); await seek(16.5 - offset); const reverse = direct === a.text.innerHTML;
      await HarnessMathProject.renderAt(16.5); const rollAPI = direct === a.text.innerHTML;
      const rhythm = [...__hfRhythmSources].flatMap(source => source()).find(event => event.kind === 'math_reveal').time;
      HarnessMathProject.dispose();
      return {before, middle, after, api, paused, reverse, rollAPI, otherScene, rhythm, cleanup: document.querySelectorAll('[data-math-scene]').length};
    }, inline);
    assert.deepEqual(result, {before: 0, middle: .5, after: 1, api: true, paused: true, reverse: true, rollAPI: true, otherScene: true, rhythm: 12, cleanup: 0});
    await host.close();
  }
  console.log(JSON.stringify({kinds: 9, ratios: 2, seek: 'pass', fonts: 'custom-only', projects: 2, output}));
} finally { await browser.close(); }
