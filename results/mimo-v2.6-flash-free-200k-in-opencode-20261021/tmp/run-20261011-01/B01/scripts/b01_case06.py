# -*- coding: utf-8 -*-
"""B01 case-06 · 启航计划 · 首次贡献者导航 (1400x1000 terminal-editor style).

Audience: 想给开源项目提第一个 PR 的新手开发者（笔记本屏）。
Goal: 30 分钟内从选 issue 到开 PR 的每步与命令。
Fictional community "启航计划"; commands are generic real git usage.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b01_common as B  # noqa: E402

W, H = 1400, 1000
BG = "#0D1117"
PANEL = "#161B22"
INK = "#E6EDF3"
MUTED = "#8B949E"
GREEN = "#3FB950"
BLUE = "#58A6FF"
PURPLE = "#BC8CFF"
YELLOW = "#D29922"
RED = "#F85149"

# (n, title, code, minutes, accent)
STEPS = [
    (1, "挑一个“好第一 issue”", None, 5, GREEN),
    (2, "fork + 克隆到本机",
     "$ git clone git@github.com:你/启航-web.git", 6, BLUE),
    (3, "建分支，做小改动",
     "$ git checkout -b fix/拼写修正", 10, PURPLE),
    (4, "本地验证全绿",
     "$ make test && make format", 6, YELLOW),
    (5, "开 PR：关联 issue + 截图",
     "$ git push -u origin fix/拼写修正", 3, GREEN),
]
LABELS = [
    ("good first issue", GREEN, "改动 ≤ 40 行、有指路人认领"),
    ("documentation", BLUE, "错字/过时示例/缺失说明"),
    ("needs-test", YELLOW, "补一个用例就能带走"),
]
PITS = [
    ("别捎带无关改动", "一个 PR 只修一件事，review 才能快"),
    ("先跑 make format", "pre-commit 会重排代码，本地先做干净"),
    ("冲突了别硬推", "git fetch && git rebase origin/main 后再 push"),
]


def main():
    els = []
    els.append(B.grad_rect(0, 0, W, H, "#0D1117,#111A26", "TOP_LEFT",
                           "BOTTOM_RIGHT"))

    # ---------------- header ----------------
    els.append(B.rect_at(0, 0, W, 8, GREEN))
    els.append(B.text_el(60, 30, 460, 34, "启航计划 · 开源社区", 23, GREEN,
                         bold=True))
    els.append(B.text_el(60, 66, 800, 50, "首次贡献者导航", 36, INK,
                         bold=True))
    els.append(B.text_el(640, 78, 500, 28, "30 分钟：选 issue → 开出第一个 PR",
                         20, MUTED))
    els.append(B.chip_el(1160, 66, 180, 40, "#12261A", "fork → PR", 20, GREEN,
                         radius=8, border=GREEN, border_w=1))

    # ---------------- left: 5-step pipeline ----------------
    els.append(B.rect_at(50, 140, 830, 790, PANEL, radius=14))
    els.append(B.text_el(80, 158, 500, 32, "五步走完（每步给出时限）", 24, INK,
                         bold=True))
    # connector spine
    els.append(B.line_v(120, 218, 862, "#30363D", 4))
    sy0 = 210
    for n, title, code, mins, c in STEPS:
        els.append(B.circle_el(120, sy0 + 22, 22, c, shadow=None))
        els.append(B.text_el(98, sy0 + 8, 44, 30, str(n), 22, "#0D1117",
                             bold=True, align="CENTER"))
        els.append(B.text_el(162, sy0 + 2, 500, 30, title, 22, INK,
                             bold=True))
        els.append(B.chip_el(724, sy0 + 2, 110, 30, "#21262D", "%d 分钟" % mins,
                             17, MUTED, radius=15, border="#30363D",
                             border_w=1))
        if code:
            els.append(B.rect_at(162, sy0 + 40, 660, 40, "#0D1117", radius=8,
                                 border="#30363D", border_w=1))
            els.append(B.text_el(176, sy0 + 48, 640, 26, code, 18, GREEN))
        else:
            els.append(B.rect_at(162, sy0 + 40, 660, 40, "#12261A", radius=8,
                                 border="#1F6FEB33", border_w=1))
            els.append(B.text_el(176, sy0 + 48, 640, 26,
                                 "issue 列表 → 认领 → 读 CONTRIBUTING.md", 18,
                                 "#7EE787"))
        sy0 += 134

    # ---------------- right column ----------------
    els.append(B.rect_at(910, 140, 440, 384, PANEL, radius=14))
    els.append(B.text_el(936, 158, 400, 30, "三个可认领标签", 22, INK,
                         bold=True))
    ly = 204
    for lab, c, desc in LABELS:
        els.append(B.chip_el(936, ly, 200, 32, "#21262D", lab, 16, c,
                             radius=6, border=c, border_w=1))
        B.fit(desc, 16, 200, "lab")
        els.append(B.text_el(936, ly + 40, 400, 24, desc, 16, MUTED))
        ly += 100
    els.append(B.text_el(936, 486, 400, 24, "认领后 48h 内给出首个 diff", 16,
                         MUTED))

    els.append(B.rect_at(910, 546, 440, 384, PANEL, radius=14))
    els.append(B.text_el(936, 564, 400, 30, "三个最常见的坑", 22, "#F85149",
                         bold=True))
    py = 610
    for t, d in PITS:
        els.append(B.rect_at(936, py, 4, 64, RED, radius=2))
        els.append(B.text_el(952, py, 380, 26, t, 19, INK, bold=True))
        B.fit(d, 16, 380, "pit")
        els.append(B.text_el(952, py + 30, 384, 24, d, 16, MUTED))
        py += 100

    # ---------------- footer ----------------
    els.append(B.text_el(60, 950, 900, 26,
                         "启航计划 · 虚构开源社区演示 · 命令为通用 git 用法，"
                         "仓库与标签为示例", 17, MUTED))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-06-%s.snapshot" % ver)
    B.emit(os.path.normpath(out), body, W, H, BG)


if __name__ == "__main__":
    main()
