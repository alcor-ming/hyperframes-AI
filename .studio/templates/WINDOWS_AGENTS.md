# HyperFrames Windows 创作根

若根目录存在 `AGENTS.local.md`，同时读取其中本机提供方与用户规则。用户直接在 Codex App 打开本目录；Agent 使用本根 `work.cmd` 的绝对路径，运行同根 `runtime/` 与 `.studio/`，配置读取 `.studio/.runtime/local.json`。`work.cmd doctor` 查看实际身份与 Review 范围。

视频模式为 `card`、`explainer` 与 `showcase`，默认 `card`，`purpose=ip` 推荐 `explainer`。Codex 不接 `showcase` 制作，仅 Opus 5.5 制作；创建时显式选择并冻结 `pdoom` / `science` 子模块。五层、A/B-roll、字幕与声音层见 [.studio/spec/visual-design.md](.studio/spec/visual-design.md)，showcase 见 [.studio/spec/showcase.md](.studio/spec/showcase.md)。生产 Finalize 渲染出最终 MP4。

## 工作边界

WSL 与 Windows 均可编写组件，WSL 开发计划可以包含组件编辑。Windows 在 Work-local 或登记 AssetSource 制作 Scene、GSAP、Three.js、shader、SVG、模型与内容脚本；工具、宿主、合同、依赖和安装器缺陷交 WSL 冻结最小复现。按会话工作目录区分：WSL 开发仓会话不修改生产 Work、Current、Binding、接受状态或 Final，生产根会话按下段执行。

Claude Code 在本生产根（WSL `/mnt/d/AI/AI+hyperframes`）的会话读取根 `CLAUDE.md`，仅 Opus 5.5 制作 showcase，或只读审查数学等系列。生产 CLI 只通过同根 `work-wsl.sh` 调用 `work.cmd`；授权 Work 的文稿、Plan 与工程源可直接编辑，Current、Binding、接受状态与配置仍由 CLI 管理。作品、Draft、Final 留在唯一生产根；不在 WSL 另起 Studio 或渲染器，画面证据使用 CLI 截图与诊断。同一 Work/Variant 同时只允许一个执行者。

安装工具、runtime、受管理规则、已接纳 AssetStore、vendor 与 Accepted Snapshot 只读；变更在可编辑源完成，复用时冻结新版本。更新保留用户 Skill 与未知文件，停止相关进程后使用安装器及恢复机制；不热换运行中的工具。Review 使用独立根配置、WorkStore、AssetStore 与必要 source-copy。

## 授权边界

- 不公开发布、不上传内容、不购买额度；不得读取 Cookie、调用未公开接口或点击发布。外部或付费服务必须单独取得用户授权；私有内容转交新外部提供方也须明确授权。
- Plan 列明生成素材用途、数量、风格与 Asset Brief 后，方向批准一并授权这些素材；未列用途或明显超量再确认。`design-taste-frontend` 仅在获批 Asset Brief 明确要求时介入，不查询图片 Prompt 库。
- Draft 与 test-work 不导出视频，包括带声短段、逐帧编码和预渲染镜头；仅生产 Variant 的 Finalize 交付链可生成视频。Studio 受限时记录未验证项，不以导出绕过。
- 部署、安装切换、应用交付、删除不可替代内容以及 commit/tag/push 需要覆盖准确目标的用户授权；测试接受不转为生产接受。Review 不修改生产 Current、源、接受记录或默认配置，不进行生产 Finalize、归档完成或平台草稿。

## 入口与治理

前台通过本根 `work.cmd current` 定位，无 Current 时 `work.cmd list`；后台显式绑定 Work/Variant，同一对象同时只允许一个执行者。按 [.agents/skills/hyperframes-codex-workflow/SKILL.md](.agents/skills/hyperframes-codex-workflow/SKILL.md) 加载当前阶段，生命周期和人工接受见 [.studio/workflow.md](.studio/workflow.md)。`podcast_quote_image` 保留创建与选择合同，方案批准前用 planner_skill，批准后用 copy_skill，不加载视频规则。

资产开发任务完成指：包已打包接纳，或场景源/配方已写发现字段，并且 `work.cmd component list --audit` 无该项告警。场景源 `manifest.json` 与配方 Markdown 的 JSON front matter（`---` 内放 JSON 对象）使用 `source_ref`、`title`、`purpose`、`tags`（数组）、`workflow_role`、`primary_category`、`classification_status`、`limits`（字符串或数组），场景源另含相对本目录的 `entry`；它们是派生参考、不可安装。字段示例见 README 的资产入口。配方目录先用 `work.cmd component source-add <目录>` 登记为 AssetSource。现有 5 个场景源与 18 条配方由 Windows 补字段，WSL 不代改。

保留现有内容、Scene/Anchor ID、正式音频/对齐与冻结快照。只报告实际结果、改动、缺口和必要决定；WSL/mock、Windows 原生与生产验收分别报告，未验证不冒充通过。
