# A09 使用说明与自检报告 · 十二个非对称图形变换标本

- 任务：`tasks/A09-transform-atlas/TASK.md`（与 `task.json` 一致），执行约定见
  `tasks/A09-transform-atlas/AGENTS.md` 与总根 `AGENTS.md`
- run_id：`20261008T1615Z-run01`；本题输出根 `outputs/20261008T1615Z-run01/A09/`，
  过程目录 `tmp/20261008T1615Z-run01/A09/`（`path_base=suite_root`，全部为相对总任务根的路径）
- 状态：**completed**。12 格主体一律为“未改动的原始印章 + 一个 `Transform.matrix`”，最终图是
  服务真实响应并配同名完整 `.snapshot`；独立像素复核 0 问题；未解决事项为空
- 服务：`POST https://open-snapshot.muedsa.com/snapshot`，`Content-Type: text/plain; charset=utf-8`
  （地址来自总 `run-config.json`，覆盖本题 `tasks/A09-transform-atlas/run-config.json` 的原题默认值）

## 1. 交付清单

| 文件 | 字节 | 说明 |
|---|---|---|
| `outputs/20261008T1615Z-run01/A09/transform-atlas.png` | 198834 | 1600×1200 RGBA，4 列 × 3 行标本图谱 |
| `outputs/20261008T1615Z-run01/A09/transform-atlas.snapshot` | 212966 | 生成该图的完整 DSL（请求体本身，非事后补写） |
| `outputs/20261008T1615Z-run01/A09/geometry-audit.json` | — | 列主序 4×4、每矩形四角、圆点中心、外接框、±1.5px 核对方法与实测结果 |
| `outputs/20261008T1615Z-run01/A09/task-metrics.json` | — | 请求/迭代/看图/耗时统计 |
| `tmp/20261008T1615Z-run01/A09/plan_a09.py` / `plan_a09.json` | — | 矩阵代数与预测几何（数据层，与绘图层分离） |
| `tmp/20261008T1615Z-run01/A09/generate_a09.py` | — | DSL 生成 + TextFit/元素数门禁 |
| `tmp/20261008T1615Z-run01/A09/check_a09.py` / `pixel-report.json` | — | 只读 PNG 与预测值的独立像素复核 |
| `tmp/20261008T1615Z-run01/A09/crop_a09.py` + `preview/crops/`（16 张） | — | 2×/3× NEAREST 放大看图 |
| `tmp/20261008T1615Z-run01/A09/requests.jsonl` / `iterations.jsonl` | 4 / 4 行 | 请求与迭代留痕 |
| `tmp/20261008T1615Z-run01/A09/requests/` | 4 组 | 每次请求体、原始响应字节、响应头 |
| `tmp/20261008T1615Z-run01/A09/v01…v04.snapshot`、`final.snapshot`、`preview/v02…v04.png` | — | 全部草稿版本与预览，未覆盖、未清理 |

字节一致性（实际比对，非声明）：`transform-atlas.png` == `requests/A09-v04-20261008T134808Z.response.bin`
== `preview/v04.png`，sha256 前缀 `53745dec3f1a0f2d`；`transform-atlas.snapshot` == `v04.snapshot`。
即交付图没有被裁切、二次编码或手工修图，交付 DSL 就是产出该图的那一份请求体。

## 2. 需求逐条对照（依据实际图像与实测数据）

| TASK.md 要求 | 实际证据 |
|---|---|
| 1600×1200 | PIL 读图 `(1600, 1200)`，服务响应头 `image/png` |
| 4 列 × 3 行、每格 300×250、格间 32 | `geometry-audit.json` 的 `canvas.grid`：`cell=[300,250] gap=32 columns=4 rows=3`，每格 `cell_rect_canvas` 实测等差 332/282 |
| 整体居中 | 网格宽 4·300+3·32=1296 → left=(1600−1296)/2=152；高 3·250+2·32=814 → top=(1200−814)/2=193；标题带在网格上方、图例在下方，均在网格之外 |
| 格外保留标题与图例 | 头部标题/两行副题（`crops/header.png`）；底部 `图例 · 印章构件与辅助线` 两行色块 + 两段说明（`crops/legend.png`），`legend_bottom=1167 ≤ 1180` |
| 120×120 透明印章：3 彩色矩形 + 黑圆点 | `inputs/stamp.json` 的 `xywh`/`color`/`center`/`radius` 原样进入 DSL：红 `8,8,28,92`、蓝 `36,72,68,28`、黄 `64,8,40,28`、点 `(91,49) r=8` |
| 矩形之间部分相邻、用圆点消除对称 | 红右边缘 x=36 与蓝左边缘重合、蓝上边缘 y=72 与红底边重合（相邻而不重叠于内部）；圆点既不在对称轴也不在矩形中心，12 格无二重对称 |
| 局部坐标从印章左上角算 | 所有形状坐标即 `stamp.json` 原值，未加任何平移；T01 单位矩阵格实测外接框 = 印章 bbox `(8,8)-(104,100)` 并含圆点半径（`identity_control_T01: true`） |
| 操作按列表顺序、每步绕局部 (60,60) | `conventions.composition`：`A_total = A_last ··· A_first`；每步的中间矩阵记入 `cells[*].steps`；旋转/镜像均以局部 (60,60) 为不动点（`matrix_column_major_local` 的平移分量为 0） |
| 像素坐标 x 向右、y 向下，“顺时针”按图像方向 | `mat_of("rotate_clockwise_deg")` 取 `[[cos,−sin],[sin,cos]]`；实测 T02（rot 90°）中原本竖直的红条变为水平且位于上方，与图像方向顺时针一致 |
| mirror_horizontal=左右、mirror_vertical=上下 | `[[−1,0],[0,1]]` / `[[1,0],[0,−1]]`；T05 红条从左侧换到右侧、T06 红条上下端互换，与定义一致 |
| 最终局部中心放到每格中心 | 每格 `Transform` 放在 `(cx−60, cy−60, 120, 120)` 且 `alignment="CENTER"`，圆点 (91,49) 变换后落在预测的 `dot_centre_canvas`，12/12 实测质心偏差 ≤ 1.5px |
| 编号、操作短名、刻度辅助线齐全 | 每格左上 `T01…T12`（24pt）、右上短名（`rot 90°`、`mirror H → rot 90°`…20pt）、底部 `det ±x.xx` 与外接框 `W×H px`；辅助线含 20px 刻度网格、每 100px 强线、格顶/格左刻度尺、过 pivot 虚线轴、pivot 环、外接框四角角标 |
| 不裁切变换后的主体 | 每格 `bbox_canvas` 与舞台边界留正 margin（`cell_margin_px` 最小 53.97，舞台内最小 10.0）；生成器 `assert` 每格外接框在舞台内；跨格 32px 沟槽墨迹扫描 = 0 px；祖先一律 `clipBehavior="NONE"` |
| 必须用 `Transform.matrix` 表示最终组合变换，不得手改形状坐标冒充 | 主体 DSL 只有一份 120×120 印章（`stamp_body()` 输出，12 格复用同一字符串），外面套 `<Transform matrix="…" alignment="CENTER">`；`transform_matrix_attribute` 与 `matrix_column_major_screen` 逐元素相等，12 格属性互不相同 |
| 圆点随同变换 | 圆点是印章 Stack 的子节点，与矩形共用同一 `Transform`；T09/T10 中实测为缩小的圆/椭圆（`dot_ellipse_half_extents` 与实测外接范围一致） |
| T07 与 T08 显示操作顺序差异 | `order_dependence`：`[[0,−1],[−1,0]] ≠ [[0,1],[1,0]]`，`order_matrices_equal=false`；两格图形互为镜像（T07 红条在底、蓝条居左，T08 红条在顶、蓝条居右），图例第一注直接写出两个矩阵不等 |
| 附 `geometry-audit.json`：列主序 4×4、每矩形四角、圆点中心、最终外接框 | `cells[*].matrix_column_major_local/screen`、`rect_corners_local/canvas`、`rect_bboxes_canvas`、`dot_centre_local/canvas`、`bbox_local/bbox_canvas` 全在 |
| ±1.5 像素的视觉/像素核对方法（反走样边缘例外） | `verification_method` 六条：`visual`、`pixel`、`edge_caveat`、`corner_probe`、`rim_attribution`、`identity_controls`、`ab_anticlipping`；实测 `pixel_verification.max_abs_delta_px=1.215 ≤ 1.5`、`corner_probes_pinned=144/144`、`problems=[]` |
| 标签 ≥ 20 | 门禁 `min_font_pt=20`（整图 43 个文本项，最小字号恰为 20pt） |

## 3. 文档与 DSL 能力的实际使用

- **`Transform.matrix` 的列主序映射**（据 `tmp/…/_suite/` 缓存的 Snapshot 文档，A01 起已真实抓取）：
  16 个 Float、外层括号必需、**值之间不能有空格**，索引 = row + 4·col。因此 2×2 仿射
  `[[a,b],[c,d]]` 加平移写作 `(a,c,0,0, b,d,0,0, 0,0,1,0, tx,ty,0,1)`。本题 12 个属性串由
  `plan_a09.py:column_major44()` 生成，并与 `dslkit.line()` 的同序约定互校，避免把行主序写反。
- **`alignment="CENTER"` 把矩阵原点放到子盒中心**：于是旋转/镜像天然绕印章局部 (60,60)，
  不需要把 60 的偏移写进任何形状坐标——这正是“不能手改形状坐标冒充矩阵”的实现方式。
- **变换只影响绘制、不影响布局**：配合祖先 `clipBehavior="NONE"`，变换后的主体越出 120×120
  子盒也不会被裁（T11/T12 外接框 129×128 > 120 即为证据）。
- **没有虚线描边原语**：刻度轴/外接框的“虚线”只能重复短 `line()`，而每段虚线要 3 个元素
  （`Positioned` + `Transform` + `Container`）。v01 因此撞上服务硬上限
  **单文档 ≤ 4096 元素**（HTTP 400 `RENDER_ERROR: Document contains more than 4096 elements`，
  314168 字节 DSL）。改法：外接框虚线轮廓 → 四角角标，虚线段 dash 6→11/gap 5→7；
  并在生成器里加 `elements <= 4000` 断言与元素计数上报。最终 2833 元素。
- **文本属性名**：字号是 `fontSize`（不是 `size`），另有 `color`、
  `fontFamily="Inter,Noto Sans CJK SC"`。
- **TextFit 门禁**（`tmp/…/_suite/scripts/` 的 `fit` 模块，A05 起用于本题）：盒宽 ≥ 估宽/0.96、
  高度按 1.45 行距容纳换行；中日韩与歧义宽度字符（U+2190–24FF、U+25A0–25FF、≥U+2E80，
  以及 `·＝—°／→×`）按 1.02 em，字母数字 0.58 em，空格 0.30 em。本题首轮报出 24 项违规
  （副题、短名、`det`、两注），逐条通过“加宽盒 / 缩短文案 / 把 `外接 96.0×92.0` 改成 `96×92 px` /
  删去每格中心坐标行”修到 `fit_problems: []`，而不是靠放大字号或裁字蒙过。
- **未使用的能力**：`<Line>`/`<Rectangle>` 标签、`backgroundImage`、外部素材（A 类要求纯 DSL 主体）。

## 4. 视觉迭代与自检结论

4 次渲染、4 个 DSL 版本、2 轮完整视觉迭代（v03、v04）+ 1 轮基线（v02）+ 1 轮语法/上限修正（v01）；
实际打开图片 10 次（2 次整图 + 8 次 2×/3× 局部放大）。

1. **v01（语法修正轮，未出图）**：元素数超上限，错误响应体与请求体都留在
   `requests/A09-v01-20261008T132712Z.response.bin`。这一轮不记为视觉迭代。
2. **v02（基线）**：整图 12 格几何已正确，但独立像素复核报 28 个角点误判。查像素邻域发现
   是我自己的判据缺陷：外接框角标画在真实角点上，探针把角标当成了主体墨迹。
   修判据同时把角标外偏 6px。另发现“只统计完全等于成分色的饱和像素”会让实测框右/下系统性
   缩进约 2px（最后一圈是抗锯齿混合），于是改为按“舞台底色→成分色”混合线段归属像素。
3. **v03（视觉迭代 1，主要修判据）**：收紧混合容差（BLEND_TOL 4 / ALPHA_MIN 0.12）后网格线不再
   被误判成蓝色墨迹，最差格 1.215px，但仍剩 2 个角点误判（T11/T12 的红色细长条）。
   沿角点对角线打印像素才发现根因：**细长条的角点对角线几乎平行于长边**，2.5px 探针只深入
   宽度 0.7px，正好落在相邻矩形覆盖的接缝上；另有 1 个角点最外圈像素是“黄 × 20px 刻度网格 ×
   舞台”的三重混合，严格 stage→色 拟合误差 15 而落判据之外（实测该像素黄色 α=0.92）。
   据此把角点判据整体换成**亚像素支撑线残差**：沿“格心→角点”方向（该方向位于角点的法锥内，
   矩形在其上的唯一极值点正是这个角点）取墨迹投影极值，并用抗锯齿覆盖率把像素中心换算成
   真实边缘位置 `中心 + (α − 0.5)`；同时加第二条准入路径“距纯成分色 ≤ 40 色阶”。
   结果 `corners_pinned_total=144/144`、`problems=[]`。
4. **v04（视觉迭代 2，最终交付）**：2× 放大看图后修三处真实视觉问题——
   (a) 20px 刻度网格与主体同样抢眼，拆出 `GRID_MINOR #D5DEEB` / `GRID_MAJOR #BCC8DA` 两级浅灰蓝；
   (b) **角标 elbow 实际落在外接框内侧 6px、压在主体角点上**（v03 图上绿色角标叠在蓝色矩形角部，
   正是 v02/v03 判据误判的图像学根源），改为 elbow 在框外、两臂朝框内回伸；
   (c) 图例中黑色圆点色块在深底板上几乎不可见，改为按色块亮度自动加浅色描边。
   复核：`problems=[]`、144/144 角点、worst 1.215px、沟槽墨迹 0、T01 单位矩阵对照通过。

**逐格看图结论**：T01（单位矩阵，与印章原样一致）、T02/T04（90°/270° 互换长短轴方向，
外接框 96×92 ↔ 92×96）、T03（180° 中心对称）、T05/T06（左右 / 上下镜像，手性翻转）、
T07/T08（顺序相反 → 互为镜像，顺序不可交换）、T09（等比 0.75，圆点同步缩小）、
T10（1.25×0.75，圆点变扁椭圆）、T11/T12（30° 与“上下镜像后 30°”，外接框 129×128 且角标完整可见）
均与预测一致。

## 5. 统计与未解决事项

- 服务请求 4 次（3 次 200 出图、1 次 400 元素超限），重试 0 次，DSL 版本 4 个，
  完整视觉迭代 2 轮，`image_views`（记录了“看过图”的迭代轮）3。
- 看图事件合计 10 次：整图 2（v03、v04）+ 局部放大 8（v03 的 header/legend/cell_T07，
  v04 的 legend/cell_T01/cell_T09/cell_T11/cell_T12）；放大裁图共生成 16 张。
- 耗时：本题墙钟 2373.0s（13:12:49 → 13:52:22），首张可用图 910.6s，
  4 次请求服务端/网络耗时之和 24.859s（`Server-Timing` 与本地计时见 `requests.jsonl`），
  其余时间为矩阵推导、门禁修正与像素复核。文档抓取属 `shared`（12 个请求 / 28.078s），
  只在 `_suite` 计一次，不并入本题。
- 数据自检：12 个矩阵属性串互不相同；`order_matrices_equal=false`；`min_cell_margin=53.97`、
  `min_stage_margin=10.0`；TextFit 43 项 0 违规；`min_font_pt=20`；元素 2833 / 上限 4096。
- **未解决事项：无。** 需要留意的是服务侧两条硬约束（单文档 ≤ 4096 元素、`Transform.matrix`
  值间不得留空格），已写入总 `_suite/snapshot-usage.md` 的跨题经验；A10 之后的题若需要密集
  虚线，应改用角标/长划或减少重复元素。
