# A17 · 快照 DSL 与文档的实际应用记录

任务：A17 documentation-handbook —— 四页 1200×1600 手册 + 四个 400×240 独立示例。
run_id：`run-20261002-220723-mimo`。本文件记录**这一题真正用了哪些文档、哪些 DSL 特性、哪些工具**，
以及跨题复用和踩过的坑；不写没有真实发生的使用。

## 1. 真实读过的文档

| 取得方式 | 保留位置 | 本题拿它做了什么 |
|---|---|---|
| 真实 GET（8 次，全部 200，共 511,484 B） | `tmp/.../A17/doc-ai-guide.md`、`doc-rendering.html`、`doc-parser-errors.html`、`doc-layout.html`、`doc-parser.html`、`doc-media-text.html`、`doc-painting.html`、`doc-testing.html` | 见下 |
| 复用 A15 已取得的标签表 | `tmp/.../A15/doc-parser-tags.html` → 抽取为 `A17/tag-attrs.md` | `Container` / `Text` / `Positioned` / `Stack` 的属性行、`Raw` 的写法 |
| 逐行摘录与索引 | `tmp/.../A17/doc-excerpts.md` | 把结论接回原文行号，供 `sources.md` 引证 |

具体被页面用到的结论：

- `ai-guide.md:28`「画布尺寸由布局决定，受服务端限制」→ 第 2 页主论点，也**推翻了初稿里"根尺寸由 Snapshot 的 width/height 决定"的错误说法**。
- `ai-guide.md:47` 纯文本请求体、`code/message/requestId`、`X-Request-Id`、`Retry-After` → 第 1 页全部要点。
- `parser-errors` 的错误表（`doc-excerpts.md:611-638`）→ 第 1 页「400 是解析失败，422 是参数或状态不合法」。
- `layout` 的 Flex / Stack / Positioned 规则（`doc-excerpts.md:170-176`、`405-411`、`413-441`）→ 第 2 页正文与踩坑。
- `parser` 的文本与空白规则（`doc-excerpts.md:547-569`、`586-608`）→ 第 3 页全部要点。
- `painting` 的滤镜与裁剪（`doc-excerpts.md:647-703`）→ 第 4 页。
- `testing` 的 golden 三态、artifact 不是断言、常见误区（`doc-excerpts.md:744-781`）→ 第 4 页踩坑。

**没读过就没写**：`Retry-After` 的具体秒数、画布尺寸上限数值、`snapshot-lsp` 的用法，三处都因为原文没给数而没有进手册。

## 2. 真实用到的 DSL 特性（每条都有保留的 `.snapshot` / `.png`）

### 2.1 手册页面本体
- `<Snapshot type="png">` + 根 `<Container width="1200" height="1600" color="…">` + 根 `<Stack>` + 若干 `<Positioned>` 排版 —— 页面 63 行，四页共用同一套网格常量。
- 字体只写单值：正文 `Noto Sans CJK SC`，代码 `Noto Sans Mono CJK SC`（写成逗号列表会被当作一个 family 名）。
- `border="1 SOLID #E2E8F0"`、`borderRadius="12"`、`padding="(6,14)"` 做卡片与徽标。
- `fontStyle="BOLD"`、`color` 显式上色（默认黑色，深底上必须自己给）。

### 2.2 把示例原文逐字印进页面 —— 本题最核心的一段 DSL
- **`Text` 会修剪自己首尾的空白**（普通文本和 CDATA 都剪），所以直接把代码行塞进 `<Text><![CDATA[…]]>` 会让缩进全丢。
- **`<Text>` 里嵌 `<Raw><![CDATA[…]]></Raw>` 能逐字保留前导缩进**，实测墨迹起点 x144 = 100 + 4×11（`probe-11`）。
- **一行里如果本身含 `]]>`，就不能整行塞进一个 CDATA**，否则 CDATA 提前结束，服务返回
  `400 PARSE_ERROR: Not Support RAWTEXT: ]]>`（`A17-pg03`）。解决办法是把终止符**跨两段拆开**：
  第 1 段以 `]]` 结束、第 2 段以 `>` 开始，拼回去正好是 `]]>`；第 3 段承接余下字符。实现在 `gen-pages.ps1` 的 `EmitVerbatim()`。
- **省略标注写成 XML 注释 `<!-- … -->`**：文档说注释在解析时被忽略（`doc-excerpts.md:555-569`、`598-601`），
  并且把四段 17 行打印片段原样发服务实测，四份全部 200（`printed-parse-report.md`），所以"删掉注释也能跑、留着注释也能跑"是**测出来的**。

### 2.3 毛玻璃与滤镜（第 4 页 + example-04）
- `<ClipRect><BackdropFilter sigmaX="8" sigmaY="8"><Container color="#FFFFFF44"/></BackdropFilter></ClipRect>` 组合。
- 文档只说「通常需要 ClipRect 或 ClipRRect 限区」（`doc-excerpts.md:672`），所以手册措辞也写成"通常需要"，没有写成绝对。
- **自己测出来的那条**：`ImageFiltered` 子树和 `BackdropFilter` 放在同一个 `Stack` 里会让背景滤镜失效。
  `probe-03`（4 种结构变体全成功）排除了结构原因，`probe-04`（去掉 ImageFiltered 就生效）、
  `probe-05`（加 `background` 失效）、`probe-06`（拆 `<Stack>`/`<Column>` 仍然失效）逐步锁定。
  最终 `example-04.snapshot` 把 `ImageFiltered` 移到 `<Stack>` 之外，模糊恢复。

### 2.4 排版量测（页面网格是量出来的，不是估的）
- `probe-07`：默认字体行盒 fs20→24、fs22→27、fs24→29、fs26→31、fs40→48。
- `probe-08`：`Noto Sans Mono CJK SC` 行盒 fs20→29、fs22→**32**、fs24→35；等宽步进 = 0.5 em，
  fs22 即 11 px/字符 → 代码行预算 **≤94 字符 / ≤1040 px**（文字起点 x88，卡片内右边界 1128）。
- `probe-09`：`Noto Sans CJK SC` 行盒 fs20→29、fs24→**35**、fs26→38、fs40→58。
- 结果：代码块 17 行 × 32 px，上留白 10、下留白 10，正好填满 564 px 深底；正文与标题间距 8 px。

### 2.5 让插图与独立示例像素完全一致
- 插图 = 示例的第 2..17 行原样放在 `<Positioned left="72" top="242">` 下面，尺寸 400×240。
- **必须再套一层 `<ClipRect>`**：否则页面的白卡会被 `BackdropFilter` 的模糊采样进去，
  第 4 页曾出现 6078 px 差异（全部落在插图左/上边缘 24 px 采样带内）。
  套上 `ClipRect` 后插图有了自己的图层，模糊在 400×240 边界处截断，**四页差异全部归 0**。

## 3. 用到的脚本与工具

| 脚本 | 作用 |
|---|---|
| `tmp/.../_suite/render.ps1` | 统一渲染：`curl.exe --data-binary` 提交，自动往本题 `requests.jsonl` 追加一行（含 status/duration/bytes/request_id/server_timing） |
| `A17/gen-pages.ps1` | 生成四页 DSL：网格常量、`ProseWidth`/`CodeWidth` 行宽预算、`Esc`/`EmitVerbatim` 逐字输出、打印片段组装 |
| `A17/check-examples.ps1` | 逐行审计示例与打印行数、行宽（`rows=83 problems=0`） |
| `A17/check-a17.ps1` | 交付自检：配对哈希、尺寸、行数、BOM/乱码、看图记录、插图像素比对、打印片段可解析 |
| `A17/cmp-illu.ps1` | 插图区域与 `example-0N.png` 的逐像素比对 |
| `A17/ink.ps1` / `col.ps1` / `bands.ps1` | 墨迹范围、单列色值、行带位置，用于定位"差在哪一片" |
| `A17/log-iter.ps1` / `log-iters.ps1` / `log-pages.ps1` / `log-v03.ps1` / `log-views.ps1` | 追加 `iterations.jsonl` |
| `A17/verify-printed.ps1` | 从交付的 `example-0N.snapshot` 重组 17 行打印片段并提交，产出 `printed-parse-report.md` |
| `A17/fetch-docs.ps1` / `doc-excerpts.ps1` | 真实抓取并逐行摘录文档 |

看图工具：`read` 直接读 PNG（本题 21 次）、以及委托 `general` 子代理逐字读帧（2 次，见第 5 节）。
像素类观察（列采样、行带、区域比对等 14 次）**只用于定位问题，不当作"看过图"**。

## 4. 跨题复用

- **从 A15 复用**：`doc-parser-tags.html` 原始字节与其抽取产物，本题没有重复请求，只把它当成已取得的共享资料。
- **从 A01–A16 复用**：`render.ps1` 的请求登记格式、`requests.jsonl` / `iterations.jsonl` 的字段与
  `type` 词表（baseline / visual / syntax-fix / alternative / retry / requirement-change）、
  版本化产物路径（`-vNN`）与"只有验收后才进 outputs"的流程、PowerShell 5.1 的写法坑。
- **可被后续题复用的**：`EmitVerbatim()`（原文逐字打印 + `]]>` 拆分）、`cmp-illu.ps1`（子图与原图的区域比对）、
  `gen-pages.ps1` 的 1200×1600 网格常量。

## 5. 踩过的坑（都留了证据）

1. **`]]>` 把 CDATA 提前关掉** → `A17-pg03` 400，`failures/` 保留响应体；修复后 `A17-pg03b` 200。
   首版草稿被生成器就地覆盖，已按原逻辑重建为 `handbook-03-v01-draft1.snapshot`，并**重发一次验证**：
   返回的 `400 PARSE_ERROR … at position 5735 near: …` 与原始响应逐字一致（`A17-pg03draft`）。
2. **`ImageFiltered` 在同一 `Stack` 内会让 `BackdropFilter` 失效**（见 2.3），四个探针留档。
3. **插图边缘的白色渗色**：套 `ClipRect` 才能让模糊在插图边界截断（见 2.5）。
4. **`$out` 覆盖了 `$OUT`** —— PowerShell 变量不区分大小写，写 `verify-printed.ps1` 时被咬；
   已改名 `$pngPath`。
5. **`@()` 是固定长度数组**，`.Add()` 会抛 `Collection was of a fixed size`；改用 `List[string]`。
6. **日志写错目录**：四行渲染记录曾被写进 `outputs/.../A17/requests.jsonl`，已追加进本题日志，
   原件归档为 `requests-merged-from-outputs.jsonl`，outputs 里只留交付物。
7. **看图工具返回过期/串位帧**：`handbook-01-v03` 与 `handbook-02-v03` 被对调返回，
   用「文件字节数 + DSL 内的徽标文字」交叉验证确认磁盘文件无误；
   `handbook-03/04-v03` 连续返回别的页，改由子代理逐字读取并把帧内文字写进
   `iterations.jsonl` seq 41/42（seq 39/40 记的是那两次失败的本地读取）。
8. **初稿有一处事实错误**：`根尺寸由 Snapshot 的 width / height 决定` 与 `ai-guide.md:28` 冲突，
   在交付前的准确性审查中被发现并改掉，记录在 `iterations.jsonl` seq 37-40。

## 6. 本题验证到什么程度

| 项 | 结果 | 证据 |
|---|---|---|
| 四个示例渲染 | 4/4 HTTP 200，18 行 | `requests.jsonl`、`example-line-audit.md` |
| 四页手册渲染 | 4/4 HTTP 200，63 行 | `requests.jsonl`、`page-gen-report.md` |
| 打印片段可解析 | 4/4 HTTP 200（含注释行） | `printed-parse-report.md` |
| 插图与原图一致 | 4 页 × 0 差异像素（400×240 全域） | `cmp-illu.ps1` 输出、`final-audit.md` |
| 八张交付图都看过 | 8/8 有真实看图记录 | `iterations.jsonl`、`examples.json` |
| 两条"踩坑"有实测 | Raw 出 Text → 400；Expanded 层级 → 400 | `probe-12`、`probe-13` 响应原文 |
| 交付自检 | `final-audit.md` problems = 0 | 同名文件 |

未做 / 不知道的：`Retry-After` 实际取值、服务端画布尺寸上限、token 与费用（无法测量，指标里记 `null`）。
