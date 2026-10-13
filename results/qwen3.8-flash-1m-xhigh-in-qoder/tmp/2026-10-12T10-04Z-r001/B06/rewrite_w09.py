"""Work 09 take 2: taller floor bands for a standing sign read at 2-3 metres."""
import ast
from pathlib import Path

fp = Path(__file__).resolve().parent / "b06works2.py"
t = fp.read_text(encoding="utf-8")
i = t.index("# ------------------------------------------------------------------ 09 门诊楼层")
j = t.index("# ------------------------------------------------------------------ 10 家庭水电煤")
new = '''# ------------------------------------------------------------------ 09 门诊楼层
def w09():
    w, h = 900, 1600
    s = Sheet(w, h, min_font=18, bg="#F5F2EA")
    s.rect(0, 0, w, h, "#F5F2EA")
    hp = D["hospital"]
    s.rect(0, 0, w, 128, "#1B3A4B")
    s.text("h", "门诊大楼：你要去的科在哪", 32, 26, 38, WHITE, bold=True)
    s.text("h", "左边按楼层看，右边按科室查；示例医院布局", 32, 78, 24, "#A8C7D6")
    floors = sorted(hp["floors"], key=lambda fl: -fl["floor"])
    fx, fw, fh = 32, 470, 188
    y = 152
    for fl in floors:
        s.rect(fx, y, fw, fh - 14, WHITE, radius=10, border=f"1 SOLID {LINE}")
        s.panel(fx, y, fw, fh - 14)
        s.text("f", f"{fl['floor']} 层", fx + 16, y + 14, 30, INK, bold=True,
               font=MONO)
        east, west = fl["zones"]["东区"], fl["zones"]["西区"]
        total = len(east) + len(west)
        ew = (fw - 32) * len(east) / total
        s.rect(fx + 16, y + 62, ew - 5, 96, "#DCE7EE", radius=8)
        s.rect(fx + 16 + ew, y + 62, fw - 32 - ew, 96, "#EFE6D8", radius=8)
        for i, d in enumerate(east):
            dw = (ew - 5 - 8 * (len(east) - 1)) / len(east)
            s.text("f", d, fx + 16 + i * (dw + 8) + dw / 2, y + 78, 20, INK,
                   align="center", maxw=dw - 4)
        for i, d in enumerate(west):
            dw = (fw - 32 - ew - 8 * (len(west) - 1)) / len(west)
            s.text("f", d, fx + 16 + ew + i * (dw + 8) + dw / 2, y + 78, 20, INK,
                   align="center", maxw=dw - 4)
        s.text("f", "东区", fx + 16, y + 128, 18, BLUE)
        s.text("f", "西区", fx + 16 + ew + 6, y + 128, 18, AMBER)
        y += fh
    gy = y - 14
    s.rect(fx, gy, fw, 44, "#1B3A4B", radius=8)
    s.text("f", "1 层入口 · 东门在右侧", fx + fw / 2, gy + 10, 22, WHITE,
           align="center")
    tgt = hp["target"]
    ty = 152 + (6 - tgt["floor"]) * fh + 96
    s.line(fx + fw - 56, gy + 22, fx + fw - 56, ty, RED, 5.0)
    s.line(fx + fw - 56, ty, fx + 16 + ew_mid(hp), ty, RED, 5.0)
    s.dot(fx + 16 + ew_mid(hp), ty, 10, RED, ring=WHITE, ring_w=2)
    s.text("r", f"例：{tgt['dept']}（{tgt['zone']}）", fx + fw - 44, ty - 34, 22, RED,
           align="right", bold=True)
    s.text("r", hp["lift_note"], fx + fw - 44, gy + 58, 20, INK2, align="right")
    ix = 540
    s.rect(ix, 152, w - ix - 32, gy + 44 - 152, WHITE, radius=12,
           border=f"1 SOLID {LINE}")
    s.panel(ix, 152, w - ix - 32, gy + 44 - 152)
    s.text("i", "按科室查楼层", ix + 20, 170, 26, INK, bold=True)
    s.text("i", "与左图同一份数据", ix + 20, 208, 18, INK3)
    iy = 244
    for name, fl, zone in hp["index"]:
        s.text("i", name, ix + 20, iy, 20, INK, maxw=180)
        s.text("i", f"{fl} 层 · {zone}", ix + 300, iy, 20, INK2, align="right",
               font=MONO)
        s.line(ix + 20, iy + 30, ix + 300, iy + 30, "#EFEADC", 1.0)
        iy += 48
    s.text("f", "示例布局与科室分布；实际就诊请以医院当日指引为准。", 32, h - 44, 20,
           INK3)
    save(s, "case09-wayfinding", 18)


def ew_mid(hp):
    """x offset of the 3F east-zone centre inside a floor band."""
    fl = next(f2 for f2 in hp["floors"] if f2["floor"] == 3)
    east, west = fl["zones"]["东区"], fl["zones"]["西区"]
    band = 470 - 32
    ew = band * len(east) / (len(east) + len(west))
    return ew / 2


'''
t = t[:i] + new + t[j:]
ast.parse(t)
fp.write_text(t, encoding="utf-8")
print("work 09 rewritten")
