#!/usr/bin/env node
// Deterministic 8-bit PCM SFX generator backed by the installed jsfxr engine.
//
// CLI: node jsfxr.mjs --parameters <params.json> --output <out.wav>
// Params JSON: { "kind": "click"|"whoosh"|"riser"|"fall"|"impact",
//                "seed": <nonnegative 31-bit int>, "gain": <0..1> }
// Defaults: seed = 1, gain = 0.5. Unknown fields/types are rejected.
//
// Synthesizes real PCM WAV bytes through the jsfxr public API, seeds the engine
// randomness deterministically (restoring Math.random afterwards), and records
// a sibling "<out.wav>.json" metadata file. Existing outputs are never
// overwritten and symlink/hardlink targets are never written through.

import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';
import {
  closeSync,
  lstatSync,
  mkdirSync,
  openSync,
  unlinkSync,
  writeSync,
} from 'node:fs';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { jsfxr, sfxr } from './vendor/jsfxr/sfxr.mjs';

const MODULE_PATH = fileURLToPath(import.meta.url);
const KINDS = Object.freeze(['click', 'whoosh', 'riser', 'fall', 'impact']);
const ALLOWED_FIELDS = new Set(['kind', 'seed', 'gain']);
const DEFAULT_SEED = 1;
const DEFAULT_GAIN = 0.5;
const MAX_SEED = 2147483647;
const SAMPLE_RATE = 44100;
const SAMPLE_SIZE = 8;

function sha256(bytes) {
  return createHash('sha256').update(bytes).digest('hex');
}

// mulberry32: small, fast, fully deterministic PRNG in [0, 1).
function mulberry32(seed) {
  let state = seed >>> 0;
  return function next() {
    state = (state + 0x6d2b79f5) >>> 0;
    let x = Math.imul(state ^ (state >>> 15), 1 | state);
    x = (x + Math.imul(x ^ (x >>> 7), 61 | x)) ^ x;
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
}

// Build the jsfxr parameter set for a kind. Preset kinds consume the patched
// Math.random stream; custom kinds draw from the same stream directly.
function buildParameters(kind) {
  const params = new jsfxr.Params();
  switch (kind) {
    case 'click':
      params.click();
      break;
    case 'impact':
      params.explosion();
      break;
    case 'riser':
      params.powerUp();
      break;
    case 'whoosh': {
      params.wave_type = jsfxr.waveforms.NOISE;
      params.p_base_freq = 0.1 + Math.random() * 0.25;
      params.p_freq_limit = 0;
      params.p_freq_ramp = -0.2 + Math.random() * 0.4;
      params.p_env_attack = 0;
      params.p_env_sustain = 0.3 + Math.random() * 0.4;
      params.p_env_decay = 0.2 + Math.random() * 0.3;
      params.p_lpf_freq = 0.4 + Math.random() * 0.5;
      params.p_lpf_ramp = -0.4 + Math.random() * 0.3;
      params.p_hpf_freq = 0.1 + Math.random() * 0.3;
      break;
    }
    case 'fall': {
      params.wave_type = Math.random() < 0.5
        ? jsfxr.waveforms.SQUARE
        : jsfxr.waveforms.SAWTOOTH;
      params.p_duty = Math.random() * 0.6;
      params.p_base_freq = 0.5 + Math.random() * 0.3;
      params.p_freq_ramp = -(0.2 + Math.random() * 0.3);
      params.p_env_attack = 0;
      params.p_env_sustain = 0.1 + Math.random() * 0.2;
      params.p_env_decay = 0.2 + Math.random() * 0.3;
      params.p_hpf_freq = Math.random() * 0.3;
      break;
    }
    default:
      throw new Error('Unknown SFX kind: ' + JSON.stringify(kind));
  }
  return params;
}

// Synthesize WAV bytes. Math.random is swapped for a seeded stream only for the
// duration of generation and always restored, even on failure.
function synthesizeWav({ kind, seed, gain }) {
  const originalRandom = Math.random;
  Math.random = mulberry32(seed);
  try {
    const params = buildParameters(kind);
    params.sound_vol = Math.log(gain + 1);
    params.sample_rate = SAMPLE_RATE;
    params.sample_size = SAMPLE_SIZE;
    const wave = sfxr.toWave(params);
    return Buffer.from(wave.wav);
  } finally {
    Math.random = originalRandom;
  }
}

// Parse a PCM WAV from its actual header bytes; throws on RIFF/WAVE/data
// violations or truncated data.
function parseWav(bytes) {
  const buffer = Buffer.isBuffer(bytes) ? bytes : Buffer.from(bytes);
  if (buffer.length < 44) throw new Error('Invalid WAV: too short for a PCM header');
  const ascii = (offset) => buffer.toString('latin1', offset, offset + 4);
  if (ascii(0) !== 'RIFF') throw new Error('Invalid WAV: missing RIFF tag');
  if (ascii(8) !== 'WAVE') throw new Error('Invalid WAV: missing WAVE format');
  const riffSize = buffer.readUInt32LE(4);
  if (riffSize !== buffer.length - 8) {
    throw new Error('Invalid WAV: RIFF size does not match file length');
  }
  let format = null;
  let dataOffset = -1;
  let dataSize = -1;
  let offset = 12;
  while (offset + 8 <= buffer.length) {
    const id = ascii(offset);
    const size = buffer.readUInt32LE(offset + 4);
    const body = offset + 8;
    if (id === 'fmt ') {
      if (size < 16 || body + size > buffer.length) throw new Error('Invalid WAV: bad fmt chunk');
      format = {
        audioFormat: buffer.readUInt16LE(body),
        channels: buffer.readUInt16LE(body + 2),
        sampleRate: buffer.readUInt32LE(body + 4),
        bitsPerSample: buffer.readUInt16LE(body + 14),
      };
    } else if (id === 'data') {
      dataOffset = body;
      dataSize = size;
    }
    offset = body + size + (size & 1);
  }
  if (!format) throw new Error('Invalid WAV: missing fmt chunk');
  if (format.audioFormat !== 1) throw new Error('Invalid WAV: not uncompressed PCM');
  if (dataSize < 0) throw new Error('Invalid WAV: missing data chunk');
  if (dataOffset + dataSize > buffer.length) throw new Error('Invalid WAV: truncated data chunk');
  const bytesPerSample = format.channels * (format.bitsPerSample / 8);
  if (bytesPerSample <= 0 || dataSize % bytesPerSample !== 0) {
    throw new Error('Invalid WAV: data chunk is not sample-aligned');
  }
  const numSamples = dataSize / bytesPerSample;
  return {
    audioFormat: format.audioFormat,
    channels: format.channels,
    sampleRate: format.sampleRate,
    bitsPerSample: format.bitsPerSample,
    dataOffset,
    dataSize,
    numSamples,
    duration: numSamples / format.sampleRate,
  };
}

// Validate and normalize the params object; rejects unknown fields/types.
function normalizeParams(input) {
  if (input === null || typeof input !== 'object' || Array.isArray(input)) {
    throw new Error('Parameters must be a JSON object');
  }
  for (const key of Object.keys(input)) {
    if (!ALLOWED_FIELDS.has(key)) throw new Error('Unknown SFX parameter: ' + key);
  }
  const { kind } = input;
  if (typeof kind !== 'string' || !KINDS.includes(kind)) {
    throw new Error('Unknown SFX kind: ' + JSON.stringify(kind));
  }
  const seed = input.seed === undefined ? DEFAULT_SEED : input.seed;
  if (typeof seed !== 'number' || !Number.isInteger(seed) || seed < 0 || seed > MAX_SEED) {
    throw new Error('SFX seed must be a nonnegative 31-bit integer');
  }
  const gain = input.gain === undefined ? DEFAULT_GAIN : input.gain;
  if (typeof gain !== 'number' || !Number.isFinite(gain) || gain < 0 || gain > 1) {
    throw new Error('SFX gain must be a finite number in [0, 1]');
  }
  return { kind, seed, gain };
}

function resolveEngineVersion() {
  const require = createRequire(import.meta.url);
  const pkg = require('./vendor/jsfxr/package.json');
  return pkg.version;
}

function ensureAbsent(filePath) {
  try {
    lstatSync(filePath);
  } catch (error) {
    if (error.code === 'ENOENT') return;
    throw error;
  }
  throw new Error('Refusing to overwrite existing path: ' + filePath);
}

// 'wx' == O_CREAT | O_EXCL | O_WRONLY: fails if the path exists, including a
// symlink, so we never write through an existing file, symlink, or hardlink.
function writeExclusive(filePath, bytes) {
  const fd = openSync(filePath, 'wx', 0o644);
  try {
    writeSync(fd, bytes);
  } finally {
    closeSync(fd);
  }
}

function parseArgs(argv) {
  const parsed = {};
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--parameters' || arg === '--output') {
      const value = argv[index + 1];
      if (value === undefined || value.startsWith('--')) {
        throw new Error('Missing value for ' + arg);
      }
      parsed[arg === '--parameters' ? 'parameters' : 'output'] = value;
      index += 1;
    } else {
      throw new Error('Unknown argument: ' + arg);
    }
  }
  if (!parsed.parameters) throw new Error('Missing required --parameters <json>');
  if (!parsed.output) throw new Error('Missing required --output <wav>');
  return parsed;
}

async function generate({ kind, seed, gain }, outputPath) {
  const output = path.resolve(outputPath);
  const metadataPath = output + '.json';
  const parent = path.dirname(output);
  mkdirSync(parent, { recursive: true });
  ensureAbsent(output);
  ensureAbsent(metadataPath);

  const bytes = synthesizeWav({ kind, seed, gain });
  const info = parseWav(bytes);
  const metadata = {
    engine: 'jsfxr',
    engine_version: resolveEngineVersion(),
    parameters: { kind, seed, gain },
    seed,
    wav_sha256: sha256(bytes),
    source_sha256: sha256(await readFile(MODULE_PATH)),
    duration: info.duration,
    duration_source: 'wav_header',
    sample_rate: info.sampleRate,
    bits_per_sample: info.bitsPerSample,
    channels: info.channels,
    num_samples: info.numSamples,
    data_bytes: info.dataSize,
  };

  writeExclusive(output, bytes);
  try {
    writeExclusive(metadataPath, Buffer.from(JSON.stringify(metadata, null, 2) + '\n'));
  } catch (error) {
    try {
      unlinkSync(output);
    } catch {
      // best effort: keep the original error
    }
    throw error;
  }
  return { output, metadata: metadataPath, ...metadata };
}

async function main(argv) {
  const args = parseArgs(argv);
  let raw;
  try {
    raw = await readFile(args.parameters, 'utf8');
  } catch (error) {
    throw new Error('Cannot read parameters file: ' + error.message);
  }
  let input;
  try {
    input = JSON.parse(raw);
  } catch (error) {
    throw new Error('Parameters file is not valid JSON: ' + error.message);
  }
  const result = await generate(normalizeParams(input), args.output);
  process.stdout.write(JSON.stringify(result, null, 2) + '\n');
}

const invokedDirectly = process.argv[1] !== undefined
  && path.resolve(process.argv[1]) === MODULE_PATH;

if (invokedDirectly) {
  main(process.argv.slice(2)).catch((error) => {
    process.stderr.write('error: ' + error.message + '\n');
    process.exitCode = 1;
  });
}

export {
  KINDS,
  DEFAULT_GAIN,
  DEFAULT_SEED,
  MAX_SEED,
  mulberry32,
  buildParameters,
  synthesizeWav,
  parseWav,
  normalizeParams,
  generate,
  main,
};
