// Isolated DOM capacity check; never renders or encodes video.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import http from 'node:http';
import {createRequire} from 'node:module';
const project = path.resolve(process.argv[2]);
const sources = JSON.parse(process.argv[3]);
const require = createRequire(import.meta.url);
let chromium;
try { ({chromium} = require('playwright-core')); }
catch { ({chromium} = createRequire(new URL('./remotion/package.json', import.meta.url))('playwright-core')); }
const server = http.createServer(async (request, response) => {
  try {
    const pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
    const file = path.resolve(project, '.' + pathname);
    assert(file.startsWith(project + path.sep));
    const actual = await fs.realpath(file);
    assert(actual.startsWith(project + path.sep));
    const types = {'.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.html': 'text/html', '.json': 'application/json', '.svg': 'image/svg+xml'};
    response.setHeader('Content-Type', (types[path.extname(file)] || 'application/octet-stream') + '; charset=utf-8');
    response.end(await fs.readFile(file));
  } catch { response.writeHead(404).end(); }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
let browser;
try {
  browser = await chromium.launch({executablePath: process.argv[4] || process.env.HYPERFRAMES_BROWSER_PATH || process.env.CHROME_PATH,
    headless: true, args: ['--no-sandbox']});
  const origin = `http://127.0.0.1:${server.address().port}`;
  for (const source of sources) {
    const page = await browser.newPage({viewport: {width: 1920, height: 1920}});
    await page.route('**/*', route => new URL(route.request().url()).origin === origin ? route.continue() : route.abort());
    await page.goto(origin + '/' + source.split('/').map(encodeURIComponent).join('/'));
    await page.waitForFunction(() => window.__hfCardBuildReady || window.__hfCardBuildError, null, {timeout: 15000});
    const count = await page.evaluate(async () => {
      if (window.__hfCardBuildError) throw Error(window.__hfCardBuildError);
      const groups = await window.__hfCardBuildReady;
      await document.fonts.ready;
      for (const group of groups.values()) {
        await group.renderAt(group.scene.start + group.scene.duration / 2);
        if (document.querySelector('[data-overflow="true"]')) throw Error('Card overflow');
      }
      return [...groups.values()].reduce((sum, group) => sum + group.instances.length, 0);
    });
    assert(count > 0, 'Generated card scene is empty');
    await page.close();
  }
  console.log(JSON.stringify({sources: sources.length, capacity: 'checked', scope: 'DOM only'}));
} finally {
  await browser?.close();
  await new Promise(resolve => server.close(resolve));
}
