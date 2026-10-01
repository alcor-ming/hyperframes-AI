# 冷静的光 · Three.js 第一批源码交接

只包含 graph-grow 与 token-stream。没有完整视频、生产 Work、接纳记录、安装切换或发布。

本目录是 GitHub 交接包，不是生产 AssetStore。仓库规则规定 Harness 发行不携带库内容，因此没有修改发行配置，也没有把源码写进任何现有生产库。使用时把两个模块目录分别复制到已登记的 `asset-library/sources/broll/calm-light/<id>/`，独立测试工具留在本交接目录。每个模块的运行时闭包自包含，可分别 pack；fixture 和 qa 不进运行时闭包。

## 本地快速检查

需要 Node、Python 3、已安装的 Playwright（或指定 PLAYWRIGHT_PACKAGE）及其 Chromium。不要在生产部署根直接编辑受管理工具。

在独立的仓库检出目录执行：

```sh
node --test handoff/calm-light/state.test.mjs
python handoff/calm-light/setup-fixtures.py --font /absolute/path/to/licensed-chinese-font.otf --font-license /absolute/path/to/font-license.txt
python -m http.server 8090 --directory handoff/calm-light
```

然后打开：
- http://localhost:8090/graph-grow/fixture/index.html
- http://localhost:8090/token-stream/fixture/index.html

字体必须覆盖实际标签。fixture 示例默认为英文，USAGE 中文示例需要中文字形；不要用缺字字体替代中文验收。setup 脚本只复制仓库冻结 runtime 与指定字体到 gitignored generated 目录，创建隔离 fixture 输入，不读取生产配置、不 pack、不 accept。fixture Theme 的 hash 是 fixture 内部引用标记，不是可接受资产 hash。

如未安装 Playwright，可在本交接目录进行独立测试依赖安装：

```sh
npm install --no-save --no-package-lock playwright@1.62.1
npx playwright install chromium
node graph-grow/fixture/seek.test.mjs
node token-stream/fixture/seek.test.mjs
```

也可以设置 `PLAYWRIGHT_PACKAGE` 为现有 Playwright 包目录、`CHROME_PATH` 为现有浏览器可执行路径，避免新装。脚本从任意 cwd 可运行；执行前先完成 setup-fixtures。没有 Playwright 时仍可用手动 fixture。

自动 seek 测试覆盖 96 个 graph / 72 个 token 配置组合（2 Theme × 2 ratios × 全部 topology/mode × normal/reduced × min/default/max）。比较同一时刻的顺播、直跳、回拖、重复跳转截图字节；另检查标签字幕区和 dispose。截图不含工具栏。默认参数、normal、默认时长下，两画幅 × 两 Theme × 全部关键时刻的 PNG 与结果 JSON 写入模块 qa（gitignored，供本机验收），不生成视频。

临时包闭包验证（使用安装好的 Harness 控制运行时 acorn；如需要，将 HYPERFRAMES_DEPENDENCY_MODULE_ROOT 指向含 node_modules 的 runtime 根）：

```sh
python handoff/calm-light/validate-packages.py
```

该命令只在临时目录 freeze/validate 并报告 hash，不 accept、不修改任何 AssetStore。不要拿历史文档 hash 代替实际 pack 的 hash。

## 本机回收

1. 将模块目录复制到已有登记 AssetSource 的目标路径；保留 Three MIT 许可
2. 阅读每个 USAGE.md；确认 Theme 存在必需 tokens 和冻结字体
3. 在官方 Windows Studio 使用两个真实账号 Theme、两画幅、最长标签、最短/默认/最长时长检查；fixture 不是官方 Studio 接纳
4. 使用当前部署根的 `work.cmd component pack <source-directory>` 生成候选；使用生成结果的准确 ref/hash 进行本地审核与用户接纳
5. 经既有 install / verify 链路进入授权工程；不要直接复制源码覆盖 accepted/vendor

## QA 状态（2026-10-01）

- 已执行：44 项 Node 状态/合同测试；源码语法检查；真实 asset_contract.freeze_source / validate_asset 的两个完整闭包；6 项现有 B-roll 合同回归；聚焦代码审查
- 已修正：响应式标签初始字号、80-token 盒内深度、partial fill 错误满容量提示、稠密图连线时间、部分节奏目标
- 已尝试但受阻：Playwright 系统 Chromium 启动，失败于 `socket() failed: Operation not permitted`
- 未完成：截图、WebGL 像素 seek、视觉对比、真实节奏 probe、标签碰撞检查、Windows 官方 Studio。没有生成或伪造 qa PNG
- 结论：可回收的源码候选，不能声称视觉验收通过或已接纳

## 设计案与现有合同差异

- max_chars=6 保持严格；hub 使用「调度」，不使用 7 字符 harness
- graph 明确提供 n1–n8，允许最多八个外围 + hub；若要求总数≤8，留一个外围槽为空
- path 的“2–5 段”解释为 2–5 条边；mount 支持 `n1>hub>n4` 或 `n1/hub/n4`。现有 pack 和 runtime 的表达式检查拒绝 `>`，因此 manifest 默认和经过通用验证器的调用使用斜线。入口先检查语法再转换，不改宿主验证器
- 因 runtime 要求所有声明槽，入口只补可选空槽；不存在的节点仍不创建图形，必填槽不补造内容
- 额外可见状态里程碑用于长时长节奏，声明间隔≤2秒已有数值检查，真实有效事件需本地 probe 复核
- 两包各自 vendor 同一 r160 ESM 字节，避免跨包 module 依赖合同缺口；共享 scene helper 当前也各包自包含，不依赖相邻源码
