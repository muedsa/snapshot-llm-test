"""Move case-10 panel B caption out of the way and raise the reconstructed text."""
from pathlib import Path

p = Path(__file__).with_name("case10_anamorphic.py")
s = p.read_text(encoding="utf-8")
s = s.replace('BX, BY, BW, BH = 50, 640, 900, 220', 'BX, BY, BW, BH = 50, 626, 900, 200')
s = s.replace('ox, oy = BX + BW / 2, BY + BH / 2 + 6', 'ox, oy = BX + BW / 2, BY + 74')
s = s.replace('''s.text("panel", f"乘客实际看到的像（同一相机模型反投影，放大 {MAG}× 便于阅读）",
       BX + 16, BY + BH - 30, 17, "#9FB2C4")''',
'''s.text("panel", f"乘客实际看到的像（同一相机模型反投影，放大 {MAG}× 便于阅读）",
       BX, BY + BH + 8, 17, INK3)''')
s = s.replace('    y = 886 + (i // 3) * 34', '    y = 878 + (i // 3) * 32')
p.write_text(s, encoding="utf-8")
print("patched", "BY + BH + 8" in s)
