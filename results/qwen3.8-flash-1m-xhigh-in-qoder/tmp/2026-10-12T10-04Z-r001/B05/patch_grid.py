"""One-off patch: replace the 7-day grid with an explicit 14-day taken/missed log.

The tablet view quotes a 14-day adherence rate, so the visible grid has to cover the
same window; otherwise every cell is green while the caption reports missed doses.
"""
import ast
import re
from pathlib import Path

fp = Path(__file__).resolve().parent / "b05data.py"
t = fp.read_text(encoding="utf-8")

old = re.search(r'def week_grid\(\):.*?\n    return days, grid\n', t, re.S)
assert old, "week_grid not found"
new = '''def day_grid():
    """14-day taken/missed log per medicine, oldest cell first.

    Fills from the newest day backwards until the 14-day taken count is used up, so a
    medicine with a partial day shows one amber cell and the misses sit at the far end
    of the window - the same window the quoted adherence rate covers.
    """
    days = [(TODAY - timedelta(days=i)).isoformat() for i in range(13, -1, -1)]
    grid = {}
    for m in MEDS:
        if not m["doses"]:
            continue
        n = DOSE_COUNT[m["id"]]
        left = TAKEN[m["id"]]
        cells = []
        for _ in range(14):
            take = min(n, left)
            left -= take
            cells.append(["取"] * take + ["漏"] * (n - take))
        cells.reverse()
        assert sum(c.count("取") for c in cells) == TAKEN[m["id"]]
        grid[m["id"]] = cells
    return days, grid


'''
t = t[:old.start()] + new + t[old.end():]
t = t.replace('DAYS, GRID = week_grid()', 'DAYS, GRID = day_grid()')
t = t.replace('"week_days": DAYS, "week_grid": GRID,', '"days14": DAYS, "grid14": GRID,')
# the 7-day slices the printout quotes come out of the same log
t = t.replace('DATA["per_person"] = PER_PERSON',
              'DATA["per_person"] = PER_PERSON\n'
              'DATA["week_days"] = DAYS[-7:]\n'
              'DATA["week_grid"] = {k: [r[i] for i in range(7, 14)] for k, r in\n'
              '                        GRID.items()}\n')
ast.parse(t)
fp.write_text(t, encoding="utf-8")
print("day_grid installed")
