# 前端审美与 Motion 资源备忘录

整理日期：2026-10-06  
用途：培养视觉判断，并为使用 Opus、Astra 编写 Three.js、前端交互和动画寻找可拆解的参考。本文是学习与选型索引，不是接入计划或完成兼容性验收的资产清单。

**先看 Emil Kowalski、Maxime Heckel、Codrops；先拆 OneElementScroll、Sonner 和 Maxime 的单篇视觉实验。** 它们分别帮助理解动效判断、交互细节和 3D 风格形成。之后再按需要看 Shader 库与完整 3D 网站，避免一开始陷入大型工程。

## 目录

- [X 创作者与作品入口](#x-创作者与作品入口)
- [值得真正拆解的 GitHub 仓库](#值得真正拆解的-github-仓库)
- [开源 Motion 资源底座](#开源-motion-资源底座)
- [需要单独看许可的资源](#需要单独看许可的资源)
- [动画与风格 Skills](#动画与风格-skills)
- [建议阅读顺序与拆解方法](#建议阅读顺序与拆解方法)
- [使用边界](#使用边界)

## X 创作者与作品入口

X 主要用于发现作品；系统学习优先看作者网站、文章、演示与源代码。以下账号身份依据官方交叉链接确认，未逐条核验最新 X 时间线，也不评价更新频率。

| 创作者 | 入口 | 重点学习什么 | 适合怎么用 |
|---|---|---|---|
| **Emil Kowalski** | [X](https://x.com/emilkowalski) · [Train your judgement](https://emilkowal.ski/ui/train-your-judgement) · [Agents with taste](https://emilkowal.ski/ui/agents-with-taste) | 节奏、缓动、细小位移、反馈、同一交互的优劣比较 | 首先训练“为什么这版更自然”，再让 AI 调参数；其 UI 经验不要直接当作所有 3D 镜头的规则 |
| **Maxime Heckel** | [X](https://x.com/MaximeHeckel) · [博客](https://blog.maximeheckel.com/) · [Moebius 风格后处理](https://blog.maximeheckel.com/posts/moebius-style-post-processing/) | Shader、后处理、光影、轮廓如何共同形成风格 | 适合 Three.js / React Three Fiber；把一篇文章拆成逐层叠加的视觉实验 |
| **Codrops** | [X](https://x.com/codrops) · [Demo Hub](https://tympanus.net/codrops/hub/) | 字体编排、滚动叙事、转场、图像与 WebGL 的组合 | 编辑团队而非单个博主；先选一个演示，研究视线和元素连续性 |
| **Yuri Artiukh / akella** | [X](https://x.com/akella) · [GitHub](https://github.com/akella) · [视频](https://www.youtube.com/@akella_) | 从参考效果到 Shader / WebGL 实现的过程 | 跟着拆问题与实验，不只复制最终 fragment shader |
| **Rauno Freiberg** | [X](https://x.com/raunofreiberg) · [Craft](https://rauno.me/craft) · [Interaction Design](https://rauno.me/craft/interaction-design) | 直接操控、空间连续性、响应、交互中的物理直觉 | 提升前端手感，检查拖拽、返回、中断等状态是否自然 |
| **Bruno Simon** | [X](https://x.com/bruno_simon) · [作品站](https://bruno-simon.com/) | 完整 3D 世界的导航、构图、交互和资源组织 | 在已有小实验基础上研究整站；不要把世界复杂度当成所有项目的目标 |
| **Jesper Vos** | [X](https://x.com/jesper_vos) · [作品](https://www.jespervos.com/projects) | 视觉概念、空间、材质、艺术方向的一致性 | 为风格讨论建立参考；作品公开不等于源代码或素材可直接复用 |

## 值得真正拆解的 GitHub 仓库

优先级表示与本备忘录学习目标的匹配度，不是项目质量排名。下面的“拆解问题”是阅读建议，未声称已完成这些项目的运行测试或全面代码审计。

### 第一批：范围小，容易看清设计因果

**1. [codrops/OneElementScroll](https://github.com/codrops/OneElementScroll)**  
[演示](https://tympanus.net/Development/OneElementScroll/) · [HTML](https://github.com/codrops/OneElementScroll/blob/main/index.html) · [JS](https://github.com/codrops/OneElementScroll/tree/main/js) · [CSS](https://github.com/codrops/OneElementScroll/tree/main/css)

- 看点：一个视觉主体跨版面持续存在，怎样通过位置、尺度和上下文变化完成叙事
- 拆解问题：HTML 的内容顺序与视觉顺序如何对应？什么由布局完成，什么由动画完成？滚动触发怎样保持主体身份？
- 可迁移模式：持续视觉锚点、跨场景连续变形；适合反复“切页”感过强的动画参考
- 边界：教学演示，不是通用生产框架；示例代码许可与 GSAP 引擎许可需分别看，[仓库 LICENSE](https://github.com/codrops/OneElementScroll/blob/main/LICENSE) 不覆盖所有依赖

**2. [emilkowalski/sonner](https://github.com/emilkowalski/sonner)**  
[演示](https://sonner.emilkowal.ski/) · [src](https://github.com/emilkowalski/sonner/tree/main/src) · [test](https://github.com/emilkowalski/sonner/tree/main/test) · [MIT](https://github.com/emilkowalski/sonner/blob/main/LICENSE.md)

- 看点：通知出现、堆叠、展开、滑走等很小的交互，如何形成统一手感
- 拆解问题：状态变化如何映射到位移和透明度？多个通知怎样排序？交互中断和移除如何处理？
- 可迁移模式：状态先行、动效服务反馈；适合学习克制和细节，不是 MG 视频素材库

**3. [MaximeHeckel/blog.maximeheckel.com](https://github.com/MaximeHeckel/blog.maximeheckel.com)**  
[文章内容](https://github.com/MaximeHeckel/blog.maximeheckel.com/tree/main/content) · [core](https://github.com/MaximeHeckel/blog.maximeheckel.com/tree/main/core) · [许可](https://github.com/MaximeHeckel/blog.maximeheckel.com/blob/main/LICENSE)

- 看点：将 Moebius 等风格拆成轮廓、颜色、明暗、纹理等可解释的步骤
- 阅读入口：先读对应文章，再从内容与组件目录追踪示例；无需先理解整套博客系统
- 拆解问题：关闭某一层后风格如何改变？材质自身与屏幕后处理分别承担什么？
- 可迁移模式：逐层构建风格，以及让 AI 给出可比较的消融版本
- 边界：**代码 MIT；文章与图像另有 CC BY-NC 许可**，不能把博客图片和文字随代码一起视为 MIT

### 第二批：形成可调的风格与清晰的版式

**4. [paper-design/shaders](https://github.com/paper-design/shaders)**  
[效果站](https://shaders.paper.design/) · [packages](https://github.com/paper-design/shaders/tree/main/packages) · [docs](https://github.com/paper-design/shaders/tree/main/docs) · [LICENSE](https://github.com/paper-design/shaders/blob/main/LICENSE) · [NOTICE](https://github.com/paper-design/shaders/blob/main/NOTICE)

- 看点：如何把一个 Shader 效果变成参数可调、可组合、具有默认视觉质量的模块
- 拆解问题：参数哪些控制风格、哪些影响性能？时间、尺寸与像素密度怎样进入效果？原生与 React 包如何分层？
- 可迁移模式：调色、纹理、噪声、背景动效的参数化，而不是每个镜头重新造一个 Shader
- 许可：当前核验版本为 **Apache-2.0**，不要沿用旧的 PolyForm 判断；使用时锁定版本并保留 NOTICE。0.0.x 接口仍应谨慎对待

**5. [satnaing/astro-paper](https://github.com/satnaing/astro-paper)**  
[演示](https://astro-paper.pages.dev/) · [src](https://github.com/satnaing/astro-paper/tree/main/src) · [MIT](https://github.com/satnaing/astro-paper/blob/main/LICENSE)

- 看点：没有大量动效时，字号、行宽、留白、链接层级、明暗主题是否仍然成立
- 拆解问题：标题和正文的层级关系是什么？长文与窄屏如何保持可读？哪些装饰其实可以删除？
- 可迁移模式：先让静态关键帧清楚，再增加动画；主要是排版对照，不是 Motion 底座

### 第三批：整体验证空间与工程组织

**6. [brunosimon/folio-2025](https://github.com/brunosimon/folio-2025)**  
[网站](https://bruno-simon.com/) · [sources](https://github.com/brunosimon/folio-2025/tree/main/sources) · [resources](https://github.com/brunosimon/folio-2025/tree/main/resources) · [说明](https://github.com/brunosimon/folio-2025/blob/main/readme.md) · [MIT](https://github.com/brunosimon/folio-2025/blob/main/license.md)

- 看点：整套交互世界如何把摄像机、导航、建模、加载与反馈组织成一种体验
- 拆解问题：用户如何知道下一步去哪里？视觉焦点如何跟随输入？Blender 资源如何进入前端？
- 可迁移模式：场景分区、可探索信息、模型到交互的制作链
- 边界：仓库含 Blender 资源；完整服务端未开源，部分功能依赖可选后端。适合专题拆解，不宜整仓照搬当轻量起点

## 开源 Motion 资源底座

这里的 Motion 包括通用动效、MG 编程动画和 3D 动画，**不只指 motion.dev**。底座提供运动和渲染能力；它们本身不会自动给出好的构图与叙事。

| 底座 | 适合解决什么 | 值得拆解的部分 | 许可与注意事项 |
|---|---|---|---|
| [Motion](https://github.com/motiondivision/motion) | React / JavaScript 前端交互、布局变化、手势 | 状态到动画的映射、弹簧、布局连续性；与 [官方 Skill](https://github.com/motiondivision/ai-kit/blob/main/plugins/motion/skills/motion/SKILL.md) 配合阅读 | 核心 MIT；Motion+ 付费资源不自动包含在 MIT 内 |
| [Anime.js](https://github.com/juliangarnier/anime) | 原生 JavaScript 的 DOM / SVG 动画和时间线 | 多目标编排、时间线位置、SVG 路径与形变 | MIT；优先按 v4 文档，避免混用 v3 API |
| [Motion Canvas](https://github.com/motion-canvas/motion-canvas) · [examples](https://github.com/motion-canvas/examples) | TypeScript 驱动的讲解动画、图解与音频同步 | 场景生成器、信号、时间编排，以及对象如何跟随讲解变化 | 两仓库 MIT；适合研究 explainer，不能假定能直接嵌入现有 HTML 视频宿主 |
| [Three.js](https://github.com/mrdoob/three.js) · [示例](https://threejs.org/examples/) | 3D 场景、材质、摄像机、Shader | 先拆一个模型 / 一个光照 / 一段相机运动；再研究后处理 | 引擎代码 MIT；示例模型、纹理、字体逐项看来源与许可 |
| [Paper Shaders](https://github.com/paper-design/shaders) | 风格化背景、材质感与参数化视觉效果 | Shader 参数 API、原生与 React 封装、分辨率适配 | Apache-2.0；保留 NOTICE，并固定版本 |
| [Magic UI](https://github.com/magicuidesign/magicui) | 可复制的 React 动效组件与产品展示界面 | 从单个组件研究进入、强调、层次和交互；不要照搬整个营销页 | MIT；组件集合，不是通用视频叙事系统 |
| [Lottie Web](https://github.com/airbnb/lottie-web) | 播放设计工具导出的矢量动画 | 播放器控制、分段、进度与宿主时间轴映射 | 运行时 MIT；LottieFiles 动画文件可能适用另外的 Simple License 或作者条款 |
| [Rive Web runtime](https://github.com/rive-app/rive-wasm) | 状态机驱动、可交互的矢量角色和 UI | 输入、状态机、交互状态与动画状态如何对应 | 运行时 MIT；编辑器、平台服务及 .riv 素材不因此获得同样授权 |
| [Theatre.js](https://github.com/theatre-js/theatre) | 代码对象与可视化时间线配合 | 可编辑参数、轨道与运行时状态的分离 | Core 为 Apache-2.0；Studio 为 AGPL-3.0，不能按整仓宽松许可处理 |

**按目标选入口：**

- 前端交互与手感：Motion / Anime.js → Sonner
- Three.js 艺术方向：Maxime → Paper Shaders → Three.js 单例 → Bruno 整站
- MG 图解与讲解节奏：Motion Canvas 的单场景示例
- 可交互角色：Rive；线性矢量片段：Lottie。两者先确认素材来源与宿主时间控制能力

## 需要单独看许可的资源

这些项目可以有学习价值，但不能混入“全部宽松开源、随意打包复用”的清单。

| 资源 | 学习价值 | 关键边界 |
|---|---|---|
| [GSAP](https://github.com/greensock/GSAP) · [许可](https://gsap.com/community/standard-license/) | 成熟的时间线、SVG / DOM 编排与复杂交互 | 引擎使用自定义 No Charge License；免费使用不等于严格开源。官方 gsap-skills 的 MIT 不会改变引擎许可 |
| [Remotion](https://github.com/remotion-dev/remotion) · [LICENSE](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md) | React、逐帧求值、参数化视频、组件复用 | 引擎为自定义许可，商业 / 团队使用应按当时条款确认；不可仅因源代码公开就当作 MIT |
| [React Bits](https://github.com/DavidHDev/react-bits) | 文本、背景、组件视觉效果的参考库 | 当前 LICENSE.md 为 MIT + Commons Clause，属于有限制的源码可见资源，不标为纯 MIT |
| [motion-graphics-skills](https://github.com/imMamdouhaboammar/motion-graphics-skills) | 可知悉其目录思路 | README 宣称 53 个 Skills，但核验时 LICENSE 是 proprietary / All Rights Reserved，并限制复制、修改与生产使用；**不纳入可采用的开源 Skill 包** |

以上是检索时的许可分类提示，不代替最终分发或商业使用前对固定版本的许可核对。

## 动画与风格 Skills

Skill 是给 Agent 的工作方法、规则和示例，不能等同于动画引擎，也不能保证某个模型必然获得更高审美。以下以源码和文档核验为依据，未安装、未实跑，也没有对 Opus / Astra 的质量提升作对照实验。

### 优先阅读：从风格拆解到检查画面

| Skill 或项目 | 真正值得看的内容 | 适用与限制 |
|---|---|---|
| [opus-video-skills](https://github.com/tuzhechen2005/opus-video-skills) | painted-animation：分镜、关键姿态、关键帧拼图（contact sheet）与裁切检查；kinetic-reel：字体、粒子 / 液态 / 金属形态与 cue 时间线 | MIT。前者偏 p5.js / p5.brush 水彩角色表演，默认无文字、无 3D，水彩渲染可能较慢；后者包含 Canvas 2D 字体和 Three.js 效果。按目标选一个，不把两套默认风格混合 |
| [ClaudeAnimationBase](https://github.com/JohnHeibel/ClaudeAnimationBase) | ANIMATION_GUIDE.md、src/clawd.js 的角色表情 / 姿态，以及确定性渲染思路 | MIT；适合研究角色表演如何参数化，是动画基础参考而非万能风格库 |
| [reelmimic](https://github.com/edenfunf/reelmimic) | .claude/skills/video-clone/SKILL.md；从参考片拆节奏、颜色、镜头，再进入风格登记、分镜批准、关键姿态检查；docs/extending 的扩展方式 | 自有代码 MIT，第三方内容看 THIRD_PARTY_NOTICES.md。以 2D 为主；纸剪、蜡笔、像素、白板、赛璐璐等较新路线成熟度不一。默认并行较多，不建议不审查就整套接管工作流 |
| [LottieFiles/motion-design-skill](https://github.com/LottieFiles/motion-design-skill) | skills/motion-design/SKILL.md、director/motion-personality.md：情绪、主角、属性、时长、缓动、层级与编排 | MIT；以 Playful / Premium / Corporate / Energetic 等数值化风格规则建立语言，偏 UI 动效，不能替代完整影片叙事 |
| [emilkowalski/skills](https://github.com/emilkowalski/skills) | animate、review-animations、improve-animations、animation-vocabulary、apple-design | MIT；关注使用频率、目的、缓动和可中断性。适合审查前端动效，不把 UI 时长经验硬套到长镜头 |

**补充风格入口：**

- [apple-style-motion-skill](https://github.com/fiston-user/apple-style-motion-skill)：MIT，小型较新项目；从点到搜索框再到卡片的形态连续性、玻璃 UI 与弹簧。包含自有确定性 Motion 引擎，**不是 motion.dev**，适合限定的 Apple-like 产品演示
- [Impeccable](https://github.com/pbakaus/impeccable)：Apache-2.0；看艺术方向、构建、检查与 critique 的闭环，以及 animate / new-work 参考。包含启动器、hooks、二进制等，不应作为“只有一份 Markdown”盲装
- [Anthropic frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design)：该 Skill 自带 Apache-2.0 LICENSE.txt；从题材、受众与文化线索建立视觉方向。可与 Impeccable **择一作为主规则**，减少冲突
- [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)：MIT；可检索风格、色彩、字体和动效预设，适合作为词汇参考，不能当作影片导演
- [3dviz-pro-max](https://github.com/viettranx/3dviz-pro-max)：实验性；自有代码 / 数据 MIT，风格档案把相机、灯光、材质与运动参数化，docs/prompt-gallery.md 可作阅读入口。第三方字体、素材和宣传示例单独核验，没有已证实的模型审美提升结论

### 执行层 Skills：跟具体技术栈对应

- [HyperFrames 官方 Skills](https://github.com/heygen-com/hyperframes/tree/main/skills)：Apache-2.0；重点看 hyperframes-animation、规则索引、Three.js adapter，以及确定性 seek、AnimationMixer.setTime、粒子与形状的时间求值
- [GSAP 官方 Skills](https://github.com/greensock/gsap-skills)：Skill 为 MIT；重点看 gsap-core 的生命周期、immediateRender、stagger、matchMedia 与性能。再次注意引擎另有许可
- [Motion 官方 AI Kit](https://github.com/motiondivision/ai-kit)：Skill / 安装器 MIT；把离线最佳实践、在线文档 MCP、Motion+ 付费功能区分开
- [Remotion Skills](https://github.com/remotion-dev/skills)：可阅读 remotion-best-practices 的逐帧规则和 React 视频 API；核验时根目录未找到明确 LICENSE，**不要声称此 Skill 仓库为 MIT，也不要默认可再分发**
- [Magic UI](https://github.com/magicuidesign/magicui)：MIT；skills/magic-ui/SKILL.md 用于组件发现与组合，仍需由人判断是否适合当前画面

**建议搭配：一份风格规则 + 一份执行规则。** 例如纸剪角色路线先研究 reelmimic 的风格扩展，执行时只选实际采用的渲染栈；前端界面可选 Emil / frontend-design，再配 Motion。不要把所有 Skill 同时装入上下文，互相冲突的默认值会使结果更难判断。

## 建议阅读顺序与拆解方法

这是一条阅读路径，不代表已经决定迁移技术栈或安排实施：

1. **先练判断**：Emil 的 A/B 判断练习、Rauno 的交互文章；描述差异时使用构图、层级、节奏、缓动和连续性等具体词
2. **再拆小作品**：OneElementScroll → Sonner。每次只追踪一个视觉主体或一次状态变化
3. **形成一个 3D 风格**：Maxime 的单篇实验 → Paper Shaders 的参数。问清每层效果对结果的贡献
4. **按题材读技能**：角色表演看 opus-video-skills / reelmimic，UI 看 Emil / LottieFiles；再选对应执行 Skill
5. **最后研究整站**：Bruno 的资源与场景组织。需要讲解动画时补读 Motion Canvas，不必为了收藏而学习所有引擎

每次值得留下的拆解记录只有五项：

- 第一眼看什么，视觉主角为何成立
- 静止时的布局、色彩与层级是否清楚
- 动画改变了什么信息，何时开始、何时停
- 去掉哪一层就失去风格，哪些只是装饰
- 可以抽出什么参数与规则；哪些依赖题材，不宜做成通用模板

给 Agent 的比较任务可以这样写：

> 保持同一内容、镜头和构图，只改变一个动效变量，给出 A / B 两版。说明它改变了观众的注意力、阅读时间或连续性；保留可定位的关键帧，让我先判断哪版更好。不要只解释用了什么库。

## 使用边界

- 本文汇总 2026-10-05 至 2026-10-06 的资料与源码阅读；“推荐”是针对学习目标的判断，维护状态、路径和许可可能变化
- 当前没有完成这些项目在本仓库中的依赖、离线运行、随机种子、绝对时间 seek、宽高比或渲染质量验收
- 引擎、Skill、模板、图片、模型、字体、音频是不同许可对象。根 LICENSE 不能自动覆盖所有下载素材、第三方文件或在线服务
- 前端实时效果进入视频时间轴时，应另测倒放 / 跳转、确定性、历史缓冲、帧率、外部网络和版本兼容；示例“能播放”不等于“可稳定逐帧渲染”
- 学习公开作品的原则和技术，不搬运作者身份、品牌、受限图片与整套视觉资产。具体复用前保存来源、固定版本及对应许可
- 本次仅整理文档和链接，不下载或引入上述第三方代码、媒体、字体或 Skills

