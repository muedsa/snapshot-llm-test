"""A18 离线断言：发请求前把能算的东西算完。

两套互相独立的验证：

1. **几何**（直接读 a18_core 的整数坐标）：单元互不重叠、连线不遮圆、节点不压
   单元、全部落在面板与画布内、单元数量与配色恒定、第三幕分配满足
   「每节点 5 个且至少两种颜色」。
2. **DSL 结构**（把生成的 DSL 文本重新解析成树）：根结构合规、Container /
   Positioned 单孩子、Positioned 父必须是 Stack、属性值无 ``<`` 与 ``&``、
   没有 ``<Image``/``<Row``/``<Column``、全图只有 4 个 Text 且内容只能是
   总标题与三个幕名、请求体不超过服务上限。

运行：``python -I a18_check.py``（无参数则检查 A 与 B 两套）。
"""
from __future__ import annotations

import json
import math
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
import a18_core as C  # noqa: E402

SUITE_ROOT = HERE.parents[3]
RUN_ID = HERE.parents[1].name
DSL_MAX = 1048576          # openapi.yaml：请求体超过 snapshot.max-request-size 返回 413

TAG_RE = re.compile(r"<(/?)([A-Za-z][A-Za-z0-9]*)([^>]*?)(/?)>", re.S)
ATTR_RE = re.compile(r'([A-Za-z][\w-]*)\s*=\s*"([^"]*)"')


def parse_tags(dsl):
    root = {"tag": None, "attrs": {}, "children": [], "text": ""}
    stack = [root]
    pos = 0
    for m in TAG_RE.finditer(dsl):
        close, tag, raw, selfc = m.groups()
        chunk = dsl[pos:m.start()]
        if chunk.strip() and stack[-1]["tag"] in ("Text", "Raw"):
            stack[-1]["text"] += chunk
        pos = m.end()
        if close:
            el = stack.pop()
            if el["tag"] != tag:
                raise AssertionError("标签不配对：%s vs %s" % (el["tag"], tag))
        else:
            el = {"tag": tag, "attrs": dict(ATTR_RE.findall(raw)),
                  "children": [], "text": ""}
            stack[-1]["children"].append(el)
            if not selfc and not close:
                stack.append(el)
    if len(stack) != 1:
        raise AssertionError("标签未闭合：%s" % [s["tag"] for s in stack])
    return root


def walk(el, parent=None, out=None):
    if out is None:
        out = []
    out.append((el, parent))
    for ch in el["children"]:
        walk(ch, el, out)
    return out


# ---------------------------------------------------------------- 几何

def geo_checks(scene):
    problems = []
    facts = {}
    W, H = scene["canvas"]
    all_units = {uid: col for uid, col in C.UNITS}
    per_act_units = {}
    per_act_nodes = {}

    for act in scene["acts"]:
        a = act["index"]
        px, py, pw, ph = act["panel"]
        # ---- 数量与配色恒定
        units = act["units"]
        if len(units) != 15:
            problems.append("幕 %d 单元数 %d ≠ 15" % (a, len(units)))
        ids = [u[0] for u in units]
        if sorted(ids) != sorted(all_units):
            problems.append("幕 %d 单元 ID 与 U01–U15 不一致" % a)
        for uid, col, hexv, _p, _rid in units:
            if col != all_units[uid]:
                problems.append("幕 %d %s 颜色 %s 与基准 %s 不一致（跨幕身份变了）"
                                % (a, uid, col, all_units[uid]))
            if hexv != C.HEX[col]:
                problems.append("幕 %d %s 色值与颜色名不一致" % (a, uid))
        per_act_units[a] = {u[0]: (u[1], u[3]) for u in units}

        # ---- 节点
        nodes = act["nodes"]
        if len(nodes) != 3:
            problems.append("幕 %d 节点数 %d ≠ 3" % (a, len(nodes)))
        nids = [n[0] for n in nodes]
        if sorted(nids) != ["N01", "N02", "N03"]:
            problems.append("幕 %d 节点 ID %s ≠ N01–N03" % (a, nids))
        per_act_nodes[a] = {nid: c for nid, c in nodes}
        for nid, c in nodes:
            if c[0] - C.NODE_H < 0 or c[1] - C.NODE_H < 0 \
               or c[0] + C.NODE_H > pw or c[1] + C.NODE_H > ph:
                problems.append("幕 %d 节点 %s 越出面板" % (a, nid))

        node_rects = [(cx - C.NODE_H, cy - C.NODE_H, C.NODE_S, C.NODE_S)
                      for _, (cx, cy) in nodes]
        centers = [p for _u, _c, _h, p, _r in units]
        node_center = {nid: c for nid, c in nodes}

        # ---- 单元互不重叠（圆-圆：中心距 ≥ 36）
        mind = None
        for i in range(len(centers)):
            for j in range(i + 1, len(centers)):
                d = math.hypot(centers[i][0] - centers[j][0],
                               centers[i][1] - centers[j][1])
                if mind is None or d < mind:
                    mind = d
        if mind < C.UNIT_D - 1e-9:
            problems.append("幕 %d 单元重叠：最小中心距 %.3f < %d" % (a, mind, C.UNIT_D))

        # ---- 单元越界
        for uid, _c, _h, (cx, cy), _r in units:
            if cx - C.UNIT_R < 0 or cy - C.UNIT_R < 0 \
               or cx + C.UNIT_R > pw or cy + C.UNIT_R > ph:
                problems.append("幕 %d 单元 %s 越出面板 (%d,%d)" % (a, uid, cx, cy))
            if cx - C.UNIT_R < 0 or cy - C.UNIT_R < 0 \
               or cx + C.UNIT_R > W or cy + C.UNIT_R > H:
                problems.append("幕 %d 单元 %s 越出画布" % (a, uid))

        # ---- 单元不能被节点压住
        for uid, _c, _h, (cx, cy), _r in units:
            for nid, nc in nodes:
                g = min(C.rect_gap(cx + s * C.UNIT_R * 0.7071,
                                   cy + t * C.UNIT_R * 0.7071,
                                   nc[0] - C.NODE_H, nc[1] - C.NODE_H,
                                   C.NODE_S, C.NODE_S)
                        for s, t in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                if g < -1e-9:
                    problems.append("幕 %d 单元 %s 被节点 %s 压住" % (a, uid, nid))

        # ---- 连线不遮圆、不压节点
        nb = 0
        for uid, _c, _h, uc, rid in units:
            ch = next(c for c in act["chains"] if c["unit"] == uid)
            if ch["receiver"] != rid:
                problems.append("幕 %d %s 连线接收者与记录不一致" % (a, uid))
            nb += len(ch["beads"])
            for bx, by in ch["beads"]:
                # 连线上不能有字面坐标越界
                if bx - C.BEAD_R < 0 or by - C.BEAD_R < 0 \
                   or bx + C.BEAD_R > pw or by + C.BEAD_R > ph:
                    problems.append("幕 %d %s 的连线圆点越出面板" % (a, uid))
                for otx, oty in centers:
                    if math.hypot(bx - otx, by - oty) < C.UNIT_R + C.BEAD_R - 1e-9:
                        problems.append("幕 %d %s 的连线遮住了单元 (%d,%d)"
                                        % (a, uid, bx, by))
                for rxc, ryc, rw, rh in node_rects:
                    if C.rect_gap(bx, by, rxc, ryc, rw, rh) < C.BEAD_R - 1e-9:
                        problems.append("幕 %d %s 的连线压上了节点 (%d,%d)"
                                        % (a, uid, bx, by))
        # ---- 连线必须真的朝自己的接收节点走
        for ch in act["chains"]:
            uc = per_act_units[a][ch["unit"]][1]
            nc = node_center[ch["receiver"]]
            for bx, by in ch["beads"]:
                v1 = (nc[0] - uc[0], nc[1] - uc[1])
                v2 = (bx - uc[0], by - uc[1])
                l1 = math.hypot(*v1) or 1.0
                l2 = math.hypot(*v2) or 1.0
                # 归一化后：|cross|/(|v1||v2|) = sin(夹角)，dot/(|v1||v2|) = cos(夹角)
                sin = abs(v1[0] * v2[1] - v1[1] * v2[0]) / (l1 * l2)
                cos = (v1[0] * v2[0] + v1[1] * v2[1]) / (l1 * l2)
                if cos < 0 or sin > 0.02:     # sin(1.15°) ≈ 0.02，坐标取整后的容差
                    problems.append("幕 %d %s 的连线方向偏离接收节点" % (a, ch["unit"]))
        facts["act%d_min_unit_gap" % a] = round(mind - C.UNIT_D, 3)
        facts["act%d_min_unit_dist" % a] = round(mind, 3)
        facts["act%d_connector_beads" % a] = nb

        # ---- 分配
        recv = {}
        for uid, _c, _h, _p, rid in units:
            recv.setdefault(rid, []).append(uid)
        facts["act%d_load" % a] = {k: len(v) for k, v in sorted(recv.items())}
        if a == 3:
            for nid, v in recv.items():
                if len(v) != 5:
                    problems.append("幕 3 节点 %s 收到 %d 个单元（应为 5）" % (nid, len(v)))
                cols = {all_units[u] for u in v}
                if len(cols) < 2:
                    problems.append("幕 3 节点 %s 的 5 个单元只有 %d 种颜色"
                                    % (nid, len(cols)))
            for color in ("blue", "orange", "gray"):
                got = sum(1 for v in recv.values() for u in v if all_units[u] == color)
                if got != 5:
                    problems.append("幕 3 颜色 %s 共分配 %d 个（应为 5）" % (color, got))
            if sum(len(v) for v in recv.values()) != 15:
                problems.append("幕 3 单元总数 %d ≠ 15"
                                % sum(len(v) for v in recv.values()))
        elif a in (1, 2):
            if sorted(recv) != ["N01"]:
                problems.append("幕 %d 只有 N01 应在收（实际 %s）" % (a, sorted(recv)))

    # ---- 跨幕身份
    for uid in all_units:
        if not all(uid in per_act_units[a] for a in (1, 2, 3)):
            problems.append("%s 没有出现在全部三幕" % uid)
    for a in (1, 2, 3):
        if sorted(per_act_nodes[a]) != ["N01", "N02", "N03"]:
            problems.append("幕 %d 节点身份不完整" % a)

    # ---- 叙事几何量（供 story-audit.json 引用）
    ring1 = 2 * C.R_ACT1 * math.sin(math.radians(180 / 15))
    ring2 = 2 * C.R_ACT2 * math.sin(math.radians(180 / 15))
    # 扇形相邻角步 = (25 - (-25)) / 4 = 12.5°，相邻中心距 = 2*R*sin(步/2)
    fan_step = (25.0 - -25.0) / (len(C.FAN_ANGLES) - 1)
    fan = 2 * C.FAN_R * math.sin(math.radians(fan_step / 2))
    facts.update({
        "act1_ring_radius": C.R_ACT1,
        "act2_ring_radius": C.R_ACT2,
        "act1_ring_adjacent_dist": round(ring1, 3),
        "act2_ring_adjacent_dist": round(ring2, 3),
        "act1_ring_adjacent_gap": round(ring1 - C.UNIT_D, 3),
        "act2_ring_adjacent_gap": round(ring2 - C.UNIT_D, 3),
        "ring_adjacent_dist_drop_pct": round((1 - ring2 / ring1) * 100, 1),
        "act1_annulus_outer_radius": round(C.R_ACT1 + C.UNIT_R, 3),
        "act2_annulus_outer_radius": round(C.R_ACT2 + C.UNIT_R, 3),
        "act3_fan_radius": C.FAN_R,
        "act3_fan_adjacent_dist": round(fan, 3),
        "act3_fan_adjacent_gap": round(fan - C.UNIT_D, 3),
    })
    return problems, facts


# ---------------------------------------------------------------- DSL 结构

def dsl_checks(dsl, scene):
    problems = []
    size = len(dsl.encode("utf-8"))
    if size > DSL_MAX:
        problems.append("DSL %d B 超过服务上限 %d B" % (size, DSL_MAX))
    if "&" in dsl:
        problems.append("DSL 含字面 & （解析器不解码实体）")
    if "<Image" in dsl:
        problems.append("DSL 含 <Image —— 主体不能靠嵌入图片")
    for bad in (" <Row", " <Column", "<Row ", "<Column "):
        if bad in dsl:
            problems.append("DSL 含 %r（本服务 Column 的直接 Row 子节点不渲染）" % bad.strip())

    tree = parse_tags(dsl)
    nodes = walk(tree)
    by_tag = {}
    for el, parent in nodes:
        by_tag.setdefault(el["tag"], []).append((el, parent))

    # 说明：parse_tags 的 tree 是一个虚拟根，第一个孩子才是真正的 <Snapshot>
    snap = tree["children"][0] if tree["children"] else None
    if not (snap and snap["tag"] == "Snapshot" and snap["attrs"].get("type") == "png"):
        problems.append("根标签不是 Snapshot type=png")
    root_child = snap["children"][0] if snap and snap["children"] else None
    if not (root_child and root_child["tag"] == "Container"
            and root_child["attrs"].get("width") == "1600"
            and root_child["attrs"].get("height") == "1000"):
        problems.append("根 Container 不是 1600×1000")
    inner = root_child["children"][0] if root_child and root_child["children"] else None
    if not (inner and inner["tag"] == "Stack"):
        problems.append("根 Container 的子不是 Stack（根 Stack 直接做 Snapshot 子节点会渲染失败）")

    # 属性值：不出现 < 与 &
    for el, _p in nodes:
        for k, v in el["attrs"].items():
            if "<" in v or "&" in v:
                problems.append("%s 属性 %s 含 < 或 &" % (el["tag"], k))

    # 单孩子契约
    for tag in ("Container", "Positioned"):
        for el, _p in by_tag.get(tag, []):
            if len(el["children"]) > 1:
                problems.append("%s 有 %d 个子元素（服务只允许 1 个）"
                                % (tag, len(el["children"])))
    for el, parent in by_tag.get("Positioned", []):
        if not (parent and parent["tag"] in ("Stack", "IndexedStack")):
            problems.append("Positioned 的父不是 Stack：%s" % parent["tag"])

    # Text：只有总标题 + 三个幕名，共 4 个，且不落在节点/单元里
    texts = by_tag.get("Text", [])
    allowed = {scene["title"], scene["acts"][0]["name"],
               scene["acts"][1]["name"], scene["acts"][2]["name"]}
    if len(texts) != 4:
        problems.append("Text 数量 %d ≠ 4（只允许总标题 + 三个幕名）" % len(texts))
    for el, parent in texts:
        # 本服务的 Text 用 text="..." 属性给内容，不是元素内容
        t = (el["attrs"].get("text") or "").strip()
        if t not in allowed:
            problems.append("出现额外文字 %r（三幕内除幕名与总标题外不写解释文字）" % t)
        if el["attrs"].get("fontFamily") != C.FONT:
            problems.append("Text 未显式声明字体后备链")
    # 每个 Text 都在一个「标签框」里，而不是节点/单元里：
    # 标签框的唯一特征是它的外层 Container 带 alignment="CENTER" 且尺寸等于 label_box / title_box
    for el, parent in texts:
        if not (parent and parent["tag"] == "Container"
                and parent["attrs"].get("alignment") == "CENTER"):
            problems.append("Text 不在居中文本框内（可能被画进了节点或单元）")

    return problems, {"dsl_bytes": size}


# ---------------------------------------------------------------- 主流程

def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    out = {}
    ok = True
    for comp in ("A", "B"):
        scene, dsl = C.build(comp)
        gp, gf = geo_checks(scene)
        dp, df = dsl_checks(dsl, scene)
        # 同一句问题只留一条，附上命中次数
        def uniq(xs):
            seen, out2 = [], {}
            for x in xs:
                out2.setdefault(x, 0)
                out2[x] += 1
                seen.append(x)
            return [{"msg": k, "count": v} for k, v in out2.items()]
        # 写一份场景快照到临时目录，供检查器复核与后续对照
        ddir = SUITE_ROOT / "tmp" / RUN_ID / "A18" / "dsl"
        ddir.mkdir(parents=True, exist_ok=True)
        (ddir / ("check-%s.scene.json" % comp)).write_text(
            json.dumps(C.summary(scene), ensure_ascii=False, indent=1),
            encoding="utf-8")
        out[comp] = {"geo_problems": uniq(gp), "dsl_problems": uniq(dp),
                     "geo_facts": gf, "dsl_facts": df,
                     "ok": not gp and not dp}
        ok = ok and not gp and not dp
    print(json.dumps({"ok": ok, "compositions": out}, ensure_ascii=False, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
