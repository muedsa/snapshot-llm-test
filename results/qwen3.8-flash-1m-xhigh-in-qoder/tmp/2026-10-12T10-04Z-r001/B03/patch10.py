"""Patch case-10 to a realistic glyph size (0.18 m) and a readable magnified check panel."""
from pathlib import Path

p = Path(__file__).with_name("case10_anamorphic.py")
s = p.read_text(encoding="utf-8")

s = s.replace('''TEXT_TARGET = "换乘 3 号线"
ARROW_TARGET = "出口 ↙"      # ↙ avoided in type; arrow drawn as geometry
VIEW_W, VIEW_H = 760, 300     # size of the "as seen" panel''',
'''TEXT_TARGET = "换乘 3 号线"
GLYPH_M = 0.18                # what one character should appear to be, metres tall
MAG = 3.3                     # magnification of the "as seen" panel, stated on the plate''')

s = s.replace('''def target_layout():
    size = 92''', '''def target_layout():
    size = GLYPH_M / EYE_D * FOCAL     # px in the eye panel: 0.18 m at 6 m''')

s = s.replace('''        pr = project((fp[0], 0.0, fp[2]))
        pts.append((ox + pr[0] * 0.34, oy + pr[1] * 0.34))''',
'''        pr = project((fp[0], 0.0, fp[2]))
        pts.append((ox + pr[0] * MAG, oy + pr[1] * MAG))''')

s = s.replace('''           (pts[0][1] + pts[1][1] + pts[2][1] + pts[3][0]) / 4 - TSIZE * 0.34 * 0.5,
           int(TSIZE * 0.34), DARK, align="center", bold=True, font=MONO)''',
'''           (pts[0][1] + pts[1][1] + pts[2][1] + pts[3][1]) / 4
           - TSIZE * MAG * 0.5, max(16, int(TSIZE * MAG)), DARK, align="center",
           bold=True, font=MONO)''')

s = s.replace('''s.text("hdr", f"观察点：眼高 {EYE_H} m · 距地贴中心 {EYE_D:.0f} m · 视场 {FOCAL:.0f}px",
       50, 98, 20, INK2)''',
'''s.text("hdr", f"观察点：眼高 {EYE_H} m · 距地贴中心 {EYE_D:.0f} m · 视场 {FOCAL:.0f}px"
              f" · 目标字高 {GLYPH_M * 1000:.0f} mm", 50, 98, 20, INK2)''')

s = s.replace('''s.text("panel", "乘客实际看到的像（按同一相机模型反投影）", BX + 16, BY + BH - 30,
       17, "#9FB2C4")''',
'''s.text("panel", f"乘客实际看到的像（同一相机模型反投影，放大 {MAG}× 便于阅读）",
       BX + 16, BY + BH - 30, 17, "#9FB2C4")''')

p.write_text(s, encoding="utf-8")
print("patched", "GLYPH_M" in s, "MAG" in s)
