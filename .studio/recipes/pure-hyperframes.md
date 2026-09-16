# Pure HyperFrames Recipe

## 制作与接受

1. 下载视频先通过共享 ASR 生成 `characters[]` 字级时间戳，再在 `dbs` 与 `verbatim` 中选择文案路径；`dbs` 正文被修改时等待 Script Approval，`verbatim` 保留原文和原时间戳。
2. 按 Script 各部分的呈现需求准备文字、实例与素材，在同一 `RESEARCH.md` 保存研究所得、素材依据及真实待补问题；已有材料足够则复用。Plan 自主取舍，设计中可定点补研究，具体职责见 `.studio/workflow.md`。
3. 按 `.studio/workflow.md` 独立确定动画型/文字型和 Profile。调用 DBS 完成 `PACKAGE.md`，全片 Plan 写清选材、实际屏幕文字、A/B 编排、素材及动作；一个真实 Scene 动态参考与整片 Plan 一次确认方向。生成素材的用途、数量、风格随方向批准，不逐张询问。
4. 方向批准后直接扩成完整占位 Draft，在官方 Studio 查看。允许计划内素材、临时音轨与约定 proxy，不允许空 Scene 或未实现动作；无占位 Draft 接受门。已有音频和原总时长保持，无正式音频才使用 provisional 预算。
5. 正式音频就绪后生成 `section_map.json` 并局部重定时；必需媒体和效果齐备后才接受最终 Draft，不接受无声占位版作为最终音画基线。按主类型检查阅读、交接、关键词强调及2秒全画面静止约束。
6. 无文件参数的 `preview register` 冻结 Studio Draft，`preview open draft-vNNN` 审阅准确隔离副本后 `preview accept draft-vNNN`；无需先导出整片 Draft MP4。
7. 从接受快照 `preview render <draft-id> --output <final.mp4> --final`，完成编码输出 QA、Finalize 与自动归档。按实际影响复核，不重审未变化观点/设计；明确“只导出”等限制优先。

## 已有正式配音

完成文案分流与按呈现需求组织的 `RESEARCH.md` 后沿用音频信息规划布局 Plan，不为静态查看强制同步或运行 ASR；Draft 以实测音频为权威生成 Section Map，工程时间线另记画面实际出现与持续，再完成 Draft、Final 和自动归档。
