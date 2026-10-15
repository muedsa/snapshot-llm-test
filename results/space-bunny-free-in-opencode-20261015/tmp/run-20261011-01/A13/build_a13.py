#!/usr/bin/env python
"""A13 定稿：四个交付画布（符号彩色 / 符号纯黑 / 品牌横幅 / 发布海报）。

启动基准：总任务根 (suite_root)。
符号在横幅与海报中由 `geom_a13.symbol()` 用**同一套几何规则**现场生成，
不嵌入任何渲染 PNG；符号只做等比缩放与平移，不做变形。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/A13")
sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
from geom_a13 import (  # noqa: E402
    PAL_COLOR, PAL_BLACK, symbol, components_of, NEGATIVE_SPACE_B, DIRECTION_NAME,
)

DRAFTS = "tmp/run-20261011-01/A13/drafts"
DIR = "B"                      # 选定方向

F_HEAD = "Inter Semi Bold"
F_NUM = "Inter Medium"
F_LAT = "Inter"
F_SC = "Noto Sans CJK SC"
F_MIX = f"{F_LAT},{F_SC}"
F_MIX_HEAD = f"{F_HEAD},{F_SC}"

BRAND_CN = "叠光"
BRAND_EN = "Layerlight"
TAGLINE = "把复杂信息，组织成清晰画面"
EVENT_LINE = "2026.11.07 · ONLINE"
BETA = "OPEN BETA"
SITE = "layerlight.example.org"


# ---------------------------------------------------------------- 图元
def rect(x, y, w, h, color, radius=0, border=None):
    b = f' border="1.5 SOLID {border}"' if border else ""
    return (f'<Positioned left="{round(x, 2)}" top="{round(y, 2)}" width="{round(w, 2)}" '
            f'height="{round(h, 2)}"><Container width="{round(w, 2)}" height="{round(h, 2)}" '
            f'color="{color}" borderRadius="{radius}"{b}/></Positioned>')


def txt(text, x, y, w, h, size, color, family=F_MIX, align=None, spacing=None):
    assert '"' not in text
    at = f' fontSize="{size}" color="{color}" fontFamily="{family}"'
    if align:
        at += f' textAlign="{align}"'
    if spacing:
        at += f' letterSpacing="{spacing}"'
    return (f'<Positioned left="{round(x, 2)}" top="{round(y, 2)}" width="{round(w, 2)}" '
            f'height="{round(h, 2)}"><Text{at} text="{text}"/></Positioned>')


def seg(x1, y1, x2, y2, t, color):
    import math
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 0.01:
        return ""
    ang = math.degrees(math.atan2(dy, dx))
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    bw = L + t
    return (f'<Positioned left="{round(cx - bw / 2, 2)}" top="{round(cy - t / 2, 2)}" '
            f'width="{round(bw, 2)}" height="{t}">'
            f'<Transform matrix="({math.cos(math.radians(ang)):.6f},'
            f'{math.sin(math.radians(ang)):.6f},0,0,'
            f'{-math.sin(math.radians(ang)):.6f},{math.cos(math.radians(ang)):.6f},'
            f'0,0,0,0,1,0,0,0,0,1)" alignment="CENTER">'
            f'<Container width="{round(bw, 2)}" height="{t}" color="{color}" '
            f'borderRadius="{round(t / 2, 2)}"/></Transform></Positioned>')


def wordmark(x, y, cn_size, en_size, cn_color, en_color, cn_family=F_SC, en_family=F_HEAD):
    """叠光 / Layerlight 字标：中文与拉丁并排，中文用 Noto Sans CJK SC 独立字族。"""
    cn_w = cn_size * 2 + 4
    return (txt(BRAND_CN, x, y, cn_w, cn_size + 12, cn_size, cn_color, cn_family) +
            txt(BRAND_EN, x + cn_w + cn_size * 0.5, y + cn_size * 0.22,
                en_size * 7.6, en_size + 14, en_size, en_color, en_family))


# ---------------------------------------------------------------- 1/2 符号
def page_symbol(pal: dict) -> str:
    S = 512
    return ('<Snapshot type="png">\n<Container width="512" height="512">\n<Stack fit="EXPAND">'
            + symbol(DIR, S / 2, S / 2, S, pal) +
            '</Stack></Container>\n</Snapshot>\n')


# ---------------------------------------------------------------- 3 横幅 1200×400
def page_banner() -> str:
    """横幅：横向锁定式（左符号 / 中字标+标语 / 右信息面板）三区构图。"""
    W, H = 1200, 400
    P = PAL_COLOR
    body = [rect(0, 0, W, H, "#071428")]
    # 背景装饰：层格母形拉长后出血，压到最低对比，只在信息区之外
    for i, yy in enumerate((330, 356, 382)):
        body.append(rect(880 + i * 10, yy, 330, 8, "#1E3A8A", 4))
    body.append(rect(1000, 52, 220, 8, "#12306B", 4))
    body.append(rect(0, 0, 16, H, P["ring"]))

    # 符号（同一几何规则现场生成，等比缩放 + 平移，无变形）
    S = 180
    body.append(rect(72, 92, 216, 216, "#FFFFFF0F", 24))
    body.append(f'<Positioned left="90" top="110" width="{S}" height="{S}">'
                f'<Container width="{S}" height="{S}" color="#FFFFFF00">'
                f'<Stack fit="EXPAND">{symbol(DIR, S / 2, S / 2, S, P)}</Stack>'
                f'</Container></Positioned>')

    # 中区：字标 + 分隔线 + 标语
    tx = 316
    body.append(wordmark(tx, 124, 58, 44, "#FFFFFF", "#93C5FD"))
    body.append(seg(tx, 226, 856, 226, 2.5, "#1E40AF"))
    body.append(txt(TAGLINE, tx, 246, 540, 56, 30, "#CBD5E1", F_MIX))

    # 右区：信息面板
    px0, py0, pw, ph = 880, 88, 256, 224
    body.append(rect(px0, py0, pw, ph, "#FFFFFF12", 18, "#1E40AF"))
    body.append(txt(BETA, px0 + 22, 112, pw - 44, 40, 24, "#F59E0B", F_HEAD, spacing="2"))
    body.append(seg(px0 + 22, 158, px0 + pw - 22, 158, 1.5, "#1E40AF"))
    for i, (lab, val, sz, col) in enumerate(
            (("日期 DATE", "2026.11.07", 22, "#E2E8F0"),
             ("地点 PLACE", "ONLINE", 22, "#E2E8F0"))):
        yy = 172 + i * 56
        body.append(txt(lab, px0 + 22, yy, pw - 44, 22, 16, "#64748B", F_MIX))
        body.append(txt(val, px0 + 22, yy + 22, pw - 44, 30, sz, col, F_HEAD))
    body.append(txt(SITE, px0 + 22, 284, pw - 44, 26, 17, "#93C5FD", F_LAT))
    return (f'<Snapshot type="png">\n<Container width="{W}" height="{H}" color="#071428">'
            f'<Stack fit="EXPAND">{"".join(body)}</Stack></Container>\n</Snapshot>\n')


# ---------------------------------------------------------------- 4 海报 1080×1350
def page_poster() -> str:
    W, H = 1080, 1350
    P = PAL_COLOR
    S = 420
    body = []
    body.append(rect(0, 0, W, H, "#071428"))
    # 独立构图：上部大符号出血，右上角斜向光带，中部大标题，底部信息栅格
    body.append(rect(0, 0, W, 18, P["ring"]))
    body.append(rect(690, 0, 390, 18, "#0F172A"))

    body.append(seg(720, 150, 1080, 60, 26, "#F59E0B"))
    body.append(seg(760, 230, 1080, 158, 14, "#0F766E"))

    body.append(f'<Positioned left="80" top="96" width="400" height="400">'
                f'<Stack fit="EXPAND">{symbol(DIR, 200, 200, 400, P)}</Stack></Positioned>')
    body.append(txt("BRAND SYSTEM · 01", 80, 556, 500, 26, 22, "#64748B", F_LAT, spacing="3"))

    body.append(txt("叠光", 80, 600, 260, 92, 82, "#FFFFFF", F_SC))
    body.append(txt("Layerlight", 80, 700, 620, 66, 56, "#93C5FD", F_HEAD, spacing="1"))
    body.append(seg(80, 796, 1000, 796, 2.5, "#1E40AF"))
    body.append(txt(TAGLINE, 80, 824, 900, 90, 42, "#E2E8F0", F_MIX))

    # 中部信息块（独立于横幅的栅格）：日期与地点按题面原样给成一行完整字样（保留中间的间隔号）
    body.append(rect(80, 950, 920, 120, "#FFFFFF0D", 16, "#1E40AF"))
    body.append(txt("日期 · 地点 DATE · PLACE", 104, 972, 500, 24, 20, "#64748B", F_MIX))
    body.append(txt(EVENT_LINE, 104, 1000, 700, 48, 40, "#E2E8F0", F_HEAD))

    body.append(rect(80, 1104, 920, 96, P["ring"], 18))
    body.append(txt(BETA, 110, 1126, 340, 52, 34, "#FFFFFF", F_HEAD, spacing="3"))
    body.append(txt(SITE, 500, 1134, 470, 40, 30, "#BFDBFE", F_LAT, align="RIGHT"))

    body.append(seg(80, 1240, 1000, 1240, 1.6, "#1E40AF"))
    body.append(txt("结构化视觉工具 · 信息叠加后仍然清晰", 80, 1258, 620, 28, 20, "#64748B", F_MIX))
    body.append(txt("LAYERLIGHT · BRAND GUIDELINES 2026", 560, 1258, 440, 28, 20, "#475569",
                    F_LAT, align="RIGHT"))
    body.append(rect(0, H - 12, W, 12, "#0F766E"))
    return (f'<Snapshot type="png">\n<Container width="{W}" height="{H}" color="#071428">'
            f'<Stack fit="EXPAND">{"".join(body)}</Stack></Container>\n</Snapshot>\n')


def main() -> None:
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    base = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    d = base / DRAFTS
    d.mkdir(parents=True, exist_ok=True)
    outs = {
        "symbol-color": page_symbol(PAL_COLOR),
        "symbol-black": page_symbol(PAL_BLACK),
        "brand-banner": page_banner(),
        "launch-poster": page_poster(),
    }
    for name, dsl in outs.items():
        (d / f"a13-{name}-{ver}.snapshot").write_text(dsl, encoding="utf-8")
        print(f"a13-{name}-{ver}.snapshot bytes={len(dsl.encode())}")
    (d / "components-selected.json").write_text(
        json.dumps(components_of(DIR), ensure_ascii=False, indent=2), encoding="utf-8")
    (d / "negative-space.json").write_text(
        json.dumps({"direction": DIR, "negative_space": NEGATIVE_SPACE_B},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    print("direction:", DIR, DIRECTION_NAME[DIR], "| components:", len(components_of(DIR)))


if __name__ == "__main__":
    main()