# A21 · 叠光 Layerlight · round-01 使用报告

执行模式：**预置三轮连续自动执行**。本题 `TASK.md` / `task.json` 自带 `rounds/round-02.md` 与
`rounds/round-03.md` 两个后续轮文件，全部需求在开工时即可访问。本轮按顺序先完成 round-01，
看图归档后再读 round-02.md、round-03.md 依次执行，**不等待用户消息、不编造未来反馈、
不提前做好第三轮再补造第一轮**。报告注明这是连续执行模式而非隐藏反馈盲测。

---

## 1. 目录与产物

| 类型 | 路径 |
|---|---|
| OUTPUT_DIR | `outputs/run-20261002-220723-mimo/A21/` |
| TEMP_DIR | `tmp/run-20261002-220723-mimo/A21/` |
| 本轮输出 | `outputs/run-20261002-220723-mimo/A21/round-01/` |

round-01 交付 8 个文件：

| 文件 | 尺寸 / 说明 | 字节 |
|---|---|---|
| `launch-portrait.png` | 1080×1350，服务原始响应字节 | 76587 |
| `launch-portrait.snapshot` | 同名完整 DSL | 2447 |
| `launch-wide.png` | 1440×810，服务原始响应字节 | 67808 |
| `launch-wide.snapshot` | 同名完整 DSL | 2492 |
| `design-tokens.json` | 主色 / 主题 / 字阶 / 品牌图形 / 版式与留白 | — |
| `content-map.json` | 必含文案逐条 → 轮次 → 图 → 位置 | — |
| `snapshot-usage.md` | 本报告 | — |
| `task-metrics.json` | 本轮指标 | — |

两张 PNG 的 SHA-256 分别为 `A41B1C2954A9C88D…` 与 `BEAEFEB2D03C3AA0…`，与临时目录里的
服务响应文件逐字节相同（归档脚本逐一比对），**未做任何后处理**。尺寸不读报告值，而是直接
解析 PNG 的 IHDR 校验为 1080×1350 / 1440×810。

---

## 2. 真实文档与服务应用

| 请求 | 用途 | 结果 |
|---|---|---|
| `GET https://open-snapshot.muedsa.com/ai-guide.md` | 本题 AGENTS 明确要求开工先读服务指南 | 200，3718 B，846.4 ms，落盘 `tmp/.../A21/doc-ai-guide.md` |

开工时还通过取文工具读过一次同一 URL 的全文；执行环境未暴露该次工具调用的起止时刻，
因此 `requests.jsonl` 的 `A21-doc-001` 记录的是随后为落盘而发起的带计时 GET，A21 的文档
请求合计 2 次（同一 URL，1 次计时完整、1 次时刻不可得记 `null`），不谎称只读过一次，也不把
不可得字段填成猜测值。

以下资源按总约定**复用已真实取得的结果，未重复发新请求**：

* DSL 逐标签属性表 —— `tmp/.../A17/tag-attrs.md`（Container / Text / Positioned / Stack /
  SizedBox / Row / Column / Padding / Align / Center … 每个标签的属性、类型、默认值）
* DSL 指南摘录 —— `tmp/.../A17/doc-excerpts.md`（颜色、常用标签、透明度与颜色滤镜、
  Transform、文本中的特殊字符、布局自省等 20 余节）
* 字体清单 —— `tmp/.../A11/fonts-0001.txt`（`GET /fonts`，27 个族）

从指南与摘录里直接用到的确定事实：

* 请求体是 **UTF-8 纯文本**、`Content-Type: text/plain; charset=utf-8`，**不是 JSON**；成功响应
  是图片二进制，错误是带 `code / message / requestId` 的 JSON。
* 颜色支持 `#RGB` / `#RGBA` / `#RRGGBB` / `#RRGGBBAA` —— **8 位按 CSS 的 `#RRGGBBAA`
  解析，透明度在最后两位**（旧版按 `#AARRGGBB` 的写法会变色，本轮一律用新序）。
* `<Text>` 支持 `fontSize` / `fontFamily`（**多个字体用英文逗号分隔**）/ `fontStyle="BOLD"` /
  `textAlign` / `letterSpacing` / `maxLines` / `overflow` / `softWrap`。
* 文本**不解析 HTML 实体**，只把 `<` `>` 当标记，`<` `>` 需要 CDATA；前导尾随空白被裁掉。
  本轮文案不含 `<` `>` `&`，但仍统一走 XML 转义函数。
* 默认管理器注册 38 个标签，`Row` `Column` `Stack` `Positioned` `Padding` `Align` `Center`
  `SizedBox` 等均可用；`Container` 有 `width/height/color/border/borderRadius/shape/transform/clipBehavior`。
* `GET /fonts` 每行一个族，**不是 JSON**；可用 `Noto Sans CJK SC`、`Inter`、`Inter Semi Bold`
  等 —— 本轮中文用 `Noto Sans CJK SC`，纯拉丁字符串用 `Inter,Noto Sans CJK SC` 作回退链。

**没有臆造任何标签、属性、字体或服务返回值。**

---

## 3. 需求满足情况

| 要求 | 竖版 1080×1350 | 横版 1440×810 |
|---|---|---|
| 「让复杂信息变得清晰」 | 主标题，fs **88** ≥56 | 主标题，fs **72** ≥56 |
| 「2026.11.07 19:30」 | 正文区 fs42 | 信息面板 fs36 |
| 「ONLINE LAUNCH」 | 左上主色胶囊 fs28 | 左上主色胶囊 fs26 |
| 「讲者：林川 / 苏言」 | 正文区 fs34 | 信息面板 fs30 |
| 「layerlight.example.org」 | 底部 fs30 | 信息面板 fs28 |
| 其余文字 ≥24 | 最小 30（副标题） ✅ | 最小 26（胶囊） ✅ |
| 两图同一主色 | `#5B4FE8` ✅ | `#5B4FE8` ✅ |
| 同一字体层级 | title > deck/date > body > meta ✅ | 同一套层级 ✅ |
| 3–6 构件品牌图形 | 叠光标记 **4 构件** ✅ | 同一标记 scale 0.8 ✅ |
| 分别构图 | 单列纵向堆叠 | 左右双栏 + 信息面板 |
| 不整图嵌入 / 不外部图片 | DSL 里 **0 个 `<Image>`**，断言通过 ✅ | 同 ✅ |
| 顶/底真实扩展空间且不写待添加文字 | 上 `0..140`、下 `1156..1350`，逐点扫描 `non_background = 0` ✅ | 上 `0..110`、下 `670..810`，同样为空 ✅ |

生成器把「顶部/底部留白不许出现任何元素」写成了硬断言：逐块检查 `y ≥ top` 且 `y+h ≤ bottom`，
任一元素越界即抛错并打印是哪一块；随后 `probe-a21.ps1` 再用 **GDI+ 逐像素扫描**这四条条带，
确认里面连一个非背景像素都没有。**不是口头声称留白，而是两道独立校验。**

---

## 4. 设计选择

### 4.1 主色与主题（`design-tokens.json`）

* 主色 `#5B4FE8`（叠光靛蓝），配 `#8B85FF`（浅靛）与 `#FFB020`（琥珀光）—— 三轮**完全不变**，
  因为 round-02 明确要求主色不变。
* round-01/02 深色主题：页面 `#0E1026`、面板 `#171A3C`、正文 `#F4F6FF` / `#C2C7EE`、强调 `#8B85FF`。
* round-03 才切浅色主题（页面 `#F4F5FB`、面板 `#FFFFFF`、正文 `#14173A` / `#474B77` / `#3730A3`），
  并新增两条带 alpha 的背景光带 —— 那时才需要按合成色算对比度。

### 4.2 字阶

`title (88/72 → round-02 起 56/52)` > `date (42/36)` > `deck (30/28)` > `body (34/30)` >
`meta (26–28)`。行高统一 `fontSize × 1.46`（服务实测的行高比）。两版用同一套相对层级。

### 4.3 品牌图形「叠光标记」—— 4 构件

| 构件 | 形状 | 颜色 | 局部偏移 |
|---|---|---|---|
| C1 layer | 88×88 圆角方 r24 | `#5B4FE8` | (0, 44) |
| C2 plane | 88×88 圆角方 r24 | `#8B85FF` | (44, 22) |
| C3 beam | 88×88 圆角方 r24 | `#FFB020` | (88, 0) |
| C4 core | ⌀30 圆（`borderRadius = d/2`） | `#FFB020` | (51, 62) |

三个圆角方沿对角线阶梯叠压、均以 `#RRGGBBAA` 半透明绘制，重叠处产生更亮的一层 ——
正是「叠光」的读法；琥珀核心圆落在 C1∩C2 的双层叠加区里。**竖版 scale=1.0（176×132）、
横版 scale=0.8（140.8×105.6），相对几何、颜色与叠压顺序逐项一致**，只整体缩放与改位置
（round-02 允许移动缩放装饰、但形态不变）。两个标记各放大 3× 实看过，确认是同一套构件。

### 4.4 两版分别构图

* **竖版**：单列纵向。标记+字标在左上 → 主张胶囊 → 主标题（fs88 单行）→ 副标题 → 分隔线 →
  日期 / 讲者 → 网址，左对齐 x=88、内容宽 904，底部留 194 px 扩展带。
* **横版**：左右双栏。左栏（x=96 宽 760）放标记、字标、胶囊、主张与副标题；右栏是一个
  圆角信息面板（x=904 宽 440、内边距 36），日期 / 讲者 / 网址在面板里纵向均分。两栏各自成形，
  **不是把竖版压扁**。

---

## 5. 逐图自检（真实看图）

| # | 看的是什么 | 结论 |
|---|---|---|
| 1 | `launch-portrait-r01.png` 整图 1080×1350 | 4 构件标记、字标、`ONLINE LAUNCH` 胶囊、fs88 主标题单行不裁切、副标题、分隔线、日期、讲者、网址全部到位；顶/底留白确为空 |
| 2 | `launch-wide-r01.png` 整图 1440×810 | 双栏构图成立，右侧面板三行信息排布均匀，左栏主张清晰，与竖版明显是两种构图 |
| 3 | `v1-mark-portrait-01.png` 竖版标记 3× 放大 | 靛蓝 / 淡紫 / 琥珀三个圆角方沿对角叠压，琥珀核心圆落在双层叠加区，重叠处亮度叠加可见，4 构件可辨 |
| 4 | `v1-mark-wide-01.png` 横版标记 3× 放大 | 与竖版同一套 4 构件、同一叠压顺序与颜色，仅整体缩小；「叠光」读法一致 |

像素级复核（`probe-a21.ps1`，GDI+ `GetPixel`）：

| 图 | probe 命中声明背景 | 保留带空 | 最低对比度 |
|---|---|---|---|
| 竖版 | **7 / 7** | 上 ✅ 下 ✅（`non_background = 0`） | 5.63:1 |
| 横版 | **7 / 7** | 上 ✅ 下 ✅（`non_background = 0`） | 5.52:1 |

probe 是每个文本框左缘外 6 px（胶囊内则落在胶囊左缘内 6 px）的一个点，落在与文字同层的
实际上，因此能证明「声明的背景叠层和真正画出来的一致」。round-01 虽无对比度硬要求，
仍把 14 处正文的实测值全部记了下来，作为 round-03 换成 `contrast` 模式前的基线。

---

## 6. 实际问题、修复与验证

| # | 问题 | 修复 | 验证 |
|---|---|---|---|
| 1 | `gen-a21.ps1` 首次运行在**全部产物写盘之后**的汇总打印阶段抛 `Method invocation failed because [System.IO.File] does not contain a method named 'GetLength'` —— 静态成员应写 `[IO.File]::GetLength(...)`，而 `.Length` 是实例属性 | 改为 `(Get-Item (...)).Length`，只改打印语句 | 第二次运行 0 problems；两次产出的 `.snapshot` 逐字节相同（生成器确定性、DSL 不含时间戳），**未影响任何 DSL 或渲染**。记为 `A21r1-it02`（syntax-fix），并注明它按时间在 baseline 之前、为保持 `iterations.jsonl` 严格追加故只在末尾补记 |

| 2 | 归档脚本 `close-a21-round01.ps1` 连续两次解析失败：先是 `Unexpected token`，最小复现证明根因是 **PowerShell 把 U+201C/U+201D（`“ ”`）也当作字符串定界符** —— `$a = "plain 中文 “curly” end"` 这样一个普通双引号字符串会在 `“` 处被切断，而单引号字符串里的同样字符不受影响（`gen-a21.ps1`、`promote-a21-r01.ps1` 里的 `“ ”` 都在单引号内，所以一直正常）；改掉引号后又报 `Missing closing '}'` | 引号换成 `「」` 并把该行改成单引号 + `-f` 传 `$base`；再用 `[System.Management.Automation.Language.Parser]::ParseFile` 一次取回全部错误、数原始大括号得 28 开 / 27 闭，补上 `IhdrOf` 函数缺失的 `}` | `ParseFile` 复查 **parse errors = 0**，脚本一次跑通，写入 events seq 41 与 checkpoint `state-000022.json`（291309 字节）。两个缺陷都在任何 DSL 生成与渲染之前，**未影响 round-01 的交付内容**。记为 `A21r1-it03`（syntax-fix，2 项改动、0 图 0 渲染） |

本轮**没有发现视觉缺陷**：两图首版看图即满足全部要求，probe 与保留带扫描 0 problems。
按总约定「一次合格时无需制造修改」，**不为凑迭代次数而改版**，完整视觉迭代记 0 次。
三行 syntax-fix 全部是脚本级缺陷（`File::GetLength` 方法名写错、`“ ”` 被当字符串定界符、
`IhdrOf` 少一个右大括号），都不产生 DSL 版本、不产生图，单独计数。

---

## 7. 请求与迭代统计

* **渲染请求 2 次**：`A21r1-p01`（200，2178.6 ms，76587 B，`render;dur=452.8, total;dur=455.1`，
  限流余量 119）、`A21r1-w01`（200，1970 ms，67808 B，`render;dur=184.5, total;dur=186.6`，
  限流余量 118）。**失败 0、重试 0、429/5xx 0。**
* **文档请求 2 次**（同一 URL `/ai-guide.md`）：1 次带计时 846.4 ms / 3718 B / 200，另 1 次时刻不可得记 `null`。
* **看图 4 次**：两图整图各 1 次 + 两个标记放大各 1 次。
* **迭代 3 行**：`A21r1-it01` baseline（1 行带图）、`A21r1-it02` 与 `A21r1-it03` syntax-fix（各 0 图）。完整视觉迭代 **0**。
* token / 图像输入 / 费用：平台未提供本任务任何计量指标，记 `null` 并注明原因。

---

## 8. 未解决事项

* 本轮无未解决的视觉或需求问题。
* `requests.jsonl` 中 `A21-doc-001` 的 `started_utc/ended_utc/bytes` 之外，另有一次开工时的工具读取
  时刻不可得，已在该行 `note` 里如实说明，不用其他量估造。
* 看图的精确时钟未被采集，`iterations.jsonl` 用 `viewed_at_basis` 记录可证明的时间窗
  （渲染完成 → 本轮归档时刻），不编造单次看图时刻。
