# token-stream v2 · 冷静的光 / 2.5D 说明图

未接纳的可编辑源码候选；这次采用审阅建议的方向 A。保持 mount / renderAt / moments / dispose 合同，不制作完整视频。v1 保留历史，v2 避免同一 ref 对应不同包 hash。

## 用途与边界

展示有限容量、最早输入先移出的 FIFO，以及与保留内容区分的新生成结果。每个方块是一格示意单位，不代表某个模型的真实 tokenizer。

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
const {mount} = await import('./vendor/components/token-stream/v2/main.js');
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

renderAt 接收全片秒数，示例非零 startCue=2；支持顺播、直跳、回拖和重复 seek。结束清理先 shot/rolls，再 appearance。dispose 可重复调用，失败只清理模块自建资源。

## 插槽

- `input_label`：text，text 层，最多 10 个 Unicode 码点
- `box_label`：text，stage 层，最多 6 个 Unicode 码点
- `output_label`：text，text 层，最多 10 个 Unicode 码点
- `counter`：number，text 层，最多 16 个 Unicode 码点

## 参数

- `mode`：string，默认 `overflow`，fill / overflow / generate
- `token_count`：integer，默认 `32`，12–80
- `capacity_ratio`：number，默认 `1.3`，0.5–1.5
- `seed`：integer，默认 `1`，1–9999

时长 5 / 7 / 12 秒（最短 / 默认 / 最长），stretch。参数是点路径键，不传嵌套 camera 对象。未知参数、类型和范围错误明确失败。

## 共同视觉合同

固定正交相机、平面布局，无雾、彩色灯光、随机旋转、环绕或末尾拉远。使用近似平涂的 MeshBasicMaterial 保持 Theme 颜色，不引入额外白色调色值。main 表示结构/文字，accent 表示当前路径或新生成，muted 只用于背景结构和移出图形；小字仍为 main。粗细、实心/空心、箭头与位置共同编码语义，不能只靠颜色。

底部 16% `[0,.84,1,.16]` 保留给字幕；canvas 与 DOM 标签使用上方 84% 内容区。横屏节点字号按全帧高 30/1080，竖屏按全帧宽 40/1080 等比缩放。胶囊标题加粗。不会为了塞字静默缩字号或截断；容器太小、字体太宽或内容布局无解会明确失败。

reduced motion 在 mount 时读取系统 prefers-reduced-motion；固定相机，按实际关键时刻切到离散状态。切换后重建实例。fixture 开关仅模拟系统设置。

每个包自包含 scene.js/layout.js 与 Three r160，没有跨包运行时依赖。重设容器尺寸后，在下一次 renderAt 更新；回到原尺寸必须恢复相同布局。

## token 具体决定

- 横屏10列、竖屏6列的平面网格；capacity=floor(token_count/capacity_ratio)，8–160个容量格全部存在、无遮挡。格子用等物理边长方块，宽高画幅不同会重新排网格
- token有稳定序号。窗口格索引=序号−FIFO移位量；所有保留 token 沿折返队列整体前移，跨行不斜穿网格。移出、移位、计数共用同一时间函数，稀疏溢出也不会先消失后计数
- fill：超额输入保持空心等待，检查容量格时使用中性描边；overflow：最早输入以空心 muted 移至「已移出」区并淡出；generate：保留窗口内容，新输出为 accent 实心，通过通道移到输出区
- overflow 必须 capacity_ratio>1；ratio<1 的 fill/generate 保持部分容量，不显示假“满格”
- counter 为用户配置的正安全整数，原槽最多16字符。合成单行「约用 x / y token（示意）」并加千分位；另显示明确的保留序号、已用/待入/移出/生成格数，不再显示无单位负数或 ●○✓
- counter 大于画面在当前字体/尺寸下可容纳的资格行宽时，报 token_usage_line_capacity；包括最大安全整数在竖屏可能失败。它不会为了满足数字范围而缩字，实际可用上限必须通过本机字体容量验收。200000 是接口示例，不是模型事实
- 状态文案固定为中文，因此即使 input_label 等使用英文，Theme 也必须覆盖中文及数字。不能用只含拉丁字母的字体验收本模块
- output_label 非 generate 可省略；generate 省略时使用「生成序列」说明。可选空槽仍按原宿主合同参与验证
- seed 保留输入兼容性，v2不扰动方块尺寸、序号或旋转；同样参数和时间总是同样画面
- reduced motion 只展示完成的整数 FIFO 步和完成的输出，不把半移出的方块冻结在途中

默认7秒：0–1空窗口和标签；1–3输入；3–3.6容量强调；3.6–5.8分支动作；5.9出现结果句；保持至7。5.9取代建议中的5.8最终结果时刻，是为了在最长12秒stretch时末态间隔仍≤2秒。moments=[0,1,2,3,3.6,4.75,5.9]；容量检查/计数/结果必须有真实可见变化，最终节奏仍需本机probe复核。

## 本地验收与证据边界

按上级 README 准备带许可的中文字体、fixture 和 Playwright。fixture 可选画幅、两个 Theme、拓扑/模式、reduced、时长、seed、JSON 插槽与参数；slider 是全片时间，局部时刻需加2秒。

运行 fixture/seek.test.mjs：真实浏览器比较顺播、直跳、回拖、重复同一时刻像素，检查可见标签互撞/字幕边界、resize-and-return、清理与节奏注销。截图写入 qa，不导出视频。graph 另有 fixture/review.test.mjs，专门生成 star4中文、chain8中文、mesh竖屏在局部1.5/3.2/4.8/6秒的图，以及末态灰度/50%/25%图。

2026-10-02：Node状态/几何/布局测试与包闭包校验已执行；云端 Chromium 启动仍因 socket() Operation not permitted 失败。没有看到审阅文本提及的8张PNG，也没有生成本次PNG；视觉、真实像素seek、真实字体碰撞和官方Windows Studio仍待本机验证。纯状态/矩形估计测试不能冒充这些结果。

复制到现有登记 AssetSource 后 component pack，再由用户按准确v2 ref/hash审核接纳；不覆盖v1已冻结包、不修改生产接受记录。
