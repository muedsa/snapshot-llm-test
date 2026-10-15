# Snapshot 使用情况说明与踩坑记录

任务ID：A09
任务名称：十二个非对称图形变换标本
本次运行ID：run-20261011-01
完成状态：完成
结束原因：需求满足并完成逐图视觉自检
输出目录：`outputs/run-20261011-01/A09/`（路径基准：suite_root）
临时目录：`tmp/run-20261011-01/A09/`（路径基准：suite_root）
路径基准：suite_root；除本报告的 Markdown 本地链接（相对本文件所在目录）外，
所有记录中的本地路径均为相对 suite_root 的相对路径，未写死机器盘符或用户目录。

遵循 [PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录环境变量。
Markdown 本地链接相对当前文档；本报告位于 `outputs/<run_id>/A09/`，
故指向题库文档的链接为 `../../../tasks/…`。

## 1. 最终产物与需求完成情况


| 文件 | 用途 | 对应 DSL 或图 | 完成状态 |
|---|---|---|---|
| `transform-atlas.snapshot` | 1600×1200 十二变换标本定稿 DSL | `transform-atlas.png` | 已完成 |
| `transform-atlas.png` | 服务返回的最终图 | `transform-atlas.snapshot` | 已完成，服务原始响应 |
| `geometry-audit.json` | 列主序 4×4 矩阵、每矩形四角、圆点中心、最终外接框、像素核对 | — | 已完成，12/12 通过 |
| `snapshot-usage.md` / `task-metrics.json` | 报告与指标 | — | 已完成 |

需求逐项核对（依据最终图**实际查看**：整屏一次 + T01 格 2× 放大 + 橙色说明框 2× 放大；全部 12 格的像素核对由 `measure_a09.py` 对定稿 PNG 实测）

| 题目要求 | 满足情况 | 证据 |
|---|---|---|
| 1600×1200 变换图谱 | 满足 | 服务 `image_info` = PNG 1600×1200 |
| 4 列 × 3 行 | 满足 | `grid.cols = 4`、`grid.rows = 3`；图上 12 格按 T01–T04 / T05–T08 / T09–T12 排列 |
| 每格 300×250 | 满足 | `grid.cell_px = [300, 250]`；实测格底圆角矩形为 300×250 |
| 格间 32 | 满足 | `grid.gap_px = [32, 32]`，格 (c,r) 左上 = (152+332c, 140+282r) |
| 整体居中，格外保留标题与图例 | 满足 | 网格宽 4×300+3×32 = 1296，左边距 (1600−1296)/2 = 152；标题在 y 24–110，图例在 y 966–1190，均在格外 |
| 印章 3 矩形 + 1 黑圆点、120×120 | 满足 | 直接按 `inputs/stamp.json` 的 xywh 与 `ClipOval` 圆点绘制，未改动输入；图例左端另画一枚未变换的参考印章 |
| 局部坐标从印章左上角算 | 满足 | `Positioned(left=bx0, top=by0)` 放置 120×120 容器，子节点用 stamp.json 原样局部坐标 |
| 矩形之间部分相邻、圆点消除对称 | 满足 | 红(8,8,28,92)/蓝(36,72,68,28) 相邻于 x=36；圆点 (91,49) r=8 位于红/蓝/黄都不覆盖处，破坏镜像与旋转对称 |
| 操作按列表顺序，每步围绕局部 (60,60) | 满足 | `compose()` 按输入顺序 `M = op_matrix(op) · M`（先做的在右侧）；每步由 `about_pivot()` 施加枢轴平移 |
| x 向右、y 向下 | 满足 | 图上每格带 x/y 坐标轴与箭头；旋转矩阵用 `[[c,−s],[s,c]]`，正角即图像顺时针 |
| 顺时针按图像方向 | 满足 | T02 顺时针 90° 实测线部件 [[0,−1],[1,0]]，渲染中红横条在顶部、蓝竖条在左侧（与顺时针一致） |
| mirror_horizontal = 左右镜像 | 满足 | T05 线部件 [[−1,0],[0,1]]；渲染中红条移到右侧、黄块移到左上，与左右镜像一致 |
| mirror_vertical = 上下镜像 | 满足 | T06 线部件 [[1,0],[0,−1]]；渲染中红条在上、黄块在右下 |
| 最终局部中心放到每格中心 | 满足 | 印章容器中心 = 格左上 + (150,112) = 格中心；`subject_center_px` 与 `cell_center_px` 逐格相等 |
| 图中编号、操作短名与刻度辅助线齐全 | 满足 | 每格左上 T01–T12 编号徽章（22px）+ 短名（22px）；虚线 120×120 原位框 + 每 20 单位一格边缘刻度 + x/y 坐标轴与箭头（20px） |
| 不裁切变换后的主体 | 满足 | 12 格 `final_bounding_box_px` 全部落在各自 `cell_box_px` 内，`clipped_by_cell` 全为 false；定稿整屏查看无任何主体被格框裁切 |
| 必须用 Transform.matrix 表示最终组合变换 | 满足 | 每格主体是唯一的 `Transform matrix="…"`（线性部分），12 个矩阵字符串逐格写入 `geometry-audit.json.matrix_dsl_string`，DSL 中不存在手改后的形状坐标 |
| 圆点随同变换 | 满足 | 圆点在同一个 `Transform` 子树内（`ClipOval`）；T02 圆点实测质心误差 0.00px，T11/T12 误差 0.10–0.13px |
| T07 与 T08 显示操作顺序差异 | 满足 | 两格并排，各自带两步操作行；线部件 T07 = [[0,−1],[−1,0]]（关于 x+y=120 的反对角线反射）、T08 = [[0,1],[1,0]]（关于 x=y 的主对角线反射）；橙色说明框单独写明两者结果与「两格互为镜像」 |
| 附 geometry-audit.json（列主序 4×4 矩阵） | 满足 | `transforms[].matrix_column_major_4x4_dsl` 为 16 个数的列主序 4×4 |
| 每矩形四角 | 满足 | `geometry[].rectangles[].local_corners_source_order`（源序）与 `local_corners_after_transform`（变换后）、`canvas_corners_tl_tr_br_bl` |
| 圆点中心 | 满足 | `geometry[].dot`：源中心/半径、变换后局部中心、画布中心、长短半轴 |
| 最终外接框 | 满足 | `transforms[].final_bounding_box_px` + `geometry[].final_bounding_box_px`（12 格齐全） |
| ±1.5 像素的视觉/像素核对方法 | 满足 | `verification[0]` 给出完整方法（白底混合反算 + 3px 外扩窗口 + 3×3 邻域覆盖率 0.12 + 抗锯齿阈值 0.04），实测最大误差 **0.566px ≤ 1.5px**，12/12 通过 |
| 反走样边缘例外 | 满足 | 同上，并列记录 strict（不含混合像素）口径：`strict_measured_radius_px` / `strict_pixels` 与 `strict_max_abs_error_px` 一并写出 |
| 标签 ≥20 | 满足 | 标题 36px、编号 22px、短名 22px、操作行 20px、轴端字母 20px、图例正文 20px、页眉副题 22px |



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

| https://snapshot.muedsa.com/reference/parser-tags/ · Text | `Text` 不加 `softWrap` 时溢出自身宽高框的部分会被裁掉，不会自动换行 | 橙色说明框标题「T07 与 T08：同一组操作，顺序不同」被截成「…顺」，见 v5→v6 修复 |


本次实际用到的能力：布局：`Container`/`Column`/`Row`/`Expanded`/`SizedBox`/`Padding`；精确定位：`Stack(fit=EXPAND)` + `Positioned`；文本：`Text` 的 `fontFamily`/`fontSize`/`textAlign`/`height`/`maxLines`/`letterSpacing`；颜色与透明度：CSS 颜色与 `#RRGGBBAA` 独立 alpha；装饰：`border`（宽度+样式+颜色）、`borderRadius` 与四角圆角、`boxShadow`；裁剪：`ClipRRect`/`ClipOval`；变换：`Transform` 的列主序 4×4 矩阵 + `alignment`；滤镜：`ImageFiltered`（子树模糊）、`BackdropFilter`（仅背景模糊）；渐变：`gradientType=LINEAR/RADIAL/SWEEP` + `gradientColors`/`gradientStops`。解析器未提供 `ClipPath`/多边形，所有图形均由矩形、圆角矩形、椭圆与渐变拼装。
本题额外用到：**`Transform.matrix` 实测语义**（探针 `probe_matrix.py`，出图 `preview/probe-p1.png`，4 次请求中前 3 次因 DSL 语法 400）：服务端把 `Transform(matrix, alignment="CENTER")` 实现为 `p' = C + L·(p − C) + t`，其中 C 为子节点中心、L 为矩阵线性部分、t 为最后一列平移，**m[8]/m[9] 两槽被忽略**，且 `t` 会在 CENTER 枢轴之外**再叠加一次**。因此本题只把组合变换的**线性部分**写入矩阵、平移列取 0，枢轴 (60,60) 由 `alignment="CENTER"` 承担——因为印章容器 120×120 的中心恰是 (60,60)；矩阵字符串不含任何空白（`matrix` 属性不接受空格）；任意方向的辅助线段（虚线框、刻度、坐标轴、箭头）统一用 `Positioned > Transform(rot) > Container` 的旋转胶囊拼装；虚线由沿折线均匀排布的短胶囊构成；坐标轴端字母、刻度、枢轴环、图例参考印章全部由 DSL 构造。

字体：实际查询 `GET /fonts` 得到 27 个字体族，原始响应留存于
`tmp/run-20261011-01/A09/responses/`（request_type=fonts），另有整理副本 `outputs/run-20261011-01/A09/../_suite/fonts-list.txt`。
中文正文使用 `Noto Sans CJK SC`，数字/拉丁使用 `Inter` 系列，代码/等宽使用 `Noto Sans Mono CJK SC`。
题目素材政策为纯 DSL，未使用任何外部图片（`<Image>` 标签本次未使用）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/run-20261011-01/A09/requests.jsonl`
迭代记录文件：`tmp/run-20261011-01/A09/iterations.jsonl`
响应与草稿留痕：`tmp/run-20261011-01/A09/responses/`、`tmp/run-20261011-01/A09/drafts/`

渲染请求总数：11
成功次数：8
失败次数：3
重试请求数：0（是总请求的子集）
DSL版本数：8
实际图片查看次数：11
完整视觉迭代数：5
未完成视觉迭代数：0
其他接口查询：字体查询与文档读取为 run 级共享准备；本题额外做了 **1 组引擎语义探针**（`probe_matrix.py`，4 次渲染请求：3 次 400 + 1 次 200），用于确定 `Transform.matrix` 在本服务端的实际语义，探针 DSL 与出图均保留在临时目录。

初次生成和查看计为基线，不计为改进迭代。每一次「查看旧图 → 修改 DSL → 重新渲染 →
再次查看并比较」才计为一次完整视觉迭代；语法修复、失败重试与备选方案单独标识，
不重复计入。所有图片均已用图像工具实际打开查看（含整屏与放大局部）。

| 请求ID | 输入 DSL | 耗时 | HTTP / Content-Type | 响应文件 | 查看与实际结果 |
|---|---|---|---|---|---|
| A09-v1-68178653 | drafts/a09-v1.snapshot | 4.28s | 200 image/png | preview/a09-v1.png | 首版出图并实际打开：12 格里只有 8 格渲染出主体，跨格虚线/刻度异常；原因是 `Transform.matrix` 语义未探明（枢轴与平移列处理未知） |
| A09probe-p1-ec97599d | drafts/a09-v1.snapshot（探针复用） | 2.34s | 400 application/json | responses/A09probe-p1-ec97599d.error.json | 无图；探针 DSL 语法错误（`Positioned` 放了多个子节点） |
| A09probe-p1-1842957c | drafts/a09-v1.snapshot（探针复用） | 1.72s | 400 application/json | responses/A09probe-p1-1842957c.error.json | 无图；探针 DSL 修正后仍有一处 `Stack` 里直接放 `Container` |
| A09probe-p1-932116da | drafts/a09-v1.snapshot（探针复用） | 1.54s | 400 application/json | responses/A09probe-p1-932116da.error.json | 无图；探针 P1/P2 两个探针共用了同一 `Positioned`，仍违反单子节点 |
| A09probe-p1-55d8c0d0 | probe_matrix.py 生成 | 2.15s | 200 image/png | preview/probe-p1.png | 语义探针出图并实际打开：确认 `alignment="CENTER"` 绕子节点中心作用、平移列会被**额外叠加一次**、`m[8]/m[9]` 被忽略、`alignment="TOP_LEFT"` 绕左上角 |
| A09-v2-163b4be9 | drafts/a09-v1.snapshot | 8.01s | 200 image/png | preview/a09-v2.png | 已打开：12 格全部渲染正确，矩阵语义问题解决；仍沿用旧的文字带位置 |
| A09-v3-9c27c1fe | drafts/a09-v1.snapshot | 4.58s | 200 image/png | preview/a09-v3.png | 已打开：几何全部正确；T07/T08/T12 的两步操作挤在同一行、连成一片不可读 |
| A09-v4-7abf3542 | drafts/a09-v1.snapshot | 4.35s | 200 image/png | preview/a09-v4.png | 已打开：操作改为每步一行后可读；但轴端字母「x」「y」落在操作文字带上，渲染成「(1) 左右镜像y」「(1) 非等比 1.2̌5 × 0.75」这类压字 |
| A09-v5-df0a16ae | drafts/a09-v1.snapshot | 4.50s | 200 image/png | preview/a09-v5.png | 已打开并 2× 放大：格内压字全部消除；橙色说明框标题「T07 与 T08：同一组操作，顺序不同」被自身高度裁成「T07 与 T08：同一组操作，顺」，「序不同」丢失 |
| A09-v6-a7af7f66 | drafts/a09-v1.snapshot | 4.27s | 200 image/png | preview/a09-v6.png | 已打开并 2× 放大：标题改为「T07 与 T08：顺序不同」并加 `softWrap`、加高，5 行正文完整；整屏与 T01 格放大复查通过（见 metrics：像素核对 12/12，最大误差 0.566px） |
| A09-final-* | outputs/run-20261011-01/A09/transform-atlas.snapshot | 见 metrics | 200 image/png | outputs/run-20261011-01/A09/transform-atlas.png | 定稿渲染并打开复查 |

## 4. 修改记录与踩坑

| 版本 / 类型 | 观察到的实际问题 | 原因及确认依据 | 实际修改 | 复验结果 |
|---|---|---|---|---|
| v1 · visual | 12 格里只有 8 格渲染出印章主体，跨格虚线与刻度异常 | `Transform.matrix` 的实际语义未探明：枢轴由谁承担、平移列是否叠加都不确定 | 先做语义探针（见下），确定「只写线性部分、t=0、枢轴交给 alignment=CENTER」，再重建全部 12 格 | 12 格主体全部正确出现 |
| probe · syntax-fix | 探针连续 3 次 400 | ① `Positioned` 内并列了多个子节点；② `Stack` 里直接放了 `Container`；③ 两个探针共用一个 `Positioned` | 逐个探针各包一层 `Positioned`，内部统一为 `Positioned > Container > Stack > Positioned…` | 探针出图（P0–P4），语义判读完成 |
| v3 · visual | T07/T08/T12 的两步操作连成「(1) 左右镜像y(2) 顺时针 90°」，不可读 | 两步操作用两个半角空格拼成一行交给自动换行，断点落在分隔处时两段会贴在一起 | 改为**一步操作一行**（自格左上 + (14,196) 起，行距 25px），行内不再有跨步分隔符 | 两步变换均可逐行读出 |
| v4 · visual | 轴端字母「y」压在操作序列第一行上（渲染成「(1) 左右镜像y」） | 「y」原放在格内主体中心 +78px，正好落在操作文字带（格左上 +194px 起）内 | 把「x」「y」移出 120×120 原位框：「x」放在水平轴上方 (ccx+60, ccy−31)、「y」放在竖直轴左下 (ccx−40, ccy+60)。该区域对 12 个变换全部为空（旋转/镜像把方框映回自身、等比缩放收缩、非等比只沿 x 越出 15px） | 格内 12 处压字全部消除 |
| v5 → v6 · visual | 橙色说明框标题「T07 与 T08：同一组操作，顺序不同」只显示到「…顺」 | `Text` 未设 `softWrap`，而所在 `Positioned` 高度只有 26px，第二行被裁掉 | 标题精简为「T07 与 T08：顺序不同」（单行可容纳）、加 `softWrap="true"`、框高 26→30px，正文下移到 top=50 并按实测 5 行留足 140px | 2× 放大确认标题与 5 行正文完整显示，末尾「两格互为镜像。」未被裁 |

「渲染成功但视觉不符合要求」的问题同样记录在上面的完整视觉迭代中。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/run-20261011-01/A09/task-metrics.json`


| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始 / 结束时间 | 2026-10-11T16:05:39.485+08:00 / 2026-10-11T16:43:20.223+08:00 | ISO8601 带时区 | 计时记录（本地时钟，带时区） |
| 任务总耗时 | 2260.738 | 秒 | 墙钟时间（读题 → 计算 → 构造 → 渲染 → 看图 → 修复 → 报告） |
| 首次可用图耗时 | 4.279 | 秒 | 从开始到首个 `200 image/png` 且能打开的图为止的全部请求耗时之和；本任务请求串行，故与实际顺序一致 |
| 等待用户反馈 | 0.0 | 秒 | 本题为单轮任务，无多轮反馈等待 |
| 限流等待 | 0.0 | 秒 | 全程未出现 `429`（见 `requests.jsonl`） |
| 排队等待 | None | 秒 | 服务未提供排队指标，不可测量，记 null 而非 0 |
| 已记录请求耗时之和 | 42.696 | 秒 | `requests.jsonl` 中 `duration_seconds` 求和；请求串行，不与墙钟重复计入 |
| 成功 / 失败 / 重试请求 | 8 / 3 / 0 | 次 | `requests.jsonl`；失败均为不同 DSL 的语法修复，非同一请求重试 |
| 看图 / 完整视觉迭代 | 11 / 5 | 次 | `iterations.jsonl` 与实际图像查看记录 |
| DSL 版本数 | 8 | 个 | `requests.jsonl` 去重 |
| Server-Timing | null | — | 服务响应未返回该头，日志中如实记为 null |


## 6. 设计选择、经验与未解决事项


**关键设计选择**

1. *先探明引擎语义，再谈矩阵*。这是本题真正的难点：题目要求「必须用 `Transform.matrix` 表示最终组合变换」，
   但服务端对 `matrix` 的实现不是教科书写法。探针 `probe_matrix.py` 一次渲染四个样本：
   - P0 恒等：`alignment="CENTER"`，单位矩阵 → 落点与理论一致；
   - P1 线性部分 + 平移 t=(120,0)：整体比理论**多右移 120px**，证明平移列被叠加了一次；
   - P2 只写线性部分：落点与理论一致；
   - P3 把平移放到 `m[8], m[9]`：与 P2 完全相同 → 这两槽被忽略；
   - P4 `alignment="TOP_LEFT"`：绕子节点左上角旋转 → `alignment` 确实生效。
   结论：`p' = C + L·(p − C) + t`，其中 C 为子节点中心、L 为线性部分、t 为最后一列；
   **矩阵里只写线性部分、t 取 0**，枢轴交给 `alignment="CENTER"`。
   由于印章容器是 120×120、中心恰为 (60,60)，这正好等于「绕局部 (60,60) 的组合变换」。

2. *绕枢轴的组合在程序里算，图形里只有一个矩阵*。`about_pivot()` 对每步操作施加
   「平移到枢轴 → 线性变换 → 平移回枢轴」，`compose()` 按输入顺序相乘（先做的在右侧）。
   写进 DSL 的只有结果的 2×2 线性部分——**不存在任何手改后的形状坐标**，
   矩形和圆点都用 stamp.json 的原始局部坐标，一个矩阵节点统管整枚印章。
   审计里同时给出「绕枢轴 3×3 仿射」「2×2 线性部分」「列主序 4×4 DSL 串」三份，便于交叉核对。

3. *坐标约定写死在代码注释与审计里*。屏幕 y 向下，正角 = 图像顺时针，故旋转用 `[[c,−s],[s,c]]`；
   T02 的实测线部件 `[[0,−1],[1,0]]` 与图中「红横条在顶、蓝竖条在左」一致，
   确认没有把「图像顺时针」写成「数学顺时针」。

4. *辅助线全部落在「变换绝不触及」的区域内*。虚线 120×120 原位框、每 20 单位一格的边缘刻度、
   x/y 坐标轴与箭头都画在**格内主体中心的固定位置**，不随变换移动：
   读者一眼就能看出「原位」与「变换后」的对照。轴端字母 `x`/`y` 则特意放在原位框**之外**
   （旋转/镜像把方框映回自身、等比缩放收缩、非等比 1.25×0.75 只沿 x 越出 15px），
   因此 12 格都不会压到主体或文字。

5. *T07/T08 用「并排 + 单独说明框」表达顺序敏感性*。两格线性部分分别为 `[[0,−1],[−1,0]]` 与 `[[0,1],[1,0]]`，
   在图中可以直接看出一个把红条压成「⌐」形、一个压成横条；橙色说明框单独写明
   「T07 = 镜像H → 旋转90° ⇒ 关于 x+y=120 的反对角线反射；T08 = 旋转90° → 镜像H ⇒ 关于 x=y 的主对角线反射」。

**问题与修复（要点）**

- 首次渲染只有 8 格出现主体，根因是把 `Transform` 当成了「带完整仿射的矩阵变换」；
  探针证明平移列会被重复叠加后，改为只写线性部分，12 格一次通过。
- `Text` 不设 `softWrap` 时超出自身宽高框的部分**直接裁掉、不自动换行**；
  橙色说明框标题就是这样丢了「序不同」三个字，已在 v6 修正（精简标题 + `softWrap` + 加高）。
- `matrix` 属性**不接受空白字符**，矩阵串用 `","` 紧凑拼接。
- `Positioned` 只接受一个子节点、`Stack` 里不能直接放 `Container`——探针阶段连续 3 次 400 都出在这里。

**可复用经验**

- 「必须用矩阵而不是手改坐标」的作图题，**第一步就应该写一个语义探针**（恒等 / 加平移 /
  平移放 m[8],m[9] / 换 alignment 四个样本，一次渲染即可判读），比逐格试错快得多。
- `Transform(matrix, alignment="CENTER")` 在本服务端的公式是 `p' = C + L·(p − C) + t`；
  当子节点中心就是要保留的枢轴时，**只写线性部分**即可，这是最省事也最不容易错的用法。
- 版面上的「压字」要靠**区域不变量**来根治：把标签放到「任何输入取值下都不会被内容触及」的带内
  （本题用「原位框之外 + 文字带之外」两条不变式），而不是靠逐格挪像素。
- 几何正确性用**渲染像素反算**独立验证，而不是靠「矩阵推导正确」自证：
  12 格 × 3 矩形 + 1 圆点的实测位置与解析值最大差 0.566px（量化上限 0.5px）。

**结束依据**：最终图实际整屏打开，并 2× 放大查看了 T01 格（编号/短名/原位框/刻度/轴端字母/枢轴环/操作行）
与橙色说明框；`measure_a09.py` 对**定稿 PNG** 逐格反算像素位置，12/12 通过、最大误差 0.566px ≤ 1.5px，
12 格外接框全部在格内、无裁切。未以「渲染成功」作为完成依据。


### 未解决事项 / 限制


- 无影响交付的未解决问题。
- 探针阶段的 3 次 400 与首版缺格均为真实失败尝试，DSL/请求体/错误响应全部保留在临时目录
  （`responses/*.request.txt`、`responses/*.error.json`），未删除、未覆盖。
- `geometry-audit.json` 中圆点在非等比变换（T10）下按长半轴 10.0px、短半轴 6.0px 的**外接圆**计入
  最终外接框与测量窗口；像素核对时圆点仍按圆形窗口求质心，故 T10 的圆点等效半径实测 7.5px
  （strict 口径 6.5px），与长短半轴的几何平均值一致，不是误差。
- 服务端 `Transform` 的平移列语义属于**实测结论**（基于本服务 2026-10-11 的行为），
  若服务升级后语义变化，需重跑 `probe_matrix.py` 并同步更新审计中的 `engine_transform_semantics` 字段。


### 留痕确认

- 临时目录中的草稿 DSL、各次请求体副本、成功图片、失败响应 JSON、放大裁切图与预览全部保留，未删除或覆盖任何一次尝试；日志为追加写入。
- `tasks/` 下的输入文件、任务说明与模板均未被修改。
- 未保存任何密钥；`SNAPSHOT_API_KEY` 若存在只从环境变量读取，不写入 DSL 或日志。
- 总任务根 `.gitignore` 已创建（参考 `templates/gitignore-template.txt`），仅排除 `__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`、`.ipynb_checkpoints/`、`node_modules/.cache/` 等明确的运行时缓存；**未**使用 `tmp/`、`outputs/`、`cache/`、`.cache/`、`*.log` 或图片/DSL/JSON 通配规则，因此本任务的过程证据不会被忽略（共享规则详见 `_suite/snapshot-usage.md`）。
- `__pycache__/` 等运行时缓存不作为留痕材料，也不列为产物或自检证据。
