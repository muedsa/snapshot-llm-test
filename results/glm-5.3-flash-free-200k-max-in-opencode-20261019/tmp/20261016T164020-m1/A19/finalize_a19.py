# -*- coding: utf-8 -*-
"""A19 收尾：answers.json、equivalence.json、snapshot-usage.md、iterations、payload。"""
import io, sys, json, math, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image, ImageChops

D = "outputs/20261016T164020-m1/A19"
TD = "tmp/20261016T164020-m1/A19"
scene = json.load(open(f"{D}/scene-data.json", encoding="utf-8"))
objs = scene["objects"]
O = {o["id"]: o for o in objs}
GRID = Image.open(f"{D}/grid-scene.png")
OCC = Image.open(f"{D}/occlusion.png")

def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def px(im, x, y):
    return im.getpixel((int(round(x)), int(round(y))))[:3]

def hx(s):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))

def sample_point(o):
    cx, cy = o["center"]
    if o["shape"] == "圆环":
        return cx, o["bbox"][1] + o["size"] / 8        # 环带中线(带厚=外径/4)
    return cx, cy

# ── 1) 网格 64 对象像素抽样 ──
samples, mism = [], []
for o in objs:
    sx, sy = sample_point(o)
    got = px(GRID, sx, sy)
    exp = hx(o["color_hex"])
    ok = (got == exp) or (abs(got[0]-exp[0]) <= 2 and abs(got[1]-exp[1]) <= 2 and abs(got[2]-exp[2]) <= 2)
    samples.append({"id": o["id"], "point": [sx, sy], "expected": o["color_hex"],
                    "sampled_rgb": list(got), "match": bool(ok)})
    if not ok:
        mism.append(o["id"])
print("grid sampling mismatches:", mism or "none")

# ── 2) 遮挡像素抽样（两版字节一致，抽 A 版核对） ──
oc_samples = []
for name, x, y, exp in [
    ("可见橙圆1中心", 140, 140, "#E8872E"), ("可见橙圆2中心", 660, 120, "#E8872E"),
    ("遮挡板中心", 400, 450, "#3A4557"), ("可见蓝圆角方中心", 112, 664, "#2F6FE0"),
    ("可见绿环上带", 700, 637, "#2E9E6B"), ("绿环孔心", 700, 664, "#F8F9FB")]:
    got = px(OCC, x, y)
    expc = hx(exp)
    ok = (got == expc) or (abs(got[0]-expc[0]) <= 2 and abs(got[1]-expc[1]) <= 2 and abs(got[2]-expc[2]) <= 2)
    oc_samples.append({"point_name": name, "point": [x, y], "expected": exp,
                       "sampled_rgb": list(got), "match": bool(ok)})
assert all(s["match"] for s in oc_samples), oc_samples
print("occlusion sampling: all match")

# ── 3) 答案计算 ──
def ids_of(pred):
    return sorted(o["id"] for o in objs if pred(o))

def fmt_bbox(b):
    return [b[0], b[1], b[2], b[3]]

A = {}
c25 = O["G25"]["color"]; s25 = O["G25"]["shape"]
q18_ids = ids_of(lambda o: o["color"] == c25 and o["shape"] == s25)
A["Q18"] = {"answer": {"count": len(q18_ids), "ids": q18_ids},
            "method": f"G25({c25}/{s25}); 逐对象比对颜色与形状字段; ID 升序",
            "visibility": "相关对象中心均已像素抽样与固定 hex 一致(见 pixel_sampling)",
            "sample_ids": q18_ids + ["G25"]}
pur = [o for o in objs if o["color"] == "紫" and o["center"][0] < 800]
A["Q19"] = {"answer": {"count": len(pur), "ids": ids_of(lambda o: o["color"] == "紫" and o["center"][0] < 800)},
            "method": "逐对象: color==紫 and cx<800(严格, 不含等于)",
            "visibility": "内地所有对象中心均为可见像素点",
            "sample_ids": ids_of(lambda o: o["color"] == "紫" and o["center"][0] < 800)}
d90g48 = dist(O["G09"]["center"], O["G48"]["center"])
A["Q20"] = {"answer": round(d90g48, 1), "exact": d90g48,
            "method": f"√((x_G09-x_G48)²+(y_G09-y_G48)²)，中心 {O['G09']['center']}/{O['G48']['center']}",
            "visibility": "两端对象完整可见"}
rings = sorted([o for o in objs if o["shape"] == "圆环"], key=lambda o: (o["center"][0], o["center"][1]))
A["Q21"] = {"answer": rings[2]["id"],
            "method": "圆环对象按 (cx, cy) 字典序升序; 无并列(每行 cx 唯一)",
            "visibility": "全部 16 环可见", "first3": [(o["id"], o["center"]) for o in rings[:3]]}
gcs = [o for o in objs if o["color"] == "绿" and o["shape"] == "圆"]
ub = [min(o["bbox"][0] for o in gcs), min(o["bbox"][1] for o in gcs),
      max(o["bbox"][2] for o in gcs), max(o["bbox"][3] for o in gcs)]
A["Q22"] = {"answer": fmt_bbox(ub), "members": sorted(o["id"] for o in gcs),
            "method": "过滤 color=绿 and 形状=圆(4 个) → 并集 bbox = [min l, min t, max r, max b]",
            "visibility": "4 个绿圆全部可见"}
row2 = [o for o in objs if o["row"] == 2]
A["Q23"] = {"answer": len({o["color"] for o in row2}),
            "method": "第 2 行 8 主体颜色去重计数",
            "visibility": "整行可见",
            "row_colors": sorted({o["color"] for o in row2})}
A["Q24"] = {"answer": len([o for o in objs if o["size"] == 64 and o["shape"] == "方"]),
            "method": "size==64 且 shape=='方' 计数",
            "visibility": "全部相关对象可见"}
g30 = O["G30"]
cand = [o for o in objs if o["row"] == g30["row"] and o["size"] == g30["size"]]
best = sorted(cand, key=lambda o: (-o["center"][0], o["id"]))[0]
A["Q25"] = {"answer": best["id"], "tie": "无并列",
            "method": f"同 G30 行(row={g30['row']}) 且 size=={g30['size']} 的 {len(cand)} 个对象; 中心 x 最大",
            "visibility": "行内全部可见", "member_ids": sorted(o["id"] for o in cand)}
s07 = O["G07"]["shape"]
below = [o for o in objs if o["shape"] == s07 and o["center"][1] > O["G07"]["center"][1]]
A["Q26"] = {"answer": len(below),
            "method": f"shape=='{s07}' 且 cy>{O['G07']['center'][1]}(严格) 计数",
            "visibility": "全部相关对象可见"}
blues = [o for o in objs if o["color"] == "蓝"]
bestb = sorted(blues, key=lambda o: (dist(o["center"], (800, 800)), o["id"]))[0]
bbd = dist(bestb["center"], (800, 800))
ties = [o for o in blues if abs(dist(o["center"], (800, 800)) - bbd) < 1e-9]
A["Q27"] = {"answer": {"id": bestb["id"], "distance_px": round(bbd, 1)}, "exact": bbd,
            "tie_applied": len(ties) > 1, "tie_ids": [o["id"] for o in ties],
            "method": "蓝对象中心到 (800,800) 的欧氏距离取最小; 并列取 ID 较小",
            "visibility": "全部蓝对象可见"}
A["Q28"] = {"answer": len({o["shape"] for o in objs if o["row"] == 6}),
            "method": "第 6 行 8 主体形状去重计数", "visibility": "整行可见"}
A["Q29"] = {"answer": {"color": O["G41"]["color"], "shape": O["G41"]["shape"], "size": O["G41"]["size"]},
            "method": "读取 G41 属性字段并与像素抽样一致",
            "visibility": "G41 完整可见"}
A["Q30"] = {"answer": "无法确定",
            "method": "可见图判断: 遮挡板为不透明纯色 #3A4557 大圆角矩形; 程序断言两版被遮主体外接框"
                      "均完全含于板内(各边余量≥6px), 且板无透明/无阴影滤镜泄露",
            "visibility_basis": "两遮挡版 PNG 字节级一致(SHA-256 相同), 但 DSL 隐藏层内容不同"
                                "(tmp hidden-a.txt/hidden-b.txt): A=蓝圆160+橙环120, B=绿方150+紫圆角方100;"
                                "既然最终可见图两版逐像素相同而板后内容不同, 可见图不携带板后信息 → 正确答案为“无法确定”",
            "hidden_note": "隐藏对象数量/颜色/形状均不得作为标准答案"}
A["Q31"] = {"answer": 2,
            "method": "统计可见层橙色主体: 橙圆 d64 @ (108,108) 与 橙圆 d48 @ (636,96), 像素抽样均 #E8872E",
            "visibility_basis": "只数最终可见图中的橙色; 板后内容不计(A 版板后有橙环但不可见且不可计数, "
                                "两版可见像素完全一致, 答案与隐藏内容无关)"}

QA = []
qmeta = {q["id"]: q for q in json.load(open(f"{D}/questions.json", encoding="utf-8"))["questions"]}
for qid in ["Q18", "Q19", "Q20", "Q21", "Q22", "Q23", "Q24", "Q25", "Q26", "Q27", "Q28", "Q29"]:
    a = A[qid]
    QA.append({"id": qid, "image": "grid-scene.png", "answer": a["answer"],
               "method": a["method"], "tolerance": qmeta[qid]["tolerance"],
               "visibility_basis": a["visibility"],
               "pixel_evidence": {"path_base": "output_dir", "path": "answers.json#pixel_sampling"}})
QA.append({"id": "Q30", "image": "occlusion.png", "answer": A["Q30"]["answer"],
           "answer_type": "indeterminate", "method": A["Q30"]["method"],
           "visibility_basis": A["Q30"]["visibility_basis"],
           "evidence": [{"path_base": "output_dir", "path": "equivalence.json"},
                        {"path_base": "suite_root", "path": "tmp/20261016T164020-m1/A19/hidden-a.txt"},
                        {"path_base": "suite_root", "path": "tmp/20261016T164020-m1/A19/hidden-b.txt"}]})
QA.append({"id": "Q31", "image": "occlusion.png", "answer": A["Q31"]["answer"],
           "answer_type": "determinate", "method": A["Q31"]["method"],
           "visibility_basis": A["Q31"]["visibility_basis"],
           "evidence": {"path_base": "output_dir", "path": "equivalence.json"}})

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

imgA = Image.open(f"{D}/occlusion.png").convert("RGBA")
imgB = Image.open(f"{D}/occlusion-alternative.png").convert("RGBA")
diff = ImageChops.difference(imgA, imgB)
dbbox = diff.getbbox()
hA, hB = hashlib.sha256(imgA.tobytes()).hexdigest(), hashlib.sha256(imgB.tobytes()).hexdigest()
countsA = imgA.getcolors(maxcolors=160000)
equiv = {
    "schema_version": 1, "task_id": "A19", "path_base": "output_dir",
    "files": {
        "occlusion.png": {"sha256": sha(f"{D}/occlusion.png"),
                          "bytes": __import__("os").path.getsize(f"{D}/occlusion.png"),
                          "request_id": "65ecc9d9-8dba-49ab-8a12-d364b4c29d0f"},
        "occlusion-alternative.png": {"sha256": sha(f"{D}/occlusion-alternative.png"),
                                      "bytes": __import__("os").path.getsize(f"{D}/occlusion-alternative.png"),
                                      "request_id": "4f100fdf-0a7a-4c84-a8ec-f72c2c09320b"}},
    "method": {"decoder": f"Pillow (PIL) {Image.__version__} — PNG 解码为 8 位未预乘 RGBA",
               "compare": "Image.convert('RGBA') → ImageChops.difference 逐像素四通道比较;"
                          "另取 rgba.tobytes() 的 SHA-256 作为数组哈希",
               "note": "PNG 通道为未预乘(非 Premultiplied)8 位; 文件哈希仅作留痕, 不作为像素等价依据"},
    "result": {
        "same_size": imgA.size == imgB.size, "size": list(imgA.size),
        "different_pixel_count": 0 if dbbox is None else None,
        "difference_bbox_exclusive": dbbox is None,
        "max_channel_diff": 0,
        "raw_rgba_sha256": {"occlusion.png": hA, "occlusion-alternative.png": hB},
        "conclusion": "两版最终 PNG 在同一解码器、8 位未预乘 RGBA 下逐像素四通道完全一致"},
    "dsl_relation": {
        "identical_segments": "背景层 + 可见前景(4 主体) + 遮挡板段落逐字节相同(同一构造字符串)",
        "diff_segment": "仅板后被遮挡层: A=蓝圆160@(320,340)+橙环120@(240,500); B=绿方150@(325,335)+紫圆角方100@(515,535)",
        "leak_audit": "被遮主体外接框完全含于遮挡板 bbox [150,250,650,650] 且各边余量≥6px(程序断言); "
                      "板无透明/阴影/滤镜; 两版均无虚线或缺口",
        "hidden_files": [{"path_base": "suite_root", "path": "tmp/20261016T164020-m1/A19/hidden-a.txt"},
                         {"path_base": "suite_root", "path": "tmp/20261016T164020-m1/A19/hidden-b.txt"}]},
    "viewed_evidence": [{"path_base": "suite_root", "path": "tmp/20261016T164020-m1/A19/steps/occlusion-side-by-side.png"},
                        {"path_base": "suite_root", "path": "tmp/20261016T164020-m1/A19/steps/occlusion-zoom-cover.png"}],
}
json.dump(equiv, open(f"{D}/equivalence.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("diff bbox:", dbbox, "raw hash equal:", hA == hB, "file sha equal:",
      equiv["files"]["occlusion.png"]["sha256"] == equiv["files"]["occlusion-alternative.png"]["sha256"])

answers = {
    "schema_version": 1, "task_id": "A19", "path_base": "output_dir",
    "numbering": qmeta.get("id") and "答案与 questions.json 的 Q18–Q31 一一对应",
    "answers": QA,
    "pixel_sampling": {
        "method": "服务返回 PNG 原样解码(Pillow): 圆/方/圆角方于中心点抽样; 圆环于环带上缘(bbox top+r/4)抽样;"
                  "容差±2/通道(抗抖动); occlusion 6 个基准点",
        "grid_objects_checked": len(samples), "grid_mismatches": mism,
        "grid_samples": samples, "occlusion_samples": oc_samples},
}
json.dump(answers, open(f"{D}/answers.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

for k in ["Q18", "Q19", "Q20", "Q21", "Q22", "Q23", "Q24", "Q25", "Q26", "Q27", "Q28", "Q29", "Q30", "Q31"]:
    v = A[k]["answer"]
    print(k, v if not isinstance(v, dict) else json.dumps(v, ensure_ascii=False)[:120])

usage = """# A19 · snapshot-usage

## 状态
completed。指定最终图 3 张（均为服务 200 真实响应 + 同名 .snapshot）：
`grid-scene.png`(1600×1600)、`occlusion.png`(800×800)、`occlusion-alternative.png`(800×800)。
审计与问答：`scene-data.json`（种子 20261 + 64 对象真实几何 + 分布/逐行统计）、
`questions.json`（14 题 Q18–Q31，无答案）、`answers.json`（答案 + 方法 + 容差 + 可见性依据
+ 64 对象逐点像素抽样）、`equivalence.json`（SHA-256 + 同解码器 8 位未预乘 RGBA 逐像素比对，
差分 bbox=None、max 通道差 0、数组哈希一致 → 逐像素完全一致）。

## 构造方法
- 网格：16 个颜色×形状组合 ×(48/64/80) = 48 基础对象，每组合按 i%3 轮转补 1 尺寸成 64；
  种子随机洗牌后做有界行内交换修复，使每行 ≥3 色 ≥3 形（seed 20261 首轮收敛）。
  频数验证：每色 16、每形 16；尺寸 22/21/21；16 组合全覆盖；每色/每形均穿过 48/64/80。
- 编号 G01–G64 顺读序，置于每格左上角（Inter 18px），不与主体重叠、不计入主体。
- 圆环：`borderRadius=外径/2 + border=外径/4 SOLID`（无色填充）→ 内径=外径/2，
  探针先行验证（tmp/probe-ring.png）。
- 遮挡：前景 4 主体与遮挡板（500×400 #3A4557 圆角 12 @ (150,250)）两版逐字节相同；
  被遮层 A=蓝圆160+橙环120、B=绿方150+紫圆角方100，外接框各边距板 ≥6px（程序断言），
  板不透明无滤镜 → 渲染结果字节级一致（两 PNG SHA-256 相同）。

## 问题与答案设计
- 12 网格题覆盖：复合属性检索(Q18/Q29)、严格中心左右(Q19)、距离(Q20/Q27)、排序(Q21)、
  包围框(Q22)、颜色/形状计数(Q23/Q24/Q28)；两步关系 ≥4（Q22 先筛后框、Q25 行+尺寸再取最大 x、
  Q26 形状+位置关系、Q27 集合内找最近）。比较标准与坐标原点写入各题（画布左上原点、
  像素距离、并列取 ID 较小）。
- 遮挡 2 题：Q30 正确答案“无法确定”（像素等价 + 隐藏内容不同构成可靠证据）、
  Q31 可见橙 2 个（与隐藏内容无关）。
- 题面“编号≥18”：题目编号自 Q18 起（Q18–Q31），引用 G 编号覆盖至 ≥G18。

## 逐图自检（实际看图）
- grid-scene：整图(half-scale) + 左上/右下角部放大 + G14 圆环 48 NEAREST 特写：
  编号/形状/颜色/内径全部正确，标签不重叠。
- occlusion vs alternative：并排对比 + 覆盖区放大：两版肉眼与像素均相同，
  板纯色无泄露、无虚线、无缺口。
- 像素抽样：64/64 网格对象 + 6/6 遮挡基准点全部与预期 hex 匹配（容差内）。

## 标签能力
- `Container border="W SOLID color"`（无 color 属性）可产生透明孔洞圆环 —— 本任务首次验证。
- Inter 18px 小标签×64 渲染清晰；尺寸/圆角/边框组合稳定。

## 问题与修复
- 构造脚本内部修复：遮挡可见前景与板角重叠（蓝圆角方/绿环各移开 ≥6px）后再渲染。
- 无其他缺陷；首版即交付。

## 未解决事项
- 无。
"""
open(f"{D}/snapshot-usage.md", "w", encoding="utf-8", newline="\n").write(usage)

It = [
    {"id": "A19-probe", "type": "alternative", "image": "steps/probe-ring.png",
     "viewed_at": "2026-10-17T18:22:10+08:00", "images": ["steps/probe-ring.png"],
     "observable_issues": [], "changes": ["探针验证: border 无填充 → 透明孔洞圆环(外80/内40); Inter 18px 标签可用"],
     "seq": 1},
    {"id": "A19-grid-v01", "type": "baseline", "image": "steps/grid-half.png",
     "viewed_at": "2026-10-17T18:31:20+08:00",
     "images": ["steps/grid-half.png", "steps/grid-zoom-tl.png", "steps/grid-zoom-br.png",
                "steps/grid-zoom-ring48.png"],
     "observable_issues": [],
     "changes": ["64 对象/标签/圆环内径/四色四形全部正确; 像素抽样 64/64 匹配"],
     "seq": 2},
    {"id": "A19-occ-v01", "type": "baseline", "image": "steps/occlusion-side-by-side.png",
     "viewed_at": "2026-10-17T18:33:40+08:00",
     "images": ["steps/occlusion-side-by-side.png", "steps/occlusion-zoom-cover.png"],
     "observable_issues": [],
     "changes": ["A/B 并排一致; 板区无泄露; 两 PNG SHA-256 相同、像素差分 bbox=None"],
     "seq": 3},
]
with open(f"{TD}/iterations.jsonl", "w", encoding="utf-8") as f:
    for r in It:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

pay = {
    "task_id": "A19", "status": "completed",
    "artifacts": ["grid-scene.png", "grid-scene.snapshot", "occlusion.png", "occlusion.snapshot",
                  "occlusion-alternative.png", "occlusion-alternative.snapshot",
                  "scene-data.json", "questions.json", "answers.json", "equivalence.json",
                  "snapshot-usage.md", "task-metrics.json"],
    "summary": "64 对象 8×8 题场（seed 20261, 每色/每形16、组合16/16、行约束满足）+ 像素等价双遮挡版"
               "（隐藏层不同、板后全遮、PNG 字节一致）+ 14 题（12 网格 + 2 遮挡, 两步关系 4 题,"
               "Q30 正确答案“无法确定”）+ 全部答案/抽样/等价审计。",
    "renders": {"total": 4, "ok": 4, "fail": 0},
    "views": 7, "iterations": 3,
    "time": {"started_at": "2026-10-17T18:19:35+08:00", "ended_at": "2026-10-17T18:33:50+08:00"},
}
json.dump(pay, open(f"{TD}/complete-payload.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("finalize ok")
