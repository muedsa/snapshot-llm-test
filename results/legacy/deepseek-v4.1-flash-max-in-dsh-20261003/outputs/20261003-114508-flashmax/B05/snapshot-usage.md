# Snapshot 使用情况说明与踩坑记录

任务ID：B05 · 从零构想产品并设计十个关键使用画面
任务名称：Kelpline — 虚构的近岸航行安全产品十屏
本次运行ID：20261003-114508-flashmax
完成状态：完成（10 件独立完整作品，全部经实际看图与整册复审）
结束原因：需求满足并完成视觉自检
输出目录：`D:\workspaces\deepseek-v4.1-flash-max-in-dsh\outputs\20261003-114508-flashmax\B05`
临时目录：`D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\B05`

> 声明：本作品集内的港口、船、人物、天气模式名、通告与电话号码全部为虚构；潮汐、方位、
> 油量与漂移数值由 `tools/b05_data.py` 用标准公式计算（潮汐为四项调和合成，相位自拟）。
> 未做任何用户调研、现场试验或专家评审，报告中不声称做过。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `case-01/final.png` | 服务返回的最终图片（500x1060，117918 字节） | `case-01/final.snapshot` | 完成，HTTP 200 image/png |
| `case-02/final.png` | 服务返回的最终图片（1600x1000，206610 字节） | `case-02/final.snapshot` | 完成，HTTP 200 image/png |
| `case-03/final.png` | 服务返回的最终图片（1240x1754，350753 字节） | `case-03/final.snapshot` | 完成，HTTP 200 image/png |
| `case-04/final.png` | 服务返回的最终图片（1600x1000，238844 字节） | `case-04/final.snapshot` | 完成，HTTP 200 image/png |
| `case-05/final.png` | 服务返回的最终图片（500x1060，130798 字节） | `case-05/final.snapshot` | 完成，HTTP 200 image/png |
| `case-06/final.png` | 服务返回的最终图片（1180x820，108577 字节） | `case-06/final.snapshot` | 完成，HTTP 200 image/png |
| `case-07/final.png` | 服务返回的最终图片（1600x1000，283752 字节） | `case-07/final.snapshot` | 完成，HTTP 200 image/png |
| `case-08/final.png` | 服务返回的最终图片（1180x820，169248 字节） | `case-08/final.snapshot` | 完成，HTTP 200 image/png |
| `case-09/final.png` | 服务返回的最终图片（800x1200，180513 字节） | `case-09/final.snapshot` | 完成，HTTP 200 image/png |
| `case-10/final.png` | 服务返回的最终图片（1600x1000，239311 字节） | `case-10/final.snapshot` | 完成，HTTP 200 image/png |
| `case-01/final.snapshot` | 完整可复现DSL（65493 字节） | `case-01/final.png` | 完成 |
| `case-02/final.snapshot` | 完整可复现DSL（143194 字节） | `case-02/final.png` | 完成 |
| `case-03/final.snapshot` | 完整可复现DSL（65431 字节） | `case-03/final.png` | 完成 |
| `case-04/final.snapshot` | 完整可复现DSL（52051 字节） | `case-04/final.png` | 完成 |
| `case-05/final.snapshot` | 完整可复现DSL（24076 字节） | `case-05/final.png` | 完成 |
| `case-06/final.snapshot` | 完整可复现DSL（16771 字节） | `case-06/final.png` | 完成 |
| `case-07/final.snapshot` | 完整可复现DSL（111963 字节） | `case-07/final.png` | 完成 |
| `case-08/final.snapshot` | 完整可复现DSL（20385 字节） | `case-08/final.png` | 完成 |
| `case-09/final.snapshot` | 完整可复现DSL（16296 字节） | `case-09/final.png` | 完成 |
| `case-10/final.snapshot` | 完整可复现DSL（26966 字节） | `case-10/final.png` | 完成 |

另交付：`product-brief.md`（问题/受众/机制/假设与验证边界）、`journey.json`（十屏前后关系与共享事实）、
`portfolio.json`、`portfolio.md`、`gallery.html`、`snapshot-usage.md`、`task-metrics.json`，
以及每例的 `case.md`。

### 逐件自检（尺寸 / 内容 / 几何 / 实际看图）

| 用例 | 尺寸 | 关键几何与字号 | 看图结论 |
|---|---|---|---|
| case-01 黎明出击卡 | 500x1060 | 判定字 64，检查行 20/16，潮汐条 96 高 | 判定 2 秒可读；标注重叠已修 |
| case-02 潮汐与流图 | 1600x1000 | 曲线 5px、24h 400 高；轴标 15 | 两个闸门窗口与两次穿越可直读 |
| case-03 航次计划 A4 | 1240x1754 | 表行 17/18，图 494 高，正文 16 | 打印页无重叠、无出界；闸门行标注正确 |
| case-04 天气窗口 | 1600x1000 | 单元 240x112，结论 30，脚注 15 | 最佳/最差窗口一眼可辨，图例不再压轴标 |
| case-05 浮报与岸上守望 | 500x1060 | 阶梯时间 19，升级行 17/15 | 非航海者能复述 15:38/16:08/16:38 三步 |
| case-06 水上扫视屏 | 1180x820 | 数值 104/72，罗经带 118 高 | 阳光可读；油量块重叠已修 |
| case-07 逾时漂移基准 | 1600x1000 | 图 1120x620，箱半径按 nm 等比 | 箱序/概率/面积/扫测时间齐全；假设写在图上 |
| case-08 油量与续航 | 1180x820 | 梯级条 52 高，刻度 0-36 L | 逆风情景与余量最醒目；无列溢出 |
| case-09 港务电子墨水板 | 800x1200 | 表行 36，正文 16-17 | 3 米外可读；右侧警告不再出界 |
| case-10 赛季复盘 | 1600x1000 | KPI 40，柱图 200 高，误差线 3.5px | 四个 KPI 不再互压，阈值带标签清楚 |

每件另有 `case.md` 写明场景、内容依据、视觉选择、自定完成标准、看图证据与发现的缺陷。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | `POST /snapshot` 请求体为 UTF-8 纯文本、成功返回图片二进制、错误为含 code/message/requestId 的 JSON、颜色 CSS 写法 | `tools/render_cases.ps1`、所有 DSL |
| https://snapshot.muedsa.com/reference/parser-tags/ | 38 个标签总表；`Container` 的 `gradientType/gradientColors/gradientStops`、`shape`、`foreground*`、`transform` 属性；`ClipOval/ClipRRect`、`Opacity`、`boxShadow` 自定义与 `ELEVATION_n`、`borderTop` 等单边边框、`Positioned` 每轴最多两项 | `bkit.py`、`style.py`：渐变卡片、圆形、圆角裁剪、阴影、单边强调条 |
| https://snapshot.muedsa.com/reference/parser-tags/#对齐 / #圆角 / #边框 | 对齐常量语义、`borderRadius` 单值 vs 四角属性、`border` 需写 `宽度 样式 颜色` | `bkit.box/text/tbox` |
| `GET /fonts`（复用 A01 已取得的响应 `tmp/.../_suite/shared/fonts.txt`） | 实际可用字体：`Noto Sans CJK SC`、`Noto Sans Mono CJK SC`、`Inter`、`Noto Serif CJK SC` 等 | 全册排版：正文 CJK、数字与代码用 Mono、标题与标签用 Inter |

未新增 `/fonts` 请求：该查询在 A01 已经真实执行并把响应保存在共享目录，本题直接复用该文件，
不把它重复计入本题消耗。文档请求 2 次（ai-guide.md、parser-tags 页面）。

实测确认（写进 `bkit.py` 注释，避免后续重复踩坑）：

- `Transform matrix` 写 16 个数字，旋转放前四位、平移放第 13/14 位，原点为左上角；
  `Container` 也可直接写 `transform` 属性。
- 文本节点**不做 XML 实体解码**：`&` 必须原样写，写 `&amp;` 会直接渲染成 "&amp;"（case-02 v1 实测）。
- 带 `width` 的 `Container` 会让 `Text` 换行，行高约 1.28 倍字号；不带宽度则永不换行。
- 对齐常量按 Flutter 语义：`CENTER` 是两轴居中（子任务简报里"CENTER 为底部居中"的说法在本服务上不成立，
  已用 Pillow 量测像素行证伪）；`TOP_LEFT` 在 20px 时墨迹距顶 5px。
- 渐变、`shape="CIRCLE"`、`ClipOval/ClipRRect`、`Opacity`、自定义 `boxShadow`、`letterSpacing` 均可用。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\B05\requests.jsonl`
迭代记录文件：`D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\B05\iterations.jsonl`
渲染请求总数：36（含 2 次能力探针）
成功次数：33
失败次数：3（两次生成脚本报错根本未发出请求 + 一次真实 400 PARSE_ERROR）
重试请求数：2
DSL版本数：32
实际图片查看次数：28
完整视觉迭代数：13
未完成视觉迭代数：0
其他接口查询：本题内 0 次（未调用 /fonts，理由见上）；文档阅读 2 次网页请求

逐请求明细见 requests.jsonl，含 request_id、case_id、phase、起止时间（+08:00）、耗时、
HTTP 状态、Content-Type、输入 DSL、输出文件、服务端 X-Request-Id 与错误正文。下表给出关键节点：

| 请求ID | 用例 | 输入DSL | 结果 | 查看与结论 |
|---|---|---|---|---|
| B05-REQ-0001 | shared | `probe1.snapshot` | 200 · 1828ms | 已看图核对 |
| B05-REQ-0002 | shared | `probe2.snapshot` | 200 · 1904ms | 已看图核对 |
| B05-REQ-0003 | case-01 | `-` | no response (失败) · 58ms | 错误正文已读，见 .failed.txt |
| B05-REQ-0004 | case-01 | `case-01.v1.snapshot` | 200 · 2219ms | 已看图核对 |
| B05-REQ-0005 | case-01 | `case-01.v1.snapshot` | 200 · 3060ms | 已看图核对 |
| B05-REQ-0006 | case-02 | `case-02.v1.snapshot` | 200 · 4327ms | 已看图核对 |
| B05-REQ-0007 | case-03 | `-` | no response (失败) · 60ms | 错误正文已读，见 .failed.txt |
| B05-REQ-0008 | case-03 | `case-03.v1.snapshot` | 200 · 3391ms | 已看图核对 |
| B05-REQ-0009 | case-01 | `case-01.v2.snapshot` | 200 · 3097ms | 已看图核对 |
| B05-REQ-0010 | case-02 | `case-02.v2.snapshot` | 200 · 2790ms | 已看图核对 |
| B05-REQ-0011 | case-03 | `case-03.v2.snapshot` | 200 · 3683ms | 已看图核对 |
| B05-REQ-0012 | case-03 | `case-03.v3.snapshot` | 200 · 2961ms | 已看图核对 |
| B05-REQ-0013 | case-04 | `case-04.v1.snapshot` | 400 (失败) · 2015ms | 错误正文已读，见 .failed.txt |
| B05-REQ-0014 | case-04 | `case-04.v2.snapshot` | 200 · 3998ms | 已看图核对 |
| B05-REQ-0015 | case-04 | `case-04.v2.snapshot` | 200 · 2719ms | 已看图核对 |
| B05-REQ-0016 | case-05 | `case-05.v2.snapshot` | 200 · 1961ms | 已看图核对 |
| B05-REQ-0017 | case-06 | `case-06.v2.snapshot` | 200 · 1879ms | 已看图核对 |
| B05-REQ-0018 | case-07 | `case-07.v1.snapshot` | 200 · 5265ms | 已看图核对 |
| B05-REQ-0019 | case-08 | `case-08.v1.snapshot` | 200 · 2460ms | 已看图核对 |
| B05-REQ-0020 | case-07 | `case-07.v2.snapshot` | 200 · 3849ms | 已看图核对 |
| B05-REQ-0021 | case-08 | `case-08.v2.snapshot` | 200 · 2347ms | 已看图核对 |
| B05-REQ-0022 | case-09 | `case-09.v1.snapshot` | 200 · 1861ms | 已看图核对 |
| B05-REQ-0023 | case-10 | `case-10.v1.snapshot` | 200 · 2438ms | 已看图核对 |
| B05-REQ-0024 | case-09 | `case-09.v3.snapshot` | 200 · 2161ms | 已看图核对 |
| B05-REQ-0025 | case-10 | `case-10.v3.snapshot` | 200 · 2118ms | 已看图核对 |
| B05-REQ-0026 | case-01 | `case-01.final.snapshot` | 200 · 3714ms | 已看图核对 |
| B05-REQ-0027 | case-02 | `case-02.final.snapshot` | 200 · 3057ms | 已看图核对 |
| B05-REQ-0028 | case-03 | `case-03.final.snapshot` | 200 · 2833ms | 已看图核对 |
| B05-REQ-0029 | case-04 | `case-04.final.snapshot` | 200 · 3170ms | 已看图核对 |
| B05-REQ-0030 | case-05 | `case-05.final.snapshot` | 200 · 1974ms | 已看图核对 |
| B05-REQ-0031 | case-06 | `case-06.final.snapshot` | 200 · 2013ms | 已看图核对 |
| B05-REQ-0032 | case-07 | `case-07.final.snapshot` | 200 · 3133ms | 已看图核对 |
| B05-REQ-0033 | case-08 | `case-08.final.snapshot` | 200 · 3414ms | 已看图核对 |
| B05-REQ-0034 | case-09 | `case-09.final.snapshot` | 200 · 2636ms | 已看图核对 |
| B05-REQ-0035 | case-10 | `case-10.final.snapshot` | 200 · 2665ms | 已看图核对 |
| B05-REQ-0036 | case-06 | `case-06.v4.snapshot` | 200 · 2089ms | 已看图核对 |

初次生成与查看计为基线；看旧图→改 DSL→重渲染→再看的完整视觉迭代共 13 次（见 iterations.jsonl
的 B05-IT-002…014），另有 1 次语法修复（B05-IT-006）、2 次未到达服务的重试（B05-IT-015/016）、
2 次能力探针（B05-IT-001）与 1 次整册复审（B05-IT-017）。

## 4. 修改记录与踩坑

| 迭代ID / 类型 | 问题或现象 | 原因及确认依据 | 采取的修改 | 验证结果 | 相关文件 |
|---|---|---|---|---|---|
| B05-IT-001 / 能力探针 | 不确定本构建是否支持旋转、渐变、裁剪 | 两次探针渲染 + Pillow 量测墨迹行 | 把可用能力与坐标语义写进 `bkit.py` | 十件作品全部依赖这些能力，无一失败 | `dsl/probe1.snapshot`、`dsl/probe2.snapshot` |
| B05-IT-002 / 视觉 | case-01 标注压标题、时间与日程不一致 | 直接看图 | 标注移到点下方、"now" 并入说明行、时间全部改为 06:25/15:08 | 复看通过 | `render/case-01.v1.png` → `final` |
| B05-IT-003 / 视觉 | case-02 出现 "&amp;"、"&lt;" 字面量 | 看图 + 服务行为确认 | `esc()` 改为原样输出，文案避免裸 `<` `>` | 复看显示正确的 "&" 与 "under" | `render/case-02.v1.png` → `final` |
| B05-IT-004/005 / 视觉 | case-03 浅滩压在岸线上、章节重叠、到达时间错 | 看图 | 岸线整体北移、章节重排、ETA 与闸门行按日程重算 | 三版后通过 | `render/case-03.v1/v2/v3.png` |
| B05-IT-006 / 语法修复 | case-04 HTTP 400：`Attr [color] unsupported CSS color [0E9F8F]` | 服务返回的 JSON 错误正文（curl 保留了 body） | 数据模型里的判定色补上 `#` | 下一次请求 200 | `render/case-04.v1.png.failed.txt` |
| B05-IT-007…014 / 视觉 | 图例压轴标、迷你图标注压正文、油量块自压、搜索箱按比例过大淹没画面、脚注与列溢出、KPI 副标压数值 | 逐张看图 | 逐条调整版式与文案（详见 iterations.jsonl） | 每件复看通过 | `render/*.v*.png` |
| B05-IT-015/016 / 重试 | 两次请求根本没发出（生成脚本异常，curl 打不开文件） | `requests.jsonl` 中 http_status 为空 | 修脚本 + 渲染脚本在生成失败时不发请求 | 后续请求均 200 | `tools/gen_b05.py`、`tools/render_cases.ps1` |

未触发的注意事项（从文档了解但本次未遇到）：`413 REQUEST_TOO_LARGE`、`429` 与 `Retry-After`
（本题 36 次请求全部在限额内，服务端未返回限流响应）；`?errorImage=png` 调试参数未使用。

## 5. 任务耗时与资源消耗

结构化指标文件：`D:\workspaces\deepseek-v4.1-flash-max-in-dsh\outputs\20261003-114508-flashmax\B05\task-metrics.json`

| 指标 | 实际值 | 单位 | 来源与统计范围 |
|---|---|---|---|
| 开始 / 结束时间 | 2026-10-03T12:52:19.4790983+08:00 / 2026-10-03T13:07:41+08:00 | ISO8601 +08:00 | 首次请求开始到产物写完 |
| 任务总耗时 | 921.5 | 秒 | 墙钟时间 |
| 首次可用图耗时 | 1.8 | 秒 | 开始 → B05-REQ-0001 返回首张可打开图片 |
| 等待用户反馈 | 0 | 秒 | 单轮自动执行，未等待 |
| 限流等待 | 未发生（0） | 秒 | 无 429 |
| 排队等待 | null | 秒 | 服务端排队不可测 |
| 已记录请求耗时之和 | 95.1 | 秒 | requests.jsonl 的 duration_ms 求和（含探针与失败请求，不等于墙钟） |
| token / 图像输入 / 费用 | null | — | 平台未提供，不用字数估算 |
| 请求数（成功/失败） | 33/3（共 36） | 次 | requests.jsonl |
| DSL 版本数 | 32 | 个 | tmp/dsl/*.snapshot |
| 看图次数 | 28 | 次 | read_image 实际打开 |
| 最终作品数 | 10 | 件 | outputs/B05/case-* |

## 6. 设计选择、经验与未解决事项

关键设计选择：把"一条潮汐曲线"当作产品记号，在手机卡片上是迷你曲线、在桌面是主图、在水上是
倒计时卡、在搜救屏上是漂移基准、在港务板上是开启时段；配色只在四种语义上用彩（青=可去、
琥珀=留意、红=不可、蓝=数据），其余靠明度分层。所有数值来自同一个 `b05-data.json`，
因此十屏之间不可能互相矛盾——这也是本册最重要的工程决定。

经验：先用两次探针把服务能力与文本坐标量清楚，再写共享构件，比逐图试错省得多；
带 `width` 的容器会换行这件事，是排版是否"压字"的分水岭。

未解决事项：
1. `case-01.v1`/`case-02.v1` 在版本命名规范确立前被同名重渲染覆盖，那两个最早的 DSL/PNG 草稿
   不可再取；此后的每次修改都使用独立版本号，`requests.jsonl` 仍完整记录了这些请求。
2. `case-04` 的 v2 在同批渲染中被提交了两次（DSL 字节完全相同，服务返回相同字节），
   日志如实记为两次请求。
3. 未做用户测试，"一眼可读"是基于实际看图的判断，不是实测结论。

临时目录内容确认：`dsl/`（32 个 .snapshot，含探针与所有中间版本）、
`render/`（每次响应 PNG、`.rawbody/.rawheaders/.rawmeta` 与失败正文 `*.failed.txt`）、
`tools/`（构建脚本、数据模型、量测脚本、渲染脚本）、`data/`（b05-data.json、tide-curve.csv）、
`requests.jsonl`、`iterations.jsonl`、`tool-usage.jsonl` 均保留，未删除或覆盖（除上述第 1 条）。
