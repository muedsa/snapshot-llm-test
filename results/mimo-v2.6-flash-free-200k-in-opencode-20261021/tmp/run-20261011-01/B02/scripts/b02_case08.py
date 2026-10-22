# -*- coding: utf-8 -*-
"""B02 case-08 · 工具房安全须知 (900x1200, 工具房门内 0.6m).

user_goal: 取工具前读懂 6 条安全规则与归还要求。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b02_common as C  # noqa: E402

W, H = 900, 1200

RULES = [
    ("领用先登记", "白板写名字+工具编号，归还划勾"),
    ("手套必戴", "修枝剪、锄头、铁锹作业全程戴手套"),
    ("护目镜防溅", "打药、破碎果壳、使用高压水管时佩戴"),
    ("剪刀不外带", "利器仅在园内使用，不带出东门"),
    ("童工不入区", "12 岁以下儿童不得进入工具作业区"),
    ("异常即停机", "电剪/水泵异响冒烟：断电并报管理员"),
]

PPE = ["手套", "护镜", "长袖", "水鞋"]


def main():
    C.assert_facts()
    els = []
    # clay warning ground
    els.append(C.grad_box(0, 0, W, H, C.col(C.CLAY, C.CLAYD), "TOP_CENTER"))
    # header
    els.append(C.text(56, 46, 788, 66, "工具房安全须知", 46, "#FFF3EC",
                      bold=True))
    els.append(C.text(56, 118, 788, 34, "取工具前 30 秒 · 6 条硬规矩", 22,
                      "#F6D7C9"))
    els.append(C.ruler_ticks(56, 166, 788, n=24, color="#E8A98A"))

    # 6 rules in 2 columns
    gx, gy = 56, 200
    cw, ch = 380, 180
    for i, (t, d) in enumerate(RULES):
        r, c = divmod(i, 2)
        x = gx + c * (cw + 28)
        y = gy + r * (ch + 20)
        els.append(C.box(x, y, cw, ch, "#FFF6F0", radius=16))
        els.append(C.circle(x + 44, y + 44, 26, C.CLAY))
        els.append(C.text(x + 18, y + 27, 52, 36, str(i + 1), 26, "#FFFFFF",
                          bold=True, align="CENTER"))
        C.fit(t, 26, cw - 100, "rule-t%d" % i)
        els.append(C.text(x + 86, y + 24, cw - 104, 40, t, 26, C.INK,
                          bold=True))
        els.append(C.text(x + 24, y + 84, cw - 48, 80, d, 19, "#6E5A4E",
                          line_h=28))

    # PPE row
    py = gy + 3 * (ch + 20) + 4
    els.append(C.box(56, py, 788, 140, "#F9D9CB", radius=16))
    els.append(C.text(84, py + 16, 300, 32, "进入作业区先穿配", 22, C.CLAYD,
                      bold=True))
    ix = 84
    for p in PPE:
        els.append(C.circle(ix + 34, py + 86, 28, "#FFFFFF",
                            border=C.CLAY, border_w=2))
        els.append(C.text(ix + 8, py + 75, 52, 30, p, 17, C.CLAYD, bold=True,
                          align="CENTER"))
        ix += 190
    els.append(C.text(760, py + 78, 84, 26, "缺件找老陈", 14, "#8A4028",
                      align="CENTER"))

    # footer info strip
    fy = py + 156
    els.append(C.box(56, fy, 788, 200, "#3A241A", radius=16))
    els.append(C.text(84, fy + 18, 340, 34, "归还要求", 24, "#F2E8D8",
                      bold=True))
    els.append(C.text(84, fy + 56, 356, 130,
                      "① 当天归还，擦净泥水\n② 白板划勾销记\n③ 损耗照价 3 成补齐",
                      18, "#D9C7A8", line_h=30))
    els.append(C.line_v(466, fy + 18, fy + 182, "#6B4A38"))
    els.append(C.text(498, fy + 18, 320, 34, "紧急联系", 24, "#F2E8D8",
                      bold=True))
    els.append(C.text(498, fy + 56, 320, 130,
                      "管理员 老陈　138-0000-1234\n园艺志愿者 小周　群内@即可\n"
                      "受伤先冲洗：东门传达室急救箱",
                      18, "#D9C7A8", line_h=32))
    els.append(C.footnote(56, H - 34, 788,
                          "禾风里社区共耕花园 · 虚构演示须知；联系人与电话为示例",
                          color="#F0C4B2", align="CENTER"))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-08-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H, bg="#C1502E")


if __name__ == "__main__":
    main()
