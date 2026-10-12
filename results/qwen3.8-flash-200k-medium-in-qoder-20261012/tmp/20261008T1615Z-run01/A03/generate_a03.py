"""A03 generator: repaired "System Pulse" monitoring card at 1280x800.

Every repair is grounded in a real service response or a documented rule; see
outputs/<run_id>/A03/repair-log.json for the finding -> evidence -> fix -> verification map.

No failing block of inputs/broken.snapshot was deleted. The repaired DSL keeps the
original skeleton and every construct that broke: the sized root Container (canvas
size), the top-level Column, <Spacer flex="1">, the metric Row with
<Expanded flex="1">, the LIVE <Positioned> label, the rotated REVIEW label and the
500x150 blur card.
"""
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "_suite" / "scripts"))
from dslkit import Doc, n  # noqa: E402

TASK = "A03"
TEMP = ROOT / "tmp" / RID / TASK
VERSION = os.environ.get("DSL_VERSION", "r04")

W, H = 1280, 800
MARGIN = 32
CW, CH = W - 2 * MARGIN, H - 2 * MARGIN          # 1216 x 736 content box
BG = "#0B1220"
CARD = "#151F33"
CARD_LINE = "#243350"
LINE_METRIC = "#33456A"
LINE_BLUR = "#4A5F86"
INK = "#FFFFFF"
DIM = "#8DA0BC"
ACCENT = {"usage": "#38BDF8", "latency": "#FBBF24", "success": "#34D399"}

METRICS = [
    ("USAGE 72%", 0.72, "72 / 100 %", "usage"),
    ("LATENCY 148 ms", 148 / 200, "148 / 200 ms 预算", "latency"),
    ("SUCCESS 99.2%", 0.992, "99.2 / 100 %", "success"),
]

# fixed block heights; the two <Spacer flex="1"> absorb the remainder of CH
HDR_H, DIV_H, GAP_H, MET_H, BLUR_H, BAR_H, FOOT_H = 84, 1, 11, 150, 150, 176, 60

CARD_X, CARD_W, CARD_R = 358, 500, 24
STRIP_X0, STRIP_X1 = 250, 980                     # cross both side boundaries of the card
# the strips only occupy the lower band of the card so they never sit under the text
STRIPS = [(94, 6, "#38BDF8"), (106, 5, "#FBBF24"), (118, 7, "#A78BFA"), (130, 5, "#34D399")]

REVIEW_W, REVIEW_H, REVIEW_DEG = 160, 56, 8.0
LIVE_W, LIVE_H = 96, 36
BAR_ROW, BAR_X0, BAR_W, BAR_LABEL = 52, 200, 700, 200


def rot_matrix(deg_ccw):
    """Column-major 4x4 that rotates visually counter-clockwise on a y-down canvas."""
    t = math.radians(deg_ccw)
    co, si = math.cos(t), math.sin(t)
    vals = [co, -si, 0, 0, si, co, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    return "(" + ",".join(f"{v:.6f}".rstrip("0").rstrip(".") or "0" for v in vals) + ")"


def pos(x, y, w, h, inner):
    return (f'<Positioned left="{n(x)}" top="{n(y)}" width="{n(w)}" '
            f'height="{n(h)}">{inner}</Positioned>')


def stack(children):
    return ('<Stack alignment="TOP_LEFT" clipBehavior="NONE">'
            + "".join(children) + "</Stack>")


def block(d, h, children):
    """A full-width Column child whose contents are absolutely placed."""
    return d.box(CW, h, inner=stack(children))


def metric_card(d, label, frac, sub, key, h):
    c = ACCENT[key]
    inner_w = 345
    bar = d.box(inner_w, 10, inner=stack([
        d.box(inner_w, 10, color="#1B2740", radius=5),
        d.box(max(inner_w * frac, 10), 10, color=c, radius=5)]))
    return d.box(None, h, color=CARD, radius=16, border=f"1 SOLID {LINE_METRIC}",
                 pad="(16,22)", align="CENTER",
                 inner=d.col([d.text("MONITORED VALUE", DIM, 18),
                              d.box(6, 1),
                              d.text(label, INK, 28, "BOLD"),
                              d.box(8, 1),
                              bar,
                              d.box(4, 1),
                              d.text(sub, c, 18)], align="START"))


def build():
    d = Doc(W, H, bg=BG)

    # --- 1. header: 44px title + 96x36 LIVE label that clears it ---------------
    header = block(d, HDR_H, [
        pos(0, 0, 700, 58, d.box(700, 58, align="CENTER_LEFT",
                                 inner=d.text("System Pulse", INK, 44, "BOLD"))),
        pos(0, 62, 700, 22, d.box(700, 22, align="CENTER_LEFT",
                                  inner=d.text(f"Snapshot DSL · {W}×{H} · 安全边距 {MARGIN}"
                                               f" · 深底 {BG}", DIM, 18))),
        pos(CW - LIVE_W, 6, LIVE_W, LIVE_H,
            d.box(LIVE_W, LIVE_H, color="#34D39926", radius=LIVE_H / 2,
                  border="1 SOLID #34D399", align="CENTER",
                  inner=d.row([d.box(10, 10, color="#34D399", radius=5),
                               d.box(8, 1),
                               d.text("LIVE", "#34D399", 20, "BOLD")]))),
    ])

    # --- 2. three equal-width metric cards: Expanded, no fixed width inside ----
    gap = 24
    cells = []
    for i, (label, frac, sub, key) in enumerate(METRICS):
        cells.append(d.exp(metric_card(d, label, frac, sub, key, MET_H)))
        if i < 2:
            cells.append(d.box(gap, MET_H))
    metrics = d.box(CW, MET_H, inner=d.row(cells))

    # --- 3. blur card block: strips cross both boundaries, text stays crisp ----
    blur_children = [pos(STRIP_X0, sy, STRIP_X1 - STRIP_X0, sh,
                         d.box(STRIP_X1 - STRIP_X0, sh, color=sc, radius=sh / 2))
                     for sy, sh, sc in STRIPS]
    blur_children.append(
        pos(CARD_X, 0, CARD_W, BLUR_H,
            f'<ClipRRect borderRadius="{CARD_R}"><BackdropFilter sigmaX="10" sigmaY="10">'
            + d.box(CARD_W, BLUR_H, color="#FFFFFF0F") + "</BackdropFilter></ClipRRect>"))
    blur_children.append(pos(CARD_X, 0, CARD_W, BLUR_H,
                             d.box(CARD_W, BLUR_H, radius=CARD_R,
                                   border=f"1 SOLID {LINE_BLUR}")))
    blur_children.append(pos(CARD_X, 0, CARD_W, 92,
                             d.box(CARD_W, 92, align="CENTER",
                                   inner=d.col([
                                       d.text("Background-only blur", INK, 28, "BOLD",
                                              align="CENTER"),
                                       d.box(6, 1),
                                       d.text("BackdropFilter σ=10 · 文字在滤镜之外",
                                              DIM, 18, align="CENTER")]))))
    blur_children.append(pos(0, 86, 240, 50,
                             d.box(240, 50, align="CENTER_RIGHT",
                                   inner=d.col([d.text("卡外细条", "#B9C8DE", 18, "BOLD"),
                                                d.text("未被模糊", "#6C7F9B", 18)]))))
    blur_children.append(pos(995, 86, CW - 995, 50,
                             d.box(CW - 995, 50, align="CENTER_LEFT",
                                   inner=d.col([
                                       d.text("同一细条进入卡内", "#B9C8DE", 18, "BOLD"),
                                       d.text("只有背景被模糊", "#6C7F9B", 18)]))))
    blur = block(d, BLUR_H, blur_children)

    # --- 4. derived bars -------------------------------------------------------
    bars = []
    for i, (label, frac, sub, key) in enumerate(METRICS):
        y = i * BAR_ROW
        bars.append(pos(0, y, BAR_LABEL, 22, d.box(BAR_LABEL, 22, align="CENTER_LEFT",
                                                   inner=d.text(label.split(" ")[0], DIM,
                                                                18, "BOLD"))))
        bars.append(pos(BAR_X0, y + 4, BAR_W, 12,
                        d.box(BAR_W, 12, color="#1B2740", radius=6)))
        bars.append(pos(BAR_X0, y + 4, BAR_W * frac, 12,
                        d.box(BAR_W * frac, 12, color=ACCENT[key], radius=6)))
        bars.append(pos(BAR_X0 + BAR_W + 12, y, 160, 22,
                        d.box(160, 22, align="CENTER_LEFT",
                              inner=d.text(sub, "#B9C8DE", 18))))
    bars.append(pos(0, 154, 900, 22, d.box(900, 22, align="CENTER_LEFT",
                                           inner=d.text("条形由题面给定值换算；LATENCY 以 "
                                                        "200 ms 预算为满格。", "#6C7F9B", 18))))
    bars_block = block(d, BAR_H, bars)

    # --- 5. footer: REVIEW 160x56 rotated 8 deg CCW, 20% white, opaque text ----
    rot = rot_matrix(REVIEW_DEG)
    footer = block(d, FOOT_H, [
        pos(0, 19, 900, 22, d.box(900, 22, align="CENTER_RIGHT",
                                  inner=d.text(f"REVIEW {REVIEW_W}×{REVIEW_H} · 逆时针 "
                                               f"{REVIEW_DEG:g}° · 底 #FFFFFF33（20% 不透明度）",
                                               "#6C7F9B", 18))),
        # top=-10: the 8 deg rotation grows the label's bbox to ~78 px tall, so the
        # unrotated box must start above the block to keep the corner inside margin 32
        pos(CW - REVIEW_W - 6, -10, REVIEW_W, REVIEW_H,
            f'<Transform matrix="{rot}" alignment="CENTER">'
            + d.box(REVIEW_W, REVIEW_H, color="#FFFFFF33", radius=10, align="CENTER",
                    border="1 SOLID #FFFFFF",
                    inner=d.text("REVIEW", INK, 24, "BOLD", align="CENTER"))
            + "</Transform>"),
    ])

    column = ('<Column crossAxisAlignment="STRETCH" mainAxisAlignment="START">'
              + header
              + d.box(CW, DIV_H, color=CARD_LINE)
              + d.box(CW, GAP_H)
              + metrics
              + '<Spacer flex="1"/>'
              + blur
              + '<Spacer flex="1"/>'
              + bars_block
              + footer
              + "</Column>")

    return (f'<Snapshot background="{BG}" type="png">'
            f'<Container width="{W}" height="{H}" color="{BG}" padding="{MARGIN}">'
            + column + "</Container></Snapshot>")


def main():
    TEMP.mkdir(parents=True, exist_ok=True)
    dsl = build()
    (TEMP / f"{VERSION}.snapshot").write_text(dsl, encoding="utf-8")
    (TEMP / f"{VERSION}-rot.json").write_text(
        json.dumps({"matrix": rot_matrix(REVIEW_DEG)}, indent=1), encoding="utf-8")
    fixed = HDR_H + DIV_H + GAP_H + MET_H + BLUR_H + BAR_H + FOOT_H
    print(f"{VERSION}: {len(dsl)} chars, rot={rot_matrix(REVIEW_DEG)}, "
          f"fixed={fixed} of {CH}, spacer each={(CH - fixed) / 2:g}")


if __name__ == "__main__":
    main()
