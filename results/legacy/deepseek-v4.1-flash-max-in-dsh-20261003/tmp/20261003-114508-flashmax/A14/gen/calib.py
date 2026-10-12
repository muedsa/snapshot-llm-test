"""A14 · step 1: measure the real font advances instead of guessing them.

Renders one probe sheet with every string class A14 needs at 72px, then (after the
service reply is on disk) reads the ink extent of each row with Pillow. The resulting
per-class advances drive the title wrapping in build_cards.py.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A14"
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
from dslkit import Doc, CJK, MONO  # noqa: E402

SIZE = 72
ROWS = [
    ("cjk20", "开始开始开始开始开始开始开始开始开始开始"),
    ("latinA10", "AAAAAAAAAA"),
    ("digits10", "0123456789"),
    ("k04", "A < B & C > D：不要把文本当成标签"),
    ("k05", "Color, Alpha & Contrast / 从颜色到可读性"),
    ("k08", "从“已经请求成功”到“已经完成作品”：模型工作能力的最后一公里"),
    ("k07", "把一次失败变成可复现记录——服务、字体、数据与视觉检查"),
    ("symbols", "○ ● ◐ ×"),
    ("brand", "Structure / Vision"),
    ("lower26", "abcdefghijklmnopqrstuvwxyz"),
    ("k03", "当所有信息都想成为标题：密集内容中的取舍与层级"),
    ("k06", "两张看似相同的图片，为什么不能证明语义相同？"),
    ("k02", "读文档，也要读懂布局约束"),
    ("speaker_long", "Northstar Research · 林川"),
    ("cancel_note", "本场取消"),
    ("cjk_punct", "：，、。？！“”—"),
]
ROW_H = 140        # 72px text occupies a ~94px line box; v1 used 76 and rows bled into
                   # each other, which is why the first measurement was nonsense.
BAND_H = 104
W, H = 2600, 40 + ROW_H * len(ROWS) + 20


def build() -> str:
    d = Doc(W, H, background="#FFFFFF")
    for i, (key, s) in enumerate(ROWS):
        y = 20 + i * ROW_H
        d.box(0, y + 62, 24, 3, "#94A3B8")          # baseline marker column
        d.text(40, y, s, SIZE, "#0F172A")
    return d.finish()


def measure() -> dict:
    from PIL import Image
    png = os.path.join(TMP, "probe", "probe.advances.v2.png")
    im = Image.open(png).convert("RGB")
    out = {}
    for i, (key, s) in enumerate(ROWS):
        y0 = 20 + i * ROW_H
        band = im.crop((24, y0, W, y0 + BAND_H))
        # ink = anything darker than the white background
        px = band.load()
        bw, bh = band.size
        left = right = None
        for x in range(bw):
            col_has_ink = any(sum(px[x, y]) < 690 for y in range(bh))
            if col_has_ink:
                if left is None:
                    left = x
                right = x
        if left is None:
            out[key] = dict(text=s, ink_px=None, advance_em=None, note="no ink found")
            continue
        ink = right - left + 1
        # the marker column at local x 0..24 is skipped by starting the crop at 24,
        # so `left` is relative to x=24 (the text origin at x=40 -> local 16)
        out[key] = dict(text=s, ink_px=ink, chars=len(s),
                        advance_em=round(ink / SIZE / len(s), 4))
    return out


if __name__ == "__main__":
    os.makedirs(os.path.join(TMP, "dsl"), exist_ok=True)
    p = os.path.join(TMP, "dsl", "probe.advances.v1.snapshot")
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(build())
    print("probe dsl written:", p, os.path.getsize(p), "bytes")
    if os.path.exists(os.path.join(TMP, "probe", "probe.advances.v1.png")):
        m = measure()
        with open(os.path.join(TMP, "probe", "advances.json"), "w", encoding="utf-8") as fh:
            json.dump(m, fh, ensure_ascii=False, indent=2)
        print(json.dumps(m, ensure_ascii=False, indent=2))
