# -*- coding: utf-8 -*-
"""B02 case-04 · 菜篮订阅卡 (1080x1920 手机长图, 微信群/朋友圈转发).

user_goal: 选好规格并知道配送日与退订规则。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b02_common as C  # noqa: E402

W, H = 1080, 1920

WEEK_CROPS = ["番茄", "黄瓜", "生菜", "空心菜", "辣椒", "茄子", "南瓜", "罗勒"]


def main():
    C.assert_facts()
    els = []
    els.append(C.grad_box(0, 0, W, H, C.col(C.PAPER, "#F0E8D6"),
                          "TOP_CENTER"))
    # hero
    els.append(C.box(0, 0, W, 330, C.LEAFD))
    els.append(C.brand_header(56, 30, 560, color=C.PAPER, mark=C.SUN,
                              size=24, latin_size=11))
    els.append(C.text(56, 108, 800, 70, "菜篮订阅", 52, C.PAPER, bold=True))
    els.append(C.text(56, 186, 900, 40, "每周六 · 当季 8 种菜直配到东门传达室",
                      24, "#CDE0C4"))
    els.append(C.chip(56, 248, 240, 46, C.CLAY, "本周可订", 20, "#FFFFFF",
                      radius=23))
    els.append(C.chip(312, 248, 300, 46, "#2F5A38", "截单：每周四 20:00", 19,
                      "#D9E4CE", radius=23, border="#7FA987"))
    for i in range(6):
        els.append(C.leaf_mark(700 + i * 56, 300 - i * 14, 15, "#3E6B47",
                                stem=False))

    # three sizes
    sy = 380
    for i, (name, price, who) in enumerate(C.FACTS["basket"]):
        feat = (i == 1)
        hgt = {"小份": 236, "中份": 268, "家庭份": 274}[name]
        bg = "#FFFFFF" if feat else C.PAPER2
        els.append(C.box(56, sy, W - 112, hgt, bg, radius=20, border=C.LEAF
                         if feat else C.LINE, border_w=3 if feat else 1,
                         shadow="0 8 20 0 #6B4A2F22 NORMAL" if feat else None))
        if feat:
            els.append(C.chip(W - 356, sy + 18, 140, 40, C.CLAY, "最多人选",
                              17, "#FFFFFF", radius=20))
        els.append(C.text(92, sy + 30, 300, 56, name + "菜篮", 38, C.INK,
                          bold=True))
        els.append(C.text(92, sy + 94, 420, 34, "适合 %s" % who, 22, C.MUTED))
        els.append(C.text(92, sy + 140, 300, 70, "%d" % price, 56, C.CLAY,
                          bold=True))
        els.append(C.text(220, sy + 166, 120, 36, "元/周", 22, C.MUTED))
        # right column contents
        contents = {
            "小份": "4 种菜 · 约 3 斤 · 附 1 份香草",
            "中份": "6 种菜 · 约 5 斤 · 附 2 份香草 + 2 枚园内鸡蛋",
            "家庭份": "8 种菜 · 约 8 斤 · 附香草 + 4 枚鸡蛋 + 儿童种植盲盒",
        }[name]
        els.append(C.text(520, sy + 40, 480, 36, "篮内示例", 20, C.LEAFD,
                          bold=True))
        els.append(C.text(520, sy + 76, 490, 64, contents, 19, C.INK,
                          line_h=30))
        # crop chips for this size
        n = {"小份": 4, "中份": 6, "家庭份": 8}[name]
        for j, crop in enumerate(WEEK_CROPS[:n]):
            cx = 520 + (j % 4) * 120
            cy = sy + 152 + (j // 4) * 46
            els.append(C.chip(cx, cy, 108, 38, C.LEAFL, crop, 17, C.LEAFD,
                              radius=19))
        sy += hgt + 24

    # delivery + rules
    els.append(C.box(56, sy + 8, W - 112, 190, C.LEAFL, radius=18))
    els.append(C.text(88, sy + 28, 500, 36, "配送与自提", 26, C.LEAFD,
                      bold=True))
    dl = [
        "每周六 09:00 前送到东门传达室，凭姓名+尾号领取",
        "当周菜色随采收微调，篮内示例仅供参考",
        "满 4 周赠 1 次园内采摘体验（限 2 大 1 小）",
    ]
    for i, d in enumerate(dl):
        els.append(C.circle(98, sy + 82 + i * 38, 5, C.CLAY))
        els.append(C.text(116, sy + 68 + i * 38, 880, 32, d, 20, C.INK))
    els.append(C.box(700, sy + 30, 324, 86, "#FFFFFF", radius=12,
                     border=C.LEAF))
    els.append(C.text(716, sy + 40, 292, 30, "下单：群内接龙", 18, C.LEAFD,
                      bold=True))
    els.append(C.text(716, sy + 68, 292, 30, "或传达室登记", 18, C.LEAFD,
                      bold=True))

    # 4-step subscription flow (fills the lower band, tells the whole loop)
    fy = sy + 218
    els.append(C.text(56, fy, 500, 36, "订阅流程", 26, C.INK, bold=True))
    steps = [("1", "群内接龙下单", "备注规格+尾号"),
             ("2", "周四 20:00 截单", "超时计下周"),
             ("3", "周六采收装篮", "凌晨 5 点起采"),
             ("4", "东门传达室自提", "09:00 前送达")]
    for j, (n, t, d) in enumerate(steps):
        x = 56 + j * 252
        els.append(C.box(x, fy + 52, 228, 132, C.PAPER2, radius=14,
                         border=C.LINE))
        els.append(C.circle(x + 34, fy + 86, 18, C.CLAY))
        els.append(C.text(x + 16, fy + 74, 36, 28, n, 18, "#FFFFFF",
                          bold=True, align="CENTER"))
        els.append(C.text(x + 62, fy + 72, 156, 30, t, 18, C.INK, bold=True))
        els.append(C.text(x + 20, fy + 116, 190, 30, d, 16, C.MUTED))
        if j < 3:
            els.append(C.text(x + 230, fy + 92, 22, 30, "→", 20, C.MUTED))

    # footer rules
    els.append(C.line_h(56, H - 150, W - 56, C.LINE))
    els.append(C.text(56, H - 136, 968, 34, "退订规则", 22, C.INK, bold=True))
    els.append(C.text(56, H - 96, 968, 80,
                      "① 周四 20:00 前可退当周，全额退　② 之后不退，可转赠邻里"
                      "　③ 连续 2 周不取且失联，暂停订阅 2 周", 19, C.MUTED,
                      line_h=30))
    els.append(C.footnote(56, H - 44, 968,
                          "禾风里社区共耕花园 · 虚构演示订阅；价格与菜色均为示例"))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-04-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H)


if __name__ == "__main__":
    main()
