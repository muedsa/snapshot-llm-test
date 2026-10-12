# B06 snapshot 使用记录 —— PLAINSIGHT 十件

- 任务：B06 把十个日常信息难题变成惊艳而好用的作品
- 运行：`run-20261002-220723-mimo` · 时区 UTC+08:00 · 系列 `PLAINSIGHT`
- 全部渲染走 `POST https://open-snapshot.muedsa.com/snapshot`（UTF-8 纯文本），PNG 为服务原始字节，落盘后不再改动
- 过程日志：`tmp/run-20261002-220723-mimo/B06/{requests.jsonl(81), iterations.jsonl(30), tool-usage.jsonl(14), calc-b06.json}`

---

## 1. 真实查阅的文档（9 + 1 次，全部 200）

| 请求 ID | URL | 状态 | 用来确认什么 |
|---|---|---|---|
| `B06-doc-01-ai-guide` | open-snapshot.muedsa.com/ai-guide.md | 200 | 服务约定：纯文本提交、PNG 返回、属性校验规则 |
| `B06-doc-02-parser-tags` | snapshot.muedsa.com/reference/parser-tags/ | 200 | 支持的标签集合与参数个数（`Ts` 12 参、`TXW` 10 参、`Circ` 4 参） |
| `B06-doc-03-painting` | snapshot.muedsa.com/guides/painting/ | 200 | 画刷、渐变、描边写法 |
| `B06-doc-04-enums` | snapshot.muedsa.com/reference/enums/ | 200 | `textAlign`、`BoxFit`、`BlendMode` 等枚举取值 |
| `B06-doc-05-transform` | snapshot.muedsa.com/widgets/layout/transform/ | 200 | `matrix` 16 个数、列序、外层括号、旋转基准 |
| `B06-doc-06-rendering` | snapshot.muedsa.com/guides/rendering/ | 200 | 裁剪、滤镜、BackdropFilter 的使用边界 |
| `B06-doc-07-decor-box` | snapshot.muedsa.com/widgets/painting/decorated-box/ | 200 | `border` 必须带 `color`、`boxShadow` 两种合法写法 |
| `B06-doc-08-source-index` | snapshot.muedsa.com/reference/source-index/ | 200 | 组件源码索引，用于核对参数顺序 |
| `B06-doc-09-faq` | snapshot.muedsa.com/reference/faq/ | 200 | 常见报错与尺寸取值方式 |
| `B06-font-01-list` | open-snapshot.muedsa.com/fonts | 200 | 27 个字体，映射到 `SANS` / `DISP` / `MONO` |

缓存文件保存在 `tmp/run-20261002-220723-mimo/B06/docs/`；这 10 次请求只在本题记一次，后续题目复用同一份文件时不重复计为新的 HTTP 请求。

---

## 2. 研究抓取（41 次：38 × 200、2 × 412、1 × 网络失败）

| 主机 | 次数 | 200 | 说明 |
|---|---|---|---|
| www.bing.com | 21 | 21 | 5 次多词查询试探 + 16 次短词 `format=rss` 查询（`setmkt=zh-CN` + 浏览器 UA） |
| sousuo.www.gov.cn | 13 | 13 | 政策库与站内检索入口，接口返回 `totalCount=0` |
| www.cma.gov.cn | 1 | 1 | 气象科普入口 |
| www.ndrc.gov.cn | 1 | 1 | 阶梯电价相关页面 |
| www.samr.gov.cn | 1 | 1 | 明码标价相关页面 |
| www.spb.gov.cn | 1 | 1 | 快递服务相关页面 |
| www.nmpa.gov.cn | 1 | **0** | 412 反爬页（HTML 原样留存） |
| www.nhc.gov.cn | 1 | **0** | 412 反爬页（HTML 原样留存） |
| lite.duckduckgo.com | 1 | **0** | 请求失败，无状态码 |
| 合计 | **41** | **38** | |

**结论（本题最大的能力边界）**：本轮没有取得任何一条法条、国家标准或服务标准**原文**。gov.cn 政策检索接口虽然返回 200，但响应里 `totalCount=0`；多词中文 Bing 查询会被截断，改用「一次一个短词 + RSS 格式」后才命中 16 条检索摘要。

因此十件作品的纪律是：

- 不写条款号、不写罚则金额、不写国标数值、不写任何机构背书；
- 唯一命中的外部线索是 **Bing RSS 短词检索的二手摘要**，画面与文档一律标注「检索摘要（Bing RSS，2026-10-08）」，只作为选题依据，不作为条文引用；
- case-02（用药）、case-08（降水概率）、case-10（快递时间窗）没有二手线索，明写 `self-authored-observation`，不冒充研究结论；
- 全部数值是演示样例 **DEMO**，画面内逐处标注。

失败响应（2 条 412 + 1 条无状态码）原样保留在 `requests.jsonl` 与 `research/`，没有被抹平，也没有伪造成功记录。抓取的中文页被 PowerShell 5.1 按 Latin-1 解码的问题，用 `repair-encoding-b06.ps1` 修出同名 `.fixed` 文件，**原文件不修改**。

---

## 3. DSL 实际用了什么

十件作品的结构骨架互不重复，全部由矩形 / 圆 / 渐变 / 矩阵 / 裁剪画出，**外部图片素材 0 个**：

| 件 | 结构骨架 | 主要构件 |
|---|---|---|
| 01 货架单价换算 | 货架网格 + 对齐刻度条 | `Page6` + `Rect`/`RoundRect` 分层 + `Pct100` 变体的价格条 + `Step6` |
| 02 当日用药卡 | 当日时间轴 + 问答卡 | `Circ`（实心 = 已服 / 双环 = 待服）+ 7×3 药格网格 |
| 03 体检报告行动清单 | 参考区间尺 + 动作卡连线 | `Ruler6` 逐项区间尺 + 状态色指针 + 连线 `Rect` |
| 04 电费阶梯账单 | 分档瀑布 + 闭合核对 | `ColStack6` 三档叠块 + `Tier-Bar` 共享刻度 |
| 05 站台到发与换乘 | 站台大屏 + 等比到发条 | 线路色带 `Rect` + 按分钟等比的到发条 + 圆角子面板 |
| 06 信用卡分期真实年化 | 现金流竖排 + 共同量程费率尺 | 12 期 `ColStack6`（本金 + 手续费两段）+ `Ruler6` 四口径尺 |
| 07 退租押金扣减瀑布 | 扣减瀑布 + 斜纹争议标记 | `Waterfall6` + **`Hatch6`**（争议行 45° 斜纹，透明度 0x33） |
| 08 降水概率怎么读 | 100 格点阵 + 翻译卡 | **`Pct100`** 10×10 点阵（填色由 `(i × 37) mod 100 < 40` 决定） |
| 09 路侧停车限时计费 | 钟面分档 + 计费刻度 | **`Hand6`** 指针 + **`Wedge6`** 三段扇形 + **`Arc6`** + `Ruler6` 带数字刻度 |
| 10 快递到件时间窗 | 节点轨道 + 共尺时间窗 | 五节点圆角块 + 与「现在」共用 105 分钟量程的比例条 |

`lib-b06.ps1`（链式复用 lib-b05 → b04 → b03 → b01）新增：

```
Get-Calc6 · D2/D1/D4/D0 · LabN · Tone6/Tone · Masthead6 · Foot6 · Src6 · Legend6
Step6 · Hand6 · Wedge6 · Arc6 · Hatch6 · Dial-Map · Ruler6 · Pct100
ColStack6 · Waterfall6 · Page6 · Write-Dsl6 · Report-Problems6
```

**先探针后依赖**：`Wedge6 / Arc6 / Hand6 / Ruler6 / Pct100 / Waterfall6 / ColStack6` 在任何一件作品用到之前，先跑了一次 `B06-smoke-01` 真机冒烟渲染（200，92,838 B）验证服务端支持；`Hatch6` 另做两次探针渲染 `B06-probe-hatch` / `B06-probe-hatch-a2`，并用逐像素扫描确认几何。

---

## 4. 数据与算术：先算、再画

`calc-b06.ps1` 把十件的全部数字算出并落盘为 `calc-b06.json`（41,312 B），生成器只读它、**不在画面里临时心算**。这样每一处百分比的分子、分母、单位与时间范围都同源：

- case-01 `groupCount = 3` · `disagreeCount = 3`（9 个价签，3 组）
- case-03 `total 6 = normal 3 + recheck 2 + sooner 1`
- case-04 上期 220 度 / 130.86 元 → 本期 356 度 / 236.63 元，差 **105.77** 元 = 二档增量 38.28（57.42 − 19.14）+ 三档新增 67.49；电费 +80.8% / 电量 +61.8% / 单价 +11.8%；档位占比 63.8% / 36.2%
- case-06 名义 7.20% → 月 IRR 1.0862% → 年化 13.03% / 实际 13.84% / 平均未还本金口径 13.29%
- case-07 6000 → 固定扣 760 + 争议 600；全扣退 4,640、争回退 5,240，差额 **600**（恰好等于争议合计）
- case-08 点阵填 **40 / 100**：`(i × 37) mod 100` 在 `i = 0..99` 上是 `0..99` 的一个排列（37 与 100 互质），其中恰有 40 个落在 40 以下 —— 与画面文字逐字一致，可核对
- case-09 累计 **3 / 9 / 17**（取自 `cumulative[].cum`，不是 `brackets[].fee` 的分段增量 3/6/8）；`120 − 27 = 93` 分钟
- case-10 `43 / 78 = 55.1%`；等待 75 分钟 + 窗宽 30 分钟 = 105 分钟共同量程

**视觉迭代里发现的三处数字矛盾全部是「读图」发现的，脚本一个都没发现**：

1. case-04 标题与页脚硬编码 `+80.6%`，KPI 卡由 130.86 → 236.63 算出的是 `+80.8%`；
2. case-06 KPI 写 `13.8%` / `7.2%`，标题与刻度写 `13.84%` / `7.20%`，且图例 `月 1.0862 x 12` 缺百分号；
3. case-09 档位卡标题写「累计」，值却是分段增量 3/6/8，最后一根比例条画成 8/17，看上去像还没到顶。

三处都已修正并重新渲染、重新读图确认。

---

## 5. 工具链与实际做法

| 脚本 | 作用 |
|---|---|
| `fetch-all-b06.ps1` | 41 条研究 + 9 条文档 + 1 条字体，逐条写 `requests.jsonl` |
| `repair-encoding-b06.ps1` | 修复 PS 5.1 把 UTF-8 响应体按 Latin-1 解码的问题（读 UTF-8 → 按 28591 编码 → 按 UTF-8 解码 → 写 `.fixed`） |
| `calc-b06.ps1` | 十件全部数字一次算出 |
| `lib-b06.ps1` | 共享绘图与排版构件 |
| `validate-b06.ps1` | 静态属性与越界校验，最终 `files=20  problems=0` |
| `gen-b06-a/b/c.ps1` | 分段生成 10 件自包含 DSL（a:01-04 · b:05-07 · c:08-10），每轮跑 `Guard` 越界守卫 |
| `render-b06.ps1` / `smoke-b06.ps1` | `POST /snapshot`，全字段写 `requests.jsonl` |
| `promote-b06.ps1` | 逐件字节校验后落 `final.png` / `final.snapshot` / `.round` |
| `mk-iter-b06.ps1` | 从 `requests.jsonl` 反查生成 `iterations.jsonl`（join key = `request_key`） |
| `mk-toolusage-b06.ps1` | 从 `requests.jsonl` 分组生成 `tool-usage.jsonl`（14 条，覆盖全部 81 个请求 ID） |
| `gen-case-md-b06.ps1` | 逐件 `case.md`（画幅、口径、渲染请求表、读图证据表） |
| `mk-portfolio-b06.ps1` | `portfolio.json` / `portfolio.md` / `gallery.html` |
| `mk-metrics-b06.ps1` | `task-metrics.json`，全部从 JSONL 反查 |

**归档约定**：每次渲染尝试存为 `case-NN/aNN.png`（`a01` = 基线），工作 DSL 是 `case-NN/r01.snapshot`；**每次渲染前把 `r01.snapshot` 复制成 `aNN.snapshot`**，使每一次尝试的 DSL 都被逐字节保留。接受的那一次再由 `promote-b06.ps1` 复制为 `final.png` / `final.snapshot`。

**读图协议**：`read` 工具会串图，所以每次读之前新建一个 GUID 文件名的副本、用 `System.Drawing` 画一圈描边（10 px，inset 5）、等待 5–7 秒再读，读完**必须同时核对描边和报头 `PLAINSIGHT NN / 10`**；不符就整张作废，换新 GUID 副本重读。必要时用逐像素扫描候选 PNG 判断究竟交付了哪一张。

---

## 6. 跨题经验与踩坑（供后续题目直接复用）

### 6.1 读图串图必须用「报头 + 描边」双重确认

`case-02` 的 a03 就是被串图的：`read` 返回了别的文件的像素，报头是 `04/10` 而不是 `02/10`。它在 `iterations.jsonl` 里被如实记为 `not-verified`、`view_confirmed=false`、`view_path=""`，同一处图例改动在 a04 上重新读图确认后再接受。

**不要用文件名确认**，要用图片里画着的字确认。只有报头（和自己画的描边）是写在像素里的。

### 6.2 `$L` 覆盖 `$l` —— 服务返回 200 但几何是错的

探针 `B06-probe-hatch` 的扫描结果：`y=110` 上 box1 的斜纹从 `x=130` 而非 `24` 开始。原因是 `Hatch6` 里一个长度局部变量被写成 `$L`，而 PowerShell **变量名不区分大小写**，`$L` 静默覆盖了 `l`（left）位置参数，两个 `ClipR` 框都被输出成 `left=130.11`（恰好等于条长）。

- 服务照样返回 200，**没有任何报错**；
- 改名 `barLen` / `halfSpan` 并把陷阱写进 `lib-b06.ps1` 头部注释后，第二次探针扫描得到 `24..354 / 354..405 / 406..735`，与书写几何完全一致。

**结论：几何类缺陷只能靠看图 + 像素扫描发现，静态校验发现不了。**

### 6.3 PowerShell 5.1 的老坑（本题又踩到的）

- `Measure-Object -Property <key>` **读不到 OrderedDictionary 的键** → 逐项 `for` 累加；`Sort-Object <prop>` 也不会给 OrderedDictionary 排序。
- **`int + string` 会把字符串转成 int 并报错**（`$n + ' 行…'` 崩），字符串必须放左边，或统一用 `-f` 格式化。
- `[pscustomobject]@{}` 不允许事后加属性 → 所有字段写进同一个字面量。
- `Invoke-WebRequest` 把 UTF-8 响应体按 Latin-1 解码 → 读 UTF-8 → 按 28591 编码 → 再按 UTF-8 解码，写 `.fixed`，原文件不动。
- `write` 工具写完含中文的 `.ps1` **没有 BOM**，`edit` 工具还会**把 BOM 剥掉** → 每次写/改之后必须重新 BOM 编码再执行。
- 双引号字符串里的 `` ` `` 是转义符 → markdown 反引号用 `$BQ = [char]96` + `Code()` 拼，不要写进字符串字面量。
- `-like` 把 `[` `]` 当通配符 → 用 `.Contains()` 或正则。

### 6.4 DSL 侧反复验证过的结论（本题新增）

- `Hatch6(l,t,w,h,rad,c,pitch,thick)` 成立：`ClipR` + `<Stack clipBehavior="NONE">` + 旋转斜条，条长 `(h+2)/0.70710678`，圆角内不会外溢。
- `Wedge6(cx,cy,rr,a0,a1,c,n)` 扇形、`Arc6` 沿弧排点、`Hand6(cx,cy,len,th,deg,color)` 指针都通过服务渲染；`Dial-Map(minute, windowMin) = -90 + 360*minute/windowMin`。
- `Ruler6` 的量程必须**自带数字刻度**；只有刻度没有数字，读者无从知道整条是多少（case-09 a01 的缺陷）。
- `ClipR(l,t,w,h,rad,inner)` 的内部 `Stack` 子元素坐标**相对 (l,t)**，不是画布坐标。
- 根 `<Snapshot type="png" background="…">` 不写 width/height，尺寸由第一个 `<Container width height>` 决定。
- 比例条 / 瀑布 / 柱组必须**共用同一分母**；各按自身总量归一会让不同量级画成等长（case-04 a01 的缺陷）。

### 6.5 「改善两栏」是信息设计类题目的声明纪律

B06 要求区分「从最终图直接可观察的改善」和「需要用户实验才能验证的效果」。落成结构就是 `problem-evidence.json` 里每个 case 的 `observable_improvements[]` 与 `not_validated_by_user_experiment[]` 两个数组，目前分别是 **40 条**与 **30 条**，另加 `totals.field_research_sessions = 0`、`user_tests = 0`、`statutory_citations_used = 0`。

- 「可观察」的判据是：**任何拿到图的人都能自己数、自己比、自己核对**（例：「点阵填 40 / 100 格，可逐格数」）。
- 「未验证」的判据是：**需要真实使用者的行为或前后测才能得出**（例：「3 秒完成比价」「减少漏服」「读者不再把概率当分钟」）。

两者不能混写，否则「设计目标」会被读成「已达成的结论」。`design-review.md` 用叙述版复述同一条边界。

---

## 7. 复核结论与剩余事项

**已复核**

- `requests.jsonl` 81 行，0 行坏 JSON；78 × 200、2 × 412、1 × 无状态码。
- 30 次 render 全部 200（27 条用例 + 1 条冒烟 + 2 条探针）；`case_metrics` 逐件请求之和 27 = 整体。
- `iterations.jsonl` 30 行：12 accepted / 17 needs-change / 1 not-verified；逐件之和 27 + 冒烟 1 + 探针 2 = 30。
- `tool-usage.jsonl` 14 行，`http_request_ids` 合计 **81** = `requests.jsonl` 全部条目，无遗漏无重复。
- `validate-b06.ps1` 最终 `files=20  problems=0`。
- 10 件 `final.png` 的 SHA256 与服务原始响应一致；PNG 实际像素与 DSL 首个 `Container` 一致（10/10）。
- 每件 `final.png` 都有一次成功读图并核对了 `PLAINSIGHT NN / 10` 报头。

**剩余事项 / 已知边界**

1. **没有取得任何法条、国家标准或服务标准原文** —— 十件不引用条款号、不写罚则金额、不写国标数字、不写机构背书。这是本题最大的能力边界，已写进 `problem-evidence.json` 的 `policy` 与 `design-review.md` 的第 0 节。
2. **没有做田野调研、用户访谈或可用性测试** —— 30 条 `not_validated_by_user_experiment` 是设计目标而非已验证结论。
3. `B06-res-25-ddg-lite` 请求失败无状态码，原样保留；`nmpa` / `nhc` 的 412 反爬页原样保留。
4. `read` 串图后被丢弃并换新 GUID 副本重读的次数**没有日志**，`image_views_confirmed = 29` 是下界。
5. `case-03` 的尝试编号跳过 `a03`（该次没有产生渲染请求），`.round = 4` 但实际只有 3 次渲染 —— 已在 `case.md` 与 `task-metrics.json` 逐处写明，**没有补造请求**。
6. token / 图像使用量 / 费用平台未提供，`task-metrics.json.usage` 全部为 `null`。
