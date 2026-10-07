# A01 · 六个月经营诊断驾驶舱 — Snapshot 使用报告

- 任务：A01（数据叙事 / advanced）
- run_id：`20261004-182918`
- 输出目录：`outputs/20261004-182918/A01/`
- 临时目录：`tmp/20261004-182918/A01/`
- 状态：**completed**

## 1. 实际使用的文档与字体

| 类型 | 来源 | 结果 |
|---|---|---|
| 服务使用指南 | `https://open-snapshot.muedsa.com/ai-guide.md` | 200，落盘 `tmp/.../_suite/docs/ai-guide.md` |
| 接口定义 | `https://open-snapshot.muedsa.com/openapi.yaml` | 200，落盘 `tmp/.../_suite/docs/openapi.yaml` |
| 标签与属性参考 | `https://snapshot.muedsa.com/reference/parser-tags/` | 已实际读取并据此编写 DSL |
| 类 DOM 解析器说明 | `https://snapshot.muedsa.com/guides/parser/` | 已实际读取 |
| 字体列表 | `GET /fonts` | 200，落盘 `tmp/.../_suite/fonts-list.txt` |

字体全部取自 `/fonts` 真实返回，未臆造：

- `Inter`（拉丁数字、英文月份标签）
- `Noto Sans CJK SC`（全部中文正文，声明为 `fontFamily="Inter,Noto Sans CJK SC"` 让 Inter 优先、缺字回退）
- `DejaVu Sans Mono`、`DejaVu Serif`、`Noto Serif CJK SC` 本题未使用

## 2. 实际使用到的标签与属性

`Snapshot`（`type`、`background`）、`Container`（`color`、`borderRadius`+四角 `borderRadiusTopLeft/...`、`border`、`boxShadow`、`gradientType/gradientColors/gradientStops/gradientBegin/gradientEnd`、`opacity`）、`Stack`（`fit="EXPAND"`）、`Positioned`（`left/top/width/height`）、`ClipRRect`（在探针中验证圆角裁剪）、`Text`（`text`、`color`、`fontSize`、`fontFamily`、`fontStyle`、`textAlign`、`maxLines`）。

**服务实测得到的关键约束（不是文档抄写，是踩出来的）：**

1. `Positioned` 必须恰好有一个子节点，且子节点不能为空 → `<Positioned .../>` 会返回
   `400 RENDER_ERROR: ProxyWidget has no widget, can not create render box`。
   因此所有矩形都写成 `Positioned > Container(...)`。
2. `Text` 若同时给了小于换行后实际行高的 `height` 和 `maxLines`，会**整段不渲染**（无任何报错）。
   本题“管理结论”三条证据和“下一步”一开始全部空白，就是这个原因；去掉 `Text` 上的 `height` 后正常。
3. `Text` 的 `fontFamily` 多字体串按整体处理，回退发生在单个字符缺字时，`Inter,Noto Sans CJK SC` 可正常混排。

## 3. 构图与设计决策

- **绝对定位优先**：整屏用一个 `Stack`，每个元素都是 `Positioned`，因此 DSL 里的坐标就是脚本算出的坐标，不存在 Flex 布局的隐式分配误差。柱高＝`value / 240000 × 绘图区高`，与 `computed-data.json` 中的轴定义同源。
- **三个数轴严格分离**：金额（0–24 万）、访问次数（0–8,000 次）、百分比（0–20%）各有自己的刻度与单位标注，柱图两个系列共用同一零起点线性刻度，不存在百分比与金额混轴。
- **视觉重点**：深色顶栏 + 四张 KPI（左侧色条区分语义）+ 一张大柱图 + 两张共享月份对齐的小图 + 明细表 + 深色结论卡。结论卡用深底反白，和数据卡形成主次。
- **不堆数字**：柱图只在净收入柱上方标原值（主系列），经营利润逐月值放在明细表；小图用顶部数值带代替每点标签，避免与刻度打架。
- **正文字号**：明细表与结论证据 20px；KPI 主数值 34px；脚注/刻度/轴标签 16–18px，满足“正文≥20、脚注≥16”。

## 4. 数据口径（全部写入 computed-data.json）

- 净收入 = 收入 − 退款；经营利润 = 净收入 − 经营成本（成本不含退款）。
- 退款率 = 退款 ÷ 退款前收入（逐月）。
- 月度转化率 = 订单 ÷ 访问次数（逐月）；**期间总体转化率 = 3,045 ÷ 27,300 = 11.15%**，不是六个月比例的算术平均（算术平均为 11.19%，题目明确要求用总 ÷ 总）。
- 汇总：总净收入 918,624 元、总经营利润 262,124 元、总订单 3,045 笔、总访问 27,300 次、总退款 56,426 元、总成本 656,500 元。
- 无负值月份；柱图仍以 0 为基线，负值处理方式记录在 `axis_definitions.bar_chart.negative_handling`。

## 5. 逐图自检（operations.png，1600×1000）

| 检查项 | 结果 |
|---|---|
| 四张 KPI | 总净收入 918,624 元 / 总经营利润 262,124 元 / 总订单 3,045 笔 / 期间总体转化率 11.15%，均为原值或正确总量，无错误换算 |
| 分组柱图 | 6 个月 × 2 系列 = 12 根柱，共用 0–24 万零起点；图例、刻度、单位、月份标签齐全；最后一个月 2026-09 标签与柱体完整 |
| 两张小图 | 访问量与转化率 x 起点、槽宽、标签位置完全一致（月份对齐）；各自独立数轴并注明“非金额” |
| 明细表 | 6 行 × 5 列；金额为整数带千分位；比例为两位小数百分比；退款率 ≥8% 与低于期间利润率的月份用红色标出 |
| 管理结论 | 一条结论 + 三条带数字的证据 + 一条下一步，全部数值可在 computed-data.json 中核对 |
| 字号 | 正文（表格、结论、KPI 数值）≥20px；脚注/轴标签 ≥16px |
| 无重叠/截断 | 逐块放大核对：结论卡、表格卡、表头单位注、结论“下一步”均已确认完整显示 |

放大核对过的局部（临时目录 `crops/`）：`operations-concl.png`、`operations-right.png`、`operations-table.png`、`operations-tnote2.png`、`operations-conc2.png`。

## 6. 遇到的问题与修复

| # | 问题 | 定位方式 | 修复 |
|---|---|---|---|
| 1 | 首次请求 `400 PARSE_ERROR: Tag Positioned only can have one child` | 服务错误 JSON 指出位置 15919 | 面积填充辅助函数不再用 `Positioned` 包裹多子节点，直接输出并列矩形 |
| 2 | `400 RENDER_ERROR: ProxyWidget has no widget` | 二分探针（t1–t6）定位到“空的 Positioned” | 所有矩形改为 `Positioned > Container` |
| 3 | 柱图数值标签压在蓝柱上不可读 | 打开整图 | 标签移到柱顶上方 |
| 4 | 结论卡三条证据与下一步完全空白 | 打开整图 + 裁切放大结论卡 | 读回生成的 DSL 发现 `Text` 同时带 `height="22"` 与 `maxLines="2"`，去掉 `Text` 的 `height` |
| 5 | 小图单位注画到了 y=0（页面右上角） | 打开整图 | 调用漏传 `y`，补 `y=y+15` |
| 6 | 表格“转化率”列越过卡片右边界 16px | 裁切放大表格 | 列宽 216 → 176，右边界对齐表格内边距 |
| 7 | 表头单位注、结论“下一步”文字被截断 | 裁切放大 | 缩短文案并加宽文本框（单行高度不足时溢出会被丢弃，不会换行显示） |
| 8 | 小图 5 条刻度在 68px 高的绘图区里文字互相重叠 | 打开整图 | 改为 3 条刻度（0 / 中值 / 上限），把绘图区高度让给曲线 |
| 9 | 左卡脚注与月份标签重叠 | 打开整图 | 绘图区下边界上移 24px，脚注单独占底部一行 |

## 7. 未解决事项与如实说明

- 无功能性未解决项。
- **过程日志的一处已知瑕疵**：`tmp/20261004-182918/A01/requests.jsonl` 中前 10 条渲染请求的 `request_id` 都写成
  `A01-req-001`。原因是最初的编号计数器只存在于单个 Python 进程内，而本题的生成脚本每次运行只发一次请求。
  已修复 `snapkit.next_id()`（改为扫描 `requests.jsonl` 取最大序号），第 11 条起编号唯一。历史条目未改写，按原样保留。
- 迭代日志 `iterations.jsonl` 中 v01–v07 为**事后按真实过程补写**的合并记录：初次生成脚本自动写入的占位条目
  （`observed_issue`/`viewed_at` 为 null）已被替换为实际观察到的问题、实际查看时间与实际修改。查看图像的次数以本节第 5 条为准。
- token、图像输入量、费用：平台与服务均未提供可引用的计量，`task-metrics.json` 中一律为 `null`，未按字数估算。

## 8. 文件清单

输出目录 `outputs/20261004-182918/A01/`：

- `operations.png`（1600×1000，服务真实响应，未做任何后处理）
- `operations.snapshot`（与图同名的完整 DSL）
- `computed-data.json`（逐月计算值、汇总、轴定义、结论引用数值）
- `snapshot-usage.md`（本文件）
- `task-metrics.json`

临时目录 `tmp/20261004-182918/A01/`：

- `build_a01.py`（唯一 DSL 生成脚本，数据 → 几何 → DSL 同源）
- `build-a01.snapshot`（生成脚本落盘的 DSL 副本）
- `requests.jsonl`（10 次渲染请求，1 次失败 / 9 次成功）
- `iterations.jsonl`（7 条迭代记录）
- `responses/`（失败响应的原始 JSON）
- `crops/`（放大核对用的局部截图）