# Snapshot 使用情况说明与踩坑记录 — A15

任务ID：A15
任务名称：复杂界面视觉复刻
本次运行ID：20261104-145656-hy4all
完成状态：完成
结束原因：需求满足并完成逐图视觉自检
输出目录：`outputs/20261104-145656-hy4all/A15/`
临时目录：`tmp/20261104-145656-hy4all/A15/`
路径基准：suite_root（记录内本地路径均相对总任务根；Markdown 链接相对本文档）

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `reconstructed.png` | 1440×900 参考界面复刻（从零 DSL 构造，参考图仅供观察） | `reconstructed.snapshot` | 完成；服务真实 PNG 120319 字节；16/16 视觉锚点满足 ±8px |
| `reconstruction-audit.json` | 16 个锚点的参考估计/重建实测/分量误差/测量方法/局部证据，颜色复核与逐项看图结论 | — | 完成 |
| `comparison.md` | 可测误差表、原尺寸同背景颜色并排判断、字体与残余差异如实说明 | — | 完成 |

1440×900 输出，重建参考图的布局、背景、侧栏、卡片、图表、表格、状态标签与主要装饰，不改成新设计、不嵌入/裁块/描图参考 PNG。content.json 全部文字逐字保真：NORTHSTAR、四个导航项、Workspace Overview、Saturday 07 November 2026、Export report、三张 KPI（¥128,400/+12.4%、426/+8.1%、3.2%/−0.8 pp）、Net revenue/Apr–Sep/六个月/¥ thousand/0–120 刻度、Team activity 三条、Recent projects 四列三行与状态编码、页脚。图表按 chart_values×1.2px 真实比例重建，零线 y=549，六柱顶部实测与参考一致。至少 12 个锚点覆盖四象限、图表与表格并逐分量记录误差（本题 16 个）。交付 reconstruction-audit.json 与 comparison.md，逐项说明颜色与残余差异。

**逐图自检证据**：用 ViewImage 实际打开 reference.png 整体一次、参考局部放大 6 张（侧栏上/下、顶部、图表、活动、表格）；v1 重建图打开一次，发现 3 项缺陷：Y 轴刻度 0 在顶部顺序颠倒、NORTHSTAR 右边缘 214 贴边、「12 team members」换行与「Manage access」重叠。v2 修复后重新渲染并再次打开原尺寸全图，三处缺陷全部消除；另生成重建图的图表/表格/侧栏底部 2 倍局部放大各打开一次，确认 Y 轴 120→0 递减且与网格线对齐、六柱比例与顶部圆角/底部平齐正确、六个月份完整、表格三行与三状态胶囊颜色编码正确、侧栏底部三行各占一行。用 ffmpeg 转 raw + 纯 Python 逐像素对重建图同法测量 16 个锚点，16/16 满足 ±8px（最大分量误差 3px）；PNG 文件头 89 50 4E 47 校验通过。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`
文档版本或访问日期：2026-11-04，服务 `/ai-guide.md`、`/openapi.yaml`、`/fonts` 与文档站 `llms.txt`、`parser.md`、`parser-tags.md`、`parser-text.md`、`parser-errors.md`、`examples.md`、`fonts.md`、`media-text.md`、`_llms-txt/dsl.txt` 已下载缓存于 `tmp/20261104-145656-hy4all/_suite/docs/`。

AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md

实际应用的契约：`POST /snapshot`，请求体 UTF-8 纯文本 `text/plain; charset=utf-8`，成功响应 `image/png` 二进制；按 `X-Request-Id`、`Server-Timing`、`Content-Type` 校验，失败时读取 JSON 的 `code`/`diagnostic`；`GET /fonts` 返回纯文本字体族清单，本套统一使用 `Noto Sans CJK SC`（中文）与 `Inter`（拉丁/数字），必要时 `Noto Sans Mono CJK SC`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| ai-guide.md + openapi.yaml | 请求体/响应类型/错误处理/字体查询/限流 | render.py、requests.jsonl |
| reference/parser-tags.md | Snapshot/Container/Stack/Positioned/Text/ClipPath/Transform/Opacity/Border | 本题全部 .snapshot |
| reference/parser-text.md | fontFamily、fontSize、fontStyle、textAlign、CDATA 文本 | 本题全部文字元素 |
| guides/examples.md | 固定画布 + Stack/Column 布局范式 | 本题布局骨架 |

使用 Snapshot 根节点 type=png + background；Stack + 固定尺寸 Container 作为 1440×900 绝对定位画布，Positioned 放置全部元素；Container 的 color/borderRadius/border/alignment 实现侧栏、卡片、导航选中态、状态胶囊与柱体（顶部圆角用 borderRadiusTopLeft/TopRight 经 c.add 原生片段）；Text 的 fontFamily/fontSize/fontStyle/color/textAlign/letterSpacing 与 CDATA 文本；ClipPath 未使用（本题无需 SVG 路径）；渐变用于顶部未启用。全部主体、图表、文字、图标均由 DSL 构造，无外部图片素材，参考 PNG 未嵌入。

字体查询：服务 /fonts 列表（缓存 tmp/<run_id>/_suite/docs/fonts.txt）含 Inter、Noto Sans CJK SC 等；本题界面为拉丁/数字，统一使用 Inter，中文回退 Noto Sans CJK SC。参考图字体未知，不同字体的字形宽度差异在 comparison.md 如实说明。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/20261104-145656-hy4all/A15/requests.jsonl`
迭代记录文件：`tmp/20261104-145656-hy4all/A15/iterations.jsonl`
渲染请求总数：5
成功次数：2
失败次数：3
重试请求数：2
DSL版本数：2
实际图片查看次数：12
完整视觉迭代数：1
未完成视觉迭代数：0
其他接口查询：`/ai-guide.md`、`/openapi.yaml`、`/fonts` 及文档站页面属共享准备，见 `tmp/20261104-145656-hy4all/_suite/requests.jsonl` 与 docs 缓存；本题不重复计为新增 HTTP 请求。

- **v1**（baseline，父版本 无）：查看 `outputs/<run_id>/A15/reconstructed.png (v1)` 发现：首版 Y 轴刻度顺序颠倒（0 在顶部、120 在底部）；NORTHSTAR 右边缘 214 贴近侧栏右边界 220；「12 team members」在 155px 文本框内换行，第二行与 Manage access 重叠。。改动：生成首版基线并实际打开全图查看。复查：确认 3 项缺陷，进入视觉迭代。
- **v2**（visual，父版本 v1）：查看 `outputs/<run_id>/A15/reconstructed.png (v2)` 发现：上述 3 项缺陷；其余结构与参考一致。改动：Y 轴刻度改为 reversed(ticks) 对应 grid_ys（120→0 递减）；NORTHSTAR 改 19 号、字距 0.4、文本框 150px；「12 team members」改 18 号、文本框 165px，保证单行。复查：重新渲染并再次打开实际 PNG 及 3 张局部放大复查：3 项缺陷全部消除；Y 轴递减正确、NORTHSTAR 右边缘 189、底部三行各占一行；16/16 锚点满足 ±8px，图表比例/全部文字/状态编码/整体视觉通过。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 |
|---|---|---|---|---|
| v1 / baseline / — | 首版 Y 轴刻度顺序颠倒（0 在顶部、120 在底部）；NORTHSTAR 右边缘 214 贴近侧栏右边界 220；「12 team members」在 155px 文本框内换行，第二行与 Manage access 重叠。 | Y 轴 ticks 与 grid_ys 同序 zip；NORTHSTAR 字号/字距过大；底部行文本框过窄、字号 19 偏大 | 生成首版基线并实际打开全图查看 | 确认 3 项缺陷，进入视觉迭代 |
| v2 / visual / v1 | 上述 3 项缺陷；其余结构与参考一致 | 实际渲染图逐项观察与像素测量（NORTHSTAR 右边缘 214 vs 参考约 192） | Y 轴刻度改为 reversed(ticks) 对应 grid_ys（120→0 递减）；NORTHSTAR 改 19 号、字距 0.4、文本框 150px；「12 team members」改 18 号、文本框 165px，保证单行 | 重新渲染并再次打开实际 PNG 及 3 张局部放大复查：3 项缺陷全部消除；Y 轴递减正确、NORTHSTAR 右边缘 189、底部三行各占一行；16/16 锚点满足 ±8px，图表比例/全部文字/状态编码/整体视觉通过 |

踩坑：Text 不做 HTML 实体解码，含特殊字符必须用 CDATA（dsl.cdata 统一处理）；Container 需 alignment=CENTER 才稳定垂直居中文字；绝对值布局必须在 Stack 中放固定尺寸 Container 作画布基准；Y 轴刻度文字顺序需与从上到下的网格线反向对应，否则 0 会落在顶部；侧栏内文本框宽度必须小于侧栏宽，否则长文字换行或贴边。服务层面：v2 首次渲染遇到 3 次连续读取/SSL 握手超时（status=0，非解析错误），保留全部失败响应于 tmp/<run_id>/A15/responses/，服务恢复后重渲染成功，未把错误响应写成图片。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/20261104-145656-hy4all/A15/task-metrics.json`

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-11-04T16:01:24+08:00 → 2026-11-04T16:42:15+08:00 | ISO8601+时区 | suite-state.json / 本地墙钟 |
| 任务总耗时 | 见 task-metrics.json | 秒 | 起止墙钟差；不与请求耗时求和 |
| 首次可用图耗时 | 近似首版渲染耗时 | 秒 | requests.jsonl 首条成功记录 |
| 等待用户反馈 | 0 | 秒 | 全套自动连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（未收到 429/503） | 秒 | requests.jsonl |
| 已记录请求耗时之和 | 566.687 | 秒 | requests.jsonl（可含重叠，不等于任务总耗时） |
| 成功、失败、重试请求 | 2 / 3 / 2 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 12 / 1 | 次 | iterations.jsonl 与实际查看记录 |

## 6. 设计选择、经验与未解决事项

以 reference.png 的像素扫描结果反推几何：侧栏 220px、主背景 #F3F6FB、卡片白色圆角 14px，三张 KPI 卡 x=261/645/1029、图表卡 [261,311,1000,594]、活动卡 [1030,311,1398,594]、表格卡 [261,625,1398,840]；图表零线 y=549、1.2px/单位，六柱按 chart_values 精确计算。颜色全部取自参考纯色区采样。文字逐字取自 content.json，状态标签三色编码保真。不追求与参考来源 DSL 树一致，只保证可测几何、数据、颜色与整体视觉一致。

最终实际图片已逐张打开检查：侧栏、导航选中态、顶部标题与按钮、三张 KPI、Net revenue 图表、Team activity、Recent projects 表格与页脚均完整可读；16 个锚点重建实测全部满足 ±8px；图表按真实比例重建、表格三行顺序与状态编码准确、content.json 文字全部保真；reconstruction-audit.json 与 comparison.md 用可测误差与人工并排判断说明残余差异，据此标为完成。

临时目录中的 DSL 版本、原始请求/响应、脚本与记录均保留，未删除或覆盖任何尝试；总任务根 `.gitignore` 已建立，仅排除 `__pycache__/`、`*.pyc` 等运行时缓存，未忽略 `tmp/`、`outputs/` 或过程证据。

未解决事项：无。
