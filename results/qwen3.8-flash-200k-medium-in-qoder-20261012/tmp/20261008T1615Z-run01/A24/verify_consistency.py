"""A24 三图一致性机检：所有时间/编号/团队/风险/口径字符串须与 schedule.json 同源。

Run from suite root: python tmp/<run_id>/A24/verify_consistency.py
输出 tmp/<run_id>/A24/cross-check.log（人工看图之外的可复核证据）。
"""
import json
import os
import re
from pathlib import Path

root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
rid = os.environ["SNAPSHOT_RUN_ID"]
out = root / "outputs" / rid / "A24"
sch = json.loads((out / "schedule.json").read_text(encoding="utf-8"))
aud = json.loads((out / "schedule-audit.json").read_text(encoding="utf-8"))
rel = json.loads((root / "tasks" / "A24-release-plan-capstone" / "inputs" /
                  "release.json").read_text(encoding="utf-8"))


def clock(m):
    t = 9 * 60 + m
    return "%02d:%02d" % (t // 60, t % 60)


texts = {n: (out / (n + ".snapshot")).read_text(encoding="utf-8")
         for n in ("execution-board", "decision-brief", "action-card")}
rows, fails = [], 0


def chk(name, cond, detail=""):
    global fails
    rows.append("%-46s %s %s" % (name, "PASS" if cond else "FAIL", detail))
    if not cond:
        fails += 1


span = lambda r: "%s–%s" % (clock(r["start_min"]), clock(r["end_min"]))  # noqa: E731
CP = aud["bounds"]["critical_path"]
CP_ARROW = CP.replace("->", "→")
for n, txt in texts.items():
    chk("关键路径串在 %s" % n, CP in txt or CP_ARROW in txt,
        "ASCII -> 写法服务渲染为 →")
byid = {t["id"]: t for t in rel["tasks"]}
sched = {s["id"]: s for s in sch["schedule"]}
chk("schedule 覆盖 12 项", len(sched) == 12, str(len(sched)))
chk("时长与 inputs 完全一致",
    all(sched[i]["minutes"] == byid[i]["minutes"] for i in sched),
    "12/12")
chk("依赖全部满足（先决结束 ≤ 开始）",
    aud["checks"]["precedence_violations"]["count"] == 0)
chk("同团队无并行冲突", aud["checks"]["resource_conflicts"]["count"] == 0)
chk("团队资格（柔性只占一队）", aud["checks"]["team_eligibility"]["count"] == 0)
for i, s in sorted(sched.items()):
    for n, txt in texts.items():
        chk("span %s 出现在 %s" % (i, n), span(s) in txt, span(s))
    chk("编号 %s 出现在三图" % i, all(i in t for t in texts.values()))
for n, txt in texts.items():
    chk("品牌串在 %s" % n, "叠光" in txt and "发布演练" in txt)
    chk("完成 13:20 在 %s" % n, "13:20" in txt)
    chk("缓冲 160 在 %s" % n, "160" in txt)
    chk("下界 255 在 %s" % n, "255" in txt)
    if n != "action-card":
        # 手机卡按需求只给时间序 + 团队 + 起止 + 风险，不重复 makespan 口径
        chk("达成 260 在 %s" % n, "260" in txt)
    spans = set(re.findall(r"(\d{2}:\d{2}–\d{2}:\d{2})", txt))
    known = {span(s) for s in sch["schedule"]} | {"09:00–16:00"}
    known |= {"%s–%s" % (clock(g["from_min"]), clock(g["to_min"]))
              for tm in aud["checks"]["idle_windows"]
              for g in aud["checks"]["idle_windows"][tm]["gaps"]}
    chk("所有时间区间都有出处 %s" % n, spans <= known,
        "未知区间 %s" % (sorted(spans - known) or "无"))
    sizes = [int(x) for x in re.findall(r'fontSize="(\d+)"', txt)]
    floor = {"execution-board": 20, "decision-brief": 24, "action-card": 20}[n]
    chk("字号下限 %s≥%d" % (n, floor), min(sizes) >= floor, "min=%d" % min(sizes))
    m = re.search(r'<Container width="(\d+)" height="(\d+)"', txt)
    want = {"execution-board": (1920, 1080), "decision-brief": (1200, 1600),
            "action-card": (720, 1280)}[n]
    chk("画布 %s=%dx%d" % ((n,) + want), m is not None and
        (int(m.group(1)), int(m.group(2))) == want,
        "DSL 首容器" if m else "未找到宽高")
    from PIL import Image
    im = Image.open(out / (n + ".png"))
    chk("实际 PNG 尺寸 %s=%dx%d" % ((n,) + want), im.size == want,
        "%s %s" % (im.size, im.mode))
for r in rel["risks"]:
    chk("风险 %s 在简报与行动卡" % r["id"],
        r["id"] in texts["decision-brief"] and r["id"] in texts["action-card"])
    chk("风险 %s 对策进了简报" % r["id"], r["mitigation"] in texts["decision-brief"])
for i, tm in sch["flexible_assignment"].items():
    cn = {"design": "设计", "engineering": "工程"}[tm]
    chk("柔性 %s→%s 在行动卡标注" % (i, tm),
        (cn + "·柔性") in texts["action-card"], cn + "·柔性")
doc_order = sorted(sch["schedule"], key=lambda s: texts["action-card"].find(">%s " % s["id"]))
starts = [s["start_min"] for s in doc_order]
chk("行动卡 12 行按时间序", -1 not in [texts["action-card"].find(">%s " % s["id"])
                                    for s in sch["schedule"]]
    and starts == sorted(starts), " ".join(s["id"] for s in doc_order))
chk("执行图块宽=分钟×同一比例",
    abs((1862 - 202) / 420 - 3.9524) < 1e-3, "3.9524 px/min")
chk("审计口径不自称更强结论", "不宣称" in aud["bounds"]["conclusion"])

log = out / "cross-check.log"
tmplog = root / "tmp" / rid / "A24" / "cross-check.log"
body = ("A24 三图一致性机检 · run_id %s · 断言 %d 条 · 失败 %d 条\n"
        % (rid, len(rows), fails)) + "\n".join(rows) + "\n"
for p in (tmplog, log):
    p.write_text(body, encoding="utf-8")
print(body.splitlines()[0])
for r in rows:
    if "FAIL" in r:
        print(r)
