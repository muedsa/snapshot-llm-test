p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A22\build_a22.py'
s = open(p, encoding='utf-8').read()
pairs = [
    ('''        if m["month"] == "2026-10":
            doc.text(tx + 16, round(ry + rh * 0.26 + 22), "新增月份", 20, PROFIT,
                     weight="BOLD", maxw=90)''',
     '''        if m["month"] == "2026-10":
            # the new month is marked by its own accent tint instead of extra copy, so the
            # mark can never spill outside the table panel
            doc.box(tx + 12, round(ry), tw - 24, round(rh), "#ECFDF5FF", radius=8)
            doc.box(tx + 12, round(ry), 4, round(rh), PROFIT, radius=(0, 2))'''),
    ('''        (f'总体转化率按全部 {t["months"]} 个月的 orders 合计 ÷ sessions 合计计算，'
         f'不是各月转化率的平均；表格与柱高来自同一份计算结果。' if rnd >= 3 else
         "总体转化率按全部 6 个月的 orders 合计 ÷ sessions 合计计算，"
         "不是各月转化率的平均；表格与柱高来自同一份计算结果。"),''',
     '''        (f'总体转化率按全部 {t["months"]} 个月的 orders 合计 ÷ sessions 合计计算，'
         f'不是各月转化率的平均；表格绿色标记行为新增月份 2026-10。' if rnd >= 3 else
         "总体转化率按全部 6 个月的 orders 合计 ÷ sessions 合计计算，"
         "不是各月转化率的平均；表格与柱高来自同一份计算结果。"),'''),
]
for a, b in pairs:
    assert a in s, 'MISSING: ' + a[:60]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched new-month marker')
