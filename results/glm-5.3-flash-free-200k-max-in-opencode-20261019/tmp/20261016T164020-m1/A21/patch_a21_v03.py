# -*- coding: utf-8 -*-
"""A21 round-01 v03 修正：chip 文本 height 残留+垂直居中；竖图短线外移+chip 下移；横屏右栏下移。"""
P = "tmp/20261016T164020-m1/A21/build_a21.py"
s = open(P, encoding="utf-8").read()

# chip: 内层 Text 去 height；垂直居中（30px 字行高约 38）
old = """    return (f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}"><Stack>'
            f'<Positioned left="0" top="0"><Container width="{w}" height="{h}"'
            f' borderRadius="{h // 2}" color="#0F2334" border="1 SOLID {CY}" /></Positioned>'
            f'<Positioned left="0" top="0" width="{w}" height="{h}">'
            f'<Text fontSize="30" color="#7FF3E6" fontFamily="{FAM_L}" textAlign="CENTER"'
            f' maxLines="1" overflow="CLIP" height="{h}">layerlight.example.org</Text></Positioned>'
            '</Stack></Positioned>')"""
new = """    ty = (h - 38) // 2
    return (f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}"><Stack>'
            f'<Positioned left="0" top="0"><Container width="{w}" height="{h}"'
            f' borderRadius="{h // 2}" color="#0F2334" border="1 SOLID {CY}" /></Positioned>'
            f'<Positioned left="0" top="{ty}" width="{w}" height="{h - ty}">'
            f'<Text fontSize="30" color="#7FF3E6" fontFamily="{FAM_L}" textAlign="CENTER"'
            ' maxLines="1" overflow="CLIP">layerlight.example.org</Text></Positioned>'
            '</Stack></Positioned>')"""
assert old in s
s = s.replace(old, new)

# 竖图: 眉行两侧短线外移
s = s.replace('<Positioned left="292" top="500"><Container width="84" height="2"',
              '<Positioned left="258" top="500"><Container width="84" height="2"')
s = s.replace('<Positioned left="704" top="500"><Container width="84" height="2"',
              '<Positioned left="738" top="500"><Container width="84" height="2"')
# 竖图: chip 下移 986 → 1118
s = s.replace("P.append(chip(310, 986, 460, 62))", "P.append(chip(310, 1118, 460, 62))")

# 横屏: 右栏整体 +30
for a, b in [("660, 122", "660, 152"), ("660?, ", ""), ("660, 136", "660, 166"),
             ("660, 188", "660, 218"), ("660, 286", "660, 316"),
             ("660, 346", "660, 376"), ("660, 410", "660, 440"),
             ("660, 430", "660, 460")]:
    if a.strip() == "660?,":
        continue
    if a in s:
        s = s.replace(a, b)
s = s.replace("W.append(chip(660, 494, 460, 60))", "W.append(chip(660, 524, 460, 60))")

open(P, "w", encoding="utf-8", newline="\n").write(s)
print("v03 patch done")
