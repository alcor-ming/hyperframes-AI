# HyperFrames AI Harness

面向本地内容创作的轻量 Harness。它以 Work 组织一次交付，以 Variant 管理平台版本，目前提供 `hyperframes_video` 与 `podcast_quote_image` 两条独立工作流。

## 快速开始

```bash
./work new "作品标题" --workflow hyperframes_video
./work status
./work variant add douyin-9x16 --from main --ratio 9:16
```

`work new` 必须选择 Workflow。视频工作流创建 `pure_hyperframes`、`optical_fluidity`、`9:16` 的 `main` Variant；Agent 可通过参数选择其他 Template、Profile 和 Ratio。

```bash
./work new "人物口播" --workflow hyperframes_video --template talking_head --subject-position left
./work wait recording
./work resume
```

播客金句图接受本地视频或明确的来源 URL。URL 通过外部 `trendradar-media` v2.0 下载并校验后复制进 Work；随后筛选 6 组双语候选，用户确认 3 到 4 组后自动对齐时间、抽取候选帧并渲染：

```bash
./work new "播客金句" --workflow podcast_quote_image
./work finalize /path/to/render --qa-passed
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
- `.agents/skills/hyperframes-codex-workflow/`：视频工作流薄路由 Skill 与三套稳定 Profile。
- `.agents/skills/podcast-quote-image/`：播客金句筛选、翻译、取帧、渲染与 QA Skill。
- `.agents/skills/native-subtitle-quote-image/`：无法转录时经人工确认启用的 [原版 v1.0.0 Skill](https://github.com/chengyi-ai/native-subtitle-quote-image/tree/f1fa5b70448f620ea92179357eca4b0222481b9d)。
- `work`：无第三方依赖的本地 Work CLI。

## 私有内容

`works/`、旧 `tasks/`、媒体、工程、Draft、Final 和运行状态均由 `.gitignore` 排除。Harness 不实现下载后端，而是调用独立的 `trendradar-media`；它不发布内容、不登录平台，也不内置 ASR 模型。

完整产品契约以 `.studio/` 和 `AGENTS.md` 为准。
