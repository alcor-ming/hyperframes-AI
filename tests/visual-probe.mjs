import assert from 'node:assert/strict';
import {defaults, frameResourcesReady} from '../.studio/visual_probe.mjs';

assert.deepEqual(Object.keys(defaults), ['step', 'width', 'timeout_ms'], 'no D2 sampling parameters');

const media = {dataset: {start: '2', mediaStart: '138.68', duration: '10'}, duration: 150,
  defaultPlaybackRate: 1, tagName: 'VIDEO', loop: false, readyState: 2, seeking: false, currentTime: 139.68,
  hasAttribute: name => name === 'data-start'};
globalThis.document = {readyState: 'complete', fonts: {status: 'loaded'}, images: [], querySelectorAll: () => [media]};
assert(frameResourcesReady(3), 'nonzero media offset');
media.currentTime = 1;
assert(!frameResourcesReady(3), 'unadjusted media time must not be ready');
media.dataset.playbackStart = '140'; media.dataset.playbackRate = '2'; media.currentTime = 142;
assert(frameResourcesReady(3), 'playback-start wins; playback-rate scales elapsed time');
media.loop = true; media.currentTime = 144;
assert(frameResourcesReady(9), 'loop wraps within [mediaStart, sourceDuration), not from zero');
delete media.dataset.duration; media.seeking = true;
assert(frameResourcesReady(7), 'default duration uses remaining media divided by rate, even when looping');
assert(!frameResourcesReady(6), 'active unready media still fails');
media.seeking = false; media.loop = false; media.dataset.playbackRate = '100'; media.currentTime = 145;
assert(frameResourcesReady(3), 'rate upper clamp');
media.dataset.playbackRate = '0.01'; media.currentTime = 140.1;
assert(frameResourcesReady(3), 'rate lower clamp');
media.dataset.playbackRate = 'invalid'; media.defaultPlaybackRate = 2; media.currentTime = 142;
assert(frameResourcesReady(3), 'invalid declared rate uses defaultPlaybackRate');
media.dataset.playbackStart = '-1'; media.currentTime = 140.68;
assert(frameResourcesReady(3), 'invalid playback-start falls back to media-start');
media.dataset.duration = '20'; media.currentTime = 150;
assert(frameResourcesReady(10), 'non-looping video holds its last frame');
delete globalThis.document;
console.log('visual probe media timing checks passed');
