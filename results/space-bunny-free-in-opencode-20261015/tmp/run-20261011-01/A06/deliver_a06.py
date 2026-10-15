#!/usr/bin/env python
"""A06 一站式交付。启动基准：总任务根。"""
from __future__ import annotations

import sys

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import deliver  # noqa: E402

SPEC = dict(
    task_id="A06", title="十四节点依赖图与反馈回路", version="v10",
    started_at="2026-10-11T13:10:00.000+08:00",
    source_drafts={"v10": "a06-v10.snapshot"},
    images=[{"name": "dependency-map.png", "dsl": "dependency-map.snapshot", "draft_key": "v10"}],
    audit_json={"filename": "graph-audit.json", "draft_name": "graph-audit-raw.json"},
    candidates=[{"path": f"tmp/run-20261011-01/A06/drafts/a06-v{v}.snapshot", "status": "superseded"}
                for v in (1, 2, 3, 4, 5, 6, 7, 8, 9)],
    extra_capabilities="任意方向的线段由 `Transform` 的列主序 4×4 旋转矩阵 + `alignment=\"CENTER\"` 拼接；"
                       "箭头用两段线拼成 V 形（解析器无多边形/path）；"
                       "虚线由沿长度均匀排布的短矩形组成（`BorderStyle` 无 DASHED）；"
                       "`#RRGGBBAA` 半透明色带表示拓扑层。",
    extra_docs="""
| https://snapshot.muedsa.com/reference/parser-tags/ · Positioned | `Positioned` 只支持 `left/top/right/bottom/width/height`，且必须是 `Stack`/`IndexedStack` 的直接子节点 | 本题曾两次因此失败，见修改记录 |
""",
    req_items="""
| 文件 | 用途 | 对应 DSL 或图片 | 完成状态 |
|---|---|---|---|
| `dependency-map.snapshot` | 1600×1000 依赖解释图定稿 DSL | `dependency-map.png` | 已完成 |
| `dependency-map.png` | 服务返回的最终图片 | `dependency-map.snapshot` | 已完成，服务原始响应 |
| `graph-audit.json` | 拓扑层/邻居/最长路径/反馈边位置 | — | 已完成 |
| `snapshot-usage.md` / `task-metrics.json` | 报告与指标 | — | 已完成 |

需求逐项核对（依据最终图**实际查看**，含底部与右侧面板放大局部）：

| 题目要求 | 满足情况 | 证据 |
|---|---|---|
| 1600×1000 | 满足 | 服务 `image_info` = 1600×1000 |
| 依据 inputs/graph.json | 满足 | 14 节点 / 16 先决边 / 2 反馈边全部取自输入；输入未修改 |
| solid_edges 为有向先决依赖，feedback_edges 不参与 DAG 排序 | 满足 | 拓扑层仅由 16 条先决边做 Kahn 分层得出；两条反馈边标注「不参与 DAG 排序」，且 `graph-audit.json` 中分层方法写明只用 solid_edges |
| 14 个节点的编号与标签完整出现 | 满足 | 图中 N01–N14 全部出现，标签 22px、编号 18px |
| 每条边的方向可辨 | 满足 | 16 条先决边末端均有 V 形箭头；2 条反馈边末端同样有箭头 |
| 反馈边用虚线和专用图例 | 满足 | 粉色虚线 + 独立图例项 + 右侧「两条反馈回路」说明卡 |
| 反馈边不能画成普通先决依赖 | 满足 | 走右侧独立通道，与灰色实线先决边在颜色、线型、位置三方面区分 |
| 交叉线无连接点不构成新依赖 | 满足 | 页脚明确写出；图中交叉处无节点或圆点标记 |
| 节点位置体现先后和并行 | 满足 | L0–L10 共 11 层；L1/L2/L3 各含 2 个节点（同层并行） |
| 用侧边弯折/线段绕行减少线压文字 | 满足 | N04→N13 跨 7 层，走左侧橙色通道绕行并在图上标注「侧边绕行」 |
| 先决边不能出现指向过去层的布局歧义 | 满足 | 所有先决边目标层号 > 源层号，一律自上而下；`layout.direction_ambiguity` 字段记录 |
| 解释「失败后回到构建」 | 满足 | N09→N08 标注「首轮渲染失败 → 回到 DSL 构建」，图中与说明卡各一次 |
| 解释「检查发现问题后修复」 | 满足 | N10→N08 标注「视觉检查发现问题 → 回到 DSL 构建」，图中与说明卡各一次 |
| 节点字号≥22、注释≥18 | 满足 | 节点标签 22px、编号 18px；层号、图例、阶段、说明、页脚均 ≥18px |
| 不把 14 条文字当作无连接的列表 | 满足 | 14 个节点全部由 18 条边连接（16 先决 + 2 反馈），逐条可追踪 |
| graph-audit.json 五类信息 | 满足 | `topological_layers` / `nodes[].in_neighbors,out_neighbors` / `longest_prerequisite_path` / `edges.feedback[].points_px` 齐备 |
""",
    request_rows=[
        ("A06-v1-1ff09f50", "drafts/a06-v1.snapshot", "6.37s", "400 application/json",
         "responses/A06-v1-1ff09f50.error.json",
         "无图；`Tag Positioned only can have one child`（图例里把已是 Positioned 的图元又套了一层 Positioned）"),
        ("A06-v2-bdeab16d", "drafts/a06-v2.snapshot", "3.85s", "400", "responses/A06-v2-bdeab16d.error.json",
         "无图；`ProxyWidget has no widget`"),
        ("A06-v3-1c6fce84", "drafts/a06-v3.snapshot", "2.31s", "400", "responses/A06-v3-1c6fce84.error.json",
         "无图；同类错误仍未消除"),
        ("（二分定位）", "drafts/_bisect.snapshot", "—", "—", "tmp/…/A06/bisect.py 输出",
         "把生成 DSL 的 290 个顶层片段逐段截断重渲，定位到第 3 个片段："
         "`<Positioned … color=… borderRadius=… border=…/>`——把 Container 的属性写在了 Positioned 上"),
        ("A06-v4-4c3a316e", "drafts/a06-v4.snapshot", "2.40s", "400", "responses/A06-v4-4c3a316e.error.json",
         "无图；`renderBox.parentData must be StackParentData`（图例行内仍有 Positioned 嵌在 Row 里）"),
        ("A06-v5-c3fcf01c", "drafts/a05…v5", "1.94s", "400", "responses/A06-v5-c3fcf01c.error.json", "无图；同类错误"),
        ("A06-v6-cd90f35d", "drafts/a06-v6.snapshot", "4.37s", "200 image/png", "preview/a06-v6.png",
         "首次出图并实际打开：右侧面板严重溢出版面（4 张卡片互相重叠、最长路径卡片超出画布底部）；"
         "反馈边标签被裁；底部出现两条跑出画布的灰线"),
        ("A06-v7-a775463e", "drafts/a06-v7.snapshot", "4.44s", "200 image/png", "preview/a06-v7.png",
         "已打开：右侧面板改为按实测行数顺排后仍溢出；最长路径 3 列后仍超出画布"),
        ("A06-v9-c5c2f674", "drafts/a06-v9.snapshot", "6.63s", "200 image/png", "preview/a06-v9.png",
         "已打开：图内已干净，但最长路径末行仍压到页脚、页脚文字右端被裁"),
        ("A06-v10-1f6bd00d", "drafts/a06-v10.snapshot", "4.59s", "200 image/png", "preview/a06-v10.png",
         "已打开整屏 + 底部与右侧面板放大局部：无重叠、无裁切，18 条边全部在画布内"),
        ("A06-final-*", "outputs/…/dependency-map.snapshot", "见 metrics", "200 image/png",
         "outputs/…/dependency-map.png", "已打开复查"),
    ],
    change_rows=[
        ("v1 · syntax-fix", "服务 400：Positioned 只能有一个子节点",
         "图例中 `sk.box(..., left=, top=)` 返回的已是 `Positioned`，又被放进 `Positioned`/Row",
         "新增 `inline()` 把局部坐标图元包进 `Container>Stack`，图例改用该形式",
         "进入下一处错误"),
        ("v2–v5 · syntax-fix", "`ProxyWidget has no widget` / `renderBox.parentData must be StackParentData`",
         "（1）把 `color`/`borderRadius`/`border` 写在了 `<Positioned>` 上——Positioned 属性表只有 "
         "`left/top/right/bottom/width/height`；（2）图例行仍把 `Positioned` 放进 `Row`",
         "绘图区背景改为 `Positioned > Container`；图例行整体改为 `Positioned > Stack > Positioned…`",
         "v6 出图"),
        ("v6 · visual", "右侧面板 4 张卡片互相重叠并溢出版心；反馈标签被裁；底部两条灰线跑出画布",
         "（1）面板高度按估算值写死；（2）折线折点 `(ex, ey + mid)` 写错，应为 `(ex, mid)`，"
         "导致 N04→N13 的中间段被算成长 759px、终点 y=1273 的线段",
         "面板改为按 `sk.est_lines()` 实测行数顺排；折点改为 `mid`；"
         "N04→N13 的普通折线与绕行线同时保留造成重复，改为长边只走绕行通道",
         "v7/v9 逐步收敛"),
        ("v9 · visual", "最长路径末行压到页脚；页脚文字右端被裁",
         "面板链路累计高度超出可用空间；页脚文案过长",
         "图例行距 32→30、阶段行距 26→24；最长路径改 3 列 4 行；页脚压缩为一行短句",
         "v10 复查通过"),
    ],
    iterations=[
        ("v1", "syntax-fix", None, ["Positioned 单子节点错误"], ["改用 inline() 包裹图元"], "进入下一处错误"),
        ("v3", "syntax-fix", None, ["ProxyWidget has no widget"], ["二分定位后修正 Positioned 上的非法属性"],
         "定位到具体片段"),
        ("v4", "syntax-fix", None, ["renderBox.parentData 错误"], ["图例行改为 Positioned>Stack 结构"],
         "错误消除"),
        ("v6", "baseline", "v6", ["右侧面板重叠溢出", "反馈标签被裁", "底部灰线跑出画布"],
         ["首版成功出图"], "实际打开后发现 3 类问题"),
        ("v7", "visual", "v7", ["面板仍溢出", "底部灰线仍在"], ["面板顺排 + 折点修正 + 去重复边"], "接近完成"),
        ("v9", "visual", "v9", ["最长路径压页脚", "页脚被裁"], ["面板行距压缩 + 3 列布局 + 页脚缩短"],
         "完成"),
        ("v10", "visual", "final", [], ["最终复查"], "整屏与放大局部均正常"),
    ],
    design_notes="""
**关键设计选择**

1. *先决边一律向下，方向唯一*。拓扑层由 Kahn 算法只用 `solid_edges` 算出，
   因此每条先决边都满足 `layer(to) > layer(from)`，画成自上而下的折线后**不可能**产生
   「指向过去层」的歧义。这是布局层面的结构性保证，而不是靠人工检查。

2. *反馈边单独走通道 + 三重区分*。两条反馈边都指回更早的层（N09/N10 → N08），
   若与先决边同样绘制就会产生方向歧义。因此它们走右侧独立通道，
   并在**颜色**（粉色 vs 灰色）、**线型**（虚线 vs 实线）、**位置**（右侧通道 vs 主图）三方面区分，
   同时配独立图例项与说明卡。

3. *长边侧边绕行*。N04→N13 跨 7 层，若直连会从 N06…N12 的节点上穿过。
   改为走左侧橙色通道并标注「侧边绕行」，同时把这条边从常规折线集合中移除，避免重复绘制。

4. *箭头用两段线拼 V 形*。解析器没有多边形/path，因此 `arrow()` 用两段旋转矩形构成箭头，
   方向由线段角度决定，视觉上清晰可辨。

5. *审计 JSON 记录可复算的量*。`topological_layers.method` 写明算法，
   `longest_prerequisite_path` 同时给出节点数、路径、所用边，并校验这些边全部属于 `solid_edges`；
   每条边的绘制折点坐标都落在 `points_px` 中，便于逐段复核。

**可复用经验**

- `Positioned` 的属性只有 `left/top/right/bottom/width/height`，把 `color`/`border` 等
  装饰属性写在它上面不会报 PARSE_ERROR，而是延后变成难懂的 `ProxyWidget has no widget`；
  遇到这类渲染期怪异错误时，**对生成的 DSL 做顶层片段二分定位**比逐行阅读快得多。
- 折线折点计算里 `(ex, ey + mid)` 这类笔误会产生远超画布的线段；
  渲染成功后应检查「所有图元的坐标是否都落在画布内」这一几何不变量。
- 同一逻辑边不要既画常规折线又画绕行线，否则会出现视觉上的重复依赖。
- 右侧面板这类纵向堆叠的卡片组，高度必须由内容行数实测决定，不能估算。

**结束依据**：最终图实际打开查看（含底部与右侧面板放大局部），18 条边全部落在画布内、
方向可辨、无重复；14 个节点编号标签齐全；审计 JSON 与图面逐项一致；未以渲染成功作为完成依据。
""",
    unresolved="""
- 未发现影响交付的未解决问题。
- 最长先决路径按题目要求「允许多解」只给出其中一条（11 个节点），另一条同长路径
  N01→N02→N04→N07→N08→…→N14 也是 11 个节点；JSON 中以 `multi_solution_allowed` 标注。
- 题目未给出节点坐标，节点位置由分层布局算法生成；坐标已全部写入 `nodes[].node_box_px`。
""",
)

if __name__ == "__main__":
    deliver.run(SPEC)