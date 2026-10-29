# Snapshot 使用情况说明与踩坑记录

- 任务ID：A15
- 任务名称：复杂界面视觉复刻
- 本次运行ID：run-20261029-110525
- 完成状态：completed
- 结束原因：需求满足并完成视觉自检
- 输出目录：`outputs/run-20261029-110525/A15/`
- 临时目录：`tmp/run-20261029-110525/A15/`
- 路径基准：suite_root；Markdown 链接相对本文档所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `reconstructed.snapshot` | 1440×900 DSL | `reconstructed.png` | 完成 |
| `reconstructed.png` | 复刻图 | `reconstructed.snapshot` | 完成 |
| `reconstruction-audit.json` | 锚点与颜色审计 | `-` | 完成 |
| `comparison.md` | 对比说明 | `-` | 完成 |

- 保持 1440×900、主要结构与信息完整 — 证据：侧栏/标题/按钮/3 KPI/图表/活动/表格/页脚齐全
- 12+ 锚点±8px，覆盖四象限、图表、表格 — 证据：14 个锚点全部通过，最大 2px
- 图表比例与标记，不只放数字 — 证据：0–120 轴、54px 柱宽、柱顶按值成比例
- 表格 3 行顺序与状态编码准确 — 证据：Atlas/Pulse/Orbit；蓝/琥珀/绿三状态
- reconstruction-audit.json 与 comparison.md — 证据：两文件含测量方法、误差、颜色与残余差异
- 不嵌入参考图 — 证据：所有结构由 DSL 绘制

按参考 PNG 实测坐标重建 1440×900 NORTHSTAR 仪表盘：220px 深色侧栏、三张 KPI、净收入柱图、活动卡、项目表。参考坐标由同算法图像测量获得（侧栏边界、卡片白区、柱色掩码、状态色块、字形暗像素），不是凭感觉摆放。字体用 Inter + Noto CJK 回退，按参考字形高度/宽度校正字号。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（run-config.json）。文档缓存：`tmp/run-20261029-110525/_suite/docs/`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 渲染接口 | 渲染 |
| https://snapshot.muedsa.com/reference/parser-tags.md | Container/Stack/Positioned/Text | 全部布局 |

本题使用固定画布、Stack/Positioned 绝对布局、Container 装饰与渐变、Text 排版、Transform 旋转与 Expanded 换行；最终图全部由 DSL 构造，无外部图片。

## 3. 迭代过程、服务调用与图像检查

- 请求记录：`tmp/run-20261029-110525/A15/requests.jsonl`
- 迭代记录：`tmp/run-20261029-110525/A15/iterations.jsonl`
- 渲染请求总数：6；成功 6；失败 0；重试 0；DSL 版本 6
- 实际图片查看次数：3；完整视觉迭代：1；未完成视觉迭代：0
- 其他接口查询：无（字体列表在共享准备阶段查询并缓存于 _suite/docs）

| 请求ID / 迭代ID | 输入DSL | 起止/耗时 | HTTP与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| `3f54aa61aadf` | `outputs/run-20261029-110525/A15/reconstructed.snapshot` | 2026-10-29T11:59:58+0800 / 3820ms | 200 / image/png | `outputs/run-20261029-110525/A15/reconstructed.png` | 已查看 |
| `fcb55730de22` | `outputs/run-20261029-110525/A15/reconstructed.snapshot` | 2026-10-29T12:00:40+0800 / 2344ms | 200 / image/png | `outputs/run-20261029-110525/A15/reconstructed.png` | 已查看 |
| `485ac0154106` | `outputs/run-20261029-110525/A15/reconstructed.snapshot` | 2026-10-29T12:01:00+0800 / 7227ms | 200 / image/png | `outputs/run-20261029-110525/A15/reconstructed.png` | 已查看 |
| `0d40b6f7da48` | `outputs/run-20261029-110525/A15/reconstructed.snapshot` | 2026-10-29T12:01:19+0800 / 2706ms | 200 / image/png | `outputs/run-20261029-110525/A15/reconstructed.png` | 已查看 |
| `8d70c032ec98` | `outputs/run-20261029-110525/A15/reconstructed.snapshot` | 2026-10-29T12:01:39+0800 / 3731ms | 200 / image/png | `outputs/run-20261029-110525/A15/reconstructed.png` | 已查看 |
| `575357a2038c` | `outputs/run-20261029-110525/A15/reconstructed.snapshot` | 2026-10-29T12:02:18+0800 / 2572ms | 200 / image/png | `outputs/run-20261029-110525/A15/reconstructed.png` | 已查看 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| A15-v1 / baseline / - | 字体偏大、标题/KPI 宽度不符 |  | 全局字号×0.78、标题微调 | 锚点通过 | `tmp/run-20261029-110525/A15/drafts/gen_a15.py` |
| A15-v2 / visual / A15-v1 | 标题右边缘差 9px |  | letterSpacing -0.1 | 全部≤8px | `outputs/run-20261029-110525/A15/reconstructed.snapshot` |
| visual | 初版字体整体偏大 | 参考使用更紧凑字号 | 0.78 缩放并按锚点微调 | 14 锚点通过 | `outputs/run-20261029-110525/A15/reconstruction-audit.json` |

## 5. 任务耗时与请求统计

结构化指标：`outputs/run-20261029-110525/A15/task-metrics.json`。任务跨度为首次请求至交付，含本地起草/看图时间；请求耗时之和可并行重叠，不等于墙钟。

| 指标 | 实际值 | 单位 | 数据来源 |
|---|---|---|---|
| 开始/结束 | 2026-10-29T11:59:58+0800 / 2026-10-29T12:02:39+0800 | 含时区 | requests.jsonl / 打包时间 |
| 任务总耗时 | 161.1 | 秒 | 墙钟跨度（含起草、等待、看图） |
| 首次可用图 | 3.8 | 秒 | 首次成功请求结束时间 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题确认 |
| 请求耗时之和 | 22.4 | 秒 | 客户端计时 |
| 成功/失败/重试 | 6 / 0 / 0 | 次 | requests.jsonl |
| 看图/完整视觉迭代 | 3 / 1 | 次 | 实际查看与 iterations.jsonl |

## 6. 设计选择、经验与未解决事项

复刻先量后画：用同一图像算法测参考与重建，避免只凭目测。字体差异在 comparison.md 如实说明。

未解决事项：无。最终图已实际打开检查，文字、数据、几何与链接均通过复查。

过程留痕：草稿 DSL、失败响应、生成脚本、文档缓存、请求与迭代日志均保留在临时目录；未清理或覆盖。总任务根 `.gitignore` 已创建，仅忽略 `__pycache__/`、`*.pyc`、`*.pyo` 与工具缓存，不忽略 `tmp/`、`outputs/` 或过程证据。
