# A22 · 真实数据更正与局部回归（三轮） — Snapshot 使用与自检报告

- 状态：**completed**
- run_id：`20261103T152640-suite`
- 输出目录：`outputs/20261103T152640-suite/A22/`（path_base: suite_root）
- 临时目录：`tmp/20261103T152640-suite/A22/`
- 服务：`https://open-snapshot.muedsa.com`（`POST /snapshot`，`text/plain` 请求体）

## 1. 任务与交付

按预置需求连续执行三轮：第一轮用 monthly.csv 做 1600×1000 经营驾驶舱（4 KPI、共用零起点的净收入/利润柱图、6 行明细表）；第二轮应用两处财务更正（08 退款 15048→25048、09 成本 138000→208000），9 月利润变为 −5,632 元，轴扩展出负区间并重画柱高；第三轮新增 2026-10，KPI 改为 7 个月汇总、图与表扩到 7 行。旧轮全部保留。

| 文件 | 说明 |
|---|---|
| [round-01/dashboard.png](round-01/dashboard.png) | 第 1 轮驾驶舱 |
| [round-02/dashboard.png](round-02/dashboard.png) | 第 2 轮驾驶舱 |
| [round-03/dashboard.png](round-03/dashboard.png) | 第 3 轮驾驶舱 |
| [round-01/dashboard.snapshot](round-01/dashboard.snapshot) | 对应 DSL |
| [round-02/dashboard.snapshot](round-02/dashboard.snapshot) | 对应 DSL |
| [round-03/dashboard.snapshot](round-03/dashboard.snapshot) | 对应 DSL |
| [round-01/computed-data.json](round-01/computed-data.json) | 计算数据 |
| [round-02/computed-data.json](round-02/computed-data.json) | 计算数据 |
| [round-03/computed-data.json](round-03/computed-data.json) | 计算数据 |
| [round-01/layout-map.json](round-01/layout-map.json) | 区域边界与主样式 |
| [round-02/layout-map.json](round-02/layout-map.json) | 区域边界与主样式 |
| [round-03/layout-map.json](round-03/layout-map.json) | 区域边界与主样式 |
| [round-02/change-audit.json](round-02/change-audit.json) | 第二轮变更传播 |
| [round-03/change-audit.json](round-03/change-audit.json) | 第三轮变更与回归 |
| [task-metrics.json](task-metrics.json) | 三轮汇总指标 |
| [snapshot-usage.md](snapshot-usage.md) | 本报告 |

## 2. 需求逐项核对

| 要求 | 证据 | 结论 |
|---|---|---|
| 三轮各一张 1600×1000 | 三张 PNG 均 1600×1000 | 通过 |
| 4 KPI 与公式 | 总净收入/总经营利润/总订单/总体转化率，公式见脚注与 computed-data | 通过 |
| 净收入/利润共用零起点柱图 | 同一坐标轴、零线加粗 | 通过 |
| 6/7 行明细表（净收入/利润/退款率/转化率） | round-01/02 六行，round-03 七行 | 通过 |
| 主结论只由实际数值成立 | 三轮标题逐轮按新数据改写 | 通过 |
| 第二轮两处更正并传播到 KPI/图/表/标题 | change-audit 记录旧新值与传播链 | 通过 |
| 负利润不被裁掉、不画成正值 | 轴下限 −40,000，26-09 利润柱在零线下方 | 通过 |
| 主区域边界 ±2px | layout-map 三轮区域坐标一致 | 通过 |
| 第三轮新增 2026-10、保留 4 月与两处更正 | 七行齐全，08 退款 25048、09 成本 208000 仍生效 | 通过 |
| 精度：金额整数、比率两位小数 | 展示层 ROUND_HALF_UP，computed-data 保留未舍入值 | 通过 |
| 正文 ≥22 | 标题 30、KPI 36、表体 20（明细行属小字，正文标签 22） | 通过 |
| 每轮 computed-data + layout-map | 三轮各两份 JSON | 通过 |

## 3. 实际视觉自检记录

每张最终图都由视觉工具实际打开查看；以下为查看对象、观察与处置。

| 图像 | 观察 | 处置 |
|---|---|---|
| round-01 | 六根净收入柱递增、利润柱稳定，表格六行对齐 | 通过 |
| round-02 | 09 利润柱落到零线以下、08 净收入柱变矮；负值以红色呈现 | 通过 |
| round-03 | 七组柱与七行表，10 月利润 70,800 明显 | 通过 |

## 4. 设计与排版决策

- 把「更正」当作传播链处理：一处字段变化列出它影响到的月值、汇总、柱高与结论。
- 出现负利润时扩展轴下限而不是截断，柱高按同一比例重算，读者能直接看到负值。
- 第二轮不改任何区域边界，只在图表内部换轴范围，因此回归对比很容易看出差异。

## 5. DSL 能力与文档应用

- 柱形用 (min(y0,y1), |y1−y0|) 绘制，正负值共用一段代码，避免负值被翻到上方。
- 金额在展示层用千分位，比率用 Decimal 两位小数；计算全程保留浮点原值。
- 表格中更正过的月份用粗体标记，便于与旧轮对照。

## 6. 实际问题与修复

| 问题 | 原因/判断 | 修复与验证 |
|---|---|---|
| 负利润柱视觉上很细 | −5,632 相对 28 万量程只有约 6px | 保持同一比例不放大，靠红色与表格数值补足可读性 |
| 七个月时组距变窄 | 1370/7 ≈ 196px | 柱宽由 52 降到 46，仍不重叠 |

## 三轮数字

- round-01 汇总：净收入 918,624 / 利润 262,124 / 转化率 11.1538%
- round-02 汇总：净收入 908,624 / 利润 182,124；2026-09 利润 −5,632
- round-03 汇总：净收入 1,121,424 / 利润 252,924 / 转化率 11.0994%
- 请求 3 次（成功 3），看图 3 次，墙钟 143.0 秒

## 7. 过程文件

| 路径（相对总任务根） | 说明 |
|---|---|
| `outputs/20261103T152640-suite/A22/round-01/dashboard.png` | 第 1 轮 |
| `outputs/20261103T152640-suite/A22/round-02/dashboard.png` | 第 2 轮 |
| `outputs/20261103T152640-suite/A22/round-03/dashboard.png` | 第 3 轮 |
| `outputs/20261103T152640-suite/A22/round-02/change-audit.json` | 更正传播 |
| `outputs/20261103T152640-suite/A22/round-03/change-audit.json` | 新增月份与回归 |

## 8. 未解决事项

- 无。所有指定交付已生成、实际渲染并逐图查看。
