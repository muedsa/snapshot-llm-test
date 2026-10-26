# -*- coding: utf-8 -*-
"""A12 mobile space budget check."""
# mobile: 360x800, margin 16
W, H, M = 360, 800, 16
hero_pad = 20
title = 40
subtitle = 20
chip = 16
cta = 18
footnote = 16
card_pad = 14
card_title = 18
card_detail = 16
cols = 1
rows = 6

hw = W - 2 * M - 2 * hero_pad   # 360-32-40 = 288
title_est = title * 0.52 * len("Structure / Vision")   # 40*0.52*18 = 374
title_lines = 2 if title_est > hw else 1
title_block = title_lines * (title + 6)

sub_est = subtitle * 1.0 * len("让模型从读懂文档到完成作品")   # 20*13 = 260
sub_lines = 2 if sub_est > hw else 1
sub_block = sub_lines * (subtitle + 4)

chip_h = chip + 12
meta = ["2026.11.07", "09:00–16:00", "云构中心 · ONLINE"]
meta_est = [chip * 0.62 * len(t) + 28 for t in meta]
print("meta est widths:", [round(w, 1) for w in meta_est], "hw =", hw)
chip_rows, cur = 1, 0.0
for w in meta_est:
    if cur + w > hw and cur > 0:
        chip_rows += 1
        cur = w + 8
    else:
        cur += w + 8
meta_block = chip_rows * chip_h + (chip_rows - 1) * 8

cta_btn_h = cta + 16
cta_est = cta * 0.62 * len("免费参加 · 扫码方式详见官网") + 28
web_est = footnote * 0.62 * len("structure.example.org")
cta_rows = 1 if (cta_est + 16 + web_est) <= hw else 2

hero_h = (hero_pad * 2 + title_block + 10 + sub_block + 16 + meta_block + 14
          + cta_rows * cta_btn_h + (10 if cta_rows > 1 else 0))
print(f"title_lines={title_lines} title_block={title_block}")
print(f"sub_lines={sub_lines} sub_block={sub_block}")
print(f"chip_rows={chip_rows} meta_block={meta_block}")
print(f"cta_rows={cta_rows} cta_est={cta_est:.0f} web_est={web_est:.0f}")
print(f"hero_h={hero_h}")

dot_d = 22
min_card = card_pad + dot_d + 10 + card_detail + 8 + card_pad
print(f"min_card_h={min_card}")
need = rows * min_card + (rows - 1) * 6 + 28 + footnote + 24 + M
print(f"total need = {M} + {hero_h} + {need} = {M + hero_h + need} (H={H})")

# 压缩 hero 后的极限
hero_min = hero_pad * 2 + title_block + sub_block + chip_h + cta_btn_h
print(f"hero_min (单行 chip + 单行 cta) = {hero_min}")
print(f"total with hero_min = {M + hero_min + need}")
print(f"remaining for cards = {H - M - hero_min - 28 - footnote - 24 - (rows-1)*6}")
print(f"per card = {(H - M - hero_min - 28 - footnote - 24 - (rows-1)*6) / rows:.1f}")
