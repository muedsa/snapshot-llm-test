# A15 Snapshot DSL 与工具使用说明

## 1 服务与请求

- 服务基址：`https://open-snapshot.muedsa.com`，渲染端点 `POST /snapshot`。
  请求体是 DSL 文本，成功时直接返回 PNG 字节流，失败时返回错误 JSON。
- 文档：服务指南 `https://open-snapshot.muedsa.com/ai-guide.md`，
  DSL 文档 `https://snapshot.muedsa.com/`。
- 全部真实请求记录在 `path_base=suite_root` 的
  `tmp/r20261014T1536+0800-5f11da/A15/requests.jsonl`，共 **17 条**，
  每条含 request_id、发起时间、HTTP 状态、耗时、响应字节数与失败原文。
  **失败响应没有清理、没有覆盖**，见第 5 节。

| 分类 | 次数 | 说明 |
|---|---|---|
| 成功（HTTP 200） | 9 | 8 次最终渲染 + 1 次排版探针页 |
| 失败 | 8 | 3 次 `PARSE_ERROR`（400）、3 次 180 s 读超时、2 次远端断开 |
| 合计 | 17 | |

最终交付渲染是 `req-a15-reconstructed-032fdf`（HTTP 200，119427 B）。
保存的 `reconstructed.png` 是**服务返回的原始字节**，没有做任何后处理。

同一 DSL 有时会被渲染两次以确认结果稳定：例如 `req-a15-reconstructed-b0d9fa-a3`
与 `req-a15-reconstructed-d6173b` 返回字节数完全相同（119142 B），那次重复渲染
是为了确认服务对同一 DSL 的输出可复现，不是设计迭代。

字体清单（Inter / Inter Light / Inter Medium / Inter Semi Bold / Inter Extra Bold /
Inter Extra Light / Inter Thin / Inter Black、Noto Sans/Mono/Serif CJK 各语系、
DejaVu Sans/Mono/Serif、Noto Color Emoji）来自服务文档，是之前题目真实取过并缓存的
结果，本题直接复用，没有重复计为新的 HTTP 请求。

## 2 DSL 构造：用什么搭出来的

DSL 是类 DOM 的 XML 风格，本次用到并**在真实响应中验证过**的属性：

| 属性 | 用法 |
|---|---|
| `<Snapshot type="png">` / `<Container>` / `<Stack>` / `<Positioned>` | 画布与绝对定位骨架 |
| `x` `y` `width` `height` `borderRadius` | 卡片、胶囊、表格底 |
| `borderRadiusTopLeft` / `borderRadiusTopRight` | 柱顶圆角——只作用于顶部两角，柱底保持直角 |
| `border="8 solid #64DBB6"` | logo 圆环的描边 |
| `shape="CIRCLE"` + `border` | 导航圆点（选中/未选） |
| `alignment="CENTER"` / `CENTER_LEFT` | 胶囊文字水平垂直居中、页脚左对齐 |
| `fontFamily` `fontSize` `color` `fontStyle="BOLD"` `letterSpacing` | 全部文字 |

两个几何模型是靠实测确认的，不是文档里明写的：

1. **CSS border-box 描边模型**：`border` 在盒**内侧**画，外轮廓恒等于
   `(x, y, width, height)`。所以 28×28 盒 + `borderRadius 14` + 8 px `border`
   得到外圆半径 14、内圆半径 6——正好是参考 logo 的实测值。如果描边是居中画的，
   会得到外半径 18、内半径 10，与参考明显不符。logo 圆环就是靠这个模型画出来的。
2. **`borderRadiusTopLeft/TopRight` 只影响顶部**：柱顶是圆角、柱底是直角。
   这个只在 4× 放大图（[review/09-bar-top-pair.png](review/09-bar-top-pair.png)）里才看得清，
   1.5× 下 6 px 圆角会误判成"没有圆角"。

## 3 三条必须靠探针确认的限制

这三条都是文档没写、只有发请求才知道的，所以先做了排版探针页
（`req-a15-probe-typography-c271d5-a2`，HTTP 200，108107 B）再定稿：

1. **服务不解码 XML 实体**：`&lt;`、`&amp;`、`&#34;` 都原样渲染成字符。
   危险字符只能靠不使用来规避。生成器里的 `esc()` 已改成 fail-fast：
   遇到 `<` `>` `&` `"` 直接抛错，而不是静默转义（转义了也无效，只会画出错误字符）。
2. **属性值里不能出现未转义的双引号**：会直接 `PARSE_ERROR`，
   报错位置在 `AFTER_ATTR_VALUE_QUOTED`。第一次探针就是因为把
   `fontFamily="Inter"` 写进了 `text` 属性，连续失败 3 次。
3. **字体度量必须实测**：Inter 的 cap height 0.727 em、ascender 0.734 em、
   descender −0.221 em 是先量出来的，再用探针页在 Inter BOLD 13/22/36 px 三档
   确认 `EM_INK_TOP = 0.32`（墨迹顶距字面框顶的比例，误差 ±0.5 px）。
   这个比例是把 `text_at` 的盒顶换算成墨迹顶的依据：
   `box_top = ink_top − 0.32 × font_size`。

## 4 定位与测量的工具链

不是用尺子量图，而是把参考位图和重建位图放在同一把尺下比较：

- **墨迹框**：ROI 内取「相对该元素底色最大色差的 50 %」作为阈值，去掉抗锯齿晕影。
  用固定 `tol=40` 会把晕影算成墨迹，字高偏大 3–6 px——这是踩过的一次。
- **文字色核心像素**：取 ROI 内 `|像素 − 底色|` 通道和最大处的像素。
  直接取最深/最饱和像素会命中抗锯齿边缘，真实 `#168267` 会被量成 `#0E7F67`。
- **三锚点定位**：`text_at`（左上）、`text_cx`（水平居中）、`text_r`（右锚）。
  `text_r` 必须满足「盒宽 = 墨宽 + PAD_X、盒左 = x_right − 墨宽 − PAD_X/2」，
  否则整行会右移半个墨宽。
- **前置校验**：生成器的 `checks()` 在渲染前跑一遍硬守卫，把曾经犯过的错假设
  变成拦路检查——logo 外框 `[30,33,57,60]`、`chart_ticks` 必须升序（否则 y 轴倒轴）、
  表头带与分隔线 `[284,...,1373,...]`、末行胶囊 `[1028,799,1175,826]` 等。
  `finals` 模式一旦校验不过就直接退出，不会产出错误图。
- **对照图**：审计器把参考与重建按区块裁出并上下拼成 pair 图（1× 到 4× 共 11 项），
  每张都实际打开看过，结论写进审计 JSON 的 `visual_reviews`。

## 5 失败响应原文（保留，未清理）

三条 `PARSE_ERROR` 的错误主体相同，都是把 DSL 语法片段写进了 `text` 属性：

```
PARSE_ERROR Unexpected character 'I' in input state [AFTER_ATTR_VALUE_QUOTED]
at position 421 near: r="#63748F" text="fontFamily="Inter"   fontStyle="none"" />
```

另外的失败是服务端稳定性问题，不是 DSL 问题：

```
read timeout after 180s: The read operation timed out        ×3
RemoteDisconnected after 43.4s: Remote end closed connection without response
RemoteDisconnected after 27.3s: Remote end closed connection without response
```

这些请求重试后都成功了；对应时间戳和耗时在 `requests.jsonl` 里逐条留档。

8 次失败里有 5 次是**逐字节相同的 DSL 重发**：坏探针 DSL 连发 3 次（6126 B，diff 全为 0 行），
小字号校准版 DSL 连发 3 次（19688 B）。连发 3 次坏 DSL 是判断失误——错误定位、位置号、
状态码三次完全一致，说明这是确定性语法错误，重发不会变，该改生成器。第 4 次才改。

另有一次**不是服务失败**的失败，记在这里以免看起来像漏记：首版渲染 `b0d9fa-a3`
已经 HTTP 200 返回 119142 B，写盘时抛 `FileNotFoundError`，因为
`outputs/<run_id>/A15/` 目录当时还不存在（见 `_suite/gen/a15_finals.log` 末尾的 traceback）。
建目录后重写，响应字节没有丢失、没有被覆盖。

17 次请求归档了 17 份 DSL（`tmp/<run_id>/A15/dsl/`），去重后是 9 份不同的 DSL 文本；
每次请求单独落盘，重试不覆盖旧版。

## 6 跨题经验（本题新学到的）

- **审计窗口不能越过被测元素的父容器**：表头带与页面底色同为 `#F3F6FB`，
  窗口右界一旦越过卡片右缘，卡外底色就命中同一个掩码，`top/bottom/right` 三个分量
  全部顶到窗口边缘，误差恒为 0——看起来"完全通过"，实际什么都没测。
- **同色掩码不能直接取外接框**：文字抗锯齿晕影里有很多像素落在带色 ±6 内，
  散在标题行与行首，外接框会把 `top` 拉早 25 px。改成先按「整行填充率 ≥ 60 %」
  筛出目标行，再在这些行里取列范围。
- **窗口里混进别的元素的抗锯齿混色**：导航选中底的窗口下界若放到 190，
  会把第 2 行文字 `Projects` 的混色算进选中框，实测框到 y=205；
  收紧到 186 后才量出正确的 `[18,116,201,163]`。
- **像素统计发现不了的语义错误**：y 轴倒轴（0 画到最顶）在锚点审计里完全正常，
  因为锚点只测零线左端点。只有把参考与重建并排看图才发现。
  几何容差通过绝不等于语义正确。
- **1× 看不出的宽度差**：表头带多画 25 px 在 1× 整页并排里几乎看不出，
  是收紧审计窗口后才量出来的。1× 看图和像素测量缺一不可。
- **采样点要落在纯色区域**：主蓝原采样点 (1330,71) 落在按钮白色文字上，
  重建图量成 `(247,249,254)`，看着像差了一整个色相；改到按钮内缘 (1200,71) 后两侧都是
  `(36,92,228)`。给"按钮 = 柱体同色"这类说法加了柱体采样点 (888,500) 单独验证，
  而不是只写一句备注。

## 7 复现

```
python -I tmp/<run_id>/_suite/gen/a15_pages.py  finals   # 前置校验 → 渲染 → 写图与 DSL
python -I tmp/<run_id>/_suite/gen/a15_audit.py                 # 锚点/字形/颜色/对照图
```

`run_id` 从脚本所在路径向上派生（`HERE.parents[2].parent.name`），
`SNAPSHOT_RUN_ID` 也从同一路径取，不写死盘符或仓库位置。
生成脚本、诊断脚本、对照图裁切、`layout.json`、`color-samples.json`、
审计运行日志都在 `path_base=suite_root` 的 `tmp/r20261014T1536+0800-5f11da/` 下，未清理。

## 8 未完成或无支撑的部分（如实说明）

- 字重归因探针 `a15_diag11.py` **已写好但本轮未运行**，所以没有字重的渲染证据；
  字号是按本服务实际渲染墨宽逐项校准的，不宣称判定出了参考的字重。
- 没有做逐像素差异图。题面不要求，而且参考位图的抗锯齿与字体度量差异会让
  逐像素差异图充满噪声、反而掩盖真正的位置与比例问题。
- 题面明确不要求 DSL 树与参考来源一致，也没有声称逐像素复刻。
