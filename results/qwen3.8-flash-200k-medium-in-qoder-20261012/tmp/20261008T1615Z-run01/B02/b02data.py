"""B02 扳手屋 · 共享数据模型（一件也不许自己编数）。

生成 tmp/<run_id>/B02/data.json：类目 / 412 件馆藏 / 2946 笔 2025 借阅 /
1860 名会员 / 示例会员的在借三件 / 以及十件触点共用的一组反算指标。

运行（总任务根）：
    python tmp/<run_id>/B02/b02data.py
"""
import json
import os
import random
from datetime import date, timedelta
from pathlib import Path

root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
rid = os.environ["SNAPSHOT_RUN_ID"]
tmp = root / "tmp" / rid / "B02"
tmp.mkdir(parents=True, exist_ok=True)

TODAY = date(2026, 10, 10)          # 周六：与所有触点的「今天」一致
LOAN_DAYS = 7
RENEW_DAYS = 5
LATE_FEE = 5.0
MAX_ACTIVE = 3
MEMBER_FEE = {"个人年卡": 180, "家庭年卡": 260, "志愿年卡(免费)": 0}

# 9 类目：count 合计 412；loan_share 合计 1.0；kg_each = 一件同类新工具的用料
CATS = [
    ("EMT", "电动工具", 96, 0.285, 6.4, 0.42, "A"),
    ("PNU", "气动工具", 34, 0.061, 11.8, 0.31, "B"),
    ("HND", "手工作业", 78, 0.171, 1.9, 0.55, "C"),
    ("WOD", "木作设备", 45, 0.116, 24.5, 0.36, "D"),
    ("MTL", "金属加工", 28, 0.068, 31.0, 0.29, "E"),
    ("GDN", "园艺绿化", 42, 0.126, 8.2, 0.48, "F"),
    ("MSR", "测量标定", 33, 0.073, 1.2, 0.61, "G"),
    ("CLN", "清洁养护", 24, 0.063, 5.5, 0.52, "H"),
    ("LIF", "生活辅件", 32, 0.037, 2.6, 0.66, "I"),
]
assert sum(c[2] for c in CATS) == 412
assert abs(sum(c[3] for c in CATS) - 1.0) < 1e-6, sum(c[3] for c in CATS)

NAMES = {
    "EMT": ["充电冲击钻", "曲线锯", "角磨机", "电圆锯", "砂带机", "锂电扳手", "热风枪",
            "电锤", "多功能振荡工具", "台钻", "电木铣", "修边机"],
    "PNU": ["气动钉枪", "空压机 8P", "气动棘轮扳手", "喷枪套装", "气动砂光机", "气铲"],
    "HND": ["棘轮扳手组套", "扭力扳手", "手板锯", "刨子", "凿子组套", "丝锥板牙组",
            "管钳", "拉铆枪", "剥线钳", "水平尺夹", "锤子组套", "螺丝刀组套"],
    "WOD": ["压刨", "平刨", "带锯", "斜切锯", "木工夹群", "钻床支架", "手工锯", "砂光机"],
    "MTL": ["逆变焊机", "等离子切割", "台锯金属", "弯管机", "剪板机", "攻丝机", "磁力钻"],
    "GDN": ["绿篱机", "割灌机", "链锯", "松土机", "高空修枝锯", "草坪打孔机", "手推扫雪板"],
    "MSR": ["激光平水仪", "红外测距仪", "管线探测仪", "经纬仪", "激光标线仪", "角度规",
            "含水率仪"],
    "CLN": ["高压清洗机", "工业吸尘吸水机", "地毯清洗机", "蒸汽清洁机", "地面抛光机"],
    "LIF": ["人字梯 2.8m", "折叠脚手架", "空气压缩机收纳", "安全帽组", "护目镜组",
            "防噪耳罩", "工具箱整理车"],
}

rng = random.Random(20261010)
TOOLS = []
for code, cname, cnt, share, kg, oneway, zone in CATS:
    pool = NAMES[code]
    for i in range(cnt):
        base = pool[i % len(pool)]
        gen = i // len(pool) + 1
        tool = {
            "id": "WH-%s-%03d" % (code, i + 1),
            "name": base if gen == 1 else "%s %d代" % (base, gen),
            "cat": code, "cat_name": cname,
            "shelf": "%s-%d" % (zone, (i // 6) + 1),
            "state": "在馆",
            "value": 60 + (i * 37 + rng.randint(0, 90)) % 3400,
            "service_days": rng.choice([90, 120, 180, 365]),
            "power": ("锂电" if rng.random() < .4 else "交流电") if code == "EMT" else (
                "气动" if code == "PNU" else "手动/无电"),
            "safety_level": "S2" if code in ("EMT", "PNU", "WOD", "MTL") else "S1",
        }
        TOOLS.append(tool)

by_cat = {}
for t in TOOLS:
    by_cat.setdefault(t["cat"], []).append(t)

# 状态：按类目分布放 在借 / 维修中 / 报废待处理，总数与下面 LOANS 的「今日在借」一致
LOANED_TODAY = 63
REPAIR = 11
SCRAP = 4
pick = rng.sample(TOOLS, LOANED_TODAY + REPAIR + SCRAP)
for t in pick[:LOANED_TODAY]:
    t["state"] = "在借"
for t in pick[LOANED_TODAY:LOANED_TODAY + REPAIR]:
    t["state"] = "维修中"
for t in pick[LOANED_TODAY + REPAIR:]:
    t["state"] = "报废待处理"
for t in TOOLS:
    t["next_service"] = (TODAY + timedelta(days=rng.randint(-6, 120))).isoformat()

# 2025 全年 2946 笔借阅，类目分布严格等于 loan_share（最大余数法配平）
TOTAL_LOANS = 2946
alloc, raw = {}, {c[0]: TOTAL_LOANS * c[3] for c in CATS}
for k, v in raw.items():
    alloc[k] = int(v)
rem = TOTAL_LOANS - sum(alloc.values())
for k, v in sorted(raw.items(), key=lambda x: x[1] - int(x[1]), reverse=True)[:rem]:
    alloc[k] += 1
assert sum(alloc.values()) == TOTAL_LOANS

# 逐月权重（千分比，合计 1000）：10 月装修季峰值、12 月年前保养次峰、2 月春节最低
MONTH_W = [x / 1000.0 for x in (52, 43, 68, 89, 101, 96, 84, 78, 92, 121, 83, 93)]
assert abs(sum(MONTH_W) - 1.0) < 1e-9

LOANS = []
cat_pool = [(k, alloc[k]) for k in alloc]
seq = []
for k, n in cat_pool:
    seq += [k] * n
rng.shuffle(seq)
for idx, code in enumerate(seq):
    month = 1
    r = rng.random()
    acc = 0.0
    for mi, w in enumerate(MONTH_W, start=1):
        acc += w
        if r < acc:
            month = mi
            break
    day = rng.randint(1, 28)
    out = date(2025, month, day)
    renewed = rng.random() < 0.213
    overdue = 0
    if rng.random() < 0.118:
        overdue = rng.choice([1, 1, 2, 2, 3, 4, 5, 7, 9, 12, 15, 21])
    tool = rng.choice(by_cat[code])
    LOANS.append({
        "n": idx + 1, "tool": tool["id"], "cat": code,
        "out": out.isoformat(),
        "due": (out + timedelta(days=LOAN_DAYS + (RENEW_DAYS if renewed else 0))).isoformat(),
        "ret": (out + timedelta(days=LOAN_DAYS + (RENEW_DAYS if renewed else 0)
                                + overdue)).isoformat(),
        "renewed": renewed, "overdue": overdue,
        "member": "WH-M-%04d" % rng.randint(1, 1860),
    })

# 示例会员：家庭年卡，手上三笔在借，其中一笔逾期 4 天（触点 04/05/03 共用这同一条记录）
active_tools = [next(t for t in TOOLS if t["state"] == "在借" and t["cat"] == c)
                for c in ("EMT", "HND", "GDN")]
MEM0 = {
    "id": "WH-M-0417", "name": "周敏", "card": "家庭年卡", "fee": 260,
    "since": "2023-04-09", "expires": "2026-12-31", "household": 3,
    "shelf_zone": "白鹤岭馆", "phone": "138****4127",
    "safety_101": "2024-03-16 已通过",
}
ACTIVE = []
for k, t in enumerate(active_tools):
    outd = TODAY - timedelta(days=[9, 4, 2][k])
    due = outd + timedelta(days=LOAN_DAYS)
    ACTIVE.append({
        "tool": t["id"], "name": t["name"], "cat": t["cat"], "cat_name": t["cat_name"],
        "out": outd.isoformat(), "due": due.isoformat(),
        "renewed": [True, False, False][k],
        "days_left": (due - TODAY).days,
        "overdue_days": max(0, -(due - TODAY).days),
    })
ACTIVE[0]["due"] = (TODAY - timedelta(days=4)).isoformat()
ACTIVE[0]["days_left"] = -4
ACTIVE[0]["overdue_days"] = 4
ACTIVE[0]["renew_used"] = True
ACTIVE[0]["note"] = "续借额度已用尽"
for a in ACTIVE:
    a["late_fee"] = round(a["overdue_days"] * LATE_FEE, 2)
    a["due_after_renew"] = a["due"] if a["renewed"] else (
        date.fromisoformat(a["due"]) + timedelta(days=RENEW_DAYS)).isoformat()

# 汇总指标：全部由上面的表反算，图上任何数字都要能回到这里
def cat_loans(code):
    return sum(1 for l in LOANS if l["cat"] == code)

per_cat = []
for code, cname, cnt, share, kg, oneway, zone in CATS:
    n = cat_loans(code)
    od = sum(1 for l in LOANS if l["cat"] == code and l["overdue"] > 0)
    per_cat.append({
        "code": code, "name": cname, "shelf_zone": zone, "count": cnt,
        "loans_2025": n, "share": round(n / TOTAL_LOANS, 4),
        "overdue_rate": round(od / n, 4), "kg_each": kg, "one_time": oneway,
        "avoid_buy": round(n * oneway),
        "tools_in_borrow": sum(1 for t in TOOLS if t["cat"] == code and t["state"] == "在借"),
    })

monthly = []
for mi in range(1, 13):
    mm = "%04d-%02d" % (2025, mi)
    monthly.append({"month": mi, "loans": sum(1 for l in LOANS if l["out"][:7] == mm)})

D = {
    "brand": {
        "name": "扳手屋", "en": "WRENCH HOUSE TOOL LIBRARY",
        "tagline": "借一次，胜过买十次",
        "sites": ["白鹤岭馆（主馆 + 公共工坊）", "望江驿（社区服务站取还柜）"],
        "fiction_notice": "本品牌、地址、电话、人名与全部数据均为虚构演示内容",
        "phone": "0000-812-3344",
        "hours": {"days": "周二至周日", "open": "09:00", "close": "20:00",
                  "closed_note": "周一馆内保养"},
        "rules": {"member_fee": MEMBER_FEE, "deposit": 0, "loan_days": LOAN_DAYS,
                  "renew_days": RENEW_DAYS, "late_fee_per_day": LATE_FEE,
                  "max_active": MAX_ACTIVE, "safety_101_min": 40,
                  "suspend_days": 15, "today": TODAY.isoformat(),
                  "repair_by": "正常使用损耗由馆方负责维修与保养",
                  "return_point": "归还口在服务台左侧"},
        "programs": ["第一个星期五 · 开放工坊", "季度修理市集", "技能分享课", "缝补圈"],
    },
    "cats": [{"code": c[0], "name": c[1], "count": c[2], "share": c[3], "kg_each": c[4],
              "one_time": c[5], "zone": c[6], "names": NAMES[c[0]]} for c in CATS],
    "tools": TOOLS,
    "loans_2025": LOANS,
    "member": MEM0,
    "active_loans": ACTIVE,
    "summary": {
        "total_loans": TOTAL_LOANS,
        "renewed": sum(1 for l in LOANS if l["renewed"]),
        "overdue_loans": sum(1 for l in LOANS if l["overdue"] > 0),
        "overdue_days_sum": sum(l["overdue"] for l in LOANS),
        "late_fee_yuan": round(sum(l["overdue"] for l in LOANS) * LATE_FEE, 2),
        "members": 1860,
        "in_borrow_now": LOANED_TODAY, "in_repair_now": REPAIR, "scrap_now": SCRAP,
        "available_now": 412 - LOANED_TODAY - REPAIR - SCRAP,
        "peak_month": max(monthly, key=lambda x: x["loans"]),
        "per_cat": per_cat,
        "monthly": monthly,
    },
}
D["summary"]["avoid_buy_total"] = sum(p["avoid_buy"] for p in per_cat)
D["summary"]["kg_saved_total"] = round(sum(p["avoid_buy"] * p["kg_each"] for p in per_cat), 1)
D["summary"]["renew_rate"] = round(D["summary"]["renewed"] / TOTAL_LOANS, 4)
D["summary"]["overdue_rate"] = round(D["summary"]["overdue_loans"] / TOTAL_LOANS, 4)
D["summary"]["loans_per_member"] = round(TOTAL_LOANS / 1860, 2)

# ---------------- 安全政策（馆方自定的条文，不是台账统计） ----------------
# 分级规则来自工具表本身：safety_level=S2 的类目为 EMT/PNU/WOD/MTL。
S2_CATS = sorted({t["cat"] for t in TOOLS if t["safety_level"] == "S2"})
S1_N = sum(1 for t in TOOLS if t["safety_level"] == "S1")
S2_N = len(TOOLS) - S1_N
D["safety"] = {
    "source": "馆方自定条文（虚构演示品牌），分级依据为工具表 safety_level 字段",
    "levels": {
        "S1": {"name": "基础防护", "tools": S1_N,
               "note": "手动与低风险工具：护目镜按工况佩戴，无需预约教学"},
        "S2": {"name": "强制防护", "tools": S2_N, "cats": S2_CATS,
               "note": "电动、气动、木作与金属加工机械：须先通过 Safety 101，作业时护目镜与耳塞强制"},
    },
    "ppe": [
        {"item": "护目镜", "s1": "按工况", "s2": "强制", "note": "切、磨、钻、喷一律佩戴"},
        {"item": "防尘口罩", "s1": "—", "s2": "木作/金属强制", "note": "砂切类作业另配"},
        {"item": "隔音耳塞", "s1": "—", "s2": "强制", "note": "气动与砂切噪声最大"},
        {"item": "防割手套", "s1": "搬运时", "s2": "仅限搬运", "note": "旋转与往复作业时禁戴，见禁令 02"},
        {"item": "工作服/围裙", "s1": "建议", "s2": "强制", "note": "收袖口、不系宽松下摆"},
        {"item": "长发束起 / 摘首饰", "s1": "强制", "s2": "强制", "note": "绞卷风险与手套无关，一律执行"},
    ],
    "prohibitions": [
        "未通过 Safety 101 不得借出 S2 类工具，卡上会注明通过日期。",
        "旋转、往复、砂切类作业中禁戴线手套，禁穿宽松衣袖——绞卷比割伤更快。",
        "不得拆除防护罩、锁扣、限位与急停装置；缺件即停借，交回馆内登记。",
        "不得在有易燃液体、粉尘或潮湿的地面使用交流电与气动工具。",
        "台钻、带锯、空压机等需双手操作的大型 S2 设备，不得单人搬运或独自使用。",
        "出现异响、异味、火花或外壳发热立即停机，交回馆内报修，不得自行拆修。",
    ],
    "cat_notes": {
        "EMT": "锂电工具也要当通电对待：拔电池后再换钻头；电池鼓包、发烫立即退回。",
        "PNU": "气管先卸压再接头；空压机不得对人身吹扫，气流可把碎屑压进皮肤。",
        "HND": "手工具也要检查：柄裂、头松、刃口卷边即停用，用前花 10 秒看一眼。",
        "WOD": "台锯/带锯推料用推杆，手距刃口 100 mm 以内必须停；木屑要及时清。",
        "MTL": "金属切屑锋利且烫，冷却后再收拾；砂轮片有额定转速，不得超配。",
        "GDN": "链锯与绿篱机需双手握持，加油在冷机状态下进行。",
        "MSR": "激光类量具不得对眼；高处测量用磁吸或三脚架，不单手伸臂。",
        "CLN": "高压清洗机先确认喷嘴朝向，禁止对人、对插座与配电箱喷射。",
        "LIF": "梯具按额定载荷使用，人字梯顶部两档不得站人，需有人扶梯。",
    },
    "signoff": {
        "title": "签字确认",
        "fields": ["会员签名", "会员编号", "日期", "馆方见证（志愿者）签名"],
        "statement": "我已读完本页，理解 S2 工具须先通过 Safety 101，并同意按上述防护与禁令使用；"
                     "工具损坏或异常当日交回并登记。",
    },
}

# ---------------- 年报口径（case-08）：只从台账反算，不新增任何数字 ----------------
_state_n = {}
for t in TOOLS:
    _state_n[t["state"]] = _state_n.get(t["state"], 0) + 1
_tool_loans = {}
for l in LOANS:
    _tool_loans[l["tool"]] = _tool_loans.get(l["tool"], 0) + 1
_by_id = {t["id"]: t for t in TOOLS}
top_tools = []
for tid, n_ in sorted(_tool_loans.items(), key=lambda kv: (-kv[1], kv[0]))[:8]:
    t = _by_id[tid]
    top_tools.append({"id": tid, "name": t["name"], "cat": t["cat"], "cat_name": t["cat_name"],
                      "loans": n_, "share": round(n_ / TOTAL_LOANS, 4), "state": t["state"],
                      "shelf": t["shelf"], "value": t["value"],
                      "power": t["power"], "safety_level": t["safety_level"]})
# 各类目平均购置价（台账 tools[].value 的算术平均），只用于折算「避免重复购买」省下的钱
_cat_val = {}
for code, _cn, _c, _s, _k, _o, _z in CATS:
    vs = [t["value"] for t in TOOLS if t["cat"] == code]
    _cat_val[code] = round(sum(vs) / len(vs))
# 单件编号最高只有 18 次（全馆均值 7.15），按单件排名读不出结论；
# 同型号各代合并后的「机型」排名才是年报里能指导采购的那一行。
_model_units, _cat_safety = {}, {}
for t in TOOLS:
    _model_units[(t["cat"], t["name"].split(" ")[0])] = \
        _model_units.get((t["cat"], t["name"].split(" ")[0]), 0) + 1
    _cat_safety[t["cat"]] = t["safety_level"]
_ml = {}
for tid, n_ in _tool_loans.items():
    t = _by_id[tid]
    key = (t["cat"], t["name"].split(" ")[0])
    _ml[key] = _ml.get(key, 0) + n_
top_models = []
for (code, base), n_ in sorted(_ml.items(), key=lambda kv: (-kv[1], kv[0]))[:6]:
    units = _model_units[(code, base)]
    top_models.append({"cat": code, "name": base, "loans": n_,
                       "share": round(n_ / TOTAL_LOANS, 4), "units": units,
                       "per_unit": round(n_ / units, 1), "safety_level": _cat_safety[code]})
avoided_value = sum(p["avoid_buy"] * _cat_val[p["code"]] for p in per_cat)
D["report"] = {
    "fiscal_year": 2025,
    "states": _state_n,
    "top_tools": top_tools,
    "top_models": top_models,
    "top_tools_share": round(sum(x["loans"] for x in top_tools) / TOTAL_LOANS, 4),
    "loans_per_tool": round(TOTAL_LOANS / len(TOOLS), 2),
    "active_members_with_loans": len({l["member"] for l in LOANS}),
    "monthly": monthly,
    "trough_month": min(monthly, key=lambda x: x["loans"]),
    "q_totals": [{"q": q, "loans": sum(x["loans"] for x in monthly
                                       if (x["month"] - 1) // 3 + 1 == q)} for q in (1, 2, 3, 4)],
    "cat_value_avg": _cat_val,
    "avoided_value_yuan": avoided_value,
    "late_fee_yuan": D["summary"]["late_fee_yuan"],
    # 台账没有会员卡型构成，也没有采购/维修发票流水，所以会费收入与维修支出无法折算。
    # 年报上不写这两个数，而不是编一个看起来合理的数。
    "not_reportable": [
        "会费总收入：台账未提供 1860 名会员的卡型构成，无法折算",
        "维修实际支出：台账只有「正常使用损耗由馆方负责」条款，无采购与维修发票流水",
        "捐赠折算：无捐赠记录",
    ],
}

# ---------------- 逐件档案明细（case-09 用）----------------
# 注意：data.json 原本只有每件工具的当前状态与保养周期，没有购入/维修流水。
# 档案卡要印「这台机器的历史」，所以这里为演示品牌补一段逐件台账：
# 用与主 rng 独立的 Random("ledger:"+id) 生成，不扰动上面任何已核对过的指标。
LEDGER_NOTE = ("购入/维修/保养流水为虚构演示品牌的自造台账明细（不是服务返回数据）；"
               "编号、库位、状态、保养周期、动力与安全级仍取自上面的工具表")
_FAULT = {
    "锂电": ["电池包鼓包，已整组更换", "开关触点烧蚀，换开关", "碳刷更换（例行）", "夹头打滑，换夹头"],
    "交流电": ["碳刷更换（例行）", "电源线护套破损，重压接头", "轴承异响，换轴承", "齿轮箱漏油，补油封"],
    "气动": ["密封圈漏气，换密封包", "换向阀卡滞，清洗并加注气动油", "气管接头滑丝，更换接头"],
    "手动/无电": ["刃口重磨", "木柄开裂，换柄", "除锈上油（例行）", "量具送检归零"],
}
_WHO = ["维修角 · 李", "维修角 · 吴", "维修角 · 陈", "厂家（保内返修）"]


def ledger_for(t):
    r = random.Random("ledger:" + t["id"])
    purchased = date(2019 + r.randint(0, 6), r.randint(1, 12), r.randint(1, 28))
    rows = [{"date": purchased.isoformat(), "kind": "购入",
             "text": "购入，台账登记价 ¥%d，供应商为市内经销商（虚构）" % t["value"],
             "who": "馆方"}]
    dcur = purchased + timedelta(days=t["service_days"])
    while dcur < TODAY:
        if r.random() < 0.62:
            rows.append({"date": dcur.isoformat(), "kind": "保养",
                         "text": "例行保养：清洁、润滑、紧固，护罩与限位复位",
                         "who": r.choice(_WHO[:3])})
        if r.random() < 0.26:
            rows.append({"date": (dcur + timedelta(days=r.randint(4, 60))).isoformat(),
                         "kind": "维修", "text": r.choice(_FAULT[t["power"]]),
                         "who": r.choice(_WHO)})
        dcur += timedelta(days=t["service_days"])
    if t["state"] == "维修中":
        rows.append({"date": (TODAY - timedelta(days=r.randint(1, 6))).isoformat(),
                     "kind": "报修", "text": "会员归还时检出异常，已挂「停止借出」牌，"
                                             "等维修角排期", "who": "服务台"})
    if t["state"] == "报废待处理":
        rows.append({"date": (TODAY - timedelta(days=r.randint(8, 40))).isoformat(),
                     "kind": "停用", "text": "维修评估后判定不经济，转报废待处理，"
                                             "库位保留至处置日", "who": "维修角 + 理事会"})
    rows.sort(key=lambda x: x["date"], reverse=True)
    return {"id": t["id"], "purchased": purchased.isoformat(),
            "age_years": round((TODAY - purchased).days / 365.0, 1),
            "loans_2025": sum(1 for l in LOANS if l["tool"] == t["id"]),
            "rows": rows}


_led_ids = []
for _st in ("维修中", "在借", "在馆", "报废待处理"):
    _led_ids += [t["id"] for t in TOOLS if t["state"] == _st][:3]
D["ledger"] = {"note": LEDGER_NOTE, "tools": {}, "ids": _led_ids}
for tid in _led_ids:
    D["ledger"]["tools"][tid] = ledger_for(_by_id[tid])

out = tmp / "data.json"
out.write_text(json.dumps(D, ensure_ascii=False), encoding="utf-8")
print(out.relative_to(root).as_posix(),
      "tools=%d loans=%d cats=%d avoid=%d kg=%.1f od=%.3f renew=%.3f peak=%s avail=%d"
      % (len(TOOLS), len(LOANS), len(per_cat), D["summary"]["avoid_buy_total"],
         D["summary"]["kg_saved_total"], D["summary"]["overdue_rate"],
         D["summary"]["renew_rate"], D["summary"]["peak_month"],
         D["summary"]["available_now"]))
