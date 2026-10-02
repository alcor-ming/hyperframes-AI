import test from 'node:test';
import assert from 'node:assert/strict';
import {graphModel,graphState,graphMoments,curvePoint} from './graph-grow/state.js';
import {resolveLabels,overlaps} from './graph-grow/layout.js';
const options={path:'n1>hub>n4',seed:41,'camera.orbit_deg':30};
const chinese={hub:'调度中心',n1:'输入问题',n2:'调用工具',n3:'长期记忆',n4:'生成回答'};
const dense={hub:'中枢调度系统',...Object.fromEntries(Array.from({length:8},(_,i)=>['n'+(i+1),'中文六个字符']))};
for(const topology of ['star','chain','layers','mesh'])for(const portrait of [false,true]) {
 test(`planar ${topology} ${portrait?'portrait':'landscape'}`,()=>{
  const m=graphModel(dense,{...options,topology,path:'n1>n3>n5>n7>n2>n4'},portrait);
  assert.ok(m.points.every(p=>p[2]===0));assert.ok(m.edges.length<=16);
  assert.deepEqual(m.points[m.ids.indexOf('hub')],[.5,.5,0]);
  assert.equal(m.route.length,5);
  m.route.forEach(step=>{assert.ok(m.edges[step.edge].includes(step.from)&&m.edges[step.edge].includes(step.to));});
  m.curves.slice(m.structuralCount).forEach(curve=>assert.equal(curve.length,3));
  assert.deepEqual(graphModel(dense,m.params,portrait),m);
  for(const reduced of [false,true])for(const t of [0,.6,1.5,3.2,3.35,4.8,5.1,5.2,6]){
   const expected=graphState(m,t,reduced);graphState(m,6,reduced);graphState(m,0,reduced);assert.deepEqual(graphState(m,t,reduced),expected);assert.equal(expected.orbit,0);
   if(reduced)expected.routeProgress.forEach((done,i)=>{if(done)assert.ok(expected.visited.includes(m.route[i].to));});
  }
  const events=[...graphMoments(m),6];assert.ok(events.every((x,i)=>!i||(x-events[i])*10/6<=2+1e-9));
  assert.ok(graphState(m,2.8).edgeProgress.every(p=>Math.abs(p-1)<1e-9));
 });
}
test('hub is exactly centered with all peripheral counts',()=>{
 for(let count=1;count<=8;count++)for(const portrait of [false,true]){
  const slots={hub:'Hub',...Object.fromEntries(Array.from({length:count},(_,i)=>['n'+(i+1),'Node']))};
  const m=graphModel(slots,{...options,topology:'chain',path:'n1>hub>n1'},portrait);
  assert.deepEqual(m.points[0],[.5,.5,0]);
 }
});
for(const [name,slots,topology,portrait]of [['star4-chinese',chinese,'star',false],['chain8-chinese',dense,'chain',false],['mesh9-portrait',dense,'mesh',true]]){
 test('deterministic capsule solver: '+name,()=>{
  const m=graphModel(slots,{...options,topology},portrait),width=portrait?540:960,height=(portrait?960:540)*.84;
  const font=portrait?20:15,radius=portrait?width*.019:height*.027;
  // Conservative CJK full-em measurement plus capsule padding; real glyph
  // measurements remain the browser fixture's responsibility.
  const obstacles=m.points.map(([x,y],i)=>({x:x*width-radius*(i?1:1.3),y:y*height-radius*(i?1:1.3),width:radius*(i?2:2.6),height:radius*(i?2:2.6)}));
  const items=m.ids.map((id,i)=>{const fs=id==='hub'?font*38/30:font,w=([...slots[id]].length+1)*fs+2,h=fs*1.74+2;let[nx,ny]=m.labelNormals[i];const n=Math.hypot(nx,ny)||1;nx/=n;ny/=n;const d=radius+(Math.abs(nx)*w+Math.abs(ny)*h)/2+Math.max(8,radius*.65);return{id,width:w,height:h,x:m.points[i][0]*width+nx*d,y:m.points[i][1]*height+ny*d,normal:[nx,ny]};});
  const result=resolveLabels(items,width,height,obstacles,6);assert.deepEqual(resolveLabels(items,width,height,obstacles,6),result);
  result.forEach((r,i)=>{assert.ok(r.x>=0&&r.y>=0&&r.x+r.width<=width&&r.y+r.height<=height);assert.ok(!result.slice(i+1).some(other=>overlaps(r,other,6)));assert.ok(!obstacles.some(o=>overlaps(r,o,2.7)));});
 });
}
test('unfit labels fail explicitly instead of clipping or shrinking',()=>{
 assert.throws(()=>resolveLabels([{id:'oversize',x:1,y:1,width:1000,height:50}],100,100),/label_capacity/);
});

test('diameter jumps and layers edges avoid unrelated nodes',()=>{
 for(const topology of ['star','layers'])for(const portrait of [false,true]){const slots=topology==='star'?dense:Object.fromEntries(Object.entries(dense).slice(0,7));const m=graphModel(slots,{...options,topology,path:'n1>n5>n3'},portrait);
 m.curves.forEach((curve,i)=>{for(let k=1;k<96;k++){const p=curvePoint(curve,k/96);m.ids.forEach((id,j)=>{if(!m.edges[i].includes(id))assert.ok(Math.hypot(p[0]-m.points[j][0],p[1]-m.points[j][1])>.043);});}});}
});
