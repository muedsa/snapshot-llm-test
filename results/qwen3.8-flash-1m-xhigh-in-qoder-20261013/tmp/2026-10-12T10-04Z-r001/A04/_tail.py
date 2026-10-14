# ---------------------------------------------------------------- geometry
W, H = 1600, 1000
PAD = 36
CW = W - 2 * PAD                     # 1528
GAP = 30

HDR_Y, HDR_H = 36, 68
ROW1_Y, ROW1_H = 114, 404
ROW2_Y, ROW2_H = 528, 170
ROW3_Y, ROW3_H = 708, 236
FOOT_Y = 948

P1_W = 610
P2_W = 380
P3_W = CW - P1_W - P2_W - 2 * GAP    # 478
TBL_W = 1000
FML_W = CW - TBL_W - GAP             # 498
CONC_W = 940
LIM_W = CW - CONC_W - GAP            # 558

# shared rate scale (0-100%) used by panels 1 and 2
AX_H = 200
AX_TOP_OFF = 76
AX_BASE_OFF = AX_TOP_OFF + AX_H      # 276
SCALE = AX_H / 100.0
GRP_OFF = AX_BASE_OFF + 10           # 286
DELTA_OFF = GRP_OFF + 28             # 314
NOTE_OFF = DELTA_OFF + 30            # 344

assert ROW1_Y + NOTE_OFF + 40 <= ROW1_Y + ROW1_H
assert FOOT_Y + 24 <= H


def layer(*children, w=W, h=H):
    return Stack(C(width=num(w), height=num(h)), *children,
                 alignment="TOP_LEFT", clipBehavior="HARD_EDGE")


def card(x, y, w, h, *, fill=CARD, radius=16, border=EDGE):
    return Positioned(C(width=num(w), height=num(h), color=fill, borderRadius=num(radius),
                        border=f"1 SOLID {border}"), left=num(x), top=num(y))


def rate_axis(px0, py, w, ticks=(0, 20, 40, 60, 80, 100)):
    """Gridlines + labels for the shared 0-100% scale; py is the plot top."""
    base = py + AX_H
    out = []
    for t in ticks:
        y = base - t * SCALE
        out.append(hline(px0, px0 + w, y, 2 if t == 0 else 1,
                         "#3A4C73" if t == 0 else "#1B2A47"))
        out.append(label(px0 - 12, y, f"{t}", 18, TXT_3, anchor="right", align="RIGHT",
                         width=40, font=FONT_MONO))
    out.append(vline(px0, py - 4, base, 2, "#3A4C73"))
    return out


def panel_head(x, y, w, title, sub):
    return [Positioned(
        Col(Text(title, color=TXT, fontSize="24", fontStyle="BOLD", fontFamily=FONT),
            Container(height="6"),
            Text(sub, color=TXT_3, fontSize="18", fontFamily=FONT),
            crossAxisAlignment="START"),
        left=num(x), top=num(y), width=num(w))]


els = []

# ---------------- header
els.append(Positioned(
    Row(C(width="6", height="58", color=P2C, borderRadius="3"), Container(width="18"),
        Col(Text("转化变化，为什么不能只看平均？", color=TXT, fontSize="36",
                 fontStyle="BOLD", fontFamily=FONT),
            Container(height="8"),
            Text("数据源 inputs/conversion.csv · 期名沿用输入：前期 / 后期 · "
                 "计数单位：访问数（次）/ 成交数（笔）· 比率 = 成交 ÷ 访问",
                 color=TXT_2, fontSize="20", fontFamily=FONT),
            crossAxisAlignment="START"),
        crossAxisAlignment="CENTER"),
    left=num(PAD), top=num(HDR_Y)))
els.append(Positioned(
    Col(
        Text("总体转化率（成交总数 ÷ 访问总数）", color=TXT_3, fontSize="18",
             fontFamily=FONT, textAlign="RIGHT"),
        Container(height="4"),
        Row(Text(pc(overall("前期")), color=P1C, fontSize="32", fontStyle="BOLD",
                 fontFamily=FONT),
            Container(width="10"),
            Text("→", color=TXT_3, fontSize="28", fontFamily=FONT),
            Container(width="10"),
            Text(pc(overall("后期")), color=P2C, fontSize="32", fontStyle="BOLD",
                 fontFamily=FONT),
            Container(width="12"),
            Text(f"（{pp(overall('后期')-overall('前期'))}）", color=ROSE, fontSize="22",
                 fontFamily=FONT),
            crossAxisAlignment="CENTER"),
        crossAxisAlignment="END"),
    right=num(PAD), top=num(HDR_Y + 6)))

# ---------------- P1 grouped channel rates
els.append(card(PAD, ROW1_Y, P1_W, ROW1_H))
p1x = PAD + 58
els += panel_head(PAD + 22, ROW1_Y + 14, P1_W - 200, "① 分组转化率",
                  "同一 0–100% 尺度 · 单位 %")
els.append(Positioned(
    Row(C(width="16", height="16", color=P1C, borderRadius="4"), Container(width="8"),
        Text("前期", color=TXT_2, fontSize="18", fontFamily=FONT),
        Container(width="20"),
        C(width="16", height="16", color=P2C, borderRadius="4"), Container(width="8"),
        Text("后期", color=TXT_2, fontSize="18", fontFamily=FONT),
        crossAxisAlignment="CENTER"),
    right=num(W - (PAD + P1_W - 22)), top=num(ROW1_Y + 20)))
els += rate_axis(p1x, ROW1_Y + AX_TOP_OFF, P1_W - 58 - 22)
g_w = (P1_W - 58 - 22) / 2
for gi, ch in enumerate(CHANNELS):
    cx = p1x + g_w * (gi + 0.5)
    bw, bgap = 74, 12
    x0 = cx - (bw * 2 + bgap) / 2
    for bi, p in enumerate(PERIODS):
        v = float(rate(p, ch)) * 100
        hpx = v * SCALE
        col = P1C if bi == 0 else P2C
        els.append(Positioned(
            C(width=num(bw), height=num(hpx), color=col,
              gradientType="LINEAR", gradientColors=f"{col},{col}99", gradientStops="0,1",
              gradientBegin="TOP_CENTER", gradientEnd="BOTTOM_CENTER"),
            left=num(x0 + bi * (bw + bgap)), top=num(ROW1_Y + AX_BASE_OFF - hpx)))
        els.append(label(x0 + bi * (bw + bgap) + bw / 2, ROW1_Y + AX_BASE_OFF - hpx - 5,
                         pc(rate(p, ch)), 18, TXT if bi else TXT_2, anchor="bottom",
                         align="CENTER", width=bw + 22, font=FONT, bold=(bi == 1)))
    els.append(label(cx, ROW1_Y + GRP_OFF, ch, 22, TXT, anchor="top", align="CENTER",
                     width=g_w - 8, font=FONT, bold=True))
    els.append(label(cx, ROW1_Y + DELTA_OFF,
                     f"{pp(rate('后期', ch) - rate('前期', ch))} 上升", 18, EMERALD,
                     anchor="top", align="CENTER", width=g_w - 8, font=FONT))
els.append(label(PAD + 22, ROW1_Y + NOTE_OFF, "横轴：渠道分组；柱高按 0–100% 同一尺度",
                 18, TXT_3, anchor="left_top", align="LEFT", width=P1_W - 44, font=FONT))

# ---------------- P2 overall comparison, same scale
P2X = PAD + P1_W + GAP
els.append(card(P2X, ROW1_Y, P2_W, ROW1_H))
q2x = P2X + 58
els += panel_head(P2X + 22, ROW1_Y + 14, P2_W - 44, "② 总体转化率", "成交总数 ÷ 访问总数")
els += rate_axis(q2x, ROW1_Y + AX_TOP_OFF, P2_W - 58 - 22)
for bi, p in enumerate(PERIODS):
    v = float(overall(p)) * 100
    bw = 92
    bx = q2x + (P2_W - 58 - 22) * (bi + 0.5) / 2 - bw / 2
    hpx = v * SCALE
    col = P1C if bi == 0 else P2C
    els.append(Positioned(
        C(width=num(bw), height=num(hpx), color=col,
          gradientType="LINEAR", gradientColors=f"{col},{col}99", gradientStops="0,1",
          gradientBegin="TOP_CENTER", gradientEnd="BOTTOM_CENTER"),
        left=num(bx), top=num(ROW1_Y + AX_BASE_OFF - hpx)))
    els.append(label(bx + bw / 2, ROW1_Y + AX_BASE_OFF - hpx - 5, pc(overall(p)), 20, TXT,
                     anchor="bottom", align="CENTER", width=bw + 26, font=FONT, bold=True))
    els.append(label(bx + bw / 2, ROW1_Y + GRP_OFF, p, 22, TXT, anchor="top", align="CENTER",
                     width=bw + 30, font=FONT, bold=True))
    els.append(label(bx + bw / 2, ROW1_Y + DELTA_OFF,
                     f"{tot[p]['conversions']:,} ÷ {tot[p]['visits']:,}", 18, TXT_3,
                     anchor="top", align="CENTER", width=bw + 44, font=FONT_MONO))
els.append(Positioned(
    Border(
        Container(Text("①升 ②降：分组与总体反向", color="#FFE1A8", fontSize="18",
                       fontFamily=FONT, textAlign="CENTER"),
                  padding="(6,12)", color="#3B2E10", borderRadius="10"),
        border="1 SOLID #7A5B1D", borderRadius="12"),
    left=num(P2X + 22), top=num(ROW1_Y + NOTE_OFF)))

# ---------------- P3 visit composition
P3X = PAD + P1_W + P2_W + 2 * GAP
els.append(card(P3X, ROW1_Y, P3_W, ROW1_H))
r3x = P3X + 22
BAR_W = P3_W - 44
els += panel_head(r3x, ROW1_Y + 14, BAR_W, "③ 两期访问构成", "每期等长 · 分段按真实占比")
for bi, p in enumerate(PERIODS):
    by = ROW1_Y + 68 + bi * 116
    els.append(label(r3x, by, p, 22, TXT, anchor="left_top", align="LEFT", width=120,
                     font=FONT, bold=True))
    els.append(label(r3x + BAR_W, by + 3, f"{tot[p]['visits']:,} 次", 18, TXT_3,
                     anchor="right_top", align="RIGHT", width=180, font=FONT))
    acc = r3x
    for ch in CHANNELS:
        share = float(mix(p, ch))
        seg = BAR_W * share
        col = DIRECT if ch == "直接访问" else PROMO
        els.append(Positioned(
            C(width=num(seg), height="54", color=col,
              borderRadiusTopLeft="10" if ch == "直接访问" else None,
              borderRadiusBottomLeft="10" if ch == "直接访问" else None,
              borderRadiusTopRight="10" if ch == "推广访问" else None,
              borderRadiusBottomRight="10" if ch == "推广访问" else None),
            left=num(acc), top=num(by + 26)))
        els.append(label(acc + seg / 2, by + 32, pc(mix(p, ch), 0), 20, "#08111F",
                         anchor="center_top", align="CENTER", width=max(seg - 8, 62),
                         font=FONT, bold=True))
        els.append(label(acc + seg / 2, by + 54, ch, 18, "#0E1626CC", anchor="center_top",
                         align="CENTER", width=max(seg - 6, 62), font=FONT))
        acc += seg
    els.append(label(r3x, by + 84,
                     f"直接访问 {D[(p,'直接访问')]['visits']:,} 次 · "
                     f"推广访问 {D[(p,'推广访问')]['visits']:,} 次",
                     18, TXT_3, anchor="left_top", align="LEFT", width=BAR_W, font=FONT))
els.append(Positioned(
    Row(C(width="16", height="16", color=DIRECT, borderRadius="4"), Container(width="8"),
        Text("直接访问（高转化渠道）", color=TXT_2, fontSize="18", fontFamily=FONT),
        Container(width="18"),
        C(width="16", height="16", color=PROMO, borderRadius="4"), Container(width="8"),
        Text("推广访问", color=TXT_2, fontSize="18", fontFamily=FONT),
        crossAxisAlignment="CENTER"),
    left=num(r3x), top=num(ROW1_Y + NOTE_OFF)))

# ---------------- table (two period groups side by side)
els.append(card(PAD, ROW2_Y, TBL_W, ROW2_H))
tl = PAD + 22
els.append(Positioned(
    Row(Text("④ 原始数据核对", color=TXT, fontSize="22", fontStyle="BOLD", fontFamily=FONT),
        Container(width="14"),
        Text("分母=访问数，分子=成交数，均可与①②③对照", color=TXT_3, fontSize="18",
             fontFamily=FONT),
        crossAxisAlignment="END"),
    left=num(tl), top=num(ROW2_Y + 12)))
GRP_W = (TBL_W - 44 - 40) / 2         # 478
COLS = [("渠道", 116, "LEFT"), ("访问数", 86, "RIGHT"), ("成交数", 86, "RIGHT"),
        ("分子/分母", 116, "RIGHT"), ("转化率", 74, "RIGHT")]
assert sum(c[1] for c in COLS) == int(GRP_W), (sum(c[1] for c in COLS), GRP_W)
TROW_H = 27
THEAD_Y = ROW2_Y + 46
for gi, p in enumerate(PERIODS):
    gx = tl + gi * (GRP_W + 40)
    acc = gx
    cols = []
    for name, wd, al in COLS:
        cols.append((acc, wd, al))
        acc += wd
    els.append(Positioned(C(width=num(GRP_W), height="2", color="#33486F"),
                          left=num(gx), top=num(THEAD_Y + 23)))
    for (cx0, cw0, al), (name, _w, _a) in zip(cols, COLS):
        px = cx0 + 6 if al == "LEFT" else cx0 + cw0 - 6
        els.append(label(px, THEAD_Y + 11, name, 18, TXT_2,
                         anchor="left" if al == "LEFT" else "right", align=al,
                         width=cw0 - 12, font=FONT))
    rows = [(ch, f"{D[(p,ch)]['visits']:,}", f"{D[(p,ch)]['conversions']:,}",
             f"{D[(p,ch)]['conversions']}/{D[(p,ch)]['visits']}", pc(rate(p, ch)))
            for ch in CHANNELS]
    rows.append(("合计", f"{tot[p]['visits']:,}", f"{tot[p]['conversions']:,}",
                 f"{tot[p]['conversions']}/{tot[p]['visits']}", pc(overall(p))))
    for ri, row in enumerate(rows):
        ry = THEAD_Y + 27 + ri * TROW_H
        is_total = row[0] == "合计"
        if is_total:
            els.append(Positioned(C(width=num(GRP_W), height=num(TROW_H), color="#18294A",
                                    borderRadius="5"), left=num(gx), top=num(ry)))
        for (cx0, cw0, al), val in zip(cols, row):
            px = cx0 + 6 if al == "LEFT" else cx0 + cw0 - 6
            colr = TXT if al == "LEFT" else TXT_2
            if is_total:
                colr = P2C if val.endswith("%") else TXT
            els.append(label(px, ry + TROW_H / 2, val, 22 if not is_total else 22,
                             colr, anchor="left" if al == "LEFT" else "right", align=al,
                             width=cw0 - 12, font=FONT_MONO if cx0 != cols[0][0] else FONT,
                             bold=is_total, line_height=1.05))
    els.append(label(gx, THEAD_Y - 20, p, 20, TXT_3, anchor="left_top", align="LEFT",
                     width=120, font=FONT, bold=True))

# ---------------- formula panel
FX = PAD + TBL_W + GAP
els.append(card(FX, ROW2_Y, FML_W, ROW2_H, fill="#12203C"))
els.append(Positioned(
    Col(
        Text("⑤ 加权算法 vs 错误算法", color=TXT, fontSize="22", fontStyle="BOLD",
             fontFamily=FONT),
        Container(height="10"),
        Text("正确 前期 2600 ÷ 10000 = 26.00%", color=EMERALD, fontSize="18",
             fontFamily=FONT),
        Container(height="6"),
        Text("正确 后期 1660 ÷ 10000 = 16.60%", color=EMERALD, fontSize="18",
             fontFamily=FONT),
        Container(height="8"),
        Text("错误 (30%+10%)÷2 = 20.00% → (35%+12%)÷2 = 23.50%", color=ROSE, fontSize="18",
             fontFamily=FONT),
        Container(height="6"),
        Text("等权平均会误判为上升 +3.50 pp；两渠道访问数相差 4 倍，"
             "且绝对成交量不等于转化率。", color=TXT_2, fontSize="18", fontFamily=FONT,
             textAlign="LEFT", softWrap="true", height="1.25"),
        crossAxisAlignment="START"),
    left=num(FX + 22), top=num(ROW2_Y + 12), width=num(FML_W - 44)))

# ---------------- conclusion + limitation
els.append(card(PAD, ROW3_Y, CONC_W, ROW3_H, fill="#0F2140", border="#2E5080"))
els.append(Positioned(C(width=num(CONC_W - 2), height="4", color=P2C, borderRadius="2"),
                      left=num(PAD + 1), top=num(ROW3_Y + 1)))
els.append(Positioned(
    Col(
        Text("主结论（由数据支持）", color=P2C, fontSize="20", fontStyle="BOLD",
             fontFamily=FONT),
        Container(height="10"),
        Container(Text(CONCLUSION, color=TXT, fontSize="22", fontFamily=FONT,
                       textAlign="LEFT", softWrap="true", height="1.3"),
                  width=num(CONC_W - 44)),
        Container(height="12"),
        Container(Text(MECHANISM, color=TXT_2, fontSize="20", fontFamily=FONT,
                       textAlign="LEFT", softWrap="true", height="1.3"),
                  width=num(CONC_W - 44)),
        crossAxisAlignment="START"),
    left=num(PAD + 22), top=num(ROW3_Y + 16), width=num(CONC_W - 44)))
els.append(card(PAD + CONC_W + GAP, ROW3_Y, LIM_W, ROW3_H, fill="#241322", border="#5A2E45"))
els.append(Positioned(C(width=num(LIM_W - 2), height="4", color=ROSE, borderRadius="2"),
                      left=num(PAD + CONC_W + GAP + 1), top=num(ROW3_Y + 1)))
els.append(Positioned(
    Col(
        Text("限制说明：不能由该数据证明因果", color=ROSE, fontSize="20", fontStyle="BOLD",
             fontFamily=FONT),
        Container(height="10"),
        Container(Text(LIMIT, color="#EBD9E0", fontSize="19", fontFamily=FONT,
                       textAlign="LEFT", softWrap="true", height="1.32"),
                  width=num(LIM_W - 44)),
        crossAxisAlignment="START"),
    left=num(PAD + CONC_W + GAP + 22), top=num(ROW3_Y + 16), width=num(LIM_W - 44)))

els.append(label(PAD, FOOT_Y,
                 "①②共用同一 0–100% 尺度与刻度位置；③每期条长相等、分段按真实访问占比；"
                 "④提供全部原始分子分母；⑤给出加权与错误算法的对照。",
                 18, TXT_3, anchor="left_top", align="LEFT", width=1150, font=FONT))
els.append(label(W - PAD, FOOT_Y, f"run {RUN}", 18, "#42536E", anchor="right_top",
                 align="RIGHT", width=340, font=FONT))

doc = Snapshot(
    Container(layer(*els), width=num(W), height=num(H),
              gradientType="LINEAR", gradientColors=f"{BG},{BG2}", gradientStops="0,1",
              gradientBegin="TOP_CENTER", gradientEnd="BOTTOM_CENTER"),
    background=BG, type="png")

OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / "analysis.json").write_text(
    json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

ap = argparse.ArgumentParser()
ap.add_argument("--ver", default="v001")
ap.add_argument("--final", default=None)
a = ap.parse_args()
TMP_DIR.mkdir(parents=True, exist_ok=True)
(TMP_DIR / f"{a.ver}.snapshot").write_text(doc.render() + "\n", encoding="utf-8")
if a.final:
    (ROOT / a.final).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / a.final).write_text(doc.render() + "\n", encoding="utf-8")
print(json.dumps({"ver": a.ver, "overall": [pc(overall(p)) for p in PERIODS],
                  "rates": [pc(rate(p, c)) for p in PERIODS for c in CHANNELS],
                  "mix_only": pc(mix_only), "delta_mix_pp": str(float(delta_mix * 100)),
                  "delta_rate_pp": str(float(delta_rate * 100)),
                  "naive": [pc(naive[p]) for p in PERIODS],
                  "bottom_used": FOOT_Y + 24}, ensure_ascii=False))
