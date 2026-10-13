# HyperFrames Design Profile Pack

版本：`0.1.0`  
快照日期：`2026-08-07`

这是一套面向 HyperFrames 的自有设计 Profile Skill。它服务两种既有模板：

1. **口播增强模板**：人物/原视频是主视觉，HyperFrames 只承担解释、强调、结构化和节奏控制。
2. **纯 HyperFrames 展示模板**：画面完全由排版、图形、图片、数据和动画构成。

包内有三套互斥 Profile：

| ID | 名称 | 上游主要依据 | 核心差异 |
|---|---|---|---|
| `optical_fluidity` | Optical Fluidity｜光学流动 | `emilkowalski/skills` 的 `apple-design`、`emil-design-eng` | 用空间连续性、材质层级和流体运动组织信息 |
| `kami_editorial` | Kami Editorial｜纸上编辑 | `tw93/Kami` | 用纸面、排版、章节与批注组织信息 |
| `monochrome_atelier` | Monochrome Atelier｜黑白工坊 | `pbakaus/impeccable` 的 `distill`、`quieter`、`typeset`、`layout` | 用删减、排版、留白和时间赋予信息重量 |

## 推荐用法

将整个目录复制到项目的 Agent Skill 目录，保持内部文件结构不变：

```text
.agents/skills/hyperframes-design-profiles/
  SKILL.md
  profiles/
  shared/
  prompt-blocks/
```

执行视频任务时，只加载本包的 `SKILL.md`，再由它加载一个 Profile。不要同时把三个上游 Skill 全部放入一次视频执行上下文。

## 为什么不是直接调用第三方 Skill

三个上游项目都很优秀，但目标并不等于预渲染视频：

- `apple-design` 主要讨论可交互 UI、手势、速度继承和可中断动画；视频没有真实指针和交互状态。
- `Kami` 是文档与页面生成系统，带模板、构建脚本、字体策略和文档工作流；直接调用会把视频误判为文档任务。
- `Impeccable` 是完整前端设计与审查系统，会根据产品/品牌上下文选择视觉世界；直接调用可能改变已经锁定的 Profile 身份。

因此本包采用：

> **自有 Profile 作为运行时唯一视觉真源，上游 Skill 作为设计知识来源、维护参考和可选审查器。**

详细决策见 [`DECISION.md`](DECISION.md)。

## 文件说明

- `SKILL.md`：可直接安装的 Profile 路由 Skill。
- `profiles/*/PROFILE.md`：三套完整设计语言。
- `profiles/*/tokens.json`：可用于 CSS/JS 的视觉与运动 token。
- `shared/profile-contract.md`：所有 Profile 必须满足的字段与优先级。
- `shared/two-template-mapping.md`：同一 Profile 在两种视频模板中的映射规则。
- `shared/review-gate.md`：Animation Plan 与渲染前审查门。
- `prompt-blocks/full-visual-identity.md`：可替换现有 prompt 中 Visual Identity 的完整版。
- `prompt-blocks/compact-visual-identity.md`：上下文紧张时使用的压缩版。
- `upstream/SOURCES.md`：来源、Star 快照、许可证和取舍。
- `upstream/OPTIONAL-INSTALL.md`：仅用于研究和维护的可选安装命令。
- `upstream/THIRD_PARTY_NOTICES.md`：第三方声明和字体限制。

## 设计优先级

执行时按以下顺序裁决冲突：

```text
用户本轮明确要求
  > 项目/品牌已锁定规则
  > 模板模式（口播增强 / 纯 HyperFrames）
  > 所选 Profile
  > shared 共用基线
  > 上游 Skill 建议
```

上游 Skill 永远不得覆盖用户明确要求，也不得在运行时自行切换 Profile。
