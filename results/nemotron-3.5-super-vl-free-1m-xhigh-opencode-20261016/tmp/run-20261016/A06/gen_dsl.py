import math

W, H = 1600, 1000
NODE = {
    "N01": (90, 300, "需求冻结"),
    "N02": (210, 170, "输入检查"),
    "N03": (210, 430, "字体查询"),
    "N04": (330, 160, "数据计算"),
    "N05": (330, 430, "内容规划"),
    "N06": (450, 300, "版式系统"),
    "N07": (570, 190, "图表生成"),
    "N08": (570, 410, "DSL构建"),
    "N09": (690, 300, "首轮渲染"),
    "N10": (810, 300, "视觉检查"),
    "N11": (930, 300, "问题修复"),
    "N12": (1050, 300, "回归渲染"),
    "N13": (1170, 300, "产物校验"),
    "N14": (1290, 300, "交付归档"),
}
HW, HH = 58, 22  # node half width / height
SOLID = "#6B7280"
FEEDBACK = "#DC2626"

el = []
el.append('<Snapshot background="#FFFFFF" type="png">')
el.append(f'  <SizedBox width="{W}" height="{H}">')
el.append('    <Stack alignment="TOP_LEFT" clipBehavior="NONE">')

# title
el.append('      <Positioned left="40" top="26">')
el.append('        <Text color="#0F172A" fontSize="26" fontStyle="BOLD" fontFamily="Noto Sans CJK SC,Inter">从需求到可复现交付 · 依赖与反馈解释图</Text>')
el.append('      </Positioned>')
el.append('      <Positioned left="40" top="60" width="700">')
el.append('        <Text color="#475569" fontSize="18" fontFamily="Noto Sans CJK SC,Inter" softWrap="true">实心箭头＝先决依赖；红色虚线＝反馈关系（不参与拓扑排序）；交叉线无连接点则不构成新依赖；节点位置体现先后与并行。</Text>')
el.append('      </Positioned>')

def seg(a, b, color, thickness=2.5):
    """straight segment a->b as rotated container"""
    (x1, y1), (x2, y2) = a, b
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length < 0.5:
        return
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    theta = math.atan2(dy, dx)
    c, s = math.cos(theta), math.sin(theta)
    mat = f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"
    # origin at center of the segment box
    el.append(f'      <Positioned left="{mx - length / 2:.1f}" top="{my - thickness / 2:.1f}" width="{length:.1f}" height="{thickness:.1f}">')
    el.append(f'        <Transform matrix="{mat}" origin="({length / 2:.1f},{thickness / 2:.1f})">')
    el.append(f'          <Container width="{length:.1f}" height="{thickness:.1f}" color="{color}"/>')
    el.append(f'        </Transform>')
    el.append(f'      </Positioned>')
    return theta

def arrow(tip, theta, color, size=7):
    a = theta - math.pi / 4
    c, s = math.cos(a), math.sin(a)
    mat = f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"
    tx, ty = tip
    el.append(f'      <Positioned left="{tx - size / 2:.1f}" top="{ty - size / 2:.1f}" width="{size:.1f}" height="{size:.1f}">')
    el.append(f'        <Transform matrix="{mat}" origin="({size / 2:.1f},{size / 2:.1f})">')
    el.append(f'          <Container width="{size:.1f}" height="{size:.1f}" color="{color}" borderRadius="1"/>')
    el.append(f'        </Transform>')
    el.append(f'      </Positioned>')

def dashed_polyline(points, color, dash=8, gap=4, thickness=2.5):
    """draw dashed polyline through points"""
    dist = 0.0
    segs = []
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        L = math.hypot(x2 - x1, y2 - y1)
        segs.append((points[i], points[i + 1], L))
    total = sum(L for _, _, L in segs)
    phase = 0.0
    on = True
    for (p1, p2, L) in segs:
        x1, y1 = p1
        x2, y2 = p2
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        t = 0.0
        while t < L - 0.01:
            seg_on = on
            seg_len = min(dash, L - t) if on else min(gap, L - t)
            if seg_on:
                mx, my = x1 + ux * (t + seg_len / 2), y1 + uy * (t + seg_len / 2)
                theta = math.atan2(uy, ux)
                c, s = math.cos(theta), math.sin(theta)
                mat = f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"
                el.append(f'      <Positioned left="{mx - seg_len / 2:.1f}" top="{my - thickness / 2:.1f}" width="{seg_len:.1f}" height="{thickness:.1f}">')
                el.append(f'        <Transform matrix="{mat}" origin="({seg_len / 2:.1f},{thickness / 2:.1f})">')
                el.append(f'          <Container width="{seg_len:.1f}" height="{thickness:.1f}" color="{color}"/>')
                el.append(f'        </Transform>')
                el.append(f'      </Positioned>')
            t += seg_len
            on = not on

def node(cx, cy, label, nid):
    el.append(f'      <Positioned left="{cx - HW:.1f}" top="{cy - HH:.1f}" width="{2 * HW:.1f}" height="{2 * HH:.1f}">')
    el.append(f'        <Container color="#FFFFFF" border="1.5 SOLID {SOLID}" borderRadius="8"/>')
    el.append(f'      </Positioned>')
    el.append(f'      <Positioned left="{cx - HW + 6:.1f}" top="{cy - 11:.1f}" width="{2 * HW - 12:.1f}" height="22">')
    el.append(f'        <Text color="#0F172A" fontSize="22" fontFamily="Noto Sans CJK SC,Inter" textAlign="CENTER">{label}</Text>')
    el.append(f'      </Positioned>')

# draw nodes
for nid, (cx, cy, label) in NODE.items():
    node(cx, cy, label, nid)

# edge routes (canvas coords)
routes = {
    ("N01", "N02"): [(148, 300), (152, 190)],
    ("N01", "N03"): [(148, 300), (152, 408)],
    ("N02", "N04"): [(268, 170), (272, 166)],
    ("N02", "N05"): [(268, 192), (272, 430)],
    ("N03", "N06"): [(210, 452), (210, 474), (392, 474), (392, 310)],
    ("N05", "N06"): [(388, 430), (392, 290)],
    ("N04", "N07"): [(388, 160), (512, 180)],
    ("N06", "N08"): [(508, 322), (560, 322), (560, 368), (560, 388)],
    ("N07", "N08"): [(628, 212), (660, 212), (660, 350), (600, 350), (600, 388)],
    ("N08", "N09"): [(628, 410), (700, 410), (700, 322)],
    ("N09", "N10"): [(748, 300), (752, 300)],
    ("N10", "N11"): [(868, 300), (872, 300)],
    ("N11", "N12"): [(988, 300), (992, 300)],
    ("N12", "N13"): [(1108, 300), (1112, 300)],
    ("N13", "N14"): [(1228, 300), (1232, 300)],
    ("N04", "N13"): [(388, 182), (388, 130), (1140, 130), (1140, 278)],
}
for (a, b), pts in routes.items():
    theta = None
    for i in range(len(pts) - 1):
        theta = seg(pts[i], pts[i + 1], SOLID)
    arrow(pts[-1], theta, SOLID)

# feedback edges (dashed red)
feedback = {
    ("N09", "N08"): [(748, 322), (748, 470), (600, 470), (600, 432)],
    ("N10", "N08"): [(868, 322), (868, 500), (540, 500), (540, 432)],
}
for (a, b), pts in feedback.items():
    for i in range(len(pts) - 1):
        dashed_polyline([pts[i], pts[i + 1]], FEEDBACK)
    x1, y1 = pts[-2]
    x2, y2 = pts[-1]
    theta = math.atan2(y2 - y1, x2 - x1)
    arrow(pts[-1], theta, FEEDBACK)

# legend
el.append('      <Positioned left="1180" top="44">')
el.append('        <Row mainAxisAlignment="START" crossAxisAlignment="CENTER">')
el.append('          <Container width="24" height="3" color="#6B7280"/>')
el.append('          <Container width="8"/>')
el.append('          <Text color="#374151" fontSize="17" fontFamily="Noto Sans CJK SC,Inter">先决依赖</Text>')
el.append('          <Container width="30"/>')
el.append('          <Container width="24" height="3" color="#DC2626"/>')
el.append('          <Container width="8"/>')
el.append('          <Text color="#DC2626" fontSize="17" fontStyle="BOLD" fontFamily="Noto Sans CJK SC,Inter">反馈关系（不参与拓扑排序）</Text>')
el.append('        </Row>')
el.append('      </Positioned>')

# bottom explanations
el.append('      <Positioned left="40" top="520" width="1100">')
el.append('        <Text color="#0F172A" fontSize="18" fontStyle="BOLD" fontFamily="Noto Sans CJK SC,Inter" softWrap="true">失败后回到构建：首轮渲染（N09）或视觉检查（N10）发现问题后，通过红色反馈边返回 DSL 构建（N08）重作。</Text>')
el.append('      </Positioned>')
el.append('      <Positioned left="40" top="554" width="1100">')
el.append('        <Text color="#0F172A" fontSize="18" fontStyle="BOLD" fontFamily="Noto Sans CJK SC,Inter" softWrap="true">检查发现问题后修复：视觉检查（N10）→ 问题修复（N11）→ 回归渲染（N12）→ 产物校验（N13）→ 交付归档（N14）。</Text>')
el.append('      </Positioned>')
el.append('      <Positioned left="40" top="590" width="1100">')
el.append('        <Text color="#64748B" fontSize="18" fontFamily="Noto Sans CJK SC,Inter" softWrap="true">拓扑层：L0 需求冻结 → L1 输入检查/字体查询 → L2 数据计算/内容规划 → L3 版式系统 → L4 图表生成/DSL构建 → L5 首轮渲染 → L6 视觉检查 → L7 问题修复 → L8 回归渲染 → L9 产物校验 → L10 交付归档；N04→N13 为跨层先决边。</Text>')
el.append('      </Positioned>')

el.append('    </Stack>')
el.append('  </SizedBox>')
el.append('</Snapshot>')

dsl = "\n".join(el)
open("tmp/run-20261016/A06/dependency-map.v1.snapshot", "w", encoding="utf-8").write(dsl)
print("DSL written, chars:", len(dsl))
