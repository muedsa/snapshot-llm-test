# Snapshot 使用情况说明与踩坑记录

任务ID：A01
任务名称：六个月经营诊断驾驶舱
本次运行ID：run-20261011-01
完成状态：完成
结束原因：需求满足并完成逐图视觉自检
输出目录：`outputs/run-20261011-01/A01/`（路径基准：suite_root）
临时目录：`tmp/run-20261011-01/A01/`（路径基准：suite_root）
路径基准：suite_root；除本报告的 Markdown 本地链接（相对本文件所在目录）外，
所有记录中的本地路径均为相对 suite_root 的相对路径，未写死机器盘符或用户目录。

遵循 [PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录环境变量。
Markdown 本地链接相对当前文档；本报告位于 `outputs/<run_id>/A01/`，
故指向题库文档的链接为 `../../../tasks/…`。

## 1. 最终产物与需求完成情况


| 文件 | 用途 | 对应 DSL 或图片 | 完成状态 |
|---|---|---|---|
| `operations.snapshot` | 完整可复现 DSL（定稿） | `operations.png` | 已完成，与最终图一致 |
| `operations.png` | 服务返回的最终图片，1600×1000 | `operations.snapshot` | 已完成，服务原始响应字节 |
| `computed-data.json` | 审计数据（每月值/汇总/轴定义/结论引用） | — | 已完成 |
| `snapshot-usage.md` | 本报告 | — | 已完成 |
| `task-metrics.json` | 结构化指标 | — | 已完成 |

需求逐项核对（依据最终图 `operations.png` 的实际查看，必要时放大局部）：

| 题目要求 | 满足情况 | 证据（图中位置 / 数值） |
|---|---|---|
| 1600×1000 | 满足 | 服务返回 `image_info` = 1600×1000 PNG |
| 四张 KPI：总净收入 / 总经营利润 / 总订单 / 期间总体转化率 | 满足 | 顶部四卡：918,624 元、262,124 元、3,045 笔、11.15% |
| KPI 保留金额原值或正确换算万元 | 满足 | 卡片同时给出原值与万元（91.86 万元 / 26.21 万元） |
| 六个月净收入与经营利润分组柱图 | 满足 | 左中卡片，6 组 2 序列，数值标签 11.97…20.24 / 3.77…6.44 |
| 柱图共用零起点与比例 | 满足 | 单一 Scale 实例驱动两序列，零线 y 同值，`axes[0].zero_line_y_px` 已记录 |
| 访问量与转化率两个共享月份对齐的小图 | 满足 | 右上（3,500…5,600）与右下（12.00%…11.07%），月份标签均为 2026-04…2026-09 且同序 |
| 百分比与金额不共用混淆数轴 | 满足 | 柱图纵轴为万元；转化率折线纵轴为比率 10.50%–12.00%，两者独立 |
| 六行明细表（月份/净收入/退款率/利润/转化率） | 满足 | 左下表 6 行 5 列，金额整数、比例两位小数，数字列右对齐 |
| 总体转化率＝总订单/总访问，不平均月比例 | 满足 | 11.15%（3,045÷27,300）；脚注同时列出月比例平均 11.19% 以示区别 |
| 退款率＝退款/退款前收入 | 满足 | 表内 5.00% / 8.00% / 4.00% 与逐月计算一致 |
| 有证据的管理结论 | 满足 | 右下五条，每条引用 computed-data.json `conclusion.items[].cited_values` |
| 负值正确处理 | 满足 | 本数据集利润均为正；`vbar_chart` 以零线为基、负值向下绘制并把标签放在柱底之下（代码支持，v1 探针中已验证） |
| 图表刻度、单位、图例、月份、表格完整可读 | 满足 | 三张图均有 y 轴刻度与单位标注；柱图图例在标题右侧且不重叠 |
| 正文≥20、脚注≥16 | 满足（见下说明） | 明细表 20px、结论正文 20px、卡片标题 20px、KPI 标签 19px、脚注 17px；图表刻度/类别标签为图表附属元素，取 14–17px。字号清单见 `computed-data.json` 的 `typography_inventory_px` |
| 视觉重点明确，不平均堆满数字 | 满足 | 深蓝净收入柱为主序列，利润为次色；09 月行加重底色；结论按「规模/症结/代价/结构/行动」分行配彩色标识 |
| 表格对齐、最后一个月标签、图表比例 | 满足 | 数字列严格右对齐；2026-09 列在柱图/两小图中均完整显示且未被裁切；柱高与数值成比例 |

说明：题目未提供负值数据，因此「负值正确处理」以构造器能力与实测探针（非本题交付图）佐证，
未在交付图中制造不存在的负值。



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

| https://open-snapshot.muedsa.com/ai-guide.md | `POST /snapshot` 请求体为 UTF-8 纯文本；成功返回图片二进制；错误为含 `code`/`message`/`requestId` 的 JSON；`GET /fonts` 返回 text/plain 字体族列表 | `tmp/…/_suite/scripts/snapshot_render.py` 的请求构造与响应分流 |
| https://snapshot.muedsa.com/reference/parser-tags/ | 38 个标签的属性表：`Container` 尺寸/颜色/边框/圆角/阴影/渐变、`Stack`+`Positioned` 定位、`Text` 文本属性、`Flex` 系列枚举、`ClipOval`/`ClipRRect` 裁剪、`Transform` 矩阵与 `alignment` | `snapkit.py` 全部构件函数；`operations.snapshot` |
| 同上 · 颜色与数值格式 | `#RRGGBBAA` 末位为 alpha；EdgeInsets 三种括号写法；`border` 为「宽度 样式 颜色」；`boxShadow` 自定义格式 | 卡片/图表配色与描边、阴影 |
| 同上 · 已知限制 | `Stack` 无 `width`/`height`；解析器未提供 `ClipPath`/多边形，图形须由 `Container`/`ClipOval`/`ClipRRect`/渐变拼装 | 柱图、折线、圆点、参考线全部由矩形与裁剪拼装 |


本次实际用到的能力：布局：`Container`/`Column`/`Row`/`Expanded`/`Flexible`/`SizedBox`/`Padding`；精确定位：`Stack(fit=EXPAND)` + `Positioned`（全部图表几何）；文本：`Text`（`fontSize`/`fontFamily`/`textAlign`/`height`/`maxLines`）；颜色与透明度：`#RRGGBBAA`、独立 alpha 面积填充；装饰：`border`、`borderRadius`/四角圆角、`boxShadow`；裁剪：`ClipOval`（圆点）、`ClipRRect`；变换：`Transform` 的列主序 4×4 矩阵 + `alignment=CENTER`（折线段旋转）；图片与网络图片：未使用（本题为纯 DSL，素材政策 dsl_only）。

字体：实际查询 `GET /fonts` 得到 27 个字体族，原始响应留存于
`tmp/run-20261011-01/A01/responses/`（request_type=fonts），另有整理副本 `outputs/run-20261011-01/A01/../_suite/fonts-list.txt`。
中文正文使用 `Noto Sans CJK SC`，数字/拉丁使用 `Inter` 系列，代码/等宽使用 `Noto Sans Mono CJK SC`。
题目素材政策为纯 DSL，未使用任何外部图片（`<Image>` 标签本次未使用）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/run-20261011-01/A01/requests.jsonl`
迭代记录文件：`tmp/run-20261011-01/A01/iterations.jsonl`
响应与草稿留痕：`tmp/run-20261011-01/A01/responses/`、`tmp/run-20261011-01/A01/drafts/`

渲染请求总数：10
成功次数：6
失败次数：4
重试请求数：0（是总请求的子集）
DSL版本数：6
实际图片查看次数：5
完整视觉迭代数：3
未完成视觉迭代数：1
其他接口查询：字体查询 `GET /fonts` 1 次（run_id 级共享准备，原始响应见 `tmp/run-20261011-01/_suite/responses/`）；AI 指南与 DSL 标签参考各读取 1 次（共享准备）；A01 范围内无其他接口查询

初次生成和查看计为基线，不计为改进迭代。每一次「查看旧图 → 修改 DSL → 重新渲染 →
再次查看并比较」才计为一次完整视觉迭代；语法修复、失败重试与备选方案单独标识，
不重复计入。所有图片均已用图像工具实际打开查看（含整屏与放大局部）。


| 请求ID | DSL 输入 | 起止与耗时 | HTTP / Content-Type | 响应文件 | 查看与实际结果 |
|---|---|---|---|---|---|
| A01-v1-3d4be87a | drafts/a01-v1.snapshot | 2026-10-11 09:2x，3.35s | 400 application/json | responses/A01-v1-3d4be87a.error.json | 未出图；`PARSE_ERROR: Tag Container only can have one child … Positioned`（面积填充把多个 Positioned 塞进 Container） |
| A01-v1-077e3ca7 | 同上（修正后） | 2.06s | 400 application/json | responses/A01-v1-077e3ca7.error.json | 未出图；同样的单子节点错误（表格） |
| A01-v1-2cbca453 | 同上（修正后） | 2.26s | 400 application/json | responses/A01-v1-2cbca453.error.json | 未出图；`RENDER_ERROR: CrossAxisAlignment.baseline 需同时指定 BaselineMode` |
| A01-v1-d43912aa | 同上（修正后） | 1.43s | 400 application/json | responses/A01-v1-d43912aa.error.json | 未出图；`crossAxisAlignment=BOTTOM` 不属于枚举 |
| A01-v1-cc5e1283 | 同上（v1 定稿） | 4.52s | 200 image/png | preview/a01-v1.png | 已打开：版式正确，但**每条文字重复渲染两次**（text 属性 + 子文本），柱值/月份/结论标签互相压盖 |
| A01-v2-c2ce1516 | drafts/a01-v2.snapshot | 3.45s | 200 image/png | preview/a01-v2.png | 已打开：重复消失；发现折线段飞出绘图区、柱图标题与图例重叠、正文字号偏小 |
| A01-v3-bd58c99e | drafts/a01-v3.snapshot | 4.01s | 200 image/png | preview/a01-v3.png | 已打开：折线正确；发现 KPI 数字压住说明文字、图例未右对齐、2026-08/09 月份标签重叠、参考线徽标压住折线、结论末字被裁 |
| A01-v4-f85cc1ef | drafts/a01-v4.snapshot | 4.60s | 200 image/png | preview/a01-v4.png | 已打开：仅剩图例仍停在左上角压住柱图标题 |
| A01-v5-278b1bb3 | drafts/a01-v5.snapshot | 3.24s | 200 image/png | preview/a01-v5.png | 已打开（整屏 + KPI 行与转化率图放大局部）：无重复、无重叠、无裁切，数值与 JSON 一致 |
| A01-final-43b2ae48 | outputs/…/A01/operations.snapshot | 4.73s | 200 image/png | outputs/…/A01/operations.png | 已打开复查，与 v5 一致，尺寸 1600×1000 |

（完整字段含时间戳、时区、请求文件、Server-Timing、requestId 见 `requests.jsonl`；上表耗时取自该日志）


## 4. 修改记录与踩坑


| 迭代 / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 修改 | 复验结果 | 相关文件 |
|---|---|---|---|---|---|
| v1 · baseline · — | 服务连续 4 次 400 | 错误 JSON 的 `message` 明确指出标签/属性非法 | ①面积填充与表格的多个 `Positioned` 从 `Container` 移入 `Stack`；②`BASELINE` 改 `END`（`BOTTOM` 非合法枚举） | v1 出图后暴露新的重复文字问题 | `responses/A01-v1-*.error.json` |
| v2 · 视觉迭代 · v1 | 全屏文字重复、KPI 与结论标签互相压盖 | `snapkit.text()` 同时输出 `text` 属性与子文本内容，两者都被绘制 | `text()` 只保留子文本内容 | v2 全屏查看：重复消失，数值与表格全部正确 | `drafts/a01-v2.snapshot` |
| v2 · 视觉迭代 · v1 | 折线段飞出图外、方向错乱 | `Transform` 未设 `alignment` 时绕子节点左上角旋转，且旋转角取了负号 | `rot_matrix` 角度改为 `+atan2(dy,dx)`，并加 `alignment="CENTER"` | v3 折线逐点正确连接 | `snapkit.py#rot_matrix` |
| v3 · 视觉迭代 · v2 | 正文/表格字号未达正文≥20；柱图标题与图例重叠 | 版面常量与图例定位方式 | 重排版面（KPI/中排/底排/页脚），字号提升；图例改为卡片内右对齐 | v3 字号达标，图例仍偏左 | `drafts/a01-v3.snapshot` |
| v3 · 视觉迭代 · v2 | KPI 数字与单位重叠 | `Text` 子文本会被 trim，`" 元"` 的前导空格被吃掉 | 单位间距改用 `<SizedBox width="8"/>` | v4 该问题消失 | `snapkit.py#kpi_card` |
| v3 · 视觉迭代 · v2 | 2026-08 与 2026-09 月份标签互相压盖 | 标签框宽度按槽位宽计算，`clamp_label` 把末位标签左推后压到前一个 | 标签框宽度取 `min(槽位宽, 文字实际宽度)` | v4 两标签分离 | `snapkit.py#vline_chart` |
| v3 · 视觉迭代 · v2 | 「总体均值 11.15%」徽标压住折线与 11.22% 数值标签 | 参考线徽标绘制在绘图区内、数据点上方 | 徽标移出绘图区，改写进卡片副标题 | v4 绘图区干净 | `build_a01.py` |
| v3 · 视觉迭代 · v2 | 结论第 5 条末字被卡片底边裁切 | 文案过长导致第三行溢出 | 精简该条文案（不删证据） | v4 全部五条完整可见 | `build_a01.py` |
| v4 · 视觉迭代 · v3 | 图例仍压在柱图标题上 | `hlegend` 未传 `total_w`，返回的 `Positioned` 嵌在外层 `Positioned` 内被钉在 (0,0) | 增加 `total_w` 右对齐模式，返回 `Row` | v5 图例位于卡片右上且不重叠 | `snapkit.py#hlegend` |
| v5 · 视觉迭代 · v4 | 需确认 KPI 说明文字下移后无重叠 | KPI 卡片改为自上而下显式排布 | 统一 `kpi_card` 内部 y 计算 | v5 整屏 + 放大局部复查通过 | `preview/a01-v5.png` |
| 共享准备 · 踩坑 · — | 首张 200×100 冒烟图两次 400 | PowerShell `Set-Content -Encoding UTF8` 与编辑工具都会写入 UTF-8 BOM，服务按 RAWTEXT 拒绝 | 渲染前统一剥离 BOM，并在 `requests.jsonl` 记录 `bom_stripped` | 第三次冒烟成功 | `_suite/scripts/snapshot_render.py` |
| 共享准备 · 探针 · — | 首版柱图整体塌陷 | 实测：`Stack` 标签没有 `width`/`height` 属性（文档属性表未列出），未知属性被忽略 | 统一改为 `SizedBox` 外包 + `Stack fit="EXPAND"` | 探针图确认几何正确 | `_suite/probe2.png` |


「渲染成功但视觉不符合要求」的问题同样记录在上面的完整视觉迭代中。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/run-20261011-01/A01/task-metrics.json`


| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始 / 结束时间 | 2026-10-11T09:12:04.310+08:00 / 2026-10-11T13:57:18.013+08:00 | ISO8601 带时区 | 计时记录（本地时钟） |
| 任务总耗时 | 17113.703 | 秒 | 墙钟时间，含读题、编写构造器、渲染与看图 |
| 首次可用图耗时 | 约 33.7 | 秒 | 从开始到首个 `200 image/png` 且能打开；本值为该题全部请求耗时之和的近似上界（请求串行，故与实际顺序一致） |
| 等待用户反馈 | 0.0 | 秒 | 本题为单轮任务，无多轮反馈等待 |
| 限流等待 | 0.0 | 秒 | 未出现 `429`，实际响应见 `requests.jsonl` |
| 排队等待 | null | 秒 | 服务未提供排队指标，不可测量；不臆测为 0 |
| 已记录请求耗时之和 | 33.653 | 秒 | `requests.jsonl` 内 10 次渲染请求的 `duration_seconds` 之和；串行执行，不与墙钟重叠重复计入 |
| 成功 / 失败 / 重试请求 | 6 / 4 / 0 | 次 | `requests.jsonl`；4 次失败均为不同 DSL 的语法修复，非同一请求重试 |
| 看图 / 完整视觉迭代 | 5 / 3 | 次 | `iterations.jsonl` 与实际图像查看记录；6 张图实际打开（含 2 张放大局部裁切） |
| Server-Timing | null | — | 服务响应未返回该头，`requests.jsonl` 中记为 null |


## 6. 设计选择、经验与未解决事项


**关键设计选择**

1. *柱图纵轴用万元而非元*。净收入 202,368 元若直接标注会得到 6 位数刻度，挤占绘图区。
   改用万元（11.97…20.24，刻度 0/5/10/15/20/25）后刻度短、标签宽裕；KPI 卡与明细表仍保留**元**原值，
   口径在三处（轴标题、副标题、脚注）显式标注，不产生单位混淆。
2. *两序列共用一个 `Scale` 实例*。柱高由同一线性映射产生，零线 y 像素相同，
   保证「共用零起点和比例」不是靠目测而是靠构造保证，并把 `zero_line_y_px` 写进审计 JSON。
3. *转化率用非零起点的折线*。比率在 10.60%–12.00% 的窄区间内波动，零起点会把差异压平。
   改用 10.50%–12.00% 的非零起点，并在**图上副标题和页脚脚注两处**显式声明非零起点，
   同时用虚线标出加权总体均值 11.15% 作为参照，避免读者把窄幅波动误读为剧烈变化。
4. *正文与图表字号分层*。叙事性正文（明细表、结论、卡片标题、KPI 标签）20–28px；
   图表刻度/类别标签 14–17px 作为图表附属元素；脚注 17px。
   完整字号清单写入 `computed-data.json.typography_inventory_px` 便于核对。
5. *结论采用「彩色标识 + 短标题 + 证据句」*，每条都带具体数字，而不是把 KPI 重新念一遍。

**可复用经验**

- `Text` 不能同时给 `text` 属性和子文本；靠前导空格做间距会被 trim，必须用 `SizedBox`。
- `Stack` 必须由 `SizedBox` 固定尺寸并设 `fit="EXPAND"`，`Positioned` 才有可用的坐标系。
- 旋转线段：`Transform` 必须配 `alignment="CENTER"`，且屏幕坐标 y 向下时角度取 `+atan2(dy,dx)`。
- 图表标签框要按「实际字宽」而非「槽位宽」定宽，否则相邻标签在边缘处必然重叠。
- 写文件后若首字节是 `EF BB BF`，服务会以 `PARSE_ERROR: Not Support RAWTEXT` 拒绝。

**结束依据**：全部指定交付物已生成，最终图经整屏与两处放大局部实际查看，
文字无重复/无重叠/无裁切，表中与结论中的每一个数字都与 `computed-data.json` 的计算值一致；
未使用渲染成功或数量达标作为完成依据。


### 未解决事项 / 限制

- 未发现影响交付的未解决问题。
- 题目数据集不含负利润，「负值须正确处理」以构造器代码路径与非交付探针图验证，交付图中不制造不存在的负值。
- 「正文≥20」的边界：图表刻度、类别标签与数值标签按图表附属元素取 14–17px；若评测要求全部文字（含刻度）≥20px，需相应放大画布或减少同屏元素数。当前判断依据是题面把「正文」与「脚注」分开列，且强调「刻度…完整可读」而非其字号。

### 留痕确认

- 临时目录中的草稿 DSL（a01-v1…v5）、每次请求体副本、成功图片、失败响应 JSON、`requests.jsonl` 与 `iterations.jsonl` 均已保留，未删除或覆盖任何一次尝试。
- 未保存任何密钥；`SNAPSHOT_API_KEY` 若存在只从环境变量读取，不写入日志。
- 总任务根已创建 `.gitignore`（参考 `templates/gitignore-template.txt`），仅排除 `__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/` 等运行时缓存；未使用 `tmp/`、`outputs/`、`cache/`、`.cache/`、`*.log` 或图片/DSL/JSON 通配规则，因此本任务的过程证据不会被忽略。（该规则为全套共享，详见 `_suite/snapshot-usage.md`。）
