# 全套 Snapshot 使用与最终审查

## 服务调用总况（各题聚合，唯一口径=逐题 requests.jsonl 原始行）
- 渲染请求：367（200×345 / 失败×22）。失败分布：A03 4 次（同因语法均可修复，已留证）；A07 1 次（同因语法均可修复，已留证）；A08 1 次（同因语法均可修复，已留证）；A11 2 次（同因语法均可修复，已留证）；A17 1 次（同因语法均可修复，已留证）；A20 1 次（同因语法均可修复，已留证）；A21 8 次（同因语法均可修复，已留证）；A22 1 次（同因语法均可修复，已留证）；B04 1 次（同因语法均可修复，已留证）；B05 2 次（同因语法均可修复，已留证）
- 服务 HTTP 总行（含文档/探针/字体等）：398 行；其中非渲染行 31 行（文档缓存抓取集中在 B04 一次完成，后续题复用计 0）。
- 无 429/速率限流（0 次）；Retry-After 均为 null；密钥零写入全部台账。
- 复现：`python tmp/<run>/_suite/snapshot_client.py render <题> <dsl> <tag> <outdir>`（需要 env：SNAPSHOT_TASK_ROOT / SNAPSHOT_RUN_ID）。

## 文档/能力应用（跨题汇编）
- 实抓文档：ai-guide.md 与 DSL 文档（B04 缓存于 `tmp/<run>/B04/renders/`）；字体清单查询一轮；其后全部复用。
- 已验证关键规约（逐题踩坑累计）：
  1) border 枚举仅 NONE/SOLID（A03/B05 DASHED 两次实证，后以线段仿真）；
  2) 8 位颜色 `#RRGGBBAA` 末组为 alpha（A01↔A10 探明）；
  3) Transform 为 4×4 列主序，平移分量 = p−K·p（A09 校正）；
  4) Positioned 仅在 Stack/画布根内定位；Row/Column 不接受它（A03 验证）；
  5) 特殊字符经 Raw/CDATA 保真（A11/A17 逐字符）；fontWeight/fontStyle 行为有探针实证（A15）；
  6) B06 新坑：**凭记忆的语法会 200 但版式全崩**——Text 无自由 x/boxWidth、Container 无 left/top；
     真实书写应为 Positioned 定位 + Container/Text 属性（B06 v1 十张全 200 不可用版式留证、v3 重写生效）；
  7) 渲染驱动会“回退旧文件”造成误渲（B05 v2/B06 v2 两次同型），候选文件必须显式 `_vN` 优先。
- 双字体纪律：CJK = Noto Sans CJK SC（txt），纯 ASCII 数字 = Inter（num）；禁裸 `<`；每 canvas 首笔全幅底色。

## 看图与迭代（各题汇总）
- 看图（显式 image_views 合计）：263 次——含每张最终图的整幅查看与密集区放大；接触表/缩略不替代整幅（各题 snapshot-usage 有逐题口径）。
- 完整视觉迭代（view→改→渲→再看的完成周期）合计 93：A 类显式字段 49 + B01–B04 显式 15 + B05 20 + B06 9（语法修复行单独计，不入此项）。
- 迭代台账行合计 193 行（baseline/语法修复/visual/需求变更分开计；B06 台账 40 行中 v2 无效批 10 行为字节哈希鉴别、非看图事件，已在行内注明）。

## 数值/调研合规（B04/B06 核查类）
- B04：来源三重校验（原文要点+检索+存疑标注），sources.json 留痕。
- B06：两次 websearch（财政部公告 2023-30 时效、WHO 2015 游离糖）真实发生并计入 tool-usage；数值唯一基准=calcs.json。
- 演示口径逐件声明；不声称未做过的调研/实验、不伪造官方背书。

## 最终审查结论
- 30/30 完成；总终图 124（=磁盘审计）；每张图配同名完整 `.snapshot`（gallery 全量校验链接可达）。
- 各题状态/证据：见 [suite-state.json](suite-state.json)（每题 artifacts/visual_review_evidence/unresolved）。
- 遗留未解决事项：无（各题 unresolved_issues 均为空）。

## 踩坑与跨题经验汇编（按时间序）
- A01↔A10：颜色 alpha 位、BackdropFilter/ImageFiltered 组合语义、文字与滤镜先后。
- A03：Positioned 需 Stack 语境；rotate 数值经 REVIEW 30° 验证。
- A07：`extend` 字符串展开需逐字落盘（PARSE_ERROR 根因）。
- A09：Transform 平移分量语义；±1.5px 像素级审计方法。
- A11/A17：CDATA 保真与教学示例 [[CDATA 转义现身说法]]。
- A13：透明 PNG 预览策略与角落最小化偏差。
- A15：fontWeight 数值 vs 命名探针。
- A19：等价像素策略（双 DSL 同画布同几何不同遮蔽层）。
- A21/A22：预置三轮的回归执行方式（每轮只改需求点，对比区域零回归）。
- B05：256 色规则下的纸感纹理（细线/渐变替代照片）；三字字体误植审查法（「元/分摊」逐字校笔）。
- B06：语法记忆坑（见上）+ **一次渲染请求=一个真实 tag**（候选顺序修正）。
