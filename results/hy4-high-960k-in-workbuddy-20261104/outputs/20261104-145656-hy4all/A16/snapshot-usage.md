# Snapshot 使用情况说明与踩坑记录 — A16

任务ID：A16
任务名称：从错误图表恢复可信叙事
本次运行ID：20261104-145656-hy4all
完成状态：完成
结束原因：需求满足并完成逐图视觉自检
输出目录：`outputs/20261104-145656-hy4all/A16/`
临时目录：`tmp/20261104-145656-hy4all/A16/`
路径基准：suite_root（记录内本地路径均相对总任务根；Markdown 链接相对本文档）

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `corrected-report.png` | 1280×900 修正后的可信季度复盘报告 | `corrected-report.snapshot` | 完成；服务真实 PNG 191201 字节；v2 复查通过 |
| `findings.json` | 7 项可观察错误（图片位置/现象/源数据核对/影响/修正/最终查看结果）+ 3 项不确定事项 | — | 完成 |
| `corrected-data.json` | 四季计算值、共同零起点轴定义、8 根柱位置/高度、结论引用字段与数值 | — | 完成 |

先用 ViewImage 实际打开 flawed-report.png 逐项诊断，只依据图片与 source.csv，不臆造常见坑。重制 1280×900 可信报告：四季收入/成本分组柱图（共同零起点 0–200 万元、柱高=数值×1.25px）、利润明细（30/27/32/54 万元）、一条有数据依据的标题「季度复盘 · Q4 收入与利润均创新高」、图例（蓝=收入/橙=成本）、单位「万元」、全部 Q1–Q4；保持「季度复盘」主题；重点季度 Q4 由数据论证。附 findings.json 与 corrected-data.json，并在报告底部以「原图勘误」逐条说明原图错在哪里。正文≥22、标注≥18、无外部图像。

**逐图自检证据**：用 ViewImage 打开 flawed-report.png 整体一次，并用 ffmpeg 转 raw 逐像素核对网格线（y=295/349/403/457/511/565，2.7px/万元，最下为 100 线）与柱高（蓝 150/172/198/246px、橙 110/135/128/165px），据此确认 7 项可观察错误。v1 修正报告打开一次，发现「重点季度」卡内两段长文字重叠、被裁切；v2 把该卡加宽至 576px、缩窄利润卡、文案拆成三行独立文本框后重新渲染并再次打开：三行各占一行、完整无裁切。最终图复查：图例颜色与系列对应正确、8 根柱顶标签 120/90/135/108/128/96/180/126 与 source.csv 一致、Q3 收入柱低于 Q2、Q4 最高、利润明细 30/27/32/54、底部勘误三行完整、字号满足正文≥22/标注≥18。PNG 文件头 89 50 4E 47 校验通过。

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

Snapshot 根节点 + 固定尺寸 Container；Stack + Positioned 绝对定位；Container 的 color/borderRadius/border/alignment 实现卡片、图例色块、状态条与柱体（顶部圆角用 borderRadiusTopLeft/TopRight 原生片段）；Text 的 fontFamily/fontSize/fontStyle/color/textAlign/letterSpacing 与 CDATA 文本；rect/hline 绘制网格线、零线与分隔线。全部主体与图表由 DSL 构造，flawed-report.png 仅用于观察，未嵌入。

字体查询：中文用 Noto Sans CJK SC、数字与单位用 Inter（服务 /fonts 列表，缓存 docs/fonts.txt）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/20261104-145656-hy4all/A16/requests.jsonl`
迭代记录文件：`tmp/20261104-145656-hy4all/A16/iterations.jsonl`
渲染请求总数：2
成功次数：2
失败次数：0
重试请求数：0
DSL版本数：2
实际图片查看次数：3
完整视觉迭代数：1
未完成视觉迭代数：0
其他接口查询：`/ai-guide.md`、`/openapi.yaml`、`/fonts` 及文档站页面属共享准备，见 `tmp/20261104-145656-hy4all/_suite/requests.jsonl` 与 docs 缓存；本题不重复计为新增 HTTP 请求。

- **v1**（baseline，父版本 无）：查看 `outputs/<run_id>/A16/corrected-report.png (v1)` 发现：首版主图/利润明细/勘误均正确，但「重点季度」卡（412px 宽）内两段长正文换行后互相重叠并被卡片底部裁切。。改动：生成首版基线并实际打开全图查看。复查：确认 1 项版式缺陷，进入视觉迭代。
- **v2**（visual，父版本 v1）：查看 `outputs/<run_id>/A16/corrected-report.png (v2)` 发现：重点季度卡文字重叠溢出；利润明细卡与重点卡比例失衡。改动：利润明细卡收窄为 592px（列距 130）、重点卡加宽为 576px；重点卡文案拆成三行独立 22 号文本框（Q4 双高 / 较 Q3 增利 22 万 / Q3 回落 7 万），各占一行。复查：重新渲染并再次打开实际 PNG 复查：三行各占一行、无重叠无裁切；利润明细四列与 Q4 高亮完整；主图柱高、图例、勘误条全部正确，数据核对一致。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 |
|---|---|---|---|---|
| v1 / baseline / — | 首版主图/利润明细/勘误均正确，但「重点季度」卡（412px 宽）内两段长正文换行后互相重叠并被卡片底部裁切。 | 卡片过窄、两段文本框高度不足且 22 号正文自动换行 | 生成首版基线并实际打开全图查看 | 确认 1 项版式缺陷，进入视觉迭代 |
| v2 / visual / v1 | 重点季度卡文字重叠溢出；利润明细卡与重点卡比例失衡 | 实际渲染图观察：576px 宽度不足以容纳原两段 38/30 字文案 | 利润明细卡收窄为 592px（列距 130）、重点卡加宽为 576px；重点卡文案拆成三行独立 22 号文本框（Q4 双高 / 较 Q3 增利 22 万 / Q3 回落 7 万），各占一行 | 重新渲染并再次打开实际 PNG 复查：三行各占一行、无重叠无裁切；利润明细四列与 Q4 高亮完整；主图柱高、图例、勘误条全部正确，数据核对一致 |

踩坑：Y 轴从 100 起截断是原图最易被忽略的误导，必须用像素测量确认柱底在 100 线；图例颜色与系列对调不能只改文字，要核对柱顶数值到底属于收入还是成本；长中文正文在窄卡片里自动换行且可溢出容器边界，应拆成独立短行文本框而非依赖自动换行；正文≥22 的硬约束下不能靠缩小字号塞进文字。未遇到解析错误；服务渲染 2 次均成功。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/20261104-145656-hy4all/A16/task-metrics.json`

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-11-04T16:21:15+08:00 → 2026-11-04T17:04:41+08:00 | ISO8601+时区 | suite-state.json / 本地墙钟 |
| 任务总耗时 | 见 task-metrics.json | 秒 | 起止墙钟差；不与请求耗时求和 |
| 首次可用图耗时 | 近似首版渲染耗时 | 秒 | requests.jsonl 首条成功记录 |
| 等待用户反馈 | 0 | 秒 | 全套自动连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（未收到 429/503） | 秒 | requests.jsonl |
| 已记录请求耗时之和 | 11.628 | 秒 | requests.jsonl（可含重叠，不等于任务总耗时） |
| 成功、失败、重试请求 | 2 / 0 / 0 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 3 / 1 | 次 | iterations.jsonl 与实际查看记录 |

## 6. 设计选择、经验与未解决事项

以 source.csv 为唯一数据源，利润=收入−成本。主图 0–200 万元共同零起点、零线 y=500、1.25px/万元，四组左收入右成本，柱顶标注真实数值；底部左右分置利润明细与重点季度卡，再加一条原图勘误把「错在哪里」直接留在报告里，使叙事与勘误自洽。标题由 Q4 收入 180、利润 54 双最高论证，重点卡给出较 Q3 增利 22 万与 Q3 回落 7 万的数据依据。

最终实际图片已打开检查：四季分组柱图共用零起点且柱高对应数值、图例与单位正确、利润明细 30/27/32/54 万元、有数据依据的标题、Q4 重点论证与底部 6 条勘误均完整可读；findings.json 7 项问题与 3 项不确定项、corrected-data.json 的轴定义与计算值均已核对，据此标为完成。

临时目录中的 DSL 版本、原始请求/响应、脚本与记录均保留，未删除或覆盖任何尝试；总任务根 `.gitignore` 已建立，仅排除 `__pycache__/`、`*.pyc` 等运行时缓存，未忽略 `tmp/`、`outputs/` 或过程证据。

未解决事项：3 项不确定事项已独立记录在 findings.json 的 uncertainties（审美偏好、页脚稿件标注、数字标签与系列对调合并），未混作数值错。
