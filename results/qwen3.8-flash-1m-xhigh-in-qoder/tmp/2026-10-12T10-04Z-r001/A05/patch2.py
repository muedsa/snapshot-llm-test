"""A05 second pass: raise summary text to 20px (body floor), retune the vertical
budget, fix the clipped gutter label, and add the negative band to the legend."""
import pathlib

p = pathlib.Path("tmp/2026-10-12T10-04Z-r001/A05/gen2.py")
s = p.read_text(encoding="utf-8")

rep = [
    ("SUM_Y, SUM_H = 116, 118\nPAN_Y, PAN_H, PAN_GAP = 244, 150, 10",
     "SUM_Y, SUM_H = 116, 146\nPAN_Y, PAN_H, PAN_GAP = 270, 142, 8"),
    ("XAX_Y = PAN_Y + 3 * PAN_H + 2 * PAN_GAP          # 706",
     "XAX_Y = PAN_Y + 3 * PAN_H + 2 * PAN_GAP          # 712"),
    ("TBL_Y, TBL_H = 776, 168\nFOOT_Y = 950", "TBL_Y, TBL_H = 774, 168\nFOOT_Y = 950"),
    ("PLOT_TOP_OFF, PLOT_BOT_OFF = 52, 136", "PLOT_TOP_OFF, PLOT_BOT_OFF = 50, 128"),
    # summary body lines at 20px, one fact per line
    ('''            Container(height="12"),
            Text(f"最小 {st['min']['value']:g} {unit}（{st['min']['time']}）｜ "
                 f"最大 {st['max']['value']:g} {unit}（{st['max']['time']}）",
                 color=TXT_2, fontSize="18", fontFamily=FONT),
            Container(height="6"),
            Text(f"缺测时点：{miss}", color=TXT_3, fontSize="18", fontFamily=FONT),''',
     '''            Container(height="12"),
            Text(f"最小 {st['min']['value']:g} {unit}（{st['min']['time']}）",
                 color=TXT_2, fontSize="20", fontFamily=FONT),
            Container(height="4"),
            Text(f"最大 {st['max']['value']:g} {unit}（{st['max']['time']}）",
                 color=TXT_2, fontSize="20", fontFamily=FONT),
            Container(height="4"),
            Text(f"缺测时点：{miss}", color=TXT_3, fontSize="20", fontFamily=FONT),'''),
    # clipped gutter label
    ('els.append(label(PAD, XAX_Y + 36, "粗刻度=整点", 18, TXT_3, anchor="left_top",\n                 align="LEFT", width=LBL_W - 22, font=FONT))',
     'els.append(label(PAD, XAX_Y + 36, "整点线", 18, TXT_3, anchor="left_top",\n                 align="LEFT", width=LBL_W - 22, font=FONT))'),
    # legend gains the negative-band swatch
    ('''        Row(C(width="24", height="3", color=NEG), Container(width="8"),
            Text("缺测处线断开", color=TXT_2, fontSize="18", fontFamily=FONT),
            Container(width="16"),
            C(width="12", height="12", color="#0B1220", borderRadius="6",
              border=f"2 SOLID {NEG}"),
            Container(width="6"),
            Text("缺测时点", color=TXT_2, fontSize="18", fontFamily=FONT),
            crossAxisAlignment="CENTER"),''',
     '''        Row(C(width="24", height="3", color=NEG), Container(width="8"),
            Text("缺测断开", color=TXT_2, fontSize="18", fontFamily=FONT),
            Container(width="14"),
            C(width="12", height="12", color="#0B1220", borderRadius="6",
              border=f"2 SOLID {NEG}"),
            Container(width="6"),
            Text("缺测", color=TXT_2, fontSize="18", fontFamily=FONT),
            Container(width="14"),
            C(width="16", height="14", color="#FB71851A", borderRadius="3",
              border=f"1 SOLID {NEG}55"),
            Container(width="6"),
            Text("负值跨度带", color=TXT_2, fontSize="18", fontFamily=FONT),
            crossAxisAlignment="CENTER"),'''),
]

for a, b in rep:
    if a not in s:
        raise SystemExit("MISS: " + a[:90])
    s = s.replace(a, b)

p.write_text(s, encoding="utf-8")
print("patched", len(rep), "sites")
