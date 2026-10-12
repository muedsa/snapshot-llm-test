"""件-01「今天几点吃药」1080×1080 方卡（冰箱贴／药盒侧贴）。

原始口径：药盒与说明书上的"一日三次""饭后服用"。
换算：一日三次＝每 8 小时，而不是跟着三餐；把 8 h 骨架摆进 24 h 盘，
      再看装不装得进清醒窗口（07:00–23:00）。
行动：三行钟点 + 下一次还剩几小时 + 三句今天用得上的判断。

数值来自 research/demo.json（b06data.py 固定种子生成）。
"""
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
for _p in (ROOT / "tmp" / RID / "_suite" / "scripts", ROOT / "tmp" / RID / "B06"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import b06kit as K  # noqa: E402

W, H = 1080, 1080
CX, CY, R = 292, 402, 196
DOSE_COL = [K.CYAN, K.GOLD, K.VIOLET]
DIM_COL = ["#1E4E52", "#5A4321", "#3E3A55"]


def ang(mins):
    return math.radians(-90.0 + 360.0 * mins / 1440.0)


def pt(cx, cy, r, mins):
    a = ang(mins)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def m24(s):
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def build():
    d, tf = K.doc(W, H, ground="dark")
    P = d.P
    c = K.data()["cases"]["case01"]
    drugs = c["drugs"]

    # ---------- 页眉 ----------
    d.rect(0, 0, W, 92, K.BASE)
    d.rect(0, 90, W, 2, P["line"])
    K.tlab(d, tf, "h-t", 40, 16, 620, 38, "今天几点吃药", 32, P["t0"])
    K.tlab(d, tf, "h-s", 40, 56, 640, 24,
           "把「一日三次」翻译成钟点，而不是跟着三餐吃", 15, P["t2"])
    K.chip(d, tf, "h-c1", 700, 22, 168, 40, "每 8 小时一次", P["t0"], P["panel2"],
           border="1 SOLID " + P["border"], size=15)
    K.chip(d, tf, "h-c2", 880, 22, 160, 40, "演示数据", P["t2"], P["card2"],
           border="1 SOLID " + P["border"], size=15)

    # ---------- ① 24 h 盘 ----------
    y1 = K.section(d, tf, "s1", 40, 108, 700, "①", "换算：24 小时盘",
                   "最外浅色带＝清醒窗口 %s–%s" % (c["wake"], c["sleep"]), P["teal"])
    CX, CY = 292, 400
    # 清醒窗口带（最外）
    K.pie_ring(d, CX, CY, 246, 240, -90 + 360 * m24(c["wake"]) / 1440.0,
               -90 + 360 * m24(c["sleep"]) / 1440.0, "#43585F")
    K.clock_ticks(d, CX, CY, 226, 206, every=30, major_every=120,
                  color=P["axis"], major=P["t2"])
    for hh in (0, 6, 12, 18):
        x, y = pt(CX, CY, 186, hh * 60)
        K.mono(d, tf, "clk-%d" % hh, x - 26, y - 12, 52, 22, "%02d" % hh, 15,
               P["t2"], align="CENTER")
    for i, dr in enumerate(drugs):
        r = 156 - i * 24
        K.disc_outline(d, CX, CY, r, 1, DIM_COL[i])
        for t in dr["times"]:
            x, y = pt(CX, CY, r, m24(t))
            d.dot(x, y, 17, DOSE_COL[i])
    # 盘心：只放"现在"，钟点交给右侧三行（点不逐个标字，避免与盘心叠字）
    d.dot(CX, CY, 80, P["card"])
    K.outline_rect(d, CX - 80, CY - 80, 160, 160, P["border"], radius=80, thick=1)
    K.tlab(d, tf, "ctr-1", CX - 70, CY - 44, 140, 24, "现在", 14, P["t2"],
           align="CENTER")
    K.mono(d, tf, "ctr-2", CX - 70, CY - 20, 140, 44, c["now"], 34, P["t0"],
           align="CENTER")
    K.tlab(d, tf, "ctr-3", CX - 70, CY + 26, 140, 24,
           "下一次 %s" % drugs[0]["next"], 14, K.CYAN, align="CENTER")
    K.tlab(d, tf, "pre-0", 40, 652, 500, 22,
           "最内圈那格在清醒窗口之前：%s 定在 %s"
           % (drugs[2]["name"], drugs[2]["times"][0]), 14, P["amber"])

    # ---------- ② 三行结论（右侧） ----------
    rx, rw = 552, 488
    K.section(d, tf, "s2", rx, y1, rw, "②", "三行钟点", "按间隔排，不按饭点排",
              P["gold"])
    yy = y1 + 78
    for i, dr in enumerate(drugs):
        hh = 96
        K.panel(d, rx, yy, rw, hh, P["card"], radius=14,
                border="1 SOLID " + P["border"])
        d.rect(rx, yy, 6, hh, DOSE_COL[i], radius=3)
        K.tlab(d, tf, "r%d-n" % i, rx + 20, yy + 12, 300, 26, dr["name"], 17, P["t0"])
        K.tlab(d, tf, "r%d-r" % i, rx + 20, yy + 40, 300, 22,
               "原口径 %s → 每 %d h" % (dr["raw"], dr["interval_h"]), 13, P["t2"])
        K.tlab(d, tf, "r%d-t" % i, rx + 20, yy + 64, 320, 22, dr["note"], 13, P["t1"])
        K.mono(d, tf, "r%d-v" % i, rx + rw - 190, yy + 14, 170, 30,
               " / ".join(dr["times"]), 14, DOSE_COL[i], align="END")
        K.mono(d, tf, "r%d-w" % i, rx + rw - 170, yy + 50, 150, 26,
               "下次 %s" % dr["next"], 14, P["t1"], align="END")
        K.mono(d, tf, "r%d-g" % i, rx + rw - 170, yy + 72, 150, 22,
               "还有 %s h" % dr["wait_h"], 13, P["t2"], align="END")
        yy += hh + 12
    assert yy <= 660, yy

    # ---------- ③ 今天剩下的事 ----------
    y3 = 682
    K.section(d, tf, "s3", 40, y3, 1000, "③", "今天剩下的事",
              "进度条＝从现在到下一次还要等多久（最长 24 h）", P["grass"])
    yy = y3 + 78
    for i, dr in enumerate(drugs):
        K.tlab(d, tf, "b%d-n" % i, 40, yy, 240, 24, dr["name"], 15, P["t1"])
        K.hbar(d, tf, "b%d" % i, 300, yy + 2, 600, 20, dr["wait_h"] / 24.0,
               DOSE_COL[i], bg=P["grid"])
        K.mono(d, tf, "b%d-v" % i, 916, yy, 124, 24,
               "%s h · %s" % (dr["wait_h"], dr["next"]), 14, P["t0"], align="END")
        yy += 36
    # 间隔是否被拉长：一天里最后一次到次日第一次
    yy += 6
    K.tlab(d, tf, "g-1", 40, yy, 1000, 24,
           "夜里最长间隔：阿莫西林 %s h、布洛芬 %s h、奥美拉唑 %s h（24 h 一次就是隔天同一分钟）"
           % (drugs[0]["overnight_gap_h"], drugs[1]["overnight_gap_h"],
              drugs[2]["overnight_gap_h"]), 14, P["t2"])
    yy += 30

    # ---------- ④ 口径与限制 ----------
    nb = K.note_band(d, tf, "note", 40, yy + 4, 1000, [
        "「一日三次＝每 8 小时」是常见服药间隔口径，不是我把饭点凑出来的；"
        "布洛芬缓释为一日二次＝每 12 小时，缓释剂型不可掰开。",
        "奥美拉唑按「早餐前 1 小时空腹」排在 %s，早于本卡设定的清醒窗口 %s–%s。"
        % (drugs[2]["times"][0], c["wake"], c["sleep"]),
        "所以这天得把闹钟设到 %s；若实际起床更晚，应整体后移而不是漏掉一剂。"
        % drugs[2]["times"][0],
        "本卡不判断该不该吃、吃不吃得下：剂量、疗程、禁忌以处方与说明书为准。"
        "药品名与钟点均为演示内容。",
    ], size=14)
    assert nb <= H - 40, nb

    K.credit(d, tf, "credit", 40, nb + 10, 1000, [
        "数据：tmp/%s/B06/research/demo.json（b06data.py，seed=%s）｜"
        "图形：环形刻度与扇形带用图元逼近，服务无矢量 path。" % (RID, K.data()["seed"]),
    ], size=12)
    info = {"case": "01", "kind": "everyday-info-reinvented",
            "canvas": [W, H], "drugs": [x["name"] for x in drugs],
            "times": [x["times"] for x in drugs], "now": c["now"],
            "waits": [x["wait_h"] for x in drugs],
            "raw_wording": [x["raw"] for x in drugs]}
    return d, tf, info
