# 隐私与效果边界

- 外部 WorkStore 的 `works/` 与 `.runtime/`、旧 `tasks/`、媒体、HTML 工程、Draft、Final 和 QA 输出不得进入公开 Git。
- 用户导入或生成的作品媒体进入对应 Variant 的 `media/`，外部源媒体保留在仓库外。
- Harness 不读取或输出凭据；授权与外部服务边界只见根 [AGENTS.md](../../AGENTS.md)。本地 CLI 不发起网络请求。
- 视频 Finalize 渲染出最终 MP4，只表示本地交付完成，不表示已发布。
