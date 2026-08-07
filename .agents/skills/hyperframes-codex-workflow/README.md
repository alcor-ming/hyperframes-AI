# HyperFrames Codex Workflow v1.0.0

这是一套供 Codex 读取和执行的 HyperFrames 视频工作流规范。它把已经稳定的三套设计 Profile，与两种视频模板、讨论式 Animation Plan、可选配音和可选图片资产连接起来。

## 核心结构

```text
稳定设计 Profile（三选一）
        +
视频模板（二选一）
        +
讨论式 Animation Plan
        +
可选 Voiceover / Image Assets
        ↓
HyperFrames 实现与静默 QA
```

三套 Profile：

- `optical_fluidity`
- `kami_editorial`
- `monochrome_atelier`

两套模板：

- `talking_head`：保留原始人物口播视频，HyperFrames 只承担信息增强。
- `pure_hyperframes`：整个画面由 HyperFrames 构建；可在计划确认后录制或生成配音。

不再保留字幕专用模板。字幕只是两套模板中的可选组件。

## Animation Plan 的定位

Animation Plan 类似一份轻量、可讨论的视觉 PRD：

1. Codex 根据素材先提交完整但精简的草案，不把问题全部抛回用户。
2. 用户围绕场景目标、Hero State、叙事顺序、图片需求和配音方式提出修改。
3. Codex原地更新同一份 `ANIMATION_PLAN.md`，讨论阶段只展示变更和仍需决策的内容。
4. 用户明确批准后，Codex才进入图片生成、配音、HyperFrames 实现和渲染。

计划不是流程证明。不要输出合规陈述、长篇自检、重复 Profile 规则、Implementation Changes 或完整 Test Plan。

## 使用方式

### 交给 Codex 集成到已有仓库

1. 将本目录解压到目标仓库，建议放在 `docs/hyperframes-workflow/`，或直接放在仓库根目录供 Codex 读取。
2. 将 `CODEX_TASK.md` 与 `AGENTS.md` 作为任务入口。
3. 将已有稳定 Profile 的真实路径填入 `profile-registry.json`。
4. 让 Codex 先检查已有架构，再按本规范适配；不得创建重复 Profile 或字幕专用模板。

可直接使用 `prompts/CODEX_INTEGRATION_PROMPT.md`。

### 用于具体视频任务

1. 复制 `templates/PROJECT_CONFIG.template.yaml` 为项目配置。
2. 从 `templates/ANIMATION_PLAN.template.md` 创建 `ANIMATION_PLAN.md`。
3. 让 Codex读取素材并提交计划草案。
4. 讨论并批准计划。
5. 执行资产、配音、动画与渲染。

可直接使用 `prompts/CODEX_VIDEO_PROMPT.md`。

## 文件结构

```text
SKILL.md                          可选本地 Skill 入口
AGENTS.md                         Codex 的最高优先级执行说明
CODEX_TASK.md                     集成任务目标与验收边界
DECISIONS.md                      已锁定产品决策
WORKFLOW.md                       端到端工作流
profile-registry.json             三套稳定 Profile 的接入表

docs/
  animation-plan-contract.md      最小计划结构
  discussion-protocol.md          类 PRD 讨论规则
  template-talking-head.md        口播增强模板
  template-pure-hyperframes.md    纯 HyperFrames 模板
  profile-integration.md          Profile 接入边界
  image-assets.md                 可选图片资产流程
  voiceover.md                    后配音与 AI 配音流程
  implementation-contract.md      HyperFrames 实现约束
  quiet-qa.md                     静默 QA
  migration-from-existing-prompts.md  旧 prompt 迁移映射

templates/                        可复制模板
examples/                         两套模板示例
schemas/                          可选机器校验 Schema
prompts/                          可直接交给 Codex 的入口提示词
scripts/validate_package.py       包结构与 JSON 校验
```

## 设计目标

- 把 token 用于叙事、构图、动画和资产，而不是流程自证。
- 一份计划持续讨论和修订，只设置一次强制执行确认。
- `section_map.json` 始终是可选语义缓存，不是入口依赖。
- 纯 HyperFrames 支持视觉先行、确认后配音。
- 图片生成是可选能力，不应把文字、Logo、图表或 UI 烧进图片。
- 技术校验默认静默执行，只报告无法自动解决的阻塞或实质偏差。
