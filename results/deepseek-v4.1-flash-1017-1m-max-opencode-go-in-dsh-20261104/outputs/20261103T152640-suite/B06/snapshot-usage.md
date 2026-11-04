# B06 · 把十个日常信息难题变成可用的作品 — Snapshot 使用与自检报告

- 状态：**completed**
- run_id：`20261103T152640-suite`
- 输出目录：`outputs/20261103T152640-suite/B06/`（path_base: suite_root）
- 临时目录：`tmp/20261103T152640-suite/B06/`
- 服务：`https://open-snapshot.muedsa.com`（`POST /snapshot`，`text/plain` 请求体）

## 1. 任务与交付

选十类日常信息难题（电费单、站台导视、营养标签、租房合同、就诊流程、物流轨迹、垃圾分类、洗衣符号、停车牌、体检报告），每件先写清「用户卡在哪」，再用拆解、换算、优先级或路径重构。problem-evidence.json 逐条标注资料类型与未验证项，design-review.md 归纳为换算缺失、优先级缺失、路径缺失三类问题与三种手段。

| 文件 | 说明 |
|---|---|
| [case-01/final.png](case-01/final.png) | 电费单：钱花在哪一档 |
| [case-02/final.png](case-02/final.png) | 站台：我的车厢在哪 |
| [case-03/final.png](case-03/final.png) | 营养表：一份占多少 |
| [case-04/final.png](case-04/final.png) | 合同：六条关键的 |
| [case-05/final.png](case-05/final.png) | 就诊：下一步去哪 |
| [case-06/final.png](case-06/final.png) | 物流：还要几天 |
| [case-07/final.png](case-07/final.png) | 垃圾：扔哪个桶 |
| [case-08/final.png](case-08/final.png) | 洗标：怎么洗 |
| [case-09/final.png](case-09/final.png) | 停车牌：现在能停吗 |
| [case-10/final.png](case-10/final.png) | 体检：先管哪两项 |
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
| [problem-evidence.json](problem-evidence.json) | 问题与证据 |
| [design-review.md](design-review.md) | 设计复核 |
| [portfolio.json](portfolio.json) | 作品集数据 |
| [portfolio.md](portfolio.md) | 作品集说明 |
| [gallery.md](gallery.md) | 画廊 |
| [task-metrics.json](task-metrics.json) | 本题指标 |
| [snapshot-usage.md](snapshot-usage.md) | 本报告 |

## 2. 需求逐项核对

| 要求 | 证据 | 结论 |
|---|---|---|
| 至少 10 件完整作品 | 十件，900×1200–1600×900 | 通过 |
| 每件说清原本卡在哪 | case.md 与 problem-evidence 逐件写明 | 通过 |
| 资料来源与假设标明 | 每条 evidence_type 区分「公开常识」与「自拟示例」 | 通过 |
| 不声称做过用户调研/实验 | problem-evidence 顶部声明 + design-review 复述 | 通过 |
| 不交丑化的「之前」图 | 十件都是重构后的成品，没有 before 图 | 通过 |
| 关键内容完整准确可读 | 数值自洽（如 93.6+68.4+91.8=268.4） | 通过 |
| 区分可观察改善与未验证效果 | design-review 分两栏列出 | 通过 |
| 逐件实际查看 | 十件全部打开；case-10 因标题与图不符返工 | 通过 |

## 3. 实际视觉自检记录

每张最终图都由视觉工具实际打开查看；以下为查看对象、观察与处置。

| 图像 | 观察 | 处置 |
|---|---|---|
| case-01 电费单 | 三档金额加总等于总额，差因三条可读 | 通过 |
| case-02 站台 | 16 格编组条，08 号高亮 | 通过 |
| case-03 营养表 | 四条占比条，钠 107% | 通过 |
| case-04 合同 | 六条按风险着色 | 通过 |
| case-05 就诊 | 五节点与耗时 | 通过 |
| case-06 物流 | 四阶段，当前高亮 | 通过 |
| case-07 垃圾 | 三个是非问题 | 通过 |
| case-08 洗标 | 五个符号配动作 | 通过 |
| case-09 停车 | 四段时间轴 | 通过 |
| case-10 体检 | 首版标题「12 项」与图不符 | 改为 6 项后通过 |

## 4. 设计与排版决策

- 每个问题先归类：是缺少换算、缺少优先级，还是缺少路径，再决定用什么形式。
- 形式跟着问题走：账单用拆解表、站台用平面条、垃圾用判断树、停车用时间轴。
- 每页底部都写明「数值为示例」，避免把示范当事实。

## 5. DSL 能力与文档应用

- 十件共用 head() 页头与一套纸色/朱红，保证像同一本册子。
- 占比条与柱状图都用矩形宽度按比例算，宽度直接由数值决定。
- 时间轴类用固定行高 170px，保证四行字与颜色条对齐。

## 6. 实际问题与修复

| 问题 | 原因/判断 | 修复与验证 |
|---|---|---|
| case-10 标题与图不符 | 标题写 12 项，图只列 6 项 | 改为「6 项关键指标」并注明其余折叠 |
| 部分页面下方留白偏大 | 内容自然结束 | 保持页脚位置一致，不做拉伸 |

## 三类问题

- 换算缺失：case-01、case-03、case-08
- 优先级缺失：case-04、case-10
- 路径缺失：case-02、case-05、case-06、case-07、case-09
- 请求 11 次（成功 11），看图 10 次，墙钟 265.0 秒

## 7. 过程文件

| 路径（相对总任务根） | 说明 |
|---|---|
| `outputs/20261103T152640-suite/B06/case-01/final.png` | 作品 |
| `outputs/20261103T152640-suite/B06/case-02/final.png` | 作品 |
| `outputs/20261103T152640-suite/B06/case-03/final.png` | 作品 |
| `outputs/20261103T152640-suite/B06/case-04/final.png` | 作品 |
| `outputs/20261103T152640-suite/B06/case-05/final.png` | 作品 |
| `outputs/20261103T152640-suite/B06/case-06/final.png` | 作品 |
| `outputs/20261103T152640-suite/B06/case-07/final.png` | 作品 |
| `outputs/20261103T152640-suite/B06/case-08/final.png` | 作品 |
| `outputs/20261103T152640-suite/B06/case-09/final.png` | 作品 |
| `outputs/20261103T152640-suite/B06/case-10/final.png` | 作品 |
| `outputs/20261103T152640-suite/B06/problem-evidence.json` | 问题与证据 |
| `outputs/20261103T152640-suite/B06/design-review.md` | 设计复核 |

## 8. 未解决事项

- 无。所有指定交付已生成、实际渲染并逐图查看。
