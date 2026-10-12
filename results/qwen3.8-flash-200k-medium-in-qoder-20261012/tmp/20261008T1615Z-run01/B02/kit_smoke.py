"""B02 设计系统构件烟雾测试：一次性把 brand_mark / hex_chip / ruler / card /
stamp / footer / section_head 在浅色与深色、三种密度下画在同一张图上。

运行：
    python tmp/<run_id>/B02/kit_smoke.py
    python tmp/<run_id>/_suite/scripts/render.py --task B02 --version kit-smoke-01 \\
        --in tmp/<run_id>/B02/kit-smoke.snapshot --out tmp/<run_id>/B02/kit-smoke.png \\
        --kind syntax --note "B02 设计系统构件烟雾测试"
"""
import os
import sys
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(root / "tmp" / rid / "_suite" / "scripts"))
sys.path.insert(0, str(root / "tmp" / rid / "B01"))
sys.path.insert(0, str(root / "tmp" / rid / "B02"))

from dslkit import Doc, TextFit  # noqa: E402
import b02kit as B  # noqa: E402

W, H = 1400, 900
tf = TextFit()
d = B.paper_doc(W, H, noise=18)
tf.check("smoke-title", "构件烟雾测试 KIT SMOKE", 30, 620, 40)
d.label(48, 34, 620, 40, "构件烟雾测试 KIT SMOKE", B.P["ink"], 30, "BOLD", "START")
tf.check("smoke-sub", "六角 / 刻度 / 印章 / 页脚 / 深浅底", 14, 500, 24)
d.label(48, 78, 500, 24, "六角 / 刻度 / 印章 / 页脚 / 深浅底", B.P["ink2"], 14, None,
        "START", valign="TOP")

# 左：浅纸底
B.brand_mark(d, 150, 225, 62, bg=B.P["paper"])
B.brand_mark(d, 300, 205, 38, bg=B.P["paper"])
B.brand_mark(d, 392, 192, 22, bg=B.P["paper"])
for i, (R, c, lab, ring) in enumerate([
        (26, B.P["green"], "在馆", False), (22, B.P["steel"], "在借", False),
        (18, B.P["greyblue"], "修", False), (20, B.P["red"], "逾期", True)]):
    B.hex_chip(d, 90 + i * 74, 335, R, c, lab, ring=ring, bg=B.P["paper"])
for i, (R, c) in enumerate([(30, B.P["ink"]), (24, B.P["orange"]), (18, B.P["steel"])]):
    B.hex_outline(d, 560 + i * 62, 205, R, c)
tf.check("smoke-outline", "hex_outline：直线斜边，大尺寸标志用", 12, 300, 18)
d.label(500, 250, 300, 18, "hex_outline：直线斜边", B.P["ink3"], 12, None, "START",
        valign="TOP")

B.section_head(d, 60, 400, 620, 3, "类目与状态", "9 / 412", dark=False)
for i, (frac, tone, lab, ticks) in enumerate([
        (0.285, B.P["orange"], "28.5%", "full"), (0.171, B.P["steel"], "17.1%", "full"),
        (0.098, B.P["brass"], "9.8%", "compact"), (0.037, B.P["greyblue"], "3.7%", "micro")]):
    B.ruler(d, 60, 452 + i * 40, 420, frac, tone, h=16, ticks=ticks, label=lab,
            lw=74, ls=17)

B.card(d, 60, 630, 300, 150, title="示例卡片", sub="card() 的标题与副标题")
tf.check("smoke-card", "正文一行，测试 17 号字宽度", 17, 250, 26)
d.label(80, 700, 250, 26, "正文一行，测试 17 号字宽度", B.P["ink"], 17, None, "START")
B.stamp(d, 380, 640, 210, 74, "逾期 4 天", deg=-9, size=22, tf=tf)
B.stamp(d, 380, 740, 210, 56, "待保养", color=B.P["brass"], deg=6, size=18, tf=tf)

B.footer(d, 60, 812, 620, "full", dark=False)
B.footer(d, 60, 856, 620, "receipt", dark=False)

# 右：深色触摸屏底
dx = 740
d.rect(dx, 120, 600, 720, B.P["dark"], radius=12)
B.brand_mark(d, dx + 110, 225, 46, ink=B.P["white"], bg=B.P["dark"])
tf.check("smoke-dark-head", "深色底 · 触摸屏 / 夜间门头", 24, 380, 34)
d.label(dx + 180, 196, 380, 34, "深色底 · 触摸屏 / 夜间门头", B.P["white"], 24, "BOLD",
        "START")
for i, (R, c, lab, ring) in enumerate([
        (26, B.P["green"], "在馆", False), (22, B.P["brass"], "4", False),
        (18, B.P["steel"], "借", True), (20, B.P["red"], "15", True)]):
    B.hex_chip(d, dx + 90 + i * 78, 320, R, c, lab, ring=ring, bg=B.P["dark"],
               dark=True)
B.section_head(d, dx + 40, 380, 520, 7, "深色小标题", "SH-07", dark=True)
for i, (frac, tone, lab, ticks) in enumerate([
        (0.552, B.P["orange"], "55.2%", "full"), (0.213, B.P["green"], "21.3%", "compact"),
        (0.061, B.P["greyblue"], "6.1%", "micro")]):
    B.ruler(d, dx + 40, 434 + i * 40, 380, frac, tone, h=16, ticks=ticks, label=lab,
            lw=70, ls=17, dark=True)
B.card(d, dx + 40, 580, 260, 130, title="深色卡片", sub="card(dark=True)", dark=True)
B.stamp(d, dx + 340, 590, 200, 66, "会员有效", color=B.P["green"], deg=-7, size=20,
        dark=True, tf=tf)
B.footer(d, dx + 40, 730, 520, "short", dark=True)
B.footer(d, dx + 40, 766, 520, "micro", dark=True)
tf.check("smoke-footer-note", "十件触点共用的识别锚点退化测试", 12, 400, 20)
d.label(dx + 40, 792, 400, 20, "十件触点共用的识别锚点退化测试",
        B.blend("#FFFFFF", 0.5, B.P["dark"]), 12, None, "START", valign="TOP")

(out := root / "tmp" / rid / "B02" / "kit-smoke.snapshot").write_text(d.dsl(), encoding="utf-8")
print(out.relative_to(root).as_posix(), len(d.dsl()), "textfit:", tf.n, "problems:", tf.problems[:4])
