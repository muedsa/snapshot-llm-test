import os, sys
sys.path.insert(0, r"tmp\\20261003-114508-flashmax\\B03\scripts")
from sk import Sk, MONO
import std
s = Sk(1200, 460, "#101418FF")
s.text(40, 40, "RAW amp:  A & B   C < D   E > F", 22, "#F8FAFCFF", family=MONO)
s.text(40, 90, "ENTITY:   A &amp; B   C &lt; D   E &gt; F", 22, "#F8FAFCFF", family=MONO)
s.text(40, 140, "QUOTE:    \"double\" and 'single' and \u2014 dash", 22, "#F8FAFCFF", family=MONO)
s.text(40, 190, "AMP ONLY: 14:30 & 19:30", 22, "#F8FAFCFF", family=MONO)
s.text(40, 240, "ampersand in cn: 盐 & 胡椒", 22, "#F8FAFCFF")
s.text(40, 300, "css colour names, no escaping needed: rebeccapurple", 20, "#94A3B8FF", family=MONO)
s.raw('<Positioned left="40" top="350"><Text fontSize="22" color="#F8FAFCFF" fontFamily="Noto Sans Mono CJK SC">percent: 100%  amp: &amp;amp;  lt: &amp;lt;</Text></Positioned>')
std.write(os.path.join(r"tmp\\20261003-114508-flashmax\\B03", "dsl", "probe-15.snapshot"), s.finish())
print("ok")