## 按需资产接线

### 统一资产目录

`asset_layer` 为 building-block（通用积木）、scene-template（场景模板）、content（内容素材）、reference（参考样例），独立于技术 kind 与画面五层。新资产在元数据声明；冻结旧包通过 `selection.json` 补充，不改包或 hash。缺分类组件显示 unclassified，不按名称猜测；media 与声明式外观/图标默认 content。`lifecycle` 为 source/candidate/accepted；推荐、历史、待补是独立选型标记，不替代接纳事实。

`component list --asset-layer <分类>` 筛选；参考样例默认隐藏，用 `--include-references` 或 `--asset-layer reference` 显式查看，`--kind scene-source` / `--kind recipe` 自身也表示请求对应参考项。参考样例不能新安装，包括路径和依赖入口；已有 Work 冻结副本仍可离线校验。`.catalog-index.json` 与 `.discovery-cache.json` 是普通查询可写的派生文件，不是版本/接纳真源。`list --audit`（含 --rebuild）与 `interface` 不写缓存、索引或报告；两者都不修改 Work、Current、Binding、源或接受记录。README 与配方保留人工说明，不另维护平行资产总表。

列表按真实声明路径去重，保留不同来源与版本。普通列表最多显示 20 条紧凑记录，`total` / `shown` / `truncated` 说明筛选结果，`full_result` 返回同参数的完整 JSON 查询 argv；诊断也保留显示数量与总数。每条记录的 `detail.argv` 是传给本根 work 入口的准确详情参数，不是安装授权。遇到歧义按返回路径选择，不按名称合并或跳到最新版。安装仍采用原精确 ref/hash 和接纳校验。

AssetStore 的 `sources/` 是托管可编辑源，packages/candidates/acceptances 保持原结构。未迁移的外部源与 legacy 根继续发现；仅完整迁移核对后由 `catalog-migration.json` 退役对应根，原文件保留，不自动改生产配置。维护命令不使用默认生产根：

```sh
work component migrate plan --from <绝对资产目录> --to <绝对目标库> --classification <分类JSON> --output <库外绝对计划路径>
work component migrate apply --plan <计划路径>
work component archive plan --to <绝对库> --item candidates/example/v1 --output <库外绝对计划路径>
work component archive apply --plan <计划路径>
```

分类 JSON 以精确引用为键，例如 `{"example@v1":{"asset_layer":"reference","recommendation":"historical"}}`。已接纳包保留原接纳记录与字节；旧批准标签不自动变成接纳。相同身份/hash 可重放，不同内容拒绝覆盖。分类不明/不支持对象列为 pending，apply 拒绝；输入改变须重新生成计划，多个外部源分别迁移。candidate.json 的目标 path/review 随迁移更新，原 provenance 保留。

归档是带逐文件 hash 清单的非破坏性快照：原目录保留，`reclaimed_bytes` 为 0，不自动回收磁盘，避免破坏外部 Studio 的使用。仅接受完整且未改 review 的工具候选，或 workspaces/<名称> 中含 `{"owner":"hyperframes.asset-maintenance/v1","active":false}` 的 `.asset-workspace.json`。未知目录、Work、已安装 vendor 与已接纳包拒绝。物理清理需另行定义占用检测与授权。本版不新增 IconPark；24 个单图标包按明确映射保留 historical，20 个旧卡片家族按已确认归层填写分类表，未知列 pending，不自动重写视觉。真实迁移、归档和 Windows 验收另行执行。

F01-F08 使用 `card-kit@v1`，插槽与接线见 [Card Kit 接口卡](card-kit.md)。`component card-kit-source <新源目录>` 只导出自有源码，之后沿用 pack/validate/accept/install。Plan 是内容真源；`cards build` 生成挂载并用冻结字体实测容量，`cards studio` 在官方 Studio 旁提供回写 Plan 的卡片编辑器。不手改生成块，不把设计源批准当作正式资产接纳。

使用 `work component interface <准确包引用、source_ref或列表返回的路径>` 读取包、场景源或配方详情，不读实现源码；候选用 `component interface <路径> --candidate`。合法 source_ref 不要求 @vN，配方可无运行 entry。详情先显示当前状态、来源、入口、检查范围和 next_step，再显示声明的用法；历史 README 或源 classification_status 不替代包接纳。长用法可通过 full_result 的 --json 读取，说明附件越界或缺失明确失败。普通图标用 `work icons search <名称或别名>` 获取精确引用。缺库时从本机包运行 `work icons import --from <lucide-static 包根> --source <可编辑源目录>`，再按既有 pack / accept / install 流程处理；导入不自动接纳。安装到目标工程后，`work --work <id> --variant <id> icons use lucide:plug@1.45.0 --output icons/plug.svg` 取用闭包内 SVG，不联网、不改路径，保留来源标记及主题颜色/线宽。Plan 引用同一精确版本，SVG 随工程快照冻结。

通过现有 `component` 能力从已配置的外部资产来源检索，以资产元数据和接纳记录为准，身份冲突不静默覆盖。按 Scene 关系、真实文字及可选说明、素材形态、画幅、可用时间和状态变化核对适配；名字相近或能换标题不算适配。模块 / 媒体读匹配的 `asset.json` 与声明的用法 / 样例，组件读 `COMPONENT.md`、必要 `cases/**/CASE.md` 和边界 Fixture，Case 不扩大公共合同。已适配或能通过合同内组合 / 参数解决的能力直接复用，不重做审批样段。语义简报、精确版本、Binding 与必要差异保留在 Plan 对应 Scene 一节，不新建数据库。

创作统一发现入口是 `work component list --include-references --query <用途或别名>`，按需使用 `--kind media|audio|module|theme|background|motion|character|component|scene-source|recipe`、`--ratio`、`--tag`、`--recommendation recommended|historical|pending`；`--research-root <明确登记根>` 加入仅供参考的研究，`--rebuild` 重建派生缓存。结果区分接纳、推荐/历史/待补、可用性和检查范围；画幅未知不等于支持，metadata-only 不等于闭包已验证，候选、源和研究不冒充可安装包。新接纳但缺选型信息的包仍可发现；同 ref 不同 hash、缺文件或异常 acceptance 不得被旧缓存遮蔽。刷新失败标未同步并重试，不自动补接受、不把派生缓存变成权威。

按结果给出的实际取用方式处理：组件安装、外观绑定、原材料复制、依赖调用或仅供参考不能混同。采用时固定精确版本并重新校验 hash/闭包；查询、刷新、接纳新版、修改推荐和研究均不升级已有 Work。普通辅助图形的表达要求只见 `visual-design.md`；没有可用对象则在可编辑源制作，WSL 开发计划也可直接包含组件编辑。

选型信息保存在已配置 AssetStore 的 `selection.json`，以精确 `id@vN` 为键；值可含 purpose、aliases、tags、examples、limitations、replacement 和 recommendation，别名/标签/示例/限制使用字符串数组。它不覆盖包身份、hash 或 acceptance，不写入冻结包；直接编辑后下次查询检查变化，不另维护第二份版本总表。 旧包未声明画幅时可补 `ratios`（9:16、16:9、4:3、1:1 字符串数组）和非空 `ratios_basis`（可核对的既有声明或测试依据位置 / 说明），输出 ratio_source 标明来源。包声明优先，不与补充取并集；冲突或非法补充有诊断，缺依据仍为 unknown，具体画幅筛选不包含 unknown。补充不改变包、hash、安装权限或已冻结 Work；生产数据另由 Windows 按授权目标补充。

`component list --audit` 按内容区分场景 manifest、源审批与包 acceptance；包 component_ref / package_sha256 记录不生成虚假的场景缺字段告警，未知审批格式单独报告。真正的场景漏字段、源审批漏 manifest、失效入口和越界路径继续告警，不按 tests/fixtures 目录名整体跳过。

安装前运行 `./work component validate <component-id>@vN`，用显式 Work/Variant 和 Binding 文件运行 `./work --work <id> --variant <variant-id> component install <component-id>@vN --binding-file <binding.json>`；Plan 批准前增加 `--purpose plan`，仍要求 Script / Research 就绪与资产合格。`component verify` 校验当前 Work 的 vendor、Scene Bindings 和 `COMPONENT_LOCK.json`，不因无关库更新或来源暂不可访问让已有闭合副本失效。库级接纳固定准确版本、依赖、目标画幅及兼容条件；`migration-ready` 不是生产批准，不批量改状态或复用旧 hash。优先验证当前需要的资产，旧家族 / 全画幅清单只作 backlog，不阻塞单个兼容包。

module/media 使用 Binding schema 3 的 `component_ref`、`scene` 和 `usage`（role / required，可选 fit / focal_point），布局和动作留 Scene，不填旧 Slots。`component pack <source-directory>` 从 `asset.json` 冻结候选；独立样例在已登记 AssetSource 内用 `component install ... --project <sample>` 与 `component verify --project <sample>`，不注册伪 Work。实际文件仍复制到 `vendor/components/<id>/vN`，Lock schema 2 的 `components[]` 用 `asset_kind` 标记类型。

音频首轮仅支持原生 MP3 media entry，一个音效一个条目；集合关系留外部索引，保留原文件 ID、来源、许可及字节 hash，不伪装成 JS module。沿用 pack/validate/accept/list/install/verify，使用现有 ffprobe/ffmpeg 检查真实格式、时长、编码、采样率、声道及全量解码；缺工具、损坏或伪装文件明确失败。包已落盘但 acceptance 写入中断时不算已接纳，只能经准确 ref/hash 的显式重试恢复。音频入库不等于听感、响度、cue、混音或成片声音接受，不改变宿主唯一时钟。

`asset.json` schema 2 在相同管道加入声明式 theme/background/motion。共同字段为 `contract_version:1`、`parameters`（可覆盖点路径到 type/default/minimum/maximum/enum）和 `compatibility`（ratios）；`asset_dependencies` 保存 `{ref,kind,package_sha256}` 精确依赖，不复用本地 `dependencies` 文件字段。当前静态声明资产跨包仅依赖 media，其他跨包组合明确拒绝；module 背景和 character 按上文合同。Theme entry 为 tokens/fonts JSON，Motion 为 slots/reduced_motion，Background 为 solid/transparent 与自身参数；字体和许可均在文件闭包。Theme 不声明 mode，mode 不参与 Theme 身份校验。

纯声明资产的 Binding schema 3 不要求 Scene，`usage.role` 为该 kind；递归依赖可标 `scope:dependency`，但必须从正常绑定根资产的精确依赖图可达，不构成绕过接纳的入口。每包沿用准确接受记录、hash 和本地 vendor 校验。JSON 预设不冒充可执行组件，也不因纯 JSON 强加动态 runtime 审片。

新 Account 的 theme/background 为精确引用，motion 为 reveal/emphasis/exit/transition 槽位到 `{asset:精确引用,entry:预设条目}` 或 null；省略继承、null 禁用。`overrides` 按 theme/background/motion 分组，组内采用 manifest 声明的点路径，0/false 不视作缺值。新 Variant 的 `appearance_lock` 保存规范化 JSON SHA-256、账户 revision/hash、精确闭包、最终参数与来源、宽高/fps/seed。账号默认不追改旧 Variant；宿主读取 `project/appearance-lock.json` 及 vendor，不重读当前服务默认值。锁校验失败明确停止。

`work appearance resolve --account <id> --appearance-file <json>` 只读解析；`new`/`variant add` 可用相同 `--appearance-file`，其中 `parameters` 为本次参数覆盖，优先级高于账号 overrides。`--theme <id@vN>`、`--background <id@vN>` 固定当前准确接纳 hash，不跟随 latest；`--mode`、`--ratio` 独立，`--fps`/`--seed` 可显式给定。source 画幅必须提供 width/height 后冻结。创建在暂存对象完成 vendor 与 Lock 校验再公布；未知字段、缺依赖或错误 hash 不留下半冻结 Variant。preview 的快照和 metadata 包含该锁及实际闭包；断开源库后仍能验证，不覆盖旧 Draft/Final。

已有 Variant 的显式更新使用 `work --work <id> --variant <id> appearance rebind`，可指定 `--account`、`--theme`、`--background` 或 `--appearance-file`；默认只预检并显示差异，确认目标与差异后 `--apply` 才提交。原位更新不改变 Variant ID 或账号全局默认；保留正文、历史 preview/Final 和旧依赖，外观变化清空当前视觉接受、Draft 接受及 Final 关联，旧文件不代表新外观已接受。相同请求不重复修订。只在明确目标的可编辑 project 中用 `--upgrade-runtime` 升级已知旧 runtime，未知或用户修改版本拒绝覆盖，冻结快照不动。异常 journal 阻断目标的继续使用，运行同目标 `appearance recover` 恢复后再重试，不能手删 journal 绕过。

冻结时复制当前 `runtime/appearance.js` 到工程本地，宿主先校验锁与闭包，再 `await HarnessAppearance.load()`，随后同步 `apply(stage, resolved)`；不引用安装根活跃源码。Theme 输出 `--appearance-*` CSS 变量，`data-appearance-text/card` 是可选宿主标记，不替 Scene 决定布局和文字。字体声明的 family/path/license 必填，文件与许可属于包内 dependencies；style 可为 normal/italic/oblique，weight 可为 1..1000 整数、对应数字字符串、normal/bold 或升序范围字符串（如 `"100 900"`），缺省 normal。load 等待本地字体加载后才返回，布局测量与宿主 ready 必须在其后；缺失、损坏、越界或重定向明确失败，不静默退回系统字体。Typography 字体族 token 映射为实例私有别名，Scene 通过这些 CSS 变量使用字体；重复 apply 不重复加载，结束时调用返回对象的 `dispose()`，仅释放自身字体，不影响其他同名字体实例。

load 默认以当前页面目录为 project；显式 projectURL 必须是同源项目目录并保留末尾 `/`，例如 `await HarnessAppearance.load("./project/")`，不能传外部 URL 或把文件 URL 当目录。

两种模式均支持 solid/transparent/module 背景。四槽 Motion 资产采用 manifest `contract_version:2` 和 entry `capability_version:2`，精确 ref/hash 不可覆盖。含 v2 Motion 的闭包生成 appearance lock schema/contract 2、resolver 1，旧宿主明确拒绝。工具安装不升级旧 Work 的冻结 runtime；明确目标的更新仍用上文 rebind/upgrade-runtime，不修改历史快照或自动接纳资产。

Motion v2 的 `slots` 与 `reduced_motion` 均须完整声明四槽，选择的 entry 必须等于槽名。公共字段为 duration（非负秒）、easing（none/linear/ease-in/ease-out/ease-in-out）。下例是 entry JSON；资产 manifest 仍按既有 schema 2 包装，只有声明在 parameters 的叶子可覆盖，effect/color_token 不可覆盖，0/false 保留原义：

```json
{
  "capability_version": 2,
  "slots": {
    "reveal": {"effect":"short-rise","duration":0.4,"easing":"ease-out","opacity_from":0,"opacity_to":1,"y":12,"hide_before":true},
    "emphasis": {"effect":"focus-restore","duration":0.2,"easing":"linear","restore_duration":0.2,"color_token":"colors.accent","outline_width":3},
    "exit": {"effect":"fade-out","duration":0.3,"easing":"ease-in","opacity_from":1,"opacity_to":0},
    "transition": {"effect":"crossfade","duration":0.4,"easing":"linear"}
  },
  "reduced_motion": {
    "reveal": {"effect":"fade","duration":0.1,"easing":"linear","opacity_from":0,"opacity_to":1,"hide_before":true},
    "emphasis": {"effect":"focus-restore","duration":0,"easing":"linear","restore_duration":0,"color_token":"colors.accent","outline_width":3},
    "exit": {"effect":"fade-out","duration":0.1,"easing":"linear","opacity_from":1,"opacity_to":0},
    "transition": {"effect":"cut","duration":0,"easing":"linear"}
  }
}
```

opacity_from/to 是相对绑定时基础 opacity 的 0..1 倍率；reveal 的 to 必须为 1，exit 为 0。reveal 可选 fade/short-rise，hide_before 默认 true；false 只取消 cue 前的 visibility 隐藏，不取消起始 opacity。short-rise 和 exit 可选 x/y/scale，组合基础 transform，不自动创建包装层。强调使用冻结 Theme token 的合法颜色形成 outline，restoreCue 由 Scene 显式给定，不推算阅读时间。cut 的 duration 必须为 0。reduced 入退场不得位移/缩放或比常规动作更长，强调两个 duration 为 0，转场为 cut；模式在 load 时固定，bind 的 reducedMotion 布尔值可显式选择，切换须重建实例。

```js
const appearance = await HarnessAppearance.load(); // 包括本地字体 ready，失败不得宣布宿主 ready
HarnessAppearance.apply(stage, appearance);
const motions = [
  HarnessAppearance.bindMotion(revealLayer, appearance, "reveal", {cue: 1}),
  HarnessAppearance.bindMotion(revealLayer, appearance, "emphasis", {cue: 2, restoreCue: 4}),
  HarnessAppearance.bindMotion(exitLayer, appearance, "exit", {cue: 6}),
  HarnessAppearance.bindMotion({outgoing, incoming}, appearance, "transition",
    {cue: 7, endCue: 7.4, overlap: [7, 7.4]})
];
function seek(seconds) { for (const motion of motions) motion.seek(seconds); }
function dispose() { for (const motion of motions) motion.dispose(); appearance.dispose(); }
```

以上元素均为 Scene 已挂载的显式图层。每个绑定返回 seek/dispose，只由宿主秒数定位暂停的原生 WAAPI，不自启时钟、音轨或场景。结束/回拖保留 DOM；零时长在 cue 精确切换；reduced 转场在原 cue 而非 endCue 瞬切。emphasis 的 restoreCue 不早于常规进入结束；transition 的 endCue-cue 等于常规预设 duration，crossfade 的 overlap 必须覆盖整个交接区间，不能自行延长 Scene 或音轨。Scene 必须保持两个不同目标及祖先可绘制，不能在交接前隐藏 outgoing，Motion 只控制目标自身 opacity/visibility。

属性所有权覆盖绑定完整存续期（包括前后填充）：入退场占用 opacity/visibility 及声明的 transform，强调占用 outlineColor/Width/Style，转场占用双目标 opacity/visibility；已有动画或其他绑定争抢相同属性时在创建前拒绝。reveal 与 emphasis 可同元素组合；同元素的 reveal/exit 或转场应使用 Scene 显式隔离的运动层，不依赖创建顺序，也不自动包装表格或 SVG。绑定只采样一次基础样式，宿主不得在存续期争写所属属性；dispose 可重复调用，仅 cancel 自身效果，露出当前基础样式，不覆盖宿主对无关属性的更新。先 dispose 所有 Motion，再释放 appearance 字体。

源侧可运行示例及截图检查为 `tests/motion-browser.mjs`，使用隔离资产/工程的真实 pack/resolve/materialize/load/apply/bind/seek 链路，不接触生产 Work、不导出视频；覆盖常规/reduced 的 16:9、4:3、9:16，不代表任意内容自动适配或 Windows 原生 Studio/音频/Final 已接受。

### Motion v3 与混合闭包

Motion v3 使用 manifest `contract_version:3` / entry `capability_version:3`，四槽和 reduced_motion 均必填，保留 v2 effect 和严格字段校验。各槽可混用 v2/v3 包；appearance lock schema/contract 是闭包中最高 Motion 版本，resolver 仍为 1，新宿主按各 entry 自身能力校验，旧宿主拒绝新 lock。冻结旧 Work 不自动升级；准确目标的升级仍须显式 rebind/upgrade-runtime。

新增 reveal 为 pop / stamp / wipe / glitch-in；emphasis 为 pulse / shake / wobble / glow；exit 为 pop-out / wipe-out / glitch-out；transition 为 wipe / push / glitch-cut。公共字段 effect/duration/easing；入退场仍必填 opacity_from/to，reveal 可选 hide_before。pop、pop-out 支持 x/y/scale，stamp 另支持 rotate（度）；glitch-in/out、shake 支持 x/y，pulse 支持 scale，wobble 支持 rotate；glow 必填冻结 Theme 的 color_token，可选 blur。wipe、wipe-out、push 可选 direction（left/right/up/down）。不属于该 effect 的字段拒绝；effect/color_token 不可作为参数覆盖。

v3 的缓动增加 back-out 与固定采样 spring；normal 可选整数 hold_fps（1..240），以 cue 为相位原点只量化中间帧，cue 与结束状态精确，不能移动 endCue/overlap。新 emphasis 为一次性动作，不需要 restoreCue，结束恢复采样的基础样式；focus-restore 保持原合同。新入退场 reduced 使用 fade/fade-out，强调时长 0，转场 cut，不使用 hold_fps 或过冲缓动。每个 effect 仅拥有实际使用的属性，争抢拒绝，不自动包装层。

新版 v2/v3 Motion 绑定在 `__hfRhythmSources` 注册带 target/cue 的 `motion_<slot>` 候选，dispose 注销；探针只计目标可见且状态实际变化的事件，不把 WAAPI 的存在当作通过。

账号外观可完整指定 Theme/Background/Motion；跨账号的风格叠加只指定 background/motion、省略 theme。后者保留账号 Theme，前者覆盖，沿用当前解析合并规则，不新增资产 kind。

### 动效 B-roll module

可选 `broll` 块及挂载示例见 [创作合同](broll-assets.md)。pack/validate 校验角色、时长、timing、插槽/参数、各画幅安全区与完整 usage/examples；无 broll 的 module 不变。`component list --broll-role hook|concept|transition` 与 `--tag` 组合筛选，`component interface` 展示完整 broll。插槽由 Scene 源码传入，不改变 Binding schema 3、不新增 Plan 解析字段。

镜头导出 mount，按全片秒数 renderAt，返回实际 moments 与 dispose；stage/text 分别挂第 2/4 层并交给既有 HarnessRolls。可复用新工程冻结的 `runtime/broll.js` 做输入、字体容量、闭包路径和时间映射校验，module 自身资源仍走正常离线闭包。开发合成样例与双 Theme/双画幅/两种 timing 的真实管道检查见 `tests/broll-browser.mjs`，不携带生产库资产。

优先复用能独立解释一个含义的语义视觉对象及其内部联动，由 Work-local Scene 安排本期叙事和媒体。已有 helper 保留，只有真实独立变化或复用需求才抽取，不强制图形/动作/布局工厂拆分。组件可由 WSL 或 Windows 开发，空间舞台可内聚保存相机、遮挡和光照。布局适配须实测可读性，不以模块数量或双画幅完成率验收。

合同范围内的新资产通过自身元数据发现；新增合同能力须升级工具，不靠标题或 kind 改名绕过校验。官方 Registry 的 block / snippet 只在明确选中后导入候选，完成本项目接线与接纳才可使用，不向上游发送私有文案或缺口。Work 用既有 vendor / Binding / Lock 固定副本与依赖；不读 WSL 活跃源码、不链接 `latest`，同身份版本不同内容拒绝覆盖。没有匹配实现时记录 `custom:<slug>` 并在可编辑源实现，不覆盖冻结 vendor；仅工具或宿主缺口交 WSL。现有已实现资产合同之外的能力，不冒用 Component 合同。
