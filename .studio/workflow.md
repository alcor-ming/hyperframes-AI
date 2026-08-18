# 创作工作流

## 最小启动

运行 `./work current`，读取 `WORK.md` 的 `workflow` 后再路由。`hyperframes_video` 只加载当前 Work、Variant、Script、一个 Recipe 和一套 Profile；`podcast_quote_image` 只加载当前 Work、Variant、PACKAGE 与对应 Skill。已有合格输入时跳过上游步骤。

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

两条路径汇合后，按最终 `SCRIPT.md` 联网研究一手资料并完成同一 Variant 的 `RESEARCH.md`。研究按 Anchor 提供补充事实、可视化机制、边界和来源链接，不替代或反向改写口播。Script Revision 变化时必须刷新 Research Revision，之后才能设计 Animation Plan。

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
本地视频 + 可选转录/字幕 -> resolve transcript
-> Agent 筛选并翻译 6 组候选 -> 用户批准 3 至 4 组
-> align time -> 每条抽取 3 张候选帧 -> Agent 选帧
-> PACKAGE.md -> 固定版式 render -> Agent 视觉 QA -> Finalize -> 自动归档
```

字幕在覆盖区间内拥有文案和时间权威，转录只补无字幕区间；同语种明显冲突必须先人工处理。转录条件缺失或失败时进入 `waiting_user`，由用户决定是否改用保留原画面字幕的 fallback，不得静默降级。

每组固定 5 条双语文字：主画面金句加 4 条连贯字幕。用户批准是唯一内容门；批准后只做确定性对齐、取帧、渲染和视觉 QA。首张使用批准候选中排名最强的一组，其余按来源时间排序。图片只保留金句，人物、节目、期数和来源放入 `PACKAGE.md`。

本仓库不实现下载器，也不为未来下载工具预留空接口。当前输入只接受本地视频和可选转录/字幕；共享 ASR 仅在用户明确同意运行时调用。

## 状态

Variant 只使用 `active`、`waiting_user`、`waiting_asset`、`parked`。具体阶段由文件、`wait_for` 和 `next_action` 推导；归档由目录位置表达。
