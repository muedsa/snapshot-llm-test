# A21 · 叠光 Layerlight 分期改版 · 任务根累计报告（三轮全部完成）

**执行模式：预置三轮连续自动执行。** `tasks/A21-staged-launch-change/TASK.md` 规定了 `rounds/round-01.md`
→ `rounds/round-02.md` → `rounds/round-03.md` 三份前置需求文件，全部在执行前就已存在于根目录，
本任务按顺序读取并连续完成，**不等待外部反馈、不编造未来意见、不覆盖前轮**。
这是连续执行模式，不声称隐藏反馈盲测；每轮报告开头都注明了这一点。

| | |
|---|---|
| 状态 | **completed**（3/3 轮） |
| OUTPUT_DIR | `outputs/run-20261002-220723-mimo/A21/` |
| TEMP_DIR | `tmp/run-20261002-220723-mimo/A21/` |
| 起止 | `2026-10-05T10:28:13+08:00` → `2026-10-05T11:42:07+08:00` |
| 首个可用图 | `2026-10-05T10:48:36.699+08:00`（耗时 1223699 ms） |
| 总墙钟 | `01:13:54.814`（4434814 ms，`task-metrics.json` 为准） |
| 请求 | 8 次（渲染 6 + 文档 2），全部 200，**失败 0、重试 0、429 0** |
| 请求耗时之和 | 16692.6 ms（渲染 15846.2 + 文档 846.4）—— **不等于** 总墙钟 |
| 渲染返回字节 | 587614 B |
| 看图 | **12 次**（每轮 4 次：两图整图 + 两个标记 3× 放大） |
| 迭代行 | **6 行**（baseline 1 / syntax-fix 3 / requirement-change 2），完整视觉迭代 **0** |
| 最终交付 PNG | **6 张**（每轮 1 竖 + 1 横），全部为原始服务响应字节 |
| 产物总数 | **27 个**（round-01 8 + round-02 8 + round-03 11），27/27 齐全 |
| GDI+ 探针 | 52/52 命中声明背景，12/12 条保留带为空 |

---

## 1. 三轮目录与产物

```
outputs/run-20261002-220723-mimo/A21/
├── snapshot-usage.md          ← 本文件（累计）
├── task-metrics.json          ← 任务根累计指标
├── round-01/   8 个文件
├── round-02/   8 个文件
└── round-03/  11 个文件
```

| 轮 | 产物 | PNG | SHA-256 前 32 位 | 报告 | 指标 |
|---|---|---|---|---|---|
| round-01 | 8 | `launch-portrait.png` 1080×1350, 76587 B | `A41B1C2954A9C88D6B9102327E000AF4` | ✅ | ✅ |
| | | `launch-wide.png` 1440×810, 67808 B | `BEAEFEB2D03C3AA0D69A6D2F75BAB68A` | | |
| round-02 | 8 | `launch-portrait.png` 1080×1350, 111670 B | `F013863FB5E50783164AC44686249378` | ✅ | ✅ |
| | | `launch-wide.png` 1440×810, 102365 B | `A9B8F6D1E035323383DADDD9BAEAFAEC` | | |
| round-03 | 11 | `launch-portrait.png` 1080×1350, 120058 B | `7F9497E8B17C04F9F780C41426C94ACD` | ✅ | ✅ |
| | | `launch-wide.png` 1440×810, 109126 B | `9C626F24FB85198064D3DAFC75DB1FBF` | | |

**每张 PNG 都与同名 `.snapshot` 一一配对**：PNG 由服务响应字节按字节复制，SHA-256 与临时目录里的
响应文件逐一相同，尺寸由 IHDR 实读校验，字节数与 `requests.jsonl` 记录的响应长度对齐；
`.snapshot` 根是 `<Snapshot type="png"…>` 且 **0 个 `<Image>`**（无整图外链、无整体嵌入）。
前两轮的四张 PNG 哈希在后两轮归档时反复硬校验，**从未被覆盖**。

---

## 2. 需求三轮演进与结果

### round-01（基础双版本）
竖 1080×1350 + 横 1440×810；必含文案「让复杂信息变得清晰」「2026.11.07 19:30」「ONLINE LAUNCH」
「讲者：林川 / 苏言」「layerlight.example.org」；标题以外文字 ≥24；**单一主色** `#5B4FE8` + 同一套字阶；
品牌图形 3–6 构件；两图各自独立构图、不整体嵌入；真实留白带、无占位文字。
→ 8 个产物；探针 14/14；保留带 4/4 空；最小对比度 5.63:1 / 5.52:1。

### round-02（长标题 + 赞助方）
标题换成 27 字长句「当所有信息都想成为标题：让复杂信息变得清晰的结构化方法」（≤3 行、≥48）；
新增赞助方「Northstar Research / 云构工具」与「免费参加 · 无需报名」；
其余文案、主色与 3–6 构件品牌图形不变（允许移动/缩放装饰）；两尺寸不变；**不得压窄变形**。
→ 8 个产物；探针 18/18；保留带 4/4 空；长标题竖 56/2 行、横 52/2 行；报告含「长标题与新信息如何避免碰撞」专节。

### round-03（浅色主题 + 实测对比度）
浅色主题；**所有普通文字与实际合成背景 ≥4.5:1**；保留第二轮全部文案与品牌图形；
网址正上方新增英文 `Clarity through structure`（≥24）；两尺寸不变；长标题仍 ≤3 行 ≥48；赞助方不得消失；
**不能只改两种颜色忽略实际叠层**；两图附 `contrast-audit.json`，每图 ≥6 处正文对比度。
→ 11 个产物；每图 **10 处**（≥6 要求）全部达标，**最低 5.63:1**；探针 20/20；保留带 4/4 空；`problems = 0`。

---

## 3. 三轮之间"没变的"与"变的"

**三轮完全一致（回归基准）**
* 尺寸 **1080×1350 / 1440×810**，IHDR 实读。
* 主色 **`#5B4FE8`**（配 `#8B85FF` 浅靛、`#FFB020` 琥珀），一轮都未改。
* 品牌图形 **4 构件叠光标记**：`C1` 88×88 r24 主色 @(0,44)、`C2` 88×88 r24 浅靛 @(44,22)、
  `C3` 88×88 r24 琥珀 @(88,0)、`C4` d30 琥珀核心圆 @(51,62)。竖版 scale 1.0、横版 scale 0.8，
  **相对几何/颜色/叠压顺序三轮逐项一致**，只在 round-02 上移 20 px 装饰位置。
* 11 条必含文案逐字不变（长标题与英语短句按轮次要求新增后保留）。
* 0 个 `<Image>`、0 个 `transform`、无压窄/拉伸/倾斜。
* 每轮两条真实保留带可用、且真实为空（竖 120/170 px、横 100/100 px）。

**每轮变化（都在要求内）**
| 轮 | 变的 | 没变的 |
|---|---|---|
| r01 | —（首版） | 全部 |
| r02 | 标题 88/72 → **56/52** 且 ≤3 行；新增赞助方 + 免费胶囊；标记上移 20 px | 主色、构件、尺寸、其余文案 |
| r03 | **主题深→浅**；新增 **bandA / bandB 两条真半透明背景光带**；网址上方新增英文短句 | 主色、构件、尺寸、全部文案、长标题行数字号 |

**视觉回归核对方式**：把三轮 layout-map 逐块比对 —— r02 与 r03 的 title/deck/date/speakers/sponsor/free
坐标与字号完全相同，差异只有主题色、两条新光带、新增 english 块三处；再用 GDI+ 复扫 12 条保留带与
52 个 probe 点，确认真实渲染与声明一致。

---

## 4. 浅色主题与真实叠层（round-03 的核心）

光带是**真半透明**，不是换个实色蒙混：

| 光带 | DSL 颜色（`#RRGGBBAA`） | 位置 | 实测合成色 |
|---|---|---|---|
| bandA 主色 12.16% | `#5B4FE81F` | 竖 (64,356,944,310)、横 (72,296,808,300)，垫在长标题+副标题下 | 页面 `#E1E1F8` |
| bandB 琥珀 16.08% | `#FFB02029` | 竖 (64,1030,944,150)、横 (928,536,392,140)，垫在英文短句+网址下 | 页面 `#F5E9D7`；**白面板 `#FFF2DB`** |

**同一条 bandB 在两种底层上得到两种不同实测色** —— 这是"叠层真的参与 source-over 计算"的直接证据。
`contrast-audit.json` 每条 entry 同时记录 `background_layers_bottom_up`、`expected_background_composited`
（参考合成值）与 `sampled_background_rgb`（真实渲染像素），三者对应。

**对比度一律按实测像素算**：`probe-a21.ps1` 用 GDI+ `GetPixel` 取每个正文 probe 的最终色，
按 WCAG 2.1 相对亮度公式求比值 —— 即 round-03.md 允许的"最终实际背景"。
参考合成值只用来反查叠层声明是否正确，**不参与对比度结论**。

---

## 5. 实际看图记录（12 次，全部为真实打开图片）

| 轮 | # | 看的是什么 | 结论 |
|---|---|---|---|
| 1 | 1 | `launch-portrait-r01.png` 整图 | 深色主题、标记与文案就位、保留带空 |
| 1 | 2 | `launch-wide-r01.png` 整图 | 双栏、标记、日期讲者网址在位 |
| 1 | 3 | `v1-mark-portrait-01.png` 3× `src[72,124,340,174]` | 4 构件、叠压顺序、色值正确 |
| 1 | 4 | `v1-mark-wide-01.png` 3× `src[82,96,460,140]` | scale 0.8 与竖版同形 |
| 2 | 1 | `launch-portrait-r02.png` 整图 | 长标题 2 行、赞助方与胶囊新增、无碰撞 |
| 2 | 2 | `launch-wide-r02.png` 整图 | 左标题右面板分栏、赞助方保留 |
| 2 | 3 | `v2-mark-portrait-01.png` 3× | 形态同 round-01，位置上移 20 px |
| 2 | 4 | `v2-mark-wide-01.png` 3× | 同上 |
| 3 | 1 | `launch-portrait-r03.png` 整图 | 浅色生效、两条光带、英文短句在网址正上方 |
| 3 | 2 | `launch-wide-r03.png` 整图 | 赞助方未消失、两栏不相碰 |
| 3 | 3 | `v3-mark-portrait-01.png` 3× `src[72,104,340,174]` | 同一套构件，仅底色深→浅 |
| 3 | 4 | `v3-mark-wide-01.png` 3× `src[82,86,460,140]` | 同上 |

> 像素扫描（GDI+ probe / contrast-audit）只作佐证，按约定**不计入**看图次数。
> 看图的精确时钟未被采集，`iterations.jsonl` 用 `viewed_at_basis` 记录可证明的时间窗，不编造时刻。

---

## 6. 实际踩坑与修复（跨轮经验）

| # | 轮 | 问题 | 根因 | 修复 | 留痕 |
|---|---|---|---|---|---|
| 1 | r01 | `File::GetLength` 调用写法不被接受 | PowerShell 5.1 要 `[IO.File]::GetLength` 这样的**静态**调用；`.Length` 是实例属性，两者不能混 | 改用 `[IO.File]::GetLength(...)` | `A21r1-it02` syntax-fix |
| 2 | r01 | 脚本抛 `Missing closing ')'` | **PowerShell 5.1 会把弯引号 `“ ”`（U+201C/U+201D）当字符串定界符**，双引号字符串里一出现就提前闭合；另有一个函数缺了收尾 `}` | 弯引号一律改 `「」`，补 `}`；`ParseFile` 复查 0 错 | `A21r1-it03` syntax-fix |
| 3 | r03 | `-Round 3` 抛 `…[System.Object[]] does not contain a method named 'op_Multiply'` | 最小复现 `1 * 2, 3`、`@(1 * 2, 3)` 全失败 —— **PowerShell 的逗号优先级高于乘法**，`@($a*$b + …, $c*$d + …)` 被解析成 `$a * (…, …) * …`。`Composite` 的三元数组只在背景有**两层**时才走到，r01/r02 全是单层所以从未触发 | `Composite` 三个分量各自加括号 `@( (…), (…), (…) )`，源码留注释 | `A21r3-it01` syntax-fix |
| 4 | r03 | 光带层描述少了冒号 | `$BAND_A = "$PRIMARY$BAND_A_ALPHA"` 拼出 `5B4FE81F`；`Composite` 期望 `RRGGBB:AAhex`，按 8 位裸 hex 会把后 6 位读成 RGB 并把光带当**完全不透明**，参考合成色会算成纯 `#5B4FE8` | 新增 `$BAND_A_SPEC = "5B4FE8:1F"` / `$BAND_B_SPEC = "FFB020:29"` 专供层描述，DSL 仍用 8 位 `#RRGGBBAA` | `A21r3-it01` syntax-fix |
| 5 | r03 | 修第 3 条时自己写出 `((` 形式 | 多重开括号未闭合 | 改回每项一对括号，`ParseFile` 0 错 | `A21r3-it03` 前置 |
| 6 | r03 | contrast 扫描报 6 个问题，**其中 1 个是真错** | bandA 在 DSL 里画在 title 之前、title 的 probe `(82,470)` 明明落在光带内，layout-map 却把 title 的 `background_layers_bottom_up` 记成只有 `page` | round-03 时竖/横 title 改为 `@($PAGE, $BAND_A_SPEC)`、`background_name = bandA`、`probe_min_x = 64/72` | `A21r3-it02` |
| 6 | r03 | 另外 5 个是误报 | 参考合成 `#E1E1F9` vs 实测 `#E1E1F8`、`#F6EAD8` vs `#F5E9D7`，每通道差 1；原断言是严格全等，把服务端 8-bit source-over 的取整误判成"叠层被忽略" | 断言改为 `max_channel_delta <= 1`，每条 entry 同记 `background_matches_composition_exact` 与 `max_channel_delta`，容差理由写进 JSON。**缺层/错层在这套配色下至少差 10**；对比度仍按实测像素算，结论不受容差影响 | `A21r3-it02` |
| 7 | 工具 | `close-a21-round03.ps1` 第一次跑报 `Cannot find drive @{id=A21r3-p01…}` | **PowerShell 变量大小写不敏感**：循环变量 `$r` 覆盖了目录变量 `$R` | 循环变量改名 `$resp` / `$rn`，复查全文件无 `$r` | 直接修正，0 次渲染影响 |

**最重要的两条经验（可跨题复用）**
1. **PowerShell 5.1 的弯引号 `“ ”` 会当定界符**；以及**逗号比乘法优先级高**，`@()` 里的多项算术必须逐项加括号。
   后者只在多层背景时才暴露 —— 单层分支掩盖了它两轮。
2. **对比度必须拿最终真实像素算**，声明色只能用来反查叠层对不对；断言要允许 8-bit 取整的 ±1，
   否则会把取整噪声误报成"叠层被忽略"，而真错（title 漏声明 bandA）反而淹没在噪音里。

---

## 7. 逐轮报告与指标入口

| 轮 | 报告 | 指标 |
|---|---|---|
| round-01 | `round-01/snapshot-usage.md` | `round-01/task-metrics.json` |
| round-02 | `round-02/snapshot-usage.md` | `round-02/task-metrics.json` |
| round-03 | `round-03/snapshot-usage.md` | `round-03/task-metrics.json` |
| 累计 | 本文件 | `task-metrics.json`（本目录） |

过程日志（任务级共享、只追加）：`tmp/run-20261002-220723-mimo/A21/requests.jsonl`（8 行）、
`iterations.jsonl`（6 行）；A 类任务不写 `tool-usage.jsonl`。
`design-tokens.json` / `content-map.json` 每轮各一份，共 6 份。
round-03 另有 `contrast-audit.json` + `contrast-audit-portrait.json` + `contrast-audit-wide.json`。

---

## 8. 未解决事项

* **无视觉或需求层面的未解决项**：三轮均 `problems = 0`，52/52 探针命中，12/12 保留带为空。
* 看图精确时钟未采集，用 `viewed_at_basis` 记录时间窗，不编造单次时刻。
* token / 图像输入 / 费用：平台未提供本任务任何计量指标，`task-metrics.json` 全部记 `null` 并注明原因。
* `requests.jsonl` 里 `A21-doc-000` 是经取文工具读取服务指南的记录，无起止时刻与字节数，记 `null`；
  `A21-doc-001` 是同 URL 的带计时 GET（846.4 ms / 3718 B），两者去重后仍是同一篇文档。
* 参考合成色与实测像素存在**每通道 ≤1** 的取整差，已在 `contrast-audit.json` 记录
  `max_channel_delta` 与容差理由；对比度结论只依赖实测像素，不受该容差影响。
* 竖版长标题断行点落在「让复 / 杂信息」中间（CJK 允许任意位置断行），三轮一致；
  不影响行数与字号要求，也未使用任何变形压窄。如需按词断句需引入分词信息，
  三份 round.md 都只约束行数与字号，故不处理。
