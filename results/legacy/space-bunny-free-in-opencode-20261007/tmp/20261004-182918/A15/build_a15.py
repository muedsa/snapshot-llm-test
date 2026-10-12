"""A15 builder: rebuild the 1440x900 reference dashboard with Snapshot DSL.

Geometry constants live in spec_a15.py and were all measured from
tasks/A15-reference-reconstruction/inputs/reference.png with PIL.  Text content and
values come from inputs/content.json.  Typography (family + size) was chosen by an
ink-density calibration against the reference (calib5_a15.py -> TYPO), and the
per-element ink offset (dx, dy) is refined by verify_render.py -> text-offsets.json.

The reference PNG is only observed, never embedded: no <Image> element is used
anywhere in this DSL.
"""
import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TMP = os.path.join(ROOT, "tmp", RUN, "A15")
OUT = os.path.join(ROOT, "outputs", RUN, "A15")
INPUTS = os.path.join(ROOT, "tasks", "A15-reference-reconstruction", "inputs")
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
sys.path.insert(0, TMP)
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import spec_a15 as S  # noqa: E402

C, G = S.C, S.G
W, H = G["canvas"]
snapkit.configure("A15", OUT, TMP)
CONTENT = json.load(open(os.path.join(INPUTS, "content.json"), encoding="utf-8"))

IB = "Inter Black"
EB = "Inter Extra Bold"
SB = "Inter Semi Bold"
MD = "Inter Medium"
# family / size chosen by ink-density calibration, constrained to <=3px ink-size error
TYPO = {
    "title": (EB, 31.5), "subtitle": (S.INTER, 18), "button_text": (EB, 16.25),
    "kpi1_label": (EB, 13), "kpi2_label": (EB, 13), "kpi3_label": (EB, 13),
    "kpi1_value": (EB, 31), "kpi2_value": (EB, 31), "kpi3_value": (EB, 31),
    "kpi1_change": (EB, 15.25), "kpi2_change": (EB, 15.25), "kpi3_change": (EB, 15.25),
    "chart_title": (SB, 22.75), "chart_period": (S.INTER, 17), "chart_unit": (S.INTER, 13),
    "ytick_120": (S.INTER, 13), "ytick_90": (S.INTER, 13), "ytick_60": (S.INTER, 13),
    "ytick_30": (S.INTER, 13), "ytick_0": (S.INTER, 13),
    "month_Apr": (S.INTER, 14), "month_May": (S.INTER, 14), "month_Jun": (S.INTER, 14),
    "month_Jul": (S.INTER, 14), "month_Aug": (S.INTER, 14), "month_Sep": (S.INTER, 14),
    "act_title": (SB, 22.5),
    "act1_title": (EB, 16.65), "act2_title": (EB, 16.65), "act3_title": (EB, 16.65),
    "act1_time": (S.INTER, 14), "act2_time": (S.INTER, 14), "act3_time": (S.INTER, 14),
    "table_title": (SB, 22.5),
    "ch_project": (EB, 11.5), "ch_owner": (EB, 11.5), "ch_status": (EB, 11.5),
    "ch_due": (EB, 11.5),
    "r1_proj": (EB, 15.75), "r2_proj": (EB, 15.75), "r3_proj": (EB, 15.75),
    "r1_owner": (S.INTER, 16), "r2_owner": (S.INTER, 16), "r3_owner": (S.INTER, 16),
    "r1_status": (EB, 12.5), "r2_status": (EB, 12.5), "r3_status": (EB, 12.5),
    "r1_due": (S.INTER, 16), "r2_due": (S.INTER, 16), "r3_due": (S.INTER, 16),
    "footer": (S.INTER, 13),
    "brand": (IB, 17),
    # selected nav label is genuinely heavier in the reference (density ratio
    # 1.11 vs Semi Bold, 1.12 vs Inter regular for the unselected ones)
    "nav_overview": (EB, 19), "nav_projects": (S.INTER, 19),
    "nav_analytics": (S.INTER, 19), "nav_settings": (S.INTER, 19),
    "side_label": (EB, 12.5), "side_member": (S.INTER, 16), "side_manage": (MD, 13.75),
}
# (key, ink_left, ink_top) measured from the reference
INK = {k: (il, it) for k, _, il, it, _, _, _, _ in S.TEXT}
LS = {k: l for k, _, _, _, _, _, _, l in S.TEXT}

OFF_PATH = os.path.join(TMP, "text-offsets.json")
DEFAULT_OFF = {}
OFF = dict(DEFAULT_OFF)
if os.path.exists(OFF_PATH):
    OFF.update(json.load(open(OFF_PATH, encoding="utf-8")))

layout = {}


def T(key, text, ck, ls=None):
    font, size = TYPO[key]
    dx, dy = OFF.get(key, (0, 3))
    il, it = INK[key]
    x = il - dx
    y = it - dy
    th = round(size * 1.9, 1)
    tw = min(620, W - x)
    use_ls = LS[key] if ls is None else ls
    extra = {"letterSpacing": use_ls} if use_ls else None
    layout[key] = {"box": [round(x, 2), round(y, 2), round(tw, 2), th],
                   "ink_target": [il, it], "text": text, "font": font, "size": size,
                   "ls": use_ls, "dx": dx, "dy": dy}
    return D.text_el(text, x=x, y=y, w=tw, h=th, color=C[ck], size=size,
                     font=font, extra=extra)


kids = []
A = kids.append

# ============================================================ sidebar
A(D.box(0, 0, G["sidebar_w"], H, color=C["sidebar_bg"]))
ox, oy, ow, oh, orad = G["logo_outer"]
A(D.box(ox, oy, ow, oh, color=C["mint"], radius=orad))
hx_, hy_, hw_, hh_, hrad = G["logo_hole"]
A(D.box(hx_, hy_, hw_, hh_, color=C["sidebar_bg"], radius=hrad))
A(T("brand", CONTENT["brand"], "white"))

nx, ny, nw, nh, nrad = G["nav_pill"]
A(D.box(nx, ny, nw, nh, color=C["nav_pill"], radius=nrad))
NAV_KEYS = ["nav_overview", "nav_projects", "nav_analytics", "nav_settings"]
for i, (key, (label, cy)) in enumerate(zip(NAV_KEYS, G["nav_items"])):
    assert label == CONTENT["navigation"][i], (label, CONTENT["navigation"][i])
    A(D.box(G["nav_dot_x"], cy - 5, 10, 10, radius=5,
            color=C["nav_dot_on"] if i == 0 else C["nav_dot_off"]))
    A(T(key, label, "white" if i == 0 else "nav_label_off"))

sx, sy, sw, sh, srad = G["side_card"]
A(D.box(sx, sy, sw, sh, color=C["side_card"], radius=srad))
A(T("side_label", CONTENT["workspace_info"][0], "mint"))
A(T("side_member", CONTENT["workspace_info"][1], "white"))
A(T("side_manage", CONTENT["workspace_info"][2], "side_manage"))

# ============================================================ page header
A(T("title", CONTENT["title"], "strong"))
A(T("subtitle", CONTENT["subtitle"], "muted"))
bx, by, bw, bh, brad = G["button"]
A(D.box(bx, by, bw, bh, color=C["accent"], radius=brad))
A(T("button_text", CONTENT["button"], "white"))

# ============================================================ KPI cards
for i, (cx, cy, cw, ch) in enumerate(G["kpi_cards"]):
    k = CONTENT["kpis"][i]
    A(D.box(cx, cy, cw, ch, color=C["card"], radius=G["card_r"],
            border="1 SOLID " + C["card_border"]))
    cl = cx + 24
    inkl, inkt = INK["kpi%d_label" % (i + 1)]
    A(T("kpi%d_label" % (i + 1), k["label"], "muted"))
    A(T("kpi%d_value" % (i + 1), k["value"], "strong"))
    A(T("kpi%d_change" % (i + 1), k["change"], "green"))
    _ = (cl, inkl, inkt)

# ============================================================ chart card
cx_, cy_, cw_, ch_ = G["chart_card"]
A(D.box(cx_, cy_, cw_, ch_, color=C["card"], radius=G["card_r"],
        border="1 SOLID " + C["card_border"]))
A(T("chart_title", CONTENT["chart_title"], "strong"))
A(T("chart_period", CONTENT["chart_period"], "muted"))
A(T("chart_unit", CONTENT["chart_unit"], "muted"))

gx0, gx1 = G["grid_x"]
gw = gx1 - gx0 + 1
for gy in G["grid_y"]:
    A(D.box(gx0, gy, gw, 1, color=C["grid"]))

# bars: height strictly proportional to the value (1.2 px per Y thousand)
bar_geom = []
for i, v in enumerate(G["bar_values"]):
    assert v == CONTENT["chart_values"][i]
    bh_ = round(v * G["px_per_unit"], 2)
    by_ = round(G["baseline_y"] - bh_, 2)
    bx_ = G["bar_x"][i]
    A(D.box(bx_, by_, G["bar_w"], bh_, color=C["accent"], radius=G["bar_r"]))
    bar_geom.append({"month": CONTENT["months"][i], "value": v, "x": bx_, "y": by_,
                     "w": G["bar_w"], "h": bh_})

TICKS = [("ytick_120", "120", 405), ("ytick_90", "90", 441), ("ytick_60", "60", 477),
         ("ytick_30", "30", 513), ("ytick_0", "0", 549)]
for i, (key, lbl, gy) in enumerate(TICKS):
    assert str(CONTENT["chart_ticks"][len(TICKS) - 1 - i]) == lbl
    assert gy == G["grid_y"][i], (gy, G["grid_y"])
    A(T(key, lbl, "muted"))

for m in CONTENT["months"]:
    A(T("month_" + m, m, "muted"))

# ============================================================ activity card
ax_, ay_, aw_, ah_ = G["act_card"]
A(D.box(ax_, ay_, aw_, ah_, color=C["card"], radius=G["card_r"],
        border="1 SOLID " + C["card_border"]))
A(T("act_title", CONTENT["activity_title"], "strong"))
ACT_DOTS = ["dot_amber", "accent", "green"]
for i, (title, tm) in enumerate(CONTENT["activity"]):
    A(D.box(1054, 397 + i * 60, 10, 10, radius=5, color=C[ACT_DOTS[i]]))
    A(T("act%d_title" % (i + 1), title, "strong"))
    A(T("act%d_time" % (i + 1), tm, "muted"))

# ============================================================ table card
tx_, ty_, tw_, th_ = G["table_card"]
A(D.box(tx_, ty_, tw_, th_, color=C["card"], radius=G["card_r"],
        border="1 SOLID " + C["card_border"]))
A(T("table_title", CONTENT["table_title"], "strong"))

hx0, hy0, hw0, hh0 = G["thead"]
A(D.box(hx0, hy0, hw0, hh0, color=C["band"], radius=G["thead_r"]))
for key, col in zip(("ch_project", "ch_owner", "ch_status", "ch_due"),
                    CONTENT["table_columns"]):
    A(T(key, col, "colhead"))

for sy_ in G["rowsep_y"]:
    A(D.box(284, sy_, 1090, 1, color=C["rowsep"]))

px_, py0_, pw_, ph_, pr_ = G["pill"]
PILL_BG = ["pill_ip_bg", "pill_rv_bg", "pill_dn_bg"]
PILL_TX = ["pill_ip_tx", "pill_rv_tx", "pill_dn_tx"]
for i, row in enumerate(CONTENT["rows"]):
    A(D.box(px_, G["pill_y"][i], pw_, ph_, color=C[PILL_BG[i]], radius=pr_))
    A(T("r%d_proj" % (i + 1), row[0], "strong"))
    A(T("r%d_owner" % (i + 1), row[1], "muted"))
    A(T("r%d_status" % (i + 1), row[2], PILL_TX[i]))
    A(T("r%d_due" % (i + 1), row[3], "due"))

# ============================================================ footer
A(T("footer", CONTENT["footer"], "footer"))

# ============================================================ emit
# Single root Container (the canvas) holding one Stack; every child is a
# Positioned with explicit left/top/width/height, so DSL coordinates == the
# measured pixel coordinates.
root = D.el("Container", {"width": W, "height": H},
            [D.el("Stack", {"fit": "EXPAND"}, kids)])
dsl = ('<Snapshot type="png" background="%s">\n%s\n</Snapshot>\n' % (C["main_bg"], root))
os.makedirs(os.path.join(TMP, "drafts"), exist_ok=True)
with open(os.path.join(TMP, "drafts", "build-a15.snapshot"), "w",
          encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)
json.dump({"text_layout": layout, "bars": bar_geom},
          open(os.path.join(TMP, "layout.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

final = "--preview" not in sys.argv
r = snapkit.render(dsl, "reconstructed.png", "reconstructed.snapshot", final=final)
print("render ok=%s status=%s bytes=%s" % (r.get("ok"), r.get("status"), r.get("bytes")))
if not r.get("ok"):
    print("ERROR:", r.get("error"))
    print("resp file:", r.get("response_file"))
for w in D.warnings():
    print("WARN", w)
print("elements:", len(kids), "texts:", len(layout), "dsl bytes:", len(dsl.encode()))
