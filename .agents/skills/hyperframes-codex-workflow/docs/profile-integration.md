# Stable Profile Integration

## 单一来源

三套 Profile 已稳定，本工作流不复制它们的完整规则。`profile-registry.json` 只保存真实文件路径、显示名称和 motion primitives。

Codex应读取对应 Profile 的：

- 完整设计说明；
- 色彩与字体 Token；
- 运动语法；
- 禁止项；
- 横竖屏适配规则。

选定后生成或引用项目级 `DESIGN.md`，所有 composition 必须追溯到该 Profile。

## 三个 Profile ID

### `optical_fluidity`

Motion primitives：

```text
Focus → Align → Connect → Resolve → Refract
```

适合空间关系、技术解释、流程和数据连接。

### `kami_editorial`

Motion primitives：

```text
Reveal → Annotate → Underline → Turn → Settle
```

适合观点、文章式叙事、引用、章节和人文解释。

### `monochrome_atelier`

Motion primitives：

```text
Isolate → Unveil → Cut → Condense → Lock
```

适合品牌宣言、单一重点、强排版和低密度视觉叙事。

## 分工边界

```text
Template 决定：谁是画面主体、能占多少画面、时间轴来自哪里。
Scene 决定：本段表达什么。
Profile 决定：颜色、字体、材质、构图倾向和运动方式。
```

Profile 不决定是否使用图片、是否配音或是否生成字幕。

## 禁止行为

- 同一视频混用多个 Profile；
- 仅换颜色而复用完全相同的构图与动画；
- 临时新增不在 Profile Token 中的品牌色；
- 因模板限制而修改稳定 Profile 的核心语言；
- 把 Profile 复制进每个项目形成不可维护的分叉。
