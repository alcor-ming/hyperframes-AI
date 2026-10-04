# HyperFrames v3.7：流程优化与复盘

状态：v3.7.0 最终规划已批准（2026-10-02），已在 WSL 开发仓实现并完成隔离验证；Windows 原生、宿主指定模型看图和生产验收未执行；v3.7.1 已按审查补定实施 R1–R9（2026-10-04），WSL 隔离验证已通过；Windows 原生、宿主模型看图与生产验收未执行；v3.7.2 待讨论；简化设计在 v3.8。本文件是 v3.7 大版本的产品真源；Trellis 任务 `hyperframes-v37-simplify-retro` 只绑定当前推进的小版本（文件名与任务 ID 沿用最初的"simplify"，不改名以免断链，简化设计已移到 v3.8）。

## 1. 背景与目标

v3.3–v3.6 逐步加入了事件表、节奏闭环、模式豁免、Opus 交接、数学链路等规则，单片的人工确认次数和 token 消耗都偏高，同一组例外分散在多份文档里。复盘也已经成为生产中占比很大的一部分，但目前只有 showcase 的提炼模板，没有画面复盘和数据复盘。

参考：

- 观默《用 Codex 自动生成顶尖动效视频》（2026-09-30）：导演层 Brief、减少自由度、参考先行、逐帧检查页。
- [motion-video-kit](https://github.com/echris6/motion-video-kit)：Brief → 参考机制 → 分镜表 → 组件打样 → Gauntlet（制作者不给自己打分、新评审逐项核对、能测就测、评审 ledger）。

v3.7 的目标有两个：

1. **流程优化**：把"Plan 里声明"换成"成片测量 + 独立评审"，A/B 交接错相，所有 token 与人工确认开销做成可开关的设置，为后续 Web 前端做准备。v3.7.0 总体是净增的：目标是成本可见可控、质量可测量，而不是减少步骤或 token；只有被档案取代的重复豁免段落会删除。
2. **复盘**：建立 Work 画面复盘（产出资产新增与优化）和 Work 内容复盘（结合抖音数据）。

简化设计（合并流程、减少步骤与 token）放到 v3.8，以 v3.7 的 ledger、设置生效值和新旧流程对照为依据。

## 2. 小版本切分

| 版本 | 主题 | 主要内容 | 依赖 |
|---|---|---|---|
| v3.7.0 | 流程优化与成本开关（只取观默文章与 MVK 中的做法） | 产品线档案（入口分流）；导演 Brief + 按 A/B 段的分镜表 Plan；取消事件表、节奏改为测量（第 2–4 层静止）；A/B 错相交接；视觉延续测量；参考机制库；评审轮次命令与 ledger；独立评审可切换且必须能看图；三层设置 | — |
| v3.7.1 | 画面复盘 | 单片 `retro/<Draft ID>/VISUAL.md`（找问题 + 找优秀，提炼扩展到全模式）；样片记忆（生产根样片库、两层参考机制库、Brief 引用与 critic 对照）；已知缺陷（负面记忆）；跨片汇总（手写重复 → 资产候选与 Asset Brief，反复缺陷 → 规则/诊断提案，资产使用频率机械统计）；修正数学积木两处诊断缺陷。A/B 交接效果与 card 跨 Scene 精确延续已移出，由复盘提案立项 | v3.7.0 的 ledger 与评审包 |
| v3.7.2 | 内容复盘 | 抖音 xlsx 导入；API 接入；逐秒留存对齐 Script Anchor / Scene / 画面事件；账号基线对比；回流到选题、Script 开头与 Plan | v3.7.0 设置；v3.7.1 可选 |
| v3.8 | 简化设计 | 待讨论；依据 v3.7 的 ledger、设置生效值与新旧流程对照决定合并或删除哪些步骤 | v3.7 |

## 3. 已确认决定

| 日期 | 决定 |
|---|---|
| 2026-10-01 | v3.7 是大版本；先讨论并锁定 v3.7.0 的边界，再逐个推进小版本。 |
| 2026-10-01 | 接受取消 Plan 逐 Scene 事件表，改为成片测量 + 独立评审。 |
| 2026-10-01 | 整轮改动围绕成本与质量均衡。成本分两类：token 与人工确认；两类都要做成可开关，为后续 Web 前端做准备。 |
| 2026-10-01 | 独立评审可切换。项目默认是 Codex 中的子 Agent；用户自己的部署默认使用 DeepSeek Flash。 |
| 2026-10-01 | 抖音数据做两类接入：导出 xlsx 后读取，以及 API。 |
| 2026-10-01 | 用户能拿到逐秒留存的 xlsx 数据。 |
| 2026-10-01 | Plan 方向批准（含唯一参考 Scene）可由设置关闭；关闭后直接进入 Draft，方向随完整 Draft 接受一并确认。dbs 改正文批准与完整 Draft 接受保持固定，不进入设置。 |
| 2026-10-01 | v3.7.0 作为中小版本，只做能追溯到观默文章与 MVK 的改动；与两者无关的内部整理（规则文档"核心 + 模式差异"重组）移出本版。 |
| 2026-10-01 | 参考机制库放入 v3.7.0：Brief 引用 1–3 个参考机制；种子条目用自己的话改写 MVK launch-film notes（MIT，仅保留原片链接），也可来自用户提供的链接或带时间点的帧；awesome-ai-motion 只给链接，不抓取不入库。从复盘向库里补充机制留在 v3.7.1。 |
| 2026-10-01 | Brief 字段按模式区分：card 必填核心表达、主体/次主体、禁止项，参考机制可选；explainer（含 math-rap）填全部字段；showcase 沿用 `SHOWCASE_PLAN`。入口分流要做成正式设计，因为本项目的主要工作就是应对多种视频类型。 |
| 2026-10-01 | 设置分三层：档案默认值 → 用户设置（根）→ Variant 设置，后者覆盖前者。档案在 Variant 创建时冻结；开关类设置不冻结，每条命令读取当时生效值，只影响后续命令；每轮评审在 ledger 记录实际生效的设置。 |
| 2026-10-01 | critic 必须能看图；不支持图像输入的模型不能被设为 critic，不提供纯文本降级。用户确认最新 DeepSeek Flash 支持图像输入。 |
| 2026-10-01 | A/B 交接在 v3.7.0 由"同一 cue 瞬切"改为运行时错相交接（S9）：只随新版冻结运行时进入新工程，旧工程保留瞬切；Brief 不设交接风格字段，个别 B 段可声明硬切例外。 |
| 2026-10-01 | 分镜表按 A/B 段写：一个 A → B → A 的 Scene 写三行（如 `S01·A1`、`S01·B1`、`S01·A2`），无 B 的 Scene 一行；主体列可空，空则取档案按 A/B 角色给出的默认值。v3.7.0 不从分镜表生成宿主 A/B 接线。 |
| 2026-10-01 | 视觉延续做"声明 + 测量"：分镜表写延续对象，工程在交界两侧对象上标同一 `data-hf-carry` ID，`preview diagnose` 在交界前一帧与起点帧报告位置与尺寸偏差（只报告）；评审包附每个交界的前后两帧。运行时精确交接与 card 卡片内对象的延续不在 v3.7.0。 |
| 2026-10-02 | 档案默认值：card 方向批准关、critic 关；explainer 与 explainer/math-rap 方向批准开、critic 为 `codex-subagent`、最多 1 轮（到上限后仍可手动继续）；showcase/pdoom、showcase/science 方向批准开（现行）、critic 关（Opus 在 WSL 制作，宿主不是 Codex）。用户层可覆盖，用户部署在用户层把 critic 模型设为 DeepSeek Flash。 |
| 2026-10-02 | v3.7.0 范围不砍。v3.7 当前优先完善流程优化与复盘两个功能，目标表述改为"成本可见可控、质量可测量"；简化设计放到 v3.8。v3.7.0 实施后在生产用同一份 Script 按新旧流程各做一个 test-work，比较 Plan 字数、人工确认次数与 critic 问题数，作为 v3.8 的输入；该对照属于生产观察，不进开发验收。 |
| 2026-10-02 | 用户批准 v3.7.0 最终规划（第 4 节、Trellis 任务 `hyperframes-v37-simplify-retro` 的 REQ-001–011 与 AC1–AC9）；实施交由 Codex 在 WSL 开发仓完成。 |
| 2026-10-02 | v3.7.1 画面复盘分两类：找问题（缺陷归因到制作执行、规则、诊断、资产能力等层，并给出系统去向）与找优秀（可复用资产、做法，乃至整片留作样片）。 |
| 2026-10-02 | 样片用途限于两项：作为制作 Agent 的参考（Brief 可引用），以及作为 critic 的对照基准。作品集留存和工具升级回归不是样片的目标。 |
| 2026-10-02 | "优秀"只由用户标记；Agent 与 critic 不提名。 |
| 2026-10-02 | 找问题复盘由用户指定发起，通常在多片段返工或 Final 后整片异常时进行；不设自动触发。 |
| 2026-10-02 | 样片以整片为单位，用户在片内标记若干好段，每段写明为什么好。 |
| 2026-10-02 | critic 只对照 Brief 引用的样片段。样片的检索、引用与对照按 agent memory 来设计，作为 v3.7.1 的设计重点。 |
| 2026-10-02 | 生产中两类复盘优先由生产根 Opus 执行，Codex 作为回退。 |
| 2026-10-02 | Final 后发现的整片异常，通常是 Draft 阶段就已存在、用户审查时遗漏的问题，不单独设计 Final 与预览的对比证据。复盘证据仍取自已接受的 Draft 快照，归因层包含"用户审查遗漏"。 |
| 2026-10-02 | 做负面记忆：找问题复盘中用户确认的缺陷模式作为"已知缺陷"加入该产品线的 critic 检查项；规则或诊断能自动拦住后退役。 |
| 2026-10-02 | 样片段由 Agent 在写 Plan 时从索引中挑选，用户可修改。索引条目由用户与 Agent 对话创建：用户指明段与理由，Agent 起草条目，用户确认后写入。样片段作为可引用的机制条目。 |
| 2026-10-02 | 索引默认只列本产品线的样片段，允许显式跨产品线引用。 |
| 2026-10-02 | A/B 交接效果（wipe/push/glitch）与时序调优、card 跨 Scene 精确延续移出 v3.7.1，等复盘提出需要后单独立项；v3.7.1 只做复盘机制本身。 |
| 2026-10-02 | 跨片汇总保留资产使用频率，只做机械统计、不做判断，作为后续开发参考。 |
| 2026-10-02 | 两处已知工具缺陷纳入 v3.7.1：数学积木事件计入节奏诊断；`math_trailing_gap` 改为按 Scene 检查。 |
| 2026-10-04 | 用户批准 v3.7.1 范围（第 5 节，R1–R9 与 AC1–AC10，含 5.6 中由 Agent 补定的模板取代、跨线标记、showcase 可选参考行、设置默认值与复盘写权限）；Trellis 任务 `hyperframes-v37-simplify-retro` 改绑 v3.7.1。 |

## 4. v3.7.0 边界

实施记录（2026-10-02）：S1–S10 当前范围已落地。新 Variant 使用冻结 line、三层设置及 3.7.0 Plan（showcase 保留专用 Plan）；旧 Variant 不迁移。新增 `settings show|set|unset`、`critic round|record`，critic 只生成证据并记录建议，由宿主按生效设置派生能看图的 Agent。错相运行时、像素静止和 carry 几何测量已通过隔离 Chromium 与本机缓存 Studio 0.8.80 验证；Studio 交界帧使用实际预览协议帧率，无法确认时明确标未测量。锁定运行时 0.8.27 的原生验证、Windows、指定 critic 模型与生产新旧流程对照仍未执行。未部署或改动生产内容。

### 4.1 规划时的现状证据

- Plan 逐 Scene 事件表由 `.studio/visual_plan.py:287-294` 解析（`cue | 层 | 目标 | 变化` 与 `例外` 行），卡片块事件由 `.studio/visual_plan.py:262-268` 自动推导。
- `preview diagnose`（`.studio/work.py:3798`）用 `.studio/visual_diagnostics.py:26` 的 `rhythm_diagnostics` 计算第 2–4 层的实际可见事件；Plan 声明的事件只用来核对目标是否命中（`.studio/visual_diagnostics.py:102-121`），不产生事件。
- Draft 冻结与审阅分为 `preview register` / `open` / `accept`（`.studio/work.py:3778-3790`），评审包由 `.studio/review_bundle.py` 单独生成。
- 根配置 `.studio/.runtime/local.json` 已经有 `review` 布尔值，含义是**隔离候选 Review 根**（`.studio/windows_runtime.py:117-135`）。新的独立评审不能复用 `review` 这个名字，草案称为 `critic`。
- showcase / math-rap / card 的豁免同时写在 `.studio/workflow.md`、`.studio/spec/visual-design.md` 与 Router SKILL 中。

### 4.2 范围

每项标注来源，便于判断是否超出本版。

- **S1 Plan 改为"导演 Brief + 分镜表"**（文章 01/03/04–09；MVK Brief 与 Storyboard）：新 `plan_format`。Brief 写主体/次主体与层次、错相、运动语言（预备 → 冲击 → 回稳）、物理、光、节拍与声音、禁止项、验收标准；分镜表一行一个 A/B 段：起点口播词 / 观众看到什么 / 本段任务 / 主体（可空，取档案默认）/ 交接例外与延续。卡片块与 `screen` 文字保留在对应 Scene 下。在制 Work 继续使用旧格式，解析器两种格式都读，不自动转换。
- **S2 节奏改为测量**（MVK frozen-time 与"无动作停留不超过约 0.6s"；文章"关键物体别冻死"）：新格式不再需要事件表，只声明刻意停顿（例外行）。`preview diagnose` 保留运行时可见事件，并加入第 2–4 层像素静止时长：截图时隐藏第 1 层与第 5 层（背景漂移和字幕推进不计入节奏），作用是补上 DOM 事件检测看不到的 canvas、WebGL、视频画面冻结（来自 Studio 帧采样，不导出视频）。截图时同样隐藏 DOM 事件检测已排除的持续动作（`data-hf-ambient`、IP 待机/说话 `data-hf-motion="idle|talk"`，`.studio/visual_probe.mjs:72`），否则 IP 角色的呼吸会让第 2–4 层永远测不出静止；持续镜头运动区间与 `talking_head` 例外区间标为未测量，不报静止。
- **S4 评审轮次命令**（MVK Gauntlet 与 ledger；文章逐帧检查页）：一个命令完成冻结准确 Draft、诊断、contact sheet、逐帧查看页、每个 Scene 交界的前后两帧、每个 Scene 起点与每次 A/B 交接附近的帧条（约 −0.2、−0.1、0、+0.1、+0.2、+0.4 秒），以及测量，并追加一条 ledger。帧条用于让 critic 在不导出视频的前提下看到时间上的错相与交接。用户接受仍然针对准确 Draft。
- **S5 独立评审（critic）可切换**（MVK"制作者不给自己打分"与 critic prompts）：提供方可选关闭、Codex 子 Agent（项目默认，模型可配置，用户部署为 DeepSeek Flash）等。评审只读评审包，不读制作过程；下一轮逐项给出 FIXED / PARTLY / STILL。
- **S7 参考机制库**（文章 10；MVK References）：仓库内小型机制目录，每条写机制、适用模式、迁移方式与原片链接；Brief 按 ID 引用。
- **S8 入口分流（产品线档案）**（用户要求，支撑 S1/S5/S6 按类型生效）：一份声明式档案表，以 `mode` + 子模块/系列规格为键（`card`、`explainer`、`explainer/math-rap`、`showcase/pdoom`、`showcase/science`），每个档案声明：制作模型、Plan 模板与 Brief 必填/可选字段、各阶段加载的规则文件、测量阈值、critic 检查项、本版开关的默认值、可用资产范围（只用冻结库 / 允许 Opus 主镜头）。Router SKILL 与 CLI 都从档案读取，删去 Router、`workflow.md`、`visual-design.md` 里重复的模式豁免段落，改为引用档案。`talking_head` 仍是叠加在 card/explainer 上的 Template，不单列档案；`podcast_quote_image` 是独立工作流，不进档案表。Variant 创建时冻结档案 ID 与版本，旧 Variant 按现行规则运行，不静默迁移。
- **S9 A/B 错相交接**（文章"错相、同一时刻一个主事件"；MVK"交接点不能整屏同时换"）：`rolls.js` 把进入 B 的三件事拆开：B 媒体提前起步并在 B 段起点 cue 落定，A 组随后退场或虚化，B 文字再晚一步出现；返回 A 时反序：B 文字先退，A 组在返回 cue 恢复，B 媒体最后淡出。时序为固定常量，随冻结运行时版本走，不进 Brief、不进设置；减少动态（reduced motion）与 B 段硬切例外保持瞬切。seek 与回拖结果只由时间决定。旧工程已冻结的 `rolls.js` 不变，因此继续瞬切。
- **S10 视觉延续测量**（MVK"被延续对象末帧 = 下一场首帧"，冻结时间测量；文章"一形贯穿"）：分镜表"延续"列写延续对象；工程在交界两侧的对象上标同一 `data-hf-carry="<ID>"`；`preview diagnose` 在交界前一帧与起点帧读取两者的位置与尺寸，报告偏差，只报告不设门禁。card 自动生成的卡片块不加标记，card 线延续仍靠 A 文字组拉回。
- **S6 设置清单**（用户要求，服务于上述开关）：只收录本版引入的开关——方向批准开关、critic 提供方/模型/最多轮数等。声明式清单（键、类型、档案默认值、可覆盖层级、阶段、成本类型 token/人工、说明），三层合并后输出每个键的生效值与来源层，CLI 可读写并输出 JSON，供日后 Web 前端直接使用。

### 4.3 规划时的补充现状证据

- Variant 已有 `profile` 字段，含义是视觉风格（`.studio/work.py:71` `PROFILES`），产品线档案不能复用这个名字，改称 `line`。CLI 也已有 `work review`（隔离测试 WorkStore，`.studio/work.py:3617`），再次确认独立评审命名为 `critic`。
- `plan_scene_rows` 只接受 `plan_format` 3.5.2，其余一律报错（`.studio/visual_plan.py:211-219`）；新格式需要并行解析，而不是替换。
- Draft 接受前要求 Plan `status=approved`（`.studio/work.py:2105-2106`）；Plan 接受写回 `status=approved`（`.studio/work.py:2413-2419`）。方向批准关闭时，需由 Draft 接受一并批准同一 Plan revision。
- `visual_probe.mjs` 已用 Puppeteer 按 `--step` 逐点 seek 并等待帧就绪（`.studio/visual_probe.mjs:432-470`），可在同一采样点取像素截图，不需要导出视频。
- 现有 `review_bundle.py` 只服务 math-rap（要求 `beat_grid`，`.studio/review_bundle.py:41-42`），不作为通用评审包复用。

### 4.4 文章设计与现行流程对照

| 文章设计 | 现行流程 | 判断 |
|---|---|---|
| 导演层 Brief：主体/次主体、轨迹、物理、光、声、禁止项、验收 | Plan「全片方向」只写概念、叙事弧、比喻、呼应、背景情绪弧、声音签名（`ANIMATION_PLAN.template.md`「全片方向」节） | **替换**：全片方向改为 Brief，原有概念/叙事弧/比喻作为 Brief 首段保留 |
| 删掉自由度：极少颜色、同一形状连续变形、禁止全体同动作 | 规则约束的是流程（A1、阅读保护、2 秒），审美约束只有冻结 Theme | **新增**：Brief 的禁止项与限制 |
| 分镜：每镜一个主任务，起势 → 发展 → 收束 | 概览表（一句摘要）+ 逐 Scene 一句概括与 A/B 编排 | **替换**：概览表与逐 Scene 概括合并为分镜表；A/B、card 块、`screen` 保留 |
| 主次与前中后景 | 五层（background/stage/overlay/text/captions）按功能分层，不表达注意力主次 | **保留五层**，分镜表增加「主体 / 次主体」列 |
| 错相、同一时刻一个主事件，所有层共用一个进度 = PPT 感 | 只有「相邻事件 ≤ 2 秒」与禁止「铺开再等」 | **新增**：A/B 交接由运行时错相（S9）；其余同步点写入 Brief 与 critic 检查项，不做 CLI 判定 |
| 运动语言：预备 → 冲击 → 回稳、动量连续 | 无；easing 自由 | **新增**：Brief 字段（主要影响 explainer 自制镜头与资产制作） |
| 物理、光、关键物体别冻死 | 无物理/光要求；节奏只数事件 | **新增**：Brief 字段；「别冻死」并入 S2 静止时长测量 |
| 先建拍点网格再做动画 | 时间依据是正式口播 Anchor 与字词对齐 | **保留现行**：口播 Anchor 就是本项目的拍点网格 |
| SFX 打在接触帧、微偏移、从运动长出 | 声音层 7 条已要求音效对应同帧可见事件、hit offset 预卷 | **基本已覆盖**，仅补「微偏移」允许 |
| 参考先行 | 只有「唯一参考 Scene」（本片自己的样段） | **新增** S7 参考机制库；唯一参考 Scene 随方向批准开关 |
| 逐帧检查 HTML 页 | Studio seek、`review_bundle.py` contact sheet、`preview diagnose` | **合并**进 S4 评审轮次 |
| 「懒得想就让 Codex 补全 Brief，你再审核」 | 方向批准 | 与已定的方向批准开关一致 |
| 代码量越多细节越多 | card 复用冻结资产 | **不采用** |

### 4.5 流程综合分析：导演层 × 五层 × A/B × Scene 拉回

**两套体系各管什么**

| 体系 | 回答的问题 | 现状 |
|---|---|---|
| 五层 | 同一时刻谁叠在谁上面、谁能遮挡谁 | 合同完整（`.studio/spec/visual-design.md` 五层分工） |
| A/B-roll | 一段时间里谁占主画面 | `.studio/runtime/rolls.js` 实现；B 期间 A 的时间暂停 |
| Scene 拉回（跨 Scene 返回 A） | 返回 A 时恢复什么 | 已读条目直接就位、A 时间续接（`.studio/runtime/rolls.js:44`、`:50`）；Plan「延续信息」只引用信息 ID（`.studio/visual_plan.py:305-308`） |
| 节奏合同 | 多久必须有一次有效变化 | 相邻有效事件 ≤ 2 秒，DOM 事件检测 |
| 文章导演层 | 观众先看哪、每个时刻谁是主事件、怎么动、怎么接 | 缺 |

项目已经管住了"结构与可读"，缺的是"注意力与交接"。

**逐项对位**

1. **主体/次主体/背景不是某一层，而随 A/B 段变化**：

   | 段 | 主体 | 次主体 | 背景化 |
   |---|---|---|---|
   | card A | 第 4 层卡片文字 | 第 2 层卡内图标/简图 | 第 1 层 |
   | explainer A | 第 2 层动态图解或第 4 层文字（按段） | IP 角色（反应）、第 3 层指示 | 第 1 层 |
   | talking_head A | 第 2 层真人 | 第 4 层短标题 | 第 1 层 |
   | 任意 B | 第 2 层媒体 | 第 4 层 B 文字组、第 3 层指示 | 虚化的 A 文字组 |

   第 5 层字幕永远不是主体；第 3 层永远是次级响应。主次默认值可由档案按 A/B 角色给出，Plan 只写偏离（例如 B 媒体里该看哪一处）。
2. **前中后景**：第 1/2/3 层已对应远/中/前景，第 1 层流动已存在且不计事件。补一条：冲击传到环境时，第 1 层响应更晚、更弱。
3. **错相**：节奏合同只管密度、不管相位。最明显的同步点是 A/B 交接：`rolls.js` 在同一 cue 把 A 组隐藏或 `blur(8px)`、同时显示 B 媒体和 B 文字（`.studio/runtime/rolls.js:81-84`），节奏事件 `b_enter`/`a_return` 也全部记在同一时刻（`.studio/runtime/rolls.js:54-60`）；Motion 已有 transition 绑定（`.studio/spec/hyperframes-assets.md:85-92`），但 A/B 交接没有接入，Plan 也没有地方写交接方式。阅读保护期间第 2、3 层继续产生事件，按文章应定位为"次级响应"（跟随、幅度小），不与第 4 层抢主事件；IP 角色换姿势可作为对文字揭示的延迟回应。**已定**：A/B 交接改为运行时错相（S9）。Motion transition 绑定不直接复用：它让两个目标在同一 cue 同时变化，并独占两者的 opacity/visibility（`.studio/runtime/appearance.js:277-290`、`.studio/spec/hyperframes-assets.md` 属性所有权段），与错相和 `rolls.js` 自己写的 visibility/filter 冲突；wipe/push/glitch 风格的交接留给 v3.7.1 资产优化（后改为由复盘提案立项，见第 3 节 2026-10-02）。
4. **动量连续、一形贯穿 ↔ Scene 拉回**：项目的信息延续比文章更严格（已读不重播、A 时间续接）；缺的是视觉延续——MVK 要求被延续的对象在 A 场末帧和 B 场首帧位置一致，现行只延续信息 ID，第 2 层对象每个 Scene 重新开始。**已定**：声明 + 测量（S10），运行时精确交接留给 v3.7.1（后改为由复盘提案立项，见第 3 节 2026-10-02）。
5. **分镜 ↔ Scene + A/B 段**：Scene 由 Script 语义切分，一个 Scene 内的 A → B → A 实际是三个镜头；A → B → A 本身就是 起势（A 提出）→ 发展（B 证据）→ 收束（A 回收）。**已定**：分镜表按 A/B 段写，一段一行。
6. **节拍 ↔ 语义 cue**：主事件落在口播语义起点 cue；次级响应按文章"微偏移"略晚。
7. **物理与光**：card 的动作在冻结资产内（card-kit easeOut、Motion v3 back-out/spring），属于资产质量，交 v3.7.1 画面复盘；explainer 写入 Brief。
8. **风格**：项目在创建 Variant 时冻结外观，早于文章顺序。矩阵账号需要外观即身份，保留。
9. **检查**：静止测量必须分层，并隐藏持续动作，见 S2；critic 只能看静态帧，Scene 起点与 A/B 交接附近要给帧条（新格式已无事件表，没有可靠的主事件时间，不另设），见 S4。

**整合后的流程**

```
创建 Variant：冻结 line 档案 + 外观
→ 内容准备：Script / 录音 / 对齐（= 拍点网格）
→ Plan
   ① 导演 Brief（全片）：核心与弧线、主次偏离、禁止项、参考机制；explainer 加运动语言/物理/光
   ② 分镜表：A/B 段、观众看到什么、主体、本段任务、交接例外（硬切）与延续（信息 + 视觉对象）
   ③ Scene 内容节：card 块 / screen / 素材 Brief / 声音 / 例外（内容，不变）
→ 方向批准（可关闭）
→ Draft（A/B 交接由运行时自动错相）
→ 评审轮次：结构合同（CLI 校验）+ 测量（DOM 事件 + 第 2–4 层像素静止 + 延续偏差）+ critic（主次、单主事件、交接错相、延续、禁止项）
→ 用户接受完整 Draft → Final
```

### 4.6 不在 v3.7.0 范围

画面复盘、内容复盘、抖音数据接入、Web 前端本身、部署与生产验收；规则文档"核心 + 模式差异"全面重写（只删除被 S8 档案取代的豁免段落）；MVK 的音频混音与响度测量（本项目以正式人声为主）；AI 视频生成与 3D 组件实验页；A/B 交接的 wipe/push/glitch 效果与运行时精确延续（由复盘提案立项）；从分镜表生成宿主 A/B 接线；critic 纯文本降级与 CLI 直接调用外部模型。

## 5. v3.7.1 画面复盘

状态：R1–R9 已在 WSL 开发仓实施并通过隔离验证（2026-10-04）；Windows 原生、指定 critic 模型看图与生产验收未执行。已定事项见第 3 节 2026-10-02 各条；5.1–5.4 是设计，5.5–5.8 是现状证据、范围、验收与边界。

### 5.1 两类复盘

**找问题**

- 由用户指定发起，通常在多片段返工或 Final 后整片异常时进行。Final 后的异常按 Draft 阶段遗漏处理。
- 证据取自出问题的已登记或已接受 Draft 快照。
- 每条缺陷记录：
  - 现象，Scene 与时间；
  - 发现阶段：Plan / Draft 诊断 / critic / 用户审查 / Final 后；
  - 返工代价：单 Scene / 多片段 / 重做 Draft / 重置 Work；
  - 归因层：制作执行 / 规则 / 诊断 / 资产能力 / critic / 用户审查遗漏；
  - 去向：作品修复、规则提案、诊断提案、资产 Asset Brief、已知缺陷条目；不改系统的标"仅本片"。
- 系统去向以冻结最小复现交 WSL 开发仓，不携带作品内容。

**找优秀**

- 只由用户标记。
- 按四种粒度留存：
  - 整片 → 样片，片内标若干好段，每段写明为什么好；
  - 段或镜头 → 样片段条目（见 5.2）；
  - 组件或动作 → 资产候选，走 `asset-library/sources` → pack → 用户 accept；
  - 做法 → Plan 配方或规则提案。
- 沿用 `SHOWCASE_REFINEMENT.template.md` 的分类，扩展到全部模式。

**执行者**：生产根 Opus 优先，Codex 回退。

### 5.2 样片记忆

按 agent memory 设计：

- **写入**：用户与 Agent 对话创建。用户指明段与理由，Agent 起草条目，用户确认后写入。Agent 与 critic 不自行提名。
- **存放**：生产根，独立复制冻结快照引用和帧证据（复用 `critic round` 证据包：contact sheet、交界前后帧、A/B 帧条），不进开发仓与 Git。样片不需要视频。
- **索引**：每段一行，含 ID（如 `<样片ID>·S03·B1`）、产品线、A/B 角色、理由、缩略帧、制作时的工具与资产版本、状态。按产品线分文件。
- **检索**：Agent 写 Plan 时读本产品线索引，挑选样片段写入 Brief 的"参考机制"，用户可修改。默认只列本产品线，允许显式跨线引用。
- **注入**：只加载 Brief 引用段的帧证据；制作与 critic 看同一组，随 Plan revision 冻结。Draft 阶段不做隐式检索。
- **借鉴维度**：理由限定借鉴哪一点；critic 只评该维度是否达到，不评相似度。
- **机制库两层**：发行内置的 `.studio/mechanisms.yaml`，加生产根的用户层（样片段条目）。Brief 引用与 `plan check` 读合并结果，数量规则沿用 v3.7.0。
- **巩固**：多个样片段指向同一做法时提炼为机制、资产或规则。原段保留为证据，索引标"已巩固 → X"，检索优先提炼后的条目。
- **失效**：不自动过期。引用的样片早于已知行为变化（如 v3.7.0 错相交接）时，Plan 阶段提示；由用户退役。
- **成本**：单次最多引用段数、critic 每段帧数进入三层设置。

### 5.3 已知缺陷（负面记忆）

- 来源：找问题复盘中用户确认的缺陷模式，含"用户审查遗漏"类。
- 按产品线加入 critic 检查项，附描述与证据帧。
- 规则或诊断能自动拦住后退役，证据保留。

### 5.4 跨片汇总

- 手写重复 → 资产候选与 Asset Brief。
- 反复缺陷 → 规则或诊断提案（与 5.3 退役衔接）。
- 多个样片段同一做法 → 巩固（5.2）。
- 资产使用频率：机械统计，只计数不判断，作为后续开发参考。

### 5.5 规划时的现状证据

- 参考机制库只有发行内置一份：`.studio/mechanisms.yaml` 字段固定为 `id/mechanism/lines/transfer/source`，`source` 必须是 https 链接（`.studio/lines.py:48-52`）。Brief 引用只查这一份，跨产品线引用一律报 `mechanism_line_mismatch`（`.studio/director_plan.py:17-25`）。样片段条目需要用户层和新的来源形式。
- showcase 使用 `SHOWCASE_PLAN`，没有 Brief、参考机制字段，也没有 A/B 段；showcase 档案 critic 默认关。
- `critic round` 证据包已有 contact sheet、逐帧页、交界帧对与 A/B 帧条（`.studio/critic.py:63` 起），存于 Variant 的 `critic/`；ledger 每轮记录 Draft、快照 hash 与生效设置（`.studio/work.py:3584-3588`）。包内 `direction.json` 只含 Brief、分镜段与例外，没有参考帧。
- critic 检查项是档案里的固定列表（`.studio/lines.yaml` 的 `critic_checks`），没有用户层。
- 设置清单只有方向批准与 critic 共 4 个键（`.studio/settings.yaml`）。
- Variant 外观锁记录冻结的资产 closure（`ref`、`kind`、`package_sha256`、`version`、`vendor_path`，`.studio/appearance.py:132-134`），可直接做机械统计。
- 提炼只有 showcase 的 `SHOWCASE_REFINEMENT.template.md`（积木 / 动作配方或规则 / 内容资产 / 仅属于本片），由 `.studio/workflow.md:59`、`.studio/spec/showcase.md:11` 与根规则模板 `.studio/templates/CLAUDE.template.md` 引用。根规则把数学系列、card 单片与未列任务定为只读，复盘写入没有授权位置。
- work42"后半段静止"对应的三处缺口：
  - 积木揭示后只有 0.25 秒透明度渐入，只有 `edge`、`equals` 有位移，`keep` 不产生画面动作（`.studio/runtime/math-kit.js:121-127`）。这属于资产能力。
  - `math_reveal` / `math_remove` 不在节奏诊断允许的事件种类中（`.studio/visual_diagnostics.py:39-48`），数学 Scene 一律报整段无事件，真实的后半段空白被噪声淹没。这属于诊断。
  - `math_trailing_gap` 只检查全片末尾（`.studio/math_chain.py:149-150`）。这属于诊断。

### 5.6 范围

- **R1 单片复盘记录**：新模板 `VISUAL_RETRO.template.md` 覆盖全部模式，含找问题表（5.1 的字段）与找优秀表（四种粒度，保留 `SHOWCASE_REFINEMENT` 的四类）；它取代 `SHOWCASE_REFINEMENT`，原引用处改指新模板。`work --work <Work ID> --variant <Variant ID> retro open <Draft ID>` 在 Variant 下建 `retro/<Draft ID>/VISUAL.md`，绑定该 Draft 的快照 hash；证据复用该 Draft 已有的 critic 证据包，没有时按同一采样另生成一份，不写 critic ledger，不导出视频。`retro check` 只校验字段与枚举，不判断归因是否正确。系统去向以文字写在记录里，交 WSL 沿用"冻结最小复现"，本版不新增导出工具。
- **R2 样片库**：位于生产根，不进开发仓与 Git。`sample add` 从指定 Draft 快照与证据包独立复制该段帧证据（不用 hardlink / symlink），记录来源 Work / Variant / Draft、快照 hash，以及制作时的运行时与资产版本。索引按产品线分文件，每段一行（字段见 5.2）。段 ID 沿用分镜段（`<样片ID>·S03·B1`）；showcase 与旧格式 Plan 没有 A/B 段，按 Scene 标记（`<样片ID>·S03`）。`sample list` 默认只列本产品线，`--all-lines` 列全部；`sample show` 给出某段的帧与理由；`sample retire`、`sample consolidate --into <X>` 只改状态，不删证据。CLI 不设确认门禁，确认在对话中完成。
- **R3 两层机制库与 Brief 引用**：`plan check` 读取发行层与生产根用户层（样片段条目）的合并结果，数量规则沿用 v3.7.0。跨产品线引用须显式标记（如 `跨线:<ID>`），未标记仍报 `mechanism_line_mismatch`。引用已退役条目时报告；引用已巩固条目时提示改用提炼后的条目；样片早于发行内置"行为变化清单"中的某项变化时提示（清单首条为 v3.7.0 错相交接）。`SHOWCASE_PLAN` 概念节增加可选"参考机制"行，走同一检查。
- **R4 注入与 critic 对照**：Plan refresh 时按 revision 冻结引用段 ID、借鉴理由、有序帧副本及 hash、两个 samples 设置的生效值；引用或设置变化产生新 revision。Draft 登记继承这份冻结输入，不重新检索或选帧；制作 Agent 用 `sample show` 读同一组帧。`critic round` 证据包加入引用段的帧与理由（借鉴维度），帧数受设置限制；critic 对每个引用段只判该维度"达到 / 部分 / 未达"，不评相似度；ledger 记录引用 ID。发行层种子条目没有帧，只给文字。
- **R5 已知缺陷**：生产根按产品线存条目（描述、证据帧、来源复盘、状态）。`defect add|list|retire`；`critic round` 把本产品线的有效条目附在档案检查项之后，ledger 记录当轮生效的条目 ID。退役时写明拦住它的规则或诊断，证据保留。
- **R6 跨片汇总**：`retro summary` 只读扫描生产根，输出 JSON 与 Markdown 到生产根：
  - 资产使用频率：按资产与版本、产品线统计各 Variant 冻结 closure 的引用次数与最近使用时间；
  - 缺陷：按归因层、去向、产品线与已知缺陷 ID 聚合各 `VISUAL.md`；
  - 资产候选：汇总各记录中"组件或动作"一类；
  - 样片：各段被 Brief 引用的次数，同一机制下的样片段数（作为巩固线索）。

  "手写重复"由复盘执行者写在记录里，汇总只计数，不做跨 Work 代码比对。
- **R7 数学诊断修正**：`rhythm_diagnostics` 把 `math_reveal` / `math_remove` 计为可见事件，层由积木挂载目标决定（第 2 层或第 4 层）。`math_trailing_gap` 改为按 Scene 检查：每个 Scene 最后一个数学事件到 Scene 终点超过 2 秒即报告，并带 Scene ID。诊断不随 Variant 冻结，修正后对在制 Work 的后续诊断生效。同步修改 `.studio/spec/math-rap.md` 中"收尾"的表述。
- **R8 设置**：`settings.yaml` 新增 `samples.max_references`（单个 Plan 最多引用的样片段数，同时受参考机制总数上限约束，默认 3）与 `samples.frames_per_reference`（制作与 critic 每段读取的帧数，默认 6），用户层与 Variant 层可覆盖，成本类型 token。旧 Variant 缺键时补发行默认值，不重绑产品线；无 line 的旧 Variant 也允许覆盖 samples 两键，其他旧设置语义不变。
- **R9 规则与执行者**：`.studio/workflow.md` 增加复盘一节，Router SKILL 增加复盘入口。根规则模板 `CLAUDE.template.md` 与 `WINDOWS_AGENTS.md` 增加"复盘"任务：生产根 Opus 优先，Codex 回退；可写范围只限 `retro/`、样片库、已知缺陷库与 `retro-summary/`，不改 Work 源、Plan、Current 与接受记录；样片与已知缺陷条目在用户对话确认后写入。

### 5.7 验收

开发验收在 WSL 隔离 fixture 上完成；Windows 原生与生产验收分别报告。

- **AC1** `retro open` 在 fixture WorkStore 上生成绑定快照 hash 的 `VISUAL.md`；有 critic 包时复用，没有时另行采样且 ledger 不变；未登记的 Draft 报错；同一 Draft 重开保留用户填写内容，不同 Draft 互不覆盖；全程不产生视频文件。
- **AC2** `retro check` 对非法枚举与缺字段给出报告，合法记录无发现。
- **AC3** `sample add|list|show|retire|consolidate`：帧为独立副本（非符号链接、inode 不同）；索引按产品线分文件；默认只列本产品线；状态变化不删证据。
- **AC4** `plan check`：用户层 ID 可引用；未标记的跨线引用报 mismatch，标记后通过；退役、已巩固、早于行为变化各给出对应发现；showcase 的可选参考行走同一检查；发行层条目的现有行为不变。
- **AC5** Plan refresh 冻结引用 ID、理由、有序帧副本与 hash 及设置，Draft 登记继承，之后退役或巩固该条目不改变已登记 Draft 的 critic 包；critic 包含引用帧与理由，帧数符合冻结设置；ledger 记录引用 ID。制作读取 Plan 冻结帧，critic 读取 Draft 继承帧，逐帧 hash 相同；修改设置不会改变旧 Draft，仅 refresh 后的新 revision 生效；critic record 拒绝缺项、重复引用、未知引用或非法结论。
- **AC6** 已知缺陷出现在本产品线的 critic 包检查项中，其他产品线与已退役条目不出现；ledger 记录生效条目 ID。
- **AC7** `retro summary` 在含多个 Variant 的 fixture 上给出正确的资产引用计数、缺陷聚合与样片引用次数；运行前后 Work 文件 hash 不变；相同 Plan revision 的多轮 Draft 不重复计数，跨 revision 分开计数；缺失关联记未关联，不猜测。
- **AC8** 数学 fixture：有揭示事件的 Scene 不再报整段无事件；最后一个数学事件距 Scene 终点超过 2 秒、且尾段无其他可见事件与豁免区间的 Scene 同时报 `rhythm_gap` 与带 Scene ID 的 `math_trailing_gap`；未超过的 Scene 不报 math_trailing_gap。补充尾段有其他可见动作的反例：仍报数学空档，但不报整体节奏空档；无数学事件的数学 Scene 从 Scene 起点计空档，cue 越界报告而不计入事件。
- **AC9** `settings show` 列出两个新键的生效值与来源层；覆盖带旧 line 与无 line 的 Variant，验证默认 3/6、用户与 Variant 覆盖、正整数校验及 line 身份不变。
- **AC10** 规则文档、Router、两份根规则模板更新后通过现有包校验；测试只用 fixture，不读取生产内容。

### 审查后补定（2026-10-04，用户批准补齐并实施）

- 复盘问题表增加可空的 `已知缺陷 ID`；优秀表分别记录四种留存粒度与原 showcase 四类，不混为一个枚举，并增加可空的 `机制 ID` 与 `手写重复`。样片段索引含可空的 `mechanism_id`；巩固目标明确为机制、资产或规则，原段不删除。
- 汇总口径：资产按 `(Work, Variant, ref, version)` 对冻结 closure 去重计数，最近使用时间取 Variant 元数据时间，不用文件 mtime；样片引用按 `(Work, Variant, Plan revision, sample ID)` 去重（同 revision 多 Draft 只计一次），统计已冻结 Plan / Draft；机制聚合使用显式 mechanism_id。未知时间、缺失关联明确为 null / 未关联。汇总输出在生产根 `retro-summary/`，规则写范围包括此目录。
- Plan 引用帧冻结存于 Variant 的 `reference-memory/<revision>/`，制作使用 `sample show <ID> --plan-revision <N>`；Draft 内继承副本，不依赖之后的库状态。样片证据不足设置帧数时使用全部可用帧，不补造；超出时均匀取样并固定顺序。帧数与引用数均为正整数，引用数超限报告。card/showcase 的机制可选，不额外引入旧版本不存在的总数限制；explainer 仍 1–3。
- 缺少冻结引用的历史 Draft 不从当前库回填；其 critic 无样片对照并明确未冻结。复盘复用包需匹配 Draft、快照与文件 hash；无包时只从登记快照采样，证据输出到该 Draft 的 retro 目录，不写 critic ledger / Current / 接受记录。采样所需可回收 Studio 运行记录沿用工具现有机制。
- 样片/缺陷库采用生产根 `sample-library/`、`known-defects/`；CLI 必须显式 Work/Variant 或产品线，不从 Current 隐式取值。条目确认在对话完成，CLI 不追加批准门。索引状态与证据完整性分别校验，损坏证据不能默默用于评审。

### 5.8 不在 v3.7.1 范围

- A/B 交接的 wipe/push/glitch 效果与时序调优、card 跨 Scene 精确延续：等复盘提出需要后单独立项。
- 数学积木保持期的画面动作（资产能力缺口）：走复盘 → Asset Brief，按数学资产流程处理。
- 自动触发复盘、Agent 或 critic 提名样片、相似度评分、样片自动过期。
- 跨 Work 代码重复的自动检测。
- 任何视频导出：样片与复盘只用帧证据。
- 内容复盘与抖音数据（v3.7.2）、Web 前端、部署与生产验收。
