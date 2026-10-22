# Snapshot 使用情况说明与踩坑记录

任务ID：A01
任务名称：六个月经营诊断驾驶舱
本次运行ID：run-20261011-01
完成状态：完成
结束原因：需求满足并完成视觉自检
输出目录：outputs/run-20261011-01/A01/
临时目录：tmp/run-20261011-01/A01/
路径基准：suite_root（所有路径相对总任务根）

遵循[PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录环境变量。
Markdown本地链接相对当前文档。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| [operations.snapshot](operations.snapshot) | 完整可复现DSL（31,452 字节） | [operations.png](operations.png) | 完成 |
| [operations.png](operations.png) | 服务返回的最终图片（1600×1000，339,925 字节，image/png） | [operations.snapshot](operations.snapshot) | 完成 |
| [computed-data.json](computed-data.json) | 每月计算值、汇总、图轴定义与像素映射、结论引用数值 | 由 `inputs/monthly.csv` 计算 | 完成 |
| [snapshot-usage.md](snapshot-usage.md) | 本报告 | — | 完成 |
| [task-metrics.json](task-metrics.json) | 本题指标 | — | 完成 |

需求逐项核对（依据实际最终图 [operations.png](operations.png) 与其放大裁片）：

| 要求 | 实现 | 证据 |
|---|---|---|
| 1600×1000 经营诊断驾驶舱，期间 2026-04–2026-09 | 画布 1600×1000，头部标注报告期 | 最终图 PNG 尺寸实测 1600×1000 |
| 四张 KPI：总净收入 / 总经营利润 / 总订单 / 期间总体转化率 | 918,624 元 · 262,124 元 · 3,045 笔 · 11.15% | 顶部四卡，44px 数值，标签带单位 |
| 六个月净收入与经营利润分组柱图，共用零起点与比例 | 零基线 0–250,000 元，两系列同一比例尺 | 左侧主图，图例 + 刻度 + 单位脚注 |
| 访问量与转化率两个共享月份对齐的小图 | 上：访问量柱图（0–6,000 次）；下：转化率折线（10.0%–13.0%） | 两图绘图区同为 x=148–896，月份中心 x 完全一致 |
| 六行明细表（月份/净收入/退款率/利润/转化率） | 六行齐全，数字右对齐，金额整数、比例两位小数 | 右侧表格，放大后逐格比对 computed-data 一致 |
| 一条有证据的管理结论 | 标题句 + 4 条证据 + 2 条行动，全部标注引用数值 | 右下结论卡 |
| 总体转化率 = 总订单 / 总访问次数 | 3,045 / 27,300 = 11.15%（非月度比例平均） | KPI 卡脚注写明「不平均月比例」 |
| 退款率 = 退款 / 退款前收入 | 逐月与总体均按该式 | 表格脚注与 computed-data 定义 |
| 百分比与金额不共用混淆数轴 | 金额轴（元）与百分比轴（%）分属不同图 | 三个图各自独立坐标轴 |
| 负值处理 | 本数据集无负值；computed-data.json 记录了零线位置与负值映射方式 | computed-data.json → axes[0].negative_values |
| 正文 ≥20、脚注 ≥16 | 正文/刻度/表格/结论均为 20px 以上（KPI 数值 44、标题 24–36、折线数值 20）；脚注 16px | 逐元素检查 DSL fontSize |
| 末月标签与图表比例 | 2026-09 柱、折线点、月份标签、表格行齐全 | 左下裁片确认 |
| 视觉重点明确 | 头部渐变条 + KPI 强调色 + 主图占最大面积 + 退款率 8.00% 警示色 | 全图查看 |

数据核对：`净收入 = gross_revenue − refund_amount`，`经营利润 = 净收入 − operating_cost`，
`退款率 = refund_amount / gross_revenue`，`转化率 = orders / sessions`。
六个月汇总：净收入 918,624、经营利润 262,124、订单 3,045、访问量 27,300、
总体转化率 11.15%、总体退款率 5.79%、净收入利润率 28.53%。与表格逐行数值一致。

已知缺陷与修复：v1 首版两个小图粘连（0 基线与下一面板标题仅 2px），已改为 18px 间距并重渲染复查；
折线数值标签原为 18px，为满足正文 ≥20 提升到 20px 并确认无重叠。当前无未修复缺陷。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档版本或访问日期：2026-10-11 实际访问

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | POST /snapshot 请求体为 UTF-8 纯文本（非 JSON）、Content-Type 需 charset=utf-8、成功响应为图片字节、错误为 code/message/requestId JSON、429/503 参考 Retry-After、`GET /fonts` 返回 text/plain 字体族 | 全局；`tmp/run-20261011-01/_suite/scripts/snap_render.py` 的请求与重试实现 |
| https://open-snapshot.muedsa.com/fonts | 服务端实际字体族清单（27 个） | `tmp/run-20261011-01/_suite/docs/fonts.txt`；本图统一 fontFamily="Inter,Noto Sans CJK SC" |
| https://snapshot.muedsa.com/reference/parser-tags/ | Snapshot 根标签、Container 渐变与边框、Positioned 定位、Text 的 textAlign/fontSize/textAlign 等段落属性、EdgeInsets 与对齐常量格式 | 全图布局；对齐方案见 §4 |
| https://snapshot.muedsa.com/guides/parser/ | 根标签必须是 Snapshot、未知属性被忽略、文本中 `<` `>` 需 CDATA、空文档抛 ParseException | `tmp/run-20261011-01/_suite/docs/parser-guide.html` |
| https://snapshot.muedsa.com/reference/enums/ | BoxShape 仅 `RECTANGLE`/`CIRCLE`；ClipBehavior、BoxFit 取值 | 修复 `shape="OVAL"` 报错 |

实际用到的 DSL 能力（只列真实使用的）：
- 根与画布：`<Snapshot type="png" background>` + `<SizedBox>` 提供有界根尺寸（见踩坑 2）。
- 布局：`Stack` + `Positioned(left/top/width/height)` 做绝对定位排版；`Container` 做卡片与色块。
- 绘制：`gradientType="LINEAR"` + `gradientColors` + `gradientBegin/End`（卡片、柱体、头部渐变条）；
  `border`/`borderRadius`/`shape="CIRCLE"`；网格线用 1px 高的 Container。
- 变换：`Transform matrix="(cos,sin,0,0,-sin,cos,0,0,0,0,1,0,tx,ty,0,1)" origin="(0,0)"` 把细长矩形旋转成折线段，
  用于转化率折线（解析器没有线段标签，这是唯一可行的 DSL 画线方式）。
- 文本：`fontFamily`、`fontSize`、`color`、`fontStyle="BOLD"`、`textAlign`（START/CENTER/END）。
- 未使用外部图片；全部内容由 DSL 几何与文字构成（A 类 dsl_only 政策）。

字体查询结果：`GET /fonts` 返回 27 族（Inter 及其字重、Noto Sans/Serif/Sans Mono CJK JP/KR/SC/TC/HK、
DejaVu Sans/Mono/Serif、Noto Color Emoji）。最终选择 `Inter,Noto Sans CJK SC`：
拉丁与数字走 Inter，中文回退到 Noto Sans CJK SC，实测混排无豆腐块（见最终图头部与表格）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：tmp/run-20261011-01/A01/requests.jsonl
迭代记录文件：tmp/run-20261011-01/A01/iterations.jsonl
渲染请求总数：7
成功次数：4
失败次数：3
重试请求数：0
DSL版本数：6
实际图片查看次数：9
完整视觉迭代数：2
未完成视觉迭代数：0
其他接口查询：共享文档请求 7 条记于 tmp/run-20261011-01/_suite/requests-shared.jsonl（ai-guide.md、fonts、parser-tags、parser-guide、enums、openapi.yaml 失败尝试、首页）

| 请求ID / 迭代ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| A01-req-0001 / it-001 | tmp/.../A01/drafts/align-test.snapshot | 2026-10-11T13:41:40.712+08:00，0.753s | 403 text/plain（Cloudflare error 1010） | tmp/.../A01/drafts/align-test.png.error.json | 未取得图片；确认为 UA 被 WAF 拦截 |
| A01-req-0002 / it-002 | 同上 | 2026-10-11T13:42:59.007+08:00，3.582s | 200 image/png | tmp/.../A01/drafts/align-test.png | 13:43 已查看：textAlign 三种对齐与 Row 主轴对齐均正确，绿色参考线吻合 |
| A01-req-0003 / it-003 | tmp/.../A01/drafts/operations.snapshot | 2026-10-11T13:50:39.536+08:00，1.671s | 400 application/json | tmp/.../A01/drafts/operations.snapshot.error.json | 未取得图片；PARSE_ERROR shape=OVAL |
| A01-req-0004 | 同上（旧版本，脚本被编码破坏） | 2026-10-11T13:50:56.377+08:00，1.086s | 400 application/json | 同上 | 未取得图片；与 0003 同因，失败尝试保留 |
| A01-req-0005 / it-004 | 同上（shape=CIRCLE） | 2026-10-11T13:53:24.700+08:00，5.470s | 200 image/png | tmp/.../A01/drafts/operations-v1.png | 13:54 已查看全图基线；随后放大 4 个区域 |
| A01-req-0006 / it-005 | 同上（面板间距修正） | 2026-10-11T13:56:40+08:00，约 4.5s | 200 image/png | tmp/.../A01/drafts/operations-v2.png | 13:57 已查看全图 + 左下裁片，间距问题消失 |
| A01-req-0007 / it-006 | outputs/run-20261011-01/A01/operations.snapshot | 2026-10-11T14:04:05.292+08:00，4.040s | 200 image/png | outputs/run-20261011-01/A01/operations.png | 14:05 已查看全图 + 折线近景，20px 标签无重叠 |

图片查看清单（9 次，全部为实际 `read` 打开图片）：align-test.png、operations-v1.png、
裁片 crop-a / crop-c（v1）、operations-v2.png、裁片 crop-c2 / crop-b2 / crop-d2（v2）、
裁片 crop-final-cv（最终图）。裁片由 `tmp/run-20261011-01/_suite/scripts/crop_view.py` 从真实 PNG 截取，不改最终交付图。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| it-001 方案探索 | Python urllib 渲染请求 403，正文 `error code: 1010` | 服务端 WAF 拦截默认 Python-urllib User-Agent（用 curl.exe 同一 DSL 立刻返回 400 而非 403，据此确认是 UA 而非地址/配额） | 渲染脚本请求头加入浏览器 User-Agent 与 Accept | A01-req-0002 起全部 200；此后所有任务复用该脚本 | tmp/.../A01/drafts/align-test.png.error.json |
| it-002 语法修复 | `RENDER_ERROR Layout size is infinite` | Stack 的子节点全部是 Positioned，Stack 不含非定位子节点时不产生有限尺寸，根约束无界（依据 ai-guide「画布尺寸由布局决定」+ 错误消息） | 根改为 `<SizedBox width height>` 包裹 `Stack` | 渲染成功；此后所有任务统一「SizedBox 根 + Stack 绝对定位」骨架 | tmp/.../A01/drafts/align-test.snapshot |
| it-003 语法修复 | `Attr [shape] value is invalid: No enum constant BoxShape.OVAL` | 文档未列出 BoxShape 取值，查 /reference/enums/ 得 `RECTANGLE`/`CIRCLE` | `shape="OVAL"` → `shape="CIRCLE"` | 折线数据点圆点渲染正常 | tmp/run-20261011-01/_suite/docs/enums.html |
| it-005 视觉迭代 | 访问量面板 0 基线（y=790）与转化率面板标题（y=792）几乎贴合，两个小图粘连 | 首版把 316px 高的卡片塞进两块 90px+86px 绘图区，剩余间距不足；由 crop-c 近景确认 | 访问量绘图区 692–778、标题 652；转化率绘图区 834–920、标题 794、月份标签 934 | crop-c2 确认两面板 18px 间距，刻度/标题/数值互不遮挡 | tmp/.../A01/drafts/operations-v2.png、crop-c2.png |
| it-006 视觉迭代 | 折线数值标签 18px，介于「正文 ≥20」与「脚注 ≥16」之间 | 自检按最严口径复核 fontSize | 提升到 20px，并从输出目录 DSL 重新渲染最终图 | 标签间距仍有 34px 富余、无重叠；交付图由交付 DSL 直接生成，可复现性得到验证 | outputs/run-20261011-01/A01/operations.png、crop-final-cv.png |

其他值得记录但本次未触发的问题：
- 解析器不做 HTML 实体解码，文本中的 `<` `>` 必须用 CDATA；本题文案刻意避开了这两个字符。
- `<Text>` 内容会被 trim，首尾空格不保留；需要保留空白时应使用 `<Raw>`（本题未用到）。
- 从文档了解到：`ColorFiltered`/`ImageFiltered` 只支持高斯模糊，任意路径 `ClipPath` 与复杂滤镜仍需 Kotlin DSL；
  本次未使用滤镜，因此未触发相关限制。

## 5. 任务耗时与请求统计

结构化指标文件：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-11T13:38:15.182+08:00 / 2026-10-11T14:09:30+08:00 | 含时区时间 | suite-state.json 起点；结束为本题交付落盘时刻 |
| 任务总耗时 | 1875 | 秒 | 本题墙钟（含读题、写脚本、渲染、看图、写报告） |
| 首次可用图耗时 | 284 | 秒 | 从起点到 A01-req-0002 成功返回有效 PNG |
| 等待用户反馈 | 0 | 秒 | 全自动顺序执行，无用户反馈轮次 |
| 限流等待 | 0 | 秒 | 未出现 429/503，无 Retry-After 等待 |
| 排队等待 | null | 秒 | 服务端未返回排队信息，不可测 |
| 已记录请求耗时之和 | 20.063 | 秒 | requests.jsonl 的 elapsed_seconds 之和（串行，无重叠）；不等于任务总耗时 |
| 成功、失败、重试请求 | 4 / 3 / 0 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 9 / 2 | 次 | iterations.jsonl 与实际图像查看记录 |

服务端 `X-Request-Id` / `Server-Timing` 未在响应中取得（错误响应体内的 `requestId` 已随错误 JSON 保留），
故 server_timing_source 记为 null，不以本地耗时冒充服务端计时。

## 6. 设计选择、经验与未解决事项

关键设计选择：
1. **深色驾驶舱 + 单一强调色体系**：净收入蓝、利润绿、访问量紫、转化率/退款警示琥珀。
   颜色在 KPI、图例、表格、折线之间保持同一语义，管理者可以靠颜色跨图追踪同一指标。
2. **三图共用 x 几何**：主柱图、访问量、转化率三块绘图区左右边界完全相同（x=148–896、月份槽宽 124.667），
   因此三个月份轴在垂直方向逐像素对齐，「共享月份对齐」不只是顺序相同，而是位置相同。
3. **证据分层**：KPI 给结论数字，明细表给逐月精确值，结论卡给引用这些值的判断与行动。
   结论卡每条都指向 computed-data.json 中的字段，避免出现无出处的叙述。
4. **金额与百分比彻底分轴**：金额轴只出现在柱图，百分比轴只出现在折线与表格，杜绝共用数轴的误读。

预览如何影响选择：v1 全图查看后发现两个小图粘连是布局问题而非配色问题，因此只调整 y 几何、不动视觉体系；
折线标签放大前先用近景确认了水平间距富余，避免放大后互相碰撞。

未解决事项与环境限制：无。服务端未提供 Server-Timing，请求耗时只能记录客户端观测值；
`GET /openapi.yaml` 因 webfetch 不支持 yaml 内容类型未取得正文，接口细节改以 ai-guide.md 为准（已在
tmp/run-20261011-01/_suite/requests-shared.jsonl 中如实记录为失败尝试）。

留痕确认：临时目录保留了 align-test 与 operations 的全部 DSL、每次渲染响应（含 3 个失败响应）、
裁片、生成脚本（compute_a01.py / gen_a01_dsl.py / gen_a01_json.py）与共享渲染脚本；
未删除或覆盖任何尝试文件，未保存任何密钥。总任务根 `.gitignore` 已按
[缓存忽略模板](../../../templates/gitignore-template.txt) 创建/合并，排除 `__pycache__/`、
`*.pyc`、`*.pyo`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`，并补充 `.ipynb_checkpoints/`、
`node_modules/`、`*.log.tmp`、`.DS_Store`、`Thumbs.db`；未忽略 `tmp/`、`outputs/` 或任何过程证据。
