# -*- coding: utf-8 -*-
"""Region ink-bbox measurement of the flawed reference report.

Every bbox written here is used verbatim as the "图片位置" evidence in findings.json.
Observation only: the reference PNG is never cropped into a deliverable.
"""
import json, os
from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
SRC = os.path.join(ROOT, "tasks", "A16-visual-data-forensics", "inputs", "flawed-report.png")
TMP = os.path.join(ROOT, "tmp", "20261004-182918", "A16")
im = Image.open(SRC).convert("RGB")
px = im.load()

REGIONS = {
    "title": (40, 28, 760, 100),
    "subtitle": (40, 100, 760, 140),
    "panel_title": (70, 172, 430, 222),
    "unit_note": (70, 222, 280, 262),
    "legend_swatch_blue": (860, 172, 905, 214),
    "legend_label_cost": (902, 176, 1050, 212),
    "legend_swatch_orange": (1040, 172, 1084, 214),
    "legend_label_revenue": (1080, 176, 1200, 212),
    "profit_card_title": (70, 662, 320, 706),
    "profit_row_labels": (80, 706, 160, 800),
    "profit_q1": (80, 706, 210, 800),
    "profit_q2": (250, 706, 380, 800),
    "profit_q3": (420, 706, 550, 800),
    "profit_q4": (590, 706, 720, 800),
    "callout_title": (856, 668, 1180, 712),
    "callout_body": (856, 716, 1200, 800),
    "footer": (40, 848, 460, 890),
}
# value labels above the bars: band just above each measured bar top
BAR_TOPS = {
    "label_q1_rev": (224, 391, 288, 415), "label_q1_cost": (300, 430, 364, 454),
    "label_q2_rev": (460, 369, 524, 393), "label_q2_cost": (536, 405, 600, 429),
    "label_q3_rev": (696, 343, 760, 367), "label_q3_cost": (772, 412, 836, 436),
    "label_q4_rev": (932, 295, 996, 319), "label_q4_cost": (1008, 375, 1072, 399),
}
REGIONS.update(BAR_TOPS)


def ink_bbox(x0, y0, x1, y1, thresh=600):
    xs, ys = [], []
    for y in range(y0, y1):
        for x in range(x0, x1):
            if sum(px[x, y]) < thresh:
                xs.append(x); ys.append(y)
    if not xs:
        return None
    return {"x0": min(xs), "y0": min(ys), "x1": max(xs), "y1": max(ys),
            "w": max(xs) - min(xs) + 1, "h": max(ys) - min(ys) + 1}


out = {k: ink_bbox(*r) for k, r in REGIONS.items()}
with open(os.path.join(TMP, "flawed-region-bboxes.json"), "w", encoding="utf-8") as f:
    json.dump({"source": SRC, "regions": out}, f, ensure_ascii=False, indent=1)
for k, v in out.items():
    print(k, v)