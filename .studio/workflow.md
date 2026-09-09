# 创作工作流

## 最小启动

Windows 从固定 `workspace/start.ps1` 创建会话，之后使用返回会话目录内的入口，整个会话绑定同一已安装版本；下文 `./work` 在 Windows 对应该目录的 `work.cmd`。`work.cmd doctor` 显示实际绑定，候选启动必须指定 `-Candidate <id> -ReviewRoot <隔离WorkStore>`。WSL 负责 Harness、组件内部和新效果开发，只在明确请求的私有复现副本中调试。Windows 可以编辑本作品文字、Slots、布局、时间和跨 Scene 编排，不修改已安装 Harness 或冻结 vendor。

前台交互运行 `./work current`；后台任务使用已分配的 Work ID 与 Variant ID 显式启动。读取 `WORK.md` 的 `workflow` 后再路由。`hyperframes_video` 只加载当前 Work、Variant、Script、一个 Recipe 和一套 Profile；Research 按当前 Scene / Anchor 缺口只读采用条目与相关资料依据，视觉阶段再读 Plan。`podcast_quote_image` 在文章方案批准前加载规划 Skill，批准后加载文案 Skill，且只读取当前阶段的机器产物。已有合格输入时跳过上游步骤。

## HyperFrames 视频

### 下载视频的文案分流

下载视频统一复用 `qivance-music` 的共享 WhisperX/FasterWhisper 运行时与 GPU 锁，不在本仓库复制模型或 ASR 实现：

```bash
/home/jym/workspace/_external/scripts/asr.sh transcribe-faster <video> --output-dir <work>/materials
```

命令必须同时生成 `*.transcript.json` 和 `*.transcript.md`。JSON 的 `characters[]` 是字级时间真源；`segments[]` 只用于快速阅读。存在口播但字级对齐失败时停止，不得以段级结果冒充完成。

转录完成后，在 `SCRIPT.md` frontmatter 中选择一种 `mode`：

- `dbs`：保留 `source.md` 原始基线，允许 DBS 多轮修改口播；正文变化时递增 Script Revision 并等待批准。
- `verbatim`：逐字保留转录口播、稳定 Anchor 和原时间戳；正文 `approval` 为 `not_required`，DBS 只可处理诊断或 `PACKAGE.md`，不得改写口播。

两条路径汇合后，先用最终 Script 的核心主题执行 `./work --work <id> --variant <variant-id> name "<核心主题>"`，再按 Scene 索引与最终口播的实际信息缺口完成同一 Variant 的 `RESEARCH.md`。只补查受影响内容，不替代或反向改写口播；没有缺口时记录无新增研究。Script Revision 变化先核对适用范围，完成必要条目更新和 Revision 同步后继续，不默认刷新全片。

`SCRIPT.md` 的口播正文使用稳定 Anchor；简短 Scene 索引必须放在成对 `<!-- scene-index:start -->` / `<!-- scene-index:end -->` 内，只记录 `Scene | Anchor 范围 | 时间预算 | 观众重点 / 调研方向`。索引是规划输入，不是口播。需要纯文本、统计、配音或对齐输入时统一使用 `./work --work <id> --variant <variant-id> script text`；只有需要同时保留 Anchor 时增加 `--anchors`。旧 SCRIPT 没有索引时按原正文读取；如已有等效索引，只补成对标记，不强行重排内容。

### 内容归属与按缺口研究

Research 只补当前内容实际缺少的理解、比较、应用或记忆点信息，可按需选择概念 / 原理 / 例子、前后 / 方案比较、应用 / 过程 / 效果、背景故事 / 反差事实 / 代表性案例；过渡和个人感受可以不研究。优先一手资料，发现事实错误时定点纠正，不另做“边界调研”。

同一 `RESEARCH.md` 内，“资料依据”保存研究结果、来源和资料或素材证据位置；源视频证据时间点不等于成片展示时间。“采用信息”按现有 Scene / Anchor 与简短条目标题保存可直接使用的信息稿和来源引用，必要时标核心 / 可选；只有歧义时加简短编号。不写布局、图标尺寸、裁切、动画状态或成片秒数。

每个 Scene 先筛选有效主题信息，再保护完整表达。候选知识存在不等于必须上屏；“不伪造”“不泛化”等内部制作约束不改写成观众正文。删除无信息增量的重复，不迁移到下一状态、脚注、口播或另一组件。可选说明为空就不生成，不用默认空话填 Slot；真实来源、必要导航、原文对象和条件仍保留，不自动扩写免责声明或边界栏目。

逐字口播引用 Script Anchor。口播摘录加工成独立维护的信息文字时写入 Research 采用信息并注明口播来源，不因此联网。原视频 / 截图内文字归素材，清楚呈现时不重复覆盖。“步骤一”“输入”“结果”等无独立主张的表现标签直接写在工程；数据、比较、因果和“效率提升十倍”等独立主张必须来自采用信息及其资料依据。Plan 引用这些来源，只用少量文字示例说明设计，不成为第二份信息稿或标签表。

同一主模型负责内容到画面。换行、层级、分组、出现顺序和表现标签直接在样段 / 工程调整；删除重复措辞、等义精简或改成流程短语时，同时原位更新 Research 采用条目及呈现，不重新联网、不生成阶段性交接或文字审批。等义以观众最终得到的结论不变为准；顺序变因果、比较对象变化、必要数值 / 单位 / 归属消失均为实质修改。

不采用可选信息由主模型决定。新增数据、比较或因果只补查相关条目；删除核心信息，或改变事实结论、观点、已确认叙事时，集中提出局部取舍、建议和对 Scene / 时间的影响，沿用既有用户确认。确实无法同时保留核心信息与时间预算时，直接给用户真实取舍，不要求 Research 反复压缩。

Research 标记为 `ready` 后，创建 Animation Plan 的同一步调用 DBS 完成 `PACKAGE.md`：使用 `dbs-xhs-title` 生成候选并选择 Top 1，再根据最终 Script 与 Research 写一条封面文字、一句话简介和内容概括。内容概括按主要对象或主题简短分项；介绍多个 Skill、工具、功能或案例时逐项单独说明。文档只保留这四项最终结果，不附公式分析或候选清单，也不新增审批门。

进入 Animation Plan 时加载 `hyperframes-anti-ppt`，按当前内容来源、时间依据、Recipe、Profile、Subtemplate 与画幅检查结论是否被正确表达、需要阅读的文字是否可读以及动效关系，不要求逐字逐卡摆放，不套用统一状态公式。结果合并进同一份 `ANIMATION_PLAN.md`，不新增审批产物。组件的检索、版本、Slots 与安装由视频工作流或组件库能力负责。

通过现有 `component` 能力从已配置的外部资产来源检索，以资产元数据和接纳记录为准；旧 `.studio/components/**/COMPONENT.md` 仅作只读兼容来源，身份冲突不静默覆盖。按 Scene 关系、真实文字及可选说明、素材形态、画幅、可用时间和状态变化核对适配；名字相近或能换标题不算适配。只读匹配资产的 `COMPONENT.md`、必要 `cases/**/CASE.md` 和边界 Fixture，Case 不扩大公共合同。已适配或能通过合同内组合 / 参数解决的能力直接复用，不重做审批样段。语义简报、精确版本、Binding 与必要差异保留在 Plan 原有资产列，不新建数据库。

安装前运行 `./work component validate <component-id>@vN`，用显式 Work/Variant 和 Binding 文件运行 `./work --work <id> --variant <variant-id> component install <component-id>@vN --binding-file <binding.json>`；Plan 批准前增加 `--purpose plan`，仍要求 Script / Research 就绪与资产合格。`component verify` 校验当前 Work 的 vendor、Scene Bindings 和 `COMPONENT_LOCK.json`，不因无关库更新或来源暂不可访问让已有闭合副本失效。库级接纳固定准确版本、依赖、目标画幅及兼容条件；`migration-ready` 不是生产批准，不批量改状态或复用旧 hash。优先验证当前需要的资产，旧家族 / 全画幅清单只作 backlog，不阻塞单个兼容包。

可复用组件、背景、Profile 与效果在 WSL 独立开发封装，Windows 按明确任务接纳到外部 AssetStore；先注册已有分离来源，不复制第二个权威库。兼容新资产通过自身元数据发现，不改全局枚举或重发 Harness。官方 Registry 的 block / snippet 只在明确选中后导入候选，完成本项目接线与接纳才可使用，不向上游发送私有文案或缺口。Work 用既有 vendor / Binding / Lock 固定副本与依赖；不读 WSL 活跃源码、不链接 `latest`，同身份版本不同内容拒绝覆盖。没有匹配实现时记录 `custom:<slug>`，其新内部实现仍交 WSL，不覆盖冻结 vendor。

### 轻量布局 Plan

Animation Plan 覆盖全片 Scene / Anchor、筛选后的 Research 或素材引用、逐场资产选择、视觉方向、动态方案与待定项，不复制完整信息稿。只有新信息结构、无法承载必要信息的布局或未确定的全片风格才构成设计缺口；为同类缺口做一个轻量样段并明确适用 Scene 和差异，数量可以为零。仅待库级验证 / 接线不是设计缺口；全部适配时引用已有资产的已验收 Preview，不重新制作同一演示。正常内容越界 QA 不增加组件设计审批。

样段用普通 HTML/CSS 呈现实际内容；其中需要阅读的文字使用拟采用的颜色、字体、字号、行距和层级，并匹配目标画幅。可用极少量 JavaScript 切换少量静态状态，不以灰色线框冒充设计。媒体占位说明用途、对象、比例和裁切意图，不使用失效路径、虚构 URL 或空文件，也不触发下载、probe、转码、同步或全媒体哈希。已有且影响布局的真实图片可使用，只检查实际用到的资源；事实核查与内容所需媒体流程不因此跳过。

主要 GSAP / Three 动作先写对象关系、起止状态、阅读位置及结果，必要时补替代。样段复用 HTML/CSS，官方 Studio 的薄承载只补必要根容器、画幅和展示时长；该时长不冒充口播时长，不为预览补齐其他 Scene、全片时间线、新 GSAP / Three 动作、真实媒体同步或 MP4。范围与未实现项留在 Plan / CLI 元数据，不绘成观众画面角标；能判断当前缺口就提交。

使用现有 preview 生命周期，样段目录位于当前 Variant 内并含 `index.html`；`--sample-dir` 按 Variant 解析（也接受其内部绝对路径），`--scene` 可重复。画布节点声明正整数 `data-width` / `data-height`，每个已展示 Scene 的 `id` 或 `data-scene-id` 与 Plan 表及 `--scene` 一致，例如：

```html
<main data-width="1920" data-height="1080">
  <section data-scene-id="S01"><!-- 当前片段实际文字与布局 --></section>
</main>
```

上例只是节点约定，实际样段还需匹配画幅的 CSS 和真实内容。实际资源均置于样段目录内，CSS `@import` 可递归引用，图片使用单一 `src` 而非 `srcset`，语义占位不写资源路径。

```bash
# 全部 Scene 已适配，无新样段
./work --work <id> --variant <variant-id> preview register --purpose plan --kind reference
# 有实际设计缺口时，改用 layout 登记该样段
./work --work <id> --variant <variant-id> preview register --purpose plan --kind layout --sample-dir <Variant内样段目录> --scene S01
./work --work <id> --variant <variant-id> preview open plan-v001
# 用户确认布局与实施方向后执行；不接受 Draft
./work --work <id> --variant <variant-id> preview accept plan-v001
./work --work <id> --variant <variant-id> preview diff plan-v001
```

两种 Plan 登记择一；`reference` 不制造虚构工程或播放地址，审阅 Plan 中的已验收资产 Preview 与逐场引用。

Plan 冻结当前 `SCRIPT.md`、`RESEARCH.md`、`ANIMATION_PLAN.md` 及实际需要的样段 / 资源，不要求完整工程或正式音频。批准范围分别记录全片配色 / 字体、局部资产或样段适用 Scene、同意实施但未验证的动作 / 媒体。局部布局默认只覆盖已列 Scene，不能由一个样段推导全片模板；静态检查不证明全片播放或渲染通过。

完整可执行 Visual Plan 保留为明确选择的高级路径：`preview register --purpose plan --kind executable`，使用完整工程与依赖闭包；顶层 Scene 使用 `id="S01"` 或 `data-scene-id="S01"` 及 `data-start`、`data-duration`，可选 `data-reading-time`。旧记录和省略 kind 的旧调用保留原语义，不要求新 Plan 走此路径。

日常工程、缺口样段和登记版本默认通过 Work CLI 启动锁定官方 HyperFrames Studio；返回实际启动的项目 URL，不把源码 `index.html` 标成预览入口，不硬编码端口或猜地址。当前制作打开可编辑工程；登记版本导出独立审阅副本后打开，不用 hardlink / symlink 暴露 Accepted Snapshot、vendor 或外部资产。副本修改不自动成为当前 Work 或旧批准版本。自制审阅页只保留显式历史查看，不静默 fallback；本机官方接入受限时说明限制，由用户选择临时替代。

`preview open` 默认等同 `preview open current`；`preview open <plan-id|draft-id>` 审阅指定版本，`--legacy` 才打开历史自制页面。`preview context [target] --fields selection,lint --detail compact` 读取已启动的准确工程上下文，确需详细样式才改 `full`；`preview stop [target]` 只停止该目标的会话。

默认 Studio 浏览器使用 Work 返回的隔离 `browser_profile`，通过真实 Chrome Do Not Track 设置关闭官方遥测，不改用户主 profile。Agent 使用 `--no-open` 自行自动化时也复用该 profile，并在导航前核对 DNT；CLI 环境变量不等于浏览器前端已经停用遥测。

受控 Windows 入口解析当前会话的 HF 路径，普通运行不下载最新版或升级依赖。底层 `--hyperframes-dist` / `--hyperframes-cli` 仅用于运行时诊断。定位时核对锁定版本实际支持的 `preview --context --json`，绑定准确 Work / Variant、工程和实际端口；先取 Scene ID、源文件、composition、时间及必要 selection / lint，确需样式才取 full。多个实例不随意选择，缺对象时不猜。

Studio 编辑后按既有来源关联重建受影响 MP4、截图和 QA，旧证据不冒充当前源码。内容字段同步回 Script / Research 的唯一选稿位置，或暂停该字段再生成；不让生成器覆盖用户修正，也不将 HTML 变成第二套文案库。

用户一次确认 Plan 及适用样段 / 资产引用，不新增 Style / Motion / Prototype 审批。Draft 共享已确认主题，逐 Scene 读取 Plan、Binding 和实际资产，优先完成最不确定镜头。角色与连接、条件与分支、反馈与结果必须进入图形或可见状态；`participants`、`branch`、`feedback` 不能全部压成通用文字行，未支持表达明确报告当前 Scene 的实现缺口，不静默 fallback。允许同构 Scene 复用，不以换颜色 / easing 代替语义实现，也不为差异数量重写正确场景。普通实现与纠错不重复审批，主构图或语义实质变化才局部确认。必需媒体和效果缺失不能接受完整 Draft 或进入 Final。`preview render <draft-id> --output <final.mp4> --final` 从 Accepted Draft 渲染，`--refined-project <Variant内目录>` 支持保留原快照的重定时。

三类时间分开维护：SCRIPT Scene 索引只给规划预算；正式音频与 `section_map.json` 保存实测时间；工程时间线决定画面实际出现与持续。`verbatim` 可用字级转录证据聚合的原时间戳作规划依据，源视频或音频仍是实测权威；`dbs` 没有正式音频时才估算。Plan 只记时间依据、必要阅读顺序和节奏意图，不复制精确时间表。

## Windows 与 WSL 请求交接

Windows 先完成逐场信息选型、配色及效果方案，只有实际缺口才做样段；新效果未交付但不影响布局判断时不阻塞 Plan。Plan 通过后按需交接组件内部或新效果，在当前讨论中形成 `REQUEST.md`，包含希望观众理解什么、行为、保留项、现有能力缺口、实际文字、画幅、阅读窗口、素材与相邻交接、验收输入。能从 Work 获取的信息不重复询问，不新增需求批准门。新组件、通用 GSAP、Three 主体仍由 WSL 实现。

Windows 用明确 Work/Variant 冻结请求；`--file` 是允许改变的工程相对路径，`--context-file` 是只读复现输入。源码来自当前工程或指定 `--preview` 快照：

```bash
./work --work <id> --variant <id> request freeze effect-001 --brief <REQUEST.md> --scene S01 --file compositions/S01.html --context-file index.html --preview plan-v001
./work request export <requests/effect-001/r001> --output <WSL私有复现目录>
# WSL 在私有副本实现；patch 内仅包含允许修改的相对路径
./work request deliver <冻结revision目录> candidate-001 --source <patch目录>
# Windows 收到交付后，在原 WorkStore 创建隔离 Review
./work request review <原revision目录> --delivery <交付目录>
./work request feedback <原revision目录> --delivery <交付目录> --note "只调整 S01 的焦点迁移"
# 仅在用户明确接纳后，由 Windows 应用准确交付
./work --work <原id> --variant <原id> request accept <原revision目录> --delivery <交付目录>
```

`review` 返回隔离 WorkStore，使用工作台 `start.ps1 -Candidate <包ID> -ReviewRoot <返回路径>` 开新会话，再注册 `--purpose plan`、播放和测试渲染。Review 不改生产 Current，不允许正式接受、Finalize、归档完成、普通生产安装或平台草稿。请求反馈仍归属准确 revision/交付，不用 WSL 录像代替 Windows 实际执行。

组件交付可在 `deliver` 增加 `--component <package> --binding <binding.json>`；正式接纳另提供 `--approved-component <批准包>`，保留生产准入限制。Work-local 交付不必公共化。`accept` 校验来源与变更范围，不等于 Plan/Draft 接受；其他 Work、未受影响 Scene、原 Accepted Snapshot 与 Final 不自动升级或覆盖。WSL 输出交付和技术结果，Windows 维护请求、反馈和接受决定，不双写同一状态。

## Talking-head

```text
下载/内容输入 -> 选择 dbs 或 verbatim -> 必要时批准 Script
-> RESEARCH.md -> 逐 Scene 筛选与资产匹配 -> Animation Plan + 必要缺口样段（可零）
-> 确认 Plan -> 源视频或用户录制 + section_map -> 优先实现高风险镜头 + 完整 Draft
-> 接受 Draft -> Final QA + 60fps high render -> Finalize -> 自动归档
```

## Pure HyperFrames

`verbatim` 下载视频先沿用逐字稿原时间戳；其他没有正式配音的输入才按字数、语速和信息密度估算时间。两者都先完成 `RESEARCH.md`，再制作接近 Final 的无声 Draft。接受 Draft 后接入正式配音时，从对应源码快照继续，只调整时间、停留、转场和元素出现顺序。

已有正式配音时沿用媒体依据规划，Draft 以 `section_map.json` 对齐；没有音频可估算。不得仅为查看布局强制配音、ASR、长音频同步或视频导出。

## 检查点

1. DBS 修改口播正文时批准 `SCRIPT.md`。
2. `RESEARCH.md` 标记为 `ready`，资料依据与采用信息覆盖当前实际缺口；Revision 变化时先核对受影响范围，不自动重研究全片。
3. 创建 Animation Plan 时同步用 DBS 完成 `PACKAGE.md` 的标题、封面文字、一句话简介和内容概括。
4. Plan 用 `hyperframes-anti-ppt` 检查逐 Scene 方案、已验收资产适配与必要缺口样段，不以零样段或未实现动作判失败；结果只进入现有 Plan。
5. 正式 Draft 前一次确认引用当前 Research Revision 的 Plan 及适用样段 / 资产引用，分别记录主题、局部方案范围和未验证动作，不新增 Motion Plan 审批。
6. Draft 提交用户前在官方 Studio 用 `hyperframes-anti-ppt` 复审问题 Scene 的稳定状态及核心变化，不仅检查开头或 contact sheet；再按现有流程注册和接受 Draft。
7. Final 前接受一个 Draft 作为视觉基线。

技术 QA、时间微调、换行、easing、性能优化和归档不要求用户批准。

局部反馈可用 `preview diff <id> --scene S02 --range 18.2 23.5 --note "保留正文，只改焦点迁移"` 记录到当前 Variant 的 `.runtime/feedback.json`；不带 `--note` 只读比较。时间范围仅适用于实际时间线，静态样段用 Scene 和对象定位，Scene 可重复指定。从新增样段开始在现有 Work 备注记录可取得的输入/输出 token（含缓存原口径）、Windows 与 WSL 的 Plan 及总制作投入、布局/动效返工，等待用户时间单列；缺失统计如实标明，不用代码行数代替 token，不以技术夹具宣称成本下降。

反馈定位到预演/Draft 版本、Scene、必要时间范围或对象。`preview diff <id>` 查看当前工程相对该快照的源码差异；只改受影响 Scene 与必要衔接。普通等义修改完成 Research / 工程更新和 Revision 同步后，由主模型确认口播、Anchor 与已批准 Plan 的视觉正文未变；Plan 只允许 frontmatter 的 `status`、`visual_plan`、`revision`、`script_revision`、`research_revision` 变化。随后使用 `preview diff <accepted-plan-id> --scene S02 --note "等义修改依据与局部影响" --compatible` 记录适用性。机器校验明确 Scene、冻结 / 当前输入与工程哈希，不猜自然语言；旧记录缺冻结来源时保留原流程，实际范围不符或后续再修改时不能沿用兼容记录。

`--compatible` 只沿用 Accepted Plan 进入一个新 Draft，避免未受影响内容被全片重做；它不把当前文件伪装成旧 Accepted Draft 已批准。Accepted Draft 的来源内容或 Revision 变化时必须注册并接受新 Draft，只有上述 Plan 纯状态 / `visual_plan` 元数据变化不使其失效。主构图、隐喻、视觉目标或核心内容变化仍只确认变更部分；未受影响源码、冻结资产、原 Accepted Draft 与 Final 不覆盖，新 Draft / Final 继续走现有来源与接受检查。正式配音接入优先调整阅读停留，再处理可变动作与衔接，不默认整场 `timeScale`，不截断音频或删必要信息。总投入、方向性返工、实际影响范围和有效复用可记入现有 Work 备注；没有真实交付证据时不宣称返工下降。

## 播客金句图

```text
来源 URL -> trendradar-media -> 校验并复制到 materials/
本地或已下载视频 + 可选原生转录/字幕 -> resolve transcript
-> 保留创建时的三位序号，只补充嘉宾名 + 核心主题
-> 规划 Skill 通读原文并生成 3 个完整文章方案
-> DBS 检查核心机制、受众情绪与传播理由 -> 用户批准 1 个方案
-> 文案 Skill 调研嘉宾背景并完成 RESEARCH.md
-> 先写开篇、每图小标题与第三人称正文，调用 dbs-content 诊断并按结果修订
-> 正文稳定后调用 dbs-xhs-title 生成可追溯公式的大标题候选并选定 Top 1
-> 调用 dbs-ai-check 诊断完整成稿
-> align time -> 每条 Hero/支撑句抽取 3 张候选帧 -> Agent 选帧
-> 从视频帧图片底部向上裁切并绘制紧凑双语字幕，render 8 至 12 张图
-> 生成小红书标题、纯文本正文、话题与有序图片清单
-> Agent 视觉 QA -> Finalize -> 自动归档 -> 经明确授权可保存到创作者平台草稿箱
```

字幕在覆盖区间内拥有文案和时间权威，转录只补无字幕区间；同语种明显冲突必须先人工处理。转录条件缺失或失败时进入 `waiting_user`，由用户决定是否改用保留原画面字幕的 fallback，不得静默降级。

每个文章方案包含 8 至 12 个按原文结构排列的图片组，每组固定 1 条 Hero，并用若干约 10 个汉字的完整支撑短句推进内容；中文总字数以 60 至 90 字为目标区间，不设逐句硬上限。同一内容可按语义拆成相邻两张图，图片只保留核心结论与必要论证，背景、案例和完整推导写入 `PACKAGE.md`。图片边界跟随原文的铺垫、观点、论证、例子、对比与收束，不按标点机械切分。用户批准 1 个文章方案是唯一内容门；批准后不得重新解释原文或另提方向。`RESEARCH.md` 只调研与获批核心相关的嘉宾身份、经历、背景故事和事实边界。全部面板绘制 50px 中文与 30px 英文；支撑条按双语文本实测高度分配并最多保留 30px 画面，Hero 至少占 60%，必要时把水平边距从 6% 收到最低 3%。Hero 与支撑字幕黑底 alpha 分别为 145 和 165。各面板从选定视频帧图片底部向上裁切，字幕条之间无间隙，整图至少保留 40% 无字幕空间。`PACKAGE.md` 直接使用可复制的纯文本：第一行为标题，其后为开篇、`01｜小标题` 形式的分节、正文、署名、`原视频：<视频原标题>` 和标签；render 只负责分离标题、正文、1 至 3 个话题和有序图片，正文连同话题不超过 1000 字。只有用户对准确 Work/Variant 明确授权后，才可用已登录浏览器保存草稿；不点击发布。

候选阶段用 `dbs-resonate` 检查每个方案是否只服务一个核心机制；`dbs-spread` 只提供受众情绪、有效立场和第一传播者信号，用于候选理由与排序，不改写原文。文案阶段不得把读取 Skill 或默认借用规则当成调用：先完成不含平台大标题的开篇、每图小标题与正文草稿，再单独调用 `dbs-content` 输出针对表达效率、认知落差和小标题的具体修订诊断，由文案 Skill 应用诊断；正文与小标题稳定后，单独调用 `dbs-xhs-title` 仅根据获批文段生成 5 至 8 个候选，覆盖至少 3 类公式、标注公式编号并给出 Top 3，再选定不超过 20 字的 Top 1。嘉宾背景不得作为大标题前提，除非它本就存在于获批文段且对含义必不可少。最后单独调用必做的 `dbs-ai-check` 诊断完整成稿。`dbs-content` 只诊断，不代写；修订仍由文案 Skill 完成。`dbs-hook` 与 `dbs-script-flow` 不进入本工作流。

URL 获取只调用外部 `trendradar-media` v2.0。适配器只接受成功 envelope 与单条成功 manifest，复核大小和 SHA-256 后原子复制到 `materials/source-video.*`，并保存不含外部临时路径的 `materials/acquisition.json`。YouTube 可先采用带结构化时间戳的原生转录；不可用时才在用户明确同意后调用共享 ASR。下载器本身不提供转录。

## 状态

Variant 只使用 `active`、`waiting_user`、`waiting_asset`、`parked`。具体阶段由文件、`wait_for` 和 `next_action` 推导；归档由目录位置表达。
