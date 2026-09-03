# HyperFrames AI vNext PRD Master

状态：产品边界已确认，待拆分实施

产品范围：Theme / Background / Component 解耦重构

风险：T3 Parent PRD

日期：2026-09-03

## 产品定位

本次重构把 HyperFrames 的视觉系统拆成三个互不替代的版本化资产：

- `Profile` 只提供语义配色与字体；
- `Background` 只提供全画幅环境层及其低强度状态；
- `Component` 提供前景信息结构、画面效果与完整动效。

`16:9` 与 `4:3` 不再共享响应式组件实现。它们属于同一个 Component Family，但分别设计、版本化、Preview 和验收。现有 `subtemplate` 与 Profile Motion Grammar 从运行时合同中移除。

这不是新的渲染器、主题组合器或自动设计黑箱。`ANIMATION_PLAN.md` 仍负责当前 Work 的资产选择、Scene 编排和用户审批，Work 仍从冻结的本地副本渲染。

## 核心问题

- Profile 当前同时拥有配色、字体、材质、构图、画幅映射、Motion Grammar 与 easing，职责过宽。
- Component 又内嵌 Profile 颜色、字体、材质、布局和 easing，导致主题与表现重复拥有同一事实。
- `Profile + subtemplate` 作为组件兼容键，使语义组件无法跨 Profile 复用。
- 单个组件同时适配多个画幅，会把独立的构图和动效设计退化为缩放或响应式折中。
- 组件自带全画幅底色或环境效果，无法独立替换背景，也难以保持跨 Scene 的视觉连续性。
- 已冻结 Work 需要继续可复现，不能通过覆盖旧公共包完成架构迁移。

## 产品目标

1. 让 Profile 严格收窄为颜色和字体的不可变主题包。
2. 建立独立 Background Family；一个 Variant 固定一个画幅实现，Scene 只调用其预定义状态。
3. 让 Component 完整拥有布局、材质、几何、字号、层级、画面效果、GSAP 编排、easing 与 Hero/Handoff。
4. 移除 `subtemplate`、Profile Motion Verb 及 `Profile` 对组件检索的影响。
5. 让同一 Component Family 的 `4x3` 与 `16x9` 实现共享语义用途和 Slot 合同，但保持独立源码与版本。
6. 一次性重构三套 Profile、四个公共 Component Family 和一个 Background Family。
7. 由 Open Design 保存设计原稿并完成集中 Gallery 验收；仓库只保存生产合同、实现、hash 与基线。
8. 保留旧 Work 的 vendored 快照与可复现性，同时禁止新 Work 使用旧合同。

## 非目标

- 不把 P001-P012 其余 Work-local 原型批量公共化。
- 不增加新的 Template、Subtemplate、Profile 继承或子 Profile。
- 不让 Component 在运行时自动适配未设计的画幅。
- 不允许每个 Scene 任意更换 Background 实现。
- 不新增 Registry 服务、向量数据库、自动评分器、组件浏览器或新的渲染运行时。
- 不修改旧 Work 的 vendor、Binding、Lock、Accepted Draft 或 Final。
- 不把 Open Design 原稿、私有链接、作品文案或媒体复制进 Git。
- 不改变媒体下载、ImageGen、平台草稿或发布权限。

## 目标架构

```mermaid
flowchart LR
    A["Profile<br/>颜色 + 字体"] --> D["Work Theme Snapshot"]
    B["Background<br/>ratio + environment states"] --> E["Variant Composition"]
    C["Component<br/>ratio + semantic contract + motion"] --> E
    D --> E
    E --> F["ANIMATION_PLAN.md"]
    F --> G["Plan Approval"]
    G --> H["Vendor + Binding + Lock"]
    H --> I["Draft + Evidence Gates"]
```

## 权责

| 层 | 拥有 | 不拥有 |
|---|---|---|
| Profile | 语义颜色、字体栈、不可变版本 | 材质、圆角、阴影、字号、字距、构图、画幅、动效、easing |
| Background | 全画幅环境 DOM/CSS、纹理、光影、低强度环境动效、预定义 Scene 状态、画幅实现 | 标题、证据、卡片、叙事信息、前景 Hero/Handoff |
| Component Family | 跨画幅共享的语义用途与 Slot 合同 | 某一画幅的具体布局与动效实现 |
| Component Ratio Release | 指定画幅的 DOM/CSS、布局、材质、字号、画面效果、GSAP、easing、Hero/Handoff、Preview 与基线 | Profile 取值、全画幅 Background、跨 Scene 编排 |
| Animation Plan | `profile_ref`、`background_ref`、`ratio`、Scene Background State、Component Ref、Slots、时间与偏离项 | 公共资产实现真源 |
| Work Binding | 当前 Scene 的 Slots、位置、尺寸、offset、timeScale、Hold 与本地媒体引用 | 修改 vendored 组件内部实现 |
| Work Snapshot | Profile、Background、Component、Binding、Lock 与验收证据的精确副本 | 反向修改公共库或 Open Design |
| Open Design | 设计原稿、两个画幅的独立设计、集中 Gallery 与用户验收证据 | Work 运行时依赖、准确作品文案、最终 Binding |

## 最小主题合同

所有 Profile 必须提供同一组 token：

```text
color.canvas
color.surface
color.text_primary
color.text_secondary
color.accent_primary
color.accent_secondary
color.positive
color.warning
color.negative

font.display
font.body
font.mono
```

Component 与 Background 只消费这些语义 token，不声明特定 Profile。它们可以使用 `transparent`、`currentColor`，也可以从 token 派生透明度或混色；不得内藏 Profile 专用 fallback。品牌 Logo、图片与视频的固有颜色不受主题 token 限制。

字体 token 只定义字体栈。字号、字重、行高、字距和排版尺度由 Component 或 Background 的具体实现负责。

## 资产与引用

```text
.studio/profiles/<profile-id>/vN/
.studio/backgrounds/<background-id>/<ratio>/vN/
.studio/components/<component-id>/<ratio>/vN/
```

引用格式：

```yaml
profile_ref: optical_fluidity@v2
background_ref: functional-field/4x3@v1
ratio: 4x3
component_ref: chapter-intro/4x3@v1
```

规则：

- `ratio` 只允许当前已设计并验收的 `4x3` 或 `16x9`。
- Profile、Background Ratio Release 与 Component Ratio Release 都使用不可变整数版本。
- 同一 Component Family 的两个画幅必须通过 Slot Schema 一致性检查。
- 一个画幅实现改变，只升级该画幅版本；不得静默改变另一画幅。
- 新 Work 的 Background 与所有 Component Ref 必须与 Variant `ratio` 一致。
- 新组件检索只使用 `ratio + semantic contract + slots/assets + duration + anti-use`，不使用 Profile 或 `subtemplate`。

## Background 运行规则

- 一个 Variant 只选择一个精确 `background_ref`。
- Background 可声明有限的命名状态，例如 `calm`、`focus-left`、`focus-center`。
- Scene 只能选择已声明状态，不能注入新背景 DOM/CSS，也不能更换 Background Release。
- Background 始终位于 Component 后方；Component 根节点必须透明，不得自带全画幅底色或环境层。
- Background 状态不得承载叙事文本、证据或替代 Component 的状态变化。
- 更换 Background Release、增加状态或改变可感知环境动效，必须提高 Plan Revision 并重新批准。

## 一次性重构范围

### Profile

- `optical_fluidity`
- `kami_editorial`
- `monochrome_atelier`

三者全部迁移到最小主题合同，并删除材质、构图、Motion Grammar、timing/easing、画幅映射和 `subtemplate` 规则。

### Component Family

- `chapter-intro`
- `rich-skill-explanation`
- `capability-convergence`
- `gap-first-selection`

每个 Family 必须交付独立的 `4x3` 与 `16x9` Ratio Release。

### Background Family

- 首个 Background 以 Open Design 中现有 `rse-functional-background` 为 `4:3` 设计起点；最终生产 ID 在 Gallery 冻结时确定。
- 同时交付独立设计的 `16x9` Ratio Release。

Open Design `Hyperframes` 项目中其余 P001-P012 原型继续保持 Work-local，不计入本次公共库范围。

## Open Design 与冻结

- Open Design `Hyperframes` 项目继续作为设计原稿真源。
- Gallery 必须覆盖 `4 Component Families x 2 ratios + 1 Background Family x 2 ratios`，共 10 个可独立 Preview/seek 的实现。
- 用户可逐项退回；只有 10 项全部通过后，整组才可进入新公共库。
- 每项冻结稳定 revision；无稳定 revision 时对完整 artifact bundle 计算 SHA-256。
- 开发仓不复制 Open Design 原稿，只记录 artifact ref、revision/hash、生产合同、实现、基线与 package hash。
- 生产翻译只允许主题 token 接线、Slots、Work 隔离、seek-safe 与离线渲染所需调整；可感知差异必须退回 Gallery 重新确认。

## 迁移与兼容

- 新资产使用 `component-contract-v2`。
- 现有公共包原样保留并标记 `legacy-profile-coupled`，不覆盖 hash，不参加新 Work 检索。
- 旧 Work 继续从原 vendored package、Binding 与 Lock 渲染。
- 新 Work 只能引用新 Profile、Background 与 Component Ratio Release。
- 迁移不改写历史 Animation Plan、Accepted Draft、Final 或 Archive。
- 新公共库整组未通过前，旧生产路径继续可用；不得形成一半新合同、一半旧合同的新 Work。

## 保持不变的能力

- Component Release 继续自包含语义合同、Slot Schema、默认 Fixture、实现、hash 清单与基线。
- 后续 Fixture 与脱敏 Case 继续采用追加式目录，不得修改既有 Release。
- Scene Semantic Brief、Component Match Record、anti-use 检查与 `custom:<slug>` 缺口记录继续有效。
- Work-local 媒体继续通过已声明 Visual Payload Surface 和 Binding 注入，并执行路径、存在性、probe、hash 与 Snapshot 闭包检查。
- Composition Evidence 继续只是组合验收证据，不自动成为公共转场或运行时依赖。
- 组件仍须 paused、seek-safe、可离线渲染；Background 也遵守相同时间确定性要求。

## 验收

1. 三套 Profile 只包含最小主题合同，不再拥有画幅、材质、构图或动效字段。
2. 10 个 Open Design Gallery 项均完成独立设计、seek、关键状态与用户验收。
3. 每个 Component Family 的两个 Ratio Release 共享相同 Slot Schema。
4. 每个 Ratio Release 分别通过三套 Profile 的主题切换、对比度、字体回退与无硬编码检查。
5. Background 与 Component 能独立 Preview，组合后层级正确且 Component 全画幅根层透明。
6. 同一 Variant 的 Profile、Background、Component 与 ratio 引用闭合，错误组合在 Draft 前失败。
7. 新 Work 的 vendor、Binding、Lock 与离线渲染可复算；公共库断开后仍可 Preview/Render。
8. 旧 Work 的 vendored 快照和既有 hash 不改变，并继续可复现。

## PRD 索引

- [组件与动效模块 PRD](./hyperframes-component-motion.md)
- [决策台账](./_ledger/component-driven-motion-vnext.md)
- [rnskill 动效分层研究](./_research/rnskill-motion-layering.md)

## 审批边界

本 PRD 只确认 Theme / Background / Component 解耦和一次性重构范围。它不授权修改 Skill、Profile、组件、Work、Open Design artifact、Git 历史或外部发布状态；实施必须另行进入 Trellis 任务并遵守 Gallery、Plan 与 Draft 的既有审批门。
