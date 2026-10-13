// node tests/english-example-cues.mjs <materialized-English-example>
import assert from 'node:assert/strict';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const {chromium} = createRequire(new URL('../.studio/parser/package.json', import.meta.url))('playwright-core');
const browser = await chromium.launch({executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome', headless: true, args: ['--no-sandbox']});
try {
  const check = async (start, invalid = false) => {
    const page = await browser.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.addInitScript(({start, invalid}) => {
      let data;
      Object.defineProperty(window, 'ENGLISH_EXAMPLE_WORDS', {
        get: () => data,
        set: words => {
          data = words;
          words[0].timing.repeats = [{start, end: invalid ? start : start + .6}];
        }
      });
    }, {start, invalid});
    await page.goto(pathToFileURL(path.resolve(process.argv[2], 'index.html')).href);
    if (invalid) {
      assert(errors.some(error => error.includes('repeat cue must fit')));
    } else {
      await page.evaluate(() => window.__example.ready);
      const state = async time => page.evaluate(async time => {
        await window.__example.seek(time);
        const scene = document.querySelector('[data-word="diligent"]');
        return {english: gsap.getProperty(scene.querySelector('.en-frag'), 'y'),
          chinese: getComputedStyle(scene.querySelector('.map-cn')).transform,
          parentheses: getComputedStyle(scene.querySelector('.paren')).transform};
      }, time);
      assert.equal((await state(start - .1)).english, 0);
      const active = await state(start + .1);
      assert(active.english < -5);
      assert.equal(active.chinese, 'none');
      assert.equal(active.parentheses, 'none');
      assert.equal((await state(start + .7)).english, 0);
      assert.deepEqual(await state(start + .1), active);
      assert.deepEqual(errors, []);
    }
    await page.close();
  };
  await check(6);
  await check(8);
  await check(6, true);
  console.log('PASS: changed repeat cues move only English fragments; invalid intervals rejected');
} finally { await browser.close(); }
