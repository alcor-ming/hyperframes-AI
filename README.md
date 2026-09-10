# HyperFrames AI Harness

面向本地内容创作的轻量 Harness。它以 Work 组织一次交付，以 Variant 管理平台版本，目前提供 `hyperframes_video` 与 `podcast_quote_image` 两条独立工作流。

## 快速开始

Windows 日常创作打开 `%LOCALAPPDATA%\HyperFramesAI\workspace`，先运行 `start.ps1`，再使用返回会话目录内的 `work.cmd`；下文 Bash 命令是相同 CLI 的 WSL 写法。WSL 开发仓不作为 Windows 的创作入口。正式 Work 由 Windows 写入；WSL 开发和回测使用冻结请求与隔离副本。

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

视频先逐 Scene 筛选信息，再按真实关系、文字、素材、画幅与时间匹配已接纳资产。全片 Plan 只为真实缺口制作轻量样段，数量可为零；同类缺口验证一次并注明适用 Scene。没有新样段时引用已验收资产 Preview：

```bash
./work preview register --purpose plan --kind reference
./work preview accept plan-v001
```

有缺口时，将真实文字与设计放在当前 Variant 的 `layout/index.html`；媒体可用语义占位，不为预览补整片动画：

```bash
./work preview register --purpose plan --kind layout --sample-dir layout --scene S01
./work preview open plan-v001
# 用户确认样段设计和实施方向后
./work preview accept plan-v001
```

两种登记方式择一，`preview accept` 只在用户确认 Plan 后执行。样段的官方 Studio 承载仅补静态 composition，不要求 Three、FFmpeg 或正式音频；接受不等于动态通过或 Draft 接受。配色、字体可全片共享，局部布局仅覆盖明确匹配的 Scene。Draft 按各自 Plan / Binding 保留连接、分支、反馈与结果，未支持表达报告当前 Scene 缺口，不静默退回通用文字卡片。完整可执行预演仍为显式高级路径。具体约定见 [创作工作流](.studio/workflow.md)。

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

可复用资产使用外部配置的 AssetStore，与 Harness 发布周期独立；先注册现有来源，兼容资产通过元数据发现，不修改全局组件白名单。WSL 开发和封装，Windows 接纳准确版本；`migration-ready` 不自动通过，不以整库 / 全画幅齐备阻塞单个资产。Work 沿用 vendor、Binding 和 `COMPONENT_LOCK.json` 固定实际依赖，库更新不漂移旧作品，已有闭合副本不依赖外部库在线。旧内置库与历史快照保留只读兼容，不自动删除。

当前独立接纳支持 Component 合同及同合同效果；Background / Profile 的完整独立安装仍是后续目标。Windows 会话使用其固定 `work.cmd` 执行以下命令，或安装时通过 `-AssetRoot` 设置独立目录：

```bash
./work component root <absolute-asset-store>
./work component source-add <existing-source-directory>
./work component import <exact-package-directory>
# 在 Windows 完成该候选的实际审阅后，使用 import 返回的精确摘要
./work component accept <component-id>@vN --sha256 <package-sha256> --note <review-result>
./work component list --query <relationship-or-name>
```

## 固定 Release 与 Codex App 部署

开发和构建只在本 WSL Git 仓进行。Windows Codex App 打开固定薄入口 `%LOCALAPPDATA%\HyperFramesAI\workspace`，从不可变 `releases\<tag>` 或 `candidates\<build-id>` 运行；`current` / `previous` 保留稳定安装与回滚入口。作品仍写入 `D:\AI\AI+hyperframes`，其中 `requests/` 保存私有交接、`review/` 保存隔离副本，不放 Harness 或运行依赖。

Release 使用 `harness-YYYY.MM.PATCH`。构建要求工作树干净、对应 tag 指向当前提交、分支已推送，并提供与 `windows-runtime.lock.json` 一致的运行时缓存：

```bash
./release build 2026.09.1 --runtime-cache /path/to/windows-runtime-cache
./release verify dist/hyperframes-ai-harness-2026.09.1-windows-x64.zip
```

首次准备固定 Windows 依赖是显式下载步骤，需具备该下载授权；普通创作命令不下载依赖：

```bash
python3 .studio/prepare_windows_runtime.py prepare \
  --cache /path/to/windows-runtime-cache --output-lock windows-runtime.lock.json
```

`windows-npm.lock.json` 固定完整依赖树。只有所有必需 Windows 文件已闭合并记录 SHA256，才移除 runtime lock 的 `pending_assets`；锁仍有缺项时构建明确失败，不生成只有 Python 的伪完整包。

本机回测不要求先提交、标记或推送：

```bash
./release candidate review-001 --runtime-cache /path/to/windows-runtime-cache \
  --include .studio/visual_plan.py --include .studio/visual_plan.html
```

候选按产品范围冻结当前源码；新增未跟踪文件需逐项 `--include`，示例不是所有新文件的清单。Manifest 记录 `channel=candidate`、基准 commit、dirty、源码文件及依赖哈希；默认输出 `dist/`。同一候选不可覆盖，重新构建使用新 ID。正式 `build` 的规则与 Git/公开发布授权不变。

完整 ZIP 内置 Windows CPython、Python 依赖、Node、HF、GSAP/Three、Chromium、FFmpeg/ffprobe 及入口。Codex App 解压 ZIP 后执行（首次安装必须提供 WorkRoot）：

```powershell
.\release.ps1 verify
.\release.ps1 install -WorkRoot D:\AI\AI+hyperframes
.\release.ps1 status
.\release.ps1 rollback
```

首次候选 ZIP 解压后执行 `release.ps1 install-candidate -WorkRoot D:\AI\AI+hyperframes`。可先从已安装候选目录运行 `work.cmd review init review-001`，只创建独立测试根、不改生产 Current，然后在固定工作台启动会话：

```powershell
.\start.ps1
# 候选必须使用已准备好的隔离 Review WorkStore
.\start.ps1 -Candidate candidate-review-001 -ReviewRoot D:\AI\AI+hyperframes\review\review-001
```

启动器输出 `sessions/<uuid>` 下的固定会话目录。Codex 后续仅使用该目录的 `work.cmd` / `work.ps1`，先运行 `work.cmd doctor` 查看实际版本、依赖、WorkRoot 与 Review 身份。安装包内的 `work.cmd session start --review-root <path>` 也可建立会话；未绑定会话的普通 Work 命令会拒绝运行。`preview open` / `preview render` 自动使用会话受控 HF，无需手填 `--hyperframes-dist`；静态样段通过同一锁定 Studio 薄承载，不加载正式音频或新增效果。缺少官方运行时会明确报错，不静默退回自制页面，也不冒充渲染能力。

会话 `work.cmd` 直接调用固定版本的内置 Python，不启动子 `powershell.exe -File`；`work.ps1` 仅保留为兼容入口。旧会话文件不会自动重写，入口修复后须选择新候选并创建新会话。安装根以当前 Codex App 内的 `%LOCALAPPDATA%` 或安装时的 `-ReleaseRoot` 为准，不能假设它与外部终端相同。若沙箱仍拒绝入口，保留准确命令和错误，不修改执行策略或把审批后通过当成沙箱验收。

稳定安装会验证 Manifest 与 WorkStore，再以 Windows junction 切换 `current` 并保留 `previous`；候选安装不改变稳定入口。配置、会话和缓存外置；会话固定实际包及其运行依赖，切换版本后开新会话，不热换 Skills 或播放器。回滚不删除 Work、旧快照、请求或 Final；旧包不自动清理。安装/回滚可带 `-CheckWork <id> -Variant <id>` 先检查目标版本能否读取指定 Work；未指定时会明确提示数据兼容性尚未验证。

Windows 可以编排 Work-local HTML、文字、媒体 Slots、位置和时间；新组件内部、新 shader 或通用动作主体交给 WSL。`work request freeze` / `export` 冻结并导出实际输入，WSL 用 `request deliver` 交付，Windows 用 `request review` 建立隔离副本、`feedback` 记录反馈，明确批准后 `request accept` 接纳精确交付。完整参数见 [请求交接](.studio/workflow.md#windows-与-wsl-请求交接)。未批准实现仅在 Review 预演，不能正式安装、Finalize、归档完成或保存平台草稿；接纳交付不等于接受 Plan/Draft，不覆盖未受影响场景。

Windows 原生、交互 WebGL、抓帧 WebGL、视频硬件编码和真实复用分别验证。构建或 Linux 测试通过不表示 Windows 已部署或硬件路径通过。目标与验收边界见 [Windows 工作台 PRD](docs/PRD/hyperframes-windows-workbench-wsl-handoff.md)。

Windows 侧共享 ASR 由包内 `asr-wsl.cmd` 桥接到固定的 `Ubuntu` 和 `/home/jym/workspace/_external/scripts/asr.sh`；`HYPERFRAMES_ASR_SCRIPT` 仅可指定另一 Windows 入口。桥接器拒绝 WorkStore 外的输入和输出，并把路径转换、可用性检查和转录合并为唯一一次固定调用：

```text
wsl.exe --distribution Ubuntu --exec /bin/sh -c <fixed-script>
```

任务参数只经 `WSLENV` 传入，路径由 WSL 内的 `wslpath` 转换；stdout、stderr 和退出码原样返回。Windows Codex 沙盒已确认能复用 WSL ASR、模型和 GPU，但未持久授权时每次调用仍可能先报 `Wsl/Service/E_ACCESSDENIED` 并要求审批。Codex 规则只匹配 Agent 发起的顶层 argv，因此应持久批准包内 `asr-wsl.cmd transcribe-faster` 前缀；不得批准任意 `wsl.exe` 命令。

完整产品契约以 `.studio/` 和 `AGENTS.md` 为准。
