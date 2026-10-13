// Direct-root NORMAL-chain isolated acceptance fixture. Synthetic fixture Work only; never
// production acceptance, never a Review session. Copy this fixture to the isolated root's
// .studio/.runtime/acceptance directory and run it with pinned runtime node and --root <abs>.
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';

assert.equal(process.platform, 'win32', 'This check must execute on native Windows');
// Refuse an inherited Review session binding before touching or clearing any environment.
assert(!process.env.SESSION_DIR && !process.env.HYPERFRAMES_AI_SESSION,
  'Reject inherited SESSION_DIR/HYPERFRAMES_AI_SESSION; this fixture runs from an explicit --root');
const argv = process.argv.slice(2);
assert.equal(argv[0], '--root', 'Usage: windows-authoring.mjs --root <absolute installed root>');
assert.equal(argv.length, 2, 'Only --root <absolute installed root> is accepted; no implicit or environment default');
const root = argv[1];
assert(root && path.isAbsolute(root), '--root must be an absolute installed root');

const readJSON = async file => JSON.parse((await fs.readFile(file, 'utf8')).replace(/^\uFEFF/, ''));
const writeJSON = async (file, value) => fs.writeFile(file, JSON.stringify(value, null, 2) + '\n', 'utf8');
const sha256 = async file => crypto.createHash('sha256').update(await fs.readFile(file)).digest('hex');
const within = (child, parent) => {
  const relative = path.relative(path.resolve(parent), path.resolve(child));
  return relative === '' || (!relative.startsWith('..') && !path.isAbsolute(relative));
};
async function frontmatter(file) {
  const match = /^---\r?\n([\s\S]*?)\r?\n---/.exec(await fs.readFile(file, 'utf8'));
  assert(match, `Fixture expects JSON front matter in ${file}`);
  return JSON.parse(match[1]);
}
async function writeDocument(file, metadata, body) {
  await fs.writeFile(file, `---\n${JSON.stringify(metadata)}\n---\n${body}`, 'utf8');
}

// Test fixtures stay outside product packages, in the explicitly isolated runtime directory.
assert.equal(await fs.realpath(fileURLToPath(import.meta.url)),
  await fs.realpath(path.join(root, '.studio/.runtime/acceptance/windows-authoring.mjs')), 'Run the isolated acceptance fixture');
assert.equal(await fs.realpath(process.execPath),
  await fs.realpath(path.join(root, 'runtime/node/node.exe')), 'Use the pinned runtime/node/node.exe');

// Direct-root acceptance contract: local channel, non-Review configuration, protected roots.
const release = await readJSON(path.join(root, '.release.json'));
assert.equal(release.channel, 'local', 'Direct-root acceptance requires a local-channel package');
const runtimeLock = await readJSON(path.join(root, 'windows-runtime.lock.json'));
const localPath = path.join(root, '.studio/.runtime/local.json');
const localConfig = await readJSON(localPath);
assert.equal(localConfig.review, false, 'Acceptance root must not be a Review configuration');
assert(Array.isArray(localConfig.acceptance_protected_roots) && localConfig.acceptance_protected_roots.length
  && localConfig.acceptance_protected_roots.every(item => typeof item === 'string' && path.isAbsolute(item)),
  'Acceptance requires explicit absolute acceptance_protected_roots');

// Canonical configuration first: locked Python resolves link/overlap/isolation before any mutation.
const python = path.join(root, 'runtime/python/python.exe');
const baseEnv = {...process.env, DO_NOT_TRACK: '1', HYPERFRAMES_NO_TELEMETRY: '1', PYTHONUTF8: '1', PYTHONDONTWRITEBYTECODE: '1'};
for (const key of Object.keys(baseEnv)) {
  if (key.toUpperCase().startsWith('HYPERFRAMES_AI_') || key === 'SESSION_DIR') delete baseEnv[key];
}
function pythonJson(code) {
  const result = spawnSync(python, ['-B', '-c', code],
    {env: baseEnv, encoding: 'utf8', timeout: 120000, maxBuffer: 8 * 1024 * 1024});
  assert.equal(result.status, 0, result.stderr || result.stdout || String(result.error || 'native Python failed'));
  return result.stdout.trim();
}
const canonicalCode = [
  'import json, sys',
  'from pathlib import Path',
  `root = Path(${JSON.stringify(root)})`,
  "sys.path.insert(0, str(root / '.studio'))",
  'import windows_runtime',
  'with windows_runtime.command_lock(root):',
  '    config = windows_runtime.resolved_config(root)',
  'print(json.dumps(config, ensure_ascii=False))',
].join('\n');
const resolved = JSON.parse(pythonJson(canonicalCode));
assert.equal(resolved.review, false, 'Canonical configuration must stay non-Review');
const deployment = JSON.parse(pythonJson([
  'import json, sys',
  'from pathlib import Path',
  `root = Path(${JSON.stringify(root)})`,
  "sys.path.insert(0, str(root / '.studio'))",
  'import root_deploy',
  'print(json.dumps(root_deploy.verify_root(root), ensure_ascii=False))',
].join('\n')));
assert(deployment.files && Object.keys(deployment.files).length, 'root_deploy verify-root must report managed files');
for (const key of ['work_root', 'asset_root']) {
  assert(resolved[key] && path.isAbsolute(resolved[key]) && within(resolved[key], root),
    `Resolved ${key} must remain inside the explicit root`);
}
assert(Array.isArray(resolved.asset_source_roots) && resolved.asset_source_roots.length
  && resolved.asset_source_roots.every(item => path.isAbsolute(item) && within(item, root)),
  'Resolved asset_source_roots must be absolute and inside the explicit root');
const exportRoot = path.resolve(resolved.export_root || path.join(root, 'exports'));
assert(within(exportRoot, root), 'Export root must remain inside the explicit root');

// Fixture evidence lives beside the runtime; it is never production acceptance.
const suffix = crypto.randomBytes(5).toString('hex');
const output = await fs.mkdtemp(path.join(root, '.studio/.runtime/native-acceptance-'));
const commands = [];
const evidence = {
  technicalFixture: true, productionAcceptance: false, review: false, platform: process.platform,
  root, suffix, release: release.release, releaseChannel: release.channel, output,
  fixtureSha256: await sha256(fileURLToPath(import.meta.url)),
  config: {work_root: resolved.work_root, asset_root: resolved.asset_root,
    asset_source_roots: resolved.asset_source_roots, export_root: exportRoot,
    acceptance_protected_roots: resolved.acceptance_protected_roots},
  hashes: {release: await sha256(path.join(root, '.release.json')), local: await sha256(localPath),
    deployment: await sha256(path.join(root, '.studio/.runtime/deployment.json')),
    runtime_lock: await sha256(path.join(root, 'windows-runtime.lock.json'))},
  commands, sessions: [], assets: [], seeks: [], images: [], errors: [], externalRequests: [],
  silent: true, audioRequired: false, passed: false,
};

const hf = path.join(root, 'runtime/npm/node_modules/hyperframes');
const require = createRequire(path.join(hf, 'package.json'));
const puppeteer = require('puppeteer-core');
const sharp = require('sharp');
const command = path.join(root, 'work.cmd');
function invoke(args, additions = {}, expectedSuccess = true) {
  const quote = value => {
    assert.equal(typeof value, 'string');
    assert(!/["\r\n%]/.test(value), 'Unsafe cmd.exe fixture argument');
    return `"${value}"`;
  };
  commands.push(args.join(' '));
  const result = spawnSync(process.env.ComSpec || 'cmd.exe',
    ['/d', '/s', '/c', `"${[command, ...args].map(quote).join(' ')}"`],
    {cwd: root, env: {...baseEnv, ...additions}, encoding: 'utf8', windowsVerbatimArguments: true,
      timeout: 600000, maxBuffer: 8 * 1024 * 1024});
  if (expectedSuccess) assert.equal(result.status, 0,
    `${args.join(' ')}\n${result.error || ''}\n${result.stderr}\n${result.stdout}`);
  return result;
}
const work = (...args) => invoke(args).stdout.trim();

let browser, page, id;
const run = (...args) => work('--work', id, '--variant', 'variant1', ...args);
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
  await frame.waitForFunction(() => window.__timelines?.['native-fixture'] &&
    [...document.querySelectorAll('img')].every(image => image.complete && image.naturalWidth > 0),
  {timeout: 30000});
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
async function ffprobe(video) {
  const probe = spawnSync(path.join(root, 'runtime/ffmpeg/bin/ffprobe.exe'),
    ['-v', 'error', '-show_streams', '-show_format', '-of', 'json', video], {encoding: 'utf8', timeout: 60000, env: baseEnv});
  assert.equal(probe.status, 0, probe.stderr || String(probe.error || 'ffprobe failed'));
  return JSON.parse(probe.stdout);
}
const opened = [];
try {
  const doctor = JSON.parse(work('doctor'));
  const polluted = JSON.parse(invoke(['doctor'], {
    HYPERFRAMES_AI_ASSET_ROOT: path.join(output, 'unused-store'),
    HYPERFRAMES_AI_ASSET_CONFIG: path.join(output, 'unused-assets.json'),
    HYPERFRAMES_AI_CONFIG: path.join(output, 'unused-config.json'),
    HYPERFRAMES_AI_WORK_ROOT: path.join(output, 'unused-work'),
  }).stdout);
  assert.deepEqual(polluted, doctor, 'Inherited root/config variables must not redirect an explicit root');
  assert.equal(doctor.backend, 'windows-native');
  assert.equal(doctor.review, false);
  assert.equal(path.resolve(doctor.runtime), root);
  assert.equal(path.resolve(doctor.work_root), path.resolve(resolved.work_root));
  assert.equal(path.resolve(doctor.asset_root), path.resolve(resolved.asset_root));
  assert(Object.values(doctor.checks).every(value =>
    typeof value === 'string' ? value === 'available' : value.status === 'available'),
    'Pinned doctor dependencies must all be available');
  evidence.doctor = doctor;
  evidence.environmentPollutionIgnored = true;

  // Fixture-owned series must exist before a standard (non-test) Work is created.
  const seriesHelp = work('series', 'put', '--help');
  assert(/--file/.test(seriesHelp) && /identity/.test(seriesHelp), 'work series put parser must accept identity --file');
  const seriesId = `native-series-${suffix}`;
  const seriesFile = path.join(output, 'series.json');
  await writeJSON(seriesFile, {name: `Native fixture series ${suffix}`, design: 'collage'});
  const series = JSON.parse(work('series', 'put', seriesId, '--file', seriesFile, '--json'));
  assert.equal(series.id, seriesId);
  assert.equal(series.revision, 1);
  evidence.series = {id: seriesId, revision: series.revision};

  // Silent initial smoke: disable cover/sfx/captions only for this fixture Variant.
  const overridesFile = path.join(output, 'overrides.json');
  await writeJSON(overridesFile, {captions: {enabled: false}, sfx: {enabled: false}, cover: {enabled: false}});

  id = work('new', `Native acceptance fixture ${suffix}`, '--workflow', 'hyperframes_video', '--purpose', 'standard',
    '--series', seriesId, '--no-account', '--design', 'collage', '--variant-id', 'variant1',
    '--overrides', overridesFile, '--detached');
  assert(/^work-hyperframes_video-\d+-/.test(id), `Unexpected Work id: ${id}`);
  evidence.work = id;
  const workDir = path.join(resolved.work_root, 'works/active', id);
  const variant = path.join(workDir, 'variants/variant1');
  const project = path.join(variant, 'project');
  let state = await readJSON(path.join(variant, 'variant.yaml'));
  assert.equal(state.design, 'collage');
  assert.equal(state.ratio, '16:9');
  assert.equal(state.account_selection, 'none');
  assert.equal(state.design_values['cover.enabled'], false);
  assert.equal(state.design_values['sfx.enabled'], false);
  assert.equal(state.design_values['captions.enabled'], false);
  assert.equal(state.plan_revision, 1);
  assert.equal(state.script_revision, 1);
  evidence.variant = {id: 'variant1', path: variant, plan_revision: state.plan_revision, script_revision: state.script_revision};

  // Shared Script/Research resolve through variant.yaml.shared_inputs, never under the Variant.
  const shared = state.shared_inputs;
  assert(shared && shared['SCRIPT.md'] && shared['RESEARCH.md'], 'Variant must declare shared_inputs');
  const scriptPath = path.join(workDir, shared['SCRIPT.md']);
  const researchPath = path.join(workDir, shared['RESEARCH.md']);
  assert(within(scriptPath, workDir) && within(researchPath, workDir));
  await assert.rejects(fs.stat(path.join(variant, 'SCRIPT.md')), {code: 'ENOENT'},
    'Script must not be duplicated under the Variant');
  evidence.sharedInputs = shared;

  const scriptBody = [
    '# 合成测试标题', '', '夹具正文只包含本地内容；无真实口播。', '', '<!-- P001 -->', '',
    '<!-- scene-index:start -->', '## Scene 索引（不属于口播）', '',
    '| Scene | Anchor 范围 | 时间预算 | 本段内容 / 观众重点 |', '|---|---|---|---|',
    '| S01 | P001 | 2s | 展示本地素材与两个独立运动节点 |', '<!-- scene-index:end -->', '',
  ].join('\n');
  await writeDocument(scriptPath, {origin: 'fixture', mode: 'user_provided', approval: 'not_required', revision: 1}, scriptBody);
  const researchMetadata = {...await frontmatter(researchPath), status: 'ready', revision: 1, script_revision: 1};
  const researchBody = (await fs.readFile(researchPath, 'utf8')).replace(/^---\r?\n[\s\S]*?\r?\n---/, '').replace(/^\r?\n/, '');
  await writeDocument(researchPath, researchMetadata, researchBody);
  evidence.script = {path: scriptPath, anchor: 'P001', revision: 1};

  // Component candidates originate from synthetic sources inside the allowed asset_source_roots.
  const sources = await fs.mkdtemp(path.join(resolved.asset_source_roots[0], 'native-fixture-'));
  assert(within(sources, root));
  const moduleId = `native-module-${suffix}`, mediaId = `native-media-${suffix}`;
  const moduleRef = `${moduleId}@v1`, mediaRef = `${mediaId}@v1`;
  for (const name of ['module', 'media']) await fs.mkdir(path.join(sources, name));
  await fs.writeFile(path.join(sources, 'module/nudge.js'),
    'window.fixtureNudge = (timeline, target, amount) => timeline.fromTo(target, {x:0}, {x:amount,duration:1.5,ease:"none"}, 0);\n');
  await fs.writeFile(path.join(sources, 'module/asset.json'), JSON.stringify({schema_version: 1,
    id: moduleId, version: 1, kind: 'module', entry: 'nudge.js', runtime: {versions: {gsap: runtimeLock.versions.gsap}}}));
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

  // ANIMATION_PLAN keeps the inherited 3.7.0 header/line identity; only the body is authored.
  const planPath = path.join(variant, 'ANIMATION_PLAN.md');
  const planHeader = await frontmatter(planPath);
  assert.equal(planHeader.plan_format, '3.7.0', 'Do not downgrade the Plan format');
  assert(planHeader.line, 'Do not remove the frozen line');
  const planBody = [
    '# Animation Plan', '', '## 导演 Brief', '',
    '**核心表达：** 技术夹具说明本地素材闭包与两条独立运动。',
    '**主体/次主体：** 主体为标题与证据图；次主体为两个独立节点。',
    '**禁止项：** 不使用外部网络资源或 CDN。',
    '**错相：** 节点先动，标题随后稳定。',
    '**运动语言：** 预备 → 冲击 → 回稳。',
    '**物理：** 轻量平移，无旋转。',
    '**光：** 纯本地平面配色。',
    '**节拍与声音：** 初始夹具静音，无正式声音。',
    '**验收标准：** S01 在 1920×1080、30fps、2 秒内完成，两个节点独立位移。',
    '**参考机制：** persistent-anchor', '',
    '## 分镜表', '',
    '| 段 | 起点口播词 | 观众看到什么 | 本段任务 | 主体 | 交接例外 | 延续 |',
    '|---|---|---|---|---|---|---|',
    '| S01·A1 | 合成标题 | 标题、证据图与两个独立节点 | 建立本地素材闭包 | | | |', '',
    '## S01', '',
    '**A/B 编排与延续：** A 为标题与证据图，B 为两个独立运动节点。',
    `**素材与声音：** 夹具模块 \`${moduleRef}\` 与媒体 \`${mediaRef}\`；初始夹具静音，无正式声音。`,
    '', '### I01 · SCRIPT.md#P001', '', '```screen', '合成测试标题：本地素材证据与两个独立节点', '```', '',
  ].join('\n');
  await writeDocument(planPath, planHeader, planBody);
  const refreshed = JSON.parse(run('plan', 'refresh', '--json'));
  assert.equal(refreshed.variant, 'variant1');
  const planAfter = await frontmatter(planPath);
  assert.equal(planAfter.plan_format, '3.7.0', 'Plan refresh must not downgrade the format');
  assert.deepEqual(planAfter.line, state.line, 'Plan refresh must keep the frozen line');
  assert.equal((await fs.readFile(planPath, 'utf8')).includes('## S01'), true, 'Plan must keep the exact ## S01 heading');
  assert(planAfter.revision >= 1);
  state = await readJSON(path.join(variant, 'variant.yaml'));
  assert.equal(state.plan_revision, planAfter.revision);
  evidence.plan = {revision: planAfter.revision, changed: refreshed.changed, line: planAfter.line};

  // Local GSAP/font from the pinned package; 1920x1080 30fps 2s composition with two moving nodes.
  await fs.mkdir(path.join(project, 'assets'), {recursive: true});
  await fs.mkdir(path.join(project, 'compositions'), {recursive: true});
  await fs.writeFile(path.join(project, 'DESIGN.md'), 'Synthetic direct-root acceptance fixture. No production acceptance.\n');
  await fs.writeFile(path.join(project, 'project-config.json'), '{}\n');
  await fs.copyFile(path.join(root, 'runtime/npm/node_modules/gsap/dist/gsap.min.js'), path.join(project, 'assets/gsap.min.js'));
  await fs.copyFile(path.join(root, 'runtime/npm/node_modules/gsap/dist/MotionPathPlugin.min.js'), path.join(project, 'assets/MotionPathPlugin.min.js'));
  // Pinned local font: the exact manifest entry only. Never search runtime/npm, never fall back.
  const fontManifest = await readJSON(path.join(root, '.studio/fonts/manifest.json'));
  assert.equal(fontManifest.version, 1, 'Font manifest schema must be version 1');
  const fontEntry = (fontManifest.files || []).find(item => item.path === 'source-han-sans/SourceHanSansCN-Regular.otf');
  assert(fontEntry && /^[0-9a-f]{64}$/.test(fontEntry.sha256) && fontEntry.bytes > 0,
    'Manifest must pin source-han-sans/SourceHanSansCN-Regular.otf with a sha256 and byte size');
  const fontSource = path.join(root, '.studio/fonts', fontEntry.path);
  assert.equal((await fs.stat(fontSource)).size, fontEntry.bytes,
    'Pinned font on disk must match the manifest byte size; no installed substitute is allowed');
  const fontName = path.basename(fontEntry.path);
  await fs.copyFile(fontSource, path.join(project, 'assets', fontName));
  assert.equal(await sha256(path.join(project, 'assets', fontName)), fontEntry.sha256,
    'Fixture font must hash-match the pinned manifest entry');
  evidence.font = {path: fontEntry.path, sha256: fontEntry.sha256, bytes: fontEntry.bytes};
  await fs.writeFile(path.join(project, 'assets/fixture.css'), [
    `@font-face { font-family: "Fixture"; src: url("${fontName}"); }`,
    'html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#eef3f1;font-family:"Fixture",sans-serif}',
    'main{position:relative;width:1920px;height:1080px}',
    'h1{position:absolute;top:80px;left:96px;margin:0;font-size:72px;color:#162725}',
    '.raster{position:absolute;left:96px;top:264px;width:832px;height:468px}',
    '.node{position:absolute;left:1072px;width:224px;height:192px;border-radius:12px;background:#188b72;color:#fff;display:grid;place-items:center;font-size:52px}',
    '#instance-a{top:264px}#instance-b{top:544px;background:#cf5068}',
    '.icon{position:absolute;left:1568px;top:800px;width:128px;height:128px}',
    '',
  ].join('\n'));
  const html = [
    '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Native acceptance fixture</title>',
    '<link rel="stylesheet" href="assets/fixture.css"></head><body>',
    '<main data-composition-id="native-fixture" data-width="1920" data-height="1080" data-start="0" data-duration="2">',
    '<section id="S01" data-scene-id="S01" class="clip" data-start="0" data-duration="2" data-reading-time="1" data-track-index="0">',
    '<h1 id="fixture-title">合成测试标题</h1>',
    `<img class="raster" alt="Synthetic evidence raster" src="vendor/components/${mediaId}/v1/evidence.png">`,
    '<div class="node" id="instance-a">A</div><div class="node" id="instance-b">B</div>',
    `<img class="icon" alt="Local SVG check" src="vendor/components/${mediaId}/v1/icon.svg">`,
    '</section></main>',
    '<script src="assets/gsap.min.js"></script>',
    '<script src="assets/MotionPathPlugin.min.js"></script>',
    `<script src="vendor/components/${moduleId}/v1/nudge.js"></script>`,
    '<script>const timeline=gsap.timeline({paused:true});',
    "window.fixtureNudge(timeline,document.getElementById('instance-a'),320);",
    "window.fixtureNudge(timeline,document.getElementById('instance-b'),-180);",
    "timeline.to({},{duration:.5},1.5);window.__timelines={'native-fixture':timeline};</script></body></html>",
  ].join('');
  await fs.writeFile(path.join(project, 'index.html'), html, 'utf8');
  // TimingSceneS01matchesPlan: local 2s Scene sharing the exact Scene ID with the Plan.
  assert.match(html, /data-composition-id="native-fixture"[^>]*data-width="1920"[^>]*data-height="1080"[^>]*data-duration="2"/);
  assert.match(html, /id="S01"[^>]*data-start="0"[^>]*data-duration="2"/);
  evidence.scene = {id: 'S01', start: 0, duration: 2, width: 1920, height: 1080};

  // Default pending Script/Plan gates block registration before the fixture-only override.
  const blocked = invoke(['--work', id, '--variant', 'variant1', 'preview', 'register',
    '--purpose', 'draft', '--kind', 'executable'], {}, false);
  assert.notEqual(blocked.status, 0, 'Default pending Script/Plan must prevent preview registration');
  evidence.prePutRegistrationBlocked = `${blocked.stdout}${blocked.stderr}`.trim().slice(0, 400);

  const shown = JSON.parse(run('workflow', 'show', '--json'));
  const confirmation = shown.values && shown.values.human_confirmation;
  assert(confirmation && ['script', 'plan', 'draft'].every(key => key in confirmation),
    'Workflow must expose three human confirmation switches');
  const workflowFile = path.join(output, 'workflow.json');
  await writeJSON(workflowFile, {human_confirmation: Object.fromEntries(Object.keys(confirmation).map(key => [key, false]))});
  const putReport = JSON.parse(run('workflow', 'put', '--layer', 'work', '--file', workflowFile, '--json'));
  assert(['script', 'plan', 'draft'].every(key => putReport.sources
    && putReport.sources[`human_confirmation.${key}`] === 'work'),
    'Workflow report must resolve the Work layer as the source of the fixture gate override');
  const gatesAfter = JSON.parse(run('workflow', 'show', '--json')).values.human_confirmation;
  assert(['script', 'plan', 'draft'].every(key => gatesAfter[key] === false), 'Fixture must disable all three gates');
  evidence.workflowGates = gatesAfter;

  // Components install after the gate override so no fabricated approval is required.
  for (const [name, ref, role] of [['module', moduleRef, 'auxiliary'], ['media', mediaRef, 'subject']]) {
    const candidate = JSON.parse(work('component', 'pack', path.join(sources, name), '--json'));
    assert.equal(candidate.component_ref, ref);
    const acceptance = JSON.parse(work('component', 'accept', ref, '--sha256', candidate.package_sha256,
      '--note', 'Synthetic direct-root acceptance fixture; not production acceptance', '--json'));
    assert.equal(acceptance.status, 'accepted');
    assert.equal('review' in acceptance, false, 'Acceptance must not carry a Review marker');
    const binding = path.join(output, `${name}-binding.json`);
    await writeJSON(binding, {schema_version: 3, component_ref: ref, scene: 'S01', usage: {role, required: true}});
    const installed = JSON.parse(run('component', 'install', ref, '--binding', binding, '--json'));
    assert.equal(installed.component_ref, ref);
    evidence.assets.push({candidate, acceptance, installed});
  }
  const installation = JSON.parse(run('component', 'verify', '--json'));
  assert.equal(installation.work, id);
  evidence.installation = installation;

  // Normal Draft chain: register an executable Studio Draft, then it is accepted under the off gate.
  const draft = run('preview', 'register', '--purpose', 'draft', '--kind', 'executable');
  assert.equal(draft, 'draft-v001');
  state = await readJSON(path.join(variant, 'variant.yaml'));
  assert.equal(state.accepted_preview, draft, 'Gate-off registration must accept the exact Draft');
  assert.equal(state.accepted_plan_revision, state.plan_revision);
  assert.equal(state.accepted_script_revision, state.script_revision);
  assert.equal(state.lifecycle, 'active');
  evidence.draft = {id: draft, accepted_preview: state.accepted_preview};

  const record = JSON.parse(run('preview', 'open', draft, '--no-open'));
  opened.push(draft);
  evidence.sessions.push(record);
  assert.equal(record.work, id);
  assert.equal(record.variant, 'variant1');
  assert.equal(record.target, draft);
  assert.equal(new URL(record.url).port, String(record.port));
  assert(new URL(record.url).hash.startsWith('#project/'), 'Must open the official Studio project');
  assert.equal((await readJSON(path.join(record.browser_profile, 'Default/Preferences'))).enable_do_not_track, true);
  const previewMeta = await frontmatter(path.join(variant, 'previews', draft, 'preview.md'));
  assert.equal(record.snapshot_sha256, previewMeta.snapshot_sha256, 'Studio must open the accepted snapshot');
  assert(within(record.project, path.join(variant, '.runtime')), 'Studio review copy must stay inside the Variant runtime');
  evidence.snapshot = {id: draft, project: record.project, sha256: record.snapshot_sha256};

  // Studio uses the normal product browser resolver; the pinned headless shell is render-only.
  const studioBrowserPath = pythonJson([
    'import sys',
    `sys.path.insert(0, ${JSON.stringify(path.join(root, '.studio'))})`,
    'import studio_preview',
    'print(studio_preview.browser_path())',
  ].join('\n'));
  browser = await puppeteer.launch({executablePath: studioBrowserPath, userDataDir: record.browser_profile, headless: true, env: baseEnv,
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
  const {iframe, frame} = await show(record);
  evidence.images = await frame.$$eval('img', images => images.map(image =>
    ({src: image.getAttribute('src'), width: image.naturalWidth, height: image.naturalHeight})));
  assert.equal(evidence.images.length, 2);
  assert(evidence.images.every(image => image.width > 0 && image.height > 0));
  // Deterministic native-frame clock: 30fps over the 2s Scene, all seeks on exact frame boundaries.
  const FPS = 30;
  for (const time of [1.5, 0, 0.5, 1.5]) {
    assert(Number.isInteger(time * FPS), 'Seek time must land on a native 30fps frame boundary');
    await page.$eval('hyperframes-player', (player, value) => { player.pause(); player.seek(value); }, time);
    await frame.waitForFunction(value => Math.abs(window.__timelines['native-fixture'].time() - value) < 0.001, {}, time);
    const nodes = await frame.evaluate(() => ['instance-a', 'instance-b'].map(id => {
      const element = document.getElementById(id);
      return {id, x: Number(gsap.getProperty(element, 'x')), transform: element.style.transform};
    }));
    evidence.seeks.push({time, nodes});
  }
  assert.deepEqual(evidence.seeks[0], evidence.seeks[3], 'Backward and repeated seek must produce identical DOM state');
  assert.deepEqual(evidence.seeks[1].nodes.map(node => node.x), [0, 0]);
  assert.deepEqual(evidence.seeks[0].nodes.map(node => node.x), [320, -180]);
  assert(evidence.seeks[2].nodes[0].x > 0 && evidence.seeks[2].nodes[0].x < 320);
  assert(evidence.seeks[2].nodes[1].x < 0 && evidence.seeks[2].nodes[1].x > -180);
  evidence.pixels = [await pixels(iframe, 'desktop')];
  await page.setViewport({width: 390, height: 844, deviceScaleFactor: 1});
  evidence.pixels.push(await pixels(iframe, 'mobile-390'));
  await browser.close(); browser = null;

  // Canonical Finalize: render + QA + append-only export. No direct render or ffmpeg encoding.
  run('finalize', '--fps', '30');
  state = await readJSON(path.join(variant, 'variant.yaml'));
  assert.equal(state.current_final, 'final.mp4', 'Finalize must promote the accepted Draft');
  assert.equal(state.lifecycle, 'active', 'Export must leave the Variant active');
  assert.equal(state.status, 'active');
  const finalPath = path.join(variant, 'final/final.mp4');
  const manifestPath = path.join(variant, 'final/manifest.json');
  const manifest = await readJSON(manifestPath);
  const finalHash = await sha256(finalPath);
  assert.equal(manifest.schema_version, 1);
  assert.equal(manifest.workflow, 'hyperframes_video');
  assert.equal(manifest.source_preview, draft);
  assert.equal(manifest.final_sha256, finalHash);
  assert.equal(manifest.qa, 'passed');
  assert.deepEqual(manifest.artifacts, [{path: 'final.mp4', role: 'video', sha256: finalHash}]);
  const receipt = await readJSON(path.join(variant, '.runtime/finalize.json'));
  assert.equal(receipt.final_sha256, finalHash, 'Finalize receipt must match the committed video');
  assert.equal(receipt.state, 'complete', 'Export copy must complete the receipt');
  const probe = await ffprobe(finalPath);
  const stream = probe.streams.find(item => item.codec_type === 'video');
  assert(stream && stream.width === 1920 && stream.height === 1080, 'Final must be exactly 1920x1080');
  assert.equal(stream.r_frame_rate, '30/1', 'Final must be 30fps');
  assert(Math.abs(Number(probe.format.duration) - 2) <= 0.1, 'Final duration must be ~2 seconds');
  // The exports.publish receipt in finalize.json is authoritative: directory + files.video + hashes.video.
  const exported = receipt.export;
  assert(exported && typeof exported.directory === 'string' && exported.files && exported.files.video
    && exported.hashes && exported.hashes.video, 'Finalize receipt must carry the export shelf record');
  assert(Number.isInteger(exported.revision) && exported.revision >= 1
    && Number.isInteger(exported.sequence) && exported.sequence >= 1, 'Export receipt needs revision and sequence');
  assert.equal(exported.hashes.video, finalHash, 'Exported copy must hash-match the committed Final');
  const exportPrefix = `variant1-r${String(exported.revision).padStart(3, '0')}-e${String(exported.sequence).padStart(3, '0')}`;
  assert.equal(exported.files.video, `${exportPrefix}-video.mp4`,
    'Export filename must follow <variant>-r<revision>-e<sequence>-<role>');
  const exportCopy = path.join(exported.directory, exported.files.video);
  assert(within(await fs.realpath(exportCopy), await fs.realpath(exportRoot)),
    'Export shelf must live inside the configured export root');
  assert.equal(path.basename(exported.directory), 'variant1', 'Export shelf must be scoped to the Variant');
  assert.equal(path.basename(path.dirname(exported.directory)), path.basename(workDir), 'Export shelf must be scoped to the Work');
  assert.equal(await sha256(exportCopy), finalHash, 'Export shelf copy must be byte-identical to the Final');
  evidence.final = {path: finalPath, sha256: finalHash, manifest: manifestPath, probe,
    receiptState: receipt.state, export: exported, exportCopy};

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
    const result = invoke(['--work', id, '--variant', 'variant1', 'preview', 'stop', target], {}, false);
    if (result.status !== 0) evidence.cleanupErrors.push(`${target}: ${result.stderr || result.stdout}`);
  }
  if (evidence.cleanupErrors.length) evidence.passed = false;
  const report = path.join(output, 'verification.json');
  await fs.writeFile(report, JSON.stringify(evidence, null, 2));
  console.log(JSON.stringify({passed: evidence.passed, report, work: id, root, draft: evidence.draft}));
  assert.deepEqual(evidence.cleanupErrors, [], 'Stop every fixture browser and Studio');
}
