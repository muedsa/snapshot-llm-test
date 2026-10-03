"""B05 case builders. Each function returns a complete, self-contained Snapshot DSL string."""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bkit import Doc, CJK, MONO, INTER, tw  # noqa: E402
import style as S  # noqa: E402


def tide_at(curve, t):
    """Linear interpolation of the tide curve at hour t (shared by all screens)."""
    lo, hi = 0, len(curve) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if curve[mid]["t"] <= t:
            lo = mid
        else:
            hi = mid
    a, b = curve[lo], curve[hi]
    f = (t - a["t"]) / (b["t"] - a["t"])
    return round(a["h"] + f * (b["h"] - a["h"]), 2)


def hm(minutes):
    """Minutes after midnight -> 'HH:MM'."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


# =====================================================================  case-01
def case01(D, ver="v1") -> str:
    """Dawn go/no-go card - phone 500x1060, dark, 05:40 before sunrise."""
    W, H = 500, 1060
    d = Doc(W, H, S.NAVY)
    tide, route, fuel, plan = D["tide"], D["route"], D["fuel"], D["plan"]
    curve = tide["curve"]
    d.grad(0, 0, W, 420, "#0B1B2BFF,#132B45FF", kind="LINEAR", begin="TOP_CENTER", end="BOTTOM_CENTER")

    # ---- status + brand
    d.text(28, 10, "05:40", 20, S.SLATE, "BOLD", MONO)
    d.rtext(W - 28, 10, 26, "SAT 3 OCT · BRINDLEMOUTH", 17, S.MUTED)
    d.circle(32, 66, 6, S.TEAL)
    d.text(48, 54, "KELPLINE", 20, S.WHITE, "BOLD", INTER, spacing=3)
    d.rtext(W - 28, 54, 26, "v3.2 · offline OK", 16, S.MUTED)
    d.box(24, 90, W - 48, 1, S.DARKLINE)

    # ---- trip
    d.text(24, 108, "Petrel · The Apron", 32, S.WHITE, "BOLD", CJK)
    d.text(24, 150, "2 POB · 17.6 nm plan · skipper M. Ellery", 18, S.SLATE, "NORMAL", CJK)

    # ---- verdict
    d.box(24, 188, W - 48, 172, S.NAVY2, radius=16, border=f"1 SOLID {S.TEAL_D}")
    d.box(24, 188, 6, 172, S.TEAL, tl=16, bl=16)
    d.text(52, 214, "GO", 64, S.TEAL_L, "BOLD", INTER)
    d.text(178, 214, "launch 06:25", 26, S.WHITE, "BOLD", CJK)
    d.text(178, 254, "bank open till 08:10 · back 15:08", 18, S.SLATE, "NORMAL", CJK)
    d.box(52, 300, W - 76, 1, S.DARKLINE)
    d.circle(60, 330, 5, S.AMBER)
    d.text(74, 319, "3 checks clear · 1 to watch (fog)", 18, S.AMBER_L, "BOLD", CJK)

    # ---- checks
    d.box(24, 376, W - 48, 232, S.NAVY2, radius=14, border=f"1 SOLID {S.DARKLINE}")
    rows = [
        (S.TEAL, "Wind SW 12–15 kn", "gust 22 kn after 15:00", "OK", S.TEAL_L),
        (S.TEAL, "Swell 0.4 m / 6 s", "no white water over the bank", "OK", S.TEAL_L),
        (S.AMBER, "Visibility 6 km", "fog patches nr Carrow Ness till 08:00", "WATCH", S.AMBER_L),
        (S.TEAL, "Bank gate 3.71 m at 06:35", "needs 2.50 m · reopens 14:55", "OK", S.TEAL_L),
    ]
    for i, (c, title, sub, status, scol) in enumerate(rows):
        y = 392 + i * 54
        d.circle(44, y + 22, 6, c)
        d.text(62, y + 6, title, 20, S.WHITE, "BOLD", CJK)
        d.text(62, y + 30, sub, 16, S.MUTED, "NORMAL", CJK)
        d.rtext(W - 40, y + 6, 28, status, 17, scol, weight="BOLD")

    # ---- tide strip
    d.box(24, 618, W - 48, 228, S.NAVY2, radius=14, border=f"1 SOLID {S.DARKLINE}")
    S.section_label(d, 40, 632, "Tide at the bank", S.MUTED, 15)
    d.rtext(W - 40, 632, 20, "gate ≥ 2.50 m", 15, S.SLATE)
    S.tide_chart(d, 46, 668, W - 92, 96, curve, t0=4, t1=20, hmin=0, hmax=4.5,
                 line=S.SKY, fill="#38BDF826",
                 gates=[{"from_t": 4.0, "to_t": 8.17}, {"from_t": 14.92, "to_t": 20.0}],
                 gate_fill="#0E9F8F26", grid_color="#1E3A57FF", label_color=S.MUTED,
                 axis_label_size=13, h_lines=2, t_step=4, thickness=3,
                 marks=[{"t": 6.58, "h": tide_at(curve, 6.58), "color": S.TEAL_L,
                         "label": "out 06:35", "dy": 14},
                        {"t": 14.97, "h": tide_at(curve, 14.97), "color": S.TEAL_L,
                         "label": "back 14:58", "dy": -36}],
                 vlines=[{"t": 5.67, "color": S.WHITE}])
    d.text(46, 800, "HW 05:10 · LW 11:25 · HW 17:30 · now 05:40", 15, S.SLATE, "NORMAL", MONO)
    d.text(46, 822, "cross out 06:35 = 3.71 m · back 14:58 = 2.55 m", 15, S.SLATE, "NORMAL", CJK)

    # ---- checklist
    d.box(24, 856, W - 48, 128, S.NAVY2, radius=14, border=f"1 SOLID {S.DARKLINE}")
    items = ["Kill cord fitted and tested", "VHF 16 + 72 radio check done", "36 L aboard · plan 19.5 L"]
    for i, it in enumerate(items):
        y = 872 + i * 38
        d.box(40, y, 20, 20, "#00000000", radius=5, border=f"2 SOLID {S.TEAL}")
        d.seg(44, y + 11, 49, y + 16, S.TEAL, 3)
        d.seg(49, y + 16, 57, y + 4, S.TEAL, 3)
        d.text(70, y - 1, it, 19, S.WHITE, "NORMAL", CJK)

    # ---- actions
    d.box(24, 1000, 292, 56, S.TEAL, radius=12)
    d.tbox(24, 1000, 292, 56, "File float plan", 22, S.NAVY, "CENTER", "BOLD", CJK)
    d.box(332, 1000, 144, 56, "#00000000", radius=12, border=f"2 SOLID {S.DARKLINE}")
    d.tbox(332, 1000, 144, 56, "Not going", 20, S.SLATE, "CENTER", "BOLD", CJK)
    return d.finish()


# =====================================================================  case-02
def case02(D, ver="v1") -> str:
    """Tide & stream day chart - 1600x1000 instrument panel."""
    W, H = 1600, 1000
    d = Doc(W, H, S.NAVY)
    tide, stream = D["tide"], D["stream"]
    curve = tide["curve"]
    d.grad(0, 0, W, 140, "#0B1B2BFF,#12293FFF", kind="LINEAR", begin="TOP_LEFT", end="BOTTOM_RIGHT")
    S.header(d, W, "Tide & stream · Brindlemouth",
             "Harmonic sum M2 S2 K1 O1 · heights above chart datum · local clock (fictional port)",
             [("SAT 3 OCT 2026", S.WHITE, 22, "BOLD"),
              ("computed 05:35 · next model run 06:35", S.MUTED, 16, "NORMAL")], h=112)

    # ---------- main chart
    d.box(40, 132, 1136, 568, S.NAVY2, radius=16, border=f"1 SOLID {S.DARKLINE}")
    S.section_label(d, 72, 152, "24-hour tide height", S.MUTED, 16)
    d.rtext(1144, 152, 22, "bank gate ≥ 2.50 m over Old Keel Bank", 16, S.SLATE)
    S.tide_chart(d, 116, 200, 1000, 400, curve, t0=0, t1=24, hmin=0, hmax=4.5,
                 line=S.SKY, fill="#38BDF826",
                 gates=[{"from_t": 2.25, "to_t": 8.17}, {"from_t": 14.92, "to_t": 20.33}],
                 gate_fill="#0E9F8F26", grid_color="#1E3A57FF", label_color=S.SLATE,
                 axis_label_size=15, h_lines=1, t_step=2, thickness=5,
                 marks=[{"t": 6.58, "h": tide_at(curve, 6.58), "color": S.TEAL_L, "label": "cross out 06:35", "dy": 16},
                        {"t": 14.97, "h": tide_at(curve, 14.97), "color": S.TEAL_L, "label": "cross back 14:58", "dy": -38}],
                 vlines=[{"t": 5.67, "color": S.WHITE, "label": "now 05:40", "lfill": S.WHITE, "lcolor": S.NAVY},
                         {"t": 15.33, "color": S.RED, "label": "deadline 15:20", "lfill": S.RED,
                          "dash": True}])
    d.text(116, 640, "GREEN BANDS = bank crossable (≥ 2.50 m) · 02:15–08:10 and 14:55–20:20",
           16, S.TEAL_L, "BOLD", CJK)
    d.text(116, 664, "crossing needs 1.30 m over the bank's 1.20 m drying height: 0.75 m draft + 0.55 m under-keel margin",
           15, S.MUTED, "NORMAL", CJK)

    # ---------- right rail
    d.box(1200, 132, 360, 200, S.NAVY2, radius=16, border=f"1 SOLID {S.DARKLINE}")
    S.section_label(d, 1224, 150, "Today's extremes", S.MUTED, 15)
    for i, e in enumerate(tide["extremes"]):
        y = 182 + i * 34
        d.text(1224, y, e["clock"], 24, S.WHITE, "BOLD", MONO)
        d.text(1330, y + 2, e["kind"], 18, S.TEAL_L if e["kind"] == "HW" else S.SKY, "BOLD", INTER)
        d.rtext(1536, y, 26, f'{e["h"]:.2f} m', 20, S.SLATE, weight="BOLD", family=MONO)

    d.box(1200, 348, 360, 186, S.NAVY2, radius=16, border=f"1 SOLID {S.DARKLINE}")
    S.section_label(d, 1224, 366, "Slack water (stream under 0.2 kn)", S.MUTED, 15)
    for i, t in enumerate(stream["slack"][:4]):
        y = 392 + i * 26
        d.text(1224, y, t, 20, S.WHITE, "BOLD", MONO)
        d.text(1320, y + 2, ["after HW", "after LW", "after HW", "after LW"][i], 16, S.MUTED, "NORMAL", CJK)
    d.text(1224, 496, "planned crossing is 27 min after HW", 14, S.MUTED, "NORMAL", CJK)

    d.box(1200, 548, 360, 164, S.NAVY2, radius=16, border=f"1 SOLID {S.DARKLINE}")
    S.section_label(d, 1224, 566, "Rule of twelfths · 3.52 m range", S.MUTED, 15)
    for i in range(6):
        y = 594 + i * 19
        d.text(1224, y, f"{i+1}h", 15, S.MUTED, "NORMAL", MONO)
        frac = [1, 3, 6, 9, 11, 12][i] / 12
        S.bar(d, 1264, y + 2, 200, 12, frac, S.SKY if i < 5 else S.TEAL)
        d.rtext(1540, y - 1, 20, f"{[1,2,3,3,2,1][i]}/12", 14, S.SLATE, weight="NORMAL", family=MONO)

    # ---------- stream strip
    d.box(40, 716, 1520, 172, S.NAVY2, radius=16, border=f"1 SOLID {S.DARKLINE}")
    S.section_label(d, 72, 732, "Tidal stream — flood 048° · ebb 228°", S.MUTED, 16)
    d.rtext(1528, 732, 22, "arrows point down-stream · values in knots", 15, S.SLATE)
    x0, x1, yrow = 116, 1496, 812
    for hrec in stream["hours"]:
        hh = int(hrec["clock"][:2])
        x = x0 + (x1 - x0) * hh / 24
        spd = hrec["stream_kn"]
        if hrec["stream"] == "slack":
            d.circle(x, yrow, 4, S.MUTED)
        else:
            up = hrec["stream"] == "flood"
            col = S.TEAL if up else "#3B82F6FF"
            L = 10 + spd * 12
            if up:
                d.arrow(x - L / 2, yrow + L / 2, x + L / 2, yrow - L / 2, col, 3, 7)
            else:
                d.arrow(x + L / 2, yrow - L / 2, x - L / 2, yrow + L / 2, col, 3, 7)
        d.ctext(x, yrow - 34, 22, f"{spd:.1f}" if spd >= 0.15 else "—", 15,
                S.WHITE if spd >= 0.15 else S.MUTED, "BOLD", MONO, pad=6)
        if hh % 3 == 0:
            d.ctext(x, yrow + 40, 24, f"{hh:02d}", 15, S.MUTED, "NORMAL", MONO, pad=6)
    d.box(116, yrow + 26, x1 - x0, 1, S.DARKLINE)

    # ---------- chips
    chips = [("Bank open", "02:15 – 08:10", S.TEAL),
             ("Cross out 06:35", "3.71 m · 1 h 35 m spare", S.TEAL),
             ("Cross back 14:58", "2.55 m · gate opens 14:55", S.AMBER),
             ("Weather deadline", "15:20 · gust 22 kn after", S.RED)]
    for i, (lbl, val, col) in enumerate(chips):
        S.chip(d, 40 + i * 390, 904, 370, 76, lbl, val, col, fill=S.NAVY2)
    return d.finish()


# ------------------------------------------------------------------ shared chart
# Hand-authored coastline for the fictional Brindlemouth chart: the land occupies the
# north and the north-east, the sea (and the whole route) is to the south-west.
COAST = [
    (51.712, -5.290), (51.712, -5.040), (51.560, -5.040), (51.570, -5.060),
    (51.582, -5.075), (51.594, -5.083), (51.604, -5.078), (51.614, -5.088),
    (51.624, -5.101), (51.634, -5.114), (51.644, -5.126), (51.652, -5.137),
    (51.660, -5.146), (51.668, -5.140), (51.674, -5.130), (51.680, -5.118),
    (51.686, -5.106), (51.690, -5.096), (51.694, -5.086), (51.697, -5.080),
    (51.699, -5.074), (51.700, -5.068), (51.702, -5.066), (51.706, -5.070),
    (51.710, -5.076), (51.712, -5.082),
]


def draw_chart(d, bounds, x, y, w, h, D, *, sea="#DCE6EF", land="#E2E5D3",
               coast="#8A9A7B", ink="#0F172A", route_col="#1D4ED8",
               escape_col="#D92D20", bank=True, escape=False, waypoints=True,
               graticule=True, label_size=15, north=True):
    """Chart sketch built entirely from DSL primitives; returns the projector."""
    P = S.projector(bounds, x, y, w, h)
    d.box(x, y, w, h, sea)
    coast_pts = [P(la, lo) for la, lo in COAST]
    S.fill_poly(d, coast_pts, land, step=6)
    d.poly(coast_pts + [coast_pts[0]], coast, 2.5)
    if graticule:
        S.sea_grid(d, x, y, w, h, bounds, color="#B9C9D8FF", step_min=10, label=True,
                   label_color="#7C93A8FF")
    # harbour: breakwater, pontoons and a few town blocks on the land side
    hx0, hy = P(51.7005, -5.0860)
    hx1, _ = P(51.7005, -5.0650)
    d.box(hx0, hy - 5, hx1 - hx0, 10, "#6B7A8CFF")
    d.box(hx0 + 16, hy - 30, 60, 5, "#9AA7B4FF")
    d.box(hx0 + 96, hy - 30, 60, 5, "#9AA7B4FF")
    tx, ty = P(51.7085, -5.0840)
    for i in range(4):
        d.box(tx + i * 26, ty + (i % 2) * 14, 20, 11, "#C9C3B2FF")
    d.text(tx + 108, ty + 2, "BRINDLEMOUTH", 13, "#6B6350FF", "BOLD", INTER) if waypoints else None
    if bank:
        cx, cy = P(51.6613, -5.1075)
        pts = []
        for i in range(40):
            a = 2 * math.pi * i / 40
            pts.append((cx + math.cos(a) * 96, cy + math.sin(a) * 34))
        S.fill_poly(d, pts, "#EADFC4", step=5)
        d.poly(pts + [pts[0]], "#C9B98CFF", 2)
        d.text(cx - 90, cy - 8, "OLD KEEL BANK · dries 1.2 m", 13, "#7A6A45FF", "BOLD", INTER)
    WP = D["route"]["waypoints"]
    order = ["HBR", "MID", "BANK", "SKER", "APRON"]
    pts = [P(WP[k]["lat"], WP[k]["lon"]) for k in order]
    d.poly(pts, route_col, 3.5)
    for i in range(len(pts) - 1):
        mx, my = (pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2
        L = math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
        ux, uy = (pts[i + 1][0] - pts[i][0]) / L, (pts[i + 1][1] - pts[i][1]) / L
        d.arrow(mx - ux * 12, my - uy * 12, mx + ux * 12, my + uy * 12, route_col, 3, 8)
    if waypoints:
        for k in order:
            px, py = P(WP[k]["lat"], WP[k]["lon"])
            d.circle(px, py, 6, "#FFFFFFFF", border=f"3 SOLID {route_col}")
            d.text(px + 12, py - 26, k, 15, route_col, "BOLD", INTER)
    if escape:
        esc_pts = [P(WP["SKER"]["lat"], WP["SKER"]["lon"]),
                   P(51.6760, -5.1400), P(51.6880, -5.1060), P(WP["HBR"]["lat"], WP["HBR"]["lon"])]
        for i in range(len(esc_pts) - 1):
            d.dash(esc_pts[i][0], esc_pts[i][1], esc_pts[i + 1][0], esc_pts[i + 1][1],
                   escape_col, 3, 11, 8)
        mx = (esc_pts[1][0] + esc_pts[2][0]) / 2
        my = (esc_pts[1][1] + esc_pts[2][1]) / 2
        d.box(mx - 78, my - 34, 156, 24, "#FFFFFFFF", radius=6, border=f"1 SOLID {escape_col}")
        d.tbox(mx - 78, my - 34, 156, 24, "escape route +1.2 nm", 14, escape_col, "CENTER", "BOLD", INTER)
    if north:
        S.north_arrow(d, x + w - 60, y + h - 90, 40, ink)
    return P


# =====================================================================  case-03
def case03(D, ver="v1") -> str:
    """Passage plan - A4 portrait 1240x1754, printed and laminated for the cockpit."""
    W, H = 1240, 1754
    d = Doc(W, H, S.PAPER)
    tide, route, fuel, plan = D["tide"], D["route"], D["fuel"], D["plan"]
    curve = tide["curve"]
    ink = "#14203AFF"
    d.box(0, 0, W, 150, S.NAVY)
    d.box(0, 146, W, 5, S.TEAL)
    d.text(48, 28, "PASSAGE PLAN", 44, S.WHITE, "BOLD", INTER, spacing=4)
    d.rtext(W - 48, 32, 34, "PETREL · 5.8 m OPEN LAUNCH", 21, S.TEAL_L, weight="BOLD")
    d.rtext(W - 48, 66, 30, "17.6 nm · 2 POB · 36 L aboard", 18, S.SLATE)
    d.text(48, 96, "Sat 3 Oct 2026 · skipper M. Ellery · crew D. Trelawn · filed 05:44 · "
                   "Brindlemouth (fictional port)", 19, S.SLATE, "NORMAL", CJK)

    # ---------- A route table
    d.text(48, 178, "A · ROUTE LEGS AND TIMING", 22, ink, "BOLD", INTER, spacing=1)
    d.box(48, 208, W - 96, 2, ink)
    cols = [("LEG", 48, 80), ("FROM → TO", 128, 500), ("BRG °T", 628, 120),
            ("DIST", 748, 120), ("ETA", 868, 150), ("TIDE AT ARRIVAL", 1018, 174)]
    d.box(48, 218, W - 96, 42, ink)
    for name, cx, cw in cols:
        d.tbox(cx + 12, 218, cw - 12, 42, name, 16, S.WHITE, "CENTER_LEFT", "BOLD", INTER)
    legs = route["legs"]
    # arrival clock in minutes after midnight, taken from the day plan in the data model
    eta = [385, 389, 395, 406, 549, 895, 904, 908]
    gate_rows = {1, 2, 5, 6}          # 0-based legs that cross, or arrive over, Old Keel Bank
    for i, l in enumerate(legs):
        y = 260 + i * 44
        if i % 2 == 0:
            d.box(48, y, W - 96, 44, "#FFFFFFFF")
        d.text(60, y + 12, str(l["leg"]), 19, S.MUTED, "BOLD", MONO)
        d.text(140, y + 12, f'{l["from_name"]} → {l["to_name"]}', 17, ink, "NORMAL", CJK)
        d.text(640, y + 12, f'{l["bearing_t"]:03d}°', 18, ink, "BOLD", MONO)
        d.text(760, y + 12, f'{l["nm"]:.2f} nm', 18, ink, "NORMAL", MONO)
        d.text(880, y + 12, f'{hm(eta[i])} · {l["minutes"]} min', 18, ink, "NORMAL", MONO)
        tt = tide_at(curve, eta[i] / 60)
        col = S.MUTED if i not in gate_rows else (S.TEAL_D if tt >= 2.5 else S.AMBER)
        d.text(1030, y + 12, f'{tt:.2f} m' + ("  · gate" if i in gate_rows else ""),
               18, col, "BOLD" if i in gate_rows else "NORMAL", MONO)
    d.box(48, 612, W - 96, 2, "#C9C2B4FF")
    d.text(48, 626, "Passage 88 min under power · 326 min on the ground · planned fuel "
                    f'{fuel["calm"]["litres"]} / {fuel["tank_l"]:.0f} L '
                    f'({fuel["calm"]["pct_of_tank"]} %) · reserve {fuel["calm"]["reserve_l"]} L · '
                    "gate wait 3 min at 14:55",
           17, S.MUTED, "NORMAL", CJK)

    # ---------- B chart sketch
    d.text(48, 664, "B · CHART SKETCH — NOT FOR NAVIGATION", 22, ink, "BOLD", INTER, spacing=1)
    d.box(48, 694, W - 96, 2, ink)
    draw_chart(d, (51.560, 51.712, -5.290, -5.040), 48, 706, W - 96, 494, D,
               escape=True, label_size=13)
    S.scale_bar(d, 84, 1140, 199, ink, "#5A6472FF", nm=2.0)

    # ---------- C / D
    y0 = 1236
    d.text(48, y0, "C · ABORT CRITERIA", 22, ink, "BOLD", INTER, spacing=1)
    d.box(48, y0 + 30, 540, 2, ink)
    aborts = [
        "Sustained wind over 18 kn, or any gust over 25 kn, before 14:00 — run for the harbour.",
        "Visibility under 1 000 m at Gannet Skerry — stop fishing, transit on the plotted track.",
        "Bank gate under 2.50 m at the planned crossing time — use the North Channel escape route.",
        "Engine note change, or fuel below the 7.2 L reserve — stop the drift and return at 12 kn.",
        "Any POB without a lifejacket, or a kill cord not fitted — no slip.",
    ]
    for i, t in enumerate(aborts):
        yy = y0 + 44 + i * 38
        d.circle(56, yy + 8, 4, S.RED)
        d.para(74, yy - 2, 520, t, 16, "#33405AFF")
    d.text(630, y0, "D · IF IT GOES WRONG", 22, ink, "BOLD", INTER, spacing=1)
    d.box(630, y0 + 30, 562, 2, ink)
    contacts = [
        ("VHF 16", "distress and urgency; DSC alert from the set"),
        ("VHF 72", "Brindlemouth Harbour Office, 07:00–19:00"),
        ("0131 555 0142", "Brindlemouth Coastguard ops room (fictional)"),
        ("PLB 1D0-2E44-91", "registered to Petrel, on the skipper's vest"),
        ("Tom Ellery", "shore contact with the plan and the check-in ladder"),
    ]
    for i, (a, b) in enumerate(contacts):
        yy = y0 + 44 + i * 38
        d.box(630, yy, 562, 34, "#FFFFFFFF", radius=6, border=f"1 SOLID {S.LINE2}")
        d.text(642, yy + 7, a, 16, S.NAVY, "BOLD", MONO)
        d.text(790, yy + 7, b, 16, "#44506AFF", "NORMAL", CJK)

    # ---------- E / F
    y1 = 1492
    d.text(48, y1, "E · CREW, KIT AND CHECKS", 20, ink, "BOLD", INTER)
    d.box(48, y1 + 28, 540, 2, ink)
    kit = ["2 lifejackets, 2 kill cords, 1 throw line, 2 in-date flares",
           "VHF handheld + fixed set, phone in a dry bag, PLB on the skipper",
           "First aid kit, 2 L water, sun cover, anchor and 30 m warp",
           "Tide table, this plan laminated, pencil and grease board"]
    for i, t in enumerate(kit):
        yy = y1 + 42 + i * 27
        d.box(52, yy + 3, 14, 14, "#00000000", radius=3, border=f"2 SOLID {S.TEAL_D}")
        d.text(76, yy, t, 16, "#33405AFF", "NORMAL", CJK)
    d.text(630, y1, "F · DAY PLAN", 20, ink, "BOLD", INTER)
    d.box(630, y1 + 28, 562, 2, ink)
    day = plan["day"]
    for i, (t, what) in enumerate(day):
        col = 630 if i < 6 else 922
        row = i if i < 6 else i - 6
        yy = y1 + 42 + row * 27
        d.text(col, yy, t, 16, S.NAVY, "BOLD", MONO)
        d.text(col + 54, yy, what, 15, "#44506AFF", "NORMAL", CJK)

    d.box(48, 1700, W - 96, 2, "#C9C2B4FF")
    d.text(48, 1712, "Generated 05:52 by Kelpline for Petrel · not a substitute for official charts, "
                     "the harbour office's notices or the skipper's judgement.", 15, S.MUTED, "NORMAL", CJK)
    d.rtext(W - 48, 1712, 24, "1 / 1", 15, S.MUTED, weight="BOLD", family=MONO)
    return d.finish()


# =====================================================================  case-04
def case04(D, ver="v1") -> str:
    """Five-morning weather window comparison - 1600x1000, light data surface."""
    W, H = 1600, 1000
    d = Doc(W, H, S.LIGHT)
    fc = D["forecast"]
    S.header(d, W, "Weather windows · the next five mornings",
             "Three-model comparison · Nimbus-HR 4 km · Pelagic-9 9 km · Coastal-Meso 2 km — model names are invented",
             [("generated 05:35 · next run 16:35", S.WHITE, 20, "BOLD"),
              ("SAT 3 OCT 2026", S.SLATE, 18, "NORMAL")], h=112, accent=S.BLUE)

    # legend
    for i, (lbl, col) in enumerate([("GOOD", S.TEAL), ("FAIR", "#B45309FF"),
                                    ("POOR", S.AMBER), ("NO-GO", S.RED)]):
        x = 40 + i * 150
        d.box(x, 130, 20, 20, col, radius=5)
        d.text(x + 30, 132, lbl, 17, S.INK, "BOLD", INTER)
    d.rtext(1140, 132, 24, "agreement = how many models sit within 3 kn of the median", 15, S.MUTED)

    # matrix
    d.box(40, 176, 120, 52, S.NAVY)
    d.tbox(40, 176, 120, 52, "DAY", 17, S.WHITE, "CENTER", "BOLD", INTER, spacing=1)
    for j, per in enumerate(fc["periods"]):
        x = 160 + j * 240
        d.box(x, 176, 240, 52, S.NAVY2)
        d.tbox(x, 176, 240, 52, per, 19, S.WHITE, "CENTER", "BOLD", MONO)
    for i, day in enumerate(fc["days"]):
        y = 228 + i * 112
        d.box(40, y, 120, 112, S.NAVY if i == 0 else "#334155FF")
        d.tbox(40, y, 120, 112, day["day"], 26, S.WHITE, "CENTER", "BOLD", CJK)
        for j, c in enumerate(day["cells"]):
            x = 160 + j * 240
            d.box(x, y, 240, 112, S.WHITE)
            d.box(x, y, 240, 1, S.LINE)
            d.box(x, y, 1, 112, S.LINE)
            d.box(x, y, 6, 112, c["color"])
            d.text(x + 20, y + 12, f'{c["dir"]} {c["kn"]}', 30, S.INK, "BOLD", INTER)
            d.text(x + 20, y + 52, f'gust {c["gust"]} kn', 18, S.MUTED, "NORMAL", CJK)
            d.text(x + 130, y + 52, f'{c["wave"]} m', 18, S.MUTED, "NORMAL", MONO)
            d.box(x + 20, y + 78, 108, 26, c["color"], radius=6)
            d.tbox(x + 20, y + 78, 108, 26, c["verdict"], 16, S.WHITE, "CENTER", "BOLD", INTER)
            for k in range(3):
                filled = k < c["agree"]
                cx = x + 208 - k * 16
                if filled:
                    d.circle(cx, y + 24, 6, S.INK)
                else:
                    d.ring(cx, y + 24, 6, S.LINE2, 2)

    # right rail
    d.box(1160, 176, 400, 174, "#E7F6F2FF", radius=14, border=f"2 SOLID {S.TEAL}")
    S.section_label(d, 1184, 194, "Best window", S.TEAL_D, 16)
    d.text(1184, 218, "SAT 3 · 06–09", 34, S.INK, "BOLD", INTER)
    for i, t in enumerate(["3 of 3 models within 1 kn", "gust 15 kn, sea 0.4 m",
                           "bank open until 08:10, cross out 06:35"]):
        d.circle(1190, 274 + i * 24, 3.5, S.TEAL)
        d.text(1204, 266 + i * 24, t, 16, "#1F3B36FF", "NORMAL", CJK)
    d.box(1160, 366, 400, 140, "#FDECE9FF", radius=14, border=f"2 SOLID {S.RED}")
    S.section_label(d, 1184, 384, "Avoid", S.RED, 16)
    d.text(1184, 408, "SUN 4 · 12–15", 30, S.INK, "BOLD", INTER)
    d.text(1184, 448, "SW 22 gust 34 kn, sea 1.4 m.", 16, "#5C2620FF", "NORMAL", CJK)
    d.text(1184, 470, "Models disagree by 6 kn on timing.", 16, "#5C2620FF", "NORMAL", CJK)

    # saturday model curves
    d.box(1160, 522, 400, 266, S.WHITE, radius=14, border=f"1 SOLID {S.LINE}")
    S.section_label(d, 1184, 538, "Saturday wind · three models", S.MUTED, 15)
    cx0, cy0, cw, ch = 1196, 584, 336, 156
    for kn in (0, 10, 20):
        yy = cy0 + ch - kn / 25 * ch
        d.box(cx0, yy, cw, 1, S.LINE)
        d.rtext(cx0 - 8, yy - 11, 20, str(kn), 13, S.MUTED, weight="NORMAL", family=MONO)
    for i, hh in enumerate(fc["curve_hours"]):
        if hh % 3 == 0:
            xx = cx0 + cw * i / (len(fc["curve_hours"]) - 1)
            d.ctext(xx, cy0 + ch + 6, 20, f"{hh:02d}", 13, S.MUTED, "NORMAL", MONO, pad=4)
    cols = ["#0E9F8FFF", "#1D4ED8FF", "#D97706FF"]
    for s, colr in zip(fc["sat_curves"], cols):
        pts = [(cx0 + cw * i / (len(s["kn"]) - 1), cy0 + ch - v / 25 * ch)
               for i, v in enumerate(s["kn"])]
        d.poly(pts, colr, 3)
        d.circle(pts[-1][0], pts[-1][1], 5, colr)
    for i, (s, colr) in enumerate(zip(fc["sat_curves"], cols)):
        d.box(1196 + i * 130, 770, 12, 12, colr, radius=3)
        d.text(1214 + i * 130, 768, s["model"], 13, S.MUTED, "NORMAL", INTER)

    # bottom
    d.box(40, 812, 700, 150, S.WHITE, radius=14, border=f"1 SOLID {S.LINE}")
    S.section_label(d, 64, 830, "Why the morning and not the afternoon", S.MUTED, 15)
    for i, t in enumerate([
        "The sea builds through the day: 0.4 m at 06:00, 0.8 m by 18:00 on the same wind.",
        "Gusts reach 26 kn after 15:00 — over the 18 kn abort line in the passage plan.",
        "The bank gate closes at 08:10; a late start wastes the morning tide.",
    ]):
        d.circle(70, 866 + i * 28, 3.5, S.BLUE)
        d.text(84, 858 + i * 28, t, 16, S.INK2, "NORMAL", CJK)
    d.box(760, 812, 800, 150, S.NAVY, radius=14)
    S.section_label(d, 784, 830, "Decision", S.TEAL_L, 15)
    d.text(784, 854, "Launch 06:25 · cross out 06:35 · back over the bank 14:58", 26, S.WHITE, "BOLD", CJK)
    d.text(784, 898, "Sunday's plan is cancelled; Monday 06:00–12:00 is the fallback window "
                     "(W 11–13 kn, 0.4 m).", 17, S.SLATE, "NORMAL", CJK)
    d.text(784, 926, "If the 06:00 inshore update shows gusts over 18 kn before 10:00, the day is off.",
           17, S.AMBER_L, "NORMAL", CJK)
    return d.finish()


# =====================================================================  case-05
def case05(D, ver="v1") -> str:
    """Float plan and shore watch - phone 500x1060, light and calm."""
    W, H = 500, 1060
    d = Doc(W, H, S.LIGHT)
    plan, fuel, route = D["plan"], D["fuel"], D["route"]
    d.text(28, 10, "05:44", 20, S.INK, "BOLD", MONO)
    d.rtext(W - 28, 10, 26, "SAT 3 OCT · ASHORE", 17, S.MUTED)

    d.box(24, 50, W - 48, 150, S.NAVY, radius=16)
    d.text(44, 72, "Float plan filed", 30, S.WHITE, "BOLD", CJK)
    d.text(44, 112, "Sent to Tom Ellery (brother) · SMS + live link", 17, S.SLATE, "NORMAL", CJK)
    d.box(44, 142, 300, 36, S.TEAL, radius=10)
    d.tbox(44, 142, 300, 36, "delivered 05:44 · link opened 05:47", 15, S.NAVY, "CENTER", "BOLD", CJK)

    d.box(24, 216, W - 48, 132, S.WHITE, radius=14, border=f"1 SOLID {S.LINE}")
    S.section_label(d, 44, 230, "Vessel and crew", S.MUTED, 15)
    for i, (k, v) in enumerate([("Vessel", "Petrel · 5.8 m open launch"),
                                ("Engine", "60 hp 4-stroke · 36 L in 2 tanks"),
                                ("POB", "M. Ellery (skipper) · D. Trelawn"),
                                ("Radio", "VHF 16 + 72 · PLB 1D0-2E44-91")]):
        y = 256 + i * 22
        d.text(44, y, k, 16, S.MUTED, "NORMAL", CJK)
        d.rtext(W - 44, y, 22, v, 16, S.INK, weight="BOLD", family=CJK)

    d.box(24, 362, W - 48, 116, S.WHITE, radius=14, border=f"1 SOLID {S.LINE}")
    S.section_label(d, 44, 376, "Route on file", S.MUTED, 15)
    d.text(44, 400, "Brindlemouth → Old Keel Bank → Gannet Skerry", 17, S.INK, "BOLD", CJK)
    d.text(44, 424, "→ The Apron → back over the bank → C4 mooring", 17, S.INK, "BOLD", CJK)
    d.text(44, 450, "17.6 nm · 88 min under power · due back 15:08", 15, S.MUTED, "NORMAL", CJK)

    d.box(24, 492, W - 48, 344, S.WHITE, radius=14, border=f"1 SOLID {S.LINE}")
    S.section_label(d, 44, 506, "Check-in ladder", S.MUTED, 15)
    steps = [("06:25", "slipped Brindlemouth", S.TEAL),
             ("09:00", "SMS: all well, 2 POB, position", S.TEAL),
             ("12:00", "SMS: drift 3, fuel 62 %, no issues", S.TEAL),
             ("15:08", "alongside C4 · plan closed", S.TEAL)]
    for i, (t, what, col) in enumerate(steps):
        y = 534 + i * 42
        d.circle(52, y + 12, 8, col)
        d.circle(52, y + 12, 3.5, S.WHITE)
        if i < len(steps) - 1:
            d.box(50, y + 22, 3, 20, S.LINE2)
        d.text(72, y + 2, t, 19, S.INK, "BOLD", MONO)
        d.text(140, y + 3, what, 16, S.INK2, "NORMAL", CJK)
    d.text(44, 716, "If no word from Petrel", 17, S.RED, "BOLD", CJK)
    escal = [("15:38", "Tom calls the boat phone, then the harbour office", S.AMBER),
             ("16:08", "Harbour office radios VHF 72 and checks the mooring", S.AMBER),
             ("16:38", "Coastguard gets the drift datum and the search boxes", S.RED)]
    for i, (t, what, col) in enumerate(escal):
        y = 742 + i * 30
        d.box(44, y, 5, 24, col, radius=2)
        d.text(60, y + 2, t, 17, col, "BOLD", MONO)
        d.text(126, y + 3, what, 15, S.INK2, "NORMAL", CJK)

    d.box(24, 850, W - 48, 168, S.WHITE, radius=14, border=f"1 SOLID {S.LINE}")
    S.section_label(d, 44, 864, "What Tom sees on the link", S.MUTED, 15)
    draw_chart(d, (51.575, 51.712, -5.290, -5.040), 44, 888, 240, 110, D,
               graticule=False, bank=False, waypoints=False, north=False)
    d.text(300, 894, "Petrel", 18, S.INK, "BOLD", CJK)
    d.text(300, 918, "Last position 11:22", 15, S.MUTED, "NORMAL", CJK)
    d.text(300, 940, "51°38.4'N 005°09.2'W", 15, S.MUTED, "NORMAL", MONO)
    d.text(300, 966, "3 of 4 check-ins done", 15, S.TEAL_D, "BOLD", CJK)
    d.box(300, 988, 156, 26, S.NAVY, radius=8)
    d.tbox(300, 988, 156, 26, "Call the boat", 15, S.WHITE, "CENTER", "BOLD", CJK)
    d.text(44, 1028, "Also shared with the Harbour Office and the coastguard liaison.",
           14, S.MUTED, "NORMAL", CJK)
    return d.finish()


# =====================================================================  case-06
def case06(D, ver="v1") -> str:
    """On-water glance display - 1180x820, sunlight-readable, big targets."""
    W, H = 1180, 820
    d = Doc(W, H, S.WHITE)
    tide, fuel, plan = D["tide"], D["fuel"], D["plan"]
    S.compass_tape(d, 0, 0, W, 118, 214)
    d.text(24, 126, "PETREL · 11:05 · 51°38.4'N 005°09.2'W", 18, S.MUTED, "BOLD", MONO)
    d.rtext(W - 24, 126, 24, "2 POB · AIS transmit on", 18, S.MUTED)

    def tile(x, y, w, h, label, value, unit, note, col=S.INK, note_col=S.MUTED, unit_dx=170):
        d.box(x, y, w, h, "#F8FAFCFF", radius=16, border=f"2 SOLID {S.LINE2}")
        d.text(x + 24, y + 18, label.upper(), 17, S.MUTED, "BOLD", INTER, spacing=2)
        d.text(x + 20, y + 50, value, 104, col, "BOLD", INTER)
        d.text(x + unit_dx, y + 114, unit, 30, S.INK2, "BOLD", INTER)
        d.text(x + 24, y + h - 40, note, 19, note_col, "NORMAL", CJK)

    tile(24, 152, 556, 210, "Speed over ground", "1.1", "kn",
         "drifting, engine idle · SOG averaged 60 s", unit_dx=176)
    tile(600, 152, 556, 210, "Depth", "8.4", "m", "7.6 m under the keel · sounder 2 s old",
         unit_dx=196)
    d.box(24, 380, 556, 210, "#FEF3F2FF", radius=16, border=f"3 SOLID {S.RED}")
    d.text(48, 398, "OLD KEEL BANK GATE", 17, S.RED, "BOLD", INTER, spacing=2)
    d.text(44, 428, "CLOSED", 84, S.RED, "BOLD", INTER)
    d.text(48, 528, "reopens 14:55 · cross back 14:58", 22, S.INK, "BOLD", CJK)
    d.text(48, 556, "3 h 50 m to the gate · water now 0.63 m, need 2.50 m", 18, S.MUTED, "NORMAL", CJK)
    d.box(600, 380, 556, 210, "#F8FAFCFF", radius=16, border=f"2 SOLID {S.LINE2}")
    d.text(624, 398, "FUEL ABOARD", 17, S.MUTED, "BOLD", INTER, spacing=2)
    d.text(620, 424, "22.4", 72, S.INK, "BOLD", INTER)
    d.text(624, 496, "L of 36 · 62 %", 24, S.INK2, "BOLD", CJK)
    S.bar(d, 624, 528, 508, 18, 22.4 / 36, S.TEAL, "#E2E8F0FF")
    d.text(624, 558, "plan 19.5 L · reserve 7.2 L · margin 9.3 L", 17, S.MUTED, "NORMAL", CJK)

    d.box(24, 608, 1132, 188, S.NAVY, radius=16)
    pills = [("DRIFT ALARM", "ARMED", S.TEAL_L), ("VHF", "16 WATCH", S.WHITE),
             ("NEXT CHECK-IN", "12:00 · 55 min", S.AMBER_L), ("POB", "2 · both in lifejackets", S.WHITE)]
    for i, (k, v, col) in enumerate(pills):
        x = 48 + i * 276
        d.text(x, 630, k, 15, S.SLATE, "BOLD", INTER, spacing=1)
        d.text(x, 654, v, 24, col, "BOLD", CJK)
    d.box(48, 700, 1084, 2, S.DARKLINE)
    d.text(48, 716, "RETURN PLAN", 15, S.SLATE, "BOLD", INTER, spacing=1)
    d.text(48, 740, "depart the ground 14:44 · cross the bank 14:58 · alongside C4 15:08 · "
                    "sunset 17:44", 22, S.WHITE, "BOLD", CJK)
    return d.finish()


# =====================================================================  case-07
def case07(D, ver="v1") -> str:
    """Overdue: drift and search datum - 1600x1000, emergency state, dark red."""
    W, H = 1600, 1000
    d = Doc(W, H, "#150B10FF")
    drift, fuel = D["drift"], D["fuel"]
    d.grad(0, 0, W, 132, "#4A0F14FF,#150B10FF", kind="LINEAR", begin="TOP_LEFT", end="BOTTOM_RIGHT")
    d.text(40, 26, "OVERDUE · PETREL · 2 POB", 34, S.WHITE, "BOLD", INTER, spacing=1)
    d.text(40, 76, "Last contact 12:00 (check-in 2 of 4) · overdue 15:52 · "
                   "Brindlemouth Coastguard notified 16:12", 19, "#FCA5A5FF", "NORMAL", CJK)
    d.rtext(W - 40, 26, 30, "SEARCH WATCH 16:20", 22, S.WHITE, weight="BOLD")
    d.rtext(W - 40, 66, 26, "SMC: Brindlemouth CG ops (fictional)", 17, "#FCA5A5FF")
    d.box(0, 128, W, 4, S.RED)

    # ---------------- chart
    bounds = (51.575, 51.755, -5.340, -4.980)
    cx, cy, cw, ch = 40, 152, 1120, 620
    d.box(cx, cy, cw, ch, "#0B1A2AFF", radius=16, border=f"1 SOLID {S.RED}")
    P = draw_chart(d, bounds, cx + 8, cy + 8, cw - 16, ch - 16, D,
                   sea="#0E2033FF", land="#1C2A22FF", coast="#54705CFF",
                   ink="#DCE6F0FF", route_col="#5A7FA8FF", escape_col="#D92D20FF",
                   bank=True, escape=False, waypoints=True)
    d.text(cx + 24, cy + 12, "PLANNED TRACK SHOWN IN BLUE · DRIFT DATUM IN RED",
           14, "#7C93A8FF", "BOLD", INTER, spacing=1)
    lat_span_nm = (bounds[1] - bounds[0]) * 60
    lon_span_nm = (bounds[3] - bounds[2]) * 60 * math.cos(math.radians(51.665))
    ppx, ppy = (cw - 16) / lon_span_nm, (ch - 16) / lat_span_nm

    def circ(centre, r_nm, fill, border_col):
        px, py = P(centre[0], centre[1])
        pts = [(px + math.cos(2 * math.pi * i / 48) * r_nm * ppx,
                py + math.sin(2 * math.pi * i / 48) * r_nm * ppy) for i in range(48)]
        S.fill_poly(d, pts, fill, step=5)
        d.poly(pts + [pts[0]], border_col, 2.5)
        return px, py

    for b in reversed(drift["boxes"]):
        px, py = circ(b["centre"], b["radius_nm"], "#D92D2022", "#F87171FF")
        d.circle(px, py, 19, S.RED, border="2 SOLID #FFFFFFFF")
        d.ctext(px, py - 12, 24, b["box"], 20, S.WHITE, "BOLD", INTER, pad=4)
    lx, ly = P(drift["lkp"][0], drift["lkp"][1])
    d.circle(lx, ly, 10, S.RED, border="3 SOLID #FFFFFFFF")
    d.box(lx - 66, ly + 18, 330, 26, "#0B1A2ACC", radius=6)
    d.text(lx - 58, ly + 23, "LKP 15:52 · 51°38.7'N 005°08.9'W", 16, S.WHITE, "BOLD", MONO)
    pts = [(lx, ly)] + [P(b["centre"][0], b["centre"][1]) for b in drift["boxes"]]
    for i in range(len(pts) - 1):
        d.arrow(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], "#FCA5A5FF", 2.5, 10)
    mx, my = pts[1]
    d.text(mx + 26, my + 46, f'drift {drift["drift_kn"]} kn toward {drift["drift_dir"]:03d}°',
           17, "#FDE68AFF", "BOLD", CJK)
    d.text(cx + 24, cy + ch - 30, "leeway 3.5 % of 18 kn wind + tidal stream 1.0 kn at 048° "
                                  "· surface drift, not a certainty", 15, "#94A3B8FF", "NORMAL", CJK)
    # box legend keeps every label off the circles themselves
    d.box(cx + 26, cy + 40, 366, 132, "#0B1A2AEE", radius=10, border=f"1 SOLID {S.RED}")
    d.text(cx + 42, cy + 52, "SEARCH BOXES · FROM THE DRIFT MODEL", 14, "#FCA5A5FF", "BOLD", INTER)
    for i, b in enumerate(drift["boxes"]):
        y = cy + 78 + i * 30
        d.circle(cx + 52, y + 10, 12, S.RED)
        d.ctext(cx + 52, y - 2, 24, b["box"], 15, S.WHITE, "BOLD", INTER, pad=4)
        d.text(cx + 74, y + 1, f'{int(b["prob"]*100)} % · {b["area_nm2"]} nm² · '
                               f'{b["radius_nm"]:g} nm radius', 16, "#E2E8F0FF", "NORMAL", CJK)

    # ---------------- right rail
    d.box(1180, 152, 380, 268, "#1B1114FF", radius=16, border=f"1 SOLID {S.RED}")
    S.section_label(d, 1204, 168, "Actions and owners", "#FCA5A5FF", 15)
    acts = [("16:12", "Coastguard ops informed, datum passed", "SMC", S.TEAL),
            ("16:18", "Harbour office checks C4 and the fuel dock", "Harbour", S.TEAL),
            ("16:24", "Lifeboat Aldrin launched, 12 kn", "RNLI-style unit", S.AMBER),
            ("16:26", "Coastal helicopter requested, ETA 16:55", "SMC", S.AMBER),
            ("16:30", "Tom Ellery confirms 36 L aboard at 06:25", "Shore contact", S.TEAL)]
    for i, (t, what, who, col) in enumerate(acts):
        y = 194 + i * 44
        d.box(1204, y, 4, 34, col, radius=2)
        d.text(1220, y, t, 17, S.WHITE, "BOLD", MONO)
        d.text(1220, y + 20, what, 15, "#E2E8F0FF", "NORMAL", CJK)
        d.rtext(1536, y, 22, who, 13, "#94A3B8FF")
    d.box(1180, 436, 380, 152, "#1B1114FF", radius=16, border=f"1 SOLID #7F1D1DFF")
    S.section_label(d, 1204, 452, "Comms log", "#FCA5A5FF", 15)
    log = [("15:52", "Overdue alarm raised by the shore contact"),
           ("16:02", "VHF 16 call to Petrel — no reply"),
           ("16:08", "DSC relay sent, AIS last seen 15:41")]
    for i, (t, what) in enumerate(log):
        y = 478 + i * 34
        d.text(1204, y, t, 16, "#FDE68AFF", "BOLD", MONO)
        d.text(1264, y + 1, what, 15, "#E2E8F0FF", "NORMAL", CJK)
    d.box(1180, 604, 380, 168, "#1B1114FF", radius=16, border=f"1 SOLID #7F1D1DFF")
    S.section_label(d, 1204, 620, "What the coastguard needs", "#FCA5A5FF", 15)
    for i, t in enumerate(["Vessel description and photos",
                           "Drift inputs: wind 18 kn 225°, stream 1.0 kn 048°",
                           "Medical notes for both POB",
                           "Fuel and water aboard at departure"]):
        d.circle(1210, 656 + i * 28, 3.5, S.AMBER_L)
        d.text(1224, 648 + i * 28, t, 15, "#E2E8F0FF", "NORMAL", CJK)

    # ---------------- bottom sweep table
    d.box(40, 796, 1520, 150, "#1B1114FF", radius=16, border=f"1 SOLID #7F1D1DFF")
    S.section_label(d, 64, 812, "Search boxes and sweep times", "#FCA5A5FF", 15)
    heads = ["BOX", "PROBABILITY", "AREA", "BOAT 12 kn", "HELI 90 kn"]
    xs = [64, 220, 560, 760, 1010]
    for h_, x_ in zip(heads, xs):
        d.text(x_, 844, h_, 15, "#94A3B8FF", "BOLD", INTER)
    for i, b in enumerate(drift["boxes"]):
        y = 874 + i * 24
        d.text(64, y, b["box"], 20, S.WHITE, "BOLD", INTER)
        S.bar(d, 220, y + 3, 260, 14, b["prob"], S.RED, "#3A2226FF")
        d.rtext(500, y - 2, 24, f'{int(b["prob"]*100)} %', 16, S.WHITE, weight="BOLD", family=MONO)
        d.text(560, y, f'{b["area_nm2"]} nm²', 17, "#E2E8F0FF", "NORMAL", MONO)
        d.text(760, y, f'{b["boat_hours"]} h', 17, "#E2E8F0FF", "NORMAL", MONO)
        d.text(1010, y, f'{b["heli_min"]} min', 17, "#E2E8F0FF", "NORMAL", MONO)
    d.text(1200, 844, "SEARCH ORDER", 15, "#94A3B8FF", "BOLD", INTER)
    d.text(1200, 872, "A → B → C, then re-sweep A on the", 16, "#E2E8F0FF", "NORMAL", CJK)
    d.text(1200, 896, "next slack water with the drift re-run", 16, "#E2E8F0FF", "NORMAL", CJK)
    d.text(1200, 924, "at 19:20. Probability halves every 3 h.", 15, "#94A3B8FF", "NORMAL", CJK)
    return d.finish()


# =====================================================================  case-08
def case08(D, ver="v1") -> str:
    """Fuel and range planner - 1180x820, dark instrument panel."""
    W, H = 1180, 820
    d = Doc(W, H, S.NAVY)
    fuel, route = D["fuel"], D["route"]
    S.header(d, W, "Fuel and range · Petrel", "36 L in two 18 L tanks · burn 8.2 L/h at 12 kn · "
             "1.1 L/h drifting · reserve 20 %", [("PLANNED 3 OCT", S.WHITE, 20, "BOLD"),
                                                 ("17.6 nm · 88 min running", S.SLATE, 16, "NORMAL")],
             h=112, accent=S.AMBER)

    # ---------------- fuel ladder
    d.box(24, 132, 720, 330, S.NAVY2, radius=16, border=f"1 SOLID {S.DARKLINE}")
    S.section_label(d, 48, 150, "Fuel ladder — where the 36 L goes", S.MUTED, 16)
    scale = 660 / fuel["tank_l"]
    segs = [("run", fuel["calm"]["run_l"], S.SKY), ("drift", fuel["calm"]["drift_l"], S.TEAL),
            ("margin", fuel["calm"]["margin_l"], "#475569FF"), ("reserve", fuel["calm"]["reserve_l"], S.AMBER)]
    segs_hw = [("run", fuel["headwind12"]["run_l"], S.SKY), ("drift", fuel["headwind12"]["drift_l"], S.TEAL),
               ("margin", fuel["headwind12"]["margin_l"], "#475569FF"),
               ("reserve", fuel["headwind12"]["reserve_l"], S.AMBER)]
    for row, (label, items, note) in enumerate([
            ("Calm day · 19.5 L used (54 %)", segs, "wind SW 12–15 kn, stream with you"),
            ("12 kn headwind home · 22.9 L used (64 %)", segs_hw, "gusts 20 kn after 13:00")]):
        y = 200 + row * 100
        d.text(48, y - 26, label, 19, S.WHITE, "BOLD", CJK)
        d.rtext(720, y - 26, 22, note, 15, S.SLATE)
        x = 48
        for name, litres, col in items:
            wpx = litres * scale
            d.box(x, y, wpx, 52, col)
            if wpx > 70:
                d.text(x + 10, y + 8, f"{litres:g} L", 20, "#0B1B2BFF" if col != "#475569FF" else S.WHITE,
                       "BOLD", MONO)
                d.text(x + 10, y + 32, name, 14, "#0B1B2BFF" if col != "#475569FF" else S.SLATE,
                       "NORMAL", INTER)
            x += wpx
    for i in range(5):
        x = 48 + i * 165
        d.box(x, 392, 1, 8, S.DARKLINE)
        d.ctext(x, 400, 20, str(int(i * 9)), 13, S.MUTED, "NORMAL", MONO, pad=6)
    d.text(48, 428, "grey = margin above the reserve · amber = the 7.2 L reserve you do not plan to touch",
           15, S.SLATE, "NORMAL", CJK)

    # ---------------- range by speed
    d.box(764, 132, 392, 330, S.NAVY2, radius=16, border=f"1 SOLID {S.DARKLINE}")
    S.section_label(d, 788, 150, "Range on 28.8 usable litres", S.MUTED, 16)
    rmax = max(r["range_nm"] for r in fuel["range_by_speed"])
    for i, r in enumerate(fuel["range_by_speed"]):
        y = 186 + i * 50
        d.text(788, y, f'{r["kn"]:g} kn', 19, S.WHITE, "BOLD", MONO)
        d.text(788, y + 22, f'{r["lph"]:g} L/h', 14, S.MUTED, "NORMAL", MONO)
        S.bar(d, 856, y + 4, 220, 18, r["range_nm"] / rmax, S.TEAL if i < 4 else S.RED, "#1B3550FF")
        d.rtext(1140, y - 2, 26, f'{r["range_nm"]:g} nm', 17, S.WHITE, weight="BOLD", family=MONO)
    d.text(788, 440, "Slowing from 12 kn to 8 kn nearly doubles the range.", 15, S.AMBER_L,
           "NORMAL", CJK)

    # ---------------- scenarios
    d.box(24, 478, 720, 204, S.NAVY2, radius=16, border=f"1 SOLID {S.DARKLINE}")
    S.section_label(d, 48, 494, "Scenarios", S.MUTED, 16)
    heads = [("SCENARIO", 48), ("RUN", 280), ("DRIFT", 370), ("TOTAL", 460),
             ("% TANK", 545), ("MARGIN L / nm", 620)]
    for h_, x_ in heads:
        d.text(x_, 524, h_, 14, S.MUTED, "BOLD", INTER)
    rows = [("calm", "Calm day", S.TEAL_L), ("headwind12", "12 kn headwind home", S.AMBER_L),
            ("foul_current", "1.5 kn foul stream", S.AMBER_L)]
    for i, (key, label, col) in enumerate(rows):
        f = fuel[key]
        y = 552 + i * 36
        d.text(48, y, label, 18, col, "BOLD", CJK)
        d.text(280, y, f'{f["run_l"]:g} L', 17, S.WHITE, "NORMAL", MONO)
        d.text(370, y, f'{f["drift_l"]:g} L', 17, S.WHITE, "NORMAL", MONO)
        d.text(460, y, f'{f["litres"]:g} L', 17, S.WHITE, "BOLD", MONO)
        d.text(545, y, f'{f["pct_of_tank"]} %', 17, S.WHITE, "NORMAL", MONO)
        d.text(620, y, f'{f["margin_l"]:g} / {f["margin_nm"]:g}', 16, col, "BOLD", MONO)
    d.text(48, 664, "The 12 kn headwind case leaves 5.9 L above reserve — 8.6 nm of running. "
                    "That is the case to plan against.", 15, S.SLATE, "NORMAL", CJK)

    # ---------------- recommendation
    d.box(764, 478, 392, 204, "#2A1F0BFF", radius=16, border=f"1 SOLID {S.AMBER}")
    S.section_label(d, 788, 494, "Recommendation", S.AMBER_L, 16)
    for i, t in enumerate(["Fill both tanks at the harbour — 36 L.",
                           "Take the spare can if gusts pass 20 kn.",
                           "If it blows up, run home at 8 kn.",
                           "Check fuel again at the 12:00 check-in.",
                           "Never plan to touch the 7.2 L reserve."]):
        d.circle(794, 532 + i * 30, 3.5, S.AMBER_L)
        d.text(808, 524 + i * 30, t, 15, "#FDE68AFF", "NORMAL", CJK)

    # ---------------- distance budget
    d.box(24, 698, 1132, 98, S.NAVY2, radius=16, border=f"1 SOLID {S.DARKLINE}")
    S.section_label(d, 48, 712, "Distance budget", S.MUTED, 15)
    dmax = 122.0
    items = [("plan today", route["total_nm"], S.TEAL), ("range at 12 kn", 42.1, S.SKY),
             ("range at 8 kn", 67.8, "#818CF8FF"), ("range at 5.5 kn", 121.8, "#A78BFAFF")]
    for i, (label, nm, col) in enumerate(items):
        y = 738 + (i % 2) * 26
        x = 48 + (i // 2) * 560
        d.text(x, y, label, 15, S.SLATE, "NORMAL", CJK)
        S.bar(d, x + 150, y + 2, 240 * nm / dmax, 12, 1.0, col, "#16283CFF")
        d.text(x + 400, y - 1, f"{nm:g} nm", 15, S.WHITE, "BOLD", MONO)
    return d.finish()


# =====================================================================  case-09
def case09(D, ver="v1") -> str:
    """Harbour office e-ink noticeboard - 800x1200 portrait, read from 2-3 m."""
    W, H = 800, 1200
    PAPER_E = "#EDEDE6FF"
    INKE = "#14161AFF"
    RED_E = "#B3261EFF"
    RULE = "#B9B6AAFF"
    d = Doc(W, H, PAPER_E)
    tide, plan = D["tide"], D["plan"]

    d.box(0, 0, W, 8, INKE)
    d.text(32, 26, "BRINDLEMOUTH HARBOUR OFFICE", 26, INKE, "BOLD", INTER, spacing=2)
    d.text(32, 68, "Noticeboard · Saturday 3 October 2026 · updated 07:05 · next 07:30",
           17, "#4A4A44FF", "NORMAL", CJK)
    d.rtext(W - 32, 30, 26, "SHEET 03", 17, "#4A4A44FF", weight="BOLD", family=MONO)
    d.box(32, 104, W - 64, 3, INKE)
    d.box(32, 111, W - 64, 1, RULE)

    # ---------------- fleet status
    d.text(32, 132, "FLEET STATUS · 9 VESSELS ON THE BOOK", 18, INKE, "BOLD", INTER, spacing=1)
    heads = [("VESSEL", 32, 180), ("TYPE", 212, 130), ("STATE", 342, 100), ("POB", 442, 60),
             ("DUE BACK", 502, 120), ("CHECK-IN", 622, 146)]
    for name, x, w in heads:
        d.text(x, 164, name, 14, "#5A5A52FF", "BOLD", INTER)
    d.box(32, 184, W - 64, 2, INKE)
    fleet = [("Petrel", "launch", "OUT", "2", "15:08", "09:00 ok", True),
             ("Kelda", "yacht", "OUT", "3", "14:30", "08:40 ok", False),
             ("Marrow", "RIB", "OUT", "2", "12:00", "11:50 late", False),
             ("Otter", "yacht", "OUT", "4", "17:00", "09:10 ok", False),
             ("Voe Star", "fishing", "OUT", "3", "18:30", "09:05 ok", False),
             ("Nimbus", "kayak", "OUT", "1", "13:00", "09:12 ok", False),
             ("Skua II", "launch", "IN", "—", "—", "—", False),
             ("Gannet", "launch", "IN", "—", "—", "—", False),
             ("Tern", "yacht", "IN", "—", "—", "—", False)]
    for i, (v, t, st, pob, due, chk, hl) in enumerate(fleet):
        y = 194 + i * 36
        if hl:
            d.box(28, y - 2, W - 56, 34, "#DCD9C8FF")
            d.box(28, y - 2, 5, 34, RED_E)
        d.text(40, y + 6, v, 19, INKE, "BOLD", CJK)
        d.text(212, y + 7, t, 16, "#3A3A34FF", "NORMAL", CJK)
        d.text(342, y + 7, st, 16, RED_E if st == "OUT" else "#3A3A34FF", "BOLD", INTER)
        d.text(448, y + 7, pob, 16, "#3A3A34FF", "NORMAL", MONO)
        d.text(502, y + 7, due, 16, "#3A3A34FF", "NORMAL", MONO)
        d.text(622, y + 7, chk, 15, "#3A3A34FF", "NORMAL", CJK)
    d.box(32, 524, W - 64, 1, RULE)
    d.text(32, 534, "Check-in = the last acknowledged position report. Boats over two hours late "
                    "are called on VHF 16.", 14, "#5A5A52FF", "NORMAL", CJK)

    # ---------------- notices
    d.text(32, 574, "NOTICES", 18, INKE, "BOLD", INTER, spacing=1)
    d.box(32, 600, W - 64, 2, INKE)
    notices = [("4–6 OCT", "Dredging in the approach channel, 06:00–18:00 daily. Keep 50 m clear of "
                           "the dredger and do not anchor in the fairway."),
               ("SUN 4 OCT", "Autumn dinghy race, first start 11:00 from the west pier. Cruising "
                             "craft give way; race control on VHF 72."),
               ("C PONTOON", "Mooring line fouled on C7. Do not berth on C7 until the diver has "
                             "cleared it — expected 5 October."),
               ("FUEL DOCK", "Winter hours from 1 October: closes 17:00. Card payments only after "
                             "16:30.")]
    for i, (tag, txt) in enumerate(notices):
        y = 616 + i * 72
        d.box(32, y, 108, 26, INKE)
        d.tbox(32, y, 108, 26, tag, 13, PAPER_E, "CENTER", "BOLD", INTER)
        d.para(152, y - 2, W - 200, txt, 16, "#26261FFF")

    # ---------------- gates and weather
    d.box(32, 918, W - 64, 2, INKE)
    d.text(32, 934, "TODAY'S BANK GATE", 17, INKE, "BOLD", INTER)
    d.text(32, 962, "Old Keel Bank needs 2.50 m over the drying height.", 15, "#4A4A44FF",
           "NORMAL", CJK)
    for i, g in enumerate(tide["gate_windows"]):
        y = 990 + i * 30
        d.text(32, y, "OPEN", 17, "#1F6B3AFF", "BOLD", INTER)
        d.text(96, y, f'{g["from"]} – {g["to"]}', 19, INKE, "BOLD", MONO)
        d.text(260, y + 2, f'peak {g["peak"]:.2f} m', 15, "#4A4A44FF", "NORMAL", MONO)
    d.box(440, 934, 2, 118, RULE)
    d.text(468, 934, "WEATHER WARNING", 17, RED_E, "BOLD", INTER)
    d.text(468, 962, "YELLOW · SW 18 gust 26 kn after 15:00.", 15, "#4A4A44FF", "NORMAL", CJK)
    d.text(468, 984, "Sea 0.8 m. Small craft: re-check your plan.", 15, "#4A4A44FF", "NORMAL", CJK)
    d.text(468, 1006, "Sunset 17:44 · civil dusk 18:14.", 15, "#4A4A44FF", "NORMAL", CJK)
    d.text(468, 1028, "Petrel due 15:08 — inside the window.", 15, RED_E, "BOLD", CJK)

    # ---------------- footer
    d.box(32, 1076, W - 64, 3, INKE)
    d.box(32, 1083, W - 64, 1, RULE)
    d.text(32, 1098, "Harbour office VHF 72 · 0131 555 0100 (fictional) · "
                     "emergencies VHF 16 / 999", 15, INKE, "BOLD", CJK)
    d.text(32, 1126, "Posted 07:05 by the harbour master's office. This board is a summary; "
                     "it is not a navigation document.", 13, "#5A5A52FF", "NORMAL", CJK)
    d.text(32, 1152, "Kelpline supplies the check-in column automatically from filed float plans.",
           13, "#5A5A52FF", "NORMAL", CJK)
    return d.finish()


# =====================================================================  case-10
def case10(D, ver="v1") -> str:
    """Season debrief - 1600x1000 light analytics surface."""
    W, H = 1600, 1000
    d = Doc(W, H, S.LIGHT)
    db, fuel = D["debrief"], D["fuel"]
    S.header(d, W, "Season debrief · Petrel, April–October 2026",
             "Logged by the skipper, analysed by Kelpline · 26 trips · 60.3 h under way · 556 nm",
             [("CLOSE OF SEASON", S.WHITE, 20, "BOLD"),
              ("generated 3 Oct 2026 · 18:40", S.SLATE, 16, "NORMAL")],
             h=112, accent=S.TEAL)

    kpis = [("Trips logged", "26", "Apr–Oct 2026", S.BLUE),
            ("Hours under way", "60.3", "average 2.3 h per trip", S.TEAL),
            ("Distance", "556 nm", "average 21.4 nm per trip", S.NAVY),
            ("Close calls", "3", "all logged with a rule adopted", S.RED)]
    for i, (label, val, sub, col) in enumerate(kpis):
        x = 40 + i * 384
        d.box(x, 132, 368, 104, S.WHITE, radius=14, border=f"1 SOLID {S.LINE}")
        d.box(x, 132, 6, 104, col, tl=14, bl=14)
        d.text(x + 24, 144, label.upper(), 14, S.MUTED, "BOLD", INTER, spacing=1)
        d.text(x + 22, 162, val, 40, S.INK, "BOLD", INTER)
        d.text(x + 24, 210, sub, 13, S.MUTED, "NORMAL", CJK)

    # ---- trips by month
    d.box(40, 262, 740, 320, S.WHITE, radius=14, border=f"1 SOLID {S.LINE}")
    S.section_label(d, 64, 278, "Distance and trips by month", S.MUTED, 15)
    S.season = db["season"]
    maxnm = max(m["nm"] for m in db["season"])
    bx, bw = 92, 78
    for i, m in enumerate(db["season"]):
        x = bx + i * 96
        hgt = 200 * m["nm"] / maxnm
        d.box(x, 520 - hgt, bw, hgt, S.BLUE if m["trips"] > 3 else "#93C5FDFF", tl=6, tr=6)
        d.ctext(x + bw / 2, 500 - hgt, 24, f'{m["nm"]:g}', 14, S.INK, "BOLD", MONO, pad=8)
        d.ctext(x + bw / 2, 528, 24, m["month"], 15, S.MUTED, "BOLD", INTER, pad=8)
        d.ctext(x + bw / 2, 548, 24, f'{m["trips"]} trips', 13, S.MUTED, "NORMAL", CJK, pad=8)
    d.box(64, 520, 700, 2, S.LINE2)
    d.text(64, 566, "Bars are nautical miles; the label under each month is the trip count. "
                    "July and August carry 45 % of the season.", 14, S.MUTED, "NORMAL", CJK)

    # ---- forecast error
    d.box(800, 262, 760, 320, S.WHITE, radius=14, border=f"1 SOLID {S.LINE}")
    S.section_label(d, 824, 278, "Forecast wind error against what you actually met", S.MUTED, 15)
    fx, fy, fw, fh = 864, 330, 660, 190
    for kn in (0, 2, 4, 6, 8):
        yy = fy + fh - kn / 8 * fh
        d.box(fx, yy, fw, 1, S.LINE)
        d.rtext(fx - 10, yy - 11, 20, str(kn), 13, S.MUTED, weight="NORMAL", family=MONO)
    band = fy + fh - 5 / 8 * fh
    d.box(fx, band, fw, fy + fh - band, "#FEE2E2FF")
    d.text(fx + 10, band + 6, "over 5 kn of error — 11 of 26 trips", 14, "#B42318FF", "BOLD", CJK)
    pts = []
    for i, fe in enumerate(db["forecast_error"]):
        x = fx + fw * i / (len(db["forecast_error"]) - 1)
        y = fy + fh - fe["mean_err_kn"] / 8 * fh
        pts.append((x, y))
    d.poly(pts, S.RED, 3.5)
    for i, (fe, p) in enumerate(zip(db["forecast_error"], pts)):
        d.circle(p[0], p[1], 6, S.WHITE, border=f"3 SOLID {S.RED}")
        d.ctext(p[0], p[1] - 30, 22, f'{fe["mean_err_kn"]:g}', 14, S.RED, "BOLD", MONO, pad=6)
        d.ctext(p[0], fy + fh + 8, 22, fe["month"], 14, S.MUTED, "NORMAL", INTER, pad=6)
    d.text(824, 552, "Mean absolute error between the 06:00 inshore forecast and the "
                     "boat's own wind readings.", 14, S.MUTED, "NORMAL", CJK)

    # ---- close calls
    d.box(40, 606, 900, 262, S.WHITE, radius=14, border=f"1 SOLID {S.LINE}")
    S.section_label(d, 64, 622, "Close-call log", S.MUTED, 15)
    for i, cc in enumerate(db["close_calls"]):
        y = 654 + i * 70
        d.box(64, y, 6, 54, S.AMBER, radius=3)
        d.text(82, y - 2, cc["date"], 15, S.MUTED, "BOLD", MONO)
        d.text(180, y - 3, cc["what"], 17, S.INK, "BOLD", CJK)
        d.text(180, y + 22, "Cause: " + cc["cause"], 14, S.MUTED, "NORMAL", CJK)
        d.text(180, y + 42, "Rule now: " + cc["rule"], 14, S.TEAL_D, "BOLD", CJK)

    # ---- patterns
    d.box(960, 606, 600, 262, S.NAVY, radius=14)
    S.section_label(d, 984, 622, "Patterns worth acting on", S.TEAL_L, 15)
    for i, t in enumerate([
        "Return legs run 1.4 kn slower than planned — add 20 min to every homeward ETA.",
        "Forecast error grows through the season: 2.4 kn in June, 7.1 kn by October.",
        "Two of three close calls happened after 13:00 — the afternoon is your risk window.",
        "Fuel margin was under 15 % on four trips, all with drift time over 4 h.",
    ]):
        d.circle(980, 664 + i * 46, 4, S.TEAL)
        d.para(996, 652 + i * 46, 540, t, 16, "#E2E8F0FF")

    # ---- bottom
    d.box(40, 884, 1520, 84, S.WHITE, radius=14, border=f"1 SOLID {S.LINE}")
    S.section_label(d, 64, 898, "Adopted for next season", S.MUTED, 15)
    for i, t in enumerate(["06:00 forecast check before every slip",
                           "Bank gate fixed at 2.50 m, entry and return",
                           "Fuel planned with the 12 kn headwind case",
                           "Afternoon trips need a second POB check-in"]):
        x = 64 + i * 372
        d.box(x, 926, 16, 16, S.TEAL, radius=4)
        d.seg(x + 4, 934, x + 7, 938, S.WHITE, 2.5)
        d.seg(x + 7, 938, x + 12, 929, S.WHITE, 2.5)
        d.text(x + 26, 924, t, 15, S.INK2, "NORMAL", CJK)
    return d.finish()
