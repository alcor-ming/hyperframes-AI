# Theme / Background / Component 解耦决策台账

状态：产品方案已确认，待拆分实施

风险：T3 Parent PRD

日期：2026-09-03

## 原始概念

首次规划原文：

> 参考idea.md中的规划，参考rn-skill的设计，结合目前实际工作进行PRD规划：目前会根据所选profile、子profile选择组件+gasp动效等设计

本次重构原文：

> 当前profile与组件存在部分耦合，我当前需要分离，profile主管配色，字体，组件负责动效，画面展示效果（16:9与4:3会单独设计组件）

补充决定：

> 增加一个背景单独用作背景用途

## 真实目标

将当前由 Profile、Subtemplate 与 Component 重复拥有的视觉事实重新分层，使主题可以独立替换，背景可以跨 Scene 连续存在，组件完整拥有前景画面和动效，同时让 `4:3` 与 `16:9` 接受真正独立的设计与验收。

本轮是一次性公共系统重构，不是旧架构上的兼容补丁。旧 Work 继续从自身冻结快照渲染，新 Work 只进入新合同。

## 已确认架构

### Profile

- 只负责语义配色与字体栈。
- 不负责材质、圆角、阴影、字号、字重、行高、字距、构图、画幅、Motion Grammar、timing 或 easing。
- 三套 Profile 全部一次性迁移到同一最小主题合同。
- Profile 使用不可变版本，Work 冻结精确版本与 hash。

### Background

- 成为独立、不可变、按画幅版本化的资产类型。
- 负责全画幅底色、纹理、光影、环境层与自身低强度动效。
- 一个 Variant 固定一个 Background Ratio Release。
- Scene 只能调用该 Release 预先声明的状态，不能更换实现或注入新背景结构。
- 不承载标题、证据、卡片、CTA 或叙事内容。

### Component

- 负责前景布局、材质、几何、字号、层级、画面效果、GSAP、easing、Hero/Handoff。
- 不声明特定 Profile，不拥有全画幅 Background。
- 只消费公共主题 token；根层透明。
- 检索只看 `ratio + semantic contract + slots/assets + duration + anti-use`。

### 画幅

- 同一 Component Family 共享语义用途与 Slot Schema。
- `4x3` 和 `16x9` 分别设计、版本化、Preview、seek 和验收。
- 不允许通过缩放、裁切、media query 或通用响应式布局冒充另一画幅。
- 一个画幅改变只升级自身版本。

### 移除项

- 从运行时合同、检索、Binding 与 Animation Plan 必填字段中移除 `subtemplate`。
- 从 Profile 中移除 Motion Grammar、Motion Verb、timing/easing 和画幅映射。
- Profile 不再参与 Component 兼容过滤。

## 最小主题合同

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

允许 `transparent`、`currentColor` 以及从 token 派生透明度或混色。品牌 Logo、图片与视频的固有颜色不受主题限制。组件和背景不得内藏 Profile 专用 fallback。

## 一次性范围

### Profile Releases

- `optical_fluidity`
- `kami_editorial`
- `monochrome_atelier`

### Component Families

- `rich-skill-explanation`
- `capability-convergence`
- `gap-first-selection`
- `rse-input-transform`
- `rse-retrieve-distill`
- `rse-knowledge-roundtrip`
- `rse-persist-reuse`

每个 Family 同时交付 `4x3` 和 `16x9`。

### Background Family

- 新增一个 Background Family。
- `4x3` 以 Open Design `Hyperframes` 项目中的 `rse-functional-background` 为设计起点。
- `16x9` 单独设计。

Open Design 中其余未命名 Work-local 原型不进入本次公共化范围。

## Open Design 与生产真源

- Open Design `Hyperframes` 项目保存设计原稿。
- 集中 Gallery 覆盖 14 个 Component Ratio Releases 与 2 个 Background Ratio Releases。
- 用户逐项通过或退回；16 项全部通过后才允许整组入库。
- 每项冻结稳定 revision；无法稳定引用时使用完整 artifact bundle SHA-256。
- 仓库保存生产合同、实现、hash、基线和 artifact 引用，不复制 Open Design 原稿。
- Work 不运行时依赖 Open Design。

## 版本与路径

```text
.studio/profiles/<profile-id>/vN/
.studio/backgrounds/<background-id>/<ratio>/vN/
.studio/components/<component-id>/<ratio>/vN/
```

```yaml
profile_ref: optical_fluidity@v2
background_ref: functional-field/4x3@v1
component_ref: rich-skill-explanation/4x3@v1
```

所有发布包不可变。旧公共组件原样保留并标记 `legacy-profile-coupled`，不参加新 Work 检索；旧 Work vendor、Binding、Lock、Accepted Draft 与 Final 不修改。

新 Release 使用通用 `asset-package-sha256-v1`；legacy Component 保留原 `component-package-sha256-v1`，不重写历史 hash。

## 四象限审查

### 已知且确定

- Profile、Background、Component 的职责已逐项确认。
- 三套 Profile、七个公共 Component Family、一个 Background Family 和两个画幅已锁定。
- Open Design 中存在七个当前组件原稿与 `rse-functional-background` 原稿。
- 新旧 Work 的兼容边界已明确。
- Gallery、不可变版本、Work vendoring/locking 与 Animation Plan 审批继续保留。
- Fixture/Case、Match Record、Visual Payload Surface、媒体闭包与 Composition Evidence 继续保留，不因职责拆分而降级。

### 执行时再确定

- Background 的最终生产 ID。
- 16 个 Gallery artifact 的最终文件名、revision/hash 和视觉细节。
- 每个 Background Release 的有限状态名称。
- Profile Release 的首个实际版本号是否统一从 `v2` 开始。

这些是实现输入，不改变产品边界。

### 隐含假设

- Open Design 原稿足以还原七个 `4x3` 组件，而无需依赖旧 Work 私有内容。
- 两个画幅能维持一致 Slot Schema；若某一画幅需要不同输入合同，应拆成新的 Component Family。
- 三套 Profile 的最小 token 能覆盖当前七个组件与背景的主题需求。
- 旧 Work 已包含完整 vendor 副本，可在公共旧包停止发现后继续渲染。

### 主要盲区与控制

- 主题合同过小：缺失 token 时失败关闭；只有多个真实实现共同需要时才扩展合同。
- 背景重新侵入组件：通过透明根层扫描和组合像素检查阻止。
- 独立画幅退化为缩放：要求独立 artifact、源码、关键帧和用户验收。
- 全组合 QA 爆炸：只固定三套 Profile x 16 个 Ratio Releases 的主题冒烟，组件语义与 seek 检查按 Release 独立执行。
- 一次性迁移破坏旧 Work：采用 expand-contract，不覆盖旧包，不修改旧快照。
- Gallery 与生产翻译漂移：记录 revision/hash，出现可感知差异即退回确认。

## 八点审查

| 维度 | 结论 |
|---|---|
| 目标 | 消除 Profile、Background、Component 的职责重叠，并支持真实独立画幅设计。 |
| 范围/非目标 | 只重构 3 Profile、7 Component Families、1 Background Family；不公共化其余原型。 |
| 验收 | 16 项 Gallery、三 Profile 主题切换、跨画幅 Slot 一致、seek/像素/hash/离线渲染。 |
| 返工歧义 | 任何可感知视觉或动效变化回到 Gallery；合同或内部实现变化发布新版本。 |
| 过度建设 | 不新增 Registry、Planner Skill、响应式组件系统、主题继承或 Background 编排器。 |
| 已知未知 | 最终 Background ID、状态名、artifact revisions 属于实施输入。 |
| 隐含假设 | 最小主题合同和共享 Slot Schema 能覆盖本轮资产。 |
| 盲区 | 用失败关闭、透明根层检查、独立画幅证据与 legacy 隔离控制。 |

## Q&A

| Q-ID | 问题 | 决定 | 状态 |
|---|---|---|---|
| Q-001 | 是否引入“子 Profile”？ | 否；本次进一步从运行时合同移除 `subtemplate`。 | 已替代 |
| Q-002 | Profile 是否继续拥有材质、构图或动效？ | 否，严格只保留颜色与字体。 | 已决定 |
| Q-003 | 是否新增独立 Background？ | 是；一个 Variant 固定一个 Release，Scene 只切换预定义状态。 | 已决定 |
| Q-004 | Component 是否跨 Profile？ | 是；只消费统一主题 token，不声明 Profile。 | 已决定 |
| Q-005 | 组件兼容键是什么？ | `ratio + semantic + slots/assets + duration + anti-use`。 | 已决定 |
| Q-006 | `4:3` 与 `16:9` 是否共享实现？ | 否，同 Family 下分别设计、版本化和验收。 | 已决定 |
| Q-007 | 是否一次性重构？ | 是，不采用按真实使用渐进迁移。 | 已决定 |
| Q-008 | 是否保护旧 Work？ | 是；旧 Work 快照不变，旧公共包只读保留。 | 已决定 |
| Q-009 | 本轮包含哪些公共组件？ | 只包含当前七个明确命名的公共 Family。 | 已决定 |
| Q-010 | 是否公共化其他 P001-P012 原型？ | 否，继续 Work-local。 | 已决定 |
| Q-011 | 是否同时交付两个画幅？ | 最终是，7 个组件和 1 个背景都交付 `4x3 + 16x9`；当前先迁移已有 `4x3` 原稿。 | 已决定 |
| Q-012 | 是否迁移全部 Profile？ | 是，三套 Profile 一次性迁移。 | 已决定 |
| Q-013 | Open Design 如何验收？ | 集中 Gallery 展示 16 项，逐项验收，整组通过后入库。 | 已决定 |
| Q-014 | 主题如何接入？ | 使用统一最小 token；缺失时失败，不允许组件 fallback。 | 已决定 |
| Q-015 | 颜色派生与媒体固有颜色是否允许？ | 允许 token 派生、`transparent`、`currentColor` 及媒体固有颜色。 | 已决定 |
| Q-016 | 新资产如何引用？ | `profile@vN` 与 `asset/ratio@vN`，Work 冻结精确版本与 hash。 | 已决定 |
| Q-017 | 是否新增 Registry 或 Planner？ | 否，继续直接发现不可变合同。 | 已决定 |

## 被替代的旧边界

以下旧决定只作为历史背景，不再指导新实现：

- Profile 拥有材质、构图、Motion Grammar 与 easing；
- `Profile + subtemplate` 是组件兼容键；
- 画幅由 Work/Subtemplate 负责而不进入组件引用；
- MVP 只覆盖 `optical_fluidity + module_stage + 4:3`；
- 只有七个明确命名的 Component Family 进入公共化路径。

新实现以 2026-09-03 确认的三层合同、两个独立画幅和一次性重构范围为准。

## 未决项

无产品级 TODO。最终 ID、状态名、artifact revision/hash 与实施顺序在 Trellis 子任务和 Gallery 中确定。
