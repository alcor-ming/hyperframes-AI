# Windows 创作工作台与 WSL 交接

版本：v3.2；日期：2026-09-11；目标合同，不代表 Windows 原生通过。

本文件接续本地 M2–M3 已有代码和画面，仅修当前工具缺口，不回退公开 HEAD，不重跑 M0–M1。Windows 先核对所选 Work、已有成果和真实问题；WSL 首先交付 R1 最小根候选，R2/R3 只处理实际暴露的工具问题。[视觉 Plan PRD](./hyperframes-visual-plan-motion-reuse.md) 维护创作流程，不新增播放器、状态机或 Shotbook。

## 职责

- Windows：正式 Work 生命周期、文案、Research、Scene、Plan 与视觉内容；在 Work-local 或已登记 AssetSource 开发 GSAP、Three.js、shader、SVG、模型、素材、样例与后续 Blender 内容，并完成资产打包、接纳和作品验收。
- WSL：唯一可写 Harness 工具仓，开发宿主接线、CLI、合同、依赖装配、打包器与安装器。只在工具请求的冻结最小私有副本中调试，不双写生产 Work 或资产源。
- 职责不按扩展名、复杂程度或可复用性分类。Windows 不改安装包、已接纳包、冻结 vendor 或 Accepted Snapshot；新效果可留 Work-local，真实复用时再从可编辑源冻结新版本。
- 不建设第二份可写 Harness；Windows 资产源是不同对象，不是工具分叉。不新增常驻调度服务、在线 Registry、新剪辑器或多轮审批链。

## 根目录与配置

Windows 直接打开实际制作根，当前为 `D:\AI\AI+hyperframes`。根内实际部署 `work.cmd`、`work.ps1`、`release.ps1`、`AGENTS.md`、`.agents/skills/`、`.studio/`、`runtime/` 和 `.release.json`；本地配置与可变工具状态归 `.studio/.runtime/`，不纳入程序 hash。不得以 `.harness/releases/current` 或自动 session 伪装直接入口。

入口按自身路径选根，绝对路径调用不受 cwd、旧 HOME、session 或 AssetRoot 影响。一次命令解析已有配置字段一次，明确 Work/Variant 优先；长进程固定本次工具、资产、内容和 Provider 输入，不宣称整次聊天跨命令固定。doctor 报实际身份、规则来源、配置、内容路径和 Review 范围，不要求 Harness session。

WorkStore、AssetStore 与已有源位置保持不动；`works/`、内容 `.runtime/`、`requests/` 和用户其他文件不迁移。AssetSource 是 Windows 可编辑内容源，不是可写 Harness 镜像。优先登记已有目录，Work-local 视觉不必先入库；只使用实际 module/media 合同，不虚称全类型或 Blender 已实现。

待安装 ZIP/staging 严格检查完整清单、hash、依赖和路径；部署根只验证 manifest 拥有的管理文件，合法 Work、本地配置和用户 Skill 不构成包损坏。更新只覆盖管理文件，旧清单拥有且新版删除的文件才清理；已被用户修改的管理文件保留并报告，不递归镜像整个根或 .agents。

更新先 staging 校验，备份旧管理文件和必要迁移信息，再更新并最后写完成标记；中断可检测恢复，损坏混合版本拒绝启动。通过现有进程管理和最小互斥停止相关 Preview/render/build，再更新，禁止热换，不建设 daemon。程序回滚不降级 Work 数据或重绑资产，无法兼容时保留新数据和可用工具。

## 原生执行与候选

Windows 原生 Work CLI 与生产渲染依赖继续由安装管理：固定 CPython、Node、HF、GSAP、Three、渲染浏览器、FFmpeg/ffprobe 与字体，普通运行不使用浮动 npx/npm install。Work 入口自动解析锁定的官方 `hyperframes preview`，返回实际 Studio 工程 URL；端口和工程从启动结果校验，不硬编码或按目录猜测。

整片 Plan 后只取一个真实 Scene 动态参考，使用已有画面、实际字体/媒体和本机官方 Studio；音频已有则裁取，无最终音频可 provisional。方向批准后生成完整占位 Draft，计划内缺素材不阻塞全片预览；最终 Draft/Final 再严格要求必需媒体和效果齐备。缺 Studio 能力明确报告，不静默换播放器。

已有 ASR/下载 Provider 沿用其受控入口；WSL Provider 不把整个创作流程变成 WSL 开发，也不成为所有用户的隐含依赖。缺 ASR 不阻塞已有音频的预览。权限受限时指出实际缺口，不关闭沙箱或授权任意 shell。

候选从当前受控工作树冻结相关 dirty 源码和逐项明确的新文件，排除私有 Work/资产、凭据和缓存，记录 commit、dirty、源码/依赖 hash；不要求 commit/tag/push、不覆盖已有候选或生产程序。旧包和历史 session 保留回退资料，新根不依赖它们。

候选必须使用独立的直接部署根和根配置，明确隔离 WorkStore、AssetStore 与必要 source-copy。检查规范化路径、嵌套和链接实际目标，以真实复制而非 hardlink/symlink 隔离内容。Review 不改生产全局配置或接受记录；准确命令只在实现后写入帮助，路径合法不算原生渲染通过。

正式 `release build` 保留干净工作树、tag 与 upstream 约束；Git 操作、安装切换和公开发布仍各自遵守明确授权。候选验收不等于正式发行或组件批准。

## 请求往返

请求使用稳定 request ID/revision、Work/Variant、Scene、预演/源码快照、实际文字或唯一 Binding、画幅、阅读窗口、媒体、相邻交接、目标与保留项、当前缺口和验收输入。已能从 Work 获取的内容不重复询问。

Windows 拥有需求、反馈、验收；WSL 读取冻结 revision，拥有交付清单和技术结果，不共同编辑同一状态文件。更新请求保留旧 revision；缺上下文只返回该请求的聚焦问题。不增加默认需求批准门，继续制作不受影响 Scene。

Windows 从当前成果修订整片 Plan，记录 A/B 职责、语义对象、稳定素材占位与 cue 意图；仅一个真实 Scene 动态参考，一次方向批准后直接扩成完整 planned-placeholder Draft，不逐场审批或强制对象入库。素材齐备后输出最终 Draft。局部样段不成为全片布局，未改变的画面不重做。只有实际工具缺口冻结复现给 WSL，视觉设计留 Windows。

未批准资产只在隔离 Review 副本预演，不通过普通 install 的 force 后门。Review 标明候选和请求 revision，同时隔离生产 Work、Current、资产源、packages / candidates / acceptances、源登记及全局配置。可生成测试视频并在 Review 库模拟接纳 / 安装，但这些记录不自动成为生产接纳；禁止正式 Finalize、归档完成和平台草稿。

验收准确实现、依赖和实际输入后，公共组件按现有准入精确安装到目标 Work，其余 Work 不升级。Work-local 补丁应用前核对源快照，基础变化只比较受影响 Scene，不覆盖整片。仅元数据变更不重复验收效果；执行代码、资源、依赖或视觉默认值变化须验证受影响部分。组件、Plan、Draft 分开记录，但一句明确回复可同时涵盖。

独立资产先导入隔离候选，再按准确身份、版本、包摘要、所需运行环境和实际 Fixture 记录接纳；目录出现或 `migration-ready` 不等于可用。新增兼容包不改 Harness 白名单、不重发程序，也不等待旧 42 项 Gallery 整组完成。接纳记录不修改 hash 覆盖的实现状态；Work 复制精确包及依赖到原 vendor / Lock，AssetStore 更新或离线不改变已绑定作品。

Studio 打开当前可编辑工程；登记版本、Accepted Snapshot 和冻结资产只通过真实复制的隔离审阅工程查看，不用 hardlink/symlink 伪装隔离。审阅副本修改不自动进入原 Work。Studio 改动当前源码后，旧 MP4、截图或 QA 不再冒充对应新源码；沿用原来源关联重新生成受影响证据。

## 验收与未验证项

1. R1 独立根直接调用自己的工具与配置，无 session 文件/环境变量要求或自动生成；从其他 cwd 调用仍准确，Review 不写生产。
2. 原生 CLI、官方 Studio 与实际工程 URL 正确；中文/空格路径、端口冲突和 Windows Agent 沙箱权限分别实测，不放宽整盘权限。
3. 严格包校验与部署根管理文件校验分离；用户 Skill、Work/资产保留，管理文件修改冲突可报告，更新互斥和失败恢复有效。
4. 当前 M2–M3 场景、音频、源文件、ID、Accepted Snapshot 与 Final 不变，R2/R3 只验证受影响工具行为。
5. 单 Scene 方向批准不获得 full Finalize 权限；完整 planned-placeholder Draft 可预览但不具最终交付资格，最终 full complete Draft 沿用原接受机制。
6. 源音频 cue、剪辑/take/速率、Scene crop、倒跳和随机 seek 经实际短片检查，关键画面及音轨不依赖回调；无音乐/Blender 不阻塞非依赖场景。
7. 兼容资产冻结准确依赖，旧 Work 在外部库离线时仍读取闭合副本；同身份版本不同内容拒绝覆盖。程序回滚不自动降级数据或删内容。

实现、Linux/mock 检查、Windows 原生实机、交互 WebGL、抓帧 WebGL、硬件编码和真实生产复用分别报告。软件渲染不冒充 GPU，Windows 浏览器打开 WSL 页面不冒充原生闭环，技术夹具不证明返工下降。
