# token-stream · 冷静的光

源码候选 v1，尚未接纳。服务 explainer / showcase；card 可选。不是完整视频。

## 语义用途

解释有限容量的上下文容器、旧 token 被挤出，以及逐 token 生成输出。方块是示意单位，不是某个模型的实际 tokenizer 或实际窗口容量。

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
const {mount} = await import('./vendor/components/token-stream/v1/main.js');
// Separate connected, positioned, equally sized elements under these layers:
// stage.closest('[data-hf-layer]').dataset.hfLayer === 'stage'
// text.closest('[data-hf-layer]').dataset.hfLayer === 'text'
const cues = {find: key => ({sceneStart:0, shotStart:2, shotEnd:9, sceneEnd:10})[key]};
const shot = await mount({stage, text, appearance,
  slots: {input_label:'你的提问', box_label:'上下文', output_label:'回答', counter:200000},
  params: {mode:'overflow', token_count:32, capacity_ratio:1.3, seed:1},
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

- `input_label`: text，text 层，最多 10 个 Unicode 码点
- `box_label`: text，stage 层，最多 6 个 Unicode 码点
- `output_label`: text，text 层，最多 10 个 Unicode 码点
- `counter`: number，text 层，最多 16 个 Unicode 码点

- `mode`: `string`; default `overflow`; fill / overflow / generate
- `token_count`: `integer`; default `32`; 12…80
- `capacity_ratio`: `number`; default `1.3`; 0.5…1.5
- `seed`: `integer`; default `1`; 1…9999

时长 5 / 7 / 12 秒（最短 / 默认 / 最长），stretch。参数以点路径为键，不传嵌套 camera 对象。显式传入未知参数或超范围值会失败。

底部 16% 是两种画幅的字幕安全区 `[0, .84, 1, .16]`，只允许宿主字幕使用。canvas 与两层 DOM 标签的绘制区域均在其上方；长标签不缩字、不截断，挂载时由 HarnessBroll 做字体容量检查。密集布局仍需视觉验收。

reduced motion 使用 mount 时 `prefers-reduced-motion: reduce` 的值；无相机运动、关键状态直接切换。切换系统设置后重建实例。fixture 的开关仅模拟系统设置。

## 事件与设计案解释

- 原设计案关键时刻保留；增加具有可见状态变化的中间事件，避免最长 stretch 的声明间隔超过 2 秒。moments 返回全片真实映射时间，dispose 注销
- 默认事件：`[0, 1, 2, 3, 3.75, 4.5, 5.25, 6, 6.7]`。事件目标是真实 DOM/canvas，但视觉节奏是否合格必须由本机 probe/人工复核，纯状态测试不能代替
- counter 必须是正的安全整数（最多 16 字符），表示容器容量；初始 caption 保持该槽值，另一个 DOM 数字显示当前使用量。它是用户指定数值，没有模型品牌或默认事实主张
- output_label 在非 generate 模式可省略，入口补空槽；固定槽仍参与字体容量验证
- overflow 要求 capacity_ratio > 1；capacity=floor(token_count/capacity_ratio)。fill 的多余输入停在外部，generate 的多余输入不解释为旧 token 被删除；ratio<1 时保持部分填充，计数不会冒称装满
- fill 阶段标记展示填充比例、容量确认与收束；overflow 显示累计移除估算数；generate 显示生成方块数。所有数字均是示意单位换算

## 本地验收

从仓库根按 `handoff/calm-light/README.md` 准备 fixture、启动 HTTP server，然后打开此目录的 `fixture/index.html`。可换画幅、Theme、模式、seed、reduced、时长、slots/params JSON，拖滑块（含 2 秒非零 startCue）。

`node fixture/seek.test.mjs` 从任意目录执行（需要上级测试工具及 Playwright）。它自动启动只读本地服务，覆盖两 Theme、两画幅、全部模式、reduced 与最短/默认/最长时长；顺播、直接跳转、倒拖、重复跳转比较截图字节，同时检查末态标签边界与清理。截图生成在 qa，失败就退出非零。

云端只完成状态/语法/包闭包验证；没有宣称截图、WebGL 或 Windows Studio 通过。复制源码到登记 AssetSource 后，沿用 component pack → 本机 Studio 审看 → 用户按准确 hash 接纳；不能直接当作 accepted 资产使用。
