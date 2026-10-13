"""A06 layout fixes: shorter header subtitle, shorter layer bands, a clean
three-card bottom row, and one stats line instead of overlapping notes."""
import pathlib

p = pathlib.Path("tmp/2026-10-12T10-04Z-r001/A06/gen.py")
s = p.read_text(encoding="utf-8")

rep = [
    ('''            Text("14 个节点 · 16 条先决依赖（实线）· 2 条反馈关系（虚线，不参与 DAG 排序）"
                 "· 数据源 inputs/graph.json", color=TXT_2, fontSize="20", fontFamily=FONT),''',
     '''            Text("14 个节点 · 16 条先决依赖（实线）· 2 条反馈关系（虚线，不参与 DAG 排序）",
                 color=TXT_2, fontSize="20", fontFamily=FONT),'''),
    ("DETOUR_Y = 612\nGROUP_Y = 655     # lane where same-column edges merge before rising",
     "DETOUR_Y = 606"),
    # ---- bottom row: three cards
    ('''els.append(Positioned(
    Border(
        Container(
            Col(Text("反馈 ① 失败后回到构建", color="#FFD9E2", fontSize="20",
                     fontStyle="BOLD", fontFamily=FONT, textAlign="LEFT"),
                Container(height="4"),
                Text("N09 首轮渲染失败 → 虚线回到 N08 DSL构建，改完再从 N09 重跑；"
                     "这条边不是先决条件，不参与分层。",
                     color="#F3C6D1", fontSize="18", fontFamily=FONT, textAlign="LEFT",
                     softWrap="true", height="1.28"),
                crossAxisAlignment="START"),
            width="452", color="#2A1520", borderRadius="12", padding="(10,14)"),
        border="1 SOLID #7A3A4E", borderRadius="12"),
    left=num(560), top=num(676)))
els.append(Positioned(
    Border(
        Container(
            Col(Text("反馈 ② 检查发现问题后修复", color="#FFD9E2", fontSize="20",
                     fontStyle="BOLD", fontFamily=FONT, textAlign="LEFT"),
                Container(height="4"),
                Text("N10 视觉检查发现问题 → 虚线回到 N08 修改；实线 N10→N11 问题修复 → "
                     "N12 回归渲染 才是先决链。",
                     color="#F3C6D1", fontSize="18", fontFamily=FONT, textAlign="LEFT",
                     softWrap="true", height="1.28"),
                crossAxisAlignment="START"),
            width="452", color="#2A1520", borderRadius="12", padding="(10,14)"),
        border="1 SOLID #7A3A4E", borderRadius="12"),
    left=num(1040), top=num(676)))

# reading guide + stats panel
els.append(card(PAD, 676, 500, 118, fill=CARD2, radius=12))
els.append(Positioned(
    Col(
        Text("怎么读这张图", color=SKY, fontSize="20", fontStyle="BOLD", fontFamily=FONT),
        Container(height="8"),
        Text(f"横轴是自左向右的拓扑层（第 0–{NLANE-1} 层），同一层内互不依赖、可并行；"
             f"实线箭头一律指向更靠右的层，不存在指向过去层的先决边。"
             f"最长先决链 {len(LP)} 个节点：{' → '.join(LP)}。",
             color=TXT_2, fontSize="18", fontFamily=FONT, textAlign="LEFT",
             softWrap="true", height="1.3"),
        crossAxisAlignment="START"),
    left=num(PAD + 18), top=num(688), width=num(464)))

els.append(label(PAD, 812,
                 "节点标签字号 22，编号与注释 18；14 个节点编号与标签全部出现在图中。",
                 18, TXT_3, anchor="left_top", align="LEFT", width=900, font=FONT))
els.append(label(W - PAD, 812, f"run {RUN}", 18, "#42536E", anchor="right_top",
                 align="RIGHT", width=340, font=FONT))

# parallel / grouping annotation under the early columns
els.append(Positioned(
    Text("N02/N03 并行 · N04/N05 并行 · N06 与 N07 并行后会聚到 N08",
         color=TXT_3, fontSize="18", fontFamily=FONT),
    left=num(GX0 + 6), top=num(760)))''',
     '''def callout(x, w, title, body, *, tint="#2A1520", edge="#7A3A4E", tcol="#FFD9E2",
            bcol="#F3C6D1"):
    return Positioned(
        Border(
            Container(
                Col(Text(title, color=tcol, fontSize="20", fontStyle="BOLD",
                         fontFamily=FONT, textAlign="LEFT"),
                    Container(height="6"),
                    Container(Text(body, color=bcol, fontSize="18", fontFamily=FONT,
                                   textAlign="LEFT", softWrap="true", height="1.3"),
                              width=num(w - 30)),
                    crossAxisAlignment="START"),
                width=num(w), height=num(132), color=tint, borderRadius="12",
                padding="(10,14)"),
            border=f"1 SOLID {edge}", borderRadius="12"),
        left=num(x), top=num(656))


els.append(card(PAD, 656, 490, 132, fill=CARD2, radius=12))
els.append(Positioned(
    Col(
        Text("怎么读这张图", color=SKY, fontSize="20", fontStyle="BOLD", fontFamily=FONT),
        Container(height="6"),
        Container(Text("横轴是自左向右的拓扑层（第 0–10 层），同一层内互不依赖、可并行；"
                       "实线箭头一律指向更靠右的层，不存在指向过去层的先决边。",
                       color=TXT_2, fontSize="18", fontFamily=FONT, textAlign="LEFT",
                       softWrap="true", height="1.3"),
                  width=num(460)),
        crossAxisAlignment="START"),
    left=num(PAD + 15), top=num(668), width=num(460)))

els.append(callout(PAD + 490 + 24, 490, "反馈 ① 失败后回到构建",
                   "N09 首轮渲染失败 → 虚线回到 N08 DSL构建；改完再从 N09 重跑。"
                   "这条边不是先决条件，不参与分层。"))
els.append(callout(PAD + 2 * (490 + 24), 508, "反馈 ② 检查发现问题后修复",
                   "N10 视觉检查发现问题 → 虚线回到 N08 修改；实线 N10→N11 问题修复 → "
                   "N12 回归渲染 才是先决链。", ))

els.append(label(PAD, 806,
                 f"最长先决路径（按节点数 {len(LP)} 个，另有等长解）：{' → '.join(LP)}",
                 18, TXT_2, anchor="left_top", align="LEFT", width=1536, font=FONT))
els.append(label(PAD, 832,
                 "并行关系：N02‖N03、N04‖N05、N06‖N07，两路会聚到 N08；"
                 "N04 另有一条跨越 7 层的先决边在下方绕行进入 N13，避免压住链上文字。",
                 18, TXT_2, anchor="left_top", align="LEFT", width=1536, font=FONT))
els.append(label(PAD, 858,
                 "节点标签字号 22，节点编号与全部注释 18；14 个节点的编号与标签都出现在图中。"
                 "数据源 inputs/graph.json。",
                 18, TXT_3, anchor="left_top", align="LEFT", width=1536, font=FONT))
els.append(label(W - PAD, 900, f"run {RUN}", 18, "#42536E", anchor="right_top",
                 align="RIGHT", width=340, font=FONT))'''),
]

for a, b in rep:
    if a not in s:
        raise SystemExit("MISS: " + a[:90])
    s = s.replace(a, b)

p.write_text(s, encoding="utf-8")
print("patched", len(rep), "sites")
