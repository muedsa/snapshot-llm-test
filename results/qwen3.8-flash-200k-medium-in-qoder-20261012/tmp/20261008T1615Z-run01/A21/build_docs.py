"""A21：从生成器自身状态导出 design-tokens.json / content-map.json（不手抄）。"""
import importlib.util
import json
import os
import sys
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"]).resolve()
rid = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(root / "tmp" / rid / "_suite" / "scripts"))
TMP = root / "tmp" / rid / "A21"
spec = importlib.util.spec_from_file_location("gl", str(TMP / "gen_launch.py"))
gl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gl)

ROUND = int(sys.argv[1]) if len(sys.argv) > 1 else 1
planes = {}
zones = {}
audits = {}
for name, fn in sorted(gl.BUILDERS[ROUND].items()):
    gl.PLANE.clear()
    dsl, w, h, ext = fn()
    gl.check_required(gl.PLANE, name, ROUND)
    audits[name] = gl.audit_layout(gl.PLANE, (w, h))
    planes[name] = dict(gl.PLANE)
    zones[name] = {"canvas": [w, h], "extension_zones": ext,
                   "dsl_bytes": len(dsl.encode("utf-8"))}

MARK = ["plate-1", "plate-2", "plate-3", "source", "ray-1", "ray-2"]
ribbon = {img: {"plate_centers": [p["center_px"] for t, p in plane.items()
                                  if t.startswith("bg.plate")],
                "plate_size_px": next(iter(p["size_px"] for t, p in plane.items()
                                           if t.startswith("bg.plate"))),
                "rotation_deg": -22}
          for img, plane in planes.items()}
tokens = {
    "round": ROUND,
    "brand": {"name_cn": "叠光", "name_latin": "Layerlight"},
    "colors": gl.C,
    "alpha_suffix": gl.A,
    "color_usage_note": "8 位 hex 的 alpha 由服务真实合成（A21 探测请求 probe02 像素核对："
                        "#FF000080 压在 #0B1020 上得到 (133,8,16)，等于 50% 合成值）；"
                        "Container 的 opacity 属性与 <Opacity value=...> 均被忽略，故未使用。",
    "fonts": gl.TOK["font"],
    "font_note": "Doc 默认 fontFamily=\"Inter,Noto Sans CJK SC\"，中西文混排由该回退链完成；"
                 "本题未使用其他字族。",
    "type_scale_px": gl.S,
    "min_size_rule": {"title": gl.TOK["minTitlePx"], "other": gl.TOK["minOtherPx"],
                      "enforced_by": "gen_launch.fl() 断言，逐元素核验"},
    "spacing": gl.TOK["space"],
    "brand_mark": {
        "component_count": len(MARK),
        "components": MARK,
        "geometry": {k.replace("mark.", ""): planes["launch-portrait"][k]
                     for k in ["mark." + m for m in MARK]},
        "note": "两图使用同一个 brand_mark() 调用，只有缩放系数不同（竖版 132、横版 108），"
                "因此图形语言完全一致。",
    },
    "background_ribbon": {
        "derived_from": "brand_mark 的同一角度（-22°）与同一相对位移，只是整体放大 3.6~4.0 倍",
        "per_image": ribbon,
    },
    "extension_zones": zones,
}
if ROUND == 3:
    tokens["theme"] = {
        "name": "light",
        "changed_from_round": 2,
        "canvas_bg": gl.LIGHT["bg"],
        "text_colors": {k: gl.LIGHT[k] for k in
                        ("ink", "muted", "primary", "cyan")},
        "unchanged": "品牌名/文案/断行/字号层级/版式坐标/品牌图形（同一 brand_mark 与"
                     "light_ribbon 调用，角度 -22°、相对位移、构件数 6 全不变）",
        "decoration": "叠光板仍用品牌三色 #3D6BFF / #7C5CFF / #22D3EE，只是把 alpha 从"
                      " 1A/1A/14/1F 提到 3A/3A/33/4D：浅色底亮度 0.93，深色主题那套透明度"
                      "压在上面几乎不可见（实测合成后与底色亮度差只有 0.11）。",
        "ring": "ONLINE LAUNCH 胶囊描边由 mix(#22D3EE, bg, 0.65) 改为"
                " mix(#0E7490, bg, 0.35)：浅色下亮青描边对比不足，改用品牌深青。",
        "hairline": gl.LIGHT["hairline"],
        "brand_dot": "品牌图形的“光源点”取 C[ink]，因此换主题时自动由白转深，"
                     "不需要单独维护两套颜色。",
        "contrast_rule": "所有文字与实测合成背景 >= 4.5:1（见 contrast_audit）",
        "tagline": {"text": gl.TOK["tagline"], "font_px": 30,
                    "min_required_px": 24, "color": gl.LIGHT["primary"],
                    "placement": "两图都紧贴标题块之下、分隔线之上，位于网址上方"},
    }

def locate(plane, r):
    """在按渲染顺序拼接的全文里定位必需文案，回指它由哪些元素（可能跨行）合成。"""
    seq = [(t, v["text"]) for t, v in plane.items() if "text" in v]
    joined = "".join(s for _, s in seq)
    i = joined.find(r)
    if i < 0:
        return []
    end, out, pos = i + len(r), [], 0
    for t, s in seq:
        a, b = pos, pos + len(s)
        if a < end and b > i:
            out.append({"element": t, "renders": s,
                        "covers": "whole" if (a >= i and b <= end) else "part"})
        pos = b
    return out


required_map = {}
for r in gl.REQUIRED[ROUND]:
    hits = {img: locate(plane, r) for img, plane in planes.items()}
    for img, found in hits.items():
        assert found, "%s 缺必需文案 %r" % (img, r)
    required_map[r] = hits

def zone_box(z):
    x, y, w, h = z
    return (x, y, x + w, y + h)


def hits_zone(box, z):
    a, b = box, zone_box(z)
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def elem_box(v):
    if "box_px" in v:
        x, y, w, h = v["box_px"]
        return (x, y, x + w, y + h)
    if "center_px" in v and "size_px" in v:      # 旋转板按外接矩形保守判定
        cx, cy = v["center_px"]
        import math
        wd, ht = v["size_px"]
        r = math.radians(abs(v.get("rotation_deg", 0)))
        half_w = (wd * math.cos(r) + ht * math.sin(r)) / 2
        half_h = (wd * math.sin(r) + ht * math.cos(r)) / 2
        return (cx - half_w, cy - half_h, cx + half_w, cy + half_h)
    if "from_px" in v:
        return (min(v["from_px"][0], v["to_px"][0]), min(v["from_px"][1], v["to_px"][1]),
                max(v["from_px"][0], v["to_px"][0]), max(v["from_px"][1], v["to_px"][1]))
    if "diameter_px" in v:
        cx, cy = v["center_px"]
        rr = v["diameter_px"] / 2
        return (cx - rr, cy - rr, cx + rr, cy + rr)
    return None


zone_check = {}
for img, plane in planes.items():
    zs = zones[img]["extension_zones"]
    per = {}
    for zname, z in zs.items():
        per[zname] = [tag for tag, v in plane.items()
                      if elem_box(v) and hits_zone(elem_box(v), z)]
    zone_check[img] = {"zones_px": zs, "elements_inside": per,
                       "clean": all(not x for x in per.values())}
assert all(c["clean"] for c in zone_check.values()), zone_check

SPLIT_NOTE = {
    1: {"string": "让复杂信息变得清晰",
        "reason": "10 个汉字在 96px 下需 979px 宽，竖版可用宽仅 904px，"
                  "因此按语义在两处断行；两图断行位置与字号完全一致。",
        "lines": ["让复杂信息", "变得清晰"]},
    2: {"string": "当所有信息都想成为标题：让复杂信息变得清晰的结构化方法",
        "reason": "27 个汉字在 64px 下整句需 1763px，远超两图可用宽；按语义在冒号与"
                  "“的”字后断成 3 行（12/10/5 字），最长行 783px 仍小于竖版 904px 与"
                  "横版标题列 840px。字号 64px 高于本轮要求的 48px 下限，"
                  "未使用任何横向缩放或字距压缩，因此不存在“变形压窄文字”。",
        "lines": gl.TITLE_R02},
}
SPLIT_NOTE[3] = dict(SPLIT_NOTE[2], unchanged_from=2,
                     note="第 3 轮只换主题色，标题文案/断行/字号与第 2 轮逐字一致。")

content = {
    "round": ROUND,
    "extension_zone_audit": zone_check,
    "collision_audit": audits,
    "canvases": {k: v["canvas"] for k, v in zones.items()},
    "required_strings": required_map,
    "title_line_split": SPLIT_NOTE[ROUND],
    "elements": planes,
    "no_placeholder_text": {
        "checked": True,
        "method": "遍历所有文字元素，确认没有“待添加/占位/TBD/LOGO 位”等字样；"
                  "顶底扩展区以空白本身表达，不写说明文字。",
        "placeholder_hits": [
            {"image": img, "element": tag, "text": v["text"]}
            for img, plane in planes.items() for tag, v in plane.items()
            if "text" in v and any(k in v["text"] for k in
                                   ("待添加", "占位", "TBD", "LOGO", "预留"))],
    },
}

out = TMP / ("layouts" if ROUND == 1 else "layouts/round-%02d" % ROUND)
ink_path = out / "ink-audit.json"
if ink_path.exists():
    content["collision_audit_measured_from_png"] = json.loads(
        ink_path.read_text(encoding="utf-8"))["images"]
ca_path = out / "contrast-audit.json"
if ca_path.exists():
    ca = json.loads(ca_path.read_text(encoding="utf-8"))
    content["contrast_audit"] = {
        "method": ca["method"], "threshold": ca["threshold"],
        "round": ca["round"],
        "body_samples": {
            img: [{"element": e["element"], "text": e["text"],
                   "font_px": e["font_px"], "text_color": e["text_color"],
                   "measured_bg": e["measured_bg"],
                   "analytic_bg": e["analytic_bg"],
                   "layers_under_text": e["layers_under_text"],
                   "contrast": e["contrast_vs_measured_bg"]}
                  for e in sorted(v["elements"],
                                  key=lambda x: x["contrast_vs_measured_bg"])[:8]]
            for img, v in ca["images"].items()},
        "summary": {img: {"text_elements": v["count"],
                          "min_contrast": v["min_contrast"],
                          "canvas_base_color": v["canvas_base_color"],
                          "decor_layers_checked": v["decor_layers_checked"],
                          "decor_max_channel_delta": v["decor_max_channel_delta"],
                          "text_over_any_plate": v["text_over_any_plate"],
                          "all_pass": all(e["pass"] for e in v["elements"])}
                    for img, v in ca["images"].items()},
        "full_report_file": "contrast-audit.json",
    }
out.mkdir(parents=True, exist_ok=True)
(out / "design-tokens.json").write_text(json.dumps(tokens, ensure_ascii=False, indent=1),
                                        encoding="utf-8")
(out / "content-map.json").write_text(json.dumps(content, ensure_ascii=False, indent=1),
                                      encoding="utf-8")
print("tokens/content-map ->", out)
print("必需文案命中：", {k: {i: len(v) for i, v in hits.items()}
                        for k, hits in required_map.items()})
print("占位文字命中：", content["no_placeholder_text"]["placeholder_hits"])
