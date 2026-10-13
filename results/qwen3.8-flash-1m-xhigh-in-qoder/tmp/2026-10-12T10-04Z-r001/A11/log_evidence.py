"""Write A11's image-view and iteration evidence logs from the actual render history."""
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "A11"
CST = timezone(timedelta(hours=8))


def ts(dt):
    return dt.astimezone(CST).isoformat(timespec="seconds")


def stamp(name):
    return ts(datetime.fromtimestamp((TMP / name).stat().st_mtime, CST))


NOW = ts(datetime.now(CST))

VIEWS = [
    ("v002", "v002-p1.png", "full",
     "整页 1：版面成立，但应付总额被右边缘裁成“4,215.”（38px 时 '.96' 需要 58px，"
     "而小数点 x=1140 已贴近 1152 安全边距）；“应付总额 / TOTAL DUE”与 x=348 的 CNY 标签重叠；"
     "A<B&C>D 原样显示正确"),
    ("v002", "v002-p2.png", "full",
     "整页 2：四条 literal_lines 的字符本身全部原样（双空格、尖括号、反斜杠、指令行都对），"
     "但我自己写的说明里含 & < > 的三段被 esc() 转成 &amp; &lt; &gt; 并原样显示出来——"
     "正是本题要考的那个失效模式；PAID / 已结算 三色共线正确"),
    ("v003", "v003-p1.png", "full",
     "整页 1：应付总额 4,215.96 完整可见并与合计列小数点对齐；CNY 移到标题下方不再重叠；"
     "所有金额落在 1152 边距内"),
    ("v003", "v003-p2.png", "full",
     "整页 2：实体名问题消失；但每条 literal 下的码点串太长（22–40 字符 × “U+XXXX ”）"
     "溢出到下一条与面板外，L4 的码点压住“保真核对”标题；账表“DSL 文本节点”格换行撞下一行"),
    ("v005", "v005-p1.png", "full",
     "整页 1：无裁切无重叠，四行 SKU、六个合计项、计算过程五条与脚注全部完整可读"),
    ("v005", "v005-p2.png", "full",
     "整页 2：说明、四条原样文字（含 26px 正文与 40px 放大样张）、保真核对表、PAID 样张、"
     "脚注各占其位；双空格在两处字号下都能直接看到"),
]

ZOOMS = [
    ("v005", "zoom-p2-l1.png",
     "第 2 页 L1 放大 3×：全角冒号后与 A 后各留两个空格位，A 与 0 之间同样空两格"),
    ("v005", "zoom-p2-l234.png",
     "第 2 页 L2–L4 放大 2×：A < B & C > D 的尖括号与 and 号、Path 的 4 个反斜杠、"
     "指令样式行全部按原字符出现，没有任何实体名"),
    ("v005", "zoom-p1-amounts.png",
     "第 1 页金额列放大 2×：单价列与行金额列的小数点上下成一条直线，"
     "4,124.30 / -180.00 / 3,944.30 / 236.66 / 35.00 / 4,215.96 同列对齐"),
    ("v005", "zoom-p1-paid.png",
     "第 1 页深蓝应付条放大 2×：白色 4,215.96 完整落在条内未被裁切，"
     "标题与“币种 CNY · 已四舍五入至分”两行不重叠"),
]

ITERS = [
    ("v001", None, "baseline", ["A11-render-v001-p1-a1", "A11-render-v001-p2-a1..a4"],
     "v001-p1.png",
     "第 1 页出图；第 2 页被服务拒绝：PARSE_ERROR Element [Raw] cant not buildWidget, "
     "it can only be used in the Text at position 4264。文档里 Raw 一节写的是"
     "“只能出现在由最外层 Text 创建的行内内容树中”，我按独立控件用了",
     "把 literal 行改成 <Text 段落属性><Raw><![CDATA[…]]></Raw></Text>，"
     "外层负责段落样式、内层负责不 trim；同步把审计与账表里的节点名改为 Text>Raw"),
    ("v002", "v001", "visual", ["A11-render-v002-p1-a1", "A11-render-v002-p2-a1..a4"],
     "v002-p1.png",
     "两页都出图。第 1 页应付总额被裁、CNY 与标题重叠；第 2 页 literal 字符保真成功，"
     "但我自己写的说明含 & < > 时被 esc() 转成可见实体名。用 PIL 在第 1 页量出等宽字体"
     "推进约 0.508em，据此算出 38px 的 '.96' 需要 58px，而 DOT_AMT=1140 只剩 12px",
     "写 patch1：DOT_AMT 1140→1086、应付字号 38→36、CNY 移到标题下方；"
     "literal 说明文案改写避免含 & < >，账表码点只写 U+XXXX；"
     "literal 条目槽位 88px、账表行距 36px、新增 40px 放大样张"),
    ("v003", "v002", "visual", ["A11-render-v003-p1-a1..a4", "A11-render-v003-p2-a1..a4"],
     "v003-p1.png",
     "第 1 页三处问题全部解决。第 2 页实体名消失，但每条 literal 下的逐字符码点串"
     "（最长 40 字符 → 280px 以上）溢出槽位，L4 的第二行压住“保真核对”标题；"
     "账表“Text 内嵌 Raw，CDATA 包裹”在 250px 格里换行撞进下一行",
     "写 patch2/patch3：删掉逐字符码点串，换成“N 字符 · 空格 M · 双空格 @i,j · 风险码点 …”"
     "一行；账表节点格改为 Text>Raw / CDATA；literal 槽位 88→96px；"
     "并加入 check() 重叠检测——它同时暴露出我最初用声明盒宽而非字形宽，"
     "把右对齐金额误报成重叠，改为按 CJK/ASCII 字宽估算字形范围后不再有真阳性"),
    ("v004", "v003", "syntax-fix", [], None,
     "只重写生成器与检测器（应付副标签下移 6px、深蓝条加高到 86px、"
     "第 2 页去掉与 L4 说明重复的一段注释以腾出放大样张的位置），未渲染",
     "工具/排版修正，不计入完整视觉迭代"),
    ("v005", "v004", "final", ["A11-render-v005-p1-a1", "A11-render-v005-p2-a1"],
     "v005-p1.png",
     "两页一次出图。check() 无重叠报告；verify.py 实测：单价列/行金额列/合计列/应付条"
     "句号左缘 x 极差均为 0px；墨迹范围 x∈[48,1151] y∈[62,1441]，未越 48px 安全边距；"
     "两页 DSL 里 &lt; &gt; &amp; &# 计数全为 0；L1 按 13px 半角推进建模时 A/0/7 误差 ≤2px，"
     "若空格被合并误差为 14–15px",
     "定稿：复制为 outputs/<run>/A11/invoice-page-0{1,2}.png 与同名 .snapshot"),
]

views = []
n = 0
for ver, img, kind, note in VIEWS + [(v, i, "zoom", z) for v, i, z in ZOOMS]:
    n += 1
    views.append({"view_id": f"A11-view-{n:02d}", "task_id": "A11", "dsl_version": ver,
                  "image": f"tmp/{RUN}/A11/{img}", "kind": kind, "note": note,
                  "tool": "Read (multimodal image view)"
                          + (" + PIL crop/resize" if kind == "zoom" else "")
                          + (" + numpy column scan" if kind == "full" else ""),
                  "image_written_at": stamp(img), "logged_at": NOW,
                  "path_base": "suite_root"})
# v001 page 1 was rendered but its content is byte-identical to v002 page 1, so the
# v002-p1 view above covers it; recorded explicitly rather than back-dating a view.
views.append({"view_id": f"A11-view-{n + 1:02d}", "task_id": "A11", "dsl_version": "v001",
              "image": f"tmp/{RUN}/A11/v001-p1.png", "kind": "full",
              "note": "v001 第 1 页 DSL 与 v002 第 1 页逐字节相同（19974 bytes，同一响应 "
                      "305430 bytes），其版面问题在 v002-p1 的整图查看中一并记录，"
                      "不另计一次独立看图",
              "tool": "Read (multimodal image view)",
              "image_written_at": stamp("v001-p1.png"), "logged_at": NOW,
              "path_base": "suite_root"})

iters = []
for ver, parent, typ, reqs, img, observed, change in ITERS:
    iters.append({"version": ver, "parent": parent, "type": typ, "renders": reqs,
                  "image": f"tmp/{RUN}/A11/{img}" if img else None,
                  "viewed": bool(img), "observed": observed, "change": change,
                  "ts": NOW, "path_base": "suite_root"})

(TMP / "image-views.jsonl").write_text(
    "\n".join(json.dumps(v, ensure_ascii=False) for v in views) + "\n", encoding="utf-8")
(TMP / "iterations.jsonl").write_text(
    "\n".join(json.dumps(v, ensure_ascii=False) for v in iters) + "\n", encoding="utf-8")
print("views", len(views), "iterations", len(iters))
