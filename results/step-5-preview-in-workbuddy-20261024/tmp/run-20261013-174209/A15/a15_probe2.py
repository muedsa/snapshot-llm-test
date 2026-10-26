"""A15 探针第 2 轮：最终候选字号/字距验证 + 修正 ink_top 公式。"""
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

# (text, size, style, family, letterSpacing or None)
ITEMS = [
    ("NORTHSTAR", 19, "BOLD", "Inter", None),
    ("Overview", 16, "BOLD", "Inter", "1"),
    ("Projects", 16, "NORMAL", "Inter", "1"),
    ("Projects", 16, "NORMAL", "Inter", "1.2"),
    ("Analytics", 16, "NORMAL", "Inter", "1"),
    ("Settings", 16, "NORMAL", "Inter", "1"),
    ("PRO WORKSPACE", 13, "BOLD", "Inter", None),
    ("12 team members", 16, "NORMAL", "Inter", None),
    ("Manage access →", 14.5, "NORMAL", "Inter", None),
    ("Workspace Overview", 32, "BOLD", "Inter", None),
    ("Saturday, 07 November 2026", 17, "NORMAL", "Inter", None),
    ("Export report", 16, "NORMAL", "Inter Semi Bold", None),
    ("Export report", 16, "NORMAL", "Inter Medium", None),
    ("Export report", 16, "BOLD", "Inter", None),
    ("REVENUE", 14, "NORMAL", "Inter Semi Bold", None),
    ("ORDERS", 14, "NORMAL", "Inter Semi Bold", None),
    ("REFUND RATE", 14, "NORMAL", "Inter Semi Bold", None),
    ("¥128,400", 32, "BOLD", "Inter", None),
    ("426", 32, "BOLD", "Inter", None),
    ("3.2%", 32, "BOLD", "Inter", None),
    ("+12.4%", 17, "NORMAL", "Inter Semi Bold", None),
    ("+8.1%", 17, "NORMAL", "Inter Semi Bold", None),
    ("−0.8 pp", 17, "NORMAL", "Inter Semi Bold", None),
    ("Net revenue", 22, "BOLD", "Inter", None),
    ("Apr – Sep", 17, "NORMAL", "Inter", None),
    ("¥ thousand", 14, "NORMAL", "Inter", None),
    ("120", 13, "NORMAL", "Inter", None),
    ("90", 13, "NORMAL", "Inter", None),
    ("0", 13, "NORMAL", "Inter", None),
    ("Apr", 13, "NORMAL", "Inter", None),
    ("May", 13, "NORMAL", "Inter", None),
    ("Jun", 13, "NORMAL", "Inter", None),
    ("Jul", 13, "NORMAL", "Inter", None),
    ("Aug", 13, "NORMAL", "Inter", None),
    ("Sep", 13, "NORMAL", "Inter", None),
    ("Team activity", 22, "BOLD", "Inter", None),
    ("Design review", 17, "NORMAL", "Inter Semi Bold", None),
    ("Dataset updated", 17, "NORMAL", "Inter Semi Bold", None),
    ("Render complete", 17, "NORMAL", "Inter Semi Bold", None),
    ("08:40", 14, "NORMAL", "Inter", None),
    ("09:15", 14, "NORMAL", "Inter", None),
    ("10:05", 14, "NORMAL", "Inter", None),
    ("Recent projects", 22, "BOLD", "Inter", None),
    ("PROJECT", 12, "BOLD", "Inter", None),
    ("OWNER", 12, "BOLD", "Inter", None),
    ("STATUS", 12, "BOLD", "Inter", None),
    ("DUE", 12, "BOLD", "Inter", None),
    ("Atlas / Visual system", 16, "NORMAL", "Inter Semi Bold", None),
    ("Pulse / Dashboard", 16, "NORMAL", "Inter Semi Bold", None),
    ("Orbit / Launch", 16, "NORMAL", "Inter Semi Bold", None),
    ("Lin Chuan", 16, "NORMAL", "Inter", None),
    ("Zhou He", 16, "NORMAL", "Inter", None),
    ("Su Yan", 16, "NORMAL", "Inter", None),
    ("In progress", 13, "NORMAL", "Inter Semi Bold", None),
    ("Review", 13, "NORMAL", "Inter Semi Bold", None),
    ("Done", 13, "NORMAL", "Inter Semi Bold", None),
    ("Nov 09", 16, "NORMAL", "Inter", None),
    ("Nov 11", 16, "NORMAL", "Inter", None),
    ("Nov 12", 16, "NORMAL", "Inter", None),
    ("All data is fictional · Snapshot benchmark", 12.5, "NORMAL", "Inter", None),
]


def cdata(s: str) -> str:
    assert "]]>" not in s
    return f"<![CDATA[{s}]]>"


def main():
    max_size = max(it[1] for it in ITEMS)
    rh = int(max_size + 40)
    canvas_w = 1440
    per_chunk = 3900 // rh
    out = []
    from PIL import Image
    for start in range(0, len(ITEMS), per_chunk):
        chunk = ITEMS[start:start + per_chunk]
        n = len(chunk)
        H = n * rh
        nodes = []
        for i, (text, size, style, fam, ls) in enumerate(chunk):
            ls_attr = f' letterSpacing="{ls}"' if ls else ""
            nodes.append(
                f'<Positioned left="30" top="{i * rh + 8}" width="{canvas_w - 60}" '
                f'height="{rh - 16}"><Container color="transparent">'
                f'<Text fontSize="{size}" fontFamily="{fam}" fontStyle="{style}"{ls_attr} '
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
        dsl_file = TMP / f"a15-probe2-{tagv}.snapshot"
        dsl_file.write_text(dsl, encoding="utf-8")
        log = R.Log(ROOT, RUN_ID, TASK)
        res = None
        for attempt in range(4):
            res = R.render(dsl_file, TMP / f"a15-probe2-{tagv}.png", ROOT, log,
                           req_type="measure-batch", label=f"a15-probe2-{tagv}({n}items)")
            if res["record"]["status"] == "ok":
                break
            err = res["record"].get("error") or ""
            if any(k in err for k in ("Timeout", "URLError", "RemoteDisconnected",
                                      "handshake", "EOF occurred", "timed out")):
                time.sleep(2 + attempt * 2)
                continue
            break
        if res["record"]["status"] != "ok":
            print(f"CHUNK {tagv} FAILED:", res["record"].get("error"))
            return
        with Image.open(TMP / f"a15-probe2-{tagv}.png") as im:
            rgba = im.convert("RGBA")
            for i, (text, size, style, fam, ls) in enumerate(chunk):
                band = rgba.crop((0, i * rh, canvas_w, (i + 1) * rh))
                bbox = band.getbbox()
                if bbox:
                    out.append({
                        "text": text, "size": size, "style": style, "family": fam,
                        "ls": ls,
                        "ink_left": bbox[0] - 30, "ink_top": bbox[1] - 8,
                        "w": bbox[2] - bbox[0], "h": bbox[3] - bbox[1],
                    })
                else:
                    out.append({"text": text, "size": size, "style": style,
                                "family": fam, "ls": ls, "ink_left": None,
                                "ink_top": None, "w": 0, "h": 0})
    (TMP / "a15-probe2.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in out:
        ls = f" ls={r['ls']}" if r["ls"] else ""
        print(f"{r['text'][:36]:38s} {r['size']:>5} {r['style']:6s} {r['family']:16s}{ls:9s} "
              f"L={r['ink_left']} T={r['ink_top']} w={r['w']} h={r['h']}")


if __name__ == "__main__":
    main()
