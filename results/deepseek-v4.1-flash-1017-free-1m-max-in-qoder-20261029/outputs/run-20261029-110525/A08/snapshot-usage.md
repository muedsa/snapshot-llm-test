# Snapshot 使用情况说明与踩坑记录

- 任务ID：A08
- 任务名称：展馆双路线导览与共享通道
- 本次运行ID：run-20261029-110525
- 完成状态：completed
- 结束原因：需求满足并完成视觉自检
- 输出目录：`outputs/run-20261029-110525/A08/`
- 临时目录：`tmp/run-20261029-110525/A08/`
- 路径基准：suite_root；Markdown 链接相对本文档所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `wayfinding.snapshot` | 1560×1080 DSL | `wayfinding.png` | 完成 |
| `wayfinding.png` | 最终图 | `wayfinding.snapshot` | 完成 |
| `paths.json` | 路径与绘制审计 | `-` | 完成 |

- 1560×1080 双路线导览，26×16 网格与门洞 — 证据：wayfinding.png 尺寸正确，所有格子/门洞可见
- 单格≥36px、格心坐标与比例尺 — 证据：36px；1 格=2 米；边缘坐标刻度
- R1 S→E 与 R2 S→B→D→E 步数/米数 — 证据：R1 35 步/70m；R2 47 步/94m；分段 19/16/12
- 两条路线可独立追踪，共享段双向可辨 — 证据：宽蓝底+窄橙虚线；入/离馆共享段各一
- 方向提示（箭头/分岔/合流/转弯） — 证据：双色箭头、分岔/合流标签
- paths.json 格序列/共享段/审计依据 — 证据：paths.json 与 BFS 复核一致

按 floor.txt 逐格绘制 26×16 网格（单格 36px），墙/通道/门格分色。BFS 求 S→E 与 S→B→D→E，R1 35 步 70 米、R2 47 步 94 米；两段共享通道分别 9 条与 8 条格间边。共享段使用宽蓝实线底 + 窄橙虚线同中心线，箭头按 ±3.5px 偏移，两侧均可追踪；分岔/合流处加标签。S/E 与 A–D 名称进入图例，格心保留字母标记。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（run-config.json）。文档缓存：`tmp/run-20261029-110525/_suite/docs/`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | POST /snapshot 文本请求、图片响应、错误 JSON、/fonts | 渲染 |
| https://snapshot.muedsa.com/reference/parser-tags.md | Container/Stack/Positioned/Transform/Text 与属性限制 | 全部布局 |
| https://snapshot.muedsa.com/reference/parser-text.md | fontSize/fontStyle/maxLines 与文本换行 | 标签与注释 |
| https://snapshot.muedsa.com/reference/parser-tags.md | Stack 子节点限制与 Transform 矩阵 | 路线与网格绘制 |

本题使用固定画布、Stack/Positioned 绝对布局、Container 装饰与渐变、Text 排版、Transform 旋转与 Expanded 换行；最终图全部由 DSL 构造，无外部图片。

## 3. 迭代过程、服务调用与图像检查

- 请求记录：`tmp/run-20261029-110525/A08/requests.jsonl`
- 迭代记录：`tmp/run-20261029-110525/A08/iterations.jsonl`
- 渲染请求总数：5；成功 3；失败 2；重试 0；DSL 版本 3
- 实际图片查看次数：3；完整视觉迭代：1；未完成视觉迭代：0
- 其他接口查询：无（字体列表在共享准备阶段查询并缓存于 _suite/docs）

| 请求ID / 迭代ID | 输入DSL | 起止/耗时 | HTTP与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| `cee29790ea9c` | `outputs/run-20261029-110525/A08/wayfinding.snapshot` | 2026-10-29T11:34:37+0800 / 4729ms | 200 / image/png | `outputs/run-20261029-110525/A08/wayfinding.png` | 已查看 |
| `87499c643596` | `outputs/run-20261029-110525/A08/wayfinding.snapshot` | 2026-10-29T11:35:06+0800 / 1807ms | 400 / application/json | `outputs/run-20261029-110525/A08/wayfinding.png` | 失败响应已保留 |
| `2dc345b437f7` | `outputs/run-20261029-110525/A08/wayfinding.snapshot` | 2026-10-29T11:35:13+0800 / 5418ms | 400 / application/json | `outputs/run-20261029-110525/A08/wayfinding.png` | 失败响应已保留 |
| `68d245382461` | `outputs/run-20261029-110525/A08/wayfinding.snapshot` | 2026-10-29T11:35:26+0800 / 6034ms | 200 / image/png | `outputs/run-20261029-110525/A08/wayfinding.png` | 已查看 |
| `ebeac968b6be` | `outputs/run-20261029-110525/A08/wayfinding.snapshot` | 2026-10-29T11:35:45+0800 / 3928ms | 200 / image/png | `outputs/run-20261029-110525/A08/wayfinding.png` | 已查看 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| A08-v1 / baseline / - | 标签压线、名称溢出 |  | 移 S/E 标签入图例、A–D 名称 22px 两行 | 基本通过 | `tmp/run-20261029-110525/A08/drafts/gen_a08.py` |
| A08-v2 / visual / A08-v1 | 分岔/合流标签压住路线 |  | 左移标签、补 S/E 名称 | 通过 | `outputs/run-20261029-110525/A08/wayfinding.snapshot` |
| render_error | 图例共享段色块用 Stack 嵌套导致 ProxyWidget 错误 | Stack 作为行内单子节点组合方式不稳定 | 改用单色条 + 文字说明 | 200 | `requests.jsonl` |
| visual | S/E 大标签遮住路线 | 标签放在门格旁且覆盖路线 | 移除地图标签，名称入图例 | 路线连续可追踪 | `outputs/run-20261029-110525/A08/wayfinding.png` |

## 5. 任务耗时与请求统计

结构化指标：`outputs/run-20261029-110525/A08/task-metrics.json`。任务跨度为首次请求至交付，含本地起草/看图时间；请求耗时之和可并行重叠，不等于墙钟。

| 指标 | 实际值 | 单位 | 数据来源 |
|---|---|---|---|
| 开始/结束 | 2026-10-29T11:34:37+0800 / 2026-10-29T11:36:18+0800 | 含时区 | requests.jsonl / 打包时间 |
| 任务总耗时 | 101.2 | 秒 | 墙钟跨度（含起草、等待、看图） |
| 首次可用图 | 4.7 | 秒 | 首次成功请求结束时间 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题确认 |
| 请求耗时之和 | 21.92 | 秒 | 客户端计时 |
| 成功/失败/重试 | 3 / 2 / 0 | 次 | requests.jsonl |
| 看图/完整视觉迭代 | 3 / 1 | 次 | 实际查看与 iterations.jsonl |

## 6. 设计选择、经验与未解决事项

共享段用宽底+窄虚线是最稳妥的双身份画法；路径长度按格间边，不按像素偏移。

未解决事项：无。最终图已实际打开检查，文字、数据、几何与链接均通过复查。

过程留痕：草稿 DSL、失败响应、生成脚本、文档缓存、请求与迭代日志均保留在临时目录；未清理或覆盖。总任务根 `.gitignore` 已创建，仅忽略 `__pycache__/`、`*.pyc`、`*.pyo` 与工具缓存，不忽略 `tmp/`、`outputs/` 或过程证据。
