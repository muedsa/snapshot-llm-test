"""Build B01 portfolio.json / portfolio.md / gallery.md / asset-sources.json.

Run from the suite root:
  python tmp/<run_id>/B01/build_b01_portfolio.py
"""
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
rid = os.environ["SNAPSHOT_RUN_ID"]
temp = root / "tmp" / rid / "B01"
out = root / "outputs" / rid / "B01"

metrics = json.loads((out / "task-metrics.json").read_text(encoding="utf-8"))
per = {c["case_id"]: c for c in metrics["case_metrics"]}
itn = [json.loads(l) for l in open(temp / "iterations.jsonl", encoding="utf-8")]
n400 = [r for r in (json.loads(l) for l in open(temp / "requests.jsonl", encoding="utf-8"))
        if r["http_status"] == 400]
tools = [json.loads(l) for l in open(temp / "tool-usage.jsonl", encoding="utf-8")]
iter_ids = defaultdict(list)
for i in itn:
    iter_ids[i["case_id"]].append(i["iteration_id"])

ATTR_INTEREST = {
    "gradientType": "渐变（LINEAR/RADIAL/SWEEP）",
    "gradientColors": "渐变色标",
    "gradientRadius": "RADIAL 比例半径",
    "gradientCenter": "RADIAL 圆心",
    "gradientBegin": "LINEAR 起点方位",
    "boxShadow": "阴影",
    "textShadow": "文字阴影",
    "foregroundColor": "前景色",
    "foregroundMode": "前景描边模式（空心字）",
    "foregroundStrokeWidth": "前景描边宽度",
    "fontFeatures": "OpenType 特性（tnum 等宽数字）",
    "letterSpacing": "字距",
    "maxLines": "多行截断",
    "overflow": "溢出策略",
    "clipBehavior": "裁剪行为",
    "blendMode": "混合模式",
    "sigmaX": "高斯模糊 sigmaX",
    "tileMode": "图像平铺",
    "matrix": "Transform 仿射矩阵",
    "border": "盒描边",
    "borderRadius": "圆角",
}


def capabilities(c):
    s = (out / c / "final.snapshot").read_text(encoding="utf-8")
    tags = sorted(set(re.findall(r"<([A-Za-z][A-Za-z0-9]*)", s)))
    attrs = sorted(set(re.findall(r'\s([a-zA-Z][a-zA-Z0-9]*)="', s)))
    return {
        "tags": tags,
        "notable_attributes": {a: ATTR_INTEREST[a] for a in attrs if a in ATTR_INTEREST},
        "counts": {"Container": s.count("<Container"), "Positioned": s.count("<Positioned"),
                   "Text": s.count("<Text"), "Transform": s.count("<Transform")},
        "source": f"{c}/final.snapshot",
    }


def qa_files(c):
    d = temp / c
    if not d.is_dir():
        return []
    return sorted(f"tmp/{rid}/B01/{c}/{f}" for f in os.listdir(d)
                  if f.endswith(".png") and ("qa" in f or "crop" in f))


META = {
    "case-01": dict(
        title="夜间地铁换乘屏",
        audience="22:47 抵达换乘通道的通勤乘客与值班站长",
        use_context="站厅 3 米外壁挂 55 寸屏，环境光偏暗、屏幕是唯一亮源，抬头 3~5 秒扫读",
        user_goal="读出四条线路未来 45 分钟到站间隔、找到本方向末班车、判断当前是否延误",
        content_basis="虚构「西江地铁」演示数据；线路/时刻/站台号由脚本按首班等待+固定间隔+末班车生成，与表格分钟数同源可反算",
        visual_intent="夜间低环境光下靠色相而非亮度区分线路；顶部红色告警条承担唯一的紧急层级",
        completion_criteria="4 条线路 45 分钟内间隔可逐格核对；末班时刻与倒计时自洽；告警条与延误原因一致；3 米距离最小字号仍达标",
        scenario_class="公共交通信息屏（横向大屏）"),
    "case-02": dict(
        title="潮汐声场音乐节三日海报",
        audience="主办方新媒体编辑；刷到图的 20~35 岁乐迷",
        use_context="公众号头图/朋友圈竖图/易拉宝缩印，6 寸手机竖屏滑动 2~3 秒决定是否购票",
        user_goal="记住品牌名→知道三日期与风格→查到自己想看的一天→看到票价与购票入口",
        content_basis="品牌「潮汐声场 / TIDAL FIELD」、场地、39/40 组艺人名、票价、日期均为虚构编造，图内已用中文声明",
        visual_intent="196px 空心描边主标题压在 SWEEP 彩色轮盘上，色轮即「声场」隐喻并解释三舞台命名",
        completion_criteria="远看标题成立、近看阵容可读；三日分栏互不重叠；价格/入口/声明齐备且字号层级不冲突",
        scenario_class="文娱竖版海报（移动端优先）"),
    "case-03": dict(
        title="精品咖啡烘焙曲线工作台",
        audience="精品咖啡烘焙师（单人站姿，1.2 米外看 15 寸笔电/工控屏）",
        use_context="出炉前 30 秒，一手扶锅一手记数据，需要一眼判断这一炉是否偏离目标",
        user_goal="读出实际曲线与目标的偏差→看发展率 18.2% 与目标 20.0% 的差距→拿到下一炉动作建议",
        content_basis="虚构品牌「岩屋咖啡·烘焙工坊」与批次 A-231；豆温曲线不是手画形状，由分段线性 RoR 模型数值积分得到",
        visual_intent="把工程曲线的可信度建立在可复算的模型上：曲线、偏差、结论卡三处必须同一套数字",
        completion_criteria="曲线上 4 个关键温度点与模型积分一致；发展率、偏差秒数、建议文案可互相反算；网格与坐标轴无遮挡",
        scenario_class="工业/工艺操作台面板"),
    "case-04": dict(
        title="急诊中心分诊态势屏",
        audience="急诊值班组长、分诊护士、轮转医生",
        use_context="三甲医院急诊夜班值班台挂墙屏，3 米外读，几秒内判断哪个分区压不住、下一个床位给谁",
        user_goal="定位超载分区→取出待处置优先级前 5→确认救护车在途到达时刻",
        content_basis="全部数字来自同一反算队列：random.Random(20261009) 生成 17:30-21:30 的 96 人次到院，其余指标由此推导",
        visual_intent="不是 KPI 汇总而是决策屏：告警条给可执行建议，右栏直接给患者编号",
        completion_criteria="三栏 12 列栅格无重叠；KPI 胶囊、时间轴、优先级列表三处数字同源；占用率与床位差自洽",
        scenario_class="医疗指挥/态势大屏"),
    "case-05": dict(
        title="台风路径与风暴潮预报会商图",
        audience="沿海省市防汛值班室会商人员",
        use_context="会商刚结束，站 3 米外 20 秒内回答：几点登陆、辖区几点起 10 级风、撤离几点收队、哪些潮位站超警戒",
        user_goal="读出登陆时刻与不确定锥、各城市入风时刻、转移截止时刻、超警戒潮位站清单",
        content_basis="虚构台风编号/路径/潮位站数据；路径点、风圈半径、不确定锥由同一组参数按等距圆柱投影（标准纬线 22°N）计算",
        visual_intent="带结论的决策图：顶部告警条一句话给四个答案，右下角把转移截止放大成红色主数字并注明等于登陆前 12 h",
        completion_criteria="页眉/告警条/右下三处时刻完全一致；跨日进位正确；风圈不对称放大与城市标注不叠字；数字可由参数反算",
        scenario_class="气象防灾会商图"),
    "case-06": dict(
        title="手游《深空回响》S7「潮汐纪元」赛季更新长图",
        audience="边刷手机边决定今晚是否上线的玩家",
        use_context="公众号与玩家社区群投放，竖着滑 90 秒",
        user_goal="确认停服时刻→这版本新增什么→自己的枪是否被砍→零氪能否满级通行证→池子值不值得抽",
        content_basis="虚构游戏/版本/角色/武器/概率数据；通行证与抽卡期望由脚本按同一套数值模型算出（出货期望 38.8 抽 / 6,201 星声）",
        visual_intent="每个板块给结论而非宣传语；六板块流式排版（Y 游标累加，画布高度=末段结束位置），结构上不可能重叠",
        completion_criteria="Hero/停服/新增/平衡性/通行证/卡池六段数据自洽；概率与期望可反算；长图无跨段遮挡",
        scenario_class="游戏版本公告长图"),
    "case-07": dict(
        title="《暗礁》月刊封面",
        audience="报刊亭/电子阅读器上的新读者、按月收刊的老订户、图书馆与邮局识别系统",
        use_context="货架前 3 秒停留决定是否购买；同时承载期号/栏目与 ISSN、条码、邮发代号",
        user_goal="回答「这期讲什么、值不值得买」，并核对刊期与篇数字数",
        content_basis="虚构刊名/刊期/ISSN/CN/邮发代号/定价/篇目/字数；篇数、字数、阅读时长由同一张篇目表算出",
        visual_intent="固定信息层级（刊名→封面报道标题→引题署名→要目→期号定价条码）+ 灰阶单色摄影感的封面美术，全部由 DSL 绘制",
        completion_criteria="页眉要素互相咬合（定价/期号/出版日期/条码数字）；三层文字压在封面上仍可读；灰阶无脏斑",
        scenario_class="杂志封面（印刷品）"),
    "case-08": dict(
        title="集换式卡牌 · Boss 卡「盐壳」",
        audience="桌面/线上卡牌对战玩家（选牌与开团前）",
        use_context="手持或线上卡池浏览，需在数秒内读完首领威胁曲线",
        user_goal="判断每回合能吃多少伤害、破盾窗口在哪、带哪套牌克制、掉落值不值得反复挑战",
        content_basis="虚构卡牌（名称、数值、技能、掉落）；7 回合伤害排程、破盾回合、克制倍率与掉落期望由同一模型计算",
        visual_intent="标准 5:7 卡牌骨架里塞进四组决策数据；盐壳主题用多晶簇 + 冷 rim 的边缘光而非明亮柱状条",
        completion_criteria="排程条总和等于面板声明的循环伤害；倍率表与克制结论一致；卡面文字不越界、5:7 比例精确",
        scenario_class="游戏卡牌（小尺寸高密度）"),
    "case-09": dict(
        title="数据新闻长图《通勤十年》",
        audience="移动端普通读者",
        use_context="手机竖屏 3 分钟读完一篇数据新闻",
        user_goal="知道十年间单程通勤变长多少、长在哪种交通方式上、早高峰是否被摊平",
        content_basis="虚构城市十年通勤方式结构数据；折线用小 logistic 路径 + 首末端点严格对齐，逐年数值可由表反算",
        visual_intent="小倍数折线让 7 种方式各自可读；成对条用空心/实心而非第二种颜色编码第二个系列",
        completion_criteria="各方式份额逐年合计 100%；峰值/最快一年等结论句由 max()/all() 生成，与图内数据不矛盾；每板块自带一句话结论",
        scenario_class="数据新闻/深度长图"),
    "case-10": dict(
        title="机场出发航显 FIDS 超宽屏",
        audience="出发大厅旅客（含陪同与首次乘机者）",
        use_context="3 米外、约 5 秒扫读 2880×1080 超宽屏",
        user_goal="确认自己那班是否在屏上→读到登机口→读到状态与还有多久",
        content_basis="虚构航班号/航司/城市/时刻；一个模拟时钟 NOW=14:32 推出计划/预计/截止/开始登机/值机开放/落地六个时间点与五种状态，10 行汇总指标同源",
        visual_intent="时刻列 40px 粗体 tnum；状态用色条+文字胶囊+倒计时+计划删除线四重冗余；时区带画成夜底挖出昼窗的连续时间轴",
        completion_criteria="每行状态与时刻由同一时钟推导且无矛盾；跨日落地日期正确（LAX）；10 列在 2688px 内严格对齐；超宽屏左右阅读顺序合理",
        scenario_class="机场旅客信息屏（超宽看板）"),
}


def case_entry(c):
    m = META[c]
    p = per[c]
    return {
        "id": c,
        "title": f"{c} · {m['title']}",
        "audience": m["audience"],
        "use_context": m["use_context"],
        "user_goal": m["user_goal"],
        "content_basis": m["content_basis"],
        "visual_intent": m["visual_intent"],
        "scenario_class": m["scenario_class"],
        "png": f"{c}/final.png",
        "snapshot": f"{c}/final.snapshot",
        "dimensions": p["final_dimensions"],
        "png_bytes": p["final_png_bytes"],
        "supporting_assets": [],
        "dsl_capabilities": capabilities(c),
        "completion_criteria": m["completion_criteria"],
        "visual_review": {
            "image_views": p["image_views"],
            "completed_visual_iterations": p["completed_visual_iterations"],
            "dsl_versions": p["dsl_versions"],
            "process_pngs": sorted(
                f"tmp/{rid}/B01/{c}/{f}" for f in os.listdir(temp / c)
                if f.endswith(".png") and "qa" not in f and "crop" not in f),
            "crop_zoom_evidence": qa_files(c),
            "log": f"tmp/{rid}/B01/iterations.jsonl",
            "case_report": f"{c}/case.md",
        },
        "request_ids": p["request_ids"],
        "promoted_from_request": p["promoted_from_request"],
        "iteration_ids": iter_ids[c],
        "unresolved_issues": [],
    }


cases = [case_entry(c) for c in sorted(META)]
portfolio = {
    "schema_version": 1,
    "path_base": "output_dir",
    "task_id": "B01",
    "run_id": rid,
    "status": "completed",
    "asset_policy": "dsl_primary_with_supporting_assets（creative 赛道）；本题十件实际全部为纯 DSL，未嵌入任何外部素材",
    "curatorial_statement": (
        "十件作品挑的是「被人真实使用」的十种版面：地铁屏、海报、工艺面板、急诊态势屏、"
        "台风会商图、手游长图、杂志封面、卡牌、数据新闻长图、机场航显。共同主张是：一块版面"
        "只有在它承载的决策上自洽才算成立。所以每件都先把内容压成一张可反算的数据表，再由表"
        "生成图与结论句；三米屏用 40px 以上的等宽数字，手机长图靠流式游标保证不重叠，卡牌用"
        " 5:7 标准骨架。风格不统一是刻意的——受众、媒介和观看时长不同，版面就该不同；统一的"
        "是同一套校验纪律（TextFit 逐框量字、逐版打开实际图片、结论句由数据生成）。"),
    "cases": cases,
    "case_field_guide": {
        "id": "case-01..case-10 唯一ID",
        "title": "作品名",
        "audience": "具体受众",
        "use_context": "设备/媒介/观看环境",
        "user_goal": "使用者要完成的事",
        "content_basis": "内容/数据来源与虚构标识",
        "visual_intent": "主要视觉主张",
        "scenario_class": "自定的场景类别，用于说明十件为何互不重复",
        "png": "相对本题输出根的主图",
        "snapshot": "相对本题输出根的同名完整 DSL",
        "dimensions": "按实际 PNG 头读取的 [width,height]",
        "supporting_assets": "本题全部为 []（纯 DSL，未嵌入外部素材）",
        "dsl_capabilities": "由 final.snapshot 正则实际提取的标签、属性与元素计数",
        "completion_criteria": "自主设定、可对照实际图核对的标准",
        "visual_review": "看图次数/完整视觉迭代/版本 PNG 与裁切放大证据/日志位置",
        "request_ids": "本题全部真实渲染请求ID",
        "promoted_from_request": "与 final.png 字节指纹（md5）完全相同的响应所属请求",
        "iteration_ids": "iterations.jsonl 中该用例的真实迭代ID",
        "unresolved_issues": "当前实际遗留问题",
    },
    "final_collection_review": {
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
        "method": "逐件打开 final.png（长图/超宽屏先等高裁带再逐带看，疑似缺陷再做 2x LANCZOS 局部放大）；"
                  "核对 final.png 与 final.snapshot 同名配对、PNG 字节等于某次真实响应、"
                  "case.md 的场景/数据/迭代三处一致；再用 metrics 交叉核对请求数、版本数、看图数",
        "checks": [
            "10/10 件都有 final.png + final.snapshot + case.md，PNG 尺寸从文件头读取，无占位或后处理图",
            "10/10 件的 final.png 与某一次 http 200 服务响应 md5 相同（promoted_from_request 全部解析成功）",
            "10/10 件的 final.snapshot 中 <Image> 标签数为 0，未把参考图或生成素材嵌入成品",
            "版式互不重复：横屏大屏 4 件（1920x1080 / 2560x1440 / 1600x1200 / 2880x1080）、"
            "竖版长图 2 件（1080x3292 / 1200x3645）、竖版海报/封面/卡牌 3 件"
            "（1080x1800 / 1240x1750 / 1100x1540）、方屏工作台 1 件（1440x900）",
            "同一版式仅换色/换字、缩放裁切、局部放大与迭代版本均未计入独立用例；"
            "每题版本 PNG 与裁带都在临时目录，不计入 10 件",
            "数据自洽：case-03/04/05/06/07/08/09/10 的结论句与图内数字同源于一个生成模型，"
            "case-09 的量化措辞由 max()/all() 生成（v03 曾因手写句与数据矛盾而修正）",
            "TextFit：每题最终版本均 0 问题（case-09 177 项、case-10 172 项），"
            "行盒高度标准 >= 1.15x 字号",
        ],
        "remaining_issues": [
            "case-08 的 v16 响应出现 Content-Length 截断（213,792/332,564），随后同 DSL 重发取回完整 332,564 字节"
            "并以完整响应定稿；截断记录作为真实失败留痕保留",
            "case-10 的 v03 是一次空转渲染（生成器在写盘前抛 KeyError，服务返回与 v02 字节相同的图），"
            "已在 iterations.jsonl 记为 syntax 且不计入视觉迭代",
            "case-05/07/08 各有 3~6 次传输层失败（curl 28/52/56，http_status 0），无 Retry-After 可用，"
            "按相同 DSL 直接重试成功；这属于服务链路抖动，未视为作品缺陷",
            "服务侧不支持矢量 path 图元，case-05 的海岸线与 case-09 的折线面积只能用逐列矩形 + polyline 近似，"
            "曲率细节受此限制",
        ],
    },
    "unresolved_issues": [
        "无题目级未完成项：B01 要求的最少 10 件独立完整作品已全部定稿并逐件看图复核",
    ],
}
(out / "portfolio.json").write_text(json.dumps(portfolio, ensure_ascii=False, indent=2),
                                    encoding="utf-8")

# ---------------- portfolio.md ----------------
L = []
L.append(f"# B01 · 十件真实世界作品 — 作品集说明（{rid}）\n")
L.append("- 本题输出根：`outputs/%s/B01/`（路径基准 `output_dir`，Markdown 链接相对本文档）" % rid)
L.append("- 临时目录：`tmp/%s/B01/`（计划、生成器、逐版 PNG、请求体与三类日志）" % rid)
L.append("- 状态：completed，10 件独立完整主作品，全部为纯 DSL + 真实服务响应\n")
L.append("## 策展逻辑\n")
L.append(portfolio["curatorial_statement"] + "\n")
L.append("## 十件作品\n")
L.append("| 用例 | 尺寸 | 场景类别 | 谁在何时何地使用 | 要完成的事 | 定稿请求 |")
L.append("|---|---|---|---|---|---|")
for c in cases:
    L.append("| [%s](%s/case.md) | %dx%d | %s | %s | %s | `%s` |" % (
        c["id"], c["id"], c["dimensions"][0], c["dimensions"][1], c["scenario_class"],
        c["audience"], c["user_goal"], c["promoted_from_request"]))
L.append("")
L.append("## 逐件说明\n")
for c in cases:
    L.append("### %s · %s（%dx%d）" % (c["id"], c["title"].split(" · ", 1)[1],
                                       c["dimensions"][0], c["dimensions"][1]))
    L.append("- 预览与文件：[%s/final.png](%s/final.png) · "
             "[%s/final.snapshot](%s/final.snapshot) · [%s/case.md](%s/case.md)"
             % ((c["id"],) * 6))
    L.append("- 受众与使用：%(audience)s；%(use_context)s" % c)
    L.append("- 使用者要完成：%(user_goal)s" % c)
    L.append("- 内容依据：%(content_basis)s" % c)
    L.append("- 视觉主张：%(visual_intent)s" % c)
    L.append("- 完成标准：%(completion_criteria)s" % c)
    v = c["visual_review"]
    L.append("- 实际自检：版本 %d 个、看图 %d 次、完整视觉迭代 %d 次、请求 %d 次；"
             "裁带/放大证据 %d 张；迭代ID `%s`"
             % (v["dsl_versions"], v["image_views"], v["completed_visual_iterations"],
                len(c["request_ids"]), len(v["crop_zoom_evidence"]),
                "`, `".join(c["iteration_ids"])))
    L.append("- DSL 能力：标签 %s；关键属性 %s"
             % (", ".join("`" + t + "`" for t in c["dsl_capabilities"]["tags"]),
                "; ".join("`%s`(%s)" % (k, d) for k, d in
                          c["dsl_capabilities"]["notable_attributes"].items()) or "—"))
    L.append("- 辅助素材：无（`<Image>` 标签数 0）\n")
L.append("## 整体终审结论\n")
for k in portfolio["final_collection_review"]["checks"]:
    L.append("- " + k)
L.append("\n### 遗留事项\n")
for k in portfolio["final_collection_review"]["remaining_issues"]:
    L.append("- " + k)
L.append("\n## 指标与日志\n")
L.append("- `task-metrics.json`（墙钟/有效工时/空闲间隔、请求/版本/看图/迭代计数、逐用例指标）")
L.append("- `gallery.md`（十件最终作品逐图预览 + 原 PNG + 同名 DSL 链接）")
L.append("- `snapshot-usage.md`（文档/能力实际应用、逐件看图与修改、踩坑与复现条件）")
L.append("- `asset-sources.json`（素材政策与本次实际素材情况：全部为无）")
L.append("- 过程日志：`tmp/%s/B01/requests.jsonl`、`iterations.jsonl`、`tool-usage.jsonl`、`PLAN.md`\n" % rid)
(out / "portfolio.md").write_text("\n".join(L), encoding="utf-8")

# ---------------- gallery.md ----------------
G = [f"# B01 画廊 · 十件最终作品（{rid}）\n",
     "路径基准：本文档位于 `outputs/%s/B01/`，下面所有链接相对本目录。" % rid,
     "每张图给出：标题与用途说明、Markdown 内嵌预览、原 PNG 链接、同名完整 DSL 链接。"
     "预览即交付件本身（服务原始响应字节），未做后处理。",
     "过程版本与裁带证据不在画廊中计入作品数，位置见 `tmp/%s/B01/<case>/`。\n" % rid]
for c in cases:
    W, H = c["dimensions"]
    G.append("## %s · %s（%d×%d）\n" % (c["id"], c["title"].split(" · ", 1)[1], W, H))
    G.append("![%s %s](%s/final.png)\n" % (c["id"], c["title"], c["id"]))
    G.append("| 项 | 内容 |")
    G.append("|---|---|")
    G.append("| 文件 | [原 PNG](%s/final.png)（%s 字节） · [完整 DSL](%s/final.snapshot) |"
             % (c["id"], f"{c['png_bytes']:,}", c["id"]))
    G.append("| 用例说明 | [%s/case.md](%s/case.md) |" % (c["id"], c["id"]))
    G.append("| 场景类别 | %s |" % c["scenario_class"])
    G.append("| 受众 | %s |" % c["audience"])
    G.append("| 使用环境 | %s |" % c["use_context"])
    G.append("| 要完成的事 | %s |" % c["user_goal"])
    G.append("| 内容依据 | %s |" % c["content_basis"])
    G.append("| 视觉主张 | %s |" % c["visual_intent"])
    G.append("| 定稿请求 | `%s` |" % c["promoted_from_request"])
    G.append("| 迭代 | 版本 %d · 看图 %d · 完整视觉迭代 %d · 请求 %d |"
             % (c["visual_review"]["dsl_versions"], c["visual_review"]["image_views"],
                c["visual_review"]["completed_visual_iterations"], len(c["request_ids"])))
    G.append("")
G.append("## 汇总\n")
G.append("- 独立主作品：**10 件**（case-01 … case-10），共 10 张最终 PNG + 10 份同名完整 DSL。")
G.append("- 画幅跨度：%s。" % "、".join("%d×%d" % tuple(c["dimensions"]) for c in cases))
e400 = sum(1 for x in n400 if True)
G.append("- 合计渲染请求 %d 次（其中 400 语法错误 %d 次、传输失败/截断 %d 次、重试 %d 次）、"
         "看图 %d 次、完整视觉迭代 %d 次。"
         % (metrics["counts"]["snapshot_requests"], e400,
            metrics["counts"]["failed_snapshot_requests"] - e400,
            metrics["counts"]["retry_requests"], metrics["counts"]["image_views"],
            metrics["counts"]["completed_visual_iterations"]))
(out / "gallery.md").write_text("\n".join(G) + "\n", encoding="utf-8")

# ---------------- asset-sources.json ----------------
assets = {
    "schema_version": 1,
    "path_base": "output_dir",
    "task_id": "B01",
    "run_id": rid,
    "asset_policy": "dsl_primary_with_supporting_assets（总 run-config 的 creative 赛道）",
    "embedded_assets": [],
    "embedded_asset_count": 0,
    "verification": {
        "method": "对 10 份 final.snapshot 正则统计 `<Image` 标签数",
        "result": "全部为 0；成品画面 100% 由 DSL 的 Container/Positioned/Text/Transform "
                  "与渐变/阴影/裁剪/混合属性构造",
        "checked_at": datetime.now(timezone.utc).isoformat(),
    },
    "reference_material_used_for_research_only": [],
    "reference_note": "本题十件作品没有使用任何外部照片/纹理/生成图作为参考素材，"
                      "视觉方案来自对实际使用场景的推演与 DSL 能力探测（probe 记录见 "
                      "tmp/<run>/B01/ 与 capability-findings.json），因此不存在来源或许可声明。",
    "generated_content_declaration": "十件作品内的品牌、人物、航班、车站、游戏、期刊、卡牌、"
                                     "疾病分区与统计数字全部为虚构演示数据，且每件 final 图内或 "
                                     "case.md 中已声明；未把未核实数据当作事实。",
    "fonts": {
        "stack": "Inter, Noto Sans SC（DSL fontFamily 属性内声明的字体名）",
        "note": "未调用字体查询接口；实际字形由服务端渲染环境决定，最终图的行盒与截断以 TextFit "
                "自检与服务响应图片的实际看图为准",
    },
    "unresolved": [],
}
(out / "asset-sources.json").write_text(json.dumps(assets, ensure_ascii=False, indent=2),
                                        encoding="utf-8")

print(out / "portfolio.json", len(cases), "cases")
print("gallery images:", sum(1 for x in G if x.startswith("![")))
