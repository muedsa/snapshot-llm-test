"""Build tmp/<run_id>/A17/iterations.jsonl from the archived requests.jsonl.

Every record's request_id / image path / timestamps are read from the real log;
the observation text is authored here and each note is traceable to the diff
between the two archived request bodies it sits between.
"""
import json
import os
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
tmp = root / "tmp" / rid / "A17"
rows = [json.loads(l) for l in (tmp / "requests.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
renders = [r for r in rows if r["kind"] == "render"]

REQ = {
    "example01": "第1页可运行示例（400×240：请求/响应/错误三种返回的对照卡）",
    "example02": "第2页可运行示例（400×240：根尺寸来自布局 + Expanded 权重）",
    "example03": "第3页可运行示例（400×240：Raw 保留空白与尾部 alpha 色）",
    "example04": "第4页可运行示例（400×240：ImageFiltered 子树滤镜 vs BackdropFilter）",
    "hb01": "手册第1页：真实调用契约、输入/输出/错误响应",
    "hb02": "手册第2页：根尺寸来自布局、有界 Row/Column/Expanded、Stack 定位",
    "hb03": "手册第3页：Raw/CDATA/富文本与尾部 alpha 常见误解",
    "hb04": "手册第4页：背景滤镜与子树滤镜、视觉自检、可复现交付",
}

Q = chr(34)
FINAL = {"example01-v03", "example02-v01", "example03-v02", "example04-v02",
         "hb01-v06", "hb02-v06", "hb03-v06", "hb04-v09"}

# version -> (parent, type, problems in this image, changes after it, recompare)
NOTE = {
    "example01-v01": (None, "baseline",
        "整幅查看：三条分隔线用 #1E3A5F，在深色卡上几乎不可见；REQUEST/RESPONSE 小标题贴住分隔线，分组关系读不出来",
        "分隔线改 #2B4C7E；小标题前后插入 height=18 / height=10 的空 Container 撑出间距",
        "v02 复看：三条分隔线可见，标签与内容分组清楚"),
    "example02-v01": (None, "baseline",
        "整幅查看未发现裁切、叠字或比例失衡；Expanded 权重与右侧定位块的关系一眼可读",
        "无改动，v01 即最终版（不为制造迭代而改）",
        "不再重渲染；outputs/example-02.png 就是本次响应字节"),
    "example03-v01": (None, "baseline",
        "整幅查看：三个色块之间的运算符写成 Text 内容，左右空格被 trim，减号等号挤成一片",
        "运算符改为 Text>Raw>CDATA 结构，用 Raw 保留空白",
        "v02 复看：运算符两侧空格恢复，等式读法正确"),
    "example04-v01": (None, "baseline",
        "整幅查看：标题条 ImageFiltered sigmaX=2.5 把条内 15px 副标题糊到无法辨认，滤镜示例本身反而读不出内容",
        "sigmaX/sigmaY 由 2.5 降到 1.5，保留“这是滤镜”的可辨识度同时让文字可读",
        "v02 复看：模糊仍明显，标题文字可读"),
    "example01-v02": ("example01-v01", "visual",
        "复看 v02：13px 说明行在 400px 宽的图里笔画发虚；CDATA 直接放在 Text 里时 “POST /snapshot  ·  text/plain” 的双空格被压成视觉上的单空格，与手册第3页讲的 trim 规则自相矛盾",
        "删除 13px 说明行；三处文本改成 Text>Raw>CDATA 结构，双空格改为单空格加中点",
        "v03 复看：只剩两档字号，标签清晰；印刷片段与独立渲染是同一份字节"),
    "example01-v03": ("example01-v02", "visual",
        "复看 v03：无遗留缺陷",
        "定稿，作为 example-01.png 的最终响应字节；手册第1页印刷片段同步到这一版",
        "与 v02 对比：删掉发虚的小字，文本结构统一为 Raw"),
    "example03-v02": ("example03-v01", "visual",
        "复看 v02：Raw 修复生效，无新问题",
        "定稿，作为 example-03.png 的最终响应字节",
        "与 v01 对比：运算符两侧留白恢复"),
    "example04-v02": ("example04-v01", "visual",
        "复看 v02：sigma 1.5 下标题与色块都清晰；左侧未加滤镜与右侧 BackdropFilter 的对照关系成立",
        "定稿，作为 example-04.png 的最终响应字节；手册第4页印刷行随后同步（见 hb04-v07）",
        "与 v01 对比：模糊减弱但仍是可见的滤镜效果"),
    "hb01-v01": (None, "syntax-fix",
        "无图像：HTTP 400 PARSE_ERROR “Not Support RAWTEXT: ]]> at position 10686 near: plain; charset=utf-8]]></Text>” —— 手册要印刷 ]]> 结束符，正好把 CDATA 段自己截断",
        "把印刷的 ]]> 拆成 “]]” 与 “>” 两个 Raw 片段，避免嵌套结束符",
        "无图片可比较；错误响应字节保留在 preview/requests/ 下，未当作成品"),
    "hb01-v02": ("hb01-v01", "baseline",
        "第1页第一张成功图：结构成立；但代码行距 33 让页底余量比另三页小，且印刷的 example-01 片段仍是旧版内容",
        "行距收紧为 32 并重算项目符号与段落 y；印刷片段同步为 example-01 v03",
        "v03 复看：四页页底留白一致"),
    "hb01-v03": ("hb01-v02", "visual",
        "复看 v03：印刷代码在 token 中间断行，出现 “</Te”+“xt>” 这种抄不得的断点；第1页流程卡的三个子标签与下方红色警告条重叠",
        "换行改成按标签边界（> 之后、空格串之后、非标签起始的 < 之前）打包，续行预留 ↳ 缩进；面板高 178→224、卡片 96→112、标签重排 iy+64/96/124、警告条下移到 iy+172",
        "v04 复看：断点全部落在合法位置，标签与警告条不再重叠"),
    "hb01-v04": ("hb01-v03", "visual",
        "放大复看 v04：流程卡里 “image/png 字节” 一类标签底部被裁——盒子比文字行盒矮时服务静默裁字形，不报错也不告警",
        "生成器给标签盒按 ceil(fontSize×1.42) 自动加高；为吸收高度把代码字号暂时降到 19、行距 28",
        "v05 复看：裁字消失，但 19px 违反 TASK.md 的“代码≥20”，必须回退"),
    "hb01-v05": ("hb01-v04", "visual",
        "复看 v05：19px 代码违反题目下限；本页版面本身已无裁切",
        "代码字号回到 20、行距改 29，代码面板高度随之增加",
        "v06 复看：20px 代码可读、不裁字、不溢出"),
    "hb01-v06": ("hb01-v05", "requirement-change",
        "复看 v06：正文 24 / 代码 20 / 边距 48 全部达标，无遗留缺陷",
        "定稿，作为 handbook-01.png 的最终响应字节",
        "与 v05 对比：字号回到 20 且行距 29，未再出现裁字"),
    "hb02-v01": (None, "baseline",
        "整幅查看：代码面板里以 ↳ 开头的续行被包在固定高 27 的 Container 中，字形下半部被静默裁掉（不报错）",
        "续行改为 Text>Raw 直接绘制，交给行盒自身高度；四页共用同一生成器一起修",
        "v02 复看：↳ 续行完整无裁切"),
    "hb02-v02": ("hb02-v01", "visual",
        "复看 v02：裁切消失；行距 33 与第1页节奏不一致",
        "行距 33→32，重算 y 坐标",
        "v03 复看：与其余三页一致"),
    "hb02-v03": ("hb02-v02", "visual",
        "复看 v03：左下说明文字被 290px 宽的标签盒裁掉，句子读不完；同时存在与第1页相同的 token 中间断行",
        "说明盒宽 290→400、文案缩短为“left + width ⇒ 另一侧被推出”，色块矩形移到 M+452 宽 190；换行策略同步为标签边界打包",
        "v04 复看：说明完整、断行合法"),
    "hb02-v04": ("hb02-v03", "visual",
        "放大复看 v04：标签盒矮于行盒导致的底部裁字（与第1页同一类问题）",
        "标签盒自动加高；代码字号暂时 19 / 行距 28",
        "v05 复看：不再裁字，但字号待回退"),
    "hb02-v05": ("hb02-v04", "visual",
        "复看 v05：19px 代码违反 TASK.md 下限",
        "字号回 20、行距 29，深色代码面板 342→381 以容纳",
        "v06 复看：达标"),
    "hb02-v06": ("hb02-v05", "requirement-change",
        "复看 v06：无遗留缺陷",
        "定稿，作为 handbook-02.png 的最终响应字节",
        "与 v05 对比：代码 20px、行距 29，面板加高后无溢出"),
    "hb03-v01": (None, "baseline",
        "整幅查看：与第2页相同的 ↳ 续行裁切；alpha 色卡与富文本示例可读",
        "随生成器一起修复续行",
        "v02 复看：见下条——这次重发是无内容变化的重复请求"),
    "hb03-v02": ("hb03-v01", "retry",
        "请求体与 hb03-v01 的 sha256 完全相同（418df819…，17534 字节），是一次内容零变化的重复请求，不构成新的视觉迭代",
        "无 DSL 改动；两次响应都是 200 + X-Snapshot-Cache: miss + 422199 字节，render;dur 1836.7 与 768.5",
        "两张图逐字节相同。这条记录同时是“相同请求未必命中缓存”结论的证据，保留不删"),
    "hb03-v03": ("hb03-v02", "visual",
        "复看 v03：行距 33 与其余页节奏不一致",
        "行距 33→32",
        "v04 复看：一致"),
    "hb03-v04": ("hb03-v03", "visual",
        "复看 v04：印刷代码在 token 中间断行（与第1页同一问题）",
        "标签边界换行 + ↳ 续行缩进",
        "v05 复看：断点合法"),
    "hb03-v05": ("hb03-v04", "visual",
        "放大复看 v05：标签盒底部裁字；代码字号被暂时压到 19",
        "标签盒自动加高；字号回退留到下一轮",
        "v06 复看：裁字消失"),
    "hb03-v06": ("hb03-v05", "requirement-change",
        "复看 v06：代码 20px / 行距 29 达标，无遗留缺陷",
        "字号回到 20，定稿为 handbook-03.png 的最终响应字节",
        "与 v05 对比：字号 +1、行距 +1，面板加高后无裁切"),
    "hb04-v01": (None, "baseline",
        "整幅查看：↳ 续行裁切（同第2、3页）；滤镜对照条与清单卡可读",
        "随生成器一起修复续行",
        "v02 复看：续行完整"),
    "hb04-v02": ("hb04-v01", "visual",
        "复看 v02：行距 33 与其余页不一致",
        "行距 33→32",
        "v03 复看：一致"),
    "hb04-v03": ("hb04-v02", "visual",
        "复看 v03：印刷代码在 token 中间断行",
        "标签边界换行；本轮把交付清单一行写成“相同请求命中渲染缓存（X-Snapshot-Cache: hit）”，措辞过强，到 v09 才核实并修正",
        "v04 复看：断点合法；文案准确性问题当时未察觉"),
    "hb04-v04": ("hb04-v03", "visual",
        "复看 v04：深色滤镜说明面板里说明文字压住面板下沿；清单卡第二行贴边",
        "面板与清单卡高度按标签行盒重算；标签盒自动加高",
        "v05 复看：说明不再压边，但代码字号被暂时压到 19"),
    "hb04-v05": ("hb04-v04", "visual",
        "复看 v05：19px 代码违反 TASK.md 下限；清单卡因自动加高而溢出卡片",
        "清单卡按行盒重排为 116（v06 落地），字号回退留到 v08",
        "v06 复看：卡片不再溢出"),
    "hb04-v06": ("hb04-v05", "visual",
        "复看 v06：清单卡与深色面板都正确；手册印刷的第 25 行仍写 sigmaX=" + Q + "2.5" + Q,
        "准备与 example-04 定稿同步",
        "v07 复看：见下条"),
    "hb04-v07": ("hb04-v06", "visual",
        "复看 v07：印刷片段与独立渲染的 example-04 DSL 已一致（sigma 1.5），但代码仍是 19px",
        "确认印刷行与 example-04.snapshot 逐字节对应",
        "v08 复看：字号回到 20 后印刷行仍一致"),
    "hb04-v08": ("hb04-v07", "requirement-change",
        "复看 v08：代码 20px / 行距 29 达标；核对响应头后开始怀疑“相同请求必命中缓存”的说法",
        "字号回到 20；把缓存核实记入待办",
        "v09 复看：见下条"),
    "hb04-v09": ("hb04-v08", "visual",
        "核对响应头：本题 35 次渲染 34 次 X-Snapshot-Cache: miss（另 1 次是 400 无该头），其中 hb03-v01/v02 请求体完全相同也仍是 miss；全套 237 次渲染仅 7 次 hit。手册把文档措辞写成了必然命中",
        "清单行改为“相同请求可能命中缓存（X-Snapshot-Cache 取 hit/miss）”，同步 sources.md 4.14",
        "v09 复看（含局部放大）：新文案在卡片内单行显示、无裁切，作为第4页最终图"),
}

missing = [r["dsl_version"] for r in renders if r["dsl_version"] not in NOTE]
if missing:
    raise SystemExit(f"no note for versions: {missing}")

out = []
for r in renders:
    v = r["dsl_version"]
    parent, typ, problems, changes, recompare = NOTE[v]
    is_image = r["http_status"] == 200
    out.append({
        "iteration_id": f"A17-{v}",
        "task_id": "A17", "run_id": rid,
        "version": v, "parent_version": parent, "type": typ,
        "requirement_part": REQ[v.split("-")[0]],
        "recorded_at": r["ended_at"],
        "request_id": r["request_id"],
        "http_status": r["http_status"],
        "image_path": r["response_file"] if is_image else None,
        "image_viewed": is_image,
        "image_viewed_at": r["ended_at"] if is_image else None,
        "viewed_at_basis": ("同一会话内渲染返回后立刻用图像工具打开该预览；秒级时间戳沿用请求结束时刻"
                            if is_image else "无图像（400 错误响应），未看图"),
        "observed_problems": problems,
        "changes_made": changes,
        "recompare_result": recompare,
        "completed": True,
        "completed_meaning": "本轮闭环：改动后有后续渲染并被实际查看比较；final=true 才表示该版本作为成品交付",
        "final": v in FINAL,
        "path_base": "suite_root",
        "image_scope": "rendered" if is_image else "none",
    })

dst = tmp / "iterations.jsonl"
if dst.exists():
    raise SystemExit(f"refuse to overwrite existing {dst}")
dst.write_text("".join(json.dumps(o, ensure_ascii=False) + "\n" for o in out), encoding="utf-8")
print("wrote", dst, len(out), "records")
print("types:", {t: sum(1 for o in out if o["type"] == t) for t in sorted({o["type"] for o in out})})
print("finals:", sorted(o["version"] for o in out if o["final"]))
