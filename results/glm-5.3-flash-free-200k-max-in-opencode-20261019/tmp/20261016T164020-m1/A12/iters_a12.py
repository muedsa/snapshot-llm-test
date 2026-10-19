# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
R = "20261016T164020-m1"
rows = [
    {"id": "A12-s01", "type": "baseline", "images": ["mobile.png", "tablet.png", "desktop.png", "stage.png"],
     "request_ids": ["41b19711-ece3-4bee-a5c7-e32cfe479013", "4954ab38-50ec-45a5-a511-a6a0d08f4398",
                     "18ed917f-6862-440f-a1db-d9cd5ffbc6fb", "2dc83b75-bed5-4aa9-adf6-3007c45d953d"],
     "viewed_at": "2026-10-17T15:52:20+08:00",
     "observable_issues": [
         "平板卡网格底 859，画布底留白约 165px（下方偏空）",
         "桌面/大屏卡内标题偏上（0.26×卡高），视觉重心不稳",
         "手机卡6 detail 距卡底边约 2px（偏紧，未越界）"],
     "note": "生成器一份 tokens 出四 DSL：初版 chip/cta 内距 1px 拟合与手机纵向 68px 超框已在构建期修掉（WARN 0 后才发起渲染，无失败请求）。",
     "changes": ["四张整图逐张查看 + 手机 4 张放大件（v2_*）"], "seq": 1},
    {"id": "A12-v02", "parent": "A12-s01", "type": "visual", "images": ["mobile.png", "tablet.png", "desktop.png", "stage.png"],
     "request_ids": ["55afc102-6cf3-4e73-8b27-031cb3badc27", "7464d695-30b2-414a-b16e-c3167a8c9fc8",
                     "e8ef1b08-a6be-427b-a144-79917b4c79d2", "be9fee09-9afb-494d-9e14-ebd4e78e2f6e"],
     "viewed_at": "2026-10-17T15:57:40+08:00",
     "changes": [
         "平板：grid 下移（card_top 1.2→2.4 meta倍），卡高 148→168，网格底 943 ≤ 992",
         "桌面/大屏：卡内文字块下移居中（标题基准 0.26→0.32×卡高）",
         "手机：卡高 62→64、网格底 766 ≤ 784，detail 底距 ~5px"],
     "recheck": "四张 v02 整图终审：全部必显文案逐字符完整（对比 fields 源文本一致）；组件词汇/调色板/层级四画布一致；放大件 v2_desktop_card、v2_stage_card、v2_mobile_ctaweb、v2_mobile_card6 通过。textbox_overlap_audit 全 pass——定稿。",
     "seq": 2},
]
with open("tmp/%s/A12/iterations.jsonl" % R, "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("iterations", len(rows))
