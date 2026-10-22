# -*- coding: utf-8 -*-
"""B02 case-11 · 自然课报名卡 (1200x1200 方图, 家长群转发/现场领取).

user_goal: 给孩子报名本周六自然课并知道携带物。
Theme: 番茄红 (the course topic is 番茄的一生), kid-friendly but clean.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b02_common as C  # noqa: E402

W, H = 1200, 1200

BRING = ["水壶", "遮阳帽", "旧报纸 2 张", "换洗袖套"]


def main():
    C.assert_facts()
    cl = C.FACTS["class"]
    pct = 100.0 * cl["enrolled"] / cl["seats"]
    els = []
    els.append(C.box(0, 0, W, H, C.PAPER))
    # top tomato-red band with topic
    els.append(C.grad_box(0, 0, W, 360, C.col(CLAYT := "#D94F2B", "#B83A1C"),
                          "TOP_LEFT"))
    # tomato motif (right side)
    els.append(C.circle(1010, 130, 78, "#E8613A"))
    els.append(C.circle(986, 106, 30, "#F08A62"))
    for k in range(5):
        import math
        ang = math.radians(-90 + (k - 2) * 36)
        els.append(C.leaf_mark(1010 + 66 * math.cos(ang),
                               130 + 66 * math.sin(ang), 20, "#3E7A46",
                               stem=False, rot=45))
    els.append(C.text(64, 56, 700, 40, "禾风里 · 亲子自然课", 26, "#FFD9C9",
                      bold=True))
    els.append(C.text(64, 110, 760, 110, "番茄的一生", 84, "#FFFFFF",
                      bold=True))
    els.append(C.text(64, 232, 760, 44, "从一粒种子到一篮红果 · 动手记录生长",
                      26, "#FFE4D8"))
    els.append(C.chip(64, 292, 260, 46, "#FFFFFF", "本周六 · 新课", 20,
                      "#B83A1C", radius=23))

    # time/age/pickup card
    els.append(C.box(56, 392, 1088, 150, C.PAPER2, radius=18, border=C.LINE,
                     shadow="0 6 16 0 #6B4A2F1A NORMAL"))
    facts3 = [("时间", cl["time"] + " · " + cl["dur"]),
              ("适合", cl["age"] + " · 亲子同来"),
              ("地点", "东门园艺角 · 雨天转堆肥棚")]
    for i, (k, v) in enumerate(facts3):
        x = 88 + i * 356
        els.append(C.text(x, 418, 120, 30, k, 19, C.MUTED))
        C.fit(v, 22, 330, "f3-%d" % i)
        els.append(C.text(x, 452, 336, 66, v, 22, C.INK, bold=True))
        if i:
            els.append(C.line_v(x - 34, 416, 518, C.LINE))

    # seat progress
    els.append(C.box(56, 574, 1088, 190, "#FBEAE4", radius=18))
    els.append(C.text(88, 598, 500, 40, "本场名额", 26, "#B83A1C", bold=True))
    els.append(C.text(88, 646, 420, 76, "%d / %d" % (cl["enrolled"],
                                                      cl["seats"]), 60,
                      "#B83A1C", bold=True))
    els.append(C.text(330, 664, 300, 40, "已报名", 24, "#8A4028"))
    # progress bar
    els.append(C.box(560, 646, 548, 40, "#FFFFFF", radius=20))
    els.append(C.box(560, 646, 548 * pct / 100.0, 40, "#D94F2B", radius=20))
    els.append(C.text(560, 602, 548, 34, "剩余 %d 位 · 报满即止" % (
        cl["seats"] - cl["enrolled"]), 22, "#B83A1C", bold=True))
    els.append(C.text(560, 700, 548, 34, "已连续 6 场满员，建议先占位", 19,
                      "#8A4028"))

    # bring list
    els.append(C.section(56, 806, 1088, "请带什么", size=26, mark=C.LEAF))
    bx = 56
    for b in BRING:
        w = 264
        els.append(C.box(bx, 866, w, 96, C.PAPER2, radius=14, border=C.LINE))
        els.append(C.leaf_mark(bx + 44, 914, 16, C.LEAF, stem=False))
        els.append(C.text(bx + 74, 896, w - 90, 36, b, 22, C.INK, bold=True))
        bx += w + 24
    els.append(C.text(56, 978, 1088, 34,
                      "课上提供：育苗盘 · 土 · 标签笔 · 每人 3 株番茄苗带回家",
                      20, C.MUTED))

    # signup steps
    els.append(C.box(56, 1030, 1088, 96, C.LEAFL, radius=16))
    els.append(C.text(84, 1046, 240, 34, "怎么报名", 24, C.LEAFD, bold=True))
    els.append(C.text(84, 1084, 1030, 34,
                      "① 家长群回复“孩子小名+岁数”　② 或东门传达室现场登记　"
                      "③ 开课前 1 小时群内提醒", 20, C.INK))

    els.append(C.footnote(56, H - 44, 1088,
                          "禾风里社区共耕花园 · 虚构演示课程；名额、时间与联系方式均为示例",
                          align="CENTER"))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-11-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H)


if __name__ == "__main__":
    main()
