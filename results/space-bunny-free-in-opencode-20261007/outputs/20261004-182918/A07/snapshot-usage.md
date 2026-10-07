# A07 · 三线换乘图与路线核验 — Snapshot 使用报告

- **状态**：completed
- **run_id**：`20261004-182918`
- **输出目录**：`outputs/20261004-182918/A07/`
- **临时目录**：`tmp/20261004-182918/A07/`
- **交付**：`network-map.png` + `network-map.snapshot`（1600×1000）、`travel-card.png` + `travel-card.snapshot`（720×1280）、`routes.json`、`snapshot-usage.md`、`task-metrics.json`
- **渲染请求**：15 次（1 次能力探针 + 9 次 network-map + 5 次 travel-card），全部 HTTP 200 / `image/png`，0 失败、0 重试
- **看图**：15 次（整图 10 次 + `crop.py` 放大 5 次）

---

## 1. 实际使用的服务文档与字体

全部为本题**真实抓取**（记录在 `tmp/20261004-182918/A07/requests.jsonl`，`request_id` 见下表），
没有沿用其它题的缓存结论：

| request_id | URL | 状态 | 落盘 | 实际用途 |
|---|---|---|---|---|
| A07-req-001 | `https://open-snapshot.muedsa.com/ai-guide.md` | 200 text/markdown | `docs/ai-guide.md` | 确认 `POST /snapshot` 请求体是 UTF-8 纯文本、响应体是图片字节；8 位颜色按 `#RRGGBBAA` 读；错误 JSON 的处理方式 |
| A07-req-002 | `https://snapshot.muedsa.com/` | 200 text/html | `docs/dsl-docs-index.html` | 找到参考文档入口 |
| A07-req-004 | `https://snapshot.muedsa.com/reference/parser-tags/` | 200 text/html | `docs/parser-tags.html` | 确认 `Transform.matrix` 是**列主序 4×4、外层带括号、值之间不能有空格**；`Positioned` 必须是 `Stack`/`IndexedStack` 直接子节点；`Text` 的 `fontSize/fontStyle/align` 等属性名 |
| A07-req-005 | `https://snapshot.muedsa.com/guides/painting/` | 200 text/html | `docs/painting.html` | 确认 `Transform` 用 `alignment` 决定变换中心、旋转只改绘制坐标不参与布局 |
| A07-req-003 | `https://open-snapshot.muedsa.com/fonts` | 200 text/plain | `fonts.txt` | 27 个可用字族，逐行核对 |

**实际使用的字体**（全部来自上面这份 `/fonts` 真实返回，未臆造）：

- `Inter,Noto Sans CJK SC`（`dsllib.UI`）— 全部中文标签与正文
- `DejaVu Sans,Noto Sans CJK SC` — 无障碍徽标 `✓`(U+2713) / `✕`(U+2715)
- 图中出现的字形 `›`(U+203A)、`→`(U+2192)、`×`(U+00D7)、`−`(U+2212)、`·`(U+00B7)、`└`(U+2514) 均先经探针图确认有字形

---

## 2. 实际用到的标签与属性

`Snapshot` / `Container` / `Stack(fit=EXPAND)` / `Positioned` / `Transform(matrix,alignment)` /
`Text(text,color,fontSize,fontFamily,fontStyle,textAlign)` / `Container(color,borderRadius,border,shape)`
（`shape="CIRCLE"` 经探针确认与 `borderRadius=r` 渲染一致，最终统一用 `borderRadius`）。

**没有任何 `<Image>`**，主体线路、站点圆、字母徽标、文字全部是 DSL 图元：

- **45°/90° 线段**：`rot_rect()` 生成一条 `width×length` 的 `Container`，外面套
  `<Transform matrix="(cosθ,-sinθ,0,0,sinθ,cosθ,0,0,0,0,1,0,0,0,0,1)" alignment="CENTER">`，
  其中 `θ = -degrees(atan2(dy,dx))`（屏幕 y 向下，所以要用负号才是视觉逆时针）。
  `Positioned` 的框中心对齐线段中点，于是 DSL 里的坐标就是脚本算出的坐标。
- **跨线交叉的"跨线桥"**：低优先级线路在交叉点处按参数 `t±GAP/len` 切成两段不画
  （`split_at()`），高优先级线路连续，形成明确的断口，而不是含糊的线条相交。
- **字母双重编码**：终点大徽标（r=19，白环 + 线色 + 白色字母）+ 每段中点线路字母小徽标
  （r=10.5，白环 + 线色 + 字母），红/绿相近也能靠字母区分。
- **无障碍徽标**：26×26 圆角方块（`#0F766E` 可用 / `#B45309` 不可用）+ 白色 ✓/✕。

## 3. 本题踩到的 DSL / 代码语义坑

| # | 现象 | 定位方式 | 结论 |
|---|---|---|---|
| 1 | `rot_rect` 的旋转方向可能整体镜像 | 探针图 `preview/probe-01.png`：从 (200,200) 画 0°/90°/135°/225° 四条旋转条，看图确认分别指向 E/S/NE/SW | `θ=-atan2(dy,dx)`、`a=cosθ,b=-sinθ,c=sinθ,d=cosθ` 正确，与手册一致 |
| 2 | **锚点分支的运算符优先级 + 语义双错** | 看图发现 S06 标签压住 R 线 45° 斜段，而脚本 `label collisions` 报的是 S06/S12 互相碰撞、不是压线 | `cx + 11 + gap - 26 if d=="E" else cx + 8` 被三元整体吞掉；且 W 落进"下方"分支。E/W 必须纵向居中 `y=cy-h/2` |
| 3 | **`out, _ = chain_kids(...)` 把整张卡的元素列表覆盖掉** | 卡片首版只渲染出页眉/站序链/页脚，白卡、序号徽标、标题、线路 chip、换乘行全部消失，而 HTTP 200 无任何报错 | Python 变量遮蔽，纯本地 bug。**只能靠看图发现**；修好后给两个生成脚本都加了 `archive()` |
| 4 | `card_metrics()` 漏加一行 28px，卡片实际高度比声明短 28px | 写 `measure_card_a07.py` 扫描 PNG 白色像素带：实测 238/360/238，声明 260/382/260 | 声明高度必须与渲染累加严格一致；现在改完实测带与 `card_metrics` 对齐 |
| 5 | 文字框过窄会被**静默截断**（不换行、不报错） | `D.warnings()` 报出 6 条，逐条缩短文案或放宽框宽，最后 warnings 清零 | 与手册一致；每轮都打印并处理 |
| 6 | 16px 小药丸里放 17px 的"换乘"会上下溢出药丸 | 放大 S04/S05/S08 标签 | 药丸高 19→24，字号 17 的基线按手册 `[y+3, y+3+1.05×size]` 重新定位 |
| 7 | 字母徽标正好落在交叉缺口旁，看起来像"绿线从 G 徽标起站" | `crop.py` 3× 放大交叉点 | 缺口 22→16px；把该段字母徽标比例从 0.65 移到 0.78，所有字母徽标离交叉点 ≥99px |

---

## 4. 逐项自检表（对照 TASK.md 每条硬指标）

### network-map.png（1600×1000）

| TASK.md 要求 | 实际值 | 结论 |
|---|---|---|
| 尺寸 1600×1000 | PIL 实测 `(1600, 1000)`，`image/png`，370 978 B | ✅ |
| 按线路站序连接相邻站 | `a07_common.validate()` 校验每条线路折线的站点序列与 `network.json` 完全一致、且每对相邻站在折线上只隔 0 或 1 个拐角 → **0 问题** | ✅ |
| 站间双向可走、耗时相同 | 16 条边在 `ADJ` 中双向登记；`routes.json` 逐条断言 `"line R connects S01-S02 in both directions"` 等 16 项全过 | ✅ |
| 共享站是换乘站 | 只有 S04(红/蓝)、S05(红/绿)、S08(蓝/绿) 出现在 ≥2 条线上；图上这 3 站用「双环 + 加粗站名 + 黑色『换乘』药丸」三重标记 | ✅ |
| 单纯线条交叉不能被误认为换乘 | 全网只有 1 处纯交叉（绿线×蓝线 @700,390），该处**无任何车站**；画成蓝线连续 / 绿线断口 16px 的跨线桥，另加引线 + 文字「跨线交叉 · 不可换乘」，图例第 2 列也画出同样的示例 | ✅ |
| 用颜色 + 线路字母，不能只靠红绿差异 | 每条线有终点大字母徽标（R/B/G）+ 每段中点字母徽标 + 图例第一列「线样 + 徽标 + 名称」；页眉右上角明写「红绿两色相近，故每条线路同时用颜色 + 字母双重编码」 | ✅ |
| 16 站名称与编号完整 | S01 松林 … S16 研究所，16 个 `✓/✕ 徽标 + 编号 + 站名` 全部在图上；右侧「全网总览」另列全量站点属性 | ✅ |
| 转折按 45°/90° 组织 | 脚本对每条折线的每一段断言 `dx==0 or dy==0 or abs(|dx|-|dy|)<=0.5` → **0 问题**（含 R 的 45° 上坡、B 的 45° 长对角、G 的 45° 上坡与 45° 下坡） | ✅ |
| 非地理地图须明确说明 | 页眉副标题、右侧信息面板、图例第 4 列、页脚共 4 处写明「非地理示意图 / 站距不代表真实距离」 | ✅ |
| accessibility 逐站标注 + 图例 | 每站标签前有 ✓(青) / ✕(琥珀) 徽标；图例第 3 列解释两种徽标含义；右侧面板列出 4 个非无障碍站 S03/S05/S09/S14 并注明「仍在线路上」 | ✅ |
| 无障碍约束不删线路 | 16 站 3 线 16 区间全部保留；4 个非无障碍站照样画在各自线路上（如 S05 东桥仍在红/绿两线上） | ✅ |
| 地图标签 ≥20 | 站名 20、图例 20、信息面板 20、交叉注释 20、页脚 20（只有页眉右侧说明与 `合计` 类辅助文字为 20），全部 ≥20 | ✅ |
| 只用 `POST /snapshot`、无 `<Image>` | `requests.jsonl` 中 15 条 render 全是 `POST https://open-snapshot.muedsa.com/snapshot`；DSL 中 `grep '<Image'` 为 0 命中 | ✅ |
| PNG 是服务真实响应原始字节 | `snapkit.render()` 直接把响应体写盘，无任何后处理；`.snapshot` 与最终渲染的 DSL 逐字一致 | ✅ |

### travel-card.png（720×1280）

| TASK.md 要求 | 实际值 | 结论 |
|---|---|---|
| 尺寸 720×1280 | PIL 实测 `(720, 1280)`，`image/png`，261 972 B | ✅ |
| 展示 3 条普通旅程 | 三张卡分别对应 `queries` 的 S01→S11、S13→S12、S07→S16，每张给出站序、线路段、边数、换乘次数 | ✅ |
| 记录站序与线路段 | 每段一行：`线路徽标 + 线路名` 与 `上车站 → 下车站 · N 区间`；下一行是逐站站序（`›` 连接，换乘站单独一行标出） | ✅ |
| 边数 = 站数 − 1 | 卡上标题行同时写「6 区间 · 1 换乘」，站序链 7 站；`routes.json` 对 4 条路线逐一断言 `edges == station_count - 1` | ✅ |
| 换乘次数，首次上车不算 | `换乘次数 = 乘车段数 − 1`，Q1/Q2/Q3 分别 2/2/2 段 → 1/1/1 次换乘；`routes.json` 断言 `transfers == leg_count - 1` | ✅ |
| 边数相同时取换乘最少 | 求解器先最小化边数、再最小化换乘、最后按站序字典序定唯一解；`routes.json` 记录每个 OD 对的全部 `(边数,换乘)` 候选成本集合 | ✅ |
| 三条旅程的无障碍可行性 | Q1 ✓ 可作无障碍旅程（经过书院、花园但可乘车通过）；Q2 ✗ 不可作（换乘站东桥非无障碍）；Q3 ✓ 可作 | ✅ |
| 最短不满足时给无障碍最短替代 | Q2 给出替代：石溪→公园→工坊→**中心**→东桥→江湾→机场，**区间数同为 6**、换乘由 1 增为 2，卡上标明「区间数相同，换乘 +1」 | ✅ |
| 手机正文 ≥20 | 卡上所有正文（标题 23、正文/说明/页脚 20）均 ≥20 | ✅ |
| 两图视觉系统一致、分别排版 | 同一套配色（`#E11D48/#1D4ED8/#047857`）、同一套徽标与 ✓/✕ 字形、同一条 R 线同为 7 站 6 区间；排版为 1600 宽三栏面板 vs 720 宽单列卡片 | ✅ |
| 附 routes.json | 29 600 B，含定义、网络全量数据、3 条 query 的完整解与 32 项自检（全过） | ✅ |

### 求解结果（与图上文字一致）

| query | 站序 | 线路段 | 边数 | 换乘 | 无障碍 |
|---|---|---|---|---|---|
| Q1 S01 松林 → S11 会展 | 松林 › 北门 › **书院** › 中心 › **花园** › 南门 › 会展 | 红线 3 区间 → 蓝线 3 区间 | 6 | 1（中心 S04） | ✅ 可作；书院、花园可乘车经过 |
| Q2 S13 石溪 → S12 机场 | 石溪 › **公园** › 工坊 › 剧院 › **东桥** › 江湾 › 机场 | 绿线 4 区间 → 红线 2 区间 | 6 | 1（东桥 S05） | ✗ 不可作：换乘站东桥非无障碍<br>替代：石溪›公园›工坊›**中心**›东桥›江湾›机场，绿线2→蓝线1→红线3，**6 区间 / 2 换乘** |
| Q3 S07 西港 → S16 研究所 | 西港 › 工坊 › 剧院 › **东桥** › 研究所 | 蓝线 1 区间 → 绿线 3 区间 | 4 | 1（工坊 S08） | ✅ 可作；东桥可乘车经过 |

> 加粗站 = 非无障碍站。琥珀色站名 = 非无障碍站，两张图一致。

---

## 5. 问题与修复表

| 版本 | 问题现象 | 定位方式 | 修复方式 | 复验结果 |
|---|---|---|---|---|
| map v01 | 琥珀色旅程高亮让图上像有第四条线，S04/S05/S08 处黄块堆叠 | 整图看图 | 删除 `journey_overlay()`，改为右侧「旅行卡上的三条旅程」编号徽标交叉引用 | v03 整图确认干净 |
| map v01 | S06/S12 标签框重叠 | 脚本 `label collisions: [('S06','S12')]` | S06 锚点 SE→W，并压缩右侧信息面板行高 | 碰撞清零 |
| map v01 | 图例「图例」二字压住第一列表头 | 整图看图 | 合并成「图例 · 线路（颜色 + 字母双重编码）」 | v03 确认 |
| map v01 | 2 条图例文字被静默截断 | `D.warnings()` | 缩短「跨线交叉（缺口＝不断线，不可换乘）」→「跨线交叉 · 缺口表示不可换乘」；改写图面说明第 3 条 | warnings 归零 |
| map v02 | S06 标签仍压住 R 线 45° 斜段 | 整图看图（脚本只报了 S06/S12 互相碰撞，没报压线） | 修 `label_box()`：E/W 纵向居中 `y=cy-h/2`，去掉三元优先级 bug | v04 整图 + `crop.py` 3× 放大 S06/S12 区域确认斜段不再穿字 |
| map v03 | 交叉点楔形只有 80px 宽，注释文字放不下 | 几何计算 | 注释移到交叉下方 y≈500 的宽楔形（230px）并加引线 | v04 整图确认 |
| map v04 | 绿线缺口 22px 偏长、字母徽标贴缺口像"起站" | `crop.py` 3× 放大交叉点 | 缺口半长 11→8；绿线该段徽标比例 0.65→0.78 | v05 放大复验：断口清晰、徽标远离 |
| map v04 | 「换乘」小药丸内文字上下溢出 | `crop.py` 放大 S04/S05/S08 | 药丸高 19→24，字号 17 基线按手册经验值重定位 | v05 放大复验完整 |
| map v05 | 信息面板 18/19px、交叉注释 19px、页脚 18px，违反「标签≥20」 | 逐条核对 TASK.md | 全部提到 20px，相应缩短 4 条文案 | v06 warnings 归零 |
| map v06 | 「西港 → 研究所　4区间·1换乘」仍溢出 | `D.warnings()` | 全角空格→普通空格、去掉中点 | v07 warnings 归零 |
| card v01 | 白卡背景/序号/标题/线路 chip/换乘行**整块消失** | 整图看图（HTTP 200 无报错） | `out, _ = chain_kids(...)` → `ck, _ = ...`；`out += ck` | v11 整卡恢复 |
| card v01 | 5 条文字溢出（替代路线标题 1 + 页脚 4） | `D.warnings()` | 页眉 168→158、卡间距 12→10、页脚文案缩短、可用宽度 628→644 | v12 剩 1 条 |
| card v12 | 页脚第 1 条仍超 4px | `D.warnings()` | 「（首乘不计）」替换「，首次上车不计」 | v13 warnings 归零 |
| card v13 | 第一张卡的提示文字骑在白卡下边框上 | `measure_card_a07.py` 扫白色像素带（实测 238/360/238 vs 声明 260/382/260）+ `crop.py` 放大 | `card_metrics()` 补上漏掉的 28px；判定与提示合并成一行；页眉 146、卡间距 14 | v14 实测 169-406 / 443-802 / 839-1076，与声明一致 |
| card v14 | 替代路线换乘竖线留白 16px 偏挤；细节文案超框 | `D.warnings()` + `crop.py` | 留白 16→22；文案改「· 经过非无障碍站 书院、花园（可乘车）」/「· 受限换乘站 东桥 S05（非无障碍）」 | 最终 warnings 归零 |

最终两图的 `D.warnings()` 均为空；`a07_common.validate()` 0 问题；
`label_collision_report()` 为空；`routes.json` 32 项自检全过。

---

## 6. 实际用到的文件

```
outputs/20261004-182918/A07/
  network-map.png        1600x1000  服务真实响应
  network-map.snapshot   与上面对应的完整 DSL
  travel-card.png        720x1280   服务真实响应
  travel-card.snapshot   与上面对应的完整 DSL
  routes.json            3 条 query 的解 + 32 项自检
  snapshot-usage.md      本文件
  task-metrics.json      finalize.build() 生成

tmp/20261004-182918/A07/
  a07_common.py          网络图、路径求解器、示意几何与校验
  build_map_a07.py       地图 DSL 生成（内含 rot_rect/badge/label 几何与 archive）
  build_card_a07.py      卡片 DSL 生成（复用 build_map_a07 的图元与配色）
  probe_01.py            旋转方向 / 圆形 / 字形覆盖探针
  write_routes_a07.py    routes.json 生成与自检
  measure_card_a07.py    扫描 PNG 白色像素带核对卡片实际高度
  log_a07.py             记迭代 + 出指标 + 更新套件状态
  patch_fonts_a07.py     一次性把地图标签统一提到 ≥20px 的补丁脚本
  fetch_docs_a07.py      抓取 ai-guide.md 与 DSL 文档
  drafts/probe-01.snapshot
  drafts/map-v09-final.snapshot
  drafts/card-v05-final.snapshot
  docs/ai-guide.md  docs/parser-tags.html  docs/painting.html  docs/dsl-docs-index.html
  fonts.txt
  preview/probe-01.png
  crops/network-map-cross-gap.png  crops/network-map-cross-gap2.png
  crops/network-map-s06-s12.png    crops/travel-card-card1-bottom.png
  crops/travel-card-card2-alt.png
  requests.jsonl  iterations.jsonl
```

> `tmp/.../A07/responses/` 目录未生成：本次 15 次渲染全部一次成功，snapkit 只在收到非图片
> 响应时才写该目录，所以没有任何失败响应留存（`failed_render_requests = 0`）。

---

## 7. 未解决事项与如实说明

1. **中间版本 DSL 未全部留存（留痕缺口）**。地图 v03~v08、卡片 v02~v04 当时直接渲染到最终
   输出路径（`snapkit.render(..., final=True)`），同名 `.snapshot` 被下一版覆盖，所以
   `drafts/` 只保留了探针和两个最终版本。每一版的可观察问题、具体改动、复验结论都完整
   写在 `iterations.jsonl`（14 条）与本文件第 5 节，但中间版本的 DSL 文本本身找不回来了。
   发现后已给两个生成脚本加上 `archive()`，之后的每次渲染都会另存不可覆盖的草稿。
2. **token / 图片用量 / 费用：未知**。`open-snapshot` 的 HTTP 接口没有暴露任何计量端点，
   本次运行也没有拿到平台侧的 per-request token 或费用数字，因此 `task-metrics.json` 中
   `input_tokens / output_tokens / image_input_usage / cost` 一律为 `null`，并注明来源与
   原因。**没有按字符数、字节数或任何余额去估算。**
3. **排队/限流等待：未知**。`finalize.py` 把 `rate_limit_or_queue_wait_seconds` 记为 `null`
   而不是 0：本次 15 次渲染的响应头都没有报告 Server-Timing 的排队段，无法区分"没有排队"
   和"服务没告知"，因此如实留空。
4. 服务本次未出现任何 4xx/5xx，也没有触发 429/503，所以没有 `Retry-After` 处理记录；
   `requests.jsonl` 中 `failed_render_requests = 0`、`retry_requests = 0`。
5. 本题为纯示意图，未做像素级"地理真实性"校验——`network.json` 本身也没有经纬度，
   TASK.md 明确要求按 45°/90° 组织转折并声明非地理，因此站位坐标是脚本设计的示意值，
   不代表任何真实城市。
