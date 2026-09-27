(function (global) {
  "use strict";
  function mount(host, cues, { ratio = "16:9", enabled = true } = {}) {
    if (!enabled) return { renderAt() {}, dispose() {} };
    if (!host || host.dataset.hfLayer !== "captions" || !["16:9", "9:16"].includes(ratio)) throw new Error("invalid_captions_host");
    const max = ratio === "9:16" ? 14 : 24, groups = [];
    let chars = [], next = Infinity;
    const timed = cues.data.characters.map(c => ({ ...c }));
    for (let i = timed.length - 1; i >= 0; i--) {
      if (timed[i].aligned) next = timed[i].start;
      timed[i].highlight = next;
    }
    function flush() {
      if (!chars.length) return;
      const aligned = chars.filter(c => c.aligned);
      if (aligned.length) groups.push({ chars, start: aligned[0].start, end: aligned.at(-1).end });
      chars = [];
    }
    for (const c of timed) {
      chars.push(c);
      if (chars.length >= max || /[。！？!?；;\n]/u.test(c.char)) flush();
    }
    flush();
    const line = document.createElement("div");
    Object.assign(line.style, { position: "absolute", left: "10%", right: "10%", bottom: "10%", textAlign: "center", fontFamily: "var(--appearance-typography-body, sans-serif)", fontSize: ratio === "9:16" ? "28px" : "32px", lineHeight: "1.4", color: "var(--appearance-colors-text, white)", background: "var(--appearance-surface-color, transparent)" });
    line.style.overflowWrap = "anywhere";
    host.append(line);
    for (const group of groups) {
      group.element = document.createElement("div");
      group.element.hidden = true;
      group.spans = group.chars.map(c => {
        const span = document.createElement("span"); span.textContent = c.char;
        group.element.append(span); return span;
      });
      line.append(group.element);
    }
    let disposed = false;
    return { groups, renderAt(t) {
      if (!Number.isFinite(t)) throw new Error("invalid_caption_time");
      if (disposed) return;
      for (const group of groups) {
        group.element.hidden = !(t >= group.start && t < group.end);
        for (let i = 0; i < group.chars.length; i++) {
          const highlighted = t >= group.chars[i].highlight, span = group.spans[i];
          span.dataset.highlighted = String(highlighted);
          span.style.color = highlighted ? "var(--appearance-colors-accent, currentColor)" : "";
        }
      }
    }, dispose() { disposed = true; line.remove(); } };
  }
  global.HarnessCaptions = { mount };
})(window);
