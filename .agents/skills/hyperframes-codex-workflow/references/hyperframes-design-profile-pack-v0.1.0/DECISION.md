# 决策：自有 Profile，还是直接使用第三方 Skill？

## 结论

采用**混合架构**，但运行时以**自有 Profile Skill**为主：

```text
上游开源 Skill
  └─ 提供设计知识、反模式和维护基线
       ↓ 适配与固化
自有 HyperFrames Profile Skill
  └─ 成为视频执行时唯一视觉真源
       ↓
HyperFrames 两种模板
  ├─ 口播增强
  └─ 纯 HyperFrames 展示
```

不是三选一，也不是把三个第三方 Skill 直接串联调用。

## 为什么自有 Profile 必须保留

### 1. Profile 是“身份”，Skill 通常是“能力”

Profile 回答：

- 画面属于什么视觉世界；
- 色彩、字体、材质和构图如何保持连续；
- 哪些动效属于这个世界；
- 哪些元素绝对不能出现。

通用设计 Skill 回答：

- 如何审查设计；
- 如何修复排版、布局、动效或性能；
- 如何根据当前任务选择设计手段。

如果只装通用 Skill，每次任务都有可能重新解释风格，导致同一个 Profile 随模型、版本和上下文漂移。

### 2. 上游 Skill 的输出介质不同

| 上游 | 原始介质 | 直接用于 HyperFrames 的主要错位 |
|---|---|---|
| Emil Apple Design | 交互 UI | 大量规则依赖手势、指针、可中断交互和高频操作 |
| Kami | PDF、文档、网页、幻灯片 | 带文档模板、构建脚本、页面密度和字体安装逻辑 |
| Impeccable | 前端产品与品牌界面 | 会执行完整设计诊断，并可能重新定义视觉世界 |

视频需要的是固定时间轴、音频语义节点、镜头连续性、帧级同步和渲染性能。因此必须经过媒介转换。

### 3. 三套风格需要互斥

第三方 Skill 同时加载时容易产生冲突：

- Apple 式玻璃与 Kami 的实体纸面冲突；
- Kami 的暖色与 Monochrome 的中性暗场冲突；
- Impeccable 的 `colorize` 或 `bolder` 可能破坏 Profile 3 的克制；
- 通用 anti-slop 规则可能误杀用户明确要求的品牌特征。

自有 Skill 可以强制“一次只选一个 Profile”。

## 推荐的实际分工

### 日常视频执行

只使用：

```text
hyperframes-design-profiles
+ HyperFrames 自身 skill
```

不要直接调用 Kami、Impeccable 或 Apple Design。

### Profile 维护与升级

在以下场景临时读取上游 Skill：

- 上游发布重大版本；
- 某个 Profile 频繁出现同类缺陷；
- 需要增加新的字体、排版、动效或反模式规则；
- 对 Profile 做季度审计。

读取后，将确认有效的规则翻译进本包，再更新版本。不要让上游内容在生产任务中动态漂移。

### 单次专业审查

可选使用：

- Profile 1：用 `review-animations` 或 `fixing-motion-performance` 审查动效代码；
- Profile 2：用 Kami 的设计规范核对纸面排版，但不运行其文档生成流程；
- Profile 3：用 Impeccable 的 `distill / quieter / typeset / layout` 做四阶段审查。

审查器只能提出问题，不能自行改换视觉身份。

## 是否需要把本包做成一个正式 Skill？

需要。

建议名称：

```text
hyperframes-design-profiles
```

它应当是薄路由层，而不是把所有上游内容复制进一个超大 prompt。执行流程：

1. 判断视频模式；
2. 锁定一个 Profile；
3. 读取对应 `PROFILE.md` 和 `tokens.json`；
4. 生成 Animation Plan；
5. 等待用户二次确认；
6. 实现和渲染；
7. 按 `shared/review-gate.md` 验证。

## 最终判断

| 方案 | 评价 |
|---|---|
| 只用自有 Profile 文本，不做 Skill | 可用，但容易被遗漏，缺少路由和确认门 |
| 直接调用三个第三方 Skill | 不建议；介质错位、上下文重、风格容易冲突 |
| 自有 Profile Skill，引用上游思想 | **推荐**；身份稳定、可版本化、可审计、适合两种模板 |
| 自有 Profile Skill + 可选上游 QA | **最佳实践**；生产稳定，同时保留社区更新能力 |
