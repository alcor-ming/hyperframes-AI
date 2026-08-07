# Optional Image Asset Workflow

## 定位

图片生成是可选能力。只有图片能显著降低理解成本、建立场景或提供无法用 HTML/SVG 高效表达的视觉证据时，才进入 Animation Plan。

## 计划阶段

在 `Optional Asset Brief` 中写：

- `Asset ID`；
- 对应 Scene；
- 叙事用途；
- 主体与负空间；
- 比例；
- 来源：`generated | provided | existing`；
- 禁止内容。

计划阶段不必输出冗长的最终生图 prompt，也不批量生成图片。

## 批准后

对 `source: generated` 的资产：

1. 读取所选 Profile；
2. 将 Brief 扩写为 image-gen 提示；
3. 生成到 `assets/generated/IMG-xxx.*`；
4. 检查主体位置、负空间、裁切和风格；
5. 不合格时直接重生成；
6. 更新 `assets/manifest.json`。

图片重生成不需要重新批准，除非改变它在 Scene 中的叙事作用或 Hero State。

## 应由 image-gen 生成

- 概念插画；
- 抽象隐喻；
- 氛围背景；
- 编辑式照片；
- 不存在的未来场景；
- 章节 Hero Image；
- 需要特定主体位置和大块负空间的图片。

## 应由 HyperFrames / SVG 实现

- 中英文文字；
- 字幕；
- 数字；
- 数据图；
- 流程图；
- 节点与路径；
- 图标；
- Logo；
- 软件 UI；
- 与时间轴同步变化的图形。

## 基本限制

- 不要求生图模型渲染可读中文。
- 不把 Logo、数字、图表或 UI 烧进图片。
- 真实证据、产品截图和品牌资产优先使用原始素材。
- 为横竖屏分别明确裁切策略，不能简单拉伸。

## 最小 Manifest

```json
{
  "id": "IMG-001",
  "scene": "S03",
  "source": "generated",
  "brief": "assets/briefs/IMG-001.md",
  "file": "assets/generated/IMG-001.png",
  "status": "accepted"
}
```
