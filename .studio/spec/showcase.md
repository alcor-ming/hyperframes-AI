# Showcase

仅 Opus 5.5 制作，Codex 不接制作。创建时显式选择并冻结 `pdoom` 或 `science`，只决定加载 [pdoom](showcase-pdoom.md) / [science](showcase-science.md) 哪份参考，不改变硬约束。16:9 为主、9:16 为辅，不使用 4:3。创建只需 `--mode showcase --submodule pdoom|science`：Theme、Background、Motion 均不强制绑定，也不继承账号外观；未显式选择的项在外观锁中记为 `null`，画面由作者在工程内自由决定。确需复用已接纳资产时再用 `--theme` / `--background` / `--appearance-file` 显式选择或 `appearance rebind` 追加。

采用 `SHOWCASE_PLAN.template.md`：概念、子模块、逐 Scene 要点、素材与声音、未验证项、作者模型审计元信息。Scene ID 与 CLI 元信息沿用现有合同。

不适用 explainer 正向方向和专项 Plan 字段、D14 主载体要求、Q1 活力自检、卡片形式规则以及 Draft 前节奏诊断必经闭环。五层、字幕、声音层只是可选参考；诊断可运行、只报告，不强制处理节奏疑点。用户对准确 Plan/Draft 的确认和接受仍按工作流执行。

硬约束不变：事实与来源可追溯，不伪造界面与数据；单一 paused timeline、seek 安全，不依赖 `onUpdate` 写状态；依赖与媒体离线闭包，不用 CDN、不引用闭包外资产。授权与 Asset Brief 见根规则；Draft/test-work 不导出视频，仅生产 Variant 的 Finalize 渲染 MP4。继续使用已部署官方 Studio，不新建渲染器。

接受后按 `VISUAL_RETRO.template.md` 分类提炼为积木、动作配方或规则、内容资产、仅属于本片。交付其他产品线的是最小模块、接口卡、配方或 Plan 数据块，不是整页源码；冻结资产仍走现有 pack / validate / accept。
