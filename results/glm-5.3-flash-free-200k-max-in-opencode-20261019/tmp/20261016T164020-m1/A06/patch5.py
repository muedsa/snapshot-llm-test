# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = 'tmp/20261016T164020-m1/A06/build_a06.py'
t = open(p, encoding='utf-8').read()
start = t.index('# =====================================================================\n# 先决边')
t = t[:start]
new = '''# =====================================================================
# 先决边（实线 + 箭头；显式折线路由，弯折绕行避字）
# =====================================================================
EDGE_COL = "#6B7A93"
EDGE_PX = []

def port_l(nid):
    b = NODE_BOX[nid]
    return (b[0], (b[1] + b[3]) / 2)

def port_r(nid):
    b = NODE_BOX[nid]
    return (b[2], (b[1] + b[3]) / 2)

def port_t(nid):
    b = NODE_BOX[nid]
    return ((b[0] + b[2]) / 2, b[1])

def port_b(nid):
    b = NODE_BOX[nid]
    return ((b[0] + b[2]) / 2, b[3])

def seg_pts(points, color, thick=3.0):
    out = []
    for i in range(len(points) - 1):
        q = quad(points[i], points[i + 1], color, thick)
        if q:
            out.append(q)
    return out

def arrow_at(tip, direction, color):
    dd = {"R": (1, 0), "L": (-1, 0), "U": (0, -1), "D": (0, 1)}[direction]
    return arrowhead(tip[0] - dd[0] * 9, tip[1] - dd[1] * 9, direction, color)

# 显式折线路由（Option B：L2 上排 N05 / 下排 N04）
def ex(p):  return [[round(x, 2), round(y, 2)] for x, y in p]
E5P = [(port_l("N03")[0], NODE_BOX["N03"][3] - 16), (COLX[0] + 68, NODE_BOX["N03"][3] - 16),
       (COLX[0] + 68, 252), (COLX[2] + 70.4, 252), (COLX[2] + 70.4, 302),
       (NODE_BOX["N06"][0], 302)]
ROUTES = {
    ("N01", "N02"): ([port_r("N01"), port_l("N02")], "R"),
    ("N01", "N03"): ([port_r("N01"), port_l("N03")], "R"),
    ("N02", "N05"): ([port_r("N02"), port_l("N05")], "R"),
    ("N02", "N04"): ([port_r("N02"), (COLX[1] + 65.2, NODE_BOX["N02"][3]),
                      (COLX[1] + 65.2, 500), (COLX[2], 500), (COLX[2], NODE_BOX["N04"][1])], "U"),
    ("N03", "N06"): (E5P, "L"),
    ("N05", "N06"): ([port_r("N05"), port_l("N06")], "R"),
    ("N04", "N07"): ([port_r("N04"), port_l("N07")], "R"),
    ("N06", "N08"): ([port_r("N06"), (NODE_BOX["N08"][0], NODE_BOX["N08"][1] + 18)], "R"),
    ("N07", "N08"): ([port_r("N07"), (NODE_BOX["N08"][0], NODE_BOX["N08"][3] - 18)], "R"),
    ("N08", "N09"): ([port_r("N08"), port_l("N09")], "R"),
    ("N09", "N10"): ([port_r("N09"), port_l("N10")], "R"),
    ("N10", "N11"): ([port_r("N10"), port_l("N11")], "R"),
    ("N11", "N12"): ([port_r("N11"), port_l("N12")], "R"),
    ("N12", "N13"): ([port_r("N12"), port_l("N13")], "R"),
    ("N13", "N14"): ([port_r("N13"), port_l("N14")], "R"),
    ("N04", "N13"): ([port_b("N04"), (COLX[2], GY + GH - 28), (COLX[9], GY + GH - 28),
                      (COLX[9], NODE_BOX["N13"][3])], "U"),
}
assert set(ROUTES) == set(SOLID), set(ROUTES) ^ set(SOLID)

for (a, b), (pts, d) in ROUTES.items():
    for q in seg_pts(pts, EDGE_COL):
        S.append(q)
    tip = pts[-1]
    S.append(arrow_at(tip, d, EDGE_COL))
    EDGE_PX.append({"from": a, "to": b,
                    "polyline": ex(pts),
                    "arrow_tip": ex([tip])[0], "arrow_direction": d})

# =====================================================================
# 反馈边（红虚线；N09→N08 顶部环 / N10→N08 底部环；不参与排序）
# =====================================================================
FB_COL = "#C0392B"
FB_PX = []

def dash_run(x1, x2, y, color, thick=3.0, dash=9.0, gap=7.0):
    x = min(x1, x2)
    end = max(x1, x2)
    out = []
    while x < end:
        x2d = min(x + dash, end)
        out.append(quad((x, y), (x2d, y), color, thick))
        x = x2d + gap
    return out

def dash_vrun(y1, y2, x, color, thick=3.0, dash=9.0, gap=7.0):
    y = min(y1, y2)
    end = max(y1, y2)
    out = []
    while y < end:
        y2d = min(y + dash, end)
        out.append(quad((x, y), (x, y2d), color, thick))
        y = y2d + gap
    return out

F1P = [(port_t("N09")[0] - 24, NODE_BOX["N09"][1]), (port_t("N09")[0] - 24, 350),
       (port_t("N08")[0] - 5, 350), (port_t("N08")[0] - 5, NODE_BOX["N08"][1])]
F2P = [(port_b("N10")[0] - 4, NODE_BOX["N10"][3]), (port_b("N10")[0] - 4, 502),
       (port_b("N08")[0] - 5, 502), (port_b("N08")[0] - 5, NODE_BOX["N08"][3])]
for (a, b), pts in ((("N09", "N08"), F1P), (("N10", "N08"), F2P)):
    for i in range(len(pts) - 1):
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        if y1 == y2:
            for q in dash_run(x1, x2, y1, FB_COL):
                S.append(q)
        else:
            for q in dash_vrun(y1, y2, x1, FB_COL):
                S.append(q)
    S.append(arrow_at(pts[-1], "U", FB_COL))
    FB_PX.append({"from": a, "to": b, "polyline": ex(pts),
                  "arrow_tip": ex([pts[-1]])[0],
                  "drawn": "红虚线 9px 划线 / 7px 间隔，末端实心箭头指入目标节点"})

# 反馈标签（图内解释）
lab1 = "① 渲染失败 → 回到构建"
fit("反馈注1", lab1, 18, 220)
S.append(text(680, 322, lab1, 18, FB_COL, family=FAM_MIX, bold=True))
lab2 = "② 检查发现问题 → 返回构建"
fit("反馈注2", lab2, 18, 240)
S.append(text(700, 508, lab2, 18, FB_COL, family=FAM_MIX, bold=True))

# =====================================================================
# 底部读图说明卡
# =====================================================================
NOTE = (56, 824, 1488, 156)
S.append(rect(NOTE[0], NOTE[1], NOTE[2], NOTE[3], CARD, 16, BORD))
S.append(rect(56, 824, 5, 132, "#C0392B", 2))
S.append(text(84, 838, "读图要点", 20, INK, family=FAM_MIX, bold=True))
n1 = "① 反馈回路（红虚线）：首轮渲染失败 → 返回 DSL构建 重新生成；② 视觉检查发现问题 → 返回 DSL构建 修复后再渲染；反馈不参与拓扑排序。"
fit("注1", n1, 18, 1420)
S.append(text(84, 870, n1, 18, SUB, family=FAM_MIX))
n2 = "跨层先决边（字体查询→版式系统、数据计算→产物校验）沿顶部/底部绕行，不穿过任何节点；线线交叉处没有连接点，不构成新的依赖。"
fit("注2", n2, 18, 1420)
S.append(text(84, 898, n2, 18, SUB, family=FAM_MIX))
n3 = "最长先决路径（11 节点）：" + " → ".join(NODES[n] for n in LONGEST) + "。"
fit("注3", n3, 18, 1420)
S.append(text(84, 926, n3, 18, INK, family=FAM_MIX))

if WARN:
    print(json.dumps({"estw_overflows": WARN}, ensure_ascii=False, indent=2))
    raise SystemExit(f"{len(WARN)} 处文本估宽超限/几何告警，先修正再渲染")

# =====================================================================
# 写出 DSL
# =====================================================================
dsl = snapshot(BG, S)
(OUT / "dependency-map.snapshot").write_text(dsl, encoding="utf-8")

# =====================================================================
# graph-audit.json（题面专用审计；visual_checks 由实际看图后填入）
# =====================================================================
nodes_audit = []
for nid in sorted(NODES):
    b = NODE_BOX[nid]
    nodes_audit.append({
        "id": nid, "label": NODES[nid],
        "layer": lay[nid],
        "in_neighbors": NEI[nid]["in"], "out_neighbors": NEI[nid]["out"],
        "box_px": [round(b[0], 2), round(b[1], 2), round(b[2], 2), round(b[3], 2)],
        "phase": PH_OF[nid], "phase_color": PHASE[PH_OF[nid]],
    })
prereq_audit = []
for e in EDGE_PX:
    a, b = e["from"], e["to"]
    assert lay[b] > lay[a], (a, b, lay[a], lay[b])
    prereq_audit.append({
        "from": a, "to": b, "from_label": NODES[a], "to_label": NODES[b],
        "polyline_px": e["polyline"], "arrow_tip_px": e["arrow_tip"],
        "arrow_direction": e["arrow_direction"],
        "drawn": "实线 #6B7A93 3px + 实心箭头",
        "layer_check": f"L{lay[a]} → L{lay[b]}（指向更晚层）",
    })
feedback_audit = []
for e in FB_PX:
    feedback_audit.append({
        "from": e["from"], "to": e["to"],
        "from_label": NODES[e["from"]], "to_label": NODES[e["to"]],
        "polyline_px": e["polyline"], "arrow_tip_px": e["arrow_tip"],
        "drawn": e["drawn"],
        "not_part_of_dag": True,
        "meaning": "运行中的回退关系：不改变任何节点的拓扑层与先决次序",
    })
crossings = []
segs = []
for e in EDGE_PX + FB_PX:
    pl = e["polyline"]
    for i in range(len(pl) - 1):
        segs.append((e["from"] + "→" + e["to"], pl[i], pl[i + 1]))
def seg_int(s1, s2):
    (x1, y1), (x2, y2) = s1; (x3, y3), (x4, y4) = s2
    d = (x2 - x1) * (y4 - y3) - (y2 - y1) * (x4 - x3)
    if d == 0:
        return None
    t = ((x3 - x1) * (y4 - y3) - (y3 - y1) * (x4 - x3)) / d
    u = ((x3 - x1) * (y2 - y1) - (y3 - y1) * (x2 - x1)) / d
    if 0 < t < 1 and 0 < u < 1:
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None
for i in range(len(segs)):
    for j in range(i + 1, len(segs)):
        p = seg_int(segs[i][1:], segs[j][1:])
        if p:
            crossings.append({"edges": [segs[i][0], segs[j][0]],
                              "at_px": [round(p[0], 2), round(p[1], 2)],
                              "note": "交叉处无连接点，不构成新依赖"})
audit = {
    "schema_version": 1,
    "task_id": "A06",
    "path_base": "output_dir",
    "question": "十四节点依赖图与反馈回路",
    "inputs": {
        "path_base": "suite_root",
        "paths": ["tasks/A06-dependency-graph/inputs/graph.json"],
        "nodes_used": 14, "solid_edges_used": len(SOLID), "feedback_edges_used": len(FEEDBACK),
        "modifications": "无——节点/边按输入原值；布局与绕行是绘制决策，不改变图语义",
    },
    "topology": {
        "method": "以 solid_edges 为 DAG，按 最长前驱层 分层（Kahn 等价）；feedback_edges 不参与",
        "layer_count": MAXL + 1,
        "layers": {f"L{k}": sorted(v) for k, v in sorted(LAYERS.items())},
        "forward_only_check": "所有先决边 from 层 < to 层（无指向过去层的布局歧义）",
    },
    "nodes": nodes_audit,
    "prerequisite_edges": prereq_audit,
    "longest_path": {
        "node_sequence": LONGEST,
        "labels": [NODES[n] for n in LONGEST],
        "length_nodes": LLEN,
        "length_edges": LLEN - 1,
        "method": "DAG 最长路径动态规划（拓扑序、按节点数计）；并列最优取先出者",
        "alternative_same_length": ["N01", "N02", "N05", "N06", "N08", "N09", "N10",
                                    "N11", "N12", "N13", "N14"],
    },
    "feedback_edges": feedback_audit,
    "crossings": crossings,
    "legend": {
        "solid": "实线灰箭头 = 先决依赖（拓扑排序内）",
        "dashed_red": "红虚线 = 反馈回路（不参与排序，指回构建）",
        "phase": "节点左色条 = 阶段：准备/构图/构建/审校/收束",
    },
    "images": {
        "dependency-map.png": {"size": [1600, 1000], "dsl": "dependency-map.snapshot",
                               "product": "14 节点依赖与反馈解释图（层列 + 绕行 + 反馈环）"},
    },
    "visual_checks": [],
    "build_script": {"path_base": "suite_root", "path": f"tmp/{RUN_ID}/A06/build_a06.py"},
}
(OUT / "graph-audit.json").write_text(
    json.dumps(audit, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")

print(json.dumps({
    "snapshot_bytes": len(dsl.encode("utf-8")),
    "edges": len(EDGE_PX), "feedback": len(FB_PX),
    "longest": LONGEST, "crossings": len(crossings),
}, ensure_ascii=False))
'''
open(p, 'w', encoding='utf-8').write(t + new)
print('appended, total chars', len(t) + len(new))
