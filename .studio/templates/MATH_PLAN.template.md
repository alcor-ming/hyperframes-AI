---
{"status":"draft","revision":1,"plan_format":"3.7.0","template":"__TEMPLATE__","ratio":"__RATIO__","script_revision":__SCRIPT_REVISION__,"research_revision":__RESEARCH_REVISION__,"timing_source":"estimated","subject_position":__SUBJECT_POSITION__}
---

# 数学思维 Plan

元信息由 CLI 生成并冻结 math 链路。原片出处、作者、片段与正式声音记录在 Research；人工核对歌词以 Script 为准。新数学制作无需角色、生图、通用导演 Brief 或固定 A/B 交替。

## S01

保留 Script 的稳定 Scene ID。每场恰好一个 `math-plan`，按真实关系、符号和歌词 cue 填写；不要把示例占位或空清单当成完成。需要现有数学积木时，依 `.studio/spec/math-kit.md` 添加同场 `math` 布局和冻结字体，使用 `math build`。

```math-plan
{"units":[],"symbols":{},"invariants":[],"zero_basics":[],"cues":[]}
```

### I01 · SCRIPT.md#P001

```screen
<本场需要的准确公式、符号或关系文字>
```

## 素材与声音

精确资产引用、正式原片声音、人工核对歌词、需要的词 cue／节拍证据按实际内容记录。时间来自正式声音，不维护另一份手填精确时间表。

```sound
{"sfx":[]}
```

## 未验证项

填写真实缺口、对应 Scene 和证据。数学专项检查见 `.studio/spec/math-rap.md`；ready、seek、闭包与准确 Draft 接受仍遵守 `.studio/workflow.md`。
