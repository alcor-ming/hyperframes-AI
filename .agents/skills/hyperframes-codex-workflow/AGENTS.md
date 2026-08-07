# AGENTS.md — Codex 执行规则

## 任务目标

在不修改三套稳定设计 Profile 核心语言的前提下，使用本工作流完成 HyperFrames 视频规划、讨论、资产制作、实现和渲染，或将该工作流集成到现有项目。

## 开始前的读取顺序

1. `CODEX_TASK.md`
2. `DECISIONS.md`
3. `WORKFLOW.md`
4. 对应模板文档
5. `docs/animation-plan-contract.md`
6. `docs/discussion-protocol.md`
7. 选定 Profile 的真实文件
8. 实现阶段再读取 `docs/implementation-contract.md` 与 `docs/quiet-qa.md`

不要在每次回复中复述这些规则。

## 已锁定边界

- 只有 `talking_head` 与 `pure_hyperframes` 两套模板。
- 不创建、不恢复字幕专用模板。
- 字幕是可选组件，不是模板。
- 三套 Profile 已稳定，只接入，不重新设计：
  - `optical_fluidity`
  - `kami_editorial`
  - `monochrome_atelier`
- `section_map.json` 可读取、可生成、可复用，但永远不是必需输入。
- `pure_hyperframes` 允许在 Animation Plan 批准后录音或生成 AI 配音。
- 图片资产是可选项；只有计划中已定义用途的资产才生成。
- Animation Plan 必须与用户讨论，并在明确批准后才能执行正式制作。

## 用户可见回复的节制规则

规划阶段只输出：

1. 精简 Plan Header；
2. Scene Table；
3. Optional Asset Brief；
4. 确实影响设计的待决策项。

不要输出：

- “我已遵守……”或类似自证；
- Profile、模板和假设的逐条复述；
- 合规清单、审批证明、计划哈希；
- 没有实际问题时的风险清单；
- 确认前的 Implementation Changes；
- 确认前的完整 Test Plan；
- 全部通过的 QA 明细。

首次规划应直接提交一版可讨论草案。存在重要歧义时，把合理默认值写入草案，并在末尾给出不超过 3 个待决策项；不要先用大量问题阻塞计划。

用户反馈后：

- 原地更新同一份 `ANIMATION_PLAN.md`；
- 回复只说明变更过的 Scene、资产或决策；
- 不重新输出未变化的长篇规则；
- 继续讨论，直到用户明确批准。

## 执行门槛

计划批准前不得：

- 开始正式 composition HTML 实现；
- 批量生成最终图片资产；
- 生成最终 AI 配音；
- 渲染正式视频。

允许进行素材读取、转录、技术探测、时长分析、计划草拟和资产 Brief 设计。

用户使用自然语言明确表达“确认、批准、按此执行”等含义，即视为批准。无需要求固定口令。

## 批准后的执行顺序

1. 锁定已批准的场景顺序、信息目标和 Hero State。
2. 仅在计划需要时生成图片资产。
3. 对 `pure_hyperframes`：在需要时生成或接收最终配音，并据真实音频更新时间码。
4. 不改变场景语义的时间微调无需再次批准。
5. 先完成每个 Scene 的静态 Hero State，再添加 GSAP 动画。
6. 运行静默 QA，自动修复可修复问题。
7. 交付预览与最终渲染；只报告实质调整和未解决阻塞。

## 必须重新讨论的变更

- 增加、删除或重新排序 Scene；
- 改变 Scene 的核心信息目标；
- 更换 Profile 或模板；
- 将局部叠加改为全屏插入，或反向改变；
- 改变叙事结论；
- 新增会改变 Hero State 的主要图片资产；
- 删除、重写已批准的关键旁白段落。

以下变更不需要重新确认：文字避让、字号适配、轻微时间调整、easing 调整、图片重生成、性能优化、溢出修复、音频生成后按真实长度重定时。

## 仓库适配原则

- 先读取现有代码和目录，不机械覆盖。
- 已有 HyperFrames 项目直接扩展；仅在不存在项目骨架时使用 `npx hyperframes init`。
- 不复制三套 Profile 形成第二套来源。
- 不把本工作流改造成复杂审批系统、任务状态机或审计框架。
- 使用最小必要代码满足两套模板和一次计划确认门槛。
