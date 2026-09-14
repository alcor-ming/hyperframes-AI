# HyperFrames AI vNext PRD Master

状态：v3.2 根目录、语义视觉对象与分准备度 Draft 调整；不是软件发行或实机通过声明

风险：T3 Parent PRD

日期：2026-09-11

## 当前路径

Windows 在 Work-local Scene 安排本期叙事，优先复用带意义且内部联动完整的视觉对象与媒体；既有 helper 和完整 Scene 均可保留，不强制拆解、合并或迁库。内容复杂度不改变 Windows 归属。

Script / Research 就绪后先整片 Plan，再一个真实 Scene 动态参考，一次方向批准后扩成完整 planned-placeholder Draft，素材齐备后生成最终 Draft。局部布局不自动推广全片，不逐 Scene 审批，不增加占位 Draft 强制接受；单 Scene 参考不授予 full Draft 的 Finalize 权限。

官方 HyperFrames Studio 继续负责预览和渲染；Work 管理身份、版本、反馈和接受。Plan、正式音频 / section_map、Draft、Final 的职责与已有内容权限不变，不新增播放器、内容数据库或审批层。本文件是产品索引，不增加日常必读材料。

## 本轮范围

接续本地 M2–M3 源码和画面，不回退公开 HEAD，不重跑 M0–M1。先与 Windows 对齐所选 Work、已有对象和真实工具缺口，在现有任务记录保存保留/轻量封装/延后/局部修复分类，不建设资产数据库。

| 阶段 | 目标与边界 |
|---|---|
| R0 | 核对实际 Work/成果，Windows 修订当前可编辑 Plan，保留原 ID、录音、对齐和接受快照 |
| R1 | 最小真正根候选：runtime/.studio/根配置与直接 work.cmd，无 session；原生检查、管理文件更新及恢复 |
| R2 | Windows 复用一个 Scene 做动态参考；WSL 仅修 cue 解析、剪辑映射、裁取或实际宿主缺口 |
| R3 | 方向批准后 Windows 扩成完整占位 Draft；WSL 仅修 planned placeholders 和范围权限等真实工具问题 |
| R4 | Windows 补素材/最终音频，生成最终 Draft，沿用整片接受与 Final |
| R5 | 原生候选通过后按授权更新生产根、检查数据兼容及当前作品闭环 |

M1 已有 module/media 合同保留，Template/Recipe/Blender 或全库迁移不是本轮前置。音乐分析可选、离线缓存，先用既有 timestamps/section_map；缺音乐或 Blender 不阻塞正常制作。

## 职责

| 对象 | 拥有 | 环境 |
|---|---|---|
| Scene | 当前内容、布局、对象关系、所需 Beat、媒体和相邻衔接 | Windows Work-local |
| Module | 图形对象、GSAP 动作、Three.js / shader 等可复用视觉实现 | Windows Work-local 或已登记 AssetSource |
| Media | 原件、派生物、格式能力及来源 | Windows 资产源或 Work 媒体目录 |
| Template / Recipe | 已声明的布局限制或受控构建输入 / 输出，按需实现 | Windows 资产源；构建协议由工具提供 |
| Harness / 宿主 | 加载、ready / seek、依赖装配、CLI、根配置、安装器 | WSL 唯一工具仓 |
| Plan / Binding / Lock | 视觉决策、工程接线、准确资产与依赖引用 | 现有 Work 生命周期 |

判定依据是职责，不是文件扩展名、复杂度或是否复用。Windows 可开发效果代码，不修改已安装 Harness。WSL 只在明确工具请求的冻结最小私有副本中复现，不直接改生产 Work 或资产源。

## 设计约束

- Scene 只组织需要的节拍，不强制 Opening / Build / Hero / End / Handoff 五阶段或标题、卡片、结果区。
- 通用模块不绑定双画幅；Scene 可重排或计算布局，必须验证真实文字、媒体与阅读时间，不能只拉伸后宣称适配。有限画幅模板保留自身限制。
- 图标、图片、截图和模型可直接成为主体、证据、纹理或辅助对象，不统一限制到固定 Surface；旧组件仍遵守原合同。
- 能独立的背景 / 前景可分开，共享相机、遮挡、光照的空间舞台保持内聚，不强制透明根层。
- 主题继续使用当前选定 Profile；全片颜色、字体与局部布局 / 动作分开。原完整主题解耦目标不成为 M1 或日常 Work 的前置门。
- GSAP 模块写入宿主有限 timeline，不拥有独立播放权；任何时刻可从显式参数与时间重建。模块用法与 preview 宿主不是同一接口。
- 媒体、依赖与字体按实际使用闭合，不把未授权内容放进公开 Harness，不承诺尚未测试的运行时或画幅。

## 资产与冻结

优先登记已有 Windows AssetSource，不创建第二份可写权威源。AssetSource 可编辑；候选、已接纳 AssetStore 包、Work vendor 和 Accepted Snapshot 不可原地改。需要变化时在源中派生并冻结新身份 / 版本。

视觉资产在 Windows 独立打包、验证与精确接纳，不随兼容内容变动重发 Harness；真正改变宿主、合同、依赖装配或工具能力才走 WSL candidate。包只带所选入口、实际依赖、必要用法和证据，不包含私人 Work、凭据或无关全库。

Work 沿用 vendor / Binding / `COMPONENT_LOCK.json`，schema 2 扩展通用资产，旧 schema 1 保留兼容读取；不建平行锁或第二套接纳台账。同身份、同版本不同内容必须拒绝，外部更新不热改已绑定 Work，库离线时闭合副本仍可渲染。Work-local 新代码只做当前作品 QA，不强制先公共化。

## 根目录部署

入口根 `.studio/.runtime/local.json` 是配置真源；一次命令解析并固定本次输入，长进程不随配置变化漂移。不创建 Root Session，也不依赖旧 session 文件。

候选同时隔离 WorkStore、AssetStore、必要试验源副本及缓存；不写生产源、包、接纳记录或全局默认配置，不覆盖稳定 workspace / current / previous。模拟资产接纳只留 Review；候选不允许正式 Finalize、归档完成或平台草稿。

工具根直接部署 runtime/.studio，根配置归 .studio/.runtime；单次命令和长进程固定输入，不创建或要求 Harness session。更新前停止相关进程，复用最小互斥，禁止热换；严格包校验与部署管理文件校验分离，不覆盖用户修改、不删 Work/资产/用户 Skill。候选独立根配置与内容副本，回滚分别检查程序、资产及 Work 兼容；不自动 commit/tag/push 或公开发布。

## 兼容与历史

- 旧公共组件及 Work 的 hash、vendor、Binding、Lock、Accepted Draft、Final 原样保留。
- `migration-ready`、目录出现或技术夹具通过不等于生产接纳；精确资产按当前真实输入和目标环境独立验收。
- 旧 Profile / Background / Component 双画幅整组设计及 42 项 Gallery 只作为历史 backlog，按真实需求提取能力，不再是新资产白名单或本轮交付清单。
- 历史决策保留在[原决策台账](./_ledger/component-driven-motion-vnext.md)；不回写过去记录，不将已替换的五阶段、双画幅或透明根层规则继续施加给新模块。

## PRD 索引

- [Scene 与独立资产合同](./hyperframes-component-motion.md)：类型边界、Windows 内容开发、最小 module/media、精确冻结与旧合同兼容。
- [逐 Scene 复用、缺口 Plan 与官方 Studio](./hyperframes-visual-plan-motion-reuse.md)：保留内容质量、轻量 Plan、局部反馈与真实验收。
- [Windows 工作台与 WSL 工具交接](./hyperframes-windows-workbench-wsl-handoff.md)：固定上下文、Review 隔离及两条交付回路。
- [rnskill 动效分层研究](./_research/rnskill-motion-layering.md)：仅按当前问题读取，不作为强制制作公式。

本 PRD 不扩大生产 Work、资产源、Open Design、Git 或外部发布授权；资产、Plan 与 Draft 分开记录，一句明确回复可以覆盖多个准确对象。
