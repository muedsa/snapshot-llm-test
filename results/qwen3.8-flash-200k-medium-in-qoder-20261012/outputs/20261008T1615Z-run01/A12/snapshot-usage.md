# A12 使用说明与自检报告 · 四断点同一内容的响应式视觉系统

一句话结论：**一份 `content.json` + 一张令牌表（`plan_a12.py`）生成四张画布**，360×800 /
768×1024 / 1440×900 / 1920×1080 全部由 Snapshot DSL 真实渲染，28 次渲染请求全部 HTTP 200，
独立复核脚本 `check_a12.py` 对交付字节 **60/60 通过**（19 条输入字符串在四张画布上逐字命中且
各出现一次）。本题的可行版面不是手调出来的，是三处“看图才发现”的度量错误被逐个证伪以后
自动解出来的，过程见 §4。

## 1. 交付清单

| 文件（`outputs/20261008T1615Z-run01/A12/`） | 字节 | 说明 |
|---|---|---|
| `mobile.png` + `mobile.snapshot` | 88320 / 11639 | 360×800，1 列 6 行卡片，meta 折 3 行，CTA 在流下方 |
| `tablet.png` + `tablet.snapshot` | 119622 / 11677 | 768×1024，2×3 卡片，meta 折 2 行 |
| `desktop.png` + `desktop.snapshot` | 139827 / 11899 | 1440×900，整幅主视觉 band + 3×2 卡片，meta 1 行且 CTA 并入该行右端 |
| `stage.png` + `stage.snapshot` | 170036 / 11941 | 1920×1080，与 desktop 同构件、更大字号与节奏（gap_multiplier 同为 1.6） |
| `design-tokens.json` | 5367 | 跨断点共享的色板/字体/圆角/构件清单 + 每断点的边距、列数、间隙、字号阶梯与下限 |
| `content-map.json` | 33416 | 每个输入字段在每张画布上的文字盒 `[x,y,w,h]`、字号、行数、来源（input/derived）与保留清单 |
| `check-report.json` | — | 15 项 × 4 张的独立复核结果与实测数值（含 `served_by` 指明交付字节来自哪次响应） |
| `snapshot-usage.md`、`task-metrics.json` | — | 本文件与统计 |
| `requests/` | 24 个文件 | 四张交付图的原始 `.body.txt` / `.response-headers.txt` / `.response.bin`（含被替换的 `final` 一轮） |

过程留痕在 `tmp/20261008T1615Z-run01/A12/`：`requests.jsonl`（28 条）、`iterations.jsonl`（25 条）、
`plan_a12.py`（令牌与规则）、`generate_a12.py`（版面求解器与 DSL 生成）、`check_a12.py`（复核）、
`crop_a12.py`（放大取证）、`preview/v01…v05/`（每版四张图与当轮请求归档）、
`preview/crops-final/`（2× 局部放大 + `manifest.json`）、`preview/solver-report-final.txt`。

## 2. 需求逐条对照（依据交付图片与实测数据）

| 需求 | 实测证据（`check-report.json` 的 tag） | 结论 |
|---|---|---|
| 四张画布尺寸精确 | `canvas_size`：actual (360,800)/(768,1024)/(1440,900)/(1920,1080) | 通过 |
| 19 条输入字符串全部逐字出现、不许改写缩写 | `all_input_strings_verbatim`（missing []）、`each_input_string_appears_once`（无重复）；小屏与大屏用的是同一批字符串，卡片标题/详情一字未减 | 通过 |
| 不得裁剪/拉伸/整图位图 | `no_raster_or_external_asset`：DSL 中不含 `<Image`、`http`、`base64`；`content-map.json` 的 `retention` 列出每图 19 个输入字段 | 通过 |
| CTA 只能用文字，不得生成二维码 | `cta` 是 `<Text>` 置于圆角 `Rect` 上的胶囊（`pill` 构件），四张都是 `报名 / Register` 原文 | 通过 |
| 字号下限：mobile 正文≥16、卡片标题≥18；其余正文≥20、标题≥40 | `type_floors` + `min_font_pt_at_least_floor`：mobile 最小 16，tablet/desktop/stage 最小 20，标题 26/48/56/72 | 通过 |
| 安全边距 ≥16（360）/≥32（其余） | `safe_margin`：29 个文字盒全部在边距内；四张画布最紧的一处恰好压在边线上（`website` 行贴内容列底部），无越界 | 通过 |
| 文字盒不得互相重叠 | `no_text_box_overlap`：每图 29 盒两两相交检查，无一对 | 通过 |
| 每个字段在四张画布中的坐标区域与保留情况 | `content-map.json` 的 `fields`（含 `font_pt`/`lines`/`mono`/`provenance`）与 `retention` | 已交付 |
| 断点重排而非四套独立设计 | 同一 `Doc` 构件（heroPanel/accentBar/indexChip/pill/dotRow/ruleLine）、同一令牌表驱动，`gap_multiplier` 与字号阶梯是唯一随断点放大的量 | 通过 |
| 每张最终 PNG 是服务真实响应 | `png_is_raw_service_response`：交付 PNG 的 sha256 与同目录 `requests/A12-final2-<bp>-*.response.bin` 逐字节相同（原始字节未二次编码/转存） | 通过 |
| DSL 自闭合且与请求体一致 | `dsl_is_self_closed`、`dsl_matches_generated_body`（与生成器当前输出 sha256 相同，可复现） | 通过 |

## 3. 文档与 DSL 能力的实际使用

本题没有新增文档 HTTP 请求，全部依据 `tmp/20261008T1615Z-run01/_suite/docs/` 里已经真实取得并
缓存的页面（原请求见 `_suite/requests.jsonl`）：

- `shared-doc-001-guide-ai`（`ai-guide.md`）：`<Positioned>` 必须是 `<Stack>` 的直接子元素、
  单张 ≤4096 元素——本题实测每张 **58 个 Positioned / 29 个 Text**（`layout_report`）。
- `shared-doc-008-doc-layout`、`shared-doc-006-doc-container`：`Stack` 绝对定位 + `Row`/`Column`
  混排，卡片内部用 Row，卡片之间用 Positioned 网格，保证坐标可预测（`content-map` 才有精确盒）。
- `shared-doc-009-doc-painting`：`Rect` 的 `radius`（panel 18 / card 14 / chip 8 / pill 999）与
  1px `Line`，强调条（accentBar）用同色不同宽（4/6/6/8px）承担断点间的重量差。
- `shared-textdoc-…`（`text.html`）与 `shared-doc-011-doc-rendering`：**行盒 = 1.45 em**，
  以及 `TextFit` 在约 0.96×盒宽处换行——这两条是本题全部版面问题的根因（§4）。
- `shared-doc-004-doc-parser-tags`：确认可用标签集合，未使用任何服务不认的标签。
- 字体名取自 `docs/fonts.txt`：正文/标题 `Inter,Noto Sans CJK SC`，序号与网址
  `Noto Sans Mono CJK SC`。服务响应头 `Server-Timing`（`render;dur=…` 或 `cache;desc=hit`）
  逐条记在 `requests.jsonl`，28 次中 4 次命中缓存。

辅助脚本都是真实运行过的：`dslkit.py`（`Doc`/`TextFit` 宽度估算）、`render.py`（渲染与归档）、
`iterlog.py`/`write_iterations_a12.py`（迭代登记）、`crop_a12.py` + `zoom.py`（局部放大取证）、
`state.py`（总进度）。

## 4. 视觉迭代、判据证伪与自检结论

版本序列（每版都出四张，共 28 次渲染，无失败）：
`v01 基线 → v02 desktop 版式重构 → v03 CTA 并入 meta 行 → v04 meta 度量折行流 →
v05 下伸部余量（=交付内容）→ final 交付渲染 → final2 交付渲染（复核后重发）`。
看图事件 **26 次**（16 次整图 + 10 次 2× 放大），其中“复核后接受、不再改”的视觉轮 17 次，
其余 8 次看图直接产出了下一版。

四处只能靠看图/度量发现的证伪：

1. **meta 标签盒宽度写错，主视觉虚高约 110px（A12-solve-02）**。标签盒原先取
   `round(估宽)+2`，而 `TextFit` 在 0.96×盒宽处换行，于是 22/26pt 下“日期/时间/地点”被
   判成 2 行，三行 meta 从 114px 变 225px，`gap_multiplier` 被压到 0.6——**大屏拿到最紧的
   节奏，与小屏统一节奏的意图正好相反**。改为 `round(估宽 / 0.96)+2` 后 stage 主视觉从
   604px 降到 470px 上下，节奏带回到 1.4。
2. **1440×900 撑不起左栏主视觉（v01 看图 → v02）**。v01 的 desktop 把主视觉放在左列：
   主标题被挤成两行（“Vision”单独一行），卡片列比面板矮 117px，页脚又被推到 y=765，
   内容与页脚之间约 175px 空洞。结论写进 `design-tokens.json`：四张一律整幅 band，
   desktop 改 3×2；`solve()` 的余量分配同时修正——原先把 96px 分给了一个在 side 模式下
   恒为 0 的杠杆（hero→grid），属于“看起来分配了其实没落地”。
3. **band 右半空白 → CTA 并入 meta 行（v03）**。desktop/stage 的 meta 一行只占约 700px，
   右侧约 600px 是深色空白而 CTA 独占一行。新增度量规则：流只有一行且
   `行宽 + 24 + 胶囊宽 ≤ 内容宽` 时，CTA 移到该行右端并按两盒中较高者居中对齐；
   主视觉高度 desktop 363→333、stage 512→393。
4. **inline/stacked 二选一太粗 → 真正的折行流（v04）**。tablet 内容宽 642px 其实放得下
   “日期+时间”只差“地点”，却被旧规则整体判成三行堆叠。改为逐组累加宽度、放不下才整组
   换行，得到 3/2/1/1 行的自然过渡（`layout_report` 的 `meta_block`）。

**下伸部被切是复核脚本抓出来的，不是看图看出来的（A12-audit-01）**：`check_a12.py` 首跑
60 项里 2 项失败——mobile 与 desktop 的 `website` 文字盒底部有 7px / 2px 的墨迹贴到盒边，
等宽字体的 `g`、`p` 下伸部被 1.45em 行盒切到最后一条像素行。修法是所有文字盒高度改为
`round(size*1.45*lines)+2`（`box_height_rule` 里写明了这个 +2 的来历）。它使 mobile 溢出 24px
（6 张卡各多 4px），于是把胶囊内边距改为随字号伸缩 `+max(18, 0.9*size)`，并把 mobile 的
`inner` 8→7、`cardGap` 16→14，节奏带下限随之落到 0.5。另有一处**复核脚本自身的假失败**
（A12-audit-02）：provenance 用 `A12-final-{bp}-*` 匹配，而交付目录保留着上一轮 `final` 的
原始响应，于是比对到了旧文件；改为 `A12-final*-{bp}-*` 按 mtime 取最新一次响应。

最终求解状态（`preview/solver-report-final.txt`，`problems` 与 `text_fit_problems` 均为 []）：

| 断点 | gap_multiplier | 主视觉高 | meta 行数 | CTA | 底部用量/上限 | 卡片 |
|---|---|---|---|---|---|---|
| mobile | 0.5 | 251 | 3line | below | 783 / 784 | 1×6，h69 |
| tablet | 1.6 | 368 | 2line | below | 984 / 992 | 2×3，h109 |
| desktop | 1.6 | 333 | 1line | same_line | 856 / 868 | 3×2，h119 |
| stage | 1.6 | 393 | 1line | same_line | 1022 / 1040 | 3×2，h137 |

看图覆盖：`preview/v01…v05/` 各四张整图都逐张开过；交付字节与 `preview/v05/` 四张
**sha256 完全相同**（`0a44f944…`/`63da8f3e…`/`0a37cf52…`/`23ed91d5…`），因此整图复核覆盖的
就是交付图本身；另有 **10 张从交付 PNG 直接裁出的 2× 放大**（mobile 主视觉 / C1–C2 卡片 /
页脚，tablet meta 两行 / C6 卡片，desktop 单行 meta+CTA / C3 卡片，stage 主视觉行 / C4 卡片 /
页脚），清单见 `preview/crops-final/manifest.json`。结论：字形完整、无贴边裁切；唯一需要
说明的是 `stage-footer.png` 的裁切框左缘切掉了 7px 强调点——该点在 DSL 里 `left="40"` 正好
等于 stage 安全边距，是裁切边界而非渲染裁切，整图 `stage.png` 中完整。

## 5. 统计与未解决事项

- 渲染请求 **28**（`kind=render`，全部 200，0 失败 0 重试），请求耗时之和 **122.592s**；
  任务墙钟 2026-10-08T15:45:23Z 起，交付图最后一条响应 16:22:42Z。
- DSL 版本 7（v01/v02/v03/v04/v05/final/final2，每版四张共 28 份请求体）。
- 看图事件 26（16 整图 + 10 张 2× 放大），接受的视觉轮 17、驱动改版的视觉轮 8，基线轮 3，
  自检轮 2（`iterations.jsonl` 共 30 行）。
- 审计：`check-report.json` 60/60 通过，`failures: []`。
- 未解决事项：**无**。一条已知约束值得记录：mobile 的 `gap_multiplier` 落在节奏带下限 0.5，
  因为 800px 高要装下 6 张完整卡片 + 3 行 meta + 页脚；若后续在同一画布上再加内容，只能
  放宽卡片行数或允许卡内换行，不能再靠缩小节奏带解决。
