"""A15 探针第 3 轮：副标题/Overview/按钮文字/¥ thousand/活动名 精修。"""
from __future__ import annotations
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "run")
sys.path.insert(0, str(ROOT / "tmp" / RUN_ID / "_suite"))
import render as R  # noqa: E402

TASK = "A15"
TMP = ROOT / "tmp" / RUN_ID / TASK / "_measure"
TMP.mkdir(parents=True, exist_ok=True)

ITEMS = [
    ("Saturday, 07 November 2026", 17.5, "NORMAL", "Inter", None),
    ("Saturday, 07 November 2026", 18, "NORMAL", "Inter", None),
    ("Overview", 16, "BOLD", "Inter", "1.2"),
    ("Overview", 17, "BOLD", "Inter", "1"),
    ("Overview", 16, "BOLD", "Inter", "1.4"),
    ("Export report", 16.5, "BOLD", "Inter", None),
    ("Export report", 16.5, "NORMAL", "Inter Semi Bold", None),
    ("Export report", 17, "BOLD", "Inter", None),
    ("¥ thousand", 13, "NORMAL", "Inter", None),
    ("Design review", 17.5, "NORMAL", "Inter Semi Bold", None),
    ("Dataset updated", 17.5, "NORMAL", "Inter Semi Bold", None),
    ("Render complete", 17.5, "NORMAL", "Inter Semi Bold", None),
]


def cdata(s):
    assert "]]>" not in s
    return f"<![CDATA[{s}]]>"


def main():
    max_size = max(it[1] for it in ITEMS)
    rh = int(max_size + 40)
    canvas_w = 1440
    n = len(ITEMS)
    H = n * rh
    nodes = []
    for i, (text, size, style, fam, ls) in enumerate(ITEMS):
        ls_attr = f' letterSpacing="{ls}"' if ls else ""
        nodes.append(
            f'<Positioned left="30" top="{i * rh + 8}" width="{canvas_w - 60}" '
            f'height="{rh - 16}"><Container color="transparent">'
            f'<Text fontSize="{size}" fontFamily="{fam}" fontStyle="{style}"{ls_attr} '
            f'textAlign="LEFT" softWrap="false" maxLines="1">{cdata(text)}</Text>'
            f"</Container></Positioned>"
        )
    dsl = (f'<Snapshot type="png" background="transparent">'
           f'<Container width="{canvas_w}" height="{H}">'
           f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
           + "".join(nodes) + "</Stack></Container></Snapshot>")
    dsl_file = TMP / "a15-probe3.snapshot"
    dsl_file.write_text(dsl, encoding="utf-8")
    log = R.Log(ROOT, RUN_ID, TASK)
    res = None
    for attempt in range(4):
        res = R.render(dsl_file, TMP / "a15-probe3.png", ROOT, log,
                       req_type="measure-batch", label="a15-probe3")
        if res["record"]["status"] == "ok":
            break
        err = res["record"].get("error") or ""
        if any(k in err for k in ("Timeout", "URLError", "RemoteDisconnected",
                                  "handshake", "EOF occurred", "timed out")):
            time.sleep(2 + attempt * 2)
            continue
        break
    if res["record"]["status"] != "ok":
        print("FAILED:", res["record"].get("error"))
        return
    from PIL import Image
    with Image.open(TMP / "a15-probe3.png") as im:
        rgba = im.convert("RGBA")
        for i, (text, size, style, fam, ls) in enumerate(ITEMS):
            band = rgba.crop((0, i * rh, canvas_w, (i + 1) * rh))
            bbox = band.getbbox()
            ls_s = f" ls={ls}" if ls else ""
            if bbox:
                print(f"{text[:34]:36s} {size:>5} {style:6s}{ls_s:9s} "
                      f"L={bbox[0]-30} T={bbox[1]-8} w={bbox[2]-bbox[0]} h={bbox[3]-bbox[1]}")
            else:
                print(f"{text[:34]:36s} {size:>5} EMPTY")


if __name__ == "__main__":
    main()
