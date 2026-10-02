import {THREE, sceneKit} from './scene.js';
import {tokenModel, tokenState, tokenCell, tokenGrid, moments, clamp} from './state.js';

export async function mount(options) {
  if (!globalThis.HarnessBroll) throw Error('Load frozen runtime/appearance.js and runtime/broll.js first');
  const response = await fetch(new URL('./asset.json', import.meta.url), {redirect:'error'});
  if (!response.ok) throw Error('token_manifest_missing');
  const metadata = await response.json();
  if (!Number.isSafeInteger(options.slots?.counter) || options.slots.counter <= 0) throw Error('token_counter_requires_positive_safe_integer');
  return HarnessBroll.mount(metadata, {...options, slots:{output_label:'', ...options.slots}}, build);
}

function build(context) {
  const {slots, params, start} = context, model = tokenModel(params), kit = sceneKit(context);
  try {
    const {scene, own, mat, palette, portrait} = kit;
    const grid = tokenGrid(model.capacity, portrait), cell = index => tokenCell(model.capacity, index, portrait);
    const square = own(new THREE.PlaneGeometry(1, 1));
    const borderShape = new THREE.Shape();
    borderShape.moveTo(-.5,-.5); borderShape.lineTo(.5,-.5); borderShape.lineTo(.5,.5); borderShape.lineTo(-.5,.5); borderShape.closePath();
    const hole = new THREE.Path();
    hole.moveTo(-.39,-.39); hole.lineTo(-.39,.39); hole.lineTo(.39,.39); hole.lineTo(.39,-.39); hole.closePath();
    borderShape.holes.push(hole);
    const hollow = own(new THREE.ShapeGeometry(borderShape));
    const instanced = (geometry, color, count, extra={}) => {
      const mesh = new THREE.InstancedMesh(geometry, mat(color, extra), count);
      mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage); mesh.frustumCulled = false; scene.add(mesh); return mesh;
    };
    const capacityCells = instanced(hollow, palette.muted, model.capacity, {transparent:true,opacity:.5});
    const blocks = instanced(square, palette.main, model.count);
    const queue = instanced(hollow, palette.main, model.count);
    const checked = instanced(hollow, palette.main, model.capacity);
    const output = instanced(square, palette.accent, 8);
    const exits = Array.from({length:model.extra}, () => {
      const mesh = new THREE.Mesh(hollow, mat(palette.muted, {transparent:true,opacity:0,depthWrite:false}));
      mesh.visible = false; scene.add(mesh); return mesh;
    });
    const dummy = new THREE.Object3D();
    function matrix(mesh, index, position, width, height, visible=true, z=.01) {
      dummy.position.set(position[0],position[1],z); dummy.rotation.set(0,0,0);
      dummy.scale.set(visible?width:0, visible?height:0, 1); dummy.updateMatrix(); mesh.setMatrixAt(index,dummy.matrix);
    }
    const plane = (color, opacity=1) => {
      const mesh = new THREE.Mesh(square,mat(color,{transparent:opacity<1,opacity})); scene.add(mesh); return mesh;
    };
    function rect(mesh,left,top,width,height,z=0) {mesh.position.set(left+width/2,top+height/2,z);mesh.scale.set(width,height,1);}
    // The capacity bar is tied to the window itself. It never uses accent,
    // which is reserved exclusively for newly generated output.
    const capacityTrack=plane(palette.muted,.35), capacityFill=plane(palette.main);
    const barY=grid.bottom+.016;
    const frameEdges=Array.from({length:4},()=>plane(palette.main,.58));
    rect(frameEdges[0],grid.left-.014,grid.top-.018,grid.right-grid.left+.028,.002);
    rect(frameEdges[1],grid.left-.014,grid.bottom+.004,grid.right-grid.left+.028,.002);
    rect(frameEdges[2],grid.left-.014,grid.top-.018,.0015,grid.bottom-grid.top+.024);
    rect(frameEdges[3],grid.right+.0125,grid.top-.018,.0015,grid.bottom-grid.top+.024);
    const channel=plane(palette.muted,.45);
    if(portrait)rect(channel,.498,.21,.004,.059);else rect(channel,.16,.492,.075,.003);
    const origin=portrait?[.5,.19,0]:[.17,.493,0];
    const queueCell=index=>portrait?[.14+(index%9)*.09,.135+Math.floor(index/9)*.028,0]:[.062+(index%4)*.037,.35+Math.floor(index/4)*.051,0];
    const queueSize=portrait?[.041,.018]:[.023,.037];
    const outCell=index=>portrait?[.19+index*.088,.88,0]:[.824+(index%2)*.064,.355+Math.floor(index/2)*.087,0];
    const outputSize=portrait?[.048,.03]:[.038,.061];
    const exitEnd=portrait?[.5,.88,0]:[.868,.55,0];
    const mix=(a,b,p)=>a.map((v,i)=>v+(b[i]-v)*p);
    const through=(points,p)=>{const f=clamp(p)*(points.length-1),i=Math.min(points.length-2,Math.floor(f));return mix(points[i],points[i+1],f-i);};
    const labels={
      input_label:kit.label('input_label',slots.input_label,'text'),
      box_label:kit.label('box_label',slots.box_label),
      output_label:kit.label('output_label',slots.output_label,'text'),
      counter:kit.label('counter',slots.counter,'text')
    };
    labels.box_label.style.fontWeight='700';
    const usage=kit.label('usage','','text'), cellCount=kit.label('cell-count','','text');
    const branch=kit.label('mode-state','','text'), result=kit.label('result','','text');
    const destination=kit.label('destination',params.mode==='overflow'?'已移出':'生成序列','text');
    const prefix=context.stage.ownerDocument.createElement('span'), units=context.stage.ownerDocument.createElement('span');
    units.textContent=' token（示意）';
    prefix.style.flexShrink=units.style.flexShrink='0';
    usage.append(prefix,labels.counter,units);
    usage.style.display='flex'; usage.style.alignItems='baseline'; usage.style.gap='0';
    // HarnessBroll validates the original raw slot before the first renderAt.
    // The slot remains an independent connected text-layer element in one
    // visually joined, fully qualified line. Formatting starts on renderAt.
    function inlineCounter(){Object.assign(labels.counter.style,{position:'static',transform:'none',padding:'0',border:'0',borderRadius:'0',minHeight:'1em',maxWidth:'none',background:'transparent',fontSize:'inherit',fontFamily:'inherit',lineHeight:'inherit',flexShrink:'0'});}
    inlineCounter();
    const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
    const format=value=>value.toLocaleString('en-US');

    function renderAt(t,globalTime) {
      const s=tokenState(model,t,reduced); kit.pose();kit.visible(globalTime>=start);inlineCounter();
      // All declared capacity cells exist, including the unoccupied half at
      // capacity_ratio=.5. A small z offset only separates ink layers.
      for(let i=0;i<model.capacity;i++) {
        matrix(capacityCells,i,cell(i),grid.tileWidth,grid.tileHeight,true,0);
        matrix(checked,i,cell(i),grid.tileWidth*1.1,grid.tileHeight*1.1,params.mode==='fill'&&i<s.inspected,.018);
      }
      model.tokens.forEach((token,i)=>{
        const state=s.tokens[i]; let position=cell(Math.min(i,model.capacity-1)),solid=false,outline=false,width=grid.tileWidth*.76,height=grid.tileHeight*.76;
        if(!state.started){/* The matrix is explicitly hidden on backward seeks. */}
        else if(!state.arrived) {
          const target=i<model.capacity?cell(i):queueCell(i-model.capacity);
          position=mix(origin,target,state.progress);solid=i<model.capacity;outline=!solid;
          if(outline){width=queueSize[0];height=queueSize[1];}
        } else if(i<model.capacity && params.mode!=='overflow') {position=cell(i);solid=true;}
        else if(params.mode==='overflow' && state.cell>=0 && state.cell<model.capacity) {
          // Incoming tail tile and outgoing head tile both follow the same
          // fractional shift. Retained tiles never get replaced in place.
          if(state.cell>model.capacity-1)position=mix(queueCell(0),cell(model.capacity-1),model.capacity-state.cell);
          else position=cell(state.cell);
          solid=true;
        } else if(state.queued || (params.mode!=='overflow'&&i>=model.capacity)) {
          const queueIndex=params.mode==='overflow'?Math.max(0,i-model.capacity-s.shift):i-model.capacity;
          const low=Math.floor(queueIndex),high=Math.ceil(queueIndex);
          position=mix(queueCell(low),queueCell(high),queueIndex-low);outline=true;
          width=queueSize[0];height=queueSize[1];
          // Fill mode advances the waiting line gently to its stop, while the
          // window inspection makes available/occupied capacity legible.
          if(params.mode==='fill')position[portrait?1:0]+=.012*s.action;
        }
        matrix(blocks,i,position,width,height,solid);
        matrix(queue,i,position,width,height,outline);
        if(i<exits.length){
          const spill=exits[i],p=state.exitProgress;
          spill.visible=params.mode==='overflow'&&p>0&&p<1;
          // A hollow, muted token leaves the oldest cell, then fades. There is
          // no falling physics, random angle or interchangeable replacement.
          const route=portrait?[cell(0),[.945,.285,0],[.945,.865,0],exitEnd]:[cell(0),[.78,.258,0],[.867,.35,0],exitEnd];
          const point=through(route,p);spill.position.set(point[0],point[1],.022);
          spill.scale.set(grid.tileWidth*.76,grid.tileHeight*.76,1);spill.rotation.set(0,0,0);spill.material.opacity=(1-p)*.9;
        }
      });
      const tail=cell(Math.max(0,s.stored-1));
      s.outputs.forEach(token=>{
        const destination=outCell(token.index),p=token.progress;
        const route=portrait?[tail,[.936,.72,0],[destination[0],.81,0],destination]:[tail,[.78,.752,0],[destination[0],.752,0],destination];
        matrix(output,token.index,through(route,p),outputSize[0],outputSize[1],token.started,.024);
      });
      for(const mesh of [capacityCells,blocks,queue,checked,output])mesh.instanceMatrix.needsUpdate=true;
      rect(capacityTrack,grid.left,barY,grid.right-grid.left,.008,.002);
      rect(capacityFill,grid.left,barY,(grid.right-grid.left)*s.fraction,.008,.004);
      // Capacity emphasis is neutral and resolves before the action begins.
      frameEdges.forEach(mesh=>mesh.material.opacity=s.t>=3&&s.t<3.6?.95:.58);
      prefix.textContent=`约用 ${format(Math.round(s.fraction*slots.counter))} / `;
      labels.counter.textContent=format(slots.counter);
      cellCount.textContent=s.stored?`保留 #${s.expelled+1}–#${s.expelled+s.stored} · ${s.stored} / ${model.capacity} 格`:`已用 0 / ${model.capacity} 格`;
      branch.textContent=params.mode==='overflow'?`已移出 ${s.expelled} 格`:
        params.mode==='generate'?`已生成 ${s.generated} 格`:`容量检查 ${s.inspected} / ${model.capacity} 格${s.waiting?' · 待入 '+s.waiting+' 格':''}`;
      result.textContent=params.mode==='overflow'?`保留最新 ${s.stored} 格 · 移出最早 ${s.expelled} 格`:
        params.mode==='generate'?`保留 ${s.stored} 格 · 生成 ${s.generated} 格${s.waiting?' · 待入 '+s.waiting+' 格':''}`:
        `保留 ${s.stored} 格 · ${s.waiting?'待入 '+s.waiting:'可用 '+(model.capacity-s.stored)} 格`;
      const placements=portrait?[
        [labels.input_label,.5,.066,true],[labels.box_label,.5,.254,true],
        [usage,.5,.772,true],[cellCount,.5,.724,true],
        [labels.output_label,.5,.827,params.mode==='generate'&&!!slots.output_label],
        [destination,.5,.827,params.mode==='overflow'||(params.mode==='generate'&&!slots.output_label)],
        [branch,.5,params.mode==='fill'?.866:.929,s.t>=3.6&&!s.result],
        [result,.5,.959,s.result]
      ]:[
        [labels.input_label,.125,.234,true],[labels.box_label,.5,.182,true],
        [usage,.5,.864,true],[cellCount,.5,.794,true],
        [labels.output_label,.87,.234,params.mode==='generate'&&!!slots.output_label],
        [destination,.87,.234,params.mode==='overflow'||(params.mode==='generate'&&!slots.output_label)],
        [branch,params.mode==='fill'?.5:.867,params.mode==='fill'?.94:.754,s.t>=3.6&&!s.result],
        [result,.5,.952,s.result]
      ];
      placements.forEach(([element,x,y,show])=>kit.place(element,[x,y,0],show));
      // Do not solve independently per frame: fixed semantic regions make
      // the composite counter stable even as its number of digits changes.
      if(usage.scrollWidth>kit.width*.96)throw Error('token_usage_line_capacity');
      kit.draw();
    }
    return {renderAt,labels,events:moments.map(time=>({time,target:time===5.9?result:time>=3.6?branch:kit.renderer.domElement})),dispose:kit.dispose};
  } catch(error) {kit.dispose();throw error;}
}
