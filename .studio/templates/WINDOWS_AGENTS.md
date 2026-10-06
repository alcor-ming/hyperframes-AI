# HyperFrames Windows 创作根

若根目录存在 `AGENTS.local.md`，同时读取其中本机提供方与用户规则。用户直接在 Codex App 打开本目录；Agent 使用本根 `work.cmd` 的绝对路径，运行同根 `runtime/` 与 `.studio/`，配置读取 `.studio/.runtime/local.json`。`work.cmd doctor` 查看实际身份与 Review 范围。

视频模式为 `explainer`、`showcase`、`math` 与 `english`，默认 `explainer`；card 制作链路已删除，旧历史仅可查看/归档，`purpose=ip` 推荐 `explainer`。Codex 不接 `showcase` 制作，仅 Opus 5.5 制作；创建时显式选择并冻结 `pdoom` / `science` 子模块。五层、A/B-roll、字幕与声音层见 [.studio/spec/visual-design.md](.studio/spec/visual-design.md)，showcase 见 [.studio/spec/showcase.md](.studio/spec/showcase.md)。生产 Finalize 渲染出最终 MP4。

## 工作边界

WSL 与 Windows 均可编写组件，WSL 开发计划可以包含组件编辑。Windows 在 Work-local 或登记 AssetSource 制作 Scene、GSAP、Three.js、shader、SVG、模型与内容脚本；工具、宿主、合同、依赖和安装器缺陷交 WSL 冻结最小复现。按会话工作目录区分：WSL 开发仓会话不修改生产 Work、Current、Binding、接受状态或 Final，生产根会话按下段执行。

Claude Code 在本生产根（WSL `/mnt/d/AI/AI+hyperframes`）的会话读取根 `CLAUDE.md`，按任务类型制作 showcase、在 `asset-library/sources` 创作库资产，或独占制作已批准的非数学 explainer 1–2 个主镜头；数学与未列出的系列只读。数学单片只复用冻结库资产，不调用 Opus。库候选由 CLI pack，接纳仍由用户执行；主镜头遵守完整 explainer 规则，不享受 showcase 豁免。生产 CLI 只通过同根 `work-wsl.sh` 调用 `work.cmd`；准确授权 Work 的工程源可直接编辑，Current、Binding、接受状态与配置仍由 CLI 管理。作品、Draft、Final 留在唯一生产根；不在 WSL 另起 Studio 或渲染器，画面证据使用 CLI 截图与诊断。同一 Work/Variant 同时只允许一个执行者。

安装工具、runtime、受管理规则、已接纳 AssetStore、vendor 与 Accepted Snapshot 只读；变更在可编辑源完成，复用时冻结新版本。更新保留未管理的用户 Skill 与未知文件；修改过的受管理退役文件保存到不会被发现为 Skill 的保留位置并报告，可回滚。继续管理文件的修改仍拒绝覆盖。停止相关进程后使用安装器及恢复机制；不热换运行中的工具。Review 使用独立根配置、WorkStore、AssetStore 与必要 source-copy。

## 授权边界

- 不公开发布、不上传内容、不购买额度；不得读取 Cookie、调用未公开接口或点击发布。外部或付费服务必须单独取得用户授权；私有内容转交新外部提供方也须明确授权。
- Plan 列明生成素材用途、数量、风格与 Asset Brief 后，方向批准一并授权这些素材；未列用途或明显超量再确认。`design-taste-frontend` 仅在获批 Asset Brief 明确要求时介入，不查询图片 Prompt 库。
- Draft 与 test-work 不导出视频，包括带声短段、逐帧编码和预渲染镜头；仅生产 Variant 的 Finalize 交付链可生成视频。Studio 受限时记录未验证项，不以导出绕过。
- 部署、安装切换、应用交付、删除不可替代内容以及 commit/tag/push 需要覆盖准确目标的用户授权；测试接受不转为生产接受。Review 不修改生产 Current、源、接受记录或默认配置，不进行生产 Finalize、归档完成或平台草稿。

## 入口与治理

前台通过本根 `work.cmd current` 定位，无 Current 时 `work.cmd list`；后台显式绑定 Work/Variant，同一对象同时只允许一个执行者。按 [.agents/skills/hyperframes-codex-workflow/SKILL.md](.agents/skills/hyperframes-codex-workflow/SKILL.md) 加载当前阶段，生命周期和人工接受见 [.studio/workflow.md](.studio/workflow.md)。本版本只提供视频制作。Work 管一期内容，Variant 管独立制作版本；已退役或未知类型只报告，不套用视频操作。

资产开发任务完成指：包已打包接纳，或场景源/配方已写发现字段，并且 `work.cmd component list --audit` 无该项告警。场景源 `manifest.json` 与配方 Markdown 的 JSON front matter（`---` 内放 JSON 对象）使用 `source_ref`、`title`、`purpose`、`tags`（数组）、`workflow_role`、`primary_category`、`classification_status`、`limits`（字符串或数组），场景源另含相对本目录的 `entry`；它们是派生参考、不可安装。字段示例见 README 的资产入口。配方目录先用 `work.cmd component source-add <目录>` 登记为 AssetSource。选型用 `work.cmd component list --include-references --query <用途>`；单查参考类型可直接用 `--kind scene-source` / `--kind recipe`。按结果 `detail.argv` 查看详情，冲突时选择准确路径，安装授权保持不变；`list --audit` 与 interface 不落盘。发现数量不代表已接纳数量，生产元数据只按明确目标补充，WSL 不代改生产资产。

保留现有内容、Scene/Anchor ID、正式音频/对齐与冻结快照。只报告实际结果、改动、缺口和必要决定；WSL/mock、Windows 原生与生产验收分别报告，未验证不冒充通过。

## 画面复盘

用户指定找问题或标记优秀后，生产根 Opus 优先执行，Codex 回退。显式绑定 Work/Variant 和登记 Draft，使用 `retro open <Draft ID>`，按 `VISUAL_RETRO.template.md` 填写，再 `retro check <Draft ID>`。复盘可写范围仅 `retro/`、生产根 `sample-library/`、`known-defects/` 与 `retro-summary/`；不改 Work 工程源、Plan、Current 或接受记录。采样所需可回收 Studio 记录由 CLI 管理。数学系列、英语的其余部分仍只读。

样片与已知缺陷在用户对话确认后经 `sample add` / `defect add` 写入，不由 Agent 或 critic 自行提名。作品修复与资产制作另按原授权边界执行。样片、帧与记录留在生产根，开发仓只收无作品内容的最小复现。具体命令与冻结参考方式见 [.studio/workflow.md](.studio/workflow.md)。

## 内容复盘

用户指定内容复盘后，生产根 Opus 优先执行，Codex 回退。显式绑定 Work / Variant，使用 `content link|import|open|check`，根汇总使用 `content summary`，流程见 `.studio/workflow.md`。只读已有发布文件与登记来源（Final / Draft / 预览）；只导入本地五份 xlsx，不联网、不导出视频、不自动判断长尾或优秀。

可写范围仅 Variant 的 `retro/content/`（含 `imports/` 导入原件目录）与生产根 `content-summary/`；不改 Work 源、Plan、Current 与接受记录。原件、记录与汇总仅留生产根，不进开发仓或 Git。数学只回流选题、Plan / 画面；Script 开头与衔接仅限非数学 showcase / explainer / english，不改变 dbs 路由。
