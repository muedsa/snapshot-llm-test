# Snapshot 使用情况说明与踩坑记录

- 任务ID：A18
- 任务名称：守恒对象的三幕视觉叙事
- 本次运行ID：run-20261029-110525
- 完成状态：completed
- 结束原因：需求满足并完成视觉自检
- 输出目录：`outputs/run-20261029-110525/A18/`
- 临时目录：`tmp/run-20261029-110525/A18/`
- 路径基准：suite_root；Markdown 链接相对本文档所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `three-act-story.snapshot` | 1600×1000 DSL | `three-act-story.png` | 完成 |
| `three-act-story.png` | 最终图 | `three-act-story.snapshot` | 完成 |
| `story-audit.json` | 三幕坐标/接收/几何审计 | `-` | 完成 |
| `rationale.md` | 叙事与选择说明 | `-` | 完成 |

- 三幕各同一组 15 单元与 3 节点、ID 稳定 — 证据：story-audit.json U01–U15 / N01–N03；每幕 15+3
- 单元直径 36、不重叠、线不遮圆 — 证据：最小圆心距 40/49.79px；线在圆下绘制；审计计算
- 第三幕每节点 5 个且至少两色 — 证据：N01/N02/N03 各 5；组色 3/3/2 种
- 仅幕名与总标题；过载不用警告文字 — 证据：图中文字只有标题与 I/II/III 幕名
- 两版预览并选择 — 证据：tmp preview-a/b 均渲染查看；rationale 记录
- 400px 缩略仍可读 — 证据：thumb-400.png 已查看

三幕并置 1600×1000：15 个 U01–U15 单元（蓝/橙/灰各 5、直径 36）与 3 个同形节点 N01–N03。第一幕三层环围绕 N01，第二幕挤压成 3×5 块且 N01 纵向 0.82 形变，第三幕三组各 5 个、每组混色。先做 A/B 两版 1600×1000 实际预览，看图选 A；连线先画、圆点后画，避免线遮圆。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（run-config.json）。文档缓存：`tmp/run-20261029-110525/_suite/docs/`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 渲染接口与错误 | 渲染 |
| https://snapshot.muedsa.com/reference/parser-tags.md | Container/Stack/Positioned/Transform | 全部布局 |

本题使用固定画布、Stack/Positioned 绝对布局、Container 装饰与渐变、Text 排版、Transform 旋转与 Expanded 换行；最终图全部由 DSL 构造，无外部图片。

## 3. 迭代过程、服务调用与图像检查

- 请求记录：`tmp/run-20261029-110525/A18/requests.jsonl`
- 迭代记录：`tmp/run-20261029-110525/A18/iterations.jsonl`
- 渲染请求总数：5；成功 5；失败 0；重试 0；DSL 版本 5
- 实际图片查看次数：4；完整视觉迭代：1；未完成视觉迭代：0
- 其他接口查询：无（字体列表在共享准备阶段查询并缓存于 _suite/docs）

| 请求ID / 迭代ID | 输入DSL | 起止/耗时 | HTTP与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| `1d669d6fab51` | `tmp/run-20261029-110525/A18/preview-a.snapshot` | 2026-10-29T12:10:05+0800 / 2765ms | 200 / image/png | `tmp/run-20261029-110525/A18/preview-a.png` | 已查看 |
| `fdda8a42b9e3` | `tmp/run-20261029-110525/A18/preview-b.snapshot` | 2026-10-29T12:10:05+0800 / 2839ms | 200 / image/png | `tmp/run-20261029-110525/A18/preview-b.png` | 已查看 |
| `b9d69fef8caf` | `tmp/run-20261029-110525/A18/preview-a.snapshot` | 2026-10-29T12:10:27+0800 / 2084ms | 200 / image/png | `tmp/run-20261029-110525/A18/preview-a.png` | 已查看 |
| `b5149a1fe99a` | `tmp/run-20261029-110525/A18/preview-b.snapshot` | 2026-10-29T12:10:27+0800 / 3417ms | 200 / image/png | `tmp/run-20261029-110525/A18/preview-b.png` | 已查看 |
| `3b9c971ee719` | `outputs/run-20261029-110525/A18/three-act-story.snapshot` | 2026-10-29T12:10:47+0800 / 2107ms | 200 / image/png | `outputs/run-20261029-110525/A18/three-act-story.png` | 已查看 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| A18-v1 / baseline / - | 预览坐标错位 |  | 卡片内坐标减去原点 | 通过 | `tmp/run-20261029-110525/A18/drafts/gen_a18.py` |
| A18-v2 / visual / A18-v1 | 第三幕按色分组 |  | 改为混色五元组 | 通过 | `outputs/run-20261029-110525/A18/three-act-story.snapshot` |
| visual | 预览只显示第一幕 | 幕内绝对坐标未减卡片原点 | 改为卡片局部坐标 | 三幕完整 | `outputs/run-20261029-110525/A18/three-act-story.png` |
| logical | 第三幕各组单色 | 按 ID 顺序切成三组 | GIDS 混色分组 | 每组≥2色 | `outputs/run-20261029-110525/A18/story-audit.json` |

## 5. 任务耗时与请求统计

结构化指标：`outputs/run-20261029-110525/A18/task-metrics.json`。任务跨度为首次请求至交付，含本地起草/看图时间；请求耗时之和可并行重叠，不等于墙钟。

| 指标 | 实际值 | 单位 | 数据来源 |
|---|---|---|---|
| 开始/结束 | 2026-10-29T12:10:05+0800 / 2026-10-29T12:15:27+0800 | 含时区 | requests.jsonl / 打包时间 |
| 任务总耗时 | 323.0 | 秒 | 墙钟跨度（含起草、等待、看图） |
| 首次可用图 | 2.8 | 秒 | 首次成功请求结束时间 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题确认 |
| 请求耗时之和 | 13.21 | 秒 | 客户端计时 |
| 成功/失败/重试 | 5 / 0 / 0 | 次 | requests.jsonl |
| 看图/完整视觉迭代 | 4 / 1 | 次 | 实际查看与 iterations.jsonl |

## 6. 设计选择、经验与未解决事项

守恒叙事用同一组 ID/尺寸，先画线后画圆保证线不遮圆；过载用间距与节点形变表达，不用文字。

未解决事项：无。最终图已实际打开检查，文字、数据、几何与链接均通过复查。

过程留痕：草稿 DSL、失败响应、生成脚本、文档缓存、请求与迭代日志均保留在临时目录；未清理或覆盖。总任务根 `.gitignore` 已创建，仅忽略 `__pycache__/`、`*.pyc`、`*.pyo` 与工具缓存，不忽略 `tmp/`、`outputs/` 或过程证据。
