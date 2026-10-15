# Snapshot 使用情况说明与踩坑记录

任务ID：A07
任务名称：三线换乘图与路线核验
本次运行ID：run-20261011-01
完成状态：完成
结束原因：需求满足并完成逐图视觉自检
输出目录：`outputs/run-20261011-01/A07/`（路径基准：suite_root）
临时目录：`tmp/run-20261011-01/A07/`（路径基准：suite_root）
路径基准：suite_root；除本报告的 Markdown 本地链接（相对本文件所在目录）外，
所有记录中的本地路径均为相对 suite_root 的相对路径，未写死机器盘符或用户目录。

遵循 [PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录环境变量。
Markdown 本地链接相对当前文档；本报告位于 `outputs/<run_id>/A07/`，
故指向题库文档的链接为 `../../../tasks/…`。

## 1. 最终产物与需求完成情况


| 文件 | 用途 | 对应 DSL 或图 | 完成状态 |
|---|---|---|---|
| `network-map.snapshot` | 1600×1000 全网示意图定稿 DSL | `network-map.png` | 已完成 |
| `network-map.png` | 服务返回的最终图 | `network-map.snapshot` | 已完成，服务原始响应 |
| `travel-card.snapshot` | 720×1280 三条路线旅行卡定稿 DSL | `travel-card.png` | 已完成 |
| `travel-card.png` | 服务返回的最终图 | `travel-card.snapshot` | 已完成，服务原始响应 |
| `routes.json` | 站序/线路段/区段数/换乘/无障碍结论与最优性核验 | — | 已完成 |
| `snapshot-usage.md` / `task-metrics.json` | 报告与指标 | — | 已完成 |

需求逐项核对（依据最终图**实际查看**：整屏 + 中心/右下/左侧放大局部）

| 题目要求 | 满足情况 | 证据 |
|---|---|---|
| 1600×1000 示意图 + 720×1280 旅行卡 | 满足 | 服务 `image_info` 分别为 1600×1000 与 720×1280 |
| 使用 inputs/network.json | 满足 | 16 站、3 线、3 查询全部取自输入；输入文件未修改（`inputs.modified=false`） |
| 按线路站序连接相邻站、相邻站可双向 | 满足 | 16 条区段全部由 `lines[].stations` 相邻项生成，`network.bidirectional=true` |
| 相邻站耗时相同 ⇒ 最小化边数即最小化耗时 | 满足 | `network.adjacent_segment_duration` 记录该前提，求解目标即最少站间边数 |
| 共享站是换乘站 | 满足 | S04(R/B)、S05(R/G)、S08(B/G) 三站画深色外环并列出双线路字母 |
| 单纯线条交叉不能让人误认为换乘 | 满足 | 全网唯一的交叉点 (970,380)（蓝线 S10–S11 × 绿线 S05–S16）只画灰色小圆点 + 就地说明「交叉点·非换乘」，无换乘标记；图例与读图约定各写一次 |
| 用颜色加线路字母，不只靠红绿差异 | 满足 | 每条线在页眉色卡、轨道中点字母徽标、站名标签三处同时出现颜色 + 字母（R/B/G） |
| 16 站名称与编号完整 | 满足 | S01–S16 的编号与站名全部出现在图中，均为 20px |
| 线路用折线绘制，转折 45° 或 90° | 满足 | 程序逐段判定：`angle_histogram = {"45°": 7, "90°": 9}`，`all_segments_45_or_90=true` |
| 明确标注非地理示意图 | 满足 | 页眉右侧橙色粗体「非地理示意图：线路走向、站距与折点仅表达拓扑，不代表真实地理位置」 |
| 标注各站无障碍状态并给图例 | 满足 | 16 个站名标签左端均有角标（青绿实心=具备 / 红框斜杠=不具备），图例列出两者含义 |
| accessible=false 不作起点/终点/换乘站，且不删线路 | 满足 | 4 个非无障碍站（S03/S05/S09/S14）全部保留在线路上；判定只作用于端点与换乘站，图面与 JSON 写明「可乘车通过」 |
| 3 个查询求最少站间边数路线，边数相同再比换乘 | 满足 | Q1 6 区间/1 换乘、Q2 6 区间/1 换乘、Q3 4 区间/1 换乘；`optimality` 记录 BFS + 穷举枚举方法与候选数 |
| 记录站序、线路段、区段数、换乘次数 | 满足 | `routes.json` 的 `queries[].normal` 四项齐备；旅行卡逐条列出 |
| 旅行卡展示 3 条普通旅程及可否作为无障碍旅程 | 满足 | 三张卡各有绿/红结论框并写明理由 |
| 最短普通旅程不满足时另求最短无障碍旅程 | 满足 | Q2 最短路线的换乘站东桥(S05) 不具备无障碍设施，卡片与 JSON 另给 6 区间/2 换乘的合规最短路线 |
| 换乘=改变线路，首次上车不算 | 满足 | 卡片页脚与 JSON `transfer_definition` 均写明 |
| 不把站数误作区间数 | 满足 | 卡片摘要行写作「7 站 / 6 站间区段」，JSON 记 `interval_count_note` |
| 两图视觉系统一致、分别排版 | 满足 | 共用同一套配色、字体族与卡片圆角/描边风格；示意图为横版三栏，旅行卡为竖版单栏 |
| 地图标签 ≥20、手机正文 ≥20 | 满足 | 站名/编号/字母/图例/说明全部 20px 及以上（标题 33px、卡片标题 22–26px） |
| 附 routes.json | 满足 | 字段遵循 `templates/audit-fields.json`，含 queries/accessibility/optimality/content_map 四个数组 |



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

| https://snapshot.muedsa.com/reference/parser-tags/ · Transform | `Transform` 只能有**一个**子节点；需要「圆形底 + 文字」时把文字放进 `Container` 的 `alignment="CENTER"`，不能并列两个 `Positioned` | 本题曾因此失败，见修改记录 |
| https://snapshot.muedsa.com/reference/parser-tags/ · Positioned | `Positioned` 必须是 `Stack`/`IndexedStack` 的直接子节点；`Row`/`Column` 内不能放 `Positioned` | 右侧图例行改为 `Positioned > Container > Stack` |


本次实际用到的能力：布局：`Container`/`Column`/`Row`/`Expanded`/`SizedBox`/`Padding`；精确定位：`Stack(fit=EXPAND)` + `Positioned`；文本：`Text` 的 `fontFamily`/`fontSize`/`textAlign`/`height`/`maxLines`/`letterSpacing`；颜色与透明度：CSS 颜色与 `#RRGGBBAA` 独立 alpha；装饰：`border`（宽度+样式+颜色）、`borderRadius` 与四角圆角、`boxShadow`；裁剪：`ClipRRect`/`ClipOval`；变换：`Transform` 的列主序 4×4 矩阵 + `alignment`；滤镜：`ImageFiltered`（子树模糊）、`BackdropFilter`（仅背景模糊）；渐变：`gradientType=LINEAR/RADIAL/SWEEP` + `gradientColors`/`gradientStops`。解析器未提供 `ClipPath`/多边形，所有图形均由矩形、圆角矩形、椭圆与渐变拼装。
本题额外用到：任意方向的线段由 `Transform` 的列主序 4×4 旋转矩阵 + `alignment="CENTER"` 拼出，并按单位法向量做**法向偏移**，使同一条轨道上多条查询路线的细线并列错开而不互相遮挡；线路字母徽标正立放置（不随轨道角度旋转）以保证字母可读；站点圆点用 `ClipOval` + 白底描边区分普通站与换乘站，「不具备无障碍设施」用 `ClipRRect` 红框加旋转 45° 的短横线表示；站名标签位置由程序按候选方位枚举求解，逐个候选校验「不压轨道线段（沿线采样 + 外扩 7px）、不压站点圆点、不压已放标签、不出绘图区」，并把最终方位与标签矩形写入 `routes.json` 的 `map_geometry.station_positions`。

字体：实际查询 `GET /fonts` 得到 27 个字体族，原始响应留存于
`tmp/run-20261011-01/A07/responses/`（request_type=fonts），另有整理副本 `outputs/run-20261011-01/A07/../_suite/fonts-list.txt`。
中文正文使用 `Noto Sans CJK SC`，数字/拉丁使用 `Inter` 系列，代码/等宽使用 `Noto Sans Mono CJK SC`。
题目素材政策为纯 DSL，未使用任何外部图片（`<Image>` 标签本次未使用）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/run-20261011-01/A07/requests.jsonl`
迭代记录文件：`tmp/run-20261011-01/A07/iterations.jsonl`
响应与草稿留痕：`tmp/run-20261011-01/A07/responses/`、`tmp/run-20261011-01/A07/drafts/`

渲染请求总数：32
成功次数：29
失败次数：3
重试请求数：0（是总请求的子集）
DSL版本数：13
实际图片查看次数：15
完整视觉迭代数：7
未完成视觉迭代数：0
其他接口查询：字体查询与文档读取为 run 级共享准备；本题另做 11 次「按保留请求体复原历史版本」的补渲染，用于把被同名输出路径覆盖的中间预览重新固化，均记入 `requests.jsonl`（`request_type=render`）。

初次生成和查看计为基线，不计为改进迭代。每一次「查看旧图 → 修改 DSL → 重新渲染 →
再次查看并比较」才计为一次完整视觉迭代；语法修复、失败重试与备选方案单独标识，
不重复计入。所有图片均已用图像工具实际打开查看（含整屏与放大局部）。

| 请求ID | 输入 DSL | 耗时 | HTTP / Content-Type | 响应文件 | 查看与实际结果 |
|---|---|---|---|---|---|
| A07-v1-f193c34b | drafts/a07-v1-map.snapshot | 3.34s | 400 application/json | responses/A07-v1-f193c34b.error.json | 无图；`Tag Transform only can have one child`（线路字母徽标里把 Container 与 Positioned 并列放进 Transform） |
| A07-v1-a41aa8d2 | drafts/a07-v1-map.snapshot | 1.59s | 400 application/json | responses/A07-v1-a41aa8d2.error.json | 无图；`Tag Positioned only can have one child`（左下小结框把 Container 与 Stack 并列放进 Positioned） |
| A07-v1-90fa7900 | drafts/a07-v1-card.snapshot | 4.91s | 200 image/png | 预览已复原为 preview/restored-card-v01-first-render.png | 旅行卡首版出图并实际打开：正文正确，但 Q2 无障碍结论误写为「不存在满足约束的无障碍旅程」，且页脚第二行被画布底边裁掉 |
| A07-v1-387ec990 | drafts/a07-v1-map.snapshot | 2.19s | 400 application/json | responses/A07-v1-387ec990.error.json | 无图；`renderBox.parentData must be StackParentData`（右侧图例行把 Positioned 放进 Row） |
| A07-v1-bea04d1c | drafts/a07-v1-map.snapshot | 2.97s | 200 image/png | preview/restored-map-v01-first-render.png | 示意图首版出图并实际打开：页眉标题被三枚线路色卡压住；图例「换乘站」色标 44px 被 30px 容器裁切 |
| A07-v1-06f54466 | drafts/a07-v1-map.snapshot | 4.64s | 200 image/png | preview/restored-map-v02-header-and-legend.png | 已打开：页眉已分开、图例色标正常；但站名标签里编号与站名被自己的宽度裁成「S0 江湾」「S16 研究」 |
| A07-v1-50d62add | drafts/a07-v1-map.snapshot | 6.19s | 200 image/png | preview/restored-map-v03-label-boxes.png | 已打开：编号/站名完整；S06 的标签因所处 45° 走廊过窄找不到不压线的方位，退回 fallback |
| A07-v1-dc400342 | drafts/a07-v1-card.snapshot | 5.12s | 200 image/png | preview/restored-card-v02-new-layout.png | 已打开：三卡版式成立，但 Q2 仍误判为无合规路线，且三卡总高超出画布 15px |
| A07-v1-4ae6aca7 | drafts/a07-v1-map.snapshot | 2.76s | 200 image/png | preview/restored-map-v04-letters-and-alt.png | 已打开：换乘站字母（RB/RG/BG）显示完整；交叉点仍只有灰点、缺就地说明 |
| A07-v1-6913b715 | drafts/a07-v1-card.snapshot | 3.71s | 200 image/png | preview/restored-card-v03-footer-fix.png | 已打开：Q2 已给出合规最短路线；但页脚第二行仍被底边裁切 |
| A07-v1-9cc91da8 | drafts/a07-v1-card.snapshot | 4.01s | 200 image/png | preview/restored-card-v04-final.png | 已打开：三卡与页脚均在画布内，但结论框内多留一行空白（行数高估） |
| A07-v1-c14120f2 | drafts/a07-v1-map.snapshot | 4.11s | 200 image/png | preview/restored-map-v05-upright-badges.png | 已打开：线路字母徽标改为正立、交叉点加就地说明与引线；交叉说明与 S16 标签不冲突 |
| A07-v1-09430258 | drafts/a07-v1-map.snapshot | 2.87s | 200 image/png | kept/A07-v1-09430258.png | 已打开：右侧面板加「本图为非地理示意图」后总高 1019px，超出面板底边 984px |
| A07-v1-249cd8fd | drafts/a07-v1-map.snapshot | 6.03s | 200 image/png | kept/A07-v1-249cd8fd.png | 已打开：删除面板内重复的非地理声明并压缩间距后收敛 |
| A07-v1-b6530879 | drafts/a07-v1-map.snapshot | 2.57s | 200 image/png | preview/restored-map-v07-panel-fit.png | 已打开：面板文字与分隔线不再重叠，面板底 953px < 984px；示意图通过 |
| A07-v1-b0028b99 / A07-v1-61de0154 / A07-v1-7662de1e | drafts/a07-v1-map.snapshot / a07-v1-card.snapshot | 3.67s / 3.66s / 2.34s | 200 image/png | kept/*.png | 渲染工具改为同时保存带 request_id 的不可变副本后的定稿重渲；整屏复查两图均无重叠与裁切 |
| A07r-*（11 次复原渲染） | drafts/restored-*.snapshot | 2.28–6.20s | 200 image/png | kept/A07r-*.png | 按 `responses/*.request.txt` 中保留的请求体重新渲染全部中间版本，使每个迭代阶段都留有独立 PNG；请求体与响应 JSON 原件均未改动 |

## 4. 修改记录与踩坑

| 版本 / 类型 | 观察到的实际问题 | 原因及确认依据 | 实际修改 | 复验结果 |
|---|---|---|---|---|
| v1 · syntax-fix | 服务 400：`Transform only can have one child` | 线路字母徽标把描边 `Container` 与文字 `Positioned` 并列塞进 `Transform` | 改为 `Transform > Container(borderRadius, border, alignment=CENTER) > Text` | 错误消除 |
| v1 · syntax-fix | 服务 400：`Positioned only can have one child` | 左下小结框把背景 `Container` 与内容 `Stack` 并列放进 `Positioned` | 合并为 `Positioned > Container > Stack > Positioned…` | 进入下一处错误 |
| v1 · syntax-fix | 服务 400：`renderBox.parentData must be StackParentData` | 右侧图例行用 `Row` 承载 `Positioned` | 图例行、查询色例行改为 `Positioned > Container > Stack` | 示意图首次出图 |
| map v2 · visual | 页眉标题「栖云市轨道交通示意图」被三枚线路色卡压住 | 标题与色卡都排在 y=14–20 的同一行 | 页眉改为两行：首行左标题右色卡，次行左统计右非地理声明 | 重叠消除 |
| map v2 · visual | 图例「换乘站」色标被 30×28 容器裁成半圆 | 色标沿用了图上 44px 的换乘圆点尺寸 | 图例改用独立的 30px 深色环 + 22px 白心 | 图例四项全部完整 |
| map v3 · visual | 站名标签里编号与站名被裁成「S0 江湾」「S16 研究」 | 编号槽 38px、站名槽 42px 不足以容纳 20px 文字（且「研究所」为 3 字） | 编号槽 44px、站名槽 64px 并加 `softWrap="false"`；同时把 S06/S12 移到 (1080,650)/(1080,850) 让出标签空间 | 16 个标签全部完整显示 |
| map v3 · visual | S06 标签退回 fallback（压在 45° 红线上） | S06 位于「红 45° 斜线 × 绿竖线 × 红竖线」围成的窄走廊里，四个正交方位都被压线 | 方位枚举器补齐 8 个方位 × 2 档间距共 16 个候选，并新增 `below_left` 命中；S06/S12 右移后走廊变宽 | 16 个标签全部落到合法方位，无 fallback |
| card v3 · visual | Q2 误判为「不存在满足约束的无障碍旅程」 | 另求无障碍路线时从 `range(E+1, …)` 开始枚举，漏掉了与最短普通路线**区间数相同**的那条合规路径 | 改为从 `range(E, …)` 起枚举，再按 (换乘次数, 路径字典序) 取最小 | Q2 正确给出 6 区间 / 2 换乘的合规最短路线 |
| card v3 · visual | 三张卡总高超出 720×1280 画布，页脚第二行被裁 | 卡高按估算式写死；末张卡后多算了一个 12px 间隔；页脚高度用常数 76/84/96 | 卡高逐张按内容实测行数计算并把剩余空间平均分配；循环末减去末张后的间隔；页脚高度改为 `12 + 实测行数×29 + 18` | 页脚完整可见，下边距 18px |
| card v4 · visual | 结论框内多留一行空白 | `est_lines` 把中文里的空格按 0.56em 计入，Q1/Q3 的说明被估成 3 行而实际渲染 2 行 | 精简说明文案（去掉站名两侧的排版空格、改用「→」连接），使估算与实际一致 | 三张卡均无多余空白 |
| map v5 · visual | 线路字母徽标随轨道 45° 旋转，字母不易读 | 徽标复用了线段的旋转矩阵 | 徽标改为正立放置（圆形徽标无需旋转） | R/B/G 三个字母始终正向 |
| map v6 · visual | 交叉点只有灰点，缺少「不是换乘」的就地说明 | 该约定只写在右侧面板里，图面上不易察觉 | 交叉点旁增加「交叉点·非换乘」说明条与一条 2px 引线；说明条矩形预先占位，站名标签排布时避让 | 图面即可读出该约定 |
| map v7 · visual | 面板加一条非地理声明后总高 1019px 超出面板底边 984px | 面板纵向堆叠仍按固定步长累加 | 删去面板内与页眉重复的声明、共享区段注释按实测 2 行分配（58→84px 预留）、条目间距 10→8 | 面板底 953px < 984px，文字与分隔线不再重叠 |

「渲染成功但视觉不符合要求」的问题同样记录在上面的完整视觉迭代中。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/run-20261011-01/A07/task-metrics.json`


| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始 / 结束时间 | 2026-10-11T15:05:00.000+08:00 / 2026-10-11T15:29:45.307+08:00 | ISO8601 带时区 | 计时记录（本地时钟，带时区） |
| 任务总耗时 | 1485.307 | 秒 | 墙钟时间（读题 → 计算 → 构造 → 渲染 → 看图 → 修复 → 报告） |
| 首次可用图耗时 | 9.845 | 秒 | 从开始到首个 `200 image/png` 且能打开的图为止的全部请求耗时之和；本任务请求串行，故与实际顺序一致 |
| 等待用户反馈 | 0.0 | 秒 | 本题为单轮任务，无多轮反馈等待 |
| 限流等待 | 0.0 | 秒 | 全程未出现 `429`（见 `requests.jsonl`） |
| 排队等待 | None | 秒 | 服务未提供排队指标，不可测量，记 null 而非 0 |
| 已记录请求耗时之和 | 120.002 | 秒 | `requests.jsonl` 中 `duration_seconds` 求和；请求串行，不与墙钟重复计入 |
| 成功 / 失败 / 重试请求 | 29 / 3 / 0 | 次 | `requests.jsonl`；失败均为不同 DSL 的语法修复，非同一请求重试 |
| 看图 / 完整视觉迭代 | 15 / 7 | 次 | `iterations.jsonl` 与实际图像查看记录 |
| DSL 版本数 | 13 | 个 | `requests.jsonl` 去重 |
| Server-Timing | null | — | 服务响应未返回该头，日志中如实记为 null |


## 6. 设计选择、经验与未解决事项


**关键设计选择**

1. *线路骨架是一次性手工验算的八向栅格*。16 条区段的端点坐标全部写在 `POS` 里，
   程序只校验「每段是 45° 或 90°」「同一条线上的相邻站确实按站序相连」「不出现非预期的线交叉」，
   校验结果写进 `routes.json.map_geometry`。这样 45°/90° 的角度要求是**可复核的硬约束**，
   而不是靠目测。全网只保留一处交叉（(970,380)，蓝线 S10–S11 × 绿线 S05–S16），
   正好用来演示「交叉 ≠ 换乘」的读图约定。
2. *换乘靠「深色外环 + 双线路字母」表达，交叉靠「灰点小圆」表达*。两者形状、颜色、是否有字母都不同，
   不会互相误读；站名标签右端再补一次线路字母，颜色与字母同时出现，不依赖红绿差异。
3. *无障碍判定严格按题面口径*：只约束起点、终点与换乘站，途经的非无障碍站允许通过。
   这一口径直接决定了 Q2 的结论——最短普通路线在东桥(S05)换乘，而东桥不具备无障碍设施，
   因此需另求合规最短路线；枚举时**必须从最少区间数 E 开始**，否则会漏掉
   「区间数相同但换乘站合规」的那条路径（本任务中正是这种情况）。
4. *两条查询共用区段时用单位法向量错开*。查询 2 与查询 3 都走绿线 S08–S15、S15–S05，
   直接叠加只会看到后画的那条。做法是按线段的单位法向量把两条细线各偏移 ±3.2px，
   轨道 15px 宽仍露出两侧的线路本色，两条查询的颜色都能看到。
5. *站名标签方位由程序求解*。16 个站各给出 16 个候选（8 个方位 × 2 档间距），
   逐个校验「不压轨道线段（沿线 3px 采样 + 外扩 7px）、不压站点圆点、不压已放标签、不出绘图区」，
   最终方位与标签矩形写入 JSON，可逐条复核是否压线。

**问题与修复（要点）**

- `Transform` 只能有一个子节点，「圆形底 + 文字」必须放进同一个 `Container` 并用 `alignment="CENTER"`。
- `Positioned` 必须是 `Stack` 的直接子节点；`Row` 内不能放 `Positioned`。
- 文字槽位宽度必须按**实际字宽**给足：20px 下 3 个字符的编号约需 44px、3 个汉字的站名约需 64px，
  给窄了会被静默裁掉（`S16 研究所` 曾变成 `S16 研究`）。
- `est_lines()` 把空格按 0.56em 计入，中文文案里为排版加的空格会让行数高估一行，
  导致卡片多出空白甚至溢出；应精简文案或按实测结果校正。

**可复用经验**

- 服务端错误信息里的 `position` 可以直接定位到出错片段，`Tag X only can have one child` 这类
  结构性错误按提示改结构即可，不必二分定位。
- 成功渲染的图片字节如果写到固定路径会被下一轮覆盖；应让渲染工具按 `request_id` 另存不可变副本。
  本题在发现覆盖后，已用 `responses/*.request.txt` 中保留的请求体把 11 个中间版本全部重新固化。
- 纵向堆叠的面板/卡片组，高度必须由**内容实测行数**逐项累加得到，并预留页脚与下边距。

**结束依据**：最终两图均已整屏打开查看，`network-map.png` 另做了中心区、右下区、左侧三处 2× 放大局部查看。
确认：16 个站名编号完整、3 个换乘站标记清晰、唯一交叉点无换乘标记、面板文字无重叠无裁切（底 953px < 984px）；
旅行卡三张卡片与页脚全部落在 1280px 内、结论与理由与 `routes.json` 逐字一致。
未以「渲染成功」作为完成依据。


### 未解决事项 / 限制


- 无影响交付的未解决问题。
- 「查询 2 与查询 3 共用绿线两段」在图上用两条 5px 细线并列（法向偏移 ±3.2px）表示，
  轨道 15px 宽因此两侧各只剩约 2px 的线路本色；已在面板中写明该约定，实际阅读无歧义。
- 示意图站距是示意性的，不代表真实地理；页眉已按题面要求明确标注为非地理示意图。
- 题目未规定线路走向，实际坐标由本程序选定并全部写入 `routes.json.map_geometry`；
  任何一组满足 45°/90° 的坐标都同样成立。
- 更严格的补充口径「全部途经站都须无障碍」也已计算并记录在
  `queries[].accessible.strict_all_stations_accessible`，三条查询在该口径下均不可行，属参考信息而非题面要求。


### 留痕确认

- 临时目录中的草稿 DSL、各次请求体副本、成功图片、失败响应 JSON、放大裁切图与预览全部保留，未删除或覆盖任何一次尝试；日志为追加写入。
- `tasks/` 下的输入文件、任务说明与模板均未被修改。
- 未保存任何密钥；`SNAPSHOT_API_KEY` 若存在只从环境变量读取，不写入 DSL 或日志。
- 总任务根 `.gitignore` 已创建（参考 `templates/gitignore-template.txt`），仅排除 `__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`、`.ipynb_checkpoints/`、`node_modules/.cache/` 等明确的运行时缓存；**未**使用 `tmp/`、`outputs/`、`cache/`、`.cache/`、`*.log` 或图片/DSL/JSON 通配规则，因此本任务的过程证据不会被忽略（共享规则详见 `_suite/snapshot-usage.md`）。
- `__pycache__/` 等运行时缓存不作为留痕材料，也不列为产物或自检证据。
