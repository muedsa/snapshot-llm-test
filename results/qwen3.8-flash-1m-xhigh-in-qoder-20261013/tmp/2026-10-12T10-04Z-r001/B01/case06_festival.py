"""B01 case-06 - 叠光声浪音乐节 · 三舞台排片与观演动线 (1600x1200, night neon).

Scenario: one festival-goer holds a 4-act wishlist and wants to know what is actually
watchable. Twelve acts share one time axis across three stages; every claim in the
picture (red collision border, amber transition shortfall, green ok, the two recommended
routes, the "at most 4 shows" bound) comes out of the same interval computation, so the
artwork cannot contradict its own arithmetic.

Run:  python tmp/<run_id>/B01/case06_festival.py
"""
from __future__ import annotations

import itertools
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from bkit import MONO, SANS, Sheet, f, tw  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B01"
W, H = 1600, 1200
BG = "#0B0F1E"
INK, INK2, INK3 = "#F2F5FF", "#A9B3D6", "#7C87B2"
RED, GREEN, AMBER, BLUE = "#F2545B", "#3DD68C", "#FFB44D", "#4FA3FF"
IDLE = "#3A4670"
GENRE = {"电子": BLUE, "摇滚": RED, "民谣": GREEN, "嘻哈": "#C77FF2",
         "爵士": "#F2C744", "世界": "#FF9A4D"}
STAGES = ["主舞台 A", "侧舞台 B", "露台 C"]
LETTER = {"主舞台 A": "A", "侧舞台 B": "B", "露台 C": "C"}
WALK = {("A", "B"): 8, ("A", "C"): 12, ("B", "C"): 5,
        ("B", "A"): 8, ("C", "A"): 12, ("C", "B"): 5}

# stage, act, start (minutes from 14:00), length, genre, headline
ROWS = [("主舞台 A", "潮汐乐队", 0, 60, "摇滚", False),
        ("主舞台 A", "南屿", 80, 55, "电子", False),
        ("主舞台 A", "回声工厂", 150, 70, "摇滚", True),
        ("主舞台 A", "林间电台", 240, 60, "民谣", False),
        ("侧舞台 B", "白鲸计划", 20, 50, "电子", False),
        ("侧舞台 B", "邱一和", 90, 55, "嘻哈", False),
        ("侧舞台 B", "夜航班", 160, 65, "电子", True),
        ("侧舞台 B", "海棠三弄", 250, 55, "世界", False),
        ("露台 C", "陈默三重奏", 30, 50, "爵士", False),
        ("露台 C", "小满", 100, 50, "民谣", False),
        ("露台 C", "沙丘信使", 170, 60, "世界", True),
        ("露台 C", "收尾 set", 245, 70, "电子", False)]
ACTS = [{"stage": r[0], "act": r[1], "start": r[2], "dur": r[3], "genre": r[4],
         "head": r[5], "end": r[2] + r[3]} for r in ROWS]
BY = {a["act"]: a for a in ACTS}
PICKS = ["潮汐乐队", "回声工厂", "夜航班", "小满", "沙丘信使"]
GROUPS = [["潮汐乐队", "白鲸计划", "陈默三重奏"],
          ["南屿", "邱一和", "小满"],
          ["回声工厂", "夜航班", "沙丘信使"],
          ["林间电台", "收尾 set", "海棠三弄"]]
T0, T1 = 0, 320
PX0, PX1 = 220, 1520
PY0, LANE_H, LANE_RECT_H = 236, 176, 148
BOTTOM = PY0 + 2 * LANE_H + LANE_RECT_H
CARD_H, CARD_DY = 132, 8


def X(m):
    return PX0 + (m - T0) / (T1 - T0) * (PX1 - PX0)


def hh(mins):
    t = 14 * 60 + mins
    return f"{t // 60:02d}:{t % 60:02d}"


def walk(a, b):
    la, lb = LETTER[a["stage"]], LETTER[b["stage"]]
    return 0 if la == lb else WALK[(la, lb)]


def overlap(a, b):
    return min(a["end"], b["end"]) - max(a["start"], b["start"])


def fits(a, b):
    """a then b: no time overlap and enough walking time in between."""
    return b["start"] >= a["end"] + walk(a, b)


def greedy(pool):
    route, prev = [], None
    for a in sorted(pool, key=lambda a: (a["end"], a["start"])):   # interval scheduling
        if prev is None or fits(prev, a):
            route.append(a)
            prev = a
    return route


def analyse():
    picks = [BY[n] for n in PICKS]
    conf = sorted([(a["act"], b["act"], max(a["start"], b["start"]),
                    min(a["end"], b["end"]), overlap(a, b))
                   for i, a in enumerate(picks) for b in picks[i + 1:]
                   if overlap(a, b) > 0], key=lambda r: -r[4])
    bad = {x for r in conf for x in r[:2]}
    short = []
    for i, a in enumerate(picks):
        for b in picks[i + 1:]:
            first, nxt = (a, b) if a["start"] <= b["start"] else (b, a)
            if overlap(first, nxt) <= 0 and not fits(first, nxt):
                short.append((first["act"], nxt["act"], walk(first, nxt),
                              nxt["start"] - first["end"], first["end"], nxt["start"]))
    amber = {n for s in short for n in s[:2] if n not in bad}
    assert len(conf) == 3 and len(short) == 1, (conf, short)

    def status(name):
        if name not in PICKS:
            return None
        if name in bad:
            return "冲突"
        if name in amber:
            return "转场不足"
        return "已选"

    best = None                      # exhaustive: which 4-show plan spans the most stages
    for combo in itertools.combinations(ACTS, len(GROUPS)):
        seq = sorted(combo, key=lambda a: a["start"])
        if all(fits(x, y) for x, y in zip(seq, seq[1:])):
            score = len({LETTER[a["stage"]] for a in seq})
            if best is None or score > best[0]:
                best = (score, seq)
    assert best and best[0] == 3, best
    routes = [("方案一 · 全场贪心（区间调度）", greedy(ACTS)),
              (f"方案二 · 跨 {best[0]} 个舞台", best[1])]
    for g in GROUPS:                       # each group is a pairwise-overlapping clique
        for i, n in enumerate(g):
            for m in g[i + 1:]:
                assert overlap(BY[n], BY[m]) > 0, (n, m)
    assert sorted(sum(GROUPS, [])) == sorted(a["act"] for a in ACTS)
    bound = len(GROUPS)
    for _, r in routes:
        assert len(r) == bound, [a["act"] for a in r]
        for a, b in zip(r, r[1:]):
            assert fits(a, b), (a["act"], b["act"])
    return {"conf": conf, "short": short, "status": status, "routes": routes,
            "bound": bound, "picks": picks, "n_bad": len(bad)}


def build():
    A = analyse()
    conf, short, status = A["conf"], A["short"], A["status"]
    s = Sheet(W, H, min_font=20, bg=BG)
    s.text("brand", "叠光声浪音乐节 · SONAWAVE 2026", 56, 40, 22, BLUE, bold=True,
           font=MONO)
    s.text("title", "三舞台排片与个人观演动线", 56, 72, 40, INK, bold=True)
    last = max(a["end"] for a in ACTS)
    s.text("sub", f"10 月 24 日 · {hh(0)}-{hh(last)} · {len(ACTS)} 组演出 · 3 个舞台 · "
                  "示例节目单（艺名自拟，非真实演出）", 56, 140, 22, INK3)
    warn = (f"你的清单 {len(PICKS)} 组：{len(conf)} 对时间冲突 · "
            f"{len(short)} 处转场不足 · 完整看完上限 {A['bound']} 场")
    s.text("warn", warn, 56, 178, 22, RED if conf or short else GREEN, bold=True)

    for m in range(T0, T1 + 1, 40):
        s.line(X(m), PY0, X(m), BOTTOM, "#18203F", 1)
        s.text("tk", hh(m), X(m), BOTTOM + 8, 20, INK3, align="center", font=MONO)
    for i, st in enumerate(STAGES):
        y = PY0 + i * LANE_H
        s.rect(56, y, 150, LANE_RECT_H, "#131A33", radius=12)
        s.text("st", st, 131, y + 34, 24, INK, bold=True, align="center")
        s.text("st2", f"{sum(1 for a in ACTS if a['stage'] == st)} 组演出", 131, y + 68,
               20, INK3, align="center")
        s.text("st3", f"压轴 {sum(1 for a in ACTS if a['stage'] == st and a['head'])} 组",
               131, y + 98, 20, INK3, align="center")
        s.rect(X(T0) - 8, y, X(T1) - X(T0) + 16, LANE_RECT_H, "#0F1530", radius=10)
    for a in ACTS:
        i = STAGES.index(a["stage"])
        y = PY0 + i * LANE_H + CARD_DY
        x, w = X(a["start"]), X(a["end"]) - X(a["start"])
        col = GENRE[a["genre"]]
        st = status(a["act"])
        border = (RED if st == "冲突" else AMBER if st == "转场不足"
                  else GREEN if st else IDLE)
        s.rect(x, y, w, CARD_H, "#171F3E", radius=10)
        s.rect(x + 5, y + 6, 4, CARD_H - 12, col, radius=2)
        s.rect(x, y, w, CARD_H, "#00000000",
               border=f"{3 if st else 2} SOLID {border}", radius=10)
        s.text("an", a["act"], x + 18, y + 12, 24, INK, bold=True)
        s.text("ag", f"{hh(a['start'])}-{hh(a['end'])}", x + 18, y + 48, 20, INK2,
               font=MONO)
        if a["head"]:
            s.rect(x + w - 70, y + 12, 58, 28, col, radius=14)
            s.text("hd", "压轴", x + w - 41, y + 15, 20, "#0B0F1E", bold=True,
                   align="center")
        s.text("dur", f"{a['dur']} 分", x + w - 16, y + 48, 20, INK3, align="right",
               font=MONO)
        s.dot(x + 24, y + 88, 6, col)
        s.text("gn", a["genre"], x + 36, y + 78, 20, INK2)
        if st:
            s.text("pk", st, x + w - 16, y + 78, 20, border, align="right", bold=True)

    # legend band
    ly = BOTTOM + 60
    s.text("lh", "风格色标", 56, ly, 22, INK2, bold=True)
    x = 152
    for g, col in GENRE.items():
        s.rect(x, ly + 3, 18, 18, col, radius=4)
        s.text("lg", g, x + 26, ly, 22, INK2)
        x += 26 + tw(g, 22) + 24
    s.text("lh2", "绿框＝清单内可行 · 红框＝清单内冲突 · 橙框＝转场不足 · 灰框＝未选",
           1544, ly, 20, INK3, align="right")

    # ---- left panel: wishlist audit
    py = 830
    s.rect(56, py, 720, 310, "#131A33", radius=14)
    s.text("ph1", f"清单核对：{len(PICKS)} 组里有 {A['n_bad']} 组时间撞车",
           80, py + 20, 24, INK, bold=True)
    cols = [80, 330, 500, 600]
    for c, lab in zip(cols, ["核对项", "时间区间", "分钟", "判定"]):
        s.text("th", lab, c, py + 62, 20, INK3, bold=True)
    s.line(80, py + 90, 752, py + 90, "#243055", 1)
    rows = [(f"{a} × {b}", f"{hh(m)}-{hh(m2)}", str(mins), "冲突")
            for a, b, m, m2, mins in conf]
    for fa, na, need, slack, fend, nstart in short:
        rows.append((f"{fa} → {na}", f"{hh(fend)}→{hh(nstart)}", f"需 {need}", "转场不足"))
    yy = py + 96
    for lab, window, mins, verdict in rows:
        s.text("c0", lab, cols[0], yy, 20, INK)
        s.text("c1", window, cols[1], yy, 20, INK2, font=MONO)
        s.text("c2", mins, cols[2], yy, 20, INK2, font=MONO)
        s.text("c3", verdict, cols[3], yy, 20, RED if verdict == "冲突" else AMBER)
        yy += 30
    s.line(80, yy + 2, 752, yy + 2, "#243055", 1)
    fa, na, need, slack, fend, nstart = short[0]
    la, lb = LETTER[BY[fa]["stage"]], LETTER[BY[na]["stage"]]
    notes = [f"分钟列＝两组重叠时长；末行的「需 {need}」＝{la}→{lb} 转场步行。",
             "口径：重叠＝max(开始)＜min(结束)，可行＝上场结束＋步行≤下场开始"]
    ny = yy + 12
    for line in notes:
        assert tw(line, 20) <= 672, (line, tw(line, 20))
        s.text("note1", line, 80, ny, 20, INK3)
        ny += 26
    assert ny - 26 + 21.2 <= py + 296, ny

    # ---- right panel: recommended routes
    s.rect(796, py, 748, 310, "#131A33", radius=14)
    s.text("ph2", f"推荐动线：上限 {A['bound']} 场，两条方案都取到上限",
           820, py + 20, 24, INK, bold=True)
    ry = py + 50
    for tag, route in A["routes"]:
        sw = sum(walk(route[i], route[i + 1]) for i in range(len(route) - 1))
        letters = "/".join(sorted({LETTER[a["stage"]] for a in route}))
        s.text("rl", f"{tag} · 舞台 {letters} · {len(route)} 场 · 步行合计 {sw} 分钟",
               820, ry, 20, BLUE, bold=True)
        ry += 30
        x = 820
        for i, a in enumerate(route):
            window = f"{hh(a['start'])}-{hh(a['end'])}"
            inner = max(tw(a["act"], 22), tw(window, 20, True))
            w = 26 + inner + 16
            s.rect(x, ry, w, 56, "#1B2446", radius=10)
            s.rect(x + 5, ry + 6, 4, 44, GENRE[a["genre"]], radius=2)
            s.text("ri", str(i + 1), x + 12, ry + 7, 20, INK3, font=MONO)
            s.text("rn", a["act"], x + 26, ry + 7, 22, INK)
            s.text("rt", window, x + 26, ry + 31, 20, INK2, font=MONO)
            if i < len(route) - 1:
                s.arrow(x + w + 2, ry + 28, x + w + 16, ry + 28, "#4A5680", 2, 6)
            x += w + 20
        assert x - 20 <= 1520, x
        ry += 68
    s.line(820, ry - 12, 1520, ry - 12, "#243055", 1)
    notes2 = [f"上界证明：{len(ACTS)} 组演出分成 {A['bound']} 个时段组，组内任意两组时间重叠；",
              f"同一时刻只能守一台 → 最多完整看完 {A['bound']} 场；两条方案都取到 {A['bound']} 场。"]
    for line in notes2:
        assert tw(line, 20) <= 700, (line, tw(line, 20))
        s.text("note2", line, 820, ry, 20, INK3)
        ry += 26
    assert ry - 26 + 21.2 <= py + 296, ry
    return s


if __name__ == "__main__":
    s = build()
    (TMP / "case06.snapshot").write_text(s.dsl(), encoding="utf-8")
    A = analyse()
    (TMP / "case06-data.json").write_text(json.dumps({
        "acts": [{**a, "start_h": hh(a["start"]), "end_h": hh(a["end"])} for a in ACTS],
        "picks": PICKS, "conflicts": A["conf"], "transition_shortfalls": A["short"],
        "routes": [[t, [a["act"] for a in r]] for t, r in A["routes"]],
        "upper_bound": A["bound"], "upper_bound_groups": GROUPS,
        "walk_minutes": {f"{k[0]}->{k[1]}": v for k, v in WALK.items()}},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(s.audit(margin=40), ensure_ascii=False))
