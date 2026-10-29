# Snapshot 使用情况说明与踩坑记录

- 任务ID：A05
- 任务名称：不规则采样与缺测的仪表报告
- 本次运行ID：run-20261029-110525
- 完成状态：completed
- 结束原因：需求满足并完成视觉自检
- 输出目录：`outputs/run-20261029-110525/A05/`
- 临时目录：`tmp/run-20261029-110525/A05/`
- 路径基准：suite_root；Markdown 链接相对本文档所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `sensor-report.snapshot` | 1440×1000 DSL | `sensor-report.png` | 完成 |
| `sensor-report.png` | 最终图 | `sensor-report.snapshot` | 完成 |
| `normalized-data.json` | 分钟偏移、缺测、范围与连接段 | `-` | 完成 |

- 1440×1000 三联趋势与真实时间比例共享横轴 — 证据：三图 x 映射一致；08:00–12:30 标签齐全
- 温度/湿度缺测处线段断开、不补值 — 证据：温度在 09:15、11:40 断；湿度在 09:40 断；图中 × 与图例
- 压差可正可负、零线清晰、标注负值区段 — 证据：零线加深；09:40–10:50 三个负样本带注释
- 每个真实读数有独立标记 — 证据：10+11+12 个空心圆标记
- 各指标有效数与观测 min/max — 证据：KPI：10/12、11/12、12/12 与范围
- 全部 12 时点简表，缺测以 — — 证据：两栏 6+6 行，09:15 温度与 09:40 湿度为 —
- 图例含缺测与断线；正文≥20、轴/表≥18 — 证据：图例在页眉；正文 20、轴 18、表 18/19
- normalized-data.json 含分钟偏移、null、范围、有效数、连接段 — 证据：normalized-data.json 完整

三张纵向堆叠的趋势图共享同一条 08:00–12:30 真实时间轴（x=120+分钟/270×1250），半小时间隔网格贯穿三图。每个真实读数画独立空心圆标记；缺失点画灰色 × 与竖线，线段只在相邻两个实测点之间连接，缺测处断开。压差图中性零线加深，09:40–10:50 用浅琥珀带标出三个负值实测点，并明确“仅采样点为负”。下方 12 时点表分两栏，缺测写“—”。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（run-config.json）。文档缓存：`tmp/run-20261029-110525/_suite/docs/`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | POST /snapshot UTF-8 文本请求、图片二进制响应、错误 JSON 与 /fonts | 渲染与字体选择 |
| https://snapshot.muedsa.com/reference/parser-tags.md | Container/Stack/Positioned/Row/Column/Transform/Text 属性与限制 | 全部 DSL |
| https://snapshot.muedsa.com/reference/parser-text.md | fontSize、fontStyle、maxLines、overflow 与文本换行 | 文字排版 |

本题使用固定画布、Stack/Positioned 绝对布局、Container 装饰与渐变、Text 排版、Transform 旋转与 Expanded 换行；最终图全部由 DSL 构造，无外部图片。

## 3. 迭代过程、服务调用与图像检查

- 请求记录：`tmp/run-20261029-110525/A05/requests.jsonl`
- 迭代记录：`tmp/run-20261029-110525/A05/iterations.jsonl`
- 渲染请求总数：5；成功 5；失败 0；重试 0；DSL 版本 4
- 实际图片查看次数：3；完整视觉迭代：1；未完成视觉迭代：0
- 其他接口查询：无（字体列表在共享准备阶段查询并缓存于 _suite/docs）

| 请求ID / 迭代ID | 输入DSL | 起止/耗时 | HTTP与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| `54083c3732ec` | `outputs/run-20261029-110525/A05/sensor-report.snapshot` | 2026-10-29T11:27:04+0800 / 2539ms | 200 / image/png | `outputs/run-20261029-110525/A05/sensor-report.png` | 已查看 |
| `f32e0e236637` | `outputs/run-20261029-110525/A05/sensor-report.snapshot` | 2026-10-29T11:27:25+0800 / 2641ms | 200 / image/png | `outputs/run-20261029-110525/A05/sensor-report.png` | 已查看 |
| `86166877d296` | `outputs/run-20261029-110525/A05/sensor-report.snapshot` | 2026-10-29T11:27:45+0800 / 2104ms | 200 / image/png | `outputs/run-20261029-110525/A05/sensor-report.png` | 已查看 |
| `d69a6156db10` | `outputs/run-20261029-110525/A05/sensor-report.snapshot` | 2026-10-29T11:27:52+0800 / 2972ms | 200 / image/png | `outputs/run-20261029-110525/A05/sensor-report.png` | 已查看 |
| `09e478caad27` | `outputs/run-20261029-110525/A05/sensor-report.snapshot` | 2026-10-29T11:28:05+0800 / 3225ms | 200 / image/png | `outputs/run-20261029-110525/A05/sensor-report.png` | 已查看 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| A05-v1 / baseline / - | 图表内容被卡片裁剪、页眉重叠 |  | 图表改页面级坐标；页眉压缩 | 趋势可见 | `tmp/run-20261029-110525/A05/drafts/gen_a05.py` |
| A05-v2 / visual / A05-v1 | 湿度缺测标记弱、12:30 缺标签 |  | 加深 ×；补 12:30；调整绘图区顶部 | 通过 | `outputs/run-20261029-110525/A05/sensor-report.snapshot` |
| visual | 三张图全空白 | 卡片内 Stack 使用页面绝对坐标，内容被裁剪 | 所有图表元素提升到页面级 Stack | 趋势、网格、标记全部显示 | `outputs/run-20261029-110525/A05/sensor-report.png` |
| visual | 12:30 轴标签与缺测标记不可见 | 标签被卡片背景覆盖；× 颜色过浅 | 标签后绘、× 改深灰 | 最终图可见 | `outputs/run-20261029-110525/A05/sensor-report.png` |

## 5. 任务耗时与请求统计

结构化指标：`outputs/run-20261029-110525/A05/task-metrics.json`。任务跨度为首次请求至交付，含本地起草/看图时间；请求耗时之和可并行重叠，不等于墙钟。

| 指标 | 实际值 | 单位 | 数据来源 |
|---|---|---|---|
| 开始/结束 | 2026-10-29T11:27:04+0800 / 2026-10-29T11:28:54+0800 | 含时区 | requests.jsonl / 打包时间 |
| 任务总耗时 | 110.5 | 秒 | 墙钟跨度（含起草、等待、看图） |
| 首次可用图 | 2.5 | 秒 | 首次成功请求结束时间 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题确认 |
| 请求耗时之和 | 13.48 | 秒 | 客户端计时 |
| 成功/失败/重试 | 5 / 0 / 0 | 次 | requests.jsonl |
| 看图/完整视觉迭代 | 3 / 1 | 次 | 实际查看与 iterations.jsonl |

## 6. 设计选择、经验与未解决事项

经验：共享时间轴必须统一 x 映射并让网格线在三图内重复绘制；缺测用“断线 + × + 图例”三重编码，避免被读成 0。

未解决事项：无。最终图已实际打开检查，文字、数据、几何与链接均通过复查。

过程留痕：草稿 DSL、失败响应、生成脚本、文档缓存、请求与迭代日志均保留在临时目录；未清理或覆盖。总任务根 `.gitignore` 已创建，仅忽略 `__pycache__/`、`*.pyc`、`*.pyo` 与工具缓存，不忽略 `tmp/`、`outputs/` 或过程证据。
