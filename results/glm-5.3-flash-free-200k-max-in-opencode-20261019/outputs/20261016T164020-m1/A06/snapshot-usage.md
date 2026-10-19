# A06 · dependency-map（十四节点依赖图与反馈回路）— 使用记录

题面：`tasks/A06-dependency-graph/TASK.md`；数据：`tasks/A06-dependency-graph/inputs/graph.json`（14 节点 / 16 条 solid 先决边 / 2 条 feedback 边，原值使用）。
权威参考：题面字段约定（`tasks/A06-dependency-graph/templates/audit-fields.json`）；DSL 语法为既得知识（A01–A05 已建立，本轮未发起新 HTTP 文档请求）。

## 实际产物（路径基准 = 本题输出根）

| 文件 | 说明 |
| --- | --- |
| `dependency-map.png` | 1600×1000，服务原始 PNG 字节（247,437B，A06-render-0001，200） |
| `dependency-map.snapshot` | 与 PNG 同名的完整 DSL（37,714B） |
| `graph-audit.json` | schema_version 1：topology/nodes（ID·拓扑层·入出邻居·像素盒）/prerequisite_edges（from·to·折线·箭头 ·层校验）/longest_path（11 节点+方法+并列次优）/feedback_edges（折线·箭头·虚线样式·不参与 DAG）/crossings（0 处）/visual_checks（10 条，查看后填写）/draw_layout/tie_break |
| `task-metrics.json` | metrics_dump 生成（elapsed/firstimg 自动计算） |

## DSL/工具应用（承接 A01–A05 模式）

- 结构：`Snapshot(background,type)` → `Stack` → 单 `SizedBox` 画布锚 → 全 `Positioned` 绝对坐标。边线用 `SizedBox+ClipPath(path=d)+Container` 四边形逼近（A05 定案），箭头为同法三角形。
- 混排字体 `fontFamily="Inter,Noto Sans CJK SC"`；颜色 8 位 hex；多行双括弧 padding 特性未再用到（本轮无 CheckBox）。
- 虚线：把折线按 9px 划线/7px 间隔切成短四边形序列实现（无原生 dash 属性，按文档语义无此概念，以图形组合表达）。
- 文本宽度用 estw 估算（WARN 机制阻断渲染）：节点 4 字 22px = 88px，节点盒文字可用宽设计为 98px 通过。

## 布局决策（绘制决策，不改图语义）

- 列 = 拓扑层 L0–L10（最长前驱层法，等价 Kahn；`lay[b] > lay[a]` 断言：N03→N06、N04→N13 为合法跨层先决）。
- 双层行序：L1 上=N03/下=N02、L2 上=N05/下=N04 —— 使 N02→N04 直连、N02→N05 底缘上入、N04→N13 走图底通道。
- 绕行路由：N03→N06 顶部空带（y=252，避开层表头 201 之下、节点顶 284 之上）；N04→N13 图底通道（y=780）。
- 反馈环：N09→N08 走节点上空带（y=350）、N10→N08 走下空带（y=502），分别箭头 D/U 进入 N08 顶/底缘；几何求交 0 处交叉。
- 最长路径并列两条（N04→N07 分支与 N05→N06 分支均 11 节点），审计主取前者（并列取 ID 较大分支的确定性规则），并列事实与次优序列均写入 JSON。

## 踩坑与经验（跨题可迁移）

1. **箭头方向必须与末端行进方向一致**：进入顶缘（自上方来）用 D，进入底缘（自下方来）用 U；`arrow_at(tip,d)` 以 tip 前退 9px 定位三角形，保证箭尖精确落在端口线上。
2. **同层多边靠近同一 y 时**（如 N03 与 N06 同为上排）：让出发段只右行 25px 再立刻上行绕行，可完全避开同排水平边；比斜线直连更清晰。
3. **节点 4 字标签 22px=88px**：盒宽 104 时文字须从 cx-46 起（色条后即起），fit 校验宽度设 98 才能通过；从 cx-30 起会 88px 溢出。
4. **审计如实记录绘制决策**：行序/绕行/并列规则写入 `draw_layout`/`tie_break`，保持"数据原值 + 布局声明"的可复现边界。

## 查看证据

- 整图查看 1 次 + PIL 放大分区 6 张（`tmp/20261016T164020-m1/A06/steps/`：z1_left 左列与顶绕、z2_mid 反馈双环、z3_bottom 底通道、z4_note 说明卡、z5_top 标题图例、z6_n13 底入箭头）。
- 迭代：v01 一次渲染即达标（0 失败请求）；`iterations.jsonl` 记录 recheck=resolved。
