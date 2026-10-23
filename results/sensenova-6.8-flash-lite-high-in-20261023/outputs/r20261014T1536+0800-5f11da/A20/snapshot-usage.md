# A20 · 二十四密集点的无重叠标注 — Snapshot 使用情况说明与踩坑记录

任务ID：A20
任务名称：二十四密集点的无重叠标注（dense annotation）
本次运行ID：r20261014T1536+0800-5f11da
完成状态：完成
结束原因：需求满足并完成视觉自检（几何审计 0 违规、144 项像素比对全过、6 个指定中心点局部视图与 1:1 整图实际打开）
输出目录：`outputs/r20261014T1536+0800-5f11da/A20/`
临时目录：`tmp/r20261014T1536+0800-5f11da/A20/`
路径基准：suite_root（本套任务总根目录，即同时包含 `tasks/`、`outputs/`、`tmp/` 的那一层；
下文所有 `outputs/…`、`tmp/…`、`tasks/…` 路径均相对该层）

遵循[PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录
环境变量；本文件中的 Markdown 本地链接相对本文件所在目录。

题目要求原文见 [TASK.md](../../../tasks/A20-dense-annotation/TASK.md)，
专用审计字段约定见
[audit-fields.json](../../../tasks/A20-dense-annotation/templates/audit-fields.json)，
输入见 [markers.json](../../../tasks/A20-dense-annotation/inputs/markers.json)。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| [annotated-map.snapshot](annotated-map.snapshot) | 完整可复现 DSL，29753 B，LF | annotated-map.png | 已交付 |
| [annotated-map.png](annotated-map.png) | 服务真实响应，148491 B，1600×1100 | annotated-map.snapshot | 已交付 |
| [label-layout.json](label-layout.json) | 原逻辑坐标、像素锚点、标签盒、引导折线、行位策略 | — | 已交付 |
| [layout-audit.json](layout-audit.json) | 距离/遮挡/穿标签/交叉/边界/高亮/看图证据 | — | 已交付 |
| [snapshot-usage.md](snapshot-usage.md) | 本文件 | — | 已交付 |
| [task-metrics.json](task-metrics.json) | 结构化指标 | — | 已交付 |

PNG sha256 `34c634b61bcff0a3d7026008f4ced5796cfc160e9f62767c29819d3c91679ed4`，
DSL sha256 `db22a1d871736acdb285bedf045ad5eb58716afe25d5eee27ebcceb655a2a2e2`，
二者逐字节一致于本次实际提交的请求体（见
[render-manifest.json](../../../tmp/r20261014T1536+0800-5f11da/A20/render-manifest.json)）。

### 1.1 需求逐项核对

| 要求 | 实际 | 结论 |
|---|---|---|
| 画布 1600×1100 | PNG IHDR 实测 (1600, 1100) | 满足 |
| 24 个点全部绘制，不删点 | 24 个 `<Container shape="CIRCLE">`；label-layout.json 24 条 label | 满足 |
| 主图区左上 (280,160)、宽 1040、高 760 | 帧矩形与 grid 均按此坐标构造 | 满足 |
| 映射不反转 | `x_px = 280 + 10.4x`，`y_px = 920 − 7.6y`（y 向下） | 满足 |
| 点圆直径 12，允许缩到 8 并在审计记录 | 24 点两两最小圆心距 30.86 px > 12 px，无需缩小，故全部保持 12 px；缩小判定与理由记于 layout-audit.json 的 `disc_policy` | 满足（允许但非必需） |
| 锚点不移动 | 标签在框外双栏，点圆严格按映射 | 满足 |
| 每点显示编号、name、value | 标签文本形如「M10 广场 93」 | 满足 |
| 标签正文 ≥ 20 | 全部标签 fontSize=20，坐标轴文字 20，标题 26/20；layout-audit.json `fonts` 逐项记录 | 满足 |
| 标签盒间距 ≥ 4 px | 实测最小欧氏距离 6.0 px（行距 38 − 盒高 32） | 满足 |
| 标签盒与非本点主体不覆盖 | 实测最小标签盒到点圆净距 199.62 px | 满足 |
| 离点 > 24 px 必须引导线 | 24 点全部 > 24 px，故 24 条引导线全部绘制；每条的实测距离与结论记于 label-layout.json | 满足 |
| 线不穿过标签文本、不连接错点 | 引导线不进入任何标签盒内部（0 处异常接触），仅终点接触自身盒边；描边压标签文字 0 处 | 满足 |
| 至多 3 处线与线交叉 | 实测 0 处（上限 3） | 满足 |
| 用弯折、分侧排序、层级减少歧义 | 全部引导线为正交三段折线（无斜线）；按锚点 x 以 774 为界分左右栏（11 + 13）；折道左栏 392−10k、右栏 1188+13k 反向单调；行 center 按锚点 y 升序贪心 | 满足 |
| 标注坐标轴、范围、单位「指数」 | x/y 各 0/20/40/60/80/100 六刻度；轴标题「x 逻辑坐标 0-100」「y 逻辑坐标 0-100」；图例「value 单位：指数」 | 满足 |
| 标注 value 最高 3 点 | M10 广场 93 / M08 中庭 91 / M23 研究所 90，按 value 降序、同值按 ID 升序；点圆与标签盒均改为橙色系 | 满足 |
| 主图完整，不另做无对应关系列表 | 24 个标签全部通过引导线连回主图内对应点圆 | 满足 |
| 放大查看指定中心 6 点及引导线，再查看整体 | 见 §3 与 [viewing-evidence.json](../../../tmp/r20261014T1536+0800-5f11da/A20/viewing-evidence.json) | 满足 |
| 附 label-layout.json / layout-audit.json | 见上表 | 满足 |
| 所有指定 PNG 为服务真实响应且有同名 .snapshot | 由 `POST /snapshot` 返回的原始字节直接落盘，未做任何后处理 | 满足 |

### 1.2 交付质量证据（不是「能渲染就算完成」）

- **几何审计**：[layout-audit.json](layout-audit.json) 判定 `通过`，0 项违规；
  距离、遮挡、穿标签、共线重合、自交、边界、高亮、字体逐项实算，容差 1e-6 px，
  保留未舍入坐标与线对。
- **渲染像素比对**：[pixel-verify.json](../../../tmp/r20261014T1536+0800-5f11da/A20/pixel-verify.json)
  直接读取交付 PNG 的实际像素与 label-layout.json 几何逐项比对 144 项，0 失败。
  这一步专门排除题目点名的「线宽造成的视觉误连」——24 个圆心像素、24 个标签底板
  内侧像素、72 段 1 px 引导线中心像素、4 处背景/主图框像素，以及 21 条
  「非 TOP3 点圆不得为橙色」的互斥性检查。
- **实际看图**：16 次图像查看事件，逐张肉眼核对，记录见
  [viewing-evidence.json](../../../tmp/r20261014T1536+0800-5f11da/A20/viewing-evidence.json)，
  每条含查看时间、具体所见与结论；未打开的视图写明原因，不以占位充数。

### 1.3 已知缺陷及其修复与复查

本次共有 2 处「渲染成功但视觉不符合要求」的缺陷被发现并修复，均经重新渲染与
重新看图确认，不在已知缺陷状态下交付：

1. **左栏引导线收尾段压 y 轴刻度数字**——初版行位等距 166+48k，有 4 行落在刻度
   文字横带内。改为按锚点 y 升序贪心分配（首行 179、行距 38、刻度带 ±17 px 回避），
   并在审计中新增 `covers_axis_text` 检查（按探针实测墨迹矩形外扩 1–2 px 的保守
   上包络），把该要求变成可机器复核项。复查：view-axis-y 显示刻度数字
   100/80/60/40 墨迹完整，引导线与刻度墨迹最小净距 10.0 px，违规 0 处。
2. **图例色样语义含混**——两个色样紧贴「x 逻辑坐标 0-100」，容易被误读为轴标签
   的一部分，且橙色的「前三」含义无文字说明。改为色样各带「普通点位」「前三点位」，
   轴标题单独占一行。复查：view-legend 与 1:1 整图确认色样与文字说明一一对应、
   无重叠、均可读。

另有 3 处审计脚本自身的误报（交叉数虚报 40、最小净距虚报 25.057、异常态不重试），
全部属检查工具缺陷而非成品缺陷，修复记录见 §4。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（POST `/snapshot`，
`Content-Type: text/plain; charset=utf-8`，请求体上限 1048576 B）
文档访问日期：2026-10-14（缓存于
`tmp/r20261014T1536+0800-5f11da/_suite/docs/`，本题未重复发起 HTTP 请求）

- AI 使用指南：https://open-snapshot.muedsa.com/ai-guide.md
  → 本地缓存 [ai-guide.md](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/ai-guide.md)
- DSL 文档：https://snapshot.muedsa.com/
  → 本地缓存 [dsl-docs.html.md.txt](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl-docs.html.md.txt)
- 字体查询：https://open-snapshot.muedsa.com/ 字体接口
  → 本地缓存 [fonts.txt](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/fonts.txt)
- OpenAPI：https://open-snapshot.muedsa.com/
  → 本地缓存 [openapi.yaml](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/openapi.yaml)

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| [ai-guide.md](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/ai-guide.md) | POST /snapshot 请求体为纯文本 DSL、`text/plain; charset=utf-8`、响应为 PNG 二进制、错误时返回 JSON（含 `code`/`message`/`diagnostic`） | `tools/suite.py` 的 `snapshot_request`；全部渲染与探针请求 |
| [guides-layout.html.md.txt](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/guides-layout.html.md.txt) | `<Positioned left top width height>` 做绝对定位；`<Stack fit="EXPAND" clipBehavior="NONE">` 作为唯一画布层 | DSL 根结构：`<Snapshot><Container><Stack><Positioned>…` |
| [guides-painting.html.md.txt](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/guides-painting.html.md.txt) | `color`、`borderRadius`、`border`、`shape="CIRCLE"`；描边可按指定矩形精确绘制 | 点圆、标签底板、1 px 引导线段、主图框、网格 |
| [guides-media-text.html.md.txt](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/guides-media-text.html.md.txt) | `<Text>` 用 `text` 属性、`fontFamily`、`fontSize`、`color`；文字不做行内测量，须自行算墨迹宽 | 24 个标签、轴刻度数字、标题与图例文字 |
| [fonts.txt](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/fonts.txt) | 中文字体族名 `Noto Sans CJK SC` | `fontFamily="Noto Sans CJK SC,Inter"` |
| [reference-parser-tags.html.md.txt](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/reference-parser-tags.html.md.txt) | 标签与属性白名单；解析器对属性值内 `<`、`&`、`(` 的限制 | `assert_dsl_wellformed()` 本地防呆 |
| [parser-text.html.md.txt](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/parser-text.html.md.txt) | 文本解析与引号/转义规则 | 标签文本生成（避免属性值内的非法字符） |
| [enums.html.md.txt](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/enums.html.md.txt) | `shape`、`border`、`clipBehavior` 等枚举取值 | `shape="CIRCLE"`、`border="3 SOLID #F59E0B"`、`clipBehavior="NONE"` |

本次实际用到的能力：绝对定位布局（Positioned）、矩形填充与圆角描边（Container）、
圆形（`shape="CIRCLE"`）、同色描边光环（`border` + `color` 组合）、纯文本排版
（Text）、网格与刻度线（细 Container）。**未使用**：外部图片、`Image` 嵌入、
裁剪、滤镜、透明度、渐变、变换/旋转。这一点是必要的——DSL 没有元素旋转，
所以全部引导线必须是轴对齐正交折线，而非任意角度直线；这一约束直接决定了
分栏阈值与折道方向的选择。

字体查询结果：中文字体取 `Noto Sans CJK SC`，拉丁与数字取 `Inter`，
组合为 `fontFamily="Noto Sans CJK SC,Inter"`。

### 2.1 本次实测确认的 DSL 约束（跨题通用）

以下均为实测结论，不是文档推测，已固化进生成脚本的本地防呆：

- `<Container>` 与 `<Positioned>` 最多一个子节点；自闭合 `<Container …/>` 可用。
- 根 `<Stack>` 不能直接作为 `<Snapshot>` 的子节点，须先包一层 `<Container>`。
- 属性值与元素内容不得含字面 `<`、`&`；属性值不得含 `(`。
- `<Rect>`、`<Circle>`、`<Line>`、`<Path>` 不存在；点圆用
  `<Container shape="CIRCLE">`。
- 文字必须写在 `text="…"` 属性里。
- `<Stack>` 按文档顺序绘制，后者在上。
- `Column` 的直接 `Row` 子节点不渲染。
- `border` 与 `color` 可同时用于 `<Container>`。
- 1 / 2 / 3 px 描边 Container 均按指定矩形精确绘制（探针 1 实测）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：[requests.jsonl](../../../tmp/r20261014T1536+0800-5f11da/A20/requests.jsonl)
迭代记录文件：[iterations.jsonl](../../../tmp/r20261014T1536+0800-5f11da/A20/iterations.jsonl)
看图证据文件：[viewing-evidence.json](../../../tmp/r20261014T1536+0800-5f11da/A20/viewing-evidence.json)

渲染请求总数：4（另有探针请求 2）
成功次数：4（渲染 2 + 探针 2）
失败次数：2（1 次 PARSE_ERROR，1 次读超时）
重试请求数：0（同 DSL 未重试；2 次失败分别由 DSL 修改与新渲染取代）
DSL 版本数：4
实际图片查看次数：16
完整视觉迭代数：2
未完成视觉迭代数：0
其他接口查询：本题未发起；文档、字体查询在 `_suite` 共享准备中完成并缓存复用

初次生成和查看计为基线，不计为改进迭代。

| 请求ID / 迭代ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| req-a20-probe-metrics-bff114 / it-a20-001 | probe-metrics.snapshot | 14:40:26 → 14:40:29（3.33 s） | 200 / image/png | responses/probe-metrics.png | 14:41 已查看：1/2/3 px 描边按矩形精确绘制、`shape="CIRCLE"` 与 `border` 组合可用 |
| req-a20-probe2-text-2996af / it-a20-002 | probe2-text.snapshot | 16:04:12 → 16:04:17（4.38 s） | 200 / image/png | responses/req-a20-probe2-text-2996af.png | 16:05 已查看：数字墨迹宽 0→10、20/40/60/80→22、100→32；盒内偏移 dx=+2、dy=+5 |
| req-a20-annotated-map-2c94fc / it-a20-004 | annotated-map.attempt-01-buggy.snapshot | 开始时间未记录 → 16:51:00（结束时间取自文件 mtime） | 未记录 / — | responses/req-a20-annotated-map-2c94fc.error.json | 无图（PARSE_ERROR）：属性值无效 [color]，元素 `<Text>`，offset 20070 / line 154 / column 124 |
| req-a20-annotated-map-b0acea / it-a20-006 | annotated-map.snapshot（v3） | 16:59:56 → 16:59:59（3.27 s） | 200 / image/png | responses/annotated-map.render-01.png | 17:05 已查看 1:1 整图：主体合格，但发现左栏引导线收尾段压 y 轴刻度数字 |
| req-a20-annotated-map-a4d103 / it-a20-009 | annotated-map.snapshot（v4） | 17:31:13 → 未取得响应 | 未记录 / — | responses/req-a20-annotated-map-a4d103.png（0 字节） | 无图（读超时 300 s） |
| req-a20-annotated-map-a2f4e5 / it-a20-010 | annotated-map.snapshot（v4） | 17:47:28 → 17:47:45（17.20 s） | 200 / image/png | responses/annotated-map.render-02.png | 17:48 已查看 1:1 整图：图例语义已修正，主体与 v3 一致，判定交付 |

时间均为 Asia/Shanghai (UTC+08:00)。

### 3.1 完整视觉迭代

| 迭代ID | 类型 | 父版本 | 依据已查看图片发现的问题 | 改动 | 重新查看与比较结果 |
|---|---|---|---|---|---|
| it-a20-006 | visual | v3 | view-axis-y 与 1:1 整图：左栏引导线收尾段压 y 轴刻度数字 | 行位由等距改为锚点 y 升序贪心避让刻度文字带；审计新增 `covers_axis_text` | 重渲 render-01 后 17:36 复查 view-axis-y：刻度墨迹完整，最小净距 10.0 px，违规 0 处 |
| it-a20-010 | visual | v4 | view-legend：色样被误读为轴标签的一部分，橙色含义无文字说明 | 色样各带「普通点位」「前三点位」，轴标题单独占一行 | 重渲 render-02 后 17:48 复查 1:1 整图与 view-legend：色样与文字说明一一对应、无重叠、均可读；144 项像素比对全过 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| it-a20-004 / syntax-fix / v3 | 服务端 PARSE_ERROR「属性值无效 [color]，元素 `<Text>`」 | Python 条件表达式优先级：非高亮分支把 `(PLATE, PLATE_BORDER, TEXT)` 元组塞进 `color` 属性。由服务端 `diagnostic.attributeName/elementName/position` 定位到 line 154 | 改为显式 `if/else`；在 `build_dsl` 末尾加 `assert_dsl_wellformed()` 拦截属性值内的 `<`、`&`、`(` 与 CRLF | 后续渲染均 200；本地防呆已覆盖，未再触发 | dsl/annotated-map.attempt-01-buggy.snapshot、responses/req-a20-annotated-map-2c94fc.error.json |
| it-a20-005 / retry / v3 | 请求已发出、失败响应已落盘，但日志写入前脚本抛错，留下无日志条目的失败响应 | `suite.log_request` → `task_dirs` → `run_id()` 需要 `SNAPSHOT_RUN_ID`，未设置即抛 `RuntimeError` | 用 a20_log_orphan.py 补记一条如实记录：可得字段照填，`http_status`/`started_at`/`elapsed_ms` 置 null 并写明原因；失败响应改名 `.error.json` 保留字节；缺陷 DSL 改名保留 | 该次尝试在 requests.jsonl 中可追溯，字节未改动 | responses/req-a20-annotated-map-2c94fc.error.json |
| it-a20-006 / visual / v3 | 引导线收尾段压 y 轴刻度数字 | 等距行位 166+48k 有 4 行落入刻度文字横带；模型审计原先不检查坐标轴文字 | 行位贪心避让；审计新增 `covers_axis_text`（刻度墨迹矩形按探针实测外扩 1–2 px） | 违规 0 处，最小净距 10.0 px；view-axis-y 复查通过 | tmp/…/A20/preview/view-axis-y.png |
| it-a20-007 / audit-fix / v3 | 审计自报 40 处引导线交叉（上限 3），实为 0 处 | `seg_relation` 的 `u` 参数叉积顺序写反：写成 `((b−a)×(c−a))/den`，正确应为 `((c−a)×(b−a))/den`，符号相反把不相交判成交叉。以 a=(0,0)、b=(0,10)、c=(−5,5)、d=(5,5) 手工验算确认 | 修正为 `u = cross(a, c, b) / den`；新增 `primitives_selftest()` 固化 8 条基元断言作为回归用例 | 交叉数 40 → 0；自检 `all passed`，结果记入 layout-audit.json | tmp/…/A20/layout_model.json |
| it-a20-008 / audit-fix / v3 | 最小净距虚报为 25.057 px | `seg_rect_min_dist` 只量两个端点到矩形的距离，漏检「线段从矩形正上方扫过」（此时最近点在矩形上边）：行 293 与刻度「80」墨迹真实最近距 11 px，被报成 48.26 px | 凸矩形与不相交线段的最近点对必在「端点—矩形上某点」或「顶点—线段上某点」，故对两个端点与四个顶点各求一次取最小值 | 最小净距 25.057 → 10.0 px；违规仍为 0；该用例已进自检 | 同上 |
| it-a20-009 / retry / v4 | 图例修改后重渲，第 1 次请求 300 s 读超时，且只尝试一次就终止 | `suite.snapshot_request` 只对 `URLError` 自行重试，`socket.timeout` 以 `TimeoutError` 抛出；外层判断 `status != 0` 把异常态 `None` 当成「不该重试」 | 改为 `status not in (0, None)` 才视为定论；异常路径补记本地墙钟耗时与 `http_status_null_reason` / `ended_at_null_reason`；空响应文件按日志的 response_path 原样保留 | 重试逻辑已可用；该次失败被后续成功请求取代，无需恢复 | responses/req-a20-annotated-map-a4d103.png（0 字节） |
| it-a20-010 / visual / v4 | 图例色样语义含混 | view-legend 实际查看：色样紧贴「x 逻辑坐标 0-100」，易被误读为轴标签的一部分；橙色「前三」含义只能靠底部 TOP-3 行反推 | 色样各带文字说明，轴标题单独占一行 | 重渲 render-02 后复查通过；144 项像素比对全过 | preview/view-legend.png、outputs/…/A20/annotated-map.png |
| — / 留档操作 / v4 | 误把探针响应存成了 `annotated-map.render-01.png` | 取「最后一次 200 响应」时误匹配到探针请求 | 改名回如实的 `probe-metrics.png`，再把正确的 `req-a20-annotated-map-b0acea.png` 复制为 `annotated-map.render-01.png`；两个文件哈希与内容均核对一致 | 留档文件名与实际内容一致 | responses/probe-metrics.png、responses/annotated-map.render-01.png |

本次未遇到已确认的平台限制或环境阻塞。上述 3 处审计脚本缺陷与 1 处重试缺陷，
若未通过手工验算发现，会把「通过」误报为「不通过」或反之——这也是把
`primitives_selftest()` 加进审计主流程的原因：审计工具本身的正确性同样需要有回归证据。

## 5. 任务耗时与请求统计

结构化指标文件：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始时间 | 2026-10-19T14:22:25+08:00 | ISO8601 | `_suite/events.jsonl` 中 A19 的 `task_completed` 时刻 |
| 任务结束时间 | 2026-10-19T18:0x+08:00（写入 task-metrics.json 时） | ISO8601 | 生成脚本 `datetime.now().astimezone()` |
| 任务总耗时 | 13645.0 | 秒 | 墙钟时间，含布局计算、审计、看图与等待服务 |
| 首次可用图耗时 | 1084.0 | 秒 | 从任务开始到首次取得且能打开的有效图（度量探针 PNG） |
| 首次交付件图耗时 | 9454.0 | 秒 | 从任务开始到 annotated-map.png 首次成功渲染 |
| 等待用户反馈 | 0 | 秒 | 单轮任务，无用户反馈等待 |
| 限流等待 | 0 | 秒 | requests.jsonl 中无 429 响应，未触发限流退避 |
| 排队等待 | null | — | 服务未返回排队信息，无 Server-Timing/排队字段可测 |
| 服务侧挂起 | 1 次 | 次 | req-a20-annotated-map-a4d103 读超时 300 s；已含在墙钟耗时内，非限流等待 |
| 已记录请求耗时之和 | 28.172 | 秒 | 仅统计有耗时记录的 4 次请求；与墙钟耗时不可混同 |
| 成功、失败、重试请求 | 4 / 2 / 0 | 次 | requests.jsonl（共 6 条：探针 2 + 渲染 4） |
| 实际看图与完整视觉迭代 | 16 / 2 | 次 | iterations.jsonl 与 viewing-evidence.json |
| 像素比对 | 144 项 / 0 失败 | 项 | pixel-verify.json |

服务端未返回 `Server-Timing`，所有耗时均为本地墙钟 `time.monotonic`（含网络往返），
已在 task-metrics.json 中注明 `server_timing_available: false`。

## 6. 设计选择、经验与未解决事项

### 6.1 关键设计选择

- **分栏阈值取 774 而不是画布中线 800**。锚点 x < 774 排左栏（11 个），
  ≥ 774 排右栏（13 个）。该阈值同时满足「引导线首段不得穿过其他点圆盘」，
  已逐点验证。取中线会让 M08 这类紧邻中线的点被切到与折道方向冲突的一侧。
- **折道反向单调**。左栏 lane = 392 − 10k（随行号递减），右栏 lane = 1188 + 13k
  （递增）。配合「行 center 随锚点 y 升序」「行在自有点上方」两条，可以在
  几何上排除全部线-线交叉情形：i < j 时 `cy_j` 高于折道 i 的上端 `cy_i`，
  y 条件不成立；j < i 时折道 i 的 x 不落入水平段 j 的 x 区间，x 条件不成立；
  收尾段因行升序直接排除。左右栏横向范围不相交（左栏最大 x = 762.8 <
  右栏最小 x = 785.2），跨栏也不会相交。审计仍按题目口径逐线对实算，
  实测 0 处，图内也声明「引导线交叉 0 处（上限 3 处）」。
- **引导线用 1 px 细 Container 拼正交折线**，而非试图画斜线或曲线：DSL 无元素
  旋转、无 `<Line>`/`<Path>`，正交三段折线是既能精确控制又能被审计验证的形式。
- **行位贪心避让刻度文字带，但保持行升序**。这是本题最实质的取舍：等距行位最
  简洁，却会把左栏收尾段压在 y 轴刻度数字上；改等距为贪心（首行 179、行距 38、
  刻度带 ±17 px 回避）后仍满足「行升序」，因此不交叉证明不变。行距 38 使盒净距
  6 px，仍满足 ≥ 4 px 且留出视觉呼吸。
- **点圆保持 12 px 不缩小**。24 点两两最小圆心距 30.86 px > 12 px，缩到 8 px
  不会带来任何遮挡改善，只会削弱点可读性。题目允许缩小并记录审计，此处如实
  记录「允许但非必需，故未缩小」。
- **标签盒与底板像素严格对齐**。探针实测底板按指定矩形精确渲染、盒内文字墨迹
  偏移 +2/+5，因此标签盒就取底板矩形的像素矩形，标签几何与渲染逐像素一致，
  审计不必再做墨迹测量；盒内留白 6/8/5/8 px。
- **图例色样必须自带文字说明**。这是本次看图发现的真实缺陷：仅靠底部 TOP-3 行
  反推颜色含义，读图者会卡住。修正后蓝「普通点位」、橙「前三点位」各自成句。

### 6.2 可复用经验

1. **审计脚本本身也需要自检**。本次 3 处误报全部来自审计工具的几何基元（叉积
   符号、线段到矩形距离、异常态判定），而成品布局其实是正确的。任何「几何自检
   通过」的结论，其可信度上限取决于检查工具本身的可信度；`primitives_selftest()`
   用 8 条固定断言把这一点变成可回归的证据。
2. **区分「模型自洽」与「服务真画出来了」**。审计只能证明 label-layout.json 内部
   一致；pixel-verify 直接读交付 PNG 的像素，才能证明服务端按模型渲染。
   144 项比对成本极低，却是排除「线宽造成的视觉误连」这类问题的唯一硬证据。
3. **本地先拦 DSL 语法坑，别拿请求次数试错**。`<`、`&`、`(` 出现在属性值里会
   直接 PARSE_ERROR，而服务端只给 offset/line/column，定位成本高。
   `assert_dsl_wellformed()` 在提交前就抛本地异常，同时拦下 CRLF 与请求体超限。
   本次仅因一次未防住的元组拼接浪费了一个渲染请求。
4. **例外要自己接住**。`suite.snapshot_request` 只对 `URLError` 自行重试，
   `socket.timeout` 会以 `TimeoutError` 抛出；外层重试必须把 `None` 也算成
   「未定论」，否则一次挂起就终止整个构建。
5. **失败留痕要如实区分「拿不到」与「是 0」**。超时的请求没有状态码和结束时间，
   这些字段置 null 并写明原因，而不是填 0 或估计值。
6. **看图顺序按最可能出问题处排**：双栏标签栏 → 指定中心点局部 → 坐标轴刻度
   → 图例 → 整图。本次两处视觉缺陷（压刻度数字、图例语义）都是在这个顺序下
   被发现的，而不是靠整体扫读。

### 6.3 未解决事项

| 事项 | 影响 | 恢复办法 |
|---|---|---|
| A20 未单独记录 `task_started` 事件，起点取自 A19 完成的 `task_completed` | 墙钟耗时可能略小于真实工作时长（起点偏晚） | 后续任务补记 `task_started` 事件 |
| `req-a20-annotated-map-a4d103.png` 为 0 字节空文件 | 无可查看内容 | 无需恢复；该次请求已被后续成功请求取代，日志已记录超时原因 |
| `req-a20-annotated-map-2c94fc` 的 `http_status` / `started_at` / `elapsed_ms` 为 null | 该次请求的耗时与状态码不可追溯 | 无需恢复；原因已写在日志的 `*_null_reason` 字段中 |
| 400 px 缩略（0.5x）下 20 px 标签文字不可读 | 缩略视图不能用于核对文字 | 可读性一律按 1:1 视图核对；已在 viewing-evidence.json 注明 |

### 6.4 留痕与清理说明

临时目录中的全部草稿、探针 DSL、4 个 DSL 版本、6 次请求的原始响应（含 1 个
0 字节超时响应与 1 个 JSON 错误响应）、14 张裁切视图、布局模型、审计与像素
比对结果、看图证据均已保留，未清理、未覆盖、未删除失败尝试。
本次仅做了两处如实的改名（探针响应曾被误存成 `annotated-map.render-01.png`，
已改名回 `probe-metrics.png`；同字节内容已在两个路径下核对一致），以及一次
补记孤儿日志，均属纠正错误命名与补齐缺失记录，没有丢弃任何尝试。
日志持续追加；`requests.jsonl` 与 `iterations.jsonl` 均只增不改。

总任务根 `.gitignore` 已按缓存忽略模板创建并合并，忽略
`__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/` 等运行时缓存，
未忽略 `tmp/`、`outputs/` 或任何过程证据（总报告另有汇总说明）。

---

**结束依据**：24 个点与 24 条引导线全部绘制并逐一对应；几何审计判定通过且
0 违规；144 项渲染像素比对 0 失败；6 个指定中心点各自放大视图、6 点同框视图
与 1:1 整图均实际打开核对；2 处已知视觉缺陷已修复并复查；所有过程与失败尝试
均已留痕。未以任何请求次数或耗时目标作为完成依据。
