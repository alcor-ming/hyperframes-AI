# HyperFrames AI Harness

面向本地内容创作的轻量 Harness。它以 Work 组织一次交付，以 Variant 管理独立账号版本或测试批次，目前提供 `hyperframes_video` 与 `podcast_quote_image` 两条独立工作流。

## 快速开始

Windows 用户在 Codex App 直接打开 `D:\AI\AI+hyperframes`，新建对话并下达任务即可。`work.cmd` 是 Agent 按需调用的命令行工具，不是需要双击打开的聊天窗口；根入口不创建或依赖 Harness session，不选择候选或 Review 根。下文 Bash 命令是相同 CLI 的 WSL 写法。正式 Work 由 Windows 写入；WSL 开发和回测使用冻结请求与隔离副本。

```bash
./work root show
./work account list
# 使用已登记账号；尚无账号时先 account put <id> --file <实际配置.json>
./work new "作品标题" --workflow hyperframes_video --account <account-id>
./work status
./work variant add douyin-9x16 --account <other-account-id> --ratio 9:16
```

开发仓位于 `/home/jym/workspace/hyperframes+AI`，外部 WorkStore 位于 Windows `D:\AI\AI+hyperframes`（WSL `/mnt/d/AI/AI+hyperframes`）。本机绑定保存在 Git 忽略的 `.studio/.runtime/work-root`；只有 `./work root set <absolute-path>` 会切换 WorkStore。

`work new` 必须选择 Workflow。CLI 会在命名锁内按 Workflow 分配三位序号，并创建 `work-<workflow>-<序号>` 形式的 Work ID 和目录；输入标题只作为初始显示标题，不参与目录命名。视频制作入口是独立的叙事模式、视觉主题、背景与画幅，不要求前置 Profile。Theme 不拥有或限制叙事模式，也不隐含选择背景和运动。旧 `main`、Profile 和 Template 元数据继续兼容，不把旧 Profile 自动视为合格新主题。

```bash
./work new "人物口播" --workflow hyperframes_video --account <account-id> --template talking_head --subject-position left
./work wait recording
./work resume
```

播客图文接受本地视频或明确的来源 URL。URL 通过外部 `trendradar-media` v2.0 下载并校验后复制进 Work；YouTube 可先读取带时间戳的原生字幕，失败后再使用已授权的共享 ASR。第一个 Skill 通读转录并给出 3 个完整文章方案，用户确认其中 1 个；第二个 Skill 先调研嘉宾背景，再从获批的选取文段归纳开篇第一段、每图小标题和第三人称正文，最后仅根据这些文段的共同结论、冲突或因果拟定大标题。文段之外的嘉宾背景只能从开篇第二段起补充，不能主导标题。`PACKAGE.md` 直接保存可复制到创作者平台的纯文本标题、`01｜小标题` 分节、正文和话题，render 同步生成有序图片 JSON；每篇渲染 8 到 12 张图，图片用约 10 个汉字的 Hero 与支撑短句把中文控制在约 60 到 90 字，完整背景、案例和推导留在正文。画面使用 50px 中文与 30px 英文，Hero 至少占 60%，支撑字幕按双语文本高度紧凑排列：

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

后台 Work 在创建时已经获得稳定序号；转录完成后只补充嘉宾名 + 核心主题，再完成 3 个文章方案并停在 `article_selection`。HyperFrames 视频在 Script 稳定后只补充核心主题。Work ID 与目录名始终不变，重复命名保留原序号；`work list` 按位置、Workflow 和序号排列。用户只需确认 1 个方案；单个 Work 失败不阻塞同批其他 Work。

视频 `SCRIPT.md` 的口播正文可附成对 `scene-index` 注释包围的非口播 Scene 索引；配音、统计或对齐使用 `./work script text`。Research 按呈现需求准备候选材料，不规定实现；Plan 写清实际采用的屏幕文字、来源与声画取舍，不复制 Script/Research 全文。文字主导与动效主导独立于工程 Template；实际语义起点、同卡累积、三种场景策略和观看检查见 [表达合同](.studio/spec/visual-design.md)。PACKAGE 仅按交付需求生成，不是视频前置。

视频沿用现有 Script、Research、音频与 M2–M3 画面，先完成整片 Plan，再选一个真实 Scene 动态参考。一次方向批准后直接生成完整 planned-placeholder Draft，素材齐备后生成最终 Draft，沿用原完整接受和 Final 流程。不逐 Scene 审批，不新建 Shotbook，不把样段或占位 Draft 当成具备 Finalize 权限的 full Draft。

复用优先选择承担明确含义的视觉对象，保留内部联动和既有 helper。Plan 列清逐 Scene 的 A/B 职责、语义对象、素材占位 ID 与人声 cue 意图；音乐分析可选，已有 timestamps/section_map 优先复用。最终 Draft 必需素材齐备，计划内占位不阻塞此前全片预览。新登记参数只在实现并验证后加入帮助；旧 reference/layout 记录保持原含义。具体约定见 [创作工作流](.studio/workflow.md)。

日常预览默认启动锁定版本的官方 HyperFrames Studio，返回实际项目 URL；当前工程可编辑，登记版本只在隔离副本打开：

```bash
./work preview open current
./work preview context current --fields selection,lint --detail compact
./work preview open draft-v001
./work preview stop current
# 仅显式历史查看保留自制审阅页
./work preview open draft-v001 --legacy
```

Studio 修改同步原文案真源或暂停对应再生成，旧 MP4 / QA 不继续代表新源码。`reference` Plan 没有虚构的可播放工程，直接审阅其资产引用。

Draft 与 Final 生命周期：

```bash
./work preview register
./work preview open draft-v001
./work preview accept draft-v001
# 仅生产 Variant：从接受源编排渲染、编码 QA 与版本化交付
./work finalize
```

无文件参数注册素材齐备的 Studio executable Draft，冻结来源和闭合工程；须打开准确登记版本的隔离副本再接受，无整片 Draft MP4 前置。旧 `preview register /path/to/draft.mp4` 保留兼容。生产 Variant 可独立 Finalize，不等待其他账号；从接受快照渲染、保留正式收据并完成编码 QA，不重审未变设计。旧文件晋升入口的 `--qa-passed` 仍只表示已完成输出 QA。Draft 与 test-work 不导出视频，Studio 受限时也不以短段或预渲染镜头绕过。软归档是独立管理标记，无 Final 也可使用，不搬目录、不清理依赖；Finalize 不自动归档，也不包含发布/上传。

## v3.3 候选边界

系列、用途、账号默认值、主题与批次通过 Work CLI 管理，命令以当前部署帮助为准。候选提供 `theme|account|series put <id> --file <json>`、`get <id>`、`list`；视频 `new` 必须显式指定 `--purpose standard|ip|test`，生产视频还须 `--series` 和已登记的 `--account`，可另指定 `--batch`、`--theme`、`--mode text-led|animation-led` 与 `--ratio`；test Work 不绑定账号。`variant add` 可为同一账号创建不同版本，按准确 Variant ID 选择，`variant name` 修改可读名称。未指定模式时默认 `text-led`，不再默认填 Profile。账号设置和主题版本/参数在创建 Variant 时冻结，修改默认值不追改已有工程；IP Beta 不机械套标准模式。播客新建与三位序号规则不变。

静态外观支持 schema 2 Theme/Background/Motion 资产，沿用 `component pack/import/accept`，不另建主题库。新账号以 `{ref,kind,package_sha256}` 保存 theme/background，motion 槽位可显式设 null；旧 `theme put/get` 只承载兼容配置，不写新制式资产。`appearance resolve --account <id> --appearance-file <json>` 只读展示最终选择；`new`/`variant add` 同样接受 `--appearance-file`、独立 `--background <id@vN>`、`--fps` 和 `--seed`。锁与真实 vendor 一起冻结并纳入 preview，不依赖源库在线。字段及参数结构见 [资产合同](.studio/spec/hyperframes.md)。候选能力不等于已部署；动态背景、选择 UI、真实 Paper 拆分和 Windows 原生换配效果不由这些合同证明。

所有新视频 Work 默认把 Script/Research 放在 `shared/`，各 Variant 通过 `shared_inputs` 引用同一源，Plan/工程/接受/Final 各自独立。`variant add --from <variant-id>` 显式创建内容分支，不是仅为了新增账号而必需；旧 Variant 内文稿仍按原位置读取。创建隔离测试可用 `work new "联动测试" --workflow hyperframes_video --purpose test --batch <batch-id>`，只进行 Studio 验证，不导出视频。

RC2 视频 Work 的全局 ID 与系列号独立递增且不封顶于 999；`name` 与 `series move <id>` 不改 ID/目录，旧系列号保留为查询别名。`list --tree`、`find --series <id> --number <n> [--account <id>]`、`account get <id>` 和可重建的 WorkStore `浏览目录.md` 用于定位。旧视频 Work 的一次性改名只经 `migrate dry-run --output <map.json>` 审阅映射，再由 `migrate apply --mapping <map.json>` 显式执行；缺用途或含糊标题可用 `--purpose-overrides` / `--title-overrides` JSON 映射重做 dry-run。若一项被阻断，可用重复的 `--only <old-id>` 生成安全子集映射；同系列须按旧 ID 顺序迁移。映射文件必须新建于 WorkStore 外。迁移只在 WSL 合成 WorkStore 验证，尚未对生产 WorkStore dry-run/apply；工具部署状态以目标根的部署收据为准。

三项入口、四阶段及历史兼容见 [v3.3 合同](docs/PRD/hyperframes-v33-production-contract.md)，RC2 范围见 [RC2 执行方案](docs/PRD/hyperframes-rc2-execution-plan.md)。工具安装不等于 Remotion Windows 原生 Studio 联动、真实生产 Finalize/缓存复用或新 Work 内容验收；这些结果须分别取得证据，不以 mock 或文档冒充完成。除 RC2 明确的一次性旧视频 Work 身份迁移外，不批量迁移播客、接受快照与 Final。

## 外观、资产与研究入口

同一 Variant 可显式原位换配，不必新建版本身份。先检查差异，再用 `--apply` 提交；已知旧 runtime 另加 `--upgrade-runtime`，未知或用户修改的 runtime 不覆盖。中断遗留 journal 时用同目标 `appearance recover` 恢复，不手删记录。账号默认、正文与历史 preview/Final 保留，变化后的外观清空当前接受及 Final 关联，不能沿用旧交付作为新外观接受。

```bash
./work --work <work-id> --variant <variant-id> appearance rebind --theme <theme-id>@vN
./work --work <work-id> --variant <variant-id> appearance rebind --theme <theme-id>@vN --apply
./work component list --query <用途或别名> --kind module --ratio 9:16
./work research --root <登记根> register --kind tool --title <标题> --path <原文.md>
./work research --root <登记根> query --kind tool
```

发现结果支持类型、画幅、标签与推荐状态筛选；区分已接纳、候选、源和仅供参考，metadata-only 不等于完整校验。采用时仍验证精确版本/hash/闭包，缓存可用 `--rebuild` 重建；查询、推荐和研究更新都不改已有 Work。研究支持 create/register/query/update/sync/link/reference，正文为真源，修改记录使用当前 revision，摘要更新校验当前正文 hash；过期或失败不覆盖正文、不自动改 Plan 或接受状态。详见 [技术合同](.studio/spec/hyperframes.md)。

本地 Theme 字体由 `await HarnessAppearance.load()` 等待加载，再同步 apply；通过 Typography CSS 变量使用隔离字体族，实例结束 dispose。MP3 使用原生 media 合同与真实 probe/decode 检查，入库不代表听感或成片声音接受。文字与辅助图形的制作默认只见 [visual-design](.studio/spec/visual-design.md)：图形内容仍由 Windows 制作，WSL 只修工具和入口，不随包提供或宣称已接纳四类图形预设。

## 公开内容

- `AGENTS.md`：环境与权限边界。
- `.studio/`：工作流、能力表、规范、Recipe、模板和生命周期 CLI。
- `.agents/skills/hyperframes-codex-workflow/`：阶段路由 Skill 与可选的旧外观参考。
- `.agents/skills/hyperframes-anti-ppt/`：指向单一表达合同的兼容检查入口。
- `.agents/skills/podcast-quote-image/`：转录理解、原文证据整理与 3 个文章候选方案 Skill。
- `.agents/skills/xiaohongshu-article-copy/`：标题、开篇、每图文案、DBS 检查、取帧、渲染与 QA Skill。
- `.agents/skills/native-subtitle-quote-image/`：无法转录时经人工确认启用的 [原版 v1.0.0 Skill](https://github.com/chengyi-ai/native-subtitle-quote-image/tree/f1fa5b70448f620ea92179357eca4b0222481b9d)。
- `work`：无第三方依赖的本地 Work CLI。

## 私有内容

外部 WorkStore 的 `works/`、旧 `tasks/`、媒体、工程、Draft、Final 和运行状态不进入开发仓或 Git。Harness 不实现下载后端，而是调用独立的 `trendradar-media`；它不公开发布内容，也不内置 ASR 模型。经用户对准确 Work/Variant 明确授权，可使用其已登录的 Windows Chrome 保存小红书创作者平台草稿，但绝不点击发布。

默认由 Windows Work-local Scene 组合模块与媒体，而不是填入完整冻结组件的 Slots。Windows 在 Work-local 或已登记 AssetSource 开发 Scene、GSAP、Three.js、shader、SVG、图片和模型；兼容视觉资产在 Windows 打包、精确接纳，不触发 Harness 发布。AssetSource 可编辑，AssetStore 已接纳包不可原地修改；先登记已有来源，不建立第二份可写权威库。`migration-ready` 不自动通过，不强制全库、双画幅、五阶段或全画幅透明根层。Work 沿用 vendor、Binding 和 `COMPONENT_LOCK.json` 固定实际依赖，库更新不漂移旧作品，已有闭合副本不依赖外部库在线。旧完整组件和历史快照只读兼容，不自动拆解或删除。

M1 扩展 module/media 最小子集，旧 Component 合同保留兼容；Template / Recipe、完整 Background / Profile 独立安装仍是后续目标。`component pack` 从 Windows 源目录的 `asset.json` 冻结实际文件，不修改编辑中源。Windows 使用根目录 `work.cmd`：

```bash
./work component source-add <existing-source-directory>
./work component pack <source-directory-with-asset.json>
# 导入已有冻结包时改用 component import <exact-package-directory>
# Windows 审阅独立副本后，使用 pack/import 返回的精确摘要
./work component accept <component-id>@vN --sha256 <package-sha256> --note <review-result>
./work component list --query <relationship-or-name>
```

资产配置归属当前入口根，变更只影响后续命令，长进程固定启动时输入；Review 不修改生产配置。module/media 的 `asset.json` 与 Binding 示例见 [资产 PRD](docs/PRD/hyperframes-component-motion.md#4-m1-最小资产合同)。独立样例沿用已实现的 `component install ... --project <registered-source/sample>` 与 `component verify --project <registered-source/sample>`，不伪装正式 Work，不增加另一套播放器。

## WSL 解析器开发依赖

`python3 .studio/prepare_windows_runtime.py dev-parser` 从 `windows-npm.lock.json` 派生并安装本地 Acorn/esbuild，写入忽略目录 `.studio/.runtime/dependency-parser`，不创建第二份受管依赖清单。缓存齐全时可加 `--offline`。Windows 产品包使用同根 `runtime/npm` 的锁定解析器；扫描只解析输入代码，不执行待检查工程。

## 根目录部署

Windows 日常直接打开 `D:\AI\AI+hyperframes`；工具实际位于同根 `runtime/`、`.studio/`，根配置位于 `.studio/.runtime/`。直接 `work.cmd` 按自身位置选择工具，不经过 `.harness/releases/current` 或 session，不自动生成 session。已有 Work、资产、用户 Skill 与请求不迁移。

一次命令解析配置一次，Preview/render 固定本次输入；更新前通过已有进程管理停止相关进程，以最小互斥防止启动和更新交错，不热换依赖。配置变更只影响后续命令，Agent 更新后重读根规则。

待安装 ZIP/staging 严格校验全部清单、hash 和路径；部署根只校验拥有的管理文件，保留合法用户文件和本地配置。更新先备份再覆盖管理文件，只有旧清单拥有且新版移除的文件可清理；用户修改冲突保留并报告，中断可检测恢复，不全根 mirror/delete。

WSL 固定部署入口（执行即更新指定根，必须已有该目标的部署授权）：

```bash
./release deploy --root 'D:\AI\AI+hyperframes'
```

默认使用 `.studio/.runtime/windows-runtime-cache` 中锁定的依赖，缺失时报告而不联网安装。
构建仍只包含受控文件；新增产品文件逐项用 `--include <path>` 指定，私有文件和开发 Harness 不可进入包。
首次安装用 `--config <Windows-JSON-path>` 指向已有配置，目标 WorkStore 目录需先存在；已有配置不被覆盖。
命令在 WSL 构建，传输到目标同级 `.hyperframes-deploy/deploy-*`，用独立的锁定 Windows Python 执行原生校验和部署。
无需临时编写 PowerShell、处理 UNC 执行或创建 session；活跃的根进程导致拒绝更新，不自动杀进程。

运行时锁与安装清单一致时构建 `tools` 包，不包含 `runtime/`，并绑定准确运行时文件 hash；首次安装、依赖锁变化或 `--full` 时构建完整包。
原生部署仍验证全部已有管理文件；只备份和重写内容变化的文件，旧清单中删除的文件也进入回滚备份。
工具包不能独立安装，运行时不符时拒绝，不静默采用其他版本。

默认 `--keep 2`：保留最近两次回滚备份；新入口按目标登记的产物位于 `dist/deployments/`，保留当前及前两版。
只回收新机制登记、成功且 hash 完整的过期备份/产物；未知内容、用户修改、旧机制副本和失败现场保留。
本次 Windows staging 在原生进程成功退出后删除，失败时返回 staging 和日志路径；恢复沿用独立包内
`.studio/root_deploy.py recover/rollback --root <Windows-root>`，由根外的 Windows Python 执行，未保留的更早回滚不可用。
清理随成功部署触发，不是定时任务；不清理生产 Work、资产、浏览器缓存、旧 `dist/` 或历史 staging。
结果返回版本、包类型、传输包大小、变更数量、备份字节和清理结果；清理失败不把已成功的部署伪装成回滚。

本机候选基于当前受控工作树，不回退公开 HEAD，不重跑 M0–M1，不自动 commit/tag/push。候选根使用独立配置与 Work/Asset/source-copy，真实入口形态与生产一致，不写生产 Current 或接纳状态。先交付 R1 根候选，再按 Windows 所选 Work 暴露的问题修 R2/R3；不把候选通过冒充已更新生产。

`release local` / `release candidate` 仍区分本机构建身份；正式 `release build` 使用 `harness-YYYY.MM.PATCH`，要求干净、tag 与 upstream 一致。完整包固定 Windows Python、Node、HF、GSAP/Three、浏览器及音视频依赖，普通制作不浮动安装。准确安装参数仅以实现后的帮助为准，不将设计目标写成可执行命令。

产品包不携带本机开发用 Trellis：候选源选择排除开发目录与 Skills，显式 include 不可绕过；正式发行发现这些文件时拒绝构建，最终 ZIP 再检查一次。保留项目自身 Work CLI、轻量状态机与创作 Skills，Windows 根规则仍来自独立模板，运行不依赖开发仓。

旧稳定包与历史 session 保留回退资料，不再作为新根的依赖。回滚程序不自动降级 Work schema、改资产绑定或删旧数据；旧工具无法读取时保留新数据与可用版本。实现、WSL/mock、Windows 原生 CLI、Studio、WebGL、带声短片及真实生产验收分别记录。

Windows 直接开发视觉内容和效果；仅宿主、CLI、合同、加载、seek 或依赖装配缺口交给 WSL。`work request freeze` / `export` 冻结最小复现，WSL 在私有副本修工具并交付安装候选，Windows 在 Review 验证；纯布局、图标或动作设计不走工具请求。旧 `deliver` / `review` / `accept` 补丁合同保留兼容，不扩大 WSL 写生产源的权限。完整参数见 [请求交接](.studio/workflow.md#windows-与-wsl-请求交接)。Review 不允许正式 Finalize、归档完成或保存平台草稿；模拟资产接纳仅留 Review，接纳交付不等于接受 Plan/Draft，不覆盖未受影响场景。

Windows 原生、交互 WebGL、抓帧 WebGL、视频硬件编码和真实复用分别验证。构建或 Linux 测试通过不表示 Windows 已部署或硬件路径通过。目标与验收边界见 [Windows 工作台 PRD](docs/PRD/hyperframes-windows-workbench-wsl-handoff.md)。

Windows 侧共享 ASR 由包内 `asr-wsl.cmd` 桥接到固定的 `Ubuntu` 和 `/home/jym/workspace/_external/scripts/asr.sh`；`HYPERFRAMES_ASR_SCRIPT` 仅可指定另一 Windows 入口。桥接器拒绝 WorkStore 外的输入和输出，并把路径转换、可用性检查和转录合并为唯一一次固定调用：

```text
wsl.exe --distribution Ubuntu --exec /bin/sh -c <fixed-script>
```

任务参数只经 `WSLENV` 传入，路径由 WSL 内的 `wslpath` 转换；stdout、stderr 和退出码原样返回。Windows Codex 沙盒已确认能复用 WSL ASR、模型和 GPU，但未持久授权时每次调用仍可能先报 `Wsl/Service/E_ACCESSDENIED` 并要求审批。Codex 规则只匹配 Agent 发起的顶层 argv，因此应持久批准包内 `asr-wsl.cmd transcribe-faster` 前缀；不得批准任意 `wsl.exe` 命令。

完整产品契约以 `.studio/` 和 `AGENTS.md` 为准。
