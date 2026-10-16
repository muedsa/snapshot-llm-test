# opencode 会话分析报告:`ses_ebdc3ba96ffeJrISp1LSM4uiPI`

- **统计快照**:2026-10-16 16:00 (+0800)
- **统计工具**:`npx ccusage@latest opencode session --json`(分别用 `--offline` 与 `--no-offline` 各跑一次)
- **原始数据**:`~/.local/share/opencode/opencode.db`
- **范围**:本报告只包含该会话。它没有子会话,因此不涉及任何其他会话数据。

## 1. 会话身份

| 字段 | 值 |
| --- | --- |
| Session ID | `ses_ebdc3ba96ffeJrISp1LSM4uiPI` |
| 标题 | 完成A01至B06共30个任务 |
| slug | curious-star |
| agent | build |
| 模型 | `nemotron-3.5-super-vl-free`(provider `opencode`,variant `xhigh`) |
| 工作目录 | `D:/mine/test/nemotron-3.5-super-vl` |
| opencode 版本 | 2.0.30 |
| 消息行数 | 973(assistant 921、synthetic 35、idle 7、user 5、compaction 3、system 2) |

值得注意:整个运行只由 **5 条 user 消息**驱动,却产生了 921 条 assistant 回合——典型的长自主执行任务。

## 2. 子会话:0 个

递归展开 `session_v2.parent_id` 只得到根节点;显式按父 ID 计数也是 0;`parent_id`、`fork_session_id`、`fork_boundary`、`metadata` 全部为空。

该会话 921 条 assistant 消息里的工具调用种类为:`shell` 556、`write` 275、`read` 214、`edit` 198、`grep` 27、`webfetch` 10、`execute` 9、`browser.preview` 2、`fetch` 1。没有 `task` 或任何子代理派发类调用(9 次 `execute` 全部 `status: completed`,是代码执行工具,不创建会话)。在全部消息正文里 grep `ses_[A-Za-z0-9]{20,34}` 命中 0 次。

结论:30 个任务全部在这一个会话内顺序完成,没有并行子代理。这与同批次其他运行的结构不同,横向比较成本时要注意口径不可比。

## 3. Token 消耗

ccusage 输出(`--json`):

| 字段 | 数值 |
| --- | --- |
| Input tokens | 8,548,404 |
| Output tokens | 735,048 |
| Cache read tokens | 453,909,824 |
| Cache creation tokens | 0 |
| **Total tokens** | **463,812,857** |
| **Total cost** | **$30.67961949**(实时定价) |

`totalTokens` 口径包含 reasoning tokens,但 ccusage 不单独输出该字段。按数据库里 assistant 消息的 reasoning 合计 `619,581` 验证:`8,548,404 + 735,048 + 453,909,824 + 619,581 = 463,812,857`,与 ccusage 的 totalTokens 精确相等。

### 成本:必须用实时定价

这是本次分析与之前不同的地方:

| 运行方式 | 结果 |
| --- | --- |
| `--offline`(本地定价缓存) | `cost: 0`、`missingPricing: true` |
| `--no-offline`(拉取 LiteLLM) | `cost: 30.67961949`、`missingPricing: false` |

即本地缓存表里没有 `nemotron-3.5-super-vl-free`,但在线定价有——不能因为离线结果为 0 就判定该模型无价。opencode 自身的 `session_v2.cost` 仍是 `0.0`(未计价)。

一个保留意见:`$30.68` 是 ccusage 算出的值,它实际套用的费率我无法从公开的 LiteLLM 定价表复现——遍历表中 58 个含 `nemotron` 的条目,按"缓存读单独计价""缓存读按输入价""reasoning 计入输出"等口径组合,误差 1% 内均无命中。所以这个金额宜作为工具计算值对待,而不是可逐条对账的账单。

## 4. ccusage 与数据库的差额:3 次上下文压缩

| 口径 | Input | Output | Reasoning | Cache read | 合计 |
| --- | --- | --- | --- | --- | --- |
| ccusage(仅 assistant) | 8,548,404 | 735,048 | 619,581 | 453,909,824 | 463,812,857 |
| 数据库 `session_v2` 累计列 | 8,651,973 | 736,942 | 664,493 | 456,034,464 | 466,087,872 |
| 差值 | 103,569 | 1,894 | 44,912 | 2,124,640 | 2,275,015 |

差额来源是 3 条 `type='compaction'` 消息,ccusage 不统计:

| 压缩时间 | Input | Output |
| --- | --- | --- |
| 2026-10-16 14:16:57 | 51,415 | 1,247 |
| 2026-10-16 14:54:29 | 47,222 | 0 |
| 2026-10-16 14:59:25 | 3,862 | 631 |
| 合计 | 102,499 | 1,878 |

cache read 两侧完全吻合(`453,909,824 + 2,124,640 = 456,034,464`),input 侧另有 1,070 tokens 的零星残差(未完成请求)。压缩集中在收尾一小时(14:16–14:59),说明上下文是在末段被压满的。

因此:**ccusage 数字是不含压缩的下界,真实消耗约 4.66 亿 tokens(高 0.49%)**;第 3 节的 `$30.68` 同样不含压缩部分,真实金额略高,但由于费率构成不可见,无法精确外推。

## 5. 消耗结构:缓存读取压倒性占比

- 缓存读取占 `453,909,824 / 463,812,857 = **97.87%**`;非缓存(input + output + reasoning)只有 9,903,033 tokens(**2.13%**)。
- 平均每条 assistant 消息搬运约 50.4 万 tokens,其中缓存读取 **493,380**、新增输入仅 9,292。
- 单条消息峰值:cache read 927,904、input 902,312 —— 上下文已逼近百万 token 量级;reasoning 单条峰值正好 `131,072`(= 128K),说明 `xhigh` 推理预算在部分回合被打满。

分时段(assistant 消息,单位 tokens):

| 小时 | 消息数 | Input | Cache read | Output |
| --- | --- | --- | --- | --- |
| 09 | 237 | 1,294,012 | 53,853,120 | 168,103 |
| 10 | 82 | 394,132 | 34,852,768 | 57,044 |
| 11 | 222 | 936,586 | 133,683,216 | 150,951 |
| 12 | 106 | 1,912,132 | 78,520,624 | 52,234 |
| 13 | 111 | 2,251,854 | 89,612,112 | 45,183 |
| 14 | 45 | 1,249,811 | 39,318,848 | 141,925 |
| 15 | 117 | 509,877 | 24,069,136 | 119,608 |

(按时段求和与总量精确对账:input 8,548,404、cache 453,909,824、output 735,048。)

12–14 点这三小时新增 input 达 5,413,797(占全天 63%),同时消息数只有 262 条,是缓存反复失效、整段上下文重送的特征;11 点则相反,消息多(222)但新增 input 少,主要是命中缓存在读。若要压缩消耗,重点在这段的高频 cache miss。

## 6. 时间分布(区分工作时间与空闲)

活动区间取各消息 `time.created → time.completed` 做区间并集:

| 项目 | 值 |
| --- | --- |
| 会话跨度(首→末) | 2026-10-16 09:03:28 → 15:40:31 |
| elapsed_time(自然流逝) | 6h37m03s |
| 合并后的模型/工具活动区间 | 5h19m26s(**80.5%** of elapsed) |
| 空闲间隔合计 | 1h17m36s(920 个间隔) |
| 其中 ≥10 分钟的长间隔 | 2 段,合计 1h10m59s |
| 最长单次间隔 | 49m52s(起于 11:09:19),另有一段 21m07s(起于 15:02:21) |

也就是说这段运行里 **约 1 小时 18 分是空闲/等待,不计为模型工作**,其中一小时集中在那两段长间隔(11:09 与 15:02 之后,后者紧跟第 3 次压缩)。上面第 3、5 节的 token 与费用只对应实际发生的 921 个模型回合,与流逝时长无关。

## 7. 复现命令

```bash
# 子会话查询(返回 0 行)
sqlite3 -readonly ~/.local/share/opencode/opencode.db "
WITH RECURSIVE tree(id, depth) AS (
  SELECT 'ses_ebdc3ba96ffeJrISp1LSM4uiPI', 0
  UNION ALL
  SELECT s.id, t.depth+1 FROM session_v2 s JOIN tree t ON s.parent_id=t.id
)
SELECT s.id, t.depth, s.title FROM tree t JOIN session_v2 s ON s.id=t.id;"

# token 与成本(注意 --offline 会把该模型判为无价)
npx -y ccusage@latest opencode session --json --no-offline

# 压缩差额
sqlite3 -readonly ~/.local/share/opencode/opencode.db "
SELECT type, count(*), sum(json_extract(data,'\$.tokens.input')), sum(json_extract(data,'\$.tokens.cache.read'))
FROM session_message WHERE session_id='ses_ebdc3ba96ffeJrISp1LSM4uiPI'
  AND json_extract(data,'\$.tokens.input') IS NOT NULL GROUP BY type;"
```

## 8. 口径备注

- ccusage 只聚合 `assistant` 类型消息,不含 `compaction`;数据库 `session_v2` 列与逐条消息求和一致(input 侧差 1,070,属未完成请求)。本报告以 ccusage 为主口径,并在第 4 节给出数据库口径作为上界。
- `cacheCreationTokens` 为 0,该模型走读取侧缓存。
- reasoning tokens 已计入 `totalTokens`,但没有独立字段;数值取自数据库。
- 金额来自 `--no-offline`;离线缓存给出 0,不代表免费也不代表无价。
- 数据是时间点快照,该会话 `time_idle` 已是 15:40:31,短期不会再变。
