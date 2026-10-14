"""One-off patch: make the tablet view render the 14-day log and quote per-person
statistics that come out of data.json instead of hand-written numbers."""
import ast
from pathlib import Path

fp = Path(__file__).resolve().parent / "b05pages.py"
t = fp.read_text(encoding="utf-8")

old_start = '    card_y = 170\n'
old_end = '    card(s, 28, 462, w - 56, 250, shadow=False)\n'
i, j = t.find(old_start), t.find(old_end)
assert i > 0 and j > i, (i, j)

new = '''    card_y = 170
    card(s, 28, card_y, w - 56, 282, shadow=False)
    s.text("t", "周秀兰 · 近 14 天服药格", 48, card_y + 18, 26, INK, bold=True)
    s.text("t", "每格一天的医嘱时点；左半为前一周，右半为最近一周", 48, card_y + 52,
           17, INK3)
    days = D["days14"]
    gx, gy = 170, card_y + 108
    cw, chh = 44, 26
    for j2, d in enumerate(days):
        if j2 % 2:
            today = j2 == len(days) - 1
            s.text("t", d[5:], gx + j2 * cw + cw / 2, gy - 28, 16,
                   INK if today else INK3, align="center", font=MONO, bold=today)
    s.line(gx + 7 * cw - 3, gy - 6, gx + 7 * cw - 3, gy + 3 * 44 + 22, LINE, 1.0)
    for i, mid in enumerate(grid_rows):
        m = MEDS[mid]
        s.text("t", m["short"], 48, gy + i * 44 + 4, 19, INK2)
        for j2, row in enumerate(D["grid14"][mid]):
            got = sum(1 for c in row if c == "取")
            need = len(row)
            col = GREEN if got == need else (RED if got == 0 else AMBER)
            s.rect(gx + j2 * cw, gy + i * 44, cw - 6, chh, col, radius=4)
            s.text("t", f"{got}/{need}", gx + j2 * cw + (cw - 6) / 2, gy + i * 44 + 3,
                   16, "#FFFFFF", align="center", font=MONO)
    s.text("t", "格内为『当日已确认时点数 / 应服时点数』；绿=全勤，黄=有漏，红=全漏。",
           48, gy + len(grid_rows) * 44 + 4, 17, INK3)
    pp = D["per_person"]
    rows = []
    for pid in ("gm", "da", "me"):
        st = pp[pid]
        if st["adherence_14"] is None:
            stat = f'{st["as_needed_meds"]} 种按需药 · 不计依从率'
            note = "无固定时点"
        else:
            stat = (f'{st["scheduled_meds"]} 种规律药 · {st["adherence_14"]:.1f}% '
                    f'（{st["taken_14"]}/{st["due_14"]}）')
            note = (f'14 天内漏 {st["missed_14"]} 次' if st["missed_14"]
                    else "14 天内无漏服")
        rows.append((PEOPLE[pid]["name"], stat, note))
'''
t = t[:i] + new + t[j:]

# grid_rows must exist before the loop that uses it
t = t.replace('    card_y = 170\n',
              '    grid_rows = [mid for mid in ("M1", "M2", "M3", "M5")\n'
              '                 if MEDS[mid]["who"] == "gm"]\n    card_y = 170\n', 1)
t = t.replace('''    grid_rows = [mid for mid in ("M1", "M2", "M3", "M5")
                 if MEDS[mid]["who"] == "gm"]
    days = D["week_days"]''', '''    days = D["week_days"]''')
ast.parse(t)
fp.write_text(t, encoding="utf-8")
print("p07 rewired to the 14-day log")
