# Task：由 Work CLI 独占新建目录编号

状态：已实现，待用户验收

## 原始请求

> 新建文件夹命名应该为工具创建不能让LLM控制，创建task修复这个流程异常问题

## 目标

让 `./work new` 在创建 Work 时原子分配并固化数字编号；LLM、来源标题和后续语义命名都不得参与 Work ID 或目录名生成。

## 范围

- 修改 Work CLI 的新建流程：数字编号、Work ID 和目录名由 CLI 独立生成。
- 编号在创建目录前完成，并在同一锁内检查冲突，保证并发创建不会重复。
- `WORK.md.id` 必须与目录名保持一致；创建后仍不可改名。
- `./work name` 只补充显示标题中的语义部分，并复用创建时的数字编号，不再承担首次编号职责。
- `podcast_quote_image` 创建后立即拥有编号；转录完成后只补充“嘉宾名-核心主题”。
- 更新与旧规则冲突的工作流文档和测试。

## 验收标准

1. 连续新建两个 `podcast_quote_image` Work 时，CLI 自动生成两个递增且唯一的数字目录名，传入标题不影响目录名。
2. 相同输入标题、不同输入标题及并发创建都不会产生重复 Work ID。
3. 新 Work 的目录名、`WORK.md.id` 和 CLI 返回的 Work ID 完全一致。
4. 新 Work 在转录前已经有稳定编号；执行 `./work name` 后编号保持不变，只更新显示标题。
5. LLM 无法通过 `work new` 的标题参数指定、覆盖或推导目录 slug。
6. `./work list`、`use`、`park`、`reopen`、`archive` 与显式 `--work` 仍能处理新编号；旧格式 Work 继续可读。
7. 不自动迁移、重命名或删除现有 WorkStore 中的任何目录。

## 不在范围

- 不修复或批量重命名当前 4 个未编号的 active XHS Work。
- 不改变 Variant ID、发布权限、媒体获取、转录或文章生成逻辑。
- 不引入新的数据库、服务或第三方依赖。

## 最小验证闭环

实现前先在 `tests/test_work_cli.py` 增加失败用例：分别用两个不同标题执行 `work new --workflow podcast_quote_image`，断言目录编号由 CLI 递增生成且不包含任一标题 slug；实现后运行：

```bash
python3 -m unittest tests.test_work_cli -q
```

## 技术备注

- 修复前的异常入口位于 `.studio/work.py::command_new`：目录 ID 由 `slugify(args.title)` 生成。
- 修复前 `.studio/work.py::command_name` 到转录后才分配三位显示编号，职责发生得过晚。
- 编号分配应复用 WorkStore `.runtime/naming.lock`，不新增锁或依赖。
- 实现格式为 `work-<workflow>-<三位序号>`；编号按 Workflow 递增，Workflow 名隔离目录命名空间。

## 下一步

全仓 `34` 个单元测试已通过。仓库当前未安装 `.trellis/scripts/task.py`，因此本文件继续作为任务事实源；用户验收后即可关闭。
