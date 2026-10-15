#!/usr/bin/env python
"""A13 两个几何方向的 512×512 透明预览（仅临时目录，供看图选择）。

启动基准：总任务根 (suite_root)。
用法：python tmp/run-20261011-01/A13/build_directions.py
输出：drafts/dir-A.snapshot / dir-B.snapshot（各 512×512 透明）
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/A13")
from geom_a13 import PAL_COLOR, symbol, DIRECTION_NAME  # noqa: E402

DRAFTS = "tmp/run-20261011-01/A13/drafts"
S = 512


def page(direction: str) -> str:
    """512×512 透明底：只画图标本身（预览用，不带任何底色或文字）。"""
    return ('<Snapshot type="png">\n<Container width="%d" height="%d">\n<Stack fit="EXPAND">'
            '%s</Stack></Container>\n</Snapshot>\n'
            % (S, S, symbol(direction, S / 2, S / 2, S, PAL_COLOR)))


def sheet() -> str:
    """并排对照图（浅底，便于肉眼比较轮廓与负空间）。"""
    W, H = 1160, 600
    tiles = []
    for i, d in enumerate(("A", "B")):
        x = 40 + i * 560
        tiles.append(f'<Positioned left="{x}" top="60" width="520" height="520">'
                     f'<Container width="520" height="520" color="#FFFFFF" borderRadius="20" '
                     f'border="2 SOLID #CBD5E1"/></Positioned>')
        # 把 512 画布的图标等比缩到 420 放在浅底上（只此对照图做缩放，交付图不做）
        tiles.append(f'<Positioned left="{x + 50}" top="110" width="420" height="420">'
                     f'<Container width="420" height="420" color="#F8FAFC" borderRadius="12">'
                     f'<Stack fit="EXPAND">{symbol(d, 210, 210, 420, PAL_COLOR)}</Stack>'
                     f'</Container></Positioned>')
        tiles.append(f'<Positioned left="{x}" top="24" width="520" height="30">'
                     f'<Text fontSize="22" color="#0F172A" fontFamily="Inter Semi Bold,Noto Sans CJK SC" '
                     f'text="方向 {d} · {DIRECTION_NAME[d]}"/></Positioned>')
    body = "".join(tiles)
    return (f'<Snapshot type="png">\n<Container width="{W}" height="{H}" color="#F1F5F9">'
            f'<Stack fit="EXPAND">{body}</Stack></Container>\n</Snapshot>\n')


def main() -> None:
    base = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    d = base / DRAFTS
    d.mkdir(parents=True, exist_ok=True)
    for k in ("A", "B"):
        s = page(k)
        (d / f"dir-{k}.snapshot").write_text(s, encoding="utf-8")
        print(f"dir-{k}.snapshot bytes={len(s.encode())}")
    sh = sheet()
    (d / "dir-sheet.snapshot").write_text(sh, encoding="utf-8")
    print("dir-sheet.snapshot bytes=", len(sh.encode()))


if __name__ == "__main__":
    main()