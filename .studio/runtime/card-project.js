/* Generated Plan data is the only card content source. The host owns the clock. */
(function (global) {
  'use strict';
  const data = document.querySelector('script[data-hf-card-plan]');
  if (!data || data.dataset.mounted) return;
  data.dataset.mounted = 'true';
  const plan = JSON.parse(data.textContent);
  const groups = new Map();
  const ready = (async () => {
    const appearance = await HarnessAppearance.load(new URL(plan.projectBase, document.baseURI));
    const cues = HarnessCues.from(plan.cues);
    try {
      for (const scene of plan.scenes) {
        const parent = scene.inline ? document.querySelector(`[data-scene-id="${scene.id}"],#${scene.id}`)
          : document.querySelector('[data-composition-id]');
        if (!parent) throw new Error(`Missing card Scene host: ${scene.id}`);
        const roots = {};
        for (const [layer, z] of [['stage', 2], ['text', 4]]) {
          const host = document.createElement('div');
          host.dataset.hfLayer = layer;
          host.dataset.cardScene = scene.id;
          Object.assign(host.style, {position: 'absolute', inset: '0', zIndex: String(z), pointerEvents: 'none'});
          parent.append(host);
          roots[layer] = host;
        }
        const instances = [];
        const group = {scene, roots, instances, ranges: [], appearance, cues, binding: null,
          documentStart: scene.inline ? 0 : scene.start};
        groups.set(scene.id, group);
        const activeTime = t => t - group.ranges.reduce((sum, range) =>
          sum + Math.max(0, Math.min(t, range.to) - range.from), 0);
        for (const card of scene.cards) {
          const instance = await HarnessCardKit.mount({
            stage: roots.stage, text: roots.text, card, ratio: plan.ratio,
            cues, appearance, start: scene.start, end: scene.start + scene.duration,
            cueTime: cue => activeTime(cues.find(cue)),
            resolveSVG: ref => {
              if (!Object.hasOwn(plan.svg, ref)) throw new Error('Card SVG outside generated closure');
              return plan.svg[ref];
            },
          });
          instances.push(instance);
        }
        group.renderAt = async t => {
          for (const instance of instances) await instance.renderAt(t);
        };
        group.a = {text: roots.text, decorations: roots.stage,
          items: instances.flatMap(instance => instance.items),
          renderAt: t => group.renderAt(scene.start + t)};
        group.binding = HarnessScene.bindScene({start: 0, duration: scene.start + scene.duration - group.documentStart,
          renderAt: async local => {
            const t = local + group.documentStart;
            const visible = t >= scene.start && t < scene.start + scene.duration;
            roots.stage.style.display = roots.text.style.display = visible ? '' : 'none';
            await group.renderAt(t);
          }});
        await group.renderAt(scene.start);
      }
      return groups;
    } catch (error) {
      for (const group of groups.values()) {
        group.binding?.dispose();
        group.instances.forEach(instance => instance.dispose());
        Object.values(group.roots).forEach(root => root.remove());
      }
      appearance.dispose();
      throw error;
    }
  })();
  let rolls, rollBinding;
  global.HarnessCardProject = {
    ready,
    async scene(id) {
      await ready;
      if (!groups.has(id)) throw new Error(`Unknown generated card Scene: ${id}`);
      return groups.get(id).a;
    },
    async setRolls(scenes, {reducedMotion} = {}) {
      await ready;
      if (rolls) throw new Error('Card rolls are already bound');
      // A/B metadata belongs to the host; card content stays exclusively in Plan.
      const entries = scenes.map(scene => {
        const group = groups.get(scene.id);
        if (!group) throw new Error(`Unknown generated card Scene: ${scene.id}`);
        group.ranges = (scene.b || []).map(range => ({from: group.cues.find(range.startCue), to: group.cues.find(range.endCue)}));
        const activeTime = t => t - group.ranges.reduce((sum, range) =>
          sum + Math.max(0, Math.min(t, range.to) - range.from), 0);
        for (const instance of group.instances)
          instance.retime(cue => activeTime(group.cues.find(cue)), activeTime(group.scene.start + group.scene.duration));
        return {...scene, a: group.a};
      });
      rolls = HarnessRolls.mount({cues: [...groups.values()][0].cues, scenes: entries, reducedMotion});
      for (const scene of scenes) {
        const group = groups.get(scene.id);
        group.binding.dispose();
        group.roots.stage.style.display = group.roots.text.style.display = '';
      }
      const end = Math.max(...entries.map(scene => [...groups.values()][0].cues.find(scene.endCue)));
      const offset = [...groups.values()][0].documentStart;
      rollBinding = HarnessScene.bindScene({start: 0, duration: end - offset, renderAt: t => rolls.renderAt(t + offset)});
      return rolls;
    },
    async renderAt(t) {
      await ready;
      if (rollBinding) await rollBinding.seek(t - [...groups.values()][0].documentStart);
      for (const group of groups.values()) await group.binding.seek(t - group.documentStart);
    },
    dispose() {
      rollBinding?.dispose();
      rolls?.dispose();
      for (const group of groups.values()) {
        group.binding.dispose();
        group.instances.forEach(instance => instance.dispose());
        Object.values(group.roots).forEach(root => root.remove());
      }
      groups.values().next().value?.appearance.dispose();
    },
  };
  global.__hfCardBuildReady = ready;
  ready.catch(error => {
    global.__hfCardBuildError = error.message;
    global.dispatchEvent(new ErrorEvent('error', {error, message: error.message}));
  });
})(window);
