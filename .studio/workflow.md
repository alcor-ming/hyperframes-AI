# 创作工作流

## 最小启动

运行 `./work current`，然后只加载当前 Work、Variant、Script、一个 Recipe 和一套 Profile。已有合格输入时跳过上游步骤。

## Talking-head

```text
内容输入 -> DBS 文案设计 -> 必要时批准 Script -> 用户录制
-> section_map -> Animation Plan -> 批准 Plan -> HTML + Draft
-> 接受 Draft -> Final QA + 60fps high render -> Finalize -> 自动归档
```

## Pure HyperFrames

没有正式配音时，先按字数、语速和信息密度估算时间，完成接近 Final 的无声 Draft。接受 Draft 后再接入正式配音，从对应源码快照继续，只调整时间、停留、转场和元素出现顺序。

已有正式配音时，先生成 `section_map.json`，再完成 Plan、Draft 和 Final。

## 检查点

1. DBS 修改口播正文时批准 `SCRIPT.md`。
2. 正式 HTML 制作前批准一份 `ANIMATION_PLAN.md`。
3. Final 前接受一个 Draft 作为视觉基线。

技术 QA、时间微调、换行、easing、性能优化和归档不要求用户批准。

## 状态

Variant 只使用 `active`、`waiting_user`、`waiting_asset`、`parked`。具体阶段由文件、`wait_for` 和 `next_action` 推导；归档由目录位置表达。
