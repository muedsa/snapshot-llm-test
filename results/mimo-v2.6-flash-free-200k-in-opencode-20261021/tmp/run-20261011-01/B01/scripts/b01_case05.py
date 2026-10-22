# -*- coding: utf-8 -*-
"""B01 case-05 · 琥珀剧院 · 今晚登台牌 (900x1600 backstage vertical).

Audience: 舞台监督与演员（后台侧幕张贴）。Goal: 三幕换景 cue、道具与
演员上场位置一目了然。Black-gold theater aesthetic; fictional play.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b01_common as B  # noqa: E402

W, H = 900, 1600
BG = "#16110C"
PANEL = "#211912"
INK = "#F3E7CF"
MUTED = "#A78B62"
GOLD = "#D9A84E"
RED = "#B3261E"
BLACK = "#0C0906"

# (cue, time, kind, content, where)
CUES = [
    ("C1", "19:00", "灯光", "全场起光 60% → 焦点 A 区", "操作台"),
    ("C2", "19:22", "音响", "雷声渐入 4s，雨声垫底", "音控室"),
    ("C3", "19:35", "吊杆", "景片 3 降至 2.4m（缓降）", "舞台上空"),
    ("C4", "19:48", "道具", "沙发右移 1.2m，茶几随行", "舞台左侧①"),
    ("C5", "20:00", "灯光", "黑场 2s → 月光冷光", "操作台"),
    ("C6", "20:26", "音响", "门响三连，左→右声像", "音控室"),
    ("C7", "20:40", "吊杆", "灯架升至 5m 安全位", "上空③"),
    ("C8", "20:55", "道具", "桌布 + 花瓶上场", "侧幕 B ②"),
]
KIND_C = {"灯光": "#E8B23A", "音响": "#5FA8D3", "吊杆": "#C97B4A",
          "道具": "#8FAE6B"}

ACTS = [  # (name, h0, h1, note)
    ("第一幕 · 雨夜", 19.0, 19 + 50 / 60.0, ""),
    ("幕间换景", 19 + 50 / 60.0, 20.0, "景片 3 + 沙发"),
    ("第二幕 · 争吵", 20.0, 20 + 45 / 60.0, ""),
    ("幕间换景", 20 + 45 / 60.0, 20 + 55 / 60.0, "桌布花瓶"),
    ("第三幕 · 和解", 20 + 55 / 60.0, 21 + 45 / 60.0, ""),
    ("谢幕", 21 + 45 / 60.0, 21 + 55 / 60.0, "三次返场"),
]


def hm(h):
    return "%02d:%02d" % (int(h), round((h - int(h)) * 60))


def main():
    els = []
    els.append(B.rect_at(0, 0, W, H, BG))

    # ---------------- curtain header ----------------
    els.append(B.grad_rect(0, 0, W, 190, "#7A1F1B,#4A1210,#2A0A08",
                           "TOP_CENTER", "BOTTOM_CENTER"))
    for i in range(0, W, 60):  # curtain folds
        els.append(B.opacity_rect(i, 0, 30, 190, "#000000", 0.16))
        els.append(B.opacity_rect(i + 30, 0, 30, 190, "#FFFFFF", 0.05))
    els.append(B.line_h(188, 0, W, GOLD, 3))
    els.append(B.text_el(60, 34, 300, 30, "琥珀剧院", 24, GOLD, bold=True))
    els.append(B.text_el(60, 70, 600, 50, "今晚登台牌", 40, INK, bold=True))
    els.append(B.text_el(60, 132, 640, 28,
                         "《雾港》· 11 月 7 日（周六）晚场 · 19:00 开演", 19,
                         "#E7C9A9"))
    els.append(B.chip_el(660, 76, 180, 46, BLACK, "第 24 场", 22, GOLD,
                         radius=23, border=GOLD, border_w=2))

    # ---------------- act timeline ----------------
    els.append(B.rect_at(40, 214, 820, 200, PANEL, radius=14))
    els.append(B.text_el(64, 226, 400, 30, "时间轴（19:00 – 21:55）", 22, INK,
                         bold=True))
    TX0, TX1 = 64.0, 836.0
    ty = 286

    def tx(h):
        return TX0 + (h - 19.0) / (21 + 55 / 60.0 - 19.0) * (TX1 - TX0)

    for name, h0, h1, note in ACTS:
        is_gap = note and name.startswith("幕间")
        c = "#3A2E20" if is_gap else "#5A2320"
        els.append(B.rect_at(tx(h0), ty, tx(h1) - tx(h0) - 3, 40, c,
                             radius=6, border="#7A5A33" if not is_gap
                             else "#4A3A26", border_w=1))
        if tx(h1) - tx(h0) > 90:
            els.append(B.text_el(tx(h0) + 6, ty + 8, tx(h1) - tx(h0) - 16,
                                 24, name, 16, INK if not is_gap else MUTED,
                                 align="CENTER"))
    for h, lab in ((19.0, "19:00"), (20.0, "20:00"), (21.0, "21:00")):
        els.append(B.line_v(tx(h), ty + 44, ty + 52, MUTED, 2))
        els.append(B.text_el(tx(h) - 30, ty + 54, 60, 22, lab, 15, MUTED,
                             align="CENTER"))
    els.append(B.text_el(64, ty + 84, 772, 24,
                         "幕间换景共 15 分钟（19:50 / 20:45）· 21:45 谢幕三次返场"
                         " · C3/C7 吊杆须清场确认", 16, MUTED))

    # ---------------- cue table ----------------
    els.append(B.text_el(40, 440, 400, 34, "CUE 表（8 条）", 24, GOLD,
                         bold=True))
    cy = 486
    els.append(B.rect_at(40, cy, 820, 34, "#2E2418", radius=8))
    for lab, x, wdt in (("编号", 60, 80), ("时间", 150, 90), ("系统", 250, 90),
                        ("内容", 350, 380), ("执行位", 640, 200)):
        els.append(B.text_el(x, cy + 6, wdt, 24, lab, 17, MUTED))
    cy += 42
    for cue, t, kind, content, where in CUES:
        els.append(B.rect_at(40, cy, 820, 52, PANEL, radius=8))
        els.append(B.text_el(60, cy + 12, 80, 28, cue, 20, GOLD, bold=True))
        els.append(B.text_el(150, cy + 12, 90, 28, t, 20, INK))
        els.append(B.chip_el(250, cy + 10, 74, 30, BLACK, kind, 16,
                             KIND_C[kind], radius=6, border=KIND_C[kind],
                             border_w=1))
        B.fit(content, 18, 280, cue)
        els.append(B.text_el(350, cy + 14, 380, 26, content, 18, INK))
        els.append(B.text_el(640, cy + 14, 200, 26, where, 17, MUTED))
        cy += 58

    # ---------------- stage plan ----------------
    els.append(B.text_el(40, cy + 16, 500, 34, "舞台平面 · 道具位（俯视）",
                         24, GOLD, bold=True))
    py = cy + 60
    els.append(B.rect_at(60, py, 780, 250, BLACK, radius=10, border="#7A5A33",
                         border_w=2))
    els.append(B.rect_at(80, py + 20, 740, 24, "#3A2E20", radius=4))
    els.append(B.text_el(80, py + 22, 740, 22, "台口（观众席方向）", 15,
                         MUTED, align="CENTER"))
    # wings
    els.append(B.rect_at(64, py + 28, 60, 200, "#241C12", radius=6))
    els.append(B.text_el(64, py + 108, 60, 24, "侧幕A", 14, MUTED,
                         align="CENTER"))
    els.append(B.rect_at(776, py + 28, 60, 200, "#241C12", radius=6))
    els.append(B.text_el(776, py + 108, 60, 24, "侧幕B", 14, MUTED,
                         align="CENTER"))
    # prop positions ①②③④
    props = [
        ("①", 180, py + 90, "#8FAE6B", "沙发+茶几 19:48 移位"),
        ("②", 620, py + 150, "#8FAE6B", "桌布+花瓶 20:55 上"),
        ("③", 430, py + 60, "#C97B4A", "灯架/景片3（上空）"),
        ("④", 240, py + 190, "#5FA8D3", "雷效音箱左置"),
    ]
    for mark, x, y, c, lab in props:
        els.append(B.circle_el(x, y, 18, c, shadow=None))
        els.append(B.text_el(x - 18, y - 12, 36, 24, mark, 18, BLACK,
                             bold=True, align="CENTER"))
        els.append(B.text_el(x + 26, y - 12, 220, 24, lab, 14, MUTED))
    # actor entries
    els.append(B.text_el(150, py + 214, 240, 22, "上场门 →（A 侧）", 14,
                         "#D9A84E"))
    els.append(B.text_el(560, py + 214, 220, 22, "← 下场门（B 侧）", 14,
                         "#D9A84E", align="RIGHT"))

    # ---------------- safety + footer ----------------
    sy0 = py + 272
    els.append(B.rect_at(60, sy0, 780, 78, "#2A0A08", radius=10,
                         border=RED, border_w=2))
    els.append(B.text_el(84, sy0 + 12, 400, 28, "警铃规则（全员）", 20, "#F87171",
                         bold=True))
    els.append(B.text_el(84, sy0 + 42, 730, 26,
                         "铃响 = 吊杆立即停机、灯光保底 20%、演员原地候场；"
                         "复位口令由舞台监督下达", 16, "#E7C9A9"))
    els.append(B.text_el(60, sy0 + 100, 470, 26, "舞台监督：周宁（分机 812）",
                         17, MUTED))
    els.append(B.text_el(470, sy0 + 100, 370, 26, "签名：＿＿＿＿＿", 17,
                         MUTED, align="RIGHT"))
    els.append(B.text_el(60, sy0 + 130, 780, 22,
                         "琥珀剧院内部用牌 · 剧目与人员为虚构演示", 14, "#6B5738"))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-05-%s.snapshot" % ver)
    B.emit(os.path.normpath(out), body, W, H, BG)


if __name__ == "__main__":
    main()
