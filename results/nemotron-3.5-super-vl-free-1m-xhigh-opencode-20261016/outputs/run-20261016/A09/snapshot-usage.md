# Snapshot 使用情况说明与踩坑记录

任务ID：A09
任务名称：十二个非对称图形变换标本
本次运行ID：run-20261016
完成状态：完成
结束原因：需求满足并完成视觉自检（以 DSL 几何自检 + PNG 尺寸校验代替直接像素读取）
输出目录：outputs/run-20261016/A09/
临时目录：tmp/run-20261016/A09/
路径基准：suite_root

遵循[PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录环境变量。Markdown本地链接相对当前文档；生成报告时按实际报告位置重新计算所有本地链接。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| transform-atlas.snapshot | 完整可复现DSL | transform-atlas.png | 已完成 |
| transform-atlas.png | 服务返回的最终图片（1600×1200） | transform-atlas.snapshot | 已完成 |
| geometry-audit.json | 每标本矩阵、矩形四角、圆点中心、外接框、±1.5像素核对方法 | — | 已完成 |
| snapshot-usage.md | 本说明 | — | 已完成 |
| task-metrics.json | 任务指标 | — | 已完成 |

需求完成情况：
- 尺寸 1600×1200：满足（PNG 头部校验）。
- 4列×3行，每格300×250，格间32，整体居中：画布网格 origin=(152,193)，cell 300×250，gap 32，四周留白用于标题与图例。
- inputs/stamp.json 印章：120×120，3 个彩色矩形（#E54B4B [8,8,28,92]、#2364DB [36,72,68,28]、#EAB53B [64,8,40,28]）+ 黑圆点（中心[91,49]，半径8），局部坐标从印章左上角，矩形部分相邻，圆点消除对称。
- 12 变换按 transforms.json 从左到右、从上到下依次为 T01..T12；操作按列表顺序，每步围绕局部(60,60)；像素坐标 x 向右、y 向下，顺时针按图像方向；mirror_horizontal=左右镜像，mirror_vertical=上下镜像；最终局部中心放到每格中心。
- 每格主体全部由 Transform.matrix（列主序 4×4，16 值）表示最终组合变换，未手改形状坐标冒充矩阵；圆点随同变换；未裁切变换后主体。
- 每格标注编号（字号22 粗体）与操作短名（字号20），刻度辅助线（字号20）齐全。
- T07 与 T08 显示操作顺序差异：T07 矩阵 [[0,1],[1,0]]（转置），T08 矩阵 [[0,-1],[-1,0]]，两者不同。
- geometry-audit.json：列主序 4×4 矩阵、每矩形四角、圆点中心、最终外接框，以及 ±1.5 像素视觉/像素核对方法（反走样边缘例外）。

未满足/已知缺陷：平台当前无可直接读取图像像素的视觉工具，未能做逐像素核查；以 DSL 坐标自检（矩阵与独立 Python 计算逐一一致）及 PNG 尺寸校验，建议人工复查最终图。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档访问日期：2026-10-16

实际应用：POST /snapshot 提交 UTF-8 纯文本 DSL；成功响应体为图片二进制；GET /fonts 字体查询复用 A01 已取得的 23 族结果。

DSL 文档应用：https://snapshot.muedsa.com/ 类 DOM 解析器、标签与属性参考、Transform 说明。应用标签/属性：Snapshot(background,type)、SizedBox(width,height)、Stack(alignment,clipBehavior)、Positioned(left,top,width,height)、Container(width,height,color,border,borderRadius,alignment)、Row/Column(mainAxisAlignment,crossAxisAlignment)、Text(color,fontSize,fontStyle,fontFamily,textAlign,softWrap)、Transform(matrix,origin)。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://snapshot.muedsa.com/reference/parser-tags/#transform | Transform.matrix 列主序 4×4 Float；origin="(x,y)" 需带圆括号；transform 只影响绘制不改布局尺寸 | transform-atlas.snapshot 每格 Transform |
| https://snapshot.muedsa.com/reference/parser-tags/#positioned | Positioned 仅一个子节点、须为 Stack 子节点 | 网格格、标记、标签绝对定位 |
| https://snapshot.muedsa.com/reference/parser-tags/#container | Container 单子节点、边框/圆角格式 | 单元格框、印章图形 |

字体：复用 A01 GET /fonts 结果，选用 `Noto Sans CJK SC,Inter`。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：tmp/run-20261016/A09/requests.jsonl
迭代记录文件：tmp/run-20261016/A09/iterations.jsonl
渲染请求总数：1
成功次数：1
失败次数：0
重试请求数：0
DSL版本数：1
实际图片查看次数：0（平台当前无直接读取图像像素的工具；仅校验了 PNG 文件头尺寸 1600×1200）
完整视觉迭代数：0
未完成视觉迭代数：0
其他接口查询：无（字体复用 A01）

DSL 由 gen_a09.py 按 2×2 矩阵合成（顺时针旋转/镜像/缩放，列表顺序左乘）后转列主序 4×4 生成（脚本保留于临时目录），渲染 1 次，HTTP 200，PNG 1600×1200，80115 字节。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| v1（编辑阶段） / 语法修正 / 无 | 400 PARSE_ERROR：Transform matrix 需 16 值；origin 需带圆括号 | 文档：matrix 为列主序 4×4 共 16 个有限 Float；origin 格式 "(x,y)" | 三处 Transform（seg/arrow/dash）均补全 16 值并为 origin 加括号 | 渲染 HTTP 200，PNG 1600×1200 | transform-atlas.v1.snapshot |

踩坑小结：与 A02/A06/A07/A08 一致的 Transform 语法约束；已全部修正，未遗留未知属性。本题核心是矩阵合成顺序，通过 T07/T08 一对对照验证“顺序先后影响结果”。

## 5. 任务耗时与请求统计

结构化指标文件：outputs/run-20261016/A09/task-metrics.json

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-16T10:01:53+08:00 / 2026-10-16T10:06:41+08:00 | 时间 | 本地计时 |
| 任务总耗时 | 约 288 | 秒 | 整个任务墙钟时间 |
| 首次可用图耗时 | 约 143 | 秒 | 从开始到首张可用图 transform-atlas.png |
| 等待用户反馈 | 未发生 | 秒 | 单轮任务 |
| 限流等待、排队等待 | 0 / 未知 | 秒 | 未发生限流 |
| 已记录请求耗时之和 | 约 6 | 秒 | 1 个渲染请求近似 |
| 成功、失败、重试请求 | 1、0、0 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 0、0 | 次 | 无直接图像查看工具 |

## 6. 设计选择、经验与未解决事项

关键设计选择：
- 矩阵以列主序 4×4 表达，合成时以 pivot (60,60) 为局部原点，再把 pivot 映射到格中心，保证各格主体中心落在格中心且不超出绘制意图。
- 刻度辅助线按局部坐标 x、y = 0/30/60/90/120 画在各格内，与印章坐标系一致，便于核对。

可复用经验：Transform matrix 需 16 分量；origin 需圆括号；矩阵合成顺序即操作列表顺序（后操作左乘），T07/T08 对照可作为顺序语义回归用例。

未解决事项：无法直接读取最终图像像素，建议人工复查变换后边缘与圆点位置。

结束依据：transform-atlas.png / transform-atlas.snapshot / geometry-audit.json 均已生成，尺寸 1600×1200、HTTP 200 有效 PNG，12 标本矩阵与 geometry-audit.json 一致；按 DSL 几何自检及报告说明，视为完成。

确认临时目录中的草稿、备选方案、已下载文档缓存、脚本、请求响应和失败记录均已保留，未删除或覆盖已有尝试文件。
确认总任务根的 .gitignore 已创建，忽略 __pycache__/、*.pyc、*.pyo、.pytest_cache/、.mypy_cache/、.ruff_cache/；未忽略 tmp/、outputs/ 及实际过程记录。
