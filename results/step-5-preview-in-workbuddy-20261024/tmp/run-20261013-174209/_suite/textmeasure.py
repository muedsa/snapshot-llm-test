"""文本宽度测量工具（渲染透明底文字后统计非透明像素范围）。

用法：在总任务根运行，导入 measure(text, font_size, font_family, font_style) 获取
{width, height, left, top, right, bottom}（像素，画布左上原点）。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / os.environ.get("SNAPSHOT_RUN_ID", "") / "_suite"))
import render as R  # noqa: E402

_CACHE: dict[tuple[str, float, str, str], dict[str, Any]] = {}


def measure(
    text: str,
    font_size: float = 20,
    font_family: str = "Noto Sans CJK SC",
    font_style: str = "NORMAL",
    task_id: str = "MEASURE",
) -> dict[str, Any]:
    key = (text, font_size, font_family, font_style)
    if key in _CACHE:
        return _CACHE[key]
    esc = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    dsl = (
        '<Snapshot type="png" background="transparent">'
        '<Container alignment="TOP_LEFT">'
        f'<Text fontSize="{font_size}" fontFamily="{font_family}" fontStyle="{font_style}" '
        f'textAlign="LEFT" softWrap="false" maxLines="1">{esc}</Text>'
        "</Container></Snapshot>"
    )
    tmp = ROOT / "tmp" / os.environ.get("SNAPSHOT_RUN_ID", "run") / task_id / "_measure"
    tmp.mkdir(parents=True, exist_ok=True)
    dsl_file = tmp / f"m{abs(hash(key))}.snapshot"
    dsl_file.write_text(dsl, encoding="utf-8")
    log = R.Log(ROOT, os.environ.get("SNAPSHOT_RUN_ID", "run"), task_id)
    res = R.render(dsl_file, tmp / f"m{abs(hash(key))}.png", ROOT, log, req_type="measure",
                   label=f"measure:{text[:24]}")
    if res["record"]["status"] != "ok":
        return {"error": res["record"].get("error"), "width": None, "height": None}
    from PIL import Image  # noqa: PLC0415

    with Image.open(tmp / f"m{abs(hash(key))}.png") as im:
        rgba = im.convert("RGBA")
        bbox = rgba.getbbox()
        w, h = im.size
    out = {
        "width": (bbox[2] - bbox[0]) if bbox else 0,
        "height": (bbox[3] - bbox[1]) if bbox else 0,
        "left": bbox[0] if bbox else 0,
        "top": bbox[1] if bbox else 0,
        "right": bbox[2] if bbox else w,
        "bottom": bbox[3] if bbox else h,
        "canvas_width": w,
        "canvas_height": h,
    }
    _CACHE[key] = out
    return out


if __name__ == "__main__":
    print(measure("测试文本 12,345", 20))
