# 全套 Snapshot 使用、经验与终审

- 运行 ID：`20261124T113838+0800-aac601`
- 当前状态：`completed`
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

## 终审更正留痕

- B03三份历史图片清单的机器路径保留原样，当前有效清单为 `final-image-inventory-r004-portable.json`；九条迭代路径错误由 `iteration-path-corrections-r001.json` 精确映射，原始日志未改。
- A22第二轮原变更审计的错误失败标记保留；当前有效后继 `round-02/change-audit-r002-corrected.json` 独立复算28项未改字段、全部公式与八个主区域0px边界差，详见 [A22报告](../A22/snapshot-usage.md)。
- B06重复完成事件保留并注明为同一任务完成，不重复计请求或工作量。
- 指标r005将预置需求变更从视觉迭代中分离；image_views按唯一服务响应及SHA-256识别来源，A18同响应预览/版本路径去重，A01/A09复制路径及B04两个覆盖前基线已校正，总计247个来源。基线接受61与失败62依据 `baseline-classification-r005.json` 逐行语义核对，不再使用文本前缀；A01 v001实际查见的裁切缺陷以失败覆盖项补记，v002误标版本按真实服务字节纠正。历史viewed_at补记与实际Read时间分列，原始迭代日志未改；B05两次研究404计入document_requests，不计other_service_requests。
- 终审前的过期全套汇总已归档至 `tmp/20261124T113838+0800-aac601/_suite/final-audit-r001/pre-final-aggregate-backup`；本目录内现行汇总由全部30题重新生成。

## 终审

- 任务完成：30/30；partial 0；blocked 0；pending 0。
- 最终 PNG：124（最低 124）；B类独立作品：60。
- A21 已完成轮次：round-01, round-02, round-03。
- A22 已完成轮次：round-01, round-02, round-03。
- 渲染请求：304；成功 283；失败 21；重试 0；文档请求 15；其他服务请求 1（类别互斥）。
- 实际查看记录：247 个不同服务图像来源；真实服务读取事件 257；重复读取 10；检查衍生图读取 91。
- 完整视觉迭代：86；未完成视觉迭代 11（均为已修复的历史中间版，不代表最终未解决缺陷）；预置需求变更 9（单列，不混入视觉迭代）；基线接受 61；失败基线 62；最终复核 60。
- 未查看服务基线 5 为实验性历史基线，不计入最终交付；124张指定最终图已全部由渲染后真实Read证据核验。
- 逐件查看证据：`tmp/20261124T113838+0800-aac601/_suite/final-audit-r001/all-final-view-audit-r002.json`；总览接触表不替代124张服务原图逐件查看。
- 墙钟耗时：29392.29 秒；包含等待与执行间隙，不等同于净工作或请求耗时之和。
- 自动审计问题：0。详见 [audit-report.json](audit-report.json) 与 [task-metrics.json](task-metrics.json)。

## 未解决事项

无。
