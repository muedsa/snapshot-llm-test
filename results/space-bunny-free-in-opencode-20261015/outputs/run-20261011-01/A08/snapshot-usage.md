# Snapshot 使用情况说明与踩坑记录

任务ID：A08
任务名称：展馆双路线导览与共享通道
本次运行ID：run-20261011-01
完成状态：完成
结束原因：需求满足并完成逐图视觉自检
输出目录：`outputs/run-20261011-01/A08/`（路径基准：suite_root）
临时目录：`tmp/run-20261011-01/A08/`（路径基准：suite_root）
路径基准：suite_root；除本报告的 Markdown 本地链接（相对本文件所在目录）外，
所有记录中的本地路径均为相对 suite_root 的相对路径，未写死机器盘符或用户目录。

遵循 [PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录环境变量。
Markdown 本地链接相对当前文档；本报告位于 `outputs/<run_id>/A08/`，
故指向题库文档的链接为 `../../../tasks/…`。

## 1. 最终产物与需求完成情况


| 文件 | 用途 | 对应 DSL 或图 | 完成状态 |
|---|---|---|---|
| `wayfinding.snapshot` | 1560×1080 双路线导览定稿 DSL | `wayfinding.png` | 已完成 |
| `wayfinding.png` | 服务返回的最终图 | `wayfinding.snapshot` | 已完成，服务原始响应 |
| `paths.json` | 路径、绘制参数与 10 项核验 | — | 已完成 |
| `snapshot-usage.md` / `task-metrics.json` | 报告与指标 | — | 已完成 |

需求逐项核对（依据最终图**实际查看**：整屏 + 入馆段/离馆段/分岔/门洞 4 处 3× 放大局部）

| 题目要求 | 满足情况 | 证据 |
|---|---|---|
| 1560×1080 单图 | 满足 | 服务 `image_info` = 1560×1080 |
| 完整显示 26×16 网格、阻挡区、通道、两处边界门洞 | 满足 | 网格区 x 60–1100、y 156–796 共 26×16 格；阻挡区灰色块、可走格白色块、27 条栅格线；S/E 门格为浅绿底并在图外边界加 4px 深绿门框条 |
| 格子保持正方形、单格边长 ≥36 像素 | 满足 | 单格 40×40 像素，`drawing.cell_px = 40` |
| 保留侧栏或清楚说明区 | 满足 | 右侧 400px 侧栏：图例、两段共享通道、绘制与计算约定 |
| 显示标题 | 满足 | 「云构展馆 · 双路线导览图」34px |
| 显示 S/E 名称、A–D 入口名称 | 满足 | 图上 S/E/A–D 六个名称标签（22px）+ 底部坐标表 |
| 坐标边缘刻度 | 满足 | 顶边偶数列号 0–24、左边行号 0–15，均 16px；另标「列 x →」「行 y ↓」 |
| 比例尺「1格=2米」 | 满足 | 底部 5 格黑白格尺，标 0 与 10 米，并写「1 格 = 2 米（单格边长 40 像素）」 |
| 两条路线的名称/必经点顺序/步数/米数 | 满足 | 底部 R1/R2 两张卡：名称、必经点链、35 步·70 米、47 步·94 米、格心数、偏移与线宽 |
| 阻挡区、入口点、路线图例 | 满足 | 侧栏 8 项图例，含两条线样式与箭头含义 |
| 不凭空画展区内部边界 | 满足 | 图上只画输入网格的墙/通道；A–D 仅是格心标记 |
| 路线用颜色 + 线型/符号两种方式区分 | 满足 | R1 深青实线 8px、R2 橙色虚线 6px（9/7 虚线节距），并各带白描边箭头 |
| 开始/分岔/合流/转弯后有方向提示 | 满足 | 每 4 条格间边一个箭头，每个转角后追加一个；分岔点 (6,10) 与合流点 (20,10) 两侧均有箭头（已放大确认） |
| 平行偏移 ≤ 单格边长 12% | 满足 | R1 −4.4px、R2 +4.4px，均为 40px 的 11%（程序核验项「绘制偏移上限」） |
| 描边与箭头须在可走格区域内 | 满足 | 程序核验项「描边落在可走格内」：偏移折线（含斜接点）每个顶点到最近格心距离均 < 20px |
| 不加宽门洞、不改路径、不抄近路穿阻挡格 | 满足 | 逻辑路径只由 4 邻接 BFS 在输入网格上产生；墙体与门洞逐格照抄输入 |
| 两段共享通道中两线身份/方向/接续可辨 | 满足 | 入馆段 9 步、离馆段 8 步，两线同向并排（外侧各加 2.4px 深色衬线），侧栏逐段说明格心与同向关系 |
| S/E/A–D 标记固定格心，文字可移到附近并用引导线 | 满足 | 六个标记固定在格心；文字放在空白墙区，用 1.8px 引导线连到标记边缘（未移动任何地标/墙体/路径） |
| 文字不得被路线或箭头覆盖 | 满足 | 六个标签框均落在墙体区域，程序与放大查看均确认未压线 |
| 正文与展区名称 ≥22、图例 ≥20、边缘坐标 ≥16 | 满足 | 正文/地标名/路线卡 22–26px；图例 20px；坐标刻度 16px |
| 附 paths.json | 满足 | 含 grid/drawing/landmarks/routes/shared_runs/audit，10 项核验均写明方法与依据；无 field_guide |



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

| https://snapshot.muedsa.com/reference/parser-tags/ · Container | `color="None"` 不是合法 CSS 颜色，透明底要用 `#RRGGBBAA`（如 `#FFFFFF00`） | 本题曾因此 400，见修改记录 |
| https://snapshot.muedsa.com/reference/parser-tags/ · Positioned | `Positioned` 只能有一个子节点；背景 `Container` 与内容 `Stack` 要合并在同一个 `Container` 内 | 侧栏「共享通道」卡曾因此 400 |


本次实际用到的能力：布局：`Container`/`Column`/`Row`/`Expanded`/`SizedBox`/`Padding`；精确定位：`Stack(fit=EXPAND)` + `Positioned`；文本：`Text` 的 `fontFamily`/`fontSize`/`textAlign`/`height`/`maxLines`/`letterSpacing`；颜色与透明度：CSS 颜色与 `#RRGGBBAA` 独立 alpha；装饰：`border`（宽度+样式+颜色）、`borderRadius` 与四角圆角、`boxShadow`；裁剪：`ClipRRect`/`ClipOval`；变换：`Transform` 的列主序 4×4 矩阵 + `alignment`；滤镜：`ImageFiltered`（子树模糊）、`BackdropFilter`（仅背景模糊）；渐变：`gradientType=LINEAR/RADIAL/SWEEP` + `gradientColors`/`gradientStops`。解析器未提供 `ClipPath`/多边形，所有图形均由矩形、圆角矩形、椭圆与渐变拼装。
本题额外用到：网格几何全部由程序从 `inputs/floor.txt` 读入：墙体按行做极大连续段合并以减少图元数量，可走格逐格绘制，并叠加 27 条半透明栅格线保证 26×16 网格完整可见；任意方向线段用 `Transform` 列主序 4×4 旋转矩阵绘制；**带斜接(miter)的平行偏移折线**让两条路线在同一中心线两侧并行、转角处仍保持固定间距；虚线由沿折线均匀排布的短胶囊组成；箭头由两段旋转胶囊构成 V 形，并先画一层加粗白色描边再画彩色笔画，使方向提示在同色实线上也能看清；

字体：实际查询 `GET /fonts` 得到 27 个字体族，原始响应留存于
`tmp/run-20261011-01/A08/responses/`（request_type=fonts），另有整理副本 `outputs/run-20261011-01/A08/../_suite/fonts-list.txt`。
中文正文使用 `Noto Sans CJK SC`，数字/拉丁使用 `Inter` 系列，代码/等宽使用 `Noto Sans Mono CJK SC`。
题目素材政策为纯 DSL，未使用任何外部图片（`<Image>` 标签本次未使用）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/run-20261011-01/A08/requests.jsonl`
迭代记录文件：`tmp/run-20261011-01/A08/iterations.jsonl`
响应与草稿留痕：`tmp/run-20261011-01/A08/responses/`、`tmp/run-20261011-01/A08/drafts/`

渲染请求总数：11
成功次数：6
失败次数：5
重试请求数：0（是总请求的子集）
DSL版本数：5
实际图片查看次数：10
完整视觉迭代数：3
未完成视觉迭代数：0
其他接口查询：字体查询与文档读取为 run 级共享准备；本题无额外接口查询。渲染曾出现一次 HTTP 200 但响应体 0 字节的服务端空响应（耗时 184.8s），原样保留在 responses/ 并按同一 DSL 重试成功，记为一次失败 + 一次重试。

初次生成和查看计为基线，不计为改进迭代。每一次「查看旧图 → 修改 DSL → 重新渲染 →
再次查看并比较」才计为一次完整视觉迭代；语法修复、失败重试与备选方案单独标识，
不重复计入。所有图片均已用图像工具实际打开查看（含整屏与放大局部）。

| 请求ID | 输入 DSL | 耗时 | HTTP / Content-Type | 响应文件 | 查看与实际结果 |
|---|---|---|---|---|---|
| A08-v1-b92be75d | drafts/a08-v1.snapshot | 2.21s | 400 application/json | responses/A08-v1-b92be75d.error.json | 无图；`Tag Positioned only can have one child`（侧栏共享通道卡把背景 Container 与 Stack 并列放进 Positioned） |
| A08-v1-8ac356f5 | drafts/a08-v1.snapshot | 3.69s | 400 application/json | responses/A08-v1-8ac356f5.error.json | 无图；构建脚本自身的语法错误导致 DSL 未更新，仍是上一处错误 |
| A08-v1-8db901af | drafts/a08-v1.snapshot | 2.07s | 400 application/json | responses/A08-v1-8db901af.error.json | 无图；`Attr [color] unsupported CSS color [None]`——`color="None"` 不是合法 CSS 颜色 |
| A08-v1-761e0d2e | drafts/a08-v1.snapshot | 1.85s | 400 application/json | responses/A08-v1-761e0d2e.error.json | 无图；同类错误（透明底需写成 `#FFFFFF00`） |
| A08-v1-667fded2 | drafts/a08-v1.snapshot | 17.92s | 200 image/png | kept/A08-v1-667fded2.png | 首版出图并实际打开：页眉右侧说明被侧栏裁掉；「行 y 列 x」互相压字；E 的出口门洞色条画到了 (94,436) 而非门格处；S 的标签被底部路线卡盖住；D 标记被 E 标签压住；比例尺「0」与「10 米」重叠；侧栏末段文字溢出画布；R2 必经点文字被裁 |
| A08-v2-08f8c5b3 | drafts/a08-v1.snapshot（构建失败时的旧稿） | 4.88s | 200 image/png | kept/A08-v2-08f8c5b3.png | 与上一张相同的旧 DSL，仅用于确认可重复渲染 |
| A08-v2-1e2ec777 | drafts/a08-v1.snapshot | 5.47s | 200 image/png | kept/A08-v2-1e2ec777.png | 已打开：门洞色条、S 标签、R2 必经点、比例尺、侧栏溢出均已修好；E 标签仍与 D 标记争位，地标文字仍带坐标导致超宽 |
| A08-v3-84839d94 | drafts/a08-v1.snapshot | 184.76s | 200 image/png（响应体 0 字节） | responses/A08-v3-84839d94.error.png | 无图；服务端返回 200 但响应体为空。按同一 DSL 重试（属 retry，非新设计） |
| A08-v3-045755ba | drafts/a08-v1.snapshot | 7.90s | 200 image/png | kept/A08-v3-045755ba.png | 已打开：版面全部收敛，10 项程序核验通过；R1 实线上的箭头与线同色、方向提示偏弱 |
| A08-v4-b95160e5 | drafts/a08-v1.snapshot | 4.45s | 200 image/png | kept/A08-v4-b95160e5.png | 已打开：箭头加白色描边后方向提示清晰；并放大确认两个共享段、分岔 (6,10)、合流 (20,10)、S/E 门洞与六个地标标签；示意图通过 |
| A08-final-* | outputs/run-20261011-01/A08/wayfinding.snapshot | 见 metrics | 200 image/png | outputs/run-20261011-01/A08/wayfinding.png | 定稿渲染并打开复查 |

## 4. 修改记录与踩坑

| 版本 / 类型 | 观察到的实际问题 | 原因及确认依据 | 实际修改 | 复验结果 |
|---|---|---|---|---|
| v1 · syntax-fix | 服务 400：`Positioned only can have one child` | 侧栏「共享通道」卡把背景 `Container` 与内容 `Stack` 并列放进 `Positioned` | 合并为 `Positioned > Container > Stack > Positioned…` | 进入下一处错误 |
| v1 · syntax-fix | 服务 400：`unsupported CSS color [None]` | 想画「只有描边、没有填充」的透明容器，写了 `color="None"` | 改用 8 位十六进制 `#FFFFFF00`（alpha=0），共 3 处（网格外框、S/E 圆环、地标圆环） | 出图 |
| map v2 · visual | E 门洞的深绿边框条出现在 (94,436)，远离门格 | `ex = OX + (2 if S else CELL-6)` 漏乘了 `cx * CELL`，把列偏移当成了绝对坐标 | 改为 `OX + cx * CELL + (2 if S else CELL - 6)` | S/E 门框条落在各自门格外边界 |
| map v2 · visual | S 的标签「S 入口门格 (0,13)」完全被底部 R1 路线卡遮住 | 标签框取在 y 824–858，而路线卡从 y 812 开始 | 把 S 标签移到 (62,722)–(242,758)，落在第 14 行全墙区域内 | 标签完整可见，引导线变短 |
| map v2 · visual | D 标记「D」被 E 的标签框完全盖住 | E 标签框 (856,386)–(1000,420) 与 D 标记 (880,416) 重叠 | E 标签移到 (898,332)–(1073,368)；D 标签左移到 (676,452)–(851,486) | D、E 两个标记与标签都可见 |
| map v2 · visual | R2 必经点「入口门格 → 结构剧场入口 → 作品巡览入口 → 出口门格」右端被裁 | 25 个全角字符在 22px 下约 550px，超出 505px 卡片内宽 473px | 改用紧凑写法「入口→结构剧场→作品巡览→出口」（21 字符 ≈ 462px） | 完整显示 |
| map v2 · visual | 比例尺的「0」与「10 米（5 格 × 2 米）」叠字 | 两段文字都从 `sx` 起排 | 「0」以尺子起点为中心、「10 米」以尺子终点为中心，另起一行写「1 格 = 2 米（单格边长 40 像素）」 | 刻度与说明分层，互不重叠 |
| map v2 · visual | 侧栏「绘制与计算约定」末条溢出画布底边 | 侧栏纵向内容按固定步长累加，未按实测行数收敛 | 图例行距 32→30、共享卡 104→96px、说明由 4 条并为 3 条并精简文字 | 侧栏内容底边落在画布内 |
| map v2 · visual | 页眉右侧「俯视平面示意图…」被侧栏裁掉；「行 y 列 x」互相压字 | 右侧说明右对齐到 x=1560 之外；两个轴标题框宽度之和超过可用间距 | 右侧说明改为 340px 宽、右边界 1100；轴标题改为「列 x →」/「行 y ↓」并分置左右 | 页眉与轴标题均完整 |
| map v3 · visual | R1 实线上的箭头与线同色、几乎看不出方向 | 同色箭头压在同色实线上，轮廓被吞掉 | 箭头先画一层加粗 2.4px 的白色描边（并略微加长），再叠彩色笔画；箭头密度由每 3 边改为每 4 边 + 每个转角后一个 | 放大后两条路线的方向提示都清晰 |

「渲染成功但视觉不符合要求」的问题同样记录在上面的完整视觉迭代中。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/run-20261011-01/A08/task-metrics.json`


| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始 / 结束时间 | 2026-10-11T15:35:00.000+08:00 / 2026-10-11T15:58:58.199+08:00 | ISO8601 带时区 | 计时记录（本地时钟，带时区） |
| 任务总耗时 | 1438.199 | 秒 | 墙钟时间（读题 → 计算 → 构造 → 渲染 → 看图 → 修复 → 报告） |
| 首次可用图耗时 | 27.745 | 秒 | 从开始到首个 `200 image/png` 且能打开的图为止的全部请求耗时之和；本任务请求串行，故与实际顺序一致 |
| 等待用户反馈 | 0.0 | 秒 | 本题为单轮任务，无多轮反馈等待 |
| 限流等待 | 0.0 | 秒 | 全程未出现 `429`（见 `requests.jsonl`） |
| 排队等待 | None | 秒 | 服务未提供排队指标，不可测量，记 null 而非 0 |
| 已记录请求耗时之和 | 240.375 | 秒 | `requests.jsonl` 中 `duration_seconds` 求和；请求串行，不与墙钟重复计入 |
| 成功 / 失败 / 重试请求 | 6 / 5 / 1 | 次 | `requests.jsonl`；失败均为不同 DSL 的语法修复，非同一请求重试 |
| 看图 / 完整视觉迭代 | 10 / 3 | 次 | `iterations.jsonl` 与实际图像查看记录 |
| DSL 版本数 | 5 | 个 | `requests.jsonl` 去重 |
| Server-Timing | null | — | 服务响应未返回该头，日志中如实记为 null |


## 6. 设计选择、经验与未解决事项


**关键设计选择**

1. *逻辑与绘制彻底分离*。路径只由 4 邻接 BFS 在输入网格上产生，**格心序列**是唯一事实来源；
   绘图时对折线做法向偏移（斜接 miter）后再画笔画。里程按逻辑格间边计（每边 2 米），
   与题面「不按描边偏移后的像素长度估算」一致。
2. *偏移量取 11% 而不是顶格 12%*。R1 偏 −4.4px（线宽 8px，占 −8.4…−0.4）、
   R2 偏 +4.4px（线宽 6px，占 +1.4…+7.4），两线之间留 1.8px 间隙，外侧到格心 8.4px < 半格 20px。
   这样既不触到 12% 上限，也保证描边完整落在 40×40 的可走格内。
3. *转角必须用斜接而不是逐段独立偏移*。逐段独立偏移会在 90° 转角处产生 √2 倍的错位缺口；
   实现里对每个顶点取进出法向量的平均方向并按 `1/cos(θ/2)` 放大，转角处两线仍保持固定间距。
4. *共享段用「外侧深色细衬线 + 并排双线」表达*。只画两条不同颜色的线在 40px 宽的通道里容易糊成一条；
   在两条线外侧各加一条 2.4px 深色衬线（画在路线之下），读图时能立刻看出「同一通道内两条路线并行」，
   且衬线宽度仍小于通道宽，不会被误认为第三条路线（侧栏图例专门说明这一点）。
5. *方向提示用带白描边的 V 形箭头*。实线上的同色箭头会被线条吞掉；
   先画一层加粗白色胶囊再叠彩色笔画后，箭头在实线和虚线上都清晰。
   密度为「每 4 条格间边一个 + 每个转角后一个」，既覆盖了分岔点 (6,10) 与合流点 (20,10)，又不至于过密。
6. *地标文字一律放到空白墙区*。S/E/A–D 六个标记固定在格心（题目允许标记局部遮住路线），
   文字按「离标记最近的空白墙块」逐个指定矩形，并用 1.8px 引导线连到标记边缘 17px 处，
   既不移动任何地标/墙体/路径，也不让文字压到路线。

**问题与修复（要点）**

- 服务端会把「HTTP 200 + 0 字节响应体」也当作失败产物；本次遇到一次（耗时 184.8s），
  按同一 DSL 重试即成功，已按失败 + 重试如实记账，未隐藏。
- `Container` 的 `color` 不接受 `None`，透明底必须写成 `#RRGGBBAA`。
- 纵向堆叠的侧栏必须按**实测行数**收敛高度，否则末尾条目会溢出画布。

**可复用经验**

- 「平行偏移画多条路线」类题目的三件套：偏移 ≤ 12% 单格、线宽按偏移反推、转角用 miter；
  再加一条外侧衬线解决「两色糊成一条」的问题。
- 用「等长路径条数」验证题面所说的「唯一最短解」，比只看距离更有说服力；
  本题 R1 及 R2 的三个分段等长路径条数均为 1，与题面描述一致。
- 共享通道必须按**格间边**判定；只共享一个格心（如 (6,10)、(20,10)）不算共享通道，
  否则会多报出两段假共享。

**结束依据**：最终图实际整屏打开，并 3× 放大查看了入馆共享段、离馆共享段、分岔点 (6,10)、
合流点 (20,10)、S 门洞、E 门洞与六个地标标签。确认：两条路线全程可独立追踪、共享段两线并排且同向、
门洞与地标未被移动、文字未被路线覆盖、10 项程序核验全部通过。未以「渲染成功」作为完成依据。


### 未解决事项 / 限制


- 无影响交付的未解决问题。
- 大尺寸 DSL（本次约 187KB、约 900 个图元）偶发触发服务端空响应（HTTP 200 + 0 字节）。
  本题只出现 1 次，重试即成功；已在 `requests.jsonl` 中如实记录，未做无谓的图元削减。
- 题目未规定两条路线在图上的配色与线型，R1/R2 的样式由本程序选定并写入 `paths.json.drawing.route_styles`；
  平行偏移方向（法向量的哪一侧为正）由折线行进方向决定，因此同一条路线在全程保持一致的左右关系。
- 侧栏「绘制与计算约定」中的像素数（origin 60,156 / 单格 40）与 `paths.json` 一致；
  若后续修改地图尺寸需同步更新该说明与 JSON。


### 留痕确认

- 临时目录中的草稿 DSL、各次请求体副本、成功图片、失败响应 JSON、放大裁切图与预览全部保留，未删除或覆盖任何一次尝试；日志为追加写入。
- `tasks/` 下的输入文件、任务说明与模板均未被修改。
- 未保存任何密钥；`SNAPSHOT_API_KEY` 若存在只从环境变量读取，不写入 DSL 或日志。
- 总任务根 `.gitignore` 已创建（参考 `templates/gitignore-template.txt`），仅排除 `__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`、`.ipynb_checkpoints/`、`node_modules/.cache/` 等明确的运行时缓存；**未**使用 `tmp/`、`outputs/`、`cache/`、`.cache/`、`*.log` 或图片/DSL/JSON 通配规则，因此本任务的过程证据不会被忽略（共享规则详见 `_suite/snapshot-usage.md`）。
- `__pycache__/` 等运行时缓存不作为留痕材料，也不列为产物或自检证据。
