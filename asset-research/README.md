# HyperFrames 开源资产调查

调查日期：2026-10-02 UTC。范围为 card 内容结构、SVG、账号外观、简洁 B-roll、开场机制、中文 3D 标题、后期转场和音频。只调查，不导入、不制作新镜头。目录仅包含本次撰写的说明与索引，不含第三方源码、字体、图像、模型或音频本体。

## 结论与下一步选择

建议下一批先选三个原型：**中文立体标题、解析式粒子聚合、照片 2.5D 视差**。它们可围绕标题或图片插槽复用，且容易剥离自动时钟。网络点亮和银河也值得保留，但网络与现有 graph-grow 有重合，应先比较复用价值。此处是选型建议，不代表已获授权开始制作。

真正挤出、倒角的中文标题优先 **Three.js r160 TextGeometry + 合法字体子集**；平面可缩放字选 **troika**；可提前冻结标题的批量账号可考虑 **预生成 MSDF**。它们不是同一种效果的等价替代。CPU 小样中，8 个汉字子集 OTF 为 2,820 字节，typeface JSON 为 5,509 字节；无倒角 1,346 个三角形，倒角 2 段为 5,914 个。样本与方法见 O2，不能把小样体积推广到任意中文标题，也不等于 GPU 性能测试。

card 优先补“对比、排行、时间线、层级/矩阵”等**内容结构**，沿用已有外观，不再增加卡面皮肤。C1 的 21 个参考覆盖九类结构，全部仅作设计参考。

音频首推是**优先试听的来源**，不是听感质量排名。科技、lo-fi、轻快等有固定曲目；温暖、史诗和时长已验证的 2–5 秒音乐 sting 仍有缺口。音效可以补快门、reverse 和得分提示；笑声候选按 NC 隔离。

## 导航与每路首推

| 调查路 | 首推或优先路线 | 详细报告 |
|---|---|---|
| R0 官方基线 | comparison-split、bar-chart-race、constellation-hub、spiral-galaxy、particle-text-dissolve | [R0](lanes/R0-registry.md) |
| C1 卡片结构 | daisyUI、Flowbite、Mermaid；9 类结构、21 个具体引用 | [C1](lanes/C1-card-structures.md) |
| C2 SVG 内容 | Phosphor、Tabler、Twemoji、Fluent High Contrast | [C2](lanes/C2-svg-content.md) |
| C3 账号外观 | Noto Sans SC、Noto Serif SC、得意黑、Radix Colors、Open Props | [C3](lanes/C3-appearance.md) |
| C4 简洁 B-roll | D3 纯几何图表与排名、ProgressBar.set、Devices.css | [C4](lanes/C4-card-broll.md) |
| O1 开场机制 | 粒子聚合、冻结网络点亮、解析银河、照片视差、中文立体标题 | [O1](lanes/O1-opening-mechanisms.md) |
| O2 中文标题与 3D 素材 | TextGeometry、troika、MSDF、Source Han Sans、逐文件 CC0 的 Khronos 小道具 | [O2](lanes/O2-3d-assets-and-cjk-title.md) |
| O3 后期转场 | r160 原生 bloom、空间 shader、Bokeh、精选 GL Transitions | [O3](lanes/O3-post-and-transitions.md) |
| O4 机制参考 | 动态标题前移、文字片层回声、图片副本路径 | [O4](lanes/O4-references.md) |
| A1 BGM | DSP 科技/lo-fi/轻快曲目、Tanner 原作选集、Kenney jingle 筛选池 | [A1](lanes/A1-bgm.md) |
| A2 音效 | Kenney UI/Interface、DSP 快门/reverse/UI 与转场精选 | [A2](lanes/A2-sfx.md) |

## 不能忽略的证据

1. **Registry 不是 400 个即用资产。** 固定快照 `8aefd91bf82c687222082a80a3c5845ff37e6ca6` 有 394 项：164 blocks、222 components、8 examples；前两类合计 386。14 个 HTML 抽样均含 GSAP CDN，部分 Three.js 为 r147 或 r181.2，与目标 r160 不同。统计与固定源码链接见 R0。
2. **根许可证不能覆盖所有素材。** 官方音效是 19 个 MP3、17 个独立内容，采用单独的 Pixabay 条款；不能用根 Apache-2.0 推导原文件素材包再分发权。Flowbite 发布代码与文档代码的许可不同；部分后期 shader 也有独立署名来源。见 R0、C1、O3、A2。
3. **有开源代码不等于可 seek。** 粒子积分、力导向、物理迭代、弧线 ticker、双 portal 纹理递归都可能读历史帧。要改为绝对时间解析求值，或预计算并冻结采样结果。TAA、afterimage、累积运动模糊与反馈效果排除。见 O1、O3、C4。
4. **字体支持中文不等于已验证通规一级字。** C3 将作者覆盖声明、cmap 统计与未逐字验证分别记录。troika 必须显式封闭字体和 fallback 网络；字体子集需保留许可并处理 RFN。见 O2、C3。
5. **SVG 必须检查具体风格。** Fluent High Contrast 通过本次标签扫描；Color 含 filter，Flat 也有少数例外。Noto 有私有元素和旗帜目录问题。标签白名单通过不代表事件属性、外链与 ID 安全已完成验收。见 C2。
6. **中国边界相关地图未找到满足本计划证据门槛的候选。** 因缺标准地图合规及再利用依据，相关用途标不可用；不用“开源”“CorrectChinaMap”等名称替代审查。见 C4。

## 需要本地决定的合同缺口

- hook 允许 WebGL 正式标题且 DOM 文字层留空；这项例外不扩展到 concept 镜头
- 图标除了单枚 media 使用，新的 icon-set provider 仍需宿主支持
- card 内容结构需表达共享比较维度、排行口径、时间/步骤、矩阵位置与图片标注槽
- 字体闭包需记录字形集合、实际覆盖、RFN/子集名、字体及 worker/WASM/fallback 依赖
- 后期需冻结 pass 顺序、颜色空间、缓冲区格式、seed/frameIndex；转场输入纹理必须来自同一目标时间
- 署名、许可全文及修改记录要随素材闭包保存；音频来源/成片使用与原音轨再分发分别判断
- NC、SA、代码 copyleft、字体 OFL 与原文件再分发限制需分别可筛选，不能只保留一个“开源”标签

## 数量与覆盖

共 **108 条调查记录**（含排除与仅参考项），不是 108 个已验收资产或独立项目。R0 15、C1 5、C2 9、C3 11、C4 8、O1 13、O2 11、O3 8、O4 5、A1 14、A2 9。C1 覆盖九类结构、21 个引用；O1 覆盖十一种机制、28 个实现入口。

## 如何读候选索引

[candidates.jsonl](candidates.jsonl) 每行一个调查对象，包含固定版本、许可路径、四项义务、可粘贴署名、风险、素材规模、映射、适配、时间驱动、运行时、维护信息及结论。候选可以是单项、曲包或一组同机制实现；不是独立仓库计数，跨路同源会有交叉引用。

- A：格式和基本使用路径较近，仍需本地许可/视觉/听音验收；不等于已入库
- B：需要离线化、主题/插槽封装、时间函数重写或格式转换
- C：需要扩展当前资产或宿主合同
- D：只借鉴结构/机制，不接纳原代码或素材
- `seekability` 描述拟采用路线；原版限制与证据等级见同一记录及分路报告。静态文件为“不适用（静态素材）”
- `obligations.share_alike` 为 true 时必须读其范围说明：可能只约束字体软件、代码修改或特定音频改编，绝不自动等于全部成片必须同许可
- `attribution` 区分许可保留与成片署名；直接粘贴的短署名不能替代分发软件/字体时的完整许可
- 未知、未验证、未试听均保留为限制，不以 false、零或“可用”掩盖
- 固定提交/标签用于可重复调查；维护日期按记录中的范围解读，不把老 tag 日期等同项目停止维护

## 验证范围与未完成项

已完成：固定源文件和 LICENSE 审查、Registry manifest 盘点、代表源码时间驱动分析、SVG XML 标签扫描、部分字体元数据与子集/几何 CPU 实验、候选字段及交叉一致性检查。O2 有一张 HDRI 的解码检查，说明中标出其精确范围。

未完成：目标 Harness 的实际接入、GPU 性能基准、跨画幅视觉检查、随机 seek 像素验收、音频试听及 Content ID 保证。站外音库只作线索；原预览链接不代表本次已实际观看或下载。只研究公开资料，未使用登录、Cookie、私有作品或付费接口。

## 建议本地筛选顺序

1. 从三个开场原型中选定首批，按现有 B-roll brief 写明确标题/图像槽、事件和时长
2. 先做断网与随机 seek 小样，再决定美术扩展；保持 r160 单实例
3. card 选两种真正缺少的内容结构；SVG 先抽样接纳，不整库搬入
4. BGM/音效由本地试听，并检查响度、循环接点、首尾、来源许可与发布限制
5. 经用户验收后再下载改造、pack 和按 hash 接纳；本调查不替代该步骤
