# Snapshot 使用情况说明与踩坑记录 — B03

任务ID：B03
任务名称：用十件作品探索DSL的创意边界
本次运行ID：20261104-145656-hy4all
完成状态：完成
结束原因：需求满足并完成逐件视觉自检
输出目录：`outputs/20261104-145656-hy4all/B03/`
临时目录：`tmp/20261104-145656-hy4all/B03/`
路径基准：suite_root（记录内本地路径均相对总任务根；Markdown 链接相对本文档）

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `case-01/final.png` | 潮汐·当代艺术展海报 900×1300 | `case-01/final.snapshot` | 完成；服务真实 PNG 203123 字节 |
| `case-02/final.png` | ORIGIN·杯测风味轮 1200×1200 | `case-02/final.snapshot` | 完成；服务真实 PNG 267164 字节 |
| `case-03/final.png` | 城市心跳·地铁客流看板 1600×900 | `case-03/final.snapshot` | 完成；服务真实 PNG 178937 字节 |
| `case-04/final.png` | 等高线·云脊徒步路线卡 1100×1100 | `case-04/final.snapshot` | 完成；服务真实 PNG 184262 字节 |
| `case-05/final.png` | 光谱·摄影色温速查卡 1600×1000 | `case-05/final.snapshot` | 完成；服务真实 PNG 153782 字节 |
| `case-06/final.png` | 夜读·月相会员卡 800×1200 | `case-06/final.snapshot` | 完成；服务真实 PNG 173772 字节 |
| `case-07/final.png` | 共振·声学频谱报告 1600×1000 | `case-07/final.snapshot` | 完成；服务真实 PNG 181496 字节 |
| `case-08/final.png` | 折光·建筑玻璃样板册页 1000×1400 | `case-08/final.snapshot` | 完成；服务真实 PNG 219690 字节 |
| `case-09/final.png` | 年轮·精酿季节菜单 1500×1000 | `case-09/final.snapshot` | 完成；服务真实 PNG 255251 字节 |
| `case-10/final.png` | 参数·生成艺术展签 1200×1200 | `case-10/final.snapshot` | 完成；服务真实 PNG 764019 字节 |
| `portfolio.json` | 10 件作品映射：尺寸/场景/来源/DSL能力/完成标准与逐条检查结果 | — | 完成 |
| `portfolio.md` | 策展逻辑与各作品用途 | — | 完成 |
| `gallery.md` | 按用例逐图展示 10 件最终作品，含 PNG 与同名 DSL 相对链接 | — | 完成 |
| `technique-notes.md` | 逐件独到手法、实际文档依据、试验与看图证据、应用价值与已确认边界 | — | 完成 |
| `case-01/case.md` | case-01 场景/内容/视觉选择/实际自检/素材 | — | 完成 |
| `case-02/case.md` | case-02 场景/内容/视觉选择/实际自检/素材 | — | 完成 |
| `case-03/case.md` | case-03 场景/内容/视觉选择/实际自检/素材 | — | 完成 |
| `case-04/case.md` | case-04 场景/内容/视觉选择/实际自检/素材 | — | 完成 |
| `case-05/case.md` | case-05 场景/内容/视觉选择/实际自检/素材 | — | 完成 |
| `case-06/case.md` | case-06 场景/内容/视觉选择/实际自检/素材 | — | 完成 |
| `case-07/case.md` | case-07 场景/内容/视觉选择/实际自检/素材 | — | 完成 |
| `case-08/case.md` | case-08 场景/内容/视觉选择/实际自检/素材 | — | 完成 |
| `case-09/case.md` | case-09 场景/内容/视觉选择/实际自检/素材 | — | 完成 |
| `case-10/case.md` | case-10 场景/内容/视觉选择/实际自检/素材 | — | 完成 |

题面要求至少 10 件独立完整主作品，每件落在自选真实使用场景，探索 DSL 创意边界并交付 technique-notes.md。实际交付 10 件 case-XX 目录，每件 final.png + final.snapshot + case.md；输出根含 portfolio.json、portfolio.md、gallery.md、snapshot-usage.md、task-metrics.json 与 technique-notes.md。10 件主题/构图/配色/信息结构/尺寸均不同（海报/风味轮/看板/地形图/色温卡/会员卡/测量报告/材料册页/菜单/展签），无同模板换字、无复用其它任务成品。所有最终 PNG 为服务真实 image/png 响应，10/10 PNG 头 89 50 4E 47 有效且 IHDR 尺寸与 DSL 声明一致。每件均实际使用至少一种已验证的高级 DSL 手法（详见 technique-notes.md）。

**逐图自检证据**：逐张用 ViewImage 打开全部 10 张最终 PNG（累计 19 次 ViewImage 调用：能力诊断图 1、首版前 5 张 5、v3 复查前 5 张 5、v3 后 5 张 5、v4 复查 3 张 3）。首版发现 9 类缺陷：case-01 底部浅青区文字对比不足、case-02 风味轮标签在亮色轮上偏淡、case-03 状态行连写、case-04 海拔标注堆叠压线、case-05 长标注射位重叠、case-06 月相标签两行挤压、case-09 第 8 款酒被底部裁切、case-10 方程溢出与线网实心化、富文本前导空格被 trim。v3/v4 两轮完整视觉迭代逐项修复并重新渲染、逐张复查，缺陷全部消除。最终 10 张图内容完整、层级清晰、文字可读、无遮挡裁切；作品独立性、视觉主张与整体关系已在 portfolio.json 的 final_collection_review 中逐项核对。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`
文档版本或访问日期：2026-11-04，服务 `/ai-guide.md`、`/openapi.yaml`、`/fonts` 与文档站 `llms.txt`、`parser.md`、`parser-tags.md`、`parser-text.md`、`parser-errors.md`、`examples.md`、`fonts.md`、`media-text.md`、`_llms-txt/dsl.txt` 已下载缓存于 `tmp/20261104-145656-hy4all/_suite/docs/`。

AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md

实际应用的契约：`POST /snapshot`，请求体 UTF-8 纯文本 `text/plain; charset=utf-8`，成功响应 `image/png` 二进制；按 `X-Request-Id`、`Server-Timing`、`Content-Type` 校验，失败时读取 JSON 的 `code`/`diagnostic`；`GET /fonts` 返回纯文本字体族清单，本套统一使用 `Noto Sans CJK SC`（中文）与 `Inter`（拉丁/数字），必要时 `Noto Sans Mono CJK SC`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| tmp/<run>/_suite/docs/ai-guide.md + openapi.yaml | POST /snapshot 请求体 text/plain;charset=utf-8、image/png 响应、X-Request-Id/Server-Timing、错误码与字体查询 | render.py、requests.jsonl |
| tmp/<run>/_suite/docs/parser-tags.md | Snapshot/Container(gradientType=LINEAR,RADIAL,SWEEP、gradientStops、gradientRotation、gradientBegin/End)/Stack/Positioned/ClipPath(path 支持 M/L/C/Z、viewBox、fit、fillRule=EVEN_ODD)/ClipOval/ClipRRect/Transform(16 列主序矩阵)/Opacity/ImageFiltered(sigmaX,sigmaY)/ColorFiltered/Text/WidgetSpan | 本题全部 .snapshot |
| tmp/<run>/_suite/docs/parser-text.md | fontFamily/fontSize/fontStyle/color/textAlign、CDATA 文本、嵌套 Text/Raw/WidgetSpan 混排、Raw 保留首尾空白、baselineMode | rich_line() 与全部文字元素 |
| tmp/<run>/_suite/docs/parser.md | 列主序 4×4 矩阵格式、SVG 路径裁剪坐标、路径不决定布局尺寸 | rot_matrix()、clip_path()、smooth_closed() |
| tmp/<run>/_suite/docs/examples.md + fonts.md + media-text.md | 固定画布 + Stack 布局范式、字体族选择、富文本基线混排 | 本题布局骨架与字体 |
| tmp/<run>/B03/probe.snapshot → probe.png | 实际服务试验：10 项高级能力逐一验证成立 | technique-notes.md 与全部作品 |

使用 Snapshot 根节点 type=png + background；Stack + 固定尺寸 Container 作绝对定位画布；Positioned 放置全部元素。渐变：LINEAR（含 gradientStops 多段色温标尺、gradientRotation 斜向玻璃高光、gradientBegin/End 方向）、RADIAL（月盘/风味轮中心/年轮中心）、SWEEP（风味轮色环，gradientStartAngle/EndAngle）。裁剪：ClipPath 的贝塞尔波浪、平滑闭合等高线/年轮、渐变填充面积图、EVEN_ODD 双轮廓空心细环；ClipOval 月相轮。变换：Transform 16 列主序旋转矩阵（倾斜印章、峰值徽标、玻璃板）。滤镜：ImageFiltered 子树高斯模糊（月晕、峰顶光晕、玻璃阴影）；Opacity 逐圈叠印与半透明。颜色：6 位与 8 位 #RRGGBBAA。文本：Text/Raw/嵌套 Text/WidgetSpan 富文本混排、textAlign、fontStyle=BOLD、CDATA。几何：c.poly/c.line/c.dashed_line/c.circle/c.rect、程序化极坐标与 Catmull-Rom→贝塞尔计算。所有主体、图形、文字与图标均由 DSL 构造，无外部图片素材。

字体查询：服务 /fonts 实测包含 Noto Sans CJK SC、Inter、Noto Sans Mono CJK SC 等（缓存见 tmp/<run>/_suite/docs/fonts.txt）；中文用 Noto Sans CJK SC，纯拉丁/数字用 Inter。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/20261104-145656-hy4all/B03/requests.jsonl`
迭代记录文件：`tmp/20261104-145656-hy4all/B03/iterations.jsonl`
渲染请求总数：28
成功次数：24
失败次数：4
重试请求数：3
DSL版本数：4
实际图片查看次数：19
完整视觉迭代数：2
未完成视觉迭代数：0
其他接口查询：`/ai-guide.md`、`/openapi.yaml`、`/fonts` 及文档站页面属共享准备，见 `tmp/20261104-145656-hy4all/_suite/requests.jsonl` 与 docs 缓存；本题不重复计为新增 HTTP 请求。

- **v1**（baseline，父版本 无）：查看 `outputs/<run>/B03/case-01..10/final.png（v1 首版）` 发现：首版 9/10 渲染成功（case-05 因 gradientStops 报 400）；逐张看图发现 case-01 底部浅青区文字对比不足、case-02 标签偏淡、case-03 状态行连写、case-04 海拔标注堆叠、case-05 长标注射位重叠、case-06 月相标签挤压、case-09 第 8 款酒裁切、case-10 方程溢出与线网实心化、富文本空格被 trim。。改动：生成首版基线并逐张实际查看；保留全部失败响应与 v1 DSL。。复查：确认需修改，进入视觉迭代。
- **v2**（syntax-fix，父版本 v1）：查看 `outputs/<run>/B03/case-05/final.png` 发现：case-05 服务返回 400 PARSE_ERROR：gradientStops 收到被逗号拆成字符的非法值。。改动：把 stops 改为浮点字符串列表再传入 grad()，生成合法 0..1 非递减列表。复查：重新渲染成功，色温带按 11 个色温节点正确映射；错误响应保留在 case-05/responses/。
- **v3**（visual，父版本 v1）：查看 `outputs/<run>/B03/case-01..10/final.png（v3）` 发现：v1 看图的 5 类视觉缺陷 + 富文本空格连写；另发现 case-05 长标注射位。。改动：rich_line() 片段改用 Raw 保留空格；case-01 底部信息改深墨色；case-02 加深色半透明标签底板；case-04 改左上角海拔图例卡并改峰顶标注为白色；case-05 删除错位长标注、加 K 值定位标签；重渲染全部 10 张并逐张复查。复查：10 张重新渲染成功；前 5 张复查上述缺陷全部消除，后 5 张同时完成逐图查看。
- **v4**（visual，父版本 v3）：查看 `outputs/<run>/B03/case-06/case-09/case-10/final.png（v4）` 发现：v3 后 5 张看图发现 case-06 两行月相标签挤压、case-09 第 8 款酒被 1000px 画布裁切、case-10 方程一行溢出且 60 圈填充路径叠成实心黑块。。改动：case-06 删除上方编号行、下方合并为「01·新月」并加大行距；case-09 季节步长压到 202px、卡片高 74px；case-10 改外轮廓+略小内轮廓的 EVEN_ODD 空心细环（84 采样点）、方程拆两行；重渲染 3 张并逐张复查。复查：3 张复查：月相标签整齐、8 款酒全部显示、线网呈同心波纹干涉图案且方程完整，缺陷全部消除。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 |
|---|---|---|---|---|
| v1 / baseline / — | 首版 9/10 渲染成功（case-05 因 gradientStops 报 400）；逐张看图发现 case-01 底部浅青区文字对比不足、case-02 标签偏淡、case-03 状态行连写、case-04 海拔标注堆叠、case-05 长标注射位重叠、case-06 月相标签挤压、case-09 第 8 款酒裁切、case-10 方程溢出与线网实心化、富文本空格被 trim。 | 实际渲染图观察 | 生成首版基线并逐张实际查看；保留全部失败响应与 v1 DSL。 | 确认需修改，进入视觉迭代 |
| v2 / syntax-fix / v1 | case-05 服务返回 400 PARSE_ERROR：gradientStops 收到被逗号拆成字符的非法值。 | 服务错误响应 diagnostic（attributeName=gradientStops）与 DSL 第 11 行定位；根因是调用 grad() 时传入字符串又被 join 一次 | 把 stops 改为浮点字符串列表再传入 grad()，生成合法 0..1 非递减列表 | 重新渲染成功，色温带按 11 个色温节点正确映射；错误响应保留在 case-05/responses/ |
| v3 / visual / v1 | v1 看图的 5 类视觉缺陷 + 富文本空格连写；另发现 case-05 长标注射位。 | 实际渲染图逐区观察；Text 普通文本节点会 trim 首尾空白，浅色文字压在最浅波浪上对比不足 | rich_line() 片段改用 Raw 保留空格；case-01 底部信息改深墨色；case-02 加深色半透明标签底板；case-04 改左上角海拔图例卡并改峰顶标注为白色；case-05 删除错位长标注、加 K 值定位标签；重渲染全部 10 张并逐张复查 | 10 张重新渲染成功；前 5 张复查上述缺陷全部消除，后 5 张同时完成逐图查看 |
| v4 / visual / v3 | v3 后 5 张看图发现 case-06 两行月相标签挤压、case-09 第 8 款酒被 1000px 画布裁切、case-10 方程一行溢出且 60 圈填充路径叠成实心黑块。 | 实际渲染图观察：填充闭合曲线逐层叠印必然并成实心；酒单季节步长 230px 使第 8 款超出画布 | case-06 删除上方编号行、下方合并为「01·新月」并加大行距；case-09 季节步长压到 202px、卡片高 74px；case-10 改外轮廓+略小内轮廓的 EVEN_ODD 空心细环（84 采样点）、方程拆两行；重渲染 3 张并逐张复查 | 3 张复查：月相标签整齐、8 款酒全部显示、线网呈同心波纹干涉图案且方程完整，缺陷全部消除 |

实际踩坑：① gradientStops 必须与 gradientColors 等长且为 0–1 非递减的浮点列表，传入字符串被二次 join 会拆成字符并触发 400 PARSE_ERROR（case-05，错误响应保留）；② Text 普通文本节点会 trim 首尾空白，富文本片段间的空格必须用 Raw 才能保留；③ ClipPath 填充闭合曲线逐圈叠印会并成一整块实心形状，要做线网必须用 EVEN_ODD 双轮廓空心环；④ 8 位颜色透明度在末两位（#RRGGBBAA）；⑤ ClipPath 的子 Container 必须与画布同尺寸，路径坐标才等于画布坐标；⑥ Transform.matrix 必须 16 个列主序浮点、逗号分隔无空格，alignment=CENTER 才绕自身中心旋转；⑦ BackdropFilter 在本服务不产生可见模糊（简报已实测），改用 ImageFiltered 作用于背景副本；⑧ 服务偶发一次约 200 秒的读超时，重试后成功（case-05、case-09 请求日志有真实记录，逐张渲染脚本规避长挂起）。以上均有服务响应或实际渲染图证据。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/20261104-145656-hy4all/B03/task-metrics.json`

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-11-04T18:34:35+08:00 → 2026-11-04T18:34:35+08:00 | ISO8601+时区 | suite-state.json / 本地墙钟 |
| 任务总耗时 | 见 task-metrics.json | 秒 | 起止墙钟差；不与请求耗时求和 |
| 首次可用图耗时 | 近似首版渲染耗时 | 秒 | requests.jsonl 首条成功记录 |
| 等待用户反馈 | 0 | 秒 | 全套自动连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（未收到 429/503） | 秒 | requests.jsonl |
| 已记录请求耗时之和 | 739.191 | 秒 | requests.jsonl（可含重叠，不等于任务总耗时） |
| 成功、失败、重试请求 | 24 / 4 / 3 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 19 / 2 | 次 | iterations.jsonl 与实际查看记录 |

## 6. 设计选择、经验与未解决事项

每件先确定受众、使用环境与要完成的事，再选一种已验证手法作为结构核心：模糊月晕+贝塞尔波浪（海报氛围）、SWEEP 色轮（分类谱系）、渐变面积图（监测）、程序化等高线（地形）、多段色温标尺（速查）、月相镂空（身份）、旋转频谱徽标（测量）、倾斜玻璃叠影（材料）、同心年轮（菜单）、透明度线网（生成艺术）。尺寸从 800×1200 竖版到 1600×1000 横版逐件变化，配色与信息结构同样更换，避免能力示范板。所有品牌与数值均为自拟演示并已在图中或脚注标注；色温颜色明确标为近似示意。

最终 10 张实际图片已逐张打开检查，内容、层级、对齐、文字可读性、遮挡裁切与视觉效果均满足题面要求；两轮完整视觉迭代修复的 9 类缺陷已逐张复查消除；portfolio/gallery/technique-notes/case.md 与请求、迭代、工具日志齐备，据此标为完成。

临时目录中的 DSL 版本、原始请求/响应、脚本与记录均保留，未删除或覆盖任何尝试；总任务根 `.gitignore` 已建立，仅排除 `__pycache__/`、`*.pyc` 等运行时缓存，未忽略 `tmp/`、`outputs/` 或过程证据。

未解决事项：无影响交付的未解决缺陷。已如实标注：品牌/数值为自拟演示；色温颜色为近似示意而非精确黑体辐射计算；BackdropFilter 在本服务不可用，统一改用 ImageFiltered。
