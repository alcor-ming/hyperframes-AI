/* Geometry and preset motions extracted from approved card-svg-slots-v352-r3. */
(function (global) {
  "use strict";
  async function mount(options) {
  const { stage, text, card, cues, cueTime, resolveSVG, appearance } = options;
  let resolveTime = cueTime;
  const start = options.start ?? 0, end = options.end;
  const doc = stage?.ownerDocument;
  const SVG_NS = 'http://www.w3.org/2000/svg';
  if (!doc || text?.ownerDocument !== doc || !stage.isConnected || !text.isConnected || stage === text || stage.contains(text) || text.contains(stage)) throw new Error('card_hosts_require_independent_layers');
  if (!Number.isFinite(start) || !Number.isFinite(end) || end <= start) throw new Error('invalid_card_interval');
  if (!card || !/^F0[1-8]$/.test(card.preset) || !Array.isArray(card.lines) || ![card.title, card.note, card.input, card.inputLabel, card.outputLabel, ...card.lines].some(Boolean)) throw new Error('invalid_card_content');
  const ratio = options.ratio ?? '16:9';
  if (!['16:9', '9:16'].includes(ratio)) throw new Error('invalid_card_ratio');
  const localTime = query => {
    const value = resolveTime ? resolveTime(query) : typeof query === 'number' ? query : cues?.find(query);
    if (!Number.isFinite(value) || value < start || value > end) throw new Error('invalid_card_cue');
    return value - start;
  };
  const timeOf = (slot, fallback = 0) => slot ? localTime(slot.cue) : fallback;
  const ROWS = card.lines.map(line => ({ body: line.text, key: (line.indexKey || line.key)?.text || '', icon: (card.preset === 'F06' ? line.key : line)?.svg }));
  const TITLE_MAIN = card.title?.text || '', TITLE_IO = TITLE_MAIN, NOTE = card.note?.text || '';
  const INPUT_TEXT = card.input?.text || '', INPUT_LABEL = card.inputLabel?.text || '', OUTPUT_LABEL = card.outputLabel?.text || '';
  const TITLE_ICON = card.title?.svg, INPUT_ICON = card.input?.svg, OUTPUT_ICON = card.outputLabel?.svg;
  const state = { preset: card.preset, ratio, count: card.lines.length, titleIcon: !!TITLE_ICON,
    inputIcon: !!INPUT_ICON, outputIcon: !!OUTPUT_ICON, svg: ROWS.map(row => !!row.icon), figure: !!card.figure };
  let rowTimes = card.lines.map(line => timeOf(line));
  if (rowTimes.some((time, i) => i && time < rowTimes[i - 1])) throw new Error('card_rows_require_ordered_cues');
  const reduce = options.reducedMotion ?? global.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const themeColors = { muted: null, accent: null, ink: null };
  const svgSources = new Map(), svgNodes = new Map();
  let decorCard, disposed = false;
  const stageRoot = el('div', 'hf-card-kit'), textRoot = el('div', 'hf-card-kit');
  for (const root of [stageRoot, textRoot]) {
    root.dataset.cardId = card.id || '';
    if (card.scene) root.dataset.sceneId = card.scene;
  }
  stageRoot.dataset.hfLayer = 'stage'; textRoot.dataset.hfLayer = 'text';
  const scale = text.getBoundingClientRect().width / text.offsetWidth || 1;
  var PRESETS = [
    { id: 'F01', name: '白页标注', material: 'M1', structure: 'default', depth: 'none' },
    { id: 'F02', name: '柔雾色块', material: 'M2', structure: 'default', depth: 'none' },
    { id: 'F03', name: '毛玻璃', material: 'M3', structure: 'default', depth: 'none' },
    { id: 'F04', name: '索引档案', material: 'M1', structure: 'S1', depth: 'none' },
    { id: 'F05', name: '编辑引文', material: 'M1', structure: 'S2', depth: 'none' },
    { id: 'F06', name: '票据清单', material: 'M1', structure: 'S3', depth: 'none' },
    { id: 'F07', name: '窗口面板', material: 'M2', structure: 'S4', depth: 'none' },
    { id: 'F08', name: '硬边叠纸', material: 'M2', structure: 'default', depth: 'D1' }
  ];

  var PRESET_BY_ID = {};
  for (var pi = 0; pi < PRESETS.length; pi++) PRESET_BY_ID[PRESETS[pi].id] = PRESETS[pi];

  /* Applicable controls per preset (line icon slots, figure, input/output). */
  var FEATURES = {
    F01: { lineIcons: true, figure: false, io: false },
    F02: { lineIcons: true, figure: false, io: false },
    F03: { lineIcons: true, figure: true, io: false },
    F04: { lineIcons: true, figure: false, io: false },
    F05: { lineIcons: false, figure: true, io: false },
    F06: { lineIcons: true, figure: false, io: false },
    F07: { lineIcons: false, figure: false, io: true },
    F08: { lineIcons: true, figure: true, io: false }
  };

  var FIGURE_W = 640;
  var FIGURE_H = 180;
  var FIG_SHALLOW_W = 400;

  var CARD_REVEAL = 0.35;
  var TITLE_START = 0.15;
  var TITLE_REVEAL = 0.3;
  var ROW_REVEAL = 0.25;
  var EMPHASIS_OFFSET = 0.25;
  var EMPHASIS_LENGTH = 0.4;
  var MARK_REVEAL = 0.3;
  var FIGURE_START = 0.4;
  var FIGURE_REVEAL = 0.4;
  var FIG_EMPH_START = 4.8;
  var FIG_EMPH_END = 5.2;
  var EXIT_START = 8.2;
  var EXIT_LENGTH = 0.8;
  /* F03 frost: top-edge light rises after the surface; one restrained 4.8-5.2 highlight. */
  var EDGE_START = 4.8;
  var EDGE_END = 5.2;
  /* F08: rear sheets animate from overlapping to offset while the front stays stable. */
  var F08_SHEET_START = 0.35;
  var F08_SHEET_END = 1.0;
  /* F07: input first, connector, then the output document. */
  var F07_IN_START = 0.25;
  var F07_IN_LEN = 0.35;
  var F07_CONN_START = 0.55;
  var F07_CONN_LEN = 0.3;
  var F07_TITLE_START = 0.85;

  /* ---------------------------------------------------------- geometry --- */

  var CANVAS = {
    '16:9': { width: 1920, height: 1080 },
    '9:16': { width: 1080, height: 1920 }
  };

  var REGIONS = {
    '16:9': {
      full:   { x: 72, y: 72,  w: 1776, h: 936 },
      left:   { x: 72, y: 72,  w: 864,  h: 936 },
      right:  { x: 984, y: 72, w: 864,  h: 936 },
      top:    { x: 72, y: 72,  w: 1776, h: 444 },
      bottom: { x: 72, y: 564, w: 1776, h: 444 }
    },
    '9:16': {
      full:   { x: 72, y: 72,  w: 936, h: 1776 },
      top:    { x: 72, y: 72,  w: 936, h: 864 },
      bottom: { x: 72, y: 984, w: 936, h: 864 },
      left:   { x: 72, y: 72,  w: 444, h: 1776 },
      right:  { x: 564, y: 72, w: 444, h: 1776 }
    }
  };

  function el(tag, className) {
    var node = doc.createElement(tag);
    if (className) node.className = className;
    return node;
  }

  function svgEl(name, attrs) {
    var node = doc.createElementNS(SVG_NS, name);
    if (attrs) for (var k in attrs) node.setAttribute(k, attrs[k]);
    return node;
  }

  function clearNode(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function clamp01(x) { return x < 0 ? 0 : x > 1 ? 1 : x; }

  function easeOut(p) { var q = 1 - p; return 1 - q * q * q; }

  function round2(n) { return Math.round(n * 100) / 100; }

  function parseColor(value) {
    var text = String(value || '').trim();
    if (/^rgba?\(/.test(text)) return text.match(/[\d.]+/g).slice(0, 3).map(Number);
    var hex = text.charAt(0) === '#' ? text.slice(1) : text;
    if (hex.length === 3) hex = hex.charAt(0) + hex.charAt(0) + hex.charAt(1) + hex.charAt(1) + hex.charAt(2) + hex.charAt(2);
    if (hex.length !== 6) return null;
    var n = parseInt(hex, 16);
    if (!isFinite(n)) return null;
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  }

  function mixColor(a, b, t) {
    if (!a || !b) return 'var(--muted)';
    return 'rgb(' + Math.round(a[0] + (b[0] - a[0]) * t) + ', ' +
      Math.round(a[1] + (b[1] - a[1]) * t) + ', ' +
      Math.round(a[2] + (b[2] - a[2]) * t) + ')';
  }

  /* Accumulate offsetLeft/offsetTop up to the card in untransformed layout
     coordinates. offset* (never getBoundingClientRect) keeps the measurement
     stable under the canvas scale and under seek transforms. */
  function offsetInCard(node, stopNode) {
    var x = 0, y = 0, current = node;
    while (current && current !== stopNode) {
      x += current.offsetLeft || 0;
      y += current.offsetTop || 0;
      current = current.offsetParent;
    }
    return { x: x, y: y };
  }

  /* First rendered line width of a text node, in untransformed layout units.
     Falls back to the box width when a range measurement is unavailable. */
  function firstLineWidth(node) {
    if (!node) return 0;
    var boxW = node.clientWidth;
    try {
      if (doc.createRange && node.firstChild && node.firstChild.nodeType === 3) {
        var rng = doc.createRange();
        rng.selectNodeContents(node);
        var rects = rng.getClientRects();
        if (rects && rects.length) {
          var rw = rects[0].width;
          if (scale > 0) rw = rw / scale;
          if (rw > 4) return Math.min(rw, boxW);
        }
      }
    } catch (e) { /* measurement is best-effort; fall back to box width */ }
    return boxW;
  }

  var cardEl = null;
  var decoEl = null;
  var layer2El = null;
  var layer4El = null;
  var figLabelsEl = null;
  var P = null;
  var slots = [];
  var overflowNodes = [];
  var mark = { title: null, titleIcon: null, rows: [], figures: [], footer: null };

  var pad = 40;
  var narrow = false;
  var shallow = false;
  var cardW = 0;
  var contentW = 0;
  var overflow = false;
  var maxRows = 6;
  var region = REGIONS['16:9'].left;

  function features() { return FEATURES[state.preset] || FEATURES.F06; }
  function materialOf() { var p = PRESET_BY_ID[state.preset]; return p ? p.material : 'M0'; }

  function regionKind(reg) {
    if (reg.w < 600) return 'narrow';
    if (reg.h < 500) return 'shallow';
    return 'normal';
  }

  function computeMaxRows() {
    var reg = region;
    var kind = regionKind(reg);
    if (kind === 'shallow') return 2;
    if (kind === 'narrow') return 4;
    if (state.preset === 'F05' || state.preset === 'F07') return 4;
    /* F04 entries and F06 receipt rows are taller (key above body / wrapped
       value), so six rows require a normal region at least 900px tall. */
    if (state.preset === 'F04' || state.preset === 'F06') return reg.h >= 900 ? 6 : 4;
    if ((state.preset === 'F03' || state.preset === 'F08') && state.figure) return 4;
    return 6;
  }

  function rowStartFor(index) { return index < rowTimes.length ? rowTimes[index] : timeOf(card.note); }
  function itemStart(index) { return index < 0 ? TITLE_START : rowStartFor(index); }

  function itemP(t, index) {
    var len = index < 0 ? TITLE_REVEAL : ROW_REVEAL;
    return easeOut(clamp01((t - itemStart(index)) / len));
  }

  function rearOffset() { return narrow ? 16 : 32; }

  function buildCard() {
    var reg = region;
    narrow = reg.w < 600;
    shallow = reg.h < 500;
    pad = (narrow || shallow) ? 28 : 40;
    /* F06 uses a narrower receipt paper (640-720) on normal regions, anchored
       left; narrow and shallow regions keep the actual region width. */
    cardW = (state.preset === 'F06' && !shallow && !narrow) ? Math.max(640, Math.min(720, reg.w)) : reg.w;
    contentW = cardW - pad * 2;

    cardEl = el('div', 'card card--' + regionKind(reg));
    cardEl.style.left = reg.x + 'px';
    cardEl.style.top = reg.y + 'px';
    cardEl.style.width = cardW + 'px';
    cardEl.style.height = reg.h + 'px';
    cardEl.style.setProperty('--pad', pad + 'px');
    cardEl.setAttribute('data-preset', state.preset);
    cardEl.setAttribute('data-material', materialOf());
    decorCard = cardEl.cloneNode(false);

    layer2El = el('div', 'layer layer2');
    layer2El.setAttribute('data-layer', '2');
    decoEl = el('div', 'deco');
    decoEl.setAttribute('data-layer', '2');
    layer2El.appendChild(decoEl);

    layer4El = el('div', 'layer layer4');
    layer4El.setAttribute('data-layer', '4');
    figLabelsEl = el('div', 'figlabels');
    layer4El.appendChild(figLabelsEl);

    P = {
      preset: state.preset, rows: [], figSlots: [], figRect: null, figSvg: null,
      bands: [], rowBands: [], entries: [], sheets: [], extras: []
    };

    buildContent();

    cardEl.appendChild(layer4El);
    decorCard.appendChild(layer2El);
    textRoot.appendChild(cardEl);
    stageRoot.appendChild(decorCard);
  }

  /* --------------------------------------------------------- builders ---- */

  function addTitle(parent, text, withIcon) {
    var block = el('div', 'title-block');
    if (!text) block.style.display = 'none';
    var spacer = null;
    if (withIcon) { spacer = el('span', 'spacer spacer-title'); block.appendChild(spacer); }
    var h = el('h1', 't-title');
    h.setAttribute('data-layer', '4');
    h.textContent = text;
    block.appendChild(h);
    parent.appendChild(block);
    return { block: block, spacer: spacer, node: h };
  }

  function addNote(parent, text) {
    var n = el('div', 't-note note');
    if (!text) n.style.margin = '0';
    n.setAttribute('data-layer', '4');
    n.textContent = text;
    parent.appendChild(n);
    return n;
  }

  function textNode(tag, cls, text) {
    var n = el(tag, cls);
    n.setAttribute('data-layer', '4');
    n.textContent = text;
    return n;
  }

  function wantsIcon(index) {
    return features().lineIcons && state.svg[index] !== false;
  }

  function pushRow(ref) { P.rows.push(ref); return ref; }

  /* line row: optional trailing-in-flow icon spacer + body. */
  function buildLineRow(parent, source, index) {
    var hasIcon = wantsIcon(index);
    var row = el('div', 'lrow lrow--line');
    var ref = { kind: 'line', index: index, rowEl: row, iconName: hasIcon ? source.icon : null, iconEl: null, markEl: null, spacer: null };
    if (hasIcon) { ref.spacer = el('span', 'spacer spacer-key'); row.appendChild(ref.spacer); }
    ref.bodyEl = textNode('div', 't-body', source.body);
    row.appendChild(ref.bodyEl);
    parent.appendChild(row);
    return pushRow(ref);
  }

  /* F04 entry: key + icon header row, body below; a flat index label extends from the spine. */
  function buildEntry(parent, source, index) {
    var hasIcon = wantsIcon(index);
    var entry = el('div', 'entry');
    var head = el('div', 'entry-head');
    var ref = { kind: 'entry', index: index, iconName: hasIcon ? source.icon : null, iconEl: null, markEl: null, spacer: null, entryEl: entry, headEl: head, tagEl: null, tickEl: null, railEl: null };
    ref.keyEl = textNode('span', 't-key', source.key);
    head.appendChild(ref.keyEl);
    if (hasIcon) { ref.spacer = el('span', 'spacer spacer-key'); head.appendChild(ref.spacer); }
    entry.appendChild(head);
    ref.bodyEl = textNode('div', 't-body', source.body);
    entry.appendChild(ref.bodyEl);
    parent.appendChild(entry);
    return pushRow(ref);
  }

  /* F06 ledger row: key/icon column + value; narrow stacks key above body. */
  function buildLedgerRow(parent, source, index) {
    var hasIcon = wantsIcon(index);
    var row = el('div', 'lrow lrow--key' + (narrow ? ' is-narrow' : ''));
    var ref = { kind: 'key', index: index, rowEl: row, iconName: hasIcon ? source.icon : null, iconEl: null, markEl: null, spacer: null };
    var kc = el('div', 'key-cell');
    if (hasIcon) { ref.spacer = el('span', 'spacer spacer-key'); kc.appendChild(ref.spacer); }
    ref.keyEl = textNode('span', 't-key', source.key);
    kc.appendChild(ref.keyEl);
    row.appendChild(kc);
    ref.bodyEl = textNode('div', 't-body', source.body);
    row.appendChild(ref.bodyEl);
    parent.appendChild(row);
    return pushRow(ref);
  }

  /* F07 output row: key + body, narrower key column. */
  function buildOutRow(parent, source, index) {
    if (!source.key) return buildLineRow(parent, source, index);
    var row = el('div', 'lrow lrow--outkey' + (narrow ? ' is-narrow' : ''));
    var ref = { kind: 'outkey', index: index, rowEl: row, iconName: null, iconEl: null, markEl: null, spacer: null };
    var kc = el('div', 'key-cell');
    ref.keyEl = textNode('span', 't-key', source.key);
    kc.appendChild(ref.keyEl);
    row.appendChild(kc);
    ref.bodyEl = textNode('div', 't-body', source.body);
    row.appendChild(ref.bodyEl);
    parent.appendChild(row);
    return pushRow(ref);
  }

  function figureWanted() { return features().figure && state.figure; }

  function addFigureSlot(content, kind, availableW) {
    var slot = el('div', 'fig-slot fig-slot--' + kind);
    slot.style.height = (Math.min(availableW, FIGURE_W) * FIGURE_H / FIGURE_W) + 'px';
    P.figSlots.push({ kind: kind, el: slot });
    content.appendChild(slot);
    return slot;
  }

  function buildContent() {
    var preset = state.preset;
    var content = el('div', 'content');
    layer4El.appendChild(content);
    P.content = content;

    if (preset === 'F02') {
      layer4El.className = 'layer layer4 layer4--flush';
      content.className = 'bands';
      buildF02(content);
      return;
    }
    if (preset === 'F07') {
      layer4El.className = 'layer layer4 layer4--flush';
      content.className = 'io-flow' + (shallow ? ' io-flow--side' : '');
      buildF07(content);
      return;
    }
    if (preset === 'F08') {
      layer4El.style.paddingRight = (pad + rearOffset()) + 'px';
      content.className = 'stack-content';
      buildF08(content);
      return;
    }
    if (preset === 'F06') { buildF06(content); return; }
    if (preset === 'F01') { content.className = 'content content--fill'; buildF01(content); return; }
    if (preset === 'F03') { content.className = 'content content--fill'; buildF03(content); return; }
    if (preset === 'F04') { content.className = 'content content--fill'; buildF04(content); return; }
    buildF05(content);
  }

  function buildF01(content) {
    P.title = addTitle(content, TITLE_MAIN, state.titleIcon);
    var list = el('div', 'rows rows--notes');
    content.appendChild(list);
    P.rowsList = list;
    for (var i = 0; i < state.count; i++) buildLineRow(list, ROWS[i], i);
    P.note = addNote(content, NOTE);
  }

  /* F02: no outer card; standalone header then independent full-width row bands. */
  function buildF02(content) {
    var head = el('div', 'band-box band-box--head');
    content.appendChild(head);
    P.headBox = head;
    P.title = addTitle(head, TITLE_MAIN, state.titleIcon);

    P.rowBoxes = [];
    for (var i = 0; i < state.count; i++) {
      var box = el('div', 'band-box band-box--row');
      content.appendChild(box);
      P.rowBoxes.push(box);
      buildLineRow(box, ROWS[i], i);
    }

    var foot = el('div', 'band-box band-box--foot');
    content.appendChild(foot);
    P.footBox = foot;
    P.note = addNote(foot, NOTE);
  }

  function buildF03(content) {
    if (figureWanted() && !shallow) addFigureSlot(content, 'glass', contentW);
    P.title = addTitle(content, TITLE_MAIN, state.titleIcon);
    var list = el('div', 'rows rows--glass');
    content.appendChild(list);
    P.rowsList = list;
    for (var i = 0; i < state.count; i++) buildLineRow(list, ROWS[i], i);
    P.note = addNote(content, NOTE);
  }

  function buildF04(content) {
    P.title = addTitle(content, TITLE_MAIN, state.titleIcon);
    var list = el('div', 'rows rows--archive' + (shallow ? ' rows--archive-cols' : ''));
    content.appendChild(list);
    P.rowsList = list;
    for (var i = 0; i < state.count; i++) buildEntry(list, ROWS[i], i);
    P.note = addNote(content, NOTE);
  }

  function buildF05(content) {
    P.title = addTitle(content, TITLE_MAIN, state.titleIcon);
    if (figureWanted() && !shallow) addFigureSlot(content, 'editorial', contentW);
    var paras = el('div', 'paragraphs');
    content.appendChild(paras);
    P.paras = paras;
    for (var i = 0; i < state.count; i++) {
      var p = el('div', 'para');
      var t = textNode('div', i === 0 ? 't-lead' : 't-body', ROWS[i].body);
      p.appendChild(t);
      paras.appendChild(p);
      pushRow({ kind: 'para', index: i, rowEl: p, bodyEl: t, iconEl: null, markEl: null, spacer: null, iconName: null });
    }
    P.note = addNote(content, NOTE);
  }

  function buildF06(content) {
    P.title = addTitle(content, TITLE_MAIN, state.titleIcon);
    var list = el('div', 'rows rows--ledger');
    content.appendChild(list);
    P.rowsList = list;
    for (var i = 0; i < state.count; i++) buildLedgerRow(list, ROWS[i], i);
    P.note = addNote(content, NOTE);
  }

  function buildF07(content) {
    var inBlock = el('div', 'io-block io-block--in');
    content.appendChild(inBlock);
    P.inZone = inBlock;
    var inRow = el('div', 'io-label-row');
    var inSpacer = null;
    if (state.inputIcon) { inSpacer = el('span', 'spacer spacer-end'); inRow.appendChild(inSpacer); }
    inRow.appendChild(textNode('div', 'io-label', INPUT_LABEL));
    inBlock.appendChild(inRow);
    P.inLabelRow = inRow;
    if (!INPUT_LABEL && !state.inputIcon) inRow.style.display = 'none';
    P.inputSpacer = inSpacer;
    P.inText = textNode('div', 'io-text t-body', INPUT_TEXT);
    inBlock.appendChild(P.inText);

    var gap = el('div', 'io-gap');
    content.appendChild(gap);
    P.gap = gap;
    if (!INPUT_TEXT && !INPUT_LABEL && !state.inputIcon) { inBlock.style.display = 'none'; gap.style.display = 'none'; }

    var outBlock = el('div', 'io-block io-block--out');
    content.appendChild(outBlock);
    P.outZone = outBlock;
    var outRow = el('div', 'io-label-row');
    var outSpacer = null;
    if (state.outputIcon) { outSpacer = el('span', 'spacer spacer-end'); outRow.appendChild(outSpacer); }
    outRow.appendChild(textNode('div', 'io-label', OUTPUT_LABEL));
    outBlock.appendChild(outRow);
    P.outLabelRow = outRow;
    if (!OUTPUT_LABEL && !state.outputIcon) outRow.style.display = 'none';
    P.outputSpacer = outSpacer;
    P.title = addTitle(outBlock, TITLE_IO, state.titleIcon);
    var list = el('div', 'rows rows--transform');
    outBlock.appendChild(list);
    P.rowsList = list;
    for (var i = 0; i < state.count; i++) buildOutRow(list, ROWS[i], i);
    P.note = addNote(outBlock, NOTE);
  }

  function buildF08(content) {
    P.title = addTitle(content, TITLE_MAIN, state.titleIcon);
    var list = el('div', 'rows rows--stack');
    content.appendChild(list);
    P.rowsList = list;
    for (var i = 0; i < state.count; i++) buildLineRow(list, ROWS[i], i);
    if (figureWanted() && !shallow) addFigureSlot(content, 'stack', contentW);
    P.note = addNote(content, NOTE);
  }

  function addRule(left, top, width, height, cls) {
    var rule = el('div', 'rule' + (cls ? ' ' + cls : ''));
    rule.setAttribute('data-layer', '2');
    rule.setAttribute('aria-hidden', 'true');
    rule.style.left = left + 'px';
    rule.style.top = top + 'px';
    rule.style.width = width + 'px';
    rule.style.height = height + 'px';
    decoEl.appendChild(rule);
    return rule;
  }

  function addRect(left, top, width, height, cls) {
    var r = el('div', cls);
    r.setAttribute('data-layer', '2');
    r.setAttribute('aria-hidden', 'true');
    r.style.left = left + 'px';
    r.style.top = top + 'px';
    r.style.width = width + 'px';
    r.style.height = height + 'px';
    decoEl.appendChild(r);
    return r;
  }

  function placeIcon(spacer, assetName, className) {
    if (!spacer || !assetName) return null;
    var icon = el('div', className);
    icon.setAttribute('data-layer', '2');
    icon.setAttribute('aria-hidden', 'true');
    var pos = offsetInCard(spacer, cardEl);
    icon.style.left = pos.x + 'px';
    icon.style.top = pos.y + 'px';
    var url = 'url("data:image/svg+xml,' + encodeURIComponent(svgSources.get(assetName)) + '")';
    icon.style.webkitMaskImage = url;
    icon.style.maskImage = url;
    decoEl.appendChild(icon);
    return icon;
  }

  function rectOf(node) {
    var p = offsetInCard(node, cardEl);
    return { x: p.x, y: p.y, width: node.offsetWidth, height: node.offsetHeight };
  }

  function slotNode(name, kind, node) {
    if (!node || !node.offsetWidth || !node.offsetHeight) return;
    var p = offsetInCard(node, cardEl);
    slots.push({ name: name, kind: kind, x: round2(p.x), y: round2(p.y), width: round2(node.offsetWidth), height: round2(node.offsetHeight) });
    if (kind === 'title' || kind === 'text' || kind === 'key' || kind === 'note') overflowNodes.push(node);
  }

  function slotRect(name, kind, x, y, w, h) {
    slots.push({ name: name, kind: kind, x: round2(x), y: round2(y), width: round2(w), height: round2(h) });
  }

  function placeTitleIcon() {
    if (P.title && P.title.spacer) {
      mark.titleIcon = placeIcon(P.title.spacer, TITLE_ICON, 'cardicon cardicon--title');
    }
  }

  function rowIcons() {
    for (var i = 0; i < P.rows.length; i++) {
      var r = P.rows[i];
      if (r.spacer && r.iconName) r.iconEl = placeIcon(r.spacer, r.iconName, 'cardicon');
      mark.rows.push({
        node: r.rowEl || r.entryEl || r.headEl, iconEl: r.iconEl, index: r.index,
        markEl: r.markEl || null, markAxis: r.markAxis || 'x',
        headEl: r.headEl || null, bodyEl: r.bodyEl || null, tagEl: r.tagEl || null, tickEl: r.tickEl || null
      });
    }
  }

  function measureAndPlace() {
    if (!cardEl || !decoEl) return;
    clearNode(decoEl);
    if (figLabelsEl) clearNode(figLabelsEl);
    slots = [];
    overflowNodes = [];
    mark.rows = [];
    mark.figures = [];
    mark.title = P.title ? P.title.block : null;
    mark.titleIcon = null;
    mark.footer = P.note || null;
    P.figRect = null;
    P.figSvg = null;

    var fn = placeByPreset[state.preset] || placeByPreset.F06;
    fn();

    if (P.kicker) slotNode('kicker', 'text', P.kicker);
    if (P.title) {
      slotNode('title', 'title', P.title.block);
      if (P.title.spacer) slotNode('title-icon', 'icon', P.title.spacer);
    }
    if (P.note) slotNode('note', 'note', P.note);
    if (P.inLabelRow) slotNode('input-label', 'text', P.inLabelRow.querySelector('.io-label'));
    if (P.outLabelRow) slotNode('output-label', 'text', P.outLabelRow.querySelector('.io-label'));
    for (var i = 0; i < P.rows.length; i++) {
      var r = P.rows[i];
      if (r.keyEl) slotNode('row' + (i + 1) + '-key', 'key', r.keyEl);
      if (r.bodyEl) slotNode('row' + (i + 1) + '-body', 'text', r.bodyEl);
      if (r.spacer) slotNode('row' + (i + 1) + '-icon', 'icon', r.spacer);
    }

    overflow = measureOverflow();

  }

  var placeByPreset = {
    F01: placeF01, F02: placeF02, F03: placeF03, F04: placeF04,
    F05: placeF05, F06: placeF06, F07: placeF07, F08: placeF08
  };

  function placeF01() {
    var bottom = offsetInCard(P.note, cardEl).y + P.note.offsetHeight + pad;
    addRect(0, 0, cardW, bottom, 'surface');
    slotRect('surface', 'surface', 0, 0, cardW, bottom);
    placeTitleIcon();
    /* A horizontal marker behind the first line of each body, width from the
       measured first line. It starts at the body edge, so it cannot collide
       with the optional leading icon. */
    for (var i = 0; i < P.rows.length; i++) {
      var r = P.rows[i];
      var pos = offsetInCard(r.bodyEl, cardEl);
      var w = firstLineWidth(r.bodyEl);
      r.markEl = addRect(pos.x, pos.y + 6, Math.max(28, w), 34, 'anno-mark');
      r.markAxis = 'x';
    }
    rowIcons();
  }

  function placeF02() {
    var hr = rectOf(P.headBox);
    P.headBand = addRect(hr.x, hr.y, hr.width, hr.height, 'band band--head');
    slotRect('band-head', 'band', hr.x, hr.y, hr.width, hr.height);
    P.rowBands = [];
    for (var i = 0; i < P.rowBoxes.length; i++) {
      var rr = rectOf(P.rowBoxes[i]);
      var b = addRect(rr.x, rr.y, rr.width, rr.height, 'band ' + (i % 2 ? 'band--b' : 'band--a'));
      P.rowBands.push(b);
      slotRect('band-row' + (i + 1), 'band', rr.x, rr.y, rr.width, rr.height);
    }
    placeTitleIcon();
    rowIcons();
  }

  function placeF03() {
    var fr = figureRect();
    var bottom = offsetInCard(P.note, cardEl).y + P.note.offsetHeight + pad;
    P.frostSurface = addRect(0, 0, cardW, bottom, 'surface surface--frost');
    slotRect('surface', 'surface', 0, 0, cardW, bottom);
    P.frostEdge = addRect(0, 0, cardW, 4, 'frost-edge');
    if (fr) paintFigure(fr);
    placeTitleIcon();
    rowIcons();
  }

  function placeF04() {
    var listR = rectOf(P.rowsList);
    var railH = 0;
    for (var i = 0; i < P.rows.length; i++) {
      var r = P.rows[i];
      var eR = rectOf(r.entryEl);
      var hR = rectOf(r.headEl);
      var spineX = eR.x + 6;
      if (i === 0) railH = eR.y;
      r.railEl = addRect(spineX, eR.y, 2, eR.height, 'spine-rail');
      r.tickEl = addRect(spineX, hR.y + hR.height / 2 - 1, 14, 2, 'tick');
      var keyEnd = hR.x + r.keyEl.offsetWidth + 10;
      r.tagEl = addRect(spineX, hR.y - 3, Math.max(20, keyEnd - spineX), hR.height + 6, 'index-label');
      r.markEl = r.tickEl;
      r.markAxis = 'x';
      slotRect('spine-' + (i + 1), 'rule', spineX, eR.y, 2, eR.height);
      slotRect('index-label-' + (i + 1), 'band', spineX, hR.y - 3, Math.max(20, keyEnd - spineX), hR.height + 6);
    }
    slotRect('spine-list', 'rule', listR.x + 6, listR.y, 2, listR.height);
    placeTitleIcon();
    rowIcons();
  }

  function placeF05() {
    var fr = figureRect();
    var parasR = rectOf(P.paras);
    var noteBottom = offsetInCard(P.note, cardEl).y + P.note.offsetHeight;
    var bottom = Math.max(noteBottom, parasR.y + parasR.height, fr ? fr.y + fr.h : 0) + pad;
    addRect(0, 0, cardW, bottom, 'surface');
    slotRect('surface', 'surface', 0, 0, cardW, bottom);
    if (fr) paintFigure(fr);
    placeTitleIcon();
    addRule(parasR.x, parasR.y + 4, 3, Math.max(12, parasR.height - 8), 'rule--accent');
    slotRect('edge', 'rule', parasR.x, parasR.y + 4, 3, Math.max(12, parasR.height - 8));
    rowIcons();
  }

  function placeF06() {
    var bottom = offsetInCard(P.note, cardEl).y + P.note.offsetHeight + pad;
    addRect(0, 0, cardW, bottom, 'surface');
    slotRect('surface', 'surface', 0, 0, cardW, bottom);
    for (var i = 0; i + 1 < P.rows.length; i++) {
      var rr = rectOf(P.rows[i].rowEl);
      addRect(pad, rr.y + rr.height, cardW - pad * 2, 2, 'ledger-dash');
    }
    addTeeth(pad, bottom, cardW - pad * 2);
    placeTitleIcon();
    rowIcons();
  }

  function placeF07() {
    var inR = rectOf(P.inZone);
    var outR = rectOf(P.outZone);
    P.inSurface = addRect(inR.x, inR.y, inR.width, inR.height, 'io-surface io-surface--in');
    slotRect('input-zone', 'surface', inR.x, inR.y, inR.width, inR.height);
    P.outSurface = addRect(outR.x, outR.y, outR.width, outR.height, 'io-surface io-surface--out');
    slotRect('output-zone', 'surface', outR.x, outR.y, outR.width, outR.height);

    if (shallow) {
      var cy = (inR.y + inR.height / 2 + outR.y + outR.height / 2) / 2;
      paintConnector(inR.x + inR.width + 8, cy, outR.x - 8, cy, true);
    } else {
      var cx = inR.x + Math.min(inR.width, 720) / 2;
      paintConnector(cx, inR.y + inR.height + 4, cx, outR.y - 4, false);
    }
    if (P.inputSpacer) { mark.inputIcon = placeIcon(P.inputSpacer, INPUT_ICON, 'cardicon'); slotNode('input-icon', 'icon', P.inputSpacer); }
    if (P.outputSpacer) { mark.outputIcon = placeIcon(P.outputSpacer, OUTPUT_ICON, 'cardicon'); slotNode('output-icon', 'icon', P.outputSpacer); }
    placeTitleIcon();
    slotNode('input-text', 'text', P.inText);
    rowIcons();
  }

  function placeF08() {
    var fr = figureRect();
    var noteBottom = offsetInCard(P.note, cardEl).y + P.note.offsetHeight;
    var stackBottom = Math.max(noteBottom, fr ? fr.y + fr.h : 0);
    var contentH = stackBottom + pad;
    var off = rearOffset();
    var sheetW = cardW - off;
    var back2 = off, back1 = off / 2;
    var e2 = addRect(back2, back2, sheetW, contentH, 'sheet sheet--back');
    var e1 = addRect(back1, back1, sheetW, contentH, 'sheet sheet--back');
    addRect(0, 0, sheetW, contentH, 'sheet sheet--front');
    P.sheets = [{ el: e1, off: back1 }, { el: e2, off: back2 }];
    slotRect('back-sheet-2', 'surface', back2, back2, sheetW, contentH);
    slotRect('back-sheet-1', 'surface', back1, back1, sheetW, contentH);
    slotRect('front-sheet', 'surface', 0, 0, sheetW, contentH);
    if (fr) paintFigure(fr);
    placeTitleIcon();
    rowIcons();
  }

  function addTeeth(left, top, width) {
    var teeth = Math.max(6, Math.round(width / 24));
    var step = width / teeth;
    var d = 'M0 0';
    for (var i = 0; i < teeth; i++) {
      d += ' L' + round2(i * step + step / 2) + ' 12 L' + round2((i + 1) * step) + ' 0';
    }
    d += ' Z';
    var svg = svgEl('svg', {
      viewBox: '0 0 ' + width + ' 12', preserveAspectRatio: 'none',
      'aria-hidden': 'true', focusable: 'false', 'class': 'teeth-svg', 'data-layer': '2'
    });
    svg.appendChild(svgEl('path', { d: d, 'class': 'teeth-path' }));
    svg.style.left = left + 'px';
    svg.style.top = top + 'px';
    svg.style.width = width + 'px';
    svg.style.height = '12px';
    decoEl.appendChild(svg);
    slotRect('teeth', 'teeth', left, top, width, 12);
  }

  function paintConnector(x1, y1, x2, y2, horizontal) {
    var w, h;
    if (horizontal) { w = Math.max(1, x2 - x1); h = 20; } else { w = 20; h = Math.max(1, y2 - y1); }
    var svg = svgEl('svg', { viewBox: '0 0 ' + w + ' ' + h, 'aria-hidden': 'true', focusable: 'false', 'class': 'connector-svg', 'data-layer': '2' });
    var tip = 10;
    if (horizontal) {
      svg.appendChild(svgEl('line', { x1: 0, y1: h / 2, x2: w - tip, y2: h / 2, 'class': 'connector-line' }));
      svg.appendChild(svgEl('path', { d: 'M' + (w - tip) + ' ' + (h / 2 - 6) + ' L' + w + ' ' + (h / 2) + ' L' + (w - tip) + ' ' + (h / 2 + 6), 'class': 'connector-line' }));
    } else {
      svg.appendChild(svgEl('line', { x1: w / 2, y1: 0, x2: w / 2, y2: h - tip, 'class': 'connector-line' }));
      svg.appendChild(svgEl('path', { d: 'M' + (w / 2 - 6) + ' ' + (h - tip) + ' L' + (w / 2) + ' ' + h + ' L' + (w / 2 + 6) + ' ' + (h - tip), 'class': 'connector-line' }));
    }
    svg.style.left = (horizontal ? x1 : x1 - w / 2) + 'px';
    svg.style.top = (horizontal ? y1 - h / 2 : y1) + 'px';
    svg.style.width = w + 'px';
    svg.style.height = h + 'px';
    decoEl.appendChild(svg);
    mark.connector = svg;
    slotRect('connector', 'connector', x1, y1, w, h);
  }

  /* --------------------------------------------------- figure placement -- */

  /* Compute the figure rect without painting it, so a content-height surface
     can be sized first. Sets the shallow text column when the figure sits right. */
  function figureRect() {
    if (!figureWanted()) return null;
    if (shallow) {
      var sheetInset = state.preset === 'F08' ? rearOffset() : 0;
      layer4El.style.paddingRight = (pad + sheetInset + FIG_SHALLOW_W + 16) + 'px';
      return { x: cardW - sheetInset - pad - FIG_SHALLOW_W, y: pad, w: FIG_SHALLOW_W, h: FIG_SHALLOW_W * FIGURE_H / FIGURE_W };
    }
    if (!P.figSlots.length) return null;
    var sr = rectOf(P.figSlots[0].el);
    var w = Math.min(sr.width, FIGURE_W);
    return { x: sr.x + (sr.width - w) / 2, y: sr.y, w: w, h: w * FIGURE_H / FIGURE_W };
  }

  function paintFigure(r) {
    var x = r.x, y = r.y, w = r.w, h = r.h;
    if (!P.figRect) P.figRect = { x: x, y: y, right: x + w, bottom: y + h };
    else {
      P.figRect.x = Math.min(P.figRect.x, x);
      P.figRect.y = Math.min(P.figRect.y, y);
      P.figRect.right = Math.max(P.figRect.right, x + w);
      P.figRect.bottom = Math.max(P.figRect.bottom, y + h);
    }
    var svg = svgNodes.get(card.figure.svg).cloneNode(true);
    svg.setAttribute('class', 'figure-svg');
    svg.setAttribute('data-layer', '2');
    svg.style.left = x + 'px';
    svg.style.top = y + 'px';
    svg.style.width = w + 'px';
    svg.style.height = h + 'px';
    decoEl.appendChild(svg);
    P.figSvg = svg;
    slotRect('figure', 'figure', x, y, w, h);

    mark.figures.push({ node: figLabelsEl, svg: svg });
  }

  /* -------------------------------------------------------- overflow ---- */

  /* The usable edge inset is the layout's own padding, not always the region
     pad: F02 bands use 20px and F07 blocks use 24px inside a flush layer. */
  function edgeInset() {
    if (state.preset === 'F02') return 20;
    if (state.preset === 'F07') return 24;
    return pad;
  }

  function measureOverflow() {
    var over = false;
    var inset = edgeInset();
    var right = cardW - inset;
    var rearReserve = state.preset === 'F08' ? rearOffset() : 0;
    var textLimit = region.h - rearReserve;
    for (var i = 0; i < slots.length; i++) {
      var s = slots[i];
      if (s.kind === 'title' || s.kind === 'text' || s.kind === 'key' || s.kind === 'note' || s.kind === 'label') {
        if (s.x + s.width > right + 1) over = true;
        if (s.y + s.height + inset > textLimit + 1) over = true;
      } else if (s.kind === 'figure') {
        if (s.y + s.height > region.h - pad + 1) over = true;
      } else if (s.kind === 'surface' || s.kind === 'band') {
        if (s.y + s.height > region.h + 1) over = true;
        if (s.x + s.width > cardW + 1) over = true;
      } else if (s.kind === 'teeth') {
        if (s.y + s.height > region.h + 1) over = true;
      }
    }
    for (var j = 0; j < overflowNodes.length; j++) {
      var n = overflowNodes[j];
      if (n.clientWidth > 0 && n.scrollWidth > n.clientWidth + 1) over = true;
    }
    return over;
  }

  /* --------------------------------------------------------- applyTime --- */

  function reveal(node, iconEl, p, plain) {
    if (node) {
      node.style.opacity = p.toFixed(3);
      node.style.transform = (reduce || plain) ? 'none'
        : 'translate3d(0,' + ((1 - p) * 8).toFixed(2) + 'px,0)';
    }
    if (iconEl) {
      iconEl.style.opacity = p.toFixed(3);
      if (!/scale/.test(iconEl.style.transform || '')) {
        iconEl.style.transform = (reduce || plain) ? 'none'
          : 'translate3d(0,' + ((1 - p) * 8).toFixed(2) + 'px,0)';
      }
    }
  }

  function emphasizeIcon(iconEl, t, index, p, plain) {
    var start = emphasisTime ?? rowStartFor(index) + EMPHASIS_OFFSET;
    var e = emphasisTime !== null && index !== rowTimes.findLastIndex(at => at <= emphasisTime) ? 0 : clamp01((t - start) / EMPHASIS_LENGTH);
    var tri = e <= 0 || e >= 1 ? 0 : (e < 0.5 ? e * 2 : (1 - e) * 2);
    if (reduce) {
      iconEl.style.transform = 'none';
      iconEl.style.backgroundColor = mixColor(themeColors.muted, themeColors.muted, 0);
      return;
    }
    var base = 0.85 + 0.15 * p;
    var scale = base * (1 + 0.1 * tri);
    iconEl.style.transform = (plain ? '' : 'translate3d(0,' + ((1 - p) * 8).toFixed(2) + 'px,0) ') + 'scale(' + scale.toFixed(4) + ')';
    iconEl.style.backgroundColor = mixColor(themeColors.muted, themeColors.accent, tri);
  }

  function applyMarkSweep(r, t, plain) {
    var start = rowStartFor(r.index);
    var mp = easeOut(clamp01((t - start) / MARK_REVEAL));
    var revealed = 0;
    for (var k = 0; k < mark.rows.length; k++) {
      if (t >= rowStartFor(mark.rows[k].index)) revealed++;
    }
    var age = Math.max(0, revealed - 1 - r.index);
    var base = Math.max(0.10, 0.24 - 0.045 * age);
    r.markEl.style.opacity = (mp * base).toFixed(3);
    r.markEl.style.transform = reduce ? 'none' : 'scaleX(' + mp.toFixed(3) + ')';
    r.markEl.style.transformOrigin = '0 50%';
  }

  function revealFooter(t, plain) {
    var fp = itemP(t, P && P.rows ? P.rows.length : 0);
    reveal(mark.footer, null, fp, plain);
  }

  function applyTime(seconds) {
    var t = Number(seconds);
    if (!isFinite(t)) throw new Error('invalid_card_time');
    if (t > DURATION) t = DURATION;

    var cardIn = easeOut(clamp01(t / CARD_REVEAL));
    var cardOut = EXIT_LENGTH === 0 ? Number(t >= EXIT_START) : easeOut(clamp01((t - EXIT_START) / EXIT_LENGTH));
    if (cardEl) {
      cardEl.style.opacity = (cardIn * (1 - cardOut)).toFixed(3);
      cardEl.style.transform = reduce ? 'none'
        : 'translate3d(0,' + ((1 - cardIn) * 12 + cardOut * -8).toFixed(2) + 'px,0)';
      cardEl.style.clipPath = '';
      cardEl.style.webkitClipPath = '';
    }

    var plain = state.preset === 'F01' || state.preset === 'F02' || state.preset === 'F05' || state.preset === 'F06';

    /* F02: standalone header band, sequential row bands, unframed footer. */
    if (state.preset === 'F02') {
      var hp = itemP(t, -1);
      reveal(mark.title, mark.titleIcon, hp, true);
      if (P && P.headBand) P.headBand.style.opacity = hp.toFixed(3);
    }

    /* F03: surface scale and the restrained top-edge light. */
    if (state.preset === 'F03') {
      if (P && P.frostSurface) {
        P.frostSurface.style.transformOrigin = '50% 50%';
        P.frostSurface.style.transform = reduce ? 'none' : 'scale(' + (0.97 + 0.03 * cardIn).toFixed(4) + ')';
      }
      if (P && P.frostEdge) {
        var rise = reduce ? 1 : easeOut(clamp01((t - 0.5) / 0.45));
        var tri = clamp01(1 - Math.abs(t - (EDGE_START + EDGE_END) / 2) / ((EDGE_END - EDGE_START) / 2));
        P.frostEdge.style.opacity = (rise * 0.3 + (reduce ? 0 : tri * 0.5)).toFixed(3);
      }
    }

    /* F07: input first, connector, then the output title and rows. */
    if (state.preset === 'F07' && P) {
      var inP = easeOut(clamp01((t - F07_IN_START) / F07_IN_LEN));
      P.inSurface.style.opacity = inP.toFixed(3);
      reveal(P.inLabelRow, null, inP, true);
      reveal(P.inText, null, inP, true);
      if (mark.inputIcon) reveal(mark.inputIcon, null, inP, true);
      var connP = easeOut(clamp01((t - F07_CONN_START) / F07_CONN_LEN));
      if (mark.connector) mark.connector.style.opacity = connP.toFixed(3);
      var tp = easeOut(clamp01((t - F07_TITLE_START) / TITLE_REVEAL));
      P.outSurface.style.opacity = tp.toFixed(3);
      reveal(P.outLabelRow, null, tp, true);
      reveal(mark.title, mark.titleIcon, tp, false);
      if (mark.outputIcon) reveal(mark.outputIcon, null, tp, false);
    } else {
      var tp2 = itemP(t, -1);
      reveal(mark.title, mark.titleIcon, tp2, plain);
      if (P && P.kicker) reveal(P.kicker, null, tp2, true);
    }

    /* generic rows */
    for (var i = 0; i < mark.rows.length; i++) {
      var r = mark.rows[i];
      var p = itemP(t, r.index);
      if (r.headEl) {
        reveal(r.headEl, null, p, true);
        r.headEl.style.transform = reduce ? 'none' : 'translateX(' + (-12 * (1-p)).toFixed(2) + 'px)';
        var bp = easeOut(clamp01((t - (rowStartFor(r.index) + 0.15)) / ROW_REVEAL));
        reveal(r.bodyEl, null, bp, true);
        if (r.iconEl) {
          r.iconEl.style.opacity = p.toFixed(3);
          r.iconEl.style.transform = r.headEl.style.transform;
        }
      } else if (state.preset === 'F06') {
        r.node.style.opacity = '1'; r.node.style.transform = 'none';
        reveal(r.bodyEl, r.iconEl, p, true);
      } else {
        reveal(r.node, r.iconEl, p, plain);
      }
      if (r.iconEl && state.preset !== 'F06' && !r.headEl) emphasizeIcon(r.iconEl, t, r.index, p, plain);
      if (r.markEl) applyMarkSweep(r, t, plain);
      if (r.tagEl) {
        r.tagEl.style.opacity = p.toFixed(3);
        r.tagEl.style.transform = (reduce || plain) ? 'none' : 'translateX(' + (-12 * (1 - p)).toFixed(2) + 'px)';
      }
      if (r.tickEl) {
        var tP = easeOut(clamp01((t - rowStartFor(r.index)) / MARK_REVEAL));
        r.tickEl.style.opacity = tP.toFixed(3);
        r.tickEl.style.transform = (reduce || plain) ? 'none' : 'scaleX(' + tP.toFixed(3) + ')';
        r.tickEl.style.transformOrigin = '0 50%';
      }
    }

    if (state.preset === 'F02' && P) {
      for (var b = 0; b < P.rowBands.length; b++) P.rowBands[b].style.opacity = itemP(t, b).toFixed(3);
    }

    /* figures: F05 gets a deterministic left-to-right reveal mask. */
    for (var f = 0; f < mark.figures.length; f++) {
      var fig = mark.figures[f];
      var fp = easeOut(clamp01((t - FIGURE_START) / FIGURE_REVEAL));
      fig.node.style.opacity = fp.toFixed(3);
      if (fig.svg) {
        fig.svg.style.opacity = fp.toFixed(3);
        if (state.preset === 'F05' && !reduce) {
          var mask = 'inset(0 ' + ((1 - fp) * 100).toFixed(2) + '% 0 0)';
          fig.svg.style.clipPath = mask;
          fig.svg.style.webkitClipPath = mask;
        } else {
          fig.svg.style.clipPath = 'none';
          fig.svg.style.webkitClipPath = 'none';
        }
        var emph = clamp01(1 - Math.abs(t - (FIG_EMPH_START + FIG_EMPH_END) / 2) / ((FIG_EMPH_END - FIG_EMPH_START) / 2));
        fig.svg.style.color = mixColor(themeColors.ink, themeColors.accent, emph);
      }
    }

    /* F08: rear sheets travel from overlapping to offset; the front stays still. */
    if (state.preset === 'F08' && P && P.sheets) {
      var sp = reduce ? 1 : easeOut(clamp01((t - F08_SHEET_START) / (F08_SHEET_END - F08_SHEET_START)));
      for (var s = 0; s < P.sheets.length; s++) {
        var sh = P.sheets[s];
        var d = -sh.off * (1 - sp);
        sh.el.style.transform = (reduce || Math.abs(d) < 0.01) ? 'none' : 'translate(' + d.toFixed(2) + 'px,' + d.toFixed(2) + 'px)';
      }
    }

    revealFooter(t, plain);


  }


  const area = card.area ?? 'full';
  const custom = typeof area === 'string' && /^([1-9]\d*)(?:px)?\s*[x×]\s*([1-9]\d*)(?:px)?$/.exec(area);
  region = typeof area === 'object' ? { x: area.x ?? 72, y: area.y ?? 72, w: area.width, h: area.height }
    : custom ? { x: 72, y: 72, w: Number(custom[1]), h: Number(custom[2]) } : REGIONS[ratio][area];
  if (!region || ![region.x, region.y, region.w, region.h].every(Number.isFinite) || region.x < 72 || region.y < 72 || region.w <= 0 || region.h <= 0 || region.x + region.w > CANVAS[ratio].width - 72 || region.y + region.h > CANVAS[ratio].height - 72) throw new Error('invalid_card_area');
  maxRows = computeMaxRows();
  if (state.count > maxRows) throw new Error('card_capacity_exceeded:' + maxRows);
  if (card.figure && !features().figure || card.lines.some(line => line.svg && !features().lineIcons)) throw new Error('unsupported_card_svg_slot');
  const allSlots = [card.title, ...card.lines.flatMap(line => [line, line.key, line.indexKey]), card.note, card.input, card.inputLabel, card.outputLabel, card.figure].filter(Boolean);
  for (const slot of allSlots) {
    timeOf(slot);
    if (slot !== card.figure && (typeof slot.text !== 'string' || !slot.text.trim())) throw new Error('invalid_card_text');
    if (!slot.svg) continue;
    if (svgSources.has(slot.svg)) {
      const expected = slot === card.figure ? '0 0 640 180' : '0 0 24 24';
      if (svgNodes.get(slot.svg).getAttribute('viewBox').trim().split(/[ ,]+/).join(' ') !== expected) throw new Error('invalid_card_svg_viewbox');
      continue;
    }
    if (typeof resolveSVG !== 'function') throw new Error('card_svg_resolver_required');
    const source = await resolveSVG(slot.svg);
    if (typeof source !== 'string' || /<!DOCTYPE|<!ENTITY/i.test(source)) throw new Error('unsafe_card_svg');
    const parsed = new DOMParser().parseFromString(source, 'image/svg+xml');
    const svg = parsed.documentElement;
    const tags = new Set(['svg', 'g', 'path', 'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'title', 'desc']);
    if (svg.localName !== 'svg' || svg.namespaceURI !== SVG_NS || parsed.querySelector('parsererror')) throw new Error('invalid_card_svg');
    for (const node of [svg, ...svg.querySelectorAll('*')]) {
      if (!tags.has(node.localName) || node.namespaceURI !== SVG_NS) throw new Error('unsafe_card_svg');
      for (const attr of node.attributes) {
        if (/^on/i.test(attr.name) || ['href', 'src', 'style', 'id'].includes(attr.localName) || /url\s*\(|javascript:|https?:/i.test(attr.value) && attr.name !== 'xmlns') throw new Error('unsafe_card_svg');
      }
    }
    const viewBox = svg.getAttribute('viewBox')?.trim().split(/[ ,]+/).map(Number);
    const expected = slot === card.figure ? [0, 0, 640, 180] : [0, 0, 24, 24];
    if (!viewBox || viewBox.length !== 4 || viewBox.some((v, i) => v !== expected[i])) throw new Error('invalid_card_svg_viewbox');
    if (slot.svg.startsWith('custom:')) {
      const shapes = svg.querySelectorAll('path,rect,circle,ellipse,line,polyline,polygon');
      if (slot === card.figure) {
        const nodes = svg.querySelectorAll('rect,circle,ellipse,polygon').length;
        const links = svg.querySelectorAll('path,line,polyline').length;
        if (nodes > 6 || links > 6 || shapes.length > 12) throw new Error('card_svg_complexity_exceeded');
        // Compound/closed paths cannot be certified as one relation link.
        for (const path of svg.querySelectorAll('path')) if (/[zZ]/.test(path.getAttribute('d') || '') || ((path.getAttribute('d') || '').match(/[mM]/g) || []).length !== 1) throw new Error('card_svg_ambiguous_figure_path');
      } else if (shapes.length > 8) throw new Error('card_svg_complexity_exceeded');
    }
    svg.setAttribute('aria-hidden', 'true');
    svgSources.set(slot.svg, new XMLSerializer().serializeToString(svg));
    svgNodes.set(slot.svg, doc.importNode(svg, true));
  }
  const DURATION = end - start;
  TITLE_START = timeOf(card.title);
  FIGURE_START = timeOf(card.figure);
  EXIT_START = card.exit ? localTime(card.exit) : Math.max(0, DURATION - EXIT_LENGTH);
  EXIT_LENGTH = Math.min(EXIT_LENGTH, DURATION - EXIT_START);
  F07_IN_START = Math.min(timeOf(card.input, TITLE_START), timeOf(card.inputLabel, TITLE_START));
  F07_CONN_START = F07_IN_START + F07_IN_LEN;
  F07_TITLE_START = TITLE_START;
  let emphasisTime = card.emphasis ? localTime(card.emphasis) : null;
  FIG_EMPH_START = emphasisTime ?? Math.max(FIGURE_START + FIGURE_REVEAL, (rowTimes.at(-1) ?? TITLE_START) + EMPHASIS_OFFSET);
  FIG_EMPH_END = FIG_EMPH_START + EMPHASIS_LENGTH;
  EDGE_START = FIG_EMPH_START; EDGE_END = FIG_EMPH_END;
  const items = [];
  const addItem = (id, slot, element) => {
    if (!slot || !element) return;
    element.dataset.cardId = card.id || '';
    element.dataset.cardRow = id;
    items.push({ id: card.id + ':' + id, cue: slot.cue, element });
  };
  const events = [];
  const rhythm = () => events;
  const api = {
    text: textRoot, decorations: stageRoot, items, rhythm,
    getState: () => ({ capacity: maxRows, overflow, region: { ...region }, slots: slots.map(slot => ({ ...slot })) }),
    retime(map, activeEnd = end) {
      if (typeof map !== 'function' || !Number.isFinite(activeEnd) || activeEnd < start) throw new Error('invalid_card_cue_mapper');
      resolveTime = map;
      rowTimes = card.lines.map(line => timeOf(line));
      TITLE_START = timeOf(card.title); FIGURE_START = timeOf(card.figure);
      EXIT_START = card.exit ? localTime(card.exit) : Math.max(0, activeEnd - start - .8);
      EXIT_LENGTH = Math.min(.8, activeEnd - start - EXIT_START);
      F07_IN_START = Math.min(timeOf(card.input, TITLE_START), timeOf(card.inputLabel, TITLE_START));
      F07_CONN_START = F07_IN_START + F07_IN_LEN; F07_TITLE_START = TITLE_START;
      emphasisTime = card.emphasis ? localTime(card.emphasis) : null;
      FIG_EMPH_START = emphasisTime ?? Math.max(FIGURE_START + FIGURE_REVEAL, (rowTimes.at(-1) ?? TITLE_START) + EMPHASIS_OFFSET);
      FIG_EMPH_END = FIG_EMPH_START + EMPHASIS_LENGTH;
      EDGE_START = FIG_EMPH_START; EDGE_END = FIG_EMPH_END;
    },
    renderAt(t) {
      if (!Number.isFinite(t)) throw new Error('invalid_card_time');
      if (disposed) return;
      const local = t - start;
      applyTime(local);
      if (EXIT_LENGTH === 0 && local >= EXIT_START) cardEl.style.opacity = '0';
      if (state.preset === 'F06' && !reduce) {
        // Print geometry advances at the spoken slots, not a fixed preview duration.
        const stops = [{ time: 0, edge: 0 }];
        for (const item of items) {
          const box = rectOf(item.element), at = localTime(item.cue);
          stops.push({ time: at, edge: box.y }, { time: at + ROW_REVEAL, edge: box.y + box.height });
        }
        stops.push({ time: Math.max(...items.map(item => localTime(item.cue))) + ROW_REVEAL, edge: Math.max(...slots.map(slot => slot.y + slot.height)) });
        stops.sort((a, b) => a.time - b.time);
        let edge = 0, previous = stops[0];
        for (const stop of stops) {
          stop.edge = Math.max(previous.edge, stop.edge);
          if (local < stop.time) { edge = previous.edge + (stop.edge - previous.edge) * clamp01((local - previous.time) / (stop.time - previous.time)); break; }
          edge = stop.edge; previous = stop;
        }
        cardEl.style.clipPath = cardEl.style.webkitClipPath = 'inset(0 0 ' + (100 * (1 - Math.min(1, edge / region.h))).toFixed(2) + '% 0)';
      }
      // Both physical layers share exactly the same card entrance, exit and print mask.
      for (const property of ['opacity', 'transform', 'clipPath', 'webkitClipPath']) decorCard.style[property] = cardEl.style[property];
      const decorationPulses = new Map();
      for (let i = 0; i < P.rows.length; i++) {
        const row = P.rows[i], slot = card.lines[i], key = slot.indexKey || slot.key;
        if (key) {
          const p = easeOut(clamp01((local - timeOf(key)) / ROW_REVEAL));
          reveal(row.keyEl, row.iconEl, p, true);
          if (row.headEl) {
            row.keyEl.style.opacity = '1';
            reveal(row.headEl, null, p, true);
            row.headEl.style.transform = reduce ? 'none' : 'translateX(' + (-12 * (1 - p)).toFixed(2) + 'px)';
            if (row.iconEl) row.iconEl.style.transform = row.headEl.style.transform;
            if (row.tagEl) { row.tagEl.style.opacity = p.toFixed(3); row.tagEl.style.transform = row.headEl.style.transform; }
            if (row.tickEl) { row.tickEl.style.opacity = p.toFixed(3); row.tickEl.style.transform = reduce ? 'none' : 'scaleX(' + p.toFixed(3) + ')'; }
          }
        }
        if (row.headEl) reveal(row.bodyEl, null, itemP(local, i), true);
        const eStart = emphasisTime === null ? rowTimes[i] + EMPHASIS_OFFSET : emphasisTime;
        const selected = emphasisTime === null || i === rowTimes.findLastIndex(at => at <= emphasisTime);
        const pulse = selected ? Math.max(0, 1 - Math.abs((local - eStart) / EMPHASIS_LENGTH * 2 - 1)) : 0;
        row.bodyEl.style.color = pulse > 0 ? 'color-mix(in srgb, var(--ink), var(--accent) ' + (pulse * 100).toFixed(2) + '%)' : 'var(--ink)';
        if (row.emphasisEl) decorationPulses.set(row.emphasisEl, Math.max(pulse, decorationPulses.get(row.emphasisEl) || 0));
      }
      for (const [element, pulse] of decorationPulses) element.style.filter = pulse > 0 ? 'brightness(' + (1 + pulse * .12).toFixed(3) + ')' : 'none';
      if (P.inText) reveal(P.inText, null, easeOut(clamp01((local - timeOf(card.input, F07_IN_START)) / ROW_REVEAL)), true);
      if (P.inLabelRow) reveal(P.inLabelRow, null, easeOut(clamp01((local - timeOf(card.inputLabel, F07_IN_START)) / ROW_REVEAL)), true);
      if (P.outLabelRow) reveal(P.outLabelRow, mark.outputIcon, easeOut(clamp01((local - timeOf(card.outputLabel, TITLE_START)) / ROW_REVEAL)), true);
      if (mark.inputIcon) reveal(mark.inputIcon, null, easeOut(clamp01((local - timeOf(card.input, F07_IN_START)) / ROW_REVEAL)), true);
    },
    dispose() { if (disposed) return; disposed = true; stageRoot.remove(); textRoot.remove(); global.__hfRhythmSources?.delete(rhythm); },
  };
  try {
    stage.appendChild(stageRoot); text.appendChild(textRoot);
    if (appearance) for (const root of [stageRoot, textRoot]) { global.HarnessAppearance.apply(root, appearance); root.style.backgroundColor = 'transparent'; }
    for (const [ref, svg] of svgNodes) if (ref.startsWith('custom:')) {
      const probe = svg.cloneNode(true), figure = ref === card.figure?.svg;
      const size = figure ? [640, 180] : [24, 24], inset = figure ? 16 : 2;
      probe.setAttribute('width', size[0]); probe.setAttribute('height', size[1]);
      probe.style.visibility = 'hidden'; stageRoot.appendChild(probe);
      try {
        const box = probe.getBBox();
        if ((!box.width && !box.height) || box.x < inset || box.y < inset || box.x + box.width > size[0] - inset || box.y + box.height > size[1] - inset) throw new Error('card_svg_safe_edge_violation');
        for (const shape of probe.querySelectorAll('path,rect,circle,ellipse,line,polyline,polygon')) {
          const style = global.getComputedStyle(shape);
          if (style.stroke !== 'none' && parseFloat(style.strokeWidth) < (figure ? 3 : 1.5)) throw new Error('card_svg_stroke_too_thin');
        }
      } finally { probe.remove(); }
    }
    buildCard();
    if (doc.fonts?.ready) await doc.fonts.ready;
    measureAndPlace();
    if (!cardEl.offsetWidth || overflow) throw new Error('card_content_overflow:' + card.id);
    const probe = el('span'); textRoot.appendChild(probe);
    for (const token of ['muted', 'accent', 'ink']) { probe.style.color = 'var(--' + token + ')'; themeColors[token] = parseColor(global.getComputedStyle(probe).color); }
    probe.remove();
    addItem('title', card.title, P.title.block);
    P.rows.forEach((row, i) => { addItem(String(i + 1), card.lines[i], row.bodyEl); addItem((i + 1) + (card.lines[i].indexKey ? ':indexKey' : ':key'), card.lines[i].indexKey || card.lines[i].key, row.keyEl); });
    addItem('note', card.note, P.note);
    addItem('input', card.input, P.inText); addItem('inputLabel', card.inputLabel, P.inLabelRow); addItem('outputLabel', card.outputLabel, P.outLabelRow);
    const originalTime = cue => typeof cue === 'number' ? cue : cues.find(cue);
    for (const item of items) events.push({ time: originalTime(item.cue), duration: ROW_REVEAL, kind: 'card_reveal', target: item.element });
    events.push({ time: start, duration: CARD_REVEAL, kind: 'card_enter', target: decorCard }, { time: card.exit ? originalTime(card.exit) : end - EXIT_LENGTH, duration: EXIT_LENGTH, kind: 'card_exit', target: cardEl });
    P.rows.forEach((row, i) => {
      row.emphasisEl = row.iconEl || row.markEl || P.rowBands[i] || P.frostEdge || decoEl.firstElementChild;
      if (emphasisTime === null || i === rowTimes.findLastIndex(at => at <= emphasisTime)) events.push({ time: card.emphasis ? originalTime(card.emphasis) : originalTime(card.lines[i].cue) + EMPHASIS_OFFSET, duration: EMPHASIS_LENGTH, kind: 'card_emphasis', target: row.emphasisEl });
    });
    if (P.figSvg) { P.figSvg.dataset.cardId = card.id || ''; P.figSvg.dataset.cardRow = 'figure'; events.push({ time: originalTime(card.figure.cue), duration: FIGURE_REVEAL, kind: 'card_figure', target: P.figSvg }); }
    (global.__hfRhythmSources ??= new Set()).add(rhythm);
    api.renderAt(start);
    return api;
  } catch (error) { api.dispose(); throw error; }
  }
  global.HarnessCardKit = { mount };
})(window);
