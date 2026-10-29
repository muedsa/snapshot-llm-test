# Snapshot 使用情况说明与踩坑记录

- 任务ID：A01
- 任务名称：六个月经营诊断驾驶舱
- 本次运行ID：run-20261029-110525
- 完成状态：completed
- 结束原因：需求满足并完成视觉自检
- 输出目录：`outputs/run-20261029-110525/A01/`
- 临时目录：`tmp/run-20261029-110525/A01/`
- 路径基准：suite_root；Markdown 链接相对本文档所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `operations.snapshot` | 经营驾驶舱完整 DSL | `operations.png` | 完成（最终版本） |
| `operations.png` | 1600×1000 最终图 | `operations.snapshot` | 完成，服务真实响应 200 |
| `computed-data.json` | 计算数据、轴定义与结论引用 | `-` | 完成 |

- 1600×1000 画布与 Northstar 六个月经营诊断 — 证据：operations.png 实际尺寸 1600×1000，页眉含 2026-04 至 2026-09
- 四张 KPI：总净收入、总经营利润、总订单、期间总体转化率 — 证据：¥918,624 / ¥262,124 / 3,045 笔 / 11.15%；总体转化率=3045÷27300
- 六个月净收入与经营利润分组柱图，共用零起点和比例 — 证据：同一 0–21 万元轴，两根柱/月，9 月净收入 20.2 万与利润 6.4 万按同比例绘制
- 访问量与转化率两个共享月份对齐的小图 — 证据：两小图绘图区同为 x=34..432、6 组中心相同；访问量 0/3k/6k 刻度，转化率 10/11/12% 刻度
- 六行明细表：月份/净收入/退款率/利润/转化率 — 证据：表格 6 行完整，金额整数、比例两位小数，逐月数值与 CSV 计算一致
- 一条有证据的管理结论 — 证据：结论引用 8 月退款 15,048、退款率 8.00%、利润环比 −16.4% 与 9 月 4.00%、64,368，均可由 computed-data.json 复算
- 正文≥20、脚注≥16；刻度单位图例完整 — 证据：KPI 数值 38、表体 20、结论正文 20；脚注 16；主图图例与万元单位、两小图单位齐全
- computed-data.json 含每月计算值、汇总、图轴定义与结论引用数值 — 证据：computed-data.json 含 months/totals/axes/bar_geometry/conclusion

采用浅色管理驾驶舱：顶部品牌与口径、四张 KPI、左侧主柱图 + 右侧两张月份对齐小图、底部六个月明细与管理结论。主图共用零起点与唯一金额轴（0–21 万元），净收入与利润分组柱；访问量小图使用零起点柱图，转化率小图使用独立百分比轴折线。表格按列右对齐，8 月退款异常行用暖色底强调，9 月用浅绿底标记收官。结论直接引用 8 月退款率 8.00%、利润环比 −16.4% 与 9 月 4.00% 的回落，避免把相关当因果。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（run-config.json）。文档缓存：`tmp/run-20261029-110525/_suite/docs/`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | POST /snapshot 使用 UTF-8 纯文本，成功为图片二进制；错误为 JSON；/fonts 返回实际字体族 | render.js 请求与错误处理、字体选择 |
| https://snapshot.muedsa.com/reference/parser-tags.md | Container 尺寸/装饰/渐变、Stack+Positioned 定位、Row/Column/Expanded、Transform 矩阵、borderRadius 分角 | operations.snapshot 全部布局与柱图 |
| https://snapshot.muedsa.com/reference/parser-text.md | fontFamily、fontSize、fontStyle=BOLD、textAlign、字体回退与行高 | KPI、表格与结论文字 |
| https://snapshot.muedsa.com/guides/examples.md | 固定画布 Container + 内层 Stack/Column 的构图方式 | 1600×1000 根布局 |

固定画布、Stack/Positioned 绝对定位、Container 边框/圆角/渐变、Row/Column/Expanded/Spacer、Text 多字号与字重、Transform 旋转绘制转化率折线；无外部图片，全部由 DSL 构造。

## 3. 迭代过程、服务调用与图像检查

- 请求记录：`tmp/run-20261029-110525/A01/requests.jsonl`
- 迭代记录：`tmp/run-20261029-110525/A01/iterations.jsonl`
- 渲染请求总数：10；成功 4；失败 6；重试 5；DSL 版本 4
- 实际图片查看次数：3；完整视觉迭代：2；未完成视觉迭代：0
- 其他接口查询：无（字体列表在共享准备阶段查询并缓存于 _suite/docs）

| 请求ID / 迭代ID | 输入DSL | 起止/耗时 | HTTP与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| `fe3d5208330b` | `run-20261029-110525/A01/drafts/test.snapshot` | 2026-10-29T11:07:44+0800 / 120316ms | None / - | `run-20261029-110525/A01/drafts/test.png` | 失败响应已保留 |
| `e6efbdb8dbac` | `run-20261029-110525/A01/drafts/test.snapshot` | 2026-10-29T11:09:47+0800 / 120664ms | None / - | `run-20261029-110525/A01/drafts/test.png` | 失败响应已保留 |
| `764a6a024e9f` | `run-20261029-110525/A01/drafts/test.snapshot` | 2026-10-29T11:11:51+0800 / 3409ms | 200 / image/png | `run-20261029-110525/A01/drafts/test.png` | 已查看 |
| `e7af481b05e1` | `../outputs/run-20261029-110525/A01/operations.snapshot` | 2026-10-29T11:13:20+0800 / 6055ms | 400 / application/json | `../outputs/run-20261029-110525/A01/operations.png` | 失败响应已保留 |
| `7a126419f34e` | `outputs/run-20261029-110525/A01/operations.snapshot` | 2026-10-29T11:13:43+0800 / 10695ms | None / - | `outputs/run-20261029-110525/A01/operations.png` | 失败响应已保留 |
| `6d46727eded5` | `outputs/run-20261029-110525/A01/operations.snapshot` | 2026-10-29T11:13:56+0800 / 10667ms | None / - | `outputs/run-20261029-110525/A01/operations.png` | 失败响应已保留 |
| `05b517ba9b96` | `outputs/run-20261029-110525/A01/operations.snapshot` | 2026-10-29T11:14:10+0800 / 7813ms | 200 / image/png | `outputs/run-20261029-110525/A01/operations.png` | 已查看 |
| `fdf5e0d87c95` | `outputs/run-20261029-110525/A01/operations.snapshot` | 2026-10-29T11:15:09+0800 / 72166ms | None / - | `outputs/run-20261029-110525/A01/operations.png` | 失败响应已保留 |
| `f5dcf7670213` | `outputs/run-20261029-110525/A01/operations.snapshot` | 2026-10-29T11:16:23+0800 / 3292ms | 200 / image/png | `outputs/run-20261029-110525/A01/operations.png` | 已查看 |
| `1f1d01865d61` | `outputs/run-20261029-110525/A01/operations.snapshot` | 2026-10-29T11:16:46+0800 / 3255ms | 200 / image/png | `outputs/run-20261029-110525/A01/operations.png` | 已查看 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| A01-v1 / baseline / - | 主图柱缺失、文本溢出 |  | 修正卡片内容坐标系与文本 Expanded | 部分修复，仍有裁剪 | `tmp/run-20261029-110525/A01/drafts/gen_a01.py` |
| A01-v2 / visual / A01-v1 | 结论脚注被裁、访问量小图无刻度 |  | 删标签行、压缩证据、补刻度与网格 | 通过，最终图完整 | `outputs/run-20261029-110525/A01/operations.snapshot` |
| A01-final / visual / A01-v2 | 复查最终图 |  | 无（确认交付） | 文字、数据、几何与链接通过 | `outputs/run-20261029-110525/A01/operations.snapshot` |
| transport | Python urllib 与 curl 在接收 PNG 时多次超时/截断（9583/15231 字节） | 本机 TLS/传输链路对大响应不稳定；服务端已返回 200 与完整 Content-Length | 改用 Node 24 fetch + Connection: close，校验 PNG IEND 后落盘；保留失败响应 | 同一 DSL 由 Node 取得 15231 字节完整 PNG，可正常打开 | `tmp/run-20261029-110525/A01/requests.jsonl` |
| syntax-fix | 首次渲染 400 PARSE_ERROR：alignment CENTER_START 无效 | 生成器把 START/END 直接拼进 CENTER_ 前缀；有效枚举是 CENTER_LEFT/CENTER_RIGHT | 表头对齐映射 LEFT/RIGHT | 重新渲染 200 | `tmp/run-20261029-110525/A01/failed/` |
| visual | 首版主图无柱、坐标被裁剪，结论与 KPI 文本溢出 | 图表内部使用页面绝对坐标却放在有 padding 的 Stack 内，重复减去/未减去 padding；结论 Row 未用 Expanded | 全部图表改为卡片内容坐标；结论与 KPI 文本改用 Expanded/独立行 | 第二版柱图、刻度、表格完整；结论脚注仍被裁 | `outputs/run-20261029-110525/A01/operations.png 首版与第二版对比` |
| visual | 结论卡片底部脚注仍被裁剪，访问量小图无刻度 | 结论内证据文字 4 行 + 双标签行超出 300px；访问量小图仅画零线 | 删去双标签行并压缩证据文案；访问量补 0/3k/6k 刻度与网格，与小图左边界对齐 | 最终图脚注完整，两小图月份列严格对齐 | `outputs/run-20261029-110525/A01/operations.png` |

## 5. 任务耗时与请求统计

结构化指标：`outputs/run-20261029-110525/A01/task-metrics.json`。任务跨度为首次请求至交付，含本地起草/看图时间；请求耗时之和可并行重叠，不等于墙钟。

| 指标 | 实际值 | 单位 | 数据来源 |
|---|---|---|---|
| 开始/结束 | 2026-10-29T11:07:44+0800 / 2026-10-29T11:17:48+0800 | 含时区 | requests.jsonl / 打包时间 |
| 任务总耗时 | 604.1 | 秒 | 墙钟跨度（含起草、等待、看图） |
| 首次可用图 | 250.4 | 秒 | 首次成功请求结束时间 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题确认 |
| 请求耗时之和 | 358.33 | 秒 | 客户端计时 |
| 成功/失败/重试 | 4 / 6 / 5 | 次 | requests.jsonl |
| 看图/完整视觉迭代 | 3 / 2 | 次 | 实际查看与 iterations.jsonl |

## 6. 设计选择、经验与未解决事项

可复用经验：卡片内绝对坐标必须使用卡片内容坐标系；文本放在 Row 中必须用 Expanded 才能按可用宽度换行；迷你图共享月份对齐应使用同一绘图区左右边界与组宽。

未解决事项：无。最终图已实际打开检查，文字、数据、几何与链接均通过复查。

过程留痕：草稿 DSL、失败响应、生成脚本、文档缓存、请求与迭代日志均保留在临时目录；未清理或覆盖。总任务根 `.gitignore` 已创建，仅忽略 `__pycache__/`、`*.pyc`、`*.pyo` 与工具缓存，不忽略 `tmp/`、`outputs/` 或过程证据。
