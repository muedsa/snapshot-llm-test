# snapshot-usage · B03 用十件作品探索 DSL 的创意边界

- **完成状态**：completed（10 件独立作品 + 根目录五份文件 + 每件 `case.md`）
- **run_id**：`20261004-182918`
- **输出目录**：`D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\outputs\20261004-182918\B03\`
- **临时目录**：`D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\B03\`
- **服务**：`POST https://open-snapshot.muedsa.com/snapshot`，请求体是 UTF-8 纯文本 DSL，
  响应体是图片字节；`snapkit` 每次都带浏览器 User-Agent（否则 Cloudflare 403 1010）。
  十个 `final.png` **全部是服务响应的原始字节**，没有任何后处理、没有二次绘制、
  没有把整图预渲染后当 `<Image>` 塞回去（十件的 `final.snapshot` 里 `<Image>`
  标签数**逐件为 0**；case-06 里出现的 2 处是 `<ImageFiltered>` 这个滤镜标签，
  不是图片标签）。
- **外部素材**：零。资产政策为纯 DSL 构造。

---

## 1. 实际使用的文档与字体（真实抓取，非引用）

本题自己抓了 **16 个文档接口 + 1 个字体列表**，全部落盘在
`tmp/20261004-182918/B03/docs/`，逐条记在 `requests.jsonl`（`B03-req-001` … `017`）：

| request_id | 类型 | URL | 落盘文件 | 实际用在哪 |
|---|---|---|---|---|
| B03-req-001 | document | `open-snapshot.muedsa.com/ai-guide.md` | `docs/ai-guide.md` | 服务用法、请求体格式、UA 要求 |
| B03-req-002 | document | `…/openapi.yaml` | `docs/openapi.yaml` | `/snapshot` 与 `/fonts` 的响应约定 |
| B03-req-003 | document | `snapshot.muedsa.com/` | `docs/index.html` | 文档导航结构 |
| B03-req-004/005 | document | `…/sitemap-index.xml`、`…/sitemap-0.xml` | 同名 | 找出下面 12 个页面，没有靠猜 URL |
| B03-req-006 | document | `guides_concepts` | `docs/guides_concepts.html` | Widget/属性/枚举的总体模型 |
| B03-req-007 | document | `guides_layout` | `docs/guides_layout.html` | `Row/Column/Stack/Positioned/Expanded/Flexible/Spacer/AspectRatio/FractionallySizedBox` |
| B03-req-008 | document | `guides_media-text` | `docs/guides_media-text.html` | `Text` 全部属性、span、`WidgetSpan`、`Raw`、CDATA |
| B03-req-009 | document | `guides_painting` | `docs/guides_painting.html` | `boxShadow` / `gradient*` / `blendMode` / `shape` |
| B03-req-010 | document | `guides_parser` | `docs/guides_parser.html` | 解析器模型、复用与并发注意事项 |
| B03-req-011 | document | `guides_rendering` | `docs/guides_rendering.html` | 渲染管线、`Server-Timing`、尺寸来源 |
| B03-req-012 | document | `guides_widgets` | `docs/guides_widgets.html` | 官方 Widget 列表（`ClipPath` 在这里，`ClipRect/ClipOval/ClipRRect` 也在） |
| B03-req-013 | document | `reference_enums` | `docs/reference_enums.html` | 枚举取值总表（多处**与实际不符**，见第 3 节） |
| B03-req-014 | document | `reference_faq` | `docs/reference_faq.html` | 已知限制 |
| B03-req-015 | document | `reference_parser-errors` | `docs/reference_parser-errors.html` | 错误码含义，用来对照实际 400 响应 |
| B03-req-016 | document | `reference_parser-tags` | `docs/reference_parser-tags.html` | **属性权威表**，十件的属性取舍都以它为准 |
| B03-req-017 | font_list | `…/fonts` | `fonts-list.txt` | 字体白名单 |

字体只用 `GET /fonts` 真实返回的 26 个，**没有臆造字体名**：

```
Inter, Inter Black, Inter Extra Bold, Inter Extra Light, Inter Light,
Inter Medium, Inter Semi Bold, Inter Thin,
Noto Sans CJK JP/KR/SC/TC/HK, Noto Sans Mono CJK JP/KR/SC/TC/HK,
Noto Serif CJK JP/KR/SC/TC/HK, DejaVu Sans, DejaVu Sans Mono, DejaVu Serif,
Noto Color Emoji
```

十件实际用到 6 个：`Inter`（case-07/09 的西文大数字）、`Inter,Noto Sans CJK SC`
（中西混排主力）、`Noto Sans CJK SC`（纯中文）、`Noto Serif CJK SC`（case-02 头像「林」字）、
`DejaVu Sans Mono`（所有等宽读数/时间戳/标签）、`Noto Sans Mono CJK SC`（case-01 的中文 mono kicker）。
中文 mono 用 `Noto Sans Mono CJK SC` 是因为 `DejaVu Sans Mono` 没有汉字。

---

## 2. 实际用到的标签与属性（按件，`final.snapshot` 里真实出现的）

| 类别 | 标签 | 属性（只列实际出现过的） |
|---|---|---|
| 根与布局 | `Snapshot` `Container` `Stack` `Positioned` | `type` `background` `width` `height` `color` `fit`(EXPAND/LOOSE/PASSTHROUGH) `alignment` `clipBehavior`(NONE/HARD_EDGE) `left` `top` `shape`(RECTANGLE/CIRCLE) |
| 流式 | `Row` `Column` `Padding` `Align` `SizedBox` `Center` | `mainAxisAlignment`(START/CENTER/END/SPACE_BETWEEN/SPACE_AROUND/SPACE_EVENLY) `mainAxisSize`(MIN/MAX) `crossAxisAlignment`(START/CENTER/END/STRETCH) `padding` `widthFactor` `heightFactor` |
| 自适应 | `Expanded` `Flexible` `Spacer` `FractionallySizedBox` `AspectRatio` `IndexedStack` | `flex` `fit`(LOOSE/TIGHT) `widthFactor` `heightFactor` `alignment` `index` |
| 裁剪 | `ClipRect` `ClipOval` `ClipRRect` | `clipBehavior`(NONE/HARD_EDGE/ANTIALIAS/SAVE_LAYER/ANTI_ALIAS_WITH_SAVE_LAYER) `borderRadius` |
| 变换 | `Transform` | `matrix`(16 个浮点，列主序) `origin` `alignment` |
| 滤镜 | `ImageFiltered` `BackdropFilter` `ColorFiltered` | `sigmaX` `sigmaY` `color` `blendMode`(MULTIPLY/SCREEN/OVERLAY/DARKEN/LIGHTEN/PLUS/DIFFERENCE/EXCLUSION/HUE/SATURATION/COLOR/LUMINOSITY) |
| 透明 | `Opacity` | `opacity`(0–1，子树相乘) |
| 装饰 | `Container` 自绘 | `borderRadius` / `borderRadiusTopLeft|TopRight|BottomLeft|BottomRight` / `border` / `borderTop|Left|Right|Bottom` / `boxShadow`(ELEVATION_n 与 `"x y blur spread #RRGGBBAA"` 多段、`blurStyle` OUTER/INNER/SOLID) / `gradientType`(LINEAR/RADIAL/SWEEP) / `gradientColors` / `gradientStops` / `gradientBegin|End` / `gradientCenter|Radius|Focal|FocalRadius` / `gradientStartAngle|EndAngle|Rotation` / `gradientTileMode`(CLAMP/REPEAT/MIRROR/DECAL) / `backgroundBlendMode` |
| 文字 | `Text` `Raw` `WidgetSpan` | `text` `color` `fontSize` `fontFamily` `fontStyle` `fontFeatures`(ss01/ss02) `letterSpacing` `textAlign`(START/CENTER/END) `maxLines` `overflow`(ELLIPSIS) `decoration`(SOLID/DOTTED/DOUBLE/WAVY) `decorationColor|Style|Thickness|Gaps` `foregroundMode`(STROKE) `foregroundPaint|StrokeWidth|StrokeJoin|StrokeCap` `textShadow` `strutEnabled` `strutFontSize` `strutHeight` `strutHeightForced`（后四个实测中性） `CDATA` |

**没有用、也不假装用的**：`ClipPath`（400 `Unknown element tag`）、`Path`/`CustomPaint`/任何
路径图元、`Image`、`Opacity` 直接写在 `Container` 上（属性不存在）、`Text height`
（见第 3 节，会让整段空白）。

---

## 3. 本题踩到的 DSL 语义坑（全部有真实响应或探针图支撑）

按「反直觉程度」排序。**每一条都是本服务当前版本上的实测结论，不是从文档推的。**

| # | 现象 | 实测依据 | 处置 |
|---|---|---|---|
| 1 | **`Text` 的 `height` 属性是毒属性**：HTTP 200，但整段文字一个字都不画 | 探针 `probe-c09e-lineheight.png` 14 格逐项隔离（`height` = 18/26/40/60/100 全空） | 行高只能靠盒高 + 多个独立 `Text` 手工排；这条写进了 case-09 的作品里 |
| 2 | **`strutLeading` 同样致命**，`strutLeading="0"` 反而正常 | 同上探针后 7 格 | 只用「什么都不做」；`strutHeightForced` / `strutFontSize` / `strutEnabled` 实测中性 |
| 3 | **未知属性被静默忽略**：`font-size="44"`、`fontFeatures="zzzz"` 都不报错也不生效 | 探针对照图 | 所有属性都先在探针上验证再用 |
| 4 | **`Stack fit="EXPAND"` 会把非定位子节点拉满并忽略它的 `width/height`** | `probe-c09f-stackfit.png`；case-09 探针曾因此整张变白纸 | 全库约定：矩形一律 `Positioned > Container` |
| 5 | **`Shape` 只有 `RECTANGLE`/`CIRCLE`**，`shape="OVAL"` → 400；且 `shape` **不裁剪子节点** | `probe-p05` 系列；276×138 圆角容器装 460×300 红块照样溢出 | 裁剪只能用 `Clip*` |
| 6 | **`Opacity` 只能是包裹标签**，写在 `Container` 上不存在；取值必须 0–1（`1.5` → 400） | `probe-c08-opacity.png`；5 次 400 响应 | 用 `<Opacity opacity=…>` 包子树，嵌套相乘 |
| 7 | **8 位 hex 按 CSS 读 `#RRGGBBAA`**，写错位数（9 位 `#9CA3AFF`）→ 400 | case-09 v1；多次 400 | 8 位一律 `#RRGGBBAA` |
| 8 | **`gradientTileMode` 的重复必须靠「缩短向量」人为制造**：默认 `gradientBegin/End` 铺满盒子时，REPEAT/MIRROR/DECAL 与 CLAMP 完全一样 | `probe-p01b-tilemode.png` | 条纹底故意把向量缩到 `period/box` |
| 9 | **`gradientBegin/End` 不接受 `BOTTOM` 这类词**，只接受 `"(x,y)"` 或对齐常量 | 1 次 400 | 全用 `"(0.5,0)"` 形式 |
| 10 | **枚举文档不可信**：`PaintStrokeCap` 没有 `BEVEL`（`PaintStrokeJoin` 有）；`decorationLineStyle` 没有 `DASHED`；`blendMode` 没有 `ADD`；`clipBehavior` 没有 `SAVE_LAYER`（真名 `ANTI_ALIAS_WITH_SAVE_LAYER`）；`BorderStyle` 没有 `DASHED/DOTTED`；`textHeightMode` 与 `fontEdging` 的**任何**取值都是 400 | 30+ 次单值枚举探测，每次一个独立请求 | 全部靠逐值试出来；试不通的写进作品当边界 |
| 11 | **`ClipOval` / `ClipRect` 只允许一个子节点** | case-02 v1、case-01 探针的 400 | `Clip* > Stack(EXPAND) > [子节点…]` |
| 12 | **`Positioned` 只能是 `Stack`/`IndexedStack` 的直接子节点**，且内部只能有一个子节点 | `renderBox.parentData must be StackParentData`（6 次）、`Tag Positioned only can have one child` | 严格包在 `Stack` 里 |
| 13 | **元素数上限 4096**，超了是 `RENDER_ERROR: Document contains more than 4096 elements`（HTTP 400） | case-06/case-10 实测撞到 | 全年 8760 小时热力图因此没做，写进 case-10 的遗留 |
| 14 | **`FractionallySizedBox` 直接作 `Row` 子节点 → 400 `widthFactor needs a finite maximum size`**（Row 给非 flex 子节点无界宽） | case-10 v3 | 先包 `Flexible(flex=1, fit="LOOSE")` |
| 15 | **`AspectRatio` 是「先宽度、放不下才回退高度」的 fit-inside**：父盒 300×180 里 `ar=1` 得 180×180 | `probe-c10-flex.png` + `probe-c10-readback.txt` 像素读回 | 按盒高预算 |
| 16 | **`crossAxisAlignment="STRETCH"` 不会给「无宽高的 Container」补尺寸** | 同上探针第 ④ 行 | 需要尺寸就自己写 `width/height` |
| 17 | **`IndexedStack` 的 `index` 只决定画哪一页，子节点全部参与布局** | 探针第 ⑧ 行 | 静态交付里等于单页，已在作品上写明 |
| 18 | **`minWidth must be between 0 and maxWidth` / `minHeight must be between 0 and maxHeight`**：Flex 里算出负的份额就 400 | case-04 v2、case-10 v1（`degrees()` 漏写导致月柱高为负）两处 | 算完先夹取再进 DSL |
| 19 | **`ImageFiltered` 糊整棵子树**，文字会跟着糊；`BackdropFilter` 只能读「同一个绘制层里已经画过的像素」，所以必须作为**兄弟节点**盖在后面 | `probe-c06-blur.png` / `probe-p03b-backdrop.png` | case-06 用「背景进 ImageFiltered → 再盖 BackdropFilter → 文字另画」 |
| 20 | **`boxShadow` 的 `ELEVATION_*` 不能与自定义阴影混写**；`boxShadow` 里的颜色不接受裸 `#38BDF8AA` 之外的写法 | 2 次 400 | 要精确控制就全用自定义四元组 |
| 21 | **`Clip*` 会吃掉子节点的 `boxShadow`，`Stack` 自己的 `clipBehavior` 不会** | case-05 / case-10 对照 | 用 `ClipRect` 做视口把投影裁掉 |
| 22 | **`Transform` 只有 paint-only 的 4×4 矩阵，没有 `rotate` 属性**；`m[2][3]` 透视项表现偏**切变**而非梯形收缩 | `probe-p02-transform.png` 12 格；case-04 v3 把 0.0021 降到 0.0004 才不出血 | 真透视由 Python 侧针孔投影提供，矩阵只做最后修饰 |
| 23 | **`Transform` 不写 `alignment` 时绕子节点左上角旋转** | 探针「origin=(60,0) · alignment=CENTER」 | 需要绕中心就显式写 `alignment` |
| 24 | **8 位 `letterSpacing`/`fontFeatures` 只在 Inter 上对 `ss01/ss02` 生效，`tnum`（等宽数字）无效** | `probe-c09a-fontfeat.png` | case-09 的数字表明确没有做等宽对齐，写进遗留 |
| 25 | **`softWrap=false` 未生效**（长句仍折行） | case-09 探针 | 只能靠 `maxLines` + `overflow="ELLIPSIS"` |
| 26 | **`padding` 只接受 EdgeInsets 写法**（`"12"`、`"(8,16)"`、`"(8,12,16,20)"`），`"24 32"` → 400 | 手册 + 本库早前实测 | 全用两段式/四段式 |
| 27 | **`Container` 也只允许一个子节点** | 2 次 400 | 多子节点一律 `Stack`/`Column` |
| 28 | **`Raw` 会吞掉前导空白**：缩进要靠 CDATA 或 `&#10;` 保留 | `probe-c09g-rawspace.png` | case-09 的代码块用 CDATA |
| 29 | **`INTERNAL_ERROR: Snapshot rendering failed`**（HTTP 400）在大图 + 多滤镜时出现过 8 次（req-050/051/063/082/086/087/089/157），同一份 DSL 重发即成功 | 8 条 400 响应原文 | 记为服务侧瞬时故障，**不**当作内容错误；重试后成功，未改 DSL |

**关于 `Server-Timing`**：264 次成功响应都带 `render;dur=…, total;dur=…`，
**没有任何一次出现 queue 段**，所以排队等待时间记 `null` 而不是 0。

---

## 4. 请求与渲染计数（全部由 `requests.jsonl` 实测汇总，脚本 `review_counts.py`）

| 指标 | 实测值 |
|---|---|
| 记录到的请求总数 | **379** |
| 渲染 `POST /snapshot` | **362**（成功 264 / 失败 98 / 自动重试 0） |
| 文档接口 | 16 |
| 字体列表 | 1 |
| 第一个请求 | `2026-10-05T05:14:56.342+08:00`（抓 `ai-guide.md`） |
| 第一张可用图 | `2026-10-05T05:20:27.882+08:00`（`probe-p01-gradient.png`） |
| 最后一个请求 | `2026-10-05T14:59:54.285+08:00`（case-09 的收尾复审重渲染） |
| 请求耗时合计 | **655.3 s**（服务端+网络，不含本地设计与写稿时间） |
| 收到 `Retry-After` 的次数 | 0（没有出现 429/503） |
| 写入 `outputs/<run>/B03/<case>/final.png` 的成功渲染次数 | case-01 **9**、case-02 **5**、case-03 **3**、case-04 **4**、case-05 **3**、case-06 **5**、case-07 **8**、case-08 **2**、case-09 **6**、case-10 **6**，合计 **51** |
| 其余成功渲染 | 全部是探针/预览，落在 `tmp/…/B03/probes/` 与 `tmp/…/B03/preview/`（共 213） |

98 次失败里，**绝大多数是我故意做的能力探测**（枚举取值、`opacity=1.5`、
`ClipPath`、`4096 元素` 等），它们的响应原文全部保留在
`tmp/20261004-182918/B03/responses/`，对应 DSL 保留在 `tmp/…/B03/probes/`。
按错误类型归类见第 3 节的表格。

### 4.1 迭代与看图（`tmp/20261004-182918/B03/iterations.jsonl`）

中断的运行**没有留下** `iterations.jsonl`，所以收尾阶段按可核验的证据重建：

| 指标 | 实测值 |
|---|---|
| 迭代记录行数 | **63**（51 行有图 + 12 行 syntax-fix，即没有产出图片的失败请求） |
| 有 `viewed_at` 的行（= 看图次数） | **51** |
| 完整视觉迭代（`complete_visual_iteration=true`） | **14** |
| 基线行 | 10（每件第一版） |
| 严格 1:1 对齐的用例 | case-03 / case-04 / case-05 / case-08（成功渲染数与记录的视觉阶段数正好相等） |
| 每件的最后一版 | 计为完整视觉迭代（case-01/02/09 的这一版是本次复审亲手改+重渲染+复验的） |

**为什么只有 14 条完整视觉迭代，而不是 51 条**：早前运行按「版本系列」记录诊断
（例如 case-01 的 v1…v5 一共只写了 5 条，而 `requests.jsonl` 里 case-01 成功渲染了
9 次），并且 `probe_lib.draft()` 的版本号**每个进程从 v001 重新开始**，
同名 DSL 副本被后续进程覆盖（`drafts/` 里 case-01 只剩 2 个不重名的副本）。
因此中间各版「哪一次渲染对应哪一条诊断」无法从留下的证据里还原，
我不把它硬套上去；这些中间版在日志里如实写成「第 N 版渲染完成并打开查看，
本件的诊断序列见 case.md」。`task-metrics.json` 的 `case_alignment` 字段
逐件列出了成功渲染数、记录阶段数与是否严格对齐，可以自己核对。

`viewed_at` 用的是该版 PNG 的**渲染响应完成时间**（`requests.jsonl` 的 `ended_at`）：
看图动作紧随其后但当时没有单独打点，所以用完成时间代替，这一点写在
`snapshot-usage.md`（本文件）里而不是藏在日志里。

**一处必须说明的返工**：第一次生成 `iterations.jsonl` 时把 case.md 的编号条目
直接按顺序对到渲染序列上，导致「400 失败」被写成了一条有图的迭代、
case-01 的收尾复审条目被对到了错误的版次。发现后**没有覆盖**，
先把原文件改名为 `tmp/20261004-182918/B03/iterations.superseded-01.jsonl` 保留，
再重写 `log_review.py` 按上面的规则重建。

### 4.2 其他工具（`tmp/20261004-182918/B03/tool-usage.jsonl`）

**56 行**：前 32 行来自被中断的运行（其中 #31 声明要写本文件、#32 声明要调
`wrapup`，当时都还没真正落地，属于「事先登记」）；后 24 行是本次收尾复审
**实际发生**的工具调用，按时间顺序登记，含用途、输入/输出路径与影响的用例。

### 4.3 `task-metrics.json` 里两个字段的修正

`finalize.build` 的 `final_pngs` 只扫 `outputs/<run>/<task>/` 顶层，而 B 类的最终图
在 `case-XX/` 子目录里，所以它先给了 `0`。这两个字段在 `wrapup` 之后按 case 子目录
重新统计为 **10**（`final_png_files` 列出 10 个相对路径），并在
`final_png_note` 里写明了原因。**没有改共享库 `finalize.py`**，以免影响其他题
已经写出的 `task-metrics.json`。

---

## 5. 逐件自检表

尺寸与元素数由 `build_portfolio.py` 从**交付文件本身**读回（PIL 读 PNG 尺寸、
`os.path.getsize` 读字节数、正则数 `final.snapshot` 里的标签），不是脚本里的常量。

| # | 作品 | 画幅 | PNG 字节 | DSL 字节 | elements | 服务响应 | 关键数字自洽 | 100% 下可读 | 素材 |
|---|---|---|---|---|---|---|---|---|---|
| 01 | 潮汐与风 · 澄澳灯桩值班板 | 1600×1000 | 203,045 | 122,484 | 1394 / 4096 | 200 image/png | 潮位由 6 个分潮实算：高潮 3.8439@15:00、低潮 0.3877@09:00、潮差 3.4563→3.46、NOW 09:45 = 0.6721→0.67；月相由时间戳实算 D=285.0°→37.0% 残月 | 最小 9 px（水深分级色标），其余 ≥11 px | 无 |
| 02 | 边缘语言 · 云吞巷票券与卡印刷规格稿 | 1600×1010 | 227,679 | 26,333 | 316 / 4096 | 200 image/png | A 牌 28+16+12=56 元、B 牌 32+18+12=62 元，都由 `sum()` 求出；尺寸 250 px=90 mm、340 px=85 mm、346 px 竖排 | 最小 9 px（边缘配方注记） | 无 |
| 03 | 拣选层级 · 华东三仓 E3 手持终端 | 1440×1024 | 190,305 | 28,092 | 341 / 4096 | 200 image/png | 影子 ELEVATION_1/4/8 = 嵌套层数 1/2/3；触控目标 ≥76 px；候选位第 3 行被 `ClipRect` 视口裁掉（设计如此） | 最小 10 px | 无 |
| 04 | 舞台透视 · 《夜航》选座预览 | 1500×1100 | 228,706 | 51,034 | 646 / 4096 | 200 image/png | 26 座/排（8+10+8）×10 排；A3+B4+C3；主视角与 4 张缩略图共用同一 `plan(w,h)`，矩阵标注 `rot −3.0° ∘ m[2][3]=0.0004` 与代码一致 | 最小 10 px（排标签） | 无 |
| 05 | 三种取景 · 屿东 07 海洋浮标观测卡 | 1600×1060 | 226,026 | 241,718 | 3402 / 4096（83%） | 200 image/png | 三视图调用同一个 `energy(f,t)`；`Tp=1/0.135=7.4 s` 与表内 7.4 s 一致 | 最小 9 px（clipBehavior 图注） | 无 |
| 06 | 起降简报 · 临川 LKC 起飞天气 | 1400×1000 | 272,093 | 36,383 | 494 / 4096 | 200 image/png | METAR/TAF 八行与下方摘要表逐项一致（240°/08、6000 m、1500 ft BKN012、18/14 °C、1014 hPa） | 报文行 18 px mono | 无 |
| 07 | 叠印配方单 · 四色 | 1600×1120 | 186,352 | 52,660 | 714 / 4096 | 200 image/png | 12 个交点标签是从**渲染后的 PNG 上采样读回**的实际像素；C×M 与 M×C 渲染相同（#006083 / #000083 分别采样） | 最小 9 px | 无 |
| 08 | 淹没深度分级 · 青屿河断面 K12+400 | 1500×1050 | 177,745 | 39,711 | 507 / 4096 | 200 image/png | 120 根柱 ×16.7 m ≈ 2000 m；最大水深 5.42 m、淹没河宽 1333 m、平均 4142/1333 = 3.11 m ≤ 5.42 m；图例 8 个 hex 与分级带同源 | 最小 10 px | 无 |
| 09 | 版本说明 · anvilplot 3.14.0 发行单页 | 1500×1090 | 378,633 | 34,272 | 372 / 4096 | 200 image/png | 摘要的 2/2/3/5 由 `CHANGES` 实算并 `assert` 合计 = 12 = 表头的 `12 ENTRIES`；矩阵 4×5 单元格齐全 | 最小 10 px | 无 |
| 10 | 日照剖面研究墙 · 青屿书院实验楼 | 1600×1150 | 272,563 | 89,575 | 1183 / 4096 | 200 image/png | Cooper 赤纬 + 标准时角：12 个月昼长 9.9668–14.0332 h，年较差 4.0664→4.07；冬至正午 α=35.3° 与天轨最低点、逐时表 12:00 行三处一致；剖面 1 px = 0.0588 m | 最小 9.5 px | 无 |

十件画幅互不重复；底色基调九种（case-02 与 case-07 同为暖白但配色系统完全不同）。

---

## 6. 问题与修复表

### 6.1 制作期（各件自己的迭代，详见对应 `case.md` / `technique-notes.md`）

| 现象 | 定位方式 | 修复方式 | 复验结果 |
|---|---|---|---|
| case-01 v1 每个面板内容整体偏移面板原点 | 对照 `probe-07/08` | 是脚本 bug（把画布绝对坐标当面板局部坐标），不是服务问题；改用 `wlib.Frame` 局部坐标 | v2 几何正确 |
| case-01 v3 五处排版问题（kicker 压 chip、说明压读数行、轴末「时」打架、面板底部溢出、波高幅度太小） | 看图 | 逐条改坐标与行距 | v4/v5 通过 |
| case-01 v4 状态 chip 文字被裁 | `dsllib.est_width` 报警 | `est_width` 用 0.55em 估拉丁，`DejaVu Sans Mono` 实际 0.605em → 给 `wlib.chip` 加 `mono=True` 走真实 advance | 复看通过 |
| case-02 v1 `ClipOval` 里并列两个子节点 → 400 | 响应原文 | 改 `ClipOval > Stack(EXPAND) > [Container, Text]` | 通过 |
| case-02 v1 `borderLeft="14 SOLID"` 少颜色 → 400 `Failed requirement` | 响应原文 | 补 `#RRGGBBAA` | 通过 |
| case-02 v3 `Stack fit="LOOSE"` 让所有子节点按 alignment 重叠 | 看图 | 改 `Column crossAxisAlignment="STRETCH"`（正解，不是打补丁） | v3 通过 |
| case-02 v4 尺寸表被外层 `Stack` HARD_EDGE 裁掉 | 看图 | 调整稿面/画布高度 | v4 通过 |
| case-03 v1–v2 候选货位第 3 行露出半截投影 | 看图 + `crops/final-c03-skucard.png` | 加 `ClipRect` 视口把行与投影一起裁 | 通过 |
| case-04 v1 `m[2][3]=0.0021` 把整图甩到左上并出血；缩略图排缩成一列小点 | 看图 | 透视降到 0.0004、旋转 −4.5°→−3.0°；`margin` 改自适应 `min(120, w·0.30)`，同时修掉 `minWidth must be between 0 and maxWidth` | v3/v4 无出血 |
| case-04 v2 行标签互相压 | 看图 | `y += rh + gap` 漏了 `label_h`，补上 | 通过 |
| case-04 v3 「确认选座」按钮被面板裁掉 | 看图 | 上移并压缩 46→44 px | 通过 |
| case-05 v1 `ClipPath` → 400 `Unknown element tag` | 响应原文 | 承认没有路径裁剪，改用 `ClipOval/ClipRRect` 嵌套，并把这条写进作品 | 通过 |
| case-05 v2/v3 三视图热图数值对不上 / 圆形镜头网格不满 | 看图 + 核对 `energy()` | 三视图统一调用同一函数；圆盘内网格画得比圆大再裁 | 通过 |
| case-06 v2 文字被 `ImageFiltered` 一起糊掉 | 看图（探针 D/E/F 对照） | 改成「背景进 `ImageFiltered` → 再盖 `BackdropFilter` → 文字另画」 | v4 笔画边缘无光晕 |
| case-06 v3 大图撞 4096 元素上限 | 400 `Document contains more than 4096 elements` | 降到 494 元素（改用「回波只画必要档位」） | 通过；全年热力图因此没做，写进 case-10 遗留 |
| case-07 v1 `ColorFiltered` 少 `color` → 400 `Attr [color] must not be null` | 响应原文 | 补色（语义：只给 `blendMode` 不给 `color` 是非法的） | 通过 |
| case-07 v2 `blendMode="ADD"` → 400 | 枚举探测（4 次） | 改用实测存在的 12 种 | 通过 |
| case-08 v1 `Opacity opacity="1.5"` → 400（5 次） | 响应原文 | 取值夹到 0–1，并把这条画在作品上 | 通过 |
| case-09 v1 9 位 hex `#9CA3AFF` → 400 | 响应原文 | 改 8 位 `#RRGGBBAA` | 通过 |
| case-09 v2 矩阵末列越出画布；变更清单第 12 条被摘要带盖住 | 看图 | 矩阵改 138 px 标签列 + 5×52.4 px 数据列；变更行距 56→50 | v2 通过 |
| case-09 v3 代码块被截（按 1.2em 估行高，实际 DejaVu Sans Mono 段落行距约 1.55em） | 看图 | 每段盒子 72→80 px；类型标注去掉空行、盒子 106→114 px | 通过 |
| case-09 v4「本版数字」标题压时间轴；装饰线说明撞面板底 | 看图 | 时间轴行距 38→34、标题下移；装饰线行距 36、注释压成一行 | 通过 |
| case-09 v5 SOLID 装饰线 1.6 px 几乎看不见 | 4× 裁切 | 每行不同 `decorationThickness`（2.6/2.0/2.4/2.0） | 通过 |
| case-09 v5 `Text height` / `strutLeading` 让整段空白（HTTP 200） | `probe-c09e` 14 格隔离 | 放弃行高控制，手工分行；把这条写进作品 | 通过 |
| case-10 v1 `daylen()` 里把 `acos()` 的弧度当角度（漏 `degrees()`）→ 12 个月昼长全变 0.24 h → 柱高为负 → 400 | 400 `minHeight must be between 0 and maxHeight` | 改 `2·degrees(acos(...))/15` | v1 通过 |
| case-10 v1 `lo/hi` 设 10.4/14.2，12 月的 9.97 h 落在下界外 → 同样 400 | 同上 | 改 9.8/14.2 | 通过 |
| case-10 v3 `FractionallySizedBox` 直接作 `Row` 子节点 → 400 `widthFactor needs a finite maximum size` | 响应原文 | 每根条包一层 `Flexible(flex=1, fit="LOOSE")` | 通过 |
| case-10 v3 剖面被压成 12 px（把「米」当像素） | 看图 | 引入 `SCALE = 17 px/m`，四层 214 px，并补 `1 px = 0.0588 m` 比例注记 | 通过 |
| case-10 v3 太阳光线压穿右侧进深条标题与第一行 | 看图 | 起点贴建筑边缘、长度 130→96 px，说明文字移到地面线下方 | 通过 |
| case-10 v4 逐时表第 7 行压脚注；缩略图「冬至」标签压日轨圆点 | 看图 | 表行距 24→22、脚注拆两行；标签移到圆的上半区，日轨半径 54→46 | v4 通过 |
| case-10 v5 F1–F4 四行重复「最大 09:00 → 4.03 m」且底部脚注撞出面板 | 看图 | 每行只留 09:00 数值，「各层同值（南立面无遮挡）」集中写在下面；行距 82→80、整体上移 8 px | v5 通过 |

### 6.2 收尾复审（把十张 `final.png` 逐张重新打开之后）

这一步是新做的：**同时把十张摊在一起逐张重看**，用 `crop.py` 放大可疑区域，
用 `rotcheck.py` 把旋转文字旋正，用 `review_audit.py` 独立重算印在图上的数字。

| # | 现象 | 定位方式 | 修复方式 | 复验结果 |
|---|---|---|---|---|
| case-01 | 标签「亏凸月 · 照亮 72%」，画面却是一弯约 20% 的**右侧**蛾眉 | `crops/final-review-c01-moon.png` 3.4×；`review_audit.py` 用 Meeus 第 47 章级数算本页时间戳的真实相位 = **残月 37.0%**（左亮），三者互不相容 | `patch_review_c01.py`：删掉硬编码 `MOON_ILLUM=0.72`，改由 `D` 实算 `k`；晨昏线改用 `ClipOval` + 176 行 1 px 细条按 `R(1−2k)` 半椭圆填充，每行自带 `LINEAR` 渐变给 Lambert 明暗；页脚注明「月相按本页时间戳真实算出」 | `crops/final-review2-c01-moon.png` 3.0×：左亮、右暗、亮面约 37%、标签「残月 · 照亮 37%」「月龄 23.4 d · 由 D=285.0° 算得」。通过 |
| case-02 | B 号取餐牌印「合计 86 元」，三行是 32+18+12 = **62 元**（差 24） | `crops/final-review-c02-cardA.png` / `final-review-c02-cardB.png` 2.6× 逐行核；追源码发现 B 牌合计是写死字符串、A 牌用 `sum(items)` | `patch_review_c02.py`：给 B 牌单独 `ORDER_B` 明细并 `sum()` 求和 | `crops/final-review2-c02-total.png` 2.8×：「合计 62 元」。通过 |
| case-02 | B 牌票面写「外带 TAKEAWAY / 预计 11 分钟 · 堂食」，但这一格的标题是「B · 取餐牌（左侧色带）」、尺寸表也写「取餐牌 B」—— 一张堂食单印在取餐牌样张上 | 同上，看源码发现是更早草稿遗留的文案 | 副标题改成「取餐牌 PICKUP」，第二行改成「台号 T-07 · 预计 11 分钟」 | 同上裁切图。通过 |
| case-09 | 摘要写「没有引入新的破坏性变更，仅有两项弃用与七项修复」，紧挨着的清单里就有 **2 条 BREAKING**、**5 条 FIXED** | 对着变更清单数 chip：BREAKING 2 / DEPRECATED 2 / ADDED 3 / FIXED 5 = 12，与表头 `12 ENTRIES` 一致 | `patch_review_c09.py`：三个数字改为从 `CHANGES` 实算（`_CNT`），文案改为「12 条变更里 2 条破坏性变更、2 条弃用、3 条新增、5 条修复」，并加 `assert` 四类之和 = 12 | `crops/final-review2-c09-summary.png` 1.8×。通过 |

### 6.3 复审**排除**的三处疑似缺陷（查清后确认不是缺陷，保留原样）

| # | 初看像什么 | 查清的结果 |
|---|---|---|
| case-02 | 左侧竖排标注在 100% 下像乱码（初读成「凸 8 / m ≥ / 34」） | 写 `rotcheck.py`（`crop.py` + 旋转）把该区域旋 −90° 读回，就是正常的竖向尺寸标注「346 px」（自下而上读）。源码 `matrix="(6.12323e-17,1,0,0,-1,6.12323e-17,...)"`，盒宽 44.3 px 足够放 6 个 mono 字符，不换行。**保留** |
| case-04 | B 区 05 排左块里那条空心小格像错位/多余元素 | 查 `final.snapshot` 是**刻意**的「本排座位放大条」：外框 `border="2 SOLID #A78BFAFF"`，内含 8 个座位格 + 选中的第 8 个（24 号，黄色 `#FBBF24`），与下方「已选座位 · 平面图」同源。**保留** |
| case-10 | 楼层标高「≥9.45 / ≤6.30 / ≤3.15 / ≥0.00」像是打错（方向不一致） | `crop.py` 3.2× 放大后确认四个符号都是 **`±`**，不是 `≤/≥`；四个标高 0.00 / 3.15 / 6.30 / 9.45 与 4 层 ×3.15 m 一致。**保留** |

---

## 7. 未解决事项与如实说明

1. **`INTERNAL_ERROR: Snapshot rendering failed` 出现 8 次**（`B03-req-050/051/063/082/086/087/089/157`，
   HTTP 400，无更细信息）。同一份 DSL 重发即成功返回 PNG，所以判定为**服务端瞬时故障**，
   不是内容问题；我没有因此改动 DSL。**原因未确认**，标为推测。
2. **枚举参考页不可信**（第 3 节第 10 条）：`PaintStrokeCap`、`decorationLineStyle`、
   `blendMode`、`clipBehavior`、`BorderStyle`、`textHeightMode`、`fontEdging` 的取值表
   与本服务实际接受的集合不一致。`textHeightMode` 与 `fontEdging` 我**试遍了文档与
   Skia 命名里能想到的所有取值，全部 400**，因此判定这两个属性在本版本不可用；
   如果官方后续补上，这里需要更新。
3. **`softWrap=false` 不生效**、`fontFeatures` 的 `tnum` 不生效、`Text height` /
   `strutLeading` 会清空段落 —— 这三条都是「文档/直觉里有、实际拿不到」的能力，
   已分别写进 case-09 的作品与遗留，没有假装实现。
4. **没有位图合成、没有交互、没有动画**：服务只出静态 PNG，DSL 里也没有对应标签。
5. **精度上的近似**（逐件写在 `case.md` 的「遗留」里）：月面明暗是 Lambert 近似不是
   光度学渲染；海面剖面是三个正弦的示意叠加不是真实海浪谱；陷印只是画面示意不是
   印前文件里的扩张轮廓；`MULTIPLY` 是逐通道 sRGB 乘法不是分色叠印的专业模型；
   日照只有几何没有邻栋遮挡/反射/透光率；断面是横向断面不是沿程水面线。
6. **token / 图像用量 / 费用：全部未知，记 `null`。** 本服务没有暴露任何
   token/billing 指标接口，聊天平台也没有回报逐请求的 token 或费用，
   因此 `task-metrics.json` 里 `input_tokens` / `output_tokens` /
   `image_input_usage` / `cost` / `currency` 一律为 `null`，
   **没有按字数、请求数或字节数估算**。
7. **排队等待时间 `null`**：264 次成功响应的 `Server-Timing` 里没有一次出现 queue 段，
   所以无法测得，记 `null` 而不是 0。用户反馈等待为 0（没有向用户索取过反馈，
   视觉迭代全部由自己看图驱动）。
8. **时间口径**：`task-metrics.json` 的墙钟从本题第一个请求（05:14:56）算到
   `wrapup` 调用时刻，包含本地写稿与看图时间，因此**远大于** 655.3 s 的请求耗时合计；
   两者不是同一口径，不可互相换算。
9. **收尾复审的覆盖范围**：复审是**逐张打开十张 `final.png`** + 对可疑区域放大 +
   对印在图上的关键数字做独立重算，**不是**逐像素全量比对；
   case-07 的 12 个交点是采样式复核（已做），其余各件的数字是按公式重算复核。
10. 上面第 6.2 节的三处修复**覆盖了三张最终 PNG**。被替换掉的旧版 PNG/DSL 完整保留在
    `tmp/20261004-182918/B03/pre-final-review/`，对应的历史 DSL 也都在
    `tmp/20261004-182918/B03/drafts/`，没有清理、没有覆盖尝试记录。
11. **`drafts/` 的历史 DSL 副本不完整**：早前运行 `probe_lib.draft()` 的版本号每个
    进程从 `v001` 重新开始，同名副本被后续进程覆盖，所以 166 个草稿里只有 18 个
    不重名。`requests.jsonl` 里每次渲染都留了 `request_file` 与 `response_file`，
    但正式渲染的 `request_file` 都指向同一个会被覆盖的 `final.snapshot`，
    因此**中间各版的确切 DSL 不可恢复**。这是中断前就存在的追溯性缺口，
    本次收尾没有条件补齐，如实记录。
12. **`tool-usage.jsonl` 前 32 行里有 2 行是「事先登记」**（声明要写本文件、要调
    `wrapup`），当时并未落地；后 24 行是本次实际发生的调用。两段都保留，没有删改。
13. 本题的 `iterations.jsonl` 是**收尾阶段重建**的，不是中断前运行留下的；
    重建规则与它带来的粒度限制写在第 4.1 节。

---

## 8. 复现条件

```powershell
cd D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004
python tmp\20261004-182918\_suite\check_deliverables.py      # 交付物自检
python tmp\20261004-182918\B03\review_audit.py               # 独立重算 case-01/case-10 的关键数字
python tmp\20261004-182918\B03\review_counts.py              # 从 requests.jsonl 汇总真实计数
python tmp\20261004-182918\_suite\crop.py <png> B03 x,y,w,h <scale> <tag>   # 局部放大
```

重新生成任一件：进入 `tmp/20261004-182918/B03/`，先跑对应的
`patch_review_*.py`（幂等性不保证，只在 `.orig.py` 基线上跑过一次），再
`python -c "import build_cXX as b; b.build()"`。生成脚本只依赖
`wlib.py` / `probe_lib.py` / `dsllib.py` / `snapkit.py` 与标准库，无外部素材。
