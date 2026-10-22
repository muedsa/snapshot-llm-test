# Snapshot 使用情况说明与踩坑记录

任务ID：B04
任务名称：researched-visual-special · 太阳系数据特辑
本次运行ID：run-20261011-01
完成状态：完成
结束原因：需求满足并完成视觉自检（11 件全部逐版实看、AM 审计与终审通过）
输出目录：outputs/run-20261011-01/B04
临时目录：tmp/run-20261011-01/B04
路径基准：suite_root（相对总任务根）

遵循[PATHS.md](../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径。Markdown
本地链接相对当前文档。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| case-01/final.snapshot + final.png | 直径比例尺 1600×1000 | case-01（定版 v3） | 完成 |
| case-02/final.snapshot + final.png | 对数距离轴 1800×900 | case-02（定版 v2） | 完成 |
| case-03/final.snapshot + final.png | 双对数散点 1600×1200 | case-03（定版 v2） | 完成 |
| case-04/final.snapshot + final.png | 太阳日/自转 1400×1000 | case-04（定版 v2） | 完成 |
| case-05/final.snapshot + final.png | 重力/逃逸 1400×1000 | case-05（定版 v3） | 完成 |
| case-06/final.snapshot + final.png | 温度阶梯（竖）1200×1400 | case-06（定版 v3） | 完成 |
| case-07/final.snapshot + final.png | 卫星点阵 1400×1000 | case-07（定版 v2） | 完成 |
| case-08/final.snapshot + final.png | 地月系统 1400×1000 | case-08（定版 v3） | 完成 |
| case-09/final.snapshot + final.png | 冥王星档案卡（竖）1200×1600 | case-09（定版 v1） | 完成 |
| case-10/final.snapshot + final.png | 环/磁场/密度 1600×1000 | case-10（定版 v5） | 完成 |
| case-11/final.snapshot + final.png | 终章导读 1600×1000 | case-11（定版 v2） | 完成 |
| sources.json / editorial-note.md | 71 claims 溯源与编辑决定 | 全部 11 件 | 完成 |
| portfolio.json / portfolio.md / gallery.md | 逐件完成标准 G1–G9 与画廊 | 全部 11 件 | 完成 |
| task-metrics.json | 结构化指标（reconciles=true） | 见 §5 | 完成 |

硬要求核对：**尺寸**——11 件 IHDR 全部与 plan 规划一致（finalize_copy.py md5+IHDR
核验 ALL_OK，draft==final 字节相同，服务原始响应未后处理）；**数据**——全部表值出自
SRC-01..11 提取件，b04_data.py 单一事实源生成期断言（ck_case01..11）全过，XTABLE
五组跨表差异如实锁定不调和；**文案**——逐版 dump_text 全文核对，AM-1..11 条款审计
（audit_ams.py）11 件全绿、被取代措辞缺席；**效果与可读性**——每版整图实看（28 次）
+ 4 次裁剪复核，终审无重叠/遮挡/裁剪/截断类缺陷。

已知缺陷修复并复查：11 件过程中发现并修复缺陷共 17 轮（v1 嵌套圆、转义直出 ×5、
标签压轴/越界 ×4、k 条错位、底卡留白、图例截断、点阵叠字、ink 穿字、三带坐标笔误、
近不可辨色、行名不一致、行名不一致、AM 合规 5 处），每处修复后重渲实看比较，无遗留。
未验证/未满足要求：无。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com（以总 run-config 为准，覆盖题内默认）
文档版本或访问日期：AI 指南与 DSL 文档来自套件共享缓存（_suite/docs，本套首读 2026-10-20），
本题直接应用其知识，无新增 HTTP 文档请求。

AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md —— 本题实际应用：POST 渲染
端点/请求响应结构由 snap_render.py 按指南封装（无凭据、HTTP 状态+Content-Type 检查、
错误 JSON 不当最终图）；字体无需查询（默认族 CJK/上标字形实看验证过）。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| ai-guide.md（套件缓存） | 渲染接口、响应检查、错误处理 | scripts/snap_render.py、requests.jsonl |
| snapshot.muedsa.com DSL 文档（套件缓存） | 布局/文本/颜色/装饰/变换边界 | b04_case01..11.py 元素选型 |
| https://nssdc.gsfc.nasa.gov/planetary/factsheet/（11 源，本题抓取） | 表值、Ratio 列、定义引文 | research/SRC-01..11，sources.json |

实际用到的 DSL 能力（仅真实使用）：`SizedBox`/`DecoratedBox` 图元（条/带/点/矩阵格/
卡片/圆）、`Positioned` 绝对定位排版、`Text` 多字号色行高、`Transform` 竖向刻度（case-02/04）、
分段填色模拟连续色温带（case-06，多段 DecoratedBox 插值）、手造线段阵虚线（case-05/10）、
圆角 borderRadius。未用滤镜/裁剪/外部图片（A+B 系均纯 DSL）。字体：默认族，未查询；
上标 ⁻¹⁵、下标 N₂/CH₄、°∝×Δ 字形逐版实看验证。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：tmp/run-20261011-01/B04/requests.jsonl（28 行，全 200）
迭代记录文件：tmp/run-20261011-01/B04/iterations.jsonl（35 行 = 33 原生 + 2 日志修复补记）
工具记录文件：tmp/run-20261011-01/B04/tool-usage.jsonl（14 行，seq14=日志截断事故）
渲染请求总数：28
成功次数：28
失败次数：0
重试请求数：0（0 次 429/503，无 Retry-After 触发）
DSL版本数：28（每版渲染恰好一次；4 次生成期语法修复均未发请求、未产生废版文件）
实际图片查看次数：32（28 次整图逐版实看 + 4 次裁剪局部复核）
完整视觉迭代数：17（12 次由看图发现 + 5 次计划条款审计发现，均"改→渲→看→比"完整闭环）
未完成视觉迭代数：0
其他接口查询：0（无字体/其他接口；文档为套件缓存）

| 请求ID | 输入DSL | 起止与耗时 | HTTP | 响应文件 | 查看结果 |
|---|---|---|---|---|---|
| B04-req-0001..0004 | case-01/02 v1,v2 | 22:15–22:40，15.7–4.6s | 200 | drafts/*.png | 已看；01 嵌套圆缺陷、02 四缺陷（见 §4） |
| B04-req-0005..0006 | case-03 v1,v2 | 22:48–22:51，5.7/3.1s | 200 | drafts/*.png | 已看；v1 k 条错位 95px 压字 |
| B04-req-0007..0008 | case-04 v1,v2 | 23:53–23:56，3.7/2.0s | 200 | drafts/*.png | 已看；转义 ×2、水星标签越界 |
| B04-req-0009..0011 | case-05 v1,v2 / case-06 v1 | 00:05–00:15，2.4/2.0/3.4s | 200 | drafts/*.png | 已看；05 底卡留白；06 v1 即合格 |
| B04-req-0012..0017 | case-07..09 v1..v3 | 00:20–00:37，2.1–3.7s | 200 | drafts/*.png | 已看；07 叠字、08 图例截断、09 合格+字形裁剪 |
| B04-req-0018..0022 | case-10 v1..v4 / case-11 v1 | 00:56–01:19，1.9–9.0s | 200 | drafts/*.png | 已看+像素复核；见 §4 case-10 链 |
| B04-req-0023..0026 | AM 修复四件（01/05/10/11） | 01:31–01:32，1.5–4.5s | 200 | drafts/*.png | 已看；单行/单卡完整、其余与前版一致 |
| B04-req-0027..0028 | case-06 v2,v3 | 01:40–01:41，7.5/4.6s | 200 | drafts/*.png | 已看；v2 转义 `&lt;` 实证、v3 全角生效接受 |

每版查看时间与观察详见 iterations.jsonl（viewed 时间戳逐条）；4 次裁剪复核件：
drafts/case-09-v1-glyphcheck.png、case-10-v1-linecheck.png、case-10-v1-zoom.png、
case-11-v1-zoom.png（PIL 裁剪，非最终图，保留于临时目录）。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 修改 | 验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| case-01-v2 / 视觉 / v1 | 嵌套圆四缺陷（小体成团、大体重合、仅木星有标签、与"圆阵"用词不符） | 整图实看（#01 观察） | 改底对齐等比圆阵+逐圆标签+同尺度断言 | v2 实看接受；v3 仅加 AM-11 页脚注 | drafts/case-01-v1/v2/v3.* |
| case-02-v2 / 视觉 / v1 | 正文 ASCII `>` 直出 `&gt;`；三处标签压轴 | 实看+token_diff 核对恰 6 处 replace | 文案改"七处空隙均为正值"、标签移位三处 | v2 实看接受；日志原条目被 PowerShell 截断→logrepair 补记 | drafts/case-02-v1/v2.*、scripts/token_diff.py |
| case-03-v1 / 语法修复 / — | y 单调断言方向写反 | 生成期断言失败（未发请求） | 改 reverse=True | v1 正常渲染；v2 修 k 条错位 95px+压字（实看发现）后接受 | drafts/case-03-v1/v2.* |
| case-04-v2 / 视觉 / v1 | 半角 `>`/`<` 直出 ×2；水星标签越右卡界 | 实看+坐标计算（967 起越过 1010） | 改全角 ＞/＜；AX1 980→930 全量重算 109 处 | v2 实看接受；同样产生日志截断→logrepair 补记 | drafts/case-04-v1/v2.* |
| case-05-v2/v3 / 视觉+合规 / v1/v2 | 底卡留白偏大；成因行"扁率"与 AM-7 不符 | 实看；计划条款审计（#24） | 补第 6 行；改"含自转的赤道有效值（SRC-04 定义）" | 两版分别实看接受 | drafts/case-05-v1..v3.* |
| case-06-v2/v3 / 合规+视觉 / v1 | 缺 AM-8 五项、含被取代旧诚实注；v2 大气行 ASCII `<` 直出 `&lt;` | AM 审计；整图实看（字形与全角对比） | 补定义引文/大气事实/辐照绝对值/因果标注/1-bar 口径；`<`→全角 ＜ | v3 实看：全角生效、⁻¹⁵ 字形正常、五卡无溢出，接受 | drafts/case-06-v1..v3.*、scripts/audit_ams.py |
| case-07-v2 / 视觉 / v1 | 独立"颗"标签与章节标题叠字 | 实看（字形重叠） | 删除独立标签（标题已含单位） | v2 实看清晰无回归，接受 | drafts/case-07-v1/v2.* |
| case-08-v1 / 语法+视觉 / —/v1 | AM-3 质量档断言带用旧值（未发请求）；v1 图例 651.8>600 框截断 | 断言失败；实看+FIT-WARN | 按 AM-3 改 ≤1%；v2 缩图例、v3 删括注至 516px | v3 实看无截断接受 | drafts/case-08-v1..v3.* |
| case-10-v1..v5 / 语法+视觉+合规 | 见 portfolio.json visual_review（畸形生成器 NameError、dict 误迭代、ink 穿字、b_t0=b_m0 笔误、色差 6、行名不一致、AM-4 残留） | 本地断言、ink 像素检测、实看、AM 审计 | 逐版修复：虚线段→强对比分带+空档留空→行名统一→AM-9 措辞 | 每版实看+复看；v5 接受定版；终版 ink 检测全过 | drafts/case-10-v1..v5.*、linecheck10*.py |
| case-11-v2 / 合规 / v1 | 口径行缺 AM-11 取整对照 | 计划条款审计（#26） | 增"木星 4,331 vs 分表 4,332.589" | v2 实看接受 | drafts/case-11-v1/v2.* |

已遇到的踩坑（均已确认）：
1. **ASCII `<`/`>` 在渲染文本中被 XML 转义直出**（case-02/04/06 共 5 处）——服务按
   XML 解析，正文一律用全角 ＞/＜。由整图实看发现，非文档预警。
2. **PowerShell 参数/重定向吃 ASCII `>`**：两次把含 `>` 的文案经 PowerShell 传参，
   iterations 原条目 action 被截断（仅存 `&gt;` 残片）。修复：diff/token_diff 核对后追加
   logrepair 补记（原条目不改）；此后含特殊字符长文本一律经脚本文件写入。另：PowerShell
   `>` 重定向写 UTF-16，本套文本输出全部改用 Python 文件 I/O。
3. **服务返回 404 的猜测文档路径**（notes.html/notesnotes.html）——记入 unread_sources，
   经 moonfact.html 链接找到 fact_notes.html。

文档了解但本次未触发：429/503 重试路径（snap_render.py 已实现，0 次触发）、字体查询
接口（无特殊字体需求）、Image 嵌入（政策允许但未用）。

## 5. 任务耗时与请求统计

结构化指标文件：outputs/run-20261011-01/B04/task-metrics.json

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-20T21:05:00+08:00 → 2026-10-21T02:40:50+08:00 | ISO8601 | 首个研究抓取（SRC-01 fetched_at）→ metrics 生成 |
| 任务总耗时 | 20,150 | 秒 | 上述墙钟（含研究/计划/生成/渲染/实看/审计/交付文档） |
| 首次可用图耗时 | 11,808 | 秒 | 开始 → case-07 v1 接受（00:21:48，首个定版） |
| 等待用户反馈 | 0 | 秒 | 本题无外部反馈轮次 |
| 限流等待、排队等待 | 0、null | 秒 | 无限流；排队不可测（无服务端队列指标） |
| 已记录请求耗时之和 | 87.42 | 秒 | requests.jsonl（28 次，串行，≠总墙钟） |
| 成功、失败、重试请求 | 28、0、0 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 32（28+4）、17 | 次 | iterations.jsonl + 裁剪复核件 |

共享准备（不重复计入用例）：研究抓取 11 源 + 2 次 404（21:05–21:45）、plan-v1/v1a/v1b
（21:15/21:32/22:04）、共享脚本 10 个。文档请求：0（套件缓存复用）。逐用例时间/请求/
迭代见 task-metrics.json cases 段（Σrequests=28=总数，Σ原生迭代=33+2 补记=35，
reconciles=true；用例串行执行，其墙钟之和小于总墙钟，差值=研究/计划/交付时间）。

## 6. 设计选择、经验与未解决事项

关键设计选择：①先研究后计划——11 源全部实取再立 plan-v1（established_before_first_render
为真），AM-1..11 修订只追加不倒填；②b04_data.py 单一事实源+每案生成期断言，几何与数值
不可能漂移；③系列统一深空视觉语言但 11 件图形形式互异（比例条/区间轴/散点/双条/阶梯/
色带/点阵/同尺圆/档案卡/矩阵分带/导读网格），对应 G8；④事实/推算/解释三层在图与
sources.json 双侧标注（G6/G9）；⑤像素级工具（ink 检测、裁剪放大）只做证据，判断以
整图实看为准。

可复用经验：转义全角约定、断言先于渲染、audit_ams 条款关键词终审、md5+IHDR 定版核验、
日志经脚本文件写入（避开 PowerShell 文本陷阱）、logrepair 修复而不覆盖原日志。

结束依据：11 件全部达到各自 G1–G9（portfolio.json criterion_results 全 pass）、AM 审计
11 件全绿、终版整图复看通过、交付文件齐全（case.md×11、sources/editorial/portfolio/
gallery/metrics/usage），非"请求数达标"式结束。

遗留与未解决事项：**无已知缺陷**。未发生事项如实说明：无外部图片素材（纯 DSL 政策下
未使用辅助素材）、无字体查询、无服务失败。总任务根 .gitignore 已在套件启动时创建
（见套件总报告），本题未新增缓存规则；__pycache__/ 等运行时缓存按约定不列为产物。

## 开放作品集补充

逐件场景/内容/DSL能力/完成标准与检查证据见 portfolio.json（11 件 × G1–G9 全 pass，
criteria_history 记录 5 处 AM 生效、unresolved_issues 全空）；portfolio.md 记录策展
逻辑（逐维度扫描→特写→综合→终章）。用例独立性：11 件读者任务/图形形式互不重复，
无"同版式换色"；无嵌入素材（asset_policy=dsl_primary_with_supporting_assets 下全部
纯 DSL 完成）。工具贡献如实见 tool-usage.jsonl 14 条（研究抓取/断言/审计/像素复核/
diff 核验/定版核验/整图实看/日志修复），未重复计入渲染请求。
