import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import * as THREE from 'three';
import { angleRange, materialRole, applyTheme, sampleSurface, characterNodes, seededRandom } from '../core.mjs';
const themes = JSON.parse(await readFile(new URL('../themes.json', import.meta.url)));

test('Three exact r160 dependency', () => assert.equal(THREE.REVISION, '160'));
test('negative lid range sorts exported endpoints; degree conversion is explicit', () => {
  assert.deepEqual(angleRange({ lid_angle_range: [0, -2.268928] }), { min: -2.268928, max: 0, units: 'radians', source: [0, -2.268928] });
  assert.equal(angleRange({ lid_angle_range: [0, -130], units: 'degrees' }).min, THREE.MathUtils.degToRad(-130));
  assert.equal(angleRange({ lid_angle_range: [0, NaN] }), null);
});
test('material extras role takes priority over name and node role', () => {
  const m = new THREE.MeshStandardMaterial(); m.name = 'wrong_name'; m.userData.role = 'hf_surface';
  assert.equal(materialRole(m, { userData: { role: 'hf_muted' } }), 'hf_surface');
});
test('every theme recolors actual hf_* roles without renaming materials', () => {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(), new THREE.MeshStandardMaterial());
  mesh.material.name = 'hf_surface'; mesh.material.userData.role = 'hf_surface';
  const colors = Object.values(themes).map(theme => { const result = applyTheme(mesh, theme); assert.equal(result.length, 1); return mesh.material.color.getHexString(); });
  assert.equal(new Set(colors).size, 3); assert.equal(mesh.material.name, 'hf_surface');
});
test('seeded random repeats for equal seeds and varies across seeds', () => {
  const draw = seed => { const rng = seededRandom(seed); return Array.from({ length: 20 }, rng); };
  assert.deepEqual(draw(160), draw(160)); assert.notDeepEqual(draw(160), draw(161));
});
test('MeshSurfaceSampler produces exactly 2000 reproducible points', () => {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(1, 2, 3)); mesh.position.set(2, 3, 4); mesh.scale.set(1, 2, 1);
  const a = sampleSurface(mesh, 2000, 160), b = sampleSurface(mesh, 2000, 160), c = sampleSurface(mesh, 2000, 161);
  assert.equal(a.length, 6000); assert.deepEqual(a, b); assert.notDeepEqual(a, c);
  for (let i = 0; i < a.length; i += 3) { assert.ok(a[i] >= 1.5 && a[i] <= 2.5); assert.ok(a[i + 1] >= 1 && a[i + 1] <= 5); assert.ok(a[i + 2] >= 2.5 && a[i + 2] <= 5.5); }
});
test('character detection honors explicit index and named glyphs', () => {
  const root = new THREE.Group(), a = new THREE.Group(), b = new THREE.Group(), nested = new THREE.Group();
  a.userData.character_index = 0; b.name = 'glyph_1'; nested.name = 'char_2'; a.add(nested); root.add(a, b);
  assert.deepEqual(characterNodes(root), [a, b]);
});
test('absolute setTime survives backward seeks and clip end without accumulated update', () => {
  const object = new THREE.Object3D(); object.name = 'test';
  const clip = new THREE.AnimationClip('Move', 4, [new THREE.NumberKeyframeTrack('.position[x]', [0, 4], [0, 8])]);
  const mixer = new THREE.AnimationMixer(object), action = mixer.clipAction(clip);
  action.setLoop(THREE.LoopOnce, 1); action.clampWhenFinished = true;
  const seek = t => { action.reset().play(); mixer.setTime(t); return object.position.x; };
  assert.deepEqual([3, 0, 1, 3].map(seek), [6, 0, 2, 6]);
  assert.equal(seek(4), 8); assert.equal(seek(1), 2); assert.equal(seek(3), 6);
});
