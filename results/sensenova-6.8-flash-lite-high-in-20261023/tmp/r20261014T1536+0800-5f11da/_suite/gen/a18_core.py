"""A18 守恒对象的三幕视觉叙事：几何计算 + DSL 生成（构图 A / 构图 B 两套）。

题面硬约束如何落到几何上：

* 三幕各 15 个信息单元（5 蓝 / 5 橙 / 5 灰），直径恒为 36，跨幕不增删不缩放；
* 同一组 3 个处理节点 N01–N03，形状、尺寸、配色三幕完全一致（不旋转、不变形，
  方向恒为 0°），身份特征 = 72×72 圆角方块 + 内部 40×40 描边「插槽」；
* 单元互不重叠、连线不遮圆、节点不压单元 —— 由 ``chain()`` 的贪心射线行走保证，
  再由 a18_check.py 用另一套独立计算复核；
* 全图只允许「总标题 + 三个幕名」四类文字，节点与单元不写任何解释文字；
* 关系不靠颜色推断：距离（环半径 / 排间距）、连线方向、构图位置三条通道同时给。

服务实测契约（A17 逼出，抄在这里免得再撞）：

* ``<Container>`` 与 ``<Positioned>`` 只允许一个子元素 —— 本文件每个 Positioned
  只包一个 Container，需要多个子元素时先包一层 ``<Stack>``；
* 根 ``<Stack>`` 不能直接做 ``<Snapshot>`` 的子节点 —— 外包 1600×1000 显式尺寸
  Container，否则 ``RENDER_ERROR Layout size is infinite``；
* 属性值与元素内容禁写字面 ``<`` 与 ``&``（解析器不做 HTML 实体解码）；
* 全程只用 ``Stack`` + ``Positioned``，不出现 ``Column > Row``
  （Column 的直接 Row 子节点不渲染且会中断其后兄弟）；
* 服务没有 ``<Line>``/``<Rect>``/``<Path>`` 标签（A13 实测不可用），
  ``<Transform>`` 的矩阵参数写法在缓存文档中查不到 —— 所以连线用直径 10、
  pitch 9 的圆点串（视觉上是虚线），不依赖任何旋转变换。

请求体上限 1048576 B（openapi.yaml 第 133–144 行，``413``），本图 DSL 约 40 KB。
"""
from __future__ import annotations

import math

# ---------------------------------------------------------------- 常量

CANVAS_W, CANVAS_H = 1600, 1000

UNIT_D = 36
UNIT_R = 18
NODE_S = 72
NODE_H = 36          # 半边长
NODE_INNER = 40
BEAD_D = 10
BEAD_R = 5
BEAD_STEP = 9        # 圆点串中心间距，直径 10 → 1px 缝隙，视觉上是虚线

C_BLUE = "#2563EB"
C_ORANGE = "#F97316"
C_GRAY = "#94A3B8"
C_NODE = "#0F172A"
C_NODE_INNER = "#64748B"
C_BEAD = "#475569"
C_CANVAS = "#FFFFFF"
C_PANEL = "#F8FAFC"
C_PANEL_BORDER = "#E2E8F0"
C_RULE = "#E2E8F0"
C_TEXT = "#0F172A"
FONT = "Noto Sans CJK SC,Inter"

TITLE = "守恒对象的三幕视觉叙事"
ACT_NAME = {1: "第一幕 · 集中", 2: "第二幕 · 过载", 3: "第三幕 · 重新分配"}

HEX = {"blue": C_BLUE, "orange": C_ORANGE, "gray": C_GRAY}
# U01–U15：颜色跨幕恒定，只有位置与接收节点会变
UNIT_COLOR = ["blue"] * 5 + ["orange"] * 5 + ["gray"] * 5
UNITS = [("U%02d" % (i + 1), UNIT_COLOR[i]) for i in range(15)]

# 幕一开放环 / 幕二紧贴环 / 幕三扇形
R_ACT1 = 150.0
R_ACT2 = 96.0
FAN_R = 180.0
FAN_ANGLES = (-25.0, -12.5, 0.0, 12.5, 25.0)

# 第三幕分配表：每节点 5 个单元，每组 3 色
ALLOC_A3 = [
    ("N01", ["U01", "U02", "U06", "U11", "U12"]),
    ("N02", ["U03", "U04", "U07", "U08", "U13"]),
    ("N03", ["U05", "U09", "U10", "U14", "U15"]),
]


def _r(v: float) -> int:
    """坐标取整：DSL 里写整数，几何校验也用同一组整数，不出现两套坐标。"""
    return int(round(v))


# ---------------------------------------------------------------- 几何

def ring(center, radius, n=15, start_deg=-90.0, step_deg=24.0):
    """环形 n 个位置：从正上方起、顺时针排列。相邻中心距 = 2*R*sin(180°/n)。"""
    cx, cy = center
    out = []
    for i in range(n):
        a = math.radians(start_deg + i * step_deg)
        out.append((_r(cx + radius * math.cos(a)), _r(cy + radius * math.sin(a))))
    return out


def rect_gap(px, py, rx, ry, rw, rh):
    """点到矩形的距离（点在矩形内时为 0）。"""
    dx = max(rx - px, 0.0, px - (rx + rw))
    dy = max(ry - py, 0.0, py - (ry + rh))
    return math.hypot(dx, dy)


def chain(uc, nc, node_rects, unit_centers, stop_gap=6.0, max_len=4000.0):
    """从单元 uc 沿指向节点中心 nc 的射线放圆点串。

    规则：首颗圆点圆心距单元圆心 = UNIT_R + BEAD_R + 1；沿射线每 BEAD_STEP 一颗；
    一旦下一颗会进入任一节点矩形（留 stop_gap 余量）或与任一其他单元圆心距
    小于 UNIT_R + BEAD_R，就停止 —— 所以连线天然不会遮圆、不会压节点。

    返回 [(x, y), ...]，是面板局部坐标。
    """
    dx, dy = nc[0] - uc[0], nc[1] - uc[1]
    dist = math.hypot(dx, dy)
    if dist < 1:
        return []
    ux, uy = dx / dist, dy / dist
    out = []
    t = UNIT_R + BEAD_R + 1.0
    while t <= max_len:
        px, py = uc[0] + ux * t, uc[1] + uy * t
        if min(rect_gap(px, py, *r) for r in node_rects) < BEAD_R + stop_gap:
            break
        if min(math.hypot(px - p[0], py - p[1]) for p in unit_centers) < UNIT_R + BEAD_R:
            break
        out.append((_r(px), _r(py)))
        t += BEAD_STEP
    return out


# ---------------------------------------------------------------- 两套构图

def composition_a():
    """三条竖幅面板并排，阅读方向左→右。

    幕一：15 单元在半径 150 的开放环上，100% 指向 N01；
    幕二：同样的 15 单元被挤进半径 96 的紧贴环，仍然只有 N01 在收；
    幕三：三站各带一个 5 单元扇形，负载 5/5/5。
    """
    pw, ph = 480, 836
    idle = [("N02", (110, 740)), ("N03", (370, 740))]
    col_of = dict(UNITS)
    acts = []

    c1 = (240, 470)
    acts.append(dict(
        index=1, name=ACT_NAME[1], panel=(40, 116, pw, ph),
        label_box=(24, 22, 432, 40), label_size=26,
        nodes=[("N01", c1)] + idle,
        units=[(uid, col, HEX[col], p, "N01")
               for (uid, col), p in zip(UNITS, ring(c1, R_ACT1))]))

    # N01 与幕一同一位置：系统不变，只有单元向内坍缩 —— 「同一系统显现过载」
    c2 = (240, 470)
    acts.append(dict(
        index=2, name=ACT_NAME[2], panel=(560, 116, pw, ph),
        label_box=(24, 22, 432, 40), label_size=26,
        nodes=[("N01", c2)] + idle,
        units=[(uid, col, HEX[col], p, "N01")
               for (uid, col), p in zip(UNITS, ring(c2, R_ACT2))]))

    clusters = [("N01", (172, 216)), ("N02", (172, 460)), ("N03", (172, 704))]
    nodes3, units3 = [], []
    for (nid, nc), (_, ids) in zip(clusters, ALLOC_A3):
        nodes3.append((nid, nc))
        for k, uid in enumerate(ids):
            a = math.radians(FAN_ANGLES[k])
            p = (_r(nc[0] + FAN_R * math.cos(a)), _r(nc[1] + FAN_R * math.sin(a)))
            units3.append((uid, col_of[uid], HEX[col_of[uid]], p, nid))
    acts.append(dict(
        index=3, name=ACT_NAME[3], panel=(1080, 116, pw, ph),
        label_box=(24, 22, 432, 40), label_size=26,
        nodes=nodes3, units=units3))

    return dict(composition="A", mode="vertical", canvas=(CANVAS_W, CANVAS_H),
                title=TITLE, title_size=30, acts=acts,
                title_box=(48, 26, 1504, 60), rule_box=(48, 96, 1504, 2))


def composition_b():
    """三条横幅面板上下堆叠，阅读方向上→下。

    幕一：15 单元单排、间距 64，全部向右流入 N01；
    幕二：同样 15 单元压成间距 44 的紧贴排，紧贴 N01，只有排头连着线；
    幕三：三站各一列 5 单元，负载 5/5/5。
    """
    bw, bh = 1520, 294
    col_of = dict(UNITS)
    label = (24, 12, 520, 40)
    acts = []

    row1 = [(200 + 64 * i, 150) for i in range(15)]
    acts.append(dict(
        index=1, name=ACT_NAME[1], panel=(40, 96, bw, bh), label_box=label, label_size=24,
        nodes=[("N01", (1250, 150)), ("N02", (60, 110)), ("N03", (60, 230))],
        units=[(uid, col, HEX[col], p, "N01") for (uid, col), p in zip(UNITS, row1)]))

    row2 = [(1156 - 44 * i, 150) for i in range(15)]
    acts.append(dict(
        index=2, name=ACT_NAME[2], panel=(40, 401, bw, bh), label_box=label, label_size=24,
        nodes=[("N01", (1250, 150)), ("N02", (60, 110)), ("N03", (60, 230))],
        units=[(uid, col, HEX[col], p, "N01") for (uid, col), p in zip(UNITS, row2)]))

    groups = [(nid, gx, ids) for (nid, ids), gx in zip(ALLOC_A3, (270, 760, 1250))]
    nodes3, units3 = [], []
    for nid, gx, ids in groups:
        nodes3.append((nid, (gx - 90, 165)))
        for k, uid in enumerate(ids):
            units3.append((uid, col_of[uid], HEX[col_of[uid]],
                           (gx + 30, 165 - 88 + 44 * k), nid))
    acts.append(dict(index=3, name=ACT_NAME[3], panel=(40, 706, bw, bh),
                     label_box=label, label_size=24, nodes=nodes3, units=units3))

    return dict(composition="B", mode="horizontal", canvas=(CANVAS_W, CANVAS_H),
                title=TITLE, title_size=26, acts=acts,
                title_box=(48, 20, 1504, 56), rule_box=(48, 82, 1504, 2))


# ---------------------------------------------------------------- DSL

def circle(d, color):
    return '<Container width="%d" height="%d" shape="CIRCLE" color="%s"/>' % (d, d, color)


def text_el(s, size, color=C_TEXT):
    return '<Text fontFamily="%s" fontSize="%d" color="%s" text="%s"/>' % (FONT, size, color, s)


def node_dsl(pad):
    """节点 = 72×72 圆角方块 + 内部 40×40 描边「插槽」。三幕同形同尺寸同配色。"""
    return [
        '%s<Container width="%d" height="%d" color="%s" borderRadius="14" alignment="CENTER">'
        % (pad, NODE_S, NODE_S, C_NODE),
        '%s  <Container width="%d" height="%d" borderRadius="8" border="2 SOLID %s"/>'
        % (pad, NODE_INNER, NODE_INNER, C_NODE_INNER),
        '%s</Container>' % pad,
    ]


def render_dsl(scene):
    W, H = scene["canvas"]
    L = []
    L.append('<Snapshot type="png" background="%s">' % C_CANVAS)
    L.append('  <Container width="%d" height="%d">' % (W, H))
    L.append('    <Stack width="%d" height="%d" fit="EXPAND" clipBehavior="NONE">' % (W, H))

    tx, ty, tw, th = scene["title_box"]
    L.append('      <Positioned left="%d" top="%d" width="%d" height="%d">' % (tx, ty, tw, th))
    L.append('        <Container width="%d" height="%d" alignment="CENTER">' % (tw, th))
    L.append('          %s' % text_el(scene["title"], scene["title_size"]))
    L.append('        </Container>')
    L.append('      </Positioned>')

    rx, ry, rw, rh = scene["rule_box"]
    L.append('      <Positioned left="%d" top="%d" width="%d" height="%d">' % (rx, ry, rw, rh))
    L.append('        <Container width="%d" height="%d" color="%s"/>' % (rw, rh, C_RULE))
    L.append('      </Positioned>')

    for act in scene["acts"]:
        px, py, pw, ph = act["panel"]
        L.append('      <Positioned left="%d" top="%d" width="%d" height="%d">' % (px, py, pw, ph))
        L.append('        <Container width="%d" height="%d" color="%s" borderRadius="16" '
                 'border="1 SOLID %s">' % (pw, ph, C_PANEL, C_PANEL_BORDER))
        L.append('          <Stack width="%d" height="%d" fit="EXPAND" clipBehavior="NONE">'
                 % (pw, ph))
        lx, ly, lw, lh = act["label_box"]
        L.append('            <Positioned left="%d" top="%d" width="%d" height="%d">'
                 % (lx, ly, lw, lh))
        L.append('              <Container width="%d" height="%d" alignment="CENTER">' % (lw, lh))
        L.append('                %s' % text_el(act["name"], act["label_size"]))
        L.append('              </Container>')
        L.append('            </Positioned>')
        # 连线先画（压在底层）：直径 10、pitch 9 的圆点串
        for ch in act["chains"]:
            for bx, by in ch["beads"]:
                L.append('            <Positioned left="%d" top="%d" width="%d" height="%d">'
                         % (bx - BEAD_R, by - BEAD_R, BEAD_D, BEAD_D))
                L.append('              %s' % circle(BEAD_D, C_BEAD))
                L.append('            </Positioned>')
        # 信息单元
        for _uid, _cname, hexv, (cx, cy), _rid in act["units"]:
            L.append('            <Positioned left="%d" top="%d" width="%d" height="%d">'
                     % (cx - UNIT_R, cy - UNIT_R, UNIT_D, UNIT_D))
            L.append('              %s' % circle(UNIT_D, hexv))
            L.append('            </Positioned>')
        # 节点最后画
        for _nid, (cx, cy) in act["nodes"]:
            L.append('            <Positioned left="%d" top="%d" width="%d" height="%d">'
                     % (cx - NODE_H, cy - NODE_H, NODE_S, NODE_S))
            L.extend(node_dsl("            "))
            L.append('            </Positioned>')
        L.append('          </Stack>')
        L.append('        </Container>')
        L.append('      </Positioned>')

    L.append('    </Stack>')
    L.append('  </Container>')
    L.append('</Snapshot>')
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- 组装

def build(composition="A"):
    """返回 (scene, dsl)。scene 里的坐标为面板局部坐标，chains 已算好。"""
    scene = composition_a() if composition == "A" else composition_b()
    for act in scene["acts"]:
        node_rects = [(cx - NODE_H, cy - NODE_H, NODE_S, NODE_S)
                      for _, (cx, cy) in act["nodes"]]
        unit_centers = [p for _u, _c, _h, p, _r2 in act["units"]]
        node_center = {nid: c for nid, c in act["nodes"]}
        chains = []
        for uid, _cname, _hexv, uc, rid in act["units"]:
            chains.append({"unit": uid, "receiver": rid,
                           "beads": chain(uc, node_center[rid], node_rects, unit_centers)})
        act["chains"] = chains
    return scene, render_dsl(scene)


def summary(scene):
    """给审计与报告用的逐幕摘要（面板局部坐标）。"""
    out = []
    for act in scene["acts"]:
        per_node = {}
        for ch in act["chains"]:
            per_node.setdefault(ch["receiver"], []).append(ch["unit"])
        out.append({
            "act": act["index"],
            "label": act["name"],
            "panel_local": act["panel"],
            "nodes": [{"id": nid, "center_local": list(c),
                       "bbox_local": [c[0] - NODE_H, c[1] - NODE_H, NODE_S, NODE_S],
                       "size": [NODE_S, NODE_S], "border_radius": 14, "rotation_deg": 0,
                       "color": C_NODE, "inner_socket": [NODE_INNER, NODE_INNER, C_NODE_INNER],
                       "received": sorted(per_node.get(nid, [])),
                       "received_count": len(per_node.get(nid, []))}
                      for nid, c in act["nodes"]],
            "units": [{"id": uid, "color": cname, "hex": hexv, "center_local": list(p),
                       "diameter": UNIT_D, "receiver": rid,
                       "connector_beads": len(ch["beads"]),
                       "beads_local": [list(b) for b in ch["beads"]]}
                      for (uid, cname, hexv, p, rid), ch in
                      zip(act["units"], act["chains"])],
        })
    return out


if __name__ == "__main__":
    import json
    import sys

    comp = sys.argv[1] if len(sys.argv) > 1 else "A"
    sc, dsl = build(comp)
    print(json.dumps({
        "composition": comp,
        "dsl_bytes": len(dsl.encode("utf-8")),
        "bead_total": sum(len(c["beads"]) for a in sc["acts"] for c in a["chains"]),
        "unit_total": sum(len(a["units"]) for a in sc["acts"]),
        "node_total": sum(len(a["nodes"]) for a in sc["acts"]),
        "per_act_units": [len(a["units"]) for a in sc["acts"]],
        "per_act_nodes": [len(a["nodes"]) for a in sc["acts"]],
    }, ensure_ascii=False, indent=1))
