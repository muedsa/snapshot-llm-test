#!/usr/bin/env python
# deliver_b05.py 的 META 每项是 8 元组
# (id, 标题, 时刻/场景, 页面/状态, 一句话说明, 用户任务, 产品功能, 与前后件的关系)，
# 原代码只解包了 7 个 → ValueError: too many values to unpack。
# 这里改成 8 个并把第 5 项作为 headline 用到 case.md / gallery 里。
# 启动基准：总任务根 (suite_root)。用法：python fix_deliver_b05_unpack.py
from pathlib import Path

p = Path(__file__).parent / "deliver_b05.py"
s = p.read_text(encoding="utf-8")
subs = [
    ("""    items = [{"id": c, "title": t, "when": w, "form": f, "user_job": u,
              "product_feature": p, "relation": r, "png": a["png"], "dsl": a["dsl"],
              "case_note": f"{OUTD}/{c}/case.md"}
             for (c, t, w, f, u, p, r), a in zip(META, arts)]""",
     """    # META 是 8 元组：(id, 标题, 时刻, 页面/状态, 一句话说明, 用户任务, 功能, 关系)
    items = [{"id": c, "title": t, "when": w, "form": f, "headline": hl,
              "user_job": u, "product_feature": p, "relation": r,
              "png": a["png"], "dsl": a["dsl"],
              "case_note": f"{OUTD}/{c}/case.md"}
             for (c, t, w, f, hl, u, p, r), a in zip(META, arts)]"""),
    ("""| 时刻 / 场景 | {it["when"]} |
| 页面 / 状态 | {it["form"]} |
| 用户任务 | {it["user_job"]} |""",
     """| 时刻 / 场景 | {it["when"]} |
| 页面 / 状态 | {it["form"]} |
| 一句话说明 | {it["headline"]} |
| 用户任务 | {it["user_job"]} |"""),
    ("""    "cases": [{"id": c, "title": t, "when": w, "form": f, "user_job": u,
               "product_feature": p, "relation": r} for c, t, w, f, u, p, r in META],""",
     """    "cases": [{"id": c, "title": t, "when": w, "form": f, "headline": hl,
               "user_job": u, "product_feature": p, "relation": r}
              for c, t, w, f, hl, u, p, r in META],"""),
    ('''        g.append(f"**{it['when']}**　{it['form']}　·　用户任务：{it['user_job']}\\n")''',
     '''        g.append(f"**{it['when']}**　{it['form']}\\n")
        g.append(f"> {it['headline']}\\n")
        g.append(f"用户任务：{it['user_job']}\\n")'''),
]
for a, bb in subs:
    assert s.count(a) == 1, repr(a[:60])
    s = s.replace(a, bb)
p.write_text(s, encoding="utf-8")
print("deliver_b05.py 改为 8 元组解包")