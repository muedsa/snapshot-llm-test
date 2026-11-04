# 手册结论与出处

本手册的四章结论都来自实际阅读的服务文档与实际请求结果。下表把每条关键技术结论对应到文档位置与本任务里的例子。

| # | 结论 | 出处 | 对应例子 |
|---|---|---|---|
| 1 | 接口为 `POST https://open-snapshot.muedsa.com/snapshot`，请求体为 UTF-8 纯文本 DSL，成功返回 PNG 原始字节 | 服务指南 `https://open-snapshot.muedsa.com/ai-guide.md`（Quick start / Response 节）；本套 `run-config.json` 的 `service` 字段 | example-01 |
| 2 | 失败响应是 JSON：`{code, message, requestId, diagnostic}`；`code` 取值如 `PARSE_ERROR`、`RENDER_ERROR` | 服务指南错误表；本套在 A03/A17 中实际收到 `PARSE_ERROR`（`Element [Raw] … can only be used in the Text`） | 第一章正文 |
| 3 | 429/503 带 `Retry-After`，应按其等待后重试 | 服务指南限流一节 | 第一章「重试」要点 |
| 4 | `Snapshot` 根只有 `background`、`debug`、`type` 属性，没有 `width`/`height`；尺寸由内容决定 | DSL 参考 `https://snapshot.muedsa.com/reference/parser-tags.md`（Snapshot 节） | example-02 |
| 5 | `Row`/`Column` 主轴无界时放 `Expanded` 会报 `Layout size is infinite` | 同上（Expanded 节）；本套 A03 实际触发该错误 | example-02 |
| 6 | `Positioned` 的父节点必须是 `Stack`/`IndexedStack`，否则报 `renderBox.parentData must be StackParentData` | 同上（Positioned 节）；本套 A03 实际触发 | example-02、第四章 |
| 7 | `Container` 上的 `left`/`top` 不会生效，绝对定位属于 `Positioned` | 同上（Container 属性表）；本任务 A17 首版实测：给 Container 写 left/top 后所有元素叠在 (0,0) | example-02 及其说明 |
| 8 | 普通 `Text` 会裁掉首尾空白；`Raw` 是 `Text` 的子节点，用于保留空白 | 同上（Text/Raw 节）；本任务实测 `<Raw>` 作为顶层元素被拒：`can only be used in the Text` | example-03 |
| 9 | `<`、`&` 需用 CDATA 包裹才能原样输出 | 同上（文本与转义节）；本套 A11 结算单第 2 页用过同样写法 | example-03 |
| 10 | 8 位颜色是 `#RRGGBBAA`，末两位为 alpha；`#FFFFFF33` 是 20% 白 | 同上（颜色格式节）；本套 A05/A10 采样验证过 | example-03 |
| 11 | `ImageFiltered` 作用于整棵子树；`BackdropFilter` 在已有内容上再叠模糊 | 同上（ColorFiltered/ImageFiltered/BackdropFilter 节） | example-04 |
| 12 | `ImageFiltered` 需要确定尺寸的子树，否则定位不稳定；用 `SizedBox` 包住最稳 | 本任务实测：未包 `SizedBox` 时模糊块被排到画布 (0,0) | example-04 |
| 13 | 富文本通过在 `Text` 内嵌 `Text` 实现，各 span 共用基线 | 同上（Text 子节点节）；本套 A11 第 2 页「PAID / 已结算」实测通过 | 第三章「要点」 |
| 14 | 最终交付必须打开真实 PNG 自检，并保留请求/迭代日志 | 本套 `AGENTS.md`「交付质量优先」与「进度、留痕与断点继续」两节 | 第四章正文 |

## 阅读方式说明

- 文档 1–3 条读自 `ai-guide.md` 的 Quick start、Response、Error、Rate limit 小节。
- 第 4–13 条读自 `parser-tags.md` 对应标签小节，并在本套 A03/A05/A10/A11/A17 的实际请求中复核。
- 第 12 条是本任务的实测发现（文档未强调），因此写在手册里作为提醒。
