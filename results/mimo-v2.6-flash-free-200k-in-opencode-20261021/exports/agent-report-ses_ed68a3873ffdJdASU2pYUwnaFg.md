# Agent 会话 Token 消耗报告 — ses_ed68a3873ffdJdASU2pYUwnaFg（quiet-cabin）

## 1. 支持范围与采集说明

**支持范围**:本平台(opencode)为完整支持。可保证:SQLite 会话树、按消息类型求和、compaction 归因、分时段对账、工具清单、独立复核。
- 本技能只对 opencode、claude、codex、gemini 四个平台实现了本地存储适配;其余 ccusage 平台只能给出 ccusage 的聚合数字,**不保证统计完整**。

- **快照时间**：2026-10-22 08:52:01 +0800（`captured_at`）
- **平台**：opencode（`platform_resolution`：取自 ccusage 行的 `agent` 字段；该会话行的 agent = opencode）
- **统计工具与参数**：`agent-session-token-report` 技能的 `scripts/collect.py <session-id>`，`platform=auto`（实际解析为 opencode）、默认开启交叉复核与 ccusage 取数、定价来源 `litellm_online`；未使用 `--no-ccusage`、`--no-crosscheck`、`--offline-only`
- **数据来源**：opencode 本地 SQLite（`%USERPROFILE%\.local\share\opencode\opencode.db`，只读 URI 连接）+ ccusage 全量扫描（`ccusage_rows_scanned` = 99 行，本机 agent 集合 claude/codex/gemini/opencode，命中本会话的仅 opencode 行）；`zstd_backend` = python-zstandard（opencode 无 `.zst` 分片，不受压缩后端影响）
- **取数方式**：ccusage 数据只经由 `collect.py` 内部取得，没有绕过脚本单独调用 `ccusage session -i`（该形式在本平台取不到行，会得到空结果）
- **覆盖度告警**：无 —— `coverage_warning` / `coverage_warnings` 均未出现，消息行解析失败数 0，没有未读取文件
- **自指污染核查**：本采集**不在被分析会话内执行**。依据：含本次采集指令的消息只存在于另一个独立的新建会话中；被分析会话的最后一条消息为 2026-10-21 18:42:32（早于快照 850 分钟）；fact pack 未出现 `self_reference_suspected`。故下列数字不含"测量自身的开销"
- **统计范围**：仅本会话及其子会话（会话树共 1 个会话，子会话 0 个）；不包含同库中的兄弟会话

## 2. 会话身份

| 项 | 值 |
| ---- | ---- |
| 会话 ID | `ses_ed68a3873ffdJdASU2pYUwnaFg` |
| slug / 标题 | quiet-cabin / 按all配置完成A01–B06全部30个任务 |
| agent | build |
| 模型 | mimo-v2.6-flash-free（providerID = opencode） |
| 工作目录 | 本机当前工作目录（`directory` 与采集目录一致） |
| 客户端版本 | opencode 2.0.26 |
| 创建 / 最后消息 / time_viewed | 2026-10-11 13:35:47 / 2026-10-21 18:42:32 / 2026-10-21 18:42:32 |
| 消息行数 | 3,666 条（解析失败 0 条） |
| 派生参数 | `parent_id` / `fork_session_id` / `fork_boundary` / `metadata` 全为空 |
| rollout 文件 | 不适用（opencode 存储为 SQLite 消息表，无 rollout 文件、无压缩分片） |

消息类型分布：user 15、assistant 3,472（其中 3,460 行带 token）、synthetic 66、compaction 77、idle 15、system 21，合计 3,666。

说明：会话行 `time_updated` = 2026-10-22 08:42:33（快照前 10 分钟），但 `time_idle`、`time_viewed` 与最后一条消息时间均为 2026-10-21 18:42:32，且今日没有任何新消息行 —— 该字段变化未伴随新消息，不产生新 token，本报告全部数字不含今日请求。

## 3. 会话树与子会话结论

**子会话：0 个**（`has_children = false`，且 `children_verified = true`，属已核查结论而非未验证）。

核查依据（opencode 递归 `parent_id` 机制）：

1. 对 `session_v2` 做递归 `parent_id` 展开（WITH RECURSIVE），以本会话为根只返回自身 1 个节点；另单独执行 `SELECT id FROM session_v2 WHERE parent_id = 'ses_ed68a3873ffdJdASU2pYUwnaFg'`，结果为空
2. 本会话 `parent_id`、`fork_session_id`、`fork_boundary`、`metadata` 全为 null，不存在 fork 血缘
3. `referenced_session_ids_in_messages` = `{}`：正文消息中没有引用任何外部 `ses_` 会话 ID
4. `tool_call_counts` 无派生子会话类调用（无 task/agent/spawn 类工具）；适配器另把 `execute`（33 次）列为 agent-like 工具提及，但本会话树中不存在任何 `parent_id` 指向它的子记录，33 次调用均未产生新会话

工具调用清单（共 3,981 次）：shell 1,331、read 944、edit 937、write 488、grep 170、webfetch 38、glob 37、execute 33、websearch 2、browser 1。

## 4. Token 消耗

| 会话 | basis | input | output | cache read | cache creation | reasoning | total | cost |
| ---- | ---- | ----: | ----: | ----: | ----: | ----: | ----: | ----: |
| ses_ed68a3873ffdJdASU2pYUwnaFg | ccusage | 30,626,861 | 1,852,977 | 398,804,096 | 0 | 3,323,054 | 434,606,988 | $6.853700688799996 |
| **合计** | ccusage | **30,626,861** | **1,852,977** | **398,804,096** | **0** | **3,323,054** | **434,606,988** | **$6.853700688799996** |

- 合计取自 `family_totals.sum`；`mixed_basis = false`，`bases = ["ccusage"]`，单一 basis，逐项与合计一致
- `reasoning` 列来自本地消息求和（ccusage 行的 `reasoning_output_tokens` 为 `null`，即"没有这个数值"而非 0），但 ccusage 的 `totalTokens` 已含 reasoning（见第 11 节差额校验）
- `rollouts_aggregated = 1`：ccusage 按 `period` 聚合到 1 个分片，无多分片合并问题
- 合计**不是下限**：`sessions_without_numbers` / `sum_missing_sessions` / `aggregated_missing` 均未出现，每个会话都有完整数字
- 占比：会话树只有 1 个会话，合计即本会话；缓存读取占 total 的 91.7620%，input 7.0470%，reasoning 0.7646%，output 0.4264%（占率为本次按 fact pack 原值计算）

## 5. 成本

`ccusage.pricing_verdict` = **priced_online**（定价来源 `litellm_online`，在线价目表）。

- 金额：**$6.853700688799996**（家族 `cost_sum`，`cost_rows` = 1）
- 模型 mimo-v2.6-flash-free 的所有行都已计价：`missing_pricing = false`，`unpriced_models = []`，无需列点名
- 金额可对账到 fact pack `ccusage.primary_rows[].modelBreakdowns`（modelName、input/output/cacheRead/cacheCreation 与上表逐项一致）
- 口径提醒：模型名含 "free"，但 ccusage 按 litellm 在线价目表给出了非零金额；同时 opencode 库自带的 `session_v2.cost` 列自记为 0.0。两者是不同记账口径，差额来源未在本次采集中定位 —— 本报告的金额一律引用 ccusage 的计价结果，不引用库内自记列

## 6. 独立复核（本地存储 vs ccusage）

复核实现：本地侧由 opencode SQLite 适配器**按消息类型求和**（assistant 行），与 ccusage 行逐字段比对。

- `agreement` = **exact**，`verdict` = **ok**
- `max_abs_delta_pct` = 0.0%，`worst_field` = input，参与比较的数值字段 3 个

| 字段 | 本地（assistant 行求和） | ccusage | delta | delta_pct |
| ---- | ----: | ----: | ----: | ----: |
| input | 30,626,861 | 30,626,861 | 0 | 0.0% |
| output | 1,852,977 | 1,852,977 | 0 | 0.0% |
| cache_read | 398,804,096 | 398,804,096 | 0 | 0.0% |
| reasoning | 3,323,054 | null | — | —（至少一侧没有可比数值，未参与差额比较） |

- `minutes_since_last_activity` = **850.1 分钟**（约 14 小时 10 分），`last_activity_basis` = **带时区 ISO**：ccusage 的 `last_activity` = 2026-10-21T10:42:03.070Z（UTC），换算本地为 2026-10-21 18:42:03，与库内最后消息时间 2026-10-21 18:42:32 相符。会话在读取前已停止写入远超 5 分钟，不存在快照错开问题；`clock_skew_suspected` 未出现
- 判定依据：三个可比字段全部 delta = 0，落在 `exact` 档，且 `verdict = ok` 与判定相称；无 `unbounded_delta_fields`（没有"一侧 0 另一侧非零"的情形）
- 结论：本地求和与 ccusage **完全一致**，token 总量可信；`reasoning` 单列字段因 ccusage 侧为 `null` 未参与比较，不构成不一致

## 7. ccusage 与本地存储的差额归因

ccusage 只统计 assistant 行；opencode 库的会话级汇总（`session_v2` rollup）额外包含 **compaction（上下文压缩）行**。差额归因如下：

| 字段 | 库 rollup（`db_rollup`） | ccusage | 差额 | compaction 行 | 残差 |
| ---- | ----: | ----: | ----: | ----: | ----: |
| input | 31,860,823 | 30,626,861 | 1,233,962 | 1,233,569 | 393 |
| output | 2,110,680 | 1,852,977 | 257,703 | 257,685 | 18 |
| cache_read | 405,982,144 | 398,804,096 | 7,178,048 | 7,177,536 | 512 |
| reasoning | 3,361,180 | 3,323,054 | 38,126 | 37,974 | 152 |
| 合计（含 reasoning） | 443,314,827 | 434,606,988 | 8,707,839 | 8,706,764 | 1,075 |

- compaction 解释了差额的 **99.98765%**（8,706,764 / 8,707,839）；残差合计 1,075 token（<0.012%），各字段分别为 input 393 / output 18 / cache_read 512 / reasoning 152，量级与一条消息的单字段尾数相当，**未进一步定位**（推测为会话 rollup 列与消息表的更新时点差，尚无证据可确认）
- assistant 行本身：本地求和与 ccusage 差额为 0（第 6 节），全部差额来自 compaction

compaction 明细：库内 compaction 行 **77 条**（其中 76 条带 token，1 条全零：2026-10-15 17:45:47），`crosscheck.compaction_excluded_from_ccusage.rows` = 76，按日汇总：

| 日期 | 次数 | input | output | reasoning | cache_read |
| ---- | ----: | ----: | ----: | ----: | ----: |
| 2026-10-11 | 1 | 83,963 | 1,896 | 8 | 98,304 |
| 2026-10-12 | 4 | 131,175 | 11,060 | 646 | 238,912 |
| 2026-10-13 | 8 | 186,419 | 22,961 | 2,121 | 719,424 |
| 2026-10-14 | 2 | 2,908 | 6,047 | 135 | 159,424 |
| 2026-10-15 | 12 | 212,364 | 34,313 | 8,310 | 875,136 |
| 2026-10-16 | 1 | 698 | 3,114 | 63 | 87,680 |
| 2026-10-19 | 17 | 183,963 | 52,524 | 8,637 | 1,355,200 |
| 2026-10-20 | 8 | 5,728 | 26,807 | 8,126 | 794,688 |
| 2026-10-21 | 24 | 426,351 | 98,963 | 9,928 | 2,848,768 |
| **合计** | **77** | **1,233,569** | **257,685** | **37,974** | **7,177,536** |

每次压缩发生的时间（共 77 次，本地时间）：

```
2026-10-11  14:33:56
2026-10-12  10:11:12 10:56:32 11:36:58 12:16:35
2026-10-13  08:56:55 10:26:10 11:07:56 11:40:07 12:05:00 12:13:34 12:52:21 13:10:28
2026-10-14  10:28:04 10:42:04
2026-10-15  12:02:49 12:23:30 12:55:24 13:12:12 13:35:24 14:09:18 15:04:25 15:39:48 16:22:36 16:56:51 17:45:47(全零) 17:55:28
2026-10-16  09:39:58
2026-10-19  10:40:46 11:15:40 11:58:39 12:37:56 13:12:50 14:02:06 14:27:31 14:55:01 16:10:16 16:45:29 17:24:28 17:52:44 18:37:56 19:14:43 19:57:34 20:24:59 20:55:58
2026-10-20  18:44:15 19:48:12 20:14:54 20:55:38 21:23:40 21:54:32 22:21:33 23:56:21
2026-10-21  00:37:52 00:51:02 01:26:54 01:39:42 01:50:59 02:32:57 02:44:17 03:35:21 03:55:35 04:28:40 09:19:50 09:57:11 10:18:26 13:16:34 14:00:19 14:35:02 15:13:51 15:42:41 16:13:18 16:53:42 17:21:19 17:39:24 18:11:29 18:38:25
```

单次压缩消耗最大的几次（input）：2026-10-15 17:55:28（192,953）、2026-10-13 13:10:28（162,460）、2026-10-21 00:51:02（145,110）、2026-10-11 14:33:56（83,963）、2026-10-19 19:57:34（77,288）。

## 8. 消耗结构

- **缓存读取占比**：398,804,096 / 434,606,988 = **91.7620%**；input 7.0470%、reasoning 0.7646%、output 0.4264%、cache creation 0
- **单条平均与峰值**（采样行 3,460 条带 token 的 assistant 消息，`per_message_peaks`）：

| 指标 | 平均 | 峰值 |
| ---- | ----: | ----: |
| input | 8,852 | 176,734 |
| cache_read | 115,261 | 179,712 |
| reasoning | — | 32,002 |
| output | — | 19,672 |

- **分时段表**（`hourly_reconciles` = true：逐小时求和与 assistant 总量逐项完全相等 —— rows 3,460、input 30,626,861、cache_read 398,804,096、output 1,852,977）：

| 小时 | 行数 | input | cache_read | output |
| ---- | ----: | ----: | ----: | ----: |
| 00 | 73 | 568,074 | 6,511,488 | 41,525 |
| 01 | 119 | 591,627 | 12,822,656 | 37,601 |
| 02 | 77 | 499,652 | 9,542,848 | 73,569 |
| 03 | 127 | 942,992 | 16,773,952 | 57,031 |
| 04 | 40 | 763,176 | 4,698,176 | 20,530 |
| 05–07 | — | — | — | 该三小时无任何 assistant 消息行（不是 0 值记录） |
| 08 | 23 | 297,750 | 2,305,728 | 7,357 |
| 09 | 324 | 1,735,177 | 32,198,976 | 141,163 |
| 10 | 389 | 3,166,937 | 44,055,360 | 189,075 |
| 11 | 197 | 2,592,882 | 23,445,824 | 101,498 |
| 12 | 326 | 2,465,198 | 40,331,840 | 185,457 |
| 13 | 338 | 3,471,721 | 37,738,496 | 169,639 |
| 14 | 257 | 2,310,291 | 30,268,608 | 150,672 |
| 15 | 159 | 1,619,264 | 19,288,640 | 70,758 |
| 16 | 148 | 1,457,888 | 18,444,288 | 79,371 |
| 17 | 187 | 1,116,680 | 22,486,912 | 118,927 |
| 18 | 231 | 2,675,408 | 24,908,608 | 135,900 |
| 19 | 167 | 2,087,837 | 19,771,648 | 86,673 |
| 20 | 140 | 858,849 | 16,879,680 | 96,972 |
| 21 | 68 | 462,888 | 7,992,384 | 48,249 |
| 22 | 58 | 710,719 | 6,796,800 | 35,282 |
| 23 | 12 | 231,851 | 1,541,184 | 5,728 |

09–14 点是消耗高峰：共 1,831 行、input 合计 15,742,206，占全部 input 的 51.40%（按 fact pack 逐小时原值计算）。

## 9. 时间分布

| 项 | 值 |
| ---- | ---- |
| elapsed（跨天总墙钟） | **245h6m44s**（2026-10-11 13:35:47 → 2026-10-21 18:42:32） |
| active | **42h16m33s**（占 elapsed 17.2%） |
| idle | **202h50m11s** |
| 消息间隔数（gap_count） | 3,470 |

`active_note`（口径原文）：取每条消息 created->completed 的区间并集,含模型响应与工具执行。

- 这是 opencode 适配器的口径（消息区间并集），与 JSONL 平台的"相邻事件阈值"口径**不可互相比较**
- 时间解析：本会话 `unparsable_message_rows` = 0，没有解析失败的消息行；opencode 适配器不存在 `events_timestamp_unparsed` 计数项，时间分布无需做偏小修正
- ≥10 分钟的长空档（前 5）：2026-10-19 10:01:16 起 72h19m34s、2026-10-15 11:12:12 起 24h20m28s、2026-10-20 18:18:24 起 21h3m36s、2026-10-14 09:32:33 起 20h20m51s、2026-10-13 08:52:06 起 19h40m17s
- 提醒：elapsed 是跨 11 天的总墙钟时间，idle 占 82.8%，不得理解为整段都在调用模型

## 10. 复现命令

```powershell
# 采集（platform 自动判定，含交叉复核与 ccusage 定价；报告与 fact pack 落在当前目录）
python "$env:USERPROFILE\.agents\skills\agent-session-token-report\scripts\collect.py" ses_ed68a3873ffdJdASU2pYUwnaFg --out-dir .

# 需要原始事实包（第 7/8 节分片与 compaction 明细）时：
#   ./agent-report-ses_ed68a3873ffdJdASU2pYUwnaFg-facts.json
# 或加 --full-output 重跑取完整 stdout
```

本次辅助查询（本目录内 `tmp_report_probe.py`、`tmp_report_fields.py`、`tmp_report_derive.py`），核心 SQL：

```sql
-- 会话身份与 rollup（只读，opencode.db）
SELECT id, slug, title, agent, model, directory, version, parent_id, fork_session_id,
       time_created, time_updated, time_idle, time_viewed, cost,
       tokens_input, tokens_output, tokens_reasoning, tokens_cache_read, tokens_cache_write
FROM session_v2 WHERE id = 'ses_ed68a3873ffdJdASU2pYUwnaFg';

-- 子会话核查（结果为空）
SELECT id FROM session_v2 WHERE parent_id = 'ses_ed68a3873ffdJdASU2pYUwnaFg';

-- 自指核查：本次指令只出现在另一个会话；目标会话最后消息时间
SELECT session_id, time_created FROM session_message
WHERE data LIKE '%agent-session-token-report%' ORDER BY time_created DESC;
SELECT count(*), max(time_created) FROM session_message
WHERE session_id = 'ses_ed68a3873ffdJdASU2pYUwnaFg';
```

（库连接使用 `file:...opencode.db?mode=ro` 只读 URI，路径经 `%USERPROFILE%` 解析，未写死盘符。）

## 11. 口径备注

1. **reasoning 是否单列**：opencode 本地把 reasoning 存为独立列并单独求和（3,323,054）；ccusage 行的 `reasoning_output_tokens` 为 `null`（无此数值，不是 0）。
2. **`totalTokens` 含 reasoning**：ccusage `total` = 434,606,988 = input 30,626,861 + output 1,852,977 + cache_read 398,804,096 + cache_creation 0 + reasoning 3,323,054，差额精确等于本地 reasoning 求和，即 total **含** reasoning。
3. **金额来源与可对账性**：金额取 ccusage 在线定价（`priced_online`，`litellm_online`）= $6.853700688799996，可对账到 fact pack 的 `modelBreakdowns`；opencode 库自带 `cost` 列为 0.0，属另一记账口径、差额来源未定位，本报告不引用它作为成本结论。
4. **快照性质**：一切数字止于 2026-10-22 08:52:01 +0800；目标会话已停止写入 850.1 分钟，token 量为终值（会话行 `time_updated` 今日被触碰，但无新消息、无新请求）。重新采集只会改变 compaction 残差一类的时点差，不会显著改变结论。
5. **适配器与复核验证**：opencode 使用 SQLite 深度适配器 + 独立复核（按消息类型求和），两者均为本技能已实现并验证的路径；本次实跑复核 `exact / ok`，非 `unsupported`、非 `not_applicable`。
6. **合计完整性**：家族合计为确切值而非下限 —— 无缺失会话、无 `aggregated_missing`、无未读文件、无覆盖度告警；唯一未参与比较的是 ccusage 侧为 `null` 的 reasoning 字段。
7. **子会话结论**：`children_verified = true`，本报告写"子会话 0 个"是核查过的结论；不存在"未验证"情形。
8. **自指**：采集不在被分析会话内执行，数字不含本次测量自身的开销（依据见第 1 节）。

---
事实包：`./agent-report-ses_ed68a3873ffdJdASU2pYUwnaFg-facts.json`（可复现凭证，请勿删除）
