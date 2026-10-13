"""One-off layout patch for the A04 generator (kept as process evidence)."""
import pathlib

p = pathlib.Path("tmp/2026-10-12T10-04Z-r001/A04/gen.py")
s = p.read_text(encoding="utf-8")

rep = [
    ("TBL_W = 1000\nFML_W = CW - TBL_W - GAP             # 498",
     "TBL_W = 1024\nFML_W = CW - TBL_W - GAP             # 474"),
    ("AX_H = 200\nAX_TOP_OFF = 76", "AX_H = 210\nAX_TOP_OFF = 64"),
    ('''            Text("数据源 inputs/conversion.csv · 期名沿用输入：前期 / 后期 · "
                 "计数单位：访问数（次）/ 成交数（笔）· 比率 = 成交 ÷ 访问",
                 color=TXT_2, fontSize="20", fontFamily=FONT),''',
     '''            Text("数据源 inputs/conversion.csv · 前期 vs 后期 · 比率 = 成交 ÷ 访问",
                 color=TXT_2, fontSize="20", fontFamily=FONT),'''),
    ("right=num(PAD), top=num(HDR_Y + 6)))", "right=num(PAD), top=num(HDR_Y + 2)))"),
    ('''def panel_head(x, y, w, title, sub):
    return [Positioned(
        Col(Text(title, color=TXT, fontSize="24", fontStyle="BOLD", fontFamily=FONT),
            Container(height="6"),
            Text(sub, color=TXT_3, fontSize="18", fontFamily=FONT),
            crossAxisAlignment="START"),
        left=num(x), top=num(y), width=num(w))]''',
     '''def panel_head(x, y, w, title, sub):
    """Title and unit note on one line so they cannot collide with the top gridline."""
    return [Positioned(
        Row(Text(title, color=TXT, fontSize="24", fontStyle="BOLD", fontFamily=FONT),
            Container(width="12"),
            Text(sub, color=TXT_3, fontSize="18", fontFamily=FONT),
            crossAxisAlignment="END", mainAxisSize="MIN"),
        left=num(x), top=num(y + 4), width=num(w))]'''),
    ('els += panel_head(PAD + 22, ROW1_Y + 14, P1_W - 200, "① 分组转化率",\n'
     '                  "同一 0–100% 尺度 · 单位 %")',
     'els += panel_head(PAD + 22, ROW1_Y + 14, P1_W - 210, "① 分组转化率", "0–100% 尺度")'),
    ('els += panel_head(P2X + 22, ROW1_Y + 14, P2_W - 44, "② 总体转化率", "成交总数 ÷ 访问总数")',
     'els += panel_head(P2X + 22, ROW1_Y + 14, P2_W - 44, "② 总体转化率", "成交÷访问")'),
    ('els += panel_head(r3x, ROW1_Y + 14, BAR_W, "③ 两期访问构成", "每期等长 · 分段按真实占比")',
     'els += panel_head(r3x, ROW1_Y + 14, BAR_W, "③ 两期访问构成", "每期等长")'),
    ("    by = ROW1_Y + 68 + bi * 116", "    by = ROW1_Y + 62 + bi * 124"),
    ('''GRP_W = (TBL_W - 44 - 40) / 2         # 478
COLS = [("渠道", 112, "LEFT"), ("访问数", 82, "RIGHT"), ("成交数", 82, "RIGHT"),
        ("分子/分母", 112, "RIGHT"), ("转化率", 70, "RIGHT")]''',
     '''GRP_W = (TBL_W - 44 - 40) / 2         # 470
COLS = [("渠道", 130, "LEFT"), ("访问数", 110, "RIGHT"), ("成交数", 110, "RIGHT"),
        ("转化率", 120, "RIGHT")]'''),
    ("TROW_H = 27\nTHEAD_Y = ROW2_Y + 46", "TROW_H = 28\nTHEAD_Y = ROW2_Y + 44"),
    ('''    rows = [(ch, f"{D[(p,ch)]['visits']:,}", f"{D[(p,ch)]['conversions']:,}",
             f"{D[(p,ch)]['conversions']}/{D[(p,ch)]['visits']}", pc(rate(p, ch)))
            for ch in CHANNELS]
    rows.append(("合计", f"{tot[p]['visits']:,}", f"{tot[p]['conversions']:,}",
                 f"{tot[p]['conversions']}/{tot[p]['visits']}", pc(overall(p))))''',
     '''    rows = [(ch, f"{D[(p,ch)]['visits']:,}", f"{D[(p,ch)]['conversions']:,}",
             pc(rate(p, ch))) for ch in CHANNELS]
    rows.append(("合计", f"{tot[p]['visits']:,}", f"{tot[p]['conversions']:,}",
                 pc(overall(p))))'''),
    ('''    els.append(label(gx, THEAD_Y - 20, p, 20, TXT_3, anchor="left_top", align="LEFT",
                     width=120, font=FONT, bold=True))''',
     '''    els.append(label(gx + 130, THEAD_Y + 24, p, 18, P2C, anchor="left_bottom",
                     align="LEFT", width=120, font=FONT, bold=True))'''),
    ('els.append(label(px, THEAD_Y + 11, name, 18, TXT_2,',
     'els.append(label(px, THEAD_Y + 14, name, 18, TXT_2,'),
    ('''            colr = TXT if al == "LEFT" else TXT_2
            if is_total:
                colr = P2C if val.endswith("%") else TXT
            els.append(label(px, ry + TROW_H / 2, val, 22 if not is_total else 22,
                             colr, anchor="left" if al == "LEFT" else "right", align=al,
                             width=cw0 - 12, font=FONT_MONO if cx0 != cols[0][0] else FONT,
                             bold=is_total, line_height=1.05))''',
     '''            colr = TXT if al == "LEFT" else TXT_2
            if is_total:
                colr = P2C if val.endswith("%") else TXT
            els.append(label(px, ry + TROW_H / 2, val, 22, colr,
                             anchor="left" if al == "LEFT" else "right", align=al,
                             width=cw0 - 12,
                             font=FONT_MONO if cx0 != cols[0][0] else FONT,
                             bold=is_total, line_height=1.0))'''),
    ('        Text("分母=访问数，分子=成交数，均可与①②③对照", color=TXT_3, fontSize="18",\n'
     '             fontFamily=FONT),',
     '        Text("每行的访问数即分母、成交数即分子，可与①②③逐格对照", color=TXT_3,\n'
     '             fontSize="18", fontFamily=FONT),'),
    ('''        Container(height="10"),
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
             textAlign="LEFT", softWrap="true", height="1.25"),''',
     '''        Container(height="8"),
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
             textAlign="LEFT", softWrap="true", height="1.2"),'''),
    ('''                 "①②共用同一 0–100% 尺度与刻度位置；③每期条长相等、分段按真实访问占比；"
                 "④提供全部原始分子分母；⑤给出加权与错误算法的对照。",''',
     '''                 "①②共用同一 0–100% 尺度与刻度；③每期条长相等、分段按真实占比；⑤为加权与错误算法对照。"
                 "期名沿用输入（前期/后期），访问数与成交数为原始计数，单位记作 次 / 笔。",'''),
]

for a, b in rep:
    if a not in s:
        raise SystemExit("MISS: " + a[:80])
    s = s.replace(a, b)

p.write_text(s, encoding="utf-8")
print("patched", len(rep), "sites")
