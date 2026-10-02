# O2 · 3D 素材与中文 3D 标题

调查日：2026-10-02。范围：公开 GitHub 只读；只交链接、固定版本、原创研究说明和测量方法。没有把字体、模型、贴图、HDRI、依赖代码或预览图本体放入交付目录。11 个候选，5 个首推；其中“首推”表示优先试做，不表示已接纳或全部验收。

## 结论与推荐顺序

1. **真正立体、能翻转、能看侧面：O2-01 TextGeometry + O2-05 中文静态字体子集。** 宿主已经固定 r160，先复用其 FontLoader / TextGeometry，避免再造一套轮廓孔洞转换器。本次已完成两组中文的 r160 CPU 字形转换和几何生成。
2. **正面可读、常换标题、描边与柔光：O2-02 troika-three-text。** SDF 字是放在 3D 场景里的平面，不是真实挤出。录帧前完成同步，主字体及 fallback 必须完全本地化。
3. **标题已确定、批量生成、要统一重现准备结果：O2-03 预生成 MSDF。** 每期重新生成用字图集和排版。运行期没有字体解析/缺字下载；代价是需要自制 r160 atlas/layout adapter。
4. **复杂逐轮廓特效：O2-04 opentype.js 作为备选。** 普通挤出不优先用它自制适配，r160 的 TTFLoader 已能处理测试的 CFF 中文 OTF。字形轮廓不是语义笔画；逐笔画动画还需要独立笔画数据、分割和笔顺方案。
5. **合法 3D 小道具基线：O2-06 的 WaterBottle / BoomBox。** 逐模型 LICENSE 明确模型与纹理 CC0；元文档另为 CC BY 4.0。HDRI 用 O2-07 的已溯源小子集作为备选。

本轮**没有确认可直接接纳的品牌手机/笔记本样机，也没有确认合规中国地图或符合全部许可门槛的地球贴图**。不要用 drei 的代码 MIT 覆盖独立的 drei-assets 模型；也不要把 NASA 来源、CC0 或无政治边界的外观误当中国地图合规证明。

## 四条中文标题路线对比

| 对比项 | TextGeometry + typeface 子集 | troika SDF | 预生成 MSDF | opentype.js → 路径挤出 |
|---|---|---|---|---|
| 中文 | 输入 JSON 必须含所需 CJK 字形；默认西文字体不能替代中文 | 本地中文 OTF/TTF/WOFF；缺字默认找 Unicode fallback | 生成时明确传中文字符集，默认 ASCII 不够 | 取决于输入字体；支持静态 glyf/CFF，额外负责排版、方向与孔洞 |
| 完全离线 | 本地 JSON、r160 模块即可 | 可，但显式主字体、fallback data/font-files、Worker/依赖都要闭包 | 最容易封闭：PNG + metrics + shader | 可；准备期本地字库与 parser，运行期可只带几何 |
| 每期换标题 | 用本期字符集合重建子集 JSON；缺字准备期报错 | 真正削小字体文件需先子集化；preloadFont(characters) 仅预生成对应 SDF，不减少原字体下载量 | 每期从完整合法字库重建 atlas/metrics；改文字不能继续引用旧 atlas | 准备期只读取需要的 glyph，或先子集字体；缓存每字几何 |
| 体积 | 样本 JSON 几 KB，但几何内存可达几十万至上百万字节 | 子集几 KB + JS闭包 + 动态SDF；完整Unicode fallback官方说“近300MB” | 图集像素/通道决定显存，PNG大小须实际测；字形不必带全量字库 | parser增量未测；只在准备期使用可消除运行期parser |
| 真挤出 / 倒角 | 原生支持；需限曲线细分和倒角 | 否；层叠平面不是真实体 | 否；需另加几何路线，不能声称 MSDF自带厚度 | 可，用 ExtrudeGeometry；必须自行生成正确 Shapes/holes |
| 描边 | 可做专用几何或额外pass，不是TextGeometry自带排版描边 | 原生 stroke / outline 参数 | shader按距离阈值做描边，受pxRange限制 | 路径偏移或额外几何，需另做鲁棒性处理 |
| 发光 | 发光材质 + 无历史bloom；不要逐帧累加 | outlineBlur可做光晕；需要亮度扩散可用无历史bloom | 距离场光晕或无历史bloom | 同几何路线 |
| 确定性 | 固定字体、几何、seed，变换由 t 求值 | SDF/layout同步完成后固定；不要到帧中途才变 text | 固定生成器、字体、glyphs、atlas和metrics后，运行期只按 t 求值 | 解析/三角化固定后按 t 求值；不在每帧重新解字 |
| r160 证据 | 精确使用r160；CPU转换/几何生成通过，未视觉/GPU/倒拖测试 | peer范围包含r160，但未实跑shader兼容 | 生成器与Three无关；r160 shader适配未实现 | parser独立；自制adapter未验证；不能借O2-01的结果冒称通过 |
| GPU成本（工程判断） | 跟顶点/面数、材质、阴影、后期有关，倒角可显著放大 | 默认每字quad，几何低；透明overdraw/大光晕可能贵 | 每字quad或实例化，主要为纹理采样/overdraw | 与生成后的几何路线相近 |

以上 GPU 开销是结构性估计，没有编造毫秒数、FPS、内存峰值或不同机器一致像素保证。相同输入/t 的确定性，指同一冻结运行环境的可重放语义；WebGL浮点与驱动差异仍需容差比较。

## troika 的离线封口是必要条件

固定 **0.52.4 / 728a1780127df0c2509e967b03f17ddc46bbf5d2**。选择此已核对版本，不是把最新版本当已兼容；调查时默认分支已到0.53.0。

- [package.json](https://github.com/protectwise/troika/blob/728a1780127df0c2509e967b03f17ddc46bbf5d2/packages/troika-three-text/package.json) 的 three peer 为 >=0.125.0；这只是版本声明，不是 r160 GPU 测试结果
- 指定本地 font；该版支持 TTF/OTF/WOFF，不支持 WOFF2
- [FontResolver](https://github.com/protectwise/troika/blob/728a1780127df0c2509e967b03f17ddc46bbf5d2/packages/troika-three-text/src/FontResolver.js) 在用户字体没覆盖字符时调用 Unicode resolver。字符含中文并不保证永远只访问用户字体
- `preloadFont({font,characters})` 只预热所需 glyph 的 SDF，**不会把一个8MB字库自动变成几KB下载文件**
- 最小路线：每期先由本地源字库生成完整覆盖标题、标点、数字、备用文案的子集；准备时做 cmap/glyph检查；不允许未记录的 fallback 请求，缺字直接失败
- 需要多语言 fallback 时，把 [unicode-font-resolver v1.0.2](https://github.com/lojjic/unicode-font-resolver/tree/974383af089e544f4ac4b0ba96b5f98891688e17) 的匹配索引和真正需要的 font-files 一起封存，并设置代码使用的 `unicodeFontsURL`。不能只下载MIT客户端就认为Noto字体也已离线
- [packages/data/LICENSE](https://github.com/lojjic/unicode-font-resolver/blob/974383af089e544f4ac4b0ba96b5f98891688e17/packages/data/LICENSE) 是 MIT，但明确指向 [font-files/LICENSE](https://github.com/lojjic/unicode-font-resolver/blob/974383af089e544f4ac4b0ba96b5f98891688e17/packages/data/font-files/LICENSE)；后者是Noto OFL，不得混同
- README 的默认字体描述与源码 `defaultFontURL:null` 不完全一致。使用显式本地路径并验收所有请求，比依赖说明中的默认值安全
- `sync` / `synccomplete` 和 `preloadFont` callback 全部完成后才进入可录帧状态。`useWorker:false` 仍然异步；它解决CSP/Worker可用性，不替代ready屏障
- 可选择 `gpuAccelerateSDF:false` 固定为CPU生成，然后冻结结果；这只是减少生成路径差异的建议，本轮未测试生成后的像素一致性

## 真实测量：字体 KB 与几何成本是两回事

### 固定源与测试范围

- Three.js **r160** 注解 tag指向的提交：[d04539a76736ff500cae883d6a38b3dd8643c548](https://github.com/mrdoob/three.js/commit/d04539a76736ff500cae883d6a38b3dd8643c548)
- 字体：[SourceHanSansCN-Bold.otf，2.005R](https://github.com/adobe-fonts/source-han-sans/blob/6c709ca72d3d7c46ab42ebecc1a26e7d69595a37/SubsetOTF/CN/SourceHanSansCN-Bold.otf)
- 原字库 **8,569,308 B**；SHA-256 `62383707c086a32f3afd5e293f34c7eff64c7fea31f579fdc6cbe34d920519a6`
- 本次读取该字库的 cmap 映射30,926码点、31,072 glyph。未核对所有规范汉字、异体字选择序列或字体全部版本，不能据此承诺通用规范一级字全覆盖
- 测试环境：fontTools **4.61.1**、Node **24.19.0**。fontTools 子集 `hinting=False`、`desubroutinize=True`、`layout_features=['*']`；name/CFF族名及PostScript名改为 AuditSubset；保留原版权和OFL。改名未作为可分发字体产品做完整fontQA，本次子集不交付
- JSON由 r160 TTFLoader.parse 生成，再经 FontLoader.parse 和 TextGeometry。r160代码仅在临时评估目录把import路径改为本地，未改解析/几何算法

| 样本 | 唯一码点 | 子集glyph（含闭包） | 子集OTF | 子集WOFF | typeface JSON | gzip(JSON) |
|---|---:|---:|---:|---:|---:|---:|
| 人工智能改变世界 | 8 | 9 | 2,820 B | 2,548 B | 5,509 B | 2,313 B |
| 2026：人工智能如何改变我们的生活？ | 18 | 30 | 5,908 B | 4,956 B | 10,563 B | 4,277 B |

这两个样本均无缺字。第二行是18个**唯一码点**，不是全文长度或18个glyph；布局闭包留下30个glyph很正常。数字只说明这次字体/参数/文案，不是所有中文标题的体积上限。gzip是传输对比数，离线未压缩JSON仍按实际磁盘资源计算。

几何参数：`size=1, height=0.15, curveSegments=6, steps=1`；有倒角时 `bevelThickness=0.015, bevelSize=0.01, bevelSegments=2`。

| 样本 | 倒角 | triangles | position顶点 | position+normal+uv数组字节 |
|---|---|---:|---:|---:|
| 8字 | 无 | 1,346 | 4,038 | 129,216 B |
| 8字 | 2段 | 5,914 | 17,742 | 567,744 B |
| 18唯一码点 | 无 | 4,132 | 12,396 | 396,672 B |
| 18唯一码点 | 2段 | 15,500 | 46,500 | 1,488,000 B |

**通过的是 CPU 解析和生成；未通过任何 GPU渲染验收、轮廓孔洞视觉验收、视频录制或随机seek测试。** 数组字节不包含JS对象、材质、阴影贴图、渲染目标、显存对齐或renderer开销，不能作为总显存。

### 可复现核心步骤（仅我们编写的评估逻辑）

以下为方法，不是要求本轮导入。将上述固定源读到临时目录，使用相同工具版本；不要复制第三方文件到研究仓库。

```python
# fontTools 4.61.1；source_otf 指向上面固定SHA的CN Bold
from fontTools.ttLib import TTFont
from fontTools import subset
font = TTFont(source_otf)
options = subset.Options()
options.hinting = False
options.desubroutinize = True
options.layout_features = ['*']
s = subset.Subsetter(options=options)
s.populate(text=title)
s.subset(font)
for n in font['name'].names:
    if n.nameID in [1,3,4,6,16,17]:
        n.string = ('Bold' if n.nameID == 17 else 'AuditSubset-Bold').encode(n.getEncoding())
if 'CFF ' in font:
    cff = font['CFF '].cff
    cff.fontNames = ['AuditSubset-Bold']
    cff.topDictIndex[0].FullName = 'AuditSubset Bold'
    cff.topDictIndex[0].FamilyName = 'AuditSubset'
font.save(subset_otf)
font.flavor = 'woff'
font.save(subset_woff)
```

```javascript
// Node 24.19.0；导入固定r160的TTFLoader、FontLoader、TextGeometry
const b = fs.readFileSync(subsetOtfPath)
const json = new TTFLoader().parse(b.buffer.slice(b.byteOffset, b.byteOffset+b.byteLength))
const raw = Buffer.from(JSON.stringify(json))
const font = new FontLoader().parse(json)
const g = new TextGeometry(title, {
  font, size:1, height:0.15, curveSegments:6, steps:1,
  bevelEnabled, bevelThickness:0.015, bevelSize:0.01, bevelSegments:2
})
const triangles = g.index ? g.index.count/3 : g.attributes.position.count/3
const attributeBytes = Object.values(g.attributes).reduce((n,a)=>n+a.array.byteLength,0)
// raw.length；zlib.gzipSync(raw).length；g.attributes.position.count
```

为了正式分发子集，还要核查全部name/CFF/STAT等命名位置和OFL保留信息；上例是**复现实测的方法，不是覆盖所有字体格式的改名器**。版权说明保留“Source”是必要来源记录，RFN禁用针对修改字体的名称，不能删版权来规避。

## 其他3D资产结果

### CC0模型与逐文件权利

固定 Khronos glTF-Sample-Assets 提交 `f36bfdabd1031c3cf6689a50570b8cdf3678b49c`：

| 文件 | GLB字节（GitHub blob metadata） | glTF unique mesh三角数 | 特点 |
|---|---:|---:|---|
| BoomBox.glb | 10,614,184 | 6,036 | core glTF，模型/纹理CC0；发光前板 |
| WaterBottle.glb | 8,966,700 | 4,510 | core glTF，模型/纹理CC0；适合作材质与灯光基线 |
| ToyCar.glb | 5,422,412 | 108,936 | 多材质/扩展、网格很重；只作负载对照 |

三角数来自各自同commit的 `glTF/<name>.gltf`，对mode4的索引accessor count除3后按unique mesh求和；GLB大小来自 `glTF-Binary/` 变体。**这不是已验证GLB与glTF二进制内部完全相同的断言**，也不包含节点实例化后的全场景重复面数。典型接纳应直接解析最终选定GLB复核，并在缩纹理/减面后重新统计。

这些模型的 [LICENSE.md示例](https://github.com/KhronosGroup/glTF-Sample-Assets/blob/f36bfdabd1031c3cf6689a50570b8cdf3678b49c/Models/WaterBottle/LICENSE.md) 明确：模型直接关联文本、图像、二进制CC0；LICENSE本身和metadata等元文档CC BY 4.0；logo和商标不在授权内。本报告没有把源文档全文拷入交付。

### HDRI：6张候选，1张解析实测

Pixal3D `assets/hdri/license.txt` 独立指定CC0和Poly Haven来源。只保留city/courtyard/forest/interior/sunrise/sunset六张；night/studio的来源写着“Probably”，不一起接纳。它们是引用的摄影HDRI，不能与该AI项目的生成模型和演示图混为一谈。

City文件204,863B，r160 EXRLoader实际解析为1024×512 DWAB、RGB源通道，默认HalfFloat RGBA数组4,194,304B；原文件header的历史字段与其声明的 Portland Landing Pad / oiiotool 转换一致。尚未验证色彩准确性、视觉内容、其余五图或PMREM像素结果。

复现：用r160的 [EXRLoader](https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/jsm/loaders/EXRLoader.js) 及同版本fflate，对固定commit的 `city.exr` 字节调用 `new EXRLoader().parse(arrayBuffer)`，读取width/height/data.byteLength/header.compression。下载字节和解码内存不同，PMREM还要额外预算。

### 纹理、地球与设备的缺口

- ambientCG目录在GitHub，但实际纹理包站外，未下载，故本轮不把它算可接纳素材；保留线索和维护者声明的体积，明确非实测
- KSRSS的地球DDS有README许可声明且NC本来允许；但无独立LICENSE、上游链混合，违反本轮准入要求。它不是因NC被排除
- drei-assets设备模型没有可确认的资产LICENSE。旁边代码库的MIT不能补授权
- 旧Khronos环境包没有统一许可证，而且HDR是LFS指针。132/133B是指针体积，不能报成HDRI大小
- 设备框宜另行设计无品牌几何，标题中的图片/屏幕走已有图片插槽；这只是后续设计建议，本轮未创建模型或模块
- **任何中国边界、城市连线底图、国家高亮都仍需国家标准地图证据。** 本轮找不到就维持不可用，不退而求其次

## 接纳前应补的合同与最小验收

1. hook-title资源：`titleText`、`fontRef`、`glyphCoverage`、字号/安全区、最长宽度和无障碍/语义对应文本。仅hook允许第4层DOM文字留空；concept不能自动继承此例外
2. prepare/ready：加载字体/atlas/模型、SDF生成、几何生成、PMREM、shader预编译与图片解码完成后才允许render(t)；禁止录制中再发隐含网络请求
3. 资源manifest：字体、typeface、atlas、GLB、EXR和decoder均须hash固定，记录许可及来源。现有media枚举未明确GLB/EXR；优先作为模块内部依赖，若不支持再扩合同，不偷塞成普通图片
4. 更换文字：把“能换标题”定义为**准备期可以重建用字资源**，不是运行中任何未见过的字也必须立即可用。字集外文字应给出明确缺字报告
5. 纯时间：每次render(t)都重算位置/旋转/透明度；禁止 `+=velocity`、基于frameIndex累积状态、物理引擎增量步进或TAA/afterimage
6. 复现测试：同一封闭浏览器/GPU配置下，分别按正序、倒序、随机顺序采样同一组 t，比对像素hash或明确容差；并检查字体/几何资源未在某个访问顺序下才加载
7. 视觉文本：测试“回国品器、，。：！？（）”、数字与Latin混排、简繁区域字形、相邻粗笔画倒角碰撞、极端字号、9:16和16:9安全区。不要把本次两句测试误当完整字库QA
8. 性能：记录最终variant的字节/三角形/texture维度/decoded bytes/材质数/draw calls；再在宿主做GPU测时。本报告的工程开销判断不代替这一步
9. 许可汇总：代码、字体、模型、贴图、metadata分别追踪。下方署名模板的“修改”句仅在**实际**做过所述改造后采用；不能把研究建议写成已发生的改动

## 生成输出与字体软件的许可边界

OFL约束字体软件和其修改版，不自动要求视频、普通图像或一次性排版输出采用OFL。TextGeometry的可复用typeface JSON按字体转换产物谨慎管理；仅输出最终排好的一次性几何或图片，不自动施加字体同许可条件。MSDF条目只计划携带图集和排版输出，故JSON中的share_alike=false；若接纳时把atlas+metrics作为可复用字体软件分发，需要重新判断其性质。任何额外分发的子集OTF/WOFF仍明确受OFL、版权和RFN改名义务约束。此边界应随实际交付物判断，不能以“生成过”作为全部免除许可的理由。

## 候选卡（与JSONL字段一致）

`obligations.share_alike=true` 对OFL条目表示**衍生字体继续OFL**，不代表视频须同许可。未知许可排除项的false布尔值表示未建立具体义务，绝不是自由使用许可。`maintenance`统一为调查时默认分支最新提交，附提交链接；选用较旧tag不等于仓库停止维护。

### O2-01 · r160 TextGeometry + 中文 typeface 子集

- **lane**：O2
- **url**：https://github.com/mrdoob/three.js
- **pinned_ref**：d04539a76736ff500cae883d6a38b3dd8643c548
- **license**：代码 MIT：https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/LICENSE；输入字体另见 O2-05 OFL，不继承代码 MIT。
- **obligations**：{"attribution": true, "share_alike": true, "non_commercial": false, "no_derivatives": false, "note": "MIT 版权和许可随代码分发；OFL 字体/子集保留 OFL 和版权、修改后避开 RFN。share_alike 仅指衍生字体保持 OFL，不约束视频。"}
- **attribution_text**：Three.js r160，© 2010–2023 three.js authors，MIT：https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/LICENSE。字体基于 Adobe Source Han Sans 2.005（Copyright 2014–2025 Adobe），SIL OFL 1.1：https://github.com/adobe-fonts/source-han-sans/blob/6c709ca72d3d7c46ab42ebecc1a26e7d69595a37/LICENSE.txt。仅使用原字形渲染；如分发字体子集，另列子集名称及实际改动。 改动说明（仅在实际改造后附加）：按本期标题生成字体子集和三维几何。
- **attribution_place**：资产包 THIRD_PARTY_NOTICES + 字体 LICENSE；视频片尾/简介可选代码鸣谢
- **risks**：["转换后的 typeface JSON 仍须按字体衍生物管理；不能因为扩展名为 JSON 改成 MIT", "中文孔洞、轮廓方向、简繁区域字形和粗体倒角碰撞需视觉验收", "标题任意换字与冻结字形包存在冲突，缺字必须准备期报错"]
- **content**：{"format": "typeface JSON + Three.js BufferGeometry", "sample_sizes": "8字样本 typeface 5,509 B / gzip 2,313 B；18唯一字符样本 10,563 B / gzip 4,277 B，详见实测表", "geometry": "8字 1,346 triangles（无倒角）或 5,914（2段倒角）；具体参数见正文", "preview": "https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/webgl_geometry_text.html"}
- **maps_to**：["module 的 hook 标题", "theme 字体衍生资源"]
- **product_lines**：["card", "explainer", "showcase"]
- **adaptation**：C：补 hook-title / prepare-ready / glyph-coverage 合同；实现本身 B：准备期把本期子集转 typeface；运行期仅生成一次几何
- **seekability**：纯函数
- **runtime**：{"three": "精确 r160；已完成 Node CPU 字形转换与几何生成；未完成 GPU/视觉/seek 测试", "react": false, "offline": "运行期本地 JSON；构建期 fontTools 4.61.1 和 r160 TTFLoader，勿每帧解析字体", "worker_wasm": "无需；同一 Three 实例，避免另打包 second copy"}
- **maintenance**：{"last_commit_date": "2026-10-02T10:41:36Z", "scope": "调查时默认分支最新提交；不是所选旧版本发布日期", "commit_sha": "633ce03810d62bd161121a88142e979e77cc69c0", "source": "https://github.com/mrdoob/three.js/commit/633ce03810d62bd161121a88142e979e77cc69c0", "checked_at": "2026-10-02"}
- **verdict**：首推：要真实厚度、倒角、侧面反光及翻转的中文短标题，优先宿主原生几何。
- **sources**：["https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/jsm/geometries/TextGeometry.js", "https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/jsm/loaders/FontLoader.js", "https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/jsm/loaders/TTFLoader.js", "https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/LICENSE", "https://github.com/adobe-fonts/source-han-sans/blob/6c709ca72d3d7c46ab42ebecc1a26e7d69595a37/LICENSE.txt"]
- **seekability_note**：纯函数：准备后位置、旋转、可见性仅依赖外部 t；几何缓存不按上一帧演化

### O2-02 · troika-three-text 0.52.4 + 完整本地中文子集

- **lane**：O2
- **url**：https://github.com/protectwise/troika
- **pinned_ref**：728a1780127df0c2509e967b03f17ddc46bbf5d2
- **license**：MIT：https://github.com/protectwise/troika/blob/728a1780127df0c2509e967b03f17ddc46bbf5d2/LICENSE；主字体独立 OFL；Unicode resolver 数据/客户端 MIT，font-files/LICENSE 的 Noto 字体为 OFL。
- **obligations**：{"attribution": true, "share_alike": true, "non_commercial": false, "no_derivatives": false, "note": "代码附 MIT；分发字体保留 OFL。share_alike 仅字体。preload 不等于已子集化字体文件。"}
- **attribution_text**：Troika Text by ProtectWise / Jason Johnston，MIT：https://github.com/protectwise/troika/blob/728a1780127df0c2509e967b03f17ddc46bbf5d2/LICENSE。字体基于 Adobe Source Han Sans 2.005（Copyright 2014–2025 Adobe），SIL OFL 1.1：https://github.com/adobe-fonts/source-han-sans/blob/6c709ca72d3d7c46ab42ebecc1a26e7d69595a37/LICENSE.txt。仅使用原字形渲染；如分发字体子集，另列子集名称及实际改动。 如用 Unicode fallback：Unicode Font Resolver by Jason Johnston，MIT；Noto fonts by The Noto Project Authors，OFL：https://github.com/lojjic/unicode-font-resolver/blob/974383af089e544f4ac4b0ba96b5f98891688e17/packages/data/font-files/LICENSE。
- **attribution_place**：资产包代码 NOTICE、每个字体对应 LICENSE；视频不强制把 MIT/OFL 全文上屏
- **risks**：["不能把 SDF 平面称为真正挤出字体", "默认 Unicode fallback 为 CDN；完全离线必须显式 font URL、缺字检查、本地 fallback 或保证所有字已覆盖", "0.52.4 README 称默认 Roboto，但 src/TextBuilder.js 的 defaultFontURL=null；按源码和网络断言验收", "异步 sync/preload、Worker/CSP、首次 glyph SDF 生成必须在录帧前完成", "三维大转角露出纸片侧面；细宋体及极大字号需要更高 sdfGlyphSize"]
- **content**：{"format": "TTF/OTF/WOFF 输入；SDF atlas 运行期生成；此版不支持 WOFF2", "size": "主字体样本见正文；完整 fallback 集近300MB仅为官方 README 近似值，未实测；最终 JS 闭包未 bundle 测量", "preview": "https://github.com/protectwise/troika/blob/728a1780127df0c2509e967b03f17ddc46bbf5d2/docs/troika-three-text/images/screenshot5.png"}
- **maps_to**：["module 的 hook 正面标题", "theme 字体"]
- **product_lines**：["card", "explainer", "showcase"]
- **adaptation**：C：准备屏障及资源闭包合同；B：显式本地字体，预生成所有文本，outline/stroke 参数主题化
- **seekability**：纯函数
- **runtime**：{"three": "peer >=0.125.0 包含 r160；仅源码兼容证据，未跑 r160 GPU smoke，不等于已验证", "react": false, "dependencies": "troika-three-utils、troika-worker-utils、bidi-js、webgl-sdf-generator；必须冻结整个 lockfile", "worker_wasm": "默认 Web Worker；可 configureTextBuilder({useWorker:false}) 但仍异步；gpuAccelerateSDF=false 可统一走 CPU生成", "network": "font 和 unicodeFontsURL 都指向本地；resolver 精确 v1.0.2 / 974383af089e544f4ac4b0ba96b5f98891688e17"}
- **maintenance**：{"last_commit_date": "2026-07-24T14:54:11Z", "scope": "调查时默认分支最新提交；不是所选旧版本发布日期", "commit_sha": "a24a35964de2d8187e0808a3f0c06a8d85e7f4a9", "source": "https://github.com/protectwise/troika/commit/a24a35964de2d8187e0808a3f0c06a8d85e7f4a9", "checked_at": "2026-10-02"}
- **verdict**：首推：标题常换、以正面可读性/描边光晕为主时，轻于几何；离线准备必须封口。
- **sources**：["https://github.com/protectwise/troika/blob/728a1780127df0c2509e967b03f17ddc46bbf5d2/packages/troika-three-text/README.md", "https://github.com/protectwise/troika/blob/728a1780127df0c2509e967b03f17ddc46bbf5d2/packages/troika-three-text/package.json", "https://github.com/protectwise/troika/blob/728a1780127df0c2509e967b03f17ddc46bbf5d2/packages/troika-three-text/src/TextBuilder.js", "https://github.com/protectwise/troika/blob/728a1780127df0c2509e967b03f17ddc46bbf5d2/packages/troika-three-text/src/FontResolver.js", "https://github.com/lojjic/unicode-font-resolver/blob/974383af089e544f4ac4b0ba96b5f98891688e17/packages/data/LICENSE", "https://github.com/lojjic/unicode-font-resolver/blob/974383af089e544f4ac4b0ba96b5f98891688e17/packages/data/font-files/LICENSE"]
- **seekability_note**：纯函数（prepare 完成后）：t 只改变变换或 shader 参数；中途改 text 必须预先同步所有候选

### O2-03 · msdf-atlas-gen 1.3 预生成中文字图集

- **lane**：O2
- **url**：https://github.com/Chlumsky/msdf-atlas-gen
- **pinned_ref**：c27de5988d7ecfbc9936ee5f936429e2dbc077b9
- **license**：MIT：https://github.com/Chlumsky/msdf-atlas-gen/blob/c27de5988d7ecfbc9936ee5f936429e2dbc077b9/LICENSE.txt；其 msdfgen 子模块 v1.12 / 85e8b3d47b3d1a42e4a5ebda0a24fb1cc2e669e0 另有 MIT LICENSE.txt；字体另为 OFL。
- **obligations**：{"attribution": true, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "本条只交付图像图集/排版输出，不自动给视频、图集或几何施加OFL/SA。若另分发修改字体，须单独保留OFL及RFN改名；若atlas+metrics被作为可复用Font Software分发，应在接纳时重新分类审查。构建程序若分发还须保留其依赖许可。"}
- **attribution_text**：MSDF Atlas Generator / msdfgen by Viktor Chlumsky，MIT：https://github.com/Chlumsky/msdf-atlas-gen/blob/c27de5988d7ecfbc9936ee5f936429e2dbc077b9/LICENSE.txt。字体基于 Adobe Source Han Sans 2.005（Copyright 2014–2025 Adobe），SIL OFL 1.1：https://github.com/adobe-fonts/source-han-sans/blob/6c709ca72d3d7c46ab42ebecc1a26e7d69595a37/LICENSE.txt。仅使用原字形渲染；如分发字体子集，另列子集名称及实际改动。 改动说明（实际生成后）：仅为本期标题生成距离场图集和排版数据。
- **attribution_place**：资产包说明、生成器 NOTICE、字体 LICENSE；无需把所有工具许可放视频画面
- **risks**：["默认 charset 是 ASCII，必须传 UTF-8 中文字符集或已排好 glyph IDs", "图集只是二维字形；不能拿 outline/glow 冒充侧面与倒角", "JSON atlasBounds/planeBounds 等不等同 BMFont JSON；不保证可直接接三方 BMFont 几何库", "CJK 细笔画需评估 em 尺寸、pxRange、padding；不同GPU像素输出仍可能有差异", "完整 shaping 不由 atlas 排包器自动解决；中文标点/拉丁 kerning 可离线排版，复杂连字需另行 shaping"]
- **content**：{"format": "PNG MSDF/MTSDF + JSON metrics；运行期每字四边形", "size": "未生成图集，压缩文件大小未知；预算公式 W×H×channels，RGBA8 512²=1,048,576 B，不含 mipmaps；这不是实测包大小", "preview": "https://github.com/Chlumsky/msdf-atlas-gen/blob/c27de5988d7ecfbc9936ee5f936429e2dbc077b9/README.md"}
- **maps_to**：["module 内部标题 atlas 资源"]
- **product_lines**：["card", "explainer", "showcase"]
- **adaptation**：C：需 r160 专用 quad+ShaderMaterial 和 layout adapter；B：按每期 title 收集字符离线生成，不能只换字串而不更新 atlas
- **seekability**：纯函数
- **runtime**：{"three": "生成器不依赖 Three；r160 渲染适配器尚未实现/验证", "react": false, "offline": "原生 C++ 构建工具可仅在准备期运行；成片闭包只含 atlas、metrics、shader，无 Worker/CDN/WASM", "build": "v1.3 固定子模块，禁用不需要的 artery 输出；FreeType 等构建依赖须独立记录，未交付工具二进制"}
- **maintenance**：{"last_commit_date": "2026-05-16T16:29:56Z", "scope": "调查时默认分支最新提交；不是所选旧版本发布日期", "commit_sha": "6148900d59423059bafde2f51a0cb303184404bd", "source": "https://github.com/Chlumsky/msdf-atlas-gen/commit/6148900d59423059bafde2f51a0cb303184404bd", "checked_at": "2026-10-02"}
- **verdict**：首推：固定标题、很多文字粒子/逐字特效或批量离线生产，准备成本换运行稳定性。
- **sources**：["https://github.com/Chlumsky/msdf-atlas-gen/blob/c27de5988d7ecfbc9936ee5f936429e2dbc077b9/README.md", "https://github.com/Chlumsky/msdf-atlas-gen/blob/c27de5988d7ecfbc9936ee5f936429e2dbc077b9/LICENSE.txt", "https://github.com/Chlumsky/msdfgen/blob/85e8b3d47b3d1a42e4a5ebda0a24fb1cc2e669e0/LICENSE.txt", "https://github.com/adobe-fonts/source-han-sans/blob/6c709ca72d3d7c46ab42ebecc1a26e7d69595a37/LICENSE.txt"]
- **seekability_note**：纯函数：字体、排版和atlas准备后固定，shader 时间参数完全由 t 提供

### O2-04 · opentype.js 1.3.4 字形路径 → ExtrudeGeometry

- **lane**：O2
- **url**：https://github.com/opentypejs/opentype.js
- **pinned_ref**：10563b50d0dcd25cd78f6ea16287b810dd9f7523
- **license**：MIT：https://github.com/opentypejs/opentype.js/blob/10563b50d0dcd25cd78f6ea16287b810dd9f7523/LICENSE；字体 OFL 单独适用。
- **obligations**：{"attribution": true, "share_alike": true, "non_commercial": false, "no_derivatives": false, "note": "MIT代码 NOTICE；字体衍生物按 OFL 保留许可与改名，视频无需 OFL。"}
- **attribution_text**：opentype.js by Frederik De Bleser，MIT：https://github.com/opentypejs/opentype.js/blob/10563b50d0dcd25cd78f6ea16287b810dd9f7523/LICENSE。字体基于 Adobe Source Han Sans 2.005（Copyright 2014–2025 Adobe），SIL OFL 1.1：https://github.com/adobe-fonts/source-han-sans/blob/6c709ca72d3d7c46ab42ebecc1a26e7d69595a37/LICENSE.txt。仅使用原字形渲染；如分发字体子集，另列子集名称及实际改动。 如采用自制转换器，应记录轮廓转换/三角化的实际改动。
- **attribution_place**：资产包说明和字体 LICENSE
- **risks**：["必须把 M/L/Q/C/Z 分轮廓、正确闭合并识别 holes；直接把所有路径塞进单 Shape 会堵住“回/国/品”等孔洞", "字体 y 轴方向与 Three 需统一，处理字距、advances、换行、标点；不是开箱即用中文排版器", "本次独立 opentype1.3.4→Extrude adapter 未实现；已测的是 r160 自带 TTFLoader 路径", "该版本支持 glyf/CFF，不应未经测试承诺所有可变字体/CFF2/emoji", "字形轮廓不是语义中文笔画；opentype不提供横竖撇捺的拆分或笔顺，需要独立笔画数据/分割算法及其许可"]
- **content**：{"format": "OTF/TTF/WOFF → path commands → Three Shapes / ExtrudeGeometry", "size": "未单独 bundle 测量；不应把包下载体积当成成片增量；可在准备期烘焙几何以删除运行期 parser", "preview": "https://github.com/opentypejs/opentype.js/blob/10563b50d0dcd25cd78f6ea16287b810dd9f7523/README.md"}
- **maps_to**：["module 制作工具或内部准备器"]
- **product_lines**：["card", "explainer", "showcase"]
- **adaptation**：C：需要自制轮廓适配与质量检测；无特殊轮廓需求时复用 O2-01
- **seekability**：纯函数
- **runtime**：{"three": "解析器 Three 无关；目标 ExtrudeGeometry r160；完整适配未测试", "react": false, "network": "可完全本地；仅静态 OTF/TTF 优先", "worker_wasm": "JS，无必需 Worker/WASM"}
- **maintenance**：{"last_commit_date": "2026-05-19T19:55:13Z", "scope": "调查时默认分支最新提交；不是所选旧版本发布日期", "commit_sha": "5d65b6dcfab5115f90d375f8ba6b7942fdaa0138", "source": "https://github.com/opentypejs/opentype.js/commit/5d65b6dcfab5115f90d375f8ba6b7942fdaa0138", "checked_at": "2026-10-02"}
- **verdict**：备选：需要逐轮廓/路径重排/特殊字形几何时才承担适配复杂度；语义笔画拆分需另有数据或算法。
- **sources**：["https://github.com/opentypejs/opentype.js/blob/10563b50d0dcd25cd78f6ea16287b810dd9f7523/README.md", "https://github.com/opentypejs/opentype.js/blob/10563b50d0dcd25cd78f6ea16287b810dd9f7523/LICENSE", "https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/src/geometries/ExtrudeGeometry.js", "https://github.com/adobe-fonts/source-han-sans/blob/6c709ca72d3d7c46ab42ebecc1a26e7d69595a37/LICENSE.txt"]
- **seekability_note**：纯函数：轮廓/几何准备后 t 驱动变换；从完整字体解析不应在 render(t) 中执行

### O2-05 · Source Han Sans 2.005 CN 静态字库基底

- **lane**：O2
- **url**：https://github.com/adobe-fonts/source-han-sans
- **pinned_ref**：6c709ca72d3d7c46ab42ebecc1a26e7d69595a37
- **license**：OFL-1.1：https://github.com/adobe-fonts/source-han-sans/blob/6c709ca72d3d7c46ab42ebecc1a26e7d69595a37/LICENSE.txt；Reserved Font Name 为 Source。
- **obligations**：{"attribution": true, "share_alike": true, "non_commercial": false, "no_derivatives": false, "note": "分发字体须附版权/OFL；禁止单独售卖字体；修改/子集名称不得用 Source；OFL保留范围仅字体，不约束所渲染的视频。"}
- **attribution_text**：字体基于 Adobe Source Han Sans 2.005（Copyright 2014–2025 Adobe），SIL OFL 1.1：https://github.com/adobe-fonts/source-han-sans/blob/6c709ca72d3d7c46ab42ebecc1a26e7d69595a37/LICENSE.txt。仅使用原字形渲染；如分发字体子集，另列子集名称及实际改动。 子集署名可用：本项目 AuditSubset Bold 基于 Adobe Source Han Sans 2.005，按本期字符子集化并去除 hint，名称已修改，依 SIL OFL 1.1 分发。仅在实际使用该子集及相同改动后附此句。
- **attribution_place**：资产包字体目录 LICENSE + 字体元数据；片尾/简介可选简短字体鸣谢
- **risks**：["源码 tag 2.005 与二进制 tag 2.005R 不同，本条 pin 为后者", "简体中文区域字形不应被泛 CJK fallback 悄悄换成日文字形", "未逐字核对《通用规范汉字表》一级3500字，不能把 cmap 数等同该覆盖证明", "OFL RFN改名需覆盖 name/CFF/typeface familyName 等，保留版权行的 Source 引用不等于保留字体名称"]
- **content**：{"format": "SubsetOTF/CN/SourceHanSansCN-Bold.otf；CN 区域静态 OTF 七字重文件", "bytes": 8569308, "coverage": "本次读取 Bold cmap 30,926 个映射码点、31,072 glyph；这是该二进制实测，不是全版本保证", "weights": ["ExtraLight", "Light", "Normal", "Regular", "Medium", "Bold", "Heavy"], "preview": "https://github.com/adobe-fonts/source-han-sans/blob/6c709ca72d3d7c46ab42ebecc1a26e7d69595a37/SourceHanSansReadMe.pdf"}
- **maps_to**：["theme 字体", "module 标题源字库"]
- **product_lines**：["card", "explainer", "showcase"]
- **adaptation**：B：每期子集化并按 RFN 改名；不建议直接在每个开场带全量字体
- **seekability**：不适用（静态素材）
- **runtime**：{"three": "字体与 Three 无关；r160 TTFLoader+FontLoader 的两组中文样本已通过 CPU几何测试", "offline": true, "react": false, "font_format": "静态 CFF OTF；troika不要直接换成 WOFF2"}
- **maintenance**：{"last_commit_date": "2025-06-18T20:25:31Z", "scope": "调查时默认分支最新提交；不是所选旧版本发布日期", "commit_sha": "0b993716f6910f0c8e00f957c767ab3cf5cb7602", "source": "https://github.com/adobe-fonts/source-han-sans/commit/0b993716f6910f0c8e00f957c767ab3cf5cb7602", "checked_at": "2026-10-02"}
- **verdict**：首推：四条中文标题路线共用的合法中文源字库，按本期字集构建闭包。
- **sources**：["https://github.com/adobe-fonts/source-han-sans/blob/6c709ca72d3d7c46ab42ebecc1a26e7d69595a37/SubsetOTF/CN/SourceHanSansCN-Bold.otf", "https://github.com/adobe-fonts/source-han-sans/blob/6c709ca72d3d7c46ab42ebecc1a26e7d69595a37/LICENSE.txt", "https://github.com/adobe-fonts/source-han-sans/blob/0b993716f6910f0c8e00f957c767ab3cf5cb7602/README.md"]

### O2-06 · Khronos CC0 小道具：BoomBox / WaterBottle，ToyCar 对照

- **lane**：O2
- **url**：https://github.com/KhronosGroup/glTF-Sample-Assets
- **pinned_ref**：f36bfdabd1031c3cf6689a50570b8cdf3678b49c
- **license**：模型及其直接关联的图像/二进制为 CC0-1.0；各模型 LICENSE.md 和 metadata.json 文档为 CC-BY-4.0；不覆盖 logo/trademark。逐模型 LICENSE.md 见 sources。
- **obligations**：{"attribution": false, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "此记录以模型/纹理为对象，CC0 无强制署名；若复制仓库 metadata/README/LICENSE 文档内容，需为 CC-BY-4.0 元文档另署名。不要把根目录文档许可套给模型。"}
- **attribution_text**：BoomBox / WaterBottle by Microsoft；ToyCar 原模型 by Guido Odendahl，扩展与场景 by Eric Chadwick；以上模型 CC0 1.0。源自 Khronos glTF Sample Assets：https://github.com/KhronosGroup/glTF-Sample-Assets/tree/f36bfdabd1031c3cf6689a50570b8cdf3678b49c。模型未修改。若重贴图/减面后使用，将末句改为实际修改说明。若复用元文档另附：Metadata © The Khronos Group，CC BY 4.0。
- **attribution_place**：CC0可选：资产包来源记录；复用元文档则在资产包说明附 CC BY 4.0 credit
- **risks**：["CC0不清除商标、外观设计或其他第三方权利；不要当成品牌授权", "ToyCar含 transmission/sheen/clearcoat 等扩展，108,936三角形远重于另两项；不作为 card 默认", "纹理占用远大于几何；把模型小等同包体小会误判", "设备截图槽不是这些模型已有合同；它们只是合法小道具基线"]
- **content**：{"models": [{"name": "BoomBox", "glb_bytes": 10614184, "triangles_gltf_unique_mesh": 6036, "preview": "https://github.com/KhronosGroup/glTF-Sample-Assets/blob/f36bfdabd1031c3cf6689a50570b8cdf3678b49c/Models/BoomBox/screenshot/screenshot.jpg"}, {"name": "WaterBottle", "glb_bytes": 8966700, "triangles_gltf_unique_mesh": 4510, "preview": "https://github.com/KhronosGroup/glTF-Sample-Assets/blob/f36bfdabd1031c3cf6689a50570b8cdf3678b49c/Models/WaterBottle/screenshot/screenshot.jpg"}, {"name": "ToyCar", "glb_bytes": 5422412, "triangles_gltf_unique_mesh": 108936, "preview": "https://github.com/KhronosGroup/glTF-Sample-Assets/blob/f36bfdabd1031c3cf6689a50570b8cdf3678b49c/Models/ToyCar/screenshot/screenshot.jpg"}], "measurement": "GLB字节数取固定 commit 的 GitHub blob metadata；三角数由同commit glTF索引 accessor count/3 求和，统计 unique mesh，不等于含实例后的全场景面数；无减面或纹理压缩测试"}
- **maps_to**：["module 内 glTF/纹理资源"]
- **product_lines**：["card", "explainer", "showcase"]
- **adaptation**：C：现有 media 类型未列 GLB；需 module 资源 manifest/加载ready/贴图色彩空间；B：选择 core变体，缩纹理后本地另行验证
- **seekability**：不适用（静态素材）
- **runtime**：{"three": "BoomBox/WaterBottle core glTF2.0，无扩展；r160 GLTFLoader 可支持（源码判断，未实渲）", "react": false, "offline": "本地 GLB可闭包；不选Draco/KTX2即可避免额外decoder；选择压缩时需把decoder/WASM入闭包"}
- **maintenance**：{"last_commit_date": "2026-09-28T15:15:02Z", "scope": "调查时默认分支最新提交；不是所选旧版本发布日期", "commit_sha": "f36bfdabd1031c3cf6689a50570b8cdf3678b49c", "source": "https://github.com/KhronosGroup/glTF-Sample-Assets/commit/f36bfdabd1031c3cf6689a50570b8cdf3678b49c", "checked_at": "2026-10-02"}
- **verdict**：首推：先用 WaterBottle/BoomBox 校准 glTF 资源合同；ToyCar仅重负载对照。
- **sources**：["https://github.com/KhronosGroup/glTF-Sample-Assets/blob/f36bfdabd1031c3cf6689a50570b8cdf3678b49c/Models/BoomBox/LICENSE.md", "https://github.com/KhronosGroup/glTF-Sample-Assets/blob/f36bfdabd1031c3cf6689a50570b8cdf3678b49c/Models/BoomBox/metadata.json", "https://github.com/KhronosGroup/glTF-Sample-Assets/blob/f36bfdabd1031c3cf6689a50570b8cdf3678b49c/Models/BoomBox/glTF/BoomBox.gltf", "https://github.com/KhronosGroup/glTF-Sample-Assets/blob/f36bfdabd1031c3cf6689a50570b8cdf3678b49c/Models/WaterBottle/LICENSE.md", "https://github.com/KhronosGroup/glTF-Sample-Assets/blob/f36bfdabd1031c3cf6689a50570b8cdf3678b49c/Models/WaterBottle/metadata.json", "https://github.com/KhronosGroup/glTF-Sample-Assets/blob/f36bfdabd1031c3cf6689a50570b8cdf3678b49c/Models/WaterBottle/glTF/WaterBottle.gltf", "https://github.com/KhronosGroup/glTF-Sample-Assets/blob/f36bfdabd1031c3cf6689a50570b8cdf3678b49c/Models/ToyCar/LICENSE.md", "https://github.com/KhronosGroup/glTF-Sample-Assets/blob/f36bfdabd1031c3cf6689a50570b8cdf3678b49c/Models/ToyCar/metadata.json", "https://github.com/KhronosGroup/glTF-Sample-Assets/blob/f36bfdabd1031c3cf6689a50570b8cdf3678b49c/Models/ToyCar/glTF/ToyCar.gltf"]
- **seekability_note**：不适用（静态素材）；旋转/飞入镜头可另用纯函数 t

### O2-07 · Pixal3D 内独立 CC0 的六个 Poly Haven HDRI

- **lane**：O2
- **url**：https://github.com/TencentARC/Pixal3D
- **pinned_ref**：f7cf38429b0bd264f1995f0f8743a88b1c728b94
- **license**：仅 assets/hdri/license.txt 的 CC0 HDRI：https://github.com/TencentARC/Pixal3D/blob/f7cf38429b0bd264f1995f0f8743a88b1c728b94/assets/hdri/license.txt；仓库代码 LICENSE 是 MIT，二者分开。
- **obligations**：{"attribution": false, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "仅选明确列出原始来源的6张；CC0无强制署名。AI生成模型/演示输出与本条无关，不采集。"}
- **attribution_text**：环境光图 City（Portland Landing Pad）by Greg Zaal / Poly Haven，CC0 1.0；经 Pixal3D 缩为1K并用 DWAB 压缩：https://github.com/TencentARC/Pixal3D/blob/f7cf38429b0bd264f1995f0f8743a88b1c728b94/assets/hdri/license.txt。本项目未另修改。使用其他文件时替换图名；若再次转换，按实际附加改动。
- **attribution_place**：可选：资产包来源/转换记录；通常无需视频署名
- **risks**：["night、studio 的原始来源在 license.txt 中标为 Probably，排除这两张，不随整目录接受", "City等虽有明确原始链接及许可记录，未在GitHub范围外重新核对创作者元数据；其他五图作者记录仅以该license为证", "该仓库是AI项目不等于本条摄影HDRI为AI生成；只收独立注明Poly Haven来源的既有图，不收项目生成内容", "1K/DWAB有损压缩已改变原图；需评估高亮裁切对镜面材质的影响"]
- **content**：{"format": "EXR（DWAB），候选6张，不含night/studio", "files_bytes": {"city.exr": 204863, "courtyard.exr": 255126, "forest.exr": 552641, "interior.exr": 189416, "sunrise.exr": 251877, "sunset.exr": 171164}, "measured": "city.exr 用 r160 EXRLoader CPU解析成功：1024×512，RGBA HalfFloat展开4,194,304 B；PMREM额外占用未测", "preview": "https://github.com/TencentARC/Pixal3D/blob/f7cf38429b0bd264f1995f0f8743a88b1c728b94/assets/app/hdri_city.png"}
- **maps_to**：["module/background 内部环境光资源"]
- **product_lines**：["card", "explainer", "showcase"]
- **adaptation**：C：补 EXR/IBL资源类型与准备期PMREM预算；B：离线装载并预过滤，只记录链接不导入
- **seekability**：不适用（静态素材）
- **runtime**：{"three": "r160 EXRLoader 的 city.exr CPU解析通过；其余文件及GPU颜色/PMREM未验收", "react": false, "offline": "EXRLoader、fflate、本地EXR均冻结；无需在线Poly Haven API", "gpu": "解码图约4MiB（此图half RGBA），加PMREM与渲染目标，数字非文件包大小"}
- **maintenance**：{"last_commit_date": "2026-09-01T12:01:59Z", "scope": "调查时默认分支最新提交；不是所选旧版本发布日期", "commit_sha": "f7cf38429b0bd264f1995f0f8743a88b1c728b94", "source": "https://github.com/TencentARC/Pixal3D/commit/f7cf38429b0bd264f1995f0f8743a88b1c728b94", "checked_at": "2026-10-02"}
- **verdict**：备选：GitHub可取得且有逐目录许可的小体积HDRI路线；先试city，六张不代表全部逐图实渲通过。
- **sources**：["https://github.com/TencentARC/Pixal3D/blob/f7cf38429b0bd264f1995f0f8743a88b1c728b94/assets/hdri/license.txt", "https://github.com/TencentARC/Pixal3D/blob/f7cf38429b0bd264f1995f0f8743a88b1c728b94/assets/hdri/city.exr", "https://github.com/mrdoob/three.js/blob/d04539a76736ff500cae883d6a38b3dd8643c548/examples/jsm/loaders/EXRLoader.js", "https://github.com/Poly-Haven/Public-API/blob/2b15bf094bde69b222a8f9b61e1a14e8e460c8a2/ToS.md"]
- **seekability_note**：不适用（静态素材）；固定环境或按t改变旋转/强度，不做跨帧累积

### O2-08 · ambientCG 的 SweetHome3D 纹理目录线索

- **lane**：O2
- **url**：https://github.com/fabien-michel/sweethome3d-textures-ambientcg
- **pinned_ref**：1a475099a89a9b979bbd15b6f59305d260795b80
- **license**：仓库 LICENSE 为 CC0-1.0：https://github.com/fabien-michel/sweethome3d-textures-ambientcg/blob/1a475099a89a9b979bbd15b6f59305d260795b80/LICENSE；README称纹理作者 Lennart Demes，并说代码和内容同许可。
- **obligations**：{"attribution": false, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "CC0没有强制署名；不能把此目录当成已核验所有上游纹理的包。"}
- **attribution_text**：Textures by Lennart Demes / ambientCG，CC0 1.0；目录由 Fabien Michel 整理：https://github.com/fabien-michel/sweethome3d-textures-ambientcg/tree/1a475099a89a9b979bbd15b6f59305d260795b80。来源线索，尚未导入或修改。
- **attribution_place**：如之后采用，资产包来源记录可选
- **risks**：["GitHub仓库有生成器和预览，实际 .sh3t 下载链接指向 murena.io，超出本轮 GitHub-only", "不运行会下载站外数据的 build.py；不会把预览拼图当作可直接使用的PBR贴图", "README体积是维护者近似声明，不是本次取得压缩包后实测"]
- **content**：{"format": "站外.sh3t包；GitHub内预览WEBP/生成脚本", "reported": "README 版本2025.05.06 声称1515纹理，256px/512px/1024px包约15.5/58.2/223.0MB；未下载核验", "preview": "https://github.com/fabien-michel/sweethome3d-textures-ambientcg/blob/1a475099a89a9b979bbd15b6f59305d260795b80/previews/Metal.webp"}
- **maps_to**：["仅参考：贴图来源线索"]
- **product_lines**：["card", "explainer", "showcase"]
- **adaptation**：D：站外线索；不是本轮可接纳素材
- **seekability**：不适用（静态素材）
- **runtime**：{"three": "图片解包后可贴图，当前尚未拿到逐文件manifest", "react": false, "network": "实际资产站外，未访问或下载"}
- **maintenance**：{"last_commit_date": "2025-05-06T07:54:21Z", "scope": "调查时默认分支最新提交；不是所选旧版本发布日期", "commit_sha": "1a475099a89a9b979bbd15b6f59305d260795b80", "source": "https://github.com/fabien-michel/sweethome3d-textures-ambientcg/commit/1a475099a89a9b979bbd15b6f59305d260795b80", "checked_at": "2026-10-02"}
- **verdict**：排除：本轮GitHub-only无法取得并逐文件核验实际纹理包；保留来源线索。
- **sources**：["https://github.com/fabien-michel/sweethome3d-textures-ambientcg/blob/1a475099a89a9b979bbd15b6f59305d260795b80/LICENSE", "https://github.com/fabien-michel/sweethome3d-textures-ambientcg/blob/1a475099a89a9b979bbd15b6f59305d260795b80/README.md", "https://github.com/fabien-michel/sweethome3d-textures-ambientcg/blob/1a475099a89a9b979bbd15b6f59305d260795b80/catalog_header.txt"]

### O2-09 · KSRSS EarthColor 地球纹理线索

- **lane**：O2
- **url**：https://github.com/KerbalFrench/KSRSS-Textures
- **pinned_ref**：98d867ae9fb00f84c87529b2fff37daf71bb76c6
- **license**：README声称 CC-BY-NC-SA-4.0；固定树未找到 LICENSE 文件，按本次规则不接受。个别源和README.txt许可表述也不完全一致。
- **obligations**：{"attribution": true, "share_alike": true, "non_commercial": true, "no_derivatives": false, "note": "此为README声称的BY/NC/SA，不代表已许可通过。无ND声明不等于权利链完备。"}
- **attribution_text**：尚不提供可用于成片的确定署名：KSRSS Team及上游作者链需先补正式许可文件和逐图来源。调查线索：https://github.com/KerbalFrench/KSRSS-Textures/blob/98d867ae9fb00f84c87529b2fff37daf71bb76c6/README.md。
- **attribution_place**：不得用于成片；待许可补齐后按实际作者/改动生成署名
- **risks**：["无LICENSE违反本轮明确门槛；不是因为NC被拒，NC本来允许", "多级NASA/JPL/Celestia/个人改图链，不能一概称NASA公有领域", "DDS法线/高度贴图需转码及色彩空间验证", "未证明中国地图边界合规；地球外观也不能当成合规中国地图来源"]
- **content**：{"format": "DDS", "source_sizes": {"4096/EarthColor.dds": 11184976, "8192/KSRSS-Textures/PluginData/EarthColor.dds": 44739408}, "sizes_note": "固定Git树字节数；未下载图片、未判断投影或内容正确性；静态纹理无面数", "preview": "https://github.com/KerbalFrench/KSRSS-Textures/blob/98d867ae9fb00f84c87529b2fff37daf71bb76c6/README.md"}
- **maps_to**：["仅参考：地球纹理"]
- **product_lines**：["card", "explainer", "showcase"]
- **adaptation**：D：许可文件/逐图链和地图合规缺口未解决
- **seekability**：不适用（静态素材）
- **runtime**：{"three": "需DDSLoader/转码，未验证r160；不应在hook运行时加载KSP插件", "react": false, "offline": "理论可，但未接纳"}
- **maintenance**：{"last_commit_date": "2020-10-22T15:01:53Z", "scope": "调查时默认分支最新提交；不是所选旧版本发布日期", "commit_sha": "98d867ae9fb00f84c87529b2fff37daf71bb76c6", "source": "https://github.com/KerbalFrench/KSRSS-Textures/commit/98d867ae9fb00f84c87529b2fff37daf71bb76c6", "checked_at": "2026-10-02"}
- **verdict**：排除：缺正式LICENSE和逐图溯源；地球纹理不提供地图合规承诺。
- **sources**：["https://github.com/KerbalFrench/KSRSS-Textures/blob/98d867ae9fb00f84c87529b2fff37daf71bb76c6/README.md", "https://github.com/KerbalFrench/KSRSS-Textures/blob/98d867ae9fb00f84c87529b2fff37daf71bb76c6/8192/KSRSS-Textures/README.txt"]

### O2-10 · drei-assets Mac/设备样机文件

- **lane**：O2
- **url**：https://github.com/pmndrs/drei-assets
- **pinned_ref**：456060a26bbeb8fdf79326f224b6d99b8bcce736
- **license**：固定仓库未见 LICENSE；README 多种素材各自来源，不可从 pmndrs/drei 的 MIT 推导本仓模型许可。
- **obligations**：{"attribution": false, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "未知授权时四布尔值仅代表未找到有效义务文本，不代表可自由使用。"}
- **attribution_text**：不可生成有效复用署名；排除直到找到该具体模型许可与作者证据。
- **attribution_place**：不得用于成片
- **risks**：["README许可叙述不等于每个GLB授权；模型可能有品牌商标与外观设计风险", "去掉Apple logo也不能补回缺失的模型再分发许可"]
- **content**：{"format": "GLB/纹理等混合；不做全仓数量/面数断言", "size": "排除前未下载统计", "preview": "https://github.com/pmndrs/drei-assets/blob/456060a26bbeb8fdf79326f224b6d99b8bcce736/README.md"}
- **maps_to**：["仅参考：设备样机"]
- **product_lines**：["card", "explainer", "showcase"]
- **adaptation**：D：不可用来源；建议本地另设计无品牌几何设备框，不把此模型当输入
- **seekability**：不适用（静态素材）
- **runtime**：{"three": "未知；drei React层不是glb许可来源", "react": "素材本身不需要React，但不能据此跳过授权", "offline": "不进入闭包"}
- **maintenance**：{"last_commit_date": "2023-01-04T12:28:51Z", "scope": "调查时默认分支最新提交；不是所选旧版本发布日期", "commit_sha": "456060a26bbeb8fdf79326f224b6d99b8bcce736", "source": "https://github.com/pmndrs/drei-assets/commit/456060a26bbeb8fdf79326f224b6d99b8bcce736", "checked_at": "2026-10-02"}
- **verdict**：排除：缺资产许可。
- **sources**：["https://github.com/pmndrs/drei-assets/blob/456060a26bbeb8fdf79326f224b6d99b8bcce736/README.md", "https://github.com/pmndrs/drei-assets/tree/456060a26bbeb8fdf79326f224b6d99b8bcce736"]

### O2-11 · 旧 Khronos glTF-Sample-Environments 整包

- **lane**：O2
- **url**：https://github.com/KhronosGroup/glTF-Sample-Environments
- **pinned_ref**：83d50e3aa24052872569c33568809c08bec1bcba
- **license**：根目录未找到 LICENSE；README把多张图片链接到 USC/HDR Labs/HDRI Hub 等各自站外源，不能继承Viewer代码许可。
- **obligations**：{"attribution": false, "share_alike": false, "non_commercial": false, "no_derivatives": false, "note": "未知授权，四布尔值不能作为自由使用授权。"}
- **attribution_text**：不提供确定复用署名；需每张HDRI原始许可，当前整包排除。
- **attribution_place**：不得当统一许可素材包
- **risks**：["Git LFS的132/133字节指针不是HDRI真实大小", "原图站外、多源许可，代码仓库名/官方组织身份不是版权授权", "预过滤cube贴图也继承原图许可，不是新生成就无版权限制"]
- **content**：{"format": "HDR、JPG预览、预过滤环境", "size": "真实LFS文件大小未取；没有用指针bytes冒充素材bytes", "preview": "https://github.com/KhronosGroup/glTF-Sample-Environments/blob/83d50e3aa24052872569c33568809c08bec1bcba/README.md"}
- **maps_to**：["仅参考：环境光资料"]
- **product_lines**：["card", "explainer", "showcase"]
- **adaptation**：D：整包许可不明确；本轮不采集
- **seekability**：不适用（静态素材）
- **runtime**：{"three": "IBL烘焙产物未验证和r160PMREM格式是否一致", "react": false, "offline": "LFS大文件实际下载未验证"}
- **maintenance**：{"last_commit_date": "2020-05-08T04:13:32Z", "scope": "调查时默认分支最新提交；不是所选旧版本发布日期", "commit_sha": "83d50e3aa24052872569c33568809c08bec1bcba", "source": "https://github.com/KhronosGroup/glTF-Sample-Environments/commit/83d50e3aa24052872569c33568809c08bec1bcba", "checked_at": "2026-10-02"}
- **verdict**：排除：缺正式资产许可，来源许可证不统一。
- **sources**：["https://github.com/KhronosGroup/glTF-Sample-Environments/blob/83d50e3aa24052872569c33568809c08bec1bcba/README.md", "https://github.com/KhronosGroup/glTF-Sample-Environments/tree/83d50e3aa24052872569c33568809c08bec1bcba"]