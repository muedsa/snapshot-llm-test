"""B02 case-07 - 暴雨天上下学 · 安全课讲义 (1080x1528, A4 打印).

Touchpoint: a single A4 sheet a grade-4 teacher hands out and a parent sticks by the door.
It teaches one decision rule - how deep the water is at your feet - with a scale the child
can point at, six pre-departure checks, three "if... then..." situations and a self-test.
The depth bands are street water depth, deliberately separate from the gauge centimetres
used elsewhere; the sheet says so.

Run:  python tmp/<run_id>/B02/case07_school.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "B02"))
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
import data  # noqa: E402
import tide  # noqa: E402
from bkit import MONO, SANS, tw  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B02"
W, H = 1080, 1528
M = 64
CHECKS = [("看", "门口积水有多深？对照下面的色条。"),
          ("听", "家长或值班志愿者有没有说改路线。"),
          ("穿", "雨鞋和反光条背心，不带雨伞挂饰。"),
          ("带", "哨子一只、纸巾一包、姓名卡一张。"),
          ("走", "靠内侧、远离井盖与围墙，跟着黄线走。"),
          ("到", "到校后向班长报到，回家向家长报到。")]
SCENES = [("水到脚踝，还在涨", "不趟水，退回门廊，打电话给家长或值班电话。", tide.SAND),
          ("路灯灭了 / 电线掉落", "远离 8 米，不捡任何东西，告诉大人并打值班电话。", tide.ALARM),
          ("同学被水围住", "不手拉手去救，找大人、扔漂浮物、记住位置。", tide.CYAN)]
QUIZ = ["水深到小腿，可不可以走过去？",
        "路上看到掉落的电线，要离多远？",
        "到校以后第一件事是什么？"]


def build():
    s = tide.sheet(W, H, min_font=20)
    tide.assert_contrast([(tide.INK, tide.PAPER, "ink"), (tide.INK_2, "#FFFFFF", "card")],
                         4.5)
    tide.lockup(s, M, 44, 56, tide.INK, latin=False)
    s.text("doc", "安全课讲义 · 第 3 课", W - M, 52, 24, tide.INK_3, align="right",
           font=MONO)
    s.text("title", "暴雨天，这样上下学", M, 122, 44, tide.INK, bold=True)
    s.text("sub", "适用：小学四年级 · 江北街道 6 个社区 · 家长与学生共读", M, 186, 24,
           tide.INK_2)
    s.line(M, 224, W - M, 224, tide.LINE, 2)

    # ---- depth scale
    y = 248
    s.text("h1", "一、先看水有多深（街上积水深度，不是水位站的厘米数）", M, y, 26, tide.INK,
           bold=True)
    y += 44
    bx, bw, bh = M, W - 2 * M, 92
    lo = 0
    for hi, name, col, advice in data.PED:
        w = bw * (min(hi, 60) - lo) / 60.0
        s.rect(bx + lo * bw / 60.0, y, w - 3, bh, col, radius=8)
        ink = tide.PAPER if col != tide.SAND else tide.INK
        s.text("bn", f"{lo}–{min(hi, 60)} cm", bx + lo * bw / 60.0 + 12, y + 10, 22, ink,
               bold=True, font=MONO)
        s.text("bx2", name, bx + lo * bw / 60.0 + 12, y + 40, 24, ink, bold=True)
        assert tw(advice, 20) <= w + 30, advice
        lo = min(hi, 60)
    y += bh + 12
    for i, (hi, name, col, advice) in enumerate(data.PED):
        x = M + i * ((W - 2 * M) / 4)
        assert tw(advice, 20) <= (W - 2 * M) / 4 - 8, advice
        s.text("ba", advice, x, y, 20, tide.INK_2)
    y += 62

    # ---- six checks
    s.text("h2", "二、出门前 6 项检查（做完再走）", M, y, 26, tide.INK, bold=True)
    y += 44
    cw = (W - 2 * M - 2 * 16) / 3
    for i, (k, txt) in enumerate(CHECKS):
        x = M + (i % 3) * (cw + 16)
        cy = y + (i // 3) * 138
        s.rect(x, cy, cw, 126, "#FFFFFF", radius=12, border=f"1.5 SOLID {tide.LINE}")
        s.rect(x, cy, 8, 126, tide.CYAN, radius=4)
        s.text("ci", f"{i + 1}", x + 22, cy + 12, 26, tide.INK_3, font=MONO, bold=True)
        s.text("ck", k, x + 60, cy + 12, 30, tide.INK, bold=True)
        end = s.para("ct", txt, x + 22, cy + 52, 20, tide.INK_2, width=cw - 40)
        assert end - 15 <= cy + 122, txt
    y += 2 * 138 + 20

    # ---- three situations
    s.text("h3", "三、路上遇到这三种情况", M, y, 26, tide.INK, bold=True)
    y += 44
    for title, what, col in SCENES:
        s.rect(M, y, W - 2 * M, 76, "#F2EDE1", radius=12)
        s.rect(M, y, 10, 76, col, radius=5)
        s.text("st", title, M + 28, y + 10, 24, tide.INK, bold=True)
        s.text("sw", what, M + 28, y + 42, 22, tide.INK_2)
        assert tw(what, 22) <= W - 2 * M - 56, what
        y += 86
    y += 16

    # ---- quiz + sign-off
    s.text("h4", "四、回家问一问", M, y, 26, tide.INK, bold=True)
    y += 42
    for i, q in enumerate(QUIZ):
        s.text("qi", f"{i + 1}.", M, y, 22, tide.INK_3, font=MONO)
        s.text("q", q, M + 34, y, 22, tide.INK_2)
        s.line(M + 34 + tw(q, 22) + 12, y + 26, W - M - 160, y + 26, "#DCD3BF", 1.5)
        y += 44
    y += 8
    s.rect(M, y, W - 2 * M, 88, tide.INK, radius=12)
    s.text("ct", f"街道防汛值班 {data.PHONE_STREET.split()[-1]}", M + 24, y + 14, 26,
           tide.PAPER, bold=True, font=MONO)
    s.text("ct2", f"市应急 {data.PHONE_CITY.split()[-1]} · 老师值班 08:00-18:00", M + 24,
           y + 50, 22, "#9FB2BE")
    s.text("sg", "家长签字：＿＿＿＿＿＿", W - M - 24, y + 32, 24, tide.PAPER, align="right")
    y += 108
    tide.footer(s, M, y, W - 2 * M,
                ["虚构演示讲义：色条深度、社区与电话均为示例；水深与水位站读数不是同一指标。",
                 "配套：社区公告海报、小程序「水位线」实时水位与集合点导航。"], size=20)
    assert y <= H - 20, y
    return s, {"ped_bands": [[h, n, c, a] for h, n, c, a in data.PED],
               "checks": CHECKS, "situations": [a for a, b, c in SCENES],
               "quiz": QUIZ, "min_font": 20, "sheet": "A4 portrait 1:1.414"}


if __name__ == "__main__":
    s, d = build()
    (TMP / "case07.snapshot").write_text(s.dsl(), encoding="utf-8")
    (TMP / "case07-data.json").write_text(json.dumps(d, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    print(json.dumps(s.audit(margin=40), ensure_ascii=False))
