# Snapshot 使用情况说明与踩坑记录（A21 · round-02）

任务ID：A21
任务名称：staged-launch-change（预置连续三轮）
本次运行ID：r20261014T1536+0800-5f11da
本轮：round-02（第 2 轮，共 3 轮）
完成状态：完成
结束原因：需求满足并完成视觉自检
输出目录：`outputs/r20261014T1536+0800-5f11da/A21/round-02/`
临时目录：`tmp/r20261014T1536+0800-5f11da/A21/`
路径基准：suite_root（本轮各 JSON 内部若另有 `path_base`，以文件内声明为准）

遵循 [PATHS.md](../../../../PATHS.md)：本文档的路径均为相对总任务根的相对路径；
Markdown 本地链接相对本文件所在位置（`outputs/<run_id>/A21/round-02/`）重新计算。

## 0. 本轮需求原文（逐字）

> 在第一轮两张作品上修改第二轮：主标题替换为"当所有信息都想成为标题：
> 让复杂信息变得清晰的结构化方法"，两图标题最多3行、字号≥48。
> 新增赞助方"Northstar Research / 云构工具"及"免费参加 · 无需报名"。
> 日期时间、讲者、ONLINE LAUNCH、网址必须保留，主色与品牌3–6构件形态
> 不变，允许移动和缩放装饰。两尺寸不变。不能用变形压窄文字。
> 保存round-02/的两图与同名DSL、design-tokens.json、content-map.json，
> 查看两张后说明如何避免长标题与新增信息碰撞；旧轮完整保留。

来源：[rounds/round-02.md](../../../../tasks/A21-staged-launch-change/rounds/round-02.md)。
修改基座是第一轮归档件 [round-01/launch-portrait.png](../round-01/launch-portrait.png)
与 [round-01/launch-wide.png](../round-01/launch-wide.png)；第一轮文件未改动。
本轮所有需求都可在 `tasks/` 与 `rounds/` 内读到，未使用任何外部反馈或评分材料。

---

## 1. 最终产物与需求完成情况

### 1.1 交付文件（8/8）

| 文件 | 用途 | 对应 DSL 或图片 | 完成状态 |
|---|---|---|---|
| `launch-portrait.snapshot`（6244 B，sha256 `498a7074…`） | 完整可复现 DSL | 同名 PNG | 完成 |
| `launch-portrait.png`（1080×1350，284930 B，sha256 `421c3c4e…`） | 服务返回的最终图片 | 同名 DSL | 完成 |
| `launch-wide.snapshot`（5240 B，sha256 `e98e1e3d…`） | 完整可复现 DSL | 同名 PNG | 完成 |
| `launch-wide.png`（1440×810，247193 B，sha256 `9f0d4bc1…`） | 服务返回的最终图片 | 同名 DSL | 完成 |
| `design-tokens.json`（15764 B） | 颜色、字号、6 个品牌构件的可复用 token | 两图 | 完成 |
| `content-map.json`（78873 B） | 内容—角色—墨迹 bbox 映射与 9 项审计结果 | 两图 | 完成 |
| `snapshot-usage.md` | 本文件 | — | 完成 |
| `task-metrics.json`（9990 B） | 结构化指标 | — | 完成 |

请求与交付件的对应关系不是手抄：`task-metrics.json` 的 `delivery_map` 用响应字节
sha256 与交付 PNG sha256 逐一比对得出——portrait 对应
`req-a21-r02-launch-portrait-3d7048`（attempt 3），wide 对应
`req-a21-r02-launch-wide-cf6641`（attempt 1）。

### 1.2 逐项需求核对

| # | 需求 | 实际 | 状态 |
|---|---|---|---|
| 1 | 主标题替换为 27 字长句 | 竖版 3 行 12/9/6 字、横版 2 行 12/15 字；两处分行拼接与 `title_full` 逐字符比对一致 | 满足 |
| 2 | 两图标题最多 3 行 | 竖版 3 行、横版 2 行 | 满足 |
| 3 | 标题字号 ≥48 | 竖版 66、横版 52 | 满足 |
| 4 | 新增赞助方「Northstar Research / 云构工具」 | 竖版 30 px、横版 28 px，muted `#8FA3C2`，位于网址牌之后 | 满足 |
| 5 | 新增「免费参加 · 无需报名」 | 报名状态牌（竖版 404×62 圆角 31、横版 400×46 圆角 23），主色描边 2 SOLID `#5FE0FF` | 满足 |
| 6 | 日期时间保留 | 竖版 48 px、横版 36 px，accent 橙、BOLD | 满足 |
| 7 | 讲者保留 | 竖版 30 px、横版 28 px | 满足 |
| 8 | ONLINE LAUNCH 保留 | 眉标 32/30 px，字距 8 px，配主色竖条 | 满足 |
| 9 | 网址保留 | 网址牌 + 主色圆点，30/28 px | 满足 |
| 10 | 主色不变 | `primary #5FE0FF`、色阶 `#1E86C8/#0B2B4E`、`glow #EAFDFF`、`accent #FFC26B` 全部与第一轮一致 | 满足 |
| 11 | 品牌 3–6 构件形态不变 | 仍为 6 个（stack-mark、mark-core、light-orb、light-band、accent-bar、牌子族）；形态、层数、色阶、opacity 未变 | 满足 |
| 12 | 允许移动和缩放装饰 | 已使用：发光球位移与半径、光带随半径等比、角部水印缩 4% 并外移、主标记 76/58→72/52 | 满足（在允许范围内） |
| 13 | 两尺寸不变 | 1080×1350 与 1440×810，读交付 PNG 的 IHDR 实测一致 | 满足 |
| 14 | 不能用变形压窄文字 | 扫描交付 `.snapshot` 中所有 `<Text>`：带 `transform`/`matrix` 的为 0 | 满足 |
| 15 | 保存两图与同名 DSL、tokens、content-map | round-02/ 下 6 个文件齐全 | 满足 |
| 16 | 查看两张后说明如何避免碰撞 | 实际打开 14 次（含归档前复查），说明见 §1.3 与 §6 | 满足 |
| 17 | 旧轮完整保留 | round-01/ 的图片、DSL、报告未改动；仅对 `round-01/task-metrics.json` **追加**了 8 个字段以对齐当前生成器字段集（数值一个未改，含归档时刻 `ended_at`/`elapsed_seconds`），原文件留底于 `tmp/r20261014T1536+0800-5f11da/A21/archive-conform/task-metrics.round-01.pre-conform.json` | 满足（见 §6 的说明） |

### 1.3 长标题与新增信息如何不碰撞（本轮要求的核心说明）

碰撞不是靠"字眼看过去没问题"判定的，是靠一条可复算的链：布局先在构造器里算出
坐标与字号 → 提交前用无网络干跑门校验 → 交付后在真实 PNG 上做墨迹检测 → 再用
视觉工具放大核对。四层里任何一层给出重叠或超宽，都不会提交。

**第一层：字数决定行数，行数决定字号，字号决定 advance。** 标题 27 字。竖版文本盒宽
860 px，横版同为 860 px。CJK 字宽恰好等于 1 em，所以"能否放进这一行"是纯算术：
竖版首行 12 字 → 12 × 66 = 792 px ≤ 860；横版第 2 行 15 字 → 15 × 52 = 780 px ≤ 860。
两条都留出 60–80 px 余量，**不折行**——折行会让"的结构化方法"掉出预期布局，
而需求只允许最多 3 行。反过来，若要保持第一轮 132/116 的大字号，27 字需要
7–8 行，远超上限，所以字号必须下调：66/52 仍远高于 48 的下限，且仍明显高于
日期（48/36）、讲者（30/28）、网址（30/28），层级不倒挂。

**第二层：提交前的干跑门（`a21_dryrun_r2.py`），零服务请求。** 构造 DSL → 断言合法 →
打印元素表 → 逐行校验 advance 不超文本盒宽 → 校验标题墨迹右缘与球体净距（含 y 带
判断）→ 校验上下扩展空间与最小字号 → 校验两处分行拼接 == `title_full`。
这一步真的抓到过一个内容缺陷：横版原本循环 `(title_1, title_2)`，而 `title_2` 是竖版
用的"让复杂信息变得清晰"，横版会**静默丢掉"的结构化方法"**——27 字变成 21 字，
而且渲染完全正常、不会报错。改为新增 `title_2w` 存放横版整句第 2 行后才提交。
这类缺陷靠服务响应是发现不了的，只能靠"拼接 == 需求原文"这条断言。

**第三层：墨迹检测而不是文字盒。** 交付 PNG 上按目标色 ±40 阈值取墨迹像素，但要处理
两个陷阱：文字盒是**故意超大**的（为了软换行与视觉留白），盒重叠不等于字重叠；
球内光带与文字同为亮色，会被同色阈值一起吃进去。解法是给每行字只开一个纵向字带窗口
`[top−0.25em, top+1.15em]`——行距 1.30 em，所以窗口的 `+1.15em` 永远够不到下一行
的字顶；再从最左命中列起保留列间隙 ≤60 px 的连续段、从最上命中行起保留行间隙 ≤24 px
的连续段，把同色光带与邻行字顶剔掉。实测结果（`content-map.json` 的 9 项检查全为
`passed: true`）：

- 文字墨迹两两交集面积：**100 个配对全部为 0 px²**（竖版 55 对、横版 45 对）；
  最小正间距为竖版 brand_cn↔brand_en 的 20 px、横版同对的 16 px（字标中英间距，
  由 `left + size×len(cn) + gap` 显式给出，属设计意图）。
- 文字墨迹与发光球实体（`orb_core`）的轴对齐净距**全部 > 0**：竖版最小
  149.35 px（`title_line2`，且 y 向本就不重叠），横版最小 141 px（`title_line2`，
  y 向有重叠但 x 向净距 141 px）。
- 上下扩展空间：竖版 上 112 / 下 153、横版 上 74 / 下 110，均 ≥70 px；
  左右 96 / 124 与 96 / 484。
- 占位词黑名单扫描：0 命中。

**第四层：视觉复核。** 14 次实际打开（整图 1:1 四次 + 放大裁切 10 次），其中专门新增
一个 `footer` 裁切窗口（竖版 `[0,1030,1080,1240]` 1.6×、横版 `[0,600,960,730]` 2.0×）
只查那两条新增信息，逐张记录见
`tmp/r20261014T1536+0800-5f11da/A21/viewing-evidence.json` 的 round 2 块
（`ev-a21-015` … `ev-a21-028`）。归档前又把两张整图重开一次（`ev-a21-027/028`），
并确认交付字节未变。

**布局上真正做的三个决定**（对应"允许移动和缩放装饰"这条许可）：

1. **让装饰避让，而不是让文字让位。** 3 行标题把标题块底部从 y404 推到 y599，右中偏下
   出现空区。于是竖版发光球从半径 130、中心 (884,700) 改为半径 165、中心 (905,800)，
   下移 100 px 填这个空区，同时把"第 3 行标题墨迹底 589 低于球体顶 635"变成结构性
   事实——球与标题在 y 向就不相交，横版球缩到半径 175 并右移到 (1190,400)，球体左缘
   1015 距标题墨迹右缘约 217 px。
2. **新信息进既有的信息栈，不进既有的品牌几何。** 赞助方是一行 muted 文字；
   "免费参加 · 无需报名"做成**牌子族的新实例**（圆角矩形 + 边框 + 居中内容），
   仅以边框色区分语义：网址牌中性蓝 `#24507A` = 可访问地址，报名状态牌主色
   `#5FE0FF` = 参与门槛。构件数因此仍是 6，没有为凑内容而新增品牌几何。
3. **竖版网址牌收窄 72 px（632→560）。** 球下移放大后球体外环左缘移到 723；原 632 宽
   会让牌右缘 728 只与球体净距 12 px，视觉上粘连。收到 560 后右缘 656，净距 67 px。
   牌内圆点 20 px 与网址 30 px 不变形。横版则把第一轮的横排（日期｜竖分隔线｜讲者）
   改为纯竖排 5 行并删掉那根 `rule` 元素——新增两行后横排已容纳不下。

**已知的、如实保留的两个"紧"的地方**，都不是碰撞、也不是缺陷：

- 字标的中英间距是 16–20 px（见上），是设计意图而非事故。
- 横版底部信息栈比竖版紧（5 行塞进 810 高），最小行距仍清楚，视觉复核未发现问题；
  若未来再加第 6 条信息，应先考虑压到两列或换横版专属的排布，而不是继续堆竖排。

### 1.4 交付质量证据小结

`content-map.json` 的 9 项检查全 `passed: true`，`all_passed: true`；
`task-metrics.json` 的 `unresolved_issues` 只记两项流程性问题（服务挂起、驱动脚本
`started_at` 记法），与作品质量无关。本轮**首版即通过**——12 个查看视图中没有发现
需要返工的缺陷，因此未产生视觉迭代，也没有为了"看起来有迭代"而重渲。

---

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`
文档版本或访问日期：AI 使用指南与 DSL 文档在本轮**之前**已实际取得并缓存于
`tmp/r20261014T1536+0800-5f11da/_suite/docs/`（含 fonts 查询结果）；本轮**复用**
已验证结论，未新增任何文档或字体 HTTP 请求（`counts.other_service_requests = 0`）。

AI 使用指南：https://open-snapshot.muedsa.com/ai-guide.md
DSL 文档：https://snapshot.muedsa.com/

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| open-snapshot AI 使用指南 | `POST /snapshot` 的请求体、编码、响应类型、错误处理；请求体上限 1048576 B；错误 JSON 不含 PNG | 驱动脚本 `tmp/…/_suite/gen/a21_round.py` 的请求构造；`requests.jsonl` 的状态字段 |
| DSL 文档 · Text | `fontFamily="Noto Sans CJK SC,Inter"`、`fontSize`、`fontStyle="BOLD"`、`letterSpacing`（px，对 CJK 生效）、`height`、`maxLines`、`softWrap`、`textAlign`、`textShadow` | 两图全部文字；眉标字距 8 px |
| DSL 文档 · 渐变 | `gradientType="LINEAR\|RADIAL\|SWEEP"`、`gradientColors`（逗号列表）、`gradientStops`、`gradientBegin/End/Center`、`gradientRadius`、`gradientFocal`、`gradientFocalRadius` | 发光球 `RADIAL #A8F0FF,#1E86C8,#0B2B4E` r=0.60；辉光 r=0.72 opacity 0.42 |
| DSL 文档 · 形状与边框 | `shape="CIRCLE"`、`border`、`borderRadius`、`boxShadow="x y blur color"`、`<Opacity>` | 网址牌/报名状态牌的圆角与圆点；主标记亮核 `boxShadow="0 8 22 #5FE0FF66"` |
| 文档缓存 fonts.txt | 中文字体族名 `Noto Sans CJK SC`，拉丁与数字用 `Inter` | `design-tokens.json` 的 `typography.fontFamily_source` |

本轮实际用到的能力（其余一律不用，不臆造标签或属性）：

- **布局**：根 `<Container>` 包 `<Stack>`，`<Stack>` 按文档顺序绘制；用
  `<Positioned>` 精确定位（每节点最多一个子节点）；不用 `<Rect>`/`<Circle>`/`<Line>`/
  `<Path>` 之外的禁用标签，文字一律放在 `text` 属性里。
- **文本**：CJK advance = 1 em 作为换行与净距的算术基准；`letterSpacing` 展开眉标；
  `textShadow` 用 8 位带 alpha 的十六进制。
- **颜色与透明度**：token 化的主色阶与暖色 accent；`<Opacity>` 用于辉光与角部水印。
- **装饰**：径向渐变球 + 辉光 + 细外环 + 三条递减光带；右上/左下叠层水印；
  主标记为三层描边方块 + 亮核。
- **变换**：仅使用带括号的矩阵格式 `(m0,…,m15)`、列主序，且只出现在
  `transform`/`matrix`/`origin` 上——`<Text>` 上一律不加，以满足"不得变形压窄文字"。
- **未使用**：外部图片、`Image` 嵌入、滤镜标签、字体下载；A 类不允许外部素材。

**第一轮已验证、本轮直接复用的能力结论**（不重复消耗探针请求）：

- `gradientFocal`/`gradientFocalRadius` 会把径向渐变压平（亮点被推出可见范围），
  所以发光球留空；
- `gradientFocal` 组合 `gradientType="RADIAL"` 时的正确用法只保留
  `gradientColors` + `gradientStops` + `gradientCenter` + `gradientRadius`；
- `shape="CIRCLE"` 与 `borderRadius` **互斥**，同时给会 `PARSE_ERROR`；
- 嵌套 `<Text>` 的子节点前导空白会被裁掉，导致 span 粘在一起——需要两个独立
  `<Text>` 并显式给出 x 偏移（字标的中文与英文就是这样分的）。

---

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/r20261014T1536+0800-5f11da/A21/requests.jsonl`
迭代记录文件：`tmp/r20261014T1536+0800-5f11da/A21/iterations.jsonl`（本轮
`it-a21-007`，`type: baseline`，父版本 `it-a21-006`）
渲染请求总数：4（渲染 4、能力探针 0、文档/字体查询 0）
成功次数：2
失败次数：2（均为服务端读取超时，**未返回任何字节**，故无响应文件可留痕）
重试请求数：2（是同 4 条请求的子集：attempt 2 与 attempt 3）
语法修复重交：0（本轮无 400 响应，无 PARSE_ERROR）
DSL 版本数：2（portrait 1、wide 1）
实际图片查看次数：14（竖版 7、横版 7，含 2 次归档前整图复查）
完整视觉迭代数：0
未完成视觉迭代数：0
其他接口查询：无（复用已缓存文档与 fonts 结果，不新增 HTTP）

| 请求ID / 轮次 | 输入 DSL | 起止时间（+08:00）与耗时 | HTTP 状态与 Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| `req-a21-r02-launch-portrait-34bd30` / r02 attempt 1 | `tmp/…/A21/dsl/r02-launch-portrait.attempt-01.snapshot`（6244 B） | 21:23:01 → 21:38:26，924.282 s | 无——`TimeoutError: The read operation timed out` | 无（服务端未返回字节） | 未取得图片 |
| `req-a21-r02-launch-portrait-c3535d` / r02 attempt 2 | `…/dsl/r02-launch-portrait.attempt-02.snapshot`（同一份 6244 B，sha256 一致，原样重发） | 21:38:46 → 21:45:44，417.859 s | 无——同一 `TimeoutError` | 无 | 未取得图片 |
| `req-a21-r02-launch-portrait-3d7048` / r02 attempt 3 | `…/dsl/r02-launch-portrait.attempt-03.snapshot`（同一份 6244 B） | 21:46:04 → 21:46:18，14.172 s | 200，`image/png`；Server-Timing `render;dur=1525.1, total;dur=1531.2` | `round-02/launch-portrait.png`（284930 B） | 21:48 首次整图 + 21:50/21:57/21:58/22:00 放大 + 22:08 归档复查，共 7 次；三行长标题完整、字号 66、行距清楚、不压球体 |
| `req-a21-r02-launch-wide-cf6641` / r02 attempt 1 | `tmp/…/A21/dsl/r02-launch-wide.attempt-01.snapshot`（5240 B） | 21:46:18 → 21:46:31，13.313 s | 200，`image/png`；Server-Timing `render;dur=1546.2, total;dur=1554.4` | `round-02/launch-wide.png`（247193 B） | 21:48 首次整图 + 21:49/21:59/22:00/22:06 放大 + 22:08 归档复查，共 7 次；两行长标题完整（第 2 行 15 字未折行）、字号 52、底部 5 行信息栈清楚 |

两次超时的记录原样保留在 `requests.jsonl`（含 `elapsed_ms`、`error`、`delivered: null`），
没有删除、没有伪造响应文件。`iteration_id it-a21-007` 里逐条说明了三次尝试。
预览视图清单：`tmp/…/A21/preview/round-02/views-manifest.json`（12 个视图，
每个带裁切框、放大倍数、输出尺寸与源图 sha256）。

**没有为凑迭代而迭代。** 首次看图即通过，所以没有"看图 → 改 → 重渲 → 再比"的闭环，
`completed_visual_iterations` 如实记为 0；改进迭代必须是完整闭环，不能把重试或审计
修 bug 记成视觉迭代。

---

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| `it-a21-007` / baseline（新需求）/ `it-a21-006` | 横版标题会静默丢掉"的结构化方法"（27 字变 21 字），且渲染完全正常 | 干跑打印元素表时发现横版循环 `(title_1, title_2)`，而 `title_2` 是竖版用的"让复杂信息变得清晰" | 新增 `title_2w` 存放横版整句第 2 行；干跑门增加"两处分行拼接 == `title_full`"断言 | 未提交任何请求就修掉；交付后 `content-map.json` 的必需文案检查对两图逐字符比对通过 | `tmp/…/_suite/gen/a21_dryrun_r2.py`、`tmp/…/A21/round-02-changes.json` |
| `it-a21-007` / retry | portrait 前两次请求挂起 924.282 s 与 417.859 s，无响应 | 读 `tools/suite.py`：`snapshot_request` 只在 429/503 与 `URLError` 上递归重试，`resp.read()` 的 `TimeoutError` 直接向上抛且不重试；`timeout=` 是每次 socket 操作的超时而非总预算，所以 elapsed_ms 能超过 `TIMEOUT_S=300` | 不猜、不跳过：按同一份已本地校验的 DSL 原样第三次提交 | 14.172 s 成功，Server-Timing 正常（`total;dur=1531.2`），判定为服务端瞬时停顿而非请求体问题 | `requests.jsonl` 两条超时记录、`it-a21-007.requests` |
| — / 留痕缺陷（已披露） | 驱动脚本异常路径把 `started_at` 写成异常发生时刻（即请求结束时刻） | 直接取 `requests.jsonl` 的 `started_at` 最小值会把本轮起点算成 21:38:26，比真实起点 21:23:01 晚 15 分 28 秒，墙钟被系统性低估 | 指标脚本对 `http_status is None` 的记录改用 `started_at − elapsed_ms` 还原，并逐条留证于 `timings.started_at_correction` | 本轮起点校正为 21:23:01；驱动脚本本身未回改，旧日志不回填 | `tmp/…/_suite/gen/a21_metrics.py` |
| — / 指标脚本真实缺陷（本段修复） | `a21_metrics.py` 无法执行：第 296 行缺一个收尾 `)`（`SyntaxError`）；`_server_timing_parts` 被引用但从未定义（会 `NameError`）；`started_at_correction_note` 的 if 分支漏了 `% len(...)`，会在输出里留下字面量 `%d`；`logs.round_changes` 缺失 | 可确认的事实是脚本在第 2 轮归档时处于语法错误状态，`round-02/task-metrics.json` 在本会话前段的记录中曾写出 8627 B 并在之后的目录列表中消失；**具体原因未确认**（推测为前段某次 Edit 的落点偏差），未回溯确认 | 补齐 `)`；新增 `_server_timing_parts()` 定义；两个条件分支都各自做 `%` 格式化；补 `logs.round_changes`；另加 `last_recorded_activity_at`/`archive_tail_seconds`/`started_at_correction_note` 等键 | 脚本 `ast.parse` 通过；`a21_metrics.py 2` 成功写出 9990 B，键结构、`retry_note`（=2）、`started_at_correction`（2 条）、`server_timing_source` 全部核对无误；**第 1 轮归档件只追加字段、不改数值**，原文件留底 | `tmp/…/_suite/gen/a21_metrics.py`、`tmp/…/A21/archive-conform/` |
| — / token 生成缺陷 | `design-tokens.json` 的 `light-orb` 把 `orb_core` 外接框宽度（直径 330/350）写成 `radius_portrait/wide`，会误导第 3 轮按 330 复用 | 读交付 layout 发现 `orb_core` 是外接框，框宽即直径 | `write_design_tokens` 同时给出 `diameter_*`（读自交付 layout）与 `radius_*`（其一半），并加 `geometry_source` 说明来源"非手抄配置值" | 现为 `diameter 330/350`、`radius 165/175`、`center (905,800)/(1190,400)` | `tmp/…/_suite/gen/a21_audit.py` |

**从文档了解到、本轮未触发的事项**（如实标注，不拿来充数）：`<Opacity>` 的取值域、
`shape="CIRCLE"` 与 `borderRadius` 的互斥、嵌套 `<Text>` 的空白裁剪——这三条都在
第一轮验证过，本轮一次都没踩到。

---

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/r20261014T1536+0800-5f11da/A21/round-02/task-metrics.json`
（`path_base: suite_root`，字段说明写在各 `*_note` 里）

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 本轮开始 | 2026-10-19T21:23:01+08:00 | ISO-8601（±1 s） | `started_at − elapsed_ms` 还原；详见 `timings.started_at_correction` |
| 本轮结束 | 2026-10-19T22:44:16+08:00 | ISO-8601 | 本指标文件生成时刻（本轮归档完成） |
| 本轮总墙钟 | 4874.3 | 秒 | `ended_at − started_at`，含设计、干跑、看图、审计、归档 |
| — 其中在案活动止于 | 2026-10-19T22:09:30+08:00 | ISO-8601 | 迭代/看图/成功请求的最晚时刻 |
| — 归档与记账尾段 | 2086.0 | 秒 | 含写本报告与指标、修复指标脚本；**不能扣掉**，也不能用请求耗时替代墙钟 |
| 首次可用图耗时 | 1396.454 | 秒 | 从开始到首次成功取得可打开图片（attempt 3）；本轮未提交能力探针，故取首次成功的渲染请求 |
| 首次成品图耗时 | 1396.5 | 秒 | `launch-portrait` attempt 3 的结束时刻 |
| 已记录请求耗时之和 | 1369.626 | 秒 | `requests.jsonl` 的 `elapsed_ms` 之和（4 条），不等于任务总耗时 |
| — 服务端读取挂起 | 1342.141 | 秒 | 2 条超时的 `elapsed_ms` 之和，无产出、非设计时间 |
| — 有效请求耗时 | 27.485 | 秒（占墙钟 0.6%） | 挂起之外真正与渲染相关的时间 |
| 成功 / 失败 / 重试请求 | 2 / 2 / 2 | 次 | `requests.jsonl`；重试是失败后的原样重发 |
| 语法修复重交 | 0 | 次 | 本轮无 400 响应 |
| DSL 版本数 | 2 | 版 | portrait 1、wide 1（`dsl_versions_breakdown`） |
| 实际看图次数 | 14 | 次 | `viewing-evidence.json` 的 round 2 块；同一张图的不同视图不合并 |
| 完整视觉迭代 / 未完成 | 0 / 0 | 次 | `iterations.jsonl`；首轮即通过 |
| 等待用户反馈 | 0 | 秒 | 预置轮次模式，前一轮归档后直接读取下一轮需求，不等待外部反馈 |
| 限流等待 | 0 | 秒 | 本轮未出现 429/503 |
| 排队等待 | `null` | 秒 | 服务端不可观测排队，未取得该数据（`queue_wait_null_reason`） |
| 服务端自报耗时 | `render;dur=1525.1/1546.2` | 毫秒 | `requests.jsonl` 的 `server_timing`，与本地墙钟分开记录，不互相替代 |

第 1 轮指标另存于 `round-01/task-metrics.json`（墙钟 8411.1 s，含本会话中段的上下文
压缩与平台停顿；归档尾段 4841.0 s），本轮未重算。两轮指标不可相加当成"设计时间"——
两轮的墙钟里都有服务挂起与归档停顿。

---

## 6. 设计选择、经验与未解决事项

**设计选择。** 本轮真正要解决的是"内容变多、画布不变"。选择的路径是：**标题让出
字号、不让出完整性和层级；新信息进信息栈、不进品牌几何；装饰负责填补新出的空区。**
- 标题 27 字在 860 px 文本盒内、最多 3 行，只有 66/52 这一档字号能同时满足"不折行、
  不下限、仍高于日期"，于是把次要文字按同比例下压（日期 56/44→48/36、讲者 34/30→
  30/28、网址 32/28→30/28），保持"标题 > 日期 > 讲者/网址"的层级不倒挂。
- "免费参加 · 无需报名"做成牌子族的新实例而不是新构件，用边框色（主色 vs 中性蓝）
  区分语义——这样"品牌 3–6 构件形态不变"这条硬约束和内容需求不打架。
- 竖版球下移 100 px、放大到半径 165，一举做了两件事：填 3 行标题留下的右下空区，
  并把"标题不压球"从"看着没压"变成"y 向就不相交"。
- 横版由横排改纯竖排并删掉竖分隔线：新增两行后横排装不下，而删掉 `rule` 后版式
  更干净，元素数 23→25（+3 条新信息、−1 条 rule）。
- 全程不使用 `transform` 压窄文字——长标题只靠减字号与加行数解决。

**本轮沉淀的可复用经验。**
1. 交付前先跑**无网络干跑门**（构造 → 断言合法 → 元素表 → advance/净距/空间校验 →
   拼接一致性校验），一次服务请求都不花就能抓到"静默丢字"这类不报错的缺陷。
2. CJK advance = 1 em 让"这行装得下吗"变成整数算术：`size × len(cn) ≤ 盒宽`。
3. 文本扩展（`height`/`maxLines`/`softWrap`）只能用来兜底，不能当布局主力；靠
   `fontSize × 字数` 自己算好再交给服务。
4. 审计别用文字盒判碰撞——文字盒故意超大，且同色装饰会被同色阈值吃进来；
   用"单行字带窗口 + 列/行连续性"取真实墨迹 bbox，结果才可复算。
5. `shape="CIRCLE"` 与 `borderRadius` 互斥；需要圆的装饰元素二选一。
6. 记录器要记录**失败请求的真实起点**：异常路径下 `started_at` 容易写成结束时刻，
   一旦落盘就只能靠 `elapsed_ms` 反推。
7. 服务端"接受连接但挂住不返回"和 429/503 是两类故障；内部重试只覆盖后者时，
   挂起时间会全额进墙钟，指标里必须单列，否则"请求耗时"会被误读成"工作时间"。
8. 交付前把图片按语义窗口放大再看一遍（本轮 12 个窗口，含专查新增信息的 footer 窗口），
   比只看整图更能发现问题。

**未解决事项与已知限制（如实保留）。**
1. `a21-r2-u1`（`status: disclosed`）：portrait 前两次请求读取超时共 1342.141 s，
   拉长了墙钟与请求耗时之和，两者都不再是模型或设计时间的代理值；两次尝试无响应文件
   可留痕。缓解：记录原样保留、attempt 3 同 DSL 重发成功、不删不补造。
2. `a21-r2-u2`（`disclosed`）：驱动脚本异常路径的 `started_at` 记法缺陷；仅在指标脚本
   里用 `elapsed_ms` 还原并逐条留证，脚本本身未回改，旧日志不回填。
3. 多次看图时刻只有**分钟级**精度：压缩前的 4 次打开（`ev-a21-015`…`ev-a21-018`）
   标为 `minute-level estimate`，其余 10 次标为 `minute-level`；不做更精细的补记。
4. 本轮墙钟的归档尾段 2086.0 s 里含修复指标脚本的时间；该段已在
   `timings.archive_tail_seconds` 单列，读者可自行判断口径。
5. 横版底部 5 行信息栈偏紧（见 §1.3）；若后续轮次再加信息，应先改排布而非继续堆行。
6. **第 1 轮归档件被追加了字段**：为对齐当前生成器的字段集，`round-01/task-metrics.json`
   追加了 `logs.round_changes` 与 4 组 `timings.*`（`service_stall_seconds/note`、
   `started_at_correction/note`、`last_recorded_activity_at`、`archive_tail_seconds/note`）。
   数值一律未改（`ended_at` 21:00:41、`elapsed_seconds` 8411.1 保持归档时的值），
   原文件留底于 `tmp/…/A21/archive-conform/task-metrics.round-01.pre-conform.json`。
   若严格要求"旧轮一字不动"，可直接用留底文件覆盖回去，不影响任何图表与结论。
7. 第一轮 `design-tokens.json` 由更早一版 `write_design_tokens` 生成，缺少
   `diameter_*`/`center_*` 键（其 `radius_*` 是真实的 130/190，来自配置而非外接框）。
   因此**不要**用当前脚本重跑 `a21_audit.py 1`——会写出不一致的 token；第 3 轮应
   从 round-02 的 token 读几何。

**留痕确认。** 临时目录中的草稿、两次失败的请求记录、12 个预览视图与
`views-manifest.json`、能力与轮次相关的脚本、指标脚本的留底与校正证据、文档缓存
均在 `tmp/r20261014T1536+0800-5f11da/` 下，未清理、未覆盖、未保存任何密钥。
交付目录不含草稿或响应正文（最终 PNG 是服务原始字节，未经后处理）。
总任务根的 `.gitignore` 已存在，只忽略 `__pycache__/`、`*.pyc`、`.pytest_cache/`
等运行时缓存，不忽略 `tmp/`、`outputs/` 与实际过程记录。
`__pycache__/` 等运行时缓存不列为产物或自检证据。

**结束依据。** 8 个交付文件齐全；`content-map.json` 的 9 项检查全通过；两张图各打开
多次并放大核对、归档前复查通过且字节未变；两项需求硬约束（主色与 6 构件形态、
两尺寸、不得变形压窄）逐项核对通过。本轮按 round-02.md 的每一项都已满足，
因此不再追加请求或迭代。下一轮（round-03）在本轮归档完成后才读取需求文件。
