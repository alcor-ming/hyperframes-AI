# HyperFrames AI Harness

面向本地内容创作的轻量 Harness。它以 Work 组织一次交付，以 Variant 管理平台版本，目前提供 `hyperframes_video` 与 `podcast_quote_image` 两条独立工作流。

## 快速开始

```bash
./work root show
./work new "作品标题" --workflow hyperframes_video
./work status
./work variant add douyin-9x16 --from main --ratio 9:16
```

开发仓位于 `/home/jym/workspace/hyperframes+AI`，外部 WorkStore 位于 Windows `D:\AI\AI+hyperframes`（WSL `/mnt/d/AI/AI+hyperframes`）。本机绑定保存在 Git 忽略的 `.studio/.runtime/work-root`；只有 `./work root set <absolute-path>` 会切换 WorkStore。

`work new` 必须选择 Workflow。视频工作流创建 `pure_hyperframes`、`optical_fluidity`、`16:9` 的 `main` Variant；Agent 可通过参数选择其他 Template、Profile 和 Ratio。

```bash
./work new "人物口播" --workflow hyperframes_video --template talking_head --subject-position left
./work wait recording
./work resume
```

播客图文接受本地视频或明确的来源 URL。URL 通过外部 `trendradar-media` v2.0 下载并校验后复制进 Work；YouTube 可先读取带时间戳的原生字幕，失败后再使用已授权的共享 ASR。第一个 Skill 通读转录并给出 3 个完整文章方案，用户确认其中 1 个；第二个 Skill 先调研嘉宾背景，再写开篇、每图小标题和第三人称正文，最后拟定结合全文核心与嘉宾背景的大标题。`PACKAGE.md` 直接保存可复制到创作者平台的纯文本标题、`01｜小标题` 分节、正文和话题，render 同步生成有序图片 JSON；每篇渲染 8 到 12 张图，图片用约 10 个汉字的 Hero 与支撑短句把中文控制在约 60 到 90 字，完整背景、案例和推导留在正文。画面使用 50px 中文与 30px 英文，Hero 至少占 60%，支撑字幕按双语文本高度紧凑排列：

```bash
./work new "播客金句" --workflow podcast_quote_image
./work finalize /path/to/render --qa-passed
```

多链接输入按“一条来源一个 Work”拆分，并以 detached 方式交给后台任务。`Current Work` 只代表前台焦点；后台任务必须始终显式绑定自己的 Work 和 Variant，因此小红书与 HyperFrames Work 可以同时运行：

```bash
./work new "播客 A" --workflow podcast_quote_image --detached
./work --work <work-id> --variant main status
./work --work <work-id> --variant main name "嘉宾名-核心主题"
./work list
```

后台在转录完成后自动写入三位序号 + 嘉宾名 + 核心主题的显示名，再完成 3 个文章方案并停在 `article_selection`。HyperFrames 视频在 Script 稳定后按三位序号 + 核心主题命名。Work ID 与目录名始终不变，重复命名保留原序号；`work list` 按位置、Workflow 和序号排列。用户只需确认 1 个方案；单个 Work 失败不阻塞同批其他 Work。

Draft 与 Final 生命周期：

```bash
./work preview register /path/to/draft.mp4
./work preview accept draft-v001
./work finalize /path/to/final.mp4 --qa-passed
```

`--qa-passed` 只能在 Agent 已完成 `.studio/spec/hyperframes.md` 规定的 Final QA 后使用。所有 Required Variants 完成 Final 后，Work 自动移入外部 WorkStore 的 `works/archive/<year-month>/`。

## 公开内容

- `AGENTS.md`：创作边界与最小上下文路由。
- `.studio/`：工作流、能力表、规范、Recipe、模板和生命周期 CLI。
- `.agents/skills/hyperframes-codex-workflow/`：视频工作流薄路由 Skill 与三套稳定 Profile。
- `.agents/skills/hyperframes-anti-ppt/`：Animation Plan 与 Draft 阶段的动态叙事重构和复审 Skill。
- `.agents/skills/podcast-quote-image/`：转录理解、原文证据整理与 3 个文章候选方案 Skill。
- `.agents/skills/xiaohongshu-article-copy/`：标题、开篇、每图文案、DBS 检查、取帧、渲染与 QA Skill。
- `.agents/skills/native-subtitle-quote-image/`：无法转录时经人工确认启用的 [原版 v1.0.0 Skill](https://github.com/chengyi-ai/native-subtitle-quote-image/tree/f1fa5b70448f620ea92179357eca4b0222481b9d)。
- `work`：无第三方依赖的本地 Work CLI。

## 私有内容

外部 WorkStore 的 `works/`、旧 `tasks/`、媒体、工程、Draft、Final 和运行状态不进入开发仓或 Git。Harness 不实现下载后端，而是调用独立的 `trendradar-media`；它不公开发布内容，也不内置 ASR 模型。经用户对准确 Work/Variant 明确授权，可使用其已登录的 Windows Chrome 保存小红书创作者平台草稿，但绝不点击发布。

完整产品契约以 `.studio/` 和 `AGENTS.md` 为准。
