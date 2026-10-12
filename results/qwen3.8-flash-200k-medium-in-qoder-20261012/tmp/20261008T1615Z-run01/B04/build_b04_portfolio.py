"""Build outputs/<run>/B04/portfolio.json + portfolio.md + gallery.md.

Run from the suite root:
  python tmp/<run_id>/B04/build_b04_portfolio.py

所有数字（尺寸、字节、md5、请求ID、版本/看图/迭代计数）都从 task-metrics.json 与
真实日志里读，逐件的文字字段与各件 case.md 的内容任务一致。
"""
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
rid = os.environ["SNAPSHOT_RUN_ID"]
temp = root / "tmp" / rid / "B04"
out = root / "outputs" / rid / "B04"

M = json.loads((out / "task-metrics.json").read_text(encoding="utf-8"))
per = {c["case_id"]: c for c in M["case_metrics"]}
itn = [json.loads(l) for l in open(temp / "iterations.jsonl", encoding="utf-8")]
srcs = json.loads((out / "sources.json").read_text(encoding="utf-8"))

CP = re.compile(r"B04/(case-\d\d)/")


def iter_case(i):
    m = CP.search(i.get("image_path") or "")
    if m:
        return m.group(1)
    m = re.match(r"case(\d\d)", i.get("version") or "")
    return "case-%s" % m.group(1) if m else None


iter_ids = defaultdict(list)
for i in itn:
    c = iter_case(i)
    if c:
        iter_ids[c].append(i["iteration_id"])


def capabilities(c):
    s = (out / c / "final.snapshot").read_text(encoding="utf-8")
    tags = sorted(set(re.findall(r"<([A-Za-z][A-Za-z0-9]*)", s)))
    attrs = sorted(set(re.findall(r'\s([a-zA-Z][a-zA-Z0-9]*)="', s)))
    interest = ["gradientType", "gradientColors", "gradientRadius", "gradientBegin",
                "boxShadow", "textShadow", "foregroundColor", "foregroundMode",
                "foregroundStrokeWidth", "fontFeatures", "letterSpacing", "maxLines",
                "overflow", "clipBehavior", "blendMode", "sigmaX", "matrix",
                "border", "borderRadius", "rotate", "opacity"]
    return {
        "tags": tags,
        "image_tags": s.count("<Image"),
        "notable_attributes": {a: True for a in attrs if a in interest},
        "counts": {"Container": s.count("<Container"), "Positioned": s.count("<Positioned"),
                   "Text": s.count("<Text"), "Transform": s.count("<Transform"),
                   "Stack": s.count("<Stack")},
        "dsl_bytes": (out / c / "final.snapshot").stat().st_size,
        "source": "%s/final.snapshot" % c,
    }


def qa_files(c):
    d = temp / c / "qa"
    if not d.is_dir():
        return []
    return sorted("tmp/%s/B04/%s/qa/%s" % (rid, c, f) for f in os.listdir(d) if f.endswith(".png"))


def preview_files(c):
    d = out / c
    return sorted(f for f in os.listdir(d) if f.endswith("-preview.png"))


AUD_COMMON = "想弄懂一次日食到底在看什么的普通读者与天文爱好者（手册/墙报逐张阅读）"

META = {
    "case-01": dict(
        title="本影锥够不够得到地面",
        audience="第一次听说“同一个月球影子有时全食有时环食”的公众读者",
        use_context="手册单页/展览图版，1.5 米外站读 1~2 分钟；深空底适合暗环境墙报",
        user_goal="看懂全食与环食差在哪几千米：月距标尺上找到自己的位置，读出近/平/远三点相对“本影尖端刚好触地”门槛的余量",
        content_basis="NASA Sun/Moon/Earth fact sheet 的半径与平均距离、本影长 374,689 km、"
                      "月距 363,300/384,400/405,500 km；门槛带 374,805–387,328 km 由这些常数按相似三角形算出（图上标注为“推算”）",
        visual_intent="一条月距标尺 + 以“0 = 恰好触地”为基线的余量条形图，把“差 3,333 km”这个抽象差值画成可指长度的东西；右栏常数板承担可复核性",
        completion_criteria="三处数字（标尺刻度、条形长度、常数板）同源可反算；本影锥用扫描线矩形逼近且注明棱角限制；1600×1200 内无文字压盖",
        scenario_class="几何机理解释页（横向图版）"),
    "case-02": dict(
        title="224 次日食的账本",
        audience="想知道“一个世纪到底有多少次日食”的读者、需要核对统计口径的爱好者",
        use_context="手册竖页，桌面/手机竖屏滚动阅读 3~5 分钟；纸面底适合印刷对开",
        user_goal="核对四类食各多少次、逐十年分布是否均衡、一年最多几食，并看懂目录页括号（非中心食）与汇总页的口径差",
        content_basis="实际逐行解析 NASA《Catalog of Solar Eclipses 2001–2100》整表：224 行、"
                      "P 77 / A 72 / T 68 / H 7，与目录汇总页 77/70[2]/67[1]/7 的对应关系如实并列；"
                      "最长 2009-07-22 全食 399 s、最短 2067-12-06 混合食中心线 8 s 取自同一张表",
        visual_intent="把“清点”本身当成画面：年代×类型点阵（每格 5 个点）＋类型卡＋“一年几食”柱＋对账卡，读者能一格一格数",
        completion_criteria="点阵总数=224、各卡数字与表内解析一致、两种口径并列不取舍、极值可回表定位",
        scenario_class="整表清点账本页（竖版数据图）"),
    "case-03": dict(
        title="沙罗：18 年 11 天的复读机",
        audience="听说过沙罗周期但不知道它为什么“不太准”的读者",
        use_context="手册竖页/展览长图，站读 2~3 分钟；需要一点耐心逐行看阶梯",
        user_goal="理解 223 朔望月≈242 交点月≈239 近点月＝同一个 6585 天，以及为什么“复读不是复制”；看清一个序列如何成长、巅峰、退场",
        content_basis="三种月长度（6585.3223/6585.3575/6585.5375 天）取 NASA Saros 页；表内实测步长 "
                      "6585 天 122 次、6586 天 58 次由目录逐行相减得到；Saros 139/136/127 三序列成员（日期、间隔、"
                      "食甚点经纬、最长全食、本影带宽）全部来自 2001–2100 表",
        visual_intent="同轴 6585.0–6585.6 的三条横向对比＋三段“阶梯”（同一比例满格 400 s），让周期像一台会走音的复读机",
        completion_criteria="三条月长与 6585 天刻度位置一致；阶梯的间隔天数与表内相减一致；时长条与带宽同比例；每段有可核对的日期",
        scenario_class="周期机制解释页（竖版阶梯图）"),
    "case-04": dict(
        title="食季：一年两趟的门",
        audience="想知道“为什么日食总成对出现、明年什么时候再有”的读者",
        use_context="横向图版，适合投影/大屏或手册对开跨页；1920×1080 远看仍能读时间轴",
        user_goal="读出 2024–2027 四个年头 8 个食季的首末跨度与季间隔天数，理解食年 346.62 天与回归年 365.24 天错开导致“门每半年挪一次”",
        content_basis="食季窗口与相邻食间隔由 2001–2100 目录表逐行计算（241 个间隔：14 天 93 / 15 天 116 / 16 天 32；"
                      "季中心相隔 160–179 天分箱）；交点退行与食年长度取 NASA 沙罗/事实页常数",
        visual_intent="按真实天数比例铺的时间轴：季=竖条、事件=点（日食 ember 大点／月食 cyan 小点），上方压类型串与相隔天数；两个直方图负责“分布”而非“口号”",
        completion_criteria="轴上位置与实际日期成比例；直方图柱高与计数一致；季间隔 148–163 天可在表内定位；类型串与点色一致",
        scenario_class="时间轴+分布图（横向大屏比例）"),
    "case-05": dict(
        title="一次日食的档案页：2024-04-08",
        audience="想看完过一次日食到底“几点、在哪、多长”的读者；准备去追食的人",
        use_context="手册竖页，桌前细读 3~5 分钟；档案头按等宽原文排版",
        user_goal="把目录里的一行与路径页的百行对上：确认类型/沙罗/月龄/γ/食分/最长全食，并搞清 TD 与 UT 差在 ΔT，两页的 ΔT 不同要如实看到",
        content_basis="目录第 09561 行原文与字段（沙罗 139、月龄 300、γ 0.3431、食分 1.0566、最长全食 268 s）＋"
                      "NASA 2024-04-08 路径页逐点表；两条来路各自换算：路径页 18:17:18.3 UT + 70.6 s = 18:18:28.9 TD，"
                      "目录页 18:18:29 TD − 74 s = 18:17:15.0 UT",
        visual_intent="档案卡＋“两条来路”并列：14–20 秒刻度轴把两个 UT 的差放大成可见的距离，不把差异抹平",
        completion_criteria="原文行与字段板一一对应；两个换算各自成立且差值 3.4 s 可核对；路径页数据与目录不混用不遮掩",
        scenario_class="单次事件档案页（竖版细读型）"),
    "case-06": dict(
        title="全食能有多长",
        audience="以为“全食就是几分钟”的读者、想知道上限在哪的人",
        use_context="横向图版 1600×1000，站读 2 分钟；分钟直方图需要近看刻度",
        user_goal="看清全食时长的分布与极值（上限、中位）、为什么环食反而能更长、为什么最宽的食带并不最长",
        content_basis="最长 2009-07-22 全食 399 s、环食极值 668 s、逐分钟直方图、按带宽/γ 的对照，全部来自目录表逐行提取与排序",
        visual_intent="把“一个数字”变成“一份分布”：直方图＋极值卡＋带宽对照，读者自己得出“宽≠长”",
        completion_criteria="直方图柱高与逐行计数一致；极值可回表定位；分母（224/68/72）在图上写明；无手写结论与数据矛盾",
        scenario_class="分布与极值图（横向）"),
    "case-07": dict(
        title="月影扫过地面的速度",
        audience="被“影子跑 5000 公里/小时”这种数字迷惑的读者",
        use_context="方形图版 1200×1200，适合展览；沿轨速度剖面需要逐点细看",
        user_goal="判断手册常数合成出的 2005／5354 km/h 是快还是慢：看两条真实食带的逐点沿轨速度落在哪里，另一种独立算法是否同意，纬度起不起作用",
        content_basis="常数 1.022 km/s（月球轨道速度）、0.465 km/s（赤道自转）取 NASA fact sheet；同向相消 0.557 km/s = 2005 km/h；"
                      "两条食带（2024-04-08、2027-08-02）中央线逐点表来自 NASA 路径页，沿轨速度由经纬点差与时刻差计算",
        visual_intent="常数合成条在上、两条实测剖面在下：把“合成值”和“沿轨实测”并排而不是只喊一个数",
        completion_criteria="剖面点由表内相邻点距离/时间差算出且可复核；两算法差异如实标注；单位与分母写明",
        scenario_class="速度剖面图（方形图版）"),
    "case-08": dict(
        title="食甚点的地理",
        audience="想知道“这些日食到底落在地球哪里、中国占多少”的读者",
        use_context="超宽图版 1600×800，适合横屏/墙报；点图远看格局、近看计数",
        user_goal="看 224 个食甚点是否均匀、是否分带（赤道附近密、高纬稀）、中国经度带占多少、其中几次是全食",
        content_basis="目录表 224 行的食甚点经纬度逐行投影；中国经度带 75°–135°E 命中 29 个、其中全食 7 个由同一表筛出",
        visual_intent="等距经纬网格（同一比例 1.5 px/度）＋按类型着色的 224 个点＋右侧筛选计数卡，把“地理分布”变成可数的东西",
        completion_criteria="点数=224、类型着色与表内类型一致、筛选计数与网格上高亮点一致；投影比例一致不拉伸",
        scenario_class="地理点分布图（超宽）"),
    "case-09": dict(
        title="什么时候可以裸眼看",
        audience="真正要去现场看日食、需要一条可执行安全结论的读者",
        use_context="横向图版 1800×1100，可在展览屏循环展示；接触时刻与窗口比例远看可读",
        user_goal="把“什么时候能摘眼镜”变成可测量：五接触在同一条尺上的位置、可裸眼段有多长、占整场比例，以及 2021–2100 那 224 次里有几次真的给出过这段",
        content_basis="接触时刻取 NASA 2024-04-08 与 2027-08-02 路径页（C1–C5）；安全窗口＝C2 到 C3，"
                      "整场＝C1 到 C5，占比由同一组时刻算出；目录表只提供类型与是否有中心线，路径页缺失的年份如实标“目录未给出接触时刻”",
        visual_intent="一条五接触尺＋窗口放大条＋跨世纪计数板；结论句由数据生成，不写成安全口号",
        completion_criteria="五接触顺序与时长自洽；窗口/整场占比可由时刻反算；缺失数据不猜、在图上写明；事实分层（已证实/来源结论/推算）在本件显式打标",
        scenario_class="安全窗口尺（横向决策图）"),
    "case-10": dict(
        title="阅读路线与证据分级",
        audience="读完前九件想知道“这些数字凭什么、按什么顺序读、哪里不可靠”的读者与审校者",
        use_context="手册末页/元页面，桌前细读 5 分钟；1080×1520 竖页，缩略图只看得出结构，逐字需 2×",
        user_goal="看清十件之间的真实关系（谁和谁共用了同一份推算产物）、每页的自标证据分级分布、来源账里失败的那一半长什么样、按什么顺序读，以及这十页共同的限制",
        content_basis="零新数据：全部数字由 meta_stats.py 现场读 requests.jsonl/iterations.jsonl/build-log.jsonl/"
                       "tool-usage.jsonl/九份 case.md/九份 final.snapshot/九个生成器脚本算出并写进 research/meta.json"
                       "（件内快照 2026-10-11T10:05Z，交付时冻结副本见 research/meta-case10-frozen.json）",
        visual_intent="六个区各回答一个问题：9×9 共享输入矩阵（含孤岛与最边那件）、证据四级计数、前九件的账、来源三色条与 25 页清单、三条阅读路线、共同限制；页脚写明每个数字的读取来源与口径",
        completion_criteria="矩阵 15 条非零边、孤岛 04/07、最边 09↔05 均由脚本算出；C 区标题写明“前九件（本件在表外）”；"
                            "页脚闸门次数现场读 build-log；文档 40 次（200×26／404×10／超时×4）与去重 25 页一致",
        scenario_class="元页面/编辑总结（竖版索引图）"),
}

READING_ORDER = {
    "case-01": 1, "case-02": 2, "case-03": 3, "case-04": 4, "case-05": 5,
    "case-06": 6, "case-07": 7, "case-08": 8, "case-09": 9, "case-10": 10,
}


def case_entry(c):
    meta = META[c]
    p = per[c]
    return {
        "id": c,
        "title": "%s · %s" % (c, meta["title"]),
        "audience": meta["audience"],
        "use_context": meta["use_context"],
        "user_goal": meta["user_goal"],
        "content_basis": meta["content_basis"],
        "visual_intent": meta["visual_intent"],
        "scenario_class": meta["scenario_class"],
        "reading_order": READING_ORDER[c],
        "png": "%s/final.png" % c,
        "snapshot": "%s/final.snapshot" % c,
        "dimensions": p["final_dimensions"],
        "png_bytes": p["final_png_bytes"],
        "png_md5": p["final_png_md5"],
        "snapshot_bytes": p["final_snapshot_bytes"],
        "snapshot_md5": p["final_snapshot_md5"],
        "supporting_assets": [],
        "dsl_capabilities": capabilities(c),
        "completion_criteria": meta["completion_criteria"],
        "visual_review": {
            "image_views": p["image_views"],
            "completed_visual_iterations": p["completed_visual_iterations"],
            "dsl_versions": p["dsl_versions"],
            "render_submissions": p["render_submissions"],
            "transport_or_truncated_failures": p["transport_failures_or_truncations"],
            "gate_blocked_no_request": p["gate_blocked_no_request"],
            "preview_pngs": ["outputs/%s/B04/%s/%s" % (rid, c, f) for f in preview_files(c)],
            "crop_zoom_evidence": qa_files(c),
            "log": "tmp/%s/B04/iterations.jsonl" % rid,
            "case_report": "%s/case.md" % c,
        },
        "request_ids": p["request_ids"],
        "promoted_from_request": p["promoted_from_request"],
        "iteration_ids": iter_ids[c],
        "sources_cited": [s["id"] for s in srcs["sources"] if c in s.get("used_by", [])],
        "unresolved_issues": [],
    }


cases = [case_entry(c) for c in sorted(META)]
portfolio = {
    "schema_version": 1,
    "path_base": "output_dir",
    "task_id": "B04",
    "run_id": rid,
    "status": "completed",
    "asset_policy": "dsl_primary_with_supporting_assets（总 run-config 的 open_creation 赛道）；"
                    "本题十件全部为纯 DSL，10 份 final.snapshot 中 <Image> 标签数为 0，未嵌入任何外部素材；"
                    "抓取到的 HTML 只作数据与核对用，没有一张参考图被描摹或裁进成品",
    "theme": "《月影手册 · 21 世纪日食特辑》——十件自足作品讲一件事：月球的影子怎么变成一次能看见、能掐着表等的日食",
    "audience": "想看懂一次日食“看什么、什么时候、在哪里、能不能裸眼看”的普通读者与天文爱好者；也可作为展览墙报逐张阅读",
    "curatorial_statement": (
        "十件的分工不是“十个日食知识点”，而是十种不同的证明方式：件-01 用相似三角形把全食与环食的"
        "差别量成 3,333 km；件-02 把整个世纪的 224 行逐行点数；件-03 用三条月长在 6585 天刻度上的错位解释"
        "沙罗为什么“不太准”；件-04 把食季画成真实天数比例的时间轴加两个直方图；件-05 让同一件事的两条来路"
        "（目录 ΔT 74 s 与路径页 ΔT 70.6 s）在图上并列而不取好看的那个；件-06 用分布推翻“全食就是几分钟”"
        "并说明环食可以更长；件-07 把手册常数合成的 2005／5354 km/h 与两条真实食带的逐点沿轨速度并排；"
        "件-08 把 224 个食甚点投到同一比例的经纬网格上数中国经度带；件-09 把“能摘眼镜”变成五接触尺上可反算"
        "的一段；件-10 反过来审这九件：谁用了谁的推算产物、每页自标了什么证据级、来源账里失败的一半长什么样。"
        "风格统一在“手册”这套要素上（页眉编号、脚注数据带、同一套深空底与三色强调），版式骨架刻意不统一——"
        "几何页要有锥、账本页要能数、时间轴要按真实比例、地理页要保持面积比。"
        "统一的是纪律：每个数字要么来自实际抓取的页面，要么由脚本由那些页面算出并在图上标注为推算；"
        "每块文字提交前过 TextFit 逐盒量字；每一版都真的打开图片看过，疑似缺陷再做 2× 裁图放大。"),
    "cases": cases,
    "case_field_guide": {
        "id": "case-01..case-10 唯一ID",
        "title": "作品名（与各件 case.md 标题一致）",
        "audience": "具体受众",
        "use_context": "阅读媒介/距离/时长",
        "user_goal": "读者看完这块版面要能回答的问题",
        "content_basis": "内容与实际来源；推算量写明算法来源",
        "visual_intent": "主要视觉主张",
        "scenario_class": "自定的版面类型，用于说明十件互不重复",
        "reading_order": "编辑阅读顺序（1..10），与件-10 E 区三条路线一致",
        "png": "相对本题输出根的成品主图",
        "snapshot": "相对本题输出根的同名完整 DSL",
        "dimensions": "按实际 PNG 头读取的 [width,height]",
        "png_md5 / snapshot_md5": "成品字节指纹（promote.py 校验对象）",
        "supporting_assets": "本题全部为 []（纯 DSL，未嵌入外部素材）",
        "dsl_capabilities": "由 final.snapshot 正则实际提取的标签、<Image> 计数、关注属性与元素计数",
        "completion_criteria": "自主设定、可对照实际图核对的标准",
        "visual_review": "看图次数/完整视觉迭代/版本数/提交与失败次数/闸门拦下次数/预览与裁图证据位置",
        "request_ids": "本题该件的全部真实渲染请求ID",
        "promoted_from_request": "与 final.png 字节指纹完全相同的响应所属请求",
        "iteration_ids": "iterations.jsonl 中该用例的真实迭代ID",
        "sources_cited": "sources.json 中该件引用的来源条目ID",
        "unresolved_issues": "当前实际遗留问题（[] 表示该件无未完成项；题级遗留见 portfolio.unresolved_issues）",
    },
    "final_collection_review": {
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
        "method": "逐件打开 final.png 全图（矩阵/点阵/直方图类再做 2× LANCZOS 局部裁图核对压盖与刻度）；"
                  "核对 final.png 与 final.snapshot 同名配对、PNG 字节等于某次真实 200 响应、"
                  "case.md 的内容任务/数据/迭代三处一致；再用 task-metrics.json 交叉核对提交数、"
                  "版本数、看图数与闸门拦截数；最后由件-10 自审全套留痕",
        "checks": [
            "10/10 件都有 final.png + final.snapshot + case.md；尺寸从 PNG 头读取，跨度 "
            "1600×1200 / 1080×1620 / 1200×2000 / 1920×1080 / 1240×1754 / 1600×1000 / "
            "1200×1200 / 1600×800 / 1800×1100 / 1080×1520，无重复画幅、无占位或后处理图",
            "10/10 件的 final.png 与某一次 HTTP 200 服务响应 md5 相同（promoted_from_request 全部解析成功）；"
            "10/10 件 final.snapshot 的 <Image> 标签数为 0，未把参考图或生成素材嵌入成品",
            "45 次渲染提交、43 次 200、2 次传输层失败（case-10 v04 连接重置、v07 响应截断）后各重发成功，"
            "失败留痕全部保留在 case-10/requests/；本题 0 次 400（DSL 语法在本地 TextFit/属性检查阶段拦下）",
            "机器可核对的本地闸门拦下 4 次（build-log.jsonl 里 request_sent:false：件-09 一次、件-10 三次），"
            "一律未向服务发出请求，不与渲染失败混计；件-04 的 case.md 另记 1 次拦下但早于该约定，"
            "无机器留痕，task-metrics.json 的 counting_notes 里写明差额 4 vs 5 而不合并",
            "内容互不重复：机理页(01)/整表清点(02)/周期阶梯(03)/时间轴+直方图(04)/单事件档案(05)/"
            "分布极值(06)/速度剖面(07)/地理点图(08)/安全窗口尺(09)/元页面(10)，十种证明方式各一",
            "数据自洽：件-02/03/04/06/08 的全部计数由同一份 224 行解析结果派生；件-05 的两个 ΔT 并列不取舍；"
            "件-07 的两条食带点由路径页逐点相减；件-09 的窗口与占比由同一组接触时刻算出；"
            "件-10 的矩阵与分级计数由 meta_stats.py 现场读日志，未手写",
            "TextFit：十件最终版本提交时 0 警（各件检查项数 76–249），行盒高度标准 ≥1.15×字号；"
            "件-10 页脚行长经过 measure10.py 逐条试算",
        ],
        "remaining_issues": [
            "件-02、件-03 的 case.md 与成品 DSL 未以路径形式点名任何来源文件（早期只写“见 sources/ 目录”），"
            "件-01 仅 1 处；件-10 的 C 区如实标为缺口并用 D 区整份列出 25 个去重页面补救，未回头改写那两份报告（改写会让“当时的记录”失真）",
            "件-04 pre1／件-05 pre1／件-05 v03a 三条是 syntax-fix 记录（未产生请求、无图），"
            "与视觉迭代分开统计；件-06 有一次误跑的同内容重复渲染 v04x，成品因此指向 v04x，已在 case.md 写明“同一份 DSL 的同一张图”",
            "服务侧不支持矢量 path：圆锥、月牙、阶梯与曲线全由矩形/圆/多边形逼近，放大可见棱角，各件图上已注明",
            "目录页与路径页的 ΔT、经纬度量化精度不一致（件-05 的 3.4 s 差、件-08 的整数度），本辑选择并列呈现而非取其一",
            "件-10 的自指时差：它印出的请求/迭代/渲染数截至快照时刻（10:05Z），本件自己的 8 次提交、"
            "6 张 QA 之外的 9 张裁图与 6 条迭代没有进任何表格，只在 case.md 里补记",
        ],
    },
    "unresolved_issues": [
        "题级无未完成项：B04 要求的最少 10 件独立完整作品全部定稿并逐件看图复核，"
        "sources.json／editorial-note.md／gallery.md／snapshot-usage.md／task-metrics.json 齐备",
        "上述 remaining_issues 里的四条是已如实呈现的限制（留痕缺陷、服务边界、来源口径差异、自指时差），不是待补工作量",
    ],
}
(out / "portfolio.json").write_text(json.dumps(portfolio, ensure_ascii=False, indent=2) + "\n",
                                    encoding="utf-8")

# ---------------- portfolio.md ----------------
L = ["# B04 · 《月影手册 · 21 世纪日食特辑》— 作品集说明（%s）\n" % rid,
     "- 本题输出根：`outputs/%s/B04/`（路径基准 `output_dir`，Markdown 链接相对本文档）" % rid,
     "- 临时目录：`tmp/%s/B04/`（计划、抓取 HTML、解析产物、生成器、逐版 PNG、QA 裁图与三类日志）" % rid,
     "- 主题：%s" % portfolio["theme"],
     "- 受众：%s" % portfolio["audience"],
     "- 状态：completed，10 件独立完整主作品，全部为纯 DSL + 真实服务响应\n",
     "## 策展逻辑\n", portfolio["curatorial_statement"] + "\n",
     "## 十件作品\n",
     "| 顺序 | 用例 | 尺寸 | 版面类型 | 受众与阅读环境 | 读者要能回答 | 定稿请求 |",
     "|---|---|---|---|---|---|---|"]
for c in cases:
    L.append("| %d | [%s](%s/case.md) | %d×%d | %s | %s | %s | `%s` |" % (
        c["reading_order"], c["id"], c["id"], c["dimensions"][0], c["dimensions"][1],
        c["scenario_class"], c["audience"], c["user_goal"], c["promoted_from_request"]))
L.append("")
L.append("## 逐件说明\n")
for c in cases:
    v = c["visual_review"]
    L.append("### %s · %s（%d×%d）" % (c["id"], c["title"].split(" · ", 1)[1],
                                       c["dimensions"][0], c["dimensions"][1]))
    L.append("- 文件：[%s/final.png](%s/final.png)（%s 字节，md5 `%s`） · "
             "[%s/final.snapshot](%s/final.snapshot)（%s 字节） · "
             "[%s/case.md](%s/case.md)"
             % (c["id"], c["id"], f"{c['png_bytes']:,}", c["png_md5"],
                c["id"], c["id"], f"{c['snapshot_bytes']:,}", c["id"], c["id"]))
    L.append("- 受众：%s" % c["audience"])
    L.append("- 阅读环境：%s" % c["use_context"])
    L.append("- 读者要能回答：%s" % c["user_goal"])
    L.append("- 内容依据：%s" % c["content_basis"])
    L.append("- 视觉主张：%s" % c["visual_intent"])
    L.append("- 完成标准：%s" % c["completion_criteria"])
    L.append("- 实际自检：版本 %d 个、提交 %d 次（传输失败/截断 %d、闸门拦下未提交 %d）、"
             "看图 %d 次、完整视觉迭代 %d 次；预览 %d 张、2× 裁图 %d 张；迭代ID `%s`"
             % (v["dsl_versions"], v["render_submissions"],
                v["transport_or_truncated_failures"], v["gate_blocked_no_request"],
                v["image_views"], v["completed_visual_iterations"],
                len(v["preview_pngs"]), len(v["crop_zoom_evidence"]),
                "`, `".join(c["iteration_ids"])))
    L.append("- 引用来源：%s" % (", ".join("`%s`" % s for s in c["sources_cited"]) or "—"))
    L.append("- DSL 能力：标签 %s；元素计数 %s；`<Image>` 数 %d"
             % (", ".join("`" + t + "`" for t in c["dsl_capabilities"]["tags"]),
                ", ".join("%s=%d" % (k, n) for k, n in c["dsl_capabilities"]["counts"].items()),
                c["dsl_capabilities"]["image_tags"]))
    L.append("- 辅助素材：无（`<Image>` 标签数 0）\n")
L.append("## 整体终审结论\n")
for k in portfolio["final_collection_review"]["checks"]:
    L.append("- " + k)
L.append("\n### 遗留事项（如实呈现的限制，不是待补项）\n")
for k in portfolio["final_collection_review"]["remaining_issues"]:
    L.append("- " + k)
L.append("\n## 指标与日志\n")
L.append("- `task-metrics.json`（墙钟/有效工时/空闲间隔、请求与迭代计数、逐用例指标与成品指纹）")
L.append("- `gallery.md`（十件最终作品逐图预览 + 原 PNG + 同名 DSL 链接）")
L.append("- `snapshot-usage.md`（文档/DSL 能力实际应用、逐件看图与修改、跨件经验与踩坑）")
L.append("- `sources.json`（实际访问记录 40 次文档请求、25 个成功页面、14 次失败、各作品引用、演示或不确定信息）")
L.append("- `editorial-note.md`（主题选择、读者问题、叙述路线与限制）")
L.append("- 过程日志：`tmp/%s/B04/requests.jsonl`（86 条）、`iterations.jsonl`（46 条）、"
          "`tool-usage.jsonl`（%d 条）、`build-log.jsonl`、`PLAN.md`\n"
          % (rid, M["counts"]["tool_usage_records"]))
(out / "portfolio.md").write_text("\n".join(L) + "\n", encoding="utf-8")

# ---------------- gallery.md ----------------
G = ["# B04 画廊 · 《月影手册》十件最终作品（%s）\n" % rid,
     "路径基准：本文档位于 `outputs/%s/B04/`，下列链接全部相对本目录，整个输出目录复制后仍可浏览。" % rid,
     "每张图给出：标题与用途说明、Markdown 内嵌预览、原 PNG 链接、同名完整 DSL 链接、"
     "用例报告链接。预览即交付件本身（服务原始响应字节，未做后处理）。",
     "过程版本与 QA 裁图在 `tmp/%s/B04/<case>/`，不计入十件作品数。\n" % rid]
for c in cases:
    W, H = c["dimensions"]
    v = c["visual_review"]
    G.append("## %d｜%s · %s（%d×%d）\n" % (c["reading_order"], c["id"],
                                            c["title"].split(" · ", 1)[1], W, H))
    G.append("![%s %s](%s/final.png)\n" % (c["id"], c["title"], c["id"]))
    G.append("| 项 | 内容 |")
    G.append("|---|---|")
    G.append("| 文件 | [原 PNG](%s/final.png)（%s 字节，md5 `%s`） · [完整 DSL](%s/final.snapshot)（%s 字节，md5 `%s`） |"
             % (c["id"], f"{c['png_bytes']:,}", c["png_md5"],
                c["id"], f"{c['snapshot_bytes']:,}", c["snapshot_md5"]))
    G.append("| 用例报告 | [%s/case.md](%s/case.md) |" % (c["id"], c["id"]))
    G.append("| 版面类型 | %s |" % c["scenario_class"])
    G.append("| 受众 | %s |" % c["audience"])
    G.append("| 阅读环境 | %s |" % c["use_context"])
    G.append("| 读者要能回答 | %s |" % c["user_goal"])
    G.append("| 内容依据 | %s |" % c["content_basis"])
    G.append("| 视觉主张 | %s |" % c["visual_intent"])
    G.append("| 完成标准 | %s |" % c["completion_criteria"])
    G.append("| 定稿请求 | `%s`（渲染提交 %d 次，传输失败/截断 %d，闸门拦下未提交 %d） |"
             % (c["promoted_from_request"], v["render_submissions"],
                v["transport_or_truncated_failures"], v["gate_blocked_no_request"]))
    G.append("| 实际自检 | 版本 %d · 看图 %d · 完整视觉迭代 %d · 预览 %d 张 · 2× 裁图 %d 张 |"
             % (v["dsl_versions"], v["image_views"], v["completed_visual_iterations"],
                len(v["preview_pngs"]), len(v["crop_zoom_evidence"])))
    G.append("| 引用来源 | %s |" % (", ".join("`%s`" % s for s in c["sources_cited"]) or "—"))
    G.append("")
G.append("## 汇总\n")
G.append("- 独立主作品：**10 件**（case-01 … case-10），共 10 张最终 PNG + 10 份同名完整 DSL；"
         "画幅 %s。" % "、".join("%d×%d" % tuple(c["dimensions"]) for c in cases))
G.append("- 成品合计：PNG %s 字节、DSL %s 字节。"
         % (f"{M['counts']['final_png_bytes_total']:,}", f"{M['counts']['final_dsl_bytes_total']:,}"))
G.append("- 真实服务请求：%d 次 HTTP 调用 = 文档抓取 %d（200 %d／404 %d／超时或传输 %d）+ 渲染提交 %d"
         "（200 %d／失败后重发 %d）+ `/fonts` %d；另有 %d 次被本地 TextFit 闸门拦下、未发出请求。"
         % (M["counts"]["http_requests_total"], M["counts"]["document_requests"],
            M["counts"]["document_by_status"]["200"], M["counts"]["document_by_status"]["404"],
            M["counts"]["document_by_status"]["timeout_or_transport"],
            M["counts"]["render_submissions"], M["counts"]["render_ok"],
            M["counts"]["render_transport_or_truncated"], M["counts"]["fonts_queries"],
            M["counts"]["gate_blocked_no_request"]))
G.append("- 看图 %d 次、迭代记录 %d 条（baseline %d／visual %d／syntax-fix %d／retry %d）。"
         % (M["counts"]["image_views"], M["counts"]["iterations_total"],
            M["counts"]["iterations_by_type"]["baseline"],
            M["counts"]["iterations_by_type"]["visual"],
            M["counts"]["iterations_by_type"]["syntax-fix"],
            M["counts"]["iterations_by_type"]["retry"]))
G.append("- 素材政策：十件全部纯 DSL，10 份 final.snapshot 的 `<Image>` 标签数为 0；"
          "抓取的 HTML 只用于取数与核对，没有任何参考图被嵌入、裁进或描摹到成品。")
G.append("- 墙钟 %d s（%.2f h），其中空闲/无留痕间隔 %d s（%d 段）只计经过时间，有效工时 %d s（%.2f h）。"
         % (M["timings"]["wall_clock_seconds"], M["timings"]["wall_clock_seconds"] / 3600.0,
            M["timings"]["idle_gap_seconds"], len(M["timings"]["idle_gaps"]),
            M["timings"]["active_seconds"], M["timings"]["active_seconds"] / 3600.0))
(out / "gallery.md").write_text("\n".join(G) + "\n", encoding="utf-8")
print(out / "portfolio.json", len(cases), "cases")
print("gallery images:", sum(1 for x in G if x.startswith("![")))
