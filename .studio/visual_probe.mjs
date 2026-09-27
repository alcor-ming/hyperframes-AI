import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';

export const defaults = {step: 0.5, window: 2, pixel_delta: 12, area_ratio: 0.005, width: 960, timeout_ms: 5000};

export function changed(a, b, parameters) {
  if (!a || !b || a.length !== b.length) return true;
  let count = 0;
  for (let i = 0; i < a.length; i += 3) {
    if (Math.max(Math.abs(a[i] - b[i]), Math.abs(a[i + 1] - b[i + 1]),
      Math.abs(a[i + 2] - b[i + 2])) >= parameters.pixel_delta) count++;
  }
  return count / (a.length / 3) >= parameters.area_ratio;
}

export function isStill(samples, parameters) {
  if (samples.length < 3 || samples.some(sample => !sample.ready)) return false;
  // The channel envelope captures cumulative slow motion in linear time.
  const min = Buffer.from(samples[0].pixels), max = Buffer.from(min);
  for (const {pixels} of samples.slice(1)) {
    if (!pixels || pixels.length !== min.length) return false;
    for (let i = 0; i < pixels.length; i++) {
      min[i] = Math.min(min[i], pixels[i]); max[i] = Math.max(max[i], pixels[i]);
    }
    if (changed(min, max, parameters)) return false;
  }
  return true;
}

export function frameResourcesReady(time) {
  if (document.readyState !== 'complete' || document.fonts.status !== 'loaded') return false;
  return [...document.images].every(image => image.complete && image.naturalWidth > 0) &&
    [...document.querySelectorAll('video,audio')].every(media => {
      const start = Number.parseFloat(media.dataset.start ?? '0');
      if (!Number.isFinite(start) || !media.hasAttribute('data-start')) return false;
      // Match the pinned runtime's media clip mapping, including trimmed loops.
      const offset = value => value != null && value.trim() !== '' && Number.isFinite(Number(value)) && Number(value) >= 0
        ? Number(value) : null;
      const mediaStart = offset(media.dataset.playbackStart) ?? offset(media.dataset.mediaStart) ?? 0;
      const declaredRate = Number.parseFloat(media.dataset.playbackRate ?? '');
      const baseRate = Number.isFinite(declaredRate) && declaredRate > 0 ? declaredRate : media.defaultPlaybackRate;
      const rate = Number.isFinite(baseRate) && baseRate > 0 ? Math.max(0.1, Math.min(5, baseRate)) : 1;
      const sourceDuration = Number.isFinite(media.duration) && media.duration > 0 ? media.duration : null;
      let duration = Number.parseFloat(media.dataset.duration ?? '');
      if (!Number.isFinite(duration) || duration < 0)
        duration = sourceDuration == null ? Infinity : Math.max(0, (sourceDuration - mediaStart) / rate);
      if (time < start || time >= start + duration) return true;
      let expected = (time - start) * rate + mediaStart;
      if (sourceDuration != null && expected >= sourceDuration) {
        if (media.loop && sourceDuration > mediaStart)
          expected = mediaStart + (expected - mediaStart) % (sourceDuration - mediaStart);
        else if (!media.loop && media.tagName === 'VIDEO') expected = sourceDuration;
      }
      return !media.error && media.readyState >= 2 && !media.seeking && Math.abs(media.currentTime - expected) < 0.08;
    });
}

function inspectFrame(scenes, time) {
  const visible = element => {
    const rect = element.getBoundingClientRect();
    if (!rect.width || !rect.height || rect.bottom <= 0 || rect.right <= 0 ||
        rect.top >= innerHeight || rect.left >= innerWidth) return false;
    for (let parent = element; parent; parent = parent.parentElement) {
      const style = getComputedStyle(parent);
      if (style.display === 'none' || style.visibility !== 'visible' || +style.opacity < 0.02) return false;
    }
    return true;
  };
  const selector = element => {
    const parts = [];
    while (element && element !== document.documentElement) {
      if (element.id) { parts.unshift('#' + CSS.escape(element.id)); break; }
      const siblings = [...element.parentElement?.children || []].filter(item => item.tagName === element.tagName);
      parts.unshift(element.localName + ':nth-of-type(' + (siblings.indexOf(element) + 1) + ')');
      element = element.parentElement;
    }
    return parts.join(' > ');
  };
  const texts = [], unverified = new Set();
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const node = walker.currentNode, element = node.parentElement;
    if (!node.textContent.trim() || !element || element.closest('script,style,noscript') || !visible(element)) continue;
    const style = getComputedStyle(element);
    const transparent = color => color === 'transparent' || /rgba\([^)]*,\s*0(?:\.0+)?\)$/.test(color);
    if (element instanceof SVGElement ? (style.fill === 'none' || transparent(style.fill) || +style.fillOpacity === 0) &&
      (style.stroke === 'none' || transparent(style.stroke) || +style.strokeOpacity === 0)
      : transparent(style.webkitTextFillColor || style.color)) continue;
    const range = document.createRange(); range.selectNodeContents(node);
    const rects = [...range.getClientRects()];
    const exposed = rects.some(rect => {
      if (!rect.width || !rect.height) return false;
      return [0.2, 0.5, 0.8].some(fraction => {
        const top = document.elementsFromPoint(rect.left + rect.width * fraction, rect.top + rect.height / 2).find(visible);
        return top && (top === element || element.contains(top) ||
          getComputedStyle(element).pointerEvents === 'none' && top.contains(element));
      });
    });
    if (!exposed) continue;
    const info = element.closest('[data-info-id]')?.getAttribute('data-info-id') || null;
    const owner = element.closest('[data-scene-id]') || element.closest('[id]');
    let scene = owner?.getAttribute('data-scene-id');
    if (!scene) {
      let parent = element;
      while (parent) {
        if (scenes.some(item => item.id === parent.id)) { scene = parent.id; break; }
        parent = parent.parentElement;
      }
    }
    if (!scene) {
      const active = scenes.filter(item => time >= item.start && time < item.start + item.duration);
      if (active.length === 1) scene = active[0].id;
    }
    texts.push({scene: scene || null, info, text: node.textContent.trim(), selector: selector(element), frame: location.href,
      layer: element.closest('[data-hf-layer]')?.getAttribute('data-hf-layer') || null});
  }
  for (const element of document.querySelectorAll('*')) {
    if (!visible(element)) continue;
    if (element.shadowRoot) unverified.add('shadow DOM text is not extracted');
    if (['CANVAS', 'IMG', 'VIDEO'].includes(element.tagName)) unverified.add('canvas/image/video text is not OCR verified');
    if (['::before', '::after'].some(pseudo => !['none', 'normal', '""'].includes(getComputedStyle(element, pseudo).content)))
      unverified.add('pseudo-element text is not extracted');
  }
  const timeline = [];
  for (const [id, track] of Object.entries(window.__timelines || {})) {
    if (typeof track.getChildren !== 'function') continue;
    for (const tween of track.getChildren(true, true, false)) {
      const targets = tween.targets?.() || [];
      timeline.push({id, start: tween.globalTime?.(0) ?? tween.startTime(), duration: tween.totalDuration(),
        properties: Object.keys(tween.vars || {}).filter(key => !['duration', 'delay', 'ease', 'parent', 'overwrite'].includes(key)),
        targets: targets.map(target => target instanceof Element
          ? {selector: selector(target), visible: visible(target)} : {non_dom: true}),
        clue: targets.length && targets.every(target => !(target instanceof Element)) ? 'non-DOM/possibly empty tween; not a verdict' : null});
    }
  }
  return {texts, unverified: [...unverified], timeline};
}

export async function probe(input) {
  const deadline = Date.now() + 25 * 60 * 1000;
  const parameters = {...defaults, ...input.parameters};
  for (const key of Object.keys(defaults)) if (!Number.isFinite(parameters[key]) || parameters[key] <= 0)
    throw new Error('Invalid positive parameter: ' + key);
  if (parameters.step > parameters.window / 2 || parameters.area_ratio > 1 || parameters.pixel_delta > 255 ||
      parameters.width < 64 || parameters.width > 7680 || parameters.timeout_ms > 30000) throw new Error('Invalid sampling bounds');
  const url = new URL(input.url);
  if (!['http:', 'https:'].includes(url.protocol) || !['localhost', '127.0.0.1', '[::1]'].includes(url.hostname))
    throw new Error('Only an explicitly bound local Studio URL is allowed');
  const require = createRequire(input.cli), puppeteer = require('puppeteer-core'), sharp = require('sharp');
  const profile = await fs.mkdtemp(path.join(os.tmpdir(), 'hf-visual-probe-'));
  await fs.mkdir(path.join(profile, 'Default'));
  await fs.writeFile(path.join(profile, 'Default/Preferences'), JSON.stringify({enable_do_not_track: true}));
  const result = {samples: [], motion: [], timeline: [], unverified: ['Finite sampling does not cover text or motion between sample times; motion semantics require viewing.'], viewport: {}, parameters};
  let browser;
  try {
    browser = await puppeteer.launch({executablePath: input.browser, userDataDir: profile, headless: true, protocolTimeout: 30000,
      args: ['--disable-dev-shm-usage', '--disable-background-networking', '--disable-component-update',
        '--no-first-run', ...(process.platform === 'linux' ? ['--no-sandbox'] : [])]});
    const page = await browser.newPage();
    let navigation = 0;
    page.on('framenavigated', () => { navigation++; });
    await page.setViewport({width: Math.max(1280, Math.ceil(parameters.width + 64)), height: 1080, deviceScaleFactor: 1});
    await page.setRequestInterception(true);
    page.on('request', request => {
      const target = new URL(request.url());
      if (['http:', 'https:', 'ws:', 'wss:'].includes(target.protocol) && target.origin !== url.origin) {
        result.unverified.push('Blocked non-Studio resource: ' + target.origin);
        void request.abort();
      } else void request.continue();
    });
    await page.goto(url.href, {waitUntil: 'domcontentloaded', timeout: 30000});
    await page.waitForFunction(() => document.querySelector('hyperframes-player')?.ready, {timeout: 30000});
    const size = await page.evaluate(width => {
      const player = document.querySelector('hyperframes-player'), frame = player.iframeElement;
      const root = frame.contentDocument.querySelector('[data-width][data-height]');
      if (!root) throw new Error('Cannot confirm composition dimensions');
      const height = Math.round(width * Number(root.dataset.height) / Number(root.dataset.width));
      player.pause(); player.removeAttribute('controls');
      player.style.cssText += `;position:fixed;left:0;top:0;width:${width}px;height:${height}px;max-width:none;max-height:none;z-index:2147483647;`;
      // Studio panels can overlay an iframe screenshot through ancestor stacking contexts.
      for (let child = player, parent = player.parentElement; parent; child = parent, parent = parent.parentElement) {
        for (const sibling of parent.children) if (sibling !== child)
          sibling.style.setProperty('visibility', 'hidden', 'important');
        for (const [key, value] of Object.entries({transform: 'none', overflow: 'visible', contain: 'none', filter: 'none'}))
          parent.style.setProperty(key, value, 'important');
      }
      return {width, height};
    }, Math.round(parameters.width));
    await page.setViewport({width: Math.max(1280, size.width + 64), height: Math.max(1080, size.height + 64), deviceScaleFactor: 1});
    await page.mouse.move(size.width + 32, size.height + 32);
    const iframe = (await page.evaluateHandle(() => document.querySelector('hyperframes-player').iframeElement)).asElement();
    const frame = await iframe.contentFrame();
    result.viewport = {...size, comparison_width: Math.min(320, size.width),
      comparison_height: Math.round(size.height * Math.min(320, size.width) / size.width)};
    const duration = await page.evaluate(() => document.querySelector('hyperframes-player').duration);
    if (!Number.isFinite(duration) || duration <= 0) throw new Error('Invalid Studio duration');
    if (duration / parameters.step > 2000) throw new Error('Sampling budget exceeded; increase step (maximum 2000 baseline samples)');
    const samples = new Map();
    const sample = async requested => {
      if (Date.now() >= deadline) throw new Error('Diagnostic time budget exceeded; browser closed before outer command timeout');
      const time = Math.round(Math.min(duration - 0.001, Math.max(0, requested)) * 1e6) / 1e6;
      if (samples.has(time)) return samples.get(time);
      const value = {time, ready: false, texts: [], unverified: []};
      if (samples.size >= 10000) throw new Error('Sampling budget exceeded (maximum 10000 samples)');
      samples.set(time, value);
      const sampleDeadline = Date.now() + parameters.timeout_ms;
      const remaining = () => ({timeout: Math.max(1, sampleDeadline - Date.now())});
      for (;;) {
        const before = navigation;
        try {
          await page.waitForFunction(() => {
            const player = document.querySelector('hyperframes-player'), win = player?.iframeElement?.contentWindow;
            return player?.ready && win?.document.body && getComputedStyle(player.iframeElement).visibility === 'visible' &&
              (win.__player || Object.keys(win.__timelines || {}).length);
          }, remaining());
          await page.evaluate(time => document.querySelector('hyperframes-player').seek(time), time);
          await page.waitForFunction(time => {
            const player = document.querySelector('hyperframes-player');
            const win = player.iframeElement.contentWindow;
            const root = win.document.querySelector('[data-composition-id]');
            const timeline = win.__timelines?.[root?.dataset.compositionId];
            const actual = win.__player?.getTime?.() ?? timeline?.time?.();
            return player.ready && Math.abs(player.currentTime - time) < 0.04 &&
              typeof actual === 'number' && Math.abs(actual - time) < 0.04;
          }, remaining(), time);
          value.actual_time = await frame.evaluate(() => {
            const root = document.querySelector('[data-composition-id]');
            return window.__player?.getTime?.() ?? window.__timelines?.[root?.dataset.compositionId]?.time?.();
          });
          await frame.waitForFunction(frameResourcesReady, remaining(), time);
          await frame.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
          const box = await iframe.boundingBox();
          if (!box || Math.abs(box.width - size.width) > 1 || Math.abs(box.height - size.height) > 1)
            throw new Error('Composition viewport is clipped or changed');
          if (!await page.evaluate(box => {
            const player = document.querySelector('hyperframes-player');
            return [[.02, .02], [.98, .02], [.02, .98], [.98, .98], [.5, .5]].every(([x, y]) =>
              document.elementFromPoint(box.x + box.width * x, box.y + box.height * y) === player);
          }, box)) throw new Error('Studio controls obscure the composition viewport');
          const screenshot = await iframe.screenshot();
          value.pixels = await sharp(screenshot).removeAlpha().resize({width: Math.min(320, size.width)}).raw().toBuffer();
          const info = await frame.evaluate(inspectFrame, input.scenes || [], time);
          if (before !== navigation || !await iframe.evaluate(element => getComputedStyle(element).visibility === 'visible'))
            throw new Error('Studio frame reloaded during sampling');
          value.texts.push(...info.texts); value.unverified.push(...info.unverified);
          result.timeline.push(...info.timeline);
          if (frame.childFrames().length) value.unverified.push('Nested frame text/resources/time mapping is not verified; excluded from stillness verdicts');
          else value.ready = true;
        } catch (error) {
          if (before !== navigation && Date.now() < sampleDeadline) { value.retried_after_navigation = true; continue; }
          value.unverified.push('Sample not verified: ' + error.message);
        }
        break;
      }
      return value;
    };
    const times = new Set([0, Math.max(0, duration - 0.001)]);
    for (let time = parameters.step; time < duration; time += parameters.step) times.add(time);
    for (const scene of input.scenes || []) if (scene.start >= 0 && scene.start < duration) times.add(scene.start);
    for (const time of [...times].sort((a, b) => a - b)) await sample(time);
    for (let start = 0; start + parameters.window <= duration + 0.001; start += parameters.step) {
      for (const value of samples.values()) if (value.time < start) delete value.pixels;
      const end = Math.min(start + parameters.window, duration - 0.001);
      const window = [...samples.values()].filter(value => value.time >= start && value.time <= end);
      if (window.length > 128) {
        result.unverified.push(`Comparison budget exceeded at ${start}-${end}; increase step or reduce window`);
        continue;
      }
      if (!isStill(window, parameters)) continue;
      // Irrational phase offset breaks common loop/step aliases without a second clock.
      for (let time = start + parameters.step * 0.381966; time < end; time += parameters.step / 2)
        window.push(await sample(time));
      if (isStill(window, parameters)) {
        const previous = result.motion.at(-1);
        if (previous && previous.end >= start) previous.end = end;
        else result.motion.push({start, end, reason: 'suspected still: no perceptible sampled change; requires viewing'});
      }
    }
    result.samples = [...samples.values()].sort((a, b) => a.time - b.time).map(({pixels, ...value}) => value);
    result.timeline = [...new Map(result.timeline.map(value => [JSON.stringify(value), value])).values()];
    result.unverified = [...new Set(result.unverified)];
    return result;
  } finally {
    if (browser) await browser.close();
    await fs.rm(profile, {recursive: true, force: true});
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  try {
    let text = '';
    for await (const chunk of process.stdin) text += chunk;
    process.stdout.write(JSON.stringify(await probe(JSON.parse(text))) + '\n');
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}
