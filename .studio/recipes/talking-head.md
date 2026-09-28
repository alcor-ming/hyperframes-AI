# Talking-head Recipe

仅记录 `talking_head` 的结构差异；四阶段、接受与交付见 `.studio/workflow.md`，表达检查见 `.studio/spec/visual-design.md`。

A-roll 为真人出镜，B-roll 为展示内容、图片等辅助素材，均在第 2 层；B 接管时保护人脸区。按创作指南编排 A → B → A 或 A → B；真人出镜区间不受 2 秒事件上限约束，B-roll 仍按节奏合同执行。主声源贯穿切换，只选人物视频音轨或外置配音之一，避免重复叠播。

已有源视频和 section_map 直接复用。确需新录制时在方向确定后按 `subject_position: left|center|right` 录制，源音频的字级证据决定对齐；不为规划强制录制或 ASR。录制后 DBS 不默认改写已经说出口的正文，实质改稿按录制失效合同处理。
