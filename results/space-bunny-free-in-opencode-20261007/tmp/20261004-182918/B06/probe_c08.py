# -*- coding: utf-8 -*-
"""Scratch: probe the case-08 tax model before wiring the numbers into the sheet."""
import io
import os

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_c08.py")
src = io.open(P, encoding="utf-8").read()
head = src.split("W, H = 1240, 1754")[0]
G = {"__file__": P, "__name__": "probe"}
exec(head, G)
gn = G["gross_to_net"]
for m in (15000, 20000, 25000, 28000, 30000, 36000, 40000, 45000, 50000, 60000):
    d = gn(float(m))
    print("%6d taxable=%8.0f tax_y=%9.0f tax_m=%8.1f net=%9.1f ratio=%.4f"
          % (m, d["taxable"], d["tax_y"], d["tax_m"], d["net"], d["net"] / m))
a, b = gn(25000.0), gn(28000.0)
print("delta net = %.1f  marginal = %.4f" % (b["net"] - a["net"], (b["net"] - a["net"]) / 3000.0))
print("25k ratio %.4f  28k ratio %.4f" % (a["net"] / 25000.0, b["net"] / 28000.0))
# where does the marginal rate step?  marginal tax rate changes when taxable crosses
# a bracket edge:  taxable = gross*12 - 60000 - 84000
for edge, br in ((36000, 0.03), (144000, 0.10), (300000, 0.20), (420000, 0.25)):
    print("taxable %7d at gross/month = %.0f" % (edge, (edge + 144000) / 12.0))