/*
 * Synthetic B-roll shot fixture: deterministic, time-pure and appearance-driven.
 *
 * The module owns only its own children inside the host stage/text roots. Every
 * state is a discrete function of the local (host-mapped) time, so forward,
 * direct seek and back-seek produce identical results. Colours and fonts come
 * exclusively from the frozen --appearance-* variables.
 */
const MANIFEST = new URL('./asset.json', import.meta.url);
const DEFAULT_DURATION = 3;

function build({ stage, text, slots, start }) {
  const doc = stage.ownerDocument;
  const nodes = [];
  const create = (parent, tag, style, content) => {
    const node = doc.createElement(tag);
    node.style.visibility = 'inherit';
    Object.assign(node.style, style);
    if (content !== undefined) node.textContent = content;
    parent.appendChild(node);
    nodes.push(node);
    return node;
  };
  const dispose = () => {
    for (const node of nodes) node.remove();
    nodes.length = 0;
  };

  try {
    const frame = create(stage, 'div', {
      position: 'absolute', left: '5%', top: '8%', width: '90%', bottom: '30%',
      display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', gap: '3%',
      fontFamily: 'var(--appearance-typography-body, system-ui)',
      color: 'var(--appearance-colors-text, currentColor)', pointerEvents: 'none',
    });
    frame.dataset.brollFrame = '';
    frame.dataset.hfSchematic = '';
    const track = create(frame, 'div', {
      position: 'relative', width: '100%', height: '10px',
      background: 'color-mix(in srgb, var(--appearance-colors-text, currentColor) 25%, transparent)',
      borderRadius: '5px',
    });
    const bar = create(track, 'div', {
      position: 'absolute', top: '0', bottom: '0', left: '0', width: '25%',
      background: 'var(--appearance-colors-accent, currentColor)', borderRadius: '5px',
      pointerEvents: 'auto',
    });
    const tiles = create(frame, 'div', { display: 'flex', width: '100%', height: '42%', gap: '3%' });
    const tile = opacity => create(tiles, 'div', {
      flex: '1 1 0', borderRadius: '4px', opacity,
      background: 'var(--appearance-colors-accent, currentColor)',
    });
    const tileA = tile('0.2');
    const tileB = tile('0.55');
    const tileC = tile('0.85');
    const highlight = create(frame, 'div', {
      position: 'absolute', left: '50%', top: '50%', width: '16%', paddingBottom: '16%',
      transform: 'translate(-50%, -50%)', borderRadius: '50%', opacity: '0',
      border: '3px solid var(--appearance-colors-accent, currentColor)',
      pointerEvents: 'auto',
    });
    const caption = create(text, 'div', {
      position: 'absolute', left: '5%', bottom: '20%', width: '90%',
      display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', gap: '4%',
      fontFamily: 'var(--appearance-typography-body, system-ui)',
    });
    caption.dataset.brollCaption = '';
    const label = (parent, content, color, opacity) => create(parent, 'span', {
      display: 'inline-block', whiteSpace: 'nowrap', fontWeight: '700', opacity,
      fontSize: '16px', color, pointerEvents: 'auto',
    }, content);
    const title = label(caption, String(slots.title), 'var(--appearance-colors-text, currentColor)', '1');
    const value = label(caption, String(slots.value), 'var(--appearance-colors-accent, currentColor)', '0');

    const renderAt = (localTime, globalTime) => {
      const time = Math.max(0, Math.min(DEFAULT_DURATION, Number(localTime) || 0));
      title.style.opacity = globalTime >= start ? '1' : '0';
      value.style.opacity = time >= 0.75 ? '1' : '0';
      bar.style.width = time >= 1.5 ? '66%' : '25%';
      tileB.style.opacity = time >= 1.5 ? '0.95' : '0.55';
      highlight.style.opacity = time >= 2.25 ? '1' : '0';
      tileC.style.opacity = time >= 2.25 ? '1' : '0.85';
      void tileA;
      void globalTime;
    };
    renderAt(0, start);

    return {
      renderAt,
      events: [
        { time: 0, target: title },
        { time: 0.75, target: value },
        { time: 1.5, target: bar },
        { time: 2.25, target: highlight },
      ],
      labels: { title, value },
      dispose,
    };
  } catch (error) {
    dispose();
    throw error;
  }
}

export async function mount(options) {
  const response = await fetch(MANIFEST, {redirect: 'error'});
  if (!response.ok) throw new Error('broll_sample_manifest');
  const metadata = await response.json();
  return globalThis.HarnessBroll.mount(metadata, options, build);
}
