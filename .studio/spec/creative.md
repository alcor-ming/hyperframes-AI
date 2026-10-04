# 创作契约

## 文案

- `source.md` 保存主要原始基线，任何改写不得覆盖它。
- `SCRIPT.md` 保存当前 Variant 引用的唯一口播正文；新视频 Work 默认通过 `shared_inputs` 引用 Work 的 `shared/`，显式内容分支使用 CLI 定位的文件。正文可附明确排除出口播的简短 Scene 索引，使用 `<!-- P001 -->` 形式的稳定 Anchor；批准后新增 Anchor，不重排全部编号。索引用成对的 `<!-- scene-index:start -->` / `<!-- scene-index:end -->` 包围，只记录 `Scene | Anchor 范围 | 时间预算 | 本段内容 / 观众重点`，不进入纯文本阅读、字数统计、配音或语音对齐。Frontmatter 的 `mode` 只使用 `dbs` 或 `verbatim`，不同于 Variant 的叙事模式。
- `hyperframes_video` 的 `PACKAGE.md` 仅在交付要求包含发布包装时生成，保存最终标题、封面文字、一句话简介和内容概括，不进入口播正文，也不作为视频前置。
- 已要求的包装标题基于实际交付需求生成候选并选择 Top 1；封面文字、一句话简介与内容概括基于最终 Script 和 Research，不编造正文没有支撑的承诺。内容概括按主要对象或主题简短分项；介绍多个 Skill、工具、功能或案例时逐项单独说明。
- `dbs` 允许多轮正文修改；DBS 只有在实际修改口播时才把 Script 状态设为 `pending` 并等待用户批准。
- `verbatim` 必须保留转录文字、Anchor 和由 `characters[]` 聚合出的原时间戳，`approval` 为 `not_required`；DBS 不改正文，只可诊断或处理包装文案。

## Research 与信息归属

- 视频 `RESEARCH.md` 在 Work 级，由各 Variant 共享；记录 Script / Research revision，按段落或 Anchor 组织事实与来源、B-roll 候选（位置与取得状态）、比喻与例子。只在真实缺口存在时记录待补问题，研究不规定布局、动画或成片秒数。
- Research 是候选材料，逐 Scene Plan 内嵌的 `screen` 是采用后屏幕正文的唯一真源，不为等义编辑回写第二份 Research 文案。来源线索不等于已取得素材；源视频证据时间点不是成片显示时间。
- Studio 改稿同步 Plan 实际表达。换行、分组、等义精简与表现标签直接调整；因果、比较对象、必要数值、单位、归属或证据边界变化先核对权威来源。新增事实定点补研究，只把改变确认结论或叙事的部分交用户判断。
- 共享 Script revision 变化后检查引用 Variant 的实际影响，只更新受影响条目及引用元数据；保留未受影响资料与接受快照。已归档版本的接受快照和旧成片不随共享稿变化；恢复该版本后按新输入检查，不沿用旧接受作为新内容批准。

## 录制对齐

- 实际视频或音频是时间轴权威，`SCRIPT.md` 是批准文案真源。
- 区分三类时间：SCRIPT Scene 索引只给规划预算；正式音频与 `section_map.json` 保存实测时间；工程时间线决定画面实际出现与持续。Plan 只记录时间依据和必要节奏意图，不维护另一份精确时间表。
- 下载视频的转录 JSON 必须保留每个非空白字符的 `characters[]`；有发音的字符包含 `start`、`end`，未对齐标点显式标记为 `aligned: false`。
- `section_map.json` 继续表达 Script Anchor 的语义分段，但边界从字级时间证据聚合，不得丢弃或覆盖原始 `characters[]`。
- 自然口语差异继续执行；改变事实、论点、段落结构或 Scene 映射时暂停。
- 需要重新说出口的正文修改会使对应 Recording、Section Map 与引用画面失效；仅同步受影响 Scene 及必要衔接。旧 Accepted Draft 保持不变，新 Draft / Final 仍须经过现有适用性与快照校验。

## Animation Plan

`ANIMATION_PLAN.md` 以全片方向加逐 Scene 一节维护设计，元信息由 CLI 从 Variant 与 lock 生成；概览只作索引，每场的 `screen` 保留信息 ID、来源、理解目标与揭示 cue。声音使用 `sound` JSON 导出。采用 [创作指南](visual-design.md) 的 A/B-roll、五层与节奏合同，阅读区域稳定。

`showcase` 改用精简 `SHOWCASE_PLAN.template.md`，不套用 explainer 正向方向、D14、Q1 与节奏必经闭环；硬约束见 [showcase.md](showcase.md)。`math-rap` 的 Research 使用 `MATH_RESEARCH.template.md` 登记原片、原作者、片段及声音来源，不新增账号或声音来源门禁；Plan 的数学职责、符号与歌词时间依据见 [math-rap.md](math-rap.md)。

Scene 数量、顺序、目标、Hero State、Template、整体主题、文案结构或核心内容实质变化时更新 Plan revision，只重新确认受影响 Scene 及必要衔接。精确 timing、easing、换行、安全区、性能和不改变 Hero State 的布局修复无需新的方向确认；成果与稳定 ID 保留。工程不是另一份文案真源。

生命周期见 [workflow.md](../workflow.md)，权限见根 [AGENTS.md](../../AGENTS.md)；实现与 QA 在 Draft 阶段加载 [hyperframes.md](hyperframes.md)。
