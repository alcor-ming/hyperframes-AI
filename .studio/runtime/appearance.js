/* Static appearance adapter. Host must verify the frozen package closure before serving it.
 * Scene layout, text and cue timing remain the host's responsibility.
 */
(function (global) {
  "use strict";
  const preparedFonts = new WeakMap();
  const motionOwners = new WeakMap();
  const backgroundPackages = new WeakMap();
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
    if (![1, 2, 3].includes(lock.schema_version) || lock.contract_version !== lock.schema_version || lock.resolver_version !== 1 || !Array.isArray(lock.assets)) throw new Error("Unsupported appearance lock");
    const result = { lock, motion: {}, projectURL: base.href };
    let themePackage;
    async function payload(kind, selected) {
      const asset = lock.assets.find(item => item.ref === selected.ref);
      if (!asset || asset.kind !== kind || asset.package_sha256 !== selected.package_sha256) throw new Error("Appearance selection differs from frozen closure");
      const metadata = await read(`${asset.vendor_path}/asset.json`);
      if (metadata.kind !== kind || `${metadata.id}@v${metadata.version}` !== selected.ref) throw new Error("Appearance package identity mismatch");
      if (kind === "theme") themePackage = { asset, metadata };
      const value = await read(`${asset.vendor_path}/${metadata.entry}`);
      if (kind === "background" && value.renderer === "module") {
        if (!["card", "explainer", "showcase"].includes(lock.mode) || !metadata.dependencies?.includes(value.entry)) throw new Error("Invalid module Background closure");
        backgroundPackages.set(result, localURL(`${asset.vendor_path}/${value.entry}`).href);
      }
      if (kind === "motion") {
        const capability = value.capability_version === undefined ? 1 : value.capability_version;
        if (![1, 2, 3].includes(metadata.contract_version) || capability !== metadata.contract_version || capability > lock.contract_version) throw new Error("Unsupported Motion capability");
      } else if (metadata.contract_version !== 1) throw new Error("Unsupported appearance capability");
      return value;
    }
    for (const kind of ["theme", "background"]) result[kind] = await payload(kind, lock.selection[kind]);
    for (const [slot, selection] of Object.entries(lock.selection.motion)) {
      if (selection !== null) {
        result.motion[slot] = await payload("motion", selection.asset);
        const motion = resolved(result.motion[slot], lock.parameters.motion[slot]);
        validateMotion(motion);
        const capability = motion.capability_version === 3 ? 3 : motion.capability_version === 2 ? 2 : 1;
        if (!Object.hasOwn(motion.slots, selection.entry) || capability >= 2 && selection.entry !== slot) throw new Error("Unknown Motion entry");
        if (capability >= 2) for (const group of [motion.slots, motion.reduced_motion]) if (group?.emphasis && typeof group.emphasis.color_token === "string") emphasisColor(group.emphasis, result);
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
    const color = ["transparent", "module"].includes(background.renderer) ? "transparent" : background.parameters.color;
    if (!["solid", "transparent", "module"].includes(background.renderer) || background.renderer === "module" && !["card", "explainer", "showcase"].includes(lock.mode) || !CSS.supports("color", color)) throw new Error("Unsupported Background");
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
  const motionSlots = ["reveal", "emphasis", "exit", "transition"];
  const motionV2Effects = { reveal: ["fade", "short-rise"], exit: ["fade-out"], emphasis: ["focus-restore"], transition: ["crossfade", "cut"] };
  const motionV3Effects = {
    reveal: ["pop", "stamp", "wipe", "glitch-in"],
    emphasis: ["pulse", "shake", "wobble", "glow"],
    exit: ["pop-out", "wipe-out", "glitch-out"],
    transition: ["wipe", "push", "glitch-cut"],
  };
  const motionV3Fields = { pop: ["x", "y", "scale"], stamp: ["x", "y", "scale", "rotate"], wipe: ["direction"], "glitch-in": ["x", "y"], pulse: ["scale"], shake: ["x", "y"], wobble: ["rotate"], glow: ["blur"], "pop-out": ["x", "y", "scale"], "wipe-out": ["direction"], "glitch-out": ["x", "y"], push: ["direction"], "glitch-cut": [] };
  function validateMotion(payload) {
    if (!payload || typeof payload !== "object") throw new Error("Invalid Motion declaration");
    const fields = (value, allowed, required = allowed) => {
      if (!value || typeof value !== "object" || Array.isArray(value) || Object.keys(value).some(key => !allowed.includes(key))
          || required.some(key => !Object.hasOwn(value, key))) throw new Error("Unsupported Motion fields");
    };
    const version = payload.capability_version === 3 ? 3 : payload.capability_version === 2 ? 2 : 1;
    fields(payload, version >= 2 ? ["capability_version", "slots", "reduced_motion"] : ["slots", "reduced_motion"]);
    for (const name of ["slots", "reduced_motion"]) {
      fields(payload[name], motionSlots, version >= 2 ? motionSlots : []);
      for (const [slot, settings] of Object.entries(payload[name])) {
        if (version === 1) {
          const required = ["duration", "easing"], optional = ["x", "y", "scale", "stagger"];
          fields(settings, [...required, ...optional], required);
          if (typeof settings.easing !== "string" || !/^(none|linear|power[1-4]\.(in|out|inOut)|(sine|expo|circ|back|bounce)\.(in|out|inOut))$/.test(settings.easing)) throw new Error("Unsupported Motion easing");
          for (const [key, value] of Object.entries(settings)) {
            if (key === "easing") continue;
            if (!Number.isFinite(value) || !["x", "y"].includes(key) && value < 0 || key.startsWith("opacity_") && value > 1) throw new Error("Invalid Motion numeric value");
          }
          continue;
        }
        const effect = settings?.effect;
        const required = ["effect", "duration", "easing"], optional = [];
        if (["reveal", "exit"].includes(slot)) {
          required.push("opacity_from", "opacity_to");
          if (slot === "exit" && (version === 2 || effect === "fade-out") || effect === "short-rise") optional.push("x", "y", "scale");
          if (slot === "reveal") optional.push("hide_before");
        } else if (slot === "emphasis" && effect === "focus-restore") {
          required.push("restore_duration", "color_token", "outline_width");
        }
        if (version === 3) {
          if (typeof effect === "string") optional.push(...(motionV3Fields[effect] || []));
          if (effect === "glow") required.push("color_token");
          if (name === "slots") optional.push("hold_fps");
        }
        fields(settings, [...required, ...optional], required);
        const effects = motionV2Effects[slot].concat(version === 3 ? motionV3Effects[slot] : []);
        const easings = ["none", "linear", "ease-in", "ease-out", "ease-in-out"].concat(version === 3 && name === "slots" ? ["back-out", "spring"] : []);
        if (typeof effect !== "string" || !effects.includes(effect) || typeof settings.easing !== "string" || !easings.includes(settings.easing)) throw new Error("Unsupported Motion effect or easing");
        for (const [key, value] of Object.entries(settings)) {
          if (["effect", "easing"].includes(key)) continue;
          if (key === "hide_before") {
            if (typeof value !== "boolean") throw new Error("Invalid Motion hide_before");
          } else if (key === "color_token") {
            if (typeof value !== "string" || !/^(typography|colors|surface|border|radius|shadow|lines)(\.[a-zA-Z][a-zA-Z0-9_-]*)+$/.test(value)) throw new Error("Invalid Motion color token");
          } else if (key === "direction") {
            if (!["left", "right", "up", "down"].includes(value)) throw new Error("Invalid Motion direction");
          } else if (key === "hold_fps") {
            if (!Number.isInteger(value) || value < 1 || value > 240) throw new Error("Invalid Motion hold_fps");
          } else if (!Number.isFinite(value) || !["x", "y", "rotate"].includes(key) && value < 0 || key.startsWith("opacity_") && value > 1) throw new Error("Invalid Motion numeric value");
        }
        if (["reveal", "exit"].includes(slot) && settings.opacity_to !== (slot === "reveal" ? 1 : 0)) throw new Error("Invalid Motion terminal opacity");
        if (slot === "transition" && effect === "cut" && settings.duration !== 0) throw new Error("Motion cut requires zero duration");
        if (name === "reduced_motion") {
          if (version === 3 && (slot === "reveal" && !["fade", "short-rise"].includes(effect)
              || slot === "exit" && effect !== "fade-out")) throw new Error("Unsupported reduced Motion");
          if (["reveal", "exit"].includes(slot) && (((settings.x ?? 0) !== 0 || (settings.y ?? 0) !== 0 || (settings.scale ?? 1) !== 1)
              || settings.duration > payload.slots[slot].duration)) throw new Error("Unsupported reduced Motion");
          if (slot === "emphasis" && (settings.duration !== 0 || (settings.restore_duration ?? 0) !== 0)) throw new Error("Unsupported reduced Motion");
          if (slot === "transition" && effect !== "cut") throw new Error("Unsupported reduced Motion");
          if (version === 3 && ["reveal", "exit"].includes(slot) && motionV3Effects[slot].includes(payload.slots[slot].effect)
              && effect !== (slot === "reveal" ? "fade" : "fade-out")) throw new Error("Unsupported reduced Motion");
        }
      }
    }
  }
  function emphasisColor(preset, appearance) {
    let color = resolved(appearance.theme, appearance.lock.parameters.theme).tokens;
    for (const part of preset.color_token.split(".")) color = color && Object.hasOwn(color, part) ? color[part] : undefined;
    if (typeof color !== "string" || !CSS.supports("color", color) || /\b(var|env|currentcolor|inherit|initial|unset|revert|light-dark)\b/i.test(color)) throw new Error("Motion requires a frozen Theme color");
    return color;
  }
  const springEasing = "linear(0, 0.02 2%, 0.089 5%, 0.2 9%, 0.343 14%, 0.505 20%, 0.669 27%, 0.82 35%, 0.945 44%, 1.034 54%, 1.09 64%, 1.113 74%, 1.109 84%, 1.086 93%, 1 100%)";
  function motionEasing(name) {
    if (name === "none") return "linear";
    if (name === "back-out") return "cubic-bezier(0.34, 1.56, 0.64, 1)";
    if (name === "spring") return springEasing;
    return name;
  }
  function bindMotion(element, appearance, slot, { cue = 0, restoreCue, endCue, overlap, reducedMotion } = {}) {
    if (!Number.isFinite(cue) || reducedMotion !== undefined && typeof reducedMotion !== "boolean") throw new TypeError("Motion requires a finite cue and boolean mode");
    const selection = appearance.lock.selection.motion[slot];
    if (selection === undefined) throw new Error("Unknown Motion slot");
    if (selection === null) return { seek() {}, dispose() {} };
    const payload = resolved(appearance.motion[slot], appearance.lock.parameters.motion[slot]);
    validateMotion(payload);
    const version = payload.capability_version === 3 ? 3 : payload.capability_version === 2 ? 2 : 1;
    if (version > appearance.lock.contract_version) throw new Error("Unsupported Motion lock capability");
    if (version === 1 && !["reveal", "exit"].includes(slot)) throw new Error("Motion v1 supports reveal and exit only");
    const normal = payload.slots[selection.entry];
    if (!normal || version >= 2 && selection.entry !== slot) throw new Error("Unknown Motion entry");
    const prepared = preparedFonts.get(appearance);
    if (prepared?.disposed) throw new Error("Appearance is disposed");
    const reduced = reducedMotion ?? prepared?.reducedMotion ?? matchMedia("(prefers-reduced-motion: reduce)").matches;
    const preset = (reduced ? payload.reduced_motion : payload.slots)[selection.entry];
    if (!preset) return { seek() {}, dispose() {} }; // v1's explicit reduced-mode no-op.
    if (version === 1 && (!["none", "linear"].includes(preset.easing) || preset.stagger)) throw new Error("Motion v1 requires linear easing without stagger");
    const targets = slot === "transition" ? [element?.outgoing, element?.incoming] : [element];
    if (targets.some(target => !isElement(target) || !target.isConnected) || targets.length === 2 && targets[0] === targets[1]) throw new TypeError("Motion requires distinct mounted elements");
    if (slot === "emphasis" && normal.effect === "focus-restore" && (!Number.isFinite(restoreCue) || restoreCue < cue + normal.duration)) throw new Error("Invalid Motion restore cue");
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
    const easing = motionEasing(preset.easing);
    const holdFps = preset.hold_fps;
    const rhythm = [];
    if (version >= 2) {
      const kind = `motion_${slot}`;
      for (const target of targets) rhythm.push({ target, time: cue, duration: preset.duration, kind,
        ...(slot === "emphasis" && preset.effect !== "focus-restore" && preset.duration > 0
          ? { after: cue + preset.duration / 5 } : ["glitch-in", "glitch-out"].includes(preset.effect)
            ? { after: cue + preset.duration * .3 } : {}) });
      if (slot === "emphasis" && preset.effect === "focus-restore") rhythm.push({ target: targets[0], time: restoreCue, duration: preset.restore_duration, kind });
    }
    let rhythmSource;
    function registerRhythm() {
      if (!rhythm.length || typeof window === "undefined") return;
      rhythmSource = () => rhythm;
      (global.__hfRhythmSources ??= new Set()).add(rhythmSource);
    }
    function unregisterRhythm() {
      if (!rhythmSource || typeof window === "undefined" || !window.__hfRhythmSources) return;
      global.__hfRhythmSources.delete(rhythmSource);
      rhythmSource = undefined;
    }
    const plans = [];
    const progress = (time, start, duration) => {
      if (duration === 0) return Number(time >= start);
      if (time <= start) return 0;
      if (time >= start + duration) return 1;
      let elapsed = time - start;
      if (holdFps) elapsed = Math.floor(elapsed * holdFps) / holdFps;
      return Math.min(1, Math.max(0, elapsed / duration));
    };
    function plan(target, frames, at) { plans.push({ target, frames, at, properties: Object.keys(frames[0]).filter(key => key !== "easing") }); }
    function visibility(target, visible) { plan(target, [{ visibility: "hidden" }, { visibility: "visible" }], time => Number(visible(time))); }
    const baseTransform = base => base.transform === "none" ? "" : base.transform;
    const transformWith = (base, x = 0, y = 0, scale = 1, rotate = 0) => {
      const parts = [baseTransform(base)];
      if (x || y) parts.push(`translate(${x}px, ${y}px)`);
      if (scale !== 1) parts.push(`scale(${scale})`);
      if (rotate) parts.push(`rotate(${rotate}deg)`);
      return parts.filter(Boolean).join(" ") || "none";
    };
    const clipPath = (direction, hidden) => {
      const amount = `${hidden * 100}%`;
      if (direction === "right") return `inset(0% 0% 0% ${amount})`;
      if (direction === "up") return `inset(${amount} 0% 0% 0%)`;
      if (direction === "down") return `inset(0% 0% ${amount} 0%)`;
      return `inset(0% ${amount} 0% 0%)`;
    };
    const settle = (time, start, duration) => { const p = progress(time, start, duration); return p < 0.65 ? p / 0.65 : 1 + (p - 0.65) / 0.35; };
    function v3Emphasis(target, base) {
      const at = time => progress(time, cue, preset.duration);
      if (preset.effect === "pulse") {
        const scale = preset.scale ?? 1.12;
        plan(target, [
          { transform: base.transform, easing },
          { transform: transformWith(base, 0, 0, scale), easing },
          { transform: base.transform },
        ], time => time <= cue || time >= cue + preset.duration ? null : at(time) * 2);
      } else if (preset.effect === "shake") {
        const x = preset.x ?? 6, y = preset.y ?? 0;
        plan(target, [
          { transform: base.transform, easing },
          { transform: transformWith(base, x, y), easing },
          { transform: transformWith(base, -x, -y), easing },
          { transform: transformWith(base, x * 0.5, -y * 0.5), easing },
          { transform: transformWith(base, -x * 0.5, y * 0.5), easing },
          { transform: base.transform },
        ], time => time <= cue || time >= cue + preset.duration ? null : at(time) * 5);
      } else if (preset.effect === "wobble") {
        const rotate = preset.rotate ?? 8;
        plan(target, [
          { transform: base.transform, easing },
          { transform: transformWith(base, 0, 0, 1, rotate), easing },
          { transform: transformWith(base, 0, 0, 1, -rotate), easing },
          { transform: transformWith(base, 0, 0, 1, rotate * 0.5), easing },
          { transform: transformWith(base, 0, 0, 1, -rotate * 0.5), easing },
          { transform: base.transform },
        ], time => time <= cue || time >= cue + preset.duration ? null : at(time) * 5);
      } else if (preset.effect === "glow") {
        const neutral = base.boxShadow;
        plan(target, [
          { boxShadow: neutral, easing },
          { boxShadow: `0 0 ${preset.blur ?? 16}px ${emphasisColor(preset, appearance)}`, easing },
          { boxShadow: neutral },
        ], time => time <= cue || time >= cue + preset.duration ? null : at(time) * 2);
      }
    }
    function v3RevealExit(target, base) {
      const at = time => progress(time, cue, preset.duration);
      const from = Number(base.opacity) * preset.opacity_from, to = Number(base.opacity) * preset.opacity_to;
      const direction = preset.direction ?? "left";
      if (preset.effect === "pop") {
        plan(target, [
          { transform: transformWith(base, preset.x ?? 0, preset.y ?? 0, preset.scale ?? 0.6), opacity: from, easing },
          { transform: transformWith(base, 0, 0, 1.06), opacity: to, easing },
          { transform: base.transform, opacity: to },
        ], time => settle(time, cue, preset.duration));
      } else if (preset.effect === "stamp") {
        const rotate = preset.rotate ?? -12;
        plan(target, [
          { transform: transformWith(base, preset.x ?? 0, preset.y ?? 0, preset.scale ?? 1.4, rotate), opacity: from, easing },
          { transform: transformWith(base, 0, 0, 0.98, rotate * 0.12), opacity: to, easing },
          { transform: base.transform, opacity: to },
        ], time => settle(time, cue, preset.duration));
      } else if (preset.effect === "wipe") {
        plan(target, [
          { clipPath: clipPath(direction, 1), opacity: from, easing },
          { clipPath: clipPath(direction, 0), opacity: to },
        ], at);
      } else if (preset.effect === "glitch-in") {
        const x = preset.x ?? 16, y = preset.y ?? 0;
        plan(target, [
          { transform: transformWith(base, x, -y), opacity: from, easing: "steps(1, end)" },
          { transform: transformWith(base, -x, y), opacity: to, easing: "steps(1, end)" },
          { transform: transformWith(base, x, y), opacity: from, easing: "steps(1, end)" },
          { transform: transformWith(base, -x, -y), opacity: to, easing: "steps(1, end)" },
          { transform: base.transform, opacity: to },
        ], time => at(time) * 4);
      } else if (preset.effect === "pop-out") {
        plan(target, [
          { transform: base.transform, opacity: from, easing },
          { transform: transformWith(base, 0, 0, 1.04), opacity: from, easing },
          { transform: transformWith(base, preset.x ?? 0, preset.y ?? 0, preset.scale ?? 0.75), opacity: to },
        ], time => settle(time, cue, preset.duration));
      } else if (preset.effect === "wipe-out") {
        plan(target, [
          { clipPath: clipPath(direction, 0), opacity: from, easing },
          { clipPath: clipPath(direction, 1), opacity: to },
        ], at);
      } else if (preset.effect === "glitch-out") {
        const x = preset.x ?? 16, y = preset.y ?? 0;
        plan(target, [
          { transform: base.transform, opacity: from, easing: "steps(1, end)" },
          { transform: transformWith(base, x, -y), opacity: from, easing: "steps(1, end)" },
          { transform: transformWith(base, -x, y), opacity: to, easing: "steps(1, end)" },
          { transform: transformWith(base, x, y), opacity: to, easing: "steps(1, end)" },
          { transform: base.transform, opacity: to },
        ], time => at(time) * 4);
      }
      visibility(target, time => slot === "reveal" ? preset.hide_before === false || time >= cue : time < cue + preset.duration);
    }
    function v3Transition(target, base, index) {
      const at = time => progress(time, cue, preset.duration);
      const direction = preset.direction ?? "left";
      if (preset.effect === "wipe") {
        plan(target, index ? [
          { clipPath: clipPath(direction, 1), easing },
          { clipPath: clipPath(direction, 0) },
        ] : [
          { clipPath: clipPath(direction, 0), easing },
          { clipPath: clipPath(direction, 1) },
        ], at);
      } else if (preset.effect === "push") {
        const axis = direction === "left" || direction === "right" ? "X" : "Y";
        const sign = direction === "left" || direction === "up" ? 1 : -1;
        const offset = amount => {
          const value = `translate${axis}(${amount}%)`;
          return baseTransform(base) ? `${baseTransform(base)} ${value}` : value;
        };
        plan(target, index ? [
          { transform: offset(sign * 100), easing },
          { transform: base.transform },
        ] : [
          { transform: base.transform, easing },
          { transform: offset(-sign * 100) },
        ], at);
      } else if (preset.effect === "glitch-cut") {
        const opacity = Number(base.opacity);
        plan(target, index ? [
          { opacity: 0, easing: "steps(1, end)" },
          { opacity, easing: "steps(1, end)" },
          { opacity: opacity * 0.3, easing: "steps(1, end)" },
          { opacity },
        ] : [
          { opacity, easing: "steps(1, end)" },
          { opacity: 0, easing: "steps(1, end)" },
          { opacity: opacity * 0.3, easing: "steps(1, end)" },
          { opacity: 0 },
        ], time => at(time) * 3);
      }
    }
    for (const [index, target] of targets.entries()) {
      const base = getComputedStyle(target);
      if (slot === "emphasis" && preset.effect === "focus-restore") {
        const original = { outlineColor: base.outlineColor, outlineWidth: base.outlineWidth, outlineStyle: base.outlineStyle, easing };
        const focus = { outlineColor: emphasisColor(preset, appearance), outlineWidth: `${preset.outline_width}px`, outlineStyle: "solid", easing };
        plan(target, [original, focus, original], time => time < restoreCue ? progress(time, cue, preset.duration) : 1 + progress(time, restoreCue, preset.restore_duration));
      } else if (slot === "emphasis") {
        v3Emphasis(target, base);
      } else if (slot === "transition") {
        if (version === 3 && !["crossfade", "cut"].includes(preset.effect)) { v3Transition(target, base, index); continue; }
        const opacity = Number(base.opacity);
        plan(target, [{ opacity: index ? 0 : opacity, easing }, { opacity: index ? opacity : 0 }], time => progress(time, cue, preset.duration));
        visibility(target, time => index ? time >= cue : time < cue + preset.duration);
      } else if (version === 3 && !["fade", "short-rise", "fade-out"].includes(preset.effect)) {
        v3RevealExit(target, base);
      } else {
        const original = {}, changed = {};
        if (version === 1 || Object.hasOwn(preset, "x") || Object.hasOwn(preset, "y") || Object.hasOwn(preset, "scale")) {
          original.transform = base.transform;
          changed.transform = `${base.transform === "none" ? "" : base.transform} translate(${preset.x ?? 0}px, ${preset.y ?? 0}px) scale(${preset.scale ?? 1})`;
        }
        const frames = slot === "reveal" ? [changed, original] : [original, changed];
        if (version >= 2) {
          frames[0].opacity = Number(base.opacity) * preset.opacity_from;
          frames[1].opacity = Number(base.opacity) * preset.opacity_to;
        }
        frames[0].easing = easing;
        plan(target, frames, time => progress(time, cue, preset.duration));
        if (version >= 2) visibility(target, time => slot === "reveal" ? preset.hide_before === false || time >= cue : time < cue + preset.duration);
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
        if (!disposed) for (const { animation, at } of animations) {
          const current = at(time);
          animation.effect.updateTiming({ fill: current === null ? "none" : "both" });
          animation.currentTime = current === null ? -1 : current;
        }
      },
      dispose() {
        if (disposed) return;
        disposed = true;
        unregisterRhythm();
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
      registerRhythm();
      binding.seek(0);
      return binding;
    } catch (error) { binding.dispose(); throw error; }
  }
  async function mountBackground(stage, appearance, cues) {
    if (!isElement(stage)) throw new TypeError("Background requires an element");
    const payload = resolved(appearance.background, appearance.lock.parameters.background);
    if (payload.renderer !== "module") {
      stage.style.backgroundColor = payload.renderer === "transparent" ? "transparent" : payload.parameters.color;
      return { renderAt() {}, dispose() {} };
    }
    const entry = backgroundPackages.get(appearance);
    if (!entry || !["card", "explainer", "showcase"].includes(appearance.lock.mode)) throw new Error("Unprepared module Background");
    const params = structuredClone(payload.parameters);
    params.moods = (params.moods || []).map(mood => ({ ...mood, cue: cues.find(mood.cue) }));
    const module = await import(entry);
    if (typeof module.create !== "function") throw new Error("Background module requires create");
    const binding = await module.create(stage, params, { seed: appearance.lock.seed ?? 0, width: stage.clientWidth, height: stage.clientHeight });
    if (typeof binding?.renderAt !== "function" || typeof binding?.dispose !== "function") throw new Error("Invalid Background module binding");
    return binding;
  }
  global.HarnessAppearance = { load, apply, bindMotion, mountBackground };
})(window);
