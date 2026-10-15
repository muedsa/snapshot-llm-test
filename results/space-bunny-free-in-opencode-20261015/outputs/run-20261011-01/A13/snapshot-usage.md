# Snapshot 使用情况说明与踩坑记录

任务ID：A13
任务名称：品牌标志到完整活动应用
本次运行ID：run-20261011-01
完成状态：完成
结束原因：需求满足并完成逐图视觉自检
输出目录：`outputs/run-20261011-01/A13/`（路径基准：suite_root）
临时目录：`tmp/run-20261011-01/A13/`（路径基准：suite_root）
路径基准：suite_root；除本报告的 Markdown 本地链接（相对本文件所在目录）外，
所有记录中的本地路径均为相对 suite_root 的相对路径，未写死机器盘符或用户目录。

遵循 [PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录环境变量。
Markdown 本地链接相对当前文档；本报告位于 `outputs/<run_id>/A13/`，
故指向题库文档的链接为 `../../../tasks/…`。

## 1. 最终产物与需求完成情况


| 文件 | 用途 | 对应 DSL 或图 | 完成状态 |
|---|---|---|---|
| `symbol-color.snapshot` | 512×512 透明彩色图标定稿 DSL | `symbol-color.png` | 已完成 |
| `symbol-black.snapshot` | 512×512 透明纯黑图标定稿 DSL | `symbol-black.png` | 已完成 |
| `brand-banner.snapshot` | 1200×400 品牌横幅定稿 DSL | `brand-banner.png` | 已完成 |
| `launch-poster.snapshot` | 1080×1350 发布海报定稿 DSL | `launch-poster.png` | 已完成 |
| `brand-system.json` | 色彩、比例、图标构件、最小留白、各应用映射、负空间规则、核验结果 | — | 已完成 |
| `rationale.md` | 两方向差异 / 实际预览选择依据 / 小尺寸改进（287 字） | — | 已完成 |
| `snapshot-usage.md` / `task-metrics.json` | 报告与指标 | — | 已完成 |

需求逐项核对（依据**最终图与 32×32 缩略实际查看**：四张定稿各整屏一次、两张 32×32 实际尺寸一次、
两版 32×32 最近邻 8× 放大一次、方向 A/B 预览与并排对照图各一次）

| 题目要求 | 满足情况 | 证据 |
|---|---|---|
| 禁用现成标志、文字整体当图标、外部图片 | 满足 | 全套只用 DSL 图元；四个 DSL 里没有任何 `<Image>`；品牌符号是 6 个圆角矩形/圆的几何组合 |
| 先做两个真正不同几何方向的预览 | 满足 | A「环聚」= 圆环 + 3 层旋转薄片 + 光核（圆形/旋转）；B「窗格」= 圆角方框 + 3 条正交层格 + 45° 光束 + 焦点（方形/正交）。各出 512×512 透明 PNG，存在 `preview/dir-A.png`、`preview/dir-B.png`，另出并排对照图 `preview/dir-sheet.png` |
| 看图选择后完善同一方案 | 满足 | 实际打开两张预览与对照图后选 B；后续 v1–v4 的返工只发生在**选定方案**上，方向 A 未被继续修改 |
| 512×512 透明彩色图标 | 满足 | 服务 `image_info` 为 PNG 512×512 RGBA；四角像素 `(0,0,0,0)` 确认透明 |
| 512×512 透明纯黑图标 | 满足 | PNG 512×512 RGBA；`violating_pixels = 0` |
| 1200×400 品牌横幅 | 满足 | 服务 `image_info` 为 PNG 1200×400 |
| 1080×1350 发布海报 | 满足 | 服务 `image_info` 为 PNG 1080×1350 |
| 两图标几何相同 | 满足 | 同一个 `symbol()` 只换调色板；把两份 DSL 的颜色字面量归一化后**逐字节相同**；alpha 通道差异仅 455/262 144 像素（0.17%）且最大差 1 级，全部在抗锯齿外缘 |
| 抗锯齿 alpha 允许 | 满足 | 纯黑版 alpha 范围 1–255，共 108 967 个 alpha>0 像素 |
| 非透明黑版 RGB 必须为 0 | 满足 | 未预乘 8 位 RGBA 全量扫描：alpha>0 像素 108 967 个，RGB≠0 的 **0** 个；alpha=0 的 0 个像素不参与判断；记录见 `brand-system.json.verification.black_check` |
| 图标最多 6 个主要几何构件 | 满足 | 可见构件 6 个（框 1 + 层格 3 + 光束 1 + 焦点 1），`within_limit = true`，逐个构件给母形/实例/几何参数/组合裁剪负空间/DSL 定位 |
| 不能把多个母形合并成容器或路径压计数 | 满足 | 每个构件都是独立 DSL 节点：框 = 1 个 Container(border)，层格 = 3 个独立 Container，光束 = 1 个 Container + Transform，焦点 = 1 个 ClipOval；没有任何母形被包进同一容器 |
| 不按 DSL 节点数计数 | 满足 | 按母形实例计：ClipOval + Container 两个节点只算 1 个圆；Transform 不另计；位置与尺寸不另计 |
| 32×32 仍能识别轮廓与关键负空间 | 满足 | 两版各出一张 32×32（保持正方形、保留 alpha）并在统一浅色底上以**实际 32 像素尺寸**打开：圆角方框轮廓、三条层格、四条横向通道与斜向断口均可辨 |
| 缩略使用预乘 alpha 重采样 | 满足 | 整数预乘 `ImageChops.multiply` → RGB 与 alpha 各做一次 Lanczos → 逐像素 `RGB = min(255, round(pm·255/a))` 恢复未预乘；工具/版本/参数记入 `brand-system.json.verification.tool` |
| 缩略仅作检查预览、存临时目录 | 满足 | 4 张缩略与 2 张放大图全在 `tmp/run-20261011-01/A13/preview/`；交付目录只有服务原始 PNG |
| 不用放大图替代原尺寸检查 | 满足 | `at_size_view_32px`（32×32 文件）与 `zoom_view_8x_nearest` 是两个独立文件，报告分列 |
| 缩略不加描边或锐化 | 满足 | `post_process` 明确记为「无额外描边、无锐化、无对比度拉伸」 |
| 横幅含「叠光 Layerlight」 | 满足 | 整屏查看：`叠光` 58px + `Layerlight` 44px 并排，右侧信息面板另起一块，不重叠 |
| 横幅含「把复杂信息，组织成清晰画面」 | 满足 | 整屏查看：标语单行 30px 完整显示，右边缘止于 x≈828，信息面板起于 x=880 |
| 不得把图标渲染 PNG 嵌进两应用 | 满足 | 横幅与海报的符号都由 `symbol()` 按同一几何规则**现场生成** DSL，只做等比缩放（0.3516 / 0.7813）与平移；四个 DSL 中无任何 base64/Image 引用 |
| 海报另含「2026.11.07 · ONLINE」 | 满足 | 海报中部信息条内为完整整串（含间隔号），34px |
| 海报另含「OPEN BETA」 | 满足 | 底部品牌色 CTA 条左侧 34px |
| 海报另含「layerlight.example.org」 | 满足 | CTA 条右侧 30px |
| 海报有独立构图，非放大横幅 | 满足 | 横幅是横向三区锁定（左符号 / 中字标+标语 / 右面板）；海报是竖向五段式（大符号 / 品牌字 / 标语 / 日期地点条 / CTA 条 / 页脚），两者的分区轴向、信息块数量与栅格都不同 |
| 交付 `brand-system.json` | 满足 | 含 `color` / `proportion` / `icon_components` / `component_count` / `negative_space` / `min_clear_space` / `applications` / `small_size` / `verification` 九组 |
| `rationale.md` ≤300 字 | 满足 | 287 个非空白字符（其中汉字 200），未超限 |
| 大图与 32×32 缩略均实际查看 | 满足 | `iterations.jsonl` 记录 11 次图像查看：4 张定稿整屏、2 张 32×32 实际尺寸、2 张 32×33 最近邻放大、方向 A/B 预览与对照图 |
| 记录违规像素数与 alpha 范围 | 满足 | `black_check` 同时记录 `violating_pixels = 0`、`alpha_positive_pixels = 108967`、`alpha_range = [1, 255]` |



## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com（与总 run-config.json 的 `service_base_url` 一致，覆盖子题默认地址）
文档访问日期：本次运行当天；字体清单由 `GET /fonts` 实际取得并缓存

AI 使用指南：https://open-snapshot.muedsa.com/ai-guide.md
实际阅读情况：已按指南使用 `POST /snapshot`（请求体为 UTF-8 纯文本 DSL，非 JSON），
按指南要求检查 HTTP 状态与 `Content-Type` 后才使用图片；遇到 `400 PARSE_ERROR`
时按响应 `message` 中的位置修正 DSL 后重新提交；未使用 `?errorImage=png`，
以保证错误 JSON 可被程序读取。字体通过 `GET /fonts` 查询后按返回值书写 `fontFamily`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|

| https://open-snapshot.muedsa.com/ai-guide.md | `POST /snapshot` 请求体为 UTF-8 纯文本 DSL（非 JSON）；成功返回图片二进制；失败返回含 `code`/`message`/`requestId` 的 JSON，按 `message` 中的 `position` 定位修正；`GET /fonts` 返回 text/plain 字体族列表 | `_suite/scripts/snapshot_render.py` |
| https://snapshot.muedsa.com/reference/parser-tags/ | 38 个标签的完整属性表（`Container`/`Stack`/`Positioned`/`Text`/`Flex`/`ClipOval`/`ClipRRect`/`Transform` 等） | `snapkit.py` 与各题 DSL |
| https://snapshot.muedsa.com/reference/enums/ | 枚举取值（`CrossAxisAlignment`、`BorderStyle`、`FlexFit`、`StackFit` 等）；已确认 `BorderStyle` 仅 `NONE`/`SOLID`、`CrossAxisAlignment` 无 `BOTTOM` | 各题构造器中的枚举取值 |

字体：实际调用 `GET /fonts` 取得 27 个字体族，原始响应留存于
`tmp/<run_id>/_suite/responses/`（`request_type=fonts`），整理副本见 `tmp/<run_id>/_suite/fonts-list.txt`。
中文正文用 `Noto Sans CJK SC`，拉丁与数字用 `Inter` 系列。本套 A 类任务素材政策为 `dsl_only`，
全部主体由 DSL 构造，**未使用 `<Image>` 标签**，未引入任何外部图片素材。

| https://snapshot.muedsa.com/reference/parser-tags/ · Container | 「出现任何边框或装饰属性时，解析器会构造 BoxDecoration，并把 `color` 合并进去」 | 据此推出 `color="#FFFFFF00"` + `border` 可得中空描边；并用 13 次探针实测确认（纯黑 0 违规、圆环中心 alpha=0） |
| 服务端行为（本 run 实测，无对应文档） | `borderRadius` < `border` 宽度时返回 500 INTERNAL_ERROR | 由 p4/p7/p8/p11/p12/p9/p10 二分定位；本套所有圆角框统一圆角 ≥ 2× 线宽 |


本次实际用到的能力：布局：`Container`/`Column`/`Row`/`Expanded`/`SizedBox`/`Padding`；精确定位：`Stack(fit=EXPAND)` + `Positioned`；文本：`Text` 的 `fontFamily`/`fontSize`/`textAlign`/`height`/`maxLines`/`letterSpacing`；颜色与透明度：CSS 颜色与 `#RRGGBBAA` 独立 alpha；装饰：`border`（宽度+样式+颜色）、`borderRadius` 与四角圆角、`boxShadow`；裁剪：`ClipRRect`/`ClipOval`；变换：`Transform` 的列主序 4×4 矩阵 + `alignment`；滤镜：`ImageFiltered`（子树模糊）、`BackdropFilter`（仅背景模糊）；渐变：`gradientType=LINEAR/RADIAL/SWEEP` + `gradientColors`/`gradientStops`。解析器未提供 `ClipPath`/多边形，所有图形均由矩形、圆角矩形、椭圆与渐变拼装。
本题额外用到：**`Container` 的 `border` 能画真正中空的框**——把 `color` 设成 `#FFFFFF00`、`borderRadius` 设成短边的一半，描边就沿圆/圆角矩形路径绘制，中心保持透明；这样一枚圆环或一个圆角方框只要**一个节点**，不必用几十个小胶囊去拼环。附带发现一条服务端硬限制：**`borderRadius` 必须大于 `border` 宽度**，否则返回 HTTP 500 INTERNAL_ERROR（180×180 上 r30+border34 失败、r45/r60/r90 成功，r30+border20 成功，且与 `color` 有无、长宽比都无关），本题统一让圆角 ≥ 2× 线宽。
**透明画布上只画 `#000000` 就能得到真正的纯黑图标**——实测 512×512 图标 108 967 个 alpha>0 像素里 RGB≠0 的有 0 个，alpha 保留 1–255 的抗锯齿边缘，因此不需要「先画黑再抠色」的后处理。
**8 位预乘/反预乘的取整是颜色相关的**：同一套几何、只换调色板重画，alpha 通道会在抗锯齿外缘出现 ±1 级差异（455/262 144 像素），黑版因为预乘 RGB 恒为 0 走了不同取整路径；几何本身逐字节一致。

字体：实际查询 `GET /fonts` 得到 27 个字体族，原始响应留存于
`tmp/run-20261011-01/A13/responses/`（request_type=fonts），另有整理副本 `outputs/run-20261011-01/A13/../_suite/fonts-list.txt`。
中文正文使用 `Noto Sans CJK SC`，数字/拉丁使用 `Inter` 系列，代码/等宽使用 `Noto Sans Mono CJK SC`。
题目素材政策为纯 DSL，未使用任何外部图片（`<Image>` 标签本次未使用）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/run-20261011-01/A13/requests.jsonl`
迭代记录文件：`tmp/run-20261011-01/A13/iterations.jsonl`
响应与草稿留痕：`tmp/run-20261011-01/A13/responses/`、`tmp/run-20261011-01/A13/drafts/`

渲染请求总数：34
成功次数：28
失败次数：6
重试请求数：0（是总请求的子集）
DSL版本数：29
实际图片查看次数：16
完整视觉迭代数：7
未完成视觉迭代数：0
其他接口查询：字体查询与文档读取为 run 级共享准备；本题额外做了 **13 次探针渲染请求**（1 次综合探针 + 12 次二分探针，定位 `borderRadius`/线宽的崩溃边界）与 **3 个设计方向预览请求**，全部 DSL、请求体、出图与 500/400 响应保留在临时目录。

初次生成和查看计为基线，不计为改进迭代。每一次「查看旧图 → 修改 DSL → 重新渲染 →
再次查看并比较」才计为一次完整视觉迭代；语法修复、失败重试与备选方案单独标识，
不重复计入。所有图片均已用图像工具实际打开查看（含整屏与放大局部）。

| 请求ID | 输入 DSL | 耗时 | HTTP / Content-Type | 响应文件 | 查看与实际结果 |
|---|---|---|---|---|---|
| A13-probe-ring-b3e01d9c | drafts/probe-ring.snapshot | 2.22s | 500 INTERNAL_ERROR | responses/A13-probe-ring-b3e01d9c.error.json | 无图；综合探针整体失败，引出「圆角小于线宽」的怀疑 |
| A13-p1-transparent-root-* | drafts/p1-transparent-root.snapshot | 1.31s | 200 image/png | preview/p1-transparent-root.png | 透明画布 + 纯黑方块：出图并全量扫描，alpha>0 的 14 400 像素 RGB≠0 的 **0** 个 |
| A13-p2-ring-white-* | drafts/p2-ring-white.snapshot | 1.72s | 200 image/png | preview/p2-ring-white.png | `border` + 圆角=直径/2 在白底上画出中空圆环（中心为白） |
| A13-p3-ring-transparent-* | drafts/p3-ring-transparent.snapshot | 0.89s | 200 image/png | preview/p3-ring-transparent.png | 同一构造在透明底上中心 alpha=0，证明圆环确实中空 |
| A13-p4-sqframe-* | drafts/p4-sqframe.snapshot | 0.82s | 500 INTERNAL_ERROR | responses/A13-p4-sqframe-644b9804.error.json | 无图；圆角 30 < 线宽 34 → 复现崩溃 |
| A13-p5-rot-rect-* | drafts/p5-rot-rect.snapshot | 0.88s | 200 image/png | preview/p5-rot-rect.png | `Transform` 绕 CENTER 旋转圆角矩形正常 |
| A13-p6-ring-no-color-* | drafts/p6-ring-no-color.snapshot | 0.94s | 200 image/png | preview/p6-ring-no-color.png | 不写 `color` 也能出圆环（说明 color 只是背景填充） |
| A13-p7-r30-nocolor-* | drafts/p7-r30-nocolor.snapshot | 1.32s | 500 INTERNAL_ERROR | responses/A13-p7-r30-nocolor-0aa8f904.error.json | 无图；去掉 color 仍 500，排除颜色因素 |
| A13-p8-r30-80-* | drafts/p8-r30-80.snapshot | 1.41s | 500 INTERNAL_ERROR | responses/A13-p8-r30-80-3c072674.error.json | 无图；半透明填充同样 500 |
| A13-p9-r45-* | drafts/p9-r45.snapshot | 0.96s | 200 image/png | preview/p9-r45.png | 圆角 45 ≥ 线宽 34 → 成功，锁定判据 |
| A13-p10-r60-* | drafts/p10-r60.snapshot | 0.83s | 200 image/png | preview/p10-r60.png | 圆角 60 → 成功 |
| A13-p11-r30-nonround-* | drafts/p11-r30-nonround.snapshot | 0.79s | 500 INTERNAL_ERROR | responses/A13-p11-r30-nonround-2357c2d0.error.json | 无图；180×120 上同样 500，排除长宽比 |
| A13-p12-r30-t20-* | drafts/p12-r30-t20.snapshot | 0.91s | 200 image/png | preview/p12-r30-t20.png | 圆角 30 > 线宽 20 → 成功，确认判据是圆角与线宽的比较 |
| A13-p13-cliprrect-* | drafts/p13-cliprrect.snapshot | 0.96s | 200 image/png | preview/p13-cliprrect.png | ClipRRect 正常（另一条中空路径，本题未用） |
| A13-dir-A-cad41fad | drafts/dir-A.snapshot | 1.46s | 200 image/png | preview/dir-A.png | 方向 A「环聚」512×512 透明预览，实际打开判读 |
| A13-dir-B-18ceba82 | drafts/dir-B.snapshot | 1.03s | 200 image/png | preview/dir-B.png | 方向 B「窗格」512×512 透明预览，实际打开判读 |
| A13-dir-sheet-3d09ef2e | drafts/dir-sheet.snapshot | 1.94s | 400 PARSE_ERROR | responses/A13-dir-sheet-3d09ef2e.error.json | 无图；Positioned 里并列了 Container 与 Stack |
| A13-dir-sheet-8ec6f4a1 | drafts/dir-sheet.snapshot | 1.24s | 200 image/png | preview/dir-sheet.png | 改正后出并排对照图，实际打开完成选择 |
| A13-v1-symbol-color-* | drafts/a13-symbol-color-v1.snapshot | 1.55s | 200 image/png | preview/a13-symbol-color-v1.png | 选定方案 v1 彩色图标（512×512），实际打开 |
| A13-v1-symbol-black-* | drafts/a13-symbol-black-v1.snapshot | 1.42s | 200 image/png | preview/a13-symbol-black-v1.png | v1 纯黑图标；全量扫描 0 违规 |
| A13-v1-brand-banner-668b2e31 | drafts/a13-brand-banner-v1.snapshot | 1.50s | 200 image/png | preview/a13-brand-banner-v1.png | 横幅首版，实际打开：标语压住右侧信息卡、分隔线穿卡、卡内小字被裁 |
| A13-v1-launch-poster-* | drafts/a13-launch-poster-v1.snapshot | 1.49s | 200 image/png | preview/a13-launch-poster-v1.png | 海报首版，实际打开：OPEN BETA 出现两次 |
| A13-v2-brand-banner-* | drafts/a13-brand-banner-v1.snapshot | 2.00s | 200 image/png | preview/a13-brand-banner-v2.png | 重排为横向三区后无重叠；实际打开复查通过 |
| A13-v2-launch-poster-* | drafts/a13-launch-poster-v1.snapshot | 1.90s | 200 image/png | preview/a13-launch-poster-v2.png | 去掉重复的状态块；实际打开复查通过 |
| A13-v3-poster-* | drafts/a13-launch-poster-v1.snapshot | 2.28s | 200 image/png | preview/a13-launch-poster-v3.png | 补回完整整串「2026.11.07 · ONLINE」；实际打开复查通过 |
| A13-v4-poster-* | drafts/a13-launch-poster-v1.snapshot | 3.52s | 200 image/png | preview/a13-launch-poster-v4.png | 符号 420→400 以满足最小留白；实际打开复查通过 |
| A13-final-* | outputs/run-20261011-01/A13/*.snapshot | 见 metrics | 200 image/png | outputs/run-20261011-01/A13/*.png | 四张定稿渲染并逐张打开复查 |

## 4. 修改记录与踩坑

| 版本 / 类型 | 观察到的实际问题 | 原因及确认依据 | 实际修改 | 复验结果 |
|---|---|---|---|---|
| probe · render-fail | 综合探针返回 500 INTERNAL_ERROR，本题的第一条线索就卡在这里 | 以为 `border` + 小圆角的圆角矩形框是安全写法 | 拆成 13 个最小用例逐个渲染，二分定位到 `borderRadius` 与 `border` 宽度的比较 | 圆角 ≥ 线宽即成功、圆角 < 线宽必 500，判据确定 |
| probe · visual | 透明底 + 纯黑方块是否真能得到 RGB 全 0？圆环是否真中空？没有文档保证 | 文档只说 PNG 支持 alpha、默认透明背景，没说抗锯齿边缘的 RGB | p1 做 200×200 全量像素扫描，p2/p3 在白底与透明底各画一次同样的圆环 | alpha>0 像素 RGB≠0 的 0 个；透明底上圆环中心 (0,0,0,0)，两条关键假设成立 |
| direction · selection | 方向 A 的内层簇只占圆环内径约三分之一，环内大片留白 | 首版把三条薄片做成 250×44 聚在中心 | 对照方向 B 出 512×512 透明预览 + 1160×600 并排对照图，实际打开看图 | 选定 B：圆角方框 32px 下仍是强剪影，层格撑满框内，通道负空间清晰 |
| direction · small-size | B 首版层格之间只有 19px，缩到 32×32 只剩 1.2px，通道会被糊死 | 按 512 画布的视觉比例定间隙，没有换算小尺寸下的可读性 | 层格高度 42→48、间隙 19→42、改为顶到框内边；光束 300×40→340×44；圆角 30→88 | 32×32 实际尺寸查看：四条通道与斜向断口均可辨（最近邻 8× 放大逐像素确认） |
| v1 → v2 · visual | 横幅：标语「把复杂信息，组织成清晰画面」右端压进右侧信息卡；分隔线穿进卡片；卡内小字「…的结构化表达」被裁；装饰条从文字后面穿过 | 标语框给了 620px 而中区只有 430px；信息卡与标语用的是同一行 y 区间；装饰条画在信息卡之前，半透明卡片让它透出来 | 改为横向三区：符号 180 + 字标 + 标语（中区宽 540）| 信息面板（右区 256px 独立卡片）；装饰条下移到 y≥330 并压到最低对比；卡内小字整条删除 | 横幅整屏复查：无重叠、无截断，两条必含文案完整可读 |
| v2 · visual | 海报上「OPEN BETA」在状态块和 CTA 条里各出现一次 | 先按「日期/地点/状态」三块栅格排，又在下方加了一条 CTA 条，两处都放了状态 | 状态只留给 CTA 条，栅格改成一条整宽的「日期 · 地点 / 2026.11.07 · ONLINE」信息条 | OPEN BETA 只出现一次，信息层级更清楚 |
| v3 · visual | 海报把日期与地点拆成两块后，题面要求的整串「2026.11.07 · ONLINE」缺了间隔号 | 按版式对称性把一条信息拆成了两个 284px 块，牺牲了字面完整性 | 改为 920px 整宽信息条，字面按题面原样一行给出（34px） | 整串「2026.11.07 · ONLINE」完整出现在海报上 |
| v4 · visual | 海报上符号下方到「BRAND SYSTEM · 01」只有 40px，低于自定的最小留白 54.7px | 符号按 420px 排版后才回头核对留白规则 | 符号 420→400（光学外框 344→328，留白要求降到 54.7px，实测间距 60px） | `brand-system.json.min_clear_space.compliance` 中 banner 62≥30.9、poster 60≥54.7 两条都成立 |
| check · measurement | 两版 alpha 通道有 455 个像素不同，比例 0.17% | 本以为同一函数只换调色板会得到逐像素一致的 alpha | 定位到差异全部落在 x≈56/455、y≈68/443（圆环外缘），最大差 1 级；补做 DSL 结构核验（颜色字面量归一化后逐字节比对） | 判定为 8 位预乘/反预乘取整的颜色相关性差异，属题面允许的抗锯齿 alpha 范围；几何一致性由 DSL 结构核验独立佐证 |

「渲染成功但视觉不符合要求」的问题同样记录在上面的完整视觉迭代中。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/run-20261011-01/A13/task-metrics.json`


| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始 / 结束时间 | 2026-10-12T09:05:00.000+08:00 / 2026-10-12T10:02:12.364+08:00 | ISO8601 带时区 | 计时记录（本地时钟，带时区） |
| 任务总耗时 | 3432.364 | 秒 | 墙钟时间（读题 → 计算 → 构造 → 渲染 → 看图 → 修复 → 报告） |
| 首次可用图耗时 | 3.528 | 秒 | 从开始到首个 `200 image/png` 且能打开的图为止的全部请求耗时之和；本任务请求串行，故与实际顺序一致 |
| 等待用户反馈 | 0.0 | 秒 | 本题为单轮任务，无多轮反馈等待 |
| 限流等待 | 0.0 | 秒 | 全程未出现 `429`（见 `requests.jsonl`） |
| 排队等待 | None | 秒 | 服务未提供排队指标，不可测量，记 null 而非 0 |
| 已记录请求耗时之和 | 51.425 | 秒 | `requests.jsonl` 中 `duration_seconds` 求和；请求串行，不与墙钟重复计入 |
| 成功 / 失败 / 重试请求 | 28 / 6 / 0 | 次 | `requests.jsonl`；失败均为不同 DSL 的语法修复，非同一请求重试 |
| 看图 / 完整视觉迭代 | 16 / 7 | 次 | `iterations.jsonl` 与实际图像查看记录 |
| DSL 版本数 | 29 | 个 | `requests.jsonl` 去重 |
| Server-Timing | null | — | 服务响应未返回该头，日志中如实记为 null |


## 6. 设计选择、经验与未解决事项


**关键设计选择**

1. *先探三个假设，再画图标*。本题的三个硬约束——「中空圆环能否一个节点画出来」、
   「透明底上纯黑是不是真的 RGB=0」「旋转是否绕中心」——文档都没有直接保证，
   所以先用 13 个最小探针把它们钉死。结果比预期好：`Container` 的 `border`
   配 `color="#FFFFFF00"` 与 `borderRadius=直径/2` 就能得到**真正中空**的圆环
   （`p3` 实测中心 (0,0,0,0)），透明画布上只画 `#000000` 的图标
   `violating_pixels = 0`。附带钉死了一条服务端硬限制：**`borderRadius` 必须大于 `border` 宽度**，
   否则 500。本实现统一让圆角 ≥ 2× 线宽。

2. *圆环只用 1 个构件，不用胶囊拼*。原先打算沿圆周摆 48 个小圆角矩形拼出圆环，
   算下来关节处会在内外缘留下缺口；探针证明 `border` 一行就够，整个符号从 5×48 个节点降到 6 个节点，
   构件计数也从「48 个胶囊」变成干净的 1 个圆环。

3. *构件计数与 DSL 节点数解耦*。`brand-system.json.component_count.basis` 把口径写死：
   框 1（Container+border 按 1 计）、层格 3（同母形重复放置分别计）、光束 1（含 Transform，变换不另计）、
   焦点 1（ClipOval + Container 两个节点按 1 个圆计）＝ 6，正好等于上限。
   框的内孔、层格通道、光束切出的对角断口都是母形之间的空隙，按题面规则不计入，
   但 `negative_space` 里逐条记录了它们的生成规则与「为什么在 32px 下必须保留」。

4. *四个应用共用一个 `symbol()`*。横幅里是 180px、海报里是 400px，比例完全一致，
   都由 `symbol(direction, cx, cy, size, palette)` 现场生成 DSL，
   没有任何一处嵌入渲染出来的 PNG——这一点在四个 `.snapshot` 里可以直接搜证。

5. *两版图标的「几何相同」用两条独立证据锁死*。① DSL 结构核验：把两份定稿 DSL 的颜色字面量
   归一化后**逐字节相同**；② alpha 通道逐像素比对：差异 455/262 144（0.17%），
   最大 1 级且全部落在圆环外缘的抗锯齿带上。报告里写明了成因（8 位预乘/反预乘取整与 RGB 有关，
   黑版预乘 RGB 恒为 0），而不是含糊地说「基本一致」。

6. *32×32 检查严格按题面口径做*。整数预乘 → Lanczos → 逐像素恢复未预乘，
   工具版本（Pillow）、方法、参数、无后处理都记进 `checks.json`；
   「实际 32 像素尺寸」与「最近邻 8× 放大」是两个独立文件，
   放大图只用来确认边缘台阶，不替代原尺寸检查。

**问题与修复（要点）**

- 最有价值的一笔是那 13 次探针。若直接凭直觉画圆角方框框，得到的会是一个
  500 错误而不是一个图标；而 `borderRadius` ≥ 线宽这条限制一旦不知道，
  后面每一处圆角描边都会踩雷。
- 返工最多的是**版面文字互相压住**：横幅首版把标语框开成 620px 却只留了 430px 的中区宽度，
  信息卡又与标语共用同一段 y 区间。改成显式的三区布局（并把各自的 x 边界写进
  `brand-system.json.applications`）之后一次通过。
- 海报差点在「字面完整性」上翻车：为了版面对称把日期与地点拆成两块，
  顺手把题面给的整串「2026.11.07 · ONLINE」连中间的间隔号一起弄丢了。
  这类"看起来更整齐"的改动必须逐条回到题面文字上核对。

**可复用经验**

- `Container` + `color="#FFFFFF00"` + `border` + `borderRadius` = **一个节点的中空框**，
  是画圆环/圆角方框的最省写法；但**圆角必须大于线宽**，否则 500。
- 透明底上只画 `#000000`，解码后 alpha>0 处 RGB 必然为 0，不需要任何后处理抠色。
- 同一几何只换调色板重画，alpha 通道在抗锯齿边缘可能有 ±1 级差异；
  要证明「几何相同」，把 DSL 的颜色字面量归一化后做结构比对比像素比对更有说服力。
- 品牌系统里的「最小留白」最好在**排版完成后再回头核对**——A13 的海报就是先按 420px 排完，
  才发现符号下方只剩 40px，低于自定的 54.7px，最后把符号缩到 400px 才达标。

**结束依据**：四张定稿各整屏打开一次（横幅查重叠与两条必含文案，海报查整串字面与 CTA），
两版 32×32 缩略各在统一浅色底上以实际 32 像素尺寸打开一次、另各出一张最近邻 8× 放大图；
纯黑版做了 512×512 全量像素扫描（108 967 个 alpha>0 像素，0 违规，alpha 1–255）。
未以「渲染成功」作为完成依据。


### 未解决事项 / 限制


- 无影响交付的未解决问题。
- 两版图标的 alpha 有 455 像素（0.17%）相差 1 级。已在
  `brand-system.json.verification.geometry_identity` 中给出成因与两处独立证据；
  若将来要求逐位完全一致，只能改用单一构件配色（例如整枚图标一个颜色 + 负空间），
  但那会牺牲彩色版的层次表达，与题面「两个方向」的设计意图冲突，故按题面允许的
  「抗锯齿 alpha 允许」处理并如实记录。
- `borderRadius` < `border` 宽度会 500，是本 run 的实测结论而非文档承诺；
  若服务端升级改变该行为，需要重跑 `probe_bisect2.py` 复核后再改 `geom_a13.py`。
- 海报与横幅上的装饰条（低对比横条）复用了层格母形，但它们属于版面装饰，
  不计入图标的 6 个构件；这一点已在 `brand-system.json.application_mapping_rule` 说明。


### 留痕确认

- 临时目录中的草稿 DSL、各次请求体副本、成功图片、失败响应 JSON、放大裁切图与预览全部保留，未删除或覆盖任何一次尝试；日志为追加写入。
- `tasks/` 下的输入文件、任务说明与模板均未被修改。
- 未保存任何密钥；`SNAPSHOT_API_KEY` 若存在只从环境变量读取，不写入 DSL 或日志。
- 总任务根 `.gitignore` 已创建（参考 `templates/gitignore-template.txt`），仅排除 `__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`、`.ipynb_checkpoints/`、`node_modules/.cache/` 等明确的运行时缓存；**未**使用 `tmp/`、`outputs/`、`cache/`、`.cache/`、`*.log` 或图片/DSL/JSON 通配规则，因此本任务的过程证据不会被忽略（共享规则详见 `_suite/snapshot-usage.md`）。
- `__pycache__/` 等运行时缓存不作为留痕材料，也不列为产物或自检证据。
