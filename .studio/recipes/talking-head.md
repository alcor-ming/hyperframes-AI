# Talking-head Recipe

1. 下载视频先通过共享 ASR 生成 `characters[]` 字级时间戳，再在 `dbs` 与 `verbatim` 中选择文案路径；`dbs` 正文被修改时等待 Script Approval，`verbatim` 保留下载视频的原文和原时间戳。
2. 用 SCRIPT 的非口播 Scene 索引定位实际信息缺口，按需研究并在同一 `RESEARCH.md` 保存资料依据与采用信息；可以无新增研究，不为过渡凑资料。
3. 调用 DBS 完成 `PACKAGE.md`，同时生成引用当前 Research 采用条目的全片 `ANIMATION_PLAN.md` 和一个代表性实际文字 HTML/CSS 布局样段；SCRIPT 索引只记规划时间预算，人物视频持续作为主视觉，样段可用语义媒体占位和估算时间，不为查看布局强制录制或 ASR。
4. Plan 批准后，没有可用人物视频时用户按 `subject_position: left|center|right` 录制；已有源视频直接使用。
5. 用实际音频的字级时间证据与 Script Anchor 对齐，生成语义分段的 `section_map.json`；工程时间线另记画面实际出现与持续。
6. 复用已确认文字、样式和有用代码，优先实现不确定镜头再补齐全片动作与媒体。主模型直接处理换行、分组和等义精简并同步 Research 采用条目；删除核心信息或改变结论才提交局部取舍。运行完整 Draft QA 并注册 Draft。
7. 用户接受 Draft 后，从该源码快照完成 Final QA、60fps high render 和 Finalize。

录制完成后 DBS 不默认重写已经说出口的正文；标题、封面、发布说明和屏幕关键词仍可继续处理。
