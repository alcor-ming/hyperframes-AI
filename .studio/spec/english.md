# 英语学习链路

直接选择 `mode=english`，使用 `ENGLISH_PLAN.template.md`，原创 Script → 公共 TTS 候选 → 正式声音采用与字词对齐 → Plan → Studio Draft。与其他链路共用 Work/Variant、冻结资产、ready/seek、闭包和接受流程。无需固定 A/B 交替、参考机制数量、角色或生图。

每个 Script Scene 对应一个 `english-plan` JSON 块。Scene 可讲一个或多个词，也可分场讲同一个词；重复词的本期词义、标准发音来源及拼写必须一致。未采用的 mnemonic/example 字段直接省略，必填空字符串或占位符不能通过检查。

```english-plan
{
  "words": [{
    "word": "cat",
    "sense": "猫（动物）",
    "pronunciation": {"source": "本期词典发音记录与英文声音听校记录", "language": "en-US"},
    "spelling": "cat",
    "mnemonic": {"kind": "spelling", "text": "依次回忆 c、a、t"},
    "example": {"text": "My cat is my boss.", "meaning": "我的猫是我的老板。", "fictional": true}
  }],
  "cues": [
    {"word": "cat", "cue": {"token": "cat", "nth": 1}, "target": "I01", "action": "pronounce"}
  ],
  "recall": [{"word": "cat", "task": "spelling", "prompt": "遮住单词后拼写", "answer": "cat", "target": "I01", "start_cue": "试着拼写", "end_cue": "答案"}]
}
```

示例的来源描述、口播词和信息 ID 必须替换成本期真实证据。`target` 引用本场定义或显式延续的 `screen` 信息 ID；实际文字写在该信息块。`pronunciation.source` 记录标准发音依据，`language` 为英语语言标签（如 en-US/en-GB）。结构检查只能确认已声明依据，发音准确性仍需听校。

`spelling` 必须与目标词逐字符相同。`mnemonic.kind` 为 homophone、association 或 spelling；homophone 明确属于近音记忆，不能当音标、标准发音、词根或词源。`example` 声明实际英文正文、对应中文含义和是否为虚构情境；是否与本期词义相符由创作审查判断，不由字符串规则假装判定。

`cues.action` 支持 pronounce、reveal、emphasize、hide、answer，引用正式字词 cue（字符串或既有 token/nth/within/edge 查询），不接受按文本长度分配的秒数。每词全片至少一个 pronounce 事件，查询正文须包含该英文目标词。事件按声音先后排列，可同时发生；真实 cue 必须处于对应 Scene 内。

`recall.task` 为 spelling 或 meaning，`prompt` 写回忆任务，`answer` 写实际答案。拼写答案必须与目标词相同。每词全片至少一个回忆任务，可以放在后面的 Scene；起止 cue 须解析且有正时长。回忆区间自动成为有理由的 pause 例外，其他阅读停顿也可沿用 Plan 的显式 pause 行。工具验证 cue、区间和声明，不自动判断停顿是否足够记忆。

缺正式声音对齐时检查返回 `english_timing_unverified`，不把 Script 估时变成真实时间。音频改变后重新检查对应 Plan/cue，接受快照保持冻结。中文字幕、英文发音与拼写文字可各自强调，既有 Motion 支持文字揭示、遮挡和答案返回；当前版本不新增动作库或例句生成器。

Work 51 仅是教学结构的试验参考；更多文字 Motion、幽默情境、谐音和拼写记忆方法保留为后续完善方向，不固定单个 Scene、纸背景、片长或排法。继续制作时显式创建英语 Variant，不能改写旧接受快照。
