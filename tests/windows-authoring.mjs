// Windows-native M1 smoke test. Synthetic Review state is not production acceptance.
// Run the installed copy with the pinned runtime/node/node.exe and SESSION_DIR only.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';

assert.equal(process.platform, 'win32', 'This check must execute on native Windows');
const sessionDir = process.env.SESSION_DIR;
assert(sessionDir && path.isAbsolute(sessionDir), 'SESSION_DIR must name an absolute, bound Review session');
const readJSON = async file => JSON.parse((await fs.readFile(file, 'utf8')).replace(/^\uFEFF/, ''));
const session = await readJSON(path.join(sessionDir, 'session.json'));
const config = await readJSON(path.join(sessionDir, 'local.json'));
assert.equal(session.review, true, 'Never run this fixture in a production session');
const runtime = session.release_root, root = config.work_root, assetRoot = config.asset_review_root;
assert(runtime && root && assetRoot && [runtime, root, assetRoot].every(path.isAbsolute));
assert.equal(await fs.realpath(fileURLToPath(import.meta.url)),
  await fs.realpath(path.join(runtime, 'tests/windows-authoring.mjs')), 'Use the immutable installed fixture');
assert.equal(await fs.realpath(process.execPath), await fs.realpath(path.join(runtime, 'runtime/node/node.exe')));
assert.equal((await readJSON(path.join(root, '.runtime/review.json'))).mode, 'review');
assert.equal(path.resolve(config.asset_root), path.resolve(assetRoot, 'store'));
assert(config.asset_source_roots.some(source => path.resolve(source) === path.resolve(assetRoot, 'sources')));
const hf = path.join(runtime, 'runtime/npm/node_modules/hyperframes');
const require = createRequire(path.join(hf, 'package.json'));
const puppeteer = require('puppeteer-core'), sharp = require('sharp');
const command = path.join(sessionDir, 'work.cmd');
const env = {...process.env, DO_NOT_TRACK: '1', HYPERFRAMES_NO_TELEMETRY: '1'};
function invoke(args, additions = {}, expectedSuccess = true) {
  const quote = value => {
    assert.equal(typeof value, 'string');
    assert(!/["\r\n%]/.test(value), 'Unsafe cmd.exe fixture argument');
    return `"${value}"`;
  };
  const result = spawnSync(process.env.ComSpec || 'cmd.exe',
    ['/d', '/s', '/c', `"${[command, ...args].map(quote).join(' ')}"`],
    {env: {...env, ...additions}, encoding: 'utf8', windowsVerbatimArguments: true,
      timeout: 300000, maxBuffer: 8 * 1024 * 1024});
  if (expectedSuccess) assert.equal(result.status, 0,
    `${args.join(' ')}\n${result.error || ''}\n${result.stderr}\n${result.stdout}`);
  return result;
}
const work = (...args) => invoke(args).stdout.trim();
const output = await fs.mkdtemp(path.join(root, '.runtime/native-authoring-'));
const evidence = {technicalFixture: true, platform: process.platform, runtime, session: session.id,
  workRoot: root, assetRoot, output, sessions: [], assets: [], seeks: [], images: [],
  errors: [], externalRequests: [], passed: false};
const opened = [];
let browser, page, id;
const run = (...args) => work('--work', id, '--variant', 'main', ...args);
async function header(file, changes, append = '') {
  const text = await fs.readFile(file, 'utf8');
  const match = /^---\r?\n([\s\S]*?)\r?\n---/.exec(text);
  assert(match, 'Synthetic fixture expects JSON front matter');
  const metadata = {...JSON.parse(match[1]), ...changes};
  await fs.writeFile(file, `---\n${JSON.stringify(metadata)}\n---${text.slice(match[0].length)}${append}`, 'utf8');
}
async function open(target) {
  const record = JSON.parse(run('preview', 'open', target, '--no-open'));
  opened.push(target); evidence.sessions.push(record);
  assert.equal(record.work, id);
  assert.equal(record.variant, 'main');
  assert.equal(record.target, target);
  assert.equal(new URL(record.url).port, String(record.port));
  assert(new URL(record.url).hash.startsWith('#project/'), 'Must open the official Studio project');
  assert.equal((await readJSON(path.join(record.browser_profile, 'Default/Preferences'))).enable_do_not_track, true);
  return record;
}
async function show(record) {
  await page.goto(record.url, {waitUntil: 'domcontentloaded'});
  assert.equal(await page.evaluate(() => navigator.doNotTrack), '1');
  const iframe = (await page.waitForFunction(() =>
    document.querySelector('hyperframes-player')?.shadowRoot?.querySelector('iframe'),
  {timeout: 30000})).asElement();
  assert(iframe, 'Official player iframe must be available in its shadow root');
  const frame = await iframe.contentFrame();
  assert(frame, 'Official Studio must host the actual composition iframe');
  await frame.waitForSelector('#fixture-title', {visible: true, timeout: 30000});
  await frame.waitForFunction(() => window.__timelines?.['m1-native'] &&
    [...document.querySelectorAll('img')].every(image => image.complete && image.naturalWidth > 0));
  return {iframe, frame};
}
async function pixels(iframe, label) {
  const {data, info} = await sharp(await iframe.screenshot()).removeAlpha().raw().toBuffer({resolveWithObject: true});
  let teal = 0, pink = 0, amber = 0;
  for (let offset = 0; offset < data.length; offset += info.channels) {
    const [r, g, b] = data.subarray(offset, offset + 3);
    if (r < 70 && g > 100 && b > 60 && g > b) teal++;
    if (r > 150 && g < 140 && b > 60 && r > b) pink++;
    if (r > 180 && g > 130 && b < 100) amber++;
  }
  assert(teal > 30 && pink > 30 && amber > 30, `${label} must contain actual module and raster pixels`);
  await page.screenshot({path: path.join(output, `${label}.png`), fullPage: true});
  return {label, width: info.width, height: info.height, teal, pink, amber};
}
try {
  const doctor = JSON.parse(work('doctor'));
  const polluted = JSON.parse(invoke(['doctor'], {
    HYPERFRAMES_AI_ASSET_ROOT: path.join(output, 'unused-store'),
    HYPERFRAMES_AI_ASSET_CONFIG: path.join(output, 'unused-assets.json'),
    HYPERFRAMES_AI_CONFIG: path.join(output, 'unused-config.json'),
    HYPERFRAMES_AI_WORK_ROOT: path.join(output, 'unused-work'),
  }).stdout);
  assert.deepEqual(polluted, doctor, 'Inherited root/config variables must not redirect a bound session');
  assert.equal(doctor.backend, 'windows-native');
  assert.equal(doctor.review, true);
  assert.equal(path.resolve(doctor.runtime), path.resolve(runtime));
  assert.equal(path.resolve(doctor.work_root), path.resolve(root));
  assert.equal(path.resolve(doctor.asset_root), path.resolve(config.asset_root));
  assert(Object.values(doctor.checks).every(value =>
    typeof value === 'string' ? value === 'available' : value.status === 'available'), 'Pinned doctor dependencies must all be available');
  evidence.doctor = doctor;
  evidence.environmentPollutionIgnored = true;
  id = work('new', 'M1 native authoring technical fixture', '--workflow', 'hyperframes_video', '--detached');
  evidence.work = id;
  const variant = path.join(root, 'works/active', id, 'variants/main');
  const project = path.join(variant, 'project');
  const sources = await fs.mkdtemp(path.join(assetRoot, 'sources/native-m1-'));
  const suffix = path.basename(sources).slice('native-m1-'.length).toLowerCase();
  const moduleId = `m1-nudge-${suffix}`, mediaId = `m1-media-${suffix}`;
  const moduleRef = `${moduleId}@v1`, mediaRef = `${mediaId}@v1`;
  for (const name of ['module', 'media']) await fs.mkdir(path.join(sources, name));
  await fs.writeFile(path.join(sources, 'module/nudge.js'),
    'window.fixtureNudge = (timeline, target, amount) => timeline.fromTo(target, {x:0}, {x:amount,duration:1.5,ease:"none"}, 0);\n');
  await fs.writeFile(path.join(sources, 'module/asset.json'), JSON.stringify({schema_version: 1,
    id: moduleId, version: 1, kind: 'module', entry: 'nudge.js',
    runtime: {versions: {gsap: session.runtime.versions.gsap}}}));
  const raster = Buffer.alloc(320 * 180 * 3);
  for (let y = 0; y < 180; y++) for (let x = 0; x < 320; x++) {
    const color = x > 50 && x < 270 && y > 35 && y < 145 ? [232, 184, 62] : [32, 108, 89];
    raster.set(color, (y * 320 + x) * 3);
  }
  await sharp(raster, {raw: {width: 320, height: 180, channels: 3}}).png().toFile(path.join(sources, 'media/evidence.png'));
  await fs.writeFile(path.join(sources, 'media/icon.svg'),
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect x="4" y="4" width="56" height="56" rx="6" fill="#cf5068"/><path d="M18 32l9 9 20-20" fill="none" stroke="white" stroke-width="6"/></svg>');
  await fs.writeFile(path.join(sources, 'media/asset.json'), JSON.stringify({schema_version: 1,
    id: mediaId, version: 1, kind: 'media', entry: 'evidence.png', dependencies: ['icon.svg'],
    source: 'Synthetic raster and SVG authored by this technical fixture; no private media.'}));
  // These states belong only to the generated technical Work, not a user's content decision.
  await header(path.join(variant, 'RESEARCH.md'), {status: 'ready'});
  await header(path.join(variant, 'ANIMATION_PLAN.md'), {status: 'approved'},
    `\nSynthetic Review simulation only. Exact fixture assets: \`${moduleRef}\`, \`${mediaRef}\`.\n`);
  await fs.mkdir(path.join(project, 'assets'), {recursive: true});
  await fs.mkdir(path.join(project, 'compositions'), {recursive: true});
  await fs.writeFile(path.join(project, 'DESIGN.md'), 'Synthetic M1 authoring integration fixture. No production acceptance.\n');
  await fs.writeFile(path.join(project, 'project-config.json'), '{}\n');
  for (const [name, ref, role] of [['module', moduleRef, 'auxiliary'], ['media', mediaRef, 'subject']]) {
    const candidate = JSON.parse(work('component', 'pack', path.join(sources, name)));
    assert.equal(candidate.component_ref, ref);
    const acceptance = JSON.parse(work('component', 'accept', ref, '--sha256', candidate.package_sha256,
      '--note', 'Synthetic Review simulation for M1 native technical fixture; not user or production acceptance'));
    assert(acceptance.review, 'Technical acceptance must remain marked as Review-only');
    const binding = path.join(output, `${name}-binding.json`);
    await fs.writeFile(binding, JSON.stringify({schema_version: 3, component_ref: ref, scene: 'S01', usage: {role, required: true}}));
    const installed = JSON.parse(run('component', 'install', ref, '--binding', binding));
    evidence.assets.push({candidate, acceptance, installed});
  }
  for (const name of ['gsap.min.js', 'MotionPathPlugin.min.js'])
    await fs.copyFile(path.join(runtime, 'runtime/npm/node_modules/gsap/dist', name), path.join(project, 'assets', name));
  await fs.writeFile(path.join(project, 'index.html'), `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>M1 native fixture</title>
<style>*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;font-family:Arial,sans-serif;letter-spacing:0}main{position:relative;width:960px;height:540px;background:#eef3f1;color:#162725}h1{position:absolute;top:36px;left:48px;margin:0;font-size:34px}.raster{position:absolute;left:48px;top:124px;width:416px;height:234px}.node{position:absolute;left:536px;width:112px;height:96px;border-radius:6px;background:#188b72;color:white;display:grid;place-items:center;font-size:26px}#instance-a{top:134px}#instance-b{top:272px;background:#cf5068}.icon{position:absolute;left:784px;top:398px;width:64px;height:64px}p{position:absolute;left:48px;top:410px;font-size:22px;margin:0}</style></head><body>
<main data-composition-id="m1-native" data-width="960" data-height="540" data-start="0" data-duration="2"><section id="S01" class="clip" data-start="0" data-duration="2" data-track-index="0"><h1 id="fixture-title">M1 native technical fixture</h1><img class="raster" alt="Synthetic amber evidence raster" src="vendor/components/${mediaId}/v1/evidence.png"><div class="node" id="instance-a">A</div><div class="node" id="instance-b">B</div><img class="icon" alt="Local SVG check" src="vendor/components/${mediaId}/v1/icon.svg"><p>Local raster + SVG + two independent instances</p></section></main>
<script src="assets/gsap.min.js"></script><script src="assets/MotionPathPlugin.min.js"></script><script src="vendor/components/${moduleId}/v1/nudge.js"></script><script>const timeline=gsap.timeline({paused:true});window.fixtureNudge(timeline,document.getElementById('instance-a'),120);window.fixtureNudge(timeline,document.getElementById('instance-b'),-70);timeline.to({},{duration:.5},1.5);window.__timelines={'m1-native':timeline};</script></body></html>`, 'utf8');
  evidence.installation = JSON.parse(run('component', 'verify'));
  const current = await open('current');
  evidence.studioURL = current.url;
  // Studio uses installed Chrome preferences; the pinned headless shell is for rendering.
  browser = await puppeteer.launch({channel: 'chrome',
    userDataDir: current.browser_profile, headless: true, env,
    args: ['--disable-background-networking', '--disable-component-update', '--disable-sync', '--no-first-run']});
  evidence.studioBrowser = {executable: browser.process().spawnfile, version: await browser.version()};
  page = await browser.newPage();
  page.on('pageerror', error => evidence.errors.push(error.message));
  await page.setRequestInterception(true);
  page.on('request', request => {
    const url = new URL(request.url());
    if (['http:', 'https:'].includes(url.protocol) && !['localhost', '127.0.0.1', '[::1]'].includes(url.hostname)) {
      evidence.externalRequests.push(request.url());
      void request.abort().catch(error => evidence.errors.push(error.message));
    } else void request.continue().catch(error => evidence.errors.push(error.message));
  });
  await page.setViewport({width: 1440, height: 1000, deviceScaleFactor: 1});
  const {iframe, frame} = await show(current);
  evidence.images = await frame.$$eval('img', images => images.map(image =>
    ({src: image.getAttribute('src'), width: image.naturalWidth, height: image.naturalHeight})));
  assert.equal(evidence.images.length, 2);
  assert(evidence.images.every(image => image.width > 0 && image.height > 0));
  for (const time of [1.5, 0, 0.5, 1.5]) {
    await page.$eval('hyperframes-player', (player, value) => { player.pause(); player.seek(value); }, time);
    await frame.waitForFunction(value => Math.abs(window.__timelines['m1-native'].time() - value) < 0.001, {}, time);
    const nodes = await frame.evaluate(() => ['instance-a', 'instance-b'].map(id => {
      const element = document.getElementById(id);
      return {id, x: Number(gsap.getProperty(element, 'x')), transform: element.style.transform};
    }));
    evidence.seeks.push({time, nodes});
  }
  assert.deepEqual(evidence.seeks[0], evidence.seeks[3], 'Backward and repeated seek must produce identical DOM state');
  assert.deepEqual(evidence.seeks[1].nodes.map(node => node.x), [0, 0]);
  assert.deepEqual(evidence.seeks[0].nodes.map(node => node.x), [120, -70]);
  assert(evidence.seeks[2].nodes[0].x > 0 && evidence.seeks[2].nodes[0].x < 120);
  assert(evidence.seeks[2].nodes[1].x < 0 && evidence.seeks[2].nodes[1].x > -70);
  evidence.pixels = [await pixels(iframe, 'desktop')];
  await page.setViewport({width: 390, height: 844, deviceScaleFactor: 1});
  evidence.pixels.push(await pixels(iframe, 'mobile-390'));
  const plan = run('preview', 'register', '--purpose', 'plan', '--kind', 'executable');
  const registered = await open(plan);
  await page.setViewport({width: 1440, height: 1000, deviceScaleFactor: 1});
  await show(registered);
  assert.notEqual(path.resolve(registered.project), path.resolve(variant, 'previews', plan, 'source-snapshot'));
  const video = path.join(variant, 'm1-smoke.mp4');
  run('preview', 'render', plan, '--output', video, '--fps', '6', '--software-gl');
  assert((await fs.stat(video)).size > 1000, 'Require a real rendered MP4');
  const probe = spawnSync(path.join(runtime, 'runtime/ffmpeg/bin/ffprobe.exe'),
    ['-v', 'error', '-show_streams', '-show_format', '-of', 'json', video], {encoding: 'utf8', timeout: 30000, env});
  assert.equal(probe.status, 0, probe.stderr || String(probe.error || 'ffprobe failed'));
  evidence.video = {path: video, ...JSON.parse(probe.stdout)};
  const stream = evidence.video.streams.find(item => item.codec_type === 'video');
  assert(stream && stream.width === 960 && stream.height === 540 && Number(evidence.video.format.duration) >= 1.8);
  assert.deepEqual(evidence.errors, [], 'Official Studio browser errors');
  assert.deepEqual(evidence.externalRequests, [], 'DNT/local assets must prevent external requests, not merely block them');
  evidence.passed = true;
} catch (error) {
  evidence.failure = error.stack;
  if (page) await page.screenshot({path: path.join(output, 'failure.png'), fullPage: true}).catch(() => {});
  throw error;
} finally {
  evidence.cleanupErrors = [];
  try { if (browser) await browser.close(); } catch (error) { evidence.cleanupErrors.push(error.message); }
  for (const target of opened.reverse()) {
    const result = invoke(['--work', id, '--variant', 'main', 'preview', 'stop', target], {}, false);
    if (result.status !== 0) evidence.cleanupErrors.push(`${target}: ${result.stderr || result.stdout}`);
  }
  if (evidence.cleanupErrors.length) evidence.passed = false;
  const report = path.join(output, 'verification.json');
  await fs.writeFile(report, JSON.stringify(evidence, null, 2));
  console.log(JSON.stringify({passed: evidence.passed, report, work: id, studioURL: evidence.studioURL}));
  assert.deepEqual(evidence.cleanupErrors, [], 'Stop every fixture browser and Studio');
}
