# A21 Snapshot 使用与自检报告

- 状态：completed
- 运行 ID：`20261124T113838+0800-aac601`
- 输出根：`outputs/20261124T113838+0800-aac601/A21`（path_base=suite_root）
- 临时根：`tmp/20261124T113838+0800-aac601/A21`（path_base=suite_root）
- 服务基址：https://open-snapshot.muedsa.com

## 文档与工具应用

实际读取服务指南、OpenAPI、Parser 语法、标签与文本属性、示例、字体、布局、绘制、错误处理与数据模板文档；原始响应缓存在 `tmp/20261124T113838+0800-aac601/_suite/shared/`。服务请求使用 UTF-8 纯文本 POST `/snapshot`，依据 HTTP 状态、Content-Type、X-Request-Id 与 Server-Timing 留痕。字体从真实 `/fonts` 响应选择 `Noto Sans CJK SC`。主体、图表、文字和几何均由完整 Snapshot DSL 构造。

## 视觉自检

| 检查项 | 结果与证据 |
|---|---|
| rounds | round-01、round-02、round-03均按预置需求连续完成，旧轮完整保留。 |
| images | 6张指定最终PNG及同名DSL均为真实服务响应；每轮两图实际查看。 |
| regression | 标题、日期、讲者、ONLINE LAUNCH、网址与赞助方在后续轮保留；新增英语句位于网址上方。 |
| contrast | round-03两张去文字背景辅助渲染覆盖全部叠层；所有普通文字run≥4.5:1，最差位置已记录。 |
| mode | 预置连续执行模式；未来需求可提前访问，不声称隐藏反馈盲测。 |

## 设计选择

同一四构件品牌系统贯穿三轮；竖版与横屏分别构图，后续轮通过独立信息带和扩大信息面板避免碰撞。

## 问题、修改与验证

第一轮首版通过；第二轮替换长标题并新增赞助信息；第三轮改浅色主题、新增英语句并完成全量对比度审计。

## 交付文件

- `outputs/20261124T113838+0800-aac601/A21/round-01/content-map.json`
- `outputs/20261124T113838+0800-aac601/A21/round-01/design-tokens.json`
- `outputs/20261124T113838+0800-aac601/A21/round-01/launch-portrait.png`
- `outputs/20261124T113838+0800-aac601/A21/round-01/launch-portrait.snapshot`
- `outputs/20261124T113838+0800-aac601/A21/round-01/launch-wide.png`
- `outputs/20261124T113838+0800-aac601/A21/round-01/launch-wide.snapshot`
- `outputs/20261124T113838+0800-aac601/A21/round-01/snapshot-usage.md`
- `outputs/20261124T113838+0800-aac601/A21/round-01/task-metrics.json`
- `outputs/20261124T113838+0800-aac601/A21/round-02/content-map.json`
- `outputs/20261124T113838+0800-aac601/A21/round-02/design-tokens.json`
- `outputs/20261124T113838+0800-aac601/A21/round-02/launch-portrait.png`
- `outputs/20261124T113838+0800-aac601/A21/round-02/launch-portrait.snapshot`
- `outputs/20261124T113838+0800-aac601/A21/round-02/launch-wide.png`
- `outputs/20261124T113838+0800-aac601/A21/round-02/launch-wide.snapshot`
- `outputs/20261124T113838+0800-aac601/A21/round-02/snapshot-usage.md`
- `outputs/20261124T113838+0800-aac601/A21/round-02/task-metrics.json`
- `outputs/20261124T113838+0800-aac601/A21/round-03/content-map.json`
- `outputs/20261124T113838+0800-aac601/A21/round-03/contrast-audit.json`
- `outputs/20261124T113838+0800-aac601/A21/round-03/design-tokens.json`
- `outputs/20261124T113838+0800-aac601/A21/round-03/launch-portrait.png`
- `outputs/20261124T113838+0800-aac601/A21/round-03/launch-portrait.snapshot`
- `outputs/20261124T113838+0800-aac601/A21/round-03/launch-wide.png`
- `outputs/20261124T113838+0800-aac601/A21/round-03/launch-wide.snapshot`
- `outputs/20261124T113838+0800-aac601/A21/round-03/snapshot-usage.md`
- `outputs/20261124T113838+0800-aac601/A21/round-03/task-metrics.json`
- `outputs/20261124T113838+0800-aac601/A21/snapshot-usage.md`
