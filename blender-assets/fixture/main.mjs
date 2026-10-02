import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { angleRange, applyTheme, characterNodes, sampleSurface } from './core.mjs';

if (THREE.REVISION !== '160') throw new Error(`Expected Three r160, received ${THREE.REVISION}`);
const $ = id => document.getElementById(id);
const themes = await (await fetch('./themes.json')).json();
const renderer = new THREE.WebGLRenderer({ canvas: $('stage'), antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.NoToneMapping;
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(34, 1, 0.001, 1000);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = false;
controls.addEventListener('change', () => renderer.render(scene, camera));
scene.add(new THREE.HemisphereLight(0xffffff, 0x3b4f70, 2));
const key = new THREE.DirectionalLight(0xffffff, 2.4);
key.position.set(3, 4, 5); scene.add(key);
const fill = new THREE.DirectionalLight(0x84b9ff, 1.5);
fill.position.set(-3, 2, -4); scene.add(fill);
let asset = null, mixer = null, actions = [], activeClip = -1, time = 0;
let lid = null, lidRadians = null, range = null, screens = [], points = null;
let characters = [], originalMaterials = new Map(), themeChanges = [], source = null;
const issues = [];
const uvCanvas = document.createElement('canvas');
uvCanvas.width = 1024; uvCanvas.height = 1024;
const ctx = uvCanvas.getContext('2d');
const corners = [
  { label: '左上', english: 'TOP LEFT', rgb: [255, 64, 64], x: 0, y: 0 },
  { label: '右上', english: 'TOP RIGHT', rgb: [64, 220, 96], x: 512, y: 0 },
  { label: '左下', english: 'BOTTOM LEFT', rgb: [64, 128, 255], x: 0, y: 512 },
  { label: '右下', english: 'BOTTOM RIGHT', rgb: [255, 208, 64], x: 512, y: 512 },
];
for (const c of corners) {
  ctx.fillStyle = `rgb(${c.rgb.join(',')})`; ctx.fillRect(c.x, c.y, 512, 512);
  ctx.fillStyle = '#111827'; ctx.font = 'bold 84px "Noto Sans CJK SC", sans-serif';
  ctx.textAlign = 'center'; ctx.fillText(c.label, c.x + 256, c.y + 250);
  ctx.font = 'bold 27px sans-serif'; ctx.fillText(c.english, c.x + 256, c.y + 300);
}
ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 6; ctx.strokeRect(5, 5, 1014, 1014);
const cornerTexture = new THREE.CanvasTexture(uvCanvas);
cornerTexture.flipY = false; // glTF image origin is top-left; v=0 must remain the top.
cornerTexture.colorSpace = THREE.SRGBColorSpace;
cornerTexture.generateMipmaps = false;
cornerTexture.minFilter = THREE.LinearFilter;
const screenMaterial = new THREE.MeshBasicMaterial({ map: cornerTexture, toneMapped: false });
screenMaterial.name = 'fixture_screen_test'; screenMaterial.userData.role = 'screen';

for (const [value, theme] of Object.entries(themes)) $('theme').add(new Option(theme.label, value));
function applyCurrentTheme() {
  const theme = themes[$('theme').value]; scene.background = new THREE.Color(theme.background);
  themeChanges = asset ? applyTheme(asset, theme) : [];
  render(time); status();
}
function setScreenTest(enabled) {
  $('screen-test').checked = Boolean(enabled);
  for (const screen of screens) screen.material = enabled ? screenMaterial : originalMaterials.get(screen);
  render(time);
}
function isScreen(node) { return node.isMesh && (node.name === 'screen' || node.userData.role === 'screen' || node.userData.screen_aspect !== undefined); }
function clearAsset() {
  if (!asset) return;
  mixer?.stopAllAction(); mixer?.uncacheRoot(asset);
  if (points) { scene.remove(points); points.geometry.dispose(); points.material.dispose(); points = null; }
  scene.remove(asset);
  const materials = new Set(); const textures = new Set();
  asset.traverse(node => {
    if (!node.isMesh) return;
    node.geometry.dispose();
    for (const m of [originalMaterials.get(node) ?? node.material].flat()) {
      if (m === screenMaterial) continue;
      materials.add(m);
      for (const value of Object.values(m)) if (value?.isTexture) textures.add(value);
    }
  });
  for (const texture of textures) texture.dispose();
  for (const material of materials) material.dispose();
  originalMaterials.clear(); screens = []; characters = []; lid = null; range = null; actions = [];
}
async function loadArrayBuffer(data, name = 'local.glb') {
  const gltf = await new GLTFLoader().parseAsync(data, '');
  clearAsset();
  asset = gltf.scene; source = name; scene.add(asset);
  // Clone per mesh to prevent a node-role recolor from changing unrelated meshes.
  asset.traverse(node => {
    if (node.isMesh) node.material = Array.isArray(node.material) ? node.material.map(m => m.clone()) : node.material.clone();
    if (isScreen(node)) { screens.push(node); originalMaterials.set(node, node.material); }
    if (node.name === 'lid') lid = node;
  });
  range = lid ? angleRange(lid.userData) ?? angleRange(asset.userData) : null;
  lidRadians = lid?.rotation.x ?? null;
  $('lid-section').hidden = !lid;
  $('lid').disabled = !range;
  if (lid && range) {
    $('lid').min = range.min; $('lid').max = range.max; $('lid').value = lidRadians;
    $('lid-range').textContent = `[${range.min.toFixed(6)}, ${range.max.toFixed(6)}] rad from extras`;
  } else if (lid) $('lid-range').textContent = 'Missing lid_angle_range extras: slider disabled';
  $('clip').replaceChildren(new Option('None', '-1'));
  mixer = new THREE.AnimationMixer(asset);
  actions = gltf.animations.map((clip, i) => {
    $('clip').add(new Option(`${clip.name || `Clip ${i}`} (${clip.duration.toFixed(3)}s)`, i));
    const action = mixer.clipAction(clip); action.setLoop(THREE.LoopOnce, 1); action.clampWhenFinished = true;
    return action;
  });
  activeClip = actions.length ? 0 : -1; $('clip').value = String(activeClip);
  $('time').max = actions[activeClip]?.getClip().duration ?? 4;
  characters = characterNodes(asset); $('characters-section').hidden = !characters.length;
  $('characters').replaceChildren();
  for (const node of characters) {
    const label = document.createElement('label'); const checkbox = document.createElement('input');
    checkbox.type = 'checkbox'; checkbox.checked = true;
    checkbox.onchange = () => { node.visible = checkbox.checked; render(time); };
    label.append(checkbox, document.createTextNode(` ${node.name}`)); $('characters').append(label);
  }
  const iconAsset = /icon/i.test(name) || asset.getObjectByProperty('name', 'icon') || (() => { let found = false; asset.traverse(n => { if (n.userData.asset_type === 'icon' || n.userData.role === 'icon') found = true; }); return found; })();
  $('sampling-section').hidden = !iconAsset; $('sampling').checked = false;
  applyCurrentTheme(); setScreenTest($('screen-test').checked); render(0); frameAsset(); status();
  return info();
}
async function loadUrl(url) {
  const response = await fetch(url); if (!response.ok) throw new Error(`GLB request: ${response.status} ${url}`);
  return loadArrayBuffer(await response.arrayBuffer(), url);
}
function setLidRadians(value) {
  if (!lid || !range) throw new Error('No lid with valid angle range');
  if (!Number.isFinite(value) || value < range.min - 1e-6 || value > range.max + 1e-6) throw new Error('Lid angle outside exported range');
  lidRadians = value; $('lid').value = value; render(time); return lid.rotation.x;
}
function render(t = time) {
  if (!Number.isFinite(t) || t < 0) throw new Error('Time must be finite and nonnegative');
  time = t;
  // Re-arm the action before every absolute seek, including after reaching its end.
  // There is no elapsed-time accumulator and no requestAnimationFrame animation loop.
  if (mixer) {
    actions.forEach((action, index) => { if (index === activeClip) action.reset().play(); else action.stop(); });
    mixer.setTime(t);
  }
  if (lid && lidRadians !== null) lid.rotation.x = lidRadians;
  asset?.updateMatrixWorld(true);
  $('time').value = t; $('time-value').textContent = t.toFixed(3);
  $('lid-value').textContent = lidRadians === null ? '' : lidRadians.toFixed(4);
  renderer.render(scene, camera);
}
function frameAsset() {
  if (!asset) return;
  const box = new THREE.Box3().setFromObject(asset), size = box.getSize(new THREE.Vector3()), center = box.getCenter(new THREE.Vector3());
  const diameter = Math.max(size.x, size.y, size.z, .01);
  camera.position.copy(center).add(new THREE.Vector3(0.65, 0.4, 1.65).multiplyScalar(diameter));
  camera.near = diameter / 1000; camera.far = diameter * 100; camera.up.set(0, 1, 0); camera.updateProjectionMatrix();
  controls.target.copy(center); controls.update(); render(time);
}
function screenFrame() {
  const screen = screens[0]; if (!screen) throw new Error('No screen mesh');
  asset.updateMatrixWorld(true);
  const positions = screen.geometry.attributes.position;
  const worldPoints = Array.from({ length: positions.count }, (_, i) => new THREE.Vector3().fromBufferAttribute(positions, i).applyMatrix4(screen.matrixWorld));
  const center = new THREE.Box3().setFromPoints(worldPoints).getCenter(new THREE.Vector3());
  const x = new THREE.Vector3(1, 0, 0);
  let up = new THREE.Vector3(0, 1, 0);
  // Physical device orientation, deliberately independent of its UV coordinates.
  if (lid && screen.parent) { x.transformDirection(lid.matrixWorld); up.set(0, 0, 1).transformDirection(lid.matrixWorld); }
  else { const root = asset.getObjectByName('phone') ?? asset; x.transformDirection(root.matrixWorld); up.transformDirection(root.matrixWorld); }
  const normal = new THREE.Vector3().crossVectors(x, up).normalize();
  const xs = worldPoints.map(p => p.clone().sub(center).dot(x));
  const ys = worldPoints.map(p => p.clone().sub(center).dot(up));
  return { screen, center, x, up, normal, width: Math.max(...xs) - Math.min(...xs), height: Math.max(...ys) - Math.min(...ys) };
}
function screenView() {
  const frame = screenFrame();
  const distance = Math.max(frame.height, frame.width / camera.aspect) / (2 * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2))) * 1.2;
  camera.position.copy(frame.center).addScaledVector(frame.normal, distance); camera.up.copy(frame.up);
  controls.target.copy(frame.center); controls.update(); render(time); return screenProbeCoordinates();
}
function screenProbeCoordinates() {
  const { center, x, up, width, height } = screenFrame();
  return [ [-.36, .36], [.36, .36], [-.36, -.36], [.36, -.36] ].map(([sx, sy], i) => {
    const p = center.clone().addScaledVector(x, sx * width).addScaledVector(up, sy * height).project(camera);
    return { label: corners[i].label, rgb: corners[i].rgb, x: Math.round((p.x * .5 + .5) * renderer.domElement.width), y: Math.round((-p.y * .5 + .5) * renderer.domElement.height) };
  });
}
function setSampling(enabled, seed = Number($('seed').value)) {
  if (points) { scene.remove(points); points.geometry.dispose(); points.material.dispose(); points = null; }
  if (enabled && asset) {
    const array = sampleSurface(asset, 2000, seed);
    const geometry = new THREE.BufferGeometry(); geometry.setAttribute('position', new THREE.BufferAttribute(array, 3));
    const extent = new THREE.Box3().setFromObject(asset).getSize(new THREE.Vector3()).length();
    points = new THREE.Points(geometry, new THREE.PointsMaterial({ color: '#ffec91', size: extent * .006, depthTest: false, toneMapped: false }));
    points.userData.fixtureGenerated = true; scene.add(points);
  }
  $('sampling').checked = enabled; render(time); return points?.geometry.attributes.position.count ?? 0;
}
function pixelHash() {
  const gl = renderer.getContext(); const pixels = new Uint8Array(renderer.domElement.width * renderer.domElement.height * 4);
  gl.readPixels(0, 0, renderer.domElement.width, renderer.domElement.height, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
  let hash = 2166136261; for (const p of pixels) hash = Math.imul(hash ^ p, 16777619);
  return (hash >>> 0).toString(16).padStart(8, '0');
}
function testSeek({ t1 = .75, t3 = 2.75 } = {}) {
  const times = [t3, 0, t1, t3], hashes = times.map(t => { render(t); return pixelHash(); });
  const result = { times, hashes, exactRepeat: hashes[0] === hashes[3], animated: actions.length > 0, framesDiffer: new Set(hashes).size > 1 };
  status(result); return result;
}
function info() {
  let meshCount = 0, triangles = 0; asset?.traverse(n => { if (n.isMesh) { meshCount++; triangles += (n.geometry.index?.count ?? n.geometry.attributes.position.count) / 3; } });
  return { threeRevision: THREE.REVISION, source, meshCount, triangles, screenCount: screens.length, screenAspects: screens.map(n => n.userData.screen_aspect), lid: lid ? { radians: lid.rotation.x, range, position: lid.position.toArray() } : null, clips: actions.map(a => ({ name: a.getClip().name, duration: a.getClip().duration })), characters: characters.map(n => n.name), themeChanges, issues };
}
function status(extra) { $('status').textContent = JSON.stringify({ ...info(), ...(extra ? { seekTest: extra } : {}) }, null, 2); }
function fail(error) { issues.push(String(error)); $('status').textContent = issues.join('\n'); console.error(error); }
function resize() { const r = renderer.domElement.parentElement.getBoundingClientRect(); renderer.setSize(Math.floor(r.width), Math.floor(r.height), false); camera.aspect = r.width / r.height; camera.updateProjectionMatrix(); render(time); }
$('file').onchange = async event => { try { const file = event.target.files[0]; if (file) await loadArrayBuffer(await file.arrayBuffer(), file.name); } catch (e) { fail(e); } };
$('theme').onchange = applyCurrentTheme;
$('screen-test').onchange = event => setScreenTest(event.target.checked);
$('fit').onclick = frameAsset;
$('screen-view').onclick = () => { try { screenView(); } catch (e) { fail(e); } };
$('lid').oninput = event => setLidRadians(Number(event.target.value));
$('time').oninput = event => render(Number(event.target.value));
$('clip').onchange = event => { activeClip = Number(event.target.value); $('time').max = actions[activeClip]?.getClip().duration ?? 4; render(0); };
$('sampling').onchange = event => setSampling(event.target.checked);
$('seed').onchange = () => setSampling($('sampling').checked);
$('seek-test').onclick = () => testSeek();
$('screenshot').onclick = () => { render(time); const a = document.createElement('a'); a.href = renderer.domElement.toDataURL('image/png'); a.download = `${source?.split('/').at(-1) ?? 'asset'}-fixture.png`; a.click(); };
window.addEventListener('resize', resize);
window.assetFixture = { ready: false, loadArrayBuffer, loadUrl, render, info, setLidRadians, screenView, screenProbeCoordinates, frameAsset, setScreenTest, testSeek, pixelHash, setSampling, setTheme: name => { if (!themes[name]) throw new Error('Unknown theme'); $('theme').value = name; applyCurrentTheme(); }, setCharacterVisible: (name, visible) => { const node = characters.find(n => n.name === name); if (!node) throw new Error('Unknown character'); node.visible = visible; render(time); }, selectClip: index => { activeClip = index; $('clip').value = String(index); render(0); } };
resize(); applyCurrentTheme();
try { const url = new URLSearchParams(location.search).get('model'); if (url) await loadUrl(url); window.assetFixture.ready = true; } catch (e) { fail(e); window.assetFixture.error = String(e); }
