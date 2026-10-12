# Snapshot 使用情况说明与踩坑记录

任务ID：A01
任务名称：六个月经营诊断驾驶舱
本次运行ID：20261008T1615Z-run01
完成状态：完成
结束原因：需求满足并完成视觉自检（整图 + 4 张局部裁剪图逐块确认）
输出目录：`outputs/20261008T1615Z-run01/A01/`
临时目录：`tmp/20261008T1615Z-run01/A01/`
路径基准：suite_root（总任务根，即本文件所在目录的上三级）

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `operations.snapshot` | 最终完整 DSL（43,240 字节） | `operations.png` | 完成 |
| `operations.png` | 服务返回的 1600×1000 真实 PNG | `operations.snapshot` | 完成（PNG 签名与 IHDR 已核对为 1600×1000） |
| `computed-data.json` | 每月计算值、汇总、图轴定义、结论引用值 | — | 完成 |

逐条核对：

- 1600×1000 单屏：满足。
- 四张 KPI（总净收入 918,624 元／总经营利润 262,124 元／总订单 3,045 笔／期间总体转化率 11.15%）：满足，金额同时给出原值与万元换算。
- 六个月净收入与经营利润分组柱图：满足，两柱共用零起点与同一线性比例（`axes.grouped_bar.shared_scale=true`），刻度 0/6万/12万/18万/24万。
- 访问量与转化率两个共享月份对齐的小图：满足，两图使用同一 `SPL=66 / SPW=438 / gw2=SPW/6` 分组宽度，月份标签逐月对齐。
- 六行明细表（月份／净收入／退款率／经营利润／利润率／转化率）＋合计行：满足，金额取整数、比例两位小数，数值列右对齐。
- 一条有证据的管理结论：满足，结论卡三段（流量驱动、退款主导利润波动、行动建议），引用值全部写入 `computed-data.json.derived.conclusion_cited_values`。
- 总体转化率用总订单÷总访问次数＝3045/27300＝11.1538%→11.15%，同时把月度简单均值 11.19% 标为“仅对照”，未混用。
- 退款率＝退款÷退款前收入；转化率轴为截断轴（9%–13%），图上显式标注“纵轴自 9% 起（截断轴）”，未与金额轴混用。
- 无负值月份（利润全部为正），零起点比例仍按负值兼容实现（柱高＝v×scale，BASE 为 0 刻度线）。
- 正文≥20、脚注≥16：正文 20–34，脚注 16–18。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档访问日期：2026-10-08（原始响应与响应头保存在 `tmp/20261008T1615Z-run01/_suite/docs/`）

AI 使用指南已完整下载并逐段阅读（`docs/ai-guide.md`，3,718 字节，`text/markdown`）。实际据其确定：请求体是 UTF-8 纯文本而非 JSON、`Content-Type: text/plain; charset=utf-8`、根标签 `<Snapshot type="png">`、成功响应是图片二进制而失败响应是 JSON、`GET /fonts` 每行一个字体族、`400 PARSE_ERROR` 按位置修正、默认不加 `?errorImage=png`。`/openapi.yaml` 也已下载，用于确认 `X-Request-Id`、`Server-Timing`、`Retry-After`、`X-Snapshot-Cache` 等响应头语义，因此 `requests.jsonl` 能记录真实 requestId 与服务端耗时。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| `docs/ai-guide.md` | 请求编码、响应类型、字体查询、错误处理 | 全部渲染调用（`_suite/scripts/render.py`） |
| `docs/openapi.yaml` | `Server-Timing`/`X-Request-Id`/429/503 语义 | `requests.jsonl` 字段设计 |
| `docs/parser-tags.html.txt` | `Stack`/`Positioned` 六属性、同轴最多两项；`Container` 的 `gradientType/gradientColors/gradientBegin/gradientEnd`；`Text` 的 `textAlign/maxLines/height/fontStyle/fontFamily`；`Transform.matrix` 列主序 16 值；`boxShadow` 与 `border="宽 样式 颜色"` 格式 | `operations.snapshot` 全篇 |
| `docs/layout.html.txt` | “父给约束、子报尺寸”；`Container` 的 `width/height` 会收紧约束（因此 `Expanded` 内不能再写死宽高）；`Stack` 默认 `HARD_EDGE` 裁剪，阴影/溢出需显式 `clipBehavior="NONE"` | KPI 卡 `Expanded` 内容、`Stack clipBehavior="NONE"` |
| `docs/painting.html.txt` | 渐变至少两色、`stops` 与颜色等长且升序；阴影会被外层裁剪截断 | 背景渐变 |
| `docs/media-text.html.txt` | `Text` 会 trim 首尾空白；多字体名用逗号且不逐项 trim，故写 `"Inter,Noto Sans CJK SC"` 无空格 | 所有 `fontFamily` |
| `docs/parser.html.txt` | 解析器不做 HTML 实体解码，`<`/`>` 需 CDATA；注释被忽略 | 本次未触发（无尖括号文本） |
| `docs/fonts.txt`（`GET /fonts`） | 26 个字体族；西文选 `Inter`，中文选 `Noto Sans CJK SC` | `operations.snapshot` 的 `fontFamily` |

实际用到的能力：`Stack`+`Positioned` 绝对栅格、`Container` 圆角/边框/内边距/对齐、线性渐变背景、`Row`/`Column` 与 `Expanded`、`Text` 的字号/粗体/对齐/行高/最大行数、`Transform` 旋转矩阵绘制折线段、纯色 `Container` 作为柱体与网格线。未使用 `Image`、`Emoji`、`WidgetSpan`、滤镜与裁剪族标签。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/20261008T1615Z-run01/A01/requests.jsonl`
迭代记录文件：`tmp/20261008T1615Z-run01/A01/iterations.jsonl`
渲染请求总数：11（含 5 张局部裁剪检查图与 1 次最终交付重投）
成功次数：11
失败次数：0（另有 1 次未记入日志的传输失败，见第 5 节）
重试请求数：0
DSL版本数：5（v01–v05）
实际图片查看次数：9
完整视觉迭代数：4
未完成视觉迭代数：0
其他接口查询：`GET /fonts` 1 次（记入 `_suite/requests.jsonl`，shared 前缀）

| 请求ID / 迭代ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| A01-v01-20261008T082030Z / A01-v01-082355 | `tmp/…/A01/v01.snapshot` | 08:20:30Z 起 4.45s（Server-Timing render 4276.9ms） | 200 image/png | `outputs/…/A01/requests/A01-v01-*.response.bin` | 已查看：图表内容按卡片相对坐标写成了画布绝对坐标，柱图压住 KPI 卡 |
| A01-v02-20261008T082356Z / A01-v02-083347 | `tmp/…/A01/v02.snapshot` | 08:23:56Z 起 1.11s | 200 image/png | `outputs/…/A01/requests/A01-v02-*.response.bin` | 已查看：坐标修复，KPI 文字溢出、合计行贴边、结论重叠 |
| A01-v03-20261008T082600Z / A01-v03-083347 | `tmp/…/A01/v03.snapshot` | 08:26:00Z 起 2.11s | 200 image/png | `tmp/…/A01/v03.png` | 已查看：结论卡 ② 与“建议”块重叠 |
| A01-v04-20261008T082745Z / A01-v04-083347 | `tmp/…/A01/v04.snapshot` | 08:27:45Z 起 1.35s | 200 image/png | `tmp/…/A01/v04.png` | 已查看：访问量 “6,000” 被裁成 “6,00” |
| A01-v05-20261008T082932Z / A01-v05-083347 | `tmp/…/A01/v05.snapshot` | 08:29:32Z 起 2.21s | 200 image/png | `tmp/…/A01/v05.png` | 已查看：整图通过，转做局部核查 |
| A01-zoom-z01…z05 | `tmp/…/A01/zoom-z0*.snapshot` | 各 1.5–2.0s | 200 image/png | `tmp/…/A01/zoom-z0*.png` | 已查看：z01/z02 暴露 Transform 缩放缺陷；z03/z04/z05 确认表格、结论卡、小图刻度 |
| A01-v05-final-20261008T083404Z | `tmp/…/A01/v05.snapshot` | 08:34:04Z | 200 image/png | `outputs/…/A01/operations.png` | 最终交付重投，与 v05 同 DSL |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| A01-v02 / visual / v01 | 分组柱图与访问量柱画在画布顶部，压住 KPI 卡；表格合计行溢出卡片 | 生成器里 `pos()` 直接提交传入坐标，而柱图内部按“卡片左上角为原点”书写，未加 `CY`/`SY` 偏移（文档证据：`Positioned` 相对 Stack 定位） | 引入 `CUR` 卡片原点，`pos/rect/label` 统一换算为画布绝对坐标；重排纵向栅格 | v02 中图表回到各自卡片内；已解决 | `v01.snapshot`、`v02.snapshot` |
| A01-v03 / visual / v02 | KPI 第四行说明被卡片裁掉；合计行贴住卡片下沿；结论三段互相重叠 | 文本块高度按字号估算不足：`fontSize 20` 实际行高约 26px，`fontSize 32` 约 42px，Column 累计超过卡片可用高度（`Container` 不裁剪也不换行提示） | KPI 卡加高到 156、数值字号 32→30、脚注降到 16；表格行高 30→28；结论卡改固定高度顶对齐文本块 | v03 中 KPI 四行完整；结论仍重叠 | `v03.snapshot`、`v03.png` |
| A01-v04 / visual / v03 | 结论 ② 与“建议”块重叠、被分隔线切断 | `label()` 默认 `CENTER_LEFT` 垂直居中，文本实际 3 行（约 81px）超出 78px 盒后向上下同时溢出 | 为 `label()` 增加 `valign="TOP"`，并按真实行数给 56/84/64 的固定高度 | v04 中结论卡无重叠（z04 裁剪图复核确认）；已解决 | `v04.snapshot`、`zoom-z04.png` |
| A01-v05 / visual / v04 | 访问量纵轴 “6,000” 显示成 “6,00” | `Positioned width` 固定 50，而 20px 字体的 “6,000” 约 55px；`Container` 不裁剪但 `Positioned` 盒宽限制了右对齐文本的可用宽度 | 刻度标签盒宽 50→58，绘图区左界 `SPL` 62→66 | v05 与 z05 复核刻度完整；已解决 | `v05.snapshot`、`zoom-z05.png` |
| zoom-z01/z02 / alternative / v05 | 用 `Transform` 矩阵把整图放大 2 倍做局部检查时，圆角 `Container`（卡片底、柱体）完全不绘制，只剩文字与 1px 网格线 | 已确认可复现：同 DSL 去掉 `Transform` 后圆角容器正常（z03/z04/z05）；具体服务端实现原因未确认，标为推测 | 放弃 Transform 缩放，改为 1:1 纯裁剪局部出图 | 裁剪图能可靠核对文字与几何；缩放缺陷已绕开 | `zoom.py`、`zoom-z01.png`、`zoom-z03.png` |
| 语法修复 | 无 | 本次 5 个设计版本与 5 个裁剪版本全部一次解析通过，未出现 `400 PARSE_ERROR` | — | 未发生 | — |

从文档了解但本次未触发的注意事项：`<Image>`/`<Emoji>` 的 `url` 与 `dataUri` 互斥且会同步取图；`Stack` 默认裁剪会截断阴影；`ColorFiltered` 要求显式 `blendMode`；`Raw` 才保留首尾空白。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/20261008T1615Z-run01/A01/task-metrics.json`

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-08T08:15:00Z → 08:34:32Z | ISO8601 UTC | 手工记录开始 + `build_metrics.py` 结束时间 |
| 任务总耗时 | ≈1172 | 秒 | 墙钟，含读文档与写生成器 |
| 首次可用图耗时 | 330 | 秒 | 从开始到 v01 成功渲染（含目录初始化与文档下载） |
| 等待用户反馈 | 0 | 秒 | 单轮任务，无外部反馈 |
| 限流等待 | 0 | 秒 | 未出现 429/503，`Retry-After` 全为 null |
| 排队等待 | 0 | 秒 | 所有成功响应的 `Server-Timing` 均未出现 `queue` 段 |
| 已记录请求耗时之和 | 21.6 | 秒 | `requests.jsonl` 11 次渲染之和，与墙钟重叠不可相加 |
| 成功／失败／重试请求 | 11／0／0 | 次 | `requests.jsonl` |
| 实际看图与完整视觉迭代 | 9／4 | 次 | `iterations.jsonl` |

未记入 `requests.jsonl` 的一次传输失败：v04 首次提交时 curl 未写出响应体（无 HTTP 状态码），脚本在读取响应前抛 `FileNotFoundError`，因此该次尝试没有日志行；证据仅存 `tmp/20261008T1615Z-run01/A01/seq/requests/A01-v04-20261008T082654Z.body.txt` 与同名 `.response-headers.txt`（响应头文件为空）。随后已修改 `render.py`，使无响应体的失败也会写入日志并自动按 `Retry-After` 重试。此事件已在 `task-metrics.json.notes` 中登记。

## 6. 设计选择、经验与未解决事项

视觉重点策略：把“净收入 91.86 万元／利润率 28.53%”这类总量放成 30–34px 的强色数字，把环比与口径说明压到 16–18px 灰字，形成 KPI→柱图→明细→结论的阅读动线；退款率与利润率异常值（8.00%、21.99%、23.72%）在表格里用红/绿着色，使结论 ② 的证据在图中可直接指认。分组柱与两个小图刻意分轴：金额轴零起点、次数轴零起点、百分比轴截断并在图上标注，避免单位混淆。

可复用经验：
1. 用 `Stack`+`Positioned` 做绝对栅格最直观，但必须给每个卡片维护一个原点偏移，否则图表内部坐标会与画布坐标混用（本次最主要的返工原因）。
2. `Container` 的 `width/height` 会收紧约束，`Expanded` 的子节点不能再写死宽高，否则该轴只剩 1px。
3. 文本块高度要按“字号×约 1.3 的行高 × 行数”预留，`Container` 不裁剪也不提示溢出，只能靠看图发现。
4. 局部核查用 1:1 裁剪图比 `Transform` 放大可靠（Transform 缩放下圆角容器不绘制）。
5. `Server-Timing` 与 `X-Request-Id` 都能真实取到，值得在日志里固定留字段。

未解决事项：无阻塞。已知的渲染器行为缺陷（Transform 缩放丢失圆角容器绘制）只影响自检工具，不影响交付图；原因未确认，如后续任务需要缩放图需改用重新生成坐标的方式。

留痕确认：`tmp/20261008T1615Z-run01/A01/` 保留 v01–v05 全部 DSL、5 张预览/裁剪图、生成器脚本与 `seq/requests/`、`outputs/…/A01/requests/` 下的请求体、响应头与原始响应字节；失败与半程文件均未删除。根目录 `.gitignore` 已创建（`.gitignore`），仅忽略 `__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`、`node_modules/` 等运行时缓存，未忽略 `outputs/`、`tmp/` 或任何过程证据。
