# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = 'tmp/20261016T164020-m1/A06/build_a06.py'
t = open(p, encoding='utf-8').read()

def rep(old, new):
    global t
    assert t.count(old) == 1, 'count=%d :: %s' % (t.count(old), old[:60])
    t = t.replace(old, new)

# 1) 拓扑校验：先决边只要求指向更晚层（N03→N06 / N04→N13 允许跨层）
rep('assert all(lay[b] == lay[a] + 1 for a, b in SOLID), "solid_edges 需为逐层+1（否则同层先决边会指回同/过去层）"',
    'assert all(lay[b] > lay[a] for a, b in SOLID), "solid_edges 必须指向更晚拓扑层（无回指歧义）"')

# 2) 最长路径并列时取 ID 较大分支（N04→N07 主链，与绘制主链一致）
rep('        n = max(preds, key=lambda p: memo[p])',
    '        n = max(preds, key=lambda p: (memo[p], p))  # 并列取 ID 较大分支（N04→N07）')

# 3) 层名与成员语义对齐
rep('''LAYER_NAMES = ["L0 启动", "L1 输入", "L2 资源", "L3 内容", "L4 版式",
               "L5 图表", "L6 构建", "L7 渲染", "L8 检查", "L9 修复回归", "L10 收束"]''',
    '''LAYER_NAMES = ["L0 启动", "L1 输入", "L2 分析", "L3 设计", "L4 构建",
               "L5 渲染", "L6 检查", "L7 修复", "L8 回归", "L9 校验", "L10 归档"]''')

# 4) 双层行序（绘制决策，拓扑不变）：L1 上=N03/下=N02；L2 上=N05/下=N04
rep('''    else:
        raise SystemExit(f"L{L} 成员数 {len(members)} 超出两行排布假设: {members}")
''',
    '''    else:
        raise SystemExit(f"L{L} 成员数 {len(members)} 超出两行排布假设: {members}")
# 同层双行次序（绘制决策，不改拓扑）：L1 上=N03/下=N02；L2 上=N05/下=N04
POS["N03"] = (COLX[1], 320); POS["N02"] = (COLX[1], 560)
POS["N05"] = (COLX[2], 320); POS["N04"] = (COLX[2], 560)
''')

# 5) 节点文字：4 字 22px 需 88px 宽 → 从 cx-46 起（左色条后 10px），fit 宽 98
rep('''    num = nid[1:]
    S.append(text(cx - NW/2 + 22, cy - NH/2 + 10, num, 22, FAINT, family=FN, bold=True))
    lab = NODES[nid]
    fit("节点" + nid, lab, 22, NW - 28)
    S.append(text(cx - NW/2 + 22, cy + 4, lab, 22, INK, family=FAM_MIX, bold=True))''',
    '''    num = nid[1:]
    S.append(text(cx - 46, cy - 27, num, 22, FAINT, family=FN, bold=True))
    lab = NODES[nid]
    fit("节点" + nid, lab, 22, 98)
    S.append(text(cx - 46, cy - 1, lab, 22, INK, family=FAM_MIX, bold=True))''')

# 6) E5 顶部绕行改从 N03 右缘出（两排同在 y320，先右 25px 再上拱）
rep('''E5P = [(port_l("N03")[0], NODE_BOX["N03"][3] - 16), (COLX[0] + 68, NODE_BOX["N03"][3] - 16),
       (COLX[0] + 68, 252), (COLX[2] + 70.4, 252), (COLX[2] + 70.4, 302),
       (NODE_BOX["N06"][0], 302)]''',
    '''E5P = [port_r("N03"), (COLX[1] + 77.2, port_r("N03")[1]),
       (COLX[1] + 77.2, 252), (COLX[2] + 70.4, 252), (COLX[2] + 70.4, 302),
       (NODE_BOX["N06"][0], 302)]''')

# 7) ROUTES：N01 分叉肘形、N02→N05 底入上拱、N02→N04 改直连、N06/N07→N08 改肘形
rep('''    ("N01", "N02"): ([port_r("N01"), port_l("N02")], "R"),
    ("N01", "N03"): ([port_r("N01"), port_l("N03")], "R"),
    ("N02", "N05"): ([port_r("N02"), port_l("N05")], "R"),
    ("N02", "N04"): ([port_r("N02"), (COLX[1] + 65.2, NODE_BOX["N02"][3]),
                      (COLX[1] + 65.2, 500), (COLX[2], 500), (COLX[2], NODE_BOX["N04"][1])], "U"),
    ("N03", "N06"): (E5P, "L"),
    ("N05", "N06"): ([port_r("N05"), port_l("N06")], "R"),
    ("N04", "N07"): ([port_r("N04"), port_l("N07")], "R"),
    ("N06", "N08"): ([port_r("N06"), (NODE_BOX["N08"][0], NODE_BOX["N08"][1] + 18)], "R"),
    ("N07", "N08"): ([port_r("N07"), (NODE_BOX["N08"][0], NODE_BOX["N08"][3] - 18)], "R"),''',
    '''    ("N01", "N02"): ([port_r("N01"), (COLX[0] + 68, port_r("N01")[1]),
                      (COLX[0] + 68, port_l("N02")[1]), port_l("N02")], "R"),
    ("N01", "N03"): ([port_r("N01"), (COLX[0] + 68, port_r("N01")[1]),
                      (COLX[0] + 68, port_l("N03")[1]), port_l("N03")], "R"),
    ("N02", "N05"): ([port_t("N02"), (port_t("N02")[0], 380), (COLX[2], 380),
                      (COLX[2], NODE_BOX["N05"][3])], "U"),
    ("N02", "N04"): ([port_r("N02"), port_l("N04")], "R"),
    ("N03", "N06"): (E5P, "R"),
    ("N05", "N06"): ([port_r("N05"), port_l("N06")], "R"),
    ("N04", "N07"): ([port_r("N04"), port_l("N07")], "R"),
    ("N06", "N08"): ([port_r("N06"), (COLX[3] + 67.6, port_r("N06")[1]),
                      (COLX[3] + 67.6, NODE_BOX["N08"][1] + 18),
                      (NODE_BOX["N08"][0], NODE_BOX["N08"][1] + 18)], "R"),
    ("N07", "N08"): ([port_r("N07"), (COLX[3] + 67.6, port_r("N07")[1]),
                      (COLX[3] + 67.6, NODE_BOX["N08"][3] - 18),
                      (NODE_BOX["N08"][0], NODE_BOX["N08"][3] - 18)], "R"),''')

# 8) 反馈箭头方向：F1 自上方进入 N08 顶缘 → D；F2 自下方进入底缘 → U
rep('''for (a, b), pts in ((("N09", "N08"), F1P), (("N10", "N08"), F2P)):''',
    '''for (a, b), pts, fdir in ((("N09", "N08"), F1P, "D"), (("N10", "N08"), F2P, "U")):''')
rep('''    S.append(arrow_at(pts[-1], "U", FB_COL))''',
    '''    S.append(arrow_at(pts[-1], fdir, FB_COL))''')

# 9) 反馈标签 ② 左移避让 F2 竖段；补两条跨层绕行小注
rep('''lab2 = "② 检查发现问题 → 返回构建"
fit("反馈注2", lab2, 18, 240)
S.append(text(700, 508, lab2, 18, FB_COL, family=FAM_MIX, bold=True))''',
    '''lab2 = "② 检查发现问题 → 返回构建"
fit("反馈注2", lab2, 18, 240)
S.append(text(690, 508, lab2, 18, FB_COL, family=FAM_MIX, bold=True))
det1 = "跨层先决：字体查询 → 版式系统"
fit("绕行注1", det1, 18, 280)
S.append(text(334, 222, det1, 18, EDGE_COL, family=FAM_MIX))
det2 = "跨层先决：数据计算 → 产物校验"
fit("绕行注2", det2, 18, 280)
S.append(text(740, 752, det2, 18, EDGE_COL, family=FAM_MIX))''')

# 10) 说明卡第 2 行按实际零交叉措辞
rep('n2 = "跨层先决边（字体查询→版式系统、数据计算→产物校验）沿顶部/底部绕行，不穿过任何节点；线线交叉处没有连接点，不构成新的依赖。"',
    'n2 = "两条跨层先决边沿顶部/图底空带绕行（见灰色小注），不穿过任何节点；全图边线零交叉，反馈环走节点上下空带，不与先决边相接。"')

open(p, 'w', encoding='utf-8').write(t)
print('patched6 ok, chars', len(t))
