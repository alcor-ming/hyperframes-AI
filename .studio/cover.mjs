import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL, fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const here = path.dirname(fileURLToPath(import.meta.url));
const runtime = path.join(here, '../runtime/npm/package.json');
const require = createRequire(fs.existsSync(runtime) ? runtime : path.join(here, 'parser/package.json'));
const [directory, width, height] = process.argv.slice(2);
const native = process.platform === 'win32';
const launch = {headless:true, executablePath:process.env.CHROME_PATH || process.env.HYPERFRAMES_BROWSER_PATH};
const browser = native ? await require('puppeteer-core').launch(launch)
  : await require('playwright-core').chromium.launch(launch);
try {
  const viewport = {width:Number(width),height:Number(height)};
  const page = native ? await browser.newPage() : await browser.newPage({viewport,deviceScaleFactor:1});
  const allowed = value => {
    const url = new URL(value);
    return url.protocol === 'file:' && path.dirname(fileURLToPath(url)) === path.resolve(directory);
  };
  if (native) {
    await page.setViewport({...viewport,deviceScaleFactor:1});
    await page.setRequestInterception(true);
    page.on('request', request => allowed(request.url()) ? request.continue() : request.abort());
  } else await page.route('**/*', route => allowed(route.request().url()) ? route.continue() : route.abort());
  await page.goto(pathToFileURL(path.join(directory,'index.html')).href);
  await page.evaluate(async () => {
    await document.fonts.ready;
    await Promise.all([...document.images].map(image => image.decode()));
    if (!document.fonts.check('16px Cover')) throw Error('Cover font missing');
    const heading = document.querySelector('h1'), logo = document.querySelector('.logo');
    if (heading.getBoundingClientRect().bottom >= logo.getBoundingClientRect().top) throw Error('Cover title overlaps Logo');
    if (heading.scrollWidth > heading.clientWidth || heading.scrollHeight > heading.clientHeight) throw Error(`Cover title overflow: ${heading.scrollWidth}x${heading.scrollHeight} in ${heading.clientWidth}x${heading.clientHeight}`);
  });
  await page.screenshot({path:path.join(directory,'cover.png')});
} finally { await browser.close(); }
