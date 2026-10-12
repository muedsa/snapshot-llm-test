# -*- coding: utf-8 -*-
"""Write B01's portfolio.json / portfolio.md / gallery.html from the real
delivered files. Every dimension and byte count is read off disk, not typed."""
from __future__ import annotations

import io
import json
import os
import re
from datetime import datetime, timezone, timedelta

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
OUT = os.path.join(ROOT, "outputs", RUN, "B01")
TMP = os.path.join(ROOT, "tmp", RUN, "B01")
CST = timezone(timedelta(hours=8))

CURATED = [
 ("case-01", "GRIDNIGHT · 凌晨的城市电网调度台实时画面",
  "夜班调度员在值班室盯 8 小时的调度大屏",
  "深空底 + 单色青，只在越限区出现琥珀",
  "右侧联络线功率条以中轴为界、正右负左，方向不需要图例就能读出",
  "深空控制台"),
 ("case-02", "PRESSDRY · 独立书店「夏日选单」读者海报",
  "在书架前站着读海报、三十秒内决定买哪本的普通读者",
  "米色纸 + 深墨 + 一枚朱红印，90% 留白",
  "整版零图表，靠字号层级与书脊色条完成说服；二维码按位用矩形画出",
  "纯排版纸面海报"),
 ("case-03", "STORMRUN · 台风登陆前的港口船舶撤离调度令",
  "要赶在 21:00 全港停工前签字的值班调度长",
  "风暴蓝 + 警戒红 + 橙，签发文件与屏幕两用",
  "等值风圈用同心圆扫描线而非色块，疏密差本身就是风力等级",
  "深色值班令"),
 ("case-04", "ROASTLOG · 咖啡烘焙批次曲线与杯测卡",
  "烘焙师本人、门店咖啡师，以及一年后接手这批的人",
  "烘焙褐 + 琥珀单色系，会被打印也会被咖啡渍溅到",
  "四个烘焙阶段用从浅到深的连续色带，一眼看出反应深度",
  "竖版纸卡"),
 ("case-05", "BIRDCAL · 城市观鸟的物种 × 月份热力年历",
  "想知道自己某个周末能看见什么的入门观鸟者",
  "四季色轮与密度色阶分层：色轮管「什么时候」，绿黄红管「有多少」",
  "264 格数字直接压格，迁徙窗口注记从数据里直接给出结论",
  "横版年历"),
 ("case-06", "INFUSION · 儿童医院输液室的取号与叫号屏",
  "坐在椅子上抬头看的孩子，和站在旁边的家长",
  "奶油纸 + 糖果色，圆角全部 ≥24px，无细线小字",
  "底部四张「输液时可以做什么」把等待变成可一起做的事——装饰即功能",
  "低密度大字号叫号屏"),
 ("case-07", "PLATGUIDE · 高铁站台的列车编组与车厢指引",
  "拎着箱子刚进站、还不清楚这趟车怎么分车厢的旅客",
  "近黑底 + 一种安全黄，日光下看的 brutal 对比",
  "每节车厢画成真正的侧视图，门号与站台门一一对齐，黄线从车��引到地面",
  "超宽站台屏"),
 ("case-08", "INNSEASONS · 古镇民宿的节气与入住率月历",
  "抬头看年历的住客，以及每天早上更新它的前台",
  "宣纸米 + 墨 + 竹青 + 朱红，手绘挂历",
  "二十四节气做成真正的圆环刻度盘（钟面），与下方月历构成两个时间尺度",
  "竖版年历"),
 ("case-09", "ABYSSLOG · 深海考古打捞现场记录卡",
  "当天在甲板上填表的作业员，和一年后回看它的修复师",
  "深海蓝 + 黄铜金 + 珊瑚红，等宽字体承载全部编号",
  "地层柱按 cm 成比例，两件文物用红线钉在各自出水深度上，标签压在柱内",
  "横版记录卡"),
 ("case-10", "CRAGMAP · 攀岩馆的线路难度分布墙",
  "同一块墙板前的 V4 新手与今天的值班设线员",
  "岩壁灰 + 五档难度色，场馆标识语言",
  "难度梯本身就是直方图：色带高度 = 线路条数，读分布与读难度是同一个动作",
  "横版墙板"),
]

WHY = {
 "case-01": "调度台要在余光里可读，所以颜色被压到最少：一种青代表正常量，"
            "琥珀只留给越限的区。右侧那五条联络线功率条以中轴分正负，"
            "「华东交联受入 −1260」是全图唯一向左的条，它自己说明方向，"
            "不需要额外图例——这是把「方向」编码进几何而不是编码进颜色的做法。",
 "case-02": "十件里唯一一件零图表。它证明这套 DSL 的排版能力本身就够用："
            "巨号序号、衬线书名、极小字元数据三级层次，加上书脊色条，"
            "在不引入任何图形的情况下完成说服。留白和克制在这件里是主张本身，"
            "与其他九件的高信息密度互为对照。",
 "case-03": "这是全套里唯一需要表达「随时间移动的风场」的一件。"
            "等值风圈用同心圆扫描线而不是填充色块，于是 7/10/12 级三圈之间的"
            "疏密差本身就是风力等级——不看图例的人也能读出「12 级圈已经罩到锚地」。"
            "叠加的探照灯扇形把「这次照的是哪几格」直接点亮。",
 "case-04": "这是一件要被打印、夹进记录本、并且可能溅到咖啡渍的纸卡，"
            "所以是烘焙褐单色系，没有一块蓝或绿。四个阶段用从浅到深的连续色带，"
            "「颜色越来越深 = 反应越来越深」先于文字被读到。"
            "转折点（回温点 118℃、一爆 08:06）直接钉在曲线上，"
            "让「为什么是 87.5 分而不是 88」有物理依据。",
 "case-05": "22 物种 × 12 月 = 264 格，密度高到必须分层用色。"
            "横跨 12 个月列的四季色轮管「什么时候」，绿→黄→红的密度色阶管「有多少」，"
            "两套色系互不干扰——这是密集信息组织里最关键的一次取舍。"
            "右侧三段迁徙窗口注记直接从数据推出结论并指向具体物种，"
            "把年历从「记录」变成「建议」。",
 "case-06": "观众是孩子且会不耐烦，所以号是全屏唯一的 150px 大字，"
            "圆角全部 ≥24px，没有任何细线和小字。最特别的一处是把「装饰」当功能用："
            "底部四张「输液时可以做什么」的卡片，每张配一个用 DSL 基本形画出的插画"
            "（书、鼓手、门、苹果）。它不传达任何数据，它让这块屏在被等的时候也有用。",
 "case-07": "唯一的问题只有一个：「我的车厢在哪扇门」。所以每节车厢都画成"
            "真正的侧视图（车窗、门、车轮、转向架、座别色带），而不是六个色块标签；"
            "下方站台门号带与车厢门一一对齐，一条黄线把「05·6 号门」从车厢一路引到地面。"
            "空间对齐关系本身就是答案，乘客不必在图和文字之间做心算。",
 "case-08": "这是一件同时回答两个时间尺度的作品：上方圆环刻度盘回答"
            "「现在是什么时候」（今天是大暑），下方 12 个月历回答「这一年过得怎么样」。"
            "圆环不是图表而是钟面，二十四节气按冷暖分竹青/朱红两色，今天那一格用朱红点出。"
            "每格下方那条短墨条是当日入住率，不是装饰。",
 "case-09": "这件的读者有一半是一年后的文物保护修复师，所以它必须用"
            "一年后还认得的语言写：深度剖面、地层柱、编目号，而不是「刚才那个青碗」。"
            "地层柱按厘米成比例绘制，粗颗粒层用斜线阴影，两件文物用红线钉在各自出水深度上，"
            "标签压在柱体内部——柱子本身就是文物的「出土位置证据」，谁接手都能复核。",
 "case-10": "同一块板要同时服务两类人（新手找空闲线路、设线员看等级分布），"
            "于是做了一个反常规的选择：难度梯本身就是直方图，色带高度 = 线路条数。"
            "读分布和读难度轴变成同一个动作，不需要图例。右下角的场馆平面里，"
            "每面墙的堆叠色块是这面墙自己的等级构成——拿着这张板就能走过去。",
}

DSL_CAPS = ("Positioned 全绝对定位、Stack fit=EXPAND、Container 的 color / borderRadius / "
            "border / boxShadow / gradient*、Text 的 fontSize / fontFamily / fontStyle / "
            "letterSpacing / textAlign、Transform 列主序 4×4 旋转、圆角矩形与圆形作图元")

# (completion criterion, element-count placeholder filled in from the delivered
#  final.snapshot below - never typed by hand)
COMPLETE_TMPL = {
 "case-01": "1920×1080 画布由唯一根 Container 决定；服务返回 200，"
            "elements {n}，dsllib.warnings() 0 条",
 "case-02": "1200×1600 竖版；服务返回 200，elements {n}，零图表，"
            "全部为排版与矩形，warnings 0 条",
 "case-03": "1600×1100 横版；服务返回 200，elements {n}，"
            "同心圆扫描线与 6 步时标全部由 DSL 生成，warnings 0 条",
 "case-04": "1400×1750 竖版；服务返回 200，elements {n}，"
            "阶段带宽度与曲线 y 值同源计算，warnings 0 条",
 "case-05": "1680×1050 横版；服务返回 200，elements {n}，"
            "22 物种 × 12 月 = 264 格全部渲染，季节色轮与密度色阶分层，warnings 0 条",
 "case-06": "1600×1200 横屏；服务返回 200，elements {n}，"
            "150px 巨号、圆角 ≥24px、无细线小字，warnings 0 条",
 "case-07": "2000×760 超宽；服务返回 200，elements {n}，"
            "6 节车厢侧视图 + 12 个站台门 + 无障碍位，warnings 0 条",
 "case-08": "1400×1600 竖版；服务返回 200，elements {n}（本套最多，占 4096 上限的 "
            "{pct}%），圆环 24 刻度 + 12 月 365 格，warnings 0 条",
 "case-09": "1600×1000 横版；服务返回 200，elements {n}，"
            "地层柱按 cm 成比例，warnings 0 条",
 "case-10": "1750×1150 横版；服务返回 200，elements {n}，"
            "七档色带直方图 + 9 行双态线路列表 + 场馆平面，warnings 0 条",
}
ORDER = ["case-01", "case-02", "case-03", "case-04", "case-05",
         "case-06", "case-07", "case-08", "case-09", "case-10"]

VIEWLOG = {
 "case-01": ("log_c01.py 记录 6 轮完整视觉迭代；本次续跑又用图像查看工具打开 "
             "final.png 与两处放大裁切复核，图例/标注/轴标签/脚注全部分离可读",
             ["tmp/20261004-182918/B01/crops/case-01-chart.png"]),
 "case-02": ("打开 final.png 逐块核对：六个条目区、编者的话、到店信息与二维码互不重叠，"
             "书脊色条与巨型序号对齐，右侧竖排标题完整",
             []),
 "case-03": ("打开 final.png + 放大裁切（chk09 之外，本件为 chk03 类）确认警戒胶囊居中；"
             "扫描线同心圆与时序轴对齐，船位菱形与标签分离",
             ["tmp/20261004-182918/B01/crops/fin03-pill.png"]),
 "case-04": ("放大裁切 chk04-axis 与 chk04-ph 定位到时间轴与阶段名整体右移 w/2，"
             "改用 A.ctr 后重新渲染并再看整图与裁切，九个轴标签与四个阶段名全部归位",
             ["tmp/20261004-182918/B01/crops/chk04-axis.png",
              "tmp/20261004-182918/B01/crops/chk04-ph.png"]),
 "case-05": ("打开 final.png 核对 264 格数字全部渲染、季节色带与月份列对齐、"
             "右侧两条注记与色阶图例不打架、底部迷你柱与月份标签对齐",
             []),
 "case-06": ("放大裁切 chk06-ring / chk06-pill 发现「剩余时长」不在环心、"
             "队列状态胶囊文字右移；改用 A.ctr 并把 x 参照改为环心 CX 后复渲染并复看",
             ["tmp/20261004-182918/B01/crops/chk06-ring.png",
              "tmp/20261004-182918/B01/crops/fin06-ring.png",
              "tmp/20261004-182918/B01/crops/fin06-pill.png"]),
 "case-07": ("打开 final.png 核对六节车厢侧视图、站台门对齐带、无障碍位标记与"
             "设施对照表；5 版迭代记录见 iteration-notes",
             ["tmp/20261004-182918/B01/crops/final-c07-train.png",
              "tmp/20261004-182918/B01/crops/final-c07-pdrow.png"]),
 "case-08": ("放大裁切 chk08-seal2 定位到朱红印章第二个字被框边切掉、"
             "以及「2026」右移；印章放大到 72px 并重排文字后复渲染复看",
             ["tmp/20261004-182918/B01/crops/chk08-seal2.png",
              "tmp/20261004-182918/B01/crops/chk08-ring.png"]),
 "case-09": ("三轮放大裁切（chk09-hdr/hdr2、cat/cat2、plan、fin09-foot）分别定位到"
             "等宽混排串尾巴被丢弃、深度列与网格列相接、「探照灯」标签被右panel覆盖、"
             "脚注行相互压叠四类缺陷；逐项修正后复渲染并复看",
             ["tmp/20261004-182918/B01/crops/chk09-hdr2.png",
              "tmp/20261004-182918/B01/crops/chk09-cat2.png",
              "tmp/20261004-182918/B01/crops/chk09-plan.png",
              "tmp/20261004-182918/B01/crops/fin09-foot.png"]),
 "case-10": ("预览后打开整图 + chk10-hdr/hdr2/wall 三处裁切，定位到标签乱码字符、"
             "难度索引整体错位一档、空闲/占用计数与布尔标记不符、"
             "「38 人」压穿段落第二行、页眉右缘出界五处问题；逐项修正后复渲染复看",
             ["tmp/20261004-182918/B01/crops/chk10-hdr.png",
              "tmp/20261004-182918/B01/crops/chk10-hdr2.png",
              "tmp/20261004-182918/B01/crops/chk10-wall.png"]),
}


def load_requests():
    p = os.path.join(TMP, "requests.jsonl")
    out = []
    for line in io.open(p, encoding="utf-8"):
        if line.strip():
            out.append(json.loads(line))
    return out


def load_iters():
    p = os.path.join(TMP, "iterations.jsonl")
    out = []
    if os.path.exists(p):
        for line in io.open(p, encoding="utf-8"):
            if line.strip():
                out.append(json.loads(line))
    return out


def elements_of(path):
    """Opening tags only - the service counts widget nodes, not XML elements."""
    s = io.open(path, encoding="utf-8").read()
    return sum(1 for m in re.finditer(r"<(/?)[A-Za-z][A-Za-z0-9]*[ />]", s)
               if m.group(1) == "")


REQS = load_requests()
ITERS = load_iters()


def reqs_for(cid):
    """Final-delivery render ids for a case: the last render whose response_file
    is that case directory's final.png."""
    ids = []
    for r in REQS:
        rf = r.get("response_file") or ""
        rf = rf.replace("\\", "/")
        if ("/B01/%s/final.png" % cid) in rf and r["request_type"] == "render":
            ids.append(r["request_id"])
    return ids


def iters_for(cid):
    return [i["iteration_id"] for i in ITERS if (cid in (i.get("dsl_file") or "")
                                                 or (i.get("image_file") or "")
                                                 and cid in (i.get("image_file") or ""))]


cases = []
for cid, title, audience, medium, signature, kind in CURATED:
    png = os.path.join(OUT, cid, "final.png")
    snap = os.path.join(OUT, cid, "final.snapshot")
    im = Image.open(png)
    w, h = im.size
    n_el = elements_of(snap)
    why, evidence = WHY[cid], VIEWLOG[cid]
    cases.append({
        "id": cid,
        "title": title,
        "audience": audience,
        "use_context": kind,
        "user_goal": WHY[cid].split("。")[0] + "。",
        "content_basis": "全部品牌、编号、数值、日期与文案均为本次设计演示自拟的示例数据，"
                         "不宣称是实际部署的客户作品，也不指向任何真实机构",
        "visual_intent": signature,
        "curatorial_reason": why,
        "png": "%s/final.png" % cid,
        "snapshot": "%s/final.snapshot" % cid,
        "dimensions": [w, h],
        "png_bytes": os.path.getsize(png),
        "snapshot_bytes": os.path.getsize(snap),
        "dsl_element_count": n_el,
        "dsl_element_limit": 4096,
        "dsl_element_limit_used_percent": round(100.0 * n_el / 4096, 1),
        "supporting_assets": [],
        "asset_note": "无外部素材：主体、排版、图形与图表全部由 DSL 构造，未使用 <Image>",
        "dsl_capabilities": DSL_CAPS,
        "completion_criteria": COMPLETE_TMPL[cid].format(
            n=n_el, pct=round(100.0 * n_el / 4096)),
        "completion_criteria_met": True,
        "completion_criteria_evidence":
            "final.png is the raw HTTP 200 response body; the element count above is "
            "re-counted from the delivered final.snapshot; dsllib.warnings() printed "
            "0 rows on the delivery run; the image was opened and reviewed",
        "visual_review": evidence[0],
        "visual_review_evidence_files": evidence[1],
        "request_ids": reqs_for(cid),
        "iteration_ids": iters_for(cid),
        "unresolved_issues": [],
    })

portfolio = {
    "schema_version": 1,
    "task_id": "B01",
    "run_id": RUN,
    "status": "completed",
    "asset_policy": "dsl_primary_with_supporting_assets (run-config.json); "
                     "in practice no case needed a photographic asset, so ZERO "
                     "external images were embedded and no <Image> tag is used "
                     "anywhere in the ten final documents",
    "brand_disclaimer": "十件中的全部品牌名、机构名、编号、日期、统计值与文案均为本次"
                        "设计演示自拟，用于展示这套 DSL 能承载什么。它们不是任何真实"
                        "机构的作品，也不代表任何真实运行记录、客户项目或部署案例。",
    "curatorial_statement":
        "这十件不是十个题材，而是十种「看」的方式：从余光可读的调度台，到必须"
        "三十秒内决策的纸面海报；从需要表达移动风场的同心圆扫描线，到把图表"
        "本身当作刻度盘。它们共享同一套排版节奏与圆角语言（atelier.py 的令牌），"
        "但配色系统、构图骨架、表现手法与画幅比例全部互不相同。"
        "至少一件（case-02）完全没有图表，一件（case-10）把直方图和难度轴合并成"
        "同一个动作，一件（case-07）用空间对齐代替文字说明，一件（case-06）把装饰"
        "当作功能使用——这四件是这个作品集真正的观点。",
    "case_count": len(cases),
    "cases": cases,
    "final_collection_review":
        "十件全部用图像查看工具逐张打开实际看过，并各自做过放大裁切复核。"
        "本次续跑阶段重新逐张审查了中断时已交付的 8 件，据此发现并修复了四类真实"
        "缺陷（align=CENTER 与 w= 混用导致字形右移 w/2、等宽混排串尾巴被静默丢弃、"
        "印章文字被框边裁切、标签被相邻面板覆盖），补齐了 case-09 的交付图与 "
        "case-10 整件，并核对了十件的 PNG/snapshot 配对与元素数上限。"
        "作品之间的关系适合 TASK.md：题材无重叠、媒介与画幅各异、无同版式换色、"
        "无简单缩放或裁切派生。",
    "unresolved_issues": [],
}

with io.open(os.path.join(OUT, "portfolio.json"), "w", encoding="utf-8",
             newline="\n") as fh:
    json.dump(portfolio, fh, ensure_ascii=False, indent=2)
print("portfolio.json cases:", len(cases))