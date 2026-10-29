#!/usr/bin/env python3
"""A10 compositing lab: alpha vs opacity, backdrop vs subtree blur, color filter, clip."""
import json, os, html
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN_ID = SCRIPT.parents[2].name
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A10"
OUT.mkdir(parents=True, exist_ok=True)

def esc(s): return html.escape(str(s), quote=False)
def T(txt, size, color="#0B1220", bold=False, extra=""):
    st = ' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="Noto Sans CJK SC" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'

W, H = 1440, 1100
CW, CH, GAP = 320, 240, 40
X0, Y0 = 200, 190
origins = {}
rows_y = [Y0, Y0 + CH + GAP]
cols_x = [X0, X0 + CW + GAP, X0 + 2 * (CW + GAP)]
for i in range(6):
    origins[i] = (cols_x[i % 3], rows_y[i // 3])

def stripes(w, h, phase=0, colors=("#F6B94A", "#FFF3D6"), sw=12):
    out = []
    x = -phase
    i = 0
    while x < w:
        out.append(f'<Positioned left="{x}" top="0" width="{sw}" height="{h}"><Container width="{sw}" height="{h}" color="{colors[i % 2]}"/></Positioned>')
        x += sw; i += 1
    return "".join(out)

def cell_bg():
    return '<Container width="320" height="240" color="#FFFFFF"/>'

parts = ['<Snapshot background="#F6F7FB" type="png">', '<Container width="1440" height="1100"><Stack alignment="TOP_LEFT"><Container width="1440" height="1100" color="#F6F7FB"/>']
parts.append('<Positioned left="40" top="30"><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T("COMPOSITING LAB / SIX DIFFERENCES", 14, "#2563EB", True, ' letterSpacing="2"') + T("看到差异，才能说用对了", 40, "#0B1220", True) + T("六个 320×240 实验区 · 编号与说明在区外 · 滤镜 sigma = 6", 20, "#56637A") + '</Column></Positioned>')
parts.append('<Positioned right="40" top="40"><Column crossAxisAlignment="END" mainAxisSize="MIN">' + T("① alpha  ≠  ② group opacity", 22, "#0B1220", True) + T("③ background blur  ≠  ④ subtree blur", 18, "#64748B") + '</Column></Positioned>')

labels = ["① 50% alpha 叠加", "② Opacity(0.5) 组", "③ 仅背景模糊", "④ 子树整体模糊", "⑤ MULTIPLY + 模糊", "⑥ 同⑤ + 圆形裁剪"]
for i in range(6):
    x, y = origins[i]
    parts.append(f'<Positioned left="{x}" top="{y-34}"><Container width="{CW}"><Row crossAxisAlignment="CENTER"><Container width="8" height="8" color="#2563EB" shape="CIRCLE"/><SizedBox width="8"/>' + T(labels[i], 20, "#334155", True) + '</Row></Container></Positioned>')
    parts.append(f'<Positioned left="{x}" top="{y}"><Container width="{CW}" height="{CH}" color="#FFFFFF" border="1 SOLID #DCE3EE" borderRadius="8"><Stack alignment="TOP_LEFT" clipBehavior="NONE">{cell_bg()}')

# ① alpha rects
parts.append('<Positioned left="40" top="40" width="160" height="120"><Container width="160" height="120" color="#FF000080"/></Positioned>')
parts.append('<Positioned left="120" top="80" width="160" height="120"><Container width="160" height="120" color="#0000FF80"/></Positioned>')
# ② opacity group
parts.append('<Positioned left="0" top="0" width="320" height="240"><Opacity opacity="0.5"><Stack alignment="TOP_LEFT"><Container width="320" height="240" color="transparent"/>')
parts.append('<Positioned left="40" top="40" width="160" height="120"><Container width="160" height="120" color="#FF0000"/></Positioned>')
parts.append('<Positioned left="120" top="80" width="160" height="120"><Container width="160" height="120" color="#0000FF"/></Positioned>')
parts.append('</Stack></Opacity></Positioned>')
parts.append('</Stack></Container></Positioned>')

# ③ background-only blur
x, y = origins[2]
parts.append(f'<Positioned left="{x}" top="{y}"><Container width="{CW}" height="{CH}" color="#FFFFFF" border="1 SOLID #DCE3EE" borderRadius="8"><Stack alignment="TOP_LEFT" clipBehavior="NONE">{cell_bg()}')
parts.append(stripes(320, 240))
parts.append('<Positioned left="40" top="40" width="240" height="160"><ClipRRect borderRadius="20" clipBehavior="ANTI_ALIAS"><Stack alignment="TOP_LEFT"><Container width="240" height="160" color="transparent"/>')
parts.append('<BackdropFilter sigmaX="6" sigmaY="6" tileMode="CLAMP"><Container width="240" height="160" color="#0B12204D"/></BackdropFilter>')
parts.append('<Container width="240" height="160" color="#FFFFFF0A" border="1 SOLID #FFFFFF66" borderRadius="20"/>')
parts.append('<Positioned left="0" top="60" width="240"><Container width="240" alignment="CENTER">' + T("SHARP / BLUR", 24, "#FFFFFF", True) + '</Container></Positioned>')
parts.append('<Positioned left="24" top="120" width="86" height="18"><Container width="86" height="18" color="#FFFFFF" borderRadius="9"/></Positioned>')
parts.append('</Stack></ClipRRect></Positioned>')
parts.append('</Stack></Container></Positioned>')

# ④ subtree blur with duplicated stripes inside card
x, y = origins[3]
parts.append(f'<Positioned left="{x}" top="{y}"><Container width="{CW}" height="{CH}" color="#FFFFFF" border="1 SOLID #DCE3EE" borderRadius="8"><Stack alignment="TOP_LEFT" clipBehavior="NONE">{cell_bg()}')
parts.append(stripes(320, 240))
parts.append('<Positioned left="40" top="40" width="240" height="160"><ClipRRect borderRadius="20" clipBehavior="ANTI_ALIAS"><ImageFiltered sigmaX="6" sigmaY="6" tileMode="CLAMP"><Stack alignment="TOP_LEFT"><Container width="240" height="160" color="#FFF3D6"/>')
parts.append('<Positioned left="0" top="0" width="240" height="160"><Stack alignment="TOP_LEFT">' + stripes(240, 160, phase=8) + '</Stack></Positioned>')
parts.append('<Container width="240" height="160" color="#0B12204D"/>')
parts.append('<Positioned left="0" top="60" width="240"><Container width="240" alignment="CENTER">' + T("SHARP / BLUR", 24, "#FFFFFF", True) + '</Container></Positioned>')
parts.append('<Positioned left="24" top="120" width="86" height="18"><Container width="86" height="18" color="#FFFFFF" borderRadius="9"/></Positioned>')
parts.append('</Stack></ImageFiltered></ClipRRect></Positioned>')
parts.append('</Stack></Container></Positioned>')

# ⑤ filter + blur
def filter_scene(clipped):
    out = ['<Stack alignment="TOP_LEFT"><Container width="320" height="240" color="#FFFFFF"/>']
    if clipped:
        out.append('<Positioned left="60" top="20" width="200" height="200"><ClipOval clipBehavior="ANTI_ALIAS"><ColorFiltered color="#F6B94A" blendMode="MULTIPLY"><ImageFiltered sigmaX="6" sigmaY="6" tileMode="CLAMP"><Stack alignment="TOP_LEFT"><Container width="200" height="200" color="#FFFFFF"/>')
        out.append('<Positioned left="0" top="10" width="110" height="180"><Container width="110" height="180" color="#2563EB" boxShadow="0 10 24 0 #2563EB66"/></Positioned>')
        out.append('<Positioned left="130" top="10" width="70" height="180"><Container width="70" height="180" color="#2563EB"/></Positioned>')
        out.append('<Positioned left="40" top="70" width="120" height="60"><Container width="120" height="60" color="#0F172A"/></Positioned>')
        out.append('<Positioned left="150" top="60" width="80" height="80"><Container width="80" height="80" color="#FACC15" shape="CIRCLE"/></Positioned>')
        out.append('</Stack></ImageFiltered></ColorFiltered></ClipOval></Positioned>')
    else:
        out.append('<Positioned left="0" top="0" width="320" height="240"><ColorFiltered color="#F6B94A" blendMode="MULTIPLY"><ImageFiltered sigmaX="6" sigmaY="6" tileMode="CLAMP"><Stack alignment="TOP_LEFT"><Container width="320" height="240" color="#FFFFFF"/>')
        out.append('<Positioned left="60" top="30" width="110" height="180"><Container width="110" height="180" color="#2563EB" boxShadow="0 10 24 0 #2563EB66"/></Positioned>')
        out.append('<Positioned left="190" top="30" width="70" height="180"><Container width="70" height="180" color="#2563EB"/></Positioned>')
        out.append('<Positioned left="100" top="90" width="120" height="60"><Container width="120" height="60" color="#0F172A"/></Positioned>')
        out.append('<Positioned left="210" top="80" width="80" height="80"><Container width="80" height="80" color="#FACC15" shape="CIRCLE"/></Positioned>')
        out.append('</Stack></ImageFiltered></ColorFiltered></Positioned>')
    out.append('</Stack>')
    return "".join(out)

for idx, clip in [(4, False), (5, True)]:
    x, y = origins[idx]
    parts.append(f'<Positioned left="{x}" top="{y}"><Container width="{CW}" height="{CH}" color="#FFFFFF" border="1 SOLID #DCE3EE" borderRadius="8">{filter_scene(clip)}</Container></Positioned>')


# explanation panel outside the cells
parts.append('<Positioned left="200" top="742"><Row crossAxisAlignment="END">' + T("观察记录 / WHAT TO LOOK AT", 16, "#2563EB", True, ' letterSpacing="1.5"') + '<SizedBox width="14"/>' + T("说明写在实验区外；所有区域 320×240 白底", 18, "#64748B") + '</Row></Positioned>')
captions = [
    ("①", "alpha 叠加", "红/蓝各自 50% alpha，按红→蓝→白底顺序合成；重叠处为 (127,63,191)。"),
    ("②", "组不透明度", "不透明红蓝先在 Opacity 0.5 组内合成，再整体叠白底；样本为 (128,128,255)。"),
    ("③", "仅背景模糊", "BackdropFilter 只作用卡内背景；条纹跨卡边，卡外仍锐利，SHARP / BLUR 清晰。"),
    ("④", "子树模糊", "同一场景整卡子树 ImageFiltered；文字与形状一起变糊，卡外条纹仍清晰。"),
    ("⑤", "滤色 + 模糊", "MULTIPLY 后 sigma 6；透明间隙、深色矩形、阴影一起被处理，可观察边缘扩散。"),
    ("⑥", "同⑤ + 圆裁", "在最外层加 ClipOval，圆心 (160,120)、r100；圆周切过黄色形状，边界可见。"),
]
for i, (num, name, body) in enumerate(captions):
    cx = 200 + (i % 3) * 355
    cy = 770 + (i // 3) * 154
    parts.append(f'<Positioned left="{cx}" top="{cy}"><Container width="330" height="140" color="#FFFFFF" borderRadius="12" border="1 SOLID #E1E7F0" padding="14"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
    parts.append('<Row crossAxisAlignment="CENTER">' + T(num + " " + name, 20, "#0B1220", True) + '</Row>')
    parts.append('<SizedBox height="4"/>')
    parts.append(T(body, 20, "#475569"))
    parts.append('</Column></Container></Positioned>')
parts.append('</Stack></Container></Snapshot>')
dsl = "\n".join(parts)
(OUT / "compositing-lab.snapshot").write_text(dsl, encoding="utf-8")

def over(src, sa, dst):
    return tuple(src[i] * sa + dst[i] * (1 - sa) for i in range(3))
a = 128 / 255
white = (255, 255, 255)
r1 = over((255, 0, 0), a, white)
r2 = over((0, 0, 255), a, r1)
p1 = tuple(int(x + 0.5) for x in r2)
g = (0, 0, 255)
p2 = tuple(int(0.5 * g[i] + 0.5 * 255 + 0.5) for i in range(3))
audit = {
    "schema_version": 1, "task_id": "A10", "path_base": "output_dir",
    "canvas": [W, H],
    "cells": [{"index": i + 1, "label": labels[i], "origin_px": list(origins[i]), "size": [CW, CH]} for i in range(6)],
    "alpha_math": {
        "sample_local": [180, 100],
        "sample_pixels": [{"cell": 1, "x": origins[0][0] + 180, "y": origins[0][1] + 100},
                          {"cell": 2, "x": origins[1][0] + 180, "y": origins[1][1] + 100}],
        "alpha_128_over_255": a,
        "cell1_steps": {
            "red_over_white": [round(v, 6) for v in r1],
            "blue_over_result": [round(v, 6) for v in r2],
            "rounded": list(p1),
            "explanation": "red #FF000080 alpha=128/255≈0.50196；蓝 #0000FF80 再次按 128/255 覆盖。"
        },
        "cell2_steps": {
            "opaque_group_content_at_sample": [0, 0, 255],
            "group_opacity": 0.5,
            "over_white": [127.5, 127.5, 255.0],
            "rounded": list(p2),
            "explanation": "红蓝不透明先在组内合成（蓝在上，样本为纯蓝），再以精确 0.5 组透明度叠到白底。"
        },
        "difference": "128/255 作用于每个绘制操作；0.5 作用于已合成后的整组，二者不可互换。",
        "rounding": "floor(value+0.5)",
        "tolerance_per_channel": 3
    },
    "filter_params": {"sigmaX": 6, "sigmaY": 6, "card": [240, 160], "card_radius": 20,
                      "color_filter": "#F6B94A", "blend_mode": "MULTIPLY",
                      "clip_circle": {"center_local": [160, 120], "radius": 100},
                      "card_local_origin": [40, 40], "text_size": 24},
    "pair_sharing": {
        "cell3_4": {"shared": ["stripe colors/width/phase", "card origin/size/radius", "text", "foreground shape", "draw order"],
                    "only_change": "blur applies to background only (3) vs whole card subtree (4)"},
        "cell5_6": {"shared": ["base scene", "MULTIPLY filter", "sigma 6", "shadow", "positions", "colors"],
                    "only_change": "ClipOval radius 100 at (160,120) in 6"}
    },
    "visual_checks": []
}
(OUT / "composite-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
print("wrote A10", len(dsl), "theoretical", p1, p2)
