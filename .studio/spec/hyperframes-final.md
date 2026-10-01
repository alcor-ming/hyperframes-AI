## Final QA

生产 `finalize` 不带文件参数时编排接受源渲染、ffprobe 与全量解码 QA，保留失败恢复 journal；该机器检查不替代实际声音/视觉和首次跨引擎一致性证据。记录实际 render/probe/decode 调用次数、耗时与返回码；工具内部重试、缓存命中、tokens 和成本未知时保留 null，不推算成功率或节省。

成功后仅清理本次冗余 candidate，清理失败登记并保留文件；下次持锁 Finalize 只有在当前 Final、manifest、candidate、QA 的 hash 与引用证明仍有效时才重试清理。其他未登记 browser/build 缓存保留，不推定已自动安全回收。

仅在生产 Variant 的 Finalize 交付链，从准确 Accepted Draft 的闭合快照正式渲染并保留收据，不从变化的可编辑工程冒充接受版本。以下是既有底层正式渲染入口，不是 Draft/test-work 的导出许可：

```bash
./work --work <id> --variant <id> preview render <draft-id> --output <final.mp4> --final
```

新编码文件检查流、规格（60fps high）、原音时长、全量解码、代表帧及必要音频核验；实际缺陷修复后重渲染。Final Error 阻止 `./work finalize ... --qa-passed`，通过后只完成目标 Variant 的 Finalize；软归档是独立标记，不自动归档、不搬目录。

QA 按影响范围：已接受且未变仅检查来源/证据适用性；局部变化只查受影响 Scene、状态和交接；共享布局/时间线/宿主变化按依赖扩展。编码 QA 不重审已接受观点/设计，仅 Finalize/归档核对来源、收据、文件、目标及归档结果，不重复审片/渲染。只报告结果与真实未验证项。
