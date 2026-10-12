# TextFit calibration finding (A14)

`dslkit.TextFit` estimates CJK advance at 1.02 em and then shrinks the usable box by
`SLACK = 0.96`. That double-counts roughly 6 % against the real renderer:

- K02 `读文档，也要读懂布局约束` = 12 CJK glyphs at 72 pt = 864 px, fits ONE line in an
  896 px box; the shared model predicts two.
- K08 line 1 `从“已经请求成功”到“已经完成作` measured 886 px estimated / 896 px available.

For a *clipping* gate the conservatism is correct — never let a box be too small. But using
the same number to size a box's height reserves lines that never render, which shows up as a
hole between the title and the next block.

**Do not change the shared class** (A01–A13 artefacts were built with it). When a task needs
box heights that match rendered line counts, subclass it locally the way
`tmp/<run_id>/A14/generate_a14.py` does (`Fit.w` with CJK 1.00 em, bold Latin 0.60 em,
`lines()` without slack), and verify the result by counting rendered text rows in the PNG
(`tmp/<run_id>/A14/check_a14.py: ink_rows/groups`).

Two checker traps recorded the same way:

- compare a per-channel threshold against `mean(axis=2)`, never against `sum(axis=2)`;
- the DSL attribute is `borderRadius` (capital R) — a lowercase `radius="` needle never matches.
