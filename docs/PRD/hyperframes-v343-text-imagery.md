# HyperFrames v3.4.3 信息承载、选择性配图与流程更新

日期：2026-09-26

状态：用户已于 2026-09-26 批准，TaskRun `hyperframes-v343-text-imagery` 已实施；WSL 全量隔离回归 277 项（275 通过、2 项 Windows 条件测试跳过），规则包校验与 D2 像素检查通过。未部署、未提交；Windows 原生与生产验证、现有场景源/配方补登记及 Work032 修正未执行，仍由 Windows 按授权完成。

来源：用户粘贴的 Work032 / account-b 调查报告（2026-09-26 对话）；用户提供的 Windows 资产库只读盘点（同日）；本仓 `main@8cb534b` 当前工作树。生产 Work 未读取；`D:\AI\AI+hyperframes\asset-library` 仅做只读结构核对。

版本归属：承接 [v3.4.2 上屏提炼与持续视觉变化](./hyperframes-v342-visual-outcomes.md)，保留其 A1（上屏提炼）、B1（整画面持续变化）、Q1（Draft QA）语义与 D1/D2 诊断；不改变 Work/Variant 生命周期、接受链与无导出边界。

## 1. 目标

1. 文字主导作品的上屏文字承担定义、对象、关系和结论，不再被“提炼”压成短标签。
2. 图片从“默认不生成”改为“Plan 逐段评估、选择性生成”，零图只能是明示的判断结果。
3. 在方向确认前发现上述问题，并由 D1 兜住实现截短 Plan 的情况。
4. 清理已落后于新模型能力（GPT-6 Astra / 6 Sol 等负责 Work Plan）和已成形模板库的流程部分，让 Windows 新开发的资产都能被 Plan 检索到。

## 2. 问题与根因

Work032 / account-b（text-led，等待方向确认，仅有 S06 样段）：

- **文字偏少**：S06 原文“给不同模型厂商和工具服务商定了统一协议”上屏为“统一协议，让双方互通”；合同比喻页面主体是横条；Prompt 场只剩“开头／结构／结尾／语气”。派工 brief 写了 Exact visible information、禁止补充解释，worker 照做。
- **零图片**：Plan 写“生成图片/视频：无”“没有必须生成的位图”；餐厅、合同、命令窗口、流程册全用 Work-local 概念 SVG，未评估情境插画或比喻图的价值。
- **检查未拦住**：QA 只验证资源、文字出现、溢出、seek、音轨与 Lint，连续观感未验证。

共同根因：规则多为历次事故后累积的否定约束，强模型逐字、保守地执行——“防照搬”变成“短标签”，“默认不生成”变成“零图”。否定词密度：`visual-design.md` 约 3.8k 字含 100 个“不”，`workflow.md` 9.9k 字含 141 个，`AGENTS.md` 4.7k 字含 64 个，Plan 模板 5.3k 字含 56 个。

| ID | 落后项 | 证据 |
|---|---|---|
| O1 | `hyperframes-anti-ppt` Skill | 10 行转发壳；名称把目标写成“反 PPT”，`visual-design.md` 还需专门补“不因反 PPT 禁止表格、列表、稳定正文”来抵消。引用：`.studio/capabilities.yaml:6`、Router、`.agents/skills/hyperframes-codex-workflow/scripts/validate_package.py:23`、`tests/test_v33_rules.py:29`、`tests/test_v342_rules.py:45`、`.gitignore:18-19`、`README.md:121` |
| O2 | `visual-design.md` 以禁止项为主 | 「叙事模式」第 3–4 段只防“多”：不得整段复制、拆卡/换词规避、无增量重复删除、可选说明为空即省略；正向只有“不设机械字数上限”。v3.4 design（`.trellis/tasks/09-20-hyperframes-v3-4/design.md:153`）“不能把例外变成整片缺少配图的默认起点”未进入现行 spec |
| O3 | Plan 模板用多列表格承载上屏正文 | `.studio/templates/ANIMATION_PLAN.template.md` §3 把“实际表达”放在 6 列表格单元格中，表格天然诱导短语；§2 共 9 列、§4 共 7 列、§5 共 8 列 |
| O4 | 默认零图 | `AGENTS.md:11` 默认不生成 AI 图片；`.studio/spec/creative.md`「排除项」不默认调用图片生成；`.studio/workflow.md` 内容准备“不强制配图”；Plan 模板 §5“不生成则写无” |
| O5 | 派工 brief 自造更严禁止项 | workflow 派工段只规定摘取内容，未限制 brief 附加约束；Router:43 只附图文互补段与组件查询 |
| O6 | 旧 Profile 包与视频文案默认链 | `capabilities.yaml` 仍登记 design-profile-pack v0.1.0 三个 profile，copywriting default 含 dbs-hook / dbs-script-flow，视频流程实际只用 `dbs` / `verbatim`；`validate_package.py:55` 校验 profiles；Plan 模板 frontmatter 有 `profile` |
| O7a | 查库发生在派工而非 Plan | Router:43、workflow 派工段；Work032 的命令窗口、合同全部自制，而库有 AI 流式对话、手机浏览、卡片家族（8 款卡片）等已批准场景源 |
| O7b | 场景源与配方无法被 CLI 检索 | `work component list`（`.studio/asset_store.py:304`）只覆盖包与登记研究；Windows 手工维护的 `reuse-index.json` 字段异构（`accepted_scenes` 为 9 个 Scene 编号），场景源实际登记在 `asset-library/README.md#参考登记`；`sources/` 77 项混有请求/修复 JSON；`card-family-v1/manifest.json` 已有 `source_ref`、`workflow_role`、`primary_category`、`classification_status`、`entry`，`ai-chat-stream-v6/manifest.json` 只有文件清单 |
| O7c | Three.js / Remotion 表述偏限制 | workflow“Remotion/Blender 仅在确有镜头需要时接入”；visual-design“Three.js 只用于确有必要的空间表达”；库的开发方向正是增加卡片、Three.js 与 Remotion 模板 |

模板库现状（用户提供的 Windows 盘点）：85 个已接纳包版本（80 推荐、5 历史）；42 个表达模块；13 个外观与运动；24 个图标包；11 个未接纳音效；5 个已批准场景源（AI 流式对话 v6、手机浏览 v1、卡片家族 v1、Word Gather v1、Word Wheel v1）用于派生而非直接安装；18 条配方。开发方向：增加卡片、Three.js 与 Remotion 模板，其余按流程关系做 GSAP 或按 Work 缺口补充。资产研究开发只在 Windows 进行。

## 3. 需求

- `V343-REQ-001` **选择性配图**：`AGENTS.md:11`、`.studio/templates/WINDOWS_AGENTS.md:21`、`creative.md`「排除项」、`workflow.md` 内容准备与 Plan 段、Research 模板改为“按 Plan 逐段评估、选择性生成”。Plan 对每个 Scene 写明是否使用图片/真实界面/库内场景源及一句理由，不得以单个“无”跳过；全片零图须在方向确认中明示。选中的生成素材写 Asset Brief，方向批准一并授权；未列用途或明显超量再确认；生成图不冒充真实界面、结果或数据；新外部提供方仍需授权。不设数量配额，不加审批。播客图文的 `excluded_v1.image_generation` 不变。
- `V343-REQ-002` **visual-design 结果优先改写**：按叙事模式先描述“好的结果是什么”，再集中列一段硬边界；删除重复禁止项与“反 PPT”抵消性表述。文字主导正向职责：上屏文字承担定义、对象、关系和结论，写成完整可读信息单元；只剩标签、关键关系全交声音属缺陷；提炼是选关键信息，不等于压短。动效主导保留必要定义、标签、条件和结论。A1/B1/Q1 语义完整保留。Three.js / Remotion 改为“库中有适配模板时优先复用”，长正文留 DOM/SVG，宿主时钟与导出边界不变（O7c）。
- `V343-REQ-003` **Plan 模板重构**：上屏信息改为按信息单元的块，信息 ID 为标题，上屏正文写在 `screen` 代码块中，按实际换行呈现最终上屏样貌；理解目标、视觉职责、声画分工、揭示边界为短字段。整片概览表保留索引列（Scene、A/B、信息 ID、策略、媒体/占位、时间依据），新增每 Scene 的图片/界面/库资产取舍。节拍表与素材表去掉为填表而设的列。frontmatter 去掉 `profile`。旧 Plan 表格格式继续有效。
- `V343-REQ-004` **Plan 阶段检查**：`visual-design.md` 增加 Plan 检查段（文字承担、标签化、图片取舍、库复用、A1/B1）；workflow 规定方向确认按 Scene 展示信息单元与图片取舍，并附该检查的结论；不新增审批或文件。删除 `hyperframes-anti-ppt`（目录、`capabilities.yaml` 条目、Router 提及、`validate_package.py`、`.gitignore`、README、相关测试），Router 在 Plan 与 Draft 阶段直接加载 `visual-design.md`。
- `V343-REQ-005` **派工与查库**：派工 brief 原样转达 Plan 信息块的完整上屏正文，不得附加比 Plan 更严的禁止项（如“禁止补充解释”）或删减；不可行时回报冲突。查库移到 Plan：Plan 按表达需求先用 `work component list` 查包、场景源与配方，再决定复用、派生或 Work-local 自制；文字主导优先考虑卡片类资产。派工只传选中项的精确引用与取用方式。
- `V343-REQ-006` **D1 反向核对**：`preview diagnose` 同时解析新块格式与旧表格格式的 Plan。Scene 已按就绪样本覆盖时，Plan 信息在该 Scene 未出现报 `plan_information_missing`；可见文字是 Plan 表达的真子集或明显更短报 `plan_information_truncated`；其余差异仍为 `plan_implementation_difference`；Scene 未覆盖仍列未验证。不做“文字太少”的质量阈值判定。
- `V343-REQ-007` **场景源与配方的自描述发现**：`work component list` 在已配置 AssetSource 根中额外识别 (a) 带发现字段的场景源 `manifest.json`，(b) 带 front matter 的配方 Markdown。发现字段沿用 card-family 已有集合：`source_ref`、`title`、`purpose`、`tags`、`workflow_role`、`primary_category`、`classification_status`、`entry`（场景源）、`limits`。结果标为派生参考、不可安装，与已接纳包区分；可用 `--kind scene-source|recipe` 过滤。`reuse-index.json` 不作为 CLI 输入。
- `V343-REQ-008` **漏登审计**：`work component list --audit` 报告：疑似资产但缺发现字段的目录（含 `ACCEPTANCE.json`、`entry` 或带 `source_ref` 的 manifest 却缺字段）、描述指向的文件缺失、已接纳包在 `selection.json` 缺 purpose/tags；`doctor` 输出审计摘要。只读，不改资产。
- `V343-REQ-009` **Windows 资产完成定义**：`WINDOWS_AGENTS.md` 与 README 写明：资产开发任务完成指已打包接纳（包）或已写发现字段（场景源/配方），且 `component list --audit` 无该项告警；配方目录需先用 `component source-add` 登记为 AssetSource。现有 5 个场景源与 18 条配方的补字段由 Windows 完成，WSL 不代改。
- `V343-REQ-010` **旧 Profile 与文案默认链**：从 `capabilities.yaml` 默认路由撤下 profiles 与视频 copywriting default（dbs-hook、dbs-script-flow），profile pack 文件保留供旧 Work 兼容；`validate_package.py` 与 Router 同步。播客 copywriting 管道不变。
- `V343-REQ-011` **边界**：不读取或修改生产 Work（含 Work032）、不部署、不提交；Work032 的修正由 Windows 按新规则完成。程序、规则测试、隔离夹具与 Windows 原生/生产验证分别报告。

## 4. 验收

- REQ-001：规则测试确认上述文件不再含“默认不生成 / 不默认调用图片 / 不生成则写无 / 不强制配图”，并含逐 Scene 取舍、零图明示、Asset Brief 授权与不冒充证据语义。
- REQ-002：规则测试确认文字主导正向职责、标签化缺陷、提炼≠压短、A1/B1/Q1 关键语义与 Three.js/Remotion 优先复用语义存在；“反 PPT”抵消句与重复禁止项移除；否定词密度下降作为观察值报告，不作通过门槛。
- REQ-003：模板含 `screen` 信息块、逐 Scene 图片/库资产取舍字段，无 `profile` 字段，不再有承载正文的表格单元格。
- REQ-004：`hyperframes-anti-ppt` 与全部引用移除，包校验与规则测试通过；workflow 方向确认段含信息单元、图片取舍与 Plan 检查结论。
- REQ-005：workflow 与 Router 含“原样转达、不附加更严禁止项”与“Plan 阶段查库”，派工段不再承担发现。
- REQ-006：隔离夹具覆盖新块格式与旧表格格式；缺失、截短、其他差异、未覆盖四类各有用例，v3.4.2 D1 用例保持通过。
- REQ-007：隔离 AssetSource 夹具中带字段的场景源与配方可被 `--query`、`--kind` 检出且标为不可安装；无字段条目不出现在结果中；包发现结果不变。
- REQ-008：审计在夹具中报出缺字段目录、失效路径、缺 purpose/tags 的已接纳包，不误报请求/修复 JSON 文件；`doctor` 含摘要；审计不写文件。
- REQ-009：`WINDOWS_AGENTS.md` 与 README 含完成定义与 `source-add` 配方目录说明。
- REQ-010：`capabilities.yaml` 无 profiles 与视频 copywriting default，profile pack 仍在，包校验通过；播客管道条目不变。
- REQ-011：无生产 WorkStore 读写（本次只读核对资产库结构除外）、无部署、无提交；全量隔离回归通过。

## 5. 不在本轮

- 不修正 Work032 或任何生产 Work；不迁移、不批量改写历史 Plan；不代 Windows 给现有场景源/配方补字段。
- 不设机械字数、图片数量或覆盖率配额；不新增审批阶段或文件；不做“文字太少”自动判定。
- 不新增生图 Skill 或 Prompt 库；不部署、不提交、不 push。
