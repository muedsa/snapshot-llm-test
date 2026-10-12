# Snapshot 使用情况说明与踩坑记录

任务ID：A09
任务名称：十二个非对称图形变换标本
本次运行ID：20261003-114508-flashmax
完成状态：完成（需求满足并完成视觉自检）
结束原因：全部指定交付已产出，最终图逐项核对通过
输出目录：`D:\workspaces\deepseek-v4.1-flash-max-in-dsh\outputs\20261003-114508-flashmax\A09`
临时目录：`D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A09`

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `transform-atlas.snapshot` | 完整可复现DSL（服务真实收到的 169,840 字节 UTF-8 文本） | `transform-atlas.png` | 完成 |
| `transform-atlas.png` | 服务返回的最终图片，1600×1200 PNG，222,166 字节 | `transform-atlas.snapshot` | 完成，已用 read_image 打开 |
| `geometry-audit.json` | 列主序4×4矩阵、每矩形四角、圆点中心、最终外接框、±1.5px 核对方法与结果 | 同上 | 完成 |
| `snapshot-usage.md` / `task-metrics.json` | 报告与指标 | — | 完成 |

逐项需求核对（依据最终 PNG 与 geometry-audit.json 的实际数值）：

| 需求 | 实际实现 | 结论 |
|---|---|---|
| 1600×1200，4列×3行，每格300×250，格间32 | 画布 1600×1200；格宽高 300/250；水平栅距 332、垂直栅距 282（= 尺寸+32） | 满足 |
| 整体居中，格外保留标题与图例 | 网格 1296×814，左上 (152,193)，左右边距各 152；标题带 0–168，图例卡 1030–1172，均在格外 | 满足 |
| 印章 120×120：3 彩色矩形 + 1 黑圆点 | 四枚图元坐标/尺寸逐字取自 `inputs/stamp.json`（R1 8,8,28×92 / R2 36,72,68×28 / R3 64,8,40×28 / dot 91,49 r8） | 满足 |
| 操作按列表顺序，每步围绕局部(60,60) | A = A_n·…·A_1，t = 格中心 − A·(60,60)；枢轴为不动点，落点即格中心 (ox+150, oy+125)（geometry-audit 每格 `pivot_canvas`） | 满足 |
| 像素坐标 x右/y下，"顺时针"按图像方向 | 旋转线性部分 [[cos,−sin],[sin,cos]]；图中 T02 红竖条由左侧转到上方、圆点落到枢轴右下 | 满足 |
| mirror_horizontal=左右镜像、mirror_vertical=上下镜像 | T05 A=[[−1,0],[0,1]]，T06 A=[[1,0],[0,−1]] | 满足 |
| 最终局部中心放到每格中心 | 12 格 `pivot_canvas` 均等于格几何中心 | 满足 |
| 编号、操作短名、刻度辅助线齐全 | 每格 `T01…T12`（22px 粗体）+ 短名（20px）；四边内侧每 25px 刻度、格内 25px 淡格线、中心十字、浅蓝本地坐标框、绿色虚线的外接框 | 满足 |
| 不裁切变换后的主体 | 最大外接框 129.1×127.7px，最大格内占位 x∈[68,232]、y∈[43,207]（格 300×250），未触及圆角/标题/脚注 | 满足 |
| 主体必须用 Transform.matrix，圆点随同变换 | 每格仅一个 `Transform`（16 数矩阵）承载整格映射，子树为 Stack+4 个 Positioned；圆点用 `shape="CIRCLE"` 随矩阵变化，T10 缩放 (1.25,0.75) 下实测为椭圆（semi-axes 10.0/6.0） | 满足 |
| T07 与 T08 显示操作顺序差异 | A(T07)=[[0,−1],[−1,0]]、A(T08)=[[0,1],[1,0]]，A(T08)=−A(T07)，det 均为 −1；两格形态互为 180° 旋转（audit `order_evidence_T07_T08`） | 满足 |
| geometry-audit.json：矩阵/四角/圆点/外接框 + ±1.5px 核对方法 | 12 格 × (矩阵、4 矩形各 4 角、圆点中心与椭圆半轴、外接框) + 核对方法、容差、例外与实测结果 | 满足 |
| 标签 ≥20 | 格号 22、短名 20、脚注 20、图例 20、页头副标题 20/22、主标题 38（无 <20px 文本） | 满足 |

像素核对实际结果：核对 589,632 像素，反走样带（预测类别边界 ±1.5px 内）之外颜色不一致 **0** 个；
320 组亚像素边缘样本，估计边缘与预测边缘最大偏差 **0.672px**，均值 0.2px 量级，全部 ≤1.5px（`verdict: pass`）。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（本次两次渲染均 `POST /snapshot`，`Content-Type: text/plain; charset=utf-8`，响应 `image/png`）
文档版本或访问日期：2026-10-03 实际访问；页面已存到共享缓存 `tmp/20261003-114508-flashmax/_suite/shared/docs/`（html + 文本提取）

AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md —— 实际读取，确认了请求体是 UTF-8 纯文本、成功响应是图片字节、
错误体是 JSON（`code`/`message`/`requestId`）、`/fonts` 返回每行一个字体族；本次两次请求均 200 且
`Content-Type: image/png`，未出现需要读错误体的失败。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://snapshot.muedsa.com/reference/parser-tags/ | `Transform.matrix` 是列主序 16 个无空格 Float；`origin`/`alignment` 语义；`shape="CIRCLE"`；`borderRadius` 单数字；`Text` 可嵌套；对齐常量语义 | 每格 `<Transform matrix="(a,b,0,0,c,d,0,0,0,0,1,0,tx,ty,0,1)">`；圆点 `<Container shape="CIRCLE">` |
| https://snapshot.muedsa.com/widgets/layout/transform/ | Transform 只改绘制坐标、不参与布局；旋转用弧度；父节点仍按变换前尺寸布局 → 本图所有定位都用绝对坐标 Stack | 格内坐标全部绝对定位，不做嵌套 Flex |
| https://snapshot.muedsa.com/guides/painting/ | 变换内容可能超出布局边界、是否可见取决于祖先裁剪 | 每格外接框上限核算，确认不出格 |
| https://snapshot.muedsa.com/reference/enums/ | `BoxShape`、`BorderStyle`、`BoxFit`、`ClipBehavior` 等枚举取值 | `shape="CIRCLE"`、`1 SOLID #E2E8F0` |

布局/文本/颜色/变换：本次用到绝对定位 Stack + Positioned、单数字 borderRadius、`#RRGGBBAA` 颜色、
16 值列主序矩阵变换、CIRCLE 形状、按实测宽度估算文本盒宽度（CJK≈1.00×字号、拉丁≈0.55×字号、
等宽≈0.60×字号，行高≈1.30×字号），生成脚本在写文字前会用该估算断言"不超宽"，避免换行压字。
字体查询：复用共享缓存 `_suite/shared/fonts.txt`（2026-10-03 11:46 由 `GET /fonts` 取得，200，448 字节），
本图全部文字使用 `Noto Sans CJK SC`（页头右侧两组统计用 `Noto Sans Mono CJK SC`），未臆造字体名。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp\20261003-114508-flashmax\A09\requests.jsonl`
迭代记录文件：`tmp\20261003-114508-flashmax\A09\iterations.jsonl`
渲染请求总数：2
成功次数：2
失败次数：0
重试请求数：0
DSL版本数：2（`transform-atlas.v1.snapshot`、`transform-atlas.v2.snapshot`）
实际图片查看次数：5（v1 全图、v1 的 T01/T11/格间三处放大、v2 全图）
完整视觉迭代数：2（v1→放大定位问题→v2 修改后复查；v2 为最终版核对）
未完成视觉迭代数：0
其他接口查询：本次未新增服务请求；复用共享的 `/fonts`（SHARED-FONTS-0001）与 13 个文档页面缓存

| 请求ID / 轮次 / 迭代ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| A09-REQ-0001 / design-v1→v1 / baseline | `transform-atlas.v1.snapshot`（142,138 字符） | 2026-10-03T12:53:49+08:00 → 12:53:53，3,637 ms | 200 / `image/png` | `transform-atlas.v1.png`（208,767 B） | 12:54:05 已查看全图：12 格形态与顺序均正确、无裁切压字；发现轴向对齐格里的绿色虚线外接框几乎被墨迹盖住 |
| A09-REQ-0002 / v1→v2 / visual | `transform-atlas.v2.snapshot`（169,457 字符） | 2026-10-03T12:55:10+08:00 → 12:55:14，4,479 ms | 200 / `image/png` | `transform-atlas.v2.png`（222,166 B） | 12:55:35 已查看全图：虚线框完整包住标本、淡格线补齐尺度参照，无新问题 → 定为最终版 |

（时间取自 `requests.jsonl` 的 `started_at`/`ended_at`/`duration_ms`；`X-Request-Id` 分别为
`57ae357b-…`、`94b99396-…`，`Server-Timing` 未返回 `render;dur` 以外的字段。）

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| design-v1 / alternative / — | 若把每个图元的本地偏移烘进矩阵（M·T(x,y)） | 形状坐标与矩阵职责混淆，无法自证"未手改形状坐标" | 改为整格一个 Transform + 子树 Stack 按 stamp 原始坐标摆放 | 结构确定，audit 中形状坐标与 stamp.json 完全一致 | `gen_a09.py` |
| v1 / baseline / design-v1 | 绿色虚线外接框在 T01/T05 等轴向格里几乎看不见，视觉上像残缺线头 | 放大 T01 看到虚线被墨迹按绘制顺序压住（虚线先画、标本后画） | 记录并放大确认不是缺元素 | 确认是图层顺序问题，非渲染缺失 | `crop-v1-cell01.png` |
| v1-crops / visual / v1 | 同上 + 格内缺少尺度参照 | 目视 T01/T11/格间三处放大图 | 虚线框整体外扩 1.5px 绘制；格内加 25px 淡格线 | v2 全图中虚线框 12 格全部完整可见 | `crop-v1-cell11.png`、`crop-v1-gap1112.png` |
| v2 / visual / v1 | 核对修改效果 | read_image 打开最终图逐格比对 | 无（本版即最终） | 12 格全部通过；T10 圆点呈椭圆证明非等比缩放沿矩阵生效 | `transform-atlas.v2.png` |
| audit-v1 / retry / v2 | 亚像素核对首轮多格误差顶到 1.0px，无法区分模型偏差与渲染偏差 | 复查发现采样点用了像素左上角（index）而非像素中心（index+0.5），模型自身偏 0.5px | 按像素中心重建覆盖率模型，边缘位置反解改为 s = 0.5 + α_q | 同一张 PNG 重算：上限 1.009px → **0.672px**，反走样带外不一致仍为 0，确认是核对模型偏差 | `check_a09.py`、`pixel-check.v2.json` |

从文档了解到、本次未触发的注意事项：`Transform` 的 `alignment` 属性可指定变换对齐点，本次刻意不设
（保持"矩阵直接作用于子节点左上角"这一 A07/A08 已验证的语义）；`<ImageFiltered>`/`<BackdropFilter>`
与本任务无关。没有遇到语法错误或服务失败，`requests.jsonl` 中失败数为 0。

## 5. 任务耗时与资源消耗

结构化指标文件：`outputs\20261003-114508-flashmax\A09\task-metrics.json`

| 指标 | 实际值 | 单位或币种 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-03T12:53:21+08:00 → 2026-10-03T12:56:39+08:00 | ISO8601（+08:00） | `_suite/suite-state.json` 的 A09 started_at + 收尾时刻 |
| 任务总耗时 | 198.0 | 秒 | 上述两时刻之差（墙钟，含生成/核对/看图） |
| 首次可用图耗时 | 32 | 秒 | 从 started_at 到 A09-REQ-0001 成功结束（12:53:53） |
| 等待用户反馈 | 0 | 秒 | 本题无用户交互 |
| 限流等待、排队等待 | 0 / 未知 | 秒 | 未出现 429/Retry-After（`rate_limit_wait_ms=0`）；服务端排队时长不可测记 `null` |
| 已记录请求耗时之和 | 8.116 | 秒 | `requests.jsonl` 两次渲染 `duration_ms` 之和（2 次串行、无重叠） |
| 输入、输出、总token | 未知 | token | 平台未提供，记 `null`，不用字数估算 |
| 图像输入使用量 | 未知 | — | 平台未提供，记 `null` |
| 任务费用 | 未知 | — | 平台未提供计费数据，记 `null` |
| 其他实际可取得指标 | 响应字节 208,767 / 222,166；DSL 142,138 / 169,457 字符 | 字节、字符 | `requests.jsonl` 的 `request_bytes`/`response_bytes` |

## 6. 设计选择、经验与未解决事项

关键设计选择：
1. **一个矩阵承载整格**：格内只用一个 `Transform`，子树是 Stack 里的四枚图元，按 `stamp.json` 原始本地坐标摆放。
   这样"矩阵完成全部映射"是可核验的，而不是把结果坐标写进形状。
2. **坐标系可视化**：每格画出本地 120×120 坐标框（含 u=60/v=60 中线）与 25px 刻度/淡格线，
   让"矩阵做了什么"直接可见；再叠加绿色虚线的外接框作为几何核对参照（外扩 1.5px 只为可见性，audit 里仍是精确值）。
3. **枢轴落点**：枢轴 (60,60) 是每步的不动点，因此必然落在格几何中心，而墨迹自身重心在 (56,54)，
   所以标本会相对格中心有 (−4,−6)px 的固有偏移——这是几何事实，浅蓝坐标框正是用来说明这一点的。
4. **可核验优先**：把"看起来对"变成"算得出来"——12 格矩阵、四角、圆点、外接框全部进 `geometry-audit.json`，
   再用独立脚本对渲染结果做 58.9 万像素的类别一致性与亚像素边缘核对。

可复用经验：
- 列主序 16 值矩阵的扁平布局 `(a,b,0,0,c,d,0,0,0,0,1,0,tx,ty,0,1)` 中，`(a,b)` 是本地 x 轴的像、`(c,d)` 是本地 y 轴的像，
  平移在第 13、14 位；把"每步围绕枢轴"写成 `A = A_n…A_1`、`t = C − A·p` 后，卡片中心与枢轴的关系不再需要手工试凑。
- 画在墨迹之前的辅助线会被墨迹整段盖住：外接框必须比墨迹外扩一点才会显示，否则视觉上像"线画残了"。
- 像素核对脚本里，采样点必须用像素中心（index+0.5）；用 index 会引入 0.5px 系统偏差，足以让 ±1.5px 的核对失去分辨力。

未解决事项：无。未发现需要后续处理的缺陷、环境限制或未验证要求。
临时目录中保留了 v1/v2 两版 DSL 与 PNG、每次请求的原始响应体（`*.rawbody`）、响应头（`*.rawheaders`）、
`curl` 元数据（`*.rawmeta`）、放大图、生成/核对/审计脚本与两份 JSON，均未删除或覆盖。
