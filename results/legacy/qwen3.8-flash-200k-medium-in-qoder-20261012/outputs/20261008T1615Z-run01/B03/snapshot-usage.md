# Snapshot 使用情况说明与踩坑记录

任务ID：`B03`
任务名称：用十件作品探索 DSL 的创意边界
本次运行ID：`20261008T1615Z-run01`
完成状态：完成（10/10 件主作品定稿，逐件完成真实看图→改→再渲染→再比较的闭环）
结束原因：需求满足并完成视觉自检（无用户中途改需求，无平台阻塞）
输出目录：`outputs/20261008T1615Z-run01/B03/`
临时目录：`tmp/20261008T1615Z-run01/B03/`
路径基准：`suite_root`（本文内所有 `tmp/…`、`outputs/…` 相对总任务根；本文自身的 Markdown 本地链接相对 `outputs/20261008T1615Z-run01/B03/`）

遵循 [PATHS.md](../../../PATHS.md)：目录、产物、证据与脚本一律用相对路径或目录环境变量，不写盘符、用户目录或 UNC 路径。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应 DSL 或图片 | 完成状态 |
|---|---|---|---|
| `case-01/final.png` | 夜航班门头霓虹效果图 + 施工标注：定稿图（2400×1200，服务原始字节） | `case-01/final.snapshot` | 定稿，提升自 `B03-case-01-v05-20261010T074930Z` |
| `case-01/final.snapshot` | 与该图同源的可复现 DSL（90,531 字符） | `case-01/final.png` | 配对完整 |
| `case-02/final.png` | 「秋声」双日音乐节 Riso 双色海报：定稿图（1080×1528，服务原始字节） | `case-02/final.snapshot` | 定稿，提升自 `B03-case-02-v08-20261010T081848Z` |
| `case-02/final.snapshot` | 与该图同源的可复现 DSL（142,980 字符） | `case-02/final.png` | 配对完整 |
| `case-03/final.png` | AX-3 手电轴测拆解评审图版：定稿图（1600×1000，服务原始字节） | `case-03/final.snapshot` | 定稿，提升自 `B03-case-03-v10-20261010T084749Z` |
| `case-03/final.snapshot` | 与该图同源的可复现 DSL（40,254 字符） | `case-03/final.png` | 配对完整 |
| `case-04/final.png` | 唱片店本周黑胶选碟牌：定稿图（1400×1400，服务原始字节） | `case-04/final.snapshot` | 定稿，提升自 `B03-case-04-v05-20261010T094338Z` |
| `case-04/final.snapshot` | 与该图同源的可复现 DSL（43,508 字符） | `case-04/final.png` | 配对完整 |
| `case-05/final.png` | 独立书店月度书单目录页：定稿图（1200×1600，服务原始字节） | `case-05/final.snapshot` | 定稿，提升自 `B03-case-05-v05-20261010T101833Z` |
| `case-05/final.snapshot` | 与该图同源的可复现 DSL（109,268 字符） | `case-05/final.png` | 配对完整 |
| `case-06/final.png` | 咖啡馆柜台季节菜单：定稿图（1080×1350，服务原始字节） | `case-06/final.snapshot` | 定稿，提升自 `B03-case-06-v05-20261010T104057Z` |
| `case-06/final.snapshot` | 与该图同源的可复现 DSL（40,090 字符） | `case-06/final.png` | 配对完整 |
| `case-07/final.png` | 徒步手册·环线剖面字符画：定稿图（1600×1000，服务原始字节） | `case-07/final.snapshot` | 定稿，提升自 `B03-case-07-v05-20261010T112135Z` |
| `case-07/final.snapshot` | 与该图同源的可复现 DSL（103,052 字符） | `case-07/final.png` | 配对完整 |
| `case-08/final.png` | 观星 App·夜空取景器界面稿：定稿图（1920×1080，服务原始字节） | `case-08/final.snapshot` | 定稿，提升自 `B03-case-08-v05-20261010T132726Z` |
| `case-08/final.snapshot` | 与该图同源的可复现 DSL（145,148 字符） | `case-08/final.png` | 配对完整 |
| `case-09/final.png` | 《裁》文化季刊封面·纸张尺寸特辑：定稿图（1080×1440，服务原始字节） | `case-09/final.snapshot` | 定稿，提升自 `B03-case-09-v07-20261011T055152Z` |
| `case-09/final.snapshot` | 与该图同源的可复现 DSL（81,451 字符） | `case-09/final.png` | 配对完整 |
| `case-10/final.png` | 品牌字系统 Type Specimen·排版参数实测页：定稿图（1080×1920，服务原始字节） | `case-10/final.snapshot` | 定稿，提升自 `B03-case-10-v07-20261011T061612Z` |
| `case-10/final.snapshot` | 与该图同源的可复现 DSL（44,332 字符） | `case-10/final.png` | 配对完整 |

题目要求逐项核对：至少 10 件独立完整主作品 ✔（10 件，媒介/幅面/数据模型/主手法互不重复）；每件落在自选真实使用场景 ✔（受众与使用者要做的事写在各 case.md 与 portfolio.json）；不交只有滤镜名称与小方块的能力示范板 ✔（最抽象的 case-10 也是一页交付文档）；尺寸/文案/数据/几何/效果自检 ✔（逐件 case.md「迭代表」＋运行时 assert＋TextFit 闸门）；所有最终 PNG 为实际服务响应 ✔（`promote.py` 用 md5 指纹确认成品字节＝该请求原始响应，final.snapshot 从同一请求的 body 留痕切出）；另交付 `technique-notes.md` ✔；`portfolio.json`/`portfolio.md`/`gallery.md`/`task-metrics.json` ✔。未满足项：无。

## 2. 文档阅读与实际使用的能力

服务基地址（以总 run-config 为准）：`https://open-snapshot.muedsa.com`
文档站：`https://snapshot.muedsa.com/`；AI 使用指南：`https://open-snapshot.muedsa.com/ai-guide.md`
访问日期：2026-10-10（本题 4 次直接抓取）与 2026-10-08（套件共享 15 次抓取，含本指南、文档站各页与 `GET /fonts`）

请求格式按指南执行：`POST /snapshot`，UTF-8 纯文本 body（`<Snapshot …>…</Snapshot>`），无 API key；响应检查按 Content-Type 判定 `image/png` 或错误 JSON，并按 Content-Length 校验完整性（case-07 v03 的截断即由此发现）；错误处理保留 400/500 报文原文不删。字体查询用 `GET /fonts`：实际 27 族，`Inter` 各字重在列，`IBM Plex Mono`／`Courier New`／`Helvetica` 不在列，清单缓存在 `tmp/20261008T1615Z-run01/_suite/docs/fonts.txt`。

| 实际阅读的文档页（缓存文件） | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| `tmp/20261008T1615Z-run01/_suite/docs/backdrop-filter.html.txt` | 命中 `BackdropFilter`：HUD 毛玻璃标签与属性 | case-08 |
| `tmp/20261008T1615Z-run01/_suite/docs/clip-rect.html.txt` | 命中 `ClipRect`：可用的矩形遮罩标签（无 ClipPath 时的替代） | case-03、case-09 |
| `tmp/20261008T1615Z-run01/_suite/docs/color-filtered.html.txt` | 命中 `ColorFiltered`：ColorFiltered 只过滤子树自身像素、不与背景混合（因此双色叠印必须显式乘算） | case-02 |
| `tmp/20261008T1615Z-run01/_suite/docs/container.html.txt` | 命中 `IndexedStack`：IndexedStack 作为分页容器的依据 | case-08 |
| `tmp/20261008T1615Z-run01/_suite/docs/container.html.txt` | 命中 `borderRadius`：圆形遮罩与端面的圆角半径 | case-08 |
| `tmp/20261008T1615Z-run01/_suite/docs/container.html.txt` | 命中 `clipBehavior`：Container 自带裁剪属性（实测对整幅子树 400 Check failed） | case-09 |
| `tmp/20261008T1615Z-run01/_suite/docs/container.html.txt` | 命中 `transformAlignment`：各窗口绕自身中心旋转的属性来源 | case-09 |
| `tmp/20261008T1615Z-run01/_suite/docs/enums.html.txt` | 命中 `CENTER`：transformAlignment 枚举取值 | case-09 |
| `tmp/20261008T1615Z-run01/_suite/docs/fonts.txt` | 命中 `DejaVu Sans Mono`：渲染服实际安装字族（等宽块字符可行性依据） | case-07 |
| `tmp/20261008T1615Z-run01/_suite/docs/fonts.txt` | 命中 `Inter`：服务端实际 27 族清单，含 Inter 各字重 | case-10 |
| `tmp/20261008T1615Z-run01/_suite/docs/image-filtered.html.txt` | 命中 `sigmaX`：ImageFiltered 固定高斯模糊并按 sigma 自动外扩边界（辉光不被文字盒子截断的依据） | case-01 |
| `tmp/20261008T1615Z-run01/_suite/docs/layout.html.txt` | 命中 `Row`：行/列布局能力边界，决定用 Positioned 逐段铺引导点 | case-05 |
| `tmp/20261008T1615Z-run01/_suite/docs/painting.html.txt` | 命中 `boxShadow`：boxShadow 属性能写在哪些绘制装饰上（实测其模糊不跟随 borderRadius） | case-01 |
| `tmp/20261008T1615Z-run01/_suite/docs/painting.html.txt` | 命中 `gradientType`：SWEEP/RADIAL 渐变的取值与语义 | case-03 |
| `tmp/20261008T1615Z-run01/_suite/docs/parser-errors.html.txt` | 命中 `Attr`：400 报文里 Attr [...] 类错误的形态与含义（gradientRadius 对 SWEEP 无效那次） | case-04 |
| `tmp/20261008T1615Z-run01/_suite/docs/parser-tags.html.txt` | 命中 `STROKE`：foregroundMode 的枚举取值 | case-02 |
| `tmp/20261008T1615Z-run01/_suite/docs/parser-tags.html.txt` | 命中 `fontFamily`：字族回退写法 | case-07 |
| `tmp/20261008T1615Z-run01/_suite/docs/parser-tags.html.txt` | 命中 `foregroundMode`：描边字属性在标签/属性总表里的定义 | case-02 |
| `tmp/20261008T1615Z-run01/_suite/docs/parser-tags.html.txt` | 命中 `gradientStartAngle`：起始角属性（用非负弧度最稳） | case-04 |
| `tmp/20261008T1615Z-run01/_suite/docs/parser-tags.html.txt` | 命中 `gradientStops`：硬色标写法（扇区图的构造基础） | case-04 |
| `tmp/20261008T1615Z-run01/_suite/docs/parser.html.txt` | 命中 `CDATA`：块字符与符号需要 CDATA 包裹的原因 | case-07 |
| `tmp/20261008T1615Z-run01/_suite/docs/positioned.html.txt` | 命中 `Positioned`：绝对定位属性 | case-05、case-08 |
| `tmp/20261008T1615Z-run01/_suite/docs/rich-text.html.txt` | 命中 `WidgetSpan`：行内嵌入 widget 的合法性依据 | case-06 |
| `tmp/20261008T1615Z-run01/_suite/docs/text.html.txt` | 命中 `fontFeatures`：高级字体特性（实测只解析不应用） | case-10 |
| `tmp/20261008T1615Z-run01/_suite/docs/text.html.txt` | 命中 `height`：行高属性（实测＝字号×倍数） | case-10 |
| `tmp/20261008T1615Z-run01/_suite/docs/text.html.txt` | 命中 `letterSpacing`：文本属性表（行内字距与引导线间距反算） | case-05、case-10 |
| `tmp/20261008T1615Z-run01/_suite/docs/text.html.txt` | 命中 `textAlign`：价格右对齐与多栏文本对齐 | case-06 |
| `tmp/20261008T1615Z-run01/_suite/docs/text.html.txt` | 命中 `wordSpacing`：词距属性（实测只对空格生效） | case-10 |
| `tmp/20261008T1615Z-run01/_suite/docs/transform.html.txt` | 命中 `transform`：transform 矩阵写法与 transformAlignment | case-01、case-03 |
| `tmp/20261008T1615Z-run01/_suite/docs/widgets.html.txt` | 命中 `WidgetSpan`：widget 清单中的行内组件 | case-06 |
| `tmp/20261008T1615Z-run01/_suite/docs/ai-guide.md`、`tmp/20261008T1615Z-run01/_suite/docs/fonts.txt` | 请求格式、响应检查与可用字族 | 全部十件的渲染与字体选择 |

实际使用的能力（只列真正出现在定稿 DSL 里的）：绝对布局 `Positioned`（合计 4,498 处）、`Container` 色块/渐变/圆角/阴影/边框（4,394 处）、`Text` 字号·字重·`fontStyle`·`letterSpacing`·`wordSpacing`·`height`·`overflow`·`foregroundMode` 描边·`textShadow`·`WidgetSpan`（1,319 处文本节点）、`ClipRRect`/`ClipOval` 遮罩、`BackdropFilter`、`IndexedStack`、`<Raw>` 与 CDATA、仿射 `transform`＋`transformAlignment` 旋转/斜切、`ImageFiltered` 高斯模糊（12 处）。**未使用任何 `<Image>` 外部素材**：十件定稿 DSL 的 `<Image>` 计数均为 0。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/20261008T1615Z-run01/B03/requests.jsonl`（追加式，含失败与重试）
迭代记录文件：`tmp/20261008T1615Z-run01/B03/iterations.jsonl`（追加式）；B 赛道另 `tmp/20261008T1615Z-run01/B03/tool-usage.jsonl`

| 指标 | 值 | 说明 |
|---|---|---|
| 渲染请求总数 | 131 | kind=render 的 HTTP 请求，含探针 |
| 成功次数 | 108 | HTTP 200 且响应体完整且无 error_summary |
| 失败次数 | 27 | 400 20 次、500 2 次、传输层无响应 4 次、截断 1 次 |
| 重试请求数 | 4 | 同版本号重复请求，全部为传输层故障重试 |
| DSL 版本数 | 64 | 十件各自的 vNN 去重；另有 63 次探针请求（40 份探针 DSL 缓存在 tmp 下）不计入作品版本 |
| 实际图片查看次数 | 60 | iterations.jsonl 中 image_viewed=true |
| 完整视觉迭代数 | 50 | 已看图＋有父版本＋改后重渲并再比较 |
| 未完成视觉迭代数 | 2 | 有父版本但本版本未取得可看的图：case-06 v03（400 PARSE_ERROR）、case-07 v03（curl 28 超时两次＋响应体截断）。未看图共 3 条，第三条 case-05 v01 是无父版本的基线，同样因 400（`clipBehavior` 的 Check failed）没有出图 |
| 其他接口查询 | 文档抓取 4 次（本题）＋共享 15 次 | 见 `tmp/20261008T1615Z-run01/_suite/requests.jsonl` |

十件定稿图的真实响应（逐条可在 requests.jsonl 复查）：

| 请求ID | 输入 DSL（tmp） | 起止时间与耗时 | HTTP 与 Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| `B03-case-01-v05-20261010T074930Z` | `tmp/20261008T1615Z-run01/B03/case-01/requests/B03-case-01-v05-20261010T074930Z.body.txt` | 07:49:30 → 07:49:39，8.546s | 200，image/png，523,879 字节 | `outputs/20261008T1615Z-run01/B03/case-01/v05-preview.png` | 2026-10-10T07:51:25 已看图：qa-v05-ground.png 确认倒影成柔和拖尾，判定定稿并提升为 final.png/final.snapshot |
| `B03-case-02-v08-20261010T081848Z` | `tmp/20261008T1615Z-run01/B03/case-02/requests/B03-case-02-v08-20261010T081848Z.body.txt` | 08:18:48 → 08:18:52，4.438s | 200，image/png，411,808 字节 | `outputs/20261008T1615Z-run01/B03/case-02/v08-preview.png` | 2026-10-10T08:21:33 已看图：HTTP 200，411808 字节；提升为 final.png/final.snapshot，md5 4eb553677d86a97cd3a53cde1e047f53 |
| `B03-case-03-v10-20261010T084749Z` | `tmp/20261008T1615Z-run01/B03/case-03/requests/B03-case-03-v10-20261010T084749Z.body.txt` | 08:47:49 → 08:47:53，3.813s | 200，image/png，365,661 字节 | `outputs/20261008T1615Z-run01/B03/case-03/v10-preview.png` | 2026-10-10T08:47:49 已看图：HTTP 200，365661 字节；提升为 final.png / final.snapshot，md5 122bc613545426cae8bbb31d221a6a61 |
| `B03-case-04-v05-20261010T094338Z` | `tmp/20261008T1615Z-run01/B03/case-04/requests/B03-case-04-v05-20261010T094338Z.body.txt` | 09:43:38 → 09:43:43，4.922s | 200，image/png，443,793 字节 | `outputs/20261008T1615Z-run01/B03/case-04/v05-preview.png` | 2026-10-10T09:47:09 已看图：HTTP 200，443793 字节；qa-v05-sum.png 三段完整；提升为 final.png / final.snapshot，md5 22c9f0f14a0854702a969ccb5187cef2 |
| `B03-case-05-v05-20261010T101833Z` | `tmp/20261008T1615Z-run01/B03/case-05/requests/B03-case-05-v05-20261010T101833Z.body.txt` | 10:18:33 → 10:18:38，5.031s | 200，image/png，363,312 字节 | `outputs/20261008T1615Z-run01/B03/case-05/v05-preview.png` | 2026-10-10T10:22:53 已看图：HTTP 200，363312 字节；提升为 final.png / final.snapshot，md5 4939d0f719dc71094f126b2bab0c9522 |
| `B03-case-06-v05-20261010T104057Z` | `tmp/20261008T1615Z-run01/B03/case-06/requests/B03-case-06-v05-20261010T104057Z.body.txt` | 10:40:57 → 10:41:00，3.687s | 200，image/png，356,102 字节 | `outputs/20261008T1615Z-run01/B03/case-06/v05-preview.png` | 2026-10-10T10:44:24 已看图：HTTP 200，356102 字节；qa-v05-pour.png 见「花香/…」省略号，qa-v05-legend.png 见 A/B/C/D 角标与 1/2/3 点分档；final md5 f283c897014eb4388a83d6c047e0ef8e |
| `B03-case-07-v05-20261010T112135Z` | `tmp/20261008T1615Z-run01/B03/case-07/requests/B03-case-07-v05-20261010T112135Z.body.txt` | 11:21:35 → 11:21:45，9.750s | 200，image/png，250,888 字节 | `outputs/20261008T1615Z-run01/B03/case-07/v05-preview.png` | 2026-10-10T11:27:35 已看图：HTTP 200，250888 字节；qa-v05-leftaxis.png 见两者分离、块字符无缝铺满；final md5 613c62240381c1716ea4f0c69be6d0f2 |
| `B03-case-08-v05-20261010T132726Z` | `tmp/20261008T1615Z-run01/B03/case-08/requests/B03-case-08-v05-20261010T132726Z.body.txt` | 13:27:26 → 13:27:30，4.672s | 200，image/png，277,222 字节 | `outputs/20261008T1615Z-run01/B03/case-08/v05-preview.png` | 2026-10-10T13:36:02 已看图：PIL 扫 x=200 列：标尺线 y=639-640、说明 659-688、10° 轴文字 713-730，三段分离；TextFit 83 节点 0 问题。定为 final（md5 6ad124d93af65cb0b9ac59e4d8c2daea） |
| `B03-case-09-v07-20261011T055152Z` | `tmp/20261008T1615Z-run01/B03/case-09/requests/B03-case-09-v07-20261011T055152Z.body.txt` | 05:51:52 → 05:51:58，6.250s | 200，image/png，574,085 字节 | `outputs/20261008T1615Z-run01/B03/case-09/v07-preview.png` | 2026-10-11T05:55:53 已看图：七级窗口全部在拼贴框内、标签 7/7 放出、√2 三要素齐备、要目与条码区不与拼贴相接；定为 final（md5 db674fd69dabb439365c707a924ff333） |
| `B03-case-10-v07-20261011T061612Z` | `tmp/20261008T1615Z-run01/B03/case-10/requests/B03-case-10-v07-20261011T061612Z.body.txt` | 06:16:12 → 06:16:21，9.281s | 200，image/png，490,715 字节 | `outputs/20261008T1615Z-run01/B03/case-10/v07-preview.png` | 2026-10-11T06:20:18 已看图：定为 final（md5 8c45a6f544868168be9addf23ab54f4e，promote.py 字节指纹校验通过） |

失败与异常的留证（不删、不改写；次数与请求 ID 由 requests.jsonl 全量分组算出）：

| 现象（错误签名） | 次数 | 典型请求 | 处理方式 |
|---|---|---|---|
| `Check failed` | 10 | `B03-case-05-v01-20261010T095039Z`、`B03-probe-leader-a-20261010T095140Z` | 确认 `Container` 的 `clipBehavior` 对该写法不可用，改用 ClipRRect/ClipOval 或去掉该属性 |
| `Attr [gradient` | 4 | `B03-probe-04-sweep-mirror-20261010T071754Z`、`B03-probe-10-blend-a-20261010T071811Z` | 去掉 SWEEP 不支持的 `gradientRadius`，起始角改非负弧度 |
| `no response body` | 4 | `B03-case-07-v03-20261010T110804Z`、`B03-case-07-v03-20261010T110832Z` | 按 `--retries 3` 重试；提升脚本只取同名记录里最后一次 200 |
| `INTERNAL_ERROR` | 2 | `B03-probe-15-shadow-modes-20261010T071823Z`、`B03-probe-15d-shadow-ring-20261010T071933Z` | 保留报文，改实现路径（外扩光晕不再走 shadow） |
| `Attr [border` | 2 | `B03-case-08-v01-20261010T125437Z`、`B03-case-08-v01b-20261010T125608Z` | 按属性表回退写法（描边与圆角不同时出现在该元素上） |
| `Unknown ele` | 1 | `B03-probe-03-clippath-20261010T071752Z` | 删除自造标签，改用文档内标签组合 |
| `Tag Contain` | 1 | `B03-probe-01c-persp-grid-20261010T072157Z` | 改为文档写法 |
| `Attr [decor` | 1 | `B03-probe-through2-20261010T095519Z` | 装饰属性回退到已支持项 |
| `Unexpected ` | 1 | `B03-case-06-v03-20261010T103840Z` | 正文里的 `<` 走 CDATA/实体处理（已在 b03kit.tlab 内统一） |
| `truncated response body` | 1 | `B03-case-07-v03-20261010T110900Z` | 按 Content-Length 校验拒绝落盘，不写成品、不看图，重打后定稿 |

## 4. 修改记录与踩坑

初次生成与查看计为基线（`type=baseline`，11 条），不计为改进迭代；下表为 iterations.jsonl 全量 63 条，按件分组，「问题或现象」列即当时看图所见。「原因及确认依据」在各件 `case.md` 的看图证据小节，未确认的原因不写。

### case-01

| 迭代ID／类型／父版本 | 问题或现象 | 采取的修改 | 前后对比与验证结果 | 相关临时文件 |
|---|---|---|---|---|
| `case-01-v01`／baseline／— | 初版自检：主标三层 textShadow 的大 sigma 阴影被文字排版矩形裁成方形光板（qa-sign.png）；月牙 boxShadow 光晕呈方角且遮挡圆与天空有色差；右侧页码框 130px 把 41.0 m／670 W、雨棚宽×出挑截断换行；窗内深色标签在暖光上不可读 | 按 PLAN.md 手法出首版：几何换算标注 + 霓虹三层阴影 + ClipOval 月牙 | 2400×1200 真实响应 448800 字节，判定需视觉迭代 | `outputs/20261008T1615Z-run01/B03/case-01/v01-preview.png` |
| `case-01-v02`／visual／case-01-v01 | v01 看图确认方板光晕与月牙方角光晕、标注截断 | 新增探针 20 对比后改用 K.neon_if（三层 ImageFiltered 模糊 + 芯层）；月牙光晕改 RADIAL 透明边渐变并置于遮挡圆之上；天空环境光下移到 y>=300 使遮挡圆与天空同色；窗内暖光改 gradientRad | 主标呈真霓虹、月牙无暗盘、右侧 6 行尺寸全部单行完整 | `outputs/20261008T1615Z-run01/B03/case-01/v02-preview.png` |
| `case-01-v03`／visual／case-01-v02 | v02 看图：立面中下段与地面偏空，雨棚只是一块暗板，缺少夜间门头的环境光 | 营业时间下加一条灯管分隔线（模糊层 + 芯层）；门两侧加壁灯与墙面光洗；雨棚前沿加三层叠色灯管、棚面条纹改细；地面加 9 条竖向霓虹倒影 | 层次更完整，但倒影呈硬边亮柱 | `outputs/20261008T1615Z-run01/B03/case-01/v03-preview.png` |
| `case-01-v04`／visual／case-01-v03 | qa-v04-ground.png：窄渐变条两端虽淡出仍像一排柱子；壁灯光洗顶边生硬；门把提示文字被雨棚前沿灯管压住 | 倒影与光洗改三段渐变（0/0.2/1 两端透明）；门提示下移到 DY+72 | 地面略改善，仍不够松散 | `outputs/20261008T1615Z-run01/B03/case-01/v04-preview.png` |
| `case-01-v05`／visual／case-01-v04 | v04 地面倒影仍呈条状硬边 | 倒影条加宽到 30-48px 并整体套 ImageFiltered sigmaX/Y=10 模糊；门洞地面光池 alpha 59→73 | qa-v05-ground.png 确认倒影成柔和拖尾，判定定稿并提升为 final.png/final.snapshot | `outputs/20261008T1615Z-run01/B03/case-01/v05-preview.png` |

### case-02

| 迭代ID／类型／父版本 | 问题或现象 | 采取的修改 | 前后对比与验证结果 | 相关临时文件 |
|---|---|---|---|---|
| `case-02-v01`／baseline／— | TextFit 报 8 项（页眉、舞台副标题、样张注、票价、版本行）；另按 1080×1528 排纵向预算时下部核对栏（BY=1300）与阵容栏底边 1394 重叠 | 重写纵向预算：日轮半径改按像素换算成正圆、压缩标题区、网屏改 38×20、核对栏合并行；加两条机械自检（TextFit 必须 0 项、各栏底边不得越出页脚线） | HTTP 200，415436 字节，render;dur=5212.7；看图发现主视觉上下关系反了 | `outputs/20261008T1615Z-run01/B03/case-02/v01-preview.png` |
| `case-02-v02`／visual／case-02-v01 | wave_lum 用 v>=e1 判「无墨」，方向写反：靛蓝满墨跑到天上，日轮压在下半部读成山；引导线点只填到时间盒左沿，与时间文字之间留 47px 空洞；两日音乐节却没有演出日信息 | 反转波线判定（v 越大越靠近海面）；引导线延伸到时间文本实际起点；每档演出加 24/25 日期前缀并在栏头标注两日分组数 | HTTP 200，415929 字节；主视觉关系正确，但日轮顶部被网格上界切平 | `outputs/20261008T1615Z-run01/B03/case-02/v02-preview.png` |
| `case-02-v03`／visual／case-02-v02 | SUN_R_PX=216 时圆心 y=346→顶边 89 < 网格上界 128，日轮被切平；奇偶错格行最后一列有半个点悬出右边界；海面下半部一片满墨，读不出「潮线」 | 半径改 196、圆心 v=0.42；b03kit.overprint 错格行少画一列；波线下移并补一条版心下线；时间盒宽按 TextFit.SLACK 补偿，TextFit 回到 0 项 | HTTP 200，392235 字节；日轮完整、边界干净，但第一色水面倒影在满墨海面上完全读不出 | `outputs/20261008T1615Z-run01/B03/case-02/v03-preview.png` |
| `case-02-v04`／visual／case-02-v03 | 叠印色 #0A1073 与满墨靛蓝 #0A3AA6 明度接近，A×B 水道不可辨；涟漪带 42% 网点太碎，读成随机散点 | 新增 refl_lum 倒影带（以日轮中心为轴、越深越宽越淡并被细波纹打断）；涟漪带提到 55%；核对栏面积率并为单行并新增「口径」定义行 | HTTP 200，403606 字节；叠印格数升到 126，但视觉上仍分不出 | `outputs/20261008T1615Z-run01/B03/case-02/v04-preview.png` |
| `case-02-v05`／visual／case-02-v04 | 海面减淡幅度不足（底部仍约 58% 网点），叠印路径缺少可对比的纸白 | 海面改为随深度线性减淡的色调坡（近岸满墨→底部约 58%） | HTTP 200，413676 字节；海面出现明度坡，但水道仍偏弱 | `outputs/20261008T1615Z-run01/B03/case-02/v05-preview.png` |
| `case-02-v06`／visual／case-02-v05 | 叠印对比仍不足 | 倒影强度提到 0.88 起并按深度衰减；海面 lum=0.10+0.55·depth（近岸 90%→底部 35% 网点） | HTTP 200，405250 字节；2 倍放大核对可见 A×B 深色水道贯穿海面，接受该强度（双色油墨的叠印只能更暗、不能更亮，已在 case.md 记录） | `outputs/20261008T1615Z-run01/B03/case-02/v06-preview.png` |
| `case-02-v07`／visual／case-02-v06 | 二维码下方只有「示意码 · 不可扫描」，没有行动召唤，行人 3 秒决定扫码的任务落空 | 码下补两行：加粗「扫码抢票」＋灰色「示意码 · 不可扫描」 | HTTP 200，407755 字节；版面与读图顺序成立 | `outputs/20261008T1615Z-run01/B03/case-02/v07-preview.png` |
| `case-02-v08`／requirement-change／case-02-v07 | 口径行写「两色之和大于 100% 为正常」，与实际 36.7%+50.0%=86.7% 自相矛盾；D1/D2 已计算却未印出；时间前缀 24/25 缺图例 | 口径行改为可核对定义「面积率＝该色上墨格数/总格数，叠印格两色都计」；栏头补「两日各 6 组」；右上补「时间前缀为演出日」图例 | HTTP 200，411808 字节；提升为 final.png/final.snapshot，md5 4eb553677d86a97cd3a53cde1e047f53 | `outputs/20261008T1615Z-run01/B03/case-02/v08-preview.png` |

### case-03

| 迭代ID／类型／父版本 | 问题或现象 | 采取的修改 | 前后对比与验证结果 | 相关临时文件 |
|---|---|---|---|---|
| `case-03-v01`／baseline／— | 轴测体糊成两大块灰板，几乎占满左半页；右栏零件表的数值列（19.6 g / L 18 mm）整列越出画布右侧；待评审三条压到页脚线 | 首版按 PLAN 生成：2D 仿射基向量拼轴测体 + 零件表/装配顺序/合计/待评审四块 | HTTP 200，275421 字节；缺陷全部记录，进入视觉迭代 | `outputs/20261008T1615Z-run01/B03/case-03/v01-preview.png` |
| `case-03-v02`／visual-fix／case-03-v01 | 体块尺寸正常，但圆柱上下各露出一截端盖（侧面画成竖直 2r 边）；装配轴渲染成一条近水平直线；灯头壳/驱动板浮在装配轴上方（轴贴的是底边） | 矩阵只保留单位基向量、S 只进尺寸；数值列右界改为 W-60-150；加「装后总长」尺寸线与打印幅宽口径 | HTTP 200，308549 字节；剩余缺陷转入 v03 | `outputs/20261008T1615Z-run01/B03/case-03/v02-preview.png` |
| `case-03-v03`／visual-fix／case-03-v02 | 端盖与筒壁不再错开，但筒身仍像平板；所有零件同色，评审时分不出材质；左下大片空白 | 新增 tangent_uv()：对 a×Mv 取极值解出切点，侧面＝两切点连线沿轴拉伸；按材料给顶/右下/左下三色；左下补「投影与读图说明」 | HTTP 200，358484 字节；圆筒轮廓成立，方件仍有问题 | `outputs/20261008T1615Z-run01/B03/case-03/v03-preview.png` |
| `case-03-v04`／visual-fix／case-03-v03 | 方件（灯头壳、驱动板）整体浮在轴上方；反光杯按实心算出 114 g、整机 359 g，与手电量级差一个数量级 | 方件绕装配轴居中；体积乘壁厚折算系数（0.16~0.86）后再乘密度，总质量降到 106.8 g；比例改按 A1 横向 841 mm，爆炸间距 26→40 mm 解拥挤 | HTTP 200，360335 字节；质量量级合理，方件面序仍可疑 | `outputs/20261008T1615Z-run01/B03/case-03/v04-preview.png` |
| `case-03-v05`／visual-fix／case-03-v04 | 尺寸线只标了装后总长，与展开后的图形不对应；重心 198.3 mm 超出装后长度（按爆炸位置加权算错了口径） | 尺寸线改标爆炸展开并括注装后长度；重心改按装后位置累计并加 _u==STACK 断言；说明第 3 条改为「与筒壁相切」 | HTTP 200，367098 字节；本版 TextFit 仍报 rv0 溢出 8 px，保留该次渲染 | `outputs/20261008T1615Z-run01/B03/case-03/v05-preview.png` |
| `case-03-v06`／text-fit／case-03-v05 | 文字溢出修掉后看图：灯头壳顶面与两个侧面之间出现白色缺口，方件像敞口的屋顶 | 收紧待评审 1 的复核口径行宽；把说明第 4 条改为 px→mm 换算 | HTTP 200，365785 字节；缺口未解，怀疑 xform 矩阵语义 | `outputs/20261008T1615Z-run01/B03/case-03/v06-preview.png` |
| `case-03-v07`／visual-fix／case-03-v06 | 缺口仍在；同时发现装配轴在 v06 之前一直是被裁成水平线的（矩阵里把 S 又乘进方向向量） | 方件改画朝向观察者的三个面（u 最大 / v 最大 / w 最大）；装配轴改用 d.line；PC 顶面加深提高与纸色对比 | HTTP 200，368569 字节；面序修正但缺口未消 | `outputs/20261008T1615Z-run01/B03/case-03/v07-preview.png` |
| `case-03-v08`／bug-fix／case-03-v07 | 4× 放大确认：三个面的角点数值彼此吻合，说明是渲染语义而非数据问题；probe-anchor-02 用 120×40 非方形实测出 m=(a,b,tx,c,d,ty) 中局部 x 轴落在 (a,c)，此前按 (cu[0],cu[1],0,cv[0],cv[1],0) 传参等于传了转置 | 新增 b03kit.basis(cu,cv)，face/disc/tube 三处矩阵统一改用它 | HTTP 200，368783 字节；轴测体三个面在角点闭合，缺口消失 | `outputs/20261008T1615Z-run01/B03/case-03/v08-preview.png` |
| `case-03-v09`／visual-fix／case-03-v08 | 尺寸线从「爆炸展开 399.5 mm」文字中间穿过，读图说明第 4 条压在下部分隔线上 | 尺寸线按 CAD 惯例在文字处断成两段（半宽换算成轴向 mm）；说明块补第 4 条落幅换算 | HTTP 200，365650 字节；断线成立，说明块仍需上移 | `outputs/20261008T1615Z-run01/B03/case-03/v09-preview.png` |
| `case-03-v10`／visual-fix／case-03-v09 | 读图说明第 4 条与分隔线仅剩 9 px 重叠，2× 放大可见笔画被线切 | 说明块 664/692→646/674、行距 23→21；新增 BOTTOMS["notes"] <= BY-28 断言常驻生成器 | HTTP 200，365661 字节；提升为 final.png / final.snapshot，md5 122bc613545426cae8bbb31d221a6a61 | `outputs/20261008T1615Z-run01/B03/case-03/v10-preview.png` |

### case-04

| 迭代ID／类型／父版本 | 问题或现象 | 采取的修改 | 前后对比与验证结果 | 相关临时文件 |
|---|---|---|---|---|
| `case-04-v01`／baseline／— | 扇区环与 22 格分钟刻度对齐、12 点钟起播成立；容量表三列 x 坐标重叠（≈22 分压在说明上）、卡片时长列被裁成「21:59 /」、主轴孔压在中心标《夜航西飞》文字上 | 无（首版） | HTTP 200，388458 字节；三处排版缺陷确认，需修 | `outputs/20261008T1615Z-run01/B03/case-04/v01-preview.png` |
| `case-04-v01`／baseline／— | 扇区环与 22 格分钟刻度对齐、12 点钟起播成立；但容量表三列 x 坐标重叠（≈22 分压在说明文字上）、卡片时长列被裁成「21:59 /」、主轴孔压在中心标《夜航西飞》文字上 | 首版基线：SWEEP 成对硬色标扇区环 + 16 圈同心沟槽盘 + 每面容量条 + 极坐标分钟刻度 | HTTP 200，388458 字节；三处排版缺陷确认，必须修 | `outputs/20261008T1615Z-run01/B03/case-04/v01-preview.png` |
| `case-04-v02`／text-fit／case-04-v01 | 改后时长列仍贴边：估算 108 px 通过闸门，实渲约 118 px——等宽字体名回退后字符更宽；沟槽对比转强 | 容量列改 118/84/320 分段；时长列宽 118→140、占比列右移到 RX+444；R_LABEL 80→92 且三行中心标避开圆心 ±14 px；沟槽高光 alpha 3A→5C | HTTP 200，397508 字节；重叠与孔压字均消除，时长列留白仍偏紧 | `outputs/20261008T1615Z-run01/B03/case-04/v02-preview.png` |
| `case-04-v03`／visual-fix／case-04-v02 | A4 扇区标注目视疑似贴左边竖条；沟槽在缩略图上看像色带，需确认是否仍是同心环 | 加 R_RING+3 的 rim 圆盘给扇区环外边界；沟槽色改 #2C333C/#1A1F26；12 点钟加「0:00 起播」标注；CX 412→418 | HTTP 200，436483 字节；PIL 逐行扫描证明 A4 文字像素在 x 65..131、竖条在 44..50 未裁切；qa-v03-groove.png 显示为同心细环 | `outputs/20261008T1615Z-run01/B03/case-04/v03-preview.png` |
| `case-04-v04`／visual-fix／case-04-v03 | 盘面与右栏第 1 张卡的关系要靠猜（图上没说这张盘是谁）；1:1 复核又发现 v01 汇总里的「标价合计」在 v02 拆三段时被挤掉 | 加「本周主打」chip 与「01《夜航西飞》A 面」标签，把盘面显式绑定到第 1 张卡 | HTTP 200，441933 字节；chip 与 0:00 标注、A5 标注互不重叠；总价缺失待补 | `outputs/20261008T1615Z-run01/B03/case-04/v04-preview.png` |
| `case-04-v05`／content-fix／case-04-v04 | 需确认汇总三段文字都不被裁切 | 汇总行补回「标价 ¥1,720」，左段加宽到 600、中段左移到 x 648 | HTTP 200，443793 字节；qa-v05-sum.png 三段完整；提升为 final.png / final.snapshot，md5 22c9f0f14a0854702a969ccb5187cef2 | `outputs/20261008T1615Z-run01/B03/case-04/v05-preview.png` |

### case-05

| 迭代ID／类型／父版本 | 问题或现象 | 采取的修改 | 前后对比与验证结果 | 相关临时文件 |
|---|---|---|---|---|
| `case-05-v01`／syntax-fail／— | HTTP 400 PARSE_ERROR "Check failed"，指向引导线所在的 <Container clipBehavior="HARD_EDGE"> | 不猜测修法，改跑 11 条最小探针（probe-leader-a…p）逐项归因 | 确认 Container 的 clipBehavior 无论有无子节点都 400；纯空格 Text 返回 200 但零像素；错误响应 191 字节已保留 | `B03-case-05-v01-20261010T095039Z` |
| `case-05-v02`／baseline／case-05-v01 | 版面成立：三档线型（点/虚/双）与停印删除线都正确渲染；但引导线起点固定在 250px 列，短书名后留大片空白 | 引导线改为几何节点程序化绘制（b03kit.rule_leader 重写）；停印书名叠加 LINE_THROUGH+DOUBLE | HTTP 200，356993 字节；qa-v02-title-a.png 证实「潮信」「夜航的鲸」后的空洞 | `outputs/20261008T1615Z-run01/B03/case-05/v02-preview.png` |
| `case-05-v03`／visual-fix／case-05-v02 | 引导线紧跟书名后目录节奏正确；新问题：停印行的双线删除线与双线引导线连成一条，「第七个冬天」像被划了 300px；点线偏疏 | 停印一类引导线退回固定列以留出间隔；点距 16→13；补「价格标红＝精装」说明行 | HTTP 200，363360 字节 | `outputs/20261008T1615Z-run01/B03/case-05/v03-preview.png` |
| `case-05-v04`／visual-fix／case-05-v03 | qa-v04-stop-a.png 确认删除线只压在 5 个字上、双线引导线独立成段；整页无遮挡；看图时发现统计带「中位价 ¥72」口径可疑 | 中位数改为偶数样本中间两项均值（另建 MEDIAN_PRICE/MED_TXT，同步 data.json） | HTTP 200，363233 字节 | `outputs/20261008T1615Z-run01/B03/case-05/v04-preview.png` |
| `case-05-v05`／content-fix／case-05-v04 | 需确认统计带数字与 data.json 一致 | 刊头/统计带显示均价 ¥78 / 中位价 ¥70；其余版面不变 | HTTP 200，363312 字节；提升为 final.png / final.snapshot，md5 4939d0f719dc71094f126b2bab0c9522 | `outputs/20261008T1615Z-run01/B03/case-05/v05-preview.png` |

### case-06

| 迭代ID／类型／父版本 | 问题或现象 | 采取的修改 | 前后对比与验证结果 | 相关临时文件 |
|---|---|---|---|---|
| `case-06-v01`／baseline／— | 四件点心行显示「Noneml 杯 · 不含咖啡」；产地句省略号已出现；行内强度点偏高 | 建立 16 项演示菜单：WidgetSpan 过敏原角标 + 行内圆点强度 + ELLIPSIS 豆卡行 | HTTP 200，354425 字节；meta 分支顺序确认为代码缺陷 | `outputs/20261008T1615Z-run01/B03/case-06/v01-preview.png` |
| `case-06-v02`／bug-fix／case-06-v01 | 点心显示「约 380 kcal / 件」正确；行内方块强度点被顶到基线上方、与名字粘连；缺咖啡因分档图例 | 强度点改为几何 d.dot + 字宽估算定位；左面板增加咖啡因三档图例 | HTTP 200，352722 字节；qa-v02-dots.png 确认行内方块偏高 | `outputs/20261008T1615Z-run01/B03/case-06/v02-preview.png` |
| `case-06-v03`／syntax-fail／case-06-v02 | HTTP 400 PARSE_ERROR：Unexpected character '9' in input state [TAG_OPEN]，指向正文中的「<90mg」 | 在 b03kit.tlab 内统一处理：正文含 < 或 > 时包 CDATA（解析器不做实体解码） | 定位到 DSL 第 31569 字符；222 字节错误体已保留 | `B03-case-06-v03-20261010T103840Z` |
| `case-06-v04`／syntax-fix／case-06-v03 | 渲染成功且 CDATA 生效（图例显示 <90mg）；但咖啡因图例三组圆点与标签互相压住 | 标签 x 偏移按点组实际宽度 41px 重排，并加 M+lx+41+lw ≤ M+COL_W-20 断言 | HTTP 200，356228 字节 | `outputs/20261008T1615Z-run01/B03/case-06/v04-preview.png` |
| `case-06-v05`／visual-fix／case-06-v04 | 需 1:1 确认省略号与字母角标真的成立 | 不再改动版面，直接提升为成品 | HTTP 200，356102 字节；qa-v05-pour.png 见「花香/…」省略号，qa-v05-legend.png 见 A/B/C/D 角标与 1/2/3 点分档；final md5 f283c897014eb4388a83d6c047e0ef8e | `outputs/20261008T1615Z-run01/B03/case-06/v05-preview.png` |

### case-07

| 迭代ID／类型／父版本 | 问题或现象 | 采取的修改 | 前后对比与验证结果 | 相关临时文件 |
|---|---|---|---|---|
| `case-07-v01`／baseline／— | 字符画整体成立、无斜切；分段表把零下降写成「−0 m」；路面被阶梯切成一段段方块，读不出连续路线 | 基线；随后用 PIL 实测 amber 连续段：单格墨迹 12px、行右端比按 0.833em 推算的边界短 4.7~14.1px | HTTP 200，244141 字节 | `outputs/20261008T1615Z-run01/B03/case-07/v01-preview.png` |
| `case-07-v02`／visual-fix／case-07-v01 | 零值与图例已修；但方块之间仍有规则空洞，剖面线与字符格存在累积错位 | 叠加真实插值剖面线（d.line 逐段）；图例加底框并补剖面线条目；零下降改「0 m」 | HTTP 200，270968 字节 | `outputs/20261008T1615Z-run01/B03/case-07/v02-preview.png` |
| `case-07-v03`／content-fix／case-07-v02 | 未取得图像：curl (28) SSL/TLS 连接超时，重试 110832Z 同样超时，110900Z 返回 200 但正文只有 149656/279821 字节，脚本按 Content-Length 不符拒绝落盘 | 天空留白加两段括注（最陡段区间、无水源区间），SEGS 补 i/j 索引；未看图故不宣称视觉结论 | 3 次传输失败，保留 3 份请求/响应留痕；该版 DSL 未提升 | `B03-case-07-v03-20261010T110804Z` |
| `case-07-v04`／bug-fix／case-07-v02 | 根因确认：probe-adv 实测 fontSize=20 时 40 个 █ 连续铺满 479px → 前进宽 12.0px＝0.60em，此前 0.833em 结论错误导致每段右端空洞 | CELL_EM 0.833→0.60，横向单元 84→116；advance_source 改引 probe-adv 并作废旧值 | HTTP 200，250576 字节；PIL 复测 5 条路面行左右边界与期望单元格边界全部 ±0~1px（修前 4.7~14.1px） | `outputs/20261008T1615Z-run01/B03/case-07/v04-preview.png` |
| `case-07-v05`／visual-fix／case-07-v04 | 1:1 下最左侧航点名「云谷停车场」与高程轴「800」几乎相压 | 起点航点名改左对齐并从标记右侧起排 | HTTP 200，250888 字节；qa-v05-leftaxis.png 见两者分离、块字符无缝铺满；final md5 613c62240381c1716ea4f0c69be6d0f2 | `outputs/20261008T1615Z-run01/B03/case-07/v05-preview.png` |

### case-08

| 迭代ID／类型／父版本 | 问题或现象 | 采取的修改 | 前后对比与验证结果 | 相关临时文件 |
|---|---|---|---|---|
| `case-08-v01`／baseline／— | 北斗七星 7 个星名标注全部未出现：星点落在 HUD 卡片与准星读数之下，避让函数判冲突后静默跳过；三页面板压在方位带与提示行上；投影视轴与锁定目标强行重合导致低空北斗与北极星无法同框 | 记录失败：视轴/目标分离方案 + 登记面板为 BLOCK + 星点登记为 RESERVED | 同版本另有 2 次 400（border="0" 非法），失败请求与响应留 tmp/<run>/B03/case-08/requests/ | `outputs/20261008T1615Z-run01/B03/case-08/v01-preview.png` |
| `case-08-v02`／structural／case-08-v01 | 视轴改 (344°,20°) 后北斗与北极星同框、8 个标注放出 6 个（天权、摇光仍被跳）；视场外指示条压在 20° 网格线上读不清；页脚第二行贴住罗盘带上边 | 准星读数移到目标左侧、三页面板移进右列、候选偏移避让算法上线；border="0" 改为不输出该属性 | 构图成立，标注密度仍不足，进入 v03 | `outputs/20261008T1615Z-run01/B03/case-08/v02-preview.png` |
| `case-08-v03`／visual-fix／case-08-v02 | 8 个星名标注全部放出、0 跳过，指示条清晰；但天枢的长引线从天权星点旁擦过，归属靠肉眼追；曲线只占面板 2/3 高且「「,」为地平线下」实际无逗号出现 | 候选偏移 12→20 并按标签实际宽度（150/240）算左放位；指示条加深色底垫；页脚与罗盘带留距并加 assert | 标注与指示均可读，遗留归属歧义与面板留白 | `outputs/20261008T1615Z-run01/B03/case-08/v03-preview.png` |
| `case-08-v04`／visual-fix／case-08-v03 | 裁剪复核确认：星点小圈＋从圈边出发的引线消除了 bowl 四星的归属歧义；曲线 11 格填满面板，地下点数改为实算「末 12 点在地下」；罗盘 000° 刻度与数字仍显挤 | 加 22px 星点圈与角度化引线（目标用 95px 准星半径起笔）；NR 7→11；删掉不成立的逗号注记 | 左上 40°×30° 区域仍无任何可用信息，进入 v05 | `outputs/20261008T1615Z-run01/B03/case-08/v04-preview.png` |
| `case-08-v05`／visual-fix／case-08-v04 | 加角距标尺后需确认它与 10° 高度轴文字不相压 | 10° 标尺（11 格、每格 1°、中线加长）＋两行比例说明，并登记进 BLOCK；罗盘刻度改 14/7px、数字下移 4px | PIL 扫 x=200 列：标尺线 y=639-640、说明 659-688、10° 轴文字 713-730，三段分离；TextFit 83 节点 0 问题。定为 final（md5 6ad124d93af65cb0b9ac59e4d8c2daea） | `outputs/20261008T1615Z-run01/B03/case-08/v05-preview.png` |

### case-09

| 迭代ID／类型／父版本 | 问题或现象 | 采取的修改 | 前后对比与验证结果 | 相关临时文件 |
|---|---|---|---|---|
| `case-09-v1`／baseline／— | 150px 描边「裁」与 kicker、主标题撞成一团；hl-sub 排到 x=1080 越出 1040 右边距；左栏开本表数字被拼贴底衬压住；A4/A5/A6 标签全部挤在同一个角；√2 作图太小且标注落在环带内 | 记录失败项：报头重排、副题收宽、标签角位避让、作图放大 | 全图可读但报头与右栏不可用，进入 v02 | `outputs/20261008T1615Z-run01/B03/case-09/v1-preview.png` |
| `case-09-v2`／visual-fix／case-09-v01 | 报头与副题正常、标签分角放出；但 A1 窗口落在 A0 的**上半**，把 A0 标签整个盖住；本地断言 OY−DIAG >= yy+24 失败（742 vs 736） | 报头改 130px 描边＋文字右移；hl-sub 宽 496；作图圆心 OY = yy+DIAG+26 | 风车顺序仍不成立 → 定位到 sub_rect() 的裁半语义写反（y += 0.0 if side=='下' else h） | `outputs/20261008T1615Z-run01/B03/case-09/v2-preview.png` |
| `case-09-v3`／structural／case-09-v02 | 裁半方向修正后拼贴读通（A0 上、A1 左下、A2 右下…）；但每块板仍按 ISO 表竖幅尺寸绘制，落进横幅槽时超出 164px，压住右栏「本辑要目」标题与要目前两行；A6 标签四角全撞，避让算法按设计抛 AssertionError: A6（没有静默丢标签） | sub_rect() 改为 y += h if side=='下' else 0.0、x += w if side=='右' else 0.0；assert 允许长短边互换（容差 0.6px，差值来自标准表取整） | 溢出根因确认在绘制尺寸而非裁半逻辑，进入 v04 | `outputs/20261008T1615Z-run01/B03/case-09/v3-preview.png` |
| `case-09-v4`／visual-fix／case-09-v03 | wall() 按落位槽绘制后拼贴完整内嵌；新缺陷：A3 与 A4 标签同角相撞、A6 三个角相撞，仍触发 AssertionError | 标签候选扩为「角位 × 纵向微调（0/±22/±44/66）」并加一档单行紧凑标签（120×20 / 64×20） | 7 个标签全部放出且互不相交；√2 图放大后内容却不见了，进入 v05 | `outputs/20261008T1615Z-run01/B03/case-09/v4-preview.png` |
| `case-09-v5`／visual-fix／case-09-v04 | PIL 裁剪放大确认三处：① √2 图里正方形与红色对角线**完全看不见**——圆环的内圆是用底色填出来的，后画把先画的盖掉了；② 标签像贴纸压在正文上（A0 首行「纸是有秩序的」被切）；③ A5 深色板配深色标签对比不足 | 圆环改为先画；标签先定位、正文让出标签所在横带（rows 按剩余带高重算并 assert rows>=1）；标签加 2px 纸色描边垫层；角位内缩 6→9px 给旋转留量 | 作图恢复可读、标签不再压字；字数由 A0 552→504、A6 36→12，标签与 data.json 同步 | `outputs/20261008T1615Z-run01/B03/case-09/v5-preview.png` |
| `case-09-v6`／visual-fix／case-09-v05 | 全图与中心群裁剪：标签带纸色描边后在深底上分离清楚，正文让带后无压字；像素级裁剪看到 √2 标签正好被圆环**下弧**穿过（交点处弧落在标签行内），读成「−2」 | √2 标签由「交点居中」改为「交点右侧弧外」（IX+10、宽 40、START 对齐）；docstring 字源字数 288→242 与实算 P_LEN 对齐 | 标签与弧线分离，进入 v07 复核 | `outputs/20261008T1615Z-run01/B03/case-09/v6-preview.png` |
| `case-09-v7`／visual-fix／case-09-v06 | 首试 B03-case-09-v07-20261011T055124Z 失败：curl (28) SSL/TLS connection timeout，http 0、无响应体（render.py 按 --retries 3 自动重试成功）；成品全图复核未见新增缺陷 | 无改动，仅重试渲染 | 七级窗口全部在拼贴框内、标签 7/7 放出、√2 三要素齐备、要目与条码区不与拼贴相接；定为 final（md5 db674fd69dabb439365c707a924ff333） | `outputs/20261008T1615Z-run01/B03/case-09/v7-preview.png` |

### case-10

| 迭代ID／类型／父版本 | 问题或现象 | 采取的修改 | 前后对比与验证结果 | 相关临时文件 |
|---|---|---|---|---|
| `case-10-v1`／baseline／— | 首版按设计没有实测值（全页「待测」）；看图两处缺陷：页眉 82px 描边「Aa」标记压在 v01·2026-10-11·1080×1920 版本号行上；§04 行高只有四栏，缺「不写 height」的默认档，无法证明 height 是乘字号还是乘默认行距 | 标记上移到 y=16/高 86、版本行下移到 y=106；§04 增默认档成五栏并列；同时把 31 条测量带坐标写进 data.json 供扫描 | 版式与留白成立（y_end 1864.5），但埋下位置键隐患 → v02 | `outputs/20261008T1615Z-run01/B03/case-10/v1-preview.png` |
| `case-10-v2`／structural／case-10-v01 | 看图发现 §04 五栏的「实测行距」整体串了一栏：默认档显示待测、1.0 档显示 21、1.25 档显示 26……根因是测量带用位置键 h-0…h-4，插入默认列后键整体右移一位，把上一版 1.25 档的数读成了 1.0 档的数（页面结论因此失真） | 测量带键名改绑参数本身（h-def / h-1 / h-1.25 / h-1.5 / h-1.9）；case10_measure.py 加 --remap 做一次性键名迁移，把 v01 的四个值搬到新键上 | 键名错位是这一页最致命的错误（数字错比没数字更坏），必须重排 §04 → v03 | `outputs/20261008T1615Z-run01/B03/case-10/v2-preview.png` |
| `case-10-v3`／visual-fix／case-10-v02 | §04 新加的两行说明文字压在五栏「行距 …｜预期 …」标题行上，整块重叠不可读；另外 v02 的实测行距（默认 20.8、1.0 16.8、1.25 20.8、1.5 25.8、1.9 31.8）显示默认档只有 1.22em，页面里 1.45em 的估算常数被实测推翻 | 段落框改 valign=TOP 并按实际墨迹高度收拢（BLOCK 110.9→100.6），说明行移到标题行下方并压成一行；§01/§02/§05/§06 行距各收 1px 给说明行腾位 | §04 分块干净可读；QA 2× 裁图另暴露 §07 说明行与页脚横线相撞 → v04 | `outputs/20261008T1615Z-run01/B03/case-10/v3-preview.png` |
| `case-10-v4`／visual-fix／case-10-v03 | qa07-v04.png 放大后看到 §07 红色说明行的下沿正压在页脚横线上，横线又贴着方法注记；四条节末结论行与下一节的编号「02/03/05」之间只剩 2px 视觉空隙 | st-note 盒高 24→26、其后留距 24→32；w/ls/ws/fb 四条 note 各让 2px；§05 结论从「与已安装族都不等」升级为「3、4 两行实测同为 186px」这一更强证据 | 留距正常；但本版生成时漏了测量文件 → v05 成为一次失误记录 | `outputs/20261008T1615Z-run01/B03/case-10/v4-preview.png` |
| `case-10-v5`／process-error／case-10-v04 | 生成器输出 measured 0、TextFit 145 检（应为 161）：本版读不到 case10-measure-v05.json，整页实测列印成「待测」，等于把这一页的立身之本丢了。依闸门输出即判定不可用，未逐张看图（image_viewed=False，不伪造看图记录） | 补上流程：先扫上一版 PNG 产出本版测量文件，再生成本版 DSL；用 v05 的 PNG 与 v05 的 data.json 量出 case10-measure-v06.json | 本版保留为失误证据，不提升、不计入成品；数字与 v04 相同，说明测量口径稳定 | `outputs/20261008T1615Z-run01/B03/case-10/v5-preview.png` |
| `case-10-v6`／gate-fix／case-10-v05 | TextFit 提交前报警：fb-note 估算 2 行 957×28 超出盒子 968×24。2× 裁图看实际渲染并未裁切（估算偏保守），但本套件规定闸门带警不提交 | fb-note 文案收短（估算宽 957→887，回到单行），实测值全部印回 | 闸门归零 → v07 复核 | `outputs/20261008T1615Z-run01/B03/case-10/v6-preview.png` |
| `case-10-v7`／final／case-10-v06 | 全图复核：31 条实测全部印回、五栏行距与结论行分列清楚、§07 与页脚留距正常、底部留白 27px；TextFit 161 检 0 警；未发现新增缺陷 | 无改动 | 定为 final（md5 8c45a6f544868168be9addf23ab54f4e，promote.py 字节指纹校验通过） | `outputs/20261008T1615Z-run01/B03/case-10/v7-preview.png` |

**渲染成功但视觉不符合要求**的问题占多数（描边字与标题相撞、圆环内圆盖掉作图内容、√2 标签被下弧穿过、行内方块顶到基线上方、倒影呈硬边亮柱等），全部由看图发现后修改；另有两类是「看图看不到、由断言拦下」的：case-09 的 A6 标签放不下（AssertionError 中断渲染）与 OY−DIAG 断言（742 vs 736）。

区分「已遇到的问题」与「从文档知道但本次未触发」：以下能力在文档中存在而十件均未使用，因此其行为未经验证——`<Image>` 外部素材与网络图（刻意不用）、`blendMode` 的其他混合模式（探针 10/11/12 三次 400 后放弃整条路线）、透视矩阵项（实测无视觉效果，故不再尝试）、`fontFeatures` 之外的 OpenType 特性、`ClipPath`（服务端无此标签）。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/20261008T1615Z-run01/B03/task-metrics.json`

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-10T07:12:07.469118+00:00 → 2026-10-11T06:16:21.432903+00:00 | UTC ISO | requests.jsonl 首末记录 |
| 任务总墙钟 | 83,054 | 秒 | 首请求至末请求（**不等于连续工作**） |
| 其中有写入证据的活动时长 | 20,508 | 秒 | 墙钟减去空闲 |
| 空闲与无证据区间 | 62,545 | 秒 | 9 段，逐段见 task-metrics.json 的 idle_gaps（含证据与分类） |
| 首次可用图耗时 | 1529.6 | 秒 | 开始到 case-01 v01 响应落盘 |
| 等待用户反馈 | 0 | 秒 | 本题无用户中途反馈 |
| 限流等待／排队等待 | 0／未知 | 秒 | 未触发 429（`x-ratelimit-limit: 120`，最低 remaining 99）；服务端排队不可测 |
| 已记录请求耗时之和 | 1064.96 | 秒 | 客户端端到端（含网络与写盘），与墙钟不可比 |
| 服务端 render 耗时之和 | 111.82 | 秒 | 105 份响应头 Server-Timing（render;dur / total;dur） |
| 服务端 total 耗时之和 | 128.47 | 秒 | 同上响应头 |
| 成功／失败／重试请求 | 108／27／4 | 次 | requests.jsonl |
| 实际看图／完整视觉迭代 | 60／50 | 次 | iterations.jsonl |

空闲区间的分类依据（按文件 mtime 证据，tz-aware 比对）：

| 区间起（UTC） | 时长 | 判定 | 证据 |
|---|---|---|---|
| 2026-10-10T07:22 | 911 秒 | idle-unverified（空闲 911 秒） | 探针 01c 于 07:22:18 落盘后到 07:37:29 首个 case-01 请求之间无任何文件写入，无法证明这段时间在产出，按空闲计 |
| 2026-10-10T07:49 | 1,103 秒 | work（空闲 0 秒） | 该区间内有文件写入 |
| 2026-10-10T08:18 | 655 秒 | work（空闲 0 秒） | 该区间内有文件写入 |
| 2026-10-10T08:47 | 2,649 秒 | work（空闲 0 秒） | 08:48:15 qa-v10-notes.png、08:48:54 提升 case-03 final、08:52:42 case.md、08:53:19 检查点、09:31:58 case04-v01.snapshot：收尾＋下一案开案 |
| 2026-10-10T09:55 | 847 秒 | work（空闲 0 秒） | 09:55:35 probe-through3 探针响应，10:09:03 写出 case05-v02.snapshot |
| 2026-10-10T10:46 | 821 秒 | work（空闲 0 秒） | 10:46:39 probe-block 响应与 1x 裁图，11:00:20 写出 case07-v01.snapshot |
| 2026-10-10T11:21 | 5,572 秒 | partial（空闲 3,492 秒） | 11:22–11:30 为 case-07 收尾（qa 裁图、final、case.md、检查点），11:56:25 写 astro8.py；11:56→12:54 无写入，按空闲计 |
| 2026-10-10T13:27 | 58,141 秒 | idle（空闲 58,141 秒） | 13:28–13:41 完成 case-08 看图裁切、final 提升、case.md、log_case08.py 与检查点；13:41:52 之后到次日 05:36:32 会话未运行（夜间停止），计空闲 |
| 2026-10-11T05:51 | 643 秒 | work（空闲 0 秒） | 05:52–05:56 case-09 提升/case.md/log_case09.py/总状态与检查点，随后编写 case-10 生成器，06:02:42 发出 v01 |

计时来源区分：客户端 `duration_seconds` 由本地计时写入；服务端耗时只取响应头 `Server-Timing`；两者不混用、不相加成「总耗时」。历史快照与检查点在 `tmp/20261008T1615Z-run01/_suite/checkpoints/`。

## 6. 设计选择、经验与未解决事项

关键设计选择与预览的影响：

- 十件的排序按「信息密度能不能扛住放大」而不是按视觉效果排。每件先用一次探针确定服务能不能做这个构造，再决定构图；因此 case-01 的霓虹、case-03 的轴测、case-04 的扇区、case-06 的行内角标都有各自的探针请求在前。
- 预览图（`v*-preview.png`，共 59 张）不只是留痕：每件的修改都由看预览决定，全图看不清的细节再裁局部放大（QA 裁图留在 tmp，不作为交付物）。
- 数字全部由数据模型算出并写在图上（case.md 的「内容真实性」小节逐件声明虚构范围与真实常数），这让「看图→改」能改成算式而不只是审美调整。

可复用经验：

- **测量带**（case-10）：把测量坐标写进 data.json，用 PIL 扫上一版成品 PNG，再把实测值印回下一版——让页面结论来自像素而不是肉眼。键名必须绑定参数本身而不是列位置，否则插一栏就全部串值。
- **确定性生成器**：同参数重跑产出逐字节相同的 DSL（case-10 用这招把 v03 的带坐标恢复出来并 md5 验证）。
- **可证伪探针**：回退字族、`fontFeatures`、`clipBehavior` 这类「看不见」的性质，用一个宽度/状态码探针就能定性，比反复试排版便宜。
- **断言比看图早**：能写成 assert 的几何约束（窗口在带内、标签不越板、累加等于总长）应在生成阶段拦下，失败即不出图，避免把静默丢内容的版本当成成功。
- 行距与字距：默认行距由字族 metrics 决定（Inter 1.22em，非套件原先估的 1.45em）；`letterSpacing` 严格线性、`wordSpacing` 只对空格生效；行内小方块的最小步进约 26px，小于它就会重叠。

未解决事项：

- 服务无矢量 path：曲线、星图轨迹、剖面层形仍靠逐段矩形与折线逼近，放大到印刷尺寸会显出棱角。
- `fontFeatures` 只解析不应用，等宽数字与小型大写需要版式手工兜底。
- `Container` 的 `clipBehavior` 对整幅子树 400，遮罩只能用 ClipRRect/ClipOval。
- 未安装字族回退到同一平台默认字体（186px 同宽），字族清单必须以 `GET /fonts` 实际返回为准。

结束依据：10 件均有真实服务响应的 `final.png` 与同名完整 `final.snapshot`（md5 指纹配对），逐件真实看图并至少完成一轮「看图→改→再渲染→再比较」，合集层面的独立性审查见 `portfolio.json` 的 `final_collection_review`。达到请求/迭代次数本身没有被当成完成依据。

留痕完整性确认：`tmp/20261008T1615Z-run01/B03/` 下保留了 25 份生成器与构件脚本、探针留痕 77 份（DSL 40 ＋图 35）、各案 `requests/` 目录内的原始请求 body 与响应头/响应副本、59 张版本预览、63 张 QA 裁图、5 份测量文件与全部失败响应（400/500/截断/无响应体），未删除、未覆盖任何已有尝试；下载文档缓存与原始响应在 `tmp/20261008T1615Z-run01/_suite/docs/`。运行时缓存（`__pycache__/`、`*.pyc` 等）不属留痕，未列为证据。总任务根 `.gitignore`（相对总任务根即 `.gitignore`，与本文相距 `../../../.gitignore`）已按模板创建并合并：忽略 `__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`，未使用 `tmp/`、`outputs/`、`*.log` 或整体图片/DSL/JSON 的通配规则，产物与过程证据均未被忽略。

## 开放作品集补充

- 逐件场景／内容依据／DSL 能力／最终自检：`portfolio.json`（`cases[]` 每项含 `audience`、`use_context`、`user_goal`、`content_basis`、`dsl_capabilities`、`completion_criteria`、`visual_review`、`request_ids`、`iteration_ids`）。
- 整体策展审查与合集独立性：`portfolio.md` 末节与 `portfolio.json` 的 `final_collection_review`。
- 实际工具贡献：B 赛道工具记录 48 条（`tmp/20261008T1615Z-run01/B03/tool-usage.jsonl`），其中渲染服务、PIL 裁切放大、TextFit 闸门、运行时断言、promote 字节指纹校验为跨件共用；case-01 的 6 条为收尾核对时按请求留痕补记（记录内 `logged_via` 已注明），不冒充当时的即时记录。
- 局部辅助素材：十件均未使用（`supporting_assets` 全为 `[]`，`<Image>` 计数 0）。
- 重复计数避免：每题指标只在题层汇总，shared 的 15 次文档抓取只计入 `_suite`，探针与构件不计入任何单件作品；`task-metrics.json` 的 `counts` 与 `case_metrics` 为同一批记录的不同切面，不相加。
