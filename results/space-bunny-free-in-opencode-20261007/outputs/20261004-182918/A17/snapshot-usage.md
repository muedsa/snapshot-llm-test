# A17 · 四页可实践的 DSL 入门手册 — snapshot-usage.md

## 完成状态

**已完成。** 8 张指定 PNG（4 页手册 1200×1600 + 4 个示例 400×240）全部是
`POST https://open-snapshot.muedsa.com/snapshot` 的真实响应，配套 8 份同名 `.snapshot`
与最终渲染逐字一致，另有 `sources.md`、`examples.json`、`task-metrics.json`。

- 输出目录：`outputs/20261004-182918/A17/`
- 临时目录：`tmp/20261004-182918/A17/`
- 手册不把 DSL 描述成 HTML：第 2 页讲"根尺寸来自布局"，第 3 页讲"解析器不做 HTML 实体解码"。

## 实际使用的服务文档与字体

本次**全部真实抓取**，逐条记录在 `tmp/20261004-182918/A17/requests.jsonl`
（8 个 document + 1 个 font_list，均 200）。抓取脚本 `fetch_and_errors.py`。

| 文件 | URL |
|---|---|
| `docs/ai-guide.md` | `https://open-snapshot.muedsa.com/ai-guide.md` |
| `docs/openapi.yaml` | `https://open-snapshot.muedsa.com/openapi.yaml` |
| `docs/snapshot-parser.html` | `https://snapshot.muedsa.com/guides/parser/` |
| `docs/snapshot-layout.html` | `https://snapshot.muedsa.com/guides/layout/` |
| `docs/snapshot-media-text.html` | `https://snapshot.muedsa.com/guides/media-text/` |
| `docs/snapshot-painting.html` | `https://snapshot.muedsa.com/guides/painting/` |
| `docs/snapshot-parser-tags.html` | `https://snapshot.muedsa.com/reference/parser-tags/` |
| `docs/snapshot-enums.html` | `https://snapshot.muedsa.com/reference/enums/` |
| `fonts.txt` | `https://open-snapshot.muedsa.com/fonts` |

字体：`fonts.txt` 实测返回 27 个族。手册正文用 `Inter,Noto Sans CJK SC`，
代码用 `DejaVu Sans Mono`，都在列表内，**未臆造字体名**。

`DSL-HANDBOOK.md`（套件共享的实测结论）作为起点阅读并复用；本题在此基础上
**新增了字形级 advance 实测**（此前只有粗略估算）。

## 实际用到的标签与属性

根与布局：`<Snapshot type background>` `<Container width height color borderRadius border
boxShadow>` `<Stack fit>` `<Positioned left top right bottom width height>`
`<Row>` `<Expanded flex>` `<ClipRRect borderRadius clipBehavior>`。

文本：`<Text fontSize fontFamily color textAlign>` + CDATA，`<Raw>`，嵌套 `<Text>` 行内 Span。

滤镜：`<BackdropFilter sigmaX sigmaY>`、`<ImageFiltered sigmaX sigmaY>`。

颜色：`#RRGGBB` 与 8 位 `#RRGGBBAA`；实测确认 8 位按 CSS 顺序读（`#80FF0000` 全透明）。

未使用：`<Image>`、`url=`、`dataUri=`、外部素材。`verify.py` 用正则 `<Image[\s/>]`
逐文件核过，8 份 `.snapshot` 全部为 False。

## 版式系统（四页统一）

一套参数驱动四页，保证页眉/页码/色板/字阶/代码块样式完全一致：

| 元素 | 规格 |
|---|---|
| 画布 | 1200×1600，安全边距 48（内容宽 1104） |
| 页眉 | 76×6 章节色条 + 书名（20px Bold）+ 站点（18px）+ 右对齐 `PAGE 0N / 04`（20px Mono Bold）+ kicker（18px Mono） |
| 分隔线 | 页眉下 2px `#CBD5E1` |
| 标题块 | 46×46 圆角章节色徽章 + 数字 + 44px Bold 标题 + 24px 导语 |
| 小节标题 | 4×22 章节色竖条 + 28px Bold |
| 正文 | **24px**，`Inter,Noto Sans CJK SC`，行高 38，词感知贪心换行 + 避头尾 |
| 代码块 | 深底圆角，`DejaVu Sans Mono` **20px**，行高 27，行号槽 46px，语法分色（标签/属性/值/标点/注释/CDATA），单行上限 83 字符 |
| 插图面板 | 章节标签行 44px + 插图 540×324（scale 1.35）+ 说明行 30px |
| 右栏 | 浅底圆角，非代码条目带色块标记、续行缩进；代码条目独立灰底 chip |
| 页脚 | 细分隔线 + 左资料来源 + 右 `A17 · 第 N 页 / 共 4 页` |

第 3、4 页共用同一色板，仅换章节强调色（紫 / 绿），其余完全一致。

## 本题踩到的 DSL 语义坑

### 1. `Text` 内容含双引号必须走 CDATA（会硬报错）

`text='width="400"'` 直接提交：

```
400 PARSE_ERROR: Unexpected character '"' in input state
[AFTER_ATTR_VALUE_QUOTED] at position 3243 near: ... text="" /> 
```

`hb.ctext()` 统一用 `<![CDATA[…]]>` 送所有文本，本手册再没踩过第二次。
另外属性值里的 `&` 也需要转义，本手册正文用 `&amp;` 显示。

### 2. 服务画布高度上限 4096px

字形探针第一次想一次画 486 行（486×132 = 62984px）：

```
400 RENDER_ERROR: Render height 62984 exceeds maximum 4096
```

改为分批（每批 28 行）。手册本身 1600px 无影响。

### 3. 行宽溢出静默截断：文本框宽度必须自己算准

第一版示例把 `<Text fontSize="19" fontFamily="DejaVu Sans Mono" color=… text=… />`
写在同一行（≈102 字符），而 20px mono 下代码块单行只放得下 83 字符，
四个示例的印刷行都被截掉尾巴。修复方式不是缩字号，而是**把示例的属性拆行**
（`examples.py` 加了 `MAX_COLS=83` 硬断言，`longest` 现为 70–79）。

### 4. 省略行被当成代码 token 化 → 中文按 mono 列宽重叠

`code_block` 原来用 `(行号, 文本)` 二元组，省略说明也走代码分支，
于是被按 token 逐个定位在 `0.6022em` 的列上——中文被硬塞进半角列距，
"；完整文档见" 六个字叠在一起。单独渲染同一串文字是正常的，
所以问题在调用路径不在服务。改为 `(行号, 代码或 None, 省略说明)` 三元组。

### 5. 逐字符换行会切断拉丁词

第一版换行器逐字符断行，正文出现 `Content-T / ype`、`mess / age`、`自带空 / 白保留`。
改为词感知贪心：CJK 可任意断，拉丁/数字/`-` 粘成一个 token，另加避头尾规则。

### 6. `Row` 的 `Expanded` 分配必须按实测像素画进插图

`example-02.png` 实测：两个 `Expanded` 解出 16–124 与 138–192（108px / 54px），
中间 14px 固定间隔。我第一版插图凭直觉画成 103/35，与示例不一致，
靠逐像素比对发现（`probe/art-compare.json`）。已按实测值修正。

### 7. 行内富文本里的空格会被 trim

`<Text> 与 </Text>` 渲染后与前后文字贴死，因为普通文本节点会被 trim。
改用 `<Raw><![CDATA[ 与 ]]></Raw>` —— 正好同时把"Raw 保留空白"这条结论演示出来。

### 8. 滤镜要放在 `Stack` 里，且 `Positioned` 不能直接当根

`BackdropFilter` 背后必须有已绘制内容才有效果，所以条纹底必须排在滤镜之前；
`ImageFiltered` 包住整棵子树（含底板）才符合"子树滤镜"的语义。
`Positioned` 直接当根节点会 `RENDER_ERROR: Layout size is empty`。

### 9. 未知属性被静默忽略（手册第 2 页的重点之一）

`colour="#38BDF8FF"`（应为 `color`）→ **HTTP 200，照常出图 200×80**。
这条是实测的，手册与 `sources.md` 都据此写"看起来没生效必须用对照探针图证明"。

## 逐图自检表

全部用 `read` 工具打开原图看过；细节用 `PIL` 裁切放大（`tmp/20261004-182918/A17/crops/`）
与 `probe/art-compare.png` 放大复核。

### handbook-01.png — 调用契约

| TASK.md 指标 | 实际值 | 结论 |
|---|---|---|
| 1200×1600 | 1200×1600 | 达标 |
| 服务真实响应 | HTTP 200，373045 字节，PNG 签名正确 | 达标 |
| 同名 `.snapshot` | 36996 字节，与 POST 的 DSL 逐字一致 | 达标 |
| 正文 ≥24 | 24px | 达标 |
| 代码 ≥20 | 20px mono | 达标 |
| 安全边距 48 | 48（内容 1104） | 达标 |
| 明确页码/章节 | `PAGE 01 / 04` + `CHAPTER 01 · CONTRACT` + 页脚"第 1 页 / 共 4 页" | 达标 |
| 示例节选 8–18 行 | 印 13 行（63 行中），省略第 9–37 行并标明 | 达标 |
| 插图由本页 DSL 画 | 是，`EX1_ART` 17 个图元，无 `<Image>` | 达标 |
| 无 Image 嵌入 | 正则核过 False | 达标 |
| 首轮问题已修 | 断词、标题重叠、页脚重叠、行数错误全部修复 | 达标 |

### handbook-02.png — 布局

| 指标 | 实际值 | 结论 |
|---|---|---|
| 1200×1600 | 1200×1600 | 达标 |
| 服务真实响应 | HTTP 200，342468 字节 | 达标 |
| 正文/代码/边距 | 24px / 20px / 48 | 达标 |
| 示例节选 | 印 15 行（48 行中），省略第 14–36 行 | 达标 |
| 插图几何一致 | Row 分配已按 example-02.png 实测像素改为 108/54 | 达标 |
| 右栏条目可读 | 四条各自成段，续行缩进对齐 | 达标 |
| 不描述为 HTML | 通篇讲约束协议与布局；无 HTML 字样 | 达标 |

### handbook-03.png — 文本与颜色

| 指标 | 实际值 | 结论 |
|---|---|---|
| 1200×1600 | 1200×1600 | 达标 |
| 服务真实响应 | HTTP 200，367221 字节 | 达标 |
| 正文/代码/边距 | 24px / 20px / 48 | 达标 |
| 示例节选 | 印 14 行（42 行中），省略第 11–23 行 | 达标 |
| CDATA 结论可验证 | example-03.png 首行 `if (a < b && c > d) {` 完整显示 | 达标 |
| 尾部 alpha 可验证 | 左块半透明红（实测合成 ≈ rgb(146,20,23)），右块全透明只剩描边 | 达标 |
| 插图去掉多余底板 | 已改为示例自身颜色与盒子 | 达标 |

### handbook-04.png — 滤镜与交付

| 指标 | 实际值 | 结论 |
|---|---|---|
| 1200×1600 | 1200×1600 | 达标 |
| 服务真实响应 | HTTP 200，396827 字节 | 达标 |
| 正文/代码/边距 | 24px / 20px / 48 | 达标 |
| 示例节选 | 印 15 行（91 行中），省略第 53–61 行 | 达标 |
| 插图即现象 | 左块真 `<BackdropFilter sigmaX="7">` 背景糊/文字清；右块真 `<ImageFiltered>` 连底板带文字一起糊 | 达标 |
| kicker 不折行 | 改为 `CHAPTER 04 · FILTER / SHIP`，实测 292px ≤ 300px | 达标 |

### 4 张示例

| 文件 | 像素 | 响应 | 看图结论 |
|---|---|---|---|
| `example-01.png` | 400×240 | 200，20131 字节 | 请求/响应/错误三块齐全，箭头为 `→` |
| `example-02.png` | 400×240 | 200，11662 字节 | Row 2:1 与 Stack 定位均正确；像素扫描确认分配 |
| `example-03.png` | 400×240 | 200，16221 字节 | CDATA 尖括号、Raw 空格、三色富文本、alpha 对照全部正确 |
| `example-04.png` | 400×240 | 200，28056 字节 | 左背景糊文字清、右整棵子树一起糊 |

## 印刷代码 = 独立渲染代码（可机械核验）

- 印刷的每一行由 `hb.excerpt(example_dsl, n, n)` 从**已渲染成功**的
  `example-0N.snapshot` 切出，切出时 `assert ln in file_text`。
- `hb.code_block` 只接受切出的原文，再按 token 上色（颜色不改字符内容）。
- `verify.py` 独立复核：打印范围是否越界、行数是否在 8–18 之间，
  结果 `page 1..4 → print 14/63, 15/48, 14/42, 15/91`，全部 8–18 区间内。
- 完整示例比印刷片段长（14/63、15/48、14/42、15/91），
  省略位置在页面上以 `⋯ 印刷省略 第 A–B 行（共 N 行）；完整文档见 example-0N.snapshot`
  明确标出，行号沿用原文件编号。

## 问题与修复表

| # | 现象 | 定位方式 | 修复 | 复验 |
|---|---|---|---|---|
| 1 | 正文把 `Content-Type` 拆成两行 | 打开 handbook-01 原图 | 换行器改词感知贪心 + 避头尾 | 重渲染后 `Content-Type`、`message` 均完整 |
| 2 | 插图标题与面板标题基线重叠 | 打开原图目视 | 插图标题移到插图下方独立行 | 重渲染无重叠 |
| 3 | 页脚左文字压住右侧页码 | 打开原图目视 | 左 804px、右 280px 分列并缩短 | 重渲染分离 |
| 4 | standfirst 写"49 行"，示例实际 63 行 | 打开原图比对 | 改写导语，不再写具体行数 | `examples.py` 断言确认 |
| 5 | 省略行中文叠字 | 裁切放大 + 读 DSL 源码定位到 token 分支 | 行协议改三元组，非代码行走 UI 字体 | 裁切复看，字距正常 |
| 6 | 代码单行超 83 字符被静默截断 | `hb.warnings()` 报 4 条 needs>box | 示例属性拆行 + `MAX_COLS` 断言 | warnings 清零 |
| 7 | 右栏红条目连成一片 | 打开 handbook-02 原图 | 条目级排版：续行缩进 + 仅首行画标记 | 重渲染可数出 4 条 |
| 8 | caption 折行掉到面板外 | `check_fit` 报警 | 缩短措辞至 540px 内 | warnings 清零 |
| 9 | CHAPTER 04 kicker 折行压分隔线 | `check_fit` 报警 | 改为 `CHAPTER 04 · FILTER / SHIP` | warnings 清零 |
| 10 | 插图 Row 分配 103/35 与示例 108/54 不符 | 插图裁切 vs example-02.png 逐像素 | 按实测像素修正三个矩形 | art-compare 均值降至 13.43 |
| 11 | 插图给文字加了示例没有的底板 | 裁切 vs example-03.png 比对 | 去掉底板，用示例自身配色 | 均值由 37.66 降至 28.3，页眉框一致 |
| 12 | 探针 mono advance 量成 0.038 em | 与 100px/字形的预期矛盾 | 行被画布截断，改为 single+repeat 配对并按实测反算重复数 | 30 字符全为 0.60000，极差 0.00000 |
| 13 | 空格对比得负值 -0.056 em | 同上，40 字形 > 2360px 文本框 | 重复数降到 8，行宽 1088px | Inter 0.28 / mono 0.60 |
| 14 | `&` 在正文渲染成空白 | 打开 handbook-03 原图 | 改写为 `&amp;` | 正常显示 |
| 15 | 示例富文本 `与` 贴住前后 | 打开 example-03 原图 | 改用 `<Raw>` 承载空格 | 间距正常 |

## 排版度量（全部实测，非估算）

| 量 | 实测值 | 来源 |
|---|---|---|
| DejaVu Sans Mono advance | 30 个字符全部 0.60000 em，极差 0.00000 | `probe/metrics.json` |
| → 代码块列距 | `20 × 0.6022 = 12.04 px/字符`，单行上限 83 | 计算自上一行 |
| Inter 空格 advance | 0.28 em | `probe/metrics.json`（`AA` vs `A A` 行宽差） |
| CJK advance | 359 个汉字全部 1.000 em | `probe/glyphs.json` |
| Inter 拉丁逐字 advance | `A`=0.68 `M`=0.89 `i`=0.24 `0`=0.63 等 | `probe/glyphs.json` |
| 服务画布高度上限 | 4096px（62984px 被拒） | `probe/glyphs.py` 首次运行 |

## 未解决事项与如实说明

1. **413 / 429 / 503 未实测**：本题没有构造超限请求体，也没有触发限流。
   手册与 `sources.md` 只把它们作为 `openapi.yaml` 的枚举事实陈述，
   并明确标注"没有声称本次实测"。
2. **行内富文本那一行的字形 x 有几像素差异**：插图里"限制条件：Stack 与 Positioned"
   由页面以三个独立 `Text` 逐段定位，而示例是服务自己的内联排版。
   其余所有元素逐像素对齐（`probe/art-compare.json`：page2 均值 13.43、
   87.71% 像素差 ≤12；page3 均值 28.3、87.23%）。已在 `examples.py` 注释
   与 `sources.md` 写明。
3. **`Layout size is infinite` 未复现**：本题库旧记录提到这条 message，
   但本次对 6 种无界写法实测，当前服务一律返回 `Layout size is empty`。
   手册按本次实测措辞，没有照抄旧记录；`sources.md` 第 2 节写明了这一点。
4. **token / 图像用量 / 费用**：平台没有提供任何计量端点，本聊天平台也未报告
   逐请求 token 与费用。`task-metrics.json` 中 `input_tokens`、`output_tokens`、
   `image_input_usage`、`cost`、`currency` 全部为 `null`，
   `unknown_fields_reason` 写明"没有权威计量来源，未按字符数估算"。
   限流排队时间同样无观测值，记 `null` 而非 0（全部 126 次渲染响应都没有
   报告 queue 段）。

## 文件路径

- 交付：`outputs/20261004-182918/A17/`（18 个文件，见 task-metrics.json 的 `final_png_files`）
- 临时：`tmp/20261004-182918/A17/`
  - `examples.py` 四个示例的唯一真相源（含 `MAX_COLS` 断言与插图定义）
  - `hb.py` 版式系统（度量、换行、代码块、页面骨架）
  - `build_examples.py` / `build_pages.py` 批量渲染
  - `write_docs.py` 生成 `sources.md` 与 `examples.json`
  - `verify.py` 交付一致性审计，`compare_art.py` 插图逐像素比对
  - `probe/` 全部探针图与度量 JSON，`responses/` 原始错误响应
  - `crops/` 放大核对图，`drafts/` 每版 DSL 副本