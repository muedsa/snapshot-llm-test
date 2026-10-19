# -*- coding: utf-8 -*-
"""A23 · probe（旋转/透明验证）+ 6 透明关键帧 + 1200×800 封面 + 几何底稿。

单元：U01–U08 风车矩形叶（4 色×2，60×190，圆角 16，终态 r=165、径向角 −90+45i°，
rotation=径向角−90°）；U09–U12 内心圆点（4 色，d=54，r=88，角 −90+90i°，rotation 恒 0）。
t=0 分散：叶 r0=195、圆点 r0=268，角度 −90+30i+jitter，叶 rotation 终态±jitter_θ。
缓动：ease-in-out cubic，u=t/1500，f(u)=4u³ (u≤0.5) / 1−(−2u+2)³/2 (u>0.5)，
帧 f = [0, 1/54, 4/27, 1/2, 23/27, 53/54]。位置/角度未舍入值进 DSL 与 JSON 底稿。
"""
import json
import math
import os
from pathlib import Path

TASK_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
OUT = TASK_ROOT / "outputs" / RUN / "A23"
TMP = TASK_ROOT / "tmp" / RUN / "A23"
OUT.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)

CYAN, AMBER, GREEN, RED = "#4CC2FF", "#FFC154", "#3FD9A4", "#FF8A80"
PAL = [CYAN, AMBER, GREEN, RED]
TXT, SUB, MUT = "#EAF3FF", "#A9BFDF", "#8FA8CE"
PANEL = "#12203A"
BG = "#0B1526"

W = H = 600.0
CX = CY = 300.0
LEAF_W, LEAF_H = 60.0, 160.0
LEAF_R = 165.0
DOT_D = 54.0
DOT_R = 48.0
LEAF_R0 = 195.0
DOT_R0 = 268.0

J_P = [0.0, 8.0, -6.0, 4.0, -9.0, 6.0, -4.0, 8.0, -7.0, 5.0, -6.0, 4.0]
J_T = [75.0, -58.0, 90.0, -84.0, 62.0, -70.0, 88.0, -95.0]

UNITS = []
for i in range(8):
    UNITS.append({"id": f"U{i + 1:02d}", "type": "rect", "w": LEAF_W, "h": LEAF_H,
                  "color": PAL[i % 4], "rgb": [], "alpha": 1.0,
                  "role": "blade", "border_radius": 16.0})
for i in range(4):
    UNITS.append({"id": f"U{i + 9:02d}", "type": "circle", "w": DOT_D, "h": DOT_D,
                  "color": PAL[(i + 2) % 4], "rgb": [], "alpha": 1.0,
                  "role": "core-dot", "border_radius": 0.0})
for u in UNITS:
    c = u["color"].lstrip("#")
    u["rgb"] = [int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)]

for i, u in enumerate(UNITS):
    if u["role"] == "blade":
        a1 = -90.0 + 45.0 * i
        u["end"] = {"x": CX + LEAF_R * math.cos(math.radians(a1)),
                    "y": CY + LEAF_R * math.sin(math.radians(a1)),
                    "rot": a1 - 90.0}
        a0 = -90.0 + 30.0 * i + J_P[i]
        u["start"] = {"x": CX + LEAF_R0 * math.cos(math.radians(a0)),
                      "y": CY + LEAF_R0 * math.sin(math.radians(a0)),
                      "rot": u["end"]["rot"] + J_T[i]}
    else:
        a1 = -67.5 + 90.0 * (i - 8)
        u["end"] = {"x": CX + DOT_R * math.cos(math.radians(a1)),
                    "y": CY + DOT_R * math.sin(math.radians(a1)), "rot": 0.0}
        a0 = (-135.0 + 90.0 * (i - 8)) + (J_P[i] % 12.0) - 6.0
        u["start"] = {"x": CX + DOT_R0 * math.cos(math.radians(a0)),
                      "y": CY + DOT_R0 * math.sin(math.radians(a0)), "rot": 0.0}


def ease(u):
    if u <= 0.5:
        return 4 * u ** 3
    return 1 - ((-2 * u + 2) ** 3) / 2


U = [k / 6.0 for k in range(6)]
F = [ease(u) for u in U]
print("ease table:", [f"{v:.6f}" for v in F])


def frame_state(k):
    """k=0..5 → 逐单元 {'x','y','rot'(deg)} 未舍入。"""
    f = F[k]
    st = []
    for u in UNITS:
        x0, y0, r0 = u["start"]["x"], u["start"]["y"], u["start"]["rot"]
        x1, y1, r1 = u["end"]["x"], u["end"]["y"], u["end"]["rot"]
        st.append({"id": u["id"],
                   "x": x0 + (x1 - x0) * f, "y": y0 + (y1 - y0) * f,
                   "rot": r1 + (r0 - r1) * (1 - f)})
    return st


def fnum(v):
    s = f"{float(v):.6f}".rstrip("0").rstrip(".")
    return s if s else "0"


def rot_matrix(deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return (f"({fnum(c)},{fnum(s)},0,0,{fnum(-s)},{fnum(c)},0,0,0,0,1,0,"
            f"0,0,0,1)")


def unit_node(u, x, y, rot):
    w, h = u["w"], u["h"]
    lx, ty = x - w / 2, y - h / 2
    shape = ' shape="CIRCLE"' if u["type"] == "circle" else ""
    rad = ""
    if u.get("border_radius"):
        rad = f' borderRadius="{fnum(u["border_radius"])}"'
    inner = (f'<Container width="{fnum(w)}" height="{fnum(h)}"{shape} '
             f'color="{u["color"]}"{rad} />')
    if abs(rot) > 1e-9:
        inner = (f'<Transform matrix="{rot_matrix(rot)}" '
                 f'origin="({fnum(w / 2)},{fnum(h / 2)})">{inner}</Transform>')
    return (f'<Positioned left="{fnum(lx)}" top="{fnum(ty)}" '
            f'width="{fnum(w)}" height="{fnum(h)}">{inner}</Positioned>')


def frame_dsl(state):
    body = "\n".join(unit_node(u, s["x"], s["y"], s["rot"])
                     for u, s in zip(UNITS, state))
    return ('<Snapshot type="png">\n<Stack>\n'
            f'<SizedBox width="600" height="600" />\n{body}\n</Stack>\n</Snapshot>\n')


# —— 6 帧（透明：不设 background） ——
for k in range(6):
    (OUT / f"frame-{k + 1:02d}.snapshot").write_text(
        frame_dsl(frame_state(k)), encoding="utf-8")

# —— 封面 1200×800（RGB 深底；右半汇聚大图 scale 1.12） ——
SC = 1.12
S = ['<SizedBox width="1200" height="800" />']
S.append(f'<Container width="1200" height="800" color="{BG}" />')
# 右半大图（终态 12 单元 1.12×）
for u in UNITS:
    x, y, r = u["end"]["x"], u["end"]["y"], u["end"]["rot"]
    dx, dy = 900.0 - CX, 400.0 - CY
    x, y = CX + (x - CX) * SC + dx, CY + (y - CY) * SC + dy
    w, h = u["w"] * SC, u["h"] * SC
    lx, ty = x - w / 2, y - h / 2
    shape = ' shape="CIRCLE"' if u["type"] == "circle" else ""
    rad = f' borderRadius="{fnum(u["border_radius"] * SC)}"' if u.get("border_radius") else ""
    inner = (f'<Container width="{fnum(w)}" height="{fnum(h)}"{shape} '
             f'color="{u["color"]}"{rad} />')
    if abs(r) > 1e-9:
        inner = (f'<Transform matrix="{rot_matrix(r)}" '
                 f'origin="({fnum(w / 2)},{fnum(h / 2)})">{inner}</Transform>')
    S.append(f'<Positioned left="{fnum(lx)}" top="{fnum(ty)}" '
             f'width="{fnum(w)}" height="{fnum(h)}">{inner}</Positioned>')
# 左侧文字区
S.append(f'<Positioned left="60" top="104"><Text fontSize="30" color="{SUB}"'
         f' fontFamily="Noto Sans CJK SC">SNAPSHOT · 结构汇聚成图像分镜单</Text></Positioned>')
S.append(f'<Positioned left="60" top="156"><Text fontSize="52" color="{TXT}"'
         f' fontFamily="Noto Sans CJK SC" fontStyle="BOLD">从结构到画面</Text></Positioned>')
S.append(f'<Positioned left="60" top="238" width="470"><Text fontSize="22"'
         f' color="{SUB}" fontFamily="Noto Sans CJK SC">12 个几何单元由四周分散，'
         f'经 6 帧缓动逐步汇聚为 8 叶放射花 + 4 点内心。</Text></Positioned>')
kpis = [("6", "关键帧"), ("250ms", "帧间隔"), ("1500ms", "循环周期"), ("12", "几何单元")]
for i, (v, lab) in enumerate(kpis):
    x, y = 60 + (i % 2) * 240, 330 + (i // 2) * 118
    S.append(f'<Positioned left="{x}" top="{y}" width="210" height="94">'
             f'<Container width="210" height="94" color="{PANEL}"'
             f' border="1 SOLID #23375C" borderRadius="12" /></Positioned>')
    S.append(f'<Positioned left="{x}" top="{y}"><Text fontSize="30" color="{TXT}"'
             f' fontFamily="Inter" fontStyle="BOLD">{v}</Text></Positioned>')
    S.append(f'<Positioned left="{x}" top="{y + 52}"><Text fontSize="22"'
             f' color="{MUT}" fontFamily="Noto Sans CJK SC">{lab}</Text></Positioned>')
S.append(f'<Positioned left="60" top="602" width="500"><Text fontSize="22"'
         f' color="{SUB}" fontFamily="Noto Sans CJK SC">插值：分段 ease-in-out cubic，'
         f'位置 p(t)=p0+(p1-p0)·f(u)；仅旋转叶（U01–U08）参与旋转归位。</Text></Positioned>')
S.append(f'<Positioned left="60" top="662" width="500"><Text fontSize="22"'
         f' color="{MUT}" fontFamily="Noto Sans CJK SC">6 × 600×600 透明 PNG 关键帧'
         f' + timing.json；SVG 文字 / CMYK / GIF 的替代口径见 limitations.md。</Text></Positioned>')
cover = ('<Snapshot background="' + BG + '" type="png">\n<Stack>\n'
         + "\n".join(S) + "\n</Stack>\n</Snapshot>\n")
(OUT / "cover.snapshot").write_text(cover, encoding="utf-8")

# —— probe（tmp）：4 旋转矩形验证方向与 pivot ——
PR = [
    (120, 120, 0.0, CYAN), (420, 120, 90.0, AMBER),
    (300, 450, 30.0, GREEN), (480, 450, 180.0, RED),
]
PU = {"id": "P", "type": "rect", "w": LEAF_W, "h": LEAF_H, "color": "",
      "border_radius": 8.0}
pb = ['<SizedBox width="600" height="600" />']
for x, y, r, col in PR:
    u = dict(PR[0] and PU, color=col)
    pb.append(unit_node(u, x, y, r))
probe = '<Snapshot type="png">\n<Stack>\n' + "\n".join(pb) + '\n</Stack>\n</Snapshot>\n'
(TMP / "probe.snapshot").write_text(probe, encoding="utf-8")

# —— 几何底稿（frame-data 前体；交付层 finalize 时落盘） ——
frames_json = []
for k in range(6):
    st = frame_state(k)
    frames_json.append({
        "id": f"F{k + 1}", "t_ms": k * 250, "easing_progress": F[k],
        "image": f"frame-{k + 1:02d}.png", "dsl": f"frame-{k + 1:02d}.snapshot",
        "units": [{"id": s["id"], "x": round(s["x"], 6), "y": round(s["y"], 6),
                   "w": UNITS[i]["w"], "h": UNITS[i]["h"],
                   "rotation_deg": round(s["rot"], 6), "visible": True,
                   "alpha": UNITS[i]["alpha"], "color": UNITS[i]["color"]}
                  for i, s in enumerate(st)]})
(TMP / "geometry.json").write_text(json.dumps(
    {"units": UNITS, "frames": frames_json,
     "ease_times": [round(v, 9) for v in F], "u": U}, ensure_ascii=False,
    indent=1), encoding="utf-8")
print("frames+cover+probe written; units", len(UNITS))
