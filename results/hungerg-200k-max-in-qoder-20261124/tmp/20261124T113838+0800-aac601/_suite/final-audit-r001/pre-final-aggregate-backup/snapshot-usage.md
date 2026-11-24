# 全套 Snapshot 使用、经验与终审

- 运行 ID：`20261124T113838+0800-aac601`
- 当前状态：`in_progress`
- 输出：`outputs/20261124T113838+0800-aac601/_suite`；临时：`tmp/20261124T113838+0800-aac601/_suite`（path_base=suite_root）
- 根缓存规则：[.gitignore](../../../.gitignore)，仅排除运行时缓存，不排除 `outputs/`、`tmp/` 与过程证据。

## 实际应用

真实读取并缓存 Open Snapshot 指南、OpenAPI、Parser 语法、标签、文本、示例、字体、媒体、绘制、布局、错误处理与数据模板。全部主体通过 UTF-8 纯文本 `<Snapshot>` DSL 提交 `/snapshot`；最终 PNG 保留服务原始字节。逐题报告记录数据/几何核对、实际图像查看、问题、修复与交付。

## 跨题经验

1. `Text.height` 是行高倍数而非像素高度；文字盒高度应由 `Positioned`/布局容器控制。
2. `Positioned` 必须直接位于 `Stack`；旋转线段使用 `Container.transform`，不把 `Positioned` 套在 `Transform` 内。
3. Parser 不解码 HTML 实体；动态文本按 CDATA/转义规则生成。边框使用 `1 SOLID #RRGGBB`。
4. 字体以 `/fonts` 实际响应为准，本套使用 `Noto Sans CJK SC`。服务文档版本不等于部署版本，新增能力均经真实渲染验证。
5. 金额轴与比例轴分离；加权比例先汇总分子分母；多轮修改保留前轮，不覆盖历史。

## 终审

- 任务完成：26/30；partial 0；blocked 0；pending 4。
- 最终 PNG：84（最低 124）；B类独立作品：20。
- A21 已完成轮次：round-01, round-02, round-03。
- A22 已完成轮次：round-01, round-02, round-03。
- 渲染请求：211；成功 194；失败 17；重试 0。
- 实际查看记录：234；完整视觉迭代：133。
- 墙钟耗时：15436.996 秒；包含等待与执行间隙，不等同于净工作或请求耗时之和。
- 自动审计问题：5。详见 [audit-report.json](audit-report.json) 与 [task-metrics.json](task-metrics.json)。

## 未解决事项

- B02: task-metrics.wall_clock_seconds 缺失或为负
- B03: 任务尚未执行
- B04: 任务尚未执行
- B05: 任务尚未执行
- B06: 任务尚未执行
