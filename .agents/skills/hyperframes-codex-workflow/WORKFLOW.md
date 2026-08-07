# End-to-End Workflow

## 0. 输入与项目探测

Codex先读取已有项目、素材和稳定 Profile，不重复创建已有结构。

识别：

- 是否存在原始人物口播视频；
- 是否已有最终音频；
- 内容来源是文稿、资料、大纲、转录还是 `section_map.json`；
- 目标比例与分辨率；
- 用户已指定或默认使用的 Profile；
- 是否可能需要 AI 配音或图片资产。

## 1. 选择模板

```text
存在必须保留为主体的原始人物口播视频
    → talking_head
否则
    → pure_hyperframes
```

只有音频、没有人物视频时，仍属于 `pure_hyperframes`。

## 2. 建立内容模型

Codex从可用来源中提取叙事结构：

```text
视频/音频转录、文稿、资料、大纲、已有 section_map
    ↓
核心论点、证据、步骤、转折、结论
    ↓
Scene 草案
```

`section_map.json` 存在时可直接利用；不存在时不阻塞。为后续复用生成它也是可选行为。

## 3. 生成第一版 Animation Plan

Codex直接生成可讨论草案，不先要求用户补齐所有细节。

计划只包含：

- Plan Header；
- 简短目标；
- Scene Table；
- Optional Asset Brief；
- 最多 3 个重要待决策项。

每个 Scene 必须回答：

1. 观众需要理解或记住什么；
2. 动画完成后的 Hero State 是什么；
3. 使用所选 Profile 的哪些运动词汇；
4. 是否需要图片或其他资产。

## 4. 类 PRD 讨论循环

用户可调整：

- Scene 顺序；
- 信息目标；
- Hero State；
- 动画强度；
- 图片构图；
- 旁白策略；
- 章节节奏；
- 全屏插入是否必要。

Codex原地修改 `ANIMATION_PLAN.md`。每轮回复只展示变更摘要、变更后的相关 Scene 和仍未解决的决策，不重复整份规范。

讨论持续到用户明确批准。

## 5. 批准后锁定视觉结构

批准后锁定：

- Scene 数量、顺序；
- 每个 Scene 的信息目标；
- Hero State；
- Template 与 Profile；
- 主要资产角色；
- 旁白内容结构。

实现参数仍可调整。

## 6. 可选资产阶段

### 图片

只生成计划中存在 Asset Brief 的图片。生成图片时使用选定 Profile 的视觉语言，但不把文字、Logo、UI、流程图或精确数据烧入位图。

### 配音

`talking_head` 通常直接使用原音轨或指定替换音轨。

`pure_hyperframes`：

- `provided`：直接锁定已有音频；
- `record_later`：输出批准后的最终旁白稿，接收录音后锁定时间；
- `ai_generated`：计划批准后生成音频；
- `none`：制作无旁白视觉视频。

配音完成后按真实音频长度更新 Scene 时间码。只要不改变场景语义和顺序，不需要再次批准。

## 7. HyperFrames 实现

对每个 Scene：

1. 先建立完整静态 Hero State；
2. 检查比例、换行、人物/字幕安全区和资产裁切；
3. 再使用 Profile 的运动词汇添加 GSAP 动画；
4. 多场景使用明确转场；
5. 用 Scene ID 关联计划与实现。

## 8. 静默 QA

依次执行：

```bash
npx hyperframes lint
npx hyperframes validate
npx hyperframes inspect --json
```

新建或大幅修改动画时再生成 animation map。先渲染 draft 检查，最终使用 60fps high quality。

自动修复可修复问题。用户可见回复不列举全部通过项。

## 9. 交付

交付内容：

- 项目预览入口；
- 最终视频；
- 使用的模板与 Profile；
- 相比批准计划发生的实质调整；
- 尚未解决的问题，仅在存在时报告。
