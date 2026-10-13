"""Work 10 fix: derive every claim in the action list from the 12-month sample.

The hand-written line said the summer months ran "about 100 yuan" above the monthly
mean; the data says 59 and 75. Facts like that must come out of the sample, not from
the person writing the layout.
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent

fp = ROOT / "b06data.py"
t = fp.read_text(encoding="utf-8")
a = '''    tot = round(sum(i["year_cost"] for i in items), 2)'''
b = '''    for it in items:
        mean = it["year_cost"] / 12
        order = sorted(range(12), key=lambda k: -it["monthly"][k])
        it["mean_month"] = round(mean, 1)
        it["peaks"] = [{"month": months[k], "cost": it["monthly"][k],
                        "over_mean": round(it["monthly"][k] - mean, 1)}
                       for k in order[:2]]
        it["top4_share"] = round(
            100 * sum(sorted(it["monthly"], reverse=True)[:4]) / it["year_cost"], 1)
    assert [p["over_mean"] for p in items[0]["peaks"]] == [75.3, 59.3], \\
        items[0]["peaks"]
    assert items[0]["mean_month"] == 176.7
    assert all(0 < i["top4_share"] < 60 for i in items)
    tot = round(sum(i["year_cost"] for i in items), 2)'''
assert t.count(a) == 1
t = t.replace(a, b)
ast.parse(t)
fp.write_text(t, encoding="utf-8")

fp2 = ROOT / "b06works2.py"
u = fp2.read_text(encoding="utf-8")
c = '''    s.text("h", f"三口单位、三种计费方式，先统一成「元 / {ut['people']} 人 · 月」",
           40, 78, 20, INK2)'''
d = '''    s.text("h", f"三种单位、三种计费方式，先统一成「元 / {ut['people']} 人 · 月」",
           40, 78, 20, INK2)'''
assert u.count(c) == 1
u = u.replace(c, d)
e = '''    for i, txt in enumerate([
            "电：夏冬两月各高出全年均值约 100 元，若为空调/采暖，可先看这两档的时段设置；",
            "燃气：全年下降 2.8%，但 11-2 月仍占全年一半，注意壁挂炉设定温度；",
            "自来水：同比 +12.9% 且集中在 6-8 月，先查是否有渗漏或浇灌用水。"]):
        s.text("u", "· " + txt, 40, y + 42 + i * 28, 18, INK2, maxw=w - 90)'''
f = '''    verbs = {"电": "若来自空调或采暖，先看这两个月的时段与温度设置；",
             "燃气": "采暖季占比高，核对壁挂炉设定温度与使用习惯；",
             "自来水": "用量集中在两三个月，先排查渗漏与浇灌用水。"}
    for i, it in enumerate(ut["items"]):
        p1, p2 = it["peaks"]
        s.text("u", f"· {it['name']}：{p1['month']} 与 {p2['month']} 高出月均 "
                    f"{p1['over_mean']:g} / {p2['over_mean']:g} 元，"
                    f"前 4 个月占全年 {it['top4_share']:g}%；{verbs[it['name']]}",
               40, y + 42 + i * 28, 18, INK2, maxw=w - 90)'''
assert u.count(e) == 1
u = u.replace(e, f)
g = '''        s.text("u", "12 个月支出（元）", sx, sy + 100, 17, INK3)'''
h = '''        s.text("u", "12 个月支出（元，按本项最高月归一）", sx, sy + 100, 17, INK3)'''
assert u.count(g) == 1
u = u.replace(g, h)
ast.parse(u)
fp2.write_text(u, encoding="utf-8")
print("work 10 claims now computed from the sample")
