# R0：HyperFrames 官方 Registry 基线

调查日期：2026-10-02 UTC。只读 GitHub 公开源码/树/提交元数据；未登录网站、未安装依赖、未执行外部音频服务、未下载媒体、未导入资产、未提交第三方文件。下列候选是本路15张调查卡，不是15个已验收资产。

## 1. 结论先行

- Registry 实数为 **394**：**164 blocks + 222 components + 8 examples**；常用 add 路径覆盖前两种，共 **386**。约400的量级接近，但不是400个可直接add的资产。已逐一读取394份 registry-item.json，无读取缺项。
- 冻结 commit：[`8aefd91bf82c687222082a80a3c5845ff37e6ca6`](https://github.com/heygen-com/hyperframes/commit/8aefd91bf82c687222082a80a3c5845ff37e6ca6)，提交时间 **2026-10-02T12:48:06Z**；[Registry清单](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/registry.json) blob为c8c99b164062b0ff97db1e8796f814efe2e946d0。后续 main 变动不改变本报告口径。
- 五个首推调查路线：comparison-split（内容结构参考）、bar-chart-race（纯t数据动画）、constellation-hub（口播节点）、spiral-galaxy（解析式星空）、particle-text-dissolve（低成本粒子字）。没有标A直接用：离线依赖、宿主合同和随机seek验收还未完成。
- 原有导入路径并不保证用户合同：抽查的14个HTML均引用GSAP CDN；Three开场有r147与r181.2，不能直接放入已固定r160的同一实例。
- 官方音效基线是 **19个MP3/17个独立blob**，不是文档声称的21。音频采用单独的Pixabay条款，根Apache不能覆盖它；原MP3再分发资产包授权尚未闭合。
- 没发现可把Registry当作已完备公开BGM曲库的证据。音频文档主要指向凭证检索或生成流程；本调查未调用。

## 2. 方法与证据等级

1. 读取完整registry.json与394份manifest，按GitHub递归树核文件体积与是否存在。
2. 对14个代表条目读HTML源码；对两个3D标题另读随包说明与字体/Three许可证；没有运行它们。
3. 各候选maintenance是候选目录在冻结commit可追溯的最后提交日期，不把仓库最后提交当成每个素材最后更新。
4. “纯函数/可烘焙”是源码可实现的技术路线；含onUpdate/call的样例必须在适配后通过随机seek测试才可接纳。跨GPU、字体栅格化、浏览器版本的像素一致性未证明。
5. 预览链接来自上游manifest或仓库demo路径，未下载/重托管媒体；有些新条目没有poster/video字段，不能虚构预览图片。

## 3. 分类基线：防止后续重复调查

下面是内容语义分组，可交叉，不将这些数相加。card不是官方独立分类；仅按tag“card”计数会严重漏检。

| 相关内容 | 现有条目与缺口 |
|---|---|
| VS/前后对比 | comparison-split、before-after-wipe；前者方向与split可配置。它们不是多产品功能对比表。 |
| 排行/数字/图表 | bar-chart-race、animated-bar-chart、chart-story、data-chart、decline-chart、count-up、number-wheel、number-pop-in、conic-progress-ring、mk-progress-stat。 |
| 时间线/步骤/层级 | flowchart、flowchart-vertical、onboarding-stepper-flow、hw-pipeline、constellation-hub；真正的时间线卡/金字塔/2×2矩阵仍需C1补参考。 |
| 聊天/问答 | ai-chat-reveal、message-thread-reveal、thread-message-stack、chat-thread、chat-message、chatgpt-exchange、claude-exchange；品牌外壳剥离，保留消息流结构。 |
| 金句/证据/清单 | testimonial-card、testimonial-proof-card、social-proof-card、vox-annotate、marker-checklist-card、mk-specs-list；不要把风格变体当内容结构。 |
| 截图样机 | device-frame-stage、browser-device-stage、multi-device-splay、screen-flow-carousel、sticky-mock-swap；vfx-iphone-device 等3D/实验浏览器路线另核。 |
| 标题/开场 | particle-text-dissolve、particle-image-reveal、spiral-galaxy、constellation-hub、wireframe-portal-title、glass-shard-title、code-particle-assemble、gallery-tunnel、cosmic-orb、three-orbiting-cards。 |
| 转场/后期 | sdf-iris、ridged-burn、domain-warp-dissolve、swirl-vortex、chromatic-radial-split、ordered-dither-pass、grid-pixelate-wipe、halftone-dissolve，以及13个 transitions-* 演示block。效果名相近不意味着无状态或可直接复用。 |

### 可复算的精确tag计数

依据冻结版本394份manifest的tags精确匹配；不是各路合格候选数。

| tag | 条目数 | 含义/限制 |
|---|---:|---|
| transition | 49 | 名称见下列清单；标签可能重叠 |
| transition-primitive | 19 | 名称见下列清单；标签可能重叠 |
| title-card | 13 | 名称见下列清单；标签可能重叠 |
| webgl | 14 | 名称见下列清单；标签可能重叠 |
| three-d-motion | 7 | 名称见下列清单；标签可能重叠 |
| data | 15 | 名称见下列清单；标签可能重叠 |
| sfx | 4 | 名称见下列清单；标签可能重叠 |
| music | 1 | 名称见下列清单；标签可能重叠 |

- **transition**：beat-freeze-cut、cinematic-zoom、chromatic-radial-split、code-slice-hero、cross-warp-morph、editorial-flash-overlay、flash-through-white、domain-warp-dissolve、glitch、gravitational-lens、hw-scribble-transition、light-leak、mk-clone-wall-transition、sdf-iris、ripple-waves、organic-light-leak-overlay、ridged-burn、transitions-destruction、swirl-vortex、transitions-3d、transitions-blur、thermal-distortion、transitions-cover、transitions-light、transitions-distortion、transitions-dissolve、transitions-grid、transitions-other、transitions-scale、transitions-mechanical、transitions-push、transitions-radial、whip-pan、cut-the-curve、fade-through、halftone-dissolve、grid-pixelate-wipe、iris-reveal、match-cut、micro-transitions、morph-swap、ordered-dither-pass、parallax-device-dive、parallax-zoom、parallax-unzoom、rubber-band-bumper、text-match-cut、type-match-cut、whip-pan-cut
- **transition-primitive**：avatar-group-hover、badge-pop、chromatic-aberration-wipe、card-resize、directional-wipe、icon-swap、input-feedback、menu-morph、micro-transitions、number-pop-in、page-slide、panel-reveal、skeleton-reveal、success-check、tabs-slide-indicator、text-state-swap、text-stagger、tilt-card、zoom-through-transition
- **title-card**：canopy-part-title、carousel-text-circle-3、carousel-text-circle-1、carousel-text-circle-4、carousel-text-circle-5、carousel-text-circle-2、glass-shard-title、hw-write-title、hw-title、wireframe-portal-title、yt-prism-title、titlecard-lockup、titlecard-calm
- **webgl**：code-3d-extrude、code-particle-assemble、code-shader-dissolve、cosmic-orb、gallery-tunnel、halftone-field、spiral-galaxy、rack-focus、vfx-liquid-glass、vfx-liquid-background、vfx-shatter、vfx-portal、vfx-magnetic、three-orbiting-cards
- **three-d-motion**：canopy-part-title、code-slice-hero、glass-shard-title、cuboid-carousel、frost-sequence-camera-orbit、orbit-card、wireframe-portal-title
- **data**：bar-chart-race、data-chart、oscilloscope-trace、spain-map、us-map-bubble、us-map、us-map-flow、us-map-hex、world-map、animated-bar-chart、conic-progress-ring、decline-chart、logo-wall、number-wheel、star-rating-fill
- **sfx**：blue-sweater-intro-video、apple-money-count、nyc-paris-flight、vpn-youtube-spot
- **music**：beat-freeze-cut

音效tag的4项是带音效的完整广告/旅行演示，不是独立音效包。music标签唯一的beat-freeze-cut也不是一条可授权BGM曲目。

## 4. 许可基线和排除门槛

- [根LICENSE](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/LICENSE)：Apache-2.0，2026 HeyGen, Inc.。分发代码/改造包时保留许可、版权及适用NOTICE，明确标修改；商标权不随许可转让。不是所有视频都必须片尾署名。
- 第三方依赖、字体、HDR、贴图、音频分别核证。Geist与Cormorant随包OFL证明只覆盖相应字体；Three随包MIT不覆盖HDR/matcap。
- marker-checklist-card带Permanent Marker/Courier Prime WOFF2，HTML头分别声明Apache-2.0/OFL-1.1，但该目录没有完整字体许可证文件：本次只推荐其清单结构，不接收随包字体。
- world-map使用world-atlas@2/countries-110m.json，未给出中国标准地图/审图证明：涉及中国边界的任务按计划标不可用，不以裁剪/视觉弱化代替合规来源。
- vfx-portal读取实验性Canvas drawElementImage；不接受为标准离线r160即用资产。机制参考仍有价值。
- 品牌演示（ChatGPT/Claude/Slack/Spotify/Apple等）不因代码开源而获得Logo/商标许可；只借结构或换成用户有权使用的内容。

## 5. 音效实盘

来源：[manifest](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/skills/media-use/audio/assets/sfx/manifest.json)、[CREDITS](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/skills/media-use/audio/assets/sfx/CREDITS.md)、[说明中的21-file声明](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/skills/media-use/audio/references/sfx.md)。

- 19个路径合计1,300,487 bytes（约1.24 MiB）；同blob去重17份内容
- click与click-soft同一blob；whoosh与whoosh-short同一blob，因此“软/脆”的描述并不证明声音不同
- 时长均是manifest元数据，未解码/试听测量；MP3实际音频长度、编码延迟、响度和真峰值仍需本地核验

| 文件 | 秒 | bytes | 类别 |
|---|---:|---:|---|
| chime.mp3 | 2.5 | 27309 | UI/提示 |
| click-soft.mp3 | 0.37 | 11702 | UI/提示 |
| click.mp3 | 0.37 | 11702 | UI/提示 |
| error.mp3 | 1.62 | 51827 | 综艺/错误反馈 |
| glitch-1.mp3 | 2.64 | 84427 | 开场/数字干扰 |
| glitch-2.mp3 | 3.5 | 112128 | 开场/数字干扰 |
| glitch-3.mp3 | 3.1 | 99072 | 开场/数字干扰 |
| impact-bass-1.mp3 | 2.12 | 67709 | 开场/低频冲击 |
| impact-bass-2.mp3 | 2.59 | 82944 | 开场/低频冲击 |
| key-press.mp3 | 0.4 | 3909 | UI/提示 |
| notification.mp3 | 2.46 | 78576 | UI/提示 |
| ping.mp3 | 1.32 | 26400 | UI/提示 |
| pop.mp3 | 0.72 | 23040 | UI/提示 |
| riser.mp3 | 10.03 | 321024 | 转场 |
| sparkle.mp3 | 1.8 | 57678 | UI/提示 |
| typing.mp3 | 1.5 | 26852 | UI/提示 |
| whoosh-cinematic.mp3 | 5.54 | 177408 | 转场 |
| whoosh-short.mp3 | 0.57 | 18390 | 转场 |
| whoosh.mp3 | 0.57 | 18390 | 转场 |

优先补缺：快门、明确reverse、笑声、明确得分音/数字播报音，以及2–5秒短sting/短riser。现有riser是10.03秒，不能当作2–5秒片头已覆盖。

CREDITS宣称允许商用/非商用、修改、无强制署名，且可随视频等衍生作品分发；未提供逐音效作者/原始页面或原始音频再分发的完整授权链。按照本次“冻结资产包”的目标，暂排除入库；这不等于断言它不可用于合法视频。

仓库另外有apple-money-count、blue-sweater-intro-video、nyc-paris-flight、vpn-youtube-spot的4份WAV混音，分别960,044 / 2,304,078 / 1,152,044 / 1,344,044 bytes。它们是完整场景混音，未证明逐声源许可，不优先拿来拆声音。测试tone/silence不算资产。bgm.mp3的少数路径在树中仅132B，未读取其正文或媒体对象，不能据文件名认定有公开可用曲目。

## 6. 对用户合同的影响

1. **统一时间桥**：现有用户render(t)应同时处理DOM tween与Canvas/WebGL绘制；不能只注册paused timeline就宣称seek安全。spiral-galaxy与bar-chart-race用setter；particle-text-dissolve等依赖eventful seek；两款3D标题有hf-seek桥。应统一显式render(t)并停用内部自由时钟。
2. **音效脱离回调**：device-frame-stage的hf:sfx由tl.call触发。导出时改为独立绝对时间音轨，拖动不触发额外声音。
3. **参数源不一致**：wireframe-portal-title、glass-shard-title的manifest没variables，但HTML及随包说明分别有9/19个参数。接口卡生成不能只读manifest；还需对照data-composition-variables。
4. **字体ready与初始化**：中文SDF/几何体、Canvas文字粒子、DOM捕获均先等本地字体，固定seed/布局再渲染。Geist的拉丁示例不是中文适用证据。
5. **版本与离线闭包**：r147和r181.2组件不能带第二份Three直接与r160混用；先移植到r160及匹配addons、固定GSAP依赖和许可证，并替换CDN/font URL。未实测兼容不能标“支持r160”。
6. **时长/画幅**：多个演示为8–15秒/1920×1080，需重新分配2–6秒hook节奏和9:16重排，不能只是整体缩放/加速。
7. **后期无状态**：SDF、解析式粒子、当前帧滤镜可行；不得由名称推断反馈/afterimage安全。新镜头接纳前逐个pass审查。

## 7. 15张候选卡

字段与candidates.jsonl一致。SA布尔对OFL字体作保守标记，义务仅作用于字体本体，不等于视频需要相同方式共享。首推是优先验证路线，不是批准入库。

### R0-01 comparison-split

- **lane / url / pinned_ref**：R0；[源清单](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/comparison-split/registry-item.json)；`8aefd91bf82c687222082a80a3c5845ff37e6ca6`
- **license**：Apache-2.0；[LICENSE](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/LICENSE)；HyperFrames自有代码；CDN依赖/字体/图像/音频另核，不自动继承根许可
- **obligations**：attribution=true；share_alike=false；non_commercial=false；no_derivatives=false。Apache代码分发保留许可/版权/相关NOTICE并标修改；不要求所有视频片尾署名。CDN依赖须另核许可。
- **attribution_text**：本作品的comparison-split实现参考自 HeyGen, Inc. 与 HyperFrames contributors，Apache-2.0，https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/comparison-split/。本次仅调查，未改动或导入原文件；实际采用时在此列明已做修改。
- **attribution_place**：资产包说明保留完整许可与修改记录；视频简介可列实现来源，不以简介替代软件/字体分发义务
- **risks**：不是多项 VS 表；默认是 before/after 全屏图片或面板；card 需按内容结构重做，不导入新卡面
- **content**：hyperframes:component；1个列出文件；已知合计16869B（仓库树中文件字节相加；不含CDN依赖和缺失远程资产）；槽：labelA、labelB、split、orientation；双端点 fromTo 明确初始化。9:16 建议上下对比，16:9 左右；不是自动排版保证。
- **preview**：[source_demo](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/comparison-split/demo.html)
- **maps_to / product_lines**：仅参考（C1 对比内容结构）、motion；card / explainer / showcase
- **adaptation**：D 仅参考：作为两屏对比结构参考重做 card 预设；若复用动效则 B，抽出 split/标签/方向并主题化、离线化
- **seekability**：纯函数。静态源码审查；尚未运行顺播/随机跳转/倒拖像素验收。分类描述改造路线；当前GSAP事件语义见adaptation。
- **runtime**：vanilla DOM/CSS + GSAP 3.14.2 CDN；无 Three/React/WASM/Worker；离线前改宿主本地依赖
- **maintenance**：[目录最后提交 2026-08-10T22:46:03Z](https://github.com/heygen-com/hyperframes/commit/9734578e6065d6dec8993c4e30a978263c3eaa8b)
- **verdict**：首推：已有方向与分割位置参数，DOM 双端点 tween，低成本补对比结构
- **evidence**：[源码1](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/comparison-split/comparison-split.html)；[源码2](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/comparison-split/registry-item.json)

### R0-02 marker-checklist-card

- **lane / url / pinned_ref**：R0；[源清单](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/marker-checklist-card/registry-item.json)；`8aefd91bf82c687222082a80a3c5845ff37e6ca6`
- **license**：Apache-2.0；[LICENSE](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/LICENSE)；HyperFrames自有代码；CDN依赖/字体/图像/音频另核，不自动继承根许可；附加许可：HTML头声明Permanent Marker为Apache-2.0、Courier Prime为OFL-1.1，但本子目录无随包字体LICENSE/OFL全文，故只推荐结构，不采用字体
- **obligations**：attribution=true；share_alike=false；non_commercial=false；no_derivatives=false。Apache代码分发保留许可/版权/相关NOTICE并标修改；不要求所有视频片尾署名。CDN依赖须另核许可。
- **attribution_text**：本作品的marker-checklist-card实现参考自 HeyGen, Inc. 与 HyperFrames contributors，Apache-2.0，https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/marker-checklist-card/。本次仅调查，未改动或导入原文件；实际采用时在此列明已做修改。
- **attribution_place**：资产包说明保留完整许可与修改记录；视频简介可列实现来源，不以简介替代软件/字体分发义务
- **risks**：HTML头有字体许可声明，但没有随包完整字体LICENSE/OFL；不把根Apache覆盖两份WOFF2；英文字体不证明支持中文
- **content**：hyperframes:component；3个列出文件；已知合计58055B（仓库树中文件字节相加；不含CDN依赖和缺失远程资产）；槽：top/mid/circled/rest 四段标题；l1/v1…l3/v3 三行标签和值；固定三行，无动态数量合同。
- **preview**：[source_demo](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/marker-checklist-card/demo.html)
- **maps_to / product_lines**：仅参考（C1 清单内容结构）；card / explainer / showcase
- **adaptation**：D 仅参考：复用标题+三行标签/值+逐条勾选结构；字体和卡面按用户已有 F01–F08 重做
- **seekability**：纯函数。静态源码审查；尚未运行顺播/随机跳转/倒拖像素验收。分类描述改造路线；当前GSAP事件语义见adaptation。
- **runtime**：vanilla DOM/SVG + GSAP 3.14.2 CDN；Permanent Marker/Courier Prime 本地 WOFF2；无 Three/React
- **maintenance**：[目录最后提交 2026-08-11T20:03:42Z](https://github.com/heygen-com/hyperframes/commit/4347af3fe1ee4bcf442159f72217ca0ed68ca9e8)
- **verdict**：备选：三项清单节奏清晰，但新增手写风格不符合本次不扩卡面方向
- **evidence**：[源码1](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/marker-checklist-card/marker-checklist-card.html)；[源码2](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/marker-checklist-card/registry-item.json)

### R0-03 bar-chart-race

- **lane / url / pinned_ref**：R0；[源清单](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/bar-chart-race/registry-item.json)；`8aefd91bf82c687222082a80a3c5845ff37e6ca6`
- **license**：Apache-2.0；[LICENSE](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/LICENSE)；HyperFrames自有代码；CDN依赖/字体/图像/音频另核，不自动继承根许可
- **obligations**：attribution=true；share_alike=false；non_commercial=false；no_derivatives=false。Apache代码分发保留许可/版权/相关NOTICE并标修改；不要求所有视频片尾署名。CDN依赖须另核许可。
- **attribution_text**：本作品的bar-chart-race实现参考自 HeyGen, Inc. 与 HyperFrames contributors，Apache-2.0，https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/bar-chart-race/。本次仅调查，未改动或导入原文件；实际采用时在此列明已做修改。
- **attribution_place**：资产包说明保留完整许可与修改记录；视频简介可列实现来源，不以简介替代软件/字体分发义务
- **risks**：图表默认 1920×1080；9:16 必须减项/重排；须使用真实统计来源；示例品牌/数字是占位而非事实
- **content**：hyperframes:block；1个列出文件；已知合计21705B（仓库树中文件字节相加；不含CDN依赖和缺失远程资产）；槽：title、subtitle、periods、series、barCount 3–12、periodDuration 0.4–6s、前后缀/小数位/accent；默认 12s。
- **preview**：[source_demo](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/bar-chart-race/bar-chart-race.html)
- **maps_to / product_lines**：module（concept）；card / explainer / showcase
- **adaptation**：B 需转换：本地化 GSAP；series/periods 解析为数据插槽；提取 render(t)，接主题 token、画幅与时长
- **seekability**：纯函数。静态源码审查；尚未运行顺播/随机跳转/倒拖像素验收。分类描述改造路线；当前GSAP事件语义见adaptation。
- **runtime**：vanilla DOM + GSAP 3.14.2 CDN；无 Three/React/WASM/Worker；GPU 低、CPU 随条目数增长
- **maintenance**：[目录最后提交 2026-08-10T22:46:03Z](https://github.com/heygen-com/hyperframes/commit/9734578e6065d6dec8993c4e30a978263c3eaa8b)
- **verdict**：首推：数值、名次、轴域都由 t 求值，并用属性 setter 保证抑制事件的 seek 也重绘
- **evidence**：[源码1](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/bar-chart-race/bar-chart-race.html)；[源码2](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/bar-chart-race/registry-item.json)

### R0-04 constellation-hub

- **lane / url / pinned_ref**：R0；[源清单](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/constellation-hub/registry-item.json)；`8aefd91bf82c687222082a80a3c5845ff37e6ca6`
- **license**：Apache-2.0；[LICENSE](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/LICENSE)；HyperFrames自有代码；CDN依赖/字体/图像/音频另核，不自动继承根许可
- **obligations**：attribution=true；share_alike=false；non_commercial=false；no_derivatives=false。Apache代码分发保留许可/版权/相关NOTICE并标修改；不要求所有视频片尾署名。CDN依赖须另核许可。
- **attribution_text**：本作品的constellation-hub实现参考自 HeyGen, Inc. 与 HyperFrames contributors，Apache-2.0，https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/constellation-hub/。本次仅调查，未改动或导入原文件；实际采用时在此列明已做修改。
- **attribution_place**：资产包说明保留完整许可与修改记录；视频简介可列实现来源，不以简介替代软件/字体分发义务
- **risks**：是 DOM/SVG 星型网络，非通用 3D 图谱；节点数量/长中文布局仍须验收
- **content**：hyperframes:component；1个列出文件；已知合计17591B（仓库树中文件字节相加；不含CDN依赖和缺失远程资产）；槽：hub_label、nodes、cues、accent、exit；固定 hub，每条连线按实长描绘；低 GPU。
- **preview**：[source_demo](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/constellation-hub/demo.html)
- **maps_to / product_lines**：module（concept/hook）；card / explainer / showcase
- **adaptation**：B 需转换：内容/cues 外接，色枚举改主题 token，字体与 GSAP 离线化；可作 graph-grow 的轻量实现参考
- **seekability**：纯函数。静态源码审查；尚未运行顺播/随机跳转/倒拖像素验收。分类描述改造路线；当前GSAP事件语义见adaptation。
- **runtime**：vanilla DOM/SVG + GSAP 3.14.2 CDN；getTotalLength 于挂载测路径；无 Three/React/WASM/Worker
- **maintenance**：[目录最后提交 2026-08-10T22:46:03Z](https://github.com/heygen-com/hyperframes/commit/9734578e6065d6dec8993c4e30a978263c3eaa8b)
- **verdict**：首推：固定中心/预布局节点，避免实时力导向；cues 可按口播点亮
- **evidence**：[源码1](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/constellation-hub/constellation-hub.html)；[源码2](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/constellation-hub/registry-item.json)

### R0-05 spiral-galaxy

- **lane / url / pinned_ref**：R0；[源清单](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/spiral-galaxy/registry-item.json)；`8aefd91bf82c687222082a80a3c5845ff37e6ca6`
- **license**：Apache-2.0；[LICENSE](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/LICENSE)；HyperFrames自有代码；CDN依赖/字体/图像/音频另核，不自动继承根许可
- **obligations**：attribution=true；share_alike=false；non_commercial=false；no_derivatives=false。Apache代码分发保留许可/版权/相关NOTICE并标修改；不要求所有视频片尾署名。CDN依赖须另核许可。
- **attribution_text**：本作品的spiral-galaxy实现参考自 HeyGen, Inc. 与 HyperFrames contributors，Apache-2.0，https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/spiral-galaxy/。本次仅调查，未改动或导入原文件；实际采用时在此列明已做修改。
- **attribution_place**：资产包说明保留完整许可与修改记录；视频简介可列实现来源，不以简介替代软件/字体分发义务
- **risks**：标为 experimental；旧 Three r147，尚未在 r160 实测；加法点精灵大量重叠时 fill-rate 上升，中文标题另接 O2
- **content**：hyperframes:block；1个列出文件；已知合计13523B（仓库树中文件字节相加；不含CDN依赖和缺失远程资产）；槽：stars、arms、rate、glow、size、core、rim；默认10s。用 setter draw(t)，不是反馈粒子/GPGPU 积分。
- **preview**：[source_demo](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/spiral-galaxy/spiral-galaxy.html)
- **maps_to / product_lines**：module（hook）、background；card / explainer / showcase
- **adaptation**：B 需转换：r147→r160 单实例移植、依赖本地化、时长压到2–6s、补标题/图标插槽和主题映射
- **seekability**：纯函数。静态源码审查；尚未运行顺播/随机跳转/倒拖像素验收。分类描述改造路线；当前GSAP事件语义见adaptation。
- **runtime**：vanilla Three 0.147.0 + GSAP 3.14.2，均 CDN；默认20,000颗，可设2,000–40,000；无 React/WASM/Worker；GPU中等（估计）
- **maintenance**：[目录最后提交 2026-08-10T22:46:03Z](https://github.com/heygen-com/hyperframes/commit/9734578e6065d6dec8993c4e30a978263c3eaa8b)
- **verdict**：首推：固定 seed 一次建星表，shader 解析式用 uTime，天然满足无历史帧星空开场
- **evidence**：[源码1](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/spiral-galaxy/spiral-galaxy.html)；[源码2](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/spiral-galaxy/registry-item.json)

### R0-06 data-chart

- **lane / url / pinned_ref**：R0；[源清单](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/data-chart/registry-item.json)；`8aefd91bf82c687222082a80a3c5845ff37e6ca6`
- **license**：Apache-2.0；[LICENSE](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/LICENSE)；HyperFrames自有代码；CDN依赖/字体/图像/音频另核，不自动继承根许可
- **obligations**：attribution=true；share_alike=false；non_commercial=false；no_derivatives=false。Apache代码分发保留许可/版权/相关NOTICE并标修改；不要求所有视频片尾署名。CDN依赖须另核许可。
- **attribution_text**：本作品的data-chart实现参考自 HeyGen, Inc. 与 HyperFrames contributors，Apache-2.0，https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/data-chart/。本次仅调查，未改动或导入原文件；实际采用时在此列明已做修改。
- **attribution_place**：资产包说明保留完整许可与修改记录；视频简介可列实现来源，不以简介替代软件/字体分发义务
- **risks**：Google Fonts 不满足离线；默认 16:9，长标题/标签未做中文容量证明
- **content**：hyperframes:block；1个列出文件；已知合计13870B（仓库树中文件字节相加；不含CDN依赖和缺失远程资产）；柱形+折线+值标签，按序出现，默认15s；标签更新含 onUpdate，适配时显式统一 render(t)。
- **preview**：[video](https://static.heygen.ai/hyperframes-oss/docs/images/catalog/blocks/data-chart.mp4)；[poster](https://static.heygen.ai/hyperframes-oss/docs/images/catalog/blocks/data-chart.png)
- **maps_to / product_lines**：module（concept）、仅参考（C1 数据卡）；card / explainer / showcase
- **adaptation**：B 需转换：把内嵌数据抽成 JSON；移除 Google Fonts/CDN，补中国字形与主题；显式处理数值标签 onUpdate
- **seekability**：纯函数。静态源码审查；尚未运行顺播/随机跳转/倒拖像素验收。分类描述改造路线；当前GSAP事件语义见adaptation。
- **runtime**：vanilla SVG + GSAP 3.14.2 CDN + Google Fonts；无 Three/React/WASM/Worker；GPU低
- **maintenance**：[目录最后提交 2026-05-19T01:15:15Z](https://github.com/heygen-com/hyperframes/commit/ffbc18ad31bc1aa5503333619b27f66ee7ddb53c)
- **verdict**：备选：柱线组合已有叙事节奏，但 manifest 未提供可直接填的业务数据参数
- **evidence**：[源码1](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/data-chart/data-chart.html)；[源码2](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/data-chart/registry-item.json)

### R0-07 device-frame-stage

- **lane / url / pinned_ref**：R0；[源清单](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/device-frame-stage/registry-item.json)；`8aefd91bf82c687222082a80a3c5845ff37e6ca6`
- **license**：Apache-2.0；[LICENSE](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/LICENSE)；HyperFrames自有代码；CDN依赖/字体/图像/音频另核，不自动继承根许可
- **obligations**：attribution=true；share_alike=false；non_commercial=false；no_derivatives=false。Apache代码分发保留许可/版权/相关NOTICE并标修改；不要求所有视频片尾署名。CDN依赖须另核许可。
- **attribution_text**：本作品的device-frame-stage实现参考自 HeyGen, Inc. 与 HyperFrames contributors，Apache-2.0，https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/device-frame-stage/。本次仅调查，未改动或导入原文件；实际采用时在此列明已做修改。
- **attribution_place**：资产包说明保留完整许可与修改记录；视频简介可列实现来源，不以简介替代软件/字体分发义务
- **risks**：screen/body 槽需适配用户图片插槽合同；音效回调不应在乱序 seek 时重复触发
- **content**：hyperframes:component；1个列出文件；已知合计19228B（仓库树中文件字节相加；不含CDN依赖和缺失远程资产）；device、cutout、body 参数；出入场固定时长，hold 用 sin(t) 浮动。当前通过 tween onUpdate 画帧。
- **preview**：[source_demo](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/device-frame-stage/demo.html)
- **maps_to / product_lines**：module（concept/hook）；card / explainer / showcase
- **adaptation**：B 需转换：screen 插槽接本地截图，重绘由显式 render(t) 接管；hf:sfx 事件改为独立绝对时间音轨
- **seekability**：纯函数。静态源码审查；尚未运行顺播/随机跳转/倒拖像素验收。分类描述改造路线；当前GSAP事件语义见adaptation。
- **runtime**：vanilla DOM/CSS + GSAP 3.14.2 CDN；无 Three/React/WASM/Worker；GPU低
- **maintenance**：[目录最后提交 2026-08-10T22:46:03Z](https://github.com/heygen-com/hyperframes/commit/9734578e6065d6dec8993c4e30a978263c3eaa8b)
- **verdict**：备选：纯 CSS 手机/平板边框比3D模型轻，能满足工具教程的截图样机需求
- **evidence**：[源码1](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/device-frame-stage/device-frame-stage.html)；[源码2](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/device-frame-stage/registry-item.json)

### R0-08 particle-text-dissolve

- **lane / url / pinned_ref**：R0；[源清单](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/particle-text-dissolve/registry-item.json)；`8aefd91bf82c687222082a80a3c5845ff37e6ca6`
- **license**：Apache-2.0；[LICENSE](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/LICENSE)；HyperFrames自有代码；CDN依赖/字体/图像/音频另核，不自动继承根许可
- **obligations**：attribution=true；share_alike=false；non_commercial=false；no_derivatives=false。Apache代码分发保留许可/版权/相关NOTICE并标修改；不要求所有视频片尾署名。CDN依赖须另核许可。
- **attribution_text**：本作品的particle-text-dissolve实现参考自 HeyGen, Inc. 与 HyperFrames contributors，Apache-2.0，https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/particle-text-dissolve/。本次仅调查，未改动或导入原文件；实际采用时在此列明已做修改。
- **attribution_place**：资产包说明保留完整许可与修改记录；视频简介可列实现来源，不以简介替代软件/字体分发义务
- **risks**：此处可烘焙指挂载期字形/粒子表预计算，不是历史帧模拟；字体/画幅/浏览器光栅化影响表；必须固定环境；不是挤出3D文字
- **content**：hyperframes:component；1个列出文件；已知合计18946B（仓库树中文件字节相加；不含CDN依赖和缺失远程资产）；text、direction in/out、density、accent、exit；原实现 paint 每次 clearRect，再由(t,table)绘制；timeline onUpdate 只在事件开启时调用。
- **preview**：[source_demo](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/particle-text-dissolve/demo.html)
- **maps_to / product_lines**：module（hook）、motion；card / explainer / showcase
- **adaptation**：B 需转换：挂载等待本地中文字体 ready 后一次采样；固定粒子表；外露 paint(t)，不用默认 suppressEvents seek；接文本/颜色/时长
- **seekability**：可烘焙。静态源码审查；尚未运行顺播/随机跳转/倒拖像素验收。分类描述改造路线；当前GSAP事件语义见adaptation。
- **runtime**：vanilla Canvas2D + DOM + GSAP 3.14.2 CDN；无 Three/React/WASM/Worker；每帧遍历粒子，CPU中等估计
- **maintenance**：[目录最后提交 2026-08-10T22:46:03Z](https://github.com/heygen-com/hyperframes/commit/9734578e6065d6dec8993c4e30a978263c3eaa8b)
- **verdict**：首推：一次字形采样+seed 表，逐帧纯重绘，可做低成本文字聚合而不需3D
- **evidence**：[源码1](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/particle-text-dissolve/particle-text-dissolve.html)；[源码2](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/particle-text-dissolve/registry-item.json)

### R0-09 wireframe-portal-title

- **lane / url / pinned_ref**：R0；[源清单](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/wireframe-portal-title/registry-item.json)；`8aefd91bf82c687222082a80a3c5845ff37e6ca6`
- **license**：Apache-2.0；[LICENSE](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/LICENSE)；HyperFrames自有代码；CDN依赖/字体/图像/音频另核，不自动继承根许可；附加许可：Geist OFL-1.1: https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/wireframe-portal-title/assets/fonts/Geist-OFL.txt
- **obligations**：attribution=true；share_alike=true；non_commercial=false；no_derivatives=false。Apache代码分发保留许可/版权/相关NOTICE并标修改；不要求所有视频片尾署名。OFL只要求字体本体/修改字体沿用OFL，不传染视频；布尔SA在此仅为保守资产筛选。
- **attribution_text**：本作品的wireframe-portal-title实现参考自 HeyGen, Inc. 与 HyperFrames contributors，Apache-2.0，https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/wireframe-portal-title/。本次仅调查，未改动或导入原文件；实际采用时在此列明已做修改。字体如保留原包，另按随包OFL版权声明附完整许可。
- **attribution_place**：资产包说明保留完整许可与修改记录；视频简介可列实现来源，不以简介替代软件/字体分发义务
- **risks**：manifest 缺 variables，参数实际在HTML/SKILL；随包 Geist 不能证明中文覆盖；r181.2不应与宿主r160混装；预算350MB/实例是上游说明，未实测
- **content**：hyperframes:block；6个列出文件；已知合计273086B（仓库树中文件字节相加；不含CDN依赖和缺失远程资产）；9参数：title(默认最大18 chars)、replacementPhrase、phraseDuration、phraseEasing、settleGlitch、depthFog、subtitle(48)、accent、burstChaos；8s；hf-seek 手动回调重绘。
- **preview**：[video](https://static.heygen.ai/hyperframes-oss/docs/images/catalog/blocks/wireframe-portal-title.mp4)；[poster](https://static.heygen.ai/hyperframes-oss/docs/images/catalog/blocks/wireframe-portal-title.png)
- **maps_to / product_lines**：module（hook）；card / explainer / showcase
- **adaptation**：C 需扩展合同：hook 允许3D正文标题且DOM第4层可空；另需B：r181.2→r160重构、中文字体子集、缩至2–6s、依赖本地化
- **seekability**：纯函数。静态源码审查；尚未运行顺播/随机跳转/倒拖像素验收。分类描述改造路线；当前GSAP事件语义见adaptation。
- **runtime**：vanilla Three0.181.2 ES模块+addons、GSAP3.14.2、Clipper6.4.2 CDN；本地Geist TTF；无React/WASM/Worker；后期多pass，GPU高估计
- **maintenance**：[目录最后提交 2026-09-25T04:43:43Z](https://github.com/heygen-com/hyperframes/commit/53e2e20a15fb183a773360543744793189557096)
- **verdict**：备选：标题穿门户并换句的机制合适，但 r160/中文/内存成本使它不宜首个直接接入
- **evidence**：[源码1](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/wireframe-portal-title/wireframe-portal-title.html)；[源码2](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/wireframe-portal-title/registry-item.json)

### R0-10 glass-shard-title

- **lane / url / pinned_ref**：R0；[源清单](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/glass-shard-title/registry-item.json)；`8aefd91bf82c687222082a80a3c5845ff37e6ca6`
- **license**：Apache-2.0；[LICENSE](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/LICENSE)；HyperFrames自有代码；CDN依赖/字体/图像/音频另核，不自动继承根许可；附加许可：Geist OFL-1.1: https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/glass-shard-title/assets/fonts/Geist-OFL.txt；Cormorant OFL-1.1: https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/glass-shard-title/assets/fonts/CormorantGaramond-OFL.txt；Three MIT: https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/glass-shard-title/assets/Three-LICENSE.txt；HDR/matcap许可来源未闭合
- **obligations**：attribution=true；share_alike=true；non_commercial=false；no_derivatives=false。Apache代码分发保留许可/版权/相关NOTICE并标修改；不要求所有视频片尾署名。OFL只要求字体本体/修改字体沿用OFL，不传染视频；布尔SA在此仅为保守资产筛选。
- **attribution_text**：本作品的glass-shard-title实现参考自 HeyGen, Inc. 与 HyperFrames contributors，Apache-2.0，https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/glass-shard-title/。本次仅调查，未改动或导入原文件；实际采用时在此列明已做修改。字体如保留原包，另按随包OFL版权声明附完整许可。
- **attribution_place**：资产包说明保留完整许可与修改记录；视频简介可列实现来源，不以简介替代软件/字体分发义务
- **risks**：HDR及matcap不应自动套根Apache；缺单项许可证证明；matcap为CDN远程资产；随包字体非CJK保证；上游预算约350MB/实例未实测
- **content**：hyperframes:block；12个列出文件；已知合计2464132B（仓库树中文件字节相加；不含CDN依赖和缺失远程资产）；19参数包括headline最大40 chars、tileCount1–400、bevel、flyInTime/flyOutTime、stagger、fog；默认12.16s；几何seed预构建，再按t闭式飞行；hf-seek接线已存在。
- **preview**：[video](https://static.heygen.ai/hyperframes-oss/docs/images/catalog/blocks/glass-shard-title.mp4)；[poster](https://static.heygen.ai/hyperframes-oss/docs/images/catalog/blocks/glass-shard-title.png)
- **maps_to / product_lines**：module（hook）；card / explainer / showcase
- **adaptation**：C 需扩展合同：hook 3D标题；另需B：r181.2→r160、中文本地字形、2–6s、替换或证明HDR/matcap许可
- **seekability**：可烘焙。静态源码审查；尚未运行顺播/随机跳转/倒拖像素验收。分类描述改造路线；当前GSAP事件语义见adaptation。
- **runtime**：vanilla bundled Three0.181.2（562335B glass-main.js）+ GSAP3.14.2/d3-delaunay6.0.4 CDN；HDR1,632,708B；无React；GPU高估计
- **maintenance**：[目录最后提交 2026-09-24T17:08:15Z](https://github.com/heygen-com/hyperframes/commit/8dabc8af63fc72fefa5af918ce99377ae1846fc3)
- **verdict**：备选：seeded Voronoi玻璃拼字+闭式飞行可复用，但第三方纹理来源与r160移植未闭合
- **evidence**：[源码1](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/glass-shard-title/glass-shard-title.html)；[源码2](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/glass-shard-title/registry-item.json)

### R0-11 vfx-portal

- **lane / url / pinned_ref**：R0；[源清单](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/vfx-portal/registry-item.json)；`8aefd91bf82c687222082a80a3c5845ff37e6ca6`
- **license**：Apache-2.0；[LICENSE](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/LICENSE)；HyperFrames自有代码；CDN依赖/字体/图像/音频另核，不自动继承根许可
- **obligations**：attribution=true；share_alike=false；non_commercial=false；no_derivatives=false。Apache代码分发保留许可/版权/相关NOTICE并标修改；不要求所有视频片尾署名。CDN依赖须另核许可。
- **attribution_text**：本作品的vfx-portal实现参考自 HeyGen, Inc. 与 HyperFrames contributors，Apache-2.0，https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/vfx-portal/。本次仅调查，未改动或导入原文件；实际采用时在此列明已做修改。
- **attribution_place**：资产包说明保留完整许可与修改记录；视频简介可列实现来源，不以简介替代软件/字体分发义务
- **risks**：drawElementImage 特性检测不通过时警告/回退；非标准HTML-in-Canvas增加浏览器锁定；DOM面板捕获与字体初始化需显式ready
- **content**：hyperframes:block；1个列出文件；已知合计27022B（仓库树中文件字节相加；不含CDN依赖和缺失远程资产）；10s；seed噪声+timeline状态可解析，但无统一通用content参数，onUpdate受seek事件选项影响。
- **preview**：[video](https://static.heygen.ai/hyperframes-oss/docs/images/catalog/blocks/vfx-portal.mp4)；[poster](https://static.heygen.ai/hyperframes-oss/docs/images/catalog/blocks/vfx-portal.png)
- **maps_to / product_lines**：仅参考（O1 门户机制）；card / explainer / showcase
- **adaptation**：D 仅参考：保留门户/能量圈/推镜机制；标准离线环境中用图片纹理槽重写采样，r147→r160
- **seekability**：纯函数。静态源码审查；尚未运行顺播/随机跳转/倒拖像素验收。分类描述改造路线；当前GSAP事件语义见adaptation。
- **runtime**：vanilla Three0.147.0+GSAP3.14.2 CDN、Google Fonts、实验性Canvas drawElementImage；无React；GPU中等估计
- **maintenance**：[目录最后提交 2026-05-19T01:15:15Z](https://github.com/heygen-com/hyperframes/commit/ffbc18ad31bc1aa5503333619b27f66ee7ddb53c)
- **verdict**：排除：当前依赖实验性 Canvas drawElementImage，不能当作标准离线 r160 即用资产；机制可参考
- **evidence**：[源码1](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/vfx-portal/vfx-portal.html)；[源码2](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/vfx-portal/registry-item.json)

### R0-12 transitions-destruction

- **lane / url / pinned_ref**：R0；[源清单](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/transitions-destruction/registry-item.json)；`8aefd91bf82c687222082a80a3c5845ff37e6ca6`
- **license**：Apache-2.0；[LICENSE](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/LICENSE)；HyperFrames自有代码；CDN依赖/字体/图像/音频另核，不自动继承根许可
- **obligations**：attribution=true；share_alike=false；non_commercial=false；no_derivatives=false。Apache代码分发保留许可/版权/相关NOTICE并标修改；不要求所有视频片尾署名。CDN依赖须另核许可。
- **attribution_text**：本作品的transitions-destruction实现参考自 HeyGen, Inc. 与 HyperFrames contributors，Apache-2.0，https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/transitions-destruction/。本次仅调查，未改动或导入原文件；实际采用时在此列明已做修改。
- **attribution_place**：资产包说明保留完整许可与修改记录；视频简介可列实现来源，不以简介替代软件/字体分发义务
- **risks**：tl.call 清理与 onUpdate 依赖事件，在乱序seek容易漏执行；transition showcase 不等于多个生产就绪效果；默认文字/面板演示不可直接复用为素材
- **content**：hyperframes:block；1个列出文件；已知合计11754B（仓库树中文件字节相加；不含CDN依赖和缺失远程资产）；本文件主要是一个page-burn演示；噪声由progress闭式求值，没有反馈buffer。
- **preview**：[video](https://static.heygen.ai/hyperframes-oss/docs/images/catalog/blocks/transitions-destruction.mp4)；[poster](https://static.heygen.ai/hyperframes-oss/docs/images/catalog/blocks/transitions-destruction.png)
- **maps_to / product_lines**：仅参考、motion/transition（改造后）；card / explainer / showcase
- **adaptation**：D 仅参考：这是完整14s演示；拆出纯 drawBurn(progress)，将 A/B 面板改纹理槽，所有清理并入按t重绘
- **seekability**：纯函数。静态源码审查；尚未运行顺播/随机跳转/倒拖像素验收。分类描述改造路线；当前GSAP事件语义见adaptation。
- **runtime**：vanilla Canvas2D/CSS + GSAP3.14.2 CDN；无Three/React/WASM/Worker；GPU低至中估计
- **maintenance**：[目录最后提交 2026-05-19T01:15:15Z](https://github.com/heygen-com/hyperframes/commit/ffbc18ad31bc1aa5503333619b27f66ee7ddb53c)
- **verdict**：备选：逐帧清空后算burn边缘，机制可改成无状态page-burn；不能整体当现成转场API
- **evidence**：[源码1](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/transitions-destruction/transitions-destruction.html)；[源码2](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/transitions-destruction/registry-item.json)

### R0-13 sdf-iris

- **lane / url / pinned_ref**：R0；[源清单](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/sdf-iris/registry-item.json)；`8aefd91bf82c687222082a80a3c5845ff37e6ca6`
- **license**：Apache-2.0；[LICENSE](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/LICENSE)；HyperFrames自有代码；CDN依赖/字体/图像/音频另核，不自动继承根许可
- **obligations**：attribution=true；share_alike=false；non_commercial=false；no_derivatives=false。Apache代码分发保留许可/版权/相关NOTICE并标修改；不要求所有视频片尾署名。CDN依赖须另核许可。
- **attribution_text**：本作品的sdf-iris实现参考自 HeyGen, Inc. 与 HyperFrames contributors，Apache-2.0，https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/sdf-iris/。本次仅调查，未改动或导入原文件；实际采用时在此列明已做修改。
- **attribution_place**：资产包说明保留完整许可与修改记录；视频简介可列实现来源，不以简介替代软件/字体分发义务
- **risks**：示例不是通用A/B纹理接口；底层原生WebGL，不受Three版本直接约束，但需同画布合成策略
- **content**：hyperframes:block；1个列出文件；已知合计12624B（仓库树中文件字节相加；不含CDN依赖和缺失远程资产）；4s演示，1–3s转场；shader只取A/B和progress，无前帧状态；timeline onUpdate须显式适配。
- **preview**：[video](https://static.heygen.ai/hyperframes-oss/docs/images/catalog/blocks/sdf-iris.mp4)；[poster](https://static.heygen.ai/hyperframes-oss/docs/images/catalog/blocks/sdf-iris.png)
- **maps_to / product_lines**：module（transition）、motion/transition（扩展后）；card / explainer / showcase
- **adaptation**：B 需转换：直接接 A/B 本地纹理，外露render(progress)，移除示例DOM截取/GoogleFonts与CDN，保证端点直达重画
- **seekability**：纯函数。静态源码审查；尚未运行顺播/随机跳转/倒拖像素验收。分类描述改造路线；当前GSAP事件语义见adaptation。
- **runtime**：vanilla原生WebGL+GSAP3.14.2 CDN、Google Fonts；无Three/React/WASM/Worker；GPU低至中估计
- **maintenance**：[目录最后提交 2026-05-19T01:15:15Z](https://github.com/heygen-com/hyperframes/commit/ffbc18ad31bc1aa5503333619b27f66ee7ddb53c)
- **verdict**：备选：SDF iris无历史采样，能补现有wipe之外的径向开孔；实现短但还不是用户合同
- **evidence**：[源码1](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/sdf-iris/sdf-iris.html)；[源码2](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/sdf-iris/registry-item.json)

### R0-14 world-map

- **lane / url / pinned_ref**：R0；[源清单](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/world-map/registry-item.json)；`8aefd91bf82c687222082a80a3c5845ff37e6ca6`
- **license**：Apache-2.0；[LICENSE](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/LICENSE)；HyperFrames自有代码；CDN依赖/字体/图像/音频另核，不自动继承根许可
- **obligations**：attribution=true；share_alike=false；non_commercial=false；no_derivatives=false。Apache代码分发保留许可/版权/相关NOTICE并标修改；不要求所有视频片尾署名。CDN依赖须另核许可。
- **attribution_text**：本作品的world-map实现参考自 HeyGen, Inc. 与 HyperFrames contributors，Apache-2.0，https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/world-map/。本次仅调查，未改动或导入原文件；实际采用时在此列明已做修改。
- **attribution_place**：资产包说明保留完整许可与修改记录；视频简介可列实现来源，不以简介替代软件/字体分发义务
- **risks**：中国边界合规未证实，按用户规则不可用；跨境地图/地名政治与地域风险；远程world-atlas数据与字体使默认不离线
- **content**：hyperframes:block；1个列出文件；已知合计12899B（仓库树中文件字节相加；不含CDN依赖和缺失远程资产）；world choropleth+globe inset，14s；地图数据URL使用@2而非精确包版本，不足以冻结数据。
- **preview**：[video](https://static.heygen.ai/hyperframes-oss/docs/images/catalog/blocks/world-map.mp4)；[poster](https://static.heygen.ai/hyperframes-oss/docs/images/catalog/blocks/world-map.png)
- **maps_to / product_lines**：仅参考（非中国边界素材）；explainer / showcase
- **adaptation**：D 仅参考；涉及中国边界的用途不可用，不能以视觉隐藏替代合规数据
- **seekability**：纯函数。静态源码审查；尚未运行顺播/随机跳转/倒拖像素验收。分类描述改造路线；当前GSAP事件语义见adaptation。
- **runtime**：vanilla D3@7、topojson-client3.1.0、world-atlas@2、GSAP3.14.2 CDN、GoogleFonts；无React/Three
- **maintenance**：[目录最后提交 2026-05-19T01:15:15Z](https://github.com/heygen-com/hyperframes/commit/ffbc18ad31bc1aa5503333619b27f66ee7ddb53c)
- **verdict**：排除：使用world-atlas国家边界，未给出中国国家标准地图审图证明，违背本次地图硬门槛
- **evidence**：[源码1](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/world-map/world-map.html)；[源码2](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/world-map/registry-item.json)

### R0-15 HyperFrames bundled SFX baseline

- **lane / url / pinned_ref**：R0；[源清单](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/skills/media-use/audio/assets/sfx/CREDITS.md)；`8aefd91bf82c687222082a80a3c5845ff37e6ca6`
- **license**：Pixabay Content License（仓库CREDITS声明，非Apache）；[skills/media-use/audio/assets/sfx/CREDITS.md](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/skills/media-use/audio/assets/sfx/CREDITS.md)；已读固定SHA的CREDITS；仓库无完整逐音效LICENSE及作者/原始条目，未在本次GitHub-only范围独立核站外条款
- **obligations**：attribution=false；share_alike=false；non_commercial=false；no_derivatives=false。四布尔按仓库CREDITS宣称，不代表再分发原始素材授权已核实；CREDITS只明确视频等衍生作品再分发。禁止据根Apache得出音效可入原始资产包。
- **attribution_text**：音效使用 HyperFrames 收录的 Pixabay 音效（具体原作者/源条目待补），Pixabay Content License： https://pixabay.com/service/license-summary/ 。来源清单：https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/skills/media-use/audio/assets/sfx/CREDITS.md 。本次未下载、转码或修改；原文件再分发授权未核实。
- **attribution_place**：资产包说明保留逐项来源/许可；若后续获准用于视频，视频简介可自愿署名
- **risks**：缺逐音效原作者/源页面，版权链不完整；官方文档声称21文件与实际19不符；19文件仅17独立blob，勿双计；只确认视频衍生使用声明，原始MP3资产包分发未确认
- **content**：19MP3，17独立blob，1300487B；逐项上表
- **preview**：https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/skills/media-use/audio/assets/sfx/
- **maps_to / product_lines**：media（许可核清后）、仅参考（当前类别基线）；card / explainer / showcase
- **adaptation**：D 仅参考：先做类别基线，不下载/再分发原始MP3；后续需逐条来源和确切许可
- **seekability**：不适用（静态素材）。音频是本地文件，非历史帧视觉状态
- **runtime**：音频文件非Three/React；不需要WASM/Worker/CDN时钟；本地音轨按绝对时间调度即可
- **maintenance**：[目录最后提交 2026-07-07T03:41:05Z](https://github.com/heygen-com/hyperframes/commit/5fe957363d2be6d04f4a002fea965dbcc2bd633b)
- **verdict**：排除：在原始资产包授权证明补齐前排除入库；仍作为A2去重基线
- **evidence**：[源码1](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/skills/media-use/audio/assets/sfx/manifest.json)；[源码2](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/skills/media-use/audio/references/sfx.md)

## 8. 后续本地验收建议（此次未执行）

- 在固定浏览器/GPU/r160/GSAP/字体环境加载，网络断开后确认全部依赖能用
- 帧序列顺播、乱序(t=4→0→2→5→2)、倒序分别取同t图像；比较同环境像素hash，必要时解释可接受色彩误差，不把“看起来一样”当证明
- 验证t=0、结束边界、重复seek同t、挂载/卸载/重挂、2/4/6秒与9:16/16:9
- 检查中文标题的空字、方框、换行、轮廓洞/挤出与主题可读性；每期只换文字/图标/图片槽，不改代码
- 分别记录CPU/GPU时间、内存峰值和掉帧；此报告的低/中/高及350MB均不是实际测量
- LICENSE/NOTICE/字体RFN/音效逐项来源进入闭包并汇总署名，再由用户hash接纳

本路交付只含本报告和自己整理的JSONL候选卡；未包含任何第三方源文件/字体/音效/截图本体。

