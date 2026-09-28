---
{"status":"draft","revision":1,"plan_format":"3.5.2","template":"__TEMPLATE__","ratio":"__RATIO__","script_revision":__SCRIPT_REVISION__,"research_revision":__RESEARCH_REVISION__,"timing_source":"estimated","subject_position":__SUBJECT_POSITION__}
---

# Animation Plan

元信息由 CLI 从 Variant 与 appearance lock 生成；未冻结或未提供的值保持 null，模型不手填。输入版本更新后用 `work --work <id> --variant <id> plan refresh` 刷新机器字段；这不接受改动后的内容。

## 全片方向

一句话概念、叙事弧、核心比喻；按需补前后呼应、背景情绪弧与声音签名。所有模式填写，card 可以只写前三项。

## 概览

| Scene | 一句话摘要 |
|---|---|
| S01 | <本场摘要> |

概览只作索引；设计只在对应 Scene 节维护。保留实际 Script 的 Scene ID，不为模板重编号。

## S01

<一句场景概括>

**A/B 编排与延续：** <A 与 B 各是什么；A → B → A 或 A → B；B 接管时 A 隐藏或虚化；跨场返回时延续自哪个 Scene>

**延续信息：** <返回 A 时列出前场已定义的信息 ID，例如 I01；不重复 screen 正文，无延续则省略>

```card C1 · P001
preset: F01
area: left
title: <卡片标题> @<口播词>
- <条目> @<口播词>
```

### I01 · SCRIPT.md#P001

```screen
<卡片之外的独立上屏正文，实际换行，不照搬口播>
```

### 素材与声音

**B 素材：** <精确引用、占位 ID 或 Asset Brief；生成素材写用途、数量、风格>

**声音 cue：** <如有，写声音资产与对应可见事件>

### 事件序列与例外

| cue | 层 | 目标 | 变化 |
|---|---|---|---|
| <口播词或词#第几次> | 4 | I01 | 揭示文字 |

只写积木块之外的事件。目标可为空，此时标未验证；有目标时只匹配该目标或子元素。例外另起行：`| 例外 | 起始 cue | 结束 cue | pause 或 talking_head | 原因 |`。声明不代表批准，停顿随本版方向确认批准。字幕、背景漂移、待机/说话起伏及持续镜头运动的中间过程不计。

## 声音导出

全片唯一 sound JSON 保留，逐 Scene 的声音 cue 引用这里的资产。未使用 BGM 则省略 bgm，未使用音效则 sfx 为空；示例占位不导出为素材。

```sound
{"sfx":[]}
```

<!-- 模板说明，不保留通过的自检清单：

- 每场 A/B 编排与第 2–4 层可见事件明确，相邻有效事件间隔不超过 2 秒，不“铺开再等”。
- A 文字不照搬口播，B 素材有来源或 Brief，事实边界清楚。
- 第 4 层阅读保护期间，第 2、3 层继续产生事件；刻意停顿写明区间和原因，talking_head 真人区间单独声明。
卡片文字中的 @ 与 [ 必须转义；SVG 写在 cue 后的方括号中，只接受闭包内图标引用或 custom:文件.svg。exit 可写退场 cue。无卡片、独立文字、素材或声音时省略对应块。信息 ID 全片唯一，延续信息只引用 ID。screen 默认 A、第 4 层，例外才写所属画面。Plan 只记录未通过项与例外。
-->

## 唯一参考 Scene 与方向批准

**Scene ID：** <一个实际 Scene>

**展示与未验证范围：** <真实实现、占位和未解决风险>

**准确预览：** <生成后的实际定位>

**方向批准：** <用户原意与对应版本，不能自行填通过>

## 后续交付与局部变更

**待补输入：** <只列真实缺口>

**本次局部变更：** <变更和影响范围>

派工只传 Plan 路径、Scene ID、负责范围与写入边界；治理与接受见 `.studio/workflow.md`，表达合同见 `.studio/spec/visual-design.md`。
