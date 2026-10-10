# Snapshot 使用情况说明与踩坑记录

任务 ID：B01
任务名称：十张真实场景的炫酷用例
本次运行 ID：run-20261002-220723-mimo
完成状态：完成
结束原因：需求满足并完成视觉自检
输出目录：`outputs\run-20261002-220723-mimo\B01`
临时目录：`tmp\run-20261002-220723-mimo\B01`

---

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `case-01/final.snapshot` | 完整可复现 DSL（14529 B） | `case-01/final.png` 900×1600 | 完成 |
| `case-02/final.snapshot` | 完整可复现 DSL（33621 B） | `case-02/final.png` 1920×1080 | 完成 |
| `case-03/final.snapshot` | 完整可复现 DSL（16398 B） | `case-03/final.png` 1080×1440 | 完成 |
| `case-04/final.snapshot` | 完整可复现 DSL（60744 B） | `case-04/final.png` 1200×900 | 完成 |
| `case-05/final.snapshot` | 完整可复现 DSL（40148 B） | `case-05/final.png` 800×1200 | 完成 |
| `case-06/final.snapshot` | 完整可复现 DSL（30688 B） | `case-06/final.png` 1600×1000 | 完成 |
| `case-07/final.snapshot` | 完整可复现 DSL（37173 B） | `case-07/final.png` 1200×1200 | 完成 |
| `case-08/final.snapshot` | 完整可复现 DSL（11878 B） | `case-08/final.png` 1080×1080 | 完成 |
| `case-09/final.snapshot` | 完整可复现 DSL（44207 B） | `case-09/final.png` 1080×1350 | 完成 |
| `case-10/final.snapshot` | 完整可复现 DSL（16576 B） | `case-10/final.png` 1920×640 | 完成 |
| `portfolio.json` / `portfolio.md` | 逐件元数据与策展说明 | 全 10 件 | 完成 |
| `gallery.html` | 本地画廊，索引全部 10 件最终图 | 全 10 件 | 完成 |
| `snapshot-usage.md` | 本文件 | — | 完成 |
| `task-metrics.json` | 结构化指标 | — | 完成 |

**需求完成情况**（题面逐条）：

- 「至少 10 件独立完整主作品」→ 10 件，画幅比例 10 种互不重复，见第 6 节独立性核对。
- 「每件交付 final.png、final.snapshot、case.md」→ 10 × 3 = 30 个文件齐全。
- 「所有最终 PNG 必须是实际服务响应」→ 10 张 PNG 均为 `POST /snapshot` 返回字节直接落盘；
  已用脚本读取 IHDR 校验：PNG 签名 `89504e470d0a1a0a`、colorType=6、宽高与声明一致。
- 「不给行业名单/文案/配色/尺寸/构图模板，自主寻找场景」→ 场景、受众、媒介、尺寸、配色、
  构图全部自拟，见 `portfolio.md` 的策展表。
- 「十张体现实质不同的使用任务与视觉想法」→ 见第 6 节。
- 「自拟品牌和示例数据允许但需说明」→ 10 件画面内均标 `演示数据 DEMO`，
  `portfolio.json` 逐件 `content_basis` 标明虚构，本文件末尾另有声明。
- 「给出逐件最终图与完整 DSL、整体画廊、使用说明、过程与消耗记录」→ 见上表与
  `gallery.html`、本文件、`task-metrics.json`、临时目录下的三个 jsonl。
- 「不设固定调用/迭代上限、持续工作」→ 共 24 次渲染、9 次完成视觉迭代 + 1 次未完成迭代、
  26 次实际看图；未因「已有 10 件」提前收工。

**未满足的要求**：无。

---

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（以总 `run-config.json` 的 `service_base_url` 为准，
覆盖子题 `run-config.json` 中的默认值）
文档访问日期：2026-10-05（UTC+08:00）

AI 使用指南：`https://open-snapshot.muedsa.com/ai-guide.md` — 实际 GET（请求 ID `B01-doc-001`，200，
1417.1 ms），落盘 `tmp/.../B01/doc-ai-guide.md`。据此确定请求格式为
`POST /snapshot`、`Content-Type: text/plain; charset=utf-8`、body 为 UTF-8 DSL 文本，
并采用「检查 HTTP 状态 + Content-Type 为 image/* + 字节落盘 + 读回图片」的响应检查顺序；
错误 JSON 不落为最终图。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| `https://open-snapshot.muedsa.com/ai-guide.md`（doc-001） | 请求/响应格式、错误处理、字体查询 | `doc-ai-guide.md`；`_suite/render.ps1` 的请求与失败落盘逻辑 |
| `https://snapshot.muedsa.com/reference/parser-tags`（doc-007，`doc-parser-tags.txt`） | 标签与属性全表：`gradientStops` 必须与颜色等长、取值 0~1 且升序；`gradientStartAngle/EndAngle` 单位为弧度且 start < end（默认 0 / 2π）；`border` 值格式为 `width style color`；`Transform matrix` 为 16 个有限浮点；`clipBehavior` 非 NONE 需要背景装饰 | case-08 的 75% 进度环（**后续实测发现服务端 SWEEP 忽略停点与起止角，已改用 `DialArc`**）；全任务 `BD()` 前缀；case-03/05 的矩阵修复 |
| `https://snapshot.muedsa.com/guides/layout`（doc-003） | `Stack` / `Positioned` 布局：`Positioned` 只能是 `Stack` 的直接子级 | 全 10 件的栅格；`Box/T/Circle` 结果不能塞进 `Transform/Opacity/*Filtered/Clip*`，故另备 `C/CC/CGrad/OpX/RotX/BlurX/BlendX` 裸发射器 |
| `https://snapshot.muedsa.com/guides/painting`（doc-002） | 渐变（LINEAR/RADIAL/SWEEP、stops、tileMode、start/end angle）、`boxShadow` 自定义格式 | case-08 圆环、case-02 风圈、case-09 页眉、case-06 徽标、全任务卡片投影 |
| `https://snapshot.muedsa.com/guides/concepts`（doc-004） | 颜色格式 `#RGB / #RGBA / #RRGGBB / #RRGGBBAA` | 全 10 件（含 `#C9A88A33` 这类半透明投影色） |
| `https://snapshot.muedsa.com/guides/widgets`（doc-005） | `Text` 组件与对齐枚举 | 全 10 件文字层级 |
| `https://snapshot.muedsa.com/guides/media-text`（doc-006） | 文本排版、宽度与换行 | `TW/Fit/MaxTW/WrapTW/TLines/TPara` 的宽度估算与生成期溢出校验 |
| `https://snapshot.muedsa.com/`（doc-002 组内，`doc-site-root.html`） | 站点入口与文档索引 | 用于定位上述页面 |

**本次实际用到的能力**（只列真实使用过的）：

- **布局**：`Snapshot` → `Container` → `Stack` → `Positioned` 四层；全部元素用绝对坐标定位。
- **形状与装饰**：`Box`（含 `borderRadius`、`border`）、`shape="CIRCLE"`、`borderRadius` 卡片、
  `boxShadow`（格式 `x y [blurRadius] [spreadRadius] [color] [blurStyle]`）。
- **渐变**：LINEAR（`gradientBegin/End` 对齐对）、RADIAL（`gradientCenter/Radius`）、
  SWEEP（`gradientColors` + `gradientStops` + `gradientStartAngle/EndAngle`，弧度制）。
- **文本**：`Text` 的字号/行高/`bold`/`textAlign`（LEFT/CENTER/RIGHT）、
  `textShadow`（`x y [blurSigma] [color]`）、同坐标多层叠印做描边（case-05）。
- **几何与变换**：`Transform matrix="(…)"`（16 浮点、外层括号、列-major、平移在 12/13 位）用于
  case-03 / case-05 的角度元素。
- **裁剪/滤镜**：能力探针中真实验证了 `ImageFiltered`、`ColorFiltered(SCREEN)`、`ClipOval`、
  `boxShadow`；**正式作品未使用滤镜**——探针显示滤镜与 `borderRadius` 组合会残留洋红角，
  故 10 件全部改用纯几何与渐变达到质感。
- **无 `<Image>`**：A 轨限制不适用于 B 轨（本题 `asset_policy = dsl_primary_with_supporting_assets`），
  但 10 件实际全部为纯 DSL，未嵌入任何外部素材。

**字体**：未在本题期间重新查询字体（此为复用本 run 内此前已真实取得的字体清单
`Noto Sans CJK SC / JP / KR / TC / HK`、`Noto Serif CJK`、`Inter`、`DejaVu`、`Noto Color Emoji`）。
10 件统一使用 `Noto Sans CJK SC` 作为中文字族；本次没有新增字体 HTTP 请求，故 `document_requests`
只计 7 条。

---

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/run-20261002-220723-mimo/B01/requests.jsonl`（31 行）
迭代记录文件：`tmp/run-20261002-220723-mimo/B01/iterations.jsonl`（25 行）
工具记录文件：`tmp/run-20261002-220723-mimo/B01/tool-usage.jsonl`（13 行）

- 渲染请求总数：**24**（1 共享探针 + 23 用例；其中 2 条为关闭后的 case-08 修正批次）
- 成功次数：**22**
- 失败次数：**2**（`B01-c03-r1`、`B01-c05-r1`，均为 HTTP 400 `PARSE_ERROR`）
- 重试请求数：**2**（`B01-c03-r2`、`B01-c05-r2`，是总请求的子集）
- 文档请求数：**7**（全部 200）
- 总请求行数：**31**（7 文档 + 24 渲染，其中 `B01-c08-r2`/`B01-c08-r1b` 为关闭后修正批次）
- DSL 版本数：**23**（22 用例版本 + 1 探针版本；`B01-c08-r1b` 复用已归档的 v1 DSL，不构成新版本）
- 实际图片查看次数：**26**（含探针 1 次、各用例 25 次）
- 完整视觉迭代数：**9**
- 未完成视觉迭代数：**1**
- 其他接口查询：无（本题只用 `POST /snapshot` 与文档 GET，无 `/fonts` 等其他接口）

**基线 vs 迭代的口径**：首次生成并查看计为 baseline（case-01/02/04/06/07/08/09/10 与
case-03、case-05 的 r2 版本，共 10 次 baseline 查看），不计入改进迭代。
「看旧图 → 改 → 新渲染 → 看新图」才算一次完整视觉迭代。

| 请求ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| B01-probe-01 | `tmp/.../B01/probe-01.snapshot` | 2026-10-05T15:58:40.611+08:00 → 15:58:46.180+08:00，5.569 s | 200 / image/png | `tmp/.../B01/probe-01.png` | 已查看：矩阵、描边字、textShadow、SWEEP/RADIAL、ImageFiltered、ColorFiltered、ClipOval 全部符合预期 |
| B01-c01-r1 | `tmp/.../case-01/final.snapshot` | 16:16:19.720 → 16:16:24.129+08:00，4.409 s | 200 / image/png，236495 B | `outputs/.../B01/case-01/final.png` | 已查看，首版即合格 |
| B01-c02-r1 | `case-02/final.snapshot` | 16:16:24.200 → 16:16:29.509+08:00，5.310 s | 200 / image/png | `case-02/final.png`（后被取代，副本存 `attempts/v1-reviewed/`） | 已查看：发现 5 处缺陷（见第 4 节） |
| B01-c03-r1 | `case-03/final.snapshot` | 16:16:29.526 → 16:16:31.311+08:00，1.785 s | **400 / application/json** | `attempts/v1/failures/B01-c03-r1.body` | 无图可看；错误 `PARSE_ERROR … Attr [matrix] value format error` |
| B01-c04-r1 | `case-04/final.snapshot` | 16:16:31.353 → 16:16:35.199+08:00，3.846 s | 200 / image/png | `case-04/final.png`（副本 `attempts/v1-reviewed/`） | 已查看：曲线区过矮、标签牌相碰、指标行距不足 |
| B01-c05-r1 | `case-05/final.snapshot` | 16:16:35.215 → 16:16:36.470+08:00，1.256 s | **400 / application/json** | `attempts/v1/failures/B01-c05-r1.body` | 无图可看；同 matrix 错误 |
| B01-c03-r2 | `case-03/final.snapshot` | 16:20:18.458 → 16:20:24.937+08:00，6.479 s | 200 / image/png | `case-03/final.png`（副本 `attempts/v1-reviewed/`） | 已查看（baseline）：分段条等分导致条尾不落点 |
| B01-c05-r2 | `case-05/final.snapshot` | 16:20:24.995 → 16:20:31.485+08:00，6.490 s | 200 / image/png | `case-05/final.png`（副本 `attempts/v1-reviewed/`） | 已查看（baseline）：CTA 压住二维码 |
| B01-c02-r3 | `case-02/final.snapshot` | 16:29:46.160 → 16:29:49.857+08:00，3.697 s | 200 / image/png，253946 B | `case-02/final.png` | 已查看：5 处缺陷全部消失 |
| B01-c03-r3 | `case-03/final.snapshot` | 16:29:49.927 → 16:29:55.497+08:00，5.570 s | 200 / image/png，220595 B | `case-03/final.png` | 已查看：5 段条尾精确落在 x=850 |
| B01-c04-r3 | `case-04/final.snapshot` | 16:29:55.514 → 16:30:00.415+08:00，4.901 s | 200 / image/png，155756 B | `case-04/final.png` | 已查看：「6:00」可见、无重叠 |
| B01-c05-r3 | `case-05/final.snapshot` | 16:30:00.430 → 16:30:04.286+08:00，3.856 s | 200 / image/png，245259 B | `case-05/final.png` | 已查看：CTA 与二维码分离 |
| B01-c06-r1 | `case-06/final.snapshot` | 16:55:19.599 → 16:55:25.374+08:00，5.775 s | 200 / image/png，274436 B | `case-06/final.png` | 已查看，首版即合格 |
| B01-c07-r1 | `case-07/final.snapshot` | 16:55:25.439 → 16:55:29.364+08:00，3.925 s | 200 / image/png | `case-07/final.png`（副本 `attempts/v1-reviewed/`） | 已查看：解说与盘面/结果栏互相矛盾 |
| B01-c08-r1 | `case-08/final.snapshot` | 16:55:29.380 → 16:55:32.452+08:00，3.072 s | 200 / image/png，179866 B | `case-08/final.png`（首版；DSL 归档 `attempts/pre-ringfix-20261006/case-08.final.snapshot`，图像见下方 `B01-c08-r1b`） | 已查看；**事后判定有误**：环实为 50.14%、自 90° 起，见第 4 节「关闭后修正」 |
| B01-c09-r1 | `case-09/final.snapshot` | 16:55:32.467 → 16:55:36.859+08:00，4.392 s | 200 / image/png | `case-09/final.png`（副本 `attempts/v1-reviewed/`） | 已查看：面积填充有抗锯齿接缝 |
| B01-c10-r1 | `case-10/final.snapshot` | 16:55:36.878 → 16:55:39.830+08:00，2.952 s | 200 / image/png | `case-10/final.png`（副本 `attempts/v1-reviewed/`） | 已查看：中栏右上角说明被卡片边缘裁切 |
| B01-c07-r2 | `case-07/final.snapshot` | 17:01:12.802 → 17:01:17.176+08:00，4.375 s | 200 / image/png | `case-07/final.png`（副本 `attempts/v2-reviewed/`） | 已查看：内容自洽，但出现行首标点 |
| B01-c09-r2 | `case-09/final.snapshot` | 17:01:17.236 → 17:01:20.411+08:00，3.175 s | 200 / image/png，191533 B | `case-09/final.png`（查看副本 `v09-*.png`） | 已查看：填充成为连续色块 |
| B01-c10-r2 | `case-10/final.snapshot` | 17:01:20.428 → 17:01:23.812+08:00，3.384 s | 200 / image/png，189776 B | `case-10/final.png`（查看副本 `v10-*.png`） | 已查看：说明文字完整、留白 24px |
| B01-c07-r3 | `case-07/final.snapshot` | 17:03:10.629 → 17:03:15.461+08:00，4.832 s | 200 / image/png | `case-07/final.png`（DSL 副本 `attempts/v3-lines/`） | **查看无效**：读图工具返回同路径旧缓存字节；生成期 `Fit` 报 2 处超宽 |
| B01-c07-r4 | `case-07/final.snapshot` | 17:04:07.628 → 17:04:10.430+08:00，2.802 s | 200 / image/png，239177 B | `case-07/final.png`（查看副本 `view-check.png` + 2x 放大 `zoom-07.png`） | 已查看：三段各 3 行、行首无标点、数字自洽 |
| **B01-c08-r2** | `case-08/final.snapshot`（v2） | 2026-10-06T13:41:44.545 → 13:41:49.132+08:00，4.580 s | 200 / image/png，185785 B | `outputs/.../B01/case-08/final.png`（当前交付版） | **关闭后修正**已查看：亮弧 12 点→9 点、复测 75.28% 自 358° 起，4 条完成标准全部通过 |
| **B01-c08-r1b** | `attempts/pre-ringfix-20261006/case-08.final.snapshot`（v1 重建） | 13:54:51.701 → 13:54:54.575+08:00，2.867 s | 200 / image/png，179866 B | `attempts/pre-ringfix-20261006/case-08.v1-reconstructed.png` | 已查看：亮弧只覆盖 3 点→6 点→9 点的下半圈，直观复现 50.14% 缺陷 |

**看图方式**：`browser.preview` 在本次环境不可用（浏览器会话断开），全部改用直接打开图片文件查看。
看图过程中发现读图工具对**同一路径**会返回先前读过的旧缓存字节（共 5 次），
应对方式是把当前 PNG 复制到**唯一文件名**再读，或裁出局部放大图核对小字号；
这些复制件与放大图全部保留在临时目录（`case-07/view-check.png`、`case-07/zoom-07.png`、
`case-09/view-171022.png`、`v09-171103038.png`、`v10-171300210.png`）。
该问题直接导致 `ite-B01-c07-v3` 成为 1 次未完成迭代，已如实标注。

---

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| `ite-B01-c03-v1` / 语法修复 / 无 | HTTP 400 `PARSE_ERROR: Attr [matrix] value format error at position 528 near … Transform matrix="0.939693,-0.34202,0,0,0.34202,…"` | 服务错误响应体（已留存），与 `reference/parser-tags` 中「matrix 为 16 个有限浮点」的定义对照，缺外层括号导致逗号分隔被误解析 | `RotM/RotX` 统一输出 `matrix="(v,v,…)"`：外层一对括号、无空格、平移量在第 12/13 位 | `B01-c03-r2` 返回 200 并产出可打开 PNG；同因错误在 case-05 复发一次后同样修复 | `case-03/attempts/v1/`、`case-03/attempts/v1/failures/B01-c03-r1.body` |
| `ite-B01-c05-v1` / 语法修复 / 无 | 同上 400 | 同一 matrix 问题 | 同上 | `B01-c05-r2` 返回 200 | `case-05/attempts/v1/failures/B01-c05-r1.body` |
| `ite-B01-c02-v1→v2` / 视觉迭代 / v1 | 风圈不共圆心；路径走向与「WNW」标注矛盾；「台风中心」标签牌压线；FORCES 数值与单位粘连；底部时间轴被裁 | 首次看图逐项比对（图证据存 `attempts/v1-reviewed/`）；路径点序列的 x 递减方向与文字方向不一致是明确的逻辑错误 | 风圈圆心统一 (510,340)；路径点改为 WNW 序列；标签牌移到 (534,296)；单位 x 改 `1420 + TW(数值) + 10`；底板 h=326 并补页脚行 | `B01-c02-r3` 复看：5 项全部消失，无剩余问题 | `case-02/attempts/v1-reviewed/` |
| `ite-B01-c03-v2→v3` / 视觉迭代 / v2 | 5 段进度条等分，条尾不落在轨道终点 | 分段比例被写成等分，与真实里程 21.0975 km 不符（图证据 `attempts/v1-reviewed/`） | 改用真实累计比例 `0.2378/0.4755/0.7102/0.9460/1.0`，`$barMax = 640`，轨道色 `#16241B` | `B01-c03-r3` 复看：5 段条尾精确落在 x=850，与里程一致 | `case-03/attempts/v1-reviewed/` |
| `ite-B01-c04-v1→v2` / 视觉迭代 / v1 | 「6:00」刻度被压住；3 个节点标签牌相碰并压曲线；指标行粘连 | 首次看图（图证据 `attempts/v1-reviewed/`） | 曲线区 `$cy0=200,$chh=324`；标签牌移到 (178,384)/(470,260)/(578,224)；指标 `$y = 198 + i*92`，分隔线 574、结论行 580 | `B01-c04-r3` 复看：无重叠、刻度可见 | `case-04/attempts/v1-reviewed/` |
| `ite-B01-c05-v2→v3` / 视觉迭代 / v2 | 「扫码购票」压住二维码右上角 | 首次成功渲染后的看图（图证据 `attempts/v1-reviewed/`） | 从 (566,1050) 移到 (520,992) 并改右对齐 | `B01-c05-r3` 复看：两者各自留白 | `case-05/attempts/v1-reviewed/` |
| `ite-B01-c07-v1→v2` / 视觉迭代 / v1 | 解说称「三三侵角」但盘面第 6 手是小飞挂；「黑先占右上与右下星位」与盘面（黑 D16/Q16、白 Q4/D4）不符；「白胜 1.5 目」与「白中盘胜」互斥；41+42.5 算不出 1.5 目分差 | 首次看图逐手核对坐标与结果栏（图证据 `attempts/v1-reviewed/`） | 解说改写为与盘面对应的落点；结果改为黑 71 / 白 66 / 贴 6.5 → 白 72.5，白胜 1.5 目；条形比例 201:187 | `B01-c07-r2` 复看：内容自洽，但中文自动换行出现行首标点 | `case-07/attempts/v1-reviewed/` |
| `ite-B01-c07-v2→v3` / 视觉迭代（**未完成**）/ v2 | 行首出现「，」 | TPara 自动换行不处理中文禁则；确认依据是 r2 的实际图片与换行结果 | 改用 `TLines` 手动指定每行内容 | 渲染 200，但**未能取得与该版本一致的图像查看**（读图工具返回同路径旧缓存），故该次迭代计为未完成；生成期 `Fit` 另报 2 处超宽（448>364、373>364） | `case-07/attempts/v3-lines/` |
| `ite-B01-c07-v3→v4` / 视觉迭代 / v3 | 两行超出 364px 文本框 | 生成器 `Fit` 校验输出（程序诊断，非图像） | 把两行各拆成两行，每块固定 3 行、每行 < 364px | `B01-c07-r4` → `problems = 0`；用 2x 局部放大图 `zoom-07.png` 逐行核对：三段各 3 行、行首无标点、无溢出、结果栏自洽 | `case-07/attempts/v3-lines/`、`case-07/zoom-07.png`、`case-07/view-check.png` |
| `ite-B01-c09-v1→v2` / 视觉迭代 / v1 | 面积填充区出现可见竖向接缝 | 96 个独立矩形之间存在亚像素间隙 + 抗锯齿（图证据 `attempts/v1-reviewed/`） | 填充块宽度 `+1.4px` 使相邻块重叠 | `B01-c09-r2` 复看：填充连续、无接缝 | `case-09/attempts/v1-reviewed/` |
| `ite-B01-c10-v1→v2` / 视觉迭代 / v1 | 中栏右上角「北门在上 · 南门在下」被卡片右边缘裁掉 | 文本框 `1100 + 304 = 1404` 超出卡片右边界 `600 + 800 = 1400`（坐标计算，配合看图确认） | 文本框改为 `(1060, 66, 316, 28)`，右边界 1376（24px 内边距） | `B01-c10-r2` 复看：文字完整、三栏边界清晰 | `case-10/attempts/v1-reviewed/` |
| `ite-B01-c08-v2-visual` / 视觉迭代（**关闭后修正**）/ v1 | 声明「75% 弧、12 点起顺时针」，实测亮弧 **50.14% 且自 90°（3 点方向）起** | `System.Drawing` 沿圆周逐 0.5° 取样：修正前 ON = 361/720、起点样本 180（90°）；根因是真实服务的 `SWEEP` 渐变**不遵循 `gradientStops` 与 `gradientStartAngle`**——`stops=0,0.75,0.75,1` + `start=-π/2` 被渲染成 `[90°, 0.75×360°]`。同一现象在 B02 case-01 以 `f=0.62` 复现（自 138° 起），B02 因此全程改用 `DialArc` | `lib-b01.ps1` 新增 `DialArc`；`gen-b01-b.ps1` 把 `Seg (RingProg …)` 换成白色镂空圆 + `DialArc(156,360,260,0.75,#FF8A5B,#F6E4D6,32,100)`，`RingProg` 保留加注作为代码证据 | `B01-c08-r2` → 200；复测 ON = 542/720 = **75.28%**、起点样本 716（358°）；看图 4 条标准全部通过；`B01-c08-r1b` 重建的 v1 图（179866 B，与原响应字节数一致）已打开查看，可见下半圈亮弧，缺陷直观可复现。回归：重新生成后 `case-06/07/09/10` 哈希与修正前完全一致 | `lib-b01.ps1`、`gen-b01-b.ps1`、`attempts/pre-ringfix-20261006/` |

**已遇到并确认的踩坑**：

1. **`Transform matrix` 必须有外层括号**——缺括号直接 400 `PARSE_ERROR`（case-03、case-05 各一次）。
2. **`border` 必须是 `width style color`**——只给颜色会 PARSE_ERROR，故 `BD()` 统一补前缀。
3. **`Positioned` 只能是 `Stack` 的直接子级**——因此 `Box/Circle/T` 的返回值永远不能嵌进
   `Transform/Opacity/ImageFiltered/ColorFiltered/Clip*`，需要 `C/CC/CGrad/OpX/RotX/BlurX/BlendX`
   这类裸发射器直接拼字符串。
4. **`ColorFiltered` + `borderRadius` 会残留洋红角**——在能力探针中观察到，正式作品全部避开。
5. **中文自动换行不处理禁则**——会出现行首逗号，需用 `TLines` 手动断行（case-07）。
6. **文字必须预估宽度**——`Fit` 在生成期就能报出超宽行，比渲染后看图更快；本次靠它省掉了一次往返。
7. **96 个独立矩形拼面会有抗锯齿接缝**——相邻块重叠 1px 以上即可消除（case-09）。
8. **读图工具按路径缓存**——同一路径重读会返回旧字节；用唯一文件名副本或局部放大规避。
   这是环境问题，不是 DSL 问题，但已导致 1 次未完成迭代。
9. **`SWEEP` 渐变不遵循 `gradientStops` 与 `gradientStartAngle`（真实服务实测）**——
   case-08 首版用 `stops=0,0.75,0.75,1` + `start=-π/2` 想画 75% 弧，实测出来是
   `[90°, 0.75×360°]`（50.14%、自 3 点起）；B02 case-01 以 `f=0.62` 复现（自 138° 起）。
   任何需要**精确弧度比例**的进度环必须用分段构造（`DialArc`：N 个 `Rotate`+`C`
   分段，先铺暗弧、后覆盖亮弧，边界恰好落在 `round(frac*N)` 段）。
   这一条是关闭后用像素量测发现的，已回填修复 case-08。

**从文档了解到、但本次未触发的注意事项**（不算踩坑）：`clipBehavior` 非 NONE 需要背景装饰；
`gradientStartAngle` 必须小于 `gradientEndAngle`（文档另有 `gradientStops` 必须等长且升序的
要求——文档本身没有错，错在服务端 SWEEP 实现忽略它，见踩坑 9）。

---

## 5. 任务耗时与资源消耗

结构化指标文件：`outputs/run-20261002-220723-mimo/B01/task-metrics.json`

| 指标 | 实际值 | 单位或币种 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始时间 | 2026-10-05T15:55:31.826+08:00（UTC 07:55:31.826Z） | 含时区时间 | `requests.jsonl` 首条记录 `started_utc` |
| 任务结束时间 | 见 `task-metrics.json` 的 `ended_at` | 含时区时间 | 本文件写完时的收尾时间 |
| 任务总耗时 | 见 `task-metrics.json` 的 `elapsed_seconds` | 秒 | 上述两点之差（含文档、写脚本、看图、修改、写交付） |
| 首次可用图耗时 | 194.354（探针）/ 1252.303（首张用例图） | 秒 | 探针 `B01-probe-01` 与 `B01-c01-r1` 的结束时间减任务开始 |
| 等待用户反馈 | 0 | 秒 | 本题无用户反馈轮次 |
| 限流等待 | 0 | 秒 | 全部 31 条请求无 429，`ratelimit_remaining` 最低仍为 115 |
| 排队等待 | 未确认（null） | 秒 | 服务未提供排队指标，无从测量 |
| 已记录请求耗时之和 | 108.966（其中渲染 99.299、文档 9.667） | 秒 | `requests.jsonl` 的 `duration_ms` 求和；串行执行，但仍不等于任务墙钟 |
| 输入、输出、总 token | 未确认（null） | token | 环境未提供任何 token 计数接口 |
| 图像输入使用量 | 未确认（null） | 平台原始单位 | 同上；无法判断是否已包含在输入 token 中，故不与 token 相加 |
| 任务费用 | 未确认（null） | — | 接口无凭据、无计费头，平台未提供账单 |
| 其他可取得指标 | 服务端 `Server-Timing`：如 `render;dur=1458.7, total;dur=1464.0`；`ratelimit_remaining` | ms / 次 | 逐条记录于 `requests.jsonl`，仅作服务侧参考，不与脚本侧 `duration_ms` 混算 |

---

## 6. 设计选择、经验与未解决事项

**关键设计选择**

1. **先探针后创作**：`B01-probe-01` 用一张图同时验证 8 项不确定能力，之后 10 件才开始——
   这直接避免了在正式作品上试错。探针图已查看并被复用（矩阵写法、发光、渐变）。
2. **统一库 + 每题独立脚本**：`lib-b01.ps1` 提供带宽度校验的函数，`gen-b01-a/b.ps1`
   分别生成 01–05 与 06–10；每次生成都以 `problems = 0` 为门槛才送渲染。
3. **数据先算后画**：case-03 的里程比例、case-06 的公差带位置、case-07 的坐标换算、
   case-09 的余弦插值、case-10 的席位合计都在脚本里计算，画面与数字同源，
   因此看图时核对的是「是否与数据一致」而不是「看起来像不像」。
4. **按观看环境定媒介**：见 `portfolio.md` 的策展表；这是十件不重样的根本原因，
   而不是靠换配色。

**看图如何影响了决定**

- case-01 / 06 / 08 首版即通过，**没有为了凑迭代次数做无意义修改**。
- case-07 的三处问题全部来自看图：先发现**内容**矛盾（解说与盘面、结果栏自相矛盾），
  改完后才发现**排版**问题（行首标点），再改才到**溢出**问题。如果只看 HTTP 200，这三类都发现不了。
- case-09 的接缝只有在实际看图时才暴露；数值与坐标都无法预测这一点。

**可复用经验**

- 生成期做宽度校验（`Fit`）比渲染后再看图省一次往返；
- 蒙层类效果（进度环、公差带、分段条）尽量用「渐变停点 / 比例换算」来表达，
  这样数据与图形天然一致；
- 中文正文宁可手动断行，也不要交给自动换行；
- 看图工具的路径缓存问题要用唯一文件名规避，并把副本留档。

**未解决事项 / 环境限制**

1. `browser.preview` 在本环境不可用（浏览器会话断开），全程使用直接打开图片文件查看。
2. 读图工具对已读路径返回旧缓存字节（5 次），导致 `ite-B01-c07-v3` 为 1 次未完成迭代；
   已通过唯一命名副本与局部放大补看，**最终版本的查看结果有效**。
3. token / 图像用量 / 费用：平台未提供，全部为 `null`，原因见 `task-metrics.json.usage.unknown_fields_reason`。
4. 逐次图片查看的精确时间戳未被工具记录（读图调用不产生时间戳），因此 `iterations.jsonl`
   中的 `viewed` 记录为布尔值 + 查看证据文件，而非精确时刻；顺序可由渲染结束时间与
   `attempts/` 归档文件推断。

**结束依据**：10 件全部取得 200 响应、逐件实际打开查看、按视觉反馈完成修改并复看通过，
且 `portfolio.json.final_collection_review` 的五项最终审查（完整性 / 独立性 / 数据一致性 /
可见性 / 留痕）全部通过。没有把「已渲染 24 次」或「已有 10 件」当作完成依据。
关闭后又做了一轮跨任务像素量测，发现并修复了 case-08 的进度环（见第 4 节）。

**留痕完整性**：临时目录中的草稿、生成脚本、共享库、文档抓取、能力探针、各版本 DSL 与 PNG、
两次 400 的失败响应体、局部放大图、三个 jsonl 全部保留，未删除任何已尝试文件。
唯一的例外已如实说明：`render.ps1` 按设计把响应字节写入 `case-NN/final.png`，
所以被取代的 **case-08 首版 PNG** 随 r2 覆盖而丢失；其 DSL 已归档在
`attempts/pre-ringfix-20261006/case-08.final.snapshot`，并用该 DSL 重新渲染
（`B01-c08-r1b`，179866 B，与原响应字节数一致）存为
`attempts/pre-ringfix-20261006/case-08.v1-reconstructed.png`，已实际打开查看。
其余 9 件被取代的版本 PNG 在被覆盖前已同步复制到 `attempts/`
（`v1-reviewed/`、`v2-reviewed/`、`v3-lines/` 等），因此没有同类缺口。
无法取得的留痕材料：逐次看图的精确时间戳（原因见上第 4 条）。

---

## 开放作品集补充

- 逐件场景/内容/DSL能力/最终自检见 `portfolio.json`（10 条 `cases`），策展逻辑见 `portfolio.md`，
  本地画廊见 `gallery.html`（相对链接、无远程脚本、点击看原图）。
- **用例独立性**：10 件画幅为 900×1600 / 1920×1080 / 1080×1440 / 1200×900 / 800×1200 /
  1600×1000 / 1200×1200 / 1080×1080 / 1080×1350 / 1920×640，**10 种比例无一重复**；
  受众、媒介、信息任务与视觉隐喻各不相同；被取代的迭代版本全部留在 `attempts/`，不计入件数。
- **实际工具**：文档 GET（7）、生成脚本（3 + 1 共享库 + 1 次关闭后重生成）、渲染辅助（24 次调用）、
  读图工具（26 次查看）、System.Drawing 局部放大（1）与环形逐角度量测（2）、PNG IHDR 校验（1）、
  版本归档与规避缓存的复制、JSON 校验；
  用途与影响的作品见 `tool-usage.jsonl`（13 条）。
- **局部素材贡献**：本题 10 件全部为纯 DSL，无外部素材嵌入；唯一额外图像是 case-07 的
  2x 局部放大查看辅助图，由服务原始 PNG 裁切而来，仅用于核对小字号，不参与合成、不作为交付图，
  服务 PNG 字节保持原样。
- **指标口径**：共享的 7 条文档请求与 1 条探针请求单列于 `task-metrics.json.shared_preparation`，
  未重复计入任何用例；`case_metrics_sum_check` 给出逐项相加与总量的对账。
