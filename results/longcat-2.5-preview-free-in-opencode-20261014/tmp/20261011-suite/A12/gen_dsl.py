import json
from pathlib import Path

with open('tasks/A12-responsive-system/inputs/content.json', 'r', encoding='utf-8') as f:
    c = json.load(f)

FONT = "Noto Sans CJK SC"
BG = "#F8FAFC"
CARD_BG = "#FFFFFF"
CARD_BORDER = "#E2E8F0"
TEXT_DARK = "#1E293B"
TEXT_MED = "#64748B"

sizes = [
    ("mobile", 360, 800, 16),
    ("tablet", 768, 1024, 32),
    ("desktop", 1440, 900, 32),
    ("stage", 1920, 1080, 32),
]

for name, W, H, margin in sizes:
    dsl_parts = []
    dsl_parts.append(f'<Snapshot type="png" background="{BG}">')
    dsl_parts.append(f'  <Column mainAxisSize="MAX" height="{H}" width="{W}">')

    # Header
    dsl_parts.append(f'    <Container height="120" padding="({margin},{margin})">')
    dsl_parts.append(f'      <Column crossAxisAlignment="START">')
    dsl_parts.append(f'        <Text text="{c["title"]}" color="{TEXT_DARK}" fontSize="40" fontStyle="BOLD"/>')
    dsl_parts.append(f'        <Text text="{c["subtitle"]}" color="{TEXT_MED}" fontSize="20"/>')
    dsl_parts.append(f'      </Column>')
    dsl_parts.append(f'    </Container>')

    # Event info
    dsl_parts.append(f'    <Container height="80" padding="({margin},{margin})">')
    dsl_parts.append(f'      <Column crossAxisAlignment="START">')
    dsl_parts.append(f'        <Text text="{c["date"]} {c["time"]}" color="{TEXT_DARK}" fontSize="20"/>')
    dsl_parts.append(f'        <Text text="{c["location"]}" color="{TEXT_MED}" fontSize="20"/>')
    dsl_parts.append(f'      </Column>')
    dsl_parts.append(f'    </Container>')

    # Cards
    for i, card in enumerate(c['cards']):
        if name == "mobile":
            col = i % 1
            row = i // 1
        elif name == "tablet":
            col = i % 2
            row = i // 2
        else:
            col = i % 3
            row = i // 3

        dsl_parts.append(f'    <Container height="100" color="{CARD_BG}" border="1 SOLID {CARD_BORDER}" borderRadius="8" padding="(8,12)">')
        dsl_parts.append(f'      <Column crossAxisAlignment="START">')
        dsl_parts.append(f'        <Text text="{card["title"]}" color="{TEXT_DARK}" fontSize="18" fontStyle="BOLD"/>')
        dsl_parts.append(f'        <Text text="{card["detail"]}" color="{TEXT_MED}" fontSize="16"/>')
        dsl_parts.append(f'      </Column>')
        dsl_parts.append(f'    </Container>')
        dsl_parts.append(f'    <SizedBox height="8"/>')

    # Footer
    dsl_parts.append(f'    <Container height="80" padding="({margin},{margin})">')
    dsl_parts.append(f'      <Column crossAxisAlignment="START">')
    dsl_parts.append(f'        <Text text="{c["cta"]}" color="{TEXT_DARK}" fontSize="20"/>')
    dsl_parts.append(f'        <Text text="{c["website"]}" color="{TEXT_MED}" fontSize="20"/>')
    dsl_parts.append(f'      </Column>')
    dsl_parts.append(f'    </Container>')

    dsl_parts.append('  </Column>')
    dsl_parts.append('</Snapshot>')

    dsl = '\n'.join(dsl_parts)
    with open(f'tmp/20261011-suite/A12/{name}.snapshot', 'w', encoding='utf-8') as f:
        f.write(dsl)
    print(f'{name}: {len(dsl)} chars')

# Save design tokens
tokens = {
    "schema_version": 1,
    "task_id": "A12",
    "path_base": "output_dir",
    "colors": {"bg": BG, "card_bg": CARD_BG, "border": CARD_BORDER, "text_dark": TEXT_DARK, "text_med": TEXT_MED},
    "fonts": {"primary": FONT},
    "sizes": [{"name": n, "width": w, "height": h, "margin": m} for n, w, h, m in sizes]
}

output_dir = Path('outputs/20261011-suite/A12')
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / 'design-tokens.json', 'w', encoding='utf-8') as f:
    json.dump(tokens, f, ensure_ascii=False, indent=2)
print('Saved design-tokens.json')
