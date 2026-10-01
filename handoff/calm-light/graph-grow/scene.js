import * as THREE from './vendor/three.min.js';
export {THREE};
export function sceneKit({stage,text,appearance}) {
 const doc=stage.ownerDocument, nodes=[],resources=new Set(); let renderer,disposed=false;
 const own=o=>{resources.add(o);return o;};
 const make=(parent,style,content)=>{const e=doc.createElement('div');Object.assign(e.style,style);if(content!==undefined)e.textContent=String(content);parent.append(e);nodes.push(e);return e;};
 const dispose=()=>{if(disposed)return;disposed=true;for(const r of resources)r.dispose?.();renderer?.dispose();renderer?.forceContextLoss();for(const e of nodes)e.remove();};
 try {
 const css=getComputedStyle(stage), read=name=>{const v=css.getPropertyValue('--appearance-'+name).trim();if(!v)throw Error('calm_light_missing_theme_token:'+name);return v;};
 const palette={background:read('surface-color'),main:read('colors-text'),accent:read('colors-accent'),muted:read('colors-muted')};
 const font=read('typography-body');
 const frame=make(stage,{position:'absolute',inset:'0 0 16% 0',overflow:'hidden',pointerEvents:'none'});frame.dataset.hfSchematic='';
 const overlay=make(text,{position:'absolute',inset:'0 0 16% 0',overflow:'hidden',pointerEvents:'none'});
 const scene=new THREE.Scene();scene.background=new THREE.Color(palette.background);scene.fog=new THREE.Fog(palette.background,9,22);
 renderer=new THREE.WebGLRenderer({antialias:true,alpha:false,preserveDrawingBuffer:true});renderer.setClearColor(palette.background,1);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.setPixelRatio(doc.defaultView.devicePixelRatio||1);frame.append(renderer.domElement);
 const camera=new THREE.PerspectiveCamera(37,1,.1,50); const portrait=appearance.lock.ratio==='9:16';
 for(const [x,y,z,intensity,color]of [[4,6,7,2.1,palette.main],[-5,2,4,1.25,palette.background],[2,3,-5,1.7,palette.accent]]){const light=new THREE.DirectionalLight(color,intensity);light.position.set(x,y,z);scene.add(light);}
 scene.add(new THREE.AmbientLight(palette.background,1.6));
 const mat=(color,extra={})=>own(new THREE.MeshStandardMaterial({color,roughness:.76,metalness:.03,...extra}));
 const label=(name,content,layer='stage')=>{const e=make(layer==='text'?overlay:frame,{position:'absolute',left:'0',top:'0',width:'max-content',maxWidth:'calc(100% - 16px)',minWidth:'1px',minHeight:'1em',whiteSpace:'nowrap',fontFamily:font,fontSize:Math.max(12,Math.min(stage.clientWidth,stage.clientHeight*.84)*.035)+'px',lineHeight:'1.35',fontWeight:'600',color:palette.main,transform:'translate(-50%,-50%)',padding:'3px 5px',pointerEvents:'none'},content);e.dataset.calmLabel=name;return e;};
 let width=0,height=0;
 function size(){const w=stage.clientWidth,h=stage.clientHeight*.84;if(w<=0||h<=0)throw Error('calm_light_empty_stage');if(w!==width||h!==height){width=w;height=h;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();for(const e of nodes)if(e.dataset.calmLabel)e.style.fontSize=Math.max(12,Math.min(w,h)*.035)+'px';}}
 function pose(angle=0,pull=0,target=[0,0,0]){size();const z=(portrait?11.8:10.8)+pull;camera.position.set(Math.sin(angle)*z,portrait?1.2:1.6,Math.cos(angle)*z);camera.lookAt(...target);camera.updateMatrixWorld();}
 function place(e,p,visible=true,dy=0){const v=new THREE.Vector3(...p).project(camera);const x=(v.x*.5+.5)*width,y=(-v.y*.5+.5)*height+dy;const hw=e.offsetWidth/2,hh=e.offsetHeight/2;e.style.left=Math.max(hw+8,Math.min(width-hw-8,x))+'px';e.style.top=Math.max(hh+8,Math.min(height-hh-8,y))+'px';e.style.opacity=visible?'1':'0';}
 function line(a,b,color,r=.02){const delta=new THREE.Vector3(...b).sub(new THREE.Vector3(...a));const mesh=new THREE.Mesh(own(new THREE.CylinderGeometry(r,r,1,8)),mat(color));mesh.position.copy(new THREE.Vector3(...a).addScaledVector(delta,.5));mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),delta.clone().normalize());mesh.scale.y=delta.length();scene.add(mesh);return {mesh,length:delta.length(),a:new THREE.Vector3(...a),delta};}
 pose();return {scene,camera,renderer,frame,overlay,palette,portrait,own,mat,label,place,line,pose,dispose,draw:()=>renderer.render(scene,camera),visible:on=>{frame.style.opacity=overlay.style.opacity=on?'1':'0';}};
 }catch(e){dispose();throw e;}
}
