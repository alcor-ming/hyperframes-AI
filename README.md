# HyperFrames AI Harness

面向本地视频创作的轻量 Harness。v3.8 化繁为简：Work 管一期内容，Variant 管独立账号版本或测试批次；普通修改保留在原 Variant，Draft、接受快照与历次导出记录其迭代。当前只提供 `hyperframes_video` 制作。

## 快速开始

资产选型使用 `work component list` 的生成式目录，可按 `--asset-layer` 筛选；参考样例默认隐藏且不可新安装，显式查看用 `--include-references`，或直接指定 `--kind scene-source` / `--kind recipe`。`component migrate plan|apply` 合并明确指定的资产目录，`component archive plan|apply` 保存非破坏性归档快照；不自动接纳、不删除旧包、不修改已有 Work。接口与边界见 [.studio/spec/hyperframes-assets.md](.studio/spec/hyperframes-assets.md)。

视频支持 `card` 卡片模式与 `explainer` 有声动态图解，均使用 16:9 / 9:16 五层宿主：背景、主体、强调转场、独立文字、口播字幕。`--captions on|off` 为 Variant 开关，card 默认关闭、explainer 默认开启。A/B-roll 管主画面时间切换，Plan 按 Scene 维护编排、内嵌上屏文字、素材、声音 cue 与节奏事件。声音层对两种模式开放；Finalize 渲染最终 MP4，不含平台工作流。

另有 `showcase` 模式，仅 Opus 5.5 制作，Codex 不接制作；创建时显式冻结 `pdoom` / `science` 子模块，使用精简 Plan 与接受后提炼模板。不强制 explainer 正向方向、D14、Q1 或 Draft 前节奏闭环，事实、授权、seek 与离线闭包等硬约束不变，见 [showcase 合同](.studio/spec/showcase.md)。`explainer` 系列可声明 `spec=math-rap`，以数学图解替代角色/生图、字幕显示歌词；Research 记录原片与声音来源，不新增账号或声音来源拦截，见 [数学系列合同](.studio/spec/math-rap.md)。

数学链路复用 `cues build --alignment <文件>` 的歌词逐字对齐，不对未对齐字插值。正式声音已有且 cue 已建立后，使用 `./work --work <id> --variant <id> beats build --audio <Work相对音频路径> --beats-per-bar <每小节拍数> --first-downbeat <零基拍点索引>`；锁定上游提取拍点，拍号和首个强拍须人工明确，弱起不猜测，生成的网格绑定音频摘要。`plan check` 报告数学职责、符号一致性和收尾空档，不替代观看或接受。

`./work --work <id> --variant <id> review package <审查ID> --manifest <Work相对JSON路径>` 将当前 Plan、字级时间/节拍和声明文件复制到 WorkStore 的 `review/<审查ID>`。声明格式为 `{"scenes":["variants/<版本>/project/scene.html"],"screenshots":[{"time":1.5,"path":"materials/frame.png"}],"contact_sheet":"materials/contact-sheet.png"}`；截图先通过官方 Studio/snapshot 取得，命令只复制，不导出视频、不扫描未声明素材。审查输出使用【图】【码】【未实现】证据、严重度表与推荐分镜表。

Windows 用户在 Codex App 直接打开 `D:\AI\AI+hyperframes`，新建对话并下达任务即可。`work.cmd` 是 Agent 按需调用的命令行工具，不是需要双击打开的聊天窗口；根入口不创建或依赖 Harness session，不选择候选或 Review 根。下文 Bash 命令是相同 CLI 的 WSL 开发写法。WSL 开发和回测使用冻结请求与隔离副本；Claude Code 在生产根 `/mnt/d/AI/AI+hyperframes` 读取受管理 `CLAUDE.md`，通过 `./work-wsl.sh` 调用同根 Windows CLI。仅此生产会话可制作获授权 showcase，直接编辑授权 Work 的文稿与工程源；作品及输出留在生产根，不在 WSL 另起 Studio 或渲染器。数学等系列只读审查使用声明范围内的审查包。

```bash
./work root show
./work account list
# 先准备共享内容，不强制选账号或创建 Variant
./work new "作品标题" --workflow hyperframes_video --purpose standard --series <series-id>
./work status
# 制作生产 Variant 时使用已登记账号
./work variant add douyin-9x16 --account <account-id> --ratio 9:16
```

开发仓位于 `/home/jym/workspace/hyperframes+AI`，外部 WorkStore 位于 Windows `D:\AI\AI+hyperframes`（WSL `/mnt/d/AI/AI+hyperframes`）。本机绑定保存在 Git 忽略的 `.studio/.runtime/work-root`；只有 `./work root set <absolute-path>` 会切换 WorkStore。

`work new` 创建视频 Work。CLI 在命名锁内分配 `work-hyperframes_video-<序号>-<初始标题slug>`，与系列号独立且不封顶于 999。后续改标题不改 ID 或目录。视频制作入口是独立的叙事模式、视觉主题、背景与画幅，不要求前置 Profile。Theme 不拥有或限制叙事模式，也不隐含选择背景和运动。

```bash
./work new "人物口播" --workflow hyperframes_video --purpose standard --series <series-id> --account <account-id> --variant-id talking-head --template talking_head --subject-position left
./work wait recording
./work resume
```

后台任务使用 `--detached` 创建 Work，并始终显式绑定自己的 Work / Variant。Current 只代表操作焦点；独立作品可并行推进，同一对象保持一个执行者。Script 稳定后用 `work name` 补充语义标题，不改变 ID 或目录。

```bash
./work new "另一作品" --workflow hyperframes_video --purpose standard --series <series-id> --detached
./work --work <work-id> --variant <variant-id> status
./work list --tree
```

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

Studio 对 current 的修改同步原文案真源或暂停对应再生成，旧 MP4 / QA 不继续代表新源码。登记版本的独立审阅副本文件只读，不支持 Studio 保存；打开时先校验，副本变化则新建目录并保留旧副本，不放宽诊断完整性检查。`reference` Plan 没有虚构的可播放工程，直接审阅其资产引用。

F01-F08 卡片使用 Plan `card` 块作为唯一内容源。安装已接纳的 `card-kit@v1` 后运行 `./work --work <id> --variant <id> cards build --browser <Chromium路径>`，先实测容量再更新生成挂载，保留其他手写内容。`cards studio` 提供官方 Studio 旁的 Plan 回写编辑器；保存使方向批准和旧接受失效，不拦截原生 Studio 的任意源码编辑。导出源、槽位及 A/B 接线见 [卡片接口卡](.studio/spec/card-kit.md)。

数学首批积木使用同 Scene 的 `math-plan` 定义单元与 cue，`math` 块只定义对应布局和冻结字体。安装已接纳的 `math-kit@v1` 后运行 `./work --work <id> --variant <id> math build --browser <Chromium路径>`；构建检查真实字形、系统字体回退和文本容量，再更新受保护挂载。接口、九种积木、导出与闭包约定见 [数学积木接口卡](.studio/spec/math-kit.md)。开发仓只做隔离验证，Windows 原生和部署后带声效果验收另报。

对已打开的准确目标运行 `./work --work <id> --variant <id> preview diagnose <current或Plan/Draft-ID>`，支持 executable 登记（`plan-vNNN` / `draft-vNNN`），拒绝静态 `reference` 和 `layout`。只读输出上屏照搬、Plan 信息缺失/截短、其他实现偏离和静止疑点，不作 QA 通过判断。Plan 支持新 `screen` 信息块与旧表格格式。登记 Plan/Draft 使用同版冻结的 Script、Research、Plan 与工程，当前文稿的跨版本差异另列；输入在诊断期间变化则报告过期。单 Scene Plan 参考沿用登记的 `sample_scenes`，其他 Scene 列入 `d1.out_of_scope`（不在本参考范围），不报缺失或未验证。文字按 `data-info-id` 或与唯一信息块的精确文本匹配归属；无法唯一归属时按元素列为待核验，相关信息不报缺失。多信息 Scene 可在信息块容器上标注可选的 `data-info-id`。参数及明确引用例外见 `preview diagnose --help`。范围内未采样状态、无法确认 ready 的媒体/子画面及图片内文字保留未验证，仍需按 [Draft QA](.studio/spec/hyperframes.md#draft-qa) 连续观看；诊断不导出视频或修改接受状态。

画面复盘使用 `./work --work <id> --variant <id> retro open <Draft-ID>` 与 `retro check`。记录按 Draft 保存；用户确认的样片和缺陷分别通过 `sample`、`defect` 管理，跨片机械统计用 `retro summary`。制作在 Plan 中引用样片段，`plan refresh` 固定参考帧与设置，Draft 和 critic 继承同组证据。详情及完整命令见 [画面复盘与样片记忆](.studio/workflow.md#画面复盘与样片记忆)。生产根 `sample-library/`、`known-defects/`、`retro-summary/` 属于用户内容，不进入 Git、发行包或部署管理清单。

Draft 与 Final 生命周期：

```bash
./work preview register
./work preview open draft-v001
./work preview accept draft-v001
# 仅生产 Variant：从接受源编排渲染、编码 QA 与版本化交付
./work finalize
```

无文件参数注册素材齐备的 Studio executable Draft，冻结来源和闭合工程；须打开准确登记版本的隔离副本再接受，无整片 Draft MP4 前置。生产 Variant 可独立 Finalize，不等待其他账号；从接受快照渲染、保留正式收据并完成编码 QA，不重审未变设计。Draft 与 test-work 不导出视频，Studio 受限时也不以短段或预渲染镜头绕过。成功 Finalize 归档目标 Variant；至少一个版本且全部归档后 Work 才整体归档。编码或 QA 失败不归档；成片已提升但归档记录中断时，重试从准确收据恢复，不重复编码。Finalize 不包含发布/上传。

## 归档、反悔与导航

`work list` 默认展示 active（含 parked），`--archived` 看归档、`--all` 看全部；`--tree` 和 WorkStore 的 `浏览目录.md` 展示同一份标题、系列号、版本归档数、焦点、等待事项与最近导出。工程、最新和历史成片均链接到准确对象，容量按需盘点，未知不当成 0。

```bash
./work list --archived --tree
./work reopen <work-id> --variant-id <variant-id>
./work --work <work-id> archive --variant-id <variant-id> --outcome abandoned
./work --work <work-id> storage inspect
./work --work <work-id> storage cleanup
# 核对上一步清单后执行可回收缓存清理
./work --work <work-id> storage cleanup --apply
```

对成片不满意，取消原 Variant 归档继续改，不新建 Work 或 successor。新增版本或重开任一版本后 Work 回 active，其他版本保持归档；零版本不自动完成。未导出版本可手动归档并显示未导出。归档与恢复不搬目录；`park` 只暂停 Work，`resume` 解除暂停，不改等待事项、兄弟版本归档或 Studio 路径。

历史条目共同保留成片与当次收据；旧散装成片缺少可证明来源时显示历史来源未知。归档保留反悔所需文件。`storage cleanup` 默认仅预览，`--apply` 才清理证明归属、可重建、无引用且进程已停止的缓存；原媒体、源、接受快照、历史成片、未知内容和失败证据保留。

已退役或未知 Work 会明确报告，不再执行旧制作流程，也不阻断无关视频创建；本版本不自动删除旧作品文件。

## 账号、系列与制作版本

系列、用途、账号默认值、主题与批次通过 Work CLI 管理，命令以当前部署帮助为准。提供 `theme|account|series put <id> --file <json>`、`get <id>`、`list`；视频 `new` 必须显式指定 `--purpose standard|ip|test`，生产视频还须 `--series`，但可无账号、零 Variant 先准备共享内容；明确账号时用 `--account <id> --variant-id <id>` 一步创建 Work 与版本，新生产 Variant 仍须已登记账号，可另指定 `--batch`、`--theme`、`--mode card|explainer|showcase` 与 `--ratio`，showcase 必须同时指定 `--submodule pdoom|science`，Theme/Background/Motion 可选且不继承账号外观；test Work 不绑定账号。`variant add` 可为同一账号创建不同版本，按准确 Variant ID 选择，`variant name` 修改可读名称。无显式、账号或系列模式时默认 `card`，不再默认填 Profile。系列身份/版本/规格、账号设置和主题版本/参数在创建 Variant 时冻结，修改默认值不追改已有工程；`purpose=ip` 推荐 `explainer`，但不改默认值。

静态外观支持 schema 2 Theme/Background/Motion 资产，沿用 `component pack/import/accept`，不另建主题库。新账号以 `{ref,kind,package_sha256}` 保存 theme/background，motion 槽位可显式设 null。`appearance resolve --account <id> --appearance-file <json>` 只读展示最终选择；`new`/`variant add` 同样接受 `--appearance-file`、独立 `--background <id@vN>`、`--fps` 和 `--seed`。锁与真实 vendor 一起冻结并纳入 preview，不依赖源库在线。字段及参数结构见 [资产合同](.studio/spec/hyperframes.md)。候选能力不等于已部署；选择 UI、真实 Paper 拆分和 Windows 原生换配效果不由这些合同证明。

Motion v3 增加风格入退场、一次性强调与转场、back-out/spring 及 cue 相位 hold_fps；允许不同槽混用 v2/v3，新 lock 采用最高能力版本，旧冻结 Work 不自动升级。完整账号外观指定 Theme/Background/Motion；跨账号风格叠加省略 theme，保留各自账号 Theme。B-roll module 可通过 `component list --broll-role hook|concept|transition --tag <style>` 查询，接口卡显示完整挂载示例和插槽；Scene 手动接既有 A/B 编排，Binding schema 不变。合同与生产源自检见 [镜头创作指南](.studio/spec/broll-assets.md)。

card 与数学单片只复用冻结库资产，不调用 Opus；card 镜头可选、无配额。生产根 Claude 可创作库源/pack 候选（用户接纳），或在方向批准后独占制作非数学 explainer 的 1–2 个指定主镜头，再交回 Codex；主镜头不享受 showcase 豁免。首次库制作、主镜头交接工具化和真实生产内容验收不随开发或工具部署自动执行。

所有新视频 Work 默认把 Script/Research 放在 `shared/`，各 Variant 通过 `shared_inputs` 引用同一源，Plan/工程/接受/Final 各自独立。`variant add --from <variant-id>` 显式创建内容分支，不是仅为了新增账号而必需；旧 Variant 内文稿仍按原位置读取。创建隔离测试可用 `work new "联动测试" --workflow hyperframes_video --purpose test --batch <batch-id>`，只进行 Studio 验证，不导出视频。

RC2 视频 Work 的全局 ID 与系列号独立递增且不封顶于 999；`name` 与 `series move <id>` 不改 ID/目录，旧系列号保留为查询别名。`list --tree`、`find --series <id> --number <n> [--account <id>]`、`account get <id>` 和可重建的 WorkStore `浏览目录.md` 用于定位。旧视频 Work 的一次性改名只经 `migrate dry-run --output <map.json>` 审阅映射，再由 `migrate apply --mapping <map.json>` 显式执行；缺用途或含糊标题可用 `--purpose-overrides` / `--title-overrides` JSON 映射重做 dry-run。若一项被阻断，可用重复的 `--only <old-id>` 生成安全子集映射；同系列须按旧 ID 顺序迁移。映射文件必须新建于 WorkStore 外。迁移只在 WSL 合成 WorkStore 验证，尚未对生产 WorkStore dry-run/apply；工具部署状态以目标根的部署收据为准。

三项入口、四阶段及历史兼容见 [v3.3 合同](docs/PRD/hyperframes-v33-production-contract.md)，RC2 范围见 [RC2 执行方案](docs/PRD/hyperframes-rc2-execution-plan.md)。工具安装不等于 Remotion Windows 原生 Studio 联动、真实生产 Finalize/缓存复用或新 Work 内容验收；这些结果须分别取得证据，不以 mock 或文档冒充完成。除 RC2 明确的一次性旧视频 Work 身份迁移外，不批量迁移旧作品、接受快照与 Final。

## v3.4.1 补充

[已批准补充方案](docs/PRD/hyperframes-v341-supplement.md) 增加归档生产 Work 的同号继任，并取消视频 main 的选择、继承与交付特权。Work 不属于账号；零 Variant 可整理共享内容、查看状态与切换 Work，但不能制作、预览或 Finalize。多版本无准确选择时返回候选，不自动选择 main；Current 只表示焦点，不跨 Work 沿用。v3.8 按所有现存 Variant 的归档状态汇总 Work，不再用 `required_variants` 维护另一套完成判据；零版本不算完成。已有 main、账号冻结、接受和 Final 保持兼容。

继任入口为 `work successor <source-work> --source-variant <id> --source-version draft-vNNN --account <id> [--variant-id <id>] [--title <title>] [--detached]`。它从准确归档源的接受版本建立新实体与自有内容，不继承接受或 Final，保留原系列号且不改变高水位。`work find --series <id> --number <n>` 定位当前对象，`--history` 查看完整链；旧 ID/别名仍定位旧实体。普通新一期继续递增，归档或删除继任不使查询回退旧对象。日常修订或账号适配仍使用现有活动 Work，不以继任替代。文档不代表已部署或真实作品已变更。

继任采用的文稿进入 `shared/`；冻结工程、媒体和原 Plan 留在新 Work 的 `materials/predecessor/`，新 Variant 按目标账号冻结配置并重新制作 Plan，不把原账号工程冒充新账号接受。源版本缺少冻结文稿或媒体依赖不闭合时拒绝创建。中断后重试原 `successor` 命令完成恢复，不手删 `.runtime/work-successor.json`。

## 外观、资产与研究入口

同一 Variant 可显式原位换配，不必新建版本身份。先检查差异，再用 `--apply` 提交；已知旧 runtime 另加 `--upgrade-runtime`，未知或用户修改的 runtime 不覆盖。中断遗留 journal 时用同目标 `appearance recover` 恢复，不手删记录。账号默认、正文与历史 preview/Final 保留，变化后的外观清空当前接受及 Final 关联，不能沿用旧交付作为新外观接受。

```bash
./work --work <work-id> --variant <variant-id> appearance rebind --theme <theme-id>@vN
./work --work <work-id> --variant <variant-id> appearance rebind --theme <theme-id>@vN --apply
./work component list --query <用途或别名> --kind module --ratio 9:16
./work research --root <登记根> register --kind tool --title <标题> --path <原文.md>
./work research --root <登记根> query --kind tool
```

创作查询用 `component list --include-references --query <用途>` 同时查包、场景源与配方；普通 list 保持参考项默认隐藏。列表 `detail.argv` 可直接传给本根 work 入口查询详情，`full_result` 可取完整 JSON；截断时保留总数和准确目标。`component interface` 区分当前状态、入口、限制与真实下一步，歧义必须按路径选择；参考项没有安装权或虚构派生命令。`list --audit` 和 interface 均不写缓存、索引或报告。

发现结果支持类型、画幅、标签与推荐状态筛选；区分已接纳、候选、源和仅供参考，metadata-only 不等于完整校验。采用时仍验证精确版本/hash/闭包，缓存可用 `--rebuild` 重建；查询、推荐和研究更新都不改已有 Work。研究支持 create/register/query/update/sync/link/reference，正文为真源，修改记录使用当前 revision，摘要更新校验当前正文 hash；过期或失败不覆盖正文、不自动改 Plan 或接受状态。详见 [技术合同](.studio/spec/hyperframes.md)。

本地 Theme 字体由 `await HarnessAppearance.load()` 等待加载，再同步 apply；通过 Typography CSS 变量使用隔离字体族，实例结束 dispose。MP3 使用原生 media 合同与真实 probe/decode 检查，入库不代表听感或成片声音接受。文字与辅助图形的制作默认只见 [visual-design](.studio/spec/visual-design.md)：图形内容由 Windows 制作，组件也可纳入 WSL 开发计划；WSL 负责工具和入口，不随包宣称已接纳图形预设。

## 公开内容

- `AGENTS.md`：环境与权限边界。
- `.studio/`：工作流、能力表、规范、Recipe、模板和生命周期 CLI。
- `.agents/skills/hyperframes-codex-workflow/`：阶段路由 Skill 与可选的旧外观参考。
- `work`：无第三方依赖的本地 Work CLI。

## 私有内容

外部 WorkStore 的 `works/`、旧 `tasks/`、媒体、工程、Draft、Final 和运行状态不进入开发仓或 Git。Harness 不实现下载后端，而是调用独立的 `trendradar-media`；它不公开发布内容，也不内置 ASR 模型。不购买额度、不读取 Cookie 或凭据、不点击发布；外部或付费服务必须单独取得用户授权。

默认由 Windows Work-local Scene 组合模块与媒体，而不是填入完整冻结组件的 Slots。WSL 与 Windows 均可编写组件，WSL 开发计划可包含组件编辑；Windows 在 Work-local 或已登记 AssetSource 开发 Scene、GSAP、Three.js、shader、SVG、图片和模型；兼容视觉资产在 Windows 打包、精确接纳，不触发 Harness 发布。AssetSource 可编辑，AssetStore 已接纳包不可原地修改；先登记已有来源，不建立第二份可写权威库。`migration-ready` 不自动通过，不强制全库、双画幅、五阶段或全画幅透明根层。Work 沿用 vendor、Binding 和 `COMPONENT_LOCK.json` 固定实际依赖，库更新不漂移旧作品，已有闭合副本不依赖外部库在线。

资产类型与接线以 [实现合同](.studio/spec/hyperframes.md) 为准。`component pack` 从 Windows 源目录的 `asset.json` 冻结实际文件，不修改编辑中源。Windows 使用根目录 `work.cmd`：

```bash
./work component source-add <existing-source-directory>
./work component pack <source-directory-with-asset.json>
# 导入已有冻结包时改用 component import <exact-package-directory>
# Windows 审阅独立副本后，使用 pack/import 返回的精确摘要
./work component accept <component-id>@vN --sha256 <package-sha256> --note <review-result>
./work component list --include-references --query <relationship-or-name>
./work component interface <列表返回的准确引用或路径> --json
```

资产配置归属当前入口根，变更只影响后续命令，长进程固定启动时输入；Review 不修改生产配置。module/media 的 `asset.json` 与 Binding 示例见 [资产 PRD](docs/PRD/hyperframes-component-motion.md#4-m1-最小资产合同)。独立样例沿用已实现的 `component install ... --project <registered-source/sample>` 与 `component verify --project <registered-source/sample>`，不伪装正式 Work，不增加另一套播放器。

Windows 资产开发任务完成指：包已打包接纳，或场景源/配方已写发现字段，并且 `component list --audit` 无该项告警。配方目录先用 `component source-add <目录>` 登记为 AssetSource。场景源和配方是派生参考、不可安装，可用 `component list --kind scene-source|recipe --query <用途>` 检索；`doctor` 显示只读漏登审计摘要。发现数量不代表已接纳数量。生产元数据补充由 Windows 按具体授权执行，WSL 不代改生产资产，使用隔离夹具验证规则。

场景源 `manifest.json` 使用以下发现字段；`entry` 为相对场景源目录的文件，`tags` 为数组，`limits` 为字符串或数组。配方 Markdown 沿用项目的 JSON front matter（`---` 内放 JSON 对象），使用相同字段但省略 `entry`：

```json
{"source_ref":"card-family-v1","title":"卡片家族","purpose":"文字信息卡片","tags":["card","text"],"workflow_role":"scene-source","primary_category":"card","classification_status":"approved","entry":"index.html","limits":["派生参考，不可直接安装"]}
```

## WSL 解析器开发依赖

`python3 .studio/prepare_windows_runtime.py dev-parser` 从 `windows-npm.lock.json` 派生并安装本地 Acorn/esbuild，写入忽略目录 `.studio/.runtime/dependency-parser`，不创建第二份受管依赖清单。缓存齐全时可加 `--offline`。Windows 产品包使用同根 `runtime/npm` 的锁定解析器；扫描只解析输入代码，不执行待检查工程。

## 根目录部署

Windows 日常直接打开 `D:\AI\AI+hyperframes`；工具实际位于同根 `runtime/`、`.studio/`，根配置位于 `.studio/.runtime/`。直接 `work.cmd` 按自身位置选择工具，不经过 `.harness/releases/current` 或 session，不自动生成 session。已有 Work、资产、用户 Skill 与请求不迁移。

一次命令解析配置一次，Preview/render 固定本次输入；更新前通过已有进程管理停止相关进程，以最小互斥防止启动和更新交错，不热换依赖。配置变更只影响后续命令，Agent 更新后重读根规则。

待安装 ZIP/staging 严格校验全部清单、hash 和路径；部署根只校验拥有的管理文件，保留合法用户文件和本地配置。更新先备份再覆盖管理文件；仍管理的文件有修改时拒绝覆盖。退出管理的文件未修改才删除，修改过的原字节保存到不会被发现为 Skill 的退役保留位置，记录原路径和摘要，更新可继续且回滚可恢复。未管理同名内容不覆盖，无法安全安置则报告冲突；不全根 mirror/delete。回滚会恢复原有用户修改并列出路径；这类根仍可能无法通过严格 `verify-root`，需处理修改后使用，不能把原包摘要改成用户文件摘要来绕过校验。

WSL 固定部署入口（执行即更新指定根，必须已有该目标的部署授权）：

```bash
./release deploy --root 'D:\AI\AI+hyperframes'
```

默认使用 `.studio/.runtime/windows-runtime-cache` 中锁定的依赖，缺失时报告而不联网安装。

Windows 入口固定本根的 `NODE_OPTIONS` 预加载器，通过锁定的 Koffi 按绝对路径加载包内 ONNX DLL，并由 Node 子进程继承；不沿用外部预加载配置，不修改系统 DLL 或 `PreferSystem32Images` 安全策略。
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

Windows 直接开发视觉内容和效果；仅宿主、CLI、合同、加载、seek 或依赖装配缺口交给 WSL。`work request freeze` / `export` 冻结最小复现，WSL 在私有副本修工具并交付安装候选，Windows 在 Review 验证；纯布局、图标或动作设计不走工具请求。完整参数见 [请求交接](.studio/workflow.md#复用与交接)。Review 不允许正式 Finalize、归档完成或保存平台草稿；模拟资产接纳仅留 Review，接纳交付不等于接受 Plan/Draft，不覆盖未受影响场景。

Windows 原生、交互 WebGL、抓帧 WebGL、视频硬件编码和真实复用分别验证。构建或 Linux 测试通过不表示 Windows 已部署或硬件路径通过。目标与验收边界见 [Windows 工作台 PRD](docs/PRD/hyperframes-windows-workbench-wsl-handoff.md)。

Windows 侧共享 ASR 由包内 `asr-wsl.cmd` 桥接到固定的 `Ubuntu` 和 `/home/jym/workspace/_external/scripts/asr.sh`；`HYPERFRAMES_ASR_SCRIPT` 仅可指定另一 Windows 入口。桥接器拒绝 WorkStore 外的输入和输出，并把路径转换、可用性检查和转录合并为唯一一次固定调用：

```text
wsl.exe --distribution Ubuntu --exec /bin/sh -c <fixed-script>
```

任务参数只经 `WSLENV` 传入，路径由 WSL 内的 `wslpath` 转换；stdout、stderr 和退出码原样返回。Windows Codex 沙盒已确认能复用 WSL ASR、模型和 GPU，但未持久授权时每次调用仍可能先报 `Wsl/Service/E_ACCESSDENIED` 并要求审批。Codex 规则只匹配 Agent 发起的顶层 argv，因此应持久批准包内 `asr-wsl.cmd transcribe-faster` 前缀；不得批准任意 `wsl.exe` 命令。

完整产品契约以 `.studio/` 和 `AGENTS.md` 为准。
