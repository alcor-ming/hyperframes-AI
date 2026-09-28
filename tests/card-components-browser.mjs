// CHROME_PATH=<local Chromium> node tests/card-components-browser.mjs
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import http from 'node:http';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const {chromium} = createRequire(path.join(repo, '.studio/remotion/package.json'))('playwright-core');
const output = await fs.mkdtemp(path.join(os.tmpdir(), 'hf-card-components-'));
const families = await fs.readdir(path.join(repo, '.studio/components'));
const html = `<!doctype html><style>
:root{--hf-color-canvas:#142728;--hf-color-surface:#233a3c;--hf-color-text-primary:#f6f7f8;--hf-color-text-secondary:#adc6c5;--hf-color-accent-primary:#62d4b0;--hf-color-accent-secondary:#ecac67;--hf-font-body:sans-serif;--hf-font-display:sans-serif;--hf-font-mono:monospace}
body{margin:0;background:#142728}[data-hf-layer]{position:absolute;inset:0}
</style><div id="stage" data-hf-layer="stage"></div><div id="text" data-hf-layer="text"></div><script src="/runtime/card-component.js"></script>
<script>
const query=new URLSearchParams(location.search),source=query.get('source'),parts=source.split('/');
const stage=document.getElementById('stage'),text=document.getElementById('text');
window.hostile='</scr'+'ipt><script>window.injected=true</scr'+'ipt>';
window.scale=Number(query.get('scale')||1);
for(const [layer,target] of [['stage',stage],['text',text]]) Object.assign(target.dataset,{
 cardSource:source,cardId:parts[2],componentRef:parts[2]+'/'+parts[3]+'@v2',componentBinding:'component-bindings/S1.json',cardLayer:layer,
 width:parts[3]==='16x9'?'1920':'1080',height:parts[3]==='16x9'?'1080':'1920',start:'0',variableValues:JSON.stringify({time_scale:scale,label:hostile})
});
window.ready=HarnessCardComponent.mount({stage,text}).then(c=>window.component=c)
</script>`;
const server = http.createServer(async (request, response) => {
  try {
    const url = new URL(request.url, 'http://localhost');
    if (url.pathname === '/') return response.end(html);
    const file = path.resolve(repo, '.studio', '.' + decodeURIComponent(url.pathname));
    assert(file.startsWith(path.join(repo, '.studio/components/') ) || file === path.join(repo, '.studio/runtime/card-component.js'));
    response.setHeader('Content-Type', path.extname(file) === '.js' ? 'application/javascript' : 'text/html');
    response.end(await fs.readFile(file));
  } catch { response.writeHead(404).end(); }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const browser = await chromium.launch({executablePath:process.env.CHROME_PATH, headless:true,args:['--no-sandbox']});
const page = await browser.newPage();
const errors = [], results = [];
page.on('pageerror', error => errors.push(error.message));
try {
  for (const ratio of ['16x9','9x16']) {
    const shots = [];
    await page.setViewportSize(ratio === '16x9' ? {width:640,height:360} : {width:360,height:640});
    for (const family of families.sort()) {
      try { await fs.access(path.join(repo,'.studio/components',family,ratio,'v2/component.html')); } catch { continue; }
      await page.goto(`http://127.0.0.1:${server.address().port}/?source=/components/${family}/${ratio}/v2/component.html&scale=${family === 'cover-title-core' ? '1.2' : '1'}`);
      await page.evaluate(() => ready);
      const result = await page.evaluate(() => {
        const frame = component.text, doc = frame.contentDocument, root = doc.querySelector('[data-composition-id]');
        const duration = Number(root.dataset.duration);
        component.renderAt(0.5);
        for (const f of [component.text, component.decorations]) {
          if (f.contentWindow.injected || f.contentWindow.__hyperframes.getVariables().label !== hostile) throw new Error('Card variable script injection');
          if (Math.abs(f.contentWindow.__timelines[root.dataset.compositionId].time() - 0.5 * scale) > 1e-6) throw new Error('Card time_scale applied incorrectly');
        }
        component.renderAt(duration * 0.92 / scale);
        const width = Number(root.dataset.width), height = Number(root.dataset.height);
        const walker = doc.createTreeWalker(root, NodeFilter.SHOW_TEXT), visible = [], overflow = [];
        while (walker.nextNode()) {
          const node = walker.currentNode, el = node.parentElement;
          if (!node.textContent.trim() || ['STYLE','SCRIPT'].includes(el.tagName)) continue;
          let shown = true;
          for (let p = el; p; p = p.parentElement) {
            const style = frame.contentWindow.getComputedStyle(p);
            if (style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity) < 0.01) shown = false;
          }
          if (!shown) continue;
          const range = doc.createRange(); range.selectNodeContents(node);
          const box = range.getBoundingClientRect();
          if (!box.width || !box.height) continue;
          visible.push(node.textContent.trim());
          if (box.left < -1 || box.top < -1 || box.right > width + 1 || box.bottom > height + 1) overflow.push({text:node.textContent.trim(),box:box.toJSON()});
        }
        return {duration,visible,overflow};
      });
      const filename = `${family}-${ratio}.png`;
      // Match the host seek test: scaled iframe paint follows synchronous DOM seek.
      await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
      const png = await page.screenshot({path:path.join(output,filename)});
      await page.evaluate(duration => {component.renderAt(0);component.renderAt(duration * 0.92 / scale);}, result.duration);
      await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
      assert(png.equals(await page.screenshot({path:path.join(output,`${family}-${ratio}-repeat.png`)})), `${family}/${ratio} seek changed pixels`);
      shots.push({family,png:png.toString('base64')});
      results.push({family,ratio,...result});
      assert(result.visible.length, `${family}/${ratio} has no visible text`);
    }
    await page.setViewportSize({width:1280,height:ratio === '16x9' ? 1040 : 3000});
    await page.setContent('<style>body{margin:0;background:#eee;display:grid;grid-template-columns:repeat(4,1fr);gap:8px;font:12px sans-serif}figure{margin:0}img{width:100%;display:block}</style>' + shots.map(({family,png})=>`<figure><figcaption>${family}</figcaption><img src="data:image/png;base64,${png}"></figure>`).join(''));
    await page.screenshot({path:path.join(output,`contact-${ratio}.png`),fullPage:true});
  }
  assert.equal(results.length,40);
  assert.deepEqual(errors,[]);
  assert.deepEqual(results.filter(result=>result.overflow.length).map(({family,ratio,overflow})=>({family,ratio,overflow})),[]);
} finally {
  await fs.writeFile(path.join(output,'evidence.json'),JSON.stringify({scope:'WSL Chromium only',results,errors},null,2));
  console.log(output);
  await browser.close(); await new Promise(resolve=>server.close(resolve));
}
