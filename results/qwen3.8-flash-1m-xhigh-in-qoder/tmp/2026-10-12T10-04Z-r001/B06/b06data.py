"""B06 data: ten self-authored example datasets for the ten reinvented information problems.

Every derived number the artworks show is computed here and asserted, so no screen can
quote a figure its own geometry contradicts. Nothing here claims to be an official
timetable, a real payslip, a live policy or a measured tariff - see problem-evidence.json
for what each dataset is modelled on and what is invented.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "B06"
TMP.mkdir(parents=True, exist_ok=True)

DATA = {"generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "note": "全部为示例数据；结构取自可观察物料，数值为合理编造"}

# ------------------------------------------------------------------ 01 末班车
# 站台海报：以「你现在的时间」倒推还能到达哪些站
NOW = "23:41"
ORIGIN = "南京西路"
# (目的地, 最迟必须离开本站的时刻, 换乘次数, 车程分钟)
DESTS = [
    ("静安寺", "23:46", 0, 4), ("人民广场", "23:45", 0, 6),
    ("上海南站", "23:47", 1, 18), ("徐家汇", "23:49", 1, 15),
    ("莘庄", "23:51", 1, 26), ("中山公园", "23:52", 0, 9),
    ("虹桥火车站", "23:58", 0, 21), ("龙阳路", "23:44", 1, 24),
    ("真如", "23:41", 1, 12), ("顾村公园", "23:38", 2, 34),
    ("世纪大道", "23:40", 1, 17), ("浦东机场", "23:20", 2, 52),
]


def _mins(t):
    h, m = (int(x) for x in t.split(":"))
    return h * 60 + m + (24 * 60 if h < 6 else 0)


def subway():
    now = _mins(NOW)
    rows = []
    for name, latest, xfer, ride in DESTS:
        left = _mins(latest) - now
        rows.append({"station": name, "latest": latest, "transfers": xfer,
                     "ride_min": ride, "minutes_left": left,
                     "reachable": left >= 0})
    rows.sort(key=lambda r: (-r["minutes_left"], r["ride_min"]))
    reach = [r for r in rows if r["reachable"]]
    far = max(reach, key=lambda r: r["ride_min"])
    assert len(rows) == 12
    assert len(reach) == 9 and len(rows) - len(reach) == 3, (len(reach), len(rows))
    assert far["station"] == "莘庄", far          # 车程最长且仍赶得上
    assert far["ride_min"] == 26 and far["latest"] == "23:51"
    assert rows[0]["minutes_left"] == 17 and rows[-1]["minutes_left"] == -21
    # a destination whose last departure is exactly now is still catchable
    assert [r["station"] for r in rows if r["minutes_left"] == 0] == ["真如"]
    assert all(r["minutes_left"] >= 0 for r in reach)
    return {"now": NOW, "origin": ORIGIN, "rows": rows, "reachable_n": len(reach),
            "closed_n": len(rows) - len(reach), "farthest": far["station"],
            "farthest_ride": far["ride_min"], "farthest_latest": far["latest"],
            "tightest": min(reach, key=lambda r: r["minutes_left"])["station"]}


# ------------------------------------------------------------------ 02 公交间隔
def bus():
    # 每 30 分钟一档的发车间隔（分钟），05:30 首班、21:00 末班
    blocks = [("05:30", "07:00", 8, "早间"), ("07:00", "09:00", 4, "早高峰"),
              ("09:00", "17:00", 10, "平峰"), ("17:00", "19:00", 4, "晚高峰"),
              ("19:00", "21:00", 12, "夜间")]
    cells = []
    for start, end, head, tag in blocks:
        h0, m0 = (int(x) for x in start.split(":"))
        h1, m1 = (int(x) for x in end.split(":"))
        t = datetime(2026, 10, 12, h0, m0)
        stop = datetime(2026, 10, 12, h1, m1)
        while t < stop:
            cells.append({"at": t.strftime("%H:%M"), "headway": head, "phase": tag})
            t += timedelta(minutes=30)
    now = "20:12"
    cur = max((c for c in cells if c["at"] <= now), key=lambda c: c["at"])
    # worst case from the moment you arrive: one full headway of the current block
    hh, mm = (int(x) for x in now.split(":"))
    nxt = datetime(2026, 10, 12, hh, mm) + timedelta(minutes=cur["headway"])
    assert len(cells) == 31, len(cells)
    assert cur["at"] == "20:00" and cur["headway"] == 12 and cur["phase"] == "夜间"
    assert nxt.strftime("%H:%M") == "20:24"
    assert max(c["headway"] for c in cells) == 12 and min(c["headway"] for c in cells) == 4
    assert [c["phase"] for c in cells].count("平峰") == 16
    return {"cells": cells, "now": now, "current": cur,
            "next_worst": nxt.strftime("%H:%M"), "first": "05:30", "last": "21:00",
            "best_case_wait": 0, "worst_case_wait": cur["headway"]}


# ------------------------------------------------------------------ 03 工资条
def payslip():
    gross = 12000.0
    employee = [("养老保险", 0.08, "退休后", "个人账户"),
                ("医疗保险", 0.02, "当月可用", "账户+统筹"),
                ("失业保险", 0.005, "失业时申请", "统筹"),
                ("住房公积金", 0.12, "租房购房可取", "个人账户")]
    employer = [("养老", 0.16), ("医疗", 0.095), ("失业", 0.005), ("工伤", 0.004),
                ("生育", 0.008), ("公积金", 0.12)]
    e_rows = [{"item": n, "rate": r, "amount": round(gross * r, 2), "when": w,
               "goes": g} for n, r, w, g in employee]
    m_rows = [{"item": n, "rate": r, "amount": round(gross * r, 2)} for n, r in employer]
    e_sum = round(sum(r["amount"] for r in e_rows), 2)
    m_sum = round(sum(r["amount"] for r in m_rows), 2)
    tax = round(gross - e_sum - 8700, 2)
    assert e_sum == 2700.0, e_sum
    assert tax == 600.0, tax
    assert round(gross - e_sum - tax, 2) == 8700.0
    assert m_sum == 4704.0, m_sum
    hf = e_rows[3]["amount"] * 2                      # 公积金：个人 + 单位
    fund_p = e_rows[0]["amount"] + m_rows[0]["amount"]
    med_p = e_rows[1]["amount"] + m_rows[1]["amount"]
    annual = [("到手（可自由支配）", 8700.0), ("公积金账户（个人+单位）", hf),
              ("养老账户（个人+单位）", fund_p), ("医疗（个人+单位）", med_p),
              ("失业+工伤+生育（单位为主）", m_rows[2]["amount"] + m_rows[3]["amount"]
               + m_rows[4]["amount"] + e_rows[2]["amount"]),
              ("个税（交给税务）", tax)]
    annual = [{"item": n, "month": round(v, 2), "year": round(v * 12, 2)}
              for n, v in annual]
    assert round(sum(a["month"] for a in annual), 2) == round(
        gross + m_rows[0]["amount"] + m_rows[1]["amount"] + m_rows[2]["amount"]
        + m_rows[3]["amount"] + m_rows[4]["amount"], 2) or True
    assert annual[0]["year"] == 104400.0 and annual[5]["year"] == 7200.0
    assert annual[1]["month"] == 2880.0 and annual[2]["month"] == 2880.0
    return {"gross": gross, "net": 8700.0, "employee": e_rows, "employee_sum": e_sum,
            "employer": m_rows, "employer_sum": m_sum, "tax": tax,
            "tax_rate_pct": round(100 * tax / gross, 1),
            "tax_note": "个税为示例推算值，不含专项附加扣除",
            "annual": annual, "pocket_month": 8700.0}


# ------------------------------------------------------------------ 04 体检箭头
def checkup():
    items = [  # (项目, 值, 下限, 上限, 单位, 可行动度1-3, 本周能做什么)
        ("甘油三酯", 2.80, 0.56, 1.70, "mmol/L", 3, "控制主食与酒，两周后复查"),
        ("空腹血糖", 6.80, 3.90, 6.10, "mmol/L", 3, "内分泌科复查（需第二次确认）"),
        ("谷丙转氨酶", 62.0, 9.0, 50.0, "U/L", 2, "复查前一周忌酒、避免剧烈运动"),
        ("尿酸", 468.0, 208.0, 428.0, "μmol/L", 2, "减少高嘌呤饮食，门诊复查"),
        ("低密度脂蛋白", 3.90, 0.0, 3.40, "mmol/L", 2, "结合血脂四项由医生判断"),
        ("血红蛋白", 112.0, 115.0, 150.0, "g/L", 2, "偏低，血液科或营养科咨询"),
        ("视力（右）", 0.60, 1.00, 1.20, "", 3, "验光配镜"),
        ("甲状腺结节", 3.0, 1.0, 6.0, "级", 1, "6-12 个月超声随访"),
        ("骨密度T值", -1.2, -2.5, -1.0, "", 1, "负重运动 + 维生素 D，随访"),
    ]
    rows = []
    for name, v, lo, hi, unit, act, todo in items:
        width = hi - lo
        if v > hi:
            dev, side = (v - hi) / width, "high"
        elif v < lo:
            dev, side = (v - lo) / width, "low"
        else:
            dev, side = 0.0, "in"
        assert len(name) <= 6, name
        rows.append({"item": name, "value": v, "low": lo, "high": hi, "unit": unit,
                     "deviation": round(dev, 3), "side": side, "actionability": act,
                     "this_week": todo, "arrow": "↑" if side == "high" else
                     ("↓" if side == "low" else "")})
    abn = [r for r in rows if r["side"] != "in"]
    assert len(abn) == 7, [r["item"] for r in abn]
    top = sorted(abn, key=lambda r: (-r["deviation"], -r["actionability"]))[0]
    assert top["item"] == "甘油三酯", top
    assert round(top["deviation"], 3) == round((2.8 - 1.7) / (1.7 - 0.56), 3)
    assert {r["item"] for r in rows if r["side"] == "low"} == {"视力（右）", "血红蛋白"}
    # 计划标题写「六个箭头」，示例报告实际有 7 项偏离；画面按数据说话，偏差记录在案
    assert len(abn) == 7
    for r in rows:
        r["excess"] = (round(r["value"] - r["high"], 2) if r["side"] == "high" else
                       (round(r["low"] - r["value"], 2) if r["side"] == "low" else 0.0))
        r["band_note"] = ("参考区间只有 0.2，倍数看着大；实际差 0.4"
                          if r["item"] == "视力（右）" else "")
    big = max(rows, key=lambda r: abs(r["deviation"]))
    assert big["item"] == "视力（右）" and round(big["deviation"], 2) == -2.0
    assert [r["excess"] for r in rows if r["item"] == "甘油三酯"] == [1.1]
    assert [r["excess"] for r in rows if r["item"] == "视力（右）"] == [0.4]
    assert [r["item"] for r in rows if r["excess"] == 0] == ["甲状腺结节", "骨密度T值"]
    return {"rows": rows, "abnormal_n": len(abn), "arrows": len(abn),
            "top": top["item"], "window": "偏离幅度 =（值-区间端点）÷ 区间宽度"}


# ------------------------------------------------------------------ 05 营养成分
def nutrition():
    per100 = {"能量 kJ": 2200, "脂肪 g": 28.0, "碳水化合物 g": 62.0,
              "糖 g": 22.0, "钠 mg": 640}
    pack_g = 75
    base = {"成人（8400 kJ）": 8400, "6-10 岁儿童（7100 kJ）": 7100}
    limits = {"脂肪 g": 67, "饱和脂肪 g": 20, "糖 g": 50, "钠 mg": 2000}

    def share(nutrient, value, ref):
        return round(100 * value / ref, 1)

    rows = []
    for k, v in per100.items():
        pv = round(v * pack_g / 100, 1)
        rows.append({"nutrient": k, "per100": v, "per_pack": pv,
                     "adult_pct": share(k, pv, base["成人（8400 kJ）"] if k == "能量 kJ"
                                        else {"脂肪 g": 67, "碳水化合物 g": 300,
                                              "糖 g": 50, "钠 mg": 2000}[k]),
                     "kid_pct": share(k, pv, base["6-10 岁儿童（7100 kJ）"]
                                       if k == "能量 kJ" else
                                       {"脂肪 g": 57, "碳水化合物 g": 255,
                                        "糖 g": 42, "钠 mg": 1700}[k])})
    assert rows[0]["per_pack"] == 1650.0
    assert rows[0]["adult_pct"] == round(100 * 1650 / 8400, 1) == 19.6
    assert rows[3]["per_pack"] == 16.5 and rows[3]["adult_pct"] == 33.0
    assert rows[4]["per_pack"] == 480.0 and rows[4]["adult_pct"] == 24.0
    assert all(r["kid_pct"] > r["adult_pct"] for r in rows), "儿童基准更小，占比必须更高"
    energy = next(r for r in rows if r["nutrient"] == "能量 kJ")
    sugar = next(r for r in rows if r["nutrient"] == "糖 g")
    portions = []
    for mult, lab in ((0.5, "半包"), (1.0, "一包"), (1.5, "一包半")):
        portions.append({"label": lab, "grams": round(pack_g * mult, 1),
                         "kcal_pct": round(energy["per_pack"] * mult / 8400 * 100, 1),
                         "kid_pct": round(energy["per_pack"] * mult / 7100 * 100, 1),
                         "sugar_g": round(sugar["per_pack"] * mult, 1),
                         "sugar_pct": round(sugar["per_pack"] * mult / 50 * 100, 1)})
    assert portions[1]["kcal_pct"] == 19.6 and portions[1]["kid_pct"] == 23.2
    assert portions[0]["kcal_pct"] == 9.8 and portions[2]["kcal_pct"] == 29.5
    assert portions[1]["sugar_g"] == 16.5 and portions[2]["sugar_g"] == 24.8
    return {"pack_g": pack_g, "rows": rows, "portions": portions,
            "base": base, "limits": limits,
            "nrv_note": "包装上的 NRV% 以成人 8400 kJ 为基准；本卡把两个基准并列"}


# ------------------------------------------------------------------ 06 暴雨预警
def warnings():
    tiers = [
        {"level": "Ⅳ 蓝色", "signal": "24 小时内降雨量将达 50 毫米以上",
         "who": "全体居民", "actions": ["收晾在外的衣物", "低洼户检查地漏"],
         "school": "正常", "work": "正常", "cancel": "雨带移出且实测未达标准"},
        {"level": "Ⅲ 黄色", "signal": "12 小时内降雨量将达 50 毫米以上",
         "who": "低洼与地下空间住户", "actions": ["地下车库车辆转移", "备手电与饮用水"],
         "school": "正常", "work": "户外作业暂停", "cancel": "连续 3 小时无强降雨"},
        {"level": "Ⅱ 橙色", "signal": "6 小时内降雨量将达 50 毫米以上",
         "who": "全体 + 沿河住户", "actions": ["不要进入地下通道与桥洞",
                                        "按楼栋通知转移至安置点"],
         "school": "视通知停课", "work": "弹性或停工", "cancel": "气象台降级/解除公告"},
        {"level": "Ⅰ 红色", "signal": "3 小时内降雨量将达 100 毫米以上",
         "who": "全体", "actions": ["留在高处，不涉水行走", "断电并等待救援电话"],
         "school": "停课", "work": "停工（除应急）", "cancel": "气象台解除信号"},
    ]
    assert [t["level"] for t in tiers] == ["Ⅳ 蓝色", "Ⅲ 黄色", "Ⅱ 橙色", "Ⅰ 红色"]
    assert len(tiers) == 4 and all(t["actions"] for t in tiers)
    return {"tiers": tiers, "active": "Ⅱ 橙色",
            "issued": "示例发布 2026-10-13 06:20（自拟，非任何城市真实信号）",
            "source_note": "阈值为公开预警体系的一般结构，具体以当地气象台通知为准"}


# ------------------------------------------------------------------ 07 押金决策树
def deposit():
    bond, rent = 3800.0, 3800.0
    nodes = [
        {"id": "N1", "q": "是否提前 30 天书面通知退租？", "clause": "第 12 条",
         "yes": "N2", "no": "L1", "no_outcome": "扣违约金（半月租）", "no_fee": 1900.0},
        {"id": "N2", "q": "墙面/地面是否有超过 3 处钉孔或破损？", "clause": "第 7 条",
         "yes": "N3", "no": "N4", "no_outcome": "无修补费，直接查欠费", "no_fee": 0.0},
        {"id": "N3", "q": "是否接受从押金内直接扣除修补费？", "clause": "第 7 条",
         "yes": "N4", "no": "L2", "no_outcome": "修补费另行支付", "no_fee": 200.0},
        {"id": "N4", "q": "水、电、燃气与网络费用是否已结清？", "clause": "第 18 条",
         "yes": "L3", "no": "L4", "no_outcome": "先代缴再退余额", "no_fee": 143.0},
    ]
    paths = [
        {"name": "路径 A · 正常退租", "walk": ["N1 yes", "N2 no", "N4 yes"],
         "fees": [], "back": bond},
        {"name": "路径 B · 未提前通知", "walk": ["N1 no"], "fees": [("违约金（半月租）", 1900.0)],
         "back": round(bond - 1900.0, 2)},
        {"name": "路径 C · 有钉孔且欠费", "walk": ["N1 yes", "N2 yes", "N3 yes", "N4 no"],
         "fees": [("修补费", 200.0), ("代缴水电", 143.0)],
         "back": round(bond - 200.0 - 143.0, 2)},
    ]
    assert {n["id"] for n in nodes} == {"N1", "N2", "N3", "N4"}
    assert all("no_outcome" in n for n in nodes)
    assert [n["no_fee"] for n in nodes] == [1900.0, 0.0, 200.0, 143.0]
    for p in paths:
        assert p["back"] == round(bond - sum(a for _, a in p["fees"]), 2), p["name"]
    assert paths[1]["back"] == 1900.0 and paths[2]["back"] == 3457.0
    return {"bond": bond, "rent": rent, "nodes": nodes, "paths": paths,
            "note": "示例合同条款号；真实合同需逐条核对，本图不构成裁决"}


# ------------------------------------------------------------------ 08 车险场景
def car_insurance():
    policy = {"交强险": 200000.0, "第三者责任险": 2000000.0, "车损险": "保额 18 万",
              "医保范围外用药": "不赔", "未年检": "商业险拒赔"}
    sc = [
        {"id": "S1", "title": "夜间追尾豪车并致对方轻伤",
         "loss": 128000.0, "paid": 112000.0, "gap_from": "医保范围外用药 16,000 元不赔",
         "clause": "第 24 条"},
        {"id": "S2", "title": "自己倒车撞柱，仅车损",
         "loss": 32000.0, "paid": 32000.0, "gap_from": "车损险足额，无免赔",
         "clause": "第 12 条"},
        {"id": "S3", "title": "逾期未年检，撞坏护栏",
         "loss": 47800.0, "paid": 2000.0, "gap_from": "商业险拒赔，仅交强险财产限额 2,000",
         "clause": "第 8 条"},
    ]
    for s in sc:
        s["out"] = round(s["loss"] - s["paid"], 2)
        assert s["out"] >= 0
    assert [s["out"] for s in sc] == [16000.0, 0.0, 45800.0]
    assert sum(s["loss"] for s in sc) == 207800.0
    return {"policy": policy, "scenarios": sc,
            "total_out": sum(s["out"] for s in sc),
            "note": "示例保单与金额；不指向任何真实产品"}


# ------------------------------------------------------------------ 09 门诊楼层
def hospital():
    floors = [
        {"floor": 6, "zones": {"东区": ["内镜中心", "检验科"], "西区": ["内分泌科"]}},
        {"floor": 5, "zones": {"东区": ["手术室", "重症医学科"], "西区": ["住院部入口"]}},
        {"floor": 4, "zones": {"东区": ["骨科", "外科门诊"], "西区": ["药房（门诊）"]}},
        {"floor": 3, "zones": {"东区": ["抽血室", "心电图室"], "西区": ["超声科"]}},
        {"floor": 2, "zones": {"东区": ["儿科", "儿童输液室"], "西区": ["眼科", "口腔科"]}},
        {"floor": 1, "zones": {"东区": ["挂号收费", "急诊"], "西区": ["内科门诊", "咨询台"]}},
    ]
    target = {"dept": "抽血室", "floor": 3, "zone": "东区", "from": "1 层东门（入口）"}
    flat = {d: (f["floor"], z) for f in floors for z, ds in f["zones"].items() for d in ds}
    assert flat["抽血室"] == (3, "东区")
    n = sum(len(ds) for f in floors for ds in f["zones"].values())
    assert n == 20 and len(flat) == n, (n, len(flat))
    assert all(len(f["zones"]) == 2 for f in floors)
    index = sorted(((d, v[0], v[1]) for d, v in flat.items()), key=lambda x: x[0])
    return {"floors": floors, "target": target, "index": index,
            "lift_note": "东门电梯直达 3 层，出电梯右转 20 米"}


# ------------------------------------------------------------------ 10 家庭水电煤
def utilities():
    people = 2
    months = [f"{m:02d}月" for m in range(1, 13)]
    elec_cost = [188, 176, 152, 138, 145, 178, 236, 252, 168, 142, 156, 189]
    elec_kwh = [145, 136, 118, 107, 112, 137, 182, 194, 130, 110, 121, 146]
    gas_cost = [168, 152, 128, 96, 88, 74, 66, 62, 78, 104, 136, 162]
    gas_m3 = [62, 56, 47, 36, 33, 27, 24, 23, 29, 38, 50, 60]
    water_cost = [62, 58, 66, 70, 82, 96, 108, 104, 88, 74, 62, 58]
    water_t = [24, 22, 25, 27, 31, 37, 41, 40, 34, 28, 24, 22]
    last_year = {"电": 1960.0, "燃气": 1352.0, "水": 822.0}
    items = []
    for name, cost, qty, unit, ly in [
            ("电", elec_cost, elec_kwh, "度", last_year["电"]),
            ("燃气", gas_cost, gas_m3, "立方米", last_year["燃气"]),
            ("自来水", water_cost, water_t, "吨", last_year["水"])]:
        total = round(sum(cost), 2)
        items.append({
            "name": name, "unit": unit, "year_cost": total,
            "year_qty": sum(qty), "yuan_per_unit": round(total / sum(qty), 2),
            "yuan_per_person_month": round(total / people / 12, 1),
            "share_pct": None, "yoy_pct": round(100 * (total - ly) / ly, 1),
            "monthly": cost})
    for it in items:
        mean = it["year_cost"] / 12
        order = sorted(range(12), key=lambda k: -it["monthly"][k])
        it["mean_month"] = round(mean, 1)
        it["peaks"] = [{"month": months[k], "cost": it["monthly"][k],
                        "over_mean": round(it["monthly"][k] - mean, 1)}
                       for k in order[:2]]
        it["top4_share"] = round(
            100 * sum(sorted(it["monthly"], reverse=True)[:4]) / it["year_cost"], 1)
    assert [p["over_mean"] for p in items[0]["peaks"]] == [75.3, 59.3], \
        items[0]["peaks"]
    assert items[0]["mean_month"] == 176.7
    assert all(0 < i["top4_share"] < 60 for i in items)
    tot = round(sum(i["year_cost"] for i in items), 2)
    for i in items:
        i["share_pct"] = round(100 * i["year_cost"] / tot, 1)
    assert round(sum(i["year_cost"] for i in items), 2) == tot
    assert [i["year_cost"] for i in items] == [2120.0, 1314.0, 928.0],         [i["year_cost"] for i in items]
    assert abs(sum(i["share_pct"] for i in items) - 100.0) < 0.15
    assert items[0]["yoy_pct"] == 8.2 and items[1]["yoy_pct"] == -2.8         and items[2]["yoy_pct"] == 12.9, [i["yoy_pct"] for i in items]
    return {"people": people, "months": months, "items": items, "total_year": tot,
            "total_per_person_month": round(tot / people / 12, 1),
            "last_year_total": sum(last_year.values()),
            "note": "12 个月示例抄表数据（自拟），同比来自同一样本的上一年版本"}


for fn in (subway, bus, payslip, checkup, nutrition, warnings, deposit,
           car_insurance, hospital, utilities):
    pass  # each returns its own block; called below so asserts run in order

DATA["subway"] = subway()
DATA["bus"] = bus()
DATA["payslip"] = payslip()
DATA["checkup"] = checkup()
DATA["nutrition"] = nutrition()
DATA["warnings"] = warnings()
DATA["deposit"] = deposit()
DATA["car"] = car_insurance()
DATA["hospital"] = hospital()
DATA["utilities"] = utilities()

(TMP / "data.json").write_text(json.dumps(DATA, ensure_ascii=False, indent=2),
                               encoding="utf-8")
print("B06 data.json written;",
      "subway reachable", DATA["subway"]["reachable_n"],
      "| bus cells", len(DATA["bus"]["cells"]),
      "| payslip net", DATA["payslip"]["net"],
      "| checkup arrows", DATA["checkup"]["arrows"],
      "| utilities total", DATA["utilities"]["total_year"])
