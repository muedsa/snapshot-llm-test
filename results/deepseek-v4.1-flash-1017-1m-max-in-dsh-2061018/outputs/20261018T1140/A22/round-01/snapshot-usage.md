# A22 round-01 报告

## 结果
- 真实服务 PNG：`round-01/dashboard.png`（1600×1000），DSL：`round-01/dashboard.snapshot`。
- 计算：`computed-data.json`；布局：`layout-map.json`；首轮无 change-audit。
- 计算口径：净收入=收入−退款；利润=净收入−运营成本；退款率=退款/收入；转化率=订单/sessions；汇总先求和再算比率。

## 本轮要点
- 6 个月原始数据：净收入 918,624，利润 262,124，订单 3,045，总体转化率 11.15%；9 月利润 64,368 最高。

## 查看
- 时间：2026-10-18T13:54:05+08:00；文件：`tmp/20261018T1140/A22/round-01/dashboard-r1v3.png`。
- 观察：净收入/利润分组柱、六行表、结论完整；同比更正前。

## 请求
- 本轮 3 次真实渲染（v1 首版、v2 分组柱修复、v3 轴标签间距）；全部 HTTP 200 image/png。
- 请求日志：`tmp/20261018T1140/A22/requests.jsonl`（共 9 次，本轮取 3 次）。
