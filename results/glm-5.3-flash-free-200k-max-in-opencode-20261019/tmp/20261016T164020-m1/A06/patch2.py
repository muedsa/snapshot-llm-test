# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = 'tmp/20261016T164020-m1/A06/build_a06.py'
t = open(p, encoding='utf-8').read()
old = '''PH_OF = {
    "N01": "准备", "N02": "准备", "N03": "准备", "N04": "准备",
    "N05": "构图", "N06": "构图", "N07": "构图", "N08": "构建",
    "N09": "审校", "N10": "审校", "N11": "审校", "N12": "审校",
    "N13": "收束", "N14": "收束",
}'''
new = '''PH_OF = {
    "N01": "准备", "N02": "准备", "N03": "准备", "N04": "准备",
    "N05": "构图", "N06": "构图", "N07": "构图", "N08": "构建",
    "N09": "审校", "N10": "审校", "N11": "审校", "N12": "审校",
    "N13": "收束", "N14": "收束",
}

# =====================================================================
# 标题带 + 图例行 + 图卡框架 + 节点
# =====================================================================
title = "从需求到可复现交付 · 14 节点依赖图"
S.append(text(56, 20, title, 32, INK, family=FAM_MIX, bold=True))
badge = "16 条先决依赖 · 2 条反馈回路"
fit("徽标", badge, 20, 384)
S.append(text(1160, 28, badge, 20, SUB, family=FAM_MIX, align="END", box_w=384))
subtitle = "先决依赖（实线）按拓扑层自左向右推进；反馈（红虚线）是运行中的回退，不参与排序。"
fit("副题", subtitle, 20, 1488)
S.append(text(56, 62, subtitle, 20, SUB, family=FAM_MIX))

LEG_Y = 100
lx = 56.0
S.append(hseg(lx, lx + 34, LEG_Y + 10, "#6B7A93", 3))
S.append(arrowhead(lx + 43, LEG_Y + 10, "R", "#6B7A93"))
l1 = "先决依赖（下一步的硬前置）"
fit("图例1", l1, 18, 300)
S.append(text(lx + 62, LEG_Y, l1, 18, SUB, family=FAM_MIX))
lx += 62 + estw(l1, 18) + 40
vx = lx
for _k in range(3):
    S.append(hseg(vx, vx + 9, LEG_Y + 10, "#C0392B", 3))
    vx += 16
S.append(arrowhead(vx + 7, LEG_Y + 10, "R", "#C0392B"))
l2 = "反馈回路（失败/缺陷回退，不参与排序）"
fit("图例2", l2, 18, 400)
S.append(text(vx + 26, LEG_Y, l2, 18, "#C0392B", family=FAM_MIX))
xw = vx + 26 + estw(l2, 18) + 40
for kk in ("准备", "构图", "构建", "审校", "收束"):
    S.append(rect(xw, LEG_Y + 2, 18, 16, PHASE[kk], 4))
    S.append(text(xw + 26, LEG_Y, kk, 18, SUB, family=FAM_MIX))
    xw += 26 + estw(kk, 18) + 18

GX, GY, GW, GH = 56, 144, 1488, 664
S.append(rect(GX, GY, GW, GH, CARD, 16, BORD))

CL, CR = GX + 60, GX + GW - 60          # 116..1484
colw = (CR - CL) / 10.0                  # 136.8
COLX = {L: CL + colw * L for L in range(11)}
NW, NH = 104.0, 72.0

LAYER_NAMES = ["L0 启动", "L1 输入", "L2 资源", "L3 内容", "L4 版式",
               "L5 图表", "L6 构建", "L7 渲染", "L8 检查", "L9 修复回归", "L10 收束"]
MEMBERS_SORT = [sorted(ms) for ms in LAYER_SEQ]
POS = {}
for L, members in enumerate(MEMBERS_SORT):
    if len(members) == 1:
        POS[members[0]] = (COLX[L], 426)
    elif len(members) == 2:
        POS[members[0]] = (COLX[L], 320)
        POS[members[1]] = (COLX[L], 560)
    else:
        raise SystemExit(f"L{L} 成员数 {len(members)} 超出两行排布假设: {members}")

NODE_BOX = {}
for nid, (cx, cy) in POS.items():
    NODE_BOX[nid] = [cx - NW/2, cy - NH/2, cx + NW/2, cy + NH/2]
GEO["node_boxes"] = NODE_BOX

for L in range(11):
    parts = LAYER_NAMES[L].split(" ")
    S.append(text(COLX[L], 158, parts[0], 18, FAINT, align="CENTER", box_w=120))
    S.append(text(COLX[L], 178, parts[1], 18, SUB, family=FAM_MIX, bold=True,
                  align="CENTER", box_w=120))

for nid in sorted(NODES):
    bx = NODE_BOX[nid]
    cx, cy = POS[nid]
    S.append(rect(bx[0], bx[1], NW, NH, "#FFFFFF", 10, BORD))
    S.append(rect(bx[0], bx[1], 6, NH, PHASE[PH_OF[nid]], 5))
    num = nid[1:]
    S.append(text(cx - NW/2 + 22, cy - NH/2 + 10, num, 22, FAINT, family=FN, bold=True))
    lab = NODES[nid]
    fit("节点" + nid, lab, 22, NW - 28)
    S.append(text(cx - NW/2 + 22, cy + 4, lab, 22, INK, family=FAM_MIX, bold=True))'''
assert t.count(old) == 1
open(p, 'w', encoding='utf-8').write(t.replace(old, new))
print('patched2')
