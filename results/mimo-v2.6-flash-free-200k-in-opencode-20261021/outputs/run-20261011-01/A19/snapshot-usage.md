# Snapshot 使用情况说明与踩坑记录

任务ID：A19
任务名称：构造可核验的视觉题场
本次运行ID：run-20261011-01
完成状态：完成
结束原因：需求满足并完成视觉自检（网格整图+1:1裁片+64对象逐像素核验、
两遮挡图逐张查看并通过RGBA逐像素等价证明）
输出目录：outputs/run-20261011-01/A19/
临时目录：tmp/run-20261011-01/A19/
路径基准：suite_root（本文件链接相对本文件所在输出目录）

遵循[PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径。
Markdown本地链接相对当前文档。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| grid-scene.snapshot | 1600×1600 8×8网格完整DSL（27563字节） | 同名 | 完成 |
| grid-scene.png | 服务渲染原图 1600×1600 PNG | 同名 | 完成 |
| occlusion.snapshot | 遮挡案例A版 DSL（隐藏内容=绿圆+“3”） | 同名 | 完成 |
| occlusion.png | A版服务渲染 800×800 PNG | 同名 | 完成 |
| occlusion-alternative.snapshot | 遮挡案例B版 DSL（隐藏内容=橙圆角方+“8”） | 同名 | 完成 |
| occlusion-alternative.png | B版服务渲染 800×800 PNG | 同名 | 完成 |
| scene-data.json | 种子、64对象真实几何（含实测ID盒）与分布核查 | — | 完成 |
| questions.json | 14题（12网格+2遮挡），不含答案 | — | 完成 |
| answers.json | 14题答案+步骤+关系定义+容差+可见性依据，附17条唯一性断言 | — | 完成 |
| equivalence.json | 两遮挡PNG的SHA-256留痕+解码器/像素逐通道对比结论 | — | 完成 |
| snapshot-usage.md | 本文件 | — | 完成 |
| task-metrics.json | 结构化指标 | — | 完成 |

需求逐项核对（以生成期断言、交付PNG逐像素测量与实际看图为据）：

- **网格**：1600×1600；8×8格、每格恰一彩色主体；G01–G64按行优先（左→右、
  上→下）编号；4色（蓝#2563EB/橙#F59E0B/绿#16A34A/紫#7C3AED）各16、
  4形状（圆/方/圆环/圆角方）各16；每行distinct_colors≥3且
  distinct_shapes≥3（实测8行全部=4）；ID在主体外（64/64实测分离）；
  无外部图像，全部DSL构造。
- **属性覆盖**：16种颜色×形状组合全覆盖（每组合4个）；每种颜色与每种形状
  都出现48/64/80三种尺寸（`color_size_coverage`/`shape_size_coverage` 实测
  均=[48,64,80]）；尺寸频数22/21/21（不要求相等 ✓）；三类属性在
  scene-data.json 的 `distribution` 中列出。
- **圆环**：外径=size、内径=外径一半——探针像素实测80/64/48三环的内孔
  =40/32/24（border画在盒内），交付网格64环逐格目视+颜色采样核验。
- **遮挡对**：A/B两版画布/可见前景/遮挡物/背景/渲染参数一致（DSL除隐藏组外
  逐元素相同）；隐藏差异写入两份DSL及equivalence.json；隐藏内容含阴影
  （boxShadow，实测外扩≤34px），不透明遮挡物最近边距≥56px完全覆盖；
  无任何虚线；指定最终图=网格1+遮挡2=3张 ✓。
- **像素等价**：两版各自解码为8位未预乘RGBA后逐通道全量比较——
  尺寸一致(800×800)、差异像素=0、最大通道差=0、RGBA数组SHA-256相同；
  未合成到白底、未缩放、alpha与透明像素RGB均参与；文件SHA-256也已记录
  （两文件字节恰好也相同）但不作判定依据；两份原始响应PNG均保留。
- **12道网格题**覆盖6类：复合属性检索(Q18,Q19)、严格中心左右(Q20)、
  距离(Q21)、排序(Q22,Q23)、包围框(Q24)、颜色/形状计数(Q25,Q26)，
  另有两步关系题(Q27,Q28,Q29)——标记two_step共**5题≥4题** ✓；
  每题给出比较标准与坐标原点（rule/origin字段+题面文字），排序/并列均有
  显式三级键，程序断言17条全部通过，唯一题无多解。
- **2道遮挡题**：Q30答案=“无法确定”（依据两版可见像素逐通道一致而隐藏
  内容不同）✓≥1题；Q31答案=4（仅可见部分）；两题均只依赖最终可见图，
  未以隐藏对象数量为答案。
- **编号≥18**：题号Q18–Q31（数字部分≥18）；同时题目与答案合计引用25个
  不同对象ID（≥18），两种读法均满足。
- **scene-data.json**含种子（20261019）与算法、64对象行列/颜色/形状/尺寸/
  中心/主体框/ID文字盒（ID盒为对交付PNG的真实像素测量值）、分布核查；
  **questions.json不含答案**；**answers.json**含答案、分步计算、关系定义、
  坐标容差与可见性依据；**equivalence.json**含原始PNG哈希与像素对比。
- **实际看图检查所有目标与标签**：整图(1600×1600)+1:1裁片(800×800)两轮
  视觉查看 + 64对象逐像素测量（颜色采样、主体框±2px、ID文字存在且在主体外）
  = 64/64通过。

无未修复缺陷、无未满足要求。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档版本或访问日期：套件共享缓存抓取于2026-10-11；本题2026-10-19实际抽取阅读

AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md
实际阅读：沿用本run已真实取得的缓存 [ai-guide.md](../../../tmp/run-20261011-01/_suite/docs/ai-guide.md)
（请求/响应/错误契约），`snap_render.py` 据此实现 POST /snapshot；本题5次渲染
全部 200 image/png，requests.jsonl 如实记录。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求/响应/错误契约、成功返回图片字节 | 5次渲染；tmp/run-20261011-01/A19/requests.jsonl |
| https://snapshot.muedsa.com/reference/parser-tags/ | **Container**：border/borderRadius/color/boxShadow/clipBehavior；**Border**：`"宽度 SOLID 颜色"`；**Text**：overflow默认CLIP、textShadow格式、fontSize/textAlign/fontStyle；Stack/Positioned/SizedBox/Snapshot | 三份构图DSL；doc_scan_container.py 与 doc_scan_shadow.py 从本地缓存抽取的 Container/Text/阴影章节原文 |
| 阴影章节（同上） | boxShadow 自定义格式 `x y [blurRadius] [spreadRadius] [color] [blurStyle]`、elevation 名称 | 遮挡隐藏内容 `boxShadow="0 8 24 0 #00000066 NORMAL"`（探针+0差异双重验证） |
| https://open-snapshot.muedsa.com/fonts | 字体族清单（[fonts.txt](../../../tmp/run-20261011-01/_suite/docs/fonts.txt)） | 全部文字 Noto Sans CJK SC（ID、标题、遮挡区、隐藏数字） |
| https://snapshot.muedsa.com/reference/enums/ | Alignment（TOP_LEFT）等枚举 | Stack/Transform alignment 取值 |

本题实际使用到的DSL能力（全部经真实渲染验证）：

- **布局**：根 `SizedBox`（1600×1600 / 800×800）+ `Stack
  alignment=TOP_LEFT clipBehavior=NONE` + `Positioned` 绝对定位。
- **几何/装饰**：`Container` 纯色圆角方、圆（borderRadius=半径的胶囊）、
  圆环（`border="size/4 SOLID 颜色"` 无填充，内径=size/2，**画在盒内**）、
  网格分隔（`border="1 SOLID #E2E8F0"`）、`boxShadow` 隐藏阴影。
- **文本**：`Text`（fontSize/fontFamily/textAlign=CENTER/fontStyle=BOLD/
  textShadow）——ID标签、幕标题、遮挡区标签、隐藏数字。
- **图片来源**：无外部图片；三张图全部由DSL构造（题面硬约束）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：tmp/run-20261011-01/A19/requests.jsonl（5条渲染）
迭代记录文件：tmp/run-20261011-01/A19/iterations.jsonl（2条）
渲染请求总数：5
成功次数：5
失败次数：0
重试请求数：0
DSL版本数：4（grid-scene两版：缺陷v1保留+修复v2、occlusion、
occlusion-alternative；另有手写探针 probe-ring.snapshot 不计入）
实际图片查看次数：6（探针、网格v1、遮挡A、遮挡B、网格v2、1:1裁片）
完整视觉迭代数：1（A19-it-002）
未完成视觉迭代数：0
其他接口查询：0（本题文档全部复用本run本地缓存，无新增HTTP）

初看与计数口径：探针+首批三图的生成与查看为基线（A19-it-001，含发现网格
主体溢出），不计改进迭代；依看图修改→重渲染→再看图并比较计1次完整视觉
迭代（A19-it-002）；无语法修复（探针一次200）、无失败重试、无用户修改轮次。

| 请求ID / 迭代ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| A19-probe-01 | scripts/probe-ring.snapshot | 2026-10-19T11:06:19.606+08:00，3.885s | 200 image/png | scripts/probe-ring.png | 2026-10-19T11:07+08:00 查看+像素测量：三环内孔40/32/24=外径一半（border在盒内）、阴影外扩≤34px、textShadow/G01标签正常 |
| A19-grid-01 | gen/grid-scene.snapshot(v1) | 2026-10-19T11:18:22.212+08:00，1.795s | 200 image/png | gen/grid-scene.png | 2026-10-19T11:18+08:00 整图查看：**主体溢出相邻格**（bbox按w/h解包缺陷），标签与行列正确——记录为待修缺陷 |
| A19-occ-a-01 | gen/occlusion.snapshot | 2026-10-19T11:18:24.113+08:00，1.49s | 200 image/png | gen/occlusion.png | 2026-10-19T11:18+08:00 整图查看：标题栏/四角主体/遮挡板/标签齐全，无虚线无泄漏 |
| A19-occ-b-01 | gen/occlusion-alternative.snapshot | 2026-10-19T11:18:25.334+08:00，0.887s | 200 image/png | gen/occlusion-alternative.png | 2026-10-19T11:18+08:00 整图查看：与A目视一致（差异只在被遮内容） |
| A19-grid-02 | gen/grid-scene.snapshot(v2) | 2026-10-19T11:19:33.406+08:00，1.753s | 200 image/png | gen/grid-scene-02.png | 2026-10-19T11:20+08:00 整图64格逐格核对 + 2026-10-19T11:31+08:00 1:1裁片（crop-tl.png）确认环孔/圆角/尺寸档/ID分离，均合格 |

无未取得的图片；全部5张渲染结果均实际打开查看。交付PNG为服务响应原始字节
（复制后md5逐一核对：grid 09e8efaea6eb990b…、occlusion与alt均为
c0d73658f63d9439…、DSL三份各自md5核对一致），无后处理。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| A19-it-001 / 基线（含能力探针）/ — | 环内径、阴影外扩不可凭空假定 | 探针+像素测量：80/64/48三环内孔实测40/32/24=外径一半，证实border画在盒内；阴影外扩实测≤34px（含dx/dy偏移） | 以实测值设定 `border=size/4` 与遮挡覆盖余量（≥56px） | 探针一次200；网格64环与遮挡板覆盖一次达标 | scripts/probe-ring.snapshot、measure_probe.py |
| A19-it-001 / 代码缺陷（看图发现）/ grid-01 | 网格主体严重溢出相邻格（如G02宽332px） | 整图查看：HTTP 200、DSL解析成功但主体跨格；代码定位 `x, y, w, h = o["body_bbox"]` 把 [left,top,right,bottom] 按宽高解包（width=right, height=bottom） | 改为取bbox左上角，宽高=size | 重建后A19-grid-02整图+1:1裁片目视合格；64/64逐像素测量（颜色采样、主体框±2px、ID存在且在主体外）全绿；**无剩余问题** | gen/grid-scene.png（缺陷版）、gen/grid-scene-02.png、gen/crop-tl.png、scripts/a19_scene.py |
| A19-it-002 / 视觉迭代 / grid-01 | 首版无法通过“实际看图检查所有目标与标签” | 见上（唯一实质缺陷，同轮修复） | 同上 | 见上；缺陷版与修复版均保留，互为前后证据 | scripts/measure_grid.py（新）、gen/grid-measure.json |

本题遇到并已确认的坑：

1. **bbox≠宽高**：几何数据的 `[left,top,right,bottom]` 与 `left,top,w,h`
   形状不同，解包错位只表现为“数值都合法”，HTTP与解析全绿、唯有看图才暴露。
   对策：发射器按语义取字段 + 交付前逐像素测量主体框（±2px）双保险。
2. **border在盒内**：圆环内径=外径一半依赖border画在盒内这一渲染语义，
   文档未明说——必须探针实测，否则内外判错会直接违反题面硬约束。
3. **阴影覆盖余量要实测**：遮挡题要求“所有绘制影响（含阴影）被完全遮住”，
   仅靠目视不够；以探针实测外扩+最终0差异像素比较双重证明。
4. **手数计数会错**：Q26初稿手写“6个”与数据（8个）不符，被生成器的
   唯一性/计数断言拦下后按实测改正——答案一律由程序从场景数据计算。

从文档了解、但本次未触发的注意事项：429限流与Retry-After路径（0次发生，
未伪造等待记录）；Text横向溢出CLIP的坑（A19文本框均≥48px、实测ID宽32-33px，
无裁切）。未确认的原因无。

## 5. 任务耗时与请求统计

结构化指标文件：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-19T11:04:02.996+08:00 → 2026-10-19T11:39:40.275806+08:00 | ISO8601 含时区 | suite-state 记录起始；结束=task-metrics.json 落盘时刻 |
| 任务总耗时 | 2137.280 | 秒 | 墙钟；本任务同日连续执行无中断 |
| 首次可用图耗时 | 136.610 | 秒 | 起始→首个可打开有效图（A19-probe-01 200，11:06:19.606+08:00） |
| 等待用户反馈 | 0 | 秒 | 本题无逐题用户反馈轮次（确认无发生） |
| 限流等待、排队等待 | 0 / null | 秒 | 限流：无429（0）；排队：客户端不可测→null |
| 已记录请求耗时之和 | 9.810（5次渲染：3.885+1.795+1.49+0.887+1.753） | 秒 | requests.jsonl；串行请求，与墙钟独立 |
| 成功、失败、重试请求 | 5 / 0 / 0（渲染）；文档0 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 6 / 1（未完成0） | 次 | iterations.jsonl 与逐图查看记录 |

时间戳均为客户端自计时并带时区；服务端未暴露 Server-Timing（→null）。

## 6. 设计选择、经验与未解决事项

**关键设计选择**

1. **先探针钉死渲染语义**：环内径（border在盒内）、阴影外扩、文本阴影
   三项不确定能力一次1.3万字节探针全部实测，避免整图返工。
2. **种子分布+断言门禁**：尺寸轮转保证每颜色/每形状三尺寸齐全，行约束
   用断言而不是看运气；分布结论以“实际生成结果”回填 scene-data.json。
3. **答案程序化生成**：14题的候选集、排序键、唯一性全部由生成器从场景
   数据计算并断言（17条），题目不可能多解；手写叙述与数据冲突时以断言为准
   （Q26由6改8即此机制生效）。
4. **遮挡等价按规范做**：文件哈希只留痕，判定用同解码器8位RGBA逐通道全量
   比较（0差异），不做白底合成/缩放/忽略alpha；两份原始响应字节都保留。
5. **两套核验互补**：像素测量（机器判据，64/64）+ 实际看图（整图、1:1裁片、
   两遮挡图各1次）都做过才算完成——HTTP与XML成功从未被当作完成依据。

**可复用经验**

- “每格一物体”的网格题，发射器必须用语义化取值（bbox就是bbox），
  并把逐格像素测量作为交付门禁，比人眼更快发现尺寸错位。
- 遮挡题的等价证明脚本可以直接复用到任何“同可见不同隐藏”的对图任务。
- 题目+答案分离交付时，答案文件附带“唯一性断言清单”是防多解最省力的证据。

**最终图如何满足要求 / 结束依据**

网格以整图+1:1裁片两轮看图+64对象逐像素测量收口；遮挡对以逐张看图+
RGBA逐像素等价(0差异)收口；题目以17条程序断言保证唯一与覆盖。全部要求
逐项核对无遗留，才判定结束——不是渲染成功或文件齐全。

**未解决事项**：无已知影响交付的缺陷；未经验证的要求：无。

**留痕确认**：tmp/run-20261011-01/A19/ 下探针（scripts/probe-*）、缺陷版
网格渲染（gen/grid-scene.png/grid-scene.snapshot v1）、修复版渲染与1:1裁片、
两遮挡渲染、scene-raw/grid-measure中间数据、全部生成/测量/对比脚本
（scripts/）、请求与迭代日志（requests.jsonl 5条、iterations.jsonl 2条）
均保留，无删除或覆盖；裁片仅为查看用临时副本，非交付件。

**.gitignore**：总任务根 [.gitignore](../../../.gitignore) 于套件启动时创建，
本题未改；忽略规则仅 `__pycache__/`、`*.pyc` 等运行时缓存（本题产生过
scripts/__pycache__，按约定不列为证据），tmp/、outputs/ 及全部日志、探针、
缺陷版与裁片均不被忽略。
