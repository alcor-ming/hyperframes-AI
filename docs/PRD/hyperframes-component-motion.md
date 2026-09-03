# HyperFrames Theme / Background / Component PRD

状态：产品边界已确认，待拆分实施

上位 PRD：[PRD_MASTER.md](./PRD_MASTER.md)

决策依据：[component-driven-motion-vnext.md](./_ledger/component-driven-motion-vnext.md)

日期：2026-09-03

## 1. 模块目标

一次性重构现有 HyperFrames 视觉资产合同，使主题、背景与前景组件各自只有一个职责：

- Profile 决定颜色和字体；
- Background 决定全画幅环境层；
- Component 决定前景布局、画面效果和动效。

新合同必须让组件跨 Profile 使用，让 `4:3` 与 `16:9` 保持独立设计，并继续保留 Work 本地冻结、离线渲染、Animation Plan 审批与历史 Work 可复现性。

## 2. 术语

### Profile Release

一个不可变主题包，只包含统一合同中的语义颜色和字体栈。Profile 不再定义材质、几何、排版尺度、构图、画幅、Motion Grammar、timing 或 easing。

### Background Family

一组语义一致的环境背景。它可以拥有不同画幅实现，但不承载标题、证据、卡片或叙事内容。

### Background Ratio Release

指定画幅的不可变 Background 实现，拥有环境 DOM/CSS、纹理、光影、低强度动效、有限命名状态、Preview 与基线。

### Component Family

跨画幅共享一个 `component_id`、communication goal、semantic contract 和 Slot Schema 的组件族。

### Component Ratio Release

指定画幅的不可变组件实现，拥有 DOM/CSS、布局、材质、字号、层级、画面效果、完整 GSAP timeline、easing、Opening/Build/Hero/End/Handoff、Preview 与基线。

### Legacy Release

现有把 `optical_fluidity`、`subtemplate`、颜色、字体与 Motion Verb 写进组件包的旧版本。它只服务既有 Work，不参加新 Work 检索。

### Work Binding

当前 Work/Scene 对 vendored Ratio Release 的外层绑定，只允许 Slots、位置、尺寸、offset、整体 timeScale、Hero/Handoff hold 和 Work 本地媒体引用。

## 3. 总体流程

### 3.1 一次性设计重构

1. 从 Open Design `Hyperframes` 项目读取四个公共 Component Family 的原稿与现有背景原稿。
2. 为每个 Family 分别设计 `4x3` 与 `16x9`，不通过拉伸、裁切或响应式规则生成另一画幅。
3. 将组件里的全画幅环境层拆入独立 Background；组件根层保持透明。
4. 把硬编码颜色与字体替换为统一语义 token；其他视觉和动效参数留在具体实现。
5. 生成一个集中 Gallery，覆盖 8 个 Component Ratio Release 与 2 个 Background Ratio Release。
6. 用户逐项验收；全部通过后冻结 artifact revision 或 bundle SHA-256。
7. 才能写入新公共库并进入 Work 集成验证。

### 3.2 正常 Work 路径

1. Variant 声明唯一 `ratio`、`profile_ref` 与 `background_ref`。
2. Animation Plan 先形成 Scene Semantic Brief。
3. 工作流按 `ratio + semantic contract + slots/assets + duration + anti-use` 过滤 Component Ratio Release。
4. Plan 为每个 Scene 记录 `background_state`、`component_ref`、Slots、时间和 Match Record。
5. 用户整体批准 Plan。
6. 工作流复制精确 Profile、Background、Component 包，创建 Binding 与 Lock。
7. Work 仅从 vendored 副本完成 Draft、Snapshot、Final 与 Archive。

缺少合适组件时继续使用 `custom:<slug>` 并记录结构化缺口；不得为了复用而扭曲原文或跨画幅调用。

## 4. 功能需求

### HCM-001｜三层职责隔离

- Profile 只拥有颜色与字体。
- Background 只拥有全画幅环境层及其低强度状态。
- Component 只拥有前景信息结构、画面效果和动效。
- `subtemplate` 从 Profile、Component、Binding、检索和 Animation Plan 必填字段中移除。
- Profile Motion Grammar、Motion Verb、timing 与 easing 从 Profile 合同中移除。
- Template 仍只区分 `talking_head` 与 `pure_hyperframes`；本组件库继续只服务 `pure_hyperframes`。

**验收**：任一字段都能唯一归属一层；新合同中不存在 `profile + subtemplate` 兼容键。

### HCM-002｜统一主题合同

三套 Profile 必须提供：

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

- 字体值是带 fallback 的字体栈。
- 字号、字重、行高、字距不属于 Profile。
- Component 与 Background 不得声明 `profile` 或内置某个 Profile 的 fallback 值。
- 允许使用 `transparent`、`currentColor` 及从主题 token 派生的透明度或混色。
- 品牌 Logo、图片与视频的固有颜色不视为主题硬编码。
- Profile 缺少必需 token 时失败关闭，不临时补值。

**验收**：三套 Profile 通过同一 schema；扫描新 Background/Component 源码不能发现未声明的主题颜色或字体。

### HCM-003｜独立画幅实现

- 画幅 ID 只使用 `4x3` 与 `16x9`。
- 同一 Component Family 的两个画幅共享语义用途和 Slot Schema。
- DOM、CSS、布局、尺寸、素材构图、动效节奏和基线可完全不同。
- 两个画幅分别版本化；一个画幅升级不要求另一个同步升级。
- 不允许通过整体缩放、裁切、CSS media query 或通用响应式布局声称完成另一画幅设计。
- 未经 Gallery 验收的画幅不存在可调用 Release。

**验收**：每个 Ratio Release 都有独立 artifact、入口、Preview、关键帧与 package hash；跨画幅 Slot Schema 一致。

### HCM-004｜Background 合同

每个 Background Ratio Release 必须定义：

- `background_id`、`ratio`、整数 `version`；
- 消费的主题 token；
- 环境 DOM/CSS、纹理、光影与自身动效；
- 有限 `states`、默认状态、每个状态的视觉边界与 seek 行为；
- Preview、关键检查时间与基线；
- 运行时网络、资产类型和本地路径约束；
- Open Design artifact revision 或 bundle hash。

运行规则：

- 一个 Variant 固定一个精确 `background_ref`。
- Scene 只能选择该 Release 已声明的状态。
- Background 不得包含作品文字、证据、卡片、CTA 或前景叙事对象。
- Background 环境动效必须低于前景注意力，不得替代 Component 的状态变化。
- Component 根层必须透明且始终位于 Background 之上。

**验收**：Background 可独立 Preview；任意 Scene state 可直接 seek；不存在前景信息或未声明状态。

### HCM-005｜Component Family 与 Ratio Release 合同

每个 Component Ratio Release 必须定义：

- `component_id`、`ratio`、整数 `version` 与 `component-contract-v2`；
- communication goal、semantic roles、information shapes、state change 与 anti-use cases；
- 与同 Family 另一画幅一致的 Required/Optional Slot Schema；
- asset contract、duration range、entry/exit contract；
- Opening、Build、Hero、End/Handoff；
- 内部有限、paused、seek-safe 的 GSAP timeline；
- 具体 easing、阶段顺序、timeScale 范围与 hold 边界；
- 主题 token 用法、透明根层与 Background 叠放合同；
- 默认/边界 Fixture、关键检查时间和独立 Preview；
- Open Design artifact revision 或 bundle hash。

Component 不得包含：

- `profile`、`subtemplate` 或 Profile Motion Verb；
- 全画幅底色、环境纹理或 Background 状态；
- wall clock、无限循环、未播种随机数或运行时网络；
- Work 私有文案、媒体、链接或凭证。

**验收**：任一组件可在两种画幅各自独立 Preview，并能应用任意一套合规 Profile。

### HCM-006｜公共目录与发现

```text
.studio/profiles/<profile-id>/vN/
.studio/backgrounds/<background-id>/<ratio>/vN/
.studio/components/<component-id>/<ratio>/vN/
```

引用格式：

```yaml
profile_ref: optical_fluidity@v2
background_ref: functional-field/4x3@v1
component_ref: chapter-intro/4x3@v1
```

- 发现机制直接读取各不可变目录内的 manifest/contract，不新增 Registry。
- Profile 只参与主题注入，不参与组件候选过滤。
- Component 候选过滤顺序固定为：ratio、依赖/资产/Schema/时长硬限制、语义职责、状态变化、anti-use、Fixture/Case。
- Background 独立选择，不作为 Component Family 的一部分。

**验收**：新增一个 Ratio Release 只需新增一个不可变目录；选择逻辑不按 Profile 或 `subtemplate` 分支。

### HCM-007｜正式 Animation Plan

Plan 顶层必须记录：

| 字段 | 含义 |
|---|---|
| `ratio` | `4x3` 或 `16x9` |
| `profile_ref` | 精确 Profile Release |
| `background_ref` | 与 ratio 一致的精确 Background Ratio Release |

每个 Scene/Beat 必须记录：

| 字段 | 含义 |
|---|---|
| `background_state` | Background 已声明状态 |
| `component_ref` | `<component-id>/<ratio>@vN` 或 `custom:<slug>` |
| Slots | 当前作品文本、数据、图标或媒体角色 |
| Scene Semantic Brief | 叙事职责、信息结构、状态变化、证据、时长、entry/exit |
| Match Record | fit、anti-use、相关拒绝候选与 fallback |
| Artifact evidence | 公共包合同/hash 或新 Gallery artifact revision/hash |
| Customization | 允许的外层位置、尺寸、offset、timeScale 与 hold |

Profile 不再要求选择理由、Motion Verb 或画幅映射；Plan 只验证主题合同完整。改变 Profile Release、Background Release、ratio、Background states 集合、Component Ref、Hero State 或 Scene 结构必须提高 Plan Revision 并重新批准。

**验收**：只读取 Plan 即可唯一解析主题、背景、组件、画幅、状态与适配边界。

### HCM-008｜版本、安装与冻结

- Profile、Background Ratio Release 与 Component Ratio Release 都使用不可变整数版本。
- 正式 Plan 批准后才复制生产包到 Work。
- Work 分别保存精确 Profile、Background、Component 副本及其 hash。
- Work Binding 不得修改 vendored DOM、CSS、状态顺序或 GSAP beat。
- Work Lock 必须记录全部 refs、公共 package hash、Work 副本 hash、Binding 路径/hash 与安装文件。
- Work 只从 vendored 副本渲染；断开公共库与 Open Design 后仍须 Preview/Render。
- 新 Release 使用通用 `asset-package-sha256-v1`：排除 hash 清单本身，按 POSIX 相对路径字典序汇总每个文件的 SHA-256，再对 UTF-8 清单计算最终 SHA-256。legacy Component 继续保留原 `component-package-sha256-v1`，不重写。

**验收**：任一包被修改都会在 Snapshot 前失败；公共库升级不能改变已冻结 Work。

### HCM-009｜旧合同迁移

- 当前旧公共包原样保留，标记 `legacy-profile-coupled`。
- 不修改旧包 hash，不移动或重写旧 Work 的 vendor、Binding、Lock、Accepted Draft 或 Final。
- 新公共资产统一声明 `component-contract-v2`。
- 新 Work 不得发现或安装 legacy 包。
- 新公共库整组完成前，禁止一个新 Work 混用新旧合同。
- 历史 Work 不需要补 Background Ref 或新 Profile Snapshot。

**验收**：旧 Work 仍按原路径离线渲染；新 Work 的 Lock 中不存在 legacy package。

### HCM-010｜一次性重构清单

必须重构三套 Profile：

- `optical_fluidity`
- `kami_editorial`
- `monochrome_atelier`

必须重构四个公共 Component Family：

- `chapter-intro`
- `rich-skill-explanation`
- `capability-convergence`
- `gap-first-selection`

必须新增一个 Background Family，`4x3` 以 Open Design 的 `rse-functional-background` 为设计起点，并重新设计 `16x9`。

每个 Family 必须同时交付两个画幅。Open Design 的其他 P001-P012 Work-local 原型不进入本轮公共化范围。

**验收**：恰好形成 3 个新 Profile Releases、8 个 Component Ratio Releases 和 2 个 Background Ratio Releases；不得用额外原型扩大范围。

### HCM-011｜Open Design Gallery 与冻结

- Open Design `Hyperframes` 项目是设计原稿真源。
- Gallery 覆盖 10 个 Ratio Release，每项可独立 Preview、pause、seek 和 render。
- 用户逐项通过或退回；只有全部通过后才能整组写入新公共库。
- 每项记录稳定 revision；没有稳定 revision 时记录完整 artifact bundle SHA-256。
- 仓库只保存生产实现、合同、hash、基线与 artifact 引用，不复制设计原稿。
- 生产翻译只允许主题 token 接线、Slots、Work 隔离、seek-safe 和离线渲染所需调整。
- 生产结果与 Gallery 存在可感知差异时必须退回重新确认。

**验收**：10 项都有独立通过记录与唯一 artifact 证据；任一未通过时不得发布整组。

### HCM-012｜失败边界

- ratio 缺失、未知或各引用不一致：Draft 前停止。
- Profile token 缺失：停止，不使用组件 fallback。
- Background state 未声明：停止，不临时生成。
- Component Slot Schema 跨画幅不一致：该 Family 不得发布。
- Component 含全画幅背景、硬编码主题值、特定 Profile 字段或 `subtemplate`：不得发布。
- Artifact 无法唯一解析、bundle 不完整或 hash 不一致：不得入库。
- Required Slot、本地资产、package hash 或 Binding hash 缺失：停止集成或 Snapshot。
- Scene 语义不匹配或命中 anti-use：失败关闭到 `custom:<slug>`。
- 需要改变内部布局、DOM、CSS、状态顺序或 GSAP beat：发布该画幅的新版本。

**验收**：所有失败都在生产 HTML、Draft 注册或 Snapshot 前暴露，不静默降级。

### HCM-013｜验证矩阵

每个 Ratio Release 必须通过：

1. 典型与边界 Fixture；
2. Opening/Build/Hero/End 直接 seek 与顺序播放一致；
3. repeat-seek 无状态累积；
4. 目标画幅安全区、最长文案、字体 fallback 与溢出检查；
5. 三套 Profile 逐一应用后的主题、对比度和硬编码扫描；
6. Background + Component 组合后的层级、透明根层、遮挡和 Hero 可读性；
7. package hash、Work vendor hash、Binding hash 与离线渲染。

Gallery 是设计验收，不能替代生产 HyperFrames Check 与像素 QA；源码扫描也不能替代实际渲染检查。

**验收**：8 个 Component Ratio Release 与 2 个 Background Ratio Release 都有独立报告；三套 Profile 全部通过主题切换。

### HCM-014｜权限与数据边界

- 公共库只保存代码、合同、Schema、Fixture、脱敏 Case、基线和无版权风险的通用资产。
- Work 文案、媒体、截图、Draft、Open Design 私有链接和运行状态不得进入 Git。
- 所有运行时媒体必须是 Work-relative 本地路径，不允许 URL、Cookie、凭证或临时外部目录。
- Open Design 原稿不复制进开发仓；仓库只记录安全的 artifact 标识与 hash。
- ImageGen、媒体下载、平台草稿与发布权限保持现有规则。

**验收**：发布包与 diff 中不存在 Work 私有内容、认证数据、临时路径或外部运行时依赖。

### HCM-015｜既有组件能力延续

- Component Ratio Release 继续自包含合同、Schema、默认 Fixture、实现、hash 清单与基线。
- 后续边界 Fixture 与脱敏 Case 继续位于 Release 外的追加目录，不得改变 package hash。
- Scene Semantic Brief、Match Record、anti-use 检查、相关拒绝候选与 `custom:<slug>` 缺口记录继续使用。
- Visual Payload Surface 仍是媒体注入的唯一稳定 DOM 锚点；Binding 不能改变外壳几何、层级、状态顺序或 GSAP beat。
- 本地图片和视频继续执行 Work-relative 路径、文件存在、probe、内容 hash、Lock 与 Snapshot 闭包检查。
- Composition Evidence 只证明真实组合与 Handoff，不自动成为公共转场资产。

**验收**：解耦重构不能削弱现有语义选择、媒体安全、Fixture/Case、离线冻结或组合证据能力。

## 5. 贡献与演进

| 变化 | 动作 |
|---|---|
| 只修改 Profile 颜色或字体 | 发布新的 Profile Release |
| 修改 Background 状态、环境 DOM/CSS 或动效 | 发布该画幅新的 Background Ratio Release |
| 修改 Component Slot Schema | 同一 Family 的两个画幅必须迁移到一致合同后再发布 |
| 修改某一画幅布局、DOM/CSS、状态顺序或 GSAP beat | 只发布该画幅新的 Component Ratio Release |
| 新真实用法仍在合同内 | 追加脱敏 Case，不修改 Release |
| 只验证边界输入 | 追加 Fixture，不修改 Release |
| 需求只服务当前作品或私有媒体 | 保持 Work-local |
| 出现新画幅 | 先独立设计、Gallery 验收，再创建新 ratio；不得复用现有实现冒充 |

## 6. PRD 完成定义

本模块 PRD 在以下条件下可进入 Trellis 拆分：

- 三层职责、最小主题合同与 `subtemplate` 移除边界已确认；
- 三套 Profile、四个 Component Family、一个 Background Family与两个画幅范围已锁定；
- Open Design Gallery、版本引用、旧 Work 兼容和失败边界已明确；
- 所有要求都有可测试验收标准；
- 无产品级 TODO。

建议实施采用 expand-contract：先增加新合同与新资产，完成 Gallery 和新路径验证，再关闭 legacy 对新 Work 的发现；不得通过覆盖旧包完成迁移。
