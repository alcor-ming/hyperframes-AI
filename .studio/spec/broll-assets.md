# 动效 B-roll 与风格资产创作

本指南适用于生产根 Opus 在 `asset-library/sources` 的库创作，不授予 Work 修改、接纳、发布或部署权限。任务需求使用 [BROLL Brief](../templates/BROLL_BRIEF.template.md)。card 与数学单片只用冻结资产；非数学 explainer 的定制主镜头另走已批准 Work/Scene 的独占交接，不直接入库。

## 创作与接纳

1. 用户给需求单；Opus 先提三个文字方向，说明语义、关键时刻、插槽、产品线与限制，选定后再写源。
2. 在 `asset-library/sources/broll/<style>/<id>/` 制作 module、完整 usage 和独立 sample。先登记已有 AssetSource，不新建平行库。
3. 用同根 `work-wsl.sh` 的 CLI 截图和诊断自检；在 Windows 官方 Studio 查看样例，至少用两个 Theme 和全部声明画幅。未验证项明确列出，不导出 Draft 视频。
4. `component pack <source>` 生成 configured AssetStore 中的候选，不手写候选记录。独立样例使用既有 `component install ... --project <registered-source/sample>` 与 `component verify --project <registered-source/sample>`，不伪装正式 Work。
5. Opus 只起草 purpose、aliases、tags、examples、limitations；用户确认准确 ref/hash 后执行 accept。已有接纳包不覆盖，变更发新版本。Harness 发版不携带库内容。

## 外观复用

- 账号外观：完整 Theme + Background + Motion，定义某个账号的整体样子。
- 风格叠加：appearance 文件只写 background / motion，省略 theme，继承账号 Theme；Motion 按槽合并，适合矩阵账号。
- appearance 文件写了 theme 就会覆盖账号 Theme，不会自动跟随账号。接口卡说明适用哪种用法和限制。
- 颜色和字体只读 `--appearance-*`。先做并接纳风格叠加，再做镜头；普通入退场、强调和转场引用 Motion，只有整段语义表演留在 module 内。

Motion v3 支持 pop、stamp、wipe、glitch-in；pulse、shake、wobble、glow；pop-out、wipe-out、glitch-out；wipe、push、glitch-cut。`back-out` / `spring` 为固定缓动，`hold_fps` 为 1..240 整数；低帧量化只影响过程，不移动 cue/endCue。每个新 effect 配 reduced 等价形式，规则见 [资产合同](hyperframes-assets.md)。

## 镜头接口

module 导出 `mount({stage, text?, appearance, slots, params, startCue, endCue, cues})`，返回 `renderAt(t)` / `moments()` / `dispose()`。宿主使用全片秒数，镜头不自启时钟，不依赖历史帧、随机数或 `onUpdate` 写状态。第 2 层 stage 交给 `HarnessRolls` 的 `media`；第 4 层 text 交给 B 文字组。

`asset.json` 的可选 `broll` 块必填字段：

| 字段 | 合同 |
|---|---|
| role / takeover | hook、concept、transition / inline、full-frame |
| duration | `{min,max,default}`，秒，`0 < min <= default <= max` |
| timing | stretch 比例映射；hold-end 只延长末态，min 等于 default，不能截短表演 |
| key_moments | 默认时长下有序、唯一的相对秒数，范围 0..default；仅说明，不直接计数 |
| sfx_cues | `[{time,purpose}]`，默认时长下相对秒数与用途，按 timing 映射 |
| slots | 以插槽名为键；text/number 声明 type、layer（stage/text）、max_chars；icon/media 只声明 type |
| params | 与 manifest `parameters` 相同的点路径/type/default/范围，调用时以点路径为键传值 |
| carries_info | 布尔；false 不允许 text 层插槽、不新增可读信息 |
| caption_safe_zone | 每个 compatibility.ratios 对应归一化 `[x,y,width,height]`，矩形在 0..1 内 |
| usage / examples | 完整挂载代码字符串 / 至少一个字符串示例，接口卡全部展示 |

text 接受字符串，number 接受有限数字，`max_chars` 按 Unicode 码点计数。字体必须在冻结 Theme 中，最长内容按每个画幅实测，超容量明确失败，不缩字号或截断掩盖问题。

icon 传 `{ref:"lucide:plug@1.45.0",path:"icons/plug.svg"}`：先安装准确图标集，再由宿主 `work icons use` 取进工程；只接受精确引用与核对过来源、几何的本地 SVG。media 传已安装 media 的 entry 相对路径；外部 URL、路径穿越和未登记文件均拒绝。插槽值不放进 Binding，Binding schema 3 不变。

新工程冻结 `runtime/broll.js`。作者可复用 `HarnessBroll.mount(metadata, options, build)` 做输入和容量校验、时间映射与节奏注册；不另建挂载框架。`build(context)` 返回 `renderAt(localTime,globalTime)`、`events:[{time,target}]`、文字 `labels:{slotName:element}` 和 `dispose()`。它只创建自己的子节点，不改变宿主 roots 的结构；标签在正确层、使用冻结字体和真实插槽内容。`events` 使用默认表演的相对时间并绑定真实可见目标；`moments()` 返回这些运行时事件映射后的 `key_moments` 与映射后的 `sfx_cues`。dispose 删除自身节点与注册，失败也清理。

```javascript
// index.html first loads runtime/appearance.js, runtime/rolls.js and runtime/broll.js.
const appearance = await HarnessAppearance.load();
const {mount} = await import('./vendor/components/example/v1/main.js');
const shot = await mount({stage: bStage, text: bText, appearance,
  slots: {title: 'Broll signal', value: 42}, params: {},
  startCue: '示例开始', endCue: '示例结束', cues});
const rolls = HarnessRolls.mount({cues, scenes: [{id: 'S01',
  startCue: '场景开始', endCue: '场景结束', a: aGroup,
  b: [{startCue: '示例开始', endCue: '示例结束', retreat: 'hide', media: bStage, text: bText}]}]});
async function renderAt(t) { shot.renderAt(t); await rolls.renderAt(t); }
const {key_moments, sfx_cues} = shot.moments();
function dispose() { shot.dispose(); rolls.dispose(); appearance.dispose(); }
```

## 画面与节奏自检

- 整帧镜头仍在第 2 层，可盖背景；overlay 在上，captions 始终最高。主图与文字避开字幕安全区。
- 承载信息的独立标题、解释与关键数字进入 text 根，遵守 A1、实际口播 cue 与阅读保护；stage 只放图形附着的短标注。B 结束恢复 A 的既有状态。
- 纯注意力镜头不新增可读信息；事实约束不豁免，示意数据或界面标 `data-hf-schematic`。
- 两个 Theme、全部画幅、最短/默认/最长时长都检查容量与 seek。顺播、直接 seek 与回拖结果一致，末帧有收束。
- 挂载时把带 target、实际秒数的事件注册到 `__hfRhythmSources`，dispose 时注销。探针仍验证可见变化，声明不能冒充事件；hold-end 尾部不自动补节奏，超过 2 秒需处理或声明合理例外。
- 接口卡写清语义用途、不适用情形、一个完整填槽例子和样例工程。验收标准是 Codex 不看实现源码也能按 usage 正确挂载。

首批建议先做贴纸拼贴（stamp / wobble / hold_fps），再做赛博 HUD（glitch / wipe / glow）和综艺花字（pop / shake / pulse / spring）。这是生产根的后续库制作，不是 Harness 开发或部署自动执行的内容。
