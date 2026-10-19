# -*- coding: utf-8 -*-
import io, sys, json, pathlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
pay = {"artifacts": ["mobile.png", "mobile.snapshot", "tablet.png", "tablet.snapshot",
                     "desktop.png", "desktop.snapshot", "stage.png", "stage.snapshot",
                     "design-tokens.json", "content-map.json", "snapshot-usage.md", "task-metrics.json"],
       "evidence": ["四画布 v02 整图终审 + 4 张关键放大件（桌面/大屏卡、手机 CTA/卡6）",
                    "content-map 76 条必显记录逐字符 complete；card_index C1–C6 逐画布映射",
                    "textbox_overlap_audit 四画布全 pass；字号/边距合规（手机16/卡题18；其余20/40/边距32+）",
                    "renders 8 全 200（无失败）；迭代 2（平板留白/卡内重心/手机底距）"],
       "summary": "A12 完成（v02）：一份 tokens 生成四断点完整 DSL——手机单列/平板2×3/桌面与大屏3×2，组件与层级统一，必显文案与6卡 title+detail 一字不丢。"}
pathlib.Path("tmp/20261016T164020-m1/A12/complete-payload.json").write_text(
    json.dumps(pay, ensure_ascii=False, indent=1), encoding="utf-8")
print("payload ok")
