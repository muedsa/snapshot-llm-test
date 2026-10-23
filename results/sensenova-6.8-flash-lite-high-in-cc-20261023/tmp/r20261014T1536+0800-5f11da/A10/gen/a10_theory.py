"""A10 ①② 的重叠内部理论颜色推导。

顺序按题面：蓝覆盖红、最后合成到白底，source-over，sRGB 0–255 通道值，
中间值不取整，最终 RGB = floor(value + 0.5)。

① 每个矩形自带 50% alpha，编码 128/255（8 位 #80）。
② 组内矩形不透明，先在同一子树里合成，再对整个不透明结果施加组透明度 0.5。

两者的差别不在「50%」这个数值上，而在 alpha 施加的对象：
① 把 128/255 分别施加给每个矩形，所以红色矩形先漏出的红色被蓝色矩形部分覆盖，
   重叠区的 G 通道会透出红色矩形留下的中间灰；
② 先在组内得到纯蓝，再对纯蓝整体乘以 0.5，重叠区保持纯蓝色相、只是变浅。
"""

from __future__ import annotations

WHITE = (255.0, 255.0, 255.0)
RED = (255.0, 0.0, 0.0)
BLUE = (0.0, 0.0, 255.0)
A_HEX80 = 128.0 / 255.0      # ① 8 位 #80 的精确 alpha
A_GROUP = 0.5                # ② 组 Opacity


def over(src: tuple, a: float, dst: tuple) -> tuple:
    """premultiplied-free 的 source-over：out = a*src + (1-a)*dst（dst 视为不透明）。"""
    return tuple(a * s + (1.0 - a) * d for s, d in zip(src, dst))


def round_nearest(vals: tuple) -> list[int]:
    """floor(value + 0.5)，题面指定的最近整数取整。"""
    import math
    return [int(math.floor(v + 0.5)) for v in vals]


def case_alpha_each() -> dict:
    """① 两个矩形各自 alpha = 128/255，逐个合成到白底。"""
    dst = WHITE
    steps = []
    prev = WHITE
    dst = over(RED, A_HEX80, dst)
    steps.append({"layer": "红矩形 #FF000080", "alpha": A_HEX80,
                  "alpha_source": "8 位十六进制 #80 = 128/255",
                  "dst_before": prev, "dst_after": dst})
    prev = dst
    dst = over(BLUE, A_HEX80, dst)
    steps.append({"layer": "蓝矩形 #0000FF80（上层）", "alpha": A_HEX80,
                  "alpha_source": "8 位十六进制 #80 = 128/255",
                  "dst_before": prev, "dst_after": dst})
    return {"case": "①", "alpha_per_rect": A_HEX80, "steps": steps,
            "theoretical_float_rgb": list(dst),
            "rounded_rgb": round_nearest(dst)}


def case_group_opacity() -> dict:
    """② 红蓝不透明先在组内合成，再对整体施加 Opacity 0.5。"""
    inner = WHITE
    steps = []
    inner = over(RED, 1.0, inner)
    steps.append({"layer": "红矩形 #FF0000（组内，不透明）", "alpha": 1.0,
                  "alpha_source": "组内矩形不透明；组透明度还未施加",
                  "dst_before": WHITE, "dst_after": inner})
    inner = over(BLUE, 1.0, inner)
    steps.append({"layer": "蓝矩形 #0000FF（组内上层，不透明）", "alpha": 1.0,
                  "alpha_source": "组内矩形不透明；组透明度还未施加",
                  "dst_before": (255.0, 0.0, 0.0), "dst_after": inner})
    flat = over(inner, A_GROUP, WHITE)
    steps.append({"layer": "Opacity 0.5 作用于整组（纯蓝）的结果", "alpha": A_GROUP,
                  "alpha_source": "组透明度 0.5（浮点），不是 128/255",
                  "dst_before": WHITE, "dst_after": flat})
    return {"case": "②", "group_opacity": A_GROUP, "inner_flat_rgb": list(inner),
            "steps": steps, "theoretical_float_rgb": list(flat),
            "rounded_rgb": round_nearest(flat)}


def report() -> dict:
    a = case_alpha_each()
    b = case_group_opacity()
    return {
        "compositing_order": "蓝覆盖红，最后合成到白底（source-over）",
        "rounding": "中间值不取整；最终 RGB = floor(value + 0.5)",
        "space": "sRGB，通道 0–255",
        "alpha_explained": {
            "①": "8 位十六进制 #80 编码的 alpha = 128/255 = %.6f，施加在两个矩形各自身上"
                 % A_HEX80,
            "②": "组透明度 0.5 是浮点 alpha，施加在整组压平后的结果上；"
                 "组内矩形不透明，先互相合成成纯蓝",
            "差别": "同一处像素：① 红先漏出再被蓝部分覆盖，G 通道含红色残影；"
                    "② 先合成纯蓝再整体变淡，色相保持纯蓝。"
                    "因此 0.5 与 128/255 不能混为同一个 alpha，作用对象不同",
        },
        "①": a, "②": b,
    }


def main() -> int:
    import json
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    r = report()
    print(json.dumps(r, ensure_ascii=False, indent=2))
    # 与板上写死的 PRED 常量互校（不在此处 import a10_board，避免拉起服务客户端）
    print("① 取整 RGB =", r["①"]["rounded_rgb"], " ② 取整 RGB =", r["②"]["rounded_rgb"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
