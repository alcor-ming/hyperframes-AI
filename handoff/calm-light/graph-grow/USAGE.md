# graph-grow · 冷静的光

源码候选 v1，尚未接纳。服务 explainer / showcase；card 可选。不是完整视频。

## 语义用途

解释节点如何组成系统，以及一条信号路径连接哪些节点。star 是调度中心，chain 是流水线，layers 是深度分层，mesh 是交联网络。

不适用：长正文、数据表、真实模型性能演示、精确物理仿真。普通文字入退场仍交给 Motion。镜头没有声音文件，只返回声音打点。

## 挂载前置条件

- 已加载宿主冻结的 appearance / rolls / broll runtime；appearance 必须来自 `await HarnessAppearance.load()`，冻结 Theme 带本地字体和许可
- Theme 必须有 `surface.color`、`colors.text`、`colors.accent`、`colors.muted`、`typography.body`；缺 token 明确报错，不静默硬编码颜色或字体
- 两个独立 connected roots，分别位于 `data-hf-layer="stage"` 与 `data-hf-layer="text"`；宽高相同，position 为 relative/absolute；不要嵌套
- WebGL 可用；画幅锁为 16:9 或 9:16。容器尺寸和浏览器 DPR 决定画布。renderAt 时重读容器尺寸，不注册 ResizeObserver / RAF
- 源内附带 Three.js 0.160.0 的 ESM minified build，文件名 `vendor/three.min.js`；不是 UMD，不导出或覆盖 window.THREE。保留 MIT 声明与 LICENSE

## 完整接线

```js
// Host loads frozen runtime/appearance.js, runtime/rolls.js, runtime/broll.js first.
const appearance = await HarnessAppearance.load();
const {mount} = await import('./vendor/components/graph-grow/v1/main.js');
// Separate connected, positioned, equally sized elements under these layers:
// stage.closest('[data-hf-layer]').dataset.hfLayer === 'stage'
// text.closest('[data-hf-layer]').dataset.hfLayer === 'text'
const cues = {find: key => ({sceneStart:0, shotStart:2, shotEnd:8, sceneEnd:9})[key]};
const shot = await mount({stage, text, appearance,
  slots: {hub:'调度', n1:'输入', n2:'工具', n3:'记忆', n4:'输出'},
  params: {topology:'star', path:'n1>hub>n4', seed:1, 'camera.orbit_deg':15},
  startCue:'shotStart', endCue:'shotEnd', cues});
const rolls = HarnessRolls.mount({cues, scenes:[{id:'S01', startCue:'sceneStart', endCue:'sceneEnd',
  a:{text:aText, items:[{id:'a1',element:aItem,cue:'sceneStart'}]},
  b:[{startCue:'shotStart',endCue:'shotEnd',retreat:'hide',media:stage,text}]}]});
async function renderAt(globalSeconds) { shot.renderAt(globalSeconds); await rolls.renderAt(globalSeconds); }
await renderAt(4.2);
const {key_moments, sfx_cues} = shot.moments();
function dispose() { shot.dispose(); rolls.dispose(); appearance.dispose(); }
```

所有时间是全片秒数；调用者持有唯一时钟。mount 等待字体；无纹理网络请求。不得在 mount ready 前宣布宿主 ready。dispose 可重复调用，只释放模块自身资源及其节奏注册。

## 插槽与参数

- `hub`: text，text 层，最多 6 个 Unicode 码点
- `n1`: text，stage 层，最多 6 个 Unicode 码点
- `n2`: text，stage 层，最多 6 个 Unicode 码点
- `n3`: text，stage 层，最多 6 个 Unicode 码点
- `n4`: text，stage 层，最多 6 个 Unicode 码点
- `n5`: text，stage 层，最多 6 个 Unicode 码点
- `n6`: text，stage 层，最多 6 个 Unicode 码点
- `n7`: text，stage 层，最多 6 个 Unicode 码点
- `n8`: text，stage 层，最多 6 个 Unicode 码点

- `topology`: `string`; default `star`; star / chain / layers / mesh
- `path`: `string`; default `n1/hub/n4`; …
- `seed`: `integer`; default `1`; 1…9999
- `camera.orbit_deg`: `number`; default `15`; 0…30

时长 4 / 6 / 10 秒（最短 / 默认 / 最长），stretch。参数以点路径为键，不传嵌套 camera 对象。显式传入未知参数或超范围值会失败。

底部 16% 是两种画幅的字幕安全区 `[0, .84, 1, .16]`，只允许宿主字幕使用。canvas 与两层 DOM 标签的绘制区域均在其上方；长标签不缩字、不截断，挂载时由 HarnessBroll 做字体容量检查。密集布局仍需视觉验收。

reduced motion 使用 mount 时 `prefers-reduced-motion: reduce` 的值；无相机运动、关键状态直接切换。切换系统设置后重建实例。fixture 的开关仅模拟系统设置。

## 事件与设计案解释

- 原设计案关键时刻保留；增加具有可见状态变化的中间事件，避免最长 stretch 的声明间隔超过 2 秒。moments 返回全片真实映射时间，dispose 注销
- 默认事件：`[0, 0.6, 1.2, 2, 2.8, 3.6, 4.2, 5.2, 5.8]`。事件目标是真实 DOM/canvas，但视觉节奏是否合格必须由本机 probe/人工复核，纯状态测试不能代替
- hub 最多 6 码点，因此示例采用「调度」，英文 `harness`（7）会报错，不擅自放宽
- `n1`～`n8` 可省略或空字符串，空值不生成节点；实现遵循明确的八个外围插槽，因此最多 8 个外围 + 1 个 hub。设计案「节点不超过 8 个」与插槽冲突时，可只填 n1～n7 保持总数 8
- path 解释为 2～5 条边，即 3～6 个已存在节点；连续重复节点拒绝。指定路径可添加拓扑原本没有的显式连接，这些连接会随网络一起绘出
- 入口先严格校验 `>` 分隔语法，然后仅在调用 HarnessBroll 前转换为 `/`，build 恢复原路径。这是对现有通用参数防表达式检查的入口适配；不要绕过入口直接把原参数交给 HarnessBroll。manifest 默认值使用 `n1/hub/n4`，因为 pack 同样拒绝 `>`。module.mount 同时接受两种分隔符；若经上游通用参数验证，请用 `/`，不能混用分隔符

## 本地验收

从仓库根按 `handoff/calm-light/README.md` 准备 fixture、启动 HTTP server，然后打开此目录的 `fixture/index.html`。可换画幅、Theme、模式、seed、reduced、时长、slots/params JSON，拖滑块（含 2 秒非零 startCue）。

`node fixture/seek.test.mjs` 从任意目录执行（需要上级测试工具及 Playwright）。它自动启动只读本地服务，覆盖两 Theme、两画幅、全部模式、reduced 与最短/默认/最长时长；顺播、直接跳转、倒拖、重复跳转比较截图字节，同时检查末态标签边界与清理。截图生成在 qa，失败就退出非零。

云端只完成状态/语法/包闭包验证；没有宣称截图、WebGL 或 Windows Studio 通过。复制源码到登记 AssetSource 后，沿用 component pack → 本机 Studio 审看 → 用户按准确 hash 接纳；不能直接当作 accepted 资产使用。
