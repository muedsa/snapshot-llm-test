# Snapshot 使用情况说明与踩坑记录

任务ID：A16
任务名称：从错误图表恢复可信叙事
本次运行ID：run-20261011-01
完成状态：完成
结束原因：需求满足并完成逐图视觉自检
输出目录：`outputs/run-20261011-01/A16/`（路径基准：suite_root）
临时目录：`tmp/run-20261011-01/A16/`（路径基准：suite_root）
路径基准：suite_root；除本报告的 Markdown 本地链接（相对本文件所在目录）外，
所有记录中的本地路径均为相对 suite_root 的相对路径，未写死机器盘符或用户目录。

遵循 [PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录环境变量。
Markdown 本地链接相对当前文档；本报告位于 `outputs/<run_id>/A16/`，
故指向题库文档的链接为 `../../../tasks/…`。

## 1. 最终产物与需求完成情况


| 文件 | 用途 | 对应 DSL 或图 | 完成状态 |
|---|---|---|---|
| `corrected-report.snapshot` | 重制报告定稿 DSL | `corrected-report.png` | 已完成 |
| `corrected-report.png` | 服务返回的最终图 1280×900 | 同名 `.snapshot` | 已完成，服务原始响应 |
| `findings.json` | 7 条问题的位置/现象/数据核对/影响/修正/查看结果 + 4 条不确定项 | — | 已完成 |
| `corrected-data.json` | 四季收入/成本/利润、轴定义与全部柱几何、结论与引用字段 | — | 已完成 |
| `snapshot-usage.md` / `task-metrics.json` | 报告与指标 | — | 已完成 |

需求逐项核对（依据**实际打开查看**：原图整屏 + 5 处 2×/3× 局部放大；定稿整屏 + 5 处局部放大）

| 题目要求 | 满足情况 | 证据 |
|---|---|---|
| 先实际查看图，逐项给出可观察证据 | 满足 | 原图整屏查看 + 6 张局部放大（轴、Q1/Q2 柱、Q3/Q4 柱、利润卡与标注卡、页眉、图例）全部在 `tmp/…/preview/flawed-*.png` |
| 不按常见错误凭空列坑 | 满足 | `checked_but_not_errors` 记录三项**量过但确认不构成错误**的地方（图例顺序、四季齐全、卡片样式）；`uncertainties` 4 条只写无法从图或数据判断的部分并注明所需证据 |
| `source.csv` 为唯一可信原始数据 | 满足 | 构建脚本只读该文件；`corrected-data.json.source.modified = false`；标题与标注卡的每个数字都能回溯到该文件的两列 |
| 图片与源码不是标准答案 | 满足 | 原图只被 `probe_flawed*.py` / `crop_flawed_a16.py` 读取像素用于测量；DSL 中无 `<Image>` |
| 重制为 1280×900 | 满足 | 服务 `image_info` 为 PNG 1280×900 |
| 四季收入/成本分组柱图 | 满足 | 4 组 × 2 柱，共 8 根；`corrected-data.json.axes.bars` 逐根记录 |
| 共同零起点 | 满足 | 刻度 0/50/100/150/200，基线 y=512 为 0；8 根柱底全部落在 0 线（`bar_bottom_on_zero_line` 全 true） |
| 利润明细 | 满足 | 五列五行表（季度/收入/成本/利润/利润率），数值全部由 CSV 现算 |
| 一条有数据依据的标题 | 满足 | 「季度复盘：Q4 收入与利润双双创高」；`conclusion.evidence` 给出 4 条引用字段与取值，Q4 在收入/利润/利润率三项上均为 max |
| 图例 | 满足 | 「收入（蓝）/ 成本（橙）」，顺序与分组内柱序一致 |
| 单位「万元」 | 满足 | 图表卡内「单位：万元」+ 利润卡标题「利润明细（万元）」+ 页脚三处 |
| 全部季度 | 满足 | Q1–Q4 齐全，柱、分组标签、明细表行一一对应 |
| 保持「季度复盘」主题 | 满足 | 标题仍以「季度复盘」开头，卡片结构仍是「图表 + 利润明细 + 重点观察」 |
| 风格允许改进 | 满足 | 加了重点季度高亮行、利润率列、共用比例的坐标轴 |
| 柱高对应数值，不能只修数字标签 | 满足 | 柱高 = value × 1.32 与刻度同源；反测 8 根柱高度误差 −0.80…+0.04 px |
| 重点季度由数据论证 | 满足 | Q4；论据（收入 180 / 成本 126 / 利润 54 / 利润率 30.0% / 四季利润 30/27/32/54）直接印在标注卡上 |
| findings.json 每项含图片位置 | 满足 | 每条含 `location_in_original`（像素框/刻度/柱体 box）与 `evidence_image` |
| 每项含现象 | 满足 | `observed` |
| 每项含源数据核对 | 满足 | `source_data_check`（含 `checked_field` / 取值 / `conclusion`） |
| 每项含影响 | 满足 | `impact` |
| 每项含修正 | 满足 | `correction` |
| 每项含最终查看结果 | 满足 | `final_visual_check`，每条都指向定稿的具体局部图 |
| 未确认部分独立记录为不确定 | 满足 | `uncertainties` 4 条，每条含 `what_is_known` / `why_unconfirmed` / `needed_evidence` / `how_handled` |
| 避免把审美偏好混作数值错 | 满足 | 图例顺序等三项进 `checked_but_not_errors`，不进 `findings` |
| corrected-data.json 含计算与轴定义 | 满足 | `quarters`（含利润与利润率的推导）、`axes`（共同零点、上限、刻度、px_per_unit 及推导式、plot_rect、8 根柱的 x/y/宽/高、网格线表、cross_check） |
| corrected-data.json 含结论 | 满足 | `conclusion`（headline / emphasis_quarter / 4 条 evidence 含引用字段与取值 / 被否掉的错误结论及原因） |
| 正文 ≥22 | 满足 | 副标题 22、图例 22、季度标签 22、利润表单元格 22、标注卡正文 22；自检脚本判定 body_min = 22 |
| 标注 ≥18 | 满足 | 单位 18、轴刻度 18、柱顶标签 18、表头 18、页脚 18；自检脚本判定 annot_min = 18 |
| 无外部图像 | 满足 | DSL 中无 `<Image>`；`verify.json.image_tag_used = false` |
| 所有指定最终 PNG 是服务真实响应且有同名 `.snapshot` | 满足 | 交付 PNG 由服务端返回，DSL 为同一份 |



## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com（与总 run-config.json 的 `service_base_url` 一致，覆盖子题默认地址）
文档访问日期：本次运行当天；字体清单由 `GET /fonts` 实际取得并缓存

AI 使用指南：https://open-snapshot.muedsa.com/ai-guide.md
实际阅读情况：已按指南使用 `POST /snapshot`（请求体为 UTF-8 纯文本 DSL，非 JSON），
按指南要求检查 HTTP 状态与 `Content-Type` 后才使用图片；遇到 `400 PARSE_ERROR`
时按响应 `message` 中的位置修正 DSL 后重新提交；未使用 `?errorImage=png`，
以保证错误 JSON 可被程序读取。字体通过 `GET /fonts` 查询后按返回值书写 `fontFamily`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|

| https://open-snapshot.muedsa.com/ai-guide.md | `POST /snapshot` 请求体为 UTF-8 纯文本 DSL（非 JSON）；成功返回图片二进制；失败返回含 `code`/`message`/`requestId` 的 JSON，按 `message` 中的 `position` 定位修正；`GET /fonts` 返回 text/plain 字体族列表 | `_suite/scripts/snapshot_render.py` |
| https://snapshot.muedsa.com/reference/parser-tags/ | 38 个标签的完整属性表（`Container`/`Stack`/`Positioned`/`Text`/`Flex`/`ClipOval`/`ClipRRect`/`Transform` 等） | `snapkit.py` 与各题 DSL |
| https://snapshot.muedsa.com/reference/enums/ | 枚举取值（`CrossAxisAlignment`、`BorderStyle`、`FlexFit`、`StackFit` 等）；已确认 `BorderStyle` 仅 `NONE`/`SOLID`、`CrossAxisAlignment` 无 `BOTTOM` | 各题构造器中的枚举取值 |

字体：实际调用 `GET /fonts` 取得 27 个字体族，原始响应留存于
`tmp/<run_id>/_suite/responses/`（`request_type=fonts`），整理副本见 `tmp/<run_id>/_suite/fonts-list.txt`。
中文正文用 `Noto Sans CJK SC`，拉丁与数字用 `Inter` 系列。本套 A 类任务素材政策为 `dsl_only`，
全部主体由 DSL 构造，**未使用 `<Image>` 标签**，未引入任何外部图片素材。

| https://snapshot.muedsa.com/reference/parser-tags/ · Text | 文本按给定框排版，超出部分会被裁 | 首版利润表单元格给 20px 是主动选择而非渲染限制；按题面「正文 ≥22」统一提到 22px |
| https://snapshot.muedsa.com/reference/parser-tags/ · Container | `borderRadius` 必须大于 `border` 宽度 | 卡片圆角 14px > 1px 描边，安全；A13 已实测该限制 |


本次实际用到的能力：布局：`Container`/`Column`/`Row`/`Expanded`/`SizedBox`/`Padding`；精确定位：`Stack(fit=EXPAND)` + `Positioned`；文本：`Text` 的 `fontFamily`/`fontSize`/`textAlign`/`height`/`maxLines`/`letterSpacing`；颜色与透明度：CSS 颜色与 `#RRGGBBAA` 独立 alpha；装饰：`border`（宽度+样式+颜色）、`borderRadius` 与四角圆角、`boxShadow`；裁剪：`ClipRRect`/`ClipOval`；变换：`Transform` 的列主序 4×4 矩阵 + `alignment`；滤镜：`ImageFiltered`（子树模糊）、`BackdropFilter`（仅背景模糊）；渐变：`gradientType=LINEAR/RADIAL/SWEEP` + `gradientColors`/`gradientStops`。解析器未提供 `ClipPath`/多边形，所有图形均由矩形、圆角矩形、椭圆与渐变拼装。
本题额外用到：**把「柱高」和「标签」和「刻度」收敛到同一个函数**，让三者结构上不可能不一致：`y = 512 − value × 1.32`、`height = value × 1.32`，标签直接取 `str(value)`。反测 8 根柱的高度误差在 −0.80…+0.04 px、x 误差 ≤0.75 px、柱底全部落在 0 线。
**用原图自己的坐标轴去量原图自己的柱子**：因为坐标轴与柱子在同一张图里，「柱顶在轴上读出多少」是一个自洽的量，不依赖任何外部真值；这让「柱高与标签不成比例」成为可计算、可复核的发现，而不是观感判断。
**净空检查避免自造「常见错误模板」**：先量出图例顺序、季度是否齐全、卡片描边等，逐项确认它们是否构成矛盾；确认不构成矛盾的写进 `checked_but_not_errors`，无法确认是否错误的写进 `uncertainties` 并注明需要什么证据。

字体：实际查询 `GET /fonts` 得到 27 个字体族，原始响应留存于
`tmp/run-20261011-01/A16/responses/`（request_type=fonts），另有整理副本 `outputs/run-20261011-01/A16/../_suite/fonts-list.txt`。
中文正文使用 `Noto Sans CJK SC`，数字/拉丁使用 `Inter` 系列，代码/等宽使用 `Noto Sans Mono CJK SC`。
题目素材政策为纯 DSL，未使用任何外部图片（`<Image>` 标签本次未使用）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/run-20261011-01/A16/requests.jsonl`
迭代记录文件：`tmp/run-20261011-01/A16/iterations.jsonl`
响应与草稿留痕：`tmp/run-20261011-01/A16/responses/`、`tmp/run-20261011-01/A16/drafts/`

渲染请求总数：3
成功次数：3
失败次数：0
重试请求数：0（是总请求的子集）
DSL版本数：3
实际图片查看次数：15
完整视觉迭代数：2
未完成视觉迭代数：0
其他接口查询：字体查询与文档读取为 run 级共享准备；本题的渲染请求共 3 次（首版、字号修正版、定稿），其余全部为本地 PIL 勘察与核验脚本。

初次生成和查看计为基线，不计为改进迭代。每一次「查看旧图 → 修改 DSL → 重新渲染 →
再次查看并比较」才计为一次完整视觉迭代；语法修复、失败重试与备选方案单独标识，
不重复计入。所有图片均已用图像工具实际打开查看（含整屏与放大局部）。

| 请求ID | 输入 DSL | 耗时 | HTTP / Content-Type | 响应文件 | 查看与实际结果 |
|---|---|---|---|---|---|
| A16-v1-cf44e676 | drafts/a16-corrected-report-v1.snapshot | 2.28s | 200 image/png | preview/corrected-report-v1.png | 首版整屏打开：版式成立；自检脚本判定字号门槛不过（表单元/图例/季度标签 20px < 22px） |
| A16-v2-cfc66a83 | drafts/a16-corrected-report-v1.snapshot | 2.42s | 200 image/png | preview/corrected-report-v2.png | 正文类文字统一提到 22px 后重渲；自检 8/8 柱高、5/5 网格线、字号门槛全过 |
| A16-final-* | outputs/run-20261011-01/A16/corrected-report.snapshot | 见 metrics | 200 image/png | outputs/run-20261011-01/A16/corrected-report.png | 定稿渲染并对交付 PNG 重跑柱高/刻度/字号核验 |

## 4. 修改记录与踩坑

| 版本 / 类型 | 观察到的实际问题 | 原因及确认依据 | 实际修改 | 复验结果 |
|---|---|---|---|---|
| probe · measurement | 原图柱高看起来「差不多对」，但说不清差在哪 | 只靠肉眼看柱高，没有把柱顶换算成轴上的值 | 写 `probe_flawed2_a16.py` 排除图例色块干扰后重测 8 根柱的 x/y/高度，再用原图自己的刻度做 `value(y) = 100 + (565 − y) / 2.7` 换算 | 得到可计算的自洽证据：蓝柱轴上读数 155.6/163.7/173.3/191.1 对标签 120/135/128/180，橙柱 140.7/150.0/147.4/161.1 对 90/108/96/126 |
| probe · alternative | 差点把「图例把成本排在收入前面」也写成一条问题 | 这类图表容易让人联想到「图例顺序与柱序不一致」的常见坑 | 量出图例文字框 [908,185,944,203]=成本、[1087,185,1123,203]=收入，同时量出每组内蓝左橙右的柱序，两者是自洽的 | 写进 `checked_but_not_errors`，不计入 findings——避免把偏好当错误 |
| v1 → v2 · visual | 利润表单元格、图例、季度标签都是 20px，低于题面「正文 ≥22」 | 首版按「表内数字属于标注」归类，但表格里的季度名与数值属于叙事正文 | 把正文类文字（副标题、图例、季度标签、表内 8 类文字、标注卡正文）统一提到 22px，标注类（单位、轴刻度、柱顶标签、表头、页脚）保持 18px；表头与列位重排 | 自检 body_min = 22、annot_min = 18，门槛通过；2× 放大复查利润表与标注卡无截断 |
| v2 · verification | 网格线核验一度报出 264px 的巨误差 | 核验脚本把实测网格线按图像自上而下的 y 升序，与按刻度升序（0→200）的声明值直接相比 | 比较前把实测序列反转为刻度序再逐条比 | 5 条网格线误差全部为 0.0px |
| v2 · verification | `all_passed` 在误差为 0 时仍然算出 False | 判据写成 `max_error or 99`，而 0.0 在 Python 里是假值，被当成「没测到」 | 改成显式的 `is not None` 判断 | 定稿 all_passed = true；也修正了 A15 核验脚本里同类的写法 |

「渲染成功但视觉不符合要求」的问题同样记录在上面的完整视觉迭代中。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/run-20261011-01/A16/task-metrics.json`


| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始 / 结束时间 | 2026-10-12T10:51:15.092+08:00 / 2026-10-12T11:00:46.565+08:00 | ISO8601 带时区 | 计时记录（本地时钟，带时区） |
| 任务总耗时 | 571.473 | 秒 | 墙钟时间（读题 → 计算 → 构造 → 渲染 → 看图 → 修复 → 报告） |
| 首次可用图耗时 | 2.28 | 秒 | 从开始到首个 `200 image/png` 且能打开的图为止的全部请求耗时之和；本任务请求串行，故与实际顺序一致 |
| 等待用户反馈 | 0.0 | 秒 | 本题为单轮任务，无多轮反馈等待 |
| 限流等待 | 0.0 | 秒 | 全程未出现 `429`（见 `requests.jsonl`） |
| 排队等待 | None | 秒 | 服务未提供排队指标，不可测量，记 null 而非 0 |
| 已记录请求耗时之和 | 7.127 | 秒 | `requests.jsonl` 中 `duration_seconds` 求和；请求串行，不与墙钟重复计入 |
| 成功 / 失败 / 重试请求 | 3 / 0 / 0 | 次 | `requests.jsonl`；失败均为不同 DSL 的语法修复，非同一请求重试 |
| 看图 / 完整视觉迭代 | 15 / 2 | 次 | `iterations.jsonl` 与实际图像查看记录 |
| DSL 版本数 | 3 | 个 | `requests.jsonl` 去重 |
| Server-Timing | null | — | 服务响应未返回该头，日志中如实记为 null |


## 6. 设计选择、经验与未解决事项


**关键设计选择**

1. *把「柱高 ↔ 标签 ↔ 刻度」收敛成一个函数*。定稿里
   `value_y(v) = 512 − v × 1.32`，柱高就是 `v × 1.32`，柱顶标签就是 `str(v)`。
   三者是同一个表达式的三次求值，因此**结构上不可能不一致**——
   这比「仔细对齐一次」可靠得多。反测结果：8 根柱高度误差 −0.80…+0.04 px、
   x 误差 ≤0.75 px、5 条网格线误差 0.0 px、柱底全部落在 0 线。

2. *用原图自己的轴去量原图自己的柱*。这是本题最有用的一招：
   坐标轴和柱子同处一张图，所以「柱顶在轴上读出多少」是一个**自洽的量**，
   完全不需要外部真值。量出来蓝柱顶分别是 155.6 / 163.7 / 173.3 / 191.1，
   而标签写的是 120 / 135 / 128 / 180——F03 就这样从「看着有点高」变成了可计算的结论。
   再补一句「同一系列内 柱高÷标签 从 1.25 漂到 1.54」，就排除了「只是整体缩放」的解释。

3. *把「不确定」和「不是错误」也写进交付物*。`findings.json` 除了 7 条 findings，
   还有 4 条 `uncertainties`（截断轴是否有意、42 的来源、原图柱高的比例规则、收入/成本口径）
   和 3 条 `checked_but_not_errors`（图例顺序、四季齐全、卡片样式）。
   题面明确要求「避免把审美偏好混作数值错」，所以「量过但确认不构成矛盾」这件事
   本身就应该有记录位置，而不是默默不写。

4. *结论必须能被读者当场核对*。标注卡上没有只写「Q4 最好」，
   而是写「收入 180 万元 · 成本 126 万元 / 利润 54 万元 · 利润率 30.0% / 三项均为全年最高 /
   四季利润 30 / 27 / 32 / 54」——四个数字都能在左侧利润表里逐个对上。

**问题与修复（要点）**

- 第一次自检就抓到字号门槛问题（20px < 22px）。这类「数值正确但规格不合」的缺陷
  靠肉眼看整屏是看不出来的，得让脚本把题面的硬门槛逐条过一遍。
- 核验脚本自己出过一次 264px 的假误差，又出过一次「误差为 0 反而判 False」。
  这两处都是脚本的 bug 而不是图的 bug——教训是：**核验脚本在报红灯之前，
  先要确认它在自己的数据上是对的**（A15 也有同类的 `or 999` 写法，已一并修正）。

**可复用经验**

- 判断「柱高是否等于数值」不需要原始数据：柱子和轴在同一张图里就够，
  量柱顶 → 按刻度换算 → 和标签比，三步。
- 截断轴会同时制造两个问题：比例失真**和**最小值落到轴外。
  本题里成本最低的 90 在原图上根本落在坐标轴范围之外，读者无从读出。
- 批量重制图表时，把「数值 → 几何」做成纯函数，标签直接由数值 `str()` 出来，
  就能从结构上消灭「数字对了但图不对」这一整类缺陷。
- 审计 JSON 里的 `uncertainties` 和 `checked_but_not_errors` 不是可选装饰：
  它们是把「我检查过什么、什么没法定论」变成可核查记录的最小成本做法。

**结束依据**：
定稿 `corrected-report.png` 整屏打开；再对交付 PNG 反测 8 根柱的高度/x/柱底、
5 条网格线的 y、以及全部字号门槛（`verify.json` all_passed = true）；
另 3× 放大柱顶与坐标轴、2× 放大利润表/标注卡/页眉逐一看图，确认无截断、无错值。
`findings.json` 的每条 `final_visual_check` 都对应一张实际打开过的图。
未以「渲染成功」作为完成依据。


### 未解决事项 / 限制


- 无影响交付的未解决问题。
- **原图柱高所用的比例无法反推**：只能确定「同一系列内 柱高÷标签 不恒定」，
  无法断定作者想画的是哪一组数。记为 U03，不臆造一个「作者本意值」。
- **利润明细里的 42 来源不明**：source.csv 的六个数里没有任何组合能相减得到 42，
  因此无法判断是笔误还是来自未提供的中间表。记为 U02，按源数据改为 32。
- **截断轴是否出于有意取舍无法判断**：成品图不携带意图信息。
  定稿按「是否误导」而非「是否有意」判定，无条件改成共同零起点。记为 U01。
- **收入/成本口径（是否含税、是否为内部结算价）未在任何输入中声明**。
  重制严格照抄 source.csv 原值，不做口径推断。记为 U04。
- 本题未做逐像素与原图的比对，也不要求：原图本身是待诊断的错误图，
  交付目标是「基于唯一可信数据重制」，不是「像素级复刻错误图」。


### 留痕确认

- 临时目录中的草稿 DSL、各次请求体副本、成功图片、失败响应 JSON、放大裁切图与预览全部保留，未删除或覆盖任何一次尝试；日志为追加写入。
- `tasks/` 下的输入文件、任务说明与模板均未被修改。
- 未保存任何密钥；`SNAPSHOT_API_KEY` 若存在只从环境变量读取，不写入 DSL 或日志。
- 总任务根 `.gitignore` 已创建（参考 `templates/gitignore-template.txt`），仅排除 `__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`、`.ipynb_checkpoints/`、`node_modules/.cache/` 等明确的运行时缓存；**未**使用 `tmp/`、`outputs/`、`cache/`、`.cache/`、`*.log` 或图片/DSL/JSON 通配规则，因此本任务的过程证据不会被忽略（共享规则详见 `_suite/snapshot-usage.md`）。
- `__pycache__/` 等运行时缓存不作为留痕材料，也不列为产物或自检证据。
