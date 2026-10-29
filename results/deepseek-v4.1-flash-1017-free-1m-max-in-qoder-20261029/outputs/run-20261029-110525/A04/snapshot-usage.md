# Snapshot 使用情况说明与踩坑记录

- 任务ID：A04
- 任务名称：分组改善与总体下降的数据解释
- 本次运行ID：run-20261029-110525
- 完成状态：completed
- 结束原因：需求满足并完成视觉自检
- 输出目录：`outputs/run-20261029-110525/A04/`
- 临时目录：`tmp/run-20261029-110525/A04/`
- 路径基准：suite_root；Markdown 链接相对本文档所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `conversion-story.snapshot` | 1600×1000 DSL | `conversion-story.png` | 完成 |
| `conversion-story.png` | 最终图 | `conversion-story.snapshot` | 完成 |
| `analysis.json` | 分数、加权公式与分解 | `-` | 完成 |

- 1600×1000 信息图，两渠道两期率、构成、总体 — 证据：conversion-story.png 1600×1000，三部分齐全
- 率图同一 0–100% 尺度，不平均渠道比例 — 证据：30.00/10.00/35.00/12.00 四柱同一轴；总体 2600/10000 与 1660/10000
- 构成图每期等长、分段按真实占比 — 证据：两期均 540px=100%，80/20 与 20/80 分段
- 总体对照与精确加权公式 — 证据：26.00%→16.60%，公式与 −9.40pp 可见
- 所有原始分母/分子小表可核对 — 证据：4 渠道行 + 2 合计行，访问/成交/转化率齐全
- 主结论与不可证明因果的限制 — 证据：结论卡明确“不能证明渠道调整导致下降”
- 正文≥22、图标注≥18 — 证据：正文 22、表体 22、图注 18、轴 18
- analysis.json 精确分数、显示百分比、加权公式与依据 — 证据：analysis.json 含 rows/totals/weights/decomposition

用同一 0–100% 尺度画四根渠道柱，直观看到 30→35、10→12 的双升；右侧用两期等长的 100% 堆叠条展示访问构成从 80/20 反转为 20/80；下方用总体 26.00%→16.60% 对照与原始分子/分母表锁定口径。结论给出精确分解：构成效应 −12.0pp、渠道内改善 +2.6pp、合计 −9.4pp，并明确观测数据不能证明因果。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（run-config.json）。文档缓存：`tmp/run-20261029-110525/_suite/docs/`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | POST /snapshot UTF-8 文本请求、图片二进制响应、错误 JSON 与 /fonts | 渲染与字体选择 |
| https://snapshot.muedsa.com/reference/parser-tags.md | Container/Stack/Positioned/Row/Column/Transform/Text 属性与限制 | 全部 DSL |
| https://snapshot.muedsa.com/reference/parser-text.md | fontSize、fontStyle、maxLines、overflow 与文本换行 | 文字排版 |

本题使用固定画布、Stack/Positioned 绝对布局、Container 装饰与渐变、Text 排版、Transform 旋转与 Expanded 换行；最终图全部由 DSL 构造，无外部图片。

## 3. 迭代过程、服务调用与图像检查

- 请求记录：`tmp/run-20261029-110525/A04/requests.jsonl`
- 迭代记录：`tmp/run-20261029-110525/A04/iterations.jsonl`
- 渲染请求总数：4；成功 3；失败 1；重试 0；DSL 版本 3
- 实际图片查看次数：3；完整视觉迭代：2；未完成视觉迭代：0
- 其他接口查询：无（字体列表在共享准备阶段查询并缓存于 _suite/docs）

| 请求ID / 迭代ID | 输入DSL | 起止/耗时 | HTTP与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| `63bc62554807` | `outputs/run-20261029-110525/A04/conversion-story.snapshot` | 2026-10-29T11:25:24+0800 / 2236ms | 400 / application/json | `outputs/run-20261029-110525/A04/conversion-story.png` | 失败响应已保留 |
| `4ad70bbfcd52` | `outputs/run-20261029-110525/A04/conversion-story.snapshot` | 2026-10-29T11:25:40+0800 / 7577ms | 200 / image/png | `outputs/run-20261029-110525/A04/conversion-story.png` | 已查看 |
| `09cf59d295b6` | `outputs/run-20261029-110525/A04/conversion-story.snapshot` | 2026-10-29T11:26:06+0800 / 3591ms | 200 / image/png | `outputs/run-20261029-110525/A04/conversion-story.png` | 已查看 |
| `2d4ef7c4e627` | `outputs/run-20261029-110525/A04/conversion-story.snapshot` | 2026-10-29T11:26:25+0800 / 3177ms | 200 / image/png | `outputs/run-20261029-110525/A04/conversion-story.png` | 已查看 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| A04-v1 / syntax-fix / - | 宽度属性出现未插值 {bar_w-w1} |  | 改成 f-string 计算 w2 | 渲染成功 | `tmp/run-20261029-110525/A04/drafts/gen_a04.py` |
| A04-v2 / visual / A04-v1 | 构成图例被裁、周期标签缺失 |  | 调整行距、加图例与周期标签 | 周期标签仍被裁 | `outputs/run-20261029-110525/A04/conversion-story.snapshot` |
| A04-v3 / visual / A04-v2 | 复查 |  | baseline 上移、表体 22 | 通过 | `outputs/run-20261029-110525/A04/conversion-story.snapshot` |
| syntax | DSL 中 width="{bar_w-w1:.1f}" 原样出现 | 拼接了非 f-string 片段 | 先算 w2 再插值 | 200 渲染 | `requests.jsonl` |
| visual | 构成图第二行图例被裁 | 卡片内容高 222px、图例结束 230px | 行距 82→76，卡片 270→280 | 图例完整 | `outputs/run-20261029-110525/A04/conversion-story.png` |
| visual | 率图 前期/后期 标签贴底被裁 | 基线下移后标签超出内容框 | baseline 338，标签上移 | 两标签完整 | `outputs/run-20261029-110525/A04/conversion-story.png` |

## 5. 任务耗时与请求统计

结构化指标：`outputs/run-20261029-110525/A04/task-metrics.json`。任务跨度为首次请求至交付，含本地起草/看图时间；请求耗时之和可并行重叠，不等于墙钟。

| 指标 | 实际值 | 单位 | 数据来源 |
|---|---|---|---|
| 开始/结束 | 2026-10-29T11:25:24+0800 / 2026-10-29T11:28:54+0800 | 含时区 | requests.jsonl / 打包时间 |
| 任务总耗时 | 210.3 | 秒 | 墙钟跨度（含起草、等待、看图） |
| 首次可用图 | 23.6 | 秒 | 首次成功请求结束时间 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题确认 |
| 请求耗时之和 | 16.58 | 秒 | 客户端计时 |
| 成功/失败/重试 | 3 / 1 / 0 | 次 | requests.jsonl |
| 看图/完整视觉迭代 | 3 / 2 | 次 | 实际查看与 iterations.jsonl |

## 6. 设计选择、经验与未解决事项

经验：百分比图统一 0–100% 轴能直接呈现“双升”，而堆叠构成条是解释辛普森悖论的关键；结论必须写出可复算的构成/渠道内分解。

未解决事项：无。最终图已实际打开检查，文字、数据、几何与链接均通过复查。

过程留痕：草稿 DSL、失败响应、生成脚本、文档缓存、请求与迭代日志均保留在临时目录；未清理或覆盖。总任务根 `.gitignore` 已创建，仅忽略 `__pycache__/`、`*.pyc`、`*.pyo` 与工具缓存，不忽略 `tmp/`、`outputs/` 或过程证据。
