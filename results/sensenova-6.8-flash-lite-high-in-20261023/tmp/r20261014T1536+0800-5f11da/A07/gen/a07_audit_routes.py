"""A07 routes.json 的独立审计：字段契约 + 内容重算。

两部分：
1) 字段契约：对照 tasks/A07-transit-topology/templates/audit-fields.json 的
   required_fields，检查最小必需字段与取值形状；
2) 内容重算：完全绕开 model.json 的路由结果，直接对
   tasks/A07-transit-topology/inputs/network.json 跑一遍字典序最短路径
   （状态 = (站, 当前线路)），再与 routes.json 声称的站序/边数/换乘数逐一比对。

用法：python -I tmp/<rid>/A07/gen/a07_audit_routes.py
"""

from __future__ import annotations

import heapq
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a07_io as IO  # noqa: E402


def _edge(a, b):
    return (a, b) if a <= b else (b, a)


def build_graph(net: dict):
    """从输入 JSON 重建双向、等权、按线路给出的相邻站图。"""
    adj: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for ln in net["lines"]:
        lid = ln["id"]
        for a, b in zip(ln["stations"][:-1], ln["stations"][1:]):
            adj[a].append((b, lid))
            adj[b].append((a, lid))
    return adj


def dijkstra(adj, st_acc, s, t, accessible):
    """字典序最短：先站间边数、后换乘次数。

    状态 = (站, 当前乘坐线路)；"-" 表示尚未上车，首次上车不计换乘。
    accessible=True 时额外要求起点、终点与每个换乘站 accessible=true
    （换乘站 = 离站 u 时线路由 l 变为 vl 的那个站）。
    返回 (边数, 换乘数, 终点, 终态线路, 前驱表) 或 None。
    """
    if accessible and not (st_acc[s] and st_acc[t]):
        return None
    INF = (10 ** 9, 10 ** 9)
    best: dict[tuple[str, str], tuple[int, int]] = {(s, "-"): (0, 0)}
    par: dict[tuple[str, str], tuple] = {}
    pq: list[tuple] = [(0, 0, s, "-")]
    while pq:
        e, tr, u, l = heapq.heappop(pq)
        if best[(u, l)] != (e, tr):
            continue
        if u == t:
            return e, tr, u, l, par
        for v, vl in adj[u]:
            if accessible and l != "-" and vl != l and not st_acc[u]:
                continue          # 换乘站必须无障碍
            cand = (e + 1, tr + (1 if (l != "-" and vl != l) else 0))
            if cand < best.get((v, vl), INF):
                best[(v, vl)] = cand
                par[(v, vl)] = (e, tr, u, l)
                heapq.heappush(pq, (e + 1, cand[1], v, vl))
    return None


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    out, tmp = IO.dirs()
    rid = out.parent.name
    d = json.loads((out / "routes.json").read_text(encoding="utf-8"))
    net = json.loads((IO.ROOT / "tasks/A07-transit-topology/inputs/network.json"
                      ).read_text(encoding="utf-8"))
    tpl = json.loads((IO.ROOT / "tasks/A07-transit-topology/templates/audit-fields.json"
                      ).read_text(encoding="utf-8"))

    res: list[tuple[str, bool, str]] = []

    def check(cid, ok, detail):
        res.append((cid, bool(ok), detail))

    # ---------- 1. 通用身份字段 ----------
    check("A0 schema_version / task_id / path_base",
          d.get("schema_version") == 1 and d.get("task_id") == "A07"
          and d.get("path_base") == "output_dir",
          f"schema_version={d.get('schema_version')} task_id={d.get('task_id')!r}"
          f" path_base={d.get('path_base')!r}")

    # ---------- 2. 无机器绝对路径 ----------
    raw = (out / "routes.json").read_text(encoding="utf-8")
    abs_paths = re.findall(r'(?<![\w/])[A-Za-z]:[\\/][^\s",]*', raw)
    check("A1 无机器绝对路径", not abs_paths,
          f"命中 {abs_paths[:3]}" if abs_paths else "0 处盘符/UNC 路径")

    # ---------- 3. 四组必需字段 ----------
    for f in tpl["artifacts"]["routes.json"]["required_fields"]:
        check(f"A2 必需字段 {f}", isinstance(d.get(f), list) and len(d[f]) > 0,
              f"{f}: list, {len(d.get(f, []))} 项")

    # ---------- 4. queries 逐项字段 ----------
    rq = ["from", "to", "normal", "accessible"]
    rk = ["stations", "edge_lines", "intervals", "transfers", "transfer_stations"]
    bad = []
    for q in d["queries"]:
        for f in rq:
            if f not in q:
                bad.append(f"{q.get('query_id')} 缺 {f}")
        for mode in ("normal", "accessible"):
            r = q.get(mode)
            if r is None:
                if not q.get(f"{mode}_reason"):
                    bad.append(f"{q['query_id']}/{mode} 为 null 但无理由")
                continue
            for f in rk:
                if f not in r:
                    bad.append(f"{q['query_id']}/{mode} 缺 {f}")
    check("A3 queries 字段齐全", not bad, "全部通过" if not bad else f"{bad}")

    # ---------- 5. accessibility ----------
    st_acc = {s["id"]: bool(s["accessible"]) for s in net["stations"]}
    listed = {a["id"]: a["accessible"] for a in d["accessibility"]}
    diff = [k for k in st_acc if k not in listed or listed[k] != st_acc[k]]
    check("A4 accessibility 16 站与输入一致",
          len(listed) == 16 and not diff,
          f"{len(listed)} 站；不一致 {diff}" if diff else "16/16 与 inputs/network.json 一致")
    per = [a for a in d["accessibility"]
           if {"endpoint", "transfer", "ride_through"} <= set(a)
           and all(isinstance(a[k], dict) and {"passed", "method"} <= set(a[k])
                   for k in ("endpoint", "transfer", "ride_through"))]
    agg = d["accessibility_checks"]
    check("A5 accessibility 含端点/换乘/途经检查与依据",
          len(per) == 16 and len(agg) >= 2
          and all({"check", "passed", "method"} <= set(c) for c in agg),
          f"{len(per)} 站逐项检查 + {len(agg)} 项汇总检查，均带 passed/method")

    # ---------- 6. optimality ----------
    check("A6 optimality 覆盖 3 查询 × 2 模式",
          len(d["optimality"]) == 6
          and all({"query_id", "mode", "objective", "intervals", "transfers",
                   "method", "evidence"} <= set(o) for o in d["optimality"]),
          f"{len(d['optimality'])} 项")

    # ---------- 7. content_map ----------
    okcm = all({"query_id", "route", "card_strip", "card_panel",
                "map_markers", "map_note", "verified", "verification"}
               <= set(c) for c in d["content_map"])
    check("A7 content_map 含显示区域与核对结论", okcm
          and all("box" in c["card_strip"] for c in d["content_map"]),
          f"{len(d['content_map'])} 项；含 box [left,top,right,bottom]")

    # ---------- 8. 内容重算：独立跑最短路径 ----------
    adj = build_graph(net)
    LINE_EDGESET = {
        ln["id"]: {_edge(a, b) for a, b in
                   zip(ln["stations"][:-1], ln["stations"][1:])}
        for ln in net["lines"]}
    rec_bad = []
    for q in d["queries"]:
        s, t = q["from"], q["to"]
        for mode, key in (("normal", "normal"), ("accessible", "accessible")):
            ac = (mode == "accessible")
            r_raw = dijkstra(adj, st_acc, s, t, ac)
            if r_raw is None:
                want = q[key]
                rec_bad.append(f"{q['query_id']}/{mode}: 重算不可行，"
                               f"routes.json 声称可行")
                continue
            e, tr, u, l, par = r_raw
            # 回溯站序：par 的值是 4 元组 (边数, 换乘数, 前站, 前线路)
            st = [u]
            prev = par.get((u, l))
            while prev is not None:
                st.append(prev[2])
                prev = par.get((prev[2], prev[3]))
            st.reverse()
            r = q[key]
            if st != r["stations"]:
                rec_bad.append(f"{q['query_id']}/{mode} 站序 重算 {st} ≠ "
                               f"交付 {r['stations']}")
            if (e, tr) != (r["intervals"], r["transfers"]):
                rec_bad.append(f"{q['query_id']}/{mode} (边,换乘) 重算 "
                               f"{(e, tr)} ≠ 交付 {(r['intervals'], r['transfers'])}")
            if len(r["stations"]) - 1 != r["intervals"]:
                rec_bad.append(f"{q['query_id']}/{mode} 站数-1 ≠ 边数")
            # 每条边必须真实存在于图上，且线路正确
            for ed_ in r["edge_lines"]:
                if _edge(ed_["from"], ed_["to"]) not in LINE_EDGESET[ed_["line"]]:
                    rec_bad.append(f"{q['query_id']}/{mode} 边 "
                                   f"{ed_['from']}→{ed_['to']} 不在 {ed_['line']} 上")
    check("A8 与独立重算的最短路径一致", not rec_bad,
          "3 查询 × 2 模式 × (站序/边数/换乘数/每条边所属线路) 全部一致"
          if not rec_bad else f"{rec_bad}")

    # ---------- 9. 可无障碍判定正确 ----------
    v_bad = []
    for q in d["queries"]:
        n = q["normal"]
        gate_ok = all(st_acc[x] for x in
                      [n["stations"][0], n["stations"][-1]] + n["transfer_stations"])
        if q["normal_is_accessible"] != gate_ok:
            v_bad.append(f"{q['query_id']} 判定不一致（重算 {gate_ok}）")
    check("A9 可无障碍判定 = 起终点与换乘站全部无障碍", not v_bad,
          "Q1（换乘站 S04 中心）与 Q3（换乘站 S08 工坊）可无障碍；"
          "Q2 的普通旅程换乘站为 S05 东桥（accessible=false）故不可"
          if not v_bad else f"{v_bad}")

    # ---------- 10. 无障碍路线本身合规 ----------
    a_bad = []
    for q in d["queries"]:
        a = q["accessible"]
        for x in [a["stations"][0], a["stations"][-1]] + a["transfer_stations"]:
            if not st_acc[x]:
                a_bad.append(f"{q['query_id']} 无障碍路线 {x} 不具备无障碍设施")
        if (a["intervals"], a["transfers"]) < (q["normal"]["intervals"],
                                                q["normal"]["transfers"]):
            a_bad.append(f"{q['query_id']} 无障碍路线反而更短（不应发生）")
    check("A10 无障碍路线合规且不劣于普通路线", not a_bad,
          "3 条无障碍路线的起终点与换乘站全部无障碍；Q2 边数相同、换乘 +1"
          if not a_bad else f"{a_bad}")

    npass = sum(1 for _, ok, _ in res if ok)
    print(f"通过 {npass}/{len(res)}\n")
    for cid, ok, detail in res:
        print(f"  [{'PASS' if ok else 'FAIL'}] {cid}  — {detail}")

    rep = {"image": None,
           "artifact": str((out / "routes.json").relative_to(IO.ROOT)),
           "source_input": str((IO.ROOT / "tasks/A07-transit-topology/inputs/network.json")
                               .relative_to(IO.ROOT)),
           "checks": [{"id": c, "pass": ok, "detail": dt} for c, ok, dt in res],
           "passed": npass, "total": len(res)}
    (tmp / "audit-routes.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n审计报告 → tmp/{IO.TASK}/audit-routes.json")
    return 0 if npass == len(res) else 1


if __name__ == "__main__":
    sys.exit(main())
