# Snapshot 使用情况说明与踩坑记录 — A22

任务ID：A22
任务名称：真实数据更正与局部回归（预置三轮连续执行）
本次运行ID：20261104-145656-hy4all
完成状态：完成
结束原因：三轮按预置需求顺序全部完成、逐图看图与累计/轴/布局回归通过，累计报告/指标已生成
输出目录：`outputs/20261104-145656-hy4all/A22/`
临时目录：`tmp/20261104-145656-hy4all/A22/`
路径基准：suite_root（记录内本地路径均相对总任务根；Markdown 链接相对本文档）

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `round-01/dashboard.png` | 第1轮 1600×1000 六个月原始 CSV 驾驶舱 (v2 修复文字裁切) | `round-01/dashboard.snapshot` | 完成；服务真实 PNG 302543 字节 |
| `round-02/dashboard.png` | 第2轮 财务更正 + 9 月负利润负轴 (v2 修复图例) | `round-02/dashboard.snapshot` | 完成；服务真实 PNG 311785 字节 |
| `round-03/dashboard.png` | 第3轮 新增 2026-10 的 7 个月期间汇总 | `round-03/dashboard.snapshot` | 完成；服务真实 PNG 316530 字节 |
| `round-01/computed-data.json` | 第1轮逐月/汇总/轴/结论真实计算(applied_changes 空) | — | 完成 |
| `round-01/layout-map.json` | 第1轮 11 个主区域边界与主样式(comparison 空) | — | 完成 |
| `round-01/monthly.csv` | 第1轮实际使用的原始 6 月数据快照(原始 CSV 未修改) | — | 完成 |
| `round-02/computed-data.json` | 第2轮更正后真实计算(9 月利润 -5632、负轴 vmin=-20000) | — | 完成 |
| `round-02/layout-map.json` | 第2轮区域边界 + 对上轮分量差(全 0≤2px) | — | 完成 |
| `round-02/change-audit.json` | 第2轮两项更正的变更传播/未改内容/数据·轴·布局·图像回归(看图后已回填) | — | 完成 |
| `round-02/monthly.csv` | 第2轮含两项更正的 6 月数据快照 | — | 完成 |
| `round-03/computed-data.json` | 第3轮 7 个月真实计算(累计 1,121,424/252,924/3,685/11.10%) | — | 完成 |
| `round-03/layout-map.json` | 第3轮区域边界 + 对上轮分量差(全 0≤2px) | — | 完成 |
| `round-03/change-audit.json` | 第3轮新增 10 月传播/未改内容(2026-04 保留、更正继续有效)/回归(已回填) | — | 完成 |
| `round-03/monthly.csv` | 第3轮 7 个月数据快照 | — | 完成 |
| `round-01/snapshot-usage.md` | 第1轮单轮报告 | — | 完成 |
| `round-01/task-metrics.json` | 第1轮单轮指标 | — | 完成 |
| `round-02/snapshot-usage.md` | 第2轮单轮报告(含负轴/更正/图例修复) | — | 完成 |
| `round-02/task-metrics.json` | 第2轮单轮指标 | — | 完成 |
| `round-03/snapshot-usage.md` | 第3轮单轮报告(含 7 个月回归) | — | 完成 |
| `round-03/task-metrics.json` | 第3轮单轮指标 | — | 完成 |

A22 为预置三轮连续执行(round_execution=preloaded_sequential, blind_feedback=false)：先按 TASK.md/task.json 完成 round-01 并归档，再读 rounds/round-02.md 完成 round-02，再读 rounds/round-03.md 完成 round-03；不等待外部反馈、不编造未来意见、不覆盖前轮。round-01：用 inputs/monthly.csv 原始 6 个月做 1600×1000 驾驶舱，四 KPI(总净收入/总经营利润/总订单/总体转化率)、净收入=收入−退款、利润=净收入−operating_cost、总体率=总订单/总 sessions；净收入/利润共用零起点柱图、六行月份/净收入/利润/退款率/转化率表、仅根据实际数值成立的主结论；正文≥22；交付 dashboard.png/.snapshot、computed-data.json、layout-map.json。round-02：2026-08 refund 15048→25048、2026-09 cost 138000→208000(其余不变)，重算每月/汇总/KPI/图表/表格/结论，允许在原柱图区域内增加负轴范围，保持画布与主区域边界±2px/主字体/视觉系统，不得把负值裁掉、画成正值或只修数字不修柱高，另交 change-audit.json。round-03：新增 2026-10(640/224000/11200/142000/5900)，两项更正继续有效，KPI 改 7 个月汇总、图与表含全部 7 个月、最后月份 2026-10、区域边界±2px、正文≥22、不得省略 2026-04 或恢复旧数据，核对累计/轴/结论并真实看图。三轮共同口径：金额整数元、比率分子/分母与未舍入值保留、Decimal ROUND_HALF_UP 两位小数、总体率按总订单/总访问量不平均月比例、先未舍入计算后格式化；只应用轮次指定更正/新增月份，不修改原始 CSV。task.json 顶层清单为全轮次最终交付、路径相对本题输出根不双重拼接；任务根另写累计 snapshot-usage.md/task-metrics.json，每轮另有单轮报告/指标。用户指令另要求 monthly.csv 与 computed-data.json 按各轮要求交付，故各轮附 monthly.csv 数据快照。

**逐图自检证据**：严格按 round-01→round-02→round-03 顺序连续执行，各轮先完成、看图、归档再读下一轮；全程共 5 次 ViewImage 真实打开(round-01 v1/v2、round-02 v1/v2、round-03 首版)。计算核对：round-01 汇总 net 918624/profit 262124/orders 3045/sessions 27300/cvr 11.15%；round-02 更正后 net 908624/profit 182124、8 月退款率 13.32%、9 月利润 -5632、负轴 vmin=-20000 zero_y=599.69；round-03 7 个月 net 1121424/profit 252924/orders 3685/cvr 11.10%、首 2026-04 末 2026-10、两项更正继续有效、9 月仍负。布局回归：layout-map.json 的 round-02/03 comparison 对上一轮 11 个主区域 box 分量差全 0≤2px，主字体/字号/色彩/视觉系统不变。视觉回归：负利润柱在 round-02/03 均红色向下画到零线以下、带 -5,632 标签、未被裁/未画正/柱高按重算值；round-03 柱图 7 组、表格 7 行(行距 26px)、两小图 7 个月、KPI/结论 7 个月口径。change-audit.json(round-02/03) 的 changes/preserved/regression 齐全，visual_review 项已由 round_report.py 在真实看图后回填、status=reviewed。3 张最终 PNG 文件头均 89 50 4E 47、尺寸 1600×1000、均有同名 .snapshot；round-01/02 的 v1 失败版(PNG/DSL/JSON/CSV/build.py 脚本)完整保留在 tmp/<run_id>/A22/round-XX/v1/，前轮未被覆盖。各轮 monthly.csv 为该轮计算所用数据快照，原始 inputs/monthly.csv 未修改。

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

Snapshot(png)+Stack/Positioned 固定 1600×1000 画布；Container(gradient/color/borderRadius/border/Opacity) 画渐变头部、4 张 KPI 卡、柱图/两小图/表格/结论卡、分组柱体与浅红负轴区；rect/bar 按同一零线与比例绘制净收入/利润柱(负值向下、红色)；ClipPath line 画转化率折线；dashed_hline 画总体转化率虚线；Text(fontFamily/fontSize/fontStyle/textAlign+CDATA) 画全部文字(正文≥22)。所有主体/图表/文字由 DSL 构造，无外部图片、无整图嵌入。

字体查询：沿用 /fonts 缓存：中文 Noto Sans CJK SC、拉丁/数字 Inter，缓存见 tmp/<run_id>/_suite/docs/fonts.txt。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/20261104-145656-hy4all/A22/requests.jsonl`
迭代记录文件：`tmp/20261104-145656-hy4all/A22/iterations.jsonl`
渲染请求总数：5
成功次数：5
失败次数：0
重试请求数：0
DSL版本数：5
实际图片查看次数：5
完整视觉迭代数：2
未完成视觉迭代数：0
其他接口查询：`/ai-guide.md`、`/openapi.yaml`、`/fonts` 及文档站页面属共享准备，见 `tmp/20261104-145656-hy4all/_suite/requests.jsonl` 与 docs 缓存；本题不重复计为新增 HTTP 请求。

- **v1**（baseline，父版本 无）：查看 `round-01/dashboard.png (v1)` 发现：首版四 KPI/6 组柱图/6 行表格/两小图/结论均正确且数据无误；但底部脚注、表格右上副标题、结论卡末行文字因文字盒宽/高不足被裁切。。改动：按 TASK.md 原始 6 月 CSV 建立首版驾驶舱 DSL 与审计 JSON 并实际查看。复查：确认 3 处文字裁切缺陷，进入 v2 视觉修复。
- **r1-v2**（visual，父版本 v1）：查看 `round-01/dashboard.png (v2)` 发现：v1 的脚注/副标题/结论文字裁切；KPI/柱图/表格/小图无误。。改动：缩短脚注与三轮结论文案、表格副标题盒加宽(196→266)、结论文字盒加高(150→162)、数据块下移(872→884)、脚注盒 y 962→960 高 26→28；v1 全部产物归档 tmp/A22/round-01/v1/。复查：重渲染并再次打开实际 PNG 复查：3 处裁切全部消除，脚注/副标题/结论/数据块完整，KPI/柱图/表格/小图无回归，accept 为 round-01 最终。
- **r2-req**（requirement-change，父版本 r1-v2）：查看 `round-02/dashboard.png (v1)` 发现：按 round-02.md 应用两项财务更正后，负柱/负轴/−20k 刻度/零线/KPI(908,624/182,124)/8 月 13.32%/9 月 -5,632/结论/脚注均正确；但柱图第三图例『负值』被裁成单字『负』且与『经营利润』图例挤在一起。。改动：2026-08 refund 15048→25048、2026-09 cost 138000→208000；重算全量、柱图 y 轴 vmin 0→-20000 加负轴、9 月利润柱转红向下、KPI/表格/结论更新、生成 change-audit.json。复查：确认 v1 图例缺陷，进入 v2 视觉修复迭代。
- **r2-v2**（visual，父版本 r2-req）：查看 `round-02/dashboard.png (v2)` 发现：v1 图例『负值』裁成『负』且与经营利润图例文字盒重叠；其余元素正确。。改动：三组图例重排 x(634/766/906)、『负值』文字盒 40→56px；数据/轴/区域/公式均未改；v1 全部产物归档 tmp/A22/round-02/v1/。复查：重渲染并再次打开实际 PNG 复查：三图例完整分开、『负值』两字完整，负柱/负轴/KPI/13.32%/-5,632/结论/脚注无回归，accept 为 round-02 最终；change-audit 的 visual_review 看图后回填。
- **r3-req**（requirement-change，父版本 r2-v2）：查看 `round-03/dashboard.png` 发现：按 round-03.md 新增 2026-10 后，7 个月标题/KPI(1,121,424/252,924/3,685/11.10%)/7 组柱图/7 行表格/7 点小图/7 个月结论逐项检查，未发现视觉缺陷。。改动：新增 2026-10 行、KPI 改 7 个月汇总、柱图 6→7 组、表格 6→7 行(行距 31→26)、两小图 6→7 月、结论 7 个月口径；两项更正继续有效、2026-04 保留；生成 change-audit.json。复查：首版即达标：2026-04 未省略、2026-10 为最后月份、9 月红色负柱仍在、累计值/轴/结论核对一致、布局 comparison 全 0≤2px、脚注/结论/图例完整无裁切；accept 为 round-03 最终，不制造迭代。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 |
|---|---|---|---|---|
| v1 / baseline / — | 首版四 KPI/6 组柱图/6 行表格/两小图/结论均正确且数据无误；但底部脚注、表格右上副标题、结论卡末行文字因文字盒宽/高不足被裁切。 | 实际渲染图观察 | 按 TASK.md 原始 6 月 CSV 建立首版驾驶舱 DSL 与审计 JSON 并实际查看 | 确认 3 处文字裁切缺陷，进入 v2 视觉修复 |
| r1-v2 / visual / v1 | v1 的脚注/副标题/结论文字裁切；KPI/柱图/表格/小图无误。 | 实际 v1 图观察；22px 正文在 196px 盒(11 字副标题)、1000px 盒(50+ 字脚注)、150px 高结论盒(6 行)放不下，且结论被下方数据块压住 | 缩短脚注与三轮结论文案、表格副标题盒加宽(196→266)、结论文字盒加高(150→162)、数据块下移(872→884)、脚注盒 y 962→960 高 26→28；v1 全部产物归档 tmp/A22/round-01/v1/ | 重渲染并再次打开实际 PNG 复查：3 处裁切全部消除，脚注/副标题/结论/数据块完整，KPI/柱图/表格/小图无回归，accept 为 round-01 最终 |
| r2-req / requirement-change / r1-v2 | 按 round-02.md 应用两项财务更正后，负柱/负轴/−20k 刻度/零线/KPI(908,624/182,124)/8 月 13.32%/9 月 -5,632/结论/脚注均正确；但柱图第三图例『负值』被裁成单字『负』且与『经营利润』图例挤在一起。 | 实际渲染图观察 | 2026-08 refund 15048→25048、2026-09 cost 138000→208000；重算全量、柱图 y 轴 vmin 0→-20000 加负轴、9 月利润柱转红向下、KPI/表格/结论更新、生成 change-audit.json | 确认 v1 图例缺陷，进入 v2 视觉修复迭代 |
| r2-v2 / visual / r2-req | v1 图例『负值』裁成『负』且与经营利润图例文字盒重叠；其余元素正确。 | 实际 v1 图观察；第三图例文字盒 40px 放不下 2 个 22px 汉字，且 x=920 落在经营利润文字盒 836~976 内 | 三组图例重排 x(634/766/906)、『负值』文字盒 40→56px；数据/轴/区域/公式均未改；v1 全部产物归档 tmp/A22/round-02/v1/ | 重渲染并再次打开实际 PNG 复查：三图例完整分开、『负值』两字完整，负柱/负轴/KPI/13.32%/-5,632/结论/脚注无回归，accept 为 round-02 最终；change-audit 的 visual_review 看图后回填 |
| r3-req / requirement-change / r2-v2 | 按 round-03.md 新增 2026-10 后，7 个月标题/KPI(1,121,424/252,924/3,685/11.10%)/7 组柱图/7 行表格/7 点小图/7 个月结论逐项检查，未发现视觉缺陷。 | 实际渲染图观察 | 新增 2026-10 行、KPI 改 7 个月汇总、柱图 6→7 组、表格 6→7 行(行距 31→26)、两小图 6→7 月、结论 7 个月口径；两项更正继续有效、2026-04 保留；生成 change-audit.json | 首版即达标：2026-04 未省略、2026-10 为最后月份、9 月红色负柱仍在、累计值/轴/结论核对一致、布局 comparison 全 0≤2px、脚注/结论/图例完整无裁切；accept 为 round-03 最终，不制造迭代 |

踩坑：(1) round-01 v1 文字盒宽/高估计不足导致脚注/副标题/结论裁切——缩短文案 + 加宽/加高盒 + 数据块下移修复；(2) round-02 v1 柱图第三图例『负值』文字盒 40px 放不下 2 个 22px 汉字且与经营利润图例重叠——三组图例重排并加宽修复；(3) 负利润 -5632 相对 20 万量级很小、负柱仅约 5.7px，故用红色柱 + 显式 '-5,632' 标签 + 表格/结论负值，确保不裁/不画正/柱高随值重算；(4) 比率四舍五入必须用 Decimal ROUND_HALF_UP(Python 内置 round 为 HALF_EVEN，恰好半单位行为不同)；(5) 多轮为避免 render_all.py --fresh 覆盖前轮归档 PNG，round-01 用 render_all.py 渲染、round-02/03 用 render.py 按文件精确渲染，日志按 round-XX/ 子目录分开。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/20261104-145656-hy4all/A22/task-metrics.json`

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-11-04T17:00:00+08:00 → 2026-11-04T17:23:55+08:00 | ISO8601+时区 | suite-state.json / 本地墙钟 |
| 任务总耗时 | 见 task-metrics.json | 秒 | 起止墙钟差；不与请求耗时求和 |
| 首次可用图耗时 | 近似首版渲染耗时 | 秒 | requests.jsonl 首条成功记录 |
| 等待用户反馈 | 0 | 秒 | 全套自动连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（未收到 429/503） | 秒 | requests.jsonl |
| 已记录请求耗时之和 | 21.942 | 秒 | requests.jsonl（可含重叠，不等于任务总耗时） |
| 成功、失败、重试请求 | 5 / 0 / 0 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 5 / 2 | 次 | iterations.jsonl 与实际查看记录 |

## 6. 设计选择、经验与未解决事项

以参数化 build.py 按 --round 顺序生成三轮(不预先生成后续轮)：固定 REGIONS 11 个主区域(跨轮 box 完全相同，comparison 分量差 0)与稳定视觉系统；data_for(n) 只应用轮次指定的更正/新增行(原始 CSV 不改)，compute() 用 Decimal 未舍入值全量重算逐月/汇总/KPI/轴/结论，axes_for(n) 在负利润轮次把 vmin 由 0 降到 -20000 并上移零线，柱图按同一比例把负值向下绘制。每轮另写 monthly.csv 数据快照(用户要求)、computed-data.json(计算证据)、layout-map.json(区域证据)、round-2/3 的 change-audit.json(变更传播/未改/回归，看图后回填 visual_review)。round_report.py 生成每轮报告/指标并回填 change-audit 图像核验；任务根累计由 finalize.py 汇总三轮。

三轮 3 张最终 PNG 均逐张实际打开检查：round-01 经 v1→v2 修复裁切、round-02 经 v1→v2 修复图例且负轴/负柱/更正传播正确、round-03 七个月首版达标；前两轮 v1 失败版与前轮产物完整保留、变化与回归证据齐全、累计报告/指标已生成，据此标为完成。连续执行模式：未来需求可提前访问，报告如实注明非隐藏反馈盲测、未编造外部意见。

临时目录中的 DSL 版本、原始请求/响应、脚本与记录均保留，未删除或覆盖任何尝试；总任务根 `.gitignore` 已建立，仅排除 `__pycache__/`、`*.pyc` 等运行时缓存，未忽略 `tmp/`、`outputs/` 或过程证据。

未解决事项：无。各轮 monthly.csv 为额外交付的数据快照(不修改原始输入)；v1 失败尝试全部过程证据保留。
