# 创作工作流

## 最小启动

用户在 Windows Codex App 打开 `D:\AI\AI+hyperframes`，新建对话下达任务。Agent 按需调用根目录 `work.cmd`，无需用户打开 CMD；入口直接运行已安装版本并读取本机配置，不创建或依赖 Harness session。`work.cmd doctor` 显示实际环境。旧 Review 流程仅在明确要求隔离测试时使用。WSL 只开发 Harness、宿主接线、CLI、合同和依赖装配，并在工具请求的私有复现副本中调试。Windows 在 Work-local 或已登记 AssetSource 开发视觉内容，包括 Scene、GSAP、Three.js、shader、SVG 与模型；不修改安装包、已接纳包、冻结 vendor 或 Snapshot。

前台交互运行 `./work current`；后台任务使用已分配的 Work ID 与 Variant ID 显式启动。读取 `WORK.md` 的 `workflow` 后再路由。`hyperframes_video` 只加载当前 Work、Variant、Script、一个 Recipe 和一套 Profile；Research 按当前部分 / Anchor 的呈现需求只读相关研究内容与素材依据，视觉阶段再读 Plan。`podcast_quote_image` 在文章方案批准前加载规划 Skill，批准后加载文案 Skill，且只读取当前阶段的机器产物。已有合格输入时跳过上游步骤。

## HyperFrames 视频

### 下载视频的文案分流

下载视频统一复用 `qivance-music` 的共享 WhisperX/FasterWhisper 运行时与 GPU 锁，不在本仓库复制模型或 ASR 实现：

```bash
/home/jym/workspace/_external/scripts/asr.sh transcribe-faster <video> --output-dir <work>/materials
```

命令必须同时生成 `*.transcript.json` 和 `*.transcript.md`。JSON 的 `characters[]` 是字级时间真源；`segments[]` 只用于快速阅读。存在口播但字级对齐失败时停止，不得以段级结果冒充完成。

转录完成后，在 `SCRIPT.md` frontmatter 中选择一种 `mode`：

- `dbs`：保留 `source.md` 原始基线，允许 DBS 多轮修改口播；正文变化时递增 Script Revision 并等待批准。
- `verbatim`：逐字保留转录口播、稳定 Anchor 和原时间戳；正文 `approval` 为 `not_required`，DBS 只可处理诊断或 `PACKAGE.md`，不得改写口播。

Script 可以来自用户写作或视频转录，负责本期及各部分讲什么，不要求用户先写视觉脚本或调研问题。已有文稿或可用转录但 `SCRIPT.md` 为空时，Agent 先按所选文案路径整理正文与 Anchor；整理不等于改写，不把全面查证作为建立 Script 的前置条件。没有可用内容才请求用户补充。

Script 就绪后，先用核心主题执行 `./work --work <id> --variant <variant-id> name "<核心主题>"`，再围绕各部分的视觉呈现需求完成同一 Variant 的 `RESEARCH.md`。Script Revision 变化只更新受影响条目和引用元数据，不默认刷新全片。

`SCRIPT.md` 的口播正文使用稳定 Anchor；简短 Scene 索引必须放在成对 `<!-- scene-index:start -->` / `<!-- scene-index:end -->` 内，只记录 `Scene | Anchor 范围 | 时间预算 | 本段内容 / 观众重点`。索引是规划输入，不是口播。需要纯文本、统计、配音或对齐输入时统一使用 `./work --work <id> --variant <variant-id> script text`；只有需要同时保留 Anchor 时增加 `--anchors`。旧 SCRIPT 没有索引时按原正文读取；如已有等效索引，只补成对标记，不强行重排内容。

### 视觉内容与素材准备

Research 为 Animation Plan 准备有来源、围绕本期内容组织的视觉内容与素材，不是第二份脚本。起点是“为了把这段讲述呈现清楚，需要什么具体内容或材料”，不是“口播哪里不完整或不准确”。即使口播完整，也可能需要真实界面、具体实例、过程与结果、图片、视频或数据；已有材料足够时复用并记录，无需新增研究，不强制每段配图或联网。

同一 `RESEARCH.md` 按 Script 内容部分与现有 Scene / Anchor 组织，按需记录“呈现需求、研究所得、素材依据、待补问题”。研究所得包含可用事实、解释、实例及必要的简短文字；素材依据说明材料中有什么可用内容，并定位来源页面、文件、区域或源时间点及必要使用条件。待补问题只写真实缺失或相关事实冲突，没有就省略。旧“资料依据 / 采用信息”及引用可保留，不批量改写历史 Work；未经用户确认的补充材料仍是候选，不因旧“核心”标记成为必上屏要求。

Research 的文字是可用表达，不是必须逐字上屏的稿件；材料被找到不代表已决定采用。Plan 结合 Script、研究材料与时间自主取舍，决定文字、素材和动作如何表达。Research 可以说明截图能展示什么，不决定构图、裁切、动画或成片时间；源视频证据时间点只定位素材。素材获取仍遵守既有授权，记录来源不冒充已取得可用文件。

优先一手资料，查证服务于拟采用的事实和材料；宣传、自述、概念示意与实际验证分开。发现与口播冲突时记录问题、依据与局部影响，交用户决定相关表达，不擅改原音、已批准观点或添加纠错画面，也不阻塞无关部分的研究。历史审阅意见标为历史，不与当前取舍并列为执行指令。

首轮完成的标准是主要呈现需求已有可用内容与可定位依据，真实待补项已说明，足以进入 Plan；不是全面查证完成或所有素材已经取得。Plan 发现具体材料需求时，只回到相应条目补研究并同步受影响引用，不重开全轮、不增加 Research 审批门；未取得素材按 Plan 现有占位与最终 Draft 就绪规则处理。

每个 Scene 先筛选有效主题信息，再保护完整表达。候选知识存在不等于必须上屏；“不伪造”“不泛化”等内部制作约束不改写成观众正文。删除无信息增量的重复，不迁移到下一状态、脚注、口播或另一组件。可选说明为空就不生成，不用默认空话填 Slot；真实来源、必要导航、原文对象和条件仍保留，不自动扩写免责声明或边界栏目。

逐字口播引用 Script Anchor。口播摘录加工成独立维护的信息文字时写入 Research 研究条目并注明口播来源，不因此联网。原视频 / 截图内文字归素材，清楚呈现时不重复覆盖。“步骤一”“输入”“结果”等无独立主张的表现标签直接写在工程；数据、比较、因果和“效率提升十倍”等独立主张必须有研究条目及其来源依据。Plan 引用这些来源，只用少量文字示例说明设计，不成为第二份信息稿或标签表。

同一主模型负责内容到画面。换行、层级、分组、出现顺序和表现标签直接在样段 / 工程调整；删除重复措辞、等义精简或改成流程短语时，同时原位更新 Research 研究条目及呈现，不重新联网、不生成阶段性交接或文字审批。等义以观众最终得到的结论不变为准；顺序变因果、比较对象变化、必要数值 / 单位 / 归属消失均为实质修改。

Research 补充文字与素材默认由 Plan 自主取舍，不采用无需逐条回传。新增数据、比较或因果只补查相关条目；只有取舍改变已确认观点、事实结论或叙事时，才提出局部建议和对 Scene / 时间的影响供用户确认。核心内容以 Script 和已批准 Plan 为准，不以 Research 候选标记为准；已批准视觉方向的实质变化仍按既有局部确认处理。确实无法同时保留已确认核心内容与时间预算时，直接给用户真实取舍，不要求 Research 反复压缩。

Research 标记为 `ready` 后，创建 Animation Plan 的同一步调用 DBS 完成 `PACKAGE.md`：使用 `dbs-xhs-title` 生成候选并选择 Top 1，再根据最终 Script 与 Research 写一条封面文字、一句话简介和内容概括。内容概括按主要对象或主题简短分项；介绍多个 Skill、工具、功能或案例时逐项单独说明。文档只保留这四项最终结果，不附公式分析或候选清单，也不新增审批门。

进入 Animation Plan 时加载 `hyperframes-anti-ppt`，按当前内容来源、时间依据、Recipe、Profile、Subtemplate 与画幅检查结论是否被正确表达、需要阅读的文字是否可读以及动效关系，不要求逐字逐卡摆放，不套用统一状态公式。结果合并进同一份 `ANIMATION_PLAN.md`，不新增审批产物。组件的检索、版本、Slots 与安装由视频工作流或组件库能力负责。

通过现有 `component` 能力从已配置的外部资产来源检索，以资产元数据和接纳记录为准；旧 `.studio/components/**/COMPONENT.md` 仅作只读兼容来源，身份冲突不静默覆盖。按 Scene 关系、真实文字及可选说明、素材形态、画幅、可用时间和状态变化核对适配；名字相近或能换标题不算适配。模块 / 媒体读匹配的 `asset.json` 与声明的用法 / 样例，旧组件读 `COMPONENT.md`、必要 `cases/**/CASE.md` 和边界 Fixture，Case 不扩大公共合同。已适配或能通过合同内组合 / 参数解决的能力直接复用，不重做审批样段。语义简报、精确版本、Binding 与必要差异保留在 Plan 原有资产列，不新建数据库。

安装前运行 `./work component validate <component-id>@vN`，用显式 Work/Variant 和 Binding 文件运行 `./work --work <id> --variant <variant-id> component install <component-id>@vN --binding-file <binding.json>`；Plan 批准前增加 `--purpose plan`，仍要求 Script / Research 就绪与资产合格。`component verify` 校验当前 Work 的 vendor、Scene Bindings 和 `COMPONENT_LOCK.json`，不因无关库更新或来源暂不可访问让已有闭合副本失效。库级接纳固定准确版本、依赖、目标画幅及兼容条件；`migration-ready` 不是生产批准，不批量改状态或复用旧 hash。优先验证当前需要的资产，旧家族 / 全画幅清单只作 backlog，不阻塞单个兼容包。

module/media 使用 Binding schema 3 的 `component_ref`、`scene` 和 `usage`（role / required，可选 fit / focal_point），布局和动作留 Scene，不填旧 Slots。`component pack <source-directory>` 从 `asset.json` 冻结候选；独立样例在已登记 AssetSource 内用 `component install ... --project <sample>` 与 `component verify --project <sample>`，不注册伪 Work。实际文件仍复制到 `vendor/components/<id>/vN`，Lock schema 2 的 `components[]` 用 `asset_kind` 标记类型，旧 schema 1 兼容。

优先复用能独立解释一个含义的语义视觉对象及其内部联动，由 Work-local Scene 安排本期叙事和媒体。已有 helper 保留，只有真实独立变化或复用需求才抽取，不强制图形/动作/布局工厂拆分。Windows 在已有 AssetSource 或 Work-local 开发；旧完整 Scene/组件保留兼容，空间舞台可内聚保存相机、遮挡和光照。布局适配须实测可读性，不以模块数量或双画幅完成率验收。

兼容新资产通过自身元数据发现，不改全局枚举或重发 Harness。官方 Registry 的 block / snippet 只在明确选中后导入候选，完成本项目接线与接纳才可使用，不向上游发送私有文案或缺口。Work 用既有 vendor / Binding / Lock 固定副本与依赖；不读 WSL 活跃源码、不链接 `latest`，同身份版本不同内容拒绝覆盖。没有匹配实现时记录 `custom:<slug>` 并在 Windows Work-local 实现，不覆盖冻结 vendor；仅工具或宿主缺口交 WSL。M1 只支持实际交付的 module/media 子集，其他资产类型不冒用 Component 合同。

### 整片 Plan 与一个参考 Scene

保留本地 M2–M3 画面、源文件、稳定 Scene/Anchor ID、音频、对齐和旧快照。从当前可编辑版本修订整片 `ANIMATION_PLAN.md`，不回退公开 HEAD，不重跑已完成阶段。先在现有任务记录核对所选 Work、已有成果和真实工具缺口；内容编排和视觉代码留 Windows。

Plan 覆盖全片：逐 Scene 的内容引用、A/B 叙事职责、语义对象、关系、真实媒体或稳定占位 ID、时间依据和 cue 意图。A-roll 承担主叙事与核心信息，B-roll 提供必要的例子、细节、过程或证据；两者均可使用图片、视频、文字、图解或操作画面，不固定为“A=文字、B=图形”，也不等于渲染引擎或物理音轨。没有补充增量可不设 B，不强制轮换或同框，不能把 talking_head 人物布局施加所有 Scene；主声音通常贯穿切换且只播放一次。

每场在现有主表或按需局部说明中写清主画面为何承载核心信息；有 B 时说明补什么、何时进入、如何接回及保留什么。关键对象应有可辨认特征、核心关系、必要起止状态、焦点迁移和阅读安排；一行方向不足以执行时补该场，不用唯一参考的细化代替其他场景设计。先决定观众需要看见什么，再选媒体形态与实现；`custom:<slug>` 或全片通用图形条目不能替代对象设计，不以图片或 SVG 数量验收，也不无依据排除图片路线。素材取得仍遵守既有授权，选择图片不等于允许生成图片。

整片 Plan 后只选一个真实 Scene 做动态参考，优先复用现有画面，不另做与内容无关演示或多 Scene 拼接。展示真实文字、画幅、已有动作和素材入口；有音频便裁取对应片段，无最终音频标 provisional。其他 Scene 的技术试验可按风险进行，但不构成第二个参考审批。

用户一次确认本版 Plan 与该 Scene 展示的制作方向；不先单独停一次 Plan，再逐 Scene 请求开工。批准记录绑定实际 Plan revision、准确预览版本、Scene 和方向用途。配色、字体及适配行为可共享；局部布局和叙事顺序不自动推广全片。方向批准不能写成完整 Draft 的接受，也不放行 Finalize。

方向批准后立即按各 Scene 方案扩成全片占位 Draft。全部计划 Scene、A/B 编排、已实现动作与阅读安排必须存在；允许 Plan 登记的图片/真人视频/模型等 planned placeholders、临时音轨和明确约定 proxy，不允许借占位掩盖代码错误、空 Scene 或缺失观点。有独立身份或替换需求的素材在 Plan 原有素材栏登记稳定 ID、内容依据、外观与构图、必要动作接口及起止状态、取得方式和完成判据；普通装饰原语不逐项登记。占位允许文件未取得，不允许用“后面做图”代替设计，不伪造真实媒体路径。只检查当前实际使用资源，不对计划占位下载、probe 或要求文件 hash。

完整占位 Draft 提供全片可审范围和待补位置，不增加强制批准门。素材就绪后按同一 ID 替换，保留无关 Scene、已确认语义及 cue；必需素材、最终音频和效果就绪后生成最终 Draft，沿用现有整片接受、Final QA 和归档。可选项可明确取消，方向和事实改变只确认受影响部分。

复用现有 preview ID/版本记录区分展示范围、准备度和接受用途；旧 `kind=reference` 仍表示不可播放的资产引用，旧 layout/executable/Accepted Snapshot 不改写为新含义。新命令和参数以实际部署的帮助为准，不把目标 schema 写成已存在 API。

日常工程、单 Scene 动态参考和登记版本默认通过 Work CLI 启动锁定官方 HyperFrames Studio；返回实际启动的项目 URL，不把源码 `index.html` 标成预览入口，不硬编码端口或猜地址。当前制作打开可编辑工程；登记版本导出独立审阅副本后打开，不用 hardlink / symlink 暴露 Accepted Snapshot、vendor 或外部资产。副本修改不自动成为当前 Work 或旧批准版本。自制审阅页只保留显式历史查看，不静默 fallback；本机官方接入受限时说明限制，由用户选择临时替代。

`preview open` 默认等同 `preview open current`；`preview open <plan-id|draft-id>` 审阅指定版本，`--legacy` 才打开历史自制页面。`preview context [target] --fields selection,lint --detail compact` 读取已启动的准确工程上下文，确需详细样式才改 `full`；`preview stop [target]` 只停止该目标的预览进程。

默认 Studio 浏览器使用 Work 返回的隔离 `browser_profile`，通过真实 Chrome Do Not Track 设置关闭官方遥测，不改用户主 profile。Agent 使用 `--no-open` 自行自动化时也复用该 profile，并在导航前核对 DNT；CLI 环境变量不等于浏览器前端已经停用遥测。

根目录 Windows 入口从自身位置和 `.studio/.runtime/` 配置解析本次命令的 HF 路径，普通运行不下载最新版或升级依赖。底层 `--hyperframes-dist` / `--hyperframes-cli` 仅用于运行时诊断。定位时核对锁定版本实际支持的 `preview --context --json`，绑定准确 Work / Variant、工程和实际端口；先取 Scene ID、源文件、composition、时间及必要 selection / lint，确需样式才取 full。多个实例不随意选择，缺对象时不猜。

Studio 编辑后按既有来源关联重建受影响 MP4、截图和 QA，旧证据不冒充当前源码。内容字段同步回 Script / Research 的唯一选稿位置，或暂停该字段再生成；不让生成器覆盖用户修正，也不将 HTML 变成第二套文案库。

用户批准方向后，Draft 逐 Scene 读取 Plan、Binding 和实际资产，保留角色、连接、条件、分支、反馈与结果，不压成通用文字行或以静帧替代已承诺动作。普通实现和纠错不重复审批，主构图或语义实质变化才局部确认。只有素材齐备的 full Draft 能获得完整接受与 Final 权限；单 Scene 和 planned-placeholder Draft 不行。`preview render <draft-id> --output <final.mp4> --final` 从适用的 Accepted Draft 渲染；原快照保留。

音频优先复用已有 timestamps 与 `section_map.json`。Binding 只记 Anchor、字符范围/明确 occurrence、对象事件和必要偏移；重复词不得全片模糊匹配，未对齐字符不捏造均匀时间。源片段按 `timeline_in + (source_time - source_in) / rate` 映射，边界半开，删除词无有效 cue，多 take 必须明确。单 Scene 裁取只减预览起点，不改原对齐；到输出 fps 时才量化。关键画面和音轨按目标时间重建，不依赖 seek/onComplete 回调；音乐分析按 hash/参数可选离线缓存，没有 BGM 或 Blender 不阻塞正常制作。检查真实声音锚点、工程映射、命中前后帧和带声短片，未试听明确记录。

三类时间分开维护：SCRIPT Scene 索引只给规划预算；正式音频与 `section_map.json` 保存实测时间；工程时间线决定画面实际出现与持续。`verbatim` 可用字级转录证据聚合的原时间戳作规划依据，源视频或音频仍是实测权威；`dbs` 没有正式音频时才估算。Plan 只记时间依据、必要阅读顺序和节奏意图，不复制精确时间表。

## Windows 与 WSL 请求交接

Windows 负责整片 Plan、唯一 Scene 动态参考及获批后的全片制作，继续开发 GSAP、Three.js、shader 与语义对象；只有加载、seek、合同、打包器、依赖或安装器等真实工具缺口才形成 `REQUEST.md`，包含准确版本、预期/实际行为、冻结最小复现、保留项和验收输入。已能从 Work 获取的信息不重复询问，不收回内容设计或增加需求批准门。

Windows 用明确 Work/Variant 冻结请求；`--file` 是允许改变的工程相对路径，`--context-file` 是只读复现输入。源码来自当前工程或指定 `--preview` 快照：

```bash
./work --work <id> --variant <id> request freeze seek-001 --brief <REQUEST.md> --scene S01 --file compositions/S01.html --context-file index.html --preview plan-v001
./work request export <requests/seek-001/r001> --output <WSL私有复现目录>
# WSL 修复工具并另行构建 Harness candidate；以下保留旧的最小复现补丁交付入口
./work request deliver <冻结revision目录> candidate-001 --source <patch目录>
# Windows 收到交付后，在原 WorkStore 创建隔离 Review
./work request review <原revision目录> --delivery <交付目录>
./work request feedback <原revision目录> --delivery <交付目录> --note "核对 S01 冷启动 seek 与顺序播放一致"
# 仅在用户明确接纳后，由 Windows 应用准确交付
./work --work <原id> --variant <原id> request accept <原revision目录> --delivery <交付目录>
```

`review` 返回隔离 WorkStore；候选根须另有独立 `.studio/.runtime/` 配置、AssetStore 和必要 source-copy，不能只凭 Work 路径声明隔离。直接根入口读取本次配置，无 session；Review 不改生产 Current、源、接纳记录或默认配置，不允许正式 Finalize、归档完成或平台草稿。请求反馈归属准确 revision/交付，不用 WSL 录像代替 Windows 原生执行。

旧组件交付的 `deliver --component <package> --binding <binding.json>` 和 `--approved-component <批准包>` 保留兼容，不作为新视觉资产的默认开发路径。Work-local 内容不必公共化；兼容资产由 Windows 源打包接纳，工具修复走 Harness candidate。`accept` 校验来源与变更范围，不等于 Plan/Draft 接受；其他 Work、未受影响 Scene、原 Accepted Snapshot 与 Final 不自动升级或覆盖。WSL 输出工具交付和技术结果，Windows 维护请求、内容与接受决定，不双写同一状态。

## Talking-head

```text
下载/内容输入 -> 选择 dbs 或 verbatim -> 必要时批准 Script
-> RESEARCH.md -> 逐 Scene 筛选与资产匹配 -> 整片 Animation Plan + 唯一动态 Scene 参考
-> 一次方向批准 -> 优先复用已有音频与 section_map -> 完整占位 Draft
-> 补齐必需素材与正式音频，必要时局部重定时 -> 素材齐备最终 Draft
-> 接受 Draft -> Final QA + 60fps high render -> Finalize -> 自动归档
```

## Pure HyperFrames

`verbatim` 下载视频沿用原字级时间；已有正式音频直接复用，其他输入才估算 provisional 时间。先整片 Plan、唯一动态参考和方向批准，再扩成完整占位 Draft。正式音频就绪后局部重定时，素材齐备最终 Draft 才作为完整接受基线，不以无声占位版冒充最终音画验收。

已有正式配音时沿用媒体依据规划，Draft 以 `section_map.json` 对齐；没有音频可估算。不得仅为查看布局强制配音、ASR、长音频同步或视频导出。

## 检查点

1. DBS 修改口播正文时批准 `SCRIPT.md`。
2. `RESEARCH.md` 标记为 `ready`，主要呈现需求已有可用内容与可定位依据，真实待补项已说明，足以进入 Plan；设计中可定点补研究。Revision 变化只同步受影响范围。
3. 创建 Animation Plan 时同步用 DBS 完成 `PACKAGE.md` 的标题、封面文字、一句话简介和内容概括。
4. Plan 用 `hyperframes-anti-ppt` 检查整片语义与一个真实 Scene 动态参考；静态旧样段不冒充动态通过，结果只进入现有 Plan。
5. 一次方向批准绑定 Plan revision 和唯一 Scene 参考，然后直接扩片；planned placeholders 不阻塞全片预览，不增加占位 Draft 接受门。
6. 完整 Draft 在官方 Studio 用 `hyperframes-anti-ppt` 复审实际关系、运动和阅读；占位版本明确缺口，素材齐备最终 Draft 才进入原完整接受。
7. Final 前接受准确 full、素材齐备的 Draft；单 Scene 方向或占位版本不能代替。

技术 QA、时间微调、换行、easing、性能优化和归档不要求用户批准。

局部反馈可用 `preview diff <id> --scene S02 --range 18.2 23.5 --note "保留正文，只改焦点迁移"` 记录到当前 Variant 的 `.runtime/feedback.json`；不带 `--note` 只读比较。时间范围仅适用于实际时间线，静态样段用 Scene 和对象定位，Scene 可重复指定。从新增样段开始在现有 Work 备注记录可取得的输入/输出 token（含缓存原口径）、Windows 与 WSL 的 Plan 及总制作投入、布局/动效返工，等待用户时间单列；缺失统计如实标明，不用代码行数代替 token，不以技术夹具宣称成本下降。

反馈定位到预演/Draft 版本、Scene、必要时间范围或对象。`preview diff <id>` 查看当前工程相对该快照的源码差异；只改受影响 Scene 与必要衔接。普通等义修改完成 Research / 工程更新和 Revision 同步后，由主模型确认口播、Anchor 与已批准 Plan 的视觉正文未变；Plan 只允许 frontmatter 的 `status`、`visual_plan`、`revision`、`script_revision`、`research_revision` 变化。随后使用 `preview diff <accepted-plan-id> --scene S02 --note "等义修改依据与局部影响" --compatible` 记录适用性。机器校验明确 Scene、冻结 / 当前输入与工程哈希，不猜自然语言；旧记录缺冻结来源时保留原流程，实际范围不符或后续再修改时不能沿用兼容记录。

`--compatible` 只沿用 Accepted Plan 进入一个新 Draft，避免未受影响内容被全片重做；它不把当前文件伪装成旧 Accepted Draft 已批准。Accepted Draft 的来源内容或 Revision 变化时必须注册并接受新 Draft，只有上述 Plan 纯状态 / `visual_plan` 元数据变化不使其失效。主构图、隐喻、视觉目标或核心内容变化仍只确认变更部分；未受影响源码、冻结资产、原 Accepted Draft 与 Final 不覆盖，新 Draft / Final 继续走现有来源与接受检查。正式配音接入优先调整阅读停留，再处理可变动作与衔接，不默认整场 `timeScale`，不截断音频或删必要信息。总投入、方向性返工、实际影响范围和有效复用可记入现有 Work 备注；没有真实交付证据时不宣称返工下降。

## 播客金句图

```text
来源 URL -> trendradar-media -> 校验并复制到 materials/
本地或已下载视频 + 可选原生转录/字幕 -> resolve transcript
-> 保留创建时的三位序号，只补充嘉宾名 + 核心主题
-> 规划 Skill 通读原文并生成 3 个完整文章方案
-> DBS 检查核心机制、受众情绪与传播理由 -> 用户批准 1 个方案
-> 文案 Skill 调研嘉宾背景并完成 RESEARCH.md
-> 先写开篇、每图小标题与第三人称正文，调用 dbs-content 诊断并按结果修订
-> 正文稳定后调用 dbs-xhs-title 生成可追溯公式的大标题候选并选定 Top 1
-> 调用 dbs-ai-check 诊断完整成稿
-> align time -> 每条 Hero/支撑句抽取 3 张候选帧 -> Agent 选帧
-> 从视频帧图片底部向上裁切并绘制紧凑双语字幕，render 8 至 12 张图
-> 生成小红书标题、纯文本正文、话题与有序图片清单
-> Agent 视觉 QA -> Finalize -> 自动归档 -> 经明确授权可保存到创作者平台草稿箱
```

字幕在覆盖区间内拥有文案和时间权威，转录只补无字幕区间；同语种明显冲突必须先人工处理。转录条件缺失或失败时进入 `waiting_user`，由用户决定是否改用保留原画面字幕的 fallback，不得静默降级。

每个文章方案包含 8 至 12 个按原文结构排列的图片组，每组固定 1 条 Hero，并用若干约 10 个汉字的完整支撑短句推进内容；中文总字数以 60 至 90 字为目标区间，不设逐句硬上限。同一内容可按语义拆成相邻两张图，图片只保留核心结论与必要论证，背景、案例和完整推导写入 `PACKAGE.md`。图片边界跟随原文的铺垫、观点、论证、例子、对比与收束，不按标点机械切分。用户批准 1 个文章方案是唯一内容门；批准后不得重新解释原文或另提方向。`RESEARCH.md` 只调研与获批核心相关的嘉宾身份、经历、背景故事和事实边界。全部面板绘制 50px 中文与 30px 英文；支撑条按双语文本实测高度分配并最多保留 30px 画面，Hero 至少占 60%，必要时把水平边距从 6% 收到最低 3%。Hero 与支撑字幕黑底 alpha 分别为 145 和 165。各面板从选定视频帧图片底部向上裁切，字幕条之间无间隙，整图至少保留 40% 无字幕空间。`PACKAGE.md` 直接使用可复制的纯文本：第一行为标题，其后为开篇、`01｜小标题` 形式的分节、正文、署名、`原视频：<视频原标题>` 和标签；render 只负责分离标题、正文、1 至 3 个话题和有序图片，正文连同话题不超过 1000 字。只有用户对准确 Work/Variant 明确授权后，才可用已登录浏览器保存草稿；不点击发布。

候选阶段用 `dbs-resonate` 检查每个方案是否只服务一个核心机制；`dbs-spread` 只提供受众情绪、有效立场和第一传播者信号，用于候选理由与排序，不改写原文。文案阶段不得把读取 Skill 或默认借用规则当成调用：先完成不含平台大标题的开篇、每图小标题与正文草稿，再单独调用 `dbs-content` 输出针对表达效率、认知落差和小标题的具体修订诊断，由文案 Skill 应用诊断；正文与小标题稳定后，单独调用 `dbs-xhs-title` 仅根据获批文段生成 5 至 8 个候选，覆盖至少 3 类公式、标注公式编号并给出 Top 3，再选定不超过 20 字的 Top 1。嘉宾背景不得作为大标题前提，除非它本就存在于获批文段且对含义必不可少。最后单独调用必做的 `dbs-ai-check` 诊断完整成稿。`dbs-content` 只诊断，不代写；修订仍由文案 Skill 完成。`dbs-hook` 与 `dbs-script-flow` 不进入本工作流。

URL 获取只调用外部 `trendradar-media` v2.0。适配器只接受成功 envelope 与单条成功 manifest，复核大小和 SHA-256 后原子复制到 `materials/source-video.*`，并保存不含外部临时路径的 `materials/acquisition.json`。YouTube 可先采用带结构化时间戳的原生转录；不可用时才在用户明确同意后调用共享 ASR。下载器本身不提供转录。

## 状态

Variant 只使用 `active`、`waiting_user`、`waiting_asset`、`parked`。具体阶段由文件、`wait_for` 和 `next_action` 推导；归档由目录位置表达。
