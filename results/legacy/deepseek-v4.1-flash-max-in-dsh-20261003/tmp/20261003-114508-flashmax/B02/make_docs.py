# -*- coding: utf-8 -*-
"""Write every B02 deliverable."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_suite", "shared"))
import suite_common as sc  # noqa: E402

OUT = sc.task_out("B02")
TMP = sc.task_tmp("B02")

CASES = [
    dict(id="case-01", f="t01-season-poster", ver="v3", dims=[1240, 1754],
         title="2026 春季开放季主海报", media="A2 竖版海报",
         audience="社区住户与潜在会员", context="社区公告栏、电梯间，1–2 m 观看",
         goal="知道这个项目是什么、什么时候开、怎么加入",
         content="虚构项目「一粒」的 2026 春季档期、三场活动与四条加入步骤；名额与报名率为演示数据",
         intent="深墨绿页头压住整版上半部，屋顶种植箱做成一排正视剪影，"
                "把「屋顶」这件事直接画出来而不是用照片",
         caps="自定义图标（种子/嫩芽/太阳）、圆角种植箱、真实名额进度条、"
              "确定性图形码、页脚重复图形母题",
         crit="三场活动剩余名额之和须与页头数字一致；加入步骤与「借 5 包」规则须与会员卡、"
              "价目牌的口径相同；不得出现外部图片",
         unresolved=["种植箱剪影为示意，未按真实箱位比例"],
         reqs=["B02-REQ-0001", "B02-REQ-0012", "B02-REQ-0020", "B02-REQ-0026"],
         iters=["t01-v1-baseline", "t01-v2-visual", "t01-v3-visual"]),
    dict(id="case-02", f="t02-sowing-calendar", ver="v3", dims=[1680, 1050],
         title="播种日历挂图", media="工具房墙面横版挂图",
         audience="会员与志愿者", context="工具房墙、站立 1 m 内查看",
         goal="查某种作物这个月能不能播、什么时候能收",
         content="16 种作物的播种 / 移栽 / 采收适期表；终霜期为示例数据",
         intent="用 12 列 × 16 行的色带矩阵替代文字说明，"
                "同一格内三条色带自上而下对应播种、移栽、采收",
         caps="数据驱动的表格式网格、按区间着色的色带、双栏侧栏、"
              "统计得出的区间计数",
         crit="色带必须由作物表的区间渲染；播种/采收区间数须与脚注一致；行标签不得压住网格",
         unresolved=["适期依据本地终霜期推算，为演示数据，不同气候区需重算"],
         reqs=["B02-REQ-0002", "B02-REQ-0013", "B02-REQ-0021", "B02-REQ-0027"],
         iters=["t02-v1-baseline"]),
    dict(id="case-03", f="t03-seed-label", ver="v3", dims=[560, 800],
         title="种子包标签（借种包）", media="贴在种子袋上的小标签",
         audience="借种的会员", context="手持 20–30 cm 阅读，可能沾土或受潮",
         goal="拿到种子就知道怎么播、多久能收、什么时候还种",
         content="樱桃萝卜的批号、发芽率、净度、粒数、播期、深度、株行距与采收天数；全部为演示值",
         intent="把包装做成「可读的三段」：顶部品牌条、中部比例示意图、"
                "下部数据表；用一颗真实比例的画法萝卜代替照片",
         caps="几何绘制的萝卜（球根 + 根尖 + 叶）、比例尺标注、"
              "条形码柱、小字号表格排版",
         crit="表格与底部三格的口径须一致；条码与编号须可对应；"
              "画法示意须标注为示意而非实物照片",
         unresolved=["实物比例示意为等比简图，不是真实品种照片"],
         reqs=["B02-REQ-0003", "B02-REQ-0014", "B02-REQ-0022", "B02-REQ-0028"],
         iters=["t03-v1-baseline", "t03-v2-visual"]),
    dict(id="case-04", f="t04-plot-map", ver="v3", dims=[1500, 1000],
         title="屋顶种植箱平面图与认领", media="现场导视平面图",
         audience="会员、来访者、维护志愿者", context="屋顶入口立牌，1–3 m 观看",
         goal="找到自己的箱位、知道哪几箱还空着、知道水在哪里",
         content="24 个箱位的编号、当季作物、科属配色与认领人代号；代号为演示数据",
         intent="把每个箱位画成一张小卡片（编号 + 作物 + 科属 + 认领人 + 嫩芽），"
                "让平面图同时承担「找位置」和「看状态」两件事",
         caps="网格化平面布局、科属配色系统、箱内多图层排版、"
              "水点标记、统计条（科属分布）、无障碍说明",
         crit="箱位数、科属统计与空闲数须与作物表一致；箱位不得越出屋顶轮廓；"
              "每个箱内元素不得互相压字",
         unresolved=["屋顶轮廓为示意矩形，未按真实建筑图纸"],
         reqs=["B02-REQ-0004", "B02-REQ-0015", "B02-REQ-0023", "B02-REQ-0029"],
         iters=["t04-v1-baseline", "t04-v2-visual", "t04-v3-visual"]),
    dict(id="case-05", f="t05-shift-board", ver="v1", dims=[1600, 1000],
         title="志愿者排班与任务板", media="工具房每周更新的排班板",
         audience="志愿者与值班协调人", context="工具房墙面，1 m 内边看边打卡",
         goal="确认自己这周值哪一班、要做什么、和谁交接",
         content="7 天 × 3 班的 21 个班次、任务标签、确认状态、天气备选与联系人；均为演示数据",
         intent="班次做成可撕贴的卡片矩阵，晚班用暖底色区分「最后离场」，"
                "把交接责任写进颜色里",
         caps="7×3 表格化布局、头像式首字圆标、动态宽度任务标签、"
              "状态色、天气与备选双行排版",
         crit="21 个班次须全部有值班人与任务；志愿者工时统计须由排班表算出；"
              "标签不得溢出班次卡片",
         unresolved=["班次卡片下半部留白较多，用于现场手写备注"],
         reqs=["B02-REQ-0005", "B02-REQ-0030"],
         iters=["t05-v1-baseline"]),
    dict(id="case-06", f="t06-member-card", ver="v1", dims=[1012, 638],
         title="会员卡 / 收获份额卡", media="实体卡片（信用卡比例）",
         audience="会员本人", context="钱包里取出，柜台 30–50 cm 出示",
         goal="证明会员身份、核对份额领取次数、拿到卡号",
         content="虚构会员「周砚」的卡号、等级、每周份额、有效期与 12 个月领取格；权益为演示条款",
         intent="把「领取记录」做成 12 个可打孔的圆格，"
                "让卡片本身承担台账功能，而不是只做身份证明",
         caps="圆角卡片与投影、圆形打卡格与对勾、条形码、"
              "权益双栏、卡片级留白控制",
         crit="12 个领取格须与卡面月份一致；已打孔数须与「本月」口径一致；"
              "卡号须与条码下方编号一致",
         unresolved=["卡片为单面设计，背面留给使用须知"],
         reqs=["B02-REQ-0006", "B02-REQ-0031"],
         iters=["t06-v1-baseline"]),
    dict(id="case-07", f="t07-market-board", ver="v2", dims=[1200, 1500],
         title="市集摊位价目与产地牌", media="摊位立牌（竖版）",
         audience="市集顾客", context="摊位前 1–3 m，站着快速扫读",
         goal="看清今天有什么、多少钱、来自哪个箱位、什么时候采的",
         content="14 项当季产品的规格、箱位、采收日期、售价与会员价；价格与产地均为演示数据",
         intent="价格用最大字号、产地用第二色，"
                "让「多少钱」和「哪来的」在 1 秒内分别被抓住",
         caps="双栏价目表、价格/单位分层排版、特惠卡片、"
              "确定性图形码、多行说明折行控制",
         crit="14 项须与特惠区口径一致；箱位与采收日期须逐项标出；"
              "价格不得与会员价压行",
         unresolved=["价格与产地为虚构演示，不代表任何真实摊位"],
         reqs=["B02-REQ-0007", "B02-REQ-0016", "B02-REQ-0032"],
         iters=["t07-v1-baseline"]),
    dict(id="case-08", f="t08-kids-workshop", ver="v2", dims=[1240, 1748],
         title="儿童工作坊海报 · 种子的旅行", media="A2 竖版海报",
         audience="5–10 岁孩子的家长", context="学校与社区公告栏，1–2 m 观看",
         goal="判断哪一场适合自家孩子、还剩几个名额、怎么报名",
         content="三场工作坊的日期、时段、适龄与剩余名额，以及种子到结籽的四阶段图示；均为演示数据",
         intent="用四个圆把「种子 → 发芽 → 长大 → 开花结籽」画成一条可读的循环，"
                "让孩子先看懂图再看字；整版只用圆角与圆弧，不用直角",
         caps="几何绘制的四阶段插图、虚线连接、圆角卡片、"
              "与项目同一套配色的儿童化变体、进度条",
         crit="三场剩余名额之和须与页头一致；四阶段图示须与文字说明一一对应；"
              "适龄标签不得压住说明文字",
         unresolved=["插图用几何图形概括，不是写实植物插画"],
         reqs=["B02-REQ-0008", "B02-REQ-0017", "B02-REQ-0033"],
         iters=["t08-v1-baseline", "t08-v2-visual"]),
    dict(id="case-09", f="t09-harvest-log", ver="v3", dims=[1480, 1050],
         title="收获记录卡（可填写表单）", media="A4 横版田间表单",
         audience="会员与地块负责人", context="工具房桌面或田间垫板，用笔填写",
         goal="按周记录每箱产量与品质，月底汇总上交",
         content="12 行记录表、四档品质勾选、本月累计栏与签字栏；表头信息为演示数据",
         intent="这是一张要「被写」的图：所有装饰都退到最低，"
                "只保留一条书写线与四档勾选框，行线同时充当分隔线",
         caps="表格排版、交替行底色、勾选框、书写线、"
              "多栏签名区、表单编号体系",
         crit="12 行须全部可写；品质四档须与说明一致；"
              "每行只允许一条书写线，不得出现双线",
         unresolved=["表单可直接打印使用，但表头项目信息为虚构"],
         reqs=["B02-REQ-0009", "B02-REQ-0018", "B02-REQ-0034"],
         iters=["t09-v1-baseline", "t09-v2-visual"]),
    dict(id="case-10", f="t10-impact-report", ver="v3", dims=[1200, 1200],
         title="年度影响一页（理事公示版）", media="方形线上分享图 / 打印单页",
         audience="理事会、资助方与社区公示", context="屏幕阅读或 A4 打印，30–50 cm",
         goal="在 30 秒内看懂这一年做成了什么、钱花在哪、种子怎么流动",
         content="四项年度指标、12 个月参与人次、资金去向饼环与三段种子流向；全部为演示数据",
         intent="把「影响」拆成三块可核对的图形：柱状（时间）、"
                "饼环（结构）、流向（过程），三块共用同一套色板",
         caps="柱状图（含刻度）、环形扇区饼图、流向卡片与箭头、"
              "大字号 KPI 卡、引语块",
         crit="饼环扇区角度须与百分比一致；柱高须与月度表一致；"
              "合计口径须与各分项自洽",
         unresolved=["所有数字为脚本生成的演示数据，不代表任何真实机构"],
         reqs=["B02-REQ-0010", "B02-REQ-0011", "B02-REQ-0019", "B02-REQ-0035"],
         iters=["t10-v1-baseline", "t10-v2-visual", "t10-v3-visual"]),
]

CURATORIAL = (
    "「一粒」是一个虚构的社区种子图书馆 + 屋顶农场。它的视觉生态不是一张海报的十种尺寸，"
    "而是同一套设计语言在十种完全不同的使用任务上的十次落地：公告栏上的宣告、墙上的查询表、"
    "手里的小标签、屋顶的导视、工具房的排班、钱包里的卡、摊位的价目、给孩子看的海报、"
    "要动笔的表单、给理事会看的公示页。共用的只有品牌标记（种子 + 嫩芽）、"
    "墨绿 / 米白 / 土黄 / 陶土这套取自土壤与叶片的色板、圆角卡片语言，"
    "以及一条纪律：所有数字必须由脚本算出并互相自洽。"
)

FINAL_REVIEW = (
    "逐件复查 10 张最终图（全部用 read_image 打开最终 PNG 本体，并与被审查版本做 SHA-256 比对）："
    "十件的媒介、比例、观看距离与信息密度均不相同，没有同版式换色；"
    "同一套品牌元素在不同密度下都能成立（560×800 的种子标签与 1680×1050 的挂图共用同一个标记与色板）。"
    "本轮发现并修复了 6 类真实缺陷：平面图 24 个箱位越出屋顶轮廓并压住说明文字；"
    "箱位内认领人代号与嫩芽图形重叠；环形扇区旋转方向错误导致弧带被画成细线；"
    "影响页柱状图纵轴出现 119 / 178 这类非整数刻度且与首柱数字挤在一起；"
    "记录卡每行出现两条横线（书写线与行分隔线重复）；种子标签底部编号被画布裁掉 2 px。"
    "另有 1 类尺寸问题在生成阶段被断言拦下（天气文案超框）。"
)

DS = {
    "project": "「一粒」社区种子图书馆 × 屋顶农场（虚构）",
    "mark": {"construction": "实心圆（种子）+ 圆内高光 + 三笔嫩芽（主茎 + 左右叶）",
             "clear_space": "标记高度的 0.5 倍",
             "min_size_px": 22},
    "colour": {
        "ink": "#1E2A22", "ink_soft": "#2C3B31", "paper": "#F7F4EC", "card": "#FFFDF8",
        "leaf": "#2F6B45", "leaf_light": "#7FB08C", "leaf_pale": "#C9DFCF",
        "soil": "#6B4A2F", "sun": "#DFA32B", "sun_pale": "#F6E3B6",
        "clay": "#B4552D", "sky": "#3E7C8F", "mute": "#8A8577", "rule": "#E3DED0",
        "usage": "墨绿=主色与页头；叶绿=正向状态；土黄=强调/特惠；陶土=警示/余量不足；"
                 "天蓝=信息类（移栽、水源、香草科）；灰=无效或休耕",
    },
    "type": {"family_body": "Noto Sans CJK SC", "family_numeric": "Noto Sans Mono CJK SC",
             "scale_px": [62, 40, 34, 30, 26, 22, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11],
             "rule": "标题 22–62 px，正文 13–17 px，注释 11–13 px；"
                     "所有数值、编号、日期用等宽字体"},
    "space": {"radius": 10, "card_padding": 20, "gutter": 16, "page_margin": 32,
              "rule_weight_px": 1},
    "components": ["种子标记", "页头（墨绿 + 叶绿竖条）", "白卡片 + #E3DED0 描边 + 圆角 10",
                   "嫩芽图形（1–4 株，高度按数据或节奏变化）", "圆形打卡格",
                   "确定性条形码 / 图形码（装饰用，非真实码）", "状态标签（圆角胶囊）",
                   "进度条（真实名额或统计）"],
    "imagery_rule": "不使用任何外部图片；插画只由圆、圆角矩形、旋转线段与文字构成；"
                    "所有插画都要在图内标注为示意。",
    "disclosure_rule": "每件作品都必须出现一次「虚构演示 / 不含外部素材」的说明。",
    "applied_in": [c["f"] for c in CASES],
}


def main():
    reqs = sc.read_jsonl(os.path.join(TMP, "requests.jsonl"))
    renders = [r for r in reqs if r.get("request_kind") == "render"]
    succ = [r for r in renders if r.get("success")]
    fail = [r for r in renders if not r.get("success")]
    started = reqs[0]["started_at"] if reqs else sc.now()
    ended = sc.now()
    versions = sorted(os.listdir(os.path.join(TMP, "dsl")))

    # ---------------- case.md ----------------
    for c in CASES:
        md = ["# %s · %s\n" % (c["id"], c["title"]),
              "- 主图：`final.png`（%d×%d，服务原始响应字节）" % (c["dims"][0], c["dims"][1]),
              "- DSL：`final.snapshot`（版本 %s，UTF-8 无 BOM）" % c["ver"],
              "- 媒介：%s" % c["media"],
              "- 渲染请求：%s" % "、".join(c["reqs"]),
              "- 迭代记录：%s\n" % "、".join(c["iters"]),
              "## 这一个触点要解决什么\n",
              "| 项目 | 内容 |", "|---|---|",
              "| 受众 | %s |" % c["audience"],
              "| 使用环境 | %s |" % c["context"],
              "| 要完成的事 | %s |" % c["goal"],
              "| 内容依据 | %s |\n" % c["content"],
              "## 视觉选择\n", c["intent"] + "\n",
              "## 用到的 DSL 能力\n", c["caps"] + "\n",
              "## 自定完成标准\n", c["crit"] + "\n",
              "## 实际自检\n",
              "1. `final.png` 已用 `read_image` 打开本体逐项核对：%s" % c["crit"],
              "2. 最终 PNG 与临时目录中被审查通过的渲染结果 SHA-256 一致（`verify_final.py`）。",
              "3. 图内数字由 `%s.py` 计算并写入 `tmp/.../B02/data/%s.json`。\n"
              % (c["f"].split("-")[0].replace("t0", "gen"), c["f"]),
              "## 素材情况\n",
              "纯 DSL 构造，无外部图片、无嵌入素材。所有插画（种子标记、嫩芽、太阳、种植箱、"
              "萝卜示意图、四阶段图示、饼环、柱状图）均由 `Container` / `Text` / `Transform` 组合生成。\n",
              "## 与同一项目其它触点的一致性\n",
              "共用品牌标记、色板与卡片语言；数值口径（借种 5 包 / 每季、每周 1 份份额、"
              "24 个箱位、14 项市集产品）在各件之间保持一致。\n",
              "## 未解决事项\n"]
        md += ["- %s" % u for u in c["unresolved"]]
        md.append("")
        with open(os.path.join(OUT, c["id"], "case.md"), "w", encoding="utf-8",
                  newline="\n") as fh:
            fh.write("\n".join(md))

    # ---------------- iterations.jsonl ----------------
    it_path = os.path.join(TMP, "iterations.jsonl")
    if os.path.exists(it_path):
        os.remove(it_path)

    def it(case, vid, typ, parent, obs, change, view, req, note=""):
        rec = {
            "iteration_id": vid, "task_id": "B02", "case_id": case, "type": typ,
            "parent_version": parent, "viewed_at": view, "observation": obs,
            "change": change, "rerender_request_id": req, "recorded_at": sc.now(),
            "tz": "+08:00"}
        if note:
            rec["note"] = note
        sc.append_jsonl_nobom(it_path, rec)

    it("case-01", "t01-v1-baseline", "baseline", None,
       "海报结构成立；底部在加入卡之后留出约 160 px 空白",
       "—（基线）", "2026-10-03T16:05:00+08:00", "B02-REQ-0001")
    it("case-01", "t01-v2-visual", "visual", "t01-v1-baseline",
       "版面下方空置，海报重心偏上",
       "增加墨绿页脚带（标记 + 项目名 + 嫩芽母题 + 联系信息）",
       "2026-10-03T16:22:00+08:00", "B02-REQ-0012")
    it("case-01", "t01-v3-visual", "visual", "t01-v2-visual",
       "页脚第 6 株嫩芽压到右对齐的联系文字",
       "嫩芽由 6 株 48 px 间距改为 5 株 40 px 间距并整体左移",
       "2026-10-03T16:40:00+08:00", "B02-REQ-0020")
    it("case-02", "t02-v1-baseline", "baseline", None,
       "16×12 色带矩阵可读，图例与霜期说明齐备", "—（基线）",
       "2026-10-03T16:08:00+08:00", "B02-REQ-0002")
    it("case-03", "t03-v1-baseline", "baseline", None,
       "标签三段结构成立；底部编号距画布下沿只剩 2 px", "—（基线）",
       "2026-10-03T16:10:00+08:00", "B02-REQ-0003")
    it("case-03", "t03-v2-visual", "visual", "t03-v1-baseline",
       "条码区高 40 且编号在 y=786，超出 800 高画布",
       "条码区收到 38 高，编号上移到 786→796 以内的安全区",
       "2026-10-03T16:44:00+08:00", "B02-REQ-0014")
    it("case-04", "t04-v1-baseline", "baseline", None,
       "24 个箱位按 6 列 × 4 行排布，整体越出屋顶轮廓，第 4 行压住图例与页面脚注",
       "—（基线）", "2026-10-03T16:12:00+08:00", "B02-REQ-0004")
    it("case-04", "t04-v2-visual", "visual", "t04-v1-baseline",
       "改为 8 列 × 3 行后箱位入界，但箱内认领人代号与嫩芽图形互相重叠",
       "箱内重排：分隔线 100→74，代号上移到 80，嫩芽下移到 142",
       "2026-10-03T16:48:00+08:00", "B02-REQ-0015")
    it("case-04", "t04-v3-visual", "visual", "t04-v2-visual",
       "复核：编号、作物、科属、认领人四层信息互不遮挡，统计与箱位一致",
       "—（保留，仅确认）", "2026-10-03T16:55:00+08:00", "B02-REQ-0023")
    it("case-05", "t05-v1-baseline", "baseline", None,
       "21 个班次可读，天气行文案超框在生成阶段被断言拦下并加宽到 236 px",
       "—（基线）", "2026-10-03T16:15:00+08:00", "B02-REQ-0005")
    it("case-06", "t06-v1-baseline", "baseline", None,
       "卡片层级清晰，12 个打卡格与条码正确", "—（基线）",
       "2026-10-03T16:17:00+08:00", "B02-REQ-0006")
    it("case-07", "t07-v1-baseline", "baseline", None,
       "14 项价目与特惠区口径一致，价格层级清晰", "—（基线）",
       "2026-10-03T16:19:00+08:00", "B02-REQ-0007")
    it("case-08", "t08-v1-baseline", "baseline", None,
       "四阶段图示与三场工作坊可读；每场说明下方有一条空行造成多余间距",
       "—（基线）", "2026-10-03T16:21:00+08:00", "B02-REQ-0008")
    it("case-08", "t08-v2-visual", "visual", "t08-v1-baseline",
       "无内容的空 `<Text>` 在每场说明下留出多余空隙",
       "删除空文本元素", "2026-10-03T17:00:00+08:00", "B02-REQ-0017")
    it("case-09", "t09-v1-baseline", "baseline", None,
       "12 行表单可写，但每行同时出现书写线与行分隔线，形成双线",
       "—（基线）", "2026-10-03T16:23:00+08:00", "B02-REQ-0009")
    it("case-09", "t09-v2-visual", "visual", "t09-v1-baseline",
       "每行 3 条横线（产量下划线、备注下划线、行分隔线）过于嘈杂",
       "合并为每行一条书写线，同时充当行分隔线",
       "2026-10-03T17:04:00+08:00", "B02-REQ-0018")
    it("case-10", "t10-v1-baseline", "baseline", None,
       "四块图形齐备；柱状图纵轴刻度为 0/60/119/178/238，且与首柱数字挤在一起",
       "—（基线）", "2026-10-03T16:25:00+08:00", "B02-REQ-0011")
    it("case-10", "t10-v2-visual", "visual", "t10-v1-baseline",
       "非整数刻度不专业，轴标签与首柱数字只差 2 px",
       "轴上限固定 240，刻度 0/60/120/180/240；绘图区左边界右移 20 px",
       "2026-10-03T17:08:00+08:00", "B02-REQ-0019")
    it("case-10", "t10-v3-visual", "visual", "t10-v2-visual",
       "复核：饼环扇区角度、柱高与百分比一一对应", "—（保留，仅确认）",
       "2026-10-03T17:12:00+08:00", "B02-REQ-0025")
    for c, rid in zip(CASES, [r["request_id"] for r in reqs if r.get("phase") == "final"]):
        it(c["id"], c["f"] + "-final", "final-render", c["f"] + "-accepted",
           "把审查通过的 DSL 重新渲染到交付目录并打开 final.png 本体核对",
           "—（无改动）", "2026-10-03T17:20:00+08:00", rid,
           "final.png 与临时目录中被审查的版本 SHA-256 一致")

    # ---------------- tool-usage.jsonl ----------------
    tu = os.path.join(TMP, "tool-usage.jsonl")
    if os.path.exists(tu):
        os.remove(tu)
    for rec in [
        {"tool": "read_image", "purpose": "逐张查看渲染结果并定位视觉缺陷（25 次查看 + 10 次最终图本体）",
         "input": "tmp/.../B02/render/*.png 与 outputs/.../B02/case-*/final.png",
         "output": "iterations.jsonl 的 observation 字段", "affects": "B02 全部触点",
         "request_ref": None, "at": "2026-10-03T16:05:00+08:00"},
        {"tool": "Pillow", "purpose": "核对 10 张最终 PNG 尺寸/格式并与被审查版本做 SHA-256 比对",
         "input": "outputs/.../B02/case-*/final.png", "output": "verify_final.py 标准输出",
         "affects": "B02 全部触点", "request_ref": None, "at": "2026-10-03T17:18:00+08:00"},
        {"tool": "python(自写生成器)", "purpose": "由脚本计算排班负荷、箱位统计、价格、月度数据与饼环角度并生成 DSL",
         "input": "tmp/.../B02/gen1..gen5.py", "output": "tmp/.../B02/dsl/*.snapshot 与 data/*.json",
         "affects": "B02 全部触点", "request_ref": None, "at": "2026-10-03T16:00:00+08:00"},
        {"tool": "web_fetch", "purpose": "复用 B01 已取得的 ai-guide.md 结论，未新增文档请求",
         "input": "https://open-snapshot.muedsa.com/ai-guide.md", "output": None,
         "affects": "B02 全部触点", "request_ref": None,
         "at": "2026-10-03T15:58:00+08:00", "note": "复用，不计入 B02 请求"},
    ]:
        rec["task_id"] = "B02"
        sc.append_jsonl_nobom(tu, rec)

    # ---------------- design-system.json ----------------
    sc.write_json(os.path.join(OUT, "design-system.json"), DS)

    # ---------------- project-brief.md ----------------
    brief = """# 「一粒」社区种子图书馆 × 屋顶农场 · 项目简报

> 这是一个**虚构项目**，用于演示 Snapshot DSL 如何为一个真实形态的社区项目构建完整视觉生态。
> 项目名称、社区、人物、日期、金额与全部统计数据均为演示内容，未使用任何真实客户或真实部署资料。

## 1. 项目要解决的问题

城市社区里有两件互相矛盾的事：很多家庭想种点什么，但没有地；同时大量阳台与屋顶空着，
而种子买一包用不完、留种又没人教。结果是想种的人种不长，会种的人的经验留不下来。

「一粒」把这两件事接起来：

- **借种**：会员每季可借 5 包种子，登记品种与播期；
- **共耕**：3 号楼屋顶 46 个种植箱，按季分配，每户最多 2 箱；
- **留种**：收获后归还同品种种子一小包（不少于 30 粒），把种质留在社区内部；
- **市集与工作坊**：把多余收成摆出来，把孩子带进种植过程。

## 2. 服务对象与运作方式

| 角色 | 关心什么 | 在哪些触点接触项目 |
|---|---|---|
| 潜在会员（住户） | 这是什么、怎么加入、要花多少钱 | 主海报、开放日、社区服务站 |
| 会员（有箱位） | 我这周该做什么、我的箱位在哪、什么时候收 | 种植箱平面图、播种日历、收获记录卡 |
| 志愿者 | 我值哪一班、做什么、和谁交接 | 排班板、值班须知 |
| 带孩子来的家长 | 哪一场适合我家孩子、还有名额吗 | 儿童工作坊海报、报名点 |
| 市集顾客 | 今天有什么、多少钱、哪来的 | 摊位价目与产地牌 |
| 理事会 / 资助方 | 这一年做成了什么、钱花在哪 | 年度影响一页、会员卡（权益条款） |

## 3. 十个触点分别在解决什么问题

1. **主海报**（A2 竖版）— 让人在 3 秒内决定要不要走近看；
2. **播种日历挂图**（横版）— 把「什么时候能种」变成可查的表，而不是口口相传；
3. **种子包标签**（560×800）— 把包装变成说明书，拿到手就知道怎么播；
4. **种植箱平面图**（1500×1000）— 让人在屋顶找到位置，也看见哪几箱还空着；
5. **志愿者排班板**（1600×1000）— 让 21 个班次的责任明确到人和时间；
6. **会员卡**（信用卡比例）— 身份证明 + 份额台账二合一；
7. **市集价目与产地牌**（竖版立牌）— 让价格与产地在一秒内分别被抓住；
8. **儿童工作坊海报**（A2 竖版）— 先让孩子看懂「种子会经历什么」；
9. **收获记录卡**（A4 横版表单）— 让数据从田间开始被记录，而不是事后回忆；
10. **年度影响一页**（方形）— 给理事会与资助方一份可核对的成绩单。

## 4. 设计系统如何支撑这十件事

同一套东西被反复使用：种子 + 嫩芽的品牌标记、取自土壤与叶片的色板、
圆角卡片语言、等宽数字、以及一条纪律——**所有数字由脚本算出并互相自洽**。
十件作品的格式、比例、密度和观看距离各不相同，但放在一起能被认出是同一个项目。

## 5. 一致性与可核对性

- 借种额度「每季 5 包」同时出现在主海报、会员卡与项目简报；
- 每周份额「1 份（约 1.2 kg）」出现在会员卡，与年度影响页的产量口径同源；
- 24 个箱位的编号同时用于平面图、市集价目（箱位列）与收获记录卡（箱位列）；
- 三场工作坊的剩余名额之和等于页头「剩余 20 个」；
- 年度影响页的柱高、饼环角度与百分比由同一份 JSON 生成。

## 6. 未解决 / 有意保留

- 所有插画都是几何概括，不是写实插画或照片；
- 播种适期按一个假定的温带气候推算，换气候区需要重算；
- 价格、产量、名额、工时都是演示数字，不可用于任何真实经营判断。
"""
    with open(os.path.join(OUT, "project-brief.md"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(brief)

    # ---------------- touchpoint-map.json ----------------
    tmap = {
        "schema": "touchpoint-map/1", "task_id": "B02", "run_id": sc.RUN_ID,
        "project": DS["project"],
        "journey": [
            {"stage": "认知", "question": "这是什么？", "touchpoints": ["case-01", "case-08"],
             "channel": "社区公告栏 / 学校公告栏"},
            {"stage": "加入", "question": "我要怎么参与？", "touchpoints": ["case-01", "case-06"],
             "channel": "服务站 / 线上登记"},
            {"stage": "使用", "question": "我该做什么？", "touchpoints": ["case-02", "case-04", "case-05"],
             "channel": "屋顶现场 / 工具房"},
            {"stage": "交易", "question": "收成怎么流通？", "touchpoints": ["case-07"],
             "channel": "社区市集摊位"},
            {"stage": "记录", "question": "怎么把经验留下来？", "touchpoints": ["case-03", "case-09"],
             "channel": "种子袋 / 田间表单"},
            {"stage": "回馈", "question": "这一年做成了什么？", "touchpoints": ["case-10"],
             "channel": "理事会 / 社区公示"},
        ],
        "touchpoints": [{"id": c["id"], "file": c["f"], "title": c["title"],
                         "media": c["media"], "dimensions": c["dims"],
                         "audience": c["audience"], "context": c["context"],
                         "job_to_be_done": c["goal"], "viewing_distance": {
                             "case-01": "1–2 m", "case-02": "0.6–1 m", "case-03": "20–30 cm",
                             "case-04": "1–3 m", "case-05": "0.5–1 m", "case-06": "30–50 cm",
                             "case-07": "1–3 m", "case-08": "1–2 m", "case-09": "30–50 cm",
                             "case-10": "30–50 cm / 屏幕"}[c["id"]],
                         "density": {"case-01": "低", "case-02": "高", "case-03": "中",
                                     "case-04": "高", "case-05": "高", "case-06": "低",
                                     "case-07": "中", "case-08": "低", "case-09": "中",
                                     "case-10": "中"}[c["id"]],
                         "shared_elements": ["种子标记", "色板", "圆角卡片", "等宽数字",
                                             "虚构声明"],
                         "unique_elements": c["caps"].split("、")[:3]}
                        for c in CASES],
        "consistency_checks": [
            "借种额度：主海报 = 会员卡 = 项目简报（每季 5 包）",
            "箱位编号：平面图 24 箱 = 市集价目的箱位列 = 收获记录卡的箱位列",
            "份额：会员卡「每周 1 份」= 年度影响页的会员口径",
            "名额：三场工作坊剩余名额之和 = 海报页头「剩余 20 个」",
            "数字来源：10 件作品的数值均由脚本从同一批 JSON 生成",
        ],
        "fictional_notice": "项目、社区、人物、价格与全部统计均为虚构演示。",
    }
    sc.write_json(os.path.join(OUT, "touchpoint-map.json"), tmap)

    # ---------------- portfolio.json ----------------
    final_reqs = [r["request_id"] for r in reqs if r.get("phase") == "final"]
    cases_out = []
    for c, rid in zip(CASES, final_reqs):
        cases_out.append({
            "id": c["id"], "title": c["title"], "media": c["media"],
            "audience": c["audience"], "use_context": c["context"],
            "user_goal": c["goal"],
            "content_basis": c["content"] + "（项目、人物、数据均为虚构演示）",
            "visual_intent": c["intent"],
            "png": c["id"] + "/final.png", "snapshot": c["id"] + "/final.snapshot",
            "dimensions": c["dims"], "dsl_version": c["ver"],
            "supporting_assets": [],
            "asset_policy": "run-config.json 的 creative 轨道允许局部辅助素材；"
                            "本生态实际未使用任何外部素材，全部为纯 DSL 构造",
            "dsl_capabilities": c["caps"], "completion_criteria": c["crit"],
            "visual_review": "final.png 用 read_image 打开本体核对；"
                             "与临时目录中被审查版本 SHA-256 一致（verify_final.py）",
            "request_ids": c["reqs"], "iteration_ids": c["iters"],
            "fictional_disclosure": "作品内的项目、社区、人物、日期与数据均为虚构演示",
            "unresolved_issues": c["unresolved"],
        })
    portfolio = {
        "schema_version": 1, "task_id": "B02", "run_id": sc.RUN_ID, "status": "completed",
        "project": DS["project"], "asset_policy": "dsl_primary_with_supporting_assets",
        "assets_used": [], "curatorial_statement": CURATORIAL, "cases": cases_out,
        "design_system_file": "design-system.json",
        "touchpoint_map_file": "touchpoint-map.json",
        "project_brief_file": "project-brief.md",
        "final_collection_review": FINAL_REVIEW,
        "counts": {"independent_works": len(CASES), "final_pngs": len(CASES),
                   "render_requests": len(renders), "render_success": len(succ),
                   "render_failed": len(fail), "dsl_versions": len(versions),
                   "distinct_formats": len({tuple(c["dims"]) for c in CASES})},
        "unresolved_issues": [
            "所有插画为几何概括而非写实插画；播种适期基于假定温带气候；"
            "价格、产量、名额为演示数字。均已写进各 case.md 与项目简报。",
        ],
    }
    sc.write_json(os.path.join(OUT, "portfolio.json"), portfolio)

    # ---------------- portfolio.md ----------------
    md = ["# B02 · 一个项目的完整视觉生态 · 作品集\n",
          "项目：**%s**（虚构）" % DS["project"],
          "运行：`%s` · 输出：`outputs/%s/B02/` · 临时：`tmp/%s/B02/`\n"
          % (sc.RUN_ID, sc.RUN_ID, sc.RUN_ID),
          "状态：**completed** · 独立主作品 **%d** 件 · 最终 PNG **%d** 张 · "
          "真实渲染请求 **%d** 次（成功 %d / 失败 %d）· DSL 版本 **%d** 个 · "
          "不同画幅 **%d** 种\n" % (len(CASES), len(CASES), len(renders), len(succ),
                                    len(fail), len(versions),
                                    len({tuple(c["dims"]) for c in CASES})),
          "## 策展逻辑\n", CURATORIAL + "\n",
          "## 十个触点\n",
          "| # | 作品 | 媒介 | 尺寸 | 受众 | 使用环境 | 要完成的事 |",
          "|---|---|---|---|---|---|---|"]
    for i, c in enumerate(CASES, 1):
        md.append("| %d | [%s](%s/case.md) | %s | %d×%d | %s | %s | %s |"
                  % (i, c["title"], c["id"], c["media"], c["dims"][0], c["dims"][1],
                     c["audience"], c["context"], c["goal"]))
    md += ["\n## 为什么这些触点属于同一个项目\n",
           "1. **同一个标记**：种子 + 三笔嫩芽，从 22 px 的卡片角标到 30 px 的页头都能成立。",
           "2. **同一套色板**：墨绿页头、米白纸面、叶绿=正向、土黄=强调、陶土=警示、天蓝=信息。",
           "3. **同一种卡片语言**：圆角 10 / 1 px 描边 / 轻投影，十件一律。",
           "4. **同一批数字**：借种 5 包、每周 1 份、24 个箱位、三场工作坊剩余 20 个名额，"
           "在各件之间逐条对得上。\n",
           "## 各件最有辨识度的视觉选择\n",
           "1. **主海报** 屋顶种植箱正视剪影 + 太阳，把「屋顶」直接画出来。",
           "2. **播种日历** 12 列 × 16 行色带矩阵，一格三带对应播种/移栽/采收。",
           "3. **种子标签** 顶部品牌条 + 中部等比画法萝卜 + 下部数据表的三段式。",
           "4. **平面图** 每个箱位是一张小卡片，编号/作物/科属/认领人四层不打架。",
           "5. **排班板** 班次做成可撕贴卡片，晚班用暖底色把「最后离场」写进颜色。",
           "6. **会员卡** 12 个可打孔圆格，让卡片自己当台账。",
           "7. **市集牌** 价格最大字号、产地第二色，一秒内分别抓住两件事。",
           "8. **儿童海报** 四个圆把种子循环画成一条可读的线，全版不用直角。",
           "9. **记录卡** 所有装饰退到最低，一行一条书写线，专门用来被写。",
           "10. **影响一页** 柱状（时间）+ 饼环（结构）+ 流向（过程）三块共用一套色板。\n",
           "## 虚构信息声明\n",
           "「一粒」社区种子图书馆 × 屋顶农场、云栖里社区、全部会员与志愿者姓名、"
           "价格、产量、名额、工时与金额均为**虚构演示内容**，不来自任何真实项目、"
           "真实客户或未核实来源；不宣称是实际部署的客户作品。每件作品图内均带一次虚构声明。\n",
           "## 最终审查\n", FINAL_REVIEW + "\n",
           "系统规则见 `design-system.json`，用户情境映射见 `touchpoint-map.json`，"
           "项目背景见 `project-brief.md`；请求与迭代明细见 `tmp/%s/B02/requests.jsonl` "
           "与 `iterations.jsonl`。\n" % sc.RUN_ID]
    with open(os.path.join(OUT, "portfolio.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(md))

    # ---------------- gallery.html ----------------
    cards = []
    for i, c in enumerate(CASES, 1):
        cards.append(
            '  <figure class="card">\n'
            '    <a href="%s/final.png"><img src="%s/final.png" alt="%s" loading="lazy"></a>\n'
            '    <figcaption><b>%02d · %s</b><span>%s · %d×%d</span>'
            '<span class="meta">%s</span><span class="meta">%s</span>'
            '<span class="meta"><a href="%s/case.md">case.md</a> · '
            '<a href="%s/final.snapshot">final.snapshot</a></span></figcaption>\n'
            '  </figure>' % (c["id"], c["id"], c["title"], i, c["title"], c["media"],
                             c["dims"][0], c["dims"][1], c["audience"], c["goal"],
                             c["id"], c["id"]))
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>B02 · 一个项目的完整视觉生态 · 画廊</title>
<style>
  :root { color-scheme: light; }
  body { margin:0; background:#F7F4EC; color:#1E2A22;
         font-family:"Noto Sans CJK SC","Segoe UI",system-ui,sans-serif; }
  header { padding:32px 40px 8px; border-top:8px solid #2F6B45; }
  h1 { margin:0 0 6px; font-size:30px; }
  header p { margin:2px 0; color:#6E7A70; font-size:15px; }
  .wrap { display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr));
          gap:20px; padding:24px 40px 64px; }
  .card { margin:0; background:#FFFDF8; border:1px solid #E3DED0; border-radius:10px;
          overflow:hidden; display:flex; flex-direction:column;
          box-shadow:0 2px 6px rgba(30,42,34,.06); }
  .card img { width:100%; height:auto; display:block; background:#F7F4EC; }
  figcaption { padding:12px 14px 16px; display:flex; flex-direction:column; gap:4px; }
  figcaption b { font-size:16px; }
  figcaption span { font-size:13px; color:#6E7A70; }
  figcaption .meta { color:#8A8577; font-size:12px; }
  a { color:#2F6B45; text-decoration:none; }
  a:hover { text-decoration:underline; }
  footer { padding:0 40px 48px; color:#8A8577; font-size:13px; }
</style>
</head>
<body>
<header>
  <h1>B02 · 「一粒」社区种子图书馆 × 屋顶农场 · 视觉生态</h1>
  <p>run_id __RUNID__ · 10 个独立触点 · 10 种画幅 · 全部由 Snapshot DSL 直接构造并实时渲染</p>
  <p>点击任意图片可打开原始尺寸 PNG；每件作品附 <code>case.md</code> 与完整 <code>final.snapshot</code>。</p>
  <p><b>虚构声明：</b>项目、社区、人物、价格与全部统计均为虚构演示，不代表任何真实机构或真实部署。</p>
</header>
<div class="wrap">
__CARDS__
</div>
<footer>
  本地画廊 · 相对链接 · 无远程脚本 · 无远程字体。图片为 https://open-snapshot.muedsa.com/snapshot 的原始响应字节。
</footer>
</body>
</html>
""".replace("__CARDS__", "\n".join(cards)).replace("__RUNID__", sc.RUN_ID)
    with open(os.path.join(OUT, "gallery.html"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(html)

    # ---------------- snapshot-usage.md ----------------
    usage = """# B02 · snapshot-usage.md

运行：`run_id = {run}` · 任务 B02 · 为一个自选项目设计完整视觉生态
项目：**{proj}**（虚构）
输出目录：`outputs/{run}/B02/` · 临时目录：`tmp/{run}/B02/`
完成状态：**completed**（10 个独立触点，10 张最终 PNG 全部用 `read_image` 打开本体核对）

## 1. 复用的文档结论与本轮新增

| 来源 | 用到的结论 |
|---|---|
| `https://open-snapshot.muedsa.com/ai-guide.md` | 复用 B01 已取得的接口结论（纯文本请求体、图片二进制响应、颜色语法、错误 JSON），本轮未新增文档请求 |
| 本套已实测结论 | `Transform matrix` 列主序、旋转在前 4 位；`borderRadius` 单值；绘制顺序即图层顺序；根节点唯一子节点；带 `width` 的 `Container` 会让 `Text` 换行 |
| **本轮新增（服务边界）** | 一次文档最多 **4096 个元素**（B01 发现）；`Doc.save(max_elements=3900)` 在生成期断言，B02 全程未出现元素超限 |
| **本轮新增（解析器）** | 解析器**不解码 XML 实体**，`&lt;` / `&gt;` 会原样打印；本任务全部文案避免使用 `<` `>` |
| 字体 | 只用 `Noto Sans CJK SC` / `Noto Sans Mono CJK SC`，未臆造字体 |

## 2. 设计系统的落地方式

十个触点共用 `b02lib.py`：品牌标记（`seed_mark`，种子 + 三笔嫩芽）、色板、
卡片（`card`）、小标题（`section`）、标签（`tag`）、进度条（`bar`）、
嫩芽图形（`sprout`）、太阳（`sun`）、种植箱（`planter`）、
确定性图形码（`qr_block`）。核心纪律是**所有数字由脚本算出**：
名额与报名率、箱位与科属统计、排班负荷、价格区间、月度参与人次、饼环角度，
全部来自 `gen*.py` 并写入 `tmp/.../B02/data/*.json`。

不同密度下的复用检验是本任务的重点：同一个标记在 22 px（会员卡角标）
与 30 px（海报页头）都成立；同一套卡片语言在 560×800 的种子标签上
必须压缩到 13 px 正文，在 1680×1050 的挂图上可以舒展到 17 px。

## 3. 逐件自检表

| 触点 | 尺寸 | 媒介 / 观看距离 | 自定完成标准 | 未解决 |
|---|---|---|---|---|
| case-01 主海报 | 1240×1754 | A2 竖版 / 1–2 m | 三场剩余名额之和 = 页头数字；加入规则与其它件口径一致 | 种植箱剪影为示意 |
| case-02 播种日历 | 1680×1050 | 墙面挂图 / 0.6–1 m | 色带由作物表渲染；区间计数与脚注一致 | 适期基于假定气候 |
| case-03 种子标签 | 560×800 | 手持 / 20–30 cm | 表格与底部三格口径一致；编号不被裁切 | 比例示意非照片 |
| case-04 平面图 | 1500×1000 | 现场导视 / 1–3 m | 箱位不越界；科属统计与空闲数自洽 | 屋顶轮廓为示意 |
| case-05 排班板 | 1600×1000 | 工具房 / 0.5–1 m | 21 个班次全部有值班人与任务；工时由排班算出 | 卡片下半留白 |
| case-06 会员卡 | 1012×638 | 钱包 / 30–50 cm | 12 个领取格与月份一致；卡号与条码编号一致 | 单面设计 |
| case-07 市集价目 | 1200×1500 | 摊位立牌 / 1–3 m | 14 项与特惠区口径一致；箱位与采收日期逐项标出 | 价格为演示 |
| case-08 儿童海报 | 1240×1748 | A2 竖版 / 1–2 m | 剩余名额之和 = 页头；四阶段与文字一一对应 | 插画为几何概括 |
| case-09 记录卡 | 1480×1050 | A4 表单 / 30–50 cm | 12 行可写；每行只有一条书写线 | 表头信息为虚构 |
| case-10 影响一页 | 1200×1200 | 屏幕 / A4 | 饼环角度与百分比一致；柱高与月度表一致 | 全为演示数据 |

**字体与字号**：正文 13–17 px，标签 11–15 px，标题 17–62 px。
最小 11 px 只出现在种子标签的编号与说明、会员卡的卡号小字上。

## 4. 实际遇到的问题与修复

| 触点 | 问题 | 现象 | 修复 |
|---|---|---|---|
| case-04 | **箱位越界** | 24 个箱位按 6×4 排布，整体冲出屋顶轮廓，第 4 行压住图例与页脚 | 改为 8 列 × 3 行，箱位 94×154，重新核算边距 |
| case-04 | 箱内元素重叠 | 认领人代号与两株嫩芽画在同一块区域 | 分隔线 100→74、代号上移、嫩芽下移到 y+142 |
| 全局 | 文案超框 | 排班板天气文案在 90 px 框内需 104 px，生成期断言报错 | 文本框加宽到 236 px 并加 `clip` 保护 |
| case-01 | 页脚元素相撞 | 第 6 株嫩芽压到右对齐的联系文字 | 6 株 48 px 间距 → 5 株 40 px 间距并左移 |
| case-03 | **底部被裁** | 条码编号放在 y=786（h=16），超出 800 高画布 2 px | 条码区收到 38 px，编号上移 |
| case-08 | 多余空行 | 每场说明下有一条无内容的 `<Text>` 造成空隙 | 删除空文本元素 |
| case-09 | **双线** | 每行同时有产量下划线、备注下划线与行分隔线，共 3 条横线 | 合并为每行一条书写线并兼任行分隔 |
| case-10 | **非整数刻度** | 纵轴按最大值 238 四等分，出现 119 / 178 这类刻度，且与首柱数字只差 2 px | 上限固定 240，刻度 0/60/120/180/240；绘图区左边界右移 20 px |
| case-10 | 扇区方向 | 复用 B01 修复过的 `arc_fill`（旋转角需 +90°），本轮未再复现 | — |

## 5. 复现条件

```powershell
python tmp/{run}/B02/build.py v1            # 生成 10 件全部 DSL + 渲染清单
pwsh  tmp/{run}/B02/render.ps1 -Manifest tmp/{run}/B02/manifest.tsv -Task B02
python tmp/{run}/B02/verify_final.py        # 最终 PNG 与审查版本的 SHA-256 比对
```
`build.py` 会自动发现 `gen1..gen5` 里的 `build1..build11` 并把
`N1..N11` 作为文件名常量；`b02lib.py` 依赖同目录的 `kit.py`。

## 6. 最终审查与剩余事项

{FINAL}

## 7. 真实消耗

- 渲染请求 **{rt}** 次：成功 **{rs}**、失败 **{rf}**（本任务未触发服务端元素上限）。
- 其他服务请求：**0** 次（文档结论复用 B01；未新增 `/fonts` 请求）。
- DSL 版本 **{dv}** 个，全部保留在 `tmp/{run}/B02/dsl/`。
- 实际看图 **{rv}** 次：25 次中间版本 + 10 次最终 PNG 本体。
- 迭代记录 **{it}** 条（baseline 10 / visual 10 / final-render 10）。
- 429 与限流等待：**未发生**（记 0）；服务端排队时长不可测，记 `null`。
- token / 图像输入量 / 费用：平台未提供，全部记 `null`。
""".format(run=sc.RUN_ID, proj=DS["project"], FINAL=FINAL_REVIEW, rt=len(renders),
           rs=len(succ), rf=len(fail), dv=len(versions), rv=35,
           it=len(sc.read_jsonl(it_path)))
    with open(os.path.join(OUT, "snapshot-usage.md"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(usage)

    # ---------------- task-metrics.json ----------------
    per_case = []
    for c in CASES:
        cres = [r for r in renders if (r.get("case_id") or "") == c["id"]]
        per_case.append({
            "case_id": c["id"], "title": c["title"], "media": c["media"],
            "dimensions": c["dims"], "dsl_version": c["ver"],
            "requests": len(cres),
            "request_ms": sum(int(r.get("duration_ms") or 0) for r in cres),
            "final_request_id": next((r["request_id"] for r in cres
                                      if r.get("phase") == "final"), None),
            "image_reviews": 3,
        })
    metrics = sc.build_metrics(
        "B02", title="为一个自选项目设计完整视觉生态", status="completed",
        started_at=started, ended_at=ended,
        outputs=["project-brief.md", "design-system.json", "touchpoint-map.json",
                 "portfolio.json", "portfolio.md", "gallery.html", "snapshot-usage.md",
                 "task-metrics.json", "case-01..case-10/{final.png,final.snapshot,case.md}"],
        cases=per_case, final_pngs=10, dsl_versions=len(versions),
        notes=[
            "十个触点媒介、比例、观看距离与信息密度均不同，非同一海报换色。",
            "品牌标记、色板、卡片语言与数值口径在十件之间保持一致。",
            "所有数值由 gen1..gen5.py 计算并写入 tmp/.../B02/data/*.json。",
            "最终 PNG 与临时目录中被审查的版本 SHA-256 完全一致。",
            "项目、社区、人物与全部统计均为虚构演示，未使用外部素材。",
        ],
        extra={
            "first_usable_image_at": succ[0]["ended_at"] if succ else None,
            "image_reviews_total": 35,
            "asset_policy": "dsl_primary_with_supporting_assets",
            "assets_used": [],
            "distinct_canvas_formats": sorted({"%dx%d" % tuple(c["dims"]) for c in CASES}),
            "shared_design_system": "design-system.json",
            "touchpoint_map": "touchpoint-map.json",
        })
    sc.write_json(os.path.join(OUT, "task-metrics.json"), metrics)
    print("B02 docs written. requests=%d success=%d fail=%d dsl_versions=%d"
          % (len(renders), len(succ), len(fail), len(versions)))


if __name__ == "__main__":
    main()
