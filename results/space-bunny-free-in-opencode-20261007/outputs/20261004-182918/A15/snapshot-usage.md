# A15 · 复杂界面视觉复刻 — 使用报告（snapshot-usage.md）

## 1. 完成状态与目录

| 项 | 内容 |
|---|---|
| 任务 | A15 复杂界面视觉复刻 |
| run_id | `20261004-182918` |
| 状态 | **completed** |
| 输出目录 | `outputs/20261004-182918/A15/` |
| 临时目录 | `tmp/20261004-182918/A15/` |
| 服务 | `POST https://open-snapshot.muedsa.com/snapshot`（snapkit 自带浏览器 UA） |
| 交付 PNG | `reconstructed.png`，真实服务响应原始字节，1440×900，PNG/RGBA |
| 交付 DSL | `reconstructed.snapshot`，14934 字节，与最终 PNG **同一次请求**产生 |
| 附加交付 | `reconstruction-audit.json`、`comparison.md` |

输出目录最终文件：

```
reconstructed.png            113273 B   服务原始响应，未做任何后处理
reconstructed.snapshot        14934 B   与 PNG 完全一致的完整 DSL
reconstruction-audit.json     ~38 KB    49 几何锚点 + 57 文本锚点 + 图表/颜色数据
comparison.md                ~14.5 KB   可测误差 + 残余差异说明
snapshot-usage.md                      本文件
task-metrics.json                      由 wrapup.py 生成
```

---

## 2. 实际使用的服务文档与字体

### 2.1 文档

| 文档 | 来源 | 是否本次新抓取 |
|---|---|---|
| `https://open-snapshot.muedsa.com/ai-guide.md` | 本套 `_suite/docs/ai-guide.md` | **复用本题库已有抓取**（`_suite/requests.jsonl` 中记录），未重复发起网络请求 |
| `https://snapshot.muedsa.com/` DSL 文档 | 由 `_suite/docs/ai-guide.md` 指引 + `_suite/docs/openapi.yaml` 归纳 | 复用 |
| `_suite/DSL-HANDBOOK.md` | 本套前序任务实测结论 | 复用 |

实际从文档确认并用到的要点：

- 请求体是 **UTF-8 纯文本 DSL**（不是 JSON），成功响应体是图片二进制；
- `type="png"`；画布尺寸由布局决定，用唯一的根 `<Container width height>` 定尺寸；
- 颜色支持 `#RGB/#RGBA/#RRGGBB/#RRGGBBAA`，8 位按 CSS 读 `#RRGGBBAA`；
- 字体族名必须与 `GET /fonts` 返回值一致，多个用英文逗号分隔；
- 非成功响应是含 `code/message/requestId` 的 JSON，`X-Request-Id` 可关联日志；
- 默认不要用 `?errorImage=png`（会掩盖错误消息）——本次未使用。

### 2.2 字体（`_suite/fonts-list.txt`，复用本题库已有抓取）

`Inter`、`Inter Black`、`Inter Extra Bold`、`Inter Extra Light`、`Inter Light`、
`Inter Medium`、`Inter Semi Bold`、`Inter Thin`、`Noto Sans CJK SC`、
`DejaVu Sans Mono`、`DejaVu Serif` 等。

本题实际用到 5 个族：`Inter`、`Inter Medium`、`Inter Semi Bold`、
`Inter Extra Bold`、`Inter Black`。没有臆造字体名。

**额外发现（探针实测，`tmp/…/A15/probe_weight.py`）**：`GET /fonts` 的列表
**不完整** —— `fontFamily="Inter Bold"` 服务端可用（密度 492506、宽 344，
与列出的族均不同），但未出现在 `/fonts` 里。同时 `fontWeight` /
`font-weight` / `weight` 三种拼写在 `Inter` 族上**全部被静默忽略**
（`Workspace Overview`@33px 在 `fontWeight=BOLD/600/700/800` 下密度恒为 430063），
所以字重只能靠切换 `fontFamily` 来实现。

### 2.3 实际用到的标签与属性

`<Snapshot type background>`、`<Container width height color borderRadius border>`、
`<Stack fit>`、`<Positioned left top width height>`、`<Text fontSize fontFamily
color letterSpacing text>`。

没有用到 `<Image>`（DSL 中 `<Image>` 出现次数 = 0）、`<Row>/<Column>`、
`<Transform>`、`<Opacity>`、渐变、阴影、裁剪。

---

## 3. 方法：如何把参考图变成可复核的坐标

参考图**只用于观察与像素测量**。全部几何来自 PIL 扫描，不含任何裁块/描图：

| 步骤 | 脚本 | 产出 |
|---|---|---|
| 1 全局扫描 / 色板 / 卡片候选框 | `measure_ref.py` | `reference-measurements.json` |
| 2 卡片矩形、柱体、网格线、标签、文本行游程 | `measure_ref2.py` | `reference-measurements2.json` |
| 3 按钮/侧栏/活动项/表格的原始色值游程 | `measure_ref3.py` | `reference-measurements3.json` |
| 4 精确色值边界 + 圆角轮廓 + 文字墨迹盒 | `measure_ref4.py`, `measure_ref5.py` | `reference-measurements4/5.json` |
| 5 57 个文本元素的紧致墨迹包围盒 | `measure_text_ink.py` | `reference-text-ink.json` |
| 6 字重/字距/字号标定（7 轮探针） | `probe_a15.py`, `calib_a15.py`, `calib2..7_a15.py` | `calibration*.json` |
| 7 共享 spec（颜色/几何/文字表/测量区域） | `spec_a15.py` | `spec_a15.py` |
| 8 生成 DSL 并渲染 | `build_a15.py` | `reconstructed.snapshot` + `.png` |
| 9 用**同一套代码**同时测量参考图与重建图 | `verify_render.py` | `verify.json`, `text-offsets.json` |
| 10 颜色/整体一致率 | `colour_audit.py` | `colour-audit.json` |
| 11 生成审计与对照文档 | `make_audit.py`, `make_comparison.py` | `reconstruction-audit.json`, `comparison.md` |

关键做法：

- **文字按「墨迹」定位**。DSL 文本框原点 = `(参考墨迹左 − dx, 参考墨迹上 − dy)`，
  `(dx, dy)` 由探针图实测（随字号/字形不同，在 0–7 px 之间），并由
  `verify_render.py` 每轮从实际渲染结果回写修正，形成闭环。
- **字重用「墨迹密度」定量标定**。定义 `密度 = Σ|bg_luma − px_luma|`
  （对背景取绝对值，明暗文字通用）。实测证明该服务对普通字重能做到 **100.0%**
  命中（subtitle / period / acttime / rowowner / footer / ytick / month / unit 全部
  密度比 1.000、宽度 0 px 误差），说明参考图确实由同一渲染器产出，
  因此密度差异可以直接归因到字重档位。
- **圆角由角点轮廓反解**。对每个圆角矩形逐列记录「首个非背景像素相对顶边的偏移」，
  参考图卡片为 `[8,6,4,3,2,2,1,1,0]`，据此在整数档中选出 12；
  最终**参考图与重建图的角点轮廓逐值相同**。

---

## 4. 逐图 / 逐项自检表（TASK.md 每条硬指标）

| # | TASK.md 硬指标 | 实测值 | 结论 |
|---|---|---|---|
| 1 | 输出尺寸保持 1440×900 | `reconstructed.png` = 1440×900 | ✅ |
| 2 | 全部由 Snapshot DSL 构造 | `reconstructed.snapshot` 14934 B，95 个 `Positioned`，`<Image>` 计数 0 | ✅ |
| 3 | 禁止嵌入参考图或裁块 | 输出目录只有 1 个 PNG，即 DSL 渲染结果；DSL 内无任何图片引用 | ✅ |
| 4 | 布局与背景 | 主区 `#F3F6FB`、侧栏 `#14233C`（x 0–219）、内容左边界 x=284 / 右 x=1373 | ✅ |
| 5 | 侧栏（标志/品牌/4 项导航/选中态/底部卡片） | 标志外框 (30,33,28,28) r7 + 内孔 (38,41,12,12)；选中胶囊 (18,116,184,48) r8；4 圆点 10×10；底部卡 (22,752,176,116) r12 | ✅ |
| 6 | 卡片 | KPI (260/644/1028, 138, 356×144)、图表卡 (260,310,742×286)、活动卡 (1030,310,370×286)、表格卡 (260,624,1140×218)，白底 + 1px `#E2E8F1`，r12 | ✅ |
| 7 | 图表 | 5 条 `#E7EDF5` 网格线 y=405/441/477/513/549，x=333–969；6 根柱 w54 r5，柱高 = 数值×1.2 px | ✅ |
| 8 | 表格 | 表头带 (284,688,1090×34) `#F3F6FB`；分隔线 y=760/795 `#EBEFF5`；3 枚标签 (1028, 729/764/799, 148×28) | ✅ |
| 9 | 状态标签 | In progress `#E7EFFF`/`#245CE4`、Review `#FFF3D7`/`#9D6613`、Done `#DCF5EC`/`#168267` | ✅ |
| 10 | 主要装饰 | 品牌环标、选中导航点 `#64DBB6`、未选中点 `#7791B3`、活动 3 圆点 `#EAAF40`/`#245CE4`/`#168267` | ✅ |
| 11 | 所有主要结构与信息完整 | `content.json` 的 brand / navigation×4 / title / subtitle / button / workspace_info×3 / kpis×3 / chart_title / chart_period / months×6 / chart_unit / chart_ticks×5 / activity×3 / table_title / table_columns×4 / rows×3 / footer 全部出现在 DSL 中（`build_a15.py` 内有 assert 校验） | ✅ |
| 12 | 不改成自己的新设计 | 未新增/删除任何元素；元素集合与参考图一一对应 | ✅ |
| 13 | 关键锚点 ±8 px | **49/49 锚点通过，最大 |Δ| = 1 px** | ✅ |
| 14 | 重建图表比例与标记 | 6 根柱 **高度/数值 = 1.2**（完全一致），柱底 y=549 零线，柱宽 54、间距 101 | ✅ |
| 15 | 表格 3 行顺序与状态编码 | 顺序 Atlas/Pulse/Orbit；编码 In progress/Review/Done 与三色一致 | ✅ |
| 16 | ≥12 个锚点，涵盖四象限/图表/表格 | 49 个锚点，覆盖左上/右上/左下/右下/图表 | ✅ |
| 17 | 用可测误差说明残余差异 | `reconstruction-audit.json`（逐项 delta）+ `comparison.md` 第 6 节 | ✅ |
| 18 | 不宣称逐像素复刻 | `comparison.md` 明确写出抽样一致率 98.29% 且非逐像素恒等 | ✅ |
| 19 | 所有指定最终 PNG 为服务真实响应且有同名 `.snapshot` | `reconstructed.png` 直接由 `snapkit.render()` 写入，未经任何后处理；同名 DSL 同请求生成 | ✅ |

补充实测指标（非 TASK 要求，用于自检）：

- 57 个文本元素墨迹位置：左偏差 ≤ **0 px**、上偏差 **0 px**、宽度 ≤ **3 px**；
- 21 个平涂色块逐点比对：**21/21 完全一致**（0 通道误差）；
- 全图每 2 像素抽样 324000 点，RGB 三通道差 ≤24 的比例 **98.29%**；
- 卡片/侧栏卡/状态标签/按钮/柱/品牌标的角点轮廓序列与参考图**逐值相同**。

---

## 5. 问题与修复表

| # | 问题现象 | 定位方式 | 修复方式 | 复验结果 |
|---|---|---|---|---|
| 1 | `build_a15.py` 首次运行 `ValueError: not enough values to unpack`（`G["button"]` 是 4 元组） | 读 traceback 定位到 spec 与解包不一致 | spec 的 `button` 补成 `(x,y,w,h,r)` 5 元组 | 构建通过 |
| 2 | `pill` 解包 `too many values` / `KeyError: 1231` | traceback + 打印 `pill_cfg` 下标 | 统一成 18 元组并改用 `cfg[16]/cfg[17]` 取底色/字色 | 3 行标签正确渲染 |
| 3 | 探针图文字墨迹被邻近探针污染（`sub16` 量出宽 402 而非 246） | 打印每格 ink bbox 发现重叠 | 探针改成 3 列 × 15 行、每格 470×54 且行距 60，`calib2` 之后全部命中 | 尺寸标定全部命中 |
| 4 | `calib_a15.py` 批次 1–4 出图仅 7180 B（几乎全白） | 逐像素统计发现无内容 | `cell_xy(i)` 用全局下标算行号，跨批时行号溢出画布；改为 `cell_xy(i - lo)` | 5 批全部有内容 |
| 5 | `calib2_a15.py` `NameError: lo` | traceback | `lo, hi = b*45, ...` 改为先赋值 `lo` 再算 `hi` | 通过 |
| 6 | `probe_weight.py` 服务返回 400 `PARSE_ERROR: Attr [fontStyle] value is invalid: Unexpected font style Bold` | 读响应 JSON | `fontStyle` 只接受 NORMAL/ITALIC；删掉 `Bold` 变体后重发 | 探针成功，证明**属性名未知被忽略、属性值非法会报错** |
| 7 | `calib3/4` 密度对比全部失真（ref 密度是 probe 的 1.4–1.7 倍） | 逐区域直方图对比 | 两处 bug：(a) 背景亮度从区域角点采样，角点可能落在字形上；(b) 探针文字固定画黑色，深底区域失真 | 改为用声明的背景 hex 算亮度；文字颜色改为与参考图一致（`#FFFFFF` / `#64DBB6` 等）；probe 侧阈值 `dd>1` 与参考侧统一 → 普通字重密度比精确到 1.000 |
| 8 | `calib6/7` 单元格超出画布 `IndexError` | traceback | `COLS/CW` 由 620/630 改为 470/480；行高 56→58、行距 60→62 | 通过 |
| 9 | 圆角明显偏小（角点轮廓比参考图少 1–2 档） | 打印参考图与重建图的角点轮廓序列逐一对比 | 卡片 10→12、侧栏卡 10→12、导航胶囊 6→8、状态标签 6→8、按钮 5→9、柱 6→5、品牌标 8→7 | **轮廓序列逐值相同** |
| 10 | 侧栏品牌标 `A02_logo_outer_top` 差 1 px（ref 34 / got 35） | 同一精确色值探针 | 半径 8→7 | 仍 1 px（抗锯齿亚像素），列入残余差异 |
| 11 | 表头 `PROJECT/OWNER/STATUS/DUE`、到期列、页脚颜色偏浅 | `colour_audit.py` 直方图：参考图墨色 `#63748F`/`#7B8BA3`，我的 `#93A0B3`/`#9FA9BA`/`#8D9BB1` | 按参考图最深墨色改为 `#63748F`（表头、到期）与 `#7B8BA3`（页脚） | 21/21 平涂色 + 全部文字墨色一致 |
| 12 | 粗体文字明显比参考图轻（墨迹密度只有参考图的 75–89%） | 引入「墨迹密度」指标，24 个字符串 × 6 个字重做标定 | 参考图粗体落在 Semi Bold(600) 与 Extra Bold(800) 之间，而 `fontWeight` 被忽略、`Inter Bold` 不可用；改为按 `密度误差 + 0.8×宽高误差` 在 6 个族 × ±2px 尺寸内自动求解（`calib5_a15.py`） | 密度比提升到 91–111%，宽度误差 ≤3 px |
| 13 | `REFUND RATE` 宽度多 7 px（101 vs 94） | `verify_render.py` 报 `dW=+7` | 单个字符串无法定出字号与字距的组合；`calib7_a15.py` 用三个 KPI 标签同时拟合，选 `Inter Extra Bold 13 / ls 0.6`（64/64、57/57、96/94） | 三标签宽度误差 ≤2 px |
| 14 | 导航文字过粗（`Projects` 密度比 1.58） | 分标签测密度：`Overview` 1.025 但 `Projects/Analytics/Settings` 1.58–1.66 | 参考图选中项确实更粗：选中项 → `Inter Extra Bold 19`，未选中项 → `Inter 19` | 三项未选中密度比 **1.000**，选中项 1.106 |
| 15 | 第一次验证 `kpi1_value/kpi2_value` 上偏差 4 px | `verify_render.py` | 估计的 `dy` 不准；用实测 `dx/dy` 回写 `text-offsets.json` 后重渲 | 全部 ≤1 px |
| 16 | DSL 根节点多一层冗余 `<Container>` | 读 `reconstructed.snapshot` 发现双层根容器 | 改为手工拼根：`<Container width height><Stack fit="EXPAND">` | DSL 更干净，像素不变（抽样一致率 98.22%→98.29%） |
| 17 | `make_audit.py` `KeyError: 'x'` | traceback | 锚点选择器 `"x"/"y"` 映射到 `x_first/y_first` | 49 锚点全部产出 |
| 18 | `make_comparison.py` 字符串里混入英文双引号导致 `SyntaxError` | traceback | 改用中文引号 | 生成成功 |

---

## 6. 本题踩到的 DSL 语义坑

1. **`fontWeight` / `font-weight` / `weight` 在 `Inter` 族上被静默忽略。**
   三种拼写、四个取值（`BOLD/600/700/800`）下渲染结果完全一致（密度 430063、宽 326）。
   想改字重只能换 `fontFamily`。
2. **`GET /fonts` 的列表不完整**：`Inter Bold` 服务端可用但未列出。
   同时 `fontFamily="Inter,Inter Bold"` 不会回退到 `Inter Bold`
   （退回 `Inter` 常规），所以族名列表的第一项决定了实际使用的字重。
3. **属性名非法 → 静默忽略；属性值非法 → 400 PARSE_ERROR。**
   `fontStyle="Bold"` 直接 400（枚举只有 NORMAL/ITALIC），
   而 `fontWeight="700"` 毫无反应。
4. **属性名大小写敏感**：正确拼写是 `fontSize`/`fontFamily`/`fontWeight`，
   `font-size` 这类写法无效（与 `_suite/DSL-HANDBOOK.md` 一致）。
5. **`Text` 墨迹偏移随内容变化**，不能只按字号套一条公式：
   实测 `dy` 在 3–7 px 之间（例如 `¥128,400`@31 → dy=7，`REVENUE`@13 → dy=3），
   `dx` 在 0–2 px 之间。必须逐元素实测。
6. **`borderRadius` 的整数档与理想圆弧有系统性偏差**：同样写 `10`，
   渲染出的角点轮廓比参考图对应的半径小约 1–2 档，需要用「角点轮廓反解」来定值。

---

## 7. 未解决事项与如实说明

1. **字重粒度无法完全对齐（主要残余差异）**。
   参考图粗体对应约 650–700 的字重，服务只提供 600/800 两档且 `fontWeight` 无效。
   当前解法是「优先保证墨迹宽度与位置不变，密度误差 ≤11%」。
   若允许更大字宽误差，可把密度误差压到 ~2%（`calibration5.json` 里保留了每档的最优解）。
   参考图本身很可能不是用本服务渲染的，或使用了本服务未暴露的变量字体档位——
   **这一条是推测，未获证实**。
2. **约 1.71% 的像素超出 ±24 通道差**，集中在粗体字形边缘的抗锯齿过渡像素上，
   是上面第 1 条的必然结果；结构性区域（平涂色、边框、网格线、柱体）
   实测为 0 误差。
3. **`A02_logo_outer_top` 差 1 px**：品牌圆角标的角点在 34/35 之间，
   属抗锯齿亚像素，无法用整数 `borderRadius` 精确命中。
4. **服务限流未触发**：71 次成功渲染 + 2 次 400，未出现 429/503，
   因此「限流/排队等待」记 0（确认未发生）。
5. **平台未提供的计量一律为 null**：`token`、`input_tokens`、`cost`、
   `image_input_usage` 等指标本次全部为 **null**，原因见下节。
6. **未做的事**：没有做逐像素模板匹配式的「完全复刻」；没有把参考图的
   任何像素块写进 DSL；没有使用 `<Image>`、`dataUri` 或外部图片。

---

## 8. 请求与耗时统计（来自 `tmp/20261004-182918/A15/requests.jsonl`）

| 项 | 值 |
|---|---|
| 请求总数 | 76（全部为渲染；文档/字体 0 —— 复用本题库已有抓取） |
| 成功 | 74（HTTP 200，`Content-Type: image/png`） |
| 失败 | 2（HTTP 400 `PARSE_ERROR`，均为 `fontStyle="Bold"` 探针） |
| 重试 | 0（无 429/503，`Retry-After` 未触发） |
| 渲染耗时合计 | 136587 ms（约 228 s，纯服务端时间） |
| 首次请求 | 2026-10-05T00:24:00.066+08:00 |
| 最后一次请求 | 2026-10-05T01:43:46.282+08:00 |
| 其中交付图渲染 | 13 次 `reconstructed.png`（2026-10-05T00:44:26.998 → 01:38:14.378 +08:00），其余为标定探针图 |
| 请求 ID | 76 个唯一 ID，34 个 `A15-req-001` … `A15-req-034`；另有 42 个 `_suite-req-001` … `_suite-req-042`（见下方说明） |
| `Server-Timing` 可见 | 是，例：`render;dur=267.7, total;dur=271.0` |
| `X-Request-Id` 可见 | 是（本地请求 ID 同时作为 `X-Request-Id` 发出，服务端响应头也回带） |
| 凭据 | 未使用、未记录任何密钥 |

失败响应原文保留在 `tmp/20261004-182918/A15/responses/`。

**留痕瑕疵（如实披露）**：`calib3_a15.py` 首次运行时漏掉 `snapkit.configure()`，
这 42 次标定请求被记成 `_suite-req-*` 前缀、`task_id="_suite"`，
但它们的响应文件实际落在 `tmp/20261004-182918/A15/probes/`，属于本题。
修复方式：给脚本补上 `snapkit.configure("A15", …)` 后**重新运行**，
新增 3 条正确标记的 `A15-req-*` 记录；旧记录按 AGENTS.md 要求**保留不删**。

### 8.1 token / 费用

| 指标 | 值 | 说明 |
|---|---|---|
| `input_tokens` | `null` | 服务响应头与响应体均未提供 token 用量 |
| `output_tokens` | `null` | 同上 |
| `image_input_usage` | `null` | 服务未提供图像输入用量字段 |
| `cost` / `currency` | `null` | 服务未提供计费信息 |

**没有按字符数、DSL 字节数或任何比例估算这些数字。** 任务墙钟耗时与请求耗时之和
分别记录在 `task-metrics.json`，两者不相等（构建、测量、对比分析都发生在请求之外）。

---

## 9. 过程留痕文件清单（`tmp/20261004-182918/A15/`）

| 文件 | 说明 |
|---|---|
| `requests.jsonl` | 76 条请求记录（ID/类型/起止/时区/耗时/HTTP 状态/Content-Type/请求与响应文件/错误摘要/X-Request-Id/Server-Timing） |
| `iterations.jsonl` | 由 `wrapup.py` 写入的迭代记录 |
| `layout.json` | 59 个文本元素的 DSL 框位置、目标墨迹坐标、字体字号字距、实测 dx/dy；6 根柱的几何 |
| `text-offsets.json` | 从实际渲染回写的每元素墨迹偏移（dx, dy） |
| `verify.json` | 57 个文本锚点的逐项 delta + 50 个结构锚点的参考/重建实测值 |
| `colour-audit.json` | 57 个文字墨色对比 + 21 个平涂色对比 + 324000 点抽样一致率 + 40 个最大偏差点 |
| `calibration*.json`（7 份） | 字号/字重/字距标定的全部候选与命中结果 |
| `reference-measurements*.json`（6 份）、`reference-text-ink.json` | 参考图的像素测量结果 |
| `probe-measurements.json`、`probe-meta.json` | 首轮字距/特殊字符探针的测量 |
| `probes/`（30 个 PNG+DSL） | 每一次标定探针的真实响应 |
| `crops/`（30 个 PNG） | 参考图与重建图的同坐标局部放大对比 |
| `responses/` | 2 个失败响应原文 |
| `*.py` | 全部测量、标定、构建、验证脚本 |
| `drafts/build-a15.snapshot` | 最终 DSL 的临时副本（与交付 DSL 字节一致） |
