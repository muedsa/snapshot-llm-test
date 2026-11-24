# A07 Snapshot 使用与自检报告

- 状态：completed
- 运行 ID：`20261124T113838+0800-aac601`
- 输出根：`outputs/20261124T113838+0800-aac601/A07`（path_base=suite_root）
- 临时根：`tmp/20261124T113838+0800-aac601/A07`（path_base=suite_root）
- 服务基址：https://open-snapshot.muedsa.com

## 文档与工具应用

实际读取服务指南、OpenAPI、Parser 语法、标签与文本属性、示例、字体、布局、绘制、错误处理与数据模板文档；原始响应缓存在 `tmp/20261124T113838+0800-aac601/_suite/shared/`。服务请求使用 UTF-8 纯文本 POST `/snapshot`，依据 HTTP 状态、Content-Type、X-Request-Id 与 Server-Timing 留痕。字体从真实 `/fonts` 响应选择 `Noto Sans CJK SC`。主体、图表、文字和几何均由完整 Snapshot DSL 构造。

## 视觉自检

| 检查项 | 结果与证据 |
|---|---|
| 1600×1000 全网图 | 通过；Read 查看最终 network-map.png，16 站与换乘关系完整。 |
| 720×1280 旅行卡 | 通过；Read 查看最终 travel-card.png，3 条普通旅程与 Q2 无障碍替代完整。 |
| 线路与角度 | 通过；程序验证所有绘制段为水平、垂直或 45°，见 tmp/geometry.json。 |
| 路线最优性 | 通过；(站,线路) 状态 Dijkstra，按(区间数,换乘数)字典序；Q1=6/1，Q2=6/1，Q3=4/1。 |
| 无障碍约束 | 通过；S03/S05/S09/S14 可途经不可端点或换乘；Q2 替代为 6 区间/2 换乘，在 S08 与 S04 换乘。 |
| 审计与留痕 | 通过；routes.json 含 queries/accessibility/optimality/content_map；请求、失败响应、DSL、查看记录均保留。 |

## 设计选择

统一灰白底、深墨文字与 R/B/G 三色系统。地图用字母、颜色、换乘大圆点和绿色/琥珀无障碍标记，旅行卡用相同色系与清晰指标。非地理示意明确，线路转折仅 45°/90°。

## 问题、修改与验证

首次请求因在 Container 内直接放 Positioned 返回 400 renderBox.parentData must be StackParentData；改为 Text 后两次成功。布局阶段程序发现一条斜段不为 45°，在渲染前调整坐标并通过断言。实际查看两张基线后未发现影响交付的视觉缺陷，直接将原始字节复制为最终文件并再次查看。

## 交付文件

- `network-map.png`
- `network-map.snapshot`
- `travel-card.png`
- `travel-card.snapshot`
- `routes.json`
- `snapshot-usage.md`
- `task-metrics.json`
