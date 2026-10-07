"""Patcher for build_c02.py: ticket column overflow, dimension labels, sheet
height (dead space at the bottom of the proof sheet)."""
import io

p = "build_c02.py"
s = io.open(p, encoding="utf-8").read()
n = 0


def rep(old, new, count=0):
    global s, n
    assert old in s, old[:80]
    s = s.replace(old, new) if not count else s.replace(old, new, count)
    n += 1


# 1. tighten both tickets so the Column fits inside the card
rep('"fontFamily": D.MONO, "letterSpacing": "1.6",\n                          "text": "云吞巷 YUNTUN ALLEY"}))',
    '"fontFamily": D.MONO, "letterSpacing": "1.4",\n                          "text": "云吞巷 YUNTUN"}))')
rep('"text": "取餐牌 PICKUP"}))', '"text": "取餐牌 PICKUP"}))')
for a, b in (('tb.append(el("SizedBox", {"height": "10"}))',
              'tb.append(el("SizedBox", {"height": "10"}))'),):
    rep(a, b)
s = s.replace('el("SizedBox", {"height": "16"})', 'el("SizedBox", {"height": "12"})')
s = s.replace('el("SizedBox", {"height": "20"})', 'el("SizedBox", {"height": "14"})')
s = s.replace('el("SizedBox", {"height": "26"})', 'el("SizedBox", {"height": "22"})')
s = s.replace('el("SizedBox", {"height": "14"})', 'el("SizedBox", {"height": "10"})')
s = s.replace('el("SizedBox", {"height": "12"})', 'el("SizedBox", {"height": "8"})')
s = s.replace('el("SizedBox", {"height": "10"}))', 'el("SizedBox", {"height": "7"}))')
s = s.replace('"fontFamily": D.MONO, "text": ORDER["no"]}))',
              '"fontFamily": D.MONO, "text": ORDER["no"]}))')
s = s.replace('"fontSize": "34",\n                          "fontFamily": D.MONO, "text": ORDER["no"]',
              '"fontSize": "30",\n                          "fontFamily": D.MONO, "text": ORDER["no"]')
s = s.replace('"fontSize": "34",\n                          "fontFamily": D.MONO, "text": "B-0448"}',
              '"fontSize": "30",\n                          "fontFamily": D.MONO, "text": "B-0448"}')
s = s.replace('"padding": "(24,26)"', '"padding": "(18,24)"')
n += 1

# 2. dimension labels: put the size on the rule, drop the floating 90 mm chip
rep('''    F.add(F.at(TA_X - 34, TA_Y - 24, 60, 22,
               el("Text", {"color": INK3, "fontSize": "10",
                           "fontFamily": D.MONO, "textAlign": "CENTER",
                           "text": "90 mm"})))
    F.add(W.dim_h(TA_X, TA_X + TA_W, TA_Y + TA_H + 20, ""))
    F.add(W.dim_v(TA_Y, TA_Y + TA_H, TA_X - 16, "346 px"))''',
    '''    F.add(W.dim_h(TA_X, TA_X + TA_W, TA_Y + TA_H + 22, "250 px = 90 mm",
                  color="#8A8175FF", size=10))
    F.add(W.dim_v(TA_Y, TA_Y + TA_H, TA_X - 18, "346 px", color="#8A8175FF"))''')
rep('F.add(W.dim_h(MC_X, MC_X + MC_W, SC_Y + SC_H + 18, ""))',
    'F.add(W.dim_h(MC_X, MC_X + MC_W, SC_Y + SC_H + 20,\n'
    '                  "340 px = 85 mm", color="#8A8175FF", size=10))')

# 3. kill the dead space: shorter sheet + shorter canvas
rep('CW, CH = 1600, 1120', 'CW, CH = 1600, 980')
rep('F = W.Frame(56, 124, 1488, 940, fill="#FFFFFF", radius=16,',
    'F = W.Frame(56, 124, 1488, 726, fill="#FFFFFF", radius=16,')
rep('k.append(W.rule(56, 1078, 1488, "#D6D3D1FF", 1))',
    'k.append(W.rule(56, 878, 1488, "#D6D3D1FF", 1))')
rep('''    k.append(W.t2("云吞巷（虚构商户）· 本稿为演示用设计交付物，票号、会员资料、"
                  "工单与印厂信息均为自拟，不代表任何真实订单或授权。",
                  56, 1086, size=10, color=INK3, w=1000, h=16))''',
    '''    k.append(W.t2("云吞巷（虚构商户）· 本稿为演示用设计交付物，票号、会员资料、"
                  "工单与印厂信息均为自拟，不代表任何真实订单或授权。",
                  56, 886, size=10, color=INK3, w=1000, h=16))''')
rep('k.append(el("Positioned", {"left": 1000, "top": 1084, "width": 544,',
    'k.append(el("Positioned", {"left": 1000, "top": 884, "width": 544,')

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched", n, "blocks")