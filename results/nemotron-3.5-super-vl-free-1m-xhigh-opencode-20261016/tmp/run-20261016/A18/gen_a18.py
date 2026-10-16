import json

W, H = 1600, 1000
C_DARK = "#0F172A"      # Deep background
C_BG = "#F8FAFC"         # Light background
C_CARD = "#FFFFFF"       # Card white
C_TEXT = "#0F172A"       # Dark text
C_MUTED = "#64748B"      # Muted text
C_PRIMARY = "#2563EB"    # Primary blue
C_SUCCESS = "#22C55E"    # Green
C_DANGER = "#DC2626"     # Red/danger

def container(x, y, w, h, color="#FFFFFF", border_radius=8, border=None):
    parts = [f'<Container color="{color}" borderRadius="{border_radius}"']
    if border:
        el = f'      <Positioned left="{x:.1f}" top="{y:.1f}" width="{w:.1f}" height="{h:.1f}">'
        el.append(f'        <Container color="{color}" borderRadius="{border_radius}"/>')
        el.append(f'      </Positioned>')
        return el
    else:
        return f'      <Positioned left="{x:.1f}" top="{y:.1f}" width="{w:.1f}" height="{h:.1f}"><Container color="{color}" borderRadius="{border_radius}"/></Positioned>'

def text(x, y, w, h, text, size=16, color=C_TEXT, bold=False, align="START", font=FONT):
    b = ' fontStyle="BOLD"' if bold else ""
    al = f' textAlign="{align}"' if align != "START" else ""
    return f'      <Positioned left="{x:.1f}" top="{y:.1f}" width="{w:.1f}" height="{h:.1f}">\n        <Text color="{color}" fontSize="{size}" fontFamily="{FONT}"{b}{al}>{text}</Text>\n      </Positioned>'

FONT = "Noto Sans CJK SC,Inter"
FONT_I = "Inter"

el = []
el.append('<Snapshot background="#FFFFFF" type="png">')
el.append(f'  <SizedBox width="{W}" height="{H}">')
el.append('    <Stack alignment="TOP_LEFT" clipBehavior="NONE">')

# Deep background
el.append('      <Positioned left="0" top="0" width="1600" height="1000">')
el.append('        <Container color="#0F172A"/>')
el.append(f'      </Positioned>')

# Left sidebar
el.append(f'      <Positioned left="0" top="0" width="240" height="1000">')
el.append(f'        <Container color="#0F172A"/>')
el.append(f'      </Positioned>')

# Logo
el.append(f'      <Positioned left="40" top="40" width="32" height="32">')
el.append(f'        <Container color="#22C55E" borderRadius="8"/>')
el.append(f'      </Positioned>')
el.append(f'      <Positioned left="80" top="44" width="120" height="24">')
el.append(f'        <Text color="#FFFFFF" fontSize="20" fontStyle="BOLD" fontFamily="{FONT}">Northstar</Text>')
el.append(f'      </Positioned>')

# Nav items
nav_items = ["Overview", "Products", "Analytics", "Settings"]
ny = 140
for i, item in enumerate(nav_items):
    active = i == 0
    color = "#FFFFFF" if i == 0 else "#64748B"
    size = 18 if i == 0 else 16
    bold = "BOLD" if i == 0 else ""
    el.append(f'      <Positioned left="40" top="{ny}" width="200" height="28">')
    el.append(f'        <Text color="{color}" fontSize="{size}" fontStyle="{bold}" fontFamily="{FONT}">{item}</Text>')
    el.append(f'      </Positioned>')
    ny += 48

# Right content area
# Header
el.append(f'      <Positioned left="280" top="40" width="1320" height="40">')
el.append(f'        <Text color="#1E293B" fontSize="28" fontStyle="BOLD" fontFamily="{FONT}">Workspace Overview</Text>')
el.append(f'      </Positioned>')
el.append(f'      <Positioned left="280" top="76" width="400" height="24">')
el.append(f'        <Text color="#64748B" fontSize="18" fontFamily="{FONT}">Saturday, 07 November 2026</Text>')
el.append(f'      </Positioned>')

# Export report button
el.append(f'      <Positioned left="1080" top="44" width="280" height="40">')
el.append(f'        <Container color="#2563EB" borderRadius="8"/>')
el.append(f'      </Positioned>')
el.append(f'      <Positioned left="1080" top="44" width="140" height="40">')
el.append(f'        <Text color="#FFFFFF" fontSize="16" fontStyle="BOLD" fontFamily="{FONT}" textAlign="CENTER">Export report</Text>')
el.append(f'      </Positioned>')

# KPI Cards
kpis = [
    ("REVENUE", "¥128,400", "+12.4%", C_SUCCESS),
    ("ORDERS", "426", "+8.1%", C_SUCCESS),
    ("REFUND RATE", "3.2%", "−0.8 pp", C_DANGER),
]

ky = 140
kx = 280
kw = 340
kh = 140
gap = 40
for label, val, change, ccolor in cards:
    el.append(f'      <Positioned left="{kx:.1f}" top="{ky:.1f}" width="{kw:.1f}" height="{kh:.1f}">')
    el.append(f'        <Container color="#FFFFFF" borderRadius="10"/>')
    el.append(f'      </Positioned>')
    el.append(f'      <Positioned left="{kx+24:.1f}" top="{ky+20:.1f}" width="{kw-48:.1f}" height="24">')
    el.append(f'        <Text color="#64748B" fontSize="16" fontFamily="{FONT}">{label}</Text>')
    el.append(f'      </Positioned>')
    el.append(f'      <Positioned left="{kx+24:.1f}" top="{ky+52:.1f}" width="{kw-48:.1f}" height="40">')
    el.append(f'        <Text color="#1E293B" fontSize="32" fontStyle="BOLD" fontFamily="{FONT}">{val}</Text>')
    el.append(f'      </Positioned>')
    el.append(f'      <Positioned left="{kx+24:.1f}" top="{ky+96:.1f}" width="{kw-48:.1f}" height="24">')
    el.append(f'        <Text color="{ccolor}" fontSize="16" fontStyle="BOLD" fontFamily="{FONT}">{change}</Text>')
    el.append(f'      </Positioned>')
    kx += kw + gap

# Chart section
ch_x = 280
ch_y = 330
ch_w = 740
ch_h = 320
el.append(f'      <Positioned left="{ch_x}" top="{ch_y}" width="{ch_w}" height="{ch_h}">')
el.append(f'        <Container color="#FFFFFF" border="1 SOLID #E2E8F0" borderRadius="12"/>')
el.append(f'      </Positioned>')
el.append(f'      <Positioned left="{ch_x+24}" top="{ch_y+16}" width="400" height="28">')
el.append(f'        <Text color="#1F293B" fontSize="20" fontStyle="BOLD" fontFamily="{FONT}">Net revenue</Text>')
el.append(f'      </Positioned>')
el.append(f'      <Positioned left="ch_x+kw-140" top="{ch_y+16}" width="120" height="24">')
el.append(f'        <Text color="#64748B" fontSize="16" fontFamily="{FONT}" textAlign="RIGHT">Apr – Sep</Text>')
el.append(f'      </Positioned>')

# Activity section right side
ax = 1060
ay = 330
aw = 360
ah = 320
el.append(f'      <Positioned left="{ax}" top="{ay}" width="{aw}" height="{ah}">')
el.append(f'        <Container color="#FFFFFF" border="1 SOLID #E2E8F0" borderRadius="12"/>')
el.append(f'      </Positioned>')
el.append(f'      <Positioned left="{ax+24}" top="{ay+24}" width="280" height="24">')
el.append(f'        <Text color="#1F293B" fontSize="20" fontStyle="BOLD" fontFamily="{FONT}">Team activity</Text>')
el.append(f'      </Positioned>')

activities = [
    ("Design review", "08:40"),
    ("Dataset updated", "09:15"),
    ("Render complete", "10:05"),
]
ay += 48
for title, time in activities:
    el.append(f'      <Positioned left="{ax+24}" top="{ay:.1f}" width="320" height="44">')
    el.append(f'        <Container color="#2563EB" borderRadius="10"/>')
    el.append(f'      </Positioned>')
    el.append(f'      <Positioned left="{cx+36:.1f}" top="{cy:.1f}" width="200" height="20">')
    el.append(f'        <Text color="#1F293B" fontSize="16" fontFamily="{FONT}">{title}</Text>')
    el.append(f'      </Positioned>')
    el.append(f'      <Positioned left="{ax+280:.1f}" top="{cy:.1f}" width="60" height="20">')
    el.append(f'        <Text color="#64748B" fontSize="16" fontFamily="{FONT}" textAlign="RIGHT">{time}</Text>')
    el.append(f'      </Positioned>')
    cy += 44

# Table section
tbl_x = 280
tbl_y = 680
tbl_w = 1040
tbl_h = 180
el.append(f'      <Positioned left="{tbl_x}" top="{tbl_y}" width="{tbl_w}" height="{tbl_h}">')
el.append(f'        <Container color="#FFFFFF" border="1 SOLID #E2E8F0" borderRadius="12"/>')
el.append(f'      </Positioned>')
el.append(f'      <Positioned left="{tbl_x+24}" top="{tbl_y+24}" width="400" height="24">')
el.append(f'        <Text color="#14233C" fontSize="20" fontStyle="BOLD" fontFamily="{FONT}">Recent projects</Text>')
el.append(f'      </Positioned>')

# Table header
tbl_hdr_y = tbl_y + 64
tbl_cols = ["PROJECT", "OWNER", "STATUS", "DUE"]
tbl_cols_x = [tbl_x+24, tbl_x+300, tbl_x+600, tbl_x+900]
for cname, cx in zip(tbl_cols, tbl_cols_x):
    el.append(f'      <Positioned left="{cx:.1f}" top="{tbl_hdr_y:.1f}" width="200" height="24">')
    el.append(f'        <Text color="#64748B" fontSize="16" fontStyle="BOLD" fontFamily="{FONT}">{cname}</Text>')
    el.append(f'      </Positioned>')

# Table rows
tbl_rows = [
    ("Atlas / Visual system", "Lin Chuan", "In progress", "Nov 09"),
    ("Pulse / Dashboard", "Zhou He", "Review", "Nov 11"),
    ("Orbit / Launch", "Su Yan", "Done", "Nov 12"),
]
ty = tbl_hdr_y + 40
for row in tbl_rows:
    el.append(f'      <Positioned left="{tbl_x+24:.1f}" top="{ty:.1f}" width="940" height="28">')
    el.append(f'        <Text color="#1F293B" fontSize="16" fontFamily="{FONT}">{row[0]}</Text>')
    el.append(f'      </Positioned>')
    el.append(f'      <Positioned left="{tbl_cols[1]+24:.1f}" top="{ty:.1f}" width="200" height="24">')
    el.append(f'        <Text color="#1F293B" fontSize="16" fontFamily="{FONT}">{row[1]}</Text>')
    el.append(f'      </Positioned>')
    el.append(f'      <Positioned left="{tbl_cols[2]+24:.1f}" top="{ty:.1f}" width="140" height="24">')
    status_color = "#22C55E" if row[2] == "Done" else "#DC2626" if row[2] == "Review" else "#D97706"
    el.append(f'        <Text color="{status_color}" fontSize="16" fontStyle="BOLD" fontFamily="{FONT}">{row[2]}</Text>')
    el.append(f'      </Positioned>')
    el.append(f'      <Positioned left="{tbl_cols[3]+24:.1f}" top="{ty:.1f}" width="80" height="24">')
    el.append(f'        <Text color="#64748B" fontSize="16" fontFamily="{FONT}" textAlign="RIGHT">{row[3]}</Text>')
    el.append(f'      </Positioned>')
    ty += 34

# Footer
el.append(f'      <Positioned left="280" top="{tbl_y+tbl_h+20}" width="{W-2*MARGIN-280}" height="24">')
el.append(f'        <Text color="#64748B" fontSize="16" fontFamily="{FONT}" softWrap="true">All data is fictional · Snapshot benchmark</Text>')
el.append(f'      </Positioned>')

el.append('    </Stack>')
el.append('  </SizedBox>')
el.append('</Snapshot>')

with open("tmp/run-20261016/A15/reconstructed.v1.snapshot", "w", encoding="utf-8") as f:
    f.write("\n".join(el))
print("A18 DSL written, chars:", len("\n".join(el)))