# Codex Video Task Prompt

请使用本目录的 HyperFrames 工作流完成当前视频任务。

先读取 `AGENTS.md`、`WORKFLOW.md`、对应模板文档、`docs/animation-plan-contract.md`、`docs/discussion-protocol.md`，并读取用户选择的稳定 Profile。

先分析现有素材并创建或更新 `ANIMATION_PLAN.md`。第一轮直接提交完整可讨论草案，不先提出长问题清单。用户可见内容仅包含：

- Plan Header；
- Scene Table；
- 必要的 Optional Asset Brief；
- 最多 3 个实质待决策项。

Animation Plan 需要与用户持续讨论。每轮反馈后原地更新同一份文件，只展示变更部分。用户明确批准前，不生成最终图片、最终 AI 配音、正式 composition 或最终视频。

批准后按顺序执行：

1. 生成计划中选择的可选图片；
2. 对 `pure_hyperframes` 生成或接收最终配音，并按真实音频重定时；
3. 先构建每个 Scene 的 Hero State；
4. 使用所选 Profile 的 motion primitives 实现动画；
5. 静默运行 lint、validate、inspect 和必要的动画检查；
6. 输出 60fps 最终视频。

不要输出流程自证、重复规则、全部通过的测试清单或无意义的风险报告。
