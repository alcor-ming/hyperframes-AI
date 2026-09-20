// PLAYWRIGHT_PACKAGE=/path/to/playwright node tests/appearance-fonts.mjs
// Real browser + local system font; isolated packages, not production assets.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import http from 'node:http';
import { createRequire } from 'node:module';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const require = createRequire(process.env.PLAYWRIGHT_PACKAGE ? path.join(process.env.PLAYWRIGHT_PACKAGE, 'package.json') : import.meta.url);
const { chromium } = require('playwright');
const output = await fs.mkdtemp(path.join(os.tmpdir(), 'hf-fonts-'));
const font = process.env.TEST_CHINESE_FONT || '/usr/share/fonts/opentype/unifont/unifont.otf';
const license = process.env.TEST_CHINESE_FONT_LICENSE || '/usr/share/doc/fonts-unifont/copyright';
const build = spawnSync('python3', ['-c', `
import json, os, pathlib, shutil, sys
sys.path.insert(0,str(pathlib.Path(sys.argv[1])/'.studio'))
import asset_store as store, appearance
root=pathlib.Path(sys.argv[2]); harness=root/'harness'; harness.mkdir()
os.environ.update(HYPERFRAMES_AI_ASSET_CONFIG=str(root/'config.json'),HYPERFRAMES_AI_ROOT=str(harness),HYPERFRAMES_AI_ASSET_ROOT='')
assets=root/'store'; store.configure_asset_store(harness,assets)
refs={}
for name in ('first','second','plain','background'):
 source=root/name; source.mkdir(); kind='background' if name=='background' else 'theme'
 payload={'renderer':'solid','parameters':{'color':'#ffffff'}} if kind=='background' else {'tokens':{'typography':{'body':'"Fixture Chinese", serif'},'colors':{'text':'#000000'}}}
 dependencies=[]
 if name in ('first','second'):
  shutil.copyfile(sys.argv[3],source/'local font.otf'); shutil.copyfile(sys.argv[4],source/'LICENSE.txt')
  dependencies=['local font.otf','LICENSE.txt']
  payload['fonts']=[{'family':'Fixture Chinese','path':'local font.otf','license':'LICENSE.txt','style':style,'weight':weight} for style,weight in [('normal','100 900'),('italic',400)]]
 (source/'asset.json').write_text(json.dumps({'schema_version':2,'id':name,'version':1,'kind':kind,'entry':'entry.json','contract_version':1,'parameters':{},'compatibility':{},'dependencies':dependencies}))
 (source/'entry.json').write_text(json.dumps(payload))
 candidate=store.pack_source(assets,source)
 store.accept_component(assets,candidate['component_ref'],candidate['package_sha256'],'Isolated local-font browser test',runtime_root=harness)
 refs[name]={'ref':candidate['component_ref'],'kind':kind,'package_sha256':candidate['package_sha256']}
for name in ('first','second','plain'):
 project=root/('project-'+name); project.mkdir()
 account={'id':'fixture','revision':1,'theme':refs[name],'background':refs['background'],'ratio':'16:9','motion':{}}
 lock=appearance.resolve(harness,account); appearance.materialize(harness,project,lock)
 appearance.verify(project,lock)
shutil.rmtree(assets)
`, repo, output, font, license], { encoding: 'utf8' });
assert.equal(build.status, 0, build.stderr);
await fs.writeFile(path.join(output, 'index.html'), `<!doctype html><meta charset="utf-8"><style>
p { font-family:var(--appearance-typography-body); font-size:32px; display:inline-block }
</style><main id="one"><p id="text" data-appearance-text>&#20013;&#25991;&#23383;&#20307;</p></main><main id="two"><p>&#20013;&#25991;&#23383;&#20307;</p></main><script src="project-first/runtime/appearance.js"></script>`);
let fontRequests = 0;
const server = http.createServer(async (request, response) => {
  try {
    const relative = decodeURIComponent(new URL(request.url, 'http://localhost').pathname).slice(1);
    assert(relative && !relative.split('/').includes('..'));
    if (relative.endsWith('font.otf')) fontRequests++;
    const data = await fs.readFile(path.join(output, relative));
    response.setHeader('Content-Type', relative.endsWith('.js') ? 'application/javascript' : relative.endsWith('.json') ? 'application/json' : relative.endsWith('.otf') ? 'font/otf' : 'text/html');
    response.end(data);
  } catch { response.writeHead(404); response.end(); }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
let browser;
try {
  browser = await chromium.launch({ headless: true, ...(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {}) });
  const page = await browser.newPage();
  await page.goto(`http://127.0.0.1:${server.address().port}/index.html`);
  const loaded = await page.evaluate(async () => {
    const before = document.fonts.size;
    window.first = await HarnessAppearance.load('./project-first/');
    HarnessAppearance.apply(document.querySelector('#one'), first);
    const width = document.querySelector('#text').getBoundingClientRect().width;
    const family = getComputedStyle(document.querySelector('#text')).fontFamily;
    const faces = [...document.fonts].map(face => ({ family: face.family, status: face.status, style: face.style, weight: face.weight }));
    HarnessAppearance.apply(document.querySelector('#one'), first);
    await new Promise(resolve => setTimeout(resolve, 100));
    return { before, width, afterWidth: document.querySelector('#text').getBoundingClientRect().width, family, faces, count: document.fonts.size };
  });
  assert.equal(loaded.count - loaded.before, 2);
  assert.equal(loaded.width, loaded.afterWidth);
  assert(loaded.family.includes('HarnessFont_'));
  assert(loaded.faces.every(face => face.status === 'loaded'));
  assert(loaded.faces.some(face => face.style === 'normal' && face.weight === '100 900'));
  assert(loaded.faces.some(face => face.style === 'italic' && face.weight === '400'));
  assert.equal(fontRequests, 2, 'Repeated apply does not reload fonts');
  const session = await page.context().newCDPSession(page);
  await session.send('DOM.enable');
  await session.send('CSS.enable');
  const { root } = await session.send('DOM.getDocument');
  const { nodeId } = await session.send('DOM.querySelector', { nodeId: root.nodeId, selector: '#text' });
  const used = await session.send('CSS.getPlatformFontsForNode', { nodeId });
  assert(used.fonts.some(font => font.isCustomFont && font.glyphCount >= 4), 'Chinese glyphs must use the loaded local font, not system fallback');
  const isolated = await page.evaluate(async () => {
    window.second = await HarnessAppearance.load('./project-second/');
    window.repeated = await HarnessAppearance.load('./project-first/');
    HarnessAppearance.apply(document.querySelector('#two'), second);
    const family = getComputedStyle(document.querySelector('#two p')).fontFamily;
    const width = document.querySelector('#two p').getBoundingClientRect().width;
    const before = document.fonts.size;
    first.dispose(); first.dispose(); repeated.dispose();
    let rejected = false;
    try { HarnessAppearance.apply(document.querySelector('#one'), first); } catch { rejected = true; }
    HarnessAppearance.apply(document.querySelector('#two'), second);
    return { family, width, afterWidth: document.querySelector('#two p').getBoundingClientRect().width, before, count: document.fonts.size, rejected };
  });
  assert.notEqual(isolated.family, loaded.family);
  assert.equal(isolated.before - isolated.count, 4);
  assert.equal(isolated.width, isolated.afterWidth);
  assert.equal(isolated.rejected, true);
  const secondNode = await session.send('DOM.querySelector', { nodeId: root.nodeId, selector: '#two p' });
  const stillUsed = await session.send('CSS.getPlatformFontsForNode', { nodeId: secondNode.nodeId });
  assert(stillUsed.fonts.some(font => font.isCustomFont && font.glyphCount >= 4), 'Disposing another instance must not remove this instance font');
  const declaration = path.join(output, 'project-first/vendor/components/first/v1/entry.json');
  const metadataPath = path.join(output, 'project-first/vendor/components/first/v1/asset.json');
  const metadata = JSON.parse(await fs.readFile(metadataPath, 'utf8'));
  const original = JSON.parse(await fs.readFile(declaration, 'utf8'));
  for (const failure of ['missing', 'corrupt', 'escape', 'redirect']) {
    const payload = structuredClone(original);
    const fontPath = path.join(output, 'project-first/vendor/components/first/v1/local font.otf');
    if (failure === 'missing') await fs.rename(fontPath, `${fontPath}.saved`);
    if (failure === 'corrupt') await fs.writeFile(fontPath, 'not a font');
    if (failure === 'escape') {
      payload.fonts[1].path = '../font.otf';
      await fs.writeFile(metadataPath, JSON.stringify({ ...metadata, dependencies: [...metadata.dependencies, '../font.otf'] }));
    }
    if (failure === 'redirect') await page.route('**/project-first/**/*font.otf', route => route.fulfill({ status: 302, headers: { location: '/project-second/vendor/components/second/v1/local%20font.otf' } }));
    await fs.writeFile(declaration, JSON.stringify(payload));
    const result = await page.evaluate(async () => {
      const before = document.fonts.size;
      try { await HarnessAppearance.load('./project-first/'); return { ready: true }; }
      catch (error) { return { ready: false, message: error.message, before, after: document.fonts.size }; }
    });
    assert.equal(result.ready, false, failure);
    assert.equal(result.before, result.after, `${failure}: partial font loading must be cleaned up`);
    assert(result.message.includes(failure === 'escape' ? 'project-local' : 'font'), result.message);
    if (failure === 'missing') await fs.rename(`${fontPath}.saved`, fontPath);
    if (failure === 'corrupt') await fs.copyFile(font, fontPath);
    if (failure === 'redirect') await page.unroute('**/project-first/**/*font.otf');
    if (failure === 'escape') await fs.writeFile(metadataPath, JSON.stringify(metadata));
  }
  await fs.writeFile(declaration, JSON.stringify(original));
  const plain = await page.evaluate(async () => {
    second.dispose();
    const plain = await HarnessAppearance.load('./project-plain/');
    HarnessAppearance.apply(document.querySelector('#one'), plain);
    plain.dispose();
    return document.fonts.size;
  });
  assert.equal(plain, loaded.before);
  await fs.writeFile(path.join(output, 'evidence.json'), JSON.stringify({ loaded, used, isolated }, null, 2));
  console.log(output);
} finally {
  if (browser) await browser.close();
  await new Promise(resolve => server.close(resolve));
}
