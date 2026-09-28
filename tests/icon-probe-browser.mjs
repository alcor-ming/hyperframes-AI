// Isolated image provenance regression: all HTTP requests are fixture responses.
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import path from 'node:path';
import {inspectFrame} from '../.studio/visual_probe.mjs';

const {HF_PACKAGE, CHROME_PATH} = process.env;
assert(HF_PACKAGE && CHROME_PATH, 'Set HF_PACKAGE and CHROME_PATH');
const {launch} = createRequire(path.join(HF_PACKAGE, 'package.json'))('puppeteer-core');
const browser = await launch({executablePath: CHROME_PATH, headless: true, args: ['--no-sandbox'],
  timeout: 10000, protocolTimeout: 10000});
try {
  const page = await browser.newPage();
  page.setDefaultTimeout(10000);
  const svg = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" data-icon="test:line@1.0.0"><title>中文</title><path d="M2 22v-5"/></svg>';
  const sources = {
    local: '/icon.svg',
    base64: 'data:image/svg+xml;base64,' + Buffer.from(svg).toString('base64'),
    percent: 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg),
    badbase64: 'data:image/svg+xml;base64,not valid base64!',
    badpercent: 'data:image/svg+xml,%XX',
    badxml: 'data:image/svg+xml,' + encodeURIComponent('<svg><path>'),
    unavailable: '/unavailable.svg',
    cross: 'http://external.invalid/icon.svg',
    redirect: '/redirect.svg',
    raster: 'data:image/png;base64,broken',
  };
  await page.setRequestInterception(true);
  page.on('request', request => {
    const url = new URL(request.url());
    if (url.protocol === 'data:') { void request.continue(); return; }
    if (url.pathname === '/redirect.svg') {
      void request.respond({status: 302, headers: {location: 'http://external.invalid/icon.svg'}});
    } else if (url.pathname.endsWith('.svg')) {
      void request.respond({status: url.pathname === '/unavailable.svg' ? 403 : 200,
        contentType: 'image/svg+xml', body: svg});
    } else {
      void request.respond({status: 200, contentType: 'text/html', body:
        '<style>img{width:24px;height:24px;margin:5px}</style>' + Object.entries(sources)
          .map(([id, src]) => `<img id="${id}" src="${src.replaceAll('&', '&amp;').replaceAll('"', '&quot;')}">`).join('')});
    }
  });
  await page.goto('http://localhost/icon-fixture', {waitUntil: 'load'});
  await page.evaluate(() => {
    const original = window.fetch;
    window.probeFetches = [];
    window.fetch = (...args) => { window.probeFetches.push(String(args[0])); return original(...args); };
  });
  const report = await page.evaluate(inspectFrame, [], 0);
  assert.deepEqual(report.icons.map(icon => icon.target).sort(), ['#base64', '#local', '#percent'],
    'Studio data URL SVGs must be sampled alongside local SVG files');
  for (const icon of report.icons) assert.equal(icon.svg, svg, 'UTF-8 and SVG geometry remain intact');
  for (const id of ['badbase64', 'badpercent', 'badxml', 'unavailable', 'cross', 'redirect'])
    assert(report.unverified.some(message => message.includes('#' + id)), id + ' must be explicitly unverified');
  assert(!report.unverified.some(message => message.includes('#raster')), 'raster is not an SVG provenance failure');
  const fetches = await page.evaluate(() => window.probeFetches);
  assert(!fetches.some(url => url.includes('external.invalid')), 'diagnostics must not fetch external SVG sources');
  console.log(JSON.stringify({checks: ['local-svg', 'studio-base64-svg', 'percent-utf8-svg',
    'malformed-data-unverified', 'unavailable-unverified', 'cross-origin-no-fetch', 'redirect-rejected'], icons: report.icons.length}));
} finally { await browser.close(); }
