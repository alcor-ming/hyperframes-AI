# HyperFrames Component Motion PRD

状态：已确认，阶段 A Plan 已批准，生产复用闭环待实现

上位 PRD：[PRD_MASTER.md](./PRD_MASTER.md)

决策依据：[component-driven-motion-vnext.md](./_ledger/component-driven-motion-vnext.md)

日期：2026-08-24

## 1. 模块目标

在 `hyperframes_video` 的 `pure_hyperframes` 视觉规划阶段建立最小可用组件库。首批组件来自真实 Work 中由用户确认的设计，不来自预设清单；后续由现有 `hyperframes-codex-workflow` 根据 `Profile + subtemplate` 直接读取组件合同并在 `ANIMATION_PLAN.md` 中提出使用方案。

模块必须降低重复实现成本，但不能把创作降级为固定模板拼接，也不能绕过用户对组件、动效和正式 Plan 的确认。

## 2. 术语

### Profile

视觉身份与约束集合。MVP 只允许 `optical_fluidity`。

### Subtemplate

Profile 下的展示架构，不是子 Profile：

- `hero_flow`：主视觉随语义转折变化。
- `module_stage`：同类模块共享讲解舞台。

组件兼容只使用 `Profile + subtemplate`。画幅由 Work 和 Subtemplate 负责，不在组件合同中作为第三个兼容键重复维护。

### Animation Draft

本次验收 Work 独有的临时设计简报 `ANIMATION_DRAFT.md`。它提供本地预规范化的语义目标、真实长度样例、素材条件和事实边界，不引用预设组件，不是正式视觉 PRD，也不授权生产 HTML。

### Component Brief

交给用户与 Kimi 的语义需求合同。它定义每个 Anchor 要介绍什么、观众应理解什么、输入长度/类型、素材条件与事实边界，但不预设组件数量、类型、Hero States、Motion Recipe、DOM 或 Slot API。

### Component

一个可复用的语义视觉机制。它必须有明确叙事用途、Required/Optional Slots、起始状态、Hero State、结束状态、默认 Preview 和至少一个有限 Motion Recipe。按钮、标签、颜色 token 或普通 `fade-in` 不算 Component。

### Motion Recipe

与某个 Component 同版本维护的 GSAP 编排。它描述组件内部有限状态变化和因果顺序，不拥有跨 Scene 转场。

### Work-local

只为一个 Work 使用的实现。它可以完成当前 Draft，但没有公共组件 ID，不得被其他 Work 运行时依赖，也不计入公共复用。

### Library-approved

用户明确允许进入公共组件库的实现。它获得不可变 `component_id@vN`，并接受独立 Preview、seek、Slots 和像素 QA。

### Component Release

一个不可变 `component_id@vN` 的自包含发布包。它拥有语义合同、输入 Schema、实现、默认 Fixture、hash 清单和基线，不拥有后续 Case 或 Work Binding。

### Fixture

用于验证 Slot、文案长度、媒体缺失和时长边界的合成输入。默认 Fixture 随发布包冻结；后续 Fixture 以独立不可变目录追加。Fixture 证明组件不会坏，不证明真实场景适用。

### Case

从真实 Work 中脱敏出的语义适用、Binding 摘要与验收证据。Case 独立追加且版本不可变，只能证明 `COMPONENT.md` 已声明范围内的用法，不能扩大组件合同。

### Work Binding

当前 Work/Scene 对 vendored Component Release 的外层绑定，只允许 Slots、位置、尺寸、offset、整体 timeScale、Hero/Handoff hold 和 Work 本地媒体引用。它随 Preview Snapshot、Accepted Draft 和 Final 冻结。

### Composition Evidence

两个或多个组件在真实 Work 中的接力、重叠、Hero 保持和遮挡检查证据。它是追加式证据，不自动成为公共转场资产。

### Element Release

至少被两个公共组件稳定复用的内部视觉或动效机制。Element 只在开发期共享；组件发布时 vendoring 为自包含副本，Work 不建立运行时动态依赖。Beta 1 只定义边界，不发布 Element。

## 3. 两条流程

### 3.1 长期正常流程

1. 按现有规则读取当前 Work、Variant、Script、Research、Recipe 和一个 Profile。
2. 根据信息结构选择一个 Subtemplate。
3. 形成 Motion Thesis、Beat Graph 和 Plan 内的 Scene Semantic Brief；不新增并列的 `SCENE_SEMANTICS.md` 真源。
4. `hyperframes-codex-workflow` 读取 Component Release 与 Case 的轻量 frontmatter，先做硬约束过滤，再按语义职责、状态变化和反例筛选。
5. 有合适组件时，在正式 `ANIMATION_PLAN.md` 中引用精确 `component_id@vN`、匹配 Case（若有）、Motion Recipe 与 Component Match Record。
6. 没有合适组件时，在 Plan 中写 `custom:<slug>` 和结构化缺口。
7. 用户整体批准 Plan。
8. 批准后复制公共发布包并创建 Work Binding/Lock，或为当前 Work 实现 work-local custom。
9. 完成 G0-G6 与 G8、关键帧和 Anti-PPT 像素检查，再注册 Draft。

### 3.2 本次临时流程

仅用于 `work-20260821-一个人做号太累-先装这10个skill/main`：

1. 基于真实输入先创建 `ANIMATION_DRAFT.md`。
2. 用户与 Kimi 根据 Component Brief 在 Open Design 中提出组件拆分，并共建可独立 Preview/seek 的 HyperFrames 组件、内部 GSAP 和一个简短的代表性组合 Preview；不完成整支视频设计。
3. 用户确认具体 artifact revision，并将每个组件判定为 `work-local` 或 `library-approved`。
4. Codex 通过 Open Design 读取一次完整 artifact bundle；没有稳定 revision 时计算 SHA-256，并将设计内容位置规范化为最终 Slot 合同。
5. Codex 根据已确认组件正式完成 `ANIMATION_PLAN.md`。
6. 用户整体批准正式 Plan。
7. Codex 才把公共版本写入 `.studio/components/`，复制精确源码进 Work，并完成全片组合、跨 Scene 转场、口播时间对齐和 QA。
8. `ANIMATION_DRAFT.md` 标记 `superseded_by: ANIMATION_PLAN.md`，不再参与后续实现。

当前 Work 的 Open Design 组件与组合 Preview 已冻结，B00 已标记为唯一 `library-approved` 目标，P001-P012 保持 `work-local`；`ANIMATION_PLAN.md` revision 2 已于 2026-08-25 整体批准。下一步是生产发布包、Work Binding/Lock 与阶段 A 验收，不重新打开设计共建或批量公共化 P001-P012。

## 4. 功能需求

### HCM-001｜保留 Harness 权威边界

- `hyperframes-codex-workflow` 继续作为唯一视频工作流入口。
- `ANIMATION_PLAN.md` 继续是正式 HTML 前唯一必须整体批准的视觉 PRD。
- `ANIMATION_DRAFT.md` 不新增 Variant 状态、审批门或全局模板，仅是当前 Work 的一次性过程文件。
- Draft 接受、Final、Archive 和发布权限保持不变。
- `talking_head` 与 `podcast_quote_image` 不加载组件库。

**验收**：没有组件引用的历史 Variant 可继续走旧路径；当前临时 Draft 不改变 `./work` 状态机。

### HCM-002｜Subtemplate 与画幅边界

- 新的 `optical_fluidity + pure_hyperframes` 正式 Plan 必须声明且只声明一个 `subtemplate`。
- 故事、命题、案例和变化流程优先 `hero_flow`；同类列表、工具集、课程或重复比较优先 `module_stage`。
- 当前验收 Work 使用 `module_stage + 4:3`。
- 组件兼容只声明 `profile` 与 `subtemplate`；画幅适配由 Work 组合层负责。
- 新的非默认画幅不得仅因 `Profile + subtemplate` 相同就宣称已完成 QA，必须留下真实 Work 验证证据。
- Plan 批准后改变 Subtemplate 必须提高 Plan Revision 并重新整体批准。

**验收**：当前 Work 的 Variant 与正式 Plan 都是 `4:3`；Subtemplate 缺失、未知或双重时在生产实现前停止。

### HCM-003｜本次 Animation Draft 合同

`ANIMATION_DRAFT.md` 至少包含：

- `status: design_brief`、当前 Work/Variant、Profile、Subtemplate 和目标画幅；
- 每个 Script Anchor 的时间区间、这一段要介绍什么、观众应理解什么；
- 本地预规范化的语义字段、数据类型、真实长度样例和必需/可选性；
- 可用素材条件、Profile/Subtemplate 硬边界与事实禁区；
- 设计 AI 需要交付的独立 HyperFrames Preview 和代表性 `combination preview`。

不得包含：

- 预设组件数量/类型、`component_ref`、Hero State 或 Motion Recipe ID；
- 预先指定 DOM、Slot API、组件库实现或具体视觉外观；
- 要求原样上屏的最终文案；
- `approved` 状态或生产 HTML 授权。

**验收**：Kimi 能据此理解内容结构并自由提出组件，但不会被文案、预设组件或生产 API 限制。

### HCM-004｜Open Design 共建与冻结

用户与 Kimi 在 Open Design 负责组件级设计与效果实现：

- 自由提出组件数量、类型、Anchor 覆盖和搭配方式，由用户确认；
- Opening/Build/Hero/End 关键状态与组件内部有限 GSAP 动效；
- 可替换内容位置及容量，但不定义最终 Slot API；
- 不含 Work 私有素材的默认 Preview 数据；
- 每个组件可独立 Preview、pause、seek 和 render 的 HyperFrames 实现；
- 一个在当前画幅与 Subtemplate 中展示代表性组合、接力或切换的简短 `combination preview`。

本地工作流在 Open Design 前规范化语义输入，落地时负责查库与选择 `component_id@vN`、调用组件和 Motion Recipe、最终文案、Slot 合同、Profile 颜色映射、真实媒体、全片 Scene 排列、跨 Scene 转场、口播时间对齐与项目级 QA。Open Design 不负责这些生产决定。

Open Design 可沿用原设计颜色或使用参考色验证动效和组件搭配；精确 Profile 配色不是本次验收项。真实截图、视频、品牌图标和字体由本地提供；Open Design 可创建组件内生的 HTML/CSS 图形和通用装饰，但不得引入运行时网络或临时外链。

用户确认时必须指定 Open Design project/file 和稳定 revision；若 revision 不稳定，Codex 对完整 artifact bundle 计算 SHA-256。确认结果同时标记 `work-local` 或 `library-approved`。

确认前 Open Design artifact 是组件设计真源；正式 Plan 批准并落库后，`.studio/components/` 中的不可变版本成为生产真源。冻结的 Open Design artifact 只作为设计证据，不是运行时依赖。

冻结面包含组件拆分与搭配、视觉结构、关键状态和可感知的内部动效。最终文案、精确 Profile 颜色、真实媒体、Slot API、`component_id@vN` 和 Scene 绝对时间不冻结；但它们若在落地后破坏已冻结效果，必须重新确认。

**验收**：正式 Plan 能唯一指向用户确认的 artifact，且同时存在独立 Preview 与组合 Preview；之后 Open Design 的修改不能静默改变已确认版本。

### HCM-005｜最小组件库与 Skill 加载

公共组件真源使用：

```text
.studio/components/
└── <component-id>/
    ├── vN/                         # 不可变 Component Release
    │   ├── COMPONENT.md
    │   ├── component.html
    │   ├── contract.schema.json
    │   ├── preview.fixture.json
    │   ├── HASHES.json
    │   └── baselines/
    ├── fixtures/                   # 后续追加的边界 Fixture
    │   └── <fixture-id>/vN/
    └── cases/                      # 真实 Work 脱敏 Case
        └── <case-id>/vN/
            ├── CASE.md
            ├── slots.json
            ├── timing.json
            └── acceptance/
```

MVP 不新增 `registry.json` 或 Component Planner Skill。现有 `hyperframes-codex-workflow`：

1. 发现 `.studio/components/**/COMPONENT.md`；
2. 发现 `.studio/components/*/cases/**/CASE.md` 与 `.studio/components/*/fixtures/**`；
3. 先读取 frontmatter 中的 ID、版本、Profile/Subtemplate、语义轴、反例、Slot/资产需求和时长边界；
4. 只为当前 Beat 加载最小数量的匹配合同与 Case；
5. 由 Agent 根据语义职责和状态变化选择，不使用关键词硬路由、向量数据库或自动评分。

发布包与 Case/Fixture 分离：新增 Case 或额外 Fixture 不得修改既有 `vN` 目录，也不得改变该发布包的 package hash。

**验收**：新增组件只新增一个不可变版本目录；新增 Case/Fixture 只追加独立目录；不需要同步第二份 Registry，也不修改按组件 ID 分支的代码。

### HCM-006｜组件合同

每个 `COMPONENT.md` 必须定义：

- `id`、整数 `version`、`library-approved` 状态；
- 唯一 `profile` 与一个或多个已确认 `subtemplate`；
- 结构化语义字段：`communication_goal`、`semantic_roles`、`information_shapes`、输入/变化/输出状态、`evidence_modes`、内容密度、时长范围、进入/退出合同；
- semantic jobs 与 `anti_use_cases`；
- Required/Optional Slots；
- 主对象、Opening、Build、Hero 和 End/Handoff 状态；
- Motion Recipe、默认时长、允许的整体 timeScale 和 Hero/Handoff 静止保持；
- 允许的资产类型与本地路径约束；
- Profile token 使用方式；
- Anti-PPT 风险、布局安全区和硬禁项；
- 默认 Preview 数据与关键检查时间点；
- 允许作品定制的边界；
- 对应 Open Design artifact hash 或可公开的冻结证据。

`contract.schema.json` 固化 Slot 类型、Required/Optional、长度/数量边界、资产类型和允许的时间范围；`preview.fixture.json` 提供不含 Work 私有数据的典型输入。后续扩大 Schema、时长范围或安全区必须发布新组件版本，不能用 Case 绕过。

作品文案、用户媒体、截图、生成图和真实指标不得进入公共目录。准确内容通过 Slots、HyperFrames Variables 或 Work 本地路径绑定。

**验收**：组件不依赖 Work 私有资产也能独立 Preview；最长中文和缺失 Optional Slot 不溢出或造成空白故障。

### HCM-007｜Motion Recipe 与生产翻译

每个 Recipe 必须定义：

- `recipe_id` 与语义目的；
- 映射到 Profile 的 Motion Verb；
- 有限阶段顺序；
- 每阶段目标元素、起止状态、默认时长和 easing；
- Hero State 形成点和最终 Hold；
- seek、重放和缺失 Optional Slot 行为。

生产实现必须：

- 使用单一 paused GSAP timeline 或组件自有的有限 timeline；
- 使用明确起止状态，优先 `fromTo()`；
- 不使用 wall clock、无限循环、未播种随机数或运行时网络；
- 不跨 Sub-composition 边界选择宿主元素；
- 不以背景漂浮、扫光或相机炫技代替功能状态变化。

Open Design 以 HyperFrames 形式创建组件和内部 Motion Recipe 本体；本地工作流负责查库、选择、命名、版本化和调用，不重新凭效果仿写。Codex 优先直接采用完整 artifact 代码，只可为 Slots、Profile 颜色映射、本地素材、seek-safe、离线渲染与 Work 隔离做最小规范化。

集成层只允许修改 Slots、位置、尺寸、整体 `offset`/`timeScale` 与 Hero/Handoff 静止保持；不得重排内部 Beat 或改变因果顺序。若任一规范化产生可感知差异，必须退回用户与 Kimi 确认。

**验收**：任意检查时间直接 seek 与顺序播放一致；技术翻译后的关键状态和动效行为与冻结 artifact 一致。

### HCM-008｜正常选择与缺口记录

正常路径先在 `ANIMATION_PLAN.md` 为 Scene/Beat 写 Scene Semantic Brief：

| 字段 | 含义 |
|---|---|
| `communication_goal` | 观众在本 Beat 后必须理解什么 |
| `semantic_roles` | orientation、transition、compare、resolve 等叙事职责 |
| `information_shapes` | ordinal、title、short_summary、optional_evidence 等信息结构 |
| `state_change` | 输入状态、转换、输出状态 |
| `evidence_mode` | none、optional、required |
| `content_density` | low、medium、high |
| `duration_budget` | 可用时长与 Hero hold |
| `entry_contract` / `exit_contract` | 接受与输出何种 Handoff |
| `must_not` | 不得承担的职责和事实边界 |

组件选择按以下顺序判断：

1. Profile、Subtemplate、依赖、资产、Slot Schema、安全区和时长范围硬过滤；
2. 叙事职责与信息结构匹配；
3. 输入/变化/输出状态匹配；
4. `anti_use_cases` 与 Scene `must_not` 检查；
5. 典型/边界 Fixture 与已有真实 Case 是否覆盖当前 Binding；
6. 在 Plan 中形成可审计 Component Match Record。

不得为了复用数量强塞组件，或让连续 Scene 只换文字和颜色。

没有合适组件时使用 `custom:<slug>`，并在正式 Plan 的 Component Gap 表记录：

| 字段 | 含义 |
|---|---|
| `gap_type` | `new` 或 `revise:<component_id>` |
| Scene / Beat | 出现缺口的位置 |
| semantic job | 需要解决的叙事任务 |
| state change | 所需起止状态与 Hero State |
| reason | 为什么现有组件不匹配 |
| local_ref | 当前 Work 的 `custom:<slug>` |

批准后由 Codex 先完成 Work-local 实现。它不自动入库；以后即使再次出现，也只能作为参考并使缺口计数加一，不能直接跨 Work 依赖。用户统一安排新增或修改设计后，才可按 HCM-004 至 HCM-007 发布公共版本。

不新增独立 Backlog；需要统计时扫描私有 Work 的 Component Gap 表。

Component Match Record 至少记录：

| 字段 | 含义 |
|---|---|
| `selected_component` | 精确 `component_id@vN` |
| `matched_case` | 可选的精确 `case-id@vN` |
| `fit_reason` | 语义职责、状态变化与边界为何匹配 |
| `anti_use_check` | 未命中的反例与事实边界 |
| `rejected_candidates` | 相关候选及拒绝原因，不要求罗列全库 |
| `fallback` | 失败关闭到 `custom:<slug>` |

**验收**：每个 custom 都能追溯到真实缺口；统计不会把作品私有内容复制进 Git。

### HCM-009｜正式 Animation Plan

正式 `ANIMATION_PLAN.md` 继续包含 Motion Thesis、Beat Graph 和 Component Plan。Component Plan 至少包含：

| 字段 | 含义 |
|---|---|
| Scene / Beat | 对应时间单元 |
| `component_ref` | `component-id@vN` 或 `custom:<slug>` |
| `motion_recipe` | 已确认 Recipe；custom 可写待实现语义链 |
| Slots | 当前作品注入的文本、数据、图标或媒体角色 |
| Scene Semantic Brief | 叙事职责、信息结构、状态变化、证据、时长与 Handoff 合同 |
| Selection reason | 为什么适合当前状态变化 |
| Component Match Record | 匹配 Case、反例检查、相关拒绝候选与 fallback |
| Artifact evidence | Open Design revision 或 bundle SHA-256，已有公共组件可引用合同 hash |
| Combination evidence | 当前搭配在 Open Design `combination preview` 中的对应关系 |
| Customization | 允许的 Slots、位置、尺寸、offset、timeScale 和 Hero/Handoff 静止保持 |

当前临时流程中，正式 Plan 必须在组件设计与 artifact 确认后写成。Plan 批准冻结 Subtemplate、Component Ref、Motion Recipe、Scene Hero State 和语义 Slots。

**验收**：只阅读正式 Plan 即可知道每个 Scene 使用什么组件、什么状态变化、来自哪个已确认 artifact，以及允许怎样适配。

### HCM-010｜版本、安装与 Work 冻结

- 公共版本只使用递增整数 `v1`、`v2`，不引入 SemVer。
- `library-approved` 版本目录不可覆盖；源码或合同发生任何变化都创建下一版本。
- 正式 Plan 批准前不向公共库或 Work Project 安装组件生产源码。
- 批准后将指定版本写入公共库，并复制完整、自包含的发布包到当前 Work 的 `project/vendor/components/<component-id>/vN/`。
- Work 的准确内容与时间适配写入 `project/component-bindings/<scene>.<component-id>.json`，不得写入 vendored package。
- Work 通过 `project/COMPONENT_LOCK.json` 记录 `component_ref`、来源证据、公共 package hash、Work 副本 package hash、一个或多个 Binding 路径/hash 和安装文件；同一发布包在同一 Work 内只 vendor 一次，可绑定多个 Scene。
- Work 只从 vendored 副本渲染；断开公共组件目录和 Open Design 后仍须 Preview/Render。
- 公共库升级、Open Design 后续编辑或其他 Work 修复不得改写该副本、Preview Source Snapshot 或 Accepted Draft。
- Work 内允许 Slots、位置、尺寸、offset、整体 timeScale 和 Hero/Handoff 静止保持；内部 DOM、样式结构或 GSAP 编排变化必须成为新公共版本或保持 work-local。

package hash 使用 `component-package-sha256-v1`：

1. 排除 `HASHES.json` 本身；
2. 对其余每个文件的实际字节计算 SHA-256；
3. POSIX 相对路径按字典序排列；
4. 拼接 UTF-8 清单行 `<file_sha256>  <relative_path>\n`；
5. 对完整清单再次计算 SHA-256，写入 `HASHES.json`；
6. Work 副本以同一算法复算，必须与公共源相等。

`vendor/`、`component-bindings/` 和 `COMPONENT_LOCK.json` 是 component-driven Work 的 Snapshot 输入。Harness 必须在不破坏历史 Work 的前提下，把存在的这些可选项复制进 Preview Source Snapshot，并随 Accepted Draft、Final 与 Archive 冻结。

**验收**：断开公共组件目录与 Open Design 后，已安装 Work 仍可 Preview 和 Render；相同版本的公共源不可被静默修改。

### HCM-011｜失败边界

- Open Design artifact 无法唯一解析、引用文件不完整或 hash 不一致：停止生成正式 Plan。
- 组件 ID/版本重复、合同缺失、入口不存在或版本被覆盖：进入实现前停止。
- 公共 package hash、Work 副本 hash 或 Binding hash 不一致：停止集成、Snapshot 或复用认定，不自动修复 vendored 文件。
- Profile/Subtemplate 不匹配：失败关闭到 `custom`，不回退任意组件。
- Scene 语义职责或状态变化不匹配、命中反例、需要扭曲原文才能复用：失败关闭到 `custom`。
- Required Slot 或本地资产缺失：保留 Plan Slot 或进入现有等待状态，不伪造内容。
- 组件未通过独立 HyperFrames Check：先修复技术问题；若改变视觉、语义机制或内部编排，退回用户确认并发布新版本。
- 画幅变化导致已验证布局失效：作为 Work-local 适配或新设计缺口，不伪称公共组件已验证。

**验收**：失败在生产 HTML 或 Draft 注册前暴露，并保留准确 Work 状态。

### HCM-012｜验收 Gate 与证据

| Gate | 验收内容 | 必须保留的证据 | 失败处理 |
|---|---|---|---|
| G0 来源完整性 | 冻结 artifact 唯一、revision/hash 与文件完整 | artifact ref、source hash | 中止生产化 |
| G1 合同完整性 | 语义字段、Schema、Required/Optional Slot、默认/边界 Fixture、timeScale、资产回退 | contract/fixture report | 中止 HTML 集成 |
| G2 语义适配 | Scene Semantic Brief、Match Record、反例和相关拒绝候选 | Plan 内 Match Record | 回退 `custom` |
| G3 视觉边界 | 最短/典型/最长文案、有/无 evidence、安全区和溢出 | keyframes、overflow report | 新版本或 `custom` |
| G4 动效确定性 | Opening、Build、Hero、End、repeat-seek、无状态累积 | seek report、pixel diff | 中止 Draft 注册 |
| G5 组合与交接 | overlap、handoff、Hero hold、无空帧和错误遮挡 | 组合关键帧 | 只调整外层 Binding/编排；超界则修订 Plan |
| G6 安装完整性 | 公共源和 Work 副本 package hash 一致、Binding hash 可复算、离线渲染 | `COMPONENT_LOCK.json`、offline render | 中止 Snapshot |
| G7 跨 Work 复用 | 第二个真实 Work 使用同一版本且未改内部实现 | 两个 Work 的 Lock、Binding、render/diff | 不得标记 `reused` |
| G8 冻结与归档 | Plan、Binding、Vendor、Lock 和 QA evidence 随 Snapshot/Draft/Final 冻结 | archive manifest | 不得完成阶段 |

G2 必须独立回答：职责是否一致、是否扭曲原文、是否命中反例、是否应选更直接组件或 `custom`。像素稳定不能替代语义正确，语义正确也不能替代渲染确定性。

新 Work 的 Draft 继续执行项目级时长、布局、媒体解码、关键帧和像素检查。源码检查不能替代渲染画面检查。

### HCM-013｜两阶段真实 Work 验收

#### 阶段 A：当前 Work

`work-20260821-一个人做号太累-先装这10个skill/main` 必须：

- 使用 `pure_hyperframes + optical_fluidity + module_stage + 4:3`；
- 先完成不含预设组件的 `ANIMATION_DRAFT.md`；
- 由用户与 Kimi 共建实际需要的 HyperFrames 组件与内部 GSAP，数量由场景决定；
- 同时交付并验收独立 Preview 和简短的代表性组合 Preview；
- 至少一个组件被用户标记为 `library-approved`；
- 正式 Plan 记录冻结 artifact 与精确组件版本并整体批准；
- 完成不可变公共发布包、Work vendor 副本、Binding/Lock、可编辑 HTML、G0-G6/G8 和 Draft 注册；
- 阶段 A 完成状态只能是 `production-installed`，不能提前写成 `reused`。

#### 阶段 B：后续真实 Work

另一条真实 Work 必须：

- 来自用户真实内容需求，不为测试预造，且先完成 Scene Semantic Brief 再选择组件；
- 直接引用阶段 A 的至少一个相同 `component_id@vN`；
- 只替换 Slots，并允许位置、尺寸、offset、整体 timeScale 与 Hero/Handoff 静止保持；
- 不修改内部 DOM、样式结构或 GSAP 编排；
- 不交给 Kimi 重建；
- 完成正式 Plan、Match Record、vendor/Binding/Lock、可编辑 Draft 与 G7；
- G7 通过后才标记 `reused`，并可从该 Work 脱敏追加第一个真实 Case；新增 Case 后原 package hash 必须不变。

只完成阶段 A、只生成组件清单、只通过单组件 Preview、复用 CSS token，或复制后重写内部实现，均不能证明跨 Work 复用。

### HCM-014｜贡献与演进

后续独立任务按下表选择动作，不新建常驻组件平台：

| 变化 | 动作 |
|---|---|
| 同一语义职责和合同下出现新的真实用法 | `add-component-case`，追加不可变 Case |
| 只验证最长文案、无 evidence、最短时长等边界 | 追加 Fixture |
| Work 只调整允许的外层参数 | 新增或修改 Work Binding |
| Slot/类型/时长范围/安全区/内部 DOM/CSS/状态顺序/GSAP beat 改变 | `revise-component`，发布下一整数版本 |
| 叙事职责改变 | `promote-component`，创建新组件 |
| 需求只服务当前作品、品牌或私有媒体 | 保持 Work-local |
| 同一内部机制在至少两个公共组件中稳定重复 | 创建 Element 候选；开发期共享，发布期 vendoring |

`add-component-case` 必须验证合同范围、反例、Schema、关键状态、repeat-seek、组合交接、脱敏和发布包 hash 不变。Case 不得携带 Work 文案、真实媒体、私有链接、Cookie、凭证或运行状态。

只有同一组合机制在至少两个真实 Work 中形成 Composition Evidence 后，才允许单独评估 Composition Recipe；Beta 1 不预建通用转场库。

## 5. 首批组件产生规则

- 设计共建前 PRD 不预设组件 ID、数量、视觉外观或 Motion Recipe；设计冻结后允许正式 Plan 记录真实结果。
- 当前 `ANIMATION_DRAFT.md` 只给本地预规范化的语义输入，由 Open Design 提出组件拆分与具体设计，再由用户确认。
- 同一次用户确认可将组件标记为 `work-local` 或 `library-approved`，不增加独立审批门。
- 阶段 A 至少需要一个 `library-approved` 组件，其余按真实场景决定。
- 当前真实结果只有 B00 获准成为 `chapter-intro@v1` 公共目标；P001-P012 均保持 Work-local，不是待批量公共化的 Backlog。
- 作品专属名称、数字、截图、AI 图片、CTA 和 Scene 转场不得进入公共实现。
- 历史 Work 只提供机制证据或参考，不自动抽取成首批组件。

## 6. Anti-PPT 约束

- Subtemplate 可以复用舞台，但连续 Scene 必须让组件内部机制随语义变化。
- `module_stage` 的重复单元不能只替换标题、颜色和图标。
- `hero_flow` 不得把不同 narrative job 填入同一个中央卡片。
- 入场不是状态变化；组件出现后必须 build、connect、transform、handoff、compare 或 resolve。
- 跨 Scene 转场继续由正式 Animation Plan 按叙事连续性设计，不建立通用 Wipe 组件库。

## 7. 数据与权限

- 公共组件库只保存代码、合同、Schema、Fixture、脱敏 Case、验收证据和无版权风险的通用图形。
- Work 文案、媒体、截图、Open Design 私有链接、Draft 和运行状态继续留在 `works/`，不得进入 Git。
- 真实截图、视频、品牌图标与字体由本地工作流获取、验证并注入；Open Design 仅使用已确认副本或可替换占位。
- 公共 `COMPONENT.md` 可保存 artifact hash，但不得泄露私有 Work 内容。
- 组件不得读取 Cookie、凭证、外部运行目录或未批准的网络资源。
- ImageGen 仍只在用户明确授权、正式 Plan 已批准且存在 Asset Brief 时调用。

## 8. 执行顺序

### A｜当前 Work 设计沉淀

当前 Work 的 Open Design 组件与组合 Preview 已冻结，`ANIMATION_DRAFT.md` 已被 `ANIMATION_PLAN.md` revision 2 替代，正式 Plan 已批准。下一步依次完成 `chapter-intro@v1` 发布包、规范化 hash、Work vendor/Binding/Lock、当前 Work 集成和 G0-G6/G8；不得新建 Work，不批量公共化 P001-P012。

### B｜跨 Work 复用验证

等待后续真实 Work，先形成 Scene Semantic Brief，再直接复用阶段 A 的相同组件版本并完成 G7。通过后追加第一个脱敏 Case；此阶段不在当前任务中提前创建。

### C｜统一组件设计安排

当多个 Work 产生 `new` 或 `revise` 缺口时，按需扫描 Plan 汇总；由用户统一决定哪些进入 Kimi/Open Design 新增或修改流程。

只有真实统计证明目录检索产生歧义时，才评估 Registry 或独立 Planner Skill。

## 9. PRD 完成定义

本模块 PRD 已满足：

- 用户已确认 Master PRD 与本文件的产品边界；
- 本次临时流程和长期正常流程已分开；
- 阶段 A Work、Variant、Profile、Subtemplate 与 `4:3` 已明确；
- 首批组件不预设，阶段 A/阶段 B 验收可操作；
- Registry、Planner Skill、组件浏览器和多 Profile 扩展已排除；
- Component Release、Fixture、Case、Work Binding、Composition Evidence 与 Element Release 的边界已明确；
- 发布包/案例分离、规范化 hash、Work vendoring/locking、语义匹配、演进规则和 G0-G8 已可实现；
- 当前 Work 的 Open Design artifact 与正式 Plan 已确认；下一步是阶段 A Harness 与生产复用闭环，不是创建新 Work。

## 10. Visual Payload Surface

组件的可替换视觉载荷统一建模为 `Visual Payload Surface`。Surface 是实现中稳定、可验收的 DOM 锚点；Binding 只替换 payload，卡片外壳的几何、遮罩、层级、3D、GSAP beat、Hero/Handoff 和状态顺序均冻结。普通结构卡、文本状态卡和装饰卡不得因为 class 名为 `.card` 就自动成为媒体位。

Beta 1 只定义两类 Surface：

1. `icon_node`：P001 的本地 SVG/icon 锚点。既有图标数量、位置和轨迹保持不变；只允许 Work-local 本地载荷，不允许 URL、运行时 HTML 注入或网络请求。
2. `active_media_card`：B00 以及 P002-P012 中实际承载内容、输入、输出或证据的活动卡片内容层。Surface 不拥有卡片壳和动效。

`chapter-intro@v1` 是唯一 `library-approved` 公共 Component。其 `evidence_primary` 必须显式选择 `none`、`image` 或 `video`；`none` 继续渲染程序化 fallback，`source_label` 保持独立 Content Slot。图片/视频 Binding 使用 Work-relative 本地路径，Harness 检查 DOM 一一对应、kind、路径安全、文件存在、ffprobe 摘要、内容 hash、Lock 记录和 Snapshot 闭包。视频使用 HyperFrames 的媒体属性（如 `data-var-src`、`data-media-start`、`muted`、`playsinline`）；Component 不实现 `play/pause/currentTime/requestVideoFrameCallback`。

P001-P012 始终 `work-local`，不批量公共化；它们的 Surface 目录进入现有 `scene-slots.json` 或其他既有 Work-local 数据真源。公共 B00 的多个实例仍使用各自 `component-bindings` 文件，Lock 中的媒体记录必须带具体 Binding/instance，不能把多实例压成一个全局媒体记录。Surface/Binding/实现属于同一已批准 Plan 的冻结快照；不覆盖 `component_id@vN`，合同或内部 Motion 改变时发布新版本。

首次 G6 与 Accepted Snapshot/Draft 之前，`chapter-intro@v1` 允许一次原子 RC 重建；公共包、Work vendor、Binding 和 Lock 必须同一事务闭合。该 Gate 之后 `v1` 不可覆盖，后续变化只能发布新整数版本。
