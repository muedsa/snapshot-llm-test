# Snapshot 使用情况说明与踩坑记录

任务ID：A05
任务名称：不规则采样与缺测的仪表报告
本次运行ID：run-20261011-01
完成状态：完成
结束原因：需求满足并完成逐图视觉自检
输出目录：`outputs/run-20261011-01/A05/`（路径基准：suite_root）
临时目录：`tmp/run-20261011-01/A05/`（路径基准：suite_root）
路径基准：suite_root；除本报告的 Markdown 本地链接（相对本文件所在目录）外，
所有记录中的本地路径均为相对 suite_root 的相对路径，未写死机器盘符或用户目录。

遵循 [PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录环境变量。
Markdown 本地链接相对当前文档；本报告位于 `outputs/<run_id>/A05/`，
故指向题库文档的链接为 `../../../tasks/…`。

## 1. 最终产物与需求完成情况


| 文件 | 用途 | 对应 DSL 或图片 | 完成状态 |
|---|---|---|---|
| `sensor-report.snapshot` | 1440×1000 三联趋势定稿 DSL | `sensor-report.png` | 已完成 |
| `sensor-report.png` | 服务返回的最终图片 | `sensor-report.snapshot` | 已完成，服务原始响应 |
| `normalized-data.json` | 分钟偏移 / null 缺测 / 范围 / 有效数量 / 连接段 | — | 已完成 |
| `snapshot-usage.md` / `task-metrics.json` | 报告与指标 | — | 已完成 |

需求逐项核对（依据最终图**实际查看**）：

| 题目要求 | 满足情况 | 证据 |
|---|---|---|
| 1440×1000 | 满足 | 服务 `image_info` = 1440×1000 |
| 数据来自 inputs/readings.csv | 满足 | 12 行全部使用；输入未修改 |
| 温度 °C、湿度 %、压差 kPa；空单元格=缺测不是 0 | 满足 | 三图单位分别标注；表内缺测一律显示「—」；`normalized-data.json` 中为 `null` |
| 三图共用 08:00–12:30 真实时间比例横轴 | 满足 | 单一 `px(min) = 106 + (min−480) × 4.726`，三图同值，见 `axes.shared_x` |
| 对齐纵向参考线 | 满足 | 12 个采样时点在三图中各画一条 `#F1F5F9` 竖线，x 完全一致；图例中说明 |
| 缺测处前后线段断开，不用直线/虚线补值 | 满足 | 温度在 09:15、11:40 处断开为 3 段；湿度在 09:40 处断开为 2 段；`segments` 字段给出实际相连的采样 ID 对 |
| 压差可正可负，零线清晰 | 满足 | 第三图画 −1/0/1/2 刻度并加粗零线、右端标「零线 0」 |
| 每个真实读数有独立采样标记 | 满足 | 10/11/12 个空心圆环标记，数量与有效采样数一致 |
| 每图独立且清晰的纵轴单位 | 满足 | 温度 °C（19…24）、湿度 %（34…42）、压差 kPa（−1…2），各自标注刻度范围 |
| 标注 09:40–10:50 压差为负的实际采样区段 | 满足 | 第三图浅紫底区 + 「负压差采样区段 09:40–10:50（共 3 个采样点）」 |
| 不声称连续期间每一刻均为负 | 满足 | 标注明确写「共 3 个采样点」；表下脚注写「仅代表这三个采样时刻，不代表 09:40–10:50 全程为负」 |
| 上方列有效采样数与观察最小/最大 | 满足 | 三张统计条：10/12、11/12、12/12 与 19.2–23.1、34–41、−0.8–1.3 |
| 下方全部 12 时点简表 | 满足 | 两列 × 6 行共 12 行，含时间、相对分钟与三项读数 |
| 表格缺测用「—」 | 满足 | 09:15 温度、09:40 湿度、11:40 温度均为「—」 |
| 图中给出缺测与断线图例 | 满足 | 独立图例行：实际读数 / 缺测（×）两侧断开 / 连接线 / 负值区段 / 纵向参考线 |
| 正文≥20、轴/表≥18 | 满足 | 表格正文 20px，表头/轴刻度/时间标签 18px，图例与注记 16–18px |
| normalized-data.json 五类字段 | 满足 | `samples`/`statistics`/`segments`/`negative_samples`/`axes` 齐备 |



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

| https://snapshot.muedsa.com/reference/enums/ | `BorderStyle` 仅 `NONE`/`SOLID`；`CrossAxisAlignment` 取值集合 | 标注线段与图例的实现方式 |


本次实际用到的能力：布局：`Container`/`Column`/`Row`/`Expanded`/`SizedBox`/`Padding`；精确定位：`Stack(fit=EXPAND)` + `Positioned`；文本：`Text` 的 `fontFamily`/`fontSize`/`textAlign`/`height`/`maxLines`/`letterSpacing`；颜色与透明度：CSS 颜色与 `#RRGGBBAA` 独立 alpha；装饰：`border`（宽度+样式+颜色）、`borderRadius` 与四角圆角、`boxShadow`；裁剪：`ClipRRect`/`ClipOval`；变换：`Transform` 的列主序 4×4 矩阵 + `alignment`；滤镜：`ImageFiltered`（子树模糊）、`BackdropFilter`（仅背景模糊）；渐变：`gradientType=LINEAR/RADIAL/SWEEP` + `gradientColors`/`gradientStops`。解析器未提供 `ClipPath`/多边形，所有图形均由矩形、圆角矩形、椭圆与渐变拼装。
本题额外用到：折线段用 `Transform` 的列主序 4×4 旋转矩阵 + `alignment="CENTER"` 逐段拼接；`ClipOval` 构成采样标记的圆环；负值区段用半透明矩形覆盖；不规则采样点的 x 轴标签在间距不足时自动上下错行。

字体：实际查询 `GET /fonts` 得到 27 个字体族，原始响应留存于
`tmp/run-20261011-01/A05/responses/`（request_type=fonts），另有整理副本 `outputs/run-20261011-01/A05/../_suite/fonts-list.txt`。
中文正文使用 `Noto Sans CJK SC`，数字/拉丁使用 `Inter` 系列，代码/等宽使用 `Noto Sans Mono CJK SC`。
题目素材政策为纯 DSL，未使用任何外部图片（`<Image>` 标签本次未使用）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/run-20261011-01/A05/requests.jsonl`
迭代记录文件：`tmp/run-20261011-01/A05/iterations.jsonl`
响应与草稿留痕：`tmp/run-20261011-01/A05/responses/`、`tmp/run-20261011-01/A05/drafts/`

渲染请求总数：7
成功次数：7
失败次数：0
重试请求数：0（是总请求的子集）
DSL版本数：6
实际图片查看次数：2
完整视觉迭代数：4
未完成视觉迭代数：0
其他接口查询：字体查询与文档读取为 run 级共享准备；本题无额外接口查询

初次生成和查看计为基线，不计为改进迭代。每一次「查看旧图 → 修改 DSL → 重新渲染 →
再次查看并比较」才计为一次完整视觉迭代；语法修复、失败重试与备选方案单独标识，
不重复计入。所有图片均已用图像工具实际打开查看（含整屏与放大局部）。

| 请求ID | 输入 DSL | 耗时 | HTTP / Content-Type | 响应文件 | 查看与实际结果 |
|---|---|---|---|---|---|
| A05-v1-ce293d6c | drafts/a05-v1.snapshot | 3.99s | 200 image/png | preview/a05-v1.png | 已打开整屏：结构正确，但数值标签顶到标题行、温度/湿度纵轴被 0 基线压扁、10:50 与 11:00 时间标签重叠、底部缺测脚注被画布裁掉 |
| A05-v2-3f25663a | drafts/a05-v2.snapshot | 3.04s | 200 image/png | preview/a05-v2.png | 已打开：错行后的时间标签与图例行相撞；右侧数值标签因 clamp 参数错误被挤到同一位置重叠 |
| A05-v3-ccb6debc | drafts/a05-v3.snapshot | 4.08s | 200 image/png | preview/a05-v3.png | 已打开：坐标范围收紧后曲线形态可读；仍有「横轴…」注记压住单位说明、表格最后一行压住脚注 |
| A05-v4-1113c4e6 | drafts/a05-v4.snapshot | 4.50s | 200 image/png | preview/a05-v4.png | 已打开：仅剩表格行高参数未生效（仍为 34px）导致末行压住脚注 |
| A05-v5-0b92be1a | drafts/a05-v5.snapshot | 5.29s | 200 image/png | preview/a05-v5.png | 已打开整屏复查：三图、图例、12 行明细表与脚注全部无重叠、无裁切 |
| A05-final-* | outputs/…/sensor-report.snapshot | 见 metrics | 200 image/png | outputs/…/sensor-report.png | 已打开复查，与 v5 一致 |

## 4. 修改记录与踩坑

| 版本 / 类型 | 观察到的实际问题 | 原因及确认依据 | 实际修改 | 复验结果 |
|---|---|---|---|---|
| v1 · baseline | 数值标签压到标题行；温度/湿度纵轴从 0 起导致 19.2–23.1 的变化被压扁；10:50 与 11:00 标签重叠；底部脚注被画布底边裁掉 | 数值标签固定放在标记上方 30px，未做边界判断；`nice_ticks(min(lo_v, 0.0), ...)` 把 0 强制纳入范围 | 数值标签改为先判顶部空间、不足则落到标记下方，并按字宽夹紧到绘图区内；温度与湿度改为按数据范围取整齐刻度（压差保留 0 以显出零线）；x 标签去掉前导零并在间距不足时错行 | v2/v3 逐步消除重叠 |
| v3 · visual | 「横轴为真实时间比例…」注记与纵轴单位说明重叠 | 注记放在卡片标题行右端，与单位说明同一位置 | 删除该注记（页面页眉已说明横轴口径，且纵向参考线本身即证据） | v4 消除 |
| v4 · visual | 表格最后一行压住下方脚注 | `row_h`/`head_h` 的替换未命中实际代码行，仍为 34px | 直接修改 `sk.table(...)` 调用处为 `row_h=30, head_h=30` | v5 消除 |
| v5 · visual | 复查 | — | 整屏与局部核对 | 无重叠、无裁切、缺测与断线表现正确 |

「渲染成功但视觉不符合要求」的问题同样记录在上面的完整视觉迭代中。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/run-20261011-01/A05/task-metrics.json`


| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始 / 结束时间 | 2026-10-11T12:20:00.000+08:00 / 2026-10-11T14:37:51.692+08:00 | ISO8601 带时区 | 计时记录（本地时钟，带时区） |
| 任务总耗时 | 8271.692 | 秒 | 墙钟时间（读题 → 计算 → 构造 → 渲染 → 看图 → 修复 → 报告） |
| 首次可用图耗时 | 3.992 | 秒 | 从开始到首个 `200 image/png` 且能打开的图为止的全部请求耗时之和；本任务请求串行，故与实际顺序一致 |
| 等待用户反馈 | 0.0 | 秒 | 本题为单轮任务，无多轮反馈等待 |
| 限流等待 | 0.0 | 秒 | 全程未出现 `429`（见 `requests.jsonl`） |
| 排队等待 | None | 秒 | 服务未提供排队指标，不可测量，记 null 而非 0 |
| 已记录请求耗时之和 | 30.907 | 秒 | `requests.jsonl` 中 `duration_seconds` 求和；请求串行，不与墙钟重复计入 |
| 成功 / 失败 / 重试请求 | 7 / 0 / 0 | 次 | `requests.jsonl`；失败均为不同 DSL 的语法修复，非同一请求重试 |
| 看图 / 完整视觉迭代 | 2 / 4 | 次 | `iterations.jsonl` 与实际图像查看记录 |
| DSL 版本数 | 6 | 个 | `requests.jsonl` 去重 |
| Server-Timing | null | — | 服务响应未返回该头，日志中如实记为 null |


## 6. 设计选择、经验与未解决事项


**关键设计选择**

1. *缺测一律画成「断线 + ×」而不是补值*。这是本题的核心要求：温度在 09:15、11:40 断开为 3 段，
   湿度在 09:40 断开为 2 段。`segments` 字段给出实际相连的采样 ID 对，可逐对复核；
   图中在缺测位置画红色 × 与「缺测」二字，并在图例中写明「两侧线段断开，不补值」。

2. *横轴用真实分钟比例，三图同一映射*。12 个采样点的时间间隔并不均匀（10、25、25、15、25、30、40、10、40、30、20 分钟），
   因此横轴按 `x = 106 + (minute − 480) × 4.726` 映射，**不按等距序号排布**。
   三张图各画 12 条纵向参考线，读者可以直接看到对齐关系。

3. *纵轴各图独立并标注真实范围*。温度取 19…24、湿度取 34…42（避免 0 基线把 19.2–23.1 的变化压平），
   压差取 −1…2 且**必须包含 0**（题目要求零线清晰）。每个范围都写在卡片右上角，
   并写入 `normalized-data.json.axes.y_axes`，避免读者误读。

4. *负压差只标注「采样区段」而非「连续区间」*。09:40、10:10、10:50 三个采样点为负，
   这三点之间没有更多采样，因此图中写「共 3 个采样点」，表下脚注再强调一次
   「不代表 09:40–10:50 全程为负」。

5. *不规则标签的自动错行*。10:50 与 11:00 只差 10 分钟（≈47px），标签宽约 60px，
   因此时间标签与数值标签都实现了「间距不足则上下错开」的规则，而不是靠固定坐标硬排。

**可复用经验**

- `nice_ticks` 强制含 0 时会严重压扁传感器曲线；折线图应按数据范围取刻度，
  并把范围明确标出；含正负的指标则必须保留 0 以画出零线。
- 数值标签必须同时做**纵向**（顶部空间）与**横向**（相邻标签间距）两种边界判断。
- 表格行高这类参数要确认替换真正命中代码行——本次 v4 就是替换未生效导致缺陷残留。

**结束依据**：最终图实际打开查看，三图的线段断开、零线、负值区段、12 个采样标记、
12 行明细表与脚注均逐项核对；数值与 `normalized-data.json` 逐项一致；未以渲染成功作为完成依据。


### 未解决事项 / 限制


- 未发现影响交付的未解决问题。
- 温度与湿度纵轴采用非零起点（19…24 / 34…42）以呈现真实波动；这是折线图的常规做法，
  范围已在图上与 JSON 中显式标注。压差因含正负而保留 0 基线。
- 图表读数为 CSV 原始数据，未做任何平滑、插值或补值；观察最小/最大为**采样极值**，
  不是连续区间的极值，该限定已写入 JSON。


### 留痕确认

- 临时目录中的草稿 DSL、各次请求体副本、成功图片、失败响应 JSON、放大裁切图与预览全部保留，未删除或覆盖任何一次尝试；日志为追加写入。
- `tasks/` 下的输入文件、任务说明与模板均未被修改。
- 未保存任何密钥；`SNAPSHOT_API_KEY` 若存在只从环境变量读取，不写入 DSL 或日志。
- 总任务根 `.gitignore` 已创建（参考 `templates/gitignore-template.txt`），仅排除 `__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`、`.ipynb_checkpoints/`、`node_modules/.cache/` 等明确的运行时缓存；**未**使用 `tmp/`、`outputs/`、`cache/`、`.cache/`、`*.log` 或图片/DSL/JSON 通配规则，因此本任务的过程证据不会被忽略（共享规则详见 `_suite/snapshot-usage.md`）。
- `__pycache__/` 等运行时缓存不作为留痕材料，也不列为产物或自检证据。
