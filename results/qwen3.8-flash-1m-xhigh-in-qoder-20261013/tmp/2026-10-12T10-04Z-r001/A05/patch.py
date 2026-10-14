"""A05 fixes: data-x inset, clamped value labels, summary single line,
axis label row removal, table label width, corrected alignment caption, one-line footer."""
import pathlib

p = pathlib.Path("tmp/2026-10-12T10-04Z-r001/A05/gen2.py")
s = p.read_text(encoding="utf-8")

rep = [
    # ---- inset the data x-range so edge markers/labels clear the gutter
    ("PX0 = PAD + LBL_W                    # 144\nPX1 = W - PAD                        # 1408\nPW = PX1 - PX0                       # 1264",
     "PX0 = PAD + LBL_W                    # 144\nPX1 = W - PAD                        # 1408\nPW = PX1 - PX0                       # 1264\nDX0, DX1 = PX0 + 24, PX1 - 24          # data markers keep clear of the axis ends"),
    ("def x_of(minute):\n    return PX0 + (minute - T0) * PPM",
     "PPM = (DX1 - DX0) / SPAN\n\n\ndef x_of(minute):\n    return DX0 + (minute - T0) * PPM"),
    ('"axis_x0_px": PX0, "axis_x1_px": PX1,',
     '"axis_x0_px": PX0, "axis_x1_px": PX1, "data_x0_px": DX0, "data_x1_px": DX1,'),
    ('"mapping": "x = 144 + (minute_of_day - 480) × 4.6815；横轴为真实时间线性比例"},',
     '"mapping": "x = 168 + (minute_of_day - 480) × 4.5037；横轴为真实时间线性比例，'
     '数据点左右各留 24px 以便边缘标记与数值标签完整显示"},'),
    # ---- vertical budget
    ("SUM_Y, SUM_H = 116, 110\nPAN_Y, PAN_H, PAN_GAP = 236, 150, 10",
     "SUM_Y, SUM_H = 116, 118\nPAN_Y, PAN_H, PAN_GAP = 244, 150, 10"),
    ("TBL_Y, TBL_H = 768, 170\nFOOT_Y = 946", "TBL_Y, TBL_H = 776, 168\nFOOT_Y = 950"),
    ("PLOT_TOP_OFF, PLOT_BOT_OFF = 42, 134", "PLOT_TOP_OFF, PLOT_BOT_OFF = 52, 136"),
    # ---- summary: min and max on one line
    ('''            Container(height="10"),
            Text(f"最小 {st['min']['value']:g} {unit}（{st['min']['time']}）",
                 color=TXT_2, fontSize="18", fontFamily=FONT),
            Container(height="4"),
            Text(f"最大 {st['max']['value']:g} {unit}（{st['max']['time']}）",
                 color=TXT_2, fontSize="18", fontFamily=FONT),
            Container(height="4"),
            Text(f"缺测时点：{miss}", color=TXT_3, fontSize="18", fontFamily=FONT),''',
     '''            Container(height="12"),
            Text(f"最小 {st['min']['value']:g} {unit}（{st['min']['time']}）｜ "
                 f"最大 {st['max']['value']:g} {unit}（{st['max']['time']}）",
                 color=TXT_2, fontSize="18", fontFamily=FONT),
            Container(height="6"),
            Text(f"缺测时点：{miss}", color=TXT_3, fontSize="18", fontFamily=FONT),'''),
    # ---- value labels: never rise into the panel title band
    ('''        y = y_of(r[key])
        els.append(dot(x, y, 13, "#0B1220"))
        els.append(dot(x, y, 8, col))
        off = -8 if i % 2 == 0 else -28
        els.append(label(x, y + off, f"{r[key]:g}", 18, "#E4EEFA", anchor="bottom",
                         align="CENTER", width=48, font=MONO))''',
     '''        y = y_of(r[key])
        els.append(dot(x, y, 13, "#0B1220"))
        els.append(dot(x, y, 8, col))
        # two label levels, and any label that would reach the title band goes below
        want_above = (y - (28 if i % 2 else 8)) >= py + 44
        if want_above:
            els.append(label(x, y + (-8 if i % 2 == 0 else -28), f"{r[key]:g}", 18,
                             "#E4EEFA", anchor="bottom", align="CENTER", width=52,
                             font=MONO))
        else:
            els.append(label(x, y + 12, f"{r[key]:g}", 18, "#E4EEFA", anchor="top",
                             align="CENTER", width=52, font=MONO))'''),
    # ---- drop the colliding hour-label row, keep the hour gridlines
    ('''for hm in (9 * 60, 10 * 60, 11 * 60, 12 * 60):
    els.append(vline(x_of(hm), XAX_Y, XAX_Y + 14, 2, "#2A3C5E"))
els.append(label(PAD, XAX_Y + 10, "采样时点", 18, TXT_3, anchor="left_top", align="LEFT",
                 width=LBL_W - 22, font=FONT))
els.append(label(PAD, XAX_Y + 44, "整点参考线", 18, TXT_3, anchor="left_top", align="LEFT",
                 width=LBL_W - 22, font=FONT))
for hm in (9 * 60, 10 * 60, 11 * 60, 12 * 60):
    els.append(label(x_of(hm), XAX_Y + 52, f"{hm//60:02d}:00", 18, TXT_3, anchor="top",
                     align="CENTER", width=80, font=MONO))''',
     '''for hm in (9 * 60, 10 * 60, 11 * 60, 12 * 60):
    els.append(vline(x_of(hm), XAX_Y, XAX_Y + 16, 3, "#44608C"))
els.append(label(PAD, XAX_Y + 10, "采样时点", 18, TXT_3, anchor="left_top", align="LEFT",
                 width=LBL_W - 22, font=FONT))
els.append(label(PAD, XAX_Y + 36, "粗刻度=整点", 18, TXT_3, anchor="left_top",
                 align="LEFT", width=LBL_W - 22, font=FONT))'''),
    # ---- table caption: state the real relationship
    ('''        Text("“—” 表示缺测（不是 0）；列中心与上方三图同一时刻的采样标记逐列对齐",
             color=TXT_3, fontSize="18", fontFamily=FONT),''',
     '''        Text("“—” 表示缺测（不是 0）；12 个时点按时间顺序等宽列出"
             "（横轴为真实时间比例，故表列位置不等同于图中横坐标）",
             color=TXT_3, fontSize="18", fontFamily=FONT),'''),
    ('els.append(label(PAD + 22, THEAD_Y + 13, "时点", 18, TXT_2, anchor="left", align="LEFT",\n                 width=LBL_W - 40, font=FONT))',
     'els.append(label(PAD + 22, THEAD_Y + 13, "时点", 18, TXT_2, anchor="left", align="LEFT",\n                 width=LBL_W - 26, font=FONT))'),
    ('    els.append(label(PAD + 22, ry + ROWH / 2, f"{lab} {unit}", 18, col, anchor="left",\n                     align="LEFT", width=LBL_W - 40, font=FONT, bold=True))',
     '    els.append(label(PAD + 22, ry + ROWH / 2, f"{lab} {unit}", 18, col, anchor="left",\n                     align="LEFT", width=LBL_W - 26, font=FONT, bold=True))'),
    # ---- footer single line
    ('''                 "连线只在相邻的有采样时点之间绘制，任一时点缺测则该点前后线段各自断开，"
                 "不以直线或虚线补值；压差 0 表示与参考压相等，正负均有实际读数。",
                 18, TXT_3, anchor="left_top", align="LEFT", width=1150, font=FONT))''',
     '''                 "连线只画在相邻有采样时点之间，缺测处前后线段各自断开，不以直线或虚线补值。",
                 18, TXT_3, anchor="left_top", align="LEFT", width=900, font=FONT))'''),
]

for a, b in rep:
    if a not in s:
        raise SystemExit("MISS: " + a[:90])
    s = s.replace(a, b)

# PPM is now derived from the data range; drop the earlier definition
s = s.replace("SPAN = T1 - T0                       # 270\nPPM = PW / SPAN",
              "SPAN = T1 - T0                       # 270")
p.write_text(s, encoding="utf-8")
print("patched", len(rep), "sites")
