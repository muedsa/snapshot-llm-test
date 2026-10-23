# A07 Snapshot 使用情况说明与踩坑记录

任务ID：A07
任务名称：三线换乘图与路线核验
本次运行ID：r20261014T1536+0800-5f11da
完成状态：完成
结束原因：需求满足并完成视觉自检与像素校验
输出目录：outputs/r20261014T1536+0800-5f11da/A07/
临时目录：tmp/r20261014T1536+0800-5f11da/A07/
路径基准：suite_root（本目录下的相对路径即相对本题输出根）

遵循[PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录
环境变量。Markdown本地链接相对当前文档。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| [network-map.snapshot](network-map.snapshot) | 全网示意图的完整可复现DSL（25645 B，147 个 Positioned） | [network-map.png](network-map.png) | 完成 |
| [network-map.png](network-map.png) | 服务返回的最终图片，1600x1000，279814 B | [network-map.snapshot](network-map.snapshot) | 完成 |
| [travel-card.snapshot](travel-card.snapshot) | 旅行卡的完整可复现DSL（28791 B，149 个 Positioned） | [travel-card.png](travel-card.png) | 完成 |
| [travel-card.png](travel-card.png) | 服务返回的最终图片，720x1280，234625 B | [travel-card.snapshot](travel-card.snapshot) | 完成 |
| [routes.json](routes.json) | 3 组查询的路线核验（52161 B） | 无（数据交付） | 完成 |

### 题目要求逐项核对

| 要求 | 结果 | 依据 |
|---|---|---|
| 使用 inputs/network.json 的 3 线 / 16 站 / 16 条相邻站边 | 满足 | routes.json 的 `input` 与 `accessibility_checks[2]`；像素校验 C2 18 段覆盖率 100% |
| 相邻站按线路顺序连接、双向、等权 | 满足 | `routes.json.routing` 的 `bidirectional=true`、`edge_cost_uniform=1`；审计 A8 由 inputs 独立重建图后重算 |
| 共享站为换乘站 | 满足 | S04（R,B）、S05（R,G）、S08（B,G）；C6 16/16 外圈为换乘深圈 |
| 普通交叉不得读成换乘 | 满足 | `false_crossing_count = 0`；像素校验 C4 三条线路像素互不接触（膨胀 2px 后接触像素 0） |
| 颜色 + 线路字母双重区分，不只靠红绿 | 满足 | 3 条线各有 R/B/G 字母角标（C9 环上取样 ≥6/8 为本线色）+ 颜色 |
| 16 个站名与站 ID 全部标注 | 满足 | C7 16 站 × 2 行文本区全部有墨迹且无线路色侵入 |
| 折线只用 45°/90° 转角 | 满足 | `drawn_angles_deg = [0, 45, 90]`；C3 三条 45° 段斜率 -1.0000（期望 -1.0），垂直厚度 14..14 px |
| 明确声明为非地理示意图 | 满足 | `geometry.is_geographic = false`，图中另有「示意 · 不按比例」标注 |
| accessible=false 的站可乘车途经但不可做起终点/换乘站；不得删线 | 满足 | `accessibility`（16 站逐项 endpoint/transfer/ride_through）+ `accessibility_checks` 3 项，全部计算得出；审计 A9/A10 |
| 逐站标注无障碍状态并附图例 | 满足 | 青核 = 有设施、灰核 = 无设施，图例含该说明；C5 16/16 核色一致 |
| 3 组查询按 (站间边数, 换乘数) 字典序求解 | 满足 | Q1 6边/1换乘、Q2 6边/1换乘、Q3 4边/1换乘；审计 A8 用独立实现从 inputs 重算，站序/边数/换乘数/每条边所属线路全部一致 |
| 旅行卡展示 3 条普通旅程、能否无障碍、不可时的最短无障碍替代 | 满足 | Q2 另给出 6边/2换乘的无障碍替代；D9 判定标 Q1/Q3 青色、Q2 红色 |
| 换乘 = 改换线路，首次上车不计 | 满足 | `objective_note` 与页脚说明 |
| 不把站数当区间数 | 满足 | 每条路线含 `station_count`、`intervals`、`drawn_segments_total` 三个不同量；审计 A8 校验 站数-1 == 边数 |
| 两张图共用视觉系统但排版不同 | 满足 | 共用 `a07_style.py`（同背景/面板/线宽/圆点/色板）；示意图为「地图面板 + 右侧图例」横向布局，旅行卡为纵向卡片分区 |
| 图上标注 ≥20、手机正文 ≥20 | 满足 | C10 最小 17px 仅用于图例补充说明，站标签两行均 20px；D2 旅行卡 61 个文本最小 20px |
| 附 routes.json | 满足 | 见上表 |

### 质量证据（不是"能渲染"，是可复算的检查）

- **示意图像素校验 C1..C10 = 10/10**，报告 [inspect-map.json](../../../tmp/r20261014T1536+0800-5f11da/A07/inspect-map.json)。
  检查器只从 `model.json` 与最终 PNG 重新推导期望，不引用绘制脚本的中间产物；
  若版面算错，检查会直接失败而不是被断言通过。
- **旅行卡像素校验 D1..D10 = 10/10**，报告 [inspect-card.json](../../../tmp/r20261014T1536+0800-5f11da/A07/inspect-card.json)。
  检查器自行重算 4 条线路条的像素位置（`strip_geometry`），因此版面算错也会失败。
- **routes.json 审计 A0..A10 = 14/14**，报告 [audit-routes.json](../../../tmp/r20261014T1536+0800-5f11da/A07/audit-routes.json)。
  其中 A8 完全绕开 `model.json`，直接对
  `tasks/A07-transit-topology/inputs/network.json` 用另一套实现跑字典序最短路径
  （状态 = (站, 当前线路)，堆 + 前驱回溯），再与 routes.json 声称的站序、边数、
  换乘数以及**每一条边所属线路**逐一比对，全部一致。
- 已知缺陷：无遗留。所有看图发现的缺陷（共 5 处）均已修复并重新渲染、重新看图复核，
  详见第 4 节。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com （以 run-config.json 为准）
文档版本或访问日期：AI 使用指南与 DSL 文档在本次运行早期已实际取得并缓存于
`tmp/r20261014T1536+0800-5f11da/_suite/`；A07 未新增文档 HTTP 请求，仅复用已取结果。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | POST /snapshot、UTF-8 DSL 请求体、成功返回 image/png、错误返回 JSON `{code,message,requestId,position}` | `a07_io.submit()` |
| https://snapshot.muedsa.com/ | 类 DOM DSL：Snapshot/Container/Stack/Positioned/Text/Border 等；无 Line/Path/Polyline/Circle/Shape/SizedBox | 全部 11 个 DSL 版本 |
| 同上 | `Positioned` + `Container transform=mat(θ)` + `transformAlignment="TOP_LEFT"` 绘制真实 45° 线段 | `a07_style.diag()` |
| 同上 | 布尔属性必须写显式字符串；颜色支持 #RGB/#RRGGBB/CSS 名/rgb()/rgba()/hsl() | `a07_style` 全部样式函数 |
| 同上 | `Stack` 绘制次序 = 后声明者在上 | 线路条与地图的层叠顺序 |
| 同上 | 字体 `Noto Sans CJK SC` 可渲染中文与 ①②③ → − ↑ ↓ 「」＝ ≥ × · — ≠ | 全部文本 |

本次实际使用的能力：布局（Positioned 绝对定位、Stack 层叠）、文本（字号/粗体/字族）、
颜色与边框（`border="宽度 样式 颜色"`、borderRadius）、形状（圆角矩形实现线、圆点、
角标、胶囊标签）、旋转（`Container transform=mat(θ)` 实现 45° 线段）、
画布（`Snapshot background=` + 根 Container 定尺寸）。
**未使用**外部图片、Image 嵌入、滤镜、裁剪路径填充。字体未在本次新查询，沿用已确认的
`Noto Sans CJK SC`（`Noto Sans SC` 未安装，不可用）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：[requests.jsonl](../../../tmp/r20261014T1536+0800-5f11da/A07/requests.jsonl)
迭代记录文件：[iterations.jsonl](../../../tmp/r20261014T1536+0800-5f11da/A07/iterations.jsonl)
渲染请求总数：12
成功次数：11
失败次数：1
重试请求数：1（是总请求的子集：req-a07-probe1-clip → req-a07-probe1-clip-1）
DSL版本数：11（network-map 9 个：probe1-clip / probe2-rot / probe3-center /
probe4-align / probe5-order / v1 / v2 / v3 / v4；travel-card 2 个：v1 / v2）
实际图片查看次数：28（含 21 张 2× 局部放大图）
完整视觉迭代数：4（map v1→v2、v2→v3、v3→v4、card v1→v2）
未完成视觉迭代数：0
其他接口查询：无（文档与字体查询在 A07 之前已完成并复用，不重复计入）

初次生成和查看计为基线，不计为改进迭代。5 个探针为方案探索（alternative），
2 次脚本语法修复未消耗服务请求。

| 请求ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| req-a07-probe1-clip | tmp/…/A07/req-req-a07-probe1-clip.snapshot | 07:56:09→07:56:11，1.656s | 400 / application/json | tmp/…/A07/responses/req-a07-probe1-clip.body | 未取得图片（PARSE_ERROR） |
| req-a07-probe1-clip-1 | tmp/…/A07/req-req-a07-probe1-clip-1.snapshot | 07:57:32→07:57:34，2.515s | 200 / image/png | tmp/…/A07/responses/req-a07-probe1-clip-1.body | 已查看：ClipPath 方案的 45° 接头不齐 |
| req-a07-probe2-rot | tmp/…/A07/req-req-a07-probe2-rot.snapshot | 08:03:00→08:03:03，2.360s | 200 / image/png | tmp/…/A07/responses/req-a07-probe2-rot.body | 已查看：transform 方案可行，斜率 -1.0000、厚度 14px |
| req-a07-probe3-center | tmp/…/A07/req-req-a07-probe3-center.snapshot | 08:26:33→08:26:36，3.047s | 200 / image/png | tmp/…/A07/responses/req-a07-probe3-center.body | 已查看：CENTER 写法全部错位 |
| req-a07-probe4-align | tmp/…/A07/req-req-a07-probe4-align.snapshot | 08:28:45→08:28:47，2.000s | 200 / image/png | tmp/…/A07/responses/req-a07-probe4-align.body | 已查看：<Transform matrix=> 静默无渲染 |
| req-a07-probe5-order | tmp/…/A07/req-req-a07-probe5-order.snapshot | 08:39:02→08:39:05，2.797s | 200 / image/png | tmp/…/A07/responses/req-a07-probe5-order.body | 已查看：后声明者在上，确认绘制次序 |
| req-a07-map-v1 | tmp/…/A07/req-req-a07-map-v1.snapshot | 08:53:12→08:53:20，7.406s | 200 / image/png | outputs/…/A07/network-map.png | 已查看（1 全图 + 4 局部）：2 处裁切、2 处压字、图例行距紧 |
| req-a07-map-v2 | tmp/…/A07/req-req-a07-map-v2.snapshot | 09:05:01→09:05:04，3.750s | 200 / image/png | outputs/…/A07/network-map.png | 已查看（5 局部）：裁切与压字消失 |
| req-a07-map-v3 | tmp/…/A07/req-req-a07-map-v3.snapshot | 09:07:00→09:07:02，2.812s | 200 / image/png | outputs/…/A07/network-map.png | 已查看（4 局部）：图例行距正常 |
| req-a07-map-v4 | tmp/…/A07/req-req-a07-map-v4.snapshot | 09:18:48→09:18:51，3.531s | 200 / image/png | outputs/…/A07/network-map.png | 已查看：站标签两行 20px，无新冲突 |
| req-a07-card-v1 | tmp/…/A07/req-req-a07-card-v1.snapshot | 10:03:59→10:04:08，8.406s | 200 / image/png | outputs/…/A07/travel-card.png | 已查看：3 处缺陷（站名越界、角标压点、标签撞角标） |
| req-a07-card-v2 | tmp/…/A07/req-req-a07-card-v2.snapshot | 10:09:44→10:09:47，2.844s | 200 / image/png | outputs/…/A07/travel-card.png | 已查看（1 全图 + 6 局部）：3 处缺陷全部消失 |

查看时间戳未在本地单独计时，故 `iterations.jsonl` 中 `viewed_at` 记为 null，
改记 `viewed_at_window` 上下界（图片在该请求返回后、下一请求开始前被查看）。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| iter-a07-01 / 语法修复 / — | 服务返回 400 PARSE_ERROR：`Attr [color] unsupported CSS color [24]` position 238 | 探针脚本把布尔属性写成字符串真值，导致某元素 color 被替换成字号数字 "24"。确认依据：错误响应的 `position` 与 `near` 字段直接定位到该行 | 颜色改显式字符串，布尔属性统一 `"true"`/`"false"` | 重发后 200 image/png | responses/req-a07-probe1-clip.body |
| iter-a07-02 / 方案探索 / — | ClipPath 承载 45° 线段时端点与相邻正交段接头不齐 | 裁剪区内填充无法保证斜向带的恒定垂直宽度（像素测量） | 放弃 ClipPath 方案 | 转 probe2 | preview/probe1-clip.png |
| iter-a07-03 / 方案探索 / iter-a07-02 | 需要确定可用的 45° 图元 | 实测 `Positioned + Container transform=mat(θ) + TOP_LEFT`：斜率 -1.0000，垂直厚度恒定 14px = 线宽 | 定位原点改为 `p1 + (sinθ·lw/2, -cosθ·lw/2)`，补偿圆头端帽外伸半个线宽 | 45° 段可用 | dsl/network-map.probe2-rot.snapshot |
| iter-a07-04 / 方案探索 / iter-a07-03 | `transformAlignment="CENTER"` 导致线段错位 | 显式尺寸 Positioned + CENTER 时 Container 撑满 Positioned 再整体旋转；无尺寸 Positioned + CENTER 时整体沿法线偏移约 160px | 统一 TOP_LEFT | CENTER 三种写法均错位，TOP_LEFT 精确 | dsl/network-map.probe3-center.snapshot |
| iter-a07-05 / 方案探索 / iter-a07-04 | `<Transform matrix=...>` 完全不渲染 | 服务对该写法静默丢弃内容（同图其他元素正常） | 排除该写法 | 仅 Positioned+Container+TOP_LEFT 可用 | dsl/network-map.probe4-align.snapshot |
| iter-a07-06 / 方案探索 / iter-a07-05 | 需确认层叠规则 | Stack 中后声明子元素在上；圆点必须后画才能压住线段端帽 | 确定成品次序：线路段 → 字母角标 → 站圆点 → 标签 | 次序颠倒时圆点被盖住一半、接头有缺口 | dsl/network-map.probe5-order.snapshot |
| iter-a07-08 / 视觉 / iter-a07-07 | Q1 与 S13 查询角标被面板裁掉一角；S16、S07 角标与站标签压字 | 看图发现（2× 局部放大） | 引入 `Q_TAG` 位移表把角标改到内侧，`LABEL_SIDE` 逐站指定标签方向与微调量 | 裁切与压字消失；C8 38 个区块两两不重叠 | dsl/network-map.v2.snapshot |
| iter-a07-09 / 视觉 / iter-a07-08 | 右侧图例说明行距过紧，末行贴近框下沿 | 看图发现 | 加宽行距、末行上移 | 三行说明彼此分离、不贴框 | dsl/network-map.v3.snapshot |
| iter-a07-10 / 视觉 / iter-a07-09 | 站标签第二行用了 17px，低于题目要求的 20 | 对照题面「图上标注不小于 20」 | 两行统一 20px，17px 仅留给图例补充说明 | C10 通过；标签变宽但未与线路或相邻标签相交 | dsl/network-map.v4.snapshot |
| iter-a07-11 / 语法修复 / — | `TypeError: sequence item 5: expected str instance, tuple found` | `a07_style.pill` 返回 (片段,宽,高) 三元组，被整个 append | 新增 `P()` 只取 `[0]`，替换 4 处调用点 | 脚本正常运行 | gen/a07_build_card.py |
| iter-a07-12 / 语法修复 / iter-a07-11 | `KeyError: 'S02'` | `line_at()` 只映射每段首站，中间站缺描边色 | 改为遍历每段全部站 | 9 条线路条全部生成 | gen/a07_build_card.py |
| iter-a07-14 / 视觉 / iter-a07-13 | 3 处缺陷：首末站名越出卡片被裁；Q2 无障碍条的 R 角标压在 S06 圆点上；换乘标签与相邻 B 角标水平距约 4px 且有 4px 垂直重叠 | 看图发现。角标问题根因：段含偶数个区间时，段中点索引 `(i0+i1)/2` 恰为整数即落在某站上 | 线路条两端内缩 42px；段中点为整站索引时右移半格；色条下移 y0+58、换乘标签上移 y0+1..38 | 3 处全部消失；2× 局部放大复核；D1..D10 通过 | dsl/travel-card.v2.snapshot |
| iter-a07-15 / 校验修复 / — | 像素校验 C3 初判 FAIL：三条 45° 段斜率均 -0.9550（期望 -1.0），三条完全一致 | 测量假象而非几何错误。排除掩膜用 r=24 站标记圆盘，45° 带在段两端被切掉的是**下方那一半**，两端列中心整体上移而中段不变，逐列拟合斜率被压小约 0.045 | 只保留整列都落在圆盘之外的中间段列（\|x - 端点x\| ≥ 站标记半径 + 2） | 三条斜率均 -1.0000，垂直厚度 14..14px，C3 转 PASS，10/10 | inspect-map.json |
| iter-a07-16 / 校验修复 / — | 像素校验 D5 初判 FAIL，两个不同原因 | (1) 26px 角标在 borderRadius=8 时 r=12 已落在圆角区之外，8 点只命中 4 点；(2)「角标压圆点」原用段跨度 0.32 的任意比例判断，误杀本应右移半格的角标 | (1) 改 26x26 盒内本线色填充 ≥350px 且中心 10x10 白字 ≥15px；(2) 改真实几何 min\|bx-xk\| ≥ 30（= 角标半径 13 + 换乘圆点半径 15 + 2 余量） | 9 个角标全部通过，D5 转 PASS，10/10 | inspect-card.json |
| iter-a07-17 / 校验修复 / — | `_polyline()` 折线回溯只走完 n-1 段，导致 4 条路线段的 `drawn_segments` 算成 0 | 一条 n 段折线有 n+1 个顶点，循环写了 `range(n-1)` | 改为 `range(n)` | 边数与折线段数关系正确（如 Q1 的 B 段 3 个站间边由 5 段折线画出） | gen/a07_routes.py |
| iter-a07-18 / 校验修复 / — | 审计 A8 回溯站序只得到终点相邻一站 | `par` 的值是 4 元组 `(边数,换乘数,前站,前线路)`，而循环把 4 元组当作 2 元组键去查 `par`，第二次查找必然失败 | 单独维护 `prev` 变量，用 `prev[2]`/`prev[3]` 继续回溯 | 3 查询 × 2 模式站序完全一致，14/14 | audit-routes.json |

渲染成功但视觉不符合要求的问题共 5 处（map v1 的 2+2、card v1 的 3，其中 map v1 的两处裁切
与两处压字记为一处迭代），已全部修复并重新渲染复核。
从文档了解到、本次未触发的注意事项：服务对未知标签/属性返回 400 PARSE_ERROR，
本次仅 probe1 触发一次，未再遇到其他解析错误。

## 5. 任务耗时与请求统计

结构化指标文件：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-15T07:40:54+08:00 → 2026-10-15T11:07:00+08:00 | ISO8601 | A06 结束后接力开始 |
| 任务总耗时 | 12366 | 秒 | 整个任务的墙钟时间（含思考、看图、写报告） |
| 首次可用图耗时 | 1000 | 秒 | 07:40:54 → 07:57:34（probe1-clip-1，首个 200 且可打开） |
| 等待用户反馈 | 0 | 秒 | 单轮任务，无用户反馈等待 |
| 限流等待 | 0 | 秒 | 12 次请求 `ratelimit_remaining` 恒为 119，未遇到 429 |
| 排队等待 | null | 秒 | 服务端未返回排队时长，不可测；`server_timing` 仅含 render/total |
| 已记录请求耗时之和 | 43.124 | 秒 | requests.jsonl 的 `elapsed_ms` 之和；不含本地计算与看图时间 |
| 成功、失败、重试请求 | 11、1、1 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 28、4 | 次 | iterations.jsonl 与实际图像查看记录 |

`elapsed_seconds`（12366 s）远大于请求耗时之和（43.124 s），差额是本地的图元原型推导、
像素测量分析、排版常量调整与逐图查看，不属于服务耗时。两者不可相加或互相替代。

## 6. 设计选择、经验与未解决事项

### 关键设计选择

1. **45° 段用旋转容器而非斜向多边形。** 五个探针逐一对比后确认唯一可用组合是
   `Positioned + Container transform=mat(θ) + transformAlignment="TOP_LEFT"`，
   并把定位原点平移到 `p1 + (sinθ·lw/2, -cosθ·lw/2)`。这样段的两端都是圆头端帽，
   与相邻正交段和站圆点自然衔接。像素上验证为斜率 -1.0000、垂直厚度恒定 14px。
2. **角度规则只约束绘图，不约束路由。** 一条站间边可以跨越多个绘图折线段
   （如 B 线 S04→S09 是一条站间边，图上跨越 3 段折线）。routes.json 为每条路线同时
   给出 `intervals`（站间边数）、`station_count`（站数）与 `drawn_segments_total`
   （绘图折线段数）三个量，并在每条 segment 上给出 `drawn_segments`，避免三者混淆。
3. **两张图共用一个样式模块、两套排版。** `a07_style.py` 集中定义背景、面板、线宽、
   圆点、色板与文字工具，保证视觉系统一致；示意图横向「地图面板 + 右侧图例」，
   旅行卡纵向「卡头 + 统计行 + 线路条（+ 说明 + 第二条线路条）+ 页脚」，互不重复。
4. **校验器不复用绘制脚本的中间结果。** C/D 系列检查器只从 `model.json` 与最终 PNG
   推导期望，并自行重算线路条位置；routes 审计则完全绕开 `model.json`，直接对
   题库输入重算最短路径。这样"答案错"与"版面错"都会被检查出来。
5. **无障碍约束通过计算得出而非声明。** 起终点/换乘站/途经的角色由遍历路线统计，
   判定字段由 `accessible` 布尔值比较得出；"未删线"一项也改为对照输入与绘制的
   站/线/边数量计算，不使用硬编码的 True。

### 可复用经验

- 旋转线段的定位原点必须补偿端帽外伸的半个线宽，否则接头错位。
- 图像坐标 y 向下，垂直方向必须由实测几何 `ux,uy = dx,dy` 归一化后取 `(uy,-ux)` 推出，
  不能用模型里不带符号的 `angle_deg`。
- 颜色判定用投影法：`v = 255 - im`，`w = 255 - color`，`t = clip(Σ(v·w)/|w|², 0, 1)`，
  `resid = ‖v - t·w‖`，保留 `‖v‖>60、t≥0.6、resid<25` 的像素。判定"是否有他色侵入"
  要收紧到 `resid<14、t≥0.75`，否则抗锯齿混合色（如 #B91C1B 70% 混合）会误判为 #DC2626。
- 测量栅格化细带的斜率必须逐列取像素中心后 `polyfit`，不能用整块像素的相关系数
  （14px 宽的带本身就有 ±7 横向散布，会把相关系数拉低约 0.02）。
- 排除掩膜不能破坏被测带的对称性：一个对称圆盘若只切掉带的一端下半截，
  逐列中心的偏差会在两端同向、中段为零，系统性压小拟合斜率。
- 圆点/角标的环取样半径要小于"半径 - 圆角半径"，否则落在圆角区之外；
  小尺寸色块改用"盒内填充像素数 + 中心白字像素数"更稳。

### 未解决事项

- 无阻塞项。题目要求的 2 张图片与 1 个 JSON 均已交付并通过独立校验。
- 唯一未单独记时的过程量是每次看图的具体时刻（`viewed_at` 为 null，
  已给出上下界窗口），其余指标均为实测。

### 结束依据

最终实际图片满足题目全部可核对要求：网络示意图 10/10 像素校验通过、旅行卡 10/10
像素校验通过、routes.json 14/14 审计通过（含对题库输入的独立重算）；
28 次看图覆盖两张图的全部版面与 21 处 2× 局部放大，5 处已知缺陷全部修复并复查。
不以"能渲染"或"文件齐全"作为完成依据。

### 留痕确认

临时目录保留了：11 个探针/版本 DSL（`dsl/`）、12 个请求体快照（`req-*.snapshot`）、
12 个响应与响应头（`responses/`、`*.headers.txt`）、22 张预览与 2× 局部放大图
（`preview/`，含 v1 成品的归档）、全部生成与校验脚本（`gen/`）、
`model.json`、`inspect-map.json`、`inspect-card.json`、`audit-routes.json`、
`requests.jsonl`、`iterations.jsonl`。未删除或覆盖任何尝试文件。
`__pycache__/` 为运行时缓存，不列为产物或自检证据。
总任务根的 `.gitignore` 已在启动时创建，忽略 `__pycache__/`、`*.pyc`、`*.pyo`、
`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/` 等运行时缓存；
未使用 `tmp/`、`outputs/`、`cache/`、`.cache/`、`*.log` 或整体图片/DSL/JSON 通配规则，
过程证据与最终产物均未被忽略。
