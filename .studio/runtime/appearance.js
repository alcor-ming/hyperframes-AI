/* Static appearance adapter. Host must verify the frozen package closure before serving it.
 * Scene layout, text and cue timing remain the host's responsibility.
 */
(function (global) {
  "use strict";
  const preparedFonts = new WeakMap();
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
    if (lock.schema_version !== 1 || !Array.isArray(lock.assets)) throw new Error("Unsupported appearance lock");
    const result = { lock, motion: {} };
    let themePackage;
    async function payload(kind, selected) {
      const asset = lock.assets.find(item => item.ref === selected.ref);
      if (!asset || asset.kind !== kind || asset.package_sha256 !== selected.package_sha256) throw new Error("Appearance selection differs from frozen closure");
      const metadata = await read(`${asset.vendor_path}/asset.json`);
      if (metadata.kind !== kind || `${metadata.id}@v${metadata.version}` !== selected.ref) throw new Error("Appearance package identity mismatch");
      if (kind === "theme") themePackage = { asset, metadata };
      return read(`${asset.vendor_path}/${metadata.entry}`);
    }
    for (const kind of ["theme", "background"]) result[kind] = await payload(kind, lock.selection[kind]);
    for (const [slot, selection] of Object.entries(lock.selection.motion)) {
      if (selection !== null) result.motion[slot] = await payload("motion", selection.asset);
    }
    const fonts = resolved(result.theme, lock.parameters.theme).fonts || [];
    if (!Array.isArray(fonts)) throw new Error("Theme fonts must be an array");
    const state = { faces: [], families: new Map(), declaration: JSON.stringify(fonts), disposed: false };
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
    if (!(stage instanceof Element)) throw new TypeError("Appearance requires a stage element");
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
  function bindMotion(element, appearance, slot, { cue = 0 } = {}) {
    if (!(element instanceof Element) || !Number.isFinite(cue)) throw new TypeError("Motion requires an element and finite cue");
    const selection = appearance.lock.selection.motion[slot];
    if (selection === undefined) throw new Error("Unknown Motion slot");
    if (selection === null) return { seek() {}, dispose() {} };
    if (!["reveal", "exit"].includes(slot)) throw new Error("Adapter supports reveal and exit Motion only");
    const payload = resolved(appearance.motion[slot], appearance.lock.parameters.motion[slot]);
    const group = matchMedia("(prefers-reduced-motion: reduce)").matches ? payload.reduced_motion : payload.slots;
    const preset = group[selection.entry];
    if (!preset) return { seek() {}, dispose() {} };
    if (!["none", "linear"].includes(preset.easing) || preset.stagger) throw new Error("Adapter requires linear Motion without stagger");
    if (!Number.isFinite(preset.duration) || preset.duration < 0) throw new Error("Invalid Motion duration");
    for (const key of ["x", "y", "scale"]) if (preset[key] !== undefined && !Number.isFinite(preset[key])) throw new Error("Invalid Motion transform");
    const transformed = `translate(${preset.x ?? 0}px, ${preset.y ?? 0}px) scale(${preset.scale ?? 1})`;
    const frames = [{ transform: transformed }, { transform: "translate(0px, 0px) scale(1)" }];
    if (slot === "exit") frames.reverse();
    const animation = new Animation(new KeyframeEffect(element, frames, { duration: preset.duration * 1000, fill: "both", easing: "linear" }), document.timeline);
    animation.pause();
    animation.currentTime = 0;
    return {
      seek(time) {
        if (!Number.isFinite(time)) throw new TypeError("Motion time must be finite");
        animation.currentTime = Math.max(0, time - cue) * 1000;
      },
      dispose() { animation.cancel(); },
    };
  }
  global.HarnessAppearance = { load, apply, bindMotion };
})(window);
