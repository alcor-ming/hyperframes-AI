/* Shared shot input checks; the authored module supplies its own time-pure performance. */
(function (global) {
  'use strict';
  const own = (value, key) => Object.hasOwn(value, key);
  const finite = value => typeof value === 'number' && Number.isFinite(value);
  function relative(value) {
    if (typeof value !== 'string' || /[\\:%?#\u0000-\u001f]/.test(value) || value.split('/').some(p => !p || p === '.' || p === '..')) throw new Error('broll_path_requires_project_closure');
    return value;
  }
  function layer(element, name, doc) {
    if (!element?.isConnected || element.ownerDocument !== doc || element.closest('[data-hf-layer]')?.dataset.hfLayer !== name) throw new Error('broll_requires_' + name + '_host');
  }
  function parameter(value, spec) {
    const types = {string: v => typeof v === 'string', number: finite, integer: Number.isInteger, boolean: v => typeof v === 'boolean'};
    if (!types[spec.type]?.(value) || spec.minimum !== undefined && value < spec.minimum || spec.maximum !== undefined && value > spec.maximum || spec.enum && !spec.enum.includes(value)) throw new Error('broll_parameter_type_or_range');
    if (typeof value === 'string' && /[<>;{}]|url\s*\(|expression\s*\(|javascript:/i.test(value)) throw new Error('broll_parameter_expression');
  }
  function geometry(node, root = true) {
    const ignored = new Set(['data-icon', 'data-icon-sha256', 'style', 'class', 'id', 'width', 'height', 'stroke', 'stroke-width', 'color', 'aria-hidden', 'role']);
    return [node.localName, [...node.attributes].filter(a => a.namespaceURI !== 'http://www.w3.org/2000/xmlns/' && a.name !== 'data-hf-id' && (!root || !ignored.has(a.name)))
      .map(a => [a.name, a.value]).sort(), [...node.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent.trim()).join(''),
      [...node.children].map(child => geometry(child, false))];
  }
  async function mount(metadata, options, build) {
    const contract = metadata?.broll, {stage, text, appearance, cues, startCue, endCue, slots = {}, params = {}} = options;
    const doc = stage?.ownerDocument;
    layer(stage, 'stage', doc);
    if (text) {
      layer(text, 'text', doc);
      if (stage.contains(text) || text.contains(stage)) throw new Error('broll_hosts_must_be_independent');
    }
    if (!contract || !appearance?.lock || typeof build !== 'function') throw new Error('broll_requires_frozen_contract_and_appearance');
    const cueTime = cue => typeof cue === 'number' ? cue : cues?.find(cue);
    const start = cueTime(startCue), end = cueTime(endCue), duration = end - start;
    // Decimal cues subtract inexactly (11.2 - 10 = 1.1999999999999993); compare at cue magnitude, keep the actual duration for mapping.
    const tolerance = 1e-9 * Math.max(1, Math.abs(start), Math.abs(end));
    const below = limit => duration < limit - tolerance, above = limit => duration > limit + tolerance;
    if (!finite(start) || start < 0 || !finite(end) || below(contract.duration.min) || above(contract.duration.max)) throw new Error('broll_duration_outside_range');
    if (!['stretch', 'hold-end'].includes(contract.timing) || contract.timing === 'hold-end' && below(contract.duration.default)) throw new Error('broll_invalid_timing');
    if (!contract.caption_safe_zone[appearance.lock.ratio]) throw new Error('broll_unsupported_ratio');
    if (!slots || typeof slots !== 'object' || Array.isArray(slots) || Object.keys(slots).some(key => !own(contract.slots, key))) throw new Error('broll_unknown_slot');
    if (!params || typeof params !== 'object' || Array.isArray(params) || Object.keys(params).some(key => !own(contract.params, key))) throw new Error('broll_unknown_parameter');
    const resolvedParams = {};
    for (const [path, spec] of Object.entries(contract.params)) {
      const value = own(params, path) ? params[path] : spec.default;
      parameter(value, spec); resolvedParams[path] = value;
    }
    const base = new URL(appearance.projectURL || '.', doc.baseURI);
    if (base.origin !== doc.location.origin) throw new Error('broll_requires_project_origin');
    const local = path => new URL(relative(path).split('/').map(encodeURIComponent).join('/'), base);
    const read = async (path, json = true) => {
      const response = await fetch(local(path), {redirect: 'error'});
      if (!response.ok) throw new Error('broll_missing_closure_file:' + path);
      return json ? response.json() : response.text();
    };
    let components;
    const closure = async () => {
      components ??= (await read('COMPONENT_LOCK.json')).components;
      if (!Array.isArray(components)) throw new Error('broll_invalid_component_lock');
      return components;
    };
    const values = {};
    for (const [name, spec] of Object.entries(contract.slots)) {
      if (!own(slots, name)) throw new Error('broll_missing_slot:' + name);
      const value = slots[name];
      if (['text', 'number'].includes(spec.type)) {
        if (spec.type === 'text' ? typeof value !== 'string' : !finite(value)) throw new Error('broll_slot_type:' + name);
        if ([...String(value)].length > spec.max_chars) throw new Error('broll_slot_capacity:' + name);
        if (spec.layer === 'text' && (!text || !contract.carries_info)) throw new Error('broll_text_host_required');
        values[name] = value;
      } else if (spec.type === 'media') {
        relative(value);
        const record = (await closure()).find(item => item.asset_kind === 'media' && item.install_files?.includes(value));
        if (!record) throw new Error('broll_media_outside_closure');
        const asset = await read(record.vendor_path + '/asset.json');
        if (value !== record.vendor_path + '/' + asset.entry) throw new Error('broll_media_requires_registered_entry');
        values[name] = local(value).href;
      } else if (spec.type === 'icon') {
        if (!value || Object.keys(value).sort().join(',') !== 'path,ref' || !/^lucide:[a-z0-9]+(?:-[a-z0-9]+)*@\d+\.\d+\.\d+(?:-[A-Za-z0-9.-]+)?$/.test(value.ref)) throw new Error('broll_icon_requires_exact_reference_and_path');
        relative(value.path);
        let original, row;
        for (const item of await closure()) if (item.asset_kind === 'icon-set') {
          const asset = await read(item.vendor_path + '/asset.json');
          const icons = await read(item.vendor_path + '/' + asset.entry);
          row = icons.icons?.find(icon => value.ref === `lucide:${icon.name}@${icons.version}`);
          if (row) { original = await read(item.vendor_path + '/' + row.path, false); break; }
        }
        if (!original) throw new Error('broll_icon_outside_closure');
        const parser = new DOMParser(), used = parser.parseFromString(await read(value.path, false), 'image/svg+xml').documentElement;
        const frozen = parser.parseFromString(original, 'image/svg+xml').documentElement;
        if (used.localName !== 'svg' || used.getAttribute('data-icon') !== value.ref || used.getAttribute('data-icon-sha256') !== row.sha256 || JSON.stringify(geometry(used)) !== JSON.stringify(geometry(frozen))) throw new Error('broll_icon_source_mismatch');
        frozen.setAttribute('data-icon', value.ref); frozen.setAttribute('data-icon-sha256', row.sha256);
        frozen.setAttribute('stroke', 'currentColor'); frozen.style.color = 'var(--appearance-colors-text)';
        values[name] = {ref: value.ref, path: value.path, svg: frozen.outerHTML};
      } else throw new Error('broll_unsupported_slot_type');
    }
    const map = time => start + time * (contract.timing === 'stretch' ? duration / contract.duration.default : 1);
    let performance, rhythm, textSource, disposed = false;
    const dispose = () => {
      if (disposed) return;
      disposed = true; global.__hfRhythmSources?.delete(rhythm);
      if (textSource) global.__hfTextSources?.delete(textSource);
      performance?.dispose?.();
    };
    try {
      for (const root of [stage, text].filter(Boolean)) {
        global.HarnessAppearance.apply(root, appearance); root.style.backgroundColor = 'transparent';
      }
      performance = await build({stage, text, slots: values, params: resolvedParams, appearance, start, end, duration});
      if (typeof performance?.renderAt !== 'function' || !Array.isArray(performance.events)) throw new Error('broll_invalid_performance');
      await doc.fonts.ready;
      const ownership = metadata.text_ownership;
      if ((stage.tagName === 'CANVAS' || stage.querySelector?.('canvas') || own(metadata, 'text_ownership')) && typeof performance.texts !== 'function') throw new Error('broll_requires_texts_inventory');
      const rawTexts = typeof performance.texts === 'function' ? await performance.texts() : [];
      if (!Array.isArray(rawTexts)) throw new Error('broll_invalid_texts_inventory');
      let scene = stage.closest?.('[data-scene-id]')?.dataset?.sceneId;
      if (scene === undefined) for (let node = stage; node; node = node.parentElement) {
        if (typeof node.id === 'string' && /^S[0-9]+$/.test(node.id)) { scene = node.id; break; }
      }
      const fontFamily = getComputedStyle(stage).fontFamily, ids = new Set();
      const inventory = rawTexts.map(item => {
        if (!item || typeof item !== 'object' || Array.isArray(item)) throw new Error('broll_invalid_text_item');
        if (typeof item.id !== 'string' || !item.id || ids.has(item.id)) throw new Error('broll_invalid_text_id');
        ids.add(item.id);
        if (typeof item.text !== 'string' || !item.text) throw new Error('broll_invalid_text_value:' + item.id);
        if (!finite(item.start) || !finite(item.end) || item.start < 0 || item.start >= item.end || item.end > contract.duration.default) throw new Error('broll_invalid_text_window:' + item.id);
        if (!['attached', 'independent'].includes(item.kind)) throw new Error('broll_invalid_text_kind:' + item.id);
        if (typeof item.embedded !== 'boolean') throw new Error('broll_invalid_text_embedded:' + item.id);
        if (item.kind === 'independent' && item.embedded && (typeof item.text_type !== 'string' || !item.text_type)) throw new Error('broll_invalid_text_type:' + item.id);
        let region;
        if (item.region !== undefined) {
          const box = item.region, unit = value => finite(value) && value >= 0 && value <= 1;
          if (!box || typeof box !== 'object' || !unit(box.x) || !unit(box.y) || !unit(box.width) || !unit(box.height) || box.x + box.width > 1 + tolerance || box.y + box.height > 1 + tolerance) throw new Error('broll_invalid_text_region:' + item.id);
          region = {x: box.x, y: box.y, width: box.width, height: box.height};
        }
        const record = {id: item.id, text: item.text, start: map(item.start), end: Math.min(map(item.end), end), kind: item.kind, embedded: item.embedded};
        if (item.text_type !== undefined) record.text_type = item.text_type;
        if (region) record.region = region;
        record.scene = scene; record.asset = options.assetRef || metadata.id;
        record.selector = '#' + metadata.id + ' [data-hf-id="' + item.id + '"]';
        record.layer = item.embedded ? 'stage' : 'text';
        record.font_family = fontFamily;
        record.ownership_allowed = item.kind === 'attached' || !item.embedded || ownership?.mode === 'embedded' && Array.isArray(ownership.kinds) && ownership.kinds.includes(item.text_type);
        return record;
      });
      textSource = () => inventory.map(entry => ({...entry, ...(entry.region ? {region: {...entry.region}} : {})}));
      (global.__hfTextSources ??= new Set()).add(textSource);
      for (const [name, spec] of Object.entries(contract.slots)) if (['text', 'number'].includes(spec.type)) {
        const label = performance.labels?.[name];
        const embedded = (!label || !label.isConnected) && inventory.find(entry => entry.id === name && entry.embedded && entry.text === String(values[name]));
        if (embedded) continue;
        layer(label, spec.layer, doc);
        if (!(appearance.lock.card_fonts?.fonts || appearance.theme?.fonts)?.length || label.textContent !== String(values[name]) || label.clientWidth <= 0 || label.clientHeight <= 0 || label.scrollWidth > label.clientWidth + 1 || label.scrollHeight > label.clientHeight + 1) throw new Error('broll_frozen_font_capacity:' + name);
      }
      const events = performance.events.map(event => {
        if (!finite(event.time) || event.time < 0 || event.time > contract.duration.default || !event.target?.isConnected || !(stage.contains(event.target) || text?.contains(event.target))) throw new Error('broll_invalid_moment_target');
        return {time: map(event.time), duration: 0, target: event.target, kind: 'broll_moment'};
      });
      rhythm = () => events;
      (global.__hfRhythmSources ??= new Set()).add(rhythm);
      const binding = {
        renderAt(t) {
          if (!finite(t)) throw new Error('broll_time_must_be_finite');
          if (!disposed) performance.renderAt(Math.max(0, Math.min(contract.duration.default,
            (t - start) * (contract.timing === 'stretch' ? contract.duration.default / duration : 1))), t);
        },
        moments: () => ({key_moments: [...new Set(events.map(event => event.time))].sort((a, b) => a - b), sfx_cues: contract.sfx_cues.map(cue => ({...cue, time: map(cue.time)}))}),
        texts: textSource,
        dispose,
      };
      binding.renderAt(start); return binding;
    } catch (error) { dispose(); throw error; }
  }
  global.HarnessBroll = {mount};
})(window);
