# 创作工作流

## 最小启动

Windows 从固定 `workspace/start.ps1` 创建会话，之后使用返回会话目录内的入口，整个会话绑定同一已安装版本；下文 `./work` 在 Windows 对应该目录的 `work.cmd`。`work.cmd doctor` 显示实际绑定，候选启动必须指定 `-Candidate <id> -ReviewRoot <隔离WorkStore>`。WSL 负责 Harness、组件内部和新效果开发，只在明确请求的私有复现副本中调试。Windows 可以编辑本作品文字、Slots、布局、时间和跨 Scene 编排，不修改已安装 Harness 或冻结 vendor。

前台交互运行 `./work current`；后台任务使用已分配的 Work ID 与 Variant ID 显式启动。读取 `WORK.md` 的 `workflow` 后再路由。`hyperframes_video` 只加载当前 Work、Variant、Script、一个 Recipe 和一套 Profile；`podcast_quote_image` 在文章方案批准前加载规划 Skill，批准后加载文案 Skill，且只读取当前阶段的机器产物。已有合格输入时跳过上游步骤。

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

两条路径汇合后，先用最终 Script 的核心主题执行 `./work --work <id> --variant <variant-id> name "<核心主题>"`，再按最终 `SCRIPT.md` 联网研究一手资料并完成同一 Variant 的 `RESEARCH.md`。研究按 Anchor 提供补充事实、可视化机制、边界和来源链接，不替代或反向改写口播。Script Revision 变化时必须刷新 Research Revision，之后才能设计 Animation Plan。

Research 标记为 `ready` 后，创建 Animation Plan 的同一步调用 DBS 完成 `PACKAGE.md`：使用 `dbs-xhs-title` 生成候选并选择 Top 1，再根据最终 Script 与 Research 写一条封面文字、一句话简介和内容概括。内容概括按主要对象或主题简短分项；介绍多个 Skill、工具、功能或案例时逐项单独说明。文档只保留这四项最终结果，不附公式分析或候选清单，也不新增审批门。

进入 Animation Plan 时加载 `hyperframes-anti-ppt`，按当前实际文字、时间边界、Recipe、Profile、Subtemplate 与画幅检查信息完整、阅读窗口和动效关系，不套用统一状态公式。结果合并进同一份 `ANIMATION_PLAN.md`，不新增审批产物。组件的检索、版本、Slots 与安装由视频工作流或组件库能力负责。

已批准的 Component Release 直接读取 `.studio/components/**/COMPONENT.md`，需要真实用法证据时再读取对应 `cases/**/CASE.md` 和边界 Fixture；Case 不扩大公共合同。安装前运行 `./work component validate <component-id>@vN`，用显式 Work/Variant 和 Binding 文件运行 `./work --work <id> --variant <variant-id> component install <component-id>@vN --binding-file <binding.json>`；Plan 批准前限预演用途，增加 `--purpose plan`，仍要求 Script / Research 就绪与 Release 合格。随后用 `component verify` 复算公共源、Work vendor、全部 Scene Bindings 和 `COMPONENT_LOCK.json`。语义简报与匹配理由仍写入 `ANIMATION_PLAN.md`，不创建第二份 Scene 数据库或逐场拒绝清单。没有匹配组件时选择 Plan 内的 `custom:<slug>`，修改内部实现应派生到 Work-local custom，不覆盖冻结 vendor。

### 可执行 Visual Plan

Animation Plan 与 Work-local 场景实现并行形成：所有 Scene 绑定实际上屏文字、关键素材、主要动效与交接，能顺序播放、暂停、拖动和定位。预演沿用正式画布尺寸、字体、布局与时间逻辑；只延后不影响视觉判断的精修。缺失关键素材要记录影响，不能用占位冒充效果通过。文字在源码或 Binding 中维护一份，Plan 引用其位置。

使用现有预览快照入口，不另做演示工程：

```bash
./work --work <id> --variant <variant-id> preview register --purpose plan
./work --work <id> --variant <variant-id> preview open plan-v001 --port 8765
# 用户确认可见效果后执行；记录 Plan 批准，不接受 Draft
./work --work <id> --variant <variant-id> preview accept plan-v001
./work --work <id> --variant <variant-id> preview diff plan-v001
./work --work <id> --variant <variant-id> preview render plan-v001 --output <Work内的draft.mp4>
./work --work <id> --variant <variant-id> preview register <Work内的draft.mp4>
```

Plan 注册不要求先编码 MP4。`preview open` 是使用官方 `hyperframes-player` 的本地前台服务器，不是 Studio 全编辑器；只查看同源快照。`index.html` 顶层 Scene 使用 `id="S01"` 或 `data-scene-id="S01"` 以及 `data-start`、`data-duration`，可选 `data-reading-time` 为 Scene 内秒数，默认中点。视觉意图从 Plan 的 Scene 表投影，不手工维护第二份 Scene 库。静态关键帧辅助正式显示尺寸的阅读检查，不替代动效播放。

受控 Windows 入口自动解析当前会话的 HF 路径；底层 `--hyperframes-dist` / `--hyperframes-cli` 仅用于兼容运行时诊断，不指向 WSL 活跃开发目录。

用户一次确认 Plan 及其源码快照，正式 Draft 沿用同源工程精修，不重新生成已确认场景。正式 Draft 注册与 Final 仍保留原批准检查。`preview render <draft-id> --output <final.mp4> --final` 从 Accepted Draft 渲染并记录实际源码摘要；需重定时时可用 `--refined-project <Variant内目录>` 保留原快照。旧 Work 的既有路径继续兼容。

`verbatim` 的 Animation Plan 直接使用字级转录证据聚合出的原时间戳；源视频或音频仍是最终时间权威。`dbs` 在没有正式音频时才估算时间。

## Windows 与 WSL 请求交接

出现组件内部或新效果缺口时，在当前讨论中形成 `REQUEST.md`，包含希望观众理解什么、行为、保留项、现有能力缺口、实际文字、画幅、阅读窗口、素材与相邻交接、验收输入。能从 Work 获取的信息不重复询问，不新增需求批准门。

Windows 用明确 Work/Variant 冻结请求；`--file` 是允许改变的工程相对路径，`--context-file` 是只读复现输入。源码来自当前工程或指定 `--preview` 快照：

```bash
./work --work <id> --variant <id> request freeze effect-001 --brief <REQUEST.md> --scene S01 --file compositions/S01.html --context-file index.html --preview plan-v001
./work request export <requests/effect-001/r001> --output <WSL私有复现目录>
# WSL 在私有副本实现；patch 内仅包含允许修改的相对路径
./work request deliver <冻结revision目录> candidate-001 --source <patch目录>
# Windows 收到交付后，在原 WorkStore 创建隔离 Review
./work request review <原revision目录> --delivery <交付目录>
./work request feedback <原revision目录> --delivery <交付目录> --note "只调整 S01 的焦点迁移"
# 仅在用户明确接纳后，由 Windows 应用准确交付
./work --work <原id> --variant <原id> request accept <原revision目录> --delivery <交付目录>
```

`review` 返回隔离 WorkStore，使用工作台 `start.ps1 -Candidate <包ID> -ReviewRoot <返回路径>` 开新会话，再注册 `--purpose plan`、播放和测试渲染。Review 不改生产 Current，不允许正式接受、Finalize、归档完成、普通生产安装或平台草稿。请求反馈仍归属准确 revision/交付，不用 WSL 录像代替 Windows 实际执行。

组件交付可在 `deliver` 增加 `--component <package> --binding <binding.json>`；正式接纳另提供 `--approved-component <批准包>`，保留生产准入限制。Work-local 交付不必公共化。`accept` 校验来源与变更范围，不等于 Plan/Draft 接受；其他 Work、未受影响 Scene、原 Accepted Snapshot 与 Final 不自动升级或覆盖。WSL 输出交付和技术结果，Windows 维护请求、反馈和接受决定，不双写同一状态。

## Talking-head

```text
下载/内容输入 -> 选择 dbs 或 verbatim -> 必要时批准 Script
-> RESEARCH.md -> 源视频或用户录制 -> section_map -> Animation Plan + 同源可播放预演
-> 确认 Plan 与预演 -> 同源精修 + Draft
-> 接受 Draft -> Final QA + 60fps high render -> Finalize -> 自动归档
```

## Pure HyperFrames

`verbatim` 下载视频先沿用逐字稿原时间戳；其他没有正式配音的输入才按字数、语速和信息密度估算时间。两者都先完成 `RESEARCH.md`，再制作接近 Final 的无声 Draft。接受 Draft 后接入正式配音时，从对应源码快照继续，只调整时间、停留、转场和元素出现顺序。

已有正式配音时，先生成 `section_map.json`，再完成 Plan、Draft 和 Final。

## 检查点

1. DBS 修改口播正文时批准 `SCRIPT.md`。
2. `RESEARCH.md` 必须与当前 Script Revision 对齐并标记为 `ready`。
3. 创建 Animation Plan 时同步用 DBS 完成 `PACKAGE.md` 的标题、封面文字、一句话简介和内容概括。
4. Plan 批准前用 `hyperframes-anti-ppt` 检查真实内容下的表达与阅读；结果只进入现有 Plan，允许必要的 Work-local HTML 预演。
5. 正式 Draft 前一次确认引用当前 Research Revision 的 `ANIMATION_PLAN.md` 与同源预演快照，不新增 Motion Plan 审批。
6. Draft 提交用户前用 `hyperframes-anti-ppt` 复审成片或代表性关键帧，再按现有流程注册和接受 Draft。
7. Final 前接受一个 Draft 作为视觉基线。

技术 QA、时间微调、换行、easing、性能优化和归档不要求用户批准。

局部反馈可用 `preview diff <id> --scene S02 --range 18.2 23.5 --note "保留正文，只改焦点迁移"` 记录到当前 Variant 的 `.runtime/feedback.json`；不带 `--note` 只读比较。范围使用当前预演的绝对秒数，Scene 可重复指定。记录修改影响与实际投入时沿用这些 Work 备注，不以技术夹具宣称返工下降。

反馈定位到预演/Draft 版本、Scene、必要时间范围或对象。`preview diff <id>` 查看当前工程相对该快照的源码差异；只改受影响 Scene 与必要交接。主构图、隐喻或视觉目标变化只确认变更部分；未受影响源码、冻结资产、原 Accepted Draft 与 Final 不覆盖。正式配音接入优先调整阅读停留，再处理可变动作与交接，不默认整场 `timeScale`，不截断音频或删必要文字。总投入、方向性返工、实际影响范围和有效复用可记入现有 Work 备注；没有真实交付证据时不宣称返工下降。

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
