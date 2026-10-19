# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
R = "20261016T164020-m1"
rows = [
    {"id": "A13-p00", "type": "alternative", "images": [None, None],
     "request_ids": ["84a5a9b4-8a61-4d1d-81f9-1eeac5bf3ad2", "40351764-7505-4bac-bb33-5ab8e418cbfc"],
     "subject": "方向预览（仅临时目录）：dir-a 叠层方片 / dir-b 光棱山形（各 512×512 透明）",
     "viewed_at": "2026-10-17T16:03:10+08:00",
     "observable_issues": ["dir-a 顶层圆孔对比弱（45% 顶片 vs 72% 中片，孔内外差小）",
                            "dir-b 双三角 32px 将融并、隐喻偏景观"],
     "decision": "选 dir-a：语义直指『叠』且小尺寸轮廓/负空间更强；改进进入终版" +
                 "（顶层 α→81%、孔 r30→36）", "seq": 1},
    {"id": "A13-v01", "parent": "A13-p00", "type": "baseline", "images": ["symbol-color.png"],
     "request_ids": ["00026c6d-571c-4ac2-942a-7d6a48c5a185", "c05fcf89-ea36-4806-83ca-6c74a19b77f3",
                     "f324b471-a48d-4969-b953-90f0355c2d4c", "7ae12e1c-669b-4577-a6ef-24c6cea2b793"],
     "viewed_at": "2026-10-17T16:07:30+08:00",
     "observable_issues": ["symbol-color 光孔位置错误：孔心误用画布坐标 (220,220) 而非顶层片局部 (110,110)，孔跑到片右下角成月牙伪影（其余三层正确）"],
     "note": "banner/poster 尚未查看（已知含同 bug，直接并入 v02 重渲）", "seq": 2},
    {"id": "A13-v02", "parent": "A13-v01", "type": "visual", "images": ["symbol-color.png", "symbol-black.png", "brand-banner.png", "launch-poster.png"],
     "request_ids": ["1fa6418a-ba95-46b0-b1b3-af9b27875973", "f637d32d-5270-450f-9d04-8c7dbf612a7f",
                     "8764f4a2-a871-49fd-9825-c46a580251f4", "d0d384e5-163f-45dd-b4f7-42160751d9cd"],
     "viewed_at": "2026-10-17T16:09:40+08:00",
     "changes": ["mark() 孔心改局部坐标——四应用同规则修复", "彩版/黑版/横幅/大屏重渲"],
     "recheck": "彩版孔洞聚焦点清晰；黑版三层 alpha 可辨、轮廓同构（64 格对称差 0）;横幅字标基线对齐 ✓；大屏发现新缺陷：叠光(104)与 Layerlight(68) 同轴居中互相压叠",
     "observable_issues": ["launch-poster 标题两行同轴碰撞"], "seq": 3},
    {"id": "A13-v03", "parent": "A13-v02", "type": "visual", "images": ["launch-poster.png"],
     "request_ids": ["1f33daa1-34aa-4acb-b1bb-ade3fa370b9d"],
     "viewed_at": "2026-10-17T16:13:20+08:00",
     "changes": ["大屏标题改纵向双行（叠光 104 居中 / Layerlight 56 居中），后段节奏下移（标语 726/分隔 790/日期条 822）"],
     "recheck": "大屏终审通过；横幅 lockup 与大屏 mark 放大件核验同规则缩放；32×32 预乘预览（彩/黑）实际尺寸查看通过，黑版纯黑审计 0 违例、alpha 区间 [1,255]，几何匹配 0 差异——四件定稿", "seq": 4},
]
with open("tmp/%s/A13/iterations.jsonl" % R, "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("iterations", len(rows))
