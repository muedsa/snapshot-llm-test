# A13 · 叠光 / Layerlight 品牌交付 — 使用说明与踩坑

run_id `20261008T1615Z-run01`；输出 `outputs/20261008T1615Z-run01/A13/`，
过程 `tmp/20261008T1615Z-run01/A13/`。路径基准见 PATHS.md（本文件所有链接相对总任务根）。

## 1. 交付清单

| 文件 | 尺寸 | 字节 | 服务响应编号 |
|---|---|---|---|
| `symbol-color.png` + `.snapshot` | 512×512 透明 | 6700 | `A13-v01-color-20261008T165348Z` |
| `symbol-black.png` + `.snapshot` | 512×512 透明 | 4557 | `A13-v01-black-20261008T165349Z` |
| `brand-banner.png` + `.snapshot` | 1200×400 | 32277 | `A13-v04-banner-20261009T010648Z` |
| `launch-poster.png` + `.snapshot` | 1080×1350 | 62750 | `A13-v06-poster-20261009T011316Z` |
| `brand-system.json` | — | 色彩/比例/构件/留白/各应用映射/小尺寸规则/服务约束 | — |
| `rationale.md` | ≤300 字 | 方向差异 · 看图选择 · 小尺寸改进 | — |
| `task-metrics.json` | — | 38 次渲染、24 条迭代、19 次实际看图 | — |

过程留痕：`requests/`（含 8×500 与 1×400 的失败响应）、`tmp/…/A13/probes/`（p01–p10 边界实验）、
`tmp/…/A13/preview/`（方向与节点色候选、32px 检查图、放大对照表）、
`tmp/…/A13/check-report.json`（52 项自检）、`tmp/…/A13/iterations.jsonl`。

## 2. 需求 ↔ 证据

| 需求 | 证据 |
|---|---|
| 两个真正不同几何方向的预览，看图后择一 | `preview/alt-A-512.png`（平移重复）与 `alt-B-512.png`（45°＋光束），B 在 `thumb-B-32.png` 下读作禁止符号而弃用 |
| 512 彩色／512 纯黑，几何相同 | `check_a13.py` 去色指纹比对 `geometry_identical_to_colour_symbol`；两次 `icon()` 调用坐标完全一致，只换颜色 |
| 纯黑版非透明像素 RGB=0 | `painted_pixels_are_rgb_zero`：49177 个着色像素全部为 (0,0,0)；`only_black_colour_in_dsl` |
| 图标 ≤6 主要构件 | `mark_blocks()` 在四份 DSL 上都只解析出 4 个（3 框＋1 节点） |
| 32×32 仍可识别轮廓与负空间 | `preview/check-32-base.png`、`check-32-tuned.png` 为服务原生 32px 渲染，四色齐全；缩略只留在 tmp |
| 横幅含品牌名与标语，海报含日期/OPEN BETA/网址 | `text_present:*` 逐串比对 DSL 文本 |
| 不得把图标渲染图嵌进应用 | `mark_rebuilt_from_symbol_geometry`：把横幅/海报的 mark 块按其包围盒归一化，与符号指纹在 0.002 容差内一致；`no_raster_or_external_asset` 断言 DSL 内无 `<Image`、无 http、无 base64 |
| 海报是独立构图 | `poster_is_not_an_enlarged_banner`（3.00 vs 0.80 长宽比）＋两套互不重叠色值 |
| 大图与 32 缩略都实际看图 | `iterations.jsonl` 19 条 `image_viewed`，含 32px 两张 |

## 3. 文档与工具的真实使用

共享缓存文档（`tmp/…/_suite/docs/`，启动阶段取得）：`container.html`（`Container` 的
`border`/`borderRadius` 组合）、`layout.html`（`Stack`/`Positioned` 溢出与 clipBehavior 语义）、
`concepts.html`（类 DOM 与 `<Positioned>` 必须是 `<Stack>` 直接子节点）。
本题新增一次抓取：`shared-cliprect-20261009T011244Z` →
`tmp/…/_suite/docs/clip-rect.html(.txt)`，用于确认 `ClipRect` 无尺寸参数、按自身布局边界裁剪、
只接受一个子节点，且非 `NONE` 的 `clipBehavior` 需要 `decoration`。
共享脚本 `dslkit.py`（Doc/TextFit/n）、`render.py`（请求归档）、`iterlog.py`、`build_metrics.py`、
`fetch_extra.py` 全部实际调用；`zoom.py` 用于 32px 放大对照表 `preview/sheets/`。

## 4. 被证伪的假设与最终解法

| 直觉做法 | 实际发生 | 解法 |
|---|---|---|
| 圆角半径按比例算即可 | 32px 下 `borderRadius 1.58 < border 1.7` → **HTTP 500 INTERNAL_ERROR**，114 字节响应体零提示 | p01–p10 十张探针定位边界（`R==W`、`R>W` 为 200）；`frame()` 钳制 `radius=max(radius,stroke)`；结论进 `_suite/notes/service-behaviour-from-a13.md` |
| `Stack clipBehavior="CLIP"` 能裁切 | **400 PARSE_ERROR**：`No enum constant ...ClipBehavior.CLIP`；文档另说非 NONE 需 decoration | 外层 `Positioned` 供尺寸 + `ClipRect` + 内层 `Stack(clipBehavior="NONE")`，海报细线收在 y=660 |
| 墨色节点在任意底上都成立 | 海报深色底上节点直接消失 | 4 张候选（红/无/蓝/琥珀）看图后改 `#F59E0B`，成为品牌第四色 |
| 描边粗细与画布无关 | 0.060S 在 32px 只有 1.9px，两框粘连 | 大图 0.070S，规范加小尺寸档：S≤48px 用 0.085S |
| 留白规则只管图标 | 自检扩展到应用图后发现横幅左边距 0.255S 违反自家 0.30S | 横幅边距改 `round(0.30*S)=66`，v04 重渲，实测 0.300 |
| 512 母版缩到 32px 等价于 32px 渲染 | LANCZOS 缩小后琥珀节点丢失（3.7px） | 作为 measurement 如实记录，规范改为「小尺寸必须原生渲染」 |
| `--out` 传目录也行 | `render.py` 把图写到运行根目录、归档写进 `outputs/<rid>/requests/` | 该次尝试（v03-banner，200）原样保留为证据，正确重渲为 v04-banner |

## 5. 统计

38 次渲染请求（29×200 / 8×500 / 1×400）、1 次新增文档抓取、37 个 DSL 版本、
24 条迭代记录（9 visual / 5 alternative / 5 baseline / 3 syntax-fix / 2 requirement-change）、
19 次实际看图、52/52 自检通过。

计时按三类分开（见 `task-metrics.json` `timings`）：
`wall_clock_seconds` 31010.3s（16:42:50Z→01:19:40Z），
`active_seconds` 2232.9s（两段活动岛），
`idle_gap_seconds` 28777.5s —— 全部来自 **17:06:10Z→01:02:57Z 的一次会话挂起/上下文压缩**，
期间没有任何请求、没有任何产出，不计为工作时间。
