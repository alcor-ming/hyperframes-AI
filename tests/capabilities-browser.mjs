// Synthetic appearance Lock parity, including a mode-free module Background.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const { chromium } = createRequire(path.join(repo, '.studio/parser/package.json'))('playwright-core');
const runtime = await fs.readFile(path.join(repo, '.studio/runtime/appearance.js'), 'utf8');
const figuresRuntime = await fs.readFile(path.join(repo, '.studio/runtime/figures.js'), 'utf8');
const background = { ref: 'background@v1', kind: 'background', vendor_path: 'background', package_sha256: 'fixture' };
const caps = { layers: { required: ['background'], optional: [] }, rolls: false,
  bindings: { theme: 'optional', background: 'optional', motion: 'optional' }, checks: [], research_template: 'RESEARCH.template.md' };
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome', headless: true, args: ['--no-sandbox'] });
try {
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  for (const modern of [false, true]) {
    background.ref = modern ? 'sample/background@v1' : 'background@v1';
    const lock = { schema_version: 1, contract_version: 1, resolver_version: 1, assets: [background],
      ...(modern ? { capabilities: caps } : { mode: 'showcase' }),
      selection: { theme: null, background, motion: {} }, parameters: { theme: {}, background: {}, motion: {} } };
    const files = {
      '/': '<main></main><script src="appearance.js"></script><script src="figures.js"></script>',
      '/appearance.js': runtime,
      '/figures.js': figuresRuntime,
      '/character/asset.json': JSON.stringify({id:'character',version:1,kind:'character',entry:'entry.json',dependencies:['normal.svg']}),
      '/character/HASHES.json': JSON.stringify({card_ref:'sample/character',component_ref:'sample/character@v1',package_sha256:'fixture'}),
      '/character/entry.json': JSON.stringify({default_state:'normal',states:{normal:{file:'normal.svg',anchor:[0,0],facing:'right'}}}),
      '/character/normal.svg': '<svg xmlns="http://www.w3.org/2000/svg" width="2" height="2"><rect width="2" height="2"/></svg>',
      '/appearance-lock.json': JSON.stringify(lock),
      '/background/asset.json': JSON.stringify({ id: 'background', version: 1, kind: 'background', contract_version: 1, entry: 'entry.json', dependencies: ['module.js'] }),
      '/background/HASHES.json': JSON.stringify({card_ref:'sample/background',component_ref:background.ref,package_sha256:'fixture'}),
      '/background/entry.json': JSON.stringify({ renderer: 'module', entry: 'module.js', parameters: {} }),
      '/background/module.js': 'export function create(host) { return { renderAt(t) { host.textContent=String(t); }, dispose() { host.textContent=""; } }; }',
    };
    await page.route('**/*', route => {
      const url = new URL(route.request().url());
      const body = url.origin === 'http://fixture.test' && files[url.pathname];
      return body ? route.fulfill({ body, contentType: url.pathname.endsWith('.svg') ? 'image/svg+xml' : url.pathname.endsWith('.js') ? 'text/javascript' : url.pathname.endsWith('.json') ? 'application/json' : 'text/html' }) : route.abort();
    });
    await page.goto('http://fixture.test/');
    const result = await page.evaluate(async () => {
      const appearance = await HarnessAppearance.load();
      const host = document.querySelector('main');
      HarnessAppearance.apply(host, appearance);
      const binding = await HarnessAppearance.mountBackground(host, appearance, { find() {} });
      const frames = [2, 0, 2, 1].map(t => { binding.renderAt(t); return host.textContent; });
      binding.dispose();
      return { frames, final: host.textContent, theme: appearance.theme };
    });
    assert.deepEqual(result, { frames: ['2', '0', '2', '1'], final: '', theme: null });
    await page.evaluate(modern => HarnessFigures.load({assets:[{kind:'character',ref:modern?'sample/character@v1':'character@v1',vendor_path:'character',package_sha256:'fixture'}]},{cues:{find:value=>value}}).then(() => true), modern);
    if (modern) {
      files['/background/HASHES.json'] = JSON.stringify({card_ref:'wrong/background',component_ref:'wrong/background@v1',package_sha256:'fixture'});
      await assert.rejects(page.evaluate(() => HarnessAppearance.load()), /card identity mismatch/);
    }
    await page.unrouteAll();
  }
  assert.deepEqual(errors, []);
  console.log('Legacy and capabilities-only Lock: load, optional bindings, module Background, repeat/backward seek, dispose passed');
} finally { await browser.close(); }
