"""Measure per-character-class advances from probe-metrics2.png."""
from __future__ import annotations

import json
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SIZE = 26.0
CLASS = {"upper": "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "lower": "abcdefghijklmnopqrstuvwxyz",
         "digit": "0123456789", "punct_dot": ".", "punct_slash": "/", "punct_comma": ",",
         "han": None}


def main() -> None:
    plan = json.load(open(os.path.join(HERE, "probe-metrics2.plan.json"), encoding="utf-8"))
    img = np.asarray(Image.open(os.path.join(HERE, "probe-metrics2.png")).convert("RGB"))
    ink = img.astype(int).sum(axis=2) < 700
    ext = {}
    for item in plan:
        y0, y1 = int(item["y"]), int(item["y"]) + 34
        band = ink[y0:y1, :]
        cols = np.nonzero(band.any(axis=0))[0]
        ext[item["key"]] = (int(cols.min()), int(cols.max()))
    out = {}
    for name, _ in [("upper", 0), ("lower", 0), ("digit", 0), ("digit5", 0),
                    ("punct_dot", 0), ("punct_slash", 0), ("punct_comma", 0), ("han", 0)]:
        w4 = ext[f"{name}_4"][1] - ext[f"{name}_4"][0]
        w12 = ext[f"{name}_12"][1] - ext[f"{name}_12"][0]
        adv = (w12 - w4) / 8.0
        out[name] = {"advance_px": round(adv, 4), "advance_em": round(adv / SIZE, 5)}
        print(f"{name:12s} advance {adv:7.4f}px = {adv/SIZE:.4f} em")
    # space advance from "A A" vs "AA"(two As)
    aa = ext["upper_4"][1] - ext["upper_4"][0]      # 4 As
    adv_a = out["upper"]["advance_px"]
    ink_a = aa - 3 * adv_a
    two = ext["space_test_2"][1] - ext["space_test_2"][0]
    four = ext["space_test_4"][1] - ext["space_test_4"][0]
    space_adv = (four - two) / 3.0
    out["space"] = {"advance_px": round(space_adv, 4), "advance_em": round(space_adv / SIZE, 5)}
    print(f"{'space':12s} advance {space_adv:7.4f}px = {space_adv/SIZE:.4f} em")
    for key in ("words", "Upper_words"):
        w = ext[key][1] - ext[key][0]
        out[key] = {"ink_width_px": w}
        print(f"{key:12s} ink width {w}px  text={key}")
    out["_raw_extents"] = {k: list(v) for k, v in ext.items()}
    with open(os.path.join(HERE, "font-metrics-cjk.json"), "w", encoding="utf-8") as fh:
        json.dump({"probe": "probe-metrics2.png", "size": SIZE, "measured": out}, fh,
                  ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
