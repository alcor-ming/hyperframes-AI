/** Deterministic, frame-independent rectangle placement in host CSS pixels. */
export const overlaps = (a, b, gap = 0) =>
  a.x < b.x + b.width + gap && a.x + a.width + gap > b.x &&
  a.y < b.y + b.height + gap && a.y + a.height + gap > b.y;

export function resolveLabels(items, width, height, obstacles = [], gap = 8) {
  const placed = [];
  const margin = Math.max(8, width * .018);
  for (const item of items) {
    if (item.width > width - margin * 2 || item.height > height - margin * 2) {
      throw Error('calm_light_label_capacity:' + item.id);
    }
    const normal = item.normal || [0, -1];
    const length = Math.hypot(...normal) || 1;
    const nx = normal[0] / length, ny = normal[1] / length;
    const tx = -ny, ty = nx;
    const step = Math.max(gap, item.height * .38);
    let selected;
    // The same full set is solved at every time, including unrevealed labels.
    // Labels never drift when new nodes appear, nor inherit previous positions.
    const candidates = [];
    for (let r = 0; r < 14; r++) {
      for (const tangent of [0, 1, -1, 2, -2, 3, -3]) {
        candidates.push([item.x + nx * r * step + tx * tangent * step,
          item.y + ny * r * step + ty * tangent * step]);
      }
    }
    // Bounded fallback searches both axes in fixed order, not random jitter.
    for (let r = 1; r <= 12; r++) {
      for (const [dx, dy] of [[0,-1],[0,1],[-1,0],[1,0],[-1,-1],[1,-1],[-1,1],[1,1]]) {
        candidates.push([item.x + dx * r * step, item.y + dy * r * step]);
      }
    }
    for (const [cx, cy] of candidates) {
      const rect = {id:item.id, x:Math.max(margin, Math.min(width - margin - item.width, cx - item.width / 2)),
        y:Math.max(margin, Math.min(height - margin - item.height, cy - item.height / 2)),
        width:item.width, height:item.height};
      if (!placed.some(other => overlaps(rect, other, gap)) &&
          !obstacles.some(other => overlaps(rect, other, gap * .45))) {
        selected = rect; break;
      }
    }
    if (!selected) throw Error('calm_light_label_layout_cannot_fit:' + item.id);
    placed.push(selected);
  }
  return placed;
}
