# -*- coding: utf-8 -*-
"""B02 final wrap-up: log the three iterations made in this session, then call
wrapup.wrapup() to regenerate task-metrics.json and update the suite state."""
import json
import os
import sys
from datetime import datetime, timezone, timedelta

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
sys.stdout.reconfigure(encoding="utf-8")
CST = timezone(timedelta(hours=8))


def now():
    return datetime.now(CST).isoformat()


ITERS = [
    ("B02-c09-v02", "B02-c09-v01", "visual-iteration",
     r"tmp\20261004-182918\B02/drafts/case-09.v02.snapshot",
     r"outputs\20261004-182918\B02/case-09/final.png",
     "复看 v01：三个 marker ②③ 与楼块文字的中心点重合，38px 圆盘直接盖住"
     "「新华里小学」和「纺机厂宿舍」；路线标签「9 分钟」正压在虚线折线上被虚线划穿"
     "「分钟」两字；最严重的是数据与图形互相矛盾——1→2 实绘 137px 却标 11 分钟，"
     "1→3 实绘 170px 却标 9 分钟，即更短的线反而说走得久，而主站自己还挂着一个"
     "无来源的「步行 4 分钟」。用 crop.py 3 倍放大 700,360-1040,500 逐项确认。",
     "marker 改为压在朝向路线的楼块边缘（社区服务中心东缘 / 小学西缘 / 宿舍东缘），"
     "与楼块文字中心彻底分离；路线标签加米纸光晕底板并排到路线之后绘制，"
     "使虚线无法穿字；删除米制比例尺（它与平面自相矛盾），改在页脚写明换算口径"
     "且只对路线成立；两条路线改为沿街折线（经纺机路、过沿河桥），"
     "步行分钟数由脚本从折线长度 × 1.38 m/px ÷ 75 m/min 换算取整，"
     "标题里的「最远」也由计算值生成，脚本内加 assert 锁定 (4, 8)。",
     True,
     "复看 v02 输出：三处碰撞全部消除；两个分钟标签均坐在光晕底板上；"
     "4 分钟 < 8 分钟，与所绘路线长度 217px < 436px 单调一致；主站不再有伪时间。"),
    ("B02-c05-v03", "B02-c05-v02", "visual-iteration",
     r"tmp\20261004-182918\B02/drafts/case-05.v03.snapshot",
     r"outputs\20261004-182918\B02/case-05/final.png",
     "复看 v02：仅 214px 宽的留存联里有两处碰撞——四个「处理结果」勾选框从 y=286 "
     "排到 y=371，而撕线说明「沿此撕开 · 留存联归柜台」画在 y=H-48=372、横跨 "
     "x=840..1040，正好压住第 4 行勾选框；等宽流水号又落在 y=384 位于说明正下方。"
     "用 crop.py 3 倍放大 880,330-1200,420 确认。",
     "把撕线说明移到第一行右侧的空白处（x=664..880 右对齐，y=44）——那里本来就是"
     "撕线的起点，说明与撕线同行更合逻辑；勾选框行距 23→22 且起点 286→284，"
     "末行结束于 360；流水号下移到 y=376，使留存联内容结束于 392，落在 400px 卡片内边之内。",
     True,
     "复看 v03：四个勾选框与流水号全部完整，撕线说明独占第一行右侧，"
     "三者无任何重叠；正文三个操作步骤仍在 48..880 预算内。"),
    ("B02-c06-v03", "B02-c06-v02", "visual-iteration",
     r"tmp\20261004-182918\B02/drafts/case-06.v03.snapshot",
     r"outputs\20261004-182918\B02/case-06/final.png",
     "复看 v02：第三栏上半部的「本场前 10 件」条形图末行（衣物织补）结束于 y=800，"
     "而第 06 栏标题「06 近 6 个月修好件数」正好也画在 y=800，"
     "条形、数值「1」与栏标题落在同一条 22px 高度带内互相压字。"
     "用 crop.py 3 倍放大 1240,780-1754,860 确认。",
     "选择收紧第三栏上半部而不是下移第 06 栏——下移 LY 会让 04 栏的两块书写框"
     "压到 y=1106 的签名线（实测 LY+28 即冲突）。改为：零件行距 30→28、"
     "结论行距 34→32、条形行距 26→24。末行结束于 y=785，"
     "与栏标题之间留出 18px，与本页其它分区间距一致。",
     True,
     "复看 v03：第 06 栏标题与上方条形图完全分离，六个分区标题互不压字；"
     "六个月柱状图数值 186/199/214/231/228/217 仍与 data.LEDGER 一致；"
     "两块书写框与页脚签名线无重叠。"),
]

import wrapup  # noqa: E402

rows = []
for vid, parent, kind, dsl, img, obs, chg, complete, recheck in ITERS:
    rows.append((vid, parent, kind, dsl, img, now(), obs, chg, complete))

ARTIFACTS = [
    "case-01/final.png", "case-01/final.snapshot", "case-01/case.md",
    "case-02/final.png", "case-02/final.snapshot", "case-02/case.md",
    "case-03/final.png", "case-03/final.snapshot", "case-03/case.md",
    "case-04/final.png", "case-04/final.snapshot", "case-04/case.md",
    "case-05/final.png", "case-05/final.snapshot", "case-05/case.md",
    "case-06/final.png", "case-06/final.snapshot", "case-06/case.md",
    "case-07/final.png", "case-07/final.snapshot", "case-07/case.md",
    "case-08/final.png", "case-08/final.snapshot", "case-08/case.md",
    "case-09/final.png", "case-09/final.snapshot", "case-09/case.md",
    "case-10/final.png", "case-10/final.snapshot", "case-10/case.md",
    "portfolio.json", "portfolio.md", "gallery.html", "snapshot-usage.md",
    "task-metrics.json", "project-brief.md", "design-system.json",
    "touchpoint-map.json",
]

EVIDENCE = (
    "十件全部 200 响应并逐张用 read 工具打开实际 PNG 查看：case-01/02/03/04/07/08/10 "
    "首轮查看后判定通过（未制造无意义迭代）；case-05/06/09 在本次会话重新打开后"
    "用 crop.py 3 倍局部放大确认了真实碰撞并修复，再次打开 PNG 复看通过。"
    "10 件 final.png 与同名 final.snapshot 逐字节配对（sha256 比对 drafts/ 下同版本快照一致）。"
)

UNRESOLVED = [
    "服务端未提供任何 token / 图像用量 / 费用计量接口，本次运行没有取得权威数值，"
    "task-metrics.json 中相应字段全部为 null，未按字数或余额估算。",
    "服务端 Server-Timing 未报告 queue 段，排队等待时间不可测，记为 null 而非 0。",
    "case-09 的示意平面未按实测地图绘制；换算系数（1 px ≈ 1.38 m）只对脚本绘制的"
    "路线成立，楼块大小为示意，这一点已印在作品页脚。",
    "十件中未使用任何辅助素材（run-config 允许 dsl_primary_with_supporting_assets），"
    "因此没有素材来源与许可需要记录。",
]

NOTES = (
    "本任务分两次会话完成：第一次会话完成 01-08 与 10 的渲染并逐件看图，"
    "在写交付文档前被中断；本次会话接续已有产物，未从零重做，"
    "只做了三处基于实际看图发现的真实修复（case-05/06/09）并补齐全部交付文档。"
)

STARTED = json.load(open(os.path.join(ROOT, "tmp", RUN, "B02", "b02-start.json"),
                         encoding="utf-8"))["started_at"]
FIRST_IMAGE = "2026-10-05T05:28:12+08:00"
ENDED = now()

m = wrapup.wrapup("B02", STARTED, FIRST_IMAGE, ENDED, rows,
                  artifacts=ARTIFACTS, visual_evidence=EVIDENCE,
                  unresolved=UNRESOLVED, notes=NOTES, status="completed",
                  rounds=["round-01", "round-02 (resume: final review + delivery docs)"],
                  cases=["case-%02d" % i for i in range(1, 11)])

print(json.dumps({k: m[k] for k in ("counts", "wall_clock_seconds_total",
                                    "wall_clock_seconds_to_first_usable_image",
                                    "sum_of_request_durations_seconds")},
                 ensure_ascii=False, indent=2))