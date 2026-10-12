# A06 使用说明与自检报告 · 十四节点依赖图与反馈回路

- 任务：`tasks/A06-dependency-graph/TASK.md`（依据 `inputs/graph.json` 的 1600×1000 依赖解释图）
- run_id：`20261008T1615Z-run01`；输出 `outputs/20261008T1615Z-run01/A06/`；
  过程 `tmp/20261008T1615Z-run01/A06/`（路径基准：总任务根，`path_base=suite_root`）
- 状态：**completed**。停止依据：14 节点/18 条边全部按输入实际渲染并可辨方向，
  完成 v02–v06 整图 5 次实际看图＋10 组 2× 局部放大，像素自检全绿。

## 1. 交付清单

| 文件 | 说明 |
|---|---|
| `dependency-map.png` | 服务真实响应，1600×1000 RGBA，301,083 B，sha256 `a1aacea529627e90894e7f0c56ae7681c15d5ca09953fd59239cdfb106a3ac5c` |
| `dependency-map.snapshot` | 与上图同一份完整 DSL（50,906 B，223 个 `Positioned`），由 `v06.snapshot` 原样复制，`cmp` 验证字节一致 |
| `graph-audit.json` | 拓扑层、每节点入/出邻居、最长先决路径（含全部等长解）、每条反馈边在图中的表示位置、节点/边几何、交叉分析、阶段分组、字号下限 |
| `dependency-map-geom.json` | 像素自检结果（尺寸、32px 安全环、阶段色条、16+2 个箭头窗口、面板 halo、节点标签墨量） |
| `snapshot-usage.md` / `task-metrics.json` | 本报告与统计 |

过程留痕：`tmp/<run_id>/A06/requests.jsonl`（7 次渲染请求，含 1 次 400 失败）、
`iterations.jsonl`（v01–v06）、`v01..v06.snapshot`、
`requests/A06-*.body.txt/.response-headers.txt/.response.bin`（原始响应字节，失败响应
为 JSON 未当作图片保存）、`preview/v01..v06.png`（v01 因 400 未出图，故预览从 v02 起）、
`preview/v03-c1..c4.png`、`preview/v04-c1..c6.png`（共 10 组 2× 放大，仅供观察，未参与交付）、
`crop-*.snapshot`（1:1 裁切 DSL 草稿，保留未渲染）、`generate_a06.py`、
`check_geom_a06.py`、`fit-report.json`、`geom-report.json`。
运行时缓存（`__pycache__/`）按总根 `.gitignore` 排除，不作为证据。

## 2. 需求逐条对照（依据实际图像）

| TASK.md 要求 | 实现与证据 |
|---|---|
| 1600×1000“从需求到可复现交付”依赖解释图 | PIL 实测 `(1600, 1000)`；标题“从需求到可复现交付 · 14 节点依赖与反馈回路” |
| 依据 inputs/graph.json，不增删节点与边 | 生成器直接读取该文件，`node_count=14 / solid_edge_count=16 / feedback_edge_count=2` 与输入一致；图中 14 个节点框、16 条实线、2 条虚线 |
| 14 节点编号与标签完整出现 | `id.NXX` 22px 编号 + `label.NXX` 24px 中文标签；自检“节点标签墨量 ≥200 px”14/14 通过，放大图逐字可读 |
| 每条边的方向可辨 | v03 发现箭头倒钩被画进目标节点内部而完全不可见；v04 改为逆行进方向画倒钩＋折线端点吸附节点边框，`arrowhead_windows` 16/16、`feedback_arrowheads` 2/2 均检出墨迹 |
| solid_edges 为有向先决依赖 | 浅蓝实线＋箭头，图例第 1 项标注“有向先决依赖（16 条）” |
| feedback_edges 另外标明、不参与 DAG 排序 | 粉色 3px 虚线（dash 11/8），图例第 2 项“反馈关系（2 条，不参与 DAG 排序）”；`analyse()` 只用 solid 边做 Kahn 分层，`graph-audit.json` 中 `excluded_from_dag=true` |
| 不能把反馈边画成普通先决依赖 | 颜色、线宽、虚实、箭头与图例四处均与普通边不同；两条反馈边各带 ①② 图内标注 |
| 交叉线无连接点时不构成新依赖 | `crossing_report()` 对 18 条折线做两两线段相交测试：**0 次交叉**（v04 起改用吸附后的真实折线复测）；图例第 3 项说明“交叉无圆点＝不相交依赖”，第 4 项说明本图未画任何圆点连接标记 |
| 节点位置体现先后与并行 | 横向＝拓扑层 L0…L10（Kahn 最长路径分层），L1(N02/N03)、L2(N05/N04)、L3(N06/N07) 上下并排表示可并行；`topological_layers` 与 `parallelism` 记录 |
| 用侧边弯折/线段绕行减少线压文字 | 折线走专用车道：上层弯折 328/352，反馈车道 330/300，N04→N13 走 640 底部绕行；放大检查未发现线压字 |
| 先决边不能出现指向过去层的布局歧义 | `analyse()` 断言 16 条边全部满足 `layer(源) < layer(目标)`，`layer_monotonicity` 记录 `checked=16, violations=[], pass=true`；图面所有实线一律自左向右 |
| 图内解释“失败后回到构建” | 左卡片原文说明 N09 渲染失败沿 ① 粉色虚线回 N08 重建，且强调虚线不是新的先决条件 |
| 图内解释“检查发现问题后修复” | 右卡片说明常规路径 N10→N11→N12 与问题出在 DSL 时沿 ② 虚线直接回 N08 |
| 节点字号≥22、注释≥18 | 编号 22、标签 24、卡片/图例/审计 20、层带与反馈标注 18；`text_minimums` 记录并附实测依据 |
| 不允许把 14 条文字当作无连接关系的列表 | 14 个节点全部由 18 条带方向的边连接成一张 DAG＋2 回路，非列表排版 |
| 附 graph-audit.json | 已交付；含 `topological_layers`、`in_neighbours`/`out_neighbours`（反馈邻居单列 `feedback_neighbours`）、`longest_prerequisite_path`（11 个节点、2 条等长解全部给出）、`feedback_edges_in_image`（虚线样式、折线点、车道 y、进入 N08 顶边 x、图例条目、标注框位置） |
| 指定 PNG 是服务真实响应且有同名 DSL | `dependency-map.png` 为 `A06-v06-final-20261008T110555Z` 响应字节；`dependency-map.snapshot` 与其 DSL 同源，`cmp` 通过 |

## 3. 文档与 DSL 能力的实际使用

- 阅读 `tmp/<run_id>/_suite/docs/`（shared 抓取，12 次请求，已缓存复用）中的
  `parser.html`、`concepts.html`、`text.html`、`container.html`、`stack.html`、
  `positioned.html`、`transform.html` 等；本题新用到的是 **parser 的文本特殊字符规则**。
- **新实测结论（已写入 `_suite/notes/dsl-findings.md`）**：
  1. 解析器**不做 HTML 实体解码**，`Text` 内出现 `<` / `>` 会直接触发
     `PARSE_ERROR`（v01 的 400 即此因，报错位置 47565 指向审计行）。按文档改用
     `<![CDATA[...]]>` 后 HTTP 200。已在共享 `dslkit.esc()` 内自动处理。
  2. 服务端缓存：v06 渲染 `render;dur=584.3`，同一 DSL 的最终交付渲染返回
     `cache;desc=hit, total;dur=251.3`，字节与预览一致。
- 复用既有结论：`Transform matrix=… alignment="TOP_LEFT"` 画任意角度线段（A05 探针）；
  文本被 `Positioned`/`Container` 盒裁切、行距≈1.45×fontSize（A04/A05）；
  8 位十六进制＝`#RRGGBBAA`；未知属性被静默忽略（因此所有属性都逐字核对文档）。

## 4. 渲染前门禁与渲染后自检（可复用做法）

1. **fit 门禁**：61 个文本盒全部按“估算字宽→换行→所需高度”校验，并对估算值再留 4%
   余量；任一盒不合格就不产出 DSL。本题在 v02 看图后据此发现图例被裁切，
   并把图例改为“按实测宽度顺序排版”，交付时违规 0。
2. **几何同源**：节点框、折线锚点、车道与审计 JSON 全部来自同一张坐标表
   （`box()` / `anchored()` / `GEOM`），图与 `graph-audit.json` 不可能互相矛盾。
3. **像素自检** `check_geom_a06.py`：画布尺寸/模式、32px 安全环墨迹计数、
   14 条阶段色条命中、16 个先决边箭头窗口＋2 个反馈箭头窗口的粉色墨迹、
   4 个面板的 halo、14 个节点标签墨量。交付值：ring 0、halo 0、全部窗口有墨。
   v05→v06 就是靠它发现 L0 背景带左缘 x=26 越出安全边距（2,985 个像素）。

## 5. 踩坑记录

| 现象 | 根因 | 处理 |
|---|---|---|
| v01 返回 400 PARSE_ERROR | 审计行含 `<`，parser 不解实体 | `esc()` 自动 CDATA 包裹，重出 v02 |
| 图例文字被裁成“不参与 DAG 排” | 字宽估算无余量、盒宽写死 330 | 估算加 4% 余量；图例改实测宽度顺序排版并加越界断言 |
| 16 条边全部看不出方向 | 箭头倒钩沿行进方向画，落进目标节点内被后画的节点覆盖；折线末端还伸进框内 14px | 倒钩反向；新增 `anchored()` 把两端吸附到节点真实边框 |
| 节点顶部色条、卡片左侧强调条在圆角处外凸 | 直角色条压在 `borderRadius=12` 的盒外 | 色条按圆角半径内缩 12px |
| 自检误报 legend halo 1484 像素 | halo 窗口 6px 与 6px 外的相邻卡片边框重叠 | 窗口收紧到 3px，并保留相邻面板间距≥6px 的约束 |
| 阶段配色无说明 | 只用了颜色没有图例 | 顶部新增 5 项阶段图例（含节点计数），并写入审计 `phases` |

## 6. 统计

见 `task-metrics.json`。摘要：7 次 `/snapshot` 渲染请求（1 次 400 语法失败、
6 次 200，其中 1 次为同一 DSL 的最终交付渲染且服务端缓存命中），6 个 DSL 版本，
1 次语法修复 + 4 轮完整视觉迭代，5 次整图实际看图 + 10 组 2× 局部放大，
请求耗时合计 42.313 s（不含 shared 文档抓取 28.078 s）。
