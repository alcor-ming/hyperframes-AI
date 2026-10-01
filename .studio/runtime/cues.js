(function (global) {
  "use strict";
  function validateBeatGrid(grid) {
    const keys = ["schema_version", "audio_sha256", "beats_per_bar", "first_downbeat", "times"];
    if (!grid || typeof grid !== "object" || Object.keys(grid).length !== keys.length || keys.some(k => !(k in grid))
        || grid.schema_version !== 1 || typeof grid.audio_sha256 !== "string" || !/^[a-fA-F0-9]{64}$/.test(grid.audio_sha256)
        || !Number.isSafeInteger(grid.beats_per_bar) || grid.beats_per_bar < 1
        || !Array.isArray(grid.times) || !grid.times.length || grid.times.some((t, i) => !Number.isFinite(t) || t < 0 || i > 0 && t <= grid.times[i - 1])
        || !Number.isSafeInteger(grid.first_downbeat) || grid.first_downbeat < 0 || grid.first_downbeat >= grid.times.length) throw new Error("invalid_beat_grid");
  }
  function from(data) {
    if (data?.schema_version !== 1 || !Array.isArray(data.characters) || typeof data.text !== "string") throw new Error("invalid_cues");
    if ("beat_grid" in data) validateBeatGrid(data.beat_grid);
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
      if ("bar" in options || "beat" in options) {
        if (token !== undefined || Object.keys(options).length !== 2 || !("bar" in options) || !("beat" in options)) throw new Error("invalid_beat_query");
        if (!("beat_grid" in data)) throw new Error("missing_beat_grid");
        const grid = data.beat_grid, { bar, beat } = options;
        validateBeatGrid(grid);
        if (!Number.isSafeInteger(bar) || bar < 1 || !Number.isSafeInteger(beat) || beat < 1 || beat > grid.beats_per_bar) throw new Error("invalid_beat_query");
        const index = grid.first_downbeat + (bar - 1) * grid.beats_per_bar + beat - 1;
        if (index >= grid.times.length) throw new Error("beat_not_found");
        return grid.times[index];
      }
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
    const target = new URL(url, document.baseURI);
    if (target.origin !== location.origin) throw new Error("cues_require_local_url");
    const response = await fetch(target, { redirect: "error" });
    if (!response.ok) throw new Error("cues_not_found");
    return from(await response.json());
  }
  global.HarnessCues = { load, from };
})(window);
