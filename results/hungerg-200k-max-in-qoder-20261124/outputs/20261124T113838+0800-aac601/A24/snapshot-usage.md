# A24 Snapshot 使用与自检报告

- 状态：completed
- 运行 ID：`20261124T113838+0800-aac601`
- 输出根：`outputs/20261124T113838+0800-aac601/A24`（path_base=suite_root）
- 临时根：`tmp/20261124T113838+0800-aac601/A24`（path_base=suite_root）
- 服务基址：https://open-snapshot.muedsa.com

## 文档与工具应用

实际读取服务指南、OpenAPI、Parser 语法、标签与文本属性、示例、字体、布局、绘制、错误处理与数据模板文档；原始响应缓存在 `tmp/20261124T113838+0800-aac601/_suite/shared/`。服务请求使用 UTF-8 纯文本 POST `/snapshot`，依据 HTTP 状态、Content-Type、X-Request-Id 与 Server-Timing 留痕。字体从真实 `/fonts` 响应选择 `Noto Sans CJK SC`。主体、图表、文字和几何均由完整 Snapshot DSL 构造。

## 视觉自检

| 检查项 | 结果与证据 |
|---|---|
| schedule | 12任务完整时长、团队资格、半开资源区间与全部依赖逐项通过；完工260分钟，13:20。 |
| bounds | 关键路径255分钟；总工作量485/2=242.5分钟；穷举2338个团队拓扑调度状态证明260分钟为全局最优。 |
| buffer | 420−260=160分钟；执行图显示两团队空档、13:20完工线与16:00截止线。 |
| execution_board | 1920×1080；真实时间同尺度；短任务R02/R12与长中文标签分别查看，编号、团队和起止可读。 |
| decision_brief | 1200×1600；关键链、工程支撑链、跨链闸口、总工时、下界、完工、缓冲、三风险与对策齐全。 |
| action_card | 720×1280；12任务按时间排序，团队、起止、依赖与K1/K2/K3风险提醒齐全。 |
| consistency | 三图由同一schedule.json生成；content-map逐任务记录位置和显示起止；正文最小字号20/24/20。 |
| provenance | 三张最终PNG均与服务原始响应逐字节一致，同名DSL与提交UTF-8请求体一致。 |

## 设计选择

深海蓝执行图配合青色design与紫色engineering；关键路径用绿色强调，剩余缓冲用浅绿区域表达。简报将证明、风险和决策集中呈现；手机卡按真实开始时间排序并保留风险入口。

## 问题、修改与验证

排程审计首先发现R05必须等待R01完成，255分钟关键路径下界不能直接实现。修正后穷举团队串行拓扑顺序，得到260分钟全局最优；R09由design执行，R10/R11于205分钟并行，R12由design在240分钟接续。v001视觉检查发现简报缓冲标题与队名裁切，v002已修正并三图复查通过；无服务重试。

## 交付文件

- `execution-board.png`
- `execution-board.snapshot`
- `decision-brief.png`
- `decision-brief.snapshot`
- `action-card.png`
- `action-card.snapshot`
- `schedule.json`
- `schedule-audit.json`
- `content-map.json`
