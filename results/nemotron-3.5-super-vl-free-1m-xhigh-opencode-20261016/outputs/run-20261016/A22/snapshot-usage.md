# A22 Snapshot 使用报告（三轮汇总）

## 任务概述
- 任务ID: A22
- 标题: 真实数据更正与局部回归（自动三轮版本）
- 执行模式: 预置连续执行三轮
- 画布尺寸: 1600×1000 (三轮不变)
- 数据源: inputs/monthly.csv

## 三轮执行摘要

### Round 01 (基线)
- 6个月数据 (2026-04 至 2026-09)
- 总净收入 918,624元, 总经营利润 262,124元
- 总订单 3,045笔, 总体转化率 11.15%
- 交付: dashboard + computed-data + layout-map

### Round 02 (财务更正)
- 2026-08 refund_amount: 15,048 → 25,048
- 2026-09 operating_cost: 138,000 → 208,000
- 2026-09 利润为负 (-5,632元)，柱图增加负轴范围
- 总净收入 908,624元, 总经营利润 182,124元
- 交付: dashboard + computed-data + layout-map + change-audit

### Round 03 (新增月份)
- 新增 2026-10: orders=640, revenue=224,000, profit=70,800 (恢复盈利)
- 7个月汇总 (2026-04 至 2026-10)
- 总净收入 1,121,424元, 总经营利润 252,924元
- 总订单 3,685笔, 总体转化率 11.10%
- 交付: dashboard + computed-data + layout-map + change-audit

## 计算口径
- 净收入 = gross_revenue − refund_amount
- 经营利润 = 净收入 − operating_cost
- 退款率 = refund_amount / gross_revenue
- 月转化率 = orders / sessions
- 总体转化率 = 总orders / 总sessions
- 金额整数元，百分比两位小数

## 视觉回归
三轮主区域边界位置保持±2px，负轴范围在 R2 引入后 R3 保留，数据连续累加。

## 交付文件
Round 01: round-01/dashboard(.png/.snapshot), computed-data.json, layout-map.json, snapshot-usage.md, task-metrics.json
Round 02: round-02/dashboard(.png/.snapshot), computed-data.json, layout-map.json, change-audit.json, snapshot-usage.md, task-metrics.json
Round 03: round-03/dashboard(.png/.snapshot), computed-data.json, layout-map.json, change-audit.json, snapshot-usage.md, task-metrics.json
汇总: snapshot-usage.md, task-metrics.json

## 未解决事项
无。
