#!/usr/bin/env python3
"""A02 - 三会场密集会议日程 DSL 生成器"""
import json
from pathlib import Path

# 数据
events = [
    {"id": "S01", "venue": "A", "start": "09:00", "end": "09:40", "title": "开场：结构如何成为画面", "speaker": "林川", "category": "keynote"},
    {"id": "S02", "venue": "B", "start": "09:00", "end": "09:55", "title": "从零阅读DSL文档", "speaker": "周禾", "category": "workshop"},
    {"id": "S03", "venue": "C", "start": "09:15", "end": "10:00", "title": "视觉评测的证据链", "speaker": "顾行", "category": "talk"},
    {"id": "S04", "venue": "A", "start": "10:00", "end": "10:45", "title": "复杂布局与约束排查", "speaker": "许宁", "category": "talk"},
    {"id": "S05", "venue": "B", "start": "10:10", "end": "11:10", "title": "一起搭建数据驾驶舱", "speaker": "周禾", "category": "workshop"},
    {"id": "S06", "venue": "C", "start": "10:15", "end": "10:50", "title": "滤镜与裁剪现场实验", "speaker": "孟澄", "category": "demo"},
    {"id": "S07", "venue": "A", "start": "11:00", "end": "11:50", "title": "圆桌：让模型完成工作", "speaker": "林川 / 顾行", "category": "panel"},
    {"id": "S08", "venue": "C", "start": "11:05", "end": "11:45", "title": "中文字体与混合排版", "speaker": "苏言", "category": "talk"},
    {"id": "S09", "venue": "A", "start": "13:00", "end": "13:50", "title": "自检迭代如何留痕", "speaker": "顾行", "category": "talk"},
    {"id": "S10", "venue": "B", "start": "13:00", "end": "14:15", "title": "重建一张复杂参考图", "speaker": "许宁", "category": "workshop"},
    {"id": "S11", "venue": "C", "start": "13:20", "end": "14:00", "title": "模型评测中的数据陷阱", "speaker": "苏言", "category": "talk"},
    {"id": "S12", "venue": "A", "start": "14:10", "end": "15:00", "title": "从单图到视觉系统", "speaker": "孟澄", "category": "talk"},
    {"id": "S13", "venue": "C", "start": "14:20", "end": "15:10", "title": "开放问题的评分分歧", "speaker": "顾行", "category": "panel"},
    {"id": "S14", "venue": "B", "start": "14:35", "end": "15:30", "title": "真实服务调试与恢复", "speaker": "周禾", "category": "workshop"},
    {"id": "S15", "venue": "A", "start": "15:30", "end": "16:00", "title": "闭幕与作品巡览", "speaker": "林川", "category": "keynote"},
]

venues = {
    "A": {"capacity": 320},
    "B": {"capacity": 80},
    "C": {"capacity": 160}
}

categories = {
    "keynote": "主旨",
    "workshop": "工作坊",
    "talk": "分享",
    "demo": "演示",
    "panel": "圆桌"
}

# 时间计算
def time_to_min(t):
    h, m = map(int, t.split(":"))
    return h * 60 + m

def min_to_time(m):
    return f"{m//60:02d}:{m%60:02d}"

start_time = time_to_min("09:00")
end_time = time_to_min("16:00")
total_min = end_time - start_time  # 420分钟

# 颜色定义
BG = "#0F172A"
CARD_BG = "#1E293B"
CARD_BORDER = "#334155"
TEXT_PRIMARY = "#F1F5F9"
TEXT_SECONDARY = "#94A3B8"
ACCENT_COLORS = {
    "keynote": "#F59E0B",
    "workshop": "#3B82F6",
    "talk": "#10B981",
    "demo": "#8B5CF6",
    "panel": "#EC4899"
}
VENUE_COLORS = {"A": "#3B82F6", "B": "#10B981", "C": "#F59E0B"}

# 生成schedule-audit.json
audit = {
    "events": [],
    "venue_gaps": {},
    "conflicts": [],
    "content_mapping": {
        "wide": "agenda-wide.png - 三会场泳道日程，包含所有15项活动的编号、标题、讲者、起止时间与类别",
        "mobile": "agenda-mobile.png - 手机导览，分时段列表，包含所有15项活动的编号、标题、会场与起止时间"
    }
}

for e in events:
    duration = time_to_min(e["end"]) - time_to_min(e["start"])
    audit["events"].append({
        "id": e["id"],
        "title": e["title"],
        "venue": e["venue"],
        "start": e["start"],
        "end": e["end"],
        "duration_min": duration,
        "category": e["category"]
    })

# 检查各会场空档
for venue in ["A", "B", "C"]:
    venue_events = sorted([e for e in events if e["venue"] == venue], key=lambda x: time_to_min(x["start"]))
    gaps = []
    prev_end = start_time
    for e in venue_events:
        e_start = time_to_min(e["start"])
        if e_start > prev_end:
            gaps.append({"start": min_to_time(prev_end), "end": min_to_time(e_start), "duration_min": e_start - prev_end})
        prev_end = max(prev_end, time_to_min(e["end"]))
    if prev_end < end_time:
        gaps.append({"start": min_to_time(prev_end), "end": min_to_time(end_time), "duration_min": end_time - prev_end})
    audit["venue_gaps"][venue] = gaps

# 检查冲突（同一会场时间重叠）
for venue in ["A", "B", "C"]:
    venue_events = sorted([e for e in events if e["venue"] == venue], key=lambda x: time_to_min(x["start"]))
    for i in range(len(venue_events)):
        for j in range(i+1, len(venue_events)):
            s1, e1 = time_to_min(venue_events[i]["start"]), time_to_min(venue_events[i]["end"])
            s2, e2 = time_to_min(venue_events[j]["start"]), time_to_min(venue_events[j]["end"])
            if s1 < e2 and s2 < e1:
                audit["conflicts"].append({
                    "venue": venue,
                    "event1": venue_events[i]["id"],
                    "event2": venue_events[j]["id"]
                })

output_dir = Path("outputs/20261008-a1b2c3/A02")
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / "schedule-audit.json", "w", encoding="utf-8") as f:
    json.dump(audit, f, ensure_ascii=False, indent=2)

# ==================== 大图 DSL (1920x1200) ====================
# 布局：
# - 标题栏：60px
# - 时间轴标签：30px
# - 三泳道：各280px = 840px
# - 午休标识：包含在泳道中
# - 底部说明：40px

chart_left = 120  # 左侧标签宽度
chart_width = 1760  # 图表区域宽度
px_per_min = chart_width / total_min  # 约4.19px/min

def time_x(t):
    return chart_left + (time_to_min(t) - start_time) * px_per_min

lines = []
lines.append(f'<Snapshot background="{BG}" type="png">')
lines.append(f'  <Container width="1920" height="1200" padding="(20,24)">')
lines.append(f'    <Column crossAxisAlignment="START">')
lines.append(f'')
lines.append(f'      <!-- 标题栏 -->')
lines.append(f'      <Container width="1872" height="50" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(12,16)">')
lines.append(f'        <Row mainAxisAlignment="SPACE_BETWEEN" crossAxisAlignment="CENTER">')
lines.append(f'          <Text color="{TEXT_PRIMARY}" fontSize="20" fontStyle="BOLD">Structure / Vision 2026 · 全日日程</Text>')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="13">2026.11.07 · 云构中心 · A/B/C会场 · Asia/Shanghai</Text>')
lines.append(f'        </Row>')
lines.append(f'      </Container>')
lines.append(f'')
lines.append(f'      <SizedBox height="10"/>')
lines.append(f'')
lines.append(f'      <!-- 时间轴 -->')
lines.append(f'      <Container width="1872" height="28">')
lines.append(f'        <Row crossAxisAlignment="CENTER">')
lines.append(f'          <Container width="{chart_left}" height="28"/>')
lines.append(f'          <Container width="{chart_width}" height="28">')
lines.append(f'            <Row mainAxisAlignment="SPACE_BETWEEN" crossAxisAlignment="CENTER">')

for h in range(9, 17):
    t = f"{h:02d}:00"
    lines.append(f'              <Text color="{TEXT_SECONDARY}" fontSize="12">{t}</Text>')

lines.append(f'            </Row>')
lines.append(f'          </Container>')
lines.append(f'        </Row>')
lines.append(f'      </Container>')
lines.append(f'')
lines.append(f'      <SizedBox height="6"/>')
lines.append(f'')
lines.append(f'      <!-- 三泳道 -->')

# 泳道高度
lane_height = 260
lane_gap = 8

for venue in ["A", "B", "C"]:
    color = VENUE_COLORS[venue]
    capacity = venues[venue]["capacity"]
    lines.append(f'      <Row crossAxisAlignment="CENTER">')
    lines.append(f'        <!-- 会场标签 -->')
    lines.append(f'        <Container width="{chart_left}" height="{lane_height}" color="{CARD_BG}" borderRadius="6" border="1 SOLID {CARD_BORDER}" padding="(8,10)">')
    lines.append(f'          <Column crossAxisAlignment="START" mainAxisAlignment="CENTER">')
    lines.append(f'            <Text color="{color}" fontSize="16" fontStyle="BOLD">会场 {venue}</Text>')
    lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="11">容量 {capacity}人</Text>')
    lines.append(f'          </Column>')
    lines.append(f'        </Container>')
    lines.append(f'        <SizedBox width="8"/>')
    lines.append(f'        <!-- 泳道 -->')
    lines.append(f'        <Container width="{chart_width}" height="{lane_height}" color="{CARD_BG}" borderRadius="6" border="1 SOLID {CARD_BORDER}">')
    lines.append(f'          <Stack>')

    # 午休背景
    lunch_start = time_x("12:00")
    lunch_end = time_x("13:00")
    lunch_width = lunch_end - lunch_start
    lines.append(f'            <!-- 午休 -->')
    lines.append(f'            <Positioned left="{lunch_start}" top="0" width="{lunch_width}" height="{lane_height}">')
    lines.append(f'              <Container width="{lunch_width}" height="{lane_height}" color="#1a1a2e" borderRadius="4">')
    lines.append(f'                <Column crossAxisAlignment="CENTER" mainAxisAlignment="CENTER">')
    lines.append(f'                  <Text color="#4a5568" fontSize="10" textAlign="CENTER">午休</Text>')
    lines.append(f'                </Column>')
    lines.append(f'              </Container>')
    lines.append(f'            </Positioned>')

    # 活动块
    venue_events = [e for e in events if e["venue"] == venue]
    for e in venue_events:
        x = time_x(e["start"])
        w = (time_to_min(e["end"]) - time_to_min(e["start"])) * px_per_min
        color = ACCENT_COLORS[e["category"]]
        cat_name = categories[e["category"]]
        lines.append(f'            <!-- {e["id"]} -->')
        lines.append(f'            <Positioned left="{x}" top="8" width="{w}" height="{lane_height - 16}">')
        lines.append(f'              <Container width="{w}" height="{lane_height - 16}" color="{color}22" borderRadius="4" border="1 SOLID {color}">')
        lines.append(f'                <Column crossAxisAlignment="START" mainAxisAlignment="CENTER" padding="(4,6)">')
        lines.append(f'                  <Text color="{color}" fontSize="10" fontStyle="BOLD">{e["id"]}</Text>')
        lines.append(f'                  <Text color="{TEXT_PRIMARY}" fontSize="11" fontStyle="BOLD">{e["title"][:8]}</Text>')
        lines.append(f'                  <Text color="{TEXT_SECONDARY}" fontSize="9">{e["start"]}-{e["end"]}</Text>')
        lines.append(f'                </Column>')
        lines.append(f'              </Container>')
        lines.append(f'            </Positioned>')

    lines.append(f'          </Stack>')
    lines.append(f'        </Container>')
    lines.append(f'      </Row>')
    lines.append(f'      <SizedBox height="{lane_gap}"/>')

lines.append(f'')
lines.append(f'      <!-- 底部说明 -->')
lines.append(f'      <Container width="1872" height="40" color="{CARD_BG}" borderRadius="6" border="1 SOLID {CARD_BORDER}" padding="(8,12)">')
lines.append(f'        <Row crossAxisAlignment="CENTER">')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="11">读图方法：横轴为时间（09:00-16:00），块的位置与长度按实际起止时间比例绘制。类别：</Text>')

for cat, name in categories.items():
    color = ACCENT_COLORS[cat]
    lines.append(f'          <Container width="8" height="8" color="{color}" borderRadius="2"/>')
    lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="10">{name}</Text>')

lines.append(f'        </Row>')
lines.append(f'      </Container>')
lines.append(f'')
lines.append(f'    </Column>')
lines.append(f'  </Container>')
lines.append(f'</Snapshot>')

dsl_wide = "\n".join(lines)
with open(output_dir / "agenda-wide.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl_wide)

# ==================== 小图 DSL (720x1280) ====================
# 手机导览：分时段列表

lines = []
lines.append(f'<Snapshot background="{BG}" type="png">')
lines.append(f'  <Container width="720" height="1280" padding="(16,20)">')
lines.append(f'    <Column crossAxisAlignment="START">')
lines.append(f'')
lines.append(f'      <!-- 标题 -->')
lines.append(f'      <Container width="680" height="60" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(12,14)">')
lines.append(f'        <Column crossAxisAlignment="START" mainAxisAlignment="CENTER">')
lines.append(f'          <Text color="{TEXT_PRIMARY}" fontSize="18" fontStyle="BOLD">Structure / Vision 2026</Text>')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="12">2026.11.07 · 手机导览 · 讲者详见完整日程</Text>')
lines.append(f'        </Column>')
lines.append(f'      </Container>')
lines.append(f'')
lines.append(f'      <SizedBox height="10"/>')
lines.append(f'')

# 按时间段分组
time_slots = [
    ("上午 09:00-12:00", "09:00", "12:00"),
    ("午休 12:00-13:00", "12:00", "13:00"),
    ("下午 13:00-16:00", "13:00", "16:00"),
]

for slot_name, slot_start, slot_end in time_slots:
    lines.append(f'      <!-- {slot_name} -->')
    lines.append(f'      <Container width="680" height="28" color="{CARD_BG}" borderRadius="6" padding="(6,10)">')
    lines.append(f'        <Text color="{TEXT_PRIMARY}" fontSize="14" fontStyle="BOLD">{slot_name}</Text>')
    lines.append(f'      </Container>')
    lines.append(f'      <SizedBox height="4"/>')

    if slot_name.startswith("午休"):
        lines.append(f'      <Container width="680" height="40" color="#1a1a2e" borderRadius="6" padding="(6,10)">')
        lines.append(f'        <Text color="#4a5568" fontSize="12">午休时间</Text>')
        lines.append(f'      </Container>')
    else:
        slot_events = [e for e in events if time_to_min(e["start"]) >= time_to_min(slot_start) and time_to_min(e["start"]) < time_to_min(slot_end)]
        for e in slot_events:
            color = VENUE_COLORS[e["venue"]]
            cat_color = ACCENT_COLORS[e["category"]]
            lines.append(f'      <Container width="680" height="56" color="{CARD_BG}" borderRadius="6" border="1 SOLID {CARD_BORDER}" padding="(6,10)">')
            lines.append(f'        <Row crossAxisAlignment="CENTER">')
            lines.append(f'          <Container width="4" height="40" color="{cat_color}" borderRadius="2"/>')
            lines.append(f'          <SizedBox width="8"/>')
            lines.append(f'          <Column crossAxisAlignment="START" mainAxisAlignment="CENTER">')
            lines.append(f'            <Row crossAxisAlignment="CENTER">')
            lines.append(f'              <Text color="{cat_color}" fontSize="11" fontStyle="BOLD">{e["id"]}</Text>')
            lines.append(f'              <SizedBox width="6"/>')
            lines.append(f'              <Text color="{TEXT_PRIMARY}" fontSize="12" fontStyle="BOLD">{e["title"]}</Text>')
            lines.append(f'            </Row>')
            lines.append(f'            <SizedBox height="2"/>')
            lines.append(f'            <Row crossAxisAlignment="CENTER">')
            lines.append(f'              <Container width="8" height="8" color="{color}" borderRadius="2"/>')
            lines.append(f'              <SizedBox width="4"/>')
            lines.append(f'              <Text color="{TEXT_SECONDARY}" fontSize="11">会场 {e["venue"]}</Text>')
            lines.append(f'              <SizedBox width="10"/>')
            lines.append(f'              <Text color="{TEXT_SECONDARY}" fontSize="11">{e["start"]}-{e["end"]}</Text>')
            lines.append(f'            </Row>')
            lines.append(f'          </Column>')
            lines.append(f'        </Row>')
            lines.append(f'      </Container>')
            lines.append(f'      <SizedBox height="4"/>')

    lines.append(f'')

lines.append(f'    </Column>')
lines.append(f'  </Container>')
lines.append(f'</Snapshot>')

dsl_mobile = "\n".join(lines)
with open(output_dir / "agenda-mobile.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl_mobile)

print(f"Wide DSL: {len(dsl_wide)} chars")
print(f"Mobile DSL: {len(dsl_mobile)} chars")
print(f"Events: {len(events)}")
print(f"Conflicts: {len(audit['conflicts'])}")
