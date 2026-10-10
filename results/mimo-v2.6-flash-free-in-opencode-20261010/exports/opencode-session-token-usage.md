# OpenCode 会话 Token 消耗汇总

- 生成时间：2026-10-10 11:00:53 +08:00
- 统计来源：`npx ccusage@latest opencode session --json --no-color`（原始输出见 [_ccusage_raw.json](_ccusage_raw.json)）
- 会话元数据：`opencode-cli.exe api get /api/session`
- 父会话：`ses_f031101b7ffeD7ubHPRzDVybL9`（执行A01至B06全部30个任务）
- 统计范围：父会话 + 其 11 个子线程（`parentID` = `ses_f031101b7ffeD7ubHPRzDVybL9`）
- 估算成本为 ccusage 依据 LiteLLM 价格表计算；`mimo-v2.6-flash-free` 为免费模型，金额仅供参照。

## 总体汇总（父会话 + 全部子线程）

| 指标 | 数值 |
| --- | ---: |
| 会话数 | 12 |
| Input tokens | 31,906,239 |
| Output tokens | 3,222,781 |
| Reasoning tokens（由总 tokens 差额推算） | 4,449,228 |
| Cache read tokens | 604,043,776 |
| Cache write tokens | 0 |
| 总 tokens | 643,622,024 |
| 估算成本 | $8.306359 |

### 子线程小计

| 指标 | 数值 |
| --- | ---: |
| 子线程数 | 11 |
| Input tokens | 2,837,027 |
| Output tokens | 273,848 |
| Reasoning tokens（由总 tokens 差额推算） | 580,980 |
| Cache read tokens | 24,579,648 |
| Cache write tokens | 0 |
| 总 tokens | 28,271,503 |
| 估算成本 | $0.705359 |

## 子线程明细

| # | 创建时间 (UTC+8) | session id | 标题 | agent | 模型 | Input | Output | Reasoning | Cache read | Cache write | 合计 | 占子线程总量 | 估算成本 |
| ---: | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2026-10-03 18:15 | `ses_efebc9497ffe0pb21lQxrPA8I7` | View and QA 8 A14 card PNGs | general | mimo-v2.6-flash-free | 150,969 | 8,174 | 14,385 | 708,544 | 0 | 882,072 | 3.1% | $0.029436 |
| 2 | 2026-10-04 13:50 | `ses_efa8934dfffeFr2XjWH4YMSTWy` | Visual QA of A16 zoom crops | general | mimo-v2.6-flash-free | 671,253 | 20,784 | 48,586 | 2,740,480 | 0 | 3,481,103 | 12.3% | $0.121072 |
| 3 | 2026-10-04 15:44 | `ses_efa20804effeEECLqVMo5ZcrrB` | View example-04 render | general | mimo-v2.6-flash-free | 41,204 | 8,042 | 16,235 | 379,008 | 0 | 444,489 | 1.6% | $0.013627 |
| 4 | 2026-10-04 17:02 | `ses_ef9d9e0f2ffeVry3J782FtZan6` | View handbook pages 3 and 4 | general | mimo-v2.6-flash-free | 30,490 | 3,164 | 3,158 | 242,240 | 0 | 279,052 | 1.0% | $0.006717 |
| 5 | 2026-10-04 18:10 | `ses_ef99b8253ffeRsomr6Nf3lhujy` | View A18 v03 image | general | mimo-v2.6-flash-free | 146,984 | 28,220 | 71,185 | 1,665,984 | 0 | 1,912,373 | 6.8% | $0.053076 |
| 6 | 2026-10-04 18:53 | `ses_ef973eff7ffe0POVBsADZP3q12` | Verify delivered A18 image | general | mimo-v2.6-flash-free | 301,054 | 52,051 | 132,307 | 4,019,456 | 0 | 4,504,868 | 15.9% | $0.105022 |
| 7 | 2026-10-04 19:55 | `ses_ef93aadc5ffe2v32Zyp4NM4us3` | Final view of delivered A18 | general | mimo-v2.6-flash-free | 203,632 | 55,732 | 76,051 | 1,740,096 | 0 | 2,075,511 | 7.3% | $0.070280 |
| 8 | 2026-10-04 21:05 | `ses_ef8fb0773ffeKLugegEmmgwaRe` | Final A18 deliverable check | general | mimo-v2.6-flash-free | 1,102,407 | 53,911 | 161,002 | 11,539,328 | 0 | 12,856,648 | 45.5% | $0.246823 |
| 9 | 2026-10-04 23:21 | `ses_ef87e7366ffeynPEWbXJGs9tUp` | Verify A19 grid v01 | general | mimo-v2.6-flash-free | 35,916 | 7,156 | 20,204 | 245,248 | 0 | 308,524 | 1.1% | $0.013376 |
| 10 | 2026-10-04 23:43 | `ses_ef86a9e88ffeNuVGVizctB4Ks3` | View A19 grid v02 and occlusion | general | mimo-v2.6-flash-free | 111,905 | 22,106 | 26,624 | 1,168,704 | 0 | 1,329,339 | 4.7% | $0.032583 |
| 11 | 2026-10-05 00:39 | `ses_ef836f8c4ffeh0nVjH7ufU0Zbx` | View A19 grid v03 | general | mimo-v2.6-flash-free | 41,213 | 14,508 | 11,243 | 130,560 | 0 | 197,524 | 0.7% | $0.013346 |
| | | **合计** | | | | **2,837,027** | **273,848** | **580,980** | **24,579,648** | **0** | **28,271,503** | **100.0%** | **$0.705359** |

## 父会话本身（不计入上面的子线程合计）

| session id | 标题 | agent | Input | Output | Reasoning | Cache read | Cache write | 合计 | 估算成本 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `ses_f031101b7ffeD7ubHPRzDVybL9` | 执行A01至B06全部30个任务 | build | 29,069,212 | 2,948,933 | 3,868,248 | 579,464,128 | 0 | 615,350,521 | $7.601000 |

## 模型明细（父会话 + 子线程）

| 模型 | 会话数 | Input | Output | Reasoning | Cache read | Cache write | 合计 | 估算成本 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mimo-v2.6-flash-free | 12 | 31,906,239 | 3,222,781 | 4,449,228 | 604,043,776 | 0 | 643,622,024 | $8.306359 |

## 备注与数据完整性

- 统计范围：父会话 1 个 + 子线程 11 个，共 12 个会话，均按 `sessionId` 与 ccusage 用量记录一一对应。
- 范围内 12 个会话在 ccusage 中均有用量记录，无缺失项。
- `Reasoning` 列为 `totalTokens` 减去 input/output/cache 四项之和的差额（ccusage JSON 未单列 reasoning 字段），因此各列相加等于“合计”。
- `Cache write tokens` 全为 0，说明这些会话未产生缓存写入计费。

本文件由 [_ccusage-join.ps1](_ccusage-join.ps1) 生成：以 [_ccusage_raw.json](_ccusage_raw.json)（ccusage 输出）与 `/api/session` 元数据按 `sessionId` 关联；token 数为各会话累计值。
