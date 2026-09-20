# HyperFrames 实现与 QA

## 实现

- Windows 在 Work-local 或已登记 AssetSource 编写 Scene、模块、GSAP / Three / shader 与视觉内容；WSL 只修 Harness、宿主、合同和依赖装配。安装包、已接纳包、vendor 与 Accepted Snapshot 不原地改，必要变化派生新源 / 版本。
- 默认 Scene 组合模块与本地媒体，旧完整组件只读兼容；M1 仅接入已交付的 module/media 子集，不假称 Template / Recipe 或通用依赖构建器已完成。Scene 只安排所需 Beat，允许计算布局和内聚空间舞台，不强制双画幅或透明根层。
- 采用 Plan 已确定的视觉主题参数，不强制 Profile；旧字段只作兼容读取。
- 阶段与接受边界只见 `.studio/workflow.md`；旧 reference/layout 记录保留原语义，不作为动态参考通过证明。
- 日常制作与 QA 默认由 Work CLI 启动锁定官方 Studio；当前工程可编辑，登记版本只打开独立复制的审阅副本，不暴露冻结快照、vendor 或外部资产。历史自制页面仅限显式 `--legacy`。实际项目 URL 和定位端口来自启动结果，不硬编码或猜测；旧 MP4 / QA 与源码不一致时重新生成受影响证据。
- 宿主 Timeline 必须同步、确定性构建，使用 `{ paused: true }` 并注册到 `window.__timelines`；模块将动作写入该 timeline，不另行注册全局播放权。异步媒体 / 几何准备须完成后再同步建 timeline，ready 前不首次 seek。
- 动作不依赖 `Math.random()`、`Date.now()`、实时 delta、异步 Timeline、`repeat: -1` 或多个 Timeline 同时修改同一属性；可用固定 seed 初始化数据，再按时间直接求值。
- composition 或 Scene 保留 `S01` 等稳定 ID；结构性偏离返回 Animation Plan。
- `talking_head` 仅在人为主叙述的适用 Scene 保留人物布局；A/B-roll 按各 Scene 叙事职责安排，主声源贯穿切换且只播放一次，其他视频音轨按需要明确静音。
- 按 Plan 选材和 `visual-design.md` 实现 seek-safe 的语义累积、强调、返回与叠层状态；直接 seek 与顺序播放结果相同，不只在播放回调中新建文字。Research 不规定动画机制。
- 动效按表达需要组织焦点、关系、证据、对象转化与交接，不要求每组件独立入场。稳定阅读贯穿 Scene，不以统一结尾停顿代替；只有可定义的真实进度才使用进度条，演示值明确标记。
- Scene 布局按 Plan 预留图片 / 视频位和需要阅读的文字位；素材内已清楚呈现的信息不重复覆盖。缺少素材时保留稳定 Slot，不用虚构素材填满。
- 逐 Scene 读取 Plan 的精确资产引用和 Binding；全片主题不等于局部结构通用。角色、连接、条件、去向、反馈及结果进入实际图形 / 状态，不能把不同语义字段统一压成文字行。未支持类型明确返回当前 Scene 的实现缺口，不静默 fallback 普通卡片；同构表达允许复用。
- Skill 讲解按需要使用真实截图与完整解释；允许对比、列表、左右分栏和稳定证据页，按真实文字与音频安排阅读，不强迫每场发生变形。

## 混合时间与资源

当前候选通过 `project-config.json` 的 `snapshot_dependencies` 列表显式声明动态依赖；存在该键时按入口静态 src/import/fetch 字面量与声明文件收集闭包，未支持的 srcset/imagesrcset 明确报错，不漏拷后冒充闭合。历史工程没有该键时沿用原快照合同。准确源、副本与接受关系仍冻结，不对可变源使用硬链接。

- 先核对本地 HyperFrames / GSAP / Three.js 版本与适配器，优先复用已有 `hf-seek` / `window.__hfThreeTime` 接口；上游存在不代表当前安装可用。
- 使用 GSAP 的工程和组件须在本地 GSAP 后显式加载同版本的 `MotionPathPlugin.min.js`，两者随资产进入快照闭包。锁定 Studio 0.8.27 会在插件缺失时自动尝试 CDN；即使当前动作未使用该插件，也不能依赖这个联网 fallback。无 GSAP 的静态样段不因此增加依赖。
- DOM / GSAP 与 WebGL 共用全局时间，明确 Scene 偏移和局部重定时；同帧先求值属性、镜头与 shader，再绘制。成片动作不能以独立 RAF 或 `setAnimationLoop()` 为时间权威。
- 渲染关键状态不能仅放在 `onUpdate` / `onComplete` 回调；随机 seek 可能抑制回调。Flip、拆字与布局状态在字体/资源就绪后固定，不在播放回调中才补正文。
- 优先复用返回有限 Timeline 的小函数或既有效果注册接口，不另建引擎。效果只暴露实际需要的配置，由宿主控制尺寸、主题、资源、seed 与时间；文字默认 DOM / SVG，效果不拥有全局叙事。
- Three.js 与 addons 固定同版本，画布尺寸、像素比与色彩配置由工程控制。纹理、shader、模型、效果代码及其他实际依赖进入现有快照闭包，抓帧不临时联网；提供就绪与释放行为，不释放他人共享资源。
- 不引入依赖历史帧的物理模拟、反馈 shader 或累积拖尾，除非可重建任意时刻或已烘焙。Three.js 故障只阻塞相关 Scene，不静默以静态图冒充通过；主视觉替代沿用局部确认边界。

唯一动态参考及包含混合效果的 Draft 应实际播放、暂停、拖动、倒跳、再播放，并按 `[t3, 0, t1, t3]` 抓帧比较同一时刻。检查实际 Scene 范围、DOM/WebGL 同帧、阅读、就绪与释放；单 Scene 不证明全片正确。完整 planned-placeholder Draft 可缺已登记素材，但所有 Scene 及实际承诺动作必须存在。最终 Draft/Final 必需资源和效果闭合。Mock/静态检查不算 Windows 原生渲染通过，技术夹具不算生产复用。

需要混合求值时，可将 `.studio/runtime/scene-binding.js` 复制到 Work 的 `project/runtime/`，由 `HarnessScene.bindScene({start, duration, timeline, ready, renderAt, dispose})` 接到当前 HyperFrames 的 `hf-seek` / `waitUntil`。`start` 相对当前 composition 文档；绑定器拥有未单独注册的局部 paused Timeline，先求值再调用 `renderAt(localTime)`，宿主仍负责可见性。不要再将同一 Timeline 加入主时间轴或注册两次。`ready` 等待资产，不异步拼装 Timeline；释放时只清理绑定器自身资源。普通 GSAP 场景不需要此接线。

历史 `tests/visual-mixed.mjs` / `tests/visual-plan.mjs` 含视频编码路径，不能直接用作 v3.3 无导出验收。测试仅使用 Studio/浏览器动态证据或明确隔离的无编码入口；test-work、Draft 和局部声画检查均不以视频导出兜底。

## 音频与裁取

优先复用 timestamps 与 `section_map.json`。语义 cue 定位 Anchor、字符范围或明确 occurrence，未可靠对齐的字符不均匀插值。源片段采用半开区间，按 `timeline_in + (source_time - source_in) / rate` 映射；多 take 明确选择，被删除词无有效 cue。单 Scene 预览减去 crop 起点而不改原对齐，仅在输出 fps 时量化。

文字新增按所对应短句或核心词的实际起点快速揭示，不能等整句结束或提前透露后文；非文字视觉事件再按语义选择动作开始、完成或结果可读。SFX 按内部 hit offset 反算起点，负起点明确 preroll/裁切/替换。Preview 和 render 共用 cue/mix 输入，不以 seek 回调即时播放音轨；关键画面同样可按目标时间重建。音乐分析只在需要时按 hash/参数离线缓存，不依赖实时 WebAudio；缺 BGM 或 Blender 不阻塞非依赖场景。

在 Studio 验证源声音、工程映射、命中前后帧及连续播放；未试听明确说明，计算误差不冒充 ASR 声学精度。已有音轨不重复 ASR。

## Draft QA

在项目目录使用已锁定的本地 CLI；以下 `npx --no-install` 不下载或升级依赖：

```bash
npx --no-install hyperframes check
```

修复错误、空 Scene、越界、遮挡、不可读和严重节奏问题。对照 Plan 检查问题 Scene 的稳定状态及核心变化：连接有指向，条件分支可区分，反馈在状态中可见，选稿与必需 Slots 不丢失。只看开头或 contact sheet、仅有字段 / CSS 差异不算语义通过；同 easing 或相似外观不自动失败。普通 Warning 不阻止 Draft。Plan 登记的 planned placeholders 允许全片预览，准确标出缺口；占位不是代码错误的豁免，也不具备最终交付资格。只有 full 范围且必需素材齐备的版本能获得完整接受并进入 Final；单 Scene 方向批准不能代替。

表达与观看检查统一按 `visual-design.md`，语义揭示和全画面静止分别验收；不以 SVG/tween 存在证明兑现设计。技术检查、设计兑现与用户接受分别保留。Windows Studio 实际声音、连续播放、暂停、seek/回拖缺证据时记未验证；播放受限交工具缺口，不导出带声短段或整片 Draft。

## Final QA

生产 `finalize` 不带文件参数时编排接受源渲染、ffprobe 与全量解码 QA，保留失败恢复 journal；该机器检查不替代实际声音/视觉和首次跨引擎一致性证据。记录实际 render/probe/decode 调用次数、耗时与返回码；工具内部重试、缓存命中、tokens 和成本未知时保留 null，不推算成功率或节省。

成功后仅清理本次冗余 candidate，清理失败登记并保留文件；下次持锁 Finalize 只有在当前 Final、manifest、candidate、QA 的 hash 与引用证明仍有效时才重试清理。其他未登记 browser/build 缓存保留，不推定已自动安全回收。

仅在生产 Variant 的 Finalize 交付链，从准确 Accepted Draft 的闭合快照正式渲染并保留收据，不从变化的可编辑工程冒充接受版本。以下是既有底层正式渲染入口，不是 Draft/test-work 的导出许可：

```bash
./work --work <id> --variant <id> preview render <draft-id> --output <final.mp4> --final
```

新编码文件检查流、规格（60fps high）、原音时长、全量解码、代表帧及必要音频核验；实际缺陷修复后重渲染。Final Error 阻止 `./work finalize ... --qa-passed`，通过后只完成目标 Variant 的 Finalize；软归档是独立标记，不自动归档、不搬目录。

QA 按影响范围：已接受且未变仅检查来源/证据适用性；局部变化只查受影响 Scene、状态和交接；共享布局/时间线/宿主变化按依赖扩展。编码 QA 不重审已接受观点/设计，仅 Finalize/归档核对来源、收据、文件、目标及归档结果，不重复审片/渲染。只报告结果与真实未验证项。

## 按需资产接线

通过现有 `component` 能力从已配置的外部资产来源检索，以资产元数据和接纳记录为准；旧 `.studio/components/**/COMPONENT.md` 仅作只读兼容来源，身份冲突不静默覆盖。按 Scene 关系、真实文字及可选说明、素材形态、画幅、可用时间和状态变化核对适配；名字相近或能换标题不算适配。模块 / 媒体读匹配的 `asset.json` 与声明的用法 / 样例，旧组件读 `COMPONENT.md`、必要 `cases/**/CASE.md` 和边界 Fixture，Case 不扩大公共合同。已适配或能通过合同内组合 / 参数解决的能力直接复用，不重做审批样段。语义简报、精确版本、Binding 与必要差异保留在 Plan 原有资产列，不新建数据库。

统一发现入口是 `work component list --query <用途或别名>`，按需使用 `--kind media|audio|module|theme|background|motion|component`、`--ratio`、`--tag`、`--recommendation recommended|historical|pending`；`--research-root <明确登记根>` 加入仅供参考的研究，`--rebuild` 重建派生缓存。结果区分接纳、推荐/历史/待补、可用性和检查范围；画幅未知不等于支持，metadata-only 不等于闭包已验证，候选、源和研究不冒充可安装包。新接纳但缺选型信息的包仍可发现；同 ref 不同 hash、缺文件或异常 acceptance 不得被旧缓存遮蔽。刷新失败标未同步并重试，不自动补接受、不把派生缓存变成权威。

按结果给出的实际取用方式处理：组件安装、外观绑定、原材料复制、依赖调用或仅供参考不能混同。采用时固定精确版本并重新校验 hash/闭包；查询、刷新、接纳新版、修改推荐和研究均不升级已有 Work。普通辅助图形的表达要求只见 `visual-design.md`；没有可用对象则由 Windows 在可编辑源制作，不要求 WSL 交付图形预设。

选型信息保存在已配置 AssetStore 的 `selection.json`，以精确 `id@vN` 为键；值可含 purpose、aliases、tags、examples、limitations、replacement 和 recommendation，别名/标签/示例/限制使用字符串数组。它不覆盖包身份、hash 或 acceptance，不写入冻结包；直接编辑后下次查询检查变化，不另维护第二份版本总表。

安装前运行 `./work component validate <component-id>@vN`，用显式 Work/Variant 和 Binding 文件运行 `./work --work <id> --variant <variant-id> component install <component-id>@vN --binding-file <binding.json>`；Plan 批准前增加 `--purpose plan`，仍要求 Script / Research 就绪与资产合格。`component verify` 校验当前 Work 的 vendor、Scene Bindings 和 `COMPONENT_LOCK.json`，不因无关库更新或来源暂不可访问让已有闭合副本失效。库级接纳固定准确版本、依赖、目标画幅及兼容条件；`migration-ready` 不是生产批准，不批量改状态或复用旧 hash。优先验证当前需要的资产，旧家族 / 全画幅清单只作 backlog，不阻塞单个兼容包。

module/media 使用 Binding schema 3 的 `component_ref`、`scene` 和 `usage`（role / required，可选 fit / focal_point），布局和动作留 Scene，不填旧 Slots。`component pack <source-directory>` 从 `asset.json` 冻结候选；独立样例在已登记 AssetSource 内用 `component install ... --project <sample>` 与 `component verify --project <sample>`，不注册伪 Work。实际文件仍复制到 `vendor/components/<id>/vN`，Lock schema 2 的 `components[]` 用 `asset_kind` 标记类型，旧 schema 1 兼容。

音频首轮仅支持原生 MP3 media entry，一个音效一个条目；集合关系留外部索引，保留原文件 ID、来源、许可及字节 hash，不伪装成 JS module。沿用 pack/validate/accept/list/install/verify，使用现有 ffprobe/ffmpeg 检查真实格式、时长、编码、采样率、声道及全量解码；缺工具、损坏或伪装文件明确失败。包已落盘但 acceptance 写入中断时不算已接纳，只能经准确 ref/hash 的显式重试恢复。音频入库不等于听感、响度、cue、混音或成片声音接受，不自动添加 BGM/SFX，不改变宿主唯一时钟。

2026-09-18 候选增量：`asset.json` schema 2 在相同管道加入声明式 theme/background/motion，保留 schema 1 字节与 hash。共同字段为 `contract_version:1`、`parameters`（可覆盖点路径到 type/default/minimum/maximum/enum）和 `compatibility`（ratios）；`asset_dependencies` 保存 `{ref,kind,package_sha256}` 精确依赖，不复用本地 `dependencies` 文件字段。当前静态声明资产跨包仅依赖 media，其他组合和动态 renderer 明确拒绝，不假装已支持。Theme entry 为 tokens/fonts JSON，Motion 为 slots/reduced_motion，Background 为 solid/transparent 与自身参数；字体和许可均在文件闭包。Theme 不声明 mode，mode 不参与 Theme 身份校验。

纯声明资产的 Binding schema 3 不要求 Scene，`usage.role` 为该 kind；递归依赖可标 `scope:dependency`，但必须从正常绑定根资产的精确依赖图可达，不构成绕过接纳的入口。每包沿用准确接受记录、hash 和本地 vendor 校验。JSON 预设不冒充可执行组件，也不因纯 JSON 强加动态 runtime 审片。

新 Account 的 theme/background 为精确引用，motion 为 reveal/emphasis/exit/transition 槽位到 `{asset:精确引用,entry:预设条目}` 或 null；省略继承、null 禁用。`overrides` 按 theme/background/motion 分组，组内采用 manifest 声明的点路径，0/false 不视作缺值。新 Variant 的 `appearance_lock` 保存规范化 JSON SHA-256、账户 revision/hash、精确闭包、最终参数与来源、宽高/fps/seed。账号默认不追改旧 Variant；宿主读取 `project/appearance-lock.json` 及 vendor，不重读当前服务默认值。新锁优先且校验失败不回退 legacy；无新锁保留旧 theme_settings/account_settings/Profile，不隐式迁移。

`work appearance resolve --account <id> --appearance-file <json>` 只读解析；`new`/`variant add` 可用相同 `--appearance-file`，其中 `parameters` 为本次参数覆盖，优先级高于账号 overrides。`--theme <id@vN>`、`--background <id@vN>` 固定当前准确接纳 hash，不跟随 latest；`--mode`、`--ratio` 独立，`--fps`/`--seed` 可显式给定。source 画幅必须提供 width/height 后冻结。创建在暂存对象完成 vendor 与 Lock 校验再公布；未知字段、缺依赖或错误 hash 不留下半冻结 Variant。preview 的快照和 metadata 包含该锁及实际闭包；断开源库后仍能验证，不覆盖旧 Draft/Final。

已有 Variant 的显式更新使用 `work --work <id> --variant <id> appearance rebind`，可指定 `--account`、`--theme`、`--background` 或 `--appearance-file`；默认只预检并显示差异，确认目标与差异后 `--apply` 才提交。原位更新不改变 Variant ID 或账号全局默认；保留正文、历史 preview/Final 和旧依赖，外观变化清空当前视觉接受、Draft 接受及 Final 关联，旧文件不代表新外观已接受。相同请求不重复修订。只在明确目标的可编辑 project 中用 `--upgrade-runtime` 升级已知旧 runtime，未知或用户修改版本拒绝覆盖，冻结快照不动。异常 journal 阻断目标的继续使用，运行同目标 `appearance recover` 恢复后再重试，不能手删 journal 绕过。

冻结时复制当前 `runtime/appearance.js` 到工程本地，宿主先校验锁与闭包，再 `await HarnessAppearance.load()`，随后同步 `apply(stage, resolved)`；不引用安装根活跃源码。Theme 输出 `--appearance-*` CSS 变量，`data-appearance-text/card` 是可选宿主标记，不替 Scene 决定布局和文字。字体声明的 family/path/license 必填，文件与许可属于包内 dependencies；style 可为 normal/italic/oblique，weight 可为 1..1000 整数、对应数字字符串、normal/bold 或升序范围字符串（如 `"100 900"`），缺省 normal。load 等待本地字体加载后才返回，布局测量与宿主 ready 必须在其后；缺失、损坏、越界或重定向明确失败，不静默退回系统字体。Typography 字体族 token 映射为实例私有别名，Scene 通过这些 CSS 变量使用字体；重复 apply 不重复加载，结束时调用返回对象的 `dispose()`，仅释放自身字体，不影响其他同名字体实例。无字体主题保持兼容。

load 默认以当前页面目录为 project；显式 projectURL 必须是同源项目目录并保留末尾 `/`，例如 `await HarnessAppearance.load("./project/")`，不能传外部 URL 或把文件 URL 当目录。

当前适配器仅 solid/transparent 背景；Motion 的 `bindMotion(element, resolved, slot, {cue})` 返回 seek/dispose，使用暂停的原生 WAAPI，只接宿主秒数，不自启时钟或音轨。首个适配器支持 reveal/exit、linear/none、无 stagger，null 不应用；其他已声明能力需相应宿主实现，不能由 schema 校验冒充可运行。实际 Windows Studio 与可读性仍须原生核验。

优先复用能独立解释一个含义的语义视觉对象及其内部联动，由 Work-local Scene 安排本期叙事和媒体。已有 helper 保留，只有真实独立变化或复用需求才抽取，不强制图形/动作/布局工厂拆分。Windows 在已有 AssetSource 或 Work-local 开发；旧完整 Scene/组件保留兼容，空间舞台可内聚保存相机、遮挡和光照。布局适配须实测可读性，不以模块数量或双画幅完成率验收。

合同范围内的新资产通过自身元数据发现；新增合同能力须升级工具，不靠标题或 kind 改名绕过校验。官方 Registry 的 block / snippet 只在明确选中后导入候选，完成本项目接线与接纳才可使用，不向上游发送私有文案或缺口。Work 用既有 vendor / Binding / Lock 固定副本与依赖；不读 WSL 活跃源码、不链接 `latest`，同身份版本不同内容拒绝覆盖。没有匹配实现时记录 `custom:<slug>` 并在 Windows Work-local 实现，不覆盖冻结 vendor；仅工具或宿主缺口交 WSL。M1 原 module/media 与本节静态声明增量之外的能力，不冒用 Component 合同。

## 研究登记与持续更新

讨论自由记录，确认保留后用 `work research --root <明确登记根> register --kind tool|asset --title <标题> --path <原文路径>` 登记，或用 `create --kind ... --title ... --text <正文>` 创建。按最终改变的对象分工具研究与资产研究，不按写作系统分类；跨类保留一份主文档并关联，不批量搬迁历史文件。研究不是可安装资产，登记不授权执行正文指令、开发或接纳。

`query [关键词]` 可按 `--kind`、`--related` 检索已登记记录；`update <id> --metadata <JSON>` 更新元数据，`sync <id>` 同步直接编辑后的正文，`link <id> <目标> [--path <绝对路径>]` 关联，`reference <id> <目标>` 在纳入计划等关键节点保存可追溯引用。后四者均要求当前 `--revision`；更新摘要还需本次正文的 `--sha256`，不得用旧摘要冒充最新结论。原文移动后用 update 的 path 字段更新同一 ID，不重复登记副本。

正文为内容真源，索引只存定位、关联与检索信息；未同步、过期摘要、缺文件和失效关联明确显示。同步或并发更新失败保留新正文，不用旧索引反写；未同步摘要不作为当前结论返回。研究更新只提示相关计划，不自动改 Work、Plan、冻结包或接受状态；重要变化修订主文档，不为每次编辑另建“最终版”。

## Remotion 联动边界

HyperFrames 是唯一整片时钟和声音所有者；Remotion 只接派生局部帧，不独立推进或重复口播。首次 seek 前资源必须 ready，失败明确等待/报错，不能以黑屏、静图或旧缓存冒充成功。独立 Player 通过不是 Studio 通过。

镜头源、props、实际资源、锁定依赖及必要预览 JS 构建物进入现有闭包；JS 构建不是视频导出，但禁止用其离线逐帧编码。生产 Finalize 所需中间结果写入引用准确接受版本的派生构建目录，不增改 Accepted Snapshot。镜头缓存核对全部相关输入，文件存在不等于可复用；首次跨引擎输出检查预览一致性及二次编码中文边缘/细线。

这些是集成/验收合同，不代表当前安装已经具备 Remotion 或 Windows 原生通过证据。实际能力以锁定实现、候选测试和原生 Studio 记录为准；失败冻结最小复现交 WSL，不回退预渲染 MP4。
