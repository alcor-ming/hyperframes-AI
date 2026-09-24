/* Static appearance adapter. Host must verify the frozen package closure before serving it.
 * Scene layout, text and cue timing remain the host's responsibility.
 */
(function (global) {
  "use strict";
  const preparedFonts = new WeakMap();
  const motionOwners = new WeakMap();
  let fontInstance = 0;
  function resolved(payload, parameters) {
    const result = structuredClone(payload);
    for (const [path, value] of Object.entries(parameters)) {
      const keys = path.split(".");
      if (keys.some(key => !key || ["__proto__", "constructor", "prototype"].includes(key))) throw new Error("Invalid appearance parameter path");
      let target = result;
      for (const key of keys.slice(0, -1)) {
        if (!Object.hasOwn(target, key) || !target[key] || typeof target[key] !== "object") throw new Error("Unknown appearance parameter path");
        target = target[key];
      }
      if (!Object.hasOwn(target, keys.at(-1))) throw new Error("Unknown appearance parameter path");
      target[keys.at(-1)] = value;
    }
    return result;
  }
  async function load(projectURL = new URL(".", location.href)) {
    const base = new URL(projectURL, location.href);
    if (base.origin !== location.origin) throw new Error("Appearance requires a project-local URL");
    function localURL(relative) {
      if (typeof relative !== "string" || /[\\:\u0000-\u001f]/.test(relative) || relative.split("/").some(p => !p || p === ".." || p === ".")) {
        throw new Error("Appearance requires a project-local file");
      }
      return new URL(relative.split("/").map(encodeURIComponent).join("/"), base);
    }
    async function read(relative) {
      const response = await fetch(localURL(relative), { redirect: "error" });
      if (!response.ok) throw new Error(`Missing frozen appearance file: ${relative}`);
      return response.json();
    }
    const lock = await read("appearance-lock.json");
    if (![1, 2].includes(lock.schema_version) || lock.contract_version !== lock.schema_version || lock.resolver_version !== 1 || !Array.isArray(lock.assets)) throw new Error("Unsupported appearance lock");
    const result = { lock, motion: {} };
    let themePackage;
    async function payload(kind, selected) {
      const asset = lock.assets.find(item => item.ref === selected.ref);
      if (!asset || asset.kind !== kind || asset.package_sha256 !== selected.package_sha256) throw new Error("Appearance selection differs from frozen closure");
      const metadata = await read(`${asset.vendor_path}/asset.json`);
      if (metadata.kind !== kind || `${metadata.id}@v${metadata.version}` !== selected.ref) throw new Error("Appearance package identity mismatch");
      if (kind === "theme") themePackage = { asset, metadata };
      const value = await read(`${asset.vendor_path}/${metadata.entry}`);
      if (kind === "motion") {
        if (![1, 2].includes(metadata.contract_version) || (metadata.contract_version === 2) !== (value.capability_version === 2)
            || metadata.contract_version === 2 && lock.schema_version !== 2) throw new Error("Unsupported Motion capability");
      } else if (metadata.contract_version !== 1) throw new Error("Unsupported appearance capability");
      return value;
    }
    for (const kind of ["theme", "background"]) result[kind] = await payload(kind, lock.selection[kind]);
    for (const [slot, selection] of Object.entries(lock.selection.motion)) {
      if (selection !== null) {
        result.motion[slot] = await payload("motion", selection.asset);
        const motion = resolved(result.motion[slot], lock.parameters.motion[slot]);
        validateMotion(motion);
        if (!Object.hasOwn(motion.slots, selection.entry) || motion.capability_version === 2 && selection.entry !== slot) throw new Error("Unknown Motion entry");
        if (motion.capability_version === 2) for (const group of [motion.slots, motion.reduced_motion]) emphasisColor(group.emphasis, result);
      }
    }
    const fonts = resolved(result.theme, lock.parameters.theme).fonts || [];
    if (!Array.isArray(fonts)) throw new Error("Theme fonts must be an array");
    const state = { faces: [], families: new Map(), declaration: JSON.stringify(fonts), disposed: false, reducedMotion: matchMedia("(prefers-reduced-motion: reduce)").matches };
    const instance = ++fontInstance;
    result.dispose = () => {
      for (const face of state.faces) document.fonts.delete(face);
      state.disposed = true;
    };
    try {
      for (const font of fonts) {
        const style = font.style ?? "normal", weight = String(font.weight ?? "normal");
        const weights = weight.split(" ").map(Number);
        if (typeof font.family !== "string" || !font.family.trim() || !["normal", "italic", "oblique"].includes(style)
            || (!["normal", "bold"].includes(weight) && (!/^\d{1,4}(?: \d{1,4})?$/.test(weight)
              || weights.some(value => value < 1 || value > 1000) || weights.length === 2 && weights[0] > weights[1]))) {
          throw new Error("Invalid Theme font family/style/weight");
        }
        if (![font.path, font.license].every(value => themePackage.metadata.dependencies?.includes(value))) {
          throw new Error("Theme font and license must belong to the frozen dependency closure");
        }
        const url = localURL(`${themePackage.asset.vendor_path}/${font.path}`);
        let family = state.families.get(font.family);
        if (!family) {
          family = `HarnessFont_${instance}_${state.families.size}`;
          state.families.set(font.family, family);
        }
        try {
          const response = await fetch(url, { redirect: "error" });
          if (!response.ok) throw new Error(`HTTP ${response.status}`);
          const face = new FontFace(family, await response.arrayBuffer(), { style, weight });
          await face.load();
          document.fonts.add(face);
          state.faces.push(face);
        } catch (error) {
          throw new Error(`Cannot load frozen Theme font ${font.family} (${font.path}): ${error.message}`);
        }
      }
      preparedFonts.set(result, state);
    } catch (error) {
      result.dispose();
      throw error;
    }
    return result;
  }

  function fontStack(value, families) {
    // Split CSS family lists without splitting commas inside quoted names.
    return value.replace(/\s*(?:"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|[^,]+)\s*/g, part => {
      let name = part.trim();
      if (/^["']/.test(name)) name = name.slice(1, -1);
      else name = name.replace(/\s+/g, " ");
      name = name.replace(/\\([0-9a-f]{1,6}\s?|.)/gi, (_, escaped) => /^[0-9a-f]/i.test(escaped)
        ? String.fromCodePoint(parseInt(escaped.trim(), 16) || 0xfffd) : escaped);
      const family = families.get(name);
      return family ? `"${family}"` : part;
    });
  }

  function apply(stage, appearance) {
    if (!isElement(stage)) throw new TypeError("Appearance requires a stage element");
    const { lock } = appearance;
    const theme = resolved(appearance.theme, lock.parameters.theme);
    const background = resolved(appearance.background, lock.parameters.background);
    const color = background.renderer === "transparent" ? "transparent" : background.parameters.color;
    if (!["solid", "transparent"].includes(background.renderer) || !CSS.supports("color", color)) throw new Error("Unsupported static Background");
    const fonts = preparedFonts.get(appearance);
    if (fonts ? fonts.disposed || fonts.declaration !== JSON.stringify(theme.fonts || []) : (theme.fonts || []).length) {
      throw new Error("Theme fonts must be prepared by load() and not disposed or changed");
    }
    const variables = [];
    function tokens(value, parts = []) {
      if (value && typeof value === "object" && !Array.isArray(value)) {
        for (const [key, child] of Object.entries(value)) {
          if (!/^[A-Za-z0-9_-]+$/.test(key)) throw new Error("Invalid Theme token name");
          tokens(child, [...parts, key]);
        }
      } else if (typeof value === "string" || typeof value === "number") {
        const text = typeof value === "string" && parts[0] === "typography" && fonts
          ? fontStack(value, fonts.families) : String(value);
        variables.push([`--appearance-${parts.join("-")}`, text]);
      } else throw new Error("Unsupported Theme token value");
    }
    tokens(theme.tokens);
    for (const name of [...stage.style]) if (name.startsWith("--appearance-")) stage.style.removeProperty(name);
    for (const [name, value] of variables) stage.style.setProperty(name, value);
    stage.style.backgroundColor = color;
    // Explicit opt-in selectors prevent the adapter from redesigning a Scene.
    for (const element of stage.querySelectorAll("[data-appearance-text]")) element.style.color = "var(--appearance-colors-text)";
    for (const element of stage.querySelectorAll("[data-appearance-card]")) element.style.backgroundColor = "var(--appearance-surface-color)";
    return appearance;
  }
  function isElement(value) {
    try { return value.nodeType === 1 && Node.prototype.contains.call(value, value); } catch { return false; }
  }
  function validateMotion(payload) {
    if (!payload || typeof payload !== "object") throw new Error("Invalid Motion declaration");
    const fields = (value, allowed, required = allowed) => {
      if (!value || typeof value !== "object" || Array.isArray(value) || Object.keys(value).some(key => !allowed.includes(key))
          || required.some(key => !Object.hasOwn(value, key))) throw new Error("Unsupported Motion fields");
    };
    const slots = ["reveal", "emphasis", "exit", "transition"];
    const v2 = payload.capability_version === 2;
    fields(payload, v2 ? ["capability_version", "slots", "reduced_motion"] : ["slots", "reduced_motion"]);
    for (const name of ["slots", "reduced_motion"]) {
      fields(payload[name], slots, v2 ? slots : []);
      for (const [slot, settings] of Object.entries(payload[name])) {
        let required = ["duration", "easing"], optional = ["x", "y", "scale", "stagger"];
        if (v2) {
          required.push("effect"); optional = [];
          if (["reveal", "exit"].includes(slot)) {
            required.push("opacity_from", "opacity_to");
            if (slot === "exit" || settings?.effect === "short-rise") optional.push("x", "y", "scale");
            if (slot === "reveal") optional.push("hide_before");
          } else if (slot === "emphasis") required.push("restore_duration", "color_token", "outline_width");
        }
        fields(settings, [...required, ...optional], required);
        if (v2 ? !["none", "linear", "ease-in", "ease-out", "ease-in-out"].includes(settings.easing)
            : typeof settings.easing !== "string" || !/^(none|linear|power[1-4]\.(in|out|inOut)|(sine|expo|circ|back|bounce)\.(in|out|inOut))$/.test(settings.easing)) throw new Error("Unsupported Motion easing");
        if (v2 && !({ reveal: ["fade", "short-rise"], exit: ["fade-out"], emphasis: ["focus-restore"], transition: ["crossfade", "cut"] })[slot].includes(settings.effect)) throw new Error("Unsupported Motion effect");
        for (const [key, value] of Object.entries(settings)) {
          if (["effect", "easing"].includes(key)) continue;
          if (key === "hide_before") {
            if (typeof value !== "boolean") throw new Error("Invalid Motion hide_before");
          } else if (key === "color_token") {
            if (typeof value !== "string" || !/^(typography|colors|surface|border|radius|shadow|lines)(\.[a-zA-Z][a-zA-Z0-9_-]*)+$/.test(value)) throw new Error("Invalid Motion color token");
          } else if (!Number.isFinite(value) || !["x", "y"].includes(key) && value < 0 || key.startsWith("opacity_") && value > 1) throw new Error("Invalid Motion numeric value");
        }
        if (!v2) continue;
        if (["reveal", "exit"].includes(slot) && settings.opacity_to !== (slot === "reveal" ? 1 : 0)) throw new Error("Invalid Motion terminal opacity");
        if (settings.effect === "cut" && settings.duration !== 0) throw new Error("Motion cut requires zero duration");
        if (name === "reduced_motion" && ((["reveal", "exit"].includes(slot) && ((settings.x ?? 0) !== 0 || (settings.y ?? 0) !== 0 || (settings.scale ?? 1) !== 1))
            || ["reveal", "exit"].includes(slot) && settings.duration > payload.slots[slot].duration
            || slot === "emphasis" && (settings.duration !== 0 || settings.restore_duration !== 0)
            || slot === "transition" && settings.effect !== "cut")) throw new Error("Unsupported reduced Motion");
      }
    }
  }
  function emphasisColor(preset, appearance) {
    let color = resolved(appearance.theme, appearance.lock.parameters.theme).tokens;
    for (const part of preset.color_token.split(".")) color = color && Object.hasOwn(color, part) ? color[part] : undefined;
    if (typeof color !== "string" || !CSS.supports("color", color) || /\b(var|env|currentcolor|inherit|initial|unset|revert|light-dark)\b/i.test(color)) throw new Error("Motion requires a frozen Theme color");
    return color;
  }
  function bindMotion(element, appearance, slot, { cue = 0, restoreCue, endCue, overlap, reducedMotion } = {}) {
    if (!Number.isFinite(cue) || reducedMotion !== undefined && typeof reducedMotion !== "boolean") throw new TypeError("Motion requires a finite cue and boolean mode");
    const selection = appearance.lock.selection.motion[slot];
    if (selection === undefined) throw new Error("Unknown Motion slot");
    if (selection === null) return { seek() {}, dispose() {} };
    const payload = resolved(appearance.motion[slot], appearance.lock.parameters.motion[slot]);
    validateMotion(payload);
    const v2 = payload.capability_version === 2;
    if (v2 && (appearance.lock.schema_version !== 2 || appearance.lock.contract_version !== 2)) throw new Error("Unsupported Motion lock capability");
    if (!v2 && !["reveal", "exit"].includes(slot)) throw new Error("Motion v1 supports reveal and exit only");
    const normal = payload.slots[selection.entry];
    if (!normal || v2 && selection.entry !== slot) throw new Error("Unknown Motion entry");
    const prepared = preparedFonts.get(appearance);
    if (prepared?.disposed) throw new Error("Appearance is disposed");
    const reduced = reducedMotion ?? prepared?.reducedMotion ?? matchMedia("(prefers-reduced-motion: reduce)").matches;
    const preset = (reduced ? payload.reduced_motion : payload.slots)[selection.entry];
    if (!preset) return { seek() {}, dispose() {} }; // v1's explicit reduced-mode no-op.
    if (!v2 && (!["none", "linear"].includes(preset.easing) || preset.stagger)) throw new Error("Motion v1 requires linear easing without stagger");
    const targets = slot === "transition" ? [element?.outgoing, element?.incoming] : [element];
    if (targets.some(target => !isElement(target) || !target.isConnected) || targets.length === 2 && targets[0] === targets[1]) throw new TypeError("Motion requires distinct mounted elements");
    if (slot === "emphasis" && (!Number.isFinite(restoreCue) || restoreCue < cue + normal.duration)) throw new Error("Invalid Motion restore cue");
    if (slot === "transition") {
      if (targets[0].ownerDocument !== targets[1].ownerDocument || targets[0].contains(targets[1]) || targets[1].contains(targets[0])) throw new Error("Scene transition targets must be independent layers");
      if (!Number.isFinite(endCue) || endCue < cue || Math.abs(endCue - cue - normal.duration) > 1e-8) throw new Error("Transition interval must match preset duration");
      if (normal.effect === "crossfade" && (!Array.isArray(overlap) || overlap.length !== 2 || !overlap.every(Number.isFinite) || overlap[0] > cue || overlap[1] < endCue || overlap[1] <= overlap[0])) throw new Error("Crossfade requires a Scene overlap budget");
      for (const target of targets) {
        if (!target.getClientRects().length || getComputedStyle(target).visibility !== "visible") throw new Error("Scene transition targets must be drawable");
        for (let parent = target; parent; parent = parent.parentElement) {
          const style = getComputedStyle(parent);
          if (style.display === "none" || style.contentVisibility === "hidden" || Number(style.opacity) === 0) throw new Error("Scene transition targets must remain drawable");
        }
      }
    }
    const easing = preset.easing === "none" ? "linear" : preset.easing;
    const plans = [];
    const progress = (time, start, duration) => duration === 0 ? Number(time >= start) : Math.min(1, Math.max(0, (time - start) / duration));
    function plan(target, frames, at) { plans.push({ target, frames, at, properties: Object.keys(frames[0]).filter(key => key !== "easing") }); }
    function visibility(target, visible) { plan(target, [{ visibility: "hidden" }, { visibility: "visible" }], time => Number(visible(time))); }
    for (const [index, target] of targets.entries()) {
      const base = getComputedStyle(target);
      if (slot === "emphasis") {
        const original = { outlineColor: base.outlineColor, outlineWidth: base.outlineWidth, outlineStyle: base.outlineStyle, easing };
        const focus = { outlineColor: emphasisColor(preset, appearance), outlineWidth: `${preset.outline_width}px`, outlineStyle: "solid", easing };
        plan(target, [original, focus, original], time => time < restoreCue ? progress(time, cue, preset.duration) : 1 + progress(time, restoreCue, preset.restore_duration));
      } else if (slot === "transition") {
        const opacity = Number(base.opacity);
        plan(target, [{ opacity: index ? 0 : opacity, easing }, { opacity: index ? opacity : 0 }], time => progress(time, cue, preset.duration));
        visibility(target, time => index ? time >= cue : time < cue + preset.duration);
      } else {
        const original = {}, changed = {};
        if (!v2 || Object.hasOwn(preset, "x") || Object.hasOwn(preset, "y") || Object.hasOwn(preset, "scale")) {
          original.transform = base.transform;
          changed.transform = `${base.transform === "none" ? "" : base.transform} translate(${preset.x ?? 0}px, ${preset.y ?? 0}px) scale(${preset.scale ?? 1})`;
        }
        const frames = slot === "reveal" ? [changed, original] : [original, changed];
        if (v2) {
          frames[0].opacity = Number(base.opacity) * preset.opacity_from;
          frames[1].opacity = Number(base.opacity) * preset.opacity_to;
        }
        frames[0].easing = easing;
        plan(target, frames, time => progress(time, cue, preset.duration));
        if (v2) visibility(target, time => slot === "reveal" ? preset.hide_before === false || time >= cue : time < cue + preset.duration);
      }
    }
    // Ownership lasts through fill-before/fill-after. Use explicit layers for overlapping properties.
    for (const { target, properties } of plans) {
      const owned = motionOwners.get(target);
      if (properties.some(key => owned?.has(key)) || target.getAnimations().some(animation => animation.effect?.getKeyframes().some(frame => properties.some(key => key in frame)))) throw new Error("Motion property ownership conflict");
    }
    const animations = [];
    let disposed = false;
    const binding = {
      seek(time) {
        if (!Number.isFinite(time)) throw new TypeError("Motion time must be finite");
        if (!disposed) for (const { animation, at } of animations) animation.currentTime = at(time);
      },
      dispose() {
        if (disposed) return;
        disposed = true;
        for (const { animation } of animations) animation.cancel();
        for (const { target, properties } of plans) for (const key of properties) if (motionOwners.get(target)?.get(key) === binding) motionOwners.get(target).delete(key);
      },
    };
    try {
      for (const { target, frames, at } of plans) {
        const animation = new Animation(new KeyframeEffect(target, frames, { duration: frames.length - 1, fill: "both" }), target.ownerDocument.timeline);
        animations.push({ animation, at });
        animation.pause();
      }
      for (const { target, properties } of plans) {
        if (!motionOwners.has(target)) motionOwners.set(target, new Map());
        for (const key of properties) motionOwners.get(target).set(key, binding);
      }
      binding.seek(0);
      return binding;
    } catch (error) { binding.dispose(); throw error; }
  }
  global.HarnessAppearance = { load, apply, bindMotion };
})(window);
