# A21 · round-01 使用报告（原始需求）

## 完成状态

| 项 | 值 |
|---|---|
| 轮次 | round-01（TASK.md 原始需求，`rounds/round-02.md`、`round-03.md` 已可提前读到，本轮**未**使用） |
| 状态 | completed（两图均已渲染、已用 read 工具逐张打开、已按审计脚本复核） |
| 输出目录 | `outputs/20261004-182918/A21/round-01/` |
| 临时目录 | `tmp/20261004-182918/A21/` |
| 交付图片 | `launch-portrait.png` 1080×1350、`launch-wide.png` 1440×810 |
| 交付 DSL | `launch-portrait.snapshot`、`launch-wide.snapshot`（与最终 PNG 同一次请求的请求体，服务原始响应字节落盘，未做任何后处理） |
| 附加 JSON | `design-tokens.json`、`content-map.json`、`task-metrics.json` |

执行模式如实说明：本题是**预置需求连续执行**（`task.json` 里 `round_execution: preloaded_sequential`、
`blind_feedback: false`）。第一轮只依据 `TASK.md` 的原始要求制作；第二、三轮的需求文件在题目目录里
一开始就存在、可以提前读到，因此本任务**不是**隐藏反馈盲测，本报告不声称任何"意外反馈"。

## 服务、文档与字体

| 项 | 内容 |
|---|---|
| 端点 | `POST https://open-snapshot.muedsa.com/snapshot`，请求体 UTF-8 纯文本 DSL，`Content-Type: text/plain; charset=utf-8`，浏览器 UA 由 snapkit 附带 |
| 文档 | 本轮**真实抓取**：`GET /ai-guide.md`（3718 B）、`GET /openapi.yaml`、`GET https://snapshot.muedsa.com/reference/parser-tags/`（标签与属性参考），分别落在 `tmp/20261004-182918/A21/docs/`，请求号 `A21-req-001/002/004` |
| 字体 | 本轮**真实查询** `GET /fonts`（`A21-req-003`，26 个字族，落在 `tmp/20261004-182918/A21/fonts-list.txt`）。实际使用：`Inter Black`（品牌展示字）、`Inter`（西文正文）、`Noto Sans CJK SC`（中文回退）。**没有臆造字体名** |
| 复用 | DSL 语义结论同时复用了 `_suite/DSL-HANDBOOK.md`（本题库 A01–A05 的实测结论）；本轮所有布局数字都用**本轮自己渲染的探针图**重新标定 |

## 实际用到的标签与属性

`Snapshot`（`type`/`background`）、`Container`（`width`/`height`/`color`/`borderRadius`/`border`/
`boxShadow`/`gradientType`/`gradientColors`/`gradientStops`/`gradientBegin`/`gradientEnd`）、
`Stack`（`fit="EXPAND"`）、`Positioned`（`left/top/width/height`）、`Transform`（`matrix`/`origin`/
`alignment="CENTER"`）、`Text`（`text`/`fontSize`/`fontFamily`/`fontStyle`/`letterSpacing`/`color`）。

- 品牌图形 6 构件：`plate-base`、`plate-mid`、`plate-top`（三层圆角矩形，`plate-top` 用
  `LINEAR` 渐变 + `boxShadow`）、`beam`（`Transform` 旋转的圆角光带）、`spark-dot`、
  `spark-ring`（只给 `border` 的空心圆）。三层矩形、圆形、圆角、旋转光带全部是 DSL 几何，
  **没有使用 `<Image>`、没有外部图片、没有用其它绘图库画主体再嵌入**。

## 本轮踩到的 DSL 语义坑（都是实测）

1. **7 位十六进制颜色**：`#6D4AFFF` → `400 PARSE_ERROR: Attr [color] color must be #RGB, #RGBA,
   #RRGGBB or #RRGGBBAA`。
2. **拼 `radial gradientColors` 时把 8 位色再拼 `00`**：`#6D4AFF5900`（10 位）同样 PARSE_ERROR。
   透明端要写成同 RGB + `00`，即 `#6D4AFF00`。
3. **根 `Container` 下不能直接挂多个 `Positioned`**：必须 `<Container><Stack fit="EXPAND">…`，
   否则 `Tag Container only can have one child`。
4. **`Positioned` 的紧约束会撑大 `Transform` 子树里的 `Container`**（本轮最关键的一个坑）：
   `<Positioned width="388.96" height="142.54"><Transform><Container width="402.8" height="19"/>`，
   渲染出来的光带是 **389×143 的斜块**而不是 402×19 的细条——`Container` 在紧约束下被
   `enforce` 成约束尺寸。实测光带在位图上占 256 行（几何应为 142 行）。修法：`Positioned`
   的 width/height 必须等于**未旋转**的条形尺寸。
5. **`radial gradient` 的方向**：`gradientColors` 第一个色是起点。想要"中心亮、边缘化开"必须
   `实色 → 同色 00`，否则得到一枚边缘清晰的实心圆盘（第一版就是这样，见问题表）。
6. **`Inter Black` 比 `Inter BOLD` 宽**：`Layerlight` @64px 实测 330px vs 316px。第一版按
   `Inter BOLD` 的测量值排版，标题框小了 15px。教训：展示字体必须单独标定。

## 逐条自检（TASK.md 硬指标）

标定方法：每条文字都用"与最终图同构图、去掉 `Text` 层"的那张对照渲染做像素差分，差分即字形
覆盖，因此"墨迹外框是否在声明框内""是否溢出到邻区"都是量出来的，不是估计的
（脚本 `tmp/20261004-182918/A21/audit.py`，报告落在 `tmp/.../A21/audits/`）。

| TASK.md 要求 | 实测值 | 结论 |
|---|---|---|
| `launch-portrait.png` 1080×1350 | 位图尺寸 1080×1350，PNG，服务原始字节 | ✅ |
| `launch-wide.png` 1440×810 | 位图尺寸 1440×810，PNG，服务原始字节 | ✅ |
| 必须含"让复杂信息变得清晰" | 两图均含，字号 36（`p-tagline` / `w-tagline`），位于 x=112 / x=116 | ✅ |
| 必须含"2026.11.07 19:30" | 两图均含，字号 28 粗体，作为**单一文本元素**（未拆成两段） | ✅ |
| 必须含"ONLINE LAUNCH" | 两图均含，字号 24 粗体，pill 形 chip | ✅ |
| 必须含"讲者：林川 / 苏言" | 两图均含，字号 28 | ✅ |
| 必须含"layerlight.example.org" | 两图均含，字号 26 粗体 | ✅ |
| 两图同一主色 | 主色 `#6D4AFF`（chip 底、plate-top 渐变端、tick、focus 环），`design-tokens.json` 中只定义一份 | ✅ |
| 两图同一字体层级 | 两图共用同一套 type scale（display_cjk 108 / display_latin 64 / tagline 36 / info 28 / link 26 / micro 24） | ✅ |
| 可识别的 3–6 构件品牌图形 | 6 构件，44px 页眉小标与 380/360px 主标形状完全一致（同一函数、同一归一化几何） | ✅ |
| 分别构图 | 竖版＝页眉/主标/标题锁定/标语/分隔线/双行信息卡（垂直堆叠）；横版＝页眉/左文字+右主标/整宽三栏事实条（两栏式） | ✅ |
| 主标题 ≥56 | 竖版"叠光"108、"Layerlight"64；横版同 | ✅ |
| 其余 ≥24 | 全图最小字号 **24**（页眉 wordmark 与 chip 文字） | ✅ |
| 不得整图嵌入/外部图片 | 全文件 0 个 `<Image>`、0 个外链；主体 100% 为 DSL 几何 | ✅ |
| 顶部/底部留真实可用扩展空间 | 竖版保留 y 0–88 与 y 1262–1350；横版 y 0–72 与 y 738–810。两条带内**逐像素**统计：非背景像素 = 0（连光晕都没进去） | ✅ |
| 不写待添加文字 | 保留带内没有任何文本元素（`content-map.json` 的 `reserved_extension_bands` 与 `reserved_band_note` 记录用途与留白原因） | ✅ |
| `design-tokens.json`、`content-map.json` | 两份都在 `round-01/`，含颜色/字阶/标记几何/栅格/保留带，以及逐元素坐标与"必含文案→落位元素"映射 | ✅ |

补充自检：

- 墨迹审计：竖版 8 个文本元素、横版 8 个，**0 处越界、0 处溢出**（`audits/*-ink.json`）。
- 对比度（作为质量参考，非本轮硬指标）：最差 5.15:1（白字 / `#6D4AFF` chip），其余 11–17:1。
- 服务错误：3 次（见下表），全部 `400 PARSE_ERROR`，无 429/503，无重试。

## 问题与修复

| # | 现象 | 定位方式 | 修复 | 复验 |
|---|---|---|---|---|
| 1 | `400 PARSE_ERROR color must be #RGB…` | 读 `tmp/.../responses/resp-A21-req-005-*.txt` | `#6D4AFFF` → `#6D4AFFFF` | 重渲染 200 |
| 2 | 首版竖版出不来：`Tag Container only can have one child` | 同上（req-008） | 根 `Container` 与所有 `Positioned` 之间补 `<Stack fit="EXPAND">` | 重渲染 200 |
| 3 | 圆形光晕是硬边圆盘 | 看图 | `radial gradientColors` 由"透明→实色"反成"实色→透明"，尺寸 ×1.55→×1.72 | 看图：柔和光晕 |
| 4 | 光带盖住整个品牌图形，像一块薄荷色板砖 | 看图 + 读 DSL（DSL 里写的是 402.8×19，明显不符） | 见坑 4：`Positioned` 改用未旋转条形尺寸 | 位图实测光带 256 行 → 几何 142 行；看图确认是细光带 |
| 5 | 页眉 44px 小标糊成一坨 | 1.6× 裁切放大（`crops/launch-portrait-r01-header.png`） | 同坑 4，厚度 0.115→0.05、光点内移缩小 | 裁切复看：三层板+光带+光点可辨 |
| 6 | 横版底部三分之一空荡 | 看图 | 改为"页眉 / 左文字+右主标 / 整宽三栏事实条"构图 | 看图：横幅被压满 |
| 7 | 第一版标题框偏窄 15px | 墨迹审计 `ink_w_delta=15` | `Inter Black` 单独探针标定（`probe-display.json`），度量表加字体维度 | 复跑审计 delta 全部 ≤3px |
| 8 | 对比度审计把 chip/卡片描边误判成"文字溢出" | 审计自身报错 | 审计改为与"去 Text 层"对照渲染做差分 | 差分后 chip 与卡片不再误报，真溢出仍能抓到（见 round-02 的 `p-card` 用例） |

## 实际渲染与看图统计

- 本轮归属的渲染请求 22 次（成功 20、失败 2，均为本报告问题表里的 `400 PARSE_ERROR`）；
  其中多次是"去 `Text` 层对照图"（不作为交付物）。另有 4 次度量探针渲染与 4 次文档/字体 GET
  记为 shared，只在任务根 `task-metrics.json` 里统计，不重复计入本轮。
- 看图（read 工具真的打开图片）：探针 2 张 + 竖版 3 轮 + 横版 3 轮 + 3 张 1.6× 局部裁切。
- 完整视觉迭代 3 次（`A21-r01-v04/v05/v06`，见 `iterations.jsonl`）。
- 每轮 DSL 版本快照存于 `tmp/20261004-182918/A21/drafts/r01-*.snapshot`。
- 注意：本报告初稿写作时统计的是"整题"请求数；修正审计脚本后又对 round-01 重渲了两次
  （DSL 未变，输出字节一致），上表已按最终归属重新统计。

## 未解决事项与如实说明

- 未遇到阻塞性错误；三次 `400 PARSE_ERROR` 均已修复并复验。
- `token`、`cost`、`image_input_usage` 等计量：**平台未提供**，一律 `null`，没有按字数或
  余额估算。服务返回的 `X-Request-Id`、`Server-Timing` 已逐条记入 `requests.jsonl`。
- 排队/限流等待：未观测到 429/503，响应也没有 queue 段，因此记 `null`（而不是 0）。
- 「顶部/底部扩展空间」的用途（未来合作方 logo 条 / 票务二维码）在 `content-map.json` 里写明
  是本设计预留的空带，**没有**写入任何占位文字。
- 字体度量表里若出现 `metric_source: "estimated"` 的条目，说明该组合未单独探针标定，需靠
  墨迹审计兜底；本轮全部文本条目为 `measured`。