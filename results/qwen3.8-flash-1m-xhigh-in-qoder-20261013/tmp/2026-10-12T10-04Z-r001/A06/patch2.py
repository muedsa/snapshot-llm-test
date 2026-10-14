"""A06: route the long N04->N13 prerequisite edge over the top instead of dropping
it through the node stacked below N04 in the same layer column; move layer labels
up to clear it; put merge dots on the node edge they mark."""
import pathlib

p = pathlib.Path("tmp/2026-10-12T10-04Z-r001/A06/gen.py")
s = p.read_text(encoding="utf-8")

rep = [
    ("DETOUR_Y = 606", "TOP_ROUTE_Y = 166"),
    ('''    if (a, b) == ("N04", "N13"):
        return [(ax, BOX[a][3]), (ax, DETOUR_Y), (bx, DETOUR_Y), (bx, BOX[b][3])]''',
     '''    if (a, b) == ("N04", "N13"):
        # N04 and N05 share layer 2, so dropping below N04 would run straight through
        # N05; this one long edge goes over the top instead.
        return [(ax, BOX[a][1]), (ax, TOP_ROUTE_Y), (bx, TOP_ROUTE_Y), (bx, BOX[b][1])]'''),
    ('''    els.append(Positioned(C(width=num(PITCH - 8), height=num(472), color="#0C1428",
                            borderRadius="10", border="1 SOLID #16223C"),
                          left=num(x + 4), top=num(168)))
    els.append(label(x + PITCH / 2, 150, f"第 {L} 层", 18, TXT_3, anchor="center",
                     align="CENTER", width=PITCH - 10, font=MONO))''',
     '''    els.append(Positioned(C(width=num(PITCH - 8), height=num(474), color="#0C1428",
                            borderRadius="10", border="1 SOLID #16223C"),
                          left=num(x + 4), top=num(176)))
    els.append(label(x + PITCH / 2, 142, f"第 {L} 层", 18, TXT_3, anchor="center",
                     align="CENTER", width=PITCH - 10, font=MONO))'''),
    ('''        els.append(Positioned(
            C(width="11", height="11", color=EMERALD, shape="CIRCLE"),
            left=num(bx - NODE_W / 2 - 18), top=num(by - 5.5)))''',
     '''        els.append(Positioned(
            C(width="13", height="13", color=EMERALD, shape="CIRCLE"),
            left=num(bx - NODE_W / 2 - 6.5), top=num(by - 6.5)))'''),
    ('''        Text("交叉处若无实心圆点，只是线段跨越，不构成依赖", color=TXT_3, fontSize="18",
             fontFamily=FONT),''',
     '''        Row(C(width="11", height="11", color=EMERALD, shape="CIRCLE"),
            Container(width="8"),
            Text("绿点=多个先决条件在此会聚；无绿点的交叉只是跨越", color=TXT_3,
                 fontSize="18", fontFamily=FONT),
            crossAxisAlignment="CENTER"),'''),
    ('''els.append(label(PAD, 832,
                 "并行关系：N02‖N03、N04‖N05、N06‖N07，两路会聚到 N08；"
                 "N04 另有一条跨越 7 层的先决边在下方绕行进入 N13，避免压住链上文字。",
                 18, TXT_2, anchor="left_top", align="LEFT", width=1536, font=FONT))''',
     '''els.append(label(PAD, 832,
                 "并行关系：N02‖N03、N04‖N05、N06‖N07，两路会聚到 N08；"
                 "N04→N13 这条跨越 7 层的先决边从顶部绕行，避免穿过同列下方的 N05。",
                 18, TXT_2, anchor="left_top", align="LEFT", width=1536, font=FONT))'''),
]

for a, b in rep:
    if a not in s:
        raise SystemExit("MISS: " + a[:90])
    s = s.replace(a, b)

p.write_text(s, encoding="utf-8")
print("patched", len(rep), "sites")
