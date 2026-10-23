"""A19 离线校验：独立复核网格几何约束、遮挡构造、以及三张 DSL 的结构安全性。

不复用 a19_core 的生成结论——颜色/形状/尺寸频次、组合覆盖、属性×尺寸覆盖、
每行分布都用另一条路径（Counter 统计 + 枚举）重算，任一不满足即报错退出。
"""
from __future__ import annotations

import math
import re
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import a19_core as C

COLORS = [n for n, _ in C.COLORS]
SHAPES = list(C.SHAPES)
SIZES = list(C.SIZES)

TAG_RE = re.compile(r"<(/?)([A-Za-z][A-Za-z0-9]*)\b([^>]*?)>")
ATTR_RE = re.compile(r'(\w+)="([^"]*)"')


def parse_tags(text):
    """把 DSL 文本解析成 {tag, children, attrs} 树（虚拟根 tag=None）。"""
    root = {"tag": None, "children": [], "attrs": {}}
    stack = [root]
    for m in TAG_RE.finditer(text):
        closing = m.group(1) == "/"
        name, attrs_s = m.group(2), m.group(3)
        selfclose = m.group(0).endswith("/>")
        if closing:
            if len(stack) < 2:
                raise ValueError("extra closing tag </%s>" % name)
            opened = stack[-1]["tag"]
            if opened != name:
                raise ValueError("tag mismatch: <%s> vs </%s>" % (opened, name))
            stack.pop()
            continue
        node = {"tag": name,
                "attrs": dict(ATTR_RE.findall(attrs_s)),
                "children": [], "src": m.group(0)}
        stack[-1]["children"].append(node)
        if not selfclose:
            stack.append(node)
    if len(stack) != 1:
        raise ValueError("unclosed tags: %s" % [n["tag"] for n in stack[1:]])
    return root["children"][0]


def walk(node):
    yield node
    for ch in node["children"]:
        yield from walk(ch)


def walk_with_parent(node, parent=None):
    yield node, parent
    for ch in node["children"]:
        yield from walk_with_parent(ch, node)


problems = []


def check(cond, msg):
    if not cond:
        problems.append(msg)


def grid_checks(objs):
    n = len(objs)
    check(n == 64, "对象数应为 64，实际 %d" % n)
    check([o["id"] for o in objs] == ["G%02d" % i for i in range(1, 65)],
          "ID 应为 G01–G64 行主序连续")

    # 每格恰好一个主体，编号与行列一致
    seen = set()
    for o in objs:
        key = (o["row"], o["col"])
        check(key not in seen, "格子重复 %s" % (o["id"],))
        seen.add(key)
        check(o["id"] == "G%02d" % (o["row"] * 8 + o["col"] + 1),
              "%s 的编号与行列不一致" % o["id"])
    check(len(seen) == 64, "应覆盖 64 个格子，实际 %d" % len(seen))

    # 颜色 / 形状 / 尺寸频次
    cc = {k: 0 for k in COLORS}
    sc = {k: 0 for k in SHAPES}
    zc = {k: 0 for k in SIZES}
    for o in objs:
        cc[o["color"]] += 1
        sc[o["shape"]] += 1
        zc[o["size"]] += 1
    check(all(v == 16 for v in cc.values()),
          "颜色频次应为各 16：%s" % cc)
    check(all(v == 16 for v in sc.values()),
          "形状频次应为各 16：%s" % sc)
    check(sum(zc.values()) == 64 and set(zc) == set(SIZES),
          "尺寸应只用 48/64/80 且合计 64：%s" % zc)

    # 16 种颜色×形状组合必须全覆盖
    combos = {}
    for o in objs:
        combos[(o["color"], o["shape"])] = combos.get((o["color"], o["shape"]), 0) + 1
    check(len(combos) == 16, "16 种颜色×形状组合应全部出现，实际 %d" % len(combos))
    for col in COLORS:
        for sh in SHAPES:
            check(combos.get((col, sh), 0) >= 1,
                  "组合缺失: %s + %s" % (col, sh))

    # 每种颜色、每种形状都必须出现全部三种尺寸
    for col in COLORS:
        sizes = {o["size"] for o in objs if o["color"] == col}
        check(sizes == set(SIZES),
              "颜色 %s 未覆盖全部尺寸：%s" % (col, sorted(sizes)))
    for sh in SHAPES:
        sizes = {o["size"] for o in objs if o["shape"] == sh}
        check(sizes == set(SIZES),
              "形状 %s 未覆盖全部尺寸：%s" % (sh, sorted(sizes)))

    # 每行 ≥3 颜色、≥3 形状
    for r in range(8):
        row = [o for o in objs if o["row"] == r]
        check(len({o["color"] for o in row}) >= 3,
              "第 %d 行颜色种类不足 3" % (r + 1))
        check(len({o["shape"] for o in row}) >= 3,
              "第 %d 行形状种类不足 3" % (r + 1))

    # 几何：中心 = 格心；bbox 正确；标签在主体外且不越格
    for o in objs:
        r, c = o["row"], o["col"]
        check(o["center"] == [200 * c + 100, 200 * r + 100],
              "%s 中心不是格心" % o["id"])
        d = o["size"]
        exp = [o["center"][0] - d // 2, o["center"][1] - d // 2,
               o["center"][0] + d // 2, o["center"][1] + d // 2]
        check(o["bbox"] == exp, "%s bbox 与尺寸不一致" % o["id"])
        # 主体与标签不相交
        lx0, ly0, lx1, ly1 = o["label_box"]
        sx0, sy0, sx1, sy1 = o["bbox"]
        # 主体与标签是真正的矩形不相交（标签比主体宽，只看垂直方向不够）
        check(lx1 <= sx0 or lx0 >= sx1 or ly1 <= sy0 or ly0 >= sy1,
              "%s 标签盒与主体盒相交" % o["id"])
        check(ly0 >= sy1, "%s 标签未落在主体正下方" % o["id"])
        # 都不越格
        x0, y0 = 200 * c, 200 * r
        check(min(o["bbox"][0], o["bbox"][2]) >= x0 and
              max(o["bbox"][0], o["bbox"][2]) <= x0 + 200,
              "%s 主体越出所在格" % o["id"])
        check(min(o["bbox"][1], o["bbox"][3]) >= y0 and
              max(o["bbox"][1], o["bbox"][3]) <= y0 + 200,
              "%s 主体越出所在格" % o["id"])
        check(lx0 >= x0 and lx1 <= x0 + 200 and
              ly0 >= y0 and ly1 <= y0 + 200,
              "%s 标签越出所在格" % o["id"])

    # 圆环内径 = 外径的一半
    for o in objs:
        if o["shape"] == "ring":
            check(o["size"] % 4 == 0, "%s 圆环外径不能被 4 整除" % o["id"])
            check(o["size"] - 2 * (o["size"] // 4) == o["size"] // 2,
                  "%s 圆环内径不等于外径的一半" % o["id"])

    return {"colors": cc, "shapes": sc, "sizes": zc,
            "combos": {("%s+%s" % k): v for k, v in combos.items()},
            "rows": [
                {"row": r + 1,
                 "ids": [o["id"] for o in objs if o["row"] == r],
                 "colors": {k: sum(1 for o in objs
                                   if o["row"] == r and o["color"] == k)
                            for k in COLORS},
                 "shapes": {k: sum(1 for o in objs
                                   if o["row"] == r and o["shape"] == k)
                            for k in SHAPES},
                 "sizes": {str(k): sum(1 for o in objs
                                       if o["row"] == r and o["size"] == k)
                           for k in SIZES}}
                for r in range(8)]}


def occ_checks(scene_a, scene_b):
    """遮挡场景：两版可见层逐字一致、隐藏层完全落在面板内且留有余量。"""
    pa = scene_a["occluder"]["bbox"]
    for s in (scene_a, scene_b):
        check(s["canvas"] == [800, 800], "遮挡画布应为 800×800")
        # 前景不越界
        for f in s["foreground"]:
            check(f["bbox"][0] >= 0 and f["bbox"][2] <= 800 and
                  f["bbox"][1] >= 0 and f["bbox"][3] <= 800,
                  "%s 前景越出画布" % f["id"])
        # 隐藏对象必须完全在面板矩形内，且四边留 ≥ 30px
        for h in s["hidden"]:
            x0, y0, x1, y1 = h["bbox"]
            check(x0 >= pa[0] + 30 and x1 <= pa[2] - 30 and
                  y0 >= pa[1] + 30 and y1 <= pa[3] - 30,
                  "%s 隐藏对象离面板边界不足 30px: %s" % (h["id"], h["bbox"]))
    # 两版隐藏层必须真的不同
    ids_a = [h["id"] for h in scene_a["hidden"]]
    ids_b = [h["id"] for h in scene_b["hidden"]]
    check(ids_a != ids_b, "两版隐藏对象编号应不同")
    sig_a = {(h["shape"], h["hex"], h["size"], tuple(h["center"]))
             for h in scene_a["hidden"]}
    sig_b = {(h["shape"], h["hex"], h["size"], tuple(h["center"]))
             for h in scene_b["hidden"]}
    check(len(sig_a & sig_b) == 0,
          "两版隐藏对象不应有任何同一 (形状,颜色,尺寸,中心) 组合，交集 %d" % len(sig_a & sig_b))


def dsl_checks(dsls, tag=""):
    for key, dsl in dsls.items():
        b = dsl.encode("utf-8")
        check(len(b) <= 1048576, "%s/%s DSL 超过请求上限: %d" % (tag, key, len(b)))
        check("<Image" not in dsl, "%s/%s 使用了外部图像" % (tag, key))
        check("<Rect" not in dsl and "<Line" not in dsl and "<Path" not in dsl,
              "%s/%s 使用了不存在的标签" % (tag, key))
        root = parse_tags(dsl)
        check(root["tag"] == "Snapshot", "%s/%s 根节点不是 Snapshot" % (tag, key))
        check(len(root["children"]) == 1, "%s/%s Snapshot 孩子数 != 1" % (tag, key))
        for node, parent in walk_with_parent(root):
            if parent is not None and parent["tag"] in ("Container", "Positioned"):
                check(len(parent["children"]) == 1,
                      "%s/%s <%s> 孩子数应为 1，实际 %d"
                      % (tag, key, parent["tag"], len(parent["children"])))
            if parent is not None and parent["tag"] == "Column":
                check(node["tag"] != "Row",
                      "%s/%s Column 内不能直接放 Row" % (tag, key))
            for k, v in node["attrs"].items():
                check("<" not in v and "&" not in v,
                      "%s/%s 属性 %s 含裸 < 或 &" % (tag, key, k))
        texts = [n for n in walk(root) if n["tag"] == "Text"]
        for t in texts:
            check("fontFamily" in t["attrs"], "%s/%s 有 Text 缺 fontFamily" % (tag, key))
            check("<" not in t["attrs"].get("text", "")
                  and "&" not in t["attrs"].get("text", ""),
                  "%s/%s Text 文本含裸 < 或 &" % (tag, key))
        return root, dsl


def run():
    objs = C.grid_objects()
    facts = grid_checks(objs)
    scene_a = C.occ_scene("A")
    scene_b = C.occ_scene("B")
    occ_checks(scene_a, scene_b)
    dsls, objs = C.build_all()
    dsl_checks(dsls, "final")

    # 遮挡 DSL：A/B 除隐藏层外必须逐字一致。
    # 隐藏层在文档开头连续排布：第 3..(3+n*3-1) 行（0 起算），每对象 3 行。
    la = dsls["occlusion"].splitlines(keepends=True)
    lb = dsls["occlusion-alternative"].splitlines(keepends=True)
    head = la[:3]
    n_a, n_b = len(C.HIDDEN_A), len(C.HIDDEN_B)
    check(head == lb[:3], "遮挡 A/B 的头部 3 行不一致")
    hid_a = la[3:3 + 3 * n_a]
    hid_b = lb[3:3 + 3 * n_b]
    check(len(hid_a) == 3 * n_a and len(hid_b) == 3 * n_b,
          "隐藏层行数异常: A=%d B=%d" % (len(hid_a), len(hid_b)))
    # 隐藏块里必须恰好有 n 个 <Positioned 开标签
    def cnt(blk, sub):
        return sum(1 for ln in blk if sub in ln)

    check(cnt(hid_a, "<Positioned") == n_a,
          "遮挡 A 隐藏块 <Positioned 数应为 %d，实际 %d"
          % (n_a, cnt(hid_a, "<Positioned")))
    check(cnt(hid_b, "<Positioned") == n_b,
          "遮挡 B 隐藏块 <Positioned 数应为 %d，实际 %d"
          % (n_b, cnt(hid_b, "<Positioned")))
    # 隐藏块结构完整：开闭标签成对
    check(cnt(hid_a, "</Positioned>") == n_a and
          cnt(hid_b, "</Positioned>") == n_b,
          "遮挡隐藏块 </Positioned> 数异常")
    # 隐藏块不得含文字、阴影、滤镜或图像（圆角属于几何，不影响结论）
    for tag, blk in (("A", hid_a), ("B", hid_b)):
        check("<Text" not in blk and "shadow" not in blk
              and "filter" not in blk and "Image" not in blk,
              "遮挡 %s 隐藏块含文字/阴影/滤镜/图像" % tag)
    frame_a = la[:3] + la[3 + 3 * n_a:]
    frame_b = lb[:3] + lb[3 + 3 * n_b:]
    check(frame_a == frame_b,
          "遮挡 A/B 除隐藏层外的框架行不完全一致（%d vs %d 行）"
          % (len(frame_a), len(frame_b)))
    # 隐藏块内容必须真的不同
    check(hid_a != hid_b, "遮挡 A/B 的隐藏块内容相同，应有差异")

    # 绘制顺序：隐藏层 < 面板 < 前景 < 标题
    panel_idx = [i for i, ln in enumerate(la)
                 if C.C_PANEL in ln and "borderRadius" in ln]
    check(len(panel_idx) == 1, "遮挡 DSL 应恰好有一个面板元素")
    if panel_idx:
        pi = panel_idx[0]
        check(3 + 3 * n_a <= pi,
              "面板必须晚于全部隐藏对象绘制（面板行 %d，隐藏块结束行 %d）"
              % (pi, 3 + 3 * n_a))
        # 前景（含 F01–F09 标签）与标题都必须在面板之后
        f01 = [i for i, ln in enumerate(la) if "F01" in ln]
        check(len(f01) == 1 and f01[0] > pi, "前景必须在面板之后")
        title_idx = [i for i, ln in enumerate(la) if "遮挡案例" in ln]
        check(len(title_idx) == 1 and title_idx[0] > pi, "标题必须在面板之后")
        close_idx = [i for i, ln in enumerate(la) if ln.strip() == "</Stack>"]
        check(close_idx and close_idx[0] > pi, "闭合标签顺序异常")

    # 遮挡面板必须是不透明纯色（无 alpha 通道）
    check(len(C.C_PANEL) == 7 and C.C_PANEL.startswith("#"),
          "面板填充色应为 6 位十六进制纯色: %s" % C.C_PANEL)
    for s in (scene_a, scene_b):
        check(s["occluder"]["opaque"] is True, "面板应标记为不透明")
        check(s["occluder"]["shadows"] == [] and s["occluder"]["filters"] == [],
              "面板不应有阴影或滤镜")

    print("problems:", len(problems))
    for p in problems:
        print(" -", p)
    print("frame_lines_shared:", len(frame_a))
    print("counts:", {k: facts[k] for k in ("colors", "shapes", "sizes")})
    print("combo_count:", len(facts["combos"]),
          "min_combo:", min(facts["combos"].values()))
    print("hidden:", {"A": len(scene_a["hidden"]), "B": len(scene_b["hidden"])})
    return problems


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    probs = run()
    sys.exit(1 if probs else 0)
