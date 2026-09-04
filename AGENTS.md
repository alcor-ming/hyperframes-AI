# HyperFrames AI 创作 Harness

## 工作边界

- 本仓库公开管理 Harness 规则、模板、Profile 接入、Skill 路由与 Work CLI。
- 所有作品的当前真源位于外部 WorkStore `D:\AI\AI+hyperframes`（WSL `/mnt/d/AI/AI+hyperframes`）的 `works/`，包括文案、媒体、工程、Draft、Final 和运行状态；这些内容不得进入开发仓或 Git。
- 不公开发布内容、不购买额度。只有用户对准确 Work 与 Variant 明确授权后，才可使用其已登录的 Windows Chrome 保存到小红书创作者平台草稿箱；不得读取 Cookie、调用未公开接口或点击发布。
- `podcast_quote_image` 的 URL 获取只调用外部 `trendradar-media` v2.0；仅采用校验成功并复制进当前 Work 的媒体，不引用其七天后过期的运行目录，也不在本仓库实现下载后端。
- v1 默认不生成 AI 图片；仅在用户明确授权、Animation Plan 已批准且存在明确 Asset Brief 时可调用 ImageGen。`design-taste-frontend` 仅用于已批准且明确要求其介入的图片 Asset Brief。不查询图片 Prompt 库。`hyperframes_video` 不生成或烧录底部字幕；`podcast_quote_image` 由工作流在选定视频帧上绘制批准的中英双语字幕。

## 开发仓与 WorkStore 路径

- 当前开发仓真源为 `/home/jym/workspace/hyperframes+AI`；Windows 旧仓 `/mnt/c/Users/Jym/Documents/hyperframes+AI` 仅作为未删除的回滚副本，不继续开发。
- 当前 WorkStore 真源为 Windows `D:\AI\AI+hyperframes`（WSL `/mnt/d/AI/AI+hyperframes`）；`./work root show` 必须返回该路径，其 Current Work、命名锁和后续运行状态位于 WorkStore 的 `.runtime/`。
- 开发仓通过本地且 Git 忽略的 `.studio/.runtime/work-root` 绑定 WorkStore。切换路径只使用 `./work root set <absolute-path>`，目标必须已经包含 `works/active`、`works/parked` 与 `works/archive`。
- 旧仓和旧 Work 副本不再具有当前权威；不得在新旧两处同时写入，也不得在没有单独明确授权时删除任一回滚副本。

## 启动顺序

1. 前台交互运行 `./work current`；没有 Current 时运行 `./work list`，不得猜测作品。后台任务必须接收明确的 Work ID 与 Variant ID，并用 `./work --work <id> --variant <id> status` 启动，不读取或改写 Current。
2. 读取当前 `WORK.md` 与 `variant.yaml` 后按 `workflow` 路由：`hyperframes_video` 使用唯一视频 Skill；`podcast_quote_image` 在文章方案批准前使用 `planner_skill`，批准后使用 `copy_skill`。
3. `hyperframes_video` 再读取 `SCRIPT.md`、当前 Template Recipe 与选定 Profile；进入视觉设计时再读取 `RESEARCH.md` 与 `ANIMATION_PLAN.md`，仅在 Plan 构建或复审、Draft 画面复审时加载 `hyperframes-anti-ppt`，进入实现或 QA 时才读取对应 `.studio/spec/`。
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
- `SCRIPT.md`：当前 Variant 唯一口播正文；批准后的隐藏段落 ID 保持稳定。
- `RESEARCH.md`：视频工作流记录与 Script Revision 对齐的联网资料、可视化机制与事实边界；播客图文工作流记录嘉宾身份、与获批观点相关的经历、可用于正文补充的背景信息、事实边界和来源。
- `PACKAGE.md`：视频工作流保存最终标题、封面文字、一句话简介和内容概括；内容概括按主要对象或主题简短分项，介绍多个 Skill、工具、功能或案例时逐项单独说明。播客图文工作流直接保存可复制的纯文本，第一行为标题，其后依次为开篇、`01｜小标题` 形式的分节与第三人称正文、署名、`原视频：<视频原标题>` 和话题标签，不放来源地址、Markdown 标记或“大标题”“开篇”“图片文案”等结构说明。标题与开篇第一段必须从用户获批的选取文段归纳，不得用文段之外的嘉宾背景主导；标题在全文稳定后最后拟定。render 生成 `xiaohongshu.json`，分别保存标题、正文、1 至 3 个话题与有序图片。
- `section_map.json`：实际录制或配音与 Script Anchor 的机器对齐结果；实际媒体是时间权威。
- `ANIMATION_PLAN.md`：正式 HTML 制作前唯一必须批准的视觉设计 PRD。
- `variant.yaml`：当前 Variant 状态，由 CLI 与 Agent 更新。
- `materials/acquisition.json`：URL 媒体的来源、Hermes job、平台和本地副本摘要；不得保存外部 `manifest_ref` 或临时媒体路径。
- `artifacts/transcript.json`：`podcast_quote_image` 的已解析文案和时间真源；字幕优先，转录仅补空档，冲突必须人工确认。
- `artifacts/article-candidates.json` 与 `article-selection.json`：3 个完整文章方案及用户批准的唯一方案真源。
- `artifacts/aligned-quotes.json`、`frames/frame-candidates.json` 与 `frames/frame-selection.json`：脚本生成的时间对齐与候选帧状态，不用临时文档替代。

## 创作检查点

- `hyperframes_video` 的下载视频必须通过共享 ASR 生成字级时间戳文案，再在 `SCRIPT.md` 中明确选择 `dbs` 或 `verbatim`：前者允许多轮 DBS 修改并在正文变化后等待批准；后者逐字保留口播与原时间戳，不运行正文改写。
- DBS 实际修改口播正文时，等待用户批准 `SCRIPT.md`；只诊断或只改包装文案时不等待。
- Script 确定后，按口播 Anchor 联网研究并完成同一 Variant 的 `RESEARCH.md`；Script Revision 变化后旧研究失效。
- 创建或复审 Animation Plan 时使用 `hyperframes-anti-ppt` 明确视觉状态链并检查候选组件或组合 Preview；结果合并进现有 `ANIMATION_PLAN.md`，不新增文件或审批门。组件的检索、版本、Slots 与安装仍由视频工作流或组件库能力负责。
- Research 完成后，创建 Animation Plan 的同时调用 DBS 完成 `PACKAGE.md`；只保留最终标题、封面文字、一句话简介和内容概括。
- `ANIMATION_PLAN.md` 必须整体批准后才能正式实现 HTML 和 Draft。
- Draft 提交用户前使用 `hyperframes-anti-ppt` 复审成片或代表性关键帧；`PASS` 只是 QA 结果，不替代 Draft 接受。
- Final 必须从用户接受的 Draft 源码快照继续。
- 只在 Scene 数量、顺序、视觉目标、Hero State、Template、Profile 或文案结构发生实质变化时重新批准 Plan。
- 时间码、easing、换行、安全区、性能和不改变 Hero State 的布局修复无需重新批准。

`podcast_quote_image` 拆成两个 Skill：第一个通读已解析文案，结合 `dbs-spread` 与 `dbs-resonate` 生成 3 个有原文证据的完整文章方案；用户只批准 1 个。第二个先调研嘉宾背景并完成 `RESEARCH.md`，再从获批的选取文段归纳开篇第一段、每图小标题与第三人称正文草稿。此时必须单独调用 `dbs-content` 对开篇、每个小标题和正文进行标题、表达效率与认知落差诊断，由文案 Skill 应用诊断后，全文稳定才能单独调用 `dbs-xhs-title`，仅根据获批文段的共同结论、冲突或因果生成 5 至 8 个可追溯公式编号的大标题候选，覆盖至少 3 类公式并给出 Top 3，再选定 Top 1。不用文段之外的嘉宾身份、估值或履历作为标题前提。最后必须单独调用 `dbs-ai-check` 诊断完整成稿；仅读取 DBS Skill 或默认套用其规则不算完成调用。然后再完成时间匹配、取帧、渲染和 Final。每篇文章输出 8 至 12 张图；每张图固定 1 条 Hero，并用若干约 10 个汉字的完整支撑短句推进论证，中文总字数以 60 至 90 字为目标区间，不设逐句硬上限。同一内容允许按语义拆成相邻两张图，详细背景、案例和推导留在 `PACKAGE.md` 正文。全部面板绘制中英双语字幕，中文固定 50px、英文固定 30px；支撑条按双语文本实测高度分配并最多保留 30px 画面，Hero 至少占 60%，必要时把水平边距从 6% 收到最低 3%。Hero 与支撑字幕黑底 alpha 分别为 145 和 165。每个面板都从选定视频帧图片的底部向上裁切，字幕条之间无间隙，整张图至少保留 40% 无字幕视觉空间。图片边界按原文的铺垫、观点、论证、例子、对比与收束组织，不按标点机械切分。批准文章方案是唯一内容门，不增加第二个 Draft 审批门。转录缺失、失败或不可用时进入 `waiting_user`，仅在用户确认后使用保留的 `native-subtitle-quote-image` fallback，不得静默降级。

## 模板

- `talking_head`：先完成文案，再录制人物视频，以实际音频生成 `section_map.json` 后设计画面。
- `pure_hyperframes`：可先用估算时间完成视觉 Draft；用户接受 Draft 后接入正式配音并仅做重定时。
- 人物持续作为主视觉时才使用 `talking_head`；否则使用 `pure_hyperframes`，不增加第三套模板。

以上 Template 仅属于 `hyperframes_video`。`podcast_quote_image` 固定使用 `podcast_drawn_subtitle_stack_v1`，输出 1440x1920 的 3:4 图片，不新增 Template 或 Profile。

## 用户回复

只展示实际设计结果、变更、阻塞和需要决定的内容。不要展示读取清单、逐项 QA、审批证明或流程自证。Plan 首版可以完整展示，后续只展示变更 Scene 和未解决决策。

## 生命周期

- Work 和 Variant 的创建、指针、等待、Park、Draft 注册、Final、Archive 与 Reopen 只通过 `./work` 管理。
- CLI 只管理生命周期和文件一致性；内容判断与视觉选择仍由 Agent 负责，确定性的解析、时间与格式处理交给对应 Skill 脚本。
- Final 是本地交付物，不表示已保存到平台草稿箱或已发布；两者分别需要外部动作，且草稿授权绝不包含发布。

## Release 与 Codex App 部署

- WSL Git 仓只负责开发和构建；Windows Codex App 原生运行 Windows x64 Release，并打开 `%LOCALAPPDATA%\HyperFramesAI\current`。不得把 Windows 旧仓恢复为运行真源。
- Harness Release 使用 `harness-YYYY.MM.PATCH`，只通过 `./release build` 从干净、已标记且与 upstream 同步的提交构建；脚本不代替用户执行 commit、tag 或 push。
- Windows Release 是内置固定 CPython 与依赖的 ZIP。Codex App 解压后只通过 `release.ps1 install` 验证并安装到 `%LOCALAPPDATA%\HyperFramesAI\releases\<tag>`，以 junction 切换 `current` 和 `previous`；回滚只使用 `release.ps1 rollback`。
- Windows 共享 ASR 只通过包内 `asr-wsl.cmd` 调用固定的 `Ubuntu` 和 `/home/jym/workspace/_external/scripts/asr.sh`。桥接器必须拒绝 `D:\AI\AI+hyperframes` 外的输入或输出，并把 WSL 内的 `wslpath` 路径转换、ASR 可用性检查和转录合并为一次 `wsl.exe --distribution Ubuntu --exec /bin/sh -c <fixed-script>` 调用，任务参数经 `WSLENV` 传递，并原样传递 stdout、stderr 与退出码。Windows Codex 沙盒可复用 WSL ASR、模型和 GPU，但未获得包内 `asr-wsl.cmd transcribe-faster` 顶层 argv 前缀的持久授权时，每次 ASR 作业仍可能需要用户审批；不得授权任意 `wsl.exe` 命令。
- `D:\AI\AI+hyperframes` 始终只是 WorkStore。部署只能在其中绑定和维护 `works/` 与 `.runtime/`，不得写入 Harness 源码、运行时或 Release。
- 升级或回滚后新建 Codex App 会话。旧 Release 不自动删除，清理需要单独明确授权。
