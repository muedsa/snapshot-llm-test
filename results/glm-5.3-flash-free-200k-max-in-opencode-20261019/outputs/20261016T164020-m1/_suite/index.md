# 全套总索引 · Snapshot 全套任务（30 题）

- run：`20261016T164020-m1` · profile：all（A01–A24 + B01–B06）· 状态：**全部完成（30/30）**
- 时间：2026-10-16T16:40:20+08:00 起 → 2026-10-19T09:33:50.723+08:00 收（含跨日运行与真实夜间暂停；单题时长见各题 task-metrics）
- 服务：https://open-snapshot.muedsa.com（真实渲染，响应字节即最终图）·DSL 文档缓存自 B04 起
- 套件交付：[gallery.md](gallery.md)（逐图 124 张）· [snapshot-usage.md](snapshot-usage.md) ·
  [task-metrics.json](task-metrics.json) · [suite-state.json](suite-state.json)

## 状态总表

| # | 题 | 状态 | 终图 | 渲染 200/4xx | 看图 | 单题入口 |
|---|---|---|---|---|---|---|
| 1 | A01 | completed | 1 | 5 / 0 | 4 | [A01](../A01/operations.png) |
| 2 | A02 | completed | 2 | 4 / 0 | 4 | [A02](../A02/agenda-mobile.png) |
| 3 | A03 | completed | 1 | 2 / 4 | 3 | [A03](../A03/system-pulse.png) |
| 4 | A04 | completed | 1 | 4 / 0 | 4 | [A04](../A04/conversion-story.png) |
| 5 | A05 | completed | 1 | 2 / 0 | 2 | [A05](../A05/sensor-report.png) |
| 6 | A06 | completed | 1 | 1 / 0 | 1 | [A06](../A06/dependency-map.png) |
| 7 | A07 | completed | 2 | 7 / 1 | 4 | [A07](../A07/network-map.png) |
| 8 | A08 | completed | 1 | 2 / 1 | 2 | [A08](../A08/wayfinding.png) |
| 9 | A09 | completed | 1 | 3 / 0 | 3 | [A09](../A09/transform-atlas.png) |
| 10 | A10 | completed | 1 | 8 / 0 | 7 | [A10](../A10/compositing-lab.png) |
| 11 | A11 | completed | 2 | 8 / 2 | 4 | [A11](../A11/invoice-page-01.png) |
| 12 | A12 | completed | 4 | 8 / 0 | 2 | [A12](../A12/desktop.png) |
| 13 | A13 | completed | 4 | 11 / 0 | 4 | [A13](../A13/brand-banner.png) |
| 14 | A14 | completed | 8 | 34 / 0 | 4 | [A14](../A14/card-K01.png) |
| 15 | A15 | completed | 1 | 12 / 0 | 8 | [A15](../A15/reconstructed.png) |
| 16 | A16 | completed | 1 | 1 / 0 | 2 | [A16](../A16/corrected-report.png) |
| 17 | A17 | completed | 8 | 10 / 1 | 10 | [A17](../A17/example-01.png) |
| 18 | A18 | completed | 1 | 4 / 0 | 4 | [A18](../A18/three-act-story.png) |
| 19 | A19 | completed | 3 | 4 / 0 | 3 | [A19](../A19/grid-scene.png) |
| 20 | A20 | completed | 1 | 2 / 1 | 2 | [A20](../A20/annotated-map.png) |
| 21 | A21 | completed | 6 | 14 / 8 | 22 | [A21](../A21/round-01/launch-portrait.png) |
| 22 | A22 | completed | 3 | 7 / 1 | 17 | [A22](../A22/round-01/dashboard.png) |
| 23 | A23 | completed | 7 | 37 / 0 | 15 | [A23](../A23/cover.png) |
| 24 | A24 | completed | 3 | 8 / 0 | 11 | [A24](../A24/action-card.png) |
| 25 | B01 | completed | 10 | 18 / 0 | 11 | [B01](../B01/portfolio.md) |
| 26 | B02 | completed | 10 | 16 / 0 | 6 | [B02](../B02/portfolio.md) |
| 27 | B03 | completed | 10 | 24 / 0 | 13 | [B03](../B03/portfolio.md) |
| 28 | B04 | completed | 10 | 20 / 1 | 17 | [B04](../B04/portfolio.md) |
| 29 | B05 | completed | 10 | 30 / 2 | 33 | [B05](../B05/portfolio.md) |
| 30 | B06 | completed | 10 | 39 / 0 | 41 | [B06](../B06/portfolio.md) |

**合计**：终图 124（A 类 64 + B 类 60）· 渲染 367（200×345 + 失败×22）·
服务 HTTP 总行 398（其余为文档/字体/探针等记录，不重复计渲染）· 看图（显式字段合计）263 · 迭代台账行 193。

## 共享准备与复用
- 文档缓存：ai-guide.md 与 DSL 文档于 B04 实抓一次（`tmp/20261016T164020-m1/B04/renders/`），后续题复用不重复计请求。
- 共享客户端：`tmp/20261016T164020-m1/_suite/snapshot_client.py`（渲染 + requests.jsonl 留痕）。
- 字体规约：CJK 用 Noto Sans CJK SC，数字用 Inter（仅纯 ASCII）；均在 A14 黑体探针与 A15 探针验证。

## 计时说明
- 套件墙钟：2026-10-16T16:40:20+08:00 → 2026-10-19T09:33:50.723+08:00。单题 elapsed 合计 39955.6 s（约 11.1 小时）；跨题含未计入的会话间隙（含 A19→A20、B05→B06 等夜间断点），
  因此单题之和≠总墙钟；各题等待时间如实标注（无等待记 0，不可测记 null）。

## 复现
- 逐题：`tmp/<run>/<题>/` 下 `requests.jsonl` / `iterations.jsonl`（B 题另有 tool-usage.jsonl）与 `renders/` 全部请求响应留痕。
- 逐题 DSL：`tmp/<run>/<题>/dsl/`（B 题）或 `tmp/<run>/<题>/*.snapshot`（A 题），版本递增不可覆盖。

## B06 特别说明（最后题）
- B06《日常信息重构十件》为自主选题（十件独立：符号语法/价格与概率语义/体感转译/行为卡/读数训练）。
- 根文档：[portfolio](../B06/portfolio.md) · [gallery](../B06/gallery.md) · 证据 [problem-evidence.json](../B06/problem-evidence.json) ·
  [design-review.md](../B06/design-review.md)（可观改善 vs 未验证效果）。
