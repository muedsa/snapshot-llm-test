# A13 · 品牌标志到完整活动应用 — 使用报告

## 完成状态

**已完成（completed）**。四张指定最终 PNG 全部由 `POST https://open-snapshot.muedsa.com/snapshot`
的真实响应字节直接落盘，未经任何后处理；每张都有同名 `.snapshot`（与出图时提交的 DSL 完全一致）。

- 输出目录：`outputs/20261004-182918/A13/`
- 临时目录：`tmp/20261004-182918/A13/`
- 自检报告（机器可读）：`tmp/20261004-182918/A13/verify/report.json`（16 项检查全部 PASS）

## 实际使用的服务文档与字体（全部本次真实抓取，未复用其他题的抓取结果）

| URL | 状态 | 用途 |
|---|---|---|
| `https://open-snapshot.muedsa.com/ai-guide.md` | 200 | 请求体是 UTF-8 纯文本 DSL、8 位 hex 按 `#RRGGBBAA` 读、`GET /fonts` 的用法 |
| `https://open-snapshot.muedsa.com/openapi.yaml` | 200 | 接口定义 |
| `https://snapshot.muedsa.com/` | 200 | 站点入口，取真实文档链接 |
| `.../guides/widgets/` | 200 | 取全部 widget 文档 URL（发现 `Text` 在 `/widgets/text/text/`，不是 `/basic/text/`） |
| `.../guides/painting/` | 200 | 绘制类 widget 索引 |
| `.../reference/parser-tags/` | 200 | 类 DOM 解析器标签参考 |
| `.../reference/enums/` | 200 | 枚举速查，确认 `TOP_CENTER` / `BOTTOM_CENTER` 合法 |
| `.../widgets/text/text/` | 200 | `Text` 函数签名与 TextStyle 字段（`softWrap`/`maxLines`/`overflow` 等） |
| `.../widgets/layout/container/` | 200 | Container 装饰能力 |
| `.../widgets/painting/decorated-box/` | 200 | BoxDecoration 字段；`shape=CIRCLE` |
| `.../widgets/painting/clip-oval/` | 200 | `ClipOval` 存在，正方形区域得正圆 |
| `.../widgets/painting/clip-rrect/` | 200 | `ClipRRect` 存在（只裁剪不绘制） |
| `.../widgets/painting/colored-box/` | 200 | `ColoredBox` |
| `.../widgets/layout/transform/` | 200 | 备查（本方案最终不使用旋转） |
| `.../widgets/basic/text/` | **404** | 猜测的 URL，失败即停手，未据此臆造属性 |
| `GET https://open-snapshot.muedsa.com/fonts` | 200 | 27 个字体族，本题只用其中真实存在的名字 |

本次真实可用字体（`fonts.txt` 全量）：Inter、Inter Black/Extra Bold/Extra Light/Light/
Medium/Semi Bold/Thin、Noto Sans CJK JP/KR/SC/TC/HK、Noto Sans Mono CJK …、
Noto Serif CJK JP/KR/SC/TC/HK、DejaVu Sans、DejaVu Sans Mono、DejaVu Serif、Noto Color Emoji。

字体使用：`Inter`（拉丁）、`Inter,Noto Sans CJK SC`（中英混排）、`Noto Sans CJK SC`（纯中文）、
`DejaVu Sans Mono`（URL/等宽数字）。**未臆造任何字体名。**

## 实际用到的标签与属性

`Snapshot`(type/background)、`Container`(width/height/color/borderRadius 及四角
borderRadiusTopLeft/TopRight/BottomRight/BottomLeft/border/boxShadow/opacity)、
`Stack`(fit="EXPAND")、`Positioned`(left/top/width/height)、`Text`(text/fontSize/fontFamily/
fontStyle/color/letterSpacing/textAlign/maxLines)、`ClipOval`、`ClipRRect`、`ColoredBox`。
渐变：`gradientType="LINEAR"` + `gradientColors` + `gradientStops` + `gradientBegin`/`gradientEnd`。
两个 512 图标的 DSL 只用了 4 种标签：`Snapshot / Container / Positioned / Stack`。

## 本题踩到的 DSL 语义坑（全部有真实失败或真实测量证据）

1. **`gradientBegin="CENTER_TOP"` 报 400**：`Attr [gradientBegin] value format error`。
   查 `reference/enums/` 后改用 `TOP_CENTER` / `BOTTOM_CENTER`（`CENTER_LEFT`/`CENTER_RIGHT`
   也在枚举里）。这是本题唯一一次 HTTP 400。
2. **透明背景可用但必须显式写**：`<Snapshot background="#00000000">` 产出真实 alpha 通道
   （探针 `probe-alpha.png` 实测 alpha min/max = 0/255，四角 alpha=0）。
3. **未知/写错的枚举不会静默通过**：写错的枚举是 400，不是静默忽略——与本套手册里
   "未知属性被忽略"的结论并列存在，写 DSL 时不能靠猜。
4. **自己代码里的比例 bug（不是服务的问题，但同样是必须靠看图+测量发现的）**：
   `layerlight.emit()` 最初自己用 `k = size/GRID` 重算缩放，忽略了 `fitted()` 返回的缩放，
   导致 512 图标按 1:1 画出 450 单位的墨迹（ink bbox 实测 451px），右下几乎贴边、
   破坏了 1/9 留白。改为直接使用 `fitted()` 返回的 `k` 后 ink bbox = 400px、留白 56.9px。
5. **同色相邻矩形会留 1px 抗锯齿缝**：沿 `叠光` 上腿/左腿共享边扫描 alpha，实测该处
   alpha 只有 193/255（图上肉眼可见一条发丝缝）。修法是让一条腿沿共享边方向多画 1 个
   **设备**像素（`pad`，不改动轮廓/通窗/ink bbox），修后该扫描线上再无非 0/非 255 的中间值。
6. **静默溢出未被触发**：`D.warnings()` 全程为空，但这是因为我给每个文本框都留了足够宽度并
   用 `est_width()` 预估（横幅 wordmark 预估 435.7px / 框宽 504px）。这是主动规避，不是没遇到。

## 逐项自检表（TASK.md 硬指标 → 实测值 → 结论）

| # | TASK.md 指标 | 实测值 | 结论 |
|---|---|---|---|
| 1 | 两个真正不同几何方向的 512×512 透明预览，保留在临时目录 | `preview/direction-A.png`、`direction-B.png`，均 512×512 RGBA、alpha min 0 | ✅ 两图几何路线不同（面积交叠 vs 平行分层），都实际打开看过 |
| 2 | 看图选择后完善同一方案 | 选 A（依据见 `rationale.md` 与 `preview/candidates.png` 六方案对照） | ✅ |
| 3 | 512×512 透明彩色图标 | `symbol-color.png` 512×512 RGBA，4883 bytes | ✅ |
| 4 | 512×512 透明纯黑图标 | `symbol-black.png` 512×512 RGBA，3576 bytes | ✅ |
| 5 | 1200×400 品牌横幅 | `brand-banner.png` 1200×400 | ✅ |
| 6 | 1080×1350 发布海报 | `launch-poster.png` 1080×1350 | ✅ |
| 7 | 两图标几何相同 | alpha 遮罩逐像素比较：91 px 不同、**最大差 1**（Skia 光栅化舍入）；ink bbox 与通窗 bbox 完全相同 `(190,190,322,322)` | ✅ |
| 8 | 抗锯齿 alpha 允许 | 已使用；容差即上条 | ✅ |
| 9 | 非透明黑版 RGB 必须为 0 | alpha>0 的像素中 RGB≠0 的数量 = **0** | ✅ |
| 10 | 最多 6 个主要几何构件 | **4** 条腿（上限 6） | ✅ |
| 11 | 32×32 仍能识别轮廓与关键负空间 | 服务端直渲 32×32 与 512→LANCZOS 缩略并放大 14× 实际查看：轮廓为阶梯双片、通窗约 9px 清晰可辨；单色版同样成立 | ✅ |
| 12 | 横幅含"叠光 Layerlight" | 在 `brand-banner.snapshot` 中逐字符串校验存在 | ✅ |
| 13 | 横幅含"把复杂信息，组织成清晰画面" | 同上校验存在 | ✅ |
| 14 | 海报含"2026.11.07 · ONLINE" | 在 `launch-poster.snapshot` 中校验存在 | ✅ |
| 15 | 海报含"OPEN BETA" | 同上校验存在（琥珀色胶囊） | ✅ |
| 16 | 海报含"layerlight.example.org" | 同上校验存在 | ✅ |
| 17 | 不得用标志 PNG 嵌入两应用 | 两应用与两图标均由同一个 `emit()` 生成；四份 DSL 中 `<Image`/`dataUri`/`http` 出现次数 = 0 | ✅ |
| 18 | 海报独立构图，非放大横幅 | 海报为深底竖版：顶栏(52px 标志)/420px 主标志/字标堆叠/三栏能力/底部卡片(96px 标志)，与横幅的浅底横版双panel结构不同 | ✅ |
| 19 | 统一色板与网格 | `brand-system.json` 记录 12 个色值与角色；标志只用 indigo_deep+cyan 两墨，amber 只用于行动点；留白统一 ink/9 | ✅ |
| 20 | `brand-system.json`（色彩/比例/构件/最小留白/各应用映射） | 15430 bytes，五部分齐全，数值直接由 `layerlight.MARK` 与实测 report 生成 | ✅ |
| 21 | `rationale.md` ≤300 字 | 去标题/空白后 **299** 字符（其中 CJK 200） | ✅ |
| 22 | 大图与 32×32 缩略均实际查看，缩略只作预览、存临时目录 | 512/1200×400/1080×1350 三张大图 + 32/48/64 服务端直渲 + 32×32 缩略对照表，共 **21** 次真实看图（逐图清单见 `task-metrics.json` 的 `a13_detail.actual_image_open_list`）；缩略全在 `tmp/.../preview/` | ✅ |
| 23 | 所有指定最终 PNG 是服务真实响应且有同名 `.snapshot` | 4/4 存在，magic 为 PNG，`.snapshot` 与当次提交文本逐字相同 | ✅ |

## 跨应用几何一致性（从像素反测，不看声明值）

方法：对每个应用中的标志实例，用"到标志油墨比到本地底色更近"的分类（平局判为材料，
以堵住抗锯齿角落的针孔），再从 ink bbox 边界对背景做 4 邻域泛洪填充；泛洪到不了的背景
像素即为封闭空洞 = 通窗。

| 实例 | ink 实测 | 通窗实测 | void/ink |
|---|---|---|---|
| symbol-512（彩色/黑版） | 400×398 | 132×132 | 0.330 |
| banner 左 panel，248px | 248×248 | 82×82 | 0.3306 |
| poster 主标志，420px | 420×420 | 140×140 | 0.3333 |
| poster 顶栏，52px | 52×52 | 18×18 | 0.3462 |
| poster 底卡，96px | 96×96 | 32×32 | 0.3333 |

模型值 0.3333（offset 150 / ink span 450），全部落在 ±0.02 内；每个 ink 与通窗都是正方形。
→ 同一几何、同一比例、同（无）旋转，在 52px 到 512px 之间成立。

留白实测：符号四周 ≥56px（要求 44.2）；banner 标志到 panel 边 76px（要求 27.6）；
poster 主标志到顶栏 52px（要求 46.7）；poster 底卡标志到卡边 25px（要求 10.7）。全部达标。

## 问题与修复表

| 现象 | 定位方式 | 修复方式 | 复验结果 |
|---|---|---|---|
| `gradientBegin="CENTER_TOP"` → 400 PARSE_ERROR | 服务 JSON `message` 给出属性名与位置 | 查枚举文档，改 `TOP_CENTER`/`BOTTOM_CENTER` | 复渲染 200；渐变竖向正确 |
| 512 图标墨迹 451px、右下几乎贴边 | `measure_symbol.py` 打印 ink bbox `(57,57,508,508)`，与声明的 398 不符 | 发现 `emit()` 重算缩放，改为使用 `fitted()` 返回的 `k` | ink bbox `(56,57,456,455)`，四边 56/57px |
| 上腿/左腿共享边出现发丝缝 | 沿 y=86 扫描 alpha，发现 x=207 处 alpha=193 | 上腿 `pad.left=1` 设备像素 | 该扫描线只剩圆角与外边缘的正常 AA 中间值 |
| 下腿/右腿共享边同类缝 | 沿 y=400 扫描 | 下腿 `pad.right=1` 设备像素 | 同上，无缝 |
| 单色版 32×32 是一团无结构黑块 | 放大 12× 实际看 `check-black-32x32.png` | 核心改为真负形，重构为 4 腿分解 | 32×32 通窗 9px、轮廓可辨；两版 alpha 遮罩最大差 1 |
| 验证脚本把两个凹角误判成"通窗" | 首次 verify 报 void/ink=0.995，明显不合理 | 改为从 bbox 边界泛洪，只认封闭空洞 | void/ink=0.330，与模型一致 |
| 泛洪仍从抗锯齿角落漏出 | banner/top-bar 实例报 "no void" | 分类改为最近色规则、平局判为材料 | 四个实例全部测出正方形通窗 |
| 海报 叠光 与 Layerlight 挤在一起 | 实际看图发现间距仅约 15px | 下移字标与整段下部节奏 | 复渲染后间距约 34px，全图节奏均衡 |
| `preview/thumb32-check.png` 面板标签顺序与实际排列不符 | 打印实际顺序时发现 | 改为显式 `(tag, colour)` 配对并输出 labels.txt | 4 格顺序与标注一致 |

## 未解决事项与如实说明

- **未遇到**的问题：没有 429/503，没有排队，没有 `Snapshot` 无限布局，没有
  `Positioned` 空标签 / 多子节点 / 错父级、没有 `padding="24 32"` 形式、没有虚线边框。
  唯一一次 400 是上表第 1 行，已修复。
- **token / 费用 / 图像输入用量：全部未知（null）**。open-snapshot 的 HTTP 接口没有返回
  token 或计费指标，本次也没有任何平台侧的可信计量来源；因此没有按字数、字节数或
  余额去估算，`task-metrics.json` 中相关字段保持 null 并写明原因。
- **排队等待时间**：服务响应头里本次未出现 queue 段，因此
  `rate_limit_or_queue_wait_seconds` 记 null（"确认没发生"才记 0）。
- **两次 alpha 遮罩 91px、最大差 1** 的差异来自 Skia 对同一几何两次独立光栅化的舍入，
  不是设计差异；容差与数字都写进 `verify/report.json`。
- **`D.warnings()` 全程为空**：这是按 `est_width()` 预留宽度后的结果，属于主动规避；
  不宣称"验证过静默溢出行为"。
- 32px 的可靠性只在 32px 及以上验证过；低于 32px 未做测试，也未在交付物里声称可用。

## DSL 层级的同一性证明（不依赖像素）

`check_dsl_identity.py` 的实测结果：

- `symbol-color.snapshot` 与 `symbol-black.snapshot` 里的 `Positioned` 矩形列表**逐个相同**：
  `132.74×265.48`、`133.74×132.74`、`132.74×265.48`、`133.74×132.74`（各 2 个方向出现两次），
  两者都只有 **4 个 `Positioned`**，只有 `color` 不同
  （`#4338CAFF`+`#22D3EEFF` vs `#000000FF`）。→ 几何相同，颜色不同。
- 三份交付 `.snapshot` 与临时目录中同时提交的草稿副本 sha256 一致
  （symbol-color `2625493e…`、symbol-black `9a585f24…`、brand-banner `3abbea14…`），
  即交付的 DSL 就是出图时提交的那一份。
- 两份 512 图标的 DSL 一共只用 4 种标签：`Snapshot / Container / Positioned / Stack`。

## 目录内的过程留痕

- `tmp/.../A13/requests.jsonl`：95 条请求（77 次成功渲染、1 次 400、1 次 404 文档、
  16 次文档/字体），每条含唯一 ID、起止时间（+08:00）、耗时、HTTP 状态、Content-Type、
  请求/响应文件路径、`X-Request-Id`、Server-Timing（服务未返回即为 null）。
- `tmp/.../A13/iterations.jsonl`：基线 / 方案探索 / 视觉迭代 / 语法修复逐条记录
  （版本号、父版本、观察时间、观察到的问题、具体改动、复看结论），共 18 条，无空字段。
  第一次 wrapup 写出的 18 条里 v03 的 DSL 查找没命中"同一份 DSL 的成功重渲染"，
  导致 `dsl_file`/`viewed_at` 为 null，已把原文件整体归档为 `iterations-regenerated.json`
  后重新生成（`requests.jsonl` 的请求留痕未被改动）。
- `tmp/.../A13/drafts/`：每次提交的 DSL 副本（v01…v12 顺序编号）。
- `tmp/.../A13/preview/`：两个方向预览、方案对照表、各版本符号与 32/48/64 检查图、
  放大对照图；`tmp/.../A13/crops/`：局部放大核对图；`tmp/.../A13/verify/report.json`。
- 失败响应保留在 `tmp/.../A13/responses/`，未清理、未覆盖。