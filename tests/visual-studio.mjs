// Real pinned Studio integration with synthetic Review Works, not production acceptance.
// Set HF_PACKAGE, PLAYWRIGHT_PACKAGE and CHROME_PATH to existing local dependencies.
// Windows also requires WORK_COMMAND=<session/work.cmd> and FIXTURE_ROOT=<bound Review root>.
// WORK_COMMAND may be a JSON argv array; WSL defaults to python3 .studio/work.py.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {fileURLToPath, pathToFileURL} from 'node:url';

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const {HF_PACKAGE, PLAYWRIGHT_PACKAGE, CHROME_PATH, WORK_COMMAND, FIXTURE_ROOT} = process.env;
assert(HF_PACKAGE && PLAYWRIGHT_PACKAGE && CHROME_PATH, 'Set local HF_PACKAGE, PLAYWRIGHT_PACKAGE, CHROME_PATH');
assert(process.platform !== 'win32' || WORK_COMMAND && FIXTURE_ROOT,
  'Windows must use an explicitly bound Review session work.cmd and FIXTURE_ROOT');
const playwrightEntry = (await fs.stat(PLAYWRIGHT_PACKAGE)).isDirectory()
  ? path.join(PLAYWRIGHT_PACKAGE, 'index.mjs') : PLAYWRIGHT_PACKAGE;
const {chromium} = await import(pathToFileURL(playwrightEntry).href);
const sharp = createRequire(path.join(HF_PACKAGE, 'package.json'))('sharp');
const hfVersion = JSON.parse(await fs.readFile(path.join(HF_PACKAGE, 'package.json'), 'utf8')).version;
assert.equal(hfVersion, '0.8.27', 'Verify an intentional pinned-version change before updating this check');
const command = WORK_COMMAND ? WORK_COMMAND.startsWith('[') ? JSON.parse(WORK_COMMAND) : [WORK_COMMAND]
  : [process.env.PYTHON || 'python3', path.join(repo, '.studio/work.py')];
assert(Array.isArray(command) && command.length && command.every(value => typeof value === 'string'));
const temporary = !FIXTURE_ROOT;
const base = temporary ? await fs.mkdtemp(path.join(os.tmpdir(), 'hf-visual-studio-')) : path.resolve(FIXTURE_ROOT);
const env = {...process.env, DO_NOT_TRACK: '1', HYPERFRAMES_NO_TELEMETRY: '1',
  HYPERFRAMES_BROWSER_PATH: CHROME_PATH, HYPERFRAMES_CLI: path.join(HF_PACKAGE, 'dist/cli.js'),
  PRODUCER_BROWSER_GPU_MODE: 'software'};
if (!WORK_COMMAND) {
  env.HYPERFRAMES_AI_ROOT = base;
  delete env.HYPERFRAMES_AI_CONFIG;
  delete env.HYPERFRAMES_AI_WORK_ROOT;
  delete env.HYPERFRAMES_AI_SESSION;
  delete env.HYPERFRAMES_AI_REVIEW;
  await fs.cp(path.join(repo, '.studio/templates'), path.join(base, '.studio/templates'), {recursive: true});
  for (const location of ['active', 'parked', 'archive']) await fs.mkdir(path.join(base, 'works', location), {recursive:true});
}
function invoke(args, expectedSuccess = true) {
  let executable = command[0], argv = [...command.slice(1), ...args];
  const options = {env, encoding: 'utf8', timeout: 240000, maxBuffer: 8 * 1024 * 1024};
  if (process.platform === 'win32' && /\.(cmd|bat)$/i.test(executable)) {
    const quote = value => {
      assert(!/["\r\n%]/.test(value), 'Unsafe cmd.exe argument in fixture');
      return `"${value}"`;
    };
    argv = ['/d', '/s', '/c', `"${[executable, ...argv].map(quote).join(' ')}"`];
    executable = process.env.ComSpec || 'cmd.exe';
    options.windowsVerbatimArguments = true;
  }
  const result = spawnSync(executable, argv, options);
  if (expectedSuccess) assert.equal(result.status, 0, `${args.join(' ')}\n${result.error || ''}\n${result.stderr}\n${result.stdout}`);
  return result;
}
function work(...args) { return invoke(args).stdout.trim(); }
const root = temporary ? work('review', 'init', 'studio-fixture') : base;
if (!WORK_COMMAND) {
  env.HYPERFRAMES_AI_WORK_ROOT = root;
  env.HYPERFRAMES_AI_REVIEW = '1';
}
assert.equal(path.resolve(JSON.parse(work('root', 'show')).work_root), path.resolve(root), 'Session must bind the intended fixture root');
const marker = JSON.parse(await fs.readFile(path.join(root, '.runtime/review.json'), 'utf8'));
assert.equal(marker.mode, 'review', 'Never run this fixture against production WorkStore');
const output = await fs.mkdtemp(path.join(root, '.runtime/studio-evidence-'));
const evidence = {technicalFixture: true, platform: process.platform, hfVersion, workCommand: command,
  root, output, sessions: [], checks: [], errors: [], externalRequests: []};
const sessions = [];
let browser;
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
async function treeHashes(directory) {
  const values = {};
  for (const entry of await fs.readdir(directory, {recursive: true, withFileTypes: true})) {
    assert(!entry.isSymbolicLink(), 'Fixture snapshots and review copies must be real files');
    if (entry.isFile()) {
      const file = path.join(entry.parentPath || entry.path, entry.name);
      values[path.relative(directory, file)] = hash(await fs.readFile(file));
    }
  }
  return values;
}
async function fixture(label) {
  const id = work('new', `Studio fixture ${label}`, '--workflow', 'hyperframes_video', '--detached');
  const variant = path.join(root, 'works/active', id, 'variants/main');
  const project = path.join(variant, 'project');
  const run = (...args) => work('--work', id, '--variant', 'main', ...args);
  const research = path.join(variant, 'RESEARCH.md');
  await fs.writeFile(research, (await fs.readFile(research, 'utf8')).replace('"pending"', '"ready"'));
  const plan = path.join(variant, 'ANIMATION_PLAN.md');
  // Approved here denotes synthetic fixture input, never acceptance of a production Work.
  await fs.writeFile(plan, (await fs.readFile(plan, 'utf8')).replace('"draft"', '"approved"'));
  await fs.mkdir(path.join(project, 'compositions'), {recursive: true});
  await fs.writeFile(path.join(project, 'DESIGN.md'), 'Synthetic Studio integration fixture. One static process; no production claim.');
  await fs.writeFile(path.join(project, 'project-config.json'), '{}');
  const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Studio fixture ${label}</title>
<style>*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;font-family:Arial,sans-serif;letter-spacing:0}main{width:960px;height:540px;background:#eef3f1;padding:48px;color:#162725}h1{font-size:38px;margin:0 0 20px}p{font-size:22px;margin:0 0 30px}.process{display:flex;align-items:center;gap:20px}.node{width:220px;height:170px;padding:24px;background:#fff;border-top:8px solid #188b72;font-size:26px}.node:last-child{border-color:#cf5068}span{font-size:32px}.footer{margin-top:34px;font-size:20px}</style></head><body>
<main data-composition-id="studio-${label}" data-width="960" data-height="540" data-start="0" data-duration="1" data-no-timeline="true">
<section id="S01" class="clip" data-start="0" data-duration="1" data-track-index="0"><h1 id="fixture-title">Studio ${label}: evidence to answer</h1><p>Keep the retrieved source attached to the answer.</p><div class="process"><div class="node">Question<br>Which policy?</div><span aria-hidden="true">&rarr;</span><div class="node">Evidence<br>Policy 7</div><span aria-hidden="true">&rarr;</span><div class="node">Answer<br>Source: Policy 7</div></div><p class="footer">A visible relationship, not a repeated explanation.</p></section></main></body></html>`;
  await fs.writeFile(path.join(project, 'index.html'), html);
  return {id, variant, project, label, run, html};
}
async function open(item, target = 'current', omitTarget = false) {
  const record = JSON.parse(item.run('preview', 'open', ...(omitTarget ? [] : [target]), '--no-open'));
  sessions.push({item, target, record}); evidence.sessions.push(record);
  assert.equal(record.work, item.id); assert.equal(record.variant, 'main'); assert.equal(record.target, target);
  assert.equal(new URL(record.url).port, String(record.port));
  assert(new URL(record.url).hash.startsWith('#project/'), 'Must return a real Studio project URL');
  assert.equal(JSON.parse(await fs.readFile(path.join(record.browser_profile,'Default/Preferences'),'utf8')).enable_do_not_track,
    true, 'Work must supply an isolated official browser profile with telemetry opt-out');
  return record;
}
async function show(record, label) {
  const page = await browser.newPage();
  page.on('pageerror', error => evidence.errors.push({label, message:error.message}));
  page.on('request', request => {
    if (/^https?:/.test(request.url()) && !['localhost','127.0.0.1','[::1]'].includes(new URL(request.url()).hostname))
      evidence.externalRequests.push(request.url());
  });
  await page.route('**/*', route => {
    const url = new URL(route.request().url());
    if (['http:', 'https:'].includes(url.protocol) && !['localhost','127.0.0.1','[::1]'].includes(url.hostname))
      return route.abort('blockedbyclient');
    return route.continue();
  });
  await page.goto(record.url, {waitUntil:'domcontentloaded'});
  assert.equal(await page.evaluate(() => navigator.doNotTrack), '1', 'Real browser preferences must enable Studio telemetry opt-out');
  const iframe = page.locator('iframe').first();
  await iframe.waitFor({timeout:30000});
  const frame = await (await iframe.elementHandle()).contentFrame();
  assert(frame, 'Official Studio must render the actual project in its player');
  try {
    await frame.locator('#fixture-title').waitFor({state:'visible'});
  } catch (error) {
    await page.screenshot({path:path.join(output, `${label}-failure.png`), fullPage:true});
    await fs.writeFile(path.join(output, `${label}-failure.json`), JSON.stringify({
      frames:page.frames().map(item => item.url()), body:await page.locator('body').innerText(),
      frame:await frame.content(),
    },null,2));
    throw error;
  }
  assert.equal(await frame.locator('audio,video,canvas').count(), 0);
  const {data, info} = await sharp(await iframe.screenshot()).removeAlpha().raw().toBuffer({resolveWithObject:true});
  let green = 0, pink = 0;
  for (let offset = 0; offset < data.length; offset += info.channels) {
    const [r,g,b] = data.subarray(offset,offset+3);
    if (r < 70 && g > 100 && b > 60 && g > b) green++;
    if (r > 150 && g < 140 && b > 60 && r > b) pink++;
  }
  assert(green > 50 && pink > 30, 'Actual Studio canvas must contain both process and answer pixels');
  await page.screenshot({path:path.join(output, `${label}-desktop.png`), fullPage:true});
  evidence.checks.push({label, title:await frame.locator('#fixture-title').textContent(), frameUrl:frame.url(), pixels:{green,pink}});
  return {page, frame};
}
async function edit(record, before, after) {
  const projectName = decodeURIComponent(new URL(record.url).hash.slice('#project/'.length));
  const url = new URL(`/api/projects/${encodeURIComponent(projectName)}/files/index.html`, record.url);
  const response = await fetch(url); assert.equal(response.status, 200);
  const file = await response.json(); assert(file.content.includes(before));
  const changed = file.content.replace(before, after);
  const saved = await fetch(url, {method:'PUT', headers:{'Content-Type':'text/plain', 'If-Match':file.version}, body:changed});
  assert.equal(saved.status, 200, await saved.text());
  assert.equal(await fs.readFile(path.join(record.project, 'index.html'), 'utf8'), changed,
    'Official Studio must write the selected project, not merely update the DOM');
}
try {
  const first = await fixture('A'), second = await fixture('B');
  const current = await open(first, 'current', true), other = await open(second);
  browser = await chromium.launchPersistentContext(current.browser_profile, {executablePath:CHROME_PATH, headless:true,
    viewport:{width:1440,height:1000},
    args:[...(process.platform === 'linux' ? ['--no-sandbox'] : []), '--disable-dev-shm-usage']});
  assert.equal(path.resolve(current.project), path.resolve(first.project));
  assert.equal(path.resolve(other.project), path.resolve(second.project));
  assert.notEqual(current.port, other.port, 'Different Works must not silently share a Studio');
  const shown = await show(current, 'current-A'), shownOther = await show(other, 'current-B');
  assert((await shown.frame.locator('#fixture-title').textContent()).startsWith('Studio A:'));
  assert((await shownOther.frame.locator('#fixture-title').textContent()).startsWith('Studio B:'));
  await shown.frame.locator('#fixture-title').click({force:true});
  await shown.page.waitForTimeout(500);
  for (const [item, record] of [[first,current],[second,other]]) {
    const context = JSON.parse(item.run('preview', 'context', 'current', '--fields', 'selection', '--detail', 'compact'));
    assert.equal(context.work.work, item.id); assert.equal(context.server.port, record.port);
    assert.equal(path.resolve(context.server.projectDir), path.resolve(item.project));
    assert(!Object.hasOwn(context, 'lint') && !Object.hasOwn(context, 'capabilities'), 'Context must honor requested fields');
    if (item === first) {
      assert(context.selection, 'A real canvas click must be visible to the bound context query');
      assert.match(context.selection.textContent, /Studio A:/);
      assert(!Object.hasOwn(context.selection,'computedStyles'), 'Compact context omits full styles');
    }
  }
  await shown.page.getByRole('button',{name:'Play',exact:true}).click();
  await shown.page.getByRole('button',{name:'Pause',exact:true}).waitFor({state:'visible'});
  await shown.page.waitForTimeout(150);
  await shown.page.getByRole('button',{name:'Pause',exact:true}).click();
  const player = shown.page.locator('hyperframes-player');
  const playbackTime = await player.evaluate(element => element.currentTime);
  assert(playbackTime > 0, 'Native Studio playback must advance its actual player clock');
  await player.evaluate(element => element.seek(0.25));
  assert.equal(await player.evaluate(element => element.currentTime), 0.25);
  await player.evaluate(element => element.seek(0));
  evidence.checks.push({nativePlaybackSeconds:playbackTime,seekSeconds:0.25});
  evidence.checks.push('two distinct Work contexts and default current Studio route');
  const planId = first.run('preview', 'register', '--purpose', 'plan', '--kind', 'executable');
  const plan = path.join(first.variant, 'previews', planId), planBefore = await treeHashes(plan);
  const planStudio = await open(first, planId);
  assert.notEqual(planStudio.project, path.join(plan, 'source-snapshot'));
  const shownPlan = await show(planStudio, 'registered-plan');
  await edit(planStudio, 'Studio A:', 'Reviewed Plan A:');
  await shownPlan.page.reload({waitUntil:'domcontentloaded'});
  await shownPlan.page.waitForTimeout(700);
  assert.deepEqual(await treeHashes(plan), planBefore, 'Studio Plan edits must preserve every frozen file');
  assert((await fs.readFile(path.join(first.project,'index.html'),'utf8')).includes('Studio A:'));
  const rendered = path.join(first.variant, 'studio-fixture-draft.mp4');
  first.run('preview', 'render', planId, '--output', rendered, '--fps', '6', '--software-gl');
  assert((await fs.stat(rendered)).size > 1000, 'Use a real rendered MP4, not fake test bytes');
  const draftId = first.run('preview', 'register', rendered);
  const draft = path.join(first.variant, 'previews', draftId), draftBefore = await treeHashes(draft);
  const draftStudio = await open(first, draftId);
  await show(draftStudio, 'registered-draft');
  await edit(draftStudio, 'Studio A:', 'Reviewed Draft A:');
  assert.deepEqual(await treeHashes(draft), draftBefore, 'Studio Draft edits must preserve every frozen file');
  await edit(current, 'Studio A:', 'Edited Current A:');
  const changed = JSON.parse(first.run('preview', 'context', 'current', '--fields', 'selection'));
  assert.equal(changed.source_changed, true);
  assert.equal(changed.render_matches_source, false);
  const stale = invoke(['--work', first.id, '--variant', 'main', 'preview', 'register', rendered], false);
  assert.notEqual(stale.status, 0, 'Old MP4 must not be registered against newly edited source');
  assert.match(stale.stderr, /different source|changed project/i);
  evidence.checks.push('official file writes isolate Plan/Draft snapshots and stale MP4 is rejected');
  const layout = path.join(second.variant, 'layout');
  await fs.mkdir(layout);
  await fs.writeFile(path.join(layout, 'index.html'), second.html.replace(/ data-composition-id="[^"]+"/, '')
    .replace(/ data-start="0" data-duration="1" data-no-timeline="true"/, ''));
  const layoutId = second.run('preview', 'register', '--purpose', 'plan', '--kind', 'layout', '--sample-dir', 'layout', '--scene', 'S01');
  const layoutSnapshot = path.join(second.variant, 'previews', layoutId), layoutBefore = await treeHashes(layoutSnapshot);
  const layoutStudio = await open(second, layoutId), shownLayout = await show(layoutStudio, 'static-gap');
  const staticState = await shownLayout.frame.evaluate(() => ({
    compositions:document.querySelectorAll('[data-composition-id]').length,
    scenes:document.querySelectorAll('#S01').length,
    duration:document.querySelector('[data-composition-id]').getAttribute('data-duration'),
    timelines:Object.entries(window.__timelines || {}).filter(([,value]) => typeof value?.duration === 'function').map(([key]) => key),
    media:document.querySelectorAll('audio,video,canvas').length,
  }));
  assert.deepEqual(staticState, {compositions:1,scenes:1,duration:'1',timelines:[],media:0});
  assert.deepEqual(await treeHashes(layoutSnapshot), layoutBefore);
  await shownLayout.page.setViewportSize({width:390,height:844});
  await shownLayout.page.screenshot({path:path.join(output,'static-gap-mobile.png'), fullPage:true});
  evidence.checks.push({staticGap:staticState, snapshotUnchanged:true});
  assert.deepEqual(evidence.errors, [], 'Official Studio browser errors');
  assert.deepEqual(evidence.externalRequests, [], 'DNT and local resources must avoid external requests, not merely block them');
  evidence.passed = true;
} catch (error) {
  evidence.failure = error.stack;
  throw error;
} finally {
  const cleanupErrors = [];
  try { if (browser) await browser.close(); } catch (error) { cleanupErrors.push(error.message); }
  for (const {item,target} of sessions.reverse()) {
    const result = invoke(['--work',item.id,'--variant','main','preview','stop',target], false);
    if (result.status !== 0) cleanupErrors.push(`${item.id}/${target}: ${result.stderr || result.stdout}`);
  }
  evidence.cleanupErrors = cleanupErrors;
  if (cleanupErrors.length) evidence.passed = false;
  await fs.writeFile(path.join(output,'verification.json'), JSON.stringify(evidence,null,2));
  console.log(output);
  assert.deepEqual(cleanupErrors, [], 'Every fixture Studio and browser must stop');
}
