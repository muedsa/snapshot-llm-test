# Snapshot 使用情况说明与踩坑记录 — A05

任务ID：A05
任务名称：不规则采样与缺测的仪表报告
本次运行ID：20261104-145656-hy4all
完成状态：完成
结束原因：需求满足并完成视觉自检
输出目录：`outputs/20261104-145656-hy4all/A05/`
临时目录：`tmp/20261104-145656-hy4all/A05/`
路径基准：suite_root（记录内本地路径均相对总任务根；Markdown 链接相对本文档）

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `sensor-report.png` | 1440×1000 三联趋势与明细 | `sensor-report.snapshot` | 完成；服务真实 PNG |
| `normalized-data.json` | 12 采样分钟偏移/null 缺测、三指标统计、逐指标连接段、负压采样点与共享/独立坐标轴 | — | 完成 |

08:00–12:30 共 270 分钟，x=190+minute×1190/270，三图共用真实时间比例横轴并对齐 12 条纵向参考线；温度/湿度在缺测采样点前后断开连线，不插值不补值；压差独立纵轴含清晰零线；每个真实读数有独立圆点标记，缺测以“—”/× 呈现；标注 09:40–10:50 的 3 个负压差采样点并明确不表示连续期间每一刻为负；上方三卡列出有效采样数与观察最小/最大值（温度 10 / 19.2–23.1 °C，湿度 11 / 34–41 %，压差 12 / −0.8–1.3 kPa）；下方 12 时点×3 指标简表，缺测用“—”；图例说明缺测与断线；正文≥20、轴/表≥18。

**逐图自检证据**：实际打开 sensor-report.png 三次（v1、v2、v3）。v1 发现 12 个不规则时刻轴标签互相挤压、纵轴标题与顶部刻度重叠、压差“零线 0 kPa”标注压住 12:30 数据点；v2 改为整点刻度（全部 12 时点交由表格承载）、纵轴标题移到 x=200、零线说明并入标题并加粗零线；v3 把底部脚注上移 10px 避免贴边裁切。最终图复查：三图纵轴单位/刻度清楚、缺测×与断线正确、压差零线清晰且末点无遮挡、整点刻度齐全、12 列表格“—”正确、脚注完整。

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

Stack 固定画布；Positioned 绝对定位；Container 纯色/圆角/边框；ClipPath 路径绘折线段；dashed_vline 绘对齐参考线；ClipPath 圆点由 Container borderRadius 实现；Text 的 fontSize/textAlign/fontFamily 与 CDATA；Opacity 半透明负压区段。全部由 DSL 构造。


## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/20261104-145656-hy4all/A05/requests.jsonl`
迭代记录文件：`tmp/20261104-145656-hy4all/A05/iterations.jsonl`
渲染请求总数：4
成功次数：3
失败次数：1
重试请求数：1
DSL版本数：3
实际图片查看次数：3
完整视觉迭代数：2
未完成视觉迭代数：0
其他接口查询：`/ai-guide.md`、`/openapi.yaml`、`/fonts` 及文档站页面属共享准备，见 `tmp/20261104-145656-hy4all/_suite/requests.jsonl` 与 docs 缓存；本题不重复计为新增 HTTP 请求。

- **v1**（baseline，父版本 无）：查看 `sensor-report.png (v1)` 发现：12 个不规则时刻轴标签互相重叠、纵轴标题压顶部刻度、零线标注压末点。改动：生成首版基线并查看。复查：记录 3 项缺陷。
- **v2**（visual，父版本 v1）：查看 `sensor-report.png (v2)` 发现：上述 3 项。改动：轴上只保留 6 个整点刻度，全部 12 时点放入下方表格并加说明；纵轴标题移到 x=200；零线说明并入标题、零线加粗。复查：重渲染并查看，3 项消除；发现底部脚注距画布底边仅 4px。
- **v3**（visual，父版本 v2）：查看 `sensor-report.png (v3)` 发现：底部脚注可能被裁切。改动：脚注上移至 y=974。复查：最终图脚注完整可见，其余元素不变。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 |
|---|---|---|---|---|
| v1 / baseline / — | 12 个不规则时刻轴标签互相重叠、纵轴标题压顶部刻度、零线标注压末点 | 实际渲染图观察 | 生成首版基线并查看 | 记录 3 项缺陷 |
| v2 / visual / v1 | 上述 3 项 | 实际渲染图观察；08:00 与 08:10 仅相隔 44px 而标签宽 104px | 轴上只保留 6 个整点刻度，全部 12 时点放入下方表格并加说明；纵轴标题移到 x=200；零线说明并入标题、零线加粗 | 重渲染并查看，3 项消除；发现底部脚注距画布底边仅 4px |
| v3 / visual / v2 | 底部脚注可能被裁切 | y=984+h20 超出 1000 画布 | 脚注上移至 y=974 | 最终图脚注完整可见，其余元素不变 |

踩坑：不规则采样的时刻标签不能等宽铺在真实比例轴上（08:00 与 08:10 只差 10 分钟≈44px），必须把完整时点清单移到表格，轴上只留整点；缺测绝不能用 0 或直线补值。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/20261104-145656-hy4all/A05/task-metrics.json`

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-11-04T15:45:52+08:00 → 2026-11-04T15:57:09+08:00 | ISO8601+时区 | suite-state.json / 本地墙钟 |
| 任务总耗时 | 见 task-metrics.json | 秒 | 起止墙钟差；不与请求耗时求和 |
| 首次可用图耗时 | 近似首版渲染耗时 | 秒 | requests.jsonl 首条成功记录 |
| 等待用户反馈 | 0 | 秒 | 全套自动连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（未收到 429/503） | 秒 | requests.jsonl |
| 已记录请求耗时之和 | 202.099 | 秒 | requests.jsonl（可含重叠，不等于任务总耗时） |
| 成功、失败、重试请求 | 3 / 1 / 1 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 3 / 2 | 次 | iterations.jsonl 与实际查看记录 |

## 6. 设计选择、经验与未解决事项

用同一 x 映射把三张图锁在同一时间轴，12 条浅色虚线贯穿三图形成可核对的对齐网格；每张图独立纵轴与单位，压差用加粗黑零线区分正负；缺测用×而非连线，负压时段用半透明红带但文字明确只代表 3 个采样点。

最终图逐项核对 12 时点、三指标有效数与极值、断线段与 normalized-data.json 的 segments 一致，负压说明措辞未越界推断，据此标为完成。

临时目录中的 DSL 版本、原始请求/响应、脚本与记录均保留，未删除或覆盖任何尝试；总任务根 `.gitignore` 已建立，仅排除 `__pycache__/`、`*.pyc` 等运行时缓存，未忽略 `tmp/`、`outputs/` 或过程证据。

未解决事项：无。
