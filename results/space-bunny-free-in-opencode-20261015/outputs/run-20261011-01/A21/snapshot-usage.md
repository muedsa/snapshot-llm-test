# A21 使用报告（三轮累计）

> 本题为**预置三轮连续执行**：第一轮按 TASK.md 完成并看图归档后，
> 立即读取 `rounds/round-02.md` 完成第二轮，再读取 `rounds/round-03.md` 完成第三轮，
> 全程不等待用户消息。后续轮的需求文件在第一轮开始前即可访问，
> 因此本任务衡量的是**对可预知需求的连续执行与回归**，不是对隐藏反馈的盲测。

生成时间：2026-10-12T13:07:48+08:00

## 1. 三轮完成状态

| 轮次 | 需求来源 | 状态 |
|---|---|---|
| round-01 | TASK.md | 完成 |
| round-02 | rounds/round-02.md | 完成 |
| round-03 | rounds/round-03.md | 完成 |

三轮共交付 6 张指定 PNG 与 6 份同名 DSL，全部为服务真实响应。

## 2. 全部最终图片

| 轮次 | 尺寸名 | PNG | DSL |
|---|---|---|---|
| round-01 | portrait | `round-01/launch-portrait.png` | `round-01/launch-portrait.snapshot` |
| round-01 | wide | `round-01/launch-wide.png` | `round-01/launch-wide.snapshot` |
| round-02 | portrait | `round-02/launch-portrait.png` | `round-02/launch-portrait.snapshot` |
| round-02 | wide | `round-02/launch-wide.png` | `round-02/launch-wide.snapshot` |
| round-03 | portrait | `round-03/launch-portrait.png` | `round-03/launch-portrait.snapshot` |
| round-03 | wide | `round-03/launch-wide.png` | `round-03/launch-wide.snapshot` |

## 3. 回归对照

| 维度 | round-01 | round-02 | round-03 |
|---|---|---|---|
| 主题 | 深色 | 深色（不变） | 浅色 |
| 主色 | #3730A3 | #3730A3（不变） | #4338CA（同靛蓝系亮端） |
| 品牌构件 | B1–B4 四件 | 形态不变，仅移动缩放 | 形态不变，仅换配色 |
| 主标题 | 1 行 68px | 2 行 52px | 2 行 52px（不变） |
| 赞助方 | 无 | 新增 | 保留 |
| 参加方式 | 无 | 新增 | 保留 |
| 英语短句 | 无 | 无 | 新增 |
| 对比度审计 | 不要求 | 不要求 | contrast-audit.json |

## 4. 三轮共用的关键工程结论

- **`textAlign="left"` 会 400**：服务端只接受 center/right/end 等枚举，left 是默认值。
  横版大量左对齐文字因此统一改为「不写 textAlign」。
- **多轮交付的路径拼接**：共享脚本原先用 `dsl_rel.split('/')[-1]` 取文件名，
  会把 `round-XX/` 前缀丢掉，导致 DSL 与 PNG 落进不同目录。已改为显式 `subdir` 参数。
- **渲染子进程的两个输出流都可能为 None**，直接相加会抛 TypeError 掩盖真实错误；
  错误回传改为 repr 形式。
- **服务端偶发「HTTP 200 但响应体 0 字节」**：本 run 在 A17/A18/A19/A20/A21 均出现，
  全部按可重试的传输层故障处理，失败响应体保留在各自 `responses/` 下。

## 5. 目录

- 题目输出根：`outputs/run-20261011-01/A21/`（含 `round-01/`–`round-03/` 与本报告、累计指标）
- 题目临时根：`tmp/run-20261011-01/A21/`（`drafts/round-01..03/`、`preview/`、`responses/`、`requests.jsonl`）

## 6. 未解决事项

见各轮报告第 9 节；累计层面无跨轮阻塞。
