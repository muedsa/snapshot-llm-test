import json

W, H = 1440, 900
C_BG_DARK = "#0F172A"
C_BG_LIGHT = "#F8FAFC"
C_CARD = "#FFFFFF"
C_TEXT = "#1F293B"
C_MUTED = "#64748B"
C_PRIMARY = "#2563EB"
C_SUCCESS = "#22C55E"
C_DANGER = "#DC2626"

FONT = "Noto Sans CJK SC,Inter"
FONT_I = "Inter"

def pos(x, y, w, h, color, radius=None):
    r = f' borderRadius="{r}"' if radius else ""
    return f'      <Positioned left="{x:.1f}" top="{y:.1f}" width="{w:.1f}" height="{h:.1f}"><Container color="{color}"{r}/></Positioned>'

def text(x, y, w, h, text, size=16, color=C_TEXT, bold=False, align="START"):
    b = ' fontStyle="BOLD"' if bold else ""
    al = f' textAlign="{align}"' if align != "LEFT" else ""
    return f'      <Positioned left="{x:.1f}" top="{y:.1f}" width="{w:.1f}" height="{h:.1f}">\n        <Text color="{color}" fontSize="{size}" fontFamily="{FONT}"{b}{al}>{text}</Text>\n      </Positioned>'

el = []
el.append('<Snapshot background="#FFFFFF" type="png">')
el.append(f'  <SizedBox width="{W}" height="{H}">')
el.append('    <Stack alignment="TOP_LEFT" clipBehavior="NONE">')

# Left sidebar - dark background
el.append(f'      <Positioned left="0" top="0" width="260" height="{H}">')
el.append(f'        <Container color="{C_BG_DARK}"/>')
el.append(f'      </Positioned>')

# Logo
el.append(f'      <Positioned left="40" top="40" width="32" height="32">')
el.append(f'        <Container color="#22C55E" borderRadius="8"/>')
el.append(f'      </Positioned>')
el.append(f'      <Positioned left="80" top="44" width="120" height="24">')
el.append(f'        <Text color="#FFFFFF" fontSize="20" fontStyle="BOLD" fontFamily="{FONT}">NORTHSTAR</Text>')
el.append(f'      </Positioned>')

# Navigation items
nav_items = ["Overview", "Projects", "Analytics", "Settings"]
ny = 130
for item in nav_items:
    el.append(f'      <Positioned left="40" top="{ny}" width="200" height="24">')
    el.append(f'        <Text color="#64748B" fontSize="16" fontFamily="{FONT}">{item}</Text>')
    el.append(f'      </Positioned>')
    ny += 40

# Main content area - white background
el.append(f'      <Positioned left="260" top="0" width="{W-260}" height="{H}">')
el.append(f'        <Container color="{C_CARD}"/>')
el.append(f'      </Positioned>')

# Header section
el.append(f'      <Positioned left="280" top="40" width="{W-280-240}" height="40">')
el.append(f'        <Text color="#1F293B" fontSize="30" fontStyle="BOLD" fontFamily="{FONT}">{data["title"]}</Text>')
el.append(f'      </Positioned>')
el.append(f'      <Positioned left="280" top="72" width="{W-280-240}" height="24">')
el.append(f'        <Text color="#64748B" fontSize="16" fontFamily="{FONT}">{data["subtitle"]}</Text>')
el.append(f'      </Positioned>')

# Export report button
el.append(f'      <Positioned left="{W-240-40}" top="40" width="140" height="36">')
el.append(f'        <Container color="{C_PRIMARY}" borderRadius="8"/>')
el.append(f'      </Positioned>')
el.append(f'      <Positioned left="{W-240+20:.1f}" top="48:.1f}" width="120" height="24">')
el.append(f'        <Text color="#FFFFFF" fontSize="16" fontStyle="BOLD" fontFamily="{FONT}" textAlign="CENTER">Export report</Text>')
el.append(f'      </Positioned>')

# KPI cards section
kpi_y = 140
kx = 280
kw = 340
kh = 120
gap = 30

kpi_data = [
    ("REVENUE", "¥128,400", "+12.4%", C_SUCCESS),
    ("ORDERS", "426", "+8.1%", C_SUCCESS),
    ("REFUND RATE", "3.2%", "−0.8 pp", C_DANGER)
]

for label, value, change, ccolor in kpi_data:
    el.append(f'      <Positioned left="{kx:.1f}" top="{kpi_y:.1f}" width="{kw:.1f}" height="{kh:.1f}">')
    el.append(f'        <Container color="{C_CARD}" border="1 SOLID #E2E8F0" borderRadius="12"/>')
    el.append(f'      </Positioned>')
    el.append(f'      <Positioned left="{kx+24:.1f}" top="{kpi_y+20:.1f}" width="{kw-48:.1f}" height="22">')
    el.append(f'        <Text color="#64748B" fontSize="16" fontStyle="BOLD" fontFamily="{FONT}">{label}</Text>')
    el.append(f'      </Positioned>')
    el.append(f'      <Positioned left="{kx+24:.1f}" top="{ky+56:.1f}" width="{kw-48:.1f}\" height="36">')
    el.append(f'        <Text color="#1F293B" fontSize="32" fontStyle="BOLD" fontFamily="{FONT}">{value}</Text>')
    el.append(f'      </Positioned>')
    el.append(f'      <Positioned left="{kx+24:.1f}" top="{ky+100:.1f}" width="{kw-48:.1f}\" height="24">')
    el.append(f'        <Text color="{ccolor}" fontSize="16" fontStyle="BOLD" fontFamily="{FONT}">{change}</Text>')
    el.append(f'      </Positioned>')
    kx += kw + gap

# Chart section
chart_x = 280
chart_y = 300
chart_w = 740
chart_h = 280
el.append(f'      <Positioned left="{chart_x}" top="{chart_y}" width="{chart_w}" height="{chart_h}">')
el.append(f'        <Container color="#FFFFFF" border="1 SOLID #E2E8F0" borderRadius="12"/>')
el.append(f'      </Positioned>')
el.append(f'      <Positioned left="{chart_x+24}" top="{chart_y+16}" width="400" height="24">')
el.append(f'        <Text color="#1F293B" fontSize="20" fontStyle="BOLD" fontFamily="{FONT}">{data["chart_title"]}</Text>')
el.append(f'      </Positioned>')
el.append(f'      <Positioned left="{chart_x+chart_w-120}" top="{chart_y+16}" width="120" height="24">')
el.append(f'        <Text color="#64748B" fontSize="16" fontFamily="{FONT}" textAlign="RIGHT">{data["chart_period"]}</Text>')
el.append(f'      </Positioned>')

# Chart bars - simplified: draw one bar per value
chart_x_offset = chart_x + 60
chart_y_start = chart_y + 60
chart_w_inner = chart_w - 120
chart_h_inner = chart_h - 80
max_val = max(data["chart_values"])
bar_width = 40
bar_gap = (chart_w - 120 - bar_width * 6) / 5

for i, (month, val) in enumerate(zip(data["months"], data["chart_values"])):
    bar_height = (val / 120) * (chart_h_inner - 60)
    bx = chart_x_offset + i * (bar_width + bar_gap)
    by = chart_y_start + chart_h_inner - bar_height
    el.append(f'      <Positioned left="{bx:.1f}" top="{by:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}">')
    el.append(f'        <Container color="{C_PRIMARY}" borderRadius="6"/>')
    el.append(f'      </Positioned>')
    # Month label
    el.append(f'      <Positioned left="{bx+bar_width/2-12:.1f}" top="{chart_y_start+chart_h_inner+4:.1f}" width="24" height="16">')
    el.append(f'        <Text color="#64748B" fontSize="14" fontFamily="{FONT}" textAlign="CENTER">{month}</Text>')
    el.append(f'      </Positioned>')

# Activity section
act_x = 280
act_y = chart_y + chart_h + 30
act_w = 740
act_h = 200
el.append(f'      <Positioned left="{act_x}" top="{act_y}" width="{act_w}" height="{act_h}">')
el.append(f'        <Container color="#FFFFFF" border="1 SOLID #E2E8F0" borderRadius="12"/>')
el.append(f'      </Positioned>')
el.append(f'      <Positioned left="{act_x+24}" top="{act_y+24}\" width=\"{act_w-48:.1f}\" height=\"24">')
el.append(f'        <Text color="#1F293B" fontSize="20" fontStyle="BOLD" fontFamily="{FONT}">{data["activity_title"]}</Text>')
el.append(f'      </Positioned>')

activities = data["activity"]
ay_inner = chart_y + chart_h + 54
for act_name, act_time in activities:
    el.append(f'      <Positioned left="{act_x+24:.1f}" top="{ay_inner:.1f}\" width="{act_w-48:.1f}\" height="24">')
    el.append(f'        <Text color="#1F293B" fontSize="16" fontFamily="{FONT}">{act_name}</Text>')
    el.append(f'      </Positioned>')
    el.append(f'      <Positioned left="{act_x+200:.1f}\" top=\"{ay_inner:.1f}" width=\"80\" height=\"24\">')
    el.append(f'        <Text color="#64748B\" fontSize="16" fontFamily="{FONT}\" textAlign=\"RIGHT\">{act_time}</Text>')
    el.append(f'      </Positioned>')
    ay_inner += 36

# Table section
tbl_x = 280
tbl_y = chart_y + chart_h + 30
tbl_w = chart_w
tbl_h = 200

el.append(f'      <Positioned left="{tbl_x}" top=\"{tbl_y}\" width=\"{tbl_w}\" height=\"{tbl_h}\">')
el.append(f'        <Container color=\"#FFFFFF\" border=\"1 SOLID #E2E8F0\" borderRadius=\"12\"/>')
el.append(f'      </Positioned>')
el.append(f'      <Positioned left=\"{tbl_x+24}\" top=\"{tbl_y+24}\" width=\"{tbl_w-48:.1f}\" height=\"24\">')
el.append(f'        <Text color=\"#1F293B\" fontSize=\"20\" fontStyle=\"BOLD\" fontFamily=\"{FONT}\">{data["table_title"]}</Text>')
el.append(f'      </Positioned>')

# Table header row
tbl_hdr_y = tbl_y + 64
tbl_cols = data["table_columns"]
tbl_cols_x = [tbl_x+24, tbl_x+240, tbl_x+600, tbl_x+900]
for cname, cx in zip(tbl_cols, tbl_cols_x):
    el.append(f'      <Positioned left=\"{cx:.1f}\" top=\"{tbl_hdr_y:.1f}\" width=\"200\" height=\"24\">')
    el.append(f'        <Text color=\"#64748B\" fontSize=\"16\" fontStyle=\"BOLD\" fontFamily=\"{FONT}\">{cname}</Text>')
    el.append(f'      </Positioned>')

# Table rows
tbl_row_y = tbl_hdr_y + 34
for row in data["table_rows"]:
    el.append(f'      <Positioned left=\"{tbl_x+24:.1f}\" top=\"{tbl_y+64+row_idx*34:.1f}\" width=\"{tbl_w-48:.1f}\" height=\"34\">')
    el.append(f'        <Container color="#FFFFFF\"/>')
    el.append(f'      </Positioned>')
    el.append(f'      <Positioned left=\"{tbl_cols[0]+24:.1f}\" top=\"{tbl_y+64+row_idx*34+8:.1f}\" width=\"{tbl_cols[1]-tbl_cols[0]-48:.1f}\" height=\"20\">')
    el.append(f'        <Text color="#1F293B" fontSize="16" fontFamily="{FONT}">{row[0]}</Text>')
    el.append(f'      </Positioned>')
    el.append(f'      <Positioned left=\"{tbl_cols[1]+24:.1f}\" top=\"{tbl_y+64+row_idx*34+8:.1f}\" width="{tbl_cols[2]-tbl_cols[1]-48:.1f}" height="20">')
    el.append(f'        <Text color="#1F293B" fontSize="16" fontFamily="{FONT}">{row[1]}</Text>')
    el.append(f'      </Positioned>')
    status_color = "#22C55E" if row[2] == "In progress" else "#DC2626" if row[2] == "Review" else "#D97706"
    el.append(f'      <Positioned left=\"{tbl_cols[2]+24:.1f}\" top=\"{tbl_y+64+row_idx*34+8:.1f}\" width=\"{tbl_cols[3]-tbl_cols[2]-48:.1f}\" height=\"20\">')
    el.append(f'        <Text color="{status_color}" fontSize="16" fontStyle="BOLD" fontFamily="{FONT}">{row[2]}</Text>')
    el.append(f'      </Positioned>')
    el.append(f'      <Positioned left=\"{tbl_cols[3]+24:.1f}\" top=\"{tbl_y+64+row_idx*34+8:.1f}\" width=\"{tbl_w-48-(tbl_cols[3]-tbl_x-24):.1f}\" height="20">')
    el.append(f'        <Text color="#64748B" fontSize="16" fontFamily="{FONT}" textAlign="RIGHT">{row[3]}</Text>')
    el.append(f'      </Positioned>')

# Footer
footer_y = tbl_y + tbl_h + 30
el.append(f'      <Positioned left="{tbl_x}" top="{footer_y:.1f}" width="{tbl_w:.1f}" height="24">')
el.append(f'        <Text color="#64748B" fontSize="16" fontFamily="{FONT}">{data["footer"]}</Text>')
el.append(f'      </Positioned>')

el.append('    </Stack>')
el.append('  </SizedBox>')
el.append('</Snapshot>')

with open("tmp/run-20261016/A15/reconstructed.v1.snapshot", "w", encoding="utf-8") as f:
    f.write("\n".join(el))
print("A15 DSL written successfully")