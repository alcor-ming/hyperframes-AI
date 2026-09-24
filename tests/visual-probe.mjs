import assert from 'node:assert/strict';
import {changed, defaults, isStill} from '../.studio/visual_probe.mjs';

const pixels = value => Buffer.alloc(30000, value);
const sample = value => ({ready: true, pixels: pixels(value)});
assert(isStill([sample(0), sample(0), sample(0)], defaults));
assert(isStill([sample(0), sample(2), sample(4)], defaults), 'pixel noise');
assert(!isStill([sample(0), sample(8), sample(16)], defaults), 'cumulative slow motion');
assert(!isStill([sample(0), {ready: false}, sample(0)], defaults), 'missing samples are not static');
const corner = pixels(0); corner.fill(255, 0, 30);
assert(!changed(pixels(0), corner, defaults), 'tiny unrelated corner does not count');
console.log('visual probe pixel checks passed');
