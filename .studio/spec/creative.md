# 创作契约

## 文案

- `source.md` 保存主要原始基线，任何改写不得覆盖它。
- `SCRIPT.md` 只包含当前 Variant 的口播正文。使用 `<!-- P001 -->` 形式的稳定 Anchor；批准后新增 Anchor，不重排全部编号。Frontmatter 的 `mode` 只使用 `dbs` 或 `verbatim`。
- `hyperframes_video` 的 `PACKAGE.md` 在 Research 完成、Animation Plan 创建时同步生成，只保存一个最终标题、一条封面文字、一句话简介和内容概括，不进入口播正文。
- 标题必须调用 `dbs-xhs-title` 生成候选并选择 Top 1；封面文字、一句话简介与内容概括基于最终 Script 和 Research，不编造正文没有支撑的承诺。内容概括按主要对象或主题简短分项；介绍多个 Skill、工具、功能或案例时逐项单独说明。
- `dbs` 允许多轮正文修改；DBS 只有在实际修改口播时才把 Script 状态设为 `pending` 并等待用户批准。
- `verbatim` 必须保留转录文字、Anchor 和由 `characters[]` 聚合出的原时间戳，`approval` 为 `not_required`；DBS 不改正文，只可诊断或处理包装文案。
- `podcast_quote_image` 先在 `RESEARCH.md` 中记录与获批观点相关的嘉宾身份、经历、背景故事、事实边界和来源，再生成可直接复制的纯文本 `PACKAGE.md`。第一行为不超过 20 字的标题，其后只使用开篇、`01｜小标题` 形式的顺序分节、正文、署名、`原视频：<视频原标题>` 和标签，不放来源地址、Markdown 标记或结构说明。render 另生成 `xiaohongshu.json`，正文连同 1 至 3 个话题不超过 1000 字，每个话题不超过 30 字。开篇第一段与每图小标题都只归纳获批文段，已核实的嘉宾背景最早从第二段开始补充。文案 Skill 先完成不含大标题的草稿，必须单独调用 `dbs-content` 对开篇、每个小标题和正文进行表达效率、认知落差与标题诊断，再由文案 Skill 应用修订。全文稳定后，必须单独调用 `dbs-xhs-title` 仅根据获批文段生成带公式编号的候选与 Top 3，再选定 Top 1 大标题；最后单独调用 `dbs-ai-check` 诊断完整成稿。仅读取 DBS Skill 或借用规则不算完成调用。DBS 不得改写批准方案中的原文金句或忠实翻译。

## 播客图片

- Hero 与字幕条都从选定视频帧图片的底部向上裁切，不查找或保留源视频中的字幕；只由工作流绘制批准的中英双语文案。
- 1440x1920 画布中所有面板固定使用中文 50px、英文 30px；支撑字幕按双语文本实测高度分配并最多保留 30px 画面，Hero 至少占 60%，字幕条之间无间隙，必要时把水平边距从 6% 收到最低 3%。Hero 与支撑字幕黑底 alpha 分别为 145 和 165；整图保留至少 40% 的无字幕视觉空间。

## Research

- 视频工作流的 `RESEARCH.md` 与 `SCRIPT.md` 位于同一 Variant，记录 `script_revision`、Research Revision、联网来源、可视化机制和事实边界；播客图文的 `RESEARCH.md` 不使用 Script Revision，只服务当前获批文章方案。
- 研究以当前口播 Anchor 为目录，优先查找一手资料；宣传、自述与实际验证必须分开陈述，不编造 UI、功能、数据或成功状态。
- Research 为 Animation Plan 提供组件内容与媒体线索，但不得覆盖 `source.md`、改写 `SCRIPT.md` 或把未经口播表达的事实伪装成口播观点。
- Script Revision 变化后 Research 状态回到 `pending`；完成更新后递增 Research Revision 并设为 `ready`。

## 录制对齐

- 实际视频或音频是时间轴权威，`SCRIPT.md` 是批准文案真源。
- 下载视频的转录 JSON 必须保留每个非空白字符的 `characters[]`；有发音的字符包含 `start`、`end`，未对齐标点显式标记为 `aligned: false`。
- `section_map.json` 继续表达 Script Anchor 的语义分段，但边界从字级时间证据聚合，不得丢弃或覆盖原始 `characters[]`。
- 自然口语差异继续执行；改变事实、论点、段落结构或 Scene 映射时暂停。
- 需要重新说出口的正文修改会使 Recording、Section Map、Plan 和 Accepted Draft 失效。

## Animation Plan

- `ANIMATION_PLAN.md` 是唯一视觉语义真源，正式 HTML 制作前必须为 `approved`。
- Scene 同时引用 Script Anchor 与 `RESEARCH.md` 的对应依据，不复制全文或研究全文。
- Scene 必须给出一个视觉目标、完整可读的 Hero State 和简短运动逻辑。
- `verbatim` Scene 直接使用 `SCRIPT.md` 原时间戳；有实际视频或音频时仍以实际媒体为最终时间权威。
- Scene 数量、顺序、目标、Hero State、Template、Profile 或文案结构变化时，Plan Revision 加一并清除 Accepted Draft。
- 精确时间、easing、换行、安全区、性能和不改变 Hero State 的布局修复不增加 Plan Revision。

## 排除项

v1 不调用图片生成、Prompt 检索或 `design-taste-frontend`，也不生成、管理或烧录传统底部字幕。用户已有静态素材可作为普通媒体引用。
