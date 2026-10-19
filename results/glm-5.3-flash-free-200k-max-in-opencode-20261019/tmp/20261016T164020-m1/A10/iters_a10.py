# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
R = "20261016T164020-m1"
PB = "suite_root"
rows = [
    {"id": "A10-s01", "parent": None, "type": "baseline", "image": "compositing-lab.png", "dsl": "compositing-lab.snapshot",
     "request_id": "12055d44-3508-4f64-9a9e-973b707a3dad",
     "note": "v01（req 13d4907d）为同一 DSL 的先行渲染，未查看未采用；首个被查看版本记为基线。",
     "observable_issues": [
         "③④ 卡内完全平色：条纹不可辨（后证实根因为颜色格式误用——8 位颜色 DSL 为 #RRGGBBAA（末组 alpha），玻璃误写 #B3FFFFFF 实为不透明青色）",
         "采样发现审计 G 公式错误：① G 应为 (127/255)²·255≈63 而非 127（红残余被蓝二次衰减）——审计文档问题，非图像缺陷，随本轮修正"],
     "changes": ["整图+z2 采样点检查；steps/v2_p1..p6 六张放大取证"],
     "comparison": "baseline", "recheck": None, "seq": 1, "path_base": PB, "viewed_at": "2026-10-17T14:50:20+08:00"},
    {"id": "A10-v03", "parent": "A10-s01", "type": "visual", "image": "compositing-lab.png", "dsl": "compositing-lab.snapshot",
     "request_id": "e5951c42-4947-43c4-bac8-707d0e96c366",
     "observable_issues": ["误诊尝试：玻璃 #B3FFFFFF→#59FFFFFF 仍为不透明青色（未意识到 #59FFFFFF=RGB(0x59,0xFF,0xFF)+αFF），卡内依旧平色"],
     "changes": ["仅换色值（无效改动，保留过程记录）"],
     "comparison": "v3_p3 平色依旧", "recheck": "未解决", "seq": 2, "path_base": PB, "viewed_at": "2026-10-17T14:51:05+08:00"},
    {"id": "A10-v04", "parent": "A10-v03", "type": "visual", "image": "compositing-lab.png", "dsl": "compositing-lab.snapshot",
     "request_id": "3d7d08c9-4e4a-41f2-b48a-d035437483ad",
     "observable_issues": ["条纹节距 28→56（宽28/间28）：σ6 模糊下低频对比保留约 64%，卡外条纹视觉更稳（该改动为正向保留）；卡内仍平色（同一根因未除）"],
     "changes": ["stripes() 复刻与 ④ 卡内条纹复刻同步改为 k·56"],
     "comparison": "v4_p3 卡外条纹更清晰；卡内仍平色", "recheck": "部分改善（卡外）", "seq": 3, "path_base": PB, "viewed_at": "2026-10-17T14:57:10+08:00"},
    {"id": "A10-v05", "parent": "A10-v04", "type": "visual", "image": "compositing-lab.png", "dsl": "compositing-lab.snapshot",
     "request_id": "947bab9e-4ffd-4c72-8bf2-8e0c37c0f342",
     "observable_issues": ["根因修复：依据 parser-tags.txt（缓存）确认 8 位颜色= #RRGGBBAA（末组 alpha）→ 玻璃改 #FFFFFF59（白 35%），阴影色 #3A000000（实为暗红全不透明）改 #0000003A",
                            "③ 卡内现呈 σ6 模糊暗带+玻璃；④ 全子树糊（BLUR 不可读）；卡外锐利——配对差异成立"],
     "changes": ["glass() 颜色 #60?? → #FFFFFF59；chip boxShadow 颜色改 #0000003A（后续 v06 加强至 #00000055）"],
     "comparison": "v5_p3/v5_p4：③ 毛玻璃纹理可见+SHARP 清晰；④ 整块糊+BLUR 糊——差异与 ③④ 设定一致", "recheck": "③④ 通过", "seq": 4, "path_base": PB, "viewed_at": "2026-10-17T14:59:30+08:00"},
    {"id": "A10-v06", "parent": "A10-v05", "type": "visual", "image": "compositing-lab.png", "dsl": "compositing-lab.snapshot",
     "request_id": "270345b3-ca88-4b80-bd50-3f418bc2e37b",
     "observable_issues": ["⑤⑥ 芯片阴影 0x3A 过淡（1× 观看融入橄榄底）→ 加强为 #00000055（33% 黑），4× 放大阴影晕清晰（题面要求阴影可观察）"],
     "changes": ["boxShadow 颜色 0x3A→0x55（4 处同步文案）"],
     "comparison": "v6_chipA 阴影可辨；整图 12 处元素齐全", "recheck": "⑤⑥ 通过", "seq": 5, "path_base": PB, "viewed_at": "2026-10-17T15:03:35+08:00"},
    {"id": "A10-v07", "parent": "A10-v06", "type": "visual", "image": "compositing-lab.png", "dsl": "compositing-lab.snapshot",
     "request_id": "92d811cb-7cc6-4207-a944-ada34949c6e0",
     "observable_issues": ["第二排说明文字相挤：④ 标题『④ 卡内整体子树模糊（ImageFiltered）』伸至 ⑤ 列边界与 ⑤ 标题视觉相连（ASCII 实宽超估值）——缩短为『④ 子树模糊（ImageFiltered）』"],
     "changes": ["DESC[4][0] 缩短"],
     "comparison": "v7_row2desc：④/⑤ 已分离，但发现 ⑤ 标题又与 ⑥ 相触（同因）", "recheck": "部分解决", "seq": 6, "path_base": PB, "viewed_at": "2026-10-17T15:04:52+08:00"},
    {"id": "A10-v08", "parent": "A10-v07", "type": "visual", "image": "compositing-lab.png", "dsl": "compositing-lab.snapshot",
     "request_id": "187244d0-f3da-4e3b-885b-c1b2d8eb5e6e",
     "observable_issues": ["⑤ 标题缩短为『⑤ MULTIPLY → 子树模糊 σ6』（滤色值已由说明带第4行与 audit 记录承担）"],
     "changes": ["DESC[5][0] 缩短；复测 v8_row2desc 三列分离干净；整图终审（六格/说明/底注）+ 六采样点复核"],
     "comparison": "finalize：samples 6/6 通过（① 误差0；② 误差≤2 组量化容差内）；visual_checks 6 条归档", "recheck": "passed（定稿）", "seq": 7, "path_base": PB, "viewed_at": "2026-10-17T15:05:48+08:00"},
]
with open("tmp/%s/A10/iterations.jsonl" % R, "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("iterations", len(rows))
