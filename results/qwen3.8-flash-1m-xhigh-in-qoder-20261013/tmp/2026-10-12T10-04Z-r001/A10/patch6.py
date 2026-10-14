"""A10 patch 6 — final prose, measured values on the board, and audit geometry.

Everything written here as an observation was read off tmp/<run>/A10/v004.png by
verify.py, not assumed: gradient 1.13/15.64 for ③, 1.71/2.13 for ④, 8.6 outside both
cards, tint spread 23px right / 7px up for ⑤, and channel jumps of 218/228 at
dx 97→98 and 99→100 for ⑥. verify.py re-measures the delivered PNG and overwrites
group_A.measured, so the board and the audit cannot silently disagree.
"""
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
p = ROOT / "tmp" / RUN / "A10" / "gen.py"
s = p.read_text(encoding="utf-8")
orig = s


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new, count)


# ---------------------------------------------------------------- board version tag
rep('SIGMA = 6', 'SIGMA = 6\nVER = os.environ.get("A10_BOARD_VER", "v005")   # version shown in the evidence panel')

# ---------------------------------------------------------------- shared 5/6 geometry
rep('''def scene_56():
    """Shared base scene for the ⑤/⑥ pair, in scene-box local coordinates.

    Deliberately carries no background fill: the white cell must stay visible, and the
    transparent gaps between the shapes are what ColorFiltered is expected to tint.
    """
    return Stack(
        C(width=num(SB_W), height=num(SB_H)),
        # blue bar: nearest corner sits inside r=100, far corner at distance 158
        Positioned(C(width="130", height="60", color="#2E7DD1"), left="6", top="4"),
        # dark rectangle whose outer corner leaves the circle
        Positioned(C(width="90", height="55", color="#16233C"), left="176", top="124"),
        # card with a drop shadow, fully inside the circle
        Positioned(
            C(width="120", height="70", color="#FFFFFF", borderRadius="10",
              border="2 SOLID #9AA9BF", boxShadow="0 6 14 0 #00000066 NORMAL"),
            left="71", top="73"),
        # red dot straddling the circumference (centre distance 116, radius 23)
        Positioned(C(width="46", height="46", color="#E24C4C", shape="CIRCLE"),
                   left="211", top="13"),
        alignment="TOP_LEFT", clipBehavior="NONE",
    )''',
    '''# kind, scene-box xywh, colour, area-local xywh, crosses r=100 circle, why
SHAPES_56 = [
    ("rect", 6, 4, 130, 60, "#2E7DD1", [30, 30, 130, 60], True,
     "远角距圆心 158>100、近角 30<100，必跨圆周"),
    ("rect", 176, 124, 90, 55, "#16233C", [200, 150, 90, 55], True,
     "内角距圆心 50<100、外角 155>100，跨圆周"),
    ("card_with_shadow", 71, 73, 120, 70, "#FFFFFF", [95, 95, 120, 70], False,
     "四角距圆心最大 71<100，完全在圆内；阴影 0 6 14 0 #00000066 NORMAL"),
    ("circle", 211, 13, 46, 46, "#E24C4C", [235, 35, 46, 46], True,
     "圆心距 116、半径 23，93<100<139，横跨圆周"),
]


def scene_56():
    """Shared base scene for the ⑤/⑥ pair, in scene-box local coordinates.

    Deliberately carries no background fill: the white cell must stay visible, and the
    transparent gaps between the shapes are what ColorFiltered is expected to tint.
    """
    kids = []
    for kind, x, y, w, h, col, _al, _cr, _why in SHAPES_56:
        attrs = {"width": num(w), "height": num(h), "color": col}
        if kind == "circle":
            attrs["shape"] = "CIRCLE"
        if kind == "card_with_shadow":
            attrs.update({"borderRadius": "10", "border": "2 SOLID #9AA9BF",
                          "boxShadow": "0 6 14 0 #00000066 NORMAL"})
        kids.append(Positioned(C(**attrs), left=num(x), top=num(y)))
    return Stack(C(width=num(SB_W), height=num(SB_H)), *kids,
                 alignment="TOP_LEFT", clipBehavior="NONE")''')

# ---------------------------------------------------------------- captions
rep('"BackdropFilter 只糊卡下条纹，字仍锐利"', '"BackdropFilter 只糊卡下条纹"')
rep('"MULTIPLY 后 sigma=6，间隙被填、边缘外溢"', '"MULTIPLY 后 sigma=6，间隙被填并外溢"')

# ---------------------------------------------------------------- panel prose
rep('''                 "都只剩白底回补出的 128。", 17, TXT_2, FONT, lh=1.3))''',
    '''                 "都只剩白底回补出的 128。", 17, TXT_2, FONT, lh=1.3))
y += 4 * 17 * 1.3 + 8
colA.append(flow(1, LX, CWS, y,
                 f"实测 {VER}：① (127,63,191) 逐通道误差 0；② (126,126,255) 误差 2，"
                 "来自组透明度在 8 位离屏层里的量化与预乘取整；未改采样值，也未后处理图片。",
                 17, "#8FE3B0", MONO))''')

rep('''                 "③ 卡内 240×160 区域的条纹糊成竖向色带，SHARP 二字与深色小方块的边缘仍然"
                 "锐利；④ 同一位置改为子树模糊后，BLUR 文字与方块一起糊开，卡片自身的圆角边"
                 "也变软。两格卡片外的条纹同样清晰，差别只落在模糊所作用的那一层。",''',
    '''                 "③ 卡内条纹已糊成色带（水平梯度 1.13），SHARP 文字与深色方块仍锐利（15.64）；"
                 "④ 同一区域条纹 1.71、文字 2.13 一起糊开，卡片圆角边也变软。两格卡外条纹梯度"
                 "同为 8.6，说明底场景一致，差别只落在模糊所作用的那一层。",''')

rep('''                 "⑤ 乘色 #F6B94A 后整片变橙并 sigma=6 模糊，柔化边缘越出原形状与实验区外框，"
                 "在深色底上形成橙色外溢光晕；⑥ 同一结果套 r=100 圆裁后，圆周处出现锐利"
                 "截断线，跨过圆周的绿色矩形被整齐切掉，圆外不再有任何橙色扩散。",''',
    '''                 "⑤ 白卡转橙、形状之间的透明间隙被 #F6B94A 填成橙色，sigma=6 让场景外框边缘"
                 "向右扩散 23px、向上 7px，实验区白底与 1px 边框仍完整；⑥ 加 r=100 圆裁后，"
                 "沿圆心向右取样在 dx 97→98、99→100 出现 218/228 的通道跳变，圆内 (246,185,74)、"
                 "圆外纯白，跨圆的蓝条与红点在弧上被整齐切断。",''')

# ---------------------------------------------------------------- audit
rep('''            "shapes": [
                {"kind": "rect", "xywh": [20, 20, 120, 60], "colour": "#2E7DD1",
                 "crosses_circle": True,
                 "why": "圆为局部圆心 (160,120) 半径 100，即 x∈[60,260]、y∈[20,220]；"
                        "该矩形 x 从 20 到 140，跨过圆周左侧"},
                {"kind": "rect", "xywh": [200, 150, 90, 60], "colour": "#16233C"},
                {"kind": "card_with_shadow", "xywh": [90, 95, 120, 70],
                 "colour": "#FFFFFF", "boxShadow": "0 6 14 0 #00000066 NORMAL"},
                {"kind": "circle", "xywh": [240, 30, 46, 46], "colour": "#E24C4C",
                 "crosses_circle": True},
            ],
            "transparent_gaps": "白底之外未覆盖的区域，用于观察 MULTIPLY 对间隙着色",''',
    '''            "scene_box": [SB_X, SB_Y, SB_W, SB_H],
            "shapes": [
                {"kind": k, "scene_box_xywh": [x, y, w, h], "area_local_xywh": al,
                 "colour": col, "crosses_circle": cr, "why": why}
                for k, x, y, w, h, col, al, cr, why in SHAPES_56
            ],
            "circle_domain": "圆心局部 (160,120)、半径 100，即 x∈[60,260]、y∈[20,220]",
            "transparent_gaps": "场景框内形状之间未覆盖的区域，用于观察 MULTIPLY 对间隙着色；"
                                "场景框本身不带底色，白底来自实验区",''')

rep('''            "3_text_sharp": None, "3_background_blurred": None, "3_effect_leaks_out": None,
            "4_text_sharp": None, "4_background_blurred": None, "4_effect_leaks_out": None,
            "basis": "见 image_views 与 zoom 图；由实际放大观察填写",''',
    '''            "3_text_sharp": True, "3_background_blurred": True, "3_effect_leaks_out": False,
            "4_text_sharp": False, "4_background_blurred": True, "4_effect_leaks_out": False,
            "observed_in": "v004",
            "gradients": {"3_stripe_row": 1.13, "3_text_row": 15.64,
                          "4_stripe_row": 1.71, "4_text_row": 2.13,
                          "outside_card_3": 8.6, "outside_card_4": 8.6},
            "basis": "在 v004.png 上取卡内 y∈[50,74] 与文字行 y∈[98,122] 的水平一阶差分均值；"
                     "整图与局部放大见 image_views.jsonl 与 zoom-*.png",''')

rep('''            "5_spills_beyond_shapes": None, "5_circle_boundary_visible": False,
            "6_spills_beyond_shapes": None, "6_circle_boundary_sharp": None,
            "basis": "见 image_views 与 zoom 图；由实际放大观察填写",''',
    '''            "5_gap_filled_by_tint": True, "5_spills_beyond_shapes": True,
            "5_spread_px": {"right": 23, "up": 7}, "5_cell_border_intact": True,
            "6_spills_beyond_shapes": False, "6_circle_boundary_sharp": True,
            "6_circle_scan": {"inside_dx80_rgb": [246, 185, 74],
                              "outside_dx120_rgb": [255, 255, 255],
                              "jumps": [{"dx": "97→98", "max_channel_delta": 218},
                                        {"dx": "99→100", "max_channel_delta": 228}]},
            "observed_in": "v004",
            "basis": "沿 ⑥ 圆心局部 (160,120) 向右逐像素取样到 dx=120；⑤ 从场景框右缘与上缘"
                     "向外找首个与纯白最大通道差 >3 的位置",''')

assert s != orig
p.write_text(s, encoding="utf-8")
print("patched 6")
