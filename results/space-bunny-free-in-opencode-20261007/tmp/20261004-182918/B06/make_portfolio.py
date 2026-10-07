# -*- coding: utf-8 -*-
"""Write the B06 deliverables that are generated from real state:

  outputs/20261004-182918/B06/problem-evidence.json   (from data.py, single source of truth)
  outputs/20261004-182918/B06/portfolio.json
  outputs/20261004-182918/B06/gallery.html
"""
from __future__ import annotations

import html
import io
import json
import os
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run as R            # noqa: E402
import data                # noqa: E402

CST = timezone(timedelta(hours=8))
OUT = R.OUT
NOW = datetime.now(CST).isoformat(timespec="seconds")

# ---------------------------------------------------------------- case metadata
# filled from the delivered PNGs (real PIL sizes) and the real request log
from PIL import Image  # noqa: E402

META = {
    "case-01": dict(
        title="把货架上的标价，换成一把尺子",
        medium="1600 × 1380 横向宽幅对照卡（贴在购物车把手 / 手机横屏）",
        visual_intent="把「每 100 克多少钱」做成可横向对齐的条长，让同品牌不同规格、"
                      "同价不同净重这两类最贵的情况在同一把尺子上直接比出高低。",
        dsl_caps="Stack + Positioned 全绝对定位；程序化条长（按真实单位价格归一）；"
                 "渐变；圆角；boxShadow；容器嵌套图案；CJK+Inter 混排",
        criteria=["四组真实单位价格全部按调查原值换算，条长比例与数字一致",
                  "同组两行的条长差能一眼看出方向（谁更贵）",
                  "多买优惠那一格必须显示「折算后单件价」而不是只显示宣传折扣",
                  "每件商品的品牌/口味/净重来自调查原文，未编造新品"],
        unresolved=[]),
    "case-02": dict(
        title="你的月供是一个数，其实是两笔钱的和",
        medium="1800 × 1300 横向房贷月供解剖图",
        visual_intent="把 360 期月供画成一根根柱子，柱高永远一样而颜色在变，"
                      "让「本金/利息」这个隐藏的内部结构变成可见的斜率。",
        dsl_caps="360 根程序化堆叠柱；折线；阶梯面积；阴影；分隔线；等宽数字",
        criteria=["每期月供完全相等（等额本息），柱高不得有视觉偏差",
                  "本金占比单调上升，『本金过半』的月份可被读出",
                  "剩余利息三个时点的数字与同一公式一致",
                  "演示参数（250 万/30 年/3.85%）在页面上明写为自拟"],
        unresolved=[]),
    "case-03": dict(
        title="多花 1,000 元买一级，10 年电费省回 2,166 元",
        medium="1500 × 1290 竖幅选购决策卡",
        visual_intent="把「能效等级 → 每度电 → 每年电费 → 10 年总电费 → 回本年限」"
                      "这条链一次算完，并用一条深浅双色条把价差与电费差放在同一把尺子上。",
        dsl_caps="三卡并列；程序化堆叠条；能源标识示意卡；胶囊排序条；阴影",
        criteria=["三台机型的年耗电量与 10 年电费由脚本按 APF 与 1136/433 小时算出",
                  "两种排序（按标价 / 按 10 年总成本）结论相反，这一点必须成立",
                  "等级门槛与折算小时数标注为 GB 21455-2019 与标识实施规则的公开值",
                  "机型、价格、APF 明写为自拟演示"],
        unresolved=[]),
    "case-04": dict(
        title="一个 ↑ 箭头，撑不起三个决定",
        medium="1240 × 1754 竖版 A4（贴冰箱 / 床头）",
        visual_intent="把「参考范围 / 医学决定水平 / 危急值」三条线画在同一根数轴上，"
                      "让一个 47 或 7.4 落在哪一段、意味着什么动作变成可以指认的事。",
        dsl_caps="分段数轴；参考带；标记点与引线；卡片网格；表格；阴影",
        criteria=["四个指标各画一条轴，三条线的位置与真实阈值一致",
                  "本人实测值与参考范围、医学决定水平的相对位置一眼可判",
                  "每个指标下方给出可执行动作而不是术语",
                  "受检者数值为自拟并声明，阈值与参考范围为真实公开值"],
        unresolved=[]),
    "case-05": dict(
        title="前 100 个 AQI 只值 60 µg/m³，后 100 个值 150",
        medium="1600 × 1000 横向双尺对照页",
        visual_intent="把 AQI 数字轴和同一天的 PM2.5 浓度轴钉在同一块板上，"
                      "让『每 100 个 AQI 要涨多少浓度』的非线性变成一排不等宽的块。",
        dsl_caps="双轴对齐；不等宽分段条（真实断点）；表格六档；程序化 7 天行",
        criteria=["AQI 断点全部按 HJ 633—2026 表 3 的 0/30/60/115/150/250/350/500 绘制",
                  "7 天示例的 AQI 由脚本按式(1)内插并向上进位，与手算一致",
                  "旧版 35/75 的口径在图上明确标注为已废止",
                  "七档颜色与 RGB 取自标准附录 A"],
        unresolved=[]),
    "case-06": dict(
        title="同一个 600 度，冬天多付 53 元",
        medium="1000 × 1414 竖版挂卡（贴电表箱旁）",
        visual_intent="一年 12 根柱，柱高是当月总用电量、柱内三段是三档电量，"
                      "再把夏冬两套标准画成两条横贯全图的虚线。",
        dsl_caps="12 根程序化堆叠柱；分段虚线（用短矩形拼接）；季节色带；暗色算例卡",
        criteria=["三档电量按粤价〔2012〕135号拆分，三档电价用广州公布的执行价",
                  "600 度的夏季/非夏季算例必须算出 370.4 / 423.4 / 差 53 元",
                  "一档上限的两条虚线位置由同一公式算出，12 根柱全部对齐",
                  "12 个月用电量为自拟演示并声明"],
        unresolved=[]),
    "case-07": dict(
        title="差 5 元跨过门槛，能省 25 元；多买反而更贵",
        medium="1720 × 1080 横向决策页（下单前停在结算按钮之前）",
        visual_intent="把折扣率随购物车金额画成一条锯齿，每一堵墙都标上编号与真实规则，"
                      "并用绿色圈标出每个门槛那一格的最优凑单点。",
        dsl_caps="330 段折线（锯齿）；分段色带；编号墙；购物车四场景对比卡",
        criteria=["锯齿的每个拐点与规则表逐条对应（199/299/399/每满300/600 叠加）",
                  "四个购物车场景的到手价由同一 pay() 算出，差额与页上文字一致",
                  "『最优凑单点』落在门槛那一格本身，且圈与文字不压墙",
                  "真实投诉数字按海报新闻原文，规则表声明为自拟"],
        unresolved=[]),
    "case-08": dict(
        title="涨 3,000 元，到手 2,400 元",
        medium="1240 × 1754 竖版 A4（夹在工资条里随身带）",
        visual_intent="上半把一张工资条拆成可核对的三段，下半把「每涨 1 元到手多少」"
                      "画成一条只在税率档边界上折下去的红色阶梯。",
        dsl_caps="按比例堆叠条；程序化净收入曲线（真实税率函数）；阶梯线；面积填充；表格",
        criteria=["应发→五险一金→个税→到手的每一项金额都能在页面上互相对上",
                  "标题的 +2,400 与脚本算出的边际 80% 完全一致（不写死文案）",
                  "红阶的三处折点（22,000 / 35,000 / 45,000）由税率表算出并逐条写出依据",
                  "税率表、减除费用、专项附加扣除标准标为真实公开值；社保比例为自拟"],
        unresolved=[]),
    "case-09": dict(
        title="第 13 个月，你的套餐悄悄涨了 80 元",
        medium="1680 × 1060 横向对照卡（手机横屏 / 营业厅窗口）",
        visual_intent="把三条资费摊成 24 个月累计支出曲线，让两处交叉点成为可见的事实，"
                      "再用一张 V 形图回答「第几个月退出最划算」。",
        dsl_caps="三条累计曲线；面积填充；交叉点标记；V 形决策图；暗色判例卡",
        criteria=["累计支出、交叉月份、最低点月份与违约金全部由脚本算出",
                  "两条交叉（第 16、24 个月）落在曲线上并与图例数字一致",
                  "最低点月份必须等于脚本枚举 24 个月后的真实最小值",
                  "判例数字按珠海法院案；资费为自拟演示并声明"],
        unresolved=[]),
    "case-10": dict(
        title="同一颗药，三种剂型，三个不同的时点",
        medium="1400 × 1080 横版药盒卡",
        visual_intent="把说明书那行小字翻译成一条 24 小时时间轴上的三个点："
                      "示意的血糖曲线在上，三条剂型泳道在下，用药时刻与餐时刻的偏移一眼可见。",
        dsl_caps="24 小时血糖曲线（插值采样）；参考带；阈值线；三条泳道；达成峰箭头",
        criteria=["三条泳道的用药时刻按官方科普的相对关系摆放（餐前 15–30 / 餐中餐后 / 晚餐）",
                  "血糖参考带 3.9–6.1 与 7.0 诊断阈值线位置正确",
                  "三条泳道各自的『为什么』与页脚来源一致",
                  "曲线明示为定性示意，剂量不给，不构成用药建议"],
        unresolved=[]),
}

cases = []
for c in data.CASES:
    cid = c["id"]
    png = os.path.join(OUT, cid, "final.png")
    dsl = os.path.join(OUT, cid, "final.snapshot")
    w, h = Image.open(png).size
    m = META[cid]
    reqs = []
    with open(os.path.join(R.TMP, "requests.jsonl"), encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("case_id") == cid:
                reqs.append(r["request_id"])
    drafts = sorted(f for f in os.listdir(R.DRAFTS) if f.startswith(cid + "-"))
    cases.append(dict(
        id=cid, title=m["title"], medium=m["medium"],
        audience=c["audience"], use_context=c["use_context"], user_goal=c["goal"],
        problem=c["problem"],
        content_basis=c["content_basis"],
        real_sources=[{"url": u, "accessed": a, "fact": f} for (u, a, f) in c["sources"]],
        real_numbers=c["real_numbers"],
        declared_demos=c["demos"],
        visual_intent=m["visual_intent"],
        png="case-%s/final.png" % cid.split("-")[1],
        snapshot="case-%s/final.snapshot" % cid.split("-")[1],
        dimensions=[w, h],
        supporting_assets=[],
        dsl_capabilities=m["dsl_caps"],
        completion_criteria=m["criteria"],
        visual_review={
            "how": "每一件都用 read 工具打开最终 PNG 全图查看；细节用 crop.py 放大局部；"
                   "每次渲染后逐条处理 dsllib 的文字溢出告警",
            "evidence_files": sorted("crops/" + f for f in os.listdir(R.CROPS)),
            "result": "见 design-review.md 逐件记录",
        },
        request_ids=reqs,
        draft_dsl_versions=drafts,
        unresolved_issues=m["unresolved"],
    ))

ev = dict(
    schema_version=1, task_id="B06", run_id="20261004-182918",
    generated_at=NOW, generator="tmp/20261004-182918/B06/data.py（唯一事实源，"
                                 "problem-evidence.json 由它生成，不会与图上数字漂移）",
    scope="十个可观察的日常信息难题。每个条目区分『真实来源』与『自拟演示』；"
          "现场调研、用户实验与任何未经核实的引语均未声称做过。",
    problems=[dict(
        id=c["id"], title=META[c["id"]]["title"],
        problem_statement=c["problem"], audience=c["audience"],
        use_context=c["use_context"], user_goal=c["goal"],
        evidence_type="real_public_sources" if c["sources"] else "declared_assumption",
        sources=[{"url": u, "accessed": a, "fact": f} for (u, a, f) in c["sources"]],
        real_numbers=c["real_numbers"],
        declared_demos=c["demos"], content_basis=c["content_basis"],
        scene_requirements=META[c["id"]]["criteria"],
    ) for c in data.CASES],
    method_notes=[
        "所有 URL 均为本次运行中真实抓取/引用的公开页面，访问日期见各条 accessed 字段。",
        "凡属自拟的人物、品牌、机型、资费、用电序列、购物车与血糖曲线，"
        "都在 declared_demos 里逐条写明，未混入 real_numbers。",
        "本作品集没有做用户实验；design-review.md 里凡涉及『更好用了』的判断，"
        "都只写成『从最终图上可观察到的可读性改善』，不写成经过验证的效果。",
    ],
)
with open(os.path.join(OUT, "problem-evidence.json"), "w", encoding="utf-8") as fh:
    json.dump(ev, fh, ensure_ascii=False, indent=2)

PORT = dict(
    schema_version=1, task_id="B06", run_id="20261004-182918",
    status="completed", asset_policy="dsl_only（最终图不含任何外部位图；"
                                     "全部主体由 DSL 生成，未使用 <Image>）",
    curatorial_statement=(
        "这十件作品的共同问题不是『信息太少』，而是『信息的量纲不对』："
        "该比的不是标价而是每单位价格，该看的不是月供而是本金占比，"
        "该读的不是箭头而是决定水平，该看的不是折扣率而是每多花 1 元的边际收益。"
        "每一件都先把用户手里的那一个数换算成真正可比的量纲，再把它排成一条尺子——"
        "货架、月份、指标、人群、档位、小时、规则、月数、剂型，十条尺子的形状都不同，"
        "所以十件作品的构图、配色与阅读顺序也各不相同，不是一套版式换十次字。"
        "真实阈值与规则来自官方或权威公开页面并逐条标注；"
        "凡是人物、价格、机型、资费、用电与血糖序列，都在自己的页面上写明是演示设定。"),
    cases=cases,
    final_collection_review=(
        "十件全部为服务真实响应的原始 PNG，尺寸分别为 "
        + "、".join("%s %dx%d" % (c["id"], c["dimensions"][0], c["dimensions"][1])
                    for c in cases)
        + "；每件的 final.snapshot 与 final.png 同源同版；"
          "十件各自解决不同问题、没有同版式换色；"
          "本次复审逐张打开后又修掉了 case-05 的颜色名被截断、case-06 的一档上限数字压在柱体上、"
          "case-07 的 ② 与 ③ 编号重叠与金额标签被墙线穿过、case-08 的标题数字与算法不一致"
          "（详见 design-review.md 与 snapshot-usage.md 的问题表）。"),
    unresolved_issues=[],
)
with open(os.path.join(OUT, "portfolio.json"), "w", encoding="utf-8") as fh:
    json.dump(PORT, fh, ensure_ascii=False, indent=2)

# ------------------------------------------------------------------- gallery
def esc(s):
    return html.escape(str(s))


cards = []
for c in cases:
    cards.append(
        '<figure class="card"><a href="{png}" target="_blank" rel="noopener">'
        '<img src="{png}" alt="{t}" loading="lazy" width="{w}" height="{h}"></a>'
        '<figcaption><div class="no">{no}</div><h2>{t}</h2>'
        '<p class="sub">{med}</p><p class="aud">{aud}</p>'
        '<p class="src">{src}</p>'
        '<p class="links"><a href="{png}" target="_blank" rel="noopener">原尺寸 PNG</a>'
        ' · <a href="{dsl}">final.snapshot</a>'
        ' · <a href="{md}">case.md</a></p></figcaption></figure>'.format(
            png=c["png"], dsl=c["snapshot"], md=c["id"] + "/case.md",
            t=esc(c["title"]), med=esc(c["medium"]), aud=esc(c["audience"]),
            src=esc("来源 %d 个公开页面 · %d 条真实数值 · 自拟演示 %d 条"
                    % (len(c["real_sources"]), len(c["real_numbers"]),
                       len(c["declared_demos"]))),
            w=c["dimensions"][0], h=c["dimensions"][1],
            no=c["id"].split("-")[1]))

GAL = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>B06 · 把十个日常信息难题变成惊艳而好用的作品</title>
<style>
:root{--ink:#0B1220;--ink2:#1E293B;--mute:#64748B;--hair:#E2E8F0;--paper:#F7F8FA}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
 font-family:Inter,"Noto Sans CJK SC","Microsoft YaHei",sans-serif;line-height:1.6}
header{background:var(--ink);color:#fff;padding:28px 32px 24px;border-left:8px solid #4F46E5}
header h1{margin:0 0 6px;font-size:30px}
header p{margin:4px 0;color:#C7C9FF;font-size:15px}
header .meta{color:rgba(255,255,255,.62);font-size:13px;margin-top:10px}
main{padding:26px 32px 60px;max-width:1760px;margin:0 auto}
h2.sec{font-size:18px;margin:28px 0 12px;padding-bottom:8px;border-bottom:2px solid var(--hair)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:22px}
.card{background:#fff;border:1px solid var(--hair);border-radius:16px;overflow:hidden;
 margin:0;box-shadow:0 6 22px rgba(15,23,42,.07)}
.card img{display:block;width:100%;height:auto;background:#fff}
.card figcaption{padding:14px 16px 16px;border-top:1px solid var(--hair);position:relative}
.card .no{position:absolute;top:-14px;left:16px;background:#0B1220;color:#fff;
 border-radius:999px;padding:2px 11px;font-size:12px;letter-spacing:.04em}
.card h2{margin:8px 0 4px;font-size:19px}
.card .sub{margin:0 0 6px;color:var(--ink2);font-size:13px}
.card .aud{margin:0 0 6px;color:var(--mute);font-size:13px}
.card .src{margin:0 0 8px;color:#0F766E;font-size:12px}
.card .links{margin:0;font-size:13px}
.card .links a{color:#4338CA}
.note{background:#fff;border:1px solid var(--hair);border-radius:14px;padding:16px 20px;
 margin:0 0 20px;font-size:14px;color:var(--ink2)}
table{border-collapse:collapse;width:100%;background:#fff;border-radius:12px;overflow:hidden;
 border:1px solid var(--hair);font-size:13px}
th,td{border-bottom:1px solid var(--hair);padding:8px 10px;text-align:left;vertical-align:top}
th{background:#F1F5F9;font-size:12px;letter-spacing:.03em}
tr:last-child td{border-bottom:none}
a{color:#4338CA}
</style></head><body>
<header>
<h1>把十个日常信息难题变成惊艳而好用的作品</h1>
<p>{{CUR}}</p>
<p class="meta">B06 · run 20261004-182918 · 10 件主作品 · 每件 final.png 均为 open-snapshot
服务的原始响应字节，未做任何后处理；全部主体由 DSL 生成，未嵌入外部位图。</p>
</header>
<main>
<div class="note"><strong>怎么看这一页：</strong>点任意一张图打开原尺寸 PNG；
每件作品旁边有它的 <code>final.snapshot</code>（与该 PNG 同一次渲染的完整 DSL）与
<code>case.md</code>（场景 / 内容 / 视觉选择 / 实际自检）。本页面全部为相对链接，
不加载任何远程脚本或远程字体，断网也能浏览。</div>
<h2 class="sec">十件作品</h2>
<div class="grid">
{{CARDS}}
</div>
<h2 class="sec">总览</h2>
<table>
<tr><th>#</th><th>作品</th><th>尺寸</th><th>受众</th><th>它解决的问题</th><th>真实来源</th></tr>
{{ROWS}}
</table>
<h2 class="sec">其余交付</h2>
<p><a href="portfolio.json">portfolio.json</a> ·
<a href="portfolio.md">portfolio.md</a> ·
<a href="problem-evidence.json">problem-evidence.json</a> ·
<a href="design-review.md">design-review.md</a> ·
<a href="snapshot-usage.md">snapshot-usage.md</a> ·
<a href="task-metrics.json">task-metrics.json</a></p>
</main></body></html>
"""

rows = []
for i, c in enumerate(cases, 1):
    rows.append("<tr><td>%d</td><td>%s</td><td>%d×%d</td><td>%s</td><td>%s</td><td>%d 个</td></tr>"
                % (i, esc(c["title"]), c["dimensions"][0], c["dimensions"][1],
                   esc(c["audience"]), esc(c["problem"][:70] + "…"),
                   len(c["real_sources"])))

GAL = GAL.replace("{{CUR}}", esc(PORT["curatorial_statement"][:230] + "…"))
GAL = GAL.replace("{{CARDS}}", "\n".join(cards))
GAL = GAL.replace("{{ROWS}}", "\n".join(rows))
with open(os.path.join(OUT, "gallery.html"), "w", encoding="utf-8") as fh:
    fh.write(GAL)
print("wrote problem-evidence.json / portfolio.json / gallery.html for", len(cases), "cases")