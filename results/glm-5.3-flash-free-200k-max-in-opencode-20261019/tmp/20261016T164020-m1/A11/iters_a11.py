# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
R = "20261016T164020-m1"
rows = [
    {"id": "A11-s00", "type": "syntax-fix", "pages": ["invoice-page-01", "invoice-page-02"],
     "requests_failed": ["adfa507b-2343-4340-bcd1-09dbe1a680bc", "92e617d6-da74-4670-acf8-433e24733198"],
     "issue": "两页均 400 PARSE_ERROR（position 189，『<P\\no\\ns…』）：Python 中 S += text(...) 把函数返回的字符串逐字符拆入列表，join 后 DSL 每字符夹换行。",
     "fix": "text()/textraw() 改为返回 [node_str] 单元素列表；重跑构建后两页 200。", "viewed": False},
    {"id": "A11-s01", "parent": "A11-s00", "type": "baseline", "images": ["invoice-page-01.png", "invoice-page-02.png"],
     "request_ids": ["3ec3433a-6dd7-4083-b1d5-8dbc3936aa38", "0805c8bb-9f36-4883-bc17-0c022cf63549"],
     "viewed_at": "2026-10-17T15:32:20+08:00",
     "observable_issues": [
         "页1 表头『单价 UNIT』与『行金额 AMOUNT』双语标签右对齐后互相重叠（v2_p1_th 可见 U 行金额 相压）",
         "页2 PAID 富文本的 PAID 呈默认黑色——首个 Raw 未给 color（斜线灰/中文深两段已生效，证明 Raw 支持 color）",
         "强调条 y156 与标题字形底缘略贴",
         "安全边距违规：页眉 y=40<48、页脚文字底缘约 1574>1552（合规修复顺延至 v04）",
         "SKU 值 20px、逐字符核对 22px 按正文口径不足（顺延至 v05）"],
     "changes": ["两页整图 + 6 张放大件取证（v2_*）"], "seq": 2},
    {"id": "A11-v03", "parent": "A11-s01", "type": "visual", "images": ["invoice-page-01.png", "invoice-page-02.png"],
     "request_ids": ["a96fb117-eab1-4766-9a04-5c60c226b8b3", "aa94d492-f284-44cb-b00f-cc90572c4c00"],
     "viewed_at": "2026-10-17T15:37:40+08:00",
     "changes": ["表头列标签改中文（数量/单价/行金额），SKU 与 名称 NAME 保持双语", "PAID 首段 Raw 加 color=#157F3B", "强调条 y156→164（两页）"],
     "recheck": "v3_p1_th 三列分离干净；v3_p2_paid PAID 绿+斜线灰+中文深同基线；v3_p2_head 条距干净；v3_p1_sku A<B&C>D 逐字符精确；v3_p1_amt 两列小数点竖向对齐。遗留：安全边距与字号口径。", "seq": 3},
    {"id": "A11-v04", "parent": "A11-v03", "type": "requirement-change", "images": ["invoice-page-01.png", "invoice-page-02.png"],
     "request_ids": ["3ca987ea-eeca-4e72-997e-2471c24fa88a", "dccc1d25-da0e-4142-a726-b0086695e776"],
     "viewed_at": "2026-10-17T15:40:10+08:00",
     "changes": ["页眉 y40→48、分隔线 72→78；页脚分隔线 1524→1490、文字 1548→1512（底缘 1538 ≤1552）"],
     "recheck": "v04 两页整图通过；内容区与边距合规。遗留：SKU 20px / 核对行 22px 正文口径。", "seq": 4},
    {"id": "A11-v05", "parent": "A11-v04", "type": "requirement-change", "images": ["invoice-page-01.png", "invoice-page-02.png"],
     "request_ids": ["16f24fbe-674d-48ba-b18f-105852d8c0d2", "0b3ea11d-890c-494e-b428-dc246dc6d2c6"],
     "viewed_at": "2026-10-17T15:46:50+08:00",
     "changes": ["SKU 值与逐字符核对行 20/22→24px"],
     "recheck": "v5_p1_sku24 四行 SKU 24px 精确；v5_p2_checks 24px 清晰；v5_p1_head 页眉干净；两页整图终审通过。margin_audit [48,48,1152,1538] pass；size_audit body_pass True；8 项 checks 全过——定稿。", "seq": 5},
]
with open("tmp/%s/A11/iterations.jsonl" % R, "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("iterations", len(rows))
