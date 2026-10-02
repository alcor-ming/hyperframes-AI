import * as THREE from 'three';
import { MeshSurfaceSampler } from 'three/addons/math/MeshSurfaceSampler.js';

export function angleRange(extras = {}) {
  const raw = extras.lid_angle_range ?? extras.lidAngleRange;
  if (!Array.isArray(raw) || raw.length !== 2 || raw.some(v => !Number.isFinite(v))) return null;
  const unit = extras.lid_angle_units ?? extras.angle_units ?? extras.angle_unit ?? extras.units ?? 'radians';
  const values = /deg/i.test(unit) ? raw.map(THREE.MathUtils.degToRad) : [...raw];
  return { min: Math.min(...values), max: Math.max(...values), units: 'radians', source: raw };
}

export function materialRole(material, node) {
  return material.userData?.role ?? material.userData?.material_role ?? node?.userData?.role
    ?? material.name.replace(/^mat[_-]?/i, '').replace(/[._-]\d+$/, '').toLowerCase();
}

export function applyTheme(root, theme) {
  const changes = [];
  root.traverse(node => {
    if (!node.isMesh) return;
    const mats = Array.isArray(node.material) ? node.material : [node.material];
    for (const material of mats) {
      const role = materialRole(material, node);
      const preset = theme.roles[role];
      if (!preset) continue;
      if (preset.color && material.color) material.color.set(preset.color);
      if (Number.isFinite(preset.metalness) && 'metalness' in material) material.metalness = preset.metalness;
      if (Number.isFinite(preset.roughness) && 'roughness' in material) material.roughness = preset.roughness;
      if (preset.emissive && material.emissive) material.emissive.set(preset.emissive);
      material.needsUpdate = true;
      changes.push({ mesh: node.name, material: material.name, role, color: material.color?.getHexString() });
    }
  });
  return changes;
}

export function seededRandom(seed) {
  let state = seed >>> 0;
  return () => {
    state += 0x6D2B79F5;
    let t = state;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// One world-space triangle soup makes sample density proportional to transformed
// surface area even when the input icon uses several meshes or nonuniform scale.
export function sampleSurface(root, count = 2000, seed = 160) {
  root.updateMatrixWorld(true);
  const vertices = [];
  root.traverse(node => {
    if (!node.isMesh || node.userData?.fixtureGenerated || !node.visible) return;
    const geometry = node.geometry.index ? node.geometry.toNonIndexed() : node.geometry.clone();
    geometry.applyMatrix4(node.matrixWorld);
    for (const value of geometry.attributes.position.array) vertices.push(value);
    geometry.dispose();
  });
  if (vertices.length < 9) throw new Error('No triangle surfaces available for sampling');
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
  const mesh = new THREE.Mesh(geometry);
  const sampler = new MeshSurfaceSampler(mesh).setRandomGenerator(seededRandom(seed)).build();
  const position = new THREE.Vector3();
  const points = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) { sampler.sample(position); position.toArray(points, i * 3); }
  geometry.dispose();
  return points;
}

export function characterNodes(root) {
  const nodes = [];
  root.traverse(node => {
    if (node.userData?.character_index !== undefined || node.userData?.characterIndex !== undefined
        || /^(?:char|character|glyph)[_.-]?\d/i.test(node.name)) nodes.push(node);
  });
  return nodes.filter(node => !nodes.includes(node.parent));
}
