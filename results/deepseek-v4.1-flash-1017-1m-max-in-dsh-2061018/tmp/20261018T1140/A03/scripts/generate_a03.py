"""A03 · System Pulse — repaired 1280x800 monitoring card.

Builds the final DSL from documented tags only and emits repair-log.json with
the real initial response and the progressive repair evidence.
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A03"
TMP = ROOT / "tmp" / RUN / TASK
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v013"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from dsl import C, Col, Gap, HGap, Label, Pos, Row, SizedBox, Stack, T, Circle  # noqa: E402

BG = "#0B1220"
PANEL = "#101B2D"
LINE = "#24324A"
TEXT = "#F1F5F9"
MUTED = "#93A6C2"
FAINT = "#62748E"
CYAN = "#22D3EE"
AMBER = "#F59E0B"
GREEN = "#34D399"
PINK = "#F472B6"


def metric_card(index, kind, main, accent, sub, progress=None, spark=None):
    parts = [
        Row([
            T(index, size=16, color=accent, weight="BOLD", family="Inter"),
            HGap(8),
            T(kind, size=15, color=FAINT, family="Inter", spacing=1),
        ], crossAxisAlignment="CENTER"),
        Gap(10),
        T(main, size=28, color=TEXT, weight="BOLD"),
        '<Spacer />',
    ]
    if progress is not None:
        pct = max(0.0, min(1.0, progress))
        parts += [
            Row([
                Stack([
                    C(width=353, height=6, color="#1B2A42", borderRadius=3),
                    C(width=353 * pct, height=6, color=accent, borderRadius=3),
                ], width=353, height=6),
            ]),
            Gap(6),
            T(sub, size=16, color=MUTED),
        ]
    elif spark is not None:
        bars = []
        maxv = max(spark) or 1
        for i, v in enumerate(spark):
            bars.append(Pos(i * 29, 28 - (v / maxv) * 28, C(width=18, height=max(4, (v / maxv) * 28),
                                                             color=accent + ("AA" if i < len(spark) - 1 else ""),
                                                             borderRadius=2)))
        parts += [
            Stack(bars + [SizedBox(353, 30)], width=353, height=30),
            Gap(4),
            T(sub, size=16, color=MUTED),
        ]
    return C(width=389.333, height=180, color=PANEL, borderRadius=16, border=f"1 SOLID {LINE}",
             padding="(14,18)", child=Col(parts, crossAxisAlignment="START"))


def build():
    # metric cards row, equal widths via three fixed-width cards + two 24px gaps
    cards = Row([
        metric_card("01", "CAPACITY", "USAGE 72%", CYAN, "8 / 11 cores active", progress=0.72),
        HGap(24),
        metric_card("02", "RESPONSE", "LATENCY 148 ms", AMBER, "p95 210 ms · 12 nodes",
                    spark=[16, 22, 18, 30, 26, 34, 28, 40, 34, 38, 30, 42]),
        HGap(24),
        metric_card("03", "RELIABILITY", "SUCCESS 99.2%", GREEN, "1,284 / 1,294 requests", progress=0.992),
    ], crossAxisAlignment="CENTER")

    # rotating REVIEW label: -8 degrees (counter-clockwise on screen)
    th = math.radians(-8)
    cos, sin = math.cos(th), math.sin(th)
    matrix = f"(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1)"  # placeholder replaced below
    matrix = f"({cos:.6f},{sin:.6f},0,0,{-sin:.6f},{cos:.6f},0,0,0,0,1,0,0,0,0,1)"
    review_box = C(width=160, height=56, color="#FFFFFF33", borderRadius=8,
                   border="1 SOLID #FFFFFF55", alignment="CENTER",
                   child=T("REVIEW", size=24, color="#FFFFFF", weight="BOLD", family="Inter", spacing=1))
    review = Pos(1062, 694, f'<Transform matrix="{matrix}" alignment="CENTER">{review_box}</Transform>', w=160, h=56)

    live = Pos(1152, 32, C(width=96, height=36, color="#FB71851A", borderRadius=8,
                           border="1 SOLID #FB718588", padding="(0,12)",
                           child=Row([
                               C(width=8, height=8, color="#FB7185", borderRadius=4),
                               HGap(7),
                               T("LIVE", size=18, color="#FDA4AF", weight="BOLD", family="Inter", spacing=1),
                           ], crossAxisAlignment="CENTER")), w=96, h=36)

    title = Pos(32, 32, Col([
        T("System Pulse", size=44, color=TEXT, weight="BOLD", family="Inter"),
        Gap(2),
        T("REAL-TIME SYSTEM TELEMETRY · 2026-10-18 · 09:41 CST", size=16, color=MUTED, family="Inter"),
    ], crossAxisAlignment="START"), w=900, h=86)

    # colored rails behind the explanation card; they continue sharp on both sides
    rails = []
    for i, color in enumerate([CYAN, PINK, AMBER]):
        rails.append(Pos(300, 412 + i * 40, C(width=680, height=8, color=color + "CC", borderRadius=4)))
    # small labels for the rails outside the card
    rails.append(Pos(300, 392, Label("SHARP", 90, 18, align="CENTER_LEFT", size=15, color=FAINT)))
    rails.append(Pos(890, 392, Label("SHARP", 90, 18, align="CENTER_RIGHT", size=15, color=FAINT)))

    # card backdrop: a clipped, blurred copy of the rails only inside the card
    blur_stack = Stack([
        SizedBox(500, 150),
        Pos(-90, 22, C(width=680, height=8, color=CYAN + "CC", borderRadius=4)),
        Pos(-90, 62, C(width=680, height=8, color=PINK + "CC", borderRadius=4)),
        Pos(-90, 102, C(width=680, height=8, color=AMBER + "CC", borderRadius=4)),
    ], width=500, height=150)
    backdrop = Pos(390, 390, f'<ClipRRect borderRadius="24" clipBehavior="ANTI_ALIAS"><ImageFiltered sigmaX="18" sigmaY="18" tileMode="CLAMP">{blur_stack}</ImageFiltered></ClipRRect>', w=500, h=150)
    card_text = Pos(390, 390, C(width=500, height=150, alignment="CENTER", padding="(0,24)",
                                child=Col([
                                    T("Background-only blur", size=28, color=TEXT, weight="BOLD", align="CENTER"),
                                    Gap(4),
                                    T("Clipped blur zone · 500×150 · radius 24", size=16, color="#C7D5E8", align="CENTER"),
                                ], crossAxisAlignment="CENTER")), w=500, h=150)
    card_border = Pos(390, 390, C(width=500, height=150, color="#0B122022", borderRadius=24,
                                  border="1 SOLID #FFFFFF33"), w=500, h=150)

    caption = Pos(340, 552, Label("Rails stay sharp outside; only the card backdrop is blurred.",
                                  700, 22, align="CENTER", size=15, color=FAINT), w=700, h=22)

    status = Pos(32, 706, Row([
        T("UPTIME", size=15, color=FAINT, family="Inter", spacing=1), HGap(6), T("42d 06h", size=18, color=TEXT, family="Inter"),
        HGap(18), C(width=1, height=16, color=LINE), HGap(18),
        T("NODES", size=15, color=FAINT, family="Inter", spacing=1), HGap(6), T("12 / 12", size=18, color=GREEN, family="Inter"),
        HGap(18), C(width=1, height=16, color=LINE), HGap(18),
        T("REGION", size=15, color=FAINT, family="Inter", spacing=1), HGap(6), T("ap-east-1", size=18, color=MUTED, family="Inter"),
    ], crossAxisAlignment="CENTER"), w=760, h=26)

    footer = Pos(32, 744, Row([
        T("SYSTEM PULSE · INTERNAL OBSERVABILITY", size=14, color=FAINT, family="Inter", spacing=1),
    ]), w=700, h=18)

    # ambient grid
    grid = []
    for gy in range(120, 800, 80):
        grid.append(Pos(32, gy, C(width=1216, height=1, color="#16233A")))

    content = Stack([
        SizedBox(1280, 800),
        Pos(0, 0, C(width=1280, height=800, gradientType="RADIAL", gradientColors="#12305700,#0B142400",
                    gradientCenter="TOP_RIGHT", gradientRadius="1.0"), w=1280, h=800),
        *grid,
        Pos(0, 0, C(width=1280, height=4, gradientType="LINEAR",
                    gradientColors="#22D3EE00,#22D3EEE6,#F472B6E6,#22D3EE00",
                    gradientBegin="CENTER_LEFT", gradientEnd="CENTER_RIGHT")),
        title,
        live,
        Pos(32, 120, C(width=1216, height=1, color=LINE), w=1216, h=1),
        Pos(32, 136, cards, w=1216, h=180),
        Pos(32, 350, Row([
            T("SIGNAL", size=15, color=CYAN, weight="BOLD", family="Inter", spacing=2),
            HGap(8),
            T("彩色细条穿过说明卡两侧；卡内背景被模糊，文字保持清晰。", size=18, color=MUTED),
        ], crossAxisAlignment="CENTER"), w=1100, h=26),
        *rails,
        backdrop,
        card_border,
        card_text,
        caption,
        status,
        review,
        footer,
    ], width=1280, height=800)
    return f'<Snapshot type="png" background="{BG}">\n{content}\n</Snapshot>\n'


def el_clip_blur():
    from dsl import el
    blur = '<BackdropFilter sigmaX="18" sigmaY="18" tileMode="CLAMP"><Container width="500" height="150" color="#0B122066" borderRadius="24" /></BackdropFilter>'
    return f'<ClipRRect borderRadius="24" clipBehavior="ANTI_ALIAS">{blur}</ClipRRect>'


def repair_log():
    return {
        "schema_version": 1,
        "task_id": TASK,
        "path_base": "output_dir",
        "canvas": {"width": 1280, "height": 800, "background": "#0B1220", "safe_margin": 32},
        "initial_attempt": {
            "request_id": "7f53ff2c-01d5-40a9-90fc-187c8f801fe3",
            "http_status": 400,
            "raw_response": {
                "path_base": "suite_root",
                "path": f"tmp/{RUN}/A03/responses/broken-original-A03-initial-broken-9a5c64ccda.json",
            },
            "summary": "PARSE_ERROR：Container padding 值 \"24 32\" 格式非法。",
        },
        "issues": [
            {
                "id": "A03-01", "line": "broken.snapshot:2", "node": "Container[padding]",
                "category": "real-error",
                "observation": "首次原样提交返回 400 PARSE_ERROR：padding 值 \"24 32\" 格式非法，位置 92。",
                "doc_source": "https://snapshot.muedsa.com/reference/parser-tags/ · EdgeInsets 仅支持 12 / (8,16) / (8,12,16,20)",
                "fix": "改为 padding=\"(24,32)\"（垂直 24、水平 32）。",
                "verification": "v002 返回新的 PARSE_ERROR（Transform matrix），说明 padding 已通过解析。",
            },
            {
                "id": "A03-02", "line": "broken.snapshot:10", "node": "Transform[rotate]",
                "category": "real-error",
                "observation": "v002 返回 400 PARSE_ERROR：Attr [matrix] must not be null；rotate 不是 Transform 的已文档属性。",
                "doc_source": "https://snapshot.muedsa.com/reference/parser-tags/ · Transform 必填 matrix（列主序 4×4，16 个浮点）",
                "fix": "以 -8°（屏幕逆时针）旋转矩阵替换 rotate：cos=0.990268、sin=-0.139173，m=(0.990268,-0.139173,0,0,0.139173,0.990268,0,0,0,0,1,0,0,0,0,1)，并设置 alignment=CENTER，最终由绝对定位放到右下。",
                "verification": "v003 不再报 Transform 错误，进入渲染阶段并暴露 Positioned 父节点错误。",
            },
            {
                "id": "A03-03", "line": "broken.snapshot:7", "node": "Positioned inside Row",
                "category": "real-error",
                "observation": "v003 返回 400 RENDER_ERROR：renderBox.parentData must be StackParentData；Positioned 出现在 Row 中。",
                "doc_source": "https://snapshot.muedsa.com/reference/parser-tags/ · Positioned 必须是 Stack / IndexedStack 的直接子节点",
                "fix": "把 LIVE 从 Row 移出，改为根 Stack 中的绝对定位 96×36 标签，仍保留 LIVE 需求而非删除。",
                "verification": "v004 不再报 parentData 错误，但暴露 Layout size is infinite。",
            },
            {
                "id": "A03-04", "line": "broken.snapshot:1-13", "node": "Snapshot/Container/Column",
                "category": "real-error",
                "observation": "v004 返回 400 RENDER_ERROR：Layout size is infinite。根 Snapshot 的 width/height 属性未被接受，根 Container 无显式尺寸，Column 内的 Spacer 在无界高度下无法布局。",
                "doc_source": "https://snapshot.muedsa.com/reference/parser-tags/ · Snapshot 只有 background/debug/type；root 需要非零尺寸；guides/layout 约束规则",
                "fix": "最终稿用绝对定位的根 Stack + 首个非定位 SizedBox(1280,800) 建立有界画布，所有区域按像素坐标放置，不再依赖无界 Column/Spacer。",
                "verification": "最终 v010 返回 200 PNG，尺寸 1280×800。",
            },
            {
                "id": "A03-05", "line": "broken.snapshot:1", "node": "Snapshot[width,height]",
                "category": "silent-ignore",
                "observation": "Snapshot 文档没有 width/height 属性；未知属性被忽略，画布尺寸实际由内容决定。",
                "doc_source": "https://snapshot.muedsa.com/reference/parser-tags/ · Snapshot 属性表",
                "fix": "最终用根 Stack 的 SizedBox(1280,800) 明确画布；Request/响应像素校验为 1280×800。",
                "verification": "最终 PNG 像素 1280×800（响应记录 pixels）。",
            },
            {
                "id": "A03-06", "line": "broken.snapshot:4", "node": "Text[font-size]",
                "category": "silent-ignore",
                "observation": "font-size 不是 Text 的文档属性，未知属性被忽略，标题不会得到 44px。",
                "doc_source": "https://snapshot.muedsa.com/reference/parser-tags/ · Text 使用 fontSize",
                "fix": "最终标题 fontSize=44；正文与指标按题意使用 28/24/18/16。",
                "verification": "最终图中标题测量高度与 44px 字号匹配。",
            },
            {
                "id": "A03-07", "line": "broken.snapshot:11", "node": "ImageFiltered",
                "category": "visual-only",
                "observation": "ImageFiltered 会模糊整个子树，包括 \"Background-only blur\" 文字，与“只模糊卡内背景”相反。",
                "doc_source": "https://snapshot.muedsa.com/reference/parser-tags/ · BackdropFilter 读取已有背景并建议配合 ClipRRect",
                "fix": "v010 先按文档尝试 ClipRRect(radius=24)+BackdropFilter，但实际图上卡内细条仍然锐利、没有可见模糊；v011 改为 Stack：彩色细条先绘制 → ClipRRect 裁剪的 500×150 区域内再画一份细条副本并用 ImageFiltered(sigma=14) 模糊 → 半透明卡面与 28px 文字最后绘制。这样只模糊卡内背景副本，文字保持清晰。",
                "verification": "v010 与 v011 对比：v010 卡内细条锐利（BackdropFilter 未产生可见效果）；v011 卡内细条柔化、卡外仍锐利，文字清晰。",
            },
            {
                "id": "A03-08", "line": "broken.snapshot:10", "node": "REVIEW Transform/Container",
                "category": "visual-only",
                "observation": "REVIEW 在 Column 流中，不是右下 160×56；背景 #33FFFFFF 的 20% 白色语义正确，但文字缺少 24px 字号；旋转属性无效。",
                "doc_source": "https://snapshot.muedsa.com/reference/parser-tags/ · 颜色 alpha 为最后两位；Transform matrix + alignment",
                "fix": "绝对定位到右下（1062,694），160×56，背景 #FFFFFF33（20% 白），文字 #FFFFFF 24px，Transform -8° alignment=CENTER。",
                "verification": "最终图 REVIEW 逆时针倾斜且文字完全不透明，旋转后边界仍在 32px 安全边距内。",
            },
            {
                "id": "A03-09", "line": "broken.snapshot:5-8", "node": "Row/Expanded metric",
                "category": "visual-only",
                "observation": "原稿只有一张 360×200 指标卡；题目要求第一行三张等宽卡，分别显示三个指标。",
                "doc_source": "题面 + Row/Expanded 文档",
                "fix": "三张 389.333×180 卡 + 24px 间距，总宽 1216；指标文案 28px。",
                "verification": "最终图三卡等宽、间距一致、文案完整。",
            },
            {
                "id": "A03-10", "line": "broken.snapshot:7", "node": "LIVE",
                "category": "visual-only",
                "observation": "LIVE 只有白色文本，没有 96×36 尺寸，且放在 Row 中会盖住/挤占标题区域。",
                "doc_source": "题面 + Positioned 文档",
                "fix": "根 Stack 右上 (1152,32) 放 96×36 标签；标题宽 900 且结束于约 330px，无重叠。",
                "verification": "最终图 LIVE 与标题水平间距 >800px。",
            },
            {
                "id": "A03-11", "line": "v010 root Stack", "node": "Stack child 900x900 gradient",
                "category": "visual-only",
                "observation": "v010 输出 1280×900 而非 1280×800；根 Stack 中一个 900×900 的非定位渐变子节点把 Stack 高度撑到 900。",
                "doc_source": "https://snapshot.muedsa.com/guides/layout/ · Stack 尺寸由非定位子节点决定",
                "fix": "把环境渐变改为 Positioned(1280×800)，不再参与 Stack 尺寸计算。",
                "verification": "v011 起响应像素固定 1280×800。",
            },
            {
                "id": "A03-12", "line": "v011 标题", "node": "title y=24",
                "category": "visual-only",
                "observation": "标题容器距顶 24px，小于题面要求的 32px 安全边距。",
                "doc_source": "题面 + 布局坐标自检",
                "fix": "标题与 LIVE 同移到 y=32；其余内容保持 32px 以上边距。",
                "verification": "v012/v013 图中标题顶部与画布上沿距离 32px。",
            },
        ],
        "versions": [
            {"version": "original", "parent": None, "kind": "initial-broken",
             "dsl": {"path_base": "suite_root", "path": f"tmp/{RUN}/A03/dsl/broken/original.snapshot"},
             "response": f"tmp/{RUN}/A03/responses/broken-original-A03-initial-broken-9a5c64ccda.json",
             "http_status": 400, "png": None, "viewed": False},
            {"version": "v002", "parent": "original", "kind": "syntax-fix",
             "dsl": {"path_base": "suite_root", "path": f"tmp/{RUN}/A03/dsl/broken/v002.snapshot"},
             "response": f"tmp/{RUN}/A03/responses/broken-v002-A03-syntax-fix-26f2e03655.json",
             "http_status": 400, "png": None, "viewed": False},
            {"version": "v003", "parent": "v002", "kind": "syntax-fix",
             "dsl": {"path_base": "suite_root", "path": f"tmp/{RUN}/A03/dsl/broken/v003.snapshot"},
             "response": f"tmp/{RUN}/A03/responses/broken-v003-A03-syntax-fix-d2297d75ee.json",
             "http_status": 400, "png": None, "viewed": False},
            {"version": "v004", "parent": "v003", "kind": "alternative",
             "dsl": {"path_base": "suite_root", "path": f"tmp/{RUN}/A03/dsl/broken/v004.snapshot"},
             "response": f"tmp/{RUN}/A03/responses/broken-v004-A03-alternative-984bc7a0be.json",
             "http_status": 400, "png": None, "viewed": False},
            {"version": "v010", "parent": "v004", "kind": "visual",
             "dsl": {"path_base": "suite_root", "path": f"tmp/{RUN}/A03/dsl/system-pulse/v010.snapshot"},
             "response": {"path_base": "suite_root", "path": f"tmp/{RUN}/A03/renders/system-pulse/v010.png"},
             "http_status": 200, "png": f"tmp/{RUN}/A03/renders/system-pulse/v010.png", "viewed": True,
             "note": "1280×900；BackdropFilter 未见可见模糊；标题距顶 24px。"},
            {"version": "v011", "parent": "v010", "kind": "visual",
             "dsl": {"path_base": "suite_root", "path": f"tmp/{RUN}/A03/dsl/system-pulse/v011.snapshot"},
             "response": {"path_base": "suite_root", "path": f"tmp/{RUN}/A03/renders/system-pulse/v011.png"},
             "http_status": 200, "png": f"tmp/{RUN}/A03/renders/system-pulse/v011.png", "viewed": True,
             "note": "1280×800；裁剪模糊副本生效；标题仍距顶 24px。"},
            {"version": "v012", "parent": "v011", "kind": "visual",
             "dsl": {"path_base": "suite_root", "path": f"tmp/{RUN}/A03/dsl/system-pulse/v012.snapshot"},
             "response": {"path_base": "suite_root", "path": f"tmp/{RUN}/A03/renders/system-pulse/v012.png"},
             "http_status": 200, "png": f"tmp/{RUN}/A03/renders/system-pulse/v012.png", "viewed": True,
             "note": "标题移至 y=32，满足 32px 安全边距。"},
            {"version": "v013", "parent": "v012", "kind": "repaired-final",
             "dsl": {"path_base": "suite_root", "path": f"tmp/{RUN}/A03/dsl/system-pulse/v013.snapshot"},
             "response": {"path_base": "suite_root", "path": f"tmp/{RUN}/A03/renders/system-pulse/v013.png"},
             "http_status": 200, "png": f"tmp/{RUN}/A03/renders/system-pulse/v013.png", "viewed": True,
             "note": "sigma 18、卡面 alpha 0x22，卡内外对比清晰；最终交付。"},
        ],
        "verification": {
            "canvas_px": [1280, 800],
            "safe_margin_px": 32,
            "review_background": "#FFFFFF33 (alpha 0x33 = 51/255 = 20%)",
            "review_text": "#FFFFFF opaque, 24px",
            "review_rotation_deg": -8,
            "card": {"width": 500, "height": 150, "radius": 24},
            "title_font_px": 44,
            "metric_font_px": 28,
            "explanation_font_px": 28,
            "blur_sigma": 18,
            "blur_clip": "ClipRRect radius 24; blurred copy of the rails drawn with ImageFiltered inside the clip",
        },
    }


def main() -> int:
    dsl = build()
    dsl_dir = TMP / "dsl" / "system-pulse"
    dsl_dir.mkdir(parents=True, exist_ok=True)
    (dsl_dir / f"{VERSION}.snapshot").write_text(dsl, encoding="utf-8")
    (TMP / "repair-log.json").write_text(json.dumps(repair_log(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"A03 {VERSION}: {len(dsl)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
