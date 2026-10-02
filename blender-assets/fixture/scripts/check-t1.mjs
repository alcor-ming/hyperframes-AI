import { readFile, mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { angleRange } from '../core.mjs';

const fixtureRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const targets = process.argv.slice(2).length ? process.argv.slice(2) : ['../T1-device-mockups/out/phone.glb', '../T1-device-mockups/out/laptop.glb'];
const reports = [];
const near = (a, b, e = 1e-5) => Math.abs(a - b) <= e;
for (const target of targets) {
  const filename = path.resolve(target), bytes = await readFile(filename);
  const report = { file: path.relative(fixtureRoot, filename), sha256: createHash('sha256').update(bytes).digest('hex'), threeRevision: THREE.REVISION, checks: [], measures: {} };
  const check = (name, pass, details) => { report.checks.push({ name, pass: Boolean(pass), ...(details !== undefined ? { details } : {}) }); };
  try {
    const gltf = await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '');
    const scene = gltf.scene; scene.updateMatrixWorld(true);
    const lid = scene.getObjectByName('lid'), kind = lid ? 'laptop' : 'phone', root = scene.getObjectByName(kind), screen = scene.getObjectByName('screen');
    check('three-exact-r160', THREE.REVISION === '160');
    check('named-device-root', Boolean(root)); check('standalone-screen-mesh', screen?.isMesh);
    check('root-meter-unit', root?.userData.unit === 'meter');
    check('root-identity-transform', root && near(root.position.length(), 0) && near(root.quaternion.angleTo(new THREE.Quaternion()), 0) && root.scale.distanceTo(new THREE.Vector3(1, 1, 1)) < 1e-6);
    if (!root || !screen?.isMesh) throw new Error('Required root/screen missing');
    const reference = lid ?? root;
    const inverse = reference.matrixWorld.clone().invert();
    const pos = screen.geometry.attributes.position, uv = screen.geometry.attributes.uv;
    check('screen-has-uv', Boolean(uv));
    const vertices = Array.from({ length: pos.count }, (_, i) => new THREE.Vector3().fromBufferAttribute(pos, i).applyMatrix4(screen.matrixWorld).applyMatrix4(inverse));
    const x = vertices.map(v => v.x), y = vertices.map(v => lid ? v.z : v.y);
    const xMin = Math.min(...x), xMax = Math.max(...x), yMin = Math.min(...y), yMax = Math.max(...y);
    const width = xMax - xMin, height = yMax - yMin, aspect = width / height;
    report.measures.screen = { width, height, aspect, exportedAspect: screen.userData.screen_aspect, expectedAspect: lid ? 1.6 : 9 / 19.5 };
    check('screen-aspect-metadata', near(screen.userData.screen_aspect, lid ? 1.6 : 9 / 19.5));
    check('screen-geometry-matches-aspect', near(aspect, screen.userData.screen_aspect, 1e-4));
    if (uv) {
      const failures = vertices.map((v, i) => ({ i, actual: [uv.getX(i), uv.getY(i)], expected: [(v.x - xMin) / width, 1 - ((lid ? v.z : v.y) - yMin) / height] }))
        .filter(v => !near(v.actual[0], v.expected[0]) || !near(v.actual[1], v.expected[1]));
      check('screen-uv-physical-top-left-v0', failures.length === 0, failures);
      const spans = [Math.min(...Array.from({ length: uv.count }, (_, i) => uv.getX(i))), Math.max(...Array.from({ length: uv.count }, (_, i) => uv.getX(i))), Math.min(...Array.from({ length: uv.count }, (_, i) => uv.getY(i))), Math.max(...Array.from({ length: uv.count }, (_, i) => uv.getY(i)))];
      check('screen-full-uv-0-1', spans.every((v, i) => near(v, i % 2)), spans);
    }
    const materialRoles = new Set(); let allRoles = true, meshCount = 0, triangles = 0, degenerates = 0;
    scene.traverse(node => {
      if (!node.isMesh) return;
      meshCount++;
      for (const material of [node.material].flat()) { const role = material.userData.role; if (!role) allRoles = false; else materialRoles.add(role); }
      const p = node.geometry.attributes.position, indices = node.geometry.index;
      const count = indices?.count ?? p.count; triangles += count / 3;
      for (let j = 0; j < count; j += 3) {
        const v = [0, 1, 2].map(k => new THREE.Vector3().fromBufferAttribute(p, indices ? indices.getX(j + k) : j + k));
        if (new THREE.Vector3().subVectors(v[1], v[0]).cross(new THREE.Vector3().subVectors(v[2], v[0])).lengthSq() < 1e-24) degenerates++;
      }
    });
    report.measures.meshes = { count: meshCount, triangles, degenerateTriangles: degenerates, materialRoles: [...materialRoles].sort() };
    check('all-materials-have-role-extras', allRoles); check('no-zero-area-triangles', degenerates === 0, degenerates);
    if (lid) {
      const range = angleRange(lid.userData); report.measures.lidRange = range;
      check('lid-direct-child-of-root', lid.parent === root);
      check('screen-descendant-of-lid', (() => { let n = screen; while (n) { if (n === lid) return true; n = n.parent; } return false; })());
      check('lid-at-hinge-origin', lid.position.length() < 1e-6);
      check('lid-range-extras-radians', range && near(range.min, THREE.MathUtils.degToRad(-130)) && near(range.max, 0));
      check('lid-default-105-degrees', near(lid.rotation.x, THREE.MathUtils.degToRad(-105), 1e-5));
      const original = lid.rotation.x;
      const angles = [0, -30, -60, -90, -105, -130]; const transforms = [];
      for (const degrees of angles) {
        lid.rotation.x = THREE.MathUtils.degToRad(degrees); scene.updateMatrixWorld(true);
        const hinge = lid.getWorldPosition(new THREE.Vector3());
        const far = new THREE.Vector3(0, 0, yMax).applyMatrix4(lid.matrixWorld);
        transforms.push({ degrees, hinge: hinge.toArray(), farEdgeY: far.y, farEdgeZ: far.z });
      }
      lid.rotation.x = original; scene.updateMatrixWorld(true);
      check('negative-angle-opens-up', transforms.slice(1).every(t => t.farEdgeY > 0), transforms);
      check('hinge-fixed-through-angle-range', transforms.every(t => t.hinge.every((v, i) => near(v, transforms[0].hinge[i]))));
    }
  } catch (error) { check('inspection-completed', false, String(error)); }
  report.pass = report.checks.every(c => c.pass); reports.push(report);
  console.log(`${report.pass ? 'PASS' : 'FAIL'} ${report.file}`);
  for (const c of report.checks.filter(c => !c.pass)) console.log(`  ${c.name}: ${JSON.stringify(c.details ?? null)}`);
}
await mkdir(path.join(fixtureRoot, 'reports'), { recursive: true });
await writeFile(path.join(fixtureRoot, 'reports', 't1-contract.json'), JSON.stringify(reports, null, 2) + '\n');
if (reports.some(r => !r.pass)) process.exitCode = 1;
