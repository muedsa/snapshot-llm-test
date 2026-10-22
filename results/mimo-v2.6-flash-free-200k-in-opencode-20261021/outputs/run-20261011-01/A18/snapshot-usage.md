# Snapshot 使用情况说明与踩坑记录

任务ID：A18
任务名称：守恒对象的三幕视觉叙事
本次运行ID：run-20261011-01
完成状态：完成
结束原因：需求满足并完成视觉自检（全图与400px缩略逐张打开，构图对比后选定并一次修改通过）
输出目录：outputs/run-20261011-01/A18/
临时目录：tmp/run-20261011-01/A18/
路径基准：suite_root（本文件链接相对本文件所在输出目录）

遵循[PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径。Markdown
本地链接相对当前文档。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| three-act-story.snapshot | 最终三幕图完整DSL（21584字节） | 同名 | 完成 |
| three-act-story.png | 服务渲染原图 1600×1000 PNG | 同名 | 完成 |
| story-audit.json | 专用审计JSON（units/nodes/acts/narrative_evidence/checks 全字段） | — | 完成 |
| rationale.md | 三幕感知说明，正文248字（≤300字） | — | 完成 |
| snapshot-usage.md | 本文件 | — | 完成 |
| task-metrics.json | 结构化指标 | — | 完成 |

需求逐项核对（以交付DSL、生成期断言与实际看图为据）：

- **三幕1600×1000**：PIL 解码交付PNG为 (1600,1000)、PNG格式；一张图三张幕卡并排。
- **每幕同15单元**：U01–U15 每幕齐备，5蓝(#2563EB)/5橙(#F59E0B)/5灰(#94A3B8)，
  直径36；`check_story` 逐幕断言ID集合与颜色映射，三幕 unit_count 均=15。
- **每幕同3节点**：N01方形/N02圆形/N03菱形，基准外包框均76×76（菱形=53.740909…
  边长正方形绕自身中心转45°，对角=76），填充同为#0F172A，形状身份跨幕不变
  （identity_basis 见 story-audit.json）。
- **叙事**：第一幕双同心环15线汇于N01单点（扇面≈全圆）＝集中；第二幕同一系统
  三队列收敛于同一N01、间隙8px、N01有限形变96×58＝过载；第三幕15→5×5×5、
  三节点恢复76×76＝重新分配。
- **守恒表达禁令**：单元无增减无缩小（三幕15×36px恒定）；无警告文字、无可读性
  破坏（仅4个文本元素：1总标题+3幕名）；关系由连线/距离/构图/方向/有限形变给出。
- **不重叠、线不遮圆**：逐幕最小单元间隙 28/8/8 px（均>0，未舍入值入审计）；DSL
  发射顺序=连线→节点→单元，全图查看确认所有圆边缘完整。
- **第三幕5/5/5且每组≥2色**：loads={N01:5,N02:5,N03:5}，每组实际3色（蓝橙灰）。
- **关系不能只靠颜色**：三幕单元ID—颜色固定但各组均为混色，归属只能读连线与
  空间分组。
- **两种构图先预览后选一**：preview-a.png（A三联幕）、preview-b.png（B三横幕）
  均为真实1600×1000渲染并逐张查看，选定A完善（选择理由与两处B的弱点记录在
  story-audit.json `composition_selection`；预览存tmp ✓）。
- **全图+400px缩略观看**：均实际打开并记录结论（checks 中 full-canvas-view、
  thumb-400px-view，含查看时间）。
- **story-audit.json**：units/nodes/acts（逐幕中心/颜色/直径/接收节点、节点几何/
  位置/方向/外包框/分配量、形变参数与身份依据）、narrative_evidence（逐幕2条
  实际线索，含图中位置与量值）、checks（守恒/不重叠/第三幕规则/整图与缩略证据
  等9项全passed）齐备。
- **rationale.md ≤300字**：正文非空白字符248，按看图说明感知方式。

无未修复缺陷、无未满足要求。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档版本或访问日期：套件共享缓存抓取于2026-10-11；本题2026-10-19实际阅读/抽取

AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md
实际阅读：沿用本run已真实取得的缓存 [ai-guide.md](../../../tmp/run-20261011-01/_suite/docs/ai-guide.md)
（请求/响应/错误契约），`snap_render.py` 据此实现 POST /snapshot 与错误落盘；本题
4次渲染全部 200 image/png，requests.jsonl 如实记录。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求/响应/错误契约、成功返回图片字节 | 4次渲染；tmp/run-20261011-01/A18/requests.jsonl |
| https://snapshot.muedsa.com/reference/parser-tags/ | **Transform**（matrix列主序4×4、origin、alignment）用于画连线与菱形；Stack（alignment/clipBehavior=NONE 允许旋转线出盒不裁）；Positioned 绝对放置；Container（color/borderRadius/border）；Text（fontSize/fontFamily/textAlign/fontStyle）；SizedBox/Snapshot | 三份构图DSL的全部元素；doc_scan_line.py/doc_scan_line2.py/doc_scan_line3.py 抽取的 Transform 章节原文 |
| https://open-snapshot.muedsa.com/fonts | 字体族清单（[fonts.txt](../../../tmp/run-20261011-01/_suite/docs/fonts.txt)） | 正文/标题 Noto Sans CJK SC（探针验证 → 箭头字形正常） |
| https://snapshot.muedsa.com/reference/enums/ | Alignment（TOP_LEFT）等枚举 | Stack/Transform alignment 取值 |

本题实际使用到的DSL能力（全部经真实渲染验证）：

- **变换**：`Transform matrix` 列主序4×4旋转——线段 = Positioned 起点盒 +
  绕 `origin (0,0) alignment TOP_LEFT` 旋转 atan2(dy,dx)；菱形 = 正方形绕
  `origin (w/2,h/2)` 转45°。探针实测端点与理论值逐像素吻合。
- **布局**：根 `SizedBox 1600×1000` + `Stack alignment=TOP_LEFT
  clipBehavior=NONE`（绝对定位、旋转出盒不裁）+ `Positioned`。
- **装饰**：`Container` 圆角填充（圆=76盒 borderRadius38 的胶囊）、卡片
  `color+borderRadius+border="1 SOLID #E2E8F0"`、线=4px 胶囊条。
- **文本**：`Text` 标题（fontStyle=BOLD、textAlign=CENTER）与幕名（LEFT）。
- **图片来源**：无外部图片；全部图形由DSL构造（题面硬约束）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：tmp/run-20261011-01/A18/requests.jsonl（4条渲染）
迭代记录文件：tmp/run-20261011-01/A18/iterations.jsonl（2条）
渲染请求总数：4
成功次数：4
失败次数：0
重试请求数：0
DSL版本数：3（preview-a、preview-b、three-act-story；另有手写探针
probe-transform.snapshot，不计入叙事DSL版本）
实际图片查看次数：5（探针、预览A、预览B、终稿全图、400px缩略）
完整视觉迭代数：1（A18-it-002）
未完成视觉迭代数：0
其他接口查询：0（本题文档全部复用本run已取得的本地缓存，无新增HTTP）

初看与计数口径：探针+两张预览的生成与查看为基线（A18-it-001），不计改进迭代；
依预览看图修改构图、重渲染终稿并再次查看比较计1次完整视觉迭代；无语法修复、
无失败重试、无用户需求轮次。

| 请求ID / 迭代ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| A18-probe-01 | scripts/probe-transform.snapshot | 2026-10-19T10:32:06.195+08:00，1.297s | 200 image/png | scripts/probe-transform.png | 2026-10-19T10:33+08:00 查看+像素测量：旋转线端点(41,39)-(360,200)≈理论(38,38)-(362,202)、菱形(163,30)-(236,103)≈理论(162,29)-(238,105)、→字形正常 |
| A18-prev-a | gen/preview-a.snapshot | 2026-10-19T10:44:42.807+08:00，2.865s | 200 image/png | gen/preview-a.png | 2026-10-19T10:45:30+08:00 整图查看：三卡轮廓分明、留白均衡，选定 |
| A18-prev-b | gen/preview-b.snapshot | 2026-10-19T10:44:44.716+08:00，1.516s | 200 image/png | gen/preview-b.png | 2026-10-19T10:46:40+08:00 整图查看：第二幕左2/3留白、第一/二幕轮廓差异弱，落选 |
| A18-final-01 | gen/three-act-story.snapshot | 2026-10-19T10:48:13.762+08:00，1.972s | 200 image/png | gen/three-act-story.png | 2026-10-19T10:49:40+08:00 全图逐幕核对通过；2026-10-19T10:51:20+08:00 400px缩略三幕仍可读 |

无未取得的图片；两张预览与终稿、缩略均实际打开查看。交付PNG为服务响应原始
字节（复制后md5逐一相等：PNG 65cc841db92bbdf9d060fcee1bd63a2b、DSL
2a0c9b1266d8f5b121a0652cac06cc83），缩略图仅为查看用临时副本、未替代交付件。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| A18-it-001 / 基线（含能力探针）/ — | Transform 旋转语义与文本溢出行为不可凭空假定 | 探针渲染+像素测量：绕原点旋转的斜线端点与理论逐像素吻合；同一探针里宽度320的文本框把标题裁到「…重新」（Text 默认 overflow=CLIP，实测） | 手写探针DSL先测后用；正式文本框按全宽1.0em/半宽0.5em保守估算并断言（标题760≤1600） | 探针200一次通过；终稿4处文本均完整无裁切 | scripts/probe-transform.snapshot、measure_probe.py、doc_scan_line*.py |
| A18-it-001 / 代码缺陷（渲染前拦截）/ — | 构图A第二幕右队列镜像表达式恒等于x=800，若发射会让右队列与中队列同轴重叠 | 代码复核时发现表达式恒值化；`check_story` 的两两中心距断言会在渲染前失败（重叠即AssertionError） | 改为 x'=1600−x 的直接镜像 | 首次构图检查即全绿（右队列与中队列最小间距92px），未产生带缺陷的渲染 | scripts/a18_layout.py |
| A18-it-002 / 视觉迭代 / preview-a | 预览A三处留白不配平：第一幕环形偏下、第二幕底部空白108px、第三幕底部空白184px且分配通道短 | 看图（整图+区域留白目测）对比卡片内容区(64,182)-(496,926) | 环心 (280,554)→(280,524)；第二幕N01与三队列同步+24px（相对几何不变）；第三幕簇 y=680/724→720/764 | 终稿一次修改通过全部断言；全图+400px缩略复看配平改善、无新问题；**无剩余问题** | gen/three-act-story.snapshot、gen/three-act-story.png、gen/three-act-story-thumb400.png |

本题遇到并已确认的坑：

1. **Text 默认裁切**：文本框宽度不足会直接截断（探针实测截掉「分配」）。对策：
   先量后放——保守宽度估算+生成期断言，终稿无裁切。
2. **旋转必须实测**：Transform 的 matrix 列主序、origin/alignment 组合语义只有
   文档描述，探针以像素测量确认后才批量用于45条连线与3个菱形，避免整图返工。
3. **恒值表达式**：镜像坐标写成冗长算式会被化简成常量，靠“渲染前”的几何断言
   （两两中心距）而非看图兜底。

从文档了解、但本次未触发的注意事项：429限流与Retry-After路径（本题0次发生，
未伪造等待记录）。未确认的原因无（所有结论均有渲染/像素/断言证据）。

## 5. 任务耗时与请求统计

结构化指标文件：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-19T10:31:43.407+08:00 → 2026-10-19T10:58:59.531286+08:00 | ISO8601 含时区 | suite-state 记录起始；结束=task-metrics.json 落盘时刻 |
| 任务总耗时 | 1636.124 | 秒 | 墙钟（起止差）；本任务同日连续执行无中断 |
| 首次可用图耗时 | 22.788 | 秒 | 起始→首个可打开有效图（A18-probe-01 200，10:32:06.195+08:00） |
| 等待用户反馈 | 0 | 秒 | 本题无逐题用户反馈轮次（确认无发生） |
| 限流等待、排队等待 | 0 / null | 秒 | 限流：无429（0）；排队：客户端不可测→null |
| 已记录请求耗时之和 | 7.65（4次渲染：1.297+2.865+1.516+1.972） | 秒 | requests.jsonl；串行请求，与墙钟独立 |
| 成功、失败、重试请求 | 4 / 0 / 0（渲染）；文档0 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 5 / 1（未完成0） | 次 | iterations.jsonl 与逐图查看记录 |

时间戳均为客户端自计时并带时区；服务端未暴露 Server-Timing（→null）。

## 6. 设计选择、经验与未解决事项

**关键设计选择**

1. **先探针后量产**：画线/菱形完全依赖 Transform，一次1.3s探针把矩阵语义、
   文本裁切两个不确定点一次钉死，后续45条连线零返工。
2. **数据驱动的三幕一致性**：单元颜色/ID、节点形状在 `a18_layout.py` 中是
   全局常量，三幕共用同一发射器——“守恒”由结构保证，审计与图同源（审计
   坐标=DSL坐标，未舍入值入档）。
3. **两构图真实预览后择优**：A/B各渲1600×1000实图并查看，按留白均衡与
   轮廓差异度选A，B的落选原因如实入审计，不做事后补造。
4. **关系只走连线与空间**：单元分组刻意混色（每簇3色），颜色无法单独推断
   归属，满足“关系不能只靠颜色推断”。
5. **线不遮圆靠绘制顺序**：连线先于节点与单元入栈（画在下层），几何上不需要
   避让计算，看图确认圆边缘完整。

**可复用经验**

- 任何“程序生成几何+服务渲染”的题，先用最小探针验证画布/变换/文本三类
  不确定性，比直接渲整图便宜一个数量级。
- 两两间距断言（中心距−直径>0）在渲染前就能拦住重叠类缺陷，值得作为默认
  门禁。
- 构图比较题把候选图都存tmp并在审计里记录选型理由，既满足流程要求又可回溯。

**最终图如何满足要求 / 结束依据**

全图与400px缩略两张实看 + 9项 checks（含守恒、不重叠、第三幕5/5/5混色、
线序、文本限制、尺寸）全绿 + 审计与DSL同源，才判定结束；不是渲染成功或
次数达标。

**未解决事项**：无已知影响交付的缺陷；未经验证的要求：无。

**留痕确认**：tmp/run-20261011-01/A18/ 下探针（scripts/probe-*）、两套预览DSL
与渲染（gen/preview-a|b.snapshot+png）、终稿渲染与查看用缩略、全部生成/测量/
复制脚本（scripts/）、请求与迭代日志（requests.jsonl 4条、iterations.jsonl
2条）均保留，无删除或覆盖；400px缩略为查看用临时副本，已标注非交付件。

**.gitignore**：总任务根 [.gitignore](../../../.gitignore) 于套件启动时创建，
本题未改；忽略规则仅 `__pycache__/`、`*.pyc` 等运行时缓存（本题产生过
scripts/__pycache__，按约定不列为证据），tmp/、outputs/ 及全部日志、预览、
探针均不被忽略。
