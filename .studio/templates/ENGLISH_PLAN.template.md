---
{"status":"draft","revision":1,"plan_format":"3.7.0","template":"__TEMPLATE__","ratio":"__RATIO__","script_revision":__SCRIPT_REVISION__,"research_revision":__RESEARCH_REVISION__,"timing_source":"estimated","subject_position":__SUBJECT_POSITION__}
---

# 英语学习 Plan

元信息由 CLI 生成并冻结 english 链路。原创教学正文在 Script，中文讲解与英文发音通过公共 TTS 分段合成、正式采用并对齐。试音和估时不能作为正式 timing。

## S01

每个 Scene 一个 `english-plan`，填写本场实际讲授的单词、词义、标准发音来源、拼写、上屏信息与 cue。各 Scene 可采用不同教学顺序；每个词须在全片至少有一个发音 cue 和一个回忆任务。例句和记忆提示仅在使用时添加，字段见 `.studio/spec/english.md`。以下空内容故意不能通过检查。

```english-plan
{"words":[],"cues":[],"recall":[]}
```

### I01 · SCRIPT.md#P001

```screen
<本场实际上屏的单词、释义或例句>
```

### 阅读停顿

回忆区间由 `recall.start_cue/end_cue` 明确声明，自动纳入 pause 例外；普通阅读停顿按实际需要填写 `| 例外 | 起始 cue | 结束 cue | pause | 阅读目的 |`。停顿不需要用无关运动填满。

## 素材与声音

记录英文发音依据、所用声音、中文讲解和英文片段的对应 Anchor。谐音只用于记忆，不能代替标准发音或冒充词源。虚构幽默情境明确标记。无需角色、生图、固定片长、A/B 顺序或参考机制配额。

```sound
{"sfx":[]}
```

## 未验证项

记录发音听校、例句是否符合本期词义、幽默表达和真实画面尚待验证的范围；结构检查不代表教学质量已验证。
