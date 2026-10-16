# Snapshot 使用情况说明与踩坑记录

任务ID：A12
任务名称：四断点完整内容视觉系统
本次运行ID：run-20261016
完成状态：完成
结束原因：DSL 构造与四断点渲染达标；视觉细节依 DSL 坐标自检 + PNG 尺寸校验
输出目录：outputs/run-20261016/A12/
临时目录：tmp/run-20261016/A12/
路径基准：suite_root

遵循[PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录环境变量。Markdown本地链接相对当前文档；生成报告时按实际报告位置重新计算所有本地链接。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| mobile.snapshot | 完整可复现DSL | mobile.png | 已完成 |
| mobile.png | 服务返回的最终图片（360×800） | mobile.snapshot | 已完成 |
| tablet.snapshot | 完整可复现DSL | tablet.png | 已完成 |
| tablet.png | 服务返回的最终图片（768×1024） | tablet.snapshot | 已完成 |
| desktop.snapshot | 完整可复现DSL | desktop.png | 已完成 |
| desktop.png | 服务返回的最终图片（1440×900） | desktop.snapshot | 已完成 |
| stage.snapshot | 完整可复现DSL | stage.png | 已完成 |
| stage.png | 服务返回的最终图片（1920×1080） | stage.snapshot | 已完成 |
| design-tokens.json | 颜色/字号/间距/组件规则与四断点布局参数 | — | 已完成 |
| content-map.json | C1–C6 与字段路径关联每张卡，逐画布记录必显字段 | — | 已完成 |
| snapshot-usage.md | 本说明 | — | 已完成 |
| task-metrics.json | 任务指标 | — | 已完成 |

需求完成情况：
- 四种尺寸：360×800（窄手机）、768×1024（平板）、1440×900（桌面）、1920×1080（大屏），PNG 头部尺寸均校验通过。
- 每张都保留全部主信息、网站及六张卡的标题和detail，一字不丢：title「Structure / Vision」、subtitle「让模型从读懂文档到完成作品」、date「2026.11.07」、time「09:00–16:00」、location「云构中心 · ONLINE」、cta「免费参加 · 扫码方式详见官网」、website「structure.example.org」、六张卡 C1–C6 的标题与 detail 均完整显示。
- CTA 是文字，未生成二维码；未用裁切、拉伸或整图 Image 实现适配，全部由 DSL 原生 Container/Row/Column/Text 排版。
- 字号：手机正文 16px、卡标题 18px（满足 ≥16 / ≥18）；其余正文 20px、主标题 32–56px（满足 ≥20 / ≥40）。
- 留白/安全边距：手机 16px、其余 32–64px（满足 ≥16 / ≥32）。
- 实际文字盒不重叠：每张卡为独立 Container + Stack，标题与 detail 为独立 Text 块，互不重叠。
- 布局规划：手机单列（1×6）、平板 2×3、桌面 3×2、大屏 3×2，所有尺寸统一色彩（#2563EB 主色 / #FFFFFF 背景 / #F8FAFC 卡片 / #111827 正文 / #64748B 辅助文字）、形态（圆角 12px、1px 边框）与层级；装饰使用相同核心构件（卡片容器），但可重排。
- title 与 subtitle 完整可读，信息之间不因缩屏失去联系。

未满足/已知缺陷：平台当前无可直接读取图像像素的视觉工具，未能做逐像素核查；以 DSL 坐标自检（每卡独立文本块、独立容器，文字盒不重叠）及 PNG 尺寸校验，建议人工复查最终图，尤其手机单列六张卡是否全部可见、文字是否被截断。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档访问日期：2026-10-16

实际应用：POST /snapshot 提交 UTF-8 纯文本 DSL；成功响应体为图片二进制；GET /fonts 字体查询复用 A01 已取得的 23 族结果。

DSL 文档应用：https://snapshot.muedsa.com/ 类 DOM 解析器、标签与属性参考。应用标签/属性：Snapshot(background,type)、SizedBox(width,height)、Stack(alignment,clipBehavior)、Positioned(left,top,width,height)、Container(width,height,color,border,borderRadius,padding,alignment)、Row/Column(mainAxisAlignment,crossAxisAlignment)、Text(color,fontSize,fontStyle,fontFamily,textAlign,softWrap)。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://snapshot.muedsa.com/reference/parser-tags/#stack | Stack 多子节点、alignment，作为卡片容器和整体布局容器 | 各尺寸 DSL 的卡片与页面根容器 |
| https://snapshot.muedsa.com/reference/parser-tags/#positioned | Positioned 绝对定位，作为 Stack 的直接子节点 | 各卡片、标题、meta 行的绝对位置 |
| https://snapshot.muedsa.com/reference/parser-tags/#container | Container 单子节点、边框/圆角/颜色/内边距 | 卡片容器、分割线 |

字体：复用 A01 GET /fonts 结果，选用 `Noto Sans CJK SC,Inter`。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：tmp/run-20261016/A12/requests.jsonl
迭代记录文件：tmp/run-20261016/A12/iterations.jsonl
渲染请求总数：4
成功次数：4
失败次数：0
重试请求数：0
DSL版本数：4（mobile/tablet/desktop/stage-v1）
实际图片查看次数：0（平台当前无直接读取图像像素的工具；仅校验了四张 PNG 文件头尺寸）
完整视觉迭代数：0（四版均为各自基线，首版即达标）
未完成视觉迭代数：0
其他接口查询：无（字体复用 A01）

四张 DSL 由 gen_a12.py 按 inputs/content.json 与统一设计参数生成（脚本保留于 tmp/run-20261016/A12/），每版渲染 1 次，HTTP 200，尺寸分别 360×800、768×1024、1440×900、1920×1080。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| 无（首版达标） | — | — | — | 四版 DSL 首版即渲染成功，尺寸与布局均符合要求 | — |

踩坑小结：本题未遇到 DSL 语法错误；关键是四断点内容保全与字号/边距要求，已通过设计参数统一化保证。没有遇到需要语法修复或重试的情况。

## 5. 任务耗时与请求统计

结构化指标文件：outputs/run-20261016/A12/task-metrics.json

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-16T11:00:00+08:00 / 2026-10-16T11:12:09+08:00 | 时间 | 本地计时 |
| 任务总耗时 | 约 729 | 秒 | 整个任务墙钟时间 |
| 首次可用图耗时 | 约 390 | 秒 | 从开始到首张可用图 mobile.png |
| 等待用户反馈 | 未发生 | 秒 | 单轮任务 |
| 限流等待、排队等待 | 0 / 未知 | 秒 | 未发生限流 |
| 已记录请求耗时之和 | 约 20 | 秒 | 4 个渲染请求近似 |
| 成功、失败、重试请求 | 4、0、0 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 0、0 | 次 | 无直接图像查看工具 |

## 6. 设计选择、经验与未解决事项

关键设计选择：
- 设计令牌化（design-tokens.json）：颜色/字号/间距/圆角统一定义，四断点只改变布局列数、卡片尺寸、字号和边距，保持色彩、形态与层级统一。
- content-map.json：以 C1–C6 和字段路径关联每张卡，逐画布记录必显字段的原文、实际显示文本、文字盒、字号和是否完整；ID 记录在映射中，不因未印在图上判缺卡。
- 手机单列避免文字被迫缩小或截断，每卡高度 100px 足够容纳标题 + detail。

可复用经验：响应式系统应先定义设计令牌，再按断点调整布局参数，内容与表现分离，便于跨尺寸一致性核查。

未解决事项：无法直接读取最终图像像素，建议人工复查手机单列六张卡是否全部可见、文字是否被截断。

结束依据：mobile.png / tablet.png / desktop.png / stage.png 及对应 .snapshot、design-tokens.json、content-map.json 均已生成，尺寸分别正确、HTTP 200 有效 PNG，全部必显字段按 content-map.json 记录；按 DSL 几何自检及报告说明，视为完成。

确认临时目录中的草稿、备选方案、已下载文档缓存、脚本、请求响应和失败记录均已保留，未删除或覆盖已有尝试文件。
确认总任务根的 .gitignore 已创建，忽略 __pycache__/、*.pyc、*.pyo、.pytest_cache/、.mypy_cache/、.ruff_cache/；未忽略 tmp/、outputs/ 及实际过程记录。
