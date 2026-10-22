# Snapshot 使用情况说明与踩坑记录

任务ID：A11
任务名称：A11 · 文字保真与跨页结算单
本次运行ID：run-20261011-01
完成状态：完成
结束原因：全部需求满足并完成两页与局部裁剪的视觉自检
输出目录：outputs/run-20261011-01/A11/
临时目录：tmp/run-20261011-01/A11/
路径基准：suite_root（本文件内 Markdown 链接相对本文件）

遵循[PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径。图片链接
相对本文件（最终图与 DSL 在同目录）。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| [invoice-page-01.snapshot](invoice-page-01.snapshot) | 第 1 页可复现DSL（1200×1600） | [invoice-page-01.png](invoice-page-01.png) | 完成 |
| [invoice-page-01.png](invoice-page-01.png) | 服务返回的最终图片（原始字节，217989 B，md5 63f4f36c…） | [invoice-page-01.snapshot](invoice-page-01.snapshot) | 完成 |
| [invoice-page-02.snapshot](invoice-page-02.snapshot) | 第 2 页可复现DSL（1200×1600） | [invoice-page-02.png](invoice-page-02.png) | 完成 |
| [invoice-page-02.png](invoice-page-02.png) | 服务返回的最终图片（原始字节，187705 B，md5 c35f6ec3…） | [invoice-page-02.snapshot](invoice-page-02.snapshot) | 完成 |
| [invoice-audit.json](invoice-audit.json) | 金额/舍入/字面行/发射证据/视觉实测审计 | 支撑两页最终图 | 完成 |
| [text-map.json](text-map.json) | 51 条文字条目（字段路径、原文、页图、像素盒、字体）+ 7 项检查 | 支撑两页最终图 | 完成 |
| [task-metrics.json](task-metrics.json) | 结构化指标 | — | 完成 |

需求逐项核对（证据 = 两页最终图 + invoice-audit.json + text-map.json 的实测数据）：

- 两页 1200×1600、同一发票号 SN-2026-1107-008、页眉逐像素一致（页眉区 diff 0、页脚左侧
  diff 0）、页码“第 1 页 / 共 2 页”“第 2 页 / 共 2 页”✓。
- 第 1 页：买卖双方、编号/开票日期/币种、4 行 SKU（中英日混排品名：结构化视觉工具包 /
  Visual Toolkit、几何卡片 · Geometry Cards、合同审校 / 契約レビュー、远程工作坊 /
  Remote Workshop），数量/单价/金额三列，SKU `A<B&C>D` 显示真实字符 ✓。
- 金额用十进制定点（Python Decimal，ROUND_HALF_UP）计算：行金额 805.50 / 478.80 /
  1160.00 / 1680.00 → 小计 4124.30；折扣 −180.00 → 税前 3944.30；税基精确 3944.30 ×
  6% = 236.6580 → 236.66（四舍五入至分）；运费 35.00 → 应付 4215.96；汇总按 notes 的
  计税顺序（小计→税前→税额→应付）排列，左侧“计税顺序 TAX ORDER”逐步列出算式 ✓。
- 小数点列对齐：单价列右缘全部 968px、金额列与合计列右缘全部 1150px、应付 1151px
  （列盒 970/1152，误差 ≤2），数值列右对齐 + 等宽字体保证每个小数点同一列 ✓（2× 裁剪
  复核）。
- 第 2 页：4 条 notes 原文排版；4 条 literal_lines 逐字符保真——L1 两处双空格保留
  （“批次：”后与 A/07 间各 2 个空格，单元格模型实测两处间隙恰好 = 2 空格单元 × 14px）、
  L2 显示真实 `< & >`（无任何实体残留）、L3 单反斜杠 `C:\work\cards\v2`、L4 指令样式行
  仅作排版展示 ✓。
- 富文本 “PAID / 已结算”：PAID 绿 #16A34A、斜杠灰 #9CA3AF、中文深色 #111827，同一
  单行 Text 的三个段落共享同一条基线（拉丁字母底行一致；中文比拉丁低 6px = 0.10em，
  与三处对照行 0.077/0.094/0.115em 一致，属 Noto Sans CJK 的字形下垂设计）；斜杠两侧
  空格保留；caption 重申“仍为 CNY 4215.96”，应付金额未被改变 ✓。
- 字体为套件字体查询结果：正文 Noto Sans CJK SC、数字与字面行 Noto Sans Mono CJK SC、
  标题 Noto Serif CJK SC；中/日/拉丁混排无豆腐块（契約レビュー 假名正常）✓。
- 正文 ≥24、脚注 ≥20（最小 20 斜体脚注）、安全边距 48：两页墨迹包围盒均为
  [48, 76, 1151, 1525]，完全在 [48,48]–[1152,1552] 内 ✓。

交付 JSON 核对：invoice-audit.json 含 currency/lines/totals/rounding/literal_lines 全部
必需字段及 identity（schema_version 1、task_id A11、path_base output_dir）；
text-map.json 的 51 条 entries 覆盖每个文字节点（字段路径、原文、页图、实际文字、像素盒、
字体族/字号、发射方式），literal_lines 四条与输入逐字符相等（程序断言通过）；
7 项 checks 全部 passed 且附查看证据。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档版本或访问日期：ai-guide.md、标签参考与字体查询结果均为本套共享缓存
（tmp/run-20261011-01/_suite/docs/，套件启动时真实抓取，本题复用不重复计为新请求）。

AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md
- 实际阅读（缓存）：`<Snapshot type="png">` 根节点与 PNG 输出、请求需浏览器 UA、
  文字/定位标签清单。本题两页 DSL 全部按该结构构造。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| ai-guide.md（缓存） | Snapshot 根节点、PNG 输出、浏览器 UA | 两页 [invoice-page-01.snapshot](invoice-page-01.snapshot) / [invoice-page-02.snapshot](invoice-page-02.snapshot) |
| 标签参考 parser-tags.html（缓存） | Text 的 fontFamily/fontSize/color/textAlign/fontWeight、Positioned 定位、Raw「保留原始空白」 | 全部文字节点；字面行用 `<Raw>` 子节点；PAID 行用 `<Raw color>` 嵌在单行 Text 内 |
| 字体查询缓存 fonts.txt | 可用字体列表：Noto Sans/Serif CJK SC、Noto Sans Mono CJK SC | 正文/标题/数字三套字体与 text-map.json 的 font 字段 |

用到的其他能力：Positioned/Stack/Row 语义的绝对定位表格、Container（底色/分隔线/圆角
深色应付条）、Text 右对齐（textAlign="END"）做小数点列对齐。未使用 Image（A 类纯 DSL）。
探针渲染（7 次）用于确定文字发射策略，详见第 4 节。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：tmp/run-20261011-01/A11/requests.jsonl
迭代记录文件：tmp/run-20261011-01/A11/iterations.jsonl
渲染请求总数：13
成功次数：7
失败次数：6（全部为可诊断的服务端 400：v1 生成器错误×2 + 探针失败×4，逐条读取 .error.json 后修正，无 429、无重试）
重试请求数：0
DSL版本数：3（v1/v2/v3）+ 6 个探针DSL
实际图片查看次数：20（v2 整图×2+裁剪×2、探针×3、v3 整图×2+裁剪×5、最终图整页×2+裁剪×4）
完整视觉迭代数：2（v2→v3、v3→定稿前复核）
未完成视觉迭代数：0
其他接口查询：0（3 条文档/字体缓存复用记录在 requests.jsonl，不计新请求）

| 请求ID / 轮次 / 迭代ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| A11-req-0001/0002 / iter-001 baseline | drafts/invoice-page-01/02.snapshot（v1） | 2026-10-13T12:49:04+08:00，2.247s / 1.403s | 400 / application/json | drafts/*.v1.png.error.json | 无图可看；读错误体：`Attr [fontStyle] value is invalid: Unexpected font style END`（生成器位置参数错位，把 textAlign 的 END 写进了 fontStyle） |
| A11-req-0003/0004 / iter-002 visual | drafts/invoice-page-01/02.snapshot（v2） | 12:49:57 起 4.435s / 12:50:03 起 2.719s | 200 / image/png | drafts/invoice-page-01/02-v2.png | 12:50–12:51 看整图+裁剪：布局/金额全对；缺陷=①SKU 与 L2 实体转义按字面渲染（`A&lt;B&amp;C&gt;D`）②合计区双语标签换行与下一行重叠 ③PAID 斜杠两侧空格被裁成 `PAID/已结算` |
| A11-req-0005–0011 / iter-003 探针 | drafts/probe-entities{,2,3,4,5}、probe-paid.snapshot | 12:52:01–12:56:48，单次 0.854–2.154s | 3×200 / 4×400 | drafts/probe-*.png(.error.json) | 12:54–12:57 看 3 张成功探针图+读 4 个错误体：得出第 4 节的 6 条发射规则 |
| A11-req-0012/0013 / iter-004 visual | drafts/invoice-page-01/02.snapshot（v3） | 13:00:53 起 3.140s / 13:00:56 起 2.622s | 200 / image/png | drafts/invoice-page-01/02-v3.png（即最终图原字节） | 13:01–13:03 看整图+5 张裁剪：三处缺陷全部修复，金额/对齐/边距/基线通过 → 定稿复制到 outputs |
| iter-005/006 测量 | —（本地像素实测，无请求） | 2026-10-13 13:05 首跑 / 2026-10-14 09:30 重跑 | — | — | 首跑 2 项检查因度量方法错误误报（见第 4 节）；修正后 7 项全部 passed，并新开 4 张最终图裁剪+2 张整页复看确认 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| iter-001 / baseline | 两页 v1 全部 400 PARSE_ERROR | 错误体：`Unexpected font style END at position 568`——生成器按位置传参时把 `END` 写进了 fontStyle 属性 | 文本节点属性全部改为关键字发射，textAlign 才是 `END` 的归属 | v2 起渲染成功；该缺陷为本地生成器 bug，非服务问题 | drafts/*.v1.png.error.json |
| iter-002 / visual / v1 | SKU 与字面行 L2 显示 `A&lt;B&amp;C&gt;D`、`A &lt; B &amp; C &gt; D` | 看图（v2 裁剪）：实体转义被按字面画出——渲染器**从不**解码实体 | 转入探针确认后改发射方式 | v3 显示真实 `< & >`，实体零残留 | crops/v2-p1-sku-totals.png、crops/v2-p2-lit-paid.png |
| iter-002 / visual / v1 | 合计区标签换行压到下一行（SUBTOTAL/DISCOUNT/PRE-TAX/TAX/SHIPPING 重叠） | 看图：标签盒宽度不足以容纳“中文 + 英文”单行 | 标签单行不换行（加大盒宽/收排版），数值列维持 END 右对齐 | v3 六行标签全部单行、行距均匀，无重叠 | 同上 |
| iter-002 / visual / v1 | `PAID/已结算` 斜杠两侧空格消失 | 看图 + 后续探针：嵌套 `<Text>` 段落会裁掉自身两侧空格 | 斜杠用 `<Raw color="#9CA3AF"> / </Raw>` 作为同一单行 Text 的中间段落 | v3 空格保留，三段共享一条自然基线 | drafts/probe-paid.png、crops/final-p2-paid.png |
| iter-003 / 探针 | 原始 `<` 写进元素内容 400：`Unknown element tag [B&C]` / `Unexpected character ' ' in TAG_OPEN`；`<Raw>` 直接放 Positioned 下 400「can only be used in the Text」；`<Raw>` 子内容里的 `<` 也按标签解析 400 | 4 个失败探针的 .error.json 错误体 | 含 `<>&` 的字符串一律走 `text="…"` 属性（探针 probe-entities5 证明属性值原样通过）；`<Raw>` 只能作 Text 子节点且其内容同样不能含裸 `<` | v3 全部通过；发射策略写入 invoice-audit.json 的 emission_evidence | drafts/probe-entities{,2,3,4}.png.error.json、probe-entities5.png |
| iter-005 / 测量修正 / v3 | 字面行空格检查误报失败 | 度量方法错误：用墨迹间隙中位数对比——字母侧差各不相同（L4 词隙 17/21px 不等），且取了 `max(g1)=48`（全角冒号后的间隙）而不是 A↔07 的 30px | 改为单元格模型：半宽 14px 由 L4 推得、全宽 28px；逐字符建模后要求空格单元无墨、字形单元有墨、右缘吻合；间隙按「前字右空 + n×14 + 后字左空」分解 | 重跑通过：L1 两处间隙均恰好 2 空格单元（48/30px 与模型逐像素相等），L2–L4 每隙恰好 1 单元 | scripts/measure_a11.py |
| iter-005 / 测量修正 / v3 | PAID 基线检查误报失败 | 度量方法错误：要求拉丁与中文墨迹底行相等，忽略 Noto Sans CJK 汉字字形天然下垂约 0.1em（size 60 实测低 6px） | 与三处中英混排行做归一化对照（delta/字号） | 重跑通过：0.10em 与对照 0.077/0.094/0.115em 同带，判定为同一条基线而非手工位移 | scripts/measure_a11.py |

另记录：6 次 400 全部有明确错误体并已修复，无 429、无网络失败、无重试；实体不解码、
裸 `<` 触发解析、`Raw` 仅限 Text 内、嵌套 Text 裁空格这四条是本题最值得复用的发射规则。

## 5. 任务耗时与请求统计

结构化指标文件：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-13T12:33:00+08:00（约）– 2026-10-14T09:50:00+08:00（两段会话，隔夜暂停） | 含时区时间 | 起始为 A10 结束（12:31:30）后读题，结束为本报告写入 |
| 任务总耗时（活跃墙钟） | 4200 | 秒 | 第 1 段 12:33–13:05（1920s）+ 第 2 段 09:12–09:50（2280s），不含隔夜等待 |
| 首次可用图耗时 | 957 | 秒 | 起始 → 首次成功渲染（12:49:57，v2 第 1 页） |
| 等待用户反馈 | 0 | 秒 | 单次自动执行，无用户反馈轮次 |
| 限流等待、排队等待 | 0 / 未知 | 秒 | 无 429；服务端排队时间不可测，记 null |
| 已记录请求耗时之和 | 26.814 | 秒 | requests.jsonl 13 次渲染之和，不等于任务总耗时 |
| 成功、失败、重试请求 | 7 / 6 / 0 | 次 | requests.jsonl（失败均有错误体并已修复） |
| 实际看图与完整视觉迭代 | 20 / 2 | 次 | iterations.jsonl 及实际查看记录（另有 2 次测量方法修正迭代） |

## 6. 设计选择、经验与未解决事项

关键设计选择：

- 数值列一律 `Noto Sans Mono CJK SC` + textAlign="END"：等宽等数字宽 + 右对齐 ⇒ 每行
  小数点必然同一列；合计区再用同一机制，右缘实测 968/1150/1150 全部一致。
- 金额全链 Decimal 字符串运算，只在「行金额」与「税额」两步按 0.01 量子 ROUND_HALF_UP；
  小计/税前/应付是已到分值的精确和，不再舍入；236.6580→236.66 的半进位见证写入
  rounding.steps。渲染与 audit 共用同一生成器（断言 payable==4215.96），杜绝图文不一致。
- 字面行用 `<Raw>` 子节点而非普通文本：普通嵌套 Text 裁空格，Raw 保留内部空白；
  含 `<>&` 的整串（SKU、L2）走 `text` 属性，绕开解析器与不解码的实体。
- PAID 行保持「一个单行 Text + 三段」：只要不拆成多个 Positioned，基线天然共享，
  也就不可能改变右侧金额区的任何数据。
- 基线核验用「归一化字形下垂 + 对照行」而不是「底行相等」：CJK 与拉丁的底行差是字体
  设计（0.1em 量级），只有跨字号归一化后才可比。

可复用经验：文字保真类任务先用 1–2 个最小探针确定发射规则（属性 vs 子节点 vs Raw），
比直接在成品上试错省请求；空格/对齐的像素核验要用「等宽单元格模型 + 侧差分解」，
不要用墨迹间隙的统计量；字面行与输入的等价性在生成端用逐字符断言，在呈现端用单元格
模型双向夹逼。

未解决事项：无。所有 7 项检查 passed，6 次 400 均已定位修复，最终 PNG 与服务响应字节
一致（md5 校验通过）。

留痕确认：tmp/run-20261011-01/A11/ 保留 drafts/（v1 错误体、v2/v3 PNG、6 个探针 DSL 与
成败图）、crops/（v2/v3 与最终图裁剪）、requests.jsonl（13 渲染 + 3 文档缓存复用）、
iterations.jsonl、scripts/（生成与测量脚本）；失败尝试未删除。总任务根 .gitignore 已按
templates/gitignore-template.txt 合并，排除 __pycache__/ 等运行时缓存，未排除 tmp/、
outputs/ 或任何过程证据。
