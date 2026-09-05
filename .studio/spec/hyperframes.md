# HyperFrames 实现与 QA

## 实现

- 一个 Variant 只读取一个 Profile。
- Work-local 预演与 Plan 并行实现：先确认各阅读状态的真实内容与排版，再编排 GSAP；正式 Draft 精修同源代码，不另写演示版。
- Timeline 必须同步、确定性构建，使用 `{ paused: true }` 并注册到 `window.__timelines`。
- 动作不依赖 `Math.random()`、`Date.now()`、实时 delta、异步 Timeline、`repeat: -1` 或多个 Timeline 同时修改同一属性；可用固定 seed 初始化数据，再按时间直接求值。
- composition 或 Scene 保留 `S01` 等稳定 ID；结构性偏离返回 Animation Plan。
- `talking_head` 保持人物视频为主视觉；只依据 `left|center|right` 预留位置，明确阻塞时才检查代表帧。
- 在不牺牲单场主焦点和可读性的前提下，优先把 `RESEARCH.md` 中的机制做成多个有语义的动效组件，并使用更丰富但 seek-safe 的 GSAP 动画；不为增加数量堆装饰。
- 动效按表达需要组织焦点、关系、证据、对象转化与交接，不要求每组件独立入场。稳定阅读贯穿 Scene，不以统一结尾停顿代替；只有可定义的真实进度才使用进度条，演示值明确标记。
- Scene 布局必须预留明确的图片/视频位和必要文案位；缺少素材时保留稳定 Slot，不用虚构素材填满。
- Skill 讲解按需要使用真实截图与完整解释；允许对比、列表、左右分栏和稳定证据页，按真实文字与音频安排阅读，不强迫每场发生变形。

## 混合时间与资源

- 先核对本地 HyperFrames / GSAP / Three.js 版本与适配器，优先复用已有 `hf-seek` / `window.__hfThreeTime` 接口；上游存在不代表当前安装可用。
- DOM / GSAP 与 WebGL 共用全局时间，明确 Scene 偏移和局部重定时；同帧先求值属性、镜头与 shader，再绘制。成片动作不能以独立 RAF 或 `setAnimationLoop()` 为时间权威。
- 渲染关键状态不能仅放在 `onUpdate` / `onComplete` 回调；随机 seek 可能抑制回调。Flip、拆字与布局状态在字体/资源就绪后固定，不在播放回调中才补正文。
- 优先复用返回有限 Timeline 的小函数或既有效果注册接口，不另建引擎。效果只暴露实际需要的配置，由宿主控制尺寸、主题、资源、seed 与时间；文字默认 DOM / SVG，效果不拥有全局叙事。
- Three.js 与 addons 固定同版本，画布尺寸、像素比与色彩配置由工程控制。纹理、shader、模型、效果代码及其他实际依赖进入现有快照闭包，抓帧不临时联网；提供就绪与释放行为，不释放他人共享资源。
- 不引入依赖历史帧的物理模拟、反馈 shader 或累积拖尾，除非可重建任意时刻或已烘焙。Three.js 故障只阻塞相关 Scene，不静默以静态图冒充通过；主视觉替代沿用局部确认边界。

预演和混合效果验证应实际播放、暂停、拖动、倒跳、再播放；固定环境按 `[t3, 0, t1, t3]` 抓帧比较同一时刻，并实际渲染短片核对 DOM 与 WebGL 同帧。验证全 Scene 覆盖、交接、资源就绪、切换释放和正式画布阅读。Mock 或静态检查不算渲染通过；技术样例不算真实生产复用。无关公共库更新不得使已冻结 Work 失效。

需要混合求值时，可将 `.studio/runtime/scene-binding.js` 复制到 Work 的 `project/runtime/`，由 `HarnessScene.bindScene({start, duration, timeline, ready, renderAt, dispose})` 接到当前 HyperFrames 的 `hf-seek` / `waitUntil`。`start` 相对当前 composition 文档；绑定器拥有未单独注册的局部 paused Timeline，先求值再调用 `renderAt(localTime)`，宿主仍负责可见性。不要再将同一 Timeline 加入主时间轴或注册两次。`ready` 等待资产，不异步拼装 Timeline；释放时只清理绑定器自身资源。普通 GSAP 场景不需要此接线。

`tests/visual-mixed.mjs` 使用本地 `HF_PACKAGE`、`GSAP_FILE`、`THREE_FILE`、`CHROME_PATH` 跑双绑定与实际短片；其输出目录作为 `MIXED_FIXTURE`，配合 `PLAYWRIGHT_PACKAGE` 运行 `tests/visual-plan.mjs` 验证播放器和生命周期。它们是技术夹具，不是已批准组件或生产复用证据。无硬件 WebGL 的 WSL 可用 `preview render --software-gl`，不会替换效果为静态图。

## Draft QA

在项目目录运行：

```bash
npx hyperframes check
npx hyperframes render --quality draft --output renders/review.mp4
```

修复错误、空 Scene、越界、遮挡、不可读和严重节奏问题。普通 Warning 不阻止 Draft。

## Final QA

沿用项目固定版本的 `check`，并检查最终音频时长、Scene 时间轴、音画同步、文字越界、最后一帧和输出比例，执行：

```bash
npx hyperframes render --fps 60 --quality high --output renders/final.mp4
```

Final Error 阻止 `./work finalize ... --qa-passed`。全部通过时只向用户报告结果，不列逐项清单。
