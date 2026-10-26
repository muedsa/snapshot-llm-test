# -*- coding: utf-8 -*-
"""A12 mobile budget v3 - trace actual code path."""
W, H, M = 360, 800, 16
hero_pad = 20
title, subtitle, chip, cta, footnote = 40, 20, 16, 18, 16
card_pad, card_title, card_detail = 14, 18, 16
gap = 12
cols, rows = 1, 6

hw = W - 2 * M - 2 * hero_pad
title_lines = 2
title_block = title_lines * (title + 6)      # 92
sub_lines = 1
sub_block = sub_lines * (subtitle + 4)       # 24
chip_h = chip + 12                           # 28
chip_rows = 2
meta_block = chip_rows * chip_h + (chip_rows - 1) * 8   # 64
cta_btn_h = cta + 16                         # 34
cta_rows = 2

hero_h = (hero_pad * 2 + title_block + 10 + sub_block + 16 + meta_block + 14
          + cta_rows * cta_btn_h + 10)
print(f"hero_h = {hero_h}")

dot_d_min = 22
min_card_h = card_pad + max(dot_d_min, card_title) + 8 + card_detail + card_pad
print(f"min_card_h = {min_card_h}")
SECTION_HDR = 28
need_cards = rows * min_card_h + (rows - 1) * 4 + SECTION_HDR + footnote + 24 + M
print(f"need_cards = {need_cards}")
total = M + hero_h + need_cards
print(f"total = {total}, H = {H}, overflow = {total - H}")

# compression
overflow = total - H
SECTION_HDR -= min(overflow, 8); overflow -= min(total - H, 8)
pad_cut = min(overflow, max(0, hero_pad - 10) * 2)
hero_h -= pad_cut; overflow -= pad_cut
gap_cut = min(overflow, 40 - 12)
hero_h -= gap_cut; overflow -= gap_cut
if chip_rows > 1:
    cg = min(overflow, (chip_rows - 1) * 4)
    hero_h -= cg; overflow -= cg
print(f"after compression: hero_h={hero_h} SECTION_HDR={SECTION_HDR} remaining_overflow={overflow}")

cards_top = M + hero_h + gap + SECTION_HDR
print(f"cards_top = {cards_top}")
footer_h = footnote + 24
avail = H - M - footer_h - cards_top
print(f"avail for cards = {avail}")
card_h = min_card_h + 24
need = rows * card_h + (rows - 1) * gap
print(f"need with card_h={card_h}: {need}")
if need > avail:
    new_gap = max(4, gap - (need - avail) // rows - 1)
    print(f"  new_gap={new_gap}, need={rows*card_h + (rows-1)*new_gap}")
    if rows * card_h + (rows - 1) * new_gap <= avail:
        print("  -> use new_gap")
    else:
        print(f"  -> card_h = {max(min_card_h, (avail - (rows-1)*gap)//rows)}")
