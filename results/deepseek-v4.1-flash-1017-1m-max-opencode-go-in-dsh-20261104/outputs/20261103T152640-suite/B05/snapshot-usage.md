# B05 · 从零构想产品并设计十个关键使用画面 — Snapshot 使用与自检报告

- 状态：**completed**
- run_id：`20261103T152640-suite`
- 输出目录：`outputs/20261103T152640-suite/B05/`（path_base: suite_root）
- 临时目录：`tmp/20261103T152640-suite/B05/`
- 服务：`https://open-snapshot.muedsa.com`（`POST /snapshot`，`text/plain` 请求体）

## 1. 任务与交付

构想 MediSort 药盒：实体 7×4 格药盒 + 家属端 + 药师端 + 纸质兜底卡，解决独居老人漏服与子女无法确认的问题。十张画面覆盖配对、配置、药师审核、待机、提醒、确认、家属查看、补药、周报复盘与纸质兜底，跨画面共用同一套人物、药品、时间点与统计数字。

| 文件 | 说明 |
|---|---|
| [case-01/final.png](case-01/final.png) | 药盒待机屏 |
| [case-02/final.png](case-02/final.png) | 到点提醒 |
| [case-03/final.png](case-03/final.png) | 服药确认 |
| [case-04/final.png](case-04/final.png) | 家属端首页 |
| [case-05/final.png](case-05/final.png) | 时间表编辑 |
| [case-06/final.png](case-06/final.png) | 补药提醒 |
| [case-07/final.png](case-07/final.png) | 用药周报 |
| [case-08/final.png](case-08/final.png) | 设备配对 |
| [case-09/final.png](case-09/final.png) | 药师复核 |
| [case-10/final.png](case-10/final.png) | 打印服药卡 |
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
| [product-brief.md](product-brief.md) | 产品简报 |
| [journey.json](journey.json) | 旅程与前后关系 |
| [portfolio.json](portfolio.json) | 作品集数据 |
| [portfolio.md](portfolio.md) | 作品集说明 |
| [gallery.md](gallery.md) | 画廊 |
| [task-metrics.json](task-metrics.json) | 本题指标 |
| [snapshot-usage.md](snapshot-usage.md) | 本报告 |

## 2. 需求逐项核对

| 要求 | 证据 | 结论 |
|---|---|---|
| 至少 10 张完整界面/使用画面 | 十张，五种形态（设备/手机/平板/桌面/印刷） | 通过 |
| 支持可信使用过程 | journey.json 给出 10 步顺序与前后状态 | 通过 |
| 每件反映不同需求/状态 | 待机、提醒、确认、查看、编辑、补药、复盘、配对、审核、打印 | 通过 |
| 具体可信内容，非骨架 | 真实药名剂量、时间点、统计数字 | 通过 |
| 不把装饰当按钮 | 每个按钮都有明确作用（已服药/稍后/下单/通过/退回） | 通过 |
| 跨画面信息一致 | 4 个时间点、2/4、26/28、两次 19:00 漏服在十张中一致 | 通过 |
| 必要状态有反馈 | 确认页给出 ✓ 与连续天数；失败有指引 | 通过 |
| 逐张与实际旅程审查 | 十张全部打开，并按 journey 顺序复核 | 通过 |

## 3. 实际视觉自检记录

每张最终图都由视觉工具实际打开查看；以下为查看对象、观察与处置。

| 图像 | 观察 | 处置 |
|---|---|---|
| case-01 待机 | 大字时间与进度清楚 | 通过 |
| case-02 提醒 | 整屏反色，两个按钮明确 | 通过 |
| case-03 确认 | 对勾 + 连续天数 + 下一次 | 通过 |
| case-04 家属首页 | 2/4、26/28、四个时间点与其它页一致 | 通过 |
| case-05 时间表 | 四种药与时间点与 case-09 一致 | 通过 |
| case-06 补药 | 剩余 6 天与有效期自洽 | 通过 |
| case-07 周报 | 七天柱与 26/28 自洽 | 通过 |
| case-08 配对 | 搜索态与失败指引 | 通过 |
| case-09 药师 | 三条相互作用 + 说明 + 两个动作 | 通过 |
| case-10 纸质卡 | A5 四行与设备端时间一致 | 通过 |

## 4. 设计与排版决策

- 设备端追求「抬头可见」：字号最大、只有一个主按钮，不用图标代替文字。
- 家属端只回答两个问题：今天怎么样、这周怎么样；其余都收进二级页。
- 药师端的布局按工作流排：左边病人与药品，右边风险，下面写给家属的话。
- 纸质卡是刻意的降级方案：断电、不会用手机、临时外出时仍然有效。

## 5. DSL 能力与文档应用

- 十张共用一套颜色与字号常量；设备端与手机端用不同的最小值字号。
- 手机画面用固定 390×844 画布，卡片按 68–132px 高度排布，避免文字换行错位。
- 表格与列表用固定列宽，保证不同药名长度下仍对齐。

## 6. 实际问题与修复

| 问题 | 原因/判断 | 修复与验证 |
|---|---|---|
| 跨画面数字容易写岔 | 十张分别手写 | 统一用 2/4、26/28、92.9%、两次 19:00 并在每张复核 |
| 设备端字号偏小 | 初版 22px 副标题 | 关键信息提到 28–96px，副标题不低于 20px |

## 旅程顺序

- 1.08 启用 → 2.05 配置 → 3.09 审核 → 4.01 日常 → 5.02 提醒 → 6.03 确认 → 7.04 查看 → 8.06 补药 → 9.07 复盘 → 10.10 兜底
- 请求 10 次（成功 10），看图 10 次，墙钟 132.0 秒

## 7. 过程文件

| 路径（相对总任务根） | 说明 |
|---|---|
| `outputs/20261103T152640-suite/B05/case-01/final.png` | 画面 |
| `outputs/20261103T152640-suite/B05/case-02/final.png` | 画面 |
| `outputs/20261103T152640-suite/B05/case-03/final.png` | 画面 |
| `outputs/20261103T152640-suite/B05/case-04/final.png` | 画面 |
| `outputs/20261103T152640-suite/B05/case-05/final.png` | 画面 |
| `outputs/20261103T152640-suite/B05/case-06/final.png` | 画面 |
| `outputs/20261103T152640-suite/B05/case-07/final.png` | 画面 |
| `outputs/20261103T152640-suite/B05/case-08/final.png` | 画面 |
| `outputs/20261103T152640-suite/B05/case-09/final.png` | 画面 |
| `outputs/20261103T152640-suite/B05/case-10/final.png` | 画面 |
| `outputs/20261103T152640-suite/B05/product-brief.md` | 产品简报 |
| `outputs/20261103T152640-suite/B05/journey.json` | 旅程 |

## 8. 未解决事项

- 无。所有指定交付已生成、实际渲染并逐图查看。
