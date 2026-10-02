# O1｜炫酷开场机制调查

核验日期：2026-10-02。范围依据附件《开源资产调查计划》v1，全部288行已读。本路只调查，不接纳资产、复制第三方文件进交付仓库、制作完整视频或推送仓库。公开GitHub源码/版本/许可按固定引用读审；未登录、未使用Cookie、未付费。

## 结论

先试五条：粒子聚合、冻结网络点亮、R0银河、照片2.5D视差、中文立体标题。它们对应13条JSON候选中的5个全路“首推”；另外6个家族各自仍有唯一首推实现路线，但全路优先级为“备选”。11个家族共28个实现入口，其中同仓库不同入口明确标注，不冒充独立项目。额外2个排除项也占15条上限。

最重要的区别：这里推荐的是“可改造路线”，不是宣称网上demo可直接入库。多数原demo有RAF、系统时钟、交互平滑、无seed随机或CDN，必须在适配时剥离。原版与改造后的seekability分别说明；未经浏览器测试的内容全部标为源码审查/工程推断。

## 证据与版本口径

- 基础引擎：[Three.js r160](https://github.com/mrdoob/three.js/tree/d04539a76736ff500cae883d6a38b3dd8643c548)，tag指向commit `d04539a76736ff500cae883d6a38b3dd8643c548`，commit时间2023-12-22T12:31:45Z；已读该版本[LICENSE](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/LICENSE)，版权2010–2023，MIT
- 当前维护快照另列，不混同冻结版本：Three.js默认分支HEAD `633ce03810d62bd161121a88142e979e77cc69c0`，最后commit 2026-10-02T10:41:36Z。它已是0.186.0开发版，绝不可用当前文档/API替代r160
- R0来自官方HyperFrames `8aefd91bf82c687222082a80a3c5845ff37e6ca6`，最后commit 2026-10-02T12:48:06Z；代码Apache-2.0，附属素材逐项另授权。引用R0现有机制是为了避免重复造资产
- 所有精确日期取公开Git commit/API返回的committer日期，不用GitHub相对时间、“最近活跃”或仓库pushed_at代替。非UTC原始时区在候选中保留
- 图预览仅链接原仓库；未保存、抓取或再发布截图。无预览图的入口提供源码本身，不能凭此宣称视觉验收完成
- 下文GPU低/中/高全部是工程定性估计，**不是测量值**。没有FPS、GPU毫秒、显存实测；实际受像素数、DPR、材质、透明过绘、后期与输出画幅影响

## 所有路线共用的离线与时间合同

1. prepare固定seed、输入顺序、字形/图片/模型/布局表、相机参数和依赖版本；等待所有图片解码、字体/worker完成、材质编译后才进入可渲染状态。随机只发生在prepare或使用可寻址hash(seed,id,t)
2. render(t)从原始输入重新赋值完整场景状态。q=clamp((t-start)/duration,0,1)，不使用Date.now、performance.now、Clock.getDelta、RAF自动推进、上帧position/quaternion或系统输入
3. 解析noise(seed,id,t)可用；position+=curl(position,t)*dt不纯。弹簧解析解可用；lerp(current,target,k)、速度积分、物理world.step、force.tick在runtime不可用
4. 可烘焙路线：固定初态、固定步长、solver/依赖版本与采样表；render(t)只查表与插值。只冻结seed不保证跨平台物理位级一致，须冻结烘焙结果hash
5. 离屏renderTarget不天然有状态，也不天然无状态。所有离屏目标必须由同一个t重建/清空，不读前一次render(t)留下的纹理；portal与feedback要特别检查
6. 按2–6秒duration伸缩事件相位；9:16与16:9分别求相机/安全区，不能仅做中心裁切。颜色从主题token取，标题/图标/照片均为插槽。字体/形状/截图替换不得触发新代码路径
7. 只使用宿主唯一r160实例。对旧版显式改Geometry→BufferGeometry、encoding→colorSpace；对新版不要无审查降版本。peer范围覆盖r160只是必要线索，不是运行测试
8. 准备后禁网络；CDN脚本、远程字体、地理/分子API、HDR/模型解码器需全部冻入本地闭包。Web Worker可在prepare运行，不能在渲染中异步改画面

## 必做但本次未执行的验收

用同一seed/插槽分别渲染 t=[0,0.25D,0.7D,D]、倒序、随机序列与重复同t，比较同浏览器/同GPU的像素hash或预先定义的容差；再跨seed复现、强制断网、cold-start重载。检查framebuffer清理、未ready是否报错、末帧所有实例复位、字体缺字/中文换行、两画幅安全区、GPU资源释放与多实例。跨GPU/驱动浮点差异不承诺逐像素一致，验收环境应冻结。

## O1-01｜粒子聚合成标题 / 图标 / logo

**全路判断：首推：固定seed的源点与目标点 + 直接求值的顶点shader**

家族首推路线：固定seed的源点与目标点 + 直接求值的顶点shader

- 对应：module/hook；card可选、explainer、showcase
- 适配：B，去demo外壳并参数化；所需合同补项见末节
- 改造后时间分类：纯函数
- 风格覆盖：科技感、克制冷光、电影感；大圆点/高饱和可综艺
- GPU定性估计（未实测）：中；粒子数影响顶点吞吐，大片半透明点与bloom导致像素过绘，不能用点数单独估FPS
- 插槽/参数：title/icon/image、seed、particleBudget、scatterRadius、palette、duration

### 实现参考 1：[ particle-morph 多形态粒子 vertex shader ](https://github.com/mmdalipour/particle-morph/blob/f26837607e83c82b50b5306d109c79c1e19c9e00/src/shaders/particleMultiShapeMorph.vert.glsl)

- 冻结：`f26837607e83c82b50b5306d109c79c1e19c9e00`
- 许可：[MIT / src/LICENSE](https://github.com/mmdalipour/particle-morph/blob/f26837607e83c82b50b5306d109c79c1e19c9e00/src/LICENSE)；Mohammad Alipour, Copyright (c) 2025
- 资产边界：只核验该代码；示例中的图片、字体、模型、数据不随代码许可自动获准
- [仓库最后commit](https://github.com/mmdalipour/particle-morph/commit/f26837607e83c82b50b5306d109c79c1e19c9e00)：2025-11-05T15:20:51+03:30；冻结版本commit日期：2025-11-05T15:20:51+03:30
- 时间、r160与依赖检查：顶点位置由固定 attributes、uProgress、uTime 直接求值；名为 dampingFactor 的属性在 shader 中只是系数，并非逐帧积分。但 React wrapper 使用 state.clock、0.001更新阈值、交互旋转，不能原样接宿主；须移植 shader、去阈值并赋外部 t。src/package.json 的 three peer ^0.160.0 与 r160 相合，只是声明，未浏览器实测。

### 实现参考 2：[ r160 custom attributes Points ](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/webgl_custom_attributes_points.html)

- 冻结：`d04539a76736ff500cae883d6a38b3dd8643c548`
- 许可：[MIT / LICENSE](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/LICENSE)；three.js authors, Copyright © 2010-2023
- 资产边界：只核验该代码；示例中的图片、字体、模型、数据不随代码许可自动获准
- [仓库最后commit](https://github.com/mrdoob/three.js/commit/633ce03810d62bd161121a88142e979e77cc69c0)：2026-10-02T10:41:36Z；冻结版本commit日期：2023-12-22T12:31:45Z
- 时间、r160与依赖检查：固定粒子属性与正弦 size 示例；Date.now 改成外部 t，初始化 Math.random 换固定 seed，自带 RAF移除。点精灵图片不入选，改解析圆点。
- [原仓库预览](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/screenshots/webgl_custom_attributes_points.jpg)

### 实现参考 3：[ R0 particle-text-dissolve ](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/particle-text-dissolve/particle-text-dissolve.html)

- 冻结：`8aefd91bf82c687222082a80a3c5845ff37e6ca6`
- 许可：[Apache-2.0 / LICENSE](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/LICENSE)；HeyGen / HyperFrames contributors
- 资产边界：只核验该代码；示例中的图片、字体、模型、数据不随代码许可自动获准
- [仓库最后commit](https://github.com/heygen-com/hyperframes/commit/8aefd91bf82c687222082a80a3c5845ff37e6ca6)：2026-10-02T12:48:06Z；冻结版本commit日期：2026-10-02T12:48:06Z
- 时间、r160与依赖检查：Canvas2D字形位图→seed表→paint(t)，不是3D粒子；可作低成本同机制基线。事件抑制的 seek 必须另调 paint(t)，或确证 seek(t,false)；GSAP CDN要本地化。

### 适配决策

目标形状先在prepare阶段采样，保持source/target相同数量与稳定对应。q=clamp((t-start)/duration)，位置为mix(source,target,ease(q))+envelope(q)*noise(seed,id,t)。noise直接查询才无状态；x+=curl(x,t)*dt仍是积分，应排除或烘焙。标题可从合法字体字形/清洗SVG取点，禁止在每帧依赖canvas字体异步变化。

9:16目标取纵向安全框，16:9可横向标题+侧向粒子场；不要仅裁切同一相机。参数换题材不应重写采样逻辑。

### 义务与可复制署名

首推代码义务：attribution=true，SA=false，NC=false，ND=false。保留相应许可全文/免责；Apache改动文件须显著标识，若源含NOTICE则随附。视频简介不是替代代码分发许可文件。附属图片/字体/数据如被另选，义务另加，不能沿用上述四布尔值。

Mohammad Alipour, Copyright (c) 2025：particle-morph 多形态粒子 vertex shader，https://github.com/mmdalipour/particle-morph/blob/f26837607e83c82b50b5306d109c79c1e19c9e00/src/shaders/particleMultiShapeMorph.vert.glsl，MIT；three.js authors, Copyright © 2010-2023：r160 custom attributes Points，https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/webgl_custom_attributes_points.html，MIT；HeyGen / HyperFrames contributors：R0 particle-text-dissolve，https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/components/particle-text-dissolve/particle-text-dissolve.html，Apache-2.0。未改造版：保留原代码版权与许可全文。后续实际改造版附加：已将交互/自带时钟改造为离线外部时间驱动，并按本作品标题与主题调整参数。仅在上述改动确实发生时使用改造版。

署名位置：资产包说明和THIRD_PARTY_NOTICES；视频简介可加实现来源。这里只提供条件模板，本调查没有实际改造或分发源码。

## O1-02｜地球 / 地图飞入 / 城市弧线 / 数据点

**全路判断：备选：无国界地球或合规底图 + r160球面坐标/弧线 + 外部t揭示**

家族首推路线：无国界地球或合规底图 + r160球面坐标/弧线 + 外部t揭示

- 对应：module/hook；card可选、explainer、showcase
- 适配：B，去demo外壳并参数化；所需合同补项见末节
- 改造后时间分类：纯函数
- 风格覆盖：克制、科技、电影；配色可更活泼，不适合无边界把戏冒充新闻地图
- GPU定性估计（未实测）：中；球体与少量弧线低中，高分辨率地表图/大气/阴影/大量tube会升高
- 插槽/参数：locations、arcs、earthTexture、mapComplianceEvidence、palette、cameraKeyframes、duration

### 实现参考 1：[ three-globe 弧线层 ](https://github.com/vasturiano/three-globe/blob/c4e4f1fc24572161bea3a4dbfc5abed78b46ee09/src/layers/arcs.js)

- 冻结：`c4e4f1fc24572161bea3a4dbfc5abed78b46ee09`
- 许可：[MIT / LICENSE](https://github.com/vasturiano/three-globe/blob/c4e4f1fc24572161bea3a4dbfc5abed78b46ee09/LICENSE)；Vasco Asturiano, Copyright (c) 2019
- 资产边界：代码MIT；地球贴图、行政边界、城市/航线数据须独立许可与合规审查
- [仓库最后commit](https://github.com/vasturiano/three-globe/commit/c4e4f1fc24572161bea3a4dbfc5abed78b46ee09)：2026-09-30T02:27:57Z；冻结版本commit日期：2026-09-30T02:27:57Z
- 时间、r160与依赖检查：弧线构形可提取；FrameTicker 用 timeDelta 累加 dashTranslate、Tween 维护前态。原样不合格；静态弧线 + 外部t设置 dash phase/显隐是可行改造。peer three>=0.154覆盖r160，但当前开发依赖0.186.1，未证明所有代码在r160通过。

### 实现参考 2：[ three-globe 路径/点序列示例 ](https://github.com/vasturiano/three-globe/blob/c4e4f1fc24572161bea3a4dbfc5abed78b46ee09/example/paths/index.html)

- 冻结：`c4e4f1fc24572161bea3a4dbfc5abed78b46ee09`
- 许可：[MIT / LICENSE](https://github.com/vasturiano/three-globe/blob/c4e4f1fc24572161bea3a4dbfc5abed78b46ee09/LICENSE)；Vasco Asturiano, Copyright (c) 2019
- 资产边界：代码MIT；示例图片不视为MIT可收
- [仓库最后commit](https://github.com/vasturiano/three-globe/commit/c4e4f1fc24572161bea3a4dbfc5abed78b46ee09)：2026-09-30T02:27:57Z；冻结版本commit日期：2026-09-30T02:27:57Z
- 时间、r160与依赖检查：参考经纬度→球面路径与paths数据接口；去外部脚本、随机路径、默认时钟和相机交互。与arcs是同仓库两条不同实现入口，并非两家独立验证。

### 适配决策

用经纬度转单位球位置，球面路径在prepare阶段建几何；head progress/dash offset直接由q求值。关闭three-globe的transitionDuration、arcDashAnimateTime与初始globe动画，或只抽取几何算法自己维护material。经纬度端点同点/近对跖必须定义fallback，避免slerp数值问题。

中国边界没有合规来源或用户批准标准地图时标不可用；“去掉国界线”不自动证明所有中国相关地理表达合规。首阶段可只接受抽象全球球体、不展示争议边界的概念图，但仍单独审核。

### 义务与可复制署名

首推代码义务：attribution=true，SA=false，NC=false，ND=false。保留相应许可全文/免责；Apache改动文件须显著标识，若源含NOTICE则随附。视频简介不是替代代码分发许可文件。附属图片/字体/数据如被另选，义务另加，不能沿用上述四布尔值。

Vasco Asturiano, Copyright (c) 2019：three-globe 弧线层，https://github.com/vasturiano/three-globe/blob/c4e4f1fc24572161bea3a4dbfc5abed78b46ee09/src/layers/arcs.js，MIT。未改造版：保留原代码版权与许可全文。后续实际改造版附加：已将交互/自带时钟改造为离线外部时间驱动，并按本作品标题与主题调整参数。仅在上述改动确实发生时使用改造版。

署名位置：资产包说明和THIRD_PARTY_NOTICES；视频简介可加实现来源。这里只提供条件模板，本调查没有实际改造或分发源码。

## O1-03｜网络 / 神经网络 / 知识图谱

**全路判断：首推：d3-force-3d 固定seed离线布局 + r160 Points/LineSegments逐节点点亮**

家族首推路线：d3-force-3d 固定seed离线布局 + r160 Points/LineSegments逐节点点亮

- 对应：module/hook；card可选、explainer、showcase
- 适配：B，去demo外壳并参数化；所需合同补项见末节
- 改造后时间分类：可烘焙
- 风格覆盖：克制、科技、电影；综艺可改弹跳节奏但保持可读
- GPU定性估计（未实测）：低到中；节点/边合批较省，大量透明线重叠和文字标签会升高
- 插槽/参数：nodes、edges、seed、revealOrder、layoutIterations、palette、duration

### 实现参考 1：[ d3-force-3d 冻结布局 ](https://github.com/vasturiano/d3-force-3d/blob/263b3bfc37578e541a7d7e59dbb32d026d66fa38/src/simulation.js)

- 冻结：`263b3bfc37578e541a7d7e59dbb32d026d66fa38`
- 许可：[MIT / LICENSE](https://github.com/vasturiano/d3-force-3d/blob/263b3bfc37578e541a7d7e59dbb32d026d66fa38/LICENSE)；Vasco Asturiano, Copyright (c) 2017
- 资产边界：只核验该代码；示例中的图片、字体、模型、数据不随代码许可自动获准
- [仓库最后commit](https://github.com/vasturiano/d3-force-3d/commit/263b3bfc37578e541a7d7e59dbb32d026d66fa38)：2025-04-09T19:05:29Z；冻结版本commit日期：2025-04-09T19:05:29Z
- 时间、r160与依赖检查：simulation 构造即开启timer；立即.stop()，固定节点/边排序、numDimensions、randomSource(seed)，用固定tick次数产生位置，冻结结果。randomSource接口和lcg.js已核查。布局是数值积分，不是render(t)纯函数；预计算后查表。无Three运行时耦合。

### 实现参考 2：[ r160 drawrange 节点连线 ](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/webgl_buffergeometry_drawrange.html)

- 冻结：`d04539a76736ff500cae883d6a38b3dd8643c548`
- 许可：[MIT / LICENSE](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/LICENSE)；three.js authors, Copyright © 2010-2023
- 资产边界：只核验该代码；示例中的图片、字体、模型、数据不随代码许可自动获准
- [仓库最后commit](https://github.com/mrdoob/three.js/commit/633ce03810d62bd161121a88142e979e77cc69c0)：2026-10-02T10:41:36Z；冻结版本commit日期：2023-12-22T12:31:45Z
- 时间、r160与依赖检查：原示例每帧 position += velocity 且边界反弹，明确有状态；只借 Points+LineSegments 合批/索引与连线构建，把运动换冻结图布局、显隐progress或解析轨迹。
- [原仓库预览](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/screenshots/webgl_buffergeometry_drawrange.jpg)

### 适配决策

layout=stop+固定N次tick，序列化位置和边表；运行时仅由q更新节点scale/emissive与线段drawRange。需要生长中的布局时，固定采样时刻烘焙全部pose再插值，不能让d3计时器继续运行。节点次序、链接端点和浮点依赖版本也要冻结。

对应已规划graph-grow，本调查提供实现参考不另造同义镜头。9:16层叠或中心放射，16:9左到右传播；布局分别生成，避免标签碰撞。

### 义务与可复制署名

首推代码义务：attribution=true，SA=false，NC=false，ND=false。保留相应许可全文/免责；Apache改动文件须显著标识，若源含NOTICE则随附。视频简介不是替代代码分发许可文件。附属图片/字体/数据如被另选，义务另加，不能沿用上述四布尔值。

Vasco Asturiano, Copyright (c) 2017：d3-force-3d 冻结布局，https://github.com/vasturiano/d3-force-3d/blob/263b3bfc37578e541a7d7e59dbb32d026d66fa38/src/simulation.js，MIT；three.js authors, Copyright © 2010-2023：r160 drawrange 节点连线，https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/webgl_buffergeometry_drawrange.html，MIT。未改造版：保留原代码版权与许可全文。后续实际改造版附加：已将交互/自带时钟改造为离线外部时间驱动，并按本作品标题与主题调整参数。仅在上述改动确实发生时使用改造版。

署名位置：资产包说明和THIRD_PARTY_NOTICES；视频简介可加实现来源。这里只提供条件模板，本调查没有实际改造或分发源码。

## O1-04｜星空跃迁 / 星系 / 行星

**全路判断：首推：以R0 spiral-galaxy解析轨道为基线，移植到固定r160**

家族首推路线：以R0 spiral-galaxy解析轨道为基线，移植到固定r160

- 对应：module/hook；card可选、explainer、showcase
- 适配：B，去demo外壳并参数化；所需合同补项见末节
- 改造后时间分类：纯函数
- 风格覆盖：电影、科技；压低密度与色彩可克制，高彩高速度可综艺
- GPU定性估计（未实测）：中到高；点精灵过绘、bloom与大雾片是主要成本，几何点本身未必是瓶颈
- 插槽/参数：seed、starCount、armCount、twist、speed、title、palette、duration

### 实现参考 1：[ R0 spiral-galaxy ](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/spiral-galaxy/spiral-galaxy.html)

- 冻结：`8aefd91bf82c687222082a80a3c5845ff37e6ca6`
- 许可：[Apache-2.0 / LICENSE](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/LICENSE)；HeyGen / HyperFrames contributors
- 资产边界：代码Apache-2.0；自生成粒子不引入星空照片，仍须核验具体依赖通知
- [仓库最后commit](https://github.com/heygen-com/hyperframes/commit/8aefd91bf82c687222082a80a3c5845ff37e6ca6)：2026-10-02T12:48:06Z；冻结版本commit日期：2026-10-02T12:48:06Z
- 时间、r160与依赖检查：源代码为20000个seeded sprite/解析uTime轨道；r147/GSAP CDN，需移植r160。20k是源码配置，不是性能承诺；setter draw(t)支持事件抑制seek。

### 实现参考 2：[ threejs-galaxy 参数银河 ](https://github.com/ggwzrd/threejs-galaxy/blob/1ec3a3f59667d1d7355c3df81f29c451b5523f76/src/Galaxy.ts)

- 冻结：`1ec3a3f59667d1d7355c3df81f29c451b5523f76`
- 许可：[MIT / LICENCE.txt](https://github.com/ggwzrd/threejs-galaxy/blob/1ec3a3f59667d1d7355c3df81f29c451b5523f76/LICENCE.txt)；ggwzrd, Copyright © 2022
- 资产边界：代码MIT；README说不提供通用粒子纹理，src/assets示例纹理没有被本调查单独批准
- [仓库最后commit](https://github.com/ggwzrd/threejs-galaxy/commit/1ec3a3f59667d1d7355c3df81f29c451b5523f76)：2024-01-29T11:35:08+01:00；冻结版本commit日期：2024-01-29T11:35:08+01:00
- 时间、r160与依赖检查：初始化Math.random且animate中 time += 1；要固定seed、直接写time(t)。原依赖three ^0.145.0并用sRGBEncoding/outputEncoding，r160须改outputColorSpace/SRGBColorSpace；不能直接复用整包。

### 实现参考 3：[ r160 Points 星空精灵 ](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/webgl_points_sprites.html)

- 冻结：`d04539a76736ff500cae883d6a38b3dd8643c548`
- 许可：[MIT / LICENSE](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/LICENSE)；three.js authors, Copyright © 2010-2023
- 资产边界：只核验该代码；示例中的图片、字体、模型、数据不随代码许可自动获准
- [仓库最后commit](https://github.com/mrdoob/three.js/commit/633ce03810d62bd161121a88142e979e77cc69c0)：2026-10-02T10:41:36Z；冻结版本commit日期：2023-12-22T12:31:45Z
- 时间、r160与依赖检查：多层Points；Date.now替换外部t、随机旋转固定seed、相机不可继续按鼠标渐近插值。自画sprite代替示例雪花图片。
- [原仓库预览](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/screenshots/webgl_points_sprites.jpg)

### 适配决策

固定分布表后用phase=phase0+omega*t求轨道；跃迁以fract(z0-speed*t)包裹位置并用解析拉长，不积累position.z。相机固定路径，随机闪烁用hash(id,floor(t*k))或连续解析noise；需要无闪变用平滑插值。

R0已覆盖银河，不重复引入旧galaxy全栈。若行星需要真实表面纹理走O2逐文件许可；程序星点不需要NASA照片。

### 义务与可复制署名

首推代码义务：attribution=true，SA=false，NC=false，ND=false。保留相应许可全文/免责；Apache改动文件须显著标识，若源含NOTICE则随附。视频简介不是替代代码分发许可文件。附属图片/字体/数据如被另选，义务另加，不能沿用上述四布尔值。

HeyGen / HyperFrames contributors：R0 spiral-galaxy，https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/spiral-galaxy/spiral-galaxy.html，Apache-2.0；ggwzrd, Copyright © 2022：threejs-galaxy 参数银河，https://github.com/ggwzrd/threejs-galaxy/blob/1ec3a3f59667d1d7355c3df81f29c451b5523f76/src/Galaxy.ts，MIT；three.js authors, Copyright © 2010-2023：r160 Points 星空精灵，https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/webgl_points_sprites.html，MIT。未改造版：保留原代码版权与许可全文。后续实际改造版附加：已将交互/自带时钟改造为离线外部时间驱动，并按本作品标题与主题调整参数。仅在上述改动确实发生时使用改造版。

署名位置：资产包说明和THIRD_PARTY_NOTICES；视频简介可加实现来源。这里只提供条件模板，本调查没有实际改造或分发源码。

## O1-05｜DNA / 细胞 / 分子

**全路判断：备选：r160球/柱实例化程序双螺旋；科学分子先冻结合法坐标数据**

家族首推路线：r160球/柱实例化程序双螺旋；科学分子先冻结合法坐标数据

- 对应：module/hook；card可选、explainer、showcase
- 适配：B，去demo外壳并参数化；所需合同补项见末节
- 改造后时间分类：纯函数
- 风格覆盖：克制、科技、电影；卡通细胞可综艺
- GPU定性估计（未实测）：低到中；球柱实例批次较省，透明膜、体积渲染/表面生成会明显增重
- 插槽/参数：mode、sequenceOrStructureId、atomsAndBonds、turns、pitch、radius、palette、duration

### 实现参考 1：[ r160 PDB 球棍结构 ](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/webgl_loader_pdb.html)

- 冻结：`d04539a76736ff500cae883d6a38b3dd8643c548`
- 许可：[MIT / LICENSE](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/LICENSE)；three.js authors, Copyright © 2010-2023
- 资产边界：只核验该代码；示例中的图片、字体、模型、数据不随代码许可自动获准
- [仓库最后commit](https://github.com/mrdoob/three.js/commit/633ce03810d62bd161121a88142e979e77cc69c0)：2026-10-02T10:41:36Z；冻结版本commit日期：2023-12-22T12:31:45Z
- 时间、r160与依赖检查：PDBLoader 读取原子与化学键，sphere/cylinder几何；可先构形后直接由t更新组transform/键draw range。不得从“代码MIT”推断PDB文件的来源许可。
- [原仓库预览](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/screenshots/webgl_loader_pdb.jpg)

### 实现参考 2：[ 3Dmol.js 分子表示与坐标帧 ](https://github.com/3dmol/3Dmol.js/blob/cf6b68429dd9f435ba004d172c0616a8fe124206/src/GLModel.ts)

- 冻结：`cf6b68429dd9f435ba004d172c0616a8fe124206`
- 许可：[BSD-3-Clause; bundled MIT notices / LICENSE](https://github.com/3dmol/3Dmol.js/blob/cf6b68429dd9f435ba004d172c0616a8fe124206/LICENSE)；University of Pittsburgh and contributors, Copyright (c) 2014
- 资产边界：LICENSE 主体BSD-3-Clause，内嵌GLmol、旧Three、jQuery通知要保留；分子数据与示例结构版权另核验
- [仓库最后commit](https://github.com/3dmol/3Dmol.js/commit/cf6b68429dd9f435ba004d172c0616a8fe124206)：2026-09-11T21:32:35-04:00；冻结版本commit日期：2026-09-11T21:32:35-04:00
- 时间、r160与依赖检查：球棍/卡通与setFrame资料可用于结构表达参考；自有渲染器不是可直接塞进Three r160的Object3D插件。若采用只在预处理提取坐标与键，渲染用r160；不用其默认动画/在线结构下载。

### 适配决策

DNA示意双螺旋可直接用sin(theta+phase(t))/cos，碱基连接端点由相同参数生成；“示意”不假装精确结构。真实分子freeze坐标、键、元素与来源，只对整体/选定原子做解析显隐。3Dmol仅作数据/表示参考，避免带入第二套renderer。

真实结构记录PDB/模型ID、作者/论文、下载来源、版本、许可与是否计算预测；源码LICENSE不会授权外部RCSB/AlphaFold文件。示例模型来源不足就不接纳数据。

### 义务与可复制署名

首推代码义务：attribution=true，SA=false，NC=false，ND=false。保留相应许可全文/免责；Apache改动文件须显著标识，若源含NOTICE则随附。视频简介不是替代代码分发许可文件。附属图片/字体/数据如被另选，义务另加，不能沿用上述四布尔值。

three.js authors, Copyright © 2010-2023：r160 PDB 球棍结构，https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/webgl_loader_pdb.html，MIT；University of Pittsburgh and contributors, Copyright (c) 2014：3Dmol.js 分子表示与坐标帧，https://github.com/3dmol/3Dmol.js/blob/cf6b68429dd9f435ba004d172c0616a8fe124206/src/GLModel.ts，BSD-3-Clause; bundled MIT notices。未改造版：保留原代码版权与许可全文。后续实际改造版附加：已将交互/自带时钟改造为离线外部时间驱动，并按本作品标题与主题调整参数。仅在上述改动确实发生时使用改造版。

署名位置：资产包说明和THIRD_PARTY_NOTICES；视频简介可加实现来源。这里只提供条件模板，本调查没有实际改造或分发源码。

## O1-06｜3D柱地形 / K线 / 硬币 / 数据城市

**全路判断：备选：r160 InstancedMesh + 稳定数据表 + 基底锚定scale(t)**

家族首推路线：r160 InstancedMesh + 稳定数据表 + 基底锚定scale(t)

- 对应：module/hook；card可选、explainer、showcase
- 适配：B，去demo外壳并参数化；所需合同补项见末节
- 改造后时间分类：纯函数
- 风格覆盖：克制、财经科技、电影；硬币弹跳可综艺
- GPU定性估计（未实测）：低到中；实例化降低drawcalls；多材质镜面币、阴影/反射会升至高
- 插槽/参数：values/OHLC、labels、seed、layout、barScale、coinStyle、palette、duration

### 实现参考 1：[ r160 InstancedMesh 数据柱群 ](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/webgl_instancing_dynamic.html)

- 冻结：`d04539a76736ff500cae883d6a38b3dd8643c548`
- 许可：[MIT / LICENSE](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/LICENSE)；three.js authors, Copyright © 2010-2023
- 资产边界：只核验该代码；示例中的图片、字体、模型、数据不随代码许可自动获准
- [仓库最后commit](https://github.com/mrdoob/three.js/commit/633ce03810d62bd161121a88142e979e77cc69c0)：2026-10-02T10:41:36Z；冻结版本commit日期：2023-12-22T12:31:45Z
- 时间、r160与依赖检查：每帧从格点+time重建matrix，适合数据柱/硬币实例；把示例加载的Suzanne几何改自建Box/Cylinder，避免额外模型来源。Date.now→t，移除GUI和RAF。
- [原仓库预览](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/screenshots/webgl_instancing_dynamic.jpg)

### 实现参考 2：[ threex.proceduralcity 程序城市 ](https://github.com/jeromeetienne/threex.proceduralcity/blob/6ed3875c16eb65c1a5a023ce6ba2d492541a531a/threex.proceduralcity.js)

- 冻结：`6ed3875c16eb65c1a5a023ce6ba2d492541a531a`
- 许可：[MIT / MIT-LICENSE.txt](https://github.com/jeromeetienne/threex.proceduralcity/blob/6ed3875c16eb65c1a5a023ce6ba2d492541a531a/MIT-LICENSE.txt)；Jerome Etienne, Copyright (c) 2011
- 资产边界：MIT-LICENSE.txt只适用代码。images/LICENSE.txt：lensflare0–3为CC BY-NC-SA3.0；hexangle.png为CC0。本首推不使用这些图片，若以后复用镜头耀斑必须NC+SA单独标记。
- [仓库最后commit](https://github.com/jeromeetienne/threex.proceduralcity/commit/6ed3875c16eb65c1a5a023ce6ba2d492541a531a)：2014-01-25T20:53:04Z；冻结版本commit日期：2014-01-25T20:53:04Z
- 时间、r160与依赖检查：古老CubeGeometry/Geometry/GeometryUtils.merge/VertexColors 已不适用于r160；只提取“分布+高度+窗口程序纹理”机制，重写InstancedMesh/BufferGeometry，固定seed。

### 适配决策

柱高h=target*ease(clamp(q-delay_i))，中心y=h/2确保从底部生长；K线实体与wick用显式OHLC映射，不用随机金融数据伪装事实。硬币使用无品牌圆柱和解析旋转/抛物线。程序窗口纹理准备时生成，seed固定。

旧proceduralcity仅借机制，Geometry API不可r160运行。币面品牌/货币图像另审；用“数据城市”不能隐去数值坐标或夸大差异。

### 义务与可复制署名

首推代码义务：attribution=true，SA=false，NC=false，ND=false。保留相应许可全文/免责；Apache改动文件须显著标识，若源含NOTICE则随附。视频简介不是替代代码分发许可文件。附属图片/字体/数据如被另选，义务另加，不能沿用上述四布尔值。

three.js authors, Copyright © 2010-2023：r160 InstancedMesh 数据柱群，https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/webgl_instancing_dynamic.html，MIT；Jerome Etienne, Copyright (c) 2011：threex.proceduralcity 程序城市，https://github.com/jeromeetienne/threex.proceduralcity/blob/6ed3875c16eb65c1a5a023ce6ba2d492541a531a/threex.proceduralcity.js，MIT。未改造版：保留原代码版权与许可全文。后续实际改造版附加：已将交互/自带时钟改造为离线外部时间驱动，并按本作品标题与主题调整参数。仅在上述改动确实发生时使用改造版。

署名位置：资产包说明和THIRD_PARTY_NOTICES；视频简介可加实现来源。这里只提供条件模板，本调查没有实际改造或分发源码。

## O1-07｜隧道 / 传送门 / 穿越

**全路判断：备选：r160 TubeGeometry + 预生成Frenet frame + camera(q)**

家族首推路线：r160 TubeGeometry + 预生成Frenet frame + camera(q)

- 对应：module/hook；card可选、explainer、showcase
- 适配：B，去demo外壳并参数化；所需合同补项见末节
- 改造后时间分类：纯函数
- 风格覆盖：科技、电影、综艺；轻光线慢运动可克制
- GPU定性估计（未实测）：中；普通管道低中，体积raymarch/多层透明/递归portal高
- 插槽/参数：path、radius、pattern、cameraFov、speedCurve、palette、duration

### 实现参考 1：[ r160 TubeGeometry 样条穿行 ](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/webgl_geometry_extrude_splines.html)

- 冻结：`d04539a76736ff500cae883d6a38b3dd8643c548`
- 许可：[MIT / LICENSE](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/LICENSE)；three.js authors, Copyright © 2010-2023
- 资产边界：只核验该代码；示例中的图片、字体、模型、数据不随代码许可自动获准
- [仓库最后commit](https://github.com/mrdoob/three.js/commit/633ce03810d62bd161121a88142e979e77cc69c0)：2026-10-02T10:41:36Z；冻结版本commit日期：2023-12-22T12:31:45Z
- 时间、r160与依赖检查：getPointAt(t)+预生成切线/法线，视点与朝向由t求值；去Date.now循环，改2–6s归一化进度与显式相机姿态。这是最低风险首推。
- [原仓库预览](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/screenshots/webgl_geometry_extrude_splines.jpg)

### 实现参考 2：[ r160 双入口portal ](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/webgl_portal.html)

- 冻结：`d04539a76736ff500cae883d6a38b3dd8643c548`
- 许可：[MIT / LICENSE](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/LICENSE)；three.js authors, Copyright © 2010-2023
- 资产边界：只核验该代码；示例中的图片、字体、模型、数据不随代码许可自动获准
- [仓库最后commit](https://github.com/mrdoob/three.js/commit/633ce03810d62bd161121a88142e979e77cc69c0)：2026-10-02T10:41:36Z；冻结版本commit日期：2023-12-22T12:31:45Z
- 时间、r160与依赖检查：源码renderPortal只隐藏thisPortal，另一个portal仍显示其renderTarget；存在读取旧portal纹理的风险，不能声称stock示例逐帧无状态。改为每个offscreen pass隐藏双方portal，或每次t完整计算固定深度递归，并清除所有目标。
- [原仓库预览](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/screenshots/webgl_portal.jpg)

### 实现参考 3：[ R0 vfx-portal ](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/vfx-portal/vfx-portal.html)

- 冻结：`8aefd91bf82c687222082a80a3c5845ff37e6ca6`
- 许可：[Apache-2.0 / LICENSE](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/LICENSE)；HeyGen / HyperFrames contributors
- 资产边界：Apache-2.0代码；附带图像和外部资源未单独批准
- [仓库最后commit](https://github.com/heygen-com/hyperframes/commit/8aefd91bf82c687222082a80a3c5845ff37e6ca6)：2026-10-02T12:48:06Z；冻结版本commit日期：2026-10-02T12:48:06Z
- 时间、r160与依赖检查：基线three0.147.0；本路仅登记既有入口、无重复资产建议。源逐帧状态仍需R0核验，不把视觉上的门户效果等同于递归renderTarget。

### 适配决策

样条几何与frame在prepare阶段固定；每次t直接算相机位置、up和lookAt。闭合路径起终点姿态要连续；不闭合路径限制q避免环跳。门户若需离屏画面每帧清空/重算，绝不复用上帧内容。

高速度/窄FOV变化容易晕；2–6秒中给标题稳定停留。按两种画幅重新设安全边缘，门户圈不能挤掉中文标题。

### 义务与可复制署名

首推代码义务：attribution=true，SA=false，NC=false，ND=false。保留相应许可全文/免责；Apache改动文件须显著标识，若源含NOTICE则随附。视频简介不是替代代码分发许可文件。附属图片/字体/数据如被另选，义务另加，不能沿用上述四布尔值。

three.js authors, Copyright © 2010-2023：r160 TubeGeometry 样条穿行，https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/webgl_geometry_extrude_splines.html，MIT；HeyGen / HyperFrames contributors：R0 vfx-portal，https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/vfx-portal/vfx-portal.html，Apache-2.0。未改造版：保留原代码版权与许可全文。后续实际改造版附加：已将交互/自带时钟改造为离线外部时间驱动，并按本作品标题与主题调整参数。仅在上述改动确实发生时使用改造版。

署名位置：资产包说明和THIRD_PARTY_NOTICES；视频简介可加实现来源。这里只提供条件模板，本调查没有实际改造或分发源码。

## O1-08｜3D手机 / 电脑 / 悬浮UI面板

**全路判断：备选：r160圆角几何自建设备壳 + Plane图片插槽 + 解析相机/姿态**

家族首推路线：r160圆角几何自建设备壳 + Plane图片插槽 + 解析相机/姿态

- 对应：module/hook；card可选、explainer、showcase
- 适配：B，去demo外壳并参数化；所需合同补项见末节
- 改造后时间分类：纯函数
- 风格覆盖：克制、科技、电影；弹性入场可综艺
- GPU定性估计（未实测）：低到中；标准壳体+一张屏幕贴图省成本，玻璃折射、实时renderTexture、HDR镜面提高成本
- 插槽/参数：screenshot、screenAspect、fit/cover、deviceShape、bezel、background、palette、duration

### 实现参考 1：[ r160 GLTFLoader 场景装配 ](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/webgl_loader_gltf.html)

- 冻结：`d04539a76736ff500cae883d6a38b3dd8643c548`
- 许可：[MIT / LICENSE](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/LICENSE)；three.js authors, Copyright © 2010-2023
- 资产边界：只核验该代码；示例中的图片、字体、模型、数据不随代码许可自动获准
- [仓库最后commit](https://github.com/mrdoob/three.js/commit/633ce03810d62bd161121a88142e979e77cc69c0)：2026-10-02T10:41:36Z；冻结版本commit日期：2023-12-22T12:31:45Z
- 时间、r160与依赖检查：加载器/材质是设备壳模型入口；model资源须另授权。模型加载、贴图、着色器编译完成后再渲染，停止自动转台与OrbitControls；变换直接由t决定。
- [原仓库预览](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/screenshots/webgl_loader_gltf.jpg)

### 实现参考 2：[ r160 RoundedBoxGeometry 自建无品牌设备壳 ](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/jsm/geometries/RoundedBoxGeometry.js)

- 冻结：`d04539a76736ff500cae883d6a38b3dd8643c548`
- 许可：[MIT / LICENSE](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/LICENSE)；three.js authors, Copyright © 2010-2023
- 资产边界：只核验该代码；示例中的图片、字体、模型、数据不随代码许可自动获准
- [仓库最后commit](https://github.com/mrdoob/three.js/commit/633ce03810d62bd161121a88142e979e77cc69c0)：2026-10-02T10:41:36Z；冻结版本commit日期：2023-12-22T12:31:45Z
- 时间、r160与依赖检查：从参数生成圆角盒体，屏幕用独立Plane+用户图片；不需要某品牌手机模型，也不用运行时DOM iframe。省却设备素材授权与网络加载，但相机/屏幕UV需自写。

### 实现参考 3：[ drei RenderTexture 屏内场景 ](https://github.com/pmndrs/drei/blob/bf6f4addf47467d3885de272d94ca5127f6ef68f/src/core/RenderTexture.tsx)

- 冻结：`bf6f4addf47467d3885de272d94ca5127f6ef68f`
- 许可：[MIT / LICENSE](https://github.com/pmndrs/drei/blob/bf6f4addf47467d3885de272d94ca5127f6ef68f/LICENSE)；react-spring, Copyright (c) 2020
- 资产边界：drei代码MIT；pmndrs/drei-assets模型不因此获得MIT许可，详见O2排除
- [仓库最后commit](https://github.com/pmndrs/drei/commit/bf6f4addf47467d3885de272d94ca5127f6ef68f)：2026-09-30T18:14:27+02:00；冻结版本commit日期：2026-09-30T18:14:27+02:00
- 时间、r160与依赖检查：屏幕呈现另一个3D子场景的参考；依赖R3F portal/useFrame、当前React19/R3F9，three peer>=0.159不能证明整套对r160适配。普通截图插槽无需这套React堆栈，r160原生Texture足够。

### 适配决策

普通截图作为sRGB texture，UV保留屏幕比例；fit/cover与圆角遮罩应显式。所有纹理解码就绪后render(t)；不要嵌iframe、在线网页或自动播放video。悬浮面板用Plane/rounded rect，不需要外部硬件品牌。

用户截图可能含个人/品牌信息；不对外上传。本调查不处理私有图。设备模型逐文件权利见O2；React RenderTexture只参考复杂屏内场景，静态截图不用引入React。

### 义务与可复制署名

首推代码义务：attribution=true，SA=false，NC=false，ND=false。保留相应许可全文/免责；Apache改动文件须显著标识，若源含NOTICE则随附。视频简介不是替代代码分发许可文件。附属图片/字体/数据如被另选，义务另加，不能沿用上述四布尔值。

three.js authors, Copyright © 2010-2023：r160 GLTFLoader 场景装配，https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/webgl_loader_gltf.html，MIT；react-spring, Copyright (c) 2020：drei RenderTexture 屏内场景，https://github.com/pmndrs/drei/blob/bf6f4addf47467d3885de272d94ca5127f6ef68f/src/core/RenderTexture.tsx，MIT。未改造版：保留原代码版权与许可全文。后续实际改造版附加：已将交互/自带时钟改造为离线外部时间驱动，并按本作品标题与主题调整参数。仅在上述改动确实发生时使用改造版。

署名位置：资产包说明和THIRD_PARTY_NOTICES；视频简介可加实现来源。这里只提供条件模板，本调查没有实际改造或分发源码。

## O1-09｜破碎 / 多米诺 / 掉落

**全路判断：备选：简单破碎用闭式弹道；真碰撞用cannon-es固定步长预烘焙pose表**

家族首推路线：简单破碎用闭式弹道；真碰撞用cannon-es固定步长预烘焙pose表

- 对应：module/hook；card可选、explainer、showcase
- 适配：B，去demo外壳并参数化；所需合同补项见末节
- 改造后时间分类：可烘焙
- 风格覆盖：综艺、电影、科技；低幅度慢速可克制
- GPU定性估计（未实测）：中到高；碎片数量、材质批次与阴影导致GPU增长；烘焙主要额外CPU和存储，不能混为GPU估计
- 插槽/参数：seed、pieces、mass/impact、gravity、bounceCount、bakeFps、title/icon、palette、duration

### 实现参考 1：[ cannon-es 刚体堆叠/倒落 ](https://github.com/pmndrs/cannon-es/blob/dd971c4a604acdbb211955382e7a80de1f31edfb/examples/stacks.html)

- 冻结：`dd971c4a604acdbb211955382e7a80de1f31edfb`
- 许可：[MIT / LICENSE](https://github.com/pmndrs/cannon-es/blob/dd971c4a604acdbb211955382e7a80de1f31edfb/LICENSE)；cannon.js Authors, Copyright (c) 2015
- 资产边界：只核验该代码；示例中的图片、字体、模型、数据不随代码许可自动获准
- [仓库最后commit](https://github.com/pmndrs/cannon-es/commit/dd971c4a604acdbb211955382e7a80de1f31edfb)：2024-01-06T14:10:13+10:00；冻结版本commit日期：2024-01-06T14:10:13+10:00
- 时间、r160与依赖检查：物理world.step积分依赖上一状态；只在准备阶段固定seed、初态、步长和求解器进行烘焙，存每个刚体pose；成片不得逐帧跑world.step。原生JS无需React/WASM；物理数据与Three版本解耦。

### 实现参考 2：[ r160 ConvexObjectBreaker 分片 ](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/jsm/misc/ConvexObjectBreaker.js)

- 冻结：`d04539a76736ff500cae883d6a38b3dd8643c548`
- 许可：[MIT / LICENSE](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/LICENSE)；three.js authors, Copyright © 2010-2023
- 资产边界：只核验该代码；示例中的图片、字体、模型、数据不随代码许可自动获准
- [仓库最后commit](https://github.com/mrdoob/three.js/commit/633ce03810d62bd161121a88142e979e77cc69c0)：2026-10-02T10:41:36Z；冻结版本commit日期：2023-12-22T12:31:45Z
- 时间、r160与依赖检查：原实现多处调用Math.random；须在预处理适配中显式注入固定PRNG（不要全局覆盖共享Math.random）并冻结碎块几何。切割本身与后续刚体模拟分开。碎片可走闭式弹道+固定旋转或关键帧表；不要把physics_ammo_break的stepSimulation搬进runtime。

### 实现参考 3：[ R0 glass-shard-title ](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/glass-shard-title/glass-shard-title.html)

- 冻结：`8aefd91bf82c687222082a80a3c5845ff37e6ca6`
- 许可：[Apache-2.0 / LICENSE](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/LICENSE)；HeyGen / HyperFrames contributors
- 资产边界：代码Apache-2.0；Three-LICENSE.txt MIT；Geist/Cormorant字体OFL；HDR+matcap来源未逐文件认证，不接受其图片资产
- [仓库最后commit](https://github.com/heygen-com/hyperframes/commit/8aefd91bf82c687222082a80a3c5845ff37e6ca6)：2026-10-02T12:48:06Z；冻结版本commit日期：2026-10-02T12:48:06Z
- 时间、r160与依赖检查：seeded Voronoi切片+解析飞行是更符合合同的破碎参考；bundled Three0.181.2、d3-delaunay CDN，需r160移植。官方350MB/instance仅上游预算非实测。

### 适配决策

闭式片段x=x0+v*t+0.5*g*t²与固定axis-angle可纯函数；碰撞后的时间/速度需在烘焙时写表。多米诺要记录固定步长世界、求解参数、每片(position,quaternion)与存在区间，runtime二分+lerp/slerp，不从前一视频帧推进。

跨CPU/引擎版本不承诺物理数值位级相同；冻结最终烘焙文件hash比只记录seed可靠。去掉玻璃标题里许可未明的HDR/matcap，勿直接接原Ammo二进制。

### 义务与可复制署名

首推代码义务：attribution=true，SA=false，NC=false，ND=false。保留相应许可全文/免责；Apache改动文件须显著标识，若源含NOTICE则随附。视频简介不是替代代码分发许可文件。附属图片/字体/数据如被另选，义务另加，不能沿用上述四布尔值。

cannon.js Authors, Copyright (c) 2015：cannon-es 刚体堆叠/倒落，https://github.com/pmndrs/cannon-es/blob/dd971c4a604acdbb211955382e7a80de1f31edfb/examples/stacks.html，MIT；three.js authors, Copyright © 2010-2023：r160 ConvexObjectBreaker 分片，https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/jsm/misc/ConvexObjectBreaker.js，MIT；HeyGen / HyperFrames contributors：R0 glass-shard-title，https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/glass-shard-title/glass-shard-title.html，Apache-2.0。未改造版：保留原代码版权与许可全文。后续实际改造版附加：已将交互/自带时钟改造为离线外部时间驱动，并按本作品标题与主题调整参数。仅在上述改动确实发生时使用改造版。

署名位置：资产包说明和THIRD_PARTY_NOTICES；视频简介可加实现来源。这里只提供条件模板，本调查没有实际改造或分发源码。

## O1-10｜照片2.5D视差（图片+深度图）

**全路判断：首推：Depthy UV位移机制移植r160 ShaderMaterial；小幅解析cameraOffset(t)**

家族首推路线：Depthy UV位移机制移植r160 ShaderMaterial；小幅解析cameraOffset(t)

- 对应：module/hook；card可选、explainer、showcase
- 适配：B，去demo外壳并参数化；所需合同补项见末节
- 改造后时间分类：纯函数
- 风格覆盖：克制、电影、新闻人文；科技/综艺取决于图像内容
- GPU定性估计（未实测）：低；单平面双纹理通常低，细分位移/多层遮罩升到中；未测GPU毫秒
- 插槽/参数：image、depthMap、depthRange、focus、parallaxAmplitude、edgeFill、palette、duration

### 实现参考 1：[ Depthy 深度图UV视差shader ](https://github.com/panrafal/depthy/blob/6ff99c1eb975e820e7feee988cd0df3978ce0df2/app/scripts/pixi/DepthDisplacementFilter.js)

- 冻结：`6ff99c1eb975e820e7feee988cd0df3978ce0df2`
- 许可：[MIT / LICENSE](https://github.com/panrafal/depthy/blob/6ff99c1eb975e820e7feee988cd0df3978ce0df2/LICENSE)；Rafał Lindemann, Copyright (c) 2014
- 资产边界：MIT代码；示例照片/Google Camera用户图不获自动许可；不接纳AI生成图片
- [仓库最后commit](https://github.com/panrafal/depthy/commit/6ff99c1eb975e820e7feee988cd0df3978ce0df2)：2015-11-21T13:42:34+01:00；冻结版本commit日期：2015-11-21T13:42:34+01:00
- 时间、r160与依赖检查：fragment直接由图片、深度、offset、scale、focus采样，数学上无历史帧；原PIXI.AbstractFilter接口很旧，不直接安装。移植shader至r160 ShaderMaterial，offset(t)由宿主直接赋值；不搬鼠标/陀螺仪easeFactor。

### 实现参考 2：[ r160 顶点位移面材质 ](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/webgl_materials_displacementmap.html)

- 冻结：`d04539a76736ff500cae883d6a38b3dd8643c548`
- 许可：[MIT / LICENSE](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/LICENSE)；three.js authors, Copyright © 2010-2023
- 资产边界：只核验该代码；示例中的图片、字体、模型、数据不随代码许可自动获准
- [仓库最后commit](https://github.com/mrdoob/three.js/commit/633ce03810d62bd161121a88142e979e77cc69c0)：2026-10-02T10:41:36Z；冻结版本commit日期：2023-12-22T12:31:45Z
- 时间、r160与依赖检查：几何细分平面+displacementMap是“真实网格位移”的第二路线；原例人头与贴图不选。网格边缘会裂/拉伸，需要限制视差或分层mask，不能从单图恢复真实被遮挡信息。
- [原仓库预览](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/screenshots/webgl_materials_displacementmap.jpg)

### 适配决策

prepare统一图片/深度尺寸、方向、色彩空间；depth按线性数据读，颜色按sRGB。offset从t直接决定，不采用鼠标平滑前态。小幅UV移动有边缘露底和遮挡拉伸，合约须定义overscan/安全区；确需大幅移动时分层抠图或真实网格。

深度图来源与生成方式须记录；本调查不接纳AI生成图，也不默认为AI生成深度图豁免。自动估深不是内容可信证据，不能把新闻照片中不存在的侧面视角当作真实记录。9:16裁切要先审主体，再算安全视差。

### 义务与可复制署名

首推代码义务：attribution=true，SA=false，NC=false，ND=false。保留相应许可全文/免责；Apache改动文件须显著标识，若源含NOTICE则随附。视频简介不是替代代码分发许可文件。附属图片/字体/数据如被另选，义务另加，不能沿用上述四布尔值。

Rafał Lindemann, Copyright (c) 2014：Depthy 深度图UV视差shader，https://github.com/panrafal/depthy/blob/6ff99c1eb975e820e7feee988cd0df3978ce0df2/app/scripts/pixi/DepthDisplacementFilter.js，MIT；three.js authors, Copyright © 2010-2023：r160 顶点位移面材质，https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/webgl_materials_displacementmap.html，MIT。未改造版：保留原代码版权与许可全文。后续实际改造版附加：已将交互/自带时钟改造为离线外部时间驱动，并按本作品标题与主题调整参数。仅在上述改动确实发生时使用改造版。

署名位置：资产包说明和THIRD_PARTY_NOTICES；视频简介可加实现来源。这里只提供条件模板，本调查没有实际改造或分发源码。

## O1-11｜3D文字主导：砸下 / 翻牌 / 拆字重组

**全路判断：首推：TextGeometry + 合法CJK子集，逐字transform(t)；平面路线由O2选SDF/MSDF**

家族首推路线：TextGeometry + 合法CJK子集，逐字transform(t)；平面路线由O2选SDF/MSDF

- 对应：module/hook；card可选、explainer、showcase
- 适配：B，去demo外壳并参数化；所需合同补项见末节
- 改造后时间分类：纯函数
- 风格覆盖：克制、科技、综艺、电影皆可
- GPU定性估计（未实测）：中到高；汉字轮廓/倒角细分易爆面数；SDF较低但透明过绘/bloom有成本
- 插槽/参数：title、fontAsset、glyphManifest、extrudeDepth、bevel、perGlyphOrder、palette、duration

### 实现参考 1：[ r160 TextGeometry 立体字 ](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/webgl_geometry_text.html)

- 冻结：`d04539a76736ff500cae883d6a38b3dd8643c548`
- 许可：[MIT / LICENSE](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/LICENSE)；three.js authors, Copyright © 2010-2023
- 资产边界：只核验该代码；示例中的图片、字体、模型、数据不随代码许可自动获准
- [仓库最后commit](https://github.com/mrdoob/three.js/commit/633ce03810d62bd161121a88142e979e77cc69c0)：2026-10-02T10:41:36Z；冻结版本commit日期：2023-12-22T12:31:45Z
- 时间、r160与依赖检查：中文前提是合法中文字体转换后含全部字形；自带英文typeface不是中文支持。挤出、倒角可用；按字分组的transform与显隐写成t函数。
- [原仓库预览](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/screenshots/webgl_geometry_text.jpg)

### 实现参考 2：[ r160 ShapeGeometry 平面字形 ](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/webgl_geometry_text_shapes.html)

- 冻结：`d04539a76736ff500cae883d6a38b3dd8643c548`
- 许可：[MIT / LICENSE](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/LICENSE)；three.js authors, Copyright © 2010-2023
- 资产边界：只核验该代码；示例中的图片、字体、模型、数据不随代码许可自动获准
- [仓库最后commit](https://github.com/mrdoob/three.js/commit/633ce03810d62bd161121a88142e979e77cc69c0)：2026-10-02T10:41:36Z；冻结版本commit日期：2023-12-22T12:31:45Z
- 时间、r160与依赖检查：同一Font.generateShapes得到薄片标题，可作翻牌/字轮或低面数路线；不是自动带挤出侧面。
- [原仓库预览](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/screenshots/webgl_geometry_text_shapes.jpg)

### 实现参考 3：[ R0 wireframe-portal-title ](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/wireframe-portal-title/wireframe-portal-title.html)

- 冻结：`8aefd91bf82c687222082a80a3c5845ff37e6ca6`
- 许可：[Apache-2.0 / LICENSE](https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/LICENSE)；HeyGen / HyperFrames contributors
- 资产边界：Apache-2.0代码；Geist字体OFL路径assets/fonts/Geist-OFL.txt；Clipper需保留其独立许可；此处不接受任何未核验外部资源
- [仓库最后commit](https://github.com/heygen-com/hyperframes/commit/8aefd91bf82c687222082a80a3c5845ff37e6ca6)：2026-10-02T12:48:06Z；冻结版本commit日期：2026-10-02T12:48:06Z
- 时间、r160与依赖检查：0.181.2+Clipper6.4.2+FontLoader/TTFLoader+hf-seek；标题爆散/门框构成已可参考，但当前字体不含CJK、默认18字符不等于18个中文都排得下，需实测汉字bbox。

### 适配决策

字形/几何须prepare完成；按字glyphOrigin固定transform。砸下可分段弹道/闭式阻尼响应，不用运行时刚体；翻牌用q→quaternion；拆字需定义按字、笔画还是预切碎片，不能把轮廓子路径误当语义笔画。

只在hook例外允许可读标题进WebGL，concept仍DOM文字。DOM第四层留空要由harness确认，3D标题仍要有文本元数据/安全区/可读停留时长；中文离线字体方案详O2。

### 义务与可复制署名

首推代码义务：attribution=true，SA=false，NC=false，ND=false。保留相应许可全文/免责；Apache改动文件须显著标识，若源含NOTICE则随附。视频简介不是替代代码分发许可文件。附属图片/字体/数据如被另选，义务另加，不能沿用上述四布尔值。

three.js authors, Copyright © 2010-2023：r160 TextGeometry 立体字，https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/webgl_geometry_text.html，MIT；HeyGen / HyperFrames contributors：R0 wireframe-portal-title，https://github.com/heygen-com/hyperframes/blob/8aefd91bf82c687222082a80a3c5845ff37e6ca6/registry/blocks/wireframe-portal-title/wireframe-portal-title.html，Apache-2.0。未改造版：保留原代码版权与许可全文。后续实际改造版附加：已将交互/自带时钟改造为离线外部时间驱动，并按本作品标题与主题调整参数。仅在上述改动确实发生时使用改造版。

署名位置：资产包说明和THIRD_PARTY_NOTICES；视频简介可加实现来源。这里只提供条件模板，本调查没有实际改造或分发源码。

## 排除项

- **O1-12 [InfiniteTubes 原实现](https://github.com/Mamboleoo/InfiniteTubes/blob/a3b831b6c95bed4d803dfeed8b66ec76de333996/js/demo1.js)**：排除：固定版本没有LICENSE文件。版本 `a3b831b6c95bed4d803dfeed8b66ec76de333996`；许可 NOASSERTION — no LICENSE file；最后commit 2017-05-09T10:24:22+01:00。无LICENSE；旧Three Geometry与交互/缓动前态
- **O1-13 [GPUComputationRenderer 鸟群/积分型粒子作为实时hook](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/webgl_gpgpu_birds.html)**：排除：反馈粒子运行时依赖历史帧。版本 `d04539a76736ff500cae883d6a38b3dd8643c548`；许可 MIT；最后commit 2026-10-02T10:41:36Z。当前速度/位置依赖前一模拟帧；重置并从0重跑不是本合同的直接任意时刻求值；把curl noise当速度场逐步积分同样不合格

## O1触发的合同缺口

- hook的3D正式标题与DOM第4层空置：明确按用户决定4覆盖，仅hook有效；title纯文本元数据、fontAsset/glyphManifest、可读停留、安全区仍要保留
- prepare/ready/error/dispose与render(t)的边界：异步字体、模型、解码器、布局/物理烘焙必须先完成；未ready禁止悄悄渲染半成品
- 描述多资源插槽：image+depthMap、title+font subset、model+screenTexture、graphData+bakedLayout、physicsPoseTable，资源各自hash/许可/预处理来源进入闭包
- 给时间分类记录“原版状态”与“适配后目标”；改造前不可用不等于原作者项目不好，也不等于本次已经完成改造
- 性能合同应让particle/instance/triangle/texture/RT/bloom budget可配；先测再写上限。不要把R0的350MB建议或源码粒子数当实测
- 署名随作品闭包汇总，代码许可与美术/字体/数据许可独立字段；跨来源聚合不能把最宽松许可证覆盖其他资产
- 中国地图合规证据缺失则地图版本不可用；不把开源许可、没有国界线或无商用用途当作地图审核通过

## 推荐的首轮试做顺序（本次不执行）

1. O1-10：照片+深度图双插槽，验证离线与随机seek；用用户本地自有合法照片，由本地另做
2. O1-11：两行中文真挤出标题，验证常见字/生僻字/标点/英文数字混排与geometry预算，字体路线遵从O2
3. O1-01：同一标题/图标两次换插槽，无新代码的粒子聚合
4. O1-03：固定图数据与布局seed，多节点逐口播出现
5. O1-04：复用R0银河，不引入第二个银河库，只做r160/离线迁移和性能验收

以上顺序是风险最小的技术建议，不改变用户后续自行筛选与写镜头任务单的决定。
