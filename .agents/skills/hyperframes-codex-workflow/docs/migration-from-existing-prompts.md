# Migration from the Existing Two Prompts

## 目标

将现行提示词从“每套模板包含完整设计语言、流程、动画和测试说明”改为可组合架构：

```text
共享工作流
+ 一个稳定 Profile
+ 一个模板
+ 可选配音能力
+ 可选图片能力
```

## 旧 §3：口播增强 prompt

迁移为：

```text
template: talking_head
```

保留：

- 原始人物口播视频作为主视觉；
- HyperFrames 关键词、解释、路径、数据和步骤；
- 人脸与原字幕保护；
- 输出比例与 60fps；
- 用户确认 Animation Plan 后执行。

删除或移出模板：

- 三套 Profile 的完整配色、字体和材质定义，改为读取稳定 Profile；
- 固定左右/中间区域，改为依据人物和负空间设计 Hero State；
- 强制 `section_map.json`；
- 确认前的 Implementation Changes 与完整 Test Plan；
- 合规性自述与逐条流程证明。

新增：

- 讨论式 `ANIMATION_PLAN.md`；
- `quiet_hold` 场景；
- 可选图片 Asset Brief；
- 结构性变更才重新讨论。

## 旧 §4：字幕专用 prompt

不再保留为模板。

迁移方式：

- 纯字幕视频、动态排版视频、图形讲解视频统一进入 `pure_hyperframes`；
- 字幕成为 `pure_hyperframes` 或 `talking_head` 中的可选组件；
- 原有字幕分组、对齐和可读性规则可保留为 caption component 规范，但不得形成第三套入口；
- 背景图片不再是唯一视觉结构，允许完整的 Scene、图形、图片、数据和章节叙事。

## 新模板二：Pure HyperFrames Narrative

旧 §4 的输入契约需扩大为：

- 文稿；
- 资料；
- 大纲；
- 已有音频；
- 可选 `section_map.json`；
- 可选图片；
- 可选后配音或 AI 配音。

时间流程改为：

```text
视觉计划讨论
→ 用户批准
→ 最终旁白/AI 配音
→ 真实时间轴
→ HyperFrames 实现
```

## Profile 迁移

旧 prompt 中的 Apple、Claude、香奈儿风格块全部删除，改为只保存 Profile ID：

```yaml
profile: optical_fluidity
profile: kami_editorial
profile: monochrome_atelier
```

Profile 内容由稳定 Profile 包提供，本工作流不重复维护。

## Animation Plan 迁移

旧要求：

```text
Animation Plan + Implementation Changes + Test Plan
```

新要求：

```text
Plan Header
+ Scene Table
+ Optional Asset Brief
+ 最多 3 个待决策项
```

计划作为可持续讨论的视觉 PRD。用户批准后，实现和 QA 静默进行，只有阻塞或实质偏离才报告。
