# HyperFrames 实现与 QA

## 实现

- 一个 Variant 只读取一个 Profile。
- 每个 Scene 先完成静态 Hero State，再添加 GSAP 动画。
- Timeline 必须同步、确定性构建，使用 `{ paused: true }` 并注册到 `window.__timelines`。
- 禁止 `Math.random()`、`Date.now()`、异步 Timeline、`repeat: -1` 和多个 Timeline 同时修改同一属性。
- composition 或 Scene 保留 `S01` 等稳定 ID；结构性偏离返回 Animation Plan。
- `talking_head` 保持人物视频为主视觉；只依据 `left|center|right` 预留位置，明确阻塞时才检查代表帧。

## Draft QA

在项目目录运行：

```bash
npx hyperframes lint
npx hyperframes validate
npx hyperframes inspect --json
npx hyperframes render --quality draft --output renders/review.mp4
```

修复错误、空 Scene、越界、遮挡、不可读和严重节奏问题。普通 Warning 不阻止 Draft。

## Final QA

除 lint、validate、inspect 外，检查最终音频时长、Scene 时间轴、音画同步、文字越界、最后一帧和输出比例，并执行：

```bash
npx hyperframes render --fps 60 --quality high --output renders/final.mp4
```

Final Error 阻止 `./work finalize ... --qa-passed`。全部通过时只向用户报告结果，不列逐项清单。
