# A01 Snapshot 使用与自检报告

- 状态：completed
- 运行 ID：`20261124T113838+0800-aac601`
- 输出根：`outputs/20261124T113838+0800-aac601/A01`（path_base=suite_root）
- 临时根：`tmp/20261124T113838+0800-aac601/A01`（path_base=suite_root）
- 服务基址：https://open-snapshot.muedsa.com

## 文档与工具应用

实际读取服务指南、OpenAPI、Parser 语法、标签与文本属性、示例、字体、布局、绘制、错误处理与数据模板文档；原始响应缓存在 `tmp/20261124T113838+0800-aac601/_suite/shared/`。服务请求使用 UTF-8 纯文本 POST `/snapshot`，依据 HTTP 状态、Content-Type、X-Request-Id 与 Server-Timing 留痕。字体从真实 `/fonts` 响应选择 `Noto Sans CJK SC`。主体、图表、文字和几何均由完整 Snapshot DSL 构造。

## 视觉自检

| 检查项 | 结果与证据 |
|---|---|
| 1600×1000 真实 PNG | 通过；PNG 头解析尺寸 1600×1000，字节来自 200 服务响应 |
| 四张 KPI | 通过；总净收入 918,624、总利润 262,124、订单 3,045、加权转化率 11.15% |
| 分组柱图 | 通过；净收入/利润共用 0—24 万元轴，六个月标签完整 |
| 访问与转化双图 | 通过；共享 04—09 月份位置，各自独立单位与刻度 |
| 六行明细 | 通过；金额整数，退款率与转化率两位小数，数字右对齐 |
| 管理结论 | 通过；引用 9月利润、4月利润、6/8月退款率，数值由 CSV 计算 |
| 文字与脚注 | 通过；正文≥20，坐标/脚注≥16，实际打开最终图复看 |
| 审计 JSON | 通过；每月原始分子分母、汇总、轴映射、结论引用齐全 |

## 设计选择

浅色管理驾驶舱；蓝绿承担收入与利润，橙色只突出转化与退款风险。上区 KPI、中部趋势、底部明细与结论形成从结果到原因的阅读路径。

## 问题、修改与验证

初次渲染发现 Text.height 被误当作像素高度，导致文字不可见；依据 Parser 文本文档将其移除，由 Positioned 提供布局尺寸。v002 实际复看确认全部文字、图表和表格恢复，未后处理最终 PNG。

## 交付文件

- `operations.png`
- `operations.snapshot`
- `computed-data.json`
- `snapshot-usage.md`
- `task-metrics.json`
