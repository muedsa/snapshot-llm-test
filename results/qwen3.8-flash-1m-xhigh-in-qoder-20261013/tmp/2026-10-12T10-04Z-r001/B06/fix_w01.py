"""Fix work 01's model: a poster must answer "by when must I leave this station".

The first cut listed each station's own last-train passing time and called anything
earlier than "now" closed. That is physically impossible in one direction (a train
cannot pass later stations at earlier times) and it also ignores transfers, which is
what actually decides whether a destination is still reachable. The poster now carries,
per destination, the latest departure from the station you are standing in.
"""
import ast
import os
import re
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "B06"

fp = TMP / "b06data.py"
t = fp.read_text(encoding="utf-8")
start = t.index('NOW = "23:41"')
end = t.index("# ------------------------------------------------------------------ 02 公交间隔")
new = '''NOW = "23:41"
ORIGIN = "南京西路"
# (目的地, 最迟必须离开本站的时刻, 换乘次数, 车程分钟)
DESTS = [
    ("静安寺", "23:46", 0, 4), ("人民广场", "23:45", 0, 6),
    ("上海南站", "23:47", 1, 18), ("徐家汇", "23:49", 1, 15),
    ("莘庄", "23:51", 1, 26), ("中山公园", "23:52", 0, 9),
    ("虹桥火车站", "23:58", 0, 21), ("龙阳路", "23:44", 1, 24),
    ("真如", "23:41", 1, 12), ("顾村公园", "23:38", 2, 34),
    ("世纪大道", "23:40", 1, 17), ("浦东机场", "23:20", 2, 52),
]


def _mins(t):
    h, m = (int(x) for x in t.split(":"))
    return h * 60 + m + (24 * 60 if h < 6 else 0)


def subway():
    now = _mins(NOW)
    rows = []
    for name, latest, xfer, ride in DESTS:
        left = _mins(latest) - now
        rows.append({"station": name, "latest": latest, "transfers": xfer,
                     "ride_min": ride, "minutes_left": left,
                     "reachable": left >= 0})
    rows.sort(key=lambda r: (-r["minutes_left"], r["ride_min"]))
    reach = [r for r in rows if r["reachable"]]
    far = max(reach, key=lambda r: r["ride_min"])
    assert len(rows) == 12
    assert len(reach) == 9 and len(rows) - len(reach) == 3, (len(reach), len(rows))
    assert far["station"] == "莘庄", far          # 车程最长且仍赶得上
    assert far["ride_min"] == 26 and far["latest"] == "23:51"
    assert rows[0]["minutes_left"] == 17 and rows[-1]["minutes_left"] == -21
    # a destination whose last departure is exactly now is still catchable
    assert [r["station"] for r in rows if r["minutes_left"] == 0] == ["真如"]
    assert all(r["minutes_left"] >= 0 for r in reach)
    return {"now": NOW, "origin": ORIGIN, "rows": rows, "reachable_n": len(reach),
            "closed_n": len(rows) - len(reach), "farthest": far["station"],
            "farthest_ride": far["ride_min"], "farthest_latest": far["latest"],
            "tightest": min(reach, key=lambda r: r["minutes_left"])["station"]}


'''
t = t[:start] + new + t[end:]
t = t.replace('''    assert len(reach) == sum(1 for r in rows if r["reachable"]) == 10
    far = max(rows, key=lambda r: r["minutes_left"] if r["reachable"] else -999)
    assert far["station"] == "虹桥火车站", far
    assert [r["station"] for r in rows if not r["reachable"]] == \\
        ["新世界路", "陆家浜路", "西藏南路"]
    assert {r["station"] for r in rows if r["reachable"] and r["transfer"]} == \\
        {"虹桥火车站", "娄山关路", "中山公园", "静安寺", "人民广场"}
    return {"now": NOW, "origin": ORIGIN, "rows": rows,
            "reachable_n": len(reach), "farthest": far["station"],
            "closed_n": len(rows) - len(reach)}''', '')
ast.parse(t)
fp.write_text(t, encoding="utf-8")

# --- artwork 01 rewritten for the new model
fp2 = TMP / "b06works.py"
u = fp2.read_text(encoding="utf-8")
i = u.index("# ------------------------------------------------------------------ 01 末班车")
j = u.index("# ------------------------------------------------------------------ 02 公交间隔")
w01 = '''# ------------------------------------------------------------------ 01 末班车
def w01():
    w, h = 900, 1270
    s = Sheet(w, h, min_font=18, bg="#0E1B26")
    s.rect(0, 0, w, h, "#0E1B26")
    sw = D["subway"]
    s.text("h", "末班车还赶得上吗", 56, 48, 52, WHITE, bold=True)
    s.text("h", f"你在 {sw['origin']}，现在 {sw['now']} · 每根条 = 最迟必须离开本站的时刻",
           56, 118, 24, "#9FC6DE")
    s.rect(56, 162, w - 112, 108, "#132A3A", radius=14)
    s.text("h", "最远还能去", 80, 184, 22, "#9FC6DE")
    s.text("a", sw["farthest"], 80, 214, 40, WHITE, bold=True)
    s.text("h", f"车程 {sw['farthest_ride']} 分钟", w - 80, 268, 22, "#9FC6DE",
           align="right")
    s.text("h", f"最迟 {sw['farthest_latest']} 上车", w - 80, 236, 26, "#7FD4B4",
           align="right", font=MONO, bold=True)
    s.text("h", f"{sw['reachable_n']} 地可去 · {sw['closed_n']} 地已来不及", w - 80, 190,
           22, "#9FC6DE", align="right")
    axis, rows = 470, sw["rows"]
    scale = 92.0 / max(max(r["minutes_left"] for r in rows),
                       -min(r["minutes_left"] for r in rows))
    s.line(axis, 316, axis, 316 + len(rows) * 62 - 26, "#3A5568", 2.0)
    s.text("h", "现在", axis - 14, 292, 22, "#E8C36B", align="right")
    s.text("h", sw["now"], axis + 14, 292, 22, "#E8C36B", font=MONO)
    y = 320
    for r in rows:
        ln = r["minutes_left"] * scale
        open_ = r["reachable"]
        s.text("l", r["station"], 56, y + 6, 26, WHITE if open_ else "#6E8DA1")
        s.text("l", f"{r['ride_min']} 分", 300, y + 10, 20,
               "#8FA9BB" if open_ else "#5A6B77", align="right", font=MONO)
        s.text("l", r["latest"], axis - 18, y + 8, 22,
               "#9FC6DE" if open_ else "#5A6B77", align="right", font=MONO)
        if open_:
            s.rect(axis, y + 8, max(ln, 4), 24, GREEN if ln > 6 else "#B47B1F",
                   radius=4)
            s.text("l", (f"还剩 {r['minutes_left']} 分" if r["minutes_left"]
                         else "刚好赶上"), axis + max(ln, 4) + 12, y + 10, 22,
                   "#7FD4B4" if r["minutes_left"] > 6 else "#E8C36B", font=MONO)
        else:
            s.rect(axis - abs(ln), y + 8, max(abs(ln), 4), 24, "#4B5C68", radius=4)
            s.line(axis - abs(ln), y + 8, axis, y + 32, "#8A4A44", 2.0)
            s.line(axis, y + 8, axis - abs(ln), y + 32, "#8A4A44", 2.0)
            s.text("l", f"差 {abs(r['minutes_left'])} 分", axis + 12, y + 10, 22,
                   "#B87F79", font=MONO)
        for k in range(r["transfers"]):
            s.rect(axis + 6, y + 12 + k * 4, 5, 5, "#E8C36B", radius=2)
        y += 62
    s.text("l", "● 数量 = 换乘次数", 56, y + 4, 20, "#E8C36B")
    s.text("l", "左侧数字是车程分钟；条长与「最迟离开时刻与现在的差」成正比", 210, y + 4,
           20, "#6E8DA1")
    s.rect(56, h - 116, w - 112, 62, "#132A3A", radius=10)
    s.text("f", "示例数据（自拟），只演示读法；实际末班与换乘以车站公告和运营方查询为准。",
           76, h - 98, 20, "#9FC6DE")
    save(s, "case01-lasttrain", 18)


'''
u = u[:i] + w01 + u[j:]
ast.parse(u)
fp2.write_text(u, encoding="utf-8")
print("work 01 rebuilt on latest-departure semantics")
