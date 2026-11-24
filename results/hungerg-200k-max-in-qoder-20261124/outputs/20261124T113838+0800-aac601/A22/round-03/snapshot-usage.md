# A22 round-03 Snapshot 使用与自检报告

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
| data | 逐月公式、期间汇总、加权率、未舍入图形值及ROUND_HALF_UP展示均由computed-data.json复算。 |
| layout | 1600×1000；八个主区域边界稳定；正文不低于22px；六/七个月完整显示。 |
| chart | 净收入与经营利润共用零起点纵轴；负利润保留并增加负刻度，未裁切或改成正值。 |
| table | 月份、净收入、利润、退款率、转化率逐行对应当前轮数据，金额整数元、百分比两位小数。 |
| visual | 最终服务PNG已实际查看，标题、KPI、柱图、表格和结论无碰撞或信息遗漏。 |
| regression | change-audit.json记录旧新值、传播位置、保留项、区域±2px、数值与真实图像回归。 |

## 设计选择

浅色经营仪表盘：四张KPI卡、单一结论带、左侧共享零轴双柱图、右侧高密度明细表；金额与计数分层显示。

## 问题、修改与验证

新增2026-10并保留两项财务更正，重排七组柱和七行表格；主区域边界保持0px差，实际查看通过。

## 交付文件

- `round-03/dashboard.png`
- `round-03/dashboard.snapshot`
- `round-03/computed-data.json`
- `round-03/layout-map.json`
- `round-03/change-audit.json`
