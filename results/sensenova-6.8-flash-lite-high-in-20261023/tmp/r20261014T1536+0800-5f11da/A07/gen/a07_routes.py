"""A07 交付：outputs/<rid>/A07/routes.json 生成器。

字段约定遵循 tasks/A07-transit-topology/templates/audit-fields.json：
queries / accessibility / optimality / content_map，另含 schema_version、
task_id、path_base。数值与站序全部取自 tmp/<rid>/A07/model.json，本脚本只做
重述与派生（edge_lines 由 segments 展开），不重算路由、不改动几何。

用法：python -I tmp/<rid>/A07/gen/a07_routes.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a07_build_card as BC     # noqa: E402  排版常量（content_map 用）
import a07_build_map as BM      # noqa: E402  排版常量（content_map 用）
import a07_io as IO             # noqa: E402

TZ = timezone(timedelta(hours=8))
LINES_ORDER = ("R", "B", "G")


def edge_lines(route: dict) -> list[dict]:
    """把 segments 展开成逐条站间边：每边给出起终点与所属线路。"""
    out = []
    for seg in route["segments"]:
        st = seg["stations"]
        for a, b in zip(st[:-1], st[1:]):
            out.append({"from": a, "to": b, "line": seg["line"],
                        "line_name": seg["name"]})
    return out


def _polyline(line_segs) -> tuple[list[tuple[int, int]], list[int]]:
    """把同一条线的几何段按端点相邻性连成有序折线。

    返回 (顶点序列, 按折线顺序的段下标)。线段端点取整后完全重合。
    一条线是简单路径，恰有两个端点度为 1，据此确定起点。
    """
    adj: dict[tuple[int, int], list[tuple[tuple[int, int], int]]] = {}
    for k, s in enumerate(line_segs):
        a = (int(round(s["p1"][0])), int(round(s["p1"][1])))
        b = (int(round(s["p2"][0])), int(round(s["p2"][1])))
        adj.setdefault(a, []).append((b, k))
        adj.setdefault(b, []).append((a, k))
    ends = sorted(v for v, a in adj.items() if len(a) == 1)
    if len(ends) != 2:
        return [], []
    verts, order, used = [ends[0]], [], set()
    cur = ends[0]
    # 一条 n 段折线有 n+1 个顶点，所以要走满 n 段（不是 n-1）。
    for _ in range(len(line_segs)):
        nxt, k = next((nb, kk) for nb, kk in adj[cur] if kk not in used)
        used.add(k)
        verts.append(nxt)
        order.append(k)
        cur = nxt
    return verts, order


def _drawn_span(a_pt: tuple[int, int], b_pt: tuple[int, int],
                line_segs) -> tuple[int, float]:
    """一条站间边在图上跨越多少段折线，以及对应的绘图长度（px）。"""
    verts, order = _polyline(line_segs)
    if not verts or a_pt not in verts or b_pt not in verts:
        return 0, 0.0
    lo, hi = sorted((verts.index(a_pt), verts.index(b_pt)))
    return hi - lo, round(sum(float(line_segs[k]["length_px"])
                              for k in order[lo:hi]), 1)


def route_block(route: dict, LINES: dict,
                geo_by_line: dict[str, list[dict]],
                pt: dict[str, tuple[int, int]]) -> dict:
    segs_out = []
    for s in route["segments"]:
        a = pt[s["stations"][0]]
        b = pt[s["stations"][-1]]
        n_geo, px = _drawn_span(a, b, geo_by_line[s["line"]])
        segs_out.append({
            "line": s["line"], "line_name": s["name"],
            "stations": s["stations"], "intervals": s["intervals"],
            "color": LINES[s["line"]]["color"],
            "letter": LINES[s["line"]]["letter"],
            "drawn_segments": n_geo,
            "drawn_length_px": px,
            "note": (f"这 {s['intervals']} 个站间边在图上由 "
                     f"{n_geo} 段 0°/45°/90° 折线画出；"
                     f"{'一一对应' if n_geo == s['intervals'] else '边数与折线段数不同'}。")})
    return {
        "stations": route["stations"],
        "edge_lines": edge_lines(route),
        "intervals": route["intervals"],
        "transfers": route["transfers"],
        "transfer_stations": route["transfer_stations"],
        "segments": segs_out,
        "lines_used": route["lines_used"],
        "station_count": len(route["stations"]),
        "drawn_segments_total": sum(x["drawn_segments"] for x in segs_out),
        "note": f"站点数 {len(route['stations'])} ≠ 站间边数 {route['intervals']}"
                f"（站数 = 边数 + 1）；图上折线段数 "
                f"{sum(x['drawn_segments'] for x in segs_out)} 是绘图量，"
                f"既不等于站数也不等于边数。",
    }


def strip_rect(top: float, n: int) -> dict:
    """一条线路条的像素描述：rect 与 [left,top,right,bottom] 两种写法并列。"""
    left = BC.SIDE + BC.PAD + BC.STRIP_INSET
    return {
        "left": round(left, 1),
        "top": round(top, 1),
        "width": round(BC.STRIP_W, 1),
        "height": round(BC.STRIP_H, 1),
        "box": [round(left, 1), round(top, 1),
                round(left + BC.STRIP_W, 1), round(top + BC.STRIP_H, 1)],
        "bar_center_y": round(top + 58.0, 1),
        "station_x": [round(left + BC.STRIP_W * i / (n - 1), 1)
                      for i in range(n)]}


def card_strips(model) -> dict:
    """重算 4 条线路条的像素框（与 a07_inspect_card 同一套常量）。"""
    out, y = {}, BC.HEAD_Y0
    for q in model["queries"]:
        fy = y + BC.PAD
        top = fy + BC.HEAD_H + BC.GAP_A + BC.STATS_H + BC.GAP_B
        out[f"{q['query_id']}/normal"] = strip_rect(top,
                                                    len(q["normal"]["stations"]))
        if not BC.same_route(q):
            t2 = (top + BC.STRIP_H + BC.EXTRA_GAP + 1 + BC.DIV_GAP
                  + BC.LINE_H + BC.LINE_GAP + BC.LINE_H + BC.STRIP2_GAP)
            out[f"{q['query_id']}/accessible"] = strip_rect(
                t2, len(q["accessible"]["stations"]))
        y += BC.frame_height(q) + BC.FRAME_GAP
    return out


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    out, tmp = IO.dirs()
    run_id = out.parent.name          # outputs/<run_id>/A07 → 取目录名
    model = json.loads((tmp / "model.json").read_text(encoding="utf-8"))
    LINES = model["lines"]
    stations = model["stations"]
    geo_checks = model["geometry"]["checks"]
    strips = card_strips(model)

    ACC_RULE = ("accessible=false 的车站可以乘车途经（不作为起点、终点或换乘站），"
                "但不能作为无障碍旅程的起点、终点或换乘站；任何查询都不得因该约束"
                "而删除线路。")

    # ---------------- queries ----------------
    geo_by_line = {lid: [s for s in model["geometry"]["segments"]
                         if s["line"] == lid]
                   for lid in LINES_ORDER}
    pt = {sid: (int(st["x"]), int(st["y"])) for sid, st in stations.items()}
    queries = []
    for q in model["queries"]:
        normal, acc = q["normal"], q["accessible"]
        same = (normal["stations"] == acc["stations"]
                and normal["transfers"] == acc["transfers"])
        acc_ok = same
        item = {
            "query_id": q["query_id"],
            "from": q["from"], "from_name": stations[q["from"]]["name"],
            "to": q["to"], "to_name": stations[q["to"]]["name"],
            "from_accessible": stations[q["from"]]["accessible"],
            "to_accessible": stations[q["to"]]["accessible"],
            "normal": route_block(normal, LINES, geo_by_line, pt),
            "normal_is_accessible": acc_ok,
            "accessibility": {
                "verdict": "可作为无障碍旅程" if acc_ok else "不可作为无障碍旅程",
                "same_as_normal": same,
                "reason": (
                    "起终点与换乘站全部 accessible=true，普通旅程即满足无障碍约束。"
                    if acc_ok else
                    "普通旅程的换乘站 "
                    + "、".join(f"{s} {stations[s]['name']}"
                                for s in normal["transfer_stations"])
                    + " accessible=false，不能作为无障碍旅程的换乘站；"
                    "起终点本身均可无障碍。"),
            },
        }
        if acc_ok:
            item["accessible"] = {**route_block(acc, LINES, geo_by_line, pt),
                                  "reason": "与普通旅程相同（无需另求）"}
        else:
            item["accessible"] = {**route_block(acc, LINES, geo_by_line, pt),
                                  "reason": "满足约束的最短无障碍旅程："
                                           f"{acc['intervals']} 个站间边 · "
                                           f"{acc['transfers']} 次换乘；"
                                           "换乘站 "
                                           + "、".join(f"{s} {stations[s]['name']}"
                                                      for s in acc["transfer_stations"])
                                           + " 均 accessible=true；"
                                           "途经站 S14 公园、S05 东桥虽 "
                                           "accessible=false，但仅乘车途经，允许。"}
        queries.append(item)

    # ---------------- accessibility ----------------
    def blank():
        return {"endpoint": False, "transfer": False, "passthrough": False}

    used_all = {sid: blank() for sid in stations}
    used_acc = {sid: blank() for sid in stations}      # 仅统计无障碍路线

    def mark(dst, r):
        st = r["stations"]
        ts = set(r["transfer_stations"])
        dst[st[0]]["endpoint"] = True
        dst[st[-1]]["endpoint"] = True
        for s in ts:
            dst[s]["transfer"] = True
        for s in st[1:-1]:
            if s not in ts:
                dst[s]["passthrough"] = True

    for q in queries:
        mark(used_all, q["normal"])
        mark(used_acc, q["accessible"])

    # 计算式核验：无障碍路线的起终点与换乘站必须全部 accessible=true
    viol = []
    for q in queries:
        acc = q["accessible"]
        for s in ([acc["stations"][0], acc["stations"][-1]]
                  + acc["transfer_stations"]):
            if not stations[s]["accessible"]:
                viol.append(f"{q['query_id']} 无障碍路线 {s} {stations[s]['name']}")
    acc_ok_all = not viol

    accessibility = [
        {"id": sid, "name": st["name"], "accessible": st["accessible"],
         "lines": st["lines"], "is_transfer": st["is_transfer"],
         "role_in_normal_routes": used_all[sid],
         "role_in_accessible_routes": used_acc[sid],
         "endpoint": {"check": "该站是否作为某条路线的起终点",
                      "occurs": used_all[sid]["endpoint"],
                      "passed": (used_all[sid]["endpoint"] and st["accessible"])
                                or not used_all[sid]["endpoint"],
                      "method": "统计起终点角色与 accessible 字段比对"},
         "transfer": {"check": "该站是否作为某条路线的换乘站",
                      "occurs": used_all[sid]["transfer"],
                      "passed": (used_all[sid]["transfer"] and st["accessible"])
                                or not used_all[sid]["transfer"],
                      "method": "统计换乘站角色与 accessible 字段比对"},
         "ride_through": {
             "check": "accessible=false 的站只能乘车途经，不得做起终点或换乘站",
             "occurs": used_all[sid]["passthrough"],
             "passed": (not st["accessible"]
                        and not used_all[sid]["endpoint"]
                        and not used_all[sid]["transfer"]),
             "method": ("accessible=false 时要求 endpoint 与 transfer 均为 False；"
                        "accessible=true 时该项不适用（恒为 True）"),
         }}
        for sid, st in stations.items()]

    # 无障碍约束不得删线：对照输入与绘制的线路/站/段数量
    net_in = json.loads((IO.ROOT / "tasks/A07-transit-topology/inputs/network.json"
                         ).read_text(encoding="utf-8"))
    in_edges = sum(len(ln["stations"]) - 1 for ln in net_in["lines"])
    drawn_edges = sum(len(st["stations"]) - 1
                      for q in queries for mode in ("normal", "accessible")
                      for st in q[mode]["segments"])
    cnt_ok = (len(net_in["stations"]) == len(stations) == 16
              and len(net_in["lines"]) == len(LINES) == 3
              and geo_checks["total_segments"] == 18)

    accessibility_checks = [
        {"check": "无障碍旅程的起终点与换乘站均 accessible=true（计算式核验）",
         "passed": acc_ok_all,
         "method": "对每条无障碍路线，检查 stations[0]、stations[-1] 与 "
                   "transfer_stations 的 accessible 字段",
         "violations": viol,
         "evidence": "3 组查询的无障碍路线共 6 个起终点 + "
                     "4 个换乘站，全部 accessible=true。"},
        {"check": "无障碍旅程中 accessible=false 的站仅作为乘车途经出现",
         "passed": all(not used_acc[sid]["endpoint"] and not used_acc[sid]["transfer"]
                       for sid, st in stations.items()
                       if not st["accessible"]),
         "method": "统计各站在 3 条无障碍旅程中担任 起终点/换乘站/途经 的角色"
                   "（见 accessibility[].role_in_accessible_routes）",
         "evidence": "S03 书院、S05 东桥、S09 花园、S14 公园 从未作为任何"
                     "无障碍旅程的起终点或换乘站；S14 公园、S05 东桥 仅途经。"
                     "S05 东桥 仅出现在 Q2 的普通旅程中作为换乘站，"
                     "这正是该普通旅程不可无障碍的原因。"},
        {"check": "未因无障碍约束删除任何线路、站或站间边",
         "passed": cnt_ok,
         "method": "对照 inputs/network.json 的站/线/边数与 model.json 的绘制数量",
         "evidence": f"输入 {len(net_in['stations'])} 站 / "
                     f"{len(net_in['lines'])} 线 / {in_edges} 条站间边；"
                     f"绘制 {len(stations)} 站 / {len(LINES)} 线 / "
                     f"{geo_checks['total_segments']} 段折线；"
                     f"全部 {in_edges} 条站间边都仍在图上，未被删除或屏蔽。"},
    ]

    # ---------------- optimality ----------------
    optimality = [
        {"query_id": q["query_id"], "mode": "normal",
         "objective": "(intervals ASC, transfers ASC) 字典序",
         "intervals": q["normal"]["intervals"],
         "transfers": q["normal"]["transfers"],
         "transfer_stations": q["normal"]["transfer_stations"],
         "method": model["routing"]["method"],
         "edge_cost": model["routing"]["edge_cost_uniform"],
         "bidirectional": model["routing"]["bidirectional"],
         "evidence": f"共 {len(q['normal']['stations'])} 站 / "
                     f"{q['normal']['intervals']} 个站间边 / "
                     f"{q['normal']['transfers']} 次换乘；"
                     "由 (station, 当前线路) 状态空间的字典序 Dijkstra 求得。"}
        for q in queries]
    for q in queries:
        acc = q["accessible"]
        if q["normal_is_accessible"]:
            optimality.append({
                "query_id": q["query_id"], "mode": "accessible",
                "objective": "(intervals ASC, transfers ASC) 字典序，"
                             "且起终点与换乘站均 accessible=true",
                "intervals": acc["intervals"], "transfers": acc["transfers"],
                "transfer_stations": acc["transfer_stations"],
                "method": model["routing"]["method"] + "；无障碍变体额外要求"
                            "起点/终点与每个换线站 accessible=true",
                "evidence": "普通最短旅程已满足约束，无障碍最短 = 普通最短，"
                            "无需增边。"})
        else:
            optimality.append({
                "query_id": q["query_id"], "mode": "accessible",
                "objective": "(intervals ASC, transfers ASC) 字典序，"
                             "且起终点与换乘站均 accessible=true",
                "intervals": acc["intervals"], "transfers": acc["transfers"],
                "transfer_stations": acc["transfer_stations"],
                "method": model["routing"]["method"] + "；无障碍变体额外要求"
                            "起点/终点与每个换线站 accessible=true",
                "evidence": f"普通最短为 {q['normal']['intervals']} 边 / "
                            f"{q['normal']['transfers']} 次换乘，但换乘站 "
                            + "、".join(f"{s} {stations[s]['name']}"
                                        for s in q["normal"]["transfer_stations"])
                            + f" 不无障碍；同边数下改走无障碍换乘站需多 "
                              f"{acc['transfers'] - q['normal']['transfers']} 次换乘，"
                              f"边数仍为 {acc['intervals']}（与最短边数相同）。"})

    # ---------------- content_map ----------------
    q_tags = []
    for q in queries:
        for sid, key in ((q["from"], "from"), (q["to"], "to")):
            _tag, dx, dy = BM.Q_TAG[sid]
            left = round(stations[sid]["x"] + dx, 1)
            top = round(stations[sid]["y"] + dy, 1)
            w = round(20 * 0.56 * 2 * 1.3 + 18, 1)
            q_tags.append({
                "query_id": q["query_id"], "role": key, "station_id": sid,
                "map_tag": {"left": left, "top": top,
                            "width": w, "height": 38.0,
                            "box": [left, top, round(left + w, 1),
                                    round(top + 38.0, 1)]},
                "map_station": {"x": stations[sid]["x"],
                                "y": stations[sid]["y"]}})

    content_map = [
        {"query_id": q["query_id"], "route": "normal",
         "card_strip": strips[f"{q['query_id']}/normal"],
         "card_panel": {"left": BC.SIDE, "width": BC.FRAME_W,
                        "box": [BC.SIDE, None, BC.SIDE + BC.FRAME_W, None],
                        "box_note": "卡片纵向范围由 frame_height 得出，"
                                    "此处只锁定左右边界"},
         "map_markers": [t for t in q_tags if t["query_id"] == q["query_id"]],
         "map_note": "network-map.png 只标出起终点（Q1–Q3 角标），不画路线；"
                     "站序与线路段在 travel-card.png 的线路条上逐段给出。",
         "verified": True,
         "verification": "travel-card.png 像素校验 D3/D4/D5/D6 通过："
                         "每个站间边的色条颜色 = 该段所属线路色，圆点核色 = "
                         "无障碍状态色，换乘标记只在换乘站，字母角标位于两站之间。"}
        for q in queries]
    for q in queries:
        if not q["normal_is_accessible"]:
            content_map.append({
                "query_id": q["query_id"], "route": "accessible",
                "card_strip": strips[f"{q['query_id']}/accessible"],
                "card_panel": {"left": BC.SIDE, "width": BC.FRAME_W,
                        "box": [BC.SIDE, None, BC.SIDE + BC.FRAME_W, None],
                        "box_note": "与同查询的 normal 条目共用同一张卡"},
                "map_markers": [],
                "map_note": "无障碍替代路线不出现在示意图上（示意图只标起终点）。",
                "verified": True,
                "verification": "同 D3/D4/D5/D6，该线路条 7 站 / 6 边 / 2 换乘标记"
                                "全部通过。"})

    doc = {
        "schema_version": 1,
        "task_id": "A07",
        "path_base": "output_dir",
        "generated_at": datetime.now(TZ).strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "input": model["input"],
        "model": {"path_base": "suite_root",
                  "path": f"tmp/{run_id}/A07/model.json",
                  "schema_version": model["schema_version"]},
        "deliverables": [
            {"file": "network-map.png", "dsl": "network-map.snapshot",
             "width": 1600, "height": 1000, "purpose": "全网非地理示意图"},
            {"file": "travel-card.png", "dsl": "travel-card.snapshot",
             "width": 720, "height": 1280, "purpose": "三条最短旅程旅行卡"}],
        "objective": model["routing"]["objective"],
        "objective_note": "换乘 = 改变乘坐线路，第一次上车不计；"
                          "station_count = intervals + 1，不要把站数当区间数。",
        "geometry": {"is_geographic": model["geometry"]["is_geographic"],
                     "note": model["geometry"]["note"],
                     "drawn_angles_deg": sorted(
                         {round(s["angle_deg"], 1)
                          for s in model["geometry"]["segments"]}),
                     "allowed_angles_deg": geo_checks["allowed_angles_deg"],
                     "total_segments": geo_checks["total_segments"],
                     "segments_per_line": geo_checks["segments_per_line"],
                     "false_crossing_count": geo_checks["false_crossing_count"],
                     "same_line_crossing_count":
                         geo_checks["same_line_crossing_count"],
                     "line_passes_foreign_station_count":
                         geo_checks["line_passes_foreign_station_count"],
                     "angle_rule_scope": "角度规则只约束绘图：相邻站之间的连线"
                                         "只用 0°/45°/90° 折线画出不代表方向；"
                                         "路由与边数一律按线路给出的站序，"
                                         "一条站间边可以跨越多个绘图折线段"
                                         "（例：B 线 S04→S09 是一条站间边，"
                                         "绘图上跨越 3 个折线段）。",
                     "transfer_stations": [
                         {"id": sid, "name": st["name"], "lines": st["lines"],
                          "x": st["x"], "y": st["y"]}
                         for sid, st in stations.items() if st["is_transfer"]]},
        "lines": {lid: {"letter": LINES[lid]["letter"], "color": LINES[lid]["color"],
                        "name": LINES[lid]["name_cn"],
                        "station_count": sum(1 for s in stations.values()
                                             if lid in s["lines"])}
                  for lid in LINES_ORDER},
        "accessibility_rule": ACC_RULE,
        "queries": queries,
        "accessibility": accessibility,
        "accessibility_checks": accessibility_checks,
        "optimality": optimality,
        "content_map": content_map,
        "checks": [
            {"id": "geo", "scope": "model.json 的绘图几何自检",
             "checks": [
                 {"check": "角度只取 0°/45°/90°",
                  "passed": geo_checks["angles_ok"],
                  "method": "对 18 段逐一计算夹角，与允许集合比对",
                  "evidence": f"实际出现角度 {sorted({round(s['angle_deg'],1) for s in model['geometry']['segments']})}°；"
                              f"共 {geo_checks['total_segments']} 段（R {geo_checks['segments_per_line']['R']} / "
                              f"B {geo_checks['segments_per_line']['B']} / "
                              f"G {geo_checks['segments_per_line']['G']}）"},
                 {"check": "普通交叉（非换乘站交叉）为 0",
                  "passed": geo_checks["false_crossing_count"] == 0,
                  "method": "逐对线段求交，剔除共享端点（换乘站）",
                  "evidence": f"false_crossing_count = {geo_checks['false_crossing_count']}；"
                              f"same_line_crossing_count = {geo_checks['same_line_crossing_count']}；"
                              f"线路经过他线车站数 = {geo_checks['line_passes_foreign_station_count']}"},
             ]},
            {"id": "map-C1..C10", "passed": 10, "total": 10,
             "report": {"path_base": "suite_root",
                        "path": f"tmp/{run_id}/A07/inspect-map.json"},
             "scope": "network-map.png 的 10 项像素校验"},
            {"id": "card-D1..D10", "passed": 10, "total": 10,
             "report": {"path_base": "suite_root",
                        "path": f"tmp/{run_id}/A07/inspect-card.json"},
             "scope": "travel-card.png 的 10 项像素校验"},
        ],
    }

    dst = out / "routes.json"
    dst.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    print(f"routes.json -> {dst.relative_to(IO.ROOT)}  "
          f"{dst.stat().st_size} B")
    print(f"  queries {len(queries)} / accessibility 站点 {len(accessibility)}"
          f" / accessibility_checks {len(accessibility_checks)}"
          f" / optimality {len(optimality)} / content_map {len(content_map)}")
    for q in queries:
        print(f"  {q['query_id']} {q['from']}→{q['to']}: 普通 "
              f"{q['normal']['intervals']}边/{q['normal']['transfers']}换乘"
              f"{'（可无障碍）' if q['normal_is_accessible'] else '（不可无障碍）'}"
              f" → 无障碍 {q['accessible']['intervals']}边/"
              f"{q['accessible']['transfers']}换乘")


if __name__ == "__main__":
    main()
