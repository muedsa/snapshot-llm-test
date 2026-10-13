"""Second layout patch for the A04 generator: header clipping, table header
collision, formula panel overflow, footer wrap, and the shared-scale offsets."""
import pathlib

p = pathlib.Path("tmp/2026-10-12T10-04Z-r001/A04/gen.py")
s = p.read_text(encoding="utf-8")

rep = [
    # ---- vertical budget
    ("HDR_Y, HDR_H = 36, 68\nROW1_Y, ROW1_H = 114, 404\nROW2_Y, ROW2_H = 528, 170\n"
     "ROW3_Y, ROW3_H = 708, 236\nFOOT_Y = 948",
     "HDR_Y, HDR_H = 32, 80\nROW1_Y, ROW1_H = 120, 382\nROW2_Y, ROW2_H = 512, 182\n"
     "ROW3_Y, ROW3_H = 704, 240\nFOOT_Y = 950"),
    # ---- shared scale offsets
    ("AX_H = 210\nAX_TOP_OFF = 64", "AX_H = 204\nAX_TOP_OFF = 64"),
    ("GRP_OFF = AX_BASE_OFF + 10", "GRP_OFF = AX_BASE_OFF + 10"),
    ("DELTA_OFF = GRP_OFF + 28             # 314", "DELTA_OFF = GRP_OFF + 28"),
    ("NOTE_OFF = DELTA_OFF + 30            # 344", "NOTE_OFF = DELTA_OFF + 30"),
    # ---- header: single short subtitle line, units folded in
    ('''            Text("数据源 inputs/conversion.csv · 前期 vs 后期 · 比率 = 成交 ÷ 访问",
                 color=TXT_2, fontSize="20", fontFamily=FONT),''',
     '''            Text("数据源 inputs/conversion.csv · 前期 / 后期（沿用输入）· "
                 "比率 = 成交 ÷ 访问", color=TXT_2, fontSize="20", fontFamily=FONT),'''),
    ('Text("总体转化率（成交总数 ÷ 访问总数）", color=TXT_3, fontSize="18",',
     'Text("总体转化率 = 成交总数 ÷ 访问总数", color=TXT_3, fontSize="18",'),
    ("right=num(PAD), top=num(HDR_Y + 2)))", "right=num(PAD), top=num(HDR_Y)))"),
    # ---- table: period folded into the first header cell, widths rebalanced
    ('''GRP_W = (TBL_W - 44 - 40) / 2         # 470
COLS = [("渠道", 130, "LEFT"), ("访问数", 110, "RIGHT"), ("成交数", 110, "RIGHT"),
        ("转化率", 120, "RIGHT")]''',
     '''GRP_W = (TBL_W - 44 - 40) / 2         # 470
COLS = [("渠道", 140, "LEFT"), ("访问数", 110, "RIGHT"), ("成交数", 110, "RIGHT"),
        ("转化率", 110, "RIGHT")]'''),
    ('''    for (cx0, cw0, al), (name, _w, _a) in zip(cols, COLS):
        px = cx0 + 6 if al == "LEFT" else cx0 + cw0 - 6
        els.append(label(px, THEAD_Y + 14, name, 18, TXT_2,
                         anchor="left" if al == "LEFT" else "right", align=al,
                         width=cw0 - 12, font=FONT))''',
     '''    for (cx0, cw0, al), (name, _w, _a) in zip(cols, COLS):
        px = cx0 + 6 if al == "LEFT" else cx0 + cw0 - 6
        shown = f"{p} · {name}" if al == "LEFT" else name
        els.append(label(px, THEAD_Y + 14, shown, 18, P2C if al == "LEFT" else TXT_2,
                         anchor="left" if al == "LEFT" else "right", align=al,
                         width=cw0 - 12, font=FONT, bold=(al == "LEFT")))'''),
    ('''    els.append(label(gx + 130, THEAD_Y + 24, p, 18, P2C, anchor="left_bottom",
                     align="LEFT", width=120, font=FONT, bold=True))''', ""),
    # ---- formula panel: four one-line rows + note
    ('''        Container(height="8"),
        Text("正确 前期 2600 ÷ 10000 = 26.00%", color=EMERALD, fontSize="18",
             fontFamily=FONT),
        Container(height="4"),
        Text("正确 后期 1660 ÷ 10000 = 16.60%", color=EMERALD, fontSize="18",
             fontFamily=FONT),
        Container(height="8"),
        Text("错误 (30+10)÷2=20.00% → (35+12)÷2=23.50%", color=ROSE, fontSize="18",
             fontFamily=FONT),
        Container(height="4"),
        Text("等权平均会误判为上升 +3.50 pp：两渠道分母相差 4 倍，"
             "绝对成交量也不等于转化率。", color=TXT_2, fontSize="18", fontFamily=FONT,
             textAlign="LEFT", softWrap="true", height="1.2"),''',
     '''        Container(height="8"),
        Text("正确 前期 2600÷10000=26.00% ｜ 后期 1660÷10000=16.60%",
             color=EMERALD, fontSize="18", fontFamily=FONT),
        Container(height="8"),
        Text("错误 等权 (30+10)÷2=20.00% → (35+12)÷2=23.50%（误判 +3.50 pp）",
             color=ROSE, fontSize="18", fontFamily=FONT),
        Container(height="8"),
        Text("错误 推广成交数 200→960 是流量规模，不是转化率", color=ROSE, fontSize="18",
             fontFamily=FONT),
        Container(height="8"),
        Text("两渠道分母相差 4 倍，不能等权平均。", color=TXT_2, fontSize="18",
             fontFamily=FONT),'''),
    # ---- footer: one short line
    ('''                 "①②共用同一 0–100% 尺度与刻度；③每期条长相等、分段按真实占比；⑤为加权与错误算法对照。"
                 "期名沿用输入（前期/后期），访问数与成交数为原始计数，单位记作 次 / 笔。",
                 18, TXT_3, anchor="left_top", align="LEFT", width=1150, font=FONT))''',
     '''                 "单位：访问数与成交数为原始计数（次 / 笔）；①②共用 0–100% 尺度；③每期条长相等。",
                 18, TXT_3, anchor="left_top", align="LEFT", width=1000, font=FONT))'''),
    ("els.append(label(W - PAD, FOOT_Y, f\"run {RUN}\", 18, \"#42536E\", anchor=\"right_top\",\n                 align=\"RIGHT\", width=340, font=FONT))",
     "els.append(label(W - PAD, FOOT_Y, f\"run {RUN}\", 18, \"#42536E\", anchor=\"right_top\",\n                 align=\"RIGHT\", width=300, font=FONT))"),
]

for a, b in rep:
    if a not in s:
        raise SystemExit("MISS: " + a[:80])
    s = s.replace(a, b)

p.write_text(s, encoding="utf-8")
print("patched", len(rep), "sites")
