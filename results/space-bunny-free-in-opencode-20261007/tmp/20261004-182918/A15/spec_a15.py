"""A15 shared spec: colours, geometry, text placement, and measurement regions.

All geometry constants come from programmatic PIL scans of
tasks/A15-reference-reconstruction/inputs/reference.png
(see reference-measurements*.json, reference-text-ink.json, calibration*.json).
The reference PNG is only observed, never embedded.
"""

# ------------------------------------------------------------------ palette
C = {
    "main_bg":      "#F3F6FBFF",
    "sidebar_bg":   "#14233CFF",
    "card":         "#FFFFFFFF",
    "card_border":  "#E2E8F1FF",
    "accent":       "#245CE4FF",
    "grid":         "#E7EDF5FF",
    "rowsep":       "#EBEFF5FF",
    "band":         "#F3F6FBFF",
    "strong":       "#18283FFF",
    "muted":        "#63748FFF",
    "green":        "#168267FF",
    "side_card":    "#233954FF",
    "nav_pill":     "#294467FF",
    "nav_dot_on":   "#64DBB6FF",
    "nav_dot_off":  "#7791B3FF",
    "nav_label_off": "#BECADDFF",
    "mint":         "#64DBB6FF",
    "side_manage":  "#B0C2D6FF",
    "dot_amber":    "#EAAF40FF",
    "pill_ip_bg":   "#E7EFFFFF",
    "pill_ip_tx":   "#245CE4FF",
    "pill_rv_bg":   "#FFF3D7FF",
    "pill_rv_tx":   "#9D6613FF",
    "pill_dn_bg":   "#DCF5ECFF",
    "pill_dn_tx":   "#168267FF",
    "colhead":      "#63748FFF",
    "due":          "#63748FFF",
    "footer":       "#7B8BA3FF",
    "white":        "#FFFFFFFF",
}

# ------------------------------------------------------------------ geometry
G = {
    "canvas": (1440, 900),
    "sidebar_w": 220,
    "content_left": 284,      # card x + 24
    "content_right": 1373,
    # KPI cards: (x, y, w, h)
    "kpi_cards": [(260, 138, 356, 144), (644, 138, 356, 144), (1028, 138, 356, 144)],
    "chart_card": (260, 310, 742, 286),
    "act_card": (1030, 310, 370, 286),
    "table_card": (260, 624, 1140, 218),
    "card_r": 12,
    "button": (1184, 43, 216, 48, 9),
    "button_r": 8,
    # sidebar
    "logo_outer": (30, 33, 28, 28, 7),
    "logo_hole": (38, 41, 12, 12, 3),
    "nav_pill": (18, 116, 184, 48, 8),
    "nav_dot_x": 35,
    "nav_items": [("Overview", 134), ("Projects", 198), ("Analytics", 262), ("Settings", 326)],
    "side_card": (22, 752, 176, 116, 12),
    # chart
    "grid_x": (333, 969),
    "grid_y": [405, 441, 477, 513, 549],
    "baseline_y": 549,          # value 0
    "px_per_unit": 1.2,         # (549-405)/120
    "bar_x": [357, 458, 559, 660, 761, 862],
    "bar_w": 54,
    "bar_r": 5,
    "bar_values": [54, 72, 63, 90, 81, 108],
    "ticks": [("120", 0), ("90", 30), ("60", 60), ("30", 90), ("0", 120)],
    # table
    "thead": (284, 688, 1090, 34),
    "thead_r": 2,
    "rowsep_y": [760, 795],
    "pill": (1028, 729, 148, 28, 8),   # x, y of first pill, w, h, r
    "pill_y": [729, 764, 799],
}

# ------------------------------------------------------------------ text table
# (key, string, ink_left, ink_top, font, size, color_key, letterSpacing)
INTER, MED, SEMI, BLACK, EB = ("Inter", "Inter Medium", "Inter Semi Bold",
                               "Inter Black", "Inter Extra Bold")

TEXT = [
    # sidebar
    ("brand", "NORTHSTAR", 73, 38, BLACK, 17, "white", 1.0),
    ("nav_overview", "Overview", 62, 126, MED, 19, "white", 0),
    ("nav_projects", "Projects", 63, 190, MED, 19, "nav_label_off", 0),
    ("nav_analytics", "Analytics", 62, 254, MED, 19, "nav_label_off", 0),
    ("nav_settings", "Settings", 63, 318, MED, 19, "nav_label_off", 0),
    ("side_label", "PRO WORKSPACE", 38, 770, EB, 12.5, "mint", 0.3),
    ("side_member", "12 team members", 38, 804, SEMI, 16, "white", 0),
    ("side_manage", "Manage access  \u2192", 39, 835, INTER, 14, "side_manage", 0),
    # page header
    ("title", "Workspace Overview", 260, 38, MED, 33, "strong", 0),
    ("subtitle", "Saturday, 07 November 2026", 261, 85, INTER, 18, "muted", 0),
    ("button_text", "Export report", 1237, 55, MED, 17, "white", 0),
    # KPI cards
    ("kpi1_label", "REVENUE", 284, 160, EB, 13, "muted", 0.6),
    ("kpi1_value", "\u00a5128,400", 284, 199, BLACK, 31, "strong", 0),
    ("kpi1_change", "+12.4%", 285, 246, SEMI, 16, "green", 0),
    ("kpi2_label", "ORDERS", 668, 160, EB, 13, "muted", 0.6),
    ("kpi2_value", "426", 669, 199, BLACK, 31, "strong", 0),
    ("kpi2_change", "+8.1%", 669, 246, SEMI, 16, "green", 0),
    ("kpi3_label", "REFUND RATE", 1052, 160, EB, 13, "muted", 0.6),
    ("kpi3_value", "3.2%", 1053, 199, BLACK, 31, "strong", 0),
    ("kpi3_change", "\u22120.8 pp", 1053, 246, SEMI, 16, "green", 0),
    # chart card
    ("chart_title", "Net revenue", 285, 336, SEMI, 22, "strong", 0),
    ("chart_period", "Apr \u2013 Sep", 896, 337, INTER, 17, "muted", 0),
    ("chart_unit", "\u00a5 thousand", 287, 375, INTER, 13, "muted", 0),
    ("ytick_120", "120", 299, 398, INTER, 13, "muted", 0),
    ("ytick_90", "90", 305, 434, INTER, 13, "muted", 0),
    ("ytick_60", "60", 305, 470, INTER, 13, "muted", 0),
    ("ytick_30", "30", 306, 506, INTER, 13, "muted", 0),
    ("ytick_0", "0", 313, 542, INTER, 13, "muted", 0),
    ("month_Apr", "Apr", 373, 560, INTER, 14, "muted", 0),
    ("month_May", "May", 472, 560, INTER, 14, "muted", 0),
    ("month_Jun", "Jun", 574, 560, INTER, 14, "muted", 0),
    ("month_Jul", "Jul", 678, 560, INTER, 14, "muted", 0),
    ("month_Aug", "Aug", 775, 560, INTER, 14, "muted", 0),
    ("month_Sep", "Sep", 876, 560, INTER, 14, "muted", 0),
    # activity card
    ("act_title", "Team activity", 1054, 335, SEMI, 22, "strong", 0),
    ("act1_title", "Design review", 1078, 395, SEMI, 17.4, "strong", 0),
    ("act1_time", "08:40", 1077, 422, INTER, 14, "muted", 0),
    ("act2_title", "Dataset updated", 1078, 455, SEMI, 17.4, "strong", 0),
    ("act2_time", "09:15", 1077, 482, INTER, 14, "muted", 0),
    ("act3_title", "Render complete", 1078, 515, SEMI, 17.4, "strong", 0),
    ("act3_time", "10:05", 1077, 542, INTER, 14, "muted", 0),
    # table card
    ("table_title", "Recent projects", 285, 645, SEMI, 22, "strong", 0),
    ("ch_project", "PROJECT", 298, 699, SEMI, 12, "colhead", 0),
    ("ch_owner", "OWNER", 782, 699, SEMI, 12, "colhead", 0),
    ("ch_status", "STATUS", 1033, 699, SEMI, 12, "colhead", 0),
    ("ch_due", "DUE", 1230, 699, SEMI, 12, "colhead", 0),
    ("r1_proj", "Atlas / Visual system", 298, 734, SEMI, 16, "strong", 0),
    ("r1_owner", "Lin Chuan", 783, 735, INTER, 16, "muted", 0),
    ("r1_status", "In progress", 1067, 736, SEMI, 13, "pill_ip_tx", 0),
    ("r1_due", "Nov 09", 1231, 735, INTER, 16, "due", 0),
    ("r2_proj", "Pulse / Dashboard", 299, 769, SEMI, 16, "strong", 0),
    ("r2_owner", "Zhou He", 783, 770, INTER, 16, "muted", 0),
    ("r2_status", "Review", 1079, 771, SEMI, 13, "pill_rv_tx", 0),
    ("r2_due", "Nov 11", 1231, 770, INTER, 16, "due", 0),
    ("r3_proj", "Orbit / Launch", 298, 804, SEMI, 16, "strong", 0),
    ("r3_owner", "Su Yan", 783, 805, INTER, 16, "muted", 0),
    ("r3_status", "Done", 1086, 806, SEMI, 13, "pill_dn_tx", 0),
    ("r3_due", "Nov 12", 1231, 805, INTER, 16, "due", 0),
    # footer
    ("footer", "All data is fictional \u00b7 Snapshot benchmark", 260, 867, INTER, 13,
     "footer", 0),
]

# ------------------------------------------------------------------ measure regions
# key -> (x0, x1, y0, y1, bg_hex, tol); identical to measure_text_ink.py so that the
# rendered image and the reference are measured by exactly the same code.
REGIONS = {
    "title": (250, 700, 28, 76, "#F3F6FB", 30),
    "subtitle": (250, 600, 80, 110, "#F3F6FB", 30),
    "button_text": (1210, 1390, 45, 90, "#245CE4", 30),
    "brand": (68, 210, 30, 60, "#14233C", 30),
    "nav_overview": (58, 195, 120, 150, "#294467", 26),
    "nav_projects": (58, 195, 184, 214, "#14233C", 26),
    "nav_analytics": (58, 195, 248, 278, "#14233C", 26),
    "nav_settings": (58, 195, 310, 342, "#14233C", 26),
    "side_label": (30, 190, 758, 790, "#233954", 26),
    "side_member": (30, 190, 790, 822, "#233954", 26),
    "side_manage": (30, 190, 824, 858, "#233954", 26),
    "kpi1_label": (278, 560, 152, 180, "#FFFFFF", 30),
    "kpi1_value": (278, 560, 190, 240, "#FFFFFF", 30),
    "kpi1_change": (278, 560, 242, 270, "#FFFFFF", 30),
    "kpi2_label": (662, 940, 152, 180, "#FFFFFF", 30),
    "kpi2_value": (662, 940, 190, 240, "#FFFFFF", 30),
    "kpi3_label": (1046, 1340, 152, 180, "#FFFFFF", 30),
    "kpi3_value": (1046, 1340, 190, 240, "#FFFFFF", 30),
    "chart_title": (278, 700, 326, 362, "#FFFFFF", 30),
    "chart_period": (820, 995, 328, 362, "#FFFFFF", 30),
    "chart_unit": (278, 500, 366, 396, "#FFFFFF", 30),
    "ytick_120": (283, 332, 392, 418, "#FFFFFF", 26),
    "ytick_90": (283, 332, 428, 454, "#FFFFFF", 26),
    "ytick_60": (283, 332, 464, 490, "#FFFFFF", 26),
    "ytick_30": (283, 332, 500, 526, "#FFFFFF", 26),
    "ytick_0": (283, 332, 536, 562, "#FFFFFF", 26),
    "month_Apr": (345, 425, 554, 580, "#FFFFFF", 26),
    "month_May": (445, 525, 554, 580, "#FFFFFF", 26),
    "month_Jun": (545, 625, 554, 580, "#FFFFFF", 26),
    "month_Jul": (645, 725, 554, 580, "#FFFFFF", 26),
    "month_Aug": (745, 825, 554, 580, "#FFFFFF", 26),
    "month_Sep": (848, 928, 554, 580, "#FFFFFF", 26),
    "act_title": (1050, 1300, 326, 362, "#FFFFFF", 30),
    "act1_title": (1072, 1300, 388, 414, "#FFFFFF", 26),
    "act1_time": (1072, 1300, 416, 442, "#FFFFFF", 26),
    "act2_title": (1072, 1300, 448, 474, "#FFFFFF", 26),
    "act2_time": (1072, 1300, 476, 502, "#FFFFFF", 26),
    "act3_title": (1072, 1300, 508, 534, "#FFFFFF", 26),
    "act3_time": (1072, 1300, 536, 562, "#FFFFFF", 26),
    "table_title": (278, 700, 634, 676, "#FFFFFF", 30),
    "ch_project": (290, 420, 692, 716, "#F3F6FB", 25),
    "ch_owner": (776, 900, 692, 716, "#F3F6FB", 25),
    "ch_status": (1026, 1140, 692, 716, "#F3F6FB", 25),
    "ch_due": (1222, 1330, 692, 716, "#F3F6FB", 25),
    "r1_proj": (290, 540, 728, 756, "#FFFFFF", 25),
    "r1_owner": (778, 920, 728, 756, "#FFFFFF", 25),
    "r1_status": (1040, 1164, 731, 755, "#E7EFFF", 25),
    "r1_due": (1224, 1340, 728, 756, "#FFFFFF", 25),
    "r2_proj": (290, 540, 763, 792, "#FFFFFF", 25),
    "r2_owner": (778, 920, 763, 792, "#FFFFFF", 25),
    "r2_status": (1040, 1164, 766, 790, "#FFF3D7", 25),
    "r2_due": (1224, 1340, 763, 792, "#FFFFFF", 25),
    "r3_proj": (290, 540, 798, 838, "#FFFFFF", 25),
    "r3_owner": (778, 920, 798, 838, "#FFFFFF", 25),
    "r3_status": (1040, 1164, 801, 825, "#DCF5EC", 25),
    "r3_due": (1224, 1340, 798, 838, "#FFFFFF", 25),
    "footer": (250, 700, 860, 886, "#F3F6FB", 30),
}

# ------------------------------------------------------------------ anchors
# key -> (ref_x, ref_y, what) ; measured structural anchors required by TASK.md
ANCHORS = [
    ("A01_sidebar_main_split", 220, 450, "sidebar / main background boundary (x)"),
    ("A02_sidebar_bottom", 900, 700, "canvas bottom-right quadrant (footer band)"),
    ("A03_kpi1_top_left", 260, 138, "KPI card 1 top-left corner"),
    ("A04_kpi3_right_edge", 1383, 200, "KPI card 3 right border"),
    ("A05_chart_card_left", 260, 310, "chart card left border"),
    ("A06_chart_card_right", 1001, 590, "chart card right border"),
    ("A07_act_card_left", 1030, 320, "activity card left border"),
    ("A08_act_card_right", 1399, 590, "activity card right border"),
    ("A09_chart_zero_line", 333, 549, "chart baseline / zero gridline"),
    ("A10_grid_top", 333, 405, "chart top gridline (120)"),
    ("A11_table_card_top", 260, 624, "table card top border"),
    ("A12_table_card_bottom", 260, 841, "table card bottom border"),
    ("A13_nav_selected_left", 18, 116, "selected nav pill top-left"),
    ("A14_nav_selected_bottom", 18, 163, "selected nav pill bottom-left"),
    ("A15_bar1_top", 357, 485, "Apr bar top-left"),
    ("A16_bar6_top", 862, 420, "Sep bar top-left"),
    ("A17_table_header_band", 284, 688, "table header band top-left"),
    ("A18_rowsep1", 284, 760, "first row separator left end"),
    ("A19_pill1", 1028, 729, "In progress pill top-left"),
    ("A20_sidecard", 22, 752, "sidebar pro-workspace card top-left"),
    ("A21_logo", 30, 33, "brand mark outer top-left"),
    ("A22_button", 1184, 43, "Export report button top-left"),
]
