import csv, json
from pathlib import Path

# Read agenda
agenda = []
with open('tasks/A02-conference-schedule/inputs/agenda.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        agenda.append(row)

# Read venues
with open('tasks/A02-conference-schedule/inputs/venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# Time range: 09:00 - 16:00 (7 hours = 420 minutes)
START_MIN = 9 * 60  # 540
END_MIN = 16 * 60   # 960
TOTAL_MIN = END_MIN - START_MIN  # 420

def time_to_min(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

def min_to_time(m):
    return f"{m//60:02d}:{m%60:02d}"

# Layout constants for wide image
W, H = 1920, 1200
MARGIN = 24
HEADER_H = 80
TIMELINE_H = 40
LANE_H = 280
LANE_GAP = 16
FOOTER_H = 60

# Colors
BG = "#F8FAFC"
CARD_BG = "#FFFFFF"
CARD_BORDER = "#E2E8F0"
TEXT_DARK = "#1E293B"
TEXT_MED = "#64748B"
TEXT_LIGHT = "#94A3B8"
GRID = "#E2E8F0"
LANE_BG = "#F1F5F9"

# Category colors
CAT_COLORS = {
    "keynote": "#3B82F6",
    "workshop": "#10B981",
    "talk": "#F59E0B",
    "demo": "#8B5CF6",
    "panel": "#EF4444",
}

# Venue colors
VENUE_COLORS = {"A": "#3B82F6", "B": "#10B981", "C": "#F59E0B"}

# Calculate positions
def calc_x(start_time):
    """Calculate x position for a start time"""
    t = time_to_min(start_time)
    return MARGIN + 120 + (t - START_MIN) / TOTAL_MIN * (W - 2 * MARGIN - 120)

def calc_width(start_time, end_time):
    """Calculate width for a time range"""
    s = time_to_min(start_time)
    e = time_to_min(end_time)
    return (e - s) / TOTAL_MIN * (W - 2 * MARGIN - 120)

# Build wide DSL
dsl_parts = []
dsl_parts.append(f'<Snapshot type="png" background="{BG}">')
dsl_parts.append(f'  <Column mainAxisSize="MAX" height="{H}" width="{W}">')

# Header
dsl_parts.append(f'    <Container height="{HEADER_H}" padding="(0,{MARGIN})">')
dsl_parts.append(f'      <Column crossAxisAlignment="START">')
dsl_parts.append(f'        <Text text="Structure / Vision 2026" color="{TEXT_DARK}" fontSize="28" fontStyle="BOLD"/>')
dsl_parts.append(f'        <Text text="2026.11.07 · 云构中心 · A/B/C会场 · Asia/Shanghai" color="{TEXT_MED}" fontSize="16"/>')
dsl_parts.append(f'      </Column>')
dsl_parts.append(f'    </Container>')

# Timeline header
dsl_parts.append(f'    <Container height="{TIMELINE_H}" padding="(0,{MARGIN})">')
dsl_parts.append(f'      <Row mainAxisAlignment="SPACE_BETWEEN">')
for h in range(9, 17):
    dsl_parts.append(f'        <Text text="{h:02d}:00" color="{TEXT_MED}" fontSize="14"/>')
dsl_parts.append(f'      </Row>')
dsl_parts.append(f'    </Container>')

# Lanes
for venue in ["A", "B", "C"]:
    dsl_parts.append(f'    <Container height="{LANE_H}" color="{LANE_BG}" border="1 SOLID {CARD_BORDER}" borderRadius="8" padding="(8,12)">')
    dsl_parts.append(f'      <Column crossAxisAlignment="START">')
    dsl_parts.append(f'        <Text text="会场{venue} (容量{venues[venue]["capacity"]}人)" color="{VENUE_COLORS[venue]}" fontSize="16" fontStyle="BOLD"/>')
    dsl_parts.append(f'        <SizedBox height="8"/>')
    
    # Sessions in this venue
    venue_sessions = [s for s in agenda if s['venue'] == venue]
    for s in venue_sessions:
        x = calc_x(s['start']) - MARGIN - 120
        w = calc_width(s['start'], s['end'])
        color = CAT_COLORS.get(s['category'], "#64748B")
        dsl_parts.append(f'        <Container width="{w:.0f}" height="40" color="{color}" borderRadius="6" padding="(8,8)">')
        dsl_parts.append(f'          <Column crossAxisAlignment="START">')
        dsl_parts.append(f'            <Text text="{s["id"]} {s["title"][:12]}" color="#FFFFFF" fontSize="12" fontStyle="BOLD"/>')
        dsl_parts.append(f'            <Text text="{s["start"]}-{s["end"]} {s["speaker"][:8]}" color="#FFFFFF" fontSize="10"/>')
        dsl_parts.append(f'          </Column>')
        dsl_parts.append(f'        </Container>')
        dsl_parts.append(f'        <SizedBox height="4"/>')
    
    dsl_parts.append(f'      </Column>')
    dsl_parts.append(f'    </Container>')
    dsl_parts.append(f'    <SizedBox height="{LANE_GAP}"/>')

# Footer
dsl_parts.append(f'    <Container height="{FOOTER_H}" padding="(0,{MARGIN})">')
dsl_parts.append(f'      <Text text="读图方法：横向为时间轴(09:00-16:00)，纵向为三个会场泳道。块的位置与长度按实际起止时间比例绘制。午休12:00-13:00跨三泳道。" color="{TEXT_MED}" fontSize="14"/>')
dsl_parts.append(f'    </Container>')

dsl_parts.append(f'  </Column>')
dsl_parts.append(f'</Snapshot>')

dsl = '\n'.join(dsl_parts)
with open('tmp/20261011-suite/A02/agenda-wide.snapshot', 'w', encoding='utf-8') as f:
    f.write(dsl)
print(f'Generated wide DSL: {len(dsl)} chars')

# Build mobile DSL
dsl_parts = []
dsl_parts.append(f'<Snapshot type="png" background="{BG}">')
dsl_parts.append(f'  <Column mainAxisSize="MAX" height="1280" width="720">')

# Header
dsl_parts.append(f'    <Container height="80" padding="(16,16)">')
dsl_parts.append(f'      <Column crossAxisAlignment="START">')
dsl_parts.append(f'        <Text text="Structure / Vision 2026" color="{TEXT_DARK}" fontSize="24" fontStyle="BOLD"/>')
dsl_parts.append(f'        <Text text="2026.11.07 · 手机导览" color="{TEXT_MED}" fontSize="14"/>')
dsl_parts.append(f'        <Text text="讲者详见完整日程" color="{TEXT_LIGHT}" fontSize="12"/>')
dsl_parts.append(f'      </Column>')
dsl_parts.append(f'    </Container>')

# Time slots
dsl_parts.append(f'    <Container height="40" padding="(0,16)">')
dsl_parts.append(f'      <Text text="上午 09:00-12:00" color="{TEXT_DARK}" fontSize="16" fontStyle="BOLD"/>')
dsl_parts.append(f'    </Container>')

morning = [s for s in agenda if time_to_min(s['start']) < 12*60]
for s in morning:
    color = CAT_COLORS.get(s['category'], "#64748B")
    dsl_parts.append(f'    <Container height="60" color="{CARD_BG}" border="1 SOLID {CARD_BORDER}" borderRadius="8" padding="(8,12)">')
    dsl_parts.append(f'      <Column crossAxisAlignment="START">')
    dsl_parts.append(f'        <Text text="{s["id"]} {s["title"][:16]}" color="{TEXT_DARK}" fontSize="14" fontStyle="BOLD"/>')
    dsl_parts.append(f'        <Text text="{s["start"]}-{s["end"]} · 会场{s["venue"]}" color="{color}" fontSize="12"/>')
    dsl_parts.append(f'      </Column>')
    dsl_parts.append(f'    </Container>')
    dsl_parts.append(f'    <SizedBox height="8"/>')

# Lunch
dsl_parts.append(f'    <Container height="40" color="#FEF3C7" borderRadius="8" padding="(8,12)">')
dsl_parts.append(f'      <Text text="午休 12:00-13:00" color="#92400E" fontSize="14" fontStyle="BOLD"/>')
dsl_parts.append(f'    </Container>')
dsl_parts.append(f'    <SizedBox height="8"/>')

# Afternoon
dsl_parts.append(f'    <Container height="40" padding="(0,16)">')
dsl_parts.append(f'      <Text text="下午 13:00-16:00" color="{TEXT_DARK}" fontSize="16" fontStyle="BOLD"/>')
dsl_parts.append(f'    </Container>')

afternoon = [s for s in agenda if time_to_min(s['start']) >= 13*60]
for s in afternoon:
    color = CAT_COLORS.get(s['category'], "#64748B")
    dsl_parts.append(f'    <Container height="60" color="{CARD_BG}" border="1 SOLID {CARD_BORDER}" borderRadius="8" padding="(8,12)">')
    dsl_parts.append(f'      <Column crossAxisAlignment="START">')
    dsl_parts.append(f'        <Text text="{s["id"]} {s["title"][:16]}" color="{TEXT_DARK}" fontSize="14" fontStyle="BOLD"/>')
    dsl_parts.append(f'        <Text text="{s["start"]}-{s["end"]} · 会场{s["venue"]}" color="{color}" fontSize="12"/>')
    dsl_parts.append(f'      </Column>')
dsl_parts.append(f'    </Container>')
    dsl_parts.append(f'    <SizedBox height="8"/>')

dsl_parts.append(f'  </Column>')
dsl_parts.append(f'</Snapshot>')

dsl = '\n'.join(dsl_parts)
with open('tmp/20261011-suite/A02/agenda-mobile.snapshot', 'w', encoding='utf-8') as f:
    f.write(dsl)
print(f'Generated mobile DSL: {len(dsl)} chars')

# Generate audit JSON
audit = {
    "schema_version": 1,
    "task_id": "A02",
    "path_base": "output_dir",
    "sessions": [],
    "venue_gaps": {},
    "conflicts": [],
    "content_mapping": {
        "wide": "agenda-wide.png",
        "mobile": "agenda-mobile.png"
    }
}

for s in agenda:
    start = time_to_min(s['start'])
    end = time_to_min(s['end'])
    audit["sessions"].append({
        "id": s["id"],
        "title": s["title"],
        "venue": s["venue"],
        "start": s["start"],
        "end": s["end"],
        "duration_min": end - start,
        "category": s["category"]
    })

# Check for conflicts
for i, s1 in enumerate(agenda):
    for j, s2 in enumerate(agenda):
        if i >= j:
            continue
        if s1['venue'] != s2['venue']:
            continue
        s1_start = time_to_min(s1['start'])
        s1_end = time_to_min(s1['end'])
        s2_start = time_to_min(s2['start'])
        s2_end = time_to_min(s2['end'])
        if s1_start < s2_end and s2_start < s1_end:
            audit["conflicts"].append({
                "session1": s1["id"],
                "session2": s2["id"],
                "venue": s1["venue"]
            })

# Venue gaps
for venue in ["A", "B", "C"]:
    venue_sessions = sorted([s for s in agenda if s['venue'] == venue], key=lambda x: time_to_min(x['start']))
    gaps = []
    prev_end = START_MIN
    for s in venue_sessions:
        start = time_to_min(s['start'])
        if start > prev_end:
            gaps.append({"from": min_to_time(prev_end), "to": min_to_time(start)})
        prev_end = max(prev_end, time_to_min(s['end']))
    if prev_end < END_MIN:
        gaps.append({"from": min_to_time(prev_end), "to": min_to_time(END_MIN)})
    audit["venue_gaps"][venue] = gaps

output_dir = Path('outputs/20261011-suite/A02')
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / 'schedule-audit.json', 'w', encoding='utf-8') as f:
    json.dump(audit, f, ensure_ascii=False, indent=2)
print('Saved schedule-audit.json')
