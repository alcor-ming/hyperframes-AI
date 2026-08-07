# HyperFrames AI Harness

一个轻量的自媒体生产 Harness，用项目约定和可复用工作流组织转录、文案、审核、配音与 HyperFrames 视频制作。

## 公开内容

- `AGENTS.md`：项目工作方式、文案生命周期与安全边界。
- `.agents/skills/hyperframes-codex-workflow/`：项目自有的 HyperFrames 视频工作流。
- `skills-lock.json`：第三方 Skill 的来源与版本记录，不包含其源码。

## 本地内容

- `tasks/<task-id>/`：转录、工作稿、审核记录与批准交付物。
- `assets/<task-id>/`：音频、图片、视频、工程与渲染结果。
- `.agents/skills/` 下除 `hyperframes-codex-workflow` 外的 Skill：按需安装，仅在本机使用。

这些目录由 `.gitignore` 隔离，不进入公开仓库。完整执行规则以 `AGENTS.md` 为准。
