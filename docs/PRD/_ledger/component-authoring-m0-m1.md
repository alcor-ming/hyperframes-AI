# Windows Component Authoring M0-M1 决策记录

## 原始请求与范围

用户请求：`C:\Users\Jym\Downloads\hyperframes-component-refactor-execution-plan-v3.1.md,创建新task，根据本机实际情况优化，先完成M0-M1后，在windows侧部署。然后我在windows侧安排M2-M3任务`。

v3.1 方案及该请求共同授权先落实 M0-M1 并部署工具候选；不再添加 PRD 审批。M2-M3 内容由用户在 Windows 分派。

## 已知与缺口

- 已知：现有候选构建、Windows 固定运行时、session、Work Review、Component 接纳与 vendor/Lock 均可复用。
- 已知未知：生产资产源/库未登记，真实困难 Work 未指定；不猜路径、不搬库、不冒充业务验证。
- 已澄清假设：视觉资产包含 JS/shader 不等于 Harness 工具代码；Windows 可修改指定可编辑源，不能修改安装包或冻结版本。
- 主要风险：全局 Asset 配置漂移、继承环境污染、候选覆盖共享入口、Review 接纳流入生产、依赖漏封装。

## 决策

| ID | 问题 | 结论 | 状态 |
|---|---|---|---|
| D1 | 本轮是否包括真实 Scene 重构及 Three 效果？ | 不包括；M2-M3 由 Windows 后续任务承担。 | 用户指定 |
| D2 | 是否需要新建工具系统/资产权威库？ | 复用现有 CLI/session/store，未配置生产资产根时只建 Review。 | 按本机核对 |
| D3 | 是否切稳定入口、公开发版？ | 仅 candidate 安装，新固定 Review 会话，不 commit/tag/push 或切 current。 | v3.1 M1 范围 |
| D4 | 最小新合同？ | module/media，真实入口与闭合文件；template/recipe/Blender 后续。 | v3.1 允许子集 |
| D5 | 未指定真实 Work 怎么办？ | 不修改生产、不复制整库；使用脱敏技术夹具并明确业务对照待 Windows 选择。 | 缺口有明确去向 |
| D6 | Review WorkRoot 是否另迁路径？ | 保留既有 production/review/id 合同，仅新增独立 AssetReviewRoot。 | 复用本机合同 |
| D7 | 用户拒绝候选程序与多入口，要求部署到 D 盘根目录 | 取代 D3 的本机入口决策：使用受控 local 构建，直接部署到 WorkRoot/.harness，由根 work.cmd 连接正式 Work；内部校验保留，不再要求手动 session/Review。旧部署不删除。 | 用户后续明确指定 |
| D8 | 用户要求直接在 Codex App 新对话工作，不接受 session 前提 | 根入口完全去除 Harness session 创建和依赖，直接读取本机配置；无参数双击显示用途和说明，不再报错后闪退。Codex 对话不是 Harness session。 | 用户后续明确指定 |

验收覆盖目标/范围、输入真源、权限边界、失败不覆盖、最小复杂度、未登记来源、环境继承及业务验证缺口。执行与私有路径证据保存在 Git 忽略的 `tasks/component-authoring-m0-m1/`，不把生产内容带入公开 PRD。
