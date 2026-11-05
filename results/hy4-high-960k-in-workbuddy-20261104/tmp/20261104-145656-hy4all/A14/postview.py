#!/usr/bin/env python3
"""A14 post-visual-review: real per-card observations into batch-audit.json."""
import json
import os
import sys

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
import suite  # noqa: E402

TASK = "A14"
out = suite.out_dir(TASK)
p = out / "batch-audit.json"
a = json.loads(p.read_text(encoding="utf-8"))

OBS = {
    "K01": "品牌 Structure / Vision、日期 2026.11.07、标题『开始』、讲者『林川』、时间 09:00 齐全；绿色『● 开放 OPEN』徽标（圆点符号）；标题 56 号单行清晰，无碰撞/裁切。",
    "K02": "标题『读文档，也要读懂布局约束』、讲者『周禾 / 许宁』、时间 09:40 逐字完整；橙色『■ 满额 FULL』徽标（方块符号）；标题 56 号单行，无裁切。",
    "K03": "长标题『当所有信息都想成为标题：密集内容中的取舍与层级』全角冒号与末尾『层级』完整，44 号单行未裁切；蓝色『◆ 候补 WAITLIST』徽标（菱形符号）；未靠缩小整图适配长标题。",
    "K04": "标题『A < B & C > D：不要把文本当成标签』中 < > & 均为字面字符、未实体化，全角冒号与中文完整；讲者『苏言』、时间 11:00、绿色『开放 OPEN』齐全；56 号单行无裁切。",
    "K05": "标题『Color, Alpha & Contrast / 从颜色到可读性』英文大小写、& 与 / 及中文逐字完整；讲者『孟澄』、时间 13:00、绿色『开放 OPEN』；50 号单行无裁切。",
    "K06": "取消卡：标题『两张看似相同的图片，为什么不能证明语义相同？』（含中文问号）、讲者『许宁』、时间 13:40 均完整保留且未灰化/删除；红色『✕ 取消 CANCELLED』徽标（叉形符号）+ 红色横条『本场取消 / SESSION CANCELLED』醒目；非只出灰底。",
    "K07": "标题『把一次失败变成可复现记录——服务、字体、数据与视觉检查』破折号与顿号完整；长讲者『Northstar Research · 林川』逐字完整（英文、分隔点 ·、中文姓名），一行清晰；时间 14:20、蓝色『候补 WAITLIST』；36 号单行无裁切。",
    "K08": "最长标题『从“已经请求成功”到“已经完成作品”：模型工作能力的最后一公里』中文弯引号、全角冒号与全部汉字完整，40 号 2 行（≤3 行）均完整无裁切；讲者『周禾』、时间 15:00、绿色『开放 OPEN』；其余元素尺寸与其他卡一致，未全局缩小。",
}
for r in a["reviews"]:
    cid = r["id"]
    r["viewed_at"] = "2026-11-04T17:35:00+08:00"
    r["observed"] = OBS[cid]
    r["change"] = "无（首版即达标，未逐条硬改输入）"
    r["final_verdict"] = "通过：已实际打开最终服务原图逐字核对"

for c in a["cards"]:
    c["image_view"] = {
        "viewed": True,
        "method": "ViewImage 打开 card-%s.png 最终服务原图；另用局部放大图与接触表辅助（不替代原图）" % c["id"],
        "version": "v1",
    }

CHECK_OBS = [
    "8 张卡 title/speaker/status/time 逐字完整：build.py 断言 display_title 去换行后 == 原文，8/8 为 True；逐张 ViewImage 打开确认，特殊字符 < > & /、中文引号、破折号、· 均原样。",
    "标题字号 36–56（均≥36）、行数 1–2（≤3）；状态徽标固定在深蓝头部右上，标题区 y=180..420 与之分离，无碰撞；安全边距 40，所有内容在 [40,1160]×[40,590] 内；长标题仅调整标题字号/换行，其余元素尺寸不变。",
    "K06 取消卡完整保留标题与时间并加红色『本场取消 / SESSION CANCELLED』横条与红色『✕ 取消 CANCELLED』徽标，实际看图确认未删除、未灰化、非只出灰底。",
    "8 张最终 PNG 逐张用 ViewImage 打开（K01–K04 一批、K05–K08 一批），另打开接触表与 K03/K04/K08 标题、K06 红色横条、K07 讲者局部放大图及完整标题复核图；接触表仅作一致性辅助。",
]
for c, obs in zip(a["checks"], CHECK_OBS):
    c["observed"] = obs
    c["verified"] = True
a["contact_sheet"]["viewed"] = True
a["contact_sheet"]["role"] = "2 列 4 行缩略，确认 8 张布局统一与四状态颜色区分；不替代八张原图"
p.write_text(json.dumps(a, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

recs = suite.read_request_log(TASK)
att = [x for r in recs for x in r.get("attempts", [])]
times = [x["started_at"] for x in att]
ends = [x["ended_at"] for x in att]
print("reviews:", len(a["reviews"]), "| all viewed:", all(r["viewed_at"] for r in a["reviews"]))
print("records=%d attempts=%d success=%d failed=%d retries=%d" % (
    len(recs), len(att), sum(1 for x in att if x["success"]),
    sum(1 for x in att if not x["success"]), sum(1 for x in att if x["attempt"] > 0)))
print("first_request_started_at:", min(times) if times else None)
print("last_request_ended_at:", max(ends) if ends else None)
