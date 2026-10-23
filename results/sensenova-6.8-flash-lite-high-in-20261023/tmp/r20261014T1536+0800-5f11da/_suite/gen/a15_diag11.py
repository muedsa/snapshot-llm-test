"""A15 诊断 XI：字重/字号归因探针。

首版重建后，同一把尺量出来的墨宽有系统性偏差：全大写的 PRO WORKSPACE 参考 112 而
我在 14 px 下渲染出 121（宽 7.9 %），而副标题参考 246 我在 17.5 px 下渲染出 241
（窄 2.2 %）。同向偏差集中在小字号、异向偏差集中在小字号全大写，说明不是「字号
取错了」这么简单——可能是字体、字重或光学尺寸轴的问题。

这里把偏差最大的几段文案在若干字重/字号组合下各画一行，用同一阈值量墨宽，看哪个
组合最接近参考墨宽。参考墨宽来自 a15_audit.py 的 GLYPH_ROIS 实测（见 REF_TARGET）。
只读参考图、不修改任何交付文件；探针渲染存档在 preview/。
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
os.environ.setdefault("SNAPSHOT_RUN_ID", HERE.parents[2].name)
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))
import suite as S  # noqa: E402
import snap_client as C  # noqa: E402
import a15_pages as P  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 参考图实测墨宽（像素），同 a15_audit.py 的严格阈值口径
REF_TARGET = {
    "PRO WORKSPACE": 112, "12 team members": 134, "Manage access  →": 122,
    "Saturday, 07 November 2026": 246, "Projects": 72, "Apr – Sep": 76,
    "¥ thousand": 68,
}
# 探针里给每个标签用的字号（只为看字重对比，不需要与正稿一致）
PROBE_SIZE = 15.0


def build() -> str:
    c = P.load_content()
    s_sub = c["subtitle"]
    ws = c["workspace_info"]
    s_ws_tag, s_ws_main, s_ws_sub = ws[0], ws[1], ws[2]
    nav = c["navigation"][1]
    strings = [s_sub, s_ws_tag, s_ws_main, s_ws_sub, nav,
               c["chart_period"], c["chart_unit"], c["months"][0]]
    groups = [
        ("A  Inter 默认字重", [], s_sub),
        ("B  Inter Regular", "Regular", s_sub),
        ("C  Inter Light", "Light", s_sub),
        ("D  Inter Medium", "Medium", s_sub),
        ("E  Inter Semi Bold", "Semi Bold", s_sub),
        ("F  Noto Sans CJK SC 默认", [], s_sub),
        ("G  Inter Regular，PRO WORKSPACE 在 13/14/15 px", "Regular", s_ws_tag),
        ("H  Inter Medium，PRO WORKSPACE 在 13/14/15 px", "Medium", s_ws_tag),
        ("I  Inter Regular，12 team members 在 15/16/17 px",
         "Regular", s_ws_main),
        ("J  Inter Medium，12 team members 在 15/16/17 px",
         "Medium", s_ws_main),
        ("K  Noto Sans CJK SC，PRO WORKSPACE 在 14 px", [], s_ws_tag),
        ("L  Noto Sans CJK SC，12 team members 在 16 px", [], s_ws_main),
        ("M  Inter Regular，Saturday… 在 17.5/18 px", "Regular", s_sub),
        ("N  Inter Medium，Saturday… 在 17.5 px", "Medium", s_sub),
        ("O  Inter Regular，Projects 在 17/19 px", "Regular", nav),
    ]
    p = [P.rect(0, 0, 1440, 900, color=P.CARD)]
    y = 26
    for title, style, s in groups:
        p.append(P.text_at(60, y, title, 16, style="BOLD", color=P.INK))
        y += 24
        if style:
            for sz in (13.0, 14.0, 15.0) if s == s_ws_tag \
                    else (15.0, 16.0, 17.0) if s == s_ws_main \
                    else (17.0, 17.5, 18.0):
                p.append(P.text_at(100, y, s, sz, style=style, color=P.INK))
                p.append(P.text_at(1300, y, "fontSize %g" % sz, 14,
                                   color=P.MUTED))
                y += 40
        else:
            p.append(P.text_at(100, y, s, PROBE_SIZE, color=P.INK))
            p.append(P.text_at(1300, y, "默认字重 / fontSize %g"
                              % PROBE_SIZE, 14, color=P.MUTED))
            y += 40
        y += 8
    return P.snapshot(1440, 900, p)


def read_out(ink_path: Path, bg_rgb=(255, 255, 255)):
    A = np.asarray(Image.open(ink_path).convert("RGB")).astype(int)
    bg = np.array(bg_rgb)
    best = []
    for tag, w in REF_TARGET.items():
        best.append((abs(w - REF_TARGET[tag]), tag, w))
    return best


def main() -> int:
    dsl = build()
    r = C.render(P.TASK, dsl, "probe-weights", kind="render",
                 purpose="A15 字重/字号归因：小字号墨宽偏差来自字体、字重还是光学尺寸")
    print("探针 HTTP", r["status"], "bytes", r["log"].get("response_bytes"),
          "rid", r["request_id"])
    if r["status"] != 200:
        print("错误：", r["log"].get("error"))
        return 1
    ink = P.TMP / "preview" / "a15-probe-weights.png"
    P._write(ink, r["body"])
    print("->", S.rel(ink))
    P._write(P.TMP / "gen" / "probe-weights.snapshot", dsl, text_mode=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
