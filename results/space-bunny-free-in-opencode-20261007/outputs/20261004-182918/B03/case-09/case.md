# case-09 · 版本说明 · 发行单页（anvilplot 3.14.0）

## 场景与受众

- **受众**：准备把依赖从 3.13 升到 3.14 的下游数据工程师，以及拿到这张稿子的
  项目维护者。发行当天贴在项目主页，同时也是一张可以打印的 A3 单页。
- **使用场景**：维护者手写变更清单与迁移片段，版面要在 100% 尺寸下把
  「哪条是破坏性的、怎么改、改完长什么样」三件事说清楚。读者不是图形设计师，
  是工程师，所以代码、类型标注和签名是正文，不是配图。
- **用户要完成的事**：30 秒内认出两条 BREAKING，判断自己是否受影响；
  然后照着迁移片段改掉 4 行代码；最后确认自己的 Python 版本和平台在支持矩阵里。
- **观看环境**：桌面浏览器与打印纸面，最小字号 10 px，等宽字 10.5 px。

## 内容依据

库名 anvilplot、版本号、日期、issue 编号、下载量、贡献者数、平台支持情况、
兼容性矩阵、发行节奏：**全部为自拟的演示值**，页脚已注明「anvilplot 非真实项目」。
摘要段落里引用了本套 case-07 实测出来的 `ColorFiltered` 语义，那一条是真实的
（见 case-07 的探针与 technique-notes），其余不是。

## 视觉选择与探索的能力

主打**排印 / 富文本**这一整族。所有语义先在
`tmp/20261004-182918/B03/probes/` 的六张探针上验证过才用：

| 手法 | 用在哪 | 实测结论 |
|---|---|---|
| `foregroundMode="STROKE"` + `foregroundStrokeWidth` + `foregroundStrokeJoin` | 报头 116 px 空心版本号「3.14.0」 | 空心大字可用；`Join` 取 MITER/ROUND/BEVEL 都成立（探针 c09b 第 2 行） |
| `fontFeatures="ss02"` | 报头版本号、兼容性矩阵表头、发行节奏版本号、本版数字 | **唯一两个真的生效的特性之一**：`ss02` 把数字 0 换成带斜杠的 Ø。`ss01` 也生效（更细的一套替代字形）。tnum/onum/zero/smcp/liga/kern 在这三种字体上**全部无效**（探针 c09a） |
| `textShadow` 双条（含负偏移） | 报头版本号 | 逗号分隔的多条阴影生效（探针 c09b 第 3 行） |
| `decoration` + `decorationLineStyle` + `decorationThickness` + `decorationGaps` | 「装饰线语义」四行 | SOLID / DOTTED / DOUBLE / WAVY 都能写；`decorationGaps="2 3"` 让 DOTTED 变成真点线。**没有 DASHED_DOUBLE** |
| 嵌套 `<Text>` 行内 span | 每条变更的标题（等宽）跟在行内 chip 后面 | 子 span 继承未覆盖的样式，跨行折行后仍保持（探针 c09c 第 1、2 格） |
| `<WidgetSpan alignment="MIDDLE">` | 12 条变更前的 BREAKING / DEPRECATED / FIXED / ADDED 色标 | 占位盒与文字同一基线排布，MIDDLE / BASELINE+IDEOGRAPHIC / TOP 三种对齐视觉可区分（探针 c09c 第 2 行） |
| `<Raw>` | 迁移 diff 两段、类型标注代码块 | 换行与缩进完整保留；普通 `Text` 会被 trim（探针 c09c、c09g） |
| CDATA | diff 里的 `"`、`list[float]`、`->`、`&`、`<`/`>` | 属性值不能含裸双引号；**解析器不解码 XML 实体**，`&lt;` 会原样打印，所以含引号/尖括号/& 的文本必须走 CDATA（探针 c09c 第 3 行） |
| `letterSpacing` | 报头 kicker、章节英文副标题、mono 时间戳 | 生效，正负都可用 |
| `fontHinting="NONE"` / `subpixel="false"` / `baselineMode` | 探针里逐项验证；作品正文未依赖它们 | 属性被接受；`fontEdging` 和 `textHeightMode` 找不到任何可用取值（枚举探针） |
| `shape="CIRCLE"` | 发行节奏时间轴的节点 | 与 case-01 一致，只有 RECTANGLE / CIRCLE 两种 |

## 三条必须写下来的反直觉结论

1. **`Text` 的 `height` 属性在当前服务版本里是「毒属性」。**
   写 `height="18"`、`"26"`、`"40"`、`"60"`、`"100"` —— HTTP 全部 200，
   但整段文字**一个字都不画**（探针 c09e，14 格逐项隔离）。
2. **`strutLeading` 与 `strutHeightOverridden` 同样致命。**
   `strutLeading="16"` → 整段空白；`strutLeading="0"` → 正常；
   `strutHeight="46"`、`strutEnabled`、`strutFontSize`、`strutHeightForced` → 正常。
   也就是说 `strut*` 里唯一能用的就是「什么都不做」（探针 c09e 后 7 格）。
3. **`PaintStrokeCap` 没有 `BEVEL`。** `PaintStrokeJoin` 有。同一个前缀、
   两套取值集，文档与枚举页都没写，只能一个个试（枚举探针 `cap-BEVEL` → 400）。
   另外 `fontFeatures="zzzz"` 这种根本不存在的标签**被静默接受**，
   和「未知属性被静默忽略」是同一类问题。

## 实际自检

| 检查项 | 实际值 | 结论 |
|---|---|---|
| 服务响应 | `POST /snapshot` 200，PNG 1500×1090 RGBA，原始响应字节无后处理 | 通过 |
| 元素数 | 372（`final.snapshot` 标签计数），远低于 4096 | 通过 |
| `D.warnings()` | 交付那一版 0 条 | 通过 |
| 12 条变更全部显示 | v3 只画到 11 条（最后一条被摘要带盖住）；v4 收紧行距后 12 条全在 | 通过 |
| 摘要与清单一致 | 摘要原写「没有引入新的破坏性变更，仅有两项弃用与七项修复」，与清单矛盾（实为 2 BREAKING / 2 DEPRECATED / 3 ADDED / 5 FIXED）；v6 改为从 `CHANGES` 实算，印「12 条变更里 2 条破坏性变更、2 条弃用、3 条新增、5 条修复」（`crops/final-review2-c09-summary.png` 1.8× 复验） | 通过 |
| 代码块不截断 | 迁移 diff 两段各 4 行、类型标注 5 行，v4 逐行放大核对 | 通过 |
| 右栏不越界 | 兼容性矩阵 v3 的 3.14 列跑出画布；v4 改成 138 px 标签列 + 5×52.4 px 数据列 | 通过 |
| 排版标签打架 | v3「本版数字」标题压在时间轴最后一行上；v4 时间轴行距 38→34、标题下移 | 通过 |
| 空心版本号 | 3.14.0 为描边而非实心，且 0 是带斜杠的 Ø | 通过（`crops/` 未放大，因 116 px 下足够清楚） |
| 装饰线四态可区分 | SOLID/WAVY/DOTTED/DOUBLE 在 4× 裁切下逐条可分；SOLID 因 1.6 px 太细，v5 提到 2.6 px | 通过 |
| 素材 | 无外部素材、无 `<Image>`、无后处理 | 通过 |

## 迭代过程（实际看图记录）

1. **v1**：400 `Attr [color] color must be …`——我写的 `#9CA3AFF` 是 9 位 hex。
   同一次还有一个 `text=` 属性里塞了 `0B0B0F` 的占位文本，被 dsllib 的
   宽度检查报警。两条都是我的笔误，改掉。
2. **v2**：看图发现右栏兼容性矩阵的最后一列被推出画布右缘；「变更清单」第 12 条
   落在摘要带底下。→ 矩阵改成独立标签列 + 5 个等宽数据列；变更行距 56→50。
3. **v3**：迁移 diff 的两段代码各被截掉 1–2 行（我按 1.2em 估行高，实际
   DejaVu Sans Mono 的段落行距约 1.55em）；类型标注代码块最后一行也被切。
   → 每段盒子从 72 px 提到 80 px；类型标注去掉一个空行、盒子 106→114 px。
4. **v4**：「本版数字」标题与时间轴最后一行重叠；右下角「装饰线语义」的两行
   说明撞到面板底边与摘要带。→ 时间轴行距 34、标题下移到 730、统计区起点
   788；装饰线四行行距 36、注释压成一行。
5. **v5**：4× 裁切放大后发现 SOLID 装饰线几乎看不见（1.6 px 在 14 px 字上太细）
   → 每行给不同 `decorationThickness`（2.6/2.0/2.4/2.0）；同时把类型标注最后
   一行缩短到不折行。
6. **v6（收尾复审）**：把十张 `final.png` 逐张重新打开后，对着「变更清单」
   数了一遍 chip：BREAKING 2、DEPRECATED 2、ADDED 3、FIXED 5 = 12，与表头
   `CHANGELOG · 12 ENTRIES` 一致；但摘要带写的是「没有引入新的破坏性变更，
   仅有两项弃用与七项修复」—— 清单里明明有两条 BREAKING，修复也只有五条。
   这是**字与图互相打脸**，而且因为摘要紧挨着清单，最容易被读者抓到。
   → 把三个数字改成从 `CHANGES` 实算（`_CNT`），文案改为
   「12 条变更里 2 条破坏性变更、2 条弃用、3 条新增、5 条修复」，并加一条
   `assert` 保证四类之和必须等于 12，以后改清单不会再漏。
   1.8× 复验（`crops/final-review2-c09-summary.png`）通过。

## 遗留 / 不足

- **两个属性在本服务版本里无法使用**：`Text height` 与 `strutLeading` /
  `strutHeightOverridden`（见上）。这意味着「行高」这件事在 DSL 里只能靠
  盒子高度和多个独立 `Text` 手工排布，做不到真正的段落行距控制。
  本页所有多行文本都是用「一个 span 换一次行」的方式排的，不是靠行高。
- `fontFeatures` 在这套字体上几乎全废：16 组特性里只有 `ss01`/`ss02` 在 Inter 上
  生效，且 `tnum`（等宽数字）这种最该有用的没有。所以本页的
  「1,284,930」「312」这类数字**没有**做到等宽对齐，是设计上的妥协。
- 没有真正的行内代码高亮（syntax highlighting）：diff 的红/绿是按「旧/新」
  整块上色，不是按 token 上色。DSL 只能整体给一个 `color`。
- 「已知问题」里那条 issue #2311 是虚构的。
