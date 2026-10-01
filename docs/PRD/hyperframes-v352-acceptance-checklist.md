# v3.5.2 阶段一原生验收与阶段二验收清单

日期：2026-09-28

对应 [v3.5.2 PRD](./hyperframes-v352-asset-kits.md) 第 6 节：阶段一 Windows 原生验收为第 13 项，阶段二验收为第 14–16 项。本清单只把这些条目展开为可执行的检查，不增加新的要求。命令以部署后的 `work.cmd --help` 为准。

## 一、阶段一 Windows 原生验收（第 13 项）

### 0. 前置条件

- [ ] 用户授权把阶段一提交 `025bbd3` 部署到一个**新的隔离候选根**，例如 `D:\AI\hyperframes-review\v352-stage1-<日期>`。不复用 v3.5.1 的对照根，也不部署到正式根 `D:\AI\AI+hyperframes`。
- [ ] WSL 使用固定的 `./release deploy --root <候选根>` 部署，不写一次性部署脚本。
- [ ] 候选根使用自己的配置、Current、AssetStore 与 AssetSource；验收全程不写正式根的源、Current、接受记录或默认配置，不做正式 Finalize，不导出视频。
- [ ] 读取真实 Lucide 包时，`--from` 只读指向正式资产库依赖中的 `lucide-static 1.45.0`（或其副本），`--source` 必须位于候选根内。

### 1. 部署身份与规则

- [ ] `work.cmd doctor` 报告的部署身份与 `025bbd3` 构建的包一致，规则与内容路径指向候选根。
- [ ] 部署根中存在按阶段拆分后的 Draft 核心规则与按需文件；Router 阶段加载表中的链接在部署根内全部可达；Windows 根规则不链接 WSL 开发路径。
- [ ] 发行包中没有 Lucide 或其他第三方图标文件。

### 2. 图标集

| # | 操作 | 预期 |
|---|---|---|
| 2.1 | 图标集未接纳时运行 `work.cmd icons search plug` | 明确报"图标集未安装"，并提示 `icons import`、`component pack`、`component accept` 的步骤 |
| 2.2 | `work.cmd icons import --from <lucide-static 目录> --source <候选根内 AssetSource>` | 只写目标源目录，不自动接纳；生成的图标集含包名、版本 1.45.0、ISC 许可、每个图标的名称 / 别名 / 标签 / SVG hash |
| 2.3 | `work.cmd component pack <路径>`，再 `component validate`，再 `component accept <ref> --sha256 <hash>` | 三步都成功；同一身份同一版本内容不同时拒绝覆盖 |
| 2.4 | `work.cmd component list --kind icon-set` | 列出刚接纳的图标集，默认输出为摘要 |
| 2.5 | `work.cmd icons search wrench`、`search server`、`search plug` | 返回精确引用（图标集版本 + 图标名），别名也能命中 |
| 2.6 | 把图标集安装进测试 Work 后，运行 `work.cmd --work <id> --variant <id> icons use <ref> --output <工程内路径>` | 生成的 SVG 带 `data-icon` 来源标记、使用 `currentColor`、路径未改写，并进入 Variant 快照闭包 |
| 2.7 | 对未安装进该 Work 的引用运行 `icons use` | 明确报"不在闭包内" |

### 3. 新格式 Plan

在候选根中用 `purpose=test` 创建测试 Work 与 Variant（参数见 `work.cmd new --help`）。

| # | 操作 | 预期 |
|---|---|---|
| 3.1 | 新建 Variant 生成的 Plan | 元信息由 CLI 生成，带 Plan 格式版本 `3.5.2` |
| 3.2 | 写入包含事件表（四列，含目标）、`screen` 信息块、`card` 块与一个纯媒体 Scene 的 Plan，运行 `plan refresh` | 成功；纯媒体 Scene 正常解析 |
| 3.3 | `preview register`、`preview open <plan-vNNN>`，改动后再登记一次并运行 `preview diff` | 登记、打开与差异比较都正常 |
| 3.4 | 放入一份 v3.5.1 格式的 Plan；再放入一份删掉格式版本的 Plan | 两者分别明确报"格式不支持"，不尝试转换 |
| 3.5 | `card` 块分别制造语法错误、重复卡片 ID、无法解析的 cue、闭包外的 SVG 引用 | 四种错误分别明确报出 |
| 3.6 | 读取 v3.5.1 时期已登记的历史诊断报告 | 直接读取已保存的报告，不重新解析旧 Plan |

### 4. 节奏诊断（原生 Studio）

测试工程至少包含：纯 GSAP 编写的第 2、3、4 层动作（部分带目标标记）、一个隐藏或离屏动作、一个空 tween、一个带 `data-hf-ambient` 的动作、第 1 层背景漂移、字幕推进、一段镜头推移、一个 Canvas 动画、一段超过 2 秒无事件的区间、一处在 Plan 中声明的例外。

| # | 检查 | 预期 |
|---|---|---|
| 4.1 | 先 `preview open` 再 `preview diagnose <目标>` | 在原生 Studio 中完成采样；默认输出摘要与 `report.json` 路径，`--json` 输出完整结构 |
| 4.2 | 纯 GSAP 的第 2–4 层动作 | 被识别为事件，并按层归类 |
| 4.3 | 隐藏 / 离屏 / 空 tween / `data-hf-ambient` / 背景漂移 / 字幕 | 都不计为事件 |
| 4.4 | 镜头推移 | 只计开始、停止与变向 |
| 4.5 | Canvas 动画 | 标为未验证，不当作静止 |
| 4.6 | 超过 2 秒的无事件区间 | 报 `rhythm_gap`；Plan 中声明的例外标注为已声明例外 |
| 4.7 | 写了目标的声明事件 | 只在同一目标上算命中；同一时刻、同一层的其他动作不被误算 |
| 4.8 | 未写目标的声明事件 | 在对照中标未验证，观察到的事件照常参与空档计算 |
| 4.9 | 回归：v3.5.1 新组参考工程的同类写法 | 不再报 `unverified_custom_motion` 空档 |

### 5. 图标定位

| # | 检查 | 预期 |
|---|---|---|
| 5.1 | 带 `data-icon` 标记但路径被改动的图标 | 报"来源标记与内容不一致" |
| 5.2 | 没有来源标记、尺寸在图标量级的手写小 SVG | 报"手写图标疑点" |
| 5.3 | 自制示意图，以及 `card` 块中 `custom:` 自制示意 | 不被误报 |

### 6. 证据与结论

- [ ] 记录部署身份、候选根路径、每条命令及其退出码、诊断报告路径与必要截图。
- [ ] 结果标为"Windows 原生"，与此前的 WSL 证据分开报告；未执行的项写明未验证及原因。
- [ ] 确认没有导出视频、没有写入正式根，Studio 进程已关闭。
- [ ] 发现工具缺陷时，冻结最小复现交给 WSL，不在 Windows 修改已部署的工具文件。

## 二、阶段二验收（第 14–16 项）

对象：Windows 侧交付的 F01–F08 SVG 槽设计稿。设计要求见 [SVG 槽设计要求](./hyperframes-v352-card-svg-slot-brief.md)。

### 1. 交付物是否齐全（第 14、15 项）

- [ ] 预览页能离线打开。
- [ ] 预览页可切换：
  - [ ] 全部 8 个预设；
  - [ ] 16:9 的 `full` / `left` / `right`，9:16 的 `full` / `top` / `bottom`，以及设计侧对 9:16 窄栏的评估结论；
  - [ ] 浅色与深色 Theme；
  - [ ] 2 / 4 / 6 条内容；
  - [ ] SVG 组合：无、仅 `title`、`title` + 部分 `line`、含 `figure`。
- [ ] 拖动时间轴可以看到逐行出现、SVG 随行出现、强调迁移与退场。
- [ ] 每个预设各有一张槽位规格表，字段齐全：槽名、各区域尺寸与对齐、紧凑布局位置、有 / 无 SVG 时的容量、接受的内容、出现与强调方式。
- [ ] 示例使用 MCP 的真实文字与 Lucide 图标，至少一个预设展示 `figure` 槽的自制示意 SVG。
- [ ] 附相对 `card-family-source@v1` 的变更说明，写明哪些预设的身份受到影响。
- [ ] 设计稿作为新的可编辑源存放；已批准的 `card-family-source@v1` 文件 hash 不变。

### 2. 设计约束是否遵守

- [ ] 有 SVG 时不缩小字号；没有 SVG 时槽位不留空洞，版面按内容收拢。
- [ ] 内容超出容量时标出溢出，不截断、不缩字。
- [ ] 规格表标明 SVG 槽与卡面在第 2 层、文字在第 4 层，两者由同一布局对齐。
- [ ] 外观通过 token 切换浅色与深色，卡片本身不带背景选项；不出现 4:3。
- [ ] 各预设保持原有身份（例如 F06 仍是台账、F07 的输入 → 输出关系仍成立）。

### 3. 用户选定（第 16 项）

- [ ] 用户逐个预设给出"选定"或"暂缓"，选定时注明采用的槽位方案，例如"F06：键列 `line` + 表头 `title`"。
- [ ] 选定结果写回 v3.5.2 PRD，作为阶段三插槽合同与 `card` 块预设专有槽写法的输入。
- [ ] 暂缓的预设不阻塞其余预设进入阶段三。

### 4. 本阶段不要求

- 原生 Studio 验证、CLI 接纳、五层运行时接入、节奏事件上报：这些属于阶段三。
- 预览只需浏览器可用，不需要 HyperFrames 工程形式。
