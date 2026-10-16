import json, os

with open("tasks/A14-content-stress-batch/inputs/cards.json", "r", encoding="utf-8") as f:
    cards = json.load(f)

W, H = 1200, 630
MARGIN = 40
FONT = "Noto Sans CJK SC,Inter"
STATUS_COLORS = {
    "开放": "#22C55E",
    "满额": "#DC2626", 
    "候补": "#D97706",
    "取消": "#6B7280"
}

def calc_lines(text, font_size, width):
    """Calculate lines needed for text at given font size and width"""
    cpl = max(1, int(width / (font_size * 0.55)))  # Approximate char width
    words = text.split()
    lines = 1
    cur = ""
    for word in words:
        test = (cur + " " + word) if cur else word
        if len(test) <= cpl:
            cur = test
        else:
            lines += 1
            cur = word
    return max(1, lines)

os.makedirs("tmp/run-20261016/A19", exist_ok=True)

for idx, card in enumerate(cards):
    el = []
    el.append('<Snapshot background="#FFFFFF" type="png">')
    el.append(f'  <SizedBox width="{W}" height="{H}">')
    el.append('    <Stack alignment="TOP_LEFT" clipBehavior="NONE">')
    
    # Card background
    el.append(f'      <Positioned left="{MARGIN}" top="{MARGIN}" width="{W-2*MARGIN:.1f}" height="{H-2*MARGIN:.1f}">')
    el.append(f'        <Container color="#FFFFFF" border="1 SOLID #E2E8F0" borderRadius="10"/>')
    el.append(f'      </Positioned>')
    
    # Title area (left side)
    title_x = MARGIN + 24
    title_y = MARGIN + 24
    title_w = W - 2*MARGIN - 24 - 150  # Leave room for status badge on right
    
    title_size = 36
    title_lines = calc_lines(card["title"], 36, title_w - 48)  # Subtract padding
    title_height = title_lines * 36 * 1.2
    
    el.append(f'      <Positioned left="{title_x:.1f}" top="{title_y:.1f}" width="{title_w:.1f}" height="{title_height:.1f}">')
    el.append(f'        <Text color="#1F293B" fontSize="{title_size}" fontStyle="BOLD" fontFamily="Noto Sans CJK SC,Inter">{card["title"]}</Text>')
    el.append(f'      </Positioned>')
    
    # Speaker line below title
    speaker_y = title_y + title_lines * 36 * 1.2 + 12
    speaker_text = f'{card["speaker"]}  ·  {card["time"]}'
    el.append(f'      <Positioned left="{title_x:.1f}" top="{speaker_y:.1f}" width="{title_w:.1f}" height="24">')
    el.append(f'        <Text color="#6B7280" fontSize="22" fontFamily="{FONT}">{speaker_text}</Text>')
    el.append(f'      </Positioned>')
    
    # Status badge (right side)
    status = card["status"]
    status_color = STATUS_COLORS.get(status, "#6B7280")
    status_text_map = {"开放": "开放", "满额": "满额", "候补": "候补", "取消": "取消"}
    status_text = status_text_map.get(status, status)
    
    badge_x = W - MARGIN - 150
    badge_y = MARGIN + 24
    badge_w = 140
    badge_h = 56
    
    el.append(f'      <Positioned left="{badge_x:.1f}" top="{badge_y:.1f}" width="{badge_w:.1f}" height="{badge_h:.1f}">')
    el.append(f'        <Container color="{status_color}" borderRadius="12"/>')
    el.append(f'      </Positioned>')
    el.append(f'      <Positioned left="{badge_x+10:.1f}" top="{badge_y+12:.1f}" width="{badge_w-20:.1f}" height="32">')
    el.append(f'        <Text color="#FFFFFF" fontSize="18" fontStyle="BOLD" fontFamily="{FONT}" textAlign="CENTER">{status_text}</Text>')
    el.append(f'      </Positioned>')
    
    # If cancelled, add "本场取消" below status badge
    if status == "取消":
        el.append(f'      <Positioned left="{badge_x:.1f}" top="{badge_y+56:.1f}" width="{badge_w:.1f}" height="24">')
        el.append(f'        <Text color="#FFFFFF" fontSize="16" fontStyle="BOLD" fontFamily="{FONT}" textAlign="CENTER">本场取消</Text>')
        el.append(f'      </Positioned>')
    
    el.append('    </Stack>')
    el.append('  </SizedBox>')
    el.append('</Snapshot>')
    
    with open(f"tmp/run-20261016/A17/card-{card['id']}.v1.snapshot", "w", encoding="utf-8") as f:
        f.write("\n".join(el))
    print(f"Written {card['id']}: {card['title'][:30]}... ({title_lines} lines, size={title_size})")

print("All 8 card DSLs written")
