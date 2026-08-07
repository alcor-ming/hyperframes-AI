# Animation Plan Contract

## 目的

`ANIMATION_PLAN.md` 是用户与 Codex 共同维护的视觉需求文档，也是正式制作前唯一需要用户批准的计划。

它描述“表达什么、最终画面是什么、如何运动”，不描述完整实现代码，也不承担流程自证。

## 状态

只使用两个状态：

```yaml
status: draft
status: approved
```

不增加 review、verified、compliant、locked 等证明性状态。

## 强制内容

### Plan Header

```yaml
template: talking_head | pure_hyperframes
profile: optical_fluidity | kami_editorial | monochrome_atelier
ratio: 16:9 | 9:16 | source
fps: 60
timing: source_locked | audio_locked | voiceover_pending | visual_only
voiceover: source | provided | record_later | ai_generated | none
```

### Scene Table

| Scene | 时间或内容锚点 | 视觉目标 | Hero State | 动画逻辑 | 资产 |
|---|---|---|---|---|---|

字段规则：

- **Scene**：稳定 ID，例如 `S01`。
- **时间或内容锚点**：有最终媒体时写时间码；后配音时写旁白段落和估算时长。
- **视觉目标**：一句话说明观众必须理解或记住什么。
- **Hero State**：动画完成后最完整、稳定、可读的构图。
- **动画逻辑**：使用 Profile motion primitives 描述，通常 1–3 个动词。
- **资产**：`无`、现有文件名或 `IMG-001` 等资产 ID。

### Optional Asset Brief

只有计划需要生成或制作图片时才出现。

| Asset ID | Scene | 用途 | 构图要求 | 比例 | 来源 | 禁止内容 |
|---|---|---|---|---|---|---|

### 待决策

只列会实质影响视觉或叙事的决策，最多 3 项。每项给出 Codex 推荐默认值，不要求用户从空白开始设计。

## 非强制层级

`Section → Scene → Beat → Cue` 仍可用于内部规划，但用户可见计划只强制 Scene。

只有以下情况才增加 Cue：

- 关键词必须对齐具体口播；
- 数字或步骤必须在精确时间变化；
- 音乐/音效触发明确视觉事件；
- 多个元素的先后关系无法仅靠 Scene 描述。

## 批准后可自动调整

- 真实配音长度引起的 Scene 时间码变化；
- 文字换行和字号；
- 避让人物、字幕、Logo 或平台 UI；
- 动画持续时间和 easing；
- 图片重生成；
- 技术性转场修正；
- 渲染性能优化。

这些调整不得改变场景的信息目标和 Hero State。
