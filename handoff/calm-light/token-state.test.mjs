import test from 'node:test';
import assert from 'node:assert/strict';
import {tokenModel, tokenState, tokenCell, tokenGrid, moments} from './token-stream/state.js';

const params=(mode='overflow',token_count=80,capacity_ratio=1.5)=>({mode,token_count,capacity_ratio,seed:1});
for(const portrait of [false,true])for(const capacity of [8,12,24,53,80,160])test(`all ${capacity} capacity cells remain visible (${portrait?'portrait':'landscape'})`,()=>{
  const grid=tokenGrid(capacity,portrait);
  assert.equal(grid.columns,portrait?6:10);
  const cells=Array.from({length:capacity},(_,i)=>tokenCell(capacity,i,portrait));
  assert.equal(new Set(cells.map(p=>JSON.stringify(p))).size,capacity);
  for(const [x,y,z] of cells){
    assert.equal(z,0);assert.ok(x-grid.tileWidth/2>=grid.left);assert.ok(x+grid.tileWidth/2<=grid.right);
    assert.ok(y-grid.tileHeight/2>=grid.top);assert.ok(y+grid.tileHeight/2<=grid.bottom);
  }
  for(let i=0;i<capacity-1;i++){
    const a=cells[i],b=cells[i+1],mid=tokenCell(capacity,i+.5,portrait);
    assert.ok(Math.abs(a[0]-b[0])<1e-8||Math.abs(a[1]-b[1])<1e-8,'no diagonal row wrap');
    assert.ok(Math.abs(mid[0]-(a[0]+b[0])/2)<1e-8);
    assert.ok(Math.abs(mid[1]-(a[1]+b[1])/2)<1e-8);
  }
});

test('overflow is serial FIFO movement, not original-cell replacement',()=>{
  const model=tokenModel(params());
  for(let shifted=0;shifted<=model.extra;shifted++){
    const state=tokenState(model,3.6+shifted/model.extra*2.2);
    assert.equal(state.expelled,shifted);
    const retained=state.tokens.filter(token=>token.cell>=0&&token.cell<model.capacity);
    assert.equal(retained.length,model.capacity);
    retained.forEach((token,index)=>{assert.equal(token.index,index+shifted);assert.equal(token.cell,index);});
  }
  const half=tokenState(model,3.6+.5/model.extra*2.2);
  assert.ok(Math.abs(half.shift-.5)<1e-8);
  assert.equal(half.expelled,0);
  assert.ok(half.tokens[0].exiting);
  assert.ok(Math.abs(half.tokens[1].cell-.5)<1e-8);
  assert.ok(Math.abs(half.tokens[model.capacity].cell-(model.capacity-.5))<1e-8);
});

test('fill keeps all surplus input visible in a hollow queue',()=>{
  const model=tokenModel(params('fill'));
  const state=tokenState(model,7);
  assert.equal(state.stored,model.capacity);assert.equal(state.waiting,model.extra);
  assert.equal(state.tokens.filter(token=>token.queued).length,model.extra);
  assert.ok(state.tokens.every(token=>token.hidden===false));
  assert.equal(state.inspected,model.capacity);assert.equal(state.expelled,0);
});

test('partial windows do not claim full and generate never discards input',()=>{
  for(const mode of ['fill','generate']){
    const model=tokenModel(params(mode,80,.5)),state=tokenState(model,7);
    assert.equal(model.capacity,160);assert.equal(state.stored,80);assert.equal(state.fraction,.5);
    assert.equal(state.full,false);assert.equal(state.expelled,0);assert.equal(state.waiting,0);
    assert.equal(state.generated,mode==='generate'?8:0);
  }
});

test('time purity, reduced motion and a real terminal result cover long stretch',()=>{
  for(const mode of ['fill','overflow','generate']){
    const model=tokenModel(params(mode));
    for(const reduced of [false,true])for(const t of [0,1,2,3,3.6,4.713,5.8,5.9,7]){
      const state=tokenState(model,t,reduced);
      tokenState(model,7,reduced);tokenState(model,1,reduced);
      assert.deepEqual(tokenState(model,t,reduced),state);
      assert.equal(state.pull,0);assert.ok(state.stored<=model.capacity);
    }
    const end=tokenState(model,5.9);assert.equal(end.result,true);
    assert.ok(end.tokens.every(token=>!token.exiting));
  }
  const landmarks=[...moments,7];
  landmarks.forEach((t,i)=>{if(i)assert.ok((t-landmarks[i-1])*12/7<=2);});
});

test('single-extra FIFO exit shares the shift clock and counted departure',()=>{
 const model=tokenModel(params('overflow',12,1.01));assert.equal(model.extra,1);
 for(const t of [3.6,3.8,4.05,4.7,5.5,5.8]){const s=tokenState(model,t);assert.equal(s.tokens[0].exitProgress,Math.min(1,s.shift));assert.equal(s.expelled,Math.floor(s.shift+1e-9));}
});

test('reduced motion presents completed FIFO and output states only',()=>{
 for(const mode of ['fill','overflow','generate']){const model=tokenModel(params(mode));for(const time of [1,2,3.6,4.75,5.9]){const s=tokenState(model,time,true);assert.ok(Number.isInteger(s.shift));assert.ok(s.tokens.every(t=>[0,1].includes(t.progress)&&[0,1].includes(t.exitProgress)));assert.ok(s.outputs.every(t=>[0,1].includes(t.progress)));}}
});
