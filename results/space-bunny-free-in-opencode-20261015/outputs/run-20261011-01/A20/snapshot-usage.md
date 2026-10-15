# Snapshot 使用情况说明与踩坑记录

任务ID：A20
任务名称：二十四密集点的无重叠标注
本次运行ID：run-20261011-01
完成状态：完成
结束原因：需求满足并完成逐图视觉自检
输出目录：`outputs/run-20261011-01/A20/`（路径基准：suite_root）
临时目录：`tmp/run-20261011-01/A20/`（路径基准：suite_root）
路径基准：suite_root；除本报告的 Markdown 本地链接（相对本文件所在目录）外，
所有记录中的本地路径均为相对 suite_root 的相对路径，未写死机器盘符或用户目录。

遵循 [PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录环境变量。
Markdown 本地链接相对当前文档；本报告位于 `outputs/<run_id>/A20/`，
故指向题库文档的链接为 `../../../tasks/…`。

## 1. 最终产物与需求完成情况


| 文件 | 用途 | 对应 DSL 或图 | 完成状态 |
|---|---|---|---|
| `annotated-map.snapshot` | 地图与引导标注定稿 DSL | `annotated-map.png` | 已完成 |
| `annotated-map.png` | 服务返回的最终图 1600×1100 | 同名 `.snapshot` | 已完成 |
| `label-layout.json` | 24 个标签的逻辑坐标、未舍入像素锚点、标签盒与引导折线 | — | 已完成 |
| `layout-audit.json` | 距离、圆盘覆盖、引导线检查、交叉数、边界与查看证据 | — | 已完成 |
| `snapshot-usage.md` / `task-metrics.json` | 报告与指标 | — | 已完成 |

需求逐项核对（依据**实际打开查看**：首版整屏、v2 整屏、中心 6 点 4× 放大、
6 点引导线 2× 放大、M12/M14 破平处 2× 放大、左侧标签列原尺寸）

| 题目要求 | 满足情况 | 证据 |
|---|---|---|
| 制作 1600×1100 示意地图 | 满足 | 服务 `image_info` 为 PNG 1600×1100 |
| inputs/markers.json 给 24 个点 | 满足 | 24 个 ID M01–M24 全部落在主图内并各有标签 |
| x/y 为 0–100 逻辑坐标，原点左下，x 右 y 上 | 满足 | `label-layout.json.coordinate_system.logical`；轴标题写明「左下原点 0,0」 |
| 主图区固定左上 (280,160)，宽 1040、高 760 | 满足 | `bounds.map_rect_fixed` = [280,160,1320,920] |
| 映射到像素时不要反转错误 | 满足 | 映射 `px=(280+10.4x, 920−7.6y)`；x=0→280、x=100→1320、y=100→160、y=0→920；逻辑 y 向上而像素 y 向下，故取负系数 |
| 点圆直径 12 | 满足 | 24 个圆盘均为 `width=12 height=12`；`point_diameter_px` = 12 |
| 严格按位置映射 | 满足 | 锚点为未舍入浮点，如 M10 = (831.2, 532.4)；几何审计全部在浮点上进行 |
| 地图本体不含真实地理 | 满足 | 只有规整网格与刻度，无地形、道路或地名边界 |
| 每点显示编号、name、value | 满足 | 标签文本为「M10 广场 93」形式，24 个全覆盖 |
| 可在主图内或左右外侧排标签，不移动锚点 | 满足 | 标签分列主图左侧 15 个、右侧 9 个；锚点全部由映射决定，未做任何偏移 |
| 密集中心点不能相互遮挡 | 满足 | 最近两圆心距 30.86px > 12px；放大后 6 点清晰分离 |
| 允许缩小该处点至 8px 并在审计记录 | 满足且未使用 | `point_diameter_note.shrunk_to_8px = []`，并写明「无需缩小」及依据（30.86 > 12） |
| 不能删点 | 满足 | 24 个点全部绘制并各有标签 |
| 所有标签正文 ≥20 | 满足 | `font_size_px` = 20；轴刻度与标题同为 20 |
| 标签盒间距 ≥4px | 满足 | `label_to_label_min_px` = 7.00 ≥ 4；阈值 4 |
| 与任何非本点主体不得覆盖 | 满足 | `point_overlaps.violation_count` = 0（24 标签 × 23 非本点圆盘全检） |
| 离点 >24px 的标签必须用引导线连回 | 满足 | 24 个标签到盒最短距离均 >24px，24 条引导线全部存在 |
| 线不穿过标签文本 | 满足 | `leader_checks.pierces_other_label` 为空（逐段 Liang-Barsky 测试） |
| 不得连接错点 | 满足 | 每条折线终点即本点圆周顶点，记录在 `leader_endpoint_on_circle` |
| 允许至多 3 处线与线交叉 | 满足 | `crossing_count` = 0 |
| 交叉不画连接点 | 满足 | DSL 中没有任何连接点图元；`no_connection_dots_drawn_at_crossings` = true |
| 用弯折、分侧排序和层级减少歧义 | 满足 | 全部折线为「水平—竖直—水平」弯折；左右分侧 + 按 y 排序消歧；最高 3 点用橙色外圈 + 橙框橙字做层级 |
| 标注坐标轴 | 满足 | x/y 两轴标题 + 每 20 一个刻度线 |
| 标注范围 | 满足 | 轴标题写「0–100」，并在两轴端点标 0 与 100 |
| 标注单位「指数」 | 满足 | 图内写明「value 单位：指数（逻辑范围 0–100）」 |
| 标注 value 最高 3 个点 | 满足 | M10 93 / M08 91 / M23 90，按 value 降序、同值按 ID 升序；三者在图上有橙圈 + 橙框橙字 + 文字说明 |
| 主图完整，不把 24 标签另做列表替代 | 满足 | 24 个标签都在图上各自连回其点；最高 3 点的文字说明只是补充，不替代任何标签 |
| `label-layout.json` 含原逻辑坐标、像素锚点、标签盒与折线 | 满足 | 每条含 `logical`、`anchor_px_unrounded`、`label_box`、`leader_polyline` |
| `layout-audit.json` 含标签交集、线穿标签、交叉数、边界检查 | 满足 | `distances`、`point_overlaps`、`leader_checks`、`bounds` 四段齐备 |
| 放大查看指定中心 6 点及引导线，再看整体 | 满足 | `highlights.visual_reviews` 6 条，含中心 6 点 4× 放大与其引导线 2× 放大 |
| 审计可用程序辅助 | 满足 | `verify()` 用段级求交、Liang-Barsky 与 Liang 裁剪参数化判定，1e-6 容差，保存未舍入坐标 |
| 所有指定最终 PNG 是服务真实响应且有同名 `.snapshot` | 满足 | 交付 PNG 由服务端返回，DSL 与服务实际接收的同一份 |



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

| https://snapshot.muedsa.com/reference/parser-tags/ · Text | fontSize/textAlign/text 的盒模型 | 标签正文 20px，轴刻度与标题同样 20px；文字盒宽度按 A14 实测字宽系数估算后统一取最大值 |
| https://snapshot.muedsa.com/reference/parser-tags/ · Container | border 与 borderRadius | 圆点用 ClipOval 实心 12px；最高 3 点的外圈用 ClipOval + `color="#FFFFFF00"` + border 实现空心环 |
| https://snapshot.muedsa.com/reference/parser-tags/ · Positioned | 须为 Stack 的直接子节点 | 所有图元统一 Positioned → Container/ClipOval/Text，避免 A18 踩过的 400 |


本次实际用到的能力：布局：`Container`/`Column`/`Row`/`Expanded`/`SizedBox`/`Padding`；精确定位：`Stack(fit=EXPAND)` + `Positioned`；文本：`Text` 的 `fontFamily`/`fontSize`/`textAlign`/`height`/`maxLines`/`letterSpacing`；颜色与透明度：CSS 颜色与 `#RRGGBBAA` 独立 alpha；装饰：`border`（宽度+样式+颜色）、`borderRadius` 与四角圆角、`boxShadow`；裁剪：`ClipRRect`/`ClipOval`；变换：`Transform` 的列主序 4×4 矩阵 + `alignment`；滤镜：`ImageFiltered`（子树模糊）、`BackdropFilter`（仅背景模糊）；渐变：`gradientType=LINEAR/RADIAL/SWEEP` + `gradientColors`/`gradientStops`。解析器未提供 `ClipPath`/多边形，所有图形均由矩形、圆角矩形、椭圆与渐变拼装。
本题额外用到：**引导线交叉可以做到构造性为零，而不是靠人工调线**。所有左侧引导线都是「水平—竖直—水平」正交折线，且按标签 y 升序排序后令竖直段 x 递增（g_i = 172 + 3i）。在此结构下两条折线相交当且仅当存在 i<j 使 py_i 落入 [y_label_j, py_j]；贪心排布保证 y_label_i > py_i − 40 且 y_label_{i+1} ≥ y_label_i + 44，于是 py_i < y_label_j 恒成立 ⇒ 左侧零交叉。右侧为镜像。左右两侧的 x 区间互不相交 ⇒ 跨侧零交叉。
**M12(48,45) 与 M14(26,45) 像素 y 同为 578**，是全场唯一同 y 点对。两条折线若都把末段放在 y=578，就会出现正长度共线重合（题面明令禁止）。解法是两件事配合：① 同 py 时按 px **升序**破平，M14(px=550.4) 拿到更小的竖直段 x、M12(px=779.2) 拿到更大的；② M14 的末段改走圆盘**上顶点**(px, py−6)，与 M12 的 y=578 平行而不重合。构建脚本对这一对还加了名次断言，防止以后改动破坏破平顺序。
**坐标轴文字也纳入程序化检查**。首版把 0–100 每 20 都标上数字，结果 M03(304.4)、M15(623.6)、M24(752.8) 三条引导线的水平末段正好落在「80」「40」「20」三个刻度上，把数字切断了。改为只在两端标 0/100（这两个 y 上没有任何引导线），范围写进轴标题；同时把 6 个轴文字盒加入几何断言，以后再出现「线穿轴文字」会直接抛错。

字体：实际查询 `GET /fonts` 得到 27 个字体族，原始响应留存于
`tmp/run-20261011-01/A20/responses/`（request_type=fonts），另有整理副本 `outputs/run-20261011-01/A20/../_suite/fonts-list.txt`。
中文正文使用 `Noto Sans CJK SC`，数字/拉丁使用 `Inter` 系列，代码/等宽使用 `Noto Sans Mono CJK SC`。
题目素材政策为纯 DSL，未使用任何外部图片（`<Image>` 标签本次未使用）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/run-20261011-01/A20/requests.jsonl`
迭代记录文件：`tmp/run-20261011-01/A20/iterations.jsonl`
响应与草稿留痕：`tmp/run-20261011-01/A20/responses/`、`tmp/run-20261011-01/A20/drafts/`

渲染请求总数：4
成功次数：3
失败次数：1
重试请求数：0（是总请求的子集）
DSL版本数：4
实际图片查看次数：6
完整视觉迭代数：5
未完成视觉迭代数：0
其他接口查询：字体查询与文档读取为 run 级共享准备；本题请求全部是渲染请求（首渲 1 次空响应 + 2 个版本各 1 次成功 + 交付 1 次）。裁切与放大观察由本地 Pillow 完成，不是服务渲染。

初次生成和查看计为基线，不计为改进迭代。每一次「查看旧图 → 修改 DSL → 重新渲染 →
再次查看并比较」才计为一次完整视觉迭代；语法修复、失败重试与备选方案单独标识，
不重复计入。所有图片均已用图像工具实际打开查看（含整屏与放大局部）。

| 请求ID | 输入 DSL | 耗时 | HTTP / Content-Type | 响应文件 | 查看与实际结果 |
|---|---|---|---|---|---|
| A20-v1-24057d89 | drafts/a20-annotated-map-v1.snapshot | 353.2s | 200 空响应体 | responses/A20-v1-24057d89.error.png | 无图；传输层空响应，保留证据 |
| A20-v1r1-cd448455 | drafts/a20-annotated-map-v1.snapshot | 4.89s | 200 image/png | preview/annotated-map-v1.png | 首版；发现轴标题与刻度数字重叠、引导线横穿刻度数字 |
| A20-v2r1-* | drafts/a20-annotated-map-v2.snapshot | 见 metrics | 200 image/png | preview/annotated-map-v2.png | 改为两端标 0/100 并加入轴文字检查后重渲；逐张放大复查通过 |
| A20-final-* | outputs/run-20261011-01/A20/annotated-map.snapshot | 见 metrics | 200 image/png | outputs/run-20261011-01/A20/annotated-map.png | 定稿渲染并整屏复查 |

## 4. 修改记录与踩坑

| 版本 / 类型 | 观察到的实际问题 | 原因及确认依据 | 实际修改 | 复验结果 |
|---|---|---|---|---|
| layout · tie-break | M12(48,45) 与 M14(26,45) 像素 y 同为 578，两条引导线末段会落在同一条水平线上，产生正长度共线重合 | 两侧都按 y=py 的中心线引入，两条水平末段互相覆盖 | ① 同 py 时按 px 升序破平，M14 拿到更小的竖直段 x；② M14 的末段改走圆盘上顶点 (px, py−6)，与 M12 的 y=578 平行而不重合；③ 对这一对的名次顺序加断言 | 共线重合 0、该对折线零交叉；放大后两条末段相隔 6px 清晰可分 |
| layout · crossing | 首次生成时仍有 1 处交叉：M14 的竖直段 (x=202) 横穿 M12 的水平末段 (y=578) | 破平用了 px **降序**，导致 px 大的 M12 拿到更小的 g、竖直段反而在内侧 | 把破平改成 px **升序**，让 px 小的 M14 拿内层竖直段 | 交叉总数从 1 降到 0（限值 3） |
| visual · axes | x 轴标题「逻辑坐标 x（左下原点 0,0）→」与刻度数字 0/20/40 重叠；y 轴刻度数字 80/40/20 被 M03/M15/M24 的引导线横穿 | 每 20 都写数字，且轴标题放在刻度同一行高度上 | ① 只在两端标 0 与 100（这两个 y 上没有任何引导线经过），范围写进轴标题；② 轴标题下移 40px；③ 把 6 个轴文字盒加入几何断言 | 整屏复查不再有轴文字重叠或被线穿过；以后同类问题会直接抛错而不是靠看图发现 |
| render · retry | 首渲收到 HTTP 200 但响应体 0 字节（353.2s） | 服务端传输层故障，与 DSL 无关 | 同一份 DSL 直接重发 | 4.89s 内成功；空响应体保留在 responses/ 下作为证据 |

「渲染成功但视觉不符合要求」的问题同样记录在上面的完整视觉迭代中。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/run-20261011-01/A20/task-metrics.json`


| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始 / 结束时间 | 2026-10-12T12:32:42.352000+08:00 / 2026-10-12T12:43:07.168+08:00 | ISO8601 带时区 | 计时记录（本地时钟，带时区） |
| 任务总耗时 | 624.816 | 秒 | 墙钟时间（读题 → 计算 → 构造 → 渲染 → 看图 → 修复 → 报告） |
| 首次可用图耗时 | 353.189 | 秒 | 从开始到首个 `200 image/png` 且能打开的图为止的全部请求耗时之和；本任务请求串行，故与实际顺序一致 |
| 等待用户反馈 | 0.0 | 秒 | 本题为单轮任务，无多轮反馈等待 |
| 限流等待 | 0.0 | 秒 | 全程未出现 `429`（见 `requests.jsonl`） |
| 排队等待 | None | 秒 | 服务未提供排队指标，不可测量，记 null 而非 0 |
| 已记录请求耗时之和 | 363.824 | 秒 | `requests.jsonl` 中 `duration_seconds` 求和；请求串行，不与墙钟重复计入 |
| 成功 / 失败 / 重试请求 | 3 / 1 / 0 | 次 | `requests.jsonl`；失败均为不同 DSL 的语法修复，非同一请求重试 |
| 看图 / 完整视觉迭代 | 6 / 5 | 次 | `iterations.jsonl` 与实际图像查看记录 |
| DSL 版本数 | 4 | 个 | `requests.jsonl` 去重 |
| Server-Timing | null | — | 服务响应未返回该头，日志中如实记为 null |


## 6. 设计选择、经验与未解决事项


**关键设计选择**

1. *把「交叉 ≤3」直接做到 0，并且靠构造而不是靠试*。
   所有左侧引导线统一走「水平—竖直—水平」的正交折线，并按标签 y 升序让竖直段 x 递增。
   在这个结构里两条折线相交当且仅当 `py_i` 落进 `[y_label_j, py_j]`；
   而贪心排布保证「标签不高于锚点 40px 以上、标签间距 ≥44px」，
   于是 `py_i < y_label_j` 恒成立，左侧零交叉。右侧镜像，左右 x 区间不相交 ⇒ 跨侧零交叉。
   这不是「调线调出来的」，而是布局规则本身排除的；程序里的段级求交只是复核。

2. *M12/M14 同 y 是全场唯一的结构性冲突，值得单独记*。
   两点逻辑 y 都是 45，像素 y 同为 578。若都把末段放在 y=578，就会出现**正长度共线重合**——
   题面明令禁止，而且比交叉更难处理（不能算成一个交点）。
   最终解法是两件事配合：同 py 时按 px 升序破平（让 M14 的竖直段在内侧），
   再让 M14 的末段改走圆盘**上顶点** `(px, py−6)`，与 M12 的 y=578 平行而不重合。
   并对这一对的名次顺序加了断言，避免以后改动悄悄破坏破平。

3. *「不需要缩小点」也要有依据*。题面允许把密集中心的点缩到 8px，但实测最近两圆心距
   30.86px，远大于 12px 直径，任何两点都不相交。因此 24 个点全部保持 12px，
   并在 `point_diameter_note` 里写明 `shrunk_to_8px = []` 与判断依据——
   「允许」不等于「必须」，用了反而说明没有认真测。

4. *轴文字也纳入几何断言*。首版每 20 都标刻度数字，结果 M03、M15、M24 三条引导线的
   水平末段正好落在「80」「40」「20」上把数字切断。这在题面的审计清单里没有明写，
   但它是**真实存在的视觉缺陷**。修法是把 6 个轴文字盒也放进几何检查，
   以后同类问题直接抛错，不必再靠看图发现。改成只在两端标 0/100 也是因为
   这两个 y（160 与 920）上没有任何引导线经过。

**问题与修复（要点）**

- 破平方向一开始写反（用了 px 降序），结果 px 大的 M12 拿到内侧竖直段，
  M14 的竖直段反而横穿 M12 的水平末段——生成器立刻报出这 1 处交叉。
- 首渲收到一次 HTTP 200 + 空响应体（353s），是传输层故障，重发即成功。

**可复用经验**

- 引导线密集的图，正交折线 + 「间距 ≥ 垂直偏移量」的排布能把交叉结构性降到 0。
- 两个对象落在同一坐标维度上时，先想清楚末段高度要不要错开，
  否则很容易撞上「共线重合」这种比交叉更难判的违规。
- 允许缩小元素不等于必须缩小；先量出最小间距，再决定用不用。
- 坐标轴刻度、图例这类「次要文字」也要进几何检查，否则它们最容易被引导线压掉。

**结束依据**：
定稿 `annotated-map.png` 原尺寸整屏打开；另做中心 6 点 4× 放大、6 点引导线 2× 放大、
M12/M14 破平处 2× 放大、左侧标签列原尺寸共 4 处局部复查。
`layout-audit.json` 的标签间距、圆盘覆盖、穿标签、共线重合、交叉数、边界与轴文字七项检查全部通过。
未以「渲染成功」作为完成依据。


### 未解决事项 / 限制


- 无影响交付的未解决问题。
- **刻度数字只标两端 0 与 100**，中间 20/40/60/80 只有刻度线没有数字。
  原因是引导线的水平末段恰好落在若干 y 上，逐个标注会被线切断。
  完整范围 0–100 已写在两条轴标题里，信息没有丢失；若后续把引导线改成不落在刻度高度上，
  可以把 20/40/60/80 的数字补回来。
- **M14 的引导线终点改在圆盘上顶点**而不是正左方。这仍然满足「从所属圆周连到本标签盒边界」，
  但视觉上与其它折线的进线角度不同；`label-layout.json` 的
  `leader_note` 已逐条注明该点为何特殊。
- **锚点坐标是未舍入浮点**（例如 532.4000000000001）。这是题面「不先对映射坐标取整」的要求，
  JSON 里以未舍入值保存并在 `coordinate_system.note` 说明；审计计算全程用浮点。


### 留痕确认

- 临时目录中的草稿 DSL、各次请求体副本、成功图片、失败响应 JSON、放大裁切图与预览全部保留，未删除或覆盖任何一次尝试；日志为追加写入。
- `tasks/` 下的输入文件、任务说明与模板均未被修改。
- 未保存任何密钥；`SNAPSHOT_API_KEY` 若存在只从环境变量读取，不写入 DSL 或日志。
- 总任务根 `.gitignore` 已创建（参考 `templates/gitignore-template.txt`），仅排除 `__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`、`.ipynb_checkpoints/`、`node_modules/.cache/` 等明确的运行时缓存；**未**使用 `tmp/`、`outputs/`、`cache/`、`.cache/`、`*.log` 或图片/DSL/JSON 通配规则，因此本任务的过程证据不会被忽略（共享规则详见 `_suite/snapshot-usage.md`）。
- `__pycache__/` 等运行时缓存不作为留痕材料，也不列为产物或自检证据。
