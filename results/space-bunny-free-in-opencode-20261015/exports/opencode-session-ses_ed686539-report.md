# opencode 会话 Token 消耗报告:`ses_ed686539cffeAVrXiMBoVXVMnu`

- **统计快照**:2026-10-15 13:24 (+0800)
- **统计工具**:`npx ccusage@latest opencode session --json --offline`(另用 `--no-offline` 复核定价)
- **原始数据**:`~/.local/share/opencode/opencode.db`
- **范围**:本报告只包含该主会话及其 3 个子会话,不含其他会话

## 1. 会话树

| 层级 | Session ID | 标题 | agent | 模型 | 消息数 |
| --- | --- | --- | --- | --- | --- |
| 主会话 | `ses_ed686539cffeAVrXiMBoVXVMnu` | A01–A24与B01–B06全量执行交付 | build | space-bunny-free / variant `max` | 2,276 |
| 子 | `ses_eccc1755bffeoEteZvOrEuO54b` | Build B03 DSL frontier portfolio | general | space-bunny-free / variant `max` | 338 |
| 子 | `ses_ec7cbd376ffel0hc1rf6mgVMdO` | Build B05 product ten screens | general | space-bunny-free / variant `max` | 84 |
| 子 | `ses_ec7cbb178ffeBcasfX7Co9uNTb` | Build B06 everyday info ten | general | space-bunny-free / variant `max` | 150 |

四个会话的 `directory` 均为 `D:/mine/test/spaceb`,模型一致。子会话通过 `session_v2.parent_id` 挂到主会话;已确认这 3 个子会话没有更深层级(孙会话查询返回 0 行),所以会话树只有两层。

3 个子会话对应 B03 / B05 / B06 三个任务,主会话标题写的是 A01–A24 与 B01–B06 全量执行,说明只有这 3 个任务是通过子代理派生的,其余任务在主会话里直接完成。

## 2. ccusage 统计(逐会话)

| 会话 | Input | Output | Cache read | Cache creation | Total tokens | Cost |
| --- | --- | --- | --- | --- | --- | --- |
| 主会话 `…XVMnu` | 5,518,170 | 1,210,536 | 591,288,857 | 0 | 598,741,504 | 无法计价 |
| 子 B03 `…uO54b` | 454,358 | 175,680 | 87,077,515 | 0 | 87,807,657 | 无法计价 |
| 子 B05 `…VMdO` | 141,951 | 61,830 | 10,011,264 | 0 | 10,262,861 | 无法计价 |
| 子 B06 `…uNTb` | 286,729 | 75,823 | 25,298,177 | 0 | 25,705,741 | 无法计价 |
| **合计** | **6,401,208** | **1,523,869** | **713,675,813** | **0** | **722,517,763** | — |

占比:

- 3 个子会话合计 123,776,259 tokens,占整棵树的 **17.13%**;主会话自身占 **82.87%**。
- 缓存读取占整棵树的 **98.78%**(713,675,813 / 722,517,763)。非缓存的 input + output 只有 7,925,077 tokens(**1.10%**),消耗主体是超长上下文被反复读取,而不是新产生的内容。
- 子会话之间差异明显:B03(1.00 亿级)≈ B06(2,571 万)≈ 8.5 × B05(1,026 万),B03 一个会话占子会话总量的 70.9%。

`totalTokens` 的口径包含 reasoning tokens,但 ccusage 没有单独列出该字段(以三个子会话验证:`input + output + cache read + reasoning = totalTokens` 精确成立)。子会话的 reasoning 取自数据库:`100,104`(B03)、`47,816`(B05)、`45,012`(B06);主会话为 `724,385`。

## 3. 成本:ccusage 给不出金额

四个会话的 `totalCost` 都是 `0`,但这不代表免费。ccusage 在模型明细里标了 `"missingPricing": true`,`totals.unpricedModels` 为 `["space-bunny-free"]`,即 LiteLLM 定价表里没有这个模型的条目。

已用两种方式复核:

| 方式 | 结果 |
| --- | --- |
| `--offline`(读本地定价缓存) | 四个会话 cost 均为 0,`missingPricing: true` |
| `--no-offline`(拉取 LiteLLM 实时定价) | 结果相同,仍缺定价 |

所以金额无法从 ccusage 得出。数据库里这四个会话的 `cost` 列也都是 `0.0`,即 opencode 侧同样没有计价。如需金额,只能按 `space-bunny-free` 的真实单价另行计算,token 数已列在上表。

## 4. 主会话:ccusage 与数据库计数不一致的原因

| 口径 | Input | Output | Cache read |
| --- | --- | --- | --- |
| ccusage | 5,518,170 | 1,210,536 | 591,288,857 |
| 数据库 `session_v2`(=逐条消息求和) | 5,933,283 | 1,228,034 | 593,466,805 |
| 差值 | 415,113 | 17,498 | 2,177,948 |

差异完全来自 **compaction(上下文压缩)**:主会话有 7 条 `type='compaction'` 的消息,合计 input 415,011 / output 17,482 / cache read 2,177,052。ccusage 只聚合 `assistant` 类型消息(实测按类型分组:assistant 2,221 条 input 恰为 5,518,170),因此不计入这 7 次压缩的开销。三个子会话没有任何 compaction 消息,所以它们的 ccusage 与数据库数字完全一致。

结论:要评估主会话的真实总消耗,应看数据库口径(598,741,504 + 压缩部分,合计约 5.99 亿 tokens);ccusage 数值是"不含压缩"的下界。

## 5. 时间跨度

活动窗口取自各会话首末条消息时间:

| 会话 | 首条消息 | 末条消息 | 跨度 |
| --- | --- | --- | --- |
| 主会话 | 2026-10-11 13:40:02 | 2026-10-15 09:28:10 | 约 3 天 19 小时 48 分 |
| 子 B03 | 2026-10-13 11:11:39 | 2026-10-13 13:10:31 | 1 小时 58 分 |
| 子 B05 | 2026-10-14 10:18:25 | 2026-10-14 10:51:24 | 33 分 |
| 子 B06 | 2026-10-14 10:18:34 | 2026-10-14 10:51:19 | 33 分 |

主会话的 3 天多是 **elapsed_time(自然流逝时间),中间包含大量空闲间隔**(数据库 `time_idle` 记录最后一次空闲在 2026-10-15 09:28),不能理解为持续运行了 3 天的模型调用。两个子会话 B05 / B06 创建时间相差 9 秒、结束时间相近,是并行派生的;B03 在更早一天单独跑过。

上表的 token 与消耗只对应各会话实际发生的请求次数(主会话 2,276 条消息、2,226 条 assistant),与流逝时长无关。

## 6. 与上一次快照的差值(主会话仍在增长)

本报告与 2026-10-14 11:01 的同工具快照相比:

| 会话 | 指标 | 2026-10-14 | 2026-10-15 | 变化 |
| --- | --- | --- | --- | --- |
| 主会话 | input | 5,141,502 | 5,518,170 | +376,668 |
| 主会话 | output | 1,178,012 | 1,210,536 | +32,524 |
| 主会话 | cache read | 563,297,385 | 591,288,857 | +27,991,472 |
| 主会话 | total | 570,331,455 | 598,741,504 | **+28,410,049** |
| 子 B03 / B05 / B06 | 全部指标 | — | — | 无变化 |

也就是说该会话树**仍在被写入**,只有主会话在继续消耗;引用本报告时请注意它是一个时间点快照。

## 7. 复现命令

```bash
# 会话树(含子会话,已确认无孙会话)
sqlite3 -readonly ~/.local/share/opencode/opencode.db "
WITH RECURSIVE tree(id, depth) AS (
  SELECT 'ses_ed686539cffeAVrXiMBoVXVMnu', 0
  UNION ALL
  SELECT s.id, t.depth+1 FROM session_v2 s JOIN tree t ON s.parent_id=t.id
)
SELECT s.id, t.depth, s.title, s.agent FROM tree t JOIN session_v2 s ON s.id=t.id ORDER BY t.depth;"

# token 统计(ccusage 不支持按 session 过滤,需从全量输出里挑出上述 4 个 sessionId)
npx -y ccusage@latest opencode session --json --offline

# 验证压缩差异:按消息类型分组求和
sqlite3 -readonly ~/.local/share/opencode/opencode.db "
SELECT type, count(*), sum(json_extract(data,'\$.tokens.input'))
FROM session_message WHERE session_id='ses_ed686539cffeAVrXiMBoVXVMnu'
  AND json_extract(data,'\$.tokens.input') IS NOT NULL GROUP BY type;"
```

## 8. 口径备注

- ccusage 从逐条消息聚合且只统计 `assistant` 类型,故不含 compaction 开销;数据库 `session_v2` 的累计列与逐条消息求和一致(主会话差 102 tokens,属未完成请求)。本报告以 ccusage 输出为主,并在第 4 节给出数据库口径作为上界。
- `cacheCreationTokens` 四个会话均为 0,该模型走的是读取侧缓存。
- 定价缺失导致金额为 0,已在第 3 节说明,不要把 `0` 读作免费。
