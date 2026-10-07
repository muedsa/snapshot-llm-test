"""B03 review fix 3 - case-09 summary sentence.

Opening case-09/final.png and counting the changelog chips showed the summary
band claiming "没有引入新的破坏性变更，仅有两项弃用与七项修复" while CHANGES
actually holds 2 BREAKING + 2 DEPRECATED + 3 ADDED + 5 FIXED = 12 entries, and
the header says CHANGELOG · 12 ENTRIES.  So the sentence was wrong twice: it
denied the two BREAKING entries that are printed right above it, and it counted
seven fixes where there are five.

Fix: derive every count from CHANGES so the sentence cannot drift again.
"""
import io

p = "build_c09.py"
s = io.open(p, encoding="utf-8").read()
n = 0


def rep(old, new):
    global s, n
    assert old in s, old[:80]
    s = s.replace(old, new, 1)
    n += 1


rep('''SUMMARY = ("本版把 colormap 的多色标合成改成真正的减色叠印：ColorFiltered 的 "
           "color 与节点自身像素相乘，而不是与背景相乘，因此同一版矩阵在 "
           "C×M 与 M×C 两个方向上必然一致。除此之外没有引入新的破坏性变更，"
           "仅有两项弃用与七项修复。发布说明与迁移片段由维护者手写，"
           "本页所有数值均为演示用虚构数据。")''',
    '''_NUM = {"BREAKING": "破坏性变更", "DEPRECATED": "弃用", "ADDED": "新增",
        "FIXED": "修复"}
_CNT = {k: len([c for c in CHANGES if c[0] == k]) for k in _NUM}
assert _CNT["BREAKING"] + _CNT["DEPRECATED"] + _CNT["ADDED"] + _CNT["FIXED"] == 12

SUMMARY = ("本版把 colormap 的多色标合成改成真正的减色叠印：ColorFiltered 的 "
           "color 与节点自身像素相乘，而不是与背景相乘，因此同一版矩阵在 "
           "C×M 与 M×C 两个方向上必然一致。12 条变更里 %d 条破坏性变更、"
           "%d 条弃用、%d 条新增、%d 条修复。发布说明与迁移片段由维护者手写，"
           "本页所有数值均为演示用虚构数据。"
           % (_CNT["BREAKING"], _CNT["DEPRECATED"], _CNT["ADDED"],
              _CNT["FIXED"]))''')

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched", n, "blocks")