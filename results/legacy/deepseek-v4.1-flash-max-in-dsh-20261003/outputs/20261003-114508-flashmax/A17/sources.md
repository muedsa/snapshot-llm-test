# A17 · sources.md

每条结论都指向**实际打开过的页面**（`web_fetch`/`Invoke-WebRequest` 取回全文）或**本套题里的实测证据**。
实测证据里的 requestId 都能在 `tmp/20261003-114508-flashmax/A17/requests.jsonl` 与服务日志中对上。

## 1. 服务与调用契约（第 1 页）

| 结论 | 来源 |
|---|---|
| `POST /snapshot`，请求体是 UTF-8 纯文本、`Content-Type: text/plain; charset=utf-8` | <https://open-snapshot.muedsa.com/ai-guide.md>（最小示例与 curl 命令） |
| 成功响应体是图片二进制；失败响应是 `{code, message, requestId}` JSON | 同上「错误处理」节 |
| `type` 可取 `png`/`jpg`/`webp`，扩展名要与实际格式一致 | 同上「生成 DSL 的要点」 |
| 根标签必须是 `Snapshot`，且只能有一个根 Widget 子节点 | <https://snapshot.muedsa.com/reference/parser-tags/>（Snapshot 一节）；<https://snapshot.muedsa.com/guides/parser/> |
| 400 PARSE_ERROR 会给出位置；413、401、429/503 的处理方式 | <https://open-snapshot.muedsa.com/ai-guide.md>；<https://snapshot.muedsa.com/reference/parser-errors/> |
| **实测**：根下多一个子节点 → `400 Tag Snapshot only can have one child` | 本项目请求 `A17-REQ-0001` |
| **实测**：真实错误串带行列偏移（第 3 页引用）`Pos[3:18]~72: Attr [color] unsupported CSS color` | 本项目探针请求，requestId `a1ea4ec4-e046-44b8-97af-8c4137f4ca40` |
| **实测**：`X-Request-Id` 出现在响应头 | `requests.jsonl` 的 `service_request_id` 字段（每次成功请求都有） |

## 2. 根尺寸与布局（第 2 页）

| 结论 | 来源 |
|---|---|
| 根尺寸来自根 RenderBox 的布局尺寸，向上取整为像素；不是 HTML 画布 | <https://snapshot.muedsa.com/guides/concepts/>（「布局、绘制和图层」「颜色、尺寸与坐标」） |
| 父节点给 BoxConstraints、子节点报尺寸 | <https://snapshot.muedsa.com/guides/layout/>（「父节点给约束，子节点报尺寸」） |
| `Expanded` = `Flexible(fit=TIGHT)`，只能挂在 Flex/Row/Column 下 | <https://snapshot.muedsa.com/reference/parser-tags/>（Row 与 Column / Expanded 与 Flexible） |
| 主轴无限时无法分配剩余空间 | <https://snapshot.muedsa.com/guides/layout/>（「Flex 布局」末段） |
| `Positioned` 只能是 Stack/IndexedStack 的直属子节点，每轴最多给两项 | <https://snapshot.muedsa.com/guides/concepts/>（ParentDataWidget）；parser-tags 的 Positioned 一节 |
| **实测**：`Container` 无尺寸 + Stack `fit="EXPAND"` → `400 RENDER_ERROR Layout size is infinite` | 本项目请求 `A17-REQ-0002`（example-02 初版）、`A17-REQ-0004` |
| **实测**：`Stack` 不接受 `width`/`height` 属性，必须用父 Container 定尺寸 | 本项目请求 `A17-REQ-0019` |
| **实测**：三等分实测结果 368/3 = 122.7px（图上与 `example-02.final.png` 一致） | `example-02.final.snapshot` 的 `Expanded flex="1"` ×3 |

## 3. 文本、CDATA 与颜色（第 3 页）

| 结论 | 来源 |
|---|---|
| `<Text>` 的普通文本会 trim；`<Raw>` 原样保留，首尾空格与换行不丢 | <https://snapshot.muedsa.com/reference/parser-errors/>（「文本与空白规则」）；<https://snapshot.muedsa.com/reference/parser-tags/>（Raw 一节） |
| 解析器**不做 HTML 实体解码**，`&amp;` 会保留为字面量 | <https://snapshot.muedsa.com/reference/parser-errors/>（同上）；**本项目实测**：`tmp/.../A17/entity-probe.png`（请求 `A17-REQ-0085`）里 `A &amp; B` 画出的是 5 个字面字符 `&amp;`，`A &lt; B` 画出的是 `&lt;`；因此手册与示例一律不用实体写法 |
| 文本里要出现 `<` 或 `>` 必须用 CDATA | <https://snapshot.muedsa.com/guides/parser/>（「文本中的特殊字符」）；parser-tags 的 Text 一节 |
| 裸写 `<` 会按标签起始解析并报错 | <https://snapshot.muedsa.com/reference/parser-errors/>（解析阶段错误表：`Not Support RAWTEXT`、TAG_OPEN） |
| 颜色支持 `#RGB`/`#RGBA`/`#RRGGBB`/`#RRGGBBAA`，8 位最后两位是透明度 | <https://open-snapshot.muedsa.com/ai-guide.md>；<https://snapshot.muedsa.com/reference/parser-tags/>（颜色一节） |
| 旧版把 8 位当 `#AARRGGBB`，现在按 CSS 的 `#RRGGBBAA`；Kotlin DSL 仍是 `0xAARRGGBB` | parser-tags 颜色一节原文 |
| **实测**：`<Raw><![CDATA[A < B > C]]></Raw>` 渲染出 `A < B > C`；`A &lt; B` 原样显示 `A &lt; B` | 探针 `t-ltgt2.png`（请求 `A17-REQ-0017`）与 `example-03.final.png` |
| **实测**：`alpha=00` 的色块不绘制（不是黑色） | 第 3 页右图，由 `#1D4ED800` 与 `#0E9F8F00` 两个色块直接画出 |
| **实测**：Raw 里可以出现 `<Text>` 这样的标签字样 | `example-03.final.snapshot` |

## 4. 滤镜与交付（第 4 页）

| 结论 | 来源 |
|---|---|
| `ImageFiltered` 对子树做高斯模糊（只支持 sigmaX/sigmaY） | <https://snapshot.muedsa.com/guides/painting/>（透明度与颜色滤镜）；parser-tags 图示 |
| `BackdropFilter` 读取**已经绘制在当前内容背后**的区域做模糊 | <https://snapshot.muedsa.com/guides/painting/>；<https://snapshot.muedsa.com/widgets/painting/backdrop-filter/> |
| BackdropFilter 通常需要 ClipRect/ClipRRect 限定区域 | guides/painting 原文：「通常需要 ClipRect 或 ClipRRect 限定区域」 |
| Parser 侧两个滤镜都只支持高斯模糊 | guides/painting 末段原话 |
| **实测**：`ImageFiltered sigmaX=5` 会把白卡与卡内文字一起糊；`ClipRRect + BackdropFilter sigma=3` 只糊背后的色块、文字仍锐利 | `example-04.final.png`；对照 `A17-REQ-0075`（sigma=8，模糊过强）与 `A17-REQ-0076`（sigma=3） |
| **实测**：相同 DSL 返回相同字节（示例重复渲染字节数一致） | 例如 `handbook-01` 的 v18/v19/final 三次请求都是 343067 字节 |

## 5. 字体与度量

| 结论 | 来源 |
|---|---|
| 可用字体：`Noto Sans CJK SC`、`Noto Sans Mono CJK SC`、`Noto Serif CJK SC`、`Noto Serif CJK JP`、`Inter`、`Inter Tight`、`DejaVu Sans`、`DejaVu Sans Mono`、`DejaVu Serif`、`Noto Color Emoji` | `GET /fonts`（本套题 A01 取得，`tmp/20261003-114508-flashmax/_suite/shared/fonts.txt`，各题复用） |
| 多字体名用英文逗号分隔，名称要与 `/fonts` 一致 | <https://open-snapshot.muedsa.com/ai-guide.md> |
| 等宽拉丁/数字实测步进 ≈ 0.603 × 字号；CJK ≈ 1.0 × 字号；大写字高 ≈ 0.75 × 字号 | 本页 `probe-metrics`/`probe-advance` 两张探针图 + `measure_advance.py` 的墨迹列测量（`tmp/.../A17/probe-adv.json`） |
| 带 `width` 的容器会让放不下的文字换行 | <https://snapshot.muedsa.com/guides/layout/>（约束与尺寸）；第 1 页自检里实际踩到并修掉 |


## 6. 修订依据（子代理实体探针确认后）

2026-10-03 收到并行子代理的实测结论并与本项目自己的探针交叉验证，A17 做了如下修订，全部有真实请求留痕：

| 结论 | 证据 | 对 A17 的影响 |
|---|---|---|
| 解析器不解码实体：`&amp;` 画出 5 个字面字符 | `entity-probe.png`（`A17-REQ-0085`）；与 `/reference/parser-errors/` 的「`&` 不会进行 HTML 实体解码」一致 | 手册正文与 4 个示例已**完全不含** `&lt;`/`&gt;`/`&amp;` 序列；印刷代码改为逐 token CDATA 包装 |
| 代码里含 `<` 必须放在 CDATA 里才能印刷 | 修订前 `handbook-03` 报 `400 PARSE_ERROR Unexpected character '<' in input state [TAG_NAME]`（`A17-REQ-0087`）；改用 `cdata_if_needed()` 后 `A17-REQ-0098..0105` 全部 200 | `hbkit.code()` 现在对每个 token 自动 CDATA 包装 |
| 单文档元素上限 4096（按标签计数） | 服务限制；本项目最大页面 `handbook-01` 为 613 个 `<Tag`，四页分别为 613 / 367 / 534 / 346 | 全部远低于上限，无需拆分 |
| `CENTER` 对齐是盒子两轴中心（不是底部居中） | 子代理实测（60px 盒内文字墨迹 162..176） | A17 未依赖该常量：所有定位都算绝对坐标，`CENTER` 只用在 `Page.code` 的等高行盒里，不影响输出 |

修订后再次渲染全部 8 张最终图（`A17-REQ-0098`–`A17-REQ-0105`，均 200），并逐张复看确认版式未变。
