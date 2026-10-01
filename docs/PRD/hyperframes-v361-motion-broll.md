# HyperFrames v3.6.1 Opus 动效 B-roll 与 Motion v3（开发方案）

状态：2026-09-29 已实施并完成 WSL 合同、全量单测及隔离浏览器验证。用户后续明确授权部署到 `D:\AI\AI+hyperframes`；部署结果以 `dist/deployments/` 的本次收据为准，不代表生产内容验收。姊妹文档：[资产库镜头创作指南](hyperframes-v361-broll-asset-authoring.md)已定稿为受管理指南与需求单。

## 1. 目标

**版本定位**：v3.4–v3.6 一直在探索如何把 Opus 能力融入各产品线，涉及运动合同、卡片套件、showcase 与提炼。v3.6.1 是一个小目标，把其中的分工确定下来：Opus 通过风格外观和 B-roll 镜头反哺 Codex 线，explainer 采用混合模型。不另开大版本。

**背景**：Opus 5.5 能写出抓注意力的 MG 动效，Codex / DS Flash 做不到同等的画面冲击力。本版本的原则是：**Opus 负责画面冲击力，Codex 负责叙事与合同**。Opus 的审美以两种可复用形态进入 Codex 各线：

- **风格外观**：Theme / Background / Motion v3 预设。
- **B-roll 镜头**：冻结的 module，带插槽、读取 Theme 变量，挂进现有 A/B 编排即可使用。

只有 explainer 线允许 Opus 为单片写定制主镜头。

**分步路线**：

1. 本 PRD：合同、规则与生产会话授权。
2. 首批库制作：按姊妹文档在生产根执行，不属于开发任务。
3. Codex 接入：Plan 工具化引用镜头与插槽值，节奏诊断建议插入位置。
4. explainer 主镜头交接工具化。

## 2. 已定决策（用户 2026-09-29）

- **D1**：只有 `explainer` 线采用混合模型：Opus 写单片 1–2 个主镜头，其余由 Codex 完成。
- **D2**：`card` 线与数学系列只复用已冻结库资产，单片生产不调用 Opus。
- **D3**：`card` 线沿用现有节奏合同。镜头与新 Motion 可以用，但不强制、不设配额。card 内容以简单信息为主，对标用 HyperFrames 基础功能做类 PPT 视频的账号及其观众。
- **D4**：首批风格方向为赛博 HUD、贴纸拼贴、综艺花字。
- **D5**：通用库镜头分三类：开场钩子 `hook`、概念镜头 `concept`、转场/强调 `transition`。explainer 主镜头属于"仅本片"，不进通用库；接受后可经提炼另行入库。
- **D6**：通用库的可编辑源放在生产根 `asset-library/sources`，由 WSL 生产根 Claude Code 会话（Opus 5.5）制作。接纳仍由用户执行，Harness 发版不携带库内容。
- **D7**：风格化运动通过扩展现有 Motion 预设实现（Motion v3），不绕过 Motion 合同、不藏进 module 私有代码。只有无法用声明式预设表达的整段表演，才留在镜头 module 内。

## 3. 现状证据

- **Motion v2 的能力范围**（`.studio/runtime/appearance.js:188`）：
  - 四槽的 effect 只有：reveal `fade`/`short-rise`、emphasis `focus-restore`、exit `fade-out`、transition `crossfade`/`cut`。
  - 实现方式是原生 WAAPI 按宿主秒数 seek。
  - 属性所有权冲突时拒绝创建（`.studio/runtime/appearance.js:280`）。
  - Motion 绑定**不向节奏探针注册事件**。
  - 验证入口：`tests/motion-browser.mjs`、`tests/test_motion_contract.py`。
- **节奏探针的事件来源**：只有宿主 GSAP timeline 的 tween 和 `window.__hfRhythmSources` 注册的事件（`.studio/visual_probe.mjs:99`）。候选事件必须满足三个条件才计数：目标在 `stage`/`overlay`/`text` 层（`.studio/visual_probe.mjs:72`）、可见、实际发生状态变化。manifest 里的声明不会被读取。`figures.js`、`rolls.js`、`card-kit.js`、`math-kit.js` 都用 `__hfRhythmSources` 注册"带目标和时间"的事件。
- **A/B 编排的接口**：`HarnessRolls.mount({cues, scenes})`（`.studio/runtime/rolls.js:5`，接口卡见 `.studio/spec/runtime-interfaces.md` 的 rolls.js 一节）。
  - 每段 B 区间提供第 2 层 `media` 和可选的第 4 层 `text`，由宿主通过 `renderAt(t)` 求值。
  - `card-kit.js` 是先例：同时持有 stage 根与 text 根，分别占第 2、4 层。
- **module Binding 的限制**：Binding schema 3 的 `usage` 只有 role / required / fit / focal_point，布局和动作留在 Scene 里，**不接受插槽值**（[资产规格](../../.studio/spec/hyperframes-assets.md)）。
- **外观解析的合并规则**：`.studio/appearance.py:69` 执行 `selected = {**account, **overrides}`。`--appearance-file` 里一旦写了 Theme，就会覆盖账号的 Theme；省略 theme / background 时继承账号值；Motion 按槽合并。
- **文字层规则**：B 的独立解释文字必须进第 4 层 B 文字组，并遵守 A1、语义 cue 和阅读保护；第 2 层只放附着标注（`.studio/spec/visual-design.md`）。
- **生产根会话模板的现状**：`.studio/templates/CLAUDE.template.md` 目前规定"其他系列只读审查、不修改 Work"，并且无条件豁免 explainer 检查、只加载 showcase 规则。

## 4. 需求

### 4.1 Motion v3

- `BROLL-REQ-001`：Motion 新增 manifest `contract_version:3` 与 entry `capability_version:3`。
  - v2 的全部 effect 与校验不变；已冻结的 v2 Work 不自动升级。
  - 同一闭包里允许不同槽位分别引用 v2 和 v3 资产，每个 entry 按自己的版本规则校验；闭包里只要含 v3，就生成新的 lock contract，旧宿主明确拒绝。
  - 观察点：`tests/test_motion_contract.py`、lock 与 resolver 测试。
- `BROLL-REQ-002`：首批新增 effect（按 D4 取最小集，用户 2026-09-29 批准）。
  - reveal：`pop`（缩放过冲）、`stamp`（缩放 + 旋转落章）、`wipe`（clip-path 定向擦入）、`glitch-in`（固定关键帧的阶梯位移）。
  - emphasis：`pulse`、`shake`、`wobble`、`glow`（颜色取自冻结 Theme token）。这四种是一次性动作，不需要 `restoreCue`。
  - exit：`pop-out`、`wipe-out`、`glitch-out`。
  - transition：`wipe`、`push`、`glitch-cut`。
  - 每个 effect 声明自己占用的属性，沿用现有的所有权冲突拒绝规则。关键帧必须确定：不用随机数，不在 `onUpdate` 里写状态。
- `BROLL-REQ-003`：公共缓动与时间规则。
  - 新增缓动：`back-out`（过冲）和 `spring`（固定采样的 `linear()` 表）。
  - 新增可选参数 `hold_fps`：以 cue 为相位原点做阶梯量化，只作用于起止之间的中间帧。`t=cue` 时必须是精确起始状态，`t=cue+duration`（transition 为 `endCue`）时必须是精确结束状态；量化不能移动 cue、endCue 或 overlap。
  - 每个新 effect 都要有 reduced 等价：入退场退化为 fade，强调时长为 0，转场退化为 cut。
- `BROLL-REQ-004`：新版 runtime 的 `bindMotion` 对 v2 和 v3 绑定都向 `__hfRhythmSources` 注册事件，内容为 `{time: cue, target, kind: "motion_<slot>"}`，`dispose` 时注销。探针仍需确认可见状态变化，只有这样才计数。已冻结在 Work 里的旧 runtime 不受影响。
  - 观察点：`preview diagnose` 夹具。

### 4.2 风格外观的两种用法

- `BROLL-REQ-005`：风格外观不新增资产种类，只区分两种用法。
  - **账号外观**：完整的 Theme + Background + Motion，用于定义一个账号的样子。
  - **风格叠加**：`--appearance-file` 只写 background / motion、省略 theme，从而继承账号 Theme，用于跨账号复用。
  - 创作指南和接口卡要写明每个风格资产适用哪种用法。card 账号可以选用，但不强制（D3）。
  - 观察点：`work appearance resolve` 测试。同一份风格叠加解析到两个 Theme 不同的账号时，各自保留自己的 Theme，Motion 与 Background 相同。

### 4.3 B-roll 镜头合同

- `BROLL-REQ-006`：镜头 module 的**挂载接口**。沿用 `rolls.js` / `card-kit.js` 的做法：
  - 入口 `mount({stage, text?, appearance, slots, params, startCue, endCue, cues})`，返回 `{renderAt(t), moments(), dispose()}`。
  - `stage` 是宿主提供的第 2 层元素，作为 B 区间的 `media` 交给 `HarnessRolls`；`text` 是可选的第 4 层元素，作为 B 文字组。
  - 由宿主按全片秒数调用 `renderAt(t)`；镜头不自启时钟、不拥有独立播放权，顺播、直接 seek、回拖三者结果一致。
  - 镜头挂载时，把实际秒数下的关键时刻以**带目标元素**的事件注册到 `__hfRhythmSources`，`dispose` 时注销。
  - manifest 里的 `key_moments` 只是说明，不参与计数。
- `BROLL-REQ-007`：manifest 里的**取用合同**。module `asset.json` 可以带一个可选的 `broll` 块，pack/validate 做结构校验，接口卡负责展示。块内字段如下：
  - `role`：hook / concept / transition。
  - `takeover`：`inline` 或 `full-frame`。
  - `duration`：{min, max, default}，单位秒。
  - `timing`：`stretch` 或 `hold-end`，规定实际时长与关键时刻的映射。
    - `stretch`：关键时刻按比例缩放。
    - `hold-end`：关键时刻保持绝对秒数，多出的时间停在末态；末态期间仍受 ≤2 秒节奏检查约束。
    - 实际时长超出 [min, max] 时拒绝挂载。
  - `key_moments`、`sfx_cues`：以 default 时长下的相对秒数书写，按 `timing` 映射；`moments()` 返回映射后的实际秒数，供 Plan 和声音层使用。
  - `slots`：逐项声明 `type`，可选值为 text / number / icon / media。
    - text 与 number 另外声明 `layer: stage|text` 和最大字数，并用冻结字体实测容量。
    - icon 只接受精确图标引用（如 `lucide:plug@1.45.0`），宿主经 `work icons use` 把它取进工程闭包后，再以工程内路径传入。
    - media 只接受当前 Work 闭包内、已登记的 media 资产路径。
    - 外部 URL、闭包外路径、类型或容量不符的插槽值一律拒绝。
  - `params`：沿用 `parameters` 的点路径 / 类型 / 范围。
  - `carries_info`：布尔。
  - `caption_safe_zone`：按画幅声明。
  - `usage` 与 `examples`：一份填好插槽的完整挂载示例，外加一个样例工程，作为 `component interface` 输出的一部分。验收标准是：只看接口卡就能写出正确的挂载代码。

  画幅沿用 `compatibility.ratios`；颜色与字体只读 `--appearance-*`。没有 `broll` 块的 module 行为不变。本步不改 Binding schema；插槽值由 Scene 源码按 `usage` 传入，Plan 工具化留到第 3 步。
- `BROLL-REQ-008`：`work component list` 增加 `--broll-role` 筛选，风格沿用 `--tag`（如 `style:cyber-hud`）。
- `BROLL-REQ-009`：开发仓自带一个合成样例镜头，跑通 pack → install → verify → 浏览器 seek 截图，至少覆盖两个不同 Theme 的账号、9:16 与 16:9，并同时覆盖 `stretch` 和 `hold-end` 两种时长。
  - 观察点：新增 `tests/broll-browser.mjs` 与 Python 合同测试。

### 4.4 规则

- `BROLL-REQ-010`：在 `visual-design.md` 的 B-roll 部分增加"动效镜头"类型。
  - 整帧镜头挂在第 2 层宿主内，可以自带底色、覆盖第 1 层；第 3 层转场可以叠加在上面；第 5 层字幕始终在最上方，镜头避开 `caption_safe_zone`。
  - `carries_info:true` 的镜头：独立标题、解释和关键数字必须走 `text` 根（第 4 层 B 文字组），继续遵守 A1、语义 cue 起点和阅读保护；第 2 层只放附着在图形上的短标注。
  - `carries_info:false` 的镜头：不新增可读信息，不能有 `layer: text` 的插槽，不适用 A1 与阅读保护。
  - 镜头里出现示意性数据或界面时，标记 `data-hf-schematic`。
  - 镜头节奏以运行时注册、且实际可见变化的事件为准。
- `BROLL-REQ-011`：按产品线写分工。
  - card：镜头可选、无配额，内容简单优先。
  - 数学系列：只用库资产。
  - explainer：Plan 可以标出 1–2 个"Opus 主镜头"位及其 Asset Brief。方向批准后，由生产根 Claude 会话在同一 Work 内独占制作；主镜头完全遵守 explainer 规则（五层、A1、节奏合同），完成后交回 Codex。

### 4.5 生产根会话

- `BROLL-REQ-012`：把 `CLAUDE.template.md` 改为**按任务类型适用**，不在原文后追加。每种任务各自说明加载哪些规则、写权限范围和豁免：
  - **showcase 制作**：保持现状，只有这一类豁免 explainer 检查。
  - **explainer 主镜头**：只能写用户指定的 Work / Scene，加载 explainer 与视觉规则，不享受豁免，遵守单一执行者。
  - **资产库创作**：只能写 `asset-library/sources` 里的源和候选，加载 `broll-assets.md`，不写接纳记录，已接纳的包只发新版本、不覆盖。
  - **只读审查**：保持现状。

  未列出的系列一律只读。
- `BROLL-REQ-013`：发行包附带创作指南 `.studio/spec/broll-assets.md` 与需求单 `.studio/templates/BROLL_BRIEF.template.md`，二者由姊妹文档定稿生成，纳入 release 根文件清单。

### 4.6 收尾

- `BROLL-REQ-014`：全量单元测试、`validate_package.py`、diff 检查全部通过；README 与 PRD 索引同步更新。Windows 原生与部署按用户后续授权单独报告真实结果；生产内容验收未执行。

## 5. 验收

1. **Motion 兼容与时间精度**（REQ-001–003）：
   - v2 资产、lock、已冻结 Work 的校验结果不变。
   - 同一闭包混用 v2 与 v3 槽位时可以解析、可以播放。
   - v3 预设在常规与 reduced 模式、三种画幅下，顺播、直接 seek、回拖结果一致。
   - 设置 `hold_fps` 时，cue、endCue 两个时刻的状态精确，中间帧按 cue 相位阶梯量化。
2. **Motion 节奏计数**（REQ-004）：`preview diagnose` 能把 Motion 绑定计为事件；目标被隐藏或状态无变化时不计。
3. **风格叠加**（REQ-005）：同一份风格叠加用于两个账号时，各自保留自己的 Theme；账号外观会整体覆盖账号值。
4. **镜头取用**（REQ-006–009）：
   - 样例镜头可以 pack、validate、install、verify，并能被 `--broll-role` 查到。
   - 只按接口卡里的 `usage` 就能挂进 `HarnessRolls` 的 B 区间。
   - 以下情况明确拒绝：插槽值类型错、超容量、外部 URL、闭包外路径、时长越界。
   - `stretch` 与 `hold-end` 两种模式下，`moments()` 给出正确的实际秒数，并与诊断计到的事件时刻一致。
   - 字幕不被镜头遮挡；第 4 层文字服从阅读保护。
5. **规则与生产会话**（REQ-010–013）：
   - 规则中 `carries_info` 两种取值的归属清楚，分工体现 D1–D3。
   - `CLAUDE.md` 模板按任务类型组织，新旧指令之间没有冲突。
   - 发行包含指南与需求单模板。

## 6. 不做

- 首批库镜头的实际制作与接纳。
- 画廊挑选页。
- Binding schema 变更、Plan 镜头字段与节奏插入建议（第 3 步）。
- 主镜头交接的 CLI 工具化（第 4 步）。
- 新增资产种类。
- 生产内容验收。部署已由用户后续指令纳入本次执行，不制作或接纳首批库内容。
