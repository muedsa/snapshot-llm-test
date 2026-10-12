import io

p = "spec_a15.py"
s = io.open(p, encoding="utf-8").read()
pairs = [
    ('("kpi2_label", "ORDERS", 668, 160, SEMI, 13, "muted", 0.8)',
     '("kpi2_label", "ORDERS", 668, 160, EB, 13, "muted", 0.6)'),
    ('("kpi3_label", "REFUND RATE", 1052, 160, SEMI, 13, "muted", 0.8)',
     '("kpi3_label", "REFUND RATE", 1052, 160, EB, 13, "muted", 0.6)'),
    ('("side_label", "PRO WORKSPACE", 38, 770, SEMI, 12, "mint", 0.8)',
     '("side_label", "PRO WORKSPACE", 38, 770, EB, 12.5, "mint", 0.3)'),
]
for a, b in pairs:
    if a not in s:
        print("MISS:", a)
    s = s.replace(a, b)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
for line in s.splitlines():
    if any(k in line for k in ("kpi1_label", "kpi2_label", "kpi3_label", "side_label")):
        print(line.strip())
