# A22 Snapshot 使用与自检报告

- 状态：completed
- 运行 ID：`20261124T113838+0800-aac601`
- 输出根：`outputs/20261124T113838+0800-aac601/A22`（path_base=suite_root）
- 临时根：`tmp/20261124T113838+0800-aac601/A22`（path_base=suite_root）
- 服务基址：https://open-snapshot.muedsa.com

## 文档与工具应用

实际读取服务指南、OpenAPI、Parser 语法、标签与文本属性、示例、字体、布局、绘制、错误处理与数据模板文档；原始响应缓存在 `tmp/20261124T113838+0800-aac601/_suite/shared/`。服务请求使用 UTF-8 纯文本 POST `/snapshot`，依据 HTTP 状态、Content-Type、X-Request-Id 与 Server-Timing 留痕。字体从真实 `/fonts` 响应选择 `Noto Sans CJK SC`。主体、图表、文字和几何均由完整 Snapshot DSL 构造。

## 视觉自检

| 检查项 | 结果与证据 |
|---|---|
| rounds | round-01、round-02、round-03按预置需求连续执行，三轮完整保留。 |
| corrections | 第二轮两项财务更正持续有效；第三轮新增2026-10且未恢复旧值。 |
| propagation | 每月、汇总、四KPI、双柱、表格与主结论均由当前轮未舍入值重新计算。 |
| regression | 主区域边界逐轮比较均为0px差；数值公式、轴范围、历史行和实际图像检查通过。 |
| mode | 预置连续执行模式；未来需求可提前访问，不声称隐藏反馈盲测。 |

## 设计选择

同一驾驶舱视觉系统贯穿三轮；通过稳定主区域和可重排内部柱组/行距容纳六个月到七个月。

## 问题、修改与验证

首轮建立数据与布局；第二轮将8月退款改为25048元、9月成本改为208000元并显示负利润；第三轮新增10月并保留前轮更正。

## 交付文件

- `outputs/20261124T113838+0800-aac601/A22/round-01/computed-data.json`
- `outputs/20261124T113838+0800-aac601/A22/round-01/dashboard.png`
- `outputs/20261124T113838+0800-aac601/A22/round-01/dashboard.snapshot`
- `outputs/20261124T113838+0800-aac601/A22/round-01/layout-map.json`
- `outputs/20261124T113838+0800-aac601/A22/round-01/snapshot-usage.md`
- `outputs/20261124T113838+0800-aac601/A22/round-01/task-metrics.json`
- `outputs/20261124T113838+0800-aac601/A22/round-02/change-audit.json`
- `outputs/20261124T113838+0800-aac601/A22/round-02/computed-data.json`
- `outputs/20261124T113838+0800-aac601/A22/round-02/dashboard.png`
- `outputs/20261124T113838+0800-aac601/A22/round-02/dashboard.snapshot`
- `outputs/20261124T113838+0800-aac601/A22/round-02/layout-map.json`
- `outputs/20261124T113838+0800-aac601/A22/round-02/snapshot-usage.md`
- `outputs/20261124T113838+0800-aac601/A22/round-02/task-metrics.json`
- `outputs/20261124T113838+0800-aac601/A22/round-03/change-audit.json`
- `outputs/20261124T113838+0800-aac601/A22/round-03/computed-data.json`
- `outputs/20261124T113838+0800-aac601/A22/round-03/dashboard.png`
- `outputs/20261124T113838+0800-aac601/A22/round-03/dashboard.snapshot`
- `outputs/20261124T113838+0800-aac601/A22/round-03/layout-map.json`
- `outputs/20261124T113838+0800-aac601/A22/round-03/snapshot-usage.md`
- `outputs/20261124T113838+0800-aac601/A22/round-03/task-metrics.json`
- `outputs/20261124T113838+0800-aac601/A22/snapshot-usage.md`


## 终审审计标记更正

- 原始 `round-02/change-audit.json` 保留不覆盖，其中 `prior_corrections_and_rows_retained: false` 是错误标记：它把两项有意数据更正当成未保留字段。
- 当前有效审计为 [change-audit-r002-corrected.json](round-02/change-audit-r002-corrected.json)：从原始 CSV 独立复算，28项未改原始字段在round-01/02/03全部保留，两项允许变更精确应用，六个月公式、期间总量与八个主区域0px边界差全部通过。
- 该更正是审计记录修正，不改变任何最终PNG、DSL或业务数据，也不增加服务渲染请求。
