> 全套运行说明：本题由总根入口自动执行。遵循 [总AGENTS.md](../../AGENTS.md)，
> 使用同一run_id的 `outputs/<run_id>/A22/` 和 `tmp/<run_id>/A22/`。
> 单题完成后继续总清单下一题，不等待逐题确认；本题内容要求保持有效。

# A22 · 真实数据更正与局部回归（自动三轮版本）

## 第一轮与执行顺序

本题按预置要求自动执行三轮。先完成第一轮：用 inputs/monthly.csv 制作1600×1000经营驾驶舱，公式、KPI、
图表和表格要求与本题以下说明一致。四KPI为总净收入、总经营利润、总订单、
总体转化率；净收入=收入−退款，利润=净收入−operating_cost；总体率=总订单/
总sessions。图中有净收入/利润共用零起点柱图、六行月份/净收入/利润/退款率/
转化率表，以及仅根据实际数值成立的主结论。所有月份原样，正文≥22。
在 round-01/ 交付 dashboard.png/.snapshot、computed-data.json 和 layout-map.json
（KPI、图、表、标题区域的边界及主样式）。生成脚本和参数留在临时目录。
实际查看图并归档第一轮后，立即读取rounds/round-02.md应用修订并完成第二轮，
再读取rounds/round-03.md完成第三轮，不等待用户消息。后续在已有作品上更新，
保留旧版、真实计算与视觉回归证据。每轮报告/指标与三轮任务汇总按AGENTS保存。

## 后续轮次

第一轮实际完成、看图、保存后，自动读取 [第二轮](rounds/round-02.md)；第二轮归档后自动读取 [第三轮](rounds/round-03.md)。全部需求预置可访问，报告注明连续执行模式。

## 全部最终图片

| PNG与同名DSL | 尺寸 |
|---|---|
| `round-01/dashboard.png` + `round-01/dashboard.snapshot` | 1600×1000 |
| `round-02/dashboard.png` + `round-02/dashboard.snapshot` | 1600×1000 |
| `round-03/dashboard.png` + `round-03/dashboard.snapshot` | 1600×1000 |

各轮额外文件和报告/指标见task.json的rounds。任务输出根另有三轮累计snapshot-usage.md与task-metrics.json。保留所有旧轮，三轮完成后继续总任务下一题。
