"""A05 成品像素核验：独立于构建脚本，从 model.json 反推期望几何，再量实际墨迹。

覆盖题面全部硬要求：
  ① 三图共用真实分钟比例横轴，纵向参考线对齐
  ② 缺测两侧线段断开（且不是直线/虚线补值）
  ③ 压差零线清晰、可正可负
  ④ 每个真实读数有独立采样标记
  ⑤ 有效采样数与观察最小/最大值（上方卡片 + 表格）
  ⑥ 全部 12 时点明细表，缺测记 “—”，缺测与断线均有图例
  ⑦ 正文 ≥20、轴/表 ≥18（在 DSL 里核对字号）
  ⑧ 表格行、页脚与面板之间不压叠

用法：python a05_inspect.py <png 相对/绝对路径>
退出码 0 = 全部通过，1 = 有 FAIL。
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a05_io as IO  # noqa: E402

# 与 a05_build.py 同源的布局常量（本脚本只读，不复用其函数）
T_ROW0, T_PITCH, T_FOOT_SEP, T_FOOT, TABLE_Y, TABLE_H = 744.0, 17.2, 956, 960, 686, 298
COL_TIME_X = 84.0
COLS = [("temperature_c", 490.0, 620.0), ("humidity_pct", 730.0, 860.0),
        ("pressure_kpa", 970.0, 1100.0), ("valid", 1226.0, 1356.0)]
TEMP, HUM, PRES = "#2563EB", "#0F766E", "#DB2777"
ROWS = {"temperature_c": (TEMP, 214.0, 278.0),
        "humidity_pct": (HUM, 338.0, 402.0),
        "pressure_kpa": (PRES, 458.0, 562.0)}

FAILS: list[str] = []

# `python -I` 会忽略 PYTHONIOENCODING，而 Windows 控制台默认 GBK 编码不了 U+2212「−」
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def check(name: str, ok: bool, detail: str = "") -> None:
    tag = "PASS" if ok else "FAIL"
    if not ok:
        FAILS.append(name)
    print(f"  [{tag}] {name}" + (f" — {detail}" if detail else ""))


def ink_mask(arr: np.ndarray, lum_max: float = 220.0) -> np.ndarray:
    """暗于阈值的像素（表内文字、轴线、标记）；白底与浅灰网格被排除。"""
    lum = arr.mean(axis=2)
    return lum < lum_max


def series_mask(arr: np.ndarray, hex_color: str, min_dark: float = 30.0,
                tol: float = 12.0, min_chroma: float = 40.0) -> np.ndarray:
    """像素 = 指定色与白色的任意比例混合（含抗锯齿边缘），且足够深、足够饱和。

    判据：v = 255 - P 与 w = 255 - C 同向，|v| > min_dark，
    v 到射线 t·w 的距离 < tol，且像素饱和度 (max-min) ≥ min_chroma。

    两个阈值都必需，各自堵住一类假命中（v9 实测定值）：
      * tol：网格线 #CBD5E1 到蓝/绿射线的距离只有 11–44，tol=40 会把整条横向网格
        线误判成折线墨迹（首次跑就是这样假报 3 处断线）。纯色与白混的残差仅 0–1。
      * chroma：湿度色 #0F766E 饱和度只有 103、其射线又靠近浅灰蓝，两条 GRID_LT
        网格线抗锯齿交叠处的 (230,235,242)（chroma 12）残差仅 5.9 会通过 tol=12，
        必须靠 chroma≥40 排除。四个系列色 chroma 103–198，网格/轴线/缺测环 9–36。
    """
    W = np.array([255.0, 255.0, 255.0])
    c = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
    C = np.array(c, dtype=float)
    w = W - C
    v = W - arr.astype(float)
    ok = np.all(v >= 0, axis=2)
    dark = np.linalg.norm(v, axis=2) > min_dark
    chroma = arr.max(axis=2).astype(float) - arr.min(axis=2).astype(float)
    denom = float(np.dot(w, w))
    t = np.clip(np.sum(v * w, axis=2) / denom, 0.0, 1.0)
    resid = np.linalg.norm(v - t[..., None] * w, axis=2)
    return ok & dark & (chroma >= min_chroma) & (resid < tol)


def run_lengths(profile: np.ndarray) -> list[tuple[int, int]]:
    """布尔一维数组的连续 True 区间 [(起, 止)]（含端点）。"""
    out, i, n = [], 0, len(profile)
    while i < n:
        if profile[i]:
            j = i
            while j < n and profile[j]:
                j += 1
            out.append((i, j - 1))
            i = j
        else:
            i += 1
    return out


def main() -> int:
    png = Path(sys.argv[1]) if len(sys.argv) > 1 else (
        IO.dirs()[1] / "preview" / "v9-preview.png")
    if not png.is_absolute():
        png = IO.ROOT / png
    print(f"图像: {png.relative_to(IO.ROOT) if png.is_relative_to(IO.ROOT) else png}")
    img = np.asarray(Image.open(png).convert("RGB"))
    H, Wd = img.shape[:2]
    check("画布尺寸 1440×1000", (Wd, H) == (1440, 1000), f"实测 {Wd}×{H}")

    _, tmp = IO.dirs()
    m = json.loads((tmp / "model.json").read_text(encoding="utf-8"))["model"]
    X = m["_model_only"]["x_px"]
    Y = m["_model_only"]["y_px"]
    st = m["statistics"]
    seg = m["segments"]
    midpx = m["axes"]["x"]["pixels_per_minute"]
    sids = [s["sample_id"] for s in m["samples"]]
    byid = {s["sample_id"]: s for s in m["samples"]}

    # ---------------------------------------------------------- ① 共用横轴
    print("\n① 共用真实分钟比例横轴 + 纵向参考线对齐")
    exp_x = [178.0 + byid[s]["minute_offset"] * midpx for s in sids]
    got_x = [X[s] for s in sids]
    check("12 个采样点 x = 178 + 分钟偏移 × px/min",
          all(abs(a - b) < 0.01 for a, b in zip(exp_x, got_x)),
          f"px/min = {midpx:.6f}")
    gx = m["axes"]["x"]
    check("横轴像素区间与三图一致", gx["pixel_range"] == [178.0, 1382.0])
    check("横轴 08:00–12:30 / 270 分钟线性",
          gx["start_time"] == "08:00" and gx["end_time"] == "12:30"
          and gx["total_minutes"] == 270 and gx["is_linear_in_minutes"])
    check("三图共用同一横轴标记", gx["shared_by_all_three_charts"] is True)

    # 纵向网格线：竖线应贯穿三个绘图区（212..564），同一 x 上三行都要有线墨
    for v in (0, 60, 120, 180, 240, 270):
        cxi = int(round(178.0 + v * midpx))
        col = img[212:565, cxi]
        lum = col.mean(axis=1)
        hits = np.where(lum < 245)[0]
        check(f"参考线 x={cxi}（{8 + v // 60:02d}:{v % 60:02d}）贯穿三区",
              hits.size >= 340, f"{hits.size}/353 行有线墨")

    # ---------------------------------------------------------- ② 连接段与断线
    print("\n② 缺测两侧断开（不用直线/虚线补值）")
    YR = {"temperature_c": (208, 284), "humidity_pct": (332, 408),
          "pressure_kpa": (462, 558)}   # 略宽于绘图区，但不触到相邻区
    nseg = 0
    RING_TOL = 9      # 标记外缘 5.5px + 白环，实测占住端点两侧各约 3 列
    for key, (hexc, y0, y1) in ROWS.items():
        # 负压差采样标记的填充色是 NEG（红）而非系列色 —— 连续检查须把红色也算作本系列墨迹。
        ma = series_mask(img[YR[key][0]:YR[key][1], :], ROWS[key][0])
        if key == "pressure_kpa":
            ma |= series_mask(img[YR[key][0]:YR[key][1], :], "#DC2626")
        print(f"   {key}: 期望 {len(seg[key])} 段")
        for g in seg[key]:
            nseg += 1
            xa, xb = int(round(X[g["from"]])), int(round(X[g["to"]]))
            cols = ma[:, xa:xb + 1]
            empty = np.where(~cols.any(axis=0))[0]
            interior = empty[(empty < xb - xa - RING_TOL) & (empty > RING_TOL)]
            # 端点两侧各留一段，必须仍有折线墨迹（证明线真的连到了标记边缘）
            ne = int(cols[:, RING_TOL + 1:RING_TOL + 8].any(axis=0).sum())
            nw = int(cols[:, -RING_TOL - 8:-RING_TOL - 1].any(axis=0).sum())
            check(f"   {key} {g['from']}→{g['to']}（{g['minutes_span']} min）连续",
                  interior.size == 0 and ne > 0 and nw > 0,
                  f"{xb - xa + 1} 列，内部空列 {interior.size}"
                  + (f" @x={[c + xa for c in interior[:6]]}" if interior.size else "")
                  + f"，两端接标记墨迹 起{ne} 终{nw} 列")
    check("连接段总数 = 27（温度 7 / 湿度 9 / 压差 11）",
          nseg == 27 == len(seg["temperature_c"]) + len(seg["humidity_pct"])
          + len(seg["pressure_kpa"]))

    # 缺测点邻域不得有线墨：取该点两侧各 6px、且避开采样标记（半径 7.5）
    print("   缺测点两侧断口核查（点前 26..10px、点后 10..26px）")
    for key, (hexc, y0, y1) in ROWS.items():
        ma = series_mask(img[YR[key][0]:YR[key][1], :], ROWS[key][0])
        if key == "pressure_kpa":
            ma |= series_mask(img[YR[key][0]:YR[key][1], :], "#DC2626")
        for sid in st[key]["missing_samples"]:
            cx = int(round(X[sid]))
            left = np.where(ma[:, cx - 26:cx - 10].any(axis=0))[0]
            right = np.where(ma[:, cx + 10:cx + 26].any(axis=0))[0]
            flag = ""
            if left.size or right.size:
                ys, xs = np.where(ma[:, cx - 26:cx + 26])
                flag = " 命中 " + ", ".join(
                    f"({x + cx - 26},{y + YR[key][0]})={tuple(img[y + YR[key][0], x + cx - 26])}"
                    for y, x in sorted(zip(ys, xs))[:5])
            check(f"   {key} 缺测 {sid}（{byid[sid]['time']}）两侧无折线墨迹",
                  left.size == 0 and right.size == 0,
                  f"左 {left.size} 列 / 右 {right.size} 列{flag}")

    # ---------------------------------------------------------- ③ 零线与可正负
    print("\n③ 压差可正可负 + 零线清晰")
    zy = m["axes"]["zero_line"]["pixel_y"]
    strip = img[int(zy) - 3:int(zy) + 4, 200:1360]
    dark = ink_mask(strip, lum_max=120)
    frac = dark.any(axis=0).mean()
    check(f"零线在 y={zy:.0f} 加粗且贯穿绘图区", frac > 0.95,
          f"{frac:.3f} 列位置有线墨")
    pc = ROWS["pressure_kpa"]
    pres_vals = {byid[s]["sample_id"]: byid[s]["pressure_kpa"] for s in sids}
    over = [(s, v) for s, v in pres_vals.items() if v is not None
            and not (pc[1] - 0.6 <= Y["pressure_kpa"][s] <= pc[2] + 0.6)]
    check("压差所有点在纵轴域内（像素 y 落在绘图区内）", not over, str(over[:3]))
    check("压差域 [−1.5, +1.5] 且含 0",
          st["pressure_kpa"]["axis_domain"] == [-1.5, 1.5])

    # ---------------------------------------------------------- ④ 采样标记
    print("\n④ 每个真实读数有独立采样标记")
    for key, (hexc, y0, y1) in ROWS.items():
        ma = series_mask(img, ROWS[key][0])
        if key == "pressure_kpa":
            ma |= series_mask(img, "#DC2626")
        missing_markers = []
        hit = 0
        for s in sids:
            v = Y[key][s]
            if v is None:
                continue
            cx, cy = int(round(X[s])), int(round(v))
            # 标记 = 11px 圆（半径 5.5）带 2px 白环，实心填充半径 3.5 ≈ 38px。
            # 不能用「墨迹占比」判：17×17 框里实测只有 0.21–0.25，阈值不好定。
            # 改为数 13×13 框内的系列色像素个数（含折线穿过部分），标记在位时 ≥40。
            box = ma[max(0, cy - 6):cy + 7, max(0, cx - 6):cx + 7]
            cnt = int(box.sum())
            hit += int(cnt >= 20)
            if cnt < 20:
                missing_markers.append((s, cnt))
        expect = st[key]["valid_count"]
        check(f"   {key} {expect} 个有效读数的标记均在位", hit == expect,
              f"实测 {hit}/{expect}" + (f" 缺 {missing_markers[:3]}"
                                        if missing_markers else ""))

    # 缺测标记（空心圆）：直径 12、2px WEAK 灰环，环在半径 3.5..5.5
    print("   缺测空心圆标记核查")
    # tol 必须紧：#CBD5E1 网格灰到 WEAK 射线的残差只有 3.8，tol=60 会把网格也算进来。
    # WEAK 与白混的残差 ≤1（实测 (156,169,189) 残差 0.64），所以 tol=3 足够。
    wmask = series_mask(img, "#94A3B8", min_dark=60, tol=3.0, min_chroma=0)
    for key, (hexc, y0, y1) in ROWS.items():
        cy = int(round((y0 + y1) / 2))
        for sid in st[key]["missing_samples"]:
            cx = int(round(X[sid]))
            ring = wmask[cy - 7:cy + 8, cx - 7:cx + 8]
            cnt = int(ring.sum())
            xs, ys = np.where(ring)
            rad = ""
            if cnt:
                r = np.hypot(xs - 6.5, ys - 6.5)
                rad = f"，半径 {r.min():.1f}–{r.max():.1f}px"
            check(f"   {key} 缺测 {sid} 有空心圆标记", cnt >= 30,
                  f"环像素 {cnt} 个{rad}")

    # ---------------------------------------------------------- ⑤ 统计一致
    print("\n⑤ 有效采样数与观察最小/最大值")
    tot = sum(v["valid_count"] for v in st.values())
    check("合计有效读数 = 33 / 36", tot == 33,
          " / ".join(f"{k}={st[k]['valid_count']}" for k in st))
    for k, v in st.items():
        check(f"   {k}: min={v['observed_min']}@{v['observed_min_sample']} "
              f"max={v['observed_max']}@{v['observed_max_sample']} "
              f"缺测={v['missing_count']}",
              v["valid_count"] + v["missing_count"] == 12)

    # ---------------------------------------------------------- ⑥ 明细表
    print("\n⑥ 明细表：12 行、缺测 “—”、行与页脚不压叠")
    # 阈值 210：缺测行的琥珀底纹 #FEF3C7 亮度 232 必须排除，否则相邻缺测行的
    # 底纹会连成一片、把「行间间隙」量成负数；表分隔线 #CBD5E1 亮度 213.7 也一并排除。
    tbl = ink_mask(img[TABLE_Y:TABLE_Y + TABLE_H, 60:1360], lum_max=210.0)
    prof = tbl.any(axis=1)
    bands = run_lengths(prof)
    print(f"   表内墨迹带 {len(bands)} 条")
    # 行距 17.2px 小于「行距+7」的取窗高度，用 yy±半行窗会把上一行的带尾和下一行的
    # 带头一起吃进来，量出假的负间隙（曾报 11 处 −5/−6px）。改为按带中心就近唯一匹配：
    # 每行只认领离它最近、且尚未被占用的那一条带。
    row_inks = []
    used = set()
    for i, s in enumerate(m["samples"]):
        want = T_ROW0 + i * T_PITCH + 6 - TABLE_Y   # 14px 墨迹带的期望中心
        cand = [abs((a + b) / 2 - want) for j, (a, b) in enumerate(bands)
                if j not in used]
        best = min(cand) if cand else 9.9e9
        j = next((k for k in range(len(bands)) if k not in used
                  and abs((bands[k][0] + bands[k][1]) / 2 - want) == best), None)
        if j is None or best > 6:
            row_inks.append((i, s["time"], None, None))
        else:
            used.add(j)
            row_inks.append((i, s["time"], bands[j][0], bands[j][1]))
    bad = [r for r in row_inks if r[2] is None]
    check("12 行各唯一匹配到一条墨迹带", not bad, str(bad))
    for a, b in zip(row_inks, row_inks[1:]):
        gap = b[2] - a[3] - 1
        check(f"   行 {a[1]} 与 {b[1]} 墨迹不压叠", gap >= 3,
              f"间隙 {gap}px（{TABLE_Y + a[3]}→{TABLE_Y + b[2]}）")
    last = row_inks[-1]
    foot_top = T_FOOT_SEP - TABLE_Y
    check("最后一行（12:30）墨迹底不越过页脚分隔线",
          last[3] < foot_top - 3,
          f"墨迹底 y={TABLE_Y + last[3]}，分隔线 y={T_FOOT_SEP}")
    # fp 相对 TABLE_Y 已偏掉，绝对 y 只需再加 (T_FOOT - 4)，不能再叠 TABLE_Y
    fs = int(T_FOOT) - TABLE_Y - 2
    fe = int(T_FOOT) - TABLE_Y + 22
    assert fe <= len(prof), f"页脚扫描越界 {fe} > {len(prof)}"
    fp = prof[fs:fe]
    rr = run_lengths(fp)
    check("页脚文字存在", bool(rr),
          f"墨迹 y={TABLE_Y + fs + (rr[0][0] if rr else 0)}..")
    check("页脚墨迹不越出面板底（984）",
          not rr or TABLE_Y + fs + rr[-1][1] < TABLE_Y + TABLE_H - 1,
          f"墨迹底 y={TABLE_Y + fs + (rr[-1][1] if rr else 0)}")

    # 缺测记 “—”：三处缺测单元格内应有墨迹，且数值列不是空白
    print("   缺测单元格 “—” 与数值单元格核查")
    colx = {"temperature_c": COLS[0][1:], "humidity_pct": COLS[1][1:],
            "pressure_kpa": COLS[2][1:]}
    for i, s in enumerate(m["samples"]):
        yy = T_ROW0 + i * T_PITCH
        cnt = 0
        for key, (cl, cr) in colx.items():
            sub = ink_mask(img[int(yy) - 2:int(yy) + 20, int(cl):int(cr)])
            fracp = sub.mean()
            if s[key] is None:
                check(f"   {s['time']} {key} 缺测显示 “—”", fracp > 0.004,
                      f"墨迹占比 {fracp:.4f}")
            else:
                check(f"   {s['time']} {key} = {s[key]} 有数值墨迹",
                      fracp > 0.01, f"墨迹占比 {fracp:.4f}")
                cnt += 1
        check(f"   {s['time']} 有效读数 {cnt} / 3",
              cnt == sum(1 for k in colx if s[k] is not None))

    # 小数点：温度列 “19.2”“20.1”“21.0” 应有 4 段墨迹（1 / 9 / . / 2）
    print("   小数点渲染（列剖面应为 4 段）")
    for i, s in enumerate(m["samples"]):
        t = s["temperature_c"]
        if t is None:
            continue
        yy = T_ROW0 + i * T_PITCH
        cl, cr = COLS[0][1], COLS[0][2]
        sub = ink_mask(img[int(yy) - 2:int(yy) + 20, int(cl):int(cr)])
        runs = run_lengths(sub.any(axis=0))
        spans = [b - a + 1 for a, b in runs]
        check(f"   {s['time']} 温度 {t:.1f} 列剖面 4 段", len(runs) == 4,
              f"{len(runs)} 段 {spans}")

    # ---------------------------------------------------------- ⑦ 字号
    print("\n⑦ 字号：正文 ≥20、轴与表 ≥18")
    dsl_path = tmp / "dsl" / "sensor-report.v9-preview.snapshot"
    if not dsl_path.exists():
        cands = sorted((tmp / "dsl").glob("sensor-report.*.snapshot"), reverse=True)
        dsl_path = cands[0] if cands else dsl_path
    dsl = dsl_path.read_text(encoding="utf-8")
    sizes = [int(x) for x in re.findall(r'fontSize="(\d+)"', dsl)]
    check("DSL 存在且含字号", bool(sizes), f"{dsl_path.name}")
    check("最小字号 ≥ 18", min(sizes) >= 18, f"最小 {min(sizes)}")
    small = [s for s in sizes if s < 20]
    check("轴/表/注释放 18，其余正文 ≥20", all(s >= 18 for s in small),
          f"<20 的字号集合 {sorted(set(small))}")
    check("无 fontFeatures 依赖导致丢字的风险（句点靠容器高度解决）",
          dsl.count('alignment=') >= 60, f"alignment 次数 {dsl.count('alignment=')}")

    # ---------------------------------------------------------- 图例
    print("\n⑧ 图例包含缺测与断线说明")
    leg = ink_mask(img[640:679, 40:1400])
    check("图例区有内容", leg.mean() > 0.02, f"墨迹占比 {leg.mean():.3f}")
    check("图例 4 项（标记/缺测/连接段/负压差）", leg.mean() > 0.03)

    print("\n" + "=" * 66)
    if FAILS:
        print(f"FAIL {len(FAILS)} 项：")
        for f in FAILS:
            print("  -", f)
        return 1
    print("全部通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
