# -*- coding: utf-8 -*-
"""A17 structural verification (run after every regeneration).

Checks per page:
  1. core subtree lines appear verbatim (modulo the page's 6-space element
     indent) as one contiguous block, byte-identical to the standalone core;
  2. paint order: flat backing fills -> core -> captions/borders/text
     (BackdropFilter-safe paint order, see snapshot-usage.md);
  3. standalone core == page core after removing the page element indent.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))

from a17_defs import CORE_PREFIX, core_lines, standalone_text  # noqa: E402

GEN = pathlib.Path(__file__).resolve().parents[1] / "gen"
PAGE_INDENT = "      "          # one page element level


def page_lines(n):
    return (GEN / f"handbook-{n:02d}.snapshot").read_text(
        encoding="utf-8").splitlines()


def find_block(lines, block):
    """Return start index of contiguous occurrence of block in lines."""
    for i in range(len(lines) - len(block) + 1):
        if lines[i:i + len(block)] == block:
            return i
    return -1


def main():
    for n in (1, 2, 3, 4):
        key = f"0{n}"
        core = core_lines(key)
        # standalone: core block present verbatim
        st = standalone_text(key).splitlines()
        s_start = find_block(st, core)
        assert s_start >= 0, f"example-{key}: core block not found"

        # page: same block, shifted by exactly one element indent level
        pl = page_lines(n)
        shifted = [PAGE_INDENT + ln for ln in core]
        p_start = find_block(pl, shifted)
        assert p_start >= 0, f"handbook-{n:02d}: core block not found"

        # byte-identical after removing the page indent level
        norm = [ln[len(PAGE_INDENT):] for ln in pl[p_start:p_start + len(core)]]
        assert norm == core, f"handbook-{n:02d}: core differs from standalone"

        # paint order: flat fills before core, borders + captions after
        def idx(pred, lo=0):
            for i in range(lo, len(pl)):
                if pred(pl[i]):
                    return i
            return -1

        bg = idx(lambda l: 'left="0" top="0" width="1200" height="1600"' in l)
        frame_fill = idx(lambda l: 'width="460" height="358"' in l
                         and "border=" not in l)
        card_fill = idx(lambda l: 'width="400" height="240"><Container color='
                         in l)
        frame_line = idx(lambda l: 'width="460" height="358"' in l
                         and "border=" in l)
        card_line = idx(lambda l: 'width="400" height="240"><Container'
                        in l and "border=" in l)
        cap1 = idx(lambda l: "独立渲染" in l)
        assert 0 <= bg < frame_fill < card_fill < p_start, \
            f"handbook-{n:02d}: backing fills not before core " \
            f"({bg},{frame_fill},{card_fill},{p_start})"
        for name, i in (("frame border", frame_line),
                        ("card border", card_line), ("caption", cap1)):
            assert i > p_start, f"handbook-{n:02d}: {name} paints before " \
                                f"core (idx {i} <= {p_start})"
        # BackdropFilter isolation wrapper: only page 4's core needs it
        has_wrap = any('<Opacity opacity="1">' in l for l in pl)
        assert has_wrap == (n == 4), \
            f"handbook-{n:02d}: opacity layer wrapper = {has_wrap}"
        print(f"handbook-{n:02d}: core ok at line {p_start + 1}, "
              f"order ok, wrapper={has_wrap}")

    # core prefix discipline
    for key in ("01", "02", "03", "04"):
        for ln in core_lines(key):
            assert ln.startswith(CORE_PREFIX), (key, ln)
    print("all checks passed")


if __name__ == "__main__":
    main()
