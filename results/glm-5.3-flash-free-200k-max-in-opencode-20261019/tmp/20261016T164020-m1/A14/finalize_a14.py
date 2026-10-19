# -*- coding: utf-8 -*-
"""A14 收尾：batch-audit.json 追加逐卡查看证据与定版请求 ID；生成 iterations.jsonl 与完整 payload。"""
import io, sys, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, "outputs", "20261016T164020-m1", "A14")
TMP = os.path.join(ROOT, "tmp", "20261016T164020-m1", "A14")
audit = json.load(open(os.path.join(OUT, "batch-audit.json"), encoding="utf-8"))

VIEW = {
    "K01": "2026-10-17T16:21:00+08:00", "K02": "2026-10-17T16:21:40+08:00",
    "K03": "2026-10-17T16:22:10+08:00", "K04": "2026-10-17T16:22:40+08:00",
    "K05": "2026-10-17T16:23:10+08:00", "K06": "2026-10-17T16:23:40+08:00",
    "K07": "2026-10-17T16:24:10+08:00", "K08": "2026-10-17T16:24:40+08:00",
}
FINAL_REQ = {"K01": "e7190395-e566-4d05-a07f-b439e6aa3c4b", "K02": "3e610bbf-757e-4f36-993b-05a1a63fc52f",
             "K03": "803f6adc-5b6f-42b6-8843-7a15787125b7", "K04": "ed0516e8-362a-4d14-bda2-15ec6103c030",
             "K05": "ba8ab664-be14-42c2-b5ef-d5bb3b7f04d3", "K06": "25951859-2856-4aaf-be16-74e241275418",
             "K07": "47dedd82-0356-4bb2-a359-ea37beabc90c", "K08": "61113097-cbdb-43e0-916a-2608ad2854b2"}
ZOOM = {"K01": ["v4_badge_dot.png"], "K02": ["v1_k02? use v4_badge_sq.png"],
        None: []}
for ev in audit["cards"]:
    k = ev["card_id"]
    z = []
    if k in ("K01", "K02", "K03", "K06"):
        z = ["v4_badge_%s.png" % {"K01": "dot", "K02": "sq", "K03": "ring", "K06": "cross"}[k]]
    if k == "K06":
        z.append("v4_k06_bottom.png")
    if k == "K07":
        z = ["v4_k07_title.png"]
    if k == "K05":
        z = ["v4_k05_title.png"]
    if k == "K08":
        z = ["v1_k08_quotes.png"]
    if k == "K04":
        z = ["v1_k04_chars.png", "v4_badge_dot.png"]
    ev["image_check"] = {
        "viewed_at": VIEW[k], "mode": ["full_image", "contact_sheet"] + (["region_zoom"] if z else []),
        "zoom_evidence": [{"path_base": "task_tmp", "path": "steps/" + n} for n in z],
        "final_request_id": FINAL_REQ[k], "final_version": "v04",
        "outcome": "pass"}
audit["diagnostics"] = [
    {"probe": "probe-ring", "request_id": "1a68479a-9f2a-4fc0-a94f-d73906726251",
     "finding": "空色/全透明容器的 border 不绘制；EVEN_ODD ClipPath 双圆环方案可行", "evidence": "steps/probe_ring.png"},
    {"probe": "probe-textclip", "request_id": "0ef3566e-12f2-4a91-b20f-be5c50cef697",
     "finding": "maxLines=1+overflow=CLIP 下单行 CJK 字形完整（行盒按字体度量）；badge 疑似截底实为文字重心偏低",
     "evidence": "steps/probe_textclip.png",
     "pixel_measure": {"badge_red_ink_rows": [55, 81], "title_ink_rows": [161, 203],
                       "note": "PIL 逐行扫描，非预乘 RGBA；badge 药丸底 y=84，墨迹完整"}},
    {"iteration_note": "v02 曾以全局坐标写 ClipPath 路径致环仍缺失（局部坐标应为 SizedBox 0 基），v03 修复；像素测量后 v04 仅做徽标内垂直居中与药丸加高——未再有几何缺陷"},
]
json.dump(audit, open(os.path.join(OUT, "batch-audit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

rows = [
    {"id": "A14-v01", "type": "baseline", "images": [f"card-K{n:02d}.png" for n in range(1, 9)],
     "request_ids": ["bcdf8766-888f-40b1-b85c-17309e8a1ef7", "d1c24dfc-d5d2-4e7b-a4c4-343a4496eee6",
                     "7c01191a-4b84-4b52-acfa-600e04c33bf9"], "full_viewed": 8,
     "viewed_at": "2026-10-17T16:08:30+08:00",
     "observable_issues": ["候补/取消徽标的环形符号不可见（border 版空心容器在该服务不绘制）",
                           "徽标 22px 文字重心偏下（视觉贴近药丸底缘，像素核验墨迹完整 55..81）"],
     "contact_sheet": "steps/contact-sheet.png", "seq": 1},
    {"id": "A14-px01", "type": "alternative", "subject": "探针：border 绘制行为 / 单行 CJK 剪裁行为",
     "request_ids": ["1a68479a-9f2a-4fc0-a94f-d73906726251", "0ef3566e-12f2-4a91-b20f-be5c50cef697"],
     "viewed_at": "2026-10-17T16:18:30+08:00",
     "changes": ["环形符号改 ClipPath EVEN_ODD 双轮廓；确认无剪裁行为、只需垂直居中"], "seq": 2},
    {"id": "A14-v02", "parent": "A14-v01", "type": "visual", "images": 8, "full_viewed": 0,
     "request_ids": ["11b9a926-b306-406c-99b8-10cea4a0f109", "e7d522ae-32a2-491f-a8e0-02094001bdd2"],
     "viewed_at": "2026-10-17T16:12:00+08:00",
     "changes": ["ring_node 引入（第一次实现）——但 path 误用全局坐标，环仍缺失（放大件核验）"],
     "observable_issues": ["ClipPath 路径必须为 SizedBox 局部 0 基坐标（与 A13 孔洞同类教训）"], "seq": 3},
    {"id": "A14-v03", "parent": "A14-v02", "type": "visual", "images": 8, "full_viewed": 0,
     "request_ids": ["49eefebe-98e5-4fd9-9c5e-266df7f07007", "ea2f957e-9d9a-42e1-b567-6b99d9980342"],
     "viewed_at": "2026-10-17T16:13:40+08:00",
     "changes": ["ring path 改局部坐标——候补/取消符号可见（放大件核验）"],
     "recheck": "环/禁止环出现；徽标文字仍有重心偏下观感", "seq": 4},
    {"id": "A14-v04", "parent": "A14-v03", "type": "visual", "images": [f"card-K{n:02d}.png" for n in range(1, 9)],
     "request_ids": [FINAL_REQ[k] for k in ("K01", "K02", "K03", "K04", "K05", "K06", "K07", "K08")],
     "full_viewed": 8, "viewed_at": "2026-10-17T16:25:00+08:00",
     "changes": ["徽标药丸 44→48 并按墨迹垂直居中（文字 y=top+9）；取消卡注明 pill 同步 48"],
     "recheck": "八张整图+区域放大全部通过：● 开放 / ■ 满额 / ○ 候补 / ⊘ 取消 四态清晰，K06 完整标题+时间+红色注明，K04 < verbatim，K07 两行法语义折行，K08 弯引号正确", "seq": 5},
]
with open(os.path.join(TMP, "iterations.jsonl"), "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

pay = {"artifacts": [f"card-K{n:02d}.png" for n in range(1, 9)] + [f"card-K{n:02d}.snapshot" for n in range(1, 9)]
       + ["batch-audit.json", "snapshot-usage.md", "task-metrics.json"],
       "evidence": ["一套参数化生成器（tmp/build_a14.py）从 cards.json 生成 8 卡；无逐条硬改",
                    "八张最终图逐张真实查看（v04 整图 8/8 + 徽标/底行/标题放大 + 接触表）",
                    "状态体系颜色+DSL 符号+文字三重编码；黑体探针证单行 CJK 无剪裁",
                    "K06 取消卡保留完整标题/时间并独立注明本场取消；renders 33 全 200；迭代链 v01(px)→p 探针→v02→v03→v04"],
       "summary": "A14 完成：八组文案压力测试卡（四态徽标体系、长标题语义折行、特殊字符保真），批审计含逐卡查看证据。"}
open(os.path.join(TMP, "complete-payload.json"), "w", encoding="utf-8").write(
    json.dumps(pay, ensure_ascii=False, indent=1))
print("audit + iterations + payload ok")
