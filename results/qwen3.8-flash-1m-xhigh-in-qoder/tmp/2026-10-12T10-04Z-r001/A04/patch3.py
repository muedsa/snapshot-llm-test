"""Third A04 patch: widen the formula panel, shorten its lines, tighten ② labels."""
import pathlib

p = pathlib.Path("tmp/2026-10-12T10-04Z-r001/A04/gen.py")
s = p.read_text(encoding="utf-8")

rep = [
    ("TBL_W = 1024\nFML_W = CW - TBL_W - GAP             # 474",
     "TBL_W = 990\nFML_W = CW - TBL_W - GAP             # 508"),
    ('''COLS = [("渠道", 140, "LEFT"), ("访问数", 110, "RIGHT"), ("成交数", 110, "RIGHT"),
        ("转化率", 110, "RIGHT")]''',
     '''COLS = [("渠道", 130, "LEFT"), ("访问数", 105, "RIGHT"), ("成交数", 105, "RIGHT"),
        ("转化率", 113, "RIGHT")]'''),
    ('''        Container(height="8"),
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
             fontFamily=FONT),''',
     '''        Container(height="6"),
        Text("正确  2600÷10000 = 26.00%（前期）", color=EMERALD, fontSize="18",
             fontFamily=FONT),
        Container(height="6"),
        Text("正确  1660÷10000 = 16.60%（后期）", color=EMERALD, fontSize="18",
             fontFamily=FONT),
        Container(height="6"),
        Text("错误  等权平均 20.00% → 23.50%，误判 +3.50 pp", color=ROSE, fontSize="18",
             fontFamily=FONT),
        Container(height="6"),
        Text("错误  成交数 200→960 是规模；分母差 4 倍不能等权", color=ROSE,
             fontSize="18", fontFamily=FONT),'''),
    ('''        Text("⑤ 加权算法 vs 错误算法", color=TXT, fontSize="22", fontStyle="BOLD",
             fontFamily=FONT),''',
     '''        Text("⑤ 加权算法 vs 错误算法", color=TXT, fontSize="22", fontStyle="BOLD",
             fontFamily=FONT),'''),
    ('''    els.append(label(bx + bw / 2, ROW1_Y + DELTA_OFF,
                     f"{tot[p]['conversions']:,} ÷ {tot[p]['visits']:,}", 18, TXT_3,
                     anchor="top", align="CENTER", width=bw + 44, font=FONT_MONO))''',
     '''    els.append(label(bx + bw / 2, ROW1_Y + DELTA_OFF,
                     f"{tot[p]['conversions']:,} ÷ {tot[p]['visits']:,}", 18, TXT_3,
                     anchor="top", align="CENTER", width=bw + 28, font=FONT_MONO))'''),
]

for a, b in rep:
    if a not in s:
        raise SystemExit("MISS: " + a[:80])
    s = s.replace(a, b)

p.write_text(s, encoding="utf-8")
print("patched", len(rep), "sites")
