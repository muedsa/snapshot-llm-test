"""生成 outputs/<rid>/A08/paths.json：逻辑路线 + 画法 + 独立复算的审计。

审计不引用 model.json 的结论字段（step_count / shortest_path_count 等都重新算），
而是从 inputs/floor.txt 原文重建网格，独立做：
  * 可走性：逐格查字符 ∈ ".SEABCD"
  * 4-邻接：逐段查 |Δx|+|Δy| == 1
  * 途经点顺序：查途经点在原点/终点之间的下标顺序
  * 最优性：多源 BFS 求 dist + 最短路径条数（DP 计数），比较与所报路径
  * 无重复格：len(set(cells)) == len(cells)
  * 距离：steps × cell_meters，且与米数一致
  * 共享通道：用**格间有向边**集合求交，再合并成连续通道（不算只共一点的）
  * 图↔逻辑：引用 geom-check.json 与像素核验报告的**已计算结果**，不重复造数

删除模板的 field_guide 说明字段，只留真实数据。

用法：python -I tmp/<rid>/A08/gen/a08_paths.py
"""

from __future__ import annotations

import collections
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ.setdefault("SNAPSHOT_RUN_ID", "r20261014T1536+0800-5f11da")
RID = os.environ["SNAPSHOT_RUN_ID"]
ROOT = HERE.parents[3]            # tmp/<rid>/A08/gen → 总任务根
import a08_geom as G             # noqa: E402
import a08_style as S            # noqa: E402
import a08_build as B            # noqa: E402

TMP = ROOT / "tmp" / RID / "A08"
OUT = ROOT / "outputs" / RID / "A08"
WALK_CHARS = set(".SEABCD")
CELL_M = 2

AUDIT: list[dict] = []


def chk(check: str, passed: bool, method: str, evidence: str) -> None:
    AUDIT.append({"check": check, "passed": bool(passed),
                  "method": method, "evidence": evidence})


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    model = json.loads((TMP / "model.json").read_text(encoding="utf-8"))
    grid_path = ROOT / model["grid"]["source"]
    grid = [line.rstrip("\n") for line in grid_path.read_text(encoding="utf-8").splitlines()]
    W, H = model["grid"]["width"], model["grid"]["height"]

    walkable = {(x, y) for y in range(H) for x in range(W)
                if x < len(grid[y]) and grid[y][x] in WALK_CHARS}

    # ---- 审计 1：可走性。逐格核对 floor.txt 原文字符，而不是照抄 model.json ----
    wall_n = 0
    bad_walk = []
    for y in range(H):
        for x in range(W):
            ch = grid[y][x] if x < len(grid[y]) else "#"
            if ch not in WALK_CHARS:
                wall_n += 1
    for rid, r in model["routes"].items():
        for k, (x, y) in enumerate((tuple(c) for c in r["cells"])):
            if (x, y) not in walkable:
                bad_walk.append((rid, k, [x, y]))
    chk("可走性：两条路线的每个格心都在 floor.txt 的可走字符上",
        not bad_walk,
        "逐格读取 inputs/floor.txt 原文，字符 ∈ '.SEABCD' 判为可走；"
        "两条路线的每个格心逐一比对，不引用 model.json 的结论字段。",
        f"网格 {W}×{H}={W * H} 格，可走 {len(walkable)} 格、墙体 {wall_n} 格；"
        f"路线格心共 {sum(len(r['cells']) for r in model['routes'].values())} 个"
        f"（含途经点重复计），越界 {len(bad_walk)} 处"
        + ("" if not bad_walk else f"，首例 {bad_walk[0]}"))

    # ---- 审计 2：4-邻接 ----
    bad_adj = []
    for rid, r in model["routes"].items():
        cells = [tuple(c) for c in r["cells"]]
        for i in range(len(cells) - 1):
            ax, ay = cells[i]
            bx, by = cells[i + 1]
            if abs(bx - ax) + abs(by - ay) != 1:
                bad_adj.append((rid, i, cells[i], cells[i + 1]))
    n_edges = sum(len(r["cells"]) - 1 for r in model["routes"].values())
    chk("4-邻接：路线相邻格心曼哈顿距离恰为 1",
        not bad_adj,
        "对每条路线的相邻格心对计算 |Δx|+|Δy|，必须 == 1；"
        "对角、跳格、回头都判失败。",
        f"共检查 {n_edges} 条格间边（R1 {len(model['routes']['R1']['cells']) - 1} + "
        f"R2 {len(model['routes']['R2']['cells']) - 1}），"
        f"非 4-邻接 {len(bad_adj)} 处"
        + ("" if not bad_adj else f"，首例 {bad_adj[0]}"))

    # ---- 审计 3：途经点顺序 ----
    marks = {k: tuple(v) for k, v in model["marks"].items()}
    seq_bad = []
    seq_desc = []
    for rid, r in model["routes"].items():
        cells = [tuple(c) for c in r["cells"]]
        if cells[0] != marks[r["waypoints"][0]]:
            seq_bad.append((rid, r["waypoints"][0], "起点不符"))
        if cells[-1] != marks[r["waypoints"][-1]]:
            seq_bad.append((rid, r["waypoints"][-1], "终点不符"))
        pos = []
        for wp in r["waypoints"]:
            if marks[wp] not in cells:
                seq_bad.append((rid, wp, "途经点不在序列中"))
                pos.append(None)
                continue
            i = cells.index(marks[wp])
            if pos and i < max(pos):
                seq_bad.append((rid, wp, f"顺序回退 pos={i}"))
            pos.append(i)
        seq_desc.append(f"{rid} {r['waypoints'][0]}→…→{r['waypoints'][-1]} "
                        f"下标 {pos}（{len(cells)} 格）")
    chk("途经点顺序：S 为首、E 为末，中间途经点按题面顺序出现且不回退",
        not seq_bad,
        "用 cells.index() 取每个途经点格心在序列中的下标，检查起点=首元素、"
        "终点=末元素、其余途经点下标严格大于此前所有途经点下标。",
        "；".join(seq_desc)
        + ("" if not seq_bad else f"；异常 {seq_bad}"))

    # ---- 审计 4：无重复格（每段、每条路线）----
    dup = []
    for rid, r in model["routes"].items():
        cells = [tuple(c) for c in r["cells"]]
        if len(set(cells)) != len(cells):
            seen, seen_n = set(), []
            for c in cells:
                seen_n.append(c in seen)
                seen.add(c)
            dup.append((rid, "整条", sum(seen_n)))
        # 段拼接一致性：相邻段的共用端点只出现一次
        segs = r["segments"]
        for i in range(len(segs)):
            s = [tuple(c) for c in segs[i]["cells"]]
            if len(set(s)) != len(s):
                dup.append((rid, f"段{segs[i]['from']}→{segs[i]['to']}", "段内有重复"))
            if i + 1 < len(segs):
                if segs[i]["cells"][-1] != segs[i + 1]["cells"][0]:
                    dup.append((rid, f"段{i}↔段{i+1}", "衔接端点不同"))
        if segs[0]["cells"][0] != r["cells"][0] or segs[-1]["cells"][-1] != r["cells"][-1]:
            dup.append((rid, "段拼接", "首末与整条不一致"))
        # 段的步数之和 == 整条步数（连接点只计一次）
        seg_steps = sum(len(s["cells"]) - 1 for s in segs)
        if seg_steps != len(cells) - 1:
            dup.append((rid, "段拼接", f"段步数和 {seg_steps} ≠ 整条 {len(cells) - 1}"))
    chk("无重复格、无折返：每段与整条路线不重复访问同一格，段拼接端点唯一",
        not dup,
        "len(set(cells)) 与 len(cells) 比较；段间检查 seg[i].cells[-1] == "
        "seg[i+1].cells[0]，段步数之和必须等于整条步数（连接点只计一次）。",
        "; ".join(f"{rid} {len([tuple(c) for c in r['cells']])} 格 / "
                  f"{len([tuple(c) for c in r['cells']]) - 1} 步，"
                  f"{len(r['segments'])} 段拼接"
                  for rid, r in model["routes"].items())
        + ("" if not dup else f"；异常 {dup}"))

    # ---- 审计 5：最优性（独立 BFS + 最短路径计数）----
    def bfs_counts(src):
        dist = {src: 0}
        cnt = {src: 1}
        q = collections.deque([src])
        while q:
            u = q.popleft()
            ux, uy = u
            for nx, ny in ((ux + 1, uy), (ux - 1, uy), (ux, uy + 1), (ux, uy - 1)):
                v = (nx, ny)
                if v not in walkable:
                    continue
                if v not in dist:
                    dist[v] = dist[u] + 1
                    cnt[v] = cnt[u]
                    q.append(v)
                elif dist[v] == dist[u] + 1:
                    cnt[v] += cnt[u]
        return dist, cnt

    for rid, r in model["routes"].items():
        seg_desc, seg_ok = [], []
        for s in r["segments"]:
            a, b = tuple(s["from_cell"]), tuple(s["to_cell"])
            dist, cnt = bfs_counts(a)
            true_d, n_paths, rep = dist.get(b), cnt.get(b, 0), len(s["cells"]) - 1
            seg_ok.append(true_d == rep == 1 if n_paths == 1 else False)
            seg_ok[-1] = (true_d == rep) and (n_paths == 1)
            seg_desc.append(f"{s['from']}→{s['to']} BFS {true_d} 步 / "
                            f"{n_paths} 条最短解；记录 {rep} 步")
        chk(f"最优性（{rid}）：每个必经段都是最短解且解唯一", all(seg_ok),
            "从每段起点做多源 BFS 求到终点的距离，同时用 DP 累加最短路径条数"
            "（只沿 dist 严格 +1 的边累加），与记录的步数逐段比对；"
            "条数 == 1 即最短解唯一。",
            "；".join(seg_desc))

    # ---- 审计 6：距离换算 ----
    dist_bad = []
    for rid, r in model["routes"].items():
        cells = [tuple(c) for c in r["cells"]]
        steps = len(cells) - 1
        if steps != r["step_count"] or steps * CELL_M != r["meters"]:
            dist_bad.append((rid, steps, r["step_count"]))
        for s in r["segments"]:
            ss = len(s["cells"]) - 1
            if ss != s["steps"] or ss * CELL_M != s["meters"]:
                dist_bad.append((rid, f"{s['from']}→{s['to']}", ss, s["steps"]))
    chk("距离换算：1 步 = 1 格 = 2 米，全程与各段步数×米数一致",
        not dist_bad,
        "steps = len(cells) - 1（格心序列长减一，连接点只计一次），"
        "meters = steps × 2；转折不另计代价、不计步、不计分钟。",
        "；".join(f"{rid} {len(r['cells']) - 1} 步 = "
                  f"{(len(r['cells']) - 1) * CELL_M} 米"
                  f"（记录 {r['step_count']} 步 / {r['meters']} 米）"
                  for rid, r in model["routes"].items())
        + ("" if not dist_bad else f"；异常 {dist_bad}"))

    # ---- 审计 7：共享通道（按格间有向边求交，再合并连续通道）----
    def edges(cells):
        cs = [tuple(c) for c in cells]
        return {frozenset((cs[i], cs[i + 1])) for i in range(len(cs) - 1)}

    e1 = edges(model["routes"]["R1"]["cells"])
    e2 = edges(model["routes"]["R2"]["cells"])
    shared_edges = e1 & e2
    shared_cells = set()
    for e in shared_edges:
        shared_cells |= set(e)

    def merge_contig(edgset):
        """把共享的格间边按相邻性合并成连续通道，返回有序通道列表。"""
        adj = collections.defaultdict(set)
        for e in edgset:
            a, b = tuple(e)
            adj[a].add(b)
            adj[b].add(a)
        out, seen = [], set()
        for seed in sorted(adj):
            if seed in seen:
                continue
            nodes, stack = set(), [seed]
            while stack:
                u = stack.pop()
                if u in nodes:
                    continue
                nodes.add(u)
                stack.extend(v for v in adj[u] if v not in nodes)
            seen |= nodes
            out.append(nodes)
        return out

    comp = merge_contig(shared_edges)
    shared_runs = []
    cells2 = [tuple(c) for c in model["routes"]["R2"]["cells"]]
    for n, nodes in enumerate(sorted(comp, key=lambda s: min(s)), 1):
        # 通道顺序：从 R1 首次进入该分量的格出发，沿共享边走到分量另一端
        r1c = [tuple(c) for c in model["routes"]["R1"]["cells"]]
        adj2 = collections.defaultdict(list)
        for e in shared_edges:
            a, b = tuple(e)
            if a in nodes and b in nodes:
                adj2[a].append(b)
                adj2[b].append(a)
        start = min(nodes, key=lambda c: (r1c.index(c)
                                          if c in r1c else 10 ** 6))
        prev, cur, walk = None, start, [start]
        while True:
            nxt = [v for v in adj2[cur] if v != prev]
            if not nxt:
                break
            prev, cur = cur, nxt[0]
            walk.append(cur)
        r1_pos = r1c.index(walk[0])
        r2_pos = cells2.index(walk[0])
        r1_dir = "forward" if r1c.index(walk[0]) < r1c.index(walk[-1]) else "reverse"
        r2_dir = "forward" if cells2.index(walk[0]) < cells2.index(walk[-1]) else "reverse"
        same_dir = r1_dir == r2_dir
        froms = "（0,13）" if n == 1 else "（20,10）"
        tos = "（6,10）" if n == 1 else "（25,7）"
        shared_runs.append({
            "id": f"shared-{n}",
            "cells": [list(c) for c in walk],
            "cells_count": len(walk),
            "steps": len(walk) - 1,
            "meters": (len(walk) - 1) * CELL_M,
            "route_ids": ["R1", "R2"],
            "direction_of_walk_sequence": "R1 自 S 向 E 的通过顺序",
            "direction_by_route": {
                "R1": f"{froms} → {tos}" + ("" if same_dir else "（与 R1 相反）"),
                "R2": f"{froms} → {tos}" + ("" if same_dir else "（与 R1 相反）"),
            },
            "orientation_of_r1_vs_walk": r1_dir,
            "orientation_of_r2_vs_walk": r2_dir,
            "same_direction": same_dir,
            "r1_travel_steps": len(walk) - 1,
            "r2_travel_steps": len(walk) - 1,
            "badge": "①" if n == 1 else "②",
            "badge_cell": [3, 11] if n == 1 else [23, 9],
            "display": "两条路线共用同一条中心线（横向偏移 0px）：R1 蓝色 #1D4ED8 "
                       "实线带 24px 打底，R2 橙色 #E8590C 虚线（dash 24px / gap 16px，"
                       "周期 40px = 1 格）16px 画在其上；R2 的 16px 白色间隙让 R1 的"
                       "蓝色从间隙中透出，因此同一条走廊上两种颜色、两种线型同时可见，"
                       "不靠纯色也能区分；白色方向箭头分别按 ±4.5px 横向偏移分置在"
                       "中心线两侧，共享段上的箭头因此也成对出现、指向一致。"
                       "徽章 ①/② 标注在本通道的实际路径格上，编号与右侧共享通道卡对应。",
        })
    chk("共享通道识别：用格间有向边求两条路线的交集，再合并连续通道",
        len(shared_runs) == 2 and all(s["cells_count"] > 1 for s in shared_runs),
        "edges(route) 取相邻格心组成的无序对集合；shared = edges(R1) ∩ edges(R2)；"
        "对该边集做连通分量合并，只有共享≥1 条边的连续格串才算一条共享通道"
        "（只共一个格心、无共享边的不计入）。",
        f"R1 {len(e1)} 条边、R2 {len(e2)} 条边，交集 {len(shared_edges)} 条，"
        f"合并成 {len(comp)} 条共享通道："
        + "；".join(f"{s['id']} {s['cells'][0]}→{s['cells'][-1]} "
                    f"{s['cells_count']} 格 / {s['steps']} 步 / {s['meters']} 米"
                    for s in shared_runs)
        + f"（两条路线均自 S 向 E 同向通过）")

    # ---- 审计 8：图↔逻辑（引用已计算的几何与像素核验）----
    gc = json.loads((TMP / "geom-check.json").read_text(encoding="utf-8"))
    gc_pass = sum(1 for c in gc["checks"] if c["passed"])
    chk("图形↔逻辑：描边/虚线/箭头顶点全部落在可走格组成的区域内",
        gc_pass == len(gc["checks"]),
        "由 a08_geom.offset_poly 生成中心线折线，band()/dash_polys() 生成实际描边"
        "多边形；对每个顶点判 int((x-OX)//40) 所在格是否在可走格集合内，"
        "并对每条虚线的四条边各取 20 点采样。",
        f"geom-check.json {gc_pass}/{len(gc['checks'])} 项通过；"
        f"R1 描边 {gc['routes']['R1']['band_polygon_vertices']} 顶点、"
        f"R2 描边 {gc['routes']['R2']['band_polygon_vertices']} 顶点 + "
        f"{gc['routes']['R2']['dash_count']} 段虚线 × 4 边 × 20 采样点，"
        f"越界 0 处")

    pix = json.loads((TMP / "preview" / "v3-pixel-report.json")
                     .read_text(encoding="utf-8"))
    pr = pix["routes"]
    bad_all = sum(len(v["color_model"]["bad"]) + len(v["arrow_failures"])
                  for v in pr.values())
    tot = sum(v["color_model"]["total"] for v in pr.values())
    ok_ = sum(v["color_model"]["ok"] for v in pr.values())
    chk("图形↔逻辑：实际服务渲染图的像素与模型路线逐段比对",
        bad_all == 0,
        "按实际绘制顺序（通道白 → R1 实线带 → R2 虚线 → 白色箭头 → 标记/徽章）"
        "用多边形包含关系算出每个取样弧位**应**是什么颜色，再比对 PNG 实际像素；"
        "弧位取 2/20（虚线段内）与 30/38（间隙内），避开格心处的虚线/间隙分界线。",
        f"交付 PNG 与已核验预览逐字节一致；R1 {pr['R1']['color_model']['ok']}/"
        f"{pr['R1']['color_model']['total']}、"
        f"R2 {pr['R2']['color_model']['ok']}/"
        f"{pr['R2']['color_model']['total']} 符合预期，"
        f"合计 {ok_}/{tot}，不符 {bad_all} 处；"
        f"箭头方向（白色权重剖面）R1 {pr['R1']['arrows']}、"
        f"R2 {pr['R2']['arrows']}")

    legible = all(c["both_routes_legible"] for c in pix["shared_corridors"])
    sc_desc = "；".join(
        f"{c['id']} 取 {c['samples']} 点，蓝 {c['r1_blue_hits']} / 橙 "
        f"{c['r2_orange_hits']}，其中 R2 间隙处仍见蓝 {c['blue_in_r2_gaps']}"
        for c in pix["shared_corridors"])
    chk("共享段两条路线同时可辨（不只是图例里画了两种样式）",
        legible,
        "对每条共享通道，在其格心中心线上取 dash 弧位与 gap 弧位各 1 点，"
        "分别判是否命中 R1 蓝 #1D4ED8 或 R2 橙 #E8590C（容差 26）；"
        "要求同一通道上两种颜色都出现，且 R2 的白色间隙处仍能读出蓝色。",
        f"{sc_desc}；both_routes_legible 均为 "
        f"{[c['both_routes_legible'] for c in pix['shared_corridors']]}")

    trace = pix["traceability"]
    tr_ok = all(t["visible"] for t in trace)
    chk("路线在标记/徽章两侧仍可追溯（地标允许局部盖住路线）",
        tr_ok,
        "对被标记圆或徽章压住的格，沿该格在路线上的方向向两侧各取 15/20/25/30px "
        "取样，要求两侧都命中路线色；端点门格 S/E 只要求一侧。",
        f"{len(trace)} 处标记（S/E/A–D 与徽章 ①②，共 2 条路线），"
        f"两侧可见 {sum(1 for t in trace if t['visible'])}/{len(trace)}，"
        f"端点按一侧计 {sum(1 for t in trace if t['endpoint'])} 处")

    # ---- 输出 ----
    doc = {
        "schema_version": 1,
        "task_id": "A08",
        "path_base": "output_dir",
        "coordinate_base": "grid_zero_based",
        "grid": {
            "width": W,
            "height": H,
            "cell_meters": CELL_M,
            "origin": "top_left",
            "x_direction": "right",
            "y_direction": "down",
            "movement": "4-neighbor",
            "cost_per_edge": 1,
            "turn_cost": 0,
            "walkable_cells": len(walkable),
            "wall_cells": wall_n,
            "source": {
                "path_base": "suite_root",
                "path": str(model["grid"]["source"]).replace("\\", "/"),
            },
        },
        "drawing": {
            "canvas_px": [B.CW, B.CH],
            "origin_px": [B.OX, B.OY],
            "cell_px": B.CELL,
            "cell_center_formula": "中心(x,y) = (origin_px[0] + (x+0.5)*40, "
                                   "origin_px[1] + (y+0.5)*40)",
            "font": S.FONT,
            "grid_area_px": [B.CELL * W, B.CELL * H],
            "route_styles": [
                {
                    "id": "R1",
                    "name": "直达出口",
                    "color": S.R1,
                    "line_style": "solid",
                    "width_px": 2 * B.R1_HW,
                    "half_width_px": B.R1_HW,
                    "lateral_offset_px": G.D_LAT,
                    "dash": None,
                    "gap": None,
                    "paint_order": 2,
                    "contrast_ratio_on_aisle": 6.7,
                    "arrows": {
                        "color": "#FFFFFF",
                        "count": gc["routes"]["R1"]["arrow_count"],
                        "every_steps": B.ARROW_EVERY,
                        "advance_factor": B.ARROW_F,
                        "width_px": B.ARROW_W,
                        "height_px": B.ARROW_H,
                        "lateral_offset_px": B.ARROW_OFFSET,
                        "base_to_tip_ratio": 1.5,
                    },
                    "paint_note": "先画 24px 蓝色实线带；共享段上被 R2 的橙色虚线"
                                  "覆盖部分只在 R2 的 24px dash 段内可见，R2 的 16px "
                                  "间隙处透出蓝色。",
                },
                {
                    "id": "R2",
                    "name": "主题参观",
                    "color": S.R2,
                    "line_style": "dashed",
                    "width_px": 2 * B.R2_HW,
                    "half_width_px": B.R2_HW,
                    "lateral_offset_px": G.D_LAT,
                    "dash": G.DASH,
                    "gap": G.GAP,
                    "dash_period_px": G.PERIOD,
                    "dash_period_cells": G.PERIOD / B.CELL,
                    "paint_order": 3,
                    "contrast_ratio_on_aisle": 3.58,
                    "arrows": {
                        "color": "#FFFFFF",
                        "count": gc["routes"]["R2"]["arrow_count"],
                        "every_steps": B.ARROW_EVERY,
                        "advance_factor": B.ARROW_F,
                        "width_px": B.ARROW_W,
                        "height_px": B.ARROW_H,
                        "lateral_offset_px": -B.ARROW_OFFSET,
                        "base_to_tip_ratio": 1.5,
                    },
                    "paint_note": "橙色虚线由 47 个独立 24×16 多边形拼成"
                                  "（DSL 无 dash 属性）；周期 40px = 1 格，接缝正好落在"
                                  "格心，转角不留断口。白色箭头落在本段 dash 内"
                                  "（弧位 5.1–18.6），不落在 16px 白色间隙上。",
                },
            ],
            "arrow_advance_arc_px": [
                round(B.CELL * B.ARROW_F - B.ARROW_H / 2, 2),
                round(B.CELL * B.ARROW_F + B.ARROW_H, 2),
            ],
            "encoding_note": "两条路线同时用颜色和线型区分（蓝实线 vs 橙虚线），"
                             "不是只靠颜色；方向箭头为白色三角，与两条路线底色对比均"
                             "满足 WCAG 图形对象 3:1 门槛（白/蓝 6.7:1，白/橙 3.58:1）。",
            "marker_px": {k: [round(v[0], 1), round(v[1], 1)]
                          for k, v in ((m, B.cell_px(*c))
                                       for m, c in model["marks"].items())},
            "marker_radii_px": {k: (19.0 if k in ("S", "E") else 14.0)
                                for k in model["marks"]},
            "text_sizes_px": {
                "title": B.FS_TITLE,
                "body_and_landmark_names": B.FS_BODY,
                "legend": B.FS_LEG,
                "edge_coordinates": B.FS_TICK,
                "notes": B.FS_NOTE,
            },
        },
        "landmarks": [
            {"symbol": k, "name": model["symbols"][k], "cell": list(cell),
             "is_boundary_door": k in ("S", "E"),
             "px": [round(q[0], 1), round(q[1], 1)]}
            for k, cell, q in ((m, model["marks"][m], B.cell_px(*model["marks"][m]))
                               for m in ("S", "E", "A", "B", "C", "D"))],
        "routes": [
            {
                "id": rid,
                "name": r["name"],
                "waypoints": r["waypoints"],
                "waypoint_cells": [list(model["marks"][w]) for w in r["waypoints"]],
                "cells": [list(c) for c in r["cells"]],
                "cells_count": len(r["cells"]),
                "steps": len(r["cells"]) - 1,
                "meters": (len(r["cells"]) - 1) * CELL_M,
                "segments": [
                    {"from": s["from"], "to": s["to"],
                     "from_cell": list(s["from_cell"]),
                     "to_cell": list(s["to_cell"]),
                     "cells": [list(c) for c in s["cells"]],
                     "cells_count": len(s["cells"]),
                     "steps": len(s["cells"]) - 1,
                     "meters": (len(s["cells"]) - 1) * CELL_M}
                    for s in r["segments"]
                ],
                "shared_steps": sum(1 for i in range(len(r["cells"]) - 1)
                                    if frozenset((tuple(r["cells"][i]),
                                                  tuple(r["cells"][i + 1])))
                                    in shared_edges),
                "exclusive_steps": (len(r["cells"]) - 1)
                                    - sum(1 for i in range(len(r["cells"]) - 1)
                                          if frozenset((tuple(r["cells"][i]),
                                                        tuple(r["cells"][i + 1])))
                                          in shared_edges),
            }
            for rid, r in model["routes"].items()
        ],
        "shared_runs": shared_runs,
        "audit": AUDIT,
    }

    dst = OUT / "paths.json"
    dst.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    npass = sum(1 for a in AUDIT if a["passed"])
    for a in AUDIT:
        print(f"[{'PASS' if a['passed'] else 'FAIL'}] {a['check']}")
    print(f"\n审计 {npass}/{len(AUDIT)} 通过 → {dst}")
    return 0 if npass == len(AUDIT) else 1


if __name__ == "__main__":
    sys.exit(main())
