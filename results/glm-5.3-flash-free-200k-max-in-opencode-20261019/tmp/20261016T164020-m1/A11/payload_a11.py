# -*- coding: utf-8 -*-
import io, sys, json, pathlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
pay = {"artifacts": ["invoice-page-01.png", "invoice-page-01.snapshot", "invoice-page-02.png", "invoice-page-02.snapshot",
                     "invoice-audit.json", "text-map.json", "snapshot-usage.md", "task-metrics.json"],
       "evidence": ["两页 v05 整图终审 + 9 张放大件（表头/行/金额列/字样块/PAID/页眉/核对行）",
                    "margin_audit [48,48,1152,1538] pass；size_audit body≥24 / footnote≥20 pass；8 项 checks 全过",
                    "A<B&C>D 与四条 literal_lines 经 Raw+CDATA 逐字符保真（双空格×2、反斜杠×3、尖括号与 & 无实体）",
                    "计税链完整：4124.30−180.00=3944.30 → ×0.06 HALF_UP 236.66 → +35.00 = 4215.96（脚本断言）；renders 10（ok8/fail2 语法修复）"],
       "summary": "A11 完成（v05）：1200×1600 跨页结算单——页1 主档（双方/元信息芯片/四行 SKU 含 CDATA 保真/小数点对齐金额/六项结算至应付 4215.96），页2 说明+原样字样+PAID 绿灰深共基线+逐字符核对。"}
pathlib.Path("tmp/20261016T164020-m1/A11/complete-payload.json").write_text(
    json.dumps(pay, ensure_ascii=False, indent=1), encoding="utf-8")
print("payload ok")
