# Talking-head Recipe

1. 下载视频先通过共享 ASR 生成 `characters[]` 字级时间戳，再在 `dbs` 与 `verbatim` 中选择文案路径；`dbs` 正文被修改时等待 Script Approval，`verbatim` 保留下载视频的原文和原时间戳。
2. 按 Script 各部分的呈现需求准备文字、实例与素材，在同一 `RESEARCH.md` 保存研究所得、素材依据及真实待补问题；已有材料足够则复用。Plan 自主取舍，设计中可定点补研究，具体职责见 `.studio/workflow.md`。
3. 按 `.studio/workflow.md` 独立确定动画型/文字型与 Profile，调用 DBS 完成 `PACKAGE.md`，全片 Plan 写清实际屏幕文字、A/B、素材与动作。一个真实 Scene 动态参考与整片 Plan 一次确认方向；人物布局不强加 B-roll，缺媒体可用语义占位，不为规划强制录制或 ASR。生成素材的用途、数量、风格随方向批准。
4. Plan 批准后，没有可用人物视频时用户按 `subject_position: left|center|right` 录制；已有源视频直接使用。
5. 用实际音频的字级时间证据与 Script Anchor 对齐，生成语义分段的 `section_map.json`；工程时间线另记画面实际出现与持续。
6. 方向批准后扩成全片占位 Draft，无额外接受门；补齐必需素材、正式音频与动作，保留原声和总时长。Studio 检查声音、连续播放、跳转/回拖、阅读及2秒全画面静止约束。无文件参数的 `preview register` 登记最终 Studio Draft，`preview open draft-vNNN` 审阅准确副本后 `preview accept draft-vNNN`，不先导出整片 Draft MP4。
7. 从接受快照 `preview render <draft-id> --output <final.mp4> --final` 完成正式渲染，再编码输出 QA、Finalize 和自动归档；局部变化只复核影响范围，不重复未变化内容的审美批准。

录制完成后 DBS 不默认重写已经说出口的正文；标题、封面、发布说明和屏幕关键词仍可继续处理。
