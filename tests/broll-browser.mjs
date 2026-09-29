// PLAYWRIGHT_PACKAGE=/path/to/playwright CHROME_PATH=/path/to/chromium node tests/broll-browser.mjs
// Isolated B-roll browser pipeline: real pack -> accept -> resolve -> materialize
// -> install -> verify, then an offline store and a served project closure.
// No production assets, Studio acceptance records, Work or video output.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import http from 'node:http';
import { createRequire } from 'node:module';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const require = createRequire(process.env.PLAYWRIGHT_PACKAGE ? path.join(process.env.PLAYWRIGHT_PACKAGE, 'package.json') : import.meta.url);
const { chromium } = require('playwright');

import {inspectRhythmFrame} from '../.studio/visual_probe.mjs';

const output = await fs.mkdtemp(path.join(os.tmpdir(), 'hf-broll-'));
const checks = [];
const record = (name, passed, detail = '') => checks.push({ name, passed, detail });

const PY_BUILD = String.raw`
import json, os, pathlib, shutil, sys
sys.path.insert(0, str(pathlib.Path(sys.argv[1]) / '.studio'))
import asset_store as store, appearance

repo = pathlib.Path(sys.argv[1])
root = pathlib.Path(sys.argv[2])
font = sys.argv[3]
license_file = sys.argv[4]
harness = root / 'harness'
harness.mkdir()
shutil.copyfile(repo / 'windows-runtime.lock.json', harness / 'windows-runtime.lock.json')
assets = root / 'store'
os.environ.update(HYPERFRAMES_AI_ASSET_CONFIG=str(root / 'config.json'), HYPERFRAMES_AI_ROOT=str(harness), HYPERFRAMES_AI_ASSET_ROOT='')
store.configure_asset_store(harness, assets)

def accept(source):
    candidate = store.pack_source(assets, source)
    store.accept_component(assets, candidate['component_ref'], candidate['package_sha256'], 'Isolated B-roll browser fixture', runtime_root=harness)
    return {'ref': candidate['component_ref'], 'kind': json.loads((source / 'asset.json').read_text())['kind'], 'package_sha256': candidate['package_sha256']}

shots = {}
for name, timing in (('stretch', 'stretch'), ('hold', 'hold-end')):
    source = root / ('src-' + name)
    source.mkdir()
    for fixture_file in ('asset.json', 'main.js', 'USAGE.md'):
        shutil.copyfile(repo / 'tests/fixtures/broll-sample' / fixture_file, source / fixture_file)
    manifest = json.loads((source / 'asset.json').read_text())
    if timing == 'hold-end':
        manifest['id'] = 'synthetic-broll-hold'
        manifest['broll']['timing'] = 'hold-end'
        manifest['broll']['duration'] = {'min': 3, 'max': 6, 'default': 3}
        (source / 'asset.json').write_text(json.dumps(manifest))
    shots[name] = accept(source)

themes = {}
for name, accent, family in (('theme-a', '#c12655', 'Fixture Chinese A'), ('theme-b', '#167340', 'Fixture Chinese B')):
    source = root / name
    source.mkdir()
    shutil.copyfile(font, source / 'local.otf')
    shutil.copyfile(license_file, source / 'LICENSE.txt')
    payload = {'tokens': {'typography': {'body': '"' + family + '", serif'}, 'colors': {'text': '#17272c', 'accent': accent}, 'surface': {'color': '#ffffff'}},
               'fonts': [{'family': family, 'path': 'local.otf', 'license': 'LICENSE.txt', 'style': 'normal', 'weight': 400}]}
    (source / 'asset.json').write_text(json.dumps({'schema_version': 2, 'id': name, 'version': 1, 'kind': 'theme', 'entry': 'entry.json',
                                                   'contract_version': 1, 'parameters': {}, 'compatibility': {}, 'dependencies': ['local.otf', 'LICENSE.txt']}))
    (source / 'entry.json').write_text(json.dumps(payload))
    themes[name] = accept(source)

source = root / 'background'
source.mkdir()
(source / 'asset.json').write_text(json.dumps({'schema_version': 2, 'id': 'background', 'version': 1, 'kind': 'background', 'entry': 'entry.json', 'contract_version': 1, 'parameters': {}, 'compatibility': {}}))
(source / 'entry.json').write_text(json.dumps({'renderer': 'solid', 'parameters': {'color': '#e0e8ec'}}))
background = accept(source)

from component_harness import install_component, parse_component_ref, verify_installation
import icon_sets
npm = root / 'synthetic-npm'; (npm / 'icons').mkdir(parents=True)
(npm / 'package.json').write_text(json.dumps({'name':'lucide-static','version':'1.45.0','license':'ISC'}))
(npm / 'LICENSE').write_text('Synthetic fixture ISC license text')
svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M1 2 L3 4"/></svg>'
(npm / 'icons/test-shape.svg').write_text(svg)
icon_source = root / 'icon-source'; icon_sets.import_lucide(npm, icon_source)
icon_ref = accept(icon_source)
media_source = root / 'media-source'; media_source.mkdir()
(media_source / 'asset.json').write_text(json.dumps({'schema_version':2,'id':'synthetic-media','version':1,'kind':'media',
    'entry':'shape.svg','contract_version':1,'parameters':{},'compatibility':{}}))
(media_source / 'shape.svg').write_text(svg)
media_ref = accept(media_source)

configs = [
    {'name': 'desktop-stretch', 'ratio': '16:9', 'theme': 'theme-a', 'shot': 'stretch', 'start': 1.0, 'end': 5.5},
    {'name': 'mobile-stretch', 'ratio': '9:16', 'theme': 'theme-b', 'shot': 'stretch', 'start': 1.0, 'end': 5.5},
    {'name': 'desktop-hold', 'ratio': '16:9', 'theme': 'theme-a', 'shot': 'hold', 'start': 1.0, 'end': 7.0},
    {'name': 'mobile-hold', 'ratio': '9:16', 'theme': 'theme-b', 'shot': 'hold', 'start': 1.0, 'end': 7.0},
]
for cfg in configs:
    project = root / ('project-' + cfg['name'])
    project.mkdir()
    account = {'id': 'fixture', 'revision': 1, 'theme': themes[cfg['theme']], 'background': background, 'ratio': cfg['ratio'], 'motion': {}}
    lock = appearance.resolve(harness, account)
    appearance.materialize(harness, project, lock)
    item = store.resolve_asset_closure(harness, [shots[cfg['shot']]])[0]
    identity, version = parse_component_ref(item['ref'])
    binding = {'schema_version': 3, 'component_ref': item['ref'], 'scene': 'S01', 'usage': {'role': 'auxiliary', 'required': True}}
    install_component(pathlib.Path(item['path']), project, binding,
                      binding_path='component-bindings/broll.' + identity + '.v' + str(version) + '.json',
                      expected_ref=item['ref'], acceptance=item['acceptance'])
    cfg['module'] = 'vendor/components/' + identity + '/v' + str(version) + '/main.js'
    (project / 'project-config.json').write_text(json.dumps({'snapshot_dependencies': [cfg['module']]}))
    for ref in (icon_ref, media_ref):
        item = store.resolve_asset_closure(harness, [ref])[0]
        binding = {'schema_version':3,'component_ref':item['ref'],'usage':{'role':ref['kind'] if ref['kind']=='icon-set' else 'auxiliary','required':True}}
        if ref['kind'] == 'media': binding['scene'] = 'S01'
        install_component(pathlib.Path(item['path']),project,binding,acceptance=item['acceptance'])
    icon_sets.use_icon(icon_sets.project_packages(project),'lucide:test-shape@1.45.0',project,'assets/test.svg')
    used = (project/'assets/test.svg').read_text()
    (project/'assets/bad.svg').write_text(used.replace('M1 2','M9 9'))
    (project/'assets/styled.svg').write_text(used.replace('style="','style="display:none;'))

(root / 'build.json').write_text(json.dumps({'configs': configs}))
shutil.rmtree(assets)
print('built')
`;

const build = spawnSync('python3', ['-c', PY_BUILD, repo, output,
  process.env.TEST_CHINESE_FONT || '/usr/share/fonts/opentype/unifont/unifont.otf',
  process.env.TEST_CHINESE_FONT_LICENSE || '/usr/share/doc/fonts-unifont/copyright'], { encoding: 'utf8' });
assert.equal(build.status, 0, build.stderr);

const built = JSON.parse(await fs.readFile(path.join(output, 'build.json'), 'utf8'));
const KEY_MOMENTS = [0, 0.75, 1.5, 2.25];

const pageHtml = moduleUrl => `<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
html,body{margin:0;height:100%;overflow:hidden}
#background{position:absolute;inset:0}
#stage[data-hf-layer],#text[data-hf-layer]{position:absolute;inset:0}
#text[data-hf-layer]{pointer-events:none}
#aText{position:absolute;left:4%;top:4%;color:#17272c;font:16px sans-serif}
#caption{position:absolute;left:0;right:0;bottom:0;height:16%;background:rgba(255,255,255,.92);z-index:9}
</style>
<div id="background" data-hf-layer="background"></div><div id="stage" data-hf-layer="stage"></div>
<div id="text" data-hf-layer="text"></div>
<div id="aText" data-hf-layer="text"><span id="aItem">A</span></div>
<div id="caption">caption</div>
<img hidden src="vendor/components/synthetic-media/v1/shape.svg"><img hidden src="assets/test.svg">
<script src="runtime/appearance.js"></script>
<script src="runtime/rolls.js"></script>
<script src="runtime/broll.js"></script>
<script>
const stage=document.getElementById('stage'), text=document.getElementById('text');
const aText=document.getElementById('aText'), aItem=document.getElementById('aItem');
const SHOT_MODULE=${JSON.stringify('./' + moduleUrl)};
window.__ready = HarnessAppearance.load().then(a => { window.__appearance=a; HarnessAppearance.apply(document.getElementById('background'),a); HarnessAppearance.apply(stage,a); return a; });
window.__mountShot = async (slots, extra) => {
  const a = await window.__ready;
  const mod = await import(SHOT_MODULE);
  window.__shot = await mod.mount(Object.assign({stage, text, appearance:a, slots, params:{}, startCue:1, endCue:4, cues:{}}, extra || {}));
  return true;
};
window.__seek = t => { window.__shot.renderAt(t); return stage.innerHTML + '|' + text.innerHTML; };
window.__baseline = () => ({children: stage.children.length + text.children.length, sources: (window.__hfRhythmSources || new Set()).size});
window.__style = () => { const [t,v]=text.querySelector('[data-broll-caption]').children, ct=getComputedStyle(t), cv=getComputedStyle(v);
  return {titleColor:ct.color, titleFont:ct.fontFamily, valueColor:cv.color}; };
window.__layout = () => { const st=stage.getBoundingClientRect(), [title,value]=text.querySelector('[data-broll-caption]').children;
  const tr=title.getBoundingClientRect(), vr=value.getBoundingClientRect(), fr=stage.querySelector('[data-broll-frame]').getBoundingClientRect();
  return {stageWidth:st.width, stageHeight:st.height, frameWidth:fr.width, frameBottom:fr.bottom,
    viewportHeight:innerHeight, titleBottom:tr.bottom, valueBottom:vr.bottom,
    title:{len:[...title.textContent].length, client:title.clientWidth, scroll:title.scrollWidth, height:title.clientHeight},
    value:{len:[...value.textContent].length, client:value.clientWidth, scroll:value.scrollWidth, height:value.clientHeight}}; };
window.__caption = () => { const h=innerHeight, w=innerWidth, y=Math.round(h*0.9), hits=[];
  for (let i=1;i<=5;i++) { const x=Math.round(w*i/6);
    for (const el of document.elementsFromPoint(x,y)) if ((stage.contains(el)||text.contains(el)) && el!==stage && el!==text) hits.push(el.tagName); }
  return hits; };
window.__rhythm = () => { const out=[];
  for (const sourceSrc of (window.__hfRhythmSources || [])) for (const e of sourceSrc()) {
    if (e.kind !== 'broll_moment') continue;
    const n=e.target, s=getComputedStyle(n), b=n.getBoundingClientRect();
    out.push({time:e.time, kind:e.kind, layer:n.closest('[data-hf-layer]')?.dataset.hfLayer || null, connected:n.isConnected,
      visibility:s.visibility, display:s.display, opacity:Number(s.opacity), width:b.width, height:b.height, text:(n.textContent||'').slice(0,24)});
  }
  return out; };
window.__raw = (broll, options) => HarnessBroll.mount({kind:'module', parameters:{}, compatibility:{ratios:['9:16','16:9']}, broll}, options, () => ({renderAt(){}, events:[], labels:{}}));
window.__closureSlots = async () => {
  const a=await __ready;
  const contract={duration:{min:2,max:6,default:3},timing:'stretch',caption_safe_zone:{[a.lock.ratio]:[0,.84,1,.16]},
    slots:{icon:{type:'icon'},media:{type:'media'}},params:{'style.amount':{type:'number',default:1,minimum:0,maximum:2}},carries_info:false,sfx_cues:[]};
  const options={stage,appearance:a,startCue:1,endCue:4,slots:{icon:{ref:'lucide:test-shape@1.45.0',path:'assets/test.svg'},media:'vendor/components/synthetic-media/v1/shape.svg'},params:{'style.amount':1.5}};
  let received;
  const build=ctx=>{received=ctx;return{renderAt(){},events:[],dispose(){}};};
  const mount=opts=>HarnessBroll.mount({broll:contract},opts,build);
  const result=await mount(options);
  const valid=received.slots.media.endsWith('/vendor/components/synthetic-media/v1/shape.svg') && received.slots.icon.svg.includes('data-icon="lucide:test-shape@1.45.0"') && received.params['style.amount']===1.5;
  result.dispose();
  const failures=[];
  for (const change of [opts=>opts.slots.icon.path='assets/bad.svg',opts=>opts.slots.icon.ref='lucide:missing@1.45.0',opts=>opts.params['style.amount']=3,opts=>opts.params['style.amount']=true]) {
    const opts=structuredClone({slots:options.slots,params:options.params});change(opts);
    try {const shot=await mount({...options,...opts});shot.dispose();failures.push(false);}catch{failures.push(true);}
  }
  const styled=await mount({...options,slots:{...options.slots,icon:{...options.slots.icon,path:'assets/styled.svg'}}});
  const canonical=!received.slots.icon.svg.includes('display:none');styled.dispose();
  return {valid,failures,canonical};
};
window.__rejects = async () => {
  const a = await window.__ready;
  const zone = {}; zone[a.lock.ratio] = [0,0.84,1,0.16];
  const slots = base => Object.assign({title:{type:'text',layer:'text',max_chars:12}, value:{type:'number',layer:'text',max_chars:8}}, base||{});
  const broll = base => ({role:'concept', takeover:'inline', duration:{min:2,max:6,default:3}, timing:'stretch', key_moments:[0,1.5], sfx_cues:[{time:0,purpose:'x'}], slots:slots(base), params:{}, carries_info:true, caption_safe_zone:zone, usage:'mount', examples:['mount']});
  const opts = extra => Object.assign({stage, text, appearance:a, params:{}, startCue:1, endCue:4, cues:{}}, extra||{});
  const cases = [
    ['slot_type', broll(), opts({slots:{title:42, value:1}}), 'broll_slot_type'],
    ['slot_capacity', broll(), opts({slots:{title:'x'.repeat(13), value:1}}), 'broll_slot_capacity'],
    ['number_infinite', broll(), opts({slots:{title:'ok', value:Infinity}}), 'broll_slot_type'],
    ['duration_range', broll(), opts({startCue:0, endCue:1, slots:{title:'ok', value:1}}), 'broll_duration_outside_range'],
    ['media_url', broll({media:{type:'media'}}), opts({slots:{title:'ok', value:1, media:'https://example.invalid/x.png'}}), 'broll_path_requires_project_closure'],
    ['media_traversal', broll({media:{type:'media'}}), opts({slots:{title:'ok', value:1, media:'../../etc/passwd'}}), 'broll_path_requires_project_closure'],
    ['media_unregistered', broll({media:{type:'media'}}), opts({slots:{title:'ok', value:1, media:'media/clip.png'}}), 'broll_media_outside_closure'],
    ['icon_ref', broll({icon:{type:'icon'}}), opts({slots:{title:'ok', value:1, icon:{ref:'lucide:plug@1.45', path:'icons/plug.svg'}}}), 'broll_icon_requires_exact_reference']
  ];
  const results = [];
  for (const [name, meta, options, expected] of cases) {
    try { await window.__raw(meta, options); results.push([name, false, 'no error']); }
    catch (e) { results.push([name, String(e.message).includes(expected), String(e.message)]); }
  }
  return results;
};
window.__failedMount = async () => {
  const before = window.__baseline();
  const beforeStage = stage.children.length;
  let message = '';
  try { await window.__mountShot({title:'x'.repeat(13), value:1}, {startCue:1, endCue:4}); }
  catch (e) { message = e.message; }
  return {message, before, after: window.__baseline(), stageChildren: stage.children.length, beforeStage};
};
window.__rolls = async ({start,end}) => {
  const cues = {find: n => ({a0:0, a1:end+1, b0:start, b1:end}[n])};
  const rolls = HarnessRolls.mount({cues, scenes:[{id:'b', startCue:'a0', endCue:'a1',
    a:{text:aText, items:[{id:'a1', element:aItem, cue:'a0'}]},
    b:[{startCue:'b0', endCue:'b1', retreat:'hide', media:stage, text}]}]});
  const read = () => ({stage:getComputedStyle(stage).visibility, text:getComputedStyle(text).visibility,
    frame:getComputedStyle(stage.querySelector('[data-broll-frame]')).visibility,
    caption:getComputedStyle(text.querySelector('[data-broll-caption]')).visibility});
  window.__shot.renderAt(start+.5); await rolls.renderAt(start+.5); const inside = read();
  window.__shot.renderAt(end+.5); await rolls.renderAt(end+.5); const outside = read();
  await rolls.renderAt(0.5); const before = read();
  rolls.dispose();
  return {inside, outside, before};
};
</script>`;

for (const cfg of built.configs) await fs.writeFile(path.join(output, `project-${cfg.name}`, 'index.html'), pageHtml(cfg.module));
const verify = spawnSync('python3', ['-c', `import pathlib,sys
sys.path.insert(0,str(pathlib.Path(sys.argv[1])/'.studio'))
from component_harness import verify_installation
for project in pathlib.Path(sys.argv[2]).glob('project-*'): verify_installation(project)
`, repo, output], {encoding: 'utf8'});
assert.equal(verify.status, 0, verify.stderr);

const server = http.createServer(async (request, response) => {
  try {
    const relative = decodeURIComponent(new URL(request.url, 'http://localhost').pathname).slice(1);
    assert(relative && !relative.split('/').includes('..'));
    const data = await fs.readFile(path.join(output, relative));
    response.setHeader('Content-Type', relative.endsWith('.js') ? 'application/javascript' : relative.endsWith('.json') ? 'application/json' : relative.endsWith('.otf') ? 'font/otf' : relative.endsWith('.md') ? 'text/markdown' : 'text/html');
    response.end(data);
  } catch { response.writeHead(404); response.end(); }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
let browser;
try {
  browser = await chromium.launch({ headless: true, ...(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {}) });
  const errors = [];
  const styles = {};

  for (const cfg of built.configs) {
    const stretch = cfg.shot === 'stretch';
    const scale = stretch ? (cfg.end - cfg.start) / 3 : 1;
    const expected = KEY_MOMENTS.map(t => cfg.start + t * scale);
    const viewport = cfg.ratio === '16:9' ? { width: 1280, height: 720 } : { width: 390, height: 844 };
    const page = await browser.newPage({ viewport });
    page.on('pageerror', error => errors.push(`${cfg.name}: ${error.message}`));
    await page.goto(`http://127.0.0.1:${server.address().port}/project-${cfg.name}/index.html`);
    await page.evaluate(() => window.__ready);

    await page.evaluate(extra => window.__mountShot({title:String.fromCodePoint(0x4e2d).repeat(12),value:12345678},extra), {startCue:cfg.start,endCue:cfg.end});
    const maximum=await page.evaluate(()=>window.__layout());
    record(`${cfg.name}: frozen font fits maximum Chinese slots`, maximum.title.scroll<=maximum.title.client+1 && maximum.value.scroll<=maximum.value.client+1);
    await page.evaluate(()=>window.__shot.dispose());

    await page.evaluate(extra => window.__mountShot({ title: 'Broll signal', value: 42 }, extra), { startCue: cfg.start, endCue: cfg.end });
    const moments = await page.evaluate(() => window.__shot.moments());
    const mapped = moments.key_moments.map(value => Math.round(value * 1000) / 1000);
    record(`${cfg.name}: moments mapped`, JSON.stringify(mapped) === JSON.stringify(expected), JSON.stringify(mapped));

    const unique = [...new Set([...expected, cfg.end - 0.5, cfg.start])];
    const forward = {};
    for (const t of unique) forward[t] = await page.evaluate(time => window.__seek(time), t);
    await page.evaluate(time => window.__seek(time), unique[unique.length - 1]);
    const backward = {};
    for (const t of [...unique].reverse()) backward[t] = await page.evaluate(time => window.__seek(time), t);
    const pure = unique.every(t => forward[t] === backward[t]);
    record(`${cfg.name}: forward/direct/back seek time-pure`, pure);

    let rhythmTimes = null;
    let rhythmVisible = true;
    let rhythmDetail = null;
    for (const t of expected) {
      const seen = await page.evaluate(time => { window.__shot.renderAt(time); return window.__rhythm(); }, t);
      rhythmTimes = seen.map(e => Math.round(e.time * 1000) / 1000);
      rhythmDetail = seen;
      const here = seen.filter(e => Math.abs(e.time - t) < 1e-6);
      if (!here.length || !here.every(e => ['stage', 'text'].includes(e.layer) && e.connected && e.visibility !== 'hidden' && e.display !== 'none' && e.opacity > 0 && e.width > 0 && e.height > 0)) rhythmVisible = false;
    }
    record(`${cfg.name}: rhythm times match mapping`, JSON.stringify(rhythmTimes) === JSON.stringify(expected), JSON.stringify(rhythmTimes));
    record(`${cfg.name}: rhythm targets real and visible at their own time`, rhythmVisible && rhythmDetail.length === 4, JSON.stringify(rhythmDetail));

    const samples = [];
    const times = [...new Set(expected.flatMap(time => [time - .001, time + .001]))].sort((a,b) => a-b);
    for (const time of times) {
      await page.evaluate(time => window.__shot.renderAt(time), time);
      samples.push({time, ready:true, texts:[], rhythm_candidates:await page.evaluate(inspectRhythmFrame)});
    }
    const diagnosed = spawnSync('python3', ['-c', `import json,sys
sys.path.insert(0,sys.argv[1]+'/.studio')
from visual_diagnostics import rhythm_diagnostics
print(json.dumps(rhythm_diagnostics(json.load(sys.stdin),[dict(id='S01',start=0,duration=float(sys.argv[2]))])))`, repo, String(cfg.end)], {input:JSON.stringify(samples),encoding:'utf8'});
    assert.equal(diagnosed.status, 0, diagnosed.stderr);
    const report = JSON.parse(diagnosed.stdout);
    const observed = report.events.filter(event => event.kind === 'broll_moment').map(event => event.time).sort((a,b)=>a-b);
    record(`${cfg.name}: real probe confirms mapped moments`, JSON.stringify(observed) === JSON.stringify(expected), JSON.stringify(report));

    const layout = await page.evaluate(() => window.__layout());
    const style = await page.evaluate(() => window.__style());
    styles[cfg.name] = style;
    const caption = await page.evaluate(() => window.__caption());
    record(`${cfg.name}: caption zone clear`, caption.length === 0, JSON.stringify(caption));
    record(`${cfg.name}: layout bound to 90% and above caption`, Math.abs(layout.frameWidth - layout.stageWidth * 0.9) < 2 && layout.frameBottom <= layout.viewportHeight * 0.86 && layout.titleBottom <= layout.viewportHeight * 0.86 && layout.valueBottom <= layout.viewportHeight * 0.86);
    record(`${cfg.name}: label text fits capacity`, layout.title.len <= 12 && layout.value.len <= 8 && layout.title.client > 0 && layout.value.client > 0 && layout.title.scroll <= layout.title.client + 1 && layout.value.scroll <= layout.value.client + 1, JSON.stringify({ title: layout.title, value: layout.value }));

    if (!stretch) {
      const first = await page.evaluate(time => window.__seek(time), cfg.end);
      const second = await page.evaluate(time => window.__seek(time), cfg.end);
      record(`${cfg.name}: hold-end tail is stable`, first === second);
      record(`${cfg.name}: hold-end tail gap reported without extra events`, moments.key_moments.length === 4 && report.findings.some(item=>item.kind==='rhythm_gap' && item.end===cfg.end && item.duration>2));
    }

    const badMount = await page.evaluate(() => window.__failedMount());
    record(`${cfg.name}: bad mount cleans children and sources`, badMount.message.includes('broll_slot_capacity') && badMount.before.children === badMount.after.children && badMount.before.sources === badMount.after.sources && badMount.stageChildren === badMount.beforeStage, JSON.stringify(badMount));

    const rejects = await page.evaluate(() => window.__rejects());
    record(`${cfg.name}: invalid slots/paths rejected`, rejects.every(item => item[1]), JSON.stringify(rejects));
    const closure = await page.evaluate(() => window.__closureSlots());
    record(`${cfg.name}: installed media/icon and bounded parameters`, closure.valid && closure.canonical && closure.failures.every(Boolean), JSON.stringify(closure));

    const rolls = await page.evaluate(range => window.__rolls(range), {start:cfg.start,end:cfg.end});
    record(`${cfg.name}: rolls hide/show propagates through inherited visibility`, rolls.inside.stage === 'visible' && rolls.inside.frame === 'visible' && rolls.outside.stage === 'hidden' && rolls.outside.frame === 'hidden' && rolls.outside.caption === 'hidden' && rolls.before.stage === 'hidden' && rolls.before.frame === 'hidden', JSON.stringify(rolls));

    await page.evaluate(time => window.__seek(time), expected[3] + .01);
    await page.screenshot({ path: path.join(output, `${cfg.name}.png`) });

    const disposed = await page.evaluate(() => { window.__shot.dispose(); return {children: stage.children.length + text.children.length, sources: (window.__hfRhythmSources || new Set()).size}; });
    record(`${cfg.name}: dispose removes nodes and rhythm sources`, disposed.children === 0 && disposed.sources === 0, JSON.stringify(disposed));

    await page.close();
  }

  const desktop = styles['desktop-stretch'], mobile = styles['mobile-stretch'];
  record('themes retain their accent and prepared font', !!desktop && !!mobile && desktop.valueColor !== mobile.valueColor && desktop.titleFont.startsWith('HarnessFont_') && mobile.titleFont.startsWith('HarnessFont_'), JSON.stringify({ desktop, mobile }));

  const offline = await fs.stat(path.join(output, 'store')).then(() => false, () => true);
  record('store removed before browser seeks', offline);
  record('no page errors', errors.length === 0, JSON.stringify(errors));
  await fs.writeFile(path.join(output, 'evidence.json'), JSON.stringify({ checks, errors }, null, 2));
} finally {
  if (browser) await browser.close();
  await new Promise(resolve => server.close(resolve));
}

const failed = checks.filter(item => !item.passed);
console.log(JSON.stringify({ output, total: checks.length, failed: failed.length }, null, 2));
for (const item of checks) console.log(`${item.passed ? 'ok  ' : 'FAIL'} ${item.name}${item.detail ? ' :: ' + item.detail : ''}`);
if (failed.length) process.exitCode = 1;
