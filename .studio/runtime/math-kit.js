/* Every frame is reconstructed from cue time; geometry and glyphs never share a layer. */
(function (global) {
  'use strict';
  let serial = 0;
  async function mount({stage, text, math, intent, cues, ratio = '16:9', start = 0, end, appearance, fontURL}) {
    const doc = stage?.ownerDocument;
    if (!doc || text?.ownerDocument !== doc || !stage.isConnected || !text.isConnected || stage === text || stage.contains(text) || text.contains(stage)) throw new Error('math_hosts_require_independent_layers');
    if (!['16:9', '9:16'].includes(ratio) || !Number.isFinite(start) || !Number.isFinite(end) || end <= start) throw new Error('invalid_math_interval_or_ratio');
    if (!math?.font?.characters || !Array.isArray(math.items) || !Array.isArray(intent?.cues)) throw new Error('invalid_math_content');
    const fontSource = new URL(fontURL, doc.baseURI), base = new URL(doc.baseURI);
    if (!['data:', 'blob:'].includes(fontSource.protocol) &&
        (!['file:', 'http:', 'https:'].includes(fontSource.protocol) || fontSource.origin !== base.origin || fontSource.protocol !== base.protocol)) throw new Error('math_font_requires_local_source');
    const family = 'HFMath' + ++serial;
    const face = new FontFace(family, `url(${JSON.stringify(fontSource.href)})`);
    const node = (parent, cls, x, y, w, h) => {
      const el = doc.createElement('div'); el.className = cls;
      if (x !== undefined) Object.assign(el.style, {left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px'});
      parent.append(el); return el;
    };
    const graphics = node(stage, 'hf-math-kit'), labels = node(text, 'hf-math-kit');
    graphics.dataset.hfLayer = 'stage'; labels.dataset.hfLayer = 'text';
    const records = [], items = [], events = [];
    let disposed = false, activeEnd = end, resolveTime = cue => typeof cue === 'number' ? cue : cues.find(cue);
    const rawTime = resolveTime;
    const rhythm = () => events;
    const dispose = () => {
      if (disposed) return;
      disposed = true; graphics.remove(); labels.remove(); doc.fonts.delete(face);
      global.__hfRhythmSources?.delete(rhythm);
    };
    try {
      if (appearance) for (const root of [graphics, labels]) {
        global.HarnessAppearance.apply(root, appearance); root.style.backgroundColor = 'transparent';
      }
      labels.style.fontFamily = family;
      await face.load(); doc.fonts.add(face);
      const probe = node(labels, 'hf-math-glyphs'); probe.dataset.hfMathGlyphs = '';
      probe.textContent = math.font.characters;
      const [width, height] = ratio === '16:9' ? [1920, 1080] : [1080, 1920];
      for (const item of math.items) {
        const [x, y, w, h] = item.box || [];
        if (![x, y, w, h].every(Number.isFinite) || x < 0 || y < 0 || w <= 0 || h <= 0 || x + w > width || y + h > height) throw new Error('invalid_math_box:' + item.id);
        const g = node(graphics, 'hf-math-item', x, y, w, h), t = node(labels, 'hf-math-item', x, y, w, h);
        g.dataset.hfMathId = t.dataset.hfMathId = item.id;
        const label = (value, lx = 0, ly = 0, lw = w, lh = h) => {
          const el = node(t, 'hf-math-label', lx, ly, lw, lh);
          el.dataset.hfMathLabel = ''; el.textContent = value; return el;
        };
        const shape = (sx, sy, sw, sh) => {
          if (![sx, sy, sw, sh].every(Number.isFinite) || sw <= 0 || sh <= 0) throw new Error('invalid_math_geometry:' + item.id);
          return node(g, 'hf-math-shape', sx, sy, sw, sh);
        };
        const line = (sx, sy, sw) => node(g, 'hf-math-line', sx, sy, sw, 3);
        let moving = [], origin;
        if (item.kind === 'formula') {
          item.slots.forEach((value, i) => { if (value) label(value, i * w / item.slots.length, 0, w / item.slots.length, h); });
        } else if (item.kind === 'unknown') {
          const size = Math.min(w, h); shape((w - size) / 2, (h - size) / 2, size, size); label(item.label);
        } else if (item.kind === 'units' || item.kind === 'segment') {
          if (!Number.isInteger(item.count) || item.count < 1 || item.count > 32) throw new Error('invalid_math_geometry:' + item.id);
          const gap = item.kind === 'units' ? 8 : 0;
          const cell = (w - gap * (item.count - 1)) / item.count;
          for (let i = 0; i < item.count; i++) {
            shape(i * (cell + gap), 0, cell, h - 44);
            label(item.value, i * (cell + gap), 0, cell, h - 44);
          }
          label(item.label, 0, h - 42, w, 42);
        } else if (item.kind === 'area') {
          const size = Math.min(w, h - 44); shape((w - size) / 2, 0, size, size);
          label(item.value, 0, 0, w, size); label(item.label, 0, h - 42, w, 42);
        } else if (item.kind === 'number-line') {
          const count = item.labels.length, spacing = w / count, left = spacing / 2;
          line(left, h / 2 - 8, w - spacing);
          item.labels.forEach((value, i) => {
            node(g, 'hf-math-tick', left + i * spacing - 1, h / 2 - 18, 3, 22);
            label(value, i * spacing, h / 2 + 8, spacing, h / 2 - 8);
          });
        } else if (item.kind === 'strike') {
          label(item.label); const strike = line(0, h / 2, w);
          if (item.negate) {
            strike.style.transform = 'rotate(-12deg)';
            line(0, h / 2, w).style.transform = 'rotate(12deg)';
          }
        } else if (item.kind === 'edge') {
          const [fx, fy] = item.from; origin = item.from;
          line(fx - x, fy - y, item.length);
          moving = [line(fx - x, fy - y, item.length), label(item.label, fx - x, fy - y - 42, item.length, 40)];
          moving[0].style.background = 'var(--appearance-colors-accent,#19776b)';
        } else if (item.kind === 'equals') {
          origin = [x, y]; moving = [label('=')];
        } else throw new Error('invalid_math_kind:' + item.kind);
        const changes = intent.cues.filter(event => [...event.reveal, ...event.remove].includes(item.id));
        if (!changes.some(event => event.reveal.includes(item.id))) throw new Error('math_item_never_revealed:' + item.id);
        const entry = {item, g, t, moving, origin, changes, times: []}; records.push(entry);
        const first = changes.find(event => event.reveal.includes(item.id));
        items.push({id: item.id, cue: first.cue, element: t});
        for (const event of changes) for (const target of [g, t].filter(root => root.children.length)) {
          events.push({time: rawTime(event.cue), duration: event.remove.includes(item.id) ? 0 : item.duration ?? .25,
            kind: event.remove.includes(item.id) ? 'math_remove' : 'math_reveal', target});
        }
      }
      const retime = (map, until = end) => {
        if (typeof map !== 'function' || !Number.isFinite(until) || until <= start) throw new Error('invalid_math_cue_mapper');
        const times = records.map(record => record.changes.map(event => {
          const at = map(event.cue);
          if (!Number.isFinite(at) || at < start || at >= until) throw new Error('invalid_math_cue');
          return at;
        }));
        if (times.some(list => list.some((time, i) => i > 0 && time < list[i - 1]))) throw new Error('math_cues_require_order');
        resolveTime = map; activeEnd = until; records.forEach((record, i) => { record.times = times[i]; });
      };
      const renderAt = time => {
        if (!Number.isFinite(time)) throw new Error('invalid_math_time');
        if (disposed) return;
        for (const record of records) {
          const {item, g, t, changes, times, moving, origin} = record;
          let visible = false, reveal = start;
          changes.forEach((event, i) => { if (time >= times[i]) {
            visible = event.reveal.includes(item.id); if (visible) reveal = times[i];
          } });
          const opacity = visible && time >= start && time < activeEnd ? Math.max(0, Math.min(1, (time - reveal) / .25)) : 0;
          g.style.opacity = t.style.opacity = String(opacity);
          if (moving.length) {
            const p = Math.max(0, Math.min(1, (time - reveal) / item.duration));
            const transform = `translate(${(item.to[0] - origin[0]) * p}px, ${(item.to[1] - origin[1]) * p}px)`;
            moving.forEach(el => { el.style.transform = transform; });
          }
        }
      };
      retime(resolveTime); renderAt(start);
      await doc.fonts.ready;
      for (const label of labels.querySelectorAll('[data-hf-math-label]')) {
        if (label.scrollWidth > label.clientWidth + 1 || label.scrollHeight > label.clientHeight + 1) throw new Error('math_label_overflow:' + label.parentElement.dataset.hfMathId);
      }
      (global.__hfRhythmSources ??= new Set()).add(rhythm);
      return {text: labels, decorations: graphics, items, rhythm, retime, renderAt, dispose,
        getState: () => ({ratio, family, items: records.map(({item, t}) => ({id: item.id, kind: item.kind, box: [...item.box], opacity: Number(t.style.opacity)}))})};
    } catch (error) { dispose(); throw error; }
  }
  global.HarnessMathKit = {mount};
})(window);
