# A14 Snapshot 使用与自检报告

- 状态：completed
- 运行 ID：`20261124T113838+0800-aac601`
- 输出根：`outputs/20261124T113838+0800-aac601/A14`（path_base=suite_root）
- 临时根：`tmp/20261124T113838+0800-aac601/A14`（path_base=suite_root）
- 服务基址：https://open-snapshot.muedsa.com

## 文档与工具应用

实际读取服务指南、OpenAPI、Parser 语法、标签与文本属性、示例、字体、布局、绘制、错误处理与数据模板文档；原始响应缓存在 `tmp/20261124T113838+0800-aac601/_suite/shared/`。服务请求使用 UTF-8 纯文本 POST `/snapshot`，依据 HTTP 状态、Content-Type、X-Request-Id 与 Server-Timing 留痕。字体从真实 `/fonts` 响应选择 `Noto Sans CJK SC`。主体、图表、文字和几何均由完整 Snapshot DSL 构造。

## 视觉自检

| 检查项 | 结果与证据 |
|---|---|
| 八张参数化生成 | 通过；K01–K08全部从cards.json生成，1200×630；无逐条硬改输入；长度仅触发56/50/46px标题分支和换行。 |
| 内容完整性 | 通过；标题、讲者、时间、状态原文字保留；换行只插入不删字符；K04尖括号与&通过Raw/CDATA原样显示。 |
| 排版约束 | 通过；标题≥36且≤3行，讲者26且≤2行；标题与状态徽标分区不碰撞；内容安全边距40，无整图缩小。 |
| 状态体系 | 通过；颜色+符号+文字共同区分开放/满额/候补/取消；取消卡另显示本场取消且保留完整标题与时间。 |
| 实际看图 | 通过；八张当前版本服务原图逐一Read并记录observed/changes/compared；接触表未替代单图检查。 |
| 视觉修复 | 通过；v001实际查看发现K03末行单字级、K08弯引号宽度低估；改为非ASCII字符统一2单位、动态规划平衡换行并惩罚短末行/断词/标点拆对。v002八张重新查看，K03在冒号后换行、K07在破折号后换行、K08在冒号后换行，原文均未改。 |

## 设计选择

统一靛蓝主色、左侧色条、顶部品牌/日期和右侧状态徽标。标题按测量长度选择三档字号并显式换行，讲者和时间使用独立底部网格。

## 问题、修改与验证

准备阶段离线验证8份DSL、文本恢复、字号/行数和安全几何。执行阶段逐张查看；任何缺陷都另存版本、重新渲染并重新查看该卡。

## 交付文件

- `card-K01.png`
- `card-K01.snapshot`
- `card-K02.png`
- `card-K02.snapshot`
- `card-K03.png`
- `card-K03.snapshot`
- `card-K04.png`
- `card-K04.snapshot`
- `card-K05.png`
- `card-K05.snapshot`
- `card-K06.png`
- `card-K06.snapshot`
- `card-K07.png`
- `card-K07.snapshot`
- `card-K08.png`
- `card-K08.snapshot`
- `batch-audit.json`
- `snapshot-usage.md`
- `task-metrics.json`
