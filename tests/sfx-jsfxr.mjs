// Assert-based regression tests for the jsfxr contrast SFX generator.
// Run: node --test tests/sfx-jsfxr.mjs
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import {
  existsSync,
  linkSync,
  lstatSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { after, before, test } from 'node:test';
import { fileURLToPath } from 'node:url';

import { KINDS, MAX_SEED, parseWav, synthesizeWav } from '../.studio/sfx/jsfxr.mjs';

const GENERATOR = fileURLToPath(new URL('../.studio/sfx/jsfxr.mjs', import.meta.url));
const KINDS_UNDER_TEST = ['click', 'whoosh', 'riser', 'fall', 'impact'];
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');

let root;
let counter = 0;
const unique = (label) => path.join(root, `${label}-${counter++}`);

before(() => {
  root = mkdtempSync(path.join(os.tmpdir(), 'sfx-jsfxr-'));
});

after(() => {
  rmSync(root, { recursive: true, force: true });
});

// Independent duration/size reader straight from the WAV header bytes.
function readWavFacts(bytes) {
  const u32 = (o) => bytes.readUInt32LE(o);
  const u16 = (o) => bytes.readUInt16LE(o);
  assert.equal(bytes.toString('latin1', 0, 4), 'RIFF');
  assert.equal(bytes.toString('latin1', 8, 12), 'WAVE');
  assert.equal(u32(4), bytes.length - 8, 'RIFF chunk size matches file length');
  assert.equal(bytes.toString('latin1', 36, 40), 'data');
  const channels = u16(22);
  const sampleRate = u32(24);
  const bitsPerSample = u16(34);
  const dataSize = u32(40);
  assert.equal(44 + dataSize, bytes.length, 'no truncation');
  const numSamples = dataSize / (channels * (bitsPerSample / 8));
  return { channels, sampleRate, bitsPerSample, dataSize, duration: numSamples / sampleRate };
}

function runCli(parameters, output, extraArgs = []) {
  const paramsPath = unique('params') + '.json';
  writeFileSync(paramsPath, JSON.stringify(parameters));
  const result = spawnSync(
    process.execPath,
    [GENERATOR, '--parameters', paramsPath, '--output', output, ...extraArgs],
    { encoding: 'utf8' },
  );
  return result;
}

test('generates a real PCM WAV plus metadata for all five kinds', () => {
  for (const kind of KINDS_UNDER_TEST) {
    const output = unique(kind) + '.wav';
    const result = runCli({ kind }, output);
    assert.equal(result.status, 0, `${kind}: ${result.stderr}`);
    assert.ok(existsSync(output), `${kind}: wav exists`);

    const bytes = readFileSync(output);
    const facts = readWavFacts(bytes);
    assert.ok(facts.duration > 0, `${kind}: audible duration`);
    assert.equal(facts.sampleRate, 44100);
    assert.equal(facts.bitsPerSample, 8);
    assert.equal(facts.channels, 1);

    const meta = JSON.parse(readFileSync(output + '.json', 'utf8'));
    assert.equal(meta.engine, 'jsfxr');
    assert.equal(meta.engine_version, '1.4.1');
    assert.deepEqual(meta.parameters, { kind, seed: 1, gain: 0.5 });
    assert.equal(meta.seed, 1);
    assert.equal(meta.duration, facts.duration);
    assert.equal(meta.wav_sha256, sha256(bytes));
    assert.equal(
      meta.source_sha256,
      sha256(readFileSync(GENERATOR)),
      `${kind}: source hash of jsfxr.mjs`,
    );
  }
});

test('same seed produces byte-identical output; different seed differs', () => {
  const first = unique('det-a') + '.wav';
  const second = unique('det-b') + '.wav';
  const other = unique('det-c') + '.wav';
  assert.equal(runCli({ kind: 'riser', seed: 4242 }, first).status, 0);
  assert.equal(runCli({ kind: 'riser', seed: 4242 }, second).status, 0);
  assert.equal(runCli({ kind: 'riser', seed: 4243 }, other).status, 0);
  const a = readFileSync(first);
  const b = readFileSync(second);
  assert.deepEqual(a, b, 'same seed -> same bytes');
  assert.notDeepEqual(a, readFileSync(other), 'different seed -> different bytes');
});

test('zero gain yields silent PCM and explicit silence is accepted', () => {
  const output = unique('zero') + '.wav';
  assert.equal(runCli({ kind: 'click', gain: 0, seed: 9 }, output).status, 0);
  const bytes = readFileSync(output);
  const facts = readWavFacts(bytes);
  const data = bytes.subarray(44, 44 + facts.dataSize);
  const distinct = new Set(data);
  assert.equal(distinct.size, 1, 'all samples share one value');
  assert.equal([...distinct][0], 0x80, '8-bit midpoint is silence');
});

test('rejects unknown fields, kinds, and non-finite or out-of-range numbers', () => {
  const cases = [
    { kind: 'click', extra: true },
    { kind: 'boom' },
    { gain: 0.5 },
    { kind: 'click', gain: 1.5 },
    { kind: 'click', gain: -0.1 },
    { kind: 'click', gain: 'loud' },
    { kind: 'click', gain: 1e999 },
    { kind: 'click', seed: -1 },
    { kind: 'click', seed: 1.5 },
    { kind: 'click', seed: '1' },
    { kind: 'click', seed: MAX_SEED + 1 },
  ];
  for (const input of cases) {
    const output = unique('bad') + '.wav';
    const result = runCli(input, output);
    assert.notEqual(result.status, 0, `rejected: ${JSON.stringify(input)}`);
    assert.ok(!existsSync(output), `no output for: ${JSON.stringify(input)}`);
    assert.ok(!existsSync(output + '.json'), `no metadata for: ${JSON.stringify(input)}`);
  }
  const malformed = unique('malformed') + '.json';
  writeFileSync(malformed, '{ not json');
  const out = unique('malformed') + '.wav';
  const result = spawnSync(
    process.execPath,
    [GENERATOR, '--parameters', malformed, '--output', out],
    { encoding: 'utf8' },
  );
  assert.notEqual(result.status, 0);
  assert.ok(!existsSync(out));
});

test('rejects unknown CLI arguments', () => {
  const result = runCli({ kind: 'click' }, unique('args') + '.wav', ['--extra']);
  assert.notEqual(result.status, 0);
});

test('refuses to overwrite existing files, symlinks, and hardlinks', () => {
  const output = unique('existing') + '.wav';
  writeFileSync(output, 'keep-me');
  const blocked = runCli({ kind: 'click' }, output);
  assert.notEqual(blocked.status, 0);
  assert.equal(readFileSync(output, 'utf8'), 'keep-me', 'existing output preserved');
  assert.ok(!existsSync(output + '.json'), 'no metadata written beside existing output');

  const metaClash = unique('metaclash') + '.wav';
  writeFileSync(metaClash + '.json', '{"keep":true}');
  const clash = runCli({ kind: 'click' }, metaClash);
  assert.notEqual(clash.status, 0);
  assert.ok(!existsSync(metaClash), 'wav not written when metadata path is taken');
  assert.equal(readFileSync(metaClash + '.json', 'utf8'), '{"keep":true}');

  const target = unique('target') + '.wav';
  writeFileSync(target, 'target-bytes');
  const symlinkPath = unique('symlink') + '.wav';
  symlinkSync(target, symlinkPath);
  const viaSymlink = runCli({ kind: 'click' }, symlinkPath);
  assert.notEqual(viaSymlink.status, 0);
  assert.equal(readFileSync(target, 'utf8'), 'target-bytes', 'symlink target untouched');

  const brokenPath = unique('broken') + '.wav';
  symlinkSync(unique('missing-target'), brokenPath);
  assert.notEqual(runCli({ kind: 'click' }, brokenPath).status, 0);
  assert.ok(lstatSync(brokenPath).isSymbolicLink(), 'broken symlink left in place');

  const hardTarget = unique('hard-target') + '.wav';
  writeFileSync(hardTarget, 'hard-target-bytes');
  const hardPath = unique('hard') + '.wav';
  linkSync(hardTarget, hardPath);
  assert.notEqual(runCli({ kind: 'click' }, hardPath).status, 0);
  assert.equal(readFileSync(hardTarget, 'utf8'), 'hard-target-bytes', 'hardlink target untouched');
});

test('leaves Math.random unpatched on success and on failure', () => {
  const original = Math.random;
  const output = unique('rand') + '.wav';
  const bytes = synthesizeWav({ kind: 'impact', seed: 3, gain: 0.4 });
  assert.ok(bytes.length > 44);
  assert.equal(Math.random, original, 'restored after success');

  assert.throws(() => synthesizeWav({ kind: 'not-a-kind', seed: 3, gain: 0.4 }));
  assert.equal(Math.random, original, 'restored after failure');
});

test('detects malformed and truncated WAV data', () => {
  const output = unique('trunc') + '.wav';
  assert.equal(runCli({ kind: 'fall', seed: 2 }, output).status, 0);
  const bytes = readFileSync(output);
  assert.doesNotThrow(() => parseWav(bytes));
  assert.throws(() => parseWav(bytes.subarray(0, bytes.length - 4)), /truncated|size/i);

  const badTag = Buffer.from(bytes);
  badTag.write('XIFF', 0, 'latin1');
  assert.throws(() => parseWav(badTag), /RIFF/);
});

test('writes only the wav and metadata, leaving no temporary files', () => {
  const workdir = mkdtempSync(path.join(root, 'isolated-'));
  const output = path.join(workdir, 'sound.wav');
  assert.equal(runCli({ kind: 'whoosh', seed: 11 }, output).status, 0);
  assert.deepEqual(readdirSync(workdir).sort(), ['sound.wav', 'sound.wav.json']);

  const empty = mkdtempSync(path.join(root, 'reject-'));
  const blocked = runCli({ kind: 'nope' }, path.join(empty, 'x.wav'));
  assert.notEqual(blocked.status, 0);
  assert.deepEqual(readdirSync(empty), [], 'failed run leaves no temp files');

  assert.deepEqual(KINDS.slice().sort(), KINDS_UNDER_TEST.slice().sort());
});
