# A17 · 技术结论与出处对照

本文件把四页手册里的每条关键技术结论落到**实际读过的页面**与**实际渲染的例子**上。
缓存路径基准为总任务根（`path_base: suite_root`），本文件内的相对链接基准为本题输出目录。
未从文档得到、只能自己量的结论单列在第 3 节，并写清测量请求。

## 1. 实际读过的文档

| # | 页面 | 缓存副本 | 用途 |
|---|---|---|---|
| D1 | <https://open-snapshot.muedsa.com/ai-guide.md> | `../../../tmp/2026-10-12T10-04Z-r001/_suite/docs/ai-guide.md` | 调用契约、错误响应、字体接口 |
| D2 | <https://snapshot.muedsa.com/reference/parser-tags/> | `../../../tmp/2026-10-12T10-04Z-r001/_suite/docs-txt/reference_parser-tags.txt` | 标签表、Snapshot 根属性、颜色格式、Text/Raw、滤镜参数 |
| D3 | <https://snapshot.muedsa.com/guides/layout/> | `../../../tmp/2026-10-12T10-04Z-r001/_suite/docs-txt/guides_layout.txt` | 约束协议、零尺寸空容器、Flex 主轴必须有界 |
| D4 | <https://snapshot.muedsa.com/widgets/layout/stack/> | `../../../tmp/2026-10-12T10-04Z-r001/_suite/docs-txt/widget_layout_stack.txt` | Stack 默认 `clipBehavior=HARD_EDGE`、`alignment=TOP_START` |
| D5 | <https://snapshot.muedsa.com/widgets/painting/backdrop-filter/> | `../../../tmp/2026-10-12T10-04Z-r001/_suite/docs-txt/widget_painting_backdrop-filter.txt` | 背景滤镜读取子树之外的背景、需裁剪限定 |
| D6 | <https://snapshot.muedsa.com/widgets/painting/image-filtered/> | `../../../tmp/2026-10-12T10-04Z-r001/_suite/docs-txt/widget_painting_image-filtered.txt` | 子树滤镜的模糊输出边界 |
| D7 | <https://snapshot.muedsa.com/reference/faq/> | `../../../tmp/2026-10-12T10-04Z-r001/_suite/docs-txt/reference_faq.txt` | Stack 阴影被切、Container color/decoration 互斥 |
| D8 | <https://open-snapshot.muedsa.com/fonts> | `../../../tmp/2026-10-12T10-04Z-r001/_suite/docs/fonts.txt` | 服务实际安装的字体族 |
| D9 | <https://snapshot.muedsa.com/reference/enums/> | `../../../tmp/2026-10-12T10-04Z-r001/_suite/docs-txt/reference_enums.txt` | textAlign / clipBehavior / tileMode 取值 |

D1–D9 是本套题在 `_suite` 共享准备阶段真实抓取并留档的副本（见
`../../../tmp/2026-10-12T10-04Z-r001/_suite/requests.jsonl`），A17 直接复用，未重复请求，
因此 A17 自己的 `requests.jsonl` 里只有 1 次字体无关的探测与 45 次渲染。

## 2. 结论 → 出处 → 落在哪一页 / 哪个例子

| 结论（手册原文位置） | 出处 | 例子证据（实际渲染） |
|---|---|---|
| 请求体是 UTF-8 纯文本、不是 JSON；成功响应体直接是图片二进制（第 1 页要点 1、2） | D1 第 3 行：“接口为 `POST /snapshot`，请求体是 UTF-8 纯文本，不是 JSON；成功时响应体是图片二进制。” | `example-01.png` 左框 `POST /snapshot` + `text/plain`，右框 `200 image/png` |
| 只有失败才返回 `{code, message, requestId}`；400 按位置改 DSL，429/部分 503 看 Retry-After（第 1 页要点 3） | D1 第 47 行 | `example-01.png` 红字行 |
| 出错时 curl 仍可能把 JSON 写进 `.png`，用前要查状态与 Content-Type（第 1 页核对项 1） | D1 第 51 行 | 本套题 A16 之前遇到过 200 但响应体截断；`_suite/scripts/render.py` 因此按“响应是否真是图片格式”判定成功 |
| `/fonts` 返回 `text/plain`，每行一个字体族（第 1 页核对项 2 的“写错标签名”同源做法） | D1 第 35 行、D8 | 四例统一使用 `Noto Sans CJK SC` 与 `Noto Sans Mono CJK SC`，两个名字都逐字来自 D8 |
| Snapshot 根只有 `background/debug/type`，必须是第一个标签且带一个根 Widget 子节点；宽度写上去不会生效（第 2 页要点 1） | D2 第 180–189 行 | `example-02.snapshot` 第 1–2 行：`<Snapshot background="#FFFFFF" type="png">` + `<Container width="400" height="240">`，尺寸只写在容器上 |
| 空 Container 在无界根约束下收缩为零尺寸，根出图仍需非零宽高（第 2 页坑 1） | D3 第 51 行 | 第 2 页插图里 400×240 容器决定画布 |
| Expanded / Flexible / Spacer 必须是 Flex/Row/Column 的**直接**子节点（第 2 页要点 3） | D2 第 327 行 | `example-02.snapshot` 第 29–33 行：`Spacer` 直接挂在 `Row` 下 |
| Flex 主轴约束无限时无法分配“剩余空间”（第 2 页坑 2 的成因） | D3 第 90 行 | v002-example-02 三条色块高度塌成 0 的实测（`iterations.jsonl` 的 v002 条目） |
| 八位颜色按 CSS `#RRGGBBAA` 解析，alpha 在末尾；旧 `#80FF0000` 写法会改变颜色（第 3 页要点 1） | D2 第 81、87 行 | `example-03.png`：`#E23B3B80` 与 `#2B5BD780` 两块叠加处更深 |
| 解析器不解码 HTML 实体（第 3 页要点 2） | D2 第 560 行的文本语义 + 实测：`&lt;` 原样出现在页面上 | 第 3 页正文“写 &lt; 就原样印出这 4 个字符”本身就是这条结论的现场演示 |
| 普通文本节点会被 trim；`Raw` 不 trim，首尾空格与换行保留，且只能出现在最外层 `Text` 的行内内容树里（第 3 页要点 3） | D2 第 560、572 行 | `example-03.snapshot` 第 26–33 行；`example-03.png` 中 `<Raw> · </Raw>` 两侧空格确实渲染出来 |
| `Text` 可嵌套 `Text`/`Raw`/`Emoji`/`WidgetSpan`，行内共用基线（第 3 页插图末行） | D2 第 560 行 | `example-03.png` 绿/橙两字与前后文字齐平 |
| `BackdropFilter` 只有背后已有内容时才有视觉效果，且读取**子树之外**的背景，必须用裁剪限定区域（第 4 页要点 1、3） | D5 | `example-04.png` 左卡：字清楚、条纹糊成色带 |
| `ImageFiltered` 糊整棵子树，会按 sigma 自动给出模糊输出边界（第 4 页要点 2） | D2 第 443、445 行、D6 | `example-04.png` 右卡：连 `ImageFiltered` 字样与描边一起糊 |
| Stack 默认 `clipBehavior=HARD_EDGE`（第 4 页要点 3 的“默认会切”） | D4 参数表、D7“Stack 中的阴影为什么被切掉” | 四例的根 Stack 都显式写 `clipBehavior="HARD_EDGE"` |
| 滤镜标签要求有限非负的 `sigmaX/sigmaY`，`tileMode` 默认 `CLAMP` | D2 第 443 行、D9 | 两卡都用 `sigmaX="6" sigmaY="6" tileMode="CLAMP"` |

## 3. 文档没写、只能自己量的结论

| 结论 | 怎么量的 | 记录 |
|---|---|---|
| `Noto Sans Mono CJK SC` 的 ASCII 步进 ≈ 0.486em（不是常见的 0.602em） | 请求 `A17-probe-mono-a1`：70 个字符、fontSize 20，墨迹首列 x=21、末字起点 x=691 → (691−21)/69 = 9.71px | `tmp/2026-10-12T10-04Z-r001/A17/probe-mono.png`；排版模型保守取 0.50em |
| CJK 满宽字步进 = 1.00em；实际行距 ≈ 1.46em | A14 用同一服务量过（本套题共享经验），A17 直接沿用 | `../../../tmp/2026-10-12T10-04Z-r001/A14/verify.py` |
| `CDATA` 段里出现 `]]>` 时，拆成相邻 `Raw` 片段即可原样印出 | 第 3 页代码面板真的印出了 `<Raw><![CDATA[<Row> 与 & 保持原样]]></Raw>` | `v007-handbook-03.png`，`zoom-v006-p3-code.png` |
| 同一棵含 `BackdropFilter` 的子树，换外层包装/画布大小就会得到不同像素（差 ≤21/255） | 请求 `A17-probe-backdrop-a/b/c-a1`：A=独立示例包装、B=页内包装（同 400×240）、C=1200×1600 页画布；A↔B 差 0.9559（max 21），差异 100% 落在滤镜矩形内 | `tmp/2026-10-12T10-04Z-r001/A17/probe-backdrop-*.png`；因此独立示例改用 `background="#FFFFFF"`，与页内白卡一致 |
| `Positioned` 只给 `width` 时 `Text` 会按该宽度软换行；109 字符的源码行确实折成两行 | 第 4 页代码面板实测，与 `measure.wrap_rows` 预测一致（此前该模型漏算空格，已修正） | `v007-verify.json` 的 `code-panel-containment` |
| `Expanded` 的 flex 比例可被像素验证 | `v007-example-02.png` 三条色块 x=24..105 / 118..281 / 294..375，宽 82/164/82 = 1:2:1 | `examples.json` 的 `flex_ratio_measured_in_example_02` |

## 4. 与手册页的对应关系

- 第 1 页 → `handbook-01.png` / `example-01.png`（核心子树：`example-01.snapshot` 第 3–41 行）
- 第 2 页 → `handbook-02.png` / `example-02.png`（核心子树：`example-02.snapshot` 第 3–41 行）
- 第 3 页 → `handbook-03.png` / `example-03.png`（核心子树：`example-03.snapshot` 第 3–38 行）
- 第 4 页 → `handbook-04.png` / `example-04.png`（核心子树：`example-04.snapshot` 第 3–65 行）

每页印刷片段、页内插图与独立渲染三者的对应行号、逐字原文和真实响应记录在
[examples.json](examples.json)。
