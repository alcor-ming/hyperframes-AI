import * as THREE from './vendor/three.min.js';
import {resolveLabels} from './layout.js';
export {THREE};

/** Shared fixed 2.5D stage. World coordinates are normalized x/y (y downward). */
export function sceneKit({stage, text, appearance}) {
  const doc = stage.ownerDocument, nodes = [], resources = new Set();
  let renderer, disposed = false, width = 0, height = 0;
  const portrait = appearance.lock.ratio === '9:16';
  const own = value => { resources.add(value); return value; };
  const make = (parent, style, content) => {
    const node = doc.createElement('div');
    Object.assign(node.style, style);
    if (content !== undefined) node.textContent = String(content);
    parent.append(node); nodes.push(node); return node;
  };
  const dispose = () => {
    if (disposed) return;
    disposed = true;
    for (const value of resources) value.dispose?.();
    renderer?.dispose(); renderer?.forceContextLoss();
    for (const node of nodes) node.remove();
  };
  try {
    const css = getComputedStyle(stage);
    const read = name => {
      const value = css.getPropertyValue('--appearance-' + name).trim();
      if (!value) throw Error('calm_light_missing_theme_token:' + name);
      return value;
    };
    const palette = {background:read('surface-color'), main:read('colors-text'),
      accent:read('colors-accent'), muted:read('colors-muted')};
    const font = read('typography-body');
    const frame = make(stage, {position:'absolute', inset:'0 0 16% 0', overflow:'hidden', pointerEvents:'none'});
    frame.dataset.hfSchematic = '';
    const overlay = make(text, {position:'absolute', inset:'0 0 16% 0', overflow:'hidden', pointerEvents:'none'});
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(palette.background);
    // No perspective, orbit, fog or colored illumination. Theme colors remain exact.
    const camera = new THREE.OrthographicCamera(0, 1, 0, 1, .01, 10);
    camera.position.set(0, 0, 4); camera.lookAt(0, 0, 0); camera.updateMatrixWorld();
    renderer = new THREE.WebGLRenderer({antialias:true, alpha:false, preserveDrawingBuffer:true});
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.setPixelRatio(doc.defaultView.devicePixelRatio || 1);
    frame.append(renderer.domElement);
    // Flat theme-matched material is an intentional choice, not a lighting fallback.
    const mat = (color, extra = {}) => {
      const {emissive, emissiveIntensity, roughness, metalness, ...basic} = extra;
      return own(new THREE.MeshBasicMaterial({color, side:THREE.DoubleSide, ...basic}));
    };
    const fontSize = () => portrait ? stage.clientWidth * 40 / 1080 : stage.clientHeight * 30 / 1080;
    function size() {
      const w = stage.clientWidth, h = stage.clientHeight * .84;
      if (w <= 0 || h <= 0) throw Error('calm_light_empty_stage');
      if (w !== width || h !== height) {
        width = w; height = h; renderer.setSize(w, h);
        for (const e of nodes) if (e.dataset.calmLabel) {
          const fs = fontSize() * (e.dataset.calmHub === 'true' ? 38 / 30 : 1);
          e.style.fontSize = fs + 'px';
          e.style.padding = `${fs * .22}px ${fs * .5}px`;
        }
      }
    }
    const label = (name, content, layer = 'stage') => {
      const fs = fontSize();
      const e = make(layer === 'text' ? overlay : frame, {
        position:'absolute', left:'0', top:'0', width:'max-content',
        maxWidth:'calc(100% - 16px)', minWidth:'1px', minHeight:'1em',
        boxSizing:'border-box', whiteSpace:'nowrap', fontFamily:font, fontSize:fs + 'px',
        lineHeight:'1.3', fontWeight:'500', color:palette.main, background:palette.background,
        borderRadius:'999px', border:'1px solid transparent', padding:`${fs*.22}px ${fs*.5}px`,
        transform:'translate(-50%,-50%)', pointerEvents:'none'
      }, content);
      e.dataset.calmLabel = name; return e;
    };
    function pose() { size(); }
    function project(point) { return [point[0] * width, point[1] * height]; }
    function place(e, point, visible = true, dy = 0) {
      const [x,y] = project(point), hw = e.offsetWidth / 2, hh = e.offsetHeight / 2;
      e.style.left = Math.max(hw + 8, Math.min(width - hw - 8, x)) + 'px';
      e.style.top = Math.max(hh + 8, Math.min(height - hh - 8, y + dy)) + 'px';
      e.style.opacity = visible ? '1' : '0';
    }
    function layoutLabels(items, obstacles = []) {
      const resolved = resolveLabels(items.map(item => ({...item,
        width:item.element.offsetWidth, height:item.element.offsetHeight})), width, height, obstacles,
        Math.max(6, fontSize() * .35));
      resolved.forEach((rect, i) => {
        items[i].element.style.left = rect.x + rect.width / 2 + 'px';
        items[i].element.style.top = rect.y + rect.height / 2 + 'px';
      });
      return resolved;
    }
    function line(a, b, color, radius = .002) {
      const delta = new THREE.Vector3(...b).sub(new THREE.Vector3(...a));
      const mesh = new THREE.Mesh(own(new THREE.CylinderGeometry(radius, radius, 1, 8)), mat(color));
      mesh.position.copy(new THREE.Vector3(...a).addScaledVector(delta, .5));
      mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0), delta.clone().normalize());
      mesh.scale.y = delta.length(); scene.add(mesh);
      return {mesh, length:delta.length(), a:new THREE.Vector3(...a), delta};
    }
    pose();
    return {scene, camera, renderer, frame, overlay, palette, portrait, own, mat, label,
      place, project, layoutLabels, line, pose, dispose,
      get width(){return width;}, get height(){return height;},
      get aspect(){return width/height;}, bounds:{left:0,right:1,top:0,bottom:1},
      draw:() => renderer.render(scene,camera),
      visible:on => {frame.style.opacity = overlay.style.opacity = on ? '1' : '0';}};
  } catch (error) { dispose(); throw error; }
}
