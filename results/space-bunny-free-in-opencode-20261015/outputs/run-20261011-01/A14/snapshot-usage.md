# Snapshot 使用情况说明与踩坑记录

任务ID：A14
任务名称：八组文案压力测试与批量生成
本次运行ID：run-20261011-01
完成状态：完成
结束原因：需求满足并完成逐图视觉自检
输出目录：`outputs/run-20261011-01/A14/`（路径基准：suite_root）
临时目录：`tmp/run-20261011-01/A14/`（路径基准：suite_root）
路径基准：suite_root；除本报告的 Markdown 本地链接（相对本文件所在目录）外，
所有记录中的本地路径均为相对 suite_root 的相对路径，未写死机器盘符或用户目录。

遵循 [PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录环境变量。
Markdown 本地链接相对当前文档；本报告位于 `outputs/<run_id>/A14/`，
故指向题库文档的链接为 `../../../tasks/…`。

## 1. 最终产物与需求完成情况


| 文件 | 用途 | 对应 DSL 或图 | 完成状态 |
|---|---|---|---|
| `card-K01.snapshot` … `card-K08.snapshot` | 8 张宣传卡的定稿 DSL | `card-K0*.png` | 已完成，8/8 |
| `card-K01.png` … `card-K08.png` | 服务返回的最终图，均 1200×630 | 同名 `.snapshot` | 已完成，服务原始响应 |
| `batch-audit.json` | 逐卡内容、标题字号/行数/位置、状态编码、安全边距、生成规则与逐张查看 | — | 已完成 |
| `snapshot-usage.md` / `task-metrics.json` | 报告与指标 | — | 已完成 |
| `tmp/…/A14/build_a14.py` | 参数化生成脚本（保留在临时目录） | — | 已完成 |

需求逐项核对（依据**8 张最终服务原图逐张实际打开**，另加 5 轮中间版本与 2 张接触表，共 22 次看图）

| 题目要求 | 满足情况 | 证据 |
|---|---|---|
| 8 张 1200×630 宣传卡，文件名 card-K01…K08 | 满足 | 8 次服务 `image_info` 均为 PNG 1200×630 RGBA |
| 内容来自 `inputs/cards.json` | 满足 | `batch-audit.json.generation.input.modified = false`；`source_fields` 逐卡抄录原始四字段 |
| 统一主色 | 满足 | 8 张共用 `#1D4ED8`（顶条、标记、分隔线、徽标描边基调）与 `#0E1830` 底色；差异只来自状态色 |
| 统一标题区域 | 满足 | 标题栏 x=40 w=700，在标题带 [150,470] 内垂直居中；眉题固定 y=146 |
| 统一日期「2026.11.07」 | 满足 | 8 张页眉右上均显示，位置逐张相同 |
| 统一品牌「Structure / Vision」 | 满足 | 8 张页眉左侧 S/V 标记 + Structure + / Vision 字标，位置逐张相同 |
| 统一状态体系 | 满足 | 4 个状态共用同一徽标盒（936,142,224×60）与同一符号位（中心 970,172）；差异只在颜色/符号/文字 |
| 保留标题原始文字 | 满足 | `rendered_text.title_lines` 拼接后与源 `title` 逐字符相同（见 `verification.text_fidelity`） |
| 保留讲者原始文字 | 满足 | 同上，讲者 8/8 逐字符一致 |
| 保留时间原始文字 | 满足 | 同上，时间 8/8 逐字符一致 |
| 保留状态原始文字 | 满足 | 徽标文字即源 `status`（开放/满额/候补/取消），8/8 一致 |
| 标题字号 ≥36 | 满足 | 实际取到 48/56/64px 三档，最小 48px；`verification.title_font_size_px` |
| 标题最多 3 行 | 满足 | 行数 1/1/2/2/2/2/2/3，最大 3 行 |
| 讲者 ≥22 | 满足 | 统一 26px |
| 状态用颜色+文字/符号共同区分 | 满足 | 三通道：颜色（#22C55E/#F59E0B/#A78BFA/#F87171）+ DSL 几何符号（实心圆/圆角方块/圆环/叉号）+ 原始状态文字；`verification.status_color_on_canvas` 逐卡确认颜色真的上了图 |
| 取消卡显示完整标题 | 满足 | K06 完整显示「两张看似相同的图片，为什么不能证明语义相同？」 |
| 取消卡显示时间 | 满足 | K06 显示 13:40 |
| 取消卡另注明「本场取消」 | 满足 | K06 徽标下方单独一行 26px 红字「本场取消」 |
| 取消卡不能删除或只出灰底 | 满足 | K06 保持统一底色 `#0E1830` 与主色顶条，仅追加红色徽标/注记/右侧斜纹带 |
| 长讲者允许两行 | 满足 | 讲者断行上限 2 行已实现；8 条讲者最长为 K07「Northstar Research · 林川」，实测 1 行即容下（`two_line_branch_used = false`，如实记录未触发） |
| 各卡安全边距 40 | 满足 | `verification.within_safe_margin` 8/8 为 true；实测内容墨迹包围盒左/上 ≥40、右 ≤1160、下 ≤590 |
| 标题不与状态徽标碰撞 | 满足 | 标题栏右缘固定 740，徽标左缘固定 936，横向净距 196px；`verification.no_collision` 8/8 为 true |
| 不通过全局缩小整图适配长标题 | 满足 | 8 张的画布、字号以外的版面参数完全一致；只有标题字号（48/56/64）与行数（1/2/3）随长度变化 |
| 一套参数化规则从数据生成 | 满足 | 唯一入口 `card(c, k)`；`generation.shared_rules` 记录全部规则与分支条件 |
| 允许长度触发不同网格/换行 | 满足 | 7 张命中 T1 分支（K01/K02 1 行，K03–K07 2 行），K08 命中 T2 分支（3 行）；字号 48/56/64 三档、行数 1/2/3 三档、右侧层格条 1/2/3 条随行数联动；逐卡命中哪条分支记在 `cards[].title_typography.branch` |
| 不逐条硬改输入 | 满足 | `inputs/cards.json` 未被修改；8 张 DSL 由同一函数生成，脚本中没有任何 `if cid == …` 的分支 |
| 保留生成脚本在临时目录 | 满足 | `tmp/run-20261011-01/A14/build_a14.py` |
| 运行后每张真实查看 | 满足 | 8 张定稿各整屏打开一次并逐张记录观察与结论，见 `reviews` |
| 可另做接触表检查一致性 | 满足 | 2 张接触表（v1/v5）出图并打开；接触表仅作辅助，不替代 8 张原图 |
| `batch-audit.json` 逐卡记录内容 | 满足 | `cards[].source_fields` + `rendered_text` |
| 逐卡记录标题字号/行数/位置 | 满足 | `cards[].title_typography`（字号、行高、行数、栏位、文本框坐标、估算行宽）+ `verification.title_line_ink` 实测值 |
| 逐卡记录状态编码 | 满足 | `cards[].status_encoding`（颜色/底色/描边/符号/符号几何/文字/字号/坐标/额外注记/编码通道数） |
| 逐卡记录安全边距 | 满足 | `cards[].geometry.safe_margin_px` + `verification.within_safe_margin` 与实测包围盒 |
| 逐卡记录图片查看 | 满足 | `reviews` 逐张给出查看时间、观察、改动与最终结论 |
| 没查看到就不能声称八张通过 | 满足 | `reviews` 中 8 张定稿各有独立条目；`verification.all_passed = true` 只在 8 张都量过之后才写 |
| 接触表不替代八张原图 | 满足 | 接触表只存在临时目录，未进交付目录；`reviews` 明确标注它是辅助证据 |
| 所有最终 PNG 是服务真实响应且有同名 `.snapshot` | 满足 | 8 对文件齐全，DSL 均为服务实际接收的同一份 |



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

| https://snapshot.muedsa.com/reference/parser-tags/ · Text | 文本按给定框排版，超出部分的行为未在文档中说明 | 实测为**按框宽静默裁切**（HTTP 仍 200）；由此产生字宽标定探针与 T3 兜底降档规则 |
| https://snapshot.muedsa.com/reference/parser-tags/ · Positioned | 子节点的 `left`/`top` 是相对父容器而非画布 | 品牌标记内的 S/V 字标一度按画布坐标给值，文本框落到方块外被裁、字标整段消失 |


本次实际用到的能力：布局：`Container`/`Column`/`Row`/`Expanded`/`SizedBox`/`Padding`；精确定位：`Stack(fit=EXPAND)` + `Positioned`；文本：`Text` 的 `fontFamily`/`fontSize`/`textAlign`/`height`/`maxLines`/`letterSpacing`；颜色与透明度：CSS 颜色与 `#RRGGBBAA` 独立 alpha；装饰：`border`（宽度+样式+颜色）、`borderRadius` 与四角圆角、`boxShadow`；裁剪：`ClipRRect`/`ClipOval`；变换：`Transform` 的列主序 4×4 矩阵 + `alignment`；滤镜：`ImageFiltered`（子树模糊）、`BackdropFilter`（仅背景模糊）；渐变：`gradientType=LINEAR/RADIAL/SWEEP` + `gradientColors`/`gradientStops`。解析器未提供 `ClipPath`/多边形，所有图形均由矩形、圆角矩形、椭圆与渐变拼装。
本题额外用到：**服务端会按 Text 框宽度静默裁掉溢出文字**——这是本题最贵的一个发现。K05 首版按估算字宽判定「Color, Alpha & Contrast 」(663.7px) 放得下 700px 的框，但真实字面宽超过 700px，右端被裁，**画面上「Contrast 」整段消失**，而 HTTP 状态仍是 200、image_info 也正常。据此补了 12 行样张的字宽标定探针（probe-width.png），实测出 Inter Semi Bold 的 `<` `&` 约 0.66em、拉丁小写约 0.60em、大写 0.70em、数字 0.53em，Noto Sans CJK SC 全角 0.98–1.0em，并把 `char_em()` 换成标定值；此后 8 张卡的标题实测宽/估算宽比值落在 0.93–1.02。同时在 `pick_size()` 里加了 T3 兜底分支：任何一档下若仍有行的字面宽超过字面框，就继续降档，宁可少排也不丢字。
**中文避头尾**：`wrap()` 在贪心断行后补一轮修正，行首若出现 ：，。、；？！·—… 等收尾标点，就把上一行末字一并降行。
**拉丁词不可断**：断行原子按「全角逐字 / 空格自成 / 拉丁词整体」切分，避免把 `Contrast` 从中间劈开。
**8 位十六进制带 alpha 的描边色**（如 `#F871718F`）让徽标底色与边框能随状态色走而不用另设一整套中性色。

字体：实际查询 `GET /fonts` 得到 27 个字体族，原始响应留存于
`tmp/run-20261011-01/A14/responses/`（request_type=fonts），另有整理副本 `outputs/run-20261011-01/A14/../_suite/fonts-list.txt`。
中文正文使用 `Noto Sans CJK SC`，数字/拉丁使用 `Inter` 系列，代码/等宽使用 `Noto Sans Mono CJK SC`。
题目素材政策为纯 DSL，未使用任何外部图片（`<Image>` 标签本次未使用）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/run-20261011-01/A14/requests.jsonl`
迭代记录文件：`tmp/run-20261011-01/A14/iterations.jsonl`
响应与草稿留痕：`tmp/run-20261011-01/A14/responses/`、`tmp/run-20261011-01/A14/drafts/`

渲染请求总数：67
成功次数：66
失败次数：1
重试请求数：0（是总请求的子集）
DSL版本数：49
实际图片查看次数：24
完整视觉迭代数：13
未完成视觉迭代数：0
其他接口查询：字体查询与文档读取为 run 级共享准备；本题额外做了 **1 次字宽标定探针渲染**（12 行样张，1 张 1600×1840 图）与 **7 次接触表/迭代渲染**。

初次生成和查看计为基线，不计为改进迭代。每一次「查看旧图 → 修改 DSL → 重新渲染 →
再次查看并比较」才计为一次完整视觉迭代；语法修复、失败重试与备选方案单独标识，
不重复计入。所有图片均已用图像工具实际打开查看（含整屏与放大局部）。

| 请求ID | 输入 DSL | 耗时 | HTTP / Content-Type | 响应文件 | 查看与实际结果 |
|---|---|---|---|---|---|
| A14-v1-K01…K08 | drafts/a14-K0*-v1.snapshot | 1.1–2.8s | 200 image/png | preview/card-K0*-v1.png | 首版 8 张出图；逐张打开后发现 4 类缺陷（字标被裁、标题死区、孤字、K05 丢词、斜纹压日期） |
| A14-v1-sheet-73047017 | drafts/a14-contact-sheet-v1.snapshot | 2.42s | 400 PARSE_ERROR | responses/A14-v1-sheet-73047017.error.json | 无图；缩放正则漏掉等号，生成非法属性名 left"0.0" |
| A14-v1-sheetb-66e81032 | drafts/a14-contact-sheet-v1.snapshot | 3.33s | 200 image/png | preview/contact-sheet-v1.png | 改正后出接触表并打开，确认 8 张的体系一致 |
| probe-width-0d1640d0 | drafts/probe-width.snapshot | 5.27s | 200 image/png | preview/probe-width.png | 12 行 100px 样张；用 PIL 逐列量墨迹宽度，标定各类字符的 em 系数 |
| A14-v2-K01/K06/K08 | drafts/a14-K0*-v1.snapshot | 1.1–2.4s | 200 image/png | preview/card-K0*-v2.png | 标题改为带内居中、斜纹移位、讲者下边距收紧后复查 |
| A14-v3-K01/K06 | drafts/a14-K0*-v1.snapshot | 1.0–2.2s | 200 image/png | preview/card-K01-v3.png / card-K06-v3.png | S/V 字标按标记内相对坐标重排后完整显示 |
| A14-v3-K01…K08 | drafts/a14-K0*-v1.snapshot | 1.0–1.9s | 200 image/png | preview/card-K0*-v3.png | 8 张统一重渲，确认字标修复 |
| A14-v4-K01…K08 | drafts/a14-K0*-v1.snapshot | 1.1–3.1s | 200 image/png | preview/card-K0*-v4.png | 加入孤字控制后重渲；逐张打开时在 K05 上发现「Contrast 」被服务端裁掉 |
| A14-v4-sheet-0a9defc8 | drafts/a14-contact-sheet-v1.snapshot | 18.26s | 200 image/png | preview/contact-sheet-v4.png | 接触表复查 |
| A14-v5-K01…K08 | drafts/a14-K0*-v1.snapshot | 1.2–2.6s | 200 image/png | preview/card-K0*-v5.png | 字宽模型换成标定值后重渲 8 张；K05 取 56px 两行，文字完整 |
| A14-v5-sheet-3b88367d | drafts/a14-contact-sheet-v1.snapshot | 2.11s | 200 image/png | preview/contact-sheet-v5.png | 最终接触表并打开确认一致性 |
| A14-final-K01…K08 | outputs/run-20261011-01/A14/card-K0*.snapshot | 见 metrics | 200 image/png | outputs/run-20261011-01/A14/card-K0*.png | 定稿渲染并逐张打开复查 |

## 4. 修改记录与踩坑

| 版本 / 类型 | 观察到的实际问题 | 原因及确认依据 | 实际修改 | 复验结果 |
|---|---|---|---|---|
| v1 · visual | 8 张卡的品牌标记内字标只画出「S/」，V 被裁掉 | 字号按 `size*0.46=25.76px` 给，而文本框只有 `size*0.72=40.3px` 宽，「S/V」字面宽约 48px 装不下 | 字号固定到 20px、框宽 40px | S/V 完整显示 |
| v1 · visual | 改成相对坐标后字标**整段消失** | 误把内层 Positioned 的 left/top 当成画布坐标给了 (48, 55)，文本框实际落在 56×56 标记方块之外被裁 | 改回标记方块内的相对坐标 (8, 15) | S/V 完整显示 |
| v1 → v2 · visual | 1 行标题（K01）时眉题与标题之间出现约 300px 死区 | 标题块一律下对齐到 y=456，行数变化只让文字向上生长，短标题就悬在下方 | 改为在标题带 [150,470] 内垂直居中，最底仍 <470 <496（讲者分隔线），「不碰撞」依旧由结构保证 | 1/2/3 行标题都落在同一视觉带内 |
| v1 → v2 · visual | 讲者文本框底边 594px，越过 590px 安全下边距 | 下对齐时多加了一个 +6px 的字面上偏 | 偏置改为 +4px、基准上移到 584 | 实测内容墨迹下缘 8/8 ≤590 |
| v1 → v2 · visual | 取消卡斜纹带压在页眉日期文字后面 | 斜纹放在 x≥950、y 0–120 的顶部，正好覆盖日期 | 移到最右侧 110px 的竖带（x 1090–1200）并压到 5% 不透明度 | 日期清晰，斜纹只作边缘质感 |
| v3 → v4 · visual | K02 末行只剩「约束」两个字 | 贪心断行把 12 字标题切成 10+2，2 字孤字在主标题末尾很难看 | 加入孤字判据（末行字面宽 < 标题栏 25% 即判孤字），命中则降一档字号重排 | K02 变成 56px 单行；K01–K08 其余不受影响 |
| v4 → v5 · visual | **K05 标题丢词**：画面只剩「Color, Alpha &」，`Contrast ` 整段消失 | 字宽模型把 Inter Semi Bold 的 `<` `&` 只给 0.42em、拉丁小写 0.55em，系统性偏小 8–18%；wrap() 判定 663.7px 放得下 700px 的框，而真实字面宽超过 700px，被服务端**按框宽静默裁掉**（HTTP 仍 200） | ① 做 12 行样张的标定探针，用 PIL 量出真实墨迹宽；② `char_em()` 换成实测系数（`<` `&` 0.66、拉丁小写 0.60、大写 0.70、数字 0.53）；③ `pick_size()` 增加 T3 兜底分支：任一行字面宽超过字面框就继续降档 | K05 取 56px 两行，标题完整；8 张的实测/估算比值落在 0.93–1.02 |

「渲染成功但视觉不符合要求」的问题同样记录在上面的完整视觉迭代中。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/run-20261011-01/A14/task-metrics.json`


| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始 / 结束时间 | 2026-10-12T10:07:33.145+08:00 / 2026-10-12T10:24:18.817+08:00 | ISO8601 带时区 | 计时记录（本地时钟，带时区） |
| 任务总耗时 | 1005.672 | 秒 | 墙钟时间（读题 → 计算 → 构造 → 渲染 → 看图 → 修复 → 报告） |
| 首次可用图耗时 | 2.784 | 秒 | 从开始到首个 `200 image/png` 且能打开的图为止的全部请求耗时之和；本任务请求串行，故与实际顺序一致 |
| 等待用户反馈 | 0.0 | 秒 | 本题为单轮任务，无多轮反馈等待 |
| 限流等待 | 0.0 | 秒 | 全程未出现 `429`（见 `requests.jsonl`） |
| 排队等待 | None | 秒 | 服务未提供排队指标，不可测量，记 null 而非 0 |
| 已记录请求耗时之和 | 132.068 | 秒 | `requests.jsonl` 中 `duration_seconds` 求和；请求串行，不与墙钟重复计入 |
| 成功 / 失败 / 重试请求 | 66 / 1 / 0 | 次 | `requests.jsonl`；失败均为不同 DSL 的语法修复，非同一请求重试 |
| 看图 / 完整视觉迭代 | 24 / 13 | 次 | `iterations.jsonl` 与实际图像查看记录 |
| DSL 版本数 | 49 | 个 | `requests.jsonl` 去重 |
| Server-Timing | null | — | 服务响应未返回该头，日志中如实记为 null |


## 6. 设计选择、经验与未解决事项


**关键设计选择**

1. *先把「服务端的字宽模型」量出来，再谈排版*。这是本题真正的坑。
   首版我用通用的 em 系数表估字宽，把 K05 的「Color, Alpha & Contrast 」算成 663.7px，
   判定放得下 700px 的 Text 框；结果真实字面宽超过 700px，
   **服务端按框宽把右端静默裁掉**，画面上「Contrast 」整段消失，而 HTTP 状态是 200、
   `image_info` 也完全正常。这类失败不会报错，只会在看图时暴露。
   于是补了 12 行 100px 样张的标定探针，用 PIL 逐列量墨迹宽度，反推出各类字符的 em 系数：
   `Inter Semi Bold` 的 `<` `&` 约 0.66em（我原来给 0.42）、拉丁小写 0.60em（原来 0.55）、
   大写 0.70em、数字 0.53em；`Noto Sans CJK SC` 全角实测 0.98–1.00em（原来 1.0 是对的）。
   换系数后 8 张卡的「实测墨迹宽 / 声明估算宽」比值落在 0.93–1.02。
   这条系数直接来自 `drafts/width-calibration.json`，不是拍脑袋。

2. *在选字号上加一道"绝不丢字"的兜底*。`pick_size()` 现在的分支是
   T1（≤2 行且无孤字）→ T2（≤3 行且无孤字）→ T2′（≤3 行，允许孤字）→ T3（最宽行仍不超过字面框）。
   T3 是专门为了「宁可降档也不让服务端裁字」加的；本题 8 条数据都没走到 T3，
   但只要输入再长一点就会命中。题面的 36px 硬底线始终留在阶梯里。

3. *不靠"缩字号"解决所有问题，而是先把层级关系写成规则*。
   首版阶梯让 K08 拿到 40px，而时间字号是 46px——主标题被次要信息压过去了。
   于是加了一条层级规则：**标题字号不得低于「时间字号 × 1.2」**，
   由此推出层级下限 48px，阶梯只在 48–64 之间取值。K08 因此落在 56px/3 行。
   这条规则是数据无关的，换任何一批讲座都成立。

4. *碰撞问题用结构解决，而不是靠对齐*。标题栏固定 x=40…740，徽标固定 x=936…1160，
   横向净距 196px；标题块只在 y 方向于 [150,470] 内活动，最底仍高于 496 的讲者分隔线。
   因此「标题不与状态徽标碰撞」对任意长度的标题都成立，不需要逐张微调。
   `verification` 里逐张量了实测墨迹右缘与徽标左缘，`no_collision` 8/8 为 true。

5. *状态做成三通道而不是只靠颜色*。颜色（绿/琥珀/紫/红）+ DSL 现画的几何符号
   （实心圆 / 圆角方块 / 圆环 / 叉号）+ 原始状态文字。
   符号全部用 `ClipOval`、`Container`、`Container+border`、`Transform` 画出来，
   不依赖任何特殊字形，因此在任何字体环境下都稳定；
   `verify_a14.py` 还按形状分别判定了实心度（`dot` 中心填充率 > 0.75、`ring` < 0.15）。

6. *把「长度分支」显式画出来*。右侧层格条的数量直接等于标题行数，
   字号取 48/56/64 三档、行数取 1/2/3 三档——这些不是手工挑的，
   全是 `pick_size()` 在阶梯上跑出来的，条件写在 `batch-audit.json` 的 `branch` 字段里。
   实测 7 张走 T1 分支（≤2 行），只有 K08 走 T2 分支（3 行）；
   题面的 36px 硬底线与 T3 兜底分支在本题数据下都没有被触发，如实记录未触发。

**问题与修复（要点）**

- 本题唯一"看不见"的缺陷就是 K05 丢词。它不会触发任何错误码，
  只有**逐张打开图**才会发现——这正好印证了「不能以渲染成功代替看图」。
- 相对坐标与绝对坐标混淆导致字标消失，值得单独记住：
  `Positioned` 的 `left`/`top` 永远相对**直接父容器**，
  在 `Container` 内部再套 `Positioned` 时很容易写错基准。

**可复用经验**

- **服务端会按 Text 框宽静默裁掉溢出文字，且 HTTP 仍返回 200。**
  做批量排版前必须先标定字宽模型，并加"最宽行不得超过字面框"的兜底降档。
- 中文断行：全角逐字可断、拉丁词整体不可断、收尾标点（：，。、；？！·—…）不得置于行首。
- 孤字控制（末行不足栏宽 25% 就降档）是很划算的一条规则，代价只是一次降档。
- 用 `Container` + `border` + 小 `borderRadius` 画状态符号（空心圆环）时，
  记得 A13 得到的限制：**圆角必须大于线宽**，否则服务端 500。
- 标记/徽标这类"小方块里的字标"，内层坐标一律相对方块本身，并给足框宽。

**结束依据**：8 张定稿逐张整屏打开（`reviews` 有 8 条独立条目与各自观察），
再用 `verify_a14.py` 对交付 PNG 做像素级对账（标题行数、每行墨迹宽与声明估算的比值、
标题右缘与徽标左缘的净距、全图内容墨迹包围盒与 40px 安全边距、状态颜色与符号实心度），
8/8 通过。中间另有 5 轮 14 次看图与 2 张接触表。未以「渲染成功」作为完成依据。


### 未解决事项 / 限制


- 无影响交付的未解决问题。
- 讲者「最多两行」的分支已实现但 8 条数据都没触发（最长的是 K07 的
  「Northstar Research · 林川」，26px 下 1 行即容下）。审计里
  `speaker_typography.two_line_branch_used = false` 如实记录，
  不谎称该分支被验证过视觉效果。
- `char_em()` 的系数是对 Inter Semi Bold / Inter Medium / Noto Sans CJK SC 在本 run
  服务端上的实测值（`drafts/width-calibration.json`）；若服务端更换字体或字重，
  需要重跑 `probe_width_a14.py` + `measure_width_a14.py` 重新标定。
- 标定探针 12 行样张中有 2 行（23 字与 27 字的纯中文长句）超出 1600px 探针框而被裁，
  这 2 行**未参与**系数拟合，只在 `width-calibration.json.rows` 里保留了实测值与
  `estimated_px` 的对照，避免用被裁的数据反推系数。
- 接触表按同一规则等比缩小重绘，用于横向比较一致性；它**不是**八张原图的替代品，
  只存在于临时目录，未进入交付目录。


### 留痕确认

- 临时目录中的草稿 DSL、各次请求体副本、成功图片、失败响应 JSON、放大裁切图与预览全部保留，未删除或覆盖任何一次尝试；日志为追加写入。
- `tasks/` 下的输入文件、任务说明与模板均未被修改。
- 未保存任何密钥；`SNAPSHOT_API_KEY` 若存在只从环境变量读取，不写入 DSL 或日志。
- 总任务根 `.gitignore` 已创建（参考 `templates/gitignore-template.txt`），仅排除 `__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`、`.ipynb_checkpoints/`、`node_modules/.cache/` 等明确的运行时缓存；**未**使用 `tmp/`、`outputs/`、`cache/`、`.cache/`、`*.log` 或图片/DSL/JSON 通配规则，因此本任务的过程证据不会被忽略（共享规则详见 `_suite/snapshot-usage.md`）。
- `__pycache__/` 等运行时缓存不作为留痕材料，也不列为产物或自检证据。
