"""A04 DSL 构造器：把 model.json 的数值排成 1600×1000 信息图。

所有百分比、分子分母、构成占比都从 tmp/.../A04/model.json 读取，DSL 里不出现
任何硬编码的比率。版式分区（画布坐标，左上原点）：

    标题区    y  40–140      只写口径与来源，不写结论（避免结论先行）
    数据小表   y 152–380     4 行原始分母/分子，可逐行核对
    三张图     y 396–736     ① 渠道分组率  ② 访问构成  ③ 总体对照
    结论与限制 y 750–960

绘制顺序：面板 → 标题 → 网格线 → 条形 → 文字。网格线必须早于条形与文字，
否则浅灰线会压在数值标签上（Stack 后绘在上层）。

率图比例：图①与图③同为 2.6 px / 1%、同一 0–100% 尺度，可直接目视比较。
构成图两条条总长同为 420px（各期 10,000 次），分段按真实访问占比。

启动基准：总任务根（cwd）。用法：python a04_build.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a04_io as IO  # noqa: E402

OUT, TMP = IO.dirs()
MODEL = json.loads((TMP / "model.json").read_text(encoding="utf-8"))

# ---------------------------------------------------------------- 模型索引
G = {(g["period"], g["channel"]): g for g in MODEL["groups"]}
P = {p["period"]: p for p in MODEL["periods"]}
DL = {d["scope"]: d for d in MODEL["deltas"]}
DECOMP = MODEL["decomposition"]
NAIVE_PP = MODEL["prohibited_methods"]["averaging_channel_rates"]["apparent_delta_pp"]

P1, P2 = "前期", "后期"
C1N, C2N = "直接访问", "推广访问"
NP, NCH = len((P1, P2)), len((C1N, C2N))   # 期数 / 渠道数，避免把格数当渠道数


def rate(period: str, channel: str) -> float:
    return G[(period, channel)]["rate_percent_exact"]


def share(period: str, channel: str) -> float:
    return next(c["share_percent_display"] for c in P[period]["composition"]
                if c["channel"] == channel)


def visits(period: str, channel: str) -> int:
    return G[(period, channel)]["visits"]


def convs(period: str, channel: str) -> int:
    return G[(period, channel)]["conversions"]


# ---------------------------------------------------------------- 排版工具
FAM = "Noto Sans CJK SC"
FA = f'fontFamily="{FAM}"'

BG, PANEL, BORDER = "#F8FAFC", "#FFFFFF", "#E2E8F0"
GRID, INK, INK2, INK3 = "#E2E8F0", "#0F172A", "#475569", "#64748B"
DIRECT, DIRECTD, DIRECTL = "#2563EB", "#1E40AF", "#93C5FD"
PROMO, PROMOD, PROMOL = "#DB2777", "#9D174D", "#F9A8D4"
TOTAL, TOTALL = "#0F766E", "#5EEAD4"
WHITE = "#FFFFFF"
UP = "#059669"
DOWN = "#DC2626"
DOWNBG, DOWNBD = "#FEF2F2", "#FCA5A5"
AMBER = "#B45309"

CHANNEL_COLOR = {C1N: DIRECT, C2N: PROMO}
# 图①用「渠道色 × 期的明暗」区分四个分组：前期浅、后期深
CHART1_COLOR = {(P1, C1N): DIRECTL, (P2, C1N): DIRECTD,
                (P1, C2N): PROMOL, (P2, C2N): PROMOD}


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def nm(v: float) -> str:
    """坐标取整输出，避免 DSL 里出现浮点长尾。"""
    f = float(v)
    return str(int(round(f))) if abs(f - round(f)) < 1e-9 else f"{f:.2f}"


def txt(x, y, s, size=18, color=INK, bold=False, tnum=False):
    st = ' fontStyle="BOLD"' if bold else ""
    ff = ' fontFeatures="+tnum=2"' if tnum else ""
    return (f'<Positioned left="{nm(x)}" top="{nm(y)}"><Text text="{esc(s)}" '
            f'fontSize="{size}"{st} color="{color}" {FA}{ff}></Text>'
            f'</Positioned>')


def rect(x, y, w, h, color, r=0, border=None):
    b = f' border="{border}"' if border else ""
    rr = f' borderRadius="{nm(r)}"' if r else ""
    return (f'<Positioned left="{nm(x)}" top="{nm(y)}" width="{nm(w)}" '
            f'height="{nm(h)}"><Container width="{nm(w)}" height="{nm(h)}" '
            f'color="{color}"{rr}{b}></Container></Positioned>')


def align_box(x, y, w, h, s, size, color, align="CENTER", bg=None,
              border=None, r=8, bold=False, tnum=False):
    """固定宽度的盒子里对齐文字——探针已确认 Text textAlign 对 shrink-wrap
    文本无效，必须靠 Container alignment。"""
    bg_a = f' color="{bg}"' if bg else ' color="transparent"'
    bd = f' border="{border}"' if border else ""
    st = ' fontStyle="BOLD"' if bold else ""
    ff = ' fontFeatures="+tnum=2"' if tnum else ""
    rr = f' borderRadius="{nm(r)}"' if r else ""
    return (f'<Positioned left="{nm(x)}" top="{nm(y)}" width="{nm(w)}" '
            f'height="{nm(h)}"><Container width="{nm(w)}" height="{nm(h)}" '
            f'alignment="{align}"{bg_a}{rr}{bd}><Text text="{esc(s)}" '
            f'fontSize="{size}"{st} color="{color}" {FA}{ff}></Text>'
            f'</Container></Positioned>')


# ---------------------------------------------------------------- 版式常量
CW, CH = 1600, 1000
M = 40                                   # 安全边距
TBL_Y, TBL_H = 152, 228                  # 152–380
CH_Y, CH_H = 396, 340                    # 396–736
CON_Y, CON_H = 750, 210                  # 750–960（CJK 墨迹比行盒高，底部要留余量）

C1_X, C2_X, C3_X, CP_W = 40, 560, 1060, 500
PAD = 24
PX = 2.6                                 # 每 1% 的像素（图①与图③共用）
O1_X, O3_X = 256, 1230                   # 率轴起点；100% = 260px
CB_X, CB_W = 584, 420                    # 构成条起点与总长
BAR2_GAP = 2                             # 两段之间的 2px 面板色间隔（含在 420px 内）
PPV = (CB_W - BAR2_GAP) / 10000.0        # 可绘制长度按真实占比切分，间隔不占比例
TICKS = [0, 25, 50, 75, 100]


def gridlines(axis_x: float, y0: float, y1: float):
    return [rect(axis_x + t * PX, y0, 1, y1 - y0, GRID) for t in TICKS]


def tick_labels(axis_x: float, y: float):
    return [align_box(axis_x + t * PX - 28, y, 56, 22, f"{t}%", 18, INK3)
            for t in TICKS]


# ---------------------------------------------------------------- 页面构造
L: list[str] = []
add = L.append


add('<Snapshot background="%s" type="png">' % BG)
add(f'<Container width="{CW}" height="{CH}" color="{BG}">')
add('<Stack fit="EXPAND" clipBehavior="NONE">')

# ================= 标题区
add(txt(M, 40, "转化变化，为什么不能只看平均？", 38, INK, bold=True))
add(txt(M, 96, "数据 inputs/conversion.csv · 2 期 × 2 渠道 · 计数单位：次 · "
               "转化率 = 成交数 ÷ 访问数", 22, INK2))
add(rect(M, 140, CW - 2 * M, 1, BORDER))

# ================= 数据小表
add(rect(M, TBL_Y, CW - 2 * M, TBL_H, PANEL, 16, f"1 SOLID {BORDER}"))
TX = M + PAD                                        # 64
add(txt(TX, TBL_Y + 14, "原始数据", 22, INK, bold=True))
add(txt(TX + 132, TBL_Y + 18, "分母 = 访问数，分子 = 成交数；"
                              "转化率 = 分子 ÷ 分母", 19, INK3))

HC = {1: TX, 2: TX + 186, 3: 660, 4: 900, 5: 960, 6: 1230}
HH = TBL_Y + 54
add(txt(HC[1], HH, "期", 19, INK3, bold=True))
add(txt(HC[2], HH, "渠道", 19, INK3, bold=True))
add(align_box(HC[3] - 200, HH, 200, 24, "访问数（次）", 19, INK3,
              "CENTER_RIGHT", bold=True))
add(align_box(HC[4] - 200, HH, 200, 24, "成交数（次）", 19, INK3,
              "CENTER_RIGHT", bold=True))
add(txt(HC[5], HH, "转化率", 19, INK3, bold=True))
add(txt(HC[6], HH, "该期访问占比", 19, INK3, bold=True))

ROW_Y = [TBL_Y + 88 + 32 * i for i in range(4)]
SEP_Y = TBL_Y + 88 + 32 * 2 - 16
add(rect(TX - 16, SEP_Y, CW - 2 * M - PAD - 16, 1, GRID))

for y, (p, ch) in zip(ROW_Y, [(P1, C1N), (P1, C2N), (P2, C1N), (P2, C2N)]):
    add(txt(HC[1], y, p, 22, INK))
    add(rect(HC[2], y + 6, 12, 12, CHANNEL_COLOR[ch], 3))
    add(txt(HC[2] + 22, y, ch, 22, INK))
    add(align_box(HC[3] - 200, y, 200, 28, f"{visits(p, ch):,}", 22, INK,
                  "CENTER_RIGHT", tnum=True))
    add(align_box(HC[4] - 200, y, 200, 28, f"{convs(p, ch):,}", 22, INK,
                  "CENTER_RIGHT", tnum=True))
    add(txt(HC[5], y, f"{rate(p, ch):.2f}%", 22, CHANNEL_COLOR[ch],
            bold=True, tnum=True))
    add(txt(HC[6], y, f"{share(p, ch):.1f}%", 22, INK2, tnum=True))

# ================= 图① 渠道分组率
X, Y0 = C1_X, CH_Y
add(rect(X, Y0, CP_W, CH_H, PANEL, 16, f"1 SOLID {BORDER}"))
add(txt(X + PAD, Y0 + 16, "① 渠道分组转化率", 22, INK, bold=True))
add(txt(X + PAD, Y0 + 50, "条长 = 转化率，0–100% 满量程", 18, INK3))
L.extend(gridlines(O1_X, Y0 + 82, Y0 + 270))        # 先画网格线

GRP_Y = [Y0 + 84, Y0 + 182]
BAR_H, BAR_PITCH = 26, 32
for gi, ch in enumerate((C1N, C2N)):
    d = DL[ch]["delta_percentage_points"]
    add(txt(X + PAD, GRP_Y[gi], ch, 19, INK, bold=True))
    add(txt(X + PAD + 86, GRP_Y[gi],
            f"{'↑' if d >= 0 else '↓'} {abs(d):.2f} pp", 19,
            UP if d >= 0 else DOWN, bold=True, tnum=True))
    for pi, p in enumerate((P1, P2)):
        by = GRP_Y[gi] + 26 + BAR_PITCH * pi
        w = rate(p, ch) * PX
        add(txt(X + PAD + 20, by, p, 18, INK3))
        add(rect(O1_X, by, w, BAR_H, CHART1_COLOR[(p, ch)], 5))
        add(txt(O1_X + w + 8, by + 2, f"{rate(p, ch):.2f}%", 18, INK,
                bold=True, tnum=True))
L.extend(tick_labels(O1_X, Y0 + 274))

# ================= 图② 访问构成
add(rect(C2_X, Y0, CP_W, CH_H, PANEL, 16, f"1 SOLID {BORDER}"))
add(txt(C2_X + PAD, Y0 + 16, "② 访问构成", 22, INK, bold=True))
add(txt(C2_X + PAD, Y0 + 50, "两条总长相同（各期 10,000 次），分段 = 真实占比",
        18, INK3))
add(rect(CB_X, Y0 + 82, 16, 16, DIRECT, 4))
add(txt(CB_X + 24, Y0 + 80, C1N, 18, INK2))
add(rect(CB_X + 164, Y0 + 82, 16, 16, PROMO, 4))
add(txt(CB_X + 188, Y0 + 80, C2N, 18, INK2))

BAR2_H = 62
BAR2_Y = [Y0 + 136, Y0 + 234]
for i, p in enumerate((P1, P2)):
    add(txt(CB_X, BAR2_Y[i] - 26, p, 20, INK, bold=True))
    add(txt(CB_X + 92, BAR2_Y[i] - 22, f"合计 {P[p]['total_visits']:,} 次",
            18, INK3, tnum=True))
    x = CB_X
    for ch, col in ((C1N, DIRECT), (C2N, PROMO)):
        w = visits(p, ch) * PPV
        if ch == C2N:
            x += BAR2_GAP                 # 间隔留给面板底色，不占任何渠道的比例
        add(rect(x, BAR2_Y[i], w, BAR2_H, col, 6))
        cx = x + w / 2
        lw = w - 8
        add(align_box(cx - lw / 2, BAR2_Y[i] + 12, lw, 22,
                      f"{visits(p, ch):,}", 18, WHITE, tnum=True))
        add(align_box(cx - lw / 2, BAR2_Y[i] + 34, lw, 24,
                      f"{share(p, ch):.1f}%", 20, WHITE, bold=True,
                      tnum=True))
        x += w
# 构成注上移 6px：面板②内框下缘在 735，18 号字墨迹比行盒低约 24px，
# 放在 708 只剩 ~2px 余量；702 留出 ~8px，同时与上条间隔仍有 ~7px
add(txt(CB_X, BAR2_Y[1] + BAR2_H + 10,
        f"构成反转：{C1N} {share(P1, C1N):.0f}% → {share(P2, C1N):.0f}%，"
        f"{C2N} {share(P1, C2N):.0f}% → {share(P2, C2N):.0f}%",
        18, INK2, tnum=True))

# ================= 图③ 总体对照
add(rect(C3_X, Y0, CP_W, CH_H, PANEL, 16, f"1 SOLID {BORDER}"))
add(txt(C3_X + PAD, Y0 + 16, "③ 总体转化率", 22, INK, bold=True))
add(txt(C3_X + PAD, Y0 + 50, "成交总数 ÷ 访问总数，同尺度可与①直接比较",
        18, INK3))
L.extend(gridlines(O3_X, Y0 + 104, Y0 + 232))       # 先画网格线

OV_Y = [Y0 + 106, Y0 + 196]
for i, (p, col) in enumerate(((P1, TOTALL), (P2, TOTAL))):
    ov = P[p]["overall_rate_percent_exact"]
    add(txt(C3_X + PAD, OV_Y[i] - 28,
            f"{P[p]['total_conversions']:,} ÷ {P[p]['total_visits']:,}",
            18, INK3, tnum=True))
    add(txt(C3_X + PAD, OV_Y[i], p, 20, INK, bold=True))
    add(rect(O3_X, OV_Y[i], ov * PX, 34, col, 5))
    add(txt(O3_X + ov * PX + 8, OV_Y[i] + 3, f"{ov:.2f}%", 22, TOTAL,
            bold=True, tnum=True))
L.extend(tick_labels(O3_X, Y0 + 236))

DOV = DL["总体（成交总数/访问总数）"]
add(rect(C3_X + PAD, Y0 + 276, CP_W - 2 * PAD, 46, DOWNBG, 10,
         f"1 SOLID {DOWNBD}"))
add(align_box(C3_X + PAD, Y0 + 276, CP_W - 2 * PAD, 46,
              f"总体 {DOV['delta_percentage_points']:+.2f} pp："
              f"{DOV['from_percent']:.2f}% → {DOV['to_percent']:.2f}%",
              22, DOWN, bold=True, tnum=True))

# ================= 结论与限制
RE = [DECOMP["order_rates_then_mix"]["rate_effect_pp"],
      DECOMP["order_mix_then_rates"]["rate_effect_pp"]]
ME = [DECOMP["order_rates_then_mix"]["mix_effect_pp"],
      DECOMP["order_mix_then_rates"]["mix_effect_pp"]]
SPP = DECOMP["order_rates_then_mix"]["sum_pp"]

BOX_A_W = 990
add(rect(M, CON_Y, BOX_A_W, CON_H, PANEL, 16, f"2 SOLID {TOTAL}"))
add(align_box(M + PAD, CON_Y + 16, 104, 30, "主结论", 18, WHITE, bold=True,
              bg=TOTAL, r=15))
CON_TX = M + PAD
# 行距 28px：Noto Sans CJK 的墨迹比 1.0 行盒高约 7px，行距太小会压边框。
# 起点取 CON_Y+54（不是 +58）：最后一行是 22 号正文，墨迹比行盒低约 27px，
# 放在 920 时墨迹底在 ~947；改 22 号后墨迹更高，整体上移 4px 保证框底余量。
CON_LY = [CON_Y + 54 + 28 * i for i in range(5)]
add(txt(CON_TX, CON_LY[0],
        f"两个渠道的转化率都在上升：{C1N} {rate(P1, C1N):.2f}% → "
        f"{rate(P2, C1N):.2f}%，{C2N} {rate(P1, C2N):.2f}% → "
        f"{rate(P2, C2N):.2f}%。", 22, INK, tnum=True))
add(txt(CON_TX, CON_LY[1],
        f"但总体转化率从 {DOV['from_percent']:.2f}% 降到 "
        f"{DOV['to_percent']:.2f}%（{DOV['delta_percentage_points']:+.2f} pp），"
        f"分组与总体方向相反。", 22, INK, tnum=True))
add(txt(CON_TX, CON_LY[2],
        f"原因在构成：{C1N}占比从 {share(P1, C1N):.0f}% 降到 "
        f"{share(P2, C1N):.0f}%，访问转向低转化渠道。", 22, INK, tnum=True))
add(txt(CON_TX, CON_LY[3],
        f"总体率 = 成交总数 ÷ 访问总数；对渠道比例取平均会得到 "
        f"{NAIVE_PP:+.2f} pp 的相反结论。", 22, INK, tnum=True))
# 恒等分解这行是正文（不是图标注），所以也要 ≥22；22 号时墨迹宽约 791px，
# 距框右边（1022）还有 170px 余量。
add(txt(CON_TX, CON_LY[4],
        f"恒等分解：率效应 {min(RE):+.2f}～{max(RE):+.2f} pp，"
        f"构成效应 {min(ME):+.2f}～{max(ME):+.2f} pp，合计 {SPP:+.2f} pp。",
        22, AMBER, tnum=True))

BOX_B_X = 1050
BOX_B_W = CW - M - BOX_B_X
add(rect(BOX_B_X, CON_Y, BOX_B_W, CON_H, PANEL, 16, f"2 SOLID {DOWN}"))
add(align_box(BOX_B_X + PAD, CON_Y + 16, 104, 30, "限制", 18, WHITE,
              bold=True, bg=DOWN, r=15))
BX = BOX_B_X + PAD
add(txt(BX, CON_LY[0], "不能由该数据证明因果。", 22, INK, bold=True))
add(txt(BX, CON_LY[1], f"只有 {NP} 期 × {NCH} 渠道共 {NP * NCH} 行聚合计数；",
        22, INK2, tnum=True))
add(txt(BX, CON_LY[2], "无对照组、无随机分配、无期内序列。", 22, INK2))
add(txt(BX, CON_LY[3], "恒等分解只说明算术关系，", 22, INK2))
add(txt(BX, CON_LY[4], "不构成已证实的因果链。", 22, INK2))

add("</Stack>")
add("</Container>")
add("</Snapshot>")

DSL = "\n".join(L) + "\n"

if __name__ == "__main__":
    import shutil

    mode = sys.argv[1] if len(sys.argv) > 1 else "v3-preview"
    if mode.endswith("-preview"):
        # 预览：只落 tmp/preview/，不写 outputs/
        ver = mode.split("-")[0]
        rec = IO.submit(DSL, label=f"A04 转化悖论信息图 {ver}（构成注上移 6px）",
                        rid=f"req-a04-{ver}-preview", dsl_version=ver,
                        kind="render")
        print("HTTP", rec["http_status"], "bytes", rec["response_bytes"],
              "ct", rec["content_type"])
        if rec.get("error_summary"):
            print("ERROR", rec["error_summary"])
        else:
            prev = TMP / "preview" / f"{ver}.png"
            prev.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(TMP / "responses" / f"{rec['request_id']}.body", prev)
            print("preview →", prev.relative_to(IO.ROOT))
    else:
        # 正式版：落 outputs/ 并保留同名 .snapshot
        rec = IO.submit(DSL, label="A04 转化悖论信息图 正式版", rid="req-a04-final",
                        kind="render", out_png="conversion-story.png",
                        out_dsl="conversion-story.snapshot")
        print("HTTP", rec["http_status"], "bytes", rec["response_bytes"],
              "ct", rec["content_type"])
        if rec.get("error_summary"):
            print("ERROR", rec["error_summary"])
        else:
            print("output →", (OUT / "conversion-story.png").relative_to(IO.ROOT))
            print("dsl    →",
                  (OUT / "conversion-story.snapshot").relative_to(IO.ROOT))
