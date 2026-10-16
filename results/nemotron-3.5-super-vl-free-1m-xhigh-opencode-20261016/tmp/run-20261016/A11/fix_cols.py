p = 'tmp/run-20261016/A11/gen_a11.py'
s = open(p, encoding='utf-8').read()
s = s.replace('el.append(T("数量", 910, 184, w=40, size="20", bold=True, color="#64748B", align="END"))',
              'el.append(T("数量", 860, 184, w=50, size="20", bold=True, color="#64748B", align="END"))')
s = s.replace('el.append(T("单价（" + CUR + "）", 1040, 184, w=80, size="20", bold=True, color="#64748B", align="END"))',
              'el.append(T("单价（" + CUR + "）", 960, 184, w=80, size="20", bold=True, color="#64748B", align="END"))')
s = s.replace('el.append(T("金额（" + CUR + "）", 1152, 184, w=0, size="20", bold=True, color="#64748B", align="END"))  # right edge 1152',
              'el.append(T("金额（" + CUR + "）", 1032, 184, w=120, size="20", bold=True, color="#64748B", align="END"))')
s = s.replace('el.append(T(l["qty"], 910, y, w=40, size="20", align="END"))',
              'el.append(T(l["qty"], 860, y, w=50, size="20", align="END"))')
s = s.replace('el.append(T(l["unit"], 1040, y, w=80, size="20", align="END"))',
              'el.append(T(l["unit"], 960, y, w=80, size="20", align="END"))')
s = s.replace('el.append(T(l["amount"], W - M, y, size="20", align="END"))',
              'el.append(T(l["amount"], 1032, y, w=120, size="20", align="END"))')
open(p, 'w', encoding='utf-8').write(s)
print("done")
