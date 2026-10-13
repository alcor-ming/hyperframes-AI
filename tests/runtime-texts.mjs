import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const source = readFileSync(new URL('../.studio/runtime/broll.js', import.meta.url), 'utf8');
const CONTRACT = {duration: {min: 1, max: 10, default: 4}, timing: 'stretch', caption_safe_zone: {'16:9': true}, slots: {}, params: {}, sfx_cues: []};
const APPEARANCE = {lock: {ratio: '16:9'}, projectURL: 'http://localhost/', theme: {fonts: ['Inter']}, colors: {}};
const plain = value => JSON.parse(JSON.stringify(value));

const matches = (node, selector) => selector === 'canvas' ? node.localName === 'canvas'
  : selector === '[data-hf-layer]' ? node.dataset?.hfLayer !== undefined
  : selector === '[data-scene-id]' ? node.dataset?.sceneId !== undefined : false;
function* descendants(node) { for (const child of node.children) { yield child; yield* descendants(child); } }
function element(localName, doc) {
  const node = {
    localName, ownerDocument: doc, isConnected: true, parentElement: null, children: [], childNodes: [], attributes: [],
    style: {}, dataset: {}, id: '', textContent: '', clientWidth: 120, clientHeight: 24, scrollWidth: 120, scrollHeight: 24, fontFamily: 'Inter',
    contains(other) { for (let n = other; n; n = n.parentElement) if (n === node) return true; return false; },
    closest(selector) { for (let n = node; n; n = n.parentElement) if (matches(n, selector)) return n; return null; },
    querySelector(selector) { for (const n of descendants(node)) if (matches(n, selector)) return n; return null; },
    appendChild(child) { child.parentElement = node; node.children.push(child); return child; },
  };
  return node;
}
function harness({canvas = false, metadata, build}) {
  const document = {baseURI: 'http://localhost/index.html', location: {origin: 'http://localhost'}, fonts: {ready: Promise.resolve()}};
  const sceneRoot = element('section', document); sceneRoot.dataset = {sceneId: 'scene-a'};
  const stage = element('div', document); stage.dataset = {hfLayer: 'stage'};
  sceneRoot.appendChild(stage);
  if (canvas) stage.appendChild(element('canvas', document));
  const sandbox = {
    window: null, document, console, URL, Promise, getComputedStyle: node => ({fontFamily: node.fontFamily}),
    HarnessAppearance: {apply() {}},
    fetch: async () => { throw new Error('fetch_not_expected'); },
    DOMParser: class { parseFromString() { return {documentElement: element('svg', document)}; } },
  };
  sandbox.window = sandbox;
  const context = vm.createContext(sandbox);
  vm.runInContext(source, context, {filename: 'broll.js'});
  const options = {stage, text: undefined, appearance: APPEARANCE, cues: undefined, startCue: 10, endCue: 16, slots: {}, params: {}};
  return {context, mount: () => context.HarnessBroll.mount(metadata, options, build)};
}
const performance = texts => ({renderAt() {}, events: [], labels: {}, ...(texts ? {texts: () => texts} : {})});

const tests = [];
const run = (name, fn) => tests.push([name, fn]);
const ok = build => ({renderAt() {}, events: [], labels: {}, ...build});

run('maps local time to cue window, records metadata, source set, fresh copies, disposal', async () => {
  const metadata = {id: 'asset-a', broll: CONTRACT, text_ownership: {mode: 'embedded', kinds: ['caption']}};
  const inventory = [
    {id: 'c1', text: 'Hello', start: 1, end: 3, kind: 'independent', embedded: true, text_type: 'caption', region: {x: 0.1, y: 0.2, width: 0.5, height: 0.1}},
    {id: 't1', text: 'Title', start: 0.5, end: 2, kind: 'attached', embedded: true, text_type: 'title'},
    {id: 'n1', text: 'Note', start: 0, end: 1, kind: 'independent', embedded: false},
    {id: 'x1', text: 'X', start: 0, end: 1, kind: 'independent', embedded: true, text_type: 'title'},
  ];
  const {context, mount} = harness({canvas: true, metadata, build: () => performance(inventory)});
  const binding = await mount();
  const texts = binding.texts();
  assert.equal(texts.length, 4);
  const find = id => texts.find(entry => entry.id === id);
  assert.deepEqual({start: find('c1').start, end: find('c1').end}, {start: 11.5, end: 14.5});
  assert.deepEqual({scene: find('c1').scene, asset: find('c1').asset, layer: find('c1').layer, font: find('c1').font_family}, {scene: 'scene-a', asset: 'asset-a', layer: 'stage', font: 'Inter'});
  assert.equal(find('c1').selector, '#asset-a [data-hf-id="c1"]');
  assert.deepEqual(plain(find('c1').region), {x: 0.1, y: 0.2, width: 0.5, height: 0.1});
  assert.deepEqual([find('c1').ownership_allowed, find('t1').ownership_allowed, find('n1').ownership_allowed, find('x1').ownership_allowed], [true, true, true, false]);
  assert.equal(find('n1').layer, 'text');
  assert.equal(context.__hfTextSources.size, 1);
  assert.equal([...context.__hfTextSources][0]().length, 4);
  const first = binding.texts(); first[0].id = 'mutated';
  assert.notEqual(binding.texts()[0].id, 'mutated');
  binding.dispose();
  assert.equal(context.__hfTextSources.size, 0);
});

run('rejects invalid inventory windows', async () => {
  const metadata = {id: 'asset-a', broll: CONTRACT};
  const inventory = [{id: 'b1', text: 'x', start: 3, end: 5, kind: 'attached', embedded: false}];
  await assert.rejects(harness({metadata, build: () => performance(inventory)}).mount(), /broll_invalid_text_window/);
});

run('clears registered sources when a later step fails', async () => {
  const metadata = {id: 'asset-a', broll: CONTRACT};
  const inventory = [{id: 'c1', text: 'Hello', start: 0, end: 1, kind: 'attached', embedded: false}];
  const {context, mount} = harness({metadata, build: () => ({renderAt() {}, events: [{time: 99, target: undefined}], labels: {}, texts: () => inventory})});
  await assert.rejects(mount(), /broll_invalid_moment_target/);
  assert.equal(context.__hfTextSources.size, 0);
});

run('rejects invalid kind, missing text_type, and unnormalized region', async () => {
  const metadata = {id: 'asset-a', broll: CONTRACT};
  const bad = [
    [{id: 'k', text: 'x', start: 0, end: 1, kind: 'float', embedded: false}],
    [{id: 't', text: 'x', start: 0, end: 1, kind: 'independent', embedded: true}],
    [{id: 'r', text: 'x', start: 0, end: 1, kind: 'attached', embedded: false, region: {x: 1.5, y: 0, width: 0.5, height: 0.5}}],
  ];
  await assert.rejects(harness({metadata, build: () => performance(bad[0])}).mount(), /broll_invalid_text_kind/);
  await assert.rejects(harness({metadata, build: () => performance(bad[1])}).mount(), /broll_invalid_text_type/);
  await assert.rejects(harness({metadata, build: () => performance(bad[2])}).mount(), /broll_invalid_text_region/);
});

run('requires texts() for canvas stage and for text_ownership metadata', async () => {
  await assert.rejects(harness({canvas: true, metadata: {id: 'a', broll: CONTRACT}, build: () => performance()}).mount(), /broll_requires_texts_inventory/);
  await assert.rejects(harness({metadata: {id: 'a', broll: CONTRACT, text_ownership: {mode: 'embedded', kinds: []}}, build: () => performance()}).mount(), /broll_requires_texts_inventory/);
});

run('legacy DOM-only performance without texts returns empty inventory', async () => {
  const {context, mount} = harness({metadata: {id: 'a', broll: CONTRACT}, build: () => performance()});
  const binding = await mount();
  assert.equal(binding.texts().length, 0);
  assert.equal(context.__hfTextSources.size, 1);
  binding.dispose();
  assert.equal(context.__hfTextSources.size, 0);
});

let failed = 0;
for (const [name, fn] of tests) {
  try { await fn(); console.log('ok -', name); }
  catch (error) { failed++; console.error('not ok -', name, '\n  ', error && error.message); }
}
console.log(failed ? `FAILED ${failed}/${tests.length}` : `PASSED ${tests.length}/${tests.length}`);
process.exitCode = failed ? 1 : 0;
