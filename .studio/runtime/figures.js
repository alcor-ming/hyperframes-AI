(function (global) {
  "use strict";
  async function load(lock, { projectURL = new URL(".", location.href), cues } = {}) {
    const assets = lock?.assets ?? lock?.components?.map(a => ({ ...a, kind: a.asset_kind, ref: a.component_ref }));
    if (!Array.isArray(assets)) throw new Error("invalid_figure_lock");
    const base = new URL(projectURL, location.href), characters = new Map(), bindings = new Set();
    if (base.origin !== location.origin) throw new Error("figures_require_local_url");
    cues ??= await global.HarnessCues.load(new URL("runtime/cues.json", base));
    function url(relative) {
      if (typeof relative !== "string" || /[\\:\u0000-\u001f]/.test(relative) || relative.split("/").some(p => !p || p === "." || p === "..")) throw new Error("invalid_figure_path");
      return new URL(relative.split("/").map(encodeURIComponent).join("/"), base).href;
    }
    async function read(relative) {
      const response = await fetch(url(relative), { redirect: "error" });
      if (!response.ok) throw new Error("figure_asset_missing");
      return response.json();
    }
    for (const asset of assets.filter(a => a.kind === "character")) {
      const metadata = await read(`${asset.vendor_path}/asset.json`);
      if (metadata.kind !== "character" || `${metadata.id}@v${metadata.version}` !== asset.ref) throw new Error("figure_identity_mismatch");
      const declaration = await read(`${asset.vendor_path}/${metadata.entry}`);
      if (!declaration.states?.[declaration.default_state]) throw new Error("figure_default_state_missing");
      const states = {};
      for (const [id, state] of Object.entries(declaration.states)) {
        if (!metadata.dependencies?.includes(state.file)) throw new Error("figure_state_outside_closure");
        const image = new Image(); image.src = url(`${asset.vendor_path}/${state.file}`); await image.decode();
        if (!Array.isArray(state.anchor) || state.anchor.length !== 2 || !state.anchor.every(Number.isFinite)
            || state.anchor[0] < 0 || state.anchor[0] >= image.naturalWidth || state.anchor[1] < 0 || state.anchor[1] >= image.naturalHeight
            || !["left", "right"].includes(state.facing)) throw new Error("invalid_figure_state");
        states[id] = { ...state, src: image.src, width: image.naturalWidth, height: image.naturalHeight };
      }
      characters.set(asset.ref, { ...declaration, states });
    }
    const time = cue => {
      const value = typeof cue === "number" ? cue : cues?.find(cue);
      if (!Number.isFinite(value) || value < 0) throw new Error("invalid_figure_cue");
      return value;
    };
    function create(el, character) {
      if (!el || el.nodeType !== 1 || !el.ownerDocument) throw new Error("invalid_figure_element");
      const image = el.tagName === "IMG" ? el : character ? el.appendChild(el.ownerDocument.createElement("img")) : null;
      const original = { transform: el.style.transform, opacity: el.style.opacity, transformOrigin: el.style.transformOrigin };
      const imageOriginal = image ? { src: image.getAttribute("src"), style: image.getAttribute("style") } : null;
      const baseTransform = getComputedStyle(el).transform, baseOpacity = Number(getComputedStyle(el).opacity);
      const fragments = []; let disposed = false;
      function add(cue, duration, fn, kind, sampleFraction = .5) {
        if (!Number.isFinite(duration) || duration < 0) throw new Error("invalid_figure_duration");
        fragments.push({ start: time(cue), duration, fn, kind, sampleFraction });
        fragments.sort((a, b) => a.start - b.start);
        return api;
      }
      function motion(kind, cue, options = {}) {
        const { duration = 0.5, x = 0, y = 0, scale = 1.15, amplitude = 12, cycles = 1, angle = 12 } = options;
        if (![x, y, scale, amplitude, cycles, angle].every(Number.isFinite) || scale <= 0 || cycles < 0) throw new Error("invalid_figure_motion");
        return add(cue, duration, (local, state) => {
          const p = duration ? Math.max(0, Math.min(1, local / duration)) : Number(local >= 0);
          const active = local >= 0 && local < duration;
          if (kind === "enter") { state.opacity *= p; state.x += x * (1 - p); state.y += (y || 30) * (1 - p); }
          if (kind === "exit") { state.opacity *= 1 - p; state.x += x * p; state.y += y * p; }
          if (kind === "pan") { state.x += x * p; state.y += y * p; }
          if (kind === "zoom") { const s = 1 + (scale - 1) * p; state.sx *= s; state.sy *= s; }
          if (kind === "point") state.angle += angle * Math.sin(Math.PI * p);
          if (!active) return;
          if (kind === "idle") state.y += amplitude * Math.sin(p * Math.PI * 2 * cycles);
          if (kind === "bounce") state.y -= amplitude * Math.abs(Math.sin(p * Math.PI * cycles));
          if (kind === "squash") { const s = 1 + (scale - 1) * Math.sin(p * Math.PI); state.sx *= s; state.sy /= s; }
        }, kind, kind === "bounce" && cycles > 0 ? Math.min(.5, .5 / cycles) : .5);
      }
      const api = {
        state(cue, id) {
          if (!character?.states[id]) throw new Error("figure_state_missing");
          return add(cue, 0, (local, value) => { if (local >= 0) value.state = id; }, "state");
        },
        talk(intervals = cues?.data.speech_intervals) {
          if (!Array.isArray(intervals) || intervals.some(i => !Array.isArray(i) || i.length !== 2 || !i.every(Number.isFinite) || i[0] < 0 || i[1] <= i[0])) throw new Error("invalid_talk_intervals");
          for (const [start, end] of intervals) add(start, end - start, (local, value) => {
            if (local >= 0 && local < end - start) value.sy *= 1 + 0.025 * Math.sin(local * Math.PI * 10);
          });
          return api;
        },
        renderAt(t) {
          if (!Number.isFinite(t)) throw new Error("invalid_figure_time");
          if (disposed) return;
          const value = { x: 0, y: 0, sx: 1, sy: 1, angle: 0, opacity: baseOpacity, state: character?.default_state };
          for (const fragment of fragments) fragment.fn(t - fragment.start, value);
          el.style.transform = `${baseTransform === "none" ? "" : baseTransform} translate(${value.x}px, ${value.y}px) rotate(${value.angle}deg) scale(${value.sx}, ${value.sy})`;
          el.style.opacity = String(value.opacity);
          if (character) {
            const state = character.states[value.state];
            if (image.src !== state.src) image.src = state.src;
            image.style.width = "100%"; image.style.height = "100%"; image.style.objectFit = "contain";
            el.style.transformOrigin = `${state.anchor[0] / state.width * 100}% ${state.anchor[1] / state.height * 100}%`;
            image.dataset.facing = state.facing;
            return image.decode();
          }
        },
        dispose() {
          if (disposed) return; disposed = true; bindings.delete(api);
          global.__hfRhythmSources.delete(rhythm);
          Object.assign(el.style, original);
          if (image && image !== el) image.remove();
          else if (image) for (const [key, value] of Object.entries(imageOriginal)) value === null ? image.removeAttribute(key) : image.setAttribute(key, value);
        },
      };
      const rhythm = () => fragments.filter(fragment => fragment.kind && fragment.kind !== "idle")
        .flatMap(fragment => {
          const value = { x: 0, y: 0, sx: 1, sy: 1, angle: 0, opacity: 1, state: character?.default_state };
          fragment.fn(fragment.duration * fragment.sampleFraction, value);
          // ponytail: local perceptibility hints; rendered visibility still needs browser evidence.
          const meaningful = fragment.kind === "state" || Math.abs(value.x) >= .5 || Math.abs(value.y) >= .5 ||
            Math.abs(value.sx - 1) >= .005 || Math.abs(value.sy - 1) >= .005 || Math.abs(value.angle) >= .5 || Math.abs(value.opacity - 1) >= .02;
          if (!meaningful) return [];
          return ["pan", "zoom"].includes(fragment.kind) ? [
            { time: fragment.start, duration: fragment.duration, kind: fragment.kind + "_start", target: el },
            { time: fragment.start + fragment.duration, before: fragment.start + fragment.duration / 2,
              duration: 0, kind: fragment.kind + "_end", target: el },
          ] : [{ time: fragment.start, duration: fragment.duration,
            after: fragment.start + (fragment.duration ? fragment.duration * fragment.sampleFraction : .001), kind: fragment.kind, target: el }];
        });
      (global.__hfRhythmSources ??= new Set()).add(rhythm);
      for (const kind of ["enter", "exit", "idle", "bounce", "squash", "pan", "zoom", "point"]) api[kind] = (cue, options) => motion(kind, cue, options);
      bindings.add(api); return api;
    }
    return {
      figure(el, ref) { const character = characters.get(ref); if (!character) throw new Error("figure_asset_outside_closure"); return create(el, character); },
      image(el) { return create(el); },
      async renderAt(t) { await Promise.all([...bindings].map(binding => binding.renderAt(t))); },
      dispose() { for (const binding of [...bindings]) binding.dispose(); },
    };
  }
  global.HarnessFigures = { load };
})(window);
