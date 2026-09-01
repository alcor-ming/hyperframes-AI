# Talking-head Recipe

1. 下载视频先通过共享 ASR 生成 `characters[]` 字级时间戳，再在 `dbs` 与 `verbatim` 中选择文案路径；`dbs` 正文被修改时等待 Script Approval，`verbatim` 保留下载视频的原文和原时间戳。
2. 按最终 Script 联网研究并完成同一 Variant 的 `RESEARCH.md`。
3. 没有可用人物视频时，用户按 `subject_position: left|center|right` 录制；已有源视频时直接使用。
4. 用实际音频的字级时间证据与 Script Anchor 对齐，生成语义分段的 `section_map.json`。
5. 调用 DBS 完成 `PACKAGE.md`，同时生成引用当前 Research Revision 的 `ANIMATION_PLAN.md`；人物视频持续作为主视觉，HyperFrames 负责信息增强。
6. Plan 批准后实现 HTML、运行 Draft QA 并注册 Draft。
7. 用户接受 Draft 后，从该源码快照完成 Final QA、60fps high render 和 Finalize。

录制完成后 DBS 不默认重写已经说出口的正文；标题、封面、发布说明和屏幕关键词仍可继续处理。
