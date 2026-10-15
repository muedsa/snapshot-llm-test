#!/usr/bin/env python
# B03 第 07 件重做。首版两处硬伤（看图发现）：
#   ① 日照条以圆心为原点向两侧摆，而楼体footprint（380×180）几乎把 430px 的条
#      **整个盖住**，只在左右各露出一小块楔形——变换做了，图上等于没做。
#      平面日照图里，光线和影子其实**共线**（影子就在太阳的反方向），
#      所以正确画法是：沿同一条轴，楼的近侧是入射光线，远侧是投影。
#      按 09/11/13/15 四个真实太阳方位角 135°/157.5°/202.5°/225° 与高度角
#      18°/30°/30°/18°，影长 = 等效楼高 30m / tan(高度角) × 3 倍比例。
#   ② 方位标签放在 r=480，落到 y≈140 的位置，和标题「冬至日 · 北纬 31.2°」
#      以及右上的「35.4°」直接撞在一起。→ 罗盘半径收到 310，圆心下移到 520。
#   ③ 外圈 r=520 的圆上下都超出画布，底边压到页脚。→ 同上收进 310。
# 启动基准：总任务根 (suite_root)。用法：python fix_b03_c07b.py
from pathlib import Path

p = Path(__file__).with_name("build_b03.py")
s = p.read_text(encoding="utf-8")
start = s.index('    W, H = 1200, 900')
end = s.index('# ══════════════ 08 ClipPath 曲线徽章')
new = '''    W, H = 1200, 900
    b = [rect(0, 0, W, H, "#F7F5F0")]
    b.append(txt("日照分析", 64, 40, 500, None, 28, "#8A6D3B"))
    b.append(txt("冬至日 · 北纬 31.2°", 64, 84, 700, None, 46, "#2B2119", W600))
    b.append(txt("冬至正午太阳高度 35.4°", 760, 50, 376, None, 24, "#8A6D3B",
                 align="END"))

    GX, GY, R = 800, 520, 310
    b.append(circle(GX, GY, R * 2, None, border="1 SOLID #DED8CB"))
    b.append(circle(GX, GY, 232, None, border="1 SOLID #E4DED2"))

    # 罗盘：北在上、南在下（平面日照图惯例）
    for lbl, dx, dy, anc in (("北", 0, -R - 34, "MIDDLE"),
                             ("南", 0, R + 12, "MIDDLE"),
                             ("东", R + 12, 0, "MIDDLE"),
                             ("西", -R - 66, 0, "MIDDLE")):
        b.append(txt(lbl, GX + dx - 33, GY + dy - 13, 66, None, 22,
                     "#A8937A", align=anc))
    # 太阳方位扇面（正南 ±40°）
    for _i in range(17):
        _a = math.radians(-40 + _i * 5)
        b.append(segment(GX + 232 * math.sin(_a), GY - 232 * math.cos(_a),
                         GX + R * math.sin(_a), GY - R * math.cos(_a),
                         "#E6E0D2", 1))

    # 时刻 → (方位角, 高度角, 比例影长m)。影长 = 等效楼高 30m / tan(高度角)。
    hours = [("09:00", 135.0, 18.0, 276), ("11:00", 157.5, 30.0, 156),
             ("13:00", 202.5, 30.0, 156), ("15:00", 225.0, 18.0, 276)]
    for lbl, az, alt, shl in hours:
        th = math.radians(az)
        ux, uy = -math.sin(th), math.cos(th)   # 太阳反方向 = 投影方向
        # 入射光线：从楼体外缘往里指（仅示意，用短箭头段）
        b.append(segment(GX + 150 * ux, GY + 150 * uy,
                         GX + 300 * ux, GY + 300 * uy, "#E8A33B", 3))
        # 投影带：从楼体往背阳侧延伸
        b.append(f'<Positioned left="{GX - shl / 2:.1f}" top="{GY - 9:.1f}" '
                 f'width="{shl:.1f}" height="18">'
                 f'<Transform matrix="({_mat(az):s})" alignment="CENTER">'
                 f'<Container width="{shl:.1f}" height="18" color="#B8C4D0" '
                 f'opacity="0.85"/></Transform></Positioned>')
        # 时刻标签放在投影带的另一端，避开楼体
        lx, ly = GX + (shl + 42) * ux, GY + (shl + 42) * uy
        b.append(txt(lbl, lx - 48, ly - 13, 96, None, 21, "#8A6D3B",
                     align="CENTER"))

    # 楼体（旋转 15° 的矩形）
    b.append(f'<Positioned left="{GX - 130:.1f}" top="{GY - 60:.1f}" '
             f'width="260" height="120">'
             f'<Transform matrix="({_mat(15):s})" alignment="CENTER">'
             f'<Container width="260" height="120" color="#3A4A5E" '
             f'borderRadius="6"/></Transform></Positioned>')
    for _i in range(4):
        b.append(rect(GX - 96 + _i * 52, GY - 36, 32, 72, "#5A6C84", 4))
    b.append(txt("拟建 12 层住宅", GX - 130, GY + 82, 260, None, 22, "#2B2119",
                 align="CENTER"))
    b.append(txt("橙色 = 入射阳光　灰蓝 = 投影", GX - 160, GY + 114, 320, None,
                 19, "#A8937A", align="CENTER"))

    facts = [("正午太阳高度", "35.4°"), ("日出 / 日落", "07:02 / 17:14"),
             ("最低日照时数", "3.8 h"), ("受影响住户", "4 户 101–104")]
    for i, (k, v) in enumerate(facts):
        y = 196 + i * 62
        b.append(txt(k, 64, y, 300, None, 24, "#8A6D3B"))
        b.append(txt(v, 64, y + 28, 300, None, 26, "#2B2119", W600))
    b.append(rect(64, 452, 340, 2, "#DED8CB"))
    b.append(txt("影长按等效楼高 30 m 与冬至日", 64, 472, 340, None, 22,
                 "#8A6D3B"))
    b.append(txt("高度角换算，比例示意。", 64, 502, 340, None, 22, "#8A6D3B"))
    b.append(txt("西侧 2–4 层午后日照不足，需复核平面。", 64, 552, 380, None,
                 22, "#B0573A"))
    footer(b, 64, H - 60, 1072, "分析图为示意；非真实工程计算结果")
    return canvas(W, H, "".join(b), "#F7F5F0")


'''
s = s[:start] + new + s[end:]

# 插入 _mat 辅助函数（把「度数」转成服务接受的 16 个 Float 列主序矩阵）
helper = '''

def _mat(deg: float) -> str:
    """把二维旋转角度转成服务要求的 16 个 Float、列主序、无空格的 4x4 矩阵。"""
    c, s2 = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return (f"{c:.5f},{s2:.5f},0,0,{-s2:.5f},{c:.5f},0,0,"
            f"0,0,1,0,0,0,0,1")

'''
anchor = "\n\n# ══════════════ 01 ClipPath"
s = s.replace(anchor, helper + "\n# ══════════════ 01 ClipPath", 1)
p.write_text(s, encoding="utf-8")
print("c07 rebuilt")