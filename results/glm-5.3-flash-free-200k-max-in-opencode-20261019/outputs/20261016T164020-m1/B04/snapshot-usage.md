# Snapshot 使用情况说明与踩坑记录

任务ID：B04 · 任务名称：researched-visual-special（深海研究特辑《下潜 DEEP DIVE》）
本次运行ID：20261016T164020-m1 · 完成状态：完成 · 结束原因：需求满足并完成视觉自检
输出目录：outputs/20261016T164020-m1/B04/ · 临时目录：tmp/20261016T164020-m1/B04/ · 路径基准：suite_root

## 1. 最终产物与需求完成情况

十件独立用例，每件 final.png + final.snapshot + case.md；输出根另有 sources.json（17 来源/59 claims/4 datasets/6 未读/8 不确定）与 editorial-note.md、portfolio.json/md、gallery.md、task-metrics.json。逐张状态：全部通过（证据见 §3/§5 与各 case.md 自检）。

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| case-01/final.snapshot | 完整可复现DSL | case-01/final.png | 通过 |
| case-01/final.png | 服务返回的最终图片 | case-01/final.snapshot | 通过（渲染 200，服务原始字节）|
| case-02/final.snapshot | 完整可复现DSL | case-02/final.png | 通过 |
| case-02/final.png | 服务返回的最终图片 | case-02/final.snapshot | 通过（渲染 200，服务原始字节）|
| case-03/final.snapshot | 完整可复现DSL | case-03/final.png | 通过 |
| case-03/final.png | 服务返回的最终图片 | case-03/final.snapshot | 通过（渲染 200，服务原始字节）|
| case-04/final.snapshot | 完整可复现DSL | case-04/final.png | 通过 |
| case-04/final.png | 服务返回的最终图片 | case-04/final.snapshot | 通过（渲染 200，服务原始字节）|
| case-05/final.snapshot | 完整可复现DSL | case-05/final.png | 通过 |
| case-05/final.png | 服务返回的最终图片 | case-05/final.snapshot | 通过（渲染 200，服务原始字节）|
| case-06/final.snapshot | 完整可复现DSL | case-06/final.png | 通过 |
| case-06/final.png | 服务返回的最终图片 | case-06/final.snapshot | 通过（渲染 200，服务原始字节）|
| case-07/final.snapshot | 完整可复现DSL | case-07/final.png | 通过 |
| case-07/final.png | 服务返回的最终图片 | case-07/final.snapshot | 通过（渲染 200，服务原始字节）|
| case-08/final.snapshot | 完整可复现DSL | case-08/final.png | 通过 |
| case-08/final.png | 服务返回的最终图片 | case-08/final.snapshot | 通过（渲染 200，服务原始字节）|
| case-09/final.snapshot | 完整可复现DSL | case-09/final.png | 通过 |
| case-09/final.png | 服务返回的最终图片 | case-09/final.snapshot | 通过（渲染 200，服务原始字节）|
| case-10/final.snapshot | 完整可复现DSL | case-10/final.png | 通过 |
| case-10/final.png | 服务返回的最终图片 | case-10/final.snapshot | 通过（渲染 200，服务原始字节）|

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com（以 run-config 为准）· 文档访问日期：2026-10-18

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| ai-guide.md（open-snapshot 服务指南，套任务级已阅；缓存 tmp/_suite/…） | 请求 JSON 骨架、响应检查、错误码处理 | tmp/_suite/snapshot_client.py＋本项目各 .snapshot |
| DSL 主体文档（snapshot.muedsa.com） | Positioned/Container/Stadium/Transform·matrix、Text align/box_w 换行、字体族（CJK 用 Noto Sans CJK SC） | 全部 10 件 DSL 通用构件 b04_common.py |

本次用到的能力：色带 rect 组、Text 对齐/宽盒换行、Stadium 胶囊、Transform matrix（rotate 文字/竖排列）、多边形扫描填充（poly_rows）、圆点构件（hill_rows）、日志页脚（srcs/exhibit 页脚锚）。不使用 Image 嵌图与滤镜（无需）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：tmp/20261016T164020-m1/B04/requests.jsonl
迭代记录文件：tmp/20261016T164020-m1/B04/iterations.jsonl
渲染请求总数：21 · 成功次数：20 · 失败次数：1（1 次 HTTP 400 解析错误已修复）· 重试请求数：0（无 429/超时重试）
DSL 版本数：21（10 件初版 + 11 修订版变体）
实际图片查看次数：17（含接触表与定位放大；每次完整打开）
完整视觉迭代数：3（批次记录见 iterations.jsonl）· 未完成视觉迭代数：0
其他接口查询：无（本任务全部经 render）

| 请求ID | 输入DSL | HTTP 状态 | 响应文件（tmp） | 查看结果 |
|---|---|---|---|---|
| B04-render-0001 | dsl/01.snapshot | 200 | b04-case-01-v1-184603871.resp | 已看：接触表 vv1 |
| B04-render-0002 | dsl/02.snapshot | 200 | b04-case-02-v1-184611344.resp | 已看：接触表 vv1 |
| B04-render-0003 | dsl/03.snapshot | 200 | b04-case-03-v1-184615562.resp | 已看：接触表 vv1 |
| B04-render-0004 | dsl/04.snapshot | 200 | b04-case-04-v1-184618442.resp | 已看：接触表 vv1 |
| B04-render-0005 | dsl/05.snapshot | 200 | b04-case-05-v1-184622136.resp | 已看：接触表 vv1 |
| B04-render-0006 | dsl/06.snapshot | 200 | b04-case-06-v1-184626273.resp | 已看：接触表 vv1 |
| B04-render-0007 | dsl/07.snapshot | 200 | b04-case-07-v1-184628789.resp | 已看：接触表 vv1 |
| B04-render-0008 | dsl/08.snapshot | 400 | b04-case-08-v1-184632045.resp | 失败（400 PARSE_ERROR：内容含裸 `<`）修正后重渲 |
| B04-render-0009 | dsl/09.snapshot | 200 | b04-case-09-v1-184633522.resp | 已看：接触表 vv1 |
| B04-render-0010 | dsl/10.snapshot | 200 | b04-case-10-v1-184636047.resp | 已看：接触表 vv1 |
| B04-render-0011 | dsl/08.snapshot | 200 | b04-case-08-v2-184711236.resp | 已看：接触表 vv2 |
| B04-render-0012 | dsl/02.snapshot | 200 | b04-case-02-v2-185430449.resp | 已看：接触表 vv2 |
| B04-render-0013 | dsl/03.snapshot | 200 | b04-case-03-v2-185433458.resp | 已看：接触表 vv2 |
| B04-render-0014 | dsl/05.snapshot | 200 | b04-case-05-v2-185435617.resp | 已看：接触表 vv2 |
| B04-render-0015 | dsl/07.snapshot | 200 | b04-case-07-v2-185438749.resp | 已看：接触表 vv2 |
| B04-render-0016 | dsl/08.snapshot | 200 | b04-case-08-v3-185443616.resp | 已看：接触表 vv3 |
| B04-render-0017 | dsl/04.snapshot | 200 | b04-case-04-v2-190718834.resp | 已看：接触表 vv2 |
| B04-render-0018 | dsl/06.snapshot | 200 | b04-case-06-v2-190723205.resp | 已看：接触表 vv2 |
| B04-render-0019 | dsl/07.snapshot | 200 | b04-case-07-v3-190726618.resp | 已看：接触表 vv3 |
| B04-render-0020 | dsl/09.snapshot | 200 | b04-case-09-v2-190734098.resp | 已看：接触表 vv2 |
| B04-render-0021 | dsl/08.snapshot | 200 | b04-case-08-v4-190859303.resp | 已看：接触表 vv4 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比与剩余问题 |
|---|---|---|---|---|
| b04-syn-1 / 语法修复 / case-08 v1 | HTTP 400：内容含裸 `<`（『差 < 0.2%』）破坏 XML 解析 | 错误响应 error_summary 明示 | 改为『相差小于 0.2%』重渲 | v2 200；结论已入 shared 经验（写文本避免裸 < &，或用全角） |
| b04-vis-1 / 视觉迭代 / 五件 | ① c02 左列带名深字深底不可读；② c03 十段只铺 990px、『200 m』端标掉出带；③ c05 海雪双簇隔断读感差；④ c07 水体/海底对比弱；⑤ c08 轴单位『atm（对数）』与『1,000』刻度重叠 | sheet-1~4 + 定位放大逐项确认 | ①双浅色双色左列；②段高改 sh/10、端标回带；③单沉降流+背噪；④水体/双深浅；⑤右移单位标签 | 五件重渲（改动 build 后 v2/v2/v2/v2/v3）并复看通过 |
| b04-vis-2 / 视觉迭代·内容纪律 / 四件 | ① c04 楼层类比未锚；② c06 『古时认为…/越往下越冷』超原文；③ c07 『只出现在』过强、『洋壳俯冲』无锚；④ c09 『不到 4/5』数学错误 | claims 复核逐句比对 sources.json | ①改纯计算 800/3,682；②改官方释义转述；③改『主要由…组成』/『示意：汇聚边界』；④改 80.9%/19.1% 正确算式 | 四件重渲复看通过；全部句段可映射 claims |
| b04-vis-3 / 视觉迭代 / case-08 | 对数网格线绘制在柱条之后，深色柱上有浅色叠印 | zoom-c08-bars 定位复看 | 网格线改到柱前绘制（v4） | 复看通过 |

从文档知悉但本次未触发的注意事项：Image 嵌图的 license 与引用、滤镜效果性能、双变换复合矩阵易错（本刊用一次旋转/竖排，B03 已验证）。

## 5. 任务耗时与请求统计（摘要；完整值见 task-metrics.json）

| 指标 | 实际值 | 来源 |
|---|---|---|
| 任务开始/结束 | 2026-10-18T18:03:55+08:00 → 2026-10-18T19:33:34+08:00 | suite-state.updated_at 衔接 + 收尾脚本时间 |
| 任务总耗时 | 89.7 min（含研究与收尾，非全部请求耗时）| 同上 |
| 首次可用图 | 渲染 18:46:03（case-01 v1，200）；接触表实看 2026-10-18T19:07:36+08:00 | requests.jsonl + sheet mtime |
| 等待用户反馈 / 限流 / 排队 | 0 / 0 / 0（未发生）| —— |
| 渲染请求耗时之和 | 66.7 s | requests.jsonl（可重叠，不等于总耗时）|
| 成功/失败/重试 | 20/1/0 | 同上 |
| 实际看图/完整迭代 | 17 次 / 3 + 1 语法修复 | iterations.jsonl |

## 6. 设计选择、经验与未解决事项

- **五带色语 + 同比尺**：全刊唯一比例常数，跨件复用显著提升可读性与可复核性；封面/分带件标注『等高示意』防误导。
- **中英文字体分工**：混排中文与数值分两个字体族（CJK：Noto Sans CJK SC；纯 ASCII/数字：Inter），避免 '·/—/±/～' 落入 Inter 缺字。
- **卡片系统统一 exhibit()**：标题/分行/锚点/着色参数化，保证 10 件视觉一致且便于逐处更新。
- **口径纪律**：三个最深点口径与 1960 系读数并列陈列，不上判断；未锚句段一律删除或注明为自算/示意。
- 未解决事项：无功能性或可见缺陷；视觉弱化点（c02 带格5名义值提示、c07 截面强示意）已以图内标注与 claims 记录。

临时目录完整性：sources/（逐源归档+README-access-log）、dsl/（10 终版 + 构建中间不可覆盖）、renders/（21 req+resp 全留）、steps/（接触表与定位放大）、claims.md/claims.jsonl、plan-v1.md（v1+v2）、各构建/收尾脚本均已保留；未清理/未覆盖失败尝试。
总任务根 .gitignore 已存在（全程规则含 tmp/outputs 不被忽略）；__pycache__ 等运行缓存规则见总报告。