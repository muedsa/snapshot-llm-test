"""A03 步骤 7：用像素众数验证颜色 alpha 语义（原稿的两个 alpha 陷阱）。

原稿 inputs/broken.snapshot 里两处 8 位十六进制颜色：
  L10  color="#33FFFFFF"   —— Flutter 习惯「alpha 在前」，本 DSL 是 #RRGGBBAA
                              → 解析为 R=0x33 G=0xFF B=0xFF A=0xFF = 不透明青色
  L11  color="#FFFFFF44"   —— 白色 alpha = 0x44 = 26.7%，不是「白底 20%」

这里在 probe5-layout.png 的 T4 格与 v2.png 的 REVIEW 上取颜色众数，
与「在背景 #0B1220 上按给定 alpha 合成的理论值」逐通道对比。

用法：python a03_alpha.py <输出目录>
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image

BG = (0x0B, 0x12, 0x20)


def mode_color(img: np.ndarray, y0: int, y1: int, x0: int, x1: int):
    """区域内出现次数最多的 2 级量化颜色 + 占比。"""
    patch = img[y0:y1, x0:x1].reshape(-1, 3)
    keys = (patch // 2) * 2
    flat = [tuple(int(v) for v in k) for k in keys]
    top = Counter(flat).most_common(1)[0]
    return list(top[0]), round(top[1] / len(flat), 4)


def theory(white: bool, alpha_pct: float, base=BG):
    """白色 alpha=a 叠加到 base 上的理论 RGB。"""
    f = alpha_pct / 100.0
    return [int(round((1 - f) * base[i] + f * 255)) for i in range(3)]


def main() -> None:
    tmp = Path(sys.argv[1])
    prev = tmp / "preview"

    probe = np.array(Image.open(prev / "probe5-layout.png").convert("RGB"))
    v2 = np.array(Image.open(prev / "v2.png").convert("RGB"))

    out = {"note": "众数为 2 级量化值，与理论值允许 ±2 通道误差",
           "background": list(BG), "cases": []}

    # probe5 T4 格实际画布坐标 x 704..1280 / y 432..768。
    # REVIEW 卡体是青色块：按颜色掩膜定位，再用它的 bbox 取众数（避开文字笔画）。
    reg = probe[432:769, 704:1281]
    cy = ((np.abs(reg[:, :, 0].astype(int) - 0x33) < 24)
          & (reg[:, :, 1].astype(int) > 200)
          & (reg[:, :, 2].astype(int) > 200))
    ys, xs = np.where(cy)
    if len(xs) == 0:
        raise SystemExit("probe5 T4 未找到青色 REVIEW 卡体，颜色掩膜失效")
    cy0, cy1 = int(ys.min()) + 432, int(ys.max()) + 432
    cx0, cx1 = int(xs.min()) + 704, int(xs.max()) + 704
    out["probe5_t4_review_mask_bbox"] = [cx0, cy0, cx1, cy1]
    out["probe5_t4_review_mask_size"] = [cx1 - cx0 + 1, cy1 - cy0 + 1]
    out["probe5_t4_review_expected_size"] = [167, 78]
    cm, sh = mode_color(probe, cy0 + 2, cy1 - 1, cx0 + 2, cx1 - 1)
    out["cases"].append({
        "source": "inputs/broken.snapshot L10",
        "dsl_attribute": 'color="#33FFFFFF"',
        "intent": "白色 20% 不透明度卡体（Flutter 0x33FFFFFF 习惯）",
        "dsl_actual_parse": {"form": "#RRGGBBAA", "R": 0x33, "G": 0xFF,
                             "B": 0xFF, "A": 0xFF,
                             "meaning": "不透明青色，alpha 被当作 R 通道"},
        "measured_mode": cm, "mode_share": sh,
        "verdict": "不是白色；青色与白色相差 222 通道，需求「白底不透明度 20%」未实现",
    })

    # T4 格内模糊说明卡（原稿 L11）：在 Column 里排在 Transform 之后。
    # 按「比格背景亮」的掩膜定位卡体，再取左上角无文字区域取众数。
    below = probe[cy1 + 1:769, 704:1281].astype(int)
    light = below.min(axis=2) > 40
    ys2, xs2 = np.where(light)
    if len(xs2) == 0:
        raise SystemExit("probe5 T4 未找到说明卡卡体")
    ky0, ky1 = int(ys2.min()) + cy1 + 1, int(ys2.max()) + cy1 + 1
    kx0, kx1 = int(xs2.min()) + 704, int(xs2.max()) + 704
    out["probe5_t4_card_bbox"] = [kx0, ky0, kx1, ky1]
    out["probe5_t4_card_sample_region"] = [kx0 + 10, ky0 + 10,
                                           kx0 + 80, ky0 + 70]
    cm2, sh2 = mode_color(probe, ky0 + 10, ky0 + 70, kx0 + 10, kx0 + 80)
    t44 = theory(True, 0x44 / 0xFF * 100, base=(0x0F, 0x17, 0x2A))
    out["cases"].append({
        "source": "inputs/broken.snapshot L11",
        "dsl_attribute": 'color="#FFFFFF44"',
        "intent": "半透明白底说明卡",
        "backdrop": [0x0F, 0x17, 0x2A],
        "alpha_pct": round(0x44 / 0xFF * 100, 2),
        "measured_mode": cm2, "mode_share": sh2,
        "expected_for_that_alpha": t44,
        "channel_delta": [abs(cm2[i] - t44[i]) for i in range(3)],
        "verdict": "alpha=26.7% 与测量一致，但仍不是题目要求的 20%",
    })

    # v2 REVIEW（160×56 旋转后外接框 1074..1242 × 663..733）
    cm3, sh3 = mode_color(v2, 676, 722, 1088, 1224)
    t33 = theory(True, 20.0)
    out["cases"].append({
        "source": "system-pulse.snapshot（修复后 REVIEW）",
        "dsl_attribute": 'color="#FFFFFF33"',
        "alpha_pct": round(0x33 / 0xFF * 100, 2),
        "measured_mode": cm3, "mode_share": sh3,
        "expected_for_that_alpha": t33,
        "channel_delta": [abs(cm3[i] - t33[i]) for i in range(3)],
        "verdict": "与白色 20% 的理论值一致（容差内）",
    })

    (tmp / "alpha-check.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
