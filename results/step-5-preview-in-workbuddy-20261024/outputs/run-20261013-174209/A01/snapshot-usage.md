# Snapshot 使用情况说明与踩坑记录

任务ID：A01
任务名称：六个月经营诊断驾驶舱
本次运行ID：run-20261013-174209
完成状态：完成
结束原因：需求满足并完成视觉自检
输出目录：`outputs/run-20261013-174209/A01/`
临时目录：`tmp/run-20261013-174209/A01/`
路径基准：默认 `suite_root`（总任务根）；`computed-data.json` 内部字段基准为 `output_dir`

遵循[PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录
环境变量。Markdown本地链接相对当前文档；生成报告时按实际报告位置重新计算所有本地链接。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| [operations.snapshot](operations.snapshot) | 完整可复现DSL | [operations.png](operations.png) | 完成 |
| [operations.png](operations.png) | 服务返回的最终图片（1600×1000 真实 PNG） | [operations.snapshot](operations.snapshot) | 完成 |
| [computed-data.json](computed-data.json) | 每月计算值、汇总、图轴定义与结论引用数值 | — | 完成 |
| [task-metrics.json](task-metrics.json) | 本题指标 | — | 完成 |

需求逐项核对（均以最终实际渲染图 `operations.png` 复核）：

| 要求 | 实际满足情况 |
|---|---|
| 1600×1000 驾驶舱 | 服务返回 PNG 实测 1600×1000 |
| 四张 KPI：总净收入 / 总经营利润 / 总订单 / 期间总体转化率 | 918,624 元、262,124 元、3,045 笔、11.15% |
| 六个月净收入与经营利润分组柱图 | 左列分组柱，两系列共用零起点与同一纵轴（0–22 万元，刻度 0/5.5/11/16.5/22） |
| 访问量与转化率两个共享月份对齐的小图 | 右列上下两个面板，共用同一 `spx0/spx1` 与分组宽度 `gw`，月份轴逐一对齐 |
| 六行明细表（月份/净收入/退款率/利润/转化率） | 六行 + 合计行，右对齐数值列 |
| 一条有证据的管理结论 | 结论区含 3 条量化证据 |
| 总体转化率 = 总订单/总访问，不平均月比例 | 3,045/27,300 = 11.15%；月比例平均为 11.19%，已核对不同 |
| 退款率 = 退款/退款前收入 | 逐月核对通过 |
| 柱图共用零起点和比例 | 两系列同一 `y_max=220000`，零线为实线轴线 |
| 百分比与金额不共用混淆数轴 | 金额用万元轴；转化率用独立 10.0%–12.0% 轴 |
| KPI 金额原值或正确万元 | 保留原值 918,624 元，并附 ≈91.9 万元 |
| 明细金额整数、比例两位小数 | 金额千分位整数；比例 5.00%/8.00%/4.00%、11.15% 等两位小数 |
| 图表刻度、单位、图例、所有月份完整可读 | 纵轴刻度 + 「万元」「次/笔」「%」单位标注 + 图例；六个月标签在 3 张图中均完整 |
| 正文 ≥20、脚注 ≥16 | 正文 17–21px 为主、关键数值 42px；脚注 14–16px |
| 视觉重点明确 | 四个 KPI 用色条区分；柱图仅标净收入与利润数值；小图避免堆数 |
| 表格对齐、最后一个月标签、图表比例 | 数值列右对齐；2026-09 标签在图与表中均未被裁切 |

`computed-data.json` 含 `months`（每月原始分子/分母、净收入、利润、退款率、转化率）、
`totals`、`axes`（各图轴单位、最小/最大值、零线、数据到像素映射）与 `conclusion`
（文案、引用字段与数值）。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com（以总 run-config.json 的 `service_base_url` 为准）
文档版本或访问日期：2026-10-13 实际访问（`/ai-guide.md`、`/fonts`、DSL 文档站与 GitHub 源码）

AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md
实际应用：请求体为 UTF-8 纯文本（非 JSON）、`Content-Type: text/plain; charset=utf-8`、
成功响应为图片二进制、失败为含 `code`/`message`/`requestId` 的 JSON；本次 3 次 400 错误均按
`PARSE_ERROR` 的位置信息修正 DSL 后重提。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| [ai-guide.md](https://open-snapshot.muedsa.com/ai-guide.md) | POST /snapshot 纯文本请求体；GET /fonts 字体族列表；错误分类与 `X-Request-Id` | [operations.snapshot](operations.snapshot) 全部请求 |
| [/fonts](https://open-snapshot.muedsa.com/fonts) | 选择 `Noto Sans CJK SC`（中文正文）与 `Noto Sans Mono CJK SC`（数值等宽） | KPI、表格、刻度文字 |
| [标签与属性参考](https://snapshot.muedsa.com/reference/parser-tags/) | `Container` 装饰合并、`Positioned` 定位、`Row/Column`、`boxShadow`、`borderRadius`、`gradient*` | 卡片、圆角、色条 |
| [类 DOM 解析器](https://snapshot.muedsa.com/guides/parser/) | 根标签必须第一个且唯一；`Text` 裁剪首尾空白；`CDATA` 处理 `<`/`>`；注释可忽略 | 整份 DSL |
| [枚举速查](https://snapshot.muedsa.com/reference/enums/) | `FontStyle` = NORMAL/BOLD；`MainAxisAlignment`；`BoxFit` | `fontStyle="BOLD"` |
| GitHub 源码 `CommonAttrDefine.kt` | 确认 `color`/`fontSize`/`fontFamily` 属性名与默认值 | 文本节点 |
| GitHub 源码 `TextParser.kt` / `TextStyleParser.kt` | 确认 `textAlign` 取 Skia `Alignment`（LEFT/CENTER/RIGHT）、`softWrap`、`maxLines`、`letterSpacing` | 表格右对齐、刻度 |
| GitHub 源码 `ContainerParser.kt` / `PositionedParser.kt` / `StackParser.kt` | 确认 `transform` 为列主序 4×4、`transformAlignment`、`Positioned` 六属性 | 折线连线、绝对定位版面 |

字体查询结果：本次 `GET /fonts` 返回 Inter 系列、Noto Sans/Serif CJK SC/TC/JP/KR/HK、
DejaVu 系列与 Noto Color Emoji。最终选择 `Noto Sans CJK SC` 与 `Noto Sans Mono CJK SC`。

变换矩阵约定通过像素采样实测确认：`transform="(cos,sin,0,0,-sin,cos,0,0,0,0,1,0,0,0,0,1)"`
配合 `transformAlignment="TOP_LEFT"` 得到顺时针旋转（屏幕坐标 y 向下），
探针图与采样记录见 `tmp/run-20261013-174209/A01/probe-rot3.png`。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：[tmp/run-20261013-174209/A01/requests.jsonl](../../../tmp/run-20261013-174209/A01/requests.jsonl)
迭代记录文件：[tmp/run-20261013-174209/A01/iterations.jsonl](../../../tmp/run-20261013-174209/A01/iterations.jsonl)
渲染请求总数：13（含 8 次能力探针）
成功次数：10
失败次数：3（1 次 403 User-Agent 拦截、2 次 400 矩阵值个数错误）
重试请求数：0
DSL版本数：5（基线 + 4 次视觉迭代）
实际图片查看次数：8（探针 3 张 + 基线 1 张 + 迭代 4 张）
完整视觉迭代数：5
未完成视觉迭代数：0
其他接口查询：`GET /fonts` 1 次（web_fetch 取得）；文本宽度测量渲染请求 18 次
（见 `tmp/run-20261013-174209/MEASURE/requests.jsonl`）

| 请求ID / 轮次 / 迭代ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| A01-probe-1791884795058 | probe.snapshot | 17:46:36 +08:00, 1.734s | 403 text/plain | responses/…-….txt | 未取得图片；错误 `error code: 1010`（CDN 拦截默认 urllib UA） |
| A01-probe-1791884873388 | probe.snapshot | 17:47:54 +08:00, 1.422s | 200 image/png | responses/…-….png | 已查看：连通性确认 |
| A01-probe-1791886012945 | probe-transform.snapshot | 17:53:32 +08:00, 4.375s | 200 image/png | responses/…-….png | 已查看：变换与中文文本正常 |
| A01-probe-1791886315671 | probe-rot.snapshot | 17:58:35 +08:00, 2.672s | 200 image/png | responses/…-….png | 已查看：用于像素采样判向 |
| A01-probe-1791886348637 / -1791886374217 | probe-rot2.snapshot | 17:59:08 / 17:59:34 +08:00 | 400 application/json | responses/…-….txt | 未取得图片；`Attr [transform] must contain 16 values` |
| A01-probe-1791886457601 | probe-rot3.snapshot | 18:00:57 +08:00, 1.141s | 200 image/png | responses/…-….png | 已查看：确认列主序顺时针约定 |
| A01-probe-1791886585202 | probe-primitives.snapshot | 18:03:05 +08:00, 3.781s | 200 image/png | responses/…-….png | 已查看：textAlign/字体/borderRadius/变换 |
| A01-render-1791886803566（A01-it00 基线） | operations.snapshot | 18:06:43 +08:00, 4.297s | 200 image/png | baseline.png | 已查看并放大分区：发现右侧重复柱图、缺少两个小图 |
| A01-render-1791887036124（A01-it01） | operations.snapshot | 18:10:36 +08:00, 8.172s | 200 image/png | iter2.png | 已查看并放大：图例与纵轴刻度重叠；折线首点标签裁切 |
| A01-render-1791887217536（A01-it02） | operations.snapshot | 18:13:37 +08:00, 3.219s | 200 image/png | iter3.png | 已查看并放大：图例仍重叠 |
| A01-render-1791887275459（A01-it03） | operations.snapshot | 18:14:35 +08:00, 3.516s | 200 image/png | iter4.png | 已查看并放大：参考线标签与末点标签重叠 |
| A01-render-1791887309955（A01-it04） | operations.snapshot | 18:15:09 +08:00, 2.266s | 200 image/png | iter5.png | 已查看整图 + 4 个分区放大：全部缺陷修复 |

文本宽度测量共 18 次渲染请求（透明底单行文字后取非透明像素包围盒），
用于确认千分位金额与百分比在 17–20px 下的实际宽度，避免表格列溢出。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| it00 → it01 / visual / A01-it00 | 右侧区域重复渲染同一张分组柱图，缺少「访问量与转化率两个共享月份对齐的小图」 | 首版查看整图发现；题面要求两个小图 | 右列改为上下两个 `small_panel`：访问量+订单分组柱、转化率折线 | iter2 查看：小图出现且月份轴对齐；但引入图例重叠与标签裁切 | baseline.png、iter2.png |
| it01 → it02 / visual / A01-it01 | 小图图例与左侧纵轴刻度文字重叠；折线 2026-04 点标签被左边界裁切 | 放大 iter2 右列确认：图例起点距纵轴文字区仅 76px，标签宽 88 超出 spx0 | 新增 `legend_right()`；点标签按 `spx0/spx1` 夹紧；绘图区左右各内缩 `PAD_LBL=44` | iter3 查看：图例仍重叠（右对齐端点仍在纵轴文字区上方） | iter3.png |
| it02 → it03 / visual / A01-it02 | 图例依旧压住纵轴刻度 | iter3 放大确认：面板标题区高度不足，图例无论左右都会落在绘图区顶部 | `small_panel()` 图例下移到副标题行（`y0+40`），`item_w=120` | iter4 查看：图例与刻度不再重叠；但参考线标签压在 2026-09 数据点标签上 | iter4.png |
| it03 → it04 / visual / A01-it03 | 「总体 11.15%」参考线标签与 2026-09 的「11.07%」数据点标签重叠 | iter4 放大确认：两者 y 接近、x 相邻 | 参考线标签从 `spx1-150` 右对齐改为 `spx0+4` 左对齐 | iter5 整图与 4 个分区放大复查：无重叠、无裁切 | iter5.png |
| 能力探针 / syntax-fix / 无 | 首次请求返回 403 `error code: 1010` | 响应体为纯文本错误码；Python `urllib` 默认 UA 被 CDN 拦截 | 在 `post_render()` 中显式设置 `User-Agent: curl/8.5.0` 与 `Accept` | 同一 DSL 立即返回 200 image/png；此经验已固化到共享脚本 | probe.snapshot、responses/A01-probe-1791884795058.txt |
| 能力探针 / syntax-fix / 无 | `PARSE_ERROR: Attr [transform] must contain 16 values` | 手写矩阵多写一个值（17 个） | 依错误信息改为标准 16 值列主序矩阵 | 400 → 200；同时用像素采样反向验证了旋转方向 | probe-rot2.snapshot、probe-rot3.snapshot |

从文档了解到但本次未触发的注意事项：`?errorImage=png` 会把错误改成图片响应，本次未使用；
`Image`/`Emoji` 会发起同步网络请求，本题为纯 DSL 主体，未使用任何外部图片
（自检已断言最终 DSL 中不含 `<Image` 与 `dataUri`）。

## 5. 任务耗时与请求统计

结构化指标文件：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-13T17:46:36.796+08:00 → 2026-10-13T18:28:34.474+08:00 | 含时区时间 | requests.jsonl 最早/最晚记录 |
| 任务总耗时 | 2517.678 | 秒 | 墙钟时间（含文档阅读、脚本编写、查看图片与思考） |
| 首次可用图耗时 | 79.442 | 秒 | 从开始到首次取得可打开的有效图（含 UA 拦截排查） |
| 等待用户反馈 | 0 | 秒 | 预置连续执行模式，无人工反馈等待 |
| 限流等待、排队等待 | 0 / null | 秒 | 未出现 429/503；服务端排队不可测，记 null |
| 已记录请求耗时之和 | 67.358 | 秒 | requests.jsonl（13 次渲染/探针 + 18 次文本测量，含重叠） |
| 成功、失败、重试请求 | 10 / 3 / 0 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 8 / 5 | 次 | iterations.jsonl 及实际图像查看记录 |

墙钟总耗时 2517.678 秒远大于请求耗时之和 67.358 秒，差额为文档阅读、数据计算、
DSL 生成脚本编写与逐区放大查看图片的时间；服务端 `Server-Timing` 另计
（如 `cache;desc=hit, total;dur=4.2`），未与墙钟混算。

## 6. 设计选择、经验与未解决事项

关键设计选择：

- 版面用 `Stack + Positioned` 绝对定位而非 `Row/Column`，因为需要在 1600×1000 内精确控制
  三张图与表格的比例关系，且要保证两个小图共享同一月份轴几何。
- 金额轴用万元（0–22 万元，5 个刻度），转化率单独用 10.0%–12.0% 轴并画总体参考虚线，
  彻底避免百分比与金额共轴。
- KPI 直接保留金额原值（918,624 元）并附万元约数，符合「保留原值或正确转换」。
- 数值文字统一用等宽字体 `Noto Sans Mono CJK SC`，表格右对齐后小数与千分位纵向对齐。
- 折线用旋转矩形（`transform` 矩阵）连接相邻点，是 DSL 内绘制线段的可靠方式；
  矩阵约定通过像素采样实测确认，未依赖猜测。

可复用经验：

1. Python `urllib` 访问 open-snapshot 需显式 `User-Agent`，否则 CDN 返回 403 `error code: 1010`。
2. `transform` 为列主序 4×4；配合 `transformAlignment="TOP_LEFT"` 时
   `(cos,sin,0,0,-sin,cos,0,0,0,0,1,0,0,0,0,1)` 是顺时针旋转。
3. `Text` 的 `textAlign` 取 Skia 的 `LEFT/CENTER/RIGHT`；`softWrap="false" maxLines="1"`
   可保证单行不换行，适合刻度与表格单元格。
4. 透明底渲染单行文字再取包围盒，是测量文字实际宽度的可靠办法，可避免列宽估算溢出。
5. `Container` 出现 `border`/`boxShadow`/`borderRadius` 等装饰属性时会自动构造
   `BoxDecoration` 并合并 `color`，不需要二选一。

未解决事项：无。全部已知缺陷（右侧重复柱图、图例与纵轴重叠、折线标签裁切、
参考线标签压点）均已在迭代中修复并再次渲染复查。

最终图片满足题面全部指定要求的依据：整图与 4 个分区（柱图、两个小图、明细表、结论区）
均实际打开查看；另运行 63 项自动核对（计算值、加权转化率、DSL 中出现的数值、
文件配对、PNG 魔数、无外部图片、无写死机器路径）全部通过。

临时目录中的草稿、备选方案、探针 DSL、请求响应与失败记录均已保留
（`tmp/run-20261013-174209/A01/` 下 `responses/`、`probe-*.snapshot`、`baseline.png`、
`iter2.png`–`iter5.png`、`requests.jsonl`、`iterations.jsonl`），未删除或覆盖。

总任务根的 `.gitignore` 已在启动时创建（见 `.gitignore`），合并自
`templates/gitignore-template.txt` 并补充 Node/编辑器缓存规则；
未忽略 `tmp/`、`outputs/` 或任何图片、DSL、JSON、日志证据。
`__pycache__/`、`*.pyc` 等运行时缓存不列为产物或自检证据。
