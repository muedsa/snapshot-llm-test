# A22 使用报告（三轮累计）

> 预置三轮连续执行：round-01（TASK.md）→ round-02（财务更正）→ round-03（新增月份），
> 全程不等待用户消息。后续轮需求在第一轮开始前即可访问。

生成时间：2026-10-13T09:16:26+08:00

## 1. 三轮完成状态

| 轮次 | 需求来源 | 状态 |
|---|---|---|
| round-01 | TASK.md | 完成 |
| round-02 | rounds/round-02.md | 完成 |
| round-03 | rounds/round-03.md | 完成 |

## 2. 全部最终图片

| 轮次 | PNG | DSL | 尺寸 |
|---|---|---|---|
| round-01 | `round-01/dashboard.png` | `round-01/dashboard.snapshot` | 1600×1000 |
| round-02 | `round-02/dashboard.png` | `round-02/dashboard.snapshot` | 1600×1000 |
| round-03 | `round-03/dashboard.png` | `round-03/dashboard.snapshot` | 1600×1000 |

## 3. 累计值演进

| 指标 | round-01 | round-03 |
|---|---|---|
| 月份数 | 6 | 7 |
| 总净收入 | 918,624 元 | 1,121,424 元 |
| 总经营利润 | 262,124 元 | 252,924 元 |
| 总订单 | 3,045 | 3,685 |
| 总 sessions | 27,300 | 33,200 |
| 总体转化率 | 11.15% | 11.10% |
| 总体退款率 | 5.79% | 6.47% |

## 4. 关键工程结论

- **更正不回写原始 CSV**：三轮的更正都以 `applied_changes`（旧值/新值/来源轮次）记录，
  `source_csv.modified = false`。
- **更正必须重跑整条计算链**：一次 `refund_amount` 修订会同时改变净收入、利润、
  退款率、期间合计、柱高、结论文本；只改表格数字会留下不一致的图。
- **`textAlign` 需要大写枚举**（A23 复查后更正）：`START`/`CENTER`/`END`/`JUSTIFY`/
  `LEFT`/`RIGHT` 有效，小写返回 400。本题三轮是在误判该属性不可用的前提下改用坐标计算
  实现对齐的，数字列经整屏查看对齐正确；改用 `textAlign="END"` 可由段落排版保证对齐。
- **负值必须真正画出来**：round-02 出现 −5,632 元后，轴在同一图表区域内展开到
  [−4万, 24万]，利润柱改用负值配色并整根落在零线之下，
  由 `bar_height_pixel_audit` 从最终 PNG 反测证明（实测 5px vs 期望 5.23px）。
- **主区域边界三轮 0px 偏移**，内部行高/刻度按各轮允许范围重排。

## 5. 目录

- 题目输出根：`outputs/run-20261011-01/A22/`（含 `round-01/`–`round-03/` 与本报告、累计指标）
- 题目临时根：`tmp/run-20261011-01/A22/`（`drafts/round-01..03/`、`preview/`、`responses/`、`requests.jsonl`）

## 6. 未解决事项

见各轮报告第 10 节；累计层面无跨轮阻塞。
