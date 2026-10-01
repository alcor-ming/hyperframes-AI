// Isolated font and layout preflight, never video rendering.
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
    assert((await fs.realpath(file)).startsWith(project + path.sep));
    const types = {'.js': 'text/javascript', '.css': 'text/css', '.html': 'text/html', '.json': 'application/json', '.ttf': 'font/ttf', '.woff2': 'font/woff2', '.woff': 'font/woff'};
    const type = types[path.extname(file)] || 'application/octet-stream';
    response.setHeader('Content-Type', type + (type.startsWith('text/') || type === 'application/json' ? '; charset=utf-8' : ''));
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
    await page.waitForFunction(() => window.__hfMathBuildReady || window.__hfMathBuildError, null, {timeout: 15000});
    await page.evaluate(async () => {
      if (window.__hfMathBuildError) throw Error(window.__hfMathBuildError);
      const groups = await window.__hfMathBuildReady;
      await document.fonts.ready;
      if (!groups.size) throw Error('Generated math scene is empty');
      for (const group of groups.values()) {
        const end = group.scene.start + group.scene.duration;
        const times = [group.scene.start, end];
        for (const event of group.scene.intent.cues) {
          const at = group.cues.find(event.cue);
          times.push(at, Math.min(end - 0.001, at + 0.25));
          for (const item of group.scene.math.items)
            if (item.duration) times.push(Math.min(end - 0.001, at + item.duration));
        }
        for (const time of times) {
          await group.renderAt(time);
          if (document.querySelector('[data-overflow="true"]')) throw Error('Math overflow');
          for (const layer of Object.values(group.roots)) {
            const bounds = layer.parentElement.getBoundingClientRect();
            for (const node of layer.querySelectorAll('.hf-math-shape,.hf-math-line,.hf-math-tick,[data-hf-math-label]')) {
              const rect = node.getBoundingClientRect();
              if (rect.left < bounds.left - 1 || rect.top < bounds.top - 1 ||
                  rect.right > bounds.right + 1 || rect.bottom > bounds.bottom + 1)
                throw Error('Math geometry outside Scene frame');
            }
          }
        }
      }
      // Inspect even initially hidden glyph probes and labels, including all declared characters.
      for (const node of document.querySelectorAll('[data-hf-math-label], [data-hf-math-glyphs]')) {
        node.style.visibility = 'visible';
        node.style.display = 'block';
        node.style.opacity = '1';
        for (let parent = node.parentElement; parent; parent = parent.parentElement) {
          parent.style.visibility = 'visible';
          if (getComputedStyle(parent).display === 'none') parent.style.display = 'block';
        }
      }
      for (const probe of document.querySelectorAll('[data-hf-math-glyphs]')) {
        const characters = [...probe.textContent];
        probe.replaceChildren(...characters.map(character => {
          const node = document.createElement('span');
          node.dataset.hfMathGlyph = '';
          node.textContent = character;
          return node;
        }));
      }
      await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    });
    const cdp = await page.context().newCDPSession(page);
    await cdp.send('DOM.enable');
    await cdp.send('CSS.enable');
    const {root} = await cdp.send('DOM.getDocument', {depth: -1});
    const {nodeIds} = await cdp.send('DOM.querySelectorAll', {nodeId: root.nodeId,
      selector: '[data-hf-math-label], [data-hf-math-glyph]'});
    assert(nodeIds.length > 0, 'Missing frozen math font probes');
    for (const nodeId of nodeIds) {
      const {fonts} = await cdp.send('CSS.getPlatformFontsForNode', {nodeId});
      assert(fonts.length && fonts.every(font => font.isCustomFont && font.glyphCount > 0),
        'Math font missing glyphs or using fallback font');
    }
    await cdp.detach();
    await page.close();
  }
  console.log(JSON.stringify({sources: sources.length, fonts: 'checked', scope: 'DOM only'}));
} finally {
  await browser?.close();
  await new Promise(resolve => server.close(resolve));
}
