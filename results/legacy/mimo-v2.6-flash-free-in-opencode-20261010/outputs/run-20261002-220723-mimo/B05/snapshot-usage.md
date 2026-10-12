# B05 snapshot 使用记录 —— 同梯 TongTi

- 任务：`B05 product from zero` · 运行：`run-20261002-220723-mimo` · 时区：UTC+08:00
- 交付：10 屏完整产品旅程 · 10 种互不重复的宽高比 · 38 次真实渲染 · 10/10 件逐张打开复核
- 日志：`tmp/run-20261002-220723-mimo/B05/{requests,iterations,tool-usage}.jsonl`

---

## 1. 真实查阅的文档（9 + 1 次，全部 200）

| 请求 ID | 地址 | 用在本题哪里 |
|---|---|---|
| `B05-doc-01-ai-guide` | open-snapshot.muedsa.com/ai-guide.md | 服务约定、POST 体例、编码与响应字段；`render-b05.ps1` 按它拼请求并把 `request_id` / `Server-Timing` / `ratelimit_remaining` 全字段写进 `requests.jsonl` |
| `B05-doc-02-parser-tags` | snapshot.muedsa.com parser-tags | 确认根节点 `<Snapshot type="png" background>` 不带 width/height，画幅取自第一个内层 `Container`；确认没有 polygon/path，形状只能靠矩形、圆与矩阵变换 |
| `B05-doc-03-painting` | snapshot.muedsa.com painting | 渐变、`Stack` / `Positioned` 的裁剪与绘制顺序；剖面底纹与井道深槽的叠放次序 |
| `B05-doc-04-enums` | snapshot.muedsa.com enums | `textAlign` 只接受 `LEFT / CENTER / RIGHT`（`LEFT_CENTER` 是错的）；`boxShadow` 只接受 `ELEVATION_n` 或 `dx dy spread #color` |
| `B05-doc-05-transform` | snapshot.muedsa.com transform | `Transform matrix` 是 16 个浮点的列主序矩阵、括号不能省；`Rotate` 的内层坐标相对自身原点 |
| `B05-doc-06-rendering` | snapshot.muedsa.com rendering | 文本渲染与字体族；本题排版只用 SANS / DISP / MONO 三种 |
| `B05-doc-07-decorated-box` | snapshot.muedsa.com decorated-box | `border="N SOLID #COLOR"` 必须配一个 `color`，且只在矩形容器上成立 |
| `B05-doc-08-source-index` | snapshot.muedsa.com source-index | 标签总索引，用来核对没有用到未实现的标签 |
| `B05-doc-09-faq` | snapshot.muedsa.com faq | 已知限制（`maxLines` 被忽略、`BackdropFilter` 全文只允许一个、高斯模糊之外的滤镜不支持） |
| `B05-font-01-list` | open-snapshot.muedsa.com/fonts | 27 种可用字体，确认 SANS / DISP / MONO 三个族存在，避免渲染时回退到默认字体导致行宽计算失真 |

> 文档抓取的原始响应留在 `tmp/run-20261002-220723-mimo/B05/docs/`，10 个文件。
> 字体查询结果未落独立文件，请求本身记录在 `requests.jsonl`。

## 2. 研究抓取（20 次：18 × 200、1 × 404、1 × 网络失败）

`B05-res-01-mohurd` … `B05-res-20-flk-root`，覆盖住建部、国务院政策库、发改委、司法部行政法规库、
国家法律法规数据库、北京与上海政务检索入口等，19 个抓取产物留在 `research/`。

**结论是负面的，而且必须写出来**：这轮研究**没有取得任何一条既有住宅加装电梯费用分摊的政策原文**。
因此本题在 10 屏里：

- 不引用任何法条条号；
- 不给出任何"法定分摊比例"；
- 不引用任何地区的补贴标准金额；
- 补贴 240,000 元标注为**演示数据 DEMO**，并写"以当地政策核定为准，本次未取得政策原文"；
- A / B / C 三套权重明写为**本产品自定义规则，不是法规要求**；
- 三家供应商的报价、工期、质保年限、检验结论、现场记录、负责人、截止日期、受理编号全部标注为演示样例。

这条纪律写进了 `product-brief.md` 第 5、9 节与 `journey.json` 的 `claims_discipline`。

两次失败按原样保留，没有伪造：

- `B05-res-16-sh-search` → HTTP 404（上海政务站内搜索入口不存在）；
- `B05-res-10-ddg` → 无状态码的网络失败（html.duckduckgo.com 不可达）。

## 3. DSL 实际用了什么

**根与画幅**：`<Snapshot type="png" background="...">` 不带 width/height；每屏的第一个
`<Container width height>` 决定画幅，10 屏的实际像素与它逐一对齐（10/10 无偏差）。

**结构**：`Positioned`（只作为 `Stack` 的直接子节点）· `Stack` · `Container` · `ClipPath`（仅少量使用）。

**形状**：矩形、圆角矩形、圆、`Rotate`（矩阵旋转）· 渐变（`Transform matrix` 16 浮点列主序）。
没有 polygon / path，剖面的井道深槽、轿厢块、斜向进度线全部由矩形 + 矩阵变换拼出。

**文本**：主排版走 `lib-b05.ps1` 的 `Ts`（12 参签名）与 `Section5` 的多行块；
`TXW`（10 参，`extra` 先按 `;` 再按 `=` 切）用于需要字距与字重的标题。
全题用到的字体族只有 `SANS` / `DISP` / `MONO`。

**装饰即控件（可解释才用）**：
- 模型 A / B / C 的选择药丸 —— 橙色实心 = 当前选中，描边 = 未选，配文字标签；
- 剖面里被高亮描边的本户格子（case-07 的 602）—— 表示"这一屏在说你家"；
- 被点亮的里程碑圆点（case-08）—— 青 = 已完成、橙 = 进行中、灰 = 未开始，配阶段名与日序；
- 12 户状态格的三色（case-06）—— 青 / 琥珀 / 珊瑚与图例一一对应。

**边界（本题实测并遵守）**：
- 圆上的 `border` 必须写成 `N SOLID #HEX` 而不是裸色值 —— 写错就是 HTTP 400；
- `Ts` 第 12 个字面量若误落进 `bold`，服务端会报 `fontStyle=LEFT` 非法；
- `color` 只接受 `#RRGGBB(AA)` 或 `none`，写成中文就 400；
- 8 位十六进制 = `#RRGGBBAA`，用来做半透明叠加而不是另开透明度属性；
- `boxShadow` 只接受 `ELEVATION_n` 与 `dx dy spread #color`；
- `maxLines` 被忽略，截断要自己算；
- 全文只允许一个 `BackdropFilter`；
- 自定义渐变对齐只支持 `(-1,0)`；
- 可见文本里不允许出现 4 位以上小数。

## 4. 数据与算术：先算、再画

`calc-b05.ps1 → calc-b05.json`（23,382 B）是唯一数据源，10 屏只引用不改写：

| 量 | 值 |
|---|---|
| 造价 / 补贴 / 净自付 | 528,000 / 240,000 / **288,000** 元 |
| 模型 A 权重和 / 单位权重 | 6.70 / 42,985 元（零负担 2 户） |
| 模型 B 单价 | 309.08 元每平米（西 23,614 / 东 24,386） |
| 模型 C 权重和 / 单位权重 | 6.10 / 47,213 元（零负担 4 户） |
| 最大极差 | 24,386 元，并列出现在 102、202 |
| 三期付款 | 12,896 + 17,194 + 12,895 = 42,985 元 |
| 每年公共支出 | 4,800 + 1,800 + 1,200 + 6,000 = 13,800 元 |
| 十年 | 288,000 + 138,000 = 426,000 元；每户十年 426,000 ÷ 12 = 35,500 元 |
| 602 室十年三模型 | 63,582 / 36,071 / 69,836 元，相差 33,765 元 |
| 工期 | 10+10+14+15+8+8 = 65 天；开工 2026-10-20 = 第 1 天，第 28 天 = 2026-11-16，第 65 天 = 2026-12-23 |
| 进度 | 28 ÷ 65 = 43.1% |
| 验收 | 12 项 = 10 合格 + 1 待检 + 1 整改，验收 2026-12-19，责任期限 12-21 |

**口径纪律**：分项四舍五入到元后合计可能出现 288,002，画面统一以 **288,000 元**为准并写脚注；
`weightSum` 在 calc 里先 `Round(x, 2)` 再落盘，显示用 `.ToString('0.00')`，
避免出现 `6.699999999999999993` 这种裸浮点（这个 bug 在 round-02 被读图抓到并修掉）。

## 5. 工具链与实际做法

| 工具 | 实际做了什么 |
|---|---|
| `fetch-b05.ps1` | 10 次文档 + 1 次字体 + 20 次研究的真实 HTTP 抓取，逐条写 `requests.jsonl` |
| `calc-b05.ps1` | 三套分摊模型、造价与补贴、付款节点、65 天工期、12 项验收日期、十年总账全部程序算出 |
| `lib-b05.ps1` | `Masthead5` / `Foot5` / `Section5` / `Stack1` / `MarkDot` / `CheckBox` / `Tick` / `Outline` / `Pill` / `Write-Dsl5` / `Report-Problems5` |
| `gen-b05-a/b/c.ps1` | 分段生成 10 屏自包含 DSL（01-03 / 04-06 / 07-10），每轮跑越界守卫 + 属性校验 |
| `smoke-b05.ps1` | 2 次真机冒烟渲染，先确认服务、字体与 8 位色可用 |
| `render-b05.ps1` | `POST /snapshot`，写全字段 `requests.jsonl`（含 `request_id`、`Server-Timing`、`ratelimit_remaining`） |
| `promote-b05.ps1` | 把 round-02 的 PNG 与 DSL 逐字节复制成 `final.png` / `final.snapshot`，并写 `.round` |
| `read` 工具 | 逐张打开最终图，核对刊头 `TONGTI NN/10` 与画幅后再判定 |
| `System.Drawing` | 尺寸、SHA256、逐像素生成唯一字节副本（角像素微调或加边框），用于破解读图串图 |
| `mk-logs` / `gen-case-md` / `mk-metrics` | 从 JSONL 反查生成 `tool-usage.jsonl`、`case.md`、`task-metrics.json`，不手写计数 |

**渲染账**：38 次 render = 2 次冒烟 + 36 次用例渲染；32 次 200，6 次 400。
6 次 400 全是属性写法错误（3 次把 `border` 裸色值写在圆上、2 次 `Ts` 第 12 个参数落进 `bold` 产生 `fontStyle=LEFT`、
1 次 `color` 写成中文 `元`），修好后重交全部 200。**0 次 429**，`ratelimit_remaining` 最低 110。

## 6. 跨题经验与踩坑（供后续题目直接复用）

### 6.1 读图串图是本套最费时间的坑

`read` 工具按内容哈希缓存，连续读取或读同内容副本时会返回**上一张**的字节。
本题 round-02 后段可逐条核验的就有 8 次（读到 case-07/02/08/10/03 的旧图），
round-01 与 round-02 前段同样有串图重读。

**可用的恢复办法（已验证）**：

1. 每次只读一张；
2. 用 `System.Drawing` 把 PNG 复制到 `view/`，文件名带新 GUID，**并改 1 个角像素或加 2px 边框**，得到全新 SHA256；
3. `shell` 里创建文件后 `Start-Sleep -Milliseconds 900~3000` 再 `read`；
4. 读完**必须核对刊头的 NN/10 与画幅**，不对就换一个全新文件名重读；
5. 串图时直接读**原始 PNG 路径**（例如 `case-09/r02.png`）常常能立刻拿到正确字节。

`browser.preview` 在本环境不可用（`browser.disconnected`），看图只能走 `read`。

### 6.2 PowerShell 5.1 的老坑（本题又踩到的）

- `.ps1` 里有中文就必须带 BOM；`edit` 工具会剥掉 BOM，**每次编辑后要重新补 BOM** 再执行；
- 双引号字符串会展开 `$var`，搜索/替换负载一律用单引号；
- **markdown 反引号不能写进双引号字符串**（`` `t `` → TAB、`` `r `` → CR），要用 `$BQ = [char]96` 拼；
- `Measure-Object -Property <key>` 读不了 `OrderedDictionary` 的键，求和要用循环；
- `Sort-Object <prop>` 对 `OrderedDictionary` 不按数值排，且 JSON 反序列化出的对象要靠脚本块排序；
- `$m` / `$M` / `$d` / `$D` 是同一个变量，取刊头结果必须换名字（本题用 `$mh`）；
- `[char]0xNNNN + [char]0xNNNN` 会做整数加法，拼中文只能用字面量或 `edit` 工具；
- `@(@('a','b'))` 会被压平，成对元素要写 `@(, $pair)`；
- 函数参数里的 `if` 表达式（`(if ...)`）是语法错误，要先 `$x = if (...) {...}`；
- 不要定义叫 `H` 的辅助函数。

### 6.3 DSL 侧反复验证过的结论

- 画幅只看第一个 `Container`，根节点不带尺寸 —— 校验脚本据此比对 PNG 实际像素；
- `Ts` 是 12 参签名，多传一个字面量会静默落进 `bold`；
- `TXW` 是 10 参，`extra` 先按 `;` 再按 `=` 切；
- `Circ(l,t,d,c,b)` 的参数顺序是**颜色在前、边框在后**；
- `border` 在矩形容器上要写 `N SOLID #HEX` 且必须配 `color`；圆上同理，裸色值直接 400；
- 可见文本绝不能出现 4 位以上小数，`Transform matrix` 里的内部几何小数不算可见文本；
- 文本越界只能自己守卫：`Report-Problems5` + 每屏的 `Guard` 断言（例如 `case-07-pay`、`case-07-btn`）。

### 6.4 跨屏一致性是产品题的硬要求，必须有脚本级检查

本题做过两轮文本比对，都写进了 `portfolio.md` 与 `gallery.html`：

- `288,000` → 02 / 03 / 04 / 10
- `42,985` → 01 / 02 / 03 / 04 / 05 / 07
- `7 / 12` 与 `9 / 12` → 01 / 06（三色格与剖面逐户一致：青 7 / 琥珀 2 / 珊瑚 3）
- `2026-10-08` → 01（状态快照）与 06（异议期第 1 天），04 的剩余 4 / 7 / 10 天同以此为今日
- `65 天` → 05 / 07 / 08

**靠这次检查抓到的真问题**（都是读图或文本比对才发现的，守卫查不出来）：

1. case-09 的首次运行记录写成 `2026-10-12`，早于开工 2026-10-20；
2. case-06 的异议期写成"第 3 天"（= 10-10），与 case-01/04 的 10-08 快照矛盾；受理编号 `WT3-20261007-07` 又早于签约起始 10-08；
3. case-10 的 KPI 标签写"每户年均"却配 35,500 元（那是每户十年合计 426,000 ÷ 12），标签与数值口径不符；
4. case-03 的模型 B 显示 `309 元/㎡`，与同一张卡的规则行 `309.08 元/㎡` 不一致；
5. case-08 的现场记录日期 10-15 早于开工，交付 12-06 与 65 天工期对不上。

全部修复后重新渲染并重新读图确认。

### 6.5 零到一产品题的声明纪律

- 研究没拿到政策原文，就**明确写"没拿到"**，而不是换个说法绕过去；
- 金额一律标 **演示数据 DEMO** 或样例价格，别让人误以为是询价结果；
- 分摊权重是**产品规则**，不是法规，画面与文档都要写明；
- 没做用户访谈就写"未验证"，成功指标标成设计假设；
- 装饰元素只有在**能用一句话解释它承担什么控件含义**时才让它兼作控件，并且必须配文字标签。

## 7. 复核结论与剩余事项

**已复核（全部有证据）**

- 10/10 件 `final.png` 与服务原始响应**逐字节一致**（SHA256 比对），同名 `final.snapshot` 与 round-02 原件一致；
- 10/10 的 PNG 实际像素 = DSL 首个 `Container` 的 width × height；
- 10/10 的 `.snapshot` 属性校验 0 问题（`border` / `color` / `textAlign` / `boxShadow` / `fontStyle`）；
- 生成器（`gen-b05-a/b/c.ps1 -Round 2`）多轮全量运行，最终输出 `problems = 0`；
- 10/10 的最终图都用 `read` 打开过并核对刊头；
- 跨屏数字与日期的文本比对通过；
- 37 个交付文件（7 个索引/文档 + 10×3 逐屏文件）全部存在，`gallery.html` 的 36 条相对链接全部有效。

**剩余事项 / 边界**

1. **政策口径缺位**：没有拿到既有加装电梯分摊的政策原文，产品不提供合规背书，只提供算术与留痕；
2. **未做用户验证**：没有访谈、测试或楼栋试点，`product-brief.md` 的成功指标是设计假设；
3. **演示数据**：梧桐里 3 号楼、12 个户号、三家供应商、检验结论、现场记录、负责人与受理编号全部是样例，接真实数据前必须清掉 DEMO 标记；
4. **token / 图像使用量 / 费用**：平台未提供，`task-metrics.json` 中一律为 `null`；
5. **读图通道**：`read` 仍会串图，本题靠唯一字节副本恢复，后续题目建议沿用第 6.1 节的流程。
