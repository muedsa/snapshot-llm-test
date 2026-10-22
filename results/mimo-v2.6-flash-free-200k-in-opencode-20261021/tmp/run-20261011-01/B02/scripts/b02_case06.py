# -*- coding: utf-8 -*-
"""B02 case-06 · 厨余堆肥三步图 (1000x1400, 堆肥箱旁立牌 0.8m).

user_goal: 30 秒学会可投/不可投与三层堆法。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b02_common as C  # noqa: E402

W, H = 1000, 1400


def main():
    C.assert_facts()
    els = []
    els.append(C.box(0, 0, W, H, C.PAPER))
    # header
    els.append(C.box(0, 0, W, 132, C.SOIL))
    els.append(C.brand_header(44, 20, 500, color="#F2E8D8", mark=C.SUN,
                              size=23, latin_size=10))
    els.append(C.text(44, 66, 700, 46, "厨余堆肥三步法", 34, "#F2E8D8",
                      bold=True))
    els.append(C.text(700, 44, 256, 60, "每%s\n产 %s 吨堆肥" % (
        "季转化", C.FACTS["compost_out"]), 17, "#D9C7A8", align="RIGHT",
        line_h=24))

    # three-layer diagram (left) + text steps (right)
    els.append(C.section(44, 170, 912, "三层堆法（一铲一层）", size=26))
    dx, dy, dw = 60, 236, 300
    layers = [
        ("顶层 · 干料", "落叶/纸箱碎屑 10cm", "#C9A97A", C.SOIL),
        ("中层 · 厨余", "菜叶果皮 15cm（本次投放）", "#8A5A34", "#F2E8D8"),
        ("底层 · 通气", "粗枝架空 10cm，沥液排出", "#5E4630", "#E5D8C2"),
    ]
    lh = 128
    for i, (t, d, bg, fg) in enumerate(layers):
        y = dy + i * lh
        els.append(C.box(dx, y, dw, lh - 10, bg, radius=10))
        els.append(C.text(dx + 20, y + 16, dw - 40, 34, t, 22, fg, bold=True))
        els.append(C.text(dx + 20, y + 54, dw - 40, 48, d, 16, fg,
                          line_h=22))
    # arrow of rotation
    els.append(C.text(dx + dw + 4, dy + 170, 40, 40, "↻", 30, C.CLAY,
                      bold=True, align="CENTER"))
    els.append(C.text(dx, dy + 3 * lh - 2, dw + 60, 56,
                      "每 5 天翻堆 1 次 · 21–28 天成熟", 18, C.CLAY,
                      bold=True, align="CENTER"))

    # right column: steps 1-2-3
    rx = 420
    steps = [
        ("1", "投放前沥水", "厨余沥干水分，减少异味与果蝇"),
        ("2", "按层入箱", "一层干料垫底，再进厨余，最后盖干料封面"),
        ("3", "翻堆与出肥", "每 5 天翻 1 次；变褐色松散即熟"),
    ]
    sy = 240
    for n, t, d in steps:
        els.append(C.circle(rx + 26, sy + 26, 24, C.CLAY))
        els.append(C.text(rx + 6, sy + 8, 40, 34, n, 24, "#FFFFFF",
                          bold=True, align="CENTER"))
        els.append(C.text(rx + 68, sy, 470, 34, t, 24, C.INK, bold=True))
        els.append(C.text(rx + 68, sy + 38, 480, 60, d, 18, C.MUTED,
                          line_h=26))
        sy += 128

    # can / cannot lists
    els.append(C.section(44, 664, 912, "能投什么 · 不能投什么", size=26))
    ly = 728
    els.append(C.box(44, ly, 446, 330, "#EAF2E2", radius=14, border=C.LEAF))
    els.append(C.text(72, ly + 18, 380, 34, "✓ 可投", 24, C.LEAFD, bold=True))
    yes = ["菜叶 · 果皮 · 蛋壳（碾碎）", "茶渣 · 咖啡渣 · 滤纸",
           "落叶 · 杂草（未结籽）", "纸巾 · 纸箱碎屑（素色）",
           "残饭（沥水后少量）"]
    yy = ly + 66
    for item in yes:
        els.append(C.circle(80, yy + 12, 5, C.LEAF))
        els.append(C.text(98, yy, 376, 44, item, 18, C.INK, line_h=24))
        yy += 52
    els.append(C.box(510, ly, 446, 330, "#FBEAE4", radius=14, border=C.CLAY))
    els.append(C.text(538, ly + 18, 380, 34, "✕ 不可投", 24, C.CLAYD,
                      bold=True))
    no = ["肉 · 骨头 · 鱼（招鼠猫）", "油 · 汤汁（破坏堆体）",
          "宠物粪便 · 猫砂（病原）", "塑料袋 · 餐盒（不可降解）",
          "病株 · 喷药杂草（带菌）"]
    ny = ly + 66
    for item in no:
        els.append(C.circle(546, ny + 12, 5, C.CLAY))
        els.append(C.text(564, ny, 376, 44, item, 18, C.INK, line_h=24))
        ny += 52

    # mature compost usage strip
    els.append(C.box(44, 1086, 912, 130, C.LEAFL, radius=14))
    els.append(C.text(72, 1104, 500, 32, "熟堆肥怎么用", 22, C.LEAFD,
                      bold=True))
    els.append(C.text(72, 1144, 856, 60,
                      "① 每块地每季基肥 2 斤，撒施后浅翻　② 熟料可免费自取（东门堆肥棚，"
                      "自备袋）　③ 本季已产 %s 吨，进度见季度报告" %
                      C.FACTS["compost_out"], 18, C.INK, line_h=28))

    # footer
    els.append(C.line_h(44, H - 128, W - 44, C.LINE))
    els.append(C.footnote(44, H - 114, 620,
                          "值守：堆肥组 · 老陈（每周六 10:00 现场答疑）"))
    els.append(C.footnote(44, H - 84, 912,
                          "禾风里社区共耕花园 · 虚构演示说明牌；周期与配比为演示参数"))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-06-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H)


if __name__ == "__main__":
    main()
