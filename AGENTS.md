# HyperFrames AI 创作 Harness

## 工作边界

- 本仓库管理 Harness 规则、模板、Skill 路由、CLI、宿主、依赖与安装器，开发真源为 `/home/jym/workspace/hyperframes+AI`。
- WSL 与 Windows 均可编写组件，WSL 开发计划可以包含组件编辑；Windows 在 Work-local 或已登记 AssetSource 制作 Scene、GSAP、Three.js、shader、SVG、模型与内容脚本，不因复杂或可复用而交回 WSL。
- 安装包、已接纳 AssetStore、冻结 vendor 与 Accepted Snapshot 不原地覆盖；变更在可编辑源完成，复用时冻结新版本。WSL 开发仓会话不修改生产 Work、Current、Binding、接受状态或 Final；工具复现只在冻结最小私有副本中调试。
- 生产 WorkStore 为 `D:\\AI\\AI+hyperframes`（WSL `/mnt/d/AI/AI+hyperframes`），作品文案、媒体、工程、Draft、Final 与运行状态不得进入开发仓或公开 Git。开发任务不读取生产 Current、Work、资产或默认配置。

视频模式为 `card`、`explainer` 与 `showcase`，默认 `card`，`purpose=ip` 推荐 `explainer`。Codex 不接 `showcase` 制作，仅 Opus 5.5 制作；创建时显式选择并冻结 `pdoom` / `science` 子模块。五层、A/B-roll、字幕与声音层见 [.studio/spec/visual-design.md](.studio/spec/visual-design.md)，showcase 的豁免与硬约束见 [.studio/spec/showcase.md](.studio/spec/showcase.md)。生产 Finalize 渲染出最终 MP4。

card 与数学单片只复用冻结库资产，不调用 Opus；card 的新 Motion / B-roll 可选、无配额。生产根 Opus 可按 [.studio/spec/broll-assets.md](.studio/spec/broll-assets.md) 在 `asset-library/sources` 创作源和 pack 候选，接纳仍由用户执行。非数学 explainer 可在方向批准后交由 Opus 独占制作指定 Work/Scene 的 1–2 个主镜头，其余由 Codex 完成；主镜头遵守完整 explainer 规则，不享受 showcase 豁免，不直接入通用库。

按会话工作目录区分 WSL 职责：`/home/jym/workspace/hyperframes+AI` 是开发仓；Claude Code 在 `/mnt/d/AI/AI+hyperframes` 的会话是生产执行者，读取根 `CLAUDE.md`。生产 CLI 只经同根 `work-wsl.sh` 调用 Windows `work.cmd`；可直接编辑当前授权 Work 的文稿、Plan 与工程源，不手改 Current、Binding、接受记录或工具配置。作品与输出留在唯一生产根，不另起 WSL Studio 或渲染器；画面证据使用 CLI 截图与诊断。数学系列与未列任务只读审查，不授予制作或修改权。

## 授权边界

- 不公开发布、不上传内容、不购买额度；不得读取 Cookie、调用未公开接口或点击发布。外部或付费服务必须单独取得用户授权；私有内容转交新外部提供方也须明确授权。
- Plan 列明生成素材用途、数量、风格与 Asset Brief 后，方向批准一并授权这些素材；未列用途或明显超量再确认。`design-taste-frontend` 仅在获批 Asset Brief 明确要求时介入，不查询图片 Prompt 库。
- Draft 与 test-work 不导出视频，包括带声短段、逐帧编码和预渲染镜头；仅生产 Variant 的 Finalize 交付链可生成视频。Studio 受限时记录未验证项，不以导出绕过。
- 部署、安装切换、应用交付、删除不可替代内容以及 commit/tag/push 需要覆盖准确目标的用户授权；测试接受不转为生产接受。Review 不修改生产 Current、源、接受记录或默认配置，不进行生产 Finalize、归档完成或平台草稿。

## 入口与治理

生产阶段定位只见 [.agents/skills/hyperframes-codex-workflow/SKILL.md](.agents/skills/hyperframes-codex-workflow/SKILL.md)，生命周期与人工接受见 [.studio/workflow.md](.studio/workflow.md)。本版本只提供视频制作；已退役或未知类型只报告，不套用视频操作。

Work 管一期内容，Variant 管独立制作版本，生命周期通过 Work CLI；后台显式绑定 Work/Variant，同一对象同时只允许一个执行者，共享 ASR 只运行一个实例。保留原始来源、正式声音、稳定 Scene/Anchor ID、未受影响内容与接受/Final 快照。登记版本只在独立复制的审阅副本打开，不用 hardlink / symlink 暴露冻结源。

只报告实际结果、变更、阻塞和必要决定；程序、规则、WSL、Windows 原生与生产验收分别报告。Plan 首版可完整展示，后续聚焦变更范围。

## Release 与 Codex App 部署

- Windows Codex App 直接打开 `D:\AI\AI+hyperframes`，根 `work.cmd` 根据自身路径运行同根 `runtime/` 与 `.studio/`；配置从 `.studio/.runtime/` 读取，不经过 `.harness/releases/current`、workspace 或 session，不生成自动 session。Windows 不编辑受管理工具文件。
- 一次命令解析配置一次；长进程固定本次 Work、Variant、资产、依赖与配置输入。继承的旧 session、HOME、AssetRoot 不得重定向工具或 Review；保留必要 Provider 凭据。配置修改仅影响后续命令。
- WSL 从当前受控工作树构建本机包。正式 `harness-YYYY.MM.PATCH` 发行仍要求干净、tag 与 upstream 一致；dirty 候选不冒充稳定发行。
- 获得目标部署授权后，WSL 使用固定 `./release deploy --root <Windows-root>`，不再编写一次性部署脚本。锁一致时发送绑定准确运行时 hash 的工具包，首次安装/锁变化发送完整包；只备份和重写变更文件。成功后默认保留最近两次回滚和当前及前两版登记产物，仅回收新机制拥有且完整的成功副本；历史、失败、未知内容及 Work/资产不自动清理。参数与恢复方式见 README 根目录部署。
- 严格发行包校验检查全部文件、hash、依赖与路径；部署根校验只检查 manifest 拥有的文件，不将 Work、配置或用户 Skill 视为损坏。生产更新只覆盖管理文件；未修改且旧清单拥有、新版本移除的文件才可删除；修改过的退役文件保留字节、记录原路径和摘要并退出活动发现路径，可随备份回滚。继续管理文件的修改仍拒绝覆盖，未管理内容不覆盖，不全根 mirror/delete。
- 更新先验证 staging、备份旧管理文件与迁移信息，再更新并最后写完成标记；中断可检测和恢复，损坏组合拒绝启动。复用现有进程记录与最小互斥，更新前停止相关 Studio/render/build 进程，不热换依赖，不新建 daemon。
- 候选部署在独立根，拥有同样的直接入口、独立配置与 Work/Asset/source-copy。Review 不写生产源、Current、接受记录或默认配置，不允许正式 Finalize、归档完成和平台草稿。不将隔离测试变成日常生产前置门。
- 优先登记已有 AssetSource；Windows 开发语义视觉对象并按实际 module/media 合同生成冻结新版本，不强制拆 helper、双画幅、五阶段或全库迁移。vendor / Binding / Lock 固定准确依赖，库离线不影响闭合作品，同身份版本不同内容拒绝覆盖。
- 工具缺口交冻结最小复现给 WSL；组件按工作边界开发。程序回滚不降级 Work schema、不重绑资产；不兼容时保留新数据与可用工具。授权见本文件授权边界。

- Windows 共享 ASR 只通过包内 `asr-wsl.cmd` 调用固定的 `Ubuntu` 和 `/home/jym/workspace/_external/scripts/asr.sh`。桥接器必须拒绝 `D:\AI\AI+hyperframes` 外的输入或输出，并把 WSL 内的 `wslpath` 路径转换、ASR 可用性检查和转录合并为一次 `wsl.exe --distribution Ubuntu --exec /bin/sh -c <fixed-script>` 调用，任务参数经 `WSLENV` 传递，并原样传递 stdout、stderr 与退出码。Windows Codex 沙盒可复用 WSL ASR、模型和 GPU，但未获得包内 `asr-wsl.cmd transcribe-faster` 顶层 argv 前缀的持久授权时，每次 ASR 作业仍可能需要用户审批；不得授权任意 `wsl.exe` 命令。
- `D:\AI\AI+hyperframes` 是统一使用根：`runtime/`、`.studio/` 是已部署工具，`.studio/.runtime/` 是根配置；`asset-library/sources` 与 `asset-library/store` 保留可编辑源和冻结资产职责，不改用既有 `assets/`。Work、请求、Review 与 `.runtime/` 的既有内容保持不动，可写 Harness 开发真源仅在 WSL。
- 更新完成后重启相关工具进程，Agent 重读根规则；下一条根命令用新版本，无需创建 Harness session。单次命令/长进程固定输入，不宣称整次聊天跨命令固定版本。
- 日常只使用统一根目录的 `work.cmd` / `work.ps1`；`doctor` 报告实际部署身份、规则、内容路径与 Review 范围。新命令或参数仅在实现后写入可执行帮助；Windows 原生结果与 WSL/mock 分别报告。
