"""case-05 环线 × 数字 定量审计。

四个可复算的问题，不产生服务请求、不改写产物：

1. 65 dB 环线的几何是否碰到格值数字框（环会不会切到数字）。
2. 环线两层各自对底/文字色的对比度——环线要贴在数字旁边，就必须和
   数字颜色也分得开，而不只是和格子底色分得开。
3. final.png 里数字框内是否还残留「芯色」像素，以及超标格（CL3）上
   是否出现「衬底色」像素（原环线色在 CL3 上对比只有 1.22:1，等于看不见）。
4. 渲染后数字框到最近环线像素的真实净空（带符号，负值 = 落进框内），
   以及贴住字形的那一圈背景对比。

像素分类按精确通道匹配，不用对比度阈值：
CL2 格上约 30% 墨色 + 70% 底色的抗锯齿边缘合成色 #5B3E19 与芯色 #5C3D18
只差 1 个通道，用对比度阈值（哪怕只到 1.15）会把数字自己的边缘误判成环线芯。
fill(pixel=True) 的实心填充一定是精确的通道值，所以芯色按 TOL_CORE=0 判定；
衬底/CL3 描边/CL0 格底三者本身颜色接近，只能按浅色归并统计。
3 与 4 节只按颜色本身判定，不依赖脚本的坐标公式。
"""
from __future__ import annotations

import math
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

FS = 16.0                      # 格值字号，与 draw_panel 一致
MORN = {"site", "logi", "scho", "metro"}
NITE = {"metro", "stall", "dine"}
PANELS = [("08:00 · 早高峰", C.GX_L, MORN), ("22:00 · 深夜", C.GX_R, NITE)]
FIELD = {t: C.field_level(C.CELLS, act) for t, _g, act in PANELS}
RING_N = 1440                  # 每条环线的角度采样点数
RADIOI = 5                     # 每个角度上的径向采样数（覆盖衬底两圈 + 芯）

TOL_CORE = 0                   # 芯色通道容差：实心填充必须是精确通道值
TOL_LIGHT = 6                  # 浅色通道容差（衬底 / CL3 描边 / CL0 底都算浅色）


def hx(p: tuple) -> str:
    return "#%02x%02x%02x" % p


def rgb(h: str) -> tuple:
    return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))


CONT_RGB = rgb(C.CONT)
FRAME_RGB = rgb(C.FRAME)


def is_core(p: tuple) -> bool:
    """是否落在环线芯色上（实心填充，精确匹配）。"""
    return all(abs(a - b) <= TOL_CORE for a, b in zip(p, CONT_RGB))


def is_light(p: tuple) -> bool:
    """是否为浅色像素（衬底、CL3 描边、CL0 格底三者颜色接近，无法只用
    颜色区分；判定缺陷只看 is_core，这一项作衬底是否生效的分布参考）。"""
    return all(abs(a - b) <= TOL_LIGHT for a, b in zip(p, FRAME_RGB))


def digit_boxes(title: str, gx: float) -> list[dict]:
    """96 个格值数字的框，与 b01_case05.digit_boxes 的墨迹框公式一致。"""
    lv = FIELD[title]
    out = []
    for (c, r) in C.CELLS:
        s = "%d" % C.dbr(lv[(c, r)])
        cx = gx + (c + 0.5) * C.CELL
        cy = C.GY + (r + 0.5) * C.CELL + C.INK_DY
        out.append({"c": c, "r": r, "s": s,
                    "x0": cx - C.INK_W / 2, "x1": cx + C.INK_W / 2,
                    "y0": cy - C.INK_H / 2, "y1": cy + C.INK_H / 2,
                    "cls": C.cls_of(lv[(c, r)])})
    return out


def hit(b: dict, x: float, y: float, pad: float = 0.0) -> bool:
    return b["x0"] - pad <= x <= b["x1"] + pad and b["y0"] - pad <= y <= b["y1"] + pad


def ring_points(gx: float, gy: float, l0: float, n: int = RING_N):
    """环带上的 n 个等角采样点，每个角度在径向取 5 个半径。

    只沿中心线采样会漏判：中心线落在芯带上（衬底之外），
    所以衬底是否可见必须采样衬底自己那两圈。
    返回 [(x, y, radius), ...]，每角度 RING_R_N 个点。
    """
    R = C.reach65(l0) * C.S
    rs = (R - C.HALO_IN + 0.25, R - 3.0, R - 1.25, R + 0.25,
          R + C.HALO_OUT - 0.25)
    out = []
    for i in range(n):
        th = 2.0 * math.pi * i / n
        ct, st = math.cos(th), math.sin(th)
        for rr in rs:
            out.append((gx + rr * ct, gy + rr * st, rr))
    return out


RADIOI = 5                     # 每个角度上的径向采样数


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")

    print("=== 1. 环带采样点 vs 数字框（几何）===")
    total = inside = 0
    for title, gx, act in PANELS:
        boxes = digit_boxes(title, gx)
        srcs = [s for s in C.SRC if s[0] in act]
        n_in = 0
        for sid, nm, g, (i, j), l0, a in srcs:
            pts = ring_points(gx + i * C.CELL, C.GY + j * C.CELL, l0)
            n_in += sum(1 for x, y, _r in pts
                        if any(hit(b, x, y) for b in boxes))
        tot = RING_N * RADIOI * len(srcs)
        total += tot
        inside += n_in
        print("  %s：环带采样 %d 点，落进数字框 %d 点（%.1f%%）"
              % (title, tot, n_in, 100.0 * n_in / tot))

    print("=== 2. 环线两层各自对底/文字色的对比度（芯 %s / 衬底 %s）==="
          % (C.CONT, C.FRAME))
    for i in range(4):
        print("  CL%d 底 %-8s 文字 %-8s → 芯vs文字 %5.2f  衬底vs文字 %5.2f  |  "
              "芯vs底 %5.2f  衬底vs底 %5.2f"
              % (i, C.CL[i], C.CLINK[i],
                 K.contrast(C.CONT, C.CLINK[i]),
                 K.contrast(C.FRAME, C.CLINK[i]),
                 K.contrast(C.CONT, C.CL[i]),
                 K.contrast(C.FRAME, C.CL[i])))
    print("  → 单一颜色无法满足「对 CL3 底 ≥3.0 且对白字 ≥3.0」（需要亮度")
    print("    既 ≥0.343 又 ≤0.300），所以必须两层 + 在数字处断开")

    im = Image.open(FINAL).convert("RGB")
    px = im.load()
    W, H = im.width, im.height
    print("=== 3. final.png 环线像素审计（%s %s×%s）==="
          % (FINAL.name, W, H))
    n_cross = n_core = 0
    n_cl3 = n_cl3_light = 0
    for title, gx, act in PANELS:
        boxes = digit_boxes(title, gx)
        lv = FIELD[title]
        for sid, nm, g, (i, j), l0, a in [s for s in C.SRC if s[0] in act]:
            pts = ring_points(gx + i * C.CELL, C.GY + j * C.CELL, l0)
            nc = ncore = n3 = n3l = 0
            for k in range(len(pts) // RADIOI):
                grp = pts[k * RADIOI:(k + 1) * RADIOI]
                in_box = False
                light = False
                over_cl3 = False
                for x, y, _r in grp:
                    X, Y = int(round(x)), int(round(y))
                    if not (0 <= X < W and 0 <= Y < H):
                        continue
                    p = px[X, Y]
                    light = light or is_light(p)
                    cc = int((x - gx) / C.CELL)
                    cr = int((y - C.GY) / C.CELL)
                    if 0 <= cc < C.COLS and 0 <= cr < C.ROWS:
                        over_cl3 = over_cl3 or C.cls_of(lv[(cc, cr)]) == 3
                    if any(hit(b, x, y) for b in boxes):
                        in_box = True
                        if is_core(p):
                            ncore += 1       # 缺陷：芯应该在这里断开
                if in_box:
                    nc += 1
                if over_cl3:
                    n3 += 1
                    if light:
                        n3l += 1
            n_cross += nc
            n_core += ncore
            n_cl3 += n3
            n_cl3_light += n3l
            print("  %s %s（L0=%g dB, R=%.1f px）：环带压到数字框 %d 角度 → "
                  "芯色 %d 点；超标格上 %d 角度 → 衬底可见 %d 角度"
                  % (title, nm, l0, C.reach65(l0) * C.S, nc, ncore, n3, n3l))

    # 数字可读性：只测贴住字形的那一圈（框外 1-2 px），这是笔画边缘的真实对比。
    # 环线到框的真实净空另在 4b 里量，两者合起来才看得出「是否糊」。
    print("=== 4a. 192 个格值：框外 1-2 px 背景与文字色的最低对比 ===")
    worst_leg = float("inf")
    worst_leg_box = None
    for title, gx, act in PANELS:
        for b in digit_boxes(title, gx):
            tc = C.CLINK[b["cls"]]
            x0, x1 = int(round(b["x0"])), int(round(b["x1"]))
            y0, y1 = int(round(b["y0"])), int(round(b["y1"]))
            cs = []
            for yy in (y0 - 2, y0 - 1, y1 + 1, y1 + 2):
                if 0 <= yy < H:
                    for xx in range(x0, x1 + 1):
                        cs.append(K.contrast(hx(px[xx, yy]), tc))
            for xx in (x0 - 2, x0 - 1, x1 + 1, x1 + 2):
                if 0 <= xx < W:
                    for yy in range(y0, y1 + 1):
                        cs.append(K.contrast(hx(px[xx, yy]), tc))
            if cs and min(cs) < worst_leg:
                worst_leg, worst_leg_box = min(cs), (title, b["s"], b["cls"])

    print("  最差的是 %s 格 %s（CL%d）：框外 1-2 px 背景对比 %.2f : 1"
          % (worst_leg_box[0], worst_leg_box[1], worst_leg_box[2], worst_leg))

    # 4b：渲染后每个数字框到最近「芯色」像素的真实净空（不依赖坐标公式）。
    # 距离取带符号：负值表示芯色像素落在数字框里面，那才是真正的缺陷。
    print("=== 4b. 渲染后数字框到最近芯色像素的净空（负 = 落进框内）===")
    core_pts = [(x, y) for y in range(H) for x in range(W)
                if is_core(px[x, y])]
    worst_clear = float("inf")
    worst_clear_box = None
    for title, gx, act in PANELS:
        for b in digit_boxes(title, gx):
            x0, x1 = b["x0"], b["x1"]
            y0, y1 = b["y0"], b["y1"]
            best = float("inf")
            for (x, y) in core_pts:
                if not (x0 - 9 <= x <= x1 + 9 and y0 - 9 <= y <= y1 + 9):
                    continue
                if x0 <= x <= x1 and y0 <= y <= y1:
                    d = -min(x - x0, x1 - x, y - y0, y1 - y)   # 深入框内
                else:
                    d = math.hypot(max(x0 - x, 0.0, x - x1),
                                   max(y0 - y, 0.0, y - y1))
                best = min(best, d)
            if best < worst_clear:
                worst_clear, worst_clear_box = best, (title, b["s"], b["cls"])

    print("  最差的是 %s 格 %s（CL%d）：到最近芯色像素 %+.2f px"
          % (worst_clear_box[0], worst_clear_box[1], worst_clear_box[2],
             worst_clear))

    print("\n汇总：环带采样 %d 点，压到数字框 %d 角度（%.1f%%）→ 芯色 %d 点"
          % (total, n_cross, 100.0 * n_cross / total, n_core))
    print("       超标格（CL3）上 %d 角度 → 衬底可见 %d 角度（%.1f%%）"
          % (n_cl3, n_cl3_light,
             100.0 * n_cl3_light / n_cl3 if n_cl3 else 0.0))
    print("       框外 1-2 px 背景与文字色的最低对比 %.2f : 1" % worst_leg)
    print("       数字框到最近芯色像素的渲染净空 %+.2f px" % worst_clear)
    ok = n_core == 0 and n_cl3_light > 0 and worst_leg >= 3.0 \
        and worst_clear >= 1.5
    print("判定：%s" % ("通过：芯不进入数字框（框内芯色 0 点）、超标格上衬底可见、"
                       "贴住字形的背景对比 ≥ 3.0、渲染净空 ≥ 1.5 px"
                       if ok else "未通过：缺陷未修完"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
