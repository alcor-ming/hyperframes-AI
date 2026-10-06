# 创作工作流与治理

环境、权限与运行边界只见根 [AGENTS.md](../AGENTS.md)。创作指南见 [visual-design.md](spec/visual-design.md)，来源与修订见 [creative.md](spec/creative.md)。本文件按需加载，维护生命周期与四阶段的人工判断；命令参数和合法状态以当前 CLI 帮助与错误信息为准。

## 对象与用途

先区分讨论、继续现有 Work/Variant、同内容目标的独立 Variant、临时实验和新生产目标。普通修订留在当前 Variant；同一期新账号适配建立独立 Variant；只有用户明确要求旧归档实体只读、另建同一期实体时使用继任。用途有实质歧义才询问，不从 URL、缺账号或缺 Final 推断实验。

账号属于 Variant；Work 级 Script/Research 由各 Variant 共享，各 Variant 独立维护 Plan、工程与接受结果。显式内容分支按 CLI 定位。新视频显式指定 `--purpose standard|ip|test`，生产用途指定系列；账号与制作版本可以稍后确定。独立输入为叙事模式、视觉主题、背景、画幅和可选 Motion；支持 `explainer`、`showcase`、`math` 与 `english`，默认 `explainer`，IP 继续推荐 `explainer`。Theme 负责字体、语义色与表面，不决定模式、布局或 cue；Variant 使用冻结外观。

产品线差异以冻结的 `line` ID/版本查 [.studio/lines.yaml](lines.yaml)：制作模型、Plan 模板、阶段规则、Brief 字段、主体默认值、资产范围与豁免只在那里维护；版本发布后保留既有档案版本，不能原地改变旧版本语义。旧 `explainer/math-rap` 及其他仍支持链路的冻结身份按原语义读取，不自动迁移。card 已移除制作与渲染支持，历史文件、接受快照与成片保留；继续内容须显式采用到受支持的新版本，不配送兼容实现。`talking_head` 是 Template。本版本只提供视频制作；已退役或未知 Work 不继续制作，也不阻断无关视频的定位。

非数学 explainer 的 Opus 主镜头按档案资产范围和获批 Asset Brief 交接，原有制作独占与用户接受边界保持；交接不改变 Current 或接受记录。WSL 开发与生产根按根规则区分，生产根通过 `work-wsl.sh` 调用 Windows CLI。

实验采用结果先复制或冻结到目标 Work；来源关系不等于接受。保留稳定 Scene/Anchor ID、正式声音、已有成果和冻结历史。更换主题、叙事结构或确认观点属于方向变化，只确认受影响部分。

## 1. 内容准备

复用合格 Script、录音、对齐与材料。Script 为空时先整理文稿/转录；`dbs` 只有实际修改正文才等待批准，`verbatim` 保留原文与原时间证据。用 `work script text` 排除 Scene 索引，避免重复 ASR。Script 稳定后通过 `work name` 补语义标题。

数学沿用原片声音与人工核对歌词；英语使用原创教学稿和公共 TTS。TTS 默认火山，可配置替代脚本；先生成候选，再明确采用正式声音，最后以可信原生时间证据或既有 ASR 完成字词对齐。未对齐处不估时，候选生成不等于声音采用或内容接受。正文或声音变化仅重做受影响的新制作范围，保留旧接受快照。

Research 按段落或 Anchor 记录事实与来源、B-roll 候选（可定位位置及取得状态）、比喻与例子。先理解完整段落，再定点补具体材料缺口；它不是另一份脚本或必上屏清单。事实冲突交用户判断相关表达，不擅改原音。共享输入变化只更新受影响研究及引用。

`PACKAGE.md` 仅按交付需求生成，**不是视频设计、制作或接受的前置**；新建版本不生成空包装占位，材料和运行目录在首次需要时创建。

## 2. 整片设计

Plan 模板与适用检查从冻结档案读取；形式豁免不扩大为接受豁免。
Plan 阶段按用途运行 `work component list --query <用途> --include-references` 查包、场景源与配方，按结果的 `detail.argv`（在本根 work 入口后传入参数）查看准确接口，再选择复用、派生或自制。单查场景源或配方可直接用 `--kind scene-source` / `--kind recipe`；裸 list 保留参考项默认隐藏的包目录行为。场景源与配方不可安装，按详情中的源入口或配方说明使用，不猜派生命令。组件可在 WSL 开发任务或 Windows 可编辑源编写；生产内容制作保持根规则边界。

通用 explainer 的新 `plan_format=3.7.0` 按 [创作指南](spec/visual-design.md) 填导演 Brief 与按 A/B 段的分镜表，每段一个观看任务。逐 Scene 保留 `screen`、素材、声音与刻意停顿例外，不再写事件表。showcase、math 与 english 使用专属 Plan，不强加通用 Brief、角色／生图或 A/B 配额；数学保留符号和图形职责，英语保留教学要素、回忆任务与阅读停顿。参考机制 ID 见 [机制目录](mechanisms.yaml)。正式声音与字词对齐仍是时间依据。CLI 冻结元信息，3.5.2 Plan 继续可读，不自动转换。拟生成素材列用途、数量、风格与 Asset Brief，权限只见根规则。

通过 `work settings show --json` 读取档案默认 → 用户 → Variant 的生效值和来源；`settings set|unset --layer user|variant` 修改后只影响后续命令。开关不冻结，每轮 critic 保存实际值。`direction_approval=true` 时完成 Plan 后制作唯一真实参考 Scene，按短自检单检查并由用户确认准确 Plan revision；关闭时直接进入完整 Draft，方向随该 Draft 接受一并确认。dbs 改正文批准和完整 Draft 接受不可关闭。

派工只传 Plan 路径、Scene ID、负责范围与写入边界，由执行者按引用读取同版全片方向和对应 Scene，不重复复制正文；不附加比 Plan 更严的禁止项，不可行时回报准确冲突。对应对象只加载已选资产接口卡与必要合同，不再派发全库研究。主模型负责内容结果。模型不产出模板之外的设计说明或自写检查脚本；检查使用 CLI 与诊断，Work 与工程中确需的文件不受影响。

## 3. Studio 制作与验收

是否要求 Q1 或节奏闭环由档案 exemptions 决定；ready、seek、离线闭包、授权和准确完整 Draft 接受始终保留。
完成当前方向批准设置要求后扩成全片 Draft。占位到素材齐备是同一阶段的准备度变化：用稳定 ID 补齐媒体，只重定时受影响范围，保持全部 Scene、A/B、动作与阅读安排。最终接受前正式声音与必需效果齐备。

使用 CLI 返回的锁定官方 Studio URL。登记版本在独立审阅副本打开；依照 [hyperframes.md](spec/hyperframes.md) 验证 ready、seek、闭包与技术 QA，按链路适用的观看检查带声连续观看。阅读区域稳定，节奏事件与声音对应；Windows 原生连续播放、暂停、任意 seek、回拖和跨 Scene 证据单独报告。

要求诊断闭环的链路在交付 Draft 前对准确版本运行 `preview diagnose`；showcase 按专属豁免处理。逐项处理适用的 `rhythm_gap` 与未验证区间：修正工程后重新诊断、在 Plan 写例外行并随对应方向或完整 Draft 接受确认，或在交付说明逐项解释原因。交付说明附诊断报告位置与未处理项；诊断只定位，不判通过、不替代观看，不新增审批门。默认读取摘要，确需完整结构时用 `--json`，不读取 `probe.json` 等原始采样。

`preview register` 冻结准确 Draft，`preview open <id>` 审阅，再由用户接受准确 full Draft。技术 PASS、素材 complete 与方向确认不替代这一决定。反馈绑定版本、Scene 与时间范围：信息缺口回 Plan，证据缺口回 Research，布局或实现问题就地修复；等义、换行、easing、安全区与性能修复无需重新批准方向。新增事实或改变原意回权威来源。工程文字同步逐 Scene 的实际 `screen` 表达。

`work --work <id> --variant <id> critic round [draft-id]` 复用登记、独立 Studio 审阅副本与诊断，一次生成准确 Draft 的截图、contact sheet、逐帧页、Scene 交界前后帧和 Scene/A/B 帧条，追加 Variant `critic/ledger.json`。不导出视频。省略 Draft ID 时先登记当前完整工程；失败不追加成功轮次。`--automatic` 在轮数上限停止；不带该参数可手动继续。

critic 提供方为 off 时仍生成证据和 ledger，不生成提示词。开启时宿主以 `critic.model` 派生支持图像输入的只读子 Agent，只读评审包并实际看 PNG；宿主不支持该模型或图像时报告未验证，不用纯文本替代。CLI 不调用模型 API。`critic record --file <verdict.json>` 校验准确轮次/快照、新问题和上一轮未解决问题的 FIXED / PARTLY / STILL；意见不阻止登记或接受。

## 4. Final 交付

生产 Variant 从准确 Accepted Draft 的闭合快照进入 Finalize，输出最终 MP4；test-work 不进入任何视频导出链。成功编码、QA、成片提升及收据完成后，归档准确 Variant；至少一个 Variant 且全部已归档时才自动归档 Work，零版本与部分归档不算整期完成。Finalize 不包含上传/发布。

编码 QA 检查规格、原音时长、全量解码、代表帧及必要听音；首次跨引擎输出核对构图、中文边缘、字体、颜色、透明合成与声音。失败不归档，保留复现及旧 Final。成片已成功而归档写入中断时，从同次收据恢复，不重复编码或增加历史条目。历史成片与当次 manifest 一起保存；旧散装 MP4 缺收据时标明历史来源未知，不猜配、不自动删除。

## 归档、恢复与停放

Work 是内容容器，各 Variant 平级；`required_variants` 不再作为第二套完成判据。取消归档用 `work reopen <Work-ID> --variant-id <Variant-ID>`，在原版本继续修改，保留上次导出和接受快照。重新激活或显式新增任一 Variant 后 Work 回到 active，其余版本保持原生命周期；多版本不隐式全部重开。已有继任链前身仍只读。

`work --work <Work-ID> archive --variant-id <Variant-ID>` 可手动收起未导出的版本，显示未导出，不冒充交付成功。归档和恢复保持物理路径稳定。`park` 只暂停 Work，`resume` 解除暂停；二者不搬目录、不改等待事项或兄弟版本的归档状态，已打开的 Studio 会话继续定位原路径。旧搬移布局只在能保持会话、Current 与原状态完整的兼容路径中处理。

`list` 默认展示 active（含 parked），`list --archived` 查看归档，`list --all` 查看全部；`list --tree` 与可重建的 `浏览目录.md` 使用同一展示数据。按标题、系列号、版本归档数、当前焦点及最近导出定位，工程与成片链接指向准确对象。查看归档不等于重新激活。

`work storage inspect` 按 Work 盘点空间，`work storage cleanup` 默认仅预览，加 `--apply` 才执行；均可用 `--work <Work-ID>` 限定目标。容量按需统计，无法读取时报告未知。回收只处理已证明归属、可重建、无引用且相关进程已停止的缓存；源、原媒体、接受快照、历史成片、未知内容及失败证据保留，归档本身不触发删除。

## 复用与交接

showcase 接受后使用 `VISUAL_RETRO.template.md` 记录积木、动作配方或规则、内容资产和仅属于本片四类。只提炼最小模块/接口/配方，不向其他线交整页代码；新可编辑 AssetSource 不引用 Work 路径，沿用 pack / validate / accept。规则提案交开发仓，开发会话不读取生产 Work。

同对象、同依赖的有效检查沿用；变化仅检查受影响 Scene 和必要衔接，共享宿主或时间线变化按依赖扩大。Studio 内容检查、编码 QA 和归档完整性各自报告。

Windows 制作 Work 内容；WSL 负责工具与开发计划内的组件。工具缺口通过准确 Work/Variant 的 `request freeze` 保存预期/实际行为、冻结最小复现、允许修改文件与只读上下文；`request export` 后在 WSL 私有副本复现，工具修复形成 Harness candidate。Windows 在独立候选根用 `request review` 验证准确交付，反馈绑定 revision；应用入口为 `request accept`，权限见根规则。交付不等于 Plan/Draft 接受，不自动升级其他 Work。程序、规则、WSL、Windows 原生与生产验收分别报告。

## 画面复盘与样片记忆

找问题由用户指定，优秀只由用户标记。生产根 Opus 优先、Codex 回退；复盘不修改作品源、Plan、Current 和接受记录。数学的复盘之外仍遵守原只读边界。只使用登记 Draft 快照与 PNG，不导出视频，不调用外部服务。

显式传 `--work <Work ID> --variant <Variant ID>` 后运行 `retro open <Draft ID>`；有匹配且 hash 完整的 critic 包时复制证据，否则加 `--hyperframes-cli` 和 `--browser` 从冻结快照采样，不写 critic ledger。记录在 `retro/<Draft ID>/VISUAL.md`，重开保留内容，不同 Draft 独立保存。`retro check <Draft ID>` 校验字段和枚举，不判断归因。

用户确认段和借鉴理由后，`sample add <样片ID> --draft <Draft ID> --segment S03·B1 --reason <借鉴维度> [--mechanism <机制ID>]` 独立复制帧；没有 A/B 段时使用 `S03`。每个样片 ID 表示一整片，可多次添加不同段。`sample list` 默认本产品线，`--all-lines` 列全库；也可显式 `--line <产品线>`。`sample show <完整段ID>` 读取证据；`sample retire <ID> --reason <理由>` 与 `sample consolidate <ID> --into mechanism:<ID>`（也支持 asset:/rule:）只改状态，不删证据。样片不自动过期。

制作时在 Brief（showcase 概念节）的 `**参考机制：**` 引用完整段 ID，跨线写 `跨线:<ID>`。`plan check` 读两层机制库，报告退役、巩固、已知行为变化提示；发行机制仍可引用。`plan refresh` 将有序帧、理由与 samples 设置冻结在 `reference-memory/<revision>/`，制作必须用 `sample show <ID> --plan-revision <N>` 看这组帧。引用或设置变动经 refresh 创建新 revision，Draft 继承独立副本；之后退役、巩固或设置变化不改变旧 Draft。禁止手改这些冻结文件。

`samples.max_references` 默认 3，`samples.frames_per_reference` 默认 6；用户层与 Variant 层可覆盖。旧 Variant 补默认值而不重绑档案，无 line 的旧 Variant 仅允许新增 samples 设置，不改旧开关语义。通用 explainer 总引用仍 1–3；showcase、math、english 按专属档案选用，不继承通用配额。每段帧不足时取全部，超过时均匀选取；不补造帧。

已知缺陷先在复盘问题行填写 `已知缺陷 ID`，用户确认后 `defect add <ID> --draft <Draft ID> --description <描述> --frame images/<帧>.png`（可重复 --frame）。`defect list` 默认本产品线；`defect retire <ID> --blocked-by <规则或诊断>` 保留证据。critic 只读本线有效缺陷，附在档案检查项后；每轮记录生效 ID。参考样片逐项评“达到 / 部分 / 未达”，按 reason 限定维度，不评相似度；`critic record` 拒绝遗漏、重复、未知引用和非法结论。

`retro summary` 只读扫描已登记 Work，写生产根 `retro-summary/summary.json` 与 `SUMMARY.md`，不改 Work。资产按 Work/Variant/ref/version 去重，时间取 Variant 元数据（未知为 null）；样片按 Work/Variant/Plan revision/ID 去重，同 revision 多 Draft 不重复计数。问题按显式缺陷 ID、归因层、去向和产品线聚合；样片按显式机制 ID 分组，缺失关联记未关联。手写重复由人填写，只计数，不比对跨片代码。资产候选、规则与诊断提案不自动接受或执行。

## 内容复盘

生产根 Opus 优先、Codex 回退。只写 Variant 的 `retro/content/`（含导入原件）和生产根 `content-summary/`，不改 Work 源、Plan、Current、接受记录。所有单片命令显式 `--work <ID> --variant <ID>`，不取 Current；以下命令位于同根 Work CLI。

1. `content link <发布 ID> --draft <登记 ID>` 或 `--final`，同时提供 `--file <已发布文件> --platform <平台> --title <标题> --cover-text <封面文字> --published-at <ISO 时间> --ratio <画幅>`。账号来自 Variant；未绑定时必填 `--account`。只计算发布文件 hash 与时长，不复制或导出视频。
2. 本期实验变量必填：重复 `--variable '开头写法=本期取值'`，其他用 `--variable '其他:说明=取值'`；可加 `--compare <同平台账号对照发布 ID>`。同 ID 有多条时用 `Work/Variant/发布ID` 消歧。没改动显式 `--no-variable`。重新 link 同 ID 保留修改历史；文件、来源、时长、时间表等身份改变须新 ID。
3. 可选 `--timings <JSON>` 提供冻结工程导出的 `[{scene,anchor,start,end,characters:[{char,start,end}]}]`；须包含有效 Script Anchor，区间不重叠，末端与片长误差不超过 1 秒。优先使用来源快照 `section_map.json`（相同 rows 或 `{sections,characters}`）；没有则未对齐，CLI 不解析工程脚本。字级数据缺失不推测口播。
4. `content import <发布 ID> --dir <五份 xlsx 目录> --cutoff YYYY-MM-DD [--stage long-tail|early]`，或重复五个 `--file`。原件独立复制，sha256 留档；分段末端与片长差超过 1 秒拒绝。长尾由用户判断；不传 stage 为未标，输出 daily 供判断。导入全部保留。
5. `content open <发布 ID> [--import <导入 ID>]` 默认最新导入，刷新 CONTENT.md 生成区并保留手填部分；`content check <发布 ID>` 校验字段与枚举。找优秀仅用户标记，已有样片机制负责登记。数学不能使用 Script 开头与衔接去向。
6. `content summary` 按平台、账号、片长分组，只计每条发布最新长尾导入；少于 5 条不报偏离；输出开头样本、选题与实验变量表。其他阶段列出但不计基线。

读数依次为观看时间、2 秒与 5 秒、封面点击、完播。条件平均观看时长已从视频起点计时，平均离开点不再加 5 秒；输出取整区间和假设。无留存曲线，跳过 / 回看不等于离开；缺来源记未列出，不记 0。API 仅接口，无网络调用。原件、记录和汇总仅留生产根，不进开发仓与 Git。
