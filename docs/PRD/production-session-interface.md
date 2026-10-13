# 生产会话接口

本合同取代历史客户端专用入口和模型分工。执行客户端负责会话、模型选择和结果链接；HyperFrames 拥有 Work/Variant、Studio、接受记录、快照与 Finalize。文案、TTS 操作与设计身份不绑定执行模型；TTS 声音服务的声学模型配置仍属于合成接口。

## 工作目录与发现

生产会话的 cwd/workspace 固定为已授权的安装根，先读取根 `AGENTS.md`，再加载 `.agents/skills/hyperframes-production-workflow/SKILL.md`。此共享目录须被会话的 Skill 发现器启用；不能发现时显式读取同一文件，不建立旧名别名或复制另一份规则。开发会话无论运行在哪里都只使用隔离夹具；WSL 生产会话可以操作授权根的指定 Work。

原生入口为根 `work.cmd`；WSL 使用同一物理根的 `./work-wsl.sh`（调用 `.studio/work_wsl.py`，后端仍是该根 Windows 运行时）。先运行 `doctor`，检查 `runtime`、`work_root`、`release`、`release_manifest_sha256` 和 `invocation`；后者为 `wsl-forwarded` 或 `windows-native`，仅标识调用路径，不授予权限。GPU 字段仍需原生渲染验证。

## 命令、输出与证据

以下 `work` 表示所选根入口，不是 PATH 中的其他安装。先 `work current`，未设置时 `work list --json`；依据用户意图选择已有 Work。后续命令显式绑定 `--work <id> --variant <id>`，不要从多个 Variant 猜测 `main`。例如：

```text
work --work <id> --variant <id> status --json
work --work <id> --variant <id> workflow show --json
work --work <id> --variant <id> preview open current --no-open --json
work --work <id> --variant <id> preview diagnose --json
work --work <id> --variant <id> critic round --json
```

参数以该根 `--help` 为准。WSL 入口原样传递退出码和输出；支持 JSON 的命令使用 `--json`，不要把退出码为非零、stderr 提示或缺失回执解析成成功。`preview register` 返回 Draft ID；保存该 ID，再查看其状态，不要假定所有命令 stdout 都是 JSON。文件参数须在授权根内，路径转换拒绝越界和 symlink；资产 ID（如 `design new --from`）不是文件路径。

Studio 打开结果提供项目、目标、URL 和来源摘要；诊断与 critic 包提供诊断 JSON、边界/seek 采样与 PNG 文件路径。执行者不具备看图能力时可检查文件、摘要、诊断及采样错误，但不能据此宣称视觉通过。`critic round` 的 `visual_review: unverified` 和 `human_checks` 明示仍需图像评审、观看运动及听校。`critic.provider=external` 只生成外部只读评审请求，不调用模型；`critic.model` 可为空，仅作来源标签。实际评审后才用 `critic record` 登记准确轮次和快照的意见；意见不代替用户接受。硬件编码、WebGL 与真实音画结论按实际证据记录。

## 断线、重试和互斥

恢复时重新核对 doctor 的根与发行身份，读取 `current`/`list`，按保存的 Work/Variant ID 运行 `status --json`，再读取该对象的工作流、预览及交付回执。磁盘状态是事实来源，聊天中的“完成”不是。保留冻结 Lock、接受快照和资产绑定，不自行编辑生命周期文件或切换为最新设计快照。

会话应在第一次创建成功后保存返回的 Work ID；响应丢失时先列出现有 Work、核对内容目标和状态。存在明确匹配时继续它，无法唯一匹配时请求选择，不能盲目重放 `new`。`new` 不是带请求幂等键的接口。同一准确对象保持单一执行者，恢复前确认前一操作不再运行。

Finalize 超时或断线后先回读交付状态、Final 回执与导出摘要；已经成功则返回原交付链接。只有确认仍未完成且原操作已结束，才对原 Work/Variant 重试；已有晋升 Final 的恢复路径复用原产物，不重复渲染。不要因为客户端未收到回复而新建 Work、换 Variant 或并行再次 Finalize。接受、归档与发布仍按各自授权执行。

执行客户端的 workspace/provider 配置、旧 Work 盘点和实际生产验收由入口侧负责，本接口实现不代表已部署。
