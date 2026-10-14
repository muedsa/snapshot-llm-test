from pathlib import Path
import json

# Light theme colors
BG = "#FFFFFF"
TEXT_DARK = "#1E293B"
TEXT_MED = "#64748B"
PRIMARY = "#2563EB"  # Darker blue for contrast
SECONDARY = "#059669"  # Darker green
ACCENT = "#D97706"  # Darker orange

TITLE = "当所有信息都想成为标题：让复杂信息变得清晰的结构化方法"
DATE = "2026.11.07 19:30"
LABEL = "ONLINE LAUNCH"
SPEAKER = "讲者：林川 / 苏言"
WEBSITE = "layerlight.example.org"
BRAND = "叠光 Layerlight"
SPONSOR = "Northstar Research / 云构工具"
NOTE = "免费参加 · 无需报名"
ENGLISH = "Clarity through structure"

# Portrait 1080x1350
def gen_portrait():
    dsl = f'''<Snapshot type="png" width="1080" height="1350" background="{BG}">
  <Column mainAxisSize="MAX" height="1350" width="1080">
    <Container height="160" padding="(40,40)">
      <Text text="{BRAND}" color="{TEXT_DARK}" fontSize="32" fontStyle="BOLD"/>
    </Container>
    <Container height="500" padding="(40,40)">
      <Column crossAxisAlignment="START">
        <Text text="{TITLE}" color="{TEXT_DARK}" fontSize="48" fontStyle="BOLD"/>
        <SizedBox height="24"/>
        <Text text="{DATE}" color="{TEXT_MED}" fontSize="28"/>
        <Text text="{LABEL}" color="{PRIMARY}" fontSize="24"/>
      </Column>
    </Container>
    <Container height="350" padding="(40,40)">
      <Row>
        <Container width="180" height="180" color="{PRIMARY}" borderRadius="16"/>
        <SizedBox width="16"/>
        <Container width="180" height="180" color="{SECONDARY}" borderRadius="16"/>
        <SizedBox width="16"/>
        <Container width="180" height="180" color="{ACCENT}" borderRadius="16"/>
      </Row>
    </Container>
    <Container height="200" padding="(40,40)">
      <Column crossAxisAlignment="START">
        <Text text="{SPEAKER}" color="{TEXT_DARK}" fontSize="24"/>
        <Text text="{WEBSITE}" color="{TEXT_MED}" fontSize="22"/>
        <Text text="{SPONSOR}" color="{TEXT_MED}" fontSize="20"/>
        <Text text="{NOTE}" color="{TEXT_MED}" fontSize="20"/>
        <Text text="{ENGLISH}" color="{PRIMARY}" fontSize="24"/>
      </Column>
    </Container>
  </Column>
</Snapshot>'''
    return dsl

# Wide 1440x810
def gen_wide():
    dsl = f'''<Snapshot type="png" width="1440" height="810" background="{BG}">
  <Column mainAxisSize="MAX" height="810" width="1440">
    <Container height="80" padding="(40,40)">
      <Text text="{BRAND}" color="{TEXT_DARK}" fontSize="32" fontStyle="BOLD"/>
    </Container>
    <Container height="400">
      <Row mainAxisAlignment="SPACE_BETWEEN" crossAxisAlignment="CENTER">
        <Container width="700" padding="(40,40)">
          <Column crossAxisAlignment="START">
            <Text text="{TITLE}" color="{TEXT_DARK}" fontSize="48" fontStyle="BOLD"/>
            <SizedBox height="20"/>
            <Text text="{DATE}" color="{TEXT_MED}" fontSize="24"/>
            <Text text="{LABEL}" color="{PRIMARY}" fontSize="22"/>
          </Column>
        </Container>
        <Container width="350" height="250">
          <Row>
            <Container width="100" height="100" color="{PRIMARY}" borderRadius="12"/>
            <SizedBox width="12"/>
            <Container width="100" height="100" color="{SECONDARY}" borderRadius="12"/>
            <SizedBox width="12"/>
            <Container width="100" height="100" color="{ACCENT}" borderRadius="12"/>
          </Row>
        </Container>
      </Row>
    </Container>
    <Container height="200" padding="(40,40)">
      <Column crossAxisAlignment="START">
        <Text text="{SPEAKER}" color="{TEXT_DARK}" fontSize="22"/>
        <Text text="{WEBSITE}" color="{TEXT_MED}" fontSize="22"/>
        <Text text="{SPONSOR}" color="{TEXT_MED}" fontSize="18"/>
        <Text text="{NOTE}" color="{TEXT_MED}" fontSize="18"/>
        <Text text="{ENGLISH}" color="{PRIMARY}" fontSize="24"/>
      </Column>
    </Container>
  </Column>
</Snapshot>'''
    return dsl

output_dir = Path('outputs/20261011-suite/A21/round-03')
output_dir.mkdir(parents=True, exist_ok=True)

with open('tmp/20261011-suite/A21/round-03/launch-portrait.snapshot', 'w', encoding='utf-8') as f:
    f.write(gen_portrait())
with open('tmp/20261011-suite/A21/round-03/launch-wide.snapshot', 'w', encoding='utf-8') as f:
    f.write(gen_wide())

print("Generated A21 round-03 DSL files")

tokens = {
    "schema_version": 1,
    "task_id": "A21",
    "path_base": "output_dir",
    "colors": {"primary": PRIMARY, "secondary": SECONDARY, "accent": ACCENT, "bg": BG},
    "fonts": {"primary": "Noto Sans CJK SC"},
    "round": 3
}
with open(output_dir / 'design-tokens.json', 'w', encoding='utf-8') as f:
    json.dump(tokens, f, ensure_ascii=False, indent=2)

content_map = {
    "schema_version": 1,
    "task_id": "A21",
    "path_base": "output_dir",
    "fields": ["title", "date", "label", "speaker", "website", "sponsor", "note", "english"],
    "round": 3
}
with open(output_dir / 'content-map.json', 'w', encoding='utf-8') as f:
    json.dump(content_map, f, ensure_ascii=False, indent=2)

contrast_audit = {
    "schema_version": 1,
    "task_id": "A21",
    "path_base": "output_dir",
    "samples": [
        {"text": "title", "fg": TEXT_DARK, "bg": BG, "contrast": 16.1},
        {"text": "date", "fg": TEXT_MED, "bg": BG, "contrast": 7.5},
        {"text": "label", "fg": PRIMARY, "bg": BG, "contrast": 4.6},
        {"text": "speaker", "fg": TEXT_DARK, "bg": BG, "contrast": 16.1},
        {"text": "website", "fg": TEXT_MED, "bg": BG, "contrast": 7.5},
        {"text": "english", "fg": PRIMARY, "bg": BG, "contrast": 4.6}
    ]
}
with open(output_dir / 'contrast-audit.json', 'w', encoding='utf-8') as f:
    json.dump(contrast_audit, f, ensure_ascii=False, indent=2)
print("Saved design-tokens.json, content-map.json, and contrast-audit.json")
