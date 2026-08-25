# Component-Driven Motion vNext 决策台账

状态：产品方案已确认，阶段 A 设计共建中

风险：T3 Parent PRD

日期：2026-08-23

## 原始概念

> 参考idea.md中的规划，参考rn-skill的设计，结合目前实际工作进行PRD规划：目前会根据所选profile、子profile选择组件+gasp动效等设计

正式用语与范围：

- 正式名称继续使用 `subtemplate`，不新增“子 Profile”。
- MVP 只覆盖 `pure_hyperframes + optical_fluidity`。
- `hero_flow` 与 `module_stage` 继续作为既有 Subtemplate。
- 组件与内部 GSAP Motion Recipe 共同版本化。
- 首批组件不从预设清单或历史 Work 自动抽取，而从当前真实场景中由用户确认后产生。
- 阶段 A 使用既有 `work-20260821-一个人做号太累-先装这10个skill/main`，不新建 Work。
- 当前 Work 使用 `module_stage + 4:3`；新建时写入的 `9:16` 是错误默认值。

## 产品目标

把“Agent 每次临场编写一次性 HTML/GSAP”升级为“真实场景共建设计、用户确认、公共组件沉淀、后续 Work 精确复用”，同时保留内容语义决定画面机制以及用户对具体组件和动效的最终确认权。

## 已确认边界

### 分层

- `Profile` 负责视觉身份、材质、排版、Motion Grammar 和硬限制。
- `subtemplate` 负责展示架构，不拥有组件外观或具体编舞。
- `Component` 负责可复用语义机制、Slots、Hero States 和内部有限动效。
- `ANIMATION_PLAN.md` 继续是正式 HTML 前唯一必须整体批准的视觉 PRD。
- Work 使用批准组件的本地副本，不运行时依赖公共库或 Open Design。

### 本次临时流程

- 当前 Work 先写不含预设组件的 `ANIMATION_DRAFT.md`。
- Draft 只定义本地预规范化的语义输入、真实长度样例、素材条件和事实边界，不预设组件拆分、Hero States、Motion Recipe 或 Slot API。
- 用户与 Kimi 在 Open Design 中提出组件拆分，并共建可独立 Preview/seek 的 HyperFrames 组件、内部 GSAP 与简短的代表性组合 Preview；不负责整支视频设计。
- 组件确认后才正式完成 `ANIMATION_PLAN.md`，整体批准后再进入生产实现。
- 正式 Plan 生成后，Animation Draft 保留但标记 superseded。

### Open Design 与本地工作流

- Open Design 创建组件和内部动效模板本体；本地工作流查库、选择、命名、版本化并调用 `component_id@vN` 与 Motion Recipe。
- 本地在 Open Design 前规范化语义字段、数据类型、长度样例和必需/可选性；落地时再完成最终文案与 Slot 合同。
- Open Design 可沿用原设计颜色或参考色验证动效与组件搭配；精确 Profile 颜色由本地映射，不是本次验收项。
- 真实截图、视频、品牌图标与字体由本地验证并提供；Open Design 可创建组件内生的 HTML/CSS 图形，但不依赖运行时网络或临时外链。
- 本地负责 Scene 绝对时间、音频对齐、跨 Scene 转场、全片组合与 QA。

### Open Design 与生产真源

- 用户确认前，Open Design artifact 是组件设计真源。
- 确认必须冻结 revision；没有稳定 revision 时使用完整 bundle SHA-256。
- Codex 读取完整 artifact bundle 并优先直接采用，只做 Slots、Profile 颜色映射、本地素材、HyperFrames seek-safe、离线渲染和隔离所需的最小规范化。
- 技术翻译不得改变已确认视觉、Hero State 顺序或内部动效编排。
- 允许作品级调整 Slots、位置、尺寸、offset、整体 timeScale 和 Hero/Handoff 静止保持；不得重排内部 Beat，明显失真则退回用户与 Kimi。
- 验收冻结组件拆分与搭配、视觉结构、关键状态和可感知的内部动效；最终文案、精确颜色、真实媒体、Slot API、生产 ID 和绝对时间不冻结，除非修改破坏已确认效果。
- 正式 Plan 批准并落库后，仓库不可变组件版本成为生产真源。

### 组件库与复用

- 用户确认同时区分 `work-local` 与 `library-approved`，不新增独立审批门。
- 阶段 A 至少产生一个 `library-approved` 组件，不设三个组件的数量 KPI。
- 公共版本使用不可变整数版本 `v1`、`v2`；任何源码或合同变化都创建新版本。
- 组件兼容只记录 `Profile + subtemplate`；画幅由 Work 与 Subtemplate 负责。
- 现有 `hyperframes-codex-workflow` 直接读取 `COMPONENT.md`，MVP 不新增 Registry 或 Planner Skill。
- 正式 Plan 批准后，把精确组件源码复制进 Work；公共库升级不得改变既有 Draft。
- 跨 Work 复用只有在相同 `component_id@vN` 且不修改内部 DOM、样式结构或 GSAP 编排时成立。

### 正常缺口处理

- 库中有合适组件时，由正式 Plan 提出并通过整体批准确认。
- 缺少组件时，Codex 先为当前 Work 实现 `custom:<slug>`。
- Plan 记录 `new` 或 `revise:<component_id>`、语义任务、状态变化和不复用原因。
- 不新增独立 Backlog；需要时扫描私有 Work 的 Plan 汇总。
- Work-local custom 只能作为后续参考和计数证据，不能直接跨 Work 依赖。
- 用户统一安排哪些缺口交给 Kimi/Open Design 新增或修改设计。

## 两阶段验收

| 阶段 | 目标 | 完成条件 |
|---|---|---|
| A：设计沉淀 | 证明 Component Brief、Open Design 共建、确认、入库和 Work 落地链路 | 当前 Work 至少产生一个 `library-approved` 组件，并完成正式 Plan、可编辑 Draft、HyperFrames Check 与关键帧像素 QA |
| B：跨 Work 复用 | 证明组件库确实降低下一条 Work 成本 | 后续真实 Work 原样使用至少一个相同 `component_id@vN`，不经 Kimi 重建，不改内部实现，并完成正式 Plan 与 Draft QA |

只完成阶段 A 不代表组件复用价值已被证明。阶段 B 不在当前任务中提前创建。

## 四象限审查

### 已知且确定

- 当前验收 Work、Variant、Template、Profile、Subtemplate 和目标 `4:3` 已明确。
- 用户亲自确认具体组件和内部动效。
- 正式 Plan、Draft 接受和 Final QA 的既有权威边界保持不变。
- 公共组件和 Work 副本必须可离线、可 seek、可独立 Preview 和 render。

### 执行时再确定

- 用户稍后提供的 Open Design project/file revision。
- Open Design 对当前场景提出的组件数量、Anchor 覆盖和搭配方式。
- 每个组件最终视觉参数、Slots 和 Motion Recipe。
- 阶段 B 使用哪一条后续真实 Work。

这些输入不改变产品边界，不阻塞 PRD。

### 隐含假设

- 当前真实场景至少能形成一个值得 `library-approved` 的组件。
- Kimi/Open Design 交付的 HyperFrames 实现可被本地直接采用并规范化为 seek-safe 生产实现，而不改变已验收效果。
- 后续真实 Work 能找到至少一个语义匹配的相同版本完成阶段 B。

### 主要盲区与控制

- 组件粒度过大或过小：通过 Component Brief、独立 Slots 和第二条 Work 复用检验。
- 原型链接继续变化：通过 revision 或 bundle SHA-256 冻结。
- 为数量 KPI 强拆组件：取消“至少三个组件”要求。
- 作品专属设计污染公共库：同次确认区分 `work-local` 与 `library-approved`。
- 公共升级破坏旧 Draft：不可变版本加 Work 本地副本。
- 缺口台账漂移：不另建 Backlog，按需扫描 Plan。

## Q&A

| Q-ID | 问题 | 决定 | 状态 |
|---|---|---|---|
| Q-001 | 是否引入“子 Profile”？ | 否，继续正式命名 `subtemplate`。 | 已决定 |
| Q-002 | MVP 覆盖几个 Profile？ | 仅 `optical_fluidity`。 | 已决定 |
| Q-003 | MVP 是否要求首个 Work 复用三个组件？ | 否。阶段 A 至少沉淀一个公共组件，阶段 B 跨 Work 复用至少一个相同版本。 | 已修订 |
| Q-004 | 组件兼容是否包含画幅？ | 否，只使用 `Profile + subtemplate`；画幅由 Work/Subtemplate 负责。 | 已决定 |
| Q-005 | 组件设计由谁确认？ | 用户与 Kimi 共建并由用户确认；Kimi 不负责整支视频。 | 已决定 |
| Q-006 | 本次正式 Plan 何时写？ | 先写一次性 Animation Draft，组件完成后再写正式 Plan。 | 已决定 |
| Q-007 | Animation Draft 能否选择预设组件？ | 不能，只写 Component Brief。 | 已决定 |
| Q-008 | Open Design 与仓库谁是真源？ | 确认前 Open Design；落库后仓库不可变版本。 | 已决定 |
| Q-009 | 如何冻结 Open Design？ | 稳定 revision 优先，否则完整 bundle SHA-256。 | 已决定 |
| Q-010 | Codex 能否修改原型代码？ | 以直接采用完整 artifact 为原则，只做生产兼容规范化，不改变确认过的视觉和编排。 | 已决定 |
| Q-011 | 落地时允许怎样重定时？ | 只允许整体 offset/timeScale 与 Hero/Handoff 静止保持；不得重排内部 Beat，失真则退回设计。 | 已决定 |
| Q-012 | 是否新增 Registry 和 Planner Skill？ | MVP 不新增，现有 Skill 直接读取组件合同。 | 已决定 |
| Q-013 | 是否自动把确认组件都入库？ | 否，区分 work-local 与 library-approved。 | 已决定 |
| Q-014 | 公共组件如何版本化？ | 不可变整数版本 `vN`。 | 已决定 |
| Q-015 | Work 如何依赖组件？ | Plan 批准后复制精确源码和 hash，不运行时链接公共库。 | 已决定 |
| Q-016 | 正常路径缺少组件怎么办？ | Codex 先做 Work-local custom，Plan 记录缺口，用户后续统一安排设计。 | 已决定 |
| Q-017 | 缺口如何统计？ | 扫描私有 Work 的 Plan，不维护独立 Backlog。 | 已决定 |
| Q-018 | 阶段 A 使用哪个 Work？ | 使用当前 `work-20260821-一个人做号太累-先装这10个skill/main`，不新建。 | 已决定 |
| Q-019 | 当前 Work 画幅是什么？ | `4:3`；创建时的 `9:16` 是错误默认值。 | 已决定 |
| Q-020 | Open Design 创建什么，本地调用什么？ | Open Design 创建可运行 HyperFrames 组件和内部动效模板；本地检索、命名、版本化并调用。 | 已决定 |
| Q-021 | 文案、颜色、Slots 和媒体由谁处理？ | 本地先规范化语义输入，再落地最终文案/Slot 合同/Profile 颜色/真实媒体；Open Design 使用示例文字、原设计颜色和可替换占位。 | 已决定 |
| Q-022 | Open Design 如何验收组件搭配？ | 每个组件交付独立 Preview，另交付一个短的代表性 `combination preview`；不制作整片。 | 已决定 |
| Q-023 | Open Design 验收后冻结什么？ | 冻结拆分/搭配、视觉结构、关键状态和可感知动效；不冻结最终文案、精确颜色、真实媒体、Slot API、生产 ID 和绝对时间。 | 已决定 |
| Q-024 | 生产落地如何处理 artifact 和时间？ | 优先直接采用完整 artifact；只做必要规范化、整体 offset/timeScale 和静止保持，可见差异必须重新确认。 | 已决定 |

## 未决执行输入

无阻塞产品决策。当前 `ANIMATION_DRAFT.md` 已更新；下一步等待用户提供已确认的 Open Design project/file revision。组件数量、Anchor 覆盖、具体搭配和阶段 B Work 属于执行输入，不是 PRD TODO。
