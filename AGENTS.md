# HyperFrames AI 创作 Harness

## 工作边界

- 本仓库公开管理 Harness 规则、模板、Profile 接入、Skill 路由与 Work CLI。
- 所有作品均位于 `works/`，包括文案、媒体、工程、Draft、Final 和运行状态；这些内容不得进入 Git。
- 不发布内容、不登录平台、不购买额度。外部或付费服务仍需用户明确授权。
- v1 不生成 AI 图片、不调用 `design-taste-frontend`、不查询图片 Prompt 库，也不生成或烧录底部字幕。

## 启动顺序

1. 运行 `./work current`；没有 Current 时运行 `./work list`，不得猜测作品。
2. 读取当前 `WORK.md`、`variant.yaml`、`SCRIPT.md`。
3. 读取 `.studio/workflow.md` 和当前 Template 对应的 Recipe。
4. 通过 `.studio/capabilities.yaml` 只读取当前 Variant 选定的一套 Profile。
5. 进入视觉设计时再读取 `RESEARCH.md` 与 `ANIMATION_PLAN.md`；进入实现或 QA 时才读取对应 `.studio/spec/`。

不要默认加载全部 Profile、全部 DBS Skill、Examples、Migration、发行文件、全部 QA 历史或全部 Draft 快照。

## 创作真源

- `source.md`：主要原始基线，DBS 不覆盖。
- `SCRIPT.md`：当前 Variant 唯一口播正文；批准后的隐藏段落 ID 保持稳定。
- `RESEARCH.md`：与当前 Script Revision 对齐的联网资料、可视化机制与事实边界；不反向改写口播。
- `PACKAGE.md`：标题、封面、发布说明等非口播内容，不阻塞视觉制作。
- `section_map.json`：实际录制或配音与 Script Anchor 的机器对齐结果；实际媒体是时间权威。
- `ANIMATION_PLAN.md`：正式 HTML 制作前唯一必须批准的视觉设计 PRD。
- `variant.yaml`：当前 Variant 状态，由 CLI 与 Agent 更新。

## 创作检查点

- 下载视频转录后必须在 `SCRIPT.md` 中明确选择 `dbs` 或 `verbatim`：前者允许多轮 DBS 修改并在正文变化后等待批准；后者逐字保留口播与原时间戳，不运行正文改写。
- DBS 实际修改口播正文时，等待用户批准 `SCRIPT.md`；只诊断或只改包装文案时不等待。
- Script 确定后，按口播 Anchor 联网研究并完成同一 Variant 的 `RESEARCH.md`；Script Revision 变化后旧研究失效。
- `ANIMATION_PLAN.md` 必须整体批准后才能正式实现 HTML 和 Draft。
- Final 必须从用户接受的 Draft 源码快照继续。
- 只在 Scene 数量、顺序、视觉目标、Hero State、Template、Profile 或文案结构发生实质变化时重新批准 Plan。
- 时间码、easing、换行、安全区、性能和不改变 Hero State 的布局修复无需重新批准。

## 模板

- `talking_head`：先完成文案，再录制人物视频，以实际音频生成 `section_map.json` 后设计画面。
- `pure_hyperframes`：可先用估算时间完成视觉 Draft；用户接受 Draft 后接入正式配音并仅做重定时。
- 人物持续作为主视觉时才使用 `talking_head`；否则使用 `pure_hyperframes`，不增加第三套模板。

## 用户回复

只展示实际设计结果、变更、阻塞和需要决定的内容。不要展示读取清单、逐项 QA、审批证明或流程自证。Plan 首版可以完整展示，后续只展示变更 Scene 和未解决决策。

## 生命周期

- Work 和 Variant 的创建、指针、等待、Park、Draft 注册、Final、Archive 与 Reopen 只通过 `./work` 管理。
- CLI 只管理生命周期和文件一致性；文案、Scene、视觉方向与 HTML 实现仍由 Agent 判断。
- Final 是本地交付物，不表示已发布。
