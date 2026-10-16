# A22 Round 01 Snapshot 使用报告

## 轮次概述
- 任务ID: A22
- 轮次: round-01
- 标题: 真实数据更正与局部回归（第1轮）
- 画布: 1600×1000
- 数据源: inputs/monthly.csv (6个月: 2026-04 至 2026-09)

## 计算口径
- 净收入 = gross_revenue − refund_amount
- 经营利润 = 净收入 − operating_cost
- 退款率 = refund_amount / gross_revenue
- 月转化率 = orders / sessions
- 总体转化率 = 总orders / 总sessions (不平均各月百分比)
- 金额保留整数元，百分比保留两位小数

## Round 01 数据
| 月份 | 净收入 | 利润 | 退款率 | 转化率 |
|------|--------|------|--------|--------|
| 2026-04 | 119,700 | 37,700 | 5.00% | 12.00% |
| 2026-05 | 135,470 | 41,970 | 5.00% | 11.22% |
| 2026-06 | 126,914 | 27,914 | 8.00% | 10.60% |
| 2026-07 | 161,120 | 49,120 | 5.00% | 11.28% |
| 2026-08 | 173,052 | 41,052 | 8.00% | 10.96% |
| 2026-09 | 202,368 | 64,368 | 4.00% | 11.07% |

汇总: 总净收入 918,624元, 总经营利润 262,124元, 总订单 3,045笔, 总体转化率 11.15%

## 交付文件
- outputs/run-20261016/A22/round-01/dashboard.png (1600×1000)
- outputs/run-20261016/A22/round-01/dashboard.snapshot
- outputs/run-20261016/A22/round-01/computed-data.json
- outputs/run-20261016/A22/round-01/layout-map.json
- outputs/run-20261016/A22/round-01/snapshot-usage.md
- outputs/run-20261016/A22/round-01/task-metrics.json

## 视觉自检
- 四KPI卡片 (总净收入/总经营利润/总订单/总体转化率)
- 净收入/利润共用零起点柱图
- 六行月度明细表
- 基于实际数据的主结论
- 正文≥22px
