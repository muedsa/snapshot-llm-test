"""case-05 字形墨迹实测：从当前 final.png 量每个格值数字的实际墨迹边界。

目的：当前的数字框用 K.pitch(16)=19.2 px 作高，比真实字形墨迹高一截，
导致 65 dB 环线在小声源处被过度打断。这一脚本直接量像素，给出真实墨迹框，
让 ring_segments 按实测边界求段，而不是按行高估算。

不产生服务请求、不改写产物。用法：python -I -X utf8 b01_case05_glyph_probe.py
"""
from __future__ import annotations

import pathlib
import sys

from PIL import Image

HERE = pathlib.Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
import b01_kit as K  # noqa: E402
import b01_case05 as C  # noqa: E402

ROOT = HERE.parents[4]
RUN_ID = HERE.parents[2].name
FINAL = ROOT / "outputs" / RUN_ID / "B01" / "case-05" / "final.png"
FS = 16.0
MORN = {"site", "logi", "scho", "metro"}
NITE = {"metro", "stall", "dine"}
PANELS = [("08:00", C.GX_L, MORN), ("22:00", C.GX_R, NITE)]


def hx(p: tuple) -> str:
    return "#%02x%02x%02x" % p


def cell_fill(lv: dict, c: int, r: int) -> str:
    return C.CL[C.cls_of(lv[(c, r)])]


def ink_bbox(px, W, H, x0, x1, y0, y1, bg):
    """框内与 bg 颜色差异 > 阈值 的像素范围。返回 (ix0, ix1, iy0, iy1) 或 None。"""
    bgr = (int(bg[1:3], 16), int(bg[3:5], 16), int(bg[5:7], 16))
    ix0 = ix1 = iy0 = iy1 = None
    for y in range(int(y0), int(y1) + 1):
        if not (0 <= y < H):
            continue
        for x in range(int(x0), int(x1) + 1):
            if not (0 <= x < W):
                continue
            p = px[x, y]
            # 只认与底色差异明显的像素；抗锯齿的过渡像素也算墨迹
            if max(abs(p[0] - bgr[0]), abs(p[1] - bgr[1]), abs(p[2] - bgr[2])) <= 24:
                continue
            if ix0 is None or x < ix0:
                ix0 = x
            if ix1 is None or x > ix1:
                ix1 = x
            if iy0 is None or y < iy0:
                iy0 = y
            if iy1 is None or y > iy1:
                iy1 = y
    if ix0 is None:
        return None
    return (ix0, ix1, iy0, iy1)


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    im = Image.open(FINAL).convert("RGB")
    W, H = im.width, im.height
    px = im.load()

    heights, widths, dxs, dys = [], [], [], []
    n_missing = 0
    shown = 0
    for title, gx, act in PANELS:
        lv = C.field_level(C.CELLS, act)
        for (c, r) in C.CELLS:
            s = "%d" % C.dbr(lv[(c, r)])
            bg = cell_fill(lv, c, r)
            cx = gx + (c + 0.5) * C.CELL
            w = K.tw(s, FS)
            y = C.GY + (r + 0.5) * C.CELL - K.pitch(FS) / 2
            # 搜索窗只外扩 1 px：环线衬底在框外 ≥2.5 px，再扩会把近白衬底
            # 当成 CL3 白字墨迹（两者颜色都偏白，24 的色差阈值分不开）
            box = ink_bbox(px, W, H, cx - w / 2 - 1, cx + w / 2 + 1,
                           y - 1, y + K.pitch(FS) + 1, bg)
            if box is None:
                n_missing += 1
                continue
            bw = box[1] - box[0] + 1
            bh = box[3] - box[2] + 1
            widths.append(bw)
            heights.append(bh)
            dxs.append((box[0] + box[1] + 1) / 2 - cx)
            dys.append((box[2] + box[3] + 1) / 2 - (y + K.pitch(FS) / 2))
            if shown < 6:
                print("  例 %s 格(%d,%d) %s 墨迹 x[%d,%d] y[%d,%d]  "
                      "框 x[%.1f,%.1f] y[%.1f,%.1f]  墨心偏移 (%+.1f,%+.1f)"
                      % (title, c, r, s, box[0], box[1], box[2], box[3],
                         cx - w / 2, cx + w / 2, y, y + K.pitch(FS),
                         (box[0] + box[1] + 1) / 2 - cx,
                         (box[2] + box[3] + 1) / 2 - (y + K.pitch(FS) / 2)))
                shown += 1

    widths.sort()
    heights.sort()
    dxs.sort()
    dys.sort()
    print("测量到的格值字形：%d 个（缺 %d）" % (len(widths), n_missing))
    print("宽度分布  min %d  中位 %d  max %d" % (
        widths[0], widths[len(widths) // 2], widths[-1]))
    print("高度分布  min %d  中位 %d  max %d" % (
        heights[0], heights[len(heights) // 2], heights[-1]))
    print("墨心 x 偏移  min %+.1f  中位 %+.1f  max %+.1f"
          % (dxs[0], dxs[len(dxs) // 2], dxs[-1]))
    print("墨心 y 偏移  min %+.1f  中位 %+.1f  max %+.1f"
          % (dys[0], dys[len(dys) // 2], dys[-1]))
    print("K.pitch(16) = %.1f px（当前数字框用的高）" % K.pitch(FS))
    print("→ 墨迹高 %d px，比框高小 %.1f px，环线断口可按墨迹框收紧"
          % (heights[-1], K.pitch(FS) - heights[-1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
