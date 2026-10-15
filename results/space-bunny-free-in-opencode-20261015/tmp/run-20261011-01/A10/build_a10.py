#!/usr/bin/env python
"""A10 透明合成与滤镜语义实验板 —— 1440×1100 六格实验板。

启动基准：总任务根 (suite_root)。本题无输入文件，参数全部来自 TASK.md。
局部坐标原点 = 对应 320×240 实验区左上外边界，x 向右、y 向下。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import snapkit as sk  # noqa: E402
from snapkit import C  # noqa: E402

TASK = "A10"
DRAFTS = f"tmp/run-20261011-01/{TASK}/drafts"

W, H = 1440, 1100
EXP_W, EXP_H = 320, 240          # 实验区尺寸（题面固定）
CELL_W, CELL_CAP_H = 416, 88     # 格宽 = 说明带 + 居中的实验区
COL_X = [56, 512, 968]           # 56 + 416 + 40 + 416 + 40 + 416 + 56 = 1440（格距 40 ≥ 32）
ROW_TOP = [96, 458]              # 两行格顶
EXP_DX = (CELL_W - EXP_W) // 2   # 实验区在格内水平居中的偏移 = 48
FOOTER = (56, 830, 1328, 262)    # 页脚面板 (x, y, w, h)

# 题面固定的 ①② 矩形
RECT_RED = (40, 40, 160, 120)
RECT_BLUE = (120, 80, 160, 120)
SAMPLE_LOCAL = (180, 100)
ALPHA_50_CSS = "#FF000080"       # 8 位 = 0x80 = 128 → 128/255
ALPHA_50_NUM = 128 / 255
GROUP_OPACITY = 0.5
FILTER_COLOR = "#F6B94A"

# ③④ 共用的条纹面板与卡片（面板坐在实验区白底上，上下各留 20px 白边）
STRIPE_W = 16
STRIPE_A, STRIPE_B = "#1E293B", "#F1F5F9"
STRIPE_PANEL = (0, 20, 320, 200)
CARD_W, CARD_H, CARD_R, CARD_DX, CARD_DY = 240, 160, 20, 40, 40
CARD_TEXT = "SHARP / BLUR"
CARD_TEXT_SIZE = 24
SIGMA = 6

# ⑤⑥ 共用的场景框：200×200 置于实验区局部 (60,20)，其内接圆即圆心 (160,120) 半径 100
SCENE_W, SCENE_H, SCENE_DX, SCENE_DY = 200, 200, 60, 20
CIRCLE_CENTER, CIRCLE_R = (160, 120), 100

CAPTIONS = [
    ("① 两个矩形各设 50% alpha", "红 #FF000080 压白底，再叠蓝 #0000FF80（各 128/255）"),
    ("② 同样两块放进 Opacity(0.5) 组", "组内红蓝均不透明，只有一次整体透明 0.5"),
    ("③ 仅背景模糊", "BackdropFilter sigma=6 只模糊卡内背景；文字与前景保持清晰"),
    ("④ 整棵子树模糊", "ImageFiltered sigma=6 模糊卡的整棵子树：背景 + 文字 + 前景"),
    ("⑤ 先滤色再模糊", "ColorFiltered(#F6B94A,MULTIPLY) → 子树高斯模糊 sigma=6"),
    ("⑥ 同样效果 + 圆形裁剪", "同一内容再加 ClipOval：圆心 (160,120)、半径 100，圆外不绘制"),
]


def exp_origin(idx: int):
    """第 idx 格（0..5）实验区在画布上的左上角。"""
    c, r = idx % 3, idx // 3
    return COL_X[c] + EXP_DX, ROW_TOP[r] + CELL_CAP_H


def cell_origin(idx: int):
    c, r = idx % 3, idx // 3
    return COL_X[c], ROW_TOP[r]


# ---------------------------------------------------------------- 共享场景
def dash_seg(x1, y1, x2, y2, wdt, color, dash=7.0, gap=5.0):
    """由均匀短胶囊拼出的虚线段（解析器无 borderStyle: DASH）。"""
    import math
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 0.01:
        return ""
    ux, uy = dx / L, dy / L
    ang = math.degrees(math.atan2(dy, dx))
    out, t = [], 0.0
    while t < L:
        e = min(t + dash, L)
        cx, cy = (x1 + ux * t + x1 + ux * e) / 2, (y1 + uy * t + y1 + uy * e) / 2
        bw = (e - t) + wdt
        out.append(f'<Positioned left="{round(cx - bw / 2, 2)}" top="{round(cy - wdt / 2, 2)}" '
                   f'width="{round(bw, 2)}" height="{wdt}">'
                   f'<Transform matrix="{sk.rot_matrix(ang)}" alignment="CENTER">'
                   f'<Container width="{round(bw, 2)}" height="{wdt}" color="{color}" '
                   f'borderRadius="{round(wdt / 2, 2)}"/></Transform></Positioned>')
        t = e + gap
    return "".join(out)


def dashed_line(x1, y1, x2, y2, wdt, color):
    return dash_seg(x1, y1, x2, y2, wdt, color)


def dashed_circle(cx, cy, r, wdt, color, n=64, dash_deg=4.6, gap_deg=2.4):
    import math
    out = []
    k = 0
    while k < n:
        a0 = 360.0 * k / n
        a1 = a0 + dash_deg
        out.append(dash_seg(cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0)),
                            cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1)),
                            wdt, color, dash=999, gap=0))
        k += 1
    return "".join(out)


def stripes_scene() -> str:
    """③④ 共用的未加效果基础场景：白底实验区 + 锐利竖条纹面板（上下留 20px 白边）。"""
    px, py, pw, ph = STRIPE_PANEL
    parts = []
    x = 0
    k = 0
    while x < pw:
        w = min(STRIPE_W, pw - x)
        parts.append(f'<Positioned left="{x}" top="0" width="{w}" height="{ph}">'
                     f'<Container width="{w}" height="{ph}" '
                     f'color="{STRIPE_A if k % 2 == 0 else STRIPE_B}"/></Positioned>')
        x += w
        k += 1
    return (f'<Positioned left="{px}" top="{py}" width="{pw}" height="{ph}">'
            f'<Container width="{pw}" height="{ph}" color="{STRIPE_A}">'
            f'<Stack fit="EXPAND">{"".join(parts)}</Stack></Container></Positioned>')


def card_foreground() -> str:
    """③④ 共用的卡片前景：文字 + 两个前景形状（层次与位置完全一致）。"""
    return (
        f'<Positioned left="24" top="22" width="192" height="34">'
        f'<Text fontSize="{CARD_TEXT_SIZE}" color="#0F172A" fontFamily="{sk.F_LATIN_SB}">'
        f'{sk.esc(CARD_TEXT)}</Text></Positioned>'
        f'<Positioned left="24" top="96" width="96" height="46">'
        f'<Container width="96" height="46" color="#0F172A" borderRadius="8"/></Positioned>'
        f'<Positioned left="136" top="96" width="80" height="46">'
        f'<Container width="80" height="46" color="#DC2626" borderRadius="8"/></Positioned>'
    )


def experiment_3() -> str:
    """③ 仅背景模糊：ClipRRect 内先 BackdropFilter，再叠清晰文字/前景。"""
    return (
        f'<Container width="{EXP_W}" height="{EXP_H}" color="#FFFFFF">'
        f'<Stack fit="EXPAND">{stripes_scene()}'
        f'<Positioned left="{CARD_DX}" top="{CARD_DY}" width="{CARD_W}" height="{CARD_H}">'
        f'<ClipRRect borderRadius="{CARD_R}" clipBehavior="ANTI_ALIAS">'
        f'<Container width="{CARD_W}" height="{CARD_H}"><Stack fit="EXPAND">'
        f'<BackdropFilter sigmaX="{SIGMA}" sigmaY="{SIGMA}">'
        f'<Container width="{CARD_W}" height="{CARD_H}" color="#FFFFFF33"/></BackdropFilter>'
        f'{card_foreground()}'
        f'</Stack></Container></ClipRRect></Positioned>'
        f'</Stack></Container>'
    )


def experiment_4() -> str:
    """④ 整棵子树模糊：同一张卡，包一层 ImageFiltered，不加 BackdropFilter。"""
    return (
        f'<Container width="{EXP_W}" height="{EXP_H}" color="#FFFFFF">'
        f'<Stack fit="EXPAND">{stripes_scene()}'
        f'<Positioned left="{CARD_DX}" top="{CARD_DY}" width="{CARD_W}" height="{CARD_H}">'
        f'<ClipRRect borderRadius="{CARD_R}" clipBehavior="ANTI_ALIAS">'
        f'<ImageFiltered sigmaX="{SIGMA}" sigmaY="{SIGMA}">'
        f'<Container width="{CARD_W}" height="{CARD_H}"><Stack fit="EXPAND">'
        f'<Container width="{CARD_W}" height="{CARD_H}" color="#FFFFFF33"/>'
        f'{card_foreground()}'
        f'</Stack></Container></ImageFiltered></ClipRRect></Positioned>'
        f'</Stack></Container>'
    )


# ---------------------------------------------------------------- ⑤⑥ 共享场景
def scene_56_core() -> str:
    """⑤⑥ 共用内容：竖条 + 透明竖隙 + 深色矩形(含阴影) + 透明横隙 + 琥珀块 + 红圆。"""
    parts = [
        # 左竖条（跨过圆周左上与左下）
        f'<Positioned left="0" top="0" width="56" height="{SCENE_H}">'
        f'<Container width="56" height="{SCENE_H}" color="#0EA5E9"/></Positioned>',
        # 右上深色矩形 + 阴影
        f'<Positioned left="96" top="0" width="104" height="74">'
        f'<Container width="104" height="74" color="#1F2937" '
        f'boxShadow="0 6 14 2 #00000059 NORMAL"/></Positioned>',
        # 右下琥珀块（跨过圆周右下）
        f'<Positioned left="96" top="118" width="104" height="82">'
        f'<Container width="104" height="82" color="#F59E0B"/></Positioned>',
        # 红圆（圆心 (128,158) r=44，右下部分跨出圆周）
        f'<Positioned left="84" top="114" width="88" height="88">'
        f'<ClipOval><Container width="88" height="88" color="#DC2626"/></ClipOval></Positioned>',
    ]
    inner = f'<Container width="{SCENE_W}" height="{SCENE_H}"><Stack fit="EXPAND">{"".join(parts)}</Stack></Container>'
    # 先 ColorFiltered(MULTIPLY)，再对结果做子树高斯模糊
    return (f'<ColorFiltered color="{FILTER_COLOR}" blendMode="MULTIPLY">{inner}</ColorFiltered>')


def scene_guides() -> str:
    """⑤⑥ 完全相同的参考线：场景框虚线 + 圆心 (160,120) 半径 100 的虚线圆。

    参考线画在滤镜子树**之外**、两格参数一致，因此不破坏「唯一变化项 = ClipOval」的对照。
    """
    x0, y0 = SCENE_DX, SCENE_DY
    x1, y1 = SCENE_DX + SCENE_W, SCENE_DY + SCENE_H
    rect = "".join([
        dashed_line(x0, y0, x1, y0, 1.6, "#33415580"),
        dashed_line(x1, y0, x1, y1, 1.6, "#33415580"),
        dashed_line(x1, y1, x0, y1, 1.6, "#33415580"),
        dashed_line(x0, y1, x0, y0, 1.6, "#33415580"),
    ])
    return rect + dashed_circle(CIRCLE_CENTER[0], CIRCLE_CENTER[1], CIRCLE_R, 1.6, "#0F172A9C")


def experiment_5() -> str:
    """⑤ 不加裁剪。"""
    return (
        f'<Container width="{EXP_W}" height="{EXP_H}" color="#FFFFFF"><Stack fit="EXPAND">'
        f'<Positioned left="{SCENE_DX}" top="{SCENE_DY}" width="{SCENE_W}" height="{SCENE_H}">'
        f'<ImageFiltered sigmaX="{SIGMA}" sigmaY="{SIGMA}">{scene_56_core()}</ImageFiltered>'
        f'</Positioned>'
        f'{scene_guides()}'
        f'</Stack></Container>'
    )


def experiment_6() -> str:
    """⑥ 同样内容与参数，最外层加 ClipOval（圆心 (160,120) 半径 100）。"""
    return (
        f'<Container width="{EXP_W}" height="{EXP_H}" color="#FFFFFF"><Stack fit="EXPAND">'
        f'<Positioned left="{SCENE_DX}" top="{SCENE_DY}" width="{SCENE_W}" height="{SCENE_H}">'
        f'<ClipOval clipBehavior="ANTI_ALIAS">'
        f'<ImageFiltered sigmaX="{SIGMA}" sigmaY="{SIGMA}">{scene_56_core()}</ImageFiltered>'
        f'</ClipOval></Positioned>'
        f'{scene_guides()}'
        f'</Stack></Container>'
    )


# ---------------------------------------------------------------- ①②
def experiment_1() -> str:
    rx, ry, rw, rh = RECT_RED
    bx, by, bw, bh = RECT_BLUE
    return (
        f'<Container width="{EXP_W}" height="{EXP_H}" color="#FFFFFF"><Stack fit="EXPAND">'
        f'<Positioned left="{rx}" top="{ry}" width="{rw}" height="{rh}">'
        f'<Container width="{rw}" height="{rh}" color="{ALPHA_50_CSS}"/></Positioned>'
        f'<Positioned left="{bx}" top="{by}" width="{bw}" height="{bh}">'
        f'<Container width="{bw}" height="{bh}" color="#0000FF80"/></Positioned>'
        + sample_ring()
        + f'</Stack></Container>'
    )


def experiment_2() -> str:
    rx, ry, rw, rh = RECT_RED
    bx, by, bw, bh = RECT_BLUE
    return (
        f'<Container width="{EXP_W}" height="{EXP_H}" color="#FFFFFF">'
        f'<Opacity opacity="{GROUP_OPACITY}">'
        f'<Container width="{EXP_W}" height="{EXP_H}"><Stack fit="EXPAND">'
        f'<Positioned left="{rx}" top="{ry}" width="{rw}" height="{rh}">'
        f'<Container width="{rw}" height="{rh}" color="#FF0000"/></Positioned>'
        f'<Positioned left="{bx}" top="{by}" width="{bw}" height="{bh}">'
        f'<Container width="{bw}" height="{bh}" color="#0000FF"/></Positioned>'
        + sample_ring()
        + f'</Stack></Container></Opacity></Container>'
    )


def sample_ring() -> str:
    """采样点标记：圆心 = 实验区局部 (180,100) 的虚线圆，半径 17。

    用「虚线圆」而不是实心/带内孔的圆，是为了让标记**完全不覆盖**被采样的那个像素：
    标记的所有笔画都在半径 ≥16 处，(180,100) 本像素始终保持纯合成结果。
    """
    return dashed_circle(SAMPLE_LOCAL[0], SAMPLE_LOCAL[1], 17, 2.0, "#0F172A",
                         n=24, dash_deg=8.0, gap_deg=7.0)


EXPERIMENTS = [experiment_1, experiment_2, experiment_3, experiment_4, experiment_5, experiment_6]


# ---------------------------------------------------------------- 页脚
def footer(m: dict) -> str:
    """页脚：①② 采样核对表 + ③④⑤⑥ 视觉判断（数值由 sample_a10.py 写回 audit 后回填）。"""
    P = []
    A = P.append
    FX, FY, FW, FH = FOOTER
    A(f'<Positioned left="{FX}" top="{FY}" width="{FW}" height="{FH}">'
      f'<Container width="{FW}" height="{FH}" color="#FFFFFF" borderRadius="14" '
      f'border="1.5 SOLID #CBD5E1"/></Positioned>')

    tx = FX + 20
    tw = FW - 40
    A(sk.text("①② 重叠内部采样核对：实验区局部 (180,100) → PNG 像素 (origin_x+180, origin_y+100)，"
              "sRGB 8 位未预乘，alpha=255",
              size=20, color=C.SLATE, family=sk.F_HEAD, left=tx, top=842, width=tw, height=26))

    cols = [(0, 60), (68, 290), (366, 175), (549, 200), (757, 170), (935, 90), (1033, 235)]
    heads = ["实验", "理论浮点 RGB（source-over）", "floor(v+0.5) 取整", "实测 RGB（最终图）",
             "逐通道 |Δ|", "判定", "关键差异"]
    A(f'<Positioned left="{tx}" top="872" width="1276" height="26">'
      f'<Container width="1276" height="26" color="#EFF6FF" borderRadius="6"/></Positioned>')
    for (cx, cwd), htxt in zip(cols, heads):
        A(sk.text(htxt, size=20, color=C.SLATE, family=sk.F_HEAD,
                  left=tx + cx, top=872, width=cwd, height=26))
    for k, row in enumerate(m["rows"]):
        ry = 898 + k * 26
        A(f'<Positioned left="{tx}" top="{ry}" width="1276" height="26">'
          f'<Container width="1276" height="26" '
          f'color="{"#F8FAFC" if k % 2 else "#FFFFFF"}"/></Positioned>')
        vals = [row.get("tag", "?"), row.get("theoretical_float", "—"),
                row.get("rounded", "—"), row.get("measured", "待采样"),
                row.get("abs_error", "待采样"), row.get("verdict", "待采样"),
                row.get("note", "")]
        for (cx, cwd), v in zip(cols, vals):
            A(sk.text(v, size=20, color=C.INK2, family=sk.F_BODY,
                      left=tx + cx, top=ry, width=cwd, height=26))

    A(sk.text("③④⑤⑥ 视觉判断（依据最终图整屏与 2× 放大局部实际观察，不是标签推断）",
              size=20, color=C.SLATE, family=sk.F_HEAD, left=tx, top=960, width=tw, height=26))
    for k, line in enumerate(m["judgments"]):
        A(sk.text(line, size=20, color=C.INK2, family=sk.F_BODY,
                  left=tx, top=990 + k * 24, width=tw, height=23))
    return "".join(P)


# ---------------------------------------------------------------- 期望值（解析计算）
def theoretical_rgb(mode: str):
    """返回 (理论浮点 RGB, 取整 RGB)。全部按题面规定用 0–255 的 sRGB 通道值计算。"""
    if mode == "per_layer_alpha":
        a = ALPHA_50_NUM
        white = 255.0
        # 红 #FF0000 @ a 压白底
        r1 = 255.0 * a + white * (1 - a)
        g1 = 0.0 * a + white * (1 - a)
        b1 = g1
        # 蓝 #0000FF @ a 压在 (r1,g1,b1) 上
        r2 = 0.0 * a + r1 * (1 - a)
        g2 = 0.0 * a + g1 * (1 - a)
        b2 = 255.0 * a + b1 * (1 - a)
        return (r2, g2, b2)
    # group_opacity：组内红蓝不透明，重叠处只剩纯蓝，再整体乘一次 0.5 压白底
    a = GROUP_OPACITY
    return (0.0 * a + 255.0 * (1 - a), 0.0 * a + 255.0 * (1 - a), 255.0 * a + 255.0 * (1 - a))


def fmt_rgb(t):
    return " / ".join(f"{v:.2f}" for v in t)


def fmt_rgb_int(t):
    return " / ".join(str(int(v + 0.5)) for v in t)


# ---------------------------------------------------------------- 建图
def build(measured: dict) -> str:
    P = []
    A = P.append
    A(f'<Container width="{W}" height="{H}" color="#F5F8FC"><Stack fit="EXPAND">')

    # 页眉
    A(sk.text("看到差异，才能说用对了", size=38, color=C.INK, family=sk.F_HEAD,
              left=56, top=14, width=700, height=48))
    A(sk.text("透明合成与滤镜语义实验板 · 实验区 320×240 白底 · 3 列 × 2 行 · 格距 40（≥32）"
              " · 编号与说明在实验区之外 · ①② 重叠内部取样 (180,100)",
              size=20, color=C.MUTED, family=sk.F_BODY, left=56, top=58, width=1328, height=26))

    for i, fn in enumerate(EXPERIMENTS):
        cx, cy = cell_origin(i)
        ox, oy = exp_origin(i)
        # 说明带（格内、实验区之外）
        A(f'<Positioned left="{cx}" top="{cy}" width="{CELL_W}" height="84">'
          f'<Container width="{CELL_W}" height="84" color="#FFFFFF" borderRadius="12" '
          f'border="1.5 SOLID #CBD5E1"><Stack fit="EXPAND">'
          f'<Positioned left="16" top="8" width="{CELL_W - 32}" height="28">'
          f'<Text fontSize="24" color="#1E293B" fontFamily="{sk.F_HEAD}">'
          f'{sk.esc(CAPTIONS[i][0])}</Text></Positioned>'
          f'<Positioned left="16" top="38" width="{CELL_W - 32}" height="46">'
          f'{sk.wrapped(CELL_W - 32, CAPTIONS[i][1], size=20, color=C.MUTED, line_height=1.25)}'
          f'</Positioned></Stack></Container></Positioned>')
        # 实验区（白底 320×240）
        A(f'<Positioned left="{ox}" top="{oy}" width="{EXP_W}" height="{EXP_H}">'
          f'<Container width="{EXP_W}" height="{EXP_H}" color="#FFFFFF">'
          f'<Stack fit="EXPAND">{fn()}</Stack></Container></Positioned>')
        # 实验区边框 + 局部坐标注记（画在区外）
        A(f'<Positioned left="{ox - 1}" top="{oy - 1}" width="{EXP_W + 2}" height="{EXP_H + 2}">'
          f'<Container width="{EXP_W + 2}" height="{EXP_H + 2}" color="#FFFFFF00" '
          f'border="1.5 SOLID #94A3B8" borderRadius="4"/></Positioned>')
        A(sk.text(f"实验区 {EXP_W}×{EXP_H} · 原点 ({ox},{oy})", size=20, color=C.FAINT,
                  family=sk.F_BODY, align="RIGHT", left=ox - 96, top=oy + EXP_H + 3,
                  width=EXP_W + 96, height=22))

    A(footer(measured))
    A("</Stack></Container>")
    return f'<Snapshot type="png">\n{"".join(P)}\n</Snapshot>\n'


def main() -> None:
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    base = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    rows, judgments = [], []
    meas = base / f"{DRAFTS}/sample-measured.json"
    if meas.exists():
        rows = json.loads(meas.read_text(encoding="utf-8")).get("rows", [])
    jd = base / f"{DRAFTS}/judgments.json"
    if jd.exists():
        judgments = json.loads(jd.read_text(encoding="utf-8"))

    if not rows:                       # 首版：先用理论值占位，实测回填
        for tag, mode in (("①", "per_layer_alpha"), ("②", "group_opacity")):
            t = theoretical_rgb(mode)
            rows.append({"tag": tag, "theoretical_float": fmt_rgb(t), "rounded": fmt_rgb_int(t),
                         "measured": "待采样", "abs_error": "待采样", "verdict": "待采样",
                         "note": "红层被蓝层二次透射" if tag == "①" else "仅一次整体 0.5"})
    if len(judgments) != 4:
        judgments = ["③ 待填写（实际打开渲染结果后据实填写）"] * 4

    d = base / DRAFTS
    d.mkdir(parents=True, exist_ok=True)
    dsl = build({"rows": rows, "judgments": judgments})
    (d / f"a10-{ver}.snapshot").write_text(dsl, encoding="utf-8")
    print("dsl bytes:", len(dsl.encode()))
    for i in range(6):
        print("exp", i + 1, "origin", exp_origin(i))


if __name__ == "__main__":
    main()