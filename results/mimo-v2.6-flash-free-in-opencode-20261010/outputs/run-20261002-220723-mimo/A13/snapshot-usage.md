# A13 叠光 / Layerlight — snapshot 使用记录

- run_id: `run-20261002-220723-mimo`
- 服务: `POST https://open-snapshot.muedsa.com/snapshot`，UTF-8 纯文本正文，`Content-Type: text/plain; charset=utf-8`
- 时间窗: 2026-10-03T15:54:10+08:00 起（任务开始），首个请求 2026-10-03T07:59:34.601Z，末个请求 2026-10-03T08:47:39.664Z
- 本题请求: 20 次，全部 HTTP 200，0 次失败，0 次重试，请求耗时合计 40998.6 ms

## 实际读取的资料

| 资料 | 来源 | 用途 |
| --- | --- | --- |
| `tasks/A13-brand-delivery/TASK.md`、`AGENTS.md`、`task.json` | 题库 | 交付表、两图标几何相同、禁用现成 logo / 外部图 / 文字当图标、≤6 个几何构件、32×32 可识别 |
| `tasks/A13-brand-delivery/inputs/README.md`、templates | 题库 | `brand-system.json`、`rationale.md` 结构参考 |
| `run-config.json`、`catalog.json` | 总根 | 服务地址覆盖子题默认值、task_order |
| AI 指南与 DSL 文档摘录 | `tmp/.../_suite/probe/A10-doc-excerpts.md`（套件已缓存的真实响应） | `POST /snapshot` 形式、颜色语法（`#RGB`/`#RGBA`/`#RRGGBB`/`#RRGGBBAA`，alpha 在末位）、`<Snapshot>` 根节点 |
| `/fonts` 列表 | `tmp/.../A11/fonts-0001.txt`（套件共享请求，字节等同 shared-fonts-0001） | 确认 `Noto Sans CJK SC/JP`、`Noto Sans Mono CJK SC` 可用 |

本题未新增文档 HTTP 请求；以上为套件内已真实取得并可复用的结果。

## 为本题新增的真实探测（5 次渲染）

| 探针 | 结论 |
| --- | --- |
| `probe-alpha-none` | `<Snapshot>` 省略 `background` ⇒ 整张画布 alpha=0，可直接做透明图标 |
| `probe-alpha-explicit` | `background="#00000000"` 与省略等价 |
| `probe-black` | 透明底上画 `#000000` ⇒ 所有 A>0 像素 RGB 均为 0（11320 个墨点，0 违例），抗锯齿只体现在 alpha，满足"纯黑"硬约束 |
| `probe-decimal` | `left/top/width/height/borderRadius` 支持小数，图标可按任意倍率重新发射到应用里 |
| `probe-overlap` | 半透明叠加遵循 source-over：`#38BDF8CC` 盖 `#F6B94ACC` 实测 (214,185,103) A=245，预测 (214,186,103) A=245 |

## 实际应用的 DSL 造法

- 结构：`<Snapshot type="png" background="..."> > <Container> > <Stack> > <Positioned> > <Transform> > <Container>`。
- 标记几何只在一个函数里定义（`Get-Bars(box, ox, oy, cA, cB, cC)`）：`k = box/512`，胶囊 `256×88 / r=44`，45° 旋转矩阵
  `(0.70710678,-0.70710678,0,0,0.70710678,0.70710678,0,0,0,0,1,0,0,0,0,1)`，原点 `(L/2, TH/2)`，中心沿 `\` 对角线按 122 等距排布。
- 横幅与海报里的标记由同一函数按 `176/512`、`300/512`、`360/512` 三个倍率重新发射，**没有**把图标渲染成 PNG 再贴进去（`N_no_embedded_raster` 4 项全过：无 `Image`、无 base64、无 URL、无 `transform=/scale=`）。
- 装饰用 10% 透明度直接写在颜色末位（`#38BDF81A`、`#F6B94A1A`），不用 `<Opacity>` 包裹 `<Positioned>`（`<Positioned>` 只能是 `<Stack>` 的子节点）。
- 文案一律走 `<Raw><![CDATA[...]]></Raw>`；CJK 字体串用 `Noto Sans CJK SC,Noto Sans CJK JP`（逗号后不加空格），标签与日期用 `Noto Sans Mono CJK SC`；正文 `height="1.2"` 留出降部空间，避免 "Layerlight" 的 y/g 被切。

## 生成与校验工具

- 生成器 `tmp/.../A13/gen.ps1`：单一几何来源，幂等。重新运行时未改动的产物字节完全一致（第 03 轮哈希比对确认只有 `launch-poster` 变化）。
- 校验器 `tmp/.../A13/verify.ps1`：29 项检查，全部从**已渲染 PNG + 已交付 DSL** 读取，结果写入 `outputs/.../A13/brand-audit.json`。

| 分组 | 项数 | 检查内容 |
| --- | --- | --- |
| P_png_signature_and_size | 5 | PNG 签名与 512×512 / 1200×400 / 1080×1350 / 32×32 尺寸 |
| A_transparency | 2 | 两个图标四角 alpha=0 |
| K_pure_black | 2 | 黑色图标 A>0 处 RGB 全为 0；alpha 1..255（抗锯齿按允许方式存在） |
| G_identical_geometry | 1 | 两图标实心覆盖（A>128）差 0 像素，软边抖动 ≤1 |
| M_clear_space | 1 | 四边留白 ≥51.2px（10%），实测 66px = 12.89% |
| S_beam_separation | 5 | 3 道光带 + 2 条通道；32×32 原生渲染同样 3 道；墨点数在合理区间 |
| C_required_copy | 7 | 横幅 2 条、海报 5 条必需文案逐字在 CDATA 中 |
| N_no_embedded_raster | 4 | 四个交付 DSL 无任何位图 / URL / 缩放 token |
| H_shared_geometry | 2 | 横幅 6 处、海报 3 处同一 45° 规则（横幅含标记 + 水印两组） |

最终 `29/29 PASS`。

## 缩略图（仅作检查预览，保存在临时目录）

- `preview-a-layers-v2-thumb32.png`、`preview-b-rings-v2-thumb32.png`：用于方向取舍。
- `symbol-color-thumb32.png`、`symbol-black-thumb32.png`：由交付的 512px 渲染降采样（HighQualityBicubic）。
- `render-02-symbol-color-native32.png`：服务端按 32×32 原生渲染同一套几何，作为对照。
- 以上均不计入交付，均在查看后保留于 `tmp/`。

## 踩坑与修正

1. **Transform 原点写错（本题最主要的问题）**：`Get-Bars` 一度把 `origin` 发成盒子尺寸 `(256,88)` 而非光带中心 `(128,44)`。因为三道光带的偏移量相对各自盒子一致，错误表现为整体平移 `(+6.4, +103.4)` 并被画布底边裁切——肉眼看仍像"一个略微靠下的标记"，是 `verify.ps1` 的 `M_clear_space`（T=169, B=0）和 `S02` 先报出来的。改成 `(L/2, TH/2)` 后四边留白恢复为 66px 对称。
2. **用颜色过滤测量抗锯齿图形会失真**：早期按 `R<120 && B>200` 挑青色像素，低 alpha 边缘因预乘被排除，量出的光带轴长只有 216（实际 256）。改成按 `A>8` 加垂直分带隔离后，实测 `u-extent=256`、`v-extent=84`，与设计值一致。测量口径本身要先被验证。
3. **校验器自身两处缺陷**：(a) 通道记录的三个 `if` 顺序有误，新光带开始时先把 `inGap` 清零，导致永远记不到通道；(b) 把扫描终点前的尾隙也算成通道，报出"3 条通道"。已改为只统计两条光带之间的通道。
4. **几何一致性不能用 alpha 逐位相等来判**：`#38BDF8`/`#F6B94A` 与 `#000000` 的预乘舍入不同，有 872 个软边像素差 1 个 alpha 级。改为"实心覆盖差 0 像素 + 抖动 ≤1"，既严格又不误报。
5. **校验器按版本解析渲染件**：`resolve` 到每个文件现存的最高 `render-0N-` 版本，避免只改海报时被迫重渲另外四件；审计里逐件记录 `render_versions`。
6. **PowerShell 老问题再次生效**：`-f` 的操作数不能跨行（已改为先拼 `$fmt` 再 `-f`）；`Get-ChildItem -File` 在 `(...)` 表达式里偶发参数绑定失败；命令行把 `-Ver` 当成位置参数传给 `$args` 导致 `[int]` 转换报错（脚本位置参数应直接传 `1`/`2`/`3`）。

## 跨题复用

- 渲染脚本 `_suite/render.ps1`（POST + `requests.jsonl` 落盘 + 429/503 自动重试 + 失败正文进 `failures/`）。
- 调色板沿用全套：青 `#38BDF8`、琥珀 `#F6B94A`、墨蓝 `#0B1220`、纸白 `#F8FAFC`。
- 字体来源沿用套件共享的 `/fonts` 响应，本题未重复发起字体请求。
- `iterations.jsonl` 的 `baseline / visual_view / incomplete_visual / checker` 分类沿用 A12，本题另加 `probe` 与 `fix` 两类以如实区分探针和缺陷修复。
