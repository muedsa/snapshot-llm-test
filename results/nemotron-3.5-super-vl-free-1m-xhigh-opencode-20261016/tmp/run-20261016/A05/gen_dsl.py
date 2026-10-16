import math

# ---------------- Data ----------------
rows = [
    ("08:00", 19.2, 41, 0.2),
    ("08:10", 19.6, 40, 0.4),
    ("08:35", 20.1, 39, 0.7),
    ("09:00", 21.0, 38, 1.1),
    ("09:15", None, 37, 1.3),
    ("09:40", 21.9, None, -0.2),
    ("10:10", 22.3, 35, -0.8),
    ("10:50", 23.1, 34, -0.3),
    ("11:00", 22.8, 35, 0.1),
    ("11:40", None, 36, 0.6),
    ("12:10", 22.0, 37, 0.3),
    ("12:30", 21.7, 38, 0.0),
]

def mins(t):
    h, m = t.split(":")
    return int(h) * 60 + int(m)

base = mins("08:00")
points = []
for t, temp, hum, pres in rows:
    points.append({"time": t, "min": mins(t) - base, "temp": temp, "hum": hum, "pres": pres})

# ---------------- Geometry ----------------
W, H = 1440, 1000
# left plot area
X0, X1 = 110, 990
scale_x = (X1 - X0) / 270.0

def xof(m):
    return X0 + m * scale_x

# panels: (ytop, ybot, vmin, vmax, unit, color)
PANELS = {
    "temp": (100, 270, 18.5, 23.5, "\u00b0C", "#EF4444"),
    "hum":  (300, 470, 33, 42, "%", "#F59E0B"),
    "pres": (500, 670, -1.2, 1.4, "kPa", "#3B82F6"),
}

def yof(panel, v):
    yt, yb, vmin, vmax, unit, color = PANELS[panel]
    return yb - (v - vmin) / (vmax - vmin) * (yb - yt)

for p in points:
    p["x"] = xof(p["min"])
    p["y_temp"] = yof("temp", p["temp"]) if p["temp"] is not None else None
    p["y_hum"] = yof("hum", p["hum"]) if p["hum"] is not None else None
    p["y_pres"] = yof("pres", p["pres"])

yt_pres, yb_pres = PANELS["pres"][0], PANELS["pres"][1]
y_zero = yb_pres - (0 - (-1.2)) / (1.4 - (-1.2)) * (yb_pres - yt_pres)

def segs(panel):
    key = {"temp": "temp", "hum": "hum", "pres": "pres"}[panel]
    out = []
    for a, b in zip(points, points[1:]):
        if a[key] is not None and b[key] is not None:
            out.append((a, b))
    return out

def rot_matrix(dx, dy):
    theta = math.atan2(dy, dx)
    c, s = math.cos(theta), math.sin(theta)
    # 4x4 column-major 2D rotation about origin
    return f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"

# ---------------- Build DSL ----------------
el = []
el.append('<Snapshot background="#FFFFFF" type="png">')
el.append(f'  <SizedBox width="{W}" height="{H}">')
el.append('    <Stack alignment="TOP_LEFT" clipBehavior="NONE">')

# Title
el.append('      <Positioned left="40" top="22">')
el.append('        <Text color="#0F172A" fontSize="26" fontStyle="BOLD" fontFamily="Noto Sans CJK SC,Inter">\u5b9d\u5ba4 \u00b7 08:00\u201312:30</Text>')
el.append('      </Positioned>')
el.append('      <Positioned left="40" top="56">')
el.append('        <Text color="#64748B" fontSize="17" fontFamily="Noto Sans CJK SC,Inter">\u4e09\u56fe\u5171\u752808:00\u201312:30\u771f\u5b9e\u65f6\u95f4\u6bd4\u4f8c\u6a2a\u5f0f\uff0c\u7a7a\u7aef\u4e3a\u7f3a\u6d88\uff0c\u4e0d\u662f0</Text>')
el.append('      </Positioned>')

# ===== LEFT: three panels =====
for panel in ["temp", "hum", "pres"]:
    yt, yb, vmin, vmax, unit, color = PANELS[panel]
    el.append(f'      <Positioned left="100" top="{yt}" width="{X1-X0}" height="{yb-yt}">')
    el.append(f'        <Container border="1 SOLID #E2E8F0"/>')
    el.append(f'      </Positioned>')
    # vertical reference lines across all three panels at each sample x
    for p in points:
        el.append(f'      <Positioned left="{p["x"]:.1f}" top="{yt}" width="1" height="{yb-yt}"><Container color="#F1F5F9"/></Positioned>')

# pressure zero line
el.append(f'      <Positioned left="100" top="{y_zero:.1f}" width="{X1-X0}" height="1"><Container color="#F59E0B"/></Positioned>')
el.append(f'      <Positioned left="100" top="{y_zero-14}" width="52"><Text color="#DC2626" fontSize="15" fontFamily="Inter,Noto Sans CJK SC">\u96f6\u7ebf</Text></Positioned>')

def draw_segments(panel):
    key = {"temp": "temp", "hum": "hum", "pres": "pres"}[panel]
    ykey = "y_" + key
    color = PANELS[panel][5]
    for a, b in segs(panel):
        dx = b["x"] - a["x"]
        dy = b[ykey] - a[ykey]
        length = math.hypot(dx, dy)
        mx, my = (a["x"] + b["x"]) / 2, (a[ykey] + b[ykey]) / 2
        mat = rot_matrix(dx, dy)
        el.append(f'      <Positioned left="{mx-length/2:.1f}" top="{my-1:.1f}" width="{length:.1f}" height="2">')
        el.append(f'        <Transform matrix="{mat}" origin="({length/2:.1f},1)">')
        el.append(f'          <Container width="{length:.1f}" height="2" color="{color}"/>')
        el.append(f'        </Transform>')
        el.append(f'      </Positioned>')

def draw_markers(panel):
    key = {"temp": "temp", "hum": "hum", "pres": "pres"}[panel]
    ykey = "y_" + key
    color = PANELS[panel][5]
    for p in points:
        if p[key] is None:
            continue
        el.append(f'      <Positioned left="{p["x"]-3:.1f}" top="{p[ykey]-3:.1f}" width="6" height="6">')
        el.append(f'        <Container color="{color}" border="1 SOLID #FFFFFF" borderRadius="3"/>')
        el.append(f'      </Positioned>')

for panel in ["temp", "hum", "pres"]:
    draw_segments(panel)
    draw_markers(panel)

# panel titles
el.append('      <Positioned left="40" top="106" width="100"><Text color="#0F172A" fontSize="18" fontStyle="BOLD" fontFamily="Noto Sans CJK SC,Inter">\u6e29\u5ea6 (\u00b0C)</Text></Positioned>')
for v in [19, 20, 21, 22, 23]:
    yy = yof("temp", v)
    el.append(f'      <Positioned left="20" top="{yy-9}" width="70"><Text textAlign="END" color="#64748B" fontSize="17" fontFamily="Noto Sans CJK SC,Inter">{v:.0f}</Text></Positioned>')

el.append('      <Positioned left="40" top="306" width="100"><Text color="#0F172A" fontSize="18" fontStyle="BOLD" fontFamily="Noto Sans CJK SC,Inter">\u6e7f\u5ea6 (%)</Text></Positioned>')
for v in [35, 38, 41]:
    yy = yof("hum", v)
    el.append(f'      <Positioned left="20" top="{yy-9}" width="70"><Text textAlign="END" color="#64748B" fontSize="17" fontFamily="Noto Sans CJK SC,Inter">{v:.0f}</Text></Positioned>')

el.append('      <Positioned left="40" top="506" width="120"><Text color="#0F172A" fontSize="18" fontStyle="BOLD" fontFamily="Noto Sans CJK SC,Inter">\u538b\u5dee (kPa)</Text></Positioned>')
for v in [-0.8, -0.4, 0, 0.4, 0.8, 1.2]:
    yy = yof("pres", v)
    el.append(f'      <Positioned left="20" top="{yy-9}" width="70"><Text textAlign="END" color="#64748B" fontSize="17" fontFamily="Noto Sans CJK SC,Inter">{v:+.1f}</Text></Positioned>')

# shared time axis under left panels
el.append(f'      <Positioned left="100" top="684" width="{X1-X0}" height="1"><Container color="#E2E8F0"/></Positioned>')
for p in points:
    if p["min"] % 30 == 0 or p["time"] in ("08:00", "12:30"):
        el.append(f'      <Positioned left="{p["x"]-22}" top="690" width="44"><Text textAlign="CENTER" color="#374151" fontSize="18" fontFamily="Noto Sans CJK SC,Inter">{p["time"]}</Text></Positioned>')

# legend (under time axis)
el.append('      <Positioned left="100" top="720">')
el.append('        <Row mainAxisAlignment="START" crossAxisAlignment="CENTER">')
el.append('          <Container width="12" height="3" color="#EF4444"/>')
el.append('          <Container width="6"/>')
el.append('          <Text color="#374151" fontSize="16" fontFamily="Noto Sans CJK SC,Inter">\u6e29\u5ea6\u7ebf</Text>')
el.append('          <Container width="22"/>')
el.append('          <Container width="12" height="3" color="#F59E0B"/>')
el.append('          <Container width="6"/>')
el.append('          <Text color="#374151" fontSize="16" fontFamily="Noto Sans CJK SC,Inter">\u6e7f\u5ea6\u7ebf</Text>')
el.append('          <Container width="22"/>')
el.append('          <Container width="12" height="3" color="#3B82F6"/>')
el.append('          <Container width="6"/>')
el.append('          <Text color="#374151" fontSize="16" fontFamily="Noto Sans CJK SC,Inter">\u538b\u5dee\u7ebf</Text>')
el.append('        </Row>')
el.append('      </Positioned>')

# ===== RIGHT: stats + table =====
RX = 1030
# stats boxes vertically
stats = [
    ("\u6e29\u5ea6 (\u00b0C)", "10", "19.2\u201323.1", "#EF4444"),
    ("\u6e7f\u5ea6 (%)", "11", "34\u201341", "#F59E0B"),
    ("\u538b\u5dee (kPa)", "12", "\u22120.8\u20131.3", "#3B82F6"),
]
sy = 100
for name, n, rng, color in stats:
    el.append(f'      <Positioned left="{RX}" top="{sy}" width="370" height="56">')
    el.append(f'        <Container color="#F8FAFC" border="1 SOLID #E2E8F0" borderRadius="8" padding="(12,10)">')
    el.append(f'          <Row crossAxisAlignment="CENTER">')
    el.append(f'            <Container width="4"><Container color="{color}"/></Container>')
    el.append(f'            <Container width="10"/>')
    el.append(f'            <Column crossAxisAlignment="START">')
    el.append(f'              <Text color="#374151" fontSize="15" fontFamily="Noto Sans CJK SC,Inter">{name}</Text>')
    el.append(f'              <Text color="#0F172A" fontSize="17" fontStyle="BOLD" fontFamily="Inter,Noto Sans CJK SC">\u6709\u52b9 {n} \u00b7 \u6700\u5c0f/\u6700\u5927 {rng}</Text>')
    el.append(f'            </Column>')
    el.append(f'          </Row>')
    el.append(f'        </Container>')
    el.append(f'      </Positioned>')
    sy += 70

# table
el.append(f'      <Positioned left="{RX}" top="330" width="370">')
el.append(f'        <Container border="1 SOLID #E2E8F0" borderRadius="8">')
el.append(f'          <Column>')
el.append(f'            <Container height="30" borderBottom="1 SOLID #E2E8F0">')
el.append(f'              <Row crossAxisAlignment="CENTER">')
el.append(f'                <SizedBox width="100"><Text textAlign="CENTER" color="#374151" fontSize="18" fontStyle="BOLD" fontFamily="Noto Sans CJK SC,Inter">\u65f6\u95f4</Text></SizedBox>')
el.append(f'                <SizedBox width="90"><Text textAlign="CENTER" color="#374151" fontSize="18" fontStyle="BOLD" fontFamily="Noto Sans CJK SC,Inter">\u6e29\u5ea6</Text></SizedBox>')
el.append(f'                <SizedBox width="90"><Text textAlign="CENTER" color="#374151" fontSize="18" fontStyle="BOLD" fontFamily="Noto Sans CJK SC,Inter">\u6e7f\u5ea6</Text></SizedBox>')
el.append(f'                <SizedBox width="90"><Text textAlign="CENTER" color="#374151" fontSize="18" fontStyle="BOLD" fontFamily="Noto Sans CJK SC,Inter">\u538b\u5dee</Text></SizedBox>')
el.append(f'              </Row>')
el.append(f'            </Container>')
for p in points:
    t, temp, hum, pres = p["time"], p["temp"], p["hum"], p["pres"]
    ts = f"{temp:.1f}" if temp is not None else "\u2014"
    hs = f"{hum:.0f}" if hum is not None else "\u2014"
    ps = f"{pres:+.1f}" if pres is not None else "\u2014"
    pres_neg = pres is not None and pres < 0
    pc = "#DC2626" if pres_neg else "#0F172A"
    el.append(f'            <Container height="22" borderBottom="1 SOLID #F1F5F9">')
    el.append(f'              <Row crossAxisAlignment="CENTER">')
    el.append(f'                <SizedBox width="100"><Text textAlign="CENTER" color="#374151" fontSize="17" fontFamily="Noto Sans CJK SC,Inter">{t}</Text></SizedBox>')
    el.append(f'                <SizedBox width="90"><Text textAlign="CENTER" color="{pc}" fontSize="17" fontFamily="Inter,Noto Sans CJK SC">{ts}</Text></SizedBox>')
    el.append(f'                <SizedBox width="90"><Text textAlign="CENTER" color="{pc}" fontSize="17" fontFamily="Inter,Noto Sans CJK SC">{hs}</Text></SizedBox>')
    el.append(f'                <SizedBox width="90"><Text textAlign="CENTER" color="{pc}" fontSize="17" fontFamily="Inter,Noto Sans CJK SC">{ps}</Text></SizedBox>')
    el.append(f'              </Row>')
    el.append(f'            </Container>')
el.append(f'          </Column>')
el.append(f'        </Container>')
el.append(f'      </Positioned>')

# annotation about negative pressure
el.append(f'      <Positioned left="{RX}" top="620" width="370">')
el.append(f'        <Text color="#DC2626" fontSize="16" fontStyle="BOLD" fontFamily="Noto Sans CJK SC,Inter">\u538b\u5dee\u70b9\u6570\u4e3a\u8d1f\u503c\u7684\u5b9e\u9645\u6570\u4e3a\uff1a09:40 (\u22120.2)\uff0c10:10 (\u22120.8)\uff0c10:50 (\u22120.3) kPa\uff0c\u53ea\u8868\u793a\u5b9e\u9645\u6362\u51fa\u7684\u91cf\u6570\u70b9\uff0c\u4e0d\u8868\u793a09:40\u201310:50\u65f6\u95f4\u6bb5\u7b49\u6b64\u65f6\u5219\u70b9\u6570\u4e3a\u8d1f</Text>')
el.append(f'      </Positioned>')

# note
el.append('      <Positioned left="40" top="940" width="1360">')
el.append('        <Text color="#64748B" fontSize="16" fontFamily="Noto Sans CJK SC,Inter">\u7b80\u65e5\u671f\u00b7\u6e29\u5ea6/\u6e7f\u5ea6\u5728\u7f3a\u6d88\u70b9\u524d\u540e\u7ebf\u6210\u65ad\uff0c\u4e0d\u4f7f\u751f\u522b\u8865\u503c\uff0c\u538b\u5dee\u53ef\u6b63\u53ef\u8d1f\u3001\u96f6\u7ebf\u6e05\u7ec7\u89c4\u5b9a\u3002\u6570\u636e\u6765\u6e90: inputs/readings.csv</Text>')
el.append('      </Positioned>')

el.append('    </Stack>')
el.append('  </SizedBox>')
el.append('</Snapshot>')

dsl = "\n".join(el)
open("tmp/run-20261016/A05/sensor-report.v1.snapshot", "w", encoding="utf-8").write(dsl)
print("DSL written, chars:", len(dsl))
