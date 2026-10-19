# -*- coding: utf-8 -*-
"""探针3：异形圆角椭圆 / 同心环叠色 / 剪切平行四边形。"""
import pathlib
import b03_common as C

s = [f'<Container width="760" height="600" color="#101418" />']
# 1) 实心异形圆角（椭圆）非法 mdash;borderRadius 999 与 w!=h
C.ellipse(s, 120, 120, 90, 60, "#FFBD69")
C.ellipse(s, 280, 120, 70, 100, "#8ECAE6")
# 2) 同心环叠色（外盖内）
C.ellipse(s, 600, 120, 100, 70, "#FFD166")
C.ellipse(s, 605, 112, 74, 50, "#101418")
C.ellipse(s, 610, 105, 48, 32, "#FFD166")
C.ellipse(s, 614, 99, 22, 15, "#101418")
# 3) integers 剪切矩阵平行四边形（等距菱形顶面）
#    X 轴(1,0) -> (0.866, 0.5); Y 轴(0,1) -> (-0.866, 0.5)
M_TOP = "(0.866025,-0.866025,0,0,0.5,0.5,0,0,0,0,1,0,0,0,0,1)"
def shear(s, cx, cy, w, h, matrix, color):
    s.append(f'<Positioned left="{C.fnum(cx - w / 2)}" top="{C.fnum(cy - h / 2)}" '
             f'width="{C.fnum(w)}" height="{C.fnum(h)}">'
             f'<Transform matrix="{matrix}" origin="({C.fnum(w / 2)},'
             f'{C.fnum(h / 2)})"><Container width="{C.fnum(w)}" '
             f'height="{C.fnum(h)}" color="{color}" /></Transform>'
             f'</Positioned>')
shear(s, 180, 420, 180, 180, M_TOP, "#3ECFA5")       # 菱形（顶面）
#    左右侧面：Y 或 X 轴垂直
M_SIDE = "(0.866025,0,0,0,0.5,1,0,0,0,0,1,0,0,0,0,1)"
shear(s, 480, 430, 160, 160, M_SIDE, "#5A6B85")      # 侧面 skew
C.txt(s, 16, 560, "pro3：椭圆 / 同心环叠色 / 等距剪切。", 18, "#94A3B8")
p = pathlib.Path("probe-iso.snapshot")
p.write_text(C.wrap_dsl(760, 600, s, "#101418"), encoding="utf-8")
print("written")
