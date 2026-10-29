# Snapshot 使用情况说明与踩坑记录

- 任务ID：A24
- 任务名称：双团队约束下的发布作战计划
- 本次运行ID：run-20261029-110525
- 完成状态：completed
- 结束原因：需求满足并完成视觉自检
- 输出目录：`outputs/run-20261029-110525/A24/`
- 临时目录：`tmp/run-20261029-110525/A24/`
- 路径基准：suite_root；Markdown 链接相对本文档所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `execution-board.snapshot` | 1920×1080 DSL | `execution-board.png` | 完成 |
| `execution-board.png` | 泳道执行图 | `execution-board.snapshot` | 完成 |
| `decision-brief.snapshot` | 1200×1600 DSL | `decision-brief.png` | 完成 |
| `decision-brief.png` | 决策简报 | `decision-brief.snapshot` | 完成 |
| `action-card.snapshot` | 720×1280 DSL | `action-card.png` | 完成 |
| `action-card.png` | 手机行动卡 | `action-card.snapshot` | 完成 |
| `schedule.json` | 精确排程 | `-` | 完成 |
| `schedule-audit.json` | 资源/依赖/下界审计 | `-` | 完成 |
| `content-map.json` | 三图区域映射 | `-` | 完成 |

- 可行且尽早排程，12 任务完整时长 — 证据：schedule.json；conflicts=[], depbad=[], duration check True
- 依赖/团队/起止可读，空档与截止线 — 证据：泳道图与索引；16:00 截止线、缓冲带
- 关键路径与工作量下界；不称最优 — 证据：审计 255/242.5/260；proven_optimal false
- 三图一致、横屏≥20/竖页≥24/手机≥20 — 证据：同一 schedule；主要正文 20/22+
- brief 风险/对策/依据 — 证据：K1-K3 + 排程依据
- audit/content-map — 证据：schedule-audit.json / content-map.json

对 12 任务做 2 团队资源约束搜索：同团队串行、依赖满足、允许 R05/R09/R12 选队；得到 09:00 起、13:20 完成（260min），缓冲 160min，关键路径 255min、资源下界 242.5min。三图共用同一排程：1920×1080 泳道、1200×1600 决策简报、720×1280 行动卡；依赖以编号索引展示，不画满交叉线。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（run-config.json）。文档缓存：`tmp/run-20261029-110525/_suite/docs/`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 渲染接口/type 仅 png/jpg/webp | A23/A24 |
| https://snapshot.muedsa.com/reference/parser-tags.md | Container/Stack/Positioned/Transform | 全部布局 |

本题使用固定画布、Stack/Positioned 绝对布局、Container 装饰与渐变、Text 排版、Transform 旋转与 Expanded 换行；最终图全部由 DSL 构造，无外部图片。

## 3. 迭代过程、服务调用与图像检查

- 请求记录：`tmp/run-20261029-110525/A24/requests.jsonl`
- 迭代记录：`tmp/run-20261029-110525/A24/iterations.jsonl`
- 渲染请求总数：12；成功 9；失败 3；重试 2；DSL 版本 8
- 实际图片查看次数：3；完整视觉迭代：0；未完成视觉迭代：0
- 其他接口查询：无（字体列表在共享准备阶段查询并缓存于 _suite/docs）

| 请求ID / 迭代ID | 输入DSL | 起止/耗时 | HTTP与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| `d11aef120419` | `outputs/run-20261029-110525/A24/decision-brief.snapshot` | 2026-10-29T12:22:33+0800 / 1799ms | 400 / application/json | `outputs/run-20261029-110525/A24/decision-brief.png` | 失败响应已保留 |
| `762aa535ff96` | `outputs/run-20261029-110525/A24/action-card.snapshot` | 2026-10-29T12:22:33+0800 / 3129ms | 200 / image/png | `outputs/run-20261029-110525/A24/action-card.png` | 已查看 |
| `4dc8c0cc8dec` | `outputs/run-20261029-110525/A24/execution-board.snapshot` | 2026-10-29T12:22:33+0800 / 3733ms | 200 / image/png | `outputs/run-20261029-110525/A24/execution-board.png` | 已查看 |
| `12098fac22fd` | `outputs/run-20261029-110525/A24/decision-brief.snapshot` | 2026-10-29T12:22:42+0800 / 2741ms | 200 / image/png | `outputs/run-20261029-110525/A24/decision-brief.png` | 已查看 |
| `c9c1aab78d36` | `outputs/run-20261029-110525/A24/execution-board.snapshot` | 2026-10-29T12:23:07+0800 / 2620ms | 200 / image/png | `outputs/run-20261029-110525/A24/execution-board.png` | 已查看 |
| `71f72956fa5e` | `outputs/run-20261029-110525/A24/action-card.snapshot` | 2026-10-29T12:23:07+0800 / 3504ms | 200 / image/png | `outputs/run-20261029-110525/A24/action-card.png` | 已查看 |
| `cf8d006d6382` | `outputs/run-20261029-110525/A24/decision-brief.snapshot` | 2026-10-29T12:23:07+0800 / 4042ms | 200 / image/png | `outputs/run-20261029-110525/A24/decision-brief.png` | 已查看 |
| `568663d678cd` | `outputs/run-20261029-110525/A24/decision-brief.snapshot` | 2026-10-29T12:23:39+0800 / 2609ms | 200 / image/png | `outputs/run-20261029-110525/A24/decision-brief.png` | 已查看 |
| `1f42550bb63e` | `outputs/run-20261029-110525/A24/execution-board.snapshot` | 2026-10-29T12:23:39+0800 / 2741ms | 200 / image/png | `outputs/run-20261029-110525/A24/execution-board.png` | 已查看 |
| `24a9c836dd70` | `outputs/run-20261029-110525/A24/action-card.snapshot` | 2026-10-29T12:23:39+0800 / 65364ms | None / - | `outputs/run-20261029-110525/A24/action-card.png` | 失败响应已保留 |
| `b216815b2b4d` | `outputs/run-20261029-110525/A24/action-card.snapshot` | 2026-10-29T12:24:46+0800 / 10628ms | None / - | `outputs/run-20261029-110525/A24/action-card.png` | 失败响应已保留 |
| `a5ea1164843f` | `outputs/run-20261029-110525/A24/action-card.snapshot` | 2026-10-29T12:25:01+0800 / 2368ms | 200 / image/png | `outputs/run-20261029-110525/A24/action-card.png` | 已查看 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| A24-v1 / baseline / - | 缓冲带盖块、简报 KPI 压标题、短块时间断行 |  | 重排缓冲/简报间距/短块时间双行 | 通过 | `tmp/run-20261029-110525/A24/drafts/gen_a24.py` |
| visual | 缓冲带覆盖 R12 边缘 | 绘制顺序 | 缓冲带先画并右移 | R12 完整 | `outputs/run-20261029-110525/A24/execution-board.png` |
| visual | 简报 KPI 压住章节标题；&amp; 实体 | 间距/转义 | 下移 KPI 与章节、改写标题 | 无重叠/无实体 | `outputs/run-20261029-110525/A24/decision-brief.png` |

## 5. 任务耗时与请求统计

结构化指标：`outputs/run-20261029-110525/A24/task-metrics.json`。任务跨度为首次请求至交付，含本地起草/看图时间；请求耗时之和可并行重叠，不等于墙钟。

| 指标 | 实际值 | 单位 | 数据来源 |
|---|---|---|---|
| 开始/结束 | 2026-10-29T12:22:33+0800 / 2026-10-29T12:25:45+0800 | 含时区 | requests.jsonl / 打包时间 |
| 任务总耗时 | 192.4 | 秒 | 墙钟跨度（含起草、等待、看图） |
| 首次可用图 | 3.1 | 秒 | 首次成功请求结束时间 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题确认 |
| 请求耗时之和 | 105.28 | 秒 | 客户端计时 |
| 成功/失败/重试 | 9 / 3 / 2 | 次 | requests.jsonl |
| 看图/完整视觉迭代 | 3 / 0 | 次 | 实际查看与 iterations.jsonl |

## 6. 设计选择、经验与未解决事项

用搜索而非手排得到 260min 方案，并明确它不是已证明最优；三图共用一份 schedule。

未解决事项：无。最终图已实际打开检查，文字、数据、几何与链接均通过复查。

过程留痕：草稿 DSL、失败响应、生成脚本、文档缓存、请求与迭代日志均保留在临时目录；未清理或覆盖。总任务根 `.gitignore` 已创建，仅忽略 `__pycache__/`、`*.pyc`、`*.pyo` 与工具缓存，不忽略 `tmp/`、`outputs/` 或过程证据。
