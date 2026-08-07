# HyperFrames Implementation Contract

## 项目探测

- 先阅读完整现有 composition、Profile 和媒体结构。
- 现有项目直接扩展。
- 只有没有项目骨架时才使用 `npx hyperframes init <project> --non-interactive`。

## 视觉来源

- 读取稳定 Profile，并建立或引用 `DESIGN.md`。
- 不使用默认蓝色、Roboto 或临时通用 UI 风格替代 Profile。
- 同一项目只使用一个 Profile。

## Hero State First

每个 Scene：

1. 先写静态 HTML/CSS，使所有主要元素处于最完整可读状态；
2. 检查画布、换行、容器、人物和字幕保护区；
3. 再使用 `gsap.from()` 添加入场；
4. 用转场处理场景离开；最终场景才允许独立退出动画。

内容容器使用全画布布局、padding、flex/grid 和 gap。绝对定位主要留给装饰元素，不用固定 1920×1080 容器硬编码横竖屏。

## Timeline

- 所有 timeline 使用 `{ paused: true }`；
- 注册到 `window.__timelines`；
- composition 时长由 `data-duration` 定义；
- 视频必须 `muted playsinline`，音频使用单独 `<audio>`；
- 使用 `data-track-index`，不使用 `data-layer`；
- 不异步构建 timeline；
- 不使用 `Math.random()`、`Date.now()` 或非确定性逻辑；
- 不使用 `repeat: -1`；
- 不让多个 timeline 同时修改同一元素的同一属性。

## 场景与计划对应

- composition、scene 容器或代码注释保留 `S01` 等 Scene ID；
- `quiet_hold` 也作为明确 Scene；
- 口播模板需要清空叠加层时，过渡到 `quiet_hold`，不要在转场前逐个执行退出动画；
- 结构性实现偏离必须回到 Animation Plan 讨论。

## 文字与资产

- 文字自然换行，不机械插入 `<br>`；短展示标题的刻意断行除外。
- 动态文本使用 `fitTextFontSize` 或等价适配。
- 外部媒体添加 `crossorigin="anonymous"`。
- 图片只承载非精确信息；文字、UI、路径和数据由 HTML/SVG 渲染。

## 输出

- 默认请求比例：16:9 为 1920×1080，9:16 为 1080×1920；保持原比例时使用项目配置。
- 最终输出 60fps。
- draft 用于内部迭代，high 用于最终交付。
