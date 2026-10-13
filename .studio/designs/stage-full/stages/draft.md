# stage-full · Draft 阶段指南

## 机制与实现

- 文件：`example/index.html` + `example/style.css` + `example/scene.js` + 卡内资产 `assets/stage-rig/stage-rig.js`（四块墙板、内对 ±86°、外板反向 ∓172°、地面桥 -90°、道具脚 88°，先内后外分级展开）。
- 四层：第 1 层 `background`、第 2 层 `stage`、第 3 层 `overlay`（`#spot-a/#spot-b`、因果指示线、吊灯横杆）、第 4 层 `text`；无第 5 层（示例静音）。
- 单一 paused 主时间线注册到 `window.__timelines['stage-full-example']`，同一条交给 `HarnessScene.bindScene`；无 RAF / play / autoplay / Date / Math.random。
- 外部 seek：`window.__example.seek(t)` 直接重建完整状态，`dispose()` 解绑并 kill 时间线；不依赖 seek 事件或回调。

## 资源闭包、字体与释放

- 资源闭包：只依赖宿主放好的 `runtime/gsap.min.js`、`runtime/scene-binding.js`、`runtime/stage-rig.js` 与 `media/SourceHanSansCN-Regular.otf`；无图片、音频、字体下载与新依赖。
- 字体：`document.fonts.ready` 就绪后才首次渲染；`@font-face` 只指向 `media/SourceHanSansCN-Regular.otf`，`font-display:block`；不使用网络字体或系统回退排版。
- 布局：固定 1920×1080；五层各占一层，第 3 层不遮挡第 4 层正文；文字只在阅读窗口内保持稳定。

## 具体技术检查

- 确定性 seek：正放、倒放、随机 seek、重复 seek 一致；对 `[t3, 0, t1, t3]` 抓帧比较同一时刻。
- 释放：`dispose()` 解绑并 kill 时间线后不再响应 seek。
- 声音：示例静音；若某 Variant 需要音效，只为结构重击与关键 hit（如 S4 折叠落定、S3 归位轻点）配音效，不给普通入场自动配音效、不要 BGM；所有 cue 对应同帧可见事件并按 `data-start` 调度以保证 seek 安全。
- 不新增几何/函数预置、通用角色库、AI 概念图库或 BGM 生成。
