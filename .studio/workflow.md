# 创作工作流与治理

环境、权限与运行边界只见根 [AGENTS.md](../AGENTS.md)。创作指南见 [visual-design.md](spec/visual-design.md)，来源与修订见 [creative.md](spec/creative.md)。本文件按需加载，维护生命周期与四阶段的人工判断；命令参数和合法状态以当前 CLI 帮助与错误信息为准。

## 对象与用途

先区分讨论、继续现有 Work/Variant、同内容目标的独立 Variant、临时实验和新生产目标。普通修订留在当前 Variant；同一期新账号适配建立独立 Variant；只有用户明确要求旧归档实体只读、另建同一期实体时使用继任。用途有实质歧义才询问，不从 URL、缺账号或缺 Final 推断实验。

账号属于 Variant；Work 级 Script/Research 由各 Variant 共享，各 Variant 独立维护 Plan、工程与接受结果。显式内容分支按 CLI 定位。新视频显式指定 `--purpose standard|ip|test`，生产用途指定系列；账号与制作版本可以稍后确定。独立输入为叙事模式、视觉主题、背景、画幅和可选 Motion；默认 `card`，IP 推荐 `explainer`。Theme 负责字体、语义色与表面，不决定模式、布局或 cue；Variant 使用冻结外观。

模式另有 `showcase`，仅 Opus 5.5 制作，Codex 不接；创建时显式冻结 `pdoom` / `science` 子模块，见 [showcase.md](spec/showcase.md)。WSL 开发仓与 Claude 生产根会话按根规则区分；生产根通过 `work-wsl.sh` 调用已部署 Windows CLI，文稿和工程源仍可在授权 Work 内直接编辑，不另起 Studio 或渲染器。`explainer` 可采用系列规格 `math-rap`，创建 Variant 时冻结规格与系列版本；数学图解替代 D14 角色/生图要求，歌词字幕保持开启，见 [math-rap.md](spec/math-rap.md)。

card 和数学单片只复用已冻结库资产，不调用 Opus；card 的风格 Motion / B-roll 可选、无配额。非数学 explainer 可在 Plan 列出 1–2 个 Opus 主镜头和 Asset Brief；方向批准后，Codex 停止该 Work/Variant 的写入，生产根 Claude 会话按根 `CLAUDE.md` 独占制作指定 Scene，交回后 Codex 续接。主镜头遵守完整 explainer 检查，不自动批准 Plan/Draft，不直接入通用库；接受后再另行提炼。交接不改变 Current 或接受记录，不新增交接 CLI。

实验采用结果先复制或冻结到目标 Work；来源关系不等于接受。保留稳定 Scene/Anchor ID、正式声音、已有成果和冻结历史。更换主题、叙事结构或确认观点属于方向变化，只确认受影响部分。

## 1. 内容准备

复用合格 Script、录音、对齐与材料。Script 为空时先整理文稿/转录；`dbs` 只有实际修改正文才等待批准，`verbatim` 保留原文与原时间证据。用 `work script text` 排除 Scene 索引，避免重复 ASR。Script 稳定后通过 `work name` 补语义标题。

Research 按段落或 Anchor 记录事实与来源、B-roll 候选（可定位位置及取得状态）、比喻与例子。先理解完整段落，再定点补具体材料缺口；它不是另一份脚本或必上屏清单。事实冲突交用户判断相关表达，不擅改原音。共享输入变化只更新受影响研究及引用。

`PACKAGE.md` 仅按交付需求生成，**不是视频设计、制作或接受的前置**；播客包装沿用自己的合同。

## 2. 整片设计

本节默认表达合同适用于 card / explainer。showcase 使用 `SHOWCASE_PLAN.template.md` 的概念、逐 Scene 要点、素材与声音、未验证项和作者审计元信息，不要求 explainer 正向方向、D14、五层或事件表；保留准确 Plan revision 的用户确认，不将形式豁免扩大为接受豁免。

Plan 阶段按用途运行 `work component list --query <用途>` 查包、场景源与配方，再选择复用、派生或自制。场景源与配方只作派生参考。组件可在 WSL 开发任务或 Windows 可编辑源编写；生产内容制作保持根规则边界。

按 [创作指南](spec/visual-design.md) 写全片方向与逐 Scene 一节：一句概括、A/B 编排、`card` 块、独立文字的 `screen` 块与 `cue | 层 | 目标 | 变化` 事件表；素材与声音仅在有内容时出现。积木 cue 不重复写入事件表。概览只作索引。元信息及 `plan_format` 由 CLI 生成，旧格式不自动转换；正式声音与字词对齐是时间依据，不另抄精确秒表。拟生成素材列用途、数量、风格与 Asset Brief，权限只见根规则。

完成全片 Plan 后只做一个真实 Scene 动态参考，使用真实文字、画幅、动作及已有音频；缺正式音频标 provisional。一次方向确认覆盖准确 Plan revision 与参考 Scene；方向确认不等于完整 Draft 接受。按短自检单检查，实质变化局部确认。

派工只传 Plan 路径、Scene ID、负责范围与写入边界，由执行者按引用读取同版全片方向和对应 Scene，不重复复制正文；不附加比 Plan 更严的禁止项，不可行时回报准确冲突。对应对象只加载已选资产接口卡与必要合同，不再派发全库研究。主模型负责内容结果。模型不产出模板之外的设计说明或自写检查脚本；检查使用 CLI 与诊断，Work 与工程中确需的文件不受影响。

## 3. Studio 制作与验收

showcase 保留 ready、seek、离线闭包和授权等硬约束，以及准确 full Draft 的用户接受；不适用下文 Q1 活力自检或 Draft 前节奏诊断必经闭环。`preview diagnose` 可用且只报告，不强制处理节奏疑点。math-rap 仍按 explainer 流程核对实际歌词、数学关系与收尾事件。

方向确认后扩成全片 Draft。占位到素材齐备是同一阶段的准备度变化：用稳定 ID 补齐媒体，只重定时受影响范围，保持全部 Scene、A/B、动作与阅读安排。最终接受前正式声音与必需效果齐备。

使用 CLI 返回的锁定官方 Studio URL。登记版本在独立审阅副本打开；依照 [hyperframes.md](spec/hyperframes.md) 验证 ready、seek、闭包与技术 QA，按创作指南 Q1 带声连续观看。阅读区域稳定，节奏事件与声音对应；Windows 原生连续播放、暂停、任意 seek、回拖和跨 Scene 证据单独报告。

交付 Draft 前对准确版本运行 `preview diagnose`。逐项处理每个 `rhythm_gap` 与未验证区间：修正工程后重新诊断、在 Plan 事件表写例外行并随方向确认批准，或在交付说明逐项解释原因。交付说明附诊断报告位置与未处理项；诊断只定位，不判通过、不替代观看，不新增审批门。默认读取摘要，确需完整结构时用 `--json`，不读取 `probe.json` 等原始采样。

`preview register` 冻结准确 Draft，`preview open <id>` 审阅，再由用户接受准确 full Draft。技术 PASS、素材 complete 与方向确认不替代这一决定。反馈绑定版本、Scene 与时间范围：信息缺口回 Plan，证据缺口回 Research，布局或实现问题就地修复；等义、换行、easing、安全区与性能修复无需重新批准方向。新增事实或改变原意回权威来源。工程文字同步逐 Scene 的实际 `screen` 表达。

## 4. Final 交付

生产 Variant 从准确 Accepted Draft 的闭合快照进入 Finalize，输出最终 MP4；test-work 不进入任何视频导出链。交付集合以本期明确目标为准，单个 Final 不代表整期完成。Finalize 不包含上传/发布，也不自动归档。

编码 QA 检查规格、原音时长、全量解码、代表帧及必要听音；首次跨引擎输出核对构图、中文边缘、字体、颜色、透明合成与声音。失败保留复现及旧 Final。软归档独立于接受与交付，保留文件及依赖。

## 复用与交接

showcase 接受后使用 `SHOWCASE_REFINEMENT.template.md` 记录积木、动作配方或规则、内容资产和仅属于本片四类。只提炼最小模块/接口/配方，不向其他线交整页代码；新可编辑 AssetSource 不引用 Work 路径，沿用 pack / validate / accept。规则提案交开发仓，开发会话不读取生产 Work。

同对象、同依赖的有效检查沿用；变化仅检查受影响 Scene 和必要衔接，共享宿主或时间线变化按依赖扩大。Studio 内容检查、编码 QA 和归档完整性各自报告。

Windows 制作 Work 内容；WSL 负责工具与开发计划内的组件。工具缺口通过准确 Work/Variant 的 `request freeze` 保存预期/实际行为、冻结最小复现、允许修改文件与只读上下文；`request export` 后在 WSL 私有副本复现，工具修复形成 Harness candidate。Windows 在独立候选根用 `request review` 验证准确交付，反馈绑定 revision；应用入口为 `request accept`，权限见根规则。交付不等于 Plan/Draft 接受，不自动升级其他 Work。程序、规则、WSL、Windows 原生与生产验收分别报告。

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
-> Agent 视觉 QA -> Finalize -> 按需独立归档
```

字幕在覆盖区间内拥有文案和时间权威，转录只补无字幕区间；同语种明显冲突必须先人工处理。转录条件缺失或失败时进入 `waiting_user`，由用户决定是否改用保留原画面字幕的 fallback，不得静默降级。

每个文章方案包含 8 至 12 个按原文结构排列的图片组，每组固定 1 条 Hero，并用若干约 10 个汉字的完整支撑短句推进内容；中文总字数以 60 至 90 字为目标区间，不设逐句硬上限。同一内容可按语义拆成相邻两张图，图片只保留核心结论与必要论证，背景、案例和完整推导写入 `PACKAGE.md`。图片边界跟随原文的铺垫、观点、论证、例子、对比与收束，不按标点机械切分。用户批准 1 个文章方案是唯一内容门；批准后不得重新解释原文或另提方向。`RESEARCH.md` 只调研与获批核心相关的嘉宾身份、经历、背景故事和事实边界。全部面板绘制 50px 中文与 30px 英文；支撑条按双语文本实测高度分配并最多保留 30px 画面，Hero 至少占 60%，必要时把水平边距从 6% 收到最低 3%。Hero 与支撑字幕黑底 alpha 分别为 145 和 165。各面板从选定视频帧图片底部向上裁切，字幕条之间无间隙，整图至少保留 40% 无字幕空间。`PACKAGE.md` 直接使用可复制的纯文本：第一行为标题，其后为开篇、`01｜小标题` 形式的分节、正文、署名、`原视频：<视频原标题>` 和标签；render 只负责分离标题、正文、1 至 3 个话题和有序图片，正文连同话题不超过 1000 字。不点击发布。

候选阶段用 `dbs-resonate` 检查每个方案是否只服务一个核心机制；`dbs-spread` 只提供受众情绪、有效立场和第一传播者信号，用于候选理由与排序，不改写原文。文案阶段不得把读取 Skill 或默认借用规则当成调用：先完成不含平台大标题的开篇、每图小标题与正文草稿，再单独调用 `dbs-content` 输出针对表达效率、认知落差和小标题的具体修订诊断，由文案 Skill 应用诊断；正文与小标题稳定后，单独调用 `dbs-xhs-title` 仅根据获批文段生成 5 至 8 个候选，覆盖至少 3 类公式、标注公式编号并给出 Top 3，再选定不超过 20 字的 Top 1。嘉宾背景不得作为大标题前提，除非它本就存在于获批文段且对含义必不可少。最后单独调用必做的 `dbs-ai-check` 诊断完整成稿。`dbs-content` 只诊断，不代写；修订仍由文案 Skill 完成。`dbs-hook` 与 `dbs-script-flow` 不进入本工作流。

URL 获取只调用外部 `trendradar-media` v2.0。适配器只接受成功 envelope 与单条成功 manifest，复核大小和 SHA-256 后原子复制到 `materials/source-video.*`，并保存不含外部临时路径的 `materials/acquisition.json`。YouTube 可先采用带结构化时间戳的原生转录；不可用时才在用户明确同意后调用共享 ASR。下载器本身不提供转录。
