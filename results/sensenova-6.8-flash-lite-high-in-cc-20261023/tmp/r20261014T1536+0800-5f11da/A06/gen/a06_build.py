"""A06 主图构建：1600×1000「从需求到可复现交付」依赖解释图（纯 DSL，无外部素材）。

几何与走线一律来自 a06_model.build()，本文件不硬编码任何节点坐标或边端点。

关键工程决策（继承 A05 的探针结论，见 A05/snapshot-usage.md §3）：
  * 文档 39 个标签里没有 Path/Line/Polyline；ClipPath 只裁剪不描边。
  * `<Transform matrix>` 只认纯平移，2×2 非单位矩阵（旋转/错切/缩放）会静默渲染为空。
    因此斜线、以及斜向箭头都不能用旋转实现。
  * 本题改用**全轴对齐 elbow 走线**（竖直/水平段 + 直角拐弯），箭头指向始终是
    正方向之一；箭头本身由 5 根逐级缩窄的矩形拼出三角轮廓，同样不需要旋转。
  * `Text` 的 textAlign 无效，对齐走 `Container alignment`；容器高度 ≤ fontSize 会
    裁掉字形底部（A05 句点缺陷），txt_box 一律把容器底边钉住、向上撑高到 size+2。
  * `fontFeatures="+tnum=2"` 对拉丁数字不生效，列对齐靠容器宽度与 alignment。

布局分区（互不侵入）：
  左侧  = 层号沟槽 + 走线走廊（N04→N13 长期先决与两条反馈回路都从左侧绕行）
  中间  = 11 行自上而下的节点主链
  右侧  = 一块贯通的说明面板：图例 / 读图规则 / 阶段色 / 两条反馈回路的图内解释
  底部  = 最长先决路径（两解）+ 规模 + 读图规则

启动基准：总任务根（cwd）。用法：python a06_build.py <version> [--final]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a06_io as IO      # noqa: E402
import a06_model as MD   # noqa: E402

PW, PH = MD.PW, MD.PH
FA = 'fontFamily="Noto Sans CJK SC"'
TNUM = 'fontFeatures="+tnum=2"'
TF = FA + " " + TNUM

INK, SUB, MUT, WEAK = "#0F172A", "#475569", "#64748B", "#94A3B8"
BG, PANEL, PANEL_BD = "#F8FAFC", "#FFFFFF", "#E2E8F0"
GRID, GRID_LT = "#CBD5E1", "#EEF2F7"
EDGE_C = "#334155"
FB_C, FB_INK, FB_BG = "#D97706", "#92400E", "#FEF3E2"
CHIP_BG = "#EEF2F7"

TITLE_TOP, SUB_TOP, SUB2_TOP = 20, 60, 88
SEP_Y = 112
GUT_X = 48.0

# 右侧说明面板：x ≥ 1080，节点最右缘是 N03 的 1037
RP_X, RP_Y, RP_W, RP_H = 1080.0, 104.0, 476.0, 680.0
# 底部面板：最长先决路径与规模
BP_X, BP_Y, BP_W, BP_H = 40.0, 796.0, 1520.0, 196.0

LW = 2.4              # 边线宽
AW, AH = 14.0, 11.0  # 箭头宽/长
DASH = (10.0, 7.0)  # 反馈边虚线 dash 参数
NODE_R = 10.0
ARROW_STEPS = 5

# 反馈边的图内短标签位置（写在各自回环内侧，避开所有走线段）
FB_LAB_POS = {("N09", "N08"): (400.0, 408.0), ("N10", "N08"): (400.0, 458.0)}


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def n(v: float) -> str:
    """坐标输出：整数值去掉小数，其余保留两位。"""
    f = float(v)
    return str(int(round(f))) if abs(f - round(f)) < 1e-9 else f"{f:.2f}"


def txt(x, y, s, size=18, color=INK, bold=False, feat=True):
    st = ' fontStyle="BOLD"' if bold else ""
    ff = ' fontFeatures="+tnum=2"' if feat else ""
    return (f'<Positioned left="{n(x)}" top="{n(y)}"><Text text="{esc(s)}" '
            f'fontSize="{size}"{st}{ff} color="{color}" {FA}></Text>'
            f'</Positioned>')


def txt_box(x, y, w, h, s, size=18, color=INK, bold=False, align="BOTTOM_RIGHT"):
    """固定宽容器内对齐的文本。

    容器高度必须**严格大于** fontSize：探针实测 130×18 容器装 18px 文本会裁掉字形
    底部（句点变没），130×20 正常。做法是钉住底边、把顶边向上撑高到 size+2，
    文字位置只上移 2px，行内与列间对齐关系不变。
    """
    st = ' fontStyle="BOLD"' if bold else ""
    he = max(h, size + 2)
    y0 = y + h - he
    return (f'<Positioned left="{n(x)}" top="{n(y0)}" width="{n(w)}" height="{n(he)}">'
            f'<Container width="{n(w)}" height="{n(he)}" color="transparent" '
            f'alignment="{align}"><Text text="{esc(s)}" fontSize="{size}"{st} '
            f'{TF} color="{color}"></Text></Container></Positioned>')


def rect(x, y, w, h, color, r=0, border=None):
    b = f' border="{border}"' if border else ""
    rr = f' borderRadius="{n(r)}"' if r else ""
    return (f'<Positioned left="{n(x)}" top="{n(y)}" width="{n(w)}" height="{n(h)}">'
            f'<Container width="{n(w)}" height="{n(h)}" color="{color}"{rr}{b}'
            f'></Container></Positioned>')


def hseg(x1, x2, y, lw, color, dash=None):
    """水平线段；dash=(on,off) 时画虚线。"""
    a, b = min(x1, x2), max(x1, x2)
    if b - a < 0.5:
        return []
    if dash is None:
        return [rect(a, y - lw / 2, b - a, lw, color)]
    on, off = dash
    out, x = [], a
    while x < b:
        seg = min(b - x, on)
        if seg >= 1:
            out.append(rect(x, y - lw / 2, seg, lw, color))
        x += seg + off
    return out


def vseg(x, y1, y2, lw, color, dash=None):
    a, b = min(y1, y2), max(y1, y2)
    if b - a < 0.5:
        return []
    if dash is None:
        return [rect(x - lw / 2, a, lw, b - a, color)]
    on, off = dash
    out, y = [], a
    while y < b:
        seg = min(b - y, on)
        if seg >= 1:
            out.append(rect(x - lw / 2, y, lw, seg, color))
        y += seg + off
    return out


def arrow(cx, cy, direction, color, w=AW, h=AH, steps=ARROW_STEPS):
    """指向正方向的三角箭头，尖端在 (cx, cy)，由 steps 根逐级缩窄的矩形拼成。

    不做旋转（Transform 2×2 静默失效），四种方向都是沿坐标轴排列的窄条，
    窄端始终在尖端一侧：
      down   尖端在下（cy），条从上到下变窄
      up     尖端在上（cy），条从上到下变宽
      right  尖端在右（cx），条从左到右变窄
      left   尖端在左（cx），条从左到右变宽
    """
    out: list[str] = []
    k = h / steps
    if direction == "down":
        for i in range(steps):
            ww = w * (steps - i) / steps
            out.append(rect(cx - ww / 2, cy - h + i * k, ww, k + 0.5, color))
    elif direction == "up":
        for i in range(steps):
            ww = w * (i + 1) / steps
            out.append(rect(cx - ww / 2, cy + i * k, ww, k + 0.5, color))
    elif direction == "right":
        for i in range(steps):
            hh = w * (steps - i) / steps
            out.append(rect(cx - h + i * k, cy - hh / 2, k + 0.5, hh, color))
    else:  # left
        for i in range(steps):
            hh = w * (i + 1) / steps
            out.append(rect(cx + i * k, cy - hh / 2, k + 0.5, hh, color))
    return out


def poly(pts: list[list[float]], lw, color, arrow_dir, dash=None):
    """画一条轴对齐折线（含末端箭头）；末段为箭头让出 AH 的长度。"""
    out: list[str] = []
    last = len(pts) - 2
    for i, ((x1, y1), (x2, y2)) in enumerate(zip(pts[:-1], pts[1:])):
        ex, ey = x2, y2
        if i == last:
            if abs(x2 - x1) < 1e-9:
                ey = y2 - AH if y2 > y1 else y2 + AH
            else:
                ex = x2 - AH if x2 > x1 else x2 + AH
        if abs(y1 - ey) < 1e-9:
            out.extend(hseg(x1, ex, y1, lw, color, dash))
        else:
            out.extend(vseg(x1, y1, ey, lw, color, dash))
    out.extend(arrow(pts[-1][0], pts[-1][1], arrow_dir, color))
    return out


def node_box(node: dict) -> list[str]:
    """节点：圆角白盒 + 阶段色 2px 边框 + 编号（阶段色加粗）+ 标签（正文色）。"""
    x0, y0, x1, y1 = node["pixel_box"]
    col = node["stage_color"] or INK
    cy = (y0 + y1) / 2
    out = [rect(x0, y0, x1 - x0, y1 - y0, PANEL, NODE_R, f"2 SOLID {col}")]
    out.append(txt(x0 + 14, cy - 12, node["id"], 22, col, bold=True))
    out.append(txt(x0 + 58, cy - 12, node["label"], 22, INK))
    return out


def build_dsl(m: dict) -> str:
    nodes = {d["id"]: d for d in m["nodes"]}
    lp = m["longest_path"]
    c = m["counts"]
    cr = m["crossing_report"]
    L: list[str] = []
    add = L.append

    add(f'<Snapshot background="{BG}" type="png">')
    add(f'<Container width="{PW}" height="{PH}" color="{BG}">')
    add('<Stack fit="EXPAND" clipBehavior="NONE">')
    add(rect(0, 0, PW, PH, BG))

    # ------------------------------------------------------------- 标题
    add(txt(40, TITLE_TOP, "从需求到可复现交付 · 14 节点依赖解释图", 30, INK,
            bold=True))
    add(txt(40, SUB_TOP, f"{c['prerequisite_edges']} 条有向先决依赖（solid）· "
                         f"{c['feedback_edges']} 条反馈回路（虚线，不参与 DAG）· "
                         f"{c['topo_layers']} 个拓扑层", 20, SUB))
    add(txt(40, SUB2_TOP,
            f"最长先决路径 {lp['length_nodes']} 节点 / {lp['length_edges']} 边"
            f"（按节点数计，共 {lp['solutions_count']} 解）· 层号 = 从源节点到该节点的"
            f"最长先决路径节点数 − 1", 18, MUT))
    add(rect(40, SEP_Y, 1520, 1, GRID_LT))

    # ------------------------------------------------------------- 层号沟槽
    layer_nodes: dict[int, list[str]] = {}
    for d in m["nodes"]:
        layer_nodes.setdefault(d["topo_layer"], []).append(d["id"])
    for i in sorted(layer_nodes):
        cy = MD.ROW_Y[i]
        cnt = len(layer_nodes[i])
        add(txt(GUT_X, cy - 20, f"层 {i}", 18, SUB, bold=True))
        add(txt(GUT_X, cy + 4, f"{cnt} 节点", 18, WEAK))

    # ------------------------------------------------------------- 边（线段 + 箭头）
    tips: list[str] = []
    for e in m["prerequisite_edges"]:
        tips.extend(poly(e["path"], LW, e["color"], e["arrow"]["direction"]))
    for e in m["feedback_edges"]:
        tips.extend(poly(e["path"], LW, e["color"], e["arrow"]["direction"],
                         dash=DASH))

    # 反馈边图内短标签：写在各自回环内侧，颜色与虚线同族，面板给出完整解释
    for e in m["feedback_edges"]:
        x, y = FB_LAB_POS[(e["from"], e["to"])]
        short = e["meaning"].split("：", 1)[0]
        add(txt(x, y, f"{e['from']} → {e['to']} · {short}", 18, FB_INK,
                bold=True))

    # ------------------------------------------------------------- 节点（压在线段之上）
    for d in sorted(m["nodes"], key=lambda z: (z["topo_layer"],
                                                -z["pixel_center"][0])):
        L.extend(node_box(d))

    # 边与箭头画在节点之上：箭头体在节点框外（尖端咬合在框边缘），不会被边框压住
    L.extend(tips)

    # ------------------------------------------------------------- 右侧说明面板
    add(rect(RP_X, RP_Y, RP_W, RP_H, PANEL, 12, "1 SOLID " + PANEL_BD))
    add(txt(RP_X + 24, RP_Y + 14, "图例与读图规则", 20, INK, bold=True))
    add(txt(RP_X + 24, RP_Y + 50, "阶段颜色仅作语义分组，不参与图论计算", 18, MUT))

    # 节点样例
    # 说明：面板内容总高必须落在 RP_H 内。此前 y=RP_Y+90、阶段块前 +34 会让第二张
    # 反馈卡占到 y=792，而面板底边在 784，卡片越出 8px（v5 实测行 784..791 仍是卡片
    # 底色 #FEF3E2）。把样例上移到 +82、阶段块前缩到 +28，共省 18px，卡片底收到 778。
    y = RP_Y + 82
    add(rect(RP_X + 24, y - 2, 56, 20, PANEL, 5, "2 SOLID " + GRID))
    add(txt_box(RP_X + 24, y - 2, 56, 20, "N01", 18, INK, bold=True,
                align="CENTER"))
    add(txt(RP_X + 92, y + 2, "节点 = 编号 + 标签，字号 22", 18, SUB))

    # 两种线型
    y += 38
    L.extend(poly([[RP_X + 24, y + 10], [RP_X + 78, y + 10]], LW, EDGE_C,
                  "right"))
    add(txt(RP_X + 92, y + 2,
            f"先决依赖（{c['prerequisite_edges']} 条，实线，层号单调递增）",
            18, SUB))

    y += 38
    L.extend(poly([[RP_X + 24, y + 10], [RP_X + 78, y + 10]], LW, FB_C, "right",
                  dash=DASH))
    add(txt(RP_X + 92, y + 2,
            f"反馈关系（{c['feedback_edges']} 条，虚线 + 专用色，反向回指）",
            18, SUB))

    # 交叉规则
    y += 38
    add(rect(RP_X + 24, y - 4, RP_W - 48, 1, GRID_LT))
    y += 18
    add(txt(RP_X + 24, y, "交叉线未落在节点上时不构成新依赖", 18, SUB))
    y += 24
    add(txt(RP_X + 24, y,
            f"本布局逐段比对 {cr['pairs_checked']} 对边组合，交叉 "
            f"{cr['total_crossings']} 处", 18, WEAK))

    # 阶段色块
    y += 28
    for st in m["stages"]:
        add(rect(RP_X + 24, y + 2, 14, 14, st["color"], 4))
        add(txt(RP_X + 48, y, st["name"], 18, INK, bold=True))
        # 右对齐盒必须把左缘定位在 (右缘 − 盒宽)，否则盒会越出面板
        add(txt_box(RP_X + RP_W - 24 - 170, y, 170, 20,
                    "  ".join(st["nodes"]), 18, MUT))
        y += 26

    # ---- 反馈回路：图内解释 ----
    y += 22
    add(rect(RP_X + 24, y - 4, RP_W - 48, 1, GRID_LT))
    y += 20
    add(txt(RP_X + 24, y, "反馈回路：图内解释", 20, FB_INK, bold=True))
    y += 40
    card_h = 98
    for e in m["feedback_edges"]:
        short, body = e["meaning"].split("：", 1)
        # 在第一个中文逗号处断行（限定在 8..22 字之间，避免断在半句话里）
        comma = body.find("，")
        cut = comma + 1 if 8 <= comma <= 22 else 18
        add(rect(RP_X + 20, y - 8, RP_W - 40, card_h, FB_BG, 8))
        add(rect(RP_X + 20, y - 8, 3, card_h, FB_C, 2))
        add(txt(RP_X + 36, y, f"{e['from']} {nodes[e['from']]['label']}"
                                f"  →  {e['to']} {nodes[e['to']]['label']}",
                18, FB_C, bold=True))
        add(txt(RP_X + 36, y + 22, short, 18, FB_INK, bold=True))
        add(txt(RP_X + 36, y + 46, body[:cut], 18, SUB))
        add(txt(RP_X + 36, y + 68, body[cut:], 18, SUB))
        y += card_h + 8

    # ------------------------------------------------------------- 底部：最长路径与规模
    add(rect(BP_X, BP_Y, BP_W, BP_H, PANEL, 12, "1 SOLID " + PANEL_BD))
    add(txt(BP_X + 24, BP_Y + 10,
            f"最长先决路径（按节点数计）· {lp['length_nodes']} 节点 / "
            f"{lp['length_edges']} 边 · 共 {lp['solutions_count']} 解",
            20, INK, bold=True))
    add(txt(BP_X + 24, BP_Y + 36,
            "仅由 solid_edges 组成；feedback_edges 全程不参与计算", 18, MUT))

    sy = BP_Y + 60
    for i, s in enumerate(lp["solutions"]):
        add(rect(BP_X + 24, sy - 4, 62, 26, CHIP_BG, 6, "1 SOLID " + PANEL_BD))
        add(txt_box(BP_X + 24, sy - 4, 62, 26, f"解 {i + 1}", 18, SUB,
                    bold=True, align="CENTER"))
        add(txt(BP_X + 100, sy, " → ".join(s["sequence"]), 18, INK))
        sy += 30

    add(rect(BP_X + 24, BP_Y + 128, 1472, 1, GRID_LT))
    add(txt(BP_X + 24, BP_Y + 136,
            f"规模：{c['nodes']} 节点 · {c['topo_layers']} 个拓扑层"
            f"（层 0 → 层 {c['topo_layers'] - 1}）· {c['prerequisite_edges']} "
            f"条先决边 · {c['feedback_edges']} 条反馈边 · 源 {c['source_nodes'][0]}"
            f" · 汇 {c['sink_nodes'][0]} · 最大入度 {c['max_indegree']} · "
            f"最大出度 {c['max_outdegree']}", 18, SUB))
    add(txt(BP_X + 24, BP_Y + 158,
            "读图规则：交叉线未落在节点上时不构成新的依赖；反馈边反向回指 N08，"
            "若计入会产生环并破坏层号，故按题面另行标出，用虚线与专用颜色区分。",
            18, MUT))

    add("</Stack>")
    add("</Container>")
    add("</Snapshot>")
    return "\n".join(L) + "\n"


def main() -> None:
    _, tmp = IO.dirs()
    m = json.loads((tmp / "model.json").read_text(encoding="utf-8"))["model"]
    dsl = build_dsl(m)
    print(f"DSL {len(dsl)} B, {dsl.count('<Positioned')} Positioned, "
          f"{dsl.count('<')} nodes")
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1-preview"
    final = "--final" in sys.argv
    if final:
        rec = IO.submit(dsl, label=f"A06 {ver}（正式交付）",
                        rid=f"req-a06-{ver.replace('-', '')}-final",
                        dsl_version=ver, kind="render",
                        out_png="dependency-map.png",
                        out_dsl="dependency-map.snapshot")
    else:
        rec = IO.submit(dsl, label=f"A06 {ver}",
                        rid=f"req-a06-{ver.replace('-', '')}",
                        dsl_version=ver, kind="draft")
    print("HTTP", rec["http_status"], "bytes", rec["response_bytes"],
          "ct", rec["content_type"], "t",
          round(rec.get("elapsed_ms", 0) / 1000, 2), "s")
    if rec.get("error_summary"):
        print("ERROR", rec["error_summary"])
        return
    if final:
        out = IO.dirs()[0]
        for f in ("dependency-map.png", "dependency-map.snapshot"):
            print("交付 →", (out / f).relative_to(IO.ROOT))
    else:
        import shutil
        prev = IO.dirs()[1] / "preview" / f"{ver}.png"
        prev.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(IO.dirs()[1] / "responses" / f"{rec['request_id']}.body",
                        prev)
        print("preview →", prev.relative_to(IO.ROOT))


if __name__ == "__main__":
    main()
