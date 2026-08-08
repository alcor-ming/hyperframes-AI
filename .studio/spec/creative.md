# 创作契约

## 文案

- `source.md` 保存主要原始基线，任何改写不得覆盖它。
- `SCRIPT.md` 只包含当前 Variant 的口播正文。使用 `<!-- P001 -->` 形式的稳定 Anchor；批准后新增 Anchor，不重排全部编号。
- `PACKAGE.md` 保存标题、封面、发布说明和风险摘要，不进入口播正文。
- DBS 只有在实际修改口播正文时才把 Script 状态设为 `pending` 并等待用户批准。

## 录制对齐

- 实际视频或音频是时间轴权威，`SCRIPT.md` 是批准文案真源。
- 默认生成 sentence-level `section_map.json`；只有精确卡点需要时才增加 word-level 数据。
- 自然口语差异继续执行；改变事实、论点、段落结构或 Scene 映射时暂停。
- 需要重新说出口的正文修改会使 Recording、Section Map、Plan 和 Accepted Draft 失效。

## Animation Plan

- `ANIMATION_PLAN.md` 是唯一视觉语义真源，正式 HTML 制作前必须为 `approved`。
- Scene 引用 Script Anchor，不复制全文。
- Scene 必须给出一个视觉目标、完整可读的 Hero State 和简短运动逻辑。
- Scene 数量、顺序、目标、Hero State、Template、Profile 或文案结构变化时，Plan Revision 加一并清除 Accepted Draft。
- 精确时间、easing、换行、安全区、性能和不改变 Hero State 的布局修复不增加 Plan Revision。

## 排除项

v1 不调用图片生成、Prompt 检索或 `design-taste-frontend`，也不生成、管理或烧录传统底部字幕。用户已有静态素材可作为普通媒体引用。
