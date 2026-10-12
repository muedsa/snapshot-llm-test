# Snapshot 全套交付索引

- run_id：`run-20261002-220723-mimo`
- profile：`all`　时区：UTC+08:00
- 起：2026-10-02T22:07:23+08:00　止：2026-10-09T12:30:01+08:00　总墙钟：570158 s（6.6 天）
- 服务：https://open-snapshot.muedsa.com　状态：**completed**（30/30 题 completed）
- 总输出根：`outputs/run-20261002-220723-mimo/`　总临时根：`tmp/run-20261002-220723-mimo/`（相对总任务根，path_base=suite_root）

## 0. 一眼看全

| 项目 | 数量 | 口径 |
| --- | --- | --- |
| 最终图片 | **124** | A 轨 64 张 + B 轨 60 张；已排除 2 张明确归档的草稿（A08/archive、A10/archive）；每张都有同名 `.snapshot` |
| 独立作品 | **118** | A 轨 58 件 + B 轨 60 件；B01–B06 每题 10 件独立完整作品；A21/A22 的多轮版本只算 1 件作品 |
| 请求 | 648 | HTTP 尝试 648 次 = render 435 + documentation 100 + fonts 5 + research 108；另有 1 行 log_note 非请求行 |
| 成功 / 失败 | 559 / 73 | 失败含刻意能力探测的 400、失效链接 404、反爬 412/403 与 1 次真实网络失败；**0 次 429**；另有 17 行状态未记录（取文工具不暴露状态码，记 null 不冒充成败） |
| 迭代 / 读图 | 409 / 505 | 迭代行来自 30 题的 `iterations.jsonl`；读图 505 次（22 题用申报值、8 题由迭代记录推得，逐题标注来源） |
| 请求耗时 / 总墙钟 | 2166.978 s / 570158 s | 请求串行；总墙钟还包含读题、写生成器、读图、像素复核与写交付物 |
| DSL 版本 | 526 | `tmp/` 402 份 + `outputs/` 124 份 `.snapshot`，未覆盖任何已渲染过的尝试 |
| token / 图像用量 / 费用 | **null** | 平台未提供计量数据，按约定未知即填 null，不以字数或渲染次数猜造 |

## 1. 套件层交付物（`outputs/run-20261002-220723-mimo/_suite/`）

| 文件 | 作用 |
| --- | --- |
| [`index.md`](index.md) | 本文件：30 题状态、产物、单题入口与实际路径的总索引 |
| [`gallery.md`](gallery.md) | **总画廊**：逐图展示全部 124 张最终图片（含 A21/A22 全部轮次、B 轨 60 件作品），每图有标题、Markdown 预览、原 PNG 链接与对应 `.snapshot` 链接；相对本目录，无远程图片 |
| [`snapshot-usage.md`](snapshot-usage.md) | 全套实际文档/DSL/工具应用、跨题经验与踩坑、总审查与剩余事项；§10 记录根 `.gitignore` 与 PATHS.md 路径基准的合规核验 |
| [`task-metrics.json`](task-metrics.json) | 全套起止与总耗时、shared + 每题请求/迭代/读图/作品数、汇总范围与计时/日志来源 |
| [`suite-state.json`](suite-state.json) | 当前进度指针：逐题状态、启止、产物、视觉复核证据、未解决事项与恢复笔记 |
| `gallery.html` | 附加的 HTML 浏览版画廊（同为相对链接、无远程脚本）；**不是** `suite_required_artifacts` 要求项，只是便于肉眼快速翻看 |
| [`../../../.gitignore`](../../../.gitignore) | 总任务根的忽略文件，只排除 6 条运行时缓存规则；`outputs/` 与 `tmp/` 中的成品与过程证据一律不排除 |

## 2. 逐题索引

### A01　六个月经营诊断驾驶舱

- 状态：**completed**　轨道：A　墙钟：1140 s
- 轮次：单轮连续视觉迭代
- 请求 2 次（200 × 2 / 失败 0 / 状态未记录 0）　迭代 2 行　读图 2 次（declared:image_views）
- 最终图片 1 张（1 件作品）：
  - operations.png　[`A01/operations.png`](../A01/operations.png)　1600x1000　324302 B
- 交付产物：5 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`A01/snapshot-usage.md`](../A01/snapshot-usage.md)　[`A01/task-metrics.json`](../A01/task-metrics.json)
- 实际输出：`outputs/run-20261002-220723-mimo/A01/`　实际临时：`tmp/run-20261002-220723-mimo/A01/`

### A02　三会场密集会议日程

- 状态：**completed**　轨道：A　墙钟：2666 s
- 轮次：单轮连续视觉迭代
- 请求 2 次（200 × 2 / 失败 0 / 状态未记录 0）　迭代 5 行　读图 7 次（declared:image_views）
- 最终图片 2 张（2 件作品）：
  - agenda-mobile.png　[`A02/agenda-mobile.png`](../A02/agenda-mobile.png)　720x1280　217403 B
  - agenda-wide.png　[`A02/agenda-wide.png`](../A02/agenda-wide.png)　1920x1200　480387 B
- 交付产物：7 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`A02/snapshot-usage.md`](../A02/snapshot-usage.md)　[`A02/task-metrics.json`](../A02/task-metrics.json)
- 实际输出：`outputs/run-20261002-220723-mimo/A02/`　实际临时：`tmp/run-20261002-220723-mimo/A02/`

### A03　多层语义故障恢复

- 状态：**completed**　轨道：A　墙钟：1726 s
- 轮次：单轮连续视觉迭代
- 请求 6 次（200 × 2 / 失败 4 / 状态未记录 0）　迭代 6 行　读图 5 次（declared:image_views）
- 最终图片 1 张（1 件作品）：
  - system-pulse.png　[`A03/system-pulse.png`](../A03/system-pulse.png)　1280x800　41456 B
- 交付产物：5 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`A03/snapshot-usage.md`](../A03/snapshot-usage.md)　[`A03/task-metrics.json`](../A03/task-metrics.json)
- 实际输出：`outputs/run-20261002-220723-mimo/A03/`　实际临时：`tmp/run-20261002-220723-mimo/A03/`

### A04　分组改善与总体下降的数据解释

- 状态：**completed**　轨道：A　墙钟：1644 s
- 轮次：单轮连续视觉迭代
- 请求 2 次（200 × 2 / 失败 0 / 状态未记录 0）　迭代 2 行　读图 5 次（declared:image_views）
- 最终图片 1 张（1 件作品）：
  - conversion-story.png　[`A04/conversion-story.png`](../A04/conversion-story.png)　1600x1000　388354 B
- 交付产物：5 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`A04/snapshot-usage.md`](../A04/snapshot-usage.md)　[`A04/task-metrics.json`](../A04/task-metrics.json)
- 实际输出：`outputs/run-20261002-220723-mimo/A04/`　实际临时：`tmp/run-20261002-220723-mimo/A04/`

### A05　不规则采样与缺测的仪表报告

- 状态：**completed**　轨道：A　墙钟：2163 s
- 轮次：单轮连续视觉迭代
- 请求 6 次（200 × 5 / 失败 1 / 状态未记录 0）　迭代 4 行　读图 10 次（declared:image_views）
- 最终图片 1 张（1 件作品）：
  - sensor-report.png　[`A05/sensor-report.png`](../A05/sensor-report.png)　1440x1000　224719 B
- 交付产物：5 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`A05/snapshot-usage.md`](../A05/snapshot-usage.md)　[`A05/task-metrics.json`](../A05/task-metrics.json)
- 实际输出：`outputs/run-20261002-220723-mimo/A05/`　实际临时：`tmp/run-20261002-220723-mimo/A05/`

### A06　十四节点依赖图与反馈回路

- 状态：**completed**　轨道：A　墙钟：2297 s
- 轮次：单轮连续视觉迭代
- 请求 2 次（200 × 2 / 失败 0 / 状态未记录 0）　迭代 1 行　读图 7 次（declared:image_views）
- 最终图片 1 张（1 件作品）：
  - dependency-map.png　[`A06/dependency-map.png`](../A06/dependency-map.png)　1600x1000　246398 B
- 交付产物：5 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`A06/snapshot-usage.md`](../A06/snapshot-usage.md)　[`A06/task-metrics.json`](../A06/task-metrics.json)
- 实际输出：`outputs/run-20261002-220723-mimo/A06/`　实际临时：`tmp/run-20261002-220723-mimo/A06/`

### A07　三线换乘图与路线核验

- 状态：**completed**　轨道：A　墙钟：3261 s
- 轮次：单轮连续视觉迭代
- 请求 5 次（200 × 5 / 失败 0 / 状态未记录 0）　迭代 2 行　读图 13 次（declared:image_views）
- 最终图片 2 张（2 件作品）：
  - network-map.png　[`A07/network-map.png`](../A07/network-map.png)　1600x1000　220348 B
  - travel-card.png　[`A07/travel-card.png`](../A07/travel-card.png)　720x1280　216935 B
- 交付产物：8 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`A07/snapshot-usage.md`](../A07/snapshot-usage.md)　[`A07/task-metrics.json`](../A07/task-metrics.json)
- 实际输出：`outputs/run-20261002-220723-mimo/A07/`　实际临时：`tmp/run-20261002-220723-mimo/A07/`

### A08　网格导览与两条可走路线

- 状态：**completed**　轨道：A　墙钟：31678 s
- 轮次：单轮连续视觉迭代
- 请求 3 次（200 × 3 / 失败 0 / 状态未记录 0）　迭代 2 行　读图 5 次（declared:image_views）
- 最终图片 1 张（1 件作品）：
  - wayfinding.png　[`A08/wayfinding.png`](../A08/wayfinding.png)　1560x1080　237094 B
- 交付产物：7 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`A08/snapshot-usage.md`](../A08/snapshot-usage.md)　[`A08/task-metrics.json`](../A08/task-metrics.json)
- 实际输出：`outputs/run-20261002-220723-mimo/A08/`　实际临时：`tmp/run-20261002-220723-mimo/A08/`

### A09　十二个非对称图形变换标本

- 状态：**completed**　轨道：A　墙钟：4227 s
- 轮次：单轮连续视觉迭代
- 请求 6 次（200 × 2 / 失败 4 / 状态未记录 0）　迭代 3 行　读图 4 次（declared:image_views）
- 最终图片 1 张（1 件作品）：
  - transform-atlas.png　[`A09/transform-atlas.png`](../A09/transform-atlas.png)　1600x1200　200495 B
- 交付产物：5 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`A09/snapshot-usage.md`](../A09/snapshot-usage.md)　[`A09/task-metrics.json`](../A09/task-metrics.json)
- 实际输出：`outputs/run-20261002-220723-mimo/A09/`　实际临时：`tmp/run-20261002-220723-mimo/A09/`

### A10　透明合成与滤镜语义实验板

- 状态：**completed**　轨道：A　墙钟：2053 s
- 轮次：单轮连续视觉迭代
- 请求 6 次（200 × 3 / 失败 0 / 状态未记录 3）　迭代 2 行　读图 7 次（declared:image_views）
- 最终图片 1 张（1 件作品）：
  - compositing-lab.png　[`A10/compositing-lab.png`](../A10/compositing-lab.png)　1440x1100　251582 B
- 交付产物：6 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`A10/snapshot-usage.md`](../A10/snapshot-usage.md)　[`A10/task-metrics.json`](../A10/task-metrics.json)
- 实际输出：`outputs/run-20261002-220723-mimo/A10/`　实际临时：`tmp/run-20261002-220723-mimo/A10/`

### A11　文字保真与跨页结算单

- 状态：**completed**　轨道：A　墙钟：6018 s
- 轮次：单轮连续视觉迭代
- 请求 13 次（200 × 11 / 失败 2 / 状态未记录 0）　迭代 17 行　读图 12 次（declared:image_views）
- 最终图片 2 张（2 件作品）：
  - invoice-page-01.png　[`A11/invoice-page-01.png`](../A11/invoice-page-01.png)　1200x1600　179476 B
  - invoice-page-02.png　[`A11/invoice-page-02.png`](../A11/invoice-page-02.png)　1200x1600　178349 B
- 交付产物：8 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`A11/snapshot-usage.md`](../A11/snapshot-usage.md)　[`A11/task-metrics.json`](../A11/task-metrics.json)
- 实际输出：`outputs/run-20261002-220723-mimo/A11/`　实际临时：`tmp/run-20261002-220723-mimo/A11/`

### A12　四断点完整内容视觉系统

- 状态：**completed**　轨道：A　墙钟：3344 s
- 轮次：单轮连续视觉迭代
- 请求 12 次（200 × 12 / 失败 0 / 状态未记录 0）　迭代 11 行　读图 8 次（declared:counts.image_views）
- 最终图片 4 张（4 件作品）：
  - desktop.png　[`A12/desktop.png`](../A12/desktop.png)　1440x900　120059 B
  - mobile.png　[`A12/mobile.png`](../A12/mobile.png)　360x800　72662 B
  - stage.png　[`A12/stage.png`](../A12/stage.png)　1920x1080　134024 B
  - tablet.png　[`A12/tablet.png`](../A12/tablet.png)　768x1024　97139 B
- 交付产物：13 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`A12/snapshot-usage.md`](../A12/snapshot-usage.md)　[`A12/task-metrics.json`](../A12/task-metrics.json)
- 实际输出：`outputs/run-20261002-220723-mimo/A12/`　实际临时：`tmp/run-20261002-220723-mimo/A12/`

### A13　品牌标志到完整活动应用

- 状态：**completed**　轨道：A　墙钟：4014 s
- 轮次：单轮连续视觉迭代
- 请求 20 次（200 × 20 / 失败 0 / 状态未记录 0）　迭代 23 行　读图 23 次（derived-from-iterations:images_viewed）
- 最终图片 4 张（4 件作品）：
  - brand-banner.png　[`A13/brand-banner.png`](../A13/brand-banner.png)　1200x400　31376 B
  - launch-poster.png　[`A13/launch-poster.png`](../A13/launch-poster.png)　1080x1350　56441 B
  - symbol-black.png　[`A13/symbol-black.png`](../A13/symbol-black.png)　512x512　6220 B
  - symbol-color.png　[`A13/symbol-color.png`](../A13/symbol-color.png)　512x512　9077 B
- 交付产物：13 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`A13/snapshot-usage.md`](../A13/snapshot-usage.md)　[`A13/task-metrics.json`](../A13/task-metrics.json)
- 实际输出：`outputs/run-20261002-220723-mimo/A13/`　实际临时：`tmp/run-20261002-220723-mimo/A13/`

### A14　八组文案压力测试与批量生成

- 状态：**completed**　轨道：A　墙钟：6182 s
- 轮次：单轮连续视觉迭代
- 请求 41 次（200 × 33 / 失败 8 / 状态未记录 0）　迭代 20 行　读图 20 次（derived-from-iterations:images_viewed）
- 最终图片 8 张（8 件作品）：
  - card-K01.png　[`A14/card-K01.png`](../A14/card-K01.png)　1200x630　26199 B
  - card-K02.png　[`A14/card-K02.png`](../A14/card-K02.png)　1200x630　58809 B
  - card-K03.png　[`A14/card-K03.png`](../A14/card-K03.png)　1200x630　72035 B
  - card-K04.png　[`A14/card-K04.png`](../A14/card-K04.png)　1200x630　62703 B
  - card-K05.png　[`A14/card-K05.png`](../A14/card-K05.png)　1200x630　54248 B
  - card-K06.png　[`A14/card-K06.png`](../A14/card-K06.png)　1200x630　67850 B
  - card-K07.png　[`A14/card-K07.png`](../A14/card-K07.png)　1200x630　74187 B
  - card-K08.png　[`A14/card-K08.png`](../A14/card-K08.png)　1200x630　53366 B
- 交付产物：19 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`A14/snapshot-usage.md`](../A14/snapshot-usage.md)　[`A14/task-metrics.json`](../A14/task-metrics.json)
- 实际输出：`outputs/run-20261002-220723-mimo/A14/`　实际临时：`tmp/run-20261002-220723-mimo/A14/`

### A15　复杂界面视觉复刻

- 状态：**completed**　轨道：A　墙钟：6005 s
- 轮次：单轮连续视觉迭代
- 请求 8 次（200 × 8 / 失败 0 / 状态未记录 0）　迭代 15 行　读图 15 次（derived-from-iterations:images_viewed）
- 最终图片 1 张（1 件作品）：
  - reconstructed.png　[`A15/reconstructed.png`](../A15/reconstructed.png)　1440x900　113766 B
- 交付产物：6 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`A15/snapshot-usage.md`](../A15/snapshot-usage.md)　[`A15/task-metrics.json`](../A15/task-metrics.json)
- 实际输出：`outputs/run-20261002-220723-mimo/A15/`　实际临时：`tmp/run-20261002-220723-mimo/A15/`

### A16　从错误图表恢复可信叙事

- 状态：**completed**　轨道：A　墙钟：65490 s
- 轮次：单轮连续视觉迭代
- 请求 4 次（200 × 4 / 失败 0 / 状态未记录 0）　迭代 16 行　读图 16 次（derived-from-iterations:images_viewed）
- 最终图片 1 张（1 件作品）：
  - corrected-report.png　[`A16/corrected-report.png`](../A16/corrected-report.png)　1280x900　178356 B
- 交付产物：6 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`A16/snapshot-usage.md`](../A16/snapshot-usage.md)　[`A16/task-metrics.json`](../A16/task-metrics.json)
- 实际输出：`outputs/run-20261002-220723-mimo/A16/`　实际临时：`tmp/run-20261002-220723-mimo/A16/`

### A17　四页可实践的DSL入门手册

- 状态：**completed**　轨道：A　墙钟：8280 s
- 轮次：单轮连续视觉迭代
- 请求 50 次（200 × 45 / 失败 5 / 状态未记录 0）　迭代 42 行　读图 37 次（derived-from-iterations:image）
- 最终图片 8 张（8 件作品）：
  - example-01.png　[`A17/example-01.png`](../A17/example-01.png)　400x240　30332 B
  - example-02.png　[`A17/example-02.png`](../A17/example-02.png)　400x240　3075 B
  - example-03.png　[`A17/example-03.png`](../A17/example-03.png)　400x240　24631 B
  - example-04.png　[`A17/example-04.png`](../A17/example-04.png)　400x240　5169 B
  - handbook-01.png　[`A17/handbook-01.png`](../A17/handbook-01.png)　1200x1600　323669 B
  - handbook-02.png　[`A17/handbook-02.png`](../A17/handbook-02.png)　1200x1600　272184 B
  - handbook-03.png　[`A17/handbook-03.png`](../A17/handbook-03.png)　1200x1600　319357 B
  - handbook-04.png　[`A17/handbook-04.png`](../A17/handbook-04.png)　1200x1600　289683 B
- 交付产物：20 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`A17/snapshot-usage.md`](../A17/snapshot-usage.md)　[`A17/task-metrics.json`](../A17/task-metrics.json)
- 实际输出：`outputs/run-20261002-220723-mimo/A17/`　实际临时：`tmp/run-20261002-220723-mimo/A17/`

### A18　守恒对象的三幕视觉叙事

- 状态：**completed**　轨道：A　墙钟：19965 s
- 轮次：单轮连续视觉迭代
- 请求 12 次（200 × 9 / 失败 3 / 状态未记录 0）　迭代 21 行　读图 18 次（derived-from-iterations:image）
- 最终图片 1 张（1 件作品）：
  - three-act-story.png　[`A18/three-act-story.png`](../A18/three-act-story.png)　1600x1000　97982 B
- 交付产物：7 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`A18/snapshot-usage.md`](../A18/snapshot-usage.md)　[`A18/task-metrics.json`](../A18/task-metrics.json)
- 实际输出：`outputs/run-20261002-220723-mimo/A18/`　实际临时：`tmp/run-20261002-220723-mimo/A18/`

### A19　构造可核验的视觉题场

- 状态：**completed**　轨道：A　墙钟：36041 s
- 轮次：单轮连续视觉迭代
- 请求 7 次（200 × 5 / 失败 2 / 状态未记录 0）　迭代 6 行　读图 7 次（declared:image_view_count）
- 最终图片 3 张（3 件作品）：
  - grid-scene.png　[`A19/grid-scene.png`](../A19/grid-scene.png)　1600x1600　97172 B
  - occlusion.png　[`A19/occlusion.png`](../A19/occlusion.png)　800x800　55304 B
  - occlusion-alternative.png　[`A19/occlusion-alternative.png`](../A19/occlusion-alternative.png)　800x800　55304 B
- 交付产物：1 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`A19/snapshot-usage.md`](../A19/snapshot-usage.md)　[`A19/task-metrics.json`](../A19/task-metrics.json)
- 实际输出：`outputs/run-20261002-220723-mimo/A19/`　实际临时：`tmp/run-20261002-220723-mimo/A19/`

### A20　二十四密集点的无重叠标注

- 状态：**completed**　轨道：A　墙钟：4093 s
- 轮次：单轮连续视觉迭代
- 请求 2 次（200 × 2 / 失败 0 / 状态未记录 0）　迭代 4 行　读图 6 次（declared:image_view_count）
- 最终图片 1 张（1 件作品）：
  - annotated-map.png　[`A20/annotated-map.png`](../A20/annotated-map.png)　1600x1100　165522 B
- 交付产物：1 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`A20/snapshot-usage.md`](../A20/snapshot-usage.md)　[`A20/task-metrics.json`](../A20/task-metrics.json)
- 实际输出：`outputs/run-20261002-220723-mimo/A20/`　实际临时：`tmp/run-20261002-220723-mimo/A20/`

### A21　真实需求变更：双尺寸发布物

- 状态：**completed**　轨道：A　墙钟：4434 s
- 轮次：预置轮次 round-01/round-02/round-03（共 3 轮，全部产物保留）
- 请求 8 次（200 × 8 / 失败 0 / 状态未记录 0）　迭代 6 行　读图 12 次（declared:image_view_count）
- 最终图片 6 张（2 件作品）：
  - round-01　launch-portrait.png　[`A21/round-01/launch-portrait.png`](../A21/round-01/launch-portrait.png)　1080x1350　76587 B
  - round-01　launch-wide.png　[`A21/round-01/launch-wide.png`](../A21/round-01/launch-wide.png)　1440x810　67808 B
  - round-02　launch-portrait.png　[`A21/round-02/launch-portrait.png`](../A21/round-02/launch-portrait.png)　1080x1350　111670 B
  - round-02　launch-wide.png　[`A21/round-02/launch-wide.png`](../A21/round-02/launch-wide.png)　1440x810　102365 B
  - round-03　launch-portrait.png　[`A21/round-03/launch-portrait.png`](../A21/round-03/launch-portrait.png)　1080x1350　120058 B
  - round-03　launch-wide.png　[`A21/round-03/launch-wide.png`](../A21/round-03/launch-wide.png)　1440x810　109126 B
- 交付产物：28 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`A21/snapshot-usage.md`](../A21/snapshot-usage.md)　[`A21/task-metrics.json`](../A21/task-metrics.json)
- 实际输出：`outputs/run-20261002-220723-mimo/A21/`　实际临时：`tmp/run-20261002-220723-mimo/A21/`

### A22　真实数据更正与局部回归

- 状态：**completed**　轨道：A　墙钟：3382 s
- 轮次：预置轮次 round-01/round-02/round-03（共 3 轮，全部产物保留）
- 请求 4 次（200 × 3 / 失败 0 / 状态未记录 1）　迭代 5 行　读图 4 次（derived-from-iterations:image）
- 最终图片 3 张（1 件作品）：
  - round-01　dashboard.png　[`A22/round-01/dashboard.png`](../A22/round-01/dashboard.png)　1600x1000　221843 B
  - round-02　dashboard.png　[`A22/round-02/dashboard.png`](../A22/round-02/dashboard.png)　1600x1000　252979 B
  - round-03　dashboard.png　[`A22/round-03/dashboard.png`](../A22/round-03/dashboard.png)　1600x1000　242917 B
- 交付产物：25 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`A22/snapshot-usage.md`](../A22/snapshot-usage.md)　[`A22/task-metrics.json`](../A22/task-metrics.json)
- 实际输出：`outputs/run-20261002-220723-mimo/A22/`　实际临时：`tmp/run-20261002-220723-mimo/A22/`

### A23　格式边界下的动画分镜交付

- 状态：**completed**　轨道：A　墙钟：5414 s
- 轮次：单轮连续视觉迭代
- 请求 23 次（200 × 23 / 失败 0 / 状态未记录 0）　迭代 4 行　读图 3 次（derived-from-iterations:image_paths）
- 最终图片 7 张（7 件作品）：
  - cover.png　[`A23/cover.png`](../A23/cover.png)　1200x800　79700 B
  - frame-01.png　[`A23/frame-01.png`](../A23/frame-01.png)　600x600　5721 B
  - frame-02.png　[`A23/frame-02.png`](../A23/frame-02.png)　600x600　5678 B
  - frame-03.png　[`A23/frame-03.png`](../A23/frame-03.png)　600x600　5618 B
  - frame-04.png　[`A23/frame-04.png`](../A23/frame-04.png)　600x600　5516 B
  - frame-05.png　[`A23/frame-05.png`](../A23/frame-05.png)　600x600　5491 B
  - frame-06.png　[`A23/frame-06.png`](../A23/frame-06.png)　600x600　3372 B
- 交付产物：19 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`A23/snapshot-usage.md`](../A23/snapshot-usage.md)　[`A23/task-metrics.json`](../A23/task-metrics.json)
- 实际输出：`outputs/run-20261002-220723-mimo/A23/`　实际临时：`tmp/run-20261002-220723-mimo/A23/`

### A24　双团队约束下的发布作战计划

- 状态：**completed**　轨道：A　墙钟：5710 s
- 轮次：单轮连续视觉迭代
- 请求 17 次（200 × 13 / 失败 4 / 状态未记录 0）　迭代 3 行　读图 6 次（declared:counts.image_views）
- 最终图片 3 张（3 件作品）：
  - action-card.png　[`A24/action-card.png`](../A24/action-card.png)　720x1280　270676 B
  - decision-brief.png　[`A24/decision-brief.png`](../A24/decision-brief.png)　1200x1600　404335 B
  - execution-board.png　[`A24/execution-board.png`](../A24/execution-board.png)　1920x1080　359450 B
- 交付产物：11 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`A24/snapshot-usage.md`](../A24/snapshot-usage.md)　[`A24/task-metrics.json`](../A24/task-metrics.json)
- 实际输出：`outputs/run-20261002-220723-mimo/A24/`　实际临时：`tmp/run-20261002-220723-mimo/A24/`

### B01　十张真实场景的炫酷用例

- 状态：**completed**　轨道：B　墙钟：80227 s
- 轮次：单轮连续视觉迭代
- 请求 31 次（200 × 29 / 失败 2 / 状态未记录 0）　迭代 25 行　读图 26 次（declared:counts.image_views）
- 最终图片 10 张（10 件作品）：
  - case-01　末班地铁到站屏　[`B01/case-01/final.png`](../B01/case-01/final.png)　900x1600　236495 B
  - case-02　台风应急指挥板　[`B01/case-02/final.png`](../B01/case-02/final.png)　1920x1080　253946 B
  - case-03　半程马拉松破风配速卡　[`B01/case-03/final.png`](../B01/case-03/final.png)　1080x1440　220595 B
  - case-04　精品咖啡烘焙曲线卡　[`B01/case-04/final.png`](../B01/case-04/final.png)　1200x900　155756 B
  - case-05　独立乐队霓虹巡演海报　[`B01/case-05/final.png`](../B01/case-05/final.png)　800x1200　245259 B
  - case-06　锂电 PACK 装配工艺指导　[`B01/case-06/final.png`](../B01/case-06/final.png)　1600x1000　274436 B
  - case-07　围棋棋谱解说图　[`B01/case-07/final.png`](../B01/case-07/final.png)　1200x1200　239177 B
  - case-08　宠物疫苗接种提醒　[`B01/case-08/final.png`](../B01/case-08/final.png)　1080x1080　185785 B
  - case-09　潮汐与海泳安全牌　[`B01/case-09/final.png`](../B01/case-09/final.png)　1080x1350　191533 B
  - case-10　社区旧物集市导览横幅　[`B01/case-10/final.png`](../B01/case-10/final.png)　1920x640　189776 B
- 交付产物：35 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`B01/snapshot-usage.md`](../B01/snapshot-usage.md)　[`B01/task-metrics.json`](../B01/task-metrics.json)　[`B01/gallery.html`](../B01/gallery.html)（附加 HTML 浏览版）
- 实际输出：`outputs/run-20261002-220723-mimo/B01/`　实际临时：`tmp/run-20261002-220723-mimo/B01/`

### B02　为一个自选项目设计完整视觉生态

- 状态：**completed**　轨道：B　墙钟：79609 s
- 轮次：单轮连续视觉迭代
- 请求 39 次（200 × 31 / 失败 7 / 状态未记录 1）　迭代 43 行　读图 47 次（declared:counts.image_views）
- 最终图片 10 张（10 件作品）：
  - case-01　迁徙季开幕海报　[`B02/case-01/final.png`](../B02/case-01/final.png)　1080x1620　220101 B
  - case-02　湿地导览地图　[`B02/case-02/final.png`](../B02/case-02/final.png)　1920x720　165945 B
  - case-03　观鸟须知立牌　[`B02/case-03/final.png`](../B02/case-03/final.png)　900x1600　154699 B
  - case-04　每日观测看板　[`B02/case-04/final.png`](../B02/case-04/final.png)　1920x1080　222559 B
  - case-05　新手工作坊手册封面　[`B02/case-05/final.png`](../B02/case-05/final.png)　1000x1400　168065 B
  - case-06　野外记录表　[`B02/case-06/final.png`](../B02/case-06/final.png)　830x1170　87951 B
  - case-07　志愿者证　[`B02/case-07/final.png`](../B02/case-07/final.png)　1040x660　72427 B
  - case-08　十月活动日程　[`B02/case-08/final.png`](../B02/case-08/final.png)　1748x760　159482 B
  - case-09　年度数据年报卡　[`B02/case-09/final.png`](../B02/case-09/final.png)　1080x1080　135315 B
  - case-10　认养滩涂捐赠页　[`B02/case-10/final.png`](../B02/case-10/final.png)　1080x1526　191282 B
- 交付产物：38 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`B02/snapshot-usage.md`](../B02/snapshot-usage.md)　[`B02/task-metrics.json`](../B02/task-metrics.json)　[`B02/gallery.html`](../B02/gallery.html)（附加 HTML 浏览版）
- 实际输出：`outputs/run-20261002-220723-mimo/B02/`　实际临时：`tmp/run-20261002-220723-mimo/B02/`

### B03　用十件作品探索DSL的创意边界

- 状态：**completed**　轨道：B　墙钟：89799 s
- 轮次：单轮连续视觉迭代
- 请求 78 次（200 × 68 / 失败 10 / 状态未记录 0）　迭代 62 行　读图 70 次（declared:counts.image_views）
- 最终图片 10 张（10 件作品）：
  - case-01　《蓝调不在场》深夜演出海报　[`B03/case-01/final.png`](../B03/case-01/final.png)　1080x1528　263211 B
  - case-02　环贸中心大堂楼层导视　[`B03/case-02/final.png`](../B03/case-02/final.png)　1920x720　244341 B
  - case-03　潮汐音乐节丝网印票根　[`B03/case-03/final.png`](../B03/case-03/final.png)　1600x640　65155 B
  - case-04　极速圈速计时板　[`B03/case-04/final.png`](../B03/case-04/final.png)　1920x1080　179949 B
  - case-05　城市鸟类图鉴内页 PLATE 03　[`B03/case-05/final.png`](../B03/case-05/final.png)　1000x1414　182307 B
  - case-06　《折叠城市》杂志封面　[`B03/case-06/final.png`](../B03/case-06/final.png)　1080x1440　93707 B
  - case-07　夜航登机牌　[`B03/case-07/final.png`](../B03/case-07/final.png)　1748x760　140684 B
  - case-08　ELEVATION 深度与材质规范 v2.4　[`B03/case-08/final.png`](../B03/case-08/final.png)　1200x1500　209634 B
  - case-09　东港站到发信息看板　[`B03/case-09/final.png`](../B03/case-09/final.png)　1920x480　124832 B
  - case-10　软木园等轴测导览图　[`B03/case-10/final.png`](../B03/case-10/final.png)　1200x1200　122860 B
- 交付产物：36 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`B03/snapshot-usage.md`](../B03/snapshot-usage.md)　[`B03/task-metrics.json`](../B03/task-metrics.json)　[`B03/gallery.html`](../B03/gallery.html)（附加 HTML 浏览版）
- 实际输出：`outputs/run-20261002-220723-mimo/B03/`　实际临时：`tmp/run-20261002-220723-mimo/B03/`

### B04　自主研究一个真实主题并制作十件视觉特辑

- 状态：**completed**　轨道：B　墙钟：59087 s
- 轮次：单轮连续视觉迭代
- 请求 84 次（200 × 63 / 失败 11 / 状态未记录 10）　迭代 21 行　读图 33 次（declared:counts.image_views）
- 最终图片 10 张（10 件作品）：
  - case-01　封面：23:59:60 那一秒钟　[`B04/case-01/final.png`](../B04/case-01/final.png)　1080x1528　184223 B
  - case-02　一秒有多长？——定义的五次落点　[`B04/case-02/final.png`](../B04/case-02/final.png)　1748x760　181385 B
  - case-03　1972 年的三条钟：TAI / UTC / UT1　[`B04/case-03/final.png`](../B04/case-03/final.png)　1920x1080　203526 B
  - case-04　27 次闰秒全表　[`B04/case-04/final.png`](../B04/case-04/final.png)　1200x1600　200127 B
  - case-05　27 次的节奏：年代与年份分布　[`B04/case-05/final.png`](../B04/case-05/final.png)　1100x1500　160657 B
  - case-06　为什么步长必须是 1 秒　[`B04/case-06/final.png`](../B04/case-06/final.png)　1080x1080　166079 B
  - case-07　23:59:60 那一分钟（2012-06-30 现场）　[`B04/case-07/final.png`](../B04/case-07/final.png)　1920x480　81701 B
  - case-08　一段创纪录的静默：空窗对照　[`B04/case-08/final.png`](../B04/case-08/final.png)　1400x1050　109040 B
  - case-09　决定：从 0.9 秒到 2035　[`B04/case-09/final.png`](../B04/case-09/final.png)　800x2000　234822 B
  - case-10　反向的一秒与工程师工具箱　[`B04/case-10/final.png`](../B04/case-10/final.png)　1600x640　161306 B
- 交付产物：37 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`B04/snapshot-usage.md`](../B04/snapshot-usage.md)　[`B04/task-metrics.json`](../B04/task-metrics.json)　[`B04/gallery.html`](../B04/gallery.html)（附加 HTML 浏览版）
- 实际输出：`outputs/run-20261002-220723-mimo/B04/`　实际临时：`tmp/run-20261002-220723-mimo/B04/`

### B05　从零构想产品并设计十个关键使用画面

- 状态：**completed**　轨道：B　墙钟：12100 s
- 轮次：单轮连续视觉迭代
- 请求 68 次（200 × 60 / 失败 7 / 状态未记录 1）　迭代 6 行　读图 47 次（declared:counts.image_views）
- 最终图片 10 张（10 件作品）：
  - case-01　楼栋剖面总览　[`B05/case-01/final.png`](../B05/case-01/final.png)　1600x1000　216801 B
  - case-02　我家出多少 · 手机　[`B05/case-02/final.png`](../B05/case-02/final.png)　540x1180　131872 B
  - case-03　三种分摊模型对比　[`B05/case-03/final.png`](../B05/case-03/final.png)　1500x980　216115 B
  - case-04　顾虑台账　[`B05/case-04/final.png`](../B05/case-04/final.png)　1440x1024　269560 B
  - case-05　造价与补贴　[`B05/case-05/final.png`](../B05/case-05/final.png)　1760x900　241212 B
  - case-06　签约与公示 · 手机　[`B05/case-06/final.png`](../B05/case-06/final.png)　480x1040　115302 B
  - case-07　602 室最终确认 · 平板　[`B05/case-07/final.png`](../B05/case-07/final.png)　900x1340　184535 B
  - case-08　施工进度 · 超宽　[`B05/case-08/final.png`](../B05/case-08/final.png)　1920x760　166943 B
  - case-09　交付验收 · 竖屏　[`B05/case-09/final.png`](../B05/case-09/final.png)　1000x1560　257796 B
  - case-10　十年总账　[`B05/case-10/final.png`](../B05/case-10/final.png)　1560x900　128823 B
- 交付产物：37 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`B05/snapshot-usage.md`](../B05/snapshot-usage.md)　[`B05/task-metrics.json`](../B05/task-metrics.json)　[`B05/gallery.html`](../B05/gallery.html)（附加 HTML 浏览版）
- 实际输出：`outputs/run-20261002-220723-mimo/B05/`　实际临时：`tmp/run-20261002-220723-mimo/B05/`

### B06　把十个日常信息难题变成惊艳而好用的作品

- 状态：**completed**　轨道：B　墙钟：84925 s
- 轮次：单轮连续视觉迭代
- 请求 81 次（200 × 78 / 失败 2 / 状态未记录 1）　迭代 30 行　读图 30 次（declared:counts.image_views）
- 最终图片 10 张（10 件作品）：
  - case-01　货架单价换算　[`B06/case-01/final.png`](../B06/case-01/final.png)　1680x1040　188511 B
  - case-02　当日用药卡　[`B06/case-02/final.png`](../B06/case-02/final.png)　540x1240　120134 B
  - case-03　体检报告行动清单　[`B06/case-03/final.png`](../B06/case-03/final.png)　1440x1080　182806 B
  - case-04　电费阶梯账单　[`B06/case-04/final.png`](../B06/case-04/final.png)　1760x980　191976 B
  - case-05　站台到发与换乘　[`B06/case-05/final.png`](../B06/case-05/final.png)　1920x620　159005 B
  - case-06　信用卡分期真实年化　[`B06/case-06/final.png`](../B06/case-06/final.png)　900x1400　184878 B
  - case-07　退租押金扣减瀑布　[`B06/case-07/final.png`](../B06/case-07/final.png)　560x1180　149028 B
  - case-08　降水概率怎么读　[`B06/case-08/final.png`](../B06/case-08/final.png)　1000x1000　115469 B
  - case-09　路侧停车限时计费　[`B06/case-09/final.png`](../B06/case-09/final.png)　840x1340　152527 B
  - case-10　快递到件时间窗　[`B06/case-10/final.png`](../B06/case-10/final.png)　1600x900　157316 B
- 交付产物：37 项（`snapshot-usage.md`、`task-metrics.json` 为每题必备）
- 单题入口：[`B06/snapshot-usage.md`](../B06/snapshot-usage.md)　[`B06/task-metrics.json`](../B06/task-metrics.json)　[`B06/gallery.html`](../B06/gallery.html)（附加 HTML 浏览版）
- 实际输出：`outputs/run-20261002-220723-mimo/B06/`　实际临时：`tmp/run-20261002-220723-mimo/B06/`

## 3. 目录结构

```
outputs/run-20261002-220723-mimo/
  _suite/            index.md  gallery.md  snapshot-usage.md  task-metrics.json  suite-state.json  (+ gallery.html)
  A01/ .. A24/       每题：作品 PNG + 同名 .snapshot + snapshot-usage.md + task-metrics.json（部分题另有归档草稿）
  B01/ .. B06/       每题：case-01/ .. case-10/{final.png,final.snapshot,case.md} + snapshot-usage.md + task-metrics.json + portfolio/gallery 等
tmp/run-20261002-220723-mimo/
  <task>/            requests.jsonl  iterations.jsonl  （B 类另有 tool-usage.jsonl）以及每一次尝试的 .snapshot / .png
  _suite/            events.jsonl（追加式事件）  checkpoints/state-0000NN.json（不可覆盖的编号快照）  各阶段脚本
```

以上目录均相对总任务根（`path_base: "suite_root"`）；文档内的本地链接则相对文档所在目录（`path_base: "document"`）。

## 4. 留痕位置

- **追加式事件**：`tmp/run-20261002-220723-mimo/_suite/events.jsonl`（62 行，从任务启动一路追加到收尾）
- **编号检查点**：`tmp/run-20261002-220723-mimo/_suite/checkpoints/state-0000NN.json`（共 38 份，只增不改）
- **逐请求留痕**：每题 `requests.jsonl`，含 request_id、起止时刻、耗时、HTTP 状态、字节数、Server-Timing、ratelimit_remaining、请求/响应文件路径与错误摘要
- **逐迭代留痕**：每题 `iterations.jsonl`，含 DSL 哈希、PNG 哈希、读图路径与读图结论、verdict、findings 与 changes
- **工具使用留痕**：B01–B06 另有 `tool-usage.jsonl`
- **根 `.gitignore`**：总任务根一份，只排除运行时缓存（`__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`），`outputs/` 与 `tmp/` 中的成品与过程证据一律不排除

## 5. 声明

- 全部 124 张最终图片均为 open-snapshot 服务返回的原始字节，未经任何后期处理；每张都有同名 `.snapshot`。
- 每张最终图片都用读图工具实际打开并核对了画幅与刊头编号之后才落盘；串图后被丢弃的重读已单独标注。
- 研究类题目（B04/B05/B06）在拿不到法条、国家标准或服务标准原文时，一律不引用条款号、不写罚则金额、不写国标数字、不写机构背书，二手线索只标「检索摘要（来源，日期）」，全部数值标 DEMO。
- token / 图像使用量 / 费用平台未提供，全套为 null，不以字数、渲染次数或剩余额度替代。

