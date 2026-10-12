# A08 · 网格导览与两条可走路线 — 使用报告

- 任务：`tasks/A08-accessible-wayfinding/`，题目「网格导览与两条可走路线」
- 输出目录：`outputs/20261004-182918/A08/`
- 临时目录：`tmp/20261004-182918/A08/`
- 服务：`POST https://open-snapshot.muedsa.com/snapshot`（`snapkit.render` 带浏览器
  `User-Agent`，无凭据）
- 状态：**completed**

## 1. 交付物

| 文件 | 大小 | 说明 |
|---|---|---|
| `wayfinding.png` | 1560×1080，296 855 字节 | 服务真实响应的原始 PNG 字节，未做任何后处理 |
| `wayfinding.snapshot` | 221 062 字节 / 4 709 行 / 1 567 个 `Positioned` / 113 个 `Text` | 与 PNG 同名的完整 DSL |
| `paths.json` | 22 549 字节 | 全站格心序列、各段步数、距离、连通性校验 |
| `snapshot-usage.md` | 本文件 | 自检表 / 问题修复表 / 未解决事项 |
| `task-metrics.json` | — | 由 `finalize.build` 从 `requests.jsonl` / `iterations.jsonl` 生成 |

过程文件（草稿、裁切图、脚本、文档快照）留在 `tmp/20261004-182918/A08/`：
`build_a08.py`、`solve_probe.py`、`verify_a08.py`、`log_a08.py`、`txt.py`、`scan_links.py`、
`docs/`（ai-guide.md 与 snapshot.muedsa.com 的 4 份文档）、`crops/`（16 张放大核对图）、
`dsl-variants/wayfinding-v12-final.snapshot`、
`iterations.partial-first-wrapup-attempt.jsonl`。

## 2. 实际使用的文档与结论

| 来源 | 用到的结论 |
|---|---|
| `GET /ai-guide`（HTTP 200） | 请求体是 UTF-8 纯文本 DSL、响应体是图片字节；`400 PARSE_ERROR` 按消息定位修正；成功/失败都用 `X-Request-Id` 关联；不要用 `?errorImage=png` |
| `https://snapshot.muedsa.com/reference/parser-tags/`（HTTP 200） | 8 位 hex 按 `#RRGGBBAA` 读；`padding` 只接受 `"12"`/`"(8,16)"`/`"(8,12,16,20)"`；`Transform.matrix` 必须 16 个无空格 Float；`borderRadius` 与四角形式；`boxShadow` 自定义格式；渐变属性组；`Text` 的 `fontSize` / `fontFamily` / `textAlign` / `maxLines` 等；`Positioned` 必须是 `Stack` 直接子节点且每轴最多两项；`Stack fit="EXPAND"` |
| `https://snapshot.muedsa.com/guides/widgets/`、`/guides/painting/`、`/guides/media-text/`（均 HTTP 200） | `Positioned` 只支持 left/top/right/bottom/width/height；`Container` 装饰属性会与 `color` 合并；`Text` 段落属性只对最外层生效 |
| `_suite/DSL-HANDBOOK.md`（本题库实测结论） | 画布尺寸由布局决定；`BorderStyle` 只有 NONE/SOLID（本题未用虚线边框）；空 `Positioned` 会 400；`Text` 高度不足会静默丢字 → 必须逐条处理 `dsllib.warnings()`；用 `dsllib.dashed()` 拼虚线；折线用短矩形铺；`text_el` 的 y 是文本框顶边 |

字体：正文/标注一律 `Inter,Noto Sans CJK SC`（拉丁优先、缺字自动回退），
坐标标尺同族；没有臆造字体名，没有调用 `GET /fonts`（沿用 `_suite/fonts-list.txt`
里本题库已真实取得的清单，本题新增知识都实际查了上面的文档）。

标签能力实测：本题只用了 `Snapshot / Container / Stack / Positioned / Text`，
全部属性都在文档表格里；`BorderStyle` 未使用；没有 `DASHED`；没有 `Transform`
（因此不需要自己算旋转矩阵）。DSL 里 `<Image>` 出现 0 次（verify 脚本已断言）。

## 3. 路线推导（可复核）

输入 `inputs/floor.txt`：26 列 × 18 行，`#` 墙、`.` 可走，字母格同样可走；
每格 2 m；只准上下左右。`inputs/legend.json`：`S 入口 / E 出口 / A 材料实验 /
B 结构剧场 / C 光影工坊 / D 作品巡览 / cell_meters=2 / movement=4-neighbor`。

可走格 337 / 总格 468，墙 131。

| | 路线一 ① | 路线二 ② |
|---|---|---|
| 经过点 | S(2,2) → E(23,15) | S(2,2) → B(12,3) → D(12,13) → E(23,15) |
| 步数 | **34** | **36** = 13 + 10 + 13 |
| 距离 | **68 m** | **72 m** = 26 + 20 + 26 |
| 最短性证明 | 34 = \|23−2\|+\|15−2\| = 曼哈顿下界，任何 4 邻接走法都不可能更短，故可证最短 | 三段各自取 BFS 最短，总和即下界 |
| 过门洞 | 8,4 / 17,7 / 22,9 | 8,4 / 12,9 / 17,14 |

重合段 **13 步 / 26 m**，逐条列在 `paths.json` 的 `routes.shared_edges.edges`：
行 2 上 (2,2)→(7,2) 5 步 + x=7 上 (7,2)→(7,4) 2 步 + 行 4 上 (7,4)→(12,4) 5 步
+ (23,14)→(23,15) 1 步。

门洞（可走格且某一轴两侧都是墙，故天然只有 1 格 = 2 m 宽）共 **7 处**：
行 9 的 x = 3 / 12 / 22；列 8 的 y = 4 / 12；列 17 的 y = 7 / 14。

## 4. TASK.md 逐条自检

| TASK.md 要求 | 满足 | 证据 / 落点 |
|---|---|---|
| 1560×1080 导览 | ✅ | `wayfinding.png` 实测 1560×1080（verify 断言 PIL size） |
| 完整墙体与可走格 | ✅ | 468 格全覆盖：1 个白底 + 63 段横向合并墙块 + 27 条竖网格线 + 19 条横网格线；墙块按行做行程合并，未省略任何 `#` |
| 坐标边缘标尺 | ✅ | 顶部 x = 0…25、左侧 y = 0…17，共 44 个数字，另加轴名字母 `x` / `y` 两个，合计 46 个 `fontSize=16` 文本（verify 断言 16px 文字恰好 46 个） |
| 入口 / 出口 | ✅ | 绿圆 `S` 在格心 (2,2)、紫圆 `E` 在格心 (23,15)，各 36 px 白环 + 30 px 彩盘 + 22 px 字母；侧栏与图例同时标注坐标 |
| 四展区名称 | ✅ | A 材料实验 / B 结构剧场 / C 光影工坊 / D 作品巡览，四个名称都画在图上（圆角白底 + 展区色描边），侧栏另有一张带坐标的表 |
| 图例 | ✅ | 侧栏「图例」卡 8 条：墙体 / 可走地面 / 门洞 / 入口 / 出口 / ①实线+箭头 / ②虚线+箭头 / 重合段叠加 |
| 尺度 | ✅ | 底部左卡：0–10 m 五段黑白比例尺（每段 2 m = 1 格 = 40 px）、刻度 0/2/4/6/8/10 + 单位 m、「每格边长 2 m；图中 1 格 = 40 px」「米数 = 步数 × 2 m」 |
| 两条路线 | ✅ | ①蓝实线 34 段、②橙虚线 36 段，全部画在格心上（verify 逐段比对交付 DSL 的 Positioned 矩形） |
| 路线一 S→E 最短 | ✅ | 34 步 / 68 m，等于曼哈顿下界；图上与 paths.json 一致 |
| 路线二 S→B→D→E 最短且先 B 后 D | ✅ | 13+10+13 = 36 步 / 72 m；`connectivity_check.route_2_order_check` 记录 B 索引 13 < D 索引 23 |
| 画在格心 | ✅ | `x_px = 68 + x*40 + 20`，`y_px = 110 + y*40 + 20`；verify 用同一公式反查每一段 |
| 用线型和箭头区分 | ✅ | 实线 vs 连续相位虚线（16 px 实 / 11 px 空）+ 三角箭头；两线还各有 ①/② 圆形起始标记 |
| 重合段两条都能追踪 | ✅ | 重合段先铺蓝色实线、再叠橙色虚线，空隙露蓝；图例有「重合段 · 两线同格叠加」一条，底部说明「重合 13 步 · 26 m，两线同格心可追踪」；裁切图确认 |
| 不遮格号 | ✅ | 坐标数字全部在网格外侧的标尺带（x 标尺 y = GY−30、y 标尺 x = GX−48），路线与展区名全部落在网格内部，与标尺无交集 |
| 不把墙变成可走 | ✅ | 路线每一步的两个端点都经 verify 断言属于可走格集合；墙块是深色实心 + 网格线，路线不覆盖任何墙块 |
| 绕行与门洞清楚 | ✅ | 7 个门洞格用琥珀填充 + 3 px 琥珀描边 + 左上角 11 px 角标（格心留空，不挡路线）；侧栏「门洞 7 处 · 各宽 1 格 = 2 m」列出全部坐标；底部列出两条路线各自过的门洞 |
| 绕行不扩大门洞 | ✅ | 门洞格只染那 1 格（40×40 px），描边内缩 1 px，未向相邻格扩展；`paths.json.doorways` 记录 7 处各 `width_m = 2` |
| 留出侧栏说明 | ✅ | 右侧 408 px × 942 px 侧栏，5 张卡：图例 / 路线一 / 路线二 / 四个展区 / 门洞 |
| 路线一步数与米数 | ✅ | 侧栏「路线一」34 步 · 68 m；「路线二」三段 13/10/13 步 · 26/20/26 m + 合计 36 步 · 72 m；底部左卡再给一次 |
| 坐标以 (x,y) 表示、从 0 开始 | ✅ | 表头写明「坐标 (x,y) 均从 0 开始，x 为列号、y 为行号，原点在左上角」；侧栏与 paths.json 全部用 `[x, y]` 形式 |
| `paths.json` 全站格心序列 | ✅ | `cell_sequence`（网格坐标）+ `cell_centers_px`（像素格心）双份；路线二另有三段各自的序列 |
| 各段步数、距离 | ✅ | `steps` / `meters`，路线二 `segments[]` 逐段给出，含 `passes_doorways` |
| 连通性检查 | ✅ | `connectivity_check`：逐段断言可走格 + 4 邻接（`bad_steps` 为空）、`diagonal_steps_found = 0`、`wall_cells_entered = []`、B 先于 D、两条路线各自进入的门洞 |
| 路线多解时任选最短 | ✅ | BFS 邻居顺序固定为 右→左→下→上，结果确定可复现；已在 paths.json 写明算法 |
| 正文 ≥ 22 | ✅ | 除坐标标尺外全部文字为 22 / 24 / 30 px；verify 断言所有 fontSize ∈ {16} ∪ [22, ∞) |
| 网格标识 ≥ 16 | ✅ | 标尺数字 16 px |
| 额外文件 paths.json | ✅ | 见上 |
| snapshot-usage.md / task-metrics.json | ✅ | 本文件 / `finalize.build` 生成 |
| 过程日志在临时目录 | ✅ | `requests.jsonl`(20 条) / `iterations.jsonl`(12 条) / `docs/` / `crops/` / 脚本 |
| 最终 PNG 必须是服务真实响应且有同名 .snapshot | ✅ | PNG 是 `snapkit.render` 收到 `Content-Type: image/png` 后直接落盘的响应体，未解码未重编码；同名 DSL 同目录 |

## 5. 视觉迭代与问题修复

共 **14 次渲染请求**（全部 HTTP 200，0 失败、0 重试），**12 个可追溯的 DSL 版本**，
登记了 **12 次看图 / 9 次完整视觉迭代**（基线与两次纯脚本纠错不计完整视觉迭代）。
完整逐条记录见 `tmp/20261004-182918/A08/iterations.jsonl`。

| 版本 | 类型 | 看图发现 | 改动 | 结果 |
|---|---|---|---|---|
| v01 | baseline | 侧栏第 5 张卡底边 1074 超出 1052；画布底部“路径明细…”整行被裁；底部右卡文字互压；尺度条“10”与“m”重叠；门洞格“门”字被路线压住；5 条溢出告警 | — | 5 warnings |
| v02 | visual | 侧栏仍超 2px；2 条告警；门洞列表把 (17,7) 错分到“列 8”、(8,12) 错分到“列 17” | 表头 78→74、GY 116→110、底部卡 840/212、门洞改角标、箭头贪心避让、列宽调整 | 2 warnings |
| v03 | visual | 0 告警；错分组仍在 | 卡片标题区 46→42、图例行距 32→29、路线二数值列 136 | 0 warnings |
| v04 | correctness-fix + visual | (310,311)、(388,430) 出现游离三角——`tri()` 的 U/D 分支把垂直轴当水平轴用；说明文字“两线同经门洞 (12,9)”与数据矛盾 | 修 `tri()` 坐标轴；门洞按列分组；“过门洞”改为实算 | 箭头归位、文案与数据一致 |
| v05 | visual | x=23 竖列 610/650 两个箭头粘连；箭头只比 11px 线宽多 5px，像鼓包 | 箭头 8/11→11/13、step 3→4、gap 26→38、①② 移到 (4,1)/(6,1) | 箭头可辨 |
| v06 | visual | 底部右卡最后一行掉到卡外 y≈1060；图例箭头尖顶到 ①/② | 说明改 6 条单行 @27.5px；图例起点 14/44/58 | 回到卡内 |
| v07 | visual | 补齐轮后 42 个箭头，行 4 与 x=12 竖列呈锯齿，虚线读不出来 | 加补齐轮（每格都试） | 判定过密 |
| v08 | visual | 间距均匀了，但橙色箭头与同色虚线糊成“旗子” | 去补齐轮，改 3 轮交错贪心、keep-out 56px、每轮交换路线先后 | 26 个箭头 |
| v09 | visual | 放大 x=12 竖列确认橙色箭头仍与虚线粘连 | 非重合段箭头下垫白色同形 halo；重合段不加 | 箭头清晰、蓝线连续 |
| v10 | visual | 整图复查通过 | 图例与底部右卡按 v06 计划落位 | 0 warnings |
| v11 | correctness-fix | **眼睛看不出**；`verify_a08.py` 解析交付 DSL 后报 route_2 有 1 段未按格心画出。`dashed_path()` 没看行进方向，(12,4)→(12,3) 这个向上步的虚线画到低 40px 处，正好被马上折返的回程虚线盖住 | `dashed_path()` 增加 `sgn` | verify 仍报 1 段 |
| v12 | correctness-fix + visual | 负方向边的虚线盒子仍朝屏幕正方向伸展；裁切 (520,220)-(700,460) 放大 4 倍确认 | `sgn < 0` 时盒子起点再回退一个 step | verify 51 项全过；裁切确认橙色虚线正确向上进入 B |

### 服务错误

**未遇到。** 14 次渲染全部 `HTTP 200` + `Content-Type: image/png`，6 次文档请求全部
`HTTP 200`，没有 400/413/429/503，没有触发重试，也没有 `Retry-After`。
响应头里服务提供了 `Server-Timing`（例如 `render;dur=3297.8, total;dur=3627.6`），
已逐条记入 `requests.jsonl`；响应里没有 `X-Request-Id`，该字段记为 `null`。

真正踩到的坑都不是服务报错，而是自己实现的问题（`tri()` 轴混用、`dashed_path()`
忽略方向、门洞列表分组错误、文案与数据不一致），其中两个是肉眼发现不了、
靠 `verify_a08.py` 直接解析交付 DSL 才查出来的。

## 6. 独立校验脚本

`tmp/20261004-182918/A08/verify_a08.py` 不看生成脚本的中间变量，而是：
重新读 `inputs/floor.txt` / `inputs/legend.json` → 重新 BFS → 再用正则解析**交付的**
`wayfinding.snapshot` 里的 `Positioned` 矩形与颜色 → 逐段比对。最终 **51 项全部通过**，
包括：

- PNG 格式与 1560×1080
- 路线一 34 步 = 曼哈顿下界；路线二 36 步 = 三段 BFS 之和；B 先于 D
- 两条路线全程只落在可走格、每步都是 4 邻接、无对角
- 交付 DSL 里 34 段蓝实线 + 36 段橙虚线逐段位于格心；橙虚线的相位与从起点累计的
  连续 16/11 相位一致（按行进方向换算）
- 全部 fontSize ∈ {16} ∪ [22, ∞)，`<Image>` 出现 0 次
- `paths.json` 的格心序列、步数、距离、门洞、重合边与重算结果完全一致

## 7. 未解决事项（如实记录）

1. **路线二在 x=12、y 250–290 一带的虚线略密。** 路线二先走到 B(12,3) 再折回
   (12,4)，两个不同相位的虚线落在同一像素带上叠加。这是路线本身折返造成的，不是画错；
   `paths.json` 与本报告都写明了，verify 脚本对该带单独放行并在输出里打印了说明。
2. **重合段上只有路线一（蓝）的箭头。** 格距 40 px、箭头 keep-out 56 px 的条件下，
   同一条格边只能放一个箭头，先放的路线占位（先轮换两条路线的先后顺序已经让非重合段
   两色都有）。两条线本身靠“蓝色实线 + 橙色虚线在同一格心叠加”来区分，图例与底部
   说明都写明了这一点。线本身没有断开，两条都能追踪。
3. **留痕不足：14 次渲染请求 vs 12 个可追溯 DSL 版本。** 早期生成脚本没有为每次渲染
   保存带编号的 DSL 副本（同名文件被覆盖），有 2 次渲染请求无法与具体 DSL 版本一一
   对应。这是本任务的过程记录缺陷，未作推测性补写。v12 的最终 DSL 已另存为
   `tmp/20261004-182918/A08/dsl-variants/wayfinding-v12-final.snapshot`。
4. **`iterations.jsonl` 里有一段重复。** 第一次调用 `wrapup.wrapup()` 时参数元组长度写错，
   脚本在写完前 11 条后抛异常，留下了半截记录；已把该半截另存为
   `iterations.partial-first-wrapup-attempt.jsonl`，`iterations.jsonl` 只保留完整的那 12 条。
5. **平台计量全部为 null。** 服务没有 token / 图像输入 / 费用的计量接口，聊天平台也没有
   报告单次请求的 token 或费用，`task-metrics.json` 中这些字段一律 `null`，没有用字符数、
   请求体大小或耗时反推。
6. **排队等待不可测。** 响应头里没有排队段，`rate_limit_or_queue_wait_seconds` 记为
   `null`（而不是 0），因为无法确认整个过程确实没有发生过排队。
7. **题目文字与输入的一处不一致（按输入执行）。** TASK.md 写“`A/A/B/D` 四个展区”，
   但 `inputs/floor.txt` 里是 A / B / C / D 四格，`inputs/legend.json` 也给了 C = 光影工坊。
   本图按输入画 A、B、C、D 四个展区；若只画 A、B、D 会漏掉 floor.txt 里真实存在的 C 格。

## 8. 消耗

- 渲染请求 14 次（成功 14 / 失败 0 / 重试 0），文档请求 6 次
- 请求耗时合计 63.11 s；任务墙钟 2 805 s（约 46.8 min），首次可用图 20.8 s
- token / 图像输入 / 费用：平台未提供，`null`