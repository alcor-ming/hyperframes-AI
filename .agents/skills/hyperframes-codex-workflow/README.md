# HyperFrames Codex Workflow v2.0.0

这是 HyperFrames AI 创作 Harness 的薄路由 Skill。产品工作流、规范、Recipe 和模板统一由仓库根目录 `.studio/` 管理；Skill 不再维护第二套流程文档。

保留内容：

- `SKILL.md`：最小上下文与阶段路由；
- `profile-registry.json`：三套稳定 Profile 的接入表；
- `references/hyperframes-design-profile-pack-v0.1.0/`：Profile 真源；
- `scripts/validate_package.py`：结构和 JSON 校验。

v2 普通运行不加载图片生成、Prompt 库、Taste Skill、字幕、Examples 或 Migration。作品生命周期通过根目录 `./work` 管理。
