# -*- coding: utf-8 -*-
"""A18 三幕叙事生成器。
用法: python build_a18.py previews | final
- previews: 方案 alpha(引力场环) 与 beta(纵向车道) 各出 1600×1000 预览 DSL(临时) + 布局 JSON
- final: 按选定方案 beta 生成 three-act-story.snapshot(输出根) + 布局 JSON
守恒对象：15 单元(U01–U15, 5蓝/5橙/5灰, d36) + 3 节点(N01 圆角方 / N02 菱形 / N03 六边形, 基准一致)。
图内文字仅总标题+幕名。连线先画(在圆与节点之下)，线不遮圆。
"""
import io, sys, json, math, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

MODE = sys.argv[1] if len(sys.argv) > 1 else "previews"
RUN = "20261016T164020-m1"
OUTD = f"outputs/{RUN}/A18"
TMPD = f"tmp/{RUN}/A18"
os.makedirs(TMPD, exist_ok=True)
os.makedirs(OUTD, exist_ok=True)

BG = "#F7F6F2"; PANEL = "#FFFFFF"; INK = "#1B2440"; SUB = "#47506B"
LINEC = "#C9D0DC"; BORDER = "#E4E1D8"
UNIT = {"B": "#2F6FE0", "O": "#E8872E", "G": "#97A1AC"}
COLORS = ["B", "O", "G"]          # U_i 颜色 = COLORS[(i-1)%3]，跨幕不变
NODEC = "#2E3D57"                 # 三节点同色，身份靠形状
NAMES = ["幕一 · 集中", "幕二 · 过载", "幕三 · 重新分配"]
PANEL_X = [24.0, 549.333, 1074.667]
PW = 501.333
TITLE = "集中 → 过载 → 重新分配"

S = []

def R(x, y, w, h, color=None, radius=None, border=None):
    a = f'width="{w}" height="{h}"'
    if color: a += f' color="{color}"'
    if radius: a += f' borderRadius="{radius}"'
    if border: a += f' border="{border}"'
    S.append(f'<Positioned left="{x}" top="{y}"><Container {a} /></Positioned>')

def seg(x1, y1, x2, y2, w=2.0):
    """斜向线段：细四边形条带，ClipPath 裁剪（线层在圆/节点之下）。"""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    nx, ny = -dy / L * w / 2, dx / L * w / 2
    xa = min(x1, x2) - w / 2 - 2; xb = max(x1, x2) + w / 2 + 2
    ya = min(y1, y2) - w / 2 - 2; yb = max(y1, y2) + w / 2 + 2
    pw, ph = xb - xa, yb - ya
    pts = [(x1 - nx, y1 - ny), (x2 - nx, y2 - ny), (x2 + nx, y2 + ny), (x1 + nx, y1 + ny)]
    path = "M" + " L".join(f"{p[0]-xa:.3f} {p[1]-ya:.3f}" for p in pts) + " Z"
    S.append(f'<Positioned left="{xa:.3f}" top="{ya:.3f}"><SizedBox width="{pw:.3f}" height="{ph:.3f}">'
             f'<ClipPath path="{path}" clipBehavior="ANTI_ALIAS"><Container width="{pw:.3f}" height="{ph:.3f}" color="{LINEC}" /></ClipPath>'
             f'</SizedBox></Positioned>')

def vl(x, y0, y1, w=2.0):
    R(x - w / 2, min(y0, y1), w, abs(y1 - y0), LINEC)

def hl(x0, x1, y, w=2.0):
    R(min(x0, x1), y - w / 2, abs(x1 - x0), w, LINEC)

def draw_node(n):
    """返回 bbox [l,t,r,b] 与视觉描述。"""
    if n["shape"] == "rounded-square":
        w = h = 72 * n["scale"]
        x, y = n["cx"] - w / 2, n["cy"] - h / 2
        R(x, y, w, h, NODEC, radius=round(20 * n["scale"]))
        return [x, y, x + w, y + h]
    if n["shape"] == "diamond":
        w = h = 72.0
        path = "M36 0 L72 36 L36 72 L0 36 Z"
    else:
        w = h = 72.0
        path = "M36 0 L72 18 L72 54 L36 72 L0 54 L0 18 Z"
    x, y = n["cx"] - w / 2, n["cy"] - h / 2
    S.append(f'<Positioned left="{x}" top="{y}"><SizedBox width="{w}" height="{h}">'
             f'<ClipPath path="{path}" clipBehavior="ANTI_ALIAS">'
             f'<Container width="{w}" height="{h}" color="{NODEC}" /></ClipPath></SizedBox></Positioned>')
    return [x, y, x + w, y + h]

def draw_unit(cx, cy, color_key):
    R(cx - 18, cy - 18, 36, 36, UNIT[color_key], radius=18)

def node_def(nid, shape, cx, cy, scale=1.0):
    return dict(id=nid, shape=shape, cx=cx, cy=cy, scale=scale,
                borderRadius=(round(20 * scale) if shape == "rounded-square" else None),
                base=[72, 72], load=0, colors=[])
S_LIST = []

def unit_def(i, cx, cy, receiver, lane):
    key = COLORS[(i - 1) % 3]
    return dict(id=f"U{i:02d}", color=key, color_hex=UNIT[key], diameter=36,
                center=[cx, cy], receiver=receiver, lane=lane)

def min_dist(units):
    mm, pair = 1e9, None
    for i in range(len(units)):
        for j in range(i + 1, len(units)):
            (x1, y1), (x2, y2) = units[i]["center"], units[j]["center"]
            d = math.hypot(x1 - x2, y1 - y2)
            if d < mm: mm, pair = d, [units[i]["id"], units[j]["id"]]
    return mm, pair

# ── 方案 BETA：纵向车道队列 ──────────────────────────
def beta_act(ai, units, nodes, lines):
    """ai: 0,1,2"""
    cx = PANEL_X[ai] + PW / 2
    if ai == 0:      # 集中：15 单元 3 车道 → N01；N02/N03 空载
        n1 = node_def("N01", "rounded-square", cx, 800)
        n2 = node_def("N02", "diamond", 110, 890)
        n3 = node_def("N03", "hex", 440, 890)
        cols = [cx - 80, cx, cx + 80]; pitch = 96; groups = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8]
        for k in range(3):
            for j in range(5):
                u = unit_def(k * 5 + j + 1, cols[k], 800 - 88 - pitch * j, "N01", f"L{k+1}")
                units.append(u)
        for cxl in cols:
            vl(cxl, 800 - 88 - pitch * 4, 800)
            if abs(cxl - cx) > 0.01:
                hl(cxl, cx, 800)
        lines.append(dict(style="vpipe+elbow", columns=3, note="每列竖管穿过队列至节点行高，再水平汇入 N01；线层在圆/节点之下"))
        theme = "集中"
    elif ai == 1:    # 过载：同一拓扑，节距 40，N01 scale1.08
        n1 = node_def("N01", "rounded-square", cx, 800, scale=1.08)
        n2 = node_def("N02", "diamond", PANEL_X[1] + 86, 890)
        n3 = node_def("N03", "hex", PANEL_X[1] + PW - 86, 890)
        cols = [cx - 80, cx, cx + 80]; pitch = 40
        for k in range(3):
            for j in range(5):
                u = unit_def(k * 5 + j + 1, cols[k], 800 - 88 - pitch * j, "N01", f"L{k+1}")
                units.append(u)
        for cxl in cols:
            vl(cxl, 800 - 88 - pitch * 4, 800)
            if abs(cxl - cx) > 0.01:
                hl(cxl, cx, 800)
        lines.append(dict(style="vpipe+elbow", columns=3, note="与幕一同管线；节距 40px(边距4px)"))
        theme = "过载"
    else:            # 再分配：3 节点各自竖列
        xs = [cx - 175.333, cx, cx + 174.667]; pitch = 96
        n1 = node_def("N01", "rounded-square", xs[0], 800)
        n2 = node_def("N02", "diamond", xs[1], 800)
        n3 = node_def("N03", "hex", xs[2], 800)
        for k, nd in enumerate((n1, n2, n3)):
            for j in range(5):
                u = unit_def(k * 5 + j + 1, nd["cx"], 800 - 88 - pitch * j, nd["id"], f"L{k+1}")
                units.append(u)
            vl(nd["cx"], 800 - 88 - pitch * 4, 800)
        lines.append(dict(style="vpipe", columns=3, note="各节点自带竖管接自身队列；N01 形变复位"))
        theme = "重新分配"
    nodes.extend([n1, n2, n3])
    return theme, dict(pitch=pitch, lane_xs=cols if ai < 2 else xs, start_d=88)

def beta():
    acts, all_acts = [], []
    for ai in range(3):
        S.clear()
        x0 = PANEL_X[ai]
        R(x0, 122, PW, 854, PANEL, radius=14, border=f"1 SOLID {BORDER}")
        S.append(f'<Positioned left="{x0}" top="146" width="{PW}"><Text fontSize="24" color="{SUB}" '
                 f'fontFamily="Noto Sans CJK SC" fontStyle="BOLD" maxLines="1" overflow="CLIP" '
                 f'textAlign="CENTER">{NAMES[ai]}</Text></Positioned>')
        units, nodes, lines = [], [], []
        theme, meta = beta_act(ai, units, nodes, lines)
        bboxes = {}
        for nd in nodes:
            bboxes[nd["id"]] = draw_node(nd)
        for u in units:
            draw_unit(u["center"][0], u["center"][1], u["color"])
        for nd in nodes:
            nd["bbox"] = [round(v, 3) for v in bboxes[nd["id"]]]
            recv = [u for u in units if u["receiver"] == nd["id"]]
            nd["load"] = len(recv)
            nd["colors"] = sorted(u["color"] for u in recv)
        md, mp = min_dist(units)
        acts.append(dict(theme=theme, units=units, nodes=nodes, lines=lines, meta=meta,
                         min_unit_dist=round(md, 3), min_pair=mp))
        dsl = (f'<Snapshot background="{BG}" type="png"><Stack>'
               f'<SizedBox width="1600" height="1000" />'
               f'<Positioned left="0" top="30" width="1600"><Text fontSize="36" color="{INK}" '
               f'fontFamily="Noto Sans CJK SC" fontStyle="BOLD" maxLines="1" overflow="CLIP" '
               f'textAlign="CENTER">{TITLE}</Text></Positioned>'
               + "".join(S) + "</Stack></Snapshot>")
        all_acts.append(dsl)
    return all_acts, acts

# ── 方案 ALPHA：引力场环 ─────────────────────────────
def alpha_act(ai, units, nodes, lines):
    cx = PANEL_X[ai] + PW / 2
    if ai == 0:
        n1 = node_def("N01", "rounded-square", cx, 560)
        n2 = node_def("N02", "diamond", 110, 890)
        n3 = node_def("N03", "hex", 440, 890)
        rings = [(90, 0), (135, 18), (180, 36)]   # (半径, 角度基) 每个 5 单元
        for r, base in rings:
            for k in range(5):
                i = len(units) + 1
                th = math.radians(base + 72 * k)
                u = unit_def(i, cx + r * math.cos(th), 560 + r * math.sin(th), "N01", f"R{r}")
                units.append(u)
                seg(cx, 560, u["center"][0], u["center"][1])
        lines.append(dict(style="radial", count=15, note="15 条辐射线汇于 N01；线层在圆之下"))
        theme = "集中"
    elif ai == 1:
        n1 = node_def("N01", "rounded-square", cx, 565, scale=1.08)
        n2 = node_def("N02", "diamond", PANEL_X[1] + 86, 890)
        n3 = node_def("N03", "hex", PANEL_X[1] + PW - 86, 890)
        rings = [(72, 0), (110, 18), (148, 36)]
        for r, base in rings:
            for k in range(5):
                i = len(units) + 1
                th = math.radians(base + 72 * k)
                u = unit_def(i, cx + r * math.cos(th), 565 + r * math.sin(th), "N01", f"R{r}")
                units.append(u)
                seg(cx, 565, u["center"][0], u["center"][1])
        lines.append(dict(style="radial", count=15, note="同一角位排布整体内压；线层在圆之下"))
        theme = "过载"
    else:
        xs = [1112, 1310, 1508]; pitch_ring = 75
        n1 = node_def("N01", "rounded-square", xs[0], 700)
        n2 = node_def("N02", "diamond", xs[1], 700)
        n3 = node_def("N03", "hex", xs[2], 700)
        bases = [90, 54, 126]
        for nd, base in zip((n1, n2, n3), bases):
            for k in range(5):
                i = len(units) + 1
                th = math.radians(base + 72 * k)
                u = unit_def(i, nd["cx"] + pitch_ring * math.cos(th), 700 + pitch_ring * math.sin(th), nd["id"], f"P{nd['id']}")
                units.append(u)
                seg(nd["cx"], 700, u["center"][0], u["center"][1])
        lines.append(dict(style="radial", count=15, note="五边形环分别锚定三节点；N01 形变复位"))
        theme = "重新分配"
    nodes.extend([n1, n2, n3])
    return theme, dict(rings=(rings if ai < 2 else [(75, 0)]), node_y=(560 if ai == 0 else 565 if ai == 1 else 700))

def alpha():
    acts, all_acts = [], []
    for ai in range(3):
        S.clear()
        x0 = PANEL_X[ai]
        R(x0, 122, PW, 854, PANEL, radius=14, border=f"1 SOLID {BORDER}")
        S.append(f'<Positioned left="{x0}" top="146" width="{PW}"><Text fontSize="24" color="{SUB}" '
                 f'fontFamily="Noto Sans CJK SC" fontStyle="BOLD" maxLines="1" overflow="CLIP" '
                 f'textAlign="CENTER">{NAMES[ai]}</Text></Positioned>')
        units, nodes, lines = [], [], []
        theme, meta = alpha_act(ai, units, nodes, lines)
        bboxes = {}
        for nd in nodes:
            bboxes[nd["id"]] = draw_node(nd)
        for u in units:
            draw_unit(u["center"][0], u["center"][1], u["color"])
        for nd in nodes:
            nd["bbox"] = [round(v, 3) for v in bboxes[nd["id"]]]
            recv = [u for u in units if u["receiver"] == nd["id"]]
            nd["load"] = len(recv)
            nd["colors"] = sorted(u["color"] for u in recv)
        md, mp = min_dist(units)
        acts.append(dict(theme=theme, units=units, nodes=nodes, lines=lines, meta=meta,
                         min_unit_dist=round(md, 3), min_pair=mp))
        dsl = (f'<Snapshot background="{BG}" type="png"><Stack>'
               f'<SizedBox width="1600" height="1000" />'
               f'<Positioned left="0" top="30" width="1600"><Text fontSize="36" color="{INK}" '
               f'fontFamily="Noto Sans CJK SC" fontStyle="BOLD" maxLines="1" overflow="CLIP" '
               f'textAlign="CENTER">{TITLE}</Text></Positioned>'
               + "".join(S) + "</Stack></Snapshot>")
        all_acts.append(dsl)
    return all_acts, acts

def fmt(x):
    s = f"{x:.3f}".rstrip("0").rstrip(".")
    return s if s else "0"

def emit(act_dsls, acts, name, dest_dir):
    dsl = act_dsls[0] if len(act_dsls) == 1 else None
    # 每幕单独生成过，这里按幕输出单幕预览？——不：整体一次成图
    raise SystemExit("use emit_full")

def emit_full(act_dsls):
    """三幕合并为一张 1600×1000：每幕 DSL 去掉根/标题后拼接。"""
    return None

if MODE == "previews":
    for scheme in ("alpha", "beta"):
        S.clear()
        fn = alpha if scheme == "alpha" else beta
        act_dsls, acts = fn()
        # 重新逐幕装入同一画布
        S.clear()
        R(0, 0, 1600, 1000, BG)
        S.append(f'<Positioned left="0" top="30" width="1600"><Text fontSize="36" color="{INK}" '
                 f'fontFamily="Noto Sans CJK SC" fontStyle="BOLD" maxLines="1" overflow="CLIP" '
                 f'textAlign="CENTER">{TITLE}</Text></Positioned>')
        # 直接重画三幕
        S2_holder = S
        drawn = []
        for ai in range(3):
            before = len(S2_holder)
            # 复用各画幕函数（其会写全局 S）
            if scheme == "alpha":
                alpha_act(ai, [], [], [])
            else:
                beta_act(ai, [], [], [])
            drawn.append(S2_holder[before:])
            del S2_holder[before:]
        # 正式构建：先标题、再逐幕（线→节点→圆 顺序在画幕函数内已固定）
        S.clear()
        R(0, 0, 1600, 1000, BG)
        S.append(f'<Positioned left="0" top="30" width="1600"><Text fontSize="36" color="{INK}" '
                 f'fontFamily="Noto Sans CJK SC" fontStyle="BOLD" maxLines="1" overflow="CLIP" '
                 f'textAlign="CENTER">{TITLE}</Text></Positioned>')
        units_all, nodes_all = [], []
        for ai in range(3):
            units, nodes, lines = [], [], []
            x0 = PANEL_X[ai]
            R(x0, 122, PW, 854, PANEL, radius=14, border=f"1 SOLID {BORDER}")
            S.append(f'<Positioned left="{x0}" top="146" width="{PW}"><Text fontSize="24" color="{SUB}" '
                     f'fontFamily="Noto Sans CJK SC" fontStyle="BOLD" maxLines="1" overflow="CLIP" '
                     f'textAlign="CENTER">{NAMES[ai]}</Text></Positioned>')
            theme, meta = (alpha_act if scheme == "alpha" else beta_act)(ai, units, nodes, lines)
            bboxes = {}
            for nd in nodes:
                bboxes[nd["id"]] = draw_node(nd)
            for u in units:
                draw_unit(u["center"][0], u["center"][1], u["color"])
            for nd in nodes:
                nd["bbox"] = [round(v, 3) for v in bboxes[nd["id"]]]
                recv = [u for u in units if u["receiver"] == nd["id"]]
                nd["load"] = len(recv)
                nd["colors"] = sorted(u["color"] for u in recv)
            md, mp = min_dist(units)
            acts = [] if 'acts' not in dir() else acts
            if not acts or len(acts) < ai + 1:
                acts.append(None)
            acts[ai] = dict(theme=theme, units=units, nodes=nodes, lines=lines, meta=meta,
                            min_unit_dist=round(md, 3), min_pair=mp)
        dsl = (f'<Snapshot background="{BG}" type="png"><Stack>'
               f'<SizedBox width="1600" height="1000" />' + "".join(S) + "</Stack></Snapshot>")
        fnm = f"{TMPD}/preview-{scheme}.snapshot"
        open(fnm, "w", encoding="utf-8", newline="\n").write(dsl)
        json.dump(dict(scheme=scheme, title=TITLE, canvas=[1600, 1000], names=NAMES, acts=acts),
                  open(f"{TMPD}/{scheme}-layout.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        for a in acts:
            print(f"[{scheme}] {a['theme']}: min_unit_dist={a['min_unit_dist']} pair={a['min_pair']} "
                  f"loads={[(n['id'], n['load']) for n in a['nodes']]} pitch={a['meta'].get('pitch') or a['meta'].get('rings')}")
        print("written", fnm)
elif MODE == "final":
    S.clear()
    units_all, acts = [], []
    R(0, 0, 1600, 1000, BG)
    S.append(f'<Positioned left="0" top="30" width="1600"><Text fontSize="36" color="{INK}" '
             f'fontFamily="Noto Sans CJK SC" fontStyle="BOLD" maxLines="1" overflow="CLIP" '
             f'textAlign="CENTER">{TITLE}</Text></Positioned>')
    for ai in range(3):
        units, nodes, lines = [], [], []
        x0 = PANEL_X[ai]
        R(x0, 122, PW, 854, PANEL, radius=14, border=f"1 SOLID {BORDER}")
        S.append(f'<Positioned left="{x0}" top="146" width="{PW}"><Text fontSize="24" color="{SUB}" '
                 f'fontFamily="Noto Sans CJK SC" fontStyle="BOLD" maxLines="1" overflow="CLIP" '
                 f'textAlign="CENTER">{NAMES[ai]}</Text></Positioned>')
        theme, meta = beta_act(ai, units, nodes, lines)
        bboxes = {}
        for nd in nodes:
            bboxes[nd["id"]] = draw_node(nd)
        for u in units:
            draw_unit(u["center"][0], u["center"][1], u["color"])
        for nd in nodes:
            nd["bbox"] = [round(v, 3) for v in bboxes[nd["id"]]]
            recv = [u for u in units if u["receiver"] == nd["id"]]
            nd["load"] = len(recv)
            nd["colors"] = sorted(u["color"] for u in recv)
        md, mp = min_dist(units)
        acts.append(dict(theme=theme, units=units, nodes=nodes, lines=lines, meta=meta,
                         min_unit_dist=round(md, 3), min_pair=mp))
        units_all.extend(units)
    dsl = (f'<Snapshot background="{BG}" type="png"><Stack>'
           f'<SizedBox width="1600" height="1000" />' + "".join(S) + "</Stack></Snapshot>")
    out = f"{OUTD}/three-act-story.snapshot"
    open(out, "w", encoding="utf-8", newline="\n").write(dsl)
    json.dump(dict(scheme="beta", title=TITLE, canvas=[1600, 1000], names=NAMES, acts=acts),
              open(f"{TMPD}/final-layout.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("written", out)
    for a in acts:
        print(f"[final] {a['theme']}: min={a['min_unit_dist']} pair={a['min_pair']} "
              f"loads={[(n['id'], n['load'], n['colors']) for n in a['nodes']]}")
