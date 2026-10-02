export const clamp = x => Math.max(0, Math.min(1, x));
export const smooth = x => { x = clamp(x); return x * x * (3 - 2 * x); };
export function random(seed) {
  return () => {
    let t = seed += 0x6D2B79F5;
    t = Math.imul(t ^ t >>> 15, t | 1);
    t ^= t + Math.imul(t ^ t >>> 7, t | 61);
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}
export const moments = [0, .35, .6, .95, 1.8, 2.8, 3.35, 4.225, 5.1, 5.2];
const edgeKey = (a,b) => [a,b].sort().join('|');

export function graphModel(slots, params, portrait = false) {
  const peripheral = Array.from({length:8}, (_,i) => 'n' + (i+1)).filter(id => slots[id]?.trim());
  const ids = ['hub', ...peripheral];
  if (!slots.hub?.trim()) throw Error('graph_hub_required');
  if (ids.length < 2) throw Error('graph_requires_peripheral_node');
  const path = params.path.replaceAll('/', '>').split('>');
  if (path.length < 3 || path.length > 6 || path.some(id => !ids.includes(id)) ||
      path.some((id,i) => i && id === path[i-1])) throw Error('graph_path_requires_2_to_5_existing_edges');
  const rng = random(params.seed), n = peripheral.length;
  // Hub retains its central semantics, including chain. Portrait uses a vertical
  // reading axis rather than compressing nine labels into a horizontal row.
  const order = [...peripheral]; order.splice(Math.floor(order.length / 2), 0, 'hub');
  const points = ids.map((id, index) => {
    if (params.topology === 'chain') {
      const hubIndex = order.indexOf('hub');
      const radius = Math.max(hubIndex,order.length-1-hubIndex);
      const offset = (order.indexOf(id)-hubIndex)/Math.max(1,radius);
      return portrait ? [.5, .5 + offset * .33, 0] : [.5 + offset * .37, .5, 0];
    }
    if (!index) return [.5, .5, 0];
    if (params.topology === 'layers') {
      const upper = Math.ceil(n / 2), tier = index <= upper ? 0 : 1;
      const count = tier ? n - upper : upper, j = tier ? index - upper - 1 : index - 1;
      return [.2 + (j + .5) / Math.max(1,count) * .6, tier ? .74 : .26, 0];
    }
    // Mesh perturbation is deliberately bounded, planar and seed-pure.
    const angle = (index-1) / n * Math.PI * 2 - Math.PI / 2;
    const perturb = params.topology === 'mesh' ? (rng() - .5) * .028 : 0;
    return [.5 + Math.cos(angle) * (portrait ? .285 : .31) + perturb,
      .5 + Math.sin(angle) * .29 + perturb, 0];
  });
  const structural = [], add = (a,b) => {
    if (!structural.some(e => edgeKey(...e) === edgeKey(a,b))) structural.push([a,b]);
  };
  if (params.topology === 'chain') order.slice(1).forEach((id,i) => add(order[i], id));
  else if (params.topology === 'layers') {
    peripheral.forEach((id,i) => add(i < Math.ceil(n/2) ? 'hub' : peripheral[i % Math.ceil(n/2)], id));
  } else {
    peripheral.forEach(id => add('hub',id));
    if (params.topology === 'mesh' && n > 2) peripheral.forEach((id,i) => add(id,peripheral[(i+1)%n]));
  }
  const structuralKeys = new Set(structural.map(e => edgeKey(...e)));
  const jumps = [];
  path.slice(1).forEach((id,i) => {
    const edge = [path[i],id];
    if (!structuralKeys.has(edgeKey(...edge)) && !jumps.some(e => edgeKey(...e) === edgeKey(...edge))) jumps.push(edge);
  });
  // Keep all spanning links and all requested path links; optional mesh ring links
  // yield to jump links so the graph stays within sixteen displayed edges.
  while (structural.length + jumps.length > 16) {
    const index = structural.findLastIndex((edge,i) => i >= peripheral.length &&
      !path.slice(1).some((id,j) => edgeKey(path[j],id) === edgeKey(...edge)));
    if (index < 0) break;
    structural.splice(index,1);
  }
  const edges = [...structural,...jumps];
  const curves = edges.map(([a,b],i) => {
    const from = points[ids.indexOf(a)], to = points[ids.indexOf(b)];
    const others = points.filter((_,j) => ids[j]!==a && ids[j]!==b);
    const clear = curve => Array.from({length:47},(_,k) => curvePoint(curve,(k+1)/48))
      .every(p => others.every(o => Math.hypot(p[0]-o[0],p[1]-o[1]) > .047));
    const straight = [from,to];
    if (i < structural.length && clear(straight)) return straight;
    const dx=to[0]-from[0],dy=to[1]-from[1],length=Math.hypot(dx,dy)||1;
    let nx=dy/length,ny=-dx/length;
    if(ny>0){nx=-nx;ny=-ny;}
    // Perpendicular displacement also works for vertical diameters. Every
    // candidate is tested against unrelated nodes, not just against its chord.
    for(const distance of [.17,.24,.32,.42,.55])for(const sign of [1,-1]){
      const control=[Math.max(.055,Math.min(.945,(from[0]+to[0])/2+nx*distance*sign)),
        Math.max(.055,Math.min(.945,(from[1]+to[1])/2+ny*distance*sign)),0];
      const candidate=[from,control,to];
      if(clear(candidate))return candidate;
    }
    throw Error('graph_edge_cannot_avoid_node:'+a+'>'+b);
  });
  const route = path.slice(1).map((to,i) => {
    const from = path[i], edge = edges.findIndex(e => edgeKey(...e) === edgeKey(from,to));
    return {from,to,edge,reverse:edges[edge][0] !== from};
  });
  const labelNormals = ids.map((id,i) => {
    if (id === 'hub') return portrait && params.topology === 'chain' ? [-1,0] : [0,-1];
    if (params.topology === 'chain') return portrait ? [order.indexOf(id)%2 ? 1 : -1,0] : [0,order.indexOf(id)%2 ? 1 : -1];
    const [x,y] = points[i]; return [x-.5,y-.5];
  });
  return {ids,points,edges,curves,route,path,params,portrait,order,labelNormals,structuralCount:structural.length};
}

export function graphMoments(model) {
  const reveals = model.ids.slice(1).flatMap((_,i) => [.6+i*.11, .95+i*.11]);
  const lines = model.edges.map((_,i) => 1.8+i/Math.max(1,model.edges.length-1)*.35);
  const route = model.route.map((_,i) => 3.35+1.75*i/model.route.length);
  return [...new Set([0,.35,...reveals,...lines,2.8,...route,5.1,5.2])].sort((a,b) => a-b);
}
export function graphState(model, t, reduced = false) {
  t = Math.max(0,Math.min(6,t));
  const events = graphMoments(model);
  if (reduced) t = events.filter(x => x <= t + 1e-9).at(-1) ?? 0;
  const grow = (start,duration) => reduced ? +(t >= start) : smooth((t-start)/duration);
  const signal = clamp((t-3.35)/1.75), segment = Math.min(model.route.length-1,Math.floor(signal*model.route.length));
  return {t,
    nodeScale:model.ids.map((_,i) => grow(i ? .6+(i-1)*.11 : 0,.35)),
    edgeProgress:model.edges.map((_,i) => grow(1.8 + i/Math.max(1,model.edges.length-1)*.35,.65)),
    connected:t>=2.8, signal, segment, pulseVisible:t>=3.35&&t<5.1,
    segmentProgress:signal*model.route.length-segment,
    visited:model.path.filter((_,i) => t>=3.35+1.75*i/model.route.length-1e-9),
    routeProgress:model.route.map((_,i) => reduced ? +(t >= 3.35+1.75*(i+1)/model.route.length-1e-9) : clamp(signal*model.route.length-i)),
    terminal:grow(5.1,.1), finished:t>=5.2, orbit:0};
}

export function curvePoint(curve,t) {
  if(curve.length===2)return curve[0].map((value,i)=>value+(curve[1][i]-value)*t);
  return curve[0].map((value,i)=>(1-t)*(1-t)*value+2*(1-t)*t*curve[1][i]+t*t*curve[2][i]);
}
