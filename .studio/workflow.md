# 创作工作流

环境、权限、生产与开发隔离只见根 `AGENTS.md`；阶段定位与按需加载见 `hyperframes-codex-workflow` Router。本文件是视频四阶段顺序、接受边界和播客分支的唯一流程。

## 视频入口

制作入口是独立的**叙事模式、视觉主题、背景、画幅**，通用运动槽位可选或关闭。叙事模式为文字主导或动效主导；采用用户已指定的主题、品牌字体与配色，不强制前置 Profile、Template 或 Subtemplate 连续选择，不新增主题审批。未指定模式时根据内容推荐，随既有方向确认，不增加混合型。Template 是人物/画面结构配置，仅按任务需要读取 Recipe。

Theme 只负责前景字体、字号角色、语义颜色、卡片表面/边框/圆角/阴影及图形线型，不拥有叙事模式、背景、布局、cue 或动画参数；不再要求 Theme 声明两种模式。Background 独立选择舞台底层，Motion 只控制从既定 cue 开始怎样动，不改 cue、选材或背景身份。画幅与宿主能力按组合验证，不临时拉伸或裁切冒充适配。更换字体、主色、背景风格或整体卡片语言仍是方向变化，只确认受影响部分。Account 只存精确资产引用和合法覆盖，Variant 冻结解析值及实际文件闭包，Plan 引用而不另建可编辑 tokens。旧 Profile 和旧 Theme 快照保持兼容，不自动拆分、接纳或迁移。

IP Beta 复用工程能力，但按真实内容与用户美术判断探索，不机械套两种标准模式、卡片比例或标准节奏。Remotion/Blender 仅在确有镜头需要时接入，不同时扩张人物系统和大资产库。

## 1. 内容准备

创建视频对象前先按 Router 区分讨论、继续现有对象、同目标独立 Variant、临时实验和新生产目标；只在用途仍有实质歧义时先问。新视频 Work 显式传 `--purpose standard|ip|test`；生产用途需要有效系列与已登记账号，实验按用途命名、不绑定账号，准确账号设置只作参考快照。同账号可有多个 Variant，不用账号名代替准确版本选择。未指定叙事模式默认 `text-led`，不自动选择旧 Profile。账号默认设置及主题版本/参数在生产 Variant 创建时冻结，不随后续默认值更新漂移。

实验可保留，不自动清理；只有准确删除请求才检查运行中的 Studio、未完成请求及生产工程/素材对实验目录的实际路径依赖，引用不明时停下说明，不级联删除生产、源媒体或公共资产。生产采用实验结果时先复制或冻结所需文件到生产 Work，不能把临时目录当运行依赖；历史 `source_work` 只记录来源，不等于活依赖或生产接受。做出实际选择时在相关 Plan/说明写一句结论和采用版本，不要求无结论实验写报告。

新视频 Work 的 Script/Research 默认位于 `shared/`，按 Variant 的 `shared_inputs` 定位；各 Variant 仍拥有独立 Plan、工程和接受/Final。显式 `variant add --from <id>` 建内容分支，旧 Variant-local 文稿位置保持兼容，不复制或重写历史来适配共享。

已有合格 Script、音频、对齐和材料直接复用。Script 为空但有文稿/转录时先整理，不把全面查证作为前置。下载视频走共享 ASR 的字级 `characters[]`，保留正式声音和时间证据；`dbs` 仅在实际修改口播正文后等待批准，`verbatim` 保留原文、Anchor 和时间戳，不改正文。来源、Scene 索引、Revision 与录制失效规则见 `spec/creative.md`。配音、统计与对齐用 `work script text` 排除非口播索引；不重复运行已有合格 ASR。

Script 稳定后用 `work --work <id> --variant <id> name "<核心主题>"` 补语义标题，不改身份或目录。Research 先理解完整段落，再按部分/Anchor 记录事实、实例、素材依据、使用边界和真实缺口；已有材料足够即复用，不强制配图或联网。它不规定布局、裁切或动画，不是第二份脚本或必上屏清单。具体材料缺口才定点补研究，不重开全轮或增加 Research 审批。事实冲突只提交相关影响，不擅改原音或阻塞无关部分。

`PACKAGE.md` 仅按交付需求生成，**不是视频设计、制作或接受的前置**；只要求视频时不默认生成标题、封面、简介或调用标题流程。包装内容合同见 `spec/creative.md`，播客专用包装不受此可选规则影响。

## 2. 整片设计

读取当前 Plan、有效 Research 选材与 `spec/visual-design.md`；Template 差异只见 Recipes，选中具体资产后才读取 `spec/hyperframes.md` 的资产接线合同。Script、Research、Plan 分开保留，Plan 是唯一采用后的视觉设计，不复制全文或另建 Shotbook/文字数据库。

全片 Plan 保留整片概览，并用上屏信息表决定完整理解单位的必要信息、准确表达、来源和声画分工；实际屏幕正文只在此处维护。Scene 节拍表按信息 ID 引用，安排完整区间的进入、阅读、变化、交接和退出，不复制正文或逐句截短口播。每场覆盖进入、阅读过程和离开，但按真实变化决定行数，稳定证据页可只需一个持续阅读状态。保留独立外观/模式输入、A/B 职责、时间依据、场景策略和素材安排。原稿数字按原意采用，事实与比喻边界见 visual-design；Research 历史核查与当前采用决定分开，清理可编辑 Plan/brief 的冲突指令，冻结历史不改。一个 Script 段可跨多个 Scene，不改原声、Anchor、原总时长和源对齐。正式音频与对齐是时间真源，Plan 只记 cue 引用及意图，cues/Binding 解析实际值；含糊处局部核验，不猜平均时间或手写第三套秒数。

先选择要表达的真实关系再选对象；保留现有成果和稳定 ID，不按技术类别强迫每场演绎机制。Plan 列已采用的资产精确版本/限制或 Work-local 实现，已适配能力直接复用，不以未入公共库阻塞。拟生成素材按 AGENTS 的授权合同登记用途、数量、风格与 Asset Brief，占位具有稳定 ID 和完成判据，不伪造路径。

整片 Plan 后只做**一个真实 Scene 动态参考**，优先复用当前成果，展示真实文字、画幅、动作和已有对应音频；无最终音频明确 provisional。仅影响整体决策的风险才提前局部试做，不增加第二个参考审批或多 Scene 拼接样片。

用户一次方向确认覆盖 Plan revision 与准确 Scene 参考。局部布局不自动推广全片，不逐场、逐素材或逐 Work-local 对象审批；方向确认不等于完整 Draft 接受。

派工 brief 摘取当前 Plan 的负责范围、采用的信息 ID 与表达、完整状态编排、上下场衔接、时间依据、精确资产引用和写入边界，不成为第二份设计；不能只传整段 Script 与总时长让 worker 均分。不可行时反馈准确冲突，不擅自删条件、填衔接句或缩字号。修订清理可编辑 brief 中失效要求，冻结历史不改；worker 完成不代替主模型内容验收。

正常 Scene 派工同时携带 `spec/visual-design.md` 的“图文互补与辅助图形”短入口，以及 `work component list --query <用途>` 的发现入口；仅传选中对象的精确引用、取用方式和本地合同/示例。普通装饰交制作者完成，不要求主模型逐图指定。无匹配资源时明确转 Windows Work-local 或可编辑 AssetSource 制作，不让 worker 猜全库路径，不虚构可运行预设。查询状态、安装及外观重绑定详见 `spec/hyperframes.md`，不因检索刷新改动现有 Work。

## 3. Studio 制作与验收

一次方向确认后直接扩成全片 Draft；占位到素材齐备是同一阶段的准备度变化，不拆成审批流程。完整占位 Draft 覆盖全部 Scene、A/B、实际动作和阅读安排，允许 Plan 登记的 planned placeholders、临时音轨和约定 proxy，不掩盖空 Scene、代码错误、缺失观点或未实现动作。素材按同一 ID 补齐，只重定时受影响范围；最终接受前正式音频、必需媒体与效果必须齐备。

日常通过 Work CLI 打开锁定官方 Studio，使用返回的真实工程 URL。当前工程可编辑，登记版本打开独立审阅副本；历史自制页面仅显式 legacy 查看。定位绑定准确 Work/Variant、工程与实际端口，按需读取 selection/lint；浏览器使用返回的隔离 profile 并核验 DNT。具体 ready/seek、资源闭包和 CLI 技术操作见 `spec/hyperframes.md`。

素材齐备后，无文件参数 `preview register` 冻结 executable Studio Draft；`preview open draft-vNNN` 审阅准确版本，再 `preview accept draft-vNNN`。旧文件型记录保持可读，但新 Draft 与 test-work 不导出视频，不以短段或镜头预渲染替代 Studio。受限时明确未验证项并提交工具缺口。

对照 `spec/visual-design.md` 检查声音、手机等效尺寸、实际语义揭示和画面运动，技术检查按 `spec/hyperframes.md`。检查 Windows Studio 连续播放、暂停、任意 seek、回拖和跨 Scene；静帧、mock、独立 Player、代码存在均不等于原生通过。技术 PASS、素材 complete、方向确认都不能替代用户接受准确 full Draft。

反馈绑定具体版本、Scene 与必要时间范围，仅修改影响范围及交接。缺必要信息回 Plan 编辑，实际证据缺口回 Research，空间关系不清改布局，阅读/交接不匹配改节拍，代码偏离修实现。Studio 文案修改同步 Plan 的实际上屏表达；新增事实、改变原意或证据边界才回权威来源，工程不是第二份文案真源。等义、换行、easing、安全区、性能修复无需新方向确认；改变已确认观点、场景结构、视觉目标或整体主题时只确认受影响部分。来源或 Revision 变化的新画面必须登记并接受新 Draft，不覆盖旧接受/Final。

## 4. Final 交付

每个生产 Variant 独立进入 Finalize，不等待其他账号完成。只有准确 full、素材齐备的 Accepted Draft 可进入必要镜头生成、正式整片渲染、编码 QA 和版本化 Final 记录；正式输出绑定接受快照与 render receipt，不从变化后的可编辑工程冒充接受源。test-work 不进入任何视频导出链，Review 不进行生产 Finalize。

Finalize 入口与已实现参数以当前 CLI 帮助为准；不要把目标能力写成可用命令。Remotion 若被采用，预览依赖宿主时钟/ready 实际联动，不能提前导出镜头；必要中间媒体仅在生产 Finalize 派生目录生成，不修改接受快照。缓存必须核对准确源、props、资源、锁定依赖、画幅、fps、帧区间和渲染设置，相关输入改变只使对应镜头失效。

新编码检查流、格式、原音时长、全量解码、代表帧和必要音频；首次跨引擎交付还需比较语义关键帧、构图、中文边缘/细线、字体、颜色、透明合成与声音。不重复设计审批不等于省略输出一致性。失败保留复现，不覆盖旧 Final、不假报完成。Finalize 不包含上传/发布，也不自动归档。

软归档是独立管理标记，无 Final 也可归档；不搬目录、不清理文件、不充当验收。查看不自动激活，继续制作保留旧接受/Final。旧物理归档可读，不为新规则改写历史。

## 复用与局部变更

同版本、同对象、同依赖的有效检查直接沿用；变化才检查受影响 Scene、状态与必要衔接，共享布局/时间线/宿主变化按依赖扩大。Studio 内容、新编码和归档文件完整性是不同对象，不能互相替代，也不重复审片或渲染。

`preview diff <id>` 定位源码差异；`--compatible` 仅按运行时现有冻结来源和哈希检查沿用 Accepted Plan 进入新 Draft，不把新工程变成旧 Accepted Draft。口播、Anchor 和 Plan 视觉正文必须未变，仅容许其既有状态/引用元数据同步；机器不判断自然语言等义，旧记录缺冻结来源保留原流程。变化只更新相关 Research/Plan 引用，不全片重写。

实际投入和缺失统计可记现有 Work 备注；等待时间单列，不用文件长度代替 token，不以技术夹具承诺成本下降。

## Windows 与 WSL 请求交接

内容派工只携带当前有效的叙事模式、Plan 范围摘取、对应 Research 依据、必要 Script/cue 引用与资产，不只给全文口播和精细 cue，也不强制每批复制全部 Research。修订时清理可编辑 brief/CONTRACT 的失效要求，冻结历史不改；worker 完成不等于验收，主模型仍负责内容结果。

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
-> Agent 视觉 QA -> Finalize -> 按需独立归档 -> 经明确授权可保存到创作者平台草稿箱
```

字幕在覆盖区间内拥有文案和时间权威，转录只补无字幕区间；同语种明显冲突必须先人工处理。转录条件缺失或失败时进入 `waiting_user`，由用户决定是否改用保留原画面字幕的 fallback，不得静默降级。

每个文章方案包含 8 至 12 个按原文结构排列的图片组，每组固定 1 条 Hero，并用若干约 10 个汉字的完整支撑短句推进内容；中文总字数以 60 至 90 字为目标区间，不设逐句硬上限。同一内容可按语义拆成相邻两张图，图片只保留核心结论与必要论证，背景、案例和完整推导写入 `PACKAGE.md`。图片边界跟随原文的铺垫、观点、论证、例子、对比与收束，不按标点机械切分。用户批准 1 个文章方案是唯一内容门；批准后不得重新解释原文或另提方向。`RESEARCH.md` 只调研与获批核心相关的嘉宾身份、经历、背景故事和事实边界。全部面板绘制 50px 中文与 30px 英文；支撑条按双语文本实测高度分配并最多保留 30px 画面，Hero 至少占 60%，必要时把水平边距从 6% 收到最低 3%。Hero 与支撑字幕黑底 alpha 分别为 145 和 165。各面板从选定视频帧图片底部向上裁切，字幕条之间无间隙，整图至少保留 40% 无字幕空间。`PACKAGE.md` 直接使用可复制的纯文本：第一行为标题，其后为开篇、`01｜小标题` 形式的分节、正文、署名、`原视频：<视频原标题>` 和标签；render 只负责分离标题、正文、1 至 3 个话题和有序图片，正文连同话题不超过 1000 字。只有用户对准确 Work/Variant 明确授权后，才可用已登录浏览器保存草稿；不点击发布。

候选阶段用 `dbs-resonate` 检查每个方案是否只服务一个核心机制；`dbs-spread` 只提供受众情绪、有效立场和第一传播者信号，用于候选理由与排序，不改写原文。文案阶段不得把读取 Skill 或默认借用规则当成调用：先完成不含平台大标题的开篇、每图小标题与正文草稿，再单独调用 `dbs-content` 输出针对表达效率、认知落差和小标题的具体修订诊断，由文案 Skill 应用诊断；正文与小标题稳定后，单独调用 `dbs-xhs-title` 仅根据获批文段生成 5 至 8 个候选，覆盖至少 3 类公式、标注公式编号并给出 Top 3，再选定不超过 20 字的 Top 1。嘉宾背景不得作为大标题前提，除非它本就存在于获批文段且对含义必不可少。最后单独调用必做的 `dbs-ai-check` 诊断完整成稿。`dbs-content` 只诊断，不代写；修订仍由文案 Skill 完成。`dbs-hook` 与 `dbs-script-flow` 不进入本工作流。

URL 获取只调用外部 `trendradar-media` v2.0。适配器只接受成功 envelope 与单条成功 manifest，复核大小和 SHA-256 后原子复制到 `materials/source-video.*`，并保存不含外部临时路径的 `materials/acquisition.json`。YouTube 可先采用带结构化时间戳的原生转录；不可用时才在用户明确同意后调用共享 ASR。下载器本身不提供转录。

## 状态

制作状态、用途、Variant 身份与归档标记分别读取当前 CLI 输出；归档不是制作状态或接受证据。旧 main、Profile、无系列 Work 和物理归档保持可读；RC2 的旧视频 Work 一次性 ID/目录/标题迁移以专用 dry-run/apply 为窄例外，日常改标题或系列不再改 ID/目录，播客与冻结历史不迁移。
