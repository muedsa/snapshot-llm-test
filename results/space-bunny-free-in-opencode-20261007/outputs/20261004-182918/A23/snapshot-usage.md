# A23 · snapshot-usage.md

| 项 | 值 |
|---|---|
| 题目 | A23 · 格式边界下的动画分镜交付 |
| 状态 | **completed** |
| 主题 | 结构汇聚成图像（structure converges into an image） |
| 输出目录 | `outputs/20261004-182918/A23/` |
| 临时目录 | `tmp/20261004-182918/A23/` |
| 服务 | `POST https://open-snapshot.muedsa.com/snapshot`（snapkit 自带浏览器 UA，未使用任何凭据） |
| 渲染请求 | 57 次（成功 53 / 失败 4 / 重试 0） |
| 文档与字体请求 | 7 次（6 文档 + 1 字体列表），全部本题实际抓取 |
| 最终 PNG | 8 张（题目要求 7 张 + 附加接触表 1 张） |
| 看图次数 | 18 次 |
| 迭代记录 | 18 条（baseline 3 / visual 6 / syntax-fix 2 / alternative 7） |

---

## 1. 交付文件清单

| 文件 | 尺寸 | 实测格式 | 说明 |
|---|---|---|---|
| `cover.png` | 1200×800 | PNG，RGBA 容器但 alpha 全 255（不透明） | 题目要求 |
| `cover.snapshot` | 37 034 B | UTF-8 纯文本 DSL | 与 PNG 同一次渲染的请求体 |
| `frame-01.png` … `frame-06.png` | 均 600×600 | PNG / RGBA，四角 alpha = 0（真透明） | 题目要求 |
| `frame-01.snapshot` … `frame-06.snapshot` | 3 491–3 669 B | UTF-8 纯文本 DSL | 同上 |
| `contact-sheet.png` | 980×792 | PNG / 不透明 | 附加自检证据（6 帧接触表） |
| `contact-sheet.snapshot` | 25 763 B | UTF-8 纯文本 DSL | 同上 |
| `limitations.md` | — | Markdown | 格式边界逐项说明 |
| `frame-data.json` | — | JSON | 逐帧 12 单元坐标与状态 |
| `timing.json` | — | JSON | 250 ms/帧、循环、帧序、接缝分析 |
| `snapshot-usage.md` | — | Markdown | 本文件 |
| `task-metrics.json` | — | JSON | 由 `finalize.build()` 生成 |

所有 PNG 都是服务响应体的**原始字节**，未做任何后处理、缩放或再编码。
验证方式：8 张图渲染两次，sha256 逐一比对，**全部字节相同**（见 §6 第 3 行）。

---

## 2. 实际使用的服务文档与字体

**全部为本题实际抓取**（不是复用本题库其他任务的缓存），落盘在 `tmp/20261004-182918/A23/docs/`：

| 文档 | 状态 | 用途 |
|---|---|---|
| `open-snapshot.muedsa.com/ai-guide.md` | 200 | 确认 `type` 枚举、请求体是纯文本非 JSON |
| `open-snapshot.muedsa.com/openapi.yaml` | 200 | 确认响应只有 `image/png` / `image/jpeg` / `image/webp` |
| `snapshot.muedsa.com/guides/rendering/` | 200 | 确认输出入口只有 PNG/JPEG/WebP；**Parser 的 `<Snapshot>` 默认背景是透明** |
| `snapshot.muedsa.com/reference/parser-tags/` | 200 | 确认 38 个标签全集、`Snapshot` 属性表、颜色只有 CSS 写法 |
| `snapshot.muedsa.com/guides/parser/` | 200 | 解析器行为与错误处理 |
| `snapshot.muedsa.com/guides/media-text/` | 200 | 图片与文本能力边界 |
| `open-snapshot.muedsa.com/fonts` | 200 | **27 个字体族**，实际清单存 `tmp/.../A23/fonts-list.txt` |

实际用到的字体（全部在 `/fonts` 返回清单内，无臆造）：
`Noto Sans CJK SC`（封面标题与全部中文）、`Inter,Noto Sans CJK SC`（中英混排）、
`DejaVu Sans Mono`（FRAME 标签、progress、错误码等拉丁小字）。

7 次访问在 `requests.jsonl` 中以 `request_type = document` / `font_list` 记录，
与渲染请求分开统计。

---

## 3. 实际用到的标签与属性

| 标签 | 用到的属性 | 用途 |
|---|---|---|
| `Snapshot` | `type`、`background` | `type="png"`；关键帧 `background="#00000000"` |
| `Container` | `width`/`height`/`color`/`borderRadius`/`gradientType`/`gradientColors`/`gradientBegin`/`gradientEnd` | 全部矩形、圆角单元、封面渐变底 |
| `Stack` | `fit="EXPAND"` | 整屏绝对定位层 |
| `Positioned` | `left`/`top`/`width`/`height` | 每个单元的精确坐标 |
| `Transform` | `matrix`、`origin="(0,0)"`、`alignment="CENTER"` | 12 个单元的逐帧旋转 |
| `Text` | `text`/`color`/`fontSize`/`fontFamily`/`letterSpacing`/`textAlign` | 封面全部文字 |
| `BoxDecoration`（`Container` 的 `border`/`boxShadow`） | `border="1 SOLID #..."`、`boxShadow="0 6 24 0 #00000059"` | 封面卡片 |

**未使用**：`<Image>`（0 次，DSL 中 `image_tag_count = 0`）、`<Emoji>`、`<Raw>`、
`<Span>`、`<WidgetSpan>`、网络图片、Data URI、外部素材。

### 本题踩到的 DSL 语义坑

1. **`text` 属性值里不能有英文双引号。** 文案 `→ 原生 type="png"，...` 导致
   `HTTP 400 PARSE_ERROR: Unexpected character 'p' in input state [AFTER_ATTR_VALUE_QUOTED] at position 9997`。
   共享库 `dsllib.esc()` 只转义 `& < >`，不转义引号，所以辅助函数不会拦住它。
   修法：文案改为 `type=png`。**这是本题遇到的唯一一次真实服务错误**（其余 3 次 400 是
   故意做的能力探针）。
2. **`Transform` 绕自身中心旋转的写法必须实测确认。** 手册只给了
   `origin="(0,0)" alignment="CENTER"` 的例子，没说 pivot 在哪。我渲染了 0/30/60/90° 四个
   胶囊叠加未旋转参考框，量红色像素包围盒：依次 120×40 / 108×80 / 80×109 / 40×120，
   **质心恒为 (99.5,99.5) 与 (699.5,99.5)**，证明确实绕子节点中心旋转，
   且屏幕 y 向下时该矩阵表现为逆时针。6 帧的朝向公式据此定稿。
3. **等宽字体的步进约 0.602em，`dsllib` 的 0.55em 估算偏低。** 封面 eyebrow 用
   `DejaVu Sans Mono` + `letterSpacing`，估算器没告警，但实际 56 字符约 573px 超出
   520px 的框，**末词 "DELIVERY" 被静默丢弃**。修法：缩短文案并把框宽放到 600px。
   教训：等宽 + `letterSpacing` 的文本必须手工留余量，不能只信 `D.warnings()`。
4. **透明背景是真实 alpha。** 手册明确「Parser 的 `<Snapshot>` 默认背景则为透明」，
   我又实测：不写 `background` 与写 `background="#00000000"` 的输出**字节完全相同**，
   四角 RGBA 为 `(0,0,0,0)`，alpha 极值 0…255。
5. **未知属性被静默忽略**（复现了手册第 3 节）：`frames`/`frameDuration`/`loop`/`animated`/
   `colorSpace`/`profile`/`cmyk`/`path`/`strokeWidth`/`vectorOutput` 全部返回
   `HTTP 200` 且无任何效果。这是判定"服务不支持动图/CMYK/矢量"的关键证据——
   不是报错了，而是**根本没有这个能力**。

---

## 4. 逐项自检表

### 4.1 题目硬指标

| # | TASK.md 要求 | 实际值 | 结论 |
|---|---|---|---|
| 1 | `cover.png` 1200×800 | PIL 实测 1200×800，`size_ok=true` | ✅ |
| 2 | 封面 RGB（不透明） | alpha 全 255，`fully_opaque_canvas=true`，`opaque_pixel_ratio=1.0` | ✅ |
| 3 | 6 张 600×600 关键帧 | 6 张全部 PIL 实测 600×600，`matches_task_json_size=true` | ✅ |
| 4 | 关键帧透明背景真实 | 6 张四角 RGBA 全 `(0,0,0,0)`；`opaque_pixel_ratio` 0.057–0.064（非 1.0） | ✅ |
| 5 | 每张 PNG 有同名 `.snapshot` | 8/8 配对，且 8 个草稿与交付 DSL **逐一字节相同** | ✅ |
| 6 | 「从结构到画面」在封面可读 | 72px `Noto Sans CJK SC`，放大 1.9x 复核清晰无裁切 | ✅ |
| 7 | 帧内不含文字 | 6 个帧 DSL 的 `text_node_count = [0,0,0,0,0,0]` | ✅ |
| 8 | 始终存在 12 个几何单元 | 6 个帧 DSL 的 `unit_node_count = [12,12,12,12,12,12]` | ✅ |
| 9 | 由分散逐步汇聚 | alpha 包围盒逐帧单调收缩 524×502 → 487×457 → 453×407 → 414×400 → 370×389 → 332×376 | ✅ |
| 10 | 末帧构成可识别图形 | 6 瓣花 / 光圈：6 根胶囊花瓣 + 6 块核心方砖围出中心光圈 | ✅ |
| 11 | 各帧颜色/数量/尺度一致 | 数量 12 恒定；颜色 12 个恒定；unit 几何集合 6 帧完全一致（`42.0x42.0 r10.0` + `76.0x34.0 r17.0`），无缩放无透明度变化 | ✅ |
| 12 | 单元轨迹连续、无突然消失 | 相邻帧位移实测 26.14–43.92px，中位 34.33px，无跳变；12 单元全程在场 | ✅ |
| 13 | 可复用参数生成 DSL，不嵌预渲染帧 | 封面缩略图与接触表缩略图由同一 `frame_state()` 按不同缩放重算；`image_tag_count=0` | ✅ |
| 14 | `timing.json` 表达 250ms/帧、循环、帧序 | `duration_per_frame_ms=250`、`total=1500ms`、`playback_mode=loop`、6 帧 `start_ms`/`end_ms` | ✅ |
| 15 | 不宣称无缝，或给无缝证据 | `seamless: false`，并给出实测接缝位移与数学不可能性推导 | ✅ |
| 16 | 逐帧和接触表看图检查 | 6 帧逐张打开 + 接触表打开 + 4 张放大核对 | ✅ |
| 17 | 附 `limitations.md` / `frame-data.json` / `timing.json` | 三个文件均在输出目录 | ✅ |
| 18 | 只用 `POST /snapshot`，不嵌位图 | 57 次渲染全部走同一端点；`Image` 标签计数 0 | ✅ |
| 19 | 不合成 GIF / 不矢量化 / 不转 CMYK / 不造假文件 | 未做；输出目录无任何 `.gif`/`.svg`/`.tif`/`.pdf` | ✅ |
| 20 | 如实说明格式边界 | `limitations.md` 逐项给出请求/支持/依据/替代/外部后续 | ✅ |

### 4.2 逐图自检

| 图 | 尺寸 | 格式 | 关键实测 | 视觉确认 |
|---|---|---|---|---|
| `cover.png` | 1200×800 ✅ | PNG 不透明 ✅ | alpha 全 255 | 标题/副标题/正文/能力卡 4 行/6 缩略图/轴线/页脚全部可读，无重叠无裁切 |
| `frame-01.png` | 600×600 ✅ | PNG RGBA ✅ | 四角 alpha=0，bbox 524×502 | 12 单元散开成环，中心留空 |
| `frame-02.png` | 600×600 ✅ | PNG RGBA ✅ | 四角 alpha=0，bbox 487×457 | 成对单元开始靠拢 |
| `frame-03.png` | 600×600 ✅ | PNG RGBA ✅ | 四角 alpha=0，bbox 453×407 | 明显收拢，出现交叠（不透明像素 20 643 为全程最低） |
| `frame-04.png` | 600×600 ✅ | PNG RGBA ✅ | 四角 alpha=0，bbox 414×400 | 接近圆形，单元开始转向 |
| `frame-05.png` | 600×600 ✅ | PNG RGBA ✅ | 四角 alpha=0，bbox 370×389 | 接近到位 |
| `frame-06.png` | 600×600 ✅ | PNG RGBA ✅ | 四角 alpha=0，bbox 332×376 | **6 瓣花/光圈成形**，两环分离，中心光圈空隙清晰 |
| `contact-sheet.png` | 980×792 ✅ | PNG 不透明 ✅ | 6 格 + progress/step 标注 | 一眼可比：progress 0.000→1.000 等距，step 31.1/34.3/38.3/38.3/34.3/31.1 均匀 |

### 4.3 放大核对

| 放大 | 倍率 | 用途 | 发现 |
|---|---|---|---|
| `frame-06` 中心 400×400 | 1.6× | 检查末帧图形 | **v1 缺陷**：6 块核心方砖互相重叠糊成一团，两环相撞 |
| `frame-05` 中心 280×280 | 1.8× | 检查中途交叠是否可接受 | 交叠明显但每个单元仍可分辨，可接受 |
| `cover` 能力卡 446×372 | 1.9× | 检查卡片文字 | **v1 缺陷**：第 4 行替代文案压住两行脚注 |
| `cover` 缩略图带 652×280 | 1.7× | 检查缩略图与轴线 | **v1 缺陷**：轴线圆点压住 progress 标签 |

---

## 5. 问题与修复表

| # | 问题现象 | 定位方式 | 修复方式 | 复验结果 |
|---|---|---|---|---|
| 1 | 末帧 6 块核心方砖重叠糊成深色团块，两环相撞 | 放大 `frame-06` 中心 1.6×，量出方砖对角线 46√2=65.1 > 相邻中心距 2·52·sin30°=52 | `R_CORE` 52→68、方砖 46→42（68 > 42√2=59.4）；`R_PETAL` 136→150、花瓣 96→76（内缘 112 > 砖外缘 97.7）。并把两条几何约束写成脚本里的 `assert` | 复看 `frame-06`：六块方砖组成干净六边形环，中心留光圈空隙，两环有可见间隙 |
| 2 | 逐帧对比几乎看不出在动 | 逐张打开 6 帧并横向对比，测出单元总行程仅约 74px 径向、不足一个单元长度 | 散布改为「炸开 +42°/−42° 交错」：花瓣起始角 = 轴角+42°±3°、半径 228–244；方砖起始角 = 轴角−42°±3°、半径 224–240；弯曲系数 ±0.30→±0.16 | 相邻帧位移实测 26.14–43.92px（中位 34.33px），逐帧变化清晰可读 |
| 3 | 封面 eyebrow 末词 "DELIVERY" 整段消失 | 打开 `cover.png` 发现；`D.warnings()` 未告警。测得 DejaVu Sans Mono + `letterSpacing` 实际约 573px 超出 520px 框 | 文案缩短为 `OPEN-SNAPSHOT · FORMAT-BOUNDARY DELIVERY`，框宽 520→600，`letterSpacing` 1.2→1.0 | 复看 `cover.png`：eyebrow 完整显示 |
| 4 | 封面能力卡第 4 行压住两行脚注 | 放大能力卡 1.9× | 卡片高 356→372、行距 70→62、整块上移，脚注重排到卡片底部留白内 | 复看：4 行与 2 行脚注互不重叠 |
| 5 | 收敛轴圆点压住缩略图 progress 标签 | 放大缩略图带 1.7× | 缩略图卡改到 y=428/高 210、`THUMB` 152→148；轴线下移到 y=652、说明文字下移到 y=664 | 复看：轴线、圆点、标签、两端说明全部清晰 |
| 6 | `HTTP 400 PARSE_ERROR ... AFTER_ATTR_VALUE_QUOTED at position 9997` | 服务错误原文直接指出 `text="→ 原生 type="png"` | 文案改为 `type=png`（去掉属性值内的双引号） | 重渲染 HTTP 200，封面正常出图 |
| 7 | **我自己的 `draft()` 辅助函数有 bug**：文件名漏 `.snapshot` 后缀，而编号又用 `glob("*.snapshot")` 计数，导致每次运行都覆盖 `v01-*` | 交付前核对 `drafts/` 时发现所有文件都是 `v01-*` | 改为写 `vNN-<name>.snapshot`，用正则 `^v(\d+)-.*\.snapshot$` 取最大编号+1；清掉旧的无后缀文件后重跑，得到 v01–v08 完整序列 | 8 个最终草稿与交付目录 `*.snapshot` 逐一字节相同。**损失范围与未重建项已在 `tmp/.../A23/drafts/README.md` 中写明** |
| 8 | 探针脚本读 `/fonts` 用 `.split()` 导致 `Noto Sans CJK SC` 判断为不存在 | 打印 `split tokens 93` 而文件只有 27 行 | 改用 `.splitlines()`；字体本身没问题 | 确认真实清单 27 个字体族，含 `Noto Sans CJK SC` |
| 9 | `emit_a23.py` 用 `re.findall(r'color="#[0-9A-F]{6}FF"')` 匹配不到单元几何（实际 DSL 写 6 位不带 alpha） | 打印 `unit geometry set: []` | 正则改为 `#[0-9A-Fa-f]{6,8}` | 输出 `['42.0x42.0 r10.0', '76.0x34.0 r17.0']` |

---

## 6. 复验与可重复性

| 项 | 方法 | 结果 |
|---|---|---|
| 服务确定性 | 记录 8 个 PNG 的 sha256 → 用同一 DSL 重跑 `build_a23.py all` → 重算 sha256 | 8/8 **字节完全相同** |
| 草稿一致性 | `drafts/v01…v08` 与输出目录 `*.snapshot` 逐文件字节比对 | 8/8 相同 |
| 帧内容一致性 | 从交付 DSL 统计 `unit_node_count` / `text_node_count` / `image_tag_count` / 几何集合 | 12 / 0 / 0 / 6 帧一致 |
| 帧收敛性 | 从交付 PNG 测 alpha 包围盒 | 6 帧单调收缩，最大帧最小帧相差 192×126px |
| 帧连续性 | 相邻帧逐单元位移 | 26.14–43.92px，最大帧间旋转步长 36.05° |

**关于 `frame-03` 不透明像素偏低（20 643 vs 其余约 23 000）**：这不是缩放或淡出。
12 个单元面积之和恒为 24 084.5 px²（由几何参数算出），而实测的是 12 个形状的**并集**，
在中途交叠最多的第 3 帧自然偏低。脚本中已把这段解释写进
`frame-data.json → measured_ink_evidence.opaque_pixel_count_interpretation`。

---

## 7. 未解决事项与如实说明

1. **循环不无缝，如实标注。** 按题目要求第 1 帧分散、第 6 帧成图，6 帧循环播放时
   `frame-06 → frame-01` 存在一次大跳：实测接缝位移中位 **171.0px**，是常规相邻帧步长
   （中位 34.33px）的 **4.98 倍**。已在 `timing.json → loop_seam` 写 `seamless: false`，
   并给出三条外部后续方案（延长末帧停留 / 增加第 7 帧 / 接缝交叉淡化）。
   **本交付不宣称无缝。**
2. **6 帧无法同时满足"第 1 帧分散 + 第 6 帧成图 + 无缝"，这是数学结论不是偷懒。**
   闭合曲线按 t 与 t+1/6 采样必然 `P(t)=P(1)`；若第 1 帧分散、第 6 帧成图，则整段行程
   要压进一个帧间隔内，无法按 6 个等步长采样。推导写在
   `timing.json → loop_seam.why_a_seamless_loop_is_impossible_here`。二选一时我选择满足
   题目明确写出的首末帧要求，并如实说明接缝跳变。
3. **未合成 GIF / 未矢量化 / 未转 CMYK / 未生成假的目标格式文件。** 服务不支持，
   且题目明确"不要求额外工具导出格式"。合成环节留给客户，路径写在 `limitations.md`。
4. **矢量与 CMYK 需客户决策。** 若客户不接受"PNG + 完整 DSL"作为最终交付，
   需另立预算在 Snapshot 之外复刻矢量版与做印前转换。
5. **帧率。** 250ms/帧 = 4fps 是题目指定值。若要 30fps 平滑播放需外部补间或更多关键帧；
   生成器 `build_a23.py` 的 `N_FRAMES` 可直接改，DSL 生成逻辑无需重写。
6. **平台计量全部为 `null`。** 服务未暴露 token / 计费指标端点，对话平台也未报告
   本次的 token 或费用数字，因此 `task-metrics.json` 中 `input_tokens` / `output_tokens` /
   `image_input_usage` / `cost` / `currency` 一律 `null`，**没有按字符数或请求数估算**。
7. **`Server-Timing` 与排队等待。** 本次所有响应的 `Server-Timing` 头均未返回，
   `rate_limit_or_queue_wait_seconds` 记为 `null` 而非 0（未确认发生，只能记未知）。
8. **`Server-Timing` 之外的可测耗时**：57 次渲染 + 7 次文档请求的耗时之和
   **88.9 秒**，而本题墙钟 **2 087.7 秒**。差额是本地设计、DSL 编写与看图迭代的时间，
   两者不可互相替代。
9. **草稿覆盖事故（我方工具缺陷）。** 见 §5 第 7 项与 `drafts/README.md`：
   v1/v2 版 6 帧 DSL 与旧版封面 DSL 的**草稿副本**曾被覆盖。权威记录
   （`requests.jsonl` 48+ 条、`responses/` 错误原文、`preview/` 14 张探针图、
   `iterations.jsonl` 18 条）均完整保留；旧封面 DSL 已精确重建为
   `v00-cover-reconstructed-PARSE_ERROR-quote.snapshot`（重建前对 `A23-req-037`
   错误原文做了断言校验）；**v1 版 6 帧 DSL 未重建**，因为凭记忆补一个冒充历史请求体的
   `.snapshot` 是不诚实的。

---

## 8. 目录与文件路径

```
outputs/20261004-182918/A23/
  cover.png / cover.snapshot
  frame-01.png … frame-06.png / frame-01.snapshot … frame-06.snapshot
  contact-sheet.png / contact-sheet.snapshot
  limitations.md / frame-data.json / timing.json
  snapshot-usage.md / task-metrics.json

tmp/20261004-182918/A23/
  requests.jsonl            57 次渲染 + 7 次文档/字体请求的真实记录
  iterations.jsonl          18 条迭代台账
  probe_format.py           10 次能力边界探针
  probe_semantics.py        4 次语义探针（旋转/透明/CJK）
  build_a23.py              单一参数集 → 6 帧 + 封面 + 接触表
  emit_a23.py               从同一参数集与交付文件生成两个 JSON
  recover_draft.py          精确重建被覆盖的旧封面 DSL（含断言校验）
  log_a23.py                迭代台账 + wrapup
  docs/                     6 份实际抓取的文档
  fonts-list.txt            实际字体清单（27 族）
  preview/                  14 张探针图 + 14 份探针 DSL
  responses/                4 次 400 的完整 JSON 错误原文
  drafts/                   v00（重建）+ v01–v08 共 10 份 DSL + README.md
  crops/                    4 张放大核对图
```
