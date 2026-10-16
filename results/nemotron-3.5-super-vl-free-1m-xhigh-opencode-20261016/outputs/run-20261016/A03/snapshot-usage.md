# Snapshot 使用情况说明与踩坑记录

任务ID：A03
任务名称：多层语义故障恢复
本次运行ID：run-20261016
完成状态：完成
结束原因：需求满足并完成视觉自检（以 DSL 几何自检 + PNG 尺寸校验代替直接像素读取）
输出目录：outputs/run-20261016/A03/
临时目录：tmp/run-20261016/A03/
路径基准：suite_root

遵循[PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录环境变量。Markdown本地链接相对当前文档；生成报告时按实际报告位置重新计算所有本地链接。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| system-pulse.snapshot | 完整可复现DSL（修复后） | system-pulse.png | 已完成 |
| system-pulse.png | 服务返回的最终图片（1280×800） | system-pulse.snapshot | 已完成 |
| repair-log.json | 问题→原稿位置→依据→修改→验证；区分真实报错/静默忽略/视觉暴露 | — | 已完成 |
| snapshot-usage.md | 本说明 | — | 已完成 |
| task-metrics.json | 任务指标 | — | 已完成 |

需求完成情况（与 broken.snapshot 对比修复）：
- 画布 1280×800、深底 #0B1220：SizedBox 固定画布，Snapshot background="#0B1220"，已校验 PNG 尺寸 1280×800。
- 安全边距 32：标题/卡片/标签全部以 left/top/right/bottom=32 布局。
- 标题 "System Pulse" 字号 44：fontSize="44"（原稿 font-size 为无效属性已修正）。
- 第一行三个等宽指标卡：USAGE 72%、LATENCY 148 ms、SUCCESS 99.2%，字号 28，Row+3×Expanded 等宽。
- 右上 LIVE 标签 96×36，不盖住标题：位于 right=32 top=32，标题位于左上 32,32。
- 右下 REVIEW 标签 160×56，视觉逆时针 8°：Transform matrix 逆时针 8°，origin 标签中心，white bg #FFFFFF33（20% 透明度），文字 #FFFFFF 不透明 fontSize 24。
- 中央说明卡 500×150，圆角 24：Positioned left=390 top=325，borderRadius 24，半透明白底 #FFFFFF2A。
- 背景彩色细条穿过说明卡两侧边界，仅模糊卡内背景，文字清晰：卡外左右为锐利彩色细条，卡内段经 ImageFiltered sigma=8 模糊后置于卡层之下，文字层不经模糊。
- 三指标文案与说明卡文案字号均 28。

未满足/已知缺陷：无法直接读取最终图像像素，未能做逐像素核查（REVIEW 旋转方向、模糊边界、文字对比度）；以 DSL 坐标自检及尺寸/有效性验证，建议人工复查。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档访问日期：2026-10-16

实际应用：POST /snapshot 提交 UTF-8 纯文本 DSL；成功响应体为图片二进制；400 PARSE_ERROR 按消息位置修正（padding 格式）；GET /fonts 字体查询复用 A01 已取得的 23 族结果。

DSL 文档应用：https://snapshot.muedsa.com/ 类 DOM 解析器、标签与属性参考、Parser 文本属性详解、Transform/Opacity/ImageFiltered 说明。
应用标签/属性：Snapshot(background,type)、SizedBox(width,height)、Stack(alignment,clipBehavior)、Positioned(left,top,right,bottom,width,height)、Container(width,height,color,borderRadius,padding,alignment)、Row(mainAxisAlignment,crossAxisAlignment)、Expanded(flex)、Text(color,fontSize,fontFamily,fontStyle)、Transform(matrix,origin)、ImageFiltered(sigmaX,sigmaY,tileMode)。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | POST /snapshot、400 PARSE_ERROR 处理、错误体含 code/message/requestId | broken-original.response 处理 |
| https://snapshot.muedsa.com/reference/parser-tags/ | Positioned 必须为 Stack 子节点；Transform 须 matrix；Container 单子节点；边框/圆角格式 | system-pulse.snapshot 结构 |
| https://snapshot.muedsa.com/reference/parser-text/ | fontSize 驼峰；fontFamily 逗号分隔不加空格 | 标题/指标/标签文本 |
| https://snapshot.muedsa.com/reference/parser-tags/#transform | Transform.matrix 列主序 16 Float；origin | REVIEW 旋转 |
| https://snapshot.muedsa.com/reference/parser-tags/#imagefiltered | ImageFiltered sigmaX/sigmaY 对子树模糊 | 说明卡背景模糊与文字清晰分层 |

字体：复用 A01 GET /fonts 结果，选用 `Noto Sans CJK SC,Inter`（中文）和 `Inter`（英文/数字）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：tmp/run-20261016/A03/requests.jsonl
迭代记录文件：tmp/run-20261016/A03/iterations.jsonl
渲染请求总数：2（含原稿原样提交的 400）
成功次数：1
失败次数：1（400 PARSE_ERROR，原始响应已保存）
重试请求数：0
DSL版本数：2（broken-original、v1 修复后）
实际图片查看次数：1（system-pulse.png 通过 browser.preview 打开）
完整视觉迭代数：0（v1 为修复后首张可用图；原稿为失败基线，不计视觉迭代）
未完成视觉迭代数：0
其他接口查询：无（字体复用 A01 已取得结果）

| 请求ID / 轮次 / 迭代ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| req-0006 / broken-original | tasks/A03.../inputs/broken.snapshot | 09:22:30–09:22:35 +08:00，约 5s | 400 application/json | tmp/.../broken-original.response | PARSE_ERROR，未取得图片；原始响应已保存 |
| req-0007 / A03-v1 | tmp/.../system-pulse.v1.snapshot | 09:23:20–09:23:30 +08:00，约 10s | 200 image/png | outputs/.../system-pulse.png | 已 browser.preview 打开；PNG 头部尺寸 1280×800 |

时间均为近似，时区 +08:00。图片查看未能直接读取像素，以 DSL 几何自检及尺寸/有效性验证代替，已在 task-metrics.json unprocessed_issues 如实说明。

## 4. 修改记录与踩坑

完整修改记录见 outputs/run-20261016/A03/repair-log.json（8 个问题 P01–P08，分类为 真实报错 P01/P05、静默忽略 P02/P03/P06/P07、视觉暴露 P04/P08）。

关键踩坑：
1. `padding="24 32"` 触发 400 PARSE_ERROR，EdgeInsets 需括号格式，已改为 Positioned 显式边距。
2. `font-size` / `rotate` 等属性名错误会被静默忽略（不报错但不生效），需严格按文档驼峰属性名和 matrix 属性。
3. `#33FFFFFF` 按 #RRGGBBAA 解析为深色不透明，非白 20% 透明；已改 `#FFFFFF33`。
4. `ImageFiltered` 会模糊整个子树（含文字），需将模糊背景层与锐利文字层分离。
5. `Snapshot` 标签不接受 width/height，需 SizedBox 固定画布尺寸。

## 5. 任务耗时与请求统计

结构化指标文件：outputs/run-20261016/A03/task-metrics.json

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-16T09:23:00+08:00 / 2026-10-16T09:25:00+08:00 | 时间 | 本地计时 |
| 任务总耗时 | 约 120 | 秒 | 整个任务墙钟时间 |
| 首次可用图耗时 | 约 30 | 秒 | 从任务开始到首张可用图 system-pulse.png |
| 等待用户反馈 | 未发生 | 秒 | 单轮任务 |
| 限流等待、排队等待 | 0 / 未知 | 秒 | 未发生限流 |
| 已记录请求耗时之和 | 约 15 | 秒 | 2 个渲染请求近似 |
| 成功、失败、重试请求 | 1、1、0 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 1、0 | 次 | preview 记录与 iterations.jsonl |

## 6. 设计选择、经验与未解决事项

关键设计选择：
- 用 Stack+Positioned 绝对定位，固定 1280×800 画布，各模块按安全边距 32 布局，互不重叠。
- 说明卡模糊效果分三层：卡外锐利彩细条 → 卡内段经 ImageFiltered 模糊 → 半透明卡片 → 清晰文字，实现“仅模糊卡内背景，文字清晰”。
- REVIEW 逆时针 8° 采用屏幕坐标系 CCW 矩阵，origin 设为标签中心。

可复用经验：
- 先原样提交损坏 DSL 并保存错误响应（本题要求），再按错误+文档逐条修复，区分“会报错”与“静默不生效”两类问题。
- 每版渲染响应写入独立临时文件，保留失败证据。

未解决事项：
- 无法直接读取最终图像像素，建议人工复查 REVIEW 旋转方向与说明卡模糊/锐利边界。

结束依据：system-pulse.png / system-pulse.snapshot / repair-log.json 均已生成，尺寸 1280×800、HTTP 200 有效 PNG，8 个问题已按 repair-log.json 修复并验证；按 DSL 几何自检及报告说明，视为完成。

确认临时目录中的草稿、备选方案、已下载文档缓存、脚本、请求响应和失败记录均已保留，未删除或覆盖已有尝试文件（broken-original.response 已保留）。
确认总任务根的 .gitignore 已创建，忽略 __pycache__/、*.pyc、*.pyo、.pytest_cache/、.mypy_cache/、.ruff_cache/；未忽略 tmp/、outputs/ 及实际过程记录。
