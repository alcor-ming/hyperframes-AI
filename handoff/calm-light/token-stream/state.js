export const clamp = x => Math.max(0, Math.min(1, x));
export const smooth = x => { x = clamp(x); return x * x * (3 - 2 * x); };

// The final, labelled result lands at 5.9 rather than 5.8: its 1.1-second
// reading hold remains below two seconds when the 7-second shot stretches to 12.
export const moments = [0, 1, 2, 3, 3.6, 4.75, 5.9];
export const timing = Object.freeze({inflowStart: 1, inflowEnd: 3, actionStart: 3.6, actionEnd: 5.8, settled: 5.9});

export function tokenModel(params) {
  if (params.mode === 'overflow' && params.capacity_ratio <= 1) throw Error('overflow_requires_capacity_ratio_above_one');
  const count = params.token_count, capacity = Math.max(1, Math.floor(count / params.capacity_ratio));
  const initial = Math.min(count, capacity), extra = Math.max(0, count - capacity);
  // Serial identity is semantic. No seeded variation in tile size, order or
  // rotation: a tile always means exactly one illustrative cell.
  const tokens = Array.from({length: count}, (_,index) => ({index, size: 1,
    departure: timing.inflowStart + (index / Math.max(1, count - 1)) * 1.64,
    arrival: timing.inflowStart + .36 + (index / Math.max(1, count - 1)) * 1.64}));
  return {count, capacity, initial, extra, params: {...params}, tokens};
}

export function tokenState(model, time, reduced = false) {
  let t = Math.max(0, Math.min(7, time));
  if (reduced) t = moments.filter(moment => moment <= t).at(-1) ?? 0;
  const {capacity, count, initial, extra, params} = model;
  const action = clamp((t - timing.actionStart) / (timing.actionEnd - timing.actionStart));
  // Complete one FIFO movement before the next. At every integer step, every
  // retained token is exactly in cell serialIndex - shiftedCount.
  const rawShift = params.mode === 'overflow' ? (reduced ? Math.floor(action * extra + 1e-9) : action * extra) : 0;
  const wholeShift = Math.floor(rawShift + 1e-9);
  const shift = wholeShift + smooth(rawShift - wholeShift);
  const expelled = Math.min(extra, wholeShift);
  const arrived = model.tokens.filter(token => (reduced ? token.departure : token.arrival) <= t + 1e-9).length;
  const stored = Math.min(capacity, arrived);
  const generated = params.mode === 'generate' ? Math.min(8, Math.floor(action * 8 + 1e-9)) : 0;
  const waiting = Math.max(0, arrived - capacity - expelled);
  const inspected = params.mode === 'fill' ? Math.floor(action * capacity + 1e-9) : 0;
  const result = t >= timing.settled;
  return {t, arrived, stored, expelled, generated, waiting, shift, inspected, action,
    full: stored === capacity, fraction: stored / capacity, initial, extra,
    countVisible: true, outputVisible: params.mode === 'generate' && t >= timing.actionStart,
    settled: result, result, phase: t < 1 ? 'ready' : t < 3 ? 'inflow' : t < 3.6 ? 'pause' : t < 5.9 ? 'action' : 'result',
    tokens: model.tokens.map(token => {
      const i = token.index, progress = reduced ? +(t >= token.departure) : smooth((t - token.departure) / .36);
      const position = i - shift, inWindow = position >= 0 && position < capacity;
      // The oldest tile's departure uses exactly the same fractional FIFO
      // step as every retained tile. Counts and serial ranges advance only
      // once that tile has fully reached the removed region.
      const exitProgress = params.mode === 'overflow' && i < extra ? clamp(shift-i) : 0;
      return {index: i, progress, size: 1, started: t >= token.departure,
        arrived: t >= (reduced ? token.departure : token.arrival), cell: position, inWindow,
        queued: i >= capacity && position >= capacity,
        exiting: params.mode === 'overflow' && exitProgress > 0 && exitProgress < 1,
        departed: params.mode === 'overflow' && position <= -1,
        exitProgress,
        // Kept explicitly false: surplus input is never silently deleted.
        hidden: false};
    }),
    outputs: Array.from({length: 8}, (_,i) => ({index: i,
      progress: reduced ? +(i < generated) : smooth(action * 8 - i), started: params.mode === 'generate' && (reduced ? i < generated : action * 8 > i),
      complete: i < generated})),
    // Fixed-camera compatibility field, deliberately always zero.
    pull: 0};
}

export function tokenGrid(capacity, portrait = false) {
  const columns = portrait ? 6 : 10, rows = Math.ceil(capacity / columns);
  const bounds = portrait ? {left: .10, right: .90, top: .30, bottom: .68} : {left: .25, right: .75, top: .29, bottom: .72};
  const stepX = (bounds.right - bounds.left) / columns;
  const stepY = (bounds.bottom - bounds.top) / rows;
  const maximumWidth = stepX * .72;
  const aspect = portrait ? 1080 / (1920 * .84) : 1920 / (1080 * .84);
  const tileHeight = Math.min(stepY * .64, maximumWidth * aspect);
  const tileWidth = tileHeight / aspect;
  return {...bounds, columns, rows, stepX, stepY, tileWidth, tileHeight};
}

// A folded sequence avoids diagonal row-wrap jumps. Integer indices occupy
// distinct, coplanar cells; fractional indices move along the same FIFO path.
export function tokenCell(capacity, index, portrait = false) {
  const grid = tokenGrid(capacity, portrait);
  const at = i => {
    i = Math.max(0, Math.min(capacity - 1, i));
    const row = Math.floor(i / grid.columns), col = i % grid.columns;
    return [grid.left + ((row % 2 ? grid.columns - 1 - col : col) + .5) * grid.stepX,
      grid.top + (row + .5) * grid.stepY, 0];
  };
  const i = Math.max(0, Math.min(capacity - 1, index));
  const a = at(Math.floor(i)), b = at(Math.ceil(i)), f = i - Math.floor(i);
  return a.map((v, axis) => v + (b[axis] - v) * f);
}
