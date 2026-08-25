# Component-Driven Motion Beta 1｜PRO 交接说明

> 日期：2026-08-24
> 状态：Open Design 组件设计已冻结，当前 Work 的 `ANIMATION_PLAN.md` revision 1 已获批；生产组件尚未落库或安装。
> 用途：把现有 PRD 决策、已完成组件和真实缺口交给 PRO，供其设计下一步开发流程。本文件不是新的 PRD 真源。

## 1. 本次目标

Beta 1 优先验证两件事：

1. 能否把一个真实 Work 中通过 Open Design 验收的组件，沉淀为通用、不可变、可独立检查的公共组件。
2. 能否让 Work 安装精确副本并稳定渲染，之后再由另一条真实 Work 复用同一个 `component_id@vN`，而不重写内部实现。

本轮只完成阶段 A 的设计冻结与正式 Plan 批准，并为开发流程提供输入。不要把“13 个原型已完成”误读为“13 个公共组件已完成”。

## 2. 真源与权限边界

| 层级 | 当前真源 | 权限边界 |
|---|---|---|
| 产品要求 | `docs/PRD/PRD_MASTER.md`、`docs/PRD/hyperframes-component-motion.md` | 本文只整理，不替代 |
| 批准前组件设计 | Open Design 冻结 artifact | 冻结拆分、视觉结构、关键状态和可感知内部动效 |
| 当前作品编排 | 当前 Variant 的 `ANIMATION_PLAN.md` revision 1 | 记录 Scene、组件引用、Slots、时间、组合证据与 custom gaps |
| 公共生产组件 | `.studio/components/<component-id>/vN/` | 只有落库后才成为公共实现真源；整数版本不可覆盖 |
| 作品运行副本 | Work 本地组件目录 | Work 只从精确副本渲染，公共升级不能改变既有 Draft |

批准和完成必须分开记录：

- `design-frozen`：Open Design 视觉与内部动效已经冻结。
- `library-approved`：用户允许该设计成为公共组件目标。
- `production-installed`：公共合同、源码、hash 与 Work 副本已经落地并通过检查。
- `reused`：另一条真实 Work 直接使用同一个不可变版本，且没有改写内部 DOM、CSS 或 GSAP 编排。

当前只达到前两层；`production-installed` 和 `reused` 均未发生。

## 3. 已确认的 Beta 1 产品边界

- 唯一 Profile：`optical_fluidity`。
- 当前验收组合：`pure_hyperframes + module_stage + 4:3`。
- 组件兼容键只声明 `profile + subtemplate`；画幅由 Work 与 Subtemplate 组合层负责。
- 公共版本只使用不可变整数 `v1`、`v2`，不使用 SemVer，不覆盖已发布版本。
- 组件发现直接读取 `.studio/components/**/COMPONENT.md`，不新增 `registry.json`。
- 继续复用现有 HyperFrames workflow、CLI、GSAP 与 QA 能力；Beta 1 不新增 Component Planner Skill、评分器、组件浏览器、在线 Registry、运行时服务或依赖。
- 公共组件只保存合同、代码、无版权风险的默认数据和通用图形；Work 文案、真实媒体、截图、私有链接与运行状态不得进入公共目录。
- 公共组件缺失或不兼容时失败关闭到 `custom`，不得伪造匹配。
- 正式 Plan 批准后才允许落库和复制到 Work；Plan 批准不等于 Draft 接受。

## 4. 当前 Work

| 字段 | 值 |
|---|---|
| Work | `work-20260821-一个人做号太累-先装这10个skill` |
| Variant | `main` |
| Template | `pure_hyperframes` |
| Profile | `optical_fluidity` |
| Subtemplate | `module_stage` |
| Ratio | `4:3` |
| 时间真源 | `materials/source-video.mp4` 原音频，`86.485s` |
| Script | revision 1，`verbatim` |
| Research | revision 1，`ready` |
| Animation Draft | revision 3，已由正式 Plan 替代 |
| Animation Plan | revision 1，已于 2026-08-24 获批 |
| 当前停止点 | 等待 PRO 给出下一步生产开发流程；未安装组件、未实现 HTML、未注册 Draft |

## 5. Open Design 已完成资产

Open Design project `Hyperframes` 已冻结 `COMPONENT_SPLIT.md` revision 12，包含 B00 与 P001-P012 共 13 个可独立 Preview/seek 的原型。

| 编号 | Artifact / revision | 核心状态变化 | 当前分类 |
|---|---|---|---|
| B00 | `chapter-intro-prototype.html` rev.5 | 左侧章节身份、右侧可选证据、进度与交接 | 唯一 `library-approved` 目标 |
| P001 | `opening-weave-core-prototype.html` rev.3 | 粒子球聚合为节点链，建立全片关系 | `work-local` |
| P002 | `topic-radar-core-prototype.html` rev.4 | 多源信号经筛选收敛为选题池 | `work-local` |
| P003 | `viral-breakdown-core-prototype.html` rev.2 | 内容表面被拆成 Hook、卖点和节奏层 | `work-local` |
| P004 | `script-draft-core-prototype.html` rev.3 | 一句话主题生长为待审文档初稿 | `work-local` |
| P005 | `storyboard-plan-core-prototype.html` rev.2 | 脚本拆分并组装成分镜计划 | `work-local` |
| P006 | `tone-rewrite-core-prototype.html` rev.1 | AI 腔被标记、梳理并改为本人终审稿 | `work-local` |
| P007 | `cover-title-core-prototype.html` rev.1 | 内容核折射成三个布局不同的候选 | `work-local` |
| P008 | `graphic-card-core-prototype.html` rev.1 | 同一内容结构依次重排为三种图文形态 | `work-local` |
| P009 | `material-archive-core-prototype.html` rev.1 | 异构素材获得溯源标签、入架并被检索命中 | `work-local` |
| P010 | `data-review-core-prototype.html` rev.3 | 预期与实际示意轨迹形成偏差问题结 | `work-local` |
| P011 | `weekly-report-core-prototype.html` rev.1 | 周记录绑定成报告，实验卡进入下一周 | `work-local` |
| P012 | `production-loop-core-prototype.html` rev.2 | 光点经过十个节点回到起点，收束为工具包 CTA | `work-local` |

这里的 `work-local` 是明确产品决定，不是待 PRO 批量转公共组件的 Backlog。只有后续真实复用需求和用户授权同时成立，才进入新的公共组件设计流程。

## 6. 代表性组合证据

已完成 `combination-preview-b00-p002.html` 与 `COMBINATION_PREVIEW_HANDOFF.md`，只验证 B00 向 P002 的真实搭配，不制作整片：

- 画布 `1440 x 1080`，4:3，总长 `8.15s`。
- B00 在 `0-1.60s` 建立章节；外层推送在 `1.95-2.35s`。
- P002 内部时间线从 `1.95s` 开始，在 B00 退出期间已可见，`7.75s` 完成 Hero，保持到 `8.15s`。
- 关键帧 `2.15s` 同时看到 B00 退出与 P002 进入；`2.35s` 没有空白舞台。
- `7.75s` 与 `8.15s` 截图 hash 一致，重复 seek 的 Hero 像素差只剩抗锯齿级误差。
- Open Design lint 为 0 errors；组合修订未改写 13 个冻结独立原型。

这份 Preview 是正式 Plan 的组合证据，不是公共组件已安装的证明。

## 7. 首个公共组件目标

### `chapter-intro@v1`

**来源**：B00 `chapter-intro-prototype.html` rev.5。
**Motion Recipe 计划名**：`chapter-intro-reveal`。
**兼容目标**：`optical_fluidity + module_stage`。
**当前状态**：用户已批准为 Beta 1 唯一公共组件目标；尚无 `COMPONENT.md`、公共 `component.html`、源码 hash 或 Work 副本。

**通用语义职责**：

- 建立同级模块的序号、名称、职责和进度位置。
- 可选展示一份真实证据；没有证据时仍保持完整构图。
- 通过明确 Handoff 把焦点交给下一个主组件。

**反例**：

- 不把它设为每个 Scene 的强制介绍页。
- 不在其中完成章节的全部主叙事。
- 不因存在右侧区域就强制要求截图或外部媒体。
- 不把章节位置伪装成任务完成率或业务指标。

**Plan 已定义的最小 Slot 输入**：

| Slot | Required | 说明 |
|---|---|---|
| `chapter_index` | 是 | 当前章节序号 |
| `chapter_total` | 是 | 同级章节总数 |
| `title` | 是 | 章节名称 |
| `summary` | 是 | 最多两行的职责说明 |
| `progress` | 是 | `0-1` 的章节位置 |
| `icon` | 否 | 本地通用图标 |
| `evidence` | 否 | Work 本地已确认媒体 |
| `source_label` | 否 | 经事实核验的来源标签 |

PRO 需要把这些 Plan 输入收敛为正式公共合同，并补齐：字段类型、默认 Preview 数据、最长中文、缺失 Optional Slot、允许的 `timeScale` 范围、安全区、检查时间、Profile token 映射、资产回退和不可改边界。

## 8. 复用能力的最低闭环

Beta 1 不需要新的管理系统，只需把现有能力串成可验证闭环：

1. **发现**：workflow 直接扫描 `COMPONENT.md`，按语义职责、反例、Profile 与 Subtemplate 判断是否匹配。
2. **引用**：正式 Plan 写入精确 `component_id@vN`、Motion Recipe、Slots、States、时间映射和证据。
3. **落库**：批准后新增一个不可变目录，不维护第二份 Registry。
4. **安装**：复制精确源码进 Work，记录公共源 hash 与 Work 副本 hash。
5. **运行**：Work 只引用副本；断开公共目录和 Open Design 后仍能 Preview/Render。
6. **适配**：外层只允许 Slots、位置、尺寸、offset、整体 `timeScale`、Hero/Handoff hold。
7. **保护**：内部 DOM、CSS、状态顺序或 GSAP beat 变化必须发布新公共版本，或明确保持 Work-local。
8. **检查**：独立 Preview、HyperFrames Check、Opening/Build/Hero/End、边界输入、重复 seek、像素对照和代表性组合检查。
9. **跨 Work 证明**：阶段 B 由另一条真实 Work 直接安装并使用同一个 `chapter-intro@v1`，不修改公共源和首个 Work 副本。

## 9. PRO 需要设计的下一步流程

请围绕以下最小生产路径给出开发方案，不扩成组件平台：

1. 如何从 B00 冻结 artifact 做最小规范化，生成 `COMPONENT.md + component.html`，同时保留内部实现和动效一致性。
2. 使用现有脚本或最少新代码完成“公共源 -> Work 副本 -> 双 hash 记录”；若直接文件复制已足够，不新增 CLI。
3. Work 本地组件目录、引用方式和 hash 记录放在哪里，才能被 Snapshot、Draft 和 Final 一起冻结。
4. 现有 HyperFrames CLI 哪些命令承担 lint、check、snapshot、repeat-seek 与像素比较；缺少的检查只补最小可运行脚本。
5. 如何用当前已批准 Plan 驱动 P001-P012 Work-local 实现，并确保 B00 + P002 的生产组合不出现空帧。
6. 哪些失败必须在 HTML 实现或 Draft 注册前中止，例如 artifact 不唯一、hash 变化、Slot 溢出、seek 不稳定、`timeScale` 超界或画幅失效。
7. 阶段 A 完成后，如何用另一条真实 Work 进行阶段 B 复用验收，而不提前创建演示 Work 或伪造复用。


方案给出后再进入生产开发；当前不需要新建 Work、补第二份 PRD、批量公共化 P001-P012 或提前实现阶段 B。
