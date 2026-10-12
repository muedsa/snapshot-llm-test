# A03 · 多层语义故障恢复 — Snapshot 使用报告

## 完成状态

**completed** · 1 张最终 PNG，6 次渲染请求（2 成功 / 4 失败 / 0 重试），6 个 DSL 版本，5 次看图，1 次完整视觉迭代。

| 交付 | 路径 |
|---|---|
| 最终图 | `outputs/run-20261002-220723-mimo/A03/system-pulse.png` (1280×800, 41,456 B, PNG 签名校验通过) |
| 同名 DSL | `outputs/run-20261002-220723-mimo/A03/system-pulse.snapshot` (3,250 B) |
| 修复台账 | `outputs/run-20261002-220723-mimo/A03/repair-log.json`（12 项问题逐条对应位置/依据/修改/验证） |
| 指标 | `outputs/run-20261002-220723-mimo/A03/task-metrics.json` |
| 过程与留痕 | `tmp/run-20261002-220723-mimo/A03/`（v00–v05 全部 DSL、v04/v05 图、6 次放大图、`failures/` 4 个失败响应体、`requests.jsonl`、`iterations.jsonl`） |

原稿 `inputs/broken.snapshot` 未被改写；副本以 `broken-v00.snapshot` 提交。

## 真实文档应用

- **https://open-snapshot.muedsa.com/ai-guide.md**（本题内真实抓取）：确认请求体为 UTF-8 纯文本而非 JSON、`Content-Type: text/plain; charset=utf-8`、错误体含 `code/message/requestId`、400 PARSE_ERROR 应按消息位置修正、`X-Request-Id` 可关联服务日志、不要用 `?errorImage=png`。本题全部 4 次失败都靠这一条拿到了可操作的错误消息。
- **https://snapshot.muedsa.com/reference/parser-tags/**（本题内真实抓取）：逐条对照后定位了 5 类语义问题——
  - `#EdgeInsets`：`padding/margin` 只接受 `"12"` / `"(8,16)"` / `"(8,12,16,20)"`，括号逗号是语法的一部分 → 修 `padding="24 32"`。
  - `#Transform`：仅 `matrix`（必填，16 个列主序 Float，值间无空格）/`origin`/`alignment` 三个属性，**没有 `rotate`** → 修 `rotate="-8"`。
  - `#Positioned`：必须是 `Stack`/`IndexedStack` 的**直接子节点** → 修 Row 内 Positioned。
  - `#Snapshot`：仅 `background`/`debug`/`type`，**不含 width/height**（未知属性被静默忽略）→ 宽高下移到根 Container。
  - `#颜色`：8 位色现按 CSS `#RRGGBBAA` 解析，alpha 在**最后两位**（旧版才是 `#AARRGGBB`）→ 修 `#33FFFFFF`。
  - `#Text`：字号属性是 `fontSize`（区分大小写）→ 修 `font-size="44"`。
  - `#ImageFiltered`：对**子树整体**做高斯模糊 → 不能直接包裹含文字的卡片。
- 字体：本题无 CJK 文案，沿用全套已验证的默认字体族，未新查 `/fonts`（共享结果在 `_suite/requests.jsonl`）。

## 修复过程（4 次真实报错逐条推进）

| 版本 | 真实响应 | 依据 | 修改 |
|---|---|---|---|
| v00 | `400 PARSE_ERROR: Attr [padding] value format error at position 92` | #EdgeInsets | 原样提交（任务要求），记录响应 |
| v01 | `400 PARSE_ERROR: Attr [matrix] must not be null` | #Transform | `padding="(24,32)"` |
| v02 | `400 RENDER_ERROR: renderBox.parentData must be StackParentData` | #Positioned | 删 `rotate`，改列主序矩阵（逆时针 8°）+ `transformAlignment="CENTER"` |
| v03 | `400 RENDER_ERROR: Layout size is infinite` | #Snapshot/#Spacer | Row+Positioned 包进 `<Stack>` |
| v04 | `200`（首次可用图 1280×800） | — | 宽高从 `<Snapshot>` 下移到根 `<Container width="1280" height="800">` |
| v05 | `200`（最终） | 看图 + 像素测量 | 一次性修复 v04 暴露的 8 项视觉/语义问题 |

4 个失败响应体全部保留在 `tmp/.../A03/failures/*.body`，逐次失败稿与图片未删除、未覆盖。

## 静默忽略与视觉暴露问题（修完显式错误后继续排查）

1. **`Snapshot width/height` 被静默忽略** —— 解析期不报错，直到布局期才以 `Layout size is infinite` 暴露（问题 4/5）。
2. **`font-size="44"` 未知属性** —— v04 标题字形仅 h=13、宽 87px；改 `fontSize="44"` 后 h=42、宽 276px，约 3.2 倍差（问题 6）。
3. **`#33FFFFFF` alpha 位置** —— v04 中 REVIEW 底为不透明亮青，而非 20% 白；改 `#FFFFFF33` 后实测 (59,65,76) 对上理论 (59.8,65.4,76.6)（问题 7）。
4. **`rotate="-8"` 永不生效** —— 被必填 `matrix` 报错先行暴露；矩阵化后按包围盒宽 165（理论 166.2）+ 右高左低确认逆时针 8°（问题 8）。
5. **滤镜作用域错误** —— `ImageFiltered` 包整卡导致文字被模糊（问题 11）。
6. **单卡 vs 三等宽卡、LIVE 无标签盒、边距 24、说明卡未居中** —— 均为只在图像上暴露的问题（问题 9/10/12）。

## 标签能力与设计选择

- **背景专属模糊的三层结构**（本题核心设计）：卡外锐利细条 → `ClipRRect borderRadius="24"` 内叠不透明深底 + `ImageFiltered sigmaX=10 sigmaY=10` **只包裹细条副本** → 文字放在滤镜**之外**。这样细条穿过卡片两侧边界（卡外锐利、卡内模糊），文字始终清晰，无需 `BackdropFilter`（后者要另配裁剪且读取已有背景，语义更绕）。
- **旋转用 `Container.transform`** 而非 `Transform` 包裹：`transformAlignment="CENTER"` 让 160×56 绕自身中心旋转，位置用 `Positioned right/bottom` 锁在右下角。
- **三等宽卡**：`Row mainAxisAlignment="SPACE_BETWEEN"` + 三张 `width="389"` 卡，实测 389/390/389（1px 为像素取整）。
- **LIVE 遮挡校验**：标题字形止于 x310，LIVE 起于 x1152，水平间距 842px。
- **细条宽度算术**：卡 500 宽居中（390..889），细条 700 宽（290..989），左右各露出 100px，确定"同时穿过两侧边界"。

## 逐图自检（v05，全图 + 2 张放大 + 像素复核）

| 检查项 | 实测 | 结论 |
|---|---|---|
| 画布 | 1280×800 | ✅ |
| 底色/安全边距 | #0B1220；内容盒 x32..1247 / y32..766 → 32/32/32/33 | ✅ |
| 标题 44 字号 | 字形 y42..83 (h=42) | ✅ |
| 三等宽指标卡 | 389/390/389，文案齐全，字号 28（h=22） | ✅ |
| LIVE 96×36 不盖标题 | x1152..1247 (96) / y32..67 (36)；与标题间距 842px | ✅ |
| REVIEW 160×56 逆时针 8° | 旋转包围盒宽 165（理论 166.2），右高左低 | ✅ |
| REVIEW 20% 白底 + 不透明 24 字 | 底色 (59,65,76) = 理论 20% 白；文字满强度 | ✅ |
| 说明卡 500×150 圆角 24 | x390..889 (500) / y325..474 (150)，中心对齐画布中心 | ✅ |
| 细条穿两侧边界 | 700 宽 (290..989) vs 卡 500 宽 (390..889) | ✅ |
| 只模糊卡内背景、文字清晰 | 卡外锐利/卡内模糊；文字满强度像素 1223 vs 中等 603 | ✅ |
| 卡文案 28 字号 | 字形高 26px | ✅ |
| 各元素完整可见 | 内容盒完全在画布内，无裁切 | ✅ |

放大目视：`z01-blur-boundary.png`（细条跨越卡片边界的模糊突变）、`z02-review.png`（旋转标签与清晰文字）。

**v05 一次通过，未制造多余修改。**

## 实际问题、修复与验证

见上文表格与 `repair-log.json`（12 项，每项含原稿行号、真实报错/文档依据、具体修改、验证方法、类别real-error / silently-ignored / visual-only）。

## 未解决事项

无。最终 DSL 中不含任何"原样留着却未实现需求"的未知属性（`rotate`、`font-size`、`#33FFFFFF` 均已替换为文档有效形式）。

## 消耗

墙钟 1726 s；请求耗时之和 15,849.7 ms（6 次渲染往返）；首次可用图 410 s；限流/排队等待 0（未触发 429/503）；token/图像/费用：**null**（执行平台未提供，不估算）。
