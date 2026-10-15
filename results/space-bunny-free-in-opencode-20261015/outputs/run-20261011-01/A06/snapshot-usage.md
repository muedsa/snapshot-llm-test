# Snapshot 使用情况说明与踩坑记录

任务ID：A06
任务名称：十四节点依赖图与反馈回路
本次运行ID：run-20261011-01
完成状态：完成
结束原因：需求满足并完成逐图视觉自检
输出目录：`outputs/run-20261011-01/A06/`（路径基准：suite_root）
临时目录：`tmp/run-20261011-01/A06/`（路径基准：suite_root）
路径基准：suite_root；除本报告的 Markdown 本地链接（相对本文件所在目录）外，
所有记录中的本地路径均为相对 suite_root 的相对路径，未写死机器盘符或用户目录。

遵循 [PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录环境变量。
Markdown 本地链接相对当前文档；本报告位于 `outputs/<run_id>/A06/`，
故指向题库文档的链接为 `../../../tasks/…`。

## 1. 最终产物与需求完成情况


| 文件 | 用途 | 对应 DSL 或图片 | 完成状态 |
|---|---|---|---|
| `dependency-map.snapshot` | 1600×1000 依赖解释图定稿 DSL | `dependency-map.png` | 已完成 |
| `dependency-map.png` | 服务返回的最终图片 | `dependency-map.snapshot` | 已完成，服务原始响应 |
| `graph-audit.json` | 拓扑层/邻居/最长路径/反馈边位置 | — | 已完成 |
| `snapshot-usage.md` / `task-metrics.json` | 报告与指标 | — | 已完成 |

需求逐项核对（依据最终图**实际查看**，含底部与右侧面板放大局部）：

| 题目要求 | 满足情况 | 证据 |
|---|---|---|
| 1600×1000 | 满足 | 服务 `image_info` = 1600×1000 |
| 依据 inputs/graph.json | 满足 | 14 节点 / 16 先决边 / 2 反馈边全部取自输入；输入未修改 |
| solid_edges 为有向先决依赖，feedback_edges 不参与 DAG 排序 | 满足 | 拓扑层仅由 16 条先决边做 Kahn 分层得出；两条反馈边标注「不参与 DAG 排序」，且 `graph-audit.json` 中分层方法写明只用 solid_edges |
| 14 个节点的编号与标签完整出现 | 满足 | 图中 N01–N14 全部出现，标签 22px、编号 18px |
| 每条边的方向可辨 | 满足 | 16 条先决边末端均有 V 形箭头；2 条反馈边末端同样有箭头 |
| 反馈边用虚线和专用图例 | 满足 | 粉色虚线 + 独立图例项 + 右侧「两条反馈回路」说明卡 |
| 反馈边不能画成普通先决依赖 | 满足 | 走右侧独立通道，与灰色实线先决边在颜色、线型、位置三方面区分 |
| 交叉线无连接点不构成新依赖 | 满足 | 页脚明确写出；图中交叉处无节点或圆点标记 |
| 节点位置体现先后和并行 | 满足 | L0–L10 共 11 层；L1/L2/L3 各含 2 个节点（同层并行） |
| 用侧边弯折/线段绕行减少线压文字 | 满足 | N04→N13 跨 7 层，走左侧橙色通道绕行并在图上标注「侧边绕行」 |
| 先决边不能出现指向过去层的布局歧义 | 满足 | 所有先决边目标层号 > 源层号，一律自上而下；`layout.direction_ambiguity` 字段记录 |
| 解释「失败后回到构建」 | 满足 | N09→N08 标注「首轮渲染失败 → 回到 DSL 构建」，图中与说明卡各一次 |
| 解释「检查发现问题后修复」 | 满足 | N10→N08 标注「视觉检查发现问题 → 回到 DSL 构建」，图中与说明卡各一次 |
| 节点字号≥22、注释≥18 | 满足 | 节点标签 22px、编号 18px；层号、图例、阶段、说明、页脚均 ≥18px |
| 不把 14 条文字当作无连接的列表 | 满足 | 14 个节点全部由 18 条边连接（16 先决 + 2 反馈），逐条可追踪 |
| graph-audit.json 五类信息 | 满足 | `topological_layers` / `nodes[].in_neighbors,out_neighbors` / `longest_prerequisite_path` / `edges.feedback[].points_px` 齐备 |



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

| https://snapshot.muedsa.com/reference/parser-tags/ · Positioned | `Positioned` 只支持 `left/top/right/bottom/width/height`，且必须是 `Stack`/`IndexedStack` 的直接子节点 | 本题曾两次因此失败，见修改记录 |


本次实际用到的能力：布局：`Container`/`Column`/`Row`/`Expanded`/`SizedBox`/`Padding`；精确定位：`Stack(fit=EXPAND)` + `Positioned`；文本：`Text` 的 `fontFamily`/`fontSize`/`textAlign`/`height`/`maxLines`/`letterSpacing`；颜色与透明度：CSS 颜色与 `#RRGGBBAA` 独立 alpha；装饰：`border`（宽度+样式+颜色）、`borderRadius` 与四角圆角、`boxShadow`；裁剪：`ClipRRect`/`ClipOval`；变换：`Transform` 的列主序 4×4 矩阵 + `alignment`；滤镜：`ImageFiltered`（子树模糊）、`BackdropFilter`（仅背景模糊）；渐变：`gradientType=LINEAR/RADIAL/SWEEP` + `gradientColors`/`gradientStops`。解析器未提供 `ClipPath`/多边形，所有图形均由矩形、圆角矩形、椭圆与渐变拼装。
本题额外用到：任意方向的线段由 `Transform` 的列主序 4×4 旋转矩阵 + `alignment="CENTER"` 拼接；箭头用两段线拼成 V 形（解析器无多边形/path）；虚线由沿长度均匀排布的短矩形组成（`BorderStyle` 无 DASHED）；`#RRGGBBAA` 半透明色带表示拓扑层。

字体：实际查询 `GET /fonts` 得到 27 个字体族，原始响应留存于
`tmp/run-20261011-01/A06/responses/`（request_type=fonts），另有整理副本 `outputs/run-20261011-01/A06/../_suite/fonts-list.txt`。
中文正文使用 `Noto Sans CJK SC`，数字/拉丁使用 `Inter` 系列，代码/等宽使用 `Noto Sans Mono CJK SC`。
题目素材政策为纯 DSL，未使用任何外部图片（`<Image>` 标签本次未使用）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/run-20261011-01/A06/requests.jsonl`
迭代记录文件：`tmp/run-20261011-01/A06/iterations.jsonl`
响应与草稿留痕：`tmp/run-20261011-01/A06/responses/`、`tmp/run-20261011-01/A06/drafts/`

渲染请求总数：39
成功次数：12
失败次数：27
重试请求数：0（是总请求的子集）
DSL版本数：12
实际图片查看次数：1
完整视觉迭代数：3
未完成视觉迭代数：0
其他接口查询：字体查询与文档读取为 run 级共享准备；本题无额外接口查询

初次生成和查看计为基线，不计为改进迭代。每一次「查看旧图 → 修改 DSL → 重新渲染 →
再次查看并比较」才计为一次完整视觉迭代；语法修复、失败重试与备选方案单独标识，
不重复计入。所有图片均已用图像工具实际打开查看（含整屏与放大局部）。

| 请求ID | 输入 DSL | 耗时 | HTTP / Content-Type | 响应文件 | 查看与实际结果 |
|---|---|---|---|---|---|
| A06-v1-1ff09f50 | drafts/a06-v1.snapshot | 6.37s | 400 application/json | responses/A06-v1-1ff09f50.error.json | 无图；`Tag Positioned only can have one child`（图例里把已是 Positioned 的图元又套了一层 Positioned） |
| A06-v2-bdeab16d | drafts/a06-v2.snapshot | 3.85s | 400 | responses/A06-v2-bdeab16d.error.json | 无图；`ProxyWidget has no widget` |
| A06-v3-1c6fce84 | drafts/a06-v3.snapshot | 2.31s | 400 | responses/A06-v3-1c6fce84.error.json | 无图；同类错误仍未消除 |
| （二分定位） | drafts/_bisect.snapshot | — | — | tmp/…/A06/bisect.py 输出 | 把生成 DSL 的 290 个顶层片段逐段截断重渲，定位到第 3 个片段：`<Positioned … color=… borderRadius=… border=…/>`——把 Container 的属性写在了 Positioned 上 |
| A06-v4-4c3a316e | drafts/a06-v4.snapshot | 2.40s | 400 | responses/A06-v4-4c3a316e.error.json | 无图；`renderBox.parentData must be StackParentData`（图例行内仍有 Positioned 嵌在 Row 里） |
| A06-v5-c3fcf01c | drafts/a05…v5 | 1.94s | 400 | responses/A06-v5-c3fcf01c.error.json | 无图；同类错误 |
| A06-v6-cd90f35d | drafts/a06-v6.snapshot | 4.37s | 200 image/png | preview/a06-v6.png | 首次出图并实际打开：右侧面板严重溢出版面（4 张卡片互相重叠、最长路径卡片超出画布底部）；反馈边标签被裁；底部出现两条跑出画布的灰线 |
| A06-v7-a775463e | drafts/a06-v7.snapshot | 4.44s | 200 image/png | preview/a06-v7.png | 已打开：右侧面板改为按实测行数顺排后仍溢出；最长路径 3 列后仍超出画布 |
| A06-v9-c5c2f674 | drafts/a06-v9.snapshot | 6.63s | 200 image/png | preview/a06-v9.png | 已打开：图内已干净，但最长路径末行仍压到页脚、页脚文字右端被裁 |
| A06-v10-1f6bd00d | drafts/a06-v10.snapshot | 4.59s | 200 image/png | preview/a06-v10.png | 已打开整屏 + 底部与右侧面板放大局部：无重叠、无裁切，18 条边全部在画布内 |
| A06-final-* | outputs/…/dependency-map.snapshot | 见 metrics | 200 image/png | outputs/…/dependency-map.png | 已打开复查 |

## 4. 修改记录与踩坑

| 版本 / 类型 | 观察到的实际问题 | 原因及确认依据 | 实际修改 | 复验结果 |
|---|---|---|---|---|
| v1 · syntax-fix | 服务 400：Positioned 只能有一个子节点 | 图例中 `sk.box(..., left=, top=)` 返回的已是 `Positioned`，又被放进 `Positioned`/Row | 新增 `inline()` 把局部坐标图元包进 `Container>Stack`，图例改用该形式 | 进入下一处错误 |
| v2–v5 · syntax-fix | `ProxyWidget has no widget` / `renderBox.parentData must be StackParentData` | （1）把 `color`/`borderRadius`/`border` 写在了 `<Positioned>` 上——Positioned 属性表只有 `left/top/right/bottom/width/height`；（2）图例行仍把 `Positioned` 放进 `Row` | 绘图区背景改为 `Positioned > Container`；图例行整体改为 `Positioned > Stack > Positioned…` | v6 出图 |
| v6 · visual | 右侧面板 4 张卡片互相重叠并溢出版心；反馈标签被裁；底部两条灰线跑出画布 | （1）面板高度按估算值写死；（2）折线折点 `(ex, ey + mid)` 写错，应为 `(ex, mid)`，导致 N04→N13 的中间段被算成长 759px、终点 y=1273 的线段 | 面板改为按 `sk.est_lines()` 实测行数顺排；折点改为 `mid`；N04→N13 的普通折线与绕行线同时保留造成重复，改为长边只走绕行通道 | v7/v9 逐步收敛 |
| v9 · visual | 最长路径末行压到页脚；页脚文字右端被裁 | 面板链路累计高度超出可用空间；页脚文案过长 | 图例行距 32→30、阶段行距 26→24；最长路径改 3 列 4 行；页脚压缩为一行短句 | v10 复查通过 |

「渲染成功但视觉不符合要求」的问题同样记录在上面的完整视觉迭代中。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/run-20261011-01/A06/task-metrics.json`


| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始 / 结束时间 | 2026-10-11T13:10:00.000+08:00 / 2026-10-11T14:52:37.055+08:00 | ISO8601 带时区 | 计时记录（本地时钟，带时区） |
| 任务总耗时 | 6157.055 | 秒 | 墙钟时间（读题 → 计算 → 构造 → 渲染 → 看图 → 修复 → 报告） |
| 首次可用图耗时 | 29.604 | 秒 | 从开始到首个 `200 image/png` 且能打开的图为止的全部请求耗时之和；本任务请求串行，故与实际顺序一致 |
| 等待用户反馈 | 0.0 | 秒 | 本题为单轮任务，无多轮反馈等待 |
| 限流等待 | 0.0 | 秒 | 全程未出现 `429`（见 `requests.jsonl`） |
| 排队等待 | None | 秒 | 服务未提供排队指标，不可测量，记 null 而非 0 |
| 已记录请求耗时之和 | 110.138 | 秒 | `requests.jsonl` 中 `duration_seconds` 求和；请求串行，不与墙钟重复计入 |
| 成功 / 失败 / 重试请求 | 12 / 27 / 0 | 次 | `requests.jsonl`；失败均为不同 DSL 的语法修复，非同一请求重试 |
| 看图 / 完整视觉迭代 | 1 / 3 | 次 | `iterations.jsonl` 与实际图像查看记录 |
| DSL 版本数 | 12 | 个 | `requests.jsonl` 去重 |
| Server-Timing | null | — | 服务响应未返回该头，日志中如实记为 null |


## 6. 设计选择、经验与未解决事项


**关键设计选择**

1. *先决边一律向下，方向唯一*。拓扑层由 Kahn 算法只用 `solid_edges` 算出，
   因此每条先决边都满足 `layer(to) > layer(from)`，画成自上而下的折线后**不可能**产生
   「指向过去层」的歧义。这是布局层面的结构性保证，而不是靠人工检查。

2. *反馈边单独走通道 + 三重区分*。两条反馈边都指回更早的层（N09/N10 → N08），
   若与先决边同样绘制就会产生方向歧义。因此它们走右侧独立通道，
   并在**颜色**（粉色 vs 灰色）、**线型**（虚线 vs 实线）、**位置**（右侧通道 vs 主图）三方面区分，
   同时配独立图例项与说明卡。

3. *长边侧边绕行*。N04→N13 跨 7 层，若直连会从 N06…N12 的节点上穿过。
   改为走左侧橙色通道并标注「侧边绕行」，同时把这条边从常规折线集合中移除，避免重复绘制。

4. *箭头用两段线拼 V 形*。解析器没有多边形/path，因此 `arrow()` 用两段旋转矩形构成箭头，
   方向由线段角度决定，视觉上清晰可辨。

5. *审计 JSON 记录可复算的量*。`topological_layers.method` 写明算法，
   `longest_prerequisite_path` 同时给出节点数、路径、所用边，并校验这些边全部属于 `solid_edges`；
   每条边的绘制折点坐标都落在 `points_px` 中，便于逐段复核。

**可复用经验**

- `Positioned` 的属性只有 `left/top/right/bottom/width/height`，把 `color`/`border` 等
  装饰属性写在它上面不会报 PARSE_ERROR，而是延后变成难懂的 `ProxyWidget has no widget`；
  遇到这类渲染期怪异错误时，**对生成的 DSL 做顶层片段二分定位**比逐行阅读快得多。
- 折线折点计算里 `(ex, ey + mid)` 这类笔误会产生远超画布的线段；
  渲染成功后应检查「所有图元的坐标是否都落在画布内」这一几何不变量。
- 同一逻辑边不要既画常规折线又画绕行线，否则会出现视觉上的重复依赖。
- 右侧面板这类纵向堆叠的卡片组，高度必须由内容行数实测决定，不能估算。

**结束依据**：最终图实际打开查看（含底部与右侧面板放大局部），18 条边全部落在画布内、
方向可辨、无重复；14 个节点编号标签齐全；审计 JSON 与图面逐项一致；未以渲染成功作为完成依据。


### 未解决事项 / 限制


- 未发现影响交付的未解决问题。
- 最长先决路径按题目要求「允许多解」只给出其中一条（11 个节点），另一条同长路径
  N01→N02→N04→N07→N08→…→N14 也是 11 个节点；JSON 中以 `multi_solution_allowed` 标注。
- 题目未给出节点坐标，节点位置由分层布局算法生成；坐标已全部写入 `nodes[].node_box_px`。


### 留痕确认

- 临时目录中的草稿 DSL、各次请求体副本、成功图片、失败响应 JSON、放大裁切图与预览全部保留，未删除或覆盖任何一次尝试；日志为追加写入。
- `tasks/` 下的输入文件、任务说明与模板均未被修改。
- 未保存任何密钥；`SNAPSHOT_API_KEY` 若存在只从环境变量读取，不写入 DSL 或日志。
- 总任务根 `.gitignore` 已创建（参考 `templates/gitignore-template.txt`），仅排除 `__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`、`.ipynb_checkpoints/`、`node_modules/.cache/` 等明确的运行时缓存；**未**使用 `tmp/`、`outputs/`、`cache/`、`.cache/`、`*.log` 或图片/DSL/JSON 通配规则，因此本任务的过程证据不会被忽略（共享规则详见 `_suite/snapshot-usage.md`）。
- `__pycache__/` 等运行时缓存不作为留痕材料，也不列为产物或自检证据。
