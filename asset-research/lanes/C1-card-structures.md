# C1 卡片内容结构调查

调查日期：2026-10-02。范围：仅结构参考，不导入代码，不增加 F01–F08 卡面风格。5 个候选来源组，覆盖 9 类结构，共 21 个结构引用（同一来源/示例可以服务多个结构）。首推 C1-01 daisyUI、C1-02 Flowbite、C1-04 Mermaid。

## 证据边界与验收状态

- 已读取固定 commit 的 LICENSE 与下列源码，记录提交时间；未下载第三方图片、音频或代码包，交付只有本调查说明、链接和索引。
- 外站预览只保留原项目预览地址，不作为已完成访问或像素验收的证据。少量早期文档查询不等于完整预览验证；GitHub-only 边界确认后未继续站外访问。ECharts 预览图路径由固定 GitHub tree 确认，未下载图像。
- 预览站可能与固定源码不是同一版，尤其 Bootstrap 公开 5.3 示例与当前开发分支；遇差异，以此处固定源码为准。所有可读性/横竖版建议是本调查的设计推导，不是上游组件保证。
- 每类提供 2–3 个具体源码+预览参考，而不是把同一通用主页重复算作多个资产；来源组计 5 个候选，避免超过每路 15 个。
- 全部画面容量是未渲染实测的估计：按 1080×1920 / 1920×1080、四周约 6% 安全区、正文约 42–52 px、中文全角字估算；实际须本地字体排版与 3 秒读屏测试。ASCII 数字另计，长英文须更早折行。

## 与 R0 的差量

官方 Registry 已有 comparison-split、chat-thread、marker-checklist-card、flowchart，以及 C4 类的 bar-chart-race。优先利用其已有导入路径；本路提供槽模型与密度补充，不建议再复制一套相似模板。真正要补的合同是数据口径/来源、多对象比较、层级/矩阵、截图裁切/标注与确定性 cue。

## 九类结构：参考、插槽、口播编排与容量

### VS 对比、优缺点

1. Bootstrap Pricing：同维度方案对比：[固定源码](https://github.com/twbs/bootstrap/blob/c1f9b9db4dd14d5353e34462ec589cdf8c7270d3/site/src/assets/examples/pricing/index.astro) · [预览链接](https://getbootstrap.com/docs/5.3/examples/pricing/)
2. Flowbite Pricing card：一组重复的对象+属性：[固定源码](https://github.com/themesberg/flowbite/blob/232ebdb33a9e37b31b293b9988d89b862ee121e5/content/components/card.md) · [预览链接](https://flowbite.com/docs/components/card/)；源码段落：Pricing card

- 槽：title；objects[2–3].{name,icon}；criteria[3–4].{label,cells[],polarity}；takeaway；source
- 逐条出现：标题和两个对象名先到位；按口播一次揭示一条比较维度及双方单元格，避免先铺满一方造成误读。优缺点用 polarity 标记，不把颜色当唯一信息。结论最后独立出现。
- 9:16：2 个对象，列标题常驻；3 个成对比较行。3 对象改成同一维度连续卡，不把三列硬挤进窄画幅。
- 16:9：2–3 列对象，左侧窄维度列；最多 4 个维度。优缺点可左右两组，但对应同一题头。
- 容量（设计估计，非上游承诺）：题头 12–20 字；对象名 4–10 字；维度 4–8 字；每个格 8–14 字，最多 2 行；结论 18–28 字。
- 合同差量：R0 comparison-split 已有两项骨架；新合同要补多对象、共享 criteria、极性与结论，不再加卡面皮肤。

### 排行榜

1. daisyUI List：有序行、内容槽与末列：[固定源码](https://github.com/saadeghi/daisyui/blob/9adbeaa259816be46b98bf497a09cd2ab127e3cf/packages/docs/src/routes/%28routes%29/components/list/%2Bpage.md) · [预览链接](https://daisyui.com/components/list/)
2. Flowbite Table with users：名称+指标行：[固定源码](https://github.com/themesberg/flowbite/blob/232ebdb33a9e37b31b293b9988d89b862ee121e5/content/components/tables.md) · [预览链接](https://flowbite.com/docs/components/tables/)；源码段落：Table with users

- 槽：title；items[3–5].{rank,label,icon,value,unit,delta,note}；metricDefinition；source
- 逐条出现：先显示排名尺度与时间范围，再按 rank 的预定顺序揭示行；可倒序揭示 3→1 留悬念。行位提前预留，不因内容出现引发重排。排名随时间变化属于 C4，不混进静态排行。
- 9:16：竖排 3–5 行，前三名不强行做领奖台；名称左、值右；一行补充说明最多 1 行。
- 16:9：排行占左 60%，右 40% 放当前项的解释或 TOP1 结论；无需铺成 5 列。
- 容量（设计估计，非上游承诺）：标题 12–20 字；名称 4–12 字；数字 1–7 个 ASCII 字符；单位 1–4 字；单项说明 12–20 字；口径 16–28 字。
- 合同差量：R0 bar-chart-race 是数值排名变化的 B-roll；C1 只补有序内容+指标口径+定点讲解。

### 时间线、步骤流程

1. daisyUI Timeline：事件+节点+日期：[固定源码](https://github.com/saadeghi/daisyui/blob/9adbeaa259816be46b98bf497a09cd2ab127e3cf/packages/docs/src/routes/%28routes%29/components/timeline/%2Bpage.md) · [预览链接](https://daisyui.com/components/timeline/)
2. Flowbite Timeline：标题+日期+说明：[固定源码](https://github.com/themesberg/flowbite/blob/232ebdb33a9e37b31b293b9988d89b862ee121e5/content/components/timeline.md) · [预览链接](https://flowbite.com/docs/components/timeline/)；源码段落：Default timeline / Vertical timeline
3. daisyUI Steps：短流程：[固定源码](https://github.com/saadeghi/daisyui/blob/9adbeaa259816be46b98bf497a09cd2ab127e3cf/packages/docs/src/routes/%28routes%29/components/steps/%2Bpage.md) · [预览链接](https://daisyui.com/components/steps/)

- 槽：title；items[3–5].{date,step,title,body,icon}；connector；activeIndex；source
- 逐条出现：静态轴/节点先建立；按 cue 逐个显露节点正文并强调当前节点。连线只由 t 计算裁切进度；状态不能靠上一个节点回调累加。步骤结果可作为独立末项。
- 9:16：3–4 项纵向，日期窄列+正文宽列；节点全部放同一侧，避免左右交错浪费宽度。
- 16:9：3–5 项横向；长文退回纵轴居左、当前说明居右。日期无需重复成每个节点的标题。
- 容量（设计估计，非上游承诺）：节点标题 6–10 字；日期 4–12 字符；说明 16–24 字；步骤序号 1–2 位；全卡题头 12–20 字。
- 合同差量：R0 flowchart 可作图结构基线；补 date/step 双语义和密度策略，避免把网页无限长时间线直接搬进视频。

### 大数字：核心数据+说明

1. daisyUI Stat：指标名+大数值+说明：[固定源码](https://github.com/saadeghi/daisyui/blob/9adbeaa259816be46b98bf497a09cd2ab127e3cf/packages/docs/src/routes/%28routes%29/components/stat/%2Bpage.md) · [预览链接](https://daisyui.com/components/stat/)
2. Flowbite Statistic list：指标名+数值配对：[固定源码](https://github.com/themesberg/flowbite/blob/232ebdb33a9e37b31b293b9988d89b862ee121e5/content/components/list-group.md) · [预览链接](https://flowbite.com/docs/components/list-group/)；源码段落：Statistic list with divider

- 槽：title；metric.{label,value,unit,delta,period,definition}；explanation；source
- 逐条出现：先交代指标名、口径与期间；数值一次出现或由外部 t 驱动短计数，随后解释/比较基线出现。最终值和单位同时出现，不能让小数/单位晚到造成错误。
- 9:16：一个主指标居中，说明与来源下置；附指标最多 2 个小项，不堆 4 个仪表盘格。
- 16:9：主数字左约 40%，解释右约 60%；两个指标才做并列，层级仍有唯一主值。
- 容量（设计估计，非上游承诺）：数值 1–8 个 ASCII 字符；单位 1–4 字；指标名 6–12 字；期间/口径 12–20 字；说明 24–40 字。
- 合同差量：大数字须有 unit、period、definition、source；不能只接受一个任意字符串 value。

### 聊天对话、问答

1. daisyUI Chat：左右说话人+气泡：[固定源码](https://github.com/saadeghi/daisyui/blob/9adbeaa259816be46b98bf497a09cd2ab127e3cf/packages/docs/src/routes/%28routes%29/components/chat/%2Bpage.md) · [预览链接](https://daisyui.com/components/chat/)
2. Flowbite Chat Bubble：人名+时间+正文：[固定源码](https://github.com/themesberg/flowbite/blob/232ebdb33a9e37b31b293b9988d89b862ee121e5/content/components/chat-bubble.md) · [预览链接](https://flowbite.com/docs/components/chat-bubble/)；源码段落：Default chat bubble / Clean chat bubble

- 槽：title；participants[2].{name,avatar,side}；messages[2–4].{speaker,body,cue}；source；illustrative
- 逐条出现：跟随口播按 message/句子出现；问句完整保留到答句被理解。默认整句显露，不用真实等待/打字状态机。对话演绎必须标明，不能用真实头像制造当事人说过话的印象。
- 9:16：最多 3 个可读气泡同时在屏；两侧对齐但正文宽度至少占可用宽度 70%。超过容量换场，不能靠自动滚动藏证据。
- 16:9：可左右问答两区，或中部保留窄的聊天列，右侧放结论；同屏 4 气泡是上限估计。
- 容量（设计估计，非上游承诺）：人名 2–8 字；每气泡 18–36 字、2–3 行；问答总计约 60–90 字；时间戳可选，最多 5–10 字符。
- 合同差量：R0 chat-thread 已有基线；优先扩充 participants、message cue、问答摘要和演绎标记。

### 金句

1. Flowbite Blockquote：引语+出处：[固定源码](https://github.com/themesberg/flowbite/blob/232ebdb33a9e37b31b293b9988d89b862ee121e5/content/typography/blockquote.md) · [预览链接](https://flowbite.com/docs/typography/blockquote/)；源码段落：User testimonial / Alignment
2. Bootstrap Blockquote：正文+归属+作品名：[固定源码](https://github.com/twbs/bootstrap/blob/c1f9b9db4dd14d5353e34462ec589cdf8c7270d3/site/src/content/docs/content/typography.mdx) · [预览链接](https://getbootstrap.com/docs/5.3/content/typography/#blockquotes)；源码段落：Blockquotes / Naming a source

- 槽：quote；emphasisRanges；author；role；workTitle；source；contextNote
- 逐条出现：整段引语先成为可读对象，随后只强调口播中的短语；作者和出处不在末帧才出现。省略引用必须保留原意；不添加来源没说过的断言。
- 9:16：3–4 行主体，作者/作品置底，最多一个强调片段；避免每个字独立飞入。
- 16:9：2–3 行主体，左对齐或居中；出处为单独底部信息层；不以大引号装饰占走一半面积。
- 容量（设计估计，非上游承诺）：引语 28–60 字；作者 2–10 字；身份 8–16 字；作品名 8–20 字；上下文补注 16–24 字。
- 合同差量：结构重点是可核查 source 和 emphasisRanges；引用内容本身的版权/真实性与组件 MIT 无关。

### 证据截图框：一张图片+标注

1. daisyUI Browser mockup：工具栏+内容视口：[固定源码](https://github.com/saadeghi/daisyui/blob/9adbeaa259816be46b98bf497a09cd2ab127e3cf/packages/docs/src/routes/%28routes%29/components/mockup-browser/%2Bpage.md) · [预览链接](https://daisyui.com/components/mockup-browser/)
2. Flowbite Figure：图片+图片说明：[固定源码](https://github.com/themesberg/flowbite/blob/232ebdb33a9e37b31b293b9988d89b862ee121e5/content/typography/images.md) · [预览链接](https://flowbite.com/docs/typography/images/)；源码段落：Image caption

- 槽：title；image.{src,aspect,fit,crop,focalPoint}；callouts[1–3].{anchor,label,rect}；caption；source；redactions
- 逐条出现：先展示完整证据视口与来源，再随口播显示 1–3 个标注；需要放大时保留局部在原图中的定位。遮挡应先于首帧生效；标注/裁切坐标归一化以便换尺寸。
- 9:16：图片上 55–65%，下方说明；横截图使用可读局部+原图缩略定位，不强行缩小整页。
- 16:9：图左 60–70%，右侧注释；足够清晰时可全宽图+底部 caption。
- 容量（设计估计，非上游承诺）：题头 12–20 字；标注标签每条 6–12 字，最多 3 条；caption 18–30 字；出处为短名+链接元数据，不把长 URL 塞画面。
- 合同差量：daisyUI 框只提供视口；annotation、crop、redactions 是新合同槽。示例照片/头像不是已获许可截图资产。

### 清单打勾

1. Bootstrap List group：逐项状态+标签：[固定源码](https://github.com/twbs/bootstrap/blob/c1f9b9db4dd14d5353e34462ec589cdf8c7270d3/site/src/content/docs/components/list-group.mdx) · [预览链接](https://getbootstrap.com/docs/5.3/components/list-group/#checkboxes-and-radios)；源码段落：Checkboxes and radios
2. Flowbite Features list：勾号+功能项：[固定源码](https://github.com/themesberg/flowbite/blob/232ebdb33a9e37b31b293b9988d89b862ee121e5/content/typography/lists.md) · [预览链接](https://flowbite.com/docs/typography/lists/)；源码段落：List with icons / Features list card
3. daisyUI Checkbox：状态+标签：[固定源码](https://github.com/saadeghi/daisyui/blob/9adbeaa259816be46b98bf497a09cd2ab127e3cf/packages/docs/src/routes/%28routes%29/components/checkbox/%2Bpage.md) · [预览链接](https://daisyui.com/components/checkbox/)

- 槽：title；items[3–5].{label,detail,state,cue}；summary；source
- 逐条出现：按口播逐行出现后切换状态；state 至少 pending/done/failed，不仅布尔。打勾是 t 与 cue 的函数，不触发真实 DOM 点击；总进度由状态数组重算。
- 9:16：单列 3–5 条，勾位固定；有细说明时最多 3 条。
- 16:9：单列清单+右侧总结；仅在条目互不依赖且足够短时两列，阅读顺序明确。
- 容量（设计估计，非上游承诺）：每条标签 8–16 字；说明 12–20 字；标题 12–20 字；总结 18–28 字；不以缩小字号容纳第 6 条。
- 合同差量：R0 marker-checklist-card 已有；优先补状态/失败理由/总结，不重复制作相同骨架。

### 金字塔 / 层级、2×2 矩阵

1. Mermaid Flowchart：父子节点层级：[固定源码](https://github.com/mermaid-js/mermaid/blob/97b345154f2cd71f23a2aadb14af6dad46f63173/docs/syntax/flowchart.md) · [预览链接](https://mermaid.js.org/syntax/flowchart.html)；源码段落：Direction / Subgraphs
2. Mermaid Quadrant：二维轴+四象限：[固定源码](https://github.com/mermaid-js/mermaid/blob/97b345154f2cd71f23a2aadb14af6dad46f63173/docs/syntax/quadrantChart.md) · [预览链接](https://mermaid.js.org/syntax/quadrantChart.html)；源码段落：Example / Quadrants text / Points
3. ECharts Funnel/Pyramid：分层宽度：[固定源码](https://github.com/apache/echarts-examples/blob/88ca004030e999073a15303e5fe32462b8fefae2/public/examples/ts/funnel-align.ts) · [预览链接](https://raw.githubusercontent.com/apache/echarts-examples/88ca004030e999073a15303e5fe32462b8fefae2/public/data/thumb/funnel-align.png)；源码段落：Pyramid series sort: ascending

- 槽：层级：nodes.{id,parent,label,body,level}，最多 3–4 层；矩阵：axes[2].{label,low,high}，quadrants[4].{label,body}，points.{x,y,label}；两者共享 title/source
- 逐条出现：层级先显示整体轮廓，自上而下/自下而上逐层解释；2×2 必须先说明两条轴，再亮四个区域，最后放点。节点布局在挂载时冻结，揭示不能重新跑布局。
- 9:16：层级 3 层、每层 1–3 节点；矩阵采用顶部正方形，下方解释当前象限，避免拉成长矩形改变关系。
- 16:9：层级树横排 3 层；矩阵保持接近正方形，右侧放当前象限或点说明。
- 容量（设计估计，非上游承诺）：层名/节点 4–10 字；层级解释 12–20 字；轴名 4–8 字；轴端 2–5 字；象限名 4–8 字；象限正文 12–20 字；点名 2–6 字且最多 4 点。
- 合同差量：请拆为 hierarchy 与 matrix 两个合同而非任意 diagram 字符串；金字塔宽度若仅表层级必须注明非定量，不能误导成面积对应数值。

## 三项共用合同建议

1. 内容与样式分离：structureType + slots + itemCount + density；颜色/字体仍读取现有 theme token，不能用导入主题代替内容结构。
2. 确定性时间：每项保存绝对 cueStart/cueEnd。显隐、强调、勾选状态都由 t 直接求值；不要依赖滚动、鼠标、setTimeout、onComplete 或上次播放状态。先固定全卡布局再逐项显示；新 preset 需做顺播/跳转/倒拖同帧比较。
3. 证据字段：source、metricDefinition、period、illustrative、redactions 必须进入作品闭包；图片位置使用 0–1 归一坐标；超容量应换场/删减，不静默缩字或丢弃来源。

## 候选卡（字段与 candidates.jsonl 一致）

### C1-01 daisyUI 内容结构组件组

- lane / url：C1 · https://github.com/saadeghi/daisyui
- pinned_ref：`9adbeaa259816be46b98bf497a09cd2ab127e3cf`
- license：MIT；[LICENSE](https://github.com/saadeghi/daisyui/blob/9adbeaa259816be46b98bf497a09cd2ab127e3cf/LICENSE)；代码及仓库内说明；第三方图像/头像/品牌不随此许可自动授权
- obligations：署名=true / SA=false / NC=false / ND=false；布尔值描述复制/改作源材料时的义务；本路只作结构参考，不自动产生视频片尾署名义务。MIT 须随代码保留完整版权和许可文本。
- attribution_text：结构参考：daisyUI 内容结构组件组，Copyright (c) 2020 Pouya Saadeghi，MIT，https://github.com/saadeghi/daisyui，参考版本 9adbeaa259816be46b98bf497a09cd2ab127e3cf。本项目按内容结构重新设计，未导入源代码；若后续复制或修改，须如实更新此说明并保留完整许可。
- attribution_place：调查/资产包说明；复制代码时随包保留完整 LICENSE。纯结构参考无需机械地塞入每条视频片尾；复用 CC BY 文档/图像时在视频简介或片尾给可访问署名。
- risks：只作内容结构参考，不是新卡面风格；无运行时导入。；示例商标、人物头像、产品照片、引用和示例统计数字未获得本调查的内容授权；不纳入。；外站预览会漂移且未完成访问验证；以固定 GitHub 源码和 LICENSE 为准。
- content：7 个选中结构引用，源码与预览见上文；HTML/Markdown/MDX/TS；体积不适用（不入库）。
- maps_to：仅参考；product_lines：card / explainer / showcase
- adaptation：D；只参考内容槽与排布，后续由本地按 card-kit 合同自研；不导入代码。
- seekability：不适用（静态素材）；未来自研的逐项可见性必须按 t 求值。
- runtime：CSS 组件；文档站使用 Svelte/Tailwind，但这里只参考结构，不引入 React/Three.js。
- maintenance：2026-09-30T02:04:09Z（所选 HEAD，不是每个组件的修改时间）
- verdict：首推：最轻量的 HTML/CSS 插槽参考，跨横竖已有明确方向。

### C1-02 Flowbite 开源结构示例组

- lane / url：C1 · https://github.com/themesberg/flowbite
- pinned_ref：`232ebdb33a9e37b31b293b9988d89b862ee121e5`
- license：MIT (released code); CC-BY-3.0 (documentation and docs code)；[固定分许可页](https://github.com/themesberg/flowbite/blob/232ebdb33a9e37b31b293b9988d89b862ee121e5/content/getting-started/license.md)；[MIT发布代码许可](https://github.com/themesberg/flowbite/blob/232ebdb33a9e37b31b293b9988d89b862ee121e5/LICENSE.md)；本组选中8个参考全部位于content/，按Documentation/docs code的CC BY 3.0记录；发布代码另为MIT，不能用根MIT覆盖这些文档示例。第三方图像/头像/品牌另审。
- 文档与上游归属证据：[Documentation段](https://github.com/themesberg/flowbite/blob/232ebdb33a9e37b31b293b9988d89b862ee121e5/content/getting-started/license.md#documentation)明确包括docs code，并注明源自Bootstrap作者及Twitter Inc.；本组选中8个参考均在content/。
- obligations：署名=true / SA=false / NC=false / ND=false；选中的文档及文档代码为CC BY 3.0：复用时署名Flowbite/Bergside、保留已有Bootstrap作者/Twitter Inc.归属、附许可/来源链接并说明改动。发布代码另为MIT，复制须保留完整版权和许可文本。无SA/NC/ND。D级纯抽象结构启发不自动触发视频署名义务。
- attribution_text：结构参考：Flowbite，Themesberg / Bergside Inc.，参考版本 232ebdb33a9e37b31b293b9988d89b862ee121e5，https://github.com/themesberg/flowbite 。本项目只借鉴抽象内容结构，未复制文档或代码。若后续复用文档/示例代码，改用：Documentation / example code adapted from Flowbite by Themesberg (Bergside Inc.), CC BY 3.0 (https://creativecommons.org/licenses/by/3.0/). Originally forked from Bootstrap by the Bootstrap authors and Twitter Inc.; adapted by Flowbite. Source: https://github.com/themesberg/flowbite/blob/232ebdb33a9e37b31b293b9988d89b862ee121e5/content/getting-started/license.md. Changes: [如实填写所复制内容及改动]. 复制MIT发布代码时另保留完整MIT许可。
- attribution_place：调查/资产包说明；纯结构参考不自动要求每条视频署名。若复用CC BY文档、示例代码或截图，资产包保留完整来源/许可/上游归属；视频复用相关内容时在简介或片尾提供合理可访问的署名。
- risks：只作内容结构参考，不是新卡面风格；无运行时导入。；示例商标、人物头像、产品照片、引用和示例统计数字未获得本调查的内容授权；不纳入。；外站预览会漂移且未完成访问验证；以固定 GitHub 源码和 LICENSE 为准。；同一仓库分许可：content/文档及docs code为CC BY 3.0；不能只见根LICENSE.md的MIT就把全部示例当MIT。许可页要求保留Bootstrap作者及Twitter Inc.上游归属。
- content：8 个选中结构引用，源码与预览见上文；HTML/Markdown；体积不适用（不入库）。
- maps_to：仅参考；product_lines：card / explainer / showcase
- adaptation：D；只参考内容槽与排布，后续由本地按 card-kit 合同自研；不导入代码。
- seekability：不适用（静态素材）；未来自研的逐项可见性必须按t求值。
- runtime：HTML + Tailwind CSS；本组选中静态内容不需 Flowbite JS。不要把 CDN、示例外部图片和 Pro 模板带入闭包。
- maintenance：2026-06-27T08:36:07Z（所选HEAD，不是每个组件的修改时间）
- verdict：首推：聊天、列表、引用、图注的语义槽齐全；本组文档示例按CC BY 3.0处理，仅作结构参考。

### C1-03 Bootstrap Pricing / List group / Blockquote

- lane / url：C1 · https://github.com/twbs/bootstrap
- pinned_ref：`c1f9b9db4dd14d5353e34462ec589cdf8c7270d3`
- license：MIT (code); CC-BY-3.0 (documentation)；[LICENSE](https://github.com/twbs/bootstrap/blob/c1f9b9db4dd14d5353e34462ec589cdf8c7270d3/LICENSE)；代码及仓库内说明；第三方图像/头像/品牌不随此许可自动授权
- 文档单独授权证据：[固定 README](https://github.com/twbs/bootstrap/blob/c1f9b9db4dd14d5353e34462ec589cdf8c7270d3/README.md#copyright-and-license)；此项不把 CC BY 文档冒充 MIT。
- obligations：署名=true / SA=false / NC=false / ND=false；代码 MIT 须保留完整版权/许可；复用文档文字或截图另按 README 的 CC BY 3.0 署名并说明改动。仅抽象结构自研不等于复制文档。
- attribution_text：结构参考：Bootstrap Pricing / List group / Blockquote，Copyright (c) 2011-2026 The Bootstrap Authors，MIT (code); CC-BY-3.0 (documentation)，https://github.com/twbs/bootstrap，参考版本 c1f9b9db4dd14d5353e34462ec589cdf8c7270d3。本项目按内容结构重新设计，未导入源代码；若后续复制或修改，须如实更新此说明并保留完整许可。
- attribution_place：调查/资产包说明；复制代码时随包保留完整 LICENSE。纯结构参考无需机械地塞入每条视频片尾；复用 CC BY 文档/图像时在视频简介或片尾给可访问署名。
- risks：只作内容结构参考，不是新卡面风格；无运行时导入。；示例商标、人物头像、产品照片、引用和示例统计数字未获得本调查的内容授权；不纳入。；外站预览会漂移且未完成访问验证；以固定 GitHub 源码和 LICENSE 为准。
- content：3 个选中结构引用，源码与预览见上文；HTML/Markdown/MDX/TS；体积不适用（不入库）。
- maps_to：仅参考；product_lines：card / explainer / showcase
- adaptation：D；只参考内容槽与排布，后续由本地按 card-kit 合同自研；不导入代码。
- seekability：不适用（静态素材）；未来自研的逐项可见性必须按 t 求值。
- runtime：HTML/CSS；当前源码含 Astro 文档模板，不能把文档构建依赖当成成片依赖。不依赖 Three.js / React。
- maintenance：2026-10-01T11:22:44Z（所选 HEAD，不是每个组件的修改时间）
- verdict：备选：比较表、署名引用与清单语义简洁；留意代码与文档许可不同。

### C1-04 Mermaid 层级与 2×2 结构

- lane / url：C1 · https://github.com/mermaid-js/mermaid
- pinned_ref：`97b345154f2cd71f23a2aadb14af6dad46f63173`
- license：MIT；[LICENSE](https://github.com/mermaid-js/mermaid/blob/97b345154f2cd71f23a2aadb14af6dad46f63173/LICENSE)；代码及仓库内说明；第三方图像/头像/品牌不随此许可自动授权
- obligations：署名=true / SA=false / NC=false / ND=false；布尔值描述复制/改作源材料时的义务；本路只作结构参考，不自动产生视频片尾署名义务。MIT 须随代码保留完整版权和许可文本。
- attribution_text：结构参考：Mermaid 层级与 2×2 结构，Copyright (c) 2014 - 2022 Knut Sveidqvist，MIT，https://github.com/mermaid-js/mermaid，参考版本 97b345154f2cd71f23a2aadb14af6dad46f63173。本项目按内容结构重新设计，未导入源代码；若后续复制或修改，须如实更新此说明并保留完整许可。
- attribution_place：调查/资产包说明；复制代码时随包保留完整 LICENSE。纯结构参考无需机械地塞入每条视频片尾；复用 CC BY 文档/图像时在视频简介或片尾给可访问署名。
- risks：只作内容结构参考，不是新卡面风格；无运行时导入。；示例商标、人物头像、产品照片、引用和示例统计数字未获得本调查的内容授权；不纳入。；外站预览会漂移且未完成访问验证；以固定 GitHub 源码和 LICENSE 为准。
- content：2 个选中结构引用，源码与预览见上文；HTML/Markdown/MDX/TS；体积不适用（不入库）。
- maps_to：仅参考；product_lines：card / explainer / showcase
- adaptation：D；只参考内容槽与排布，后续由本地按 card-kit 合同自研；不导入代码。
- seekability：不适用（静态素材）；未来自研的逐项可见性必须按 t 求值。
- runtime：文档和 JS/SVG 图布局；不要求 Three.js/React。自动布局、字体测量/异步渲染不直接作为 seek 合同；C1 不导入运行时。
- maintenance：2026-10-02T12:41:41Z（所选 HEAD，不是每个组件的修改时间）
- verdict：首推：把层级、轴、象限、点的内容模型分清，适合据此自研固定预设。

### C1-05 ECharts Funnel/Pyramid 结构参考

- lane / url：C1 · https://github.com/apache/echarts-examples
- pinned_ref：`88ca004030e999073a15303e5fe32462b8fefae2`
- license：Apache-2.0；[LICENSE](https://github.com/apache/echarts-examples/blob/88ca004030e999073a15303e5fe32462b8fefae2/LICENSE)；代码及仓库内说明；第三方图像/头像/品牌不随此许可自动授权
- obligations：署名=true / SA=false / NC=false / ND=false；Apache-2.0：随分发保留 LICENSE、适用版权/归属；修改文件注明改动；如适用上游 NOTICE 须保留。该固定仓库顶层未发现 NOTICE。无 SA/NC/ND。
- attribution_text：结构参考：ECharts Funnel/Pyramid 结构参考，Apache Software Foundation and Apache ECharts contributors，Apache-2.0，https://github.com/apache/echarts-examples，参考版本 88ca004030e999073a15303e5fe32462b8fefae2。本项目按内容结构重新设计，未导入源代码；若后续复制或修改，须如实更新此说明并保留完整许可。
- attribution_place：调查/资产包说明；复制代码时随包保留完整 LICENSE。纯结构参考无需机械地塞入每条视频片尾；复用 CC BY 文档/图像时在视频简介或片尾给可访问署名。
- risks：只作内容结构参考，不是新卡面风格；无运行时导入。；示例商标、人物头像、产品照片、引用和示例统计数字未获得本调查的内容授权；不纳入。；外站预览会漂移且未完成访问验证；以固定 GitHub 源码和 LICENSE 为准。
- content：1 个选中结构引用，源码与预览见上文；HTML/Markdown/MDX/TS；体积不适用（不入库）。
- maps_to：仅参考；product_lines：card / explainer / showcase
- adaptation：D；只参考内容槽与排布，后续由本地按 card-kit 合同自研；不导入代码。
- seekability：不适用（静态素材）；未来自研的逐项可见性必须按 t 求值。
- runtime：示例是 ECharts option TypeScript；非 Three.js。参考静态排列，不引入 ECharts 默认动画；若日后直接用库，另按 C4 外部时间驱动评估。
- maintenance：2026-09-24T09:32:38Z（所选 HEAD，不是每个组件的修改时间）
- verdict：备选：同一数据的漏斗/金字塔与标签关系直观；视频中应缩减层数。

## 排除 / 不纳入本轮

- 不把 Flowbite Pro、付费主题或页面推荐的商业模板作为上述 MIT 候选的一部分；本轮只读该固定开源仓库。
- 不纳入示例中的人物头像、摄影、品牌 Logo、假设财务数字、现成引语正文。代码许可证不是这些内容的单独授权证明；换用用户有权使用的图片/事实，并另审肖像、商标和引用。
- 不把自动响应式网页等同于短视频横竖版验收；不采用网页滚动揭示/用户点击状态来满足 render(t)。
- 不新增代码导入包、截图文件或公开网站抓取物；本路所有候选均为 D 级结构参考。
