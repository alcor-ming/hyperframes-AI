# 隐私与效果边界

- 外部 WorkStore 的 `works/` 与 `.runtime/`、旧 `tasks/`、媒体、HTML 工程、Draft、Final 和 QA 输出不得进入公开 Git。
- 下载用于转录的源视频保留在仓库外；用户导入或生成的作品媒体进入对应 Variant 的 `media/`。
- Harness 不读取或输出凭据，不公开发布内容，不购买额度。经用户对准确 Work/Variant 明确授权，可使用其已登录的 Windows Chrome 保存小红书创作者平台草稿；不得读取 Cookie、调用未公开接口或点击发布。
- 外部或付费服务必须单独取得用户授权；本地 CLI 不发起网络请求。
- Final 只表示本地交付完成，不表示已保存到平台草稿箱或已发布。
