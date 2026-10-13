"""A10 layout patch 1: the evidence panel used an unbounded Row/Col flow, so its
long paragraphs never wrapped and ran past the canvas; row-2 captions were then
clipped by the panel. Switch to a computed text-flow and a wider panel."""
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
p = ROOT / "tmp" / RUN / "A10" / "gen.py"
s = p.read_text(encoding="utf-8")
orig = s


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:70])
    s = s.replace(old, new, count)


# ---------------------------------------------------------------- grid positions
rep('ROW_Y = [168, 512]', 'ROW_Y = [132, 468]')
rep("import argparse", "import argparse" + chr(10) + "import math")

# ---------------------------------------------------------------- title block
rep('''            Text("六格实验板 · 每格 320×240 白底 · 每对只改一个变量 · 滤镜 sigmaX=sigmaY=6",
                 color=TXT_2, fontSize="20", fontFamily=FONT),
            crossAxisAlignment="START"),
        crossAxisAlignment="CENTER"),
    left=num(OX0), top=num(34)))''',
    '''            Text("六格实验板 · 每格 320×240 白底 · 每对只改一个变量 · 滤镜 sigmaX=sigmaY=6",
                 color=TXT_2, fontSize="20", fontFamily=FONT),
            crossAxisAlignment="START"),
        crossAxisAlignment="CENTER"),
    left=num(OX0), top=num(20)))''')

# ---------------------------------------------------------------- captions
rep('''    els.append(label(ox, oy + AH + 10, sub, 20, TXT_2, anchor="left_top", align="LEFT",
                     width=AW, font=FONT))''',
    '''    els.append(label(ox, oy + AH + 6, sub, 18, TXT_2, anchor="left_top", align="LEFT",
                     width=AW, font=FONT, line_height=1.3))''')

# ---------------------------------------------------------------- evidence panel
start = s.index("# ---------------------------------------------------------------- evidence panel")
end = s.index('doc = Snapshot(')
panel_src = '''# ---------------------------------------------------------------- evidence panel
CAP_H = 2 * 18 * 1.3                       # two caption lines under each area
assert ROW_Y[1] - (ROW_Y[0] + AH + 6 + CAP_H) >= 8, "row-1 captions hit row-2 titles"
assert ROW_Y[1] + AH + 6 + CAP_H + 13 <= 774, "row-2 captions collide with the panel"

PX, PY, PW, PH = 40, 774, 1360, 302
PAD = 22
CX0, CWS, CGAP = PX + PAD, 644, 28
FLOW_LOG = []


def flow(col, x, width, y, text, fs, color, font, *, bold=False, align="LEFT", lh=1.3):
    """Estimate wrapped height and emit a width-bounded text node at (x, y)."""
    n_cjk = sum(1 for ch in text if ord(ch) > 0x2E80)
    adv = n_cjk * fs + (len(text) - n_cjk) * fs * 0.55
    lines = max(1, math.ceil(adv / width))
    h = lines * fs * lh
    FLOW_LOG.append((col, text[:18], lines, round(y, 1), round(y + h, 1)))
    return label(x, y, text, fs, color, anchor="left_top", align=align, width=width,
                 font=font, bold=bold, line_height=lh, lines=lines)


els.append(Positioned(C(width=num(PW), height=num(PH), color="#0E1830",
                        borderRadius="12", border=f"1 SOLID {PEDGE}"),
                      left=num(PX), top=num(PY)))

HEAD_Y = PY + 18
els.append(label(PX + PAD, HEAD_Y,
                 "像素与视觉证据（数值由 composite-audit.json 记录，采样自服务返回的 PNG）",
                 20, TXT, anchor="left_top", align="LEFT", width=PW - 2 * PAD,
                 font=FONT, bold=True))
els.append(label(PX + PW - PAD, HEAD_Y + 2,
                 "依据 /reference/parser-tags/ 的 Opacity · ColorFiltered · ImageFiltered · "
                 "BackdropFilter 条目，以及 /guides/painting/ “透明度与颜色滤镜”",
                 16, TXT_3, anchor="right", align="RIGHT", width=640, font=FONT))

LX = PX + PAD
COL_Y = HEAD_Y + 34

colA = []
y = COL_Y
colA.append(flow(1, LX, CWS, y, "A 组 · 重叠内部局部 (180,100) 的理论值与实测", 17, TXT_2,
                 FONT, bold=True)); y += 17 * 1.3 + 8
colA.append(flow(1, LX, CWS, y, f"① 逐元素 alpha 128/255 = {float(A128):.5f}，两次 source-over "
                            f"→ RGB {P1_overlap[0]},{P1_overlap[1]},{P1_overlap[2]}",
                 17, TXT, MONO)); y += 17 * 1.3 + 6
colA.append(flow(1, LX, CWS, y, f"② 组 opacity 0.5（蓝完全不透明盖红，再整组半透明）"
                            f" → RGB {P2_overlap[0]},{P2_overlap[1]},{P2_overlap[2]}",
                 17, TXT, MONO)); y += 17 * 1.3 + 8
colA.append(flow(1, LX, CWS, y,
                 "差别有两处：128/255=0.50196 并不等于 0.5；更主要的是“各自合成”与"
                 "“先叠合再整组透明”不是同一件事。①里蓝色半透明叠在已被红色改过的底色上，"
                 "绿通道被压到 63；②里蓝色完全不透明，组内已不含红色，整组透明后红绿两通道"
                 "都只剩白底回补出的 128。", 17, TXT_2, FONT, lh=1.3))
els += colA

RX = LX + CWS + CGAP
colB = []
y = COL_Y
colB.append(flow(2, RX, CWS, y, "B / C 组 · ③–⑥ 的实际看图判断（非预期描述）", 17, TXT_2,
                 FONT, bold=True)); y += 17 * 1.3 + 8
colB.append(flow(2, RX, CWS, y,
                 "③ 卡内 240×160 区域的条纹糊成竖向色带，SHARP 二字与深色小方块的边缘仍然"
                 "锐利；④ 同一位置改为子树模糊后，BLUR 文字与方块一起糊开，卡片自身的圆角边"
                 "也变软。两格卡片外的条纹同样清晰，差别只落在模糊所作用的那一层。",
                 17, TXT, FONT, lh=1.3)); y += 3 * 17 * 1.3 + 8
colB.append(flow(2, RX, CWS, y,
                 "⑤ 乘色 #F6B94A 后整片变橙并 sigma=6 模糊，柔化边缘越出原形状与实验区外框，"
                 "在深色底上形成橙色外溢光晕；⑥ 同一结果套 r=100 圆裁后，圆周处出现锐利"
                 "截断线，跨过圆周的绿色矩形被整齐切掉，圆外不再有任何橙色扩散。",
                 17, TXT, FONT, lh=1.3))
els += colB

BOTTOM = max(v[4] for v in FLOW_LOG)
assert BOTTOM <= PY + PH - 14, f"panel text overflows: {BOTTOM} > {PY + PH - 14}"
print("panel flow:", json.dumps(FLOW_LOG, ensure_ascii=False), file=sys.stderr)

'''
s = s[:start] + panel_src + s[end:]
assert s != orig
p.write_text(s, encoding="utf-8")
print("patched", p)
