# Snapshot 使用情况说明与踩坑记录

任务ID：A13
任务名称：A13 · 品牌标志到完整活动应用（叠光 Layerlight）
本次运行ID：run-20261011-01
完成状态：完成
结束原因：两方向预览实际对比选定后完善，四张交付图逐张与32×32缩略均通过视觉自检，纯黑与几何一致性实测通过
输出目录：outputs/run-20261011-01/A13/
临时目录：tmp/run-20261011-01/A13/
路径基准：suite_root（本文件内 Markdown 链接相对本文件）

遵循[PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径。图片链接
相对本文件（最终图与 DSL 在同目录）。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| [symbol-color.snapshot](symbol-color.snapshot) | 512×512 透明彩色图标 DSL | [symbol-color.png](symbol-color.png) | 完成 |
| [symbol-color.png](symbol-color.png) | 服务返回最终图（原始字节，md5 c1f6f569…） | [symbol-color.snapshot](symbol-color.snapshot) | 完成 |
| [symbol-black.snapshot](symbol-black.snapshot) | 512×512 透明纯黑图标 DSL（同几何） | [symbol-black.png](symbol-black.png) | 完成 |
| [symbol-black.png](symbol-black.png) | 服务返回最终图（原始字节，md5 286a9041…） | [symbol-black.snapshot](symbol-black.snapshot) | 完成 |
| [brand-banner.snapshot](brand-banner.snapshot) | 1200×400 品牌横幅 DSL | [brand-banner.png](brand-banner.png) | 完成 |
| [brand-banner.png](brand-banner.png) | 服务返回最终图（原始字节，md5 b98a31c3…） | [brand-banner.snapshot](brand-banner.snapshot) | 完成 |
| [launch-poster.snapshot](launch-poster.snapshot) | 1080×1350 发布海报 DSL | [launch-poster.png](launch-poster.png) | 完成 |
| [launch-poster.png](launch-poster.png) | 服务返回最终图（原始字节，md5 a7989b12…） | [launch-poster.snapshot](launch-poster.snapshot) | 完成 |
| [brand-system.json](brand-system.json) | 色彩/比例/构件(3≤6)/最小留白/四应用映射/黑版检查/小尺寸审阅 | 支撑四图 | 完成 |
| [rationale.md](rationale.md) | 两方向差异、实际选择依据、小尺寸改进（正文293字≤300） | 支撑四图 | 完成 |
| [task-metrics.json](task-metrics.json) | 结构化指标 | — | 完成 |

需求逐项核对（证据 = 四张最终图 + 两方向预览 + 实测检查文件）：

- 未用现成标志/文字当图标/外部图片；全部几何由 DSL 构造，无 Image 组件 ✓。
- 先做两个真正不同几何方向的 512×512 透明预览：方向A"叠层光板"（三圆角横条
  对角错排，正交母形）与方向B"光圈叠月"（圆环+偏心透镜盘+光点，圆形母形），
  均在临时目录保留（drafts/preview-a、preview-b 的 PNG 与 .snapshot）✓。
  实际打开两方向 512 整图、32px 浅底原尺寸图与 ×8 放大图后选定方向B：更独特、
  "光"意象直扣品牌名、月牙负空间在 32px 仍保留；A 清晰但接近通用列表图标。
- 完善同一方案：圆盘 176→160 并外移（45° 处保留 29.49 单位残环，环小尺寸连续）、
  圆盘改不透明（85% 透明压环在 32px 轮廓混色发糊）、光点 48→56（32px 下约
  3.5px）✓。
- 两图标几何相同：同一生成函数、同一坐标表，仅颜色不同；alpha 通道逐像素比对，
  542 个差异像素全部差值=1 且全部位于形状抗锯齿边缘，alpha 覆盖率相对差
  2.3e-5，判为 AA 舍入而非几何差异（checks-geometry-detail.json）✓。
- 纯黑版：Pillow 10.0.0 解码 RGBA（PNG 存非预乘值），alpha>0 像素 92,549 个
  全部 RGB=0，违规 0；alpha 范围 [1,255]（1–254 仅出现在抗锯齿边缘）✓。
- 图标 3 个主要几何构件（环C1/盘C2/点C3）≤6；环孔与三处间隙为负空间不计数，
  生成规则已记录 ✓。
- 横幅含"叠光 Layerlight""把复杂信息，组织成清晰画面"（另含官网，属允许的
  补充信息）✓；海报另含"2026.11.07 · ONLINE""OPEN BETA"胶囊徽章
  "layerlight.example.org" ✓。
- 横幅与海报未嵌入图标渲染 PNG：由同一 ICON 参数表按统一比例 s+原点偏移重新
  生成（横幅 ×0.375@(72,104)、海报 ×0.62@(382,176)），DSL 中无任何 Image ✓。
- 海报为独立纵向构图（徽章/标题/副文/分隔条/日期/网址居中轴），非横幅放大 ✓。
- 32×32 检查：预乘 alpha → Pillow 10.0.0 Image.LANCZOS 512→32 → 反预乘，
  仅存临时目录 thumbs/，未覆盖最终 PNG；以共享浅色底 #F1F5F9 在实际 32px
  尺寸查看两枚图标（轮廓与月牙负空间可辨认），另开 ×8 NEAREST 放大观察边缘；
  预览无额外描边或锐化 ✓。
- 留白：两图标 alpha 包围盒 [56,56,455,455]，四边 56 单位（=11% 盒宽=0.7×环宽）；
  横幅内图标最近元素间距 72px、海报 101.28px，均 ≥56 单位换算 ✓。

交付 JSON 核对：brand-system.json 含必需字段 colors/geometry/components/
clear_space/applications/black_check/small_size_review，identity（schema_version 1、
task_id A13、path_base output_dir）齐全，数值为实测/未舍入推导值并附方法。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档版本或访问日期：ai-guide.md、parser-tags.html、字体查询结果均为本套共享缓存
（tmp/run-20261011-01/_suite/docs/，套件启动时真实抓取，本题复用不重复计新请求）。

AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md
- 实际阅读（缓存）：请求结构、浏览器 UA 要求、/fonts 端点。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| ai-guide.md（缓存） | 请求体结构/Snapshot 根节点约定 | 全部6张 DSL 根结构 |
| 标签参考 parser-tags.html（缓存，本题实际抽取） | **Snapshot background 默认 transparent**（透明图标不设该属性）；Container border 格式 `"宽度 SOLID 颜色"`；**shape="CIRCLE"** 造圆环与实心圆；颜色 #RRGGBBAA 带 alpha；渐变/boxShadow 属性表 | symbol-*.snapshot 的圆环/圆盘/光点；brand-banner/launch-poster 的渐变底 |
| 字体查询缓存 fonts.txt | Inter+Noto Sans CJK SC、Noto Sans Mono CJK SC | 横幅海报标题/副文/网址/日期/徽章 |

用到的其他能力：Container LINEAR 渐变（三色 stops）、borderRadius 胶囊、
textAlign CENTER、height 行高、Positioned 几何。圆环用 "border+无填充+shape
CIRCLE" 实现（Flutter BoxDecoration 语义），首次渲染即通过。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：tmp/run-20261011-01/A13/requests.jsonl
迭代记录文件：tmp/run-20261011-01/A13/iterations.jsonl
渲染请求总数：6
成功次数：6
失败次数：0（无 400/429，无重试）
重试请求数：0
DSL版本数：6个DSL文件（2方向预览 + 4定稿；定稿几何为预览B的完善版）
实际图片查看次数：18（两方向预览 512×2、32px 浅底×2、×8 放大×2、定稿整图×4、
定稿 32px 浅底×2、定稿 ×8×2、交付目录最终图复看×4）
完整视觉迭代数：1（iter-002：看预览→改几何→渲染定稿→比较）
方案探索迭代数：1（iter-001 两方向对比选型）
测量迭代数：2（iter-003 纯黑/几何/包围盒检查 + 差值像素追加量化）
其他接口查询：0（3条文档/字体缓存复用记录，不计新请求）

| 请求ID / 轮次 / 迭代ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| A13-req-0001/0002 / iter-001 方案探索 | drafts/preview-{a,b}.snapshot | 2026-10-14T10:38:08+08:00 起 1.36s/1.07s | 2×200 / image/png | drafts/preview-{a,b}.png | 10:39–10:40 看两方向 512 整图 + 32px 浅底 + ×8：A 清晰但像通用列表图标；B 独特、月牙负空间保留，但 v1 圆盘透明压环混色发糊 → 选 B 并完善 |
| A13-req-0003–0006 / iter-002 visual | drafts/{symbol-color,symbol-black,brand-banner,launch-poster}.snapshot | 10:41:42 起 0.95/1.27/1.22/2.10s | 4×200 / image/png | drafts/*-v1.png（即最终图原字节） | 10:42 逐张整图：四图达标（几何一致/文字齐全/海报独立构图）→ 定稿复制到 outputs 并 md5 校验 |
| iter-003 测量 | —（本地像素实测，无请求） | 10:44–10:48 | — | — | 32px 原尺寸×2 + ×8×2 查看通过；纯黑 0 违规；几何差异 542px 全部为边缘 ±1 AA；包围盒 [56,56,455,455] |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| iter-001 / 方案探索 | 方向B预览 v1：32px 下圆盘轮廓发糊呈团块、环在 45° 处残环偏薄、光点偏小 | 32px ×8 放大查看确认：圆盘 85% 透明度叠在青环上混色，边缘 AA 区域色彩浑浊；几何计算残环仅 21.5 单位 | 圆盘改不透明、176→160 并外移至 (240,240)、光点 48→56 | 定稿 32px 原尺寸与 ×8 复查：轮廓干净、残环 29.49 单位（32px 下约 1.84px 连续）、光点约 3.5px 清晰 | drafts/preview-b.png、symbol-*-v1.png |
| iter-003 / 测量量化 | 彩/黑两图 alpha 通道有 542 像素不一致，一度疑似几何不一致 | 追加量化：全部差值=1，全部紧邻两侧全不透明像素（形状边缘），alpha 覆盖率相对差仅 2.3e-5 | 无需修改——记录为抗锯齿舍入证据并写入 brand-system.json | 纯黑检查 0 违规、几何一致性 passed | checks.json、checks-geometry-detail.json |

另记录：`Container shape="CIRCLE" + border="宽度 SOLID 颜色"` 首次使用即渲染
出正确圆环（无填充时即为环）；透明画布不写 background 属性即可（默认
transparent），若写白色反而破坏图标 alpha。全程 6 渲染全部 200，无 429。

## 5. 任务耗时与请求统计

结构化指标文件：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-14T10:33:00+08:00（约）– 2026-10-15T11:24:48+08:00 | 含时区时间 | 起始为 A12 完成（10:31:08）后读题，结束为指标最终写入；中间含一次平台会话中断（见下） |
| 任务总耗时 | 89508（其中有效工作约 2340） | 秒 | 墙钟含会话中断：四图渲染、看图、检查与本报告草稿在 10-14 10:33–11:12 完成（约 2340s）；10-15 11:24 恢复后补写指标与状态，产物无损失 |
| 首次可用图耗时 | 310 | 秒 | 起始 → 首次成功渲染完成（10:38:09.7，方向A预览；两预览一次成型可用） |
| 等待用户反馈 | 0 | 秒 | 单次自动执行，无用户反馈轮次 |
| 限流等待、排队等待 | 0 / 未知 | 秒 | 无 429；服务端排队时间不可测，记 null |
| 已记录请求耗时之和 | 7.970 | 秒 | requests.jsonl 6 次渲染之和，不等于任务总耗时 |
| 成功、失败、重试请求 | 6 / 0 / 0 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 18 / 1 | 次 | iterations.jsonl 及实际查看记录（另有 1 次方案探索、2 次测量迭代） |

## 6. 设计选择、经验与未解决事项

关键设计选择：

- 两个方向真正不同（正交圆角横条 vs 圆形光圈），用同一透明画布、同一 512 盒、
  同一 32px 检查流程公平对比，选择依据全部来自实际看图（512 整图+32px 原尺寸+
  ×8 边缘），写入 rationale.md（293 字）。
- 图标几何收敛为一张参数表（环/盘/点的盒与直径）+ 一个缩放函数：彩版、黑版、
  横幅、海报四张 DSL 全部由它生成，保证"同一 DSL 几何规则"且不可能漂移。
- 圆环用 border 实现而非两圆相减：单节点即得精确内外径，黑版天然 RGB=0。
- 黑版不用渐变/滤镜，纯 #000000 实色，AA 边缘 alpha 渐变即满足"抗锯齿 alpha
  允许"且实测 0 违规。
- 海报独立构图：纵向居中轴 + 胶囊徽章 + 分隔线，与横幅的左图右文横排完全不同。
- 32px 检查严格按题面流程：预乘→LANCZOS→反预乘，浅色底实际尺寸查看，
  ×8 仅辅助观察边缘，全部预览只存临时目录。

可复用经验：**透明图标必须省略 background 属性（默认即 transparent）**；
`shape="CIRCLE"` + border 是造环的最稳方式；32px 下半透明叠色是轮廓发糊的
常见根因——图标叠层优先用不透明色 + 几何重叠表达"叠"；两版渲染的 alpha 通道
比较要先量化差值分布再下结论（边缘 ±1 是 AA 舍入，不是几何不一致）。

未解决事项：无。6 次渲染全部 200；纯黑 0 违规；四张最终 PNG 与服务响应字节
一致（md5 校验通过）；两方向预览与全部 32px 检查证据保留于临时目录。

留痕确认：tmp/run-20261011-01/A13/ 保留 drafts/（两方向预览 PNG+DSL、定稿
4×PNG+DSL、chosen-direction.txt）、thumbs/（8 张 32px 检查图）、checks.json、
checks-geometry-detail.json、requests.jsonl（6 渲染 + 3 文档缓存复用）、
iterations.jsonl（3 条）、scripts/（生成/缩略/检查/日志脚本）；失败尝试
（输出目录未建导致的复制失败）未删除，见会话命令记录。总任务根 .gitignore
已按 templates/gitignore-template.txt 维护，排除 __pycache__/ 等运行时缓存，
未排除 tmp/、outputs/ 或任何过程证据。
