// CHROME_PATH=/usr/bin/google-chrome node tests/card-kit-browser.mjs
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const { chromium } = createRequire(path.join(repo, '.studio/remotion/package.json'))('playwright-core');
const output = await fs.mkdtemp(path.join(os.tmpdir(), 'hf-card-kit-'));
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome', headless: true, args: ['--no-sandbox'] });
const evidence = { output, scope: 'Isolated WSL browser, not Windows or user acceptance', cases: [] };
try {
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  await page.route('**/*', route => route.abort());
  await page.setContent('<style>body{margin:0;background:#e6e9e8}#frame{position:relative;width:1920px;height:1080px;transform:scale(.6666667);transform-origin:0 0}#stage,#text{position:absolute;inset:0}#stage{z-index:2}#text{z-index:4}</style><div id="frame"><div id="stage" data-hf-layer="stage"></div><div id="text" data-hf-layer="text"></div></div>');
  await page.addStyleTag({ path: path.join(repo, '.studio/runtime/card-kit.css') });
  await page.addScriptTag({ path: path.join(repo, '.studio/runtime/card-kit.js') });
  await page.addScriptTag({ path: path.join(repo, '.studio/runtime/cues.js') });
  await page.addScriptTag({ path: path.join(repo, '.studio/runtime/rolls.js') });
  await page.evaluate(() => {
    window.slot = (text, cue, svg) => ({ text, cue, ...(svg ? { svg } : {}) });
    window.icon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 12H20M12 4V20"/></svg>';
    window.figure = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 180" fill="none" stroke="currentColor" stroke-width="3"><rect x="16" y="16" width="160" height="120"/><path d="M176 76H450"/><rect x="450" y="16" width="160" height="120"/></svg>';
    window.cues = { find: query => typeof query === 'number' ? query : Number(query.token) };
    window.makeCard = (preset, area, svgMode) => ({
      id: preset, preset, area, title: slot('角色与能力', { token: '.15' }, svgMode ? 'icon' : null),
      lines: [slot('连接协议', { token: '1' }, svgMode && !['F05', 'F06', 'F07'].includes(preset) ? 'icon' : null), slot('能力发现', { token: '2' })].map((line, i) => ({ ...line,
        ...(preset === 'F04' ? { indexKey: slot('索引' + (i + 1), { token: String(.7 + i) }) } : {}),
        ...(preset === 'F06' ? { key: slot('字段' + (i + 1), { token: String(.7 + i) }, svgMode && !i ? 'icon' : null) } : {}),
      })),
      note: slot('概念说明', { token: '3' }),
      ...(preset === 'F07' ? { input: slot('说明角色', { token: '.2' }, svgMode ? 'icon' : null), inputLabel: slot('输入', { token: '.1' }), outputLabel: slot('输出', { token: '.4' }, svgMode ? 'icon' : null) } : {}),
      ...(svgMode && ['F03', 'F05', 'F08'].includes(preset) ? { figure: { svg: 'figure', cue: { token: '.4' } } } : {}),
    });
    window.mount = async (card, ratio = '16:9', extra = {}) => HarnessCardKit.mount({ stage: document.querySelector('#stage'), text: document.querySelector('#text'), card, cues, ratio, end: 9, resolveSVG: async ref => ref === 'figure' ? figure : icon, ...extra });
    window.snapshot = () => document.querySelector('#stage').innerHTML + document.querySelector('#text').innerHTML;
  });
  for (const ratio of ['16:9', '9:16']) {
    await page.setViewportSize(ratio === '16:9' ? { width: 1280, height: 720 } : { width: 450, height: 800 });
    await page.evaluate(ratio => {
      const frame = document.querySelector('#frame');
      Object.assign(frame.style, ratio === '16:9' ? { width: '1920px', height: '1080px', transform: 'scale(.6666667)' } : { width: '1080px', height: '1920px', transform: 'scale(.4166667)' });
    }, ratio);
    for (const area of ['full', 'left', 'right', 'top', 'bottom']) for (const preset of ['F01', 'F02', 'F03', 'F04', 'F05', 'F06', 'F07', 'F08']) for (const svg of [false, true]) {
      const result = await page.evaluate(async ({ ratio, area, preset, svg }) => {
        const binding = await mount(makeCard(preset, area, svg), ratio);
        binding.renderAt(4);
        const direct = snapshot();
        for (let t = 0; t <= 4; t += .1) binding.renderAt(t);
        binding.renderAt(4);
        const sequential = snapshot();
        binding.renderAt(8.7); binding.renderAt(4);
        const reverse = snapshot();
        const geometry = binding.getState();
        const layers = !binding.decorations.textContent.trim() && binding.items.every(item => binding.text.contains(item.element));
        const rhythm = binding.rhythm().length;
        binding.dispose();
        return { equal: direct === sequential && direct === reverse, geometry, layers, rhythm };
      }, { ratio, area, preset, svg });
      assert(result.equal, `${ratio}/${area}/${preset}/${svg}: non-deterministic seek`);
      assert(result.layers && !result.geometry.overflow && result.rhythm > 4);
      evidence.cases.push({ ratio, area, preset, svg, slots: result.geometry.slots.length });
      if (area === 'full' && svg) {
        await page.evaluate(async ({ preset, ratio }) => { window.shot = await mount(makeCard(preset, 'full', true), ratio); shot.renderAt(4); }, { preset, ratio });
        await page.screenshot({ path: path.join(output, preset + '-' + ratio.replace(':', 'x') + '.png') });
        await page.evaluate(() => shot.dispose());
      }
    }
    await page.evaluate(async ratio => { window.shot = await mount(makeCard('F03', 'full', true), ratio); shot.renderAt(4); }, ratio);
    await page.screenshot({ path: path.join(output, ratio.replace(':', 'x') + '.png') });
    await page.evaluate(() => shot.dispose());
  }
  const checks = await page.evaluate(async () => {
    const a = await mount(makeCard('F01', 'left', true));
    const b = await mount(makeCard('F08', 'right', true));
    a.renderAt(2); b.renderAt(4);
    const before = b.text.innerHTML; a.renderAt(8); a.dispose();
    const independent = before === b.text.innerHTML && b.text.isConnected;
    b.dispose();
    const fail = async (card, extra) => { try { const c = await mount(card, '16:9', extra); c.dispose(); return ''; } catch (e) { return e.message; } };
    const long = makeCard('F01', 'left', false); long.lines[0].text = '超出容量'.repeat(500);
    const overflow = await fail(long);
    const malicious = await fail(makeCard('F01', 'left', true), { resolveSVG: () => '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><script>alert(1)</script></svg>' });
    const reduced = await mount(makeCard('F08', 'full', true), '16:9', { reducedMotion: true });
    reduced.renderAt(.4);
    const noMotion = [...reduced.text.querySelectorAll('*'), ...reduced.decorations.querySelectorAll('*')].every(node => !node.style.transform || node.style.transform === 'none');
    reduced.dispose();
    return { independent, overflow, malicious, noMotion, remaining: document.querySelectorAll('.hf-card-kit').length, sources: __hfRhythmSources.size };
  });
  assert(checks.independent && checks.noMotion);
  assert.match(checks.overflow, /overflow/); assert.match(checks.malicious, /unsafe_card_svg/);
  assert.equal(checks.remaining, 0); assert.equal(checks.sources, 0);
  const special = await page.evaluate(async () => {
    const a = makeCard('F06', 'full', true); a.title = undefined; a.note = undefined;
    const sparse = await mount(a); sparse.renderAt(1.9);
    const absentSlots = !sparse.items.some(item => /:title|:note/.test(item.id)); sparse.dispose();
    const minimal = await mount({ id: 'minimal', preset: 'F01', area: 'full', lines: [], title: slot('单独标题', { token: '.1' }) });
    const minimalSlots = minimal.items.length; minimal.dispose();
    const pixel = await mount(makeCard('F01', '864px x 936px', false));
    const pixelRegion = pixel.getState().region; pixel.dispose();
    const dark = await mount(makeCard('F03', 'full', true));
    for (const root of [dark.text, dark.decorations]) { root.style.setProperty('--appearance-colors-text', '#f2f5f3'); root.style.setProperty('--appearance-surface-color', '#252d29'); }
    const darkText = getComputedStyle(dark.items[0].element.querySelector('h1')).color;
    dark.dispose();
    const actualCues = HarnessCues.from({ schema_version: 1, text: 'ABCDEFGHIJK', characters: Array.from('ABCDEFGHIJK', (char, start) => ({ char, start, end: start + .9, aligned: true })) });
    const abCard = { id: 'AB', preset: 'F01', area: 'full', title: slot('标题', { token: 'A' }), lines: [slot('第一条', { token: 'C' }), slot('第二条', { token: 'G' })], note: slot('注释', { token: 'I' }) };
    const instance = await mount(abCard, '16:9', { cues: actualCues, end: 10 });
    const activeTime = t => t - Math.max(0, Math.min(t, 5) - 3);
    instance.retime(cue => activeTime(actualCues.find(cue)), activeTime(10));
    const b = document.createElement('div'); document.querySelector('#stage').appendChild(b);
    const rolls = HarnessRolls.mount({ cues: actualCues, scenes: [{ id: 'S1', startCue: 'A', endCue: 'K', a: instance, b: [{ startCue: 'D', endCue: 'F', retreat: 'hide', media: b }] }] });
    await rolls.renderAt(3.1); const frozen = instance.text.innerHTML;
    await rolls.renderAt(4.9); const paused = instance.text.innerHTML === frozen;
    await rolls.renderAt(6.5); const direct = snapshot();
    const second = instance.items.find(item => item.id === 'AB:2').element;
    const revealed = Number(second.parentElement.style.opacity) === 1 && getComputedStyle(second).visibility === 'visible';
    await rolls.renderAt(9); await rolls.renderAt(6.5); const reverse = snapshot() === direct;
    const rawRhythm = instance.rhythm().find(event => event.target.dataset.cardRow === '2' && event.kind === 'card_reveal').time;
    rolls.dispose(); instance.dispose(); b.remove();
    return { absentSlots, minimalSlots, paused, revealed, reverse, rawRhythm, pixelRegion, darkText };
  });
  assert(special.absentSlots && special.paused && special.revealed && special.reverse, JSON.stringify(special));
  assert.equal(special.minimalSlots, 1); assert.equal(special.rawRhythm, 6);
  assert.deepEqual(special.pixelRegion, { x: 72, y: 72, w: 864, h: 936 });
  assert.equal(special.darkText, 'rgb(242, 245, 243)');
  evidence.special = special;
  evidence.labelOverflow = await page.evaluate(async () => {
    const results = [];
    for (const slot of ['inputLabel', 'outputLabel']) {
      const card = makeCard('F07', 'left', true);
      card[slot].text = 'X'.repeat(500);
      let wrapped;
      try {
        const instance = await mount(card);
        const label = instance.items.find(item => item.id === 'F07:' + slot).element.querySelector('.io-label');
        const name = slot === 'inputLabel' ? 'input-label' : 'output-label';
        wrapped = label.scrollWidth <= label.clientWidth + 1 && instance.getState().slots.some(item => item.name === name);
        instance.dispose();
      } catch (error) { if (!error.message.startsWith('card_content_overflow:')) throw error; wrapped = true; }
      card[slot].text = 'X'.repeat(5000);
      let error = '';
      try { const instance = await mount(card); instance.dispose(); } catch (failure) { error = failure.message; }
      results.push({ slot, wrapped, error });
    }
    return results;
  });
  for (const result of evidence.labelOverflow) { assert(result.wrapped); assert.match(result.error, /^card_content_overflow:/); }
  evidence.svgSafety = await page.evaluate(async () => {
    const custom = makeCard('F01', 'full', false); custom.title.svg = 'custom:icon.svg';
    const attempt = async (card, source) => {
      try { const instance = await mount(card, '16:9', { resolveSVG: () => source }); instance.dispose(); return 'ok'; }
      catch (error) { return error.message; }
    };
    const base = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">';
    const nine = '<path d="M4 12H20"/>'.repeat(9);
    const standard = makeCard('F01', 'full', false); standard.title.svg = 'lucide:fixture';
    const standardSVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" data-icon="lucide:fixture@1" fill="none" stroke="currentColor" color="var(--appearance-colors-text)" stroke-width="var(--appearance-lines-icon-width,2)">' + nine + '</svg>';
    const figureCard = makeCard('F03', 'full', false); figureCard.figure = { svg: 'custom:figure.svg', cue: { token: '.4' } };
    return {
      validCustom: await attempt(custom, icon), standard: await attempt(standard, standardSVG),
      complexity: await attempt(custom, base + nine + '</svg>'),
      edge: await attempt(custom, base + '<path d="M0 12H24"/></svg>'),
      stroke: await attempt(custom, icon.replace('stroke-width="2"', 'stroke-width="1"')),
      figure: await attempt(figureCard, figure),
      ambiguous: await attempt(figureCard, figure.replace('M176 76H450', 'M176 76H450Z')),
    };
  });
  assert.deepEqual(evidence.svgSafety, { validCustom: 'ok', standard: 'ok', complexity: 'card_svg_complexity_exceeded', edge: 'card_svg_safe_edge_violation', stroke: 'card_svg_stroke_too_thin', figure: 'ok', ambiguous: 'card_svg_ambiguous_figure_path' });
  // Use the approved font only in memory for a same-content geometry comparison.
  try {
  const font = await fs.readFile(path.join(repo, 'output/card-svg-slots-v352-r3/assets/font.ttf'));
  await page.addStyleTag({ content: '@font-face{font-family:ApprovedParity;src:url(data:font/ttf;base64,' + font.toString('base64') + ')}.hf-card-kit{font-family:ApprovedParity}' });
  await page.evaluate(() => document.fonts.load('32px ApprovedParity'));
  const parity = await page.evaluate(async () => {
    const card = makeCard('F01', 'left', true);
    card.title.text = 'MCP 的角色与能力'; card.note.text = '概念示意 · 非执行记录';
    card.lines[0].text = 'AI 应用协调客户端与模型交互。'; card.lines[1].text = '客户端负责与服务端交换协议消息。';
    card.lines[1].svg = 'icon';
    const binding = await mount(card); const slots = binding.getState().slots; binding.dispose(); return slots;
  });
  const approved = JSON.parse(await fs.readFile(path.join(repo, 'output/card-svg-slots-v352-r3/qa/slot-measurements.json'), 'utf8'));
  assert.deepEqual(parity, approved.find(row => row.preset === 'F01' && row.group === 'A' && row.on).state.slots);
  evidence.approvedGeometryParity = 'F01/A/two rows/all icons, exact slot geometry with approved font';
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
    evidence.approvedGeometryParity = 'not_available: local approved source/font absent; synthetic matrix still verified';
  }
  evidence.projectIntegration = [];
  for (const inline of [false, true]) {
    const host = await browser.newPage({ viewport: { width: 1280, height: 720 } });
    const errors = []; host.on('pageerror', error => errors.push(error.message));
    await host.route('**/*', route => route.abort());
    await host.setContent('<base href="http://fixture.invalid/"><style>body{margin:0}main{position:relative;width:1920px;height:1080px}#S2{position:absolute;inset:0}</style><main data-composition-id="fixture">' + (inline ? '<div id="S2" data-scene-id="S2"></div>' : '') + '</main>');
    await host.addStyleTag({ path: path.join(repo, '.studio/runtime/card-kit.css') });
    for (const script of ['cues', 'rolls', 'scene-binding', 'card-kit']) await host.addScriptTag({ path: path.join(repo, '.studio/runtime', script + '.js') });
    await host.evaluate(inline => {
      window.HarnessAppearance = { load: async () => ({ dispose() {} }), apply() {} };
      const field = (text, token) => ({ text, cue: { token } });
      const plan = { projectBase: './', ratio: '16:9', svg: {},
        cues: { schema_version: 1, text: 'ABCDEFGHIJKLMNOPQRSTU', characters: Array.from('ABCDEFGHIJKLMNOPQRSTU', (char, start) => ({ char, start, end: start + .9, aligned: true })) },
        scenes: [{ id: 'S2', inline, start: 10, duration: 10, cards: [{ id: 'C1', preset: 'F01', area: 'full', title: field('场景二', 'K'), lines: [field('稍后出现', 'M'), field('恢复之后', 'Q')], note: field('结论', 'S') }] }],
      };
      const data = document.createElement('script'); data.type = 'application/json'; data.dataset.hfCardPlan = ''; data.textContent = JSON.stringify(plan); document.body.appendChild(data);
      window.seekDocument = async time => { const pending = []; dispatchEvent(new CustomEvent('hf-seek', { detail: { time, waitUntil: job => pending.push(job) } })); await Promise.all(pending); };
    }, inline);
    await host.addScriptTag({ path: path.join(repo, '.studio/runtime/card-project.js') });
    const result = await host.evaluate(async inline => {
      await HarnessCardProject.ready;
      const a = await HarnessCardProject.scene('S2');
      const offset = inline ? 0 : 10;
      const first = a.items.find(item => item.id === 'C1:1').element;
      const opacity = () => Number(first.parentElement.style.opacity);
      await seekDocument(11.9 - offset); const beforeCue = opacity();
      await seekDocument(12.1 - offset); const duringCue = opacity();
      await seekDocument(12.3 - offset); const afterCue = opacity();
      const beforeAPI = a.text.innerHTML;
      await HarnessCardProject.renderAt(12.3); const globalAPI = a.text.innerHTML === beforeAPI;
      const b = document.createElement('div'); b.dataset.hfLayer = 'stage'; document.querySelector('main').appendChild(b);
      await HarnessCardProject.setRolls([{ id: 'S2', startCue: 'K', endCue: 'U', b: [{ startCue: 'N', endCue: 'P', retreat: 'hide', media: b }] }]);
      await seekDocument(13.4 - offset); const frozen = a.text.innerHTML;
      await seekDocument(14.6 - offset); const paused = a.text.innerHTML === frozen;
      await seekDocument(16.4 - offset); const direct = a.text.innerHTML;
      const second = a.items.find(item => item.id === 'C1:2').element;
      const resumed = Number(second.parentElement.style.opacity) === 1 && getComputedStyle(second).visibility === 'visible';
      await seekDocument(19.4 - offset); await seekDocument(16.4 - offset);
      const reverse = direct === a.text.innerHTML;
      await HarnessCardProject.renderAt(16.4); const globalRollsAPI = direct === a.text.innerHTML;
      const reveal = [...__hfRhythmSources].flatMap(source => source()).find(event => event.kind === 'card_reveal' && event.target === first);
      const snapshot = a.text.innerHTML;
      HarnessCardProject.dispose();
      return { beforeCue, duringCue, afterCue, globalAPI, globalRollsAPI, paused, resumed, reverse, rhythmTime: reveal.time, snapshot, cleanup: document.querySelectorAll('[data-card-scene]').length };
    }, inline);
    assert.equal(result.beforeCue, 0); assert(result.duringCue > 0 && result.duringCue < 1); assert.equal(result.afterCue, 1);
    assert(result.globalAPI && result.globalRollsAPI && result.paused && result.resumed && result.reverse, JSON.stringify(result));
    assert.equal(result.rhythmTime, 12); assert.equal(result.cleanup, 0); assert.deepEqual(errors, []);
    evidence.projectIntegration.push({ inline, ...result }); await host.close();
  }
  assert.equal(evidence.projectIntegration[0].snapshot, evidence.projectIntegration[1].snapshot);
  evidence.checks = checks;
  await fs.writeFile(path.join(output, 'evidence.json'), JSON.stringify(evidence, null, 2));
  console.log(JSON.stringify({ cases: evidence.cases.length, ...checks, ...special, parity: evidence.approvedGeometryParity, projectIntegration: evidence.projectIntegration.length, output }));
} finally { await browser.close(); }
