# HyperFrames AI 创作 Harness

## 工作边界

- 本仓库公开管理 Harness 规则、模板、Profile 接入、Skill 路由与 Work CLI。
- WSL 是 Harness 工具的唯一开发面，负责 CLI、宿主接线、依赖装配与安装器；Windows 负责 Work 和视觉资产内容，包括 Work-local 或已登记 AssetSource 内的 Scene、GSAP 动作、Three.js、shader、SVG、模型与内容脚本。分类看职责，不以扩展名、复杂度或可复用性把视觉内容交回 WSL。
- Windows 不修改安装包、已接纳 AssetStore 包、冻结 vendor 或 Accepted Snapshot；变化在可编辑源中完成，需要复用时生成新版本。WSL 默认只读正式 Work 与生产资产源；仅按工具缺陷请求，在冻结最小私有副本中调试，不改生产 Current、Binding、接受状态或 Final。
- 所有作品的当前真源位于外部 WorkStore `D:\AI\AI+hyperframes`（WSL `/mnt/d/AI/AI+hyperframes`）的 `works/`，包括文案、媒体、工程、Draft、Final 和运行状态；这些内容不得进入开发仓或 Git。
- 不公开发布内容、不购买额度。只有用户对准确 Work 与 Variant 明确授权后，才可使用其已登录的 Windows Chrome 保存到小红书创作者平台草稿箱；不得读取 Cookie、调用未公开接口或点击发布。
- `podcast_quote_image` 的 URL 获取只调用外部 `trendradar-media` v2.0；仅采用校验成功并复制进当前 Work 的媒体，不引用其七天后过期的运行目录，也不在本仓库实现下载后端。
- 默认不生成 AI 图片；Plan 列明拟生成素材的用途、数量、风格和 Asset Brief 后，方向批准一并授权这些素材，不逐张询问；未列用途或明显超量再确认，私有内容转交新外部提供方仍需明确授权。生成内容不冒充真实界面、操作结果或数据证据。`design-taste-frontend` 仅用于已批准且明确要求其介入的图片 Asset Brief。不查询图片 Prompt 库。视频不生成或烧录底部字幕；播客图文沿用自己的双语字幕合同。

## 开发仓与 WorkStore 路径

- 当前开发仓真源为 `/home/jym/workspace/hyperframes+AI`；Windows 旧仓 `/mnt/c/Users/Jym/Documents/hyperframes+AI` 仅作为未删除的回滚副本，不继续开发。
- 当前正式 WorkStore 真源为 Windows `D:\AI\AI+hyperframes`（WSL `/mnt/d/AI/AI+hyperframes`）；生产 `work root show` 返回该路径，其 Current Work、命名锁和后续运行状态位于 WorkStore 的 `.runtime/`。候选工具只读取自身根配置指向的隔离 Review 内容，不切换正式指针。
- 开发仓通过本地且 Git 忽略的 `.studio/.runtime/work-root` 绑定 WorkStore。切换路径只使用 `./work root set <absolute-path>`，目标必须已经包含 `works/active`、`works/parked` 与 `works/archive`。
- 旧仓和旧 Work 副本不再具有当前权威；不得在新旧两处同时写入，也不得在没有单独明确授权时删除任一回滚副本。

## 入口与权限

生产入口按 `.agents/skills/hyperframes-codex-workflow/SKILL.md` 定位 Work、Variant 和阶段；完整视频流程只维护在 `.studio/workflow.md`。播客图文使用自己的 planner_skill / copy_skill，不加载视频规则。开发仓不执行生产启动步骤，不读取或修改生产 Current、Work、资产或默认配置。

Work 与 Variant 的创建、指针、等待、Park、接受、Final、Archive 与 Reopen 只通过 Work CLI；CLI 管理生命周期与一致性，不代替用户的方向批准、准确 Draft 接受或内容判断。后台每个命令显式绑定 Work/Variant，同一对象同时只允许一个执行者；多来源按 detached Work 分开，共享 ASR 只运行一个实例，调度不另建常驻 daemon。

Draft 与 test-work 不导出视频，包括带声短段、离线逐帧编码和预渲染镜头。只有生产 Variant 的 Finalize 交付链可生成视频；测试接受不变成生产接受。Studio 受限时记录未验证项并交工具缺口，不以导出绕过。软归档不授予接受、交付或删除权限，不搬目录、不清理依赖；旧物理归档保留兼容，不批量迁移。

保留原始来源、正式声音、稳定 Scene/Anchor ID、未受影响内容及旧接受/Final 快照。Studio 登记版本只在独立复制的审阅副本打开，不用 hardlink / symlink 暴露冻结源。生产源码和资产内容不得流入公开工具包。程序、规则、Windows 原生证据和生产验收分别报告，不把 mock 或夹具通过冒充真实完成。

只展示实际结果、变更、阻塞和必要决定，不展示流程自证或逐项审批清单；Plan 首版可完整展示，后续聚焦变更范围。

## Release 与 Codex App 部署

- Windows Codex App 直接打开 `D:\AI\AI+hyperframes`，根 `work.cmd` 根据自身路径运行同根 `runtime/` 与 `.studio/`；配置从 `.studio/.runtime/` 读取，不经过 `.harness/releases/current`、workspace 或 session，不生成自动 session。Windows 不编辑受管理工具文件。
- 一次命令解析配置一次；长进程固定本次 Work、Variant、资产、依赖与配置输入。继承的旧 session、HOME、AssetRoot 不得重定向工具或 Review；保留必要 Provider 凭据。配置修改仅影响后续命令。
- WSL 从当前受控工作树构建本机包，保留已完成 M2–M3 内容，不重跑 M0–M1，不自动 commit/tag/push。正式 `harness-YYYY.MM.PATCH` 发行仍要求干净、tag 与 upstream 一致；dirty 候选不冒充稳定发行。
- 获得目标部署授权后，WSL 使用固定 `./release deploy --root <Windows-root>`，不再编写一次性部署脚本。锁一致时发送绑定准确运行时 hash 的工具包，首次安装/锁变化发送完整包；只备份和重写变更文件。成功后默认保留最近两次回滚和当前及前两版登记产物，仅回收新机制拥有且完整的成功副本；历史、失败、未知内容及 Work/资产不自动清理。参数与恢复方式见 README 根目录部署。
- 严格发行包校验检查全部文件、hash、依赖与路径；部署根校验只检查 manifest 拥有的文件，不将 Work、配置或用户 Skill 视为损坏。生产更新只覆盖管理文件；旧清单拥有且新版本移除的文件才可删除，遇到用户修改保留并报告，不全根 mirror/delete。
- 更新先验证 staging、备份旧管理文件与迁移信息，再更新并最后写完成标记；中断可检测和恢复，损坏组合拒绝启动。复用现有进程记录与最小互斥，更新前停止相关 Studio/render/build 进程，不热换依赖，不新建 daemon。
- 候选部署在独立根，拥有同样的直接入口、独立配置与 Work/Asset/source-copy。Review 不写生产源、Current、接受记录或默认配置，不允许正式 Finalize、归档完成和平台草稿。不将隔离测试变成日常生产前置门。
- 优先登记已有 AssetSource；Windows 开发语义视觉对象并按实际 module/media 合同生成冻结新版本，不强制拆 helper、双画幅、五阶段或全库迁移。vendor / Binding / Lock 固定准确依赖，库离线不影响闭合作品，同身份版本不同内容拒绝覆盖。
- 工具缺口只交冻结最小复现给 WSL；视觉内容留 Windows。旧包、旧 session 与旧源码仅保留回退资料，不自动重写或删除。程序回滚不降级 Work schema、不重绑资产；不兼容时保留新数据与可用工具。外部发布、删除不可替代内容及安装切换仍遵守准确授权。

- Windows 共享 ASR 只通过包内 `asr-wsl.cmd` 调用固定的 `Ubuntu` 和 `/home/jym/workspace/_external/scripts/asr.sh`。桥接器必须拒绝 `D:\AI\AI+hyperframes` 外的输入或输出，并把 WSL 内的 `wslpath` 路径转换、ASR 可用性检查和转录合并为一次 `wsl.exe --distribution Ubuntu --exec /bin/sh -c <fixed-script>` 调用，任务参数经 `WSLENV` 传递，并原样传递 stdout、stderr 与退出码。Windows Codex 沙盒可复用 WSL ASR、模型和 GPU，但未获得包内 `asr-wsl.cmd transcribe-faster` 顶层 argv 前缀的持久授权时，每次 ASR 作业仍可能需要用户审批；不得授权任意 `wsl.exe` 命令。
- `D:\AI\AI+hyperframes` 是统一使用根：`runtime/`、`.studio/` 是已部署工具，`.studio/.runtime/` 是根配置；`asset-library/sources` 与 `asset-library/store` 保留可编辑源和冻结资产职责，不改用既有 `assets/`。Work、请求、Review 与 `.runtime/` 的既有内容保持不动，可写 Harness 开发真源仅在 WSL。
- 更新完成后重启相关工具进程，Agent 重读根规则；下一条根命令用新版本，无需创建 Harness session。单次命令/长进程固定输入，不宣称整次聊天跨命令固定版本。
- 日常只使用统一根目录的 `work.cmd` / `work.ps1`；`doctor` 报告实际部署身份、规则、内容路径与 Review 范围。新命令或参数仅在实现后写入可执行帮助；Windows 原生结果与 WSL/mock 分别报告。
