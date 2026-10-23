# Snapshot 使用情况说明与踩坑记录

任务ID：A11
任务名称：文字保真与跨页结算单（双语发票样张）
本次运行ID：`r20261014T1536+0800-5f11da`
完成状态：完成
结束原因：需求满足并完成视觉自检（14/14 项检查通过，两页最终图逐区实际查看并复核）
输出目录：`outputs/r20261014T1536+0800-5f11da/A11`
临时目录：`tmp/r20261014T1536+0800-5f11da/A11`
路径基准：`suite_root`（总任务根）；本文档内的本地链接相对本文件所在目录
结构化指标：[task-metrics.json](task-metrics.json)
模板来源：[snapshot-usage-template.md](../../../tasks/A11-bilingual-invoice/templates/snapshot-usage-template.md)
路径约定：[PATHS.md](../../../PATHS.md)

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应 DSL 或图片 | 完成状态 |
|---|---|---|---|
| [invoice-page-01.png](invoice-page-01.png) | 服务返回的第 1 页最终图（1200×1600 PNG，238 801 B） | [invoice-page-01.snapshot](invoice-page-01.snapshot) | 完成 |
| [invoice-page-02.png](invoice-page-02.png) | 服务返回的第 2 页最终图（1200×1600 PNG，249 682 B） | [invoice-page-02.snapshot](invoice-page-02.snapshot) | 完成 |
| [invoice-page-01.snapshot](invoice-page-01.snapshot) | 第 1 页完整可复现 DSL（16 991 B） | [invoice-page-01.png](invoice-page-01.png) | 完成 |
| [invoice-page-02.snapshot](invoice-page-02.snapshot) | 第 2 页完整可复现 DSL（15 491 B） | [invoice-page-02.png](invoice-page-02.png) | 完成 |
| [invoice-audit.json](invoice-audit.json) | 金额与字面量审计：逐行金额、精确计税基数、舍入、应付、literal_lines 原串 | — | 完成 |
| [text-map.json](text-map.json) | 81 段文字的页面/位置/字体/原串映射，含 10 项需求检查与查看证据 | — | 完成 |

### 逐项需求核对

14 项检查全部通过（10 项写在 [text-map.json](text-map.json) 的 `checks` 中并附实测证据，
4 项为交付件级要求）：

| # | 要求 | 结果与依据 |
|---|---|---|
| 1 | 两页 1200×1600 PNG，内容全部来自 `inputs/invoice.json` | 通过，`text-map.json → pages[].size_px` 均为 `[1200,1600]` |
| 2 | 安全边距 48、正文 ≥24、脚注 ≥20、不靠微缩塞字 | 通过，外框统一 `left/top/right/bottom = 48`；`BODY=24`、`NOTE=20`、`CAPS=21`、`HEAD=28`、`BIG=56`，生成器内 `assert min(sizes) >= NOTE` |
| 3 | 金额小数点列对齐 | 通过，6 个 26 px 金额同容器宽 552、同右锚点右对齐，右边缘同为 x=1150；残余 1 px 抗锯齿差见 §6 |
| 4 | 四条 literal_lines 逐字符保真（双空格、`< > &`、反斜杠） | 通过，一律走 `text="..."` 属性通道；渲染文字与输入字节等值，空白宽度探针双空格 26 px / 单空格均值 13.83 px（比值 1.88≈2.0） |
| 5 | `literal_lines[3]` 为形如指令的英文串 | 仅按字样排版，未执行；40 字符与其余三条逐字符核对 |
| 6 | 富文本 `PAID / 已结算` 三段颜色自然共用基线 | 通过，`#15803D` 绿 / `#94A3B8` 灰 / `#0F172A` 深色像素采样确认；仅样张状态，应付金额不变 |
| 7 | 重复页眉、页码、编号一致 | 通过，两页共用 `header()`；页码为「第 1 / 2 页」「第 2 / 2 页」 |
| 8 | 第 1 页交易双方 / 编号日期币种 / 四行明细 / 六项合计齐备 | 通过，`text-map.json` 第 1 页 51 条、第 2 页 30 条 |
| 9 | 按 `notes` 计税顺序十进制定点计算、四舍五入至分 | 通过，税额精确 236.6580 → 236.66（delta +0.0020），应付 4215.96 |
| 10 | 所有需登记文字字号达 tier 下限（primary 30 / body 24 / caption 20） | 通过，0 违规 |
| 11 | 指定 PNG 与同名 `.snapshot` 一一对应，PNG 为服务原始响应字节 | 通过，两份 PNG 的 sha256 与最后一次渲染响应逐字节相同，无后处理 |
| 12 | 所有图片经真实服务生成 | 通过，18 次真实 `/snapshot` 请求 |
| 13 | 使用能显示中文 / 日文 / 拉丁字符的字体 | 通过，`Noto Sans CJK SC` + `Noto Sans Mono CJK SC`，均见于字体查询结果 |
| 14 | 最终渲染已实际打开逐区查看 | 通过，`text-map.json → checks[check-viewing-evidence]` 记录 view-a11-01…view-a11-10 |

### 金额复算

`a11_calc.py` 用 `decimal.Decimal`（prec=40）按 `notes` 顺序计算，
`a11_verify.py` 用 `fractions.Fraction` 完全独立的路径复算并逐项断言：

- 4 行金额 `805.50 / 478.80 / 1160.00 / 1680.00`，货品小计 4 124.30
- 折扣 180.00 → 税前货品额 3 944.30
- 税额精确值 3 944.30 × 6% = 236.6580 → `ROUND_HALF_UP` 至分 = 236.66（唯一取整步骤）
- 运费 35.00 不计税；应付 = 3 944.30 + 236.66 + 35.00 = 4 215.96，无二次取整

`invoice-audit.json` 的 `self_check` 3 项全为 `true`；
`a11_verify.py` **33 项断言全部通过**（收口阶段现场执行确认，输出 `ALL CHECKS PASSED (33 assertions)`）。

### 交付标准依据

判定完成不依赖「渲染成功 / 文件齐全 / 数量达标」，而是：

1. 每处文字的实际墨迹盒由 [a11_measure.py](../../../tmp/r20261014T1536+0800-5f11da/_suite/gen/a11_measure.py)
   从最终 PNG 量出，与 DSL 放置盒双向对照（81 条逐条记录在 text-map.json）。
2. 字号不是声明值，而是用「同一字符串墨迹跨度比 = 字号比」实测：
   第一版正文为终版的 0.809、脚注 0.798 → 折算 20 px / 16 px，据此判不达标并重排。
3. 最终两页逐区放大查看，10 次查看事件带裁切框与检查内容记录在 text-map.json。
4. 已知缺陷（§4 表中的 a11-i1…i13）在标完成前全部处置：8 项已修、1 项有绕过方案、
   1 项已披露为不可逆、1 项实测后确认为非缺陷。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`
文档访问日期：2026-10-14（共享准备阶段）与 2026-10-16（本题新增 4 页），均为本次运行真实请求

共享准备阶段读取（`tmp/r20261014T1536+0800-5f11da/_suite/docs/`，9 次请求，跨题复用不重复计）：

| 文档 | 本次使用的知识 |
|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求体为 UTF-8 纯文本、`Content-Type: text/plain; charset=utf-8`、成功返回图片字节、失败返回 JSON；错误处理与字体查询方式 |
| https://snapshot.muedsa.com/ | DSL 总览与页面入口 |
| https://snapshot.muedsa.com/reference/parser-tags/ | `Snapshot / Container / Stack / Positioned / Text / Raw / Border` 的标签集合与嵌套关系 |
| https://snapshot.muedsa.com/guides/layout/ | `Container.alignment` 只接受 BoxAlignment 枚举，与 `Text.textAlign` 是两套东西 |
| https://snapshot.muedsa.com/guides/painting/ | `color` / `Border border="1 SOLID #hex"` 的写法 |
| https://snapshot.muedsa.com/guides/media-text/ | 富文本嵌套与基线共用方式 |
| https://snapshot.muedsa.com/guides/widgets/ | 可用组件边界 |
| https://open-snapshot.muedsa.com/fonts | 字体查询：确认 `Noto Sans CJK SC` 与 `Noto Sans Mono CJK SC` 可用（缓存 `docs/fonts.txt`） |
| https://open-snapshot.muedsa.com/openapi.yaml | `/snapshot` 的请求/响应契约 |

本题新增 4 次文档请求（记入 A11 的 requests.jsonl）：

| 文档页面 | 本次使用的知识 | 对应文件与位置 |
|---|---|---|
| https://snapshot.muedsa.com/reference/parser-text/ | `Text` 的 `text` 属性、子内容形态差异、`letterSpacing` | `invoice-page-0{1,2}.snapshot` 全部 81 处文字 |
| https://snapshot.muedsa.com/reference/text-layout/ | `Text.textAlign`、文本盒对齐 | 表格与合计区的右对齐列 |
| https://snapshot.muedsa.com/reference/text-style/ | `fontFamily` / `fontSize` / `fontStyle="BOLD"` / `color` | 字号阶梯与色彩体系 |
| https://snapshot.muedsa.com/reference/enums/ | BoxAlignment 枚举取值、`mode="light|dark"` | 深色底上的白字（表头、应付强调带） |

### 实际使用的能力

- **布局**：`Container` + `Positioned` 绝对定位搭骨架；`Container.alignment` 做盒内对齐；
  两页共用同一 `header()` 函数保证页眉一致。
- **文本**：中文用 `Noto Sans CJK SC`，金额与 SKU 用 `Noto Sans Mono CJK SC`（等宽，
  ASCII 步进 = fontSize/2），配合固定宽容器 + 右对齐得到精确的小数点列。
- **富文本**：`<Text><Text color="#15803D">PAID</Text><Raw color="#94A3B8"> / </Raw>
  <Text color="#0F172A">已结算</Text></Text>` —— 只写在**子内容形态**上才生效（见 §4 a11-i4）。
- **颜色/装饰**：teal 主色阶 + slate 中性阶；`Border border="1 SOLID #E2E8F0"` 描边、
  斑马纹行底、强调带左侧 8 px 色条；`mode="light"` 处理深底浅字。
- **未使用**：图片、滤镜、变换、裁剪、媒体元素。A 类为 `dsl_only`，主体全部由 DSL 构造。

## 3. 迭代过程、服务调用与图像检查

请求记录：[requests.jsonl](../../../tmp/r20261014T1536+0800-5f11da/A11/requests.jsonl)（22 条）
迭代记录：[iterations.jsonl](../../../tmp/r20261014T1536+0800-5f11da/A11/iterations.jsonl)（18 条）

| 统计项 | 值 |
|---|---|
| 渲染请求总数 | 18 |
| 成功次数 | 15 |
| 失败次数 | 3（全为 HTTP 400 语法错误） |
| 重试请求数 | 2（`probe3-child-raw` 的 attempt 2 与 3，是总请求的子集） |
| 文档请求数 | 4（另有 9 次共享准备请求，跨题复用不重复计） |
| DSL 文件数 / 唯一文本数 | 15 / 13（终版第 1、2 页各有 1 份字节相同的 v2 副本） |
| 响应文件数 | 15 PNG + 3 错误 JSON |
| 实际图片查看次数 | 35 |
| 完成迭代数 | 17 |
| 未完成迭代数 | 1（`a11-it-05`，三次 400 未取得图片） |
| 迭代构成 | baseline 1 / diagnostic 10 / build 5 / fix 1 / review 1 |
| 渲染耗时之和 | 45.500 s |
| 文档耗时之和 | 6.703 s |
| 全部请求耗时之和 | 52.203 s（22 条全部有 `elapsed_ms`，0 条排除） |

### 逐请求记录

时间为 `Asia/Shanghai (UTC+08:00)`。路径相对总任务根。

| 请求 ID | 迭代 | 阶段 | 起→止（秒） | 状态 / Content-Type | 响应文件 | 查看与实际结果 |
|---|---|---|---|---|---|---|
| `req-7cc7ee4bc175` | — | 文档 | 09:02:23→09:02:25（2.063） | 200 / text-html | `docs/dsl/parser-text.html` | 已读，确定 `text` 属性与子内容形态 |
| `req-7fd3c89fdf10` | — | 文档 | 09:02:25→09:02:27（1.421） | 200 / text-html | `docs/dsl/text-layout.html` | 已读，确定 `textAlign` |
| `req-8e4ef03e2474` | — | 文档 | 09:02:27→09:02:28（1.657） | 200 / text-html | `docs/dsl/text-style.html` | 已读，确定字号/字体/样式属性 |
| `req-852e662461c5` | — | 文档 | 09:02:28→09:02:30（1.562） | 200 / text-html | `docs/dsl/enums.html` | 已读，确认 alignment 枚举 |
| `req-a11-probe-text-1e8326` | `a11-it-01` | 基线 | 09:08:48→09:08:53（5.828） | 200 / image-png（147 365 B） | `responses/req-a11-probe-text-1e8326.png` | 已查看 + 3 处放大（digits/row5/spaces）：字体覆盖 OK，发现实体不解码、等宽墨块数≠字符数 |
| `req-a11-probe2-safe-2b9745` | `a11-it-02` | 诊断 | 09:14:17→09:14:20（3.453） | 200 / image-png（66 920 B） | `responses/…2b9745.png` | 已查看：数字/十六进制引用、实体写法均得不到字面 `< > &` |
| `req-a11-probe2-raw-amp-f56016` | `a11-it-03` | 诊断 | 09:14:20→09:14:22（1.859） | 200 / image-png（28 947 B） | `responses/…f56016.png` | 已查看：子内容原样 `&` 可渲染 |
| `req-a11-probe2-raw-lt-3bc19c` | `a11-it-04` | 诊断 | 09:14:22→09:14:24（1.750） | 200 / image-png（28 478 B） | `responses/…3bc19c.png` | 已查看：子内容原样 `<` 在探针页可渲染，但下一页组合会 400 |
| `req-a11-probe3-attr-raw-e062b5` | `a11-it-03` | 诊断 | 09:16:44→09:16:46（1.546） | 200 / image-png（36 476 B） | `responses/…e062b5.png` | 已查看：属性值可承载原样 `<` |
| `req-a11-probe3-attr-allraw-c83e90` | `a11-it-04` | 诊断 | 09:16:46→09:16:47（1.844） | 200 / image-png（34 692 B） | `responses/…c83e90.png` | 已查看：`< > &` 三字符在属性值内全部字面 |
| `req-a11-probe3-child-raw-6c74d5` | `a11-it-05` | 诊断 | 09:16:47→09:16:48（0.922） | **400** / application-json | `responses/…6c74d5.error.json` | 未取得图片：子内容原样 `<` 语法错误 |
| `req-a11-probe3-child-raw-d82768-a2` | `a11-it-05` | 重试 | 09:16:53→09:16:55（1.500） | **400** / application-json | `responses/…d82768-a2.error.json` | 未取得图片：同因，attempt 2 |
| `req-a11-probe3-child-raw-b9f7b9-a3` | `a11-it-05` | 重试 | 09:17:00→09:17:01（0.860） | **400** / application-json | `responses/…b9f7b9-a3.error.json` | 未取得图片：同因，attempt 3；判定为服务端契约，转用属性通道 |
| `req-a11-probe3-nested-attr-6168a1` | `a11-it-06` | 诊断 | 09:17:06→09:17:08（2.500） | 200 / image-png（35 275 B） | `responses/…6168a1.png` | 已查看：嵌套 `Text` 的**属性形态**不生效子级颜色，外层覆盖 |
| `req-a11-probe3-attr-long-167c57` | `a11-it-07` | 诊断 | 09:17:08→09:17:10（1.594） | 200 / image-png（37 153 B） | `responses/…167c57.png` | 已查看：属性值承载长串与反斜杠原样 |
| `req-a11-probe4-layout-173945` | `a11-it-07` | 方案探索 | 09:22:13→09:22:14（1.422） | 200 / image-png（93 287 B） | `responses/…173945.png` | 已查看：真实数据试排，量出金额列与双空格 |
| `req-a11-probe4b-layout-43490f` | `a11-it-08` | 方案探索 | 09:23:59→09:24:03（3.672） | 200 / image-png（101 613 B） | `responses/…43490f.png` | 已查看 + 2 处放大（L12/L34 行）：定稿排版方案 |
| `req-a11-invoice-page-01-b2f090` | `a11-it-09` | 首版 | 09:37:52→09:37:56（3.859） | 200 / image-png（242 029 B） | `responses/…b2f090.png` | 已查看 + 3 处放大：**不达标**，正文≈20 px、脚注≈16 px |
| `req-a11-invoice-page-02-9cdbb8` | `a11-it-10` | 首版 | 09:40:33→09:40:36（3.438） | 200 / image-png（207 056 B） | `responses/…9cdbb8.png` | 已查看 + 2 处放大：同一字号问题 |
| `req-a11-invoice-page-01-a5701c` | `a11-it-11` | 视觉迭代 | 09:51:21→09:51:24（2.969） | 200 / image-png（238 156 B） | `responses/…a5701c.png` | 已查看 + 表格放大：字号达标，但合计 6 金额混用 24/26 px |
| `req-a11-invoice-page-02-e2f4d1` | `a11-it-12` | 视觉迭代 | 09:51:55→09:51:58（3.031） | 200 / image-png（249 682 B） | `responses/…e2f4d1.png` | 已查看：最终第 2 页，10 项检查通过 |
| `req-a11-invoice-page-01-74bbd3` | `a11-it-13` | 修复 | 09:55:37→09:55:40（3.453） | 200 / image-png（238 801 B） | `responses/…74bbd3.png` | 已查看 + 10 次逐区查看（view-a11-01…10）：最终第 1 页 |

### 实际查看次数（35 次）

| 类别 | 次数 | 对象 |
|---|---|---|
| 最终页逐区查看（记录在 text-map.json） | 10 | view-a11-01…10，含 `crop_box_from` 与检查内容 |
| 交付前整页与局部复核（上下文压缩前） | 8 | 两页整页、表格、合计、尾部、literal 区、盖章区、L12/L34 放大 |
| 探针阶段看图 | 15 | 12 张探针 PNG + 3 处探针放大 |
| 收口阶段对比 | 2 | 第一版与终版表格区对比，确认取代理由 |

## 4. 修改记录与踩坑

| 迭代 / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| `a11-it-01`→`a11-it-02` / 方案探索 / `a11-it-01` | 子内容写 `&lt;` 原样显示 `&lt;` | **实测**：解析器不解码实体（探针 1、2） | 放弃实体写法 | 数字/十六进制引用、实体写法均失败 | `dsl/probe2-*.snapshot` |
| `a11-i2` / 语法修复 / `a11-it-05` | 子内容原样 `<` → HTTP 400 | **实测**：3 次尝试（attempt 1/2/3）均 400，错误体同为 223 B JSON。属服务端契约，非限流，无 Retry-After | 含 `< > &` 的文本一律走 `text="..."` 属性 | 属性通道在 F1/F2/F5 探针全部字面通过 | `responses/…6c74d5/d82768/b9f7b9.error.json` |
| `a11-i4` / 视觉迭代 / `a11-it-06` | 嵌套 `<Text text="PAID" color="#15803D"/>` 不显示绿色 | **实测**：属性形态下子级颜色被外层覆盖（探针 F4） | 改用子内容形态 `<Text color="#15803D">PAID</Text>` | 像素采样确认三段颜色，共用基线 | `dsl/probe3-nested-attr.snapshot` |
| `a11-i11` / 判据修正 / `a11-it-01` | 等宽墨块数 ≠ 字符数 | CJK 笔画碎裂成多个墨块、ASCII 空格无墨迹，墨块计数不可作等值判据 | 改为三项判定：DSL `text` 属性字节等值 + 渲染文字与输入等值 + 空白宽度探针 | 双空格 26 px、单空格均值 13.83 px，比值 1.88≈2.0 | `tmp/…/A11/gen/*.measure.json` |
| `a11-i5` / 视觉迭代 / `a11-it-09,10` | 第一版正文≈20 px、脚注≈16 px，低于「正文≥24、脚注≥20」 | **实测**：名称列文字墨迹跨度为终版的 0.809、页脚 0.798；墨迹高度 20/23 与 16/20 | 统一 `BODY=24 / NOTE=20 / CAPS=21`，两页重排，生成器内加 `assert min(sizes) >= NOTE` | `check-type-size-floors` 0 违规 | `responses/…b2f090.png`、`…9cdbb8.png` |
| `a11-it-13` / 修复 / `a11-it-11` | 合计 6 个金额字号不统一 | **实测**：同一字符串 4 行墨迹跨度为终版的 0.922 倍（24 px），2 个强调行与终版逐像素相同（26 px） | 6 个金额统一 `size=26` | 六行跨度一致，右边缘同为 x=1150；`check-decimal-column-alignment` 通过 | `responses/…a5701c.png` → `…74bbd3.png` |
| `a11-i6` / 工具修复 / — | `next_iteration_seq` 撞号：取 `max(已用最大值, floor)`，floor 等于已用最大值时必撞 | 早期探针脚本按 CASES 下标派生编号，导致 seq 与 id 3/4/7/12 各重复一次 | 改为返回 `>= floor` 的最小未占用序号 | 重跑 page-01 取得 seq=13 而非再撞 12 | `tools/suite.py` |
| `a11-i12` / 工具修复 / — | 自建 `ink_bbox()` 的 `maxx = x` 未做比较更新，被后续任意有墨迹行覆盖 | 双循环结构错误；返回的是「最后一行有墨的行」的最右像素，而非全区的 | 四个极值改为按比较更新，并在 docstring 里写明原因 | 两页 `full_page_ink_bbox` 由 `[0,0,1104,1547]` 更正为 `[0,0,1200,1547]`（两页均含顶栏与强调带装饰），页脚带复核为 `[49,1525,1151,1547]`；81 处逐条 `ink_box` 来自 a11_measure.py、不受影响，10 项检查复核仍全部 PASS | [a11_textmap.py](../../../tmp/r20261014T1536+0800-5f11da/_suite/gen/a11_textmap.py) |
| `a11-i8` / 流程偏离 / — | 重渲覆盖了 3 份被取代的页面 DSL 文本 | `a11_client.render()` 按 `dsl_name` 写 `tmp/dsl/<stem>.snapshot`，生成器固定传 `<stem>.snapshot` | 建 [superseded-MANIFEST.md](../../../tmp/r20261014T1536+0800-5f11da/A11/dsl/superseded-MANIFEST.md) 逐项登记；后续任务改为按 request_id 命名 DSL | **不可逆**：5 份页面响应 PNG 全部保留（5 个不同 sha256），3 份 DSL 文本无法还原，未做伪造重建 | `tmp/…/A11/dsl/`、`tmp/…/A11/responses/` |
| `a11-i9` / 记录更正 / — | 迭代 detail 写「第一版正文缩到 14–21px」是估计值 | 未量像素就写入结论 | 追加 `a11-it-14` 更正为「正文≈20 px、脚注≈16 px」；违规结论不变 | 历史行原样保留，更正与披露分开 | `iterations.jsonl` |
| `a11-i13` / 记录更正 / — | `invoice-audit.json` 的 `fidelity_notes.angle_amp` 沿用探针期说法「源文以 XML 实体书写」，与最终实现矛盾 | 探针期结论写进审计文件后未随实现更新 | 更正说明，注明实体不解码与子内容 400 两项实测；重生成 audit JSON | 金额与自检值不变，33 项断言重跑仍全部通过 | `outputs/…/A11/invoice-audit.json` |
| `a11-i3` / 已接受取舍 / — | `text` 属性通道无法承载子级样式 | 保真与样式无法同通道 | 含 `< > &` 的文本一律用 `text` 属性；需子级样式处不用这些字符 | 已接受，非缺陷 | — |

**从文档了解到、本次未触发**：`Image` / 媒体元素与滤镜变换（A 类 `dsl_only`，未使用）；
429/503 限流退避（本次未遇到 429 或 503，`rate_limit_wait_seconds = 0`）。

## 5. 任务耗时与请求统计

结构化指标：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始时间 | 2026-10-16T08:57:50+08:00 | ISO 8601 / Asia/Shanghai | `tmp/…/_suite/events.jsonl → task_started[A11].ts` |
| 任务结束时间 | 见 task-metrics `ended_at` | ISO 8601 / Asia/Shanghai | 写入 metrics 时刻，含收口核对与文档撰写 |
| 任务总耗时 | 9 635 | 秒（约 2.68 h） | 墙钟，含看图、量测、文档撰写 |
| 核心制作耗时 | 3 470 | 秒（约 0.96 h） | 起点到最后一版页面渲染结束（09:55:40），不含收口 |
| 首次可用图耗时 | 663 | 秒（约 11.1 min） | 到 `req-a11-probe-text-1e8326` 返回 147 365 B PNG |
| 等待用户反馈 | 0 | 秒 | 单轮任务，无用户反馈等待 |
| 限流等待 | 0 | 秒 | 未遇到 429/503，无 Retry-After |
| 排队等待 | 0 | 秒 | 仅按服务端返回时间测量；服务端未提供排队时间，无独立排队等待发生 |
| 已记录请求耗时之和 | 52.203 | 秒 | 22 条请求全部有 `elapsed_ms`（渲染 45.500 + 文档 6.703），0 条排除；**不等于任务总耗时** |
| 服务端计时来源 | 本地实测往返 | — | 记录 `elapsed_ms` 为本地计时，非服务端 `server-timing` 头（该头不可取得，记为 null） |
| 渲染请求 成功/失败/重试 | 15 / 3 / 2 | 次 | `requests.jsonl`，3 次失败均为 HTTP 400 |
| 其他接口请求 | 4（+ 9 次共享准备） | 次 | 本题 4 次文档请求；共享 9 次为跨题复用，不重复计 |
| DSL 版本数 | 13 唯一文本（15 文件） | 份 | 按 sha256 去重；2 对字节相同的终版副本 |
| 实际看图次数 | 35 | 次 | 10 最终逐区 + 8 交付前复核 + 15 探针 + 2 收口对比 |
| 完成迭代数 | 17 | 次 | `iterations.jsonl` 共 18 条，其中 17 条 `outcome=done` |
| 未完成迭代数 | 1 | 次 | `a11-it-05`（诊断探针），三次 400，未取得图片 |
| 迭代构成 | baseline 1 / diagnostic 10 / build 5 / fix 1 / review 1 | 次 | 合计 18；其中「查看旧图→修改→再渲染→再查看比较」构成的完整视觉迭代为 `a11-it-08`（probe4→probe4b）、`a11-it-11/12`（首版→字号重排）、`a11-it-13`（字号统一→终版）共 3 次，其余为基线、诊断探针、构建、复核 |

## 6. 设计选择、经验与未解决事项

### 设计选择

- **等宽字体 + 固定宽容器 + 右对齐**做金额列，而不是逐字符 `Positioned`。
  代价是等宽字形下小数点左侧的字形宽度不受控（因此出现 1 px 的抗锯齿残差），
  换来的是列宽调整时对齐自动成立、DSL 简洁得多。
- **两页共用一个 `header()` 函数**而不是复制粘贴，页眉一致性由构造保证而非事后核对。
- **金额只从 `invoice-audit.json` 取**，页面生成器 `assert` 期望值，避免渲染层与计算层各算一遍。
- **保真与样式分层**：含 `< > &` 的文本走 `text` 属性（保真优先），需要子级样式的富文本不含这些字符。
- **色板**：teal 主色阶（`#0F766E` / `#134E4A`）承担「金额与状态」，slate 中性阶承担结构，
  amber 只标折扣、green 只标 PAID —— 状态色不复用为普通序列色。

### 可复用经验（供后续题目）

1. **解析器不解码实体**：子内容写 `&lt;` 会原样显示 `&lt;`。
2. **子内容原样 `<` 直接 400**；`text="..."` 属性值里的 `< > &` 按字面取用，是唯一保真通道，
   但无法承载子级样式。
3. **嵌套 `Text` 的子级样式只在子内容形态生效**，写成 `<Text text=".." color=".."/>` 会被外层覆盖。
4. **`Container.alignment` 只接受 BoxAlignment**，与 `Text.textAlign` 是两套机制，混用会静默失败。
5. **Noto Sans Mono CJK SC 是等宽**：ASCII 步进 = fontSize/2，CJK 全宽 = fontSize。
6. **字号必须实测**：同一字符串的墨迹跨度比等于字号比，可无损判定实际字号，
   比读回 DSL 声明值可靠（本次正是靠它抓出第一版 20/16 px 的违规）。
7. **别用等宽墨块数当字符数**：CJK 笔画碎裂、ASCII 空格无墨迹，只能作参考。
8. **DSL 临时文件按 request_id 命名**，不要按 label 命名 —— 否则重渲会覆盖被取代版本（a11-i8）。
9. **追加式日志只增不改**：数字写错就追加更正记录 + 在 metrics 里披露，不要回改历史行。

### 未解决事项

| ID | 状态 | 说明与恢复办法 |
|---|---|---|
| `residual-decimal-1px` | 仅装饰性残差，判定为非缺陷 | 6 个 26 px 金额的小数点墨迹起点有 1117 / 1118 两个值，差 1 px。同字号、同容器宽 552、同右锚点、同字符数，属同一字形单元的抗锯齿覆盖差异；六行右边缘完全同为 x=1150。如需严格同一列，可改逐字符 `Positioned` 排版 |
| `superseded-dsl-lost` | 不可逆，已披露 | 3 份被取代页面 DSL 文本不可还原（a11-i8）。5 份响应 PNG 完整保留，终版 DSL 有两份独立副本，不影响交付；清单见 `tmp/…/A11/dsl/superseded-MANIFEST.md` |
| `residual-iteration-id-collision` | 已披露 | `iterations.jsonl` 中 `a11-it-03/04/07/12` 的 `id` **与** `seq` 各重复一次（两者同源，早期探针脚本按 CASES 下标派生），所以两个字段都不是唯一键；日志只增不改，原样保留。计数按行数、去重按 `(id, seq, label)`，重复行可由 `label` 与 `request_ids` 明确区分；`next_iteration_seq` 已修复，新建迭代不再撞号。完整清单见 [task-metrics.json](task-metrics.json) 的 `logs.duplicate_iteration_id` |

### 留痕与 .gitignore 确认

- 临时目录草稿、备选方案、脚本、请求响应、**3 份 400 错误 JSON**、探针 PNG 与量测输出全部保留，
  未清理、未删除失败尝试：`tmp/r20261014T1536+0800-5f11da/A11/{dsl,responses,preview,gen}/`。
- 已下载文档缓存在 `tmp/r20261014T1536+0800-5f11da/_suite/docs/`（含 `.headers.txt` 与 `.md.txt` 提取件）。
- **无法取得的留痕**：3 份被覆盖的页面 DSL 文本（a11-i8，不可逆）；服务端 `server-timing` 头（不可取得，记 null）。
- 未保存任何凭据；请求头不含密钥。
- 总任务根 `.gitignore` 已创建，仅忽略 `__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/`、
  `.mypy_cache/`、`.ruff_cache/` 等运行时缓存；`tmp/`、`outputs/` 与实际过程证据**未被忽略**。
  运行时缓存不列为产物或自检证据。

### 结束依据

两页最终图逐字节等于最后一次渲染的服务响应（无后处理），10 次逐区查看事件带裁切框与检查内容，
14 项需求检查全部通过（含金额 33 项独立断言复算），已知问题 13 项全部处置（8 修 / 1 绕过 /
1 已接受取舍 / 1 不可逆披露 / 1 实测为非缺陷 / 1 记录更正）。据此标记 A11 为 `completed`。
