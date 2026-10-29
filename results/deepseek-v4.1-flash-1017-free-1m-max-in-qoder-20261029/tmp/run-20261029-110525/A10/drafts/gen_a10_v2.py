#!/usr/bin/env python3
"""A10 compositing lab (v2): six cells emitted independently."""
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
cols_x = [X0, X0 + CW + GAP, X0 + 2 * (CW + GAP)]
rows_y = [Y0, Y0 + CH + GAP]
origins = {i: (cols_x[i % 3], rows_y[i // 3]) for i in range(6)}

def stripes(w, h, phase=0):
    out = []
    x = -phase; i = 0
    while x < w:
        c = "#F6B94A" if i % 2 == 0 else "#FFF3D6"
        out.append(f'<Positioned left="{x}" top="0" width="12" height="{h}"><Container width="12" height="{h}" color="{c}"/></Positioned>')
        x += 12; i += 1
    return "".join(out)

def begin(i):
    x, y = origins[i]
    return (f'<Positioned left="{x}" top="{y}"><Container width="{CW}" height="{CH}" color="#FFFFFF" border="1 SOLID #DCE3EE" borderRadius="8">'
            f'<Stack alignment="TOP_LEFT" clipBehavior="NONE"><Container width="320" height="240" color="#FFFFFF"/>')

END = '</Stack></Container></Positioned>'

def card_sharp():
    return ('<Positioned left="40" top="40" width="240" height="160"><ClipRRect borderRadius="20" clipBehavior="ANTI_ALIAS"><Stack alignment="TOP_LEFT"><Container width="240" height="160" color="transparent"/>'
            '<BackdropFilter sigmaX="6" sigmaY="6" tileMode="CLAMP"><Container width="240" height="160" color="#0B12204D"/></BackdropFilter>'
            '<Container width="240" height="160" color="#FFFFFF0A" border="1 SOLID #FFFFFF66" borderRadius="20"/>'
            '<Positioned left="0" top="60" width="240"><Container width="240" alignment="CENTER">' + T("SHARP / BLUR", 24, "#FFFFFF", True) + '</Container></Positioned>'
            '<Positioned left="24" top="120" width="86" height="18"><Container width="86" height="18" color="#FFFFFF" borderRadius="9"/></Positioned>'
            '</Stack></ClipRRect></Positioned>')

def card_blur():
    return ('<Positioned left="40" top="40" width="240" height="160"><ClipRRect borderRadius="20" clipBehavior="ANTI_ALIAS"><ImageFiltered sigmaX="6" sigmaY="6" tileMode="CLAMP"><Stack alignment="TOP_LEFT"><Container width="240" height="160" color="#FFF3D6"/>'
            '<Positioned left="0" top="0" width="240" height="160"><Stack alignment="TOP_LEFT">' + stripes(240, 160, 8) + '</Stack></Positioned>'
            '<Container width="240" height="160" color="#0B12204D"/>'
            '<Positioned left="0" top="60" width="240"><Container width="240" alignment="CENTER">' + T("SHARP / BLUR", 24, "#FFFFFF", True) + '</Container></Positioned>'
            '<Positioned left="24" top="120" width="86" height="18"><Container width="86" height="18" color="#FFFFFF" borderRadius="9"/></Positioned>'
            '</Stack></ImageFiltered></ClipRRect></Positioned>')

def filter_scene(clipped):
    if clipped:
        content = ('<ClipOval clipBehavior="ANTI_ALIAS"><ColorFiltered color="#F6B94A" blendMode="MULTIPLY"><ImageFiltered sigmaX="6" sigmaY="6" tileMode="CLAMP"><Stack alignment="TOP_LEFT"><Container width="200" height="200" color="#FFFFFF"/>'
                   '<Positioned left="0" top="10" width="110" height="180"><Container width="110" height="180" color="#2563EB" boxShadow="0 10 24 0 #2563EB66"/></Positioned>'
                   '<Positioned left="130" top="10" width="70" height="180"><Container width="70" height="180" color="#2563EB"/></Positioned>'
                   '<Positioned left="40" top="70" width="120" height="60"><Container width="120" height="60" color="#0F172A"/></Positioned>'
                   '<Positioned left="150" top="60" width="80" height="80"><Container width="80" height="80" color="#FACC15" shape="CIRCLE"/></Positioned>'
                   '</Stack></ImageFiltered></ColorFiltered></ClipOval>')
        return ('<Positioned left="0" top="0" width="320" height="240"><ClipRect><Stack alignment="TOP_LEFT"><Container width="320" height="240" color="#FFFFFF"/>'
                '<Positioned left="60" top="20" width="200" height="200">' + content + '</Positioned></Stack></ClipRect></Positioned>')
    content = ('<ColorFiltered color="#F6B94A" blendMode="MULTIPLY"><ImageFiltered sigmaX="6" sigmaY="6" tileMode="CLAMP"><Stack alignment="TOP_LEFT"><Container width="320" height="240" color="#FFFFFF"/>'
               '<Positioned left="60" top="30" width="110" height="180"><Container width="110" height="180" color="#2563EB" boxShadow="0 10 24 0 #2563EB66"/></Positioned>'
               '<Positioned left="190" top="30" width="70" height="180"><Container width="70" height="180" color="#2563EB"/></Positioned>'
               '<Positioned left="100" top="90" width="120" height="60"><Container width="120" height="60" color="#0F172A"/></Positioned>'
               '<Positioned left="210" top="80" width="80" height="80"><Container width="80" height="80" color="#FACC15" shape="CIRCLE"/></Positioned>'
               '</Stack></ImageFiltered></ColorFiltered>')
    return ('<Positioned left="0" top="0" width="320" height="240"><ClipRect><Stack alignment="TOP_LEFT"><Container width="320" height="240" color="#FFFFFF"/>'
            + content + '</Stack></ClipRect></Positioned>')

parts = ['<Snapshot background="#F6F7FB" type="png">', '<Container width="1440" height="1100"><Stack alignment="TOP_LEFT"><Container width="1440" height="1100" color="#F6F7FB"/>']
parts.append('<Positioned left="40" top="30"><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T("COMPOSITING LAB / SIX DIFFERENCES", 14, "#2563EB", True, ' letterSpacing="2"') + T("看到差异，才能说用对了", 40, "#0B1220", True) + T("六个 320×240 实验区 · 编号与说明在区外 · 滤镜 sigma = 6", 20, "#56637A") + '</Column></Positioned>')
parts.append('<Positioned right="40" top="40"><Column crossAxisAlignment="END" mainAxisSize="MIN">' + T("① alpha  ≠  ② group opacity", 22, "#0B1220", True) + T("③ background blur  ≠  ④ subtree blur", 18, "#64748B") + '</Column></Positioned>')
labels = ["① 50% alpha 叠加", "② Opacity(0.5) 组", "③ 仅背景模糊", "④ 子树整体模糊", "⑤ MULTIPLY + 模糊", "⑥ 同⑤ + 圆形裁剪"]
for i in range(6):
    x, y = origins[i]
    parts.append(f'<Positioned left="{x}" top="{y-34}"><Container width="{CW}"><Row crossAxisAlignment="CENTER"><Container width="8" height="8" color="#2563EB" shape="CIRCLE"/><SizedBox width="8"/>' + T(labels[i], 20, "#334155", True) + '</Row></Container></Positioned>')
    parts.append(begin(i))
    if i == 0:
        parts.append('<Positioned left="40" top="40" width="160" height="120"><Container width="160" height="120" color="#FF000080"/></Positioned>')
        parts.append('<Positioned left="120" top="80" width="160" height="120"><Container width="160" height="120" color="#0000FF80"/></Positioned>')
    elif i == 1:
        parts.append('<Positioned left="0" top="0" width="320" height="240"><Opacity opacity="0.5"><Stack alignment="TOP_LEFT"><Container width="320" height="240" color="transparent"/>')
        parts.append('<Positioned left="40" top="40" width="160" height="120"><Container width="160" height="120" color="#FF0000"/></Positioned>')
        parts.append('<Positioned left="120" top="80" width="160" height="120"><Container width="160" height="120" color="#0000FF"/></Positioned>')
        parts.append('</Stack></Opacity></Positioned>')
    elif i == 2:
        parts.append(stripes(320, 240)); parts.append(card_sharp())
    elif i == 3:
        parts.append(stripes(320, 240)); parts.append(card_blur())
    elif i == 4:
        parts.append(filter_scene(False))
    elif i == 5:
        parts.append(filter_scene(True))
    parts.append(END)

parts.append('<Positioned left="200" top="742"><Row crossAxisAlignment="END">' + T("观察记录 / WHAT TO LOOK AT", 16, "#2563EB", True, ' letterSpacing="1.5"') + '<SizedBox width="14"/>' + T("说明写在实验区外；所有区域 320×240 白底", 18, "#64748B") + '</Row></Positioned>')
captions = [
    ("①", "alpha 叠加", "红/蓝各自 50% alpha，按红→蓝→白底顺序合成；重叠处理论为 (127,63,191)。"),
    ("②", "组不透明度", "不透明红蓝先在 Opacity 0.5 组内合成，再整体叠白底；样本理论为 (128,128,255)。"),
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
p2 = (128, 128, 255)
audit = {
    "schema_version": 1, "task_id": "A10", "path_base": "output_dir",
    "canvas": [W, H],
    "cells": [{"index": i + 1, "label": labels[i], "origin_px": list(origins[i]), "size": [CW, CH]} for i in range(6)],
    "alpha_math": {
        "sample_local": [180, 100],
        "alpha_128_over_255": a,
        "cell1_steps": {"red_over_white": [round(v, 6) for v in r1],
                        "blue_over_result": [round(v, 6) for v in r2],
                        "rounded": list(p1)},
        "cell2_steps": {"opaque_group_content_at_sample": [0, 0, 255],
                        "group_opacity": 0.5, "over_white": [127.5, 127.5, 255.0],
                        "rounded": list(p2)},
        "difference": "128/255 作用于每次绘制；0.5 作用于已合成的整组。",
        "rounding": "floor(value+0.5)", "tolerance_per_channel": 3
    },
    "filter_params": {"sigmaX": 6, "sigmaY": 6, "card": [240, 160], "card_radius": 20,
                      "color_filter": "#F6B94A", "blend_mode": "MULTIPLY",
                      "clip_circle": {"center_local": [160, 120], "radius": 100},
                      "card_local_origin": [40, 40], "text_size": 24},
    "pair_sharing": {
        "cell3_4": {"shared": ["条纹颜色/宽度/相位", "卡片位置/尺寸/圆角", "文字", "前景形状", "绘制层次"],
                    "only_change": "模糊作用于背景（3）或整卡子树（4）"},
        "cell5_6": {"shared": ["基础场景", "MULTIPLY", "sigma 6", "阴影", "位置与颜色"],
                    "only_change": "⑥增加 ClipOval r100 at (160,120)"}
    },
    "visual_checks": []
}
(OUT / "composite-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
print("wrote A10", len(dsl), "theoretical", p1, p2)
