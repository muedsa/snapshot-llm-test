# A11 被取代的页面 DSL 清单（superseded manifest）

run_id: `r20261014T1536+0800-5f11da`　task: `A11`　path_base: `suite_root`
生成时间: 2026-10-16T11:46:42+08:00　时区: Asia/Shanghai (UTC+08:00)

## 为什么存在这个清单

约定要求失败响应、草稿、临时 DSL 全部保留、不清理也不覆盖尝试。A11 的渲染客户端
`a11_client.render()` 按 `dsl_name` 写 `tmp/<rid>/A11/dsl/<stem>.snapshot`，而页面生成器
`a11_pages.py` 固定传 `dsl_name=<stem>.snapshot`——因此**同一页重渲会覆盖前一版的 DSL 文本**。
这是一次真实的约定偏离（记录为 a11-i8），不能隐瞒，也不能事后补造「原件」。

影响范围严格限定为**页面级**的 3 份中间 DSL 文本。所有响应字节（PNG / 错误 JSON）
始终按 request_id 命名保存在 `responses/`，从未被覆盖，5 份页面响应共 5 个不同 sha256，
所以每一版页面都还能看到，只是 3 份被取代版本的 DSL 源码不可复原。

## 被覆盖的 DSL（不可还原）

| request_id | 迭代 | 版本 | 对应响应（保留） | 被覆盖的 DSL 路径 | 取代原因 |
|---|---|---|---|---|---|
| `req-a11-invoice-page-01-b2f090` | `a11-it-09` | 第一版 第 1 页 | [响应](tmp/r20261014T1536+0800-5f11da/A11/responses/req-a11-invoice-page-01-b2f090.png) | `tmp/r20261014T1536+0800-5f11da/A11/dsl/invoice-page-01.snapshot` | 正文与脚注低于字号下限，按 ≥24/≥20 重排 |
| `req-a11-invoice-page-02-9cdbb8` | `a11-it-10` | 第一版 第 2 页 | [响应](tmp/r20261014T1536+0800-5f11da/A11/responses/req-a11-invoice-page-02-9cdbb8.png) | `tmp/r20261014T1536+0800-5f11da/A11/dsl/invoice-page-02.snapshot` | 同一字号问题，随第 1 页一并重排 |
| `req-a11-invoice-page-01-a5701c` | `a11-it-11` | 第二版试排 第 1 页 | [响应](tmp/r20261014T1536+0800-5f11da/A11/responses/req-a11-invoice-page-01-a5701c.png) | `tmp/r20261014T1536+0800-5f11da/A11/dsl/invoice-page-01.snapshot` | 合计 6 个金额字号不统一（24 px 与 26 px 混用），统一为 26 px |

## 现存（未被覆盖）的页面 DSL

| 路径 | 说明 |
|---|---|
| `tmp/r20261014T1536+0800-5f11da/A11/dsl/invoice-page-01.snapshot` | 终版第 1 页（最后一次渲染 `req-a11-invoice-page-01-74bbd3` 写入，与交付件同字节） |
| `tmp/r20261014T1536+0800-5f11da/A11/dsl/invoice-page-02.snapshot` | 终版第 2 页（最后一次渲染 `req-a11-invoice-page-02-e2f4d1` 写入，与交付件同字节） |
| `tmp/r20261014T1536+0800-5f11da/A11/dsl/v2-invoice-page-01.snapshot` | 终版第 1 页副本（生成器另存的 v2 副本） |
| `tmp/r20261014T1536+0800-5f11da/A11/dsl/v2-invoice-page-02.snapshot` | 终版第 2 页副本 |

探针类 DSL 各用一个独立 `dsl_name`，未发生覆盖，全部保留在 `dsl/` 下。

## 已采取的补救

1. 本清单逐项登记被覆盖对象、对应保留的响应与取代原因，不重建、不伪造成原件。
2. 交付件 `outputs/<rid>/A11/invoice-page-0{1,2}.snapshot` 是终版 DSL 的独立副本，
   与对应 PNG 一一对应、内容完整。
3. `task-metrics.json` 的 `unresolved_issues` 与 `disclosures` 已登记此事及其影响。
4. 后续任务改为按 request_id 命名 DSL，避免同类覆盖（见 `snapshot-usage.md` 跨题经验）。

## 明确不做的

不用生成器重跑后得到的近似文本冒充被覆盖的原件；不删除、不覆盖 `responses/` 下的任何字节。
