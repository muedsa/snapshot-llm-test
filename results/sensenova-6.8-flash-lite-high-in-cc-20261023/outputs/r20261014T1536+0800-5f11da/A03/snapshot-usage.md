# Snapshot 使用情况说明与踩坑记录

任务ID：A03
任务名称：语义调试 / Semantic Debugging —— 修复迁移后失效的原稿并交付 System Pulse 监控卡
本次运行ID：`r20261014T1536+0800-5f11da`
完成状态：完成
结束原因：需求满足并完成视觉自检
输出目录：`outputs/r20261014T1536+0800-5f11da/A03/`
临时目录：`tmp/r20261014T1536+0800-5f11da/A03/`
路径基准：suite_root（本文件与 [repair-log.json](repair-log.json)、[task-metrics.json](task-metrics.json) 同层；`outputs/...` 与 `tmp/...` 一律以总任务根为基准）

遵循 [PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录环境变量。
Markdown 本地链接相对当前文档；本文件位于输出目录，因此只对本层文件建立链接，
`tmp/` 下的证据以代码形式给出相对总任务根的路径。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| [system-pulse.snapshot](system-pulse.snapshot) | 完整可复现 DSL（5796 B） | [system-pulse.png](system-pulse.png) | 完成 |
| [system-pulse.png](system-pulse.png) | 服务返回的最终图片（48526 B，`image/png`） | [system-pulse.snapshot](system-pulse.snapshot) | 完成 |
| [repair-log.json](repair-log.json) | 11 项问题 × 原稿行号/类别/证据/文档来源/修改/验证 + 16 个版本谱系 | — | 完成 |
| [task-metrics.json](task-metrics.json) | 结构化计时与请求统计 | — | 完成 |

### 题面要求逐项核验

判定阈值全部先于测量定义；数值断言由 `tmp/.../A03/gen/a03_inspect.py` 对最终 PNG 做像素测量产生，
报告在 `tmp/.../A03/v2-inspect.json`，alpha 语义另在 `tmp/.../A03/alpha-check.json` 用众数 vs 理论上叠值核验。
完整 20 项见 [repair-log.json](repair-log.json) 的 `final_verification.requirement_check.items`，全部 `passed: true`。

| 要求 | 实测 | 结果 |
|---|---|---|
| 1280×800 | `size=[1280,800]` | 通过 |
| 深底 #0B1220 | 四角像素均 `[11,18,32]` | 通过 |
| 安全边距 32 | `content_bbox=[32,42,1247,735]`，余量 `{left:32,top:42,right:32,bottom:64,min:32}` | 通过 |
| 44 字号标题 | `title.bbox=[33,44,322,85]`，高 42px | 通过 |
| 第一行三个等宽指标卡 | `widths=[384,384,384]`，`max_width_delta=0` | 通过 |
| 卡片间距 | `gaps=[32,32]` | 通过 |
| 文案 USAGE 72% / LATENCY 148 ms / SUCCESS 99.2% | 与题面逐字一致（最终图人工确认） | 通过 |
| 三指标文案字号 28 | 与 28px 字号一致（最终图人工确认） | 通过 |
| 右上 LIVE 96×36 | `live.bbox=[1152,42,1247,77]`，96×36 | 通过 |
| LIVE 不盖住标题 | `title.right_edge=322` ≪ `live.left=1152`，横向间隔 830px | 通过 |
| 说明卡 500×150、圆角 24 | `size=[500,150]`，上下边框行 446/595，左右边框列 390/889 | 通过 |
| 彩色细条穿过说明卡两侧边界 | `extent_x=[250,1029]`，卡边 390/889，两侧各越出 140px | 通过 |
| 只模糊卡内背景 | 卡外单步亮度跳变均值 173.77 vs 卡内 10.48（比值 16.59） | 通过 |
| 文字保持清晰 | 卡内文字笔画最大跳变 172.09，为卡内模糊背景的 16 倍 | 通过 |
| 说明卡文字 Background-only blur、字号 28 | `card_text_bbox=[495,511,785,536]`，高 26px | 通过 |
| 右下 REVIEW 160×56 | `bbox=[1076,660,1239,735]`，164×76（旋转 8° 后理论外接框 167×78，差值来自圆角与抗锯齿） | 通过 |
| REVIEW 视觉逆时针 8° | `rotation=counterclockwise`（topmost_x 1221 > centroid 1157.5 > bottommost_x 1093） | 通过 |
| REVIEW 白底不透明度 20% | 众数 `[58,64,76]` vs 白色 20% 理论值 `[60,65,77]`，通道差 ≤2 | 通过 |
| REVIEW 文字不透明、字号 24 | 不透明白色（最终图人工确认） | 通过 |
| 各元素完整可见 | 与画布四边余量均 ≥32，`fully_visible=true`、`inside_safe_margin=true` | 通过 |

### 为何达到交付标准

本任务的难点不在能否出图，而在**修好全部显式报错之后服务仍然返回 200 和一张看起来正常的 PNG，
画面却只剩标题**。这是 TASK.md 明确点名的那一类「静默忽略」问题——任何只看 HTTP 状态、XML 合法性或像素总量的
检查都会判为通过。所以验收依据是：20 项要求全部有可复算的数值断言或明确的看图记录；
卡外/卡内锐度比值 16.59 同时证明「细条穿过卡外仍锐利」和「卡内背景真的被模糊」；
文字笔画跳变 172.09 证明文字没有被模糊波及。这些都不是「渲染成功」能替代的证据。

### 已知缺陷状态

自己引入的两项缺陷都已修复并在 [repair-log.json](repair-log.json) 的 `own_defects` 单独归档：
V-0（probe3-p6 多加 `<Container>` 漏闭合，不能当干净基线，已改用 probe4-p7 重做）、
V-1（v1 漏减根 padding 的 32px 平移，v2 用 `L()/T()` 统一换算修复）。
修复后已重新渲染并逐项复查，`v1-inspect.json` 与 `v2-inspect.json` 保留前后对照。

### 已知局限（如实保留）

- 文字字符内容与字号，像素测量只能给出外接框与高度比例，逐字核对靠人工看图完成；对应看图记录在
  `tmp/.../A03/iterations.jsonl` 与 `repair-log.json` 的 `versions[].viewed`。
- REVIEW 与说明卡卡体的 alpha 用「众数 vs 理论上叠值」核验，众数做了 2 级量化、允许 ±2 通道误差——
  这是测量方法的上限，不是渲染误差。
- 说明卡圆角 24 未做单独的弧半径数值断言：`card_geometry_check` 用「上下边框行只在 x=413..866 出现亮蓝」
  作为边框行判据，侧面证明圆角生效，但弧半径本身未量化。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（来自总 run-config，覆盖子题默认值）
文档版本或访问日期：未确认（文档页无版本号；缓存文件的落盘时间在 `tmp/.../_suite/docs/` 的 headers 里）
服务接口：`POST /snapshot`，请求体为 UTF-8 DSL 字符串，成功返回图像字节流，失败返回 JSON
`{code, message, requestId}`，其中 `position` 与 `near:` 摘录是本次定位问题最关键的信号。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| `open-snapshot.muedsa.com/ai-guide.md` | 请求体格式、UTF-8 编码、`Content-Type: image/png` vs `application/json` 的判定、错误响应结构、`/fonts` 查询 | 全部 16 次请求的实现 `tmp/.../A03/gen/a03_io.py` |
| `snapshot.muedsa.com/` → `reference-parser-tags.html` · EdgeInsets | `padding`/`margin` 只接受 `"12"`、`"(8,16)"`、`"(8,12,16,20)"` 三种格式，「括号和逗号是语法的一部分」 | I-01；最终稿根 `Container padding="(32,32)"` |
| 同上 · 颜色 | 「4 位与 8 位的最后一组是透明度（alpha）」，`#FF000080` 是约 50% 透明红色 | I-07、I-08；`#FFFFFF33` |
| 同上 · 坐标与矩阵 / Transform | 列主序 4×4、16 个有限 Float、外层必须有括号、值间不能有空格 | I-02、I-03；`matrix="(0.9902681,-0.1391731,…)"` |
| 同上 · Positioned / Stack | 「Positioned 必须是 Stack 或 IndexedStack 的直接子节点」；Stack 先布局非 Positioned 子节点 | I-06；最终稿全部绝对定位挂在根 `Stack` 下 |
| 同上 · Expanded 与 Flexible | 「固定使用 TIGHT」，「Expanded 强制填满分配到的主轴空间」 | I-10；弃用 Expanded，改固定 384 宽 |
| 同上 · Snapshot | 属性表只有 `background`/`debug`/`type` | I-04；画布尺寸移到根 `Container` |
| 同上 · Text | `fontSize`/`fontFamily`/`fontStyle`/`letterSpacing` 为可选项（未设置取默认） | I-05、I-11 |
| 同上 · 通用属性格式 | 裸属性回退为默认值不等价于 `true` | p8 加 `debug="true"` 而非裸写 `debug` |
| `snapshot.muedsa.com/` → `guides-painting.html` | **`ImageFiltered` 对子树结果应用 ImageFilter；`BackdropFilter` 对已经绘制在背后的区域应用滤镜** | I-09；说明卡四层拆分 |
| `snapshot.muedsa.com/` → `guides-layout.html` | `Container` 属性组合顺序（子节点→对齐→padding→装饰→约束→margin→transform）；`Spacer` 可作 Flex 直属子项 | 最终稿布局顺序 |
| `/fonts` | Inter 家族 7 个字重已安装；`Noto Sans SC` 未安装（只有 `Noto Sans CJK SC`） | 最终稿全部用 `fontFamily="Inter"` |

文档缓存与原始 headers 保留在 `tmp/.../_suite/docs/`（shared 归属，多题复用，不重复计为新请求）。

简述本次用到的能力：**布局** `Snapshot` > `Container`(定尺寸+padding) > `Stack fit="EXPAND" clipBehavior="NONE"` >
多个绝对定位兄弟节点；**文本** `Text` 的 `fontSize`/`fontStyle`/`letterSpacing`/`fontFamily`；
**颜色与透明度** `#RRGGBBAA`、命名色、`transparent`；**装饰** `Container` 的 `color`/`borderRadius`/`border="1 SOLID …"`；
**裁剪** `ClipRRect borderRadius="24"`；**变换** `Transform matrix`（列主序，绕中心 `alignment="CENTER"`）；
**滤镜** `BackdropFilter sigmaX/sigmaY tileMode="CLAMP"`。未使用任何外部图片，全部由 DSL 构造。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/r20261014T1536+0800-5f11da/A03/requests.jsonl`
迭代记录文件：`tmp/r20261014T1536+0800-5f11da/A03/iterations.jsonl`
渲染请求总数：16
成功次数：9
失败次数：7
重试请求数：1（`req-a03-probe5-layout`，`attempts=2`，第一次读取超时；该次无响应无日志）
DSL版本数：16 份草稿落盘 / 15 个不同版本实际提交（v2 提交两次：preview + final）
实际图片查看次数：11
完整视觉迭代数：1（v1 → v2）
未完成视觉迭代数：0
其他接口查询：`/fonts` 1 次（shared，本次未新增）

初次生成与查看计为基线，不计为改进迭代。语法修复（6 个单点探针 + 2 个 matrix 探针）、
对照实验（3 次）、重试（1 次）分别标识，不并入视觉迭代。

| 请求ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| req-a03-original-0001 | `dsl/system-pulse.v0-original.snapshot` | 23:53:51→23:53:58，7.609s | 400 application/json | `responses/req-a03-original-0001.body` | 无图像（错误 JSON）。PARSE_ERROR padding@91 |
| req-a03-probe-p1 | `dsl/system-pulse.p1.snapshot` | 23:54:59→23:55:01，2.188s | 400 application/json | `responses/req-a03-probe-p1.body` | 无图像。matrix@466 |
| req-a03-probe-p2 | `dsl/system-pulse.p2.snapshot` | 23:55:01→23:55:05，4.047s | 400 application/json | `responses/req-a03-probe-p2.body` | 无图像。matrix@440（=466−26） |
| req-a03-probe-p3 | `dsl/system-pulse.p3.snapshot` | 23:55:05→23:55:07，2.046s | 400 application/json | `responses/req-a03-probe-p3.body` | 无图像。matrix@439（−1） |
| req-a03-probe-p4 | `dsl/system-pulse.p4.snapshot` | 23:55:07→23:55:10，3.360s | 400 application/json | `responses/req-a03-probe-p4.body` | 无图像。matrix@467 |
| req-a03-probe-p5 | `dsl/system-pulse.p5.snapshot` | 23:55:10→23:55:12，2.094s | 400 application/json | `responses/req-a03-probe-p5.body` | 无图像。matrix@467，near 变成裸 `<Transform>` |
| req-a03-probe2-q1 | `dsl/system-pulse.probe2-q1.snapshot` | 23:56:26→23:56:28，1.703s | 400 application/json | `responses/req-a03-probe2-q1.body` | 无有效图像（204 B 错误 JSON，仍存了预览稿） |
| req-a03-probe3-p6 | `dsl/system-pulse.probe3-p6.snapshot` | 00:10:59→00:11:02，3.453s | 200 image/png | `responses/req-a03-probe3-p6.body` | 00:11:02 起查看：只剩标题 → 自查出自造嵌套错误 V-0 |
| req-a03-probe3-s1 | `dsl/system-pulse.probe3-s1.snapshot` | 00:11:02→00:11:04，1.875s | 200 image/png | `responses/req-a03-probe3-s1.body` | 00:11:04 起查看：BackdropFilter 结构成立 |
| req-a03-probe3-s2 | `dsl/system-pulse.probe3-s2.snapshot` | 00:11:04→00:11:06，1.906s | 200 image/png | `responses/req-a03-probe3-s2.body` | 00:11:06 起查看：文字在 BackdropFilter 子树内仍清晰 → 确认语义差别 |
| req-a03-probe4-p7 | `dsl/system-pulse.probe4-p7.snapshot` | 00:18:01→00:18:04，2.641s | 200 image/png | `responses/req-a03-probe4-p7.body` | 00:18:04 起查看：语法全修，画面仍只剩标题 |
| req-a03-probe4-p8 | `dsl/system-pulse.probe4-p8.snapshot` | 00:18:04→00:18:07，3.829s | 200 image/png | `responses/req-a03-probe4-p8.body` | 00:18:07 起查看：debug 层只有 2 个盒子 |
| req-a03-v1-preview | `dsl/system-pulse.v1.snapshot` | 00:18:07→00:18:11，4.046s | 200 image/png | `responses/req-a03-v1-preview.body` | 00:18:11 起查看：构图对，整体右下偏移 32px（缺陷 V-1） |
| req-a03-v2-preview | `dsl/system-pulse.v2.snapshot` | 00:21:43→00:21:50，6.875s | 200 image/png | `responses/req-a03-v2-preview.body` | 00:21:50 起查看：安全边距 min=32，逐项通过 |
| req-a03-probe5-layout | `dsl/system-pulse.probe5-layout.snapshot` | 00:32:23→00:32:26，2.219s（第 2 次；第 1 次读取超时 300s） | 200 image/png | `responses/req-a03-probe5-layout.body` | 00:32:26 起查看：四象限定位静默忽略机制；另看 T1/T4 两张放大裁图 |
| req-a03-v2-final | `system-pulse.snapshot`（与 v2-preview 相同） | 01:00:42→01:00:48，6.172s | 200 image/png | `system-pulse.png` | 01:00:48 起查看最终 PNG：题面要求逐项满足 |

时间均为 2026-10-15（除第一行 23:53 为 2026-10-14），时区 Asia/Shanghai (UTC+08:00)。
图像查看只记录真实下界：未记精确时刻，`viewed_not_before` 取该响应结束时间。

看图发现的问题（均已在后续版本修复）：
V-0（p6 自造嵌套错误）、I-04/I-05/I-06（语法修复后内容大面积缺失）、
I-07（`#33FFFFFF` 渲染成不透明青色）、I-08（`#FFFFFF44` = 26.7% 而非 20%）、
I-09（`ImageFiltered` 把文字一起糊掉）、I-10（`Expanded` 覆盖固定尺寸）、V-1（漏减 32px 平移）。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| p1 语法修复 / v0 | padding 报 PARSE_ERROR@91 | 文档：括号逗号是语法的一部分 | `"24 32"` → `"(24,32)"` | 错误消失，轮到 matrix@466 | `dsl/p1` |
| p2 语法修复 / v0 | 想删 Snapshot 上不存在的 width/height | 字节级证明被静默忽略：错误位置精确左移 26 = 被删字节数 | 移除；尺寸移到根 Container | 仍 400，同一 matrix 错误 | `dsl/p2` |
| p3 语法修复 / v0 | kebab 属性名 `font-size` | 同上，位置只移 1 字节 | 改 `fontSize` | 仍 400 | `dsl/p3` |
| p4 语法修复 / v0 | `Positioned` 直接放 `<Row>` 里 | 文档：Positioned 必须是 Stack 直接子节点 | 包进 `Stack fit="EXPAND"` | 仍 400 | `dsl/p4` |
| p5 语法修复 / v0 | `<Transform rotate="-8">` | 文档：无 rotate，matrix 必填 | 删 rotate | 错误不变，near 变成裸 `<Transform>` | `dsl/p5` |
| probe2-q1 语法修复 / v0 | matrix 值算对但缺外层括号 | 文档：外层必须有括号 | 加括号 | 仍 400（q2/q3 读取超时，无记录） | `dsl/probe2-q1`、`dsl/probe2-q2` |
| probe3-p6 语法修复 / v0 | 返回 200 但只剩标题 | 自查：我多加 `<Container>` 漏闭合（自造缺陷 V-0，非原稿） | 改用 probe4-p7 重做 | p6 不能当基线 | `preview/probe3-p6.png` |
| probe3-s1/s2 对照 / — | 「只模糊卡内背景」怎么做 | 文档：`ImageFiltered` 作用子树结果，`BackdropFilter` 作用背后已绘区域；s2 实测文字在子树内仍清晰 | `ClipRRect` + `BackdropFilter`，卡体与文字作为滤镜之后的兄弟节点 | 结构成立，v2 采用 | `preview/probe3-s1.png`、`probe3-s2.png` |
| probe4-p7/p8 语法修复 / v0 | 语法全修，画面仍只剩标题 | p8 加 `debug="true"`：布局树只有 2 个盒子 | 不改，继续定位 | 把猜测变成事实 | `preview/probe4-p7.png`、`probe4-p8.png` |
| probe5-layout 对照 / — | 定位静默丢子节点与 alpha | 四象限：T2 `Row>Stack>Positioned>Text` 空白；T1 `Expanded` 拉满 576；T4 青色 + 26.7% 白 | 全部绝对定位挂根 Stack；固定 384 宽；alpha 改末两位 | 三类问题全部定位 | `preview/probe5-layout.png` + 2 张裁图 |
| v1 视觉迭代 / probe4-p7 | 首个完整设计版 | 按题面重构全部元素 | 1280×800 根容器 + 44 标题 + 96×36 LIVE + 3×384 卡 + 500×150 说明卡 + 5 细条 + BackdropFilter + REVIEW | 构图对，但整体右下偏移 32px（V-1） | `preview/v1.png`、`v1-inspect.json` |
| v2 视觉迭代 / v1 | V-1：根 padding 平移了 Stack 原点 | padding 平移坐标原点，而 Positioned 写的是画布绝对坐标 | 常量改画布绝对值，`<Positioned>` 统一经 `L()/T()` 减 32；alpha 改 `#FFFFFF33` | 安全边距 min=32，20 项全通过 | `preview/v2.png`、`v2-inspect.json`、`alpha-check.json` |
| v2-final 重试交付 / v2 | 把真实响应写入输出目录 | 同一 DSL 重提交 | 无内容改动 | 48526 B，与 preview 同字节数 | `system-pulse.png` |

**从文档了解到、但本次未触发的注意事项**（不算本次踩坑）：
`Gradient` 的 `gradientBegin`/`gradientEnd` 属性、`IndexedStack` 的 `index`、
`ColorFiltered` 的 `blendMode`、`boxShadow` 与 `clipBehavior` 的交互（文档明确说
「需要无条件限制在容器边界内时外包 `<ClipRect>`」，本次用 `clipBehavior="NONE"` 反而需要它）——
最终稿的说明卡细条确实越出了卡体，是靠根 Stack 的 `clipBehavior="NONE"` 保留下来的。

## 5. 任务耗时与请求统计

结构化指标文件：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-14T23:52:20+08:00 → 2026-10-15T01:21:00+08:00 | ISO 8601 带时区 | 输出根 `suite-state.json` 的 A03 记录 / 本文件生成时刻 |
| 任务总耗时 | 5340 | 秒 | 上述两点墙钟差 |
| 首次可用图耗时 | 1122 | 秒 | 起点 → `req-a03-probe3-p6` 结束 00:11:02+08:00（首个 200） |
| 等待用户反馈 | 0 | 秒 | 单轮任务，无反馈等待 |
| 限流等待 | 0 | 秒 | 确认未发生：16 次请求 `X-RateLimit-Remaining` 始终 115–119，无 429、无 `Retry-After` |
| 排队等待 | null | 秒 | 不可测：服务未返回排队字段，`Server-Timing` 只有 `render;dur` 与 `total;dur` |
| 已记录请求耗时之和 | 56.06 | 秒 | `requests.jsonl` 的 `elapsed_ms` 求和（客户端视角，含 DNS/TLS/重试，可含重叠） |
| 服务端 `total;dur` 之和 | 8065.2 | 秒 | `Server-Timing` 解析；**与上项含义不同，不可相加** |
| 服务端 `render;dur` 之和 | 7207.6 | 秒 | 同上 |
| 成功、失败、重试请求 | 9 / 7 / 1 | 次 | `requests.jsonl`；重试是总数子集 |
| 无响应的尝试 | 3 | 次 | probe2 的 q2/q3 与 probe5 第 1 次均在读取阶段超时，未写日志——见 `unresolved_issues` |
| 实际看图与完整视觉迭代 | 11 / 1 | 次 | `iterations.jsonl` + 最终 PNG 看图记录 |
| DSL 版本 | 16 草稿 / 15 提交 | 份 | `dsl/` 目录计数 / 去重后的提交版本 |

任务总耗时 5340s **不等于** 请求耗时之和 56.06s：差值是本地构造 DSL、二分定位、
像素测量、逐图查看与文档查阅的墙钟时间。请求耗时总和是客户端视角且可含重试，
`Server-Timing` 是服务端视角，两者不可相加。

## 6. 设计选择、经验与未解决事项

### 设计选择

- **用固定宽度而非 flex 实现「等宽」**：`Expanded flex="1"` 覆盖子节点固定尺寸（I-10 实测），
  而固定 384px 让「等宽」变成可断言的 `max_width_delta=0`。可测性优先于 DSL 写法惯例。
- **说明卡拆四层而非用一个装饰容器**：这是「只模糊卡内背景」的唯一正确结构，
  因为 `BackdropFilter` 只模糊它之前绘制的图层。用 `ImageFiltered` 会把文字一起糊掉。
- **`ClipRRect` 限定模糊区域 + 根 `Stack clipBehavior="NONE"` 保留越界细条**：两个相反的裁剪策略共存，
  一个把模糊圈在卡内，一个让细条自由伸出卡外 140px。
- **旋转用矩阵 + `alignment="CENTER"`**：绕自身中心旋转，否则绕画布左上角会把标签甩出安全区。
- **调色**：深底 `#0B1220` 上，三张指标卡分别用 `#38BDF8`/`#FBBF24`/`#34D399` 作强调色；
  说明卡边框复用 `#38BDF8`，五条细条用 5 种高饱和色形成穿过效果。
  字体统一 `Inter`（`/fonts` 确认 7 个字重可用；`Noto Sans SC` 未安装）。

### 可复用经验

1. **服务返回的错误 `position` 等于 DSL 里出错标签的 UTF-8 字节偏移**。
   本次用这个规律把「静默忽略」变成可验证事实：只删 26 字节，错误位置就从 466 精确左移到 440。
   这是区分「真实报错」和「静默忽略」最便宜的手段——改一处、看 position 移了多少。
2. **修好语法不等于内容正确**。p7/p8 是本次最有价值的两个请求：HTTP 200、PNG 正常，
   画面却只剩标题。`debug="true"` 让布局盒子可见，直接把「内容消失」变成可定位的事实。
   遇到「出图但缺内容」，第一反应就该开 debug 层，而不是继续猜 DSL。
3. **一图四象限二分定位**：一个请求同时验证 4 个假设（probe5），比逐个探针省请求，
   且四格互为对照。
4. **alpha 语义用「众数 vs 理论上叠值」核验**，而不是肉眼看「够不够淡」。
   量化后可直接算出 26.66% vs 20%，肉眼只能看到「偏灰」。
5. **测量脚本里的 float/int16 陷阱**：`dtype=np.int16` 会把 0.299/0.587/0.114 截断成全 0，
   让所有梯度恒为 0，把正确渲染误判成无差别。这类静默失效和 DSL 的静默忽略性质一样。
6. **排除测量污染源**：卡内锐度测量必须排除卡体自身边框行和文字笔画列，
   否则测到的 138.46 是边框跳变而不是背景模糊，结论完全反转。

### 未解决事项

1. **3 次提交没有 HTTP 响应**（probe2 的 q2/q3、probe5 第 1 次）：均在读取阶段 `TimeoutError`。
   没有响应 body、没有 `requests.jsonl` 记录。真实 HTTP 尝试数是 19 而日志是 16 条。
   不补造记录，已在 `task-metrics.json` 的 `unresolved_issues` 如实列出。
2. **`tmp/.../A03/v2.json` 被最终提交覆盖了 preview 的记录**：`--final` 运行把 preview 写入的
   `final: false` 那份覆盖成了最终记录。两个请求都在 `requests.jsonl` 里，PNG 字节数一致（48526 B），
   preview 副本 `preview/v2.png` 完整保留。这是留痕上的小瑕疵，不影响可复现性。
3. **排队等待不可测**：服务无相关字段，记 `null`，不记 0。
4. **查看时刻只有下界**：图像查看未记精确时刻，`viewed_not_before` 取响应结束时间。
5. **说明卡圆角弧半径未量化**（见 §1 局限）。

### 留痕确认

`tmp/.../A03/` 下草稿、备选方案、请求快照与 headers、7 份失败响应 body、16 份 DSL 版本、
11 张预览图（含 2 张放大裁图）、4 份像素测量报告、生成脚本与迭代日志全部保留，未清理、未覆盖尝试。
失败响应没有被当作最终图片；没有把未知属性原样留在源码里来声称实现需求
（最终稿不含 `rotate`、`font-size`、`Snapshot` 上的 `width/height`、`Row` 内的 `Positioned`）。
文档缓存与 `/fonts` 结果在 `tmp/.../_suite/docs/`（shared 归属），本次未重复计为新请求。

总任务根的 [.gitignore](../../../.gitignore) 已在启动时创建，只忽略 `__pycache__/`、`*.pyc`、`*.pyo`、
`.pytest_cache/`、`.ruff_cache/` 等运行时缓存；未用 `tmp/`、`outputs/`、`cache/`、`*.log`
或整体图片/DSL/JSON 通配规则排除过程证据。运行时缓存不列为产物或自检证据。
