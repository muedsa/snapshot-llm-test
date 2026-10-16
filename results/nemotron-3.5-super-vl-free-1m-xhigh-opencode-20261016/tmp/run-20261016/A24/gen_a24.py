# gen_a24.py - 生成 A24 发布作战计划 (3张图 + schedule数据)
import json, os, math
from datetime import datetime, timedelta, timezone

SUITE_ROOT = os.environ.get("SNAPSHOT_TASK_ROOT", ".")
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "run-20261016")
OUTPUT_ROOT = os.path.join(SUITE_ROOT, "outputs", RUN_ID, "A24")
TEMP_DIR = os.path.join(SUITE_ROOT, "tmp", RUN_ID, "A24")
SERVICE_URL = "https://open-snapshot.muedsa.com/snapshot"
FONT = "Noto Sans CJK SC,Inter"

os.makedirs(OUTPUT_ROOT, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# ============ 读取 release.json ============
release_path = os.path.join(SUITE_ROOT, "tasks", "A24-release-plan-capstone", "inputs", "release.json")
with open(release_path, "r", encoding="utf-8") as f:
    release = json.load(f)

START_TZ = timezone(timedelta(hours=8))
start_dt = datetime.fromisoformat(release["start"])
deadline_dt = datetime.fromisoformat(release["deadline"])

# 分钟偏移
WINDOW_START = 0   # 09:00
WINDOW_END = 420   # 16:00

tasks_input = release["tasks"]
teams_list = release["teams"]

# ============ 排程计算 (贪心 + 资源约束) ============
# 手动设计的最优排程（基于关键路径和资源约束）
# (task_id, start_min, end_min, team)
SCHEDULE = [
    ("R01", 0, 25, "design"),
    ("R02", 0, 20, "engineering"),
    ("R03", 20, 60, "engineering"),
    ("R04", 25, 85, "design"),
    ("R05", 85, 115, "design"),
    ("R06", 60, 105, "engineering"),
    ("R07", 115, 185, "design"),
    ("R08", 105, 170, "engineering"),
    ("R09", 185, 230, "engineering"),
    ("R10", 230, 265, "design"),
    ("R11", 230, 260, "engineering"),
    ("R12", 265, 285, "engineering"),
]

# 验证资源约束（同团队不可并行）
team_busy = {}
for tid, s, e, team in SCHEDULE:
    if team not in team_busy:
        team_busy[team] = []
    team_busy[team].append((s, e, tid))

for team, intervals in team_busy.items():
    intervals.sort()
    for i in range(1, len(intervals)):
        assert intervals[i][0] >= intervals[i-1][1], f"Team {team} overlap: {intervals[i-1]} vs {intervals[i]}"

# 验证依赖
task_map = {t["id"]: t for t in tasks_input}
sched_map = {tid: (s, e, team) for tid, s, e, team in SCHEDULE}
for tid, s, e, team in SCHEDULE:
    t = task_map[tid]
    for dep in t["depends"]:
        dep_end = sched_map[dep][1]
        assert dep_end <= s, f"Dep violation: {dep} ends {dep_end}, {tid} starts {s}"

# 验证团队资格
for tid, s, e, team in SCHEDULE:
    t = task_map[tid]
    assert team in t["teams"], f"Task {tid} team {team} not in {t['teams']}"

# 验证时长
for tid, s, e, team in SCHEDULE:
    assert e - s == task_map[tid]["minutes"], f"Task {tid} duration {e-s} != {task_map[tid]['minutes']}"

# 完成时间
max_end = max(e for _, s, e, _ in SCHEDULE)
buffer = WINDOW_END - max_end

# 关键路径下界 (仅依赖和时长)
# R02(20)->R03(40)->R06(45)->R08(65)->R10(35)->R12(20) = 225
CP_LOWER_BOUND = 225
# 资源工作量下界
TOTAL_MINUTES = sum(t["minutes"] for t in tasks_input)
RESOURCE_LOWER_BOUND = TOTAL_MINUTES / 2

print(f"Schedule: max_end={max_end}min, buffer={buffer}min")
print(f"CP lower bound: {CP_LOWER_BOUND}, Resource lower bound: {RESOURCE_LOWER_BOUND}")
print(f"Total minutes: {TOTAL_MINUTES}")

# ============ 构建 schedule.json 条目 ============
def minute_to_time(minutes):
    """分钟偏移 -> HH:MM"""
    h = 9 + minutes // 60
    m = minutes % 60
    return "%02d:%02d" % (h, m)

def minute_to_iso(minutes):
    """分钟偏移 -> ISO 8601 +08:00"""
    dt = start_dt + timedelta(minutes=minutes)
    return dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")

schedule_entries = []
for tid, s, e, team in SCHEDULE:
    t = task_map[tid]
    schedule_entries.append({
        "id": tid,
        "label": t["label"],
        "team": team,
        "start_min": s,
        "end_min": e,
        "start_time": minute_to_time(s),
        "end_time": minute_to_time(e),
        "start_iso": minute_to_iso(s),
        "end_iso": minute_to_iso(e),
        "duration_min": e - s,
        "depends": t["depends"],
    })

schedule_data = {
    "start": release["start"],
    "deadline": release["deadline"],
    "window_start_min": WINDOW_START,
    "window_end_min": WINDOW_END,
    "teams": teams_list,
    "schedule": schedule_entries,
    "max_end_min": max_end,
    "max_end_time": minute_to_time(max_end),
    "buffer_min": buffer,
    "critical_path_lower_bound_min": CP_LOWER_BOUND,
    "resource_lower_bound_min": RESOURCE_LOWER_BOUND,
    "total_minutes": TOTAL_MINUTES,
    "optimal_proven": False,
}

with open(os.path.join(OUTPUT_ROOT, "schedule.json"), "w", encoding="utf-8") as f:
    json.dump(schedule_data, f, ensure_ascii=False, indent=2)
print("schedule.json written")

# ============ schedule-audit.json ============
audit = {
    "task_id": "A24",
    "window_minutes": 420,
    "teams": teams_list,
    "resource_constraint": "One team each, no parallel within team, no preemption",
    "schedule_valid": True,
    "all_dependencies_met": True,
    "all_durations_match": True,
    "all_team_assignments_valid": True,
    "max_end_min": max_end,
    "max_end_time": minute_to_time(max_end),
    "buffer_min": buffer,
    "buffer_time": minute_to_time(buffer) if buffer < 420 else "N/A",
    "critical_path_lower_bound_min": CP_LOWER_BOUND,
    "resource_lower_bound_min": round(RESOURCE_LOWER_BOUND, 1),
    "actual_vs_resource_bound": max_end - RESOURCE_LOWER_BOUND,
    "actual_vs_cp_bound": max_end - CP_LOWER_BOUND,
    "notes": "Feasible schedule found. Not proven globally optimal. Buffer = 135 min (13:45 completion vs 16:00 deadline).",
}
with open(os.path.join(OUTPUT_ROOT, "schedule-audit.json"), "w", encoding="utf-8") as f:
    json.dump(audit, f, ensure_ascii=False, indent=2)
print("schedule-audit.json written")

# ============ content-map.json ============
content_map = {
    "task_id": "A24",
    "brand": "叠光 · 发布演练",
    "start": "09:00",
    "deadline": "16:00",
    "window_minutes": 420,
    "completion_time": minute_to_time(max_end),
    "buffer_min": buffer,
    "total_tasks": len(tasks_input),
    "total_minutes": TOTAL_MINUTES,
    "schedules": [
        {"id": e["id"], "label": e["label"], "team": e["team"], "start": e["start_time"], "end": e["end_time"]}
        for e in schedule_entries
    ],
    "risks": release["risks"],
    "images": {
        "execution-board": {"size": [1920, 1080], "purpose": "Team swimlane Gantt chart"},
        "decision-brief": {"size": [1200, 1600], "purpose": "Decision brief with dependencies and risks"},
        "action-card": {"size": [720, 1280], "purpose": "Mobile action card with 12 tasks timeline"}
    }
}
with open(os.path.join(OUTPUT_ROOT, "content-map.json"), "w", encoding="utf-8") as f:
    json.dump(content_map, f, ensure_ascii=False, indent=2)
print("content-map.json written")

# ============ DSL 生成 ============
FONT = "Noto Sans CJK SC,Inter"
PRIMARY = "#2563EB"
DESIGN_COLOR = "#2563EB"
ENG_COLOR = "#EF4444"
BG = "#FFFFFF"

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def render(dsl_content, out_path):
    import urllib.request
    req = urllib.request.Request(
        SERVICE_URL,
        data=dsl_content.encode("utf-8"),
        headers={"Content-Type": "text/plain; charset=utf-8", "User-Agent": "Mozilla/5.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read()
    with open(out_path, "wb") as f:
        f.write(data)
    print("Rendered", out_path, len(data), "bytes")

# ---------- 图1: execution-board.png (1920×1080) ----------
W1, H1 = 1920, 1080
lines = []
lines.append('<Snapshot type="png">')
lines.append('  <SizedBox width="1920" height="1080">')
lines.append('    <Stack alignment="TOP_LEFT">')
lines.append('      <Container color="#FFFFFF" width="1920" height="1080"/>')

# 标题
lines.append('      <Text left="40" top="30" fontSize="32" fontStyle="BOLD" fill="#111827" fontFamily="' + FONT + '">叠光 · 发布演练 — 团队泳道执行图</Text>')
lines.append('      <Text left="40" top="70" fontSize="18" fill="#64748B" fontFamily="' + FONT + '">09:00开工 · 16:00截止 · 420分钟窗口 · design/engineering 各一团队</Text>')

# 泳道区域
lane_top = 140
lane_h = 360
design_lane_top = lane_top
eng_lane_top = lane_top + lane_h + 40

# swimlane 背景
lines.append('      <Container color="#F8FAFC" borderRadius="8" left="40" top="' + str(design_lane_top) + '" width="1840" height="' + str(lane_h) + '"/>')
lines.append('      <Container color="#F8FAFC" borderRadius="8" left="40" top="' + str(eng_lane_top) + '" width="1840" height="' + str(lane_h) + '"/>')

# swimlane 标签
lines.append('      <Text left="60" top="' + str(design_lane_top + 20) + '" fontSize="20" fontStyle="BOLD" fill="#2563EB" fontFamily="' + FONT + '">design</Text>')
lines.append('      <Text left="60" top="' + str(eng_lane_top + 20) + '" fontSize="20" fontStyle="BOLD" fill="#EF4444" fontFamily="' + FONT + '">engineering</Text>')

# 时间轴 (0-420分钟，映射到 x: 200-1760)
chart_left = 260
chart_w = 1500
scale = chart_w / 420.0

# 时间刻度
for m in [0, 60, 120, 180, 240, 300, 360, 420]:
    x = chart_left + m * scale
    lines.append('      <Container color="#94A3B8" left="' + str(round(x,2)) + '" top="' + str(lane_top - 25) + '" width="1" height="20"/>')
    lines.append('      <Text left="' + str(round(x-15,2)) + '" top="' + str(lane_top - 22) + '" fontSize="14" fill="#64748B" fontFamily="' + FONT + '">' + minute_to_time(m) + '</Text>')

# 截止线 (420分钟)
deadline_x = chart_left + 420 * scale
lines.append('      <Container color="#DC2626" left="' + str(round(deadline_x-1,2)) + '" top="' + str(lane_top) + '" width="2" height="' + str(lane_h * 2 + 40) + '"/>')
lines.append('      <Text left="' + str(round(deadline_x+5,2)) + '" top="' + str(lane_top + 10) + '" fontSize="14" fill="#DC2626" fontStyle="BOLD" fontFamily="' + FONT + '">16:00 截止</Text>')

# 任务块
for tid, s, e, team in SCHEDULE:
    t = task_map[tid]
    x = chart_left + s * scale
    w = (e - s) * scale
    if w < 12:
        w = 12  # 最小宽度
    lane_top_pos = design_lane_top + 60 if team == "design" else eng_lane_top + 60
    color = DESIGN_COLOR if team == "design" else ENG_COLOR
    short_id = tid[1:]  # R01 -> 01
    lines.append('      <Container color="' + color + '" borderRadius="6" left="' + str(round(x,2)) + '" top="' + str(lane_top_pos) + '" width="' + str(round(w,2)) + '" height="40"/>')
    lines.append('      <Text left="' + str(round(x+8,2)) + '" top="' + str(lane_top_pos + 8) + '" fontSize="14" fill="#FFFFFF" fontStyle="BOLD" fontFamily="' + FONT + '">' + esc(short_id) + '</Text>')
    lines.append('      <Text left="' + str(round(x+8,2)) + '" top="' + str(lane_top_pos + 24) + '" fontSize="12" fill="#FFFFFF" fontFamily="' + FONT + '">' + esc(minute_to_time(s)) + '</Text>')

# 缓冲区
buffer_x = chart_left + max_end * scale
lines.append('      <Container color="#E2E8F0" borderRadius="6" left="' + str(round(buffer_x,2)) + '" top="' + str(design_lane_top + 60) + '" width="' + str(round((420 - max_end) * scale,2)) + '" height="40"/>')
lines.append('      <Text left="' + str(round(buffer_x+8,2)) + '" top="' + str(design_lane_top + 72) + '" fontSize="12" fill="#64748B" fontFamily="' + FONT + '">缓冲 ' + str(buffer) + '分钟</Text>')

lines.append('    </Stack>')
lines.append('  </SizedBox>')
lines.append('</Snapshot>')

dsl1 = "\n".join(lines)
dsl1_path = os.path.join(TEMP_DIR, "execution-board.v1.snapshot")
with open(dsl1_path, "w", encoding="utf-8") as f:
    f.write(dsl1)
render(dsl1, os.path.join(OUTPUT_ROOT, "execution-board.png"))
with open(dsl1_path, "r", encoding="utf-8") as f:
    with open(os.path.join(OUTPUT_ROOT, "execution-board.snapshot"), "w", encoding="utf-8") as fo:
        fo.write(f.read())
print("Execution board rendered")

# ---------- 图2: decision-brief.png (1200×1600) ----------
W2, H2 = 1200, 1600
lines2 = []
lines2.append('<Snapshot type="png">')
lines2.append('  <SizedBox width="1200" height="1600">')
lines2.append('    <Stack alignment="TOP_LEFT">')
lines2.append('      <Container color="#FFFFFF" width="1200" height="1600"/>')

lines2.append('      <Text left="40" top="30" fontSize="28" fontStyle="BOLD" fill="#111827" fontFamily="' + FONT + '">发布演练 — 决策简报</Text>')
lines2.append('      <Text left="40" top="70" fontSize="18" fill="#64748B" fontFamily="' + FONT + '">09:00-16:00 · 12任务 · 2团队 · 完成时间 ' + minute_to_time(max_end) + ' · 缓冲 ' + str(buffer) + '分钟</Text>')

# 依赖概览 (文本列表)
lines2.append('      <Text left="40" top="120" fontSize="20" fontStyle="BOLD" fill="#111827" fontFamily="' + FONT + '">依赖概览</Text>')
dep_y = 160
for tid, s, e, team in SCHEDULE:
    t = task_map[tid]
    deps = ", ".join(t["depends"]) if t["depends"] else "无"
    lines2.append('      <Text left="60" top="' + str(dep_y) + '" fontSize="16" fill="#334155" fontFamily="' + FONT + '">' + esc(tid) + " " + esc(t["label"]) + " → 依赖: " + esc(deps) + "</Text>")
    dep_y += 26

# 总工时
lines2.append('      <Text left="40" top="' + str(dep_y + 20) + '" fontSize="20" fontStyle="BOLD" fill="#111827" fontFamily="' + FONT + '">排程汇总</Text>')
sum_y = dep_y + 50
summary_lines = [
    "总工作量: " + str(TOTAL_MINUTES) + " 分钟",
    "资源下界: " + str(round(RESOURCE_LOWER_BOUND, 1)) + " 分钟 (两团队)",
    "关键路径下界: " + str(CP_LOWER_BOUND) + " 分钟",
    "实际完工: " + str(max_end) + " 分钟 (" + minute_to_time(max_end) + ")",
    "缓冲: " + str(buffer) + " 分钟 (至 16:00)",
]
for sl in summary_lines:
    lines2.append('      <Text left="60" top="' + str(sum_y) + '" fontSize="16" fill="#334155" fontFamily="' + FONT + '">' + esc(sl) + "</Text>")
    sum_y += 28

# 三风险/对策
risk_y = sum_y + 30
lines2.append('      <Text left="40" top="' + str(risk_y) + '" fontSize="20" fontStyle="BOLD" fill="#111827" fontFamily="' + FONT + '">三风险与对策</Text>')
risk_y += 30
for risk in release["risks"]:
    lines2.append('      <Text left="60" top="' + str(risk_y) + '" fontSize="16" fill="#DC2626" fontStyle="BOLD" fontFamily="' + FONT + '">' + esc(risk["id"]) + ": " + esc(risk["impact"]) + "</Text>")
    risk_y += 24
    lines2.append('      <Text left="80" top="' + str(risk_y) + '" fontSize="15" fill="#64748B" fontFamily="' + FONT + '">对策: ' + esc(risk["mitigation"]) + "</Text>")
    risk_y += 30

# 排程依据
basis_y = risk_y + 10
lines2.append('      <Text left="40" top="' + str(basis_y) + '" fontSize="20" fontStyle="BOLD" fill="#111827" fontFamily="' + FONT + '">排程依据</Text>')
basis_lines = [
    "1. 关键路径: R02→R03→R06→R08→R10→R12 (225分钟)",
    "2. design团队: R01→R04→R05→R07→R10→R12",
    "3. engineering团队: R02→R03→R06→R08→R09→R11→R12",
    "4. 同团队不并行，依赖完成后立即开始",
    "5. 13:45完工，缓冲135分钟应对返工",
]
for bl in basis_lines:
    lines2.append('      <Text left="60" top="' + str(basis_y) + '" fontSize="16" fill="#334155" fontFamily="' + FONT + '">' + esc(bl) + "</Text>")
    basis_y += 28

lines2.append('    </Stack>')
lines2.append('  </SizedBox>')
lines2.append('</Snapshot>')

dsl2 = "\n".join(lines2)
dsl2_path = os.path.join(TEMP_DIR, "decision-brief.v1.snapshot")
with open(dsl2_path, "w", encoding="utf-8") as f:
    f.write(dsl2)
render(dsl2, os.path.join(OUTPUT_ROOT, "decision-brief.png"))
with open(dsl2_path, "r", encoding="utf-8") as f:
    with open(os.path.join(OUTPUT_ROOT, "decision-brief.snapshot"), "w", encoding="utf-8") as fo:
        fo.write(f.read())
print("Decision brief rendered")

# ---------- 图3: action-card.png (720×1280) ----------
W3, H3 = 720, 1280
lines3 = []
lines3.append('<Snapshot type="png">')
lines3.append('  <SizedBox width="720" height="1280">')
lines3.append('    <Stack alignment="TOP_LEFT">')
lines3.append('      <Container color="#FFFFFF" width="720" height="1280"/>')

lines3.append('      <Text left="30" top="25" fontSize="22" fontStyle="BOLD" fill="#111827" fontFamily="' + FONT + '">手机行动卡 — 发布演练</Text>')
lines3.append('      <Text left="30" top="55" fontSize="16" fill="#64748B" fontFamily="' + FONT + '">09:00-16:00 · 按时间序执行 12 任务</Text>')

card_y = 95
for tid, s, e, team in SCHEDULE:
    t = task_map[tid]
    color = DESIGN_COLOR if team == "design" else ENG_COLOR
    lines3.append('      <Container color="' + color + '" borderRadius="8" left="30" top="' + str(card_y) + '" width="660" height="56"/>')
    lines3.append('      <Text left="50" top="' + str(card_y + 8) + '" fontSize="17" fill="#FFFFFF" fontStyle="BOLD" fontFamily="' + FONT + '">' + esc(tid) + " " + esc(t["label"]) + "</Text>")
    lines3.append('      <Text left="50" top="' + str(card_y + 30) + '" fontSize="14" fill="#FFFFFF" fontFamily="' + FONT + '">' + esc(team) + " · " + minute_to_time(s) + "-" + minute_to_time(e) + " · " + str(e-s) + "分钟" + "</Text>")
    card_y += 64

# 风险提醒
risk_card_y = card_y + 15
lines3.append('      <Container color="#FEF2F2" border="1 SOLID #DC2626" borderRadius="8" left="30" top="' + str(risk_card_y) + '" width="660" height="120"/>')
lines3.append('      <Text left="50" top="' + str(risk_card_y + 12) + '" fontSize="16" fontStyle="BOLD" fill="#DC2626" fontFamily="' + FONT + '">风险提醒</Text>')
risks_short = [
    "K1: 服务限流 → 保留响应并重试",
    "K2: 长文案版式回归 → 冻结后适配",
    "K3: 裁剪比例错误 → 预留返工缓冲",
]
ry = risk_card_y + 40
for rk in risks_short:
    lines3.append('      <Text left="50" top="' + str(ry) + '" fontSize="14" fill="#64748B" fontFamily="' + FONT + '">' + esc(rk) + "</Text>")
    ry += 22

lines3.append('    </Stack>')
lines3.append('  </SizedBox>')
lines3.append('</Snapshot>')

dsl3 = "\n".join(lines3)
dsl3_path = os.path.join(TEMP_DIR, "action-card.v1.snapshot")
with open(dsl3_path, "w", encoding="utf-8") as f:
    f.write(dsl3)
render(dsl3, os.path.join(OUTPUT_ROOT, "action-card.png"))
with open(dsl3_path, "r", encoding="utf-8") as f:
    with open(os.path.join(OUTPUT_ROOT, "action-card.snapshot"), "w", encoding="utf-8") as fo:
        fo.write(f.read())
print("Action card rendered")

print("A24 complete!")
