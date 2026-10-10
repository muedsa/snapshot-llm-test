# A17 来源与引证（sources）

本文件把手册每一条结论接回**本次任务真实取得并保留在磁盘上的原文**。读法是：先看结论，再看
`→` 后面的引证；引证写的是保留文件及其行号（行号指该保留文件本身的行号）。

- 任务：A17 四页快照设计文档手册（1200×1600）+ 四个 400×240 独立示例
- run_id：`run-20261002-220723-mimo`
- 文档取得时间：2026-10-04（UTC+08:00），全部 8 次请求 200，明细见
  `tmp/run-20261002-220723-mimo/A17/requests.jsonl`（`type=document`，id `A17-doc-01..08`）
- 行号索引：`tmp/run-20261002-220723-mimo/A17/doc-excerpts.md`（由原始 HTML 提取，含每个章节的起始行号）
- 标签与属性表：`tmp/run-20261002-220723-mimo/A17/tag-attrs.md`（从 `doc-parser-tags.html` 抽取的逐标签属性行）

## 1. 真实取得的来源

| 请求 id | URL | 保留文件 | 字节 | 状态 |
|---|---|---|---|---|
| `A17-doc-01-ai-guide` | `https://open-snapshot.muedsa.com/ai-guide.md` | `tmp/.../A17/doc-ai-guide.md` | 3718 | 200 |
| `A17-doc-02-rendering` | `/docs/rendering` | `tmp/.../A17/doc-rendering.html` | 70839 | 200 |
| `A17-doc-03-parser-errors` | `/docs/parser-errors` | `tmp/.../A17/doc-parser-errors.html` | 77552 | 200 |
| `A17-doc-04-layout` | `/docs/layout` | `tmp/.../A17/doc-layout.html` | 68617 | 200 |
| `A17-doc-05-parser` | `/docs/parser` | `tmp/.../A17/doc-parser.html` | 85941 | 200 |
| `A17-doc-06-media-text` | `/docs/media-text` | `tmp/.../A17/doc-media-text.html` | 70445 | 200 |
| `A17-doc-07-painting` | `/docs/painting` | `tmp/.../A17/doc-painting.html` | 65022 | 200 |
| `A17-doc-08-testing` | `/docs/testing` | `tmp/.../A17/doc-testing.html` | 69350 | 200 |

另外复用 **A15 已取得**的 `tmp/run-20261002-220723-mimo/A15/doc-parser-tags.html`（标签总表、Raw、颜色、对齐等属性），
本次没有重复请求，因此不重复计入请求数。

`doc-ai-guide.md` 有一次先经 harness 的 webfetch 读取、再用真实 GET 取回留档的过程，只记一行请求、
在该行 `note` 里如实披露，不重复计数。

## 2. 第 1 页 · 调用契约

| 结论 | 引证 |
|---|---|
| 请求体是 UTF-8 纯文本，不是 JSON | `doc-ai-guide.md:26-31` |
| 成功返回 PNG 字节，失败返回含 `code / message / requestId` 的 JSON | `doc-ai-guide.md:47` |
| 成功和失败都能用 `X-Request-Id` 关联服务日志 | `doc-ai-guide.md:47` |
| 429 和部分 503 可按 `Retry-After` 延迟重试 | `doc-ai-guide.md:47` |
| `400 PARSE_ERROR` 按消息里的位置改 DSL 再提交；`413` 缩请求体；`401` 查凭据 | `doc-ai-guide.md:47` |
| 解析阶段错误包成 `ParseException` → HTTP 400 | `doc-excerpts.md:571-578`、`611-625` |
| 布局尺寸为空/无限更适合 422；`IllegalArgumentException`/`IllegalStateException` 走 422 | `doc-excerpts.md:578`、`628-638` |
| 省略标注是 XML 注释，解析时被忽略 | `doc-excerpts.md:555-569`、`598-601` |

**省略标注确实可被忽略这一条，除了文档还做了实测**：把手册打印的 17 行原样发给服务，
四份全部 200（`tmp/.../A17/printed-parse-report.md`，请求 id `A17-printed01..04`）。

## 3. 第 2 页 · 尺寸与定位

| 结论 | 引证 |
|---|---|
| **画布尺寸由布局决定，受服务端限制**（不是 `Snapshot` 的 width/height） | `doc-ai-guide.md:28`；尺寸推导见 `doc-excerpts.md:1036-1062` |
| 根尺寸是布局结果，不是 HTML 视口 | `doc-ai-guide.md:28`；`doc-excerpts.md:1036-1062` |
| 约束由父节点给出、子节点报尺寸，只能逐层收紧 | `doc-excerpts.md:333-353`、`1036-1062` |
| `Expanded / Flexible / Spacer` 必须是 `Flex / Row / Column` 的直接子节点 | `doc-excerpts.md:170-176` |
| Flex 主轴无限时算不出"剩余空间"，要先用 `SizedBox / Container / ConstrainedBox` 给有限主轴 | `doc-excerpts.md:405-411` |
| `Stack` 不提供尺寸，先布局非 `Positioned` 子节点，再按 left/top/right/bottom/width/height 摆位 | `doc-excerpts.md:413-422` |
| **同一轴上 left / right / width 最多只能给两个**（垂直轴相同） | `doc-excerpts.md:433-436` |
| `Stack` 默认 `HARD_EDGE` 裁剪；要画到边界外需显式 `clipBehavior="NONE"` | `doc-excerpts.md:437-441` |
| 空 `Container` 在无界根约束下会收缩为 0，根出图仍需非零宽高 | `doc-excerpts.md:374-376`、`1061` |

> 页面初稿里"根尺寸由 Snapshot 的 width / height 决定"与 `doc-ai-guide.md:28` 冲突，
> 已在 v03 改为"根尺寸由根布局决定，受服务端限制"。改动记录见
> `iterations.jsonl` seq 37-40 的 `change` 字段。

**两条"踩坑"是实测出来的，不是抄来的：**

- `Raw` 写在 `Text` 之外 → **400**，原文 `Element [Raw] ... cant not buildWidget, it can only be used in the Text`
  （`A17-probe12`，保留 `tmp/.../A17/probe-12.snapshot`）
- `Expanded` 放错层级 → **400**，原文 `Tag [Expanded] must be a direct child of Flex, Row or Column`
  （`A17-probe13`，保留 `tmp/.../A17/probe-13.snapshot`）

## 4. 第 3 页 · 文本与颜色

| 结论 | 引证 |
|---|---|
| `<Text>` 内普通文本会 trim；要保留原始空白用 `<Raw>` | `doc-excerpts.md:553`、`586-590` |
| `<Raw>` 用法示例（原样保留空白与 `<tag>` 字符） | `doc-excerpts.md:606-608` |
| 解析器不做 HTML 实体解码，`&amp;` 保留为字面量 | `doc-excerpts.md:547`、`592-594` |
| 文本里要出现 `<` 或 `>` 时用 CDATA | `doc-excerpts.md:547-551` |
| 非文本标签里只能出现纯空白，否则 `Not Support RAWTEXT` | `doc-excerpts.md:554`、`621` |
| 旧版 parser 按 `#AARRGGBB` 读八位颜色；**Kotlin 侧仍用 `0xAARRGGBB`** | `doc-excerpts.md:309-314`、`1030` |
| 手册用的 `#RRGGBBAA`（尾随 alpha）是当前 DSL 顺序 | `doc-excerpts.md:278-316`（颜色）、`example-03.png` 实测三块 `FF/80/26` 色条 |

**空白语义两条是量出来的**（不是读来的）：

- `probe-10`：普通文本与 CDATA 的首尾空格都会被剪（墨迹起于 x102），中间空格保留；
  嵌进 `Text` 的 `Raw` 保留 4 个前导空格（墨迹起于 x126）。
- `probe-11`：`<Raw><![CDATA[    AA]]></Raw>` 墨迹起于 x144 = 100 + 4×11，
  即 `Raw + CDATA` 能逐字还原缩进 —— 这是手册能按原文打印代码缩进的依据。

## 5. 第 4 页 · 滤镜与自检

| 结论 | 引证 |
|---|---|
| `BackdropFilter` 读取已有背景，**通常需要** `ClipRect` 或 `ClipRRect` 限定区域 | `doc-excerpts.md:672` |
| 透明度与颜色滤镜的作用范围 | `doc-excerpts.md:647-686` |
| 边框、圆角属性 | `doc-excerpts.md:687-703` |
| Golden 三态、文本测试 | `doc-excerpts.md:744-764` |
| **Artifact 不是断言** | `doc-excerpts.md:765-769` |
| 常见误区（字体、抗锯齿导致 golden 不稳） | `doc-excerpts.md:770-781` |

**"ImageFiltered 在同一 Stack 里会让背景滤镜失效"是本任务自己做隔离实验得到的**，文档没有这条：

| 探针 | 内容 | 结果 |
|---|---|---|
| `probe-03` | 4 种 `BackdropFilter` 结构变体 | 全部模糊成功 → 结构不是原因 |
| `probe-04` | 示例 04 去掉 `ImageFiltered` | **模糊生效** |
| `probe-05` | 给 `Stack` 加 `background` 属性 | **模糊失效** |
| `probe-06` | 拆成 `<Stack>` / `<Column>` 两级 | **模糊失效** |

结论：`ImageFiltered` 子树出现在同一个 `Stack` 内会让 `BackdropFilter` 失效，
解决办法是把它移出该 `Stack`（见 `example-04.snapshot` 最终结构）。

同一页的"要先量像素再看图"来自 `doc-excerpts.md:765-781`，
本任务的做法就是 `cmp-illu.ps1` 像素比对 + 真实看图两条腿。

## 6. 拿不准就不写进手册的东西

以下内容在准备时被明确排除，因为本次没有可引证的来源或实测结果：

- `Retry-After` 的具体秒数（服务没有返回过该头，不猜）
- 服务端对画布尺寸的上限数值（`doc-ai-guide.md:28` 只说"受服务端限制"，没给数）
- `snapshot-lsp` 的版本与安装方式（`doc-excerpts.md:542-543` 只说存在，未展开）
- 任何未经实测的错误码与状态码组合

## 7. 相关保留物

- 原始来源字节：`tmp/run-20261002-220723-mimo/A17/doc-*.md|html`
- 提取与索引：`doc-excerpts.md`、`tag-attrs.md`
- 实测探针：`probe-01` … `probe-13`（`.snapshot` / `.png` / 请求行）
- 打印片段解析报告：`printed-parse-report.md`
- 行宽与生成报告：`page-gen-report.md`、`example-line-audit.md`
- 最终自检：`final-audit.md`
