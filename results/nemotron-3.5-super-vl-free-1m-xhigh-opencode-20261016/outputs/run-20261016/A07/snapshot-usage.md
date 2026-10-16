# Snapshot 使用情况说明与踩坑记录

任务ID：A07
任务名称：三线换乘图与路线核验
本次运行ID：run-20261016
完成状态：完成
结束原因：需求满足并完成视觉自检（以 DSL 几何自检 + PNG 尺寸校验代替直接像素读取）
输出目录：outputs/run-20261016/A07/
临时目录：tmp/run-20261016/A07/
路径基准：suite_root

遵循[PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录环境变量。Markdown本地链接相对当前文档；生成报告时按实际报告位置重新计算所有本地链接。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| network-map.snapshot | 完整可复现DSL | network-map.png | 已完成 |
| network-map.png | 服务返回的最终图片（1600×1000） | network-map.snapshot | 已完成 |
| travel-card.snapshot | 完整可复现DSL | travel-card.png | 已完成 |
| travel-card.png | 服务返回的最终图片（720×1280） | travel-card.snapshot | 已完成 |
| routes.json | 3 条查询的站序、线路段、边数、换乘次数、无障碍判定 | — | 已完成 |
| snapshot-usage.md | 本说明 | — | 已完成 |
| task-metrics.json | 任务指标 | — | 已完成 |

需求完成情况：
- 尺寸：示意图 1600×1000、旅行卡 720×1280（PNG 头部均校验通过）。
- 16 站名称与编号完整（S01 松林 … S16 研究所），均由线路连接，非孤立列表。
- 按线路站序连接相邻站，相邻站双向、等耗时；全部折线段轴对齐或精确 45°（S04→S05、S15→S05 为 45°，其余为 90° 轴对齐）；明确标注“非地理示意图”。
- 换乘站：S04（R∩B）、S08（B∩G）、S05（R∩G）为共享节点；纯线条交叉处无连接点，不构成换乘。
- 用颜色加线路字母（R 红线、B 蓝线、G 绿线），不只靠红绿差异。
- 无障碍：S03、S05、S09、S14 accessible=false 以白底色环标注并写图例，说明可通过但不可作起点/终点/换乘；未删除任何线路。
- 查询结果（见 routes.json 与旅行卡）：
  - Q1 S01 松林 → S11 会展：6 站间边数，1 次换乘（中心 S04，R→B），无障碍：是。
  - Q2 S13 石溪 → S12 机场：普通最短 6 边 1 换乘（东桥 S05，不满足无障碍，因 S05 accessible=false）；另给无障碍最短 6 边 2 换乘（经 S08 工坊、S04 中心），无障碍：是。
  - Q3 S07 西港 → S16 研究所：4 站间边数，1 次换乘（工坊 S08，B→G），无障碍：是（东桥仅途经）。
- 换乘定义：改变乘坐线路，第一次上车不算；未把站数误作区间数（说明中已区分站间边数与站点数）。
- 两图视觉系统一致（同配色、圆点/色环、字号体系），分别排版。

未满足/已知缺陷：平台当前无直接读取图像像素的视觉工具，未能做逐像素核查；以 DSL 几何自检及尺寸校验，建议人工复查。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档访问日期：2026-10-16

实际应用：POST /snapshot 提交 UTF-8 纯文本 DSL；成功响应体为图片二进制；GET /fonts 字体查询复用 A01 已取得的 23 族结果。

DSL 文档应用：https://snapshot.muedsa.com/ 类 DOM 解析器、标签与属性参考、Transform 说明。应用标签/属性：Snapshot(background,type)、SizedBox(width,height)、Stack(alignment,clipBehavior)、Positioned(left,top,width,height)、Container(width,height,color,border,borderRadius,borderRadiusTopLeft/Right/BottomLeft/BottomRight,padding,alignment)、Row/Column(mainAxisAlignment,crossAxisAlignment)、Text(color,fontSize,fontStyle,fontFamily,textAlign,softWrap)、Transform(matrix,origin)。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://snapshot.muedsa.com/reference/parser-tags/#transform | Transform.matrix 列主序 16 Float；origin="(x,y)" | 斜线段旋转绘制 |
| https://snapshot.muedsa.com/reference/parser-tags/#positioned | Positioned 仅一个子节点、须为 Stack 子节点 | 绝对定位布局 |
| https://snapshot.muedsa.com/reference/parser-text/ | fontSize/fontFamily/textAlign、softWrap | 站名与说明文本 |

字体：复用 A01 GET /fonts 结果，选用 `Noto Sans CJK SC,Inter`。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：tmp/run-20261016/A07/requests.jsonl
迭代记录文件：tmp/run-20261016/A07/iterations.jsonl
渲染请求总数：2
成功次数：2
失败次数：0
重试请求数：0
DSL版本数：2（map-v1、card-v1）
实际图片查看次数：0（平台当前无直接读取图像像素的工具；仅校验了 PNG 文件头尺寸）
完整视觉迭代数：0
未完成视觉迭代数：0
其他接口查询：无（字体复用 A01）

两版 DSL 由本地按 inputs/network.json 计算的站点坐标与路由生成（gen_map.py 保留于临时目录），每版渲染响应独立保存。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| map-v1（编辑阶段） / 语法修正 / 无 | 400 PARSE_ERROR：Transform matrix 需 16 值；origin 需带圆括号 | 文档：matrix 列主序 4×4 共 16 个有限 Float；origin 格式 "(x,y)" | 补全 16 值；origin 加括号 | 渲染 HTTP 200，PNG 1600×1000 | network-map.v1.snapshot |
| map-v1（编辑阶段） / 结构修正 / 无 | 图例两行原误嵌套于同一 Positioned（Positioned 仅一子节点） | Positioned 最多一个子节点 | 两条图例各自独立 Positioned 兄弟节点 | 渲染成功 | network-map.v1.snapshot |
| card-v1（编辑阶段） / 内容更正 / 无 | Q2 普通路线最初误标 S08 为换乘站 | 路由复核：普通最短经 G S08→S15→S05，仅在 S05 换乘 | 改为 S08 继续 G，S05 换乘 R | 卡片与 routes.json 一致 | travel-card.v1.snapshot |

## 5. 任务耗时与请求统计

结构化指标文件：outputs/run-20261016/A07/task-metrics.json

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-16T09:44:06+08:00 / 2026-10-16T09:53:49+08:00 | 时间 | 本地计时 |
| 任务总耗时 | 约 583 | 秒 | 整个任务墙钟时间 |
| 首次可用图耗时 | 约 301 | 秒 | 从开始到首张可用图 network-map.png |
| 等待用户反馈 | 未发生 | 秒 | 单轮任务 |
| 限流等待、排队等待 | 0 / 未知 | 秒 | 未发生限流 |
| 已记录请求耗时之和 | 约 14 | 秒 | 2 个渲染请求近似 |
| 成功、失败、重试请求 | 2、0、0 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 0、0 | 次 | 无直接图像查看工具 |

## 6. 设计选择、经验与未解决事项

关键设计选择：
- 示意图以三条换乘站为锚点（S04/S08/S05 同坐标），线路按站序绘制，换乘站为共享节点，避免“单纯线条交叉被误认为换乘”。
- 旅行卡每条路线垂直展开：站名、线路字母色块、换乘标记、无障碍标记（色环/“×”），底部给边数、换乘次数、无障碍判定与理由；Q2 并列展示普通最短与无障碍最短。
- routes.json 与卡片内容同源，便于交叉核对。

可复用经验：Transform matrix 需 16 分量；origin 需圆括号；Positioned 单子节点约束；每版渲染响应独立保存；路由逻辑先在 JSON 中固定，再与图文分别呈现。

未解决事项：无法直接读取最终图像像素，建议人工复查线段贴合与标签遮挡。

结束依据：network-map.png / travel-card.png / routes.json 均已生成，尺寸分别 1600×1000、720×1280、HTTP 200 有效 PNG，路由与 routes.json 一致；按 DSL 几何自检及报告说明，视为完成。

确认临时目录中的草稿、备选方案、已下载文档缓存、脚本、请求响应和失败记录均已保留，未删除或覆盖已有尝试文件。
确认总任务根的 .gitignore 已创建，忽略 __pycache__/、*.pyc、*.pyo、.pytest_cache/、.mypy_cache/、.ruff_cache/；未忽略 tmp/、outputs/ 及实际过程记录。
