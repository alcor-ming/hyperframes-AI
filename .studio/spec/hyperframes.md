# HyperFrames 实现与 QA

## 实现

- Windows 在 Work-local 或已登记 AssetSource 编写 Scene、模块、GSAP / Three / shader 与视觉内容；WSL 只修 Harness、宿主、合同和依赖装配。安装包、已接纳包、vendor 与 Accepted Snapshot 不原地改，必要变化派生新源 / 版本。
- 默认 Scene 组合模块与本地媒体，旧完整组件只读兼容；M1 仅接入已交付的 module/media 子集，不假称 Template / Recipe 或通用依赖构建器已完成。Scene 只安排所需 Beat，允许计算布局和内聚空间舞台，不强制双画幅或透明根层。
- 一个 Variant 只读取一个 Profile。
- 先整片 Plan，再一个真实 Scene 动态参考；优先复用当前 M2–M3 源码与画面，使用实际音频裁取或明确 provisional 预算。用户一次方向批准后扩成完整 planned-placeholder Draft，不逐 Scene 审批；素材齐备后输出最终 Draft。旧 reference/layout 记录保持原语义，不作为新动态参考通过证明。
- 日常制作与 QA 默认由 Work CLI 启动锁定官方 Studio；当前工程可编辑，登记版本只打开独立复制的审阅副本，不暴露冻结快照、vendor 或外部资产。历史自制页面仅限显式 `--legacy`。实际项目 URL 和定位端口来自启动结果，不硬编码或猜测；旧 MP4 / QA 与源码不一致时重新生成受影响证据。
- 宿主 Timeline 必须同步、确定性构建，使用 `{ paused: true }` 并注册到 `window.__timelines`；模块将动作写入该 timeline，不另行注册全局播放权。异步媒体 / 几何准备须完成后再同步建 timeline，ready 前不首次 seek。
- 动作不依赖 `Math.random()`、`Date.now()`、实时 delta、异步 Timeline、`repeat: -1` 或多个 Timeline 同时修改同一属性；可用固定 seed 初始化数据，再按时间直接求值。
- composition 或 Scene 保留 `S01` 等稳定 ID；结构性偏离返回 Animation Plan。
- `talking_head` 仅在人为主叙述的适用 Scene 保留人物布局；A/B-roll 按各 Scene 叙事职责安排，主声源贯穿切换且只播放一次，其他视频音轨按需要明确静音。
- 依据主类型、Plan 实际屏幕文字及选材实现 seek-safe 动画。动画型不强制机制演绎，文字型保留卡片/装饰与局部强调；SVG/icon/图片允许装饰价值，但不以细碎运动干扰阅读。Research 不规定动画机制。
- 动效按表达需要组织焦点、关系、证据、对象转化与交接，不要求每组件独立入场。稳定阅读贯穿 Scene，不以统一结尾停顿代替；只有可定义的真实进度才使用进度条，演示值明确标记。
- Scene 布局按 Plan 预留图片 / 视频位和需要阅读的文字位；素材内已清楚呈现的信息不重复覆盖。缺少素材时保留稳定 Slot，不用虚构素材填满。
- 逐 Scene 读取 Plan 的精确资产引用和 Binding；全片主题不等于局部结构通用。角色、连接、条件、去向、反馈及结果进入实际图形 / 状态，不能把不同语义字段统一压成文字行。未支持类型明确返回当前 Scene 的实现缺口，不静默 fallback 普通卡片；同构表达允许复用。
- Skill 讲解按需要使用真实截图与完整解释；允许对比、列表、左右分栏和稳定证据页，按真实文字与音频安排阅读，不强迫每场发生变形。

## 混合时间与资源

- 先核对本地 HyperFrames / GSAP / Three.js 版本与适配器，优先复用已有 `hf-seek` / `window.__hfThreeTime` 接口；上游存在不代表当前安装可用。
- 使用 GSAP 的工程和组件须在本地 GSAP 后显式加载同版本的 `MotionPathPlugin.min.js`，两者随资产进入快照闭包。锁定 Studio 0.8.27 会在插件缺失时自动尝试 CDN；即使当前动作未使用该插件，也不能依赖这个联网 fallback。无 GSAP 的静态样段不因此增加依赖。
- DOM / GSAP 与 WebGL 共用全局时间，明确 Scene 偏移和局部重定时；同帧先求值属性、镜头与 shader，再绘制。成片动作不能以独立 RAF 或 `setAnimationLoop()` 为时间权威。
- 渲染关键状态不能仅放在 `onUpdate` / `onComplete` 回调；随机 seek 可能抑制回调。Flip、拆字与布局状态在字体/资源就绪后固定，不在播放回调中才补正文。
- 优先复用返回有限 Timeline 的小函数或既有效果注册接口，不另建引擎。效果只暴露实际需要的配置，由宿主控制尺寸、主题、资源、seed 与时间；文字默认 DOM / SVG，效果不拥有全局叙事。
- Three.js 与 addons 固定同版本，画布尺寸、像素比与色彩配置由工程控制。纹理、shader、模型、效果代码及其他实际依赖进入现有快照闭包，抓帧不临时联网；提供就绪与释放行为，不释放他人共享资源。
- 不引入依赖历史帧的物理模拟、反馈 shader 或累积拖尾，除非可重建任意时刻或已烘焙。Three.js 故障只阻塞相关 Scene，不静默以静态图冒充通过；主视觉替代沿用局部确认边界。

唯一动态参考及包含混合效果的 Draft 应实际播放、暂停、拖动、倒跳、再播放，并按 `[t3, 0, t1, t3]` 抓帧比较同一时刻。检查实际 Scene 范围、DOM/WebGL 同帧、阅读、就绪与释放；单 Scene 不证明全片正确。完整 planned-placeholder Draft 可缺已登记素材，但所有 Scene 及实际承诺动作必须存在。最终 Draft/Final 必需资源和效果闭合。Mock/静态检查不算 Windows 原生渲染通过，技术夹具不算生产复用。

需要混合求值时，可将 `.studio/runtime/scene-binding.js` 复制到 Work 的 `project/runtime/`，由 `HarnessScene.bindScene({start, duration, timeline, ready, renderAt, dispose})` 接到当前 HyperFrames 的 `hf-seek` / `waitUntil`。`start` 相对当前 composition 文档；绑定器拥有未单独注册的局部 paused Timeline，先求值再调用 `renderAt(localTime)`，宿主仍负责可见性。不要再将同一 Timeline 加入主时间轴或注册两次。`ready` 等待资产，不异步拼装 Timeline；释放时只清理绑定器自身资源。普通 GSAP 场景不需要此接线。

`tests/visual-mixed.mjs` 使用本地 `HF_PACKAGE`、`GSAP_FILE`、`THREE_FILE`、`CHROME_PATH` 跑双绑定与实际短片；其输出目录作为 `MIXED_FIXTURE`，配合 `PLAYWRIGHT_PACKAGE` 运行 `tests/visual-plan.mjs` 验证播放器和生命周期。它们是技术夹具，不是已批准组件或生产复用证据。无硬件 WebGL 的 WSL 可用 `preview render --software-gl`，不会替换效果为静态图。

## 音频与裁取

优先复用 timestamps 与 `section_map.json`。语义 cue 定位 Anchor、字符范围或明确 occurrence，未可靠对齐的字符不均匀插值。源片段采用半开区间，按 `timeline_in + (source_time - source_in) / rate` 映射；多 take 明确选择，被删除词无有效 cue。单 Scene 预览减去 crop 起点而不改原对齐，仅在输出 fps 时量化。

视觉事件选择动作开始、完成或结果可读，不自动将动画起点贴词首。SFX 按内部 hit offset 反算起点，负起点明确 preroll/裁切/替换。Preview 和 render 共用 cue/mix 输入，不以 seek 回调即时播放音轨；关键画面同样可按目标时间重建。音乐分析只在需要时按 hash/参数离线缓存，不依赖实时 WebAudio；缺 BGM 或 Blender 不阻塞非依赖场景。

验证源声音、工程映射、命中前后帧及带声短片；未试听明确说明，计算误差不冒充 ASR 声学精度。已有音轨不重复 ASR。

## Draft QA

在项目目录使用已锁定的本地 CLI；以下 `npx --no-install` 不下载或升级依赖：

```bash
npx --no-install hyperframes check
```

修复错误、空 Scene、越界、遮挡、不可读和严重节奏问题。对照 Plan 检查问题 Scene 的稳定状态及核心变化：连接有指向，条件分支可区分，反馈在状态中可见，选稿与必需 Slots 不丢失。只看开头或 contact sheet、仅有字段 / CSS 差异不算语义通过；同 easing 或相似外观不自动失败。普通 Warning 不阻止 Draft。Plan 登记的 planned placeholders 允许全片预览，准确标出缺口；占位不是代码错误的豁免，也不具备最终交付资格。只有 full 范围且必需素材齐备的版本能获得完整接受并进入 Final；单 Scene 方向批准不能代替。

在 Studio 按主类型核对 Plan：动画型看对象/比较/关系/过程，文字型看卡片阅读/装饰/关键词强调；检查主辅载体及回接、承诺动作和素材。保原声和总时长，整幅画面完全静止不超过2秒而正文可稳定阅读；实际播放人工判断可感知变化及阅读干扰，不以 tween 数量判定，自动容差尚待 Windows 实测。不能凭 SVG 存在或文件齐备宣称设计完成。

技术检查、设计兑现和用户接受分开。素材齐备后无文件参数的 `preview register` 冻结 executable Studio Draft，再 `preview open draft-vNNN` 审阅准确隔离副本、`preview accept draft-vNNN`。无需完整 Draft MP4 或伪造收据；旧文件型兼容。核验 Windows Studio 声音、连续播放、跳转/回拖，局部限制可用带声短段，未听音明确未验证。素材 complete/技术 PASS 不替代设计和接受。

## Final QA

从准确 Accepted Draft 的闭合快照正式渲染，保留收据，不从变化的可编辑工程冒充接受版本：

```bash
./work --work <id> --variant <id> preview render <draft-id> --output <final.mp4> --final
```

新编码文件检查流、规格（60fps high）、原音时长、全量解码、代表帧及必要音频核验；实际缺陷修复后重渲染。Final Error 阻止 `./work finalize ... --qa-passed`，通过后 Finalize 自动归档；明确只导出/暂不归档等限制优先。

QA 按影响范围：已接受且未变仅检查来源/证据适用性；局部变化只查受影响 Scene、状态和交接；共享布局/时间线/宿主变化按依赖扩展。编码 QA 不重审已接受观点/设计，仅 Finalize/归档核对来源、收据、文件、目标及归档结果，不重复审片/渲染。只报告结果与真实未验证项。
