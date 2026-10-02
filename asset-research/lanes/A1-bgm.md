# A1 背景音乐与独立短音标调查

检索日：2026-10-02 UTC。结果是“源与许可可审计的候选”，不是听音验收。严格门槛：GitHub内实际文件 + 固定40位commit + 实际LICENSE/COPYING。README单独声明不满足本调查的LICENSE文件门槛；NC可列条件候选，ND与AI生成排除。没有下载音频/ZIP、没有运行生成器、没有转码。

## 建议与缺口

优先五项：A1-01科技、A1-02 lo-fi、A1-03轻快、A1-10作曲者小选集、A1-11独立sting池。A1-04搞笑、A1-05悬疑、A1-06环境、A1-07/09电子补充。它们是来源优先级，不是听感质量排名。温暖与史诗目前只有Tanner选曲方向，未以试听证实；不能为凑齐八种风格宣布全部覆盖。

2–5秒sting必须独立管理：Kenney85条jingle提供筛选池，但逐条时长未知。本轮没有一条已测合格的2–5秒音乐sting；Reza的logo_sting元数据1.8秒、hook_loop_8s元数据7.74秒，都不算满足。3秒boom、4.2秒gong是SFX，不冒充BGM sting。

源码合成与AI生成分开：Reza用可读DSP公式与固定/伪随机种子生成，暂无音频模型调用证据，因此作为程序合成候选；这不证明其代码作者完全没用AI辅助，也不保证所有版权/平台权利。

许可重点：CC-BY必须作者/作品/许可链接/改动说明；CC-BY-SA的同步视频属于改编材料，不能只给音轨挂SA而忽略视频发布条件；NC单独隔离；仓库代码开源不自动覆盖音频。

## A1-01 · bgm_tech_explainer

结论：首推：科技讲解优先试听

- 仓库：https://github.com/RezaParsian/free-sfx-bgm-pack
- 固定commit：f8d463c05c814804b786f9c8a5683d1abcd954da
- 许可与实际许可文件：{"spdx": "CC0-1.0", "path": "LICENSE", "url": "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/LICENSE", "scope": "sfx-lab/代码另为MIT；audio-pack/音频明确CC0"}
- 义务：{"attribution": false, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "保留许可与来源证据；录音/曲目和程序许可分开核对"}
- 内容与证据：{"kind": "GitHub实际曲目", "mood": "科技/电子", "files": ["https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/bgm/bgm_tech_explainer.mp3", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/bgm/bgm_tech_explainer.wav"], "metadata_evidence": ["https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/measured.csv", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/sfx-lab/build_bgm.py"], "instrumental": "是，按纯乐器DSP生成代码；未听测", "loop": "仅hook宣称loop；其代码仍首尾50ms淡变，须测接点。其余为淡入淡出完整段，不宣称无缝loop。", "clean_ending": "代码淡出，不等于自然乐句收尾", "stems": "未提供音频stems；生成源码存在，可另行授权改编后导出", "usage_mapping": ["科技/电子", "背景音乐"], "size_metadata": {"basis": "GitHub固定树blob.size；只统计本条files所列文件/目录内音频，不含文本、目录外preview或其他包", "by_format": {".mp3": {"file_count": 1, "sum_bytes": 782462}, ".wav": {"file_count": 1, "sum_bytes": 5740516}}, "unique_blob_bytes": 6522978, "unique_blob_count": 2, "note": "unique值按Git blob SHA去重；不同编码版本仍是不同blob，不按作品跨格式去重。未下载测量。"}}
- 用途映射：["media"]
- 产品线：["explainer"]
- 音频元数据：{"format": "仓库已供MP3(README称192kbps)与WAV；不是仅WAV待转码", "duration_sec": 32.54, "bpm": 118, "integrated_lufs_publisher": "-20.0", "duration_basis": "发布者measured.csv，未自行测量", "dependencies": "使用成品音频无需运行生成器或模型", "timeline_validation": "作为本地静态音频文件按固定时间线调度；跳转到中段与重复渲染，检查首音偏移、尾音及loop接点。不要依赖实时WebAudio播放时钟。"}
- 适配：{"grade": "A", "detail": "已有MP3，待本地听测/许可验收。未下载、转码、剪辑或试听二进制；入库后再做响度、头尾、爆音、混音避让和源文件哈希验收。"}
- 可seek性：不适用（静态素材）
- 维护状态：{"snapshot_checked": "2026-10-02 UTC", "note": "只读元数据与文本审计；不保证听感或Content ID状态", "last_commit": "2026-09-15T04:24:02Z", "commit": "f8d463c05c814804b786f9c8a5683d1abcd954da"}
- 风险：["项目较新；README的40/9与旧标题31/8、WAV不入库说法存在漂移。该pin实际49 WAV+49 MP3；以树和measured.csv为准。", "发布者声称无版权/Content ID风险不是保证，本报告不背书。这里是代码DSP合成，已读生成代码，没有把模型生成音频当素材引入。", "尚未试听、未重新测量，公开duration/LUFS只是发布者数据；没有成品stems。"]

可粘贴署名：

bgm_tech_explainer — RezaParsian — CC0 1.0 (https://creativecommons.org/publicdomain/zero/1.0/). Source: https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/bgm/bgm_tech_explainer.mp3. Modified: [填写剪辑/淡变/调音/转码，或 none].（署名自愿）

放置位置：视频简介或片尾署名；可再分发素材包附 ATTRIBUTION 与许可文本。CC0署名为自愿溯源。

## A1-02 · bgm_lofi_focus

结论：首推：长讲解低密度备选

- 仓库：https://github.com/RezaParsian/free-sfx-bgm-pack
- 固定commit：f8d463c05c814804b786f9c8a5683d1abcd954da
- 许可与实际许可文件：{"spdx": "CC0-1.0", "path": "LICENSE", "url": "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/LICENSE", "scope": "sfx-lab/代码另为MIT；audio-pack/音频明确CC0"}
- 义务：{"attribution": false, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "保留许可与来源证据；录音/曲目和程序许可分开核对"}
- 内容与证据：{"kind": "GitHub实际曲目", "mood": "lo-fi", "files": ["https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/bgm/bgm_lofi_focus.mp3", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/bgm/bgm_lofi_focus.wav"], "metadata_evidence": ["https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/measured.csv", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/sfx-lab/build_bgm.py"], "instrumental": "是，按纯乐器DSP生成代码；未听测", "loop": "仅hook宣称loop；其代码仍首尾50ms淡变，须测接点。其余为淡入淡出完整段，不宣称无缝loop。", "clean_ending": "代码淡出，不等于自然乐句收尾", "stems": "未提供音频stems；生成源码存在，可另行授权改编后导出", "usage_mapping": ["lo-fi", "背景音乐"], "size_metadata": {"basis": "GitHub固定树blob.size；只统计本条files所列文件/目录内音频，不含文本、目录外preview或其他包", "by_format": {".mp3": {"file_count": 1, "sum_bytes": 935435}, ".wav": {"file_count": 1, "sum_bytes": 6865340}}, "unique_blob_bytes": 7800775, "unique_blob_count": 2, "note": "unique值按Git blob SHA去重；不同编码版本仍是不同blob，不按作品跨格式去重。未下载测量。"}}
- 用途映射：["media"]
- 产品线：["explainer"]
- 音频元数据：{"format": "仓库已供MP3(README称192kbps)与WAV；不是仅WAV待转码", "duration_sec": 38.92, "bpm": 74, "integrated_lufs_publisher": "-19.9", "duration_basis": "发布者measured.csv，未自行测量", "dependencies": "使用成品音频无需运行生成器或模型", "timeline_validation": "作为本地静态音频文件按固定时间线调度；跳转到中段与重复渲染，检查首音偏移、尾音及loop接点。不要依赖实时WebAudio播放时钟。"}
- 适配：{"grade": "A", "detail": "已有MP3，待本地听测/许可验收。未下载、转码、剪辑或试听二进制；入库后再做响度、头尾、爆音、混音避让和源文件哈希验收。"}
- 可seek性：不适用（静态素材）
- 维护状态：{"snapshot_checked": "2026-10-02 UTC", "note": "只读元数据与文本审计；不保证听感或Content ID状态", "last_commit": "2026-09-15T04:24:02Z", "commit": "f8d463c05c814804b786f9c8a5683d1abcd954da"}
- 风险：["项目较新；README的40/9与旧标题31/8、WAV不入库说法存在漂移。该pin实际49 WAV+49 MP3；以树和measured.csv为准。", "发布者声称无版权/Content ID风险不是保证，本报告不背书。这里是代码DSP合成，已读生成代码，没有把模型生成音频当素材引入。", "尚未试听、未重新测量，公开duration/LUFS只是发布者数据；没有成品stems。"]

可粘贴署名：

bgm_lofi_focus — RezaParsian — CC0 1.0 (https://creativecommons.org/publicdomain/zero/1.0/). Source: https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/bgm/bgm_lofi_focus.mp3. Modified: [填写剪辑/淡变/调音/转码，或 none].（署名自愿）

放置位置：视频简介或片尾署名；可再分发素材包附 ATTRIBUTION 与许可文本。CC0署名为自愿溯源。

## A1-03 · bgm_upbeat_vlog

结论：首推：轻快showcase优先试听

- 仓库：https://github.com/RezaParsian/free-sfx-bgm-pack
- 固定commit：f8d463c05c814804b786f9c8a5683d1abcd954da
- 许可与实际许可文件：{"spdx": "CC0-1.0", "path": "LICENSE", "url": "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/LICENSE", "scope": "sfx-lab/代码另为MIT；audio-pack/音频明确CC0"}
- 义务：{"attribution": false, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "保留许可与来源证据；录音/曲目和程序许可分开核对"}
- 内容与证据：{"kind": "GitHub实际曲目", "mood": "轻快", "files": ["https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/bgm/bgm_upbeat_vlog.mp3", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/bgm/bgm_upbeat_vlog.wav"], "metadata_evidence": ["https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/measured.csv", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/sfx-lab/build_bgm.py"], "instrumental": "是，按纯乐器DSP生成代码；未听测", "loop": "仅hook宣称loop；其代码仍首尾50ms淡变，须测接点。其余为淡入淡出完整段，不宣称无缝loop。", "clean_ending": "代码淡出，不等于自然乐句收尾", "stems": "未提供音频stems；生成源码存在，可另行授权改编后导出", "usage_mapping": ["轻快", "背景音乐"], "size_metadata": {"basis": "GitHub固定树blob.size；只统计本条files所列文件/目录内音频，不含文本、目录外preview或其他包", "by_format": {".mp3": {"file_count": 1, "sum_bytes": 618831}, ".wav": {"file_count": 1, "sum_bytes": 4536044}}, "unique_blob_bytes": 5154875, "unique_blob_count": 2, "note": "unique值按Git blob SHA去重；不同编码版本仍是不同blob，不按作品跨格式去重。未下载测量。"}}
- 用途映射：["media"]
- 产品线：["showcase"]
- 音频元数据：{"format": "仓库已供MP3(README称192kbps)与WAV；不是仅WAV待转码", "duration_sec": 25.71, "bpm": 112, "integrated_lufs_publisher": "-20.2", "duration_basis": "发布者measured.csv，未自行测量", "dependencies": "使用成品音频无需运行生成器或模型", "timeline_validation": "作为本地静态音频文件按固定时间线调度；跳转到中段与重复渲染，检查首音偏移、尾音及loop接点。不要依赖实时WebAudio播放时钟。"}
- 适配：{"grade": "A", "detail": "已有MP3，待本地听测/许可验收。未下载、转码、剪辑或试听二进制；入库后再做响度、头尾、爆音、混音避让和源文件哈希验收。"}
- 可seek性：不适用（静态素材）
- 维护状态：{"snapshot_checked": "2026-10-02 UTC", "note": "只读元数据与文本审计；不保证听感或Content ID状态", "last_commit": "2026-09-15T04:24:02Z", "commit": "f8d463c05c814804b786f9c8a5683d1abcd954da"}
- 风险：["项目较新；README的40/9与旧标题31/8、WAV不入库说法存在漂移。该pin实际49 WAV+49 MP3；以树和measured.csv为准。", "发布者声称无版权/Content ID风险不是保证，本报告不背书。这里是代码DSP合成，已读生成代码，没有把模型生成音频当素材引入。", "尚未试听、未重新测量，公开duration/LUFS只是发布者数据；没有成品stems。"]

可粘贴署名：

bgm_upbeat_vlog — RezaParsian — CC0 1.0 (https://creativecommons.org/publicdomain/zero/1.0/). Source: https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/bgm/bgm_upbeat_vlog.mp3. Modified: [填写剪辑/淡变/调音/转码，或 none].（署名自愿）

放置位置：视频简介或片尾署名；可再分发素材包附 ATTRIBUTION 与许可文本。CC0署名为自愿溯源。

## A1-04 · bgm_playful_marimba

结论：备选：轻喜剧/纠错段落

- 仓库：https://github.com/RezaParsian/free-sfx-bgm-pack
- 固定commit：f8d463c05c814804b786f9c8a5683d1abcd954da
- 许可与实际许可文件：{"spdx": "CC0-1.0", "path": "LICENSE", "url": "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/LICENSE", "scope": "sfx-lab/代码另为MIT；audio-pack/音频明确CC0"}
- 义务：{"attribution": false, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "保留许可与来源证据；录音/曲目和程序许可分开核对"}
- 内容与证据：{"kind": "GitHub实际曲目", "mood": "搞笑/轻快", "files": ["https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/bgm/bgm_playful_marimba.mp3", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/bgm/bgm_playful_marimba.wav"], "metadata_evidence": ["https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/measured.csv", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/sfx-lab/build_bgm.py"], "instrumental": "是，按纯乐器DSP生成代码；未听测", "loop": "仅hook宣称loop；其代码仍首尾50ms淡变，须测接点。其余为淡入淡出完整段，不宣称无缝loop。", "clean_ending": "代码淡出，不等于自然乐句收尾", "stems": "未提供音频stems；生成源码存在，可另行授权改编后导出", "usage_mapping": ["搞笑/轻快", "背景音乐"], "size_metadata": {"basis": "GitHub固定树blob.size；只统计本条files所列文件/目录内音频，不含文本、目录外preview或其他包", "by_format": {".mp3": {"file_count": 1, "sum_bytes": 666479}, ".wav": {"file_count": 1, "sum_bytes": 4884964}}, "unique_blob_bytes": 5551443, "unique_blob_count": 2, "note": "unique值按Git blob SHA去重；不同编码版本仍是不同blob，不按作品跨格式去重。未下载测量。"}}
- 用途映射：["media"]
- 产品线：["card"]
- 音频元数据：{"format": "仓库已供MP3(README称192kbps)与WAV；不是仅WAV待转码", "duration_sec": 27.69, "bpm": 104, "integrated_lufs_publisher": "-20.2", "duration_basis": "发布者measured.csv，未自行测量", "dependencies": "使用成品音频无需运行生成器或模型", "timeline_validation": "作为本地静态音频文件按固定时间线调度；跳转到中段与重复渲染，检查首音偏移、尾音及loop接点。不要依赖实时WebAudio播放时钟。"}
- 适配：{"grade": "A", "detail": "已有MP3，待本地听测/许可验收。未下载、转码、剪辑或试听二进制；入库后再做响度、头尾、爆音、混音避让和源文件哈希验收。"}
- 可seek性：不适用（静态素材）
- 维护状态：{"snapshot_checked": "2026-10-02 UTC", "note": "只读元数据与文本审计；不保证听感或Content ID状态", "last_commit": "2026-09-15T04:24:02Z", "commit": "f8d463c05c814804b786f9c8a5683d1abcd954da"}
- 风险：["项目较新；README的40/9与旧标题31/8、WAV不入库说法存在漂移。该pin实际49 WAV+49 MP3；以树和measured.csv为准。", "发布者声称无版权/Content ID风险不是保证，本报告不背书。这里是代码DSP合成，已读生成代码，没有把模型生成音频当素材引入。", "尚未试听、未重新测量，公开duration/LUFS只是发布者数据；没有成品stems。"]

可粘贴署名：

bgm_playful_marimba — RezaParsian — CC0 1.0 (https://creativecommons.org/publicdomain/zero/1.0/). Source: https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/bgm/bgm_playful_marimba.mp3. Modified: [填写剪辑/淡变/调音/转码，或 none].（署名自愿）

放置位置：视频简介或片尾署名；可再分发素材包附 ATTRIBUTION 与许可文本。CC0署名为自愿溯源。

## A1-05 · bgm_cinematic_tension

结论：备选：悬念铺垫

- 仓库：https://github.com/RezaParsian/free-sfx-bgm-pack
- 固定commit：f8d463c05c814804b786f9c8a5683d1abcd954da
- 许可与实际许可文件：{"spdx": "CC0-1.0", "path": "LICENSE", "url": "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/LICENSE", "scope": "sfx-lab/代码另为MIT；audio-pack/音频明确CC0"}
- 义务：{"attribution": false, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "保留许可与来源证据；录音/曲目和程序许可分开核对"}
- 内容与证据：{"kind": "GitHub实际曲目", "mood": "悬疑", "files": ["https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/bgm/bgm_cinematic_tension.mp3", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/bgm/bgm_cinematic_tension.wav"], "metadata_evidence": ["https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/measured.csv", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/sfx-lab/build_bgm.py"], "instrumental": "是，按纯乐器DSP生成代码；未听测", "loop": "仅hook宣称loop；其代码仍首尾50ms淡变，须测接点。其余为淡入淡出完整段，不宣称无缝loop。", "clean_ending": "代码淡出，不等于自然乐句收尾", "stems": "未提供音频stems；生成源码存在，可另行授权改编后导出", "usage_mapping": ["悬疑", "背景音乐"], "size_metadata": {"basis": "GitHub固定树blob.size；只统计本条files所列文件/目录内音频，不含文本、目录外preview或其他包", "by_format": {".mp3": {"file_count": 1, "sum_bytes": 721649}, ".wav": {"file_count": 1, "sum_bytes": 5292044}}, "unique_blob_bytes": 6013693, "unique_blob_count": 2, "note": "unique值按Git blob SHA去重；不同编码版本仍是不同blob，不按作品跨格式去重。未下载测量。"}}
- 用途映射：["media"]
- 产品线：["showcase"]
- 音频元数据：{"format": "仓库已供MP3(README称192kbps)与WAV；不是仅WAV待转码", "duration_sec": 30.0, "bpm": 80, "integrated_lufs_publisher": "-19.9", "duration_basis": "发布者measured.csv，未自行测量", "dependencies": "使用成品音频无需运行生成器或模型", "timeline_validation": "作为本地静态音频文件按固定时间线调度；跳转到中段与重复渲染，检查首音偏移、尾音及loop接点。不要依赖实时WebAudio播放时钟。"}
- 适配：{"grade": "A", "detail": "已有MP3，待本地听测/许可验收。未下载、转码、剪辑或试听二进制；入库后再做响度、头尾、爆音、混音避让和源文件哈希验收。"}
- 可seek性：不适用（静态素材）
- 维护状态：{"snapshot_checked": "2026-10-02 UTC", "note": "只读元数据与文本审计；不保证听感或Content ID状态", "last_commit": "2026-09-15T04:24:02Z", "commit": "f8d463c05c814804b786f9c8a5683d1abcd954da"}
- 风险：["项目较新；README的40/9与旧标题31/8、WAV不入库说法存在漂移。该pin实际49 WAV+49 MP3；以树和measured.csv为准。", "发布者声称无版权/Content ID风险不是保证，本报告不背书。这里是代码DSP合成，已读生成代码，没有把模型生成音频当素材引入。", "尚未试听、未重新测量，公开duration/LUFS只是发布者数据；没有成品stems。"]

可粘贴署名：

bgm_cinematic_tension — RezaParsian — CC0 1.0 (https://creativecommons.org/publicdomain/zero/1.0/). Source: https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/bgm/bgm_cinematic_tension.mp3. Modified: [填写剪辑/淡变/调音/转码，或 none].（署名自愿）

放置位置：视频简介或片尾署名；可再分发素材包附 ATTRIBUTION 与许可文本。CC0署名为自愿溯源。

## A1-06 · bgm_ambient_underscore

结论：备选：中性环境床

- 仓库：https://github.com/RezaParsian/free-sfx-bgm-pack
- 固定commit：f8d463c05c814804b786f9c8a5683d1abcd954da
- 许可与实际许可文件：{"spdx": "CC0-1.0", "path": "LICENSE", "url": "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/LICENSE", "scope": "sfx-lab/代码另为MIT；audio-pack/音频明确CC0"}
- 义务：{"attribution": false, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "保留许可与来源证据；录音/曲目和程序许可分开核对"}
- 内容与证据：{"kind": "GitHub实际曲目", "mood": "环境/温暖候选（温暖感未试听确认）", "files": ["https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/bgm/bgm_ambient_underscore.mp3", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/bgm/bgm_ambient_underscore.wav"], "metadata_evidence": ["https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/measured.csv", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/sfx-lab/build_bgm.py"], "instrumental": "是，按纯乐器DSP生成代码；未听测", "loop": "仅hook宣称loop；其代码仍首尾50ms淡变，须测接点。其余为淡入淡出完整段，不宣称无缝loop。", "clean_ending": "代码淡出，不等于自然乐句收尾", "stems": "未提供音频stems；生成源码存在，可另行授权改编后导出", "usage_mapping": ["环境/温暖候选（温暖感未试听确认）", "背景音乐"], "size_metadata": {"basis": "GitHub固定树blob.size；只统计本条files所列文件/目录内音频，不含文本、目录外preview或其他包", "by_format": {".mp3": {"file_count": 1, "sum_bytes": 1153610}, ".wav": {"file_count": 1, "sum_bytes": 8467244}}, "unique_blob_bytes": 9620854, "unique_blob_count": 2, "note": "unique值按Git blob SHA去重；不同编码版本仍是不同blob，不按作品跨格式去重。未下载测量。"}}
- 用途映射：["media"]
- 产品线：["explainer"]
- 音频元数据：{"format": "仓库已供MP3(README称192kbps)与WAV；不是仅WAV待转码", "duration_sec": 48.0, "bpm": 60, "integrated_lufs_publisher": "-20.4", "duration_basis": "发布者measured.csv，未自行测量", "dependencies": "使用成品音频无需运行生成器或模型", "timeline_validation": "作为本地静态音频文件按固定时间线调度；跳转到中段与重复渲染，检查首音偏移、尾音及loop接点。不要依赖实时WebAudio播放时钟。"}
- 适配：{"grade": "A", "detail": "已有MP3，待本地听测/许可验收。未下载、转码、剪辑或试听二进制；入库后再做响度、头尾、爆音、混音避让和源文件哈希验收。"}
- 可seek性：不适用（静态素材）
- 维护状态：{"snapshot_checked": "2026-10-02 UTC", "note": "只读元数据与文本审计；不保证听感或Content ID状态", "last_commit": "2026-09-15T04:24:02Z", "commit": "f8d463c05c814804b786f9c8a5683d1abcd954da"}
- 风险：["项目较新；README的40/9与旧标题31/8、WAV不入库说法存在漂移。该pin实际49 WAV+49 MP3；以树和measured.csv为准。", "发布者声称无版权/Content ID风险不是保证，本报告不背书。这里是代码DSP合成，已读生成代码，没有把模型生成音频当素材引入。", "尚未试听、未重新测量，公开duration/LUFS只是发布者数据；没有成品stems。"]

可粘贴署名：

bgm_ambient_underscore — RezaParsian — CC0 1.0 (https://creativecommons.org/publicdomain/zero/1.0/). Source: https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/bgm/bgm_ambient_underscore.mp3. Modified: [填写剪辑/淡变/调音/转码，或 none].（署名自愿）

放置位置：视频简介或片尾署名；可再分发素材包附 ATTRIBUTION 与许可文本。CC0署名为自愿溯源。

## A1-07 · bgm_terminal_flow

结论：备选：屏录/终端过程

- 仓库：https://github.com/RezaParsian/free-sfx-bgm-pack
- 固定commit：f8d463c05c814804b786f9c8a5683d1abcd954da
- 许可与实际许可文件：{"spdx": "CC0-1.0", "path": "LICENSE", "url": "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/LICENSE", "scope": "sfx-lab/代码另为MIT；audio-pack/音频明确CC0"}
- 义务：{"attribution": false, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "保留许可与来源证据；录音/曲目和程序许可分开核对"}
- 内容与证据：{"kind": "GitHub实际曲目", "mood": "电子/极简", "files": ["https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/bgm/bgm_terminal_flow.mp3", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/bgm/bgm_terminal_flow.wav"], "metadata_evidence": ["https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/measured.csv", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/sfx-lab/build_bgm.py"], "instrumental": "是，按纯乐器DSP生成代码；未听测", "loop": "仅hook宣称loop；其代码仍首尾50ms淡变，须测接点。其余为淡入淡出完整段，不宣称无缝loop。", "clean_ending": "代码淡出，不等于自然乐句收尾", "stems": "未提供音频stems；生成源码存在，可另行授权改编后导出", "usage_mapping": ["电子/极简", "背景音乐"], "size_metadata": {"basis": "GitHub固定树blob.size；只统计本条files所列文件/目录内音频，不含文本、目录外preview或其他包", "by_format": {".mp3": {"file_count": 1, "sum_bytes": 878384}, ".wav": {"file_count": 1, "sum_bytes": 6442476}}, "unique_blob_bytes": 7320860, "unique_blob_count": 2, "note": "unique值按Git blob SHA去重；不同编码版本仍是不同blob，不按作品跨格式去重。未下载测量。"}}
- 用途映射：["media"]
- 产品线：["explainer"]
- 音频元数据：{"format": "仓库已供MP3(README称192kbps)与WAV；不是仅WAV待转码", "duration_sec": 36.52, "bpm": 92, "integrated_lufs_publisher": "-20.0", "duration_basis": "发布者measured.csv，未自行测量", "dependencies": "使用成品音频无需运行生成器或模型", "timeline_validation": "作为本地静态音频文件按固定时间线调度；跳转到中段与重复渲染，检查首音偏移、尾音及loop接点。不要依赖实时WebAudio播放时钟。"}
- 适配：{"grade": "A", "detail": "已有MP3，待本地听测/许可验收。未下载、转码、剪辑或试听二进制；入库后再做响度、头尾、爆音、混音避让和源文件哈希验收。"}
- 可seek性：不适用（静态素材）
- 维护状态：{"snapshot_checked": "2026-10-02 UTC", "note": "只读元数据与文本审计；不保证听感或Content ID状态", "last_commit": "2026-09-15T04:24:02Z", "commit": "f8d463c05c814804b786f9c8a5683d1abcd954da"}
- 风险：["项目较新；README的40/9与旧标题31/8、WAV不入库说法存在漂移。该pin实际49 WAV+49 MP3；以树和measured.csv为准。", "发布者声称无版权/Content ID风险不是保证，本报告不背书。这里是代码DSP合成，已读生成代码，没有把模型生成音频当素材引入。", "尚未试听、未重新测量，公开duration/LUFS只是发布者数据；没有成品stems。"]

可粘贴署名：

bgm_terminal_flow — RezaParsian — CC0 1.0 (https://creativecommons.org/publicdomain/zero/1.0/). Source: https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/bgm/bgm_terminal_flow.mp3. Modified: [填写剪辑/淡变/调音/转码，或 none].（署名自愿）

放置位置：视频简介或片尾署名；可再分发素材包附 ATTRIBUTION 与许可文本。CC0署名为自愿溯源。

## A1-08 · bgm_screen_bed

结论：备选：低干扰讲解

- 仓库：https://github.com/RezaParsian/free-sfx-bgm-pack
- 固定commit：f8d463c05c814804b786f9c8a5683d1abcd954da
- 许可与实际许可文件：{"spdx": "CC0-1.0", "path": "LICENSE", "url": "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/LICENSE", "scope": "sfx-lab/代码另为MIT；audio-pack/音频明确CC0"}
- 义务：{"attribution": false, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "保留许可与来源证据；录音/曲目和程序许可分开核对"}
- 内容与证据：{"kind": "GitHub实际曲目", "mood": "稀疏无鼓背景", "files": ["https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/bgm/bgm_screen_bed.mp3", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/bgm/bgm_screen_bed.wav"], "metadata_evidence": ["https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/measured.csv", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/sfx-lab/build_bgm.py"], "instrumental": "是，按纯乐器DSP生成代码；未听测", "loop": "仅hook宣称loop；其代码仍首尾50ms淡变，须测接点。其余为淡入淡出完整段，不宣称无缝loop。", "clean_ending": "代码淡出，不等于自然乐句收尾", "stems": "未提供音频stems；生成源码存在，可另行授权改编后导出", "usage_mapping": ["稀疏无鼓背景", "背景音乐"], "size_metadata": {"basis": "GitHub固定树blob.size；只统计本条files所列文件/目录内音频，不含文本、目录外preview或其他包", "by_format": {".mp3": {"file_count": 1, "sum_bytes": 961767}, ".wav": {"file_count": 1, "sum_bytes": 7056044}}, "unique_blob_bytes": 8017811, "unique_blob_count": 2, "note": "unique值按Git blob SHA去重；不同编码版本仍是不同blob，不按作品跨格式去重。未下载测量。"}}
- 用途映射：["media"]
- 产品线：["explainer"]
- 音频元数据：{"format": "仓库已供MP3(README称192kbps)与WAV；不是仅WAV待转码", "duration_sec": 40.0, "bpm": 60, "integrated_lufs_publisher": "-19.9", "duration_basis": "发布者measured.csv，未自行测量", "dependencies": "使用成品音频无需运行生成器或模型", "timeline_validation": "作为本地静态音频文件按固定时间线调度；跳转到中段与重复渲染，检查首音偏移、尾音及loop接点。不要依赖实时WebAudio播放时钟。"}
- 适配：{"grade": "A", "detail": "已有MP3，待本地听测/许可验收。未下载、转码、剪辑或试听二进制；入库后再做响度、头尾、爆音、混音避让和源文件哈希验收。"}
- 可seek性：不适用（静态素材）
- 维护状态：{"snapshot_checked": "2026-10-02 UTC", "note": "只读元数据与文本审计；不保证听感或Content ID状态", "last_commit": "2026-09-15T04:24:02Z", "commit": "f8d463c05c814804b786f9c8a5683d1abcd954da"}
- 风险：["项目较新；README的40/9与旧标题31/8、WAV不入库说法存在漂移。该pin实际49 WAV+49 MP3；以树和measured.csv为准。", "发布者声称无版权/Content ID风险不是保证，本报告不背书。这里是代码DSP合成，已读生成代码，没有把模型生成音频当素材引入。", "尚未试听、未重新测量，公开duration/LUFS只是发布者数据；没有成品stems。"]

可粘贴署名：

bgm_screen_bed — RezaParsian — CC0 1.0 (https://creativecommons.org/publicdomain/zero/1.0/). Source: https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/bgm/bgm_screen_bed.mp3. Modified: [填写剪辑/淡变/调音/转码，或 none].（署名自愿）

放置位置：视频简介或片尾署名；可再分发素材包附 ATTRIBUTION 与许可文本。CC0署名为自愿溯源。

## A1-09 · bgm_hook_loop_8s

结论：备选：7.74秒hook，禁止误标8秒或2–5秒sting

- 仓库：https://github.com/RezaParsian/free-sfx-bgm-pack
- 固定commit：f8d463c05c814804b786f9c8a5683d1abcd954da
- 许可与实际许可文件：{"spdx": "CC0-1.0", "path": "LICENSE", "url": "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/LICENSE", "scope": "sfx-lab/代码另为MIT；audio-pack/音频明确CC0"}
- 义务：{"attribution": false, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "保留许可与来源证据；录音/曲目和程序许可分开核对"}
- 内容与证据：{"kind": "GitHub实际曲目", "mood": "电子短loop，不是2–5秒sting", "files": ["https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/bgm/bgm_hook_loop_8s.mp3", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/bgm/bgm_hook_loop_8s.wav"], "metadata_evidence": ["https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/measured.csv", "https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/sfx-lab/build_bgm.py"], "instrumental": "是，按纯乐器DSP生成代码；未听测", "loop": "仅hook宣称loop；其代码仍首尾50ms淡变，须测接点。其余为淡入淡出完整段，不宣称无缝loop。", "clean_ending": "代码淡出，不等于自然乐句收尾", "stems": "未提供音频stems；生成源码存在，可另行授权改编后导出", "usage_mapping": ["电子短loop，不是2–5秒sting", "背景音乐"], "size_metadata": {"basis": "GitHub固定树blob.size；只统计本条files所列文件/目录内音频，不含文本、目录外preview或其他包", "by_format": {".mp3": {"file_count": 1, "sum_bytes": 187497}, ".wav": {"file_count": 1, "sum_bytes": 1365720}}, "unique_blob_bytes": 1553217, "unique_blob_count": 2, "note": "unique值按Git blob SHA去重；不同编码版本仍是不同blob，不按作品跨格式去重。未下载测量。"}}
- 用途映射：["media"]
- 产品线：["showcase"]
- 音频元数据：{"format": "仓库已供MP3(README称192kbps)与WAV；不是仅WAV待转码", "duration_sec": 7.74, "bpm": 124, "integrated_lufs_publisher": "-20.2", "duration_basis": "发布者measured.csv，未自行测量", "dependencies": "使用成品音频无需运行生成器或模型", "timeline_validation": "作为本地静态音频文件按固定时间线调度；跳转到中段与重复渲染，检查首音偏移、尾音及loop接点。不要依赖实时WebAudio播放时钟。"}
- 适配：{"grade": "A", "detail": "已有MP3，待本地听测/许可验收。未下载、转码、剪辑或试听二进制；入库后再做响度、头尾、爆音、混音避让和源文件哈希验收。"}
- 可seek性：不适用（静态素材）
- 维护状态：{"snapshot_checked": "2026-10-02 UTC", "note": "只读元数据与文本审计；不保证听感或Content ID状态", "last_commit": "2026-09-15T04:24:02Z", "commit": "f8d463c05c814804b786f9c8a5683d1abcd954da"}
- 风险：["项目较新；README的40/9与旧标题31/8、WAV不入库说法存在漂移。该pin实际49 WAV+49 MP3；以树和measured.csv为准。", "发布者声称无版权/Content ID风险不是保证，本报告不背书。这里是代码DSP合成，已读生成代码，没有把模型生成音频当素材引入。", "尚未试听、未重新测量，公开duration/LUFS只是发布者数据；没有成品stems。", "文件名8s但元数据7.74s；1.8秒logo_sting同样不是2–5秒sting。"]

可粘贴署名：

bgm_hook_loop_8s — RezaParsian — CC0 1.0 (https://creativecommons.org/publicdomain/zero/1.0/). Source: https://github.com/RezaParsian/free-sfx-bgm-pack/blob/f8d463c05c814804b786f9c8a5683d1abcd954da/audio-pack/mp3/bgm/bgm_hook_loop_8s.mp3. Modified: [填写剪辑/淡变/调音/转码，或 none].（署名自愿）

放置位置：视频简介或片尾署名；可再分发素材包附 ATTRIBUTION 与许可文本。CC0署名为自愿溯源。

## A1-10 · Tanner Helland：原作候选小选集

结论：首推：作曲者自托管来源优先；只小选集试听，不能整库盲入

- 仓库：https://github.com/tannerhelland/free-music
- 固定commit：f6bfe16f49feab2181075ab86b13b24740592aa6
- 许可与实际许可文件：{"spdx": "CC-BY-4.0", "path": "LICENSE.md", "url": "https://github.com/tannerhelland/free-music/blob/f6bfe16f49feab2181075ab86b13b24740592aa6/LICENSE.md", "scope": "不借用根代码许可推断音频授权"}
- 义务：{"attribution": true, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "须署名、许可链接、改动说明，保留已有版权/免责声明；允许商业与改编；无SA/NC/ND，禁止施加妨碍许可权利的限制。"}
- 内容与证据：{"kind": "作曲者GitHub实际音频选集", "tracks": ["A Memory Away", "Assault on Mist Castle", "Clowns", "Syntheticity"], "files": ["https://github.com/tannerhelland/free-music/blob/f6bfe16f49feab2181075ab86b13b24740592aa6/mp3/A%20Memory%20Away.mp3", "https://github.com/tannerhelland/free-music/blob/f6bfe16f49feab2181075ab86b13b24740592aa6/mp3/Assault%20on%20Mist%20Castle.mp3", "https://github.com/tannerhelland/free-music/blob/f6bfe16f49feab2181075ab86b13b24740592aa6/mp3/Clowns.mp3", "https://github.com/tannerhelland/free-music/blob/f6bfe16f49feab2181075ab86b13b24740592aa6/mp3/Syntheticity.mp3"], "mood": "温暖/史诗/搞笑/电子为选曲方向，仅凭曲名不能验收，需试听", "instrumental": "未知；本轮没试听", "duration": "未知", "bpm": "未知", "loop": "未知", "clean_ending": "未知", "stems": "没有成套音频stems；这些曲目的MIDI可编辑谱面，不等于stems", "evidence": ["https://github.com/tannerhelland/free-music/blob/f6bfe16f49feab2181075ab86b13b24740592aa6/README.md", "https://github.com/tannerhelland/free-music/blob/f6bfe16f49feab2181075ab86b13b24740592aa6/LICENSE.md"], "usage_mapping": ["温暖候选", "史诗候选", "搞笑候选", "电子候选"], "size_metadata": {"basis": "GitHub固定树blob.size；只统计本条files所列文件/目录内音频，不含文本、目录外preview或其他包", "by_format": {".mp3": {"file_count": 4, "sum_bytes": 22355329}}, "unique_blob_bytes": 22355329, "unique_blob_count": 4, "note": "unique值按Git blob SHA去重；不同编码版本仍是不同blob，不按作品跨格式去重。未下载测量。"}}
- 用途映射：["media"]
- 产品线：["card", "explainer", "showcase"]
- 音频元数据：{"format": "49 MP3/47 MIDI/29 OGG/20 FLAC是全库目录计数，不是本选集数量；所选四曲MP3存在", "duration_sec": null, "bpm": null, "dependencies": "静态音频；MIDI非直接替代的渲染资产，需额外音源及其许可", "timeline_validation": "作为本地静态音频文件按固定时间线调度；跳转到中段与重复渲染，检查首音偏移、尾音及loop接点。不要依赖实时WebAudio播放时钟。"}
- 适配：{"grade": "A", "detail": "已有MP3，待本地听测/许可验收。未下载、转码、剪辑或试听二进制；入库后再做响度、头尾、爆音、混音避让和源文件哈希验收。"}
- 可seek性：不适用（静态素材）
- 维护状态：{"snapshot_checked": "2026-10-02 UTC", "note": "只读元数据与文本审计；不保证听感或Content ID状态", "last_commit": "2020-01-23T22:11:12Z", "commit": "f6bfe16f49feab2181075ab86b13b24740592aa6"}
- 风险：["整库同时存在Aerith/FF7/Castlevania/DragonFyre等明确改编曲，根CC-BY不能替第三方原作清权；本选集不含这些明确改编项。", "即使所选四曲名称没有改编标记，也不代表逐曲权利与听感已完成验收。BPM、时长、loop和纯音乐状态未知。", "不要把MIDI当音频stems，也不要用开源代码许可替换音乐许可。"]

可粘贴署名：

Music: [所用具体曲名] by Tanner Helland — CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Source: https://github.com/tannerhelland/free-music/tree/f6bfe16f49feab2181075ab86b13b24740592aa6. Modified: [填写截取/混音/变速/转码，或 none].

放置位置：视频简介或片尾署名，并提供可访问的来源与许可链接；再分发素材包附完整ATTRIBUTION与许可文本。

## A1-11 · Kenney Music Jingles：独立sting候选池

结论：首推：仅作为2–5秒sting池，待逐条时长/听感验收

- 仓库：https://github.com/OmniTender-Systems/game-audio-assets
- 固定commit：378269191f4219775f113d52dcf7ce7d5c810b5f
- 许可与实际许可文件：{"spdx": "CC0-1.0", "path": "vendor/kenney/music-jingles/License.txt", "url": "https://github.com/OmniTender-Systems/game-audio-assets/blob/378269191f4219775f113d52dcf7ce7d5c810b5f/vendor/kenney/music-jingles/License.txt", "scope": "不借用根代码许可推断音频授权"}
- 义务：{"attribution": false, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "保留许可与来源证据；录音/曲目和程序许可分开核对"}
- 内容与证据：{"kind": "GitHub镜像实际音频包", "files": ["https://github.com/OmniTender-Systems/game-audio-assets/tree/378269191f4219775f113d52dcf7ce7d5c810b5f/vendor/kenney/music-jingles/Audio"], "groups": ["8-Bit", "Hit", "Pizzicato", "Sax", "Steel"], "count": 85, "mood": "短片头/得分/结尾音标候选", "instrumental": "jingle分类；未试听确认所有文件", "duration_sec": "逐文件未知；不能宣称85条全部满足2–5秒", "bpm": "未知", "loop": "短一次性音标用途，未知", "clean_ending": "未知", "stems": "未提供", "upstream_external_lead": "https://kenney.nl/assets/music-jingles", "usage_mapping": ["2–5秒sting筛选池（尚未按时长验收）", "得分", "片头", "片尾"], "size_metadata": {"basis": "GitHub固定树blob.size；只统计本条files所列文件/目录内音频，不含文本、目录外preview或其他包", "by_format": {".ogg": {"file_count": 85, "sum_bytes": 1277396}}, "unique_blob_bytes": 1277396, "unique_blob_count": 85, "note": "unique值按Git blob SHA去重；不同编码版本仍是不同blob，不按作品跨格式去重。未下载测量。"}}
- 用途映射：["media"]
- 产品线：["card", "explainer", "showcase"]
- 音频元数据：{"format": "85 OGG+另有preview；没有原生MP3", "duration_sec": null, "bpm": null, "conversion": "可后续OGG解码后转MP3，标记为转码版本；不会恢复原始有损信息", "timeline_validation": "作为本地静态音频文件按固定时间线调度；跳转到中段与重复渲染，检查首音偏移、尾音及loop接点。不要依赖实时WebAudio播放时钟。"}
- 适配：{"grade": "B", "detail": "WAV/OGG/FLAC需统一转MP3并重新验收。未下载、转码、剪辑或试听二进制；入库后再做响度、头尾、爆音、混音避让和源文件哈希验收。"}
- 可seek性：不适用（静态素材）
- 维护状态：{"snapshot_checked": "2026-10-02 UTC", "note": "只读元数据与文本审计；不保证听感或Content ID状态", "last_commit": "2026-07-13T21:26:30Z", "commit": "378269191f4219775f113d52dcf7ce7d5c810b5f"}
- 风险：["这是第三方镜像；原始License.txt和来源台账存在，但本轮未做与作者原包的二进制哈希比对。", "不让sting代替持续BGM；2–5秒硬条件仍待测量，不能只凭jingles命名通过。"]

可粘贴署名：

Music Jingles by Kenney (https://kenney.nl) — CC0 1.0 (https://creativecommons.org/publicdomain/zero/1.0/). Source mirror: https://github.com/OmniTender-Systems/game-audio-assets/tree/378269191f4219775f113d52dcf7ce7d5c810b5f/vendor/kenney/music-jingles. Modified: [填写OGG→MP3/剪辑等，或 none].（署名自愿）

放置位置：视频简介或片尾署名；可再分发素材包附 ATTRIBUTION 与许可文本。CC0署名为自愿溯源。

## A1-12 · OpenMusic — Airtime Junkies

结论：备选：只用于愿意履行视频同步SA义务的项目

- 仓库：https://github.com/OpenRCT2/OpenMusic
- 固定commit：a1f043dd9543e22a103a242d0e659c25f1ccb56b
- 许可与实际许可文件：{"spdx": "CC-BY-SA-4.0", "path": "COPYING", "url": "https://github.com/OpenRCT2/OpenMusic/blob/a1f043dd9543e22a103a242d0e659c25f1ccb56b/COPYING", "scope": "不借用根代码许可推断音频授权"}
- 义务：{"attribution": true, "share_alike": true, "non_commercial": false, "no_derivatives": false, "note": "CC-BY-SA4.0规定音乐/录音与动态图像定时同步必然构成Adapted Material。共享适配作品需满足SA；不是仅将原音频附件标SA就当然满足视频义务。应由具体发布方式审核。"}
- 内容与证据：{"kind": "GitHub实际FLAC曲目", "files": ["https://github.com/OpenRCT2/OpenMusic/blob/a1f043dd9543e22a103a242d0e659c25f1ccb56b/alternative/openrct2.music.acid/music/0.flac"], "author": "Jalmaan / Karst van Galen Last", "mood": "Acid electronic，object.json标注Acid style", "evidence": ["https://github.com/OpenRCT2/OpenMusic/blob/a1f043dd9543e22a103a242d0e659c25f1ccb56b/alternative/openrct2.music.acid/object.json", "https://github.com/OpenRCT2/OpenMusic/blob/a1f043dd9543e22a103a242d0e659c25f1ccb56b/README.md"], "instrumental": "未知", "duration_sec": null, "bpm": null, "loop": "未知", "clean_ending": "未知", "stems": "未提供", "usage_mapping": ["电子", "showcase音乐"], "size_metadata": {"basis": "GitHub固定树blob.size；只统计本条files所列文件/目录内音频，不含文本、目录外preview或其他包", "by_format": {".flac": {"file_count": 1, "sum_bytes": 15105425}}, "unique_blob_bytes": 15105425, "unique_blob_count": 1, "note": "unique值按Git blob SHA去重；不同编码版本仍是不同blob，不按作品跨格式去重。未下载测量。"}}
- 用途映射：["media"]
- 产品线：["showcase"]
- 音频元数据：{"format": "FLAC；需要后续离线转成视频管线支持格式，没有原生MP3证据", "duration_sec": null, "bpm": null, "timeline_validation": "作为本地静态音频文件按固定时间线调度；跳转到中段与重复渲染，检查首音偏移、尾音及loop接点。不要依赖实时WebAudio播放时钟。"}
- 适配：{"grade": "B", "detail": "WAV/OGG/FLAC需统一转MP3并重新验收。未下载、转码、剪辑或试听二进制；入库后再做响度、头尾、爆音、混音避让和源文件哈希验收。"}
- 可seek性：不适用（静态素材）
- 维护状态：{"snapshot_checked": "2026-10-02 UTC", "note": "只读元数据与文本审计；不保证听感或Content ID状态", "last_commit": "2025-09-15T07:34:55Z", "commit": "a1f043dd9543e22a103a242d0e659c25f1ccb56b"}
- 风险：["会对同步视频触发SA适配义务，默认不进闭源或不愿SA发布的成品线。", "COPYING有明确条款；不要把README的部分传统曲公有领域例外套到这首原创Acid曲。"]

可粘贴署名：

“Airtime Junkies” — Jalmaan (Karst van Galen Last), OpenMusic — CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/). Source: https://github.com/OpenRCT2/OpenMusic/tree/a1f043dd9543e22a103a242d0e659c25f1ccb56b/alternative/openrct2.music.acid. Modified: [填写改动]. Adapted work license: [填写兼容的SA许可及链接].

放置位置：视频简介或片尾署名，并提供可访问的来源与许可链接；再分发素材包附完整ATTRIBUTION与许可文本。SA适配作品还须明确兼容许可。

## A1-X1 · Glorytales

结论：排除：无独立LICENSE文件（不等于断言作者从未授权）

- 仓库：https://github.com/0xabad1dea/glorytales
- 固定commit：b11b570de5b3072fc5f409a3e515a28e62ae56be
- 许可与实际许可文件：{"spdx": null, "path": null, "url": null, "scope": "README声明CC-BY-4.0；不满足独立LICENSE文件门槛，不能入库。"}
- 义务：{"attribution": true, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "README声明CC-BY4.0，若未来补齐接受证据则须署名；当前仍因无独立LICENSE文件排除。此标记不是接受授权证明。"}
- 内容与证据：{"kind": "实际音频但未满足证据门槛", "readme_evidence": "https://github.com/0xabad1dea/glorytales/blob/b11b570de5b3072fc5f409a3e515a28e62ae56be/readme.md", "usage_mapping": [], "size_metadata": {"basis": "未查明；本轮已排除该来源，未追加获取文件体积。", "bytes": null}}
- 用途映射：["media"]
- 产品线：["card", "explainer", "showcase"]
- 音频元数据：{"format": "MP3等存在；未进入入库验证", "timeline_validation": "不适用；本轮排除，不进行入库或时间线验证。"}
- 适配：{"grade": "D", "detail": "本轮排除，不适配入库。未下载、转码、剪辑或试听二进制。"}
- 可seek性：不适用（静态素材）
- 维护状态：{"snapshot_checked": "2026-10-02 UTC", "note": "只读元数据与文本审计；不保证听感或Content ID状态", "last_commit": "2016-08-17T20:22:10Z", "commit": "b11b570de5b3072fc5f409a3e515a28e62ae56be"}
- 风险：["作者README有授权且MP3命名含BPM/loop，然而本调查要求独立LICENSE文件；树中没有，所以不进入接受集合。"]

可粘贴署名：

不提供投产署名模板；本轮排除

放置位置：本轮排除，不提供投产署名。

## A1-X2 · Homebrew VGM jingles

结论：排除：无独立LICENSE文件（不等于断言作者从未授权）

- 仓库：https://github.com/Beatscribe/homebrew_vgm
- 固定commit：5a82f88b87bb442499685c494b7a96278121b4c7
- 许可与实际许可文件：{"spdx": null, "path": null, "url": null, "scope": "README声明CC0；不满足独立LICENSE文件门槛，不能入库。"}
- 义务：{"attribution": false, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "保留许可与来源证据；录音/曲目和程序许可分开核对"}
- 内容与证据：{"kind": "实际音频但未满足证据门槛", "readme_evidence": "https://github.com/Beatscribe/homebrew_vgm/blob/5a82f88b87bb442499685c494b7a96278121b4c7/README.md", "usage_mapping": [], "size_metadata": {"basis": "未查明；本轮已排除该来源，未追加获取文件体积。", "bytes": null}}
- 用途映射：["media"]
- 产品线：["card", "explainer", "showcase"]
- 音频元数据：{"format": "MP3等存在；未进入入库验证", "timeline_validation": "不适用；本轮排除，不进行入库或时间线验证。"}
- 适配：{"grade": "D", "detail": "本轮排除，不适配入库。未下载、转码、剪辑或试听二进制。"}
- 可seek性：不适用（静态素材）
- 维护状态：{"snapshot_checked": "2026-10-02 UTC", "note": "只读元数据与文本审计；不保证听感或Content ID状态", "last_commit": "2026-02-27T05:04:20Z", "commit": "5a82f88b87bb442499685c494b7a96278121b4c7"}
- 风险：["README有CC0声明但无独立LICENSE文件；此外仓库含游戏音色dump等复杂子目录，不能把整库描述直接当所有素材清权。"]

可粘贴署名：

不提供投产署名模板；本轮排除

放置位置：本轮排除，不提供投产署名。

