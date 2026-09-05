# Windows 创作工作台与 WSL 交接

日期：2026-09-05

本文件收敛用户提供的《HyperFrames AI：Windows 创作工作台、WSL 开发与候选回测补充 PRD》v1.0 的实施边界。它补充 [可执行 Visual Plan PRD](./hyperframes-visual-plan-motion-reuse.md)，不重做已有播放、seek、Plan/Draft 分离、来源与依赖快照、局部差异、Range 或混合渲染。本文是目标与验收合同，不是 Windows 实机通过报告。

## 职责

- Windows：正式 Work 生命周期、文案、Research、Plan、Slots、布局、时间、跨 Scene 编排、需求讨论及作品验收。
- WSL：唯一 Git 开发仓、Harness、组件内部、新 shader、通用效果主体的开发与打包。只在冻结请求的私有复现副本中调试，不双写生产 Work。
- Work-local 不是绕过开发边界的名称。新效果可交付为单个 Work 的补丁，不强制公共化；真实复用与用户认可后才考虑入库。
- 不建设第二份源码仓、常驻调度服务、在线 Registry、新剪辑器或多轮审批链。

## 目录与会话

Windows 日常打开 `%LOCALAPPDATA%\HyperFramesAI\workspace`。它是薄入口，不是开发仓。不可变稳定包放 `releases/`，候选包放 `candidates/`，保留 `current` / `previous` 稳定安装兼容入口。本机配置、会话状态与缓存外置，不写已校验安装文件。

正式 WorkStore 保留 `works/` 和 `.runtime/`；私有请求放 `requests/`，候选副本放 `review/`。Work、媒体、请求和真实测试输入不得进入 Git。WSL 与 Windows 不共享 node_modules、venv 或浏览器缓存。

一次会话绑定实际版本，不在每条命令重新追踪 current。切换稳定版或候选后开新会话；旧会话保持原版本或明确结束，不能热混用 Skills、HF、GSAP、Three 与播放器。

## 原生执行与候选

Windows 原生 Work CLI、Visual Plan 和渲染依赖须闭合：固定 CPython、Node、HF、GSAP、Three、渲染浏览器、FFmpeg/ffprobe 与所需字体；由安装管理，普通渲染不运行浮动 npx/npm install。入口自动解析受控 HF 路径，不要求用户填写开发 dist。

已有 ASR/下载 Provider 沿用其受控入口；WSL Provider 不把整个创作流程变成 WSL 开发，也不成为所有用户的隐含依赖。缺 ASR 不阻塞已有音频的预览。权限受限时指出实际缺口，不关闭沙箱或授权任意 shell。

候选构建冻结当前受控源码，包括相关未提交修改和明确选中的新增文件；排除私有数据、凭据、缓存和任意未跟踪文件。记录 base commit、dirty、实际源码与依赖哈希。候选不要求 commit/tag/push，不覆盖 stable current，不原地修改既有候选。

正式 `release build` 保留干净工作树、tag 与 upstream 约束；Git 操作、安装切换和公开发布仍各自遵守明确授权。候选验收不等于正式发行或组件批准。

## 请求往返

请求使用稳定 request ID/revision、Work/Variant、Scene、预演/源码快照、实际文字或唯一 Binding、画幅、阅读窗口、媒体、相邻交接、目标与保留项、当前缺口和验收输入。已能从 Work 获取的内容不重复询问。

Windows 拥有需求、反馈、验收；WSL 读取冻结 revision，拥有交付清单和技术结果，不共同编辑同一状态文件。更新请求保留旧 revision；缺上下文只返回该请求的聚焦问题。不增加默认需求批准门，继续制作不受影响 Scene。

未批准组件只在隔离 Review 副本预演，不通过普通 install 的 force 后门。Review 标明候选和请求 revision，隔离生产 Current/接受状态；禁止正式 Finalize、归档完成和平台草稿，可生成测试视频。

验收准确实现、依赖和实际输入后，公共组件按现有准入精确安装到目标 Work，其余 Work 不升级。Work-local 补丁应用前核对源快照，基础变化只比较受影响 Scene，不覆盖整片。仅元数据变更不重复验收效果；执行代码、资源、依赖或视觉默认值变化须验证受影响部分。组件、Plan、Draft 分开记录，但一句明确回复可同时涵盖。

## 验收与未验证项

1. 候选准确包含本轮修改，不泄露私有输入；安装失败不改稳定入口。
2. Windows 固定入口原生完成隔离 Work、Plan 和测试渲染，不依赖 WSL 活跃目录或全局依赖。
3. 长 Work 的副本、真实文字、Scene 定位、随机 seek、长音频 Range、GSAP/Three 生命周期保持正确，原件不变。
4. 请求经真实内容、WSL 实现、Windows Review、反馈、明确验收及精确接纳完成往返。
5. 候选/稳定版并存且会话不混版，未批准候选不能正式安装或 Finalize。
6. 安装、升级失败恢复、回滚和数据兼容性在目标环境验证，旧 Snapshot/Final/请求不删除。
7. 正式音频重定时只改必要时间和交接，不删字、不重写已确认视觉。
8. 中文/空格路径、端口冲突和实际 Windows Agent 沙箱权限通过；不以放宽整盘权限验收。

实现、Linux/mock 检查、Windows 原生实机、交互 WebGL、抓帧 WebGL、硬件编码和真实生产复用分别报告。软件渲染不冒充 GPU，Windows 浏览器打开 WSL 页面不冒充原生闭环，技术夹具不证明返工下降。
