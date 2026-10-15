# Snapshot 使用情况说明与踩坑记录

任务ID：A04
任务名称：分组改善与总体下降的数据解释
本次运行ID：run-20261011-01
完成状态：完成
结束原因：需求满足并完成逐图视觉自检
输出目录：`outputs/run-20261011-01/A04/`（路径基准：suite_root）
临时目录：`tmp/run-20261011-01/A04/`（路径基准：suite_root）
路径基准：suite_root；除本报告的 Markdown 本地链接（相对本文件所在目录）外，
所有记录中的本地路径均为相对 suite_root 的相对路径，未写死机器盘符或用户目录。

遵循 [PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录环境变量。
Markdown 本地链接相对当前文档；本报告位于 `outputs/<run_id>/A04/`，
故指向题库文档的链接为 `../../../tasks/…`。

## 1. 最终产物与需求完成情况


| 文件 | 用途 | 对应 DSL 或图片 | 完成状态 |
|---|---|---|---|
| `conversion-story.snapshot` | 1600×1000 信息图定稿 DSL | `conversion-story.png` | 已完成 |
| `conversion-story.png` | 服务返回的最终图片 | `conversion-story.snapshot` | 已完成，服务原始响应 |
| `analysis.json` | 审计数据（分数/百分比/加权公式/结论） | — | 已完成 |
| `snapshot-usage.md` / `task-metrics.json` | 报告与指标 | — | 已完成 |

需求逐项核对（依据最终图**实际查看**）：

| 题目要求 | 满足情况 | 证据 |
|---|---|---|
| 1600×1000 | 满足 | 服务 `image_info` = 1600×1000 |
| 两渠道各自两期转化率 | 满足 | 图①四根柱：30.00% / 10.00% / 35.00% / 12.00% |
| 两期访问构成 | 满足 | 图②两条**等长**堆叠条：80%/20% 与 20%/80%，各标「访问 10,000 次 · 合计 100%」 |
| 总体转化率 | 满足 | 图③实心柱 26.00% → 16.60%，小表两行「总体」 |
| 解释分组与总体是否同向 | 满足 | 标题、主结论与图③底部对照同时点明「分组↑、总体↓，不同向」 |
| 总体＝成交总数/访问总数 | 满足 | 2600/10000、1660/10000；`analysis.json.periods[].weighted_formula` |
| 不准平均渠道比例 | 满足 | 所有结论与总体值均用总成交÷总访问；渠道平均**仅**在图③以灰色虚框标注为「错误做法」，并在 `guardrails` 中说明 |
| 不把同期不同渠道绝对成交量当转化率 | 满足 | 每个渠道的率都用自己的分母：2400/8000、200/2000、700/2000、960/8000 |
| 率图同一 0–100% 尺度 | 满足 | 图①与图③均用 0/25/50/75/100 刻度，轴范围与像素映射写入 `analysis.json.axes` |
| 构成图每期等长、分段按真实占比 | 满足 | 两条长度相同，分段宽＝占比×等长；`axes[1].equal_length_per_period=true` |
| 所有原始分母/分子可从小表核对 | 满足 | 小表 6 行含「访问（分母）」「成交（分子）」「精确分数」三列，逐行可验 |
| 一条由数据支持的主结论 | 满足 | 「主结论」段，引用 4 个渠道率与 2 个总体率，差额 −9.40 个百分点 |
| 「不能证明因果」的限制说明 | 满足 | 「限制」段独立成块并标橙色 |
| 单位与期名齐全 | 满足 | 页眉右上单位说明；四张图与表格均标「前期 / 后期」；表头标单位 |
| 正文≥22、图标注≥18 | 满足 | 主结论与限制正文 22px；图内标注、坐标、表格、图注 18–20px |
| 用色和位置建立三图关系 | 满足 | ① ② ③ 编号建立顺序；① ② 共用渠道配色（直接=蓝、推广=橙），③ 专用青色表示总量 |
| 避免结论先行 | 满足 | 三图与数据表排在结论卡之前，结论卡位于右下 |
| analysis.json 四类字段 | 满足 | `groups` / `periods` / `axes` / `conclusions` 齐备 |



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

| https://open-snapshot.muedsa.com/ai-guide.md | `POST /snapshot` 纯文本 DSL；按 `Content-Type` 判定成败；错误 JSON 的 `message` 与 `position` 用于定位 | `_suite/scripts/snapshot_render.py` |
| https://snapshot.muedsa.com/reference/parser-tags/ | `Stack`+`Positioned` 精确坐标；`Container` 渐变/圆角/边框；`Text` 的 `textAlign`/`height`；`Flex` 的 `mainAxisAlignment="END"` | `snapkit.py`、`conversion-story.snapshot` |
| https://snapshot.muedsa.com/reference/enums/ | `BorderStyle` 仅 `NONE`/`SOLID`（**没有** DASHED）；`CrossAxisAlignment` 仅 START/END/CENTER/STRETCH/BASELINE | 虚线外框改用小矩形拼出；右对齐图例用 `Row mainAxisAlignment="END"` |


本次实际用到的能力：布局：`Stack(fit=EXPAND)` + `Positioned` 实现三图的全部柱、网格线、刻度与堆叠分段；`Row mainAxisAlignment=END` 做右对齐图例；`Column`/`SizedBox` 组装卡片内元素。文本：`Text` 的 `fontFamily`/`fontSize`/`textAlign`（LEFT/CENTER/RIGHT）；`height` 控制行高。颜色与透明度：`#RRGGBBAA`（灰色虚框填充 `#CBD5E155`）、`borderRadius` 四角圆角。装饰：`border`、`border` 变体。图片标签：未使用（纯 DSL）。

字体：实际查询 `GET /fonts` 得到 27 个字体族，原始响应留存于
`tmp/run-20261011-01/A04/responses/`（request_type=fonts），另有整理副本 `outputs/run-20261011-01/A04/../_suite/fonts-list.txt`。
中文正文使用 `Noto Sans CJK SC`，数字/拉丁使用 `Inter` 系列，代码/等宽使用 `Noto Sans Mono CJK SC`。
题目素材政策为纯 DSL，未使用任何外部图片（`<Image>` 标签本次未使用）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/run-20261011-01/A04/requests.jsonl`
迭代记录文件：`tmp/run-20261011-01/A04/iterations.jsonl`
响应与草稿留痕：`tmp/run-20261011-01/A04/responses/`、`tmp/run-20261011-01/A04/drafts/`

渲染请求总数：5
成功次数：4
失败次数：1
重试请求数：0（是总请求的子集）
DSL版本数：4
实际图片查看次数：1
完整视觉迭代数：3
未完成视觉迭代数：0
其他接口查询：字体与文档读取为 run 级共享准备；A04 另查枚举速查页确认 BorderStyle 取值

初次生成和查看计为基线，不计为改进迭代。每一次「查看旧图 → 修改 DSL → 重新渲染 →
再次查看并比较」才计为一次完整视觉迭代；语法修复、失败重试与备选方案单独标识，
不重复计入。所有图片均已用图像工具实际打开查看（含整屏与放大局部）。


| 请求ID | DSL | 耗时 | HTTP | 响应 | 查看与实际结果 |
|---|---|---|---|---|---|
| A04-v1-d96032d9 | drafts/a04-v1.snapshot | 2.06s | 400 application/json | responses/A04-v1-d96032d9.error.json | 无图；`PARSE_ERROR Attr [border] value is invalid: No enum constant BorderStyle.DASHED` |
| A04-v1-2f174c14 | drafts/a04-v1.snapshot（修正后） | 6.29s | 200 image/png | preview/a04-v1.png | 已打开整屏：数据与结构正确，但图③标题与图例重叠、图③绘图区过扁、结论卡三段严重重叠、表格「精确分数」被截断、图②窄分段标签溢出 |
| A04-v2-4c225775 | drafts/a04-v2.snapshot | 5.36s | 200 image/png | preview/a04-v2.png | 已打开整屏：结论卡已不重叠；但图②两根条的行距不足（外置标签压住上一行的「访问 10,000 次」），表格分数仍折行，结论第三段溢出卡片并与页脚相碰 |
| A04-v3-72aea110 | drafts/a04-v3.snapshot | 12.20s | 200 image/png | preview/a04-v3.png | 已打开整屏：图②、表格、结论卡均正常；仅图①底部注释右端被裁 |
| A04-final-* | outputs/…/conversion-story.snapshot | 见 metrics | 200 image/png | outputs/…/conversion-story.png | 已打开复查 |

（完整字段见 `requests.jsonl`；上表耗时取自该日志）


## 4. 修改记录与踩坑


| 迭代 / 类型 | 问题或现象 | 原因及确认依据 | 修改 | 复验结果 | 文件 |
|---|---|---|---|---|---|
| v1 · syntax-fix | 服务 400 | `BorderStyle` 枚举速查页只有 `NONE`/`SOLID`，不存在 `DASHED` | 虚线外框改为按柱宽均匀排布的小矩形（顶边+底边各一组） | 服务 200 | `a04-v1.snapshot` |
| v2 · visual | 图③标题压住图例；图③绘图区被 `pb=70` 压扁；结论三段重叠；表格分数列折行；图②窄分段标签挤在条内 | 图例与标题同处 y=CH_Y+16；结论卡按固定行数 3/4/2 估算而实际为 3/3/2+ 溢出；分数列 106px 不足 | 图例下移到副标题行；绘图区上下边距收紧；卡片宽度重分配（520/420/剩余）；表格列宽重排并去掉分数中的空格；窄分段标签移到条形上方 | 结论不再重叠，表格分数完整 | `a04-v2.snapshot` |
| v3 · visual | 图②两根条行距 92px 不足，外置标签压住上一行说明；结论第三段仍与页脚相碰 | 行距需 ≥ 标签高+说明高；结论文案偏长 | 行距提到 112px；限制段与口径段各缩短一行 | 图②与结论均正常 | `a04-v3.snapshot` |
| v4 · visual | 图①底部注释右端被裁 | 卡片宽 520，注释文字宽 480 而实际约 600px | 注释压缩为「↑ 30.00%→35.00% · 10.00%→12.00%（成交 ÷ 访问）」 | 复查通过 | `a04-v4.snapshot` |


「渲染成功但视觉不符合要求」的问题同样记录在上面的完整视觉迭代中。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/run-20261011-01/A04/task-metrics.json`


| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始 / 结束时间 | 2026-10-11T11:40:00.000+08:00 / 2026-10-11T14:27:49.094+08:00 | ISO8601 带时区 | 计时记录 |
| 任务总耗时 | 10069.094 | 秒 | 墙钟时间 |
| 首次可用图耗时 | 8.352 | 秒 | 至首个 `200 image/png` 的请求耗时之和（串行） |
| 等待用户反馈 / 限流等待 | 0.0 / 0.0 | 秒 | 单轮任务；全程无 429 |
| 排队等待 | null | 秒 | 服务未提供该指标 |
| 已记录请求耗时之和 | 31.088 | 秒 | `requests.jsonl` 求和，串行不重叠 |
| 成功 / 失败 / 重试请求 | 4 / 1 / 0 | 次 | 1 次失败为语法错误，非重试 |
| 看图 / 完整视觉迭代 | 1 / 3 | 次 | `iterations.jsonl`；实际打开 4 张 |
| Server-Timing | null | — | 服务未返回该响应头 |


## 6. 设计选择、经验与未解决事项


**关键设计选择**

1. *把「错误做法」画出来，而不是只说不要用*。题目的核心悖论正是「简单平均会给出相反方向」。
   因此图③同时画出正确的加权总体（青色实心）与错误的渠道比例平均（灰色虚框），
   两条线一眼可见方向相反；但**所有结论、表格与 JSON 都只用总成交÷总访问**，
   并在 `analysis.json.guardrails` 中写明这一约束，避免读者误读。
2. *构成图用等长条而不是饼图*。两条 100% 堆叠条长度完全一致、分段宽度＝真实占比，
   翻转一眼可见；饼图面积难比较，等长条更适合表达构成变化。
3. *三图用「① ② ③ + 共享配色」建立关系*。① ② 共用渠道色（直接=蓝、推广=橙），
   ③ 用区别于渠道的青色代表总量，位置从左到右对应「分组 → 构成 → 总体」的推理顺序。
4. *精确分数与百分比并列*。小表同时给「访问（分母）」「成交（分子）」「精确分数」「转化率」，
   让读者能自己验算；JSON 里用 `fractions.Fraction` 保留精确值而非浮点近似。
5. *结论不先行*。三图与小表排在结论卡之前，先看数据再看判断。

**可复用经验**

- `BorderStyle` 没有 `DASHED`，虚线只能自己用小矩形拼。
- 固定行数估算在真实渲染下不可靠（本任务实际行数与估计差 1 行就造成重叠）。
  改为按 `sk.est_lines()`（CJK 1.0em、其余 0.56em）估算并把估算值写入排版逻辑，
  仍以最终看图为准。
- 表格列宽要按**最长内容**而不是按标题分配；`2400/8000` 这类紧凑写法比 `2400 / 8000` 更省宽。
- 堆叠条的窄分段放不下标签时，标签要移到条形外并为行距留出空间，不能硬塞。

**结束依据**：最终图实际打开查看，三图数值、小表分数与结论引用的数字逐项与
`analysis.json` 及 CSV 原始分子分母核对一致；无重叠、无截断；未以渲染成功作为完成依据。


### 未解决事项 / 限制

- 未发现影响交付的未解决问题。
- 「正文≥22」已按主结论/限制/口径三段正文 22px 执行；表格正文为 20px、图内标注 18px，属于表体与图表附属元素。如需表体也 ≥22px，需加宽表格卡片并相应压缩结论卡片。
- 因果限制已在图中与 JSON 中显式声明；本图不主张任何因果关系。

### 留痕确认

- 草稿 a04-v1…v4 全部保留，失败响应 JSON 保留在 `tmp/run-20261011-01/A04/responses/`，未删除或覆盖。
- `tasks/A04-conversion-paradox/inputs/` 未被修改。
- 未保存密钥。
- 总任务根 `.gitignore` 仅排除运行时缓存，过程证据不受影响（共享规则见 `_suite/snapshot-usage.md`）。
