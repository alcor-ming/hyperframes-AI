# HyperFrames Windows 创作根

若根目录存在 `AGENTS.local.md`，同时读取其中保留的本机提供方与用户规则；本文件负责当前工具入口，不恢复旧 session 或历史安装路径。

用户直接在 Codex App 打开本目录并下达任务，无需打开 CMD 或建立 Harness session。Agent 使用本根 `work.cmd` 的绝对路径；它运行同根 `runtime/` 与 `.studio/`，配置读取 `.studio/.runtime/local.json`，不调用 WSL 创作入口或历史 session 启动器。`work.cmd doctor` 查看实际身份与 Review 范围。

前台先调用 `work.cmd current`，无 Current 时 `work.cmd list`，不猜作品。后台必须明确 Work/Variant，并以 `work.cmd --work <id> --variant <id> status` 启动；同一 Work/Variant 同时只允许一个执行者。生命周期、指针、接受、Final 与归档只通过 Work CLI。

读取当前 `WORK.md` 与 `variant.yaml` 后按 workflow 加载 Skill：`hyperframes_video` 用 `hyperframes-codex-workflow`，仅按阶段加载 Script、相关 Research、Plan、一个 Recipe/Profile；`hyperframes-anti-ppt` 只在 Plan/动态参考与 Draft 复审时加载。`podcast_quote_image` 在方案批准前用 planner_skill，批准后用 copy_skill，不加载视频规则。详细创作合同见 `.studio/workflow.md`，实现/QA 按需读取 `.studio/spec/`。

Windows 负责 Work-local 或登记 AssetSource 的内容和视觉代码，包括 Scene、GSAP、Three.js、shader、SVG、模型及内容脚本；复杂或可复用不因此交回 WSL。WSL 只修工具、宿主、合同、依赖与安装器，接收准确工具缺口的冻结最小复现，不写生产 Work/资产源。

保留已有 M2–M3 画面、源文件、Scene/Anchor ID、音频/对齐和未受影响内容；不回退公开 HEAD，不重跑 M0–M1。整片 Plan -> 一个真实 Scene 动态参考 -> 一次方向批准 -> 完整 planned-placeholder Draft -> 素材齐备最终 Draft。局部布局不复制全片，不逐 Scene 审批，不另建 Shotbook。单 Scene 方向和占位 Draft 不授予 full Finalize 权限；最终 Draft 沿用既有完整接受。

安装工具、runtime、受管理规则、已接纳 AssetStore、vendor 和 Accepted Snapshot 只读；修改在可编辑源完成，复用时冻结新版本。保留用户 Skill 与未知文件，不整根镜像删除。更新先停止相关 Studio/render/build，使用安装器和现有互斥/恢复；不得热换运行中的工具。单次命令/长进程固定输入，无跨对话 session 绑定。

Review 候选使用自己的根配置、WorkStore、AssetStore 与必要 source-copy；禁止修改生产 Current、源、接纳记录、全局默认配置，禁止正式 Finalize、归档完成、平台草稿或发布。测试接受不转为生产接受。未明确授权不删除历史包、作品或不可替代数据；不自行 commit/tag/push。

不公开上传/发布或购买额度。平台草稿须对准确 Work/Variant 明确授权，不点击发布、不读取 Cookie。ImageGen 仅在明确授权、方向 Plan 批准且有 Asset Brief 时使用；视频不烧录底部字幕，播客图文遵守自己的字幕合同。缺音乐或 Blender 不阻塞非依赖制作。

只报告实际结果、改动、缺口和必要决定；WSL/mock、Windows 原生、带声渲染和生产验收分别报告，未验证不冒充通过。
