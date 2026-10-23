"""诊断留痕：打印像素审计被判为 unexplained 的取样点及其几何覆盖链。

像素审计第一次跑有 3 帧各 1 个点未解释（帧1/4/5）。这个脚本定位出根因：取样点用
浮点坐标做几何判定、却用取整后的整数坐标读像素，0.7 px 的取整误差让点落到形状
边界的另一侧。审计改为两者同用像素中心整数坐标 + 边界 1 px 抗锯齿带后全部通过。
保留此脚本作为那次定位的证据，不进交付。
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(HERE.parent))

import a23_units as U  # noqa: E402

OUT = ROOT / "outputs" / "r20261014T1536+0800-5f11da" / "A23"
N = 7


def rgb_of(uid):
    u = next(x for x in U.UNITS if x["id"] == uid)
    r = u["rgb"]
    return tuple(int(r[k:k + 2], 16) for k in (0, 2, 4)), u["alpha"]


def compatible(obs, rgb, alpha, tol=6):
    a = alpha / 255.0
    for o, fc in zip(obs[:3], rgb):
        if a >= 1.0:
            if abs(o - fc) > tol:
                return False
            continue
        bg = (o - a * fc) / (1.0 - a)
        if bg < -tol / (1.0 - a) or bg > 255.0 + tol / (1.0 - a):
            return False
    return True


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    for f in (int(v) for v in sys.argv[1:]) or (4, 5):
        row = U.all_frames()[f - 1]
        by = {u["id"]: u for u in U.UNITS}
        rows = {r["id"]: r for r in row}
        order = U.PAINT_ORDER
        img = Image.open(OUT / ("frame-%d.png" % f)).convert("RGBA")
        buf = img.tobytes()
        W = img.size[0]

        def px(x, y):
            i = y * W * 4 + x * 4
            return (buf[i], buf[i + 1], buf[i + 2], buf[i + 3])

        print("=== 帧 %d" % f)
        bad = 0
        for uid in order:
            u = by[uid]
            for wx, wy in U.sample_world_points(u, rows[uid], N):
                xi, yi = int(round(wx)), int(round(wy))
                chain = [v for v in order
                         if U.in_shape(*U.world_to_local(wx, wy, rows[v], by[v]), by[v])]
                if not chain:
                    print("  !! %s 采样点(%.2f,%.2f) 不在任何单元内" % (uid, wx, wy))
                    bad += 1
                    continue
                top = chain[-1]
                obs = px(xi, yi)
                tr, ta = rgb_of(top)
                if compatible(obs, tr, ta):
                    continue
                bad += 1
                print("  %s 采样点(%.2f,%.2f) px(%d,%d) obs=%s" % (uid, wx, wy, xi, yi, obs))
                print("     覆盖链=%s  最上层=%s(%s,a%d) 与该层相容=%s"
                      % (chain, top, by[top]["rgb"], ta, True))
                print("     逐层相容:", [(v, rgb_of(v)[0], rgb_of(v)[1],
                                          compatible(obs, rgb_of(v)[0], rgb_of(v)[1], 30))
                                         for v in chain])
                if uid != top:
                    ur, ua = rgb_of(uid)
                    print("     本单元 %s(%s,a%d) 相容=%s" % (uid, by[uid]["rgb"], ua,
                                                            compatible(obs, ur, ua, 30)))
        print("  未对上 %d 个点" % bad)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
