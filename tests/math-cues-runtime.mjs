import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import vm from 'node:vm';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {fileURLToPath} from 'node:url';

const fixture = JSON.parse((await promisify(execFile)('python3', [fileURLToPath(new URL('./test_math_chain.py', import.meta.url)), '--fixture'])).stdout);
const context = {window: {}};
vm.runInNewContext(await fs.readFile(new URL('../.studio/runtime/cues.js', import.meta.url), 'utf8'), context);
const helper = context.window.HarnessCues.from(fixture.cues);
for (const [query, expected] of fixture.queries) {
  if (typeof expected === 'string') assert.throws(() => helper.find(query), new RegExp(expected));
  else assert.equal(helper.find(query), expected);
}
assert.equal(fixture.cues.characters[1].start, null);
assert.throws(() => helper.find('a', {bar: 1, beat: 1}), /invalid_beat_query/);
for (const patch of [{times: [0, 0]}, {times: [0, NaN]}, {times: [-1, 1]}, {times: [false, 1]},
  {times: []}, {audio_sha256: 'no'}, {first_downbeat: null}, {first_downbeat: 8},
  {first_downbeat: true}, {beats_per_bar: 0}, {beats_per_bar: true}, {schema_version: true}]) {
  assert.throws(() => context.window.HarnessCues.from({...fixture.cues, beat_grid: {...fixture.cues.beat_grid, ...patch}}), /invalid_beat_grid/);
}
delete fixture.cues.beat_grid;
assert.throws(() => context.window.HarnessCues.from(fixture.cues).find({bar: 1, beat: 1}), /missing_beat_grid/);
console.log('math cue Python/browser parity passed');
