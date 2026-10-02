import { chromium } from 'playwright';
import { PNG } from 'pngjs';
import { mkdir, writeFile, readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { startServer } from './serve.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const inputs = args.length ? args : ['../T1-device-mockups/out/phone.glb', '../T1-device-mockups/out/laptop.glb'];
const out = path.join(root, 'reports', 'browser');
await mkdir(out, { recursive: true });
const report = { state: 'running', three: '0.160.0', viewport: { width: 1280, height: 900, deviceScaleFactor: 1 }, assets: [], errors: [] };
let browser, server;
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const assert = (condition, message) => { if (!condition) throw new Error(message); };
try {
  server = await startServer({ port: 0 });
  try {
    browser = await chromium.launch({ headless: true, ...(process.env.CHROMIUM_EXECUTABLE ? { executablePath: process.env.CHROMIUM_EXECUTABLE } : {}) });
  } catch (error) {
    report.state = 'blocked'; report.errors.push(`Chromium launch unavailable: ${error.message}`); throw error;
  }
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 1 });
  const pageErrors = [];
  page.on('pageerror', error => pageErrors.push(error.message));
  await page.goto(`http://127.0.0.1:${server.address().port}/`);
  await page.waitForFunction(() => window.assetFixture?.ready || window.assetFixture?.error);
  for (const input of inputs) {
    const file = path.resolve(input), bytes = await readFile(file), name = path.basename(file, '.glb');
    const result = { file: path.relative(root, file), sha256: sha(bytes), checks: [] };
    report.assets.push(result);
    const check = (name, pass, details) => { result.checks.push({ name, pass: Boolean(pass), ...(details !== undefined ? { details } : {}) }); assert(pass, name); };
    // Exercise the real file-input/GLTFLoader path. Bytes remain on the local machine.
    await page.locator('#file').setInputFiles(file);
    await page.waitForFunction(name => window.assetFixture.info().source === name, path.basename(file));
    result.info = await page.evaluate(() => window.assetFixture.info());
    check('r160', result.info.threeRevision === '160');
    check('loaded-real-meshes', result.info.meshCount > 0);
    const canvas = page.locator('#stage');
    await canvas.screenshot({ path: path.join(out, `${name}-overview.png`) });
    if (result.info.screenCount) {
      const probes = await page.evaluate(() => { window.assetFixture.setScreenTest(true); return window.assetFixture.screenView(); });
      const image = PNG.sync.read(await canvas.screenshot({ path: path.join(out, `${name}-screen-corners.png`) }));
      const colors = probes.map(p => {
        const i = (p.y * image.width + p.x) * 4;
        const actual = [...image.data.subarray(i, i + 3)];
        return { ...p, actual, pass: actual.length === 3 && actual.every((c, j) => Math.abs(c - p.rgb[j]) <= 10) };
      });
      check('physical-screen-four-corner-colors', colors.every(p => p.pass), colors);
    }
    await page.evaluate(() => window.assetFixture.frameAsset());
    const duration = result.info.clips[0]?.duration ?? 4, t1 = duration * .25, t3 = duration * .75;
    const sequence = [t3, 0, t1, t3], images = [];
    for (let i = 0; i < sequence.length; i++) {
      await page.evaluate(t => window.assetFixture.render(t), sequence[i]);
      images.push(PNG.sync.read(await canvas.screenshot({ path: path.join(out, `${name}-seek-${i}-${sequence[i].toFixed(3)}.png`) })));
    }
    const identical = images[0].data.equals(images[3].data);
    result.seek = { sequence, pixelHashes: images.map(i => sha(i.data)), exactRepeat: identical, animationPresent: result.info.clips.length > 0, note: result.info.clips.length ? 'Animated seek exercised' : 'Static GLB: checks deterministic fixture rendering, not animation motion' };
    check('absolute-seek-exact-pixel-repeat', identical);
    if (result.info.clips.length) check('animation-changes-pixels', !images[0].data.equals(images[1].data));
    if (result.info.lid?.range) {
      for (const degrees of [0, -30, -60, -90, -105, -130]) {
        const radians = degrees * Math.PI / 180;
        const actual = await page.evaluate(angle => window.assetFixture.setLidRadians(angle), radians);
        check(`lid-${degrees}-degrees`, Math.abs(actual - radians) < 1e-6);
        await canvas.screenshot({ path: path.join(out, `${name}-lid-${Math.abs(degrees)}deg.png`) });
      }
      await page.evaluate(angle => window.assetFixture.setLidRadians(angle), result.info.lid.radians);
    }
    const themeHashes = [];
    for (const theme of ['neutral', 'warm', 'cool']) {
      const changes = await page.evaluate(theme => { window.assetFixture.setTheme(theme); return window.assetFixture.info().themeChanges.length; }, theme);
      check(`theme-${theme}-has-matched-roles`, changes > 0);
      themeHashes.push(sha(PNG.sync.read(await canvas.screenshot({ path: path.join(out, `${name}-theme-${theme}.png`) })).data));
    }
    check('themes-visually-differ', new Set(themeHashes).size === 3);
    await page.evaluate(() => window.assetFixture.setTheme('neutral'));
    for (const character of result.info.characters) {
      const hashes = [];
      for (const visible of [true, false, true]) {
        await page.evaluate(({ character, visible }) => window.assetFixture.setCharacterVisible(character, visible), { character, visible });
        hashes.push(sha(PNG.sync.read(await canvas.screenshot()).data));
      }
      check(`character-toggle-${character}`, hashes[0] === hashes[2] && hashes[0] !== hashes[1]);
    }
    if (await page.locator('#sampling-section').isVisible()) {
      const count = await page.evaluate(() => window.assetFixture.setSampling(true, 160));
      check('surface-sample-2000', count === 2000);
      const first = PNG.sync.read(await canvas.screenshot()).data;
      await page.evaluate(() => window.assetFixture.setSampling(true, 160));
      check('seeded-sampling-repeat-pixels', first.equals(PNG.sync.read(await canvas.screenshot()).data));
      await canvas.screenshot({ path: path.join(out, `${name}-surface-2000.png`) });
      await page.evaluate(() => window.assetFixture.setSampling(false));
    }
    check('no-page-errors', pageErrors.length === 0, pageErrors);
  }
  report.state = 'passed';
} catch (error) {
  if (report.state !== 'blocked') report.state = 'failed';
  if (!report.errors.includes(error.message)) report.errors.push(error.message);
  process.exitCode = report.state === 'blocked' ? 2 : 1;
} finally {
  await browser?.close();
  if (server) await new Promise(resolve => server.close(resolve));
  await writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(`${report.state.toUpperCase()}: ${path.relative(root, path.join(out, 'report.json'))}`);
}
