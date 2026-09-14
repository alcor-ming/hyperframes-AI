# HyperFrames AI 创作 Harness

## 工作边界

- 本仓库公开管理 Harness 规则、模板、Profile 接入、Skill 路由与 Work CLI。
- WSL 是 Harness 工具的唯一开发面，负责 CLI、宿主接线、依赖装配与安装器；Windows 负责 Work 和视觉资产内容，包括 Work-local 或已登记 AssetSource 内的 Scene、GSAP 动作、Three.js、shader、SVG、模型与内容脚本。分类看职责，不以扩展名、复杂度或可复用性把视觉内容交回 WSL。
- Windows 不修改安装包、已接纳 AssetStore 包、冻结 vendor 或 Accepted Snapshot；变化在可编辑源中完成，需要复用时生成新版本。WSL 默认只读正式 Work 与生产资产源；仅按工具缺陷请求，在冻结最小私有副本中调试，不改生产 Current、Binding、接受状态或 Final。
- 所有作品的当前真源位于外部 WorkStore `D:\AI\AI+hyperframes`（WSL `/mnt/d/AI/AI+hyperframes`）的 `works/`，包括文案、媒体、工程、Draft、Final 和运行状态；这些内容不得进入开发仓或 Git。
- 不公开发布内容、不购买额度。只有用户对准确 Work 与 Variant 明确授权后，才可使用其已登录的 Windows Chrome 保存到小红书创作者平台草稿箱；不得读取 Cookie、调用未公开接口或点击发布。
- `podcast_quote_image` 的 URL 获取只调用外部 `trendradar-media` v2.0；仅采用校验成功并复制进当前 Work 的媒体，不引用其七天后过期的运行目录，也不在本仓库实现下载后端。
- v1 默认不生成 AI 图片；仅在用户明确授权、Animation Plan 已批准且存在明确 Asset Brief 时可调用 ImageGen。`design-taste-frontend` 仅用于已批准且明确要求其介入的图片 Asset Brief。不查询图片 Prompt 库。`hyperframes_video` 不生成或烧录底部字幕；`podcast_quote_image` 由工作流在选定视频帧上绘制批准的中英双语字幕。

## 开发仓与 WorkStore 路径

- 当前开发仓真源为 `/home/jym/workspace/hyperframes+AI`；Windows 旧仓 `/mnt/c/Users/Jym/Documents/hyperframes+AI` 仅作为未删除的回滚副本，不继续开发。
- 当前正式 WorkStore 真源为 Windows `D:\AI\AI+hyperframes`（WSL `/mnt/d/AI/AI+hyperframes`）；生产 `work root show` 返回该路径，其 Current Work、命名锁和后续运行状态位于 WorkStore 的 `.runtime/`。候选工具只读取自身根配置指向的隔离 Review 内容，不切换正式指针。
- 开发仓通过本地且 Git 忽略的 `.studio/.runtime/work-root` 绑定 WorkStore。切换路径只使用 `./work root set <absolute-path>`，目标必须已经包含 `works/active`、`works/parked` 与 `works/archive`。
- 旧仓和旧 Work 副本不再具有当前权威；不得在新旧两处同时写入，也不得在没有单独明确授权时删除任一回滚副本。

## 启动顺序

用户在 Windows Codex App 直接打开 `D:\AI\AI+hyperframes`，新建对话并下达任务，无需打开 CMD。Agent 按需调用根目录 `work.cmd`；入口直接运行已安装版本，读取本机配置，不创建或依赖 Harness session。下文 `./work` 均替换为该命令的绝对路径，不选择候选、Review 根或会话目录，不运行 WSL 创作入口。

1. 前台交互运行 `./work current`；没有 Current 时运行 `./work list`，不得猜测作品。后台任务必须接收明确的 Work ID 与 Variant ID，并用 `./work --work <id> --variant <id> status` 启动，不读取或改写 Current。
2. 读取当前 `WORK.md` 与 `variant.yaml` 后按 `workflow` 路由：`hyperframes_video` 使用唯一视频 Skill；`podcast_quote_image` 在文章方案批准前使用 `planner_skill`，批准后使用 `copy_skill`。
3. `hyperframes_video` 再读取 `SCRIPT.md`、当前 Template Recipe 与选定 Profile；Research 只按当前 Scene / Anchor 的信息缺口读取或补查相关采用条目和资料依据，进入视觉设计时再读取 `ANIMATION_PLAN.md`。仅在 Plan 构建或复审、Draft 画面复审时加载 `hyperframes-anti-ppt`，进入实现或 QA 时才读取对应 `.studio/spec/`。
4. `podcast_quote_image` 只读取当前阶段的 Skill 与机器 JSON；文章方案批准后先完成播客专用 `RESEARCH.md`，再生成 `PACKAGE.md`。不得加载视频工作流的 Script、Plan、Recipe 或 Profile。

新建 Work 时，CLI 在命名锁内按 Workflow 分配三位递增序号，并以 `work-<workflow>-<序号>` 创建 Work ID 和目录；输入标题、来源标题与 LLM 均不得参与目录命名，创建后也不得改名。`podcast_quote_image` 在转录可用后、生成文章方案前，自动执行 `./work --work <id> --variant <variant-id> name "<嘉宾名>-<核心主题>"`；`hyperframes_video` 在 Script 稳定后、开始 Research 前执行 `./work --work <id> --variant <variant-id> name "<核心主题>"`。`name` 只补充语义标题并保留创建时的序号；语义标题保持简短，不使用来源平台 ID。

不要默认加载全部 Profile、全部 DBS Skill、Examples、Migration、发行文件、全部 QA 历史或全部 Draft 快照。

## 后台与并行

- 一次输入多条来源时，每条来源创建一个 detached Work；Batch 只用于汇总进度，不创建共享内容目录。
- `Current Work` 只是前台导航指针，不是后台任务身份。后台任务的每个 `./work` 命令都必须显式传入 Work 与 Variant，且一个 Work/Variant 同时只允许一个执行者。
- 不同 Work 可并行运行，Workflow 可以混合；共享 ASR 同时只运行一个实例，下载可并行。任务调度由 Agent 运行时负责，Harness 不另建常驻 daemon。
- `podcast_quote_image` 在后台完成下载、转录和 3 个完整文章方案后进入 `waiting_user/article_selection`；用户只确认其中 1 个。单个 Work 的等待、失败或重试不得阻塞同批其他 Work。

## 创作真源

- `source.md`：主要原始基线，DBS 不覆盖。
- `materials/*.transcript.json`：下载视频的时间真源；YouTube 可优先采用结构化原生转录，其余或 fallback 统一复用 `qivance-music` 的共享 ASR，ASR 的 `characters[]` 不得退化为仅段级时间戳。
- `SCRIPT.md`：当前 Variant 唯一口播正文，以及由成对 `scene-index` 注释明确排除出口播的简短 Scene / Anchor / 规划时间 / 信息缺口索引；批准后的隐藏段落 ID 保持稳定，索引不进入阅读版、统计、配音或对齐。
- `RESEARCH.md`：视频工作流在同一文件内保存按内容缺口取得的“资料依据”和按 Scene / Anchor 组织的“采用信息”，并记录与 Script Revision 的适用关系；不负责视觉机制、布局、裁切或成片时间。播客图文工作流仍记录嘉宾身份、与获批观点相关的经历、可用于正文补充的背景信息、事实边界和来源。
- `PACKAGE.md`：视频工作流保存最终标题、封面文字、一句话简介和内容概括；内容概括按主要对象或主题简短分项，介绍多个 Skill、工具、功能或案例时逐项单独说明。播客图文工作流直接保存可复制的纯文本，第一行为标题，其后依次为开篇、`01｜小标题` 形式的分节与第三人称正文、署名、`原视频：<视频原标题>` 和话题标签，不放来源地址、Markdown 标记或“大标题”“开篇”“图片文案”等结构说明。标题与开篇第一段必须从用户获批的选取文段归纳，不得用文段之外的嘉宾背景主导；标题在全文稳定后最后拟定。render 生成 `xiaohongshu.json`，分别保存标题、正文、1 至 3 个话题与有序图片。
- `section_map.json`：实际录制或配音与 Script Anchor 的机器对齐结果；实际媒体是时间权威。
- `ANIMATION_PLAN.md`：全片视觉语义、A/B 职责、逐 Scene 语义对象、素材占位与 cue 意图真源。整片 Plan 后制作一个真实 Scene 动态参考，用户一次方向批准后扩成完整占位 Draft，再补齐素材生成最终 Draft；不另建 Shotbook。Work 源码与 Binding 是可执行真源。
- `variant.yaml`：当前 Variant 状态，由 CLI 与 Agent 更新。
- `materials/acquisition.json`：URL 媒体的来源、Hermes job、平台和本地副本摘要；不得保存外部 `manifest_ref` 或临时媒体路径。
- `artifacts/transcript.json`：`podcast_quote_image` 的已解析文案和时间真源；字幕优先，转录仅补空档，冲突必须人工确认。
- `artifacts/article-candidates.json` 与 `article-selection.json`：3 个完整文章方案及用户批准的唯一方案真源。
- `artifacts/aligned-quotes.json`、`frames/frame-candidates.json` 与 `frames/frame-selection.json`：脚本生成的时间对齐与候选帧状态，不用临时文档替代。

## 创作检查点

- `hyperframes_video` 的下载视频必须通过共享 ASR 生成字级时间戳文案，再在 `SCRIPT.md` 中明确选择 `dbs` 或 `verbatim`：前者允许多轮 DBS 修改并在正文变化后等待批准；后者逐字保留口播与原时间戳，不运行正文改写。
- DBS 实际修改口播正文时，等待用户批准 `SCRIPT.md`；只诊断或只改包装文案时不等待。
- Script 确定后，按 Scene 索引与口播 Anchor 的真实信息缺口研究；可选择概念 / 原理 / 例子、比较、应用 / 过程 / 效果、背景故事 / 反差事实 / 代表性案例，也可无新增研究。`RESEARCH.md` 的资料依据保存研究结果、来源和素材证据位置，采用信息保存可直接使用的精炼措辞及引用，必要时区分核心与可选。
- 创建或复审 Animation Plan 时使用 `hyperframes-anti-ppt` 检查信息是否被正确表达、阅读窗口、关系与动效适配；不要求逐字逐卡摆放，不强制统一场景公式。结果合并进现有 `ANIMATION_PLAN.md`，不新增文件或审批门。组件的检索、版本、Slots 与安装仍由视频工作流或组件库能力负责。
- Research 完成后，创建 Animation Plan 的同时调用 DBS 完成 `PACKAGE.md`；只保留最终标题、封面文字、一句话简介和内容概括。
- 主模型对最终 Scene 负责：换行、层级、分组、顺序和无独立主张的标签直接在样段 / 工程调整；删除重复措辞、等义精简或转成流程短语时原位更新对应 Research 采用条目和呈现，不重新联网、不增加文字审批。逐字口播引用 Script Anchor；独立信息写入 Research；原视频 / 截图内文字归素材，已清楚呈现时不强制重复覆盖。
- 不采用可选增补无需回传。新增数据、比较或因果只补查相关条目；删除核心信息，或改变事实结论、观点、因果、必要数值 / 单位 / 归属及已确认叙事时，提出局部取舍和对 Scene / 时间的影响。确实无法同时保留核心信息与时间预算时直接交给用户取舍，不循环压缩。
- Script / Research 就绪后，先完成整片 Plan，按真实含义、关系、媒体和时间匹配语义视觉对象。保留已有 M2–M3 源码、Scene/Anchor ID 与画面，不为重构拆解对象内部联动或回退公开 HEAD。随后仅选一个当前 Scene 制作动态参考，优先复用已有成果；使用真实文字、画幅和已有音频片段，缺素材用稳定 ID 的语义占位，无最终音频标 provisional。局部布局不自动推广全片，不额外制作多 Scene 拼接样片。
- 主要动效先写清对象关系、起止状态、阅读安排与必要替代，默认在 Draft 最先实现最不确定的镜头；只有会改变整体决策的风险才提前局部试做。Windows 在 Work-local 或已登记 AssetSource 开发效果，未实现动作不无条件阻塞 Plan；只有宿主、合同、工具或依赖装配缺口才交给 WSL，不改公共冻结资产。
- 用户一次确认整片 `ANIMATION_PLAN.md` 与唯一 Scene 参考的制作方向，之后直接按各 Scene 方案扩片，不逐场审批或要求 Work-local 对象先入库。完整占位 Draft 必须覆盖全片和已实现动作，允许 Plan 登记的 planned placeholders、临时音轨及明确约定 proxy；不能掩盖空 Scene、代码错误或缺失内容，不增加占位 Draft 的强制批准门。素材齐备后生成最终 Draft，沿用原完整 Draft 接受与 Final 流程。方向批准和占位 Draft 均不放行 Finalize。
- Draft 提交用户前使用 `hyperframes-anti-ppt` 复审成片或代表性关键帧；`PASS` 只是 QA 结果，不替代 Draft 接受。
- Final 必须从用户接受的 Draft 源码快照继续。
- Script / Research / Plan Revision 继续留痕；版本变化先检查实际影响范围，只补查、同步或重做引用变动的 Scene 与必要衔接，不自动刷新全片。内容等义由主模型判断，机器仍校验明确范围、引用及冻结 / 当前内容一致性；元数据同步不等于旧 Accepted Draft 自动批准新画面。
- 只在 Scene 数量、顺序、视觉目标、Hero State、Template、Profile、文案结构或核心内容发生实质变化时重新确认受影响部分。反馈绑定预演/Draft 版本、Scene 与必要时间范围，只修改该范围及必要衔接，保留未受影响场景与原 Accepted Draft / Final 快照。
- 时间码、easing、换行、安全区、性能和不改变 Hero State 的布局修复无需重新批准。
- 三类时间各自留在权威位置：Script 是规划预算，现有 timestamps / `section_map.json` 是人声证据，工程是实际时间。Binding 记录 Anchor、字符范围或明确 occurrence、对象语义事件及必要偏移；源剪辑、take、速率与 Scene 裁取仅做确定映射，不重写原对齐。关键画面和音轨从目标时间重建，不依赖 seek 回调。音乐分析可选且按 hash/参数离线缓存；无 BGM 或 Blender 不阻塞非依赖场景。

`podcast_quote_image` 拆成两个 Skill：第一个通读已解析文案，结合 `dbs-spread` 与 `dbs-resonate` 生成 3 个有原文证据的完整文章方案；用户只批准 1 个。第二个先调研嘉宾背景并完成 `RESEARCH.md`，再从获批的选取文段归纳开篇第一段、每图小标题与第三人称正文草稿。此时必须单独调用 `dbs-content` 对开篇、每个小标题和正文进行标题、表达效率与认知落差诊断，由文案 Skill 应用诊断后，全文稳定才能单独调用 `dbs-xhs-title`，仅根据获批文段的共同结论、冲突或因果生成 5 至 8 个可追溯公式编号的大标题候选，覆盖至少 3 类公式并给出 Top 3，再选定 Top 1。不用文段之外的嘉宾身份、估值或履历作为标题前提。最后必须单独调用 `dbs-ai-check` 诊断完整成稿；仅读取 DBS Skill 或默认套用其规则不算完成调用。然后再完成时间匹配、取帧、渲染和 Final。每篇文章输出 8 至 12 张图；每张图固定 1 条 Hero，并用若干约 10 个汉字的完整支撑短句推进论证，中文总字数以 60 至 90 字为目标区间，不设逐句硬上限。同一内容允许按语义拆成相邻两张图，详细背景、案例和推导留在 `PACKAGE.md` 正文。全部面板绘制中英双语字幕，中文固定 50px、英文固定 30px；支撑条按双语文本实测高度分配并最多保留 30px 画面，Hero 至少占 60%，必要时把水平边距从 6% 收到最低 3%。Hero 与支撑字幕黑底 alpha 分别为 145 和 165。每个面板都从选定视频帧图片的底部向上裁切，字幕条之间无间隙，整张图至少保留 40% 无字幕视觉空间。图片边界按原文的铺垫、观点、论证、例子、对比与收束组织，不按标点机械切分。批准文章方案是唯一内容门，不增加第二个 Draft 审批门。转录缺失、失败或不可用时进入 `waiting_user`，仅在用户确认后使用保留的 `native-subtitle-quote-image` fallback，不得静默降级。

## 模板

- `talking_head`：人物为主叙述时采用；A/B-roll 是逐 Scene 的叙事职责，不把人物布局强加全片。已有实际音频与 `section_map.json` 优先复用；无正式录音可用明确临时音轨扩成占位 Draft。
- `pure_hyperframes`：无真人主视觉时采用；可先以预算生成 provisional 全片 Draft，不宣称卡点通过。正式音频就绪后只重定时相关部分，最终 Draft 再作完整接受。
- 人物持续作为主视觉时才使用 `talking_head`；否则使用 `pure_hyperframes`，不增加第三套模板。

以上 Template 仅属于 `hyperframes_video`。`podcast_quote_image` 固定使用 `podcast_drawn_subtitle_stack_v1`，输出 1440x1920 的 3:4 图片，不新增 Template 或 Profile。

## 用户回复

只展示实际设计结果、变更、阻塞和需要决定的内容。不要展示读取清单、逐项 QA、审批证明或流程自证。Plan 首版可以完整展示，后续只展示变更 Scene 和未解决决策。

## 生命周期

- Work 和 Variant 的创建、指针、等待、Park、Draft 注册、Final、Archive 与 Reopen 只通过 `./work` 管理。
- CLI 只管理生命周期和文件一致性；内容判断与视觉选择仍由 Agent 负责，确定性的解析、时间与格式处理交给对应 Skill 脚本。
- 日常制作、唯一 Scene 动态参考和 Draft 审阅默认通过 Work CLI 启动锁定版本的官方 HyperFrames Studio，返回实际工程 URL；自制审阅页仅保留显式历史查看。当前工程可编辑，登记版本只在独立复制的审阅副本中打开，不用 hardlink / symlink 暴露冻结快照、vendor 或资产包。定位绑定准确 Work / Variant、工程和实际端口，只读必要 Scene / selection / lint 上下文；Studio 改稿同步原文案真源或暂停相关再生成，旧 MP4 / QA 不冒充对应新源码。
- Final 是本地交付物，不表示已保存到平台草稿箱或已发布；两者分别需要外部动作，且草稿授权绝不包含发布。

## Release 与 Codex App 部署

- Windows Codex App 直接打开 `D:\AI\AI+hyperframes`，根 `work.cmd` 根据自身路径运行同根 `runtime/` 与 `.studio/`；配置从 `.studio/.runtime/` 读取，不经过 `.harness/releases/current`、workspace 或 session，不生成自动 session。Windows 不编辑受管理工具文件。
- 一次命令解析配置一次；长进程固定本次 Work、Variant、资产、依赖与配置输入。继承的旧 session、HOME、AssetRoot 不得重定向工具或 Review；保留必要 Provider 凭据。配置修改仅影响后续命令。
- WSL 从当前受控工作树构建本机包，保留已完成 M2–M3 内容，不重跑 M0–M1，不自动 commit/tag/push。正式 `harness-YYYY.MM.PATCH` 发行仍要求干净、tag 与 upstream 一致；dirty 候选不冒充稳定发行。
- 严格发行包校验检查全部文件、hash、依赖与路径；部署根校验只检查 manifest 拥有的文件，不将 Work、配置或用户 Skill 视为损坏。生产更新只覆盖管理文件；旧清单拥有且新版本移除的文件才可删除，遇到用户修改保留并报告，不全根 mirror/delete。
- 更新先验证 staging、备份旧管理文件与迁移信息，再更新并最后写完成标记；中断可检测和恢复，损坏组合拒绝启动。复用现有进程记录与最小互斥，更新前停止相关 Studio/render/build 进程，不热换依赖，不新建 daemon。
- 候选部署在独立根，拥有同样的直接入口、独立配置与 Work/Asset/source-copy。Review 不写生产源、Current、接受记录或默认配置，不允许正式 Finalize、归档完成和平台草稿。不将隔离测试变成日常生产前置门。
- 优先登记已有 AssetSource；Windows 开发语义视觉对象并按实际 module/media 合同生成冻结新版本，不强制拆 helper、双画幅、五阶段或全库迁移。vendor / Binding / Lock 固定准确依赖，库离线不影响闭合作品，同身份版本不同内容拒绝覆盖。
- 工具缺口只交冻结最小复现给 WSL；视觉内容留 Windows。旧包、旧 session 与旧源码仅保留回退资料，不自动重写或删除。程序回滚不降级 Work schema、不重绑资产；不兼容时保留新数据与可用工具。外部发布、删除不可替代内容及安装切换仍遵守准确授权。

- Windows 共享 ASR 只通过包内 `asr-wsl.cmd` 调用固定的 `Ubuntu` 和 `/home/jym/workspace/_external/scripts/asr.sh`。桥接器必须拒绝 `D:\AI\AI+hyperframes` 外的输入或输出，并把 WSL 内的 `wslpath` 路径转换、ASR 可用性检查和转录合并为一次 `wsl.exe --distribution Ubuntu --exec /bin/sh -c <fixed-script>` 调用，任务参数经 `WSLENV` 传递，并原样传递 stdout、stderr 与退出码。Windows Codex 沙盒可复用 WSL ASR、模型和 GPU，但未获得包内 `asr-wsl.cmd transcribe-faster` 顶层 argv 前缀的持久授权时，每次 ASR 作业仍可能需要用户审批；不得授权任意 `wsl.exe` 命令。
- `D:\AI\AI+hyperframes` 是统一使用根：`runtime/`、`.studio/` 是已部署工具，`.studio/.runtime/` 是根配置；`asset-library/sources` 与 `asset-library/store` 保留可编辑源和冻结资产职责，不改用既有 `assets/`。Work、请求、Review 与 `.runtime/` 的既有内容保持不动，可写 Harness 开发真源仅在 WSL。
- 更新完成后重启相关工具进程，Agent 重读根规则；下一条根命令用新版本，无需创建 Harness session。单次命令/长进程固定输入，不宣称整次聊天跨命令固定版本。
- 日常只使用统一根目录的 `work.cmd` / `work.ps1`；`doctor` 报告实际部署身份、规则、内容路径与 Review 范围。新命令或参数仅在实现后写入可执行帮助；Windows 原生结果与 WSL/mock 分别报告。
