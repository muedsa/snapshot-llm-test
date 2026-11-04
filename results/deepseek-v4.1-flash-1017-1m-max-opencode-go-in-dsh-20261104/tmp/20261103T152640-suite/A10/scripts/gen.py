# -*- coding: utf-8 -*-
"""A10 v2: six-cell compositing lab (1440x1100) + audit."""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A10"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)
clock = rep.TaskClock(TASK)

BG = "#ECF0F6"
CARD = "#FFFFFF"
INK = "#0F172A"
INK2 = "#475569"
MUTED = "#7B8BA0"
AREAS = [(208, 160), (560, 160), (912, 160), (208, 500), (560, 500), (912, 500)]
AW, AH = 320, 240
W, H = 1440, 1100

p: list[str] = []
p.append(K.rect(0, 0, W, 6, color="#E11D48"))
p.append(K.text(208, 24, "看到差异，才能说用对了", size=40, color=INK, bold=True))
p.append(K.text(208, 76, "六个 320×240 实验区：①②对比 alpha 的两种写法，③④对比模糊作用层，⑤⑥对比滤镜与裁剪范围。",
                width=1030, size=20, color=INK2))
p.append(K.text(208, 104, "局部坐标以各区左上角为原点；像素采样点 (180,100) 与合成结果见底部与 composite-audit.json。",
                width=1030, size=19, color=MUTED))

STRIPES = ["#E11D48", "#F59E0B", "#0EA5E9"]
def stripe_block(w, h, x0=0, y0=0):
    out, x, i = [], x0 - 8, 0
    while x < x0 + w:
        out.append(K.rect(x, y0, 16, h, color=STRIPES[i % 3]))
        x += 26
        i += 1
    return "".join(out)

def area_frame(ax, ay):
    p.append(K.rect(ax, ay, AW, AH, color=CARD, radius=4, border="1 SOLID #CBD5E1"))

def caption(ax, ay, num, title, l1, l2):
    p.append(K.text(ax, ay + AH + 12, f"{num}  {title}", width=AW, size=21, color=INK, bold=True))
    p.append(K.text(ax, ay + AH + 42, l1, width=AW, size=17, color=INK2))
    p.append(K.text(ax, ay + AH + 66, l2, width=AW, size=17, color=MUTED))

# ---------------------------------------------------------------- ① ②
for idx, (ax, ay) in enumerate(AREAS[:2], start=1):
    area_frame(ax, ay)
    if idx == 1:
        body = (K.rect(40, 40, 160, 120, color="#FF000080")
                + K.rect(120, 80, 160, 120, color="#0000FF80"))
    else:
        body = (f'<Positioned left="0" top="0"><Opacity opacity="0.5">'
                f'<SizedBox width="{AW}" height="{AH}"><Stack alignment="TOP_LEFT">'
                + K.rect(40, 40, 160, 120, color="#FF0000")
                + K.rect(120, 80, 160, 120, color="#0000FF")
                + '</Stack></SizedBox></Opacity></Positioned>')
    p.append(f'<Positioned left="{ax}" top="{ay}"><SizedBox width="{AW}" height="{AH}">'
             f'<Stack alignment="TOP_LEFT" clipBehavior="HARD_EDGE">{body}</Stack>'
             f'</SizedBox></Positioned>')
    p.append(K.text(ax + 196, ay + 104, "× (180,100)", width=120, size=16, color="#0F172A"))

caption(*AREAS[0], "①", "两个 50% alpha 矩形", "红 #FF000080 + 蓝 #0000FF80", "α = 128/255，蓝在上层")
caption(*AREAS[1], "②", "整组不透明度 0.5", "不透明红蓝放进 Opacity(0.5)", "组内先合成，再整体混到白底")

# ---------------------------------------------------------------- ③ ④
CX_, CY_, CW_, CH_, CR_ = 40, 40, 240, 160, 20
for idx, (ax, ay) in enumerate(AREAS[2:4], start=3):
    area_frame(ax, ay)
    if idx == 3:
        inner = (K.rect(CX_, CY_, CW_, CH_, color="#FFFFFF", radius=CR_)
                 + f'<Positioned left="{CX_}" top="{CY_}"><ClipRRect borderRadius="{CR_}" '
                   f'clipBehavior="ANTI_ALIAS"><SizedBox width="{CW_}" height="{CH_}">'
                   f'<ImageFiltered sigmaX="6" sigmaY="6" tileMode="CLAMP">'
                   f'<Stack alignment="TOP_LEFT" clipBehavior="NONE">'
                 + stripe_block(CW_ + 20, CH_, -CX_, -CY_)
                 + '</Stack></ImageFiltered></SizedBox></ClipRRect></Positioned>'
                 + K.rect(CX_, CY_, CW_, CH_, color="#FFFFFF1A", radius=CR_,
                          border="1 SOLID #FFFFFFB3")
                 + K.text(CX_ + 20, CY_ + 18, "SHARP", size=24, color="#0F172A", bold=True)
                 + K.rect(CX_ + 20, CY_ + 70, 84, 42, color="#1E293B", radius=6)
                 + K.rect(CX_ + 148, CY_ + 82, 44, 44, color="#FFFFFF", radius=22))
    else:
        inner = (f'<Positioned left="{CX_}" top="{CY_}"><ClipRRect borderRadius="{CR_}" '
                 f'clipBehavior="ANTI_ALIAS"><SizedBox width="{CW_}" height="{CH_}">'
                 f'<ImageFiltered sigmaX="6" sigmaY="6" tileMode="CLAMP">'
                 f'<Stack alignment="TOP_LEFT" clipBehavior="NONE">'
                 + K.rect(0, 0, CW_, CH_, color="#FFFFFF")
                 + stripe_block(CW_ + 20, CH_, 0, 0)
                 + K.text(20, 18, "BLUR", size=24, color="#0F172A", bold=True)
                 + K.rect(20, 70, 84, 42, color="#1E293B", radius=6)
                 + K.rect(148, 82, 44, 44, color="#FFFFFF", radius=22)
                 + K.rect(0, 0, CW_, CH_, color="#00000000", radius=CR_,
                          border="1 SOLID #FFFFFFB3")
                 + '</Stack></ImageFiltered></SizedBox></ClipRRect></Positioned>')
    p.append(f'<Positioned left="{ax}" top="{ay}"><SizedBox width="{AW}" height="{AH}">'
             f'<Stack alignment="TOP_LEFT" clipBehavior="HARD_EDGE">'
             + stripe_block(AW, AH) + inner +
             '</Stack></SizedBox></Positioned>')

caption(*AREAS[2], "③", "仅背景模糊（文字清晰）", "卡 240×160、r=20，σ=6", "模糊只作用于卡内背景层")
caption(*AREAS[3], "④", "整棵子树模糊（文字也糊）", "同一底图、同一 σ 与参数", "模糊覆盖背景 + 文字 + 形状")

# ---------------------------------------------------------------- ⑤ ⑥
SCENE = (
    K.rect(16, 96, 288, 40, color="#2563EB")
    + K.rect(96, 52, 128, 72, color="#1F2937", radius=8,
             extra='boxShadow="0 10 18 0 #0F172A55"')
    + K.rect(210, 150, 56, 56, color="#10B981", radius=28)
    + K.rect(40, 170, 28, 28, color="#F43F5E", radius=6)
    + K.rect(76, 170, 28, 28, color="#F43F5E", radius=6, extra='opacity="0.45"')
)
CIRCLE = "M160 20 A100 100 0 1 0 160 220 A100 100 0 1 0 160 20 Z"
for idx, (ax, ay) in enumerate(AREAS[4:6], start=5):
    area_frame(ax, ay)
    core = (f'<ColorFiltered color="#F6B94A" blendMode="MULTIPLY">'
            f'<ImageFiltered sigmaX="6" sigmaY="6" tileMode="CLAMP">'
            f'<Stack alignment="TOP_LEFT" clipBehavior="NONE">{SCENE}</Stack>'
            f'</ImageFiltered></ColorFiltered>')
    if idx == 6:
        core = (f'<ClipPath path="{CIRCLE}" fillRule="NON_ZERO" clipBehavior="ANTI_ALIAS">'
                f'{core}</ClipPath>')
    p.append(f'<Positioned left="{ax}" top="{ay}"><SizedBox width="{AW}" height="{AH}">'
             f'<Stack alignment="TOP_LEFT" clipBehavior="HARD_EDGE">{core}</Stack>'
             f'</SizedBox></Positioned>')

caption(*AREAS[4], "⑤", "MULTIPLY 着色 + 子树模糊", "#F6B94A 相乘，σ=6", "无裁剪，效果铺满整区")
caption(*AREAS[5], "⑥", "同样效果 + 圆形裁剪", "圆心 (160,120)、半径 100", "蓝条跨圆周，暴露裁剪边界")

# ---------------------------------------------------------------- bottom evidence
BY = 862
p.append(K.rect(208, BY, 1024, 198, color=CARD, radius=14, border="1 SOLID #CBD5E1"))
p.append(K.text(230, BY + 14, "①② 重叠处 (180,100) 的合成结果", size=21, color=INK, bold=True))
for i, line in enumerate([
    "① α=128/255：白底上红→蓝 source-over → RGB(127.0, 63.25, 191.25) → 取整 (127, 63, 191)",
    "② 组 0.5：组内合成纯蓝 (0,0,255)，再以 0.5 混白 → RGB(127.5, 127.5, 255.0) → (128, 128, 255)",
    "R 通道差 1，正是 128/255 与 0.5 的差别；实测取自服务 PNG 的未预乘 RGBA，逐通道容差 ≤3。",
    "③ 仅背景糊、文字锐利　④ 整棵子树糊　⑤ 无裁剪　⑥ r=100 圆裁（蓝条跨圆周）",
]):
    p.append(K.text(230, BY + 46 + i * 34, line, width=980, size=19,
                    color=INK2 if i < 2 else MUTED))

dsl = K.document(W, H, p, background=BG)
path = OUT / "compositing-lab.snapshot"
path.write_text(dsl, encoding="utf-8")
warn = K.drain_warnings()
logger = api.TaskLogger(TASK, TMP)
rec = logger.render(path, OUT / "compositing-lab.png", "lab v2")
print("render:", rec["http_status"], rec["response_bytes"], rec["elapsed_s"], "s")
for w in warn:
    print(w)
if rec["http_status"] != 200:
    print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:1500])
    raise SystemExit(1)
print("size:", api.measure_png(OUT / "compositing-lab.png"))
