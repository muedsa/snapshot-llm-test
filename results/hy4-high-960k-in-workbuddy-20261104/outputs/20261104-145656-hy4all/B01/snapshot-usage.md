# Snapshot 使用情况说明与踩坑记录 — B01

任务ID：B01
任务名称：十张真实场景的炫酷用例
本次运行ID：20261104-145656-hy4all
完成状态：完成
结束原因：十件独立作品全部达成，逐张看图并完成整体最终审查，已知缺陷修复并复查
输出目录：`outputs/20261104-145656-hy4all/B01/`
临时目录：`tmp/20261104-145656-hy4all/B01/`
路径基准：suite_root（记录内本地路径均相对总任务根；Markdown 链接相对本文档）

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `case-01/final.png` | 1600×900 独立作品 · 滨江公园站 · 实时到站信息牌 | `case-01/final.snapshot` | 完成；服务真实 PNG，157950 字节 |
| `case-02/final.png` | 1000×1400 独立作品 · 一滴 DRIP LAB · 手冲配方卡 | `case-02/final.snapshot` | 完成；服务真实 PNG，197551 字节 |
| `case-03/final.png` | 1280×720 独立作品 · ECHO 回声音乐节 · 霓虹电子票 | `case-03/final.snapshot` | 完成；服务真实 PNG，134484 字节 |
| `case-04/final.png` | 1800×520 独立作品 · 城市马拉松 · 配速腕带 | `case-04/final.snapshot` | 完成；服务真实 PNG，92136 字节 |
| `case-05/final.png` | 1080×1080 独立作品 · 台风「海燕」· 路径预警图 | `case-05/final.snapshot` | 完成；服务真实 PNG，206090 字节 |
| `case-06/final.png` | 1080×1080 独立作品 · 巷声唱片 · 黑胶 Now Playing 卡 | `case-06/final.snapshot` | 完成；服务真实 PNG，319957 字节 |
| `case-07/final.png` | 1080×1350 独立作品 · 李奶奶的每周药盒 · 用药提醒 | `case-07/final.snapshot` | 完成；服务真实 PNG，125597 字节 |
| `case-08/final.png` | 1000×1400 独立作品 · 巷口 TAPROOM · 今日酒头黑板 | `case-08/final.snapshot` | 完成；服务真实 PNG，184671 字节 |
| `case-09/final.png` | 1200×1500 独立作品 · 今夜观星 · 猎户座导览卡 | `case-09/final.snapshot` | 完成；服务真实 PNG，236787 字节 |
| `case-10/final.png` | 1200×800 独立作品 · 社区捐书计划 · 渐满的书架 | `case-10/final.snapshot` | 完成；服务真实 PNG，112876 字节 |
| `portfolio.json` | 10 件作品逐一映射尺寸/场景/来源/DSL 能力/完成标准/真实检查证据 | — | 完成 |
| `portfolio.md` | 策展逻辑与十件作品用途 | — | 完成 |
| `gallery.md` | 逐图预览、原 PNG 与同名 .snapshot 离线链接 | — | 完成 |
| `asset-sources.json` | 素材来源与装饰性码说明（本套未使用外部素材） | — | 完成 |
| `snapshot-usage.md` | 文档应用、逐件看图、修改与踩坑、最终审查（finalize.py 生成） | — | 完成 |
| `task-metrics.json` | 墙钟、请求、迭代、看图与用例统计（finalize.py 生成） | — | 完成 |

交付 10 件独立完整主作品（10 张最终 PNG + 10 份同名 final.snapshot，另有 case-*/case.md）。各件主题、使用任务、媒介形制、尺寸、配色、信息结构与视觉隐喻真正不同，不是同模板换文字，也未复用 A 题成品。全部主体由 Snapshot DSL 构造并经真实 open-snapshot 服务渲染，PNG 为服务原始字节（已校验 89 50 4E 47 文件头与 IHDR 尺寸）。自拟品牌/人物/数值在画面内标注为演示数据；装饰性点阵码与条码注明非可扫码。输出根交付 portfolio.json、portfolio.md、gallery.md、snapshot-usage.md、task-metrics.json，另附 asset-sources.json；临时目录保留 plan.md、v1/v2/v3 全部 DSL 版本、build.py/cases.py、每版 requests.jsonl 与原始响应、iterations.jsonl、tool-usage.jsonl、finalize.json、能力冒烟测试图。

**逐图自检证据**：用 ViewImage 逐张打开全部 10 张最终 PNG（共 14 次看图：首版 10 张 + v2 复查 3 张 + v3 复查 1 张）。首版确认 7 张直接通过；case-04/06/10 共发现 3 类缺陷（图例与声明文字重叠、轴孔压标题与唱臂穿栏、进度环压书脊与底部裁切）。v2 修复 case-04/10 并部分修复 case-06；v3 把 case-06 唱臂整体移出右侧文字栏后复查通过。最终整体复查：10 张四 KPI 式信息层级、对齐、留白、遮挡、裁切、文字可读性与图形效果均满足各用例完成标准，portfolio.json 的 30 条 criterion_results 全部 passed。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`
文档版本或访问日期：2026-11-04，服务 `/ai-guide.md`、`/openapi.yaml`、`/fonts` 与文档站 `llms.txt`、`parser.md`、`parser-tags.md`、`parser-text.md`、`parser-errors.md`、`examples.md`、`fonts.md`、`media-text.md`、`_llms-txt/dsl.txt` 已下载缓存于 `tmp/20261104-145656-hy4all/_suite/docs/`。

AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md

实际应用的契约：`POST /snapshot`，请求体 UTF-8 纯文本 `text/plain; charset=utf-8`，成功响应 `image/png` 二进制；按 `X-Request-Id`、`Server-Timing`、`Content-Type` 校验，失败时读取 JSON 的 `code`/`diagnostic`；`GET /fonts` 返回纯文本字体族清单，本套统一使用 `Noto Sans CJK SC`（中文）与 `Inter`（拉丁/数字），必要时 `Noto Sans Mono CJK SC`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| ai-guide.md + openapi.yaml | POST /snapshot、text/plain;charset=utf-8、image/png 二进制、X-Request-Id/错误码、/fonts | render.py / fast_render.py / requests.jsonl |
| reference/parser-tags.md | Snapshot/Container/Stack/Positioned/Text/ClipPath/Transform/Opacity/ImageFiltered/Image 属性与颜色格式 | 10 份 final.snapshot |
| reference/parser-text.md | fontFamily/fontSize/fontStyle/textAlign/letterSpacing、CDATA、嵌套 Text Span | 10 份 final.snapshot 全部文字 |
| guides/examples.md | 固定画布 + ClipPath SVG 路径票券、viewBox/fit 语义 | case-03 票券、case-08 菱形 |
| guides/fonts.md + fonts.txt | 可用字体族与回退 | 全部文字元素 |

根节点 Snapshot(type=png, background) + Stack(alignment=TOP_LEFT, clipBehavior=HARD_EDGE) + 固定尺寸 Container 作画布基准；Positioned 绝对定位全部元素；Container 的 color/borderRadius/border/boxShadow 与 gradientType=LINEAR/RADIAL/SWEEP（含 gradientStops 硬停止、gradientCenter/Radius）实现卡片、渐变与光晕；ClipPath SVG 路径（M/L/Q/C/A、fillRule=EVEN_ODD）实现圆弧仪表、同心环、多边形面积图、螺旋、星形、菱形与票券半圆凹口；Transform(matrix 16 列主序浮点, alignment=CENTER) 旋转唱头与头壳；Opacity 与 8 位 #RRGGBBAA 透明度；ImageFiltered(sigmaX/sigmaY) 高斯光晕；Text/CDATA、fontFamily(Noto Sans CJK SC / Inter / Noto Serif CJK SC)、fontSize、fontStyle、textAlign、letterSpacing、maxLines 与嵌套 Text 富文本 Span；参数化 dot_grid/starfield/qr_matrix/barcode/polyline/wave_band/arc/ring 等生成式几何。全部由 DSL 构造，无外部图片。

字体查询：/fonts 清单（tmp/<run_id>/_suite/docs/fonts.txt）含 Inter、Noto Sans CJK SC、Noto Serif CJK SC、Noto Sans Mono CJK SC、Noto Color Emoji 等；中文用 Noto Sans CJK SC，拉丁/数字用 Inter，编辑性标题用 Noto Serif CJK SC。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/20261104-145656-hy4all/B01/requests.jsonl`
迭代记录文件：`tmp/20261104-145656-hy4all/B01/iterations.jsonl`
渲染请求总数：21
成功次数：14
失败次数：7
重试请求数：6
DSL版本数：3
实际图片查看次数：14
完整视觉迭代数：4
未完成视觉迭代数：0
其他接口查询：`/ai-guide.md`、`/openapi.yaml`、`/fonts` 及文档站页面属共享准备，见 `tmp/20261104-145656-hy4all/_suite/requests.jsonl` 与 docs 缓存；本题不重复计为新增 HTTP 请求。

- **v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B01/case-01/final.png (v1)` 发现：四行到站信息完整可辨：线路徽标 2/4/2/6、方向中英文、终点站、站台、琥珀倒计时 2/5/8/12 MIN 与状态点齐全；五列对齐、无重叠；LED 点阵底纹克制不干扰正文；底部末班车、刷新说明与演示声明完整无裁切。…。改动：生成首版基线并实际 ViewImage 打开。复查：逐项记录；有缺陷的用例进入视觉迭代。
- **v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B01/case-02/final.png (v1)` 发现：风味轮四段弧与「酸72/甜55/醇80/苦35」标签完整，弧长与数值、颜色一致；参数表五行对齐；注水时间轴四阶段（闷蒸/第一段/第二段/收尾）与水量进度条比例正确；风味胶囊、两条演示声明与英文标语完整无裁切。…。改动：生成首版基线并实际 ViewImage 打开。复查：逐项记录；有缺陷的用例进入视觉迭代。
- **v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B01/case-03/final.png (v1)` 发现：霓虹顶条、左右 SVG 半圆凹口、品红/青光晕、装饰点阵码、全息渐变条、条码、票号与竖向虚线撕口均完整；主标题、日期地点、GATE/ZONE/NO. 三组信息分区清晰；底部「不可用于入场」演示声明可见。…。改动：生成首版基线并实际 ViewImage 打开。复查：逐项记录；有缺陷的用例进入视觉迭代。
- **v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B01/case-04/final.png (v1)` 发现：v1 发现底部图例第 5 项「冲刺」与右对齐演示声明重叠；v2 把演示声明移至标题区右上后消除。五段配速色带、海拔面积折线、0–42.2K 公里刻度、六段计时点与五色图例完整对齐，元素未越界、无裁切。…。改动：生成首版基线并实际 ViewImage 打开。复查：逐项记录；有缺陷的用例进入视觉迭代。
- **v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B01/case-05/final.png (v1)` 发现：雷达四个同心环、N/E/S/W 方位与 100–400km 标注、螺旋路径及三处箭头、当前中心橙色光晕、实况五项数值、五级预警色标与白色指示三角、四项影响时间轴均完整；底部演示声明可见。螺旋略超出最外环，按「自雷达范围外…。改动：生成首版基线并实际 ViewImage 打开。复查：逐项记录；有缺陷的用例进入视觉迭代。
- **v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B01/case-06/final.png (v1)` 发现：v1 发现中心轴孔黑点压在「午夜电台」标题中间、唱臂斜线穿过曲目表；v2 上移标签文字让轴孔落在标题与英文副标题之间，但改短后的唱臂仍穿过右侧标题；v3 把唱臂整体移到唱片上方区域（转轴在唱片右上外侧、唱头落于标签上缘）…。改动：生成首版基线并实际 ViewImage 打开。复查：逐项记录；有缺陷的用例进入视觉迭代。
- **v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B01/case-07/final.png (v1)` 发现：7 天 × 早/午/晚 共 21 个网格单元完整，胶囊药丸与「1粒/2粒」剂量可辨；药品对照 A–D 四项颜色/名称/剂量、两条提醒、非医嘱声明与家属电话胶囊完整；大字版在竖版卡片上可读性良好，无错位或裁切。…。改动：生成首版基线并实际 ViewImage 打开。复查：逐项记录；有缺陷的用例进入视觉迭代。
- **v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B01/case-08/final.png (v1)` 发现：双层粉笔边框、衬线标题「巷口 · TAPROOM」、六行酒单（编号圆章、中文名、英文风格、ABV 与 IBU 迷你条、¥价格）对齐完整；HAPPY HOUR 横幅、营业信息、演示声明与星形装饰完整，迷你条比例正确。…。改动：生成首版基线并实际 ViewImage 打开。复查：逐项记录；有缺陷的用例进入视觉迭代。
- **v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B01/case-09/final.png (v1)` 发现：猎户座七颗主星、星座连线与星名、亮星光晕完整；观测条件六项、娥眉月图形与两条观测说明清晰；波浪地平线与「东南地平线」标注、底部深蓝信息条三行文字完整无裁切；非实时天文数据声明可见。…。改动：生成首版基线并实际 ViewImage 打开。复查：逐项记录；有缺陷的用例进入视觉迭代。
- **v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B01/case-10/final.png (v1)` 发现：v1 发现右上 68% 进度环与第一层书脊重叠、环内数字被遮挡、底部演示声明被裁切；v2 把进度环缩小并移到标题区右侧、底部声明上移后全部消除。五层书架的彩色书脊与虚位隐喻成立，四个里程碑（2,000/5,000/6,8…。改动：生成首版基线并实际 ViewImage 打开。复查：逐项记录；有缺陷的用例进入视觉迭代。
- **v2**（visual，父版本 v1）：查看 `outputs/20261104-145656-hy4all/B01/case-04/final.png (v2)` 发现：case-04 底部图例第 5 项「冲刺 40 - 42.2K」与右对齐演示声明文字重叠。。改动：把演示声明移到标题区右上 y=120（腕带上方），图例行独占底部。。复查：重渲染并用 ViewImage 打开 v2 case-04/final.png 复查：重叠消除，六段计时点与五色图例完整。。
- **v2**（visual，父版本 v1）：查看 `outputs/20261104-145656-hy4all/B01/case-06/final.png (v2)` 发现：case-06 中心轴孔黑点压在「午夜电台」标题中间；长唱臂斜线穿过右侧曲目表 A1/A2 行。。改动：标签文字上移（SIDE A cy-108、标题 cy-66、英文副标题 cy+24），让轴孔落在标题与副标题之间；唱臂改短。。复查：重渲染并打开 v2 复查：轴孔遮挡消除，但改短后的唱臂斜线改为穿过右侧「午夜电台」标题，需再修。。
- **v2**（visual，父版本 v1）：查看 `outputs/20261104-145656-hy4all/B01/case-10/final.png (v2)` 发现：case-10 右上 68% 进度环与第一层彩色书脊重叠、环内「68%」被遮挡；底部演示声明 y=790/h=18 超出画布 800 被裁切。。改动：进度环缩小至 r=42 并移到标题区 (1090,76)，大数字框左移到 x=740；底部演示声明上移到 y=776。。复查：重渲染并打开 v2 复查：环与书脊分离、68% 可读，底部声明完整无裁切。。
- **v3**（visual，父版本 v2）：查看 `outputs/20261104-145656-hy4all/B01/case-06/final.png (v3)` 发现：v2 的 case-06 唱臂斜线穿过右侧 NOW PLAYING / 午夜电台标题与 MIDNIGHT RADIO 副标题。。改动：把唱臂整体移到唱片上方区域：转轴 (690,170) 位于唱片右上外侧，唱头落于标签上缘 (490,316)、旋转 -38°；完全避开右侧文字栏。DSL 备份到 tmp v3/。。复查：重渲染并打开 v3 复查：右侧文字栏完全无遮挡，轴孔位置正确；随后整体复查 10 张全部通过。。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 |
|---|---|---|---|---|
| v1 / baseline / — | 四行到站信息完整可辨：线路徽标 2/4/2/6、方向中英文、终点站、站台、琥珀倒计时 2/5/8/12 MIN 与状态点齐全；五列对齐、无重叠；LED 点阵底纹克制不干扰正文；底部末班车、刷新说明与演示声明完整无裁切。… | 实际渲染图目视观察 | 生成首版基线并实际 ViewImage 打开 | 逐项记录；有缺陷的用例进入视觉迭代 |
| v1 / baseline / — | 风味轮四段弧与「酸72/甜55/醇80/苦35」标签完整，弧长与数值、颜色一致；参数表五行对齐；注水时间轴四阶段（闷蒸/第一段/第二段/收尾）与水量进度条比例正确；风味胶囊、两条演示声明与英文标语完整无裁切。… | 实际渲染图目视观察 | 生成首版基线并实际 ViewImage 打开 | 逐项记录；有缺陷的用例进入视觉迭代 |
| v1 / baseline / — | 霓虹顶条、左右 SVG 半圆凹口、品红/青光晕、装饰点阵码、全息渐变条、条码、票号与竖向虚线撕口均完整；主标题、日期地点、GATE/ZONE/NO. 三组信息分区清晰；底部「不可用于入场」演示声明可见。… | 实际渲染图目视观察 | 生成首版基线并实际 ViewImage 打开 | 逐项记录；有缺陷的用例进入视觉迭代 |
| v1 / baseline / — | v1 发现底部图例第 5 项「冲刺」与右对齐演示声明重叠；v2 把演示声明移至标题区右上后消除。五段配速色带、海拔面积折线、0–42.2K 公里刻度、六段计时点与五色图例完整对齐，元素未越界、无裁切。… | 实际渲染图目视观察 | 生成首版基线并实际 ViewImage 打开 | 逐项记录；有缺陷的用例进入视觉迭代 |
| v1 / baseline / — | 雷达四个同心环、N/E/S/W 方位与 100–400km 标注、螺旋路径及三处箭头、当前中心橙色光晕、实况五项数值、五级预警色标与白色指示三角、四项影响时间轴均完整；底部演示声明可见。螺旋略超出最外环，按「自雷达范围外… | 实际渲染图目视观察 | 生成首版基线并实际 ViewImage 打开 | 逐项记录；有缺陷的用例进入视觉迭代 |
| v1 / baseline / — | v1 发现中心轴孔黑点压在「午夜电台」标题中间、唱臂斜线穿过曲目表；v2 上移标签文字让轴孔落在标题与英文副标题之间，但改短后的唱臂仍穿过右侧标题；v3 把唱臂整体移到唱片上方区域（转轴在唱片右上外侧、唱头落于标签上缘）… | 实际渲染图目视观察 | 生成首版基线并实际 ViewImage 打开 | 逐项记录；有缺陷的用例进入视觉迭代 |
| v1 / baseline / — | 7 天 × 早/午/晚 共 21 个网格单元完整，胶囊药丸与「1粒/2粒」剂量可辨；药品对照 A–D 四项颜色/名称/剂量、两条提醒、非医嘱声明与家属电话胶囊完整；大字版在竖版卡片上可读性良好，无错位或裁切。… | 实际渲染图目视观察 | 生成首版基线并实际 ViewImage 打开 | 逐项记录；有缺陷的用例进入视觉迭代 |
| v1 / baseline / — | 双层粉笔边框、衬线标题「巷口 · TAPROOM」、六行酒单（编号圆章、中文名、英文风格、ABV 与 IBU 迷你条、¥价格）对齐完整；HAPPY HOUR 横幅、营业信息、演示声明与星形装饰完整，迷你条比例正确。… | 实际渲染图目视观察 | 生成首版基线并实际 ViewImage 打开 | 逐项记录；有缺陷的用例进入视觉迭代 |
| v1 / baseline / — | 猎户座七颗主星、星座连线与星名、亮星光晕完整；观测条件六项、娥眉月图形与两条观测说明清晰；波浪地平线与「东南地平线」标注、底部深蓝信息条三行文字完整无裁切；非实时天文数据声明可见。… | 实际渲染图目视观察 | 生成首版基线并实际 ViewImage 打开 | 逐项记录；有缺陷的用例进入视觉迭代 |
| v1 / baseline / — | v1 发现右上 68% 进度环与第一层书脊重叠、环内数字被遮挡、底部演示声明被裁切；v2 把进度环缩小并移到标题区右侧、底部声明上移后全部消除。五层书架的彩色书脊与虚位隐喻成立，四个里程碑（2,000/5,000/6,8… | 实际渲染图目视观察 | 生成首版基线并实际 ViewImage 打开 | 逐项记录；有缺陷的用例进入视觉迭代 |
| v2 / visual / v1 | case-04 底部图例第 5 项「冲刺 40 - 42.2K」与右对齐演示声明文字重叠。 | ViewImage 打开 v1 PNG 目视确认：图例第 5 项 x≈1390-1690 与右对齐声明 x=1250-1750 同处 y≈480 | 把演示声明移到标题区右上 y=120（腕带上方），图例行独占底部。 | 重渲染并用 ViewImage 打开 v2 case-04/final.png 复查：重叠消除，六段计时点与五色图例完整。 |
| v2 / visual / v1 | case-06 中心轴孔黑点压在「午夜电台」标题中间；长唱臂斜线穿过右侧曲目表 A1/A2 行。 | ViewImage 目视：轴孔 y=470 与标题盒 442-494 重叠；唱臂线 x=690-1010 覆盖右侧文字栏 x≥760 | 标签文字上移（SIDE A cy-108、标题 cy-66、英文副标题 cy+24），让轴孔落在标题与副标题之间；唱臂改短。 | 重渲染并打开 v2 复查：轴孔遮挡消除，但改短后的唱臂斜线改为穿过右侧「午夜电台」标题，需再修。 |
| v2 / visual / v1 | case-10 右上 68% 进度环与第一层彩色书脊重叠、环内「68%」被遮挡；底部演示声明 y=790/h=18 超出画布 800 被裁切。 | ViewImage 目视：环中心 (1100,160) r=58 与书架 y≈150 起重叠；声明底部 808 > 画布 800 | 进度环缩小至 r=42 并移到标题区 (1090,76)，大数字框左移到 x=740；底部演示声明上移到 y=776。 | 重渲染并打开 v2 复查：环与书脊分离、68% 可读，底部声明完整无裁切。 |
| v3 / visual / v2 | v2 的 case-06 唱臂斜线穿过右侧 NOW PLAYING / 午夜电台标题与 MIDNIGHT RADIO 副标题。 | v2 实际 PNG 目视确认：从右上到左下的斜线必然穿过 x≥760 的右侧文字栏 | 把唱臂整体移到唱片上方区域：转轴 (690,170) 位于唱片右上外侧，唱头落于标签上缘 (490,316)、旋转 -38°；完全避开右侧文字栏。DSL 备份到 tmp v3/。 | 重渲染并打开 v3 复查：右侧文字栏完全无遮挡，轴孔位置正确；随后整体复查 10 张全部通过。 |

已确认踩坑：①本环境出现间歇性 `ssl handshake operation timed out`；共享 render.py 使用 urlopen(timeout=180)，一次失败空耗约 180s，10 张中有 6 张在 v1 阶段触发 7 次失败尝试（重试后成功）。为规避该真实环境问题，修复版改用等价短超时客户端 fast_render.py（timeout=30、同 schema 日志、保存原始请求/响应字节），成功 PNG 仍为服务真实响应。②Text 不做实体解码，含特殊字符须用 CDATA（dsl.cdata() 统一处理）；③Container 的 alignment 才能稳定垂直居中文字，fontSize 不等于行盒高度；④ClipPath 的子 Container 需与画布同尺寸，路径坐标才等于画布坐标（本题 arc/ring/poly 均用绝对画布像素多边形逼近，规避 SVG A 命令 large-arc/sweep 标志的歧义）；⑤绝对定位元素需人工核对边界，case-10 底部声明在 v1 因 y=790、h=18 超出画布 800 被裁切，上移后修复；⑥BackdropFilter 在本实例不产生可见模糊，光晕统一用 ImageFiltered 作用于背景副本实现。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/20261104-145656-hy4all/B01/task-metrics.json`

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-11-04T18:01:13+08:00 → 2026-11-04T18:40:18+08:00 | ISO8601+时区 | suite-state.json / 本地墙钟 |
| 任务总耗时 | 见 task-metrics.json | 秒 | 起止墙钟差；不与请求耗时求和 |
| 首次可用图耗时 | 近似首版渲染耗时 | 秒 | requests.jsonl 首条成功记录 |
| 等待用户反馈 | 0 | 秒 | 全套自动连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（未收到 429/503） | 秒 | requests.jsonl |
| 已记录请求耗时之和 | 1407.598 | 秒 | requests.jsonl（可含重叠，不等于任务总耗时） |
| 成功、失败、重试请求 | 14 / 7 / 6 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 14 / 4 | 次 | iterations.jsonl 与实际查看记录 |

## 6. 设计选择、经验与未解决事项

以「真实使用任务 → 媒介形制 → 信息结构 → 视觉语言」为每件作品的推演顺序：站台到站用深色 LED 点阵与琥珀倒计时，手冲配方用暖纸四象限风味轮与纵向注水时间轴，电子票用霓虹光晕与 SVG 凹口，配速腕带用超宽五色分区带与海拔面积图，台风预警用雷达同心环与螺旋路径，黑胶用同心沟纹与径向标签，用药提醒用大字 7×3 网格与胶囊药丸，酒单用粉笔黑板与 ABV/IBU 迷你条，观星用星点/星座连线/波浪地平线，捐书用「书架渐满」原创隐喻。刻意让十件的尺寸、配色、图形系统与信息结构互不相同，同时覆盖题面列举的Stack/Positioned/Container/ClipPath SVG/Transform/渐变/Opacity/ImageFiltered/富文本等能力。

最终 10 张实际 PNG 已逐张打开检查并完成整体最终审查：内容、数据标注、层级、对齐、留白、遮挡、裁切、文字可读性与图形效果均满足要求；三处已发现缺陷修复并复查消除；10 份 final.snapshot 与 10 张 final.png 一一配对，PNG 文件头与 IHDR 尺寸已校验；附加交付文件齐备。据此标为完成。

临时目录中的 DSL 版本、原始请求/响应、脚本与记录均保留，未删除或覆盖任何尝试；总任务根 `.gitignore` 已建立，仅排除 `__pycache__/`、`*.pyc` 等运行时缓存，未忽略 `tmp/`、`outputs/` 或过程证据。

未解决事项：无。
