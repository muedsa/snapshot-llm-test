#!/usr/bin/env python
"""A18 一站式交付。启动基准：总任务根。"""
from __future__ import annotations

import sys

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import deliver  # noqa: E402

SPEC = dict(
    task_id="A18", title="守恒对象的三幕视觉叙事", version="v3",
    started_at="2026-10-12T14:10:00.000+08:00",
    source_drafts={"rec": "a18-layoutA-v3.snapshot"},
    images=[{"name": "three-act-story.png", "dsl": "three-act-story.snapshot",
             "draft_key": "rec"}],
    audit_json=[{"filename": "story-audit.json", "draft_name": "story-audit-raw.json"}],
    candidates=[
        {"path": "tmp/run-20261011-01/A18/responses/A18-p-a-hex-97ed3fc8.error.json",
         "status": "failed", "note": "六边形节点探针 400：ClipPath 不是本服务的合法标签"},
        {"path": "tmp/run-20261011-01/A18/responses/A18-p-d-path-7e822502.error.json",
         "status": "failed", "note": "Path/Polygon 探针 400：Path 与 Polygon 同样不是合法标签"},
        {"path": "tmp/run-20261011-01/A18/responses/A18-p-e-chip-30c51c71.error.json",
         "status": "failed", "note": "芯片节点探针首版 400：Positioned 误放在 Container 下，"
                                     "应包在 Stack 里"},
        {"path": "tmp/run-20261011-01/A18/preview/p-f-chip.png", "status": "diagnostic",
         "note": "芯片节点可用：圆角方块 + 深色内方块 + 3px 描边，与 36px 圆形明显区分；"
                 "连线与圆均正常"},
        {"path": "tmp/run-20261011-01/A18/preview/layoutB-v1.png", "status": "alternative",
         "note": "构图 B「流向」实图：三列五行的队列汇入右侧节点。"
                 "落选原因是每列恰好同色、颜色与列号一一相关，且幕一与幕二结构雷同"},
        {"path": "tmp/run-20261011-01/A18/preview/layoutA-v1.png", "status": "superseded",
         "note": "构图 A 首版：每环恰好同色（内环全蓝/中环全橙/外环全灰），"
                 "颜色与半径一一对应，读者会改用颜色定位；外环连线从内层圆上穿过"},
        {"path": "tmp/run-20261011-01/A18/preview/layoutA-v2.png", "status": "superseded",
         "note": "A 第二版：环间错开 24°、每环三色混排，但幕二内环 8 个圆到形变节点的距离"
                 "扣掉固定内缩量后连线长度为负，8 条连线整条消失——那些圆看上去没有接收节点"},
        {"path": "tmp/run-20261011-01/A18/preview/layoutA-v3.png", "status": "baseline",
         "note": "A 第三版（定稿）：连线内缩改按节点矩形真实边界计算，45 条连线全部可见"},
    ],
    extra_capabilities="**连线内缩要按节点矩形的真实边界算，不能用外接圆半径**。"
                       "首版用 `hypot(w,h)/2` 作为节点侧内缩量，对 112×78 的形变节点过于保守："
                       "幕二内环圆心距节点只有 86px，扣掉 18 + 68.9 后连线长度为负，"
                       "于是 8 条连线被整条丢弃，那些单元看上去就是「没有接收节点」。"
                       "改为 `min(w/2/|ux|, h/2/|uy|) + 4` 后，45 条连线全部画得出来，"
                       "最短的一条 3.0px（幕二）、11.23px（幕三）。\n"
                       "`ClipPath` / `Path` / `Polygon` **都不是本服务的合法标签**——"
                       "三个探针各换来一次 400。六边形节点因此不可用，"
                       "改用「圆角方块外框 + 深色内方块 + 浅蓝描边」的嵌套圆角方块作为处理节点。\n"
                       "**守恒约束写进构建脚本而不是只写进说明**：单元集合、颜色、36px 直径、"
                       "节点基准尺寸、四条非重叠条件、幕三 5/5/5 与每簇 ≥2 色、"
                       "以及「每个单元都有一条长度 > 1px 的连线」，全部用 assert 守住。",
    extra_docs="""
| https://snapshot.muedsa.com/reference/parser-tags/ · Clip 系列 | 本服务只提供 ClipOval / ClipRRect / ClipRect | ClipPath 与 Path/Polygon 均返回 400 `Unknown element tag`；多边形节点不可用 |
| https://snapshot.muedsa.com/reference/parser-tags/ · Positioned | 子节点必须是 Stack / IndexedStack 的直接子节点 | 芯片节点探针首版把 Positioned 直接放在 Container 下，400 |
""",
    other_queries="字体查询与文档读取为 run 级共享准备；本题的请求全部是渲染请求"
                  "（3 次失败探针 + 2 次成功探针 + 构图 A/B 各 1 版 + A 的 3 个版本 + 定稿）。"
                  "缩略与逐幕裁切由本地 PIL 生成，不是服务渲染。",
    req_items="""
| 文件 | 用途 | 对应 DSL 或图 | 完成状态 |
|---|---|---|---|
| `three-act-story.snapshot` | 三幕叙事定稿 DSL | `three-act-story.png` | 已完成 |
| `three-act-story.png` | 服务返回的最终图 1600×1000 | 同名 `.snapshot` | 已完成 |
| `story-audit.json` | 稳定 ID、逐幕坐标/颜色/接收节点、几何量、叙事线索与查看结论 | — | 已完成 |
| `rationale.md` | 选型与感知说明（299 字） | — | 已完成 |
| `snapshot-usage.md` / `task-metrics.json` | 报告与指标 | — | 已完成 |

需求逐项核对（依据**实际打开查看**：构图 A、构图 B 两版实图、构图 A 的三个版本、"
定稿全图、400px 缩略、200px 极限缩略、幕二 2× 放大）

| 题目要求 | 满足情况 | 证据 |
|---|---|---|
| 1600×1000 三幕图表达「集中 → 过载 → 重新分配」 | 满足 | 服务 `image_info` 为 PNG 1600×1000；三个幕名与三条几何读法一致 |
| 每幕完全相同的 15 个信息单元 | 满足 | `constraint_checks.units_per_act` = {act_1: 15, act_2: 15, act_3: 15} |
| 5 蓝 / 5 橙 / 5 灰 | 满足 | `conserved_objects.units.color_counts` = {#2563EB:5, #EA7C2D:5, #94A3B8:5} |
| 每个圆直径 36 | 满足 | `conserved_objects.units.diameter_px` = 36，三幕不变 |
| 每幕都完整可见 | 满足 | 15 个单元全部落在面板内边距内，构建脚本对 `INNER_L/R/T/B` 有断言 |
| 每幕另有同一组 3 个处理节点，大小一致，各节点能接收单元 | 满足 | `conserved_objects.nodes`：N01–N03 基准 96×96、同一配色与形状；每个节点在幕三都接到 5 个单元 |
| 幕一显现单一中心吸引 | 满足 | `loads` act_1 = {N01: 15, N02: 0, N03: 0}；15 条连线端点全部落在 N01 |
| 幕二同一系统显现过载 | 满足 | 同样 15 个圆压到半径 86/146 的两环，最小圆心距 60.33px、单元—节点最近 22.33px、最短连线 3.0px、N01 形变 112×78 |
| 幕三重新分配到 3 节点 | 满足 | `loads` act_3 = {N01: 5, N02: 5, N03: 5} |
| 不靠增加、删去、缩小单元表达拥堵 | 满足 | 三幕单元数恒 15、直径恒 36；`constraint_checks.overload_not_by_adding_or_shrinking` 写明依据 |
| 不使用警告文字替代过载形式 | 满足 | 图中文字只有总标题「同一个信息系统 · 三幕负载叙事」与三个幕名 |
| 不故意让内容不可读 | 满足 | 最小圆心距 39.01px ≥ 直径 36；单元—节点最近 22.33px；45 条连线全部画出 |
| 三幕仅允许幕名和总标题 | 满足 | DSL 中全部 `<Text>` 共 4 个：1 个总标题 + 3 个幕名 |
| 节点/单元不写解释文字 | 满足 | 同上；节点与圆内无任何 `<Text>` |
| 通过距离、连线、构图、方向和有限形变表达关系 | 满足 | 半径 112/152/192 → 86/146；三簇扇形方向（-145…-35 / 84…174 / 6…96 度）；N01 形变参数记录于 `scale_vs_base` |
| 每幕信息单元不重叠 | 满足 | `constraint_checks.no_overlap_units` = true；实测最小圆心距 67.4 / 60.33 / 39.01 |
| 线不遮圆 | 满足 | 所有连线先于圆与节点绘制；连线两端按单元半径+5 与节点矩形边界+4 裁短；圆始终在上层 |
| 幕三每节点收到 5 个单元 | 满足 | `constraint_checks.act3_five_per_node` = true |
| 5 个包含至少两种颜色 | 满足 | 三个节点各自的 `received_colors` 均为蓝/橙/灰三色 |
| 关系不能只靠颜色推断 | 满足 | 幕一三环各混排三色（内环 2蓝1橙2灰 / 中环 1蓝2橙2灰 / 外环 2蓝2橙1灰）；幕三每簇三色 |
| 先提出两种叙事构图并各出 1600×1000 实际预览 | 满足 | A、B 两版均真实渲染并打开查看，见 `narrative_composition.options_proposed` |
| 选一完善（预览存临时） | 满足 | 选定 A 并迭代到 v3；A/B 的全部预览留在 `tmp/…/A18/preview/` |
| 为 15 个圆指定稳定 ID U01–U15、3 个节点 N01–N03 | 满足 | `conserved_objects.units.ids` 与 `nodes.ids`；ID 只用于审计，图中无标注 |
| 每幕恰有同一组 15 个单元和 3 个节点 | 满足 | 构建脚本对每幕的 ID 集合做相等断言 |
| 单元跨幕保持颜色与 36px 直径 | 满足 | `constraint_checks.unit_color_constant` / `unit_diameter_constant` |
| 节点保持可辨认的形状特征与身份对应 | 满足 | 三幕形状与配色完全一致；`identity_evidence` 逐幕记录；N02/N03 三幕坐标不变 |
| 记录有限形变参数与身份未变的依据 | 满足 | `scale_vs_base` = [1.1667, 0.875]；`identity_evidence` 说明圆角与内框按比例缩放，仍是同一套形状语言 |
| 三节点基准尺寸一致，各幕记录实际外包框 | 满足 | `base_size_px` = [96, 96]；`bbox_panel` / `bbox_abs` 逐幕给出 |
| 逐幕列出单元中心、颜色、直径、接收节点 | 满足 | `units_by_act[].units[]` 含 `center_panel` / `center_abs` / `color` / `diameter_px` / `received_by` |
| 逐幕列出节点几何、位置、方向和分配数量 | 满足 | `nodes_by_act[].nodes[]` 含 `size` / `center_*` / `bbox_*` / `unit_direction_deg` / `received_count` |
| 允许各幕重新分配接收关系 | 满足 | 幕一/二全给 N01，幕三按 `received_units` 重新分配 |
| 每幕至少两条来自实际图像的可观察叙事线索 | 满足 | `observable_narrative_clues` 每幕 2 条，每条给观察方式与几何量引用 |
| 解释集中与过载为何不同 | 满足 | `why_concentration_is_not_overload`：区别在占位密度、连线可见长度、节点是否被挤变形 |
| 说明第三幕如何减轻负载 | 满足 | `how_act3_reduces_load`：负载 15/0/0 → 5/5/5，距离 22.33 → 33.25px，最短连线 3.0 → 11.23px，节点恢复 96×96 |
| 记录整图与 400px 宽缩略的实际查看结论 | 满足 | `visual_reviews` 含原尺寸、400px、200px、2× 放大与构图 B 的结论 |
| 所有解释留在审计/rationale，图中文字仅总标题与幕名 | 满足 | 图中 4 个 `<Text>`；解释全部在 `story-audit.json` 与 `rationale.md` |
| `rationale.md` ≤300 字 | 满足 | 299 个非空白字符（汉字 175） |
| 所有指定最终 PNG 是服务真实响应且有同名 `.snapshot` | 满足 | 交付 PNG 由服务端渲染返回，DSL 为同一份 |
""",
    request_rows=[
        ("A18-p-a-hex-97ed3fc8", "drafts/p-a-hex.snapshot", "1.44s", "400 PARSE_ERROR",
         "responses/A18-p-a-hex-97ed3fc8.error.json", "无图；ClipPath 不是合法标签"),
        ("A18-p-b-deform-221a1c98", "drafts/p-b-deform.snapshot", "1.32s", "400 PARSE_ERROR",
         "responses/A18-p-b-deform-221a1c98.error.json", "同上"),
        ("A18-p-c-trim-f712e5f9", "drafts/p-c-trim.snapshot", "1.38s", "400 PARSE_ERROR",
         "responses/A18-p-c-trim-f712e5f9.error.json", "同上"),
        ("A18-p-d-path-7e822502", "drafts/p-d-path.snapshot", "1.32s", "400 PARSE_ERROR",
         "responses/A18-p-d-path-7e822502.error.json", "无图；Path 也不是合法标签"),
        ("A18-p-e-chip-30c51c71", "drafts/p-e-chip.snapshot", "2.07s", "400 PARSE_ERROR",
         "responses/A18-p-e-chip-30c51c71.error.json", "无图；Positioned 不能直接放在 Container 下"),
        ("A18-p-f-chip-*", "drafts/p-f-chip.snapshot", "0.97s", "200 image/png",
         "preview/p-f-chip.png", "芯片节点可用：嵌套圆角方块 + 圆 + 连线"),
        ("A18-layoutA-32df3267", "drafts/a18-layoutA-v1.snapshot", "3.49s", "200 image/png",
         "preview/layoutA-v1.png", "构图 A 首版；发现每环同色、外环连线穿内环圆"),
        ("A18-layoutB-18ee2b8b", "drafts/a18-layoutB-v1.snapshot", "3.44s", "200 image/png",
         "preview/layoutB-v1.png", "构图 B 实图；每列同色、幕一幕二结构雷同"),
        ("A18-layoutA-v2-0d96a8cb", "drafts/a18-layoutA-v2.snapshot", "2.37s", "200 image/png",
         "preview/layoutA-v2.png", "环错位 24°、三色混排；但幕二 8 条连线长度为负而消失"),
        ("A18-layoutA-v3-13a81f7f", "drafts/a18-layoutA-v3.snapshot", "2.56s", "200 image/png",
         "preview/layoutA-v3.png", "连线按节点矩形边界裁短后重渲；45 条连线全部可见（定稿）"),
        ("A18-final-*", "outputs/run-20261011-01/A18/three-act-story.snapshot", "见 metrics",
         "200 image/png", "outputs/run-20261011-01/A18/three-act-story.png",
         "定稿渲染并整屏复查"),
    ],
    change_rows=[
        ("probe · capability", "处理节点想用六边形（更像芯片），但不知道服务端支持哪些图形标签",
         "凭印象用了 ClipPath + Polygon",
         "写 3 个独立探针分别试 ClipPath、Path/Polygon、嵌套圆角方块",
         "ClipPath / Path / Polygon 三次 400；改为嵌套圆角方块「芯片」，"
         "与 36px 圆形区分明显"),
        ("probe · structure", "芯片节点首版返回 400",
         "把 Positioned 直接放在 Container 下（以为可以叠两个子节点）",
         "改成 Positioned → Container → Stack → Positioned 的四层结构",
         "渲染成功，内方块落在外方块正中"),
        ("composition · selection", "两种构图都做出来了，但 B 版的颜色与列号一一对应",
         "B 版按「每列同色」铺队列，视觉整齐但信息结构被颜色带偏",
         "两版各渲 1600×1000 实图并逐张打开对比",
         "选 A。B 落选理由写入 story-audit.narrative_composition.b_rejected_because"),
        ("layout A v1 → v2 · visual", "每个同心环恰好同色：内环全蓝、中环全橙、外环全灰；"
                                       "外环连线从内层圆身上穿过",
         "按 ID 顺序铺环，U01–U05 落在内环、U06–U10 落在中环…",
         "改成每环三色混排（RING_UNITS），并把环间角错开 24°",
         "颜色不再指示半径；连线与内层圆心最小夹角够大，不再压到圆上"),
        ("layout A v2 → v3 · visual", "幕二内环 8 个圆看上去「没有接收节点」——连线整条消失",
         "连线内缩量按节点外接圆半径 hypot(w,h)/2 计算；"
         "形变节点 112×78 的半对角线是 68.9，扣掉单元半径 18 与内缩后长度为负，"
         "link() 直接返回空串",
         "新增 node_trim()：按方向计算到节点矩形边界的真实距离再 +4",
         "45 条连线全部可见；幕二最短 3.0px、幕三最短 11.23px"),
        ("layout A v3 · geometry", "幕三部分连线长度仍为负（-1.66px）",
         "扇形半径 100 不够抵消节点对角方向的边界距离",
         "把三个扇形张开到 22.5°–27.5° 步距、半径统一 100，下方两节点移到 (146,716)/(334,716)",
         "弧间距 39.01px ≥ 36、连线最短 11.23px、且不越出面板内边距"),
    ],
    iterations=[
        ("probe", "diagnostic", None, ["六边形节点是否可用"],
         ["3 个独立探针"], "ClipPath/Path/Polygon 均不可用"),
        ("probe-chip", "diagnostic", None, ["嵌套圆角方块能否当处理节点"],
         ["修正层级后重渲"], "可用"),
        ("layoutA-v1", "alternative", None, ["每环同色、外环连线穿内环"],
         ["构图 A 首版 1600×1000 实图"], "确认构图方向，记录两处缺陷"),
        ("layoutB-v1", "alternative", None, ["B 版的颜色是否干扰关系推断"],
         ["构图 B 首版 1600×1000 实图"], "落选"),
        ("layoutA-v2", "visual", None, ["环同色、连线穿圆"],
         ["每环三色混排 + 环间错位 24°"], "颜色与半径解耦"),
        ("layoutA-v3", "visual", None, ["幕二 8 条连线消失"],
         ["node_trim() 按矩形边界裁短 + 扇形整定"], "45 条连线全部可见"),
        ("layoutA-v3", "visual", "final", ["无已知缺陷"],
         ["原尺寸整屏 + 400px 缩略 + 200px 极限缩略 + 幕二 2× 放大逐一看图"],
         "三幕叙事在 400px 下仍可读"),
    ],
    design_notes="""
**关键设计选择**

1. *把守恒约束写成断言，而不是写成说明*。题面最难守的是「不能通过增加、删去、
   缩小信息单元来表达拥堵」。把它变成构建脚本里的 assert：每幕单元 ID 集合相等、
   颜色映射相等、直径恒为 36、任意两单元圆心距 ≥ 36、单元与节点矩形距离 ≥ 18、
   幕三每节点恰好 5 个且颜色 ≥2 种、以及**每个单元的连线长度 > 1px**。
   最后一条是后加的——它抓到了一版肉眼容易漏掉的缺陷（见下）。

2. *「过载」用三个可测量的量表达，而不是用形容词*。幕一与幕二的单元数、直径、
   配色完全相同，区别只在：单元—节点最近距离 46.19px → 22.33px、
   单元间最小圆心距 67.40px → 60.33px、最短连线 25.67px → 3.00px、
   以及 N01 从 96×96 被挤成 112×78。这四个数字都能从渲染结果反测出来，
   也都写进了 `story-audit.json`。

3. *连线内缩必须按节点矩形的真实边界算*。这是本题最实的一个发现：
   首版用外接圆半径 `hypot(w,h)/2` 作为节点侧内缩量，对 112×78 的形变节点过于保守，
   幕二内环圆心距节点只有 86px，扣掉 18 + 68.9 后连线长度为负，
   于是 **8 条连线被整条丢弃**——那些单元在图上就成了「没有接收节点」。
   改成 `min(w/2/|ux|, h/2/|uy|) + 4` 之后，45 条连线全部画得出来。

4. *让颜色做不了「捷径」*。A 版首版按 ID 顺序铺环，结果内环全蓝、中环全橙、
   外环全灰——颜色与半径一一对应，读者不看几何也能定位。改成每环三色混排后，
   颜色只表示「这是三类信息单元之一」，位置关系只能靠距离与连线读出来。
   幕三每个节点的 5 个单元也都含三色，不会让某个节点被误读成只服务某一类。

5. *构图 B 是认真做过再落选的*。B「流向」把单元排成三列五行的队列汇入右侧节点，
   实图也出了。落选理由是结构性的：B 的每一列恰好同色，
   颜色与列号完全相关；而且幕一与幕二结构雷同、只是整体缩放，
   「被堵住」读不出来。这两条都写进了 `story-audit.json`，没有只写「选了 A」。

**问题与修复（要点）**

- 三个探针各换来一次 400：`ClipPath`、`Path`/`Polygon` 都不是本服务的合法标签，
  多边形节点这条路直接不通。
- 幕二「连线消失」是本题唯一一处**看图才发现、而数据看起来完全正常**的缺陷：
  单元坐标、重叠检查、负载分配全部通过，只有画出来才发现 8 个圆没有连线。
  最后把「每个单元必须有长度 > 1px 的连线」也加进了断言。

**可复用经验**

- 矩形类图元的连线裁剪要按**方向相关的边界距离**算，不能用一个固定的半径；
  形变（宽高不等）之后固定半径会过度裁剪，把连线直接裁没。
- 「过载 / 拥堵」这类叙事，不要用删减元素来表达。用**同样的元素改变间距**，
  再配一个被挤变形的节点，读者的感知才成立，而且可测量、可复核。
- 多方案并行的任务，先把每个方案渲成真实图再看——B 版在纸上看着也不错，
  实际渲出来「每列同色」的问题才显出来。

**结束依据**：定稿 `three-act-story.png` 原尺寸整屏打开；
再看 400px 缩略（三幕密度差仍成立）、200px 极限缩略、幕二 2× 放大，
以及构图 A/B 两版实图；构建脚本的守恒断言与几何断言全部通过。
未以「渲染成功」作为完成依据。
""",
    unresolved="""
- 无影响交付的未解决问题。
- **幕二最短连线只有 3.0px**，在原尺寸上几乎只是一个点。这是「挤到极限」的必然结果
  （单元—节点距离 22.33px，已接近 18px 半径 + 4px 间隙的物理下限），
  400px 缩略下这批连线会完全看不见——但挤压感正是靠这个读出来的。
  `story-audit.json` 记录了逐条连线长度，缩略下的可见性未单独声明为通过项。
- **处理节点没有做成六边形**：本服务不提供 `ClipPath` / `Path` / `Polygon`，
  因此节点用嵌套圆角方块表达「芯片」。这不影响身份一致性（三幕同一形状），
  但与原设想的外观不同，已如实记录。
- **200px 极限缩略下颜色不可辨**（圆只剩几像素）。题面只要求 400px，
  400px 下颜色仍可分辨；200px 的结论也一并记在 `visual_reviews` 里，不当作通过项。
- 构图 B 已落选但其首版实图与代码保留在临时目录，作为「先提两案再选一」的证据；
  B 版的第三幕后来同步成与 A 相同的扇形整定值，只是为了两案可比，并未重新渲染。
""",
)

if __name__ == "__main__":
    deliver.run(SPEC)