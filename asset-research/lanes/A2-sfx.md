# A2 音效补充调查

检索日：2026-10-02 UTC。R0官方Registry基线由另一路核验；本页补充可带回项目的许可明确候选，不复制或重计R0资源。只读GitHub文本/元数据，没有音频、ZIP、第三方二进制下载或转码；“推荐”指优先试听/验收的来源。

## 优先五项与映射

1. A2-01 Kenney/Calinou UI：tick/click/rollover，51 WAV实际树计数，README写50
2. A2-02 Interface Sounds：tick、ding/confirmation、error、glitch，OGG待转码
3. A2-06 Camera Shutter：0.32秒，补专用快门，仓库已有MP3
4. A2-07 Rewind Sweep：0.75秒，补reverse，仓库已有MP3
5. A2-08 DSP精选：pop、typing、whoosh、riser、boom、error、coin/score映射，仓库已有MP3

笑声缺口有A2-09真实录音，但整个ESC-50以NC条件隔离；没有把CC0单项扩大到整库商业授权。专门名为score的资产未检出，coin_ping/powerUp是建议映射。

所有时长来自发布者CSV或数据集规范而非本轮测量。OGG→WAV不是恢复无损母带；再转MP3须记录变化与新哈希。音频调度应本地化、固定入出点、抽样验证中段seek与尾音，不用播放时钟驱动画面。

## 排除与来源风险

[SFXMint固定README](https://github.com/flreey/sfxmint-mcp/blob/34ad5e74b2b209f0774af80966cab63c8240b167/README.md)明确混合AI生成/程序合成音效，且仓库只有MCP说明而没有被审计音频源包；不纳入推荐，也不使用其API下载。Awesome-list、聚合API和站外音库只算来源线索，不能拿代码MIT许可证充当音频许可证。

Kenney镜像保留每包License.txt与作者来源台账，可作为后续取材路径；未做原包字节比对。mirror的Sci-Fi73 OGG、Digital62 OGG存在数量漂移，低于Interface/Calinou优先级。

## A2-01 · Kenney UI Audio (Calinou WAV转包)

结论：首推：干净UI候选，原生WAV（非原生MP3）

- 仓库：https://github.com/Calinou/kenney-ui-audio
- 固定commit：8c3d81b9159d058c444f89d12d518276b0b09345
- 许可与实际许可文件：{"spdx": "CC0-1.0", "path": "LICENSE.txt", "url": "https://github.com/Calinou/kenney-ui-audio/blob/8c3d81b9159d058c444f89d12d518276b0b09345/LICENSE.txt", "scope": "不借用根代码许可推断音频授权"}
- 义务：{"attribution": false, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "保留许可与来源证据；录音/曲目和程序许可分开核对"}
- 内容与证据：{"kind": "GitHub实际音频包", "files": ["https://github.com/Calinou/kenney-ui-audio/blob/8c3d81b9159d058c444f89d12d518276b0b09345/addons/kenney_ui_audio/click1.wav", "https://github.com/Calinou/kenney-ui-audio/blob/8c3d81b9159d058c444f89d12d518276b0b09345/addons/kenney_ui_audio/mouseclick1.wav", "https://github.com/Calinou/kenney-ui-audio/blob/8c3d81b9159d058c444f89d12d518276b0b09345/addons/kenney_ui_audio/mouserelease1.wav", "https://github.com/Calinou/kenney-ui-audio/blob/8c3d81b9159d058c444f89d12d518276b0b09345/addons/kenney_ui_audio/rollover1.wav", "https://github.com/Calinou/kenney-ui-audio/blob/8c3d81b9159d058c444f89d12d518276b0b09345/addons/kenney_ui_audio/switch1.wav"], "examples": ["click1.wav", "mouseclick1.wav", "mouserelease1.wav", "rollover1.wav", "switch1.wav"], "mapping": "UI tick/click", "duration_sec": "未知，未试听测量", "stems": "不适用", "upstream_external_lead": "https://kenney.nl/assets/ui-audio", "usage_mapping": ["UI tick", "click"], "size_metadata": {"basis": "GitHub固定树blob.size；只统计本条files所列文件/目录内音频，不含文本、目录外preview或其他包", "by_format": {".wav": {"file_count": 5, "sum_bytes": 146054}}, "unique_blob_bytes": 146054, "unique_blob_count": 5, "note": "unique值按Git blob SHA去重；不同编码版本仍是不同blob，不按作品跨格式去重。未下载测量。"}}
- 用途映射：["media"]
- 产品线：["card", "explainer", "showcase"]
- 音频元数据：{"format": "WAV（由OGG解码转包，源本来有损）", "duration_sec": null, "bpm": "不适用", "conversion": "未来转MP3须离线统一采样率并重新检测瞬态/前置静音/峰值；本轮未转码", "timeline_validation": "作为本地静态音频文件按固定时间线调度；跳转到中段与重复渲染，检查首音偏移、尾音及loop接点。不要依赖实时WebAudio播放时钟。"}
- 适配：{"grade": "B", "detail": "WAV/OGG/FLAC需统一转MP3并重新验收。未下载、转码、剪辑或试听二进制；入库后再做响度、头尾、爆音、混音避让和源文件哈希验收。"}
- 可seek性：不适用（静态素材）
- 维护状态：{"snapshot_checked": "2026-10-02 UTC", "note": "只读元数据与文本审计；不保证听感或Content ID状态", "last_commit": "2020-12-06T19:28:35Z", "commit": "8c3d81b9159d058c444f89d12d518276b0b09345"}
- 风险：["未试听；无法保证每条符合短视频听感和音量范围。", "README称50条，pin树有51 WAV；不能把转换成WAV说成恢复无损母带。"]

可粘贴署名：

Kenney UI Audio (Calinou WAV转包) by Kenney — CC0 1.0 (https://creativecommons.org/publicdomain/zero/1.0/). Source: https://github.com/Calinou/kenney-ui-audio/tree/8c3d81b9159d058c444f89d12d518276b0b09345/addons/kenney_ui_audio. Modified: [填写OGG→WAV/MP3/剪辑等，或 none].（署名自愿）

放置位置：视频简介或片尾署名；可再分发素材包附 ATTRIBUTION 与许可文本。CC0署名为自愿溯源。

## A2-02 · Kenney Interface Sounds

结论：首推：一包覆盖信息卡反馈与glitch

- 仓库：https://github.com/OmniTender-Systems/game-audio-assets
- 固定commit：378269191f4219775f113d52dcf7ce7d5c810b5f
- 许可与实际许可文件：{"spdx": "CC0-1.0", "path": "vendor/kenney/interface-sounds/License.txt", "url": "https://github.com/OmniTender-Systems/game-audio-assets/blob/378269191f4219775f113d52dcf7ce7d5c810b5f/vendor/kenney/interface-sounds/License.txt", "scope": "不借用根代码许可推断音频授权"}
- 义务：{"attribution": false, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "保留许可与来源证据；录音/曲目和程序许可分开核对"}
- 内容与证据：{"kind": "GitHub实际音频包", "files": ["https://github.com/OmniTender-Systems/game-audio-assets/blob/378269191f4219775f113d52dcf7ce7d5c810b5f/vendor/kenney/interface-sounds/Audio/tick_001.ogg", "https://github.com/OmniTender-Systems/game-audio-assets/blob/378269191f4219775f113d52dcf7ce7d5c810b5f/vendor/kenney/interface-sounds/Audio/click_001.ogg", "https://github.com/OmniTender-Systems/game-audio-assets/blob/378269191f4219775f113d52dcf7ce7d5c810b5f/vendor/kenney/interface-sounds/Audio/confirmation_001.ogg", "https://github.com/OmniTender-Systems/game-audio-assets/blob/378269191f4219775f113d52dcf7ce7d5c810b5f/vendor/kenney/interface-sounds/Audio/error_001.ogg", "https://github.com/OmniTender-Systems/game-audio-assets/blob/378269191f4219775f113d52dcf7ce7d5c810b5f/vendor/kenney/interface-sounds/Audio/glitch_001.ogg"], "examples": ["tick_001.ogg", "click_001.ogg", "confirmation_001.ogg", "error_001.ogg", "glitch_001.ogg"], "mapping": "tick/click/ding/error/glitch", "duration_sec": "未知，未试听测量", "stems": "不适用", "upstream_external_lead": "https://kenney.nl/assets/interface-sounds", "usage_mapping": ["tick", "click", "ding", "error", "glitch"], "size_metadata": {"basis": "GitHub固定树blob.size；只统计本条files所列文件/目录内音频，不含文本、目录外preview或其他包", "by_format": {".ogg": {"file_count": 5, "sum_bytes": 30835}}, "unique_blob_bytes": 30835, "unique_blob_count": 5, "note": "unique值按Git blob SHA去重；不同编码版本仍是不同blob，不按作品跨格式去重。未下载测量。"}}
- 用途映射：["media"]
- 产品线：["card", "explainer", "showcase"]
- 音频元数据：{"format": "OGG；没有原生MP3", "duration_sec": null, "bpm": "不适用", "conversion": "未来转MP3须离线统一采样率并重新检测瞬态/前置静音/峰值；本轮未转码", "timeline_validation": "作为本地静态音频文件按固定时间线调度；跳转到中段与重复渲染，检查首音偏移、尾音及loop接点。不要依赖实时WebAudio播放时钟。"}
- 适配：{"grade": "B", "detail": "WAV/OGG/FLAC需统一转MP3并重新验收。未下载、转码、剪辑或试听二进制；入库后再做响度、头尾、爆音、混音避让和源文件哈希验收。"}
- 可seek性：不适用（静态素材）
- 维护状态：{"snapshot_checked": "2026-10-02 UTC", "note": "只读元数据与文本审计；不保证听感或Content ID状态", "last_commit": "2026-07-13T21:26:30Z", "commit": "378269191f4219775f113d52dcf7ce7d5c810b5f"}
- 风险：["未试听；无法保证每条符合短视频听感和音量范围。", "第三方镜像有每包原始License.txt及ATTRIBUTION来源台账；尚未与原作者包做二进制同一性校验。"]

可粘贴署名：

Kenney Interface Sounds by Kenney — CC0 1.0 (https://creativecommons.org/publicdomain/zero/1.0/). Source: https://github.com/OmniTender-Systems/game-audio-assets/tree/378269191f4219775f113d52dcf7ce7d5c810b5f/vendor/kenney/interface-sounds/Audio. Modified: [填写OGG→WAV/MP3/剪辑等，或 none].（署名自愿）

放置位置：视频简介或片尾署名；可再分发素材包附 ATTRIBUTION 与许可文本。CC0署名为自愿溯源。

## A2-03 · Kenney Sci-Fi Sounds

结论：备选：科幻开场，留意镜像数量漂移

- 仓库：https://github.com/OmniTender-Systems/game-audio-assets
- 固定commit：378269191f4219775f113d52dcf7ce7d5c810b5f
- 许可与实际许可文件：{"spdx": "CC0-1.0", "path": "vendor/kenney/sci-fi-sounds/License.txt", "url": "https://github.com/OmniTender-Systems/game-audio-assets/blob/378269191f4219775f113d52dcf7ce7d5c810b5f/vendor/kenney/sci-fi-sounds/License.txt", "scope": "不借用根代码许可推断音频授权"}
- 义务：{"attribution": false, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "保留许可与来源证据；录音/曲目和程序许可分开核对"}
- 内容与证据：{"kind": "GitHub实际音频包", "files": ["https://github.com/OmniTender-Systems/game-audio-assets/blob/378269191f4219775f113d52dcf7ce7d5c810b5f/vendor/kenney/sci-fi-sounds/Audio/computerNoise_000.ogg", "https://github.com/OmniTender-Systems/game-audio-assets/blob/378269191f4219775f113d52dcf7ce7d5c810b5f/vendor/kenney/sci-fi-sounds/Audio/lowFrequency_explosion_000.ogg", "https://github.com/OmniTender-Systems/game-audio-assets/blob/378269191f4219775f113d52dcf7ce7d5c810b5f/vendor/kenney/sci-fi-sounds/Audio/explosionCrunch_000.ogg"], "examples": ["computerNoise_000.ogg", "lowFrequency_explosion_000.ogg", "explosionCrunch_000.ogg"], "mapping": "片头boom/digital", "duration_sec": "未知，未试听测量", "stems": "不适用", "upstream_external_lead": "https://kenney.nl/assets/sci-fi-sounds", "usage_mapping": ["片头boom", "digital"], "size_metadata": {"basis": "GitHub固定树blob.size；只统计本条files所列文件/目录内音频，不含文本、目录外preview或其他包", "by_format": {".ogg": {"file_count": 3, "sum_bytes": 161615}}, "unique_blob_bytes": 161615, "unique_blob_count": 3, "note": "unique值按Git blob SHA去重；不同编码版本仍是不同blob，不按作品跨格式去重。未下载测量。"}}
- 用途映射：["media"]
- 产品线：["card", "explainer", "showcase"]
- 音频元数据：{"format": "OGG；没有原生MP3", "duration_sec": null, "bpm": "不适用", "conversion": "未来转MP3须离线统一采样率并重新检测瞬态/前置静音/峰值；本轮未转码", "timeline_validation": "作为本地静态音频文件按固定时间线调度；跳转到中段与重复渲染，检查首音偏移、尾音及loop接点。不要依赖实时WebAudio播放时钟。"}
- 适配：{"grade": "B", "detail": "WAV/OGG/FLAC需统一转MP3并重新验收。未下载、转码、剪辑或试听二进制；入库后再做响度、头尾、爆音、混音避让和源文件哈希验收。"}
- 可seek性：不适用（静态素材）
- 维护状态：{"snapshot_checked": "2026-10-02 UTC", "note": "只读元数据与文本审计；不保证听感或Content ID状态", "last_commit": "2026-07-13T21:26:30Z", "commit": "378269191f4219775f113d52dcf7ce7d5c810b5f"}
- 风险：["未试听；无法保证每条符合短视频听感和音量范围。", "第三方镜像有每包原始License.txt及ATTRIBUTION来源台账；尚未与原作者包做二进制同一性校验。", "镜像文件数与README/作者页面可能漂移，不能声称这就是未经改动的全量原包。"]

可粘贴署名：

Kenney Sci-Fi Sounds by Kenney — CC0 1.0 (https://creativecommons.org/publicdomain/zero/1.0/). Source: https://github.com/OmniTender-Systems/game-audio-assets/tree/378269191f4219775f113d52dcf7ce7d5c810b5f/vendor/kenney/sci-fi-sounds/Audio. Modified: [填写OGG→WAV/MP3/剪辑等，或 none].（署名自愿）

放置位置：视频简介或片尾署名；可再分发素材包附 ATTRIBUTION 与许可文本。CC0署名为自愿溯源。

## A2-04 · Kenney Digital Audio

结论：备选：得分是使用映射，不把文件名误写成score

- 仓库：https://github.com/OmniTender-Systems/game-audio-assets
- 固定commit：378269191f4219775f113d52dcf7ce7d5c810b5f
- 许可与实际许可文件：{"spdx": "CC0-1.0", "path": "vendor/kenney/digital-audio/License.txt", "url": "https://github.com/OmniTender-Systems/game-audio-assets/blob/378269191f4219775f113d52dcf7ce7d5c810b5f/vendor/kenney/digital-audio/License.txt", "scope": "不借用根代码许可推断音频授权"}
- 义务：{"attribution": false, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "保留许可与来源证据；录音/曲目和程序许可分开核对"}
- 内容与证据：{"kind": "GitHub实际音频包", "files": ["https://github.com/OmniTender-Systems/game-audio-assets/blob/378269191f4219775f113d52dcf7ce7d5c810b5f/vendor/kenney/digital-audio/Audio/powerUp1.ogg", "https://github.com/OmniTender-Systems/game-audio-assets/blob/378269191f4219775f113d52dcf7ce7d5c810b5f/vendor/kenney/digital-audio/Audio/threeTone1.ogg", "https://github.com/OmniTender-Systems/game-audio-assets/blob/378269191f4219775f113d52dcf7ce7d5c810b5f/vendor/kenney/digital-audio/Audio/highUp.ogg", "https://github.com/OmniTender-Systems/game-audio-assets/blob/378269191f4219775f113d52dcf7ce7d5c810b5f/vendor/kenney/digital-audio/Audio/lowDown.ogg"], "examples": ["powerUp1.ogg", "threeTone1.ogg", "highUp.ogg", "lowDown.ogg"], "mapping": "数字提示/得分/升降音", "duration_sec": "未知，未试听测量", "stems": "不适用", "upstream_external_lead": "https://kenney.nl/assets/digital-audio", "usage_mapping": ["数字提示", "得分", "升降音"], "size_metadata": {"basis": "GitHub固定树blob.size；只统计本条files所列文件/目录内音频，不含文本、目录外preview或其他包", "by_format": {".ogg": {"file_count": 4, "sum_bytes": 28463}}, "unique_blob_bytes": 28463, "unique_blob_count": 4, "note": "unique值按Git blob SHA去重；不同编码版本仍是不同blob，不按作品跨格式去重。未下载测量。"}}
- 用途映射：["media"]
- 产品线：["card", "explainer", "showcase"]
- 音频元数据：{"format": "OGG；没有原生MP3", "duration_sec": null, "bpm": "不适用", "conversion": "未来转MP3须离线统一采样率并重新检测瞬态/前置静音/峰值；本轮未转码", "timeline_validation": "作为本地静态音频文件按固定时间线调度；跳转到中段与重复渲染，检查首音偏移、尾音及loop接点。不要依赖实时WebAudio播放时钟。"}
- 适配：{"grade": "B", "detail": "WAV/OGG/FLAC需统一转MP3并重新验收。未下载、转码、剪辑或试听二进制；入库后再做响度、头尾、爆音、混音避让和源文件哈希验收。"}
- 可seek性：不适用（静态素材）
- 维护状态：{"snapshot_checked": "2026-10-02 UTC", "note": "只读元数据与文本审计；不保证听感或Content ID状态", "last_commit": "2026-07-13T21:26:30Z", "commit": "378269191f4219775f113d52dcf7ce7d5c810b5f"}
- 风险：["未试听；无法保证每条符合短视频听感和音量范围。", "第三方镜像有每包原始License.txt及ATTRIBUTION来源台账；尚未与原作者包做二进制同一性校验。", "镜像文件数与README/作者页面可能漂移，不能声称这就是未经改动的全量原包。"]

可粘贴署名：

Kenney Digital Audio by Kenney — CC0 1.0 (https://creativecommons.org/publicdomain/zero/1.0/). Source: https://github.com/OmniTender-Systems/game-audio-assets/tree/378269191f4219775f113d52dcf7ce7d5c810b5f/vendor/kenney/digital-audio/Audio. Modified: [填写OGG→WAV/MP3/剪辑等，或 none].（署名自愿）

放置位置：视频简介或片尾署名；可再分发素材包附 ATTRIBUTION 与许可文本。CC0署名为自愿溯源。

## A2-05 · Kenney Impact Sounds

结论：备选：3条已核实路径的impact候选；转场适用性待试听

- 仓库：https://github.com/OmniTender-Systems/game-audio-assets
- 固定commit：378269191f4219775f113d52dcf7ce7d5c810b5f
- 许可与实际许可文件：{"spdx": "CC0-1.0", "path": "vendor/kenney/impact-sounds/License.txt", "url": "https://github.com/OmniTender-Systems/game-audio-assets/blob/378269191f4219775f113d52dcf7ce7d5c810b5f/vendor/kenney/impact-sounds/License.txt", "scope": "不借用根代码许可推断音频授权"}
- 义务：{"attribution": false, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "保留许可与来源证据；录音/曲目和程序许可分开核对"}
- 内容与证据：{"kind": "GitHub实际音频包中的3条impact候选", "files": ["https://github.com/OmniTender-Systems/game-audio-assets/blob/378269191f4219775f113d52dcf7ce7d5c810b5f/vendor/kenney/impact-sounds/Audio/impactGeneric_light_000.ogg", "https://github.com/OmniTender-Systems/game-audio-assets/blob/378269191f4219775f113d52dcf7ce7d5c810b5f/vendor/kenney/impact-sounds/Audio/impactMetal_heavy_000.ogg", "https://github.com/OmniTender-Systems/game-audio-assets/blob/378269191f4219775f113d52dcf7ce7d5c810b5f/vendor/kenney/impact-sounds/Audio/impactPunch_heavy_000.ogg"], "examples": ["impactGeneric_light_000.ogg", "impactMetal_heavy_000.ogg", "impactPunch_heavy_000.ogg"], "mapping": "轻通用撞击 / 重金属撞击 / 重拳冲击（文件命名证据；转场听感尚待试听）", "duration_sec": "未知，未试听测量", "stems": "不适用", "upstream_external_lead": "https://kenney.nl/assets/impact-sounds", "usage_mapping": ["物理撞击强调", "转场impact候选（未试听）"], "size_metadata": {"basis": "GitHub固定树blob.size；只统计本条files所列文件/目录内音频，不含文本、目录外preview或其他包", "by_format": {".ogg": {"file_count": 3, "sum_bytes": 23554}}, "unique_blob_bytes": 23554, "unique_blob_count": 3, "note": "unique值按Git blob SHA去重；不同编码版本仍是不同blob，不按作品跨格式去重。未下载测量。"}}
- 用途映射：["media"]
- 产品线：["card", "explainer", "showcase"]
- 音频元数据：{"format": "OGG；没有原生MP3", "duration_sec": null, "bpm": "不适用", "conversion": "未来转MP3须离线统一采样率并重新检测瞬态/前置静音/峰值；本轮未转码", "timeline_validation": "作为本地静态音频文件按固定时间线调度；跳转到中段与重复渲染，检查首音偏移、尾音及loop接点。不要依赖实时WebAudio播放时钟。"}
- 适配：{"grade": "B", "detail": "WAV/OGG/FLAC需统一转MP3并重新验收。未下载、转码、剪辑或试听二进制；入库后再做响度、头尾、爆音、混音避让和源文件哈希验收。"}
- 可seek性：不适用（静态素材）
- 维护状态：{"snapshot_checked": "2026-10-02 UTC", "note": "只读元数据与文本审计；不保证听感或Content ID状态", "last_commit": "2026-07-13T21:26:30Z", "commit": "378269191f4219775f113d52dcf7ce7d5c810b5f"}
- 风险：["分类依据文件名，未试听；不能保证具备电影式boom/转场听感或符合短视频音量范围。", "第三方镜像有每包原始License.txt及ATTRIBUTION来源台账；尚未与原作者包做二进制同一性校验。"]

可粘贴署名：

Kenney Impact Sounds by Kenney — CC0 1.0 (https://creativecommons.org/publicdomain/zero/1.0/). Source: https://github.com/OmniTender-Systems/game-audio-assets/tree/378269191f4219775f113d52dcf7ce7d5c810b5f/vendor/kenney/impact-sounds/Audio. Modified: [填写OGG→WAV/MP3/剪辑等，或 none].（署名自愿）

放置位置：视频简介或片尾署名；可再分发素材包附 ATTRIBUTION 与许可文本。CC0署名为自愿溯源。

## A2-06 · DSP Camera Shutter

结论：首推：补Registry缺的专用快门

- 仓库：https://github.com/RezaParsian/free-sfx-bgm-pack
- 固定commit：f8d463c05c814804b786f9c8a5683d1abcd954da
- 许可与实际许可文件：{"spdx": "CC0-1.0", "path": "LICENSE", "url": "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/LICENSE", "scope": "sfx-lab/代码MIT；audio-pack/音频CC0"}
- 义务：{"attribution": false, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "保留许可与来源证据；录音/曲目和程序许可分开核对"}
- 内容与证据：{"kind": "GitHub实际音频/代码DSP合成", "files": ["https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/sfx/camera_shutter.mp3"], "evidence": ["https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/measured.csv", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/sfx-lab/build_sfx.py"], "durations_sec_publisher": {"camera_shutter": 0.32}, "source_method": "显式振荡器/噪声/包络DSP代码，不是外部音频样本或模型生成声明", "loop": "一次性SFX，无loop承诺", "usage_mapping": ["UI快门"], "size_metadata": {"basis": "GitHub固定树blob.size；只统计本条files所列文件/目录内音频，不含文本、目录外preview或其他包", "by_format": {".mp3": {"file_count": 1, "sum_bytes": 7880}}, "unique_blob_bytes": 7880, "unique_blob_count": 1, "note": "unique值按Git blob SHA去重；不同编码版本仍是不同blob，不按作品跨格式去重。未下载测量。"}}
- 用途映射：["media"]
- 产品线：["card", "explainer", "showcase"]
- 音频元数据：{"format": "仓库已有MP3与WAV；MP3是发布者预转版本，不需要本轮转换", "bpm": "不适用", "dependencies": "直接媒体文件；无需执行MIT生成器", "timeline_validation": "作为本地静态音频文件按固定时间线调度；跳转到中段与重复渲染，检查首音偏移、尾音及loop接点。不要依赖实时WebAudio播放时钟。"}
- 适配：{"grade": "A", "detail": "已有MP3，待本地听测/许可验收。未下载、转码、剪辑或试听二进制；入库后再做响度、头尾、爆音、混音避让和源文件哈希验收。"}
- 可seek性：不适用（静态素材）
- 维护状态：{"snapshot_checked": "2026-10-02 UTC", "note": "只读元数据与文本审计；不保证听感或Content ID状态", "last_commit": "2026-09-15T04:24:02Z", "commit": "f8d463c05c814804b786f9c8a5683d1abcd954da"}
- 风险：["项目较新；README的40/9与旧标题31/8、WAV不入库说法存在漂移。该pin实际49 WAV+49 MP3；以树和measured.csv为准。", "发布者声称无版权/Content ID风险不是保证，本报告不背书。这里是代码DSP合成，已读生成代码，没有把模型生成音频当素材引入。", "尚未试听、未重新测量，公开duration/LUFS只是发布者数据；没有成品stems。"]

可粘贴署名：

camera_shutter — RezaParsian — CC0 1.0 (https://creativecommons.org/publicdomain/zero/1.0/). Source: https://github.com/RezaParsian/free-sfx-bgm-pack/tree/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/sfx. Modified: [填写截取/混音/转码，或 none].（署名自愿）

放置位置：视频简介或片尾署名；可再分发素材包附 ATTRIBUTION 与许可文本。CC0署名为自愿溯源。

## A2-07 · DSP Rewind / Reverse Sweep

结论：首推：补反向扫频

- 仓库：https://github.com/RezaParsian/free-sfx-bgm-pack
- 固定commit：f8d463c05c814804b786f9c8a5683d1abcd954da
- 许可与实际许可文件：{"spdx": "CC0-1.0", "path": "LICENSE", "url": "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/LICENSE", "scope": "sfx-lab/代码MIT；audio-pack/音频CC0"}
- 义务：{"attribution": false, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "保留许可与来源证据；录音/曲目和程序许可分开核对"}
- 内容与证据：{"kind": "GitHub实际音频/代码DSP合成", "files": ["https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/sfx/rewind_sweep.mp3"], "evidence": ["https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/measured.csv", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/sfx-lab/build_sfx.py"], "durations_sec_publisher": {"rewind_sweep": 0.75}, "source_method": "显式振荡器/噪声/包络DSP代码，不是外部音频样本或模型生成声明", "loop": "一次性SFX，无loop承诺", "usage_mapping": ["转场reverse"], "size_metadata": {"basis": "GitHub固定树blob.size；只统计本条files所列文件/目录内音频，不含文本、目录外preview或其他包", "by_format": {".mp3": {"file_count": 1, "sum_bytes": 16240}}, "unique_blob_bytes": 16240, "unique_blob_count": 1, "note": "unique值按Git blob SHA去重；不同编码版本仍是不同blob，不按作品跨格式去重。未下载测量。"}}
- 用途映射：["media"]
- 产品线：["card", "explainer", "showcase"]
- 音频元数据：{"format": "仓库已有MP3与WAV；MP3是发布者预转版本，不需要本轮转换", "bpm": "不适用", "dependencies": "直接媒体文件；无需执行MIT生成器", "timeline_validation": "作为本地静态音频文件按固定时间线调度；跳转到中段与重复渲染，检查首音偏移、尾音及loop接点。不要依赖实时WebAudio播放时钟。"}
- 适配：{"grade": "A", "detail": "已有MP3，待本地听测/许可验收。未下载、转码、剪辑或试听二进制；入库后再做响度、头尾、爆音、混音避让和源文件哈希验收。"}
- 可seek性：不适用（静态素材）
- 维护状态：{"snapshot_checked": "2026-10-02 UTC", "note": "只读元数据与文本审计；不保证听感或Content ID状态", "last_commit": "2026-09-15T04:24:02Z", "commit": "f8d463c05c814804b786f9c8a5683d1abcd954da"}
- 风险：["项目较新；README的40/9与旧标题31/8、WAV不入库说法存在漂移。该pin实际49 WAV+49 MP3；以树和measured.csv为准。", "发布者声称无版权/Content ID风险不是保证，本报告不背书。这里是代码DSP合成，已读生成代码，没有把模型生成音频当素材引入。", "尚未试听、未重新测量，公开duration/LUFS只是发布者数据；没有成品stems。"]

可粘贴署名：

rewind_sweep — RezaParsian — CC0 1.0 (https://creativecommons.org/publicdomain/zero/1.0/). Source: https://github.com/RezaParsian/free-sfx-bgm-pack/tree/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/sfx. Modified: [填写截取/混音/转码，或 none].（署名自愿）

放置位置：视频简介或片尾署名；可再分发素材包附 ATTRIBUTION 与许可文本。CC0署名为自愿溯源。

## A2-08 · DSP UI / Typing / Comedy / Transition精选

结论：首推：按缺口取小集合，coin_ping可映射得分但无score命名

- 仓库：https://github.com/RezaParsian/free-sfx-bgm-pack
- 固定commit：f8d463c05c814804b786f9c8a5683d1abcd954da
- 许可与实际许可文件：{"spdx": "CC0-1.0", "path": "LICENSE", "url": "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/LICENSE", "scope": "sfx-lab/代码MIT；audio-pack/音频CC0"}
- 义务：{"attribution": false, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "保留许可与来源证据；录音/曲目和程序许可分开核对"}
- 内容与证据：{"kind": "GitHub实际音频/代码DSP合成", "files": ["https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/sfx/pop_bubble.mp3", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/sfx/notification_ding.mp3", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/sfx/typing_keyboard.mp3", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/sfx/type_key_single.mp3", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/sfx/error_buzz.mp3", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/sfx/coin_ping.mp3", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/sfx/air_horn_meme.mp3", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/sfx/whoosh_transition.mp3", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/sfx/riser_tension.mp3", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/sfx/boom_cinematic.mp3"], "evidence": ["https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/measured.csv", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/sfx-lab/build_sfx.py"], "durations_sec_publisher": {"pop_bubble": 0.13, "notification_ding": 0.85, "typing_keyboard": 1.5, "type_key_single": 0.05, "error_buzz": 0.42, "coin_ping": 0.55, "air_horn_meme": 1.25, "whoosh_transition": 0.95, "riser_tension": 2.6, "boom_cinematic": 3.0}, "source_method": "显式振荡器/噪声/包络DSP代码，不是外部音频样本或模型生成声明", "loop": "一次性SFX，无loop承诺", "usage_mapping": ["UI pop/ding/typing，转场whoosh/riser，片头boom，搞笑error/score映射"], "size_metadata": {"basis": "GitHub固定树blob.size；只统计本条files所列文件/目录内音频，不含文本、目录外preview或其他包", "by_format": {".mp3": {"file_count": 10, "sum_bytes": 239194}}, "unique_blob_bytes": 239194, "unique_blob_count": 10, "note": "unique值按Git blob SHA去重；不同编码版本仍是不同blob，不按作品跨格式去重。未下载测量。"}}
- 用途映射：["media"]
- 产品线：["card", "explainer", "showcase"]
- 音频元数据：{"format": "仓库已有MP3与WAV；MP3是发布者预转版本，不需要本轮转换", "bpm": "不适用", "dependencies": "直接媒体文件；无需执行MIT生成器", "timeline_validation": "作为本地静态音频文件按固定时间线调度；跳转到中段与重复渲染，检查首音偏移、尾音及loop接点。不要依赖实时WebAudio播放时钟。"}
- 适配：{"grade": "A", "detail": "已有MP3，待本地听测/许可验收。未下载、转码、剪辑或试听二进制；入库后再做响度、头尾、爆音、混音避让和源文件哈希验收。"}
- 可seek性：不适用（静态素材）
- 维护状态：{"snapshot_checked": "2026-10-02 UTC", "note": "只读元数据与文本审计；不保证听感或Content ID状态", "last_commit": "2026-09-15T04:24:02Z", "commit": "f8d463c05c814804b786f9c8a5683d1abcd954da"}
- 风险：["项目较新；README的40/9与旧标题31/8、WAV不入库说法存在漂移。该pin实际49 WAV+49 MP3；以树和measured.csv为准。", "发布者声称无版权/Content ID风险不是保证，本报告不背书。这里是代码DSP合成，已读生成代码，没有把模型生成音频当素材引入。", "尚未试听、未重新测量，公开duration/LUFS只是发布者数据；没有成品stems。"]

可粘贴署名：

pop_bubble, notification_ding, typing_keyboard, type_key_single, error_buzz, coin_ping, air_horn_meme, whoosh_transition, riser_tension, boom_cinematic — RezaParsian — CC0 1.0 (https://creativecommons.org/publicdomain/zero/1.0/). Source: https://github.com/RezaParsian/free-sfx-bgm-pack/tree/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/sfx. Modified: [填写截取/混音/转码，或 none].（署名自愿）

放置位置：视频简介或片尾署名；可再分发素材包附 ATTRIBUTION 与许可文本。CC0署名为自愿溯源。

## A2-09 · ESC-50 laughing：1-33658-A-26.wav

结论：备选：真实笑声已找到；NC隔离，不作为通用商用默认

- 仓库：https://github.com/karolpiczak/ESC-50
- 固定commit：33c8ce9eb2cf0b1c2f8bcf322eb349b6be34dbb6
- 许可与实际许可文件：{"spdx": "CC-BY-NC-3.0", "path": "LICENSE", "url": "https://github.com/karolpiczak/ESC-50/blob/33c8ce9eb2cf0b1c2f8bcf322eb349b6be34dbb6/LICENSE", "scope": "数据集整体CC-BY-NC-3.0；此条源录音在LICENSE明列CC0。按数据集取用路线保守NC隔离，代码许可不覆盖音频。"}
- 义务：{"attribution": true, "share_alike": false, "non_commercial": true, "no_derivatives": false, "note": "本报告保守按取用的数据集NC范围处理，不把单个原录音CC0自动等同整个数据集可商用。商业项目应回到原音频另行确认与获取，且受本轮禁止站外下载约束。"}
- 内容与证据：{"kind": "GitHub实际录音数据集中的单项", "files": ["https://github.com/karolpiczak/ESC-50/blob/33c8ce9eb2cf0b1c2f8bcf322eb349b6be34dbb6/audio/1-33658-A-26.wav"], "author": "sagetyrtle（pin许可表作者名）；数据集整理Karol J. Piczak", "source_title": "laughter.wav", "evidence": ["https://github.com/karolpiczak/ESC-50/blob/33c8ce9eb2cf0b1c2f8bcf322eb349b6be34dbb6/LICENSE", "https://github.com/karolpiczak/ESC-50/blob/33c8ce9eb2cf0b1c2f8bcf322eb349b6be34dbb6/meta/esc50.csv"], "upstream_external_lead": "https://freesound.org/people/sagetyrtle/sounds/33658/", "mapping": "真实笑声，非语言笑场；不是AI音频", "duration_sec": 5, "duration_basis": "ESC-50 README统一5秒规范，未自行测量", "notes": "LICENSE旧条目标成1-33658-A.ogg；meta新格式映射为1-33658-A-26.wav，源ID33658一致", "usage_mapping": ["搞笑laugh"], "size_metadata": {"basis": "未查明；ESC单项依据固定许可证和CSV映射，未读取二进制或查询文件体积。", "bytes": null}}
- 用途映射：["media"]
- 产品线：["card", "explainer", "showcase"]
- 音频元数据：{"format": "WAV、44.1kHz mono为README数据集规范；不是原生MP3", "duration_sec": 5, "bpm": "不适用", "timeline_validation": "作为本地静态音频文件按固定时间线调度；跳转到中段与重复渲染，检查首音偏移、尾音及loop接点。不要依赖实时WebAudio播放时钟。"}
- 适配：{"grade": "B", "detail": "WAV/OGG/FLAC需统一转MP3并重新验收。未下载、转码、剪辑或试听二进制；入库后再做响度、头尾、爆音、混音避让和源文件哈希验收。"}
- 可seek性：不适用（静态素材）
- 维护状态：{"snapshot_checked": "2026-10-02 UTC", "note": "只读元数据与文本审计；不保证听感或Content ID状态", "last_commit": "未查明（commit已固定，未查提交日期）", "commit": "33c8ce9eb2cf0b1c2f8bcf322eb349b6be34dbb6"}
- 风险：["不是专业短SFX包，可能含环境底噪、切边或多个笑声，必须试听后裁剪。", "NC用途允许纳入候选但须隔离到非商业目录；不能仅凭视频暂未收费推定非商业。", "原录音和数据集权利范围不同；许可证中的旧扩展名需保留映射证据。", "真实人声的肖像/人格/隐私等权利不由版权授权自动清理；不要用于可识别人物的敏感、诽谤或背书语境。"]

可粘贴署名：

“laughter.wav” by sagetyrtle, source clip33658 (CC0; https://freesound.org/people/sagetyrtle/sounds/33658/). Excerpt “1-33658-A-26.wav” from ESC-50, Karol J. Piczak — dataset CC BY-NC 3.0 (https://creativecommons.org/licenses/by-nc/3.0/). Source: https://github.com/karolpiczak/ESC-50/blob/33c8ce9eb2cf0b1c2f8bcf322eb349b6be34dbb6/audio/1-33658-A-26.wav. Modified: [填写裁剪/转码/混音，或 none].

放置位置：视频简介或片尾署名，并提供可访问的来源与许可链接；再分发素材包附完整ATTRIBUTION与许可文本。

