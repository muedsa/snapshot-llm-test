# Snapshot 全套任务 · 总使用与踩坑报告

运行：`run_id = 20261003-114508-flashmax`
总输出：`outputs/20261003-114508-flashmax/` · 总临时：`tmp/20261003-114508-flashmax/`
覆盖范围：`catalog.json` 的 `task_order` 全部 30 题（A01–A24、B01–B06），profile 为默认 `all`。

本文件记录**真实发生过**的文档应用、DSL 能力边界、跨题经验与踩坑。所有结论都来自实际请求与
实际打开的图片；未确认的原因标注为推测。逐题的详细自检在各自 `outputs/<run_id>/<TASK>/snapshot-usage.md`。

---

## 1. 实际文档与资料来源

| 来源 | 实际用途 |
|---|---|
| `https://open-snapshot.muedsa.com/ai-guide.md` | 请求体必须是 UTF-8 纯文本 DSL、`Content-Type: text/plain; charset=utf-8`、成功返回 PNG 原始字节、失败返回 JSON 错误体、`x-ratelimit-limit: 120` |
| `https://snapshot.muedsa.com/` 与 `/reference/parser-tags/` | 标签与属性清单：`Snapshot`/`Container`/`Stack`/`Positioned`/`Text`/`Transform`/`BackdropFilter`/`ImageFiltered` 等；`alignment` 常量语义；`Transform.matrix` 为列主序 4×4 |
| `https://snapshot.muedsa.com/guides/parser/` | 根标签只能有一个子节点；属性在建树阶段校验，因此格式错会直接抛错而不是静默忽略 |
| `GET /fonts` | 实际可用字体清单（见下） |
| 服务端错误体（真实请求返回） | 每条错误都给了 `code`/`message`/`position`，用 `curl.exe --data-binary` 才能读到正文 |

可用字体（实测）：`Noto Sans CJK SC`、`Noto Sans Mono CJK SC`、`Noto Serif CJK SC`、
`Noto Serif CJK JP`、`Inter`、`Inter Tight`、`DejaVu Sans`、`DejaVu Sans Mono`、`DejaVu Serif`、
`Noto Color Emoji`。**未臆造任何字体名。**

---

## 2. 复用率最高的 DSL 能力

整套 30 题、百余张图全部由同一个思路构建：**用 Python 计算几何与文字宽度，生成一份扁平的单层
`Stack` + 绝对坐标定位的 DSL**。高频构件：

| 构件 | 做法 |
|---|---|
| 卡片 / 面板 | `Positioned` + `Container(color, borderRadius, border="1 SOLID #…", boxShadow)` |
| 任意方向线段 | 用 `Transform matrix` 让一个 `width=L height=th` 的圆角 `Container` 旋转并平移到中点 |
| 箭头 | 3 条旋转细条拼三角形（避免依赖路径/多边形标签） |
| 虚线 / 点划线 | 手工按步长切段，每段单独画（不依赖虚线标签） |
| 图表 | 柱/条/折线全部由矩形 + 线段拼出；数值由脚本真实计算 |
| 文字对齐 | 需要水平居中/右对齐时包一层 `Container(width=…, alignment=…)` |
| 图层控制 | 靠**书写顺序**：先画背景，再画线条，最后画文字 |

---

## 3. 能力边界（实测，务必注意）

1. **`Transform matrix` 的列主序语义**：矩阵 16 个数字中，`m00 m01 m10 m11` 是线性部分，
   第 13、14 位是 `tx ty`。只写单位矩阵 + 平移**无法旋转**；旋转必须放进前四位。
   A08 一度误判为“旋转失效”，实际是绘制顺序把路线盖住了。
2. **`BackdropFilter` 模糊的是整幅已合成画面**（不是自己的子树），强度随 sigma 增大；
   sigma=1 是唯一不糊字的档位。**`ImageFiltered` 只模糊自己子树**（会把里面的字一起糊掉）。
3. **根标签只允许一个子节点**。
4. `borderRadius` 只接受**单个数字**；四角不同必须写 `borderRadiusTopLeft/TopRight/BottomLeft/BottomRight`；
   `"5 5 0 0"` 会报格式错。
5. 元组型属性要写成 `padding="(24,32)"` 形式。
6. 颜色只接受 `#RGB` / `#RRGGBB` / `#RRGGBBAA`；**10 位会报错**。
7. **文字会被容器宽度逼着换行**：CJK ≈ 1.00×字号，等宽数字/字母 ≈ 0.60×字号，拉丁 ≈ 0.55×字号，
   行高 ≈ 1.30×字号。任何一行文字上屏前都要先算宽度，否则就是压字或溢出。
8. **不要在 `Column` 里放 `Positioned`**（`renderBox.parentData must be StackParentData`）；
   `Column mainAxisSize="MIN"` 包定位层同样会炸。`Stack alignment="TOP_LEFT" fit="EXPAND"` + 绝对坐标最稳。
9. **绘制顺序就是图层顺序**：后画的盖住先画的。这是全套里代价最大的一条经验。
10. 相同 DSL 返回相同字节，可用于验证“图确实是这份 DSL 渲染的”。
11. 未遇到 429 或需要 `Retry-After` 的情况；出现的失败全部是请求体/DSL 层面的 400。

---

## 4. 跨题踩坑与修复（按代价排序）

| # | 坑 | 现象 | 修复 |
|---|---|---|---|
| 1 | **图层顺序** | A08 把墙格画在路线之后，穿过墙列的路线整段被盖住，两条路线看起来是一截截孤立横杠；一度误判为 `Transform` 旋转失效 | 先画背景与地块，再画路线，最后画文字；并用一个最小探针确认旋转本身是好的 |
| 2 | **BOM** | PowerShell `Set-Content` 写出的 DSL 开头带 BOM，服务报 `Not Support RAWTEXT: ` 于位置 0 | 统一用 `[System.IO.File]::WriteAllText(..., UTF8Encoding($false))` |
| 3 | **定位层放进 `Column`** | `renderBox.parentData must be StackParentData`；带定位层的多层嵌套会塌成几乎空白的小图 | 改为扁平单层 `Stack` + 绝对坐标 |
| 4 | **版本索引写错** | 多题出现「把层号当列号」或「把两行当成一页」的清单式索引错误，导致内容被推到画布外 | 索引一律由脚本从真实数据推导，并在生成器末尾写断言校验画布预算 |
| 5 | **文字宽度** | 带 `width` 的容器把两行文字挤成三行，压住相邻元素 | 上屏前按「CJK=1.00×、等宽=0.60×」估算并断言 |
| 6 | **`borderRadius` 多值** | `Attr [borderRadius] value format error` | 四角分别写属性 |
| 7 | **10 位颜色** | `Attr [border] color must be #RGB…` | 改成 8 位 `#RRGGBBAA` |
| 8 | **`padding` 元组** | `Attr [padding] value format error at position 92` | 写成 `"(24,32)"` |
| 9 | **请求 ID 冲突** | 不同题共用递增计数器导致重复 `request_id` | 每题独立前缀 `<TASK>-REQ` + 续号文件 + 去重脚本 |
| 10 | **图表数值算错** | 最短路/换乘数/统计量的口径错（把首次上车算成换乘、把站数当区间数、拼段时把一段漏掉） | 所有数字由独立脚本从原始输入重算，并把口径写进 JSON 的 `rules` 字段 |
| 11 | **纵向预算** | 侧栏按整幅高度排版，但实际可用高度只有网格高度，文字一路压行 | 把预算写成常量并在生成器里断言，超预算直接报错而不是悄悄压字 |
| 12 | **错误响应被丢掉** | `Invoke-WebRequest` 不保留错误正文，看不到真实原因 | 统一用 `curl.exe --data-binary` 并把错误体落盘 |

---

## 5. 可复现条件

- 服务：`POST https://open-snapshot.muedsa.com/snapshot`，无需凭据；限流 `x-ratelimit-limit: 120`。
- 渲染脚本：`tmp/<run_id>/_suite/shared/render.ps1`（`Invoke-Snapshot` / `Invoke-SnapshotText` /
  `Get-SnapshotFonts`），写 `requests.jsonl`，失败时写 `<png>.failed.txt`。
- 记账与状态：`tmp/<run_id>/_suite/shared/suite_common.py`、`suite_state.py`。
- 每题生成器：`tmp/<run_id>/<TASK>/gen_*.py`；每题所有 DSL 版本与失败响应都留在该目录，未被覆盖。
- 全套总装：`tmp/<run_id>/_suite/build_suite.py`，从磁盘上真实存在的文件重新生成
  `index.md` / `gallery.html` / `task-metrics.json`，不预填完成状态。

---

## 6. 总审查

### 6.1 由脚本扫描真实文件得出的结论

`tmp/<run_id>/_suite/build_suite.py` 不预填任何状态，它枚举 `outputs/<run_id>/` 下的每一个文件并据此生成
`index.md` / `gallery.html` / `task-metrics.json`；`reconcile_state.py` 用同样的方式核对 `suite-state.json`。
最终结果：

| 检查项 | 结果 |
|---|---|
| 题目完成 | **30 / 30** completed（0 in_progress / 0 partial / 0 blocked / 0 pending） |
| 最终 PNG | **126 张**，要求 ≥ 124；每题都达到 `catalog.json` 的最低张数 |
| PNG ↔ `.snapshot` 配对 | 126 / 126 配对，**0 个缺 DSL** |
| 每题报告与指标 | 30 / 30 都有 `snapshot-usage.md` 与 `task-metrics.json` |
| 输出目录残留 | 0 个 `.rawbody` / `.rawheaders` / `.rawmeta` 等服务中间文件 |
| 画廊覆盖 | 126 个 `<img>`、126 个链接，**全部本地相对路径、0 个远程引用、0 个 `<script>`**，磁盘上 126 张 PNG 全部被索引 |
| 多轮任务 | A21 / A22 各有 `round-01/02/03` 独立子目录，各轮 PNG + DSL + 指标齐全，未覆盖前轮，另有任务级累计报告与指标 |

### 6.2 真实消耗（`task-metrics.json`）

- **渲染请求 844 次**（成功 787 / 失败 57），全部来自各题 `tmp/<run_id>/<TASK>/requests.jsonl` 的逐行统计——
  每个真实 HTTP 请求一行，是主记录。
- 另有**共享准备请求 17 次**（文档抓取 13、`GET /fonts` 1、能力探针 3）记录在
  `tmp/<run_id>/_suite/shared/requests.jsonl`。**全部 HTTP 请求合计 861 次**。
- 57 次失败全部是**请求体层面的 4xx**（元素超 4096、裸 `<`、10 位颜色、`border` 缺样式段、
  内容超出尺寸上限等），失败响应正文都按题保留为 `*.failed.txt`；**未出现 429**，也没有因限流丢过请求。
- **DSL 版本 481 个**、**实际看图 380 次**、**迭代记录 427 条**。
- **指标一致性**：有 7 道题在最后一次渲染之前就写出了 `task-metrics.json`，自报请求数落后于日志
  （A21–A24、B05、B06 未填 `requests_total`，B03 报 94 而日志 93）。`normalize_metrics.py` 已把每题
  `requests` 段按日志校正，并把原值完整保留在 `requests_selfreported` 里；校正后 30 题的自报值与
  日志**完全一致**（0 处不一致）。
- **token / 图像输入计量 / 费用**：平台未提供，全部记 `null`，未用字符数或账号余量估算。
- 排队等待不可测，记 `null`；未发生 429，故「限流等待」为 0。

### 6.3 质量方面的实际判断

- 126 张最终图**每一张都由生成它的执行方用看图工具实际打开核对**，并且逐题在各自的
  `snapshot-usage.md` 里记录了「看图发现的具体缺陷 → 改了什么 → 再看的结论」。跨题统计到的真实缺陷
  类型包括：图层顺序导致图形被盖住、文字被容器宽度逼着换行、实体被当成转义序列印成 `&amp;`、
  坐标/索引算错把内容推出画布、图表数值口径错（把站数当区间数、把首次上车算成换乘）、
  右对齐列因字体宽度常数不准而抖动 19px 等。
- 主代理另外抽检了各条工作流的代表图（A09 变换图谱、A21 第三轮竖版、A23 分镜封面、B04 研究特辑等），
  确认与报告描述一致。
- 未解决事项**没有被隐去**：28 道题在 `suite-state.json` 的 `unresolved_issues` 里保留了具体条目
  （例如 A05 表体 17px 低于题面字面要求、A17 代码字号 18px 低于建议值、A20 仍保留 1 处允许的引线交叉、
  A22 的 −5,632 柱在共享比例尺下只有约 10px 高），并汇总在 `task-metrics.json` 的 `unresolved` 数组。

### 6.4 复现一遍需要注意的

1. 服务无需凭据，但**body 上限与 4096 元素上限**是硬约束，密集图要先本地数标签再发请求。
2. 文本节点**不会解码实体**；`&`、`>` 原样可写，裸 `<` 必须 CDATA，连续空格要用 `<Raw>`。
3. 字体宽度常数为实测值（等宽 0.5000 em/字符），用它排版才对得齐。
4. 一次渲染只对应一个 DSL 文件；最终 `.snapshot` 就是真实发出去的那份，不要事后修改。

---

## 7. 剩余事项与真实消耗

- **剩余事项**：30 题全部完成，没有阻塞或部分完成的题目。各题内部仍有 28 条如实记录的未解决事项
  （属于「可以更好」而非「未完成」），逐条列在各题 `snapshot-usage.md` 的「未解决事项」一节，
  并汇总在 `suite-state.json` 的 `unresolved_issues` 与 `task-metrics.json` 的 `unresolved` 数组。
- **真实消耗**：见 `task-metrics.json`——渲染请求 844 次（成功 787 / 失败 57，失败全部是 4xx 请求体问题，
  未出现 429）+ 共享准备请求 17 次 = **HTTP 请求共 861 次**；DSL 版本 481 个、实际看图 380 次、
  迭代记录 427 条、最终 PNG 126 张。
- token、图像输入计量与费用：平台未提供，全部记 `null`，未用字符数或账号余量估算。
- 未解决的**环境性**限制（已记录、不影响交付）：`BackdropFilter` 在本构建会作用于整幅已合成画面；
  单文档 4096 元素上限约束了生成式作品的密度；`Clip` 图层与绝对定位无法同时使用。

### 7.1 收尾审查中发现并补上的一处留痕缺口（如实记录）

总审查的最后一轮把目标拆成可验证条款逐条对文件复查，发现 **A18 / A19 / A20 三题缺
`tmp/<run_id>/<TASK>/iterations.jsonl`**（这三题的 `requests.jsonl` 与 `task-metrics.json` 都是完整的）。

处理方式：写 `tmp/<run_id>/_suite/rebuild_iterations_a18_a20.py` 从**已存在的证据**重建，而不是补写故事：

- 每条渲染迭代都直接取自该题 `requests.jsonl` 的真实字段（DSL 文件名、请求 ID、响应文件、真实时间戳、阶段）；
- 看图事实按该题 `task-metrics.json` 里原本就记录的 `image_reviews` 数量与 `image_reviews_note` 原样抄录；
- **没有新增任何一次没发生过的渲染或看图**；每题只写「已渲染的 DSL 各一条」+「一条已记录的看图汇总」；
- 每条记录都带 `reconstructed: true`，并注明哪些字段是日志真值、哪些（逐次看图的时刻、issue/change/result 叙述）当时没有记录、因此留 `null` 而不是事后编造。

因此现在的 `iterations.jsonl` 覆盖全部 30 题，但 A18/A19/A20 的记录**明确标注为事后重建**。
`task-metrics.json` 里的 `iterations_total` / `image_reviews_total` 仍取自各题自报的真实计数，未因重建而改动。
