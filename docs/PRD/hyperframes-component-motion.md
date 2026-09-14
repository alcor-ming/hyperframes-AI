# HyperFrames Scene / Module / Media PRD

状态：v3.2 语义视觉对象与根配置调整；保留 M1 已有 module/media 子集，不代表全部资产类型已实现或原生已部署

上位 PRD：[PRD_MASTER.md](./PRD_MASTER.md)

历史依据：[component-driven-motion-vnext.md](./_ledger/component-driven-motion-vnext.md)，保留原记录，不把历史整组规则施加给新模块。

日期：2026-09-11

## 1. 目标与边界

Windows 用 Work-local Scene 组合模块和媒体，控制当前内容、画幅、对象关系、阅读顺序与衔接；完整冻结 Component 不再是唯一复用单位。旧组件只读兼容，不批量拆解或要求迁移全部 Work。

Windows 在 Work-local 或已登记 AssetSource 开发图形对象、GSAP、Three.js、shader、SVG、模型与后续 Blender 内容。WSL 只维护 Harness、宿主、合同、打包器、依赖装配及安装工具；效果复杂或可复用不构成移交 WSL 的理由。

保留 M1 已有 module/media 合同与打包能力，接续本地 M2–M3。R1 先交付真正根候选，再针对 Windows 所选 Work 修 R2/R3 实际工具缺口；视觉内容仍在 Windows，不重跑全套旧阶段。不新增万能 Scene DSL、在线 Registry、向量数据库、播放器或审批层。

## 2. 对象与运行职责

| 对象 | 内容与边界 |
|---|---|
| Scene | 叙事单元，拥有实际内容、对象、布局、Beat、媒体和衔接；简单 Scene 可仍是一份 HTML |
| Module | 实际代码入口、用法、输入限制、依赖及生命周期；不要求 `component.html`、完整全场状态或独立全局 timeline |
| Media | 文件、来源、格式和能力；可为原件或已接受派生产物，不要求代码 Fixture 或主题合同 |
| Template（后续） | 只有实际固定结构才声明画幅、时长、内容限制，不让所有模块冒用模板合同 |
| Recipe（后续） | 源工程、参数、受控工具与输出；浏览器不执行构建命令，Blender 构建器不是 M1 前提 |
| Legacy Component | 按原 Component 合同使用精确冻结版本；保留 Slot、ratio 与状态限制，不回写旧包 |

Scene 与 composition 不必一对一。相邻 Scene 需要连续对象、同一相机和空间时可以共享 composition；稳定 Scene ID 保留，不靠上一 Scene 已播放才能得到当前状态。

## 3. 设计与时间

- Scene 只安排所需 Beat，不强制 Opening / Build / Hero / End / Handoff、标题区、卡片区或结果区。
- 图形绘制和运动按真实复用分开；GSAP 模块把 tween 写入宿主有限 timeline，不同时注册全局播放。child timeline 必须明确所有权，不建 easing / stagger / label DSL。
- 准备字体、媒体几何和依赖后同步构建固定 timeline；异步准备须有 ready 屏障。直接 seek、倒跳、repeat-seek 和冷启动得到同样状态，不依赖播放回调创建正文。
- root、选择器、SVG defs 与资源按实例隔离；不要让多个动画同时拥有同一属性。Three 资源、监听和 renderer 按实际所有权释放。
- 通用模块不强制双画幅，Scene 可计算布局和重新分组，但必须验真实文字、媒体、时间与阅读。只拉伸不能证明适配；有限画幅模板保留明确限制。
- 背景和前景可独立时分开，共享相机、遮挡、光照的空间舞台保持内聚，不要求所有模块透明根层。
- 图标 / 图片 / 截图 / 模型可直接承担主体、证据、纹理或辅助对象；只有旧组件内部注入仍遵守其 Visual Payload Surface。
- 正式音频与 `section_map.json` 是实测时间权威，工程 timeline 负责实际显示；Plan 不复制精确时间表，不默认整体 timeScale 代替局部阅读 hold。

## 4. M1 最小资产合同

沿用 `component` CLI，新增 `component pack <source-directory>`，从源目录的 `asset.json` 生成冻结候选。该 JSON 使用 `schema_version: 1`、`id`、`version`、`kind`、`entry`；M1 的 kind 只支持 `module` / `media`，module 入口为 JS / MJS，media 首批为 PNG / JPEG / WebP / SVG。

可选 `dependencies` 显式列出依赖文件路径；`usage`、`example`、`license` 指向实际文件。模块用法与 preview 宿主分开，不把预览 HTML 当成唯一模块接口。只验证本轮实际闭合的子集，不宣称具备任意 npm 打包或所有 shader / 模型依赖分析能力；缺依赖明确报告。

最小源声明示例：

```json
{"schema_version":1,"id":"focus-motion","version":1,"kind":"module","entry":"focus.js","usage":"USAGE.md"}
```

module/media 使用 Binding schema 3；沿用 `component_ref` 命名，不填旧组件 Slots：

```json
{"schema_version":3,"component_ref":"focus-motion@v1","scene":"S01","usage":{"role":"auxiliary","required":true}}
```

`usage.role` 为 `subject|evidence|texture|auxiliary`，`required` 必须是布尔值；可选 `fit` 为 `contain|cover|fill`，`focal_point` 是两个 0 到 1 的数。布局、动作参数与时间留 Scene，不塞进 usage。Work 安装仍需 Plan 引用及 `component install --binding-file`；独立样例用 `--project <已登记AssetSource内的样例目录>` 安装 / verify，不注册伪 Work，不增加新 preview API。

文件复制到兼容路径 `vendor/components/<id>/vN`，Lock schema 2 沿用 `components[]` 并用 `asset_kind` 标记类型，不另建平行 vendor 或 lock。绑定与工程实际入口均须一致，不能仅安装成功就宣称 Scene 已使用该模块。

后续按 kind 扩展共同身份、版本、实际入口、依赖、路径和摘要；模块声明用法及运行时限制，媒体按实际格式与能力检查。Template / Recipe 未实现时明确拒绝，不能伪装 Component。

运行时兼容要求与曾测试的准确环境分开。模块只承诺实际验证的能力，普通媒体不因 Harness 文档更新失效；固定旧 Work 不回溯要求最新外部运行时通过。实时效果、GLB 和烘焙媒体是不同表示，不隐式互换，也不要求每个效果同时提供三份。

每个小 helper / icon 不单独发包，按实际维护边界成组。普通素材不强制库级代码审批，Work-local 新代码只接受当前作品 QA。

## 5. Windows 源到精确版本

1. 优先登记已有可编辑 AssetSource；在固定 Windows 工具上开发并预览，未发布工具能力只用 Review 源副本试验。
2. 有真实复用价值后，从选择的源目录打包实际入口、依赖、必要用法和证据；不含 `.git`、缓存、临时输出、私人 Work、无关大文件或个人配置。
3. 冻结前后核对所选源未变化，hash 清单属于冻结产物，不将其回写成编辑中源的唯一状态。候选身份与字节固定，修改审阅副本后必须产生新候选。
4. 官方 Studio 只打开候选的独立真实复制，不以 hardlink / symlink 暴露冻结包。精确接纳关联身份、版本、摘要和实际环境，不原地改包状态。
5. Review 模拟接纳 / 安装仅写 Review 库；兼容稳定版时由 Windows 生产根按现有授权正式接纳，不能把候选测试记录自动变为生产接纳。
6. Work 复制精确资产及实际依赖到 vendor，生成既有 Binding / `COMPONENT_LOCK.json`；不读活跃 AssetSource 或 latest，不热更新其他 Work。

现有 `source-add/import/accept/list/validate/install/verify` 扩展识别 module/media，不新建 `asset` CLI。Work Lock schema 2 允许混装，旧 schema 1 兼容读取；不建立第二套台账或权威 lock。具体参数以当前安装包帮助为准；部署与真实通过状态见[本轮任务台账](./_ledger/component-authoring-m0-m1.md)。

## 6. 目录、发现与安全

AssetSource 可编辑，AssetStore candidate/package、Work vendor 和 Accepted Snapshot 不可原地编辑。AssetStore 与安装目录、WorkStore 分离；Review 的 store 和试验源副本不放生产 packages 或 WorkStore 内。

发现先按类型、实际媒体 / 画幅 / 运行时硬条件过滤，再给有限相关结果、用途、边界和样例。外部元数据驱动发现，不修改全局白名单；不每次检索全库重算大媒体 hash，冻结、安装和验证检查真实依赖。

路径规范化并检查相等 / 嵌套、Windows 大小写和链接实际目标；不能用 junction 或环境变量绕过写入隔离。普通创作只消费本地闭合资产，不运行时联网拉 CDN、浮动安装依赖或借 WSL 活跃 node_modules。hash 表示字节一致，不证明未知代码安全。

统一根部署允许 WorkRoot 下专用 `asset-library/store` 和 `asset-library/sources`；它们独立于 `works/`、既有 `assets/`、`.runtime/`、`.studio/` 和 `runtime/`。不再为存储位置强迫用户使用另一操作根。

单次根命令解析 WorkRoot、AssetStore、AssetSource 和缓存，长进程固定本次输入，不创建或依赖 Harness session。根配置优先于继承全局变量；候选根具有独立配置和 source-copy，不写生产源、包或接受记录。同身份版本不同内容拒绝覆盖，未接纳或依赖不完整的包不得冒充正式可用。

语义视觉对象是主要复用单位：解释职责和必须联动的内部关系决定边界，不以 DOM 数、文件数、渲染器或大小决定。可复用一整个空间舞台；既有 helper 保留，只为真实独立变化抽取，不强制图形/动作/布局工厂或新状态机。Scene 负责本期叙事、A/B 职责与编排，内容创作留 Windows。

## 7. Plan 与兼容

Plan 只记录当前 Scene 的视觉目标、Script / Research / 素材引用、对象关系、模块 / 媒体选择与未验证项，不复制全文内容。组件没有匹配时用 `custom:<slug>` 表示 Windows Work-local 实现，不默认产生 WSL 效果请求。

整片 Plan 后只选一个真实 Scene 动态参考，一次方向批准后直接扩成完整 planned-placeholder Draft；素材齐备后输出最终 Draft，沿用完整接受与 Final。颜色字体可共享，局部布局不自动全片继承；计划占位不阻塞全片预览，方向和占位 Draft 不具 Finalize 权限。旧样段和接受记录保持原义。

旧 `.studio/components` 与历史 Work 按原合同只读兼容；旧 package hash、vendor、Binding、Lock、Accepted Draft / Final 原样保留。新合同在既有 Lock 中版本化，未知 schema 明确报错，不能覆盖旧字节或自动降级新数据。

原三套 Profile、二十个双画幅 Component Family 和一个双画幅 Background 的 42 项 Gallery 只属历史 backlog。当前按实际需求提取能力，不把未完成家族、另一画幅或主题解耦作为准入门，也不声称原批次已完成。

## 8. 验证与交付

本轮接续当前 M2–M3，不重跑 M0–M1。R1/R2/R3 的 Windows 原生 CLI、Studio、混合短片及带声验证必须分别记录；Linux/mock、打包和路径检查不冒充原生完成。根配置防止继承变量将 Review 重定向生产，既有闭合资产与旧作品保留。

新增非平凡工具逻辑保留最小可运行回归：新旧合同、确定性打包、路径 / 身份冲突与候选隔离。按实际用到的能力验证直接 seek、多实例、ready、资源释放、依赖闭合和离线；不强制 M1 提前完成 M3 Three 空间视觉矩阵。

M2-M3 再由 Windows 用真实内容完成 GSAP、素材、模块复用和 Three 空间验收。技术夹具不冒充真实成片、用户资产批准或返工下降；软件渲染、交互 WebGL、抓帧 WebGL、硬件编码分别报告。

媒体下载、ImageGen、平台草稿、发布和 Git 权限不变。真实内容、私有素材与资产权威源不进入公开 Harness；兼容资产发布不等于程序发布，更不等于公开上传授权。
