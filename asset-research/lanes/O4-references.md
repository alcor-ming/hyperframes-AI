# O4 只作参考：五种可复述的开场/转场机制

调查日期：2026-10-02。本路只保留链接与原创机制分析，未抓取站点图片/视频/字体，也没有将原代码复制进交付目录。下列“关键时刻”是我们建议的短视频节奏，不是伪造的逐帧观测记录。

## 首推与边界
首推动态文字进前景、文字片层回声、图片副本路径三种机制。三个都能围绕单个标题或图片槽构造；只参考动作逻辑，不搬网页布局。

Repeating Image Transition的示例图由Midjourney生成，图像本体按计划排除。两个2019 WebGL参考没有独立LICENSE，且README有Codrops限制原样再分发/插件化条款，代码同样不接纳；保留链接是为了机制研究。不要把“在Codrops出现”自动等同MIT，也不要把MIT代码许可套到摄影/字体上。

## 从参考到模块时应补的约束
单镜头2–6秒；slots只接标题/图片/主题；所有延迟以归一化duration缩放；图片副本用有限对象的解析位置，不用afterimage；段落长文始终留给DOM信息层。9:16优先纵向展开，16:9允许横向扫过，但都给标题稳定读时。

本路不把获奖标签作为质量证据，也不从Awwwards搬运未获许可的作品素材。

## 候选卡

### O4-01 Kinetic Typography Page Transition

- **ID**：O4-01
- **调查路**：O4
- **名称**：Kinetic Typography Page Transition
- **仓库**：https://github.com/codrops/KineticTypePageTransition
- **固定版本**：ebe926e2f1de42950c36ff8a678321155280c1af
- **许可**：
  - spdx：MIT
  - name：MIT
  - path：LICENSE
  - url：https://github.com/codrops/KineticTypePageTransition/blob/ebe926e2f1de42950c36ff8a678321155280c1af/LICENSE
  - scope：此许可记录只描述被链接的代码；本次只写自己的机制分析，不复制任何代码、图片、字体、音频或预览。
- **义务**：
  - attribution：True
  - share_alike：False
  - non_commercial：False
  - no_derivatives：False
  - note：若以后复制MIT代码须保留版权/许可；本次仅链接及原创分析。
- **可粘贴署名**：机制参考：Kinetic Typography Page Transition — Codrops，https://tympanus.net/codrops/?p=56722。本报告仅链接并以自己的话分析，未复制原作素材或代码。
- **署名位置**：研究说明/资产包设计出处（不是把参考作品署名伪装成获准分发）
- **风险**：
  - 示例图片/字体/依赖授权与代码分开；不抓取、不复制原站资产。
- **内容、格式、体积与预览**：
  - quantity：1
  - format：链接+原创机制说明
  - bytes：0
  - preview：https://tympanus.net/Development/KineticTypePageTransition/
  - article：https://tympanus.net/codrops/?p=56722
- **映射**：
  - 仅参考
- **产品线**：
  - explainer
  - showcase
- **适配等级**：D：仅参考，自写参数化机制；没有资产导入许可。
- **时间可寻址性**：不适用（仅参考）
- **运行环境**：网页原运行时未导入/未在r160验证；自己的实现再按render(t)合同重写。
- **维护证据**：
  - last_commit_at：2025-05-30T04:50:40+01:00
  - source：https://github.com/codrops/KineticTypePageTransition/commit/ebe926e2f1de42950c36ff8a678321155280c1af
  - checked_at：2026-10-02
- **结论**：首推（仅机制参考）
- **审查与适配说明**：
  - 发生了什么：背景大字先被放大推到前景，文字列错时横向掠过，遮住旧内容后露出新一层。文字本身承担场景切换，不需要再加独立转场贴片。
  - 为什么好看_研究判断：把“读标题”和“进入正文”做成一次因果明确的动作；最大字形遮住画面时藏切镜，开场视觉连续。
  - 关键时刻_建议的影片节奏而非原站测量：0–25%让主标题先可读；25–70%文字放大、错时横扫；70–100%揭示正文。原源码timeline的duration/stagger只是参考，不照搬网页节奏。
  - evidence：
    - label：固定版本说明/源码
    - url：https://github.com/codrops/KineticTypePageTransition/blob/ebe926e2f1de42950c36ff8a678321155280c1af/src/js/typeTransition.js
    - label：原作者文章
    - url：https://tympanus.net/codrops/?p=56722
  - review_scope：只读README/许可/关键源码与作者文字说明；未运行交互网页、未录屏、未下载示例图片。

### O4-02 Text Repetition Scroll Effect

- **ID**：O4-02
- **调查路**：O4
- **名称**：Text Repetition Scroll Effect
- **仓库**：https://github.com/codrops/TextRepetitionEffect
- **固定版本**：fabaafe0124e7bdf66906c6214f00800f5575c4c
- **许可**：
  - spdx：MIT
  - name：MIT
  - path：LICENSE
  - url：https://github.com/codrops/TextRepetitionEffect/blob/fabaafe0124e7bdf66906c6214f00800f5575c4c/LICENSE
  - scope：此许可记录只描述被链接的代码；本次只写自己的机制分析，不复制任何代码、图片、字体、音频或预览。
- **义务**：
  - attribution：True
  - share_alike：False
  - non_commercial：False
  - no_derivatives：False
  - note：若以后复制MIT代码须保留版权/许可；本次仅链接及原创分析。
- **可粘贴署名**：机制参考：Text Repetition Scroll Effect — Codrops，https://tympanus.net/codrops/2022/04/13/on-scroll-text-repetition-animation/。本报告仅链接并以自己的话分析，未复制原作素材或代码。
- **署名位置**：研究说明/资产包设计出处（不是把参考作品署名伪装成获准分发）
- **风险**：
  - 示例图片/字体/依赖授权与代码分开；不抓取、不复制原站资产。
- **内容、格式、体积与预览**：
  - quantity：1
  - format：链接+原创机制说明
  - bytes：0
  - preview：https://tympanus.net/Development/TextRepetitionEffect/
  - article：https://tympanus.net/codrops/2022/04/13/on-scroll-text-repetition-animation/
- **映射**：
  - 仅参考
- **产品线**：
  - card
  - explainer
  - showcase
- **适配等级**：D：仅参考，自写参数化机制；没有资产导入许可。
- **时间可寻址性**：不适用（仅参考）
- **运行环境**：网页原运行时未导入/未在r160验证；自己的实现再按render(t)合同重写。
- **维护证据**：
  - last_commit_at：2022-04-13T11:22:55+01:00
  - source：https://github.com/codrops/TextRepetitionEffect/commit/fabaafe0124e7bdf66906c6214f00800f5575c4c
  - checked_at：2026-10-02
- **结论**：首推（仅机制参考）
- **审查与适配说明**：
  - 发生了什么：同一句大字复制成上下多层，只露出片段。层与层按不同距离展开，页面背景色填进层间间隙，形成像回声一样的文字节奏。
  - 为什么好看_研究判断：所有层都来自同一信息，繁复运动仍围绕一个标题；可在峰值后收拢成一行，阅读目标清楚。
  - 关键时刻_建议的影片节奏而非原站测量：0–20%完整词出现；20–65%上下片层展开；65–100%收回主标题并停稳。把scroll进度换绝对时间，不能读取滚轮速度。
  - evidence：
    - label：固定版本说明/源码
    - url：https://github.com/codrops/TextRepetitionEffect/blob/fabaafe0124e7bdf66906c6214f00800f5575c4c/src/js/demo1/repeatTextScrollFx.js
    - label：原作者文章
    - url：https://tympanus.net/codrops/2022/04/13/on-scroll-text-repetition-animation/
  - review_scope：只读README/许可/关键源码与作者文字说明；未运行交互网页、未录屏、未下载示例图片。

### O4-03 Repeating Image Transition

- **ID**：O4-03
- **调查路**：O4
- **名称**：Repeating Image Transition
- **仓库**：https://github.com/codrops/RepeatingImageTransition
- **固定版本**：354c58487ad6a8b728e35b34d6666fca72e9b4eb
- **许可**：
  - spdx：MIT
  - name：MIT
  - path：LICENSE
  - url：https://github.com/codrops/RepeatingImageTransition/blob/354c58487ad6a8b728e35b34d6666fca72e9b4eb/LICENSE
  - scope：此许可记录只描述被链接的代码；本次只写自己的机制分析，不复制任何代码、图片、字体、音频或预览。
- **义务**：
  - attribution：True
  - share_alike：False
  - non_commercial：False
  - no_derivatives：False
  - note：若以后复制MIT代码须保留版权/许可；本次仅链接及原创分析。
- **可粘贴署名**：机制参考：Repeating Image Transition — Codrops，https://tympanus.net/codrops/?p=92571。本报告仅链接并以自己的话分析，未复制原作素材或代码。
- **署名位置**：研究说明/资产包设计出处（不是把参考作品署名伪装成获准分发）
- **风险**：
  - 示例图片/字体/依赖授权与代码分开；不抓取、不复制原站资产。
  - README明确示例图为Midjourney生成，本次按计划排除这些图像。
- **内容、格式、体积与预览**：
  - quantity：1
  - format：链接+原创机制说明
  - bytes：0
  - preview：https://tympanus.net/Development/RepeatingImageTransition/
  - article：https://tympanus.net/codrops/?p=92571
- **映射**：
  - 仅参考
- **产品线**：
  - explainer
  - showcase
- **适配等级**：D：仅参考，自写参数化机制；没有资产导入许可。
- **时间可寻址性**：不适用（仅参考）
- **运行环境**：网页原运行时未导入/未在r160验证；自己的实现再按render(t)合同重写。
- **维护证据**：
  - last_commit_at：2025-05-01T14:12:53+01:00
  - source：https://github.com/codrops/RepeatingImageTransition/commit/354c58487ad6a8b728e35b34d6666fca72e9b4eb
  - checked_at：2026-10-02
- **结论**：首推（仅机制参考，示例图排除）
- **审查与适配说明**：
  - 发生了什么：同一图片的多个副本沿规划路径错时通过画面，前后副本形成轨迹，最后一个成为新场景的稳定主体。
  - 为什么好看_研究判断：轨迹让用户预知主体去向，错时副本制造速度与节拍；是预先画出的多个副本，不需要历史帧afterimage。
  - 关键时刻_建议的影片节奏而非原站测量：0–20%单张主体定位；20–75%有限数量副本沿曲线错时运动；75–100%删除尾随副本，主图稳定。每个副本位置直接用t-delay求值。
  - evidence：
    - label：固定版本说明/源码
    - url：https://github.com/codrops/RepeatingImageTransition/blob/354c58487ad6a8b728e35b34d6666fca72e9b4eb/js/index.js
    - label：原作者文章
    - url：https://tympanus.net/codrops/?p=92571
  - review_scope：只读README/许可/关键源码与作者文字说明；未运行交互网页、未录屏、未下载示例图片。

### O4-04 Creative WebGL Image Transitions

- **ID**：O4-04
- **调查路**：O4
- **名称**：Creative WebGL Image Transitions
- **仓库**：https://github.com/akella/webGLImageTransitions
- **固定版本**：498d8fb48426de0a82fc5f6ad06736efc875a75b
- **许可**：
  - spdx：NOASSERTION
  - name：自定义Codrops条款（仅README；无独立LICENSE）
  - path：None
  - url：https://github.com/akella/webGLImageTransitions/blob/498d8fb48426de0a82fc5f6ad06736efc875a75b/README.md
  - scope：此许可记录只描述被链接的代码；本次只写自己的机制分析，不复制任何代码、图片、字体、音频或预览。
- **义务**：
  - attribution：False
  - share_alike：False
  - non_commercial：False
  - no_derivatives：False
  - note：无独立LICENSE且README另限制原样再分发/插件化，按计划排除资产入库；四布尔不足表达自定义限制，不代表可用。
- **可粘贴署名**：机制参考：Creative WebGL Image Transitions — Yuri Artiukh，https://tympanus.net/codrops/2019/11/05/creative-webgl-image-transitions/。本报告仅链接并以自己的话分析，未复制原作素材或代码。
- **署名位置**：研究说明/资产包设计出处（不是把参考作品署名伪装成获准分发）
- **风险**：
  - 示例图片/字体/依赖授权与代码分开；不抓取、不复制原站资产。
  - 代码无独立LICENSE；README自定义条款限制再分发，本次不采纳代码。
- **内容、格式、体积与预览**：
  - quantity：1
  - format：链接+原创机制说明
  - bytes：0
  - preview：https://tympanus.net/Development/webGLImageTransitions/
  - article：https://tympanus.net/codrops/2019/11/05/creative-webgl-image-transitions/
- **映射**：
  - 仅参考
- **产品线**：
  - explainer
  - showcase
- **适配等级**：D：仅参考，自写参数化机制；没有资产导入许可。
- **时间可寻址性**：不适用（仅参考）
- **运行环境**：网页原运行时未导入/未在r160验证；自己的实现再按render(t)合同重写。
- **维护证据**：
  - last_commit_at：2019-11-05T16:42:33+04:00
  - source：https://github.com/akella/webGLImageTransitions/commit/498d8fb48426de0a82fc5f6ad06736efc875a75b
  - checked_at：2026-10-02
- **结论**：备选（只看机制，代码包排除）
- **审查与适配说明**：
  - 发生了什么：用progress扭曲两张图的UV：把局部区域拉伸、复制成分段纹理，再让目标图填入。中点变形最大，首尾回到完整图片。
  - 为什么好看_研究判断：短时间破坏空间连续性，又在终点迅速恢复清晰，有适合换章节的“过门”感；图像内容不必改成特定题材。
  - 关键时刻_建议的影片节奏而非原站测量：建议0–20%稳定旧图、20–80%UV扭曲/换图、80–100%稳定新图；参数化只需两图、方向、幅度和时长。若实现，应优先使用O3已有明确MIT的GL Transitions机制。
  - evidence：
    - label：固定版本说明/源码
    - url：https://github.com/akella/webGLImageTransitions/blob/498d8fb48426de0a82fc5f6ad06736efc875a75b/README.md
    - label：原作者文章
    - url：https://tympanus.net/codrops/2019/11/05/creative-webgl-image-transitions/
  - review_scope：只读README/许可/关键源码与作者文字说明；未运行交互网页、未录屏、未下载示例图片。

### O4-05 Grid-to-Fullscreen Animations

- **ID**：O4-05
- **调查路**：O4
- **名称**：Grid-to-Fullscreen Animations
- **仓库**：https://github.com/Anemolo/GridToFullscreenAnimations
- **固定版本**：884fe4fbb1192a1013cccc51e580b4c14f9df480
- **许可**：
  - spdx：NOASSERTION
  - name：自定义Codrops条款（仅README；无独立LICENSE）
  - path：None
  - url：https://github.com/Anemolo/GridToFullscreenAnimations/blob/884fe4fbb1192a1013cccc51e580b4c14f9df480/README.md
  - scope：此许可记录只描述被链接的代码；本次只写自己的机制分析，不复制任何代码、图片、字体、音频或预览。
- **义务**：
  - attribution：False
  - share_alike：False
  - non_commercial：False
  - no_derivatives：False
  - note：无独立LICENSE且README另限制原样再分发/插件化，按计划排除资产入库；四布尔不足表达自定义限制，不代表可用。
- **可粘贴署名**：机制参考：Grid-to-Fullscreen Animations — Daniel Velasquez，https://tympanus.net/codrops/2019/05/22/creating-grid-to-fullscreen-animations-with-three-js/。本报告仅链接并以自己的话分析，未复制原作素材或代码。
- **署名位置**：研究说明/资产包设计出处（不是把参考作品署名伪装成获准分发）
- **风险**：
  - 示例图片/字体/依赖授权与代码分开；不抓取、不复制原站资产。
  - 代码无独立LICENSE；README自定义条款限制再分发，本次不采纳代码。
- **内容、格式、体积与预览**：
  - quantity：1
  - format：链接+原创机制说明
  - bytes：0
  - preview：https://tympanus.net/Tutorials/GridToFullscreenAnimations/
  - article：https://tympanus.net/codrops/2019/05/22/creating-grid-to-fullscreen-animations-with-three-js/
- **映射**：
  - 仅参考
- **产品线**：
  - explainer
  - showcase
- **适配等级**：D：仅参考，自写参数化机制；没有资产导入许可。
- **时间可寻址性**：不适用（仅参考）
- **运行环境**：网页原运行时未导入/未在r160验证；自己的实现再按render(t)合同重写。
- **维护证据**：
  - last_commit_at：2019-05-22T15:32:58+08:00
  - source：https://github.com/Anemolo/GridToFullscreenAnimations/commit/884fe4fbb1192a1013cccc51e580b4c14f9df480
  - checked_at：2026-10-02
- **结论**：备选（只看机制，代码包排除）
- **审查与适配说明**：
  - 发生了什么：缩略图匹配为一个平面，顶点按方向或距离的激活顺序翻转/变形，最终平面扩满全屏。局部顶点错时，而不是所有像素同步缩放。
  - 为什么好看_研究判断：“从证据图进入故事”有明确空间来源；从一个小图拉到全屏比任意黑场切镜更有联系。
  - 关键时刻_建议的影片节奏而非原站测量：先留出缩略图辨识期，再逐区域激活顶点，满屏时才交接下一场。计划可以只有一张图槽，不需要复制原站的整套网格布局。
  - evidence：
    - label：固定版本说明/源码
    - url：https://github.com/Anemolo/GridToFullscreenAnimations/blob/884fe4fbb1192a1013cccc51e580b4c14f9df480/README.md
    - label：原作者文章
    - url：https://tympanus.net/codrops/2019/05/22/creating-grid-to-fullscreen-animations-with-three-js/
  - review_scope：只读README/许可/关键源码与作者文字说明；未运行交互网页、未录屏、未下载示例图片。
