"""批量文本宽度测量（一次渲染测量多条字符串）。

启动基准：从总任务根运行，或设置 SNAPSHOT_TASK_ROOT 指向总任务根；
需要 SNAPSHOT_RUN_ID。用法：

    from bm import batch_measure
    widths = batch_measure([
        {"text": "Structure / Vision", "size": 40, "style": "BOLD"},
        {"text": "云构中心 · ONLINE", "size": 16},
    ])
    # widths[i] = {"width": px, "height": px}

渲染一张透明底大画布，每条字符串一行（softWrap=false, maxLines=1），
用 PIL 按行带裁剪统计墨迹范围得到精确像素宽度。测量请求计入
tmp/<run_id>/<task_id>/requests.jsonl（type=measure-batch）。
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "run")
sys.path.insert(0, str(ROOT / "tmp" / RUN_ID / "_suite"))
import render as R  # noqa: E402

SANS = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def cdata(s: str) -> str:
    """文本内容用 CDATA 包裹：解析器不解码 HTML 实体，裸字符需原样传入。"""
    assert "]]>" not in s, "text contains ]]> which cannot appear in CDATA"
    return f"<![CDATA[{s}]]>"


def batch_measure(
    items: list[dict[str, Any]],
    task_id: str = "MEASURE",
    label: str = "measure-batch",
    row_h: int | None = None,
    canvas_w: int = 3000,
) -> list[dict[str, Any]]:
    """一次渲染测量全部条目，返回与 items 等长的 {width,height} 列表。

    服务画布上限 4096px，按行高自动分块，每块单独渲染。
    """
    if not items:
        return []
    max_size = max(float(i.get("size", 20)) for i in items)
    rh = row_h or int(max_size + 34)
    per_chunk = max(1, 3900 // rh)
    out: list[dict[str, Any]] = []
    for start in range(0, len(items), per_chunk):
        chunk = items[start:start + per_chunk]
        out.extend(_measure_one(chunk, task_id, label, rh, canvas_w,
                                tag=start // per_chunk))
    return out


def _measure_one(
    items: list[dict[str, Any]],
    task_id: str,
    label: str,
    rh: int,
    canvas_w: int,
    tag: int = 0,
) -> list[dict[str, Any]]:
    n = len(items)
    H = n * rh
    nodes = []
    for i, it in enumerate(items):
        fam = it.get("family", SANS)
        style = it.get("style", "NORMAL")
        nodes.append(
            f'<Positioned left="30" top="{i * rh + 8}" width="{canvas_w - 60}" '
            f'height="{rh - 16}"><Container color="transparent">'
            f'<Text fontSize="{it.get("size", 20)}" fontFamily="{fam}" '
            f'fontStyle="{style}" textAlign="LEFT" softWrap="false" maxLines="1">'
            f"{cdata(it['text'])}</Text></Container></Positioned>"
        )
    dsl = (
        f'<Snapshot type="png" background="transparent">'
        f'<Container width="{canvas_w}" height="{H}">'
        f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
        + "".join(nodes) + "</Stack></Container></Snapshot>"
    )
    tmp = ROOT / "tmp" / RUN_ID / task_id / "_measure"
    tmp.mkdir(parents=True, exist_ok=True)
    tagv = abs(hash((json.dumps(items, ensure_ascii=False, sort_keys=True), tag))) % 10**12
    dsl_file = tmp / f"bm{tagv}.snapshot"
    dsl_file.write_text(dsl, encoding="utf-8")
    log = R.Log(ROOT, RUN_ID, task_id)
    # 网络层故障（SSL 超时/连接中断）原样重试，最多 4 次
    res = None
    for attempt in range(4):
        res = R.render(dsl_file, tmp / f"bm{tagv}.png", ROOT, log, req_type="measure-batch",
                       label=f"{label}({n}items#{tag})")
        if res["record"]["status"] == "ok":
            break
        err = res["record"].get("error") or ""
        if any(k in err for k in ("Timeout", "URLError", "RemoteDisconnected",
                                  "handshake", "EOF occurred", "timed out")):
            time.sleep(2 + attempt * 2)
            continue
        break
    if res["record"]["status"] != "ok":
        return [{"width": None, "height": None, "error": res["record"].get("error")}
                for _ in items]
    from PIL import Image  # noqa: PLC0415

    out: list[dict[str, Any]] = []
    with Image.open(tmp / f"bm{tagv}.png") as im:
        rgba = im.convert("RGBA")
        for i in range(n):
            band = rgba.crop((0, i * rh, canvas_w, (i + 1) * rh))
            bbox = band.getbbox()
            if bbox:
                out.append({"width": bbox[2] - bbox[0], "height": bbox[3] - bbox[1]})
            else:
                out.append({"width": 0, "height": 0})
    return out


def wrap_text(text: str, maxw: float, widths: dict[str, float]) -> list[str]:
    """用已测量的字符宽度表做贪心折行（CJK 按字符断，拉丁按空格断）。"""
    if not text:
        return [""]
    # 将文本切成 token：CJK 单字成 token，拉丁连续串成 token，空格归入前一 token
    tokens: list[tuple[str, bool]] = []  # (token, is_space)
    buf = ""
    for ch in text:
        if ord(ch) > 0x2E7F:  # CJK 及全角标点
            if buf:
                tokens.append((buf, False))
                buf = ""
            tokens.append((ch, False))
        elif ch == " ":
            if buf:
                tokens.append((buf, False))
                buf = ""
            tokens.append((" ", True))
        else:
            buf += ch
    if buf:
        tokens.append((buf, False))

    def w(tok: str) -> float:
        return sum(widths.get(c, 0.0) for c in tok)

    lines: list[str] = []
    cur = ""
    cur_w = 0.0
    for tok, is_sp in tokens:
        tw = w(tok)
        if is_sp:
            if cur:
                cur += tok
                cur_w += tw
            continue
        if cur and cur_w + tw > maxw + 0.5:
            lines.append(cur.rstrip())
            cur = tok
            cur_w = tw
        else:
            cur += tok
            cur_w += tw
    if cur:
        lines.append(cur.rstrip())
    return lines or [""]


if __name__ == "__main__":
    demo = batch_measure([
        {"text": "Structure / Vision", "size": 40, "style": "BOLD"},
        {"text": "云构中心 · ONLINE", "size": 16},
    ], task_id="MEASURE", label="bm-selftest")
    print(json.dumps(demo, ensure_ascii=False))
