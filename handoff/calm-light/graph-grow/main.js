import {THREE,sceneKit} from './scene.js';
import {graphModel,graphState,moments} from './state.js';
const manifestURL=new URL('./asset.json',import.meta.url);
export async function mount(options) {
 if(!globalThis.HarnessBroll)throw Error('Load frozen runtime/appearance.js and runtime/broll.js first');
 const response=await fetch(manifestURL,{redirect:'error'});if(!response.ok)throw Error('graph_manifest_missing');
 const metadata=await response.json();
 const slots={...Object.fromEntries(Array.from({length:8},(_,i)=>['n'+(i+1),''])),...options.slots};
 const suppliedPath=options.params?.path??metadata.parameters.path.default;
 if(typeof suppliedPath!=='string'||!/^((hub|n[1-8])>){2,5}(hub|n[1-8])$|^((hub|n[1-8])\/){2,5}(hub|n[1-8])$/.test(suppliedPath))throw Error('graph_invalid_path');
 const originalPath=suppliedPath.replaceAll('/','>');
 if(typeof originalPath!=='string'||!/^((hub|n[1-8])>){2,5}(hub|n[1-8])$/.test(originalPath))throw Error('graph_invalid_path');
 // HarnessBroll's generic anti-expression validator rejects >. Validate the
 // public grammar above, then translate only this value before its validation.
 metadata.broll.params=structuredClone(metadata.broll.params);metadata.broll.params.path.default=originalPath.replaceAll('>','/');
 const params={...options.params,path:originalPath.replaceAll('>','/')};
 return HarnessBroll.mount(metadata,{...options,slots,params},context=>build({...context,params:{...context.params,path:originalPath}}));
}
function build(context) {
 const {slots,params,start,appearance}=context;
 const model=graphModel(slots,params,appearance.lock.ratio==='9:16');
 const kit=sceneKit(context);try {
 const {scene,own,mat,palette}=kit;
 const geometry=own(new THREE.SphereGeometry(.24,28,20));
 const meshes=model.ids.map((id,i)=>{const m=new THREE.Mesh(geometry,mat(palette.main,{emissive:palette.accent,emissiveIntensity:.08}));m.position.set(...model.points[i]);scene.add(m);return m;});
 const links=model.edges.map(([a,b])=>kit.line(model.points[model.ids.indexOf(a)],model.points[model.ids.indexOf(b)],palette.muted));
 const labels=Object.fromEntries(Object.entries(slots).map(([id,value])=>[id,kit.label(id,value,id==='hub'?'text':'stage')]));
 const pulse=new THREE.Mesh(own(new THREE.SphereGeometry(.11,16,12)),mat(palette.accent,{emissive:palette.accent,emissiveIntensity:.45}));scene.add(pulse);
 const ring=new THREE.Mesh(own(new THREE.TorusGeometry(.38,.025,8,48)),mat(palette.accent));scene.add(ring);
 const status=kit.label('status','','stage');status.style.color=palette.accent;
 const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
 function renderAt(t,globalTime){const s=graphState(model,t,reduced);const endpoint=model.points[model.ids.indexOf(model.path.at(-1))];kit.pose(s.orbit,-.45*s.terminal,endpoint.map(v=>v*s.terminal*.15));kit.visible(globalTime>=start);
  meshes.forEach((m,i)=>{const active=s.visited.includes(model.ids[i]);const terminal=model.ids[i]===model.path.at(-1);m.scale.setScalar(Math.max(.0001,s.nodeScale[i])*(1+(terminal?.18*s.terminal:0)));m.visible=s.nodeScale[i]>0;m.material.color.set(t>=4.2?(active?palette.accent:palette.muted):palette.main);m.material.emissiveIntensity=active?.2:.04;kit.place(labels[model.ids[i]],model.points[i],s.nodeScale[i]>.1,-28);});
  for(const id of Object.keys(labels))if(!model.ids.includes(id))labels[id].style.opacity='0';
  links.forEach((e,i)=>{const p=s.edgeProgress[i];e.mesh.visible=p>0;e.mesh.scale.y=e.length*p;e.mesh.position.copy(e.a).addScaledVector(e.delta,p/2);e.mesh.material.color.set(s.connected?palette.main:palette.muted);});
  pulse.visible=s.pulseVisible;if(pulse.visible){const a=new THREE.Vector3(...model.points[model.ids.indexOf(model.path[s.segment])]),b=new THREE.Vector3(...model.points[model.ids.indexOf(model.path[s.segment+1])]);pulse.position.copy(a.lerp(b,s.signal*(model.path.length-1)-s.segment));}
  ring.visible=s.settled;ring.position.copy(s.finished?meshes[model.ids.indexOf(model.path.at(-1))].position:meshes[0].position);ring.quaternion.copy(kit.camera.quaternion);ring.scale.setScalar(s.labelsReady?1.15:1);
  status.textContent=s.finished?'●':s.connected?'●':s.labelsReady?'○':'';kit.place(status,s.finished?endpoint:model.points[0],s.labelsReady,36);kit.draw();
 }
 return {renderAt,events:moments.map(time=>({time,target:time===2||time===5.8?status:kit.renderer.domElement})),labels,dispose:kit.dispose};
 }catch(e){kit.dispose();throw e;}
}
