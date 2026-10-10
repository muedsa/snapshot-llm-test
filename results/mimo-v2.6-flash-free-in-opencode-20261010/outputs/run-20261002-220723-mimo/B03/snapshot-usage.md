# snapshot-usage.md · B03 的真实文档、DSL 与工具应用记录

- 任务：B03 · 用十件作品探索 DSL 的创意边界
- run_id：`run-20261002-220723-mimo`
- 输出：`outputs/run-20261002-220723-mimo/B03/`
- 临时与留痕：`tmp/run-20261002-220723-mimo/B03/`
- 服务：`POST https://open-snapshot.muedsa.com/snapshot`（UTF-8 纯文本）
- 日志：`requests.jsonl` **78 行** / `iterations.jsonl` **62 行** / `tool-usage.jsonl` **9 行**（全部 JSON 校验通过，0 行坏 JSON）

---

## 1. 交付产物

| 文件 | 说明 |
|---|---|
| `portfolio.json` | 结构化作品清单（10 件，含尺寸来源、能力、完成标准、视觉复核、请求与迭代 ID、终审 11 项检查） |
| `portfolio.md` | 策展逻辑、证据表、十件用途、迭代最深的三件 |
| **`technique-notes.md`** | **本任务指定的额外交付**：13 节实测技术边界与踩坑 |
| `gallery.html` | 本地画廊，10 张缩略图可点开原尺寸；纯本地 lightbox，无远程脚本 |
| `snapshot-usage.md` | 本文件 |
| `task-metrics.json` | 从三份日志反算生成的指标（非手写） |
| `case-01/…/case-10` | 每件含 `final.png` + `final.snapshot` + `case.md` + `.round` |
| `case-04/failures/`、`case-08/failures/`、`case-10/failures/` | 3 条用例 400 的服务原始响应字节 |
| `tmp/…/B03/probes.md` | 探针 p01–p19 的实测表与两处结论更正 |
| `tmp/…/B03/probes/*.png|.snapshot` | 19 个探针的原始响应与配对 DSL |
| `tmp/…/B03/attempts/` | 被取代的轮次（`case-04-r1/r2`、`case-06-r1/r2/r3`、`case-07-r1/r2/r3`、`case-08-r1/r2/r3/r4`、`case-10-r1/r2/r3/r4`、`case-10-r4-2`） |
| `tmp/…/B03/doc-*.{md,html,xml,txt}` | 20 条文档请求的原始响应 + 提取出的 `.txt` |

**10 张 `final.png` 全部为服务返回的原始字节，未做任何后处理**，
逐件与 `requests.jsonl` 的 `bytes` 核对通过，合计 **1,626,680 B**。
每张 PNG 的 IHDR 尺寸 == 同名 `.snapshot` 中第一个 `<Container width height>`。

---

## 2. 文档：20 条真实请求，全部 200

先读文档再做实验，**不预设结论**。20 条 `type=documentation` 请求（`B03-doc-01`…`B03-doc-20`）
全部 200，响应原样落盘：

| # | URL | 落盘 |
|---|---|---|
| 01 | `open-snapshot.muedsa.com/ai-guide.md` | `doc-ai-guide.md` |
| 02 | `snapshot.muedsa.com/` | `doc-site-root.html` |
| 03 / 07 | `sitemap-index.xml` / `sitemap-0.xml` | 同名 `.xml` |
| 04 / 05 | `guides/rendering/` `guides/testing/` | `.html` + `.txt` |
| 06 | `reference/source-index/` | `.html` + `.txt` |
| 08–14 | `widgets/painting/{backdrop-filter,clip-path,image-filtered,color-filtered,decorated-box}`、`widgets/text/rich-text`、`widgets/layout/transform` | 各 `.html` + `.txt` |
| 15 / 16 | `guides/painting/` `guides/media-text/` | `.html` + `.txt` |
| 17 / 18 / 19 | `reference/{parser-tags,enums,faq}` | `.html` + `.txt`（`parser-tags` 147,408 B，最大） |
| 20 | `widgets/text/widget-span/` | `.html` + `.txt` |

**文档给出的能力清单被逐条拿去做实验**（而不是抄进作品里就算数），
对应关系如下：

| 文档条目 | 落到哪个探针 / 作品 |
|---|---|
| `Text` 描边字 / 多重 `textShadow` | p01 → case-01 |
| `BackdropFilter` | p02 → **失败** → p14–p18 → case-02 |
| `ColorFiltered` + `blendMode` | p03 → case-03 |
| `ImageFiltered` | p04 → case-04 |
| `WidgetSpan` | p05 → case-05 |
| `Stack` / `clipBehavior` | p06 → **结论被推翻** → p19 → case-08 |
| `gradientType/Rotation/Stops/TileMode`、对齐常量 | p07 / p11 / p12 / p13-align01..05 → case-07 |
| `fontFeatures` | p08 → case-09 |
| `SizedOverflowBox` + `ClipRect` | p09 → **初读有误** → case-06 |
| `Transform matrix` | p10 → case-10 |
| `boxShadow` 层级名 | `reference/parser-tags` → case-08 r1 的 400 修复 |
| `Container` 单子节点 | p19 首次 400 的服务端报错 → 写入 technique-notes §9 |

---

## 3. 服务使用：58 条渲染 + 20 条文档 = 78 条请求

| 类别 | 条数 | 200 | 400 |
|---|---|---|---|
| 用例渲染（`case_id` 非空） | 33 | 30 | 3 |
| 能力探针（`case_id = null`，属 shared） | 25 | 18 | 7 |
| 文档抓取 | 20 | 20 | 0 |
| **合计** | **78** | **68** | **10** |

- **10 条 400 全部是 `PARSE_ERROR`**，服务端原文保留在
  `case-04/failures/`、`case-08/failures/`、`case-10/failures/`、`probes/failures/`：
  - 探针 6 条：`p11-linear-tiling`、`p12-short-tile`、`p13-align02/03/04/05`
    （后四条是五连测里的四种非法对齐写法，**属实验设计内的预期失败**，不重试）
  - 探针 1 条：`p19-stack-clip`（根 `<Container>` 挂了多个 `<Positioned>`）
  - 用例 3 条：`case-04-r1`（`Positioned` 父数据类型）、`case-08-r1`（`boxShadow` 纯数字）、
    `case-10-r5`（`@()` 数组折叠成 `color="#"`）
- **6 处 400 修正 DSL 后沿用同一请求 ID 再次请求**（一行 400 + 一行 200，
  两条原始记录保留未合并——见 §7 遗留问题）。
- **限流**：全程无 429、无 `Retry-After`，`ratelimit_remaining` 最低 110 → 限流等待 = 0（不是未知）。
- **请求耗时合计 216.057 s**（78 行全部含 `duration_ms`，最短 767.3 ms、最长 9119.4 ms）；
  请求串行无重叠，但**不等于总墙钟**（任务墙钟 87,610.396 s，含跨日闲置）。
- **token / 图像使用量 / 费用**：平台未提供，按约定一律 `null`，不用字数或额度反推。

---

## 4. 19 个能力探针：结论优先于印象

探针属 shared 准备（`case_id = null`），25 条渲染请求、23 个探针 ID。
每个探针**只验证一件事**，且结论一律用像素或字节判定：

| 探针 | 验证 | 结论 |
|---|---|---|
| p01 | `STROKE` / 多重 `textShadow` / `letterSpacing` | ✅ 成立 |
| p02 | `BackdropFilter` + `ClipRRect` | ❌ **初读有误** → 由 p14–p18 更正 |
| p03 | `ColorFiltered MULTIPLY` | ⚠️ 只与**子节点**混合，与直觉相反 |
| p04 | `ImageFiltered sigmaX≠sigmaY` | ✅ 各向异性成立 |
| p05 | `WidgetSpan` 行内徽章 | ✅ 基线自然对齐 |
| p06 | `Stack` 默认裁阴影 | ❌ **初读有误** → 由 p19 推翻 |
| p07 | 渐变平铺与旋转 | ⚠️ 部分成立（见 p11/p12） |
| p08 | `fontFeatures=+tnum` | ✅ 294 px → 325 px |
| p09 | `SizedOverflowBox` 出血 | ⚠️ **初读有误**：实为换行 |
| p10 | `Transform` 16 元矩阵 | ✅ 轴测网格成立 |
| p11 / p12 | REPEAT 分片长度 | ✅ 分片 = 起止点距离 |
| p13-align01..05 | 5 种自定义对齐写法 | ✅ 只有 `(-1,0)` 可用；4 条 400 是预期失败 |
| p14–p18 | BackdropFilter 四变量对照 | ✅ 定出两条硬规则 |
| p19 | `Stack` 裁子节点 vs 裁阴影，4×2 | ✅ 裁子节点 / ❌ **阴影完全不裁** |

**两条被推翻的结论 + 一条被字节证伪的假设**已写回 `probes.md`
（§2、§6、§9 三节重写），并各记一条 `evidence-correction` 迭代。
→ **读图印象与像素量测冲突时一律以像素量测为准。**

---

## 5. 工具应用（`tool-usage.jsonl` 9 行）

| ID | 工具 | 分类 | 关键产出 |
|---|---|---|---|
| tu-01 | `render-b03.ps1`（复用 `_suite/render.ps1`） | 共享准备 | 每条渲染请求都带 `case_id` / `dsl_chars` |
| tu-02 | `docfetch.ps1`（复用 B01 版本） | 文档查阅 | 20 条文档请求全部 200，落盘为 `doc-*` |
| tu-03 | System.Drawing 像素采样 | 量测/放大 | `+tnum` 字宽、`ColorFiltered` 混合语义、渐变 stops/rotation/REPEAT |
| tu-04 | 读图工具内容哈希缓存缺陷 | 看图 | 批量化读图串图 → 改「每次只读一张 + 重新编码新哈希」后恢复；`browser.preview` 同样不可用 |
| tu-05 | `gen-probes.ps1` / `gen-probe11` / `gen-probe13` | 生成程序 | 13 份探针 DSL，逐份真实渲染 |
| tu-06 | `gen-probe14..18.ps1` | 生成程序 | 把毛玻璃失效拆成结构/sigma/裁剪/顺序四变量，5 次请求全 200 |
| tu-07 | System.Drawing 高斯模型比对 | 量测/放大 | σ=25 理论值逐点验算（误差 ≤1 RGB），反推出「后续 BF 只能读到前一个之后的内容」 |
| tu-08 | p19 生成与渲染 | 生成程序 | 4×2 对照定论：裁子节点 ✅ / 裁阴影 ❌ |
| tu-09 | System.Drawing 逐像素裁剪与出血复核 | 量测/放大 | p06 逐点相同、p09 仅 2 字形、case-06 墨迹 891→1079、case-08 底边 1223/1293 |

**跨题复用**：`docfetch.ps1` 与 `_suite/render.ps1` 直接复用前序任务已验证的版本；
`lib-b03.ps1` 复用 B01/B02 的排版基础（`TX`/`TXW`/`Page`/`Write-Dsl`）并新增本题特有的
`Bleed`/`ClipAt`/`IBlur`/`Glass`/`Frost`/`IsoM`/`Chip`。
复用不重复计入请求：**文档 20 条、探针 25 条为本题实际新发出**，
`_suite` 共享渲染 0 条。

---

## 6. 视觉迭代过程（`iterations.jsonl` 62 行）

| 类型 | 行数 | 说明 |
|---|---|---|
| `baseline` | 10 | 每件首版，全部真实渲染并读图 |
| `visual` | 21 | 19 次真实改动 + case-09 的「无改版直接通过」判定 + case-08/case-10 的 round 5 |
| `capability-probe` | 24 | 23 个探针 ID（p13 五个子项各一行）+ p19 |
| `syntax-fix` | 4 | p19、case-04、case-08、case-10 的 400 修复 |
| `evidence-correction` | 3 | p02 更正、p06 更正、p09 更正 |
| **合计** | **62** | `viewed=true` **58 行**；读图调用合计 **70 次**（58 + 终审/写文档时的 12 次复看） |

**每件作品都真实打开过最终图**（`case-09` 为「首版即通过」，另记一条明确的
「无改版」判定，不虚构一次不存在的渲染）。`case-08` 与 `case-10` 在撰写交付文档期间
各新增了一次 round 5，因此各复看了 2 次。

三件迭代最深的（也是信息量最大的）：

- **case-06（4 轮）**：r2 读图"觉得"出血了 → 像素量到 `x=63..891`（**没有**）；
  r3 加 `maxLines="1"` → PNG **字节与 r2 完全相同**（`516CCB8B…`），
  同时证伪「`maxLines` 有效」与「框内可换行溢出」两条假设；
  r4 框宽 1032→2000 后墨迹 `x=63..1079`（页宽 1080）= 真出血。
- **case-08（5 轮 + 1 次 400）**：r3 显式加 `HARD_EDGE` 后逐像素采样左右两半**完全相同**
  → 原方案被推翻 → 探针 p19 定论 → r4 整段改版（左 1223 / 右 1293，差 70px）；
  r5 修掉指向不存在任务的 `B08` 交叉引用。
- **case-10（5 轮 + 1 次 400）**：`$U`/`$u` 大小写冲突、矩阵重复平移、体块未按深度排序
  （定点取色证明塔身曾被树色覆盖 `#7FB07A` → 修正后 `#C98A4A`）、
  图例两次不完整（r4 缺 5 馆、r5 缺 5 树）、r5 的 `@()` 数组折叠 400。

---

## 7. 跨题经验与踩坑

1. **`BackdropFilter` 只有一处可用，且 `Clip` 必须直接包住它** —— 本套最贵的一条，
   直接决定了 case-02 从「四块玻璃」重做成「一块玻璃」。
2. **`SizedOverflowBox` 不会替你横向溢出**；`maxLines` 被渲染器忽略。
   要出血就把裁切框放宽到超过字宽，让页边当刀。
3. **`Stack` 裁子节点、从不裁 `boxShadow`** —— 想控制阴影范围只能靠版面边界。
4. **`ColorFiltered` 只与子节点混合** —— 不能给"画好的背景"整体叠色。
5. **PowerShell 侧的三个坑**：变量名大小写冲突（`$U`/`$u`）、
   `transform matrix` 与 `Positioned` 重复平移、`@(@('a','b'))` 被 `@()` 折叠
   导致 `$items[0][0]` 取到首字符 `#`。
6. **PS 5.1 写完 `.ps1` 必须重新加 BOM**（编辑工具会剥掉 BOM）；
   逐行追加用 `[IO.File]::AppendAllText`；函数名不要取 `H`（撞 `Get-History` 别名）。
7. **读图工具按内容哈希缓存**，批量化读取会串图 → 每次只读一张，
   必要时对 PNG 重新编码生成新哈希副本；**终审一律读 `outputs/.../<case>/final.png` 原件**。
8. **`browser.preview` 不可用**（`browser.disconnected: No desktop browser is connected`）
   → 看图走 `read` + System.Drawing 双轨。
9. **交付前要查交叉引用**：case-08 页脚的 `B08` 在本套不存在（只有 A01–A24、B01–B06），
   已改为「本页为虚构规范演示」；全库 grep 确认再无同类悬空引用。
10. **图例/说明必须能解释图上每一种形体** —— case-10 因此补了两轮（5 馆、5 树）。

---

## 8. 终审结论

- 10 件主作品齐全，`final.png` + `final.snapshot` + `case.md` + `.round` 四件套完整；
- 10 张 PNG 字节 == 对应成功响应的 `bytes`，IHDR 尺寸 == DSL 首个 `Container` 宽高；
- 10 种画幅互不重复，观看距离 0.25–10 m，10 种主导 DSL 能力互不重复；
- 10 件全部有真实受众、使用场景与要完成的判断；
- 10 件全部实际打开最终图并留有 `viewed` 证据；
- 全库无指向不存在产物的交叉引用；
- 图例/说明与画面一致（case-10 三行图例、case-08 实测脚注）；
- 画面内均可见 `DEMO . 演示数据`，全部内容为虚构演示数据。

**遗留（如实记录，非阻塞）**：

1. `requests.jsonl` 中 `case-04-r1` / `case-08-r1` / `case-10-r5` 三处重试沿用同一请求 ID
   （一次 400 + 一次 200），两条原始记录均保留未合并 —— 日志编号缺陷，非渲染缺陷；
2. `attempts/` 中 `case-10-r4` 与 `case-10-r4-2` 是同一次 r4 内容的重复归档
   （首次归档后渲染 400，二次运行再次归档），按「不清理尝试」原则保留；
3. 浏览器通道不可用，`browser.preview` 无法参与看图 —— 属环境限制，已记录为失败的工具尝试；
4. token / 图像使用量 / 费用平台未提供，一律 `null`。
