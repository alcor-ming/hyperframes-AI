export const clamp = x => Math.max(0, Math.min(1, x));
export const smooth = x => { x=clamp(x); return x*x*(3-2*x); };
export function random(seed) { return () => { let t=seed+=0x6D2B79F5; t=Math.imul(t^t>>>15,t|1); t^=t+Math.imul(t^t>>>7,t|61); return ((t^t>>>14)>>>0)/4294967296; }; }
export const moments = [0,.6,1.2,2,2.8,3.6,4.2,5.2,5.8];
export function graphModel(slots, params, portrait=false) {
  const ids=['hub',...Array.from({length:8},(_,i)=>`n${i+1}`).filter(id=>slots[id]?.trim())];
  if (!slots.hub?.trim()) throw Error('graph_hub_required');
  // Explicit n1..n8 contract means up to eight peripheral nodes plus hub.
  if(ids.length<2) throw Error('graph_requires_peripheral_node');
  const path=params.path.split('>');
  if(path.length<3||path.length>6||path.some(id=>!ids.includes(id))||path.some((id,i)=>i&&id===path[i-1])) throw Error('graph_path_requires_2_to_5_existing_edges');
  const rng=random(params.seed), n=ids.length-1;
  const points=ids.map((id,i)=> {
    if(params.topology==='chain') {const u=i/(ids.length-1); return portrait?[Math.sin(u*Math.PI*2)*.8,2.2-u*4.4,(i%2)*.5]:[-3.5+u*7,Math.sin(u*Math.PI)*.8,(i%2)*.5];}
    if(!i)return [0,.3,0];
    const a=(i-1)/n*Math.PI*2-Math.PI/2;
    if(params.topology==='layers') {const tier=i<=Math.ceil(n/2)?0:1; const count=tier?n-Math.ceil(n/2):Math.ceil(n/2); const j=tier?i-Math.ceil(n/2)-1:i-1; return [(j-(count-1)/2)*(portrait?1.2:1.6),tier?-1.65:1.8,tier?-.65:.65];}
    return [Math.cos(a)*(portrait?1.55:2.8)+(params.topology==='mesh'?(rng()-.5)*.45:0),Math.sin(a)*(portrait?2:1.65)+.3,params.topology==='mesh'?(rng()-.5)*1.8:Math.sin(a*2)*.55];
  });
  const edges=[], add=(a,b)=>{if(!edges.some(e=>e.includes(a)&&e.includes(b)))edges.push([a,b]);};
  if(params.topology==='chain') ids.slice(1).forEach((id,i)=>add(ids[i],id));
  else if(params.topology==='layers') {ids.slice(1).forEach((id,i)=>add(i<Math.ceil(n/2)?'hub':ids[1+(i%Math.ceil(n/2))],id));}
  else {ids.slice(1).forEach(id=>add('hub',id)); if(params.topology==='mesh')ids.slice(1).forEach((id,i)=>add(id,ids[1+(i+1)%n]));}
  // A declared signal route is an explicit extra link in any topology.
  path.slice(1).forEach((id,i)=>add(path[i],id));
  return {ids,points,edges,path,params};
}
export function graphState(model,t,reduced=false) {
  t=Math.max(0,Math.min(6,t));
  if(reduced)t=moments.filter(x=>x<=t).at(-1)??0;
  const grow=(start,duration)=>reduced?+(t>=start):smooth((t-start)/duration);
  const signal=clamp((t-4.2)/1), segment=Math.min(model.path.length-2,Math.floor(signal*(model.path.length-1)));
  return {t,nodeScale:model.ids.map((_,i)=>grow(i?1.2+(i-1)*.08:0,.48)),
    settled:t>=.6, labelsReady:t>=2, connected:t>=3.6,
    edgeProgress:model.edges.map((_,i)=>grow(2.8+i/Math.max(1,model.edges.length-1)*.3,.45)),
    signal,segment,pulseVisible:t>=4.2&&t<5.2,
    visited:model.path.filter((_,i)=>t>=4.2+i/(model.path.length-1)),
    terminal:grow(5.2,.6), finished:t>=5.8,
    orbit:reduced?0:(model.params['camera.orbit_deg']*Math.PI/180)*smooth(t/5.2)};
}
