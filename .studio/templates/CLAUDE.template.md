# HyperFrames Claude 生产执行者

本文件适用于 Claude Code 在 WSL 生产根 `/mnt/d/AI/AI+hyperframes` 的会话，不适用于 `/home/jym/workspace/hyperframes+AI` 开发仓。读取根 [AGENTS.md](AGENTS.md) 的授权边界；本文件不增加发布、外部服务、部署或接受权限。有 `AGENTS.local.md` 时同时读取。

CLI 只用同根 `./work-wsl.sh` 调用 Windows `work.cmd`。先确定任务类型和准确授权对象；同一 Work/Variant 只允许一个执行者。不手改 Current、Binding、接受记录、配置或已部署工具。所有内容留在唯一生产根，只使用 Windows 官方 Studio 的截图和诊断，不在 WSL 另起 Studio、浏览器渲染器或导出 Draft 视频。生命周期见 [.studio/workflow.md](.studio/workflow.md)。

## Showcase 制作

仅 Opus 5.5 制作，创建时显式指定并冻结 `pdoom` / `science`。读取 [.studio/spec/showcase.md](.studio/spec/showcase.md) 与选定子模块参考，可编辑获授权 Work 的文稿、Plan、Scene 与工程源。只有这一类不要求 explainer 正向方向、D14、Q1 或 Draft 前节奏必经闭环；硬约束与用户接受不豁免。接受后按 `.studio/templates/VISUAL_RETRO.template.md` 提炼最小积木、配方或内容资产，不把整页代码交给其他产品线。

## Explainer 主镜头

仅限非数学 explainer 的单片 1–2 个主镜头。Plan 列明 Scene 与 Asset Brief，方向批准后，先由 Codex 释放执行权，再独占制作用户指定 Work/Variant/Scene 的工程源；其余叙事和合同由 Codex 负责。读取 [.studio/spec/visual-design.md](.studio/spec/visual-design.md)、[.studio/spec/creative.md](.studio/spec/creative.md) 与相关接口卡，完整遵守五层、A1、语义 cue、阅读保护、节奏诊断和 Q1，不享受 showcase 豁免。完成后交回 Codex，不代替用户接受；主镜头不直接进入通用库，接受后才能另行提炼。

## 资产库创作

读取 [.studio/spec/broll-assets.md](.studio/spec/broll-assets.md)，用 [.studio/templates/BROLL_BRIEF.template.md](.studio/templates/BROLL_BRIEF.template.md) 确定需求。可编辑范围只在 `asset-library/sources`，候选仅通过 `component pack` 生成；不修改任何 Work、不手写候选管理记录或接纳记录，不执行 accept。已接纳版本只发新版本，不覆盖。账号外观和风格叠加、插槽、时长、字体容量、关键时刻与离线闭包均按指南自检；选型信息只起草，接纳仍由用户执行。

## 只读审查

除下述用户指定画面复盘的限定写入外，数学系列、card 单片及未列出的系列一律只读，不修改 Work。数学审查包采用 [.studio/spec/math-rap.md](.studio/spec/math-rap.md) 的固定输出：证据【图】【码】【未实现】、严重度表、推荐分镜表。读取范围限声明文件，不代替用户观看或接受。

## 画面复盘

用户指定找问题或标记优秀后，生产根 Opus 优先执行，Codex 回退。显式绑定 Work/Variant 和登记 Draft，使用 `retro open <Draft ID>`，按 `VISUAL_RETRO.template.md` 填写，再 `retro check <Draft ID>`。复盘可写范围仅 `retro/`、生产根 `sample-library/`、`known-defects/` 与 `retro-summary/`；不改 Work 工程源、Plan、Current 或接受记录。采样所需可回收 Studio 记录由 CLI 管理。数学系列、card 单片的其余部分仍只读。

样片与已知缺陷在用户对话确认后经 `sample add` / `defect add` 写入，不由 Agent 或 critic 自行提名。作品修复与资产制作另按原授权边界执行。样片、帧与记录留在生产根，开发仓只收无作品内容的最小复现。具体命令与冻结参考方式见 [.studio/workflow.md](.studio/workflow.md)。

## 内容复盘

用户指定内容复盘后，生产根 Opus 优先执行，Codex 回退。显式绑定 Work / Variant，使用 `content link|import|open|check`，根汇总使用 `content summary`，流程见 `.studio/workflow.md`。只读已有发布文件与登记来源（Final / Draft / 预览）；只导入本地五份 xlsx，不联网、不导出视频、不自动判断长尾或优秀。

可写范围仅 Variant 的 `retro/content/`（含 `imports/` 导入原件目录）与生产根 `content-summary/`；不改 Work 源、Plan、Current 与接受记录。原件、记录与汇总仅留生产根，不进开发仓或 Git。card / 数学只回流选题、Plan / 画面；Script 开头与衔接仅限非数学 showcase / explainer，不改变 dbs 路由。
