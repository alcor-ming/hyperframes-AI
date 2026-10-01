import {THREE,sceneKit} from './scene.js';
import {tokenModel,tokenState,tokenCell,moments,clamp} from './state.js';
export async function mount(options) {
 if(!globalThis.HarnessBroll)throw Error('Load frozen runtime/appearance.js and runtime/broll.js first');
 const response=await fetch(new URL('./asset.json',import.meta.url),{redirect:'error'});if(!response.ok)throw Error('token_manifest_missing');
 const metadata=await response.json();
 if(!Number.isSafeInteger(options.slots?.counter)||options.slots.counter<=0)throw Error('token_counter_requires_positive_safe_integer');
 return HarnessBroll.mount(metadata,{...options,slots:{output_label:'',...options.slots}},build);
}
function build(context) {
 const {slots,params,start}=context,model=tokenModel(params),kit=sceneKit(context);
 try {
 const {scene,own,mat,palette,portrait}=kit;
 const origin=portrait?[-1.15,2.55,0]:[-3.7,.65,0],exit=portrait?[1,-2.2,0]:[3.6,.45,0];
 const curve=new THREE.QuadraticBezierCurve3(new THREE.Vector3(...origin),new THREE.Vector3(portrait?-1.8:-2.5,portrait?1.3:2.1,1),new THREE.Vector3(-.95,.45,.3));
 const pipe=new THREE.Mesh(own(new THREE.TubeGeometry(curve,48,.035,8,false)),mat(palette.muted));scene.add(pipe);
 const glass=mat(palette.main,{transparent:true,opacity:.085,depthWrite:false,side:THREE.DoubleSide});
 const box=new THREE.Mesh(own(new THREE.BoxGeometry(2.3,2.4,1.2)),glass);scene.add(box);
 const outline=new THREE.LineSegments(own(new THREE.EdgesGeometry(box.geometry)),own(new THREE.LineBasicMaterial({color:palette.muted,transparent:true,opacity:.7})));scene.add(outline);
 const cube=own(new THREE.BoxGeometry(.23,.23,.23));
 const blocks=new THREE.InstancedMesh(cube,mat(palette.main),model.count);blocks.instanceMatrix.setUsage(THREE.DynamicDrawUsage);scene.add(blocks);
 const spill=new THREE.InstancedMesh(cube,mat(palette.muted,{transparent:true,opacity:.65}),model.count);scene.add(spill);
 const output=new THREE.InstancedMesh(cube,mat(palette.accent,{emissive:palette.accent,emissiveIntensity:.1}),8);scene.add(output);
 const dummy=new THREE.Object3D(),matrix=(mesh,i,p,scale)=>{dummy.position.set(...p);dummy.rotation.set(.12,.15,.08);dummy.scale.setScalar(scale);dummy.updateMatrix();mesh.setMatrixAt(i,dummy.matrix);};
 const cell=i=>tokenCell(model.capacity,i);
 const labels={input_label:kit.label('input_label',slots.input_label,'text'),box_label:kit.label('box_label',slots.box_label),output_label:kit.label('output_label',slots.output_label,'text'),counter:kit.label('counter',slots.counter,'text')};
 const current=kit.label('current','','text'),branch=kit.label('branch','','text');current.style.color=branch.style.color=palette.accent;
 const ticks=Array.from({length:6},(_,i)=>kit.line([1.17,-.9+i*.35,.65],[1.38,-.9+i*.35,.65],palette.muted,.012));
 const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
 function renderAt(t,globalTime){const s=tokenState(model,t,reduced);kit.pose(0,s.pull*.65);kit.visible(globalTime>=start);
  model.tokens.forEach((token,i)=>{let p,scale=token.size;const u=s.tokens[i].progress;
   if(u<1){p=curve.getPoint(u).toArray();const spread=(1-clamp(u*5));p[0]+=((i%8)-3.5)*.14*spread;p[1]-=(Math.floor(i/8)*.16)*spread;scale*=t>=0?1:0;}
   else if(i<model.capacity){p=cell(i);if(params.mode==='overflow'&&i<s.expelled)p=cell(i);}
   else {const extraIndex=i-model.capacity;if(params.mode==='overflow'&&extraIndex<s.expelled)p=cell(extraIndex);else {p=curve.getPoint(.92).toArray();scale=0;}}
   // Once replaced, render the new incoming token in the old slot only once.
   if(params.mode==='overflow'&&i<model.capacity&&i<s.expelled)scale=0;
   if(s.tokens[i].hidden)scale=0;
   matrix(blocks,i,p,scale);
   const launch=3+(i+1)/Math.max(1,model.count-model.capacity)*2.25,age=s.t-launch;
   const active=params.mode==='overflow'&&i<model.count-model.capacity&&age>=0&&age<1.1;
   const fall=clamp(age/1.1);matrix(spill,i,[1.25+fall*(portrait?.4:1.5),-.2+1.1*fall-3.4*fall*fall,.3],active?token.size*(1-fall):0);
  });
  for(let i=0;i<8;i++){const u=clamp((s.t-3-i*.28)/.5),visible=i<s.generated;matrix(output,i,portrait?[.65+(i%3)*.34,-1.6-Math.floor(i/3)*.35,.2]:[1.5+i*.29,.1+(i%2)*.35,.1],visible?(reduced?1:u):0);}
  pipe.visible=t<6;
  blocks.instanceMatrix.needsUpdate=spill.instanceMatrix.needsUpdate=output.instanceMatrix.needsUpdate=true;
  ticks.forEach((x,i)=>x.mesh.material.color.set(s.fraction>=(i+1)/6?palette.accent:palette.muted));
  outline.material.color.set(s.full&&t>=3?palette.accent:palette.muted);outline.scale.setScalar(s.full&&t>=3&&!reduced?1+Math.sin(clamp((t-3)/.5)*Math.PI)*.025:1);
  glass.opacity=params.mode==='generate'&&t>=3?.16:.085;
  kit.place(labels.input_label,[origin[0],origin[1]+.45,0],true);
  kit.place(labels.box_label,[0,1.55,0],t>=1);
  kit.place(labels.counter,[0,-1.4,0],s.countVisible);
  kit.place(labels.output_label,[exit[0],exit[1]-.6,0],params.mode==='generate'&&s.outputVisible);
  current.textContent=s.countVisible?Math.round(s.fraction*slots.counter)+' /':'';kit.place(current,[0,-1.1,0],s.countVisible);
  // Milestones visibly describe retention/output instead of padding the rhythm
  // registry with camera-only events. No semantic claim about a real model.
  const percentage=Math.round(s.fraction*100)+'%';const fillStages=['','↘','↘',percentage,percentage+' ○',percentage+' ●',percentage+' ✓','✓','✓'];
  branch.textContent=params.mode==='overflow'&&s.t>=4.5?'-'+Math.round(s.expelled/model.capacity*slots.counter):params.mode==='generate'&&s.t>=3?'+'+s.generated:params.mode==='fill'?fillStages[s.phase]:'';
  if(s.t>=6)branch.textContent+=' ✓';if(s.settled)branch.textContent+=' ●';kit.place(branch,portrait?[0,-2.4,0]:[2.8,-1,0],!!branch.textContent);kit.draw();
 }
 return {renderAt,labels,events:moments.map(time=>({time,target:time>=4.5||(params.mode==='fill'&&time>=3)?branch:kit.renderer.domElement})),dispose:kit.dispose};
 }catch(e){kit.dispose();throw e;}
}
