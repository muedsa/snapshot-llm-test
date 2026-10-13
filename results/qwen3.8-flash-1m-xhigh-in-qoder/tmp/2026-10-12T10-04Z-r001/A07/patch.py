"""A07 map fixes: compact single-line station labels with the × marker inline,
per-station offsets that avoid the polylines, a taller legend card, and a
single-line bottom route strip."""
import pathlib

p = pathlib.Path("tmp/2026-10-12T10-04Z-r001/A07/gen.py")
s = p.read_text(encoding="utf-8")

rep = [
    ('''LBL = {  # (dx, dy, anchor) place each station name clear of the lines
    "S01": (-14, 0, "right"), "S02": (0, -30, "center"), "S03": (0, -30, "center"),
    "S04": (-16, -34, "right"), "S05": (16, -34, "left"), "S06": (0, -30, "center"),
    "S12": (16, 0, "left"), "S07": (0, -30, "center"), "S08": (0, 34, "center"),
    "S09": (20, 0, "left"), "S10": (-20, 0, "right"), "S11": (0, 34, "center"),
    "S13": (0, -30, "center"), "S14": (-18, 0, "right"), "S15": (0, -30, "center"),
    "S16": (0, 34, "center"),
}''',
     '''# (dx, dy, anchor): every offset keeps the label off the polylines and off its
# neighbours; the accessibility mark is appended to the same line.
LBL = {
    "S01": (-18, 0, "right"), "S02": (0, -26, "above"), "S03": (0, -26, "above"),
    "S04": (0, -26, "above"), "S05": (0, -26, "above"), "S06": (0, -26, "above"),
    "S12": (0, -26, "above"), "S07": (0, -26, "above"), "S08": (0, 30, "below"),
    "S09": (-18, 0, "right"), "S10": (-18, 0, "right"), "S11": (18, 0, "left"),
    "S13": (0, -26, "above"), "S14": (0, -26, "above"), "S15": (0, -26, "above"),
    "S16": (0, 30, "below"),
}'''),
    ('''    dx, dy, anchor = LBL[sid]
    lx, ly = x + dx, y + dy
    if anchor == "center":
        anchor_v = "bottom" if dy < 0 else "top"
        mapels.append(label(lx, ly, f"{sid} {NAME[sid]}", 20, TXT, anchor=anchor_v,
                            align="CENTER", width=150, font=FONT, bold=True))
    else:
        mapels.append(label(lx, ly, f"{sid} {NAME[sid]}", 20, TXT,
                            anchor="left" if anchor == "left" else "right",
                            align="LEFT" if anchor == "left" else "RIGHT", width=160,
                            font=FONT, bold=True))
    if not ACC[sid]:
        mapels.append(label(lx + (0 if anchor == "center" else (-8 if anchor == "right" else 8)),
                            ly + (26 if dy < 0 else (-26 if anchor == "center" else 0)),
                            "× 不具备无障碍设施", 18, AMBER,
                            anchor="bottom" if dy < 0 else "top",
                            align="CENTER" if anchor == "center" else
                                 ("LEFT" if anchor == "left" else "RIGHT"),
                            width=190, font=FONT))''',
     '''    dx, dy, anchor = LBL[sid]
    lx, ly = x + dx, y + dy
    txt = f"{sid} {NAME[sid]}" + ("" if ACC[sid] else "  ×")
    if anchor in ("above", "below"):
        mapels.append(label(lx, ly, txt, 20, TXT,
                            anchor="center_bottom" if anchor == "above" else "center_top",
                            align="CENTER", width=170, font=FONT, bold=True))
    elif anchor == "left":
        mapels.append(label(lx, ly, txt, 20, TXT, anchor="left", align="LEFT",
                            width=170, font=FONT, bold=True))
    else:
        mapels.append(label(lx, ly, txt, 20, TXT, anchor="right", align="RIGHT",
                            width=170, font=FONT, bold=True))'''),
    ("LEG_X, LEG_Y, LEG_W, LEG_H = 1290, 150, 282, 470",
     "LEG_X, LEG_Y, LEG_W, LEG_H = 1318, 150, 254, 430"),
    ('''ly += 30
mapels.append(Positioned(
    Container(Text("不具备无障碍设施的站可以乘车通过，"
                   "但不能作为无障碍旅程的起点、终点或换乘站。",
                   color="#F0DFAE", fontSize="18", fontFamily=FONT, textAlign="LEFT",
                   softWrap="true", height="1.3"),
              width=num(LEG_W - 44), color="#2A2410", borderRadius="10", padding="(8,10)"),
    left=num(LEG_X + 18), top=num(ly + 6)))
ly += 112
mapels.append(Positioned(
    Container(Text("线条若在某点相交而没有白色换乘圆环，只是跨越，不是换乘。"
                   "本图布局已避免产生此类裸交叉。",
                   color=TXT_2, fontSize="18", fontFamily=FONT, textAlign="LEFT",
                   softWrap="true", height="1.3"),
              width=num(LEG_W - 44)),
    left=num(LEG_X + 18), top=num(ly)))''',
     '''ly += 34
mapels.append(Positioned(
    Container(
        Container(Text("不具备无障碍设施的站可以乘车通过，但不能作为无障碍旅程的"
                       "起点、终点或换乘站。",
                       color="#F0DFAE", fontSize="18", fontFamily=FONT, textAlign="LEFT",
                       softWrap="true", height="1.3"),
                  width=num(LEG_W - 64)),
        padding="(8,10)", color="#2A2410", borderRadius="10"),
    left=num(LEG_X + 18), top=num(ly)))
ly += 128
mapels.append(Positioned(
    Container(Text("两条线若在某点相交而没有白色换乘圆环，只是跨越，不是换乘；"
                   "本图布局已让线路只在共享站相遇。",
                   color=TXT_2, fontSize="18", fontFamily=FONT, textAlign="LEFT",
                   softWrap="true", height="1.3"),
              width=num(LEG_W - 40)),
    left=num(LEG_X + 18), top=num(ly)))'''),
    ('mapels.append(card(28, 928, 1240, 56, fill="#0E1830", radius=10))',
     'mapels.append(card(28, 926, W - 56, 58, fill="#0E1830", radius=10))'),
    ('''mapels.append(label(44, 944, "　·　".join(qs), 20, TXT_2, anchor="left_top", align="LEFT",
                    width=1210, font=FONT))
mapels.append(label(1268, 944, f"run {RUN}", 18, "#42536E", anchor="left_top",
                    align="LEFT", width=300, font=FONT))''',
     '''mapels.append(label(44, 944, "　·　".join(qs), 20, TXT_2, anchor="left_top", align="LEFT",
                    width=1290, font=FONT))
mapels.append(label(W - 44, 946, f"run {RUN}", 18, "#42536E", anchor="right_top",
                    align="RIGHT", width=220, font=FONT))'''),
]

for a, b in rep:
    if a not in s:
        raise SystemExit("MISS: " + a[:90])
    s = s.replace(a, b)

p.write_text(s, encoding="utf-8")
print("patched", len(rep), "sites")
