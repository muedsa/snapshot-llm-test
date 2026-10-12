# 跨题 DSL 实测结论（shared）

path_base: suite_root。仅记录**真实请求/真实渲染**验证过的行为；未确认的写"推测"。
每题的原始请求与响应仍在各自 `tmp/<run_id>/<TASK>/requests/` 下。

## 请求与响应

- `POST /snapshot`，body 为 UTF-8 纯文本 DSL；成功时响应体直接是图片字节，失败时是
  JSON `{code,message,requestId}`（`A03-probe-*`、`A04-v01..v03` 均按此处理）。
- 响应头 `X-Request-Id`、`Server-Timing: render;dur=…, total;dur=…`、`X-Snapshot-Cache`
  可取得；`Server-Timing` 已写入各题 `requests.jsonl`。
- 同一 DSL 第二次渲染 `render;dur` 从 3458.7ms 降到 799.0/1019.5ms（A04 v02/v03），
  说明服务端有缓存，不据此减少请求。

## 画布与容器

- `<Snapshot width height>` 上的宽高被忽略；画布尺寸由根 `Container` 决定
  （探针：声明 1280×800 的 Snapshot + 200×100 Container → 输出 200×100 PNG）。
- 无内容/无约束时根 Container 会缩成 345×117 之类的小画布，因此最终图必须显式给
  根 Container 宽高。
- `padding`/EdgeInsets 接受 `"12"`、`"(8,16)"`、`"(8,12,16,20)"`；`"24 32"` → `PARSE_ERROR`。
- 未知属性与 kebab-case 属性被**静默忽略**（`font-size` 不报错也不生效，回落默认字号）。
- `borderRadius` 在没有 `color` 时不起作用，也不会裁剪子节点
  （`A03-probe-radius-nocolor-20261008T092557Z`）。
- `Expanded` 给子节点 TIGHT 约束，内部固定 `width` 被静默覆盖。
- `Positioned` 出现在 `Stack` 之外 → `RENDER_ERROR: renderBox.parentData must be StackParentData`。
- `Stack clipBehavior="NONE"` 时允许负 `Positioned` 偏移与溢出绘制；但**负偏移在裁剪包装
  容器里表现不稳定**（A03 经验：像素级几何以整图测量为准，局部放大只用于看纹理）。
- `Spacer flex="1"` 在 `Column` 中合法，但父级必须有界高度。

## 文字

- 字体串 `Inter,Noto Sans CJK SC` 可用；中文按 CJK 回退。
- **行距 ≈ fontSize × 1.45**（A04 v03 像素测量：22px 文本行墨迹高约 22px、行步进 32px；
  18px 行墨迹约 21px）。早期按 1.3 估算会导致多行文本被裁。
- **文本会被裁到其 `Positioned`/`Container` 盒子**：单行超宽时在盒子右边界截断（不显示
  省略号），多行超盒高时最后一行被横向切掉。因此段落盒高度必须 ≥ 行数 × 1.45 × fontSize，
  宽度必须 ≥ 最长行；A04 v01 的 ②③ 三处溢出即此原因。
- `Text height="1.1"` 确实控制行距：同一 22 号三行文本，默认行步进 32px（≈1.45×），
  加 `height="1.1"` 后行步进约 24px（`A04-probe-textheight-20261008T101005Z`，
  响应图 `tmp/<run_id>/A04/probe/textheight.png` 像素带 22/46/70）。密集正文可用它省高度。
- 居中方式：`Container alignment="CENTER"` + `Text textAlign="CENTER"`；
  左/右对齐用 `CENTER_LEFT` / `CENTER_RIGHT` / `TOP_LEFT` 等。
- **`Text` 内的 `<` / `>` 必须用 CDATA**（`A06-v01-20261008T105143Z` → HTTP 400
  `PARSE_ERROR: Unexpected character ' ' in input state [TAG_OPEN]`，位置正好指向含
  `layer(源) < layer(目标)` 的那一行）。文档 `parser.html`“文本中的特殊字符”明确：
  解析器**不做 HTML 实体解码**，`&lt;` 无效，要写 `<Text><![CDATA[…<…]]></Text>`。
  共享 `dslkit.esc()` 已改为自动判断（仅当文本含 `<`/`>` 时包裹），`A06-v02` 起渲染成功。
  同一节还说明：`Text` 会裁掉首尾空白，需保留原始空白要用 `Raw`。
- 字宽估算（CJK/全角 1.02em、数字字母 0.58em、空格 0.30em、U+2212 0.62em）在
  **恰好等于盒宽时会裁字**：A06 v02 图例第 2 项估算 329.6 / 盒宽 330 就被裁成
  “不参与 DAG 排”。门禁统一按 `盒宽 × 0.96` 试算换行，图例类横排改为按实测宽度顺序推进。

## 颜色与效果

- 8 位十六进制是 CSS `#RRGGBBAA`：`#33FFFFFF` 几乎不透明的青色，`#FFFFFF33` 是 20% 白。
- `ImageFiltered` 会模糊整个子树（含文字）；只模糊背景要用
  `ClipRRect` + `BackdropFilter sigmaX sigmaY`（A03 最终图即此方案）。
- `Transform` 只接受 `matrix`（列主序 4×4、16 个有限浮点、带括号、无空格）；
  `rotate` 属性 → `PARSE_ERROR: Attr [matrix] must not be null`。
- **旋转线段的对齐**（`A05-probe-diagonal-20261008T101451Z`，`tmp/<run_id>/A05/probe/diagonal.*`）：
  同一条 (40,180)→(160,40) 线段，`Transform matrix=…` 不带 `alignment` 在**嵌套**
  `Positioned > Stack > Positioned > Transform` 里整条不绘制（0 墨迹）；
  `alignment="CENTER"` 会平移到别处；只有 `alignment="TOP_LEFT"` 落在正确的两个端点上
  （实测左端 (41,177)、右端 (161,40)）。A01 的 sparkline 在**扁平** Stack 下不带
  `alignment` 也正常绘制（像素复核 5 段均有墨迹），因此统一改用 `TOP_LEFT` 更稳。
  `dslkit.line()` 已按此更新。

## 生成期自检方法

- 用像素检查代替肉眼断言：安全边距环计数、指定颜色的包围盒、面板边界外墨迹计数
  （A03 `check_geom.py`、A04 `check_overflow.py`），再用 Read 打开真实 PNG 目视确认。
- 放大局部只用于判断纹理/边缘，绝对几何以整图测量为准。
- **像素自检要覆盖“方向标记”而不是只看整图**：A06 v03 整图缩略看着正常，2× 放大才发现
  16 条边的箭头倒钩被画在行进方向前侧、落进目标节点内部被后画的节点完全遮住。修法是
  倒钩取 `tip − size·(cosθ, sinθ)`，并把折线两端吸附到节点真实边框（端点与框边的偏差
  会让箭头浮空或藏进框里）。
- **圆角盒上的装饰条要按半径内缩**：`borderRadius="12"` 的节点/卡片上直接画满宽的 6px
  色条（或满高的左侧强调条）会在圆角处外凸成直角。横向条内缩 `x+12 … w−24`，
  纵向条内缩 `y+12 … h−24`。
- **halo（越界墨迹）检查的窗口要小于相邻面板间距**：A06 图例与卡片只隔 6px，
  ±6px 窗口把卡片边框全算成图例越界（误报 1484 px），收紧到 ±3px 后为 0。
  同理，安全边距环要按 `max(M, x−6)` 夹住背景带，否则背景层会吃掉边距。

## A07 新增（网络示意图 + 出行卡片）

- **东亚“宽度含糊”字符按全角排版**：`①②③`（U+2460–U+2473）、箭头 `→`（U+2190–U+24FF）、
  几何图形 `■●`（U+25A0–U+25FF）在服务端字体里与汉字等宽。共享宽度模型原先只按
  `o >= 0x2E80` 判定全角，这类字符按 0.5em 估算，导致 A07 v01 图例末项
  “①②③＝三条查询旅程的起终点”被裁成“……的起”。`dslkit.TextFit.w()` 已把
  0x2190–0x24FF、0x25A0–0x25FF 与 CJK 同样按 `size * 1.02` 计入。
- **文字避让要按描边宽度外扩碰撞框**：`Line` 的 12px 描边以端点为中心，几何上“线段不穿过
  标签盒”并不等于“像素不落在标签盒上”。A07 v05 的像素自检在 S05 标签盒内检出 28 个
  绿线像素（线只切到盒角）。修法是把避让矩形四边各外扩 `stroke/2`（8px），并对经过的
  区间按 `trim_seg(..., 34)` 裁掉末端后再判交。
- **只裁“与标签所属站点相关联”的区间**：避让求解器若对所有区间都做端点裁剪，会误判可用
  槽位（A07 v02 有 4 个站因此无处放标签）。正确写法是 `if sid in (a, b)` 只对关联区间裁剪，
  其余区间用完整线段判定。
- **站点上的装饰记号要与该站区间方向错开**：缺无障碍设施的斜杠若与 45° 区间同向，会被
  后画的区间完全遮住（A07 v03 的 S05、S14 肉眼放大后确认消失）。改为枚举本站所有关联
  区间角度，在候选 45°/135° 中选“与所有区间的最小角距最大”的那个。
- **区间等长布局的可验证性**：把每跳长度锁成常量（200px，对角跳用 200/√2 的 dx/dy），
  就能用像素测距直接验证“图上相邻站耗时相同”这类需求；转折角断言用
  `min(abs(ang-v) for v in (0,45,90)) > 0.2`，不要用 `% 45`（浮点角差会让 45.00 误报）。
- **缓存与重复渲染**：DSL 未改动时服务端返回缓存命中（`X-Snapshot-Cache` /
  `cache;desc=hit`），因此无需为同一 DSL 重复请求。A07 用 `diff` 证明 v05/v06 卡面 DSL
  字节相同，只渲染一次并直接复用该响应作为交付图；保留原始响应字节即可。
