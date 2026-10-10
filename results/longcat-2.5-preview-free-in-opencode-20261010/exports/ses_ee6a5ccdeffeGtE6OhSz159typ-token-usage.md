# Token 消耗报告：ses_ee6a5ccdeffeGtE6OhSz159typ

- **命令来源**：`npx ccusage@latest opencode session --json --no-color`（ccusage v20.0.28）
- **会话 ID**：`ses_ee6a5ccdeffeGtE6OhSz159typ`
- **模型**：`longcat-2.5-preview-free`
- **统计口径**：该会话全部已落库消息的累计用量

## 汇总

| 指标 | 数值 |
|---|---:|
| Input tokens | 1,543,035 |
| Output tokens | 162,980 |
| Cache read tokens | 84,917,376 |
| Cache creation tokens | 0 |
| **Total tokens** | **86,651,682** |
| **Total cost** | **$2.995286** |

## 模型明细

| 模型 | Input | Output | Cache read | Cache creation | Total tokens | Cost |
|---|---:|---:|---:|---:|---:|---:|
| longcat-2.5-preview-free | 1,543,035 | 162,980 | 84,917,376 | 0 | 86,651,682 | $2.995286 |

## 说明

- Cache read 占总 token 的 98.0%（84,917,376 / 86,651,682），实际非缓存输入仅 1,543,035。
- 成本为 ccusage 按 LiteLLM 价目表折算的等价值；`*-free` 模型为免费额度模型，此处金额仅作参考量级。
- 该会话无子线程（`parent_id` 为空），报告仅含本会话自身用量。
