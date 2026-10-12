# A17 · sources.md — 每条技术结论的实际出处

路径基准 `path_base = suite_root`（见 `PATHS.md`），本文件位于
`outputs/20261008T1615Z-run01/A17/`。缓存文件都在
`tmp/20261008T1615Z-run01/_suite/docs/`；`.html` 是原始响应字节，
`.html.txt` 是 `html2txt.py` 抽出的纯文本，行号指该 `.txt`。
“请求号”是真实 HTTP 请求的 `request_id`：`shared-*` 记录在
`tmp/20261008T1615Z-run01/_suite/requests.jsonl`，`A17-*` 记录在
`tmp/20261008T1615Z-run01/A17/requests.jsonl`（本题 7 次文档请求）。
只有实际取回 200 响应的页面才列入；未读到的内容不写结论。

## 第 1 页 · 调用契约与错误响应

| # | 手册中的结论 | 来源 URL | 缓存文件:行 | 原文摘句 | 请求号 |
|---|---|---|---|---|---|
| 1.1 | 请求体是 UTF-8 纯文本，`Content-Type: text/plain` | https://open-snapshot.muedsa.com/ai-guide.md | `ai-guide.md:19` | `-H "Content-Type: text/plain; charset=utf-8"` | `shared-doc-001-guide-ai` |
| 1.2 | `<Snapshot>` 必须是文档第一个开始标签、只出现一次、必须有且仅有一个根 Widget | https://snapshot.muedsa.com/reference/parser-tags/ | `parser-tags.html.txt:483` | 必须是文档第一个开始标签，只能出现一次，并且最终必须有一个根 Widget 子节点。 | `shared-doc-004-doc-parser-tags` |
| 1.3 | `type` 决定 png/jpg/webp 编码，响应 Content-Type 与之一致 | https://open-snapshot.muedsa.com/openapi.yaml | `openapi.yaml`（responses 的 `content` 键） | `image/png` / `image/jpeg` / `image/webp` 三种成功响应体 | `shared-doc-002-openapi` |
| 1.4 | 所有响应都带 `X-Request-Id`，传入合法值被沿用，否则服务生成 UUID | https://open-snapshot.muedsa.com/openapi.yaml | `openapi.yaml:9` | 所有响应都带 `X-Request-Id`；调用方传入格式合法的值会被沿用，否则服务生成 UUID。 | `shared-doc-002-openapi` |
| 1.5 | 成功响应另有 `Server-Timing`、`X-Snapshot-Cache`、`X-Snapshot-Image-Count` 三个头 | https://open-snapshot.muedsa.com/openapi.yaml | `openapi.yaml:110`、`:112`、`:114` | 三个 header 参数定义并列于 200 响应 | `shared-doc-002-openapi` |
| 1.6 | `Server-Timing` 分段为 queue / render / image / cache;desc=hit / total，单位毫秒 | https://open-snapshot.muedsa.com/openapi.yaml | `openapi.yaml:110` 描述字段 | 同左 | `shared-doc-002-openapi` |
| 1.7 | 非成功响应是 `{code, message, requestId}` JSON；按 code 分支 | https://open-snapshot.muedsa.com/ai-guide.md | `ai-guide.md:47` | 非成功响应通常是包含 `code`、`message`、`requestId` 的 JSON。 | `shared-doc-001-guide-ai` |
| 1.8 | `400 PARSE_ERROR` 的 message 带位置，按位置修 DSL 再提交 | https://open-snapshot.muedsa.com/ai-guide.md | `ai-guide.md:47`；`parser-errors.html.txt:216` | `Pos[3:18]~72: Attr [color] unsupported CSS color [not-a-color]` | `shared-doc-001`、`A17-parser-errors-20261009T031454Z` |
| 1.9 | 401 查凭据、413 缩请求体、429 与部分 503 参考 `Retry-After` | https://open-snapshot.muedsa.com/ai-guide.md | `ai-guide.md:47` | `429` 和部分 `503` 响应可参考 `Retry-After` 延迟重试 | `shared-doc-001-guide-ai` |
| 1.10 | `?errorImage=png` 会把解析错误改成图片响应，默认不要用 | https://open-snapshot.muedsa.com/ai-guide.md | `ai-guide.md:49` | 默认不要使用 `?errorImage=png`：它会把解析错误改为图片响应 | `shared-doc-001-guide-ai` |
| 1.11 | 普通容器里出现裸文本会报 `Not Support RAWTEXT`（本页实测踩过） | https://snapshot.muedsa.com/reference/parser-errors/ | `parser-errors.html.txt:239` | `Not Support RAWTEXT` | `A17-parser-errors-20261009T031454Z` |

本页流程图与 `example-01` 只用这些结论：卡片文案逐行取自实测响应头/体的字段名，
没有编造字段。`example-01.png` 的 `ERROR 400` 行是**内容**（教学用的错误体形状），
不是某次真实失败的截图；本题 36 次渲染里唯一一次真实 400 是
`A17-hb01-v01-20261009T032843Z`（`PARSE_ERROR: Not Support RAWTEXT: ]]>`），
归档在 `tmp/20261008T1615Z-run01/A17/preview/requests/`。

## 第 2 页 · 尺寸来自布局、有界主轴与定位

| # | 手册中的结论 | 来源 URL | 缓存文件:行 | 原文摘句 | 请求号 |
|---|---|---|---|---|---|
| 2.1 | 父向下传 `BoxConstraints`，子在其中选尺寸 | https://snapshot.muedsa.com/guides/concepts/ | `concepts.html.txt:251` 附近 | 这也是图片尺寸由内容决定的原因 | `shared-doc-007-doc-concepts` |
| 2.2 | `Snapshot` 不接受单独的画布宽高 | https://snapshot.muedsa.com/guides/rendering/ | `rendering.html.txt:231` | Snapshot 不接受单独的画布宽高。 | `shared-doc-011-doc-rendering` |
| 2.3 | 固定画布要用根 `Container` 或 `SizedBox` 表达 | https://snapshot.muedsa.com/guides/rendering/ | `rendering.html.txt:243` | 因此，固定画布应通过根 `Container` 或 `SizedBox` 表达 | `shared-doc-011-doc-rendering` |
| 2.4 | Surface 取根 RenderBox 的布局尺寸并向上取整 | https://snapshot.muedsa.com/guides/concepts/、`.../rendering/` | `concepts.html.txt:251`、`rendering.html.txt:237` | 宽高分别 `ceil()` 向上取整 | `shared-doc-007`、`shared-doc-011` |
| 2.5 | 根尺寸为 0 → `layout size is empty`；无限 → `layout size is infinite` | https://snapshot.muedsa.com/reference/parser-errors/ | `parser-errors.html.txt:291`、`:293` | `IllegalArgumentException: layout size is empty` / `is infinite` | `A17-parser-errors-20261009T031454Z` |
| 2.6 | `Row`/`Column` 是 `Flex` 的特化，`Expanded` = `Flexible(fit = FlexFit.TIGHT)` | https://snapshot.muedsa.com/widgets/layout/expanded/ | `expanded.html.txt:166` | `Expanded` 是 `Flexible(fit = FlexFit.TIGHT)` 的便捷形式。 | `A17-expanded-20261009T031501Z` |
| 2.7 | `Expanded` 只能直接写在 `Flex`/`Row`/`Column` 作用域中 | https://snapshot.muedsa.com/widgets/layout/expanded/、`.../reference/parser-errors/` | `expanded.html.txt:218`；`parser-errors.html.txt:264` | must be a direct child of Flex, Row or Column | `A17-expanded-…`、`A17-parser-errors-…` |
| 2.8 | `Expanded` 依赖有限主轴，主轴无限就没有剩余空间 | https://snapshot.muedsa.com/widgets/layout/expanded/ | `expanded.html.txt:216` | Expanded 依赖 Flex 父节点和有限主轴 | `A17-expanded-20261009T031501Z` |
| 2.9 | `flex` 是剩余主轴空间的分配权重（正整数） | https://snapshot.muedsa.com/widgets/layout/expanded/ | `expanded.html.txt:188` | `flex` … 剩余主轴空间的分配权重 | `A17-expanded-20261009T031501Z` |
| 2.10 | `Positioned` 是 Stack/IndexedStack 专用 ParentDataWidget，放错父节点因 parentData 类型不匹配失败 | https://snapshot.muedsa.com/widgets/layout/positioned/ | `positioned.html.txt:162`、`:227` | `Positioned` 只能作为 `Stack` 或 `IndexedStack` 的直接子节点。 | `A17-positioned-20261009T031457Z` |
| 2.11 | 每轴 `left`/`right`/`width` 最多给两项：两边推尺寸，一边加尺寸推另一侧 | https://snapshot.muedsa.com/widgets/layout/positioned/ | `positioned.html.txt:202` | 每个轴最多指定三项中的两项 … 给出两边时尺寸由边距推导 | `A17-positioned-20261009T031457Z` |
| 2.12 | Stack 先布局非 Positioned 子节点，由它们决定尺寸 | https://snapshot.muedsa.com/guides/layout/ | `layout.html.txt:270` | `Stack` 先布局非 Positioned 子节点，再按 … 放置 | `shared-doc-008-doc-layout` |
| 2.13 | Stack 的 `clipBehavior` 默认 `HARD_EDGE`；取值 `NONE`/`HARD_EDGE`/`ANTI_ALIAS`/`ANTI_ALIAS_WITH_SAVE_LAYER` | https://snapshot.muedsa.com/reference/parser-tags/ | `parser-tags.html.txt:677`、`:633` | `clipBehavior` \| `HARD_EDGE` \| 溢出时的裁剪策略 | `shared-doc-004-doc-parser-tags` |
| 2.14 | `Container` 的 `width`/`height` 是收紧约束，父级更严格约束仍生效 | https://snapshot.muedsa.com/widgets/layout/container/ | `container.html.txt`（布局约束一节） | 同左 | `shared-doc-006-doc-container` |

`example-02.png` 的 2:1:1 三色条与两条 Positioned 演示、手册第 2 页插图里的
“flex 份额 ≈ 50/33/17%”与“left+right / left+width”两行，都是按 2.9–2.11
用真实 `Expanded` 与 `Positioned` 画出来的，不是贴图。

## 第 3 页 · 文本、转义与颜色

| # | 手册中的结论 | 来源 URL | 缓存文件:行 | 原文摘句 | 请求号 |
|---|---|---|---|---|---|
| 3.1 | 解析器不做 HTML 实体解码；要出现 `<`/`>` 用 CDATA | https://snapshot.muedsa.com/guides/parser/ | `parser.html.txt:330` | 解析器不做 HTML 实体解码。文本中要包含 `<` 或 `>` 时，使用 CDATA | `shared-doc-012-doc-parser` |
| 3.2 | `Text` 裁剪首尾空白，保留原始空白用 `Raw` | https://snapshot.muedsa.com/guides/parser/ | `parser.html.txt:338` | `Text` 会裁剪首尾空白；需要保留原始空白时使用 `Raw`。 | `shared-doc-012-doc-parser` |
| 3.3 | `Raw` 只能作为 `Text` 的行内子节点（非文本标签里不能有裸原始文本） | https://snapshot.muedsa.com/guides/parser/ | `parser.html.txt:338` | 非文本标签中不能出现非空白原始文本。 | `shared-doc-012-doc-parser` |
| 3.4 | `Text` 是 `RichText` 的便捷封装，可嵌套 `Text`/`Raw`/`Emoji`/`WidgetSpan` | https://snapshot.muedsa.com/widgets/text/text/、`.../rich-text/` | `text.html.txt`、`rich-text.html.txt` | 同左 | `shared-textdoc-20261008T145223Z`、`shared-richtext-20261008T145221Z` |
| 3.5 | `textAlign`/`softWrap`/`overflow`/`maxLines`/`textWidthBasis` 是段落属性，只作用于最外层 | https://snapshot.muedsa.com/widgets/text/text/ | `text.html.txt`（段落属性表） | 同左 | `shared-textdoc-20261008T145223Z` |
| 3.6 | `overflow` 取 CLIP（默认）/FADE/ELLIPSIS/VISIBLE，盒子太小会静默丢字 | https://snapshot.muedsa.com/widgets/text/text/ | `text.html.txt`（`overflow` 行） | 同左 | `shared-textdoc-20261008T145223Z` |
| 3.7 | 十六进制支持 3/4/6/8 位，4 与 8 位的最后一组是 alpha | https://snapshot.muedsa.com/reference/parser-tags/ | `parser-tags.html.txt:385` | 4 位与 8 位的最后一组是透明度（alpha）… `#FF000080` 是约 50% 透明红色 | `shared-doc-004-doc-parser-tags` |
| 3.8 | 旧版按 `#AARRGGBB` 解析，迁移写法 `#80FF0000` → `#FF000080` | https://snapshot.muedsa.com/guides/concepts/、`.../rendering/` | `concepts.html.txt`、`rendering.html.txt`（颜色迁移说明） | 同左 | `shared-doc-007`、`shared-doc-011` |
| 3.9 | Kotlin DSL 的颜色 Int 仍是 `0xAARRGGBB`，不受该变更影响 | https://snapshot.muedsa.com/guides/concepts/ | `concepts.html.txt`（颜色一节） | 同左 | `shared-doc-007-doc-concepts` |
| 3.10 | 布尔属性必须显式写值（`debug="true"`），只写属性名会回落默认值 | https://snapshot.muedsa.com/reference/parser-tags/ | `parser-tags.html.txt`（`Snapshot` 属性表） | `debug` 需写 `debug="true"` | `shared-doc-004-doc-parser-tags` |
| 3.11 | 标签名与属性名大小写敏感，未知属性被忽略 | https://snapshot.muedsa.com/guides/parser/ | `parser.html.txt`（属性解析规则） | 同左 | `shared-doc-012-doc-parser` |
| 3.12 | `fontFamily` 多字体用逗号分隔且名称本身要与 `/fonts` 一致；逗号后不加空格 | https://open-snapshot.muedsa.com/ai-guide.md | `ai-guide.md:43` | `fontFamily="Noto Serif SC,Noto Color Emoji"`；多个名称用英文逗号分隔 | `shared-doc-001-guide-ai` |
| 3.13 | 本手册实际用到的字体族确实装在服务上（Inter / Inter Semi Bold / Noto Sans CJK SC / DejaVu Sans Mono / Noto Sans Mono CJK SC） | https://open-snapshot.muedsa.com/fonts | `fonts.txt:1`、`:7`、`:11`、`:16`、`:25` | 每行一个字体族名称，不是 JSON | 预套件探测，响应头日期 `2026-10-08T08:14:01Z`，缓存 `tmp/20261008T1615Z-run01/_suite/docs/fonts.txt` + `.headers.txt`；**没有**对应 per-task JSONL 记录 |

`example-03.png` 的 `<b>标签</b>`、`&amp;` 与三个红色 alpha 色块（`#FF0000FF` /
`#FF000080` / `#FF00001A`）分别落在 3.1、3.7 两条结论上；手册第 3 页的
“Text 与 Raw 差别”对照块直接引用 3.2。

## 第 4 页 · 滤镜、自检与可复现交付

| # | 手册中的结论 | 来源 URL | 缓存文件:行 | 原文摘句 | 请求号 |
|---|---|---|---|---|---|
| 4.1 | `ImageFiltered` 把自身子树当输入图像应用滤镜 | https://snapshot.muedsa.com/widgets/painting/image-filtered/ | `image-filtered.html.txt:162` | `ImageFiltered` 把子树作为输入图像应用 `ImageFilter` | `A17-image-filtered-20261009T031505Z` |
| 4.2 | 要处理已画在后方的内容用 `BackdropFilter` | https://snapshot.muedsa.com/widgets/painting/image-filtered/ | `image-filtered.html.txt:206` | 它处理的是自身子树；要处理已经绘制在后方的内容，使用 BackdropFilter。 | `A17-image-filtered-20261009T031505Z` |
| 4.3 | 模糊会扩展可见像素范围，祖先裁剪可能截掉模糊边缘 | https://snapshot.muedsa.com/widgets/painting/image-filtered/ | `image-filtered.html.txt:206` | 模糊会扩展可见像素范围，祖先裁剪可能截掉模糊边缘 | `A17-image-filtered-20261009T031505Z` |
| 4.4 | `BackdropFilter` 读背后已绘制内容，按 BlendMode 合成，典型用途毛玻璃 | https://snapshot.muedsa.com/widgets/painting/backdrop-filter/ | `backdrop-filter.html.txt:162` | `BackdropFilter` 读取当前区域背后的已绘制内容，应用 `ImageFilter` 后再按 BlendMode 合成 | `A17-backdrop-filter-20261009T031503Z` |
| 4.5 | `BackdropFilter` 只有背后有内容时才可见，应配 ClipRect/ClipRRect 限定区域 | https://snapshot.muedsa.com/widgets/painting/backdrop-filter/ | `backdrop-filter.html.txt:219` | 通常应配合 ClipRect 或 ClipRRect 限制滤镜区域 | `A17-backdrop-filter-20261009T031503Z` |
| 4.6 | `blendMode` 默认 `SRC_OVER`；`sigmaX`/`sigmaY` 要求有限且非负，`tileMode` 默认 `CLAMP` | https://snapshot.muedsa.com/widgets/painting/backdrop-filter/、`.../image-filtered/` | `backdrop-filter.html.txt:173`、`:188` | `blendMode: BlendMode = BlendMode.SRC_OVER` | `A17-backdrop-filter-…`、`A17-image-filtered-…` |
| 4.7 | 通用 Skia 滤镜的输出边界不能自动查询；`blurImageFilterBounds(sigma)` 按 `ceil(3 × sigma)` 向两侧扩张 | https://snapshot.muedsa.com/widgets/painting/image-filtered/ | `image-filtered.html.txt:211`、`:233` | 分别按 `ceil(3 × sigma)` 向两侧扩张输入矩形 | `A17-image-filtered-20261009T031505Z` |
| 4.8 | Parser 的 `<ImageFiltered>` 会自动按 sigma 给出模糊输出边界，嵌在 `<ColorFiltered>` 内无需手写 `outputBounds` | https://snapshot.muedsa.com/guides/painting/ | `painting.html.txt:307` | Parser 的 `<ImageFiltered>` 会自动按 sigma 提供模糊输出边界 | `shared-doc-009-doc-painting` |
| 4.9 | 这两个滤镜标签在 Parser 侧只构造高斯模糊，复杂滤镜链走 Kotlin DSL | https://snapshot.muedsa.com/reference/parser-tags/ | `parser-tags.html.txt`（`ImageFiltered`/`BackdropFilter` 属性表只有 sigma/tileMode/blendMode） | 同左 | `shared-doc-004-doc-parser-tags` |
| 4.10 | `ColorFiltered` 要求 `color` 与 Skia `BlendMode` | https://snapshot.muedsa.com/guides/painting/ | `painting.html.txt`（ColorFiltered 一节） | 同左 | `shared-doc-009-doc-painting` |
| 4.11 | testkit 四层：布局与数值断言 → 像素采样 → Golden → Artifact；artifact 不是断言 | https://snapshot.muedsa.com/guides/testing/ | `testing.html.txt`（“测试与 Golden”正文） | 建议优先使用越靠前、越稳定的断言 … Artifact：落盘输出，供人眼检视，不作为自动断言。 | `A17-testing-20261009T031509Z` |
| 4.12 | 只有跨节点绘制、裁剪、滤镜、渐变等无法由结构证明的视觉行为才升级到像素/Golden | https://snapshot.muedsa.com/guides/testing/ | `testing.html.txt`（选择原则段） | 能用布局断言证明的行为，不使用 Golden | `A17-testing-20261009T031509Z` |
| 4.13 | 渲染是 JVM + Skia 的确定性离线过程，不经过浏览器 | https://snapshot.muedsa.com/guides/rendering/ | `rendering.html.txt`（渲染管线一节） | 同左 | `shared-doc-011-doc-rendering` |
| 4.14 | `X-Snapshot-Cache` 响应头取 `hit` / `miss`，`hit` 表示命中服务侧渲染缓存 | https://open-snapshot.muedsa.com/openapi.yaml | `openapi.yaml:112` | `X-Snapshot-Cache` 取 `hit` / `miss` | `shared-doc-002-openapi`（是否命中见下方实测第 5 条，手册措辞已按实测收敛） |
| 4.15 | 用 `X-Request-Id` 把图片与服务日志对应起来 | https://open-snapshot.muedsa.com/ai-guide.md | `ai-guide.md:47` | 成功和失败都可用 `X-Request-Id` 关联服务日志。 | `shared-doc-001-guide-ai` |

`example-04.png` 与手册第 4 页的对照插图落在 4.1–4.5：彩色条纹是真实
`Expanded` 背景，右侧卡片是 `ClipRRect` + `BackdropFilter sigmaX="12"`，
顶部标题条是 `ImageFiltered sigmaX="1.5"`（v01 用 2.5 时 15px 标题被糊到不可读，
看图后降到 1.5，见 `example-04-v01` 与 `example-04-v02` 两张预览）。

## 看图得到的、文档没写的经验（不属于文档结论）

这些只能由实际渲染得到，标注为“实测”，不冒充文档内容：

1. `Container` 盒子比文字行盒窄会在底部裁掉字形（不报错、不告警）。本题把手册
   生成器的标签盒高统一按 `ceil(fontSize × 1.42)` 放大后才不再裁字。
   证据：`hb-01-v04.png` 第 4 张流程卡 “image/png 字节” 被裁 → `hb-01-v05.png` 修复。
2. 代码字号下限（TASK.md 要求 ≥20）与行距要一起调：字号 20 时行距需 ≥29。
3. `Text` 的 CDATA 里再出现 `]]>` 会让解析器把整段吞掉并报
   `Not Support RAWTEXT: ]]>`（实测 `A17-hb01-v01-20261009T032843Z`）；
   手册里印刷 `]]>` 时拆成 `]]` + `>` 两个 `<Raw>` 片段绕开。
4. 手册印刷代码时按标签边界（`>` 之后、`<` 之前、空格串之后）续行，
   不在 token 中间断开，否则读者会抄到错误的一行。
5. **缓存没有文档读起来那么可靠**：本题 35 次渲染尝试里 34 次带
   `X-Snapshot-Cache: miss`（第 35 次是 400 错误响应，无该头）。其中包括一对
   请求体 sha256 完全相同的调用 `A17-hb03-v01-20261009T032853Z` 与
   `A17-hb03-v02-20261009T033042Z`（相隔 109 秒），两次都是 `miss`、都带
   `render;dur`、响应都是 422199 字节。全套 237 次渲染汇总为 7 hit / 211 miss /
   19 无该头（错误响应），7 次 hit 全部来自 A06/A12/A13/A15 的重复请求。
   因此手册第 4 页交付清单从“相同请求命中渲染缓存”改为“相同请求**可能**命中缓存
   （`X-Snapshot-Cache` 取 hit/miss）”，对应重渲染为 `A17-hb04-v09-20261009T040510Z`。

## 未使用/未采信的来源

- `https://snapshot.muedsa.com/reference/parser-errors/` 中被抓取两次
  （`A17-parser-errors-20261009T031454Z`、`A17-parser-errors-20261009T031526Z`），
  原因是批量脚本的 stdout 解析报错后重跑；两次都是真实 200 响应，都保留在日志里。
- 文档里出现 422 的映射只存在于 `parser-errors` 页面的“建议映射”表述，
  与 `openapi.yaml` 的实际枚举不一致，本题手册不采用 422 说法。
- 参考图/外部素材：本题为 A 类，未嵌入任何外部图片，全部插图为 DSL 构件直绘。
