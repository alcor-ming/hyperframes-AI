export function create(el, params, { width, height, seed }) {
  const canvas = document.createElement('canvas');
  canvas.width = width; canvas.height = height; el.append(canvas);
  const ctx = canvas.getContext('2d');
  return { renderAt(t) {
    const mood = params.moods.filter(m => m.cue <= t).at(-1);
    ctx.fillStyle = mood?.tint || '#edf4f2'; ctx.fillRect(0, 0, width, height);
    ctx.fillStyle = '#167c74';
    ctx.fillRect(24 + Math.sin(t + seed) * 12, height * .45, width * .65, 4);
  }, dispose() { canvas.remove(); } };
}
