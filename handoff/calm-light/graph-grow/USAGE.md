# graph-grow v2 · 冷静的光 / 2.5D 说明图

未接纳的可编辑源码候选；这次采用审阅建议的方向 A。保持 mount / renderAt / moments / dispose 合同，不制作完整视频。v1 保留历史，v2 避免同一 ref 对应不同包 hash。

## 用途与边界

展示部件之间的结构与有方向的信息路径。star：中心调度；chain：顺序链；layers：分层；mesh：互联。

不适合长文、数据表、真实模型能力或容量证明。无需空间关系的普通入退场继续使用 Motion。没有音频资源，只提供声音打点。

## 宿主前置条件

- 先加载冻结的 runtime/appearance.js、runtime/rolls.js、runtime/broll.js，调用 await HarnessAppearance.load()
- 冻结 Theme 必须含 surface.color、colors.text、colors.accent、colors.muted、typography.body，及本地字体和许可；不写死账号配色
- stage 与 text 是同宽高的独立 connected positioned roots，分别在 data-hf-layer="stage" / "text" 下，不得相互嵌套
- WebGL 可用；appearance.lock.ratio 为 16:9 或 9:16；在有真实宽高的容器挂载
- 使用包内原字节 Three.js r160 ESM（vendor/three.min.js）及 MIT 许可，不加载 CDN、不更改 window.THREE
- mount 等字体 ready；没有纹理、独立时钟、RAF、物理积累或历史帧反馈。宿主持有唯一时钟

## 完整挂载示例

```js
// Host loads frozen runtime/appearance.js, runtime/rolls.js, runtime/broll.js first.
const appearance = await HarnessAppearance.load();
const {mount} = await import('./vendor/components/graph-grow/v2/main.js');
// Separate connected, positioned, equally sized elements under these layers:
// stage.closest('[data-hf-layer]').dataset.hfLayer === 'stage'
// text.closest('[data-hf-layer]').dataset.hfLayer === 'text'
const cues = {find: key => ({sceneStart:0, shotStart:2, shotEnd:8, sceneEnd:9})[key]};
const shot = await mount({stage, text, appearance,
  slots: {hub:'调度', n1:'输入', n2:'工具', n3:'记忆', n4:'输出'},
  params: {topology:'star', path:'n1>hub>n4', seed:1, 'camera.orbit_deg':0},
  startCue:'shotStart', endCue:'shotEnd', cues});
const rolls = HarnessRolls.mount({cues, scenes:[{id:'S01', startCue:'sceneStart', endCue:'sceneEnd',
  a:{text:aText, items:[{id:'a1',element:aItem,cue:'sceneStart'}]},
  b:[{startCue:'shotStart',endCue:'shotEnd',retreat:'hide',media:stage,text}]}]});
async function renderAt(globalSeconds) { shot.renderAt(globalSeconds); await rolls.renderAt(globalSeconds); }
await renderAt(4.2);
const {key_moments, sfx_cues} = shot.moments();
function dispose() { shot.dispose(); rolls.dispose(); appearance.dispose(); }
```

renderAt 接收全片秒数，示例非零 startCue=2；支持顺播、直跳、回拖和重复 seek。结束清理先 shot/rolls，再 appearance。dispose 可重复调用，失败只清理模块自建资源。

## 插槽

- `hub`：text，text 层，最多 6 个 Unicode 码点
- `n1`：text，stage 层，最多 6 个 Unicode 码点
- `n2`：text，stage 层，最多 6 个 Unicode 码点
- `n3`：text，stage 层，最多 6 个 Unicode 码点
- `n4`：text，stage 层，最多 6 个 Unicode 码点
- `n5`：text，stage 层，最多 6 个 Unicode 码点
- `n6`：text，stage 层，最多 6 个 Unicode 码点
- `n7`：text，stage 层，最多 6 个 Unicode 码点
- `n8`：text，stage 层，最多 6 个 Unicode 码点

## 参数

- `topology`：string，默认 `star`，star / chain / layers / mesh
- `path`：string，默认 `n1/hub/n4`，–
- `seed`：integer，默认 `1`，1–9999
- `camera.orbit_deg`：number，默认 `0`，0–30

时长 4 / 6 / 10 秒（最短 / 默认 / 最长），stretch。参数是点路径键，不传嵌套 camera 对象。未知参数、类型和范围错误明确失败。

## 共同视觉合同

固定正交相机、平面布局，无雾、彩色灯光、随机旋转、环绕或末尾拉远。使用近似平涂的 MeshBasicMaterial 保持 Theme 颜色，不引入额外白色调色值。main 表示结构/文字，accent 表示当前路径或新生成，muted 只用于背景结构和移出图形；小字仍为 main。粗细、实心/空心、箭头与位置共同编码语义，不能只靠颜色。

底部 16% `[0,.84,1,.16]` 保留给字幕；canvas 与 DOM 标签使用上方 84% 内容区。横屏节点字号按全帧高 30/1080，竖屏按全帧宽 40/1080 等比缩放。胶囊标题加粗。不会为了塞字静默缩字号或截断；容器太小、字体太宽或内容布局无解会明确失败。

reduced motion 在 mount 时读取系统 prefers-reduced-motion；固定相机，按实际关键时刻切到离散状态。切换后重建实例。fixture 开关仅模拟系统设置。

每个包自包含 scene.js/layout.js 与 Three r160，没有跨包运行时依赖。重设容器尺寸后，在下一次 renderAt 更新；回到原尺寸必须恢复相同布局。

## graph 具体决定

- hub 始终保留并准确放在中心，包括奇偶节点数的 chain。横屏水平阅读，竖屏改纵向阅读，不把九个六字标签压进同一横行
- n1–n8 省略/空串时不创建节点，入口为 HarnessBroll 补可选空槽。最多八外围 + hub；要求总数≤8 时只填七个外围
- star 正放射，mesh 只有少量 seed 控制的平面扰动；layers 用平面分层，不再用大小或 z 暗示重要性
- 胶囊按拓扑外向/交替放置，以完整节点集和实际字体矩形一次性确定性避让；未出现节点也预留标签位置，不随播放顺序漂移。失败报 calm_light_label_layout_cannot_fit
- hub 字号横屏38px/1080p、竖屏48px/1080宽，加粗描边。其他标签保持 main 文字，不被淡化成 muted
- path 为2–5条边（3–6个节点）。mount 支持 n1>hub>n4 或 n1/hub/n4，不混用分隔符；pack/通用参数验证仍用斜线默认，避免已有表达式校验器拒绝 >
- 原拓扑以外的跳跃是独立弧线；曲线和穿过其他节点的结构线都会确定性避让无关节点。路径加粗2.2倍、accent、方向箭头；非路径线变细变淡，节点保留 main
- 上限九节点、十六连线、一个脉冲、一个终点环。密集 mesh 优先保留连通骨架与所需路径，再裁掉可选环边。删除无意义 status 圆点
- camera.orbit_deg 保留0–30输入兼容性，v2默认0，所有值都不移动相机。这是本次方向 A 的明确取舍
- hub 仍严格6码点；英文 harness（7）不合法，例子用「调度」

默认6秒：hub 0–.35；外围 .6–1.72；连线1.8–2.8；完整结构停留至3.35；路径3.35–5.1；终点5.1–5.2；末态静止.8秒。最长五段在默认时长每段.35秒；最短4秒 stretch 后约.233秒/段，若需每段至少.35秒应选6秒以上。实际 moments 按存在的节点/边/路径生成，注册真实可见目标；不会用相机运动或空白标记补事件。

## 本地验收与证据边界

按上级 README 准备带许可的中文字体、fixture 和 Playwright。fixture 可选画幅、两个 Theme、拓扑/模式、reduced、时长、seed、JSON 插槽与参数；slider 是全片时间，局部时刻需加2秒。

运行 fixture/seek.test.mjs：真实浏览器比较顺播、直跳、回拖、重复同一时刻像素，检查可见标签互撞/字幕边界、resize-and-return、清理与节奏注销。截图写入 qa，不导出视频。graph 另有 fixture/review.test.mjs，专门生成 star4中文、chain8中文、mesh竖屏在局部1.5/3.2/4.8/6秒的图，以及末态灰度/50%/25%图。

2026-10-02：Node状态/几何/布局测试与包闭包校验已执行；云端 Chromium 启动仍因 socket() Operation not permitted 失败。没有看到审阅文本提及的8张PNG，也没有生成本次PNG；视觉、真实像素seek、真实字体碰撞和官方Windows Studio仍待本机验证。纯状态/矩形估计测试不能冒充这些结果。

复制到现有登记 AssetSource 后 component pack，再由用户按准确v2 ref/hash审核接纳；不覆盖v1已冻结包、不修改生产接受记录。
