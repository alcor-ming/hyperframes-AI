# Template B — Pure HyperFrames Narrative

## 定义

没有必须保留为主视觉的原始人物口播画面。整个视觉叙事由 HyperFrames 构建：

```text
HyperFrames = 主视觉 + 叙事 + 解释
音频/配音 = 可选时间轴驱动
```

## 最小输入

至少一种内容来源：

- 完整文稿或口播稿；
- `资料.md`；
- 大纲；
- 分镜草稿；
- 已有音频；
- 已有 `section_map.json`。

`section_map.json` 不强制。

## 配音模式

### 已有最终音频

```yaml
timing: audio_locked
voiceover: provided
```

### 用户后续录制

```yaml
timing: voiceover_pending
voiceover: record_later
```

### AI 生成

```yaml
timing: voiceover_pending
voiceover: ai_generated
```

### 无旁白

```yaml
timing: visual_only
voiceover: none
```

正确顺序是：

```text
视觉计划草案 → 用户讨论并批准 → 最终旁白/AI 配音 → 锁定真实时间 → 完成动画
```

不是在整片动画完成后才第一次生成音频。

## Scene 类型

- `opening_statement`
- `typographic_argument`
- `concept_diagram`
- `process_build`
- `data_story`
- `comparison_stage`
- `image_evidence`
- `quote_or_source`
- `chapter_reset`
- `final_resolution`
- `quiet_hold`

## 视觉连续性

由于没有持续人物锚点，场景之间应尽量延续一个对象：关键词、数字、线条、图形、图片、章节编号、空间方向或色块。

避免每个 Scene 都完全清空后重新淡入。

## 计划阶段的时间

尚无最终音频时，在 Scene 的“时间或内容锚点”中写：

- 对应旁白段落；
- 预计持续时间范围。

配音完成后自动替换为真实时间码，不改变已批准的视觉目标和 Hero State。

## 图片资产

图片可以承担完整场景、证据、背景或章节 Hero Image，但必须在计划中写明：

- 叙事用途；
- 主体位置；
- 留白位置；
- 裁切方式；
- 比例；
- 禁止出现的内容。

## 字幕

字幕可作为旁白的辅助组件、动排内容或可访问性层。字幕不是本模板的唯一主体，也不形成第三套模板。
