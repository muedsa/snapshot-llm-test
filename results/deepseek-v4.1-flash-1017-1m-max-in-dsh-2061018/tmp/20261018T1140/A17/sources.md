# A17 技术结论与来源

本手册每页的结论都对应实际阅读的官方页面或本套实测证据；示例 ID 对应 `examples.json`。

| # | 结论 | 来源（实际阅读） | 示例 |
|---|---|---|---|
| 1 | 请求体是 UTF-8 文本 DSL；成功响应 `image/png` 二进制，失败响应 JSON，含 `code`/`message`/`requestId`。错误 JSON 不能存成 `.png`。 | [open-snapshot ai-guide](https://open-snapshot.muedsa.com/ai-guide.md) | P01 / example-01 |
| 2 | 根尺寸由有界布局决定，不是 HTML viewport；Row/Column 的主轴必须有界，`Expanded` 只在 Row/Column 内分配剩余空间。 | [Snapshot layout guide](https://snapshot.muedsa.com/guides/layout/)；[parser-tags](https://snapshot.muedsa.com/reference/parser-tags/) Row/Column/Expanded/Stack 条目 | P02 / example-02 |
| 3 | 普通 `Text` 内容会 trim 首尾空格；`Raw` 保留空白，但只能出现在 Text 创建的行内内容树中。 | [parser-tags · Text / Raw](https://snapshot.muedsa.com/reference/parser-tags/) | P03 / example-03 |
| 4 | 字面 `<`、`>`、`&` 应放在 Text 的 `text` 属性中，避免被当作标签解析；代码展示可用 XML 转义并在 examples.json 还原原文。 | [parser-tags · Text](https://snapshot.muedsa.com/reference/parser-tags/)；本页 example-03 的 `Text text="A < B & C > D"` | P03 / example-03 |
| 5 | 颜色支持 `#RRGGBBAA`，最后两位是 alpha；`#F9736280` 是约 50% 的珊瑚红，不是 AARRGGBB。 | [parser-tags · 颜色](https://snapshot.muedsa.com/reference/parser-tags/) | P03 / example-03 |
| 6 | 官方解析标签表没有 CDATA；不要把 XML 的 CDATA 当作 Snapshot 的转义机制，使用 Raw / text 属性。 | [parser-tags 标签表](https://snapshot.muedsa.com/reference/parser-tags/)（未列 CDATA） | P03 / example-03 |
| 7 | `ImageFiltered` 对单个子树做高斯模糊，`sigmaX`/`sigmaY` 必须有限且非负；`ClipRRect` 可限制模糊范围。 | [parser-tags · ColorFiltered/ImageFiltered/BackdropFilter](https://snapshot.muedsa.com/reference/parser-tags/) | P04 / example-04 |
| 8 | 本套实测 `BackdropFilter` 容易受背景/裁剪影响（A03 首次无可见模糊）；背景模糊的可靠做法是裁剪后的背景副本 + ImageFiltered。 | `tmp/20261018T1140/A03/composite-audit.json`、`tmp/20261018T1140/A10/composite-audit.json` | P04 / example-04 |
| 9 | 交付要保留服务原始 PNG、同名完整 DSL、请求/响应/失败 JSON 与查看记录；错误与重试不能删。 | [open-snapshot ai-guide](https://open-snapshot.muedsa.com/ai-guide.md)；本套 AGENTS 交付约定 | P01–P04 |

## 示例与页面

- P01 `example-01.snapshot`：请求 / 200 / 400 的最小契约卡；页面插图与独立 400×240 渲染逐像素一致（除页面外框）。
- P02 `example-02.snapshot`：`Row` + `Expanded` 1:2 与 `Stack` + `Positioned` 对照；同一 400×240 有界容器。
- P03 `example-03.snapshot`：嵌套 Text / Raw / `text` 属性 / `#RRGGBBAA`。
- P04 `example-04.snapshot`：同一子树左侧 crisp、右侧 `ImageFiltered σ=6`。

## 说明

- `examples.json` 记录每例完整 DSL 行号、印刷片段逐字原文、教学页定位和真实 requestId。
- 页面代码块按 XML 转义展示（`&lt;` 等），`examples.json` 保存未转义原文；省略处用“省略……”明确标出，不把省略号插入可执行源码。
- 本手册没有使用 Image 嵌入预渲染图；教学插图与独立示例都由同一份 DSL 核心构件生成。
