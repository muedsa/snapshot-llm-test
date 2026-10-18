"""A13 · Layerlight brand system — previews, icons, banner, poster."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A13"
TMP = ROOT / "tmp" / RUN / TASK
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v001"
MODE = sys.argv[2] if len(sys.argv) > 2 else "all"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from dsl import C, Col, Gap, HGap, Label, Pos, Row, SizedBox, Stack, T, polygon  # noqa: E402

INK = "#0B1220"
PAPER = "#F4F1E9"
CYAN = "#22D3EE"
VIOLET = "#8B5CF6"
AMBER = "#F59E0B"
CORAL = "#F97362"
MUTED = "#93A6C2"
LINE = "#22314B"


def logo_a(x, y, s, black=False, mono=False):
    """Five primary primitives: 3 bars + 1 ring + 1 dot."""
    bar_colors = ["#000000"] * 3 if black else [CYAN, VIOLET, AMBER]
    alphas = ["FF", "FF", "FF"]
    bars = [(64, 150, 300, 56), (96, 224, 300, 56), (128, 298, 300, 56)]
    out = []
    for (bx, by, bw, bh), col, a in zip(bars, bar_colors, alphas):
        out.append(Pos(x + bx * s, y + by * s, C(width=bw * s, height=bh * s,
                                                  color=col + a, borderRadius=24 * s)))
    ring = "#000000" if black else CORAL
    out.append(Pos(x + 256 * s, y + 156 * s, C(width=200 * s, height=200 * s, color="transparent",
                                               border=f"{30*s} SOLID {ring}", borderRadius=100 * s)))
    out.append(Pos(x + 356 * s - 18 * s, y + 256 * s - 18 * s,
                   C(width=36 * s, height=36 * s, color="#000000" if black else INK, borderRadius=18 * s)))
    return out


def preview_a():
    return (f'<Snapshot type="png" background="#00000000"><Container width="512" height="512">'
            + Stack([SizedBox(512, 512)] + logo_a(0, 0, 1), width=512, height=512)
            + "</Container></Snapshot>\n")


def preview_b():
    # four primitives: two rotated beams + one diamond + one dot
    beam1 = ('<Transform matrix="(0.707107,0.707107,0,0,-0.707107,0.707107,0,0,0,0,1,0,0,0,0,1)" alignment="CENTER">'
             + C(width=300, height=58, color=CORAL + "E6", borderRadius=29) + "</Transform>")
    beam2 = ('<Transform matrix="(0.707107,-0.707107,0,0,0.707107,0.707107,0,0,0,0,1,0,0,0,0,1)" alignment="CENTER">'
             + C(width=300, height=58, color=CYAN + "D9", borderRadius=29) + "</Transform>")
    diamond = ('<Transform matrix="(0.707107,-0.707107,0,0,0.707107,0.707107,0,0,0,0,1,0,0,0,0,1)" alignment="CENTER">'
               + C(width=120, height=120, color=AMBER + "E6", borderRadius=12) + "</Transform>")
    return (f'<Snapshot type="png" background="#00000000"><Container width="512" height="512">'
            + Stack([SizedBox(512, 512),
                     Pos(106, 227, beam1, w=300, h=58),
                     Pos(106, 227, beam2, w=300, h=58),
                     Pos(196, 196, diamond, w=120, h=120),
                     Pos(238, 238, C(width=36, height=36, color=INK, borderRadius=18))], width=512, height=512)
            + "</Container></Snapshot>\n")


def banner():
    nodes = [SizedBox(1200, 400),
             Pos(0, 0, C(width=1200, height=400, gradientType="LINEAR",
                         gradientColors="#0B1220,#101E33", gradientBegin="TOP_LEFT", gradientEnd="BOTTOM_RIGHT"))]
    for i in range(6):
        nodes.append(Pos(60 + i * 200, 0, C(width=1, height=400, color="#16243A")))
    nodes += logo_a(64, 72, 0.5)
    nodes += [
        Pos(360, 118, T("叠光", size=58, color="#F8FAFC", weight="BOLD", family="Noto Serif CJK SC,Inter")),
        Pos(500, 132, T("Layerlight", size=44, color=CORAL, weight="BOLD", family="Inter")),
        Gap(0),
        Pos(360, 200, T("把复杂信息，组织成清晰画面", size=27, color="#D9E4F2")),
        Pos(360, 250, T("STRUCTURED VISUAL TOOLS", size=15, color=MUTED, family="Inter", spacing=3)),
        Pos(64, 340, T("LAYERLIGHT / BRAND SYSTEM", size=14, color="#5F7290", family="Inter", spacing=2)),
        Pos(1000, 332, T("2026.11.07 · ONLINE", size=16, color=MUTED, family="Inter")),
    ]
    return f'<Snapshot type="png" background="{INK}">\n' + Stack(nodes, width=1200, height=400) + "\n</Snapshot>\n"


def poster():
    nodes = [SizedBox(1080, 1350),
             Pos(0, 0, C(width=1080, height=1350, gradientType="LINEAR",
                         gradientColors="#07101E,#0D1A2E,#111E33", gradientBegin="TOP_CENTER", gradientEnd="BOTTOM_CENTER"))]
    for i in range(10):
        nodes.append(Pos(40 + i * 112, 0, C(width=1, height=1350, color="#152338")))
    nodes.append(Pos(0, 0, polygon(1080, 1350, [(820, 0), (1080, 0), (1080, 260), (620, 0)], CORAL + "18")))
    nodes += logo_a(382, 120, 0.62)
    nodes += [
        Pos(64, 470, T("叠光", size=96, color="#F8FAFC", weight="BOLD", family="Noto Serif CJK SC,Inter")),
        Pos(64, 590, T("Layerlight", size=44, color=CORAL, weight="BOLD", family="Inter", spacing=1)),
        Pos(64, 660, T("把复杂信息，组织成清晰画面", size=30, color="#D9E4F2")),
        Pos(64, 730, C(width=220, height=2, color=CORAL)),
        Pos(64, 770, T("2026.11.07 · ONLINE", size=24, color=MUTED, family="Inter")),
        Pos(64, 826, C(width=164, height=42, color=CORAL + "22", borderRadius=21, border="1 SOLID " + CORAL,
                       alignment="CENTER", child=T("OPEN BETA", size=18, color=CORAL, weight="BOLD", family="Inter", spacing=2))),
        Pos(64, 900, T("layerlight.example.org", size=24, color="#7DD3FC", family="Inter")),
        Pos(64, 960, T("信息叠加之后，画面仍然清晰。", size=20, color="#5F7290")),
        Pos(64, 1260, T("LAYERLIGHT · STRUCTURED VISUAL TOOLS", size=15, color="#5F7290", family="Inter", spacing=2)),
        Pos(820, 1260, T("01 / 01", size=15, color="#5F7290", family="Inter")),
    ]
    return f'<Snapshot type="png" background="{INK}">\n' + Stack(nodes, width=1080, height=1350) + "\n</Snapshot>\n"


def black_icon():
    return (f'<Snapshot type="png" background="#00000000"><Container width="512" height="512">'
            + Stack([SizedBox(512, 512)] + logo_a(0, 0, 1, black=True), width=512, height=512)
            + "</Container></Snapshot>\n")


def brand_system():
    return {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "brand": {"name_zh": "叠光", "name_en": "Layerlight",
                  "concept": "信息叠加后仍然清晰", "category": "结构化视觉工具"},
        "colors": {"ink": INK, "cyan": CYAN, "violet": VIOLET, "amber": AMBER, "coral": CORAL,
                   "paper": PAPER, "muted": MUTED},
        "proportions": {"icon_canvas": [512, 512], "safe_area": 56, "ring_outer": 200,
                        "ring_border": 30, "bar_height": 56, "bar_radius": 24,
                        "clear_space_rule": "图标外接框到画布边至少 56px；横幅/海报按 0.5/0.62 等比复用同一几何规则"},
        "icon_components": [
            {"id": "C1", "primitive": "rounded bar", "instance": 1, "params": "x64 y150 w300 h56 r24", "color": CYAN + "EB",
             "negative_space": "none", "dsl": "logo_a bar[0]"},
            {"id": "C2", "primitive": "rounded bar", "instance": 2, "params": "x96 y224 w300 h56 r24", "color": VIOLET + "D9",
             "negative_space": "none", "dsl": "logo_a bar[1]"},
            {"id": "C3", "primitive": "rounded bar", "instance": 3, "params": "x128 y298 w300 h56 r24", "color": AMBER + "E6",
             "negative_space": "none", "dsl": "logo_a bar[2]"},
            {"id": "C4", "primitive": "ring", "instance": 1, "params": "center(356,256) outerD200 border30", "color": CORAL,
             "negative_space": "inner hole d=140; generated by border ring, not an extra component", "dsl": "logo_a ring"},
            {"id": "C5", "primitive": "dot", "instance": 1, "params": "center(356,256) r18", "color": INK,
             "negative_space": "none", "dsl": "logo_a dot"},
        ],
        "component_count": 5,
        "component_count_reason": "3 个独立圆角条 + 1 个圆环 + 1 个圆点 = 5；圆环内孔为扣除负空间，不另计；分组、位移、缩放不计数。",
        "small_size_check": {"size": [32, 32], "method": "premultiplied alpha + Lanczos + unpremultiply",
                             "previews": ["tmp/%s/A13/previews/symbol-color-32.png" % RUN,
                                          "tmp/%s/A13/previews/symbol-black-32.png" % RUN]},
        "applications": {
            "symbol_color": {"file": "symbol-color.png", "size": [512, 512], "background": "transparent",
                             "geometry": "logo_a(0,0,1)"},
            "symbol_black": {"file": "symbol-black.png", "size": [512, 512], "background": "transparent",
                             "geometry": "logo_a(0,0,1,black=True)", "rule": "all alpha>0 pixels RGB=0"},
            "brand_banner": {"file": "brand-banner.png", "size": [1200, 400],
                             "geometry": "logo_a(64,72,0.5)", "texts": ["叠光 Layerlight", "把复杂信息，组织成清晰画面"]},
            "launch_poster": {"file": "launch-poster.png", "size": [1080, 1350],
                              "geometry": "logo_a(382,120,0.62)", "texts": ["叠光 Layerlight", "把复杂信息，组织成清晰画面",
                                                                            "2026.11.07 · ONLINE", "OPEN BETA", "layerlight.example.org"]},
        },
        "anti_copy_rule": "两应用均由 logo_a 几何函数重新生成 DSL，未嵌入 symbol PNG。",
    }


def main() -> int:
    (TMP / "previews").mkdir(parents=True, exist_ok=True)
    (TMP / "dsl" / "preview-a").mkdir(parents=True, exist_ok=True)
    (TMP / "dsl" / "preview-b").mkdir(parents=True, exist_ok=True)
    (TMP / "dsl" / "symbol-color").mkdir(parents=True, exist_ok=True)
    (TMP / "dsl" / "symbol-black").mkdir(parents=True, exist_ok=True)
    (TMP / "dsl" / "banner").mkdir(parents=True, exist_ok=True)
    (TMP / "dsl" / "poster").mkdir(parents=True, exist_ok=True)
    (TMP / "dsl" / "preview-a" / f"{VERSION}.snapshot").write_text(preview_a(), encoding="utf-8")
    (TMP / "dsl" / "preview-b" / f"{VERSION}.snapshot").write_text(preview_b(), encoding="utf-8")
    (TMP / "dsl" / "symbol-color" / f"{VERSION}.snapshot").write_text(preview_a(), encoding="utf-8")
    (TMP / "dsl" / "symbol-black" / f"{VERSION}.snapshot").write_text(black_icon(), encoding="utf-8")
    (TMP / "dsl" / "banner" / f"{VERSION}.snapshot").write_text(banner(), encoding="utf-8")
    (TMP / "dsl" / "poster" / f"{VERSION}.snapshot").write_text(poster(), encoding="utf-8")
    (TMP / "brand-system.json").write_text(json.dumps(brand_system(), ensure_ascii=False, indent=2), encoding="utf-8")
    (TMP / "rationale.md").write_text(
        "# 方向选择与迭代说明\n\n"
        "方向 A 用三条水平圆角条与一个珊瑚圆环相交，表达“多层信息叠合后仍被清晰框定”；方向 B 用两条对角梁与菱形构成棱镜，动势更强但 32px 下斜线变细、负空间难辨。实际预览后选 A：横条与圆环的正交关系在小尺寸仍保留 3 层与 1 个孔径，识别稳定。小尺寸改进：条高 56、环宽 30、点径 36，预览 32px 时仍能读出层数与圆孔；清空图标外 56px 留白，黑版全部形状用 #000000 与 alpha 边缘。\n",
        encoding="utf-8")
    print("A13", VERSION, MODE, "written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
