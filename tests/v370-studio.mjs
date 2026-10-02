// Native Studio pixel/carry evidence; existing HF_PACKAGE and browser only, no media encoding.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import net from 'node:net';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {fileURLToPath} from 'node:url';
import {probe} from '../.studio/visual_probe.mjs';
const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const {HF_PACKAGE} = process.env;
assert(HF_PACKAGE, 'Set HF_PACKAGE to an existing local runtime');
const root = await fs.mkdtemp(path.join(os.tmpdir(), 'hf-v370-studio-'));
const project = path.join(root, 'fixture'); await fs.mkdir(project);
const cli = path.join(HF_PACKAGE, 'dist/cli.js');
await fs.copyFile(path.join(repo, '.studio/components/script-draft-core/16x9/v1/assets/vendor/gsap/gsap.min.js'), path.join(project, 'gsap.js'));
await fs.writeFile(path.join(project, 'index.html'), `<!doctype html><meta charset="utf-8"><style>
body{margin:0}main{width:640px;height:360px;position:relative;background:white;overflow:hidden}[data-hf-layer]{position:absolute;inset:0}#bg{background:#def}#ip{position:absolute;width:30px;height:30px;left:400px;top:100px;background:orange}.carry{position:absolute;left:40px;top:120px;width:80px;height:80px;background:black}#next{left:80px;opacity:0}#caption{position:absolute;bottom:8px;font:22px sans-serif}
</style><main data-composition-id="fixture" data-width="640" data-height="360" data-duration="4">
<div data-hf-layer="background" id="bg"></div><div data-hf-layer="stage"><canvas id="static" width="160" height="80"></canvas><div id="ip" data-hf-motion="idle"></div><div id="first" class="carry" data-hf-carry="node"></div><div id="next" class="carry" data-hf-carry="node"></div></div><div data-hf-layer="captions"><div id="caption">字幕持续推进</div></div></main>
<script src="gsap.js"></script><script>
const c=document.getElementById('static').getContext('2d');c.fillStyle='#369';c.fillRect(0,0,160,80);
window.__timelines={fixture:gsap.timeline({paused:true}).to('#bg',{x:20,duration:4},0).to('#ip',{y:40,duration:4},0).to('#caption',{x:160,duration:4},0).set('#next',{opacity:0},0).set('#first',{opacity:0},3).set('#next',{opacity:1},3)};
</script>`);
await fs.chmod(path.join(project, 'index.html'), 0o444);
const socket = net.createServer(); socket.listen(0, '127.0.0.1'); await once(socket, 'listening');
const port = socket.address().port; await new Promise(resolve => socket.close(resolve));
let server, log = '';
try {
  server = spawn(process.execPath, [cli, 'preview', project, '--port', String(port), '--foreground', '--no-open', '--no-proxy'],
    {env: {...process.env, DO_NOT_TRACK: '1', HYPERFRAMES_NO_TELEMETRY: '1'}});
  server.stdout.on('data', bytes => {log += bytes;}); server.stderr.on('data', bytes => {log += bytes;});
  const url = `http://127.0.0.1:${port}/#project/fixture`;
  let ready = false;
  for (let i = 0; i < 100; i++) {
    if (server.exitCode !== null) break;
    try {if ((await fetch(url)).ok) {ready = true; break;}} catch {}
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  assert(ready, log);
  const result = await probe({cli, browser: process.env.CHROME_PATH || '/usr/bin/google-chrome', url,
    measurements: true, fps: 60, evidence_dir: path.join(root, 'images'),
    scenes: [{id:'S01', start:0, duration:3}, {id:'S02', start:3, duration:1}], parameters: {width:640, step:.5, timeout_ms:5000}});
  await fs.writeFile(path.join(root, 'probe.json'), JSON.stringify(result));
  assert.equal(result.fps, 30, 'boundary pairs use actual Studio protocol fps, not export fps');
  assert(result.samples.every(s => s.ready), JSON.stringify(result.samples.filter(s => !s.ready)));
  const still = result.samples.filter(s => s.time < 3 && s.still);
  assert(still.length >= 5 && still.every(s => s.still.mean_delta === 0), JSON.stringify(still));
  const before = result.samples.find(s => Math.abs(s.time - (3 - 1/30)) < .000001);
  const after = result.samples.find(s => s.time === 3);
  assert.equal(before.carry.length, 1, JSON.stringify({before,after})); assert.equal(after.carry.length, 1, JSON.stringify({before,after}));
  assert.equal(after.carry[0].box[0] - before.carry[0].box[0], 40);
  assert(await fs.stat(path.join(root, 'images', before.screenshot)));
  assert((await fs.readdir(root, {recursive:true})).every(name => !/\.(mp4|webm|mov)$/i.test(name)));
  console.log(JSON.stringify({nativeStudio: JSON.parse(await fs.readFile(path.join(HF_PACKAGE, 'package.json'))).version, samples:result.samples.length, frozenCanvas:true, carryDelta:40, noVideo:true}));
} finally {
  if (server && server.exitCode === null) {server.kill('SIGTERM'); await once(server, 'exit');}
  await fs.rm(root, {recursive:true, force:true});
}
