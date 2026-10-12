# -*- coding: utf-8 -*-
"""临时量宽器：给定 (宽, 字号, 文本) 返回 TextFit 估计的行数与所需高度。非成品证据。"""
import sys, io, json
sys.path.insert(0, str("tmp/20261008T1615Z-run01/_suite/scripts"))
from dslkit import TextFit
tf = TextFit()
for bw, size, s in json.load(io.open(sys.argv[1], encoding="utf-8")):
    nl, h = tf.need(s, size, bw)
    print("%5d %5.1f -> nl=%d h=%.1f est_w=%.0f | %s" % (bw, size, nl, h, tf.w(s, size), s[:34]))
