"""B03 review fix 2 - case-02 pickup ticket B.

Two real defects found by opening case-02/final.png at 2.6x:
  1. the ticket printed 合计 86 元 while its three lines are 32 + 18 + 12 = 62 元.
     The total was a hard-coded string while ticket A computed its own total,
     so the two tickets used different arithmetic.  Ticket A's format prints the
     LINE subtotal (28 + 16 + 12 = 56), so B must sum the same way.
  2. the specimen is titled "B · 取餐牌（左侧色带）" and the sheet's own size
     table calls it "取餐牌 B", yet the card printed "外带 TAKEAWAY" and
     "预计 11 分钟 · 堂食" - a dine-in label on a pickup-ticket proof.

Fix: give ticket B its own data block, compute the total from it, and make the
card say what the panel says.
"""
import io

p = "build_c02.py"
s = io.open(p, encoding="utf-8").read()
n = 0


def rep(old, new):
    global s, n
    assert old in s, old[:80]
    s = s.replace(old, new, 1)
    n += 1


rep('''MEMBER = {"name": "林 砚",''',
    '''ORDER_B = {"no": "B-0448", "table": "T-07", "mins": 11, "items": [
    ("干炒牛河", "大", 1, 32.0),
    ("白灼菜心", "份", 1, 18.0),
    ("冻柠茶", "少冰", 2, 12.0)]}
MEMBER = {"name": "林 砚",''')

rep('''    tb.append(el("Text", {"color": "#FED7AAFF", "fontSize": "10",
                          "fontFamily": D.MONO, "text": "外带 TAKEAWAY"}))''',
    '''    tb.append(el("Text", {"color": "#FED7AAFF", "fontSize": "10",
                          "fontFamily": D.MONO, "text": "取餐牌 PICKUP"}))''')

rep('''    tb.append(el("Text", {"color": WHITE, "fontSize": "30",
                          "fontFamily": D.MONO, "text": "B-0448"}))''',
    '''    tb.append(el("Text", {"color": WHITE, "fontSize": "30",
                          "fontFamily": D.MONO, "text": ORDER_B["no"]}))''')

rep('''    tb.append(el("Text", {"color": "#FED7AAFF", "fontSize": "10",
                          "fontFamily": D.MONO,
                          "text": "预计 11 分钟 · 堂食"}))''',
    '''    tb.append(el("Text", {"color": "#FED7AAFF", "fontSize": "10",
                          "fontFamily": D.MONO,
                          "text": "台号 %s · 预计 %d 分钟"
                                  % (ORDER_B["table"], ORDER_B["mins"])}))''')

rep('''    for name, spec, qty, price in (
            ("干炒牛河", "大", 1, 32), ("白灼菜心", "份", 1, 18),
            ("冻柠茶", "少冰", 2, 12)):''',
    '''    for name, spec, qty, price in ORDER_B["items"]:''')

rep('''        el("Text", {"color": WHITE, "fontSize": "18",
                    "fontFamily": D.MONO, "text": "86 元"})]))''',
    '''        el("Text", {"color": WHITE, "fontSize": "18",
                    "fontFamily": D.MONO,
                    "text": "%.0f 元"
                            % sum(i[3] for i in ORDER_B["items"])})]))''')

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched", n, "blocks")