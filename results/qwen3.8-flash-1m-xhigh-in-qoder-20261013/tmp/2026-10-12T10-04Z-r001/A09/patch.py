"""A09 fixes: the parser does no HTML-entity decoding, so write the tag name via
CDATA; shorten the legend so it fits; reflow the vertical budget."""
import pathlib

p = pathlib.Path("tmp/2026-10-12T10-04Z-r001/A09/gen.py")
s = p.read_text(encoding="utf-8")

rep = [
    ("OY = 150", "OY = 138"),
    ('''        Container(height="10"),
        Text("印章左右不对称（红竖条在左、金横条在右上方），圆点只落在右上区域，"
             "因此镜像与旋转后的朝向都能分辨；蓝、金两条横条部分相邻，旋转后仍可见相对位置。"
             f"每格 {CELL_W}×{CELL_H}、格间 {GAP}，网格整体水平居中（左右各 {OX:.0f}px）。"
             "浅线为 30px 刻度辅助线，十字为格心，即印章局部 (60,60) 的落点。",
             color=TXT_2, fontSize="18", fontFamily=FONT, textAlign="LEFT",
             softWrap="true", height="1.32"),
        Container(height="8"),
        Text("12 个标本各自只使用一个列主序 4×4 矩阵，经 <Transform matrix> 作用在原始印章上，"
             "未手改任何形状坐标；T07 与 T08 使用同样的两个操作但顺序相反，矩阵与图像均不同。",
             color="#BFD6EE", fontSize="18", fontFamily=FONT, textAlign="LEFT",
             softWrap="true", height="1.32"),''',
     '''        Container(height="10"),
        Text(f"印章左右不对称（红竖条在左、金横条在右上），圆点只落在右上区域，"
             f"镜像与旋转后的朝向都能分辨。每格 {CELL_W}×{CELL_H}、格间 {GAP}，"
             f"网格水平居中（左右各 {OX:.0f}px）；浅线 30px 刻度，十字为格心。",
             color=TXT_2, fontSize="18", fontFamily=FONT, textAlign="LEFT",
             softWrap="true", height="1.3"),
        Container(height="8"),
        Text("12 个标本各自只使用一个列主序 4×4 矩阵作用在原始印章上，未手改任何形状坐标；"
             "T07 与 T08 用同样的两个操作但顺序相反，矩阵与图像均不同。",
             cdata=True, color="#BFD6EE", fontSize="18", fontFamily=FONT, textAlign="LEFT",
             softWrap="true", height="1.3"),'''),
    ("LY = OY + GRID_H + 26\nLEG_H = 1200 - LY - 30",
     "LY = OY + GRID_H + 22\nLEG_H = 1200 - LY - 26"),
    # audit text also mentions the tag; keep it plain there (JSON, not DSL)
    ('"dsl_translation_note": "<Transform> 的平移相对子节点布局盒，因此矩阵里写的是 "',
     '"dsl_translation_note": "Transform 标签的平移相对子节点布局盒，因此矩阵里写的是 "'),
    ('"matrix_format": "列主序 4×4，16 值",',
     '"matrix_format": "列主序 4×4，16 值，写在 Transform 的 matrix 属性上",'),
]

for a, b in rep:
    if a not in s:
        raise SystemExit("MISS: " + a[:90])
    s = s.replace(a, b)

p.write_text(s, encoding="utf-8")
print("patched", len(rep), "sites")
