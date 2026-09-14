# Pure HyperFrames Recipe

## 无正式配音

1. 下载视频先通过共享 ASR 生成 `characters[]` 字级时间戳，再在 `dbs` 与 `verbatim` 中选择文案路径；`dbs` 正文被修改时等待 Script Approval，`verbatim` 保留原文和原时间戳。
2. 按 Script 各部分的呈现需求准备文字、实例与素材，在同一 `RESEARCH.md` 保存研究所得、素材依据及真实待补问题；已有材料足够则复用。Plan 自主取舍，设计中可定点补研究，具体职责见 `.studio/workflow.md`。
3. SCRIPT 索引只保留规划时间预算；`verbatim` 用原时间戳作依据，其他没有正式音频的输入根据字数、参考语速和 Scene 信息密度估算。调用 DBS 完成 `PACKAGE.md`，同时生成引用当前 Research 的全片 Animation Plan：逐 Scene 筛选信息并匹配已接纳资产或组合，只有真实缺口才做实际文字 HTML/CSS 样段，数量可为零；媒体语义占位、主要动作先写方案。
4. Plan 批准后共享已确认主题，局部布局仅在明确匹配的 Scene 复用；先实现最不确定镜头，再逐 Scene 补齐结构、动作和媒体，完成接近 Final 的无声 Draft。默认在官方 Studio 查看工程，登记版本用隔离审阅副本。主模型可直接完成换行、分组和等义精简；独立信息措辞同步回写 Research 研究条目，取舍改变已确认观点或叙事才提交用户。
5. 用户接受 Draft 后接收正式配音，以实测音频生成 `section_map.json`。
6. 从 Accepted Draft 的源码快照继续，工程时间线记录画面实际出现与持续；只调整时间、停留、转场和元素出现顺序。
7. 无法保持可读性时返回 Draft Review，不改变 Scene 语义或 Hero State 强行压缩。

## 已有正式配音

完成文案分流与按呈现需求组织的 `RESEARCH.md` 后沿用音频信息规划布局 Plan，不为静态查看强制同步或运行 ASR；Draft 以实测音频为权威生成 Section Map，工程时间线另记画面实际出现与持续，再完成 Draft、Final 和自动归档。
