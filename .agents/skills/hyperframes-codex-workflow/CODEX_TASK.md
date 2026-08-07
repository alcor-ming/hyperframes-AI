# Codex Project Task

## 目标

将本工作流接入现有 HyperFrames 项目，使 Codex 可以：

1. 在三套稳定 Profile 中选择一个；
2. 在两套模板中选择一个；
3. 根据素材生成可与用户持续讨论的 `ANIMATION_PLAN.md`；
4. 在用户批准后处理可选图片资产与可选后配音；
5. 完成 HyperFrames 实现、静默 QA 和 60fps 渲染。

## 两套模板

### A. `talking_head`

- 原始人物口播视频是主视觉。
- HyperFrames 只承担关键词、解释、数据、关系、步骤、短暂图片和少量全屏插入。
- 默认时间轴锁定原视频或用户指定的替换音频。

### B. `pure_hyperframes`

- 整个画面由 HyperFrames 构建。
- 输入可以是文稿、资料、大纲、已有音频或任意组合。
- 不强制 `section_map.json`。
- 可以先讨论视觉计划，再录制或生成 AI 配音，最后锁定真实时间轴。

## 集成要求

- 保留现有三套 Profile 的单一来源，不复制、不重新设计。
- 建立清晰但轻量的模板选择与配置入口。
- 将 `ANIMATION_PLAN.md` 作为讨论和批准的唯一视觉计划文档。
- 支持可选的 `Asset Brief → image-gen → generated asset` 流程。
- 支持 `provided | record_later | ai_generated | none` 配音模式。
- 允许读取或生成 `section_map.json`，但不得把它设为 schema required。
- 不实现字幕专用模板。
- 不引入多级审批、证明性日志或大段用户可见测试报告。
- 技术 QA 可以输出机器日志到项目目录，但用户回复只报告阻塞和实质偏差。

## 建议产物

根据现有仓库结构适配，不要求机械使用以下路径：

```text
project.yaml
ANIMATION_PLAN.md
DESIGN.md 或稳定 Profile 引用
assets/briefs/
assets/generated/
assets/manifest.json
compositions/
.hyperframes/qa/
renders/
```

## 验收边界

- 两套模板均可完成一次端到端样例。
- 未提供 `section_map.json` 时仍可形成计划。
- `pure_hyperframes` 在无最终音频时可形成估算时长计划，并在生成或接收音频后自动重定时。
- Animation Plan 的用户可见结构保持精简，支持多轮原地修订。
- 用户批准前不开始正式制作。
- 图片资产只在计划选择后生成，且不承载需要精确渲染的文字、Logo、UI 或数据图。
- 最终合成遵循所选 Profile、请求比例与 60fps 输出。
- HyperFrames lint、validate、inspect 在最终渲染前完成；无法自动修复的问题被明确报告。

## 非目标

- 不重新设计三套 Profile。
- 不建设通用项目管理系统。
- 不建设多角色授权或审计系统。
- 不要求每个项目都生成 JSON 版本的计划。
- 不强制生成字幕。
- 不把 AI 配音或 AI 图片设为必需能力。
