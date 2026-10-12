"""B06 数据生成器：一次生成十件共用的演示数据与派生量。

设计纪律：
1. 固定种子（SEED=20261011），任何随机量都可复算；不随机就写成字面常量，
   常量即"我拟的合理示例"，在 problem-evidence.json 里逐条标注来源类型。
2. 所有派生量（月均、每 100 g 单价、偏差度、降速日、封顶时长…）在这里算完，
   caseNN.py 只负责取数和排版，避免十处各算各的、口径漂移。
3. 输出 tmp/<run>/B06/research/demo.json，十件共用同一个文件。

用法（总任务根下）：python tmp/<run_id>/B06/b06data.py
"""
import json
import math
import os
import random
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "tmp" / RID / "B06" / "research"
SEED = 20261011


def hhmm(mins):
    m = int(round(mins)) % (24 * 60)
    return "%02d:%02d" % (m // 60, m % 60)


def mins(s):
    h, m = s.split(":")
    return int(h) * 60 + int(m)


# ---------- 件-01 服药钟点 ----------
def case01():
    """把"一日三次"翻译成钟点：以每 8 小时为骨架，再检查落不落在清醒窗口里。

    规则口径（common_rule_needs_check）：一日三次＝每 8 小时一次，不是跟着三餐；
    空腹＝餐前 1 小时或餐后 2 小时；缓释片不可掰开。
    """
    wake, sleep = mins("07:00"), mins("23:00")
    window = sleep - wake                      # 清醒 16 h
    drugs = [
        {"id": "D1", "name": "阿莫西林胶囊", "raw": "一日三次", "interval_h": 8,
         "dose": "1 粒", "note": "随餐或餐后，整粒吞服", "first": mins("07:00")},
        {"id": "D2", "name": "布洛芬缓释胶囊", "raw": "一日二次", "interval_h": 12,
         "dose": "1 粒", "note": "缓释剂型，不可掰开", "first": mins("08:00")},
        {"id": "D3", "name": "奥美拉唑肠溶胶囊", "raw": "一日一次·空腹", "interval_h": 24,
         "dose": "1 粒", "note": "早餐前 1 小时，空腹", "first": mins("06:00")},
    ]
    for d in drugs:
        step = d["interval_h"] * 60
        n = int(math.floor(window / step)) + 1
        pts = [d["first"] + i * step for i in range(n)]
        inside = [p for p in pts if wake <= p <= sleep]
        # 空腹剂按口径落在早餐前 1 小时，可能早于清醒窗口起点：这不是错误，
        # 而是要提醒"这天得把闹钟设到 06:00"，件-01 里作为显式结论出现。
        d["before_window"] = bool(pts) and (not inside)
        if not inside:
            inside = pts[:1]
        d["times"] = [hhmm(p) for p in inside]
        d["n_doses"] = len(inside)
        # 等间隔装不进清醒窗口时，最后一针到次日第一针之间会拉长
        gaps = []
        circ = inside + [p + 24 * 60 for p in inside]
        for i in range(len(inside)):
            gaps.append((circ[i + 1] - circ[i]) / 60.0)
        d["gap_h"] = [round(g, 1) for g in gaps]
        d["min_gap_h"] = round(min(gaps), 1) if gaps else None
        d["overnight_gap_h"] = round(gaps[-1], 1) if gaps else None
        d["fits_evenly"] = all(abs(g - d["interval_h"]) < 0.1 for g in gaps)
    # 相对"现在"的进度：以演示时刻 14:05 计
    now = mins("14:05")
    for d in drugs:
        nxt = None
        for t in d["times"]:
            if mins(t) > now:
                nxt = mins(t)
                break
        d["next"] = hhmm(nxt) if nxt is not None else d["times"][0]
        nxt_abs = nxt if nxt is not None else mins(d["times"][0]) + 24 * 60
        d["wait_h"] = round((nxt_abs - now) / 60, 1)
        done = [t for t in d["times"] if mins(t) <= now]
        d["taken_today"] = len(done)
    return {"wake": hhmm(wake), "sleep": hhmm(sleep), "window_h": window / 60,
            "now": hhmm(now), "drugs": drugs}


# ---------- 件-02 末班车倒推 ----------
def case02():
    """末班时刻只给一个数；从"必须几点到家"倒推最迟出发时刻。"""
    last_train = mins("23:41")          #  observed 形式的告示：末班 23:41
    ride_min = 26                        # 本站到终点方向目标站，6 站 + 停站
    transfer_walk = 5
    second_ride = 14                     # 换乘后另一线
    exit_walk = 9                        # 出站到家
    buffer = 6                           # 闸机前刷卡排队 + 车门警示
    # 从"必须几点到家"倒推：末班时刻 + 各段 = 到家时刻
    home_at = (last_train + ride_min + transfer_walk + second_ride + exit_walk) % (24 * 60)
    segs = [
        {"k": "末班车发车", "v": hhmm(last_train), "d": 0, "kind": "anchor"},
        {"k": "车上运行", "v": "%d min" % ride_min, "d": ride_min, "kind": "ride"},
        {"k": "换乘走行", "v": "%d min" % transfer_walk, "d": transfer_walk, "kind": "walk"},
        {"k": "二线乘车", "v": "%d min" % second_ride, "d": second_ride, "kind": "ride"},
        {"k": "出站到家", "v": "%d min" % exit_walk, "d": exit_walk, "kind": "walk"},
    ]
    total = sum(s["d"] for s in segs)
    # 正向：要赶上这班，人必须在站台上车的时刻
    must_reach_platform = (last_train - buffer) % (24 * 60)
    walk_in = 12                          # 当前位置走到该站
    must_leave_now = (must_reach_platform - walk_in) % (24 * 60)
    check_at = mins("22:55")              # 我给自己定的"这个点还不动身就危险了"
    slack = (must_leave_now - check_at) % (24 * 60)
    return {"last_train": hhmm(last_train), "segs": segs, "total_min": total,
            "home_at": hhmm(home_at), "crosses_midnight": home_at < last_train,
            "buffer": buffer, "must_reach_platform": hhmm(must_reach_platform),
            "walk_in": walk_in, "must_leave_now": hhmm(must_leave_now),
            "check_at": hhmm(check_at), "slack_min": slack,
            "risk_note": "缓冲 6 min 是我给的保守值，不含临时限流与末班加班车"}


# ---------- 件-03 房租真实年成本 ----------
def case03():
    """月租不可比：把押金占用、中介费、物业、免租期、通勤都折进 12 个月。"""
    commute_hours_per_trip = 1.0 / 60     # 分钟→小时
    time_value = 30                       # 元/小时，我自己定的机会成本口径
    extra_util = 180                      # 元/月 水电网络均摊（三套同口径，仍列出）
    a = [
        {"id": "A", "name": "同泰新苑 主卧", "rent": 2780, "dep_n": 1, "prepay_n": 3,
         "agency_pct": 1.0, "prop_m": 0, "free_days": 0, "commute": 22, "util_m": 240},
        {"id": "B", "name": "纺织厂宿舍 单间", "rent": 2150, "dep_n": 2, "prepay_n": 1,
         "agency_pct": 0.5, "prop_m": 65, "free_days": 15, "commute": 41, "util_m": 190},
        {"id": "C", "name": "滨江旧改 隔断间", "rent": 1980, "dep_n": 1, "prepay_n": 3,
         "agency_pct": 1.0, "prop_m": 40, "free_days": 7, "commute": 55, "util_m": 210},
    ]
    days = 365
    for x in a:
        r = x["rent"]
        x["deposit"] = r * x["dep_n"]
        x["first_pay"] = r * x["prepay_n"]
        x["agency"] = round(r * x["agency_pct"])
        x["prop_y"] = x["prop_m"] * 12
        x["util_y"] = x["util_m"] * 12
        x["rent_paid_y"] = round(r * (days - x["free_days"]) / 30.42)
        x["free_saved"] = round(r * x["free_days"] / 30.42)
        x["commute_y_min"] = x["commute"] * 2 * 22 * 12
        x["commute_y_h"] = round(x["commute_y_min"] / 60, 1)
        x["commute_cost_y"] = round(x["commute_y_min"] / 60 * time_value)
        # 现金流：签约当月一次拿出押金+首期+中介费
        x["sign_out"] = x["deposit"] + x["first_pay"] + x["agency"]
        x["total_year"] = (x["rent_paid_y"] + x["prop_y"] + x["util_y"]
                           + x["agency"] + x["commute_cost_y"])
        x["real_month"] = round(x["total_year"] / 12)
        x["ratio_to_rent"] = round(x["real_month"] / r * 100, 1)
        # 押金是占用不是消耗，单列
        x["locked_not_spent"] = x["deposit"]
        x["true_spend_month"] = round((x["total_year"] - x["deposit"]) / 12)
    base = min(a, key=lambda x: x["rent"])
    top = max(a, key=lambda x: x["real_month"])
    return {"time_value": time_value, "util_note": "水电网络按各自实际均摊列出",
            "units": a, "cheapest_face": base["id"],
            "costliest_real": top["id"],
            "gap": top["real_month"] - min(x["real_month"] for x in a)}


# ---------- 件-04 外卖价格解剖 ----------
def case04():
    """两份外卖没法比：拆到实付，再除以净重量，并算凑单临界点。"""
    def build(o):
        sub = sum(i["price"] * i["qty"] for i in o["items"])
        o["subtotal"] = sub
        # 满减：满 45 减 14 / 满 30 减 8
        cut = 0
        rule = None
        for th, amt in sorted([(30, 8), (45, 14)], reverse=True):
            if sub >= th:
                cut, rule = amt, "满 %d 减 %d" % (th, amt)
                break
        o["discount"], o["discount_rule"] = cut, rule or "未满 30，无满减"
        o["package"] = sum(i.get("pkg", 0) * i["qty"] for i in o["items"])
        o["delivery"] = o["delivery_base"] + (
            o["dist_km"] - o["free_km"]) * o["per_km"] if o["dist_km"] > o["free_km"] else o["delivery_base"]
        o["delivery"] = round(o["delivery"], 2)
        o["coupon"] = min(o["coupon"], max(0.0, sub - cut))
        o["pay"] = round(max(0, sub - cut + o["package"] + o["delivery"] - o["coupon"]), 2)
        o["grams"] = sum(i["g"] * i["qty"] for i in o["items"])
        o["per_100g"] = round(o["pay"] / o["grams"] * 100, 2)
        # 凑单临界：再加多少钱能进下一档，且加的东西本身值不值
        nxt = 45 if 30 <= sub < 45 else (30 if sub < 30 else None)
        if nxt is None:
            o["add_to_next"], o["add_gain"] = 0, 0
        else:
            need = round(nxt - sub, 2)
            gain = 6 if nxt == 45 else 8
            o["add_to_next"], o["add_gain"] = need, gain
            o["add_net"] = round(need - gain, 2)
            o["add_worth"] = gain > need
        o["fee_share_pct"] = round((o["package"] + o["delivery"]) / o["pay"] * 100, 1)
        return o

    orders = [
        build({"id": "T1", "shop": "云滇小锅米线", "items": [
            {"n": "小锅米线", "price": 26, "qty": 1, "g": 620, "pkg": 2},
            {"n": "卤蛋", "price": 4, "qty": 1, "g": 55, "pkg": 0.5}],
            "coupon": 5, "delivery_base": 3, "dist_km": 2.6, "free_km": 2.0, "per_km": 1.2}),
        build({"id": "T2", "shop": "老傅家常菜", "items": [
            {"n": "红烧肉饭", "price": 32, "qty": 1, "g": 480, "pkg": 2.5},
            {"n": "例汤", "price": 6, "qty": 1, "g": 300, "pkg": 1.5},
            {"n": "凉拌黄瓜", "price": 12, "qty": 1, "g": 180, "pkg": 1}],
            "coupon": 0, "delivery_base": 4, "dist_km": 3.4, "free_km": 2.0, "per_km": 1.2}),
    ]
    cheap = min(orders, key=lambda x: x["pay"])
    dense = min(orders, key=lambda x: x["per_100g"])
    return {"orders": orders, "cheapest_pay": cheap["id"],
            "best_per_100g": dense["id"], "same_shop_flag": cheap["id"] != dense["id"],
            "rule": "满减档：满 30 减 8／满 45 减 14；配送费 起步价 + 超出免费里程 ×1.2 元/km"}


# ---------- 件-05 体检偏离度 ----------
def case05():
    """报告只标 ↑：把"偏了多少"归一化到区间半宽，再排序分诊。

    dev = (value - mid) / half，mid=(low+high)/2，half=(high-low)/2。
    dev=±1 恰好在边界；|dev|>2 是我自定的"值得复查看"线，不是诊断标准。
    """
    rng = random.Random(SEED + 5)
    items = [
        {"k": "血红蛋白", "u": "g/L", "low": 130, "high": 175, "v": 121, "dept": "血液科", "fast": False},
        {"k": "空腹血糖", "u": "mmol/L", "low": 3.9, "high": 6.1, "v": 6.8, "dept": "内分泌科", "fast": True},
        {"k": "低密度脂蛋白", "u": "mmol/L", "low": 0, "high": 3.4, "v": 4.1, "dept": "心血管内科", "fast": True},
        {"k": "丙氨酸氨基转移酶", "u": "U/L", "low": 9, "high": 50, "v": 63, "dept": "消化内科", "fast": True},
        {"k": "甘油三酯", "u": "mmol/L", "low": 0, "high": 1.7, "v": 2.4, "dept": "内分泌科", "fast": True},
        {"k": "尿酸", "u": "μmol/L", "low": 208, "high": 428, "v": 471, "dept": "风湿免疫科", "fast": False},
        {"k": "甲状腺促激素", "u": "mIU/L", "low": 0.27, "high": 4.2, "v": 3.1, "dept": "内分泌科", "fast": False},
        {"k": "肌酐", "u": "μmol/L", "low": 57, "high": 111, "v": 88, "dept": "肾内科", "fast": False},
        {"k": "白细胞计数", "u": "10^9/L", "low": 3.5, "high": 9.5, "v": 6.2, "dept": "血液科", "fast": False},
        {"k": "总胆固醇", "u": "mmol/L", "low": 0, "high": 5.2, "v": 5.6, "dept": "心血管内科", "fast": True},
        {"k": "维生素 D", "u": "ng/mL", "low": 30, "high": 100, "v": 17, "dept": "内分泌科", "fast": False},
        {"k": "血压收缩压", "u": "mmHg", "low": 90, "high": 139, "v": 146, "dept": "心血管内科", "fast": False},
    ]
    for it in items:
        mid = (it["low"] + it["high"]) / 2
        half = (it["high"] - it["low"]) / 2
        it["mid"], it["half"] = round(mid, 2), round(half, 2)
        it["dev"] = round((it["v"] - mid) / half, 2)
        it["abs_dev"] = abs(it["dev"])
        it["flag"] = "high" if it["v"] > it["high"] else "low" if it["v"] < it["low"] else "in"
        # 单边区间（低密度脂蛋白、总胆固醇只有上限）用中值归一会被压低，
        # 因此另算"越界比例"：偏离被违反的那条边多少个百分点。件-05 里两式并列并注明。
        bound = it["high"] if it["flag"] == "high" else it["low"] if it["flag"] == "low" else None
        if bound:
            it["rel_out_pct"] = round((it["v"] - bound) / bound * 100, 1)
            it["one_sided"] = it["low"] == 0
        else:
            it["rel_out_pct"], it["one_sided"] = 0.0, it["low"] == 0
        it["watch"] = it["flag"] != "in" and it["rel_out_pct"] > 15
        it["recheck"] = ("2 周内复查并挂号" if it["rel_out_pct"] > 20 else
                         "6 周内复查" if it["rel_out_pct"] > 10 else
                         "3 个月内复查" if it["flag"] != "in" else
                         "随下次年度体检")
        # 需要空腹复查的项目，标注取数条件
        it["need_fast"] = it["fast"] and it["flag"] != "in"
    items.sort(key=lambda x: -x["abs_dev"])
    n_hi = sum(1 for i in items if i["flag"] == "high")
    n_lo = sum(1 for i in items if i["flag"] == "low")
    depts = {}
    for i in items:
        if i["flag"] != "in":
            depts.setdefault(i["dept"], []).append(i["k"])
    worst_rel = max([i for i in items if i["flag"] != "in"], key=lambda i: i["rel_out_pct"])
    return {"items": items, "n_abnormal": n_hi + n_lo, "n_high": n_hi, "n_low": n_lo,
            "n_watch": sum(1 for i in items if i["watch"]),
            "worst": items[0]["k"], "worst_dev": items[0]["dev"],
            "worst_rel": worst_rel["k"], "worst_rel_pct": worst_rel["rel_out_pct"],
            "n_one_sided": sum(1 for i in items if i["one_sided"]),
            "depts": depts,
            "dev_scale": [round(i["abs_dev"], 2) for i in items],
            "seed_note": "12 项数值与区间全为演示；dev 是我自定义的归一化偏离度，"
                         "不是诊断标准，区间也不是任何实验室的真实参考值"}


# ---------- 件-06 套餐降速陷阱 ----------
def case06():
    """40 GB 后降速：把 30 天用量累加，找出撞线那天与撞线后能做什么。"""
    rng = random.Random(SEED + 6)
    cap_gb, speed_after = 40.0, 1.0
    usage = []
    for d in range(1, 31):
        wk = d % 7 in (6, 0)
        base = rng.uniform(0.7, 1.5) + (1.4 if wk else 0)
        if d in (9, 10, 11):
            base += 2.6            # 出差三天酒店没 Wi-Fi
        if d == 24:
            base += 3.1            # 缓存了一季剧
        usage.append(round(base, 2))
    cum, hit_day, hit_part = [], None, None
    run = 0.0
    for i, u in enumerate(usage, start=1):
        if hit_day is None and run + u > cap_gb:
            hit_day = i
            hit_part = round((cap_gb - run) / u * 24, 1)   # 当天几点开始降速
        run += u
        cum.append(round(run, 2))
    left = round(sum(usage[hit_day - 1:]), 2) if hit_day else 0
    month_total = round(sum(usage), 2)
    fast_days = hit_day - 1 if hit_day else 30
    can_do = [
        {"s": "文字聊天／语音消息", "need": 0.1, "ok": True},
        {"s": "网页浏览", "need": 0.5, "ok": True},
        {"s": "音乐在线（标准音质）", "need": 0.32, "ok": True},
        {"s": "视频通话 720p", "need": 1.5, "ok": False},
        {"s": "短视频 1080p", "need": 4.0, "ok": False},
        {"s": "地图导航实时路况", "need": 0.6, "ok": True},
        {"s": "远程桌面／文件上传", "need": 6.0, "ok": False},
    ]
    return {"cap_gb": cap_gb, "speed_after": speed_after, "usage": usage, "cum": cum,
            "hit_day": hit_day, "hit_hour": int(hit_part), "hit_minute": int(round((hit_part % 1) * 60)),
            "month_total": month_total, "fast_days": fast_days,
            "slow_days": 30 - fast_days, "gb_after_cap": left,
            "gb_after_cap_hours": round(left * 8 * 1000.0 / speed_after / 3600.0, 1),
            "can_do": can_do, "price": 39,
            "detail": "详情页两行小字：高速流量 40 GB，超出后降至 1 Mbps，次月恢复"}


# ---------- 件-07 停车分段计费 ----------
def case07():
    """四行字变阶梯函数：算出封顶临界与常见时长。"""
    free_min, first_h, first_price, step_min, step_price, cap = 15, 60, 6, 30, 3, 40

    def cost(minutes):
        m = minutes
        if m <= free_min:
            return 0.0, "免费时段内"
        m -= free_min
        if m <= first_h:
            return float(first_price), "首小时一口价"
        extra = math.ceil((m - first_h) / step_min)
        c = first_price + extra * step_price
        if c >= cap:
            return float(cap), "已到 %d 元封顶，多停不加钱" % cap
        return float(c), "首小时 + %d 个半小时" % extra

    def cap_minutes():
        """封顶所需时长：首小时后每 step_min 加 step_price，直到 cap。"""
        need_steps = math.ceil((cap - first_price) / step_price)
        return first_h + need_steps * step_min

    cm = cap_minutes()
    durs = [10, 15, 20, 45, 60, 90, 120, 180, cm, cm + 30, 360, 480, 720, 1440, 1500]
    table = []
    for d in sorted(set(durs)):
        c, why = cost(d)
        # 超过 24 h 按整天 + 余下时长计（本费率假设）
        if d > 1440:
            days = d // 1440
            rem = d % 1440
            rc, _ = cost(rem if rem > 0 else 1440)
            c = days * cap + (rc if rem else 0)
            why = "%d 天封顶 + 余 %d min" % (days, rem)
        table.append({"min": d, "label": ("%dh%02d" % (d // 60, d % 60)).lstrip("0h")
                      if d >= 60 else "%d min" % d, "cost": round(c, 0), "why": why})
    # 逐分钟扫描出精确台阶：cap_minutes 只是"首小时段之后再停 420 min"的粗估，
    # 真正到封顶的墙钟分钟数含免费期，用 steps 给画面用。
    steps, cur_start, cur_cost = [], 0, cost(0)[0]
    for m in range(1, 1441):
        cc = cost(m)[0]
        if cc != cur_cost:
            steps.append({"from": cur_start, "to": m - 1, "cost": cur_cost})
            cur_start, cur_cost = m, cc
    steps.append({"from": cur_start, "to": 1440, "cost": cur_cost})
    cap_at_min = next(x["from"] for x in steps if x["cost"] >= cap)
    curve = [{"min": m, "cost": cost(m)[0]} for m in range(0, 1441, 15)]
    return {"free_min": free_min, "first_h": first_h, "first_price": first_price,
            "step_min": step_min, "step_price": step_price, "cap": cap,
            "cap_hours": round(cm / 60, 1), "cap_minutes": cm,
            "cap_at_min": cap_at_min, "steps": steps,
            "table": table, "curve": curve,
            "per_day_hours": {h: cost(h * 60)[0] for h in (1, 2, 3, 4, 6, 7, 8, 12)},
            "note": "超过 24 h 按每日封顶重复计；此为演示费率"}


# ---------- 件-08 洗衣机程序选择 ----------
def case08():
    """14 个图标 → 三问收敛到 2 个可选程序 + 明确不该选的。"""
    progs = [
        {"id": "P01", "name": "棉麻 20℃", "temp": 20, "rpm": 800, "min": 45,
         "fab": ["棉", "麻"], "soil": ["轻"], "oil": False, "delicate": False},
        {"id": "P02", "name": "棉麻 40℃", "temp": 40, "rpm": 1200, "min": 62,
         "fab": ["棉", "麻"], "soil": ["轻", "中"], "oil": True, "delicate": False},
        {"id": "P03", "name": "棉麻 60℃", "temp": 60, "rpm": 1200, "min": 78,
         "fab": ["棉"], "soil": ["中", "重"], "oil": True, "delicate": False},
        {"id": "P04", "name": "快洗 15′", "temp": 30, "rpm": 800, "min": 15,
         "fab": ["棉", "化纤"], "soil": ["轻"], "oil": False, "delicate": False},
        {"id": "P05", "name": "强力 30℃", "temp": 30, "rpm": 1000, "min": 95,
         "fab": ["棉", "牛仔"], "soil": ["重"], "oil": True, "delicate": False},
        {"id": "P06", "name": "羊毛 手洗级", "temp": 30, "rpm": 600, "min": 58,
         "fab": ["羊毛"], "soil": ["轻"], "oil": False, "delicate": True},
        {"id": "P07", "name": "羽绒", "temp": 40, "rpm": 600, "min": 70,
         "fab": ["化纤", "羽绒"], "soil": ["轻"], "oil": False, "delicate": True},
        {"id": "P08", "name": "丝绸／内衣", "temp": 20, "rpm": 500, "min": 40,
         "fab": ["真丝"], "soil": ["轻"], "oil": False, "delicate": True},
        {"id": "P09", "name": "筒自洁", "temp": 90, "rpm": 0, "min": 20,
         "fab": [], "soil": [], "oil": False, "delicate": False, "empty": True},
        {"id": "P10", "name": "单脱水", "temp": 0, "rpm": 1200, "min": 12,
         "fab": [], "soil": [], "oil": False, "delicate": False, "empty": True},
        {"id": "P11", "name": "化纤 40℃", "temp": 40, "rpm": 1000, "min": 55,
         "fab": ["化纤"], "soil": ["轻", "中"], "oil": True, "delicate": False},
        {"id": "P12", "name": "婴儿服 高温", "temp": 60, "rpm": 1000, "min": 88,
         "fab": ["棉"], "soil": ["中", "重"], "oil": True, "delicate": False},
        {"id": "P13", "name": "牛仔 30℃", "temp": 30, "rpm": 900, "min": 68,
         "fab": ["牛仔"], "soil": ["中"], "oil": True, "delicate": False},
        {"id": "P14", "name": "漂洗＋脱水", "temp": 0, "rpm": 1000, "min": 25,
         "fab": [], "soil": [], "oil": False, "delicate": False, "empty": True},
    ]
    q = {"fab": "棉", "soil": "重", "oil_kind": "火锅红油（油脂＋辣椒色素）",
         "clock_in": "20:40", "must_dry_by": "23:30", "max_min": 150}
    cand = []
    for p in progs:
        if p.get("empty"):
            continue
        score, why = 0, []
        if q["fab"] in p["fab"]:
            score += 2
            why.append("面料匹配")
        else:
            score -= 3
            why.append("面料不含%s" % q["fab"])
        if q["soil"] in p["soil"]:
            score += 2
            why.append("脏污等级够")
        else:
            score -= 2
            why.append("带不动%s脏" % q["soil"])
        if p["oil"]:
            score += 2
            why.append("可处理油脂")
        else:
            score -= 2
            why.append("油脂洗不掉")
        if p["min"] > q["max_min"]:
            score -= 2
            why.append("超出可用时间")
        if p["temp"] >= 40 and q["fab"] == "棉":
            score += 1
        cand.append({"p": p, "score": score, "why": why})
    cand.sort(key=lambda c: -c["score"])
    ok = [c for c in cand if c["score"] >= 6]
    bad = [c for c in cand if c["score"] <= 0]
    pick = []
    for c in ok:
        t = int(q["clock_in"].split(":")[0]) * 60 + int(q["clock_in"].split(":")[1]) + c["p"]["min"]
        pick.append({"id": c["p"]["id"], "name": c["p"]["name"], "min": c["p"]["min"],
                     "temp": c["p"]["temp"], "rpm": c["p"]["rpm"], "score": c["score"],
                     "why": c["why"], "done_at": hhmm(t), "in_time": t <= 23 * 60 + 30})
    avoid = [{"id": c["p"]["id"], "name": c["p"]["name"], "why": c["why"]} for c in bad[:4]]
    steps = [
        "先刮掉凝固的牛油（纸巾＋勺背），不要先冲热水",
        "领口／油点处涂少量洗涤剂静置 5–10 min",
        "翻面、拉好拉链，单独或与同类棉件同洗",
        "选 %s，油渍模式若面板有则开" % (pick[0]["name"] if pick else "—"),
        "结束立刻取出晾晒；色素残留别用烘干机（高温会固色）",
    ]
    return {"progs": progs, "q": q, "n_icons": len(progs),
            "pick": pick, "avoid": avoid, "steps": steps,
            "note": "程序名与时长是我按常见家用滚筒拟的演示值，以你家机器说明书为准"}


# ---------- 件-09 含糖量方糖 ----------
def case09():
    """每 100 mL 与每瓶是两个口径：折到整瓶，再数方糖。"""
    sugar_cube_g = 4.5
    daily_soft = 50.0     # 常见建议上限之一
    daily_best = 25.0
    drinks = [
        {"id": "S1", "name": "碳酸饮料（罐）", "vol": 330, "per100": 10.6, "sucrose_free_label": False, "label": ""},
        {"id": "S2", "name": "冰红茶（瓶）", "vol": 500, "per100": 8.4, "sucrose_free_label": False, "label": ""},
        {"id": "S3", "name": "「0 蔗糖」乳酸菌（瓶）", "vol": 300, "per100": 9.1, "sucrose_free_label": True, "label": "0 蔗糖"},
        {"id": "S4", "name": "运动饮料（瓶）", "vol": 600, "per100": 6.0, "sucrose_free_label": False, "label": ""},
        {"id": "S5", "name": "无糖茶（瓶）", "vol": 500, "per100": 0.0, "sucrose_free_label": True, "label": "无糖"},
    ]
    for x in drinks:
        x["total_g"] = round(x["per100"] * x["vol"] / 100, 1)
        x["cubes"] = round(x["total_g"] / sugar_cube_g, 1)
        x["cubes_int"] = int(round(x["total_g"] / sugar_cube_g))
        x["pct_soft"] = round(x["total_g"] / daily_soft * 100)
        x["pct_best"] = round(x["total_g"] / daily_best * 100)
        x["over_best"] = x["total_g"] > daily_best
        x["ml_to_best"] = round((daily_best / x["per100"] * 100)) if x["per100"] > 0 else None
        x["half_bottle_g"] = round(x["total_g"] / 2, 1)
    ranked = sorted([d for d in drinks if d["total_g"] > 0], key=lambda d: -d["total_g"])
    trap = [d for d in drinks if d["sucrose_free_label"] and d["total_g"] > 0]
    return {"cube_g": sugar_cube_g, "daily_soft": daily_soft, "daily_best": daily_best,
            "drinks": drinks, "ranked": [d["id"] for d in ranked],
            "max_cubes": ranked[0]["cubes_int"] if ranked else 0,
            "trap": [d["id"] for d in trap],
            "trap_note": "「0 蔗糖」只说明未额外添加蔗糖，浓缩果汁／糖浆仍计入总糖",
            "note": "含量为演示值；上限为常见公开建议口径，落地前核对现行指南"}


# ---------- 件-10 入职第一个月核对单 ----------
def case10():
    """8 项：该是多少 / 合同写的 / 对不对 / 不对怎么办。"""
    monthly = 12000          # 示例月薪（税前）
    contract_months = 36     # 示例合同期 3 年
    checks = [
        {"id": "K1", "k": "合同期限与试用期", "rule": "合同 3 年，试用期上限 6 个月",
         "in": "合同写“试用期 8 个月”", "should": "≤ 6 个月", "verdict": "不符",
         "act": "要求改到 6 个月内并留书面变更记录；不改可向劳动监察投诉",
         "src": "common_rule_needs_check"},
        {"id": "K2", "k": "社保起缴时间", "rule": "用工之日起 30 日内办理参保登记",
         "in": "HR 口头“转正后再缴”", "should": "入职当月或次月申报", "verdict": "不符",
         "act": "先查个人参保记录截图，再书面要求补缴；口头承诺不作数",
         "src": "common_rule_needs_check"},
        {"id": "K3", "k": "公积金缴存比例", "rule": "5%–12%，单位与个人同比例",
         "in": "合同未写比例", "should": "写明比例与基数", "verdict": "缺项",
         "act": "入职单要求补一页薪酬结构确认，注明比例／基数／起缴月",
         "src": "common_rule_needs_check"},
        {"id": "K4", "k": "加班费基数", "rule": "平日 1.5 倍／休息日 2 倍／法定日 3 倍",
         "in": "“加班费以最低工资为基数”", "should": "以约定工资为基数", "verdict": "不符",
         "act": "保留打卡与工单记录；基数争议在离职一年内可主张",
         "src": "common_rule_needs_check"},
        {"id": "K5", "k": "月加班上限", "rule": "一般每日不超 1 h，特殊不超 3 h、每月不超 36 h",
         "in": "排班表 3 月实际 61 h", "should": "≤ 36 h/月", "verdict": "不符",
         "act": "先记台账，再走内部反馈渠道；不签放弃加班费声明",
         "src": "common_rule_needs_check"},
        {"id": "K6", "k": "年假天数", "rule": "累计工龄满 1 年不满 10 年，年假 5 天",
         "in": "合同“按公司制度另行规定”", "should": "写明天数与折算", "verdict": "缺项",
         "act": "要求附页写明天数、是否含法定、未休是否折薪",
         "src": "common_rule_needs_check"},
        {"id": "K7", "k": "竞业限制与补偿", "rule": "期限≤2 年，期间应按月支付经济补偿",
         "in": "条款包含全部岗位、无补偿金额", "should": "限定岗位＋写明月补偿", "verdict": "不符",
         "act": "争取删除或缩范围；已签则注意离职后是否实际收到补偿",
         "src": "common_rule_needs_check"},
        {"id": "K8", "k": "工资构成与发薪日", "rule": "应写明结构、发薪日与扣款项",
         "in": "仅写“按公司薪酬制度执行”", "should": "基本 %s + 绩效 + 补贴" % f"{monthly:,}",
         "verdict": "缺项", "act": "把口头说明变成一页邮件确认，保留发送记录",
         "src": "self_defined_demo"},
    ]
    n_bad = sum(1 for c in checks if c["verdict"] == "不符")
    n_gap = sum(1 for c in checks if c["verdict"] == "缺项")
    first_month = [
        {"d": "第 1 天", "k": "拿到合同全本与附件清单，逐页拍照"},
        {"d": "第 3 天", "k": "确认考勤方式、加班审批入口与打卡记录导出"},
        {"d": "第 7 天", "k": "查社保参保记录与公积金账户是否已开户"},
        {"d": "第 14 天", "k": "把口头承诺（奖金／调薪／年假）写成邮件请对方确认"},
        {"d": "第 25 天", "k": "首个完整考勤周结束后核对加班小时数台账"},
        {"d": "第 30 天", "k": "对照本表逐项复盘，未闭环项走内部渠道并留痕"},
    ]
    return {"monthly": monthly, "contract_months": contract_months,
            "checks": checks, "n_bad": n_bad, "n_gap": n_gap, "n_total": len(checks),
            "n_ok": len(checks) - n_bad - n_gap, "first_month": first_month,
            "overtime_hours": 61, "overtime_cap": 36,
            "overtime_over_h": 61 - 36,
            "note": "本表是核对清单不是法律意见；条款口径需按现行法规与当地执行口径核对"}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    doc = {
        "run_id": RID,
        "seed": SEED,
        "source": "self_defined_demo unless noted",
        "generated_by": "tmp/%s/B06/b06data.py" % RID,
        "city": "汀州市（虚构，与 B05 同一虚构城市但不共享实体）",
        "cases": {
            "case01": case01(), "case02": case02(), "case03": case03(),
            "case04": case04(), "case05": case05(), "case06": case06(),
            "case07": case07(), "case08": case08(), "case09": case09(),
            "case10": case10(),
        },
    }
    p = OUT / "demo.json"
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote %s (%d bytes)" % (p, p.stat().st_size))
    for k in sorted(doc["cases"]):
        print("  %s: %d keys" % (k, len(doc["cases"][k])))


if __name__ == "__main__":
    main()
