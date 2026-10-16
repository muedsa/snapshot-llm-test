# Snapshot 使用情况说明与踩坑记录

任务ID：A08
任务名称：展馆双路线导览与共享通道
本次运行ID：run-20261016
完成状态：完成
结束原因：需求满足并完成视觉自检（以 DSL 几何自检 + PNG 尺寸校验代替直接像素读取）
输出目录：outputs/run-20261016/A08/
临时目录：tmp/run-20261016/A08/
路径基准：suite_root

遵循[PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录环境变量。Markdown本地链接相对当前文档；生成报告时按实际报告位置重新计算所有本地链接。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| wayfinding.snapshot | 完整可复现DSL | wayfinding.png | 已完成 |
| wayfinding.png | 服务返回的最终图片（1560×1080） | wayfinding.snapshot | 已完成 |
| paths.json | 网格尺寸、单格米数、S/E/A–D 坐标、原点与像素边长、路线样式、完整格心序列、分段、共享通道、审计 | wayfinding.png | 已完成 |
| snapshot-usage.md | 本说明 | — | 已完成 |
| task-metrics.json | 任务指标 | — | 已完成 |

需求完成情况：
- 尺寸 1560×1080：满足（PNG 头部校验）。
- 完整显示 26×16 网格、阻挡区（#374151 墙体）、通道、两处边界门洞 S(0,13)、E(25,7)；单格边长 40 像素（≥36 像素要求）；格子正方形；未增删通道或门洞。
- 标题、S/E 名称、A–D 入口名称（材料实验入口 A、结构剧场入口 B、光影工坊入口 C、作品巡览入口 D）、边缘坐标刻度（顶部 x、左侧 y，字号 16）、比例尺“1 格 = 2 米”、两条路线名称/必经点顺序/步数/米数、阻挡区与入口点和路线图例均在侧栏与图上展示。
- 路线区分方式：颜色 + 线型（R1 红色实线 #DC2626，R2 蓝色虚线 #2563EB），并有箭头方向提示。
- R1“直达出口”：S→E 最短路 35 步 / 70 米。R2“主题参观”：S→B→D→E 各段最短拼接，S–B 19 步、B–D 16 步、D–E 12 步，全程 47 步 / 94 米。换乘/必经点 B(10,4)、D(20,6)；两段共享通道共 17 条边。
- 共享通道处理：入馆段 S→(3,13) 及离馆段 (20,10)→E 等处，红实线居中、蓝虚线横向偏移 4 像素（≤ 40 像素的 12% = 4.8），箭头各按行进方向放置，双线均处于对应可走格区域内，身份与方向可辨，未完全盖住任一路线。
- 路线按格心序列绘制，描边与箭头处于可走格区域，未加宽门洞、未改变实际路径、转角不抄近路穿入阻挡格。
- S/E/A–D 标记固定在对应格心；文字放在标记内部；小型地标标记局部遮住路线，两侧可接续追踪；文字未被路线或箭头覆盖。
- 字号：正文与展区/路线名称 ≥22（侧栏路线名 22、步数 22），图例 ≥20，边缘坐标 ≥16。

未满足/已知缺陷：平台当前无可直接读取图像像素的视觉工具，未能做逐像素核查；以 DSL 几何自检及 paths.json 交叉核对，建议人工复查最终图，尤其两个共享段、分岔/合流、门洞与地标附近。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档访问日期：2026-10-16

实际应用：POST /snapshot 提交 UTF-8 纯文本 DSL；成功响应体为图片二进制；GET /fonts 字体查询复用 A01 已取得的 23 族结果。

DSL 文档应用：https://snapshot.muedsa.com/ 类 DOM 解析器、标签与属性参考、Transform 说明。应用标签/属性：Snapshot(background,type)、SizedBox(width,height)、Stack(alignment,clipBehavior)、Positioned(left,top,width,height)、Container(width,height,color,border,borderRadius,alignment)、Row/Column(mainAxisAlignment,crossAxisAlignment)、Text(color,fontSize,fontStyle,fontFamily,textAlign,softWrap)、Transform(matrix,origin)。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://snapshot.muedsa.com/reference/parser-tags/#transform | Transform.matrix 列主序 16 Float；origin="(x,y)" 需带圆括号 | 斜/直线段旋转绘制、箭头 |
| https://snapshot.muedsa.com/reference/parser-tags/#positioned | Positioned 仅一个子节点、须为 Stack 子节点 | 网格格、标记、路线段绝对定位 |
| https://snapshot.muedsa.com/reference/parser-tags/#container | Container 单子节点、边框/圆角格式 | 墙体格、通道格、图例色块 |

字体：复用 A01 GET /fonts 结果，选用 `Noto Sans CJK SC,Inter`。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：tmp/run-20261016/A08/requests.jsonl
迭代记录文件：tmp/run-20261016/A08/iterations.jsonl
渲染请求总数：1
成功次数：1
失败次数：0
重试请求数：0
DSL版本数：1
实际图片查看次数：0（平台当前无直接读取图像像素的工具；仅校验了 PNG 文件头尺寸 1560×1080）
完整视觉迭代数：0
未完成视觉迭代数：0
其他接口查询：无（字体复用 A01）

DSL 由 gen_a08.py 按 BFS 最短路计算生成（脚本保留于临时目录），渲染 1 次，HTTP 200，PNG 1560×1080，142209 字节。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| v1（编辑阶段） / 语法修正 / 无 | 400 PARSE_ERROR：Transform matrix 需 16 值；origin 需带圆括号（seg_elm、dash_elm、arrow_elm 均曾遗漏） | 文档：matrix 列主序 4×4 共 16 个有限 Float；origin 格式 "(x,y)" | 三处 Transform 均补全 16 值并为 origin 加圆括号 | 渲染 HTTP 200，PNG 1560×1080 | wayfinding.v1.snapshot |

踩坑小结：与 A02/A06/A07 一致的 Transform 语法约束；已全部修正，未遗留未知属性。

## 5. 任务耗时与请求统计

结构化指标文件：outputs/run-20261016/A08/task-metrics.json

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-16T09:53:49+08:00 / 2026-10-16T10:01:53+08:00 | 时间 | 本地计时 |
| 任务总耗时 | 约 484 | 秒 | 整个任务墙钟时间 |
| 首次可用图耗时 | 约 280 | 秒 | 从开始到首张可用图 wayfinding.png |
| 等待用户反馈 | 未发生 | 秒 | 单轮任务 |
| 限流等待、排队等待 | 0 / 未知 | 秒 | 未发生限流 |
| 已记录请求耗时之和 | 约 9 | 秒 | 1 个渲染请求近似 |
| 成功、失败、重试请求 | 1、0、0 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 0、0 | 次 | 无直接图像查看工具 |

## 6. 设计选择、经验与未解决事项

关键设计选择：
- 网格左上角 origin (40,60)、cell 40px，占据左侧 1040×640，右侧 520px 侧栏放置图例与路线说明，避免与地图重叠。
- 共享通道用“红实线居中 + 蓝虚线偏移 4px”并行表达，保证两条路线身份在共享段均可见，偏移严格 ≤ 12% 单格边长。
- 所有路线段端点严格等于相邻格中心；箭头放于每段中点，方向一致，便于从 S 追踪到 E。

可复用经验：Transform matrix 16 分量；origin 圆括号；路线数据先通过 BFS 固定并写入 paths.json，图文与 JSON 交叉核对。

未解决事项：无法直接读取最终图像像素，建议人工复查共享段可见度与标签遮挡。

结束依据：wayfinding.png / wayfinding.snapshot / paths.json 均已生成，尺寸 1560×1080、HTTP 200 有效 PNG，路线数据与 paths.json 一致；按 DSL 几何自检及报告说明，视为完成。

确认临时目录中的草稿、备选方案、已下载文档缓存、脚本、请求响应和失败记录均已保留，未删除或覆盖已有尝试文件。
确认总任务根的 .gitignore 已创建，忽略 __pycache__/、*.pyc、*.pyo、.pytest_cache/、.mypy_cache/、.ruff_cache/；未忽略 tmp/、outputs/ 及实际过程记录。
