# rnskill 动效分层研究

日期：2026-08-21

用途：为 HyperFrames Component-Driven Motion vNext 提供产品分层参考，不复制上游实现。

## 一手来源

- [Pluviobyte/rnskill](https://github.com/Pluviobyte/rnskill)
- [rn-motion-director](https://github.com/Pluviobyte/rnskill/blob/main/skills/rn-motion-director/SKILL.md)
- [rn-motion-director motion grammar](https://github.com/Pluviobyte/rnskill/blob/main/skills/rn-motion-director/references/motion-grammar.md)
- [rn-motion-director anti-PPT gate](https://github.com/Pluviobyte/rnskill/blob/main/skills/rn-motion-director/references/anti-ppt-gate.md)
- [rn-dark-saas-video](https://github.com/Pluviobyte/rnskill/blob/main/skills/rn-dark-saas-video/SKILL.md)
- [rn-dark-saas-video scene blueprints](https://github.com/Pluviobyte/rnskill/blob/main/skills/rn-dark-saas-video/references/scene-blueprints.md)
- [rn-motion-replica](https://github.com/Pluviobyte/rnskill/blob/main/skills/rn-motion-replica/SKILL.md)

## 可借鉴结构

### 1. Director 与实现层分离

`rn-motion-director` 先形成 Motion Thesis、Beat Graph、视觉隐喻、Motion Grammar 和 Anti-PPT 判断，再交给具体生产能力。它不替代渲染器、媒体能力或 QC。

本项目采用的对应关系：

- `hyperframes-codex-workflow` 继续做薄入口、生命周期路由和组件合同选择。
- Animation Plan 继续拥有全片 Motion Thesis、Beat Graph、Scene Hero State 与组件引用。
- Component 与 Motion Recipe 只拥有组件内部有限状态变化。
- HyperFrames 继续拥有确定性实现、检查、截图、Draft 和 Final。

首批组件数量很少，单独创建 Component Planner Skill 只会复制入口职责。因此 MVP 由现有 Skill 直接读取 `.studio/components/**/COMPONENT.md`；真实规模产生检索歧义后再评估拆分。

### 2. 有限候选与渐进读取

`rn-dark-saas-video` 不是让 Agent 从所有效果中任意组合，而是在明确风格内选择少量 Scene Blueprint、Timing Preset 和 Asset Contract。Blueprint 描述叙事用途与状态变化，具体实现仍由渲染层完成。

本项目不新增风格 Skill；现有 `Profile + subtemplate` 已覆盖视觉身份和展示架构。MVP 吸收的是：

- 组件合同先暴露轻量 frontmatter；
- 先按 `Profile + subtemplate` 过滤；
- 再根据 narrative job、起止状态、Slots 和时长读取最小候选；
- 选择进入正式 Animation Plan，由用户整体批准。

不采用重复的 `registry.json`。当目录规模真实证明需要索引时，再从组件合同生成或引入索引，不提前维护第二份真源。

### 3. Motion 以状态变化而不是入场特效为单位

上游 Motion Grammar 使用 `draw`、`branch`、`merge`、`handoff`、`morph`、`flow` 等语义动词。Anti-PPT Gate 要求每个 Beat 有主运动对象、起止状态和可见变化，而不是重复标题、卡片与淡入。

本项目要求 Motion Recipe 记录：

- 叙事用途；
- 主运动对象；
- Opening、Build、Hero 与 End/Handoff 状态；
- Profile Motion Verb；
- 有限 GSAP 阶段顺序；
- seek、重放、timeScale 和最终 Hold；
- PPT 风险和禁用条件。

### 4. 参考复刻与普通复用分路

`rn-motion-replica` 在实现前固定参考区间并记录视觉、几何、运动、顺序与 timing 证据，随后才建立原创工程和像素 QC。它不把可变参考直接变成运行时依赖。

本项目把这一原则用于 Open Design 交接：

- 用户确认前，Open Design artifact 是组件设计真源；
- 确认时冻结 revision 或完整 bundle SHA-256；
- Codex 一次读取完整 artifact bundle；
- 正式 Plan 批准后生成不可变公共组件版本和 Work 本地副本；
- 冻结 artifact 只作设计证据，运行时不读取 Open Design。

这不是普通 `motion-replica` 自动复刻流程。用户与 Kimi 负责组件级设计确认，Codex 负责 HyperFrames 技术翻译、整片组合和 QA。

### 5. 真实验证优先于预设目录

上游的有限蓝图来自已明确的产品风格，而本项目目前还没有经过用户确认的公共组件。因此不能先把历史 Work 中的机制命名为六个组件，再用首条任务证明自己预设正确。

本项目改用两阶段证据：

1. 当前真实 Work 通过 Animation Draft 和 Open Design 共建，至少沉淀一个 `library-approved` 组件。
2. 后续另一条真实 Work 不经 Kimi 重建，原样复用相同 `component_id@vN`。

第一阶段证明设计交接，第二阶段才证明复用价值。组件数量由场景决定，不使用“至少三个”的人为 KPI。

## 本项目已有证据

- `optical_fluidity` 已把视觉身份和 `hero_flow` / `module_stage` 展示架构分开。
- `work-20260819-自媒体必装10个skill-2` 的 Accepted Draft 与 Final 已验证 `module_stage` 的中心舞台和顺序 GSAP 因果链。
- `work-20260813-006-codex一键智能剪辑包装skill开源了` 已验证 `hero_flow` 下流程、对比、证据和数据机制可随 Scene 语义变化。

这些历史 Work 只证明机制可行，可作为 Component Brief 和 Anti-PPT 判断的证据；它们不会自动晋升为公共组件，也不会被回写。

## 不采用的上游做法

- 不复制 `rnskill` 的目录、文案、模板代码、资产或 Showcase。
- 不引入另一个总导演取代现有 Harness 生命周期。
- 不照搬暗色 SaaS 的固定颜色、粒子、CTA 或 Scene Blueprint。
- 不引入与正式 Animation Plan 重复的长期 Storyboard 真源。
- 不把 Anti-PPT 或组件确认变成新的 Variant 审批状态。
- 不预建组件目录、Registry、Planner Skill、评分器或全局 GSAP DSL。

## 许可证边界

`rnskill` 仓库声明的默认许可证为 CC BY-NC 4.0，部分第三方内容另有许可证。本 PRD 只吸收分层原则和公开概念；后续如需复制任何代码、模板或资产，必须单独确认对应文件许可证和分发边界。
