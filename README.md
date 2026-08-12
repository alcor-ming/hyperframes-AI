# HyperFrames AI Harness

面向约两分钟中文口播视频的轻量创作 Harness。它以 Work 组织长期作品，以 Variant 管理平台版本，支持 DBS 改写或逐字保留、联网 Research、Animation Plan、HyperFrames Draft/Final 和可恢复归档。

## 快速开始

```bash
./work new "作品标题"
./work status
./work variant add douyin-9x16 --from main --ratio 9:16
```

`work new` 默认创建 `pure_hyperframes`、`optical_fluidity`、`9:16` 的 `main` Variant；Agent 可通过参数选择其他 Template、Profile 和 Ratio。

```bash
./work new "人物口播" --template talking_head --subject-position left
./work wait recording
./work resume
```

Draft 与 Final 生命周期：

```bash
./work preview register /path/to/draft.mp4
./work preview accept draft-v001
./work finalize /path/to/final.mp4 --qa-passed
```

`--qa-passed` 只能在 Agent 已完成 `.studio/spec/hyperframes.md` 规定的 Final QA 后使用。所有 Required Variants 完成 Final 后，Work 自动移入 `works/archive/<year-month>/`。

## 公开内容

- `AGENTS.md`：创作边界与最小上下文路由。
- `.studio/`：工作流、能力表、规范、Recipe、模板和生命周期 CLI。
- `.agents/skills/hyperframes-codex-workflow/`：Codex 薄路由 Skill 与三套稳定 Profile。
- `work`：无第三方依赖的本地 Work CLI。

## 私有内容

`works/`、旧 `tasks/`、媒体、工程、Draft、Final 和运行状态均由 `.gitignore` 排除。Harness 不发布内容，不登录平台，也不管理字幕或 AI 图片生成。

完整产品契约以 `.studio/` 和 `AGENTS.md` 为准。
