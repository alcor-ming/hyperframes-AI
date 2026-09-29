# HyperFrames Claude 生产执行者

本文件适用于 Claude Code 在 WSL 生产根 `/mnt/d/AI/AI+hyperframes` 的会话，不适用于 `/home/jym/workspace/hyperframes+AI` 开发仓。读取根 [AGENTS.md](AGENTS.md) 的授权边界；本文件不增加发布、外部服务、部署或接受权限。有 `AGENTS.local.md` 时同时读取。

CLI 只用同根 `./work-wsl.sh` 调用 Windows `work.cmd`。先确定任务类型和准确授权对象；同一 Work/Variant 只允许一个执行者。不手改 Current、Binding、接受记录、配置或已部署工具。所有内容留在唯一生产根，只使用 Windows 官方 Studio 的截图和诊断，不在 WSL 另起 Studio、浏览器渲染器或导出 Draft 视频。生命周期见 [.studio/workflow.md](.studio/workflow.md)。

## Showcase 制作

仅 Opus 5.5 制作，创建时显式指定并冻结 `pdoom` / `science`。读取 [.studio/spec/showcase.md](.studio/spec/showcase.md) 与选定子模块参考，可编辑获授权 Work 的文稿、Plan、Scene 与工程源。只有这一类不要求 explainer 正向方向、D14、Q1 或 Draft 前节奏必经闭环；硬约束与用户接受不豁免。接受后按 `.studio/templates/SHOWCASE_REFINEMENT.template.md` 提炼最小积木、配方或内容资产，不把整页代码交给其他产品线。

## Explainer 主镜头

仅限非数学 explainer 的单片 1–2 个主镜头。Plan 列明 Scene 与 Asset Brief，方向批准后，先由 Codex 释放执行权，再独占制作用户指定 Work/Variant/Scene 的工程源；其余叙事和合同由 Codex 负责。读取 [.studio/spec/visual-design.md](.studio/spec/visual-design.md)、[.studio/spec/creative.md](.studio/spec/creative.md) 与相关接口卡，完整遵守五层、A1、语义 cue、阅读保护、节奏诊断和 Q1，不享受 showcase 豁免。完成后交回 Codex，不代替用户接受；主镜头不直接进入通用库，接受后才能另行提炼。

## 资产库创作

读取 [.studio/spec/broll-assets.md](.studio/spec/broll-assets.md)，用 [.studio/templates/BROLL_BRIEF.template.md](.studio/templates/BROLL_BRIEF.template.md) 确定需求。可编辑范围只在 `asset-library/sources`，候选仅通过 `component pack` 生成；不修改任何 Work、不手写候选管理记录或接纳记录，不执行 accept。已接纳版本只发新版本，不覆盖。账号外观和风格叠加、插槽、时长、字体容量、关键时刻与离线闭包均按指南自检；选型信息只起草，接纳仍由用户执行。

## 只读审查

数学系列、card 单片及未列出的系列一律只读，不修改 Work。数学审查包采用 [.studio/spec/math-rap.md](.studio/spec/math-rap.md) 的固定输出：证据【图】【码】【未实现】、严重度表、推荐分镜表。读取范围限声明文件，不代替用户观看或接受。
