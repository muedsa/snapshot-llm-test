# -*- coding: utf-8 -*-
"""Append A23 iteration records (seq 1-4) + summarize request stats."""
import json

E = [
    dict(seq=1, kind="baseline", at="2026-10-19T15:06:19.425+08:00",
         rid="A23-f01..f06 + A23-cover-01(失败) + A23-probe-01",
         image="tmp/run-20261011-01/A23/contact-sheet.png",
         viewed_at="2026-10-19T15:13:00+08:00",
         observation=("探针A23-probe-01实测：background=transparent返回RGBA四角"
                      "alpha=0（透明真实）；矩阵+45°使端点标记落到右下=正角顺时针。"
                      "首批6帧渲染200，接触表实看：透明真实、F6为可识别相机、"
                      "12单元逐帧存在；像素可见性检测发现缺陷：F1 U05红点0.02"
                      "（整圆被后绘制的U07握持条覆盖，手算握持条倾斜方向搞反）、"
                      "F2 U05 0.08、F2 U04 0.31与F3 U04 0.42（黄色闪光滑到"
                      "镜头内圈下方）；cover-01渲染400"),
         action=("U04起点(500,500,30°)→(74,40,30°)改走左上走廊；"
                 "U05起点(70,150)→(36,300)；封面幽灵元素改为Positioned外层"
                 "（Opacity只包内层box）"),
         result="v2 DSL（frame v2 + cover v2）", defect="单元被其他单元完全覆盖"),
    dict(seq=2, kind="syntax-fix", at="2026-10-19T15:07:59.522+08:00",
         rid="A23-cover-02",
         image="tmp/run-20261011-01/A23/cover-02.png",
         viewed_at="2026-10-19T15:23:30+08:00",
         observation=("cover-01 400 RENDER_ERROR 'renderBox.parentData must be "
                      "StackParentData'：Opacity包裹了Positioned（Positioned必须"
                      "是Stack直接子节点）。修正发射顺序后cover-02渲染200；"
                      "实看封面：标题'从结构到画面'大号可读，右侧相机成图+幽灵"
                      "单元+汇聚虚线，页脚timing/frame-data指引清楚"),
         action="Opacity/Transform改包内层SizedBox，Positioned保持Stack直接子节点",
         result="封面定稿（不计入帧动画交付图）", defect=None),
    dict(seq=3, kind="visual",
         at="2026-10-19T15:15:28.123+08:00", rid="A23-f01b..f05b",
         image=None, viewed_at=None,
         evidence=dict(
             frame="tmp/run-20261011-01/A23/frames/frame-03b.png",
             verify="tmp/run-20261011-01/A23/verify-report.json",
             overlap_script="tmp/run-20261011-01/A23/scripts/a23_overlap.py"),
         observation=("b系列复测：F1 U05→0.92、F2/F3 U04修复确认；但F3 U05=0.00"
                      "——像素采样(143,258)=#475569(U11底板色)，几何覆盖脚本确认"
                      "F3姿态下U05整圆落在U11板带内（底板左端下垂）。"
                      "（本缺陷由像素可见性检测+几何分析发现，非看图发现；"
                      "修复效果由seq4看图+复测确认）"),
         action="U05起点(36,300)→(36,120)改走上走廊，避开底板F3板带",
         result="v3 DSL（最终帧DSL）", defect="单元被底板完全覆盖"),
    dict(seq=4, kind="visual", at="2026-10-19T15:22:51.832+08:00",
         rid="A23-f01c..f05c (+frame-06同DSL复用)",
         image="tmp/run-20261011-01/A23/contact-sheet.png",
         viewed_at="2026-10-19T15:23:30+08:00",
         observation=("c系列全检通过：每帧每单元纯色像素占比≥0.508（无完全遮挡），"
                      "12色集合逐帧守恒，四角alpha=0、透明面积0.62–0.74；"
                      "接触表+逐帧600×600整图+封面实看：U05红点/U04黄闪在6帧中"
                      "全部清晰可见，F1分散→F6相机的汇聚过程连续可读，"
                      "F6末帧为可识别相机图形，帧内无文字"),
         action="通过视觉回归，归档交付（原始字节复制+md5/alpha断言）",
         result="A23最终交付定稿", defect=None),
]

with open("tmp/run-20261011-01/A23/iterations.jsonl", "a",
          encoding="utf-8") as fh:
    for e in E:
        fh.write(json.dumps(e, ensure_ascii=False) + "\n")

reqs = [json.loads(l) for l in
        open("tmp/run-20261011-01/A23/requests.jsonl", encoding="utf-8")]
ok = [r for r in reqs if r["ok"]]
print("iterations appended (seq 1-4)")
print("requests: %d total, %d ok, %d failed, sum=%.3fs"
      % (len(reqs), len(ok), len(reqs) - len(ok),
         sum(r["elapsed_seconds"] for r in reqs)))
print("failed:", [(r["id"], r["status"]) for r in reqs if not r["ok"]])
