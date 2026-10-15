#!/usr/bin/env python
"""A03 System Pulse 监控卡 —— 修复后的 1280×800 定稿。

启动基准：总任务根。输入 broken.snapshot 只读；本脚本产出的定稿不含任何未知属性。
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import snapkit as sk  # noqa: E402
from snapkit import C  # noqa: E402

TASK = "A03"
W, H = 1280, 800
BG = "#0B1220"
SAFE = 32
DRAFTS = f"tmp/run-20261011-01/{TASK}/drafts"

METRICS = [
    ("USAGE 72%", "GPU 与工作池占用", 0.72, "标尺 0 – 100%", "#0EA5E9"),
    ("LATENCY 148 ms", "请求延迟 p95", 148 / 400, "标尺 0 – 400 ms", "#F59E0B"),
    ("SUCCESS 99.2%", "请求成功率", 0.992, "标尺 0 – 100%", "#10B981"),
]

CARD_W, CARD_H = 500, 150
CARD_X = (W - CARD_W) // 2          # 390
CARD_Y = 396
BAR_H = 10
BAR_X0 = CARD_X - 60                # 330
BAR_X1 = CARD_X + CARD_W + 60       # 950
BARS = [("#22D3EE", CARD_Y + 18), ("#A78BFA", CARD_Y + 64), ("#34D399", CARD_Y + 110)]

LIVE_W, LIVE_H = 96, 36
LIVE_X, LIVE_Y = W - SAFE - LIVE_W, 34          # 1152, 34
REVIEW_W, REVIEW_H = 160, 56
REVIEW_X, REVIEW_Y = W - SAFE - REVIEW_W, 676  # 1088, 676
ROT_DEG = -8.0                                   # 视觉逆时针 8°


def pulse_values(n=44):
    """确定性的「心跳」脉冲序列（示意数据，非实测）。"""
    vals = []
    for i in range(n):
        t = i / n
        base = 0.30 + 0.16 * math.sin(t * math.pi * 5.0)
        spike = 0.0
        for c in (0.12, 0.30, 0.52, 0.78):
            spike = max(spike, 0.62 * math.exp(-((t - c) ** 2) / 0.0011))
        vals.append(min(1.0, base + spike))
    return vals


def build():
    P = []
    A = P.append

    # ---------- 标题
    A(sk.text("System Pulse", size=44, color="#FFFFFF", family=sk.F_HEAD,
              left=SAFE, top=26, width=620, height=60))
    A(sk.text("Realtime service health · 2026-11-07 14:32 CST · 演示数据",
              size=18, color="#94A3B8", family=sk.F_BODY, left=SAFE, top=92, width=760, height=26))

    # ---------- LIVE 标签 96×36（右上，不与标题重叠）
    live_box = [LIVE_X, LIVE_Y, LIVE_X + LIVE_W, LIVE_Y + LIVE_H]
    title_box = [SAFE, 26, SAFE + 620, 26 + 60]
    overlap = not (live_box[2] <= title_box[0] or live_box[0] >= title_box[2]
                   or live_box[3] <= title_box[1] or live_box[1] >= title_box[3])
    A(f'<Positioned left="{LIVE_X}" top="{LIVE_Y}" width="{LIVE_W}" height="{LIVE_H}">'
      f'<Container width="{LIVE_W}" height="{LIVE_H}" color="#22C55E" borderRadius="8" alignment="CENTER">'
      f'<Text fontSize="20" color="#052E16" fontFamily="{sk.F_HEAD}" fontStyle="BOLD">LIVE</Text>'
      f'</Container></Positioned>')

    # ---------- 第一行三个等宽指标卡
    row_y, row_h = 136, 186
    gap = 20
    mw = (W - 2 * SAFE - 2 * gap) // 3          # 392
    metric_boxes = []
    for i, (label, caption, ratio, scale, col) in enumerate(METRICS):
        x = SAFE + i * (mw + gap)
        metric_boxes.append([x, row_y, x + mw, row_y + row_h])
        A(f'<Positioned left="{x}" top="{row_y}" width="{mw}" height="{row_h}">'
          f'<Container width="{mw}" height="{row_h}" color="#111C30" border="1.5 SOLID #1E3A5F" '
          f'borderRadius="16"><Stack fit="EXPAND">'
          f'<Positioned left="0" top="0" width="{mw}" height="4">'
          f'<Container width="{mw}" height="4" color="{col}" borderRadius="2"/></Positioned>'
          f'<Positioned left="26" top="30" width="{mw - 52}" height="38">'
          f'<Text fontSize="28" color="#FFFFFF" fontFamily="{sk.F_HEAD}">{label}</Text></Positioned>'
          f'<Positioned left="26" top="78" width="{mw - 52}" height="24">'
          f'<Text fontSize="17" color="#94A3B8" fontFamily="{sk.F_BODY}">{caption}</Text></Positioned>'
          f'<Positioned left="26" top="122" width="{mw - 52}" height="10">'
          f'<Container width="{mw - 52}" height="10" color="#1E293B" borderRadius="5"/></Positioned>'
          f'<Positioned left="26" top="122" width="{(mw - 52) * ratio:.2f}" height="10">'
          f'<Container width="{(mw - 52) * ratio:.2f}" height="10" color="{col}" borderRadius="5"/></Positioned>'
          f'<Positioned left="26" top="146" width="{mw - 52}" height="20">'
          f'<Text fontSize="15" color="#64748B" fontFamily="{sk.F_BODY}">{scale}</Text></Positioned>'
          f'</Stack></Container></Positioned>')

    # ---------- 彩色细条（同时穿过说明卡两侧边界）
    for col, by in BARS:
        A(f'<Positioned left="{BAR_X0}" top="{by}" width="{BAR_X1 - BAR_X0}" height="{BAR_H}">'
          f'<Container width="{BAR_X1 - BAR_X0}" height="{BAR_H}" color="{col}" borderRadius="5"/></Positioned>')

    # ---------- 中央说明卡：只模糊卡内背景，文字保持清晰
    A(f'<Positioned left="{CARD_X}" top="{CARD_Y}" width="{CARD_W}" height="{CARD_H}">'
      f'<ClipRRect borderRadius="24" clipBehavior="ANTI_ALIAS">'
      f'<BackdropFilter sigmaX="12" sigmaY="12" tileMode="CLAMP">'
      f'<Container width="{CARD_W}" height="{CARD_H}" color="#FFFFFF1F"/>'
      f'</BackdropFilter></ClipRRect></Positioned>')
    # 文字单独一层，不放进任何 ImageFiltered/BackdropFilter 子树
    A(f'<Positioned left="{CARD_X}" top="{CARD_Y + 58}" width="{CARD_W}" height="36">'
      f'<Text fontSize="28" color="#FFFFFF" fontFamily="{sk.F_HEAD}" textAlign="CENTER">'
      f'Background-only blur</Text></Positioned>')
    # 说明文字层放在卡外，避免与穿过卡内的彩色细条叠压（文字层不参与任何滤镜）
    A(f'<Positioned left="{CARD_X}" top="{CARD_Y + CARD_H + 12}" width="{CARD_W}" height="24">'
      f'<Text fontSize="16" color="#94A3B8" fontFamily="{sk.F_BODY}" textAlign="CENTER">'
      f'σ=12 模糊仅作用于卡内背景，文字层不在滤镜子树内</Text></Positioned>')

    # ---------- 脉冲条（右端让开 REVIEW 标签）
    strip_y, strip_h = 620, 68
    A(sk.text("pulse", size=16, color="#94A3B8", family=sk.F_BODY, left=SAFE, top=strip_y + 24,
              width=70, height=22))
    vals = pulse_values()
    sx0, sw = SAFE + 76, 1030 - (SAFE + 76)
    slot = sw / len(vals)
    bw = slot * 0.56
    for i, v in enumerate(vals):
        bh = max(4.0, strip_h * v)
        A(f'<Positioned left="{sx0 + slot * i:.2f}" top="{strip_y + (strip_h - bh):.2f}" '
          f'width="{bw:.2f}" height="{bh:.2f}">'
          f'<Container width="{bw:.2f}" height="{bh:.2f}" color="#22D3EE" borderRadius="2" '
          f'opacity="{0.35 + 0.65 * v:.3f}"/></Positioned>')

    # ---------- REVIEW 标签 160×56，视觉逆时针 8°，白底 20%，文字不透明 24px
    A(f'<Positioned left="{REVIEW_X}" top="{REVIEW_Y}" width="{REVIEW_W}" height="{REVIEW_H}">'
      f'<Transform matrix="{sk.rot_matrix(ROT_DEG)}" alignment="CENTER">'
      f'<Container width="{REVIEW_W}" height="{REVIEW_H}" color="#FFFFFF33" borderRadius="10" alignment="CENTER">'
      f'<Text fontSize="24" color="#FFFFFF" fontFamily="{sk.F_HEAD}">REVIEW</Text>'
      f'</Container></Transform></Positioned>')

    # ---------- 页脚
    A(sk.text("数据为演示用示意值 · 修复自 inputs/broken.snapshot（详见 repair-log.json）",
              size=16, color="#64748B", family=sk.F_BODY, left=SAFE, top=744, width=900, height=24))

    body = "".join(P)
    return (f'<Snapshot background="{BG}" type="png">\n'
            f'<Container width="{W}" height="{H}" color="{BG}">\n'
            f'<Stack fit="EXPAND">\n{body}\n</Stack>\n</Container>\n</Snapshot>\n'), {
        "title_box": title_box, "live_box": live_box, "live_overlaps_title": overlap,
        "metric_boxes": metric_boxes, "card_box": [CARD_X, CARD_Y, CARD_X + CARD_W, CARD_Y + CARD_H],
        "bar_span": [BAR_X0, BARS[0][1], BAR_X1, BARS[-1][1] + BAR_H],
        "review_box": [REVIEW_X, REVIEW_Y, REVIEW_X + REVIEW_W, REVIEW_Y + REVIEW_H],
    }


def main():
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    r = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    d = r / DRAFTS
    d.mkdir(parents=True, exist_ok=True)
    dsl, geo = build()
    (d / f"a03-{ver}.snapshot").write_text(dsl, encoding="utf-8")
    (d / f"a03-{ver}-geometry.json").write_text(
        json.dumps({"canvas": [W, H], "safe_margin": SAFE, **geo,
                    "bars": [{"color": c, "y": y, "x0": BAR_X0, "x1": BAR_X1, "h": BAR_H} for c, y in BARS],
                    "card": {"w": CARD_W, "h": CARD_H, "radius": 24, "x": CARD_X, "y": CARD_Y},
                    "live": {"w": LIVE_W, "h": LIVE_H, "x": LIVE_X, "y": LIVE_Y},
                    "review": {"w": REVIEW_W, "h": REVIEW_H, "x": REVIEW_X, "y": REVIEW_Y,
                               "rotation_deg": ROT_DEG, "rotation_note": "屏幕坐标 y 向下，负角即视觉逆时针",
                               "background": "#FFFFFF33", "text_size": 24},
                    "metric_cards": [{"label": m[0], "x": mb[0], "y": mb[1],
                                      "w": mb[2] - mb[0], "h": mb[3] - mb[1]}
                                     for m, mb in zip(METRICS, geo["metric_boxes"])],
                    "title_font_size": 44, "metric_font_size": 28, "card_text_font_size": 28},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(d / f"a03-{ver}.snapshot"))


if __name__ == "__main__":
    main()