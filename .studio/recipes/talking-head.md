# Talking-head Recipe

1. 基于输入运行所需 DBS 文案能力；正文被修改时等待 Script Approval。
2. 用户按 `subject_position: left|center|right` 录制人物视频。
3. 用实际音频与 Script Anchor 对齐，生成 sentence-level `section_map.json`。
4. 生成并讨论 `ANIMATION_PLAN.md`；人物视频持续作为主视觉，HyperFrames 负责信息增强。
5. Plan 批准后实现 HTML、运行 Draft QA 并注册 Draft。
6. 用户接受 Draft 后，从该源码快照完成 Final QA、60fps high render 和 Finalize。

录制完成后 DBS 不默认重写已经说出口的正文；标题、封面、发布说明和屏幕关键词仍可继续处理。
