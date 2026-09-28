// Companion editor UI only: the iframe is a local stub, not native Studio acceptance.
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import fs from 'node:fs/promises';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const require = createRequire(path.join(root, '.studio/remotion/package.json'));
const {chromium} = require('playwright-core');
const temporary = await fs.mkdtemp(path.join(os.tmpdir(), 'card-editor-fixture-'));
const output = await fs.mkdtemp(path.join(os.tmpdir(), 'card-editor-ui-'));
const planPath = path.join(temporary, 'ANIMATION_PLAN.md');
const body = 'preset: F01\narea: full\ntitle: Before @hello\n- Row @row\nnote: Note @note';
const plan = '---\n{"plan_format":"3.5.2"}\n---\n## S01\n```card C1 · P001\n' + body + '\n```\n'
  + '```card C2 · P002\npreset: F02\narea: left\n- Other @other\n```\n';
await fs.writeFile(planPath, plan);
const studio = http.createServer((_, response) => {
  response.setHeader('Content-Type', 'text/html; charset=utf-8');
  response.end('<!doctype html><html><meta charset="utf-8"><style>body{margin:0;background:#edf0f2;color:#31363b;font:20px system-ui}header{padding:16px;background:#fff;border-bottom:1px solid #ccd3da}main{padding:32px}h1{font-size:24px}</style><header>Studio fixture</header><main><h1>S01</h1></main></html>');
});
let browser, child, capability = '';
try {
  await new Promise(resolve => studio.listen(0, '127.0.0.1', resolve));
  child = spawn('python3', ['-u', '-c', `
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from card_editor import serve
from card_build import replace_card
plan = Path(sys.argv[2])
def save(data):
    candidate = replace_card(plan.read_text(), data['card'], data['body'])
    plan.write_text(candidate)
serve(plan, plan.parent, sys.argv[3], save)
`, path.join(root, '.studio'), planPath, `http://127.0.0.1:${studio.address().port}/`], {stdio: ['ignore', 'pipe', 'pipe']});
  capability = await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(Error('Editor startup timeout')), 10000);
    let text = '';
    child.stdout.on('data', chunk => {
      text += chunk;
      if (text.includes('\n')) { clearTimeout(timer); resolve(text.split('\n')[0].trim()); }
    });
    child.on('error', error => { clearTimeout(timer); reject(error); });
    child.on('exit', () => { clearTimeout(timer); reject(Error('Editor exited before readiness')); });
  });
  browser = await chromium.launch({executablePath: process.env.HF_CARD_BROWSER || '/opt/google/chrome/chrome',
    headless: true, args: ['--no-sandbox']});
  const page = await browser.newPage({viewport: {width: 1280, height: 720}});
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(capability);
  await page.waitForFunction(() => document.querySelector('#body').value.includes('Before'));
  assert.equal(new URL(page.url()).hash, '');
  await page.frameLocator('#studio').getByRole('heading', {name: 'S01'}).waitFor();
  await page.locator('#body').fill(body.replace('Before', 'Unsaved'));
  assert.equal(await page.locator('#status').textContent(), '未保存');
  page.once('dialog', dialog => dialog.dismiss());
  await page.locator('#reload').click();
  assert.match(await page.locator('#body').inputValue(), /Unsaved/);
  page.once('dialog', dialog => dialog.dismiss());
  await page.locator('#card').selectOption('C2');
  assert.equal(await page.locator('#card').inputValue(), 'C1');
  assert.match(await page.locator('#body').inputValue(), /Unsaved/);
  await fs.writeFile(planPath, plan.replace('Before', 'External'));
  await page.locator('#save').click();
  await page.waitForFunction(() => document.querySelector('#status').textContent.includes('Plan changed'));
  assert.match(await page.locator('#body').inputValue(), /Unsaved/);
  assert.match(await fs.readFile(planPath, 'utf8'), /External/);
  page.once('dialog', dialog => dialog.accept());
  await page.locator('#reload').click();
  await page.waitForFunction(() => document.querySelector('#body').value.includes('External'));
  await page.locator('#body').fill(body.replace('Before', 'Saved'));
  await page.locator('#save').click();
  await page.waitForFunction(() => document.querySelector('#status').textContent === '已保存');
  assert.match(await fs.readFile(planPath, 'utf8'), /Saved/);
  assert.doesNotMatch(await fs.readFile(planPath, 'utf8'), /External|Unsaved/);
  for (const [name, width, height] of [['desktop', 1280, 720], ['mobile', 390, 844]]) {
    await page.setViewportSize({width, height});
    const bounds = await page.evaluate(() => {
      const box = selector => {
        const {x, y, width, height} = document.querySelector(selector).getBoundingClientRect();
        return {x, y, width, height};
      };
      return {aside: box('aside'), frame: box('iframe'), body: box('#body'), footer: box('footer'),
        scroll: document.documentElement.scrollWidth, width: innerWidth};
    });
    assert(bounds.scroll <= bounds.width, `${name}: horizontal overflow`);
    assert(bounds.body.y + bounds.body.height <= bounds.footer.y + 1, `${name}: textarea overlaps footer`);
    assert(bounds.aside.x + bounds.aside.width <= bounds.frame.x + 1
      || bounds.aside.y + bounds.aside.height <= bounds.frame.y + 1, `${name}: editor overlaps preview`);
    assert(bounds.body.height >= 70 && bounds.frame.height > 200, `${name}: collapsed workspace`);
    await page.screenshot({path: path.join(output, `${name}.png`), fullPage: true});
  }
  assert.deepEqual(errors, []);
  console.log(JSON.stringify({checks: ['save', 'stale-write', 'dirty-cancel', 'desktop-layout', 'mobile-layout'],
    screenshots: output, iframe: 'local stub, not native Studio'}));
} catch (error) {
  const secret = capability.split('#')[1];
  console.error(String(error.stack || error).replaceAll(capability || '__no_url__', '[editor session]')
    .replaceAll(secret || '__no_token__', '[session token]'));
  process.exitCode = 1;
} finally {
  await browser?.close();
  if (child && child.exitCode === null) {
    await new Promise(resolve => {
      const timer = setTimeout(() => child.kill('SIGKILL'), 3000);
      child.once('exit', () => { clearTimeout(timer); resolve(); });
      child.kill('SIGINT');
    });
  }
  await new Promise(resolve => studio.close(resolve));
  await fs.rm(temporary, {recursive: true, force: true});
}
