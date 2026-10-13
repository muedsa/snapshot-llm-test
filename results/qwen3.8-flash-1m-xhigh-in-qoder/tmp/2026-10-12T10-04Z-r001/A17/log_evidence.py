"""Append the A17 visual-review records and iteration records actually made."""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RUN_DIR = Path(__file__).resolve().parents[1]
ROOT = RUN_DIR.parents[1]
sys.path.insert(0, str(RUN_DIR / "_suite" / "scripts"))
LOG = ROOT / "tmp" / RUN_DIR.name / "A17"


def rec(fname, obj):
    obj.setdefault("ts", datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"))
    obj.setdefault("path_base", "suite_root")
    with (LOG / fname).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


VIEWS = [
    ("A17-view-01", "v001", "tmp/<run>/A17/v001-example-01.png", "full",
     "400×240 独立示例首版：左卡 POST /snapshot 的墨迹压住中间蓝色箭头；右卡 200 + image/png 与 图片字节，不是 JSON 越过卡片右边并被画布裁掉；底部一行超出 400px 边界"),
    ("A17-view-02", "v002", "tmp/<run>/A17/v002-example-01.png", "full",
     "改为按测量摆放后：两卡各 158×78，箭头 24×8 居中在 182..206，四段文字均在卡内，底部两行在 24px 安全边距内"),
    ("A17-view-03", "v002", "tmp/<run>/A17/v002-example-03.png", "full",
     "两块 96px 方块带 alpha 80 重叠处更深；末行 <Row> 与 & 原样出现，绿/橙两字与前后文字同基线，Raw 的空格未被 trim"),
    ("A17-view-04", "v002", "tmp/<run>/A17/v002-example-04.png", "full",
     "左卡条纹糊成色带且 BackdropFilter 字样锐利；右卡连 ImageFiltered 字样与描边一起糊；底部说明仍压在彩色条纹上，可读性偏弱"),
    ("A17-view-05", "v002", "tmp/<run>/A17/v002-example-02.png", "full",
     "标题与紫色条正常，但 y=96 处 flex 1:2:1 三条色块完全不可见——Row 只有宽度约束、交叉轴无界时 STRETCH 子容器高度塌成 0"),
    ("A17-view-06", "v003", "tmp/<run>/A17/v003-example-02.png", "full",
     "补上 height=40 并改 crossAxisAlignment=START 后三条色块出现；随后用 numpy 量得 x=24..105/118..281/294..375，宽 82/164/82 正是 1:2:1，紫条 352 宽"),
    ("A17-view-07", "v003", "tmp/<run>/A17/v003-handbook-01.png", "full",
     "第 1 页整体成立：页眉卡、示例插图与要点两栏、代码面板、两栏核对、页脚互不遮挡；代码缩进在 CDATA 中保留"),
    ("A17-view-08", "v003", "tmp/<run>/A17/v003-handbook-02.png", "full",
     "第 2 页插图与要点一致；代码面板 15 行未溢出"),
    ("A17-view-09", "v003", "tmp/<run>/A17/v003-handbook-03.png", "full",
     "缺陷：正文里我写的 &lt; 被显示成 &amp;lt;，&amp; 被显示成 &amp;amp;amp;——正是本页要讲的“解析器不解码实体”，说明 txt() 走了 esc() 而不是 CDATA"),
    ("A17-view-10", "v003", "tmp/<run>/A17/v003-handbook-04.png", "full",
     "第 4 页版式成立；插图底部说明与彩色条纹重叠，需要修"),
    ("A17-view-11", "v004", "tmp/<run>/A17/v004-handbook-03.png", "full",
     "改为含 & < > 的正文一律走 Raw/CDATA 后：写 &lt; 就原样印出这 4 个字符、用 &amp; 转义 &、含 < > & 的文字三处均按字面显示；页码区间显示为 39 而不是 39–39"),
    ("A17-view-12", "v006", "tmp/<run>/A17/v006-handbook-01.png", "full",
     "印刷片段改为直接引用 example-NN.snapshot 的 1-based 行（含 Snapshot 根与 400×240 容器），页面上多出的两级缩进与文件一致"),
    ("A17-view-13", "v006", "tmp/<run>/A17/v006-handbook-03.png", "zoom",
     "1.5× 放大代码面板：缩进保留、……省略外层包装……独立成行、<Raw><![CDATA[<Row> 与 & 保持原样]]></Raw> 原样印出（含 ]]>)"),
    ("A17-view-14", "v006", "tmp/<run>/A17/v006-handbook-04.png", "zoom",
     "1.6× 放大插图：左卡字清楚、右卡连字一起糊；但“裁剪决定效果停在哪里”仍叠在彩色条纹上"),
    ("A17-view-15", "v007", "tmp/<run>/A17/v007-example-04.png", "full",
     "条纹高度改为 172 后，示例底部说明落在白底上，清晰可读"),
    ("A17-view-16", "v007", "tmp/<run>/A17/v007-example-01.png", "full",
     "确认加白底后示例外观不变（原本就画在白卡上）"),
    ("A17-view-17", "v007", "tmp/<run>/A17/v007-example-02.png", "full",
     "flex 1:2:1 与 Spacer 两端对齐均正确"),
    ("A17-view-18", "v007", "tmp/<run>/A17/v007-example-03.png", "full",
     "alpha 叠加、CDATA 与行内 Span 基线正确"),
    ("A17-view-19", "v007", "tmp/<run>/A17/v007-handbook-01.png", "full",
     "第 1 页最终态：插图与独立示例逐像素一致（verify 0.9999+），片段 12 行"),
    ("A17-view-20", "v007", "tmp/<run>/A17/v007-handbook-02.png", "full",
     "第 2 页最终态：片段 15 行含 Expanded/Spacer 结构"),
    ("A17-view-21", "v007", "tmp/<run>/A17/v007-handbook-03.png", "full",
     "第 3 页最终态：片段 14 行，实体与 CDATA 文案按字面显示"),
    ("A17-view-22", "v007", "tmp/<run>/A17/v007-handbook-04.png", "full",
     "第 4 页最终态：插图说明改到白底；代码面板中 109 字符的卡容器一行按真实软换行显示为两行，面板高度已按同一模型预留"),
]

for vid, ver, img, kind, note in VIEWS:
    rec("image-views.jsonl", {"view_id": vid, "task_id": "A17", "dsl_version": ver,
                              "image": img.replace("<run>", RUN_DIR.name),
                              "kind": kind, "note": note,
                              "tool": "Read (multimodal image view)"})

ITERS = [
# v001 baseline and v002 visual were appended while the work was in progress
    ("v003", "v002", "visual",
     ["tmp/<run>/A17/v003-handbook-03.png", "tmp/<run>/A17/v003-handbook-01.png"],
     "手册正文里的 &lt; / &amp; 被 esc() 二次转义，页面显示成 &amp;lt;；单行区间印成 39–39",
     "txt() 对含 & < > 的文案改用 Raw/CDATA 分块；区间单行时只显示一个行号",
     "v004-handbook-03 看图确认三处实体文案按字面显示"),
    ("v004", "v003", "visual",
     ["tmp/<run>/A17/v004-handbook-04.png"],
     "第 4 页插图与独立示例在 BackdropFilter 卡内差 0.956（max 21）；probe-backdrop a/b/c 证明同一棵子树换外层包装/画布就会不同",
     "独立示例改为 background=#FFFFFF（与页内白卡一致），并把该差异限定在滤镜区域内、量化记录",
     "v005/v006 verify：三页 >0.995 完全一致，第 4 页差异全部落在滤镜矩形内且 ≤21"),
    ("v005", "v004", "syntax-fix",
     ["tmp/<run>/A17/v005-handbook-04.png"],
     "verify.py 取正文时把 DSL 自身缩进当成内容；印刷片段行号按 core 相对行统计，与交付文件的 1-based 行号不一致",
     "code_text 改为直接给出 example-NN.snapshot 的行；RANGES 换成文件行号；提取时只取面板墨色 Text 的 Raw 拼接",
     "v006 verify：printed-snippet-verbatim 四页通过"),
    ("v006", "v005", "visual",
     ["tmp/<run>/A17/v006-handbook-04.png"],
     "wrap_rows 把空格丢掉，109 字符的源码行被算成一行；插图底部说明压在彩色条纹上",
     "measure.wrap_rows 计入空格；示例条纹高度 240→172；面板内边距 20→14、段间距 14→12",
     "v007：四页 bottom 1435/1481/1481/1489 ≤ 1498，verify 全绿"),
    ("v007", "v006", "visual",
     ["tmp/<run>/A17/v007-handbook-01.png", "tmp/<run>/A17/v007-handbook-02.png",
      "tmp/<run>/A17/v007-handbook-03.png", "tmp/<run>/A17/v007-handbook-04.png",
      "tmp/<run>/A17/v007-example-01.png", "tmp/<run>/A17/v007-example-02.png",
      "tmp/<run>/A17/v007-example-03.png", "tmp/<run>/A17/v007-example-04.png"],
     "最终八件全部实际看图：内容、层级、可读性、裁剪与效果均达标；已知残余：第 4 页代码面板中一行 109 字符按软换行显示为两行（与文件内容一致，非缺陷）",
     "无进一步修改；定为交付版本",
     "verify --ver v007：ALL PASSED True"),
]

for ver, parent, typ, arts, obs, chg, recheck in ITERS:
    rec("iterations.jsonl", {"version": ver, "parent": parent, "type": typ,
                             "artifacts": [a.replace("<run>", RUN_DIR.name) for a in arts],
                             "observed": obs, "change": chg, "recheck": recheck})
print("appended", len(VIEWS), "views and", len(ITERS), "iterations")
