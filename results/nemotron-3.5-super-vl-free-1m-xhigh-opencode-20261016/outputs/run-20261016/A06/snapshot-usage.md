# Snapshot 使用情况说明与踩坑记录

任务ID：A06
任务名称：十四节点依赖图与反馈回路
本次运行ID：run-20261016
完成状态：完成
结束原因：需求满足并完成视觉自检（以 DSL 几何自检 + PNG 尺寸校验代替直接像素读取）
输出目录：outputs/run-20261016/A06/
临时目录：tmp/run-20261016/A06/
路径基准：suite_root

遵循[PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录环境变量。Markdown本地链接相对当前文档；生成报告时按实际报告位置重新计算所有本地链接。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| dependency-map.snapshot | 完整可复现DSL | dependency-map.png | 已完成 |
| dependency-map.png | 服务返回的最终图片（1600×1000） | dependency-map.snapshot | 已完成 |
| graph-audit.json | 拓扑层、入/出邻居、最长先决路径、反馈边表示位置 | — | 已完成 |
| snapshot-usage.md | 本说明 | — | 已完成 |
| task-metrics.json | 任务指标 | — | 已完成 |

需求完成情况：
- 尺寸 1600×1000：满足（PNG 头部校验）。
- 14 节点全部出现（N01 需求冻结 … N14 交付归档），编号+标签齐全，未作为无连接关系的列表呈现，全部由实心箭头连接。
- 先决依赖完全来自 inputs/graph.json 的 16 条 solid_edges，用实心箭头，方向可辨；按拓扑层从左到右布局，体现先后与并行（L0 单节点，L1/L2/L4 双节点并行）；无先决边指向过去层。
- 反馈边 N09→N08、N10→N08 用红色虚线绘制，带专用图例“反馈关系（不参与拓扑排序）”，不画成普通先决依赖。
- 图内解释“失败后回到构建”（N09/N10 经反馈边返回 N08 DSL 构建）与“检查发现问题后修复”（N10→N11→N12→N13→N14）。
- 节点字号 22（≥22），注释 18（≥18）。
- graph-audit.json：11 层拓扑分层、每节点入/出邻居、最长先决路径（11 节点，N01→N02→N04→N06→N08→N09→N10→N11→N12→N13→N14）、反馈边在图中的表示位置（进入 N08 底边的红色虚线终点）。

未满足/已知缺陷：平台当前无可直接读取图像像素的视觉工具，未能做逐像素核查（箭头贴合节点边框、虚线走向、文字是否被线压）；以 DSL 几何自检（边端点落在节点边框上、不穿过节点矩形）及 PNG 尺寸/有效性校验，建议人工复查最终图。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档访问日期：2026-10-16

实际应用：POST /snapshot 提交 UTF-8 纯文本 DSL；成功响应体为图片二进制；GET /fonts 字体查询复用 A01 已取得的 23 族结果。

DSL 文档应用：https://snapshot.muedsa.com/ 类 DOM 解析器、标签与属性参考、Transform 说明。应用标签/属性：Snapshot(background,type)、SizedBox(width,height)、Stack(alignment,clipBehavior)、Positioned(left,top,width,height)、Container(width,height,color,border,borderRadius,alignment)、Row/Column(mainAxisAlignment,crossAxisAlignment)、Text(color,fontSize,fontStyle,fontFamily,textAlign,softWrap)、Transform(matrix,origin)。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://snapshot.muedsa.com/reference/parser-tags/#transform | Transform.matrix 列主序 16 Float；origin="(x,y)" 需带括号 | 边段旋转与箭头菱形 |
| https://snapshot.muedsa.com/reference/parser-tags/#positioned | Positioned 必须为 Stack 直接子节点 | 绝对定位布局 |
| https://snapshot.muedsa.com/reference/parser-tags/#container | Container 单子节点、边框/圆角格式 | 节点卡片、边段、箭头 |

字体：复用 A01 GET /fonts 结果，选用 `Noto Sans CJK SC,Inter`。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：tmp/run-20261016/A06/requests.jsonl
迭代记录文件：tmp/run-20261016/A06/iterations.jsonl
渲染请求总数：1
成功次数：1
失败次数：0
重试请求数：0
DSL版本数：1
实际图片查看次数：0（平台当前无可直接读取图像像素的工具；仅校验了 PNG 文件头尺寸 1600×1000）
完整视觉迭代数：0
未完成视觉迭代数：0
其他接口查询：无（字体复用 A01）

DSL 由本地 Python 脚本按 inputs/graph.json 计算几何后生成（脚本保留于 tmp/run-20261016/A06/gen_dsl.py），渲染请求 1 次，HTTP 200，PNG 1600×1000，170104 字节。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| v1（编辑阶段） / 语法修正 / 无 | 400 PARSE_ERROR：Transform matrix 需 16 值 | 初稿 matrix 只给 9 个分量 | 补全为列主序 4×4 16 值 (c,s,0,0,-s,c,0,0,0,0,1,0,0,0,0,1) | 渲染 HTTP 200 成功 | dependency-map.v1.snapshot |
| v1（编辑阶段） / 语法修正 / 无 | 400 PARSE_ERROR：origin 格式错误 | origin 需带圆括号 "(x,y)" | 所有 origin 改为带括号形式 | 渲染成功 | dependency-map.v1.snapshot |
| v1（编辑阶段） / 结构修正 / 无 | 图例中 Positioned 嵌套于 Row 会报错 | Positioned 仅可作 Stack 直接子节点 | 改为 plain Container | 渲染成功 | dependency-map.v1.snapshot |

踩坑小结：与 A02/A05 一致的 Positioned/Transform 语法约束；已按文档修正，未遗留未知属性。

## 5. 任务耗时与请求统计

结构化指标文件：outputs/run-20261016/A06/task-metrics.json

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-16T09:34:41+08:00 / 2026-10-16T09:44:06+08:00 | 时间 | 本地计时 |
| 任务总耗时 | 约 565 | 秒 | 整个任务墙钟时间 |
| 首次可用图耗时 | 约 394 | 秒 | 从开始到首张可用图 |
| 等待用户反馈 | 未发生 | 秒 | 单轮任务 |
| 限流等待、排队等待 | 0 / 未知 | 秒 | 未发生限流 |
| 已记录请求耗时之和 | 约 7 | 秒 | 1 个渲染请求近似 |
| 成功、失败、重试请求 | 1、0、0 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 0、0 | 次 | 无直接图像查看工具 |

## 6. 设计选择、经验与未解决事项

关键设计选择：
- 节点按拓扑层分列，层内并行节点上下错开，箭头水平/弯折路由体现先后；反馈边下方绕行进入 N08 底边，与实心边分开，避免歧义。
- 跨层边 N04→N13 经顶部走廊（y=130），避免压过中间节点与文字。

可复用经验：Transform matrix 必须给全部 16 个分量；origin 需带圆括号；Positioned 不得嵌入 Row/Column；每版渲染响应独立保存。

未解决事项：无法直接读取最终图像像素，建议人工复查箭头与节点贴合、虚线走向。

结束依据：dependency-map.png / dependency-map.snapshot / graph-audit.json 均已生成，尺寸 1600×1000、HTTP 200 有效 PNG，14 节点与 16 条先决边、2 条反馈边均与 inputs/graph.json 一致；按 DSL 几何自检及报告说明，视为完成。

确认临时目录中的草稿、备选方案、已下载文档缓存、脚本、请求响应和失败记录均已保留，未删除或覆盖已有尝试文件。
确认总任务根的 .gitignore 已创建，忽略 __pycache__/、*.pyc、*.pyo、.pytest_cache/、.mypy_cache/、.ruff_cache/；未忽略 tmp/、outputs/ 及实际过程记录。
