# Codex Integration Prompt

请将本目录中的 HyperFrames 工作流规范接入当前仓库。

先读取：

1. `AGENTS.md`
2. `CODEX_TASK.md`
3. `DECISIONS.md`
4. `WORKFLOW.md`
5. `docs/` 下对应规范

然后检查当前仓库的实际结构、已有 HyperFrames composition、三套稳定 Profile、现有 prompt、脚本和测试。不要假设目录结构与本包示例完全相同。

本次集成的硬边界：

- 只保留 `talking_head` 与 `pure_hyperframes` 两套模板；
- 删除或废弃字幕专用模板入口，但保留字幕作为组件的能力；
- 不复制、不重写三套稳定 Profile；
- `section_map.json` 改为可选；
- `pure_hyperframes` 支持视觉计划批准后再录音或 AI 配音；
- Animation Plan 是可与用户持续讨论、原地更新的轻量视觉 PRD；
- 用户批准前不进入正式图片生成、配音、composition 实现和最终渲染；
- 图片生成是可选能力，Asset Brief 必须先出现在计划中；
- QA 默认静默，不建立多级审批或流程自证系统。

优先复用现有架构，用最小变更完成集成。先给出仓库映射与最小实施方案；除非存在真正阻塞，不要把可自行判断的问题退回用户。完成后运行现有测试与 HyperFrames 基础校验，并只报告实质变更、测试失败和遗留问题。
