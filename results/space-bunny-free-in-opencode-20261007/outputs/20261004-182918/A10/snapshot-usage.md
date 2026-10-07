# A10 · 透明合成与滤镜语义实验板 —— 使用与自检报告

## 1. 完成状态与目录

- 状态：**completed**（六格全部渲染、逐格实际看图核对、逐项像素取样复核）
- 输出目录：`outputs/20261004-182918/A10/`
- 临时目录：`tmp/20261004-182918/A10/`
- 生成脚本：`tmp/20261004-182918/A10/build_a10.py`（两遍渲染）
- 取样/审计/复核脚本：`sample_a10.py`、`audit_a10.py`、`verify_a10.py`、`verify2_a10.py`、`probe_bounds.py`
- 过程留痕：`requests.jsonl`（22 次渲染 + 7 次文档抓取）、`iterations.jsonl`（8 条）、
  `drafts/v01.snapshot`、`drafts/v02.snapshot`、`preview/*.png`（全部历史版本）、
  `crops/*.png`（放大核对图）、`docs/*`（本次真实抓取的官方文档）

### 交付文件

| 文件 | 尺寸 / 大小 | 说明 |
|---|---|---|
| `compositing-lab.png` | 1440×1100，336 964 字节 | 服务真实响应原始字节，PNG 签名 `89 50 4E 47 0D 0A 1A 0A`，未做后处理 |
| `compositing-lab.snapshot` | 40 717 字节 / 39 449 字符，sha256 `8614be4d…` | 与最后一次请求体逐字节一致（脚本已断言 `dsl_identical_to_last_request = true`） |
| `composite-audit.json` | 26 460 字节 | ①②预期 RGB 计算与实测、③④⑤⑥视觉判断、文档引用、未解决事项 |
| `snapshot-usage.md` | 本文件 | — |
| `task-metrics.json` | — | 由 `finalize.build()` 从 requests/iterations 生成 |

## 2. 实际使用的服务、文档与字体

- 服务：`https://open-snapshot.muedsa.com` → `POST /snapshot`，请求体 UTF-8 纯文本 DSL，
  匿名访问（未使用任何凭据）。22 次渲染全部 HTTP 200、全部返回 `image/png`。
- **本次运行真实抓取并存档**（`tmp/.../A10/docs/`，已记入 requests.jsonl）：
  - `https://snapshot.muedsa.com/reference/parser-tags/`（146 738 字节）
  - `https://snapshot.muedsa.com/guides/painting/`（64 351 字节）
  - `https://snapshot.muedsa.com/widgets/painting/color-filtered/`（52 206 字节）
  - `https://snapshot.muedsa.com/widgets/painting/image-filtered/`（55 506 字节）
  - `https://snapshot.muedsa.com/widgets/painting/backdrop-filter/`（52 644 字节）
  - `https://snapshot.muedsa.com/widgets/painting/clip-oval/`（48 966 字节）
  - `https://open-snapshot.muedsa.com/ai-guide.md`（3 718 字节）
- 复用本题库已有抓取（run 起始时已落盘，本次未重复请求）：
  `tmp/.../_suite/docs/openapi.yaml`、`tmp/.../_suite/fonts-list.txt`。
- 字体：只用 `/fonts` 真实返回过的族名 —— `Inter,Noto Sans CJK SC`（正文/中文）、
  `DejaVu Sans Mono`（数字与坐标标注）。未臆造字体名。

## 3. 实际用到的标签与属性

结构骨架：`Snapshot > Container(1440×1100) > Stack(fit=EXPAND) > Positioned …`，
每格 `Positioned > Container(color=#FFFFFF,border) > Stack(fit=EXPAND)`。

| 用途 | 标签 / 属性 |
|---|---|
| 定位 | `Positioned left/top/width/height`、`Stack fit="EXPAND"`（默认 `clipBehavior=HARD_EDGE` 会把内容裁到格内） |
| 色块 | `Container color= shape="CIRCLE"`、`border`、`borderRadius` |
| 文字 | `Text text/color/fontSize/fontFamily/fontStyle/textAlign/textShadow` |
| 阴影 | `Container boxShadow="4 10 10 -2 #0F172ABF"` |
| 半透明组 | `Opacity opacity="0.5"` |
| 背景滤镜 | `BackdropFilter sigmaX sigmaY` + `ClipRRect borderRadius="20"` |
| 子树滤镜 | `ImageFiltered sigmaX sigmaY` + `ClipRRect borderRadius="20"` |
| 颜色滤镜 | `ColorFiltered color="#F6B94A" blendMode="MULTIPLY"` |
| 圆形裁剪 | `ClipOval`（默认 `ANTI_ALIAS`） |
| 标注 | `dashed()` 用短矩形拼虚线、`transform` 未使用 |

### 本题踩到的 DSL 语义坑（均为实测，非引述）

1. **8 位十六进制按 CSS 读 `#RRGGBBAA`**：`#FF000080` 才是 50% 红；旧写法的
   `#80FF0000` 会变成"透明度 0x80 的蓝色系"。本题全部 8 位色都按 CSS 读法写。
2. **`ImageFiltered` 会模糊整棵子树，且子树的透明间隙会让背后的清晰内容漏出来**。
   第一版 ④ 把条纹复制进被模糊的子树但没铺不透明底板，结果卡内条纹的"透明间隙"
   直接透出背后未被模糊的锐利条纹，视觉上像没模糊（见问题表第 1 条）。
3. **`ColorFiltered` 的作用范围 = 子树"绘制边界"再按 sigma 外扩**。子树里的
   `boxShadow` 会把绘制边界撑大（第一版 ⑤ 实测边界 x36–319/y20–189，既不对称也不等于
   ±18px）；给子树加一圈 2px 不透明边框把边界钉死后，实测正好是四边各 +18px = `ceil(3σ)`。
4. **`MULTIPLY` 会给边界内原本透明的像素上色**：⑤ 子树里的透明间隙被填成 `#F6B94A`，
   边界外的白底/条纹保持原色。
5. **`Opacity` 是整层离屏合成**，`#RRGGBBAA` 是逐像素合成：①实测重叠 `#7F3FBF`
   （红透出），②实测 `#7E7EFF`（红被盖住），两者 G 通道差 63 级。
6. **`ClipRRect`/`ClipOval` 会把滤镜硬切在边界上**：④ 卡片上边缘在像素上是 13 级软过渡
   （子树内容被模糊后在边缘淡出），而 ③ 的同一位置只有 1 级硬过渡（BackdropFilter 被裁切）。
7. **本工具库的 `dsllib.box()` 不接受 `shape` 参数**，圆形要走 `extra={"shape":"CIRCLE"}`
   （`BoxShape` 只有 `RECTANGLE`/`CIRCLE`）。
8. **文字框放不下会静默丢弃**：右上角 meta 文字第一版被截断在"抽样点"三个字，
   `D.warnings()` 报了"needs ~2 lines but box holds 1"；把框从 `x=890,w=502` 放宽到
   `x=700,w=692` 后恢复。这是本题库手册里"静默行为"的又一次复现。
9. **`textShadow` 可当白色光晕用**：`textShadow="0 0 4 #FFFFFFF2"` 让压在红/蓝矩形上的
   深色标注文字可读，且没有污染 (180,100) 的采样像素（复验后实测仍是 `#7F3FBF`）。
10. **`Stack` 不接受 `width`/`height`**（未知属性被忽略），尺寸只能靠父级紧约束给。

## 4. 逐项自检表（对照 TASK.md 每条硬指标）

所有"实际值"都是从最终 PNG `compositing-lab.png` 上量出来的，不是从 DSL 里抄的。

| # | TASK.md 要求 | 实际值 | 结论 |
|---|---|---|---|
| 1 | 1440×1100 六格实验板 | PNG 尺寸 1440×1100，签名合法 | ✅ |
| 2 | 上方标题"看到差异，才能说用对了" | 11 字标题渲染在 (48,34)，字号 40，粗体 | ✅ |
| 3 | 实验区 320×240、白底 | 六格四角逐点均为 `#FFFFFF`；格内描边 `#CBD5E1`；区外一像素是版面底色 `#F1F5F9` | ✅ |
| 4 | 3 列 × 2 行 | 列起点 x=48/560/1072，行起点 y=186/572 | ✅ |
| 5 | 区与区间距 ≥32px | 横向 192px、纵向 146px | ✅ |
| 6 | 编号和说明在区外 | 圆形编号+标题在格上方 40px，说明/参数/实测值在格下方 | ✅ |
| 7 | ① 红蓝矩形各 50% alpha | 像素分段实测：红 x40–119(y40–159)、蓝 x120–279(y80–199)，蓝在上；红单独区 `#FF7F7F`、重叠 `#7F3FBF`、蓝单独区 `#7F7FFF` | ✅ |
| 8 | ② 同样两个不透明矩形放进 Opacity(0.5) 组 | y=150 行从 x120 到 x279 全部是同一个 `#7E7EFF`，红层在重叠区完全消失 | ✅ |
| 9 | ③ 圆角卡仅背景模糊 | 卡内文字区 599 个 `#0F172A` 暗像素、最深值等于设定色；卡外条纹相邻像素落差 1 级 | ✅ |
| 10 | ④ 相同条纹，卡内文字与形状一起子树模糊 | 同一文字区暗像素 0 个、最深仅 `#A1A9B4`；卡边变成 13 级软过渡 | ✅ |
| 11 | ⑤ 先 ColorFiltered(MULTIPLY) 后子树高斯模糊 | DSL 为 `ColorFiltered(#F6B94A,MULTIPLY) > ImageFiltered(6,6)`；深色矩形中心实测 `#1A1A10`，子树边框呈软带 | ✅ |
| 12 | ⑥ 同样⑤再限定于圆形裁剪 | `ClipOval` 200×200@ (60,20)；垂直着色区间实测 y20–219 与裁剪框一致；圆外方形四角实测 `#C7D2DE` 原色 | ✅ |
| 13 | sigmaX=sigmaY=6 | 六格滤镜全部 `sigmaX="6" sigmaY="6"`（①②无滤镜） | ✅ |
| 14 | ③④ 卡 240×160、圆角 20 | `ClipRRect borderRadius="20"` 包 240×160 容器 | ✅ |
| 15 | 卡内文字"SHARP / BLUR"字号 24 | ③④ 同文同字号 `fontSize="24"`，用于直接对照 | ✅ |
| 16 | 条纹跨卡边，外部仍清晰 | 条纹铺满 320 宽，卡在 (40,40)–(279,199)；卡外条纹实测 1 级硬边 | ✅ |
| 17 | ⑤⑥ 滤色 `#F6B94A` | 两格 `color="#F6B94A"`；圆心/间隙实测 `#F6B94A` | ✅ |
| 18 | ⑤⑥ 内含透明间隙、深色矩形、阴影 | 子树含 2px 边框、2 块深色矩形、1 条半透明深色条、1 个带 `boxShadow` 的浅蓝圆，其余为透明间隙 | ✅ |
| 19 | 能观察裁剪边界 | ⑤ 四角标记贴在实测边界 x22–297/y22–217；⑥ 画出方形子树边界与四角标记，圆形把深色矩形与浅蓝圆切出缺口 | ✅ |
| 20 | ①② 几何 x=40,y=40,160,120 / x=120,y=80,160,120 | 像素分段完全吻合（见第 7 行） | ✅ |
| 21 | ① 用 `#FF000080` 与 `#0000FF80` | DSL 与像素两侧实测均已核对 | ✅ |
| 22 | 每区 (180,100) 为重叠内部采样点 | (180,100) 同时落在红(x40–199,y40–159)与蓝(x120–279,y80–199)内 | ✅ |
| 23 | 交付 `composite-audit.json`，算①②重叠预期 RGB | 已交付；①预期 `(128,64,191)` 实测 `#7F3FBF`，②预期 `(128,128,255)` 实测 `#7E7EFF` | ✅ |
| 24 | 解释 128/255 与 0.5 的差别 | audit 的 `alpha_128_vs_0.5`：128/255=0.501961，比 0.5 大 0.00196，量化到 8 位只差 0.5 级；语义差异在 G 通道 63 级 | ✅ |
| 25 | ③–⑥ 明确视觉判断（字/背景/外溢） | audit 每格都有 `verdict`，含具体像素与转移级数，不是只写标签名 | ✅ |
| 26 | 引用相关文档 | audit 的 `documentation_cited` 列出 7 个 URL 及其支撑的结论 | ✅ |
| 27 | 说明文字 ≥20 | 六条说明分别 58/52/57/59/77/50 字 | ✅ |
| 28 | 实验区和证据清楚可见 | 整图 + 6 张放大核对图已逐张用 read 工具打开查看 | ✅ |

### 关于"白底"的口径说明（如实记录）

①②的实验区是纯白底。③④⑤⑥的实验区底色同样是 `#FFFFFF`，但按任务同一段里的
"条纹跨卡边，外部仍清晰"要求在其上叠了一层高 212px 的锐利条纹带；条纹带下方保留
28px 纯白底，用作 MULTIPLY 的"未着色对照"。这样既满足"白底"，又能看到条纹跨卡边。

## 5. 问题与修复表

| # | 现象 | 定位方式 | 修复方式 | 复验结果 |
|---|---|---|---|---|
| 1 | ④ 视觉上像没模糊，卡内条纹仍是硬边 | 逐像素扫描卡内条纹（y=60 行）发现蓝通道在 222/238 之间跳变，而模糊应只剩 ±2 级 | 给 `ImageFiltered` 子树加 240×160 不透明底板 `#F1F5F9`，让条纹/文字/形状落在同一被模糊图层 | 卡内落差降到 11 级（卡外 33 级），文字区暗像素 0 个，模糊成立 |
| 2 | ⑤ 滤色边界实测 x36–319/y20–189，与子树±18px 不符 | 对整格做逐像素 `_is_tint` 扫描，比较四边与子树盒的距离 | 定位到子树里 `boxShadow="6 14 20 -4"` 把绘制边界撑大；改为子树内加 2px 不透明边框把边界钉死，并把高光圆改成 `#93C5FDF2`（近白色乘琥珀色会消失） | 实测边界 x22–297/y22–217，四边各 +18px = `ceil(3σ)` |
| 3 | ⑥ 变成方形着色，圆形裁剪失效 | 打开 preview/p6.png 目视 | 重写 `panel_multiply()` 时把 `<ClipOval>` 包裹丢了，补回 `ClipOval > Container 200×200 > ColorFiltered` | 圆外方形四角实测 `#C7D2DE`（未着色），垂直着色区间 y20–219 = 裁剪框 |
| 4 | 顶部右侧 meta 文字被静默截断在"抽样点" | `D.warnings()` 报 "needs ~2 line(s) but box holds 1"，放大图确认 `(180,100)` 缺失 | 文本框 `x=890,w=502` → `x=700,w=692` | 整行完整显示 |
| 5 | ⑤ 的边界说明压在条纹上不易读、②的图例像进度条、行距过紧 | 整图查看 + 2 倍放大 | ⑤ 说明移到白底带；② 图例改成两个 22×13 纯色方块；行距 130→146px；条纹带高度改 212px 留白底 | 整板 v02 复看全部可读 |
| 6 | "采样 (180,100)" 标注压在蓝矩形上读不清 | 3 倍放大观察 | `textShadow="0 0 4 #FFFFFFF2"` 白色光晕 | 标注清晰；复验 (180,100) 仍为 `#7F3FBF`，未被光晕污染 |

## 6. 如实说明与未解决事项

1. **类 DOM DSL 做不到的部分（如实说明，没有假装实现）**：
   `ImageFiltered` / `BackdropFilter` 在类 DOM DSL 里**只有** `sigmaX`/`sigmaY` 高斯模糊，
   `ColorFiltered` 只能给 `color` + Skia `blendMode` 常量名，无法直接构造 `ColorMatrix` /
   饱和度 / 色相矩阵。因此本题**没有**做"饱和度矩阵"类实验，改用 MULTIPLY 与
   MULTIPLY+圆形裁剪来验证 `ColorFiltered` 的作用范围语义。
   需要复杂 Skia 滤镜时必须写 Kotlin DSL，这一点在 audit 的
   `not_possible_in_class_dom_dsl` 里也写明了。
2. **`ColorFiltered` 边界的精确公式未公开**。官方文档只说"保留合法溢出和阴影"，
   没给阴影绘制范围的公式。本题通过 2px 不透明子树边框把边界钉死，得到可复核的
   ±18px 结果；未加边框时边界会被 `boxShadow` 撑大（实测记录在 v01→v03 的迭代里）。
   这是"文档未给出 + 已用可复核方式规避"，不是已解决。
3. **⑥ 圆周在水平极值点附近是渐变而不是硬边**：子树内容被模糊后在子树边缘变透明，
   再与 `ClipOval` 的 `ANTI_ALIAS` 抗锯齿边缘叠加。严格着色区间只有 x72–246，
   而垂直方向实测 y20–219 与 200×200 裁剪框完全一致；圆外方形四角仍是未着色原色，
   所以不是 `ClipOval` 失效。
4. **预览/探针图不是交付物**：`tmp/.../A10/preview/*.png` 全部是过程版本，
   最终交付只有 `compositing-lab.png` 一张（`task-metrics.json` 的 `final_pngs = 1`）。
5. **计量**：平台未提供 token、费用、图像输入用量等指标，`task-metrics.json` 中
   `input_tokens`/`output_tokens`/`image_input_usage`/`cost`/`currency` 一律为 `null`，
   并在 `usage.source` 里写明来源与不可测原因；没有任何按字数或余额的估算。
   限流/排队等待同样记 `null`：本次 22 次渲染没有任何 `Server-Timing` 的 `queue` 段，
   按约定"不能确认没有发生就记 0"，所以留空。
6. **墙钟口径**：`wall_clock_seconds_total ≈ 2793s` 是从第一条 A10 请求
   （2026-10-04T21:15:24+08:00）到收尾（2026-10-04T22:01:57+08:00）的本地墙钟，
   含大量读文档/写脚本/看图时间；22 次渲染的服务+网络耗时合计只有 70.4s，两者不可混用。
7. **无服务错误**：22 次渲染、7 次文档抓取全部 HTTP 200，没有出现 400/413/429/503/504，
   也没有重试。本报告里的"问题"全部是设计/语义/排版问题，不是服务故障。