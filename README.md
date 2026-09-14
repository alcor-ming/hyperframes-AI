# HyperFrames AI Harness

面向本地内容创作的轻量 Harness。它以 Work 组织一次交付，以 Variant 管理平台版本，目前提供 `hyperframes_video` 与 `podcast_quote_image` 两条独立工作流。

## 快速开始

Windows 用户在 Codex App 直接打开 `D:\AI\AI+hyperframes`，新建对话并下达任务即可。`work.cmd` 是 Agent 按需调用的命令行工具，不是需要双击打开的聊天窗口；根入口不创建或依赖 Harness session，不选择候选或 Review 根。下文 Bash 命令是相同 CLI 的 WSL 写法。正式 Work 由 Windows 写入；WSL 开发和回测使用冻结请求与隔离副本。

```bash
./work root show
./work new "作品标题" --workflow hyperframes_video
./work status
./work variant add douyin-9x16 --from main --ratio 9:16
```

开发仓位于 `/home/jym/workspace/hyperframes+AI`，外部 WorkStore 位于 Windows `D:\AI\AI+hyperframes`（WSL `/mnt/d/AI/AI+hyperframes`）。本机绑定保存在 Git 忽略的 `.studio/.runtime/work-root`；只有 `./work root set <absolute-path>` 会切换 WorkStore。

`work new` 必须选择 Workflow。CLI 会在命名锁内按 Workflow 分配三位序号，并创建 `work-<workflow>-<序号>` 形式的 Work ID 和目录；输入标题只作为初始显示标题，不参与目录命名。视频工作流创建 `pure_hyperframes`、`optical_fluidity`、`16:9` 的 `main` Variant；Agent 可通过参数选择其他 Template、Profile 和 Ratio。

```bash
./work new "人物口播" --workflow hyperframes_video --template talking_head --subject-position left
./work wait recording
./work resume
```

播客图文接受本地视频或明确的来源 URL。URL 通过外部 `trendradar-media` v2.0 下载并校验后复制进 Work；YouTube 可先读取带时间戳的原生字幕，失败后再使用已授权的共享 ASR。第一个 Skill 通读转录并给出 3 个完整文章方案，用户确认其中 1 个；第二个 Skill 先调研嘉宾背景，再从获批的选取文段归纳开篇第一段、每图小标题和第三人称正文，最后仅根据这些文段的共同结论、冲突或因果拟定大标题。文段之外的嘉宾背景只能从开篇第二段起补充，不能主导标题。`PACKAGE.md` 直接保存可复制到创作者平台的纯文本标题、`01｜小标题` 分节、正文和话题，render 同步生成有序图片 JSON；每篇渲染 8 到 12 张图，图片用约 10 个汉字的 Hero 与支撑短句把中文控制在约 60 到 90 字，完整背景、案例和推导留在正文。画面使用 50px 中文与 30px 英文，Hero 至少占 60%，支撑字幕按双语文本高度紧凑排列：

```bash
./work new "播客金句" --workflow podcast_quote_image
./work finalize /path/to/render --qa-passed
```

多链接输入按“一条来源一个 Work”拆分，并以 detached 方式交给后台任务。`Current Work` 只代表前台焦点；后台任务必须始终显式绑定自己的 Work 和 Variant，因此小红书与 HyperFrames Work 可以同时运行：

```bash
./work new "播客 A" --workflow podcast_quote_image --detached
./work --work <work-id> --variant main status
./work --work <work-id> --variant main name "嘉宾名-核心主题"
./work list
```

后台 Work 在创建时已经获得稳定序号；转录完成后只补充嘉宾名 + 核心主题，再完成 3 个文章方案并停在 `article_selection`。HyperFrames 视频在 Script 稳定后只补充核心主题。Work ID 与目录名始终不变，重复命名保留原序号；`work list` 按位置、Workflow 和序号排列。用户只需确认 1 个方案；单个 Work 失败不阻塞同批其他 Work。

视频 `SCRIPT.md` 的口播正文可附成对 `scene-index` 注释包围的非口播 Scene 索引；需要配音、统计或对齐文本时使用 `./work script text`，索引不会混入。`RESEARCH.md` 只按当前 Scene / Anchor 的内容缺口补充资料依据和采用信息，不规定视觉实现。Plan 引用 Script、Research 或素材，不再复制一份信息稿。

视频沿用现有 Script、Research、音频与 M2–M3 画面，先完成整片 Plan，再选一个真实 Scene 动态参考。一次方向批准后直接生成完整 planned-placeholder Draft，素材齐备后生成最终 Draft，沿用原完整接受和 Final 流程。不逐 Scene 审批，不新建 Shotbook，不把样段或占位 Draft 当成具备 Finalize 权限的 full Draft。

复用优先选择承担明确含义的视觉对象，保留内部联动和既有 helper。Plan 列清逐 Scene 的 A/B 职责、语义对象、素材占位 ID 与人声 cue 意图；音乐分析可选，已有 timestamps/section_map 优先复用。最终 Draft 必需素材齐备，计划内占位不阻塞此前全片预览。新登记参数只在实现并验证后加入帮助；旧 reference/layout 记录保持原含义。具体约定见 [创作工作流](.studio/workflow.md)。

日常预览默认启动锁定版本的官方 HyperFrames Studio，返回实际项目 URL；当前工程可编辑，登记版本只在隔离副本打开：

```bash
./work preview open current
./work preview context current --fields selection,lint --detail compact
./work preview open draft-v001
./work preview stop current
# 仅显式历史查看保留自制审阅页
./work preview open draft-v001 --legacy
```

Studio 修改同步原文案真源或暂停对应再生成，旧 MP4 / QA 不继续代表新源码。`reference` Plan 没有虚构的可播放工程，直接审阅其资产引用。

Draft 与 Final 生命周期：

```bash
./work preview register /path/to/draft.mp4
./work preview accept draft-v001
./work finalize /path/to/final.mp4 --qa-passed
```

`--qa-passed` 只能在 Agent 已完成 `.studio/spec/hyperframes.md` 规定的 Final QA 后使用。所有 Required Variants 完成 Final 后，Work 自动移入外部 WorkStore 的 `works/archive/<year-month>/`。

## 公开内容

- `AGENTS.md`：创作边界与最小上下文路由。
- `.studio/`：工作流、能力表、规范、Recipe、模板和生命周期 CLI。
- `.agents/skills/hyperframes-codex-workflow/`：视频工作流薄路由 Skill 与三套稳定 Profile。
- `.agents/skills/hyperframes-anti-ppt/`：Animation Plan 与 Draft 阶段的动态叙事重构和复审 Skill。
- `.agents/skills/podcast-quote-image/`：转录理解、原文证据整理与 3 个文章候选方案 Skill。
- `.agents/skills/xiaohongshu-article-copy/`：标题、开篇、每图文案、DBS 检查、取帧、渲染与 QA Skill。
- `.agents/skills/native-subtitle-quote-image/`：无法转录时经人工确认启用的 [原版 v1.0.0 Skill](https://github.com/chengyi-ai/native-subtitle-quote-image/tree/f1fa5b70448f620ea92179357eca4b0222481b9d)。
- `work`：无第三方依赖的本地 Work CLI。

## 私有内容

外部 WorkStore 的 `works/`、旧 `tasks/`、媒体、工程、Draft、Final 和运行状态不进入开发仓或 Git。Harness 不实现下载后端，而是调用独立的 `trendradar-media`；它不公开发布内容，也不内置 ASR 模型。经用户对准确 Work/Variant 明确授权，可使用其已登录的 Windows Chrome 保存小红书创作者平台草稿，但绝不点击发布。

默认由 Windows Work-local Scene 组合模块与媒体，而不是填入完整冻结组件的 Slots。Windows 在 Work-local 或已登记 AssetSource 开发 Scene、GSAP、Three.js、shader、SVG、图片和模型；兼容视觉资产在 Windows 打包、精确接纳，不触发 Harness 发布。AssetSource 可编辑，AssetStore 已接纳包不可原地修改；先登记已有来源，不建立第二份可写权威库。`migration-ready` 不自动通过，不强制全库、双画幅、五阶段或全画幅透明根层。Work 沿用 vendor、Binding 和 `COMPONENT_LOCK.json` 固定实际依赖，库更新不漂移旧作品，已有闭合副本不依赖外部库在线。旧完整组件和历史快照只读兼容，不自动拆解或删除。

M1 扩展 module/media 最小子集，旧 Component 合同保留兼容；Template / Recipe、完整 Background / Profile 独立安装仍是后续目标。`component pack` 从 Windows 源目录的 `asset.json` 冻结实际文件，不修改编辑中源。Windows 使用根目录 `work.cmd`：

```bash
./work component source-add <existing-source-directory>
./work component pack <source-directory-with-asset.json>
# 导入已有冻结包时改用 component import <exact-package-directory>
# Windows 审阅独立副本后，使用 pack/import 返回的精确摘要
./work component accept <component-id>@vN --sha256 <package-sha256> --note <review-result>
./work component list --query <relationship-or-name>
```

资产配置归属当前入口根，变更只影响后续命令，长进程固定启动时输入；Review 不修改生产配置。module/media 的 `asset.json` 与 Binding 示例见 [资产 PRD](docs/PRD/hyperframes-component-motion.md#4-m1-最小资产合同)。独立样例沿用已实现的 `component install ... --project <registered-source/sample>` 与 `component verify --project <registered-source/sample>`，不伪装正式 Work，不增加另一套播放器。

## 根目录部署

Windows 日常直接打开 `D:\AI\AI+hyperframes`；工具实际位于同根 `runtime/`、`.studio/`，根配置位于 `.studio/.runtime/`。直接 `work.cmd` 按自身位置选择工具，不经过 `.harness/releases/current` 或 session，不自动生成 session。已有 Work、资产、用户 Skill 与请求不迁移。

一次命令解析配置一次，Preview/render 固定本次输入；更新前通过已有进程管理停止相关进程，以最小互斥防止启动和更新交错，不热换依赖。配置变更只影响后续命令，Agent 更新后重读根规则。

待安装 ZIP/staging 严格校验全部清单、hash 和路径；部署根只校验拥有的管理文件，保留合法用户文件和本地配置。更新先备份再覆盖管理文件，只有旧清单拥有且新版移除的文件可清理；用户修改冲突保留并报告，中断可检测恢复，不全根 mirror/delete。

本机候选基于当前受控工作树，不回退公开 HEAD，不重跑 M0–M1，不自动 commit/tag/push。候选根使用独立配置与 Work/Asset/source-copy，真实入口形态与生产一致，不写生产 Current 或接纳状态。先交付 R1 根候选，再按 Windows 所选 Work 暴露的问题修 R2/R3；不把候选通过冒充已更新生产。

`release local` / `release candidate` 仍区分本机构建身份；正式 `release build` 使用 `harness-YYYY.MM.PATCH`，要求干净、tag 与 upstream 一致。完整包固定 Windows Python、Node、HF、GSAP/Three、浏览器及音视频依赖，普通制作不浮动安装。准确安装参数仅以实现后的帮助为准，不将设计目标写成可执行命令。

旧稳定包与历史 session 保留回退资料，不再作为新根的依赖。回滚程序不自动降级 Work schema、改资产绑定或删旧数据；旧工具无法读取时保留新数据与可用版本。实现、WSL/mock、Windows 原生 CLI、Studio、WebGL、带声短片及真实生产验收分别记录。

Windows 直接开发视觉内容和效果；仅宿主、CLI、合同、加载、seek 或依赖装配缺口交给 WSL。`work request freeze` / `export` 冻结最小复现，WSL 在私有副本修工具并交付安装候选，Windows 在 Review 验证；纯布局、图标或动作设计不走工具请求。旧 `deliver` / `review` / `accept` 补丁合同保留兼容，不扩大 WSL 写生产源的权限。完整参数见 [请求交接](.studio/workflow.md#windows-与-wsl-请求交接)。Review 不允许正式 Finalize、归档完成或保存平台草稿；模拟资产接纳仅留 Review，接纳交付不等于接受 Plan/Draft，不覆盖未受影响场景。

Windows 原生、交互 WebGL、抓帧 WebGL、视频硬件编码和真实复用分别验证。构建或 Linux 测试通过不表示 Windows 已部署或硬件路径通过。目标与验收边界见 [Windows 工作台 PRD](docs/PRD/hyperframes-windows-workbench-wsl-handoff.md)。

Windows 侧共享 ASR 由包内 `asr-wsl.cmd` 桥接到固定的 `Ubuntu` 和 `/home/jym/workspace/_external/scripts/asr.sh`；`HYPERFRAMES_ASR_SCRIPT` 仅可指定另一 Windows 入口。桥接器拒绝 WorkStore 外的输入和输出，并把路径转换、可用性检查和转录合并为唯一一次固定调用：

```text
wsl.exe --distribution Ubuntu --exec /bin/sh -c <fixed-script>
```

任务参数只经 `WSLENV` 传入，路径由 WSL 内的 `wslpath` 转换；stdout、stderr 和退出码原样返回。Windows Codex 沙盒已确认能复用 WSL ASR、模型和 GPU，但未持久授权时每次调用仍可能先报 `Wsl/Service/E_ACCESSDENIED` 并要求审批。Codex 规则只匹配 Agent 发起的顶层 argv，因此应持久批准包内 `asr-wsl.cmd transcribe-faster` 前缀；不得批准任意 `wsl.exe` 命令。

完整产品契约以 `.studio/` 和 `AGENTS.md` 为准。
