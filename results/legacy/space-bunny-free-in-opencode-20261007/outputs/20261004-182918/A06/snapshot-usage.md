# A06 · 十四节点依赖图与反馈回路 —— 使用报告与自检表

- 题目：`tasks/A06-dependency-graph/`（TASK.md / task.json）
- run_id：`20261004-182918`
- 输出目录：`outputs/20261004-182918/A06/`
- 临时目录：`tmp/20261004-182918/A06/`
- 服务：`POST https://open-snapshot.muedsa.com/snapshot`（匿名、带浏览器 User-Agent，由 `_suite/snapkit.py` 处理）
- 完成状态：**completed**

## 1. 交付文件清单

| 文件 | 大小 | 说明 |
|---|---|---|
| `dependency-map.png` | 348,463 字节 | 1600×1000，服务真实响应的原始 PNG 字节，未做任何后处理 |
| `dependency-map.snapshot` | 194,817 字节 | 与 PNG 同名的完整 DSL；与 `tmp/.../A06/build-a06.snapshot` 的 SHA-256 前 16 位一致（`13b6f7f47932426b`） |
| `graph-audit.json` | 20,949 字节 | 拓扑层、邻居、最长先决路径、反馈边图内表示位置等核验数据 |
| `snapshot-usage.md` | 本文件 | 使用报告 + 逐条自检表 |
| `task-metrics.json` | 由 `wrapup.wrapup()` 写入 | 任务指标 |

过程文件（未清理、未覆盖）：`tmp/20261004-182918/A06/build_a06.py`、`build-a06.snapshot`、
`requests.jsonl`、`iterations.jsonl`、`responses/resp-A06-req-001-dba7dc-att1.txt`（400 错误响应）、
`crops/` 下 12 张放大核对图。

## 2. 文档与 DSL 实际应用

- `_suite/DSL-HANDBOOK.md`（A01–A05 实测结论）——本题全程照此执行。
- `_suite/docs/ai-guide.md`（run 级缓存的真实抓取结果）+ `_suite/docs/openapi.yaml`——确认
  请求体为 UTF-8 纯文本 DSL、错误响应含 `code/message/requestId`、8 位 hex 的 alpha 在末两位。
- 字体：只用了手册第 1 节列出并经真实 `GET /fonts` 确认过的字体族。
  拉丁+中文混排用 `Inter,Noto Sans CJK SC`，等宽数字用 `DejaVu Sans Mono`（图例里没有用）。
  **未臆造任何字体名、标签、属性或枚举值。**
- 用到的 DSL 能力：`<Snapshot type background>` → `<Container width height>` → `<Stack fit="EXPAND">`
  → `Positioned(left top width height)` → `Container`（`color` / `borderRadius` / `border="2 SOLID #…"`
  / `boxShadow` / 四角 `borderRadiusTopLeft…`）与 `Text`（`fontSize` / `fontFamily` / `textAlign` /
  `fontStyle="BOLD"` / `text` 属性）。
- 几何全部由脚本计算后写进绝对坐标：线段 = 一串小矩形；虚线 = 一串短矩形 + 转角实心方块；
  箭头 = 逐行收缩的三角形矩形（`tri_down` / `tri_right` / `tri_left`）。
  **没有用 `<Image>`，没有任何外部图片或外部绘图库。**

## 3. 布局与设计选择（为什么这么画）

1. **纵向（自上而下）分层，而不是横向。** 11 个拓扑层横向排需要 11 列 × 约 175px＝1925px，
   超出 1600px 画布。纵向每层 60px（节点 36px + 层间 24px），11 层正好 636px。
2. **先决边全部严格向下**，层号 = 最长路径分层。任何一条 `solid_edges` 的起点层号都小于终点层号，
   脚本用 `assert` 强制校验，因此不存在"指向过去层"的布局歧义。
3. **并行用三重手段表达**：层带（交替底色 + 行分隔线）、左侧 `L1…L11` 沟槽标签、右侧「拓扑分层」面板
   （含 `×2` 并行标记）。L2/L3/L4 是并行层。
4. **同源/同汇分端口出线**，刻意把整图安排成**零几何交叉**，因此"交叉线无连接点不构成新依赖"
   这条约定只需要在图例里声明成立，不会出现真的交叉线造成误读（并且 `graph-audit.json` 里
   `geometric_crossings` 明确为空）。
5. **侧边绕行**（对应"用侧边弯折/线段绕行减少线压文字"）：
   - `N04 → N13`（直接校验，跨 7 层）从 N04 **左侧**出图，沿**左侧边距通道 x=160** 下行到 L10 行高，
     再右折从 N13 左侧进入。整图最左节点边框在 x=330，所以这条通道不压任何节点文字。
   - `F1 N09→N08` 走**右侧**通道 x=950（从 N09 右侧出 → 上行 → 从 N08 右侧进入，箭头朝左）。
   - `F2 N10→N08` 走**左侧**通道 x=560（从 N10 左侧出 → 上行两级 → 从 N08 左侧进入，箭头朝右）。
     两条反馈分居两侧，从几何上就不可能互相穿越，也不可能与实线主干穿越。
6. **反馈边的视觉隔离**：红色 `#DC2626`、虚线、独立的 `F1/F2` 胶囊标签 + 引线 + 页脚两张专用说明卡，
   与实线 `#334155` 在颜色、线型、端点样式（虚线端点用红圆点）三方面都不同，不可能被误读为先决依赖。
7. **每个边的起点画实心圆点**（18 个），配合图例"圆点＝边的起点端点"，让"有连接点才算依赖"可见。

## 4. 渲染与视觉迭代记录（真实过程）

| 版本 | 请求 | 类型 | 看了什么 | 发现的问题 | 改了什么 |
|---|---|---|---|---|---|
| — | `A06-req-001` | syntax-fix（无图） | — | `400 PARSE_ERROR: Attr [color] color must be #RGB, #RGBA, #RRGGBB or #RRGGBBAA`（第 3 阶段底色写成了 10 位 `#ECFDF5FFFF`） | 改成 `#ECFDF5FF`（8 位 = `#RRGGBBAA`） |
| `A06-v01` | `A06-req-002` | baseline | 整图 | ① 箭头三角形画反了：宽端在尖端，竖边上的箭头看起来像"菱形"而不是箭头；② F1/F2 两个红色箭头都指向 N08 左侧、只差 12px，糊成一团；③ "直接校验"标签的引线从文字中间穿过，像删除线；④ 左侧沟槽底色比 L11 少 24px；⑤ 图例一行占了 1499px，和右侧说明块重叠 | —（基线） |
| `A06-v02` | `A06-req-003` | visual | 整图 + 2.6× `n08-feedback` + 2.6× `direct-verify-label` + 2.6× `n06-converge` + 3.0× `direct-label` + 3.0× `f1-loop` + 2.8× `n13-arrive` | 放大后确认：箭头已正确指向；F1/F2 已分开。但 `n13-arrive` 看到 `N04→N13` 的箭头尖端停在 x=1119，离 N13 左边框 1130 还差 11px（路线点没画到边框）；`direct-label` 看到"直接校验"的引线仍像破折号 | `tri_down`/`tri_right` 改为宽端在基部并新增 `tri_left`；F1 改走右侧通道、F2 改走左侧通道；引线与文字拉开 8px 并加长；沟槽高度 636；图例拆成两行 |
| `A06-v03` | `A06-req-004` | visual | 整图 + 1.6× `header` + 2.2× `n01-fork` + 2.6× `layer-panel` + 1.6× `footer` | `layer-panel` 放大后看到"11 节点 / 10 边"的字形底部越过面板下边框 2px；`footer` 里圆点图例太小，看不清 | 长边路线末端延到 x=1130；脚注第 2 行补上边距通道说明；拓扑面板高度 372→384；圆点图例 r 3.4→5 |
| `A06-v04` | `A06-req-005` | visual | 3.0× `direct-label2` + 3.0× `panel-bottom` + 整图 | 全部通过：面板底边留白正常、引线与文字分离清晰、18 个箭头方向全部正确、无文字溢出 | 无需再改 → accepted |
| `A06-v05` | `A06-req-006` | provenance re-render | 整图（最终交付图复核） | 与 v04 的 DSL 字节完全一致（同一 SHA-256 `13b6f7f47932426b`），画面相同；此请求只是为了把审计 JSON 里原先写死的 `arrow_direction` / 拓扑检查改成真实计算值 | 仅 Python 侧 JSON 字段，DSL 未变 |

计数口径（与 `iterations.jsonl` 一致）：

- 渲染请求总数：**6**（成功 5、失败 1、重试 0、429/503 排队 0）
- 看图次数：**16** 次（整图 5 次 + 放大裁切 11 次；其中 `crops/dependency-map-direct-verify-label.png`
  是一次坐标参数写错后补生成的裁切，未单独查看，后续由 `direct-label` / `direct-label2` 取代）
- 完整视觉迭代：**3** 次（`A06-v02`、`A06-v03`、`A06-v04`，每次都是"看旧图 → 改生成脚本 → 重渲染 → 再看并比较"）
- `A06-v01` 是基线（生成并首次查看，不算迭代）；`A06-v05` DSL 与 v04 逐字节相同，
  只用于把交付图绑定到"产出计算版审计 JSON"的那次运行，因此**记为已查看但不计入新的视觉迭代**；
  `A06-v00` 只有一次 400 语法失败、没有图像。
- 脚本打印的 `D.warnings()`：**6 次请求全部一次告警都没有**。文字框宽度全部由 `D.est_width()`
  计算后再留余量，且节点字号 22、注释字号 ≥18 的框高均按 `fontSize*1.2` 以上给足，
  因此没有出现"文字放不下被静默丢弃"。
- 时间戳来源（全部取自真实日志，无估算）：`task_started_at` = `_suite/events.jsonl` 里 A06 的第一条
  `task_started` 事件 `2026-10-04T20:18:41.749+08:00`（生成脚本每次运行都会重新调用
  `state.start_task`，所以 `suite-state.json` 里的 `started_at` 指针显示的是最后一次运行，不是首次）；
  `first_usable_image_at` = `A06-req-002` 的 `started_at` `2026-10-04T20:20:21.343+08:00`
  （req-002 是第一个返回 `Content-Type: image/png` 的请求）；每个版本的 `viewed_at` 等于该版本渲染请求
  在 `requests.jsonl` 里的 `ended_at`（图像字节可被打开查看的时刻）；
  `task_ended_at` = 写完报告与套件收尾时的真实时刻。墙钟合计与请求耗时之和分别记录在
  `task-metrics.json`，两者不可互相替代。

## 5. 遇到的服务错误与修复

| 请求 | 状态 | 错误 | 修复 |
|---|---|---|---|
| `A06-req-001` | 400 | `PARSE_ERROR: Attr [color] color must be #RGB, #RGBA, #RRGGBB or #RRGGBBAA at position 187057` | 第 3 阶段（校验与交付）节点底色写成了 `#ECFDF5FFFF`（10 位）。改为 `#ECFDF5FF` 后 200。原始错误体保存在 `tmp/20261004-182918/A06/responses/resp-A06-req-001-dba7dc-att1.txt` |

其余请求全部 200 / `image/png`。**未遇到 403、429、503、413、401。**
另有两类**本地**错误（不算服务错误）：
`crop.py` 的坐标参数按 `(left, upper, right, lower)` 解释，我最初按文档里的 `x,y,w,h` 传，
导致 2 次 `PIL ValueError`，改正后正常；以及 `build_a06.py` 早期的两个 Python 断言/解包错误
（分层字典未初始化、记忆化返回值类型），在发出任何请求前就已修正。

## 6. 逐条自检表（对照 TASK.md）

| # | TASK.md 要求 | 满足 | 证据 / 位置 |
|---|---|---|---|
| 1 | 依据 `inputs/graph.json` | ✅ | 脚本直接读该文件；节点/边全部来自数据，未手写 |
| 2 | 尺寸 1600×1000 | ✅ | `dependency-map.png` 实测 `PNG (1600, 1000) RGBA`；画布由根 `Container width=1600 height=1000` 决定 |
| 3 | `solid_edges` 是有向先决依赖 | ✅ | 16 条全部实线 `#334155` + 箭头 + 起点圆点 |
| 4 | `feedback_edges` 不参与 DAG 排序 | ✅ | 分层函数只喂 `SOLID`；`graph-audit.json → topological_layers.method` 写明；图内脚卡明写"虚线…不参与 DAG 拓扑排序" |
| 5 | 14 个节点的编号与标签完整出现 | ✅ | 整图 14 个圆角卡片，`N01 需求冻结` … `N14 交付归档`，编号+中文标签同框 |
| 6 | 每条边方向可辨 | ✅ | 18 个箭头（16 实线 + 2 虚线），逐条放大核对过尖端朝向 |
| 7 | 反馈边用虚线 | ✅ | `dash_h`/`dash_v` 短矩形拼接，`11/8` 虚线节奏，红色 |
| 8 | 反馈边有专用图例 | ✅ | 图例第 1 行第 2 项"虚线＝反馈回路（不参与 DAG 排序）"（红色虚线样本） |
| 9 | 反馈边不能画成普通先决依赖 | ✅ | 颜色/线型/端点三点区分 + `F1`/`F2` 编号 + 页脚两张专用说明卡 |
| 10 | 交叉线无连接点不构成新依赖 | ✅ | 全图零几何交叉（分端口出线）；图例明确写出该约定；`geometric_crossings: []` |
| 11 | 节点位置体现先后 | ✅ | 纵向 11 层，严格自上而下 |
| 12 | 节点位置体现并行 | ✅ | L2/L3/L4 同层并排（`N02/N03`、`N04/N05`、`N06/N07`），层带 + 沟槽标签 + 面板 `×2` |
| 13 | 用侧边弯折/线段绕行减少线压文字 | ✅ | `N04→N13` 走 x=160 左侧边距通道；F1 走 x=950 右侧通道；F2 走 x=560 左侧通道 |
| 14 | 先决边不能出现指向过去层的布局歧义 | ✅ | 脚本 `assert layer_of[a] < layer_of[b]` 对 16 条边逐条通过；`no_prerequisite_edge_points_into_an_earlier_layer: true` |
| 15 | 图内解释"失败后回到构建" | ✅ | `F1` 胶囊标签"F1 · 失败后回到构建"（图内右侧）+ 页脚卡①"① 失败后回到构建（F1：N09 → N08）"三行说明 |
| 16 | 图内解释"检查发现问题后修复" | ✅ | `F2` 胶囊标签"F2 · 检查发现问题后修复"（图内左侧）+ 页脚卡②"② 检查发现问题后修复（F2：N10 → N08）"三行说明 |
| 17 | 节点字号 ≥22 | ✅ | 14 个节点文字统一 `fontSize="22"` |
| 18 | 注释字号 ≥18 | ✅ | 最小字号就是 18（层标签、图例、页脚卡正文、说明、脚注、面板 `×N`）；只有主标题 30、页脚卡标题 22、面板标题 20 更大 |
| 19 | 不能把 14 条文字当成无连接的列表 | ✅ | 14 个卡片 + 18 条带箭头的有向边 + 层号 + 拓扑面板，不存在无连接的文字条目 |
| 20 | 附 `graph-audit.json`：先决关系的拓扑层 | ✅ | `topological_layers.layers`（L1–L11，每层成员/标签/并行数）+ `layer_of_node` |
| 21 | 每节点入/出邻居 | ✅ | `node_neighbors` 逐节点给出 `prerequisite_in/out`（含度数）与 `feedback_in/out` |
| 22 | 最长先决路径（按节点数，至少一条） | ✅ | `longest_prerequisite_path`：11 个节点 / 10 条边，并把全部 **2** 条等长解都列出 |
| 23 | 每条反馈边在图中的表示位置 | ✅ | `feedback_edges[].image_representation`：`polyline_points_px`、`arrow_tip_px`、`arrow_direction`、`side_channel_x_px`、`inline_label_bbox_px`、`leader_line_px`、`explanation_card_in_footer` |
| 24 | 同时交付 `snapshot-usage.md` / `task-metrics.json` | ✅ | 本文件 + `wrapup.wrapup()` 生成的 `task-metrics.json` |
| 25 | 过程日志在临时目录 | ✅ | `requests.jsonl`（6 条，含 400 失败）、`iterations.jsonl`、`responses/`、`crops/`、脚本与草稿 DSL |
| 26 | 最终 PNG 须为服务真实响应 | ✅ | 6 次请求的响应体原样落盘，无裁剪/重编码/调色；`Content-Type: image/png` |
| 27 | 同名 `.snapshot` | ✅ | `dependency-map.snapshot`，与最终渲染所用 DSL 字节一致 |
| 28 | 主体/文字/几何全部 DSL 构造 | ✅ | 1,364 个 `Positioned` 元素全部由 Python 计算坐标后写成 DSL；无 `<Image>`、无外部素材 |
| 29 | 只用 `POST /snapshot` 出图且带 User-Agent | ✅ | `_suite/snapkit.py` 固定 `https://open-snapshot.muedsa.com/snapshot` + 浏览器 UA；本题未发起其他出图请求 |
| 30 | token / 费用等平台未提供的计量 | ✅ | `task-metrics.json` 中 `input_tokens / output_tokens / image_input_usage / cost / currency` 全部 `null`，并注明来源与"未用字符数估算" |

## 7. 未解决事项 / 已知限制

1. **线与箭头是"短矩形拼接"而不是矢量图元。** 该 class-DOM DSL 没有画线/画路径图元（手册第 4 节已记录），
   所以斜线在 4.5px 步长下、最陡处（`N06→N08`，380px 横向 / 24px 纵向）放大到 2.6× 时能看到轻微阶梯。
   这不影响任何方向、端点、层号或计数的结论。推测原因：服务端未暴露 `CustomPaint` / path 类标签
   （我按手册列出的能力清单使用，未臆造标签）。
2. **箭头尖端是"逐行收缩的矩形堆"**，不是真正的三角形；在 3× 放大下斜边有约 1px 的台阶。
   同上，属于同一限制。
3. **跨行斜边的箭头方向是按"进入目标节点上边框的垂直向下箭头"处理的**，
   也就是说 `N03→N06`、`N05→N06`、`N12→N13` 这类浅斜线在接近目标时会有一个很小的折角。
   我选择这样做而不是旋转三角形，是因为手册只记录了 `Transform` + `matrix` 的一种用法，
   在没有对照探针图验证 `origin`/`alignment` 语义之前不冒险（手册第 3 节：看起来没生效的地方要用探针图证明）。
   这个折角不影响方向判读——箭头尖端落在目标节点边框上，且实线主干方向自上而下。
4. **N04→N13 的"直接校验：数据不经过渲染回路"标签放在左侧边距通道旁（x=234, y=470）**，
   而不是贴在 N13 旁边。取舍理由：N13 右侧/下方空间被 `N13→N14` 与层带占满，
   放在通道旁能让"这条边是绕行过来的"这一点更直观。
5. **平台未提供的计量**（token、图像输入量、费用、服务端排队时长）无法取得，
   `task-metrics.json` 中一律为 `null`，未做任何估算。
6. 未遇到 429 / 503 / 限流，因此 `rate_limit_or_queue_wait_seconds` 记为 `null`（不能确认为 0）。

## 8. 质量与消耗分开说明

- **质量**：16 次放大/整图查看后确认——14 节点齐全、18 条边方向全部正确、零几何交叉、
  无文字溢出或压字、反馈边在颜色/线型/端点/图例/编号/说明卡六个维度上都与先决依赖区分开。
- **消耗**：渲染请求 6 次（成功 5 / 失败 1）。精确数值全部在 `task-metrics.json` 里
  （`sum_of_request_durations_seconds` ≈ 24 秒，`wall_clock_seconds_total` ≈ 25 分钟，
  `wall_clock_seconds_to_first_usable_image` ≈ 100 秒；`task_ended_at` 会随报告收尾时间小幅后移，
  以文件里的值为准）。墙钟远大于请求耗时之和，差额是本地的读文档、写 DSL、看图、改脚本与写报告时间，
  两者不可互相替代。服务端未返回任何 token / 计费信息，也未返回 `Server-Timing` 排队段，故
  `input_tokens / output_tokens / image_input_usage / cost / currency /
  rate_limit_or_queue_wait_seconds` 一律为 `null`，未做任何估算。
