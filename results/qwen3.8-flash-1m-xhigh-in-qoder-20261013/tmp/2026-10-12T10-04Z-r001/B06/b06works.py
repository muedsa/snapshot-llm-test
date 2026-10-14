"""B06 works 01-05: five everyday information problems, reinvented.

Each artwork answers a question the original artefact cannot: a timetable that asks
"can I still get home", a headway strip that answers "should I wait here", a payslip
that says whose money it is, a lab report ordered by what you can do about it, and a
nutrition label that states whose day the percentage belongs to.

Run: python tmp/<run_id>/B06/b06works.py [01 02 ... | all]
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from bkit import Sheet, MONO, SANS, SERIF, tw, wrap, fit, f  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B06"
D = json.loads((TMP / "data.json").read_text(encoding="utf-8"))

INK = "#17212B"
INK2 = "#4A5866"
INK3 = "#7C8894"
LINE = "#D6D0C2"
PAPER = "#F4F1E8"
WHITE = "#FFFFFF"
GREEN = "#1F6F5C"
AMBER = "#8A6A12"
RED = "#A83224"
BLUE = "#1D5F8C"
GREY = "#A7B0B7"
NAVY = "#0B2F4A"


def save(s, name, min_font):
    s.min_font = min_font
    a = s.audit()
    print(name, json.dumps(a, ensure_ascii=False))
    assert a["overlap_n"] == 0, a["overlaps"]
    assert a["outside_n"] == 0, a["outside"]
    assert a["spill_n"] == 0, a["spill"]
    assert a["truncated_n"] == 0, a["truncated"]
    assert a["below_min_font_n"] == 0, a["below_min_font"]
    (TMP / f"{name}.snapshot").write_text(s.dsl(), encoding="utf-8")


# ------------------------------------------------------------------ 01 末班车
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
    axis, rows = 560, sw["rows"]
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
        s.text("l", f"{r['ride_min']} 分" + (f" · 换 {r['transfers']}"
                                             if r["transfers"] else ""), 348, y + 10, 20,
               "#8FA9BB" if open_ else "#5A6B77", align="right", font=MONO)
        s.text("l", r["latest"], 444, y + 8, 22,
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
        y += 62
    s.text("l", "「换 N」= 需换乘 N 次", 56, y + 4, 20, "#E8C36B")
    s.text("l", "左侧是车程分钟；条长 = 最迟离开时刻与现在的差", 350, y + 4,
           20, "#6E8DA1")
    s.rect(56, h - 116, w - 112, 62, "#132A3A", radius=10)
    s.text("f", "示例数据（自拟），只演示读法；实际末班与换乘以车站公告和运营方查询为准。",
           76, h - 98, 20, "#9FC6DE")
    save(s, "case01-lasttrain", 18)


# ------------------------------------------------------------------ 02 公交间隔带
def w02():
    w, h = 1200, 420
    s = Sheet(w, h, min_font=16, bg=PAPER)
    s.rect(0, 0, w, h, PAPER)
    b = D["bus"]
    cells = b["cells"]
    s.text("h", "现在要不要等这趟公交", 40, 26, 34, INK, bold=True)
    s.text("h", "一格 = 30 分钟；颜色从绿到红，要等的分钟变多", 40, 70, 20, INK3)
    x0, y0, cw, chh = 40, 150, 26, 74
    ramp = {4: "#1F6F5C", 8: "#5C8A63", 10: "#C9A227", 12: "#A83224"}
    for i, c in enumerate(cells):
        x = x0 + i * cw
        s.rect(x, y0, cw - 3, chh, ramp[c["headway"]])
        if c["at"].endswith(":00"):
            s.text("t", c["at"][:2], x + (cw - 3) / 2, y0 + chh + 8, 18, INK2,
                   align="center", font=MONO)
    # phase bands above
    px = {"早间": (0, 3), "早高峰": (3, 7), "平峰": (7, 23), "晚高峰": (23, 27),
          "夜间": (27, 31)}
    for tag, (a, z) in px.items():
        s.text("t", tag, x0 + a * cw, y0 - 34, 20, INK2, bold=True)
        s.line(x0 + a * cw, y0 - 8, x0 + (z - 1) * cw + cw - 3, y0 - 8, LINE, 2.0)
    # legend for the four headway values actually used
    ly = 318
    for i, (v, lab) in enumerate(((4, "4 分钟 · 高峰"), (8, "8 分钟 · 早间"),
                                  (10, "10 分钟 · 平峰"), (12, "12 分钟 · 夜间"))):
        s.rect(40 + i * 176, ly, 26, 18, ramp[v])
        s.text("t", lab, 74 + i * 176, ly + 1, 18, INK2)
    s.text("t", "间隔取自示例时刻表（自拟）；真实线路请以站牌与到站预报为准。", 40,
           ly + 40, 16, INK3)
    # the needle: 20:12 sits between the 20:00 and 20:30 cells
    idx = max(i for i, c in enumerate(cells) if c["at"] <= b["now"])
    frac = (int(b["now"][3:5]) - int(cells[idx]["at"][3:5])) / 30.0
    nx = x0 + (idx + frac) * cw
    s.line(nx, y0 - 44, nx, y0 + chh + 34, NAVY, 3.0)
    s.rect(nx - 46, y0 + chh + 34, 92, 26, NAVY, radius=6)
    s.text("t", "现在 " + b["now"], nx, y0 + chh + 40, 18, WHITE, align="center",
           font=MONO)
    # answer panel
    ax = x0 + 31 * cw + 24
    s.rect(ax, 26, w - ax - 40, 300, WHITE, radius=12, border=f"1 SOLID {LINE}")
    s.panel(ax, 26, w - ax - 40, 300)
    s.text("t", "这一档发车间隔", ax + 20, 44, 20, INK3)
    s.text("t", f"{b['current']['headway']} 分钟", ax + 20, 70, 40, INK, bold=True,
           font=MONO)
    s.text("t", "最坏还要等", ax + 20, 124, 20, INK3)
    s.text("t", f"到 {b['next_worst']} 前", ax + 20, 150, 34, RED, bold=True, font=MONO)
    s.text("t", f"首班 {b['first']} · 末班 {b['last']}", ax + 20, 200, 20, INK2,
           font=MONO)
    s.line(ax + 20, 232, w - 60, 232, LINE, 1.0)
    s.text("t", "错过末班：改乘夜班线", ax + 20, 248, 20, INK2)
    s.text("t", "示例数据（自拟），非真实时刻表", ax + 20, 278, 16, INK3)
    save(s, "case02-headway", 16)


# ------------------------------------------------------------------ 03 工资条
def w03():
    w, h = 794, 1123
    s = Sheet(w, h, min_font=14, bg=WHITE)
    s.rect(0, 0, w, h, WHITE)
    p = D["payslip"]
    s.rect(48, 48, w - 96, 3, INK)
    s.text("h", "应发 12,000，到手 8,700：中间去了哪", 48, 66, 30, INK, bold=True)
    s.text("h", "把每一笔拆成「谁的口袋」与「什么时候能用」", 48, 106, 19, INK2)
    s.text("h", "示例费率，非现行政策", 48, 132, 16, AMBER, font=MONO)
    scale = 400.0 / p["gross"]
    y = 176
    s.text("t", "① 你的应发", 48, y, 20, INK, bold=True)
    s.rect(48, y + 30, p["gross"] * scale, 34, "#22303A", radius=4)
    s.text("t", "12,000.00 元", 48 + p["gross"] * scale - 12, y + 38, 20, WHITE,
           align="right", font=MONO)
    y += 86
    s.text("t", "② 从你工资里扣（合计 " + f"{p['employee_sum']:,.0f}" + " 元）", 48, y,
           20, INK, bold=True)
    y += 30
    for r in p["employee"]:
        s.text("t", r["item"], 48, y + 2, 19, INK)
        s.rect(200, y, max(r["amount"] * scale, 3), 26, BLUE, radius=3)
        s.text("t", f"{r['amount']:,.0f}", 200 + r["amount"] * scale + 10, y + 2, 19,
               INK2, font=MONO)
        s.text("t", f"{r['rate'] * 100:g}% · {r['goes']} · {r['when']}", 470, y + 4,
               16, INK3)
        y += 34
    s.text("t", "个税（示例）", 48, y + 2, 19, INK)
    s.rect(200, y, max(p["tax"] * scale, 3), 26, "#6B7A86", radius=3)
    s.text("t", f"{p['tax']:,.0f}", 200 + p["tax"] * scale + 10, y + 2, 19, INK2,
           font=MONO)
    s.text("t", f"{p['tax_rate_pct']:g}% · 交给税务 · 当期", 470, y + 4, 16, INK3)
    y += 44
    s.rect(48, y, w - 96, 1.2, INK)
    y += 16
    s.text("t", "③ 到手", 48, y + 4, 22, INK, bold=True)
    s.rect(200, y, p["net"] * scale, 30, GREEN, radius=4)
    s.text("t", f"{p['net']:,.0f} 元", 200 + p["net"] * scale - 12, y + 6, 20, WHITE,
           align="right", font=MONO)
    y += 58
    s.text("t", "④ 单位另外出的钱（不进你当期工资，合计 "
                f"{p['employer_sum']:,.0f} 元）", 48, y, 20, INK, bold=True)
    y += 30
    for r in p["employer"]:
        s.text("t", r["item"], 48, y + 2, 17, INK2)
        s.rect(200, y, max(r["amount"] * scale, 3), 22, "#B9C6D0", radius=3)
        s.text("t", f"{r['amount']:,.0f}", 200 + r["amount"] * scale + 10, y + 2, 17,
               INK3, font=MONO)
        y += 30
    y += 10
    s.rect(48, y, w - 96, 108, "#F4F1E8", radius=10)
    s.panel(48, y, w - 96, 108)
    s.text("t", "两个最容易看错的点", 68, y + 14, 19, INK, bold=True)
    s.text("t", "· 公积金两边各 1,440 元，合计 2,880 元都在你个人账户里，租房可提取；",
           68, y + 42, 17, INK2)
    s.text("t", "· 养老与医疗的单位缴款进统筹，不等于你账上少了同样的钱。", 68,
           y + 70, 17, INK2)
    ay = 884
    s.text("t", "⑤ 把上面这些按一年看", 48, ay, 20, INK, bold=True)
    ay += 30
    amax = max(a["year"] for a in p["annual"])
    for a in p["annual"]:
        s.text("t", a["item"], 48, ay + 2, 17, INK2)
        s.rect(260, ay, max(a["year"] / amax * 276, 3), 20, "#22303A", radius=3)
        s.text("t", f"{a['year']:,.0f}", 260 + a["year"] / amax * 276 + 10, ay + 1, 17,
               INK, font=MONO)
        s.text("t", f"每月 {a['month']:,.0f}", 746, ay + 3, 15, INK3, align="right",
               font=MONO)
        ay += 26
    s.text("t", "本页不替代工资条与社保机构口径；黑白打印时以文字标注为准。", 48,
           h - 42, 16, INK3)
    save(s, "case03-payslip", 14)


# ------------------------------------------------------------------ 04 体检二维
def w04():
    w, h = 390, 844
    s = Sheet(w, h, min_font=16, bg="#EFEDE6")
    s.rect(0, 0, w, h, "#EFEDE6")
    c = D["checkup"]
    s.rect(0, 0, w, 104, "#22303A")
    s.text("h", "七个箭头，哪个要紧", 16, 20, 28, WHITE, bold=True)
    s.text("h", "灰带 = 参考区间；标记 = 你的值", 16, 54, 18, "#B9CBD8")
    s.text("h", f"{c['abnormal_n']} 项偏离 · 多数只超出一点点", 16, 78, 17, "#8FB6CE")
    bands = {3: "本周可做", 2: "需复查", 1: "按期随访"}
    y = 112
    for i, r in enumerate(c["rows"], 1):
        lo, hi = r["low"], r["high"]
        v = r["value"]
        width = hi - lo
        d0 = min(lo, v) - 0.3 * width
        d1 = max(hi, v) + 0.3 * width

        def mx(val):
            return 28 + (val - d0) / (d1 - d0) * 232

        s.rect(14, y - 6, w - 28, 50, WHITE, radius=10, border=f"1 SOLID {LINE}")
        s.panel(14, y - 6, w - 28, 50)
        s.text("l", f"{i} {r['item']}", 28, y, 19, INK, bold=True, maxw=170)
        s.text("l", f"{r['value']:g}{r['arrow']}", 262, y, 19, INK2, font=MONO,
               align="right")
        s.text("l", r["unit"] or "-", 272, y + 2, 16, INK3, maxw=62)
        s.rect(mx(lo), y + 26, mx(hi) - mx(lo), 7, "#DCD6C8", radius=3)
        col = RED if r["side"] == "high" else (GREY if r["side"] == "low" else GREEN)
        if r["side"] == "high":
            s.line(mx(hi), y + 29, mx(v), y + 29, RED, 3.0)
        elif r["side"] == "low":
            s.line(mx(v), y + 29, mx(lo), y + 29, GREY, 3.0)
        s.dot(mx(v), y + 29, 6, col, ring=WHITE, ring_w=2)
        s.text("l", bands[r["actionability"]], 272, y + 24, 16,
               RED if r["actionability"] == 3 else INK3)
        y += 56
    s.line(14, y + 2, w - 14, y + 2, LINE, 1.0)
    y += 14
    s.text("l", "这周可以做三件事", 16, y, 20, INK, bold=True)
    y += 30
    for r in c["rows"]:
        if r["actionability"] != 3:
            continue
        s.text("l", f"{r['item']}：{r['this_week']}", 16, y, 16, INK2, maxw=w - 34)
        y += 26
    y = s.para("l", "视力一项的参考区间只有 0.2 宽，倍数显得大，实际差 0.4。",
               16, y + 4, 16, INK3, w - 34)
    s.text("l", "本页不下诊断结论；请携报告咨询医生。", 16, y + 8, 16, AMBER,
           maxw=w - 34)
    save(s, "case04-checkup", 16)


NAME_CN = {"能量 kJ": "能量", "脂肪 g": "脂肪", "碳水化合物 g": "碳水",
           "糖 g": "糖", "钠 mg": "钠"}


# ------------------------------------------------------------------ 05 营养成分
def w05():
    w, h = 680, 900
    s = Sheet(w, h, min_font=16, bg="#FFFDF7")
    s.rect(0, 0, w, h, "#FFFDF7")
    n = D["nutrition"]
    s.rect(0, 0, w, 120, "#1E3A2F")
    s.text("h", "这一包，占掉我一天多少", 32, 26, 34, WHITE, bold=True)
    s.text("h", f"净含量 {n['pack_g']} g · 包装上的 NRV% 只按成人 8400 kJ 折算",
           32, 74, 20, "#A8CDBB")
    y = 148
    s.text("l", "每 100 g", 236, y, 18, INK3, align="right")
    s.text("l", f"一包 {n['pack_g']} g", 348, y, 18, INK3, align="right")
    s.text("l", "占一天", 372, y, 18, INK3)
    y += 26
    s.line(32, y, w - 32, y, LINE, 1.2)
    y += 16
    for r in n["rows"]:
        if r["nutrient"] == "碳水化合物 g":
            continue
        s.text("l", NAME_CN[r["nutrient"]], 32, y + 8, 22, INK, bold=True, maxw=150)
        s.text("l", f"{r['per100']:g}", 260, y + 8, 22, INK2, font=MONO, align="right")
        s.text("l", f"{r['per_pack']:g}", 348, y + 8, 22, INK, font=MONO, bold=True,
               align="right")
        bw = 168
        s.rect(372, y + 4, bw, 18, "#EAE5DA", radius=4)
        s.rect(372, y + 4, min(r["adult_pct"], 100) / 100 * bw, 18, GREEN, radius=4)
        s.text("l", f"成人 {r['adult_pct']:g}%", 550, y + 4, 16, INK2, maxw=98)
        s.rect(372, y + 26, bw, 18, "#EAE5DA", radius=4)
        s.rect(372, y + 26, min(r["kid_pct"], 100) / 100 * bw, 18, AMBER, radius=4)
        s.text("l", f"儿童 {r['kid_pct']:g}%", 550, y + 26, 16, INK2, maxw=98)
        y += 76
    s.line(32, y, w - 32, y, LINE, 1.2)
    y += 16
    s.rect(32, y, w - 64, 150, "#F4F1E8", radius=12)
    s.panel(32, y, w - 64, 150)
    s.text("l", "两条基准差在哪", 52, y + 14, 20, INK, bold=True)
    s.text("l", "成人 8400 kJ / 脂肪 67 g / 糖 50 g / 钠 2000 mg", 52, y + 42, 17,
           INK2, font=MONO)
    s.text("l", "6-10 岁 7100 kJ / 脂肪 57 g / 糖 42 g / 钠 1700 mg", 52, y + 66, 17,
           INK2, font=MONO)
    s.text("l", "同一包，孩子的占比更高；NRV% 不区分这一点。", 52, y + 94, 18, RED)
    py2 = 686
    s.rect(32, py2, w - 64, 150, WHITE, radius=12, border=f"1 SOLID {LINE}")
    s.panel(32, py2, w - 64, 150)
    s.text("l", "吃多少决定占比（只看能量与糖）", 52, py2 + 12, 20, INK, bold=True)
    s.text("l", "份量", 52, py2 + 44, 16, INK3)
    s.text("l", "能量占一天", 190, py2 + 44, 16, INK3)
    s.text("l", "糖（g / 占比）", 420, py2 + 44, 16, INK3)
    yy = py2 + 66
    for p2 in n["portions"]:
        s.text("l", f"{p2['label']} {p2['grams']:g} g", 52, yy, 17, INK, font=MONO)
        s.text("l", f"成人 {p2['kcal_pct']:g}% · 儿童 {p2['kid_pct']:g}%", 190, yy,
               16, INK2, font=MONO)
        s.text("l", f"{p2['sugar_g']:g} g / {p2['sugar_pct']:g}%", 420, yy, 16, INK2,
               font=MONO)
        yy += 26
    s.text("l", "数值为示例编制，用于演示读法；以包装实际标签为准。", 32, h - 40, 16,
           INK3)
    save(s, "case05-nutrition", 16)


WORKS = {"01": w01, "02": w02, "03": w03, "04": w04, "05": w05}

if __name__ == "__main__":
    which = sys.argv[1:] or ["all"]
    for k, fn in WORKS.items():
        if "all" in which or k in which:
            fn()
            print("built", k)
