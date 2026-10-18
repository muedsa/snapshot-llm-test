"""A10 · 透明合成与滤镜语义实验板 (1440×1100)."""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A10"
TMP = ROOT / "tmp" / RUN / TASK
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from dsl import C, Col, Gap, HGap, Label, Pos, Row, SizedBox, Stack, T  # noqa: E402

BG = "#F3F0E8"
AREA = "#FFFFFF"
INK = "#111827"
MUTED = "#6B7280"
FAINT = "#9CA3AF"
BORDER = "#D9E0E8"
TEAL = "#0F766E"
AMBER = "#B45309"
RED = "#B91C1C"
BLUE = "#1D4ED8"

W, H = 1440, 1100
AW, AH = 320, 240
BLOCK_W, BLOCK_H, GAP = 400, 340, 32
X0 = (W - (3 * BLOCK_W + 2 * GAP)) // 2
Y0 = 170
ORIGINS = [[X0 + c * (BLOCK_W + GAP), Y0 + r * (BLOCK_H + GAP) + 58] for r in range(2) for c in range(3)]


def stripes():
    parts = [Pos(0, 0, C(width=AW, height=AH, color="#FFFFFF"))]
    for i in range(0, 20):
        color = "#0EA5E9" if i % 2 == 0 else "#E2E8F0"
        parts.append(Pos(i * 16, 0, C(width=16, height=AH, color=color)))
    return Stack(parts, width=AW, height=AH)


def card_stack(blur_all: bool):
    base = stripes()
    fill = Pos(40, 40, C(width=240, height=160, color="#FFFFFF66", borderRadius=20, border="1 SOLID #0F172A22"))
    plate = Pos(65, 85, C(width=190, height=40, color="#FFFFFFCC", borderRadius=8))
    text = Pos(65, 85, Label("SHARP / BLUR", 190, 40, align="CENTER", size=24, color="#0F172A", weight="BOLD", family="Inter"))
    shape = Pos(196, 140, C(width=32, height=32, color="#F59E0B", borderRadius=8))
    if blur_all:
        inner = Stack([base, fill, plate, text, shape], width=AW, height=AH)
        filt = f'<ImageFiltered sigmaX="6" sigmaY="6" tileMode="CLAMP">{inner}</ImageFiltered>'
    else:
        filt = f'<ImageFiltered sigmaX="6" sigmaY="6" tileMode="CLAMP">{base}</ImageFiltered>'
    contents = [filt]
    if not blur_all:
        contents += [fill, plate, text, shape]
    path = ("M60 40 H260 A20 20 0 0 1 280 60 V180 A20 20 0 0 1 260 200 "
            "H60 A20 20 0 0 1 40 180 V60 A20 20 0 0 1 60 40 Z")
    clip = f'<ClipPath path="{path}">{Stack(contents, width=AW, height=AH)}</ClipPath>'
    return Stack([stripes(), Pos(0, 0, clip, w=AW, h=AH)], width=AW, height=AH)


def fshape(x, y, w, h, color, radius=0, shadow=None):
    kw = f'color="{color}" borderRadius="{radius}"'
    if shadow:
        kw += f' boxShadow="{shadow}"'
    return Pos(x, y, f'<ColorFiltered color="#F6B94A" blendMode="MULTIPLY"><Container width="{w}" height="{h}" {kw} /></ColorFiltered>')


def filter_scene():
    parts = [SizedBox(AW, AH)]
    parts.append(fshape(20, 70, 280, 100, "#1F2937", 14))
    parts.append(fshape(60, 30, 70, 58, "#2563EB", 10))
    parts.append(fshape(190, 30, 70, 58, "#0EA5E9", 10))
    parts.append(fshape(60, 150, 80, 30, "#F59E0B", 6))
    parts.append(fshape(150, 150, 100, 30, "#EF4444", 6))
    parts.append(fshape(110, 84, 100, 72, "#FFFFFF", 12, "0 10 22 0 #00000066 NORMAL"))
    return Stack(parts, width=AW, height=AH)


def filtered(clip: bool):
    scene = filter_scene()
    wrapped = (f'<ImageFiltered sigmaX="6" sigmaY="6" tileMode="CLAMP">'
               f'{scene}'
               f'</ImageFiltered>')
    if clip:
        path = "M60 120 A100 100 0 1 0 260 120 A100 100 0 1 0 60 120 Z"
        inner = f'<ClipPath path="{path}">{wrapped}</ClipPath>'
        return Stack([Pos(0, 0, C(width=AW, height=AH, color="#FFFFFF")), Pos(0, 0, inner, w=AW, h=AH)],
                     width=AW, height=AH)
    return Stack([Pos(0, 0, wrapped, w=AW, h=AH)], width=AW, height=AH)


def alpha_panels():
    # panel 1: per-shape alpha
    p1 = Stack([
        Pos(0, 0, C(width=AW, height=AH, color="#FFFFFF")),
        Pos(40, 40, C(width=160, height=120, color="#FF000080")),
        Pos(120, 80, C(width=160, height=120, color="#0000FF80")),
    ], width=AW, height=AH)
    # panel 2: group opacity with opaque rects
    group = Stack([
        Pos(40, 40, C(width=160, height=120, color="#FF0000")),
        Pos(120, 80, C(width=160, height=120, color="#0000FF")),
    ], width=AW, height=AH)
    p2 = Stack([
        Pos(0, 0, C(width=AW, height=AH, color="#FFFFFF")),
        Pos(0, 0, f'<Opacity opacity="0.5">{group}</Opacity>', w=AW, h=AH),
    ], width=AW, height=AH)
    return p1, p2


def build():
    p1, p2 = alpha_panels()
    panels = [p1, p2, card_stack(False), card_stack(True), filtered(False), filtered(True)]
    titles = ["① 逐形状 alpha", "② 组 Opacity 0.5", "③ 仅背景模糊",
              "④ 子树模糊", "⑤ 滤色 × 模糊", "⑥ ⑤ + 圆形裁剪"]
    descs = ["红/蓝各自 50% alpha，蓝在上层", "不透明红蓝先合成，再整体 0.5",
             "卡内背景条纹模糊，文字/前景清晰", "卡内背景、文字、前景一起模糊",
             "先 MULTIPLY #F6B94A，再 sigma 6", "同一结果裁剪到 r=100 圆内"]

    blocks = []
    for i, p in enumerate(panels):
        col, row = i % 3, i // 3
        bx = X0 + col * (BLOCK_W + GAP)
        by = Y0 + row * (BLOCK_H + GAP)
        blocks.append(Pos(bx, by, T(titles[i], size=22, color=INK, weight="BOLD"), w=BLOCK_W, h=30))
        blocks.append(Pos(bx, by + 32, T(descs[i], size=20, color=MUTED, max_lines=1), w=BLOCK_W, h=24))
        blocks.append(Pos(bx, by + 58, C(width=AW, height=AH, color=AREA, borderRadius=4,
                                        border=f"1 SOLID {BORDER}", child=p), w=AW, h=AH))
        blocks.append(Pos(bx, by + 58 + AH + 6, T(f"局部 320×240 · origin ({ORIGINS[i][0]},{ORIGINS[i][1]})",
                                                  size=16, color=FAINT, family="Inter"), w=BLOCK_W, h=20))

    header = Row([
        C(width=46, height=46, gradientType="LINEAR", gradientColors="#F6B94A,#2563EB",
          gradientBegin="TOP_LEFT", gradientEnd="BOTTOM_RIGHT", borderRadius=12,
          child=C(alignment="CENTER", child=T("A", size=22, color="#FFFFFF", weight="BOLD", family="Inter"))),
        HGap(12),
        Col([
            T("看到差异，才能说用对了", size=40, color=INK, weight="BOLD", family="Noto Serif CJK SC,Inter"),
            Gap(2),
            T("透明合成 · 背景/子树模糊 · ColorFiltered × 高斯 · 圆形裁剪", size=20, color=MUTED),
        ], crossAxisAlignment="START"),
        '<Spacer />',
        Col([
            T("COMPOSITING LAB", size=14, color=AMBER, weight="BOLD", family="Inter", spacing=2),
            Gap(3),
            T("6 个 320×240 实验区", size=16, color=MUTED),
        ], crossAxisAlignment="END"),
    ], crossAxisAlignment="CENTER")

    footer = C(width=1352, height=176, color="#FFFFFF", borderRadius=14, border=f"1 SOLID {BORDER}",
               padding="(14,22)", child=Col([
                   Row([T("读数与判断", size=22, color=INK, weight="BOLD"), HGap(10),
                        T("采样点：局部 (180,100)；① ② 分别在各自实验区", size=20, color=MUTED)]),
                   Gap(4),
                   T("① 128/255 逐层：红 over 白 → 蓝 over 红 ⇒ 理论 (127.000, 63.247, 191.247)，取整 (127,63,191)。", size=20, color=INK),
                   T("② 组 0.5：不透明蓝整体 over 白 ⇒ 理论 (127.5, 127.5, 255.0)，取整 (128,128,255)。128/255 与 0.5 不是同一个 alpha。", size=20, color=INK),
                   T("③ 文字清晰、卡内背景模糊、卡外不外溢；④ 文字与前景一起模糊；⑤ 无裁剪、模糊向圆周外溢出；⑥ 同样结果被 r=100 圆裁剪，边界可见。", size=20, color=MUTED),
               ], crossAxisAlignment="START"))

    content = Stack([
        SizedBox(W, H),
        Pos(0, 0, C(width=W, height=5, gradientType="LINEAR",
                    gradientColors="#F6B94A00,#F6B94AE6,#2563EBE6,#F6B94A00",
                    gradientBegin="CENTER_LEFT", gradientEnd="CENTER_RIGHT"), w=W, h=5),
        Pos(44, 30, header, w=W - 88, h=76),
        Pos(44, 120, Row([
            T("六个实验区均为白底 320×240，区与区间距 32px；编号与说明在区外。", size=20, color=MUTED),
            '<Spacer />',
            T("滤镜 sigmaX = sigmaY = 6", size=18, color=FAINT),
        ], crossAxisAlignment="CENTER"), w=W - 88, h=26),
        *blocks,
        Pos(44, 900, footer, w=1352, h=176),
        Pos(44, 1080, Row([
            T("数据源：任务说明中的固定参数 · 无外部素材", size=15, color=FAINT),
            '<Spacer />',
            T("COMPOSITING LAB · 1440×1100", size=14, color=FAINT, family="Inter", spacing=1),
        ], crossAxisAlignment="CENTER"), w=W - 88, h=18),
    ], width=W, height=H)
    return f'<Snapshot type="png" background="{BG}">\n{content}\n</Snapshot>\n'


def expected():
    a = 128 / 255
    # red over white
    r1 = (255.0, 255.0 * (1 - a), 255.0 * (1 - a))
    # blue over that
    r2 = (r1[0] * (1 - a), r1[1] * (1 - a), r1[2] * (1 - a) + 255.0 * a)
    b = 0.5
    g = (0.0 * b + 255.0 * (1 - b), 0.0 * b + 255.0 * (1 - b), 255.0 * b + 255.0 * (1 - b))
    return r2, g


def audit():
    e1, e2 = expected()
    return {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "canvas": [W, H],
        "panels": [
            {"id": 1, "title": "逐形状 alpha", "origin": ORIGINS[0], "size": [AW, AH],
             "local_rects": {"red": [40, 40, 160, 120], "blue": [120, 80, 160, 120]},
             "colors": {"red": "#FF000080 (alpha 128/255)", "blue": "#0000FF80 (alpha 128/255)"},
             "effect_nodes": ["两个 Container color 8 位 RGBA"]},
            {"id": 2, "title": "组 Opacity 0.5", "origin": ORIGINS[1], "size": [AW, AH],
             "local_rects": {"red": [40, 40, 160, 120], "blue": [120, 80, 160, 120]},
             "colors": {"red": "#FF0000 opaque", "blue": "#0000FF opaque"},
             "effect_nodes": ["<Opacity opacity=\"0.5\"> 包裹不透明红蓝组"]},
            {"id": 3, "title": "仅背景模糊", "origin": ORIGINS[2], "size": [AW, AH],
             "effect_nodes": ["ClipPath 圆角卡", "ImageFiltered 仅包裹条纹副本", "文字/前景在滤镜外"]},
            {"id": 4, "title": "子树模糊", "origin": ORIGINS[3], "size": [AW, AH],
             "effect_nodes": ["ClipPath 圆角卡", "ImageFiltered 包裹条纹+卡面+文字+前景"]},
            {"id": 5, "title": "滤色 × 模糊", "origin": ORIGINS[4], "size": [AW, AH],
             "effect_nodes": ["每个可见形状先 ColorFiltered MULTIPLY", "整组再 ImageFiltered sigma=6", "无裁剪"]},
            {"id": 6, "title": "⑤ + 圆形裁剪", "origin": ORIGINS[5], "size": [AW, AH],
             "effect_nodes": ["与⑤相同的逐形状 ColorFiltered + 整组 ImageFiltered", "外层 ClipPath 圆 r=100"]},
        ],
        "paired_scenes": [
            {"pair": "③④", "shared": {"stripes": "vertical 16px #0EA5E9 / #E2E8F0, phase 0",
                                        "card": [40, 40, 240, 160], "radius": 20,
                                        "card_fill": "#FFFFFF66", "text": "SHARP / BLUR", "text_size": 24,
                                        "foreground": [196, 140, 32, 32, "#F59E0B"],
                                        "sigma": 6},
             "only_change": "ImageFiltered 的作用对象：③仅条纹副本；④条纹+卡面+文字+前景整个子树"},
            {"pair": "⑤⑥", "shared": {"content": "同一 Stack：深色矩形、两块彩色矩形、透明间隙、白色圆角卡+阴影",
                                        "color_filter": {"color": "#F6B94A", "blendMode": "MULTIPLY"},
                                        "sigma": 6, "filter_order": "先 ColorFiltered，再外层 ImageFiltered"},
             "only_change": "⑥ 在同样结果外增加 ClipPath 圆（中心 160,120，半径 100）；⑤ 无裁剪",
             "circle": {"center": [160, 120], "radius": 100,
                        "path": "M60 120 A100 100 0 1 0 260 120 A100 100 0 1 0 60 120 Z"}},
        ],
        "samples": [
            {"panel": 1, "local": [180, 100], "canvas": [ORIGINS[0][0] + 180, ORIGINS[0][1] + 100],
             "alpha_model": "per-shape alpha 128/255", "steps": [
                 {"step": "red over white", "rgb_float": [round(v, 6) for v in (255.0, 255.0 * (1 - 128/255), 255.0 * (1 - 128/255))]},
                 {"step": "blue over previous", "rgb_float": [round(v, 6) for v in e1]}],
             "theoretical_float": [round(v, 6) for v in e1],
             "rounded": [math.floor(v + 0.5) for v in e1],
             "expected_rgb": [math.floor(v + 0.5) for v in e1], "actual_rgb": None, "alpha": None,
             "errors": None, "tolerance_per_channel": 3, "passed": None},
            {"panel": 2, "local": [180, 100], "canvas": [ORIGINS[1][0] + 180, ORIGINS[1][1] + 100],
             "alpha_model": "group opacity 0.5", "steps": [
                 {"step": "opaque blue over opaque red (within group)", "rgb_float": [0.0, 0.0, 255.0]},
                 {"step": "group over white at 0.5", "rgb_float": [round(v, 6) for v in e2]}],
             "theoretical_float": [round(v, 6) for v in e2],
             "rounded": [math.floor(v + 0.5) for v in e2],
             "expected_rgb": [math.floor(v + 0.5) for v in e2], "actual_rgb": None, "alpha": None,
             "errors": None, "tolerance_per_channel": 3, "passed": None},
        ],
        "visual_checks": [
            {"panel": 3, "text": "SHARP / BLUR 边缘清晰，无模糊光晕", "background": "卡内条纹明显柔化，卡外条纹保持锐利", "spill": "卡外无模糊外溢", "evidence": "tmp/RUN/checks/panel3.png", "doc": "parser-tags · ImageFiltered 只作用于被包裹子树"},
            {"panel": 4, "text": "文字与橙色前景均出现明显模糊边缘", "background": "卡内条纹柔化", "spill": "卡外无模糊外溢", "evidence": "tmp/RUN/checks/panel4.png", "doc": "同 ImageFiltered 包裹整棵卡片子树"},
            {"panel": 5, "text": "内容整体被 #F6B94A 乘色后模糊，外围可见模糊晕", "background": "白底，无裁剪边界", "spill": "模糊向四周溢出", "evidence": "tmp/RUN/checks/panel5.png", "doc": "ColorFiltered MULTIPLY + ImageFiltered"},
            {"panel": 6, "text": "与⑤同样模糊，但被圆形边界截断", "background": "圆外为白，圆内保留模糊结果", "spill": "无圆外溢出", "evidence": "tmp/RUN/checks/panel6.png", "doc": "ClipPath 圆 + 同⑤滤镜"},
        ],
        "docs": [
            "https://snapshot.muedsa.com/reference/parser-tags/ · 颜色 alpha 8 位、Opacity、ImageFiltered、BackdropFilter、ColorFiltered、ClipPath",
            "https://open-snapshot.muedsa.com/ai-guide.md · 请求/响应与 PNG 检查",
        ],
    }


def main() -> int:
    dsl = build()
    d = TMP / "dsl"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{VERSION}.snapshot").write_text(dsl, encoding="utf-8")
    audit_data = audit()
    (TMP / "composite-audit.json").write_text(json.dumps(audit_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"A10 {VERSION}: {len(dsl)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
