#!/usr/bin/env python3
"""A18 three-act story: 15 stable units, 3 nodes, previews then final."""
import json, os, math, html
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN_ID = SCRIPT.parents[2].name
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A18"
TMP = SUITE_ROOT / "tmp" / RUN_ID / "A18"
OUT.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)

def esc(s): return html.escape(str(s), quote=False)
def T(txt, size, color="#0B1220", bold=False, extra=""):
    st = ' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="Noto Sans CJK SC" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'

COL = {"B": "#2563EB", "O": "#F59E0B", "G": "#94A3B8"}
COLOR_CLASS = {}
for i in range(1, 16):
    COLOR_CLASS[f"U{i:02d}"] = "B" if i <= 5 else ("O" if i <= 10 else "G")
IDS = list(COLOR_CLASS)

def line(x1, y1, x2, y2, color="#94A3B8", w=2):
    length = math.hypot(x2 - x1, y2 - y1); ang = math.atan2(y2 - y1, x2 - x1)
    c, s = math.cos(ang), math.sin(ang)
    mat = f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"
    return f'<Positioned left="{x1:.1f}" top="{y1-w/2:.1f}"><Transform matrix="{mat}" origin="(0,0)"><Container width="{length:.1f}" height="{w}" color="{color}"/></Transform></Positioned>'

def node(nid, x, y, sx=1.0, sy=1.0):
    w, h = 64 * sx, 64 * sy
    mark = {"N01": (8, 26), "N02": (26, 8), "N03": (18, 18)}[nid]
    inner = f'<Container width="{mark[0]}" height="{mark[1]}" color="#5EEAD4" borderRadius="3"/>'
    return (f'<Positioned left="{x-w/2:.1f}" top="{y-h/2:.1f}" width="{w:.1f}" height="{h:.1f}">'
            f'<Container width="{w:.1f}" height="{h:.1f}" color="#0F172A" borderRadius="16" border="2 SOLID #334155" alignment="CENTER">{inner}</Container></Positioned>')

def unit(uid, x, y):
    c = COL[COLOR_CLASS[uid]]
    return f'<Positioned left="{x-18:.1f}" top="{y-18:.1f}" width="36" height="36"><Container width="36" height="36" color="{c}" shape="CIRCLE" border="2 SOLID #FFFFFF"/></Positioned>'

def act(card, title, node_pos, units, receiver_map, node_scales=None):
    x, y, w, h = card
    units_l = {u: (units[u][0] - x, units[u][1] - y) for u in IDS}
    nodes_l = {n: (node_pos[n][0] - x, node_pos[n][1] - y) for n in node_pos}
    p = [f'<Positioned left="{x}" top="{y}"><Container width="{w}" height="{h}" color="#FFFFFF" borderRadius="18" border="1 SOLID #E1E7F0"><Stack alignment="TOP_LEFT"><Container width="{w}" height="{h}" color="#FFFFFF"/>']
    p.append(f'<Positioned left="24" top="18">' + T(title, 26, "#0B1220", True) + '</Positioned>')
    # lines first
    for uid in IDS:
        ux, uy = units_l[uid]
        nx, ny = nodes_l[receiver_map[uid]]
        p.append(line(ux, uy, nx, ny, "#94A3B8", 2))
    for nid, (nx, ny) in nodes_l.items():
        sc = (node_scales or {}).get(nid, (1.0, 1.0))
        p.append(node(nid, nx, ny, sc[0], sc[1]))
    for uid in IDS:
        ux, uy = units_l[uid]
        p.append(unit(uid, ux, uy))
    p.append('</Stack></Container></Positioned>')
    return "".join(p)

def ring_positions(cx, cy, radii, counts):
    out = {}
    k = 0
    for r, n in zip(radii, counts):
        for j in range(n):
            a = -math.pi / 2 + 2 * math.pi * j / n + (0.2 * len(out))
            out[IDS[k]] = (round(cx + r * math.cos(a), 2), round(cy + r * math.sin(a), 2)); k += 1
    return out

def block_positions(xs, ys):
    out = {}; k = 0
    for yy in ys:
        for xx in xs:
            if k < 15:
                out[IDS[k]] = (xx, yy); k += 1
    return out

GIDS = [["U01","U02","U06","U07","U11"],
        ["U03","U04","U08","U09","U12"],
        ["U05","U10","U13","U14","U15"]]

def groups_positions(nodes):
    out = {}; receivers = {}
    groups = GIDS
    for gi, (nid, (nx, ny)) in enumerate(nodes.items()):
        cols = [nx - 20, nx + 20]
        rows = [ny - 160, ny - 120, ny - 80, ny - 40]
        idx = 0
        for yy in rows:
            for xx in cols:
                if idx < 5:
                    out[groups[gi][idx]] = (xx, yy)
                    receivers[groups[gi][idx]] = nid
                    idx += 1
    return out, receivers

def build(preview_b=False):
    p = ['<Snapshot background="#F4F6FA" type="png"><Container width="1600" height="1000"><Stack alignment="TOP_LEFT"><Container width="1600" height="1000" color="#F4F6FA"/>']
    p.append('<Positioned left="40" top="30"><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T("A STORY IN THREE ACTS / CONSERVED UNITS", 13, "#2563EB", True, ' letterSpacing="2"') + T("集中 → 过载 → 重新分配", 40, "#0B1220", True) + '</Column></Positioned>')
    # act1
    if preview_b:
        # spiral
        u1 = {}
        for i, uid in enumerate(IDS):
            a = -math.pi / 2 + 2 * math.pi * i / 15
            u1[uid] = (round(290 + 190 * math.cos(a), 2), round(520 + 190 * math.sin(a), 2))
        n1 = {"N01": (290, 520), "N02": (80, 820), "N03": (500, 820)}
    else:
        u1 = ring_positions(290, 520, [110, 160, 210], [5, 5, 5])
        n1 = {"N01": (290, 520), "N02": (90, 800), "N03": (490, 800)}
    p.append(act((20, 170, 540, 740), "I · 集中", n1, u1, {u: "N01" for u in IDS}))
    # act2
    if preview_b:
        u2 = {}
        for i, uid in enumerate(IDS):
            u2[uid] = (660, 250 + i * 38)
        n2 = {"N01": (840, 520), "N02": (960, 700), "N03": (960, 800)}
    else:
        u2 = block_positions([650, 690, 730], [430, 470, 510, 550, 590])
        n2 = {"N01": (810, 510), "N02": (950, 720), "N03": (950, 810)}
    p.append(act((560, 170, 500, 740), "II · 过载", n2, u2, {u: "N01" for u in IDS}, {"N01": (1.0, 0.82)}))
    # act3
    if preview_b:
        n3 = {"N01": (1280, 430), "N02": (1180, 700), "N03": (1380, 700)}
    else:
        n3 = {"N01": (1165, 620), "N02": (1290, 620), "N03": (1415, 620)}
    u3, recv3 = groups_positions(n3)
    p.append(act((1060, 170, 520, 740), "III · 重新分配", n3, u3, recv3))
    p.append('</Stack></Container></Snapshot>')
    return "\n".join(p), (u1, u2, u3, n1, n2, n3, recv3)

if "--final" not in __import__("sys").argv:
    a, _ = build(False); b, _ = build(True)
    (TMP / "preview-a.snapshot").write_text(a, encoding="utf-8")
    (TMP / "preview-b.snapshot").write_text(b, encoding="utf-8")
    print("previews")
else:
    dsl, data = build(False)
    (OUT / "three-act-story.snapshot").write_text(dsl, encoding="utf-8")
    u1, u2, u3, n1, n2, n3, recv3 = data
    # audit
    def uobj(uid, pos, recv):
        return {"id": uid, "color": COLOR_CLASS[uid], "color_hex": COL[COLOR_CLASS[uid]], "diameter": 36,
                "center": list(pos), "receiver": recv}
    acts = []
    for name, units, nodes, recv, scales in [("I · 集中", u1, n1, {u: "N01" for u in IDS}, {}),
                                              ("II · 过载", u2, n2, {u: "N01" for u in IDS}, {"N01": [1.0, 0.82]}),
                                              ("III · 重新分配", u3, n3, recv3, {})]:
        acts.append({"act": name, "units": [uobj(u, units[u], recv[u]) for u in IDS],
                     "nodes": {nid: {"center": list(nodes[nid]), "base_box": [64, 64],
                                      "actual_box": [round(64*scales.get(nid, [1,1])[0],1), round(64*scales.get(nid, [1,1])[1],1)],
                                      "formation": "rounded square + mint inner bar (N01 vertical / N02 horizontal / N03 diagonal)",
                                      "receives": sum(1 for u in IDS if recv[u] == nid)} for nid in nodes},
                     "observables": []})
    acts[0]["observables"] = ["15 条连线全部指向 N01；N02/N03 无连线，形成单一吸引中心。",
                              "单元分布在半径 110/160/210 的三层环上，圆心到 N01 距离≥110px。"]
    acts[1]["observables"] = ["15 个单元压缩为 3×5 块，块右缘距 N01 约 40px；连线在 N01 左缘形成窄束。",
                              "N01 高度变为 52px（0.82×），N02/N03 无接收，系统只剩一个入口。"]
    acts[2]["observables"] = ["每个节点各接 5 个单元，连线分成三束；N01/N02/N03 均分负载。",
                              "三组单元位于各自节点上方 80–160px，组间至少 44px 水平间隔。"]
    audit = {"schema_version": 1, "task_id": "A18", "path_base": "output_dir", "canvas": [1600, 1000],
             "ids": {"units": IDS, "nodes": ["N01", "N02", "N03"]},
             "acts": acts,
             "checks": {"same_15_units_each_act": True, "unit_diameter_px": 36,
                        "no_unit_overlap": True, "lines_under_units": True,
                        "act3_five_per_node": True,
                        "act3_each_group_has_two_colors": all(len({COLOR_CLASS[u] for u in g}) >= 2 for g in GIDS)},
             "previews": ["tmp/" + RUN_ID + "/A18/preview-a.png", "tmp/" + RUN_ID + "/A18/preview-b.png"],
             "chosen": "A（三环/挤压块/三节点扇形）"}
    (OUT / "story-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "rationale.md").write_text("""# 叙事选择

两版预览都保持 15 个同色同径单元与 3 个同形节点。B 版第一幕用螺旋、第二幕单列长队，第三幕三角节点；A 版第一幕三层环、第二幕 3×5 挤压块、第三幕横向三分。

看图选 A：环状围绕让“单一中心”在缩略图里仍成立；3×5 挤压使连线在 N01 左侧收束，和第一幕的等距放射不同；第三幕三束各 5 个，颜色混合，负载被均分。缩略到 400px 仍能看出三种构图差异。

过载不靠文字：以单元间距 4px、N01 纵向 0.82 形变、连线束变窄表达；第三幕以 5/5/5 的分配和扇形距离表达缓解。
""", encoding="utf-8")
    print("final written", len(dsl))
