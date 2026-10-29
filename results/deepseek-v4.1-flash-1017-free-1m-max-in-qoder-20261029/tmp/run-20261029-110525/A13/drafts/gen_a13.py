#!/usr/bin/env python3
"""A13 brand system: icon previews, final color/black icons, banner, poster."""
import json, os, sys, html
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN_ID = SCRIPT.parents[2].name
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A13"
TMP = SUITE_ROOT / "tmp" / RUN_ID / "A13"
OUT.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)
(OUT / "previews").mkdir(exist_ok=True)

def esc(s): return html.escape(str(s), quote=False)
def T(txt, size, color="#0B1220", bold=False, extra="", fam="Noto Sans CJK SC"):
    st = ' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="{fam}" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'

CY, BL, AM, INK = "#38BDF8DB", "#2563EBD9", "#F6B94ADB", "#0B1220"

def ring(cx, cy, r, stroke, color, alpha_suffix=""):
    size = 2 * r
    return (f'<Container width="{size}" height="{size}" color="transparent" shape="CIRCLE" border="{stroke} SOLID {color}"/>',
            f'<Positioned left="{cx-r}" top="{cy-r}" width="{size}" height="{size}">', '</Positioned>')

def icon_a(scale=1.0, black=False):
    cols = ["#000000D9", "#000000D9", "#000000D9"] if black else [CY, BL, AM]
    dot = "#000000" if black else INK
    def s(v): return v * scale
    out = ['<Stack alignment="TOP_LEFT"><Container width="{0}" height="{0}" color="transparent"/>'.format(int(512 * scale))]
    for (cx, cy), col in zip([(206, 206), (256, 256), (306, 306)], cols):
        r, stroke = 110, 44
        out.append(f'<Positioned left="{s(cx-r)}" top="{s(cy-r)}" width="{s(2*r)}" height="{s(2*r)}"><Container width="{s(2*r)}" height="{s(2*r)}" color="transparent" shape="CIRCLE" border="{s(stroke)} SOLID {col}"/></Positioned>')
    out.append(f'<Positioned left="{s(256-34)}" top="{s(256-34)}" width="{s(68)}" height="{s(68)}"><Container width="{s(68)}" height="{s(68)}" color="{dot}" shape="CIRCLE"/></Positioned>')
    out.append('</Stack>')
    return "".join(out)

def icon_a_box(x, y, size, black=False):
    sc = size / 512
    return f'<Positioned left="{x}" top="{y}" width="{size}" height="{size}">{icon_a(sc, black)}</Positioned>'

def icon_b():
    # alternative direction: three offset panes with a circular cut-out
    out = ['<Stack alignment="TOP_LEFT"><Container width="512" height="512" color="transparent"/>']
    panes = [(116, 150, "#38BDF8"), (196, 196, "#2563EB"), (276, 242, "#F6B94A")]
    for i, (x, y, c) in enumerate(panes):
        out.append(f'<Positioned left="{x}" top="{y}" width="200" height="200"><Container width="200" height="200" color="{c}" borderRadius="34"/></Positioned>')
    # circular hole via even-odd clip over the top pane only
    out.append('<Positioned left="276" top="242" width="200" height="200"><ClipPath path="M0 0 H200 V200 H0 Z M100 40 A60 60 0 1 0 100 160 A60 60 0 1 0 100 40 Z" viewBox="0 0 200 200" fillRule="EVEN_ODD"><Container width="200" height="200" color="#F6B94A" borderRadius="34"/></ClipPath></Positioned>')
    out.append('</Stack>')
    return "".join(out)

def preview_snapshot(name, body):
    dsl = f'<Snapshot background="transparent" type="png"><Container width="512" height="512"><Stack alignment="TOP_LEFT"><Container width="512" height="512" color="transparent"/>{body}</Stack></Container></Snapshot>'
    (TMP / "previews" / f"{name}.snapshot").write_text(dsl, encoding="utf-8")

if "--finals" not in sys.argv:
    preview_snapshot("preview-a", icon_a())
    preview_snapshot("preview-b", icon_b())
    print("previews written")
    sys.exit(0)

# ---------------- finals ----------------
def color_icon_dsl(black=False):
    return f'<Snapshot background="transparent" type="png"><Container width="512" height="512"><Stack alignment="TOP_LEFT"><Container width="512" height="512" color="transparent"/>{icon_a(1.0, black)}</Stack></Container></Snapshot>'
(OUT / "symbol-color.snapshot").write_text(color_icon_dsl(False), encoding="utf-8")
(OUT / "symbol-black.snapshot").write_text(color_icon_dsl(True), encoding="utf-8")

# banner
BW, BH = 1200, 400
b = [f'<Snapshot background="#0B1220" type="png"><Container width="{BW}" height="{BH}"><Stack alignment="TOP_LEFT"><Container width="{BW}" height="{BH}" color="#0B1220"/>']
b.append('<Positioned left="-160" top="-200" width="620" height="620"><Container width="620" height="620" gradientType="RADIAL" gradientColors="#1D4ED84D,#0B122000" gradientCenter="CENTER" gradientRadius="0.5" borderRadius="999"/></Positioned>')
b.append('<Positioned left="620" top="80" width="620" height="620"><Container width="620" height="620" gradientType="RADIAL" gradientColors="#7C3AED33,#0B122000" gradientCenter="CENTER" gradientRadius="0.5" borderRadius="999"/></Positioned>')
b.append(icon_a_box(56, 66, 268))
b.append('<Positioned left="360" top="80" width="1" height="240"><Container width="1" height="240" color="#334155"/></Positioned>')
b.append('<Positioned left="404" top="78"><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T("叠光", 68, "#FFFFFF", True) + T("Layerlight", 34, "#93C5FD", True, ' letterSpacing="2"') + '<SizedBox height="12"/>' + T("把复杂信息，组织成清晰画面", 26, "#E2E8F0") + '</Column></Positioned>')
b.append('<Positioned right="56" bottom="44"><Row crossAxisAlignment="CENTER"><Container width="10" height="10" color="#38BDF8" shape="CIRCLE"/><SizedBox width="6"/><Container width="10" height="10" color="#2563EB" shape="CIRCLE"/><SizedBox width="6"/><Container width="10" height="10" color="#F6B94A" shape="CIRCLE"/><SizedBox width="10"/>' + T("LAYERLIGHT / 2026", 18, "#64748B", True, ' letterSpacing="2"') + '</Row></Positioned>')
b.append('</Stack></Container></Snapshot>')
(OUT / "brand-banner.snapshot").write_text("\n".join(b), encoding="utf-8")

# poster
PW, PH = 1080, 1350
p = [f'<Snapshot background="#0B1220" type="png"><Container width="{PW}" height="{PH}"><Stack alignment="TOP_LEFT"><Container width="{PW}" height="{PH}" color="#0B1220"/>']
p.append('<Positioned left="120" top="-80" width="900" height="900"><Container width="900" height="900" gradientType="RADIAL" gradientColors="#1D4ED84D,#0B122000" gradientCenter="CENTER" gradientRadius="0.5" borderRadius="999"/></Positioned>')
p.append('<Positioned left="520" top="620" width="760" height="760"><Container width="760" height="760" gradientType="RADIAL" gradientColors="#7C3AED3D,#0B122000" gradientCenter="CENTER" gradientRadius="0.5" borderRadius="999"/></Positioned>')
p.append('<Positioned left="90" top="70"><Row crossAxisAlignment="CENTER"><Container width="8" height="8" color="#38BDF8" shape="CIRCLE"/><SizedBox width="6"/><Container width="8" height="8" color="#2563EB" shape="CIRCLE"/><SizedBox width="6"/><Container width="8" height="8" color="#F6B94A" shape="CIRCLE"/><SizedBox width="10"/>' + T("LAYERLIGHT / BRAND LAUNCH", 16, "#94A3B8", True, ' letterSpacing="2"') + '</Row></Positioned>')
p.append(icon_a_box(290, 190, 500))
p.append('<Positioned left="90" top="760"><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T("叠光", 104, "#FFFFFF", True) + T("Layerlight", 46, "#93C5FD", True, ' letterSpacing="3"') + '<SizedBox height="16"/>' + T("把复杂信息，组织成清晰画面", 32, "#E2E8F0") + '</Column></Positioned>')
p.append('<Positioned left="90" top="1030"><Container padding="(10,20)" color="#F6B94A" borderRadius="999">' + T("OPEN BETA", 24, "#0B1220", True, ' letterSpacing="2"') + '</Container></Positioned>')
p.append('<Positioned left="90" top="1130"><Row crossAxisAlignment="CENTER">' + T("2026.11.07 · ONLINE", 28, "#FFFFFF", True) + '<SizedBox width="20"/>' + T("layerlight.example.org", 24, "#94A3B8") + '</Row></Positioned>')
p.append('<Positioned left="90" top="1240"><Container width="900" height="1" color="#334155"/></Positioned>')
p.append('<Positioned left="90" top="1264">' + T("STRUCTURED VISUAL TOOLS / 结构化视觉工具", 18, "#64748B", True, ' letterSpacing="2"') + '</Positioned>')
p.append('</Stack></Container></Snapshot>')
(OUT / "launch-poster.snapshot").write_text("\n".join(p), encoding="utf-8")

system = {
    "schema_version": 1, "task_id": "A13", "path_base": "output_dir",
    "brand": {"name_cn": "叠光", "name_en": "Layerlight", "concept": "信息叠加后仍然清晰"},
    "colors": {"ink": INK, "cyan": "#38BDF8", "blue": "#2563EB", "amber": "#F6B94A",
               "white": "#FFFFFF", "muted": "#94A3B8"},
    "icon": {
        "geometry": "3 个等半径圆环（r=110, stroke=44, centers (206,206)/(256,256)/(306,306)）+ 1 个中心实心圆点（r=34）",
        "components": [
            {"id": "C1", "type": "ring", "params": {"center": [206, 206], "r": 110, "stroke": 44}, "dsl": "symbol-color.snapshot ring 1"},
            {"id": "C2", "type": "ring", "params": {"center": [256, 256], "r": 110, "stroke": 44}, "dsl": "ring 2"},
            {"id": "C3", "type": "ring", "params": {"center": [306, 306], "r": 110, "stroke": 44}, "dsl": "ring 3"},
            {"id": "C4", "type": "dot", "params": {"center": [256, 256], "r": 34}, "dsl": "center dot"}
        ],
        "component_count": 4, "max_components": 6,
        "negative_space": "每环的内孔由 border 绘制自然形成；中心圆点占据三环交叠处，形成视觉锚点。",
        "clear_space": "图标外缘 0.25r（约 27.5px）内不放其他元素",
        "min_size": "32px；环宽在 32px 时约 2.75px，中心点约 2.1px"
    },
    "variants": {"color": "C1 #38BDF8DB / C2 #2563EBD9 / C3 #F6B94ADB / C4 #0B1220",
                 "black": "全部构件 #000000（含抗锯齿）"},
    "applications": {
        "symbol-color.png": {"size": [512, 512], "use": "彩色透明图标"},
        "symbol-black.png": {"size": [512, 512], "use": "纯黑透明图标；仅作单色场景"},
        "brand-banner.png": {"size": [1200, 400], "use": "横向品牌横幅；图标 + 中英字标 + 口号"},
        "launch-poster.png": {"size": [1080, 1350], "use": "发布海报；纵向独立构图，非横幅缩放"}
    },
    "ratio": {"icon_to_banner_height": 268 / 400, "icon_to_poster_height": 500 / 1350,
              "wordmark_cn_banner": 68, "wordmark_cn_poster": 104}
}
(OUT / "brand-system.json").write_text(json.dumps(system, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "rationale.md").write_text("""# 叠光 / Layerlight · 方向说明

两个方向：A 用三个交叠圆环与中心点，表达“多层叠加仍保留清晰边界”；B 用错位圆角方块与一个圆形负空间，偏“实体叠片”。

实际预览后选择 A：在 32×32 下三环的交叠关系仍可辨认，中心点提供稳定锚点；B 的三块实心在该尺寸更易糊成一体。

小尺寸改进：把环宽从 44 保持为比例值、中心点加大到 r=34；色环使用轻微 alpha 让交叠处出现深浅变化，但轮廓不依赖透明。横幅与海报复用同一几何规则，海报采用纵向独立构图。
""", encoding="utf-8")
print("finals written")
