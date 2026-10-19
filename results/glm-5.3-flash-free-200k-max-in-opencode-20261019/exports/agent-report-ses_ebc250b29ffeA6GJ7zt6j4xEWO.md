# agent 会话 Token 报告:`ses_ebc250b29ffeA6GJ7zt6j4xEWO`

**支持范围**:本平台(opencode)为完整支持。可保证:SQLite 会话树、按消息类型求和、compaction 归因、分时段对账、工具清单、独立复核。
本技能只对 opencode、claude、codex、gemini 四个平台实现了本地存储适配;其余 ccusage 平台只能给出 ccusage 的聚合数字,**不保证统计完整**。

- **快照时间**:2026-10-19 09:41:42 +0800
- **平台**:opencode(判定依据:ccusage 行的 `agent` 字段)
- **统计工具**:`npx -y ccusage@latest session --json --no-offline`(实时定价),另有技能内置的独立复核
- **数据来源**:`~/.local/share/opencode/opencode.db`(全量扫描 91 行 ccusage 输出后按 id 匹配)
- **范围**:只含该会话。它没有子会话,因此不涉及其他任何会话。

## 1. 会话身份

| 字段 | 值 |
| --- | --- |
| Session ID | `ses_ebc250b29ffeA6GJ7zt6j4xEWO` |
| 标题 | Snapshot DSL 30题批量任务全流程交付 |
| slug | quick-cabin |
| agent | build |
| 模型 | `glm-5.3-flash-free`(provider `opencode`,variant `max`) |
| 工作目录 | `D:/mine/test/glm-5.3-flash` |
| opencode 版本 | 2.0.30 |
| 消息行数 | 2,490(assistant 2,382、synthetic 49、compaction 38、system 9、idle 6、user 6) |

只由 **6 条 user 消息**驱动,却产生了 2,382 个 assistant 回合,是长时间自主执行的任务。

## 2. 会话树:子会话 0 个

四项依据全部指向同一结论:

1. 递归展开 `session_v2.parent_id`,只得到根节点自身。
2. `fork_session_id`、`fork_boundary`、`metadata`、`parent_id` 均为空,没有 fork 关系。
3. 工具调用清单:`shell` 847、`read` 741、`edit` 656、`write` 298、`grep` 67、`glob` 28、`webfetch` 23、`websearch` 11、`execute` 1。**没有 `task`/`agents` 等派生子代理的调用**(`execute` 是代码执行工具,不创建会话)。
4. 消息正文里 grep `ses_[A-Za-z0-9]{20,34}` 的外部引用为空。

因此 30 个任务全部在这一个会话内顺序完成,统计只需覆盖它自己。

## 3. Token 消耗

| 字段 | 数值 |
| --- | --- |
| Input tokens | 10,170,075 |
| Output tokens | 1,106,969 |
| Cache read tokens | 289,435,428 |
| Cache creation tokens | 0 |
| **Total tokens** | **302,299,726** |
| **Total cost** | **无法计价**(见第 5 节) |
| Reasoning tokens(取自数据库) | 1,587,254 |

口径说明:`totalTokens` 由 `input + output + cache_read + reasoning` 构成(10,170,075 + 1,106,969 + 289,435,428 + 1,587,254 = 302,299,726,精确成立),但 ccusage 不单独输出 reasoning,该值取自数据库。`rollouts_aggregated = 1`,即一个会话对应一行,无需跨文件聚合。

结构占比:缓存读取占 **95.74%**(289,435,428 / 302,299,726);净输入 + 输出 + reasoning 共 12,864,298 tokens(**4.26%**)。平均每条 assistant 消息搬运约 12.7 万 tokens(127,284),其中缓存读取 121,868、新增输入仅 4,282。

## 4. ccusage 与数据库的差额:38 次上下文压缩

| 口径 | Input | Output | Reasoning | Cache read | 合计 |
| --- | --- | --- | --- | --- | --- |
| ccusage(仅 assistant) | 10,170,075 | 1,106,969 | 1,587,254 | 289,435,428 | 302,299,726 |
| 数据库 `session_v2` 累计列 | 12,678,615 | 1,210,073 | 1,671,418 | 290,747,364 | 306,307,470 |
| 差值 | 2,508,540 | 103,104 | 84,164 | 1,311,936 | 4,007,744 |

差额几乎全部来自 **38 条 `type='compaction'` 消息**(ccusage 不统计压缩事件),其 token 明细:input 2,507,661 / output 103,093 / reasoning 83,492 / cache read 1,311,936。剩余不足 1,600 tokens 的零星残差属未完成请求。

**压缩代价很可观**:38 次压缩的 input 占数据库口径 input 的 **19.8%**(2,507,661 / 12,678,615)。也就是说这个会话将近五分之一的输入开销花在反复生成上下文摘要上,这是它上下文压力大、回合极多的直接证据。真实总消耗应按数据库口径 **306,307,470 tokens** 计,ccusage 的 302,299,726 是不含压缩的下界(低 1.33%)。

## 5. 成本:无法计价

`pricing_verdict = unpriced_everywhere`,定价来源为 **实时 LiteLLM**(`litellm_online`)。`glm-5.3-flash-free` 出现在 `unpriced_models` 里,即公开定价表没有这个模型的条目,`missingPricing = true`,因此 ccusage 返回的 `cost = 0` **不代表免费,而是无法计价**。opencode 自身的 `session_v2.cost` 同样是 `0.0`。

要得到金额,需要该模型的真实单价后按第 3 节的 token 数另行换算(注意区分是否按压缩口径计费)。

## 6. 独立复核

复核口径:从 `session_message` 按消息类型自行求和(assistant 部分),再与 ccusage 行逐字段比对。

| 字段 | 自算值 | ccusage | 差值 |
| --- | --- | --- | --- |
| Input | 10,170,075 | 10,170,075 | 0 |
| Output | 1,106,969 | 1,106,969 | 0 |
| Cache read | 289,435,428 | 289,435,428 | 0 |
| Reasoning | 1,587,254 | ccusage 不输出该字段 | 不可比 |

判定:**`exact`,最大偏差 0.0%**。三个可比字段与 ccusage 完全一致,说明 ccusage 的 opencode 统计与数据库逐条消息求和严格同源,复核通过。

需要注意会话活跃度:会话在快照前 7 分钟(09:34:34)仍有写入,`idle` 与 `updated` 都是这个时间,因此**数字可能继续变化**;本次复核之所以仍能取到 0 偏差,是因为两次读取间隔极短(不足一分钟)。

## 7. 消耗结构

单条 assistant 消息的规模分布:

| 指标 | 值 |
| --- | --- |
| 平均缓存读取 | 121,868 |
| 峰值缓存读取 | 179,520 |
| 平均新增输入 | 4,282 |
| 峰值新增输入 | 175,173 |
| 峰值 reasoning | 32,000 |
| 峰值 output | 23,656 |

峰值 reasoning 正好是 32,000,说明 `variant: max` 的推理预算在部分回合被打顶;峰值新增输入 175,173 接近缓存读取峰值 179,520,即某些回合是**整段上下文缓存失效后的全量重送**。

分时段(hour-of-day 汇总,跨 10-16 至 10-19 四天同小时合并;求和与总量已对账,`hourly_reconciles = true`):

| 时段 | 消息数 | Input | Cache read | Output |
| --- | --- | --- | --- | --- |
| 08 | 34 | 267,473 | 4,926,464 | 2,125 |
| 09 | 66 | 410,261 | 8,780,160 | 58,055 |
| 11 | 43 | 442,888 | 2,563,876 | 23,762 |
| 12 | 208 | 921,213 | 21,664,704 | 79,990 |
| 13 | 124 | 453,115 | 15,753,152 | 54,256 |
| 14 | 154 | 470,548 | 21,164,864 | 47,777 |
| 15 | 230 | 739,840 | 28,620,928 | 79,976 |
| 16 | 307 | 1,116,742 | 37,430,528 | 132,978 |
| 17 | 390 | 1,473,634 | 50,167,104 | 202,790 |
| 18 | 314 | 1,559,759 | 34,735,936 | 153,071 |
| 19 | 271 | 1,362,182 | 32,594,688 | 127,498 |
| 20 | 147 | 475,549 | 19,934,336 | 92,669 |
| 21 | 87 | 476,871 | 11,098,688 | 52,022 |

17 点是全天高峰(390 条消息、缓存读取 5,016 万),12 点与 18–19 点次之;10 点与 22 点之后无活动。缺 10 点这一行说明该时段没有 assistant 消息落库。

## 8. 时间分布

| 项目 | 值 |
| --- | --- |
| 活动区间 | 2026-10-16 16:36:25 → 2026-10-19 09:34:34 |
| elapsed_time(自然流逝) | 64h58m8s |
| 活跃时间 | 17h9m36s(**26.4%** of elapsed) |
| 空闲合计 | 47h48m32s(2,380 个间隔) |
| 最长几段空闲 | 16h57m32s(起 10-17 12:41)、15h24m54s(起 10-18 11:32)、11h1m17s(起 10-19 08:52)、2h53m24s(起 10-18 15:49) |

活跃时间口径:取每条消息 `created → completed` 的区间并集,含模型响应与工具执行时间。

**这 2.7 天是 elapsed_time,不是持续运行。**真正有请求活动的约 17 小时,其余 47.8 小时是空闲(仅三段 10 小时以上的间隔就占 43.4 小时)。第 3、4 节的 token 与压缩次数只对应实际发生的 2,382 个回合。

## 9. 复现命令

```bash
# 采集 + 独立复核(实时定价)
python .qoder/skills/agent-session-token-report/scripts/collect.py ses_ebc250b29ffeA6GJ7zt6j4xEWO

# 子会话核查:递归 parent_id(返回 1 行,即只有自身)
sqlite3 -readonly ~/.local/share/opencode/opencode.db "
WITH RECURSIVE tree(id, depth) AS (
  SELECT 'ses_ebc250b29ffeA6GJ7zt6j4xEWO', 0
  UNION ALL
  SELECT s.id, t.depth+1 FROM session_v2 s JOIN tree t ON s.parent_id=t.id)
SELECT s.id, t.depth, s.title FROM tree t JOIN session_v2 s ON s.id=t.id;"

# 压缩差额:按消息类型求和
sqlite3 -readonly ~/.local/share/opencode/opencode.db "
SELECT type, count(*), sum(json_extract(data,'\$.tokens.input')), sum(json_extract(data,'\$.tokens.cache.read'))
FROM session_message WHERE session_id='ses_ebc250b29ffeA6GJ7zt6j4xEWO'
  AND json_extract(data,'\$.tokens.input') IS NOT NULL GROUP BY type;"
```

## 10. 口径备注

- ccusage 只聚合 `assistant` 类型消息,不含 38 次 compaction;真实总量以数据库口径 306,307,470 为准,ccusage 的 302,299,726 为下界(差 1.33%)。
- `totalTokens` 含 reasoning,但 reasoning 无独立字段,数值取自数据库。
- `cacheCreationTokens` 为 0,该模型只走读取侧缓存。
- 成本无法计价:`glm-5.3-flash-free` 在实时 LiteLLM 定价表里没有条目;即使有条目,ccusage 的费率也未必可从公开表逐条复现,金额应按"工具计算值"对待。
- 数据是时间点快照(2026-10-19 09:41:42),而会话在 09:34:34 仍有写入,后续数字会继续增长。
- 分时段表是按"小时"跨天合并的(10-16 至 10-19),不是单日逐小时。
- 复核结论 `exact` 基于本次采集,opencode 适配器与复核逻辑均已在本机真实数据上验证过。
