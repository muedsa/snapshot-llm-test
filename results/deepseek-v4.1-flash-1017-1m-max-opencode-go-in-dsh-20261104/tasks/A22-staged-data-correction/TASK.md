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

## 交付路径与轮次归属

本题 task.json 的 required_outputs（PNG/DSL）、additional_outputs（专用审计）、
common_outputs（报告/指标）均使用相对本题输出根的完整路径，顶层列出全部最终交付。
rounds 内的同名字段是顶层清单按轮次划分的子集；output_subdirectory 仅表示归属目录，
不能再次拼接到这些已带 round-XX/ 的路径前。同一个路径只交付一次。
snapshot-usage.md 与 task-metrics.json 位于本题输出根，汇总三轮；每轮另有
round-XX/snapshot-usage.md 与 round-XX/task-metrics.json，只记录该轮。
专用审计仅在清单指定的轮次目录交付，不另在输出根复制一份。

## 三轮共同计算与显示口径

金额单位为元，orders为订单笔数，sessions为访问次数。gross_revenue为退款前收入，
refund_amount为当月退款，operating_cost不含退款。每月净收入=gross_revenue−refund_amount，
经营利润=净收入−operating_cost；退款率=refund_amount/gross_revenue，
月转化率=orders/sessions。期间汇总先分别求和；总体转化率=总orders/总sessions，
总体退款率（若展示）=总refund_amount/总gross_revenue，不平均各月百分比。
计算及computed-data.json保留原金额整数、各比率的分子/分母与未按展示精度舍入的计算值；
先用未舍入值计算汇总、差额与图形比例，最后才格式化展示。
明细金额以整数元显示，订单和访问量为整数；百分比统一保留两位小数。
KPI金额可保留整数元，或除以10000后保留两位小数并明确“万元”；
展示使用十进制四舍五入（恰好半单位时绝对值增大），图轴单位与缩放须明确。
第二、三轮继承以上公式与精度；只应用轮次指定的数据更正或新增月份，不修改原始CSV。

## 专用审计JSON字段

本题指定的专用JSON须遵循[最小字段约定](templates/audit-fields.json)，可增加字段；
该文件只解释结构、单位、坐标/路径基准及证据要求，不是已完成答案。多轮任务复用
同名文件的字段约定，仍按task.json各轮完整路径交付；不要在输出根增加重复文件。

## 后续轮次

第一轮实际完成、看图、保存后，自动读取 [第二轮](rounds/round-02.md)；第二轮归档后自动读取 [第三轮](rounds/round-03.md)。全部需求预置可访问，报告注明连续执行模式。

## 全部最终图片

| PNG与同名DSL | 尺寸 |
|---|---|
| `round-01/dashboard.png` + `round-01/dashboard.snapshot` | 1600×1000 |
| `round-02/dashboard.png` + `round-02/dashboard.snapshot` | 1600×1000 |
| `round-03/dashboard.png` + `round-03/dashboard.snapshot` | 1600×1000 |

各轮额外文件和报告/指标见task.json的rounds。任务输出根另有三轮累计snapshot-usage.md与task-metrics.json。保留所有旧轮，三轮完成后继续总任务下一题。

## 全部审计文件与报告

| 相对本题输出根的路径 | 归属 |
|---|---|
| `round-01/computed-data.json` | round-01 |
| `round-01/layout-map.json` | round-01 |
| `round-02/computed-data.json` | round-02 |
| `round-02/layout-map.json` | round-02 |
| `round-02/change-audit.json` | round-02 |
| `round-03/computed-data.json` | round-03 |
| `round-03/layout-map.json` | round-03 |
| `round-03/change-audit.json` | round-03 |
| `snapshot-usage.md` | 三轮任务汇总 |
| `task-metrics.json` | 三轮任务汇总 |
| `round-01/snapshot-usage.md` | round-01 |
| `round-01/task-metrics.json` | round-01 |
| `round-02/snapshot-usage.md` | round-02 |
| `round-02/task-metrics.json` | round-02 |
| `round-03/snapshot-usage.md` | round-03 |
| `round-03/task-metrics.json` | round-03 |
