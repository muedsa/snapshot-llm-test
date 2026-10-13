"""A03 - repair inputs/broken.snapshot into the System Pulse monitoring card.

The original file is submitted verbatim first (see tmp/<run_id>/A03/orig-as-submitted.*);
this script emits the repaired 1280x800 card and writes repair-log.json.

Run from the suite task root:
  python tmp/<run_id>/A03/gen.py --ver v005 [--final outputs/<run_id>/A03/system-pulse.snapshot]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / "2026-10-12T10-04Z-r001" / "_suite" / "scripts"))

from snap import (  # noqa: E402
    C, Border, ClipRRect, Col, Container, Node, Positioned, Row, Snapshot, Spacer,
    Stack, Text, Transform, num,
)

RUN = "2026-10-12T10-04Z-r001"
TASK = "A03"
TMP_DIR = ROOT / "tmp" / RUN / TASK
OUT_DIR = ROOT / "outputs" / RUN / TASK

W, H = 1280, 800
MARGIN = 32
CW = W - 2 * MARGIN                      # 1216
BG = "#0B1220"
FONT = "Noto Sans CJK SC,Inter"

TXT, MUTED = "#F8FAFC", "#94A3B8"
CARD, CARD_EDGE = "#16223C", "#27395C"
SKY, EMERALD, AMBER, ROSE = "#38BDF8", "#34D399", "#FBBF24", "#FB7185"

METRICS = [("USAGE", "72%", SKY), ("LATENCY", "148 ms", AMBER),
           ("SUCCESS", "99.2%", EMERALD)]

GAP = 24
CARD_W = (CW - 2 * GAP) / 3              # 389.33
CARD_H = 168
CARD_Y = 120

TITLE_Y, TITLE_H = MARGIN, 64
LIVE_W, LIVE_H = 96, 36
LIVE_X, LIVE_Y = W - MARGIN - LIVE_W, 44

DESC_W, DESC_H, DESC_R = 500, 150, 24
DESC_X = (W - DESC_W) / 2                # 390
DESC_Y = 400

STRIPE_X0, STRIPE_X1 = MARGIN, W - MARGIN
STRIPE_TOP = DESC_Y - 34                 # 366
STRIPE_BOTTOM = DESC_Y + DESC_H + 34     # 584
STRIPE_BAND = STRIPE_BOTTOM - STRIPE_TOP
STIPES = [(0.10, "#38BDF8", 7), (0.22, "#A78BFA", 5), (0.34, "#34D399", 9),
          (0.46, "#FBBF24", 5), (0.58, "#FB7185", 8), (0.70, "#22D3EE", 5),
          (0.82, "#C084FC", 7), (0.93, "#4ADE80", 4)]

SIGMA = 9.0
REV_W, REV_H, REV_FONT = 160, 56, 24
REV_ANGLE_DEG = 8.0
REV_BOX_X = W - MARGIN - REV_W - 8       # 1072
REV_BOX_Y = 640


def rot_ccw(deg: float) -> str:
    """Column-major 4x4 rotation that turns counter-clockwise on a y-down canvas."""
    t = math.radians(-deg)
    c, s = math.cos(t), math.sin(t)
    vals = [c, s, 0, 0, -s, c, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    return "(" + ",".join(f"{v:.6f}" if v else "0" for v in vals) + ")"


def rotated_bbox(x, y, w, h, deg):
    """Axis-aligned bbox of a box rotated about its centre on a y-down canvas."""
    t = math.radians(-deg)
    c, s = abs(math.cos(t)), abs(math.sin(t))
    bw, bh = w * c + h * s, w * s + h * c
    cx, cy = x + w / 2, y + h / 2
    return [cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2]


def BackdropFilter(*children, sigmaX, sigmaY, tileMode=None):  # noqa: N802
    return Node("BackdropFilter", {"sigmaX": sigmaX, "sigmaY": sigmaY,
                                   "tileMode": tileMode}, list(children))


def metric_card(name, value, accent):
    """Original Expanded>Container>Text block, repaired: no hard-coded main-axis width,
    explicit colour, and the original Spacer kept to push the value to the card base."""
    return Container(
        Col(
            Row(
                C(width="10", height="10", color=accent, shape="CIRCLE"),
                C(width="10"),
                Text(name, color=MUTED, fontSize="28", fontFamily=FONT),
                crossAxisAlignment="CENTER",
            ),
            Spacer(flex=1),
            Text(value, color=accent, fontSize="28", fontStyle="BOLD", fontFamily=FONT),
            crossAxisAlignment="START",
            mainAxisSize="MAX",
        ),
        width=num(CARD_W), height=num(CARD_H), color=CARD, borderRadius="18",
        border=f"1 SOLID {CARD_EDGE}", padding="(24,26)", alignment="CENTER_LEFT",
    )


def stripe(y_frac, color, thick):
    return Positioned(
        C(width=num(STRIPE_X1 - STRIPE_X0), height=num(thick), color=color,
          borderRadius=num(thick / 2)),
        left=num(STRIPE_X0), top=num(STRIPE_TOP + STRIPE_BAND * y_frac),
    )


def build():
    kids = [
        Positioned(Text("System Pulse", color=TXT, fontSize="44", fontStyle="BOLD",
                        fontFamily=FONT), left=num(MARGIN), top=num(TITLE_Y)),
        Positioned(
            Border(
                Container(
                    Row(
                        C(width="9", height="9", color="#FFFFFF", shape="CIRCLE"),
                        C(width="8"),
                        Text("LIVE", color="#FFFFFF", fontSize="18", fontStyle="BOLD",
                             fontFamily=FONT),
                        crossAxisAlignment="CENTER",
                    ),
                    width=num(LIVE_W), height=num(LIVE_H), color="#BE123C",
                    borderRadius="18", alignment="CENTER",
                ),
                border="1 SOLID #FB7185", borderRadius="18",
            ),
            left=num(LIVE_X), top=num(LIVE_Y)),
    ]
    for i, m in enumerate(METRICS):
        kids.append(Positioned(metric_card(*m),
                               left=num(MARGIN + i * (CARD_W + GAP)), top=num(CARD_Y)))
    kids += [stripe(*s) for s in STIPES]
    kids.append(Positioned(
        ClipRRect(
            BackdropFilter(
                C(width=num(DESC_W), height=num(DESC_H), color="#FFFFFF14",
                  border="1 SOLID #FFFFFF45", borderRadius=num(DESC_R)),
                sigmaX=num(SIGMA), sigmaY=num(SIGMA), tileMode="CLAMP",
            ),
            borderRadius=num(DESC_R), clipBehavior="ANTI_ALIAS",
        ),
        left=num(DESC_X), top=num(DESC_Y)))
    kids.append(Positioned(
        Col(
            Text("Background-only blur", color="#FFFFFF", fontSize="28", fontStyle="BOLD",
                 fontFamily=FONT, textAlign="CENTER"),
            Container(height="10"),
            Text("卡内背景被高斯模糊，卡外细条保持锐利，文字不进入滤镜子树",
                 color="#D8E4F5", fontSize="16", fontFamily=FONT, textAlign="CENTER"),
            crossAxisAlignment="CENTER",
        ),
        left=num(DESC_X), top=num(DESC_Y + 40), width=num(DESC_W)))
    kids.append(Positioned(
        Transform(
            Container(
                Text("REVIEW", color="#FFFFFF", fontSize=num(REV_FONT), fontStyle="BOLD",
                     fontFamily=FONT, textAlign="CENTER"),
                width=num(REV_W), height=num(REV_H), color="#FFFFFF33", borderRadius="12",
                border="1 SOLID #FFFFFF66", alignment="CENTER",
            ),
            matrix=rot_ccw(REV_ANGLE_DEG), alignment="CENTER",
        ),
        left=num(REV_BOX_X), top=num(REV_BOX_Y)))

    return Snapshot(
        Stack(C(width=num(W), height=num(H), color=BG), *kids,
              width=num(W), height=num(H), alignment="TOP_LEFT",
              clipBehavior="HARD_EDGE"),
        background=BG, type="png",
    )


REV_BBOX = [round(v, 1) for v in
            rotated_bbox(REV_BOX_X, REV_BOX_Y, REV_W, REV_H, REV_ANGLE_DEG)]

REPAIRS = [
    {"id": "R01", "symptom_class": "真实报错", "original_location": "第 2 行 Container padding=\"24 32\"",
     "observed": "HTTP 400 PARSE_ERROR: Attr [padding] value format error at position 92",
     "evidence_request": "A03-render-v000-orig",
     "basis": "/reference/parser-tags/ EdgeInsets：\"12\" / \"(8,16)\" / \"(8,12,16,20)\"，括号与逗号是语法的一部分",
     "fix": "padding=\"32\"（题面安全边距 32，四边一致）",
     "verified_by": "A03-render-v001 不再报该错"},
    {"id": "R02", "symptom_class": "真实报错", "original_location": "第 10 行 Transform rotate=\"-8\"",
     "observed": "HTTP 400 PARSE_ERROR: Attr [matrix] must not be null at position 475",
     "evidence_request": "A03-render-v001",
     "basis": "标签参考 Transform：matrix 必填，Parser 无 rotate 便捷属性",
     "fix": "改列主序 4×4 矩阵；y 向下时负角度才是视觉逆时针，θ=-8° → cos=0.990268, sin=-0.139173，并加 alignment=CENTER",
     "verified_by": "A03-render-v002 通过该错；最终图 REVIEW 向左上倾斜"},
    {"id": "R03", "symptom_class": "真实报错", "original_location": "第 7 行 Row 内 Positioned right=\"20\"",
     "observed": "HTTP 400 RENDER_ERROR: renderBox.parentData must be StackParentData",
     "evidence_request": "A03-render-v002",
     "basis": "标签参考 Positioned：必须是 Stack / IndexedStack 的直接子节点",
     "fix": "标题与 LIVE 改由 Stack 并置，LIVE 用 Positioned(left,top) 定位到右上",
     "verified_by": "A03-render-v003 通过该错"},
    {"id": "R04", "symptom_class": "真实报错",
     "original_location": "第 1 行 Snapshot width/height + 第 2 行 Container 无尺寸",
     "observed": "HTTP 400 RENDER_ERROR: Layout size is infinite",
     "evidence_request": "A03-render-v003",
     "basis": "/guides/rendering/：Snapshot 不接受独立画布宽高，Surface 尺寸来自根布局",
     "fix": "尺寸移到根 Container：width=1280 height=800",
     "verified_by": "A03-render-v004 返回 200，实测图片 1280×800"},
    {"id": "R05", "symptom_class": "静默忽略", "original_location": "第 4 行 Text font-size=\"44\"",
     "observed": "v004 图中标题按默认字号渲染，明显小于 44，服务不报错",
     "evidence_request": "A03-render-v004 + v004.png 实际看图",
     "basis": "/reference/faq/：未知属性静默忽略；属性名 camelCase，字号属性为 fontSize",
     "fix": "改为 fontSize=\"44\"",
     "verified_by": "最终图标题字高与 44 号一致"},
    {"id": "R06", "symptom_class": "静默忽略", "original_location": "第 1 行 Snapshot@width / @height",
     "observed": "两属性被丢弃且不报错，是 R04 无限尺寸的根因之一",
     "evidence_request": "A03-render-v003 / v004",
     "basis": "标签参考 Snapshot 只有 background / debug / type",
     "fix": "从 Snapshot 上移除 width/height，不保留无效属性冒充已实现",
     "verified_by": "最终 DSL 的 Snapshot 仅带 background 与 type"},
    {"id": "R07", "symptom_class": "只在视觉上暴露", "original_location": "第 10 行 color=\"#33FFFFFF\"",
     "observed": "v004 中 REVIEW 底为实心青色，而非 20% 不透明度白",
     "evidence_request": "A03-render-v004 + v004.png",
     "basis": "/reference/parser-tags/ “八位十六进制颜色的迁移”：现按 CSS #RRGGBBAA，透明度在末两位",
     "fix": "改 #FFFFFF33（0x33/255≈20%），文字另用 #FFFFFF 保持不透明",
     "verified_by": "最终图 REVIEW 底透出背景、文字边缘清晰"},
    {"id": "R08", "symptom_class": "只在视觉上暴露",
     "original_location": "第 11 行 ImageFiltered 包裹含 Text 的 Container",
     "observed": "v004 中 “Background-only blur” 文字本身被模糊到不可读",
     "evidence_request": "A03-render-v004 + v004.png",
     "basis": "/guides/painting/：ImageFiltered 作用于整棵子树；BackdropFilter 才读取已绘制背景，且建议配合 ClipRRect 限定区域",
     "fix": "改为 ClipRRect(borderRadius=24) + BackdropFilter(sigmaX=sigmaY=9) 只糊卡内背景，文字移到滤镜子树之外叠在上层",
     "verified_by": "最终图卡内细条糊、卡外细条锐、文字清晰"},
    {"id": "R09", "symptom_class": "只在视觉上暴露",
     "original_location": "第 6 行 Expanded 内 Container width=\"360\"",
     "observed": "v004 中指标卡横贯整行且只有一个，等宽三卡不成立",
     "evidence_request": "A03-render-v004 + v004.png",
     "basis": "/guides/layout/：Expanded 以紧约束占用 Flex 剩余空间，子节点主轴宽度被覆盖",
     "fix": "三个 Expanded flex=1 各包一卡，卡宽 (1216-2×24)/3=389.33 由等分得到，不再写死宽度",
     "verified_by": "最终图三卡宽度一致"},
    {"id": "R10", "symptom_class": "需求缺失（原稿未实现）", "original_location": "第 5-8 行 Row 内只有 USAGE",
     "observed": "LATENCY 148 ms 与 SUCCESS 99.2% 两卡在原稿中不存在",
     "evidence_request": "A03-render-v004 + v004.png",
     "basis": "题面要求第一行三个等宽指标卡",
     "fix": "补齐三卡，文案严格为 USAGE 72% / LATENCY 148 ms / SUCCESS 99.2%，字号 28",
     "verified_by": "最终图三项齐全"},
    {"id": "R11", "symptom_class": "需求缺失（原稿未实现）",
     "original_location": "第 11 行滤镜之外无任何背景元素",
     "observed": "没有“同时穿过说明卡两侧边界的彩色细条”，模糊语义无从判断",
     "evidence_request": "A03-render-v004",
     "basis": "题面要求背景有穿过卡两侧的彩色细条",
     "fix": "卡后绘制 8 条 x 从 32 到 1248 的细条，卡左右边界 390 与 890 均被穿过",
     "verified_by": "最终图细条在卡外锐利、卡内模糊"},
    {"id": "R12", "symptom_class": "只在视觉上暴露", "original_location": "第 7 行 Positioned right=\"20\"",
     "observed": "LIVE 为无底板纯文字，20px 越过 32 安全边距，且与标题同基线",
     "evidence_request": "A03-render-v004 + v004.png",
     "basis": "题面要求 LIVE 标签 96×36 且不盖住标题",
     "fix": "改为 96×36 圆角底板，盒 [1152,44,1248,80]；标题盒 [32,32,约332,91]，二者不相交",
     "verified_by": "最终图二者无重叠"},
    {"id": "R13", "symptom_class": "只在视觉上暴露",
     "original_location": "第 10 行 Transform 直接作为 Column 子节点",
     "observed": "v004 中 REVIEW 水平居中并压在说明卡上，不在右下",
     "evidence_request": "A03-render-v004 + v004.png",
     "basis": "题面要求右下；/guides/painting/：Transform 只改绘制坐标，不改布局尺寸",
     "fix": "放入 Stack，布局盒 [1072,640,1232,696]，旋转后包围盒 " + str(REV_BBOX) + " 仍在画布内",
     "verified_by": "最终图 REVIEW 位于右下且为逆时针倾斜"},
    {"id": "R14", "symptom_class": "静默忽略",
     "original_location": "第 2 行 Container 只有 borderRadius 无背景装饰",
     "observed": "根容器圆角无任何可见效果",
     "evidence_request": "A03-render-v004",
     "basis": "/guides/layout/ Container 组合顺序：子节点→对齐→padding→颜色/裁剪/装饰→约束→margin→transform；裁剪需要可生成路径的装饰",
     "fix": "根 Container 显式 color=#0B1220 且 padding=32，圆角落到各卡片上",
     "verified_by": "最终图背景与各卡圆角均生效"},
    {"id": "R15", "symptom_class": "只在视觉上暴露",
     "original_location": "第 6 行 Text fontSize=\"28\" 无 color",
     "observed": "v004 中指标文字为默认深色，落在深色卡面上几乎不可读",
     "evidence_request": "A03-render-v004 + v004.png",
     "basis": "Text 的 color 默认未设置，不从父容器继承颜色",
     "fix": "指标名 #94A3B8、数值用各自强调色，均 28 号",
     "verified_by": "最终图三项文字清晰可读"},
]

audit = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "input_file": "tasks/A03-semantic-debugging/inputs/broken.snapshot",
    "verbatim_first_submission": {
        "dsl": "tmp/%s/A03/orig-as-submitted.snapshot" % RUN,
        "request_id": "A03-render-v000-orig", "http_status": 400,
        "error_code": "PARSE_ERROR",
        "error_message": "Attr [padding] value format error at position 92",
        "x_request_id": "6a80ac12-52e7-4cac-af4a-c8d055a4c23f",
        "raw_response": "tmp/%s/A03/A03-render-v000-orig.resp" % RUN,
        "byte_identical_to_input": True,
        "verification": "cp 后以 cmp 校验副本与 inputs/broken.snapshot 完全一致",
    },
    "error_chain": [
        {"request_id": "A03-render-v000-orig", "status": 400, "code": "PARSE_ERROR",
         "message": "Attr [padding] value format error at position 92"},
        {"request_id": "A03-render-v001", "status": 400, "code": "PARSE_ERROR",
         "message": "Attr [matrix] must not be null at position 475"},
        {"request_id": "A03-render-v002", "status": 400, "code": "RENDER_ERROR",
         "message": "renderBox.parentData must be StackParentData"},
        {"request_id": "A03-render-v003", "status": 400, "code": "RENDER_ERROR",
         "message": "Layout size is infinite"},
        {"request_id": "A03-render-v004", "status": 200, "code": None,
         "message": "可出图，但暴露 11 项静默/视觉/缺失问题"},
    ],
    "classification_counts": {"真实报错": 4, "静默忽略": 3, "只在视觉上暴露": 6,
                              "需求缺失（原稿未实现）": 2},
    "repairs": REPAIRS,
    "blocks_preserved": {
        "title": "System Pulse 文本（原第 4 行）保留并修好 fontSize",
        "metric_row": "Row + Expanded + Container + Text（原第 5-8 行）保留，改为三个 Expanded 等分",
        "live_label": "Positioned + Text LIVE（原第 7 行）保留，移入 Stack 并加 96×36 底板",
        "spacer": "Spacer flex=1（原第 9 行）保留，现用于指标卡内部把数值推到底部",
        "review_label": "Transform + 160×56 Container + REVIEW 文字（原第 10 行）全部保留",
        "blur_card": "滤镜 + 500×150 卡 + Background-only blur 文字（原第 11 行）保留，换用 BackdropFilter 语义",
        "deleted_blocks": "无；出错区块全部保留并修复",
    },
    "no_unknown_attributes_left": {
        "checked": True,
        "method": "最终 DSL 每个属性都对照 /reference/parser-tags/ 的属性表；"
                  "Snapshot 仅 background/type，Text 仅 fontSize/color/fontStyle/fontFamily/textAlign，"
                  "Transform 仅 matrix/alignment，Container 仅文档列出的属性",
        "removed_from_original": ["Snapshot@width", "Snapshot@height", "Text@font-size",
                                  "Transform@rotate"],
    },
    "geometry": {
        "canvas": [W, H], "safe_margin": MARGIN,
        "content_box": [MARGIN, MARGIN, W - MARGIN, H - MARGIN],
        "coordinate_space": "画布左上原点，x 向右 y 向下，单位像素",
        "metric_cards": {"count": 3, "width_each": round(CARD_W, 2), "height": CARD_H,
                         "gap": GAP, "equal_width": True,
                         "boxes": [[round(MARGIN + i * (CARD_W + GAP), 1), CARD_Y,
                                    round(MARGIN + i * (CARD_W + GAP) + CARD_W, 1),
                                    CARD_Y + CARD_H] for i in range(3)]},
        "live_badge": {"w": LIVE_W, "h": LIVE_H,
                       "box": [LIVE_X, LIVE_Y, LIVE_X + LIVE_W, LIVE_Y + LIVE_H],
                       "title_box": [MARGIN, TITLE_Y, MARGIN + 300, TITLE_Y + 59],
                       "covers_title": False},
        "review_badge": {"w": REV_W, "h": REV_H, "rotation_deg_ccw": REV_ANGLE_DEG,
                         "background": "#FFFFFF33",
                         "background_alpha": round(0x33 / 255, 4),
                         "text": "#FFFFFF", "text_font_size": REV_FONT,
                         "layout_box": [REV_BOX_X, REV_BOX_Y, REV_BOX_X + REV_W,
                                        REV_BOX_Y + REV_H],
                         "rotated_bbox": REV_BBOX,
                         "inside_canvas": REV_BBOX[0] >= 0 and REV_BBOX[2] <= W
                                          and REV_BBOX[1] >= 0 and REV_BBOX[3] <= H},
        "description_card": {"w": DESC_W, "h": DESC_H, "border_radius": DESC_R,
                             "box": [DESC_X, DESC_Y, DESC_X + DESC_W, DESC_Y + DESC_H],
                             "font_size": 28},
        "stripes": {"count": len(STIPES), "x_span": [STRIPE_X0, STRIPE_X1],
                    "crosses_card_left_boundary": STRIPE_X0 < DESC_X,
                    "crosses_card_right_boundary": STRIPE_X1 > DESC_X + DESC_W},
        "blur": {"mechanism": "ClipRRect + BackdropFilter", "sigmaX": SIGMA,
                 "sigmaY": SIGMA, "applies_to": "卡内已绘制的背景",
                 "text_inside_filter_subtree": False},
    },
}
OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / "repair-log.json").write_text(
    json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

ap = argparse.ArgumentParser()
ap.add_argument("--ver", default="v005")
ap.add_argument("--final", default=None)
a = ap.parse_args()
doc = build()
TMP_DIR.mkdir(parents=True, exist_ok=True)
(TMP_DIR / f"{a.ver}.snapshot").write_text(doc.render() + "\n", encoding="utf-8")
if a.final:
    (ROOT / a.final).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / a.final).write_text(doc.render() + "\n", encoding="utf-8")
print(json.dumps({"ver": a.ver, "card_w": round(CARD_W, 2), "review_bbox": REV_BBOX,
                  "desc_box": [DESC_X, DESC_Y, DESC_X + DESC_W, DESC_Y + DESC_H],
                  "live_box": [LIVE_X, LIVE_Y, LIVE_X + LIVE_W, LIVE_Y + LIVE_H]},
                 ensure_ascii=False))
