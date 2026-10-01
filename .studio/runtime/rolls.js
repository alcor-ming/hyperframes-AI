/* Cue-driven A/B groups. The host owns layout and renders A at the supplied
 * active time, which pauses during B and never restarts on return. */
(function (global) {
  "use strict";
  function mount({ cues, scenes }) {
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
      saved.set(el, { visibility: el.style.visibility, filter: el.style.filter });
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
        return { from, to, retreat: range.retreat, targets };
      }).sort((a, b) => a.from - b.from);
      if (ranges.some((range, i) => i && ranges[i - 1].to > range.from)) throw new TypeError("Overlapping B intervals");
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
    let disposed = false;
    const rhythm = () => plans.flatMap(scene => [
      ...scene.items.map(item => ({ time: item.at, duration: 0, kind: "text_reveal", scene: scene.id, target: item.target })),
      ...scene.ranges.flatMap(range => [
        ...range.targets.map(target => ({ time: range.from, duration: 0, kind: "b_enter", scene: scene.id, target })),
        ...scene.groups.map(target => ({ time: range.to, duration: 0, kind: "a_return", scene: scene.id, target })),
      ]),
    ]);
    (global.__hfRhythmSources ??= new Set()).add(rhythm);
    const show = (el, visible, blur = false) => {
      el.style.visibility = visible ? "visible" : "hidden";
      el.style.filter = blur ? "blur(8px)" : saved.get(el).filter;
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
          for (const target of scene.groups) show(target, active && b?.retreat !== "hide", active && b?.retreat === "blur");
          // Set child visibility explicitly: CSS visibility can override a hidden parent.
          for (const item of scene.items) show(item.target, active && b?.retreat !== "hide" && t >= item.at);
          for (const range of scene.ranges) for (const target of range.targets) show(target, active && range === b);
        }
      },
      dispose() {
        if (disposed) return;
        disposed = true;
        global.__hfRhythmSources.delete(rhythm);
        for (const [el, style] of saved) Object.assign(el.style, style);
      },
    };
  }
  global.HarnessRolls = { mount };
})(window);
