export const clamp=x=>Math.max(0,Math.min(1,x));
export const smooth=x=>{x=clamp(x);return x*x*(3-2*x);};
export function random(seed){return()=>{let t=seed+=0x6D2B79F5;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return((t^t>>>14)>>>0)/4294967296;};}
export const moments=[0,1,2,3,3.75,4.5,5.25,6,6.7];
export function tokenModel(params) {
 if(params.mode==='overflow'&&params.capacity_ratio<=1)throw Error('overflow_requires_capacity_ratio_above_one');
 const rng=random(params.seed),count=params.token_count,capacity=Math.max(1,Math.floor(count/params.capacity_ratio));
 return {count,capacity,params,tokens:Array.from({length:count},(_,i)=>({size:.8+rng()*.3,arrival:1.7+(i/Math.max(1,count-1))*1.25+(i?(rng()-.5)*.035:0)}))};
}
export function tokenState(model,t,reduced=false) {
 t=Math.max(0,Math.min(7,t));
 if(reduced)t=moments.filter(x=>x<=t).at(-1)??0;
 const arrived=model.tokens.filter(x=>x.arrival<=t).length;
 const extra=Math.max(0,model.count-model.capacity);
 const expelled=model.params.mode==='overflow'?Math.min(extra,Math.floor(clamp((t-3)/2.25)*extra)):0;
 const generated=model.params.mode==='generate'?Math.floor(clamp((t-3)/2.25)*8):0;
 const stored=Math.min(model.capacity,arrived);
 return {t,arrived,stored,expelled,generated,full:arrived>=model.capacity,
 fraction:Math.min(1,arrived/model.capacity),
 tokens:model.tokens.map((x,i)=>({progress:clamp((t-(x.arrival-.7))/.7),size:x.size,hidden:model.params.mode==='fill'&&i>=model.capacity&&t>=x.arrival})),
 outputVisible:t>=4.5, countVisible:t>=1, settled:t>=6.7,
 phase: t<1?0:t<2?1:t<3?2:t<3.75?3:t<4.5?4:t<5.25?5:t<6?6:t<6.7?7:8,
 pull:reduced?0:smooth((t-6)/.7)};
}

export function tokenCell(capacity,i) {
 const depth=Math.min(4,Math.ceil(capacity/40)),rows=Math.ceil(capacity/(5*depth)),stepY=Math.min(.35,1.9/Math.max(1,rows-1));
 return [-.7+(i%5)*.35,-(rows-1)*stepY/2+(Math.floor(i/5)%rows)*stepY,-(depth-1)*.27/2+Math.floor(i/(5*rows))*.27];
}
