"""A15 字体探针：一次渲染测量所有文本的墨迹 left/top 偏移与宽高（Inter 字体族）。

用法：在总任务根设置 SNAPSHOT_TASK_ROOT / SNAPSHOT_RUN_ID 后运行。
返回每条的 {text, size, style, family, ink_left, ink_top, w, h}，其中
ink_left/ink_top 是相对于 Positioned 文本框左上角的墨迹偏移。
"""
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

# (text, size, style, family)
ITEMS = [
    ("NORTHSTAR", 19, "BOLD", "Inter"),
    ("NORTHSTAR", 20, "BOLD", "Inter"),
    ("Overview", 16, "BOLD", "Inter"),
    ("Projects", 16, "NORMAL", "Inter"),
    ("Analytics", 16, "NORMAL", "Inter"),
    ("Settings", 16, "NORMAL", "Inter"),
    ("PRO WORKSPACE", 13, "BOLD", "Inter"),
    ("PRO WORKSPACE", 13, "NORMAL", "Inter Semi Bold"),
    ("12 team members", 15, "NORMAL", "Inter"),
    ("Manage access →", 14, "NORMAL", "Inter"),
    ("Workspace Overview", 30, "BOLD", "Inter"),
    ("Workspace Overview", 32, "BOLD", "Inter"),
    ("Saturday, 07 November 2026", 16, "NORMAL", "Inter"),
    ("Export report", 16, "BOLD", "Inter"),
    ("Export report", 16, "NORMAL", "Inter Semi Bold"),
    ("REVENUE", 14, "NORMAL", "Inter Semi Bold"),
    ("REVENUE", 15, "NORMAL", "Inter Semi Bold"),
    ("REVENUE", 16, "NORMAL", "Inter Semi Bold"),
    ("REFUND RATE", 15, "NORMAL", "Inter Semi Bold"),
    ("¥128,400", 40, "BOLD", "Inter"),
    ("¥128,400", 38, "BOLD", "Inter"),
    ("426", 40, "BOLD", "Inter"),
    ("3.2%", 40, "BOLD", "Inter"),
    ("+12.4%", 17, "NORMAL", "Inter Semi Bold"),
    ("+12.4%", 18, "NORMAL", "Inter Semi Bold"),
    ("−0.8 pp", 18, "NORMAL", "Inter Semi Bold"),
    ("Net revenue", 22, "BOLD", "Inter"),
    ("Net revenue", 24, "BOLD", "Inter"),
    ("Apr – Sep", 16, "NORMAL", "Inter"),
    ("Apr – Sep", 18, "NORMAL", "Inter"),
    ("¥ thousand", 14, "NORMAL", "Inter"),
    ("¥ thousand", 15, "NORMAL", "Inter"),
    ("120", 13, "NORMAL", "Inter"),
    ("120", 14, "NORMAL", "Inter"),
    ("Apr", 15, "NORMAL", "Inter"),
    ("Team activity", 22, "BOLD", "Inter"),
    ("Design review", 17, "NORMAL", "Inter Semi Bold"),
    ("Design review", 18, "NORMAL", "Inter Semi Bold"),
    ("08:40", 15, "NORMAL", "Inter"),
    ("08:40", 16, "NORMAL", "Inter"),
    ("Recent projects", 22, "BOLD", "Inter"),
    ("PROJECT", 13, "BOLD", "Inter"),
    ("PROJECT", 14, "BOLD", "Inter"),
    ("OWNER", 14, "BOLD", "Inter"),
    ("STATUS", 14, "BOLD", "Inter"),
    ("DUE", 14, "BOLD", "Inter"),
    ("Atlas / Visual system", 20, "NORMAL", "Inter Semi Bold"),
    ("Atlas / Visual system", 19, "BOLD", "Inter"),
    ("Lin Chuan", 16, "NORMAL", "Inter"),
    ("In progress", 13, "NORMAL", "Inter Semi Bold"),
    ("Review", 13, "NORMAL", "Inter Semi Bold"),
    ("Done", 13, "NORMAL", "Inter Semi Bold"),
    ("Nov 09", 16, "NORMAL", "Inter"),
    ("All data is fictional · Snapshot benchmark", 13, "NORMAL", "Inter"),
]


def cdata(s: str) -> str:
    assert "]]>" not in s
    return f"<![CDATA[{s}]]>"


def main():
    max_size = max(it[1] for it in ITEMS)
    rh = int(max_size + 40)
    canvas_w = 1440
    # 服务画布上限 4096：按 2 块渲染
    per_chunk = 3900 // rh
    out = []
    from PIL import Image
    for start in range(0, len(ITEMS), per_chunk):
        chunk = ITEMS[start:start + per_chunk]
        n = len(chunk)
        H = n * rh
        nodes = []
        for i, (text, size, style, fam) in enumerate(chunk):
            nodes.append(
                f'<Positioned left="30" top="{i * rh + 8}" width="{canvas_w - 60}" '
                f'height="{rh - 16}"><Container color="transparent">'
                f'<Text fontSize="{size}" fontFamily="{fam}" fontStyle="{style}" '
                f'textAlign="LEFT" softWrap="false" maxLines="1">{cdata(text)}</Text>'
                f"</Container></Positioned>"
            )
        dsl = (
            f'<Snapshot type="png" background="transparent">'
            f'<Container width="{canvas_w}" height="{H}">'
            f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
            + "".join(nodes) + "</Stack></Container></Snapshot>"
        )
        tagv = start // per_chunk
        dsl_file = TMP / f"a15-probe-{tagv}.snapshot"
        dsl_file.write_text(dsl, encoding="utf-8")
        log = R.Log(ROOT, RUN_ID, TASK)
        res = None
        for attempt in range(4):
            res = R.render(dsl_file, TMP / f"a15-probe-{tagv}.png", ROOT, log,
                           req_type="measure-batch", label=f"a15-probe-{tagv}({n}items)")
            if res["record"]["status"] == "ok":
                break
            err = res["record"].get("error") or ""
            if any(k in err for k in ("Timeout", "URLError", "RemoteDisconnected",
                                      "handshake", "EOF occurred", "timed out")):
                time.sleep(2 + attempt * 2)
                continue
            break
        if res["record"]["status"] != "ok":
            print(f"CHUNK {tagv} RENDER FAILED:", res["record"].get("error"))
            return
        with Image.open(TMP / f"a15-probe-{tagv}.png") as im:
            rgba = im.convert("RGBA")
            for i, (text, size, style, fam) in enumerate(chunk):
                band = rgba.crop((0, i * rh, canvas_w, (i + 1) * rh))
                bbox = band.getbbox()
                if bbox:
                    out.append({
                        "text": text, "size": size, "style": style, "family": fam,
                        "ink_left": bbox[0] - 30, "ink_top": bbox[1] - (i * rh + 8),
                        "w": bbox[2] - bbox[0], "h": bbox[3] - bbox[1],
                    })
                else:
                    out.append({"text": text, "size": size, "style": style,
                                "family": fam, "ink_left": None, "ink_top": None,
                                "w": 0, "h": 0})
    (TMP / "a15-probe.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in out:
        print(f"{r['text'][:34]:36s} {r['size']:>3} {r['style']:6s} {r['family']:16s} "
              f"L={r['ink_left']} T={r['ink_top']} w={r['w']} h={r['h']}")


if __name__ == "__main__":
    main()
