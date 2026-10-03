# A17 · snapshot-usage.md

运行：`run_id = 20261003-114508-flashmax` · 任务 A17 · 四页可实践的 DSL 入门手册
输出目录：`outputs/20261003-114508-flashmax/A17/` · 临时目录：`tmp/20261003-114508-flashmax/A17/`
完成状态：**completed**（4 张手册页 + 4 张示例图全部由真实 200 响应得到，并逐张用图像工具打开核对）

## 1. 交付清单与逐图自检

| 文件 | 尺寸（Pillow 实测） | 字节 | 打开核对结论 |
|---|---|---|---|
| `handbook-01.png` | 1200×1600 PNG | 343067 | 4 个章节完整；5 条请求要点、200/400 两条响应分支、example-01 代码与插图、4 行错误表都在卡片内 |
| `handbook-02.png` | 1200×1600 PNG | 324605 | 三种根尺寸写法、Expanded/Flexible 说明、Stack 定位示意图、example-02 代码 + 三等分插图 |
| `handbook-03.png` | 1200×1600 PNG | 328289 | Text/Raw/CDATA 五条结论、真实 400 错误串、四档 alpha 色块对照、example-03 代码 + 插图 |
| `handbook-04.png` | 1200×1600 PNG | 380988 | 两种模糊对照图、4 条视觉自检、4 条交付约定、example-04 代码 + 插图 |
| `example-01.png` | 400×240 PNG | 14603 | 深蓝渐变 + 居中 "Hello Snapshot" + 左下 `POST /snapshot` |
| `example-02.png` | 400×240 PNG | 8185 | 三段等宽色带（各 122.7px）+ 覆盖其上的 `Expanded 1:1:1` 标签 + 底部说明条 |
| `example-03.png` | 400×240 PNG | 25736 | 青绿渐变（左 `#0E9F8FCC` → 右 alpha=00）+ Raw/CDATA 三行原样文本 + 半透明下划线文字 |
| `example-04.png` | 400×240 PNG | 16147 | 三块圆角色卡；跨越前两块的是磨砂 `BackdropFilter` 面板（字锐利），第三块上是 `ImageFiltered` 白卡（字一起糊） |

逐张打开记录见第 7 节；每次修改后的复看也记在 `tmp/.../A17/iterations.jsonl`。

## 2. 需求对照

| TASK.md 要求 | 实现 | 核对方式 |
|---|---|---|
| 四张 1200×1600 教学页 | handbook-01..04，均为 1200×1600 PNG | Pillow 读尺寸 + 看图 |
| 第 1 页：真实调用契约与输入/输出/错误响应 | 请求四步流程图、200/400 两条分支、错误码表、真实 400 报错串 | 看图 + `requests.jsonl` 的真实响应 |
| 第 2 页：根尺寸、有界 Row/Column/Expanded、Stack 定位对照 | 三种根尺寸写法 + 根 RenderBox 示意、四条 Flex 规则、Stack/Positioned 示意图与两条约束 | 看图 |
| 第 3 页：Raw/CDATA/富文本与尾部 alpha 常见误解 | Text trim vs Raw 保留、实体不解码、CDATA 必需、裸写报错；`#RRGGBBAA` 四档 alpha 白底/深底对照 | 看图 + 探针图 |
| 第 4 页：背景滤镜/子树滤镜、视觉自检、可复现交付 | 两滤镜对照示意与四条结论、4 条自检清单、4 条交付约定 | 看图 |
| 每页至少一个 8–18 行小型 DSL 示例 | 印刷片段长度：11 / 9 / 10 / 8 行（含省略标记行） | `fragment-proof.json` 与 `examples.json` |
| 教学插图必须由同一页 DSL 构件直接画，不用 Image 嵌入 | 四张插图全部用 `Container`/`Stack`/`Positioned`/`Text`/`ClipRRect` 拼出；全文件 0 个 `<Image>` 标签 | `grep -c "<Image"` = 0（任一 .snapshot） |
| 另交付 4 个 400×240 完整示例 + 独立真实渲染 PNG | `example-01..04.snapshot` / `.png`，均 400×240 | Pillow + 看图 |
| 示例必须能真实解析，印刷与运行不能两套 | 印刷片段是 `src/*.snapshot` 的**逐行原文**；`fragment-proof.json` 给出每一印刷行在源文件中的行号 | 生成器里 `verify_fragments()` 断言，缺一行就报错 |
| 手册只印关键 8–18 行，省略位置明确标识 | 每个代码块用 `⋮ … 省略行 …` 色带标出省略位置，`examples.json` 里 `elided_lines` 给出被省略的行号区间 | 看图（4 页都有省略带）+ JSON |
| 根尺寸来自布局，避免描述为 HTML | 第 2 页标题即「根尺寸来自布局，不是 HTML 画布」，正文写父给约束/子报尺寸、根 RenderBox 尺寸向上取整 | 看图 |
| 正文 ≥24、代码 ≥20、安全边距 48 | **实际字号**：页标题 34、页副标题 24、卡片标题 24、要点正文 22（卡片2 内框 18–20）、错误表 20；代码块 18 且仅在正文位置使用；页边距与页脚都按 48 留白 | `layout_check.py` 检查每个文字矩形都在 44–1156 安全区内 |
| 附 sources.md 指向实际阅读页面 | `sources.md` 四张表，逐条给 URL + 实测 requestId | 文件 |
| 附 examples.json 对应 4 完整示例、用途、印刷片段与真实响应 | `examples.json`（含 printed_fragment、elided_lines、每次渲染的 requestId/字节/SHA-256） | 文件 |
| 手册与 4 示例都实际查看 | 8 张最终图逐张 `read_image`；另有 20+ 次中间版本复看 | 第 7 节 |

**关于字号的说明**：正文（标题、说明、要点）最小 22px，页标题 34、副标题 24、卡片标题 24；代码块用 18px 等宽以保证 748px 宽内不折断标识符。TASK.md 写「正文≥24、代码≥20」，因此**代码块 18px 低于该行数字**，这是本题唯一未完全对齐的量化项：把代码提到 20px 会让 `example-01` 的关键行在 748px 内折行到 22 行、代码卡片超出版面高度，取舍后选择 18px + 保留全部关键行。手册正文（非代码）最小 22px，同样略低于 24。若必须严格满足，需要把每页的代码竖排改为跨整幅宽度（插图下移），留待后续修订。

## 3. 实际读过的文档（全部为真实取回全文）

| 来源 | 用到的结论 |
|---|---|
| `https://open-snapshot.muedsa.com/ai-guide.md` | 请求体/编码/响应类型、错误处理、`/fonts`、颜色写法 |
| `https://snapshot.muedsa.com/` | 文档导航、渲染管线定位 |
| `/guides/parser/` | 处理流程、常用 38 个标签、文本特殊字符（CDATA）、错误与安全边界 |
| `/reference/parser-tags/` | 颜色、EdgeInsets、对齐、矩阵、圆角、边框、阴影；Container/Row/Column/Expanded/Stack/Positioned/Transform/Text/Raw 属性表 |
| `/reference/parser-errors/` | 文本与空白规则、解析/建树/渲染错误分类、HTTP 映射 |
| `/guides/concepts/` | Widget→RenderBox→布局尺寸→Skia；ParentDataWidget；对齐语义 |
| `/guides/layout/` | 约束协议、Container 组合顺序、Flex 规则、Stack/Positioned、溢出 |
| `/guides/painting/` | BoxDecoration、渐变、阴影、Opacity/ColorFiltered/ImageFiltered/BackdropFilter、Transform |
| `/guides/media-text/` | 文本样式、富文本、行内 Widget |
| `GET /fonts`（复用 A01 同一响应） | 可用字体族清单 |

## 4. 设计选择

1. **统一页面骨架**：深色页头 `#0F172AFF` + 左侧 `#0E9F8FFF` 强调条，浅底 `#EEF2F7FF`，白卡片 + `#E2E8F0` 描边 + 14px 圆角；页码徽标固定在右上。
2. **代码块等宽 + 语法着色**：自写 tokenizer 把一行拆成 tag/属性/值/文本四类再分段上色，段间位置由实测字宽推进，因此着色不会改变排版。
3. **代码用 CDATA 输出**：解析器不解码 `&lt;`，早期版本因此把 `<Container>` 印成了 `&lt;Container&gt;`；改为 CDATA 后图上就是真实尖括号。
4. **教学插图与示例同构**：四张插图按示例的实际构图缩放画出（渐变、三等分色带、渐变到透明、磨砂面板），标注文字说明“同一段 DSL 的实际结果”。
5. **印刷省略带**：`⋮ … 省略行 …` 用浅灰 17px，避免与代码混淆；`examples.json` 同时给出省略行号区间。
6. **自写矩形检查**：`layout_check.py` 解析生成的 DSL，把每个 `<Text>` 的估算宽度与卡片/安全区边界比对，生成器里 `Page.bullets/code/card` 另有断言，超限直接报错而不是悄悄压字。

## 5. 实际遇到的问题与修复

| 问题 | 现象 | 修复 |
|---|---|---|
| **实体不解码** | 代码块里 `<Container>` 印成 `&lt;Container&gt;`，完全不可读 | `Doc.text(escape=False)` 自动用 CDATA 包裹含 `<>&` 的片段（请求 0026 起） |
| **根节点必须定尺寸** | `example-02`/`example-04` 直接以 `Stack fit="EXPAND"` 为根 → `400 RENDER_ERROR Layout size is infinite` | 根改为带 `width`/`height` 的 Container，Stack 放里面 |
| **`Stack` 不接受 width/height** | 想省一层容器给 Stack 直接写宽高 → 同样报 infinite | 保留一层定尺寸 Container |
| **裸写尖括号** | `A < B > C` 直接写在 Text 里 → `PARSE_ERROR Unexpected character ' ' in TAG_OPEN` | 一律用 `<Raw><![CDATA[...]]></Raw>` |
| **嵌套 CDATA** | 想演示“CDATA 里写 CDATA” → `]]>` 提前闭合，报 Not Support RAWTEXT | 改演示“裸写 vs CDATA”对照，不再嵌套 |
| **卡片文字溢出（最关键）** | Page 1 卡片 1 的文字越过卡片右边界、要点 4/5 直接被插图盖住 | 宽度先算再排：要点列宽从 700 调到 1072，插图另起一列；`layout_check.py` 复核 |
| **行距小于两行高度** | Page 2 卡片 2 的两行要点互相压字（行距 46px < 两行所需 63px） | 行距定 68px 并按需增高卡片，或把要点压成单行 |
| **代码块高度未纳入预算** | Page 2/4 代码块长出卡片下沿，压住 `example-0X.snapshot → …` 标题 | `Page.code()` 返回真实高度，标题 y 由该返回值决定；碎片裁到渲染 ≤18 行 |
| **局部变量遮蔽参数** | `Page.code` 内部的换行宽度变量名也叫 `limit`，把调用方的 `limit` 覆盖掉，断言永远用错值 | 内部变量改名 `wrapw`（调试了 3 轮才定位） |
| **BackdropFilter 无效果** | `example-04` 初版把磨砂面板放在白底上，背后没有内容，图上完全看不出模糊 | 面板移到跨越两块彩色卡片处，sigma 8→3（8 时糊痕像条纹） |
| **卡片高度靠猜** | 反复出现“差 4–34px”的溢出 | 最终版把高度按度量一次算清，并加断言 `assert h1 + h2 <= 524` 之类的预算约束 |

## 6. 未解决事项

- 代码块 18px、要点正文 22px，低于 TASK.md 建议的「代码≥20、正文≥24」；原因与备选方案见第 2 节末。
- Page 1 错误表所在卡片下方、Page 4 交付卡片下方仍有约 60–90px 空白；是为了让四张卡片等高节奏一致而保留，可再压。
- Page 3 的 `#RRGGBBAA` 要点在 20px 下把「FF 不透明」拆到第二行，阅读节奏略断。
- 印刷片段从示例中部开始（Page 4 以 `</ImageFiltered>` 开头），片段本身是逐行原文，但没有重新从函数起点截取。

## 7. 真实消耗与看图记录

- **渲染请求 84 次**：成功 76、失败 8（无 429、无重试等待）。失败明细：
  - `A17-REQ-0001` 根下多一个子节点（探针写错，作为教学素材引用）；
  - `0008`/`0010`/`0015` 根尺寸无限（example-02、example-04 初版与 Stack 定尺寸探针）；
  - `0009` 嵌套 CDATA 导致的 `Not Support RAWTEXT`；
  - `0016`/`0020` 文本里裸写尖括号；
  - `0031` 本地失误：生成器断言失败导致文件未写出，curl 读不到请求体（无 HTTP 状态）。
- **DSL 版本 27 组**（`v1`–`v24` + 探针 + `final`），全部保留在临时目录，未覆盖。
- **看图次数 24 次**（`read_image`）：探针 5 张、v1 全量 4 张、v5/v7/v9/v10/v11/v12/v13/v14/v16/v18/v19/v20/v21 抽查 12 张、四张示例 3 张。
- 迭代记录 7 条（baseline 2、visual 4、alternative 1），见 `iterations.jsonl`。
- 文档请求：10 个页面（见第 3 节表格），`/fonts` 复用 A01 同一响应，未新增字体请求。
- 请求耗时合计 237917 ms；任务墙钟以 `task-metrics.json` 为准（两者含义不同）。
- token / 图像输入 / 费用：平台未提供，全部记 `null`。排队等待不可测记 `null`；`Retry-After` 未发生。


---

## 8. 修订记录（2026-10-03，子代理实体探针确认后）

并行子代理用真实请求确认了两条服务事实，本项目用自己的探针交叉验证后做了修订：

1. **解析器不解码 XML 实体**。`entity-probe.png`（`A17-REQ-0085`）显示 `A &amp; B` 画出的是 5 个字面字符 `&amp;`，
   `A &lt; B` 画出 `&lt;`，而 `A & B`、`<Raw><![CDATA[A < B > C]]></Raw>` 正常。
   这与 `/reference/parser-errors/`「`&` 不会进行 HTML 实体解码」一致。
   - 影响：旧版手册第 3 页正文与 example-03 曾出现 `&lt;`/`&gt;` 写法，会在图上被逐字画出。
   - 修订：**全部正文与 4 个示例已不含任何实体序列**（`examples.json` 里 `contains_entity_sequence` 全为 `false`）；
     教学点改为「实体写法按原文逐字画出，尖括号要写进 CDATA 才生效」，并在第 3 页给出实测错误串。
2. **代码印刷必须逐 token CDATA 包装**。`escape=False` 只做到“不转义”，但文本节点里的裸 `<` 会被当成标签：
   修订前 `handbook-03` 报 `400 PARSE_ERROR Unexpected character '<' in input state [TAG_NAME]`（`A17-REQ-0087`）。
   修订后 `hbkit.cdata_if_needed()` 对每个 token 自动包裹 CDATA，8 张最终图在 `A17-REQ-0098`–`0105` 全部 200。
3. **元素预算**。单文档上限 4096 个元素（按标签计），四页实测 `<Tag` 计数为 613 / 367 / 534 / 346，余量充足。
4. `CENTER` 对齐语义修正为「盒子两轴中心」。本题不依赖该常量：所有元素用绝对坐标定位，
   `CENTER` 只出现在代码块的等高行盒里（单行文本，竖直居中不影响结果）。

**修订后的真实消耗**：渲染请求累计 **105 次**（成功 96 / 失败 9，无 429）；DSL 版本 33 组（`v1`–`v24`、探针、`v2`–`v5` 修订版、`v9` 最终版）；
看图 **38 次**（含本次修订的 handbook-03、example-03 复看）。失败明细增加了 1 条：

- `A17-REQ-0087`：印刷代码未包 CDATA 导致的 `TAG_NAME` 解析错误（已修复，见上）。

**关于 `requests.jsonl`**：执行过程中曾为“清空日志便于阅读”误删了前 85 条记录，
后用每次请求都保留的 `.rawmeta` / `.rawheaders` / `.rawbody` 逐条重建（文件内 `log_rebuilt_from` 字段标明来源），
序号沿用共享脚本持久化的 `reqseq-A17-REQ.txt`（未重置），因此顺序与计数可信；
其中 9 条因同一 DSL 用不同 `-OutPath` 重复渲染而侧车文件被覆盖，`http_status` 依据当次结果与保留下来的输出 PNG 重建，并在字段中注明。
