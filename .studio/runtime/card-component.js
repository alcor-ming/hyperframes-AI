/* Two paint projections preserve one component layout and its seekable timeline.
 * As with Appearance, the host verifies the frozen package closure before serving it. */
(function (global) {
  'use strict';
  async function mount({source, stage, text, componentId, items = []}) {
    if (!stage?.isConnected || !text?.isConnected || stage.closest('[data-hf-layer]')?.dataset.hfLayer !== 'stage'
        || text.closest('[data-hf-layer]')?.dataset.hfLayer !== 'text') throw new Error('Card requires separate stage and text layer mounts');
    for (const key of ['cardSource', 'cardId', 'componentRef', 'componentBinding', 'variableValues', 'width', 'height', 'start']) {
      if (stage.dataset[key] !== text.dataset[key]) throw new Error('Card projection mount declarations disagree: ' + key);
    }
    if (stage.dataset.cardLayer && stage.dataset.cardLayer !== 'stage' || text.dataset.cardLayer && text.dataset.cardLayer !== 'text') throw new Error('Card mount layer mismatch');
    source ??= text.dataset.cardSource;
    if (typeof source !== 'string' || !source || text.dataset.cardSource && source !== text.dataset.cardSource) throw new Error('Card source differs from its mount');
    const url = new URL(source, document.baseURI);
    if (url.origin !== location.origin || !['http:', 'https:'].includes(url.protocol)) throw new Error('Card source must be local to the host');
    const variables = JSON.parse(text.dataset.variableValues || '{}');
    if (!variables || typeof variables !== 'object' || Array.isArray(variables)) throw new Error('Card variables must be an object');
    const timeScale = variables.time_scale ?? 1;
    if (typeof timeScale !== 'number' || !Number.isFinite(timeScale) || timeScale <= 0) throw new Error('Card time_scale must be positive');
    if (!Array.isArray(items)) throw new Error('Card items must be an array');
    const response = await fetch(url, {redirect: 'error'});
    if (!response.ok) throw new Error('Cannot load Card Component: ' + response.status);
    const parsed = new DOMParser().parseFromString(await response.text(), 'text/html');
    const template = parsed.querySelector('template');
    const root = template?.content.querySelector('[data-composition-id]');
    if (!root || root.dataset.cardLayers !== 'stage text') throw new Error('Card Component must declare stage text projections');
    if (componentId && componentId !== root.dataset.compositionId) throw new Error('Card Component identity mismatch');
    componentId = root.dataset.compositionId;
    if (text.dataset.cardId && text.dataset.cardId !== componentId) throw new Error('Card mount identity mismatch');
    const width = Number(root.dataset.width), height = Number(root.dataset.height);
    if (!(Number.isFinite(width) && Number.isFinite(height) && width > 0 && height > 0)) throw new Error('Card dimensions must be positive');
    for (const element of template.content.querySelectorAll('[src],[href]')) {
      const dependency = new URL(element.getAttribute('src') ?? element.getAttribute('href'), url);
      if (dependency.origin !== url.origin || !dependency.pathname.startsWith(new URL('.', url).pathname)) throw new Error('Card dependency escapes its package');
    }
    const tokens = getComputedStyle(text);
    const tokenStyle = document.createElement('style');
    const declarations = [];
    for (const name of tokens) if (name.startsWith('--hf-')) declarations.push(name + ':' + tokens.getPropertyValue(name));
    tokenStyle.textContent = ':root{' + declarations.join(';') + '}';
    const frames = [];
    try {
      for (const [layer, target] of [['stage', stage], ['text', text]]) {
        const frame = document.createElement('iframe');
        frame.title = componentId + ' ' + layer;
        frame.dataset.cardLayer = layer;
        frame.style.cssText = `position:absolute;left:0;top:0;width:${width}px;height:${height}px;border:0;background:transparent;pointer-events:none;transform-origin:top left`;
        const doc = document.implementation.createHTMLDocument(componentId);
        doc.documentElement.dataset.cardLayer = layer;
        const base = doc.createElement('base');
        base.href = url.href;
        doc.head.append(base, tokenStyle.cloneNode(true));
        const values = doc.createElement('script');
        values.textContent = 'window.__hyperframes={getVariables:()=>(' + JSON.stringify(variables).replace(/</g, '\\u003c') + ')};';
        doc.head.append(values);
        doc.body.append(template.content.cloneNode(true));
        const loaded = new Promise((resolve, reject) => {
          frame.onload = resolve;
          frame.onerror = () => reject(new Error('Card projection failed to load'));
        });
        frame.srcdoc = '<!doctype html>' + doc.documentElement.outerHTML;
        frames.push(frame);
        target.append(frame);
        await loaded;
        for (const face of document.fonts) frame.contentDocument.fonts.add(face);
        await frame.contentDocument.fonts.ready;
        if (!frame.contentWindow.__timelines?.[componentId]) throw new Error('Card timeline did not initialize');
      }
    } catch (error) {
      frames.forEach(frame => frame.remove());
      throw error;
    }
    const resize = () => frames.forEach(frame => {
      const target = frame.parentElement;
      frame.style.transform = `scale(${Math.min(target.clientWidth / width, target.clientHeight / height)})`;
    });
    const observer = new ResizeObserver(resize);
    observer.observe(stage); observer.observe(text); resize();
    let resolvedItems;
    try {
      resolvedItems = items.map(item => {
        if (!item || typeof item.id !== 'string' || typeof item.selector !== 'string') throw new Error('Card item requires id and selector');
        const matches = frames[1].contentDocument.querySelectorAll(item.selector);
        if (matches.length !== 1) throw new Error('Card item selector must resolve exactly once');
        return {id: item.id, cue: item.cue, element: matches[0]};
      });
    } catch (error) {
      observer.disconnect(); frames.forEach(frame => frame.remove()); throw error;
    }
    return {
      decorations: frames[0], text: frames[1], items: resolvedItems,
      renderAt(seconds) {
        if (!Number.isFinite(seconds)) throw new Error('Card time must be finite');
        for (const frame of frames) {
          const time = Math.max(0, seconds) * timeScale;
          frame.dataset.cardTime = String(time);
          frame.contentWindow.__timelines[componentId].pause().seek(time, true);
        }
      },
      dispose() { observer.disconnect(); frames.forEach(frame => frame.remove()); }
    };
  }
  global.HarnessCardComponent = {mount};
})(window);
