# Blender 资产候选：T1 设备样机

当前交付仅包含 **T1 手机与笔记本**。按用户 2026-10-02 最新要求，先推送独立分支供验收，**T2 / T3 / T4 未开始，收到用户验收通知后才能继续**。

## 结果与门槛

| 项目 | 手机 | 笔记本 |
|---|---:|---:|
| 三角面 | 3,202 / 30,000 | 16,606 / 50,000 |
| GLB 字节 | 62,572 / 2,000,000 | 261,856 / 3,000,000 |
| 两次独立构建 | 字节一致 | 字节一致 |
| 源网格零面积面 / 重复顶点 | 0 / 0 | 0 / 0 |
| 刚体零件流形与正体积 | 通过 | 通过 |
| 屏幕 UV 0..1 / r160 数值方向检查 | 通过 | 通过 |
| Khronos glTF Validator | 0 errors / 0 warnings | 0 errors / 0 warnings |
| 开合采样检查 | 不适用 | 0–130°，每 1°，131 档无三角面相交 |

真实 Three.js r160 `GLTFLoader` 已在 Node 环境成功解析两个最终 GLB，并通过节点、UV 数值方向、尺寸、角色、三角面与铰链检查；这不替代浏览器显示检查。完整数据见 `T1-device-mockups/out/metrics.json`、`geometry-check.json` 与 `reproducibility.json`。两张屏幕有意为独立单面显示面，因此有边界；其他零件为闭合实体。整机是装配件，不是把所有零件布尔并集成一个实体。

**严格 T1 门槛尚未宣布通过。** CPU PNG 和脚本几何检查已完成；实际 Three.js 浏览器截图、贴图四角的可视确认、拖动开合与浏览器像素回跳仍需执行。环境中的 Chromium 启动报 `socket() Operation not permitted`，提供的云浏览器访问本地 fixture 地址报 `net::ERR_BLOCKED_BY_CLIENT`。没有以 CPU 渲染冒充样例页截图，也没有以静态矩阵测试冒充动画像素验收。

## 固定环境

- Blender **4.5.14 LTS**，官方 Linux x64 可移植版，无第三方 Blender 扩展
- 官方包：https://download.blender.org/release/Blender4.5/blender-4.5.14-linux-x64.tar.xz
- 官方校验表：https://download.blender.org/release/Blender4.5/blender-4.5.14.sha256
- 包 SHA-256：`9ba871ff2ecd36526b77432745980b7e6664ecd0c7ca11c48849073dcfe06da3`
- 已实际以 `--background --factory-startup` 构建并用 Cycles CPU / 24 samples 输出 PNG；禁用降噪，色彩管理 Standard
- Three.js 固定 **0.160.0 (r160)**；Khronos `gltf-validator` 固定 **2.0.0-dev.3.10**；依赖锁见 `fixture/package-lock.json`
- 不使用 Draco、meshopt、KTX2 或 transmission；T1 GLB 不内嵌第三方贴图

Linux 安装（不改系统配置）：

```sh
bash blender-assets/common/install_blender.sh "$HOME/.cache/hf-blender"
export BLENDER="$HOME/.cache/hf-blender/blender-4.5.14-linux-x64/blender"
```

其他操作系统请使用相同 4.5.14 LTS 官方构建；本次字节级可复现结果仅证实上述 Linux 构建，同参数跨 OS / CPU 未验证。

## 构建与验证

在仓库根运行：

```sh
"$BLENDER" --background --factory-startup \
  --python blender-assets/T1-device-mockups/build.py -- \
  --params blender-assets/T1-device-mockups/params.json \
  --out blender-assets/T1-device-mockups/out/

"$BLENDER" --background --factory-startup \
  --python blender-assets/T1-device-mockups/check_geometry.py --

"$BLENDER" --background --factory-startup \
  --python blender-assets/T1-device-mockups/build.py -- \
  --params blender-assets/T1-device-mockups/params.json \
  --out blender-assets/.repeat/T1 --no-previews

python3 blender-assets/common/check_reproducibility.py \
  blender-assets/T1-device-mockups/out blender-assets/.repeat/T1 \
  --report blender-assets/T1-device-mockups/out/reproducibility.json

# 可选：合并四视图；需 Pillow，字体用本机 DejaVu Sans（未提交字体文件）
python3 blender-assets/common/make_contact_sheet.py \
  --previews blender-assets/T1-device-mockups/previews

cd blender-assets/fixture
npm ci
npm test
npm run validate -- ../T1-device-mockups/out --out ../T1-device-mockups/validator
npm run check:t1
npm run serve
# 另开终端（fixture 目录），实际 Chromium 验证和截图
npm run check:browser
```

样例页默认地址与参数详见 `fixture/README.md`。没有制作或导出视频。日志位于 `T1-device-mockups/logs/`。

## 模型约定

- 坐标单位为米，glTF `+Y` 朝上、`+Z` 朝前。所有静态网格缩放为 1、旋转为 0，几何写入网格坐标
- 手机原点位于机身几何中心，机身 0.074 × 0.16 × 0.0082 m；前置摄像头为居中圆形挖孔，无品牌标志或品牌式开口
- 手机独立 `screen` 网格：9:19.5，`extras.screen_aspect = 0.4615384615`
- 笔记本底座后沿中点为原点，屏幕对角线 0.36 m、16:10
- `lid` 节点原点即铰链轴，局部 X 为开合轴。闭合为 `lid.rotation.x = 0`，最大打开为 `-2.2689280275926285` 弧度（130°），默认 `-1.8325957145940461`（105°）
- `lid.extras.lid_angle_range = [0, -2.2689280275926285]`，范围按“闭合、最大打开”顺序存储，不能假定数值升序
- 笔记本屏幕是 `lid` 的独立子网格 `screen`，`screen_aspect = 1.6`
- UV 从正面观看不镜像，物理顶边对应导出 glTF V=0；最终显示方向仍待真实浏览器可视验收
- 材质名与 `material.extras.role` 相同，T1 使用 `hf_surface` / `hf_muted` / `hf_screen`。材质均为 glTF metallic-roughness；默认浅灰哑光
- 几何开合测试使用所有盖部网格对所有固定网格（包括铰链）的 BVH 三角相交检测；这是 1° 离散采样，不是连续碰撞数学证明。屏幕和边框贴合通过构造保证，实拍漏光检查待用户浏览器验收

## 预览与自评

`T1-device-mockups/previews/T1-device-four-views.png` 为实际 CPU 渲染的八张图拼图：每个设备正面、3/4、背面、俯视。透明单张在 `previews/phone/` 与 `previews/laptop/`。这些用于检查形体与比例；不是样例页截图。

自评：可复现、面数/大小、源网格检查已通过；低采样 PNG 能看清设备及主要细节。形体判断属于人工看图检查。浏览器可用性、屏幕测试图方向与主题视觉效果尚未验证，不能称 T1 全面合格。

## 来源与许可

设备建模脚本、网格和渲染为本任务原创；无品牌 Logo、无第三方模型、无 HDRI、无纹理素材。代码和原创产物保持仓库已有许可范围，不擅自为仓库增加新的开源许可。

运行时依赖：Blender（GPL-3.0-or-later），Three.js（MIT），Khronos glTF Validator（Apache-2.0），Playwright（Apache-2.0），pngjs（MIT）。这些通过安装脚本 / npm 获取，未提交二进制或 `node_modules`。拼图标签使用本机 DejaVu Sans 字体（DejaVu Fonts / Bitstream Vera 字体许可），未提交字体；中文测试图使用浏览器本机中文字体，检查截图时须确保可显示中文。

当前资产仅是候选。没有导入或改动生产 Work / AssetStore / Current / 接受状态，没有 merge、部署、视频导出或按 hash 接纳。
