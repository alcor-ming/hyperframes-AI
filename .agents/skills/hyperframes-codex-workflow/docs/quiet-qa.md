# Quiet QA

## 原则

QA 必须执行，但不应占用用户讨论 Animation Plan 的 token。

Codex默认静默运行、读取结果并自动修复。只有无法自动解决的错误、会改变批准方案的修复，或最终输出与计划存在实质偏差时才报告。

## 基础命令

```bash
npx hyperframes lint
npx hyperframes validate
npx hyperframes inspect --json
```

新 composition 或显著动画变更时运行 animation map。小型颜色或单一时长调整可以省略。

## 检查重点

- composition 与 timeline 注册；
- 轨道冲突；
- 文字溢出和画布越界；
- 人脸、原字幕、Logo 和平台 UI 冲突；
- 对比度；
- Scene 转场；
- 动画碰撞、不可见和过快节奏；
- 音频时长与最终 composition 时长；
- 最后一帧；
- 60fps 渲染。

## 渲染顺序

```bash
npx hyperframes render --quality draft --output renders/review.mp4
npx hyperframes render --fps 60 --quality high --output renders/final.mp4
```

## 用户可见报告

所有检查通过时，不列出逐条清单。交付中最多写：

```text
渲染与基础检查已完成。
```

存在问题时只报告：

- 问题是什么；
- 影响哪个 Scene；
- 已采取什么修复；
- 是否改变批准方案；
- 仍需用户决定的内容。

机器日志可保存至 `.hyperframes/qa/`，但不把它们复制到聊天回复中。
