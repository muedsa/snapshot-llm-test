# A14 · 八组文案压力测试与批量生成 — 使用与自检报告

- **任务**：给 `tasks/A14-content-stress-batch/inputs/cards.json` 的 8 条讲座各生成一张 1200×630 宣传卡，`card-K01` … `card-K08`
- **状态**：完成（8/8 张最终 PNG 均为服务真实响应的原始字节，均已逐张用图像工具打开查看；68 项自动化检查全部通过）
- **服务**：`https://open-snapshot.muedsa.com`（`run-config.json` 的 `service_base_url`），只用 `POST /snapshot`
- **输出目录**：`outputs/20261004-182918/A14/`
- **临时目录**：`tmp/20261004-182918/A14/`（脚本、探针、逐次 DSL 副本、请求/迭代日志、失败响应、裁切放大图、接触表）
- **run_id**：`20261004-182918`（沿用全套统一 run_id，未另建）

---

## 1. 交付文件清单

| 文件 | 尺寸 | 说明 |
|---|---|---|
| `card-K01.png` + `card-K01.snapshot` | 1200×630 | 开始 / 林川 / 09:00 / 开放 |
| `card-K02.png` + `card-K02.snapshot` | 1200×630 | 读文档，也要读懂布局约束 / 周禾 / 许宁 / 09:40 / 满额 |
| `card-K03.png` + `card-K03.snapshot` | 1200×630 | 当所有信息都想成为标题… / 顾行 / 10:20 / 候补 |
| `card-K04.png` + `card-K04.snapshot` | 1200×630 | A \< B & C > D：不要把文本当成标签 / 苏言 / 11:00 / 开放 |
| `card-K05.png` + `card-K05.snapshot` | 1200×630 | Color, Alpha & Contrast / 从颜色到可读性 / 孟澄 / 13:00 / 开放 |
| `card-K06.png` + `card-K06.snapshot` | 1200×630 | 两张看似相同的图片…？ / 许宁 / 13:40 / **取消** |
| `card-K07.png` + `card-K07.snapshot` | 1200×630 | 把一次失败变成可复现记录——… / Northstar Research · 林川 / 14:20 / 候补 |
| `card-K08.png` + `card-K08.snapshot` | 1200×630 | 从"已经请求成功"到"已经完成作品"：… / 周禾 / 15:00 / 开放 |
| `batch-audit.json` | — | 逐卡内容、标题字号/行数/位置、状态三通道编码、像素实测结果、逐次看图记录、68 项检查 |
| `snapshot-usage.md` | — | 本文件 |
| `task-metrics.json` | — | 由 `finalize.py` 从 `requests.jsonl` / `iterations.jsonl` 生成 |

辅助产物（临时目录，非交付）：`probe/probe-widths.png`（字宽标定探针）、`probe/measured.json`、`probe/diag-A..E.png` 与 `probe/grad-F..I.png`（9 张诊断对照图）、`drafts/v01..v16-Kxx.snapshot`（逐次 DSL 副本）、`crops/*.png`（徽标放大核对 4 张）、`contact-sheet/contact-sheet-all-8.png`（一致性接触表）、`responses/resp-*.txt`（12 条失败响应原文）、`docs/*`（抓取的文档）、`hashes-viewed.json` / `hashes-delivered.json`（被查看版本与交付版本的 SHA-256 比对）、`iterations-superseded-duplicate-wrapup-run.jsonl`（重复 wrapup 运行的归档）。

---

## 2. 实际使用的服务文档与字体

全部为**本题真实抓取**，原始响应体保存在 `tmp/20261004-182918/A14/docs/`，请求记在 `requests.jsonl`（`request_type=document` / `font_list`）。

| URL | 状态 | 用途 |
|---|---|---|
| `https://open-snapshot.muedsa.com/ai-guide.md` | 200 | 确认请求体是 UTF-8 纯文本 DSL（非 JSON）、`POST /snapshot` 返回图片字节、8 位色按 `#RRGGBBAA`、错误码语义 |
| `https://open-snapshot.muedsa.com/fonts` | 200 | 实际可用字体族清单（27 个），保存为 `fonts-list.txt` |
| `https://snapshot.muedsa.com/` | 200 | 文档导航结构 |
| `https://snapshot.muedsa.com/reference/parser-tags/` | 200 | `Container`/`Text`/`Transform`/`Stack`/`Positioned` 的属性表、EdgeInsets、颜色格式 |
| `https://snapshot.muedsa.com/guides/media-text/` | 200 | `Text`/`TextStyle`/`maxLines`/`overflow`/`softWrap` 语义 |
| `https://snapshot.muedsa.com/guides/layout/` | 200 | 布局与约束 |
| `https://snapshot.muedsa.com/guides/painting/` | 200 | 渐变 / 阴影 / 裁切 |
| `https://snapshot.muedsa.com/guides/parser/` | 200 | 类 DOM 解析器行为 |
| `https://snapshot.muedsa.com/reference/enums/` | 200 | 枚举速查：确认 `TextOverflow` 含 `VISIBLE`、`FontStyle` 含 `BOLD`、`BorderStyle` 只有 `NONE`/`SOLID` |
| `https://snapshot.muedsa.com/openapi.yaml` | **404** | 指南里提到的同源 openapi 文件在该站点不存在，如实记录 |
| `https://snapshot.muedsa.com/widgets/text/` | **403** | 猜测路径被站点拒绝，改用上面的 `reference/parser-tags` + `guides/media-text` 获取 `Text` 属性 |

**实际用到的字体**（全部来自本次 `GET /fonts` 的返回，未臆造）：
`Inter`（品牌名、SPEAKER/TIME 标签）、`Inter,Noto Sans CJK SC`（标题、讲者、状态词、品牌中文回退）、`DejaVu Sans Mono`（日期 `2026.11.07`、时间 `09:00`、序号 `01 / 08`）。

**实际用到的标签**：`Snapshot` / `Container` / `Stack` / `Positioned` / `Text` / `Transform`。
**实际用到的属性**：`type`、`background`、`width`、`height`、`fit="EXPAND"`、`left`、`top`、`alignment="CENTER"`、`color`、`borderRadius`、`border="N SOLID #RRGGBBAA"`、`gradientType="LINEAR|RADIAL"`、`gradientColors`、`fontSize`、`fontFamily`、`fontStyle="BOLD"`、`color`、`textAlign="END"`、`letterSpacing`、`softWrap="false"`、`overflow="VISIBLE"`、`matrix`（16 个列主序 Float）。

**未使用**：`<Image>`、`dataUri`、任何外部图片、任何外部绘图库。主体、字样、图标、几何全部由 DSL 构造。

---

## 3. 共享设计令牌（一套令牌驱动 8 张卡）

全部集中在 `tmp/20261004-182918/A14/build_cards.py` 的 `TOKENS` 字典里，8 张卡共用，没有任何按 id 硬改的分支。

### 3.1 画布与栅格
```
画布            1200 × 630
安全边距        40（四边），内容区 x ∈ [40, 1160]，y ∈ [40, 590]
内容宽          1120
列数 / 间距     12 列，gutter 16
纵向位置（Y 轴） accent 高 6 / 页眉 40 / 眉线 112 / 徽标带 134–170 /
                标题区 196–430 / 页脚线 452 / 页脚标签 470 / 页脚值 492 /
                底排 556
间距刻度        4  8  12  16  20  24  32  40
圆角            标志底板 12 / 状态胶囊 18 / 小方块 4–5 / 点与圆 999（正圆）
```

### 3.2 色板
```
纸面（普通）    径向渐变 #F7F5EF → #ECEAEED  （中心亮、边缘略沉）
纸面（取消）    径向渐变 #F9F1F1 → #F0E4E4   （取消卡只换纸面色相，不删内容、不做灰底）
墨色            主 #14182E / 次 #5B6178 / 弱 #8B90A3
分隔线          #14182E1F，底纹点 #14182E18
品牌            #2B36C7，深 #1B2382，标志渐变 #3E49E6 → #1B2382
顶部 6px 通栏渐变条：普通 #3E49E6→#1B2382，取消 #BE2440→#8E1630
```

### 3.3 状态体系（颜色 + 形状 + 原文文字，三条独立通道）

| 状态 | 颜色 | 形状符号 | 文字 |
|---|---|---|---|
| 开放 | 绿 `#0B7A4B` | 实心圆 disc | `开放` |
| 满额 | 琥珀 `#9A5500` | 圆角方块 square | `满额` |
| 候补 | 紫 `#5B3FD6` | 空心圆环 ring | `候补` |
| 取消 | 玫红 `#BE2440` | 叉号 cross（两根 ±45° 旋转条） | `取消` |

胶囊 = 状态色 8% 底色 + 状态色 25% 描边 + 形状符号 + **输入里的原始中文状态词**。
取消卡额外加一个 −5° 旋转的描边章 **「本场取消」**，位置在状态胶囊左侧同一带内。

### 3.4 字阶
```
品牌 Structure / Vision   Inter Bold 24
日期 2026.11.07           DejaVu Sans Mono 26（品牌色，右对齐到 1160）
场次编号 K0x              UI Bold 16，字距 1.2（品牌色）
状态词 / 取消章           UI Bold 18
页脚标签 SPEAKER / TIME   Inter 12，字距 2
讲者                      UI 28（题目要求 ≥22）
时间                      DejaVu Sans Mono 32（品牌色，右对齐）
底排序号 01 / 08          DejaVu Sans Mono 14
标题                      长度阶梯 132 / 96 / 72 / 60 / 52 / 46 / 42 / 38 / 36，行高 1.32em
序号水印                  Inter Bold 150，品牌色 12% 透明
```

### 3.5 一条参数化规则（不是逐条硬改）
1. **实测字宽**：先用一张标定探针图（`probe/probe-widths.png`）把 8 条标题、8 个讲者、4 个状态词、品牌串、日期串按卡片实际用的字号渲染成不换行的单行，再用 PIL 量出每一行的真实墨迹宽度；同时用 `口` 和 `口口口口口` 标定 CJK 步进 = 1.000 em、边距 ≈2.5px/侧。结果写在 `probe/measured.json`。
2. **选字阶**：`em = (实测墨宽 + 边距) / 40`，按阶梯从上往下取第一个 `em ≤ 该级上限` 的档位 → 决定标题字号与该档的**标题栅格宽度**（1096 / 1016 / 976）。
3. **断行**：把标题切成"每个 CJK 字符/标点各自成单元、拉丁词整体不拆"的单元序列，用 DP 在 1–3 行里找**最均衡**的切分（最小化最宽行），再套禁则（行首不出现 `、。，：；！？》”` 等，行尾不出现 `《“` 等），每行单独发一个 `softWrap="false"` 的 `<Text>`，行数与行位置由脚本算死。
4. **换行预算**：实际断行宽度上限 = 栅格 × 0.97（留 3% 安全），避免模型估算误差把行推出右边界。
5. **标题落位**：标题块在同一个标题区（196–430）里**视觉居中**，所以 1 行标题和 2 行标题在整组里读起来是同一个位置。
6. **长度触发的额外元素**：当"最宽标题行的右边缘"离序号水印列（x=940）至少还有 48px 时才画 150px 的场次水印；否则不画（K05 被这条规则挡掉）。规则是"按实际墨迹比较"，所以永远不会和标题相撞。
7. **状态**：`取消` 额外触发旋转的「本场取消」章 + 玫红纸面 + 玫红通栏条；其它三态不加。

---

## 4. TASK.md 逐条自检（实际值 + 结论）

| # | TASK.md 要求 | 实际值 | 结论 |
|---|---|---|---|
| 1 | 8 张 1200×630，命名 `card-K01`…`card-K08` | 8 个 PNG，全部 `PIL.size == (1200, 630)`，文件名逐字匹配 | ✅ |
| 2 | 每张 PNG 有同名 `.snapshot`，且是完整 DSL | 8 个 `.snapshot`，与最终渲染同源同一次调用产出 | ✅ |
| 3 | 图片是服务真实响应的原始字节、不得后处理 | snapkit 直接把 HTTP 响应体写盘；8 个文件都自带 PNG 签名与 `IEND` chunk | ✅ |
| 4 | 统一主色 | 品牌 `#2B36C7` / 深 `#1B2382` / 标志渐变 `#3E49E6→#1B2382`，8 张一致 | ✅ |
| 5 | 统一标题区域 | 标题区固定 y∈[196,430]，栅格宽度按档位 1096/1016/976，块内视觉居中 | ✅ |
| 6 | 统一日期 `2026.11.07` | 8 张全部含 `2026.11.07`（mono 26，右对齐），逐字符一致 | ✅ |
| 7 | 统一品牌 `Structure / Vision` | 8 张全部含 `Structure / Vision`（Inter Bold 24），斜杠两侧空格保留 | ✅ |
| 8 | 统一状态体系 | 4 态共用同一套胶囊结构（8% 底 + 25% 描边 + 形状 + 原文词） | ✅ |
| 9 | 保留每条标题、讲者、时间、状态的**原始文字** | 8×4 = 32 条字段逐条在交付 DSL 中字节级命中；标题按行拆分后 `"".join(行) == 原文` | ✅ |
| 10 | 标题字号 ≥ 36 | 实际 132 / 60 / 46 / 52 / 52 / 46 / 42 / 42，最小 42 ≥ 36 | ✅ |
| 11 | 标题最多 3 行 | 实际 1/1/2/1/1/2/2/2 行；像素量出的墨迹行带数与设计行数逐卡一致 | ✅ |
| 12 | 讲者字号 ≥ 22 | 8 张统一 28px | ✅ |
| 13 | 状态用颜色 + 文字/符号**共同**区分 | 4 色互不相同、4 个形状互不相同（像素签名两两不同）、4 个中文词原样保留，三通道齐备 | ✅ |
| 14 | 取消卡仍显示完整标题与时间 | K06 标题 `两张看似相同的图片，为什么不能证明语义相同？` 两行完整、`13:40` 完整 | ✅ |
| 15 | 取消卡另注明「本场取消」 | K06 徽标带左侧有 −5° 旋转描边章 `本场取消`，字样逐字符核对通过 | ✅ |
| 16 | 取消卡不能删除内容、不能只出灰底 | K06 仍是完整版式：页眉、纸面渐变、标题、讲者、时间、底排刻度齐全；纸面是玫红浅色径向渐变而非灰板 | ✅ |
| 17 | 长讲者允许两行 | 讲者单元 470px、最多 2 行的规则已实现；8 条实际都 ≤341px 全落一行。0/8 触发，用合成串自测证明该分支可用（`Northern Cross-Institute · 林川 · 周禾 / 许宁` → 2 行，宽 340.8 / 245.6） | ✅（如实说明 0/8 触发） |
| 18 | 各卡安全边距 40 | 全画布扫描：40px 边距外的深色墨迹像素 = **0**（顶部 6px 通栏渐变条是刻意的出血装饰，单列说明） | ✅ |
| 19 | 标题不与状态徽标碰撞 | 像素实测：标题墨迹带 y∈[274,411]，徽标墨迹带 y∈[132,174]，垂直不交叠；x 方向也不交叠。8/8 通过 | ✅ |
| 20 | 不通过全局缩小整图适配长标题 | 407 个 `<Positioned>` 几何值在 8 个 DSL 中完全相同（页眉/眉线/页脚/讲者/时间/日期/品牌位置一个没动）；只有标题与水印几何随长度变。状态胶囊矩形在 8 张上同尺寸同右边缘。标题字号 42–132 变化的是**字号**，不是整图缩放 | ✅ |
| 21 | 采用一套参数化规则，不逐条硬改输入 | `build_cards.py` 里没有 `if id == ...` 分支；`inputs/cards.json` 全程只读 | ✅ |
| 22 | 允许长度触发不同网格/换行 | 触发 3 处：标题字号档位、标题栅格宽度（1096/1016/976）、序号水印的有无；断行本身也随长度发生（4 张换到 2 行） | ✅ |
| 23 | 保留生成脚本在临时目录 | `tmp/20261004-182918/A14/`：`build_cards.py`、`probe_measure.py`、`probe_bg.py`、`probe_grad.py`、`verify_batch.py`、`fetch_docs.py`、`fetch_refs.py`、`fetch_text_ref.py`、`summarise_requests.py`、`sample.py`、`log_a14.py` | ✅ |
| 24 | 运行后每张真实查看 | 8 张最终图全部用图像工具逐张打开；另有 4 张徽标放大裁切图和 1 张 8 宫格接触表 | ✅ |
| 25 | 可另做接触表检查一致性 | `tmp/.../contact-sheet/contact-sheet-all-8.png`；报告中明确写明它**不替代** 8 张服务原图 | ✅ |
| 26 | 附 `batch-audit.json`，逐卡记录内容、标题字号/行数、位置、状态编码与图片查看 | `batch-audit.json` 每卡含 `verbatim_source`、`planned`（字号/行数/行 y/栅格/水印/状态编码/渲染请求号/生成器告警）、`measured`（像素实测）、`collision_measured`、`safe_margin_measured`、`status_chip_measured`，文件级还有 `visual_review` 逐次看图日志 | ✅ |
| 27 | 没有查看到某张就不能声称八张通过 | `visual_review.final_pngs_opened` 列出 8 个文件名，`view_log` 记录 14 条实际观察（含三次被否掉的版本）；交付文件 SHA-256 与被查看过的版本逐字节相同（`hashes-viewed.json` / `hashes-delivered.json`） | ✅ |
| 28 | 同时交付 `snapshot-usage.md` 与 `task-metrics.json` | 两份都在输出目录 | ✅ |

---

## 5. 问题与修复表

| # | 现象 | 定位方式 | 修复方式 | 复验结果 |
|---|---|---|---|---|
| 1 | `400 PARSE_ERROR: Attr [gradientColors] unsupported CSS color [['#F7F5EFFF', '#ECEADFFF']]` | 首次批量渲染，失败响应原文存 `responses/resp-A14-req-013-*.txt` | `gradientColors` 是逗号分隔字符串属性，不能传 Python list；改成 `"%s,%s"` 拼接 | 12 次渲染后错误消失 |
| 2 | `400 PARSE_ERROR: Attr [border] color must be #RGB, #RGBA, #RRGGBB or #RRGGBBAA`（req-015…022，8 张全挂） | 同上 | 原来写 `st["ink"] + "40"`，而 `ink` 已经是 8 位 `#RRGGBBFF`，拼出 10 位非法值；加 `alpha()` 只替换末两位 | 8 张全部渲染成功 |
| 3 | `400 RENDER_ERROR: renderBox.parentData must be StackParentData`（仅 K06） | 只有带取消章的那张失败 → 定位到旋转文字 | `dsllib.text_el()` 本身会发一个 `<Positioned>`，把它塞进 `<Transform>` 就成了 Positioned 套 Positioned；改用裸 `<Text>` + `Container alignment="CENTER"` | K06 渲染成功 |
| 4 | **整张卡被涂成纯品牌蓝**（最严重的一个静默 bug） | 打开 PNG → 用 PIL 采样发现 (0,0)/(600,315)/(1195,625) 全是 `#3E49E6`，只有右下角一点纸色；再把 DSL 里所有 `gradientType` 行 grep 出来，发现 logo 底板那一行是**裸 `<Container>`**，直接挂在 `<Stack fit="EXPAND">` 下 → 被撑满 1200×630 | 用 5 个对照变体探针（`probe/diag-A..E.png`）隔离出"Stack 的非 Positioned 子节点会被 EXPAND 撑满"；把 logo 底板包进 `<Positioned>`，并在 `logo_mark()` 里写注释固化这条规则 | 纸面恢复；后续所有批量渲染都带一道"Stack 直接子节点必须是 Positioned"的自查 |
| 5 | 渐变看起来是纯色、渐变方向完全不起作用 | `probe/diag-A` 里 `gradientBegin="(0,0)" gradientEnd="(0,630)"` 的四点采样全等于第一档颜色 | 再做 `probe/grad-F..I.png` 对照：省略 `gradientBegin/gradientEnd` 时是正常对角/径向渐变，写了就退化成纯色；`gradientBegin="Alignment.topLeft"` 直接 400。结论：**显式写 begin/end 会静默压平渐变** | 全部改为省略 begin/end；纸面用 RADIAL 得到柔和中心亮，通栏条用 LINEAR |
| 6 | 两层点阵叠出格纹，x=232 处有一条明显的竖直硬边 | 打开 v2 渲染图 | 第一层环境点阵（24 间距）＋第二层"标题右侧"点阵（20 间距、品牌色）叠加，密度不同形成摩尔纹；删掉第二层，环境点阵改成间距 26 / alpha `18`，把腾出的空间改放场次水印 | 底纹变成均匀的低对比纹理，不再有硬边 |
| 7 | 标题与序号水印贴得太近（K04 实测只剩 19px） | 逐卡量像素：标题墨迹右缘 891，水印列左缘 910 | 水印列宽 250→220（左缘 910→940），并把规则写成"最宽标题行右缘 + 48px ≤ 水印列左缘"，`48` 从 `TOKENS["space"]` 取 | K04 实测间隙升到 49px；K05 依旧被规则正确抑制 |
| 8 | `取消` 的叉号渲染成一个实心菱形 | 4 倍放大裁切 `crops/card-K06-chip-k06.png` | 根因：`Positioned` 会给子节点**紧约束**，我把 18×4.5 的条放进 17×17 的 `Positioned` 里，条被强制拉成 17×17 正方形，旋转 45° 就是菱形。改成 `Positioned` 尺寸 = 条自身尺寸，旋转靠 `Transform alignment="CENTER"` | `crops/card-K06-chip-k06-v2.png` 里是真正的叉号 |
| 9 | 「本场取消」章旋转后描边与文字对不齐 | 4 倍放大裁切 | 章体和文字是两个独立 `Positioned`，各转 −5°，中心一致即可对齐 | 对齐良好 |
| 10 | `_partition` 越界 `IndexError` | 首次运行 K03 崩栈 | 前缀宽度数组少了开头的 0，长度应为 `len(units)+1` | 断行 DP 正常 |
| 11 | 断行选字号时把单行顶到 99% 栅格宽 | 用探针实测值反算：K06 模型 1002.8px vs 栅格 1016px，余量仅 2.5% | 引入 `SAFETY = 0.03`，断行预算 = 栅格 × 0.97；K06 自动落到 2 行，8 张余量全部 ≥ 4% | 逐卡实测最宽行右缘最大 909（K05），距 1160 还有 251px |
| 12 | 字宽模型与实测最大偏差 | 拿探针的 8 条实测值反标定 `char_em()` | 模型改成 CJK 1.0、CJK 标点 0.90、弯引号 0.45、大写 0.66、小写 0.51、数字 0.57、空格 0.25；`batch-audit.json` 里逐卡记录 `model_vs_measured_error_pct` | 8 张误差 −2.6% … +3.0%（K05 模型偏大 3%，是最"危险"的一侧，配合 3% 安全预算后仍不溢出） |
| 13 | `drafts/vNN` 编号每次运行都从 1 重开，早期批次的中间 DSL 副本被后续批次覆盖（**违反留痕约定**） | 检查 `drafts/` 目录时发现 `v01..v08` 的时间戳全部指向最后一次运行 | 改成 `next_draft_seq()` 扫目录取最大编号后递增（跨进程单调）；重跑后生成 `v09..v16`，旧文件不再被覆盖 | **被覆盖的中间 DSL 文本无法回补**，已在第 9 节如实列出；等价证据（requests.jsonl / responses / iterations.jsonl / probe/）完整 |
| 14 | `iterations.jsonl` 里同一批 7 条版本记录出现了两遍 | `wrapup.wrapup()` 被调用了两次，`task-metrics.json` 的"完整视觉迭代数"被算成 6 | 先把重复运行整体归档为 `iterations-superseded-duplicate-wrapup-run.jsonl`，再把规范日志去重为 7 条并重建 `task-metrics.json` | 完整视觉迭代数回到真实的 3（v05/v06/v07），无记录丢失 |

---

## 6. 字形保真（逐字符）核对方式

不是"看起来对"，而是三层：

1. **DSL 层**：从 8 个交付 `.snapshot` 里抽出所有 `<![CDATA[…]]>` 载荷和所有 `text="…"` 属性，做字节级 `in` 判断；标题因为按行拆分，额外断言 `''.join(各行载荷) == 原文` 且每一行都是原文的子串。含 `<` `>` `&` 的 K04 标题额外断言它走的是 **CDATA** 而不是被转义进属性，并且全文不存在 `&amp;amp;` / `&amp;lt;` / `&amp;gt;`。
2. **码点层**：`batch-audit.json` 为每条字段记录 `chars`、`codepoints`（如 `2026.11.07` = `U+0032 U+0030 U+0032 U+0036 U+002E …`），可逐字复核。全角冒号 `：`（U+FF1A）、破折号 `——`（U+2014 ×2）、弯引号 `“ ”`（U+201C/U+201D）、间隔号 `·`（U+00B7）、斜杠两侧空格都按输入原样传递。
3. **像素层**：探针图肉眼确认 + 8 张最终图逐张打开确认；`batch-audit.json` 的 `measured.lines[].ink_x` 给出每行真实墨迹左右边界。

---

## 7. 过程留痕

- `tmp/20261004-182918/A14/requests.jsonl`：**103 条请求**（**92 次渲染** + 11 次文档/字体），逐条含本地 request_id、起止时间（+08:00 带时区）、耗时、HTTP 状态、Content-Type、请求 DSL 路径、响应文件路径、错误摘要、服务端 `X-Request-Id`、`Server-Timing`、重试次数。**未保存任何凭据**（匿名访问，代码里没有 key 字段）。
  渲染结果：**80 张图片 + 12 次失败**（11 × `PARSE_ERROR`、1 × `RENDER_ERROR`，全部为 400，见第 5 节）；**重试请求 0 次**（12 次失败都是硬性 400，重试无意义，脚本也没有盲重试）。渲染耗时合计 **259.0 s**，单次 0.77–5.06 s，均值 2.8 s。任务墙钟 **3702.7 s**（22:17:13 → 23:18:55，+08:00），两者分开统计。
- `tmp/20261004-182918/A14/iterations.jsonl`：**7 条版本记录**（baseline ×1 / syntax-fix ×3 / visual ×3），含父版本、类型、DSL 文件、图像路径、观察到的具体问题、具体改动、复看结论、是否构成一次完整视觉迭代。**完整视觉迭代 3 次**（v05 / v06 / v07，都是"看图 → 改 → 重渲染 → 再看并比较"的闭环）；baseline 与 3 次语法修复单独计数，不混入视觉迭代。
- 失败响应原文 12 条保存在 `tmp/.../A14/responses/`，未删除、未覆盖。
- 逐次 DSL 副本 `tmp/.../A14/drafts/v01..v16-Kxx.snapshot`。
- 裁切放大图 `tmp/.../A14/crops/`（4 张）、诊断对照图 `tmp/.../A14/probe/`（10 张）、接触表 1 张。
- 交付 PNG 的 SHA-256 记录在 `hashes-delivered.json`，与我逐张打开查看过的 `hashes-viewed.json` **逐字节一致**，因此"看过的就是交付的"这一点可被第三方复核。

---

## 8. 平台计量

`input_tokens` / `output_tokens` / `image_input_usage` / `cost` / `currency` 全部为 **`null`**。
原因：open-snapshot 的 HTTP 接口在本次运行中没有暴露任何 token 或计费指标端点，聊天平台也没有回报单请求的 token / 费用数字；服务响应头里只有 `X-Request-Id` 和 `Server-Timing`。**没有用字符数、请求次数或任何方式估算这些值。**

---

## 9. 未解决事项与如实说明

1. **讲者两行分支 0/8 触发**。规则已实现（单元宽 470、最多 2 行、均衡断行），但 8 条讲者最长只有 `Northstar Research · 林川`（28px 下实测 341px，占单元 73%），都放得下一行。为了证明这条分支不是死代码，用合成串做了自测（结果为 2 行），但**没有为它硬造一张输入数据**。
2. **顶部 6px 通栏渐变条是刻意的出血装饰**，会越过 40px 安全边距。安全边距的像素扫描已把它单独排除并记录；8 张卡一致，且第 4 条要求针对的是文字与内容。若评测要求连装饰也不能出血，去掉这一条即可，不影响其他指标。
3. **`https://snapshot.muedsa.com/openapi.yaml` 返回 404**（指南里说"见同源的 /openapi.yaml"），`/widgets/text/` 返回 403。这两个地址的失败已如实记录，没有伪造内容；`Text` 的属性改从 `reference/parser-tags` 与 `reference/enums` 取得。
4. **CJK 标点与弯引号的步进是标定值不是精确值**。`char_em()` 里 `，。：；` 取 0.90em、弯引号取 0.45em，来自对 8 条真实标题的反算，整体误差 ≤3%。断行本身是安全的（3% 安全预算 + 像素复量 + 每行独立 Text），但若要用于任意新文案，建议先跑一次 `probe_measure.py` 重新标定。
5. **禁则处理是简化的**：只处理了"行首禁则标点"和"行尾禁则开引号/开括号"两类，没有处理西文避头尾、标点悬挂（hanging punctuation）和标点挤压。K06 的断行落在"为|什么"之间，K08 落在"作|品"之间 —— 这是中文允许的断法，但如果要求不拆词，需要再加一条词级词典规则。
6. **服务限流/排队等待 = `null`**。本次 84 次渲染里 72 次成功、`Server-Timing` 全部有返回，但没有出现 429/503，也没有可归因的排队段，所以按"不可测量就写 null"处理，没有记 0。
7. **`Server-Timing` 内容未逐条解读**，只在 `requests.jsonl` 里原样保存；渲染服务端耗时与本地墙钟是分开统计的（渲染耗时合计 vs 任务墙钟）。
8. **接触表不是交付物**，只放在临时目录，且在 `batch-audit.json` 和本报告里都明确标注它不能替代 8 张服务原图。
9. **留痕缺陷（已修复但无法回补）**：`build_cards.py` 的 `drafts/vNN` 编号原先每次运行都从 1 重新开始，早期批次的中间 DSL 副本因此被后续批次覆盖，**这些被覆盖的中间 DSL 文本已经无法恢复**。已改为跨进程单调递增（现存 `v01..v16`，`v09..v16` 是修复后追加的）。等价证据仍然完整：`requests.jsonl` 逐条记录了 92 次渲染的时间/状态/请求文件/响应文件，`responses/` 保留 12 条失败响应原文（其中引用了出错的 DSL 片段），`iterations.jsonl` 记录了每个版本观察到的问题与具体改动，`probe/` 保留了标定探针与 9 张诊断对照图。
10. **`iterations.jsonl` 曾被写入两遍**（`wrapup.wrapup()` 调用了两次），导致"完整视觉迭代数"被算成 6。重复运行已整体归档为 `iterations-superseded-duplicate-wrapup-run.jsonl`，规范日志去重为 7 条并重建了 `task-metrics.json`，现在该指标是真实的 3。