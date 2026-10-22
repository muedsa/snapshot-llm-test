# -*- coding: utf-8 -*-
"""B01 case-07 · 安诺药房 · 处方核对单 (1240x1754 A4 print).

Audience: 社区药房药师（柜台 A4 打印）。Goal: 核对 5 位患者 7 张处方，
拦下 1 处高危相互作用 + 1 处剂量异常。
Fictional demo; clinical-checklist aesthetic.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b01_common as B  # noqa: E402

W, H = 1240, 1754
INK = "#1E293B"
MUTED = "#64748B"
RED = "#DC2626"
BLUE = "#2563EB"
LINE = "#E2E8F0"

# no, patient, drug, spec, qty, flag(None/'red'/'orange'), check cells
ROWS = [
    ("1", "王建国 72", "华法林钠片", "2.5mg × qn", "30 片", "red",
     [1, 1, 1, 1, 1, 0]),
    ("2", "王建国 72", "阿托伐他汀钙片", "20mg × qn", "30 片", None,
     [1, 1, 1, 1, 1, 1]),
    ("3", "刘敏 34", "左氧氟沙星片", "0.5g × qd", "5 片", None,
     [1, 1, 1, 1, 1, 1]),
    ("4", "陈晓 8 岁 22kg", "布洛芬混悬液", "300mg × tid", "1 瓶", "orange",
     [1, 0, 1, 1, 1, 1]),
    ("5", "陈晓 8 岁", "吸入用生理盐水", "2ml × bid", "6 支", None,
     [1, 1, 1, 1, 1, 1]),
    ("6", "赵岚 29（妊娠）", "碳酸钙 D3 咀嚼片", "600mg × qd", "28 片", None,
     [1, 1, 1, 1, 1, 1]),
    ("7", "孙博 45", "二甲双胍缓释片", "0.5g × bid", "60 片", None,
     [1, 1, 1, 1, 1, 1]),
]
COLS = [("药名", 210), ("规格频次", 165), ("数量", 95), ("药名同", 72),
        ("剂量同", 72), ("途径", 62), ("频次", 62), ("疗程", 62),
        ("相互作用", 90)]


def main():
    els = []
    els.append(B.rect_at(0, 0, W, H, "#FFFFFF"))

    # ---------------- header ----------------
    els.append(B.rect_at(0, 0, W, 12, BLUE))
    els.append(B.text_el(60, 40, 500, 36, "安诺药房 · 发药核对单", 28, INK,
                         bold=True))
    els.append(B.text_el(60, 84, 700, 26,
                         "2026-11-07 09:12 · 柜台 2 号窗口 · 药师：李蕙", 19,
                         MUTED))
    els.append(B.text_el(760, 44, 420, 30, "单号 AN-2611-0731", 20, INK,
                         align="RIGHT"))
    els.append(B.chip_el(980, 84, 200, 36, "#FEE2E2", "拦截 2 · 待电话确认",
                         17, RED, radius=18, border=RED, border_w=1))
    els.append(B.line_h(126, 60, 1180, LINE, 2))

    # ---------------- table ----------------
    ty = 150
    COLS2 = [("患者", 210), ("药品", 200), ("规格 × 频次", 150), ("数量", 90),
             ("药名同", 70), ("剂量同", 70), ("途径", 60), ("频次", 60),
             ("疗程", 60), ("相互作用", 90)]
    xs = [60]
    for _lab, wd in COLS2:
        xs.append(xs[-1] + wd)
    els.append(B.rect_at(60, ty, 1120, 40, "#F1F5F9", radius=6))
    for (lab, wd), x in zip(COLS2, xs[:-1]):
        els.append(B.text_el(x + 6, ty + 8, wd - 10, 24, lab, 16, MUTED))
    ty += 46
    for no, pat, drug, spec, qty, flag, cells in ROWS:
        c_bg = "#FEF2F2" if flag == "red" else (
            "#FFF7ED" if flag == "orange" else "#FFFFFF")
        els.append(B.rect_at(60, ty, 1120, 76, c_bg, radius=6, border=LINE,
                             border_w=1))
        if flag:
            els.append(B.rect_at(60, ty, 5, 76, RED if flag == "red"
                                 else "#EA580C", radius=2))
        vals = ["%s %s" % (no, pat), drug, spec, qty]
        for v, (lab, wd), x in zip(vals, COLS2[:4], xs[:4]):
            B.fit(v, 17, wd - 12, "r%s-%s" % (no, lab))
            els.append(B.text_el(x + 8, ty + 25, wd - 12, 26, v, 17, INK))
        for i, (ok, (lab, wd)) in enumerate(zip(cells, COLS2[4:])):
            mc = "#16A34A" if ok else RED
            els.append(B.text_el(xs[4 + i], ty + 24, wd, 28,
                                 "✓" if ok else "✕", 20, mc, bold=True,
                                 align="CENTER"))
        ty += 82

    # ---------------- red alert cards ----------------
    ay = ty + 16
    els.append(B.rect_at(60, ay, 546, 170, "#FEF2F2", radius=12, border=RED,
                         border_w=2))
    els.append(B.text_el(84, ay + 16, 500, 30, "① 高危相互作用（处方 1）", 21,
                         RED, bold=True))
    els.append(B.text_el(84, ay + 52, 500, 26,
                        "华法林 + 阿托伐他汀：出血风险升高", 18, INK))
    els.append(B.text_el(84, ay + 82, 500, 26,
                        "处置：联系处方医师确认，交代 INR 随访", 18, INK))
    els.append(B.text_el(84, ay + 112, 500, 22,
                        "确认前暂缓发出（已电话，09:20 回电）", 16, MUTED))
    els.append(B.rect_at(634, ay, 546, 170, "#FFF7ED", radius=12,
                         border="#EA580C", border_w=2))
    els.append(B.text_el(658, ay + 16, 500, 30, "② 剂量异常（处方 4）", 21,
                         "#EA580C", bold=True))
    els.append(B.text_el(658, ay + 52, 500, 26,
                        "布洛芬混悬液每次 300mg 超出体重剂量", 18, INK))
    els.append(B.text_el(658, ay + 82, 500, 26,
                        "22kg 儿童 ≤10mg/kg/次 → 应 ≤220mg", 18, INK))
    els.append(B.text_el(658, ay + 112, 500, 22,
                        "处置：请医师更正为 150mg tid 后调配", 16, MUTED))

    # ---------------- process + notes + signatures ----------------
    py = ay + 198
    els.append(B.text_el(60, py, 300, 30, "核对流程", 21, INK, bold=True))
    flow = ["收方", "审方（本次拦截 2）", "调配", "复核", "发药交代"]
    fx = 60
    for i, f in enumerate(flow):
        wd = 210 if i == 1 else 130
        c = "#FEE2E2" if i == 1 else "#F1F5F9"
        tc = RED if i == 1 else INK
        els.append(B.chip_el(fx, py + 42, wd, 40, c, f, 17, tc, radius=20,
                             border=RED if i == 1 else LINE, border_w=1))
        fx += wd + 14
        if i < len(flow) - 1:
            els.append(B.text_el(fx - 10, py + 46, 20, 30, "→", 18, MUTED))

    # 发药交代（逐患者）
    els.append(B.text_el(60, py + 110, 500, 30, "发药交代（逐患者）", 21, INK,
                         bold=True))
    NOTES = [
        ("王建国", "red",
         "华法林每日固定时间服；牙龈出血/黑便立即就诊，本周五复查 INR"),
        ("刘敏", None,
         "左氧氟沙星整疗程 5 天吃完，服药后避免烈日暴晒"),
        ("陈晓", "orange",
         "布洛芬按更正后 150mg tid；体温 <38.5℃ 不服，48h 无效复诊"),
        ("赵岚", None,
         "碳酸钙随餐嚼服；与铁剂间隔 ≥2 小时"),
        ("孙博", None,
         "二甲双胍整片吞服；服药期禁酒，腹泻样反应多 1–2 周缓解"),
    ]
    ny = py + 152
    for pat, flag, note in NOTES:
        c_bg = "#FEE2E2" if flag == "red" else (
            "#FFF7ED" if flag == "orange" else "#F1F5F9")
        c_in = RED if flag == "red" else (
            "#EA580C" if flag == "orange" else INK)
        els.append(B.chip_el(60, ny, 120, 34, c_bg, pat, 17, c_in, radius=8,
                             border=c_in if flag else LINE, border_w=1))
        B.fit(note, 17, 940, "note-%s" % pat)
        els.append(B.text_el(200, ny + 4, 950, 26, note, 17, INK))
        ny += 50

    sy = py + 390
    els.append(B.line_h(sy, 60, 1180, LINE, 2))
    els.append(B.text_el(60, sy + 16, 500, 26, "调配药师：＿＿＿＿＿", 18, MUTED))
    els.append(B.text_el(460, sy + 16, 500, 26, "复核药师：李蕙＿＿＿＿", 18,
                         MUTED))
    els.append(B.text_el(860, sy + 16, 320, 26, "时间 09:26", 18, MUTED,
                         align="RIGHT"))
    els.append(B.text_el(60, sy + 56, 1120, 22,
                        "安诺药房内部核对单 · 患者与处方均为虚构演示数据，"
                        "不构成真实用药建议", 15, "#94A3B8"))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-07-%s.snapshot" % ver)
    B.emit(os.path.normpath(out), body, W, H, "#FFFFFF")


if __name__ == "__main__":
    main()
