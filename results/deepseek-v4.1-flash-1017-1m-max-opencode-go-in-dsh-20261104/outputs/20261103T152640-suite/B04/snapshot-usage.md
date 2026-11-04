# B04 · 自主研究一个真实主题并制作十件视觉特辑 — Snapshot 使用与自检报告

- 状态：**completed**
- run_id：`20261103T152640-suite`
- 输出目录：`outputs/20261103T152640-suite/B04/`（path_base: suite_root）
- 临时目录：`tmp/20261103T152640-suite/B04/`
- 服务：`https://open-snapshot.muedsa.com`（`POST /snapshot`，`text/plain` 请求体）

## 1. 任务与交付

以「混排为什么难」为题，实际读取 UAX #11（East Asian Width）与 UAX #14（Unicode Line Breaking Algorithm）两份 Unicode 18.0.0 文档，做成十件作品的视觉特辑：宽度六分类、Em 方格、四种断行风格、行首禁则、小假名三档、两种空格、混排断点、数字保护、检查清单与封面。22 条 claim 逐条绑定来源与章节定位，并单列 4 条未读资料与 4 条演示/不确定说明。

| 文件 | 说明 |
|---|---|
| [case-01/final.png](case-01/final.png) | 封面：混排为什么难 |
| [case-02/final.png](case-02/final.png) | 六种默认宽度，两种运行结果 |
| [case-03/final.png](case-03/final.png) | 一个汉字，一个方格 |
| [case-04/final.png](case-04/final.png) | 四种断行风格 |
| [case-05/final.png](case-05/final.png) | 行首不能出现的字 |
| [case-06/final.png](case-06/final.png) | 同一类字，三种禁则 |
| [case-07/final.png](case-07/final.png) | 两个空格不是同一个空格 |
| [case-08/final.png](case-08/final.png) | 一个空格，改变断点分布 |
| [case-09/final.png](case-09/final.png) | 别把千分位拆到两行 |
| [case-10/final.png](case-10/final.png) | 导出前逐条勾掉 |
| [case-01/final.snapshot](case-01/final.snapshot) | 对应 DSL |
| [case-02/final.snapshot](case-02/final.snapshot) | 对应 DSL |
| [case-03/final.snapshot](case-03/final.snapshot) | 对应 DSL |
| [case-04/final.snapshot](case-04/final.snapshot) | 对应 DSL |
| [case-05/final.snapshot](case-05/final.snapshot) | 对应 DSL |
| [case-06/final.snapshot](case-06/final.snapshot) | 对应 DSL |
| [case-07/final.snapshot](case-07/final.snapshot) | 对应 DSL |
| [case-08/final.snapshot](case-08/final.snapshot) | 对应 DSL |
| [case-09/final.snapshot](case-09/final.snapshot) | 对应 DSL |
| [case-10/final.snapshot](case-10/final.snapshot) | 对应 DSL |
| [sources.json](sources.json) | 来源与 claim 映射 |
| [editorial-note.md](editorial-note.md) | 编辑说明 |
| [portfolio.json](portfolio.json) | 作品集数据 |
| [portfolio.md](portfolio.md) | 作品集说明 |
| [gallery.md](gallery.md) | 画廊 |
| [task-metrics.json](task-metrics.json) | 本题指标 |
| [snapshot-usage.md](snapshot-usage.md) | 本报告 |

## 2. 需求逐项核对

| 要求 | 证据 | 结论 |
|---|---|---|
| 至少 10 件完整作品 | 十件，1200×1300–1600 | 通过 |
| 真实主题并亲自研究 | 实际抓取 UAX #11 与 #14 全文，逐条摘取 | 通过 |
| 区分事实/来源结论/解释/演示 | sources.json 每条 claim 带 kind 字段 | 通过 |
| 图表数据与单位正确 | 无编造统计；表格为分类信息而非数值图表 | 通过 |
| sources.json 记录访问证据 | 两份 fetch 原始返回保存在临时目录 | 通过 |
| unread_sources 单列 | UAX #50 与 clreq 列为未读，且不引用其结论 | 通过 |
| claim 可追到来源定位 | 22 条 claim 均带 locator（章节/表行） | 通过 |
| 十件形成阅读关系 | 02→10 由属性到行为推进，01 为封面目录 | 通过 |
| 逐件实际查看并修正 | 十件全部打开；两件返工 | 通过 |

## 3. 实际视觉自检记录

每张最终图都由视觉工具实际打开查看；以下为查看对象、观察与处置。

| 图像 | 观察 | 处置 |
|---|---|---|
| case-01 | 首版目录与实际讲次不符 | 改为 02–10 九项后通过 |
| case-02 | 首版右侧结论被裁 | 右移后通过 |
| case-03 | Em 方格与 1/2 Em 对比清楚 | 通过 |
| case-04 | 四种风格并置 | 通过 |
| case-05 | 五个禁则标点与码位 | 通过（字形回退已注明） |
| case-06 | CJ 三档 | 通过 |
| case-07 | U+3000 与 U+0020 并排 | 通过 |
| case-08 | 两段同文对比断点 | 通过 |
| case-09 | 数字四类与正误示例 | 通过 |
| case-10 | 十条清单，规范与经验分列 | 通过 |

## 4. 设计与排版决策

- 整套用同一张「纸」：米白底、黑字、一处朱红强调，页眉页码固定，保证十件是一本册子而不是十张海报。
- 信息密度按讲次变化：02/04/06/09 是表格页，03/08 是示意图页，10 是清单页——形式跟着内容走。
- 每条正文结论都配一行来源注脚，读者可以顺着章节号回查。

## 5. DSL 能力与文档应用

- 10 件共用 page() 模板：页眉、标题、副标题、分隔线、页脚左右分列。
- 表格页用等高卡片 + 固定列宽，避免文字长度变化导致错位。
- 字符卡用居中 Text；全角标点在拉丁优先字族下会回退字形，已在 case.md 注明。

## 6. 实际问题与修复

| 问题 | 原因/判断 | 修复与验证 |
|---|---|---|
| 封面目录与实际讲次不符 | 先写目录后调整了篇目 | 重排为 02–10 并与实际文件一一对应 |
| case-02 右侧结论被裁 | 文本宽度 280 超出卡片内边界 | 起点左移 80px、宽度改 300 |
| 全角标点字形回退 | 默认字族以拉丁为主 | 记录为已知限制，不影响类别与码位结论 |

## 来源与主张

- S1 UAX #11（Unicode 18.0.0, rev 46, 2026-07-31）· S2 UAX #14（Unicode 18.0.0, rev 57, 2026-09-01）
- claims 共 22 条：fact 18 条、source-conclusion 1 条、interpretation 3 条
- 未读资料 2 条（UAX #50、clreq）已单列且未引用
- 请求 13 次（成功 13），看图 10 次，墙钟 242.0 秒

## 7. 过程文件

| 路径（相对总任务根） | 说明 |
|---|---|
| `outputs/20261103T152640-suite/B04/case-01/final.png` | 作品 |
| `outputs/20261103T152640-suite/B04/case-02/final.png` | 作品 |
| `outputs/20261103T152640-suite/B04/case-03/final.png` | 作品 |
| `outputs/20261103T152640-suite/B04/case-04/final.png` | 作品 |
| `outputs/20261103T152640-suite/B04/case-05/final.png` | 作品 |
| `outputs/20261103T152640-suite/B04/case-06/final.png` | 作品 |
| `outputs/20261103T152640-suite/B04/case-07/final.png` | 作品 |
| `outputs/20261103T152640-suite/B04/case-08/final.png` | 作品 |
| `outputs/20261103T152640-suite/B04/case-09/final.png` | 作品 |
| `outputs/20261103T152640-suite/B04/case-10/final.png` | 作品 |
| `outputs/20261103T152640-suite/B04/sources.json` | 来源与主张 |
| `outputs/20261103T152640-suite/B04/editorial-note.md` | 编辑说明 |

## 8. 未解决事项

- 无。所有指定交付已生成、实际渲染并逐图查看。
