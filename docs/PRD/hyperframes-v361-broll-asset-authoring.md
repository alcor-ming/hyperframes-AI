# 资产库镜头创作指南（用户 × 生产根 Opus）

状态：2026-09-29 已定稿并同步到受管理的[创作规则](../../.studio/spec/broll-assets.md)与[需求单](../../.studio/templates/BROLL_BRIEF.template.md)。[v3.6.1 开发方案](hyperframes-v361-motion-broll.md)已实现；生产根使用权限以成功部署后的 AGENTS/CLAUDE 为准。本任务不制作或接纳首批库内容。

## 1. 这份指南解决什么

你在生产根（WSL `/mnt/d/AI/AI+hyperframes`）的 Claude Code 会话里，和 Opus 5.5 一起做两类可复用资产：

- **风格外观**：Background + Motion v3 预设（风格叠加，跨账号复用，继承账号 Theme），必要时再加一个 Theme（账号外观，定义某个账号的整体样子）。
- **B-roll 镜头**：3–6 秒的冻结 module，带插槽、读取 Theme 变量，按接口卡的 `usage` 挂进 A/B 编排的 B 区间就能用。

产出的使用方是 Codex / DS Flash。Codex 不读源码，只看接口卡和选型信息，所以**一件资产合格的标准，是 Codex 只看接口卡就能用对**。

## 2. 分工

| 谁 | 做什么 | 不做什么 |
|---|---|---|
| 你 | 写需求单、挑候选、看 Windows Studio 预览、决定接纳 | 不需要读代码 |
| Opus | 提方案、写源码、自检、pack 成候选、写选型信息草稿 | 不写接纳记录，不覆盖已接纳版本，不改任何 Work，不做单片主镜头（那在 explainer 的 Work 流程里） |
| Codex | 用 `component list` / `interface` 选用，在 Plan 填插槽 | 不改库资产 |

## 3. 一件资产的流程

1. **需求单**：你按第 6 节模板写。说不清的地方写"由你提议"。
2. **提案**：Opus 先给 3 个方向，只写文字，不写代码。每个方向说明画面、关键时刻、插槽、适合哪条线、风险。你选一个，或者合并。
3. **候选源**：Opus 在 `asset-library/sources/broll/<风格>/<id>/` 写源码，自带一个样例工程。
4. **自检**：Opus 按第 5 节逐项核对，用 CLI 截图和诊断看画面。没法验证的项列为"未验证"。
5. **你看预览**：在 Windows 官方 Studio 打开样例，用手机尺寸看，并换两个账号 Theme 各看一遍。反馈尽量说具体秒数和具体感受，比如"1.2 秒的落章太慢"比"不够炸"更容易改。
6. **打包**：`component pack` 生成候选；Opus 起草 `selection.json` 的 purpose、aliases、tags、examples、limitations。
7. **接纳**：你确认后执行 accept。之后要改只能发新版本（`v2`），不覆盖旧版本。

每次可以批量做 3–5 件同风格的资产，在第 2、5 步集中挑选，比一件件来回效率高。

## 4. 先做风格外观，再做镜头

同一风格的镜头共用一套风格外观，Codex 在同一片里混用时画风才统一。

1. **风格叠加优先**：先做 Background 和 Motion v3 预设并接纳。使用时 appearance 文件省略 theme，继承账号 Theme，所以一套叠加能用在所有矩阵号上。
2. **账号外观按需**：只有需要为某个账号定义整体样子时才做 Theme。注意：appearance 文件里写了 theme 就会覆盖账号 Theme，不再跟随账号。
3. 镜头的颜色和字体只读 `--appearance-*` 变量，动作优先引用 Motion 预设；只有整段表演才写在镜头自己的 module 里。
4. 同一镜头至少在两个不同 Theme 的账号下都要可读，这是矩阵号复用的前提。风格强依赖特定配色的（比如赛博 HUD 的霓虹色），要写进 limitations。

## 5. 每件资产的自检清单

**合同**
- 实现接口卡 `usage` 规定的挂载入口：`mount({stage, text?, appearance, slots, params, startCue, endCue, cues})`，返回 `renderAt(t)` / `moments()` / `dispose()`。由宿主按秒调用 `renderAt`，镜头不自启时钟；不在 `onUpdate` 里写状态，不用随机数；顺播、直接 seek、回拖三者结果一致。
- 关键时刻在挂载时以带目标元素的事件注册到 `__hfRhythmSources`，`dispose` 时注销。manifest 里的 `key_moments` 只是说明，不参与节奏计数。
- 依赖和字体离线闭包；不用 CDN，不引用闭包外路径。
- 颜色和字体只读 `--appearance-*`，不写死色值。
- 声明完整的 `broll` 块：role、takeover、duration、timing（`stretch` 或 `hold-end`）、slots、params、carries_info、key_moments、sfx_cues、caption_safe_zone、usage、examples；画幅写在 `compatibility.ratios`。
- 插槽规则：
  - text 和 number 声明所在层（stage 或 text）以及最大字数，容量用冻结字体实测。
  - icon 只接受精确图标引用。
  - media 只接受 Work 闭包内已登记的资产。
  - 外部 URL 和闭包外路径一律拒绝。

**画面**
- 用最长的文字测试文字插槽，每个声明的画幅都不溢出；标题数字在手机尺寸下看得清。
- 整帧镜头挂在第 2 层，避开字幕安全区。
- 承载信息的镜头（`carries_info:true`）：独立标题、解释和关键数字放在 text 根（第 4 层），在对应口播的 cue 出现，并遵守阅读保护；第 2 层只放附着在图形上的短标注。
- 纯注意力镜头（`carries_info:false`）：不设第 4 层文字插槽。
- 在 `stretch` 与 `hold-end` 两种设定下，分别用最短、默认、最长时长各看一遍；`moments()` 返回的秒数要和画面对得上。
- 相邻关键时刻间隔 ≤2 秒，末帧有收束，方便 Codex 接回 A-roll。
- 示意性数据或界面标 `data-hf-schematic`；不伪造真实产品界面或数据。

**复用**
- 接口卡写清楚：适合什么语义、不适合什么（limitations），并给一个填好插槽的完整挂载例子（usage 加 examples）。检验标准：Codex 只看接口卡就能写出正确的挂载代码。
- 标上适合的产品线：card 只推荐简洁、信息为主的镜头和预设。

## 6. 需求单模板

```markdown
# 镜头需求单

- 类型：风格叠加 / 账号外观 / 镜头（hook | concept | transition）
- 风格：赛博 HUD / 贴纸拼贴 / 综艺花字 / 其他：
- 服务产品线：card / explainer / 数学（可多选）
- 用途一句话：观众在这几秒应该感到/看懂什么
- 画幅：9:16 / 16:9
- 时长：约 _ 秒
- 插槽：标题（≤_字）/ 数字 / 图标 / 图片 / 无
- 时长变化：拉伸（stretch）/ 末态停留（hold-end）/ 由你提议
- 是否承载信息：是 / 否（纯注意力）
- 参考：链接、截图、awesome 仓库条目、"像 xx 那样"
- 声音：建议音效打点 / 由你提议
- 不要：
- 批量：本次同风格做 _ 件
```

## 7. 常用开场话术

- 新风格叠加：`按 broll-assets 指南，用这份需求单做一套<风格>风格叠加（Background + Motion v3，继承账号 Theme）。先给 3 个方向，只写文字，别写代码。`
- 批量镜头：`基于已接纳的 <motion@vN>/<background@vN>，做 4 个 hook 镜头候选，至少用两个账号 Theme 自检，每个都附未验证项。`
- 修改：`<id> 在 1.2 秒的落章太慢，数字插槽 8 位时溢出。改完 pack 成新候选，不要覆盖旧版本。`
- 发新版：`<id@v1> 已接纳。按这些反馈做 v2，保持插槽接口兼容，接口有变化就在 limitations 里说明。`
- 从 explainer 主镜头提炼：`<Work> 的 <Scene> 主镜头已接受。按提炼模板把它参数化成通用 concept 镜头，本片专属内容去掉。`

## 8. 首批建议（D4）

每种风格先做 1 套风格叠加加 4–5 个镜头，共约 15 件：

| 风格 | 风格叠加的 Motion 手感 | 镜头建议 | 适合 card |
|---|---|---|---|
| 赛博 HUD | glitch-in、wipe、glow | hook 系统启动标题；hook 数字锁定（数字插槽）；concept 数据流扫描；concept 目标锁定框（图标插槽）；transition 扫描线切换 | 转场与 glow 强调 |
| 贴纸拼贴 | stamp、wobble、`hold_fps:12`（仅原地拍章/强调；位移、旋转、翻面逐帧求值，2026-10-02 数学镜头返工补充） | hook 贴纸标题拍入；concept 剪贴对比（双文字插槽）；concept 手绘圈重点；transition 纸片翻页 | 最适合，温和、信息友好 |
| 综艺花字 | pop、shake、pulse、spring | hook 花字爆出；concept 大数字冲击；transition 色块冲屏；强调 惊叹贴 | 仅强调与转场，少用 hook |

建议先从贴纸拼贴做起：它三条线都能用，最能检验"一套风格叠加、多账号换色"这件事。
