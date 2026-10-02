/* Cue-driven A/B groups. The host owns layout and renders A at the supplied
 * active time, which pauses during B and never restarts on return. */
(function (global) {
  "use strict";
  function mount({ cues, scenes, reducedMotion = global.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false }) {
    if (typeof reducedMotion !== 'boolean') throw new TypeError('reducedMotion must be boolean');
    if (typeof cues?.find !== "function" || !Array.isArray(scenes) || !scenes.length) throw new TypeError("Rolls require cues and scenes");
    const time = cue => {
      const value = cues.find(cue);
      if (!Number.isFinite(value) || value < 0) throw new TypeError("Invalid roll cue");
      return value;
    };
    const saved = new Map(), ids = new Map();
    const frameOf = el => el?.ownerDocument?.defaultView?.frameElement;
    const element = (el, layer) => {
      const frame = frameOf(el);
      const host = el?.closest?.("[data-hf-layer]") ?? (frame?.dataset.cardLayer === layer ? frame.closest("[data-hf-layer]") : null);
      if (!el || el.nodeType !== 1 || !el.isConnected || host?.dataset.hfLayer !== layer || saved.has(el)) throw new TypeError("Roll requires a distinct mounted " + layer + " element");
      saved.set(el, { visibility: el.style.visibility, filter: el.style.filter, opacity: el.style.opacity });
      return el;
    };
    const plans = scenes.map(scene => {
      if (!scene || typeof scene.id !== "string" || !scene.id || ids.has(scene.id)) throw new TypeError("Roll scene IDs must be unique");
      const start = time(scene.startCue), end = time(scene.endCue);
      if (end <= start || !scene.a || scene.a.renderAt !== undefined && typeof scene.a.renderAt !== "function") throw new TypeError("Invalid roll scene");
      const groups = [element(scene.a.text, "text")];
      if (scene.a.decorations) groups.push(element(scene.a.decorations, "stage"));
      if (!Array.isArray(scene.a.items) || !Array.isArray(scene.b ?? [])) throw new TypeError("Roll items and B ranges must be arrays");
      const ranges = (scene.b ?? []).map(range => {
        const from = time(range.startCue), to = time(range.endCue);
        if (from < start || to > end || to <= from || !["hide", "blur"].includes(range.retreat)) throw new TypeError("Invalid B interval or retreat");
        const targets = [element(range.media, "stage")];
        if (range.text) targets.push(element(range.text, "text"));
        if (range.handoff !== undefined && range.handoff !== 'cut') throw new TypeError('Unknown B handoff');
        return { from, to, retreat: range.retreat, targets, cut: reducedMotion || range.handoff === 'cut' };
      }).sort((a, b) => a.from - b.from);
      if (ranges.some((range, i) => i && ranges[i - 1].to > range.from)) throw new TypeError("Overlapping B intervals");
      ranges.forEach((range, i) => {
        const scale = Math.min(1, (range.to - range.from) / .8);
        range.pre = range.cut ? 0 : Math.min(.2, (range.from - (ranges[i - 1]?.to ?? start)) / 2);
        range.post = range.cut ? 0 : Math.min(.2, ((ranges[i + 1]?.from ?? end) - range.to) / 2);
        range.retreatAt = range.from + .04 * scale;
        range.retreatEnd = range.from + .16 * scale;
        range.textAt = range.from + .2 * scale;
        range.textEnd = range.from + .32 * scale;
        range.textOut = range.to - .32 * scale;
        range.textGone = range.to - .2 * scale;
        range.returnAt = range.to - .16 * scale;
      });
      const continuation = scene.continuation;
      const source = continuation && ids.get(continuation.from);
      const read = continuation?.readItems ?? [];
      if (continuation && (!source || source.end > start || !Array.isArray(read) || new Set(read).size !== read.length
          || read.some(id => !source.items.some(item => item.id === id)))) throw new TypeError("Invalid A continuation");
      const itemIds = new Set();
      const items = scene.a.items.map(item => {
        if (!item || typeof item.id !== "string" || !item.id || itemIds.has(item.id)) throw new TypeError("Roll item IDs must be unique");
        itemIds.add(item.id);
        const at = read.includes(item.id) ? start : time(item.cue);
        if (at < start || at >= end || ranges.some(range => at >= range.from && at < range.to)) throw new TypeError("A reveals must occur outside B");
        const target = element(item.element, "text");
        if (!scene.a.text.contains(target) && frameOf(target) !== scene.a.text) throw new TypeError("A items must belong to their text group");
        return { id: item.id, at, target };
      });
      if (read.some(id => !itemIds.has(id))) throw new TypeError("Continuation items are missing");
      const offset = source ? source.offset + source.end - source.start - source.ranges.reduce((sum, range) => sum + range.to - range.from, 0) : 0;
      const plan = { id: scene.id, start, end, offset, groups, ranges, items, renderAt: scene.a.renderAt, continuation };
      ids.set(scene.id, plan);
      return plan;
    });
    if (plans.some((scene, i) => i && plans[i - 1].end > scene.start)) throw new TypeError("Roll scenes must be ordered without overlap");
    const owned = global.__hfRollOwners ??= new WeakMap();
    const targets = plans.flatMap(scene => [...scene.groups, ...scene.ranges.flatMap(range => range.targets)]);
    const properties = ['opacity', 'visibility', 'filter'];
    for (const target of targets) {
      if (owned.has(target) || target.getAnimations().some(animation => animation.effect?.getKeyframes().some(frame => properties.some(key => key in frame))))
        throw new Error('Roll property ownership conflict; use a separate wrapper');
    }
    const opacity = new Map(targets.map(target => [target, Number(target.ownerDocument.defaultView.getComputedStyle(target).opacity)]));
    for (const target of targets) owned.set(target, properties);
    let disposed = false;
    const rhythm = () => plans.flatMap(scene => [
      ...scene.items.map(item => ({ time: item.at, duration: 0, kind: "text_reveal", scene: scene.id, target: item.target })),
      ...scene.ranges.flatMap(range => [
        ...range.targets.map((target, i) => ({ time: range.cut ? range.from : i ? range.textAt : range.from - range.pre,
          duration: range.cut ? 0 : i ? range.textEnd - range.textAt : range.pre, kind: "b_enter", scene: scene.id, target })),
        ...scene.groups.flatMap(target => [
          { time: range.cut ? range.from : range.retreatAt, duration: range.cut ? 0 : range.retreatEnd - range.retreatAt, kind: 'exit', scene: scene.id, target },
          { time: range.cut ? range.to : range.returnAt, duration: range.cut ? 0 : range.to - range.returnAt, kind: 'a_return', scene: scene.id, target },
        ]),
        ...range.targets.map((target, i) => ({ time: range.cut ? range.to : i ? range.textOut : range.to,
          duration: range.cut ? 0 : i ? range.textGone - range.textOut : range.post, kind: 'exit', scene: scene.id, target })),
      ]),
    ]);
    (global.__hfRhythmSources ??= new Set()).add(rhythm);
    const boundaries = () => plans.flatMap(scene => scene.ranges.flatMap(range => [range.from, range.to]));
    (global.__hfRollBoundaries ??= new Set()).add(boundaries);
    const progress = (t, start, end) => end === start ? +(t >= end) : Math.max(0, Math.min(1, (t - start) / (end - start)));
    const show = (el, visible, blur = 0, alpha = 1) => {
      el.style.visibility = visible ? "visible" : "hidden";
      const base = saved.get(el).filter === 'none' ? '' : saved.get(el).filter;
      el.style.filter = blur ? `${base} blur(${8 * blur}px)`.trim() : saved.get(el).filter;
      if (opacity.has(el)) el.style.opacity = String(alpha * opacity.get(el));
    };
    return {
      async renderAt(t) {
        if (!Number.isFinite(t)) throw new TypeError("Roll time must be finite");
        if (disposed) return;
        for (const scene of plans) {
          const active = t >= scene.start && t < scene.end;
          const b = scene.ranges.find(range => t >= range.from && t < range.to);
          const local = Math.max(0, Math.min(t, scene.end) - scene.start);
          const paused = scene.ranges.reduce((total, range) => total + Math.max(0, Math.min(t, range.to) - range.from), 0);
          if (scene.renderAt) await scene.renderAt(scene.offset + Math.max(0, local - paused), { continuation: scene.continuation });
          const transition = scene.ranges.find(range => t >= range.from && t < range.to);
          const retreat = !transition ? 0 : transition.cut ? 1 : Math.min(
            progress(t, transition.retreatAt, transition.retreatEnd), 1 - progress(t, transition.returnAt, transition.to));
          const alpha = transition?.retreat === 'hide' ? 1 - retreat : 1;
          const blur = transition?.retreat === 'blur' ? retreat : 0;
          for (const target of scene.groups) show(target, active && alpha > 0, active ? blur : 0, alpha);
          // Set child visibility explicitly: CSS visibility can override a hidden parent.
          for (const item of scene.items) show(item.target, active && alpha > 0 && t >= item.at);
          for (const range of scene.ranges) for (const [i, target] of range.targets.entries()) {
            const amount = range.cut ? +(range === b) : i
              ? Math.min(progress(t, range.textAt, range.textEnd), 1 - progress(t, range.textOut, range.textGone))
              : Math.min(progress(t, range.from - range.pre, range.from), 1 - progress(t, range.to, range.to + range.post));
            show(target, active && amount > 0, 0, amount);
          }
        }
      },
      dispose() {
        if (disposed) return;
        disposed = true;
        global.__hfRhythmSources.delete(rhythm);
        global.__hfRollBoundaries.delete(boundaries);
        for (const target of targets) owned.delete(target);
        for (const [el, style] of saved) Object.assign(el.style, style);
      },
    };
  }
  global.HarnessRolls = { mount };
})(window);
