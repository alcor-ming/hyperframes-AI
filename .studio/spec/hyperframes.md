# HyperFrames 实现与 QA

## 实现

- 一个 Variant 只读取一个 Profile。
- 每个 Scene 先完成静态 Hero State，再添加 GSAP 动画。
- Timeline 必须同步、确定性构建，使用 `{ paused: true }` 并注册到 `window.__timelines`。
- 禁止 `Math.random()`、`Date.now()`、异步 Timeline、`repeat: -1` 和多个 Timeline 同时修改同一属性。
- composition 或 Scene 保留 `S01` 等稳定 ID；结构性偏离返回 Animation Plan。
- `talking_head` 保持人物视频为主视觉；只依据 `left|center|right` 预留位置，明确阻塞时才检查代表帧。
- 在不牺牲单场主焦点和可读性的前提下，优先把 `RESEARCH.md` 中的机制做成多个有语义的动效组件，并使用更丰富但 seek-safe 的 GSAP 动画；不为增加数量堆装饰。
- 每个组件都有可辨识的入场动画。除持续播放的媒体外，组件主动作约在 Scene 结束前 `0.4s` 完成，并保留稳定 Hero State 到 Scene 结束。
- 适合进度语义的组件使用 `0 -> 100%` progress fill 与 counter 同步动画；完成时只 pulse 一次。进度条不同区域使用多种可区分颜色，文字色按信息层级丰富变化，同时保持对比度。
- Scene 布局必须预留明确的图片/视频位和必要文案位；缺少素材时保留稳定 Slot，不用虚构素材填满。
- Skill 讲解为每个 Skill 建立独立介绍 Scene：左侧名称与功能介绍，右侧真实 GitHub 页面截图，并用轻微透视、层次或阴影形成可读的立体感，不伪造仓库数据。

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
