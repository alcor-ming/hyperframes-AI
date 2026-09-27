(function (global) {
  "use strict";
  function from(data) {
    if (data?.schema_version !== 1 || !Array.isArray(data.characters) || typeof data.text !== "string") throw new Error("invalid_cues");
    let previous = 0;
    for (const c of data.characters) {
      if (typeof c.char !== "string" || Array.from(c.char).length !== 1 || typeof c.aligned !== "boolean") throw new Error("invalid_cues");
      if (c.aligned) {
        if (!Number.isFinite(c.start) || !Number.isFinite(c.end) || c.start < previous || c.end < c.start) throw new Error("invalid_cues");
        previous = c.start;
      } else if (c.start !== null || c.end !== null) throw new Error("invalid_cues");
    }
    if (data.characters.map(c => c.char).join("") !== data.text) throw new Error("invalid_cues");
    if (data.speech_intervals !== undefined && (!Array.isArray(data.speech_intervals) || data.speech_intervals.some(interval => !Array.isArray(interval)
        || interval.length !== 2 || !interval.every(Number.isFinite) || interval[0] < 0 || interval[1] <= interval[0]))) throw new Error("invalid_cues");
    return { data, find(token, options = {}) {
      if (token && typeof token === "object") { options = token; token = options.token; }
      const { nth, within, edge = "start" } = options;
      if (Object.keys(options).some(key => !["token", "nth", "within", "edge"].includes(key)) || typeof token !== "string" || !token || !["start", "end"].includes(edge)
          || nth !== undefined && (!Number.isInteger(nth) || nth < 1)
          || within !== undefined && (!Array.isArray(within) || within.length !== 2 || !within.every(Number.isFinite) || within[0] < 0 || within[0] > within[1])) throw new Error("invalid_cue_query");
      const letters = Array.from(token), matches = [];
      for (let i = 0; i <= data.characters.length - letters.length; i++) {
        const chars = data.characters.slice(i, i + letters.length);
        if (!chars.every((c, j) => c.char === letters[j])) continue;
        const known = chars.filter(c => c.aligned);
        if (within && known.length && (known[0].start < within[0] || known.at(-1).end > within[1])) continue;
        matches.push(chars);
      }
      if (!matches.length || nth > matches.length) throw new Error("cue_not_found");
      if (nth === undefined && matches.length > 1) throw new Error("cue_ambiguous");
      const chars = matches[(nth ?? 1) - 1];
      if (!chars.every(c => c.aligned)) throw new Error("cue_unaligned");
      return edge === "start" ? chars[0].start : chars.at(-1).end;
    } };
  }
  async function load(url = "runtime/cues.json") {
    const target = new URL(url, location.href);
    if (target.origin !== location.origin) throw new Error("cues_require_local_url");
    const response = await fetch(target, { redirect: "error" });
    if (!response.ok) throw new Error("cues_not_found");
    return from(await response.json());
  }
  global.HarnessCues = { load, from };
})(window);
