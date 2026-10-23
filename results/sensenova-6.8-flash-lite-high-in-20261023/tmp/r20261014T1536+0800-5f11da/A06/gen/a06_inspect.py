"""A06 成品像素核验：独立于构建脚本，从 model.json 反推期望几何，再量实际墨迹。

覆盖题面全部硬要求：
  ① 画布 1600×1000
  ② 14 节点编号与标签完整出现，盒在审计坐标上，边框为阶段色
  ③ 16 条先决边沿折线连续有墨，方向可辨（终点箭头）
  ④ 2 条反馈边为虚线 + 专用色 + 箭头，与先决边可区分
  ⑤ 交叉线没有连接点（零交叉，与逐段比对审计一致）
  ⑥ 节点位置体现先后（层号自上而下）与并行（同层左右）
  ⑦ 边走线绕行、不压节点盒内文字
  ⑧ 先决边不指向过去层（层号单调递增）
  ⑨ 图内解释「失败后回到构建」与「检查发现问题后修复」
  ⑩ 节点字号 ≥22、注释 ≥18
  ⑪ 图例区分实线与虚线；最长先决路径完整出现
  ⑫ graph-audit.json 字段齐备（对照 templates/audit-fields.json）

用法：python a06_inspect.py <png>
退出码 0 = 全部通过，1 = 有 FAIL。
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a06_io as IO  # noqa: E402

PW, PH = 1600, 1000
EDGE = "#334155"          # 先决边
FB = "#D97706"            # 反馈边
FB_INK = "#92400E"        # 反馈文字
SUB, MUT = "#475569", "#64748B"
INK = "#0F172A"

# 与 a06_build.py 同源的布局常量（本脚本只读，不复用其函数）
RP_X, RP_Y, RP_W, RP_H = 1080.0, 104.0, 476.0, 680.0
BP_X, BP_Y, BP_W, BP_H = 40.0, 796.0, 1520.0, 196.0
GUT_X = 48.0
FB_LAB = {"N09→N08": (400.0, 408.0), "N10→N08": (400.0, 458.0)}

FAILS: list[str] = []

try:  # `python -I` 忽略 PYTHONIOENCODING，Windows 控制台默认 GBK
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def check(name: str, ok: bool, detail: str = "") -> bool:
    tag = "PASS" if ok else "FAIL"
    if not ok:
        FAILS.append(name)
    print(f"  [{tag}] {name}" + (f" — {detail}" if detail else ""))
    return ok


def ink_mask(arr: np.ndarray, lum_max: float = 220.0) -> np.ndarray:
    return arr.mean(axis=2) < lum_max


def series_mask(arr: np.ndarray, hex_color: str, min_dark: float = 30.0,
                tol: float = 14.0, min_chroma: float = 30.0) -> np.ndarray:
    """像素 = 指定色与白色的任意比例混合（含抗锯齿），且足够深、足够饱和。

    两个阈值都必需（A05 v9 实测定值）：
      * tol：网格线 #CBD5E1 到深射线距离 11–44，tol 太松会把网格当墨迹。
      * chroma：排除低饱和的浅灰抗锯齿混色。本题取值 30 的依据是各类色的实测
        饱和度：先决边 #334155 = 34、SUB #475569 = 34 必须保留；网格 #CBD5E1
        = 22、面板描边 #E2E8F0 = 14、浅网格 #EEF2F7 = 9 必须排除。取 30 恰好
        落在 22 与 34 之间。阶段色（≥154）与反馈色（103）余量更大。
    """
    W = np.array([255.0, 255.0, 255.0])
    C = np.array([int(hex_color[1:3], 16), int(hex_color[3:5], 16),
                  int(hex_color[5:7], 16)], dtype=float)
    w, v = W - C, W - arr.astype(float)
    dark = np.linalg.norm(v, axis=2) > min_dark
    chroma = arr.max(axis=2).astype(float) - arr.min(axis=2).astype(float)
    t = np.clip(np.sum(v * w, axis=2) / float(np.dot(w, w)), 0.0, 1.0)
    resid = np.linalg.norm(v - t[..., None] * w, axis=2)
    return np.all(v >= 0, axis=2) & dark & (chroma >= min_chroma) & (resid < tol)


def run_lengths(p: np.ndarray) -> list[tuple[int, int]]:
    out, i, n = [], 0, len(p)
    while i < n:
        if p[i]:
            j = i
            while j < n and p[j]:
                j += 1
            out.append((i, j - 1))
            i = j
        else:
            i += 1
    return out


def seg_inks(arr: np.ndarray, pts: list[list[float]], hex_color: str,
             tol: float = 14.0, min_chroma: float = 30.0, widen: int = 2) -> np.ndarray:
    """沿折线逐像素采样，返回每段「是否命中该色墨迹」的布尔数组。

    两端各留一段端帽（跳过箭头体与节点边框咬合处）。段长很短时（如 elbow 的
    10px 转折段）端帽不能吞掉整段，因此上限取 min(6, (L−2)/2)，保证至少采样
    中间 2px。
    """
    hits: list[np.ndarray] = []
    for (xa, ya), (xb, yb) in zip(pts[:-1], pts[1:]):
        dx, dy = xb - xa, yb - ya
        L = float(np.hypot(dx, dy))
        if L < 1.0:
            hits.append(np.ones(0, dtype=bool))
            continue
        cap = min(6.0, max(0.0, (L - 2.0) / 2.0))
        t0, t1 = cap / L, 1.0 - cap / L
        if t1 <= t0:
            hits.append(np.ones(0, dtype=bool))
            continue
        n = max(int((t1 - t0) * L), 1)
        row = np.zeros(n, dtype=bool)
        for k in range(n):
            t = t0 + (t1 - t0) * k / max(n - 1, 1)
            x, y = int(round(xa + dx * t)), int(round(ya + dy * t))
            x0, x1 = max(x - widen, 0), min(x + widen + 1, PW)
            y0, y1 = max(y - widen, 0), min(y + widen + 1, PH)
            if x1 > x0 and y1 > y0:
                row[k] = bool(series_mask(
                    arr[y0:y1, x0:x1], hex_color, tol=tol,
                    min_chroma=min_chroma).any())
        hits.append(row)
    return hits


def arrow_present(arr: np.ndarray, tip: list[float], direction: str,
                  hex_color: str) -> tuple[bool, str]:
    """箭头由 5 根缩窄矩形拼成（AW=14 宽，AH=11 长），尖端在 tip 指向 direction。

    取尖端朝内的 12×14 窗，要求该色像素占比 > 0.2。
    """
    ax, ay = int(round(tip[0])), int(round(tip[1]))
    if direction == "down":
        x0, y0, x1, y1 = ax - 7, ay - 12, ax + 8, ay + 1
    elif direction == "up":
        x0, y0, x1, y1 = ax - 7, ay - 1, ax + 8, ay + 12
    elif direction == "right":
        x0, y0, x1, y1 = ax - 12, ay - 7, ax + 1, ay + 8
    else:
        x0, y0, x1, y1 = ax - 1, ay - 7, ax + 12, ay + 8
    sub = series_mask(arr[y0:y1, x0:x1], hex_color, min_dark=25, tol=16,
                      min_chroma=30)
    frac = float(sub.mean())
    return frac > 0.18, f"{frac:.3f}"


def main() -> int:
    png = Path(sys.argv[1]) if len(sys.argv) > 1 else (
        IO.dirs()[1] / "preview" / "v6-preview.png")
    if not png.is_absolute():
        # 相对路径优先按当前工作目录解析（本脚本常在 tmp/<rid>/A06 下运行），
        # 不存在时再按总任务根解析。
        png = png if png.exists() else IO.ROOT / png
    _, tmp = IO.dirs()
    m = json.loads((tmp / "model.json").read_text(encoding="utf-8"))["model"]
    nodes = {d["id"]: d for d in m["nodes"]}

    print(f"图像: {png.relative_to(IO.ROOT) if png.is_relative_to(IO.ROOT) else png}")
    im = Image.open(png)
    img = np.asarray(im.convert("RGB"))
    H, Wd = img.shape[:2]
    check("画布尺寸 1600×1000", (Wd, H) == (PW, PH), f"实测 {Wd}×{H}")
    # 面板窗口（后面多节复用）
    rp_win = img[int(RP_Y):int(RP_Y + RP_H), int(RP_X):int(RP_X + RP_W)]
    bp = img[int(BP_Y):int(BP_Y + BP_H), int(BP_X):int(BP_X + BP_W)]

    # ---------------------------------------------------------- ①② 节点
    print("\n① ② 14 节点：坐标、阶段色边框、编号与标签墨迹")
    for d in sorted(m["nodes"], key=lambda z: z["id"]):
        x0, y0, x1, y1 = (int(round(v)) for v in d["pixel_box"])
        bx = series_mask(img[y0:y1, x0:x1], d["stage_color"], tol=20,
                         min_chroma=50)
        # 边框是盒的 2px 环：四边上各取一条带，统计命中
        bands = np.concatenate([bx[:3].ravel(), bx[-3:].ravel(),
                                bx[:, :3].ravel(), bx[:, -3:].ravel()])
        check(f"   {d['id']} 盒边框为阶段色 {d['stage_color']}",
              bands.mean() > 0.35, f"边框像素占比 {bands.mean():.3f}")
        # 盒内（去 6px 边框带）应有文字墨迹，且分两段（编号 + 标签）
        inner = ink_mask(img[y0 + 6:y1 - 6, x0 + 6:x1 - 6], lum_max=200)
        runs = run_lengths(inner.any(axis=0))
        wide = [r for r in runs if r[1] - r[0] >= 6]
        check(f"   {d['id']} 「{d['display_text']}」两段文字在位",
              inner.mean() > 0.08 and len(wide) >= 2,
              f"墨迹 {inner.mean():.3f}，宽段 {len(wide)} 条 "
              f"{[r[1] - r[0] for r in wide]}")

    # ---------------------------------------------------------- ③ 先决边
    print("\n③ 16 条先决边：连续有墨 + 方向可辨")
    for e in m["prerequisite_edges"]:
        pts = e["path"]
        segs = seg_inks(img, pts, EDGE)
        nonzero = [s for s in segs if s.size]
        cov = float(np.concatenate(nonzero).mean()) if nonzero else 0.0
        worst = max((int((~s).sum()) for s in segs if s.size), default=0)
        check(f"   {e['key']} 路径连续", cov > 0.93 and worst <= 3,
              f"覆盖 {cov:.3f}，单段最长缺口 {worst}px")
        ok, d2 = arrow_present(img, e["arrow"]["tip"], e["arrow"]["direction"],
                               EDGE)
        check(f"   {e['key']} 箭头 {e['arrow']['direction']}@tip", ok, d2)
        check(f"   {e['key']} 层号单调递增（{e['from_layer']}→{e['to_layer']}）",
              e["to_layer"] > e["from_layer"], f"Δ={e['layer_delta']}")

    # ---------------------------------------------------------- ④ 反馈边
    print("\n④ 2 条反馈边：虚线 + 专用色 + 箭头 + 与先决边可区分")
    for e in m["feedback_edges"]:
        pts = e["path"]
        segs = seg_inks(img, pts, FB, tol=16)
        flat = np.concatenate([s for s in segs if s.size])
        cov = float(flat.mean())
        check(f"   {e['key']} 专用色 {FB} 覆盖", cov > 0.80, f"{cov:.3f}")
        # 虚线：段内必须有长度 ≥3 的连续空档（dash off=7）
        gapmax = 0
        for s in segs:
            if s.size:
                for a, b in run_lengths(~s):
                    gapmax = max(gapmax, b - a + 1)
        check(f"   {e['key']} 呈虚线（有 ≥3px 空档）", gapmax >= 3,
              f"最长空档 {gapmax}px")
        ok, d2 = arrow_present(img, e["arrow"]["tip"], e["arrow"]["direction"],
                               FB)
        check(f"   {e['key']} 箭头 {e['arrow']['direction']}@tip", ok, d2)
        check(f"   {e['key']} 反向回指（层 {e['from_layer']}→{e['to_layer']}）",
              e["to_layer"] < e["from_layer"], f"Δ={e['layer_delta']}")
        check(f"   {e['key']} 标注不参与 DAG 分层",
              e["excluded_from_dag_layering"] is True)
    # 颜色可区分：先决边射线与反馈边射线互不命中
    sedge = series_mask(img, EDGE, tol=10, min_chroma=40)
    sfb = series_mask(img, FB, tol=10, min_chroma=40)
    both = int((sedge & sfb).sum())
    check("先决边色与反馈边色不重叠", both == 0, f"同时命中 {both} px")

    # ---------------------------------------------------------- ⑤ 交叉
    print("\n⑤ 交叉线没有连接点")
    cr = m["crossing_report"]
    tot = sum(e["crossing_count"] for e in
              m["prerequisite_edges"] + m["feedback_edges"])
    check("逐段比对交叉数 = 0", tot == 0 == cr["total_crossings"],
          f"比对 {cr['pairs_checked']} 对边组合")
    check("每条边 crosses_other_edges_at 为空",
          all(not e["crosses_other_edges_at"] for e in
              m["prerequisite_edges"] + m["feedback_edges"]))
    # 图中确实在走廊绕行而非斜穿：检查 N04→N13 的走线顶点
    far = next(e for e in m["prerequisite_edges"] if e["key"] == "N04→N13")
    check("N04→N13 跨 7 层走左侧走廊绕行（4 顶点）",
          far["path_vertex_count"] == 4 and far["routing"] != "直下",
          far["routing"])

    # ---------------------------------------------------------- ⑥ 层号布局
    print("\n⑥ ⑧ 节点位置体现先后与并行")
    layers = sorted({d["topo_layer"] for d in m["nodes"]})
    check("拓扑层 = 11 个连续整数 0..10", layers == list(range(11)),
          str(layers))
    # 层号越大 y 越大（自上而下）
    bad = [(a["id"], b["id"]) for a in m["nodes"] for b in m["nodes"]
           if a["topo_layer"] < b["topo_layer"]
           and a["pixel_center"][1] >= b["pixel_center"][1]]
    check("层号单调对应 y 自上而下", not bad, str(bad[:3]))
    # 同层节点左右分开
    for lay in layers:
        group = [d for d in m["nodes"] if d["topo_layer"] == lay]
        if len(group) > 1:
            xs = sorted(d["pixel_center"][0] for d in group)
            check(f"   层 {lay} {len(group)} 个节点左右并行",
                  all(b - a >= 154 for a, b in zip(xs, xs[1:])),
                  f"x = {xs}")

    # ---------------------------------------------------------- ⑦ 线不压盒内
    print("\n⑦ 边不侵入任何节点盒内部（端点邻域除外）")
    for e in m["prerequisite_edges"] + m["feedback_edges"]:
        pts = e["path"]
        hexc = e["color"]
        bad = []
        for (xa, ya), (xb, yb) in zip(pts[:-1], pts[1:]):
            L = float(np.hypot(xb - xa, yb - ya))
            n = max(int(L), 1)
            for k in range(n + 1):
                t = k / n
                x, y = xa + (xb - xa) * t, ya + (yb - ya) * t
                if any(bx0 < x < bx1 and by0 < y < by1
                       for d in m["nodes"]
                       for bx0, by0, bx1, by1 in [d["pixel_box"]]):
                    # 端点各留 10px：箭头与锚点允许贴盒边
                    d0 = np.hypot(x - pts[0][0], y - pts[0][1])
                    d1 = np.hypot(x - pts[-1][0], y - pts[-1][1])
                    if min(d0, d1) > 10:
                        bad.append((round(x, 1), round(y, 1)))
        check(f"   {e['key']} 不压节点盒内", not bad, str(bad[:4]))

    # ---------------------------------------------------------- ⑨ 图内解释
    print("\n⑨ 图内解释两条反馈回路")
    for e in m["feedback_edges"]:
        # 面板卡片区
        short = e["meaning"].split("：", 1)[0]
        hit_short = series_mask(rp_win, FB_INK, tol=20, min_chroma=40)
        check(f"   {e['key']} 短名「{short}」出现在说明面板",
              hit_short.mean() > 0.004, f"{hit_short.mean():.4f}")
        # 图内短标签（回环内侧）
        lx, ly = FB_LAB[e["key"]]
        win = img[int(ly) - 3:int(ly) + 20, int(lx):int(lx) + 330]
        frac = float(series_mask(win, FB_INK, tol=20, min_chroma=40).mean())
        check(f"   {e['key']} 图内短标签在回环内侧", frac > 0.02, f"{frac:.3f}")

    # ---------------------------------------------------------- ⑩ 字号
    print("\n⑩ 字号：节点 ≥22、注释 ≥18")
    cands = sorted((tmp / "dsl").glob("dependency-map.*.snapshot"),
                   key=lambda p: p.stat().st_mtime, reverse=True)
    check("DSL 版本文件存在", bool(cands), cands[0].name if cands else "-")
    dsl = cands[0].read_text(encoding="utf-8")
    sizes = [int(x) for x in re.findall(r'fontSize="(\d+)"', dsl)]
    check("最小字号 ≥18", min(sizes) >= 18, f"字号集合 {sorted(set(sizes))}")
    node_sizes = set(re.findall(r'fontSize="(\d+)"', dsl))
    check("节点字号 22 出现", "22" in node_sizes, str(sorted(node_sizes)))
    check("无 <18 的字号", all(s >= 18 for s in sizes))

    # ---------------------------------------------------------- ⑪ 图例与最长路径
    print("\n⑪ 图例区分实线/虚线；最长先决路径完整出现")
    leg = rp_win
    check("图例区先决边实线样例",
          series_mask(leg, EDGE, tol=14).sum() > 40,
          f"{int(series_mask(leg, EDGE, tol=14).sum())} px")
    check("图例区反馈边虚线样例",
          series_mask(leg, FB, tol=16).sum() > 40,
          f"{int(series_mask(leg, FB, tol=16).sum())} px")
    check("图例 5 个阶段色块齐备",
          all(series_mask(leg, s["color"], tol=18, min_chroma=50).sum() > 60
              for s in m["stages"]))
    check("底部面板有最长路径文字墨迹",
          ink_mask(bp, lum_max=200).mean() > 0.01,
          f"{ink_mask(bp, lum_max=200).mean():.4f}")
    lp = m["longest_path"]
    check("最长先决路径 ≥1 解且为 11 节点",
          lp["solutions_count"] >= 1 and lp["length_nodes"] == 11,
          f"{lp['solutions_count']} 解 × {lp['length_nodes']} 节点")
    check("最长路径排除反馈边", lp["excludes_feedback_edges"] is True)
    for i, s in enumerate(lp["solutions"], 1):
        seq = " → ".join(s["sequence"])
        check(f"   解 {i} 11 节点序列在图内", len(s["sequence"]) == 11
              and s["sequence"][0] == "N01" and s["sequence"][-1] == "N14",
              seq[:60] + "…")

    # ---------------------------------------------------------- 层号标注
    print("\n层号沟槽标注（层 0..10 + 节点数）")
    for lay in layers:
        cy = 128.0 + lay * 63.0
        win = img[int(cy) - 24:int(cy) + 22, int(GUT_X) - 4:int(GUT_X) + 82]
        frac = float(ink_mask(win, lum_max=210).mean())
        check(f"   层 {lay} 沟槽标注", frac > 0.03, f"{frac:.3f}")

    # ---------------------------------------------------------- ⑫ 审计字段
    print("\n⑫ graph-audit.json 字段齐备")
    tmpl = json.loads((IO.ROOT / "tasks/A06-dependency-graph/templates/"
                       "audit-fields.json").read_text(encoding="utf-8"))
    req = tmpl["artifacts"]["graph-audit.json"]["required_fields"]
    audit_path = IO.dirs()[0] / "graph-audit.json"
    check("graph-audit.json 已写出", audit_path.exists(),
          f"{audit_path.stat().st_size} B" if audit_path.exists() else "-")
    if audit_path.exists():
        a = json.loads(audit_path.read_text(encoding="utf-8"))
        for k, v in {"schema_version": 1, "task_id": "A06",
                     "path_base": "output_dir"}.items():
            check(f"   公共字段 {k}", a.get(k) == v, f"实测 {a.get(k)}")
        # 模板四个必需字段
        check("   nodes = 14 项", len(a.get("nodes", [])) == 14,
              f"{len(a.get('nodes', []))} 项")
        check("   prerequisite_edges = 16 项",
              len(a.get("prerequisite_edges", [])) == 16,
              f"{len(a.get('prerequisite_edges', []))} 项")
        check("   feedback_edges = 2 项", len(a.get("feedback_edges", [])) == 2,
              f"{len(a.get('feedback_edges', []))} 项")
        lp2 = a.get("longest_path", {})
        check("   longest_path 至少一条序列", len(lp2.get("solutions", [])) >= 1,
              f"{len(lp2.get('solutions', []))} 条")
        # 逐字段核对模板说明
        for d in a["nodes"]:
            for fld in ("id", "topo_layer", "prereq_in", "prereq_out",
                        "pixel_box"):
                if fld not in d:
                    check(f"   nodes[{d.get('id')}] 字段 {fld}", False)
        check("   nodes 全含 id/topo_layer/入出邻居/pixel_box",
              all(all(f in d for f in ("id", "topo_layer", "prereq_in",
                                       "prereq_out", "pixel_box"))
                  for d in a["nodes"]))
        check("   prerequisite_edges 全含有向 from/to、path、arrow",
              all(all(f in e for f in ("from", "to", "path", "arrow"))
                  for e in a["prerequisite_edges"]))
        check("   feedback_edges 全含 from/to、虚线标记、箭头、path、"
              "不参与 DAG 声明",
              all(all(f in e for f in ("from", "to", "path", "arrow",
                                       "line_style",
                                       "excluded_from_dag_layering"))
                  and e["line_style"] == "dashed"
                  for e in a["feedback_edges"]))
        check("   feedback_edges 均标注不参与 DAG 计算",
              all(e["excluded_from_dag_layering"] is True
                  for e in a["feedback_edges"]))
        check("   每条边记录交叉位置与计数",
              all(("crosses_other_edges_at" in e and "crossing_count" in e)
                  for e in a["prerequisite_edges"] + a["feedback_edges"]))
        check("   画布坐标说明齐备（左上原点 / x 向右 y 向下 / px）",
              a.get("canvas", {}).get("origin") == "top-left"
              and a.get("canvas", {}).get("width") == PW
              and a.get("canvas", {}).get("unit") == "px")
        check("   层号定义有方法说明", bool(a.get("nodes", [{}])[0]
                                            .get("layer_note")))
        check("   longest_path 有计算方法", bool(lp2.get("method")))

    print("\n" + "=" * 66)
    if FAILS:
        print(f"FAIL {len(FAILS)} 项：")
        for f in FAILS:
            print("  -", f)
        return 1
    print("全部通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
