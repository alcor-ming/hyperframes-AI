# 创作工作流

## 最小启动

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

Research 标记为 `ready` 后，创建 Animation Plan 的同一步调用 DBS 完成 `PACKAGE.md`：使用 `dbs-xhs-title` 生成候选并选择 Top 1，再根据最终 Script 与 Research 写一条封面文字和一句话简介。文档只保留这三项最终结果，不附公式分析或候选清单，也不新增审批门。

`verbatim` 的 Animation Plan 直接使用字级转录证据聚合出的原时间戳；源视频或音频仍是最终时间权威。`dbs` 在没有正式音频时才估算时间。

## Talking-head

```text
下载/内容输入 -> 选择 dbs 或 verbatim -> 必要时批准 Script
-> RESEARCH.md -> 源视频或用户录制 -> section_map -> Animation Plan
-> 批准 Plan -> HTML + Draft
-> 接受 Draft -> Final QA + 60fps high render -> Finalize -> 自动归档
```

## Pure HyperFrames

`verbatim` 下载视频先沿用逐字稿原时间戳；其他没有正式配音的输入才按字数、语速和信息密度估算时间。两者都先完成 `RESEARCH.md`，再制作接近 Final 的无声 Draft。接受 Draft 后接入正式配音时，从对应源码快照继续，只调整时间、停留、转场和元素出现顺序。

已有正式配音时，先生成 `section_map.json`，再完成 Plan、Draft 和 Final。

## 检查点

1. DBS 修改口播正文时批准 `SCRIPT.md`。
2. `RESEARCH.md` 必须与当前 Script Revision 对齐并标记为 `ready`。
3. 创建 Animation Plan 时同步用 DBS 完成 `PACKAGE.md` 的标题、封面文字和一句话简介。
4. 正式 HTML 制作前批准一份引用当前 Research Revision 的 `ANIMATION_PLAN.md`。
5. Final 前接受一个 Draft 作为视觉基线。

技术 QA、时间微调、换行、easing、性能优化和归档不要求用户批准。

## 播客金句图

```text
来源 URL -> trendradar-media -> 校验并复制到 materials/
本地或已下载视频 + 可选原生转录/字幕 -> resolve transcript
-> 自动命名为三位序号 + 嘉宾名 + 核心主题
-> 规划 Skill 通读原文并生成 3 个完整文章方案
-> DBS 检查核心机制、受众情绪与传播理由 -> 用户批准 1 个方案
-> 文案 Skill 调研嘉宾背景并完成 RESEARCH.md
-> 先写开篇、每图小标题与第三人称正文，最后拟定大标题并通过 DBS 检查
-> align time -> 每条 Hero/支撑句抽取 3 张候选帧 -> Agent 选帧
-> 从视频帧图片底部向上裁切并绘制紧凑双语字幕，render 8 至 12 张图
-> 生成小红书标题、纯文本正文、话题与有序图片清单
-> Agent 视觉 QA -> Finalize -> 自动归档 -> 经明确授权可保存到创作者平台草稿箱
```

字幕在覆盖区间内拥有文案和时间权威，转录只补无字幕区间；同语种明显冲突必须先人工处理。转录条件缺失或失败时进入 `waiting_user`，由用户决定是否改用保留原画面字幕的 fallback，不得静默降级。

每个文章方案包含 8 至 12 个按原文结构排列的图片组，每组固定 1 条 Hero，并用若干约 10 个汉字的完整支撑短句推进内容；中文总字数以 60 至 90 字为目标区间，不设逐句硬上限。同一内容可按语义拆成相邻两张图，图片只保留核心结论与必要论证，背景、案例和完整推导写入 `PACKAGE.md`。图片边界跟随原文的铺垫、观点、论证、例子、对比与收束，不按标点机械切分。用户批准 1 个文章方案是唯一内容门；批准后不得重新解释原文或另提方向。`RESEARCH.md` 只调研与获批核心相关的嘉宾身份、经历、背景故事和事实边界。全部面板绘制 50px 中文与 30px 英文；支撑条按双语文本实测高度分配并最多保留 30px 画面，Hero 至少占 60%，必要时把水平边距从 6% 收到最低 3%。Hero 与支撑字幕黑底 alpha 分别为 145 和 165。各面板从选定视频帧图片底部向上裁切，字幕条之间无间隙，整图至少保留 40% 无字幕空间。`PACKAGE.md` 直接使用可复制的纯文本：第一行为标题，其后为开篇、`01｜小标题` 形式的分节、正文、署名、`原视频：<视频原标题>` 和标签；render 只负责分离标题、正文、1 至 3 个话题和有序图片，正文连同话题不超过 1000 字。只有用户对准确 Work/Variant 明确授权后，才可用已登录浏览器保存草稿；不点击发布。

候选阶段用 `dbs-resonate` 检查每个方案是否只服务一个核心机制；`dbs-spread` 只提供受众情绪、有效立场和第一传播者信号，用于候选理由与排序，不改写原文。文案阶段先用 `dbs-content` 检查开篇、每图小标题与正文的表达效率和认知落差；全文稳定后才用 `dbs-xhs-title` 选择结合核心总结与嘉宾背景、不超过 20 字且不超出证据的 Top 1 标题，最后执行必做的 `dbs-ai-check`。`dbs-hook` 与 `dbs-script-flow` 不进入本工作流。

URL 获取只调用外部 `trendradar-media` v2.0。适配器只接受成功 envelope 与单条成功 manifest，复核大小和 SHA-256 后原子复制到 `materials/source-video.*`，并保存不含外部临时路径的 `materials/acquisition.json`。YouTube 可先采用带结构化时间戳的原生转录；不可用时才在用户明确同意后调用共享 ASR。下载器本身不提供转录。

## 状态

Variant 只使用 `active`、`waiting_user`、`waiting_asset`、`parked`。具体阶段由文件、`wait_for` 和 `next_action` 推导；归档由目录位置表达。
