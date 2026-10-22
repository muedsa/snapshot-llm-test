# -*- coding: utf-8 -*-
"""Dump every text= payload of a snapshot for AM compliance reading."""
import io
import re
import sys

fn = sys.argv[1]
s = io.open(fn, encoding="utf-8").read()
texts = re.findall(r'text="([^"]*)"', s)
for i, t in enumerate(texts):
    t = (t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
          .replace("&quot;", '"'))
    print("{:3d}| {}".format(i, t))
