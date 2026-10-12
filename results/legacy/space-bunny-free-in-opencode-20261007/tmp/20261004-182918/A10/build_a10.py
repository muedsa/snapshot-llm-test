# -*- coding: utf-8 -*-
"""A10 透明合成与滤镜语义实验板 —— 生成器。

用法：
    python build_a10.py main              # 渲染最终 1440x1100 实验板
    python build_a10.py probe <name>      # 渲染某个单格探针图到临时目录
"""
from __future__ import annotations

import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402

TASK = "A10"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)

W, H = 1440, 1100
PW, PH = 320, 240          # 每个实验区的尺寸
SIGMA = 6
COLS = [48, 560, 1072]
ROWS = [186, 572]
CARD = (240, 160, 20)      # ③④ 卡：宽、高、圆角
TINT = "#F6B94A"           # ⑤⑥ 滤色
RED_A, BLUE_A = "#FF000080", "#0000FF80"
SAMPLE = (180, 100)        # 每格规定的重叠采样点（格内坐标）
STRIPE_H = 212             # 条纹带高度；其下保留白底作为未着色对照
SAMPLE_MARK = (180, 78)    # 采样点的可视标记位置（避开采样像素本身）
GAP = 192                  # 列间距（>=32）
ROW_GAP = ROWS[1] - (ROWS[0] + PH)   # 行间距

TITLE = "看到差异，才能说用对了"

CAPTIONS = [
    "两个矩形各自带 50% alpha：红在下 #FF000080、蓝在上 #0000FF80，重叠处同时看到两层颜色。",
    "同样两个完全不透明的矩形放进 Opacity(0.5) 组：整组先离屏合成再整体半透明，重叠只剩上层蓝。",
    "圆角卡内用 ClipRRect + BackdropFilter 读卡后已画的条纹并模糊，卡面文字与形状保持锐利。",
    "同样条纹改放进 ImageFiltered 子树：条纹、形状与 SHARP / BLUR 被一起高斯模糊，字明显发糊。",
    "ColorFiltered(MULTIPLY, #F6B94A) 在外、ImageFiltered sigma 6 在内；琥珀色铺满子树边界内的透明间隙。",
    "同样的滤色与模糊再套一层 ClipOval：方形子树边界被裁成圆形，琥珀色止步于圆边，卡外条纹不变。",
]

LABELS = [
    "逐像素 50% alpha",
    "组 Opacity(0.5)",
    "只模糊背景",
    "整棵子树模糊",
    "滤色 + 子树模糊",
    "滤色 + 圆形裁剪",
]

NOTES = {
    1: "红 40,40,160,120｜蓝 120,80,160,120｜蓝在上",
    2: "子层 (255,0,0)+(0,0,255)｜整层 ×0.5 后压白底",
    3: "卡 240×160 r20｜BackdropFilter σ6｜卡外条纹不变",
    4: "卡 240×160 r20｜ImageFiltered σ6｜文字同源同字号",
    5: "MULTIPLY #F6B94A｜σ6 扩张 3σ=18px｜边界 +5,5,+10,0",
    6: "ClipOval 200×200｜子树方形边界→圆形可见范围",
}


def circ(x, y, d, **kw):
    """BoxShape.CIRCLE 的圆形容器（dsllib.box 不支持 shape 属性）。"""
    kw["extra"] = dict(kw.get("extra") or {}, shape="CIRCLE")
    return D.box(x, y, d, d, **kw)


def stripes(x0: float, y0: float, w: float, h: float, period: float = 20.0,
            bar: float = 10.0, color: str = "#C7D2DEFF") -> str:
    """竖直锐利条纹；x0 可以是负数，用于卡内复制条纹。"""
    out = []
    period = int(period)
    bar = int(bar)
    start = int(x0) - (int(x0) % period)
    x = start
    while x < x0 + w:
        cx0 = max(x, int(x0))
        cx1 = min(x + bar, int(x0 + w))
        if cx1 > cx0:
            out.append(D.box(cx0, y0, cx1 - cx0, h, color=color))
        x += period
    return "\n".join(out)


def stack_box(x, y, w, h, kids, extra=None):
    """Positioned > Container(w,h) > Stack(fit=EXPAND) —— 实验区内容容器。"""
    pa = {"left": round(x, 2), "top": round(y, 2), "width": w, "height": h}
    core = {"width": w, "height": h}
    if extra:
        core.update(extra)
    return D.el("Positioned", pa, [D.el("Container", core,
                                       [D.el("Stack", {"fit": "EXPAND"}, kids)])])


def panel(cx, py, kids):
    """320x240 白底实验区 + 1px 描边。"""
    pa = {"left": cx, "top": py, "width": PW, "height": PH}
    core = {"width": PW, "height": PH, "color": "#FFFFFFFF",
            "border": "1 SOLID #CBD5E1FF"}
    return D.el("Positioned", pa, [D.el("Container", core,
                                       [D.el("Stack", {"fit": "EXPAND"}, kids)])])


def sample_marker(cx, py, extra=True):
    """采样点标记：外圈环 + 实心点，放在 (180,78) 以免污染 (180,100) 的采样像素。"""
    out = [D.box(SAMPLE_MARK[0] - 8, SAMPLE_MARK[1] - 8, 16, 16, color=None,
                 border="2 SOLID #0F172AFF", radii={
                     "TopLeft": 8, "TopRight": 8, "BottomLeft": 8, "BottomRight": 8}),
           D.box(SAMPLE_MARK[0] - 2, SAMPLE_MARK[1] - 2, 4, 4, color="#DC2626FF")]
    if extra:
        out.append(D.text_el("采样 (180,100)", x=SAMPLE_MARK[0] + 12,
                             y=SAMPLE_MARK[1] - 9, w=132, h=20, size=13,
                             color="#0F172AFF", shadow="0 0 4 #FFFFFFF2"))
    return "\n".join(out)


# ---------------------------------------------------------------- ① 逐像素 alpha
def panel_alpha():
    return [
        D.box(40, 40, 160, 120, color=RED_A),
        D.box(120, 80, 160, 120, color=BLUE_A),
        D.text_el("red #FF000080", x=44, y=22, w=160, h=18, size=13, color="#7F1D1DFF"),
        D.text_el("blue #0000FF80", x=124, y=204, w=170, h=18, size=13, color="#1E3A8AFF"),
        sample_marker(0, 0),
    ]


# ------------------------------------------------------------- ② 组 Opacity(0.5)
def panel_group():
    inner = [
        D.box(40, 40, 160, 120, color="#FF0000FF"),
        D.box(120, 80, 160, 120, color="#0000FFFF"),
    ]
    group = D.el("Stack", {"fit": "EXPAND", "width": PW, "height": PH}, inner)
    return [
        D.el("Positioned", {"left": 0, "top": 0, "width": PW, "height": PH},
             [D.el("Opacity", {"opacity": "0.5"}, [group])]),
        D.text_el("Opacity(0.5) 组", x=14, y=221, w=180, h=16, size=12,
                  color="#0F172AFF"),
        D.box(206, 222, 22, 13, color="#FF0000FF"),
        D.box(232, 222, 22, 13, color="#0000FFFF"),
        D.text_el("red/blue 子层", x=14, y=22, w=180, h=18, size=13, color="#7F1D1DFF"),
        sample_marker(0, 0),
    ]


# ------------------------------------------------ ③ BackdropFilter：只模糊背景
def card_text_and_shapes():
    """③④ 卡内共用的文字与形状，坐标为卡内局部坐标。"""
    return [
        D.text_el("SHARP / BLUR", x=16, y=32, w=208, h=32, size=24,
                  color="#0F172AFF"),
        D.box(20, 78, 110, 26, color="#2563EBFF", radius=8),
        D.box(138, 78, 86, 26, color="#F59E0BFF", radius=8),
        circ(20, 118, 30, color="#10B981FF"),
        D.box(60, 132, 164, 8, color="#0F172A80"),
    ]


def panel_backdrop():
    cx, cy = 40, 40
    kids = [stripes(0, 0, PW, STRIPE_H)]
    frost = D.el("BackdropFilter", {"sigmaX": SIGMA, "sigmaY": SIGMA},
                 [D.el("Container", {"width": CARD[0], "height": CARD[1],
                                     "color": "#FFFFFFA6"})])
    clip = D.el("ClipRRect", {"borderRadius": CARD[2]}, [frost])
    kids.append(D.el("Positioned",
                     {"left": cx, "top": cy, "width": CARD[0], "height": CARD[1]},
                     [clip]))
    kids.append(D.el("Positioned",
                     {"left": cx, "top": cy, "width": CARD[0], "height": CARD[1]},
                     [D.el("Stack", {"fit": "EXPAND"}, card_text_and_shapes())]))
    kids += [
        D.text_el("卡片 240×160 r20", x=42, y=218, w=180, h=18, size=13,
                  color="#0F172AFF"),
        D.text_el("σ6 只作用于背后条纹", x=42, y=16, w=250, h=18, size=13,
                  color="#0F172AFF"),
    ]
    return kids


# ------------------------------------------------ ④ ImageFiltered：整棵子树模糊
def panel_imagefilter():
    cx, cy = 40, 40
    w, h = CARD[0], CARD[1]
    # 子树自带不透明底板：否则卡内透明间隙会漏出背后清晰的条纹，
    # 模糊效果就被背景抵消（实测 p4-v1 的教训）。
    inner = [D.box(0, 0, w, h, color="#F1F5F9FF"),
             stripes(-40, 0, w + 80, h)] + card_text_and_shapes()
    sub = D.el("Stack", {"fit": "EXPAND", "width": w, "height": h}, inner)
    filtered = D.el("ImageFiltered", {"sigmaX": SIGMA, "sigmaY": SIGMA},
                    [D.el("Container", {"width": w, "height": h}, [sub])])
    kids = [stripes(0, 0, PW, STRIPE_H)]
    kids.append(D.el("Positioned", {"left": cx, "top": cy, "width": w, "height": h},
                     [D.el("ClipRRect", {"borderRadius": CARD[2]}, [filtered])]))
    # 卡片参考边界（不参与模糊），用短划线拼出
    kids.append(D.dashed(cx, cx + w, cy, "#0F172A66", w=1, dash=6, gap=5))
    kids.append(D.dashed(cx, cx + w, cy + h, "#0F172A66", w=1, dash=6, gap=5))
    for yy in range(cy + 6, cy + h - 3, 10):
        kids.append(D.box(cx, yy, 1, 4, color="#0F172A66"))
        kids.append(D.box(cx + w - 1, yy, 1, 4, color="#0F172A66"))
    kids += [
        D.text_el("卡片 240×160 r20", x=42, y=218, w=180, h=18, size=13,
                  color="#0F172AFF"),
        D.text_el("σ6 作用于整棵子树", x=42, y=16, w=250, h=18, size=13,
                  color="#0F172AFF"),
    ]
    return kids


# ------------------------------------------ ⑤ / ⑥ MULTIPLY 滤色 + 子树高斯模糊
def tint_content(w, h):
    """⑤⑥ 共用的滤色内容：2px 子树边框、深色矩形、阴影圆与透明间隙。"""
    return [
        D.box(0, 0, w, h, border="2 SOLID #0F172AB3"),
        D.box(16, 26, 86, 34, color="#0F172AF2"),
        D.box(16, 68, 84, 10, color="#0F172A99"),
        circ(150, 26, 48, color="#93C5FDF2", shadow="4 10 10 -2 #0F172ABF"),
        D.box(w - 64, h - 48, 54, 32, color="#1E293BF2"),
    ]


def panel_multiply(clip_oval=False, edges=None):
    """edges=(l,t,r,b) 为实测的滤色边界；缺省按名义子树 ±18 标注。"""
    kids = [stripes(0, 0, PW, STRIPE_H)]
    if not clip_oval:
        bw, bh, bx, by = 240, 160, 40, 40
    else:
        bw, bh, bx, by = 200, 200, 60, 20
    inner = tint_content(bw, bh)
    sub = D.el("Stack", {"fit": "EXPAND", "width": bw, "height": bh}, inner)
    filtered = D.el("ImageFiltered", {"sigmaX": SIGMA, "sigmaY": SIGMA},
                    [D.el("Container", {"width": bw, "height": bh}, [sub])])
    tinted = D.el("ColorFiltered", {"color": TINT, "blendMode": "MULTIPLY"},
                  [filtered])
    node = D.el("ClipOval", {}, [tinted]) if clip_oval else tinted
    kids.append(D.box(bx, by, bw, bh, children=[
        D.el("Stack", {"fit": "EXPAND"}, [
            D.el("Positioned", {"left": 0, "top": 0, "width": bw, "height": bh},
                 [node])])]))
    if clip_oval:
        kids.append(D.box(bx, by, bw, bh, border="1 SOLID #0F172A80"))
        for cxx, cyy in ((bx, by), (bx + bw - 5, by), (bx, by + bh - 5),
                         (bx + bw - 5, by + bh - 5)):
            kids.append(D.box(cxx, cyy, 5, 5, color="#0F172AFF"))
        kids.append(D.text_el("方形子树边界 200×200 → ClipOval 圆形裁剪",
                              x=14, y=2, w=292, h=16, size=11, color="#0F172AFF"))
    else:
        if edges is None:
            edges = (bx - 18, by - 18, bx + bw + 18, by + bh + 18)
        el, et, er, eb = edges
        # 四角标记画在滤色边界外侧 3px，不遮挡边界本身
        kids.append(D.box(el - 3, et - 3, 14, 1, color="#0F172AFF"))
        kids.append(D.box(el - 3, et - 3, 1, 14, color="#0F172AFF"))
        kids.append(D.box(er - 11, et - 3, 14, 1, color="#0F172AFF"))
        kids.append(D.box(er + 3, et - 3, 1, 14, color="#0F172AFF"))
        kids.append(D.box(el - 3, eb + 3, 14, 1, color="#0F172AFF"))
        kids.append(D.box(el - 3, eb - 11, 1, 14, color="#0F172AFF"))
        kids.append(D.box(er - 11, eb + 3, 14, 1, color="#0F172AFF"))
        kids.append(D.box(er + 3, eb - 11, 1, 14, color="#0F172AFF"))
        kids.append(D.text_el("滤色边界 x%d–%d y%d–%d ＝子树±3σ"
                              % (el, er - 1, et, eb - 1),
                              x=8, y=220, w=304, h=16, size=12,
                              color="#0F172AFF"))
    return kids


PANEL_BUILDERS = [panel_alpha, panel_group, panel_backdrop, panel_imagefilter,
                  lambda: panel_multiply(False), lambda: panel_multiply(True)]


def board(measured=None):
    """measured: 可选的 dict，index -> 实测值文本，用于第二遍渲染。"""
    kids = []
    # ---- 顶部标题区
    kids.append(D.text_el(TITLE, x=48, y=34, w=760, h=54, size=40,
                          color="#0F172AFF", style="BOLD"))
    kids.append(D.text_el("A10 · 六格对照实验：透明合成、Opacity 组、背景滤镜、子树滤镜与裁剪边界",
                          x=48, y=94, w=900, h=24, size=17, color="#475569FF"))
    kids.append(D.hline(48, 1392, 120, "#CBD5E1FF", 1.5))
    kids.append(D.text_el("画布 1440×1100 ｜ 6 格 × 320×240 ｜ 格间距 %dpx / %dpx ｜ 抽样点 (180,100)"
                          % (GAP, ROW_GAP),
                          x=700, y=44, w=692, h=22, size=14, color="#64748BFF",
                          align="END"))
    kids.append(D.text_el("白底=未着色对照 ｜ 细虚线=标注边界 ｜ 红点=采样位置",
                          x=700, y=70, w=692, h=20, size=13, color="#94A3B8FF",
                          align="END"))

    # ---- 六格
    for i in range(6):
        col, row = i % 3, i // 3
        cx, py = COLS[col], ROWS[row]
        kids.append(circ(cx, py - 40, 30, color="#0F172AFF"))
        kids.append(D.text_el(str(i + 1), x=cx, y=py - 36, w=30, h=24, size=19,
                              color="#FFFFFFFF", align="CENTER"))
        kids.append(D.text_el(LABELS[i], x=cx + 40, y=py - 37, w=280, h=26, size=20,
                              color="#0F172AFF", style="BOLD"))
        kids.append(panel(cx, py, PANEL_BUILDERS[i]()))
        kids.append(D.text_el(CAPTIONS[i], x=cx, y=py + PH + 10, w=PW, h=58,
                              size=14, color="#334155FF", line_height=19))
        kids.append(D.text_el(NOTES[i + 1], x=cx, y=py + PH + 70, w=PW, h=18,
                              size=12, color="#64748BFF"))
        # 实测值（小字，写在实验区下方说明里）
        if measured and measured.get(i):
            kids.append(D.text_el(measured[i], x=cx, y=py + PH + 88, w=PW, h=18,
                                  size=12, color="#B45309FF"))

    # ---- 底部结论与数据来源
    kids.append(D.hline(48, 1392, 940, "#CBD5E1FF", 1))
    kids.append(D.box(48, 956, 5, 96, color="#F6B94AFF"))
    kids.append(D.text_el("读图结论", x=66, y=954, w=200, h=24, size=18,
                          color="#0F172AFF", style="BOLD"))
    kids.append(D.text_el(
        "① 与 ② 的重叠区取样差异最大：alpha 直接作用于每个像素，红层仍可透出；Opacity 先把整组离屏合成一层再统一压 0.5，红层已被蓝层完全覆盖。",
        x=66, y=982, w=880, h=20, size=13, color="#334155FF"))
    kids.append(D.text_el(
        "③ 与 ④ 用同一句 24 号文字做对照：BackdropFilter 只读取并模糊背后条纹，字与形状锐利；ImageFiltered 把子树整张模糊，字随条纹一起糊。",
        x=66, y=1004, w=880, h=20, size=13, color="#334155FF"))
    kids.append(D.text_el(
        "⑤ 与 ⑥ 显示 MULTIPLY 会给边界内的透明间隙上色：矩形边界按 ceil(3σ)=18px 外扩，再由 ClipOval 收缩为圆形，圆外条纹保持原色。",
        x=66, y=1026, w=880, h=20, size=13, color="#334155FF"))
    src = D.text_el("数据来源：全部像素取自本次 open-snapshot 服务真实响应的 PNG，"
                    "与本图同名 compositing-lab.snapshot 一一对应。",
                    x=976, y=1014, w=416, h=40, size=12, color="#64748BFF")
    kids.append(src)
    return D.snapshot([D.stack(kids, W, H)], W, H, bg="#F1F5F9FF")


def probe(name, dsl, w, h):
    r = snapkit.render(dsl, name + ".png", name + ".snapshot", final=False)
    print("PROBE", name, "ok=", r.get("ok"), r.get("status"), r.get("image"),
          r.get("error"))
    for wl in D.warnings():
        print("WARN", wl)
    return r


def measure_lines(png_path):
    """从真实响应 PNG 取样，生成写在图上的实测短句。"""
    import sample_a10 as SA
    cells = SA.analyse(png_path)
    exp1 = (128, 64, 191)
    exp2 = (128, 128, 255)
    a1 = tuple(cells["1"]["points"]["overlap"]["rgb"])
    a2 = tuple(cells["2"]["points"]["overlap"]["rgb"])
    return {
        0: "实测 (180,100)＝%s｜预期 %s" % (SA.hexs(a1), SA.hexs(exp1)),
        1: "实测 (180,100)＝%s｜预期 %s" % (SA.hexs(a2), SA.hexs(exp2)),
        2: "实测 卡内条纹落差 %d 级 vs 卡外 %d 级" % (
            cells["3"]["stats"]["card_stripe_delta"],
            cells["3"]["stats"]["out_stripe_delta"]),
        3: "实测 卡内条纹落差 %d 级 vs 卡外 %d 级" % (
            cells["4"]["stats"]["card_stripe_delta"],
            cells["4"]["stats"]["out_stripe_delta"]),
        4: "实测 滤色边界 %s" % cells["5"]["stats"]["tint_bbox"],
        5: "实测 圆外 (66,26)＝%s 未着色" % cells["6"]["points"]["square_corner"]["hex"],
    }


def main():
    S.start_task(TASK)
    drafts = os.path.join(TMP, "drafts")
    os.makedirs(drafts, exist_ok=True)
    # ---- 第一遍：无实测文字，用于取样
    dsl1 = board()
    with open(os.path.join(drafts, "v01.snapshot"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(dsl1)
    r1 = snapkit.render(dsl1, "board-pass1.png", "board-pass1.snapshot",
                        final=False)
    print("PASS1 ok=", r1.get("ok"), r1.get("status"), r1.get("error"))
    for wl in D.warnings():
        print("WARN", wl)
    if not r1.get("ok"):
        return
    meas = measure_lines(r1["image"])
    for k in sorted(meas):
        print("MEASURED[%d] %s" % (k, meas[k]))
    # ---- 第二遍：带上实测值，落到输出目录
    dsl2 = board(meas)
    with open(os.path.join(drafts, "v02.snapshot"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(dsl2)
    D.WARNINGS.clear()
    r2 = snapkit.render(dsl2, "compositing-lab.png", "compositing-lab.snapshot",
                        final=True)
    print("PASS2 ok=", r2.get("ok"), r2.get("status"), r2.get("image"),
          r2.get("bytes"), r2.get("error"))
    for wl in D.warnings():
        print("WARN", wl)
    # ---- 第二遍取样，确认加字没有改变任何实验区像素
    if r2.get("ok"):
        import sample_a10 as SA
        c1, c2 = SA.analyse(r1["image"]), SA.analyse(r2["image"])
        same = all(c1[k]["points"][p]["rgb"] == c2[k]["points"][p]["rgb"]
                   for k in c1 for p in c1[k]["points"])
        print("PASS2_SAMPLES_IDENTICAL_TO_PASS1 =", same)
        for k in c1:
            for p in c1[k]["points"]:
                if c1[k]["points"][p]["rgb"] != c2[k]["points"][p]["rgb"]:
                    print("  DIFF", k, p, c1[k]["points"][p]["rgb"],
                          c2[k]["points"][p]["rgb"])
        with open(os.path.join(TMP, "measured-lines.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(meas, fh, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "main"
    if cmd == "main":
        main()
    else:
        idx = {"p1": 0, "p2": 1, "p3": 2, "p4": 3, "p5": 4, "p6": 5}[cmd]
        dsl = D.snapshot([D.stack(PANEL_BUILDERS[idx](), PW, PH)], PW, PH,
                         bg="#F1F5F9FF")
        probe(cmd, dsl, PW, PH)