"""Archive the ten B06 works and write problem-evidence.json.

Each archived PNG must be the service response for the DSL file that is archived next to
it, so the script re-reads the request log and matches bytes rather than trusting names.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "B06"
OUT = ROOT / "outputs" / RUN / "B06"
D = json.loads((TMP / "data.json").read_text(encoding="utf-8"))
AUD = json.loads((TMP / "audits.json").read_text(encoding="utf-8"))
PLAN = json.loads((TMP / "work-plan.json").read_text(encoding="utf-8"))
REQ = {}
for line in (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines():
    r = json.loads(line)
    REQ[r["request_id"]] = r

STEMS = ["case01-lasttrain", "case02-headway", "case03-payslip", "case04-checkup",
         "case05-nutrition", "case06-warnings", "case07-deposit", "case08-insurance",
         "case09-wayfinding", "case10-utilities"]

CASES = [
    ("01", STEMS[0], "末班车还赶得上吗", "站台海报 900×1270",
     "时刻表按线路排，乘客要自己做「我的时间 vs 每站末班」的减法"),
    ("02", STEMS[1], "现在要不要等这趟公交", "横长条卡 1200×420",
     "站牌只写首末班与间隔区间，回答不了「现在」这一问"),
    ("03", STEMS[2], "应发 12000，到手 8700：中间去了哪", "A4 单页 794×1123",
     "工资条列了项目和比例，但没说哪些是自己的钱、什么时候能用"),
    ("04", STEMS[3], "七个箭头，哪个要紧", "手机 390×844",
     "报告按项目顺序罗列参考区间与箭头，看不出偏离幅度与紧急程度"),
    ("05", STEMS[4], "这一包，占掉我一天多少", "货架标签卡 680×900",
     "NRV% 以成人 8400 kJ 为基准，且「一份」的分母经常被人忽略"),
    ("06", STEMS[5], "暴雨预警：颜色之后要做什么", "社区公告 800×1130",
     "四级颜色只表示高低，不告诉居民停课、转移还是照常上班"),
    ("07", STEMS[6], "退租时，押金能拿回多少", "决策树 1200×620",
     "押金规则散在四条条款里，退租前算不清会扣多少"),
    ("08", STEMS[7], "这三种事故，你要自己掏多少钱", "对比册页 1000×1400",
     "保单写保额与免赔，不发生事故永远不知道哪些不赔"),
    ("09", STEMS[8], "门诊大楼：你要去的科在哪", "大厅立牌 900×1600",
     "楼层索引按科室拼音排，而人手里只有空间信息"),
    ("10", STEMS[9], "水、电、燃气：终于能放在一张表里比", "信息图 1200×900",
     "三种单位三种单价，无法比较，也看不出哪项在涨"),
]

FACTS = {
    "01": ["12 个目的地按「最迟离开本站」排序：还剩 17 分到差 21 分",
           "9 地可去、3 地已来不及；最远可达莘庄（车程 26 分，最迟 23:51）",
           "「换 N」标出换乘次数——真正卡住行程的往往是换乘而非本线末班"],
    "02": ["31 格 × 30 分钟，覆盖 05:30 首班到 21:00 末班",
           "四档间隔 4 / 8 / 10 / 12 分钟各配文字说明，不只靠颜色",
           "现在 20:12 落在夜间档 → 最坏等到 20:24"],
    "03": ["个人扣款 2,700 + 个税 600 + 到手 8,700 = 应发 12,000（断言）",
           "单位另出 4,704 元，单列一栏说明「不进你当期工资」",
           "第五节把六笔钱按一年重算：到手 104,400、公积金 34,560、个税 7,200"],
    "04": ["9 项指标各配自己的参考区间与刻度，不共用一条被压扁的轴",
           "7 项偏离，其中 5 项只超出区间一小截，画面如实呈现",
           "视力一项注明「区间只有 0.2 宽，倍数显得大」"],
    "05": ["每 100 g 与每 75 g 两列并排，避免偷换分母",
           "能量 19.6%（成人）/ 23.2%（儿童）双基准同屏",
           "半包 / 一包 / 一包半三档占比由同一份数据算出"],
    "06": ["四级 2×2 卡片：触发标准、谁受影响、该做什么、停课/停工/解除",
           "当前生效级别用红框 + 「当前生效」文字双重标注",
           "顶部递进条保留颜色顺序，但每级都写名称"],
    "07": ["四个判断节点各带合同条款号；「是」向下、「否」向右掉出结果",
           "三条路径的退回金额 = 押金 - 扣款（断言）：3,800 / 1,900 / 3,457",
           "N2 的「否」明确写「不扣费」，不与 N3 的修补费混淆"],
    "08": ["三场景同一比例（1 元 = 0.00406 px），斜纹严格裁在不赔区间内",
           "自掏 16,000 / 0 / 45,800，合计 61,800 元写在页首",
           "每个缺口都指回一条条款号"],
    "09": ["六层剖切，每层的东区/西区色块宽度与该层科室数量成比例",
           "红线示例：1 层东门 → 3 层东区抽血室，目标块加红框与圆点",
           "右栏 20 个科室按名称查楼层，与左图同一份数据"],
    "10": ["统一成元/人·月：电 88.3、燃气 54.8、水 38.7，份额 48.6/30.1/21.3%",
           "原始单位与单价单独列出（度/立方米/吨），不让归一化掩盖差异",
           "可行动项里的每个数字（75.3、59.3、40.8% 等）都由 12 个月样本算出"],
}

EVIDENCE = {
    "01": ("地铁/火车站末班时刻表与换乘指示", "在换乘站按指示牌找末班、自己心算还差几分钟的经历"),
    "02": ("公交站牌的「首末班 + 间隔」写法", "站牌前等车、无法判断还要不要等的经历"),
    "03": ("工资条与社保缴费明细的常见版式", "第一次拿到工资条时对不上到手金额的经历"),
    "04": ("体检报告单（项目 / 参考区间 / ↑↓）", "替家人读体检报告、不知道哪个箭头要紧的经历"),
    "05": ("预包装食品营养成分表与 NRV%", "在货架前比较两包零食、被百分比绕住的经历"),
    "06": ("气象预警信号四级颜色与社区公告栏", "看到橙色预警但不知道该不该去接孩子的经历"),
    "07": ("住房租赁合同中的押金、维修与费用条款", "退租时逐条翻合同算押金的经历"),
    "08": ("机动车保险单的责任限额与免责条款", "听身边人说起「以为赔结果不赔」的经历"),
    "09": ("医院门诊大厅楼层索引牌", "拿着预约单在门诊大厅找科室的经历"),
    "10": ("水、电、燃气三张不同单位的账单", "想比较家庭开销却对不上单位的经历"),
}

REINVENT = {
    "01": "把表倒过来：以「你此刻在站台」为唯一输入，列出每个目的地的最迟离开时刻",
    "02": "把一天摊成一条带子，一格 30 分钟，颜色=要等的分钟数；针尖右侧就是答案",
    "03": "同一笔钱拆成「谁的口袋 / 什么时候能用」两栏，并按一年重算一遍",
    "04": "放弃共用坐标轴，改为每项一条自己的参考带，偏离量在各自尺度上可见",
    "05": "把「每 100 g」换成「这一包 / 半包 / 一包半占我一天多少」，双基准并列",
    "06": "四级并排成四张行动卡，每级写谁受影响、该做什么、何时解除",
    "07": "把散在四条条款里的规则合成一棵树，另附三条常见路径的金额结果",
    "08": "换成三个具体事故，每个画「损失→赔付→自己掏」，缺口用斜纹显式标出",
    "09": "画建筑剖切：科室落在各层东西区，并给一条从入口到目标的示例路径",
    "10": "统一折算成元/人·月做比较，同时保留原始单位与单价，再给可行动项",
}

ASSUMPTIONS = {
    "01": "车站名与时刻为自拟示例；末班逻辑假设同方向逐站变晚",
    "02": "线路与间隔为自拟；假设发车间隔在半个时段内均匀",
    "03": "费率取常见区间但标注为示例，不声称是现行标准",
    "04": "指标与数值为示例，不构成任何真实个体的结果",
    "05": "食品数值为示例编制；儿童基准取一般参考值",
    "06": "阈值取自公开预警体系的一般结构，未查证本地细则",
    "07": "合同条款号与金额为示例，不构成裁决",
    "08": "保单条款与金额为示例，不指向任何真实产品",
    "09": "医院布局与科室分布为示例",
    "10": "12 个月用量与同比为自拟样本，非真实抄表",
}


def rel(p):
    return p.relative_to(ROOT).as_posix()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = []
    for cid, stem, title, device, stuck in CASES:
        dsl = TMP / f"{stem}.snapshot"
        cands = [k for k in REQ
                 if k.startswith(f"B06-{stem}-") and REQ[k]["http_status"] == 200
                 and Path(REQ[k]["request_file"]).resolve() == dsl.resolve()
                 and (ROOT / REQ[k]["response_file"]).exists()]
        assert cands, stem
        cands.sort(key=lambda k: REQ[k]["ended_at"])
        rid = cands[-1]
        r = REQ[rid]
        raw = (ROOT / r["response_file"]).read_bytes()
        assert raw[:8] == b"\x89PNG\r\n\x1a\n", stem
        cd = OUT / f"case-{cid}"
        cd.mkdir(exist_ok=True)
        (cd / "final.png").write_bytes(raw)
        (cd / "final.snapshot").write_text(dsl.read_text(encoding="utf-8"),
                                           encoding="utf-8")
        a = AUD[stem]
        versions = sorted(k.split(stem + "-")[1] for k in REQ
                          if k.startswith(f"B06-{stem}-"))
        md = [f"# case-{cid} · {title}", "",
              f"- 形式/画布：{device}",
              f"- 原本卡在哪：{stuck}",
              f"- 服务请求：`{rid}`（200，{r['duration_seconds']}s，"
              f"server {r['server_timing']}，X-Request-Id `{r['x_request_id']}`）",
              f"- 响应字节：{len(raw):,} B，sha256 `{hashlib.sha256(raw).hexdigest()[:16]}…`",
              f"- 渲染次数：{len(versions)}（{', '.join(versions)}）",
              f"- DSL：`case-{cid}/final.snapshot`", "",
              "## 屏上的具体内容", ""]
        md += [f"- {x}" for x in FACTS[cid]]
        md += ["", "## 自检", "",
               f"- 生成器审计：overlap {a['overlap_n']}、outside {a['outside_n']}、"
               f"spill {a['spill_n']}、truncated {a['truncated_n']}、"
               f"below_min_font {a['below_min_font_n']}"
               f"（{a['texts']} 段文字 / {a['shapes']} 图形）",
               "- 所有数值来自 `b06data.py` 生成的 data.json，派生量带断言",
               "- final.png 为服务原始响应字节，未做后处理",
               "- 实际看图：见 `iterations.jsonl`", "",
               "## 假设与边界", "", f"- {ASSUMPTIONS[cid]}",
               "- 未做用户实验：改善判断只基于最终画面的可读性与结构，"
               "不声称验证过实际效果。", ""]
        (cd / "case.md").write_text("\n".join(md), encoding="utf-8")
        manifest.append({"case": f"case-{cid}", "title": title, "device": device,
                         "stuck": stuck, "dsl_stem": stem, "request_id": rid,
                         "bytes": len(raw), "renders": len(versions), "audit": a,
                         "png": rel(cd / "final.png"),
                         "snapshot": rel(cd / "final.snapshot"),
                         "report": rel(cd / "case.md")})
    (TMP / "case-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    ev = {"schema_version": 1, "path_base": "output_dir", "task_id": "B06",
          "run_id": RUN,
          "method_note": "问题来自可观察的日常物料与使用者本人的经历；没有做现场调研、"
                         "访谈或用户实验。所有数据为示例编制，结构参照真实物料。",
          "not_claimed": ["未做用户测试，不声称任何作品提升了真实用户的效率或准确率",
                          "未核实任何官方费率、时刻表、政策或产品条款",
                          "没有制作「故意丑化的之前图」；原材料只作为研究输入"],
          "problems": []}
    for cid, stem, title, device, stuck in CASES:
        src, obs = EVIDENCE[cid]
        plan_case = next(c for c in PLAN["cases"] if c["id"] == f"case-{cid}")
        a = AUD[stem]
        audience = plan_case.get("audience") or PLAN["audience"]
        ev["problems"].append({
            "case": f"case-{cid}", "title": title,
            "source_observed": src, "personal_observation": obs,
            "stuck_point": stuck,
            "audience": audience,
            "format": device,
            "scene_requirements": plan_case["criteria"],
            "reinvention": REINVENT[cid],
            "data_basis": ASSUMPTIONS[cid],
            "visible_improvement": FACTS[cid],
            "self_check": {"overlap": a["overlap_n"], "outside": a["outside_n"],
                           "spill": a["spill_n"], "truncated": a["truncated_n"],
                           "below_min_font": a["below_min_font_n"]},
            "unverified": "是否真的更快/更少出错，未经用户实验验证",
        })
    (OUT / "problem-evidence.json").write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("archived", len(manifest), "cases + problem-evidence.json")


if __name__ == "__main__":
    main()
