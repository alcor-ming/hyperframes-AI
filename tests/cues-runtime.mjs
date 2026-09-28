import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import vm from 'node:vm';

const source = await fs.readFile(new URL('../.studio/runtime/cues.js', import.meta.url), 'utf8');
const calls = [];
const location = new URL('http://localhost/api/projects/fixture/preview?revision=1');
const document = {baseURI: 'http://localhost/api/projects/fixture/preview/'};
const context = {window: {}, URL, location, document, fetch: async (url, options) => {
  calls.push({url: url.href, options});
  return {ok: true, json: async () => ({schema_version: 1, text: 'a',
    characters: [{char: 'a', aligned: true, start: 0, end: 1}]})};
}};
vm.runInNewContext(source, context);
const cues = context.window.HarnessCues;
assert.equal((await cues.load()).find('a'), 0);
assert.equal(calls[0].url, document.baseURI + 'runtime/cues.json');
assert.equal(calls[0].options.redirect, 'error');
await cues.load('/fixed/cues.json');
assert.equal(calls[1].url, 'http://localhost/fixed/cues.json');
await assert.rejects(cues.load('https://external.invalid/cues.json'), /cues_require_local_url/);
document.baseURI = 'https://external.invalid/';
await assert.rejects(cues.load(), /cues_require_local_url/);
assert.equal(calls.length, 2, 'cross-origin cues must not be fetched');
console.log('cues baseURI and same-origin guards passed');
