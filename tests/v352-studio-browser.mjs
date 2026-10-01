// Real Studio preview-route integration, not UI playback or video acceptance.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import net from 'node:net';
import {once} from 'node:events';
import {spawn, spawnSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {inspectFrame} from '../.studio/visual_probe.mjs';

const {HF_PACKAGE, CHROME_PATH, GSAP_FILE} = process.env;
assert(HF_PACKAGE && CHROME_PATH && GSAP_FILE, 'Set HF_PACKAGE, CHROME_PATH, GSAP_FILE');
assert.equal(JSON.parse(await fs.readFile(path.join(HF_PACKAGE, 'package.json'))).version, '0.8.27');
const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const root = await fs.mkdtemp(path.join(os.tmpdir(), 'hf-v352-studio-'));
const project = path.join(root, 'fixture');
const python = process.env.PYTHON || (process.platform === 'win32' ? 'python' : 'python3');
const runPython = (code, input = '') => {
  const result = spawnSync(python, ['-B', '-c', code, repo, root], {input, encoding: 'utf8', timeout: 30000});
  assert.equal(result.status, 0, result.stderr || result.error?.message);
  return JSON.parse(result.stdout);
};
const setup = runPython(`import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.argv[1])/'.studio'))
import icon_sets as icons,asset_store as store,component_harness as components
root=Path(sys.argv[2]); npm=root/'npm'; project=root/'fixture'
(npm/'icons').mkdir(parents=True); project.mkdir()
(npm/'package.json').write_text(json.dumps(dict(name='lucide-static',version='1.45.0',license='ISC')),encoding='utf-8')
(npm/'LICENSE').write_text('Synthetic test fixture only',encoding='utf-8')
(npm/'icons/test-shape.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M1 2 L21 22"/></svg>',encoding='utf-8')
(project/'index.html').write_text('<main></main>',encoding='utf-8')
icons.import_lucide(npm,root/'source')
candidate=store.pack_source(root/'store',root/'source')
acceptance=store.accept_component(root/'store',candidate['component_ref'],candidate['package_sha256'],'Synthetic fixture',runtime_root=root)
components.install_component(root/'store/packages/lucide-static/v1',project,{'schema_version':3,'component_ref':candidate['component_ref'],'usage':{'role':'icon-set','required':True}},acceptance=acceptance)
icons.use_icon(icons.project_packages(project),'lucide:test-shape@1.45.0',project,'icons/original.svg')
svg=(project/'icons/original.svg').read_text(encoding='utf-8')
(project/'icons/tampered.svg').write_text(svg.replace('M1 2','M9 2'),encoding='utf-8')
print(json.dumps({'svg':svg}))`);
await fs.mkdir(path.join(project, 'runtime'));
await fs.copyFile(path.join(repo, '.studio/runtime/cues.js'), path.join(project, 'runtime/cues.js'));
await fs.copyFile(GSAP_FILE, path.join(project, 'gsap.js'));
await fs.writeFile(path.join(project, 'runtime/cues.json'), JSON.stringify({schema_version: 1, text: 'A',
  characters: [{char: 'A', aligned: true, start: .25, end: .75}]}));
const inline = (id, tampered = false) => setup.svg.replace('<svg ', `<svg id="${id}" `)
  .replace('M1 2', tampered ? 'M9 2' : 'M1 2');
const small = id => `<svg id="${id}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M2 2L22 2L12 22Z"/></svg>`;
await fs.writeFile(path.join(project, 'index.html'), `<!doctype html><html><head><meta charset="utf-8">
<style>html,body{margin:0}main{width:960px;height:540px;background:white;--appearance-colors-text:black}img,svg{width:24px;height:24px;margin:12px}</style>
<script src="gsap.js"></script><script src="runtime/cues.js"></script></head><body>
<main data-composition-id="fixture" data-width="960" data-height="540" data-duration="2">
<img id="img-original" src="icons/original.svg"><img id="img-tampered" src="icons/tampered.svg">
${inline('inline-original')}${inline('inline-tampered', true)}${small('handwritten')}
<span data-hf-schematic>${small('schematic')}</span><span data-card-svg-slot>${small('slot')}</span></main>
<script>window.__timelines={fixture:gsap.timeline({paused:true}).to({},{duration:2})};
HarnessCues.load().then(cues=>window.cueResult={start:cues.find('A'),end:cues.find('A',{edge:'end'})})
.catch(error=>window.cueResult={error:error.message});</script></body></html>`);
const socket = net.createServer();
socket.listen(0, '127.0.0.1'); await once(socket, 'listening');
const port = socket.address().port;
await new Promise(resolve => socket.close(resolve));
let server, browser, log = '';
try {
  const origin = `http://127.0.0.1:${port}`;
  server = spawn(process.execPath, [path.join(HF_PACKAGE, 'dist/cli.js'), 'preview', project,
    '--port', String(port), '--foreground', '--no-open', '--no-proxy'],
  {env: {...process.env, HOME: root, XDG_CONFIG_HOME: root, XDG_CACHE_HOME: root,
    DO_NOT_TRACK: '1', HYPERFRAMES_NO_TELEMETRY: '1'}});
  server.stdout.on('data', data => { log += data; });
  server.stderr.on('data', data => { log += data; });
  let ready = false;
  for (let i = 0; i < 100; i++) {
    try { if ((await fetch(origin, {signal: AbortSignal.timeout(500)})).ok) { ready = true; break; } } catch {}
    if (server.exitCode !== null) break;
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  assert(ready, log);
  const {launch} = createRequire(path.join(HF_PACKAGE, 'package.json'))('puppeteer-core');
  browser = await launch({executablePath: CHROME_PATH, headless: true, timeout: 10000, protocolTimeout: 15000,
    args: process.platform === 'linux' ? ['--no-sandbox'] : []});
  const page = await browser.newPage();
  page.setDefaultTimeout(10000);
  await page.setViewport({width: 1000, height: 600});
  await page.setRequestInterception(true);
  page.on('request', request => {
    const url = new URL(request.url());
    void (['http:', 'https:'].includes(url.protocol) && url.origin !== origin ? request.abort() : request.continue());
  });
  await page.goto(origin + '/api/projects/fixture/preview', {waitUntil: 'load'});
  await page.waitForFunction(() => window.cueResult);
  const state = await page.evaluate(() => ({cue: window.cueResult, base: document.baseURI, location: location.href,
    source: document.querySelector('#img-tampered').getAttribute('src'),
    stampedRoot: document.querySelector('#inline-original').hasAttribute('data-hf-id'),
    stampedPath: document.querySelector('#inline-original path').hasAttribute('data-hf-id')}));
  assert.deepEqual(state.cue, {start: .25, end: .75});
  assert.notEqual(state.base, state.location, 'exercise the Studio-injected base URI');
  assert(state.source.startsWith('data:image/svg+xml;base64,'), 'real Studio converts local SVG into data URL');
  assert(state.stampedRoot && state.stampedPath, 'real Studio injects root and path editing IDs');
  const observed = await page.evaluate(inspectFrame, [], 0);
  assert.equal(observed.icons.length, 7);
  const findings = runPython(`import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.argv[1])/'.studio'))
import icon_sets
project=Path(sys.argv[2])/'fixture'
print(json.dumps(icon_sets.audit_icons(json.load(sys.stdin),icon_sets.project_packages(project))))`, JSON.stringify(observed.icons));
  assert.deepEqual(findings.filter(item => item.code === 'icon_source_mismatch').map(item => item.target).sort(),
    ['#img-tampered', '#inline-tampered']);
  assert.deepEqual(findings.filter(item => item.code === 'unmarked_small_svg').map(item => item.target), ['#handwritten']);
  const evidence = {platform: process.platform, actualStudio: '0.8.27', routeOnly: true,
    state, observed, findings, checks: ['default-cue-base-uri', 'studio-data-svg', 'studio-editor-ids',
      'normal-icons-clean', 'tampered-icons-detected', 'small-svg', 'schematic-slot-exempt']};
  await fs.writeFile(path.join(root, 'evidence.json'), JSON.stringify(evidence, null, 2));
  console.log(JSON.stringify({platform: process.platform, actualStudio: '0.8.27', routeOnly: true,
    checks: evidence.checks, findings: findings.length, evidence: root}));
} finally {
  if (browser) await browser.close();
  if (server && server.exitCode === null) {
    const exited = once(server, 'exit');
    server.kill('SIGTERM');
    const timer = setTimeout(() => server.kill('SIGKILL'), 5000);
    timer.unref();
    await exited; clearTimeout(timer);
  }
  await fs.writeFile(path.join(root, 'studio.log'), log);
}
