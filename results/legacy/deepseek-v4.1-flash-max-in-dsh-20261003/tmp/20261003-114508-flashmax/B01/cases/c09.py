# -*- coding: utf-8 -*-
"""B01 case-09 -- 仪表进近图（虚构机场，教学用）.

All bearings, distances, altitudes and descent gradients are computed from the
procedure definition with real trigonometry; the plan view, the profile view and
the minima table are generated from the same numbers.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kit import Doc, CJK, MONO, clip, tw  # noqa: E402

NAME = "c09-approach-chart"
W, H = 1500, 1050

BG = "#FBFBF6FF"
PANEL = "#FFFFFFFF"
INK = "#12181FFF"
DIMC = "#5A6672FF"
SUB = "#98A2AEFF"
MAG = "#C2185BFF"
BLU = "#1565C0FF"
GRN = "#2E7D32FF"
RUL = "#C9CFD6FF"

ICAO = "ZZYC"
ARP = (700.0, 400.0)         # VOR position inside the plan view
VOR_FREQ = "114.30"
FINAL_CRS = 245.0            # degrees magnetic
RWY = "07"
FAF_DME = 6.4                # nm from VOR
MAP_DME = 0.6
IAF_DME = 14.0
FAF_ALT = 2600
MDA = 640
TDZE = 118
GS_ANGLE = 3.00
SCALE = 16.4                 # px per nm in the plan view


def pol(cx, cy, bearing, dist):
    """Plan-view point for a magnetic bearing and a distance in nm."""
    a = math.radians(bearing - 90)     # 0 deg = up
    return cx + math.cos(a) * dist * SCALE, cy + math.sin(a) * dist * SCALE


def sdeg(bearing):
    """Screen rotation for a box whose local +x axis should point at `bearing`."""
    return bearing - 90.0


def build(ver="v1", outdir=None):
    descent = (FAF_ALT - TDZE) / (FAF_DME * 6076.12)
    grad_pct = descent * 100
    data = {
        "airport": ICAO + " / 云岭（虚构）", "runway": RWY, "vor_freq": VOR_FREQ,
        "final_course_mag": FINAL_CRS, "iaf_dme_nm": IAF_DME, "faf_dme_nm": FAF_DME,
        "map_dme_nm": MAP_DME, "faf_alt_ft": FAF_ALT, "mda_ft": MDA, "tdze_ft": TDZE,
        "glidepath_deg": GS_ANGLE,
        "descent_gradient_pct": round(grad_pct, 2),
        "descent_ft_per_nm": round((FAF_ALT - TDZE) / FAF_DME, 1),
        "faf_to_map_nm": round(FAF_DME - MAP_DME, 2),
        "minima": [{"cat": "A", "mda": MDA, "vis_m": 1600},
                   {"cat": "B", "mda": MDA, "vis_m": 1600},
                   {"cat": "C", "mda": MDA + 40, "vis_m": 2400},
                   {"cat": "D", "mda": MDA + 60, "vis_m": 3200}],
        "note": "虚构机场与程序，仅用于演示；不可用于真实飞行。",
    }

    d = Doc(W, H, BG)
    # ---------------------------------------------------------------- header
    d.box(0, 0, W, 86, "#12181FFF")
    d.text(28, 14, "仪表进近图 · VOR/DME RWY %s" % RWY, 26, "#FFFFFFFF", "BOLD")
    d.text(28, 50, "%s · 云岭（虚构机场）· 跑道标高 %d ft · 磁差 4°W · 平面图 1 NM ≈ %.0f px"
           % (ICAO, TDZE, SCALE), 16, "#9AA6B4FF")
    d.ctext(1000, 16, "VOR %s MHz · 最终进近航向 %03.0f°M" % (VOR_FREQ, FINAL_CRS),
            17, "#FFD166FF", "BOLD", w=472, h=24, align="CENTER_RIGHT")
    d.ctext(1000, 48, "下滑角 %.2f° · 梯度 %.1f %% · %.0f ft/NM"
            % (GS_ANGLE, grad_pct, data["descent_ft_per_nm"]), 17, "#7DD3FCFF",
            w=472, h=24, align="CENTER_RIGHT")

    # ---------------------------------------------------------------- plan view
    PX, PY, PW, PH = 28, 100, 936, 600
    d.box(PX, PY, PW, PH, PANEL, radius=8, border="1 SOLID " + RUL)
    d.text(PX + 16, PY + 12, "平面图 PLAN VIEW", 15, INK, "BOLD")
    d.text(PX + PW - 210, PY + 12, "距离以 VOR/DME 为准（NM）", 13, DIMC)

    # compass rose: thin DME rings, radial ticks every 10 deg, labels every 30 deg.
    # Rings are stroked arcs built from short bars, so they are kept coarse -- the
    # service caps one document at 4096 elements.
    for r in (4, 8, 12, 14):
        d.ring(ARP[0], ARP[1], r * SCALE, 1.0, "#DCE1E6FF", step=13.0)
    d.ring(ARP[0], ARP[1], 8 * SCALE, 1.4, "#B9C1C9FF", step=13.0)
    for k in range(0, 360, 10):
        r0, r1 = (8.0, 8.5) if k % 30 else (8.0, 8.9)
        a = math.radians(k)
        d.seg(ARP[0] + math.cos(a) * r0 * SCALE, ARP[1] + math.sin(a) * r0 * SCALE,
              ARP[0] + math.cos(a) * r1 * SCALE, ARP[1] + math.sin(a) * r1 * SCALE,
              INK, 1.6)
    for k in range(0, 360, 30):
        a = math.radians(k)
        lab = "%03d" % ((360 - k) % 360)
        d.ctext(ARP[0] + math.cos(a) * 9.7 * SCALE - 26,
                ARP[1] + math.sin(a) * 9.7 * SCALE - 10, lab, 14, INK, "BOLD",
                family=MONO, w=52, h=20, align="CENTER")
    d.ctext(ARP[0] + 9.7 * SCALE - 60, ARP[1] - 46, "DME 8 NM", 12, DIMC, w=120, h=18,
            align="CENTER")

    # final approach course (inbound on FINAL_CRS towards the VOR)
    for dme in (10.0, 3.0):
        x, y = pol(ARP[0], ARP[1], FINAL_CRS, dme)
        d.dashed(x, y, ARP[0], ARP[1], MAG, 1.6, 9, 6)
    xa, ya = pol(ARP[0], ARP[1], FINAL_CRS, IAF_DME + 0.5)
    d.seg(xa, ya, ARP[0], ARP[1], MAG, 3)
    # runway strip: a real runway is ~1.5 NM long, so at this chart scale it is a
    # short bar centred on the field rather than a bar spanning the whole rose
    rlen = 2.6 * SCALE
    rx0, ry0 = pol(ARP[0], ARP[1], FINAL_CRS - 180, 1.3)
    rx1, ry1 = pol(ARP[0], ARP[1], FINAL_CRS - 180, -1.3)
    d.rbox((rx0 + rx1) / 2, (ry0 + ry1) / 2, rlen, 15, sdeg(FINAL_CRS - 180), INK)
    d.rbox((rx0 + rx1) / 2, (ry0 + ry1) / 2, rlen, 2, sdeg(FINAL_CRS - 180), "#FFFFFFFF")

    # procedure turn barb at the IAF (drawn in screen space: at this chart scale a
    # real 45/180 turn is only ~30 px across)
    tx, ty = pol(ARP[0], ARP[1], FINAL_CRS, IAF_DME)
    d.disc(tx, ty, 13, MAG)
    d.seg(tx, ty, tx + 34, ty - 15, MAG, 2.4)
    d.seg(tx + 34, ty - 15, tx + 62, ty + 6, MAG, 2.4)
    d.seg(tx + 62, ty + 6, tx + 30, ty + 22, MAG, 2.4)
    d.ctext(tx - 158, ty - 104, "程序转弯 45/180", 13, MAG, w=170, h=20)

    # fixes
    fixes = [("IAF", IAF_DME, "云岭 VOR · 14.0", 0), ("FAF", FAF_DME, "%.1f DME" % FAF_DME, -1),
             ("MAPt", MAP_DME, "%.1f DME" % MAP_DME, 1)]
    for name, dme, sub, side in fixes:
        x, y = pol(ARP[0], ARP[1], FINAL_CRS, dme)
        if name != "IAF":
            d.disc(x, y, 12, "#FFFFFFFF")
            d.disc(x, y, 8, MAG)
        d.box(x - 44, y + 22 + side * 34, 88, 22, PANEL, radius=4,
              border="1 SOLID " + MAG)
        d.ctext(x - 44, y + 22 + side * 34, name, 13, MAG, "BOLD", w=88, h=22,
                align="CENTER")
        d.box(x - 56, y + 44 + side * 34, 112, 18, "#FFFFFFFF", radius=3)
        d.ctext(x - 56, y + 44 + side * 34, sub, 12, DIMC, family=MONO, w=112, h=18,
                align="CENTER")

    # VOR symbol and ident, placed clear of the runway bar and the course line
    d.disc(ARP[0], ARP[1], 26, "#FFFFFFFF", border="2 SOLID " + INK)
    for k in range(0, 360, 60):
        a = math.radians(k)
        d.seg(ARP[0] + math.cos(a) * 6, ARP[1] + math.sin(a) * 6,
              ARP[0] + math.cos(a) * 13, ARP[1] + math.sin(a) * 13, INK, 1.6)
    d.box(ARP[0] - 20, ARP[1] - 34, 150, 20, "#FFFFFFFF", radius=3)
    d.text(ARP[0] - 16, ARP[1] - 32, "RWY %s · %d ft" % (RWY, TDZE), 12, INK, "BOLD")
    d.box(ARP[0] + 26, ARP[1] - 66, 130, 20, "#FFFFFFFF", radius=3)
    d.text(ARP[0] + 30, ARP[1] - 64, "%s / %s" % (ICAO, VOR_FREQ), 13, INK, "BOLD")

    # left-hand annotation block
    d.text(PX + 20, PY + 40, "平面图说明", 14, INK, "BOLD")
    for i, s in enumerate([
            "细圆 = DME 距离环（4 / 8 / 12 / 14 NM）",
            "粗圆 = 8 NM 参考环，刻度每 10°",
            "数字 = 以 VOR 为基准的磁方位",
            "洋红 = 进近航迹与复飞保护区边界",
            "程序转弯位于 IAF，出航 45°，转弯 180°"]):
        d.ctext(PX + 20, PY + 66 + i * 24, clip(s, 13, 330), 13, DIMC, w=330, h=20)
    d.box(PX + 20, PY + 200, 330, 1, RUL)
    d.ctext(PX + 20, PY + 210, "MSA 以 VOR 为圆心 25 NM：", 13, INK, "BOLD", w=330, h=20)
    d.ctext(PX + 20, PY + 230, "扇区 090–270 为 5400 ft，其余 4200 ft", 13, DIMC, w=330,
            h=20)
    d.box(PX + PW - 200, PY + PH - 40, 180, 26, "#FFF7E0FF", radius=4,
          border="1 SOLID #E0B84CFF")
    d.ctext(PX + PW - 200, PY + PH - 40, "比例 1 NM ≈ %.0f px" % SCALE, 12,
            "#8A6D1CFF", w=180, h=26, align="CENTER")

    # ---------------------------------------------------------------- right column
    RX, RW = 984, 488
    d.box(RX, 100, RW, 208, PANEL, radius=8, border="1 SOLID " + RUL)
    d.text(RX + 16, 112, "最低标准 MINIMA", 15, INK, "BOLD")
    d.text(RX + 16, 142, "类别", 12, DIMC)
    d.ctext(RX + 110, 140, "MDA/H", 12, DIMC, w=110, h=18, align="CENTER_RIGHT")
    d.ctext(RX + 260, 140, "能见度", 12, DIMC, w=110, h=18, align="CENTER_RIGHT")
    d.ctext(RX + 372, 140, "复飞爬升", 12, DIMC, w=100, h=18, align="CENTER_RIGHT")
    d.box(RX + 16, 162, RW - 32, 1, RUL)
    for i, m in enumerate(data["minima"]):
        y = 172 + i * 30
        d.ctext(RX + 16, y, m["cat"], 16, INK, "BOLD", family=MONO, w=70, h=22)
        d.ctext(RX + 110, y + 1, "%d ft" % m["mda"], 16, INK, family=MONO, w=110,
                h=22, align="CENTER_RIGHT")
        d.ctext(RX + 260, y + 1, "%d m" % m["vis_m"], 16, INK, family=MONO, w=110,
                h=22, align="CENTER_RIGHT")
        d.ctext(RX + 372, y + 1, "%d ft/NM" % (200 if m["cat"] in "AB" else 250), 15,
                DIMC, family=MONO, w=100, h=22, align="CENTER_RIGHT")
    d.box(RX + 16, 296 - 4, RW - 32, 1, RUL)

    d.box(RX, 320, RW, 200, PANEL, radius=8, border="1 SOLID " + RUL)
    d.text(RX + 16, 332, "复飞 MISSED APPROACH", 15, INK, "BOLD")
    for i, s in enumerate([
            "爬升至 2400 ft 后左转",
            "切入 114.30 VOR 的 R-155 径向线",
            "沿 R-155 爬升到 4200 ft 加入等待",
            "等待航向 155° 右转，1 分钟腿"]):
        y = 362 + i * 30
        d.ctext(RX + 16, y, "%d" % (i + 1), 14, MAG, "BOLD", family=MONO, w=24, h=22)
        d.ctext(RX + 46, y, clip(s, 15, 420), 15, INK, w=420, h=22)
    d.ctext(RX + 16, 484, "复飞爬升梯度按 200 ft/NM 计算，至 2400 ft 后转向。", 12, DIMC,
            w=RW - 32, h=18)

    d.box(RX, 532, RW, 168, "#FFF9E8FF", radius=8, border="1 SOLID #E0B84CFF")
    d.text(RX + 16, 544, "使用限制（演示）", 15, "#8A6D1CFF", "BOLD")
    for i, s in enumerate([
            "本图为虚构机场与虚构程序，不可用于真实飞行",
            "DME 弧进近仅限同向跑道使用",
            "MDA 640 ft 对应离地约 %d ft" % (MDA - TDZE),
            "夜间进近需开启跑道边灯（示例）"]):
        d.ctext(RX + 16, 574 + i * 30, clip(s, 14, RW - 32), 14, "#7A5F14FF",
                w=RW - 32, h=22)

    # ---------------------------------------------------------------- profile
    FX, FY, FW, FH = 28, 716, 1440, 220
    d.box(FX, FY, FW, FH, PANEL, radius=8, border="1 SOLID " + RUL)
    d.text(FX + 16, FY + 12, "剖面图 PROFILE VIEW", 15, INK, "BOLD")
    d.ctext(FX + 900, FY + 14, "垂直夸大：水平 1 NM = 150 px，垂直 1000 ft = 38 px",
            12, DIMC, w=520, h=18, align="CENTER_RIGHT")
    d.ctext(FX + 16, FY + 36, "进近剖面：%.0f ft / %.1f NM = %.1f ft/NM（%.1f %%），"
            "FAF 至 MAPt 共 %.2f NM。" % (FAF_ALT - TDZE, FAF_DME,
                                          data["descent_ft_per_nm"], grad_pct,
                                          data["faf_to_map_nm"]),
            13, DIMC, w=880, h=18)
    px0, px1 = FX + 70, FX + 880
    py0, py1 = FY + 64, FY + 168
    ALTI, ALTH = 0, 3000

    def PXf(nm):
        return px1 - (nm / (IAF_DME + 1.5)) * (px1 - px0)

    def PYf(ft):
        return py1 - (ft - ALTI) / float(ALTH - ALTI) * (py1 - py0)

    for ft in range(0, 3001, 500):
        y = PYf(ft)
        d.box(px0, y, px1 - px0, 1, "#EDF0F3FF")
        d.ctext(px0 - 62, y - 10, "%d" % ft, 12, DIMC, family=MONO, w=56, h=20,
                align="CENTER_RIGHT")
    for nm in (IAF_DME, 10, FAF_DME, 3, MAP_DME):
        x = PXf(nm)
        d.dashed(x, py0, x, py1, "#D7DCE1FF", 1, 6, 5)
        d.ctext(x - 40, py1 + 4, "%.1f" % nm, 12, DIMC, family=MONO, w=80, h=18,
                align="CENTER")
    d.ctext(px1 - 60, py1 + 22, "DME NM", 12, DIMC, w=120, h=18, align="CENTER_RIGHT")
    # descent path
    d.seg(PXf(IAF_DME), PYf(2600), PXf(FAF_DME), PYf(FAF_ALT), MAG, 3)
    d.seg(PXf(FAF_DME), PYf(FAF_ALT), PXf(MAP_DME), PYf(TDZE), MAG, 3)
    d.box(PXf(MAP_DME) - 40, PYf(TDZE) - 3, 84, 6, INK)
    for nm, ft, lab in ((IAF_DME, 2600, "2600"), (FAF_DME, FAF_ALT, "2600"),
                        (MAP_DME, TDZE, "TDZE %d" % TDZE)):
        x, y = PXf(nm), PYf(ft)
        d.disc(x, y, 10, MAG)
        d.ctext(x - 50, y - 30, lab, 13, MAG, "BOLD", family=MONO, w=100, h=20,
                align="CENTER")
    # missed approach climb
    d.seg(PXf(MAP_DME), PYf(TDZE), PXf(0.0), PYf(2400), GRN, 3)
    d.ctext(PXf(0.0) - 124, PYf(2400) - 30, "复飞 2400", 13, GRN, "BOLD", family=MONO,
            w=120, h=20, align="CENTER")

    # ---------------------------------------------------------------- footer
    d.box(28, 950, 1440, 84, "#F1F3F5FF", radius=8, border="1 SOLID " + RUL)
    d.ctext(44, 960, "本图由 Snapshot DSL 生成，为虚构机场 %s 的教学演示，所有频率、航向、高度均为示例数据；"
            "严禁用于真实飞行或导航。" % ICAO, 14, "#8A3A3AFF", "BOLD", w=1408, h=22)
    d.ctext(44, 986, "制图：Snapshot 演示作品 · 版本 R1 · 磁差 4°W（示例）· 单位：高度 ft，距离 NM，能见度 m",
            13, DIMC, w=1408, h=20)
    d.ctext(44, 1008, "平面图上的距离环、径向刻度与剖面图共用同一套 VOR/DME 距离定义，可逐项对照。",
            13, DIMC, w=1408, h=20)

    if outdir:
        d.save(os.path.join(outdir, "dsl", "%s.%s.snapshot" % (NAME, ver)))
        os.makedirs(os.path.join(outdir, "data"), exist_ok=True)
        with open(os.path.join(outdir, "data", "%s.json" % NAME), "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
    return d, data


if __name__ == "__main__":
    out = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _, info = build("v1", out)
    print(json.dumps(info, ensure_ascii=False, indent=2))
