# -*- coding: utf-8 -*-
"""A12 mobile budget v2."""
W, H, M = 360, 800, 16
hero_pad_eff = 10
title, subtitle, chip, cta, footnote = 40, 20, 16, 18, 16
card_pad, card_title, card_detail = 14, 18, 16
cols, rows = 1, 6

hw = W - 2 * M - 2 * hero_pad_eff
title_lines = 2
title_block = title_lines * (title + 6)
sub_block = 1 * (subtitle + 4)
chip_h = chip + 12
chip_rows = 2
meta_block = chip_rows * chip_h + (chip_rows - 1) * 4
cta_btn_h = cta + 16
cta_rows = 2

hero_h = (hero_pad_eff * 2 + title_block + 4 + sub_block + 4 + meta_block + 4
          + cta_rows * cta_btn_h + 4)
print(f"hero_h (compressed) = {hero_h}")

dot_d = 22
min_card = card_pad + max(dot_d, card_title) + 8 + card_detail + card_pad
print(f"min_card_h = {min_card}")

cards_top = M + hero_h + 12 + 28
footer_h = footnote + 24
avail = H - M - footer_h - cards_top
print(f"cards_top = {cards_top}, avail for cards = {avail}")
need = rows * min_card + (rows - 1) * 4
print(f"need = {need}")
print(f"per card available = {(avail - (rows-1)*4)/rows:.1f}")
