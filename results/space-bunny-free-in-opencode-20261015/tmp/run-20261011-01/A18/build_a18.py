#!/usr/bin/env python
"""A18 守恒对象的三幕视觉叙事：1600×1000，两种叙事构图 A/B，参数化生成。

启动基准：总任务根 (suite_root)。无附加输入，文案与数值写在题面。

**守恒约束（写进代码而不是只写进说明）**
  * 15 个信息单元 U01–U15 的颜色与直径 36 在三幕之间**恒定**；
  * 3 个处理节点 N01–N03 的基准尺寸 96×96、填充色、内框样式在三幕之间恒定；
  * 「过载」只通过**间距 / 连线密度 / 节点有限形变**表达，
    绝不通过增删单元或缩小单元；构建脚本用断言守住这三条。
  * 每个单元在每幕都参与构图，且与其它单元、节点的圆心距满足非重叠。

**两种叙事构图**
  A「径向」：以 N01 为圆心，单元分布在同心环上；幕一环半径大而分散，
    幕二环半径收紧且内环几乎贴住节点（拥堵），幕三分成三簇。
  B「流向」：左→右单流；幕一三列五行的宽队列汇入一个节点，幕二压成紧块，
    幕三分成三条支路。
两版都出1600×1000 实际预览后再选。
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
DRAFTS = "tmp/run-20261011-01/A18/drafts"

W, H = 1600, 1000
MARGIN = 40
TITLE = "同一个信息系统 · 三幕负载叙事"

# ---------------------------------------------------------------- 守恒对象
UNIT_D = 36
UNIT_R = UNIT_D / 2
UNITS = [{"id": f"U{i:02d}", "color": c} for i, c in enumerate(
    ["#2563EB"] * 5 + ["#EA7C2D"] * 5 + ["#94A3B8"] * 5, start=1)]
UNIT_COLOR = {u["id"]: u["color"] for u in UNITS}

NODE_BASE_W, NODE_BASE_H = 96, 96
NODE_FILL, NODE_INNER, NODE_EDGE = "#1D3ED8", "#0B1736", "#7DA7F5"
NODES = ["N01", "N02", "N03"]
LINK_COLOR = "#B9C4D6"

# ---------------------------------------------------------------- 版面
PANEL_Y, PANEL_H = 104, 856
PANEL_W, PANEL_GAP = 484, 34
PANEL_X = [MARGIN + i * (PANEL_W + PANEL_GAP) for i in range(3)]
INNER_L, INNER_R = 28, 456          # 相对面板的左右内边距
INNER_T, INNER_B = 176, 928         # 相对面板的上下内边距

ACT_NAMES = ["第一幕 · 集中", "第二幕 · 过载", "第三幕 · 重新分配"]

# ---------------------------------------------------------------- 图元
def unit(cx, cy, color, d=UNIT_D):
    return (f'<Positioned left="{cx - d/2:.2f}" top="{cy - d/2:.2f}" width="{d}" height="{d}">'
            f'<ClipOval><Container width="{d}" height="{d}" color="{color}"/></ClipOval>'
            f'</Positioned>')


def node(x, y, w, h):
    r = round(w * 0.229, 1)
    iw, ih = round(w * 0.42), round(h * 0.42)
    ix, iy = round((w - iw) / 2), round((h - ih) / 2)
    r2 = round(min(iw, ih) * 0.233, 1)
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w}" height="{h}">'
            f'<Container width="{w}" height="{h}" color="{NODE_FILL}" borderRadius="{r}">'
            f'<Stack fit="EXPAND">'
            f'<Positioned left="{ix}" top="{iy}" width="{iw}" height="{ih}">'
            f'<Container width="{iw}" height="{ih}" color="{NODE_INNER}" borderRadius="{r2}" '
            f'border="3 SOLID {NODE_EDGE}"/></Positioned>'
            f'</Stack></Container></Positioned>')


def node_trim(nw, nh, ux, uy):
    """从节点中心沿方向 (ux,uy) 到矩形边界的距离 + 4px 间隙。

    首版用「外接圆半径 = hypot(w,h)/2」作为内缩量，对形变节点过于保守：
    幕二内环 8 个单元到节点的距离只有 86px，扣掉 18 + 68.9 后连线长度为负，
    于是 8 条连线被整条丢弃——那些单元看上去就是「没有接收节点」。
    改按矩形真实边界裁短后，每条连线都刚好抵到节点边缘。"""
    ax, ay = abs(ux), abs(uy)
    tx = (nw / 2) / ax if ax > 1e-9 else 1e9
    ty = (nh / 2) / ay if ay > 1e-9 else 1e9
    return min(tx, ty) + 4


def link(x1, y1, x2, y2, color=LINK_COLOR, w=3, trim_a=23, trim_b=53):
    """两点连线；两端按单元半径+间隙、节点半径+间隙裁短，保证线不压圆、不压节点。"""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L <= trim_a + trim_b + 2:
        return ""
    ux, uy = dx / L, dy / L
    ax, ay = x1 + ux * trim_a, y1 + uy * trim_a
    bx, by = x2 - ux * trim_b, y2 - uy * trim_b
    L2 = math.hypot(bx - ax, by - ay)
    ang = math.degrees(math.atan2(by - ay, bx - ax))
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    return (f'<Positioned left="{(ax+bx)/2 - L2/2:.2f}" top="{(ay+by)/2 - w/2:.2f}" '
            f'width="{L2:.2f}" height="{w}">'
            f'<Transform matrix="({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)" '
            f'alignment="CENTER"><Container width="{L2:.2f}" height="{w}" color="{color}" '
            f'borderRadius="{w/2:.1f}"/></Transform></Positioned>')


def txt(t, x, y, w, h, size, color, family="Inter,Noto Sans CJK SC", align=None, spacing=None):
    if '"' in t:
        q = "'"
    else:
        q = '"'
    at = f' fontSize="{size}" color="{color}" fontFamily="{family}"'
    if align:
        at += f' textAlign="{align}"'
    if spacing:
        at += f' letterSpacing="{spacing}"'
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Text{at} text={q}{t}{q}/></Positioned>')


def rect(x, y, w, h, color, radius=0, border=None):
    b = f' border="1.5 SOLID {border}"' if border else ""
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Container width="{w:.2f}" height="{h:.2f}" color="{color}" '
            f'borderRadius="{radius}"{b}/></Positioned>')


# ---------------------------------------------------------------- 构图 A：径向
# 环上的单元分配：故意让**每一环都混有三种颜色**。
# 首版按 ID 顺序铺环，结果内环全蓝、中环全橙、外环全灰——颜色与半径一一对应，
# 读者只要看颜色就知道它在第几圈，颜色就退化成了位置标签。
RING_UNITS = [["U01", "U08", "U12", "U04", "U15"],
              ["U06", "U02", "U13", "U09", "U14"],
              ["U03", "U11", "U07", "U05", "U10"]]
RING_OFFSETS = [0, 24, 48]     # 24° 错位：外环连线与内层圆心的最小夹角足够大，不从圆上穿过
# 幕二：内环 8 个、外环 7 个，两环颜色也都混排
TIGHT_INNER = ["U01", "U07", "U12", "U03", "U14", "U06", "U11", "U05"]
TIGHT_OUTER = ["U08", "U02", "U13", "U09", "U10", "U04", "U15"]


def layout_A() -> list[dict]:
    n1 = (242, 420)
    n2, n3 = (146, 716), (334, 716)
    nodes = {  # x, y, w, h
        "N01": (n1[0], n1[1], NODE_BASE_W, NODE_BASE_H),
        "N02": (n2[0], n2[1], NODE_BASE_W, NODE_BASE_H),
        "N03": (n3[0], n3[1], NODE_BASE_W, NODE_BASE_H),
    }
    acts = []

    # 幕一：三个同心环 112 / 152 / 192，每环 5 个、每环三色混排
    units = {}
    for ring, r in enumerate([112, 152, 192]):
        for k, uid in enumerate(RING_UNITS[ring]):
            a = math.radians(-90 + RING_OFFSETS[ring] + k * 72)
            units[uid] = (round(n1[0] + r * math.cos(a), 2),
                          round(n1[1] + r * math.sin(a), 2), "N01")
    acts.append({"act": 1, "name": ACT_NAMES[0], "nodes": dict(nodes), "units": units})

    # 幕二：两个收紧的环 86 / 146，8 + 7；N01 有限形变 112×78
    nodes2 = dict(nodes)
    nodes2["N01"] = (n1[0], n1[1], 112, 78)
    units = {}
    for k, uid in enumerate(TIGHT_INNER):
        a = math.radians(-90 + k * 45)
        units[uid] = (round(n1[0] + 86 * math.cos(a), 2),
                      round(n1[1] + 86 * math.sin(a), 2), "N01")
    for k, uid in enumerate(TIGHT_OUTER):
        # 外环相对内环错开 22.5°（内环相邻圆的中分角），连线尽量从内环圆缝里穿过
        a = math.radians(-67.5 + k * (360 / 7))
        units[uid] = (round(n1[0] + 146 * math.cos(a), 2),
                      round(n1[1] + 146 * math.sin(a), 2), "N01")
    acts.append({"act": 2, "name": ACT_NAMES[1], "nodes": nodes2, "units": units})

    # 幕三：三个节点各接 5 个，每组至少两种颜色
    assign = {"N01": ["U01", "U05", "U08", "U12", "U14"],
              "N02": ["U02", "U04", "U06", "U09", "U15"],
              "N03": ["U03", "U07", "U10", "U11", "U13"]}
    nodes3 = {"N01": (242, 300, NODE_BASE_W, NODE_BASE_H),
              "N02": (146, 716, NODE_BASE_W, NODE_BASE_H),
              "N03": (334, 716, NODE_BASE_W, NODE_BASE_H)}
    # 每组 5 个单元的扇形：弧间距 2r·sin(step/2) ≥ 36，且连线长度 = r − 23 − node_trim > 1
    fans = {"N01": (-145, -35, 100), "N02": (84, 174, 100), "N03": (6, 96, 100)}
    units = {}
    for nid, ids in assign.items():
        cx, cy = nodes3[nid][0], nodes3[nid][1]
        a0, a1, r = fans[nid]
        for j, uid in enumerate(ids):
            a = math.radians(a0 + (a1 - a0) * j / (len(ids) - 1))
            units[uid] = (round(cx + r * math.cos(a), 2), round(cy + r * math.sin(a), 2), nid)
    acts.append({"act": 3, "name": ACT_NAMES[2], "nodes": nodes3, "units": units})
    return acts


# ---------------------------------------------------------------- 构图 B：流向
def layout_B() -> list[dict]:
    nodes = {"N01": (330, 450, NODE_BASE_W, NODE_BASE_H),
             "N02": (146, 716, NODE_BASE_W, NODE_BASE_H),
             "N03": (334, 716, NODE_BASE_W, NODE_BASE_H)}
    acts = []

    # 幕一：三列五行的宽队列，全部指向右侧的 N01
    units = {}
    order = [(c, r) for c in range(3) for r in range(5)]
    # 行首从 236 起：最后一排到 N02/N03 顶边(668)仍有 32px，避免圆与节点贴死
    for i, (c, r) in enumerate(order):
        units[f"U{i+1:02d}"] = (56 + c * 62, 236 + r * 100, "N01")
    acts.append({"act": 1, "name": ACT_NAMES[0], "nodes": dict(nodes), "units": units})

    # 幕二：同一批单元压成 N01 左侧的紧块，N01 有限形变
    nodes2 = dict(nodes)
    nodes2["N01"] = (336, 450, 112, 78)
    units = {}
    for i, (c, r) in enumerate(order):
        # 紧块整体左移，避免最右一列压到形变后的 N01（x 280…392）
        units[f"U{i+1:02d}"] = (160 + c * 38, 326 + r * 62, "N01")
    acts.append({"act": 2, "name": ACT_NAMES[1], "nodes": nodes2, "units": units})

    assign = {"N01": ["U01", "U05", "U08", "U12", "U14"],
              "N02": ["U02", "U04", "U06", "U09", "U15"],
              "N03": ["U03", "U07", "U10", "U11", "U13"]}
    nodes3 = dict(nodes)
    nodes3["N01"] = (242, 300, NODE_BASE_W, NODE_BASE_H)
    units = {}
    for nid, ids in assign.items():
        cx, cy = nodes3[nid][0], nodes3[nid][1]
        a0, a1, r = {"N01": (-145, -35, 100), "N02": (84, 174, 100),
                     "N03": (6, 96, 100)}[nid]
        for j, uid in enumerate(ids):
            a = math.radians(a0 + (a1 - a0) * j / (len(ids) - 1))
            units[uid] = (round(cx + r * math.cos(a), 2), round(cy + r * math.sin(a), 2), nid)
    acts.append({"act": 3, "name": ACT_NAMES[2], "nodes": nodes3, "units": units})
    return acts


LAYOUTS = {"A": layout_A, "B": layout_B}


# ---------------------------------------------------------------- 校验
def check(acts: list[dict]) -> dict:
    rep = {"acts": []}
    ok = True
    for a in acts:
        pts = {uid: (p[0], p[1]) for uid, p in a["units"].items()}
        # 守恒：单元集合、颜色、直径
        assert sorted(pts) == sorted(UNIT_COLOR), f"幕 {a['act']} 单元集合不守恒"
        for uid, (x, y) in pts.items():
            assert INNER_L <= x - UNIT_R and x + UNIT_R <= INNER_R, \
                f"幕 {a['act']} {uid} 越出左右内边距"
            assert INNER_T <= y - UNIT_R and y + UNIT_R <= INNER_B, \
                f"幕 {a['act']} {uid} 越出上下内边距"
        # 单元两两不重叠
        min_uu = 1e9
        ids = sorted(pts)
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                x1, y1 = pts[ids[i]]
                x2, y2 = pts[ids[j]]
                d = math.hypot(x2 - x1, y2 - y1)
                min_uu = min(min_uu, d)
                assert d >= UNIT_D - 0.01, f"幕 {a['act']} {ids[i]}–{ids[j]} 重叠 ({d:.2f})"
        # 节点外包框
        nb = {k: [v[0] - v[2] / 2, v[1] - v[3] / 2, v[0] + v[2] / 2, v[1] + v[3] / 2]
              for k, v in a["nodes"].items()}
        min_un = 1e9
        for uid, (x, y) in pts.items():
            for nid, (x0, y0, x1, y1) in nb.items():
                dx = max(x0 - x, 0, x - x1)
                dy = max(y0 - y, 0, y - y1)
                d = math.hypot(dx, dy)
                min_un = min(min_un, d)
                assert d >= UNIT_R - 0.01, f"幕 {a['act']} {uid} 与 {nid} 重叠 ({d:.2f})"
        loads = {}
        for uid, p in a["units"].items():
            loads.setdefault(p[2], []).append(uid)
        colors = {n: sorted({UNIT_COLOR[u] for u in v}) for n, v in loads.items()}
        # 每个单元都必须有一条真正画得出来的连线（长度 > 0），否则看上去就是「无接收节点」
        link_len = {}
        for uid, (x, y) in pts.items():
            nid = a["units"][uid][2]
            nx, ny, nw, nh = a["nodes"][nid]
            L = math.hypot(x - nx, y - ny)
            tb = node_trim(nw, nh, (x - nx) / L, (y - ny) / L) if L > 1e-9 else 0
            link_len[uid] = round(L - UNIT_R - 5 - tb, 2)
            assert link_len[uid] > 1, \
                f"幕 {a['act']} {uid} 的连线长度为 {link_len[uid]}，等于没有画出来"
        rep["acts"].append({
            "act": a["act"], "unit_count": len(pts),
            "min_unit_unit_distance_px": round(min_uu, 2),
            "min_unit_node_distance_px": round(min_un, 2),
            "min_link_length_px": min(link_len.values()),
            "link_length_px": link_len,
            "loads": {n: sorted(v) for n, v in loads.items()},
            "load_sizes": {n: len(v) for n, v in loads.items()},
            "colors_per_node": colors,
            "node_bbox": {k: [round(x, 2) for x in v] for k, v in nb.items()},
        })
        # 幕三约束
        if a["act"] == 3:
            for n, v in loads.items():
                assert len(v) == 5, f"幕三 {n} 收到 {len(v)} 个单元，应为 5"
                assert len(colors[n]) >= 2, f"幕三 {n} 只有一种颜色"
        else:
            for n, v in loads.items():
                if n != "N01":
                    assert len(v) == 0, f"幕 {a['act']} 的 {n} 不该收到单元"
            assert len(loads.get("N01", [])) == 15, f"幕 {a['act']} N01 应收到 15 个"
    rep["ok"] = ok
    return rep


# ---------------------------------------------------------------- 出图
def build(layout_key: str) -> tuple[str, dict]:
    acts = LAYOUTS[layout_key]()
    rep = check(acts)
    b = [rect(0, 0, W, H, "#F1F5F9")]
    b.append(rect(0, 0, W, 8, "#1D3ED8"))
    b.append(txt(TITLE, MARGIN, 34, 900, 44, 30, "#0F172A",
                 "Inter Semi Bold,Noto Sans CJK SC"))
    b.append(rect(MARGIN, 88, W - 2 * MARGIN, 1, "#CBD5E1"))

    for ai, a in enumerate(acts):
        px = PANEL_X[ai]
        b.append(rect(px, PANEL_Y, PANEL_W, PANEL_H, "#FFFFFF", 20, "#E2E8F0"))
        b.append(txt(a["name"], px + INNER_L, PANEL_Y + 26, 420, 34, 26,
                     "#1D3ED8", "Inter Semi Bold,Noto Sans CJK SC"))
        b.append(rect(px + INNER_L, PANEL_Y + 64, PANEL_W - INNER_L - INNER_R, 1, "#E2E8F0"))
        for nid in NODES:                      # 先画连线，避免压住后面的节点与圆
            nx, ny, nw, nh = a["nodes"][nid]
            for uid, p in a["units"].items():
                if p[2] != nid:
                    continue
                ux, uy = p[0] - nx, p[1] - ny
                L = math.hypot(ux, uy)
                trim_b = node_trim(nw, nh, ux / L, uy / L) if L > 1e-9 else 53
                b.append(link(px + p[0], PANEL_Y + p[1], px + nx, PANEL_Y + ny,
                              trim_a=UNIT_R + 5, trim_b=trim_b))
        for uid, p in a["units"].items():
            b.append(unit(px + p[0], PANEL_Y + p[1], UNIT_COLOR[uid]))
        for nid in NODES:
            nx, ny, nw, nh = a["nodes"][nid]
            b.append(node(px + nx - nw / 2, PANEL_Y + ny - nh / 2, nw, nh))

    dsl = (f'<Snapshot type="png">\n<Container width="{W}" height="{H}" color="#F1F5F9">'
           f'<Stack fit="EXPAND">{"".join(b)}</Stack></Container>\n</Snapshot>\n')
    return dsl, rep


def main() -> None:
    key = sys.argv[1] if len(sys.argv) > 1 else "A"
    ver = sys.argv[2] if len(sys.argv) > 2 else "v1"
    d = BASE / DRAFTS
    d.mkdir(parents=True, exist_ok=True)
    dsl, rep = build(key)
    (d / f"a18-layout{key}-{ver}.snapshot").write_text(dsl, encoding="utf-8")
    (d / f"a18-layout{key}-{ver}-check.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"layout {key}: bytes={len(dsl.encode())}")
    for a in rep["acts"]:
        print(f"  幕{a['act']}: 单元{a['unit_count']} 最小单元距{a['min_unit_unit_distance_px']} "
              f"最小单元-节点距{a['min_unit_node_distance_px']} 负载{a['load_sizes']}")


if __name__ == "__main__":
    main()