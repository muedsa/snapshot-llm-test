# A08 使用说明与自检报告 · 26×18 网格展馆导览与两条可走路线

- 任务：`tasks/A08-accessible-wayfinding/TASK.md`（与 `task.json` 一致），执行约定见
  `tasks/A08-accessible-wayfinding/AGENTS.md` 与总根 `AGENTS.md`
- run_id：`20261008T1615Z-run01`；本题输出根 `outputs/20261008T1615Z-run01/A08/`，
  过程目录 `tmp/20261008T1615Z-run01/A08/`（路径基准 `path_base=suite_root`，均为相对总任务根的路径）
- 状态：**completed**。主体全部由 Snapshot DSL 构造，最终图为服务真实响应，配同名完整 `.snapshot`；
  独立像素自检 0 问题；未解决事项为空
- 服务：`POST https://open-snapshot.muedsa.com/snapshot`，`Content-Type: text/plain; charset=utf-8`
  （地址来自总 `run-config.json`，覆盖本题 `tasks/A08-accessible-wayfinding/run-config.json` 的原题默认值）

## 1. 交付清单

| 文件 | 字节 | 说明 |
|---|---|---|
| `outputs/…/A08/wayfinding.png` | 297,981 | 1560×1080 RGBA；sha256 前缀 `d9616065cccc2791`；字节与 `tmp/…/A08/requests/A08-v06-20261008T125750Z.response.bin` 及 `preview/v06.png` 完全一致，未做任何后处理 |
| `outputs/…/A08/wayfinding.snapshot` | 113,045 | 与图像对应的完整 DSL（112,273 字符，UTF-8）；sha256 前缀 `ca11df8c31785f2d`；重跑 `tmp/…/A08/generate_a08.py` 可逐字节复现；内容等于 `requests/A08-v06-20261008T125750Z.body.txt` 去掉 render.py 的三行请求前缀 |
| `outputs/…/A08/paths.json` | 79,492 | 两条路线的全站格心序列、每步边、各段步数/米数、连通性与检查；sha256 前缀 `c96195efaa5ea657` |
| `outputs/…/A08/snapshot-usage.md` | 本文件 | |
| `outputs/…/A08/task-metrics.json` | | 计时、请求/迭代与自检计数 |

过程留痕（保留全部失败与草稿，不清理、不覆盖）：
`tmp/…/A08/requests.jsonl`（8 行）、`tmp/…/A08/iterations.jsonl`（6 行）、
`tmp/…/A08/requests/`（6 个 DSL 版本的请求体、响应头、原始响应体；v02 首次连接重置无响应体；
v04 截断残体 286,720/293,507 字节 + `NOTE-v04-hung-request.json`；`NOTE-truncated-response.json`）、
`tmp/…/A08/preview/v01|v02|v03|v05|v06.png` 与 17 张局部放大图、
`plan_a08.py`/`plan.json`、`build_paths.py`、`generate_a08.py`、`check_a08.py`、
`fit-report.json`、`pixel-report.json`、`v01.snapshot`–`v06.snapshot`。

## 2. 需求逐条对照（依据实际图像与实测数据）

| TASK.md 要求 | 实际做法与证据 |
|---|---|
| 26 列 × 18 行虚构展馆，左上原点 | `plan.json.grid`：cols=26、rows=18；墙 131 格、可走 337 格，逐格来自 `inputs/floor.txt`；图像网格区 936×648px，格宽 36px |
| `#` 不可走、`.` 可走，S/E/A/B/D 同样可走 | 墙体填 `#070D1A`、地面填 `#182A4A`；6 个标记格按 `legend.json` 命名；`check_a08.py` 逐格取色：131/131 墙格暗、337/337 地面格亮 |
| 每格边长 2 米，只可上下左右跨格 | 尺度在标题、图例和里程表中三处写明；`paths.json.checks.all_steps_4_neighbor` 全为真（每步曼哈顿距离=1） |
| 完整墙体与可走格、坐标边缘标尺 | 上边 x=0…25、左边 y=0…17 的刻度标尺（16pt），标尺说明"坐标标尺：上方 x · 左侧 y"；像素自检：路线墨迹落入 4 条标尺带的像素数 = 0（`route_ink_in_gutter`） |
| 入口/出口、四展区名称、图例、尺度 | S 入口 `#34D399`、E 出口 `#F87171`、A/B/C/D 展区徽标 + `legend.json` 名称（材料实验/结构剧场/光影工坊/作品巡览）；图例区 936×234px 含 9 类色样与 2 类线型 |
| 路线一：S→E 最短 | BFS 最短 34 步 = 68 米（等 shortest path 数 406,980，任选一条，条件已记录在 `paths.json.route_1.equivalent_shortest_paths`） |
| 路线二：S→B→D→E 最短，先 B 后 D，各段最短路 | 分段 BFS：S→B 13 步、B→D 10 步、D→E 13 步，合计 36 步 = 72 米；`checks.b_before_d`、`route_2_legs_shortest=[13,10,13]`、`route_2_total_equals_legs` 为真 |
| 画在格心，用线型和箭头区分 | 路线一青色实线 5.5px + 每 5 步一个 11px 箭头（段长 62% 处）；路线二琥珀虚线（14px 实段/10px 空档，DSL 无原生虚线，由重复 `line()` 生成）；折点取格心坐标 `cell_centres_px` |
| 重合段两条都能追踪 | 14 条重合边按左边法向 ±7.5px 平移成两条平行细线；像素横截面复核 14/14 同时命中 `r1`、`r2` 两色（`shared_drawn_as_pair=14`、`shared_pair_failures=0`） |
| 不遮格号、不把墙变成可走；绕行与门洞清楚 | 6 个标记徽标固定在标尺带之外；偏移量 7.5px < 格宽 36px，双线不越格；`route_ink_on_wall` 为空；门洞 7 处（`connectivity.doorways`）加 `#2E2153` 底色与两侧紫色刻度，门洞尺寸未被放大 |
| 侧栏说明，不扩大门洞 | 右侧栏 x=1032 起、宽 496px，含路线说明与分段里程表（S→E 34 步/68 米、S→B 13、B→D 10、D→E 13、路线二合计 36 步/72 米）；网格几何与 `floor.txt` 完全一致，无任何格属性改动 |
| 步数与米数、坐标 (x,y) 从 0 起 | 里程表逐段给出步数与米数；说明文字明确"坐标 (x,y) 均从 0 起、每格边长 2 米"；`paths.json.grid.coordinates` 同义记录 |
| `paths.json`：全站格心序列、各段步数、距离、连通性检查 | `route_*` 含 `cells / cell_centres_px / sequence(step,cell,centre_px,floor,walkable) / step_edges`；`connectivity`：S 的 BFS 可达 337/337，不可达可走格 = []，`marker_distance_from_S` 齐全；`checks.validation_problems=[]` |
| 路线多解时任选一条满足条件的最短路线 | 已在 `route_1.equivalent_shortest_paths`、`segments[].equivalent_shortest_paths` 记录解数量，并注明不要求与作者选择同一条 |
| 正文 ≥ 22、网格标识 ≥ 16 | 交付 DSL 字号普查：正文 22pt（43 个 Text）、标题 32pt、6 个站点徽标 18pt、标尺刻度与徽标字母 16pt（47 个）——最小 16，正文最小 22 |
| 1560×1080 | 服务响应即 1560×1080 RGBA；`pixel-report.json.size=[1560,1080]` |

## 3. 文档与 DSL 能力的实际使用

文档为 shared 轮次已真实取得的缓存（`tmp/…/_suite/docs/`，12 个请求全部 200，
记录在 `tmp/…/_suite/requests.jsonl`，本题不重复计为新请求）：`ai-guide.md`、`openapi.yaml`、
`snapshot.muedsa.com/` 与 parser-tags / widgets / container / concepts / layout / painting /
media-text / rendering / parser 指南。据此实际使用与验证：

- **元素集合**：交付 DSL 标签普查 `{Snapshot:1, Stack:1, Container:544, Positioned:543, Transform:285, Text:97}`。
  全部图形都通过 `<Container>`（尺寸/背景/圆角/边框）+ `<Positioned>`（绝对定位）+
  `<Transform>`（`rotate` 用于斜向无关的箭头朝向、平移用于虚线段）实现；
  **没有 `<Line>`、`<Rectangle>` 这类标签**，也未使用 `Image` 嵌入或外部素材——本题主体 100% 为纯 DSL。
- **无原生虚线**：按文档确认 DSL 无 dashed stroke，虚线由生成器沿边法向逐步 emit 14px 实线段（每段一个 `<Container>`），
  因此路线二的 36 步产生了数百个 Positioned 元素；这是尺寸可控的代价，已在字节数与响应耗时上体现。
- **无 HTML 实体解码**：解析器不解码 `&lt;`，说明文字中的 `<`/`>` 一律用 `<![CDATA[…]]>` 包裹（`dslkit.esc()`），
  否则会被当作标签起始。
- **文本盒静默裁切**：任何 Text 盒都必须过预渲染门禁（`TextFit`，SLACK=0.96、PITCH=1.45）。
  本题新增的关键结论：**n 行文本盒高度是 `n × 1.45 × size`，字形在行盒内垂直居中**，
  因此"小标题 + 分隔线"的推进量与分隔线 y 坐标都必须用完整行盒高度，而不是名义墨迹高度
  `size + (n-1) × 1.45 × size`；用后者会让分隔线穿过 CJK 字形（v03 实测问题，v05 修正）。
  东亚"ambiguous width"字符（U+2190–24FF、U+25A0–25FF、≥U+2E80）按 1.02em 计费，
  箭头"→"与"·""≥"都会计宽。
- **字体**：`fontFamily="Inter,Noto Sans CJK SC"`，与指南列出的可用字体一致；未查询到新的字体族，
  故本题未发起 fonts 探测请求（不声称查过）。
- **请求实践**：`tmp/…/_suite/scripts/render.py` 以 curl 发送 UTF-8 纯文本体，保存原始响应字节、
  响应头与 `X-Request-Id`/`Server-Timing`/`X-Snapshot-Cache`/`x-ratelimit-*`。
  本题为该脚本补上 `--connect-timeout 25 --max-time 240`（v04 挂起暴露缺失），
  并修正 `error_summary` 被二进制读取分支覆盖的问题。

数据层：`plan_a08.py` 解析 `inputs/floor.txt` 并做 BFS；`build_paths.py` 生成 `paths.json`；
`generate_a08.py` 只读取 `plan.json` 输出 DSL；`check_a08.py` 只读交付 PNG 做像素反测。三者分离，
便于把"数据正确"与"画面对"分别证明。

## 4. 视觉迭代与自检结论

5 轮完整视觉迭代（`iterations.jsonl` 6 行：v01 基线 + v02/v03/v05/v06 视觉轮 + v04 传输重试轮）：

1. **v01 基线**（首次响应 7.375s，200，272,955B）：几何与数据正确，但侧栏正文超框
   （`PANEL_H` 断言 1217>1048）、图例文字 212–288px 超出 204px 框、尺度行两段横向重叠、门洞与普通地面区分不足。
2. **v02**：格宽 40→36px 让出侧栏；图例改 3×3；删除文件里残留的第二套旧面板绘制（重复面板）；
   门洞加底色与刻度；面板改两遍布局（先量高再画框）。首次 v02 请求遇 `curl (56) Send failure: Connection was reset`
   无响应体，第二次 200 但 Content-Length=42,718 截断，第三次成功（3 行日志如实保留）。
3. **v03**：尺度行改用 `fit.w()` 实际字宽顺序排布、标尺说明移到图例标题行右侧；
   面板推进仍用名义墨迹高度 → 小标题分隔线穿过字形；S/E 端点未钉在格心（徽标与线错位）；
   拐角两条相邻段各画箭头叠成对勾形 → 箭头移到段长 62% 处。
4. **v04（重试轮，不计视觉迭代）**：HTTP 200 + Content-Length=293,507 但只落盘 286,720 字节后停滞约 10 分钟，
   因 render.py 缺 `--max-time` 而挂起，后台任务被我终止；残体与 `NOTE-v04-hung-request.json` 保留，
   该 `requests.jsonl` 行由存活文件手工补记（`duration_seconds` 为 null，不伪造耗时）。改动并入 v05。
5. **v05**：折返段仍像一条线 → 让 DUP 边的相邻两条边继承同一偏移，往返段整体保持 ±OFF 双线，
   会聚点落在徽标下方；`check_a08.py` 首跑 0 问题。字号审计发现 20pt/15pt 低于下限。
6. **v06（交付版）**：三处 20pt 升为 22pt（来源行右移到 x=660..1528 腾出宽度）、徽标字母 15→16pt、
   里程表标题框 26→30px；整图与局部放大复核无重叠、无裁切。

**独立像素自检**（`check_a08.py` 直接读 `outputs/…/A08/wayfinding.png`，输出 `pixel-report.json`）：
尺寸 1560×1080；`problems: []`；131/131 墙格暗、337/337 地面格亮；
路线墨迹 `r1=5,853px`、`r2=4,340px`；14/14 重合步与 1/1 折返步均横截面命中两色双线；
`route_ink_on_wall` 空、`route_ink_in_gutter=0`、外框溢出 0、`edge_ring_diff=0`。
**生成器门禁**（`fit-report.json`）：41 个文本盒 0 违规、0 标签回退、`trace_checks` 空、
`side_panel_height=660.3`、`legend_bottom=1024.0`（均 < 1048 安全线）。
看图证据：5 次整图打开 + 17 次局部放大（v01×5、v02×5、v03×4、v05×1、v06×2），
均为 1:1 或 2× NEAREST 裁剪（早期误用 LANCZOS 曾把 22px 笔画放大成"删除线"假象，改用 NEAREST 后排除）。

**数据自检**：`paths.json.checks` 全真、`validation_problems=[]`；
`connectivity` 证明可走格 337/337 全部连通，门洞 7 处；
`comparison`：路线二比路线一多 2 步、重合格 16、重合边 14、重访格 `[12,4]`、折返边 `[((12,3),(12,4))]`。
`plan.json` 曾有一处真实数据缺陷：`backtrack` 用**有向**边统计，永远为空；
改为无向规范化（`[(min,max) …]` 计数 >1）后折返边正确浮出，两条路线的格序列与修复前逐格相同（不影响已交付图像）。

## 5. 统计与未解决事项

- 渲染请求 8 次：7 次 200（其中 1 次 Content-Length 截断不可用、1 次连接重置无响应体另计）→
  可用图像 5 张（v01、v02、v03、v05、v06）；DSL 版本 6 个（v01–v06）。
- 请求耗时之和 441.595s（7 条有 `duration_seconds` 的行；v04 被终止的记 null，不计入也不猜测）。
  其中两次异常占大头（68.454s 连接重置、319.344s 慢速截断）；正常渲染 5.765–20.844s，
  与 `Server-Timing: render;dur≈…` 一致。shared 的 12 次文档请求（28.078s）不计入本题。
- 完整视觉迭代 4 轮（v02→v03→v05→v06），基线 1 次，传输重试轮 1 次（v04，另计，未重复算入视觉迭代）。
- 整图打开 5 次、局部放大查看 17 次。
- 未解决事项：**无**。跨题遗留的改进已落地在 `tmp/…/_suite/scripts/render.py`
  （curl 传输超时 + Content-Length 截断拒绝 + `error_summary` 覆盖修正），供 A09–B06 直接受益。
- 诚实性说明：残体、失败响应头、被终止的请求与手工补记的日志行全部保留在 `tmp/…/A08/requests/`；
  未把错误 JSON 存成最终图片；最终 PNG 未经任何后处理；密钥只经 `SNAPSHOT_API_KEY` 环境变量与请求头传递，未写入任何文件。
