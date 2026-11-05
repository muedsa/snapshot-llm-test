# Snapshot 使用情况说明与踩坑记录 — A01

任务ID：A01
任务名称：六个月经营诊断驾驶舱
本次运行ID：20261104-145656-hy4all
完成状态：完成
结束原因：需求满足并完成视觉自检
输出目录：`outputs/20261104-145656-hy4all/A01/`
临时目录：`tmp/20261104-145656-hy4all/A01/`
路径基准：suite_root（记录内本地路径均相对总任务根；Markdown 链接相对本文档）

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `operations.png` | 1600×1000 经营驾驶舱 | `operations.snapshot` | 完成；服务真实 PNG，282145 字节 |
| `computed-data.json` | 每月计算值、汇总、图轴定义与结论引用数值 | — | 完成 |

同屏包含四张 KPI（总净收入 ¥918,624、总经营利润 ¥262,124、总订单 3,045 笔、期间总体转化率 11.15%）、六个月净收入与经营利润分组柱图（共用零起点与 0–220,000 元同一比例）、访问量与转化率两个共享月份对齐的小图（各自独立单位与数轴）、六行明细表（月份/净收入/退款率/利润/转化率，金额整数、比例两位小数）及有证据的管理结论。总体转化率按 3,045÷27,300=11.1538% 计算，不平均月比例（月均 11.19% 已标注区别）；退款率=退款÷退款前收入。正文≥20、脚注≥16，柱图零起点、金额与百分比分轴。

**逐图自检证据**：打开 outputs/…/A01/operations.png 两次（v1 首版、v2 修正版）。首版发现 KPI 右上英文标签换行溢出、左图轴单位与副标题重叠、柱顶数值为约数、月份标签与“月份”字样挤在一起、结论文字与底部数据块间距不足、转化率虚线标注压线；v2 逐项修复后再次打开实际 PNG 复查：短英文标签单行、轴单位并入副标题、柱顶改为精确金额 119,700…202,368、访问量改为精确 3,500…5,600、月份标签 04月–09月 完整且 09月 未裁切、结论文字与数据块分离、总体转化率改为带底色标注块且不再压线；表格 6 行数字右对齐、退款率 8.00% 高亮、最后一行 2026-09 完整；底部脚注完整可见。

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

使用 Snapshot 根节点 type=png + background；Stack 作为绝对定位画布，固定尺寸 Container 定义 1600×1000；Positioned 放置全部元素；Container 的 color/borderRadius/border/gradientType+gradientColors/gradientStops 实现卡片、渐变头部与柱体；Text 的 fontFamily/fontSize/fontStyle/color/textAlign 与 CDATA 文本；ClipPath SVG 路径实现斜线与几何面；Opacity 未使用。所有主体、图表、文字、图标均由 DSL 构造，无外部素材。

字体查询：/fonts 返回 Inter 系列、Noto Sans CJK SC、Noto Serif CJK SC、Noto Sans Mono CJK SC、DejaVu Sans 等；本题选 Noto Sans CJK SC 作中文、Inter 作数字与拉丁。缓存见 tmp/<run_id>/_suite/docs/fonts.txt。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/20261104-145656-hy4all/A01/requests.jsonl`
迭代记录文件：`tmp/20261104-145656-hy4all/A01/iterations.jsonl`
渲染请求总数：2
成功次数：2
失败次数：0
重试请求数：0
DSL版本数：2
实际图片查看次数：2
完整视觉迭代数：1
未完成视觉迭代数：0
其他接口查询：`/ai-guide.md`、`/openapi.yaml`、`/fonts` 及文档站页面属共享准备，见 `tmp/20261104-145656-hy4all/_suite/requests.jsonl` 与 docs 缓存；本题不重复计为新增 HTTP 请求。

- **v1**（baseline，父版本 无）：查看 `outputs/<run_id>/A01/operations.png (v1)` 发现：首版 KPI 英文长标签换行溢出；左图“金额/元”与副标题重叠；柱顶与访问量使用 k 约数；“月份”字样挤压 04月 标签；结论文字与底部数据块过近；CVR 虚线标注压线。。改动：生成首版基线并实际查看。复查：确认需修改，进入视觉迭代。
- **v2**（visual，父版本 v1）：查看 `outputs/<run_id>/A01/operations.png (v2)` 发现：上述 6 项缺陷。改动：英文标签缩短为 NET/PROFIT/ORDERS/CVR；删除独立轴单位标签并并入副标题；柱顶与访问量改精确数值；删除“月份”字样；结论文本框加高至 132px、底部数据块下移 12px；CVR 标注改为带底色圆角块并上移 23px。复查：再次渲染并打开实际 PNG 复查，6 项缺陷全部消除，数据/对齐/遮挡/裁切正常。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 |
|---|---|---|---|---|
| v1 / baseline / — | 首版 KPI 英文长标签换行溢出；左图“金额/元”与副标题重叠；柱顶与访问量使用 k 约数；“月份”字样挤压 04月 标签；结论文字与底部数据块过近；CVR 虚线标注压线。 | 实际渲染图观察 | 生成首版基线并实际查看 | 确认需修改，进入视觉迭代 |
| v2 / visual / v1 | 上述 6 项缺陷 | 实际渲染图逐项观察；标签宽度与中文换行行数估计不足 | 英文标签缩短为 NET/PROFIT/ORDERS/CVR；删除独立轴单位标签并并入副标题；柱顶与访问量改精确数值；删除“月份”字样；结论文本框加高至 132px、底部数据块下移 12px；CVR 标注改为带底色圆角块并上移 23px | 再次渲染并打开实际 PNG 复查，6 项缺陷全部消除，数据/对齐/遮挡/裁切正常 |

踩坑：Text 不做实体解码，含特殊字符必须用 CDATA（本题由 dsl.cdata() 统一处理）；Container 的 alignment 才能稳定垂直居中文字，fontSize 不是行盒高度；绝对值布局需在 Stack 中放一个固定尺寸 Container 作为画布基准；ClipPath 的子 Container 需与画布同尺寸才能让路径坐标等于画布坐标。这些均通过冒烟测试与 colortest 实际渲染确认。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/20261104-145656-hy4all/A01/task-metrics.json`

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-11-04T15:02:45+08:00 → 2026-11-04T15:05:42+08:00 | ISO8601+时区 | suite-state.json / 本地墙钟 |
| 任务总耗时 | 见 task-metrics.json | 秒 | 起止墙钟差；不与请求耗时求和 |
| 首次可用图耗时 | 近似首版渲染耗时 | 秒 | requests.jsonl 首条成功记录 |
| 等待用户反馈 | 0 | 秒 | 全套自动连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（未收到 429/503） | 秒 | requests.jsonl |
| 已记录请求耗时之和 | 10.963 | 秒 | requests.jsonl（可含重叠，不等于任务总耗时） |
| 成功、失败、重试请求 | 2 / 0 / 0 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 2 / 1 | 次 | iterations.jsonl 与实际查看记录 |

## 6. 设计选择、经验与未解决事项

采用深蓝渐变头部 + 白色卡片 + 单一强调色（蓝/青/琥珀/紫）的信息层级；KPI 行给出结论性数字，主图承担对比，两个小图承担趋势，底部明细表提供可核查数值，右侧深色结论卡把数字转成行动建议。金额图与百分比图使用完全独立的数轴并在标题/副标题显式标注单位，避免共用混淆。

最终实际图片已逐张打开检查：四 KPI、分组柱图、两个小图、六行明细表与管理结论均完整可读，数值与 computed-data.json 一致，柱图共用零起点且金额/百分比分轴，09月 标签与底部脚注无裁切，据此标为完成。

临时目录中的 DSL 版本、原始请求/响应、脚本与记录均保留，未删除或覆盖任何尝试；总任务根 `.gitignore` 已建立，仅排除 `__pycache__/`、`*.pyc` 等运行时缓存，未忽略 `tmp/`、`outputs/` 或过程证据。

未解决事项：无。
