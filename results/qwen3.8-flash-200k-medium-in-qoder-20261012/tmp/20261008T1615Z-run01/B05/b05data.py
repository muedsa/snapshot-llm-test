"""B05 唯一数据源：汀州市（虚构）行道树档案、风险分与派生统计。

固定种子、可复算：`python tmp/<run>/B05/b05data.py` 重写 research/*.json。
十件作品的每个数字都从这两份文件读出，不在件内手填。

风险分（跨屏一致的唯一算法）：
    R = 0.30·S_倾斜 + 0.25·S_空洞 + 0.20·S_根系 + 0.15·S_暴露对象 + 0.10·S_历史病害
分级：R>=70 立即处置 / 55-69 限期处置 / 40-54 观察期 / <40 正常
"""
import datetime as dt
import json
import os
import random
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
TMP = ROOT / "tmp" / RID / "B05"
RES = TMP / "research"
RES.mkdir(parents=True, exist_ok=True)

SEED = 20261011
NOW = "2026-10-11T09:20:00+08:00"

STREETS = [
    ("LJ", "临江街道", 3), ("WT", "梧桐街道", 9), ("BL", "白鹭街道", 7),
    ("YQ", "岩前街道", 8), ("NM", "南门街道", 12), ("YY", "云屿街道", 9),
]
ROADS = [
    ("JS", "建设路", "LJ", "香樟"), ("JX", "江滨西路", "LJ", "悬铃木"),
    ("GY", "观海路", "LJ", "榕树"), ("WC", "望潮街", "WT", "香樟"),
    ("WT", "梧桐大道", "WT", "悬铃木"), ("XH", "杏槐路", "WT", "国槐"),
    ("LY", "麓园路", "WT", "复羽叶栾"), ("BL", "白鹭洲路", "BL", "水杉"),
    ("HS", "湖山街", "BL", "香樟"), ("DQ", "堤前巷", "BL", "榕树"),
    ("YP", "岩前路", "YQ", "国槐"), ("YS", "云杉街", "YQ", "银杏"),
    ("ST", "石台账沿路", "YQ", "悬铃木"), ("QZ", "前宅路", "YQ", "香樟"),
    ("NM", "南门街", "NM", "榕树"), ("MZ", "民主路", "NM", "悬铃木"),
    ("XX", "学苑西街", "NM", "复羽叶栾"), ("GY2", "公园路", "NM", "香樟"),
    ("DH", "东湖街", "NM", "水杉"), ("YZ", "屿仔路", "NM", "榕树"),
    ("YY", "云屿大道", "YY", "银杏"), ("HZ", "海角路", "YY", "香樟"),
    ("LT", "龙湖街", "YY", "复羽叶栾"),
]
EXPOSURE = [(0, "内院绿地"), (35, "封闭庭院"), (60, "人行道内侧"),
            (85, "公交站/停车位"), (100, "架空线路下方")]

W = dict(tilt=0.30, cav=0.25, root=0.20, target=0.15, hist=0.10)
FLOW = ["待复核", "已复核", "已派单", "作业中", "待复查", "已归档"]


def band(r):
    if r >= 70:
        return "立即处置"
    if r >= 55:
        return "限期处置"
    if r >= 40:
        return "观察期"
    return "正常"


def s_tilt(deg):
    return min(100.0, deg / 6.0 * 100.0)


def s_cav(pct):
    return min(100.0, pct * 1.6)


def risk_of(t):
    parts = dict(tilt=round(s_tilt(t["tilt_deg"]), 1),
                 cav=round(s_cav(t["cavity_pct"]), 1),
                 root=float(t["pavement_pct"]),
                 target=float(t["exposure"]),
                 hist=float(t["disease_hist"]))
    r = sum(W[k] * parts[k] for k in W)
    return parts, int(round(r))


def build():
    rnd = random.Random(SEED)
    trees, seq = [], {}
    for code, name, street, sp in ROADS:
        cnt = rnd.choice([128, 144, 156, 168, 184, 196, 212])
        for i in range(1, cnt + 1):
            seq[code] = seq.get(code, 0) + 1
            # 悬铃木/榕树更易空心；水杉根系问题少；银杏多在云屿
            sp_here = sp if rnd.random() > 0.22 else rnd.choice(
                ["香樟", "悬铃木", "国槐", "复羽叶栾", "榕树", "银杏", "水杉", "女贞"])
            base_tilt = 0.9 if sp_here in ("悬铃木", "榕树") else 0.6
            p = rnd.random()
            if p < 0.085:                      # 明显倾斜的尾部
                tilt = round(rnd.uniform(4.4, 8.6), 1)
            elif p < 0.235:                    # 可观察到的偏移
                tilt = round(rnd.uniform(1.9, 4.3), 1)
            else:
                tilt = round(max(0.0, rnd.gauss(base_tilt, base_tilt * 0.8)), 1)
            cavity = int(max(0, rnd.gauss(7 if sp_here != "悬铃木" else 17, 12)))
            cavity = min(62, cavity)
            pavement = int(min(96, max(6, rnd.gauss(52, 24))))
            # 倾斜、空洞与铺装破损同源（树龄+根系受限），所以三者正相关
            if tilt > 4.4:
                cavity = min(62, cavity + int(rnd.gauss(17, 7)))
                pavement = min(96, pavement + int(rnd.gauss(19, 8)))
            exp = rnd.choices([e[0] for e in EXPOSURE],
                              [14, 12, 34, 26, 14])[0]
            hist = int(min(90, max(0, rnd.gauss(22, 20))))
            dbh = int(rnd.gauss(34 if sp_here != "榕树" else 44, 12))
            dbh = max(9, min(96, dbh))
            height = round(dbh * 0.22 + rnd.gauss(6.6, 1.9), 1)
            planted = rnd.randint(1978, 2019)
            days_since = int(min(760, max(3, rnd.gauss(210, 175))))
            insp = (dt.date(2026, 10, 11) - dt.timedelta(days=days_since)).isoformat()
            t = dict(
                id="TZ-%s-%04d" % (code, seq[code]), road_code=code, road=name,
                street=street, species=sp_here, dbh_cm=dbh, height_m=height,
                crown_m=round(max(1.6, height * 0.62 + rnd.gauss(0, 0.6)), 1),
                planted=planted, tilt_deg=tilt, cavity_pct=cavity,
                pavement_pct=pavement, exposure=exp,
                exposure_name=dict(EXPOSURE)[exp], disease_hist=hist,
                last_inspect=insp,
                x=round(rnd.uniform(0, 100), 2), y=round(rnd.uniform(0, 100), 2),
                inspector=rnd.choice(["陈拓", "林枝", "周远", "吴荷", "郑山"]),
            )
            t["subs"], t["risk"] = risk_of(t)
            t["band"] = band(t["risk"])
            trees.append(t)

    # 关键那棵树：市民报修 / 档案卡 / 处置单 / 倾斜序列 共用
    f = dict(id="TZ-JS-0417", road_code="JS", road="建设路", street="LJ",
             species="香樟", dbh_cm=62, height_m=14.2, crown_m=9.4, planted=1987,
             tilt_deg=6.8, cavity_pct=34, pavement_pct=78, exposure=85,
             exposure_name="公交站/停车位", disease_hist=40,
             last_inspect="2026-09-28", inspector="陈拓",
             x=41.7, y=36.2)
    f["subs"], f["risk"] = risk_of(f)
    f["band"] = band(f["risk"])
    trees = [t for t in trees if t["id"] != f["id"]] + [f]

    # 倾斜序列：2025-11 → 2026-10，共 12 次读数；近 4 次加速
    series, cur = [], 3.4
    for i, m in enumerate(["2025-11", "2025-12", "2026-01", "2026-02", "2026-03",
                           "2026-04", "2026-05", "2026-06", "2026-07", "2026-08",
                           "2026-09", "2026-10"]):
        step = 0.14 if i < 8 else 0.36
        cur = round(cur + step + (0.02 if i % 3 else -0.01), 2)
        series.append(dict(month=m, tilt_deg=round(cur, 1),
                           rate_deg_per_30d=round(step, 2),
                           wind_kts=int(rnd.gauss(14, 6))))
    series[-1]["tilt_deg"] = f["tilt_deg"]

    # 工单：风险越高越可能已派单；状态机 6 态
    orders = []
    hi = sorted([t for t in trees if t["risk"] >= 55], key=lambda t: -t["risk"])
    for i, t in enumerate(hi):
        st = FLOW[min(len(FLOW) - 1, i % 6 if t["risk"] < 70 else (i % 4))]
        sla = 24 if t["risk"] >= 70 else (72 if t["risk"] >= 55 else 168)
        age = int(rnd.gauss(18 if t["risk"] >= 70 else
                            (52 if t["risk"] >= 55 else 96),
                            12 if t["risk"] >= 70 else (30 if t["risk"] >= 55 else 55)))
        age = max(1, min(sla * 4, age))
        orders.append(dict(
            wo="WO-2026%04d" % (1200 + len(orders)), tree=t["id"], street=t["street"],
            road=t["road"], band=t["band"], state=st, age_hours=max(1, age),
            sla_hours=sla, overdue=max(1, age) > sla,
            crew=rnd.choice(["园林一班", "园林二班", "市政应急三班", "外包·绿建"]),
            opened=(dt.datetime(2026, 10, 11, 9, 20) -
                    dt.timedelta(hours=max(1, age))).isoformat(timespec="minutes")))
    return trees, series, orders


def stats(trees, series, orders):
    def pct(a, b):
        return round(a / b * 100.0, 1)
    bands = {}
    for t in trees:
        bands[t["band"]] = bands.get(t["band"], 0) + 1
    per_street = {}
    for t in trees:
        d = per_street.setdefault(t["street"], dict(total=0, urgent=0, limited=0,
                                                   watch=0, normal=0, mean_risk=0.0,
                                                   crown=0.0))
        d["total"] += 1
        d["mean_risk"] += t["risk"]
        d["crown"] += t["crown_m"] ** 2 * 0.72
        d[{"立即处置": "urgent", "限期处置": "limited", "观察期": "watch",
            "正常": "normal"}[t["band"]]] += 1
    for k, d in per_street.items():
        d["mean_risk"] = round(d["mean_risk"] / d["total"], 1)
        d["crown"] = round(d["crown"], 0)
        d["share_pct"] = pct(d["urgent"], d["total"])
    insp = {}
    for t in trees:
        age = (dt.date(2026, 10, 11) - dt.date.fromisoformat(t["last_inspect"])).days
        b = "<=90 天" if age <= 90 else ("91-180" if age <= 180 else
                                        ("181-365" if age <= 365 else ">365 天"))
        insp[b] = insp.get(b, 0) + 1
    species = {}
    for t in trees:
        species[t["species"]] = species.get(t["species"], 0) + 1
    cav_top = sorted(trees, key=lambda t: -t["risk"])[:20]
    return dict(
        generated_at=NOW, seed=SEED, total=len(trees), roads=len(ROADS),
        streets=len(STREETS), bands=bands, band_pct={k: pct(v, len(trees))
                                                   for k, v in bands.items()},
        per_street=per_street, inspect_age=insp,
        coverage_90d=pct(insp.get("<=90 天", 0), len(trees)),
        coverage_365d=pct(sum(insp.get(k, 0) for k in ("<=90 天", "91-180", "181-365")),
                          len(trees)),
        species=dict(sorted(species.items(), key=lambda kv: -kv[1])),
        crown_area_m2=round(sum(t["crown_m"] ** 2 * 0.72 for t in trees), 0),
        orders=dict(total=len(orders), states={
            s: sum(1 for o in orders if o["state"] == s) for s in
            ["待复核", "已复核", "已派单", "作业中", "待复查", "已归档"]},
            overdue=sum(1 for o in orders if o["overdue"]),
            overdue_urgent=sum(1 for o in orders if o["overdue"] and o["band"] == "立即处置"),
            crew={c: sum(1 for o in orders if o["crew"] == c) for c in
                  sorted({o["crew"] for o in orders})}),
        top20=[dict(id=t["id"], road=t["road"], risk=t["risk"], tilt=t["tilt_deg"],
                    exposure=t["exposure_name"]) for t in cav_top],
        featured=dict(tree=f_next(trees), series=series),
        heat=[[round(100.0 * sum(1 for t in trees if t["risk"] >= 70
                                 and abs(t["x"] - gx * 12.5) < 6.25
                                 and abs(t["y"] - gy * 12.5) < 6.25), 1)
               for gx in range(8)] for gy in range(8)],
    )


def f_next(trees):
    for t in trees:
        if t["id"] == "TZ-JS-0417":
            return t
    raise KeyError("featured tree missing")


def incidents():
    """台风「银杏」过境的后果：已核实/待核实两套数（件-09 用）。"""
    rnd = random.Random(SEED + 7)
    rows = []
    for code, street, size in STREETS:
        v = int(rnd.gauss(21, 9) * size / 6.0)
        rows.append(dict(street=street, street_code=code, fallen=v,
                         fallen_confirmed=int(v * rnd.uniform(0.62, 0.86)),
                         branch=int(rnd.gauss(34, 14)),
                         wire=int(max(0, rnd.gauss(3.4, 2.2)) * size / 6.0),
                         blocked=int(max(0, rnd.gauss(6.5, 3.2)) * size / 6.0),
                         hrs_since=int(rnd.gauss(6.2, 1.4))))
    return rows


def adoption():
    rnd = random.Random(SEED + 3)
    rows = []
    for code, street, size in STREETS:
        rows.append(dict(street=street, trees=int(rnd.gauss(190, 60) * size / 6.0),
                         adopted=int(rnd.gauss(64, 28)),
                         households=int(rnd.gauss(41, 20)),
                         shade_m2=int(rnd.gauss(1420, 520)),
                         events=int(rnd.gauss(9, 4))))
    return rows


def main():
    trees, series, orders = build()
    st = stats(trees, series, orders)
    st["incidents"] = incidents()
    st["adoption"] = adoption()
    (RES / "trees.json").write_text(json.dumps(
        dict(generated_at=NOW, seed=SEED, weights=W, thresholds=[70, 55, 40],
             streets=STREETS, roads=ROADS, count=len(trees), trees=trees),
        ensure_ascii=False), encoding="utf-8")
    (RES / "stats.json").write_text(json.dumps(st, ensure_ascii=False), encoding="utf-8")
    (RES / "orders.json").write_text(json.dumps(
        dict(generated_at=NOW, seed=SEED, flow=FLOW, orders=orders),
        ensure_ascii=False), encoding="utf-8")
    feat = [o for o in orders if o["tree"] == "TZ-JS-0417"]
    f = st["featured"]["tree"]
    print(json.dumps(dict(total=st["total"], bands=st["bands"],
                          coverage_90d=st["coverage_90d"],
                          overdue=st["orders"]["overdue"],
                          featured=dict(risk=f["risk"], band=f["band"],
                                        subs=f["subs"]),
                          series_last=st["featured"]["series"][-1],
                          featured_order=(feat[0] if feat else "无工单")),
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
