# 冷静的光 · graph-grow / token-stream v2

本次根据审阅文本采用方向 A：固定正交的 2.5D 说明图。graph 重做标签布局与有方向的路径；token 重做平面容量网格和真实 FIFO。仍是两个通用模块，没有完整视频。提交沿用 feat/calm-light-threejs-modules，manifest 升为 v2，避免覆盖已 pack 的 v1 身份。

## 本地查看

在独立仓库检出目录更新原分支，不在生产工具目录修改源码：

```sh
git fetch origin
git switch feat/calm-light-threejs-modules
git pull --ff-only
node --test handoff/calm-light/*test.mjs
python handoff/calm-light/setup-fixtures.py --font /absolute/path/to/chinese-font.otf --font-license /absolute/path/to/font-license.txt
python -m http.server 8090 --directory handoff/calm-light
```

PowerShell 可用显式测试文件，避免通配符行为差异：

```powershell
node --test handoff/calm-light/state.test.mjs handoff/calm-light/graph-layout.test.mjs handoff/calm-light/token-state.test.mjs
```

打开：
- http://localhost:8090/graph-grow/fixture/index.html
- http://localhost:8090/token-stream/fixture/index.html

手动预览不需要 npm install。字体必须合法且包含中文，即使槽内写英文，token 的状态说明仍使用中文。setup 只建立被 git 忽略的隔离 fixture 字体与冻结 runtime 输入，不 pack、不 accept、不读取生产库。

## 自动像素与审阅截图

需要 Playwright 和 Chromium。可用现有安装，或在 handoff/calm-light 目录安装独立测试依赖：

```sh
npm install --no-save --no-package-lock playwright@1.62.1
npx playwright install chromium
node graph-grow/fixture/review.test.mjs
node graph-grow/fixture/seek.test.mjs
node token-stream/fixture/seek.test.mjs
```

现有安装可设置 PLAYWRIGHT_PACKAGE 到包目录、CHROME_PATH 到浏览器程序。三条测试命令自行启动本地只读服务器，不需要先运行 http.server。

- graph 核心矩阵96组 + 定向审阅12组：两个 Theme、双画幅、全部拓扑、normal/reduced、最短/默认/最长时长
- 定向案例：star四外围+hub（USAGE中文例子）、chain总八节点（六字中文）、mesh竖屏九节点；局部1.5、3.2、4.8、6秒，fixture全片时间需加2秒
- 定向末态另存灰度、50%、25%尺寸图，用于人工核对起点→终点、灰度层级和缩小可读性
- token 核心矩阵72组 + 10组容量极值；格数80/容量比.5或1.5。overflow的.5无效，不生成这个组合
- 比较同一时刻顺播、直跳、回拖、重复seek像素；检查可见标签碰撞和字幕安全区、resize-and-return、dispose清理/节奏注销
- QA PNG与结果JSON只写各模块 qa（gitignored），不生成视频。截图字节通过不等于审美或官方Studio接纳

## 包闭包验证与回收

```sh
python handoff/calm-light/validate-packages.py
```

需要已安装的Harness控制运行时及acorn；必要时 HYPERFRAMES_DEPENDENCY_MODULE_ROOT 指向含node_modules的runtime根。该脚本只在临时目录freeze/validate，并输出准确包hash，不接纳资产。

本目录是GitHub源码交接包，不随Harness发行。将每个模块复制到现有登记 AssetSource 的 asset-library/sources/broll/calm-light/<id>/，再用当前部署根的 work.cmd component pack <source-directory> 生成候选。官方Windows Studio用两个真实账号Theme、两画幅、最长标签和各时长查看，由用户按新v2 ref/hash接纳。不得覆盖已冻结v1、vendor或生产接受记录。

## 本次采用的取舍

- 采用正交平涂，删除雾、彩色灯、环绕、随机旋转和末尾拉远；Theme颜色与字体仍由宿主提供
- hub保留接口并准确居中；竖屏chain采用纵向阅读轴。跳过原拓扑的路径画弧线，并避让不相关节点
- graph完整标签集确定性排版，不依赖历史帧；同容器尺寸恢复相同布局。无法放下就明确失败，不缩字
- camera.orbit_deg仍接受0–30以保持调用兼容，默认0，v2一律固定相机；token seed保留但不再扰动序号或格子
- path的>语法仍需入口适配；manifest与通用验证器使用n1/hub/n4
- 五段路径默认6秒时每段.35秒，最短4秒stretch约.233秒；若要求每段≥.35秒，应选择≥6秒
- token计数明确区分示意token换算和真实绘制格数；最大安全整数可能因字体/竖屏行宽被拒绝，详见USAGE容量错误
- reduced显示完整离散状态；最终结果放在5.9秒，以保持最长stretch末态间隔≤2秒

## QA 状态 · 2026-10-02

已执行：76项Node状态/几何/矩形布局测试、6项已有B-roll合同回归、JS与fixture语法检查、真实临时freeze/闭包验证和集中代码审查。测试覆盖居中、曲线避障、标签矩形分离、时间纯度、FIFO序号/计数同步及最大容量全部格子可见。

实际重试：系统Chromium启动失败，原因仍是 socket() failed: Operation not permitted。没有尝试绕过限制。

未验证：本次PNG、WebGL像素seek、真实字体视觉碰撞、逐像素对比度、审美、实际节奏probe和官方Windows Studio。审阅附件只有文字，未提供它提及的8张PNG；本次未声称看过那些图。

结论：源码候选可供本机验收，不声称视觉通过或已经接纳。
