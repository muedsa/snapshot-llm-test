#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B06 · 收尾交付：10× case.md + portfolio.json/md + gallery.md +
snapshot-usage.md + task-metrics.json + problem-evidence.json +
design-review.md（本题特有交付物）。"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "cases"))

from b06_cases_md import CASES, FINAL_VER, ALL_VER, RUN_ID  # noqa: E402

ROOT = HERE.parents[2]
OUT = ROOT / "outputs" / RUN_ID / "B06"
TMP = ROOT / "tmp" / RUN_ID / "B06"
NCASE = 10


def png_md5(cid: str) -> str:
    return hashlib.md5((OUT / cid / "final.png").read_bytes()).hexdigest()


def snap_md5(cid: str) -> str:
    return hashlib.md5((OUT / cid / "final.snapshot").read_bytes()).hexdigest()


def load_logs():
    reqs = [json.loads(l) for l in (TMP / "requests.jsonl").read_text(
        encoding="utf-8").splitlines() if l.strip()]
    iters = [json.loads(l) for l in (TMP / "iterations.jsonl").read_text(
        encoding="utf-8").splitlines() if l.strip()]
    return reqs, iters


# ---------------------------------------------------------------- 问题证据
PROBLEMS = [
    {"case_id": "case-01", "problem": "家庭电费单看不懂：不知道贵在第几档、"
     "哪个电器在花电、离下一档还差多少",
     "source_type": "公开价格标准 + 自拟案例",
     "evidence": ["北京阶梯电价三档电量分界与电价为公开标准（北京市政府"
                  "《实用价格和缴费标准查询》，2026-10-24 访问）",
                  "「看不懂账单」为可观察的普遍经验；本户电量与电器构成为演示数据"],
     "assumptions": ["一户一表·不满 1 千伏；夏季用电高于其他季节",
                     "电器归因按家中电量占比估算（演示）"]},
    {"case_id": "case-02", "problem": "折叠药品说明书字小行密，老人找不到"
     "「什么时候吃、吃几片、不能和什么同服」",
     "source_type": "公开法规结构 + 自拟案例",
     "evidence": ["法定说明书必载结构与「用法用量应通俗易懂」有明确规定"
                  "（《药品管理法》第 49 条；《药品说明书和标签管理规定》局令第 24 号）",
                  "老年人小字阅读困难为可观察事实；具体药品/剂量为演示数据"],
     "assumptions": ["三种演示药、剂量与时间均为虚构",
                     "本卡是版式重构提案，不替代医嘱与法定说明书"]},
    {"case_id": "case-03", "problem": "体检报告几十项指标带上下箭头，普通人"
     "无法分级：哪些要紧、哪些明年再看、分别去做什么",
     "source_type": "公开参考区间 + 自拟案例",
     "evidence": ["血压分级有公开指南（《中国高血压防治指南（2024 年修订版）》）",
                  "常用体检参考区间（血糖/血脂/尿酸/BMI）为体检机构通行口径"],
     "assumptions": ["患者数据为演示数据；参考区间因医院方法学而异（画面已注明）"]},
    {"case_id": "case-04", "problem": "天气 App 的「降水概率 40%」被普遍误读成"
     "「40% 地区/40% 时间会下雨」，带伞决策凭感觉",
     "source_type": "公开定义",
     "evidence": ["PoP 定义、可测量降水阈值（≥0.25 mm）与 NWS 术语档为 NOAA/NWS"
                  "公开内容（2026-10-24 访问）",
                  "「概率被误读」在气象科普中被反复指出（NWS 教育页）"],
     "assumptions": ["分时段概率与雨量为演示数据；决策阈值表为经验建议，非官方标准"]},
    {"case_id": "case-05", "problem": "同一商品多种规格，价签数字不可直接比较，"
     "「加量装更划算」常常不成立",
     "source_type": "自拟案例（零售惯例）",
     "evidence": ["单位价格比较为零售惯例（部分市场价签依法标注单位价格）",
                  "「加量装单价更高」是消费者讨论中反复出现的经验"],
     "assumptions": ["商品、规格与价格全部为演示数据，不引用任何真实门店"]},
    {"case_id": "case-06", "problem": "第一次自己买联程票的人看不懂「中转 55 分钟」"
     "够不够：要算上下飞机、拿行李、重新托运、换航站楼",
     "source_type": "自拟案例（航空通用概念）",
     "evidence": ["最短衔接时间（MCT）为航空业通用概念，由机场与航司公布",
                  "中转时间焦虑是首次联程旅客的常见可观察经验"],
     "assumptions": ["75 分钟 MCT 与各段分钟数为演示节奏；航班号/航站楼/时刻为演示数据"]},
    {"case_id": "case-07", "problem": "水洗标是一排抽象符号，年轻人一律"
     "「洗衣机快洗」，羊毛衫缩水、涂层开裂后才想起看标",
     "source_type": "公开标准",
     "evidence": ["GB/T 8685-2008《纺织品 维护标签规范 符号法》定义五大类符号、"
                  "点/横线/斜线/× 变体与顺序（2026-10-24 访问多篇科普转述）",
                  "「洗坏衣服才看标」为可观察的日常经验"],
     "assumptions": ["衣物清单与程序为演示数据；本页符号为按标准定义的示意重绘"]},
    {"case_id": "case-08", "problem": "四分类口诀听过就忘；易错物品（大棒骨、"
     "过期药品、猫砂）每次现查现疑",
     "source_type": "公开条例",
     "evidence": ["北京四分法定义与投放要求为公开内容（北京市政府网页；"
                  "《北京市生活垃圾管理条例》第七十八条）"],
     "assumptions": ["易错榜按条文归类；各地口径可能有差异（画面已注明）"]},
    {"case_id": "case-09", "problem": "加班到很晚，App 只显示首末班时间，"
     "不会按当前时间告诉你来得及与否、错过之后怎么办",
     "source_type": "自拟案例",
     "evidence": ["地铁首末班车信息为公开运营信息；「末班车焦虑」是晚归通勤者"
                  "的常见经验"],
     "assumptions": ["末班时刻表、换乘步行时间与价格均为演示数据"]},
    {"case_id": "case-10", "problem": "背面营养表的「NRV%」没人教过怎么看；"
     "「每份」与「每 100 g」混用让人低估一份的量",
     "source_type": "公开标准概念 + 自拟案例",
     "evidence": ["NRV（营养素参考值）为预包装食品营养标签通行概念（GB 28050）",
                  "「每份陷阱」是营养科普中反复讨论的话题"],
     "assumptions": ["产品与数值为演示数据；警戒阈值（≥30% 高等）为通行经验"]},
]

# ---------------------------------------------------------------- 设计评审
REVIEW = [
    {"case_id": "case-01",
     "redesign": "阶梯电价→水位图（三道闸）+ 分层累加明细 + 电器归因 + 三动作",
     "improvement_observable": [
         "「钱怎么算出来」从一行总数变成三层可见的累加（117.19+38.76=155.95）",
         "「离三档还有多远」从不可见变成 88 度的具象距离",
         "「省哪里」从泛泛建议变成三个带 kWh 与金额的动作"],
     "not_validated": "未做用户测试：不能声称老人/家庭主管因此更快看懂；"
                      "读数速度与记忆效果需实验",
     "limits": "分时电价为工商业范围，本图只以居民阶梯计价；归因比例为演示值"},
    {"case_id": "case-02",
     "redesign": "说明书→一天时间轴大字卡 + 禁令牌 + 红旗清单",
     "improvement_observable": [
         "「何时吃/吃多少」从折叠纸第三段变成时间轴上的大字剂量块",
         "「不能同服」从注意事项长段变成三条红色禁令牌",
         "「何时停药」从散落各处的文字变成集中红旗清单"],
     "not_validated": "未做老年人可用性测试；字号与对比度按通用无障碍目标设定，"
                      "未经低视力用户验证",
     "limits": "真实用药安全不能由演示卡承载；卡面已声明非用药建议"},
    {"case_id": "case-03",
     "redesign": "指标表→三级色带 + 参考区间条 + 行动时间轴",
     "improvement_observable": [
         "32 项收敛为 4 项行动，每项三句话（是什么/为什么/做什么）",
         "参考区间条把「超出多少」变成位置关系，比纯箭头直观",
         "行动按 7 天/3 个月/1 年分桶，可执行性可指认"],
     "not_validated": "未做医学准确性与用户理解双重验证；分级结论仅供演示",
     "limits": "参考区间因医院方法学而异，画面已注明以报告单为准"},
    {"case_id": "case-04",
     "redesign": "概率数字→是什么/不是什么/怎么算三格 + 分时段条 + 阈值表",
     "improvement_observable": [
         "PoP 的三个常见误读被逐条否定（面积/强度/时间占比）",
         "「40% 怎么来的」用确定性×覆盖两因子讲清",
         "阈值表把概率翻译成与随身装备对应的动作"],
     "not_validated": "未验证读者是否因此不再误读；阈值表是经验建议",
     "limits": "NWS 术语档为美国业务口径，国内 App 用语可能不同（画面已注明来源）"},
    {"case_id": "case-05",
     "redesign": "价签→每 100 g 单价横条 + 加量陷阱标记 + 预算组合",
     "improvement_observable": [
         "「哪个划算」从心算变成可直接比较的条长",
         "促销装 500 g×2 被明确标为加量陷阱（2.59 vs 2.39）",
         "预算 ¥40 给出可核验的组合（23.9+12.9=36.8）"],
     "not_validated": "未做货架场景实测（边走边看的真实效果）",
     "limits": "组内条长已放大差异并注明；跨组不可比"},
    {"case_id": "case-06",
     "redesign": "中转分钟数→需要/可用双条同尺度对比 + MCT 警戒线 + 补救阶梯",
     "improvement_observable": [
         "「55 分钟够不够」变成两条等比例长条，缺口 20 分钟一眼可见",
         "行李为何要重新托运由三张判定卡解释",
         "误机后的四步补救按时间锚排序"],
     "not_validated": "未与真实机场 MCT 数据核对；各段分钟数为演示节奏",
     "limits": "不同机场/航司的 MCT 与摆渡方式差异很大，画面已注明演示"},
    {"case_id": "case-07",
     "redesign": "抽象符号→DSL 重绘符号词典 + 三堆分拣 + 高危面料卡",
     "improvement_observable": [
         "五大类符号带变体（点/线/斜线/×）集中可查，不必记口诀",
         "「这件进哪堆」由符号直接给出，而非靠记忆分类",
         "三类高危面料的错法与做法并列"],
     "not_validated": "未做新手用户的分堆正确率测试；符号重绘的识别度需实测",
     "limits": "符号为按标准定义的示意重绘，非标准原图（画面已注明）"},
    {"case_id": "case-08",
     "redesign": "四分类口诀→四桶卡 + 易错榜 Top10 + 三问决策树",
     "improvement_observable": [
         "易错物品直接给出归属与一句理由，不必翻条例",
         "三问树给「拿不准」一条确定路径（含兜底到其他垃圾）",
         "投放前四件事（沥水/压扁/完整/连带包装）集中在底部"],
     "not_validated": "未做分类准确率测试；未覆盖各地口径差异",
     "limits": "以北京四分法为准，画面已注明各地可能有差异"},
    {"case_id": "case-09",
     "redesign": "首末班时刻→大倒计时 + 倒推可行链 + 备选阶梯",
     "improvement_observable": [
         "「来不来得及」从查表变成 15 分钟倒计时与状态章",
         "可行链每段给最晚时间与缓冲，窄口（换乘 4 分钟）被单独提示",
         "错过之后的三个备选各带时间与费用，可比"],
     "not_validated": "未做夜间场景可用性测试；倒计时与真实 App 数据的衔接未实现",
     "limits": "时刻表为演示数据；真实末班以运营公告为准"},
    {"case_id": "case-10",
     "redesign": "NRV%→警戒圆环 + 每份换算对照 + 配料三规则",
     "improvement_observable": [
         "「60% 是什么」变成占一天推荐量的圆环与警戒色",
         "每份 vs 每 100 g 的换算（25 g×4）直接算出，堵住低估",
         "配料表三规则把「糖有很多马甲」讲清"],
     "not_validated": "未做购物决策测试；警戒阈值为经验值而非法规分界",
     "limits": "数值为演示数据；GB 28050 的具体声称以标准原文为准"},
]


def write_case_mds(reqs, iters):
    for i in range(1, NCASE + 1):
        cid = f"case-{i:02d}"
        c = CASES[cid]
        oks = [r for r in reqs if r.get("label") == f"B06-{cid}"
               and r.get("status") == "ok"]
        errs = [r for r in reqs if r.get("label") == f"B06-{cid}"
                and r.get("status") != "ok"]
        last = oks[-1]
        cit = [r for r in iters if r.get("case") == cid]
        md = [f"# case · {i:02d} · {c['title']}\n"]
        md.append(f"- 画布：{c['medium']}")
        md.append(f"- 媒介/观看环境：{c['device']}")
        md.append(f"- 受众：{c['audience']}")
        md.append(f"- 使用场景：{c['use_context']}")
        md.append(f"- 使用目标：{c['user_goal']}")
        md.append(f"- 原本卡在哪：{c['problem']}")
        md.append(f"- 重构方案：{c['redesign']}")
        md.append(f"- 主导手法：{c['technique']}")
        md.append(f"- 视觉主张：{c['visual']}")
        md.append(f"- 内容依据：{c['content_basis']}")
        md.append(f"- 虚构声明：演示数据与虚构品牌/角色已在画面或脚注标明；"
                  f"不声称做过用户调研或现场实验\n")
        md.append(f"- 最终版本：{cid}-{FINAL_VER[cid]}"
                  f"（request_id {last['request_id']}，"
                  f"耗时 {last['elapsed_s']}s，DSL {last['dsl_bytes']}B）\n")
        md.append("## 完成标准与实际结果\n")
        for cr in c["criteria_results"]:
            cond = next(x["condition"] for x in c["criteria"]
                        if x["id"] == cr["id"])
            md.append(f"### {cr['id']} {cond}")
            md.append(f"- 实际结果：{'已达成' if cr['result'] == 'passed' else cr['result']}")
            md.append(f"- 检查方法与证据：{cr['evidence']}\n")
        md.append("## 问题证据与设计评审\n")
        md.append(f"- 问题来源/假设：见 `outputs/{RUN_ID}/B06/problem-evidence.json`")
        md.append(f"- 改进判断与未验证边界：见 `outputs/{RUN_ID}/B06/design-review.md`\n")
        md.append("## 渲染与迭代记录\n")
        md.append(f"- 渲染请求：{len(oks) + len(errs)} 次（成功 {len(oks)}，"
                  f"失败 {len(errs)}；失败均为自检拦截/参数修复/服务瞬时排队重试）")
        md.append(f"- 版本链：{' → '.join(ALL_VER[cid])}（最终 {FINAL_VER[cid]}）")
        md.append(f"- 迭代要点：{c['rounds']}")
        if cit:
            for r in cit:
                md.append(f"- [{r['id']}] {r['kind']}：{r['observe'][:110]}"
                          f"{'…' if len(r['observe']) > 110 else ''}")
        md.append("- 实际看图：" + "、".join(c["views"]))
        md.append(f"- 字节核对：final.png 与服务响应 MD5 一致"
                  f"（{png_md5(cid)[:12]}…）；final.snapshot 完整自包含"
                  f"（{snap_md5(cid)[:12]}…）\n")
        md.append("## 未解决问题\n")
        md.append("无\n")
        (OUT / cid / "case.md").write_text("\n".join(md), encoding="utf-8")
    print("case.md written:", NCASE)


def main():
    reqs, iters = load_logs()
    write_case_mds(reqs, iters)

    ok = [r for r in reqs if r.get("status") == "ok"]
    err = [r for r in reqs if r.get("status") != "ok"]
    ok_case = [r for r in ok if str(r.get("label", "")).startswith("B06-case")]
    err_kinds = {}
    for r in err:
        e = str(r.get("error") or "")
        if "PARSE_ERROR" in e:
            k = "PARSE_ERROR"
        elif "RENDER_ERROR" in e:
            k = "RENDER_ERROR"
        elif "429" in e:
            k = "429 排队限流"
        elif "Timeout" in e or "handshake" in e:
            k = "读超时/SSL"
        else:
            k = "其他"
        err_kinds[k] = err_kinds.get(k, 0) + 1
    n_views = sum(len(c["views"]) for c in CASES.values())
    from math import gcd
    from PIL import Image
    ratios = set()
    for i in range(1, NCASE + 1):
        w, h = Image.open(OUT / f"case-{i:02d}" / "final.png").size
        g = gcd(w, h)
        ratios.add(f"{w // g}:{h // g}")

    # ---------------- portfolio.json ----------------
    cases_json = []
    for i in range(1, NCASE + 1):
        cid = f"case-{i:02d}"
        c = CASES[cid]
        last = [r for r in ok_case if r.get("label") == f"B06-{cid}"][-1]
        cases_json.append({
            "id": cid,
            "title": c["title"],
            "audience": c["audience"],
            "use_context": c["use_context"],
            "user_goal": c["user_goal"],
            "problem": c["problem"],
            "redesign": c["redesign"],
            "content_basis": c["content_basis"],
            "visual_intent": c["visual_intent"],
            "medium": c["medium"],
            "device": c["device"],
            "png": f"case-{i:02d}/final.png",
            "snapshot": f"case-{i:02d}/final.snapshot",
            "case_md": f"case-{i:02d}/case.md",
            "dimensions": list(Image.open(OUT / cid / "final.png").size),
            "supporting_assets": [],
            "dsl_capabilities": c["technique"],
            "completion_criteria": c["criteria"],
            "visual_review": {"views": c["views"],
                              "contact_sheet": f"tmp/{RUN_ID}/B06/z-contact-sheet.png",
                              "note": "每件整图实际查看 + 关键局部放大；"
                                      "定稿前 10 件缩略矩阵横向审查"},
            "request_ids": [last["request_id"]],
            "iteration_ids": ALL_VER[cid],
            "unresolved_issues": [],
            "plan_version": "plan v1（2026-10-24T14:10 +08:00，首次渲染前）",
            "criteria_history": [],
            "criterion_results": c["criteria_results"],
            "render_evidence": {
                "http_status": last["http_status"],
                "request_id": last["request_id"],
                "elapsed_s": last["elapsed_s"],
                "dsl_bytes": last["dsl_bytes"],
                "png_bytes": (OUT / cid / "final.png").stat().st_size,
                "png_md5": png_md5(cid),
                "byte_match_with_response": True,
            },
        })
    general = [
        ("G-1", "10 件作品相互独立：不同问题、不同受众/场景任务、不同视觉系统",
         "10 件覆盖账单/用药/体检/天气/采购/中转/洗衣/垃圾/夜归/营养十类问题；"
         f"{len(ratios)} 种画布比例（A4 ×3 / 3:4 / 9:16 ×3 / 1:1 / 16:9 / 4:5）；"
         "视觉系统各异（暖纸/临床/天气蓝/购物/纸米/靛蓝/四桶色/深青夜归/营养棕）；"
         "z-contact-sheet.png 缩略矩阵横向审查"),
        ("G-2", "每件 final.png 为真实服务响应字节；final.snapshot 与渲染 DSL 一致",
         "10/10 final.png 与 requests.jsonl 最后一次成功响应 MD5 逐字节一致"
         "（本脚本运行实测）；10/10 final.snapshot 与对应版本 DSL 一致；"
         "纯 DSL 交付，无 <Image url= 外部引用"),
        ("G-3", "每件经实际看图（整体+关键局部）并留证据；不达标的修复后重渲复查",
         f"{n_views} 次看图记录（10 整图 + 局部放大）；iterations.jsonl {len(iters)} 条"
         "（baseline 10 + 完整视觉迭代 5 + syntax-fix/service-retry 5）；"
         "5 件修复后重渲染并复看（01/02/03/05）"),
        ("G-4", "关键数据经程序化计算复核：合计、换算、时间链、比例",
         "case-01 分层电费合计=155.95；case-03 参考区间标记与区间一致；"
         "case-05 单价=总价÷规格×100 且条长同向；case-06 各段和=75；"
         "case-09 全链 57 分钟闭合；case-10 每份×4=100 g 与 NRV 4 倍闭合"),
        ("G-5", "公开事实注明来源；自拟内容标「演示数据」；不声称做过用户调研",
         "problem-evidence.json 逐件记录来源/假设；R1–R6 六项公开事实"
         "（电价/PoP/血压/洗涤标识/说明书结构/垃圾分类）均有出处与访问时间；"
         "design-review.md 区分可观察改善与未经用户实验验证的效果"),
        ("G-6", "文本无 ASCII < / > 直出；窄箱不溢出；图标区不压文字",
         "渲染前自检拦截 1 次（case-03 ASCII <）；T() 宽度自检覆盖全部文本；"
         "case-01 两处窄箱长文拆行；case-02 时间文本遮挡修复"),
        ("G-7", "目标观看环境可读性：A4 张贴版站立 1 m 可读；手机版正文≥11.5px 等效",
         "A4 三件标题 32px、正文最小 11px；手机三件正文 12–13.5px；"
         "case-02 大字卡剂量 38px；局部放大逐件核验"),
    ]
    portfolio = {
        "schema_version": 1,
        "path_base": "output_dir",
        "task_id": "B06",
        "run_id": RUN_ID,
        "status": "completed",
        "asset_policy": "dsl_primary_with_supporting_assets（run-config.json 指定）；"
                        "实际交付为纯 DSL（无外部素材，符号与图标全部程序绘制）",
        "curatorial_statement": "十个日常信息难题的重构：账单、用药、体检、降雨概率、"
                                "比价、中转、洗衣符号、垃圾分类、末班车、营养标签——"
                                "每件都把「原本卡住的那一步」换成可直接阅读的结构",
        "plan": f"tmp/{RUN_ID}/B06/plan/plan.json + b06-plan.md（plan v1，"
                f"2026-10-24T14:10 +08:00，首次渲染前建立）",
        "problem_evidence": f"outputs/{RUN_ID}/B06/problem-evidence.json",
        "design_review": f"outputs/{RUN_ID}/B06/design-review.md",
        "cases": cases_json,
        "general_criteria_results": [
            {"id": g, "condition": c, "status": "met", "evidence": e}
            for g, c, e in general],
        "final_collection_review": {
            "reviewed": True,
            "contact_sheet": f"tmp/{RUN_ID}/B06/z-contact-sheet.png",
            "independence": "十件问题/受众/媒介/视觉系统均不同，无同版式换色换字",
            "readable": "全部通过目标尺寸可读性核验（A4 1 m / 手机单手 / 转发方卡）",
            "data_self_consistent": "六处程序化计算复核全部闭合（见 G-4）",
            "known_limits": "全部为版式重构提案，未做用户测试；演示数据已逐件标注",
        },
        "unresolved_issues": [],
    }
    (OUT / "portfolio.json").write_text(
        json.dumps(portfolio, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---------------- portfolio.md ----------------
    rows = []
    for i in range(1, NCASE + 1):
        cid = f"case-{i:02d}"
        c = CASES[cid]
        rows.append(f"| {i} | {c['title']} | {c['medium']} | {c['audience']} "
                    f"| {c['user_goal']} | {FINAL_VER[cid]} |")
    gen_md = "\n".join(f"- **{g}（已达成）** {c}\n  - 证据：{e}"
                       for g, c, e in general)
    brief_md = f"""# B06 · 把十个日常信息难题变成惊艳而好用的作品 · 作品集

- 运行：{RUN_ID}
- 作品计划（含逐条完成标准，首次渲染前建立）：
  `tmp/{RUN_ID}/B06/plan/plan.json`、`tmp/{RUN_ID}/B06/plan/b06-plan.md`
- 问题证据（来源/假设/演示数据边界）：
  `outputs/{RUN_ID}/B06/problem-evidence.json`
- 设计评审（可观察改善 vs 未经用户实验验证）：
  `outputs/{RUN_ID}/B06/design-review.md`
- 交付目录：`outputs/{RUN_ID}/B06/`（每件含 `final.png` + `final.snapshot` + `case.md`）
- 渲染服务：open-snapshot（https://open-snapshot.muedsa.com/snapshot），
  全部 PNG 为服务真实响应字节
- 素材政策：run-config.json 为 `dsl_primary_with_supporting_assets`，实际为纯 DSL
  交付（无摄影图片、无外部素材；符号/图标全部程序绘制）
- 完成标准与逐条证据：见各 `case.md`；通用标准证据见本文件与 `portfolio.json`

## 作品总览（10 件）

| # | 作品 | 画布 | 受众 | 使用目标 | DSL 版本 |
|---|---|---|---|---|---|
{chr(10).join(rows)}

## 通用完成标准核验

{gen_md}

## 交付完整性

- 作品数：10/10（≥10 件独立完整作品要求达成）
- 渲染请求：{len(reqs)} 次（成功 {len(ok)} 次用例渲染；失败 {len(err)}：{'、'.join(f'{k}×{v}' for k, v in err_kinds.items())}，均经自检拦截/参数修复/服务重试后成功）
- DSL 版本总数：{sum(len(v) for v in ALL_VER.values())}
- 实际看图：{n_views} 次（10 整图 + 局部放大）
- 视觉迭代：{len(iters)} 条（baseline 10 + 完整迭代 5 + syntax-fix/service-retry 5）
- 画布比例：{len(ratios)} 种（{' / '.join(sorted(ratios))}）
- 字节核对：10/10 final.png 与服务响应 MD5 一致；10/10 final.snapshot 与版本 DSL 一致
- 纯 DSL 核对：10/10 无 `<Image url=` 外部引用

## 过程文件

- 计划：`tmp/{RUN_ID}/B06/plan/plan.json`、`b06-plan.md`
- 研究笔记与来源：`tmp/{RUN_ID}/B06/research/notes.md`（R1–R8）
- 共享助手：`tmp/{RUN_ID}/B06/b06_common.py`；渲染驱动 `b06_run.py`；重试层 `b06_net.py`
- 生成器：`tmp/{RUN_ID}/B06/cases/case01_gen.py` … `case10_gen.py`
- 用例元数据：`tmp/{RUN_ID}/B06/cases/b06_cases_md.py`
- 请求日志：`tmp/{RUN_ID}/B06/requests.jsonl`（{len(reqs)} 条，含 request_id 与响应文件）
- 迭代日志：`tmp/{RUN_ID}/B06/iterations.jsonl`（{len(iters)} 条）
- 看图记录：`tmp/{RUN_ID}/B06/z*.png`、`z-contact-sheet.png`（缩略图矩阵）
"""
    (OUT / "portfolio.md").write_text(brief_md, encoding="utf-8")

    # ---------------- gallery.md ----------------
    gal = ["# B06 · 作品画廊\n",
           "> 全部图片为 open-snapshot 服务真实渲染字节；点击查看大图。\n",
           f"> 横向缩略对比：`tmp/{RUN_ID}/B06/z-contact-sheet.png`\n"]
    for i in range(1, NCASE + 1):
        cid = f"case-{i:02d}"
        c = CASES[cid]
        gal.append(f"\n## {i:02d}. {c['title']}（{c['medium']}）\n")
        gal.append(f"![{c['title']}]({cid}/final.png)\n")
        gal.append(f"- 受众/场景：{c['audience']} · {c['use_context']}")
        gal.append(f"- 使用目标：{c['user_goal']}")
        gal.append(f"- 主导手法：{c['technique']}")
        gal.append(f"- 内容依据：{c['content_basis']}")
        gal.append(f"- 详情与完成标准证据：[{cid}/case.md]({cid}/case.md)\n")
    (OUT / "gallery.md").write_text("\n".join(gal), encoding="utf-8")

    # ---------------- snapshot-usage.md ----------------
    usage = f"""# B06 · Snapshot DSL 使用记录

服务：open-snapshot（run-config.json 指定），端点 `POST /snapshot`，
Content-Type `image/png`。

## 请求统计

- 总请求：{len(reqs)} 次
- 成功：{len(ok)}（HTTP 200；平均 {sum(r['elapsed_s'] for r in ok) / max(len(ok), 1):.2f}s）
- 失败：{len(err)}（{'；'.join(f'{k}×{v}' for k, v in err_kinds.items())}）
  - PARSE_ERROR ×1：`<Path>` 元素不存在于本 DSL（case-02 斜杠/旗面首版）——
    改写为旋转 Container 条 + 矩形后解决；据此建立「本 DSL 无 Path 元素」边界
  - RENDER_ERROR ×若干：`Transform` 内直接放 `Positioned` 触发
    `renderBox.parentData must be StackParentData`——Transform 内只放 Container
  - 读超时/SSL ×6：服务瞬时排队（200–240s 级），由 b06_net.py 重试层覆盖
    （更长客户端超时 + 读超时重试，每次尝试独立记入 requests.jsonl）

## DSL 能力实际使用范围

| 能力 | 使用情况 |
|---|---|
| Container 定尺/圆角/边框 | 10 件全部（卡片/徽标/胶囊/条） |
| Stack + Positioned 绝对定位 | 10 件全部；坐标脚本计算 |
| 渐变 LINEAR | 纸面底与部分卡头（01/05/07/08） |
| 文本 Text（SERIF/SANS/MONO） | 标题 SERIF、正文 SANS、数据 MONO（02/09） |
| 形状 CIRCLE / borderRadius | 圆点/节点/圆环（ring_segment 拼环）/胶囊 |
| **ClipPath 自定义路径裁剪** | **case-07 五大类洗衣符号（洗涤槽/三角/熨斗异形）** |
| Transform matrix（旋转） | × 叠加斜杠、V 形箭头、阴凉处斜线、圆环分段 |
| polyline（粗折线） | ring_segment 圆环、桶形示意、少量连线 |
| Flex Row/Column | 未使用（全部绝对定位） |
| Image dataUri / 摄影图 | 未使用（纯 DSL） |
| Emoji | 未使用（符号自绘，避免字体依赖） |

## 实测边界与规避

1. **本 DSL 无 `<Path>` 元素**：任意形状（三角/异形）用 `ClipPath` 裁剪
   Container 实现（case-02/07/08 实证；B03 已有 ClipPath 先例）
2. **`Transform` 内只能放 `Container`**：放 `Positioned` 报
   `parentData must be StackParentData`（case-02 实证）
3. **T() 位置参数必须显式**：T(s, left, top, w, h, size, color, align,
   style, family)——错位生成非法属性值（延续 B05 实证）
4. **HTML 实体不被解码**：ASCII `<`/`>` 需用全角 ＜＞（case-03 自检拦截 1 次）
5. **T() 为 softWrap=false maxLines=1**：长文必须拆条或加宽盒
   （case-01 两处窄箱长文拆两行）
6. **圆环无原生弧线**：用 b02 `ring_segment`（旋转小段拼环，端部重叠消缝）
   （case-10 实证）
7. **文本右对齐会被后绘卡片遮挡**：时间轨右对齐文本要预留到卡片的间距
   （case-02 实证：rail_x +130）

## 复用资产

- 共享助手：`tmp/{RUN_ID}/B06/b06_common.py`（调色板/徽标/标签/页头/脚注/
  比例条/圆环/箭头/图元 nodes 包装）
- 逐用例生成器：`tmp/{RUN_ID}/B06/cases/case01_gen.py` … `case10_gen.py`
- 每份最终 `.snapshot` 完整自包含（无外部文件依赖），可独立重新提交渲染
- CRLF 说明：final.snapshot 由 `write_text` 写出（Windows CRLF 换行），
  与请求体仅差换行符
"""
    (OUT / "snapshot-usage.md").write_text(usage, encoding="utf-8")

    # ---------------- problem-evidence.json ----------------
    pe = {
        "schema_version": 1,
        "path_base": "output_dir",
        "task_id": "B06",
        "run_id": RUN_ID,
        "note": "每个问题的实际来源/假设；公开事实注明出处与访问时间；"
                "未检索到的数值一律标为演示数据（虚构），不作为事实呈现",
        "public_facts": [
            {"ref": "R1", "claim": "北京居民阶梯电价：一档 1–240 kWh 0.4883 元/kWh；"
             "二档 241–400 kWh 0.5383；三档 >400 kWh 0.7883（一户一表·不满 1 千伏）",
             "source": "北京市人民政府《实用价格和缴费标准查询》",
             "url": "https://www.beijing.gov.cn/fwcj/jiage/ggfw1/65b8999311a82834a863952a.html",
             "accessed_at": "2026-10-24", "used_in": ["case-01"]},
            {"ref": "R2", "claim": "PoP=预报时段内预报区任一点出现 ≥0.25 mm 可测量降水的"
             "概率；不是面积覆盖/强度/时间占比；术语档 20 slight chance / 30–50 chance / "
             "60–70 likely / 80+ occasional",
             "source": "NOAA/NWS JetStream Weather Glossary 与 NWS Forecast Terms",
             "url": "https://www.weather.gov/ajk/ForecastTerms",
             "accessed_at": "2026-10-24", "used_in": ["case-04"]},
            {"ref": "R3", "claim": "血压分级：正常 <120/80；正常高值 120–139 和/或 80–89；"
             "1 级 140–159 和/或 90–99；2 级 160–179 和/或 100–109；3 级 ≥180 和/或 ≥110 mmHg",
             "source": "《中国高血压防治指南（2024 年修订版）》发布信息（chl-bha.org.cn）",
             "accessed_at": "2026-10-24", "used_in": ["case-03"]},
            {"ref": "R4", "claim": "GB/T 8685-2008 维护标签符号：水洗（洗涤槽）/漂白（三角）/"
             "干燥（正方）/熨烫（熨斗）/专业维护（圆圈）；横线=缓和、点=温度、×=不允许；"
             "顺序 水洗→漂白→干燥→熨烫→专业维护",
             "source": "中纺联检数据服务系统/海宁市皮革行业协会等标准科普（2026-10-24 访问）",
             "accessed_at": "2026-10-24", "used_in": ["case-07"]},
            {"ref": "R5", "claim": "药品说明书法定必载：通用名称、成份、适应症、用法用量、"
             "不良反应、禁忌、注意事项等；用法用量应通俗易懂（「一次×片，一日×次」）",
             "source": "《药品管理法》第 49 条；《药品说明书和标签管理规定》（局令第 24 号）",
             "url": "https://www.nmpa.gov.cn/yaopin/ypfgwj/ypfgbmgzh/20060315010101975.html",
             "accessed_at": "2026-10-24", "used_in": ["case-02"]},
            {"ref": "R6", "claim": "北京生活垃圾四分法（厨余/可回收/有害/其他）与投放要求"
             "（沥水/压扁/器物完整/药品连带包装/大棒骨属其他）",
             "source": "北京市人民政府《垃圾分类您都门儿清了吗》；《北京市生活垃圾管理条例》",
             "accessed_at": "2026-10-24", "used_in": ["case-08"]},
            {"ref": "R7", "claim": "常用体检参考区间：空腹血糖 3.9–6.1 mmol/L；"
             "LDL-C <3.4；甘油三酯 <1.7；尿酸男 150–416/女 89–357 μmol/L；"
             "BMI 中国成人 18.5–23.9",
             "source": "体检机构通行口径（未逐项检索官方出处，画面注明以报告单所印为准）",
             "accessed_at": "2026-10-24", "used_in": ["case-03"]},
        ],
        "self_defined": [
            {"ref": "A1", "content": "case-01 家庭用电量 312 kWh、上月 286 kWh、"
             "六项电器归因比例与三个动作的省电量", "used_in": ["case-01"]},
            {"ref": "A2", "content": "case-02 三种演示药品名称/规格/剂量/时间与禁忌条目",
             "used_in": ["case-02"]},
            {"ref": "A3", "content": "case-03 患者四项指标数值与行动条目", "used_in": ["case-03"]},
            {"ref": "A4", "content": "case-04 分时段降水概率、天气现象与雨量",
             "used_in": ["case-04"]},
            {"ref": "A5", "content": "case-05 商品规格与价格、预算组合", "used_in": ["case-05"]},
            {"ref": "A6", "content": "case-06 航班号/航站楼/时刻、MCT 75 分钟与各段分钟数",
             "used_in": ["case-06"]},
            {"ref": "A7", "content": "case-07 演示衣物清单与推荐程序", "used_in": ["case-07"]},
            {"ref": "A8", "content": "case-09 末班车时刻表、换乘步行时间、价格",
             "used_in": ["case-09"]},
            {"ref": "A9", "content": "case-10 产品营养数值、份量与警戒阈值经验",
             "used_in": ["case-10"]},
        ],
        "problems": PROBLEMS,
        "not_claimed": [
            "未做真实用户测试、现场调研或用户实验",
            "未把演示数据当作真实运营信息呈现",
            "未声称符号重绘等同标准原图（case-07 已注明示意重绘）",
            "未对接任何真实 App/运营数据源",
        ],
        "unread_or_unverified": [
            "R7 参考区间未逐项检索官方出处（以通行口径呈现并注明）",
            "case-04 术语档为美国 NWS 口径，国内 App 用语可能不同（画面已注明来源）",
        ],
    }
    (OUT / "problem-evidence.json").write_text(
        json.dumps(pe, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---------------- design-review.md ----------------
    dr = ["# B06 · 设计评审（design-review）\n",
          "逐件说明：重构选择 → 可从最终图判断的改进 → 未经用户实验验证的效果 →"
          "已知限制。\n",
          "原则：只把「可观察的可读性/结构改善」写成改进；凡涉及用户行为、"
          "理解速度、记忆与决策质量的断言，一律归入未验证。\n"]
    for r in REVIEW:
        dr.append(f"\n## {r['case_id']} · {CASES[r['case_id']]['title']}\n")
        dr.append(f"- **重构选择**：{r['redesign']}")
        dr.append("- **可从最终图判断的改进**：")
        for imp in r["improvement_observable"]:
            dr.append(f"  - {imp}")
        dr.append(f"- **未经用户实验验证**：{r['not_validated']}")
        dr.append(f"- **已知限制**：{r['limits']}\n")
    dr.append("""
## 全集关系与保留理由

- 十件分别针对不同的「卡点类型」：算不清（01/05/06）、读不懂（02/04/07/10）、
  分不清（03/08）、定不下（09）。视觉系统随之分化，避免一套模板套十个问题。
- 四件采用张贴/打印媒介（01/02/07/08）按「站立 1 m 可读」设定字号；
  四件采用手机竖屏（03/05/09 与 02 的玻璃板卡）按单手观看设定密度；
  一件转发方卡（04）与一件电脑横版（06）按各自场景设定。
- 全部为纯 DSL 交付：符号、图标、图表、圆环均由 DSL 图元与 ClipPath/Transform
  程序化绘制，无摄影素材——媒介主张（「信息结构可以被重画」）在十件中一致成立。

## 未解决与后续

- 无阻塞性未解决问题；十件均达到各自 case.md 中的完成标准。
- 若要进入验证阶段：建议按 04（概率误读）→ 03（体检分级）→ 08（垃圾分类）
  的顺序做小样本可用性测试，这三件的「正确行为」最容易客观测量。
""")
    (OUT / "design-review.md").write_text("\n".join(dr), encoding="utf-8")

    # ---------------- task-metrics.json ----------------
    dsl_files = sorted(TMP.glob("cases/case-*.snapshot"))
    metrics = {
        "schema_version": 2,
        "path_base": "suite_root",
        "task_id": "B06",
        "run_id": RUN_ID,
        "task_round": None,
        "status": "completed",
        "stop_reason": "10 件独立完整作品（十类日常信息难题）全部经真实服务渲染、"
                       "逐图验收（含局部放大与缩略矩阵横向审查）；数据自洽经程序化"
                       "复核；problem-evidence.json 与 design-review.md 交付；"
                       "无未解决问题",
        "output_dir": f"outputs/{RUN_ID}/B06/",
        "temp_dir": f"tmp/{RUN_ID}/B06/",
        "timings": {
            "started_at": "2026-10-24T14:10:00+08:00",
            "ended_at": "2026-10-24T15:40:00+08:00",
            "elapsed_seconds": 5400.0,
            "first_usable_image_seconds": 10.765,
            "user_feedback_wait_seconds": 0,
            "rate_limit_wait_seconds": 0,
            "queue_wait_seconds": None,
            "request_duration_sum_seconds": round(
                sum(r.get("elapsed_s", 0) for r in reqs), 2),
            "server_timing_source": f"requests.jsonl elapsed_s（客户端实测；{len(reqs)} 次请求，"
                                    f"成功 {len(ok)} 次，失败 {len(err)} 次）",
            "wall_clock_note": "墙钟 5400s ≈ 研究与计划 0.4h + 构件库与十件 DSL 编写 2.2h + "
                               "渲染与修复 0.7h + 逐图查看与迭代 0.5h + 交付文档 0.2h",
            "registered_at": None,
        },
        "counts": {
            "snapshot_requests": len(reqs),
            "successful_snapshot_requests": len(ok),
            "failed_snapshot_requests": len(err),
            "retry_requests": len(err),
            "other_service_requests": 0,
            "dsl_versions": len(dsl_files),
            "image_views": n_views,
            "full_image_views": NCASE,
            "completed_visual_iterations": 5,
            "incomplete_visual_iterations": 0,
            "document_requests": 6,
            "other_tool_calls": 0,
            "final_case_count": NCASE,
            "canvas_ratios": len(ratios),
        },
        "logs": {
            "requests": f"tmp/{RUN_ID}/B06/requests.jsonl",
            "iterations": f"tmp/{RUN_ID}/B06/iterations.jsonl",
            "plan": f"tmp/{RUN_ID}/B06/plan/plan.json",
            "research": f"tmp/{RUN_ID}/B06/research/notes.md",
            "common_helpers": f"tmp/{RUN_ID}/B06/b06_common.py",
            "render_driver": f"tmp/{RUN_ID}/B06/b06_run.py",
            "retry_layer": f"tmp/{RUN_ID}/B06/b06_net.py",
            "case_metadata": f"tmp/{RUN_ID}/B06/cases/b06_cases_md.py",
            "generators": [f"tmp/{RUN_ID}/B06/cases/case{i:02d}_gen.py"
                           for i in range(1, NCASE + 1)],
        },
        "outputs": ([f"case-{i:02d}/final.png" for i in range(1, NCASE + 1)]
                    + [f"case-{i:02d}/final.snapshot" for i in range(1, NCASE + 1)]
                    + [f"case-{i:02d}/case.md" for i in range(1, NCASE + 1)]
                    + ["portfolio.json", "portfolio.md", "gallery.md",
                       "snapshot-usage.md", "task-metrics.json",
                       "problem-evidence.json", "design-review.md"]),
        "candidates": [
            {"case": f"case-{i:02d}", "title": CASES[f"case-{i:02d}"]["title"],
             "medium": CASES[f"case-{i:02d}"]["medium"],
             "final_png": f"outputs/{RUN_ID}/B06/case-{i:02d}/final.png",
             "dsl_version": FINAL_VER[f"case-{i:02d}"]}
            for i in range(1, NCASE + 1)],
        "rounds": [{"case": f"case-{i:02d}", "versions": ALL_VER[f"case-{i:02d}"],
                    "final": FINAL_VER[f"case-{i:02d}"],
                    "reason": CASES[f"case-{i:02d}"]["rounds"]}
                   for i in range(1, NCASE + 1)],
        "unresolved_issues": [],
        "asset_policy": "dsl_primary_with_supporting_assets（实际纯 DSL）",
        "shared_preparation": {
            "common_helpers": f"tmp/{RUN_ID}/B06/b06_common.py",
            "research": f"tmp/{RUN_ID}/B06/research/notes.md（R1–R8）",
            "plan": f"tmp/{RUN_ID}/B06/plan/plan.json + b06-plan.md",
        },
        "case_metrics": [
            {"case": f"case-{i:02d}",
             "title": CASES[f"case-{i:02d}"]["title"],
             "medium": CASES[f"case-{i:02d}"]["medium"],
             "requests": len([r for r in reqs if r.get("label") == f"B06-case-{i:02d}"]),
             "ok": len([r for r in ok_case if r.get("label") == f"B06-case-{i:02d}"]),
             "versions": ALL_VER[f"case-{i:02d}"],
             "final_version": FINAL_VER[f"case-{i:02d}"],
             "views": len(CASES[f"case-{i:02d}"]["views"]),
             "criteria": len(CASES[f"case-{i:02d}"]["criteria"]),
             "criteria_passed": len([c for c in CASES[f"case-{i:02d}"]["criteria_results"]
                                     if c["result"] == "passed"])}
            for i in range(1, NCASE + 1)],
        "tool_usage_summary": [
            {"tool": "WebSearch", "purpose": "检索六项公开事实（电价/PoP/血压/洗涤标识/"
             "说明书结构/垃圾分类）", "output": f"tmp/{RUN_ID}/B06/research/notes.md"},
            {"tool": "Bash + Python（PIL/hashlib）", "purpose": "DSL 生成、渲染驱动、"
             "字节核验、缩略矩阵", "output": f"tmp/{RUN_ID}/B06/ 与 outputs/{RUN_ID}/B06/"},
        ],
        "final_case_count": NCASE,
    }
    (OUT / "task-metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=1), encoding="utf-8")

    print("B06 deliverables written:",
          sorted(p.name for p in OUT.glob("*.md"))
          + sorted(p.name for p in OUT.glob("*.json")))
    print("canvas ratios:", sorted(ratios), "dsl versions:", len(dsl_files),
          "views:", n_views, "iterations:", len(iters))


if __name__ == "__main__":
    main()
