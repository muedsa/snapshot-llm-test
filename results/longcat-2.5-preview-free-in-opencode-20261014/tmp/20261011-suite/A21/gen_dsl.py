from pathlib import Path

# Brand colors (same as A13)
PRIMARY = "#3B82F6"
SECONDARY = "#10B981"
ACCENT = "#F59E0B"
DARK = "#0F172A"
BG = "#0F172A"

# Content
TITLE = "让复杂信息变得清晰"
DATE = "2026.11.07 19:30"
LABEL = "ONLINE LAUNCH"
SPEAKER = "讲者：林川 / 苏言"
WEBSITE = "layerlight.example.org"
BRAND = "叠光 Layerlight"

# Portrait 1080x1350
def gen_portrait():
    dsl = f'''<Snapshot type="png" width="1080" height="1350" background="{BG}">
  <Column mainAxisSize="MAX" height="1350" width="1080">
    <Container height="200" padding="(40,40)">
      <Text text="{BRAND}" color="#FFFFFF" fontSize="36" fontStyle="BOLD"/>
    </Container>
    <Container height="500" padding="(40,40)">
      <Column crossAxisAlignment="START">
        <Text text="{TITLE}" color="#FFFFFF" fontSize="72" fontStyle="BOLD"/>
        <SizedBox height="32"/>
        <Text text="{DATE}" color="#CBD5E1" fontSize="32"/>
        <Text text="{LABEL}" color="{PRIMARY}" fontSize="28"/>
      </Column>
    </Container>
    <Container height="400" padding="(40,40)">
      <Stack>
        <Positioned left="340" top="100" width="200" height="200">
          <Container color="{PRIMARY}" borderRadius="16"/>
        </Positioned>
        <Positioned left="390" top="150" width="200" height="200">
          <Container color="{SECONDARY}" borderRadius="16"/>
        </Positioned>
        <Positioned left="440" top="200" width="200" height="200">
          <Container color="{ACCENT}" borderRadius="16"/>
        </Positioned>
      </Stack>
    </Container>
    <Container height="200" padding="(40,40)">
      <Column crossAxisAlignment="START">
        <Text text="{SPEAKER}" color="#FFFFFF" fontSize="28"/>
        <Text text="{WEBSITE}" color="#CBD5E1" fontSize="24"/>
      </Column>
    </Container>
  </Column>
</Snapshot>'''
    return dsl

# Wide 1440x810
def gen_wide():
    dsl = f'''<Snapshot type="png" width="1440" height="810" background="{BG}">
  <Column mainAxisSize="MAX" height="810" width="1440">
    <Container height="100" padding="(40,40)">
      <Text text="{BRAND}" color="#FFFFFF" fontSize="36" fontStyle="BOLD"/>
    </Container>
    <Container height="400">
      <Row mainAxisAlignment="SPACE_BETWEEN" crossAxisAlignment="CENTER">
        <Container width="600" padding="(40,40)">
          <Column crossAxisAlignment="START">
            <Text text="{TITLE}" color="#FFFFFF" fontSize="64" fontStyle="BOLD"/>
            <SizedBox height="24"/>
            <Text text="{DATE}" color="#CBD5E1" fontSize="28"/>
            <Text text="{LABEL}" color="{PRIMARY}" fontSize="24"/>
          </Column>
        </Container>
        <Container width="400" height="300">
          <Stack>
            <Positioned left="100" top="50" width="120" height="120">
              <Container color="{PRIMARY}" borderRadius="12"/>
            </Positioned>
            <Positioned left="140" top="90" width="120" height="120">
              <Container color="{SECONDARY}" borderRadius="12"/>
            </Positioned>
            <Positioned left="180" top="130" width="120" height="120">
              <Container color="{ACCENT}" borderRadius="12"/>
            </Positioned>
          </Stack>
        </Container>
      </Row>
    </Container>
    <Container height="200" padding="(40,40)">
      <Column crossAxisAlignment="START">
        <Text text="{SPEAKER}" color="#FFFFFF" fontSize="24"/>
        <Text text="{WEBSITE}" color="#CBD5E1" fontSize="24"/>
      </Column>
    </Container>
  </Column>
</Snapshot>'''
    return dsl

output_dir = Path('outputs/20261011-suite/A21/round-01')
output_dir.mkdir(parents=True, exist_ok=True)

with open('tmp/20261011-suite/A21/round-01/launch-portrait.snapshot', 'w', encoding='utf-8') as f:
    f.write(gen_portrait())
with open('tmp/20261011-suite/A21/round-01/launch-wide.snapshot', 'w', encoding='utf-8') as f:
    f.write(gen_wide())

print("Generated A21 round-01 DSL files")

# Save design-tokens.json and content-map.json
import json
tokens = {
    "schema_version": 1,
    "task_id": "A21",
    "path_base": "output_dir",
    "colors": {"primary": PRIMARY, "secondary": SECONDARY, "accent": ACCENT, "bg": BG},
    "fonts": {"primary": "Noto Sans CJK SC"}
}
with open(output_dir / 'design-tokens.json', 'w', encoding='utf-8') as f:
    json.dump(tokens, f, ensure_ascii=False, indent=2)

content_map = {
    "schema_version": 1,
    "task_id": "A21",
    "path_base": "output_dir",
    "fields": ["title", "date", "label", "speaker", "website"],
    "round": 1
}
with open(output_dir / 'content-map.json', 'w', encoding='utf-8') as f:
    json.dump(content_map, f, ensure_ascii=False, indent=2)
print("Saved design-tokens.json and content-map.json")
