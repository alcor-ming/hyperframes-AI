# Voiceover Workflow

## Talking-head

默认使用原视频音轨：

```yaml
timing: source_locked
voiceover: source
```

用户提供替换音频时，以替换音频作为唯一权威时间轴。视频画面与音频需要同步，但不能同时由两者分别定义总时长。

## Pure HyperFrames

### `provided`

已有最终音频。先分析音频，再生成带真实时间码的 Animation Plan。

### `record_later`

先讨论视觉计划和旁白结构。批准后输出最终旁白稿，接收录音后提取真实时长并更新时间码。

### `ai_generated`

先讨论视觉计划和旁白结构。批准后生成最终配音，再提取时间信息并完成动画。

最小语音配置：

```yaml
voice:
  language: zh-CN
  tone: calm_explanatory
  speed: 1.0
  intensity: restrained
```

不要输出长篇声音人格论证。只有用户提出明确声音要求时才扩展。

### `none`

无旁白，可由音乐、音效或纯视觉时间线驱动。

## 配音后的重定时

配音完成后自动：

- 获取真实总时长；
- 识别句间停顿；
- 将 Scene 估算时间替换为实际时间；
- 必要时生成词级时间信息；
- 调整动画持续时间和停留时间。

只要 Scene 数量、顺序、信息目标和 Hero State 不变，不重新要求用户批准。

## section_map

`section_map.json` 可以：

- 由现有内容提供；
- 从文稿生成；
- 从最终音频转录后生成；
- 完全省略。

它是缓存和复用工具，不是制作门槛。

## 本地 HyperFrames TTS

项目选择 HyperFrames 本地 TTS 时，可在批准后使用：

```bash
npx hyperframes tts script.txt --voice <voice-id> --output narration.wav
npx hyperframes transcribe narration.wav
```

也可接入其他 AI 语音服务；工作流只依赖最终音频文件和时间信息，不绑定某一家模型。
