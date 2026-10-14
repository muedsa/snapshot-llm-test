# opencode 会话 Token 消耗报告

- **查询时间**:2026-10-14
- **统计工具**:`npx ccusage@latest opencode session --json --offline`
- **数据来源**:`~/.local/share/opencode/opencode.db`(含 WAL)

## 1. 会话标识

| 字段 | 值 |
| --- | --- |
| Session ID | `ses_ed688daeeffd34NXZbexRZvfV5` |
| 标题 | 批量生成A01-B06完整任务套件 |
| slug | misty-meadow |
| 工作目录 | `D:/mine/test/longcat` |
| agent | build |
| model | `longcat-2.5-preview-free`(provider: opencode) |
| 消息数 | 308(assistant 271) |

## 2. 子会话:0 个

该会话没有子会话,因此本报告仅统计主会话本身。核查过程:

1. 按 `session_v2.parent_id` 递归展开整棵会话树,结果只有根节点自身;把 db + wal 复制到工作区再查一次(`WHERE parent_id='ses_ed688daeeffd...'`),计数同样为 0,排除未落盘数据。
2. `fork_session_id` / `fork_boundary` / `metadata` 均为空。
3. 遍历该会话 271 条 assistant 消息里的全部工具调用:`shell` 200、`read` 93、`write` 67、`edit` 28、`webfetch` 3、`glob` 2、`execute` 1。没有 `task`/子代理类调用(那条 `execute` 是一次参数为空的失败调用,报 `Invalid arguments for tool "execute"`,未创建会话)。
4. 消息正文中 grep `ses_[A-Za-z0-9]{20,34}` 无任何命中;18 处 `sessionID` 字样全部来自 read 到的接口文档文本,不是真实会话引用。

## 3. ccusage 统计

| 指标 | 数值 |
| --- | --- |
| Input tokens | 1,128,166 |
| Output tokens | 149,685 |
| Cache read tokens | 53,841,792 |
| Cache creation tokens | 0 |
| **Total tokens** | **55,217,002** |
| **Total cost** | **$2.382531** |
| Model | longcat-2.5-preview-free |

结构上,缓存读取占总量的 **97.51%**(53,841,792 / 55,217,002),真正的非缓存 input + output 只有 1,277,851 tokens。也就是说绝大多数消耗来自长上下文反复读取,而非新产生的内容。

补充:ccusage 的 opencode session 视图不输出 reasoning tokens,而 db 里记录了该会话 97,443 reasoning tokens(计入 output 口径之外)。

## 4. 时间跨度(避免误读为工作量)

| 事件 | 时间 |
| --- | --- |
| 创建 | 2026-10-11 13:37:16 |
| 最后一次 idle 记录 | 2026-10-14 09:55:04 |
| 最后更新 | 2026-10-14 10:39:58 |

创建到最后活跃跨越约 3 天,这是 **elapsed_time(自然流逝时间),其中包含大量空闲间隔**,不代表 3 天的持续计算投入。上表的 token 与费用是这段跨度内实际发生的消耗,与流逝时长无关。

## 5. 复现命令

```bash
# 子会话查询(返回 0 行)
sqlite3 -readonly ~/.local/share/opencode/opencode.db "
WITH RECURSIVE tree(id, depth) AS (
  SELECT 'ses_ed688daeeffd34NXZbexRZvfV5', 0
  UNION ALL
  SELECT s.id, t.depth+1 FROM session_v2 s JOIN tree t ON s.parent_id=t.id
)
SELECT s.id, t.depth, s.title FROM tree t JOIN session_v2 s ON s.id=t.id;"

# token 统计(ccusage 不支持按 session 过滤,输出全量后按 sessionId 取目标行)
npx -y ccusage@latest opencode session --json --offline
```

## 6. 数据口径备注

- ccusage 从逐条消息记录聚合,与 `session_v2` 上的累计列存在小幅差异:input 1,128,166(库:1,128,546)、output 149,685(库:149,699)、cache read 53,841,792(库:53,842,304)。本报告以 ccusage 输出为准。
- 使用了 `--offline` 缓存定价数据;`longcat-2.5-preview-free` 有定价条目,费用数值可直接采信。去掉 `--offline` 会改为拉取 LiteLLM 实时定价。
