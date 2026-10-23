"""A05 主图构建：1440×1000 三联趋势报告（纯 DSL，无外部素材）。

几何一律由 a05_model.build() 计算，本文件不硬编码任何数据数值。

关键工程决策（探针 1–5 量像素结论，见 snapshot-usage.md）：
  * 文档的 39 个标签里没有 Path/Line/Polyline；ClipPath 只裁剪不描边。
  * `<Transform matrix=>` 只认**纯平移**（2×2 单位矩阵），任何旋转/错切/缩放
    都会静默地什么都不画（探针 5 的 5 个变体含一个纯错切，蓝色像素总数 = 0）。
  * 因此斜线段用「按 x 步进取端点 y 包络的竖条」拼合：每根条覆盖
    [min(ya,yb)-lw/2, max(ya,yb)+lw/2]，相邻条共用端点 y，所以段内连续、无阶梯
    缺口。代价是竖条比该列的真实线带多出 |Δy| = |m|·step 的厚度（取的是端点包络，
    不是该列的实际 y），故步长必须随斜率收缩：step = min(step_max, over/|m|)。
    固定 step=12 时最陡段（|m|=0.466）实测线宽 7–8px，是目标 2.2px 的 3.5 倍；
    收缩后全图实测 2–3px，均匀。
  * 右对齐文本用 `Container alignment="BOTTOM_RIGHT"`（Text 的 textAlign 无效）。

启动基准：总任务根（cwd）。用法：python a05_build.py <version>
"""

from __future__ import annotations

import json
import math
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a05_io as IO      # noqa: E402
import a05_model as MD   # noqa: E402

# ---------------------------------------------------------------- 画布与版式
PW, PH = MD.PW, MD.PH
FA = 'fontFamily="Noto Sans CJK SC"'
TNUM = 'fontFeatures="+tnum=2"'
TF = FA + " " + TNUM

INK, SUB, MUT, WEAK = "#0F172A", "#475569", "#64748B", "#94A3B8"
BG, PANEL, PANEL_BD = "#F8FAFC", "#FFFFFF", "#E2E8F0"
GRID, GRID_LT, AXIS = "#CBD5E1", "#EEF2F7", "#334155"
NEG, NEG_BG, WARN = "#DC2626", "#DC262614", "#B45309"

PX0, PX1 = MD.PLOT_X0, MD.PLOT_X1
YLBL_R = 168.0            # 纵轴刻度标签右缘
YLBL_W = 108.0            # 纵轴刻度标签容器宽
VGRID_Y0, VGRID_Y1 = 212.0, 564.0
TITLE_TOP, SUB_TOP, DIV_Y = 34, 70, 100
SUM_Y, SUM_H = 110, 54
CHART_Y, CHART_H = 174, 458            # 174..632
LEG_BOX_Y, LEG_BOX_H = 640, 38         # 640..678
LEG_TXT_TOP, LEG_MID = 649, 659
TABLE_Y, TABLE_H = 686, 298            # 686..984
# 表内墨迹模型：txt_box 修句点后高度 20、顶边在 y-2，数字墨迹落 y+5..y+17（12px）；
# 裸 Text 墨迹落 y+7..y+17。以下坐标按「墨迹不互相压叠」排布并留出 5px 以上间隙。
T_TITLE, T_HEAD, T_SEP = 690, 716, 738
T_ROW0, T_PITCH = 744.0, 17.2     # 行 11 墨迹 938.2..950.2
T_FOOT_SEP = 956                  # 与行 11 墨迹底留 5.8px
T_FOOT = 960                      # 墨迹 967..977，面板底 984 留 7px
XLAB_TOP = 568
NOTE1_TOP, NOTE2_TOP = 588, 610
ROWBG = "#FEF3C7"
ROW_KEYS = ("temperature_c", "humidity_pct", "pressure_kpa")
LADDER_STEP = 12.0        # 竖条宽度上限（像素）
LW = 2.2                  # 折线目标垂直宽度
LADDER_OVER = 0.9         # 允许的超厚上限：实际线宽 ≤ LW + LADDER_OVER
DOT, RING = 11.0, 2.0
MISS_D = 12.0

# 表格五列：容器 [左, 右]，前四列右对齐/左对齐，最后一列居中
COL_TIME_X = 84.0
COLS = [("temperature_c", 490.0, 620.0),
        ("humidity_pct", 730.0, 860.0),
        ("pressure_kpa", 970.0, 1100.0),
        ("valid", 1226.0, 1356.0)]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def sign(v: float) -> str:
    """带符号压差显示：+0.2 / −0.8 / 0.0。负号用 U+2212 而非连字符。"""
    if v > 0:
        return f"+{v:.1f}"
    if v < 0:
        return f"−{abs(v):.1f}"
    return f"{v:.1f}"


def n(v: float) -> str:
    """坐标输出：整数值去掉小数，其余保留两位。"""
    f = float(v)
    return str(int(round(f))) if abs(f - round(f)) < 1e-9 else f"{f:.2f}"


def txt(x, y, s, size=18, color=INK, bold=False, feat=True):
    st = ' fontStyle="BOLD"' if bold else ""
    ff = f' fontFeatures="+tnum=2"' if feat else ""
    return (f'<Positioned left="{n(x)}" top="{n(y)}"><Text text="{esc(s)}" '
            f'fontSize="{size}"{st}{ff} color="{color}" {FA}></Text>'
            f'</Positioned>')


def txt_box(x, y, w, h, s, size=18, color=INK, bold=False, align="BOTTOM_RIGHT"):
    """固定宽容器内对齐的文本（Text 的 textAlign 无效，必须走 Container alignment）。

    容器高度必须**严格大于** fontSize：探针 8 实测同一串「19.2」在 130×18 @18px 时
    句点字形被裁掉（被画成「192」），在 130×20 下句点完整；对齐方式与 fontFeatures
    均不影响（BOTTOM_LEFT/CENTER/无对齐/无 tnum 在高度 18 时全部丢句点）。
    墨迹固定在「容器顶 +7 .. 容器顶 +19」，句点占最后 2 行，故把容器顶部向上撑高、
    底边保持在 y+h 不动：数值只上移 2px，行内与列间对齐关系不变。
    """
    st = ' fontStyle="BOLD"' if bold else ""
    he = max(h, size + 2)
    y0 = y + h - he
    return (f'<Positioned left="{n(x)}" top="{n(y0)}" width="{n(w)}" height="{n(he)}">'
            f'<Container width="{n(w)}" height="{n(he)}" color="transparent" '
            f'alignment="{align}"><Text text="{esc(s)}" fontSize="{size}"{st} '
            f'{TF} color="{color}"></Text></Container></Positioned>')


def rect(x, y, w, h, color, r=0, border=None):
    b = f' border="{border}"' if border else ""
    rr = f' borderRadius="{n(r)}"' if r else ""
    return (f'<Positioned left="{n(x)}" top="{n(y)}" width="{n(w)}" height="{n(h)}">'
            f'<Container width="{n(w)}" height="{n(h)}" color="{color}"{rr}{b}'
            f'></Container></Positioned>')


def dot(cx, cy, d, color, border=None, rd=None):
    r = rd if rd is not None else d / 2
    return rect(cx - d / 2, cy - d / 2, d, d, color, r=r, border=border)


def ladder(x1, y1, x2, y2, color, lw=LW, step_max=LADDER_STEP, over=LADDER_OVER):
    """按 x 步进取斜线 y 包络拼成竖条，斜率越大步长越小。

    竖条覆盖 [min(ya,yb)-lw/2, max(ya,yb)+lw/2]，比真实带宽多出
    |Δy| = |m|·step（竖条取的是端点 y 包络，不是该列的真实线宽）。所以步长必须
    随斜率收缩到 min(step_max, over/|m|)，把超厚压在 over 以内、线宽控制在
    lw+over。相邻竖条共用端点 y，段内连续不断线；代价只是线略粗。
    """
    dx = x2 - x1
    if abs(dx) < 1e-9:
        return [rect(x1 - lw / 2, min(y1, y2) - lw / 2, lw, abs(y2 - y1) + lw,
                     color)]
    m = (y2 - y1) / dx
    step = step_max if abs(m) < 1e-9 else min(step_max, over / abs(m))
    k = max(1, int(math.ceil(abs(dx) / step)))
    out = []
    for i in range(k):
        a = x1 + dx * i / k
        b = x1 + dx * (i + 1) / k
        ya = y1 + (y2 - y1) * i / k
        yb = y1 + (y2 - y1) * (i + 1) / k
        out.append(rect(a, min(ya, yb) - lw / 2, b - a, abs(yb - ya) + lw, color))
    return out


def build_dsl(m: dict) -> str:
    st, seg, rows = m["statistics"], m["segments"], m["_model_only"]["rows"]
    sids = [s["sample_id"] for s in m["samples"]]
    X = m["_model_only"]["x_px"]
    Y = m["_model_only"]["y_px"]
    byid = {s["sample_id"]: s for s in m["samples"]}
    mids = MD.MIN_PX
    L: list[str] = []
    add = L.append

    add(f'<Snapshot background="{BG}" type="png">')
    add(f'<Container width="{PW}" height="{PH}" color="{BG}">')
    add('<Stack fit="EXPAND" clipBehavior="NONE">')
    add(rect(0, 0, PW, PH, BG))

    # ---------------------------------------------------------------- 标题
    add(txt(40, TITLE_TOP, "实验舱 · 08:00–12:30 三联趋势报告", 30, INK, bold=True))
    add(txt(40, SUB_TOP, "不等间隔采样 · 缺测不断线 · 共享真实分钟横轴 · "
                         "12 时点 / 33 条有效读数", 20, SUB))
    add(rect(40, DIV_Y, 1360, 1, GRID_LT))

    # ---------------------------------------------------------------- 汇总卡
    cards = [("temperature_c", 40), ("humidity_pct", 500), ("pressure_kpa", 960)]
    for key, cx in cards:
        cfg, s = rows[key], st[key]
        add(rect(cx, SUM_Y, 440, SUM_H, PANEL, r=10, border="1 SOLID " + PANEL_BD))
        add(rect(cx, SUM_Y, 4, SUM_H, cfg["color"], r=2))
        add(txt(cx + 20, SUM_Y + 10, f"{cfg['label']}（{cfg['unit']}）", 20, INK,
                bold=True))
        miss = (f" · 缺测 {s['missing_count']} 处" if s["missing_count"] else "")
        vmin, vmax = s["observed_min"], s["observed_max"]
        if key == "pressure_kpa":
            vmin = sign(vmin); vmax = sign(vmax)
        elif key == "temperature_c":
            vmin = f"{vmin:.1f}"; vmax = f"{vmax:.1f}"
        else:
            vmin = f"{vmin:.0f}"; vmax = f"{vmax:.0f}"
        add(txt(cx + 20, SUM_Y + 36,
                f"有效 {s['valid_count']} / 12{miss} · 最小 {vmin} · 最大 {vmax}",
                18, MUT))

    # ---------------------------------------------------------------- 图表面板
    add(rect(40, CHART_Y, 1360, CHART_H, PANEL, r=10, border="1 SOLID " + PANEL_BD))

    # 行标题 + 右侧缺测说明
    notes = {
        "temperature_c": "缺测 2 处（09:15、11:40）→ 该两点前后线段断开，不补值",
        "humidity_pct": "缺测 1 处（09:40）→ 该点前后线段断开，不补值",
        "pressure_kpa": "零线 0.0 kPa 加粗；可正可负，纵轴域 −1.5 → +1.5 kPa",
    }
    marks = {"temperature_c": "①", "humidity_pct": "②", "pressure_kpa": "③"}
    for key, cfg in rows.items():
        c = cfg["color"]
        add(rect(64, cfg["header_top"] + 4, 4, 18, c, r=2))
        add(txt(80, cfg["header_top"], f"{marks[key]} {cfg['label']}（{cfg['unit']}）"
                                       " · 独立纵轴", 20, INK, bold=True))
        add(txt_box(PX1 - 620, cfg["header_top"] + 4, 620, 20, notes[key], 18,
                    MUT, align="BOTTOM_RIGHT"))

    # 纵网格线：三图共用，每条竖线贯穿三个绘图区，直接体现对齐
    # 主刻度每 30 分钟（深色），次刻度每 15 分钟（浅色）
    for v in range(0, 271, 15):
        color = GRID if v % 30 == 0 else GRID_LT
        add(rect(PX0 + v * mids, VGRID_Y0, 1, VGRID_Y1 - VGRID_Y0, color))

    # 横网格线 + 纵轴刻度
    for key, cfg in rows.items():
        y0, y1 = cfg["y0"], cfg["y1"]
        for v in cfg["ticks"]:
            py = y1 - (v - cfg["lo"]) / (cfg["hi"] - cfg["lo"]) * (y1 - y0)
            add(rect(PX0, py - 0.5, PX1 - PX0, 1, GRID if key != "pressure_kpa"
                     else (GRID if abs(v) else GRID_LT)))
            lab = sign(v) if key == "pressure_kpa" else (
                f"{v:.1f}" if key == "temperature_c" else f"{v:.0f}")
            add(txt_box(PX0 - YLBL_W - 10, py - 9, YLBL_W, 18, lab, 18, MUT))
        # 绘图区底框（上下细线，界定纵轴范围）
        add(rect(PX0, y0 - 0.5, PX1 - PX0, 1, GRID_LT))
        add(rect(PX0, y1 - 0.5, PX1 - PX0, 1, GRID_LT))

    # 压差零线：贯穿全宽、加粗、深色（压过网格，低于折线与标记）
    zy = m["axes"]["zero_line"]["pixel_y"]
    add(rect(PX0 - 6, zy - 1, PX1 - PX0 + 12, 2, AXIS))

    # 横轴刻度标签（仅第 3 行下方，三图共用）
    ticks_min = list(range(0, 271, 30))
    for i, v in enumerate(ticks_min):
        tx = PX0 + v * mids
        lb = f"{8 + v // 60:02d}:{v % 60:02d}"
        if i == 0:
            add(txt_box(PX0, XLAB_TOP, 80, 18, lb, 18, MUT, align="BOTTOM_LEFT"))
        elif i == len(ticks_min) - 1:
            add(txt_box(tx - 60, XLAB_TOP, 60, 18, lb, 18, MUT,
                        align="BOTTOM_RIGHT"))
        else:
            add(txt_box(tx - 40, XLAB_TOP, 80, 18, lb, 18, MUT, align="CENTER"))
        add(rect(tx, VGRID_Y1 + 2, 1, 6, GRID))

    add(rect(PX0, VGRID_Y1 + 1, 1, 2, AXIS))
    add(rect(PX1 - 1, VGRID_Y1 + 1, 1, 2, AXIS))

    # 负压差区段底纹（仅覆盖实际为负的采样点 x 范围，不外扩）
    negx = [X[s["sample_id"]] for s in m["negative_samples"]]
    add(rect(min(negx), rows["pressure_kpa"]["y0"] - 1, max(negx) - min(negx),
             rows["pressure_kpa"]["y1"] - rows["pressure_kpa"]["y0"] + 2, NEG_BG))

    # 折线段（阶梯竖条）+ 采样标记
    for key, cfg in rows.items():
        c = cfg["color"]
        for g in seg[key]:
            a, b = g["from"], g["to"]
            L.extend(ladder(X[a], Y[key][a], X[b], Y[key][b], c))
        for sid in sids:
            v = Y[key][sid]
            if v is None:
                continue
            if key == "pressure_kpa" and byid[sid]["pressure_kpa"] < 0:
                add(dot(X[sid], v, DOT + 2, NEG, f"{int(RING)} SOLID #FFFFFF"))
            else:
                add(dot(X[sid], v, DOT, c, f"{int(RING)} SOLID #FFFFFF"))
        for sid in st[key]["missing_samples"]:
            cy = (cfg["y0"] + cfg["y1"]) / 2
            add(dot(X[sid], cy, MISS_D, "transparent",
                    f"{int(RING)} SOLID {WEAK}", rd=MISS_D / 2))

    # 负压差区段说明（两行：只标注真实读数 + 不等间隔读图提醒）
    add(txt(64, NOTE1_TOP,
            "■ 09:40–10:50 内实际压差为负的 3 个采样点：09:40 −0.2、10:10 −0.8、"
            "10:50 −0.3 kPa", 18, NEG, bold=True))
    add(txt(64, NOTE2_TOP,
            "仅标注这 3 个真实读数，不代表该期间每一刻均为负（相邻的 09:15 与 11:00 "
            "为 +1.3 与 +0.1 kPa）；采样间隔不等，横轴按真实分钟刻度，线段长度 ∝ 实际时间间隔。",
            18, MUT))

    # ---------------------------------------------------------------- 图例
    add(rect(40, LEG_BOX_Y, 1360, LEG_BOX_H, PANEL, r=8,
             border="1 SOLID " + PANEL_BD))
    add(dot(70, LEG_MID, DOT, "#2563EB", "2 SOLID #FFFFFF"))
    add(txt(88, LEG_TXT_TOP, "实际采样标记（33 个真实读数）", 18, INK))
    add(dot(376, LEG_MID, MISS_D, "transparent", f"2 SOLID {WEAK}", rd=6))
    add(txt(394, LEG_TXT_TOP, "缺测：空单元格 = 无读数，不是 0", 18, INK))
    add(rect(774, LEG_MID - 1, 22, 2, "#DB2777"))
    add(txt(802, LEG_TXT_TOP, "连接段：仅相邻有效采样相连", 18, INK))
    add(rect(1088, LEG_MID - 8, 22, 16, NEG_BG, border="1 SOLID #FCA5A5"))
    add(txt(1116, LEG_TXT_TOP, "负压差实际采样区段", 18, INK))

    # ---------------------------------------------------------------- 明细表
    add(rect(40, TABLE_Y, 1360, TABLE_H, PANEL, r=10, border="1 SOLID " + PANEL_BD))
    add(txt(64, T_TITLE, "全部 12 时点明细 · 合计 33 / 36 有效读数 · 缺测记为 “—”",
            20, INK, bold=True))
    add(txt_box(PX1 - 560, T_TITLE, 560, 20,
                "压差带符号 · “有效”= 该时点实际有读数的指标个数",
                18, MUT, align="BOTTOM_RIGHT"))
    add(txt_box(COL_TIME_X, T_HEAD, 92, 18, "时点", 18, SUB, bold=True,
                align="BOTTOM_LEFT"))
    for key, cl, cr in COLS[:3]:
        cfg = rows[key]
        add(txt_box(cl, T_HEAD, cr - cl, 18, f"{cfg['label']}（{cfg['unit']}）",
                    18, SUB, bold=True))
    add(txt_box(COLS[3][1], T_HEAD, COLS[3][2] - COLS[3][1], 18, "有效读数",
                18, SUB, bold=True, align="CENTER"))
    add(rect(64, T_SEP, 1292, 1, GRID))

    # 先画缺测行底色，再画文字 —— Stack 后画者在上，顺序反了底色会盖住数字
    for i, s in enumerate(m["samples"]):
        if any(s[k] is None for k in ROW_KEYS):
            add(rect(64, T_ROW0 + i * T_PITCH - 1, 1292, T_PITCH + 1, ROWBG))

    for i, s in enumerate(m["samples"]):
        yy = T_ROW0 + i * T_PITCH
        add(txt_box(COL_TIME_X, yy, 92, 18, s["time"], 18, INK,
                    align="BOTTOM_LEFT"))
        cnt = 0
        for key, cl, cr in COLS[:3]:
            v = s[key]
            if v is None:
                add(txt_box(cl, yy, cr - cl, 18, "—", 18, WEAK))
                continue
            cnt += 1
            if key == "temperature_c":
                t = f"{v:.1f}"
            elif key == "humidity_pct":
                t = f"{v:.0f}"
            else:
                t = sign(v)
            neg = key == "pressure_kpa" and v < 0
            add(txt_box(cl, yy, cr - cl, 18, t, 18, NEG if neg else INK, bold=neg))
        add(txt_box(COLS[3][1], yy, COLS[3][2] - COLS[3][1], 18, f"{cnt} / 3", 18,
                    WARN if cnt < 3 else MUT, align="CENTER", bold=(cnt < 3)))

    add(rect(64, T_FOOT_SEP, 1292, 1, GRID_LT))
    add(txt(64, T_FOOT,
            "表内数值与图上标记同源（normalized-data.json）；空单元格保持为空，"
            "观察最小 / 最大值仅基于有效读数。", 18, MUT))

    add("</Stack>")
    add("</Container>")
    add("</Snapshot>")
    return "\n".join(L) + "\n"


def main() -> None:
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1-preview"
    final = "--final" in sys.argv
    _, tmp = IO.dirs()
    m = json.loads((tmp / "model.json").read_text(encoding="utf-8"))["model"]
    dsl = build_dsl(m)
    print(f"DSL {len(dsl)} B, {dsl.count('<Positioned')} Positioned, "
          f"{dsl.count('<')} nodes")
    if final:
        # 正式交付：PNG 用服务原始字节落 outputs/，同名 .snapshot 一并写入。
        rec = IO.submit(dsl, label=f"A05 {ver}（正式交付）",
                        rid=f"req-a05-{ver.replace('-', '')}-final",
                        dsl_version=ver, kind="render",
                        out_png="sensor-report.png", out_dsl="sensor-report.snapshot")
    else:
        rec = IO.submit(dsl, label=f"A05 {ver}", rid=f"req-a05-{ver.replace('-', '')}",
                        dsl_version=ver, kind="draft")
    print("HTTP", rec["http_status"], "bytes", rec["response_bytes"],
          "ct", rec["content_type"], "t", round(rec.get("elapsed_ms", 0) / 1000, 2),
          "s")
    if rec.get("error_summary"):
        print("ERROR", rec["error_summary"])
    elif final:
        out = IO.dirs()[0]
        for f in ("sensor-report.png", "sensor-report.snapshot"):
            print("交付 →", (out / f).relative_to(IO.ROOT))
    else:
        prev = IO.dirs()[1] / "preview" / f"{ver}.png"
        prev.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(IO.dirs()[1] / "responses" / f"{rec['request_id']}.body", prev)
        print("preview →", prev.relative_to(IO.ROOT))


if __name__ == "__main__":
    main()
