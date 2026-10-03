# A21 · snapshot-usage.md（任务级累计报告，三轮）

- run_id：`20261003-114508-flashmax` · 任务 A21「真实需求变更：双尺寸发布物」
- 输出目录：`outputs/20261003-114508-flashmax/A21/`（含 `round-01/`、`round-02/`、`round-03/`）
- 临时目录：`tmp/20261003-114508-flashmax/A21/`
- 完成状态：**completed** —— 6 张最终 PNG 全部为服务真实 200 响应，且逐张用 `read_image` 打开核对
- 执行模式：**预置连续执行（preloaded_sequential）**。`rounds/round-02.md`、`rounds/round-03.md` 自始可读；
  实际执行顺序是先完成并归档 round-01（保存 DSL/PNG/报告/指标）后，才读取 round-02.md 并在第一轮作品上修改，
  再读取 round-03.md 完成第三轮。**不是隐藏反馈盲测**，报告中如实注明这一模式。

## 1. 最终产物与需求完成情况

| 文件 | 尺寸 | 对应 DSL | 完成状态 |
|---|---|---|---|
| `round-01/launch-portrait.png` | 1080×1350 | `round-01/launch-portrait.snapshot` | 200，已查看 |
| `round-01/launch-wide.png` | 1440×810 | `round-01/launch-wide.snapshot` | 200，已查看 |
| `round-02/launch-portrait.png` | 1080×1350 | `round-02/launch-portrait.snapshot` | 200，已查看 |
| `round-02/launch-wide.png` | 1440×810 | `round-02/launch-wide.snapshot` | 200，已查看 |
| `round-03/launch-portrait.png` | 1080×1350 | `round-03/launch-portrait.snapshot` | 200，已查看 |
| `round-03/launch-wide.png` | 1440×810 | `round-03/launch-wide.snapshot` | 200，已查看 |

每轮另有 `design-tokens.json`、`content-map.json`；第三轮另有 `contrast-audit.json`；本层为三轮累计报告与指标。

### 第一轮要求逐项

| 要求 | 实现 | 依据 |
|---|---|---|
| 1080×1350 竖版 + 1440×810 横版 | 实测 PNG 尺寸一致 | Pillow + 看图 |
| 必含「让复杂信息变得清晰」 | 竖版 64px、横版 72px 主标题，一行不换行不压缩 | 看图 |
| 必含「2026.11.07 19:30」 | 竖版 36px、横版板块内 30px，全部六图都在 | 看图 |
| 必含「ONLINE LAUNCH」 | 竖版 28px / 横版 28px 眉题，带字距 | 看图 |
| 必含「讲者：林川 / 苏言」 | 竖版 40px / 横版 40px | 看图 |
| 必含「layerlight.example.org」 | 竖版 36px / 横版 40px | 看图 |
| 两图同一主色 | 深色主色 `#0B1220` + 强调 `#0E9F8F`，两图共用同一 token 表 | `design-tokens.json` |
| 同一字体层级 | 竖/横各自一套 title/display/lead/body/meta，比例一致 | `design-tokens.json` |
| 3–6 构件品牌图形且可识别 | **5 构件**：圆角容器 + 三条光条（高度比 0.46/0.62/0.34）+ 基座横杆；两图同形同比例，仅尺寸不同 | `content-map.json > brand_mark` |
| 分别构图 | 竖版上下分区居中轴；横版左文右品牌面板，构图不同 | 看图 |
| 主标题 ≥56、其余 ≥24 | 竖版主标题 64、正文最小 26；横版主标题 72、正文最小 28 | DSL 属性 + 生成脚本断言 |
| 不用整图嵌入或外部图片 | DSL 中没有任何 `<Image>`；全部由 Container/Text 构造 | `grep` 全轮 DSL |
| 顶部/底部留真实可用扩展空间 | 竖版 0–110 / 1238–1350；横版 0–100 / 780–810，均无文字 | `content-map.json > expansion_bands` |
| 不写「待添加」文字 | 装饰文案只陈述发布事实与尺度原则，没有占位语 | `content-map.json` |

### 第二轮要求逐项

| 要求 | 实现 | 依据 |
|---|---|---|
| 标题替换为指定长标题 | 全文「当所有信息都想成为标题：让复杂信息变得清晰的结构化方法」未经改写 | 看图 + `content-map.json` |
| 标题最多 3 行、字号 ≥48 | 竖版 60px 共 3 行；横版 60px 共 2 行 | 看图 + 生成脚本输出 |
| 新增赞助方「Northstar Research / 云构工具」 | 竖版 36px / 横版 34px，单行不折行 | 看图 |
| 新增「免费参加 · 无需报名」 | 竖/横均为 chip 形式，文字完整 | 看图 |
| 日期时间/讲者/ONLINE LAUNCH/网址保留 | 四项全部在位 | 看图 |
| 主色与品牌 3–6 构件形态不变 | 主色 token 未变；品牌图形构件数、比例、几何完全未变 | `design-tokens.json`、`content-map.json` |
| 允许移动缩放装饰 | 装饰光晕与强调条位置随排版调整 | DSL diff |
| 两尺寸不变 | 仍为 1080×1350 / 1440×810 | Pillow + 看图 |
| 不能用变形压窄文字 | 未使用任何 scale 变形；长标题靠**自动选字号 + 自然换行**解决（竖版 60px，横版 60px） | 生成脚本 `_wrap_lines` |
| 说明如何避免长标题与新增信息碰撞 | 见第 4 节「长标题避碰策略」 | 本报告 |

### 第三轮要求逐项

| 要求 | 实现 | 依据 |
|---|---|---|
| 改浅色主题 | 页面 `#EEF3F8` + 纯白卡片 `#FFFFFF`；深色主题的整体结构不变 | 看图 |
| 所有普通文字与**实际合成背景**对比度 ≥4.5:1 | 竖版 11 对、横版 10 对全部通过，最低 5.47:1 | `round-03/contrast-audit.json` |
| 保留全部第二轮文案 | 长标题、讲者、赞助方、免费参加、日期、网址全部保留 | 看图 |
| 保留品牌图形 | 同一 5 构件图形，仅改配色（浅色底上改为深青系列） | 看图 |
| 在网址**上方**新增英文短句 | 「Clarity through structure」位于网址正上方（竖版 936 与 1000；横版 600 与 660） | 看图 + `content-map.json` |
| 英文新增句 ≥24 | 竖版 28px、横版 30px | DSL 属性 |
| 中文长标题仍 ≤3 行、≥48 | 竖版 60px 2 行；横版 60px 2 行 | 看图 |
| 两尺寸不变 | 1080×1350 / 1440×810 | Pillow |
| 不得让赞助方消失 | 两图赞助方都在，且不再折行 | 看图 |
| 不能只改两种颜色忽略实际叠层 | 每处文字都按其**真实所在区域**的合成背景计算：页面 → 半透明光晕 → 白色卡片；chip/badge 文字按自身填充色再合成 | `contrast-audit.json > method` |
| 每图附 ≥6 处正文对比度 | 竖版 9 处正文 + 2 处 chip，横版 8 处正文 + 2 处 chip | `contrast-audit.json` |
| 说明视觉回归 | 见第 4 节 | 本报告 |

## 2. 实际读过的文档与用到的能力

| 实际阅读的文档/接口 | 本次使用的知识 | 对应位置 |
|---|---|---|
| `https://open-snapshot.muedsa.com/ai-guide.md`（HTTP 200） | 请求体是 UTF-8 纯文本 DSL、成功返回图片二进制、失败返回 JSON、`/fonts` 与 `/snapshot` 共用配额、不要用 `?errorImage=png` | 渲染脚本 `renderer.py` |
| `https://open-snapshot.muedsa.com/openapi.yaml`（HTTP 200，已存 `tmp/.../A23/openapi.yaml`） | `type` 只支持 `png/jpg/webp`；`X-Request-Id`、`Server-Timing`、`X-Snapshot-Cache` 等响应头；错误码枚举 | 请求日志字段 |
| `GET /fonts`（复用 A01 已取得的 `_suite/shared/fonts.txt`） | 字体族清单，仅使用 `Noto Sans CJK SC` | 全部 Text |
| 父代理实测探针（`cdata-probe.png`、`entity-center-probe.png`，均 200 OK） | ① 文本节点里 `&` 与 `>` **原样输出**，裸 `<` 会 400 TAG_OPEN，需 `<![CDATA[…]]>`；实体**不解码**（`&amp;` 会画成 5 个字面字符）。② 单文档元素上限 **4096**，超出返回 400 RENDER_ERROR。③ **校准字宽**：`Noto Sans Mono CJK SC` = 0.5000 em/字符；`Noto Sans CJK SC` 汉字 0.9952、大写 0.6106、小写 0.5769、数字 0.5385、空格 0.5641、句点 0.2692。④ `border` 必须写 `"宽 样式 颜色"` 三值；10 位颜色被拒。 | `snapkit.esc()` 自动 CDATA、`text_width()` 校准字宽表、`element_count()` 元素守卫 |

用到的 DSL 能力：`Snapshot background`、`Container`（width/height/color/borderRadius/四角圆角/border/boxShadow）、
`Stack alignment="TOP_LEFT" fit="EXPAND"`、`Positioned`、`Text`（fontSize/fontFamily/fontStyle/letterSpacing/color）、
`Container alignment` 做右对齐。**未使用** Image/Emoji/Transform/Filter/Clip，全部主体为纯 DSL 几何与文字。

## 3. 请求、迭代与看图

- 请求日志：`tmp/20261003-114508-flashmax/A21/requests.jsonl`
- 迭代日志：`tmp/20261003-114508-flashmax/A21/iterations.jsonl`
- 看图日志：`tmp/20261003-114508-flashmax/A21/image-views.jsonl`
- 渲染请求 67 次（`A21-REQ-0001`–`A21-REQ-0067`）：成功 65、失败 2（均为 `A21-REQ-0001/0002`，
  urllib 原生客户端被 Cloudflare 以 403 error 1010 拒绝，改用 curl 兼容 UA 后全部成功）；无 429。
- 版本留痕的诚实说明：沙箱用 `renderer.py` 逐次覆盖轮次输出文件并只在渲染当下记录哈希，
  67 次请求中能在磁盘上重新哈希区分的 DSL 内容为 **7 个**（另有 1 支 border 探针）；
  生成脚本实际迭代 4 代（v1 手工排版 → v4 锚定卡片底边 + 自动选字号），早期几代因共用文件名被覆盖，
  已无法再用哈希区分，如实说明而**不臆造版本数**。每轮最终 DSL 另行存档为
  `launch-*.r{1,2,3}.v1.snapshot`，全程未被覆盖。
- 实际看图：**27 次**（每条记录含轮次、图片与当时观察到的问题，见 `image-views.jsonl`）。
- 迭代记录 50 条：其中 `visual` 11 条（完整视觉迭代 11 次，均为「看图 → 改 DSL → 重渲染 → 再看并比较」），
  其余为 `baseline`、`requirement-change`（round-02/round-03 两轮需求变更）与探针渲染。

## 4. 修改记录与踩坑（关键视觉问题）

| 问题 | 现象 | 原因（确认依据） | 修改与验证 |
|---|---|---|---|
| **品牌图形被卡片盖住** | 第三轮浅色主题里品牌只剩一个空方框，三条光条不见了 | `draw_mark` 先画光条、后画方框；深色主题方框填充是 `#00000000` 所以看不出问题，浅色主题方框填充改为 `#F0FDFAFF` 不透明，把光条整片盖住（DSL 顺序可直接读出） | 改为**先画容器框、再画基座与光条**；重渲染后光条恢复 |
| **品牌图形被面板盖住** | 横版两轮里右侧白色/深色面板完全看不到品牌图形 | 面板 `Container` 在 `draw_mark` 之后绘制，不透明填充盖住标记（同样是绘制顺序问题，A08 踩过的同一个坑） | 改为**先画面板底、再画品牌图形**；重渲染后正常 |
| **年份/标签压字** | 竖版第一版眉题与品牌图形叠在一起 | 文案列在竖版里与品牌共用同一列，起始 y 取的是卡片内边距而非品牌下沿 | 竖版文案起点改为 `max(卡片内边距, 品牌下沿 + 34)`；并加 `_gaps()` 文本包围盒互斥检查 |
| **长标题与新增信息碰撞** | 第二轮首版竖版标题挤出第三行末尾、与摘要行重叠 | 手工估算行高与间距在多轮修改后失配 | 引入 `_wrap_lines()` 自然换行 + 自动降字号（上限 3 行）+ 全部文本包围盒互斥断言；生成脚本直接报错而不是静默压字 |
| **chip 宽度取整不够** | 生成脚本抛 `cta: 270.2px > 270.0px` | `round()` 把 270.2 取成 270 作为可用宽度 | 改用 `math.ceil()`，并把全角间隔号按 1.08 倍字宽计量（实测该字形确实更宽） |
| **赞助方被拆成两行** | 横版出现 `Northstar Re` / `search / 云构工具` | 该块换行阈值仍是早期调试值 400px，而整行实测 528.7px | 阈值提到 760px，单行完整显示 |
| **日期徽标对比度不足** | 第三轮橙色徽标上的白字只有 3.19:1 | `contrast()` 实测 `#FFFFFF` on `#D97706` = 3.19 | 徽标底色改为 `#92400E`，白字升到 7.09:1；横版日期改为面板内同款深色徽标 |
| **面板日期与左列撞行** | 竖版/横版日期文字与网址水平相接 | 面板文字被误记入左列文本盒做互斥检查 | 面板文字改用面板自身坐标测量并从互斥检查中排除，同时把面板日期下移到面板底部 |
| **装饰条压住 CTA chip** | 横版底部三个色条与 chip 视觉相接 | 装饰条按画布底边定位 | 横版去掉重复装饰条（品牌图形已在面板内），竖版装饰条锚定 chip 行下方 |

**长标题避碰策略（第二轮要求说明）**：长标题不靠 scale 压窄，而是（1）先按列宽做**自然换行**，
（2）在 3 行预算内**自动选字号**（竖版 60px、横版 60px），（3）标题之后的所有块由同一游标顺序下推，
（4）生成阶段用文本包围盒互斥断言拦住任何重叠。新增的赞助方与 chip 因此被推到标题下方独立带，
不侵入标题行；底部 CTA 行则锚定卡片底边，与正文列之间留 40px 以上间隔，脚本超限直接报错。

**视觉回归说明（第三轮要求）**：第三轮只改变「主题」与「新增英文句」，几何骨架完全沿用第二轮：
卡片矩形、品牌图形几何比例、文字块顺序与字号阶梯（title/display/lead/body/meta）一致；
新增英文句插在网址上方，靠把底部 CTA 行下移到卡片底边腾出空间，没有改动任何第二轮文案的位置语义。
两轮的 `design-tokens.json` 可直接 diff 出「变了什么、没变什么」。

## 5. 未解决事项

- 竖版第一轮卡片高度 1154 而第一轮正文列只到 y≈666，标题与底部 CTA 之间留白偏大（属设计选择，
  不是缺陷）；第二、三轮因新增文案把该区域填满，三图纵向节奏因此不完全一致，已如实记录。
- 横版第三轮日期放在右侧面板内的深色徽标里，与竖版「CTA 行右侧徽标」位置不同；两版式尺寸差异较大，
  未强行统一，`contrast-audit.json` 与 `content-map.json` 都标明了各自位置。
- 浅色主题的装饰光晕色 `#0E9F8F1F` 只覆盖卡片之外的页面区域，卡片内部叠层为纯白；
  审计按真实叠层计算，未把光晕算进文字背景（如需更强的层次感需要另行设计卡片内叠层）。

## 6. 真实消耗

| 指标 | 实际值 | 来源 |
|---|---|---|
| 渲染请求 / 成功 / 失败 | 67 / 65 / 2 | `requests.jsonl` |
| 重试请求 | 2（403 后换客户端重试，是总数子集） | `requests.jsonl` |
| 其他服务请求 | 0（文档与字体为复用，未新增 HTTP） | `requests.jsonl` |
| DSL 版本 | 磁盘可区分的 DSL 内容 7 个 + 1 支探针；生成脚本 4 代（早期被覆盖，见上） | 重新哈希 + 临时目录 |
| 看图次数 / 完整视觉迭代 | 27 / 11 | `image-views.jsonl`、`iterations.jsonl` |
| 限流等待 | 未发生（无 429），排队等待不可测记 `null` | 请求头 |
| token / 图像输入 / 费用 | `null`（平台未提供） | 见 `task-metrics.json` |

每轮明细见 `round-01/task-metrics.json`、`round-02/task-metrics.json`、`round-03/task-metrics.json`；
本层 `task-metrics.json` 为三轮累计（不重复累加轮内明细）。
