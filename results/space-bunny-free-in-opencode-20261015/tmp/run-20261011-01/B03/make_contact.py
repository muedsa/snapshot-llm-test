#!/usr/bin/env python
"""把探针 PNG 拼成带标签的接触表，便于一次看全一批实验结果。

探针只是中间实验，接触表够用；最终作品的检查一律逐张打开原图。
启动基准：总任务根。  用法：python make_contact.py <输入目录> <输出png> [列数]
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]


def main() -> None:
    src_dir = ROOT / sys.argv[1]
    out = ROOT / sys.argv[2]
    cols = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    files = sorted(src_dir.glob("*.png"))
    if not files:
        print("no png")
        return
    cell = 300
    label_h = 26
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell, rows * (cell + label_h)), "#0A0F1E")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 15)
    except Exception:  # noqa: BLE001
        font = ImageFont.load_default()
    for i, f in enumerate(files):
        im = Image.open(f).convert("RGB")
        im.thumbnail((cell - 8, cell - 8))
        cx, cy = (i % cols) * cell, (i // cols) * (cell + label_h)
        sheet.paste(im, (cx + 4, cy + label_h + 4))
        draw.text((cx + 6, cy + 5), f.stem, fill="#F2F6FC", font=font)
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print(f"{out}  {len(files)} imgs  {sheet.size}")


if __name__ == "__main__":
    main()