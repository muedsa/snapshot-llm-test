# -*- coding: utf-8 -*-
"""A12 mobile budget v4 - with compact tokens."""
W, H, M = 360, 800, 16
hero_pad = 12
title, subtitle, chip, cta, footnote = 40, 20, 16, 18, 16
card_pad, card_title, card_detail = 10, 18, 16
gap = 8
cols, rows = 1, 6
dot_d = 18

hw = W - 2 * M - 2 * hero_pad     # 360-32-24 = 304
title_lines = 2
title_block = title_lines * (title + 6)      # 92
sub_block = 1 * (subtitle + 4)               # 24
chip_h = chip + 12                           # 28
chip_rows = 2
meta_block = chip_rows * chip_h + (chip_rows - 1) * 8   # 64
cta_btn_h = cta + 16                         # 34
cta_rows = 2

hero_h = (hero_pad * 2 + title_block + 10 + sub_block + 16 + meta_block + 14
          + cta_rows * cta_btn_h + 10)
print(f"hw={hw} hero_h={hero_h}")

min_card_h = card_pad + max(dot_d, card_title) + 8 + card_detail + card_pad
print(f"min_card_h = {min_card_h}")
SECTION_HDR = 28
need_cards = rows * min_card_h + (rows - 1) * 4 + SECTION_HDR + footnote + 24 + M
print(f"need_cards={need_cards} total={M+hero_h+need_cards}")

overflow = (M + hero_h + need_cards) - H
print(f"overflow={overflow}")
SECTION_HDR -= min(overflow, 8); overflow -= min((M+hero_h+need_cards)-H, 8)
pad_cut = min(overflow, max(0, hero_pad - 10) * 2)
hero_h -= pad_cut; overflow -= pad_cut
gap_cut = min(overflow, 40 - 12)
hero_h -= gap_cut; overflow -= gap_cut
if chip_rows > 1:
    cg = min(overflow, (chip_rows - 1) * 4)
    hero_h -= cg; overflow -= cg
print(f"after: hero_h={hero_h} SECTION_HDR={SECTION_HDR} overflow={overflow}")

cards_top = M + hero_h + gap + SECTION_HDR
avail = H - M - (footnote + 24) - cards_top
print(f"cards_top={cards_top} avail={avail}")
card_h = min_card_h + 24
need = rows * card_h + (rows - 1) * gap
print(f"need(card_h={card_h}, gap={gap})={need}")
if need > avail:
    new_gap = max(4, gap - (need - avail) // rows - 1)
    print(f" new_gap={new_gap} -> need={rows*card_h+(rows-1)*new_gap}")
    if rows * card_h + (rows - 1) * new_gap <= avail:
        print("  OK with new_gap")
    else:
        print(f"  card_h={max(min_card_h,(avail-(rows-1)*gap)//rows)}")
