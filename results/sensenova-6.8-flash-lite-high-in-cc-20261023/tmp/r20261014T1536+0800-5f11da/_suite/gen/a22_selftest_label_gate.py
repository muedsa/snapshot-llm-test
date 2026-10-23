"""像素审计第 6 项（标签是否压在柱上）的活性自检。

这一项在 round-02 上反复改过三次，前两次都不是改图而是改检查器：

  1. 索引漏减 PLOT["left"]，把子图里别处的柱体算进标签矩形；
  2. 坐标基准写错（any_bar 是子图、block 是子图里再切一层，下标却按子图换算，
     导致外扩后的列下标 614 > 块宽 104，切片为空，"挖掉标签墨迹"成了空操作）；
  3. 换成按柱体列窗口的实心行段判定。

之所以要单独写自检：前两次「修好」后检查器都是在空转——第 2 次里 `cnt` 从 366
变成 366 一模一样，只是没人想到去核对。没有自检验证「该报的时候真的会报」，
"全部通过"就只是自证。

判定语义（与 a22_build.audit 第 6 项完全一致）：取标签矩形与柱体矩形的交集，
在柱体自身的列窗口里，一行被柱族像素填满的比例 ≥ FILL_MIN 算「实心行」，
连续 ≥ ROWS_MIN 行即判为标签压在柱体上。柱体是实心块（填满约 0.93），
文字笔画只有 1–3 px 宽（同一窗口里远低于 0.75），所以同色也不误报。

用法
    python -I -X utf8 a22_selftest_label_gate.py
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))

import a22_build as M  # noqa: E402

# 与 styles() 一致的三个颜色
NEG_GRAD_TOP = np.array([0xE0, 0x61, 0x1F])
NEG_GRAD_BOT = np.array([0x9E, 0x33, 0x06])
NEG_COLOR = np.array([0xC2, 0x41, 0x0C])   # 负值标签颜色，和负柱同族
PANEL = np.array([0xFF, 0xFF, 0xFF])

FILL_MIN = 0.75
ROWS_MIN = 4

W, H = 400, 700                      # 整幅当子图：PLOT["left"]=0
BAR = {"x": 300, "y": 500, "width": 30, "y_top": 500, "height_px": 40}
# 五块互不重叠的标签矩形（104 x 24，和真实 BAR_LABEL_W/H 一致）
BOX_CLEAN = {"label_x": 100, "label_y": 560}          # 远离柱体
BOX_OVER = {"label_x": 268, "label_y": 496}           # 压住柱体 21 行
BOX_SAME = {"label_x": 268, "label_y": 526}           # 压住柱体，且文字同色
BOX_TINY = {"label_x": 268, "label_y": 537}           # 只压住柱体 3 行
BOX_BELOW = {"label_x": 268, "label_y": 542}          # 柱体在其上方，不重叠


def stamp(arr, x0, y0):
    """画一串数字的墨迹（含抗锯齿边缘），字形总宽 88 px，落在 y0+4..y0+20。"""
    for dx, w in ((0, 12), (20, 10), (38, 12), (58, 10)):
        x = x0 + dx
        y = y0 + 4
        arr[y - 1:y + 17, x - 1:x + w + 2] = (
            0.78 * NEG_COLOR + 0.22 * PANEL).astype(np.uint8)
        arr[y:y + 16, x:x + w] = NEG_COLOR


def paint_text(x0: int, y0: int) -> np.ndarray:
    """白底 + 一根渐变负柱 +（可选）一串墨迹。"""
    arr = np.tile(PANEL, (H, W, 1)).astype(np.uint8)
    for i in range(BAR["height_px"]):
        t = i / (BAR["height_px"] - 1)
        arr[BAR["y_top"] + i, BAR["x"]:BAR["x"] + BAR["width"]] = (
            NEG_GRAD_TOP * (1 - t) + NEG_GRAD_BOT * t).astype(np.uint8)
    stamp(arr, x0, y0)
    return arr


def white() -> np.ndarray:
    return np.tile(PANEL, (H, W, 1)).astype(np.uint8)


def solid_run(arr, box) -> tuple[int, float]:
    """复刻审计第 6 项：返回标签矩形内该柱体的最长实心行段与最大填充比例。"""
    sub0 = arr[0:H, 0:W].astype(int)
    a = sub0[..., 0]; b = sub0[..., 1]; c = sub0[..., 2]
    any_bar = (M.FAMILY_TEST["net"](a, b, c) |
               M.FAMILY_TEST["profit"](a, b, c) |
               M.FAMILY_TEST["neg"](a, b, c))
    ay0 = box["label_y"]
    ay1 = ay0 + 24
    c0 = max(box["label_x"], BAR["x"])
    c1 = min(box["label_x"] + 104, BAR["x"] + BAR["width"])
    if c1 - c0 < 3:
        return 0, 0.0
    r0 = max(ay0, BAR["y_top"])
    r1 = min(ay1, BAR["y_top"] + BAR["height_px"])
    if r1 - r0 < 1:
        return 0, 0.0
    band = any_bar[r0:r1, c0:c1]
    solid = np.fromiter(
        (float(band[i].mean()) >= FILL_MIN for i in range(band.shape[0])),
        dtype=bool)
    frac = max((float(band[i].mean()) for i in range(band.shape[0])),
               default=0.0)
    return M.best_run(solid), frac


def main() -> int:
    cases = [
        # (说明, 图, 矩形, 是否应该报警)
        ("A 文字墨迹在纯背景上，柱体不在矩形内      -> 不报",
         paint_text(BOX_CLEAN["label_x"], BOX_CLEAN["label_y"]), BOX_CLEAN, False),
        ("B 标签矩形压住柱体 21 行                  -> 必须报",
         paint_text(100, 640), BOX_OVER, True),
        ("C 标签矩形只压住柱体 3 行                  -> 不报（低于最短实心行段）",
         paint_text(100, 640), BOX_TINY, False),
        ("D 标签压住柱体、且文字与柱体同色          -> 仍必须报（同色不掩盖）",
         paint_text(BOX_SAME["label_x"], BOX_SAME["label_y"]), BOX_SAME, True),
        ("E 标签覆盖柱体全宽、柱体比矩形高          -> 必须报",
         paint_text(100, 640), {"label_x": BAR["x"] - 60, "label_y": 480}, True),
        ("F 柱体在标签矩形上方、墨迹与柱体同列      -> 不报",
         paint_text(BOX_BELOW["label_x"], BOX_BELOW["label_y"]), BOX_BELOW, False),
        ("G 空标签矩形（无墨迹、无柱）              -> 不报",
         white(), BOX_CLEAN, False),
    ]
    ok = True
    for name, img, box, expect in cases:
        run, frac = solid_run(img, box)
        got = run >= ROWS_MIN
        passed = got == expect
        ok = ok and passed
        print("%s  %s" % ("OK   " if passed else "FAIL ", name))
        print("         solid_run=%d  max_fill=%.2f  判定=%s  期望=%s"
              % (run, frac, got, expect))
    print()
    print("活性自检：%s" % ("通过" if ok else "失败"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
