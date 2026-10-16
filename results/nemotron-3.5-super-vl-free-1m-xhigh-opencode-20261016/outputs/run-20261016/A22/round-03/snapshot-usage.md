# A22 Round 03 Snapshot 使用报告

## 轮次概述
- 任务ID: A22
- 轮次: round-03
- 基于: round-02 数据更正，新增2026-10
- 画布: 1600×1000 (保持±2px)
- 数据: 7个月 (2026-04 至 2026-10)

## 新增数据
2026-10: orders=640, gross_revenue=224,000, refund_amount=11,200, operating_cost=142,000, sessions=5,900
- 净收入: 212,800元
- 利润: 70,800元 (恢复盈利)
- 退款率: 5.00%
- 转化率: 10.85%

## 7个月汇总
| 指标 | 数值 |
|------|------|
| 总净收入 | 1,121,424元 |
| 总经营利润 | 252,924元 |
| 总订单 | 3,685笔 |
| 总体转化率 | 11.10% |

## 变更内容
- Round 02 两项更正继续有效 (2026-08 退款额, 2026-09 运营成本)
- KPI改成7个月期间汇总
- 图与表包括全部7个月
- 最后月份指2026-10
- 主区域边界维持上一轮±2px
- 负轴范围保留 (显示2026-09亏损)

## 交付文件
- outputs/run-20261016/A22/round-03/dashboard.png (1600×1000)
- outputs/run-20261016/A22/round-03/dashboard.snapshot
- outputs/run-20261016/A22/round-03/computed-data.json
- outputs/run-20261016/A22/round-03/layout-map.json
- outputs/run-20261016/A22/round-03/change-audit.json
- outputs/run-20261016/A22/round-03/snapshot-usage.md
- outputs/run-20261016/A22/round-03/task-metrics.json

## 视觉回归
三轮数据连续，旧数据保留，新数据累加，主区域边界位置一致。
