# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
tm = json.load(open("outputs/20261016T164020-m1/A11/text-map.json", encoding="utf-8"))
for n in tm["entries"]:
    if n["role"] == "body" and n["font"]["font_size_px"] < 24:
        print(n["key"], n["font"]["font_size_px"], n["source_text"][:30])
