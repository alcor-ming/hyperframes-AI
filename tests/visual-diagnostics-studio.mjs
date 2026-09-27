// Isolated native Studio, no WorkStore and no rendering/encoding paths.
// HF_PACKAGE, CHROME_PATH and VIDEO_FIXTURE point to existing local dependencies.
// VIDEO_FIXTURE: existing moving video of at least 5s, not generated/encoded here.
// Verified with https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import net from 'node:net';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {probe} from '../.studio/visual_probe.mjs';

const {HF_PACKAGE, CHROME_PATH, VIDEO_FIXTURE} = process.env;
assert(HF_PACKAGE && CHROME_PATH, 'Set HF_PACKAGE and CHROME_PATH');
assert.equal(JSON.parse(await fs.readFile(path.join(HF_PACKAGE, 'package.json'))).version, '0.8.27');
const root = await fs.mkdtemp(path.join(os.tmpdir(), 'hf-visual-diagnostics-'));
const project = path.join(root, 'fixture');
await fs.mkdir(project);
await fs.copyFile(process.env.GSAP_FILE || path.join(HF_PACKAGE, '../gsap/dist/gsap.min.js'), path.join(project, 'gsap.js'));
const videoFile = 'video' + path.extname(VIDEO_FIXTURE || 'video.webm');
if (VIDEO_FIXTURE) await fs.copyFile(VIDEO_FIXTURE, path.join(project, videoFile));
const socket = net.createServer(); socket.listen(0, '127.0.0.1'); await once(socket, 'listening');
const port = socket.address().port; await new Promise(resolve => socket.close(resolve));
const cli = path.join(HF_PACKAGE, 'dist/cli.js');
let server, log = '';
const checks = [];
async function source(mode) {
  const video = mode.startsWith('video');
  const duration = video ? 2.5 : 4;
  const mediaTiming = {
    'video-offset': 'data-media-start="0.5" data-playback-rate="1.5" data-duration="2.5"',
    'video-loop': 'data-media-start="4" data-playback-rate="2" data-duration="2.5" loop',
    'video-default-duration': 'data-media-start="4" data-playback-rate="2"',
  }[mode] || 'data-duration="2.5"';
  const actions = {
    static: '.to({}, {duration:4})',
    short: '.to("#block", {x:50,duration:.4}).to({}, {duration:3.6})',
    slow: '.to("#block", {x:60,duration:4,ease:"none"})',
    periodic: '.to("#block", {x:250,duration:.25,ease:"none",repeat:15,yoyo:true})',
    corner: '.to("#corner", {opacity:0,duration:.25,repeat:15,yoyo:true})',
    noise: '.to("main", {backgroundColor:"rgb(246,246,246)",duration:.25,repeat:15,yoyo:true})',
    video: '.to({}, {duration:2.5})',
    broken: '.to({}, {duration:4})',
    transition: '.to({}, {duration:4})',
  }[mode] || (video ? '.to({}, {duration:2.5})' : '');
  await fs.writeFile(path.join(project, 'index.html'), `<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;width:100%;height:100%;overflow:hidden}main{position:relative;width:960px;height:540px;background:rgb(250,250,250)}
#block{position:absolute;width:250px;height:250px;left:100px;top:180px;background:#dd3155}#corner{position:absolute;right:0;top:0;width:5px;height:5px;background:#000}
p{position:absolute;font:26px Arial;left:100px;top:30px}video{position:absolute;width:960px;height:540px;object-fit:cover}.hidden{opacity:0}
</style></head><body><main data-composition-id="fixture" data-width="960" data-height="540" data-duration="${duration}"${mode === 'video-native' ? ' data-no-timeline="true"' : ''}>
<section data-scene-id="S01" class="clip" data-start="0" data-duration="${mode === 'transition' ? 2 : duration}"><p data-info-id="I01">Visible text <span>continues here.</span></p><p class="hidden">Hidden text must not appear.</p><div id="block"></div><div id="corner"></div>
<svg width="300" height="100" style="position:absolute;left:400px;top:100px"><text x="0" y="40">SVG evidence</text></svg></section>
${mode === 'transition' ? '<section class="clip" data-scene-id="S02" data-start="2" data-duration="2"><p>Visible text <span>continues here.</span></p><div style="position:absolute;width:250px;height:250px;left:100px;top:180px;background:#dd3155"></div><svg width="300" height="100" style="position:absolute;left:400px;top:100px"><text x="0" y="40">SVG evidence</text></svg></section>' : ''}
${video ? `<video src="${videoFile}" muted preload="auto" data-start="0" ${mediaTiming} data-track-index="1"></video>` : ''}
${mode === 'broken' ? '<img src="missing.png">' : ''}
</main>${mode === 'video-native' ? '' : `<script src="gsap.js"></script><script>window.__timelines={fixture:gsap.timeline({paused:true})${actions}};</script>`}</body></html>`);
}
try {
  const url = `http://127.0.0.1:${port}/#project/fixture`;
  for (const mode of ['static', 'short', 'slow', 'periodic', 'corner', 'noise', 'transition', 'broken',
    ...(VIDEO_FIXTURE ? ['video', 'video-native', 'video-offset', 'video-loop', 'video-default-duration'] : [])]
    .filter(mode => !process.env.PROBE_MODES || process.env.PROBE_MODES.split(',').includes(mode))) {
    await source(mode);
    server = spawn(process.execPath, [cli, 'preview', project, '--port', String(port), '--foreground', '--no-open', '--no-proxy'],
      {env: {...process.env, HOME: root, XDG_CONFIG_HOME: root, XDG_CACHE_HOME: root, DO_NOT_TRACK: '1', HYPERFRAMES_NO_TELEMETRY: '1'}});
    server.stdout.on('data', data => { log += data; }); server.stderr.on('data', data => { log += data; });
    let ready = false;
    for (let i = 0; i < 100; i++) {
      try { if ((await fetch(url)).ok) { ready = true; break; } } catch {}
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    assert(ready, log);
    const report = await probe({cli, browser: CHROME_PATH, url,
      scenes: mode === 'transition' ? [{id: 'S01', start: 0, duration: 2}, {id: 'S02', start: 2, duration: 2}]
        : [{id: 'S01', start: 0, duration: mode.startsWith('video') ? 2.5 : 4}], parameters: {timeout_ms: mode === 'broken' ? 300 : 10000}});
    await fs.writeFile(path.join(root, mode + '.json'), JSON.stringify(report, null, 2));
    if (mode === 'broken') {
      assert(report.samples.every(item => !item.ready)); assert.equal(report.motion.length, 0);
    } else {
      assert(report.samples.every(item => item.ready), `${mode}: ${JSON.stringify(report.samples.filter(item => !item.ready))}`);
      if (mode !== 'video-default-duration')
        assert.equal(report.motion.length > 0, ['static', 'short', 'corner', 'noise', 'transition'].includes(mode), `${mode}: ${JSON.stringify(report.motion)}`);
      if (mode === 'static') assert.equal(report.motion[0].start, 0, 'opening static');
      if (mode === 'short') assert(report.motion.some(item => item.start >= .4 && item.end > 3), 'in-scene static after short tween');
      if (mode === 'transition') assert(report.motion.some(item => item.start <= 1 && item.end >= 3), 'static across scene boundary');
      if (!mode.startsWith('video')) {
        const text = report.samples.flatMap(item => item.texts).map(item => item.text).join(' ');
        assert(text.includes('Visible text') && text.includes('SVG evidence'));
        assert(!text.includes('Hidden text'));
      }
    }
    checks.push({mode, samples: report.samples.length, motion: report.motion});
    server.kill('SIGTERM'); await once(server, 'exit'); server = null;
  }
  console.log(JSON.stringify({platform: process.platform, actualStudio: '0.8.27', viewport: {width: 960, height: 540},
    checks, realVideo: !!VIDEO_FIXTURE, evidence: root}));
} finally {
  if (server && server.exitCode === null) { server.kill('SIGTERM'); await once(server, 'exit'); }
}
