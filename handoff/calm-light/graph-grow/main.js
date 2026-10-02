import {THREE,sceneKit} from './scene.js';
import {graphModel,graphState,graphMoments} from './state.js';
const manifestURL = new URL('./asset.json',import.meta.url);

export async function mount(options) {
  if (!globalThis.HarnessBroll) throw Error('Load frozen runtime/appearance.js and runtime/broll.js first');
  const response = await fetch(manifestURL,{redirect:'error'});
  if (!response.ok) throw Error('graph_manifest_missing');
  const metadata = await response.json();
  const slots = {...Object.fromEntries(Array.from({length:8},(_,i)=>['n'+(i+1),''])),...options.slots};
  const supplied = options.params?.path ?? metadata.parameters.path.default;
  if (typeof supplied !== 'string' || !/^((hub|n[1-8])>){2,5}(hub|n[1-8])$|^((hub|n[1-8])\/){2,5}(hub|n[1-8])$/.test(supplied)) throw Error('graph_invalid_path');
  const path = supplied.replaceAll('/','>');
  // Public arrow grammar is validated before adapting to HarnessBroll's generic
  // expression guard. Manifest uses the pack-compatible slash representation.
  metadata.broll.params = structuredClone(metadata.broll.params);
  metadata.broll.params.path.default = path.replaceAll('>','/');
  return HarnessBroll.mount(metadata,{...options,slots,params:{...options.params,path:path.replaceAll('>','/')}},
    context => build({...context,params:{...context.params,path}}));
}

function build(context) {
  const {slots,params,start,appearance} = context;
  const model = graphModel(slots,params,appearance.lock.ratio==='9:16');
  const kit = sceneKit(context);
  try {
    const {scene,own,mat,palette} = kit;
    const nodeGeometry = own(new THREE.CircleGeometry(1,48));
    const meshes = model.ids.map((id,i) => {
      const mesh = new THREE.Mesh(nodeGeometry,mat(palette.main,{transparent:true}));
      mesh.position.set(...model.points[i]); scene.add(mesh); return mesh;
    });
    const curveObjects = model.curves.map(points => points.length===2
      ? new THREE.LineCurve3(...points.map(p=>new THREE.Vector3(...p)))
      : new THREE.QuadraticBezierCurve3(...points.map(p=>new THREE.Vector3(...p))));
    // Pixel-width ribbons avoid WebGL implementation-dependent Line widths.
    function ribbon(curve,color) {
      const positions = new Float32Array(48*6*3), geometry = own(new THREE.BufferGeometry());
      geometry.setAttribute('position',new THREE.BufferAttribute(positions,3));
      const mesh = new THREE.Mesh(geometry,mat(color,{transparent:true,depthWrite:false}));
      mesh.renderOrder = 1; scene.add(mesh);
      return {curve,positions,geometry,mesh};
    }
    const links = curveObjects.map(curve=>ribbon(curve,palette.muted));
    const routeLinks = model.route.map(step=>ribbon(curveObjects[step.edge],palette.accent));
    const arrows = model.route.map(() => {
      const geometry = own(new THREE.BufferGeometry());
      geometry.setAttribute('position',new THREE.BufferAttribute(new Float32Array(9),3));
      const mesh = new THREE.Mesh(geometry,mat(palette.accent));
      mesh.renderOrder=4;scene.add(mesh);return mesh;
    });
    const pulse = new THREE.Mesh(nodeGeometry,mat(palette.accent)); pulse.renderOrder=5; scene.add(pulse);
    const ring = new THREE.Mesh(own(new THREE.RingGeometry(.83,1,48)),mat(palette.accent)); ring.renderOrder=4; scene.add(ring);
    const labels = Object.fromEntries(Object.entries(slots).map(([id,value])=>[id,kit.label(id,value,id==='hub'?'text':'stage')]));
    labels.hub.dataset.calmHub='true'; labels.hub.style.fontWeight='700'; labels.hub.style.borderColor=palette.accent;
    const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
    let layoutKey = '';
    function updateLayout() {
      const key = kit.width + 'x' + kit.height;
      if (key===layoutKey) return;
      layoutKey=key;
      const nodeRadius = (kit.portrait ? kit.width*.019 : kit.height*.027);
      const hubFont=kit.portrait ? context.stage.clientWidth*48/1080 : context.stage.clientHeight*38/1080;
      labels.hub.style.fontSize=hubFont+'px';labels.hub.style.padding=`${hubFont*.22}px ${hubFont*.5}px`;
      const obstacles = model.points.map((point,i)=>({x:point[0]*kit.width-nodeRadius*(i?1:1.3),y:point[1]*kit.height-nodeRadius*(i?1:1.3),width:nodeRadius*(i?2:2.6),height:nodeRadius*(i?2:2.6)}));
      const items = model.ids.map((id,i)=>{
        const [x,y]=kit.project(model.points[i]); let [nx,ny]=model.labelNormals[i];
        const magnitude=Math.hypot(nx,ny)||1;nx/=magnitude;ny/=magnitude;
        const e=labels[id], offset=nodeRadius+(Math.abs(nx)*e.offsetWidth+Math.abs(ny)*e.offsetHeight)/2+Math.max(8,nodeRadius*.65);
        return {id,element:e,x:x+nx*offset,y:y+ny*offset,normal:[nx,ny]};
      });
      kit.layoutLabels(items,obstacles);
      for(const id of Object.keys(labels))if(!model.ids.includes(id))labels[id].style.opacity='0';
    }
    function paintRibbon(item,progress,widthPx,reverse=false) {
      const verts=item.positions, count=48;
      for(let i=0;i<count;i++) {
        const at=i/count*progress, next=(i+1)/count*progress;
        const a=item.curve.getPoint(reverse?1-at:at),b=item.curve.getPoint(reverse?1-next:next);
        const dx=(b.x-a.x)*kit.width,dy=(b.y-a.y)*kit.height,length=Math.hypot(dx,dy)||1;
        const ox=-dy/length*widthPx/2/kit.width,oy=dx/length*widthPx/2/kit.height;
        const v=[[a.x+ox,a.y+oy],[a.x-ox,a.y-oy],[b.x+ox,b.y+oy],[b.x+ox,b.y+oy],[a.x-ox,a.y-oy],[b.x-ox,b.y-oy]];
        v.forEach(([x,y],j)=>{const k=(i*6+j)*3;verts[k]=x;verts[k+1]=y;verts[k+2]=.015;});
      }
      item.geometry.attributes.position.needsUpdate=true;
      item.geometry.computeBoundingSphere();item.mesh.visible=progress>0;
    }
    function renderAt(t,globalTime) {
      const s=graphState(model,t,reduced);kit.pose();updateLayout();kit.visible(globalTime>=start);
      const radius=kit.portrait?kit.width*.019:kit.height*.027;
      meshes.forEach((mesh,i)=>{
        const visited=s.visited.includes(model.ids[i]),end=model.ids[i]===model.path.at(-1);
        const r=radius*(i?1:1.3)*s.nodeScale[i]*(end?1+.12*s.terminal:1);
        mesh.scale.set(r/kit.width,r/kit.height,1);mesh.visible=r>0;
        mesh.material.color.set(visited?palette.accent:palette.main);
        mesh.material.opacity=s.t>=3.35&&!model.path.includes(model.ids[i])?.65:1;
        mesh.position.z=visited?.03:.025;
        labels[model.ids[i]].style.opacity=s.nodeScale[i]>.01?'1':'0';
      });
      const baseWidth=Math.max(1.25,kit.width*(kit.portrait?.003:.0018));
      links.forEach((link,i)=>{
        paintRibbon(link,s.edgeProgress[i],baseWidth);
        link.mesh.material.opacity=s.t>=3.35?.38:.72;
        link.mesh.material.color.set(palette.muted);
      });
      model.route.forEach((step,i)=>{
        const progress=s.routeProgress[i];paintRibbon(routeLinks[i],progress,baseWidth*2.2,step.reverse);
        const arrow=arrows[i],curve=curveObjects[step.edge];arrow.visible=progress>.05;
        const u=Math.min(.86,Math.max(.15,progress*.86)),p=curve.getPoint(step.reverse?1-u:u),v=curve.getTangent(step.reverse?1-u:u).multiplyScalar(step.reverse?-1:1);
        const dx=v.x*kit.width,dy=v.y*kit.height,len=Math.hypot(dx,dy)||1;
        const ux=dx/len,uy=dy/len,arrowSize=baseWidth*3.3;
        const vertices=[[1,0],[-.7,-.65],[-.7,.65]],positions=arrow.geometry.attributes.position;
        vertices.forEach(([along,side],j)=>positions.setXYZ(j,
          p.x+(ux*along-uy*side)*arrowSize/kit.width,
          p.y+(uy*along+ux*side)*arrowSize/kit.height,.03));
        positions.needsUpdate=true;arrow.geometry.computeBoundingSphere();
      });
      pulse.visible=s.pulseVisible&&!reduced;
      if(pulse.visible){const step=model.route[s.segment],p=curveObjects[step.edge].getPoint(step.reverse?1-s.segmentProgress:s.segmentProgress);pulse.position.set(p.x,p.y,.04);pulse.scale.set(radius*.42/kit.width,radius*.42/kit.height,1);}
      ring.visible=s.t>=5.1;ring.position.set(...model.points[model.ids.indexOf(model.path.at(-1))]);ring.position.z=.04;
      ring.scale.set(radius*1.65/kit.width,radius*1.65/kit.height,1);kit.draw();
    }
    // Solve once with the actual frozen font before the shared host validates.
    kit.pose();updateLayout();
    return {renderAt,labels,events:graphMoments(model).map(time=>({time,target:kit.renderer.domElement})),dispose:kit.dispose};
  } catch(error) {kit.dispose();throw error;}
}
