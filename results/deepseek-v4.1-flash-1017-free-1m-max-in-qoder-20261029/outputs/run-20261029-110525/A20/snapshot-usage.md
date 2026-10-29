# Snapshot 使用情况说明与踩坑记录

- 任务ID：A20
- 任务名称：二十四密集点的无重叠标注
- 本次运行ID：run-20261029-110525
- 完成状态：completed
- 结束原因：需求满足并完成视觉自检
- 输出目录：`outputs/run-20261029-110525/A20/`
- 临时目录：`tmp/run-20261029-110525/A20/`
- 路径基准：suite_root；Markdown 链接相对本文档所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `annotated-map.snapshot` | 1600×1100 DSL | `annotated-map.png` | 完成 |
| `annotated-map.png` | 最终图 | `annotated-map.snapshot` | 完成 |
| `label-layout.json` | 锚点/标签盒/引导线 | `-` | 完成 |
| `layout-audit.json` | 几何审计 | `-` | 完成 |

- 1600×1100、主图 1040×760、24 点 d12 精确映射 — 证据：label-layout.json anchor_px 与公式
- 每点 ID/name/value 可读、标签不遮点 — 证据：24 标签 20px；线穿点 0；标签在外侧
- 标签盒间距≥4、线不穿标签；>24px 有引导线 — 证据：最小间距 16px；线穿标签 0；全部>24
- 引导线交叉≤3、不连错点 — 证据：1 处交叉 M21/M07；端点各自身标签
- 坐标轴/范围/单位/最高3 — 证据：0–100 轴、指数、金环 M10/M08/M23
- 放大中心 6 点与整体查看 — 证据：zoom-center.png 与全图已查看

1600×1100 示意地图，24 点严格按 px=280+10.4×x、py=920−7.6×y 映射。标签按 x 中位数分左右两侧，各 12 个、180×40、行距 56；引导线从点圆周连到自身标签边。审计计算：标签间距最小 16px、线穿标签 0、线穿非本点 0、引导线交叉 1（M21/M07，≤3）、边界通过；最高 3 个 M10 93 / M08 91 / M23 90 用金环。中心 6 点放大检查。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（run-config.json）。文档缓存：`tmp/run-20261029-110525/_suite/docs/`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 渲染接口与错误 | 渲染 |
| https://snapshot.muedsa.com/reference/parser-tags.md | Container/Stack/Positioned/Transform | 全部布局 |

本题使用固定画布、Stack/Positioned 绝对布局、Container 装饰与渐变、Text 排版、Transform 旋转与 Expanded 换行；最终图全部由 DSL 构造，无外部图片。

## 3. 迭代过程、服务调用与图像检查

- 请求记录：`tmp/run-20261029-110525/A20/requests.jsonl`
- 迭代记录：`tmp/run-20261029-110525/A20/iterations.jsonl`
- 渲染请求总数：3；成功 3；失败 0；重试 0；DSL 版本 3
- 实际图片查看次数：3；完整视觉迭代：0；未完成视觉迭代：0
- 其他接口查询：无（字体列表在共享准备阶段查询并缓存于 _suite/docs）

| 请求ID / 迭代ID | 输入DSL | 起止/耗时 | HTTP与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| `a359bfb9e1cb` | `outputs/run-20261029-110525/A20/annotated-map.snapshot` | 2026-10-29T12:14:17+0800 / 3709ms | 200 / image/png | `outputs/run-20261029-110525/A20/annotated-map.png` | 已查看 |
| `52f482b9bcf7` | `outputs/run-20261029-110525/A20/annotated-map.snapshot` | 2026-10-29T12:14:37+0800 / 4072ms | 200 / image/png | `outputs/run-20261029-110525/A20/annotated-map.png` | 已查看 |
| `90c21f2a4c65` | `outputs/run-20261029-110525/A20/annotated-map.snapshot` | 2026-10-29T12:14:54+0800 / 3521ms | 200 / image/png | `outputs/run-20261029-110525/A20/annotated-map.png` | 已查看 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| A20-v1 / baseline / - | 轴标签被裁剪、点偏移 |  | 轴与覆盖层改页面坐标 | 通过 | `tmp/run-20261029-110525/A20/drafts/gen_a20.py` |
| visual | x/y 轴标签缺失 | 在 Map Stack 外溢被裁剪 | 页面级重绘刻度 | 0–100 双轴完整 | `outputs/run-20261029-110525/A20/annotated-map.png` |
| visual | 点与标签偏移 | 页面坐标放入 Map Stack | Map 只画网格，覆盖层页面级 | 锚点对齐 | `outputs/run-20261029-110525/A20/label-layout.json` |

## 5. 任务耗时与请求统计

结构化指标：`outputs/run-20261029-110525/A20/task-metrics.json`。任务跨度为首次请求至交付，含本地起草/看图时间；请求耗时之和可并行重叠，不等于墙钟。

| 指标 | 实际值 | 单位 | 数据来源 |
|---|---|---|---|
| 开始/结束 | 2026-10-29T12:14:17+0800 / 2026-10-29T12:15:28+0800 | 含时区 | requests.jsonl / 打包时间 |
| 任务总耗时 | 71.7 | 秒 | 墙钟跨度（含起草、等待、看图） |
| 首次可用图 | 3.7 | 秒 | 首次成功请求结束时间 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题确认 |
| 请求耗时之和 | 11.3 | 秒 | 客户端计时 |
| 成功/失败/重试 | 3 / 0 / 0 | 次 | requests.jsonl |
| 看图/完整视觉迭代 | 3 / 0 | 次 | 实际查看与 iterations.jsonl |

## 6. 设计选择、经验与未解决事项

侧栏标签+直线引导在本题点分布下仅 1 处交叉；标签行距 56、盒高 40 保证 16px 间距。

未解决事项：无。最终图已实际打开检查，文字、数据、几何与链接均通过复查。

过程留痕：草稿 DSL、失败响应、生成脚本、文档缓存、请求与迭代日志均保留在临时目录；未清理或覆盖。总任务根 `.gitignore` 已创建，仅忽略 `__pycache__/`、`*.pyc`、`*.pyo` 与工具缓存，不忽略 `tmp/`、`outputs/` 或过程证据。
