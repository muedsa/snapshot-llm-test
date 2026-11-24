# A11 Snapshot 使用与自检报告

- 状态：completed
- 运行 ID：`20261124T113838+0800-aac601`
- 输出根：`outputs/20261124T113838+0800-aac601/A11`（path_base=suite_root）
- 临时根：`tmp/20261124T113838+0800-aac601/A11`（path_base=suite_root）
- 服务基址：https://open-snapshot.muedsa.com

## 文档与工具应用

实际读取服务指南、OpenAPI、Parser 语法、标签与文本属性、示例、字体、布局、绘制、错误处理与数据模板文档；原始响应缓存在 `tmp/20261124T113838+0800-aac601/_suite/shared/`。服务请求使用 UTF-8 纯文本 POST `/snapshot`，依据 HTTP 状态、Content-Type、X-Request-Id 与 Server-Timing 留痕。字体从真实 `/fonts` 响应选择 `Noto Sans CJK SC`。主体、图表、文字和几何均由完整 Snapshot DSL 构造。

## 视觉自检

| 检查项 | 结果与证据 |
|---|---|
| 交易与计算 | 通过；四行明细、小计4124.30、折扣180.00、税前3944.30、精确税额236.658、税额236.66、运费35.00、应付4215.96。 |
| 文字保真 | 通过；Raw/CDATA 保留批次双空格、反斜杠、尖括号、& 和指令样式文本；未使用实体解码。 |
| 跨页与富文本 | 通过；重复页眉与编号一致；PAID / 已结算同段落自然基线，状态样张不改应付。 |
| 尺寸与字号 | 通过；两页1200×1600，安全边距48，正文≥24、脚注20，金额固定两位小数并右对齐。 |
| 实际看图 | 通过；每张当前版本服务原图均由 Read 实际查看并记录 observed/changes/compared。 |

## 设计选择

白底结算单以靛蓝标题、细分隔线和固定金额列形成严谨账单层级；第二页将说明与字面文本分区，绿色PAID只作为富文本样章。

## 问题、修改与验证

准备阶段离线验证Decimal顺序及所有字面值。执行阶段依真实Read反馈修改；本报告只汇总已接受版本，失败请求和旧版本由suitekit完整保留。

## 交付文件

- `invoice-page-01.png`
- `invoice-page-01.snapshot`
- `invoice-page-02.png`
- `invoice-page-02.snapshot`
- `invoice-audit.json`
- `text-map.json`
- `snapshot-usage.md`
- `task-metrics.json`
