# Snapshot 使用情况说明与踩坑记录

任务ID：A12
任务名称：A12 · 四断点完整内容视觉系统
本次运行ID：run-20261011-01
完成状态：完成
结束原因：四尺寸需求满足并完成逐张与放大裁剪的视觉自检
输出目录：outputs/run-20261011-01/A12/
临时目录：tmp/run-20261011-01/A12/
路径基准：suite_root（本文件内 Markdown 链接相对本文件）

遵循[PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径。图片链接
相对本文件（最终图与 DSL 在同目录）。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| [mobile.snapshot](mobile.snapshot) | 360×800 手机单列 DSL | [mobile.png](mobile.png) | 完成 |
| [mobile.png](mobile.png) | 服务返回最终图（原始字节，md5 70af22a3…） | [mobile.snapshot](mobile.snapshot) | 完成 |
| [tablet.snapshot](tablet.snapshot) | 768×1024 平板 2×3 网格 DSL | [tablet.png](tablet.png) | 完成 |
| [tablet.png](tablet.png) | 服务返回最终图（原始字节，md5 cb5c4af6…） | [tablet.snapshot](tablet.snapshot) | 完成 |
| [desktop.snapshot](desktop.snapshot) | 1440×900 桌面 3×2 网格 DSL | [desktop.png](desktop.png) | 完成 |
| [desktop.png](desktop.png) | 服务返回最终图（原始字节，md5 c61b5b7d…） | [desktop.snapshot](desktop.snapshot) | 完成 |
| [stage.snapshot](stage.snapshot) | 1920×1080 大屏 3×2 网格 DSL | [stage.png](stage.png) | 完成 |
| [stage.png](stage.png) | 服务返回最终图（原始字节，md5 b0af4d21…） | [stage.snapshot](stage.snapshot) | 完成 |
| [design-tokens.json](design-tokens.json) | 颜色/字号/间距/组件与断点布局规则 | 支撑四图 | 完成 |
| [content-map.json](content-map.json) | 19 必显字段 ×4 画布的坐标/字号/完整性 + C1–C6 映射 + 4 项检查 | 支撑四图 | 完成 |
| [task-metrics.json](task-metrics.json) | 结构化指标 | — | 完成 |

需求逐项核对（证据 = 四张最终图 + content-map.json 实测 + design-tokens.json）：

- 四尺寸 360×800、768×1024、1440×900、1920×1080 各自独立排版，全部由 DSL 构造；
  **未使用任何 Image 组件**，无裁切、无拉伸、无整图适配（design-tokens.json 的
  adaptation_rules 记录该规则）✓。
- 一字不丢：title「Structure / Vision」、subtitle「让模型从读懂文档到完成作品」、
  date「2026.11.07」、time「09:00–16:00」、location「云构中心 · ONLINE」、
  cta「免费参加 · 扫码方式详见官网」、website「structure.example.org」及 6 张卡的
  title+detail 共 19 个必显字段，在四种画布中逐字符完整显示（无省略号、无缩写、
  无改写；手机端仅在 title 原有的空格处折为两行）✓。逐图放大读图核对 + 每个申报
  文字盒实测含真实文字墨迹（最低墨迹计数远超阈值 30）✓。
- 字号：手机正文 16（subtitle/日期时间/CTA/website/卡 detail）、卡标题 18；
  其余画布正文 20–30、主标题 56/64/72（均 ≥40）✓。
- 安全边距：手机 16、平板 40、桌面 56、大屏 64（≥16/≥32）；四张图全局文字墨迹
  包围盒分别为 [16,25,344,758]、[40,55,727,946]、[56,67,1383,835]、[64,77,1855,1003]，
  全部落在安全区内（背景渐变用亮度阈值排除）✓。
- 实际文字盒不重叠：生成时对全部申报盒两两断言，交付图上再按实际墨迹包围盒两两
  检查，四画布 0 重叠 ✓。
- 统一色彩/形态/层级：同一渐变背景、同色板、同一组件栈（标题块 + 强调条 + 元信息
  芯片 + CTA 胶囊 + 卡片(左侧色条+ID徽章) + 页脚），仅列数与间距随断点变化；装饰为
  相同核心构件重排（手机省略页脚与 S/V 水印，平板省略水印）✓。
- CTA 为纯文字，无二维码 ✓；cards[].id 只作追踪，显示为徽章，content-map.json
  记录 C1–C6 与字段路径的对应关系 ✓。
- 信息联系不因缩屏丢失：手机上 title→subtitle→元信息芯片→CTA/网站→六卡顺序排列，
  各段之间有分隔条/间距保持分组 ✓。

交付 JSON 核对：design-tokens.json 含 colors/typography/spacing/components 必需字段；
content-map.json 含 canvases/entries 必需字段（entries 19 条，逐画布记录 box、
font_size、actual_ink_box、complete、text_matches_source），identity
（schema_version 1、task_id A12、path_base output_dir）齐全，4 项 checks 全部 passed
并附查看证据。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档版本或访问日期：ai-guide.md、parser-tags.html、字体查询结果均为本套共享缓存
（tmp/run-20261011-01/_suite/docs/，套件启动时真实抓取，本题复用不重复计为新请求）。

AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md
- 实际阅读（缓存）：`<Snapshot type="png">` 根节点、SizedBox/Stack 结构、请求需浏览器
  UA、`GET /fonts`。四张 DSL 全部按该结构构造。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| ai-guide.md（缓存） | Snapshot/SizedBox/Stack/Positioned/Container/Text 结构 | 四张 [mobile.snapshot](mobile.snapshot) 等根结构 |
| 标签参考 parser-tags.html（缓存，本题实际抽取属性表） | Positioned 支持 left/top/right/bottom/width/height（每轴最多两项）；Container 的 color/borderRadius/boxShadow/gradientType/gradientColors/gradientBegin/gradientEnd；Text 的 style 属性、height（行高倍数）、textAlign（默认 START，用 CENTER 居中 CTA/芯片/徽章文字）；Opacity 0–1 | design-tokens.json 的 typography.line_height；CTA 胶囊与芯片的居中文字；四图的线性渐变背景 |
| 字体查询缓存 fonts.txt | 可用字体 Inter+Noto Sans CJK SC、Noto Sans Mono CJK SC | 正文/标题 sans、日期时间/website/ID 徽章 mono |

用到的其他能力：渐变 Container（LINEAR, TOP_CENTER→BOTTOM_CENTER）、boxShadow 自定义
格式 `x y blur spread color`、圆角、textAlign 居中/右对齐、height 行高控制。未使用
Image（A 类纯 DSL）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：tmp/run-20261011-01/A12/requests.jsonl
迭代记录文件：tmp/run-20261011-01/A12/iterations.jsonl
渲染请求总数：8
成功次数：8
失败次数：0（无 400/429、无重试；v1 的缺陷是静默的——HTTP 200 但文字不可见）
重试请求数：0
DSL版本数：2（v1/v2，各含四张断点 DSL）
实际图片查看次数：12（v1 手机+平板 2、v2 四张整图 4、放大裁剪 2、交付图整图复看 4）
完整视觉迭代数：1（v1→v2）
未完成视觉迭代数：0
其他接口查询：0（3 条文档/字体缓存复用记录在 requests.jsonl，不计新请求）

| 请求ID / 轮次 / 迭代ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| A12-req-0001–0004 / iter-001 baseline | drafts/{mobile,tablet,desktop,stage}.snapshot（v1） | 2026-10-14T10:16:55+08:00 起 1.3–2.5s/张 | 4×200 / image/png | drafts/*-v1.png | 10:17 看手机+平板整图：**全部文字不可见**——样式属性被误写在 `<Positioned>` 上，解析器静默忽略，文字以默认黑色渲染在深底上；形状全部正常 |
| A12-req-0005–0008 / iter-002 visual | drafts/*.snapshot（v2，text_el 修正） | 10:18:31 起 1.9–5.1s/张 | 4×200 / image/png | drafts/*-v2.png（即最终图原字节） | 10:19–10:20 逐张看四张整图：19 个必显字段全部可见且逐字符一致，布局/字号/边距/层级达标 → 定稿复制到 outputs |
| iter-003/004 测量 | —（本地像素实测，无请求） | 10:22 首跑 / 10:23 重跑 | — | — | 首跑 mobile 报 6 处"重叠"（±4px 窗口渗色的度量误报）；改为严格按申报框量测后四画布全部通过，并打开 2 张放大裁剪 + 4 张交付图复看 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| iter-001 / baseline | 四张图 HTTP 200 但一个字都没有 | 看图确认（手机+平板 v1 整图）：生成器把 fontSize/color/fontFamily/fontStyle/textAlign 写在 `<Positioned>` 上；文档（parser-tags Text 节）说明这些是 Text 的属性，解析器对 Positioned 上的样式属性**静默忽略**——错误只在视觉上暴露 | text_el() 改为 `<Positioned left top width><Text fontSize color fontFamily height fontStyle textAlign>…</Text></Positioned>`，几何归 Positioned、样式归 Text | v2 四张全部出字，需求逐项通过；**本题最大踩坑：HTTP 成功≠内容正确，必须看图** | drafts/mobile-v1.png、tablet-v1.png |
| iter-002 / visual | 无新缺陷 | —— | 无需再改，直接定稿（首版达标不制造迭代） | 四图定稿，md5 与服务响应字节一致 | outputs/run-20261011-01/A12/*.png |
| iter-003 / 测量修正 | 重叠检查在 mobile 误报 6 对（卡标题 vs 卡详情差 1px 相交） | 度量窗口取了申报框 ±4px，标题窗口把下一行的抗锯齿顶行包了进来；实际两行相距 4px | 量测窗口改为严格限制在申报框内，再两两比对实际墨迹包围盒 | 重跑：四画布 0 重叠、覆盖率与边距全过；实际墨迹盒写回 content-map.json | scripts/measure_a12.py |

另记录：渐变（gradientType/gradientColors/gradientBegin/gradientEnd）与 boxShadow 自定义
字符串首次使用即通过解析，无 400；全程 8 渲染全部 200，无 429、无重试。

## 5. 任务耗时与请求统计

结构化指标文件：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-14T09:58:00+08:00（约）– 2026-10-14T10:32:00+08:00 | 含时区时间 | 起始为 A11 完成（09:50）后读题，结束为本报告写入 |
| 任务总耗时 | 2040 | 秒 | 单段会话墙钟 |
| 首次可用图耗时 | 1135 | 秒 | 起始 → 首次成功渲染（10:16:55，v1 手机；该版文字不可见，真正可用图为 10:18:31 的 v2，1169s） |
| 等待用户反馈 | 0 | 秒 | 单次自动执行，无用户反馈轮次 |
| 限流等待、排队等待 | 0 / 未知 | 秒 | 无 429；服务端排队时间不可测，记 null |
| 已记录请求耗时之和 | 19.496 | 秒 | requests.jsonl 8 次渲染之和，不等于任务总耗时 |
| 成功、失败、重试请求 | 8 / 0 / 0 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 12 / 1 | 次 | iterations.jsonl 及实际查看记录（另有 2 次测量方法修正迭代） |

## 6. 设计选择、经验与未解决事项

关键设计选择：

- 一份 content.json + 一份 design-tokens.json 参数 → 生成器按断点函数分别排版，
  每张是独立完整 DSL（非缩放/裁切），生成时即对全部申报文字盒做两两不重叠与
  安全边距断言，不满足直接抛错。
- 拓扑保持"标题→副标题→强调条→元信息→CTA/网站→六卡→页脚"的同一语义链：手机把
  芯片竖排、CTA 变全宽胶囊；平板 2×3；桌面/大屏 3×2 并加 S/V 水印——同一组件栈
  仅重排，色彩与层级完全一致。
- 全部 Text 显式 `height="1.2"`，把行盒钉死为 1.2×字号，预留高度不再依赖字体默认
  行高，换行行为可预测。
- 数字/日期/website/ID 徽章统一 mono，中文/标题统一 sans：跨断点字号变化时仍保持
  相同的阅读节奏。
- 保真核验双保险：生成端断言 displayed==source 且无省略号；交付端按申报盒测真实
  墨迹（覆盖）+ 实际墨迹盒两两不相交（重叠）+ 全局墨迹在安全区内（边距）。

可复用经验：**样式属性写错位置不会报 HTTP 错误，只会静默出空图——每个 DSL 新结构
先渲染小图看一眼**；像素重叠检测的量测窗口不要越出申报框，否则相邻行的抗锯齿会
造成误报；渐变与 boxShadow 自定义字符串可直接用，无需探针。

未解决事项：无。四项检查全部 passed，8 次渲染全部 200，四张最终 PNG 与服务响应
字节一致（md5 校验通过）。

留痕确认：tmp/run-20261011-01/A12/ 保留 drafts/（v1、v2 各四张 PNG 与 DSL）、
crops/（2 张放大裁剪）、requests.jsonl（8 渲染 + 3 文档缓存复用）、iterations.jsonl、
scripts/（生成与测量脚本）；失败尝试未删除。总任务根 .gitignore 已按
templates/gitignore-template.txt 合并，排除 __pycache__/ 等运行时缓存，未排除 tmp/、
outputs/ 或任何过程证据。
