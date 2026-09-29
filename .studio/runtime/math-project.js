/* Generated Plan owns content; the host owns the composition clock and A/B media. */
(function (global) {
  'use strict';
  const data = document.querySelector('script[data-hf-math-plan]');
  if (!data || data.dataset.mounted) return;
  data.dataset.mounted = 'true';
  const plan = JSON.parse(data.textContent), groups = new Map();
  const base = new URL(plan.projectBase, document.baseURI);
  let appearance, rolls, rollBinding;
  const activeTime = (group, t) => t - group.ranges.reduce((sum, range) =>
    sum + Math.max(0, Math.min(t, range.to) - range.from), 0);
  function dispose() {
    rollBinding?.dispose(); rolls?.dispose();
    for (const group of groups.values()) {
      group.binding?.dispose(); group.instance?.dispose();
      Object.values(group.roots).forEach(root => root.remove());
    }
    appearance?.dispose();
  }
  const ready = (async () => {
    try {
      appearance = await HarnessAppearance.load(base);
      const cues = HarnessCues.from(plan.cues);
      for (const scene of plan.scenes) {
        const parent = scene.inline ? document.querySelector(`[data-scene-id="${scene.id}"],#${scene.id}`)
          : document.querySelector('[data-composition-id]');
        if (!parent) throw new Error('Missing math Scene host: ' + scene.id);
        const roots = {};
        for (const [layer, z] of [['stage', 2], ['text', 4]]) {
          const host = document.createElement('div');
          host.dataset.hfLayer = layer; host.dataset.mathScene = scene.id; host.dataset.sceneId = scene.id;
          Object.assign(host.style, {position: 'absolute', inset: '0', zIndex: String(z), pointerEvents: 'none'});
          parent.append(host); roots[layer] = host;
        }
        const group = {scene, roots, cues, ranges: [], documentStart: scene.inline ? 0 : scene.start};
        groups.set(scene.id, group);
        const instance = await HarnessMathKit.mount({stage: roots.stage, text: roots.text,
          math: scene.math, intent: scene.intent, cues, ratio: plan.ratio,
          start: scene.start, end: scene.start + scene.duration, appearance,
          fontURL: new URL(scene.math.font.path, base)});
        group.instance = instance;
        group.renderAt = t => instance.renderAt(t);
        group.a = {text: roots.text, decorations: roots.stage, items: instance.items,
          renderAt: t => instance.renderAt(scene.start + t)};
        group.binding = HarnessScene.bindScene({start: 0, duration: scene.start + scene.duration - group.documentStart,
          renderAt: local => {
            const t = local + group.documentStart;
            roots.stage.style.display = roots.text.style.display = t >= scene.start && t < scene.start + scene.duration ? '' : 'none';
            instance.renderAt(t);
          }});
      }
      return groups;
    } catch (error) { dispose(); throw error; }
  })();
  global.HarnessMathProject = {
    ready,
    async scene(id) {
      await ready;
      if (!groups.has(id)) throw new Error('Unknown generated math Scene: ' + id);
      return groups.get(id).a;
    },
    async setRolls(scenes) {
      await ready;
      if (rolls) throw new Error('Math rolls are already bound');
      const entries = scenes.map(scene => {
        const group = groups.get(scene.id);
        if (!group) throw new Error('Unknown generated math Scene: ' + scene.id);
        group.ranges = (scene.b || []).map(range => ({from: group.cues.find(range.startCue), to: group.cues.find(range.endCue)}));
        group.instance.retime(cue => activeTime(group, group.cues.find(cue)), activeTime(group, group.scene.start + group.scene.duration));
        return {...scene, a: group.a};
      });
      const first = groups.values().next().value;
      rolls = HarnessRolls.mount({cues: first.cues, scenes: entries});
      for (const scene of scenes) {
        const group = groups.get(scene.id); group.binding.dispose();
        group.roots.stage.style.display = group.roots.text.style.display = '';
      }
      const end = Math.max(...entries.map(scene => first.cues.find(scene.endCue)));
      rollBinding = HarnessScene.bindScene({start: 0, duration: end - first.documentStart,
        renderAt: t => rolls.renderAt(t + first.documentStart)});
      return rolls;
    },
    async renderAt(t) {
      await ready;
      if (rollBinding) await rollBinding.seek(t - groups.values().next().value.documentStart);
      for (const group of groups.values()) await group.binding.seek(t - group.documentStart);
    },
    dispose,
  };
  global.__hfMathBuildReady = ready;
  ready.catch(error => {
    global.__hfMathBuildError = error.message;
    global.dispatchEvent(new ErrorEvent('error', {error, message: error.message}));
  });
})(window);
